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

import glob
import math
import operator
import os
import random
import shlex
import subprocess
import sys
import copy
import time
import hashlib

from collections import namedtuple
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

    def __init__(self, name, **kwargs):

        self.name = name
        # self.shell = '/bin/sh'
        self.cmd = None
        self.run_command = None
        self.args = []
        self.conda_command = kwargs.get('conda_command')
        self.job_parms = kwargs.get('job_parms')
        self.paired_end = kwargs.get('paired_end',False)
        self.cwd = kwargs.get('cwd', os.getcwd())
        self.log_dir = kwargs.get('log_dir', os.path.join(os.getcwd(), "logs"))
        self.align_dir = kwargs.get('align_dir', os.path.join(os.getcwd(), 'align_dir'))
        self.qc_dir = kwargs.get('qc_dir', os.path.join(os.getcwd(), 'qc_dir'))
        ## Define the checkpoint files
        ##self.luigi_source = os.path.join(self.cwd, 'checkpoints', kwargs.get('source', "None"))
        self.luigi_source = "Present"
        self.luigi_target = os.path.join(self.cwd, 'checkpoints', kwargs.get('target', "None"))

        ## Below for testing only
        self.local_target = kwargs.get('local_targets', True)
        if self.local_target:
            self.luigi_local_target = os.path.join(
                kwargs.get('luigi_local_path', "/Users/aragaven/scratch/test_workflow"),
                                               kwargs.get('target',"None"))
        self.stdout = kwargs.get('stdout')
        self.stderr = kwargs.get('stderr')
        self.stdout_append = kwargs.get('stdout_append')
        # self.pipe = kwargs.get('pipe')
        self.env = os.environ.copy()
        self.max_concurrency = kwargs.get('max_concurrency', 1)
        self.prog_args = dict()
        for k,v in kwargs.iteritems():
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

        self.env['PATH'] = self.conda_command.split()[2] + "/bin:" + self.env['PATH']
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
        cmd = 'java '
        cmd.append('-jar')
        cmd += self.cmd
        self.version(cmd=cmd, path=self.cmd[0])

    def setup_run(self, add_command=None):

        """
        Call this function at the end of your class's `__init__` function.
        """

        cmd = self.cmd
        stderr = os.path.join(self.log_dir, '_'.join([self.input, self.name, 'err.log']))
        if self.stderr is not None:
            stderr = self.stderr
        if len(self.name.split()) > 1:
            stderr = os.path.join(self.log_dir, '_'.join([self.input, '_'.join(self.name.split()), 'err.log']))
        self.args.append('2>>' + stderr)

        # if self.pipe:
        # 	self.args += ('|', self.pipe, '2>>' + stderr)

        # Write to a stdout file if it was set by the derived class.
        # Otherwise, stdout and stderr will be combined into the log file.

        if self.stdout:
            stdout = os.path.abspath(self.stdout)
            self.args.append('1>' + stdout)
            # diagnostics.log('stdout', stdout)
        elif self.stdout_append:
            stdout = os.path.abspath(self.stdout_append)
            self.args.append('1>>' + stdout)
            # diagnostics.log('stdout', stdout)
        else:
            self.args.append('1>>' + stderr)

        cmd = ' '.join(chain(cmd, map(str, self.args)))

        if add_command is not None:
            cmd += "; " + add_command

        self.run_command = cmd
        return

    def run_jar(self, mem=None):
        """
        Special case of run() when the executable is a JAR file. This may be deprecated as we  will use conda for all
        packages

        """
        # cmd = config.get_command('java')
        cmd = 'java '
        if mem:
            cmd.append('-Xmx%s' % mem)
        cmd.append('-jar')
        cmd += self.cmd
        self.run(cmd)


### Third-party command line tools ###

class FastQC(BaseWrapper):
    """
    A wrapper for FastQC.
    http://www.bioinformatics.bbsrc.ac.uk/projects/fastqc/
    """
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.fastqc.zip.'+ hashlib.sha224(input + '.fastqc.zip').hexdigest() + ".txt"

        # only need second part as fastqc is run on each file sequentially in the same job
        if kwargs.get('paired_end'):
            kwargs['target'] = input + '.2.fastqc'+ hashlib.sha224(input + '.2.fastqc.zip').hexdigest() + ".txt"

        self.init(name, **kwargs)
        # self.luigi_source = "None"
        self.version('-v')
        self.add_threading('-t')
        self.args += [' -o ' + self.qc_dir]
        self.args += args
        if self.paired_end:

            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1.fq.gz"))
            self.setup_run()
            run_cmd1 = self.run_command
            self.init(name, **kwargs)
            if kwargs.get('job_parms_type') != 'default':
                self.job_parms.update(kwargs.get('add_job_parms'))
            else:
                self.job_parms.update({'mem': 1000, 'time': 80, 'ncpus': 1})

            self.args += args
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2.fq.gz"))
            self.setup_run()
            run_cmd2 = self.run_command
            self.run_command = run_cmd1 + "; " + run_cmd2
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + ".fq.gz"))
            self.setup_run()

        return

