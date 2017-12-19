import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd
from Bio import Entrez
import numpy as np
from biobrewliteutils import utils


class sramethods:
    email = "ashok.ragavendran@gmail.com"

    def __init__(self):
        self.check_email()
        self.id = 'SRP069872'

        return

    def check_email(self):
        """
        Check if the `email` field, required for Entrez queries, has been set.
        """
        if self.email is None:
            utils.die("""to make an Entrez query, you must either:
     1) set the field 'Entrez.email' manually
     2) set the 'email' resource in your BioLite configuration file""")
        return

    def all_ids(self, id, db='sra'):
        """
        Queries SRA via Entrez and returns all accession IDs associated with the
        given accession `id`.
        """
        self.check_email()
        handle = Entrez.esearch(db=db, MaxRet=1000, term=id)
        record = Entrez.read(handle)
        return record['IdList']

    def get_entrez_query(self):
        Entrez.email = self.email
        paramEutils = {'usehistory': 'Y'}

        handle = Entrez.esearch(db="sra",
                                term='((((("library selection polya"[Properties]) AND "strategy rna seq"[Properties])) AND "transcriptomic"[Source]) AND "type rnaseq"[Filter]) AND "single"[Layout] ',
                                usehistory="Y")

        res = Entrez.read(handle, validate=False)
        return res

    def printRecur(self, root, level=0):
        """Recursively prints the tree."""

        level = level + 1
        print 'level%s:: %s: %s' % (str(level), root.tag.title(),
                                    root.attrib.get('name', root.text))
        for elem in root.getchildren():
            self.printRecur(elem, level)
        return

    def xml2df(self, xml_data):
        """
        Convert XML output from web retrieved XML document into a pandas dataframe
        :param xml_data: An XML document as string
        :return: A tuple (pandas dataframe, dict)

        """
        # tree = ET.parse(xml_data) #Initiates the tree Ex: <user-agents>

        root = etree.XML(xml_data)  # Starts the root of the tree Ex: <user-agent>
        base = "./"
        samp_attr = {}
        i = 1
        headers = []
        first = True
        all_records = []

        for package in root:
            record_elem = {}
            samp_attr_elem = {}
            for attr in package.xpath(base + '/SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE'):
                children = attr.getchildren()
                try:
                    samp_attr_elem[children[0].text] = children[1].text
                except:
                    samp_attr_elem[children[0].text] = None

            run_ids = package.xpath(base + '/RUN_SET/RUN/@accession')[0]

            def get_text(key, path):
                result = package.xpath(base + path)
                if len(result):
                    record_elem[key] = result[0].text

            # Find other fields for populating the BioLite catalog.
            get_text('species', '/SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME')
            get_text('ncbi_id', '/SAMPLE/SAMPLE_NAME/TAXON_ID')
            get_text('library_source', '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SOURCE')
            get_text('library_strategy', '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY')
            get_text('library_selection', '/EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SELECTION')
            get_text('sequencer', '/EXPERIMENT/PLATFORM/ILLUMINA/INSTRUMENT_MODEL')
            try:
                record_elem['run_file_sz'] = package.xpath(base + '/RUN_SET/RUN/Run/@size')[0]
            except:
                record_elem['run_file_sz'] = np.nan
            try:
                record_elem['run_num_seq'] = package.xpath(base + '/RUN_SET/RUN/Run/@spot_count')[0]
            except:
                record_elem['run_num_seq'] = np.nan
            record_elem['paths'] = run_ids
            record_elem['experiment_id'] = package.xpath(base + '/EXPERIMENT/@accession')[0]
            record_elem['seq_center'] = package.xpath(base + '/RUN_SET/RUN/@run_center')
            if first:
                for k in record_elem.keys():
                    headers.append(k)
                first = False
            samp_attr[run_ids] = samp_attr_elem
            all_records.append([v for v in record_elem.values()])  # Append this record to all_records.

        return (pd.DataFrame(all_records, columns=headers),
                samp_attr)  # Finally, return our Pandas dataframe with headers in the column.
