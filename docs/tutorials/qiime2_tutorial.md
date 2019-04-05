# QIIME2

## Overview

This tutorial shows how to run a standard predefined QIIME2 analysis on the Brown HPC cluster OSCAR, using the bioflows tool. The particular analysis is the first half of the [Moving pictures tutorial](https://docs.qiime2.org/2019.1/tutorials/moving-pictures/) from QIIME2.

We will assume that you have run through the [RNA-Seq tutorial](#/docs/tutorials/rna-seq_tutorial) and know how to set up a control file, create a working directory, and setup a screen session as well as have the prerequisites set up. The following is more details specific to the workflow and YAML setup.

## Getting Started

#### The workflow consists of the following steps:

 - **qiime tools import** for importing raw amplicon sequencing data into a QIIME2 artifact
 - **qiime demux** for demultiplexing data
-  **qiime dada2** for detecting and correcting data and creating feature tables and representative sequences
-  **qiime feature-table** for summarizing and visualizing the feature table and representative sequences
-  **qiime phylogeny align-to-tree-mafft-fasttree** for multiple sequence alignment and phylogeny inference (with mafft and fasttree)
-  **qiime diversity core-metrics-phylogenetic** for computing alpha and beta diversity statistics
-  **qiime feature-classifier classify-sklearn** for taxonomic assignment
-  **qiime taxa barplot** for generating interactive taxonomy barplots
-  **qiime composition** for differential abundance testing with ANCOM

#### Setup the YAML configuration file (control file)

For the current example, copy the following code into a text file and save it in `/users/username` as `test_run.yaml`.

!!! note
    Don't forget to edit the work_dir parameter to reflect the path to your own working directory.

```
bioproject: Project_test_localhost # Project Name  Required
experiment: rnaseq_pilot # Experiment type  Required
sample_manifest:
  qiime:
    --type: EMPSingleEndSequences
    --input-path: emp-single-end-sequences
    --output-path: emp-single-end-sequences.qza
    --m-barcodes-file: sample-metadata.tsv
    #--output-suffix: test1
run_parms:
  conda_command: source /gpfs/runtime/cbc_conda/bin/activate_cbc_conda; conda activate qiime2-2019.1
  work_dir: */users/username*
  log_dir: logs
  paired_end: True
  local_targets: False
  saga_host: localhost
  ssh_user: *ccv username*
  saga_scheduler: slurm
  reference_fasta_path: /gpfs/scratch/test.fa
  gtf_file: /gpfs/scratch/aragaven/lapierre/caenorhabditis_elegans.PRJNA13758.WBPS8.canonical_geneset.gtf
workflow_sequence:
- qiime:
    subcommand: "demux emp-single"
    options:
      --i-seqs: emp-single-end-sequences.qza
      --m-barcodes-file: sample-metadata.tsv
      --m-barcodes-column: BarcodeSequence
      --o-per-sample-sequences: demux.qza
- qiime:
    subcommand: demux summarize
    options:
      --i-data: demux.qza
      --o-visualization: demux.qzv
- qiime:
    subcommand: "dada2 denoise-single"
    options:
      --i-demultiplexed-seqs: demux.qza
      --p-trim-left: 0
      --p-trunc-len: 120
      --o-representative-sequences: rep-seqs-dada2.qza
      --o-table: table-dada2.qza
      --o-denoising-stats: stats-dada2.qza

- qiime:
    subcommand: metadata tabulate
    options:
      --m-input-file: stats-dada2.qza
      --o-visualization: stats-dada2.qzv

- qiime:
    subcommand: feature-table summarize
    options:
      --i-table: table.qza
      --o-visualization: table.qzv
      --m-sample-metadata-file: sample-metadata.tsv
- qiime:
    subcommands: feature-table tabulate-seqs
    options:
      --i-data rep-seqs.qza
      --o-visualization rep-seqs.qzv
- qiime:
    subcommand: phylogeny align-to-tree-mafft-fasttree
    options:
      --p-n-threads: 2
      --i-sequences: rep-seqs.qza
      --o-alignment: aligned-rep-seqs.qza
      --o-masked-alignment: masked-aligned-rep-seqs.qza
      --o-tree: unrooted-tree.qza
      --o-rooted-tree: rooted-tree.qza
```

### Submit the workflow

If you haven't done so already, copy the above into a text file and save it in `/users/username` as `test_run.yaml`. The data here is the same as from the Moving pictures tutorial. Because it follows the EMP format, no manifest file is needed, but if providing other data the user will need to provide a manifest file matching the [description in QIIME2](https://docs.qiime2.org/2019.1/tutorials/importing/#fastq-manifest-formats), specified in the YAML in the same way as in the [RNA-seq tutorial](#/docs/tutorials/rna-seq_tutorial)

If you haven't already started a screen session in the [setup](#/docs/tutorials/Setup_bioflows_env), start one using the following command:
```
screen -S rnaseq_tutorial
```
In your screen session, run the following commands to setup your conda environment (if you have not done so previously during the [setup](#/docs/tutorials/Setup_bioflows_env) or if you just started a new screen session).

```
source activate_cbc_conda
bioflows-qiime2 test_run.yaml
```

(TODO: bioflows-qiime2 is not a defined wrapper...)

### Workflow outputs

The bioflows-qiime2 call will automatically generate several directories, which may or may not have any outputs directed to them depending on which analyses have been run in bioflows. These directories include: `qiime2`, `slurm_scripts`, `logs`, and `checkpoints`. (TODO: not actually sure what output gets made)

`sra` Will be empty in this tutorial.

`fastq` symlinks to fastq files.

`alignments` SAM and BAM files from GSNAP alignments.

`qc` QC reports from fastqc and qualimap.

`slurm_scripts` Records of the commands sent to slurm.

`logs` Log files from various bioflows processes (including the standard error and standard out).

`expression` Expression values from featureCounts.

`checkpoints` Contains checkpoint records to confirm that bioflows has progressed through each step of the analysis.
