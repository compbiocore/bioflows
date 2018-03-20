#!/usr/bin/env python
#
# BioLite - Tools for processing gene sequence data and automating workflows
# Copyright (c) 2012-2014 Brown University. All rights reserved.
#
# This file is part of BioLite.
#
# BioLite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BioLite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioLite.  If not, see <http://www.gnu.org/licenses/>.

import copy

from Bio import Entrez
from lxml import etree

from bioflows.bioflowsutils import utils


class SraUtils:
    Entrez.email = None  # Need to set the Entrez.email

    # Entrez.email = "ashok.ragavendran@gmail.com"
    sra_records = dict()
    downloaded_xmls = ''
    accession_record_ids = []
    sample_to_file = dict()
    sample_to_name = dict()

    def __init__(self, sra_info):
        """
        Inititate the class with a dictionary containing necessary elements to query sra
        :param sra_info: A dict containing the the following keys entrez_email and ids
        """
        Entrez.email = sra_info['entrez_email']
        self.check_email()
        self.all_ids(sra_info['id'])
        print self.accession_record_ids
        self.download_xmls(self.accession_record_ids)
        self.get_sra_records()
        self.write_records(sra_info['outfile'])
        return

    def check_email(self):
        """
        Check if the `email` field, required for Entrez queries, has been set.
        """
        if Entrez.email is None:
            utils.die("""to make an Entrez query, you must either:
     1) set the field 'Entrez.email' manually
     2) set the 'email' resource in your BioLite configuration file""")

    def ftp_url(self, id):
        """
        Returns the URL for downloading the data for accession `id` from SRA's
        FTP server.
        """

        return 'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/{0}/{1}/{2}/{2}.sra'.format(id[:3],
                                                                                                             id[:6],
                                                                                                             id)

    def all_ids(self, id, db='sra'):
        """
        Queries SRA via Entrez and returns all accession IDs associated with the
        given accession `id`.
        """
        if type(id)== list:
            for i in id:
                handle = Entrez.esearch(db=db, RetMax=1000, term=i)
                record = Entrez.read(handle)
                self.accession_record_ids += record['IdList']
        else:
            handle = Entrez.esearch(db=db, RetMax=1000, term=id)
            record = Entrez.read(handle)
            self.accession_record_ids = record['IdList']
        return

    def download_xmls(self, ids, db='sra'):
        """
        Returns a list of XML files for the given list of SRA accession `ids`.
        """
        self.downloaded_xmls = [Entrez.efetch(db=db, id=i) for i in ids]
        return

    def get_sra_records(self):
        """
        Populates a dict with all ids and their metadata retrieved from SRA
        :param id: An SRA project id
        :return:
        """
        counter = 1
        for xml in self.downloaded_xmls:
            # x = etree.parse(xml)
            # print etree.tostring(x, pretty_print = True)
            test_record = Sra_Element(xml)
            key_url = test_record.record['paths'][0]
            key_name = test_record.record['sample_primary_id'] + "_" + test_record.record['experiment_id']
            test_record.record['manifest_name'] = key_name
            if 'sample_name' in test_record.record.keys():
                self.sample_to_name[key_name] = test_record.record['sample_name']
            else:
                #self.sample_to_name[test_record.record['sample_primary_id']] = "Unknown_" + str(counter)
                self.sample_to_name[key_name] = test_record.record['sample_primary_id']

            #self.sample_to_file[test_record.record['sample_primary_id']] = [self.ftp_url(key_url)]
            self.sample_to_file[key_name] = [self.ftp_url(key_url)]
            self.sra_records[key_url] = copy.deepcopy(test_record.record)

            if len(test_record.record['paths']) > 1:
                for i in xrange(1,len(test_record.record['paths'])):
                    key_url = test_record.record['paths'][i]
                    #self.sample_to_file[test_record.record['sample_primary_id']].append(self.ftp_url(key_url))
                    self.sample_to_file[key_name].append(self.ftp_url(key_url))
                    self.sra_records[key_url] = copy.deepcopy(test_record.record)

        #Pretty Print XML
        # print etree.tostring(test_record.package, pretty_print=True)
        #
        # for key, val in self.sra_records.iteritems():
        #     print key, ":"
        #     for k,v in val.iteritems():
        #         print '\t',k,":",v,'\n'
        #     print self.ftp_url(key), "\n"

        if 'SINGLE' in self.sra_records[key_url]['library_type']:
            print "SE library\n"
        elif 'PAIRED' in self.sra_records[key_url]['library_type']:
            print "PE library\n"

        for key, val in self.sample_to_file.iteritems():
            print key, ": ", val, "\n"
        "\nPrinting Sample to Name\n"
        for key, val in self.sample_to_name.iteritems():
            print key, ": ", val, "\n"
        return

    def write_records(self, outfile):
        if outfile is not None:
            f= open(outfile,'w')
            for k,v in self.sra_records.iteritems():
                f.write(k + "," + ','.join([k1 + ":" + self.check_str(v1) for k1, v1 in v.iteritems()]) +"\n")
            f.close()

        # for k, v in self.sra_records.iteritems():
        #     print k,v

        return

    def check_str(self, val):
        out = ''
        if type(val) == list:
            out = ';'.join([v.encode("utf-8") for v in val])
        else:
            out = val.encode("utf-8")
        return out

