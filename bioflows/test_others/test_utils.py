import unittest, os, sys
import bioutils.convert_bam_to_fastq as cbf


class TestConverter(unittest.TestCase):

    def setUp(self):
        self.convert_parms = dict()
        self.convert_parms['bamlist'] = "/gpfs/data/cbc/rob_reenan/analysis/sample_bams.txt"


    def test_picard_converter(self):
        print "\n***** Testing  the picard bamToFastq converter *****\n"
        self.convert_parms['converter'] = 'picard'
        self.convert_parms['output'] = "/gpfs/data/cbc/rob_reenan/analysis/picard_fastqs"
        cbf.bamtofastq(self.convert_parms)

    def test_biobambam_converter(self):
        print "\n***** Testing  the biobambam bamToFastq converter *****\n"
        self.convert_parms['converter'] = 'biobambam'
        self.convert_parms['output'] = "/gpfs/data/cbc/rob_reenan/analysis/biobambam_fastqs"
        cbf.bamtofastq(self.convert_parms)

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestConverter("test_picard_converter"))
    suite.addTest(TestConverter("test_biobambam_converter"))
    runner = unittest.TextTestRunner()
    runner.run(suite)