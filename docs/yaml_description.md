# `bioflows` YAML control file Specifications

## Project information section

-   `bioproject`: This will be an unique identifier for your project.
    This is adopted from the NCBI SRA format structure, so if you use an
    SRA dataset you can employ these ids

-   `experiment`: An identifier for your experiment such as RNA-seq,
    ChIP-seq etc

-   `sample_manifest`: This section contains two sections
    -   `fastq_file`: The full path to the sample to fastq map file.
        This file is in a three column comma separated format with each line formatted as:
        
        `sample_id, path_to_fastq_file_for_read1, path_to_fastq_file_for_read2`
        
        The `sample_id` is unique and if you are **using single end data** you just need
        to specify one column as shown below:
        
        `sample_id, path_to_fastq_file`
    
    -   `metadata`: This is all the metadata associated with a given
        `sample_id` if available such as gender, extraction date etc. This
        should also be a CSV format file. Currently, not necessary as this
        information is not yet used

## Global run parameters
-   `run_parms`: This section specifies the global parameters for the
    current analysis
    -   `conda_command`: This is the command used to activate your conda
        environment
    
    -   `work_dir`: The working directory for analysis usually created on  `/gpfs/scratch`
    
    -   `log_dir`: The subdirectory for all the log files
    
    -   `paired_end`: Whether data consists of paired end reads or single end
        reads (True/False)
    
    -   `local_targets`: Whether this workflow is being run from a local
        machine
    -   `saga_host`: The hostname if workflow is run from a local machine
    
    -   `ssh_user`: The user name if workflow is run from a local machine
    
    -   `saga_scheduler`: The scheduler being used, for CCV the value
        used here is
    
    -   `gtf_file`: The full path to the gtf file for gene annotations

## Workflow parameters
-   `workflow_sequence`: This section specifies the sequence of tools to
    be used and the options passed to tools as well as the job parameters
    if using a scheduler such as slurm
    -   `fastqc`:If you want to use the default parameters use *default*
        else you can use any of the options provided by the
        program. See  the example for GSNAP below on how to do
        that. See the documentation for the options for fastqc.
    
    -   `gsnap`: Here we give an example of two sections as we need to
        pass the index information to the aligner
        -   `options`: Specify program options here. In this example we
            specify the following
            
            -   **-d:** The genome index for GSNAP
            
            -   **-s:** and the splicesites file location for GSNAP.
            
            The format is exactly that as to what you would specify on the command line for the program
            
                -d Ensembl_mus_GRCm38.p5_rel89
                -s Mus_musculus.GRCm38.89.splicesites.iit
            
            See the documentation for the GSNAP program for more options
        
        -   `job_param`s: This section specifies parameters for job submission such as memory, number of cores etc
            -   ncpus: 16
            -   mem: 40000
            -   time: 60
    
    -   `qualimap_rnaseq`: Run the qualimap module for RNAseq with the **default** settings

The final YAML control file should look as below to run a test example. Only modify the parts
that are highlighted below to fill in your own values.

    bioproject: Project_test_localhost
    experiment: rnaseq_pilot
    sample_manifest:
      fastq_file: /users/:bluetext:`username/sample_manifest_min.csv`
      metadata:
    run_parms:
      conda_command: source activate /gpfs/runtime/opt/conda/envs/cbc_conda_test
      work_dir: /gpfs/scratch/'user/test_workflow'
      log_dir: logs
      paired_end: False
      local_targets: False
      db: sqlite
      db_loc: ":memory:"
      saga_host: localhost
      ssh_user: 'ccv username'
      saga_scheduler: slurm
      gtf_file: /gpfs/data/cbc/cbcollab/ref_tools/Ensembl_hg_GRCh37_rel87/Homo_sapiens.GRCh37.87.gtf
    workflow_sequence:
      fastqc: default
      gsnap:
        options:
          -d: Ensembl_Homo_sapiens_GRCh37
          -s: Ensembl_Homo_sapiens.GRCh37.87.splicesites.iit
        job_params:
          ncpus: 16
          mem: 40000
    	time: 60
      qualimap_rnaseq: default
      htseq-count: default



### How to run

Copy the above into a text file and save it in `/users/username` as `test_run.yaml`

Copy the manifest below into a text file and save it in `/users/username` as `sample_manifest_min.csv`

```yaml
samp_1299,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_2.gz
samp_1214,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_2.gz

```
    
Now in your screen session run the following commands to setup your
environment if you have not done so previously during the setup or you
have started a new screen session
```commandline
source activate bflows
bioflows-rnaseq test_run.yaml
```

In this case I have created a small test dataset with 10000 reads from a
test human RNAseq data, so it should run within the hour and you should
see that the alignments are completed.