class Gsnap(BaseWrapper):
    """
    A wrapper for gsnap 
    
    """

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        ## set the checkpoint target file
        kwargs['target'] = input + '.sam.' + hashlib.sha224(input + '.sam').hexdigest() + ".txt"

        self.init(name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]
        else:
            self.job_parms.update({'mem': 1000, 'time': 80, 'ncpus': 1})

        if self.paired_end:
            kwargs['source'] = hashlib.sha224(input + '_2_fastqc.gzip').hexdigest() + ".txt"
        else:
            kwargs['source'] = hashlib.sha224(input + '_fastqc.gzip').hexdigest() + ".txt"

        self.setup_args()

        self.args += args

        if self.paired_end:
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1.fq.gz"))
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2.fq.gz"))
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + ".fq.gz"))
        # self.cmd = ' '.join(chain(self.cmd, map(str, self.args), map(str,input)))

        self.setup_run()
        return

    def setup_args(self):
        self.args += ["--gunzip", "-A sam", "-N1", "--use-shared-memory=0"]
        return


class SamTools(BaseWrapper):
    '''
    Wrapper class for the samtools command
    '''
    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        # kwargs['target'] = hashlib.sha224(input + '.fq.gz').hexdigest() + ".txt"
        self.init(name, **kwargs)
        # self.version()
        self.args += args
        self.args.append(input)
        self.setup_run()
        return


class SamToBam(BaseWrapper):
    '''
    Wrapper class to filter sam and produce a bam with only mapped reads
    '''

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.bam'+ hashlib.sha224(input + '.bam').hexdigest() + ".txt"
        new_name = name + " view"
        self.init(new_name, **kwargs)
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 2000, 'time': 300, 'ncpus': 1})

        self.args = ["-Sbh ", "-o", os.path.join(self.align_dir, input + ".bam")]
        self.args += args
        self.args.append(os.path.join(self.align_dir, input + ".sam"))
        self.setup_run()
        self.name = self.name + " fromsam"
        return


class BamToMappedBam(BaseWrapper):
    '''
    Wrapper class to filter sam and produce a bam with only mapped reads
    '''
    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.mapped.bam'+ hashlib.sha224(input + '.mapped.bam').hexdigest() + ".txt"
        new_name = name + " view"

        self.init(new_name, **kwargs)
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 2000, 'time': 300, 'ncpus': 1})

        self.args = ["-F 0x4", "-bh ", "-o", os.path.join(self.align_dir, input + ".mapped.bam")]
        self.args += args
        self.args.append(os.path.join(self.align_dir, input + ".bam"))
        self.setup_run()
        self.name = self.name + " mapped"
        return


class BamToUnmappedBam(BaseWrapper):
    '''
    Wrapper class to filter sam and produce a bam with only unmapped reads
    '''
    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.unmapped.bam'+ hashlib.sha224(input + '.unmapped.bam').hexdigest() + ".txt"
        new_name = name + " view"
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 2000, 'time': 300, 'ncpus': 1})

        self.args = ["-f 0x4", "-bh ", "-o", os.path.join(self.align_dir, input + ".unmapped.bam")]
        self.args += args
        self.args.append(os.path.join(self.align_dir, input + ".sam"))
        self.setup_run()
        self.name = self.name + " unmapped"
        return


class SamToolsSort(BaseWrapper):
    '''
    Wrapper class to sort a bam file using samtools
    '''

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.srtd.bam'+ hashlib.sha224(input + '.srtd.bam').hexdigest() + ".txt"
        new_name = name + " sort"
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            # add threading
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]
        else:
            self.job_parms.update({'mem': 4000, 'time': 300, 'ncpus': 1})

        self.args = ["-o", os.path.join(self.align_dir, input + ".srtd.bam")]
        self.args += args
        self.args.append(os.path.join(self.align_dir, input + ".bam"))
        self.setup_run()
        return