class Sra_Element:
    record = dict()
    package = ''

    def __init__(self, xml):
        self.xml_metadata(xml)
        return

    def get_text(self, key, base, path):
        ''''
        Helper function for retrieving text values if they exist from parsed XML.
        '''
        result = self.package.xpath(base + path)
        if len(result):
            self.record[key] = result[0].text

    def xml_metadata(self, xml):
        """
        Returns a dict populated with the metadata from an SRA EXPERIMENT_PACKAGE
        `xml` file location, with fields matching those of the BioLite catalog. The
        `paths` entry contains a list of run accessions that need to be converted
        to URLs for downloading.
        The attributes collected are:

        library_type 	GENOMIC
        paths 			['SRR353664']
        ncbi_id 		3702
        library_id 		SRR353664
        sample_prep 	None
        id 				SRX101463
        note: 			Columbia (Col-0)
        sequencer 		Illumina HiSeq 2000
        seq_center 		Center for Genomic Regulation (CRG)
        species 		Arabidopsis thaliana

        """
        parser = etree.XMLParser(remove_blank_text=True)
        self.package = etree.parse(xml, parser)
        #print(etree.tostring(self.package, pretty_print=True))

        base = '//EXPERIMENT_PACKAGE_SET/EXPERIMENT_PACKAGE'
        # Parse the sample attributes first, in case a key is defined that
        # conflicts with a catalog field name.
        for attr in self.package.xpath(base + '/SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE'):
            children = attr.getchildren()
            self.record[children[0].text] = children[1].text

        # These should always be present.
        self.record['experiment_id'] = self.package.xpath(base + '/EXPERIMENT/@accession')[0]
        run_ids = self.package.xpath(base + '/RUN_SET/RUN/@accession')
        try:
            self.record['run_file_sz'] = self.package.xpath(base + '/RUN_SET/RUN/Run/@size')[0]
        except:
            self.record['run_file_sz'] = "Nan"
            self.record['run_num_seq'] = self.package.xpath(base + '/RUN_SET/RUN/Run/@spot_count')
            self.record['paths'] = run_ids
            self.record['library_id'] = '|'.join(run_ids)

        self.record['library_type'] = ','.join([etree.tostring(x)
                                                for x in self.package.xpath(
                base + '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_LAYOUT')[0]])

        # Find other fields for populating the BioLite catalog.
        self.get_text('sample_primary_id', base, '/EXPERIMENT/DESIGN/SAMPLE_DESCRIPTOR/IDENTIFIERS/PRIMARY_ID')
        #self.get_text('sample_primary_id', base, '/SAMPLE/IDENTIFIERS/PRIMARY_ID')
        self.get_text('species', base, '/SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME')
        self.get_text('ncbi_id', base, '/SAMPLE/SAMPLE_NAME/TAXON_ID')
        self.get_text('library_source', base, '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SOURCE')
        self.get_text('library_strategy', base, '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY')
        self.get_text('library_selection', base, '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SELECTION')
        self.get_text('sequencer', base, '/EXPERIMENT/PLATFORM/ILLUMINA/INSTRUMENT_MODEL')
        # seq_center = package.xpath(base + '/RUN_SET/RUN/@run_center')
        # if seq_center: record['seq_center'] = seq_center[0]
        self.record['seq_center'] = self.package.xpath(base + '/RUN_SET/RUN/@run_center')

        self.get_text('note', base, '/SAMPLE/DESCRIPTION')
        if self.record.get('note', 'None') == 'None': self.record['note'] = None

        self.get_text('sample_prep', base, '/EXPERIMENT/DESIGN/DESIGN_DESCRIPTION')
        self.get_text('sample_name', base, '/EXPERIMENT/DESIGN/DESIGN_DESCRIPTION/SAMPLE_DESCRIPTOR/IDENTIFIERS/SUBMITTER_ID')
        #self.record['sample_name'] = self.package.xpath(base + '/SAMPLE/IDENTIFIERS/SUBNITTER_ID')
        #self.get_sample_name(base)

        return

    def get_sample_name(self, base):
        '''
        Need to build tbis function which will find the appropriate Sample Name based on the Sample ID
        :return:
        '''
        if  self.record['sample_name'] != '' :
            return
        return

# Test
if __name__ == '__main__':
    # ids = all_ids('SRP008975')
    # SraUtils({'id':'SRS1283645', 'entrez_email':'ashok.ragavendran@gmail.com'})
    #SraUtils({'id': 'ERS1051222', 'entrez_email': 'ashok.ragavendran@gmail.com'})
    #SraUtils({'id': 'SRP072326', 'entrez_email': 'ashok.ragavendran@gmail.com'})
    SraUtils({'id': ["SRX040903","SRX040904","SRX040905","SRX040906","SRX040907","SRX040908","SRX041958",
                     "SRX041959","SRX041961","SRX041962","SRX041963","SRX041964","SRX041965","SRX041966",
                     "SRX041968","SRX041969","SRX041970","SRX041971","SRX041972","SRX041973","SRX041974",
                     "SRX041975","SRX041976","SRX041977","SRX041978","SRX041979","SRX041980","SRX041981",
                     "SRX041982","SRX041983","SRX043720","SRX043721","SRX043722","SRX043723","SRX043724",
                     "SRX655426","SRX655464", "SRX655475"],
                    'entrez_email': 'ashok.ragavendran@gmail.com','outfile':'/Users/aragaven/temp.csv'})