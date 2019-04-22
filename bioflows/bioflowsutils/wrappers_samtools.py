# import copy
import hashlib
import os
# import subprocess
import sys

from wrappers import BaseWrapper


# from itertools import chain
# import config
# import diagnostics
# import utils


class SamTools(BaseWrapper):
    '''
    Wrapper class for the samtools command
    '''
    stdout_as_output = False

    def __init__(self, name, input, *args, **kwargs):
        self.reset_add_args()
        self.input = input
        self.make_target(name, input, *args, **kwargs)
        kwargs['target'] = self.target
        if self.stdout_as_output:
            kwargs['stdout'] = os.path.join(kwargs['align_dir'], input + self.out_suffix)
        else:
            kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + "_" + name + '.log')
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            # add threading
            if name.split('_')[1] == "sort":
                if 'ncpus' in kwargs.get('add_job_parms').keys():
                    # TODO make sure threads are not given in the args
                    self.args += [' -@ ' + str(kwargs.get('add_job_parms')['ncpus'])]
                    if 'mem' in kwargs.get('add_job_parms').keys() and name.split('_')[1] == "sort":
                        # TODO make sure threads are not given in the args
                        mem_per_thread = int(kwargs.get('add_job_parms')['mem'] / kwargs.get('add_job_parms')['ncpus'])
                        self.args += [' -m ' + str(mem_per_thread) + "M"]
                    else:
                        mem_per_thread = int(kwargs.get('job_parms')['mem'] / kwargs.get('add_job_parms')['ncpus'])
                        self.args += [' -m ' + str(mem_per_thread) + "M"]
        else:
            self.job_parms.update({'mem': 4000, 'time': 300, 'ncpus': 1})
        # print self.add_args
        self.args += self.add_args
        self.setup_run()
        return

    def make_target(self, name, input, *args, **kwargs):
        # Make sure output suffix is enforced
        name_str = "_" + name + "_"
        if kwargs['suffix_type'] != "custom":
            print "Error1!!! you need to specify an output suffix"
            sys.exit(0)
        else:
            self.out_suffix = kwargs['suffix']['output']
            if kwargs['suffix']['input'] != "default":
                self.in_suffix = kwargs['suffix']['input']
            else:
                self.in_suffix = "default"

        if name.split('_')[1] == "view":
            # self.stdout_as_output = True
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_view(input, *args, **kwargs)

        elif name.split('_')[1] == "sort":
            # self.stdout_as_output = True
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_sort(input, *args, **kwargs)

        elif name.split('_')[1] == "index":
            self.target = input + name_str + self.in_suffix + ".bai." + "_" + hashlib.sha224(
                input + name_str + self.in_suffix + ".bai").hexdigest() + ".txt"
            self.add_args_index(input, *args, **kwargs)
        return

    def add_args_view(self, input, *args, **kwargs):

        if self.in_suffix == "default":
            print "Error: You need to provide the input suffix\n"
            sys.exit(0)
        self.add_args += args
        self.add_args += ["-o", os.path.join(kwargs['align_dir'], input + self.out_suffix)]
        self.add_args.append(os.path.join(kwargs['align_dir'], input + self.in_suffix))
        return

    def add_args_sort(self, input, *args, **kwargs):
        if self.in_suffix == "default":
            self.in_suffix = ".bam"

        self.add_args += args
        if any("-T" in a for a in self.add_args):
            idx_to_replace = [i for i, s in enumerate(self.add_args) if '-T' in s][0]
            tmpdir_string = self.add_args[idx_to_replace] + "_" + input
            self.add_args[idx_to_replace] = tmpdir_string

        self.add_args += ["-o", os.path.join(kwargs['align_dir'], input + self.out_suffix)]
        self.add_args.append(os.path.join(kwargs['align_dir'], input + self.in_suffix))
        return

    def add_args_index(self, input, *args, **kwargs):
        if self.in_suffix == "default":
            self.in_suffix = ".bam"
        if any("-b" or "-c" or "-m" not in a for a in args):
            self.add_args += ["-b"]
            self.add_args += args
        else:
            self.add_args += args

        self.add_args.append(os.path.join(kwargs['align_dir'], input + self.in_suffix))
        if self.out_suffix != "default":
            self.add_args.append(os.path.join(kwargs['align_dir'], input + self.out_suffix))
        return