class SamIndex(BaseWrapper):
    '''
    Wrapper class to index a sorted bam file
    '''
    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.srtd.bam.bai' + hashlib.sha224(input + '.srtd.bam.bai').hexdigest() + ".txt"
        new_name = name + " index"
        self.init(new_name, **kwargs)
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 1000, 'time': 80, 'ncpus': 1})

        self.args = [os.path.join(self.align_dir, input + ".srtd.bam")]
        self.args += args
        self.setup_run()
        return


class BiobambamMarkDup(BaseWrapper):
    '''
    Wrapper class to mark duplicates in a bam using biobambam
    '''
    input = ''
    args = ''

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.dup.srtd.bam'+ hashlib.sha224(input + '.dup.srtd.bam').hexdigest() + ".txt"
        self.init(name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 10000, 'time': 300, 'ncpus': 1})

        self.args = ["index=0",
                     "I=" + os.path.join(self.align_dir, input + ".srtd.bam"),
                     "O=" + os.path.join(self.align_dir, input + ".dup.srtd.bam"),
                     "M=" + os.path.join(self.qc_dir, input + ".dup.metrics.txt")]
        self.args += args
        self.setup_run()
        return


class QualiMapRnaSeq(BaseWrapper):
    """
    A wrapper for the running qualimap QC suite for RNAseq

    """

    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.qualimapReport.' + hashlib.sha224(
            input + '.qualimapReport.html').hexdigest() + ".txt"
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
        gtf = kwargs.get('gtf_file')
        self.args += [" -gtf ", gtf,
                      " -bam ", os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                      " -outdir ", os.path.join(kwargs.get('work_dir'), "qc", input)]
        self.args += args
        rename_results = ' '.join([" cp ", os.path.join(kwargs.get('qc_dir'), input, "qualimapReport.html "),
                                   os.path.join(kwargs.get('qc_dir'), input, input + "_qualimapReport.html ")])
        self.setup_run(add_command=rename_results)
        return

class QualiMap(BaseWrapper):
    """
    A wrapper for the running qualimap QC suite for RNAseq

    """

    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = input + '.qualimapReport.' + hashlib.sha224(
            input + '.qualimapReport.html').hexdigest() + ".txt"
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

        self.args += [ " -bam ", os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),

                      " -outdir ", os.path.join(kwargs.get('work_dir'), "qc", input)]
        rename_results = ' '.join([" cp ", os.path.join(kwargs.get('qc_dir'), input, "qualimapReport.html "),
                                   os.path.join(kwargs.get('qc_dir'), input, input + "_qualimapReport.html ")])
        self.setup_run(add_command=rename_results)
        return


class SalmonCounts(BaseWrapper):
    """
    A wrapper for generating salmon counts

    """

    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        kwargs['target'] = input + '.salmoncounts.' + hashlib.sha224(input + '.salmoncounts').hexdigest() + ".txt"
        new_name = name + " quant"
        self.init(new_name, **kwargs)

        # update job parameters if needed
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

        else:
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 8})

        gtf = kwargs.get('gtf_file')
        self.args += args
        self.args += ["-l A"]

        if not self.paired_end:
            self.args += ["-r", os.path.join(kwargs.get('fastq_dir'), input + ".fq.gz")]
        else:
            self.args += ["-1", os.path.join(kwargs.get('fastq_dir'), input + "_1.fq.gz"),
                          "-2", os.path.join(kwargs.get('fastq_dir'), input + "_2.fq.gz")]

        self.args += [" -o " + os.path.join(kwargs.get('work_dir'), kwargs.get('expression_dir'),
                                            input + "_salmon_counts")]
        rename_results = ' '.join(
            [" cp ", os.path.join(kwargs.get('expression_dir'), input + "_salmon_counts", "quant.genes.sf"),
             os.path.join(kwargs.get('expression_dir'), input + "_salmon_quant.genes.txt")])
        self.setup_run(add_command=rename_results)
        return


