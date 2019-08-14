# import copy
import hashlib
import os

from wrappers import BaseWrapper


# import subprocess


# from itertools import chain
# import config
# import diagnostics
# import utils


class Picard(BaseWrapper):
    """
        A wrapper for picardtools
        picard CollectWgsMetrics \
        INPUT=$mysamplebase"_sorted.bam" \ OUTPUT=$mysamplebase"_stats_picard.txt"\
        REFERENCE_SEQUENCE=$myfasta \
        MINIMUM_MAPPING_QUALITY=20 \
        MINIMUM_BASE_QUALITY=20 \
        VALIDATION_STRINGENCY=LENIENT
    """

    def __init__(self, name, input, *args, **kwargs):
        self.input = input
        print "Printing optional arguments " + name
        print args
        # TODO add remove duprun function

        kwargs['prog_id'] = name
        # Remove the round from the name
        name = self.prog_name_clean(name)

        ## set the checkpoint target file
        new_name = ' '.join(name.split("_"))

        # kwargs['target'] = input + '._wgs_stats_picard.' + hashlib.sha224(input + '._wgs_stats_picard.txt').hexdigest() + ".txt"
        self.make_target(name, input, *args, **kwargs)

        kwargs['target'] = self.target
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            ## Update threads if cpus given
            # if 'ncpus' in kwargs.get('add_job_parms').keys():
            #     self.args += [' -t ' + str(kwargs.get('add_job_parms')['ncpus'])]

            ## Update memory requirements  if needed
            if 'mem' in kwargs.get('add_job_parms').keys():
                self.args += [' -Xmx' + str(kwargs.get('add_job_parms')['mem']) + 'M']

        else:
            # Set default memory and cpu options
            self.job_parms.update({'mem': 10000, 'time': 80, 'ncpus': 4})
            self.args += [' -Xmx10000M']

        kwargs['source'] = input + self.in_suffix + hashlib.sha224(input + self.in_suffix).hexdigest() + ".txt"
        self.args += self.add_args

        self.setup_run()
        return

    def make_target(self, name, input, *args, **kwargs):
        '''

        :param name: the name of the program including subcommand and roung
        :param input: the sample id
        :param args: the arguments passed as Program options in YAML
        :param kwargs: Generic options passed to bioflows
        :return:
        '''
        if name.split('_')[1] == "CollectWgsMetrics":
            self.update_file_suffix(input_default=".dup.srtd.bam", output_default='_wgs_stats_picard.txt', **kwargs)
            self.target = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
                input + "_" + name + "_" + self.out_suffix).hexdigest() + ".txt"
            self.add_args_collect_wgs_metrics(input, *args, **kwargs)

        elif name.split('_')[1] == "MeanQualityByCycle":
            self.update_file_suffix(input_default=".dup.srtd.bam", output_default='_read_qual_by_cycle_picard',
                                    **kwargs)
            self.target = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
                input + "_" + name + "_" + self.out_suffix + ".txt").hexdigest() + ".txt"
            self.add_args_mean_quality_by_cycle(input, *args, **kwargs)

        elif name.split('_')[1] == "QualityScoreDistribution":
            self.update_file_suffix(input_default=".dup.srtd.bam", output_default='_read_qual_overall_picard', **kwargs)
            self.target = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
                input + "_" + name + "_" + self.out_suffix + ".txt").hexdigest() + ".txt"
            self.add_args_quality_score_distribution(input, *args, **kwargs)

        elif name.split('_')[1] == "MarkDuplicates":
            self.update_file_suffix(input_default=".rg.srtd.bam", output_default=".rg.srtd.bam", **kwargs)
            self.target = input + "_" + name + "_" + 'mark_dup_picard.txt' + "_" + hashlib.sha224(
                input + "_" + name + "_" + 'mark_dup_picard.txt').hexdigest() + ".txt"
            self.add_args_markduplicates(input, *args, **kwargs)

        elif name.split('_')[1] == "AddOrReplaceReadGroups":
            self.update_file_suffix(input_default=".dup.srtd.bam", output_default=".rg.srtd.bam", **kwargs)
            self.target = input + "_" + name + "_" + self.out_suffix + "_" + hashlib.sha224(
                input + "_" + name + "_" + self.out_suffix).hexdigest() + ".txt"
            self.add_args_addorreplacereadgroups(input, *args, **kwargs)

        elif name.split('_')[1] == "BuildBamIndex":
            self.update_file_suffix(input_default=".gatk.recal.bam", output_default="", **kwargs)
            self.target = input + "_" + name + "_" + self.in_suffix + ".bai_" + hashlib.sha224(
                input + "_" + name + "_" + self.in_suffix + '.bai').hexdigest() + ".txt"

            self.add_args_buildbamindex(input, *args, **kwargs)

        elif name.split('_')[1] == "SamToFastq":
            self.update_file_suffix(input_default=".bam", output_default="fq.gz", **kwargs)
            self.target = input + "_" + name + "_" + self.in_suffix + "_" + hashlib.sha224(
                input + "_" + name + "_" + self.in_suffix).hexdigest() + ".txt"

            self.add_args_samtofastq(input, *args, **kwargs)

        elif name.split('_')[1] == "CollectHsMetrics":
            self.update_file_suffix(input_default=".dedup.rg.srtd.realigned.bam", output_default="_hs_metrics.txt",
                                    **kwargs)
            self.target = input + "_" + name + "_" + hashlib.sha224(
                input + "_" + name).hexdigest() + ".txt"
            self.add_args_collect_hs_metrics(input, *args, **kwargs)
            # TODO add tests for BAIT_INTERVALS and TARGET_INTERVALS

        elif name.split('_')[1] == "CollectAlignmentSummaryMetrics":
            self.update_file_suffix(input_default=".rg.srtd.bam", output_default="_alignment_summary_metrics.txt",
                                    **kwargs)
            self.target = input + "_" + name + "_" + hashlib.sha224(
                input + "_" + name).hexdigest() + ".txt"
            self.add_args_collect_alignment_summary_metrics(input, *args, **kwargs)

        elif name.split('_')[1] == "CollectGcBiasMetrics":
            self.update_file_suffix(input_default=".rg.srtd.bam", output_default="_gc_bias_metrics.txt", **kwargs)
            self.target = input + "_" + name + "_" + hashlib.sha224(
                input + "_" + name).hexdigest() + ".txt"
            self.add_args_collect_gcbias_metrics(input, *args, **kwargs)

        elif name.split('_')[1] == "CollectInsertSizeMetrics":
            self.update_file_suffix(input_default=".rg.srtd.bam", output_default="_insert_size_metrics.txt", **kwargs)
            self.target = input + "_" + name + "_" + hashlib.sha224(
                input + "_" + name).hexdigest() + ".txt"
            self.add_args_collect_insert_size_metrics(input, *args, **kwargs)
        return

    def add_args_collect_alignment_summary_metrics(self, input, *args, **kwargs):
        self.reset_add_args()
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path")]
        self.add_args += args
        return

    def add_args_collect_gcbias_metrics(self, input, *args, **kwargs):
        self.reset_add_args()
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix),
                         "CHART=" + os.path.join(kwargs.get('qc_dir'),
                                                 input + self.out_suffix.replace(".txt", "_plots.pdf")),
                         "SUMMARY_OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + "_summary" + self.out_suffix),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path")]
        self.add_args += args
        return

    def add_args_collect_insert_size_metrics(self, input, *args, **kwargs):
        self.reset_add_args()
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix),
                         "HISTOGRAM_FILE=" + os.path.join(kwargs.get('qc_dir'),
                                                          input + self.out_suffix.replace(".txt", "_histogram.pdf")),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path")]
        self.add_args += args
        return

    def add_args_collect_hs_metrics(self, input, *args, **kwargs):
        self.reset_add_args()
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix),
                         "PER_TARGET_COVERAGE=" + os.path.join(kwargs.get('qc_dir'),
                                                               input + self.out_suffix.replace(".txt",
                                                                                               "_per_target_cov.txt")),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path")]
        self.add_args += args
        return

    def add_args_collect_wgs_metrics(self, input, *args, **kwargs):
        self.reset_add_args()
        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                         "MINIMUM_MAPPING_QUALITY=20", "MINIMUM_BASE_QUALITY=20",
                         "COUNT_UNPAIRED=true", "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return

    def add_args_mean_quality_by_cycle(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + + self.out_suffix + '.txt'),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                         "CHART_OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix + '.pdf'),
                         "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return

    def add_args_quality_score_distribution(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix + '.txt'),
                         "REFERENCE_SEQUENCE=" + kwargs.get("ref_fasta_path"),
                         "CHART_OUTPUT=" + os.path.join(kwargs.get('qc_dir'), input + self.out_suffix + '.pdf'),
                         "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return

    def add_args_addorreplacereadgroups(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + self.out_suffix),
                         "RGID=" + input,
                         "RGLB=lib1 RGPL=illumina  RGPU=unit1 RGCN=BGI",
                         "RGSM=" + input,
                         "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return

    def add_args_markduplicates(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'), input + self.in_suffix),
                         "M=" + os.path.join(kwargs.get('qc_dir'), input + '_mark_duplicates_picard.txt'),
                         "CREATE_INDEX=true VALIDATION_STRINGENCY=LENIENT"
                         ]
        if "REMOVE_DUPLICATES=true" in args:
            # TODO add update to input/output suffixes here
            self.out_suffix = ".dedup" + self.out_suffix

            self.add_args += ["OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + self.out_suffix)]
        else:
            # TODO add update to input/output suffixes here
            self.out_suffix = ".picdup" + self.out_suffix

            self.add_args += ["OUTPUT=" + os.path.join(kwargs.get('align_dir'), input + self.out_suffix)]

        self.add_args += args
        return

    def add_args_buildbamindex(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'),
                                                 input + self.in_suffix),
                         "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return

    def add_args_samtofastq(self, input, *args, **kwargs):
        self.reset_add_args()

        self.add_args = ["INPUT=" + os.path.join(kwargs.get('align_dir'),
                                                 input + self.in_suffix),
                         "VALIDATION_STRINGENCY=LENIENT"]
        self.add_args += args
        return
