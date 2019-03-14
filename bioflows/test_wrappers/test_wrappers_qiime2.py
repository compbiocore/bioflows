import unittest

import bioflows.bioflowsutils.wrappers_qiime2 as wr
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as rsw


class TestQiime2(unittest.TestCase):

    def setUp(self):
        self.wrapper_name = "qiime2"
        self.parmsfile = "test_wrappers_qiime.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()

    # def test_qiime2_dada2_denoise_single_wrapper(self):
    #     self.wrapper_name = 'qiime_dada2_denoise-single'
    #     self.add_args = self.rw1.progs[self.wrapper_name]
    #     self.rw1.update_job_parms(self.wrapper_name)
    #     self.rw1.update_prog_suffixes(self.wrapper_name)
    #     print "\n***** Printing Chained Commands ******\n"
    #     self.rw1.chain_commands_qiime()
    #     print self.rw1.progs
    #
    #     self.qiime2_test = wr.Qiime2(self.wrapper_name, "EMPSingleEndSequences", *self.add_args,
    #                                  **dict(self.rw1.new_base_kwargs))
    #     print "\n***** Testing qiime dada2 denoise-single command *****\n"
    #     print self.qiime2_test.run_command
    #     out_command = "qiime dada2 denoise-single --i-demultiplexed-seqs /gpfs/scratch/qiime/demux.qza  --p-trim-left 0 "
    #     out_command += "--p-trunc-len 120  --o-representative-sequences /gpfs/scratch/qiime/rep-seqs-dada2.qza "
    #     out_command += "--o-table /gpfs/scratch/qiime/table-dada2.qza --o-denoising-stats /gpfs/scratch/qiime/stats-dada2.qza "
    #     out_command += "2>>/gpfs/scratch/logs/EMPSingleEndSequences_qiime_dada2_denoise-single_err.log "
    #     out_command += "1>/gpfs/scratch/logs/EMPSingleEndSequences_qiime_dada2_denoise-single.log"
    #     self.assertEqual(self.qiime2_test.run_command.split(), out_command.split())

    def test_qiime2_phylogeny_mafft_wrapper(self):
        self.wrapper_name = 'qiime_phylogeny_align-to-tree-mafft-fasttree'
        self.add_args = self.rw1.progs[self.wrapper_name]
        self.rw1.update_job_parms(self.wrapper_name)
        self.rw1.update_prog_suffixes(self.wrapper_name)
        print "\n***** Printing Chained Commands ******\n"
        self.rw1.chain_commands_qiime()
        print self.rw1.progs
        self.qiime2_test = wr.Qiime2(self.wrapper_name, "EMPSingleEndSequences", *self.add_args,
                                     **dict(self.rw1.new_base_kwargs))
        print "\n***** Testing qiime dada2 denoise-single command *****\n"
        print self.qiime2_test.run_command
        out_command = "qiime qiime phylogeny align-to-tree-mafft-fasttree --p-n-threads 2 "
        out_command += "--i-sequences /gpfs/scratch/qiime/rep-seqs.qza --o-alignment /gpfs/scratch/qiime/aligned-rep-seqs.qza  "
        out_command += "--o-masked-alignment /gpfs/scratch/qiime/masked-aligned-rep-seqs.qza --o-tree /gpfs/scratch/qiime/unrooted-tree.qza "
        out_command += "--o-rooted-tree /gpfs/scratch/qiime/rooted-tree.qza "
        out_command += "2>>/gpfs/scratch/logs/EMPPairedEndSequences_qiime_phylogeny_align-to-tree-mafft-fasttree_err.log "
        out_command += "1>/gpfs/scratch/logs/EMPPairedEndSequences_qiime_phylogeny_align-to-tree-mafft-fasttree.log"
        self.assertEqual(self.qiime2_test.run_command.split(), out_command.split())

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    # suite.addTest(TestBwaMem("test_bwa_wrapper"))
    # suite.addTest(TestPicard("test_picard_wrapper"))
    # suite.addTest(TestQualimap("test_qualimap_wrapper"))
    # suite.addTest(TestHtSeq("test_htseq_counts_wrapper"))
    # suite.addTest(TestSalmon("test_salmon_counts_wrapper"))
    # suite.addTest(TestSamMarkDup("test_sammarkdup_wrapper"))
    # suite.addTest(TestQualimapRna("test_qualimap_wrapper"))
    suite.addTest(TestQiime2("test_qiime2_dada2_denoise_single_wrapper"))
    # suite.addTest(TestFastqc("test_bwa_wrapper"))

    # runner = unittest.TextTestRunner()
    # runner.run(suite)
