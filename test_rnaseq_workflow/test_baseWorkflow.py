from unittest import TestCase
import unittest,saga
from definedworkflows.rnaseq.rnaseqworkflow import BaseWorkflow as bwf

class TestBaseWorkflow(TestCase):

    def setUp(self):
        self.parmsfile = "/Users/aragaven/PycharmProjects/biobrewlite/tests/test_rnaseq_workflow/test_run.yaml"
        self.rw1 = bwf(self.parmsfile)

    def test_parse_config(self):
        self.rw1.parse_config(self.parmsfile)

        for k,v in self.rw1.__dict__.iteritems():
            print k,v

        return

    # def test_create_catalog(self):
    #     self.rw1.create_catalog()
    #     print "\n============================\n"
    #     print CatalogMain.__table__
    #     for t in cb.Base.metadata.sorted_tables:
    #         print "Table name: ", t.name
    #         for column in t.columns:
    #             print "\tColumn(name , type): %s\t%s " %(column.name, column.type)
    #     return

if __name__ == '__main__':
    unittest.main()