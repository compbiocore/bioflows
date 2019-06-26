# import copy
import hashlib
import os

from wrappers import BaseWrapper


# import subprocess


# from itertools import chain
# import config
# import diagnostics
# import utils


class Gatk(BaseWrapper):
    """
        A wrapper for GATK
    """

    def __init__(self, name, input, *args, **kwargs):

        self.input = input

        kwargs['prog_id'] = name
        # Remove the round from the name
        name = self.prog_name_clean(name)

        ## set the checkpoint target file

        self.make_target(name, input, *args, **kwargs)
        kwargs['target'] = self.target
        kwargs['stdout'] = self.stdout

        # We have to set name and run init so mem_str can be updated
        # from the yaml and then we re-ddo name and init a second time
        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        mem_str = ' -Xmx10000M'
        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))
            # TODO: figure how how to update threads for GATK based on CPUS?
            ## Update memory requirements  for Java
            if 'mem' in kwargs.get('add_job_parms').keys():
                # self.args += [' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M']
                mem_str = ' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M'
        else:
            # Set default memory and cpu options
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 4})

        new_name = name.split("_")

        # Adding control to make the the same wrappers usable
        # for gatk4 which does not use the '-T' delimiter for subcommands
        if name.split('_')[0] != "gatk4":
            new_name.insert(1, mem_str)
            new_name.insert(2, '-T')
        else:
            pass
        new_name = ' '.join(new_name)

        self.init(new_name, **kwargs)

        # kwargs['source'] = input + '.dedup.srtd.bam' + hashlib.sha224(input + '.dedup.rg.srtd.bam').hexdigest() + ".txt"
        # ref_fasta = kwargs.get("ref_fasta_path")
        # self.args += args

        # Note: We add all optional arguments to the end of the add_args variable

        self.args += self.add_args
        # self.args += ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + ".dup.srtd.bam"),
        #               "OUTPUT=" + os.path.join(kwargs.get('qc_dir'),input + '._wgs_stats_picard.txt'),
        #               "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
        #               "MINIMUM_MAPPING_QUALITY="+"20","MINIMUM_BASE_QUALITY="+"20",
        #               "COUNT_UNPAIRED=true", "VALIDATION_STRINGENCY="+"LENIENT"]

        self.setup_run()
        return

    def make_target(self, name, input, *args, **kwargs):
        name_str = "_" + name + "_"
        if name.split('_')[1] == "RealignerTargetCreator":
            self.update_file_suffix(input_default=".dedup.rg.srtd.bam", output_default='_realign_targets.intervals',
                                    **kwargs)
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_realigner_target_creator(input, *args, **kwargs)

        elif name.split('_')[1] == "IndelRealigner":
            self.update_file_suffix(input_default=".dedup.rg.srtd.bam", output_default='.dedup.rg.srtd.realigned.bam',
                                    **kwargs)
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_indel_realigner(input, *args, **kwargs)

        elif name.split('_')[1] == "BaseRecalibrator":

            self.update_file_suffix(input_default='.dedup.rg.srtd.realigned.bam', output_default='_recal_table.txt',
                                    **kwargs)
            if "-BQSR" in args:
                self.target = input + name_str + 'post' + self.out_suffix + "_" + hashlib.sha224(
                    input + name_str + 'post' + self.out_suffix).hexdigest() + ".txt"
            else:
                self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                    input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_base_recalibrator(input, *args, **kwargs)

        elif name.split('_')[1] == "PrintReads":
            self.update_file_suffix(input_default='.dedup.rg.srtd.realigned.bam', output_default='.gatk.recal.bam',
                                    **kwargs)
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_print_reads(input, *args, **kwargs)

        elif name.split('_')[1] == "HaplotypeCaller":
            self.update_file_suffix(input_default='.gatk.recal.bam', output_default='.GATK-HC.g.vcf', **kwargs)
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_haplotype_caller(input, *args, **kwargs)

        elif name.split('_')[1] == "VariantRecalibrator":
            # TODO Fix this
            self.target = input + name_str + 'mark_dup_picard.' + hashlib.sha224(
                input + name_str + 'mark_dup_picard.txt').hexdigest() + ".vcf"

        elif name.split('_')[1] == "AnalyzeCovariates":
            self.update_file_suffix(input_default="_recal_table.txt", output_default="_recalibration_plots.pdf",
                                    **kwargs)
            self.target = input + name_str + self.out_suffix + "_" + hashlib.sha224(
                input + name_str + self.out_suffix).hexdigest() + ".txt"
            self.add_args_analyze_covariates(input, *args, **kwargs)
        return

    def add_args_realigner_target_creator(self, input, *args, **kwargs):
        # gatk -Xmx20G -T RealignerTargetCreator -R $my.fasta -I $my.bam\
        #  -known /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf \
        # -o $samp_realign_targets.intervals
        # kwargs.get()
        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = ["-I " + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "-o " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix),
                         "-R " + kwargs.get("ref_fasta_path")]

        self.add_args += args
        # TODO Dont need the below.. Add an exception handler to make sure at least one -known is present
        # self.add_args += [
        #     "-known " + "/gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf"]

        return

    def add_args_indel_realigner(self, input, *args, **kwargs):
        # gatk - T IndelRealigner \
        # - R $myfasta \
        # - known $myindel \
        # - targetIntervals $mysamplebase"_realign_targets.intervals" \
        # - I $mysamplebase"_sorted_dedup.bam" \
        # - o $mysamplebase"_sorted_dedup_realigned.bam" \

        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = ["-I " + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "-o " + os.path.join(kwargs.get('align_dir'), input + self.out_suffix),
                         "-R " + kwargs.get("ref_fasta_path"),
                         "-targetIntervals " + os.path.join(kwargs.get('gatk_dir'),
                                                            input + '_realign_targets.intervals')
                         ]
        self.add_args += args

        return

    def add_args_base_recalibrator(self, input, *args, **kwargs):
        # gatk - T IndelRealigner \
        # - R $myfasta \
        # - known $myindel \
        # - targetIntervals $mysamplebase"_realign_targets.intervals" \
        # - I $mysamplebase"_sorted_dedup.bam" \
        # - o $mysamplebase"_sorted_dedup_realigned.bam" \

        # kwargs.get()

        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = ["-I " + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "-R " + kwargs.get("ref_fasta_path")]

        # TODO make this optional by searching *args and replacing and an exception handler to ensure at least one -knownSites is present
        # self.add_args += [" -ncgt 8"]
        # self.add_args += [
        #    "-knownSites " + "/gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/Mills_and_1000G_gold_standard.indels.hg19.sites.vcf"]
        # self.add_args += [
        #    "-knownSites " + "/gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/dbsnp_138.hg19.vcf"]
        print "Printing optional arguments"
        print args
        if "-BQSR" in args:
            self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
            new_args = list(args)
            idx_to_rm = [i for i, s in enumerate(new_args) if '-BQSR' in s][0]
            del new_args[idx_to_rm]
            self.add_args += new_args
            # self.out_suffix is used as input and the output has '_post` appended to it
            self.add_args += ["-BQSR " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)]
            if kwargs['prog_id'].split('_')[0] == "gatk4":
                self.add_args += ["-O " + os.path.join(kwargs.get('gatk_dir'), input + "_post" + self.out_suffix)]
            else:
                self.add_args += ["-o " + os.path.join(kwargs.get('gatk_dir'), input + "_post" + self.out_suffix)]
        else:
            self.add_args += args
            if kwargs['prog_id'].split('_')[0] == "gatk4":
                self.add_args += ["-O " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)]
            else:
                self.add_args += ["-o " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)]

        return

    def add_args_print_reads(self, input, *args, **kwargs):
        # gatk - Xmx30G - T PrintReads
        # -R /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/ucsc.hg19.fasta
        # -I /gpfs/data/cbc/uzun/wes_analysis/wes_run_1/gatk_all_run/WESPE2932_dedup_rg_realigned.bam
        # -BQSR /gpfs/data/cbc/uzun/wes_analysis/wes_run_1/gatk_all_run/WESPE2932_recal_table.txt
        # -o /gpfs/data/cbc/uzun/wes_analysis/wes_run_1/gatk_all_run/WESPE2932_recal_gatk.bam

        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = [
            "-I " + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
            "-R " + kwargs.get("ref_fasta_path"),
            "-BQSR " + os.path.join(kwargs.get('gatk_dir'), input + "_recal_table.txt"),
            "-o " + os.path.join(kwargs.get('align_dir'), input + self.out_suffix)
        ]
        return

    def add_args_haplotype_caller(self, input, *args, **kwargs):
        # gatk -Xmx30G -T HaplotypeCaller
        # -nct 4
        # -R /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/ucsc.hg19.fasta
        # -I /gpfs/data/cbc/uzun/wes_analysis/wes_run_1/gatk_all_run/WESPE2932_recal_gatk.bam
        # --dbsnp /gpfs/data/cbc/references/ftp.broadinstitute.org/bundle/hg19/dbsnp_138.hg19.vcf
        # -stand_call_conf 30
        # --genotyping_mode DISCOVERY
        # --emitRefConfidence GVCF
        # -o /gpfs/data/cbc/uzun/wes_analysis/wes_run_1/gatk_all_run/WESPE2932_GATK-HC.g.vcf

        # kwargs.get()

        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = ["-I " + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "-R " + kwargs.get("ref_fasta_path")]
        self.add_args += args
        if kwargs['prog_id'].split('_')[0] == "gatk4":
            self.add_args += ["-o " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)]
        else:
            self.add_args += ["-o " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)]
        return

    def add_args_analyze_covariates(self, input, *args, **kwargs):
        self.stdout = os.path.join(kwargs['log_dir'], input + "_" + kwargs['prog_id'] + '.log')
        self.reset_add_args()

        self.add_args = ["-R " + kwargs.get("ref_fasta_path"),
                         "-before " + os.path.join(kwargs.get('gatk_dir'), input + self.in_suffix),
                         "-after " + os.path.join(kwargs.get('gatk_dir'), input + "_post" + self.in_suffix),
                         "-plots " + os.path.join(kwargs.get('gatk_dir'), input + self.out_suffix)
                         ]
        return
