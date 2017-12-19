import bioflowsutils.wrappers as wr
import unittest, os,saga
from definedworkflows.rnaseq.rnaseqworkflow import RnaSeqFlow as rsw


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

class TestSamToBam(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'samtools'
        self.samtobam_test = wr.SamToMappedBam(self.wrapper_name, "test_samp",
                                               stdout=os.path.join(self.rw1.run_parms['work_dir'], 'samtools_view.log'),
                                               **dict(self.rw1.base_kwargs))

    def test_samtools_wrapper(self):
        print "\n***** Testing samtobam_wrapper command *****\n"
        print self.samtobam_test.run_command

        # print "\n***** Testing samtobam_wrapper *****\n"
        # for k, v in self.samtobam_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"

class TestSamtoolsSort(unittest.TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = rsw(self.parmsfile)
        self.rw1.set_base_kwargs()
        self.rw1.parse_prog_info()
        self.wrapper_name = 'samtools'
        self.samtoolssort_test = wr.SamToolsSort(self.wrapper_name, "test_samp",
                                                 stdout=os.path.join(self.rw1.run_parms['work_dir'],
                                                                     'samtools_sort.log'),
                                                 **dict(self.rw1.base_kwargs))

    def test_samtools_wrapper(self):
        print "\n***** Testing samtoolsort_wrapper command *****\n"
        print self.samtoolssort_test.run_command

        # print "\n***** Testing samtoolsort_wrapper *****\n"
        # for k, v in self.samtoolssort_test.__dict__.iteritems():
        #     print k + ": " + str(v) +  "\n"

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
