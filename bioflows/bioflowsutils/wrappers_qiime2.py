# import copy
import hashlib
import os
# import subprocess
import sys

from wrappers import BaseWrapper


# from itertools import chain
# import config
# import diagnostics
# import utils

class Qiime2(BaseWrapper):
    '''
    Wrapper class for the samtools command
    '''
    stdout_as_output = False

    def __init__(self, name, input, *args, **kwargs):
        self.reset_add_args()
        self.input = input
        self.make_target(name, input, *args, **kwargs)
        kwargs['target'] = self.target
        kwargs['stdout'] = os.path.join(kwargs['log_dir'], input + "_" + name + '.log')
        kwargs['prog_id'] = name
        name = self.prog_name_clean(name)

        new_name = ' '.join(name.split("_"))
        self.init(new_name, **kwargs)

        if kwargs.get('job_parms_type') != 'default':
            self.job_parms.update(kwargs.get('add_job_parms'))

            # add threading
            # if name.split('_')[1] == "sort":
            #     if 'ncpus' in kwargs.get('add_job_parms').keys():
            #         # TODO make sure threads are not given in the args
            #         self.args += [' -@ ' + str(kwargs.get('add_job_parms')['ncpus'])]
            #         if 'mem' in kwargs.get('add_job_parms').keys() and name.split('_')[1] == "sort":
            #             # TODO make sure threads are not given in the args
            #             mem_per_thread = int(kwargs.get('add_job_parms')['mem'] / kwargs.get('add_job_parms')['ncpus'])
            #             self.args += [' -m ' + str(mem_per_thread) + "M"]
            #         else:
            #             mem_per_thread = int(kwargs.get('job_parms')['mem'] / kwargs.get('add_job_parms')['ncpus'])
            #             self.args += [' -m ' + str(mem_per_thread) + "M"]
        else:
            self.job_parms.update({'mem': 4000, 'time': 300, 'ncpus': 1})
        # print self.add_args
        self.args += self.add_args
        self.setup_run()
        return

    def make_target(self, name, input, *args, **kwargs):

        if name.split('_')[1] == "tools":
            sub_option = name.split('_')[2]
            if sub_option == "import":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_tools(sub_option, *args, **kwargs)

        if name.split('_')[1] == "demux":
            sub_option = name.split('_')[2]
            if sub_option == "emp-single":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_demux(sub_option, *args, **kwargs)
            elif sub_option == "emp-paired":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_demux(sub_option, *args, **kwargs)
            elif sub_option == "summarize":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_demux(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime Demux plugin"
                sys.exit(0)

        if name.split('_')[1] == "dada2":
            sub_option = name.split('_')[2]
            if sub_option == "denoise-paired":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_dada2(sub_option, *args, **kwargs)
            elif sub_option == "denoise-pyro":
                print " this subcommand is not implemented for the qiime dada2 plugin"
                sys.exit(0)
            elif sub_option == "denoise-single":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_dada2(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime dada2 plugin"
                sys.exit(0)

        if name.split('_')[1] == "metadata":
            sub_option = name.split('_')[2]
            if sub_option == "tabulate":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_metadata(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime metadata plugin"
                sys.exit(0)

        if name.split('_')[1] == "phylogeny":
            sub_option = name.split('_')[2]
            if sub_option == "align-to-tree-mafft-fasttree":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_phylogeny(input, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime phylogeny plugin"
                sys.exit(0)

        if name.split('_')[1] == "feature-table":
            sub_option = name.split('_')[2]
            if sub_option == "summarize":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_feature_table(sub_option, *args, **kwargs)
            elif sub_option == "tabulate-seqs":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_feature_table(sub_option, *args, **kwargs)
            elif sub_option == "filter-samples":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_feature_table(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime feature-table plugin"
                sys.exit(0)

        if name.split('_')[1] == "diversity":
            sub_option = name.split('_')[2]
            if sub_option == "core-metrics-phylogenetic":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_diversity(sub_option, *args, **kwargs)
            elif sub_option == "alpha-group-significance":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_diversity(sub_option, *args, **kwargs)
            elif sub_option == "beta-group-significance":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_diversity(sub_option, *args, **kwargs)
            elif sub_option == "alpha-rarefaction":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_diversity(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime diversity plugin"
                sys.exit(0)
        if name.split('_')[1] == "emperor":
            sub_option = name.split('_')[2]
            if sub_option == "plot":
                self.target = input + "_" + name + "_" + hashlib.sha224(
                    input + "_" + name).hexdigest() + ".txt"
                self.add_args_emperor(sub_option, *args, **kwargs)
            else:
                print "Error !!! unknown subcommand used for the Qiime emperor plugin"
                sys.exit(0)

        return

    def update_qiime_args(self, default_args, *args, **kwargs):
        tmp_args = []
        tmp_args += args
        args_list = [y for x in args for y in x.split()]

        for k, v in default_args.iteritems():
            if k not in args_list:
                self.add_args += [' '.join([k, os.path.join(kwargs['qiime_dir'], v)])]
            elif '--i-' in k or '--o-' in k or '-file' in k:
                k_pos = [i for i, s in enumerate(args) if k in s][0]
                print "Printing"
                print tmp_args[k_pos]
                tmp_args[k_pos] = tmp_args[k_pos].replace(v, os.path.join(kwargs['qiime_dir'], v))
                print tmp_args[k_pos]
            else:
                pass

        return tmp_args

    def add_args_tools(self, sub_option, *args, **kwargs):
        default_args = dict()

        if sub_option == "import":
            default_args = {'--type': 'EMPPairedEndSequences',
                            '--input-path': 'emp-paired-end-sequences',
                            '--output-path': 'emp-paired-end-sequences.qza'}
        else:
            pass
        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_demux(self, sub_option, *args, **kwargs):
        default_args = dict()

        if sub_option == "emp-paired":
            default_args = {'--m-barcodes-file': 'sample-metadata.tsv',
                            '--m-barcodes-column': 'BarcodeSequence',
                            '--i-seqs': 'emp-paired-end-sequences.qza',
                            '--o-per-sample-sequences': 'demux.qza',
                            '--p-rev-comp-mapping-barcodes': ''}

        elif sub_option == 'emp-single':
            default_args = {'--i-seqs': 'emp-single-end-sequences.qza',
                            '--m-barcodes-file': 'sample-metadata.tsv',
                            '--m-barcodes-column': 'BarcodeSequence',
                            '--o-per-sample-sequences': 'demux.qza'}

        elif sub_option == "summarize":
            default_args = {'--i-data': 'demux.qza',
                            '--o-visualization': 'demux.qzv'}
        else:
            pass

        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_dada2(self, sub_option, *args, **kwargs):
        default_args = dict()
        if sub_option == "denoise-single":
            default_args = {'--i-demultiplexed-seqs':
                                'demux.qza',
                            '--p-trim-left':
                                '0',
                            '--p-trunc-len':
                                '120',
                            '--o-representative-sequences':
                                'rep-seqs-dada2.qza',
                            '--o-table':
                                'table-dada2.qza',
                            '--o-denoising-stats':
                                'stats-dada2.qza'}
        elif sub_option == "denoise-paired":
            default_args = {'--p-n-threads': 2,
                            '--i-demultiplexed-seqs': 'demux.qza',
                            '--p-trim-left-f': 13,
                            '--p-trim-left-r': 13,
                            '--p-trunc-len-f': 150,
                            '--p-trunc-len-r': 150,
                            '--o-table': 'table.qza',
                            '--o-representative-sequences': 'rep-seqs.qza',
                            '--o-denoising-stats': 'denoising-stats.qza'}
        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_metadata(self, sub_option, *args, **kwargs):
        default_args = dict()
        if sub_option == "tabulate":
            default_args = {'--m-input-file': 'stats-dada2.qza',
                            '--o-visualization': 'stats-dada2.qzv'}
        else:
            pass
        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_phylogeny(self, sub_option, *args, **kwargs):
        default_args = dict()

        if sub_option == "align-to-tree-mafft-fasttree":
            default_args = {'  --i-sequences': 'rep-seqs.qza',
                            '--o-alignment': 'aligned-rep-seqs.qza',
                            '--o-masked-alignment': 'masked-aligned-rep-seqs.qza',
                            '--o-tree': 'unrooted-tree.qza',
                            '--o-rooted-tree': 'rooted-tree.qza'}
        else:
            pass

        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_feature_table(self, sub_option, *args, **kwargs):
        default_args = dict()
        if sub_option == 'summarize':
            default_args = {'--i-table': 'table.qza',
                            '--o-visualization': 'table.qzv',
                            '--m-sample-metadata-file': "sample-metadata.tsv"}

        elif sub_option == "tabulate-seqs":
            default_args = {'--i-data': 'rep-seqs.qza',
                            '--o-visualization': 'rep-seqs.qzv'}
        elif sub_option == 'filter-samples':
            default_args = {'--i-table': 'table.qza', '--m-metadata-file': 'sample-metadata.tsv',
                            '--p-where': "BodySite='gut'", '--o-filtered-table': 'gut-table.qza'}
        else:
            print "Error!!! Unknown suboption"
            sys.exit(0)

        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_diversity(self, sub_option, *args, **kwargs):
        default_args = dict()
        if sub_option == 'core-metrics-phylogenetic':
            default_args = {'--i-phylogeny': 'rooted-tree.qza',
                            '--i-table': 'table.qza',
                            '--p-sampling-depth': 1109,
                            '--m-metadata-file': 'sample-metadata.tsv',
                            '--output-dir': 'core-metrics-results'}

        elif sub_option == "alpha-group-significance":
            default_args = {'--i-alpha-diversity': 'core-metrics-results/faith_pd_vector.qza',
                            '--m-metadata-file': 'sample-metadata.tsv',
                            '--o-visualization': 'core-metrics-results/faith-pd-group-significance.qzv'}

        elif sub_option == 'beta-group-significance':
            default_args = {'--i-distance-matrix': 'core-metrics-results/unweighted_unifrac_distance_matrix.qza',
                            '--m-metadata-file': 'sample-metadata.tsv',
                            '--m-metadata-column': 'BodySite',
                            '--o-visualization': 'core-metrics-results/unweighted-unifrac-body-site-significance.qzv',
                            '--p-pairwise': ''}
        elif sub_option == 'alpha-rarefaction':
            default_args = {'--i-table': 'table.qza',
                            '--i-phylogeny': 'rooted-tree.qza',
                            '--p-max-depth': 4000,
                            '--m-metadata-file': 'sample-metadata.tsv',
                            '--o-visualization': 'alpha-rarefaction.qzv'}
        else:
            print "Error!!! Unknown suboption"
            sys.exit(0)

        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return

    def add_args_emperor(self, sub_option, *args, **kwargs):
        default_args = dict()
        if sub_option == 'plot':
            default_args = {'--i-pcoa': 'core-metrics-results/unweighted_unifrac_pcoa_results.qza',
                            '--m-metadata-file': 'sample-metadata.tsv',
                            '--p-custom-axes': 'DaysSinceExperimentStart'}
            default_args['--o-visualization'] = ''.join(
                [default_args['--i-pcoa'].strip('_pcoa_results.qza').replace('_', '-'),
                 '-emperor-',
                 default_args['--p-custom-axes'], '.qzv'])
        updated_args = self.update_qiime_args(default_args, *args, **kwargs)
        self.add_args += updated_args
        return
