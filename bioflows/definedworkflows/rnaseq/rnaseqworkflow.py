import copy
import os
import subprocess
import sys
import time
from collections import OrderedDict, defaultdict

import jsonpickle
import luigi
import saga
import yaml

import bioflows.bioflowsutils.wrappers as wr
import bioflows.bioflowsutils.wrappers_gatk as wr_gatk
import bioflows.bioflowsutils.wrappers_picard as wr_picard
import bioflows.bioflowsutils.wrappers_qiime2 as wr_qiime2
import bioflows.bioflowsutils.wrappers_samtools as wr_samtools
from bioflows.bioutils.access_sra.sra import SraUtils


def ordered_load(stream, loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    '''
     Load YAML as an Ordered Dict
    :param stream:
    :param loader:
    :param object_pairs_hook:
    :return:

    Borrowed shamelessly from http://codegist.net/code/python2-yaml/
    #todo fix hack
    '''
    class OrderedLoader(loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )
    return yaml.load(stream, OrderedLoader)

class BaseTask:

    # Variable for suffix for multiple run of a program

    def setup(self, prog_input):
        self.parms = jsonpickle.decode(prog_input)
        self.jobparms = self.parms.job_parms
        self.jobparms['name'] = self.parms.name
        self.jobparms['workdir'] = self.parms.cwd
        self.jobparms['scripts_dir'] = self.parms.scripts_dir

        # todo fix:  Hack to get the command to work for now
        #              Clear all the environment variables
        self.jobparms['command'] = "\n#SBATCH --export=NONE\n\n"
        self.jobparms['command'] += "set -e\necho '***** Old PATH *****'\necho $PATH\n"
        self.jobparms['command'] += "echo '**** Conda command***'\necho '" + self.parms.conda_command + "'\n"
        self.jobparms['command'] += self.parms.conda_command + "\n"
        # todo Fix hack because CCV loads global modules
        # with conda activate a new shell is created and the PATH gets muddled
        # need to figure out how to clear out the env
        # self.jobparms['command'] += "export PATH=$CONDA_PREFIX/bin:$PATH"

        self.jobparms['command'] += "\necho '***** New PATH *****'\necho $PATH\n\n"
        self.jobparms['command'] += "\necho '***** checking Java ****'\njava -version 2>&1 \n\n"
        self.jobparms['command'] += "\necho '***** checking env *****'\nprintenv\n\n"

        # self.jobparms['command'] += 'conda activate $CONDA_PREFIX\n'
        self.jobparms[
            'command'] += "\necho '***** printing JOB INFO *****'\nscontrol write batch_script $SLURM_JOBID /dev/stdout \n"

        # Add a script here to print out the actual commands used by the slurm using sbatch script
        self.jobparms['command'] += 'srun --export=ALL '
        self.jobparms['command'] += self.parms.run_command + "\n"
        self.jobparms['command'] += " echo 'DONE' > " + self.parms.luigi_target

        # self.jobparms['name'] = self.parms.name.replace(" ", "_")
        # self.jobparms['script_name'] = self.parms.input + "_" + self.jobparms['name']
        self.jobparms['script_name'] = self.parms.input + "_" + self.parms.prog_id
        ## Replace class name to be reflected in the luigi visualizer
        ##self.__class__.__name__ = self.name
        self.jobparms['out'] = os.path.join(self.parms.log_dir, self.jobparms['script_name'] + "_slurm.stdout")
        self.jobparms['error'] = os.path.join(self.parms.log_dir, self.jobparms['script_name'] + "_slurm.stderr")
        if self.jobparms['saga_host'] != 'localhost':
            self.jobparms['outfilesource'] = 'ssh.ccv.brown.edu:' + self.parms.luigi_target
            self.jobparms['outfiletarget'] = '' + os.path.dirname(self.parms.luigi_local_target) + "/"
        print self.jobparms
        return

    def create_saga_job(self, **kwargs):
        ctx = saga.Context("ssh")
        ctx.user_id = kwargs.get('saga_user', 'aragaven')
        host = kwargs.get('saga_host', 'localhost')
        scheduler = kwargs.get('saga_scheduler', 'fork')

        session = saga.Session()
        if host != 'localhost':
            session.add_context(ctx)
        # describe our job
        # these parameters are standard saga parameters that map tp slurm specific ones:
        # ref: line 410+ https://github.com/radical-cybertools/saga-python/blob/devel/src/saga/adaptors/slurm/slurm_job.py

        jd = saga.job.Description()
        jd.executable = ''
        jd.arguments = [kwargs.get('command')]  # cmd
        jd.working_directory = kwargs.get('work_dir', os.getcwd())
        jd.wall_time_limit = kwargs.get('time', 60)
        jd.total_physical_memory = kwargs.get('mem', 2000)
        jd.number_of_processes = 1
        jd.processes_per_host = 1
        jd.total_cpu_count = kwargs.get('ncpus', 1)
        jd.output = kwargs.get('out', os.path.join(jd.working_directory, "slurmlog.stdout"))
        jd.error = kwargs.get('error', "slurmlog.stderr")
        js = saga.job.Service(scheduler + "://" + host, session=session)

        f = open(os.path.join(kwargs.get('scripts_dir'), kwargs.get('script_name') + "_sbatch_cmds"), 'w')
        f.write("#/bin/bash\n\n#*************\n")
        f.write(kwargs.get('command'))
        f.write("\n\n#*************\n")
        f.close()

        myjob = js.create_job(jd)
        # Now we can start our job.
        # print " \n ***** SAGA: job Started ****\n"
        myjob.run()

        myjob.wait()
        # print " \n ***** SAGA: job Done ****\n"
        # print kwargs.get('outfilesource')
        # out = saga.filesystem.File(kwargs.get('outfilesource'), session=session)
        # print kwargs.get('outfiletarget')
        # out.copy(kwargs.get('outfiletarget'))
        # subprocess.call(' '.join(['ssh ', host+server] ))
        if host != 'localhost':
            subprocess.call(' '.join(['scp ', kwargs.get('outfilesource'), kwargs.get('outfiletarget')]), shell=True)
        # print "\n **** SAGA: copy Done ***** \n"
        # out.close()
        js.close()
        return


class TopTask(luigi.Task, BaseTask):
    prog_parms = luigi.ListParameter()

    def run(self):

        self.setup(self.prog_parms[0])
        self.__class__.__name__ = str(self.jobparms['name'])
        job = self.create_saga_job(**self.jobparms)
        return

    def output(self):
        self.setup(self.prog_parms[0])
        self.__class__.__name__ = str(self.jobparms['name'])
        if self.parms.local_target:
            # lcs.RemoteFileSystem("ssh.ccv.brown.edu").get( self.parms.luigi_target,self.parms.luigi_local_target)
            return luigi.LocalTarget(self.parms.luigi_local_target)
        else:
            return luigi.LocalTarget(self.parms.luigi_target)


class TaskSequence(luigi.Task, BaseTask):
    prog_parms = luigi.ListParameter()
    n_tasks = luigi.IntParameter()
    def requires(self):
        self.setup(self.prog_parms[0])
        newParms = [x for x in self.prog_parms]

        # Test if only one command is submitted or more commands are submitted
        if self.n_tasks > 1:
            del newParms[0]
            if len(newParms) > 1:
                return TaskSequence(prog_parms=newParms, n_tasks=self.n_tasks)
            else:
                return TopTask(prog_parms=newParms)
        else:
            return []
            # return TopTask(prog_parms=newParms)

    def run(self):
        self.setup(self.prog_parms[0])
        self.__class__.__name__ = str(self.jobparms['name'])
        job = self.create_saga_job(**self.jobparms)
        return

    def output(self):
        self.setup(self.prog_parms[0])
        self.__class__.__name__ = str(self.jobparms['name'])
        if self.parms.local_target:
            return luigi.LocalTarget(self.parms.luigi_local_target)
        else:
            return luigi.LocalTarget(self.parms.luigi_target)


class TaskFlow(luigi.WrapperTask):
    tasks = luigi.ListParameter()
    task_name = luigi.Parameter()
    task_namespace = "BioProject"

    def requires(self):
        for x in self.tasks:
            yield jsonpickle.decode(x)

    def task_id_str(self):
        return self.task_name


class BaseWorkflow:
    base_kwargs = ''
    new_base_kwargs = ''
    sample_fastq = ''
    sample_fastq_work = dict()
    progs = OrderedDict()
    sra_info = ''
    multi_run_var = "round"
    qiime_info = ''
    gatk_flag = False
    rna_seq_flag = False
    dna_seq_flag = False

    prog_job_parms = dict()
    prog_suffix_type = dict()
    prog_output_suffix = dict()
    prog_input_suffix = dict()

    def __init__(self, parmsfile):
        self.parse_config(parmsfile)
        self.prog_wrappers = {'feature_counts': wr.BedtoolsCounts,
                              'gsnap': wr.Gsnap,
                              'fastqc': wr.FastQC,
                              'qualimap_rnaseq': wr.QualiMap,
                              'qualimap_bamqc': wr.QualiMap,
                              'samtools_view': wr_samtools.SamTools,
                              'samtools_index': wr_samtools.SamTools,
                              'samtools_sort': wr_samtools.SamTools,
                              'bammarkduplicates2': wr.Biobambam,
                              'bamsort': wr.Biobambam,
                              'salmon': wr.SalmonCounts,
                              'htseq-count': wr.HtSeqCounts,
                              'bwa_mem': wr.Bwa,
                              'picard_CollectWgsMetrics': wr_picard.Picard,
                              'picard_MarkDuplicates': wr_picard.Picard,
                              'picard_BuildBamIndex': wr_picard.Picard,
                              'picard_AddOrReplaceReadGroups': wr_picard.Picard,
                              'gatk_RealignerTargetCreator': wr_gatk.Gatk,
                              'gatk_IndelRealigner': wr_gatk.Gatk,
                              'gatk_BaseRecalibrator': wr_gatk.Gatk,
                              'gatk_PrintReads': wr_gatk.Gatk,
                              'gatk_HaplotypeCaller': wr_gatk.Gatk,
                              'gatk_AnalyzeCovariates': wr_gatk.Gatk,
                              'trimmomatic_PE': wr.Trimmomatic,
                              'fastq_screen': wr.FastqScreen,
                              'qiime_tools_import': wr_qiime2.Qiime2,
                              'qiime_demux_emp-single': wr_qiime2.Qiime2,
                              'qiime_demux_emp-paired': wr_qiime2.Qiime2,
                              'qiime_demux_summarize': wr_qiime2.Qiime2,
                              'qiime_dada2_denoise-single': wr_qiime2.Qiime2,
                              'qiime_dada2_denoise-paired': wr_qiime2.Qiime2,
                              'qiime_metadata_tabulate': wr_qiime2.Qiime2,
                              'qiime_feature-table_summarize': wr_qiime2.Qiime2,
                              'qiime_feature-table_tabulate-seqs': wr_qiime2.Qiime2,
                              'qiime_phylogeny_align-to-tree-mafft-fasttree': wr_qiime2.Qiime2
                              }
        self.job_params = {'work_dir': self.run_parms['work_dir'],
                           'time': 80,
                           'mem': 3000,
                           'ncpus': 1
                           }

        # Check and make sure both fastq_file and sra don't exist
        if 'fastq_file' in self.sample_manifest.keys():
            self.parse_sample_info_from_file()
        elif 'sra' in self.sample_manifest.keys():
            self.parse_sample_info_from_sra()
        elif 'qiime' in self.sample_manifest.keys():
            self.parse_sample_info_qiime()
            # subprocess.check_output('cp ' + self.qiime_info["--m-barcodes-file"] + ' ' + self.run_parms['work_dir']+"/" , shell=True)
        else:
            print "Error: unknown Sample type option provided"
            sys.exit(0)

        # todo close so we can trap errors else will fail silently

        # Setup saga parameters
        self.set_saga_parms()

        # Setup the Conda PATH
        if 'conda_command' not in self.run_parms.keys():
            self.run_parms['conda_command'] = 'source /gpfs/runtime/cbc_conda/bin/activate_cbc_conda'

        #self.paired_end = False
        if "log_dir" not in self.run_parms.keys():
            self.run_parms['log_dir'] = "logs"

        self.set_paths()

        self.set_base_kwargs()

        self.paths_to_test = [self.work_dir, self.log_dir, self.scripts_dir, self.checkpoint_dir]

        if 'sra' in self.sample_manifest.keys():
            self.paths_to_test += [self.sra_dir]
        if 'qiime' in self.sample_manifest.keys():
            self.paths_to_test += [self.qiime_dir]
        else:
            self.paths_to_test += [self.fastq_dir, self.align_dir, self.qc_dir]

        return

    """A shortcut for calling the BaseWrapper __init__ from a subclass."""
    init = __init__

    def parse_config(self, fileHandle):


        for k, v in ordered_load(open(fileHandle, 'r'), yaml.SafeLoader).iteritems():
            setattr(self, k, v)

        return


    def set_saga_parms(self):
        """
            setup the parameters needed for the saga interface
        :return:
        """

        if 'saga_host' in self.run_parms.keys():
            self.job_params['saga_host'] = self.run_parms['saga_host']
        else:
            self.job_params['saga_host'] = "localhost"
        if 'saga_user' in self.run_parms.keys():
            self.job_params['ssh_user'] = self.run_parms['ssh_user']
        if 'saga_scheduler' in self.run_parms.keys():
            self.job_params['saga_scheduler'] = self.run_parms['saga_scheduler']
        else:
            self.job_params['saga_scheduler'] = 'fork'

        return

    def set_base_kwargs(self):
        """
        Setup the generic keyword arguments for the wrappers to use. These keywords are the
        global parameters for the entire workflow.
        :return:
        """
        print "\n ****** Setting base Keywords ***** \n"
        self.base_kwargs = dict()
        self.base_kwargs['cwd'] = self.work_dir
        self.base_kwargs['work_dir'] = self.work_dir
        self.base_kwargs['log_dir'] = self.log_dir
        self.base_kwargs['checkpoint_dir'] = self.checkpoint_dir

        if 'sra' in self.sample_manifest.keys():
            self.base_kwargs['sra_dir'] = self.sra_dir
        if 'qiime' in self.sample_manifest.keys():
            self.base_kwargs['qiime_dir'] = self.qiime_dir
            self.base_kwargs['qiime_info'] = self.qiime_info
        else:
            self.base_kwargs['qc_dir'] = self.qc_dir
            self.base_kwargs['fastq_dir'] = self.fastq_dir
            self.base_kwargs['align_dir'] = self.align_dir


        self.base_kwargs['conda_command'] = self.run_parms.get('conda_command', 'source activate cbc_conda')
        self.base_kwargs['job_parms'] = self.job_params
        self.base_kwargs['job_parms_type'] = "default"
        self.base_kwargs['add_job_parms'] = None
        self.base_kwargs['log_dir'] = self.log_dir
        self.base_kwargs['scripts_dir'] = self.scripts_dir
        self.base_kwargs['paired_end'] = self.run_parms.get('paired_end', False)
        self.base_kwargs['local_targets'] = self.run_parms.get('local_targets', False)
        self.base_kwargs['luigi_local_path'] = self.run_parms.get('luigi_local_path', os.getcwd())

        # These can be application specific
        self.base_kwargs['gtf_file'] = self.run_parms.get('gtf_file', None)
        self.base_kwargs['ref_fasta_path'] = self.run_parms.get('reference_fasta_path', None)
        self.base_kwargs['genome_file'] = self.run_parms.get('genome_file', None)
        # self.new_base_kwargs = copy.deepcopy(self.base_kwargs)
        # Does not work keeps the object in memory
        return

    def parse_sample_info_from_file(self):
        """
        Read in the sample attributes from file as a dictionary with
        the sample id as the key
        :return:
        """
        self.sample_fastq = dict()
        for line in open(self.sample_manifest['fastq_file'], 'r'):
            tmpline = line.strip('\n').split(',')
            # print tmpline[0], tmpline[1]
            self.sample_fastq[tmpline[0]] = []
            self.sample_fastq[tmpline[0]].append(tmpline[1])
            if len(tmpline) > 2:
                self.sample_fastq[tmpline[0]].append(tmpline[2])
                self.paired_end = True
        return

    def parse_sample_info_from_sra(self):
        """
        Read in the sample attributes from an SRA id and create the sample to fastq as a dictionary with
        the sample id as the key
        """
        self.sra_info = self.sample_manifest['sra'].copy()
        self.sra_info['outfile'] = os.path.join(self.run_parms['work_dir'],"sra_manifest.csv")
        sample_sra = SraUtils(self.sra_info)
        self.sample_fastq = copy.deepcopy(sample_sra.sample_to_file)

        self.write_cmds(self.sample_fastq,os.path.join(self.run_parms['work_dir'], "sra_to_sample.txt"))

        print self.sample_fastq

        # need to check that all samples are SE or PE
        key = self.sample_fastq.keys()[0]
        query_val = os.path.basename(self.sample_fastq[key][0])
        query_val = query_val.replace('.sra', '')

        if 'SINGLE' in sample_sra.sra_records[query_val]['library_type']:
            print "SE library\n"
            self.paired_end = False
            self.base_kwargs['paired_end'] = False
        elif 'PAIRED' in sample_sra.sra_records[query_val]['library_type']:
            print "PE library\n"
            self.paired_end = True
            self.base_kwargs['paired_end'] = True
        return

    def parse_sample_info_qiime(self):
        """
        Read in the sample attributes from an SRA id and create the sample to fastq as a dictionary with
        the sample id as the key
        """
        self.qiime_info = self.sample_manifest['qiime'].copy()
        if self.qiime_info["--type"] == "EMPSingleEndSequences" or self.qiime_info["--type"] == "EMPPairedEndSequences":
            if "--input-path" not in self.qiime_info.keys():
                print "Error !!! input path is required"
                sys.exit(0)
            elif "--output-path" not in self.qiime_info.keys():
                print "Error !!! output path is required"
                sys.exit(0)
            elif "--m-barcodes-file" not in self.qiime_info.keys():
                print "Error !!! barcodes file is required"
                sys.exit(0)
        return

    def set_paths(self):
        '''
        Setup all the values for the minimum required paths for the analysis
        :return:
        '''
        self.work_dir = self.run_parms['work_dir']
        self.log_dir = os.path.join(self.work_dir, self.run_parms['log_dir'])
        self.scripts_dir = os.path.join(self.work_dir, "slurm_scripts")
        self.checkpoint_dir = os.path.join(self.work_dir, 'checkpoints')

        # TODO refactor to make sra dir only if sra option is used
        if 'sra' in self.sample_manifest.keys():
            self.sra_dir = os.path.join(self.work_dir, 'sra')
        else:
            pass
        if 'qiime' in self.sample_manifest.keys():
            self.qiime_dir = os.path.join(self.work_dir, 'qiime')
        else:
            self.fastq_dir = os.path.join(self.work_dir, 'fastq')
            self.align_dir = os.path.join(self.work_dir, 'alignments')
            self.qc_dir = os.path.join(self.work_dir, 'qc')

        return

    def check_paths(self, path, remote=False):
        """
        Check if the directory exists, remote and local, using the saga module.
        :param path:
        :param remote:
        :return:
        """
        if remote:
            session = saga.Session()
            ctx = saga.Context("ssh")
            ctx.user_id = self.run_parms['ssh_user']
            session.add_context(ctx)
            try:
                dir = saga.filesystem.Directory(path, session=session)
            except:
                print os.path.dirname(path)
                dir = saga.filesystem.Directory(os.path.dirname(path))
                dir.make_dir(os.path.basename(path))
                dir.close()
        else:
            if not os.path.exists(path):
                os.mkdir(path)
        return

    def test_paths(self):
        '''
        Check that all the required paths exist either locally or remotely
        :return:
        '''

        remote_dirs_flag = False
        paths_to_test = self.paths_to_test
        if self.run_parms['saga_host'] != "localhost":
            remote_dirs_flag = True
            remote_prefix = "sftp://" + self.run_parms['saga_host']
            paths_to_test = [remote_prefix + "/" + x for x in self.paths_to_test]
            print paths_to_test

        for p in paths_to_test:
            self.check_paths(p, remote_dirs_flag)

        return

    def download_sra_cmds(self):
        '''
        Download sra based on ftp urls using lftp
        :return:
        '''
        cmds = []
        # Add commands to the command list
        samp_list = []
        for samp, fileName in self.sample_fastq.iteritems():
            for srr_file in fileName:
                cmds.append(' '.join([self.run_parms['conda_command'], ";",
                                  'lftp', '-e "get ', srr_file, '-o ', self.sra_dir, '; bye"',
                                  'ftp://ftp-trace.ncbi.nlm.nih.gov > ']))
                samp_list.append(samp)

        # Create a dictionary of Sample and commands
        #cmds_dict = dict(zip(samp_list,cmds))

        cmds_dict = defaultdict(list)
        for samp,cmd in zip(samp_list,cmds):
            cmds_dict[samp].append(cmd)

        self.write_cmds(cmds_dict,os.path.join(self.run_parms['work_dir'], "sra_download_cmds.txt"))

        self.symlink_fastqs_submit_jobs(cmds_dict, "_sra_download.log",300)

        f = open(os.path.join(self.run_parms["work_dir"],"debug.txt"),'a')
        f.write ("\n******* End Test1 ******** \n")

        for k, v in self.sample_fastq_work.iteritems():
            #print k, ":", v, "\n"
            f.write(k + ":"+ str(v) + "\n")
        f.write("n******* End Test1 ******** \n")

        f.close()

        self.convert_sra_to_fastq_cmds()

        return

    def convert_sra_to_fastq_cmds(self):
        '''
        Download sra based on ftp urls and process to fastq
        :return:
        '''

        # Add commands to the command list
        cmds = []

        # Add samples to a list
        samp_list =[]
        for samp, fileName in self.sample_fastq.iteritems():
            self.sample_fastq_work[samp] = []
            if len(fileName) < 2:
                if not self.paired_end:
                    sra_name = os.path.basename(fileName[0])

                    cmds.append(' '.join([self.run_parms['conda_command'], ";",
                                          "fastq-dump", "-v", "-v", "-v", "--gzip",
                                          os.path.join(self.sra_dir, sra_name), '-O',
                                          self.fastq_dir, ";",
                                          " mv -v", os.path.join(self.fastq_dir, sra_name.replace("sra", "fastq.gz")),
                                          os.path.join(self.fastq_dir, samp + ".fq.gz"), ";",
                                          "echo DONE:", fileName[0], "> "]))
                    samp_list.append(samp)
                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + ".fq.gz"))
                else:
                    sra_name = os.path.basename(fileName[0])

                    cmds.append(' '.join([self.run_parms['conda_command'], ";",
                                          "fastq-dump", "-v", "-v", "-v", "--gzip", "--split-files",
                                          os.path.join(self.sra_dir, sra_name),
                                          '-O',
                                          self.fastq_dir, ";",
                                          " mv -v",
                                          os.path.join(self.fastq_dir, sra_name.replace(".sra", "_1.fastq.gz")),
                                          os.path.join(self.fastq_dir, samp + "_1.fq.gz"), ";",
                                          " mv -v",
                                          os.path.join(self.fastq_dir, sra_name.replace(".sra", "_2.fastq.gz")),
                                          os.path.join(self.fastq_dir, samp + "_2.fq.gz"), ";",
                                          "echo DONE:", fileName[0], "> "]))
                    samp_list.append(samp)

                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + "_1.fq.gz"))
                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + "_2.fq.gz"))
            else:
                if not self.paired_end:
                    num = 1
                    for srr_file in fileName:
                        sra_name = os.path.basename(srr_file)
                        cmds.append(' '.join([self.run_parms['conda_command'], ";",
                                              "fastq-dump", "-vvv", "--gzip", os.path.join(self.sra_dir, sra_name),
                                              '-O',
                                              self.fastq_dir, ";",
                                              " cat", os.path.join(self.fastq_dir, sra_name.replace("sra", "fastq.gz")),
                                              ">>", os.path.join(self.fastq_dir, samp + ".fq.gz"), ";",
                                              "echo DONE:", srr_file, "> "]))
                        samp_list.append(samp)
                        num += 1
                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + ".fq.gz"))
                else:
                    num = 1
                    for srr_file in fileName:
                        sra_name = os.path.basename(srr_file)
                        cmds.append(' '.join([self.run_parms['conda_command'], ";",
                                              "fastq-dump", "-vvv", "--gzip", "--split-files",
                                              os.path.join(self.sra_dir, sra_name), '-O', self.fastq_dir, ";",
                                              "cat",
                                              os.path.join(self.fastq_dir, sra_name.replace(".sra", "_1.fastq.gz")),
                                              ">>", os.path.join(self.fastq_dir, samp + "_1.fq.gz"), ";",
                                              "rm -v",
                                              os.path.join(self.fastq_dir, sra_name.replace(".sra", "_1.fastq.gz")), ";",
                                              "cat",
                                              os.path.join(self.fastq_dir, sra_name.replace(".sra", "_2.fastq.gz")),
                                              ">>", os.path.join(self.fastq_dir, samp + "_2.fq.gz"), ";",
                                              "rm -v",
                                              os.path.join(self.fastq_dir, sra_name.replace(".sra", "_2.fastq.gz")), ";",
                                              "echo DONE:", srr_file, "> "]))
                        samp_list.append(samp)
                        num += 1

                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + "_1.fq.gz"))
                    self.sample_fastq_work[samp].append(os.path.join(self.fastq_dir, samp + "_2.fq.gz"))

        # defaultdict with a default factory of list. A new list is created for each new key.

        cmds_dict = defaultdict(list)
        for samp,cmd in zip(samp_list,cmds):
            cmds_dict[samp].append(cmd)

        self.write_cmds(cmds_dict,os.path.join(self.run_parms['work_dir'], "sra_run_cmds.txt"))

        self.symlink_fastqs_submit_jobs(cmds_dict, "symlink.stdout", 300)

        f=open(os.path.join(self.run_parms['work_dir'],"sra_sample_fastq.csv"),'w')
        for k, v in self.sample_fastq_work.iteritems():
            print k, ":", v, "\n"
            outstring = k + "," + ','.join(v)
            f.write( outstring.strip(',')+ "\n")
        f.close()
        return

    def write_cmds(self,cmds_set, outfile):
        """
        Utility functon to write dictionary of commands to file
        :param cmds_set:
        :param outfile:
        :return:
        """
        f = open(outfile, 'w')
        for samp, cmds in cmds_set.iteritems():
            if type(cmds) == list:
                f.write(samp + ":" + '\n'.join(cmds) + "\n")
            else:
                f.write(samp + ":" + cmds + "\n")

        f.close()
        return

    def symlink_fastqs_submit_jobs(self, cmds, job_output_suffix, run_time, depend=False):
        """
        take in a dictionary of sample and associated commands to run for the sample and submit each command as a job
        :param cmds:
        :return:
        """
        # setup remote session
        remote_dirs = False
        remote_path = self.run_parms['work_dir']

        if self.run_parms['saga_host'] != "localhost":
            session = saga.Session()
            ctx = saga.Context("ssh")
            ctx.user_id = self.run_parms['ssh_user']
            session.add_context(ctx)
            remote_dirs = True
            remote_path = "sftp://" + self.run_parms['saga_host'] + self.run_parms['work_dir']

        # setup basic job parameters

        jd = saga.job.Description()
        jd.executable = ''
        jd.working_directory = self.run_parms['work_dir']
        jd.wall_time_limit = run_time
        # jd.output = os.path.join(log_dir, "symlink.stdout")
        # jd.error = os.path.join(log_dir, "symlink.stderr")
        # job_output = os.path.join(self.log_dir, "symlink.stdout")
        # job_error = os.path.join(self.log_dir, "symlink.stderr")

        # Setup the saga host to use

        js = saga.job.Service("fork://localhost")

        # Check if the submission is on a remote host
        if self.run_parms['saga_host'] != "localhost":
            js = saga.job.Service("ssh://" + self.run_parms['saga_host'], session=session)

        # check if submission is using a scheduler

        elif self.run_parms['saga_host'] == 'localhost' and 'saga_scheduler' in self.run_parms.keys():
            js = saga.job.Service(self.run_parms['saga_scheduler'] + "://" + self.run_parms['saga_host'])

        # Check if submission is not using a scheduler
        elif self.run_parms['saga_host'] == 'localhost' and 'saga_scheduler' not in self.run_parms.keys():
            self.run_parms['saga_scheduler'] = "fork"
            js = saga.job.Service("fork://" + self.run_parms['saga_host'])

        # Submit jobs

        jobs = []
        for samp,cmd in cmds.iteritems():
            num = 1
            prev_job_id = None

            for c in cmd:
                job_output = os.path.join(self.log_dir, samp + "_" + str(num) + "_" + job_output_suffix)
                jd.error = os.path.join(self.log_dir, samp + "_" + str(num) + "_slurm.err")
                jd.output = os.path.join(self.log_dir, samp + "_" + str(num) + "_slurm.out")

                ## Always redirect stderr to stdout in this case
                myjob = ''

                if num == 1 and depend:
                    jd.arguments = c + " 2>&1 " + job_output
                    myjob = js.create_job(jd)
                    myjob.run()
                    jobs.append(myjob)
                    prev_job_id = myjob.get_id().split('-')[1].strip('[').strip(']')
                elif num > 1 and depend:
                    # Hack to append other SBATCH defs
                    tmp_args = "#SBATCH--dependency=afterok:" + str(prev_job_id) + "\n"
                    jd.output += "\n" + tmp_args
                    jd.arguments = c + job_output + " 2>&1 "
                    myjob = js.create_job(jd)
                    myjob.run()
                    jobs.append(myjob)
                    prev_job_id = myjob.get_id().split('-')[1].strip('[').strip(']')
                else:
                    jd.arguments = c + job_output + " 2>&1 "
                    myjob = js.create_job(jd)
                    myjob.run()
                    jobs.append(myjob)

                # myjob.run()
                # jobs.append(myjob)
                print ' * Submitted %s for %s. Output will be written to: %s' % (myjob.id, samp, job_output)

                num += 1

        # Wait for all jobs to finish

        while len(jobs) > 0:
            for job in jobs:
                jobstate = job.get_state()
                print ' * Job %s status: %s' % (job.id, jobstate)
                if jobstate in [saga.job.DONE, saga.job.FAILED]:
                    jobs.remove(job)
            print ""
            time.sleep(60)
        js.close()
        return

    def symlink_fastqs(self):
        """
        Create soft links to original fastqs by renaming, local or remote, using the given sample IDs and the saga module
        :return:
        """
        # command list
        cmds = []
        # cmds = ''

        remote_dirs = False

        # Add commands to the command list

        for samp, fileName in self.sample_fastq.iteritems():
            self.sample_fastq_work[samp] = []
            if len(fileName) < 2:
                symlnk_name = os.path.join(self.fastq_dir, samp + ".fq.gz")
                # cmds.append(' '.join(['/bin/ln', '-s', fileName[0], symlnk_name]))
                cmds.append(' '.join(['/bin/ln', '-s', fileName[0], symlnk_name, "; echo DONE:", fileName[0], ">> "]))
                self.sample_fastq_work[samp].append(symlnk_name)
            else:
                num = 1
                for fq_file in fileName:
                    symlnk_name = os.path.join(self.fastq_dir, samp + "_" + str(num) + ".fq.gz")
                    # cmds.append(' '.join(['/bin/ln','-s', fq_file, symlnk_name]))
                    cmds.append(' '.join(['/bin/ln', '-s', fq_file, symlnk_name, "; echo DONE:", fq_file, ">> "]))
                    self.sample_fastq_work[samp].append(symlnk_name)
                    num += 1
        print cmds

        # setup remote session

        remote_path = self.run_parms['work_dir']

        if self.run_parms['saga_host'] != "localhost":
            session = saga.Session()
            ctx = saga.Context("ssh")
            ctx.user_id = self.run_parms['ssh_user']
            session.add_context(ctx)
            remote_dirs = True
            remote_path = "sftp://" + self.run_parms['saga_host'] + self.run_parms['work_dir']

        # setup basic job parameters

        jd = saga.job.Description()
        jd.executable = ''
        jd.working_directory = self.run_parms['work_dir']
        # jd.output = os.path.join(log_dir, "symlink.stdout")
        # jd.error = os.path.join(log_dir, "symlink.stderr")
        job_output = os.path.join(self.log_dir, "symlink.stdout")
        job_error = os.path.join(self.log_dir, "symlink.stderr")

        # Setup the saga host to use

        js = saga.job.Service("fork://localhost")
        if self.run_parms['saga_host'] != "localhost":
            js = saga.job.Service("ssh://" + self.run_parms['saga_host'], session=session)
        elif self.run_parms['saga_host'] == 'localhost' and 'saga_scheduler' in self.run_parms.keys():
            # js = saga.job.Service(self.run_parms['saga_scheduler'] + "://" + self.run_parms['saga_host'])
            js = saga.job.Service("fork://" + self.run_parms['saga_host'])
        elif self.run_parms['saga_host'] == 'localhost' and 'saga_scheduler' not in self.run_parms.keys():
            self.run_parms['saga_scheduler'] = "fork"
            js = saga.job.Service("fork://" + self.run_parms['saga_host'])

        # Submit jobs

        jobs = []
        for cmd in cmds:
            jd.arguments = cmd + job_output
            myjob = js.create_job(jd)
            myjob.run()
            jobs.append(myjob)

        print ' * Submitted %s. Output will be written to: %s' % (myjob.id, job_output)

        # Wait for all jobs to finish

        while len(jobs) > 0:
            for job in jobs:
                jobstate = job.get_state()
                print ' * Job %s status: %s' % (job.id, jobstate)
                if jobstate in [saga.job.DONE, saga.job.FAILED]:
                    jobs.remove(job)
            print ""
            time.sleep(5)
        js.close()
        return

    def symlink_fastqs_local(self):
        """
        Create symlinks to the original fastqs locally renaming with given sample ids using the os module
        :return:
        """
        for samp, fileName in self.sample_fastq.iteritems():
            self.sample_fastq_work[samp] = []
            if len(fileName) < 2:
                symlnk_name = os.path.join(os.path.dirname(fileName[0]), samp + ".fq.gz")
                os.symlink(symlnk_name, fileName)
                self.sample_fastq_work[samp].append(symlnk_name)
            else:
                num = 1
                for file in fileName:
                    symlnk_name = os.path.join(os.path.dirname(file), samp + "_" + num + ".fq.gz")
                    os.symlink(symlnk_name, file)
                    self.sample_fastq_work[samp].append(symlnk_name)
                    num += 1
        return

    def parse_prog_info(self):
        """
        Read in the sequence of programs to be run for the current workflow
         and their specified parameters
        :return:
        """

        ##******************************************
        ## This whole section needs to be refactored
        ## to allow for program options to be updated

        tool_prefix = []
        for p in self.workflow_sequence:

            # round_counter = 0
            for k, v in p.iteritems():
                new_key = k
                if isinstance(v, dict):
                    # Add the specific program options
                    # Need to modify to dict so that default values can be updated
                    # Right now program options are directly added as text
                    # Also need to edit this in wrappers so that two sets of arg dicts are used
                    # one for options and one for job parms

                    if 'subcommand' in v.keys():
                        # Update current program name by adding the subcommand
                        if len(v['subcommand'].split()) < 2:
                            new_key = '_'.join([k, v['subcommand']])
                        else:
                            # subcommands = '_'.join(v['subcommand'].split())
                            new_key = '_'.join([k, '_'.join(v['subcommand'].split())])

                    # search if the same command was used before
                    tool_prefix.append(new_key)
                    round_counter = self.find_command_rounds(new_key, tool_prefix)

                    # If this command is a repeat update the program key to include the times it was called

                    if len(self.progs.keys()) > 0 and round_counter > 1:
                        # Update Current Program name by adding the number of times called
                        new_key += "_" + self.multi_run_var + "_" + str(round_counter)

                    # Gather all arguments for the program in this list
                    self.progs[new_key] = []

                    self.prog_suffix_type[new_key] = 'default'
                    self.prog_input_suffix[new_key] = 'default'
                    self.prog_output_suffix[new_key] = 'default'


                    if 'suffix' in v.keys():
                        suffixes = v['suffix']
                        self.prog_suffix_type[new_key] = "custom"

                        if 'input' in suffixes.keys():
                            self.prog_input_suffix[new_key] = suffixes['input']
                        if 'output' in suffixes.keys():
                            self.prog_output_suffix[new_key] = suffixes['output']

                    #todo add an else here

                    if 'options' in v.keys():
                        for k1, v1 in v['options'].iteritems():
                            # Should we test for flag options?
                            if v1 is not None:

                                # This If-else block checks if options are repeated for example
                                # in GATK -knownSites can be specified multiple times

                                if not isinstance(v1, list):
                                    self.progs[new_key].append("%s %s" % (k1, v1))
                                else:  # isinstance(v1, list):
                                    for v11 in v1:
                                        self.progs[new_key].append("%s %s" % (k1, v11))
                            else:
                                print "Flag type argument " + k1
                                self.progs[new_key].append("%s" % (k1))
                    else:
                        self.progs[new_key].append('')

                    # Add the specific program job parameters
                    if 'job_params' in v.keys():
                        self.prog_job_parms[new_key] = v['job_params']
                    else:
                        self.prog_job_parms[new_key] = 'default'

                # Todo should we use an else here instead of elif
                elif v == 'default':

                    tool_prefix.append(new_key)
                    round_counter = self.find_command_rounds(new_key, tool_prefix)

                    if len(self.progs.keys()) > 0 and round_counter > 1:
                        # Update Current Program name by adding the number of times called
                        new_key += "_" + self.multi_run_var + "_" + str(round_counter)

                    self.progs[new_key] = []
                    self.progs[new_key].append('')
                    self.prog_job_parms[new_key] = 'default'
                    self.prog_input_suffix[new_key] = 'default'
                    self.prog_output_suffix[new_key] = 'default'
                    self.prog_suffix_type[new_key] = 'default'


        self.progs = OrderedDict(reversed(self.progs.items()))
        # print self.progs
        return

    def find_command_rounds(self, new_key, prog_list):
        """
        Find the number of times a program has been called
        :param new_key:
        :param prog_list:
        :return:
        """
        round_cnt = sum([new_key in S for S in prog_list])
        return round_cnt


    def update_job_parms(self, key):
        self.new_base_kwargs = copy.deepcopy(self.base_kwargs)
        if isinstance(self.prog_job_parms, dict) and self.prog_job_parms[key] == 'default':
            print "Using default **kwarg Values"
            self.new_base_kwargs['job_parms_type'] = "default"
            self.new_base_kwargs['job_parms'] = self.job_params
            print self.new_base_kwargs['job_parms']
        else:
            print "Using Custom Values for job parms"
            self.new_base_kwargs['job_parms_type'] = "custom"
            self.new_base_kwargs['add_job_parms'] = self.prog_job_parms[key]
            print self.new_base_kwargs['job_parms']

        # Alternate version
        # if isinstance(self.prog_job_parms, dict) and self.prog_job_parms[key] != 'default':
        #         self.new_base_kwargs['job_parms_type'] = "custom"
        #         self.new_base_kwargs['add_job_parms'] = self.prog_job_parms[key]
        # else:
        #     print "Using default Values for job parms"
        #     self.new_base_kwargs['job_parms_type'] = "default"
        return self.new_base_kwargs

    def update_prog_suffixes(self, key):
        if self.prog_suffix_type[key] != 'default':
            self.new_base_kwargs['suffix_type'] = "custom"
        else:
            print "Using default **kwarg Values"
            self.new_base_kwargs['suffix_type'] = "default"

        self.new_base_kwargs['suffix'] = {"input": self.prog_input_suffix[key],
                                          "output": self.prog_output_suffix[key]}
        return self.new_base_kwargs

    def create_qiime_inputs(self):
        ln_com = 'ln -s ' + self.base_kwargs['qiime_info']["--input-path"] + ' ' + self.base_kwargs['qiime_dir'] + '/'
        cp_com = 'cp ' + self.base_kwargs['qiime_info']["--m-barcodes-file"] + ' ' + self.run_parms['qiime_dir'] + '/'
        print cp_com
        print ln_com
        subprocess.check_output(cp_com, shell=True)
        subprocess.check_output(ln_com, shell=True)
        return

