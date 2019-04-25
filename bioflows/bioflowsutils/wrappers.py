# BioFlow - Package for  automating bio-informatics workflows
# Copyright (c) 2012-2014 Brown University. All rights reserved.
#
# This file is part of BioFlows.
#
# BioFlows is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BioFlows is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioFlows.  If not, see <http://www.gnu.org/licenses/>.

"""
A series of wrappers for external calls to various bioinformatics tools.
"""

import copy
import hashlib
import os
import subprocess
import sys
from itertools import chain

# import config
# import diagnostics
import utils


class BaseWrapper(object):
    """
    A base class that handles generic wrapper functionality.

    Wrappers for specific programs should inherit this class, call `self.init`
    to specify their `name` (which is a key into the executable entries in the
    BioLite configuration file), and append their arguments to the `self.args`
    list.

    By convention, a wrapper should call `self.run()` as the final line in its
    `__init__` function. This allows for clean syntax and use of the wrapper
    directly, without assigning it to a variable name, e.g.

    wrappers.MyWrapper(arg1, arg2, ...)

    When your wrapper runs, BaseWrapper will do the following:

    * log the complete command line to diagnostics;
    * optionally call the program with a version flag (invoked with `version`)
      to obtain a version string, then log this to the :ref:`programs-table`
      along with a hash of the binary executable file;
    * append the command's stderr to a file called `name`.log in the CWD;
    * also append the command's stdout to the same log file, unless you set
      `self.stdout`, in which case stdout is redirected to a file of that name;
    * on Linux, add a memory profiling library to the LD_PRELOAD environment
      variable;
    * call the command and check its return code (which should be 0 on success,
      unless you specify a different code with `self.return_ok`), optionally
      using the CWD specified in `self.cwd` or the environment specified in
      `self.env`.
    * parse the stderr of the command to find [biolite.profile] markers and
      use the rusage values from `utils.safe_call` to populate a profile
      entity in the diagnostics with walltime, usertime, systime, mem, and
      vmem attributes.
    """
    # hold the input/output suffixes for output
    in_suffix = ''
    out_suffix = ''
    add_args = []
    target = ''
    stdout = ''
    args = []
    input = ''

    def __init__(self, name, **kwargs):

        self.name = name
        self.prog_id = kwargs.get('prog_id')
        # self.shell = '/bin/sh'
        self.cmd = None
        self.run_command = None
        self.args = []
        self.conda_command = kwargs.get('conda_command')
        self.job_parms = kwargs.get('job_parms')
        self.paired_end = kwargs.get('paired_end', False)
        self.cwd = kwargs.get('cwd', os.getcwd())
        self.log_dir = kwargs.get('log_dir', os.path.join(os.getcwd(), "logs"))
        self.align_dir = kwargs.get('align_dir', os.path.join(os.getcwd(), 'align_dir'))
        self.qc_dir = kwargs.get('qc_dir', os.path.join(os.getcwd(), 'qc_dir'))
        self.scripts_dir = kwargs.get('scripts_dir', os.path.join(self.log_dir, 'scripts_dir'))
        self.intermediary_dir = kwargs.get('intermediary_dir', os.path.join(os.getcwd(), 'intermediary_files'))
        ## Define the checkpoint files
        ##self.luigi_source = os.path.join(self.cwd, 'checkpoints', kwargs.get('source', "None"))
        self.luigi_source = "Present"
        self.luigi_target = os.path.join(self.cwd, 'checkpoints', kwargs.get('target', "None"))

        ## Below for testing only
        self.local_target = kwargs.get('local_targets', True)
        if self.local_target:
            self.luigi_local_target = os.path.join(
                kwargs.get('luigi_local_path', "/Users/aragaven/scratch/test_workflow"),
                kwargs.get('target', "None"))
        self.stdout = kwargs.get('stdout')
        self.stderr = kwargs.get('stderr')
        self.stdout_append = kwargs.get('stdout_append')
        # self.pipe = kwargs.get('pipe')
        self.env = os.environ.copy()
        self.max_concurrency = kwargs.get('max_concurrency', 1)
        self.prog_args = dict()
        for k, v in kwargs.iteritems():
            self.prog_args[k] = v
        self.setup_command()
        # self.output_patterns = None
        return

    init = __init__
    """A shortcut for calling the BaseWrapper __init__ from a subclass."""

    # def check_input(self, flag, path):
    #     """
    #     Turns path into an absolute path and checks that it exists, then
    #     appends it to the args using the given flag (or None).
    #     """
    #     path = os.path.abspath(path)
    #     if os.path.exists(path):
    #         if flag:
    #             self.args.append(flag)
    #         self.args.append(path)
    #     else:
    #         utils.die("input file for flag '%s' does not exists:\n  %s" % (flag, path))

    def prog_name_clean(self, name):
        """
        A function to strip the run name from programs
        :return:
        """
        if 'round' in name:
            input_list = name.split('_')
            idx_to_rm = [i for i, s in enumerate(input_list) if 'round' in s][0]
            del input_list[idx_to_rm:]
            new_name = '_'.join(input_list)
        else:
            new_name = name
        return new_name

    def add_threading(self, flag):
        """
        Indicates that this wrapper should use threading by appending an
        argument with the specified `flag` followed by the number of threads
        specified in the BioLite configuration file.
        """
        # threads = min(int(config.get_resource('threads')), self.max_concurrency)
        threads = self.max_concurrency
        if threads > 1:
            self.args.append(flag)
            self.args.append(threads)
        return

    def add_openmp(self):
        """
        Indicates that this wrapper should use OpenMP by setting the
        $OMP_NUM_THREADS environment variable equal to the number of threads
        specified in the BioLite configuration file.
        """
        ##threads = min(int(config.get_resource('threads')), self.max_concurrency)
        threads = self.max_concurrency
        self.env['OMP_NUM_THREADS'] = str(threads)

    def join_split_cmd(self, name):
        ''' Check if cmd needs to be split

         When cmds are passed in the YAML control file sub cmds are joined by an underscore
         This function will split the commands as needed to run the program
        :param name:
        :return:
        '''
        if len(name.split('_')) > 0:
            return ' '.join(name.split('_'))
        else:
            return name

    def setup_command(self):
        """
        Generate the command to be run based on the input. There are three cases and more can defined based on the YAML
        1) Just a name is given and this is also the executable name and is available in the PATH
        2) The name is given along-with a separate sub-command to be run. A simple example will be `samtools sort`
         this definition need to be implemented
        :param self: 
        :return: 
        """
        # Setup the command to run

        if not self.cmd:
            self.cmd = [self.name]  # change cmd to be name if specific command is not specified
        else:
            self.cmd = list(self.cmd.split())
        return

    # TODO fix this function
    def version(self, flag=None):
        """
        Generates and logs a hash to distinguish this particular installation
        of the program (on a certain host, with a certain compiler, program
        version, etc.)

        Specify the optional 'binary' argument if the wrapper name is not
        actually the program, e.g. if your program has a Perl wrapper script.
        Set 'binary' to the binary program that is likely to change between
        versions.

        Specify the optional 'cmd' argument if the command to run for version
        information is different than what will be invoked by `run` (e.g.
        if the program has a perl wrapper script, but you want to version an
        underlying binary executable).
        """
        cmd = copy.deepcopy(self.cmd)
        if flag:
            cmd.append(flag)
        else:
            cmd.append('-v')
        # Run the command.

        # self.env['PATH'] = self.conda_command.split()[2] + "/bin:" + self.env['PATH']
        print "\n ***** print PATH ***** \n"
        print self.env['PATH']
        try:
            vstring = subprocess.check_output(cmd, env=self.env, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            vstring = e.output
        except OSError as e:
            utils.failed_executable(cmd[0], e)

            # Generate a hash.
            # vhash = diagnostics.log_program_version(self.name, vstring, path)
            # if vhash:
            # 	diagnostics.prefix.append(self.name)
            # 	diagnostics.log('version', vhash)
            # 	diagnostics.prefix.pop()

    def version_jar(self):
        """
        Special case of version() when the executable is a JAR file.
        """
        # cmd = config.get_command('java')
        cmd = ['java ']
        cmd.append('-jar')
        cmd += self.cmd
        self.version(cmd=cmd, path=self.cmd[0])
        return

    def name_clean(self):
        """
        A function to strip the Xmx tags for Java programs
        and any other tags from other programs mainly the -T from gatk
        """
        input_list = self.name.split()
        if "Xmx" in self.name:
            idx_to_rm = [i for i, s in enumerate(input_list) if 'Xmx' in s][0]
            del input_list[idx_to_rm]
        if "-T" in self.name:
            idx_to_rm = [i for i, s in enumerate(input_list) if '-T' in s][0]
            del input_list[idx_to_rm]
        if "bqsr" in self.name:
            idx_to_rm = [i for i, s in enumerate(input_list) if 'bqsr' in s][0]
            del input_list[idx_to_rm]
        new_name = '_'.join(input_list)
        return new_name

    def setup_run(self, add_command=None):

        """
        Call this function at the end of your class's `__init__` function.
        """

        cmd = self.cmd
        stderr = os.path.join(self.log_dir, '_'.join([self.input, self.prog_id, 'err.log']))

        if self.stderr is not None:
            stderr = self.stderr
        if len(self.name.split()) > 1:
            stderr = os.path.join(self.log_dir, '_'.join([self.input, self.prog_id, 'err.log']))
            # MAYBE redundant
        self.args.append('2>>' + stderr)

        # if self.pipe:
        # 	self.args += ('|', self.pipe, '2>>' + stderr)

        # Write to a stdout file if it was set by the derived class.
        # Otherwise, stdout and stderr will be combined into the log file.

        if self.stdout:
            stdout = os.path.abspath(self.stdout)
            self.args.append('1>' + stdout)
        elif self.stdout_append:
            stdout = os.path.abspath(self.stdout_append)
            self.args.append('1>>' + stdout)
        else:
            self.args.append('1>>' + stderr)

        cmd = ' '.join(chain(cmd, map(str, self.args)))

        if add_command is not None:
            cmd += "; " + add_command

        self.run_command = cmd
        return

    def run_jar(self, mem=None):
        '''
        Special case of run() when the executable is a JAR file. This may be deprecated as we  will use conda for all
        packages

        :param mem:
        :return:
        '''

        # cmd = config.get_command('java')
        cmd = ['java ']
        if mem:
            cmd.append('-Xmx%s' % mem)
        cmd.append('-jar')
        cmd += self.cmd
        self.run(cmd)

    def update_file_suffix(self, input_default=None, output_default=None, **kwargs):
        """
        Update the file suffix for each wrapper based on whether custom input/output suffixes are provided. When the
        defaults for inputs and/or outputs are not provided then it is expected that the user will have to provide a
        suffix. For example with samtools view an output suffix is always required

        :param input_default:  Default suffix for input to the program
        :param output_default:  default suffix for output to the program
        :param kwargs:  this is new_base_kwargs passed on from the workflow class to each program
        :return:

        """

        if kwargs['suffix_type'] != "custom":
            if input_default is not None and output_default is not None:
                self.in_suffix = input_default
                self.out_suffix = output_default
            elif input_default is not None and output_default is None:
                print "Error!!! you need to specify an output suffix"
                sys.exit(0)
            elif input_default is None and output_default is not None:
                print "Error!!! you need to specify an input suffix"
                sys.exit(0)
            else:
                print "Error!!! you need to specify BOTH input  and output suffixes"
                sys.exit(0)
        else:
            if kwargs['suffix']['output'] != "default":
                self.out_suffix = kwargs['suffix']['output']
            else:
                self.out_suffix = output_default
            if kwargs['suffix']['input'] != "default":
                self.in_suffix = kwargs['suffix']['input']
            else:
                self.in_suffix = input_default
        return

    def reset_add_args(self):
        """
        This function needed to reset the add args when wrapper class is called multiple time
        Should perhaps be moved to the basewrapper class
        :return:

        """
        self.add_args = []
        return

    def update_default_args(self, default_args, *args, **kwargs):
        """
        Override the default values for program args to those provided by the user for a  wrapper
        :param default_args:
        :param args:
        :param kwargs:
        :return:
        """
        tmp_args = []
        tmp_args += args
        args_list = [y for x in args for y in x.split()]

        for k, v in default_args.iteritems():
            if k not in args_list:
                tmp_args += [' '.join([k, str(v)])]
            else:
                # k_pos = [i for i, s in enumerate(args) if k in s][0]
                # print "Printing tmp_args while updating"
                # print tmp_args[k_pos]
                # tmp_args[k_pos] = tmp_args[k_pos].replace(v, v))
                # print tmp_args[k_pos]
                pass

        return tmp_args

### Third-party command line tools ###

class FastQC(BaseWrapper):
    """
    A wrapper for FastQC.
    http://www.bioinformatics.bbsrc.ac.uk/projects/fastqc/
    """


    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + "_" + name + "_" + hashlib.sha224(input + "_" + name).hexdigest() + ".txt"

        # only need second part as fastqc is run on each file sequentially in the same job
        if kwargs.get('paired_end'):
            kwargs['target'] = input + "_" + name + "_PE_" + hashlib.sha224(
                input + "_" + name + "_PE").hexdigest() + ".txt"

        # Ssetup inputs/outputs
        self.update_file_suffix(input_default=".fq.gz", output_default="", **kwargs)

        kwargs['stdout_append'] = os.path.join(kwargs['log_dir'], input + '_' + name + '.log')
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)
        self.init(name, **kwargs)
        self.args += [' -o ' + self.qc_dir]
        self.args += args

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 1000, 'time': 80, 'ncpus': 1})

        if self.paired_end:

            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1" + self.in_suffix))
            self.setup_run()
            run_cmd1 = self.run_command

            ## Re initialize the object for the second in pair
            self.init(name, **kwargs)
            self.args += [' -o ' + self.qc_dir]
            self.args += args
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2" + self.in_suffix))
            self.setup_run()
            run_cmd2 = self.run_command

            self.run_command = run_cmd1 + "; " + run_cmd2
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + self.in_suffix))
            self.setup_run()

        return


