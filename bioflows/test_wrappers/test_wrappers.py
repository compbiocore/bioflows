import os
import unittest

import bioflows.bioflowsutils.wrappers_samtools as wr
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import RnaSeqFlow as rsw


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

class TestKneaddata(unittest.TestCase):

    def setUp(self):
        self.wrapper_name = "kneaddata"
        self.parmsfile = "../test_metatranscriptome/test_run.yaml" # not made yet
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'fastqc'
        self.kneaddata_test = wr.Kneaddata(self.wrapper_name, "test_samp",
                                     stdout=os.path.join(self.rw1.run_parms['work_dir'], 'fastqc.log'),
                                     **dict(self.rw1.base_kwargs))


    def test_kneaddata_wrapper(self):
        print "\n***** Testing Kneaddata_wrapper command *****\n"
        print self.kneaddata_test.run_command
        out_command = "kneaddata -o /gpfs/scratch/aragaven/test_workflow/qc /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_1.fq.gz 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_fastqc_err.log 1>/gpfs/scratch/aragaven/test_workflow/fastqc.log; fastqc /gpfs/scratch/aragaven/test_workflow/fastq/test_samp_2.fq.gz 2>>/gpfs/scratch/aragaven/test_workflow/logs/test_samp_fastqc_err.log 1>/gpfs/scratch/aragaven/test_workflow/fastqc.log"
        self.assertEqual(self.fastqc_test.run_command, out_command)
        # print "\n***** Testing Fastqc_wrapper *****\n"
        # for k, v in self.fastqc_test.__dict__.iteritems():
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
        self.parmsfile = "test_wrappers_pe.yaml"
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

class TestBwaMem(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'bwa_mem'
        self.add_args = self.rw1.progs[self.wrapper_name]
        #use  *self.add_args to unroll the list
        new_base_kwargs = self.rw1.update_job_parms(self.wrapper_name)
        self.bwa_test = wr.Bwa(self.wrapper_name, "test_samp", *self.add_args,
                                   stdout=os.path.join(self.rw1.align_dir, 'bwa.sam'),
                                   **dict(new_base_kwargs))


    def test_bwa_wrapper(self):
        print "\n***** Testing Bwa_wrapper command *****\n"
        print self.bwa_test.run_command
        print self.bwa_test.job_parms



if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestBwaMem("test_bwa_wrapper"))
    suite.addTest(TestPicard("test_picard_wrapper"))
    #suite.addTest(TestQualimap("test_qualimap_wrapper"))
    #suite.addTest(TestHtSeq("test_htseq_counts_wrapper"))
    # suite.addTest(TestSalmon("test_salmon_counts_wrapper"))
    # suite.addTest(TestSamMarkDup("test_sammarkdup_wrapper"))
    #suite.addTest(TestQualimapRna("test_qualimap_wrapper"))
    #suite.addTest(TestFastqc("test_fastqc_wrapper"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