class RnaSeqFlow(BaseWorkflow):
    allTasks = []
    progs_job_parms = dict()

    def __init__(self, parmsfile):
        self.init(parmsfile)

        # Create Expression quantification directory for RNASeq
        self.expression_dir = os.path.join(self.work_dir, 'expression')

        # Update kwargs to include directory for expression quantification
        self.base_kwargs['expression_dir'] = self.expression_dir
        self.new_base_kwargs = copy.deepcopy(self.base_kwargs)
        # Update paths to check to include directory for expression quantification
        self.paths_to_test += [self.expression_dir]

        return

    def chain_commands(self):
        """
        Create a n ordered list of commands to be run sequentially for each sample for use with the Luigi scheduler.
        :return:
        """

        for samp, file in self.sample_fastq_work.iteritems():
            print "\n *******Commands for Sample:%s ***** \n" % (samp)
            samp_progs = []

            for key in self.progs.keys():
                new_base_kwargs = self.update_job_parms(key)
                if key == 'gsnap':
                    # update job parms
                    # new_base_kwargs = self.update_job_parms(key)
                    # Add additional samtools processing steps to GSNAP output

                    tmp_prog = self.prog_wrappers['bammarkduplicates2']('bammarkduplicates2', samp,
                                                                        stdout=os.path.join(self.log_dir,
                                                                                            samp + '_bamdup.log'),
                                                                        **dict(self.base_kwargs)
                                                                        )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samindex']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir, samp + '_bamidx.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    # TODO why use new_base_kwargs instead of base_kwargs like the others
                    tmp_prog = self.prog_wrappers['samsort']('samtools', samp,
                                                             stdout=os.path.join(self.log_dir, samp + '_bamsrt.log'),
                                                             **dict(new_base_kwargs)
                                                             )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtomapped']('samtools', samp,
                                                                 stdout=os.path.join(self.log_dir,
                                                                                     samp + '_bamtomappedbam.log'),
                                                                 **dict(self.base_kwargs)
                                                                 )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtounmapped']('samtools', samp,
                                                                   stdout=os.path.join(self.log_dir,
                                                                                       samp + '_bamtounmappedbam.log'),
                                                                   **dict(self.base_kwargs)
                                                                   )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samtobam']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir,
                                                                                  samp + '_samtobam.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.align_dir, samp + '.sam'),
                                                       **dict(new_base_kwargs))

                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                # Remove the duprun from the the key and create the wrapper command
                elif self.multi_run_var in key:
                    input_list = key.split('_')
                    idx_to_rm = [i for i, s in enumerate(input_list) if self.multi_run_var in s][0]
                    del input_list[idx_to_rm:]
                    new_key = '_'.join(input_list)

                    # Testing here
                    tmp_prog = self.prog_wrappers[new_key](new_key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.run_parms['work_dir'],
                                                                               self.run_parms['log_dir'],
                                                                               samp + '_' + key + '.log'),
                                                       **dict(self.new_base_kwargs)
                                                       )

                    # print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))
                else:
                    # print "\n**** Base kwargs *** \n"
                    # print self.base_kwargs
                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.run_parms['work_dir'],
                                                                           self.run_parms['log_dir'],
                                                                           samp + '_' + key + '.log'),
                                                       **dict(self.new_base_kwargs)
                                                       )

                    print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))

            self.allTasks.append(jsonpickle.encode(TaskSequence(samp_progs, n_tasks=len(samp_progs))))

        return