class Gsnap(BaseWrapper):
    """
    A wrapper for gsnap 
    
    """


    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        ## Setup the inputs/output
        self.update_file_suffix(input_default=".fq.gz", output_default=".sam", **kwargs)
        ## set the checkpoint target file
        kwargs['target'] = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
            input + "_" + name + "_" + self.out_suffix).hexdigest() + ".txt"

        kwargs['stdout'] = os.path.join(kwargs['align_dir'], input + self.out_suffix)
        kwargs['prog_id'] = name

        name = self.prog_name_clean(name)
        self.init(name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                # TODO make sure threads are not given in the args
                self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]
        else:
            self.job_parms.update({'mem': 1000, 'time': 80, 'ncpus': 1})

        if self.paired_end:
            kwargs['source'] = hashlib.sha224(input + '_2_fastqc.gzip').hexdigest() + ".txt"
        else:
            kwargs['source'] = hashlib.sha224(input + '_fastqc.gzip').hexdigest() + ".txt"

        self.setup_args(*args)

        self.args += args

        if self.paired_end:
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1" + self.in_suffix))
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2" + self.in_suffix))
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + self.in_suffix))
        # self.cmd = ' '.join(chain(self.cmd, map(str, self.args), map(str,input)))

        self.setup_run()
        return

    def setup_args(self, *args):
        """
        setup default args
        :param args: The arguments from the Options section in the YAML
        :return:
        """
        if any("--gunzip" in a for a in args):
            pass
        else:
            self.args += ["--gunzip"]
        if any("-A sam" in a for a in args):
            pass
        else:
            self.args += ["-A sam"]
        if any("-N1" in a for a in args):
            pass
        else:
            self.args += ["-N1"]
        if any("--use-shared-memory=0" in a for a in args):
            pass
        else:
            self.args += ["--use-shared-memory=0"]
        return

