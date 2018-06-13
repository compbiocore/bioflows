import os
import sys
import unittest

print(sys.path)

import bioflows.bioflowsutils.wrappers as wr
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import DnaSeqFlow as dsw


# class TestSamtools(unittest.TestCase):
#
#     def setUp(self):
#         self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
#         self.rw1 = rsw(self.parmsfile)
#         #self.rw1.parse_prog_info()
#         self.wrapper_name = 'samtools'
#         self.samtools_test=wr.SamTools(self.wrapper_name,"test_in.sam", cwd=self.rw1.run_parms['work_dir'],
#                                         stdout=os.path.join(self.rw1.run_parms['work_dir'],'samtools.log'))
#
#
#     def test_samtools_wrapper(self):
#         print "\n***** Testing samtools_wrapper command *****\n"
#         print self.samtools_test.run_command
#
#         print "\n***** Testing samtools_wrapper *****\n"
#         for k, v in self.samtools_test.__dict__.iteritems():
#             print k + ": " + str(v) +  "\n"

class TestGatkInit(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe_gatk_picard.yaml"
        self.dw1 = dsw(self.parmsfile)
        self.dw1.set_base_kwargs()
        self.dw1.parse_prog_info()

    def test_gatk_realignerTargetcreator(self):
        self.wrapper_name = 'gatk_RealignerTargetCreator'
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp",
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_RealignerTargetCreator.log'),
                                 **dict(self.dw1.base_kwargs))
        print "\n***** Testing GATK REALIGNER TARGET CREATOR command *****\n"
        print self.gatk_test.run_command
        out_command = "gatk  -Xmx10000M  RealignerTargetCreator INPUT=/gpfs/scratch/alignments/test_samp.dedup.rg.srtd.bam OUTPUT=/gpfs/scratch/qc/test_samp_realign_targets.intervals "
        out_command += "-R /gpfs/scratch/test.fa -known /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_RealignerTargetCreator_err.log 1>/gpfs/scratch/logs/test_samp_gatk_RealignerTargetCreator.log"
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())

    def test_gatk_indelRealigner(self):
        self.wrapper_name = 'gatk_IndelRealigner'
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp",
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_IndelRealigner.log'),
                                 **dict(self.dw1.base_kwargs))
        print "\n***** Testing GATK INDEL REALINER command *****\n"
        print self.gatk_test.run_command
        # self.assertEqual(self.gatk_test.run_command.split(), out_command.split())


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestGatkInit("test_gatk_realignerTargetcreator("))
    # suite.addTest(TestQualimap("test_qualimap_wrapper"))
    # suite.addTest(TestHtSeq("test_htseq_counts_wrapper"))
    # suite.addTest(TestSalmon("test_salmon_counts_wrapper"))
    # suite.addTest(TestSamMarkDup("test_sammarkdup_wrapper"))
    # suite.addTest(TestQualimapRna("test_qualimap_wrapper"))
    # suite.addTest(TestFastqc("test_fastqc_wrapper"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
