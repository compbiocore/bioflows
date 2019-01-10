# `bioflows`

## Summary
This is a guide to using the `bioflows` package for running standard
pipelines to analyse NGS datasets. Currently, we have implemented one version of a 
standard RNA-seq pipeline, alongwith a tutorial, for analysis of
RNA-seq data using this package.

## Overview
A primary objective of the Computational Biology Core at Brown's Centre for Computational Biology of Human Diesease, is to enable reproducibility in computational analysis of NGS data. Critical to this objective is to provide a simple tool for creating/running bioinformatics workflows as well as consistent software environments across multiple platforms. To achieve this goal we have:
    - Developed `bioflows` a workflow tool to ensure consistency in analysis steps and stages with interoperability across multiple job submission systems
    - [**Use CONDA**](https://conda.io/docs/) package management system for managing software tools
    - Container based approach using [**docker**](https://www.docker.com) for cross-platform interoperability of the analysis environment

`bioflows` is an user-friendly python implementation of a workflow manager. The user is expected to not have any programming knowledge and needs to only provide a control file in a YAML format, chosen for its human readability. The goal here is to provide users with a simple and straight-forward interface for processing NGS datasets with many samples using standard bioinformatics pipelines, e.g  RNA-seq, GATK variant calling etc. The tool is developed to alleviate some of the primary issues with scaling up pipelines, such as file naming, management of data, output and logs. 

## How it works

## Key Features
Currently `bioflows` provides the following features:
    - A straightforward approach to management of
        1) data
        2) logs
        3) results
        4) scripts
    - A module to easily download data from NCBI's SRA archive and to optionally directly continue processing the data through the pipelines. A few key elements of this module are:
        - Only download and convert the data to usable fastqs
        - Data from multiple runs are concatenated automatically
        - Metadata associated with the SRA data is also provided as a seperate table
    - Conda packages for all dependencies are already pre-built and provided alongwith the software
## Conda Package Management

CONDA is a system agnostic software package management system based on
the Anaconda python distribution to ensure that a software and all its
dependencies are bundled together. These conda packages can be
downloaded from various publicly available repositories called
*channels* and one such channel for bio-informatics tools is bioconda.

For ensuring reproducibily, we have established a publicly accessible
channel for all programs that are included with wrappers within the
*bioflows* tool through the [**compbiocore channel**](https://anaconda.org/compbiocore/). In this channel, we have also provided conda packages of all software used including
the *bioflows* package itself. To download specific packages or the *bioflows* tool use the command into your conda environment:

```
    conda install -c compbiocore /pkg_name/
```
!!! note
    **bioflows** and its dependencies are available as `conda` pacakges for the linux OS only. 
    To use **bioflows** in other OSes you will need to use the docker container approach
    
More detailed instructions on how to install anaconda and use the conda
environments can be found in the anaconda documentation for:

-   [Installation](https://docs.anaconda.com/anaconda/install.html)
-   [Getting started](https://docs.anaconda.com/anaconda/user-guide/getting-started.html)