class Kneaddata(BaseWrapper):
    '''
    Wrapper class for kneaddata
    '''
    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        self.args += args
        self.args.append(input)
        self.setup_run()
        return

class Biobambam(BaseWrapper):
    '''
    Wrapper class to mark duplicates in a bam using biobambam
    '''

    # TODO: Clean up

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        # TODO add update to input/output suffixes here
        if name.split("_")[0] == "bammarkduplicates2":
            self.update_file_suffix(input_default=".srtd.bam", output_default=".dup.srtd.bam", **kwargs)
        elif name.split("_")[0] == "bamsort":
            self.update_file_suffix(input_default=".bam", output_default=".srtd.bam", **kwargs)

        kwargs['target'] = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
            input + "_" + name + "_" + self.out_suffix).hexdigest() + ".txt"
        kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + "_" + name + '.log')
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        self.init(name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 10000, 'time': 300, 'ncpus': 1})

        self.args = ["index=0",
                     "I=" + os.path.join(self.align_dir, input + self.in_suffix),
                     "O=" + os.path.join(self.align_dir, input + self.out_suffix),
                     "M=" + os.path.join(self.qc_dir, input + ".dup.metrics.txt")]
        self.args += args
        self.setup_run()
        return




class QualiMap(BaseWrapper):
    """
    A wrapper for the running qualimap QC suite
    """

    cmd = ''

    # TODO: Clean up

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        # TODO add update to input/output suffixes here
        self.update_file_suffix(input_default=".dup.srtd.bam", output_default="", **kwargs)

        kwargs['target'] = input + "_" + name + "_" + 'qualimapReport' + "_" + hashlib.sha224(
            input + "_" + name + "_" + 'qualimapReport').hexdigest() + ".txt"

        kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + '_' + name + '.log')
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = name.split('_')[0]
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            ## Update memory requirements for job if needed
            if 'mem' in kwargs.get('add_job_parms').keys():
                self.args += [' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M']
        else:
            # Set default memory options
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 8})
            self.args += [' -Xmx10000M']
        self.args += [name.split('_')[1]]
        self.args += args

        if name.split("_")[1] == "rnaseq":
            gtf = kwargs.get('gtf_file')
            self.args += [" -gtf ", gtf]

        self.args += [" -bam ", os.path.join(kwargs.get('align_dir'), input + self.in_suffix),

                      " -outdir ", os.path.join(kwargs.get('work_dir'), "qc", input)]
        rename_results = ' '.join([" cp ", os.path.join(kwargs.get('qc_dir'), input, "qualimapReport.html "),
                                   os.path.join(kwargs.get('qc_dir'), input, input + "_qualimapReport.html ")])
        self.setup_run(add_command=rename_results)
        return