class DnaSeqFlow(BaseWorkflow):
    allTasks = []
    progs_job_parms = dict()

    def __init__(self, parmsfile):
        self.init(parmsfile)

        # Create  quantification directory for
        #self.expression_dir = os.path.join(self.work_dir, 'expression')

        # Update kwargs to include directory for expression quantification
        #self.base_kwargs['expression_dir'] = self.expression_dir

        # Update paths to check to include directory for expression quantification
        #self.paths_to_test += self.expression_dir

        return

    def chain_commands(self):
        """
        Create a n ordered list of commands to be run sequentially for each sample for use with the Luigi scheduler.
        :return:
        """

        for samp, file in self.sample_fastq_work.iteritems():
            print "\n *******Commands for Sample:%s ***** \n" % (samp)
            samp_progs = []

            for key in self.progs.keys():
                new_base_kwargs = self.update_job_parms(key)
                if key == 'bwa_mem':
                    # update job parms
                    # new_base_kwargs = self.update_job_parms(key)
                    # Add additional samtools processing steps to GSNAP output

                    tmp_prog = self.prog_wrappers['bammarkduplicates2']('bammarkduplicates2', samp,
                                                                        stdout=os.path.join(self.log_dir, samp + '_bamdup.log'),
                                                                        **dict(self.base_kwargs)
                                                                        )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samindex']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir, samp + '_bamidx.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samsort']('samtools', samp,
                                                             stdout=os.path.join(self.log_dir, samp + '_bamsrt.log'),
                                                             **dict(new_base_kwargs)
                                                             )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtomapped']('samtools', samp,
                                                                 stdout=os.path.join(self.log_dir,
                                                                                     samp + '_bamtomappedbam.log'),
                                                                 **dict(self.base_kwargs)
                                                                 )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtounmapped']('samtools', samp,
                                                                   stdout=os.path.join(self.log_dir,
                                                                                       samp + '_bamtounmappedbam.log'),
                                                                   **dict(self.base_kwargs)
                                                                   )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samtobam']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir,
                                                                                  samp + '_samtobam.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))


                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.align_dir, samp + '.sam'),
                                                       **dict(new_base_kwargs))

                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                elif self.multi_run_var in key:
                    input_list = key.split('_')
                    idx_to_rm = [i for i, s in enumerate(input_list) if self.multi_run_var in s][0]
                    del input_list[idx_to_rm:]
                    new_key = '_'.join(input_list)
                    tmp_prog = self.prog_wrappers[new_key](new_key, samp, *self.progs[key],
                                                           stdout=os.path.join(self.run_parms['work_dir'],
                                                                               self.run_parms['log_dir'],
                                                                               samp + '_' + key + '.log'),
                                                           **dict(self.new_base_kwargs)
                                                           )

                    # print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))
                else:
                    # print "\n**** Base kwargs *** \n"
                    # print self.base_kwargs
                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.run_parms['work_dir'],
                                                                           self.run_parms['log_dir'],
                                                                           samp + '_' + key + '.log'),
                                                       **dict(self.new_base_kwargs)
                                                       )
                    print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))
                    # print self.job_params
                    # tmp_prog.job_parms['mem'] = 1000
                    # tmp_prog.job_parms['time'] = 80
                    # tmp_prog.job_parms['ncpus'] = 1
                    ## Need to fix to read in options and parms

            # Remove the first job and re-add it without any targets

            # del samp_progs[-1]
            # tmp_prog = self.prog_wrappers[key](key, samp,
            #                                    stdout=os.path.join(self.log_dir,samp + '_' + key + '.log'),
            #                                    **dict(self.base_kwargs)
            #                                    )
            # tmp_prog.luigi_source = "None"
            # samp_progs.append(jsonpickle.encode(tmp_prog))
            # print "\n**** Command after removal *** \n"
            # print tmp_prog.run_command
            # for k,v in tmp_prog.__dict__.iteritems():
            #     print k,v
            # # print self.job_params
            # # print tmp_prog.job_parms
            # print tmp_prog.luigi_source
            # self.allTasks.append(TaskSequence(samp_progs))
            self.allTasks.append(jsonpickle.encode(TaskSequence(samp_progs, n_tasks=len(samp_progs))))
            # print self.allTasks

        return