class HtSeqCounts(BaseWrapper):
    """
    A wrapper for generating counts from HTSeq

    """

    cmd = ''
    args = []

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        kwargs['target'] = input + '.htseqcounts.' + hashlib.sha224(input + '.htseqcounts').hexdigest() + ".txt"
        new_name = name
        kwargs['stderr'] = kwargs.get('stdout')
        kwargs.update({'stdout': os.path.join(kwargs.get('work_dir'), kwargs.get('expression_dir'),
                                              input + "_htseq_counts")})
        self.init(new_name, **kwargs)
        # update job parameters if needed
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 2})

        gtf = kwargs.get('gtf_file')
        self.args += args
        self.args += ["-f", "bam", "-r", "pos", "-a", "0", "-t", "exon", "-i", "gene_id", "--additional-attr=gene_name",
                      "--nonunique=all", "--secondary-alignments=score"]
        self.args += [os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                      gtf]

        self.setup_run()
        return

class Bwa(BaseWrapper):
    """
    A wrapper for BWA

    """

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        ## set the checkpoint target file
        kwargs['target'] = input + '.sam.' + hashlib.sha224(input + '.sam').hexdigest() + ".txt"
        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            if 'ncpus' in kwargs.get('add_job_parms').keys():
                self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]
        else:
            self.job_parms.update({'mem': 4000, 'time': 80, 'ncpus': 12})
            self.args += ['-t 12']

        if self.paired_end:
            kwargs['source'] = hashlib.sha224(input + '_2_fastqc.gzip').hexdigest() + ".txt"
        else:
            kwargs['source'] = hashlib.sha224(input + '_fastqc.gzip').hexdigest() + ".txt"

        #self.setup_args()

        self.args += args

        if self.paired_end:
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_1.fq.gz"))
            self.args.append(os.path.join(self.cwd, 'fastq', input + "_2.fq.gz"))
        else:
            self.args.append(os.path.join(self.cwd, 'fastq', input + ".fq.gz"))
        # self.cmd = ' '.join(chain(self.cmd, map(str, self.args), map(str,input)))

        self.setup_run()
        return

    # def setup_args(self):
    #     self.args += ["--gunzip", "-A sam", "-N1", "--use-shared-memory=0"]
    #     return

class BedtoolsCounts(BaseWrapper):
    """
    A wrapper for bedtools to count RNAseq reads for Single End data

    """

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
    """A wrapper for FeatureCounts
    """

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        kwargs['target'] = hashlib.sha224(input + '.featureCounts.csv').hexdigest() + ".txt"
        # name = name + " multicov "
        self.init(name, **kwargs)
        self.args = ["-split", "-D", "-f 0.95",
                     "-a " + os.path.join(self.cwd, input + ".dup.srtd.bam"),
                     "-b " + os.path.join(self.cwd, input + ".dup.metrics.txt")]
        self.args += args
        self.setup_run()
        return

