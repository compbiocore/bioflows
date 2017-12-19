import biobrewliteutils.wrappers as wr
import unittest, os, saga
from definedworkflows.rnaseq.rnaseqworkflow import BaseWorkflow as bwflw
from definedworkflows.rnaseq.rnaseqworkflow import RnaSeqFlow as rsw


#
# class TestWrapper(unittest.TestCase):
#
#     def setUp(self):
#         self.wrapper_name = "fastqc"
#         self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
#         self.rw1 = bwflw(self.parmsfile)
#         self.test_wrap = wr.BaseWrapper(self.wrapper_name,cwd=self.rw1.run_parms['work_dir'],
#                                         stdout=os.path.join(self.rw1.run_parms['work_dir'],'fastqc.log'))
#
#     def test_wrapper(self):
#         print "\n***** Testing  the Base wrapper class *****\n"
#         for k, v in self.test_wrap.__dict__.iteritems():
#             print k + ": " + str(v) +  "\n"
#         #print "**** Using inspect ***\n"
#         # for x in inspect.getmembers(self.test_wrap):
#         #     print x[0], x[1], "\n"n
#         #test_wrap.run('fastqc')
#
#     def test_check_version(self):
#         self.test_wrap.version()
#
#     def test_run(self):
#         self.test_wrap.setup_run()
#         self.assertEqual(self.test_wrap.cmd[0],"fastqc")
#
class TestFastqc(unittest.TestCase):

    def setUp(self):
        self.wrapper_name = "fastqc"
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'fastqc'
        self.fastqc_test = wr.FastQC(self.wrapper_name, "test_samp",
                                     stdout=os.path.join(self.rw1.run_parms['work_dir'], 'fastqc.log'),
                                     **dict(self.rw1.base_kwargs))


    def test_fastqc_wrapper(self):
        print "\n***** Testing Fastqc_wrapper command *****\n"
        print self.fastqc_test.run_command
        out_command = "fastqc  -o /gpfs/scratch/aragaven/test_workflow/qc /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_1.fq.gz 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_fastqc_err.log 1>/gpfs/scratch/aragaven/test_workflow/fastqc.log; fastqc /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_2.fq.gz 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_fastqc_err.log 1>/gpfs/scratch/aragaven/test_workflow/fastqc.log"
        self.assertEqual(self.fastqc_test.run_command, out_command)
        # print "\n***** Testing Fastqc_wrapper *****\n"
        # for k, v in self.fastqc_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"