class SalmonCounts(BaseWrapper):
    """
    A wrapper for generating salmon counts

    """
    # TODO: Clean up
    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        self.make_target(name, input)
        kwargs['target'] = self.target
        self.update_file_suffix(input_default=".fq.gz", output_default="", **kwargs)

        kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + "_" + name + ".log")
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)
        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)
        default_args = dict()

        # update job parameters if needed
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                # TODO make sure threads are not given in the args
                default_args['-p'] = str(2 * kwargs.get('add_job_parms')['ncpus'])
        else:
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 8})
            default_args['-p'] = str(2 * self.job_parms['ncpus'])

        rename_results = ''
        if name.split('_')[1] == "quant":
            self.add_args_quant(input, default_args, *args, **kwargs)
            rename_results = ' '.join(
                [" cp ", os.path.join(kwargs.get('expression_dir',
                                                 os.path.join(kwargs['work_dir'], "expression")),
                                      input + "_salmon_counts", "quant.genes.sf"),
                 os.path.join(kwargs.get('expression_dir',
                                         os.path.join(kwargs['work_dir'], "expression")),
                              input + "_salmon_quant.genes.txt")])

        self.args += self.add_args
        self.setup_run(add_command=rename_results)

        return

    def make_target(self, name, input):
        """
        Create the luigi targets
        :param name:
        :param input:
        :return:
        """
        if name.split('_')[1] == "quant":
            self.target = input + '_' + name + "_" + hashlib.sha224(input + '_' + name).hexdigest() + ".txt"
        else:
            print "Not implemented yet"
        return

    def add_args_quant(self, input, default_args, *args, **kwargs):
        """
        Generic function that takes care of adding default args and updating them with user provided values if needed. Each function is\
        custom generated for the wrapper depending on how the program options are defined.

        :param input: The Sample ID
        :param default_args: Dictionary of defaults
        :param args: list of program specific options parsed from the YAML
        :param kwargs: List of general options across the entire workflow
        :return:
        """
        self.reset_add_args()
        default_args.update({'-l': 'A', '-g': kwargs.get('gtf_file')})

        if not self.paired_end:
            default_args["-r"] = os.path.join(kwargs.get('fastq_dir'), input + self.in_suffix)
        else:
            default_args["-1"] = os.path.join(kwargs.get('fastq_dir'), input + "_1" + self.in_suffix)
            default_args["-2"] = os.path.join(kwargs.get('fastq_dir'), input + "_2" + self.in_suffix)

        default_args["-o"] = os.path.join(kwargs.get('expression_dir',
                                                     os.path.join(kwargs['work_dir'], "expression")),
                                          input + "_salmon_counts")
        print default_args

        updated_args = self.update_default_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