class Picard(BaseWrapper):
    """
        A wrapper for picardtools
        picard CollectWgsMetrics \
        INPUT=$mysamplebase"_sorted.bam" \ OUTPUT=$mysamplebase"_stats_picard.txt"\
        REFERENCE_SEQUENCE=$myfasta \
        MINIMUM_MAPPING_QUALITY=20 \
        MINIMUM_BASE_QUALITY=20 \
        VALIDATION_STRINGENCY=LENIENT
    """
    target =''
    add_args = ''

    def __init__(self, name, input, *args, **kwargs):
        self.input = input

        ## set the checkpoint target file
        new_name = ' '.join(name.split("_"))
        # kwargs['target'] = input + '._wgs_stats_picard.' + hashlib.sha224(input + '._wgs_stats_picard.txt').hexdigest() + ".txt"
        self.make_target(input,**kwargs)
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            ## Update threads if cpus given
            # if 'ncpus' in kwargs.get('add_job_parms').keys():
            #     self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]

            ## Update memory requirements  if needed
            if 'mem' in kwargs.get('add_job_parms').keys():
                self.args += [' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M']

        else:
            # Set default memory and cpu options
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 4})
            self.args += [' -Xmx10000M']

        kwargs['source'] = input + '.dup.srtd.bam'+ hashlib.sha224(input + '.dup.srtd.bam').hexdigest() + ".txt"
        #ref_fasta = kwargs.get("ref_fasta_path")
        self.args += args
        self.args += self.add_args
        # self.args += ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
        #               "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._wgs_stats_picard.txt'),
        #               "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
        #               "MINIMUM_MAPPING_QUALITY="+"20","MINIMUM_BASE_QUALITY="+"20",
        #               "COUNT_UNPAIRED=true", "VALIDATION_STRINGENCY="+"LENIENT"]

        self.setup_run()
        return

    def make_target(self, name, input, **kwargs):
        if name.split('_')[1] == "CollectWgsMetrics":
            self.target = input + '._wgs_stats_picard.' + hashlib.sha224(input + '._wgs_stats_picard.txt').hexdigest() + ".txt"
            self.add_args_collect_wgs_metrics(input,**kwargs)
        elif name.split('_')[1] == "MeanQualityByCycle":
            self.target = input + '._read_qual_by_cycle_picard.' + hashlib.sha224(input + '._read_qual_by_cycle_picard.txt').hexdigest() + ".txt"
        elif name.split('_')[1] == "QualityScoreDistribution":
            self.target = input + '._read_qual_overall_picard.' + hashlib.sha224(input + '._read_qual_overall_picard.txt').hexdigest() + ".txt"
        elif name.split('_')[1] == "MarkDuplicates":
            self.target = input + '._mark_dup_picard.' + hashlib.sha224(input + '._mark_dup_picard.txt').hexdigest() + ".txt"
        return

    def add_args_collect_wgs_metrics(self,input,**kwargs):
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                      "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._wgs_stats_picard.txt'),
                      "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                      "MINIMUM_MAPPING_QUALITY="+"20","MINIMUM_BASE_QUALITY="+"20",
                      "COUNT_UNPAIRED=true", "VALIDATION_STRINGENCY="+"LENIENT"]
        return

    def add_args_mean_quality_by_cycle(self,input,**kwargs):
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                      "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._read_qual_by_cycle_picard.txt'),
                      "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                      "CHART_OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + '._mean_qual_by_cycle.pdf') ,
                      "VALIDATION_STRINGENCY="+"LENIENT"]
        return

    def add_args_quality_score_distribution(self,input,**kwargs):
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                      "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._read_qual_overall_picard.txt'),
                      "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                      "CHART_OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + '._mean_qual_overall.pdf') ,
                      "VALIDATION_STRINGENCY="+"LENIENT"]
        return

    def add_args_markduplicates(self,input,**kwargs):

        ##TODO: Name dup output based on REMOVE_DUPLICATES Attr
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
                          "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.srtd.bam"),
                           "M=" + os.path.join(kwargs.get('qc_dir'),input + '._mark_duplicates_picard.txt'),
                          "REMOVE_DUPLICATES=" + kwargs.get("REMOVE_DUPLICATES","true") ,
                          "CREATE_INDEX=" + kwargs.get("CREATE_INDEX","true"),
                          "VALIDATION_STRINGENCY="+"LENIENT"]
        return

