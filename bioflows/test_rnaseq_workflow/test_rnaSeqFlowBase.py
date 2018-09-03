import unittest
from collections import OrderedDict
from unittest import TestCase

from bioflows.definedworkflows.rnaseq.rnaseqworkflow import RnaSeqFlow as rsw


class TestRnaSeqFlowFunctions(TestCase):

    def setUp(self):
        self.parmsfile = "test_run_mac_remote_pe_celegans.yaml"
        self.rw1 = rsw(self.parmsfile)

    def test_init(self):

        print "\n***** Printing config Parsing Class ******\n"
        print self.rw1.__dict__

        print "\n***** Printing config Parsing by item for base kwargs******\n"
        for k, v in self.rw1.base_kwargs.iteritems():
            print k, v
        print "\n  ***** Printing config Parsing by item******  \n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v


    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        print "\n***** Printing config Parsing Class ******\n"
        print self.rw1.__dict__

        print "\n***** Printing config Parsing by item******\n"
        for k, v in self.rw1.__dict__.iteritems():
            print k, v

        config_dict = {'sra_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/sra',
                       'qc_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/qc',
                       'paired_end': True,
                       'fastq_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/fastq',
                       'run_parms': OrderedDict(
                           [('conda_command', 'source activate cbc_conda'),
                            ('work_dir', '/gpfs/scratch/aragaven/test_workflow_pe_celegans'),
                            ('log_dir', 'logs'),
                            ('paired_end', True),
                            ('local_targets', True),
                            ('luigi_local_path', '/Users/aragaven/scratch/test_workflow_pe_celegans'),
                            ('saga_host', 'ssh.ccv.brown.edu'),
                            ('ssh_user', 'aragaven'),
                            ('saga_scheduler', 'slurm+ssh'),
                            ('gtf_file',
                             '/gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf')]
                       ),
                       'work_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans',
                       'expression_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/expression',
                       'job_params':
                           {'mem': 3000, 'saga_host': 'ssh.ccv.brown.edu', 'time': 80, 'saga_scheduler': 'slurm+ssh',
                            'work_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans'},
                       'align_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/alignments',
                       'experiment': 'rnaseq_pilot',
                       'log_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/logs',
                       # 'prog_wrappers': {'gatk_HaplotypeCaller': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'fastqc': <class 'bioflows.bioflowsutils.wrappers.FastQC'>,
                       #                  'gsnap': <class 'bioflows.bioflowsutils.wrappers.Gsnap'>,
                       #                  'feature_counts': <class 'bioflows.bioflowsutils.wrappers.BedtoolsCounts'>,
                       #                  'picard_CollectWgsMetrics': <class 'bioflows.bioflowsutils.wrappers.Picard'>,
                       #                  'qualimap_bamqc': <class 'bioflows.bioflowsutils.wrappers.QualiMap'>,
                       #                  'picard_MarkDuplicates': <class 'bioflows.bioflowsutils.wrappers.Picard'>,
                       #                  'bwa_mem': <class 'bioflows.bioflowsutils.wrappers.Bwa'>,
                       #                  'gatk_IndelRealigner': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'qualimap_rnaseq': <class 'bioflows.bioflowsutils.wrappers.QualiMap'>,
                       #                  'gatk_AnalyzeCovariates': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'picard_BuildBamIndex': <class 'bioflows.bioflowsutils.wrappers.Picard'>,
                       #                  'bammarkduplicates2': <class 'bioflows.bioflowsutils.wrappers.BiobambamMarkDup'>,
                       #                  'salmon': <class 'bioflows.bioflowsutils.wrappers.SalmonCounts'>,
                       #                  'gatk_BaseRecalibrator': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'bamtomapped': <class 'bioflows.bioflowsutils.wrappers.BamToMappedBam'>,
                       #                  'samsort': <class 'bioflows.bioflowsutils.wrappers.SamToolsSort'>,
                       #                  'picard_AddOrReplaceReadGroups': <class 'bioflows.bioflowsutils.wrappers.Picard'>,
                       #                  'bamtounmapped': <class 'bioflows.bioflowsutils.wrappers.BamToUnmappedBam'>,
                       #                  'gatk_RealignerTargetCreator': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'samindex': <class 'bioflows.bioflowsutils.wrappers.SamIndex'>,
                       #                  'htseq-count': <class 'bioflows.bioflowsutils.wrappers.HtSeqCounts'>,
                       #                  'gatk_PrintReads': <class 'bioflows.bioflowsutils.wrappers.Gatk'>,
                       #                  'samtobam': <class 'bioflows.bioflowsutils.wrappers.SamToBam'>},
                       'bioproject': 'Project_nm_1',
                       'checkpoint_dir': '/gpfs/scratch/aragaven/test_workflow_pe_celegans/checkpoints',
                       'sample_manifest': OrderedDict(
                           [('fastq_file', 'sampl_manifest_min_pe_celegans.csv'),
                            ('metadata', None)]
                       ),
                       'paths_to_test': ['/gpfs/scratch/aragaven/test_workflow_pe_celegans',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/logs',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/checkpoints',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/sra',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/fastq',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/alignments',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/qc',
                                         '/gpfs/scratch/aragaven/test_workflow_pe_celegans/expression'],
                       'workflow_sequence': [OrderedDict([('fastqc', 'default')]),
                                             OrderedDict([('gsnap', OrderedDict([('options',
                                                                                  OrderedDict([('-d', 'c_elegans_Ws8'),
                                                                                               ('-s',
                                                                                                'caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.splicesites.iit')])),
                                                                                 ('job_params',
                                                                                  OrderedDict([('mem', 40000),
                                                                                               ('ncpus', 16),
                                                                                               ('time', 600)]))]))]),
                                             OrderedDict([('qualimap', OrderedDict([('subcommand', 'rnaseq')]))]),
                                             OrderedDict([('salmon', OrderedDict([('options',
                                                                                   OrderedDict([('-g',
                                                                                                 '/gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf'),
                                                                                                ('-i',
                                                                                                 '/gpfs/data/cbc/cbcollab/cbc_ref/salmon_index/c_elegans_PRJNA13758_WBPS8_mRNA_transcripts_index')]))]))]),
                                             OrderedDict([('htseq-count', 'default')])]}


    def test_parse_prog_info(self):
        self.rw1.parse_prog_info()
        print "\n***** Printing Progs dict ******\n"
        for k, v in self.rw1.progs.iteritems():
            print k, v

        rev_progs = OrderedDict(reversed(self.rw1.progs.items()))
        print "\n***** Printing Progs dict in reverse ******\n"
        for k, v in rev_progs.iteritems():
            print k, v
        print "\n***** Printing Progs job Parms  ******\n"
        for k, v in self.rw1.progs_job_parms.iteritems():
            print k, v

    # TODO: Fix this test to make sense
    # def test_symlink_fastqs(self):
    #     # self.rw1.sample_fastq = {'sampN2': ['/gpfs/scratch/aragaven/test_workflow/N1-BC1_AACCAG_R1.fastq.gz'],
    #     #                        'sampN3': ['/gpfs/scratch/aragaven/test_workflow/N3-BC3_AGTGAG_R1.fastq.gz']}
    #     self.rw1.parse_sample_info()
    #     self.rw1.symlink_fastqs()


    def test_chain_commands_se(self):
        self.rw1.sample_fastq_work = {'N2': '/gpfs/scratch/aragaven/test_workflow/sampN2.fq.gz',
                                      'N3': '/gpfs/scratch/aragaven/test_workflow/sampN3.fq.gz'}
        # self.rw1.symlink_fastqs
        # self.rw1.set_base_kwargs()
        # self.rw1.parse_prog_info()
        print self.rw1.progs
        print "\n***** Printing Chained Commands ******\n"
        #self.rw1.set_base_kwargs()
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



if __name__ == '__main__':
    # run all tests
    # unittest.main()

    ## Test specific workflow function

    suite = unittest.TestSuite()
    # suite.addTest(TestRnaSeqFlowFunctions("test_init"))

    # suite.addTest(TestRnaSeqFlowFunctions("test_parse_config"))

    suite.addTest(TestRnaSeqFlowFunctions("test_parse_prog_info"))
    suite.addTest(TestRnaSeqFlowFunctions("test_chain_commands_se"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

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

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRnaSeqFlowSRALocalSlurmSEDual)
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
