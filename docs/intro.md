# Using bioflows

## INTRODUCTION

This is a guide to using the bioflows package for standard
workflows to analyse NGS datasets. Currently, we have implemented one
standard RNA-seq workflow and a tutorial is included for analysis of
RNA-seq data using this package.

One primary objective of the Core is to enable reproducibility of 
computational analysis of NGS data and critical to this objective is to
provide a consistent software environment across multiple platforms. The
achieve this goal we are using the following approaches:

-   Container based approach using [docker](https://www.docker.com) for managing the analysis environment
-   [CONDA](https://conda.io/docs/) package management system for managing software tools
-   BioFlows workflow tool to ensure consistency in analysis steps and
    stages with interoperability across multiple job submission systems



## CONDA PACKAGE MANAGEMENT

CONDA is a system agnostic software package management system based on
the Anaconda python distribution to ensure that a software and all its
dependencies are bundled together. These conda packages can be
downloaded from various publicly available repositories called
*channels* and one such channel for bio-informatics tools is bioconda.

For ensuring reproducibily, we have established a publicly accessible
channel for all programs that are included with wrappers within the
bioflows tool accessible through the [compbiocore channel](https://anaconda.org/compbiocore/). In this channel, we have provided conda packages of all software used including
the bioflows package itself. To download the packages or the bioflows tool use the command into your conda environment:

    conda install -c compbiocore /pkg_name/

More detailed instructions on how to install anaconda and use the conda
environments can be found in the anaconda documentation for:

-   [Installation](https://docs.anaconda.com/anaconda/install.html)
-   [Getting started](https://docs.anaconda.com/anaconda/user-guide/getting-started.html)

