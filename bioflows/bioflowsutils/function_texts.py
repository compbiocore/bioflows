function_text1 = """
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