#  RNAseq with GSNAP
## Overview

This tutorial shows how to run a standard predefined RNA-seq analysis on
the Brown HPC cluster OSCAR, using the bioflows tool. The workflow
consists of the following steps:

-  **Fastqc**: For QC of Raw Fastq reads
-  **GSNAP** alignment of the reads to the reference genome of the reads
-  **Qualimap** tool for the QC of the aligments generated
-  **featureCounts** tool for quantifying expression based on mapped reads
-  **Salmon** tool for alignment free quantification of known transcripts

The next section provide a short how-to with all the commands to
execute the test workflow on Brown University's CCV cluster. 

 The basic steps to running a workflow are
 1. [Create a control file] [#Setup the configuration fie]
 2. Create your working directory if does not exist
 3. [Setup a screen session][/docs/tutorials/Setup_bioflows_env/#Setup GNU screen session]
## Setup the YAML configuration file

For the test run we use the following YAML format control file. A
detailed documentation of the YAML file and all the options is shown
here. For the current example, we will discuss each section in detail  below

```yaml
    bioproject: Project_test_localhost
    experiment: :red:rnaseq_pilot
    sample_manifest:
      fastq_file: sampl_manifest_min.csv
      metadata:
    run_parms:
      conda_command: source activate /gpfs/runtime/opt/conda/envs/cbc_conda_test
      work_dir: /gpfs/scratch/aragaven/test_workflow
      log_dir: logs
      paired_end: False
      local_targets: False
      db: sqlite
      db_loc: ':memory:'
      saga_host: localhost
      ssh_user: aragaven
      saga_scheduler: slurm
      gtf_file: /gpfs/data/cbc/cbcollab/ref_tools/Ensembl_mus_GRCm38.p5_rel89/Mus_musculus.GRCm38.89.gtf
    workflow_sequence:
      fastqc: default
      gsnap:
        options:
          -d: Ensembl_mus_GRCm38.p5_rel89
          -s: Mus_musculus.GRCm38.89.splicesites.iit
        job_params:
          ncpus: 16
          mem: 40000
          time: 60
      qualimap_rnaseq: default
      htseq-count: default
```

## Submit the workflow

Copy the above into a text file and save it in **/users/username** as
__test_run.yaml__

Copy the manifest below into a text file and save it in
**/users/username** as __sample_manifest_min.csv__

```
    samp_1299,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_2.gz
    samp_1214,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_2.gz
```

Now in your screen session run the following commands to setup your
environment if you have not done so previously during the setup or you
have started a new screen session

```
    source activate_cbcC_dona
    bioflows-rnaseq test_run.yaml
```

In this case I have created a small test dataset with 10000 reads from a
test human RNAseq data, so it should run within the hour and you should
see that the alignments are completed.
