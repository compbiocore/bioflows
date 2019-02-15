import unittest

import bioflows.bioflowsutils.wrappers as wr
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as rsw


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
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'fastqc'
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.fastqc_test = wr.FastQC(self.wrapper_name, "test_samp", **dict(new_base_kwargs))


    def test_fastqc_wrapper(self):
        print "\n***** Testing Fastqc_wrapper command *****\n"
        print self.fastqc_test.run_command
        out_command = "fastqc  -o /gpfs/scratch/qc /gpfs/scratch/fastq/test_samp_1.fq.gz 2>>/gpfs/scratch/logs/test_samp_fastqc_err.log "
        out_command += "1>>/gpfs/scratch/logs/test_samp_fastqc.log; "
        out_command += "fastqc -o /gpfs/scratch/qc /gpfs/scratch/fastq/test_samp_2.fq.gz 2>>/gpfs/scratch/logs/test_samp_fastqc_err.log "
        out_command += "1>>/gpfs/scratch/logs/test_samp_fastqc.log"
        self.assertEqual(self.fastqc_test.run_command.split(), out_command.split())

class TestGsnap(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'gsnap'
        self.add_args = self.rw1.progs[self.wrapper_name]
        #use  *self.add_args to unroll the list
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.gsnap_test = wr.Gsnap(self.wrapper_name, "test_samp", *self.add_args,
                                   **dict(new_base_kwargs))


    def test_gsnap_wrapper(self):
        print "\n***** Testing Gsnap_wrapper command *****\n"
        print self.gsnap_test.run_command
        print self.gsnap_test.job_parms
        out_command = "gsnap  -t 16 --gunzip -A sam -N1 --use-shared-memory=0 -d c_elegans_Ws8 "
        out_command += "-s caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.splicesites.iit "
        out_command += "/gpfs/scratch/fastq/test_samp_1.fq.gz /gpfs/scratch/fastq/test_samp_2.fq.gz 2>>/gpfs/scratch/logs/test_samp_gsnap_err.log "
        out_command += "1>/gpfs/scratch/alignments/test_samp.sam"
        self.assertEqual(self.gsnap_test.run_command.split(), out_command.split())


class TestSamMarkDup(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'bammarkduplicates2'
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.biobambammarkdup_test = wr.Biobambam(self.wrapper_name, "test_samp", **dict(new_base_kwargs))

    def test_sammarkdup_wrapper(self):
        print "\n***** Testing biobambam_wrapper command *****\n"
        print self.biobambammarkdup_test.run_command
        out_command = "bammarkduplicates2 index=0 I=/gpfs/scratch/alignments/test_samp.srtd.bam "
        out_command += "O=/gpfs/scratch/alignments/test_samp.dup.srtd.bam M=/gpfs/scratch/qc/test_samp.dup.metrics.txt "
        out_command += "2>>/gpfs/scratch/logs/test_samp_bammarkduplicates2_err.log 1>/gpfs/scratch/logs/test_samp_bammarkduplicates2.log"
        self.assertEqual(self.biobambammarkdup_test.run_command.split(), out_command.split())


# class TestQualimapRna(unittest.TestCase):
#
#     def setUp(self):
#         self.parmsfile = "test_wrappers_pe.yaml"
#         self.rw1 = rsw(self.parmsfile)
#         # self.rw1.parse_prog_info()
#         self.wrapper_name = 'qualimap_rnaseq'
#         self.add_args = self.rw1.progs[self.wrapper_name]
#         self.qualimap_test = wr.QualiMapRnaSeq(self.wrapper_name, "test_samp", *self.add_args,
#                                                **dict(self.rw1.base_kwargs))
#
#     def test_qualimap_wrapper(self):
#         print "\n***** Testing Qualimap_wrapper command for RNASeq*****\n"
#         print self.qualimap_test.run_command
#         out_command = "qualimap  -Xmx10000M rnaseq  -gtf /gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf "
#         out_command += "-bam /gpfs/scratch/alignments/test_samp.dup.srtd.bam "
#         out_command += "-outdir /gpfs/scratch/qc/test_samp 2>>/gpfs/scratch/logs/test_samp_qualimap_rnaseq_err.log 1>/gpfs/scratch/logs/qualimap.log; "
#         out_command += "cp  /gpfs/scratch/qc/test_samp/qualimapReport.html  /gpfs/scratch/qc/test_samp/test_samp_qualimapReport.html "
#         self.assertEqual(self.qualimap_test.run_command.split(), out_command.split())


class TestQualimap(unittest.TestCase):
    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        # self.rw1.parse_prog_info()
        self.wrapper_name = 'qualimap_bamqc'
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.add_args = self.rw1.progs[self.wrapper_name]
        self.qualimap_test = wr.QualiMap(self.wrapper_name, "test_samp", *self.add_args,
                                         **dict(new_base_kwargs))

    def test_qualimap_wrapper(self):
        print "\n***** Testing Qualimap_wrapper command for DNASeq*****\n"
        print self.qualimap_test.run_command
        out_command = "qualimap  -Xmx10000M bamqc -nr 10000 -c  -bam /gpfs/scratch/alignments/test_samp.dup.srtd.bam "
        out_command += "-outdir /gpfs/scratch/qc/test_samp 2>>/gpfs/scratch/logs/test_samp_qualimap_err.log"
        out_command += " 1>/gpfs/scratch/logs/test_samp_qualimap.log; "
        out_command += "cp  /gpfs/scratch/qc/test_samp/qualimapReport.html  /gpfs/scratch/qc/test_samp/test_samp_qualimapReport.html "
        self.assertEqual(self.qualimap_test.run_command.split(), out_command.split())


# class TestSalmon(unittest.TestCase):
#     def setUp(self):
#         self.parmsfile = "test_wrappers_pe.yaml"
#         self.rw1 = rsw(self.parmsfile)
#         self.rw1.parse_prog_info()
#         self.wrapper_name = 'salmon'
#         self.salmon_test = wr.SalmonCounts(self.wrapper_name, "test_samp", *self.rw1.progs['salmon'],
#                                            **dict(self.rw1.base_kwargs))
#
#     def test_salmon_counts_wrapper(self):
#         print "\n***** Testing Salmon_wrapper command *****\n"
#         print self.salmon_test.run_command
#         out_command = "salmon quant -g /gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf "
#         out_command += "-i /gpfs/data/cbc/cbcollab/cbc_ref/salmon_index/c_elegans_PRJNA13758_WBPS8_mRNA_transcripts_index "
#         out_command += "-l A -1 /gpfs/scratch/fastq/test_samp_1.fq.gz -2 /gpfs/scratch/fastq/test_samp_2.fq.gz -o /gpfs/scratch/expression/test_samp_salmon_counts "
#         out_command += "2>>/gpfs/scratch/logs/test_samp_salmon_quant_err.log 1>>/gpfs/scratch/logs/test_samp_salmon_quant_err.log; "
#         out_command += "cp  /gpfs/scratch/expression/test_samp_salmon_counts/quant.genes.sf /gpfs/scratch/expression/test_samp_salmon_quant.genes.txt"
#         self.assertEqual(self.salmon_test.run_command.split(), out_command.split())


# class TestHtSeq(unittest.TestCase):
#     def setUp(self):
#         self.parmsfile = "test_wrappers_pe.yaml"
#         self.rw1 = rsw(self.parmsfile)
#         self.rw1.parse_prog_info()
#         self.wrapper_name = 'htseq-count'
#         self.htseq_test = wr.HtSeqCounts(self.wrapper_name, "test_samp",
#                                          stdout=os.path.join(self.rw1.run_parms['work_dir'],
#                                                              self.rw1.run_parms['log_dir'],
#                                                              'test_samp.log'),
#                                          **dict(self.rw1.base_kwargs))
#
#     def test_htseq_counts_wrapper(self):
#         print "\n***** Testing Htseq_wrapper command *****\n"
#         print self.htseq_test.run_command

class TestBwaMem(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'bwa_mem'
        self.add_args = self.rw1.progs[self.wrapper_name]
        #use  *self.add_args to unroll the list
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.bwa_test = wr.Bwa(self.wrapper_name, "test_samp", *self.add_args,
                                   **dict(new_base_kwargs))


    def test_bwa_wrapper(self):
        print "\n***** Testing Bwa_wrapper command *****\n"
        print self.bwa_test.run_command
        print self.bwa_test.job_parms
        out_command = "bwa mem  -t 16 index.db /gpfs/scratch/fastq/test_samp_1.fq.gz /gpfs/scratch/fastq/test_samp_2.fq.gz"
        out_command += " 2>>/gpfs/scratch/logs/test_samp_bwa_mem_err.log"
        out_command += " 1>/gpfs/scratch/alignments/test_samp.sam"




class TestTrimmomaticPE(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'trimmomatic_PE'
        self.add_args = self.rw1.progs[self.wrapper_name]
        #use  *self.add_args to unroll the list
        self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.trimmomatic_pe_test = wr.Trimmomatic(self.wrapper_name, "test_samp", *self.add_args,
                                                  **dict(new_base_kwargs))

    def test_trimmomatic_wrapper(self):
        print "\n***** Testing Trimmomatic wrapper command *****\n"
        print self.trimmomatic_pe_test.run_command
        print self.trimmomatic_pe_test.job_parms
        out_command = "trimmomatic PE -threads 8  "
        out_command += "-trimlog /gpfs/scratch/logs/test_samptrimmomatic_PE.log  /gpfs/scratch/fastq/test_samp_1.fq.gz /gpfs/scratch/fastq/test_samp_2.fq.gz "
        out_command += "-baseout /gpfs/scratch/fastq/test_samp_tr.fq.gz "
        out_command += "ILLUMINACLIP:/gpfs/data/cbc/cbc_conda_v1/envs/cbc_conda/opt/trimmomatic-0.36/adapters/TruSeq3-PE-2.fa:2:30:5:6:true SLIDINGWINDOW:10:25 MINLEN:75 "
        out_command += "2>>/gpfs/scratch/logs/test_samp_trimmomatic_PE_err.log 1>/gpfs/scratch/logs/test_samp_trimmomatic.log; "
        out_command += "mv -v /gpfs/scratch/fastq/test_samp_tr_1P.fq.gz /gpfs/scratch/fastq/test_samp_1_tr.fq.gz; "
        out_command += "mv -v /gpfs/scratch/fastq/test_samp_tr_2P.fq.gz /gpfs/scratch/fastq/test_samp_2_tr.fq.gz; "
        out_command += "rm -v /gpfs/scratch/fastq/test_samp_tr_1U.fq.gz; rm -v /gpfs/scratch/fastq/test_samp_tr_2U.fq.gz;"
        self.assertEqual(self.trimmomatic_pe_test.run_command.split(), out_command.split())


class TestFastqScreen(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'fastq_screen'
        self.add_args = self.rw1.progs[self.wrapper_name]
        # use  *self.add_args to unroll the list
        new_base_kwargs = self.rw1.update_job_parms(self.wrapper_name)
        self.fastq_screen_test = wr.FastqScreen(self.wrapper_name, "test_samp", *self.add_args,
                                                **dict(new_base_kwargs))


class TestSamtools(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'samtools_sort'
        self.add_args = self.rw1.progs[self.wrapper_name]
        # use  *self.add_args to unroll the list
        new_base_kwargs = self.rw1.update_job_parms(self.wrapper_name)
        new_base_kwargs = self.rw1.update_prog_suffixes(self.wrapper_name)
        self.samtools_sort_test = wr.SamTools(self.wrapper_name, "test_samp", *self.add_args,
                                              **dict(new_base_kwargs))

    def test_samtools_wrapper(self):
        print "\n***** Testing Samtools_wrapper command *****\n"
        print self.samtools_sort_test.run_command
        print self.samtools_sort_test.job_parms


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    # suite.addTest(TestBwaMem("test_bwa_wrapper"))
    # suite.addTest(TestPicard("test_picard_wrapper"))
    #suite.addTest(TestQualimap("test_qualimap_wrapper"))
    #suite.addTest(TestHtSeq("test_htseq_counts_wrapper"))
    # suite.addTest(TestSalmon("test_salmon_counts_wrapper"))
    # suite.addTest(TestSamMarkDup("test_sammarkdup_wrapper"))
    #suite.addTest(TestQualimapRna("test_qualimap_wrapper"))
    suite.addTest(TestFastqc("test_fastqc_wrapper"))
    suite.addTest(TestFastqc("test_bwa_wrapper"))

    # runner = unittest.TextTestRunner()
    # runner.run(suite)