class HtSeqCounts(BaseWrapper):
    """
    A wrapper for generating counts from HTSeq

    """
    # TODO: Clean up
    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        # Update input/output suffixes here
        self.update_file_suffix(input_default=".dup.srtd.bam", output_default="", **kwargs)

        kwargs['target'] = input + "_" + name + "_" + hashlib.sha224(
            input + "_" + name).hexdigest() + ".txt"

        kwargs['stderr'] = os.path.join(kwargs['log_dir'], input + "_" + name + ".log")

        kwargs['stdout'] = os.path.join(kwargs.get('expression_dir', os.path.join(kwargs.get('work_dir'), 'expression'))
                                        , input + "_htseq_counts")

        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = name.split('_')[0]
        self.init(new_name, **kwargs)
        # update job parameters if needed
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 2})
        if kwargs.get('gtf_file') is not None:
            gtf = kwargs.get('gtf_file')
        else:
            print "Error!!!  you need to specify a gtf file to run htseq-counts"
            sys.exit(0)

        default_args = {'-f': "bam", "-r": "pos", "-a": "0", "-t": "exon", "-i": "gene_id",
                        "--additional-attr=gene_name": '', "--nonunique=all": '',
                        "--secondary-alignments=score": ''}
        # self.args += args
        # self.args += ["-f", "bam", "-r", "pos", "-a", "0", "-t", "exon", "-i", "gene_id", "--additional-attr=gene_name",
        #              "--nonunique=all", "--secondary-alignments=score"]
        self.reset_add_args()
        self.add_args = self.update_default_args(default_args, *args, **kwargs)
        self.args += self.add_args
        self.args += [os.path.join(kwargs.get('align_dir'), self.input + self.in_suffix), gtf]

        self.setup_run()
        return