class GatkFlow(BaseWorkflow):
    allTasks = []
    progs_job_parms = dict()

    def __init__(self, parmsfile):
        self.init(parmsfile)

        # Create  directory for storing GATK files
        #self.gatk_dir = os.path.join(self.work_dir, 'gatk_results')

        # Update kwargs to include directory for VCFs
        #self.base_kwargs['gatk_dir'] = self.gatk_dir

        self.new_base_kwargs = copy.deepcopy(self.base_kwargs)

        # Update paths to check to include directory for VCFs
        #self.paths_to_test += [self.gatk_dir]

        return

    def chain_commands(self):
        """
        Create a n ordered list of commands to be run sequentially for each sample for use with the Luigi scheduler.
        :return:
        """

        for samp, file in self.sample_fastq_work.iteritems():
            print "\n *******Commands for Sample:%s ***** \n" % (samp)
            samp_progs = []

            for key in self.progs.keys():
                print "Printing original Parms\n"
                print self.prog_job_parms
                self.update_job_parms(key)
                self.update_prog_suffixes(key)
                if self.multi_run_var in key:
                    input_list = key.split('_')
                    idx_to_rm = [i for i, s in enumerate(input_list) if self.multi_run_var in s][0]
                    del input_list[idx_to_rm:]
                    new_key = '_'.join(input_list)
                    tmp_prog = self.prog_wrappers[new_key](key, samp, *self.progs[key], **dict(self.new_base_kwargs))

                    print "new_key", new_key, key
                    print self.progs[key], self.progs[new_key]
                    print tmp_prog.run_command
                    print tmp_prog.job_parms

                    samp_progs.append(jsonpickle.encode(tmp_prog))
                else:
                    # print "\n**** Base kwargs *** \n"
                    # print self.base_kwargs
                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key], **dict(self.new_base_kwargs))

                    print self.progs[key]
                    print tmp_prog.run_command
                    print tmp_prog.job_parms
                    samp_progs.append(jsonpickle.encode(tmp_prog))

            self.allTasks.append(jsonpickle.encode(TaskSequence(prog_parms=samp_progs, n_tasks=len(samp_progs))))

        return

    def chain_commands_qiime(self):
        """
        Create a n ordered list of commands to be run sequentially for each sample for use with the Luigi scheduler.
        :return:
        """

        # for samp, file in self.sample_fastq_work.iteritems():
        #     print "\n *******Commands for Sample:%s ***** \n" % (samp)
        samp_progs = []
        if '--output-suffix' not in self.base_kwargs['qiime_info'].keys():
            samp = self.base_kwargs['qiime_info']['--type']
        else:
            samp = self.base_kwargs['qiime_info']['--output-suffix']
        # print "Sample Name"
        # print samp

        for key in self.progs.keys():
            print "Printing original Parms\n"
            print self.prog_job_parms
            self.update_job_parms(key)
            self.update_prog_suffixes(key)
            if self.multi_run_var in key:
                input_list = key.split('_')
                idx_to_rm = [i for i, s in enumerate(input_list) if self.multi_run_var in s][0]
                del input_list[idx_to_rm:]
                new_key = '_'.join(input_list)
                tmp_prog = self.prog_wrappers[new_key](key, samp, *self.progs[key], **dict(self.new_base_kwargs))

                print "new_key", new_key, key
                print self.progs[key], self.progs[new_key]
                print tmp_prog.run_command
                print tmp_prog.job_parms

                samp_progs.append(jsonpickle.encode(tmp_prog))
            else:
                # print "\n**** Base kwargs *** \n"
                # print self.base_kwargs
                tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key], **dict(self.new_base_kwargs))

                print self.progs[key]
                print tmp_prog.run_command
                print tmp_prog.job_parms
                samp_progs.append(jsonpickle.encode(tmp_prog))

            self.allTasks.append(jsonpickle.encode(TaskSequence(prog_parms=samp_progs, n_tasks=len(samp_progs))))

        return


