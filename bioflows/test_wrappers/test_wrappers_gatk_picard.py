import os
import sys
import unittest

print(sys.path)

import bioflows.bioflowsutils.wrappers as wr
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as dsw


class TestGatkInit(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe_gatk_picard.yaml"
        self.dw1 = dsw(self.parmsfile)
        self.dw1.set_base_kwargs()
        self.dw1.parse_prog_info()

    def test_gatk_realignerTargetcreator(self):
        self.wrapper_name = 'gatk_RealignerTargetCreator'
        self.dw1.update_job_parms(self.wrapper_name)
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_RealignerTargetCreator.log'),
                                 **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing GATK REALIGNER TARGET CREATOR command *****\n"
        print self.gatk_test.run_command
        out_command = "gatk  -Xmx30000M  -T RealignerTargetCreator -I /gpfs/scratch/alignments/test_samp.dedup.rg.srtd.bam "
        out_command += "-o /gpfs/scratch/gatk_results/test_samp_realign_targets.intervals "
        out_command += "-R /gpfs/scratch/test.fa -known /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_RealignerTargetCreator_err.log 1>/gpfs/scratch/logs/test_samp_gatk_RealignerTargetCreator.log"
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())

    def test_gatk_indelRealigner(self):
        self.wrapper_name = 'gatk_IndelRealigner'
        self.dw1.update_job_parms(self.wrapper_name)
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_IndelRealigner.log'),
                                 **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing GATK INDEL REALIGNER command *****\n"
        out_command = "gatk  -Xmx30000M  -T IndelRealigner "
        out_command += "-I /gpfs/scratch/alignments/test_samp.dedup.rg.srtd.bam OUTPUT=/gpfs/scratch/alignments/test_samp.dedup.rg.srtd.realigned.bam "
        out_command += "-R /gpfs/scratch/test.fa -targetIntervals /gpfs/scratch/gatk_results/test_samp_realign_targets.intervals --filter_bases_not_stored "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_IndelRealigner_err.log 1>/gpfs/scratch/logs/test_samp_gatk_IndelRealigner.log"
        print self.gatk_test.run_command
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())

    def test_gatk_BaseRecalibrator(self):
        self.wrapper_name = 'gatk_BaseRecalibrator'
        self.dw1.update_job_parms(self.wrapper_name)
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_BaseRecalibrator.log'),
                                 **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing GATK Base Recalibrator command *****\n"
        print self.gatk_test.run_command
        out_command = "gatk -Xmx30000M -T BaseRecalibrator "
        out_command += "-I /gpfs/scratch/alignments/test_samp.dedup.rg.srtd.realigned.bam  "
        out_command += "-R /gpfs/scratch/test.fa "
        out_command += "-knownSites /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/dbsnp_138.hg19.vcf "
        out_command += "-knownSites /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf "
        out_command += "-nct 8 -o /gpfs/scratch/gatk_results/test_samp_recal_table.txt "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_BaseRecalibrator_err.log 1>/gpfs/scratch/logs/test_samp_gatk_BaseRecalibrator.log"
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())

    def test_gatk_BaseRecalibrator_bqsr(self):
        self.wrapper_name = 'gatk_BaseRecalibrator_duprun_1'
        self.dw1.update_job_parms(self.wrapper_name)
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_BaseRecalibrator.log'),
                                 **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing GATK Base Recalibrator with BQSR command *****\n"
        print self.gatk_test.run_command
        out_command = "gatk -Xmx30000M -T BaseRecalibrator "
        out_command += "-I /gpfs/scratch/alignments/test_samp.dedup.rg.srtd.realigned.bam "
        out_command += "-R /gpfs/scratch/test.fa "
        out_command += "-knownSites /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/dbsnp_138.hg19.vcf "
        out_command += "-knownSites /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf "
        out_command += "-nct 8 -BQSR /gpfs/scratch/gatk_results/test_samp_recal_table.txt "
        out_command += "-o /gpfs/scratch/gatk_results/test_samp_post_recal_table.txt "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_BaseRecalibrator_err.log 1>/gpfs/scratch/logs/test_samp_gatk_BaseRecalibrator.log"
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())

    # @unittest.skip("demonstrating skipping")
    def test_gatk_PrintReads(self):
        self.wrapper_name = 'gatk_PrintReads'
        self.dw1.update_job_parms(self.wrapper_name)
        self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                 stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_PrintReads.log'),
                                 **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing GATK Print Reads command *****\n"
        print self.gatk_test.run_command
        out_command = "gatk -Xmx10000M -T PrintReads "
        out_command += "-I /gpfs/scratch/alignments/test_samp.dedup.rg.srtd.realigned.bam "
        out_command += "-R /gpfs/scratch/test.fa "
        out_command += "-BQSR /gpfs/scratch/gatk_results/test_samp_recal_table.txt "
        out_command += "-o /gpfs/scratch/alignments/test_samp.gatk.recal.bam "
        out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_PrintReads_err.log 1>/gpfs/scratch/logs/test_samp_gatk_PrintReads.log"
        self.assertEqual(self.gatk_test.run_command.split(), out_command.split())