class Bwa(BaseWrapper):
    """
    A wrapper for BWA

    """


    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        self.update_file_suffix(input_default=".fq.gz", output_default=".sam", **kwargs)

        ## set the checkpoint target file
        kwargs['target'] = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
            input + "_" + name + "_" + self.out_suffix).hexdigest() + ".txt"
        kwargs['stdout'] = os.path.join(kwargs['align_dir'], input + self.out_suffix)

        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                # TODO make sure threads are not given in the args
                self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]
        else:
            self.job_parms.update({'mem': 4000, 'time': 80, 'ncpus': 12})
            self.args += ['-t 12']

        #TODO add update default args if needed

        self.args += args

        if self.paired_end:
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1" + self.in_suffix))
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2" + self.in_suffix))
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + self.in_suffix))

        self.setup_run()
        return

    # def setup_args(self):
    #     self.args += ["--gunzip", "-A sam", "-N1", "--use-shared-memory=0"]
    #     return


class BedtoolsCounts(BaseWrapper):
    """
    A wrapper for bedtools to count RNAseq reads for Single End data

    """

    # TODO: Clean up

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = hashlib.sha224(input + '.bedtoolsCounts.csv').hexdigest() + ".txt"
        name = name + " multicov "
        self.init(name, **kwargs)
        self.args = ["-split", "-D", "-f 0.95",
                     "-a " + os.path.join(self.cwd, input + ".dup.srtd.bam"),
                     "-b " + os.path.join(self.cwd, input + ".dup.metrics.txt")]
        self.args += args
        self.setup_run()
        return


