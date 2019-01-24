#  RNAseq with GSNAP
## Overview

This tutorial shows how to run a standard predefined RNA-seq analysis on
the Brown HPC cluster OSCAR, using the bioflows tool.

## Getting Started
#### The workflow consists of the following steps:

-  **Fastqc**: For QC of Raw Fastq reads
-  **GSNAP** alignment of the reads to the reference genome of the reads
-  **Qualimap** tool for the QC of the aligments generated
-  **featureCounts** tool for quantifying expression based on mapped reads
-  **Salmon** tool for alignment free quantification of known transcripts

#### The basic steps to running a workflow are:

1. [Create a control file](#Setup the YAML configuration file)
2. Create your working directory if does not exist, here we assume it is `/users/username`.
3. [Setup a screen session](#/docs/tutorials/Setup_bioflows_env/#Setup GNU screen session)

### Prerequisites
Make sure you have access to the OSCAR cluster or request one by contacting support@ccv.brown.edu. If you are not comfortable with the Linux environment, you can consult the tutorial [here.](https://compbiocore.github.io/cbc-linux-tutorial/linux_explication/) You should also [set up bioflows.](#/docs/tutorials/Setup_bioflows_env)

The next section provide a short how-to with all the commands to
execute the test workflow on Brown University's CCV cluster.

!!! caution
    The working directory in a real example can end up being quite large: up to a few terabytes. On OSCAR, you would create the working directory in a location such as your `data` folder or the `scratch` folder.

#### Setup the YAML configuration file (control file)

Bioflows uses YAML configuration files. A
detailed documentation of the YAML file and all the options is shown
[here](#/docs/yaml_description.md). For the current example, copy the following code into a text file and save it in `/users/username` as `test_run.yaml`.

!!! note
    Don't forget to edit the work_dir parameter to reflect the path to your own working directory.

```
bioproject: Project_test_localhost
experiment: rnaseq_pilot
sample_manifest:
  fastq_file: sampl_manifest_min.csv
  metadata:
run_parms:
  conda_command: source /gpfs/runtime/cbc_conda/bin/activate_cbc_conda
  work_dir: */users/username*
  log_dir: logs
  paired_end: True
  local_targets: False
  saga_host: localhost
  ssh_user: *ccv username*
  saga_scheduler: slurm
  gtf_file: /gpfs/data/cbc/cbcollab/ref_tools/Ensembl_hg_GRCh37_rel87/Homo_sapiens.GRCh37.87.gtf
workflow_sequence:
  - fastqc: default
  - gsnap:
      options:
       -d: Ensembl_Homo_sapiens_GRCh37
       -s: /gpfs/data/cbc/cbcollab/cbc_ref/gmapdb_2017.01.14/Ensembl_Homo_sapiens_GRCh37/Ensembl_Homo_sapiens_GRCh37.maps/Ensembl_Homo_sapiens.GRCh37.87.splicesites.iit
      job_params:
        ncpus: 8
        mem: 40000
        time: 60
  - qualimap_rnaseq: default
  - htseq-count: default

```

### Submit the workflow

If you haven't done so already, copy the above into a text file and save it in `/users/username` as `test_run.yaml`

For this tutorial I have created a small test dataset with 10000 read pairs from human RNAseq data, so it should run within the hour and you should see that the alignments are completed.

We will now create the sample manifest file, which is in `csv` format. You can find more information about sample manifest files [here](#/docs/yaml_description.md). Copy the manifest below into a text file and save it in `/users/username` as `sample_manifest_min.csv`

```
samp_1299,/gpfs/data/cbc/rnaseq_test_data/PE_hg/Cb2_1.gz,/gpfs/data/cbc/rnaseq_test_data/PE_hg/Cb2_2.gz
samp_1214,/gpfs/data/cbc/rnaseq_test_data/PE_hg/Cb_1.gz,/gpfs/data/cbc/rnaseq_test_data/PE_hg/Cb_2.gz
```

If you haven't already started a screen session in the [setup](#/docs/tutorials/Setup_bioflows_env), start one using the following command:
```
screen -S rnaseq_tutorial
```
In your screen session, run the following commands to setup your conda environment (if you have not done so previously during the [setup](#/docs/tutorials/Setup_bioflows_env) or if you just started a new screen session).

```
source activate_cbc_conda
bioflows-rnaseq test_run.yaml
```