class TestGsnap(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'gsnap'
        self.add_args = self.rw1.progs[self.wrapper_name]
        #use  *self.add_args to unroll the list
        new_base_kwargs = self.rw1.update_job_parms(self.wrapper_name)
        self.gsnap_test = wr.Gsnap(self.wrapper_name, "test_samp", *self.add_args,
                                   stdout=os.path.join(self.rw1.align_dir, 'gsnap.sam'),
                                   **dict(new_base_kwargs))


    def test_gsnap_wrapper(self):
        print "\n***** Testing Gsnap_wrapper command *****\n"
        print self.gsnap_test.run_command
        print self.gsnap_test.job_parms
        out_command = "gsnap  -t 8 --gunzip -A sam -N1 --use-shared-memory=0 -d Ensembl_Mus_musculus_GRCm38 -s Mus_musculus.GRCm38.88.splicesites.iit /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_1.fq.gz /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_2.fq.gz 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_gsnap_err.log 1>/gpfs/scratch/aragaven/test_workflow/alignments/gsnap.sam"
        self.assertEqual(self.gsnap_test.run_command, out_command)
        # print "\n***** Testing Gsnap_wrapper *****\n"
        # for k, v in self.gsnap_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"

class TestSamMarkDup(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'bammarkduplicates2'
        self.biobambammarkdup_test=wr.BiobambamMarkDup(self.wrapper_name,"test_samp",
                                                       stdout=os.path.join(self.rw1.log_dir, 'bammarkduplicates.log'),
                                                       **dict(self.rw1.base_kwargs))

    def test_sammarkdup_wrapper(self):
        print "\n***** Testing biobambam_wrapper command *****\n"
        print self.biobambammarkdup_test.run_command
        out_command = "bammarkduplicates2 index=0 I=/gpfs/scratch/aragaven/test_workflow/alignments/test_samp.srtd.bam O=/gpfs/scratch/aragaven/test_workflow/alignments/test_samp.dup.srtd.bam M=/gpfs/scratch/aragaven/test_workflow/qc/test_samp.dup.metrics.txt 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_bammarkduplicates2_err.log 1>/gpfs/scratch/aragaven/test_workflow/logs/bammarkduplicates.log"
        self.assertEqual(self.biobambammarkdup_test.run_command, out_command)
        # print "\n***** Testing biobambam_wrapper *****\n"
        # for k, v in self.biobambammarkdup_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"


class TestQualimap(unittest.TestCase):
    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        # self.rw1.parse_prog_info()
        self.wrapper_name = 'qualimap_rnaseq'
        self.qualimap_test = wr.QualiMapRnaSeq(self.wrapper_name, "test_samp",
                                               stdout=os.path.join(self.rw1.log_dir, 'qualimap.log'),
                                               **dict(self.rw1.base_kwargs))

    def test_qualimap_wrapper(self):
        print "\n***** Testing Qualimap_wrapper command *****\n"
        print self.qualimap_test.run_command
        out_command = "qualimap  -Xmx10000M rnaseq  -bam /gpfs/scratch/aragaven/test_workflow/alignments/test_samp.dup.srtd.bam  -gtf /gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf  -outdir /gpfs/scratch/aragaven/test_workflow/qc/test_samp 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_qualimap_rnaseq_err.log 1>/gpfs/scratch/aragaven/test_workflow/logs/qualimap.log;  cp  /gpfs/scratch/aragaven/test_workflow/qc/test_samp/qualimapReport.html  /gpfs/scratch/aragaven/test_workflow/qc/test_samp/test_samp_qualimapReport.html "
        self.assertEqual(self.qualimap_test.run_command, out_command)

        # print "\n***** Testing Qualimap_wrapper *****\n"
        # for k, v in self.qualimap_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"


class TestSalmon(unittest.TestCase):
    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.parse_prog_info()
        self.wrapper_name = 'salmon'
        self.salmon_test = wr.SalmonCounts(self.wrapper_name, "test_samp", *self.rw1.progs['salmon'],
                                           **dict(self.rw1.base_kwargs))

    def test_salmon_counts_wrapper(self):
        print "\n***** Testing Salmon_wrapper command *****\n"
        print self.salmon_test.run_command
        # out_command = "salmon quant -i /gpfs/data/cbc/cbcollab/cbc_ref/salmon_index/Mus_musculus.GRCm38.cdna.all_transcripts_sal_index -g /gpfs/data/cbc/cbcollab/ref_tools/Ensembl_mus_GRCm38.p5_rel89/Mus_musculus.GRCm38.89.gtf -l A -r /gpfs/data/cbc/Namrata/N1-BC1_AACCAG_R1.fastq.gz -o /gpfs/scratch/aragaven/namrata_final_2/expression/salmon_counts/N1_quant "
        # self.assertEqual(self.qualimap_test.run_command, out_command)

        # print "\n***** Testing Qualimap_wrapper *****\n"
        # for k, v in self.qualimap_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"


class TestHtSeq(unittest.TestCase):
    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.parse_prog_info()
        self.wrapper_name = 'htseq-count'
        self.htseq_test = wr.HtSeqCounts(self.wrapper_name, "test_samp",
                                         stdout=os.path.join(self.rw1.run_parms['work_dir'],
                                                             self.rw1.run_parms['log_dir'],
                                                             'test_samp.log'),
                                         **dict(self.rw1.base_kwargs))

    def test_htseq_counts_wrapper(self):
        print "\n***** Testing Htseq_wrapper command *****\n"
        print self.htseq_test.run_command



if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestHtSeq("test_htseq_counts_wrapper"))
    # suite.addTest(TestSalmon("test_salmon_counts_wrapper"))
    # suite.addTest(TestSamMarkDup("test_sammarkdup_wrapper"))
    # suite.addTest(TestQualimap("test_qualimap_wrapper"))
    #suite.addTest(TestFastqc("test_fastqc_wrapper"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