class FeatureCounts(BaseWrapper):
    """
     Wrapper for FeatureCounts
    """

    # TODO: Clean up

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        # Update input/output suffixes here
        self.update_file_suffix(input_default=".dup.srtd.bam", output_default=".featureCounts.txt", **kwargs)

        kwargs['target'] = input + "_" + name + "_" + hashlib.sha224(
            input + "_" + name).hexdigest() + ".txt"

        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        self.init(name, **kwargs)

        default_args = {"--fracOverlap": '80', "-M": '', "-O": '', '-s': 1}
        self.reset_add_args()
        self.add_args = self.update_default_args(default_args, *args, **kwargs)
        self.args += self.add_args
        self.args += ["-a " + kwargs.get('gtf_file'),
                      "-o " + os.path.join(
                          kwargs.get('expression_dir', os.path.join(kwargs.get('work_dir'), 'expression')),
                          input + self.out_suffix),
                      os.path.join(kwargs.get('align_dir'), input + self.in_suffix)]
        self.setup_run()
        return


class FastqScreen(BaseWrapper):
    """
     Wrapper for fastqScreen
    """

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        self.update_file_suffix(input_default='.fq.gz', output_default='', **kwargs)
        kwargs['target'] = input + "_" + name + "_" + hashlib.sha224(input + "_" + name).hexdigest() + ".txt"
        # kwargs['paired_end'] = False
        # if kwargs.get('paired_end'):
        #    kwargs['target'] = input + '.2.' + name + hashlib.sha224(input + '.2.' + name).hexdigest() + ".txt"
        # print "Printing FastqScreen target"
        # print kwargs['paired_end']

        kwargs['stdout_append'] = os.path.join(kwargs['log_dir'], input + "_" + name + ".log")
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        self.init(name, **kwargs)

        fastq_screen_dir = os.path.join(kwargs.get('qc_dir'), "fastq_screen")
        default_args = {"--outdir": fastq_screen_dir, "--force": '', "--aligner": "bwa" }

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            # Update threads if cpus given
            # TODO make sure threads are not given in the args
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                # self.args += [' --threads ' + str(kwargs.get('add_job_parms')['ncpus'])]
                default_args["--threads"] = str(2 * (kwargs.get('add_job_parms')['ncpus']))
            else:
                # Set default memory and cpu options
                self.job_parms.update({'mem': 10000, 'time': 600, 'ncpus': 4})
                # TODO make sure threads are not given in the args
                # self.args += ['--threads 4']
                default_args["--threads"] = str(4)

        if self.paired_end:

            self.reset_add_args()
            self.add_args = self.update_default_args(default_args, *args, **kwargs)
            self.args += self.add_args
            self.args += [os.path.join(kwargs.get('fastq_dir'), input + "_1" + self.in_suffix)]
            self.setup_run()
            run_cmd1 = self.run_command

            ## Re initialize the object for the second pair
            self.init(name, **kwargs)
            self.reset_add_args()
            self.add_args = self.update_default_args(default_args, *args, **kwargs)
            self.args += self.add_args
            self.args += [os.path.join(kwargs.get('fastq_dir'), input + "_2" + self.in_suffix)]
            self.setup_run()
            run_cmd2 = self.run_command

            self.run_command = run_cmd1 + "; " + run_cmd2
        else:

            self.reset_add_args()
            self.add_args = self.update_default_args(default_args, *args, **kwargs)
            self.args += self.add_args
            self.args += [os.path.join(kwargs.get('fastq_dir'), input + self.in_suffix)]
            #self.args += [os.path.join(kwargs.get('fastq_dir'), input + "_2" + self.in_suffix)]
            self.setup_run()

        self.run_command = "mkdir -pv " + fastq_screen_dir + "; " + self.run_command
        return


