import yaml, os, hashlib, sys

class BaseWrapperNew(object):
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
    pre_args = []
    post_args = []
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
        self.work_dir = kwargs.get('work_dir', os.getcwd())
        self.log_dir = kwargs.get('log_dir', os.path.join(os.getcwd(), "logs"))
        self.align_dir = kwargs.get('align_dir', os.path.join(os.getcwd(), 'align_dir'))
        self.qc_dir = kwargs.get('qc_dir', os.path.join(os.getcwd(), 'qc_dir'))
        self.scripts_dir = kwargs.get('scripts_dir', os.path.join(self.log_dir, 'scripts_dir'))
        #self.intermediary_dir = kwargs.get('intermediary_dir', os.path.join(os.getcwd(), 'intermediary_files'))
        ## Define the checkpoint files
        ##self.luigi_source = os.path.join(self.cwd, 'checkpoints', kwargs.get('source', "None"))
        self.luigi_source = "Present"
        self.luigi_target = os.path.join(self.work_dir, 'checkpoints', kwargs.get('target', "None"))

        ## Below for testing only
        self.local_target = kwargs.get('local_targets', True)
        if self.local_target:
            self.luigi_local_target = os.path.join(
                kwargs.get('luigi_local_path', "/Users/aragaven/scratch/test_workflow"),
                kwargs.get('target', "None"))
        #self.stdout = kwargs.get('stdout')
        #self.stderr = kwargs.get('stderr')
        #self.stdout_append = kwargs.get('stdout_append')
        self.prog_args = dict()
        for k, v in kwargs.iteritems():
            self.prog_args[k] = v
        #self.setup_command()
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
        self.cmd = list(self.cmd.split())
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

    # def setup_run(self, add_command=None):
    #
    #     """
    #     Call this function at the end of your class's `__init__` function.
    #     """
    #
    #     cmd = self.cmd
    #     stderr = os.path.join(self.log_dir, '_'.join([self.input, self.prog_id, 'err.log']))
    #
    #     if self.stderr is not None:
    #         stderr = self.stderr
    #     if len(self.name.split()) > 1:
    #         stderr = os.path.join(self.log_dir, '_'.join([self.input, self.prog_id, 'err.log']))
    #         # MAYBE redundant
    #     self.args.append('2>>' + stderr)
    #
    #
    #     # Write to a stdout file if it was set by the derived class.
    #     # Otherwise, stdout and stderr will be combined into the log file.
    #
    #     if self.stdout:
    #         stdout = os.path.abspath(self.stdout)
    #         self.args.append('1>' + stdout)
    #     elif self.stdout_append:
    #         stdout = os.path.abspath(self.stdout_append)
    #         self.args.append('1>>' + stdout)
    #     else:
    #         self.args.append('1>>' + stderr)
    #
    #     cmd = ' '.join(chain(cmd, map(str, self.args)))
    #
    #     if add_command is not None:
    #         cmd += "; " + add_command
    #
    #     self.run_command = cmd
    #     return

    def setup_run(self, add_command=None):

        """
        Call this function at the end of your class's `__init__` function.
        """

        cmd = self.cmd

        cmd = ' '.join(chain(cmd, map(str, self.args)))

        if add_command is not None:
            cmd += "; " + add_command

        self.run_command = cmd
        return


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
            elif output_default is not None:
                self.out_suffix = output_default
            else:
                print "Error!!! you need to specify an output suffix"
                sys.exit(0)
            if kwargs['suffix']['input'] != "default":
                self.in_suffix = kwargs['suffix']['input']
            elif input_default is not None:
                self.in_suffix = input_default
            else:
                print "Error!!! you need to specify an input suffix"
                sys.exit(0)
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

        Refactor this to if(any(' '.join[k,v] not in a for a in args):
                            add default_args
                         else:
                            pass
        Also add post_args parser in args to differentiate pre and post args
        """
        tmp_args = []
        tmp_args += args

        args_list = [y for x in args for y in x.split()]

        for k, v in default_args.iteritems():
            if any(' '.join([k,str(v)]) not in a for a in tmp_args):
                tmp_args += [' '.join([k, str(v)])]
            else:
                # k_pos = [i for i, s in enumerate(args) if k in s][0]
                # print "Printing tmp_args while updating"
                # print tmp_args[k_pos]
                # tmp_args[k_pos] = tmp_args[k_pos].replace(v, v))
                # print tmp_args[k_pos]
                pass

        return ' '.join(tmp_args)

    # def update_default_args(self, default_args, *args, **kwargs):
    #     """
    #     Override the default values for program args to those provided by the user for a  wrapper
    #     :param default_args:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #
    #     Refactor this to if(any(' '.join[k,v] not in a for a in args):
    #                         add default_args
    #                      else:
    #                         pass
    #     Also add post_args parser in args to differentiate pre and post args
    #     """
    #     tmp_args = []
    #     tmp_args += args
    #
    #     args_list = [y for x in args for y in x.split()]
    #
    #     for k, v in default_args.iteritems():
    #         if k not in args_list:
    #             tmp_args += [' '.join([k, str(v)])]
    #         else:
    #             # k_pos = [i for i, s in enumerate(args) if k in s][0]
    #             # print "Printing tmp_args while updating"
    #             # print tmp_args[k_pos]
    #             # tmp_args[k_pos] = tmp_args[k_pos].replace(v, v))
    #             # print tmp_args[k_pos]
    #             pass
    #
    #     return ' '.join(tmp_args)

    def make_target(self, name, input, *args, **kwargs ):
        name_str = "_" + name + "_"
        self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
            input + name_str + self.out_suffix).hexdigest() + ".txt"
        return
