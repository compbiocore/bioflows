import zipfile as zf, re

class FastqcParser:
    """
    A class for parsing and collating the output from fastqc runs
    """
    def __init__(self, file_handle):
        self.module_names = None
        self.parsed_results = None
        self.infile = file_handle
        self.module_start_stop = None
        return

    def parse_results_file(self):
        '''
        read in the results in zipfile and return parsed file and the locations of modules
        :return: list of output and tuple with location of modules
        '''
        zp = zf.ZipFile(self.infile,'r')
        results_idx= next((i for i, item in enumerate(zp.namelist()) if re.search('fastqc_data.txt', item)), None)

        # Parse results into a list
        self.parsed_results = zp.open(zp.namelist()[results_idx]).readlines()

        # Generate a tuple for the start and end locs of the modules 12 in total
        # ['>>Basic Statistics\tpass\n',
        #  '>>Per base sequence quality\tpass\n',
        #  '>>Per tile sequence quality\twarn\n',
        #  '>>Per sequence quality scores\tpass\n',
        #  '>>Per base sequence content\twarn\n',
        #  '>>Per sequence GC content\tpass\n',
        #  '>>Per base N content\tpass\n',
        #  '>>Sequence Length Distribution\tpass\n',
        #  '>>Sequence Duplication Levels\tfail\n',
        #  '>>Overrepresented sequences\twarn\n',
        #  '>>Adapter Content\tpass\n',
        #  '>>Kmer Content\tfail\n']

        module_start_idx = [i for i, item in enumerate(self.parsed_results) if re.search('^>>', item)]
        module_end_idx = [i for i, item in enumerate(self.parsed_results) if re.search('^>>END_MODULE', item)]
        module_start_idx = sorted(list(set(module_start_idx) - set(module_end_idx)))

        self.module_names = [self.parsed_results[i] for i in module_start_idx ]
        self.module_start_stop = zip(module_start_idx, module_end_idx)
        return

    def extract_seq_quals_module(self):
        loc = self.module_start_stop[1]
        self.seq_quals_data = self.parsed_results[loc[0]+1: loc[1]-1]
        seq_quals_head =self.seq_quals_data[0].strip('\n').strip('#').split('\t')
        print seq_quals_head
        return