def test_gatk_AnalyzeCovariates(self):
    self.wrapper_name = 'gatk_AnalyzeCovariates'
    self.dw1.update_job_parms(self.wrapper_name)
    self.gatk_test = wr.Gatk(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                             stdout=os.path.join(self.dw1.log_dir, 'test_samp_gatk_AnalyzeCovariates.log'),
                             **dict(self.dw1.new_base_kwargs))
    print "\n***** Testing GATK ANALYZECOVRIATES command *****\n"
    print self.gatk_test.run_command
    out_command = "gatk -Xmx30000M -T PrintReads "
    out_command += "INPUT=/gpfs/scratch/alignments/test_samp.dedup.rg.srtd.realigned.bam "
    out_command += "-R /gpfs/scratch/test.fa "
    out_command += "-BQSR /gpfs/scratch/gatk_results/test_samp_recal_table.txt "
    out_command += "-o /gpfs/scratch/alignments/test_samp.gatk.recal.bam "
    out_command += "2>>/gpfs/scratch/logs/test_samp_gatk_PrintReads_err.log 1>/gpfs/scratch/logs/test_samp_gatk_PrintReads.log"
    self.assertEqual(self.gatk_test.run_command.split(), out_command.split())


class TestPicardInit(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe_gatk_picard.yaml"
        self.dw1 = dsw(self.parmsfile)
        self.dw1.set_base_kwargs()
        self.dw1.parse_prog_info()

    def test_picard_markduplicates(self):
        self.wrapper_name = 'picard_MarkDuplicates'
        self.dw1.update_job_parms(self.wrapper_name)
        self.picard_test = wr.Picard(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                     stdout=os.path.join(self.dw1.log_dir, 'test_samp_picard_markduplicates.log'),
                                     **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing Picard MarkDuplicates command *****\n"
        print self.picard_test.run_command
        out_command = "picard MarkDuplicates  -Xmx30000M INPUT=/gpfs/scratch/alignments/test_samp.rg.srtd.bam "
        out_command += "M=/gpfs/scratch/qc/test_samp_mark_duplicates_picard.txt  CREATE_INDEX=true VALIDATION_STRINGENCY=LENIENT "
        out_command += "OUTPUT=/gpfs/scratch/alignments/test_samp.dedup.rg.srtd.bam REMOVE_DUPLICATES=true "
        out_command += "2>>/gpfs/scratch/logs/test_samp_picard_MarkDuplicates_err.log 1>/gpfs/scratch/logs/test_samp_picard_markduplicates.log"
        self.assertEqual(self.picard_test.run_command.split(), out_command.split())

    def test_picard_addorreplacereadgroups(self):
        self.wrapper_name = 'picard_AddOrReplaceReadGroups'
        self.dw1.update_job_parms(self.wrapper_name)
        self.picard_test = wr.Picard(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                     stdout=os.path.join(self.dw1.log_dir,
                                                         'test_samp_picard_AddOrReplaceReadGroups.log'),
                                     **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing Picard AddOrReplaceReadGroups command *****\n"
        print self.picard_test.run_command
        out_command = "picard AddOrReplaceReadGroups  -Xmx30000M INPUT=/gpfs/scratch/alignments/test_samp.dup.srtd.bam OUTPUT=/gpfs/scratch/alignments/test_samp.rg.srtd.bam "
        out_command += "RGID=test_samp RGLB=lib1 RGPL=illumina  RGPU=unit1 RGCN=BGI RGSM=test_samp VALIDATION_STRINGENCY=LENIENT "
        out_command += "2>>/gpfs/scratch/logs/test_samp_picard_AddOrReplaceReadGroups_err.log 1>/gpfs/scratch/logs/test_samp_picard_AddOrReplaceReadGroups.log"
        self.assertEqual(self.picard_test.run_command.split(), out_command.split())

    def test_picard_buildbamindex(self):
        self.wrapper_name = 'picard_BuildBamIndex'
        self.dw1.update_job_parms(self.wrapper_name)
        self.picard_test = wr.Picard(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                     stdout=os.path.join(self.dw1.log_dir, 'test_samp_picard_BuildBamIndex.log'),
                                     **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing Picard BuildBamIndex command *****\n"
        print self.picard_test.run_command
        out_command = "picard BuildBamIndex -Xmx30000M INPUT=/gpfs/scratch/alignments/test_samp.gatk.recal.bam VALIDATION_STRINGENCY=LENIENT "
        out_command += "2>>/gpfs/scratch/logs/test_samp_picard_BuildBamIndex_err.log 1>/gpfs/scratch/logs/test_samp_picard_BuildBamIndex.log"
        self.assertEqual(self.picard_test.run_command.split(), out_command.split())

    def test_picard_collect_wgs_metrics(self):
        self.wrapper_name = 'picard_CollectWgsMetrics'
        self.dw1.update_job_parms(self.wrapper_name)
        self.picard_test = wr.Picard(self.wrapper_name, "test_samp", *self.dw1.progs[self.wrapper_name],
                                     stdout=os.path.join(self.dw1.log_dir, 'test_samp_picard_CollectWgsMetrics.log'),
                                     **dict(self.dw1.new_base_kwargs))
        print "\n***** Testing Picard CollectWgsMetrics command *****\n"
        print self.picard_test.run_command
        out_command = "picard CollectWgsMetrics -Xmx30000M INPUT=/gpfs/scratch/alignments/test_samp.dup.srtd.bam "
        out_command += "OUTPUT=/gpfs/scratch/qc/test_samp_wgs_stats_picard.txt REFERENCE_SEQUENCE=/gpfs/scratch/test.fa "
        out_command += "MINIMUM_MAPPING_QUALITY=20 MINIMUM_BASE_QUALITY=20 COUNT_UNPAIRED=true VALIDATION_STRINGENCY=LENIENT "
        out_command += "2>>/gpfs/scratch/logs/test_samp_picard_CollectWgsMetrics_err.log 1>/gpfs/scratch/logs/test_samp_picard_CollectWgsMetrics.log"
        self.assertEqual(self.picard_test.run_command.split(), out_command.split())

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestGatkInit("test_gatk_realignerTargetcreator"))
    suite.addTest(TestGatkInit("test_gatk_indelRealigner"))
    suite.addTest(TestGatkInit("test_gatk_BaseRecalibrator"))
    suite.addTest(TestGatkInit("test_gatk_BaseRecalibrator_bqsr"))
    suite.addTest(TestGatkInit("test_gatk_PrintReads"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    # suite.run()