class GatkFlow2(BaseWorkflow):
    allTasks = []
    progs_job_parms = dict()

    def __init__(self, parmsfile):
        self.init(parmsfile)

        # Create  directory for storing GATK files
        self.gatk_dir = os.path.join(self.work_dir, 'gatk_results')

        # Update kwargs to include directory for VCFs
        self.base_kwargs['gatk_dir'] = self.gatk_dir
        self.new_base_kwargs = copy.deepcopy(self.base_kwargs)
        # Update paths to check to include directory for VCFs
        self.paths_to_test += [self.gatk_dir]

        return

    def chain_commands(self):
        """
        Create a n ordered list of commands to be run sequentially for each sample for use with the Luigi scheduler.
        :return:
        """

        for samp, file in self.sample_fastq_work.iteritems():
            print "\n *******Commands for Sample:%s ***** \n" % (samp)
            samp_progs = []

            for key in self.progs.keys():
                new_base_kwargs = self.update_job_parms(key)
                if key == 'bwa_mem':
                    # update job parms
                    # new_base_kwargs = self.update_job_parms(key)
                    # Add additional samtools processing steps to GSNAP output

                    tmp_prog = self.prog_wrappers['bammarkduplicates2']('bammarkduplicates2', samp,
                                                                        stdout=os.path.join(self.log_dir,
                                                                                            samp + '_bamdup.log'),
                                                                        **dict(self.base_kwargs)
                                                                        )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samindex']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir, samp + '_bamidx.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samsort']('samtools', samp,
                                                             stdout=os.path.join(self.log_dir, samp + '_bamsrt.log'),
                                                             **dict(new_base_kwargs)
                                                             )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtomapped']('samtools', samp,
                                                                 stdout=os.path.join(self.log_dir,
                                                                                     samp + '_bamtomappedbam.log'),
                                                                 **dict(self.base_kwargs)
                                                                 )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['bamtounmapped']('samtools', samp,
                                                                   stdout=os.path.join(self.log_dir,
                                                                                       samp + '_bamtounmappedbam.log'),
                                                                   **dict(self.base_kwargs)
                                                                   )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers['samtobam']('samtools', samp,
                                                              stdout=os.path.join(self.log_dir,
                                                                                  samp + '_samtobam.log'),
                                                              **dict(self.base_kwargs)
                                                              )
                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.align_dir, samp + '.sam'),
                                                       **dict(new_base_kwargs))

                    print tmp_prog.run_command

                    samp_progs.append(jsonpickle.encode(tmp_prog))

                elif self.multi_run_var in key:
                    input_list = key.split('_')
                    idx_to_rm = [i for i, s in enumerate(input_list) if self.multi_run_var in s][0]
                    del input_list[idx_to_rm:]
                    new_key = '_'.join(input_list)
                    # Testing here
                    tmp_prog = self.prog_wrappers[new_key](key, samp, *self.progs[key],
                                                           stdout=os.path.join(self.run_parms['work_dir'],
                                                                               self.run_parms['log_dir'],
                                                                               samp + '_' + key + '.log'),
                                                           **dict(self.new_base_kwargs)
                                                           )

                    # print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))
                else:
                    # print "\n**** Base kwargs *** \n"
                    # print self.base_kwargs
                    tmp_prog = self.prog_wrappers[key](key, samp, *self.progs[key],
                                                       stdout=os.path.join(self.run_parms['work_dir'],
                                                                           self.run_parms['log_dir'],
                                                                           samp + '_' + key + '.log'),
                                                       **dict(self.new_base_kwargs)
                                                       )
                    print tmp_prog.run_command
                    samp_progs.append(jsonpickle.encode(tmp_prog))

            self.allTasks.append(jsonpickle.encode(TaskSequence(prog_parms=samp_progs, n_tasks=len(samp_progs))))

        return