class Gatk(BaseWrapper):
        """
            A wrapper for picardtools
            picard CollectWgsMetrics \
            INPUT=$mysamplebase"_sorted.bam" \ OUTPUT=$mysamplebase"_stats_picard.txt"\
            REFERENCE_SEQUENCE=$myfasta \
            MINIMUM_MAPPING_QUALITY=20 \
            MINIMUM_BASE_QUALITY=20 \
            VALIDATION_STRINGENCY=LENIENT
        """
        target = ''
        add_args = ''

        def __init__(self, name, input, *args, **kwargs):
            self.input = input

            ## set the checkpoint target file
            new_name = ' '.join(name.split("_"))
            # kwargs['target'] = input + '._wgs_stats_picard.' + hashlib.sha224(input + '._wgs_stats_picard.txt').hexdigest() + ".txt"
            self.make_target(input, **kwargs)
            self.init(new_name, **kwargs)

            if kwargs.get('job_parms_type') != 'default':
                self.job_parms.update(kwargs.get('add_job_parms'))

                ## Update threads if cpus given
                # if 'ncpus' in kwargs.get('add_job_parms').keys():
                #     self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]

                ## Update memory requirements  if needed
                if 'mem' in kwargs.get('add_job_parms').keys():
                    self.args += [' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M']

            else:
                # Set default memory and cpu options
                self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 4})
                self.args += [' -Xmx10000M']

            kwargs['source'] = input + '.dedup.srtd.bam' + hashlib.sha224(input + '.dedup.rg.srtd.bam').hexdigest() + ".txt"
            # ref_fasta = kwargs.get("ref_fasta_path")
            self.args += args
            self.args += self.add_args
            # self.args += ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
            #               "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._wgs_stats_picard.txt'),
            #               "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
            #               "MINIMUM_MAPPING_QUALITY="+"20","MINIMUM_BASE_QUALITY="+"20",
            #               "COUNT_UNPAIRED=true", "VALIDATION_STRINGENCY="+"LENIENT"]

            self.setup_run()
            return

        def make_target(self, name, input, **kwargs):
            if name.split('_')[1] == "RealignerTargetCreator":
                self.target = input + '._wgs_stats_picard.' + hashlib.sha224(
                    input + '._wgs_stats_picard.txt').hexdigest() + ".txt"
                self.add_args_realigner_target_creator(input, **kwargs)

            elif name.split('_')[1] == "IndelRealigner":
                self.target = input + '._read_qual_by_cycle_picard.' + hashlib.sha224(
                    input + '._read_qual_by_cycle_picard.txt').hexdigest() + ".txt"

            elif name.split('_')[1] == "BaseRecalibrator":
                self.target = input + '._read_qual_overall_picard.' + hashlib.sha224(
                    input + '._read_qual_overall_picard.txt').hexdigest() + ".txt"

            elif name.split('_')[1] == "PrintReads":
                self.target = input + '._mark_dup_picard.' + hashlib.sha224(
                    input + '._mark_dup_picard.txt').hexdigest() + ".txt"

            elif name.split('_')[1] == "HaplotypeCaller":
                self.target = input + '._mark_dup_picard.' + hashlib.sha224(
                    input + '._mark_dup_picard.txt').hexdigest() + ".txt"

            elif name.split('_')[1] == "VariantRecalibrator":
                self.target = input + '._mark_dup_picard.' + hashlib.sha224(
                    input + '._mark_dup_picard.txt').hexdigest() + ".txt"
            return

        def add_args_realigner_target_creator(self, input, **kwargs):
            # gatk -Xmx20G -T RealignerTargetCreator -R $my.fasta -I $my.bam\
            #  -known /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf \
            # -o $samp_realign_targets.intervals
            #kwargs.get()
            self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.rg.srtd.bam"),
                             "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + '_realign_targets.intervals'),
                             "-R " + kwargs.get("ref_fasta_path"),
                             "-known=" + kwargs.get("-known", "/gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf")]
            return

        def add_args_indel_realigner(self, input, **kwargs):
            # gatk - T IndelRealigner \
            # - R $myfasta \
            # - known $myindel \
            # - targetIntervals $mysamplebase"_realign_targets.intervals" \
            # - I $mysamplebase"_sorted_dedup.bam" \
            # - o $mysamplebase"_sorted_dedup_realigned.bam" \

            kwargs.get()
            self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.rg.srtd.bam"),
                             "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + '.dedup.rg.srtd.realigned.bam'),
                             "-R " + kwargs.get("ref_fasta_path"),
                             "-known=" +  ]
            return

        def add_args_base_recalibrator(self, input, **kwargs):
            # gatk - T IndelRealigner \
            # - R $myfasta \
            # - known $myindel \
            # - targetIntervals $mysamplebase"_realign_targets.intervals" \
            # - I $mysamplebase"_sorted_dedup.bam" \
            # - o $mysamplebase"_sorted_dedup_realigned.bam" \

            kwargs.get()
            self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.rg.srtd.bam"),
                             "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + '.dedup.rg.srtd.realigned.bam'),
                             "-R " + kwargs.get("ref_fasta_path"),
                             "-known=" +]
            return

        def add_args_print_reads(self, input, **kwargs):
            # gatk - T IndelRealigner \
            # - R $myfasta \
            # - known $myindel \
            # - targetIntervals $mysamplebase"_realign_targets.intervals" \
            # - I $mysamplebase"_sorted_dedup.bam" \
            # - o $mysamplebase"_sorted_dedup_realigned.bam" \

            kwargs.get()
            self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.rg.srtd.bam"),
                             "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + '.dedup.rg.srtd.realigned.bam'),
                             "-R " + kwargs.get("ref_fasta_path"),
                             "-known=" +]
            return

        def add_args_haplotype_caller(self, input, **kwargs):
            # gatk - T IndelRealigner \
            # - R $myfasta \
            # - known $myindel \
            # - targetIntervals $mysamplebase"_realign_targets.intervals" \
            # - I $mysamplebase"_sorted_dedup.bam" \
            # - o $mysamplebase"_sorted_dedup_realigned.bam" \

            kwargs.get()
            self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dedup.rg.srtd.bam"),
                             "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + '.dedup.rg.srtd.realigned.bam'),
                             "-R " + kwargs.get("ref_fasta_path"),
                             "-known=" +]
            return