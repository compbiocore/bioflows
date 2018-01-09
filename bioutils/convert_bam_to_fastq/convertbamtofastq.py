import subprocess as sp, sys,

class bamtofastq:
    sample_list=dict()

    def __init__(self, convert_info):
        """
        Initilize the bam to fastq conversion using multiple tools

        :param bamlist:
        """
        self.parse_sample(convert_info['bamlist'])
        self.output_folder = convert_info['output']
        if convert_info['converter'] == 'picard':
            self.picard_converter()
        elif convert_info['converter'] == 'biobambam':
            self.biobambam_converter()

        return

    def parse_sample(self, bamlist):
        for line in open(bamlist,'r').readlines():
            tmpline = line.strip('\n').split(',')
            self.sample_list[line[0]] = line[1]
        return

    def picard_converter(self):

        f = open("bam_fastq_picard_commands.log", 'w')
        f.write("*** Convert Bam to Fastq Using Picard ***\n")

        for samp,filepath in self.sample_list.iteritems():
            cmd = " sbatch -t 05:00:00 --mem=10g -n 4 --wrap='source activate cbc_conda;"
            cmd = cmd + " picard -Xmx 10000m SamToFastq I=" + file  +  " "
            cmd = cmd + " F="  + self.output_folder + "/pic_" + samp + "_r1.fq "
            cmd = cmd + " F2=" + self.output_folder + "/pic_" + samp + "_r2.fq "
            cmd = cmd + " FU=" + self.output_folder + "/pic_" + samp + "_up.fq ;"
            cmd = cmd + " gzip " + self.output_folder + "/pic_" + samp + "_r1.fq ;"
            cmd = cmd + " gzip " + self.output_folder + "/pic_" + samp + "_r2.fq ;"
            cmd = cmd + " gzip " + self.output_folder + "/pic_" + samp + "_up.fq'"
            sp.getoutput(cmd, shell=True)
            f.write(cmd + '\n')
        f.close()

        return

    def biobambam_converter(self):
        f = open("bam_fastq_biobambam_commands.log", 'w')
        f.write("*** Convert Bam to Fastq Using BioBamBam ***\n")
        for samp,filepath in self.sample_list.iteritems():
            cmd = " sbatch -t 05:00:00 --mem=10g -n 4 --wrap='source activate cbc_conda; bamtofastq"
            cmd = cmd + " F="  + self.output_folder + "/bb_" + samp + "_r1.fq.gz "
            cmd = cmd + " F2=" + self.output_folder + "/bb_" + samp + "_r2.fq.gz "
            cmd = cmd + " O="  + self.output_folder + "/bb_" + samp + "_um_r1.fq.gz "
            cmd = cmd + " O2=" + self.output_folder + "/bb_" + samp + "_um_r2.fq.gz "
            cmd = cmd + " filename=" + filepath + " gz=1'"
            sp.getoutput(cmd, shell=True)
            f.write(cmd + '\n')
        f.close()
        return

if __name__ == '__main__':
    convert_parms = dict()
    convert_parms['converter'] = sys.argv[1]
    convert_parms['bamlist'] = sys.argv[2]
    convert_parms['output'] = sys.argv[3]
    bamtofastq(convert_parms)