class Trimmomatic(BaseWrapper):
    """
        Wrapper for trimmomatic
    """

    def __init__(self, name, input, *args, **kwargs):
        print "Printing trimmomatic args"
        print args
        self.input = input
        kwargs['target'] = input + "_" + name + "_" + hashlib.sha224(input + "_" + name).hexdigest() + ".txt"
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = ' '.join(name.split("_"))

        # TODO add update to input/output suffixes here
        self.update_file_suffix(input_default=".fq.gz", output_default="_tr.fq.gz", **kwargs)

        kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + ".log")

        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            # self.job_parms.update(dict(kwargs.get('add_job_parms')))
            self.job_parms.update(kwargs.get('add_job_parms'))

            # Update threads if cpus given ## Need to fix this based on environment o
            # Other parameters. this can break when slurm config does not allow multi
            # threads per cpu
            # TODO make sure threads are not given in the args

            if 'ncpus' in kwargs.get('add_job_parms').keys():
                self.args += [' -threads ' + str(kwargs.get('add_job_parms')['ncpus'])]

        else:
            # Set default memory and cpu options
            self.job_parms.update({'mem': 10000, 'time': 600, 'ncpus': 4})
            # TODO make sure threads are not given in the args
            self.args += ['-threads 4']

        self.args += ["-trimlog", os.path.join(kwargs.get('log_dir'), input + "_" + name + ".log")]
        add_command = ''
        if self.paired_end:

            self.args += [os.path.join(kwargs.get('fastq_dir'), input + "_1" + self.in_suffix),
                          os.path.join(kwargs.get('fastq_dir'), input + "_2" + self.in_suffix)]

            self.args += ["-baseout", os.path.join(kwargs.get('fastq_dir'), input + self.out_suffix)]

            add_command = "mv -v " + os.path.join(kwargs.get('fastq_dir'), input + "_tr_1P.fq.gz") + " "
            add_command += os.path.join(kwargs.get('fastq_dir'), input + "_1" + self.out_suffix) + "; "
            add_command += "mv -v " + os.path.join(kwargs.get('fastq_dir'), input + "_tr_2P.fq.gz") + " "
            add_command += os.path.join(kwargs.get('fastq_dir'), input + "_2" + self.out_suffix) + "; "
            add_command += "rm -v " + os.path.join(kwargs.get('fastq_dir'), input + "_tr_1U.fq.gz") + "; "
            add_command += "rm -v " + os.path.join(kwargs.get('fastq_dir'), input + "_tr_2U.fq.gz") + "; "
        else:
            self.args += [os.path.join(kwargs.get('fastq_dir'), input + self.in_suffix)]
            self.args += [os.path.join(kwargs.get('fastq_dir'), input + self.out_suffix)]
            # Todo need to check what move commands are added for SingleEnd

        # Add all other optional trimming specification arguments
        self.args += args
        self.setup_run(add_command=add_command)

        return
