import unittest, saga, luigi
from unittest import TestCase
from definedworkflows.rnaseq.rnaseqworkflow import RnaSeqFlow as rsw
from collections import OrderedDict
from definedworkflows.rnaseq.rnaseqworkflow import TaskFlow
import luigi.contrib.ssh as lcs


class TestRnaSeqFlowFunctions(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_mac_remote_pe_celegans.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v


    def test_parse_prog_info(self):
        self.rw1.parse_prog_info()
        print "\n***** Printing Progs dict ******\n"
        for k, v in self.rw1.progs.iteritems():
            print k, v

        rev_progs = OrderedDict(reversed(self.rw1.progs.items()))
        print "\n***** Printing Progs dict in reverse ******\n"
        for k, v in rev_progs.iteritems():
            print k, v
        for k, v in self.rw1.progs_job_parms.iteritems():
            print k, v

    def test_symlink_fastqs(self):
        # self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
        #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
        self.rw1.parse_sample_info()
        self.rw1.symlink_fastqs()

    def test_chain_commands_se(self):
        self.rw1.sample_fastq_work = {'N2': '/gpfs/scratch/aragaven/test_workflow/sampN2.fq.gz',
                                      'N3': '/gpfs/scratch/aragaven/test_workflow/sampN3.fq.gz'}
        # self.rw1.symlink_fastqs
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        print self.rw1.progs
        print "\n***** Printing Chained Commands ******\n"
        self.rw1.set_base_kwargs()
        self.rw1.chain_commands()

    def test_parse_sample_info_from_file(self):
        if 'fastq_file' in self.rw1.sample_manifest.keys():
            self.rw1.parse_sample_info_from_file()
            print "\n***** Printing Sample Info parsed from file ******\n"
            for k, v in self.rw1.sample_fastq.iteritems():
                print k, v
            print self.rw1.paired_end
        else:
            print "\n***** Sample Info is not being parsed from file ******\n"

    def test_parse_sample_info_from_sra(self):
        self.rw1.setup_paths()
        self.rw1.test_paths()
        self.rw1.parse_sample_info_from_sra()
        print "\n***** Printing Sample Info Parsed from SRA ******\n"
        print "\n # Samples parsed:", len(self.rw1.sample_fastq.keys())
        for k, v in self.rw1.sample_fastq.iteritems():
            print k, v
        print self.rw1.paired_end

    def test_download_sra_cmds(self):
        self.rw1.setup_paths()
        self.rw1.test_paths()
        self.rw1.parse_sample_info_from_sra()
        print "\n***** Printing commands to download from SRA ******\n"
        self.rw1.download_sra_cmds()
        return


class TestRnaSeqFlowLocalToRemoteSE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_mac_remote_se_mus.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)


class TestRnaSeqFlowLocalToRemotePE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_mac_remote_pe_celegans.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        #luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    #workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)],
                    local_scheduler=False, workers = len(self.rw1.sample_fastq_work.keys()), lock_size = 1)


class TestRnaSeqFlowLocalSlurmSE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_localhost_slurm_se_mus.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)


class TestRnaSeqFlowLocalSlurmPE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_localhost_slurm_pe_celegans.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)


class TestRnaSeqFlowSRALocalSlurmSE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_sra_localhost_slurm_se_mus.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.download_sra_cmds()
        # self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)


class TestRnaSeqFlowSRALocalSlurmPE(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_sra_localhost_slurm_pe_mus.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.download_sra_cmds()
        #self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)



class TestRnaSeqFlowSRALocalSlurmSEDual(TestCase):
    def setUp(self):
        self.parmsfile = "test_run_sra_localhost_slurm_se_mus_spnuemonia.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing ******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

    # def test_symlink_fastqs(self):
    #     #self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #      #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info_from_file()
    #     self.rw1.symlink_fastqs()

    def test_run_chain_commands(self):
        self.rw1.parse_prog_info()
        self.rw1.test_paths()
        self.rw1.download_sra_cmds()
        # self.rw1.symlink_fastqs()
        # self.rw1.set_base_kwargs()
        self.rw1.chain_commands()
        luigi.build([TaskFlow(tasks=self.rw1.allTasks, task_name=self.rw1.bioproject)], local_scheduler=True,
                    workers=len(self.rw1.sample_fastq_work.keys()), lock_size=1)

        ## Need to write another test to test the luigi web interface

        # luigi.build([TaskFlow(tasks=self.rw1.allTasks)], local_scheduler=False, workers=2, lock_size=3)



if __name__ == '__main__':
    # run all tests
    # unittest.main()

    ## Test specific workflow function

    # suite = unittest.TestSuite()
    # suite.addTest(TestRnaSeqFlowFunctions("test_parse_prog_info"))
    # suite.addTest(TestRnaSeqFlowFunctions("test_chain_commands_se"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific function

    # suite = unittest.TestSuite()
    # suite.addTest(TestRnaSeqFlowLocalHostSE("test_download_sra_cmds"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)



    ## Runs  only a specific class for SE Mouse from my mac to CCV

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowLocalToRemoteSE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific class for PE C elegans from my mac to CCV
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowLocalToRemotePE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific class for SE Mouse locally on CCV

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowLocalSlurmSE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific class for PE c elegans locally on CCV

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowLocalSlurmPE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific class for SE mus from SRA locally on CCV

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowSRALocalSlurmSE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    ## Runs  only a specific class for PE mus from SRA locally on CCV
    #
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowSRALocalSlurmPE)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # Runs  only a specific class for SE  dual RNA Seq mus and S. pnuemonia from SRA locally on CCV

    suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowSRALocalSlurmSEDual)
    runner = unittest.TextTestRunner()
    runner.run(suite)
