import bioflows.bioflowsutils.wrappers_samtools as wr
import bioflows.bioflowsutils.wrappers as genwr
import unittest, os,saga, pytest
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as mainwf

@pytest.fixture(params=["/Users/aragaven/PycharmProjects/bioflows/bioflows/test_wrappers/test_wrappers_pe.yaml"])
def baseWrapper(request):
    return mainwf(request.param)

def test_samtools_index(baseWrapper):
    baseWrapper.set_base_kwargs()
    baseWrapper.parse_prog_info()
    wrapper_name = 'samtools_index'
    new_base_kwargs = baseWrapper.update_prog_suffixes(wrapper_name)
    samtoolindex_test = wr.SamTools(wrapper_name, "test_samp",
                                   stdout=os.path.join(baseWrapper.run_parms['work_dir'],
                                                       'samtools_index.log'),
                                   **dict(new_base_kwargs))
    print samtoolindex_test.run_command
    print samtoolindex_test.__dict__
    return

def test_samtools_sort(baseWrapper):
    baseWrapper.set_base_kwargs()
    baseWrapper.parse_prog_info()
    wrapper_name = 'samtools_sort'
    new_base_kwargs = baseWrapper.update_prog_suffixes(wrapper_name)
    samtoolsort_test = wr.SamTools(wrapper_name, "test_samp",
                                        stdout=os.path.join(baseWrapper.run_parms['work_dir'],
                                                            'samtools_sort.log'),
                                        **dict(new_base_kwargs))
    assert samtoolsort_test.run_command == "samtools sort -o /gpfs/scratch/alignments/test_samp.tst.srtd.bam /gpfs/scratch/alignments/test_samp.mapped.bam 2>>/gpfs/scratch/logs/test_samp_samtools_sort_err.log 1>/gpfs/scratch/logs/test_samp_samtools_sort.log"
    return

def test_htseq_counts(baseWrapper):
    baseWrapper.set_base_kwargs()
    baseWrapper.parse_prog_info()
    wrapper_name = 'htseq-count'
    new_base_kwargs = baseWrapper.update_prog_suffixes(wrapper_name)
    print "\n***** Testing Htseq_wrapper command *****\n"
    htseq_test = genwr.HtSeqCounts(wrapper_name, "test_samp", *['-r name', '--secondary-alignments=ignore'],
                                         stdout=os.path.join(baseWrapper.run_parms['work_dir'],
                                                             baseWrapper.run_parms['log_dir'],
                                                             'test_samp.log'),
                                         **dict(new_base_kwargs))
    print htseq_test.run_command

class TestHtSeq(unittest.TestCase):
    def setUp(self):
        self.parmsfile = "test_wrappers_pe.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.parse_prog_info()
        self.wrapper_name = 'htseq-count'
        self.htseq_test = genwr.HtSeqCounts(self.wrapper_name, "test_samp",
                                         stdout=os.path.join(self.rw1.run_parms['work_dir'],
                                                             self.rw1.run_parms['log_dir'],
                                                             'test_samp.log'),
                                         **dict(self.rw1.base_kwargs))



class TestSamtoolsIndex(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'samtools'
        self.samtoolsindex_test = wr.SamIndex(self.wrapper_name, "test_samp",
                                              stdout=os.path.join(self.rw1.run_parms['work_dir'], 'samtools_index.log'),
                                              **dict(self.rw1.base_kwargs))

    def test_samtoolsindex_wrapper(self):
        print "\n***** Testing samtoolindex_wrapper command *****\n"
        print self.samtoolsindex_test.run_command

        # print "\n***** Testing samtoolindex_wrapper *****\n"
        # for k, v in self.samtoolsindex_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"


if __name__ == '__main__':
    unittest.main()