def rna_seq_main():

    print "success intall worked"
    #sys.exit(0)
    # parmsfile = "/home/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run_remote_tdat.yaml"
    parmsfile = sys.argv[1]
    rw1 = RnaSeqFlow(parmsfile)

    rw1.parse_prog_info()


    print "\n***** Printing Chained Commands ******\n"

    # Actual jobs start here
    rw1.test_paths()
    if 'sra' in rw1.sample_manifest.keys():
        rw1.download_sra_cmds()
        if rw1.sra_info['downloads']:
            sys.exit(0)
    else:
        rw1.symlink_fastqs()
    rw1.chain_commands()
    # todo make the number of workers a parameter for luigi as slurm has limits on the number of submissions and
    # this can breask luigi

    luigi.build([TaskFlow(tasks=rw1.allTasks, task_name=rw1.bioproject)], local_scheduler=True,
                workers=min(50, len(rw1.sample_fastq_work.keys())), lock_size=1, log_level='WARNING')
    return


def dna_seq_main():
    print "success intall worked"
    # sys.exit(0)
    # parmsfile = "/home/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run_remote_tdat.yaml"
    parmsfile = sys.argv[1]
    dw1 = DnaSeqFlow(parmsfile)

    dw1.parse_prog_info()

    print "\n***** Printing Chained Commands ******\n"

    # Actual jobs start here
    dw1.test_paths()
    if 'sra' in dw1.sample_manifest.keys():
        dw1.download_sra_cmds()
        if dw1.sra_info['downloads']:
            sys.exit(0)
    else:
        dw1.symlink_fastqs()

    dw1.chain_commands()
    # todo make the number of workers a parameter for luigi as slurm has limits on the number of submissions and
    # this can breask luigi

    luigi.build([TaskFlow(tasks=dw1.allTasks, task_name=dw1.bioproject)], local_scheduler=True,
                workers=min(50, len(dw1.sample_fastq_work.keys())), lock_size=1, log_level='WARNING')
    return

def gatk_main():
    print "success intall worked"
    parmsfile = sys.argv[1]
    gt1 = GatkFlow(parmsfile)

    gt1.parse_prog_info()

    print "\n***** Printing Chained Commands ******\n"

    # Actual jobs start here
    gt1.test_paths()

    if 'sra' in gt1.sample_manifest.keys():
        gt1.download_sra_cmds()
        if gt1.sra_info['downloads']:
            sys.exit(0)
    elif 'qiime' in gt1.sample_manifest.keys():
        gt1.create_qiime_inputs()
    else:
        gt1.symlink_fastqs()

    luigi_workers =1
    if 'qiime' in gt1.sample_manifest.keys():
        gt1.chain_commands_qiime()
    else:
        gt1.chain_commands()
        luigi_workers = len(gt1.sample_fastq_work.keys())
    # todo make the number of workers a parameter for luigi as slurm has limits on the number of submissions and
    # this can breask luigi

    luigi.build([TaskFlow(tasks=gt1.allTasks, task_name=gt1.bioproject)], local_scheduler=True,
                workers=min(50, luigi_workers), lock_size=1, log_level='WARNING')
    return



if __name__ == '__main__':
    rna_seq_main()
