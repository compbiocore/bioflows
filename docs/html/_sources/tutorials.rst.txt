    :Author: aragaven

.. contents::


2 BioFlows Tutorials
--------------------

This section provides an overview of how to run pre-defined workflows using
the **bioflows** package. The tutorials are based on presuming that the analysis is
conducted on the Brown `CCV <https://web1.ccv.brown.edu>`_ compute cluster, to use on other systems please
check the installation instructions for setting up your environment. Currently, we have implemented an RNA-seq
workflow using the GSNAP RNAseq aligner. This will be updated as new
workflows and enhnacements are made to the BioFlows package.

2.1 Setup the Environment for bioflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First make sure the conda environment is setup in your PATH
variable. In your CCV console type

.. code:: sh

    echo $PATH

and you should see ``/gpfs/data/cbc/cbc_conda_v1/bin/`` in your output.

*If you are not sure what the console means or how to login to CCV go to this resource.*

For convenience we will use ``/users/username`` as the working directory and you should modify
accordingly.

These scripts should be run in a persistent terminal session and we will
use GNU screen to do that, so that the we can disconnnect from our ssh
sessions for long running jobs. To learn more on how to use screen use
the following link
`gnu
screen tutorial <https://www.linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions>`_

.. code:: sh

    screen -S test_bioflows

once you are in your screen session you set up your python environment
with the following commands

.. code:: sh

    source activate test_bioflows

Now you are ready to run the predefined RNAseq workflow

2.2 Tutorial 1. RNAseq with GSNAP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial show how to run a standard predefined RNA-seq analysis on
the using the bioflows tool. This workflow
consists of the following steps which have been implemented:

- **Fastqc**: For QC of Raw Fastq reads

- **GSNAP** alignment of the reads to the reference genome of the reads

- **Qualimap** tool for the QC of the aligments generated

- **featureCounts** tool for quantifying expression based on mapped reads

- **Salmon** tool for alignment free quantification of known transcripts

Below is a short how-to with all the commands

2.2.1 Setup the YAML configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the test run we use the following YAML format control file. A
detailed documentation of the YAML file and all the options is shown
here. For the current example, we will discuss each section in detail  below

.. code:: yaml

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

2.2.2 YAML description
^^^^^^^^^^^^^^^^^^^^^^

bioproject
    This will be an unique identifier for your project.
    This is adopted from the NCBI SRA format structure, so if you use an
    SRA dataset you can employ these ids

experiment
    An identifier for your experiment such as RNA-seq,
    ChIP-seq etc

sample\_manifest
    This section contains two sections

    fastq\_file
        The full path to the sample to fastq map file.
        This file is in a three column comma separated format with each line formatted as:

        *sample\_id, path\_to\_fastq\_file\_for\_read1, path\_to\_fastq\_file\_for\_read2*

        The *sample\_id* is unique and if you are **using single end data** you just need
        to specify one column as shown below:

        *sample\_id, path\_to\_fastq\_file*

    metadata
        This is all the metadata associated with a given
        *sample\_id* if available such as gender, extraction date etc. This
        should also be a CSV format file. Currently, not necessary as this
        information is not yet used

run\_parms
    This section specifies the global parameters for the
    current analysis

    conda\_command
        This is the command used to activate your conda
        environment

    work\_dir
        The working directory for analysis usually created on  ***gpfs/scratch***

    log\_dir
        The subdirectory for all the log files

    paired\_end
        Whether data consists of paired end reads or single end
        reads (True/False)

    local\_targets
        Whether this worklfow is being run from a local
        machine

    db
        default database engine to use ( sqlite)

    db\_loc
        location of the database ':memory:'

    saga\_host
        The hostname if workflow is run from a local machine

    ssh\_user
        The user name if workflow is run from a local machine

    saga\_scheduler
        The scheduler being used, for CCV the value
        used here is :redtext:`/slurm/`

    gtf\_file
        The full path to the gtf file for gene annotations

workflow\_sequence
    This section specifies the sequence of tools to
    be used and the options passed to tools as well as the job parameters
    if using a scheduler such as slurm

    fastqc
        If you want to use the default parameters use *default*
        else you can use any of the options provided by the
        program. See  the example for GSNAP below on how to do
        that. See the documentation for the options for fastqc.

    gsnap
        Here we give an example of two sections as we need to
        pass the index information to the aligner

        options
            Specify program options here. In this example we
            specify the following

            -d
                The genome index for GSNAP

            -s
                and the splicesites file location for GSNAP.

            The format is exactly that as to what you would specify on the command line for the program

            .. code:: sh

                -d Ensembl_mus_GRCm38.p5_rel89
                -s Mus_musculus.GRCm38.89.splicesites.iit

            See the documentation for the GSNAP program for more options

        job\_params
            This section specifies parameters for job submission such as memory, number of cores etc

            - ncpus: 16

            - mem: 40000

            - time: 60

    qualimap\_rnaseq
        Run the qualimap module for RNAseq with the **default** settings


The final YAML control file should look as below to run a test example. Only modify the parts
that are highlighted below to fill in your ownm values.

.. code:: yaml

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

2.2.3 How to run
^^^^^^^^^^^^^^^^

Copy the above into a text file and save it in **/users/username** as
test\_run.yaml

Copy the manifest below into a text file and save it in
**/users/username** as sample\_manifest\_min.csv

.. code:: sh

    samp_1299,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb2_2.gz
    samp_1214,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_1.gz,/gpfs/scratch/aragaven/rnaseq_test/PE_hg/Cb_2.gz

Now in your screen session run the following commands to setup your
environment if you have not done so previously during the setup or you
have started a new screen session

.. code:: sh

    source activate bflows
    bioflows-rnaseq test_run.yaml

In this case I have created a small test dataset with 10000 reads from a
test human RNAseq data, so it should run within the hour and you should
see that the alignments are completed.