### Third-party command line tools ###

def create_wrapper_class(wrapper_yaml):
    with open(os.path.abspath("../bioflowsutils/function_texts.py")) as f:
        print "RUNNING EXEC"
        exec (f.read()) in locals()


    with open(wrapper_yaml) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        programs_list = yaml.load(file, Loader=yaml.FullLoader)

    progs_dict = dict()

    ## ******* Some definitions *********
    ##
    ##  name: The actual program key generated. Example samtools_sort_round_2
    ##  input: The Sample ID
    ##  *args: The options section of the YAML passed in by the user
    ##  **kwargs: This is usually the generic workflow options section of the YAML passed in by the user

    function_text_base = function_text1
    function_text_base = """
def __init__(self, name, input, *args, **kwargs):
        self.reset_add_args()
        self.input = input
        self.make_target(name, input, *args, **kwargs)
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)
        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
        else:
            self.job_parms.update({'mem': 4000, 'time': 300, 'ncpus': 1})
        default_pre_args = {}
        default_post_args= {}
        self.add_pre_args = self.update_default_args(default_pre_args, *args, **kwargs)
        self.add_post_args = self.update_default_args(default_post_args, *args, **kwargs)
        insert_cmd
        self.run_command = self.cmd
        return
        """

    def make_function_object(txt):
        loc = dict()
        exec(txt,globals(),loc)
        #print(loc)
        return loc

#Test=type("gsnap",(object,), {"__init__": make_function_object(function_text)['__init__']})

    #print (function_text)
    indent='        '

    for k,v in programs_list.iteritems():
        function_text = locals()[v['function_text']]
        print "\n *** looking for exec results***\n"
        print function_text
        print "\n *** looking for exec results***\n"
        cmd_info = v['command_setup']
        print(cmd_info)
        if cmd_info.has_key('default_pre_args') and cmd_info['default_pre_args'] is not None:
            function_text=function_text.replace('default_pre_args = {}', cmd_info['default_pre_args'])
        compile_commands = "self.cmd = '" + cmd_info['call'] + "' +  ' '" +'\n'
        compile_commands += indent + "self.cmd +=  self.add_pre_args\n"
        compile_commands += '\n'.join([indent + x.strip('\n')  for x in cmd_info['inputs']]) + '\n'
        #compile_commands += '\n'.join([indent + "self.cmd += ' ' + " + x + "" for x in cmd_info['outputs']]) + '\n'
        if cmd_info.has_key('default_post_args') and cmd_info['default_post_args'] is not None  :
            function_text=function_text.replace('default_post_args = {}', cmd_info['default_post_args'])
            compile_commands += indent + "self.cmd +=  self.add_post_args\n"
        #compile_commands += '\n'.join([indent + "self.cmd += ' ' + " + x + "" for x in cmd_info['logs']])
        function_text = function_text.replace("insert_cmd", compile_commands)
        #print (function_text)
        #print "\n\n\n"
        #print (repr(function_text))
        progs_dict[k]=type(k.title(),(BaseWrapperNew,), make_function_object(function_text))
    return progs_dict




#wrapper_def= 'programs_config.yaml'
#wrappers=create_wrapper_class(wrapper_def)
#print(wrappers)
#print (dir(wrappers))
