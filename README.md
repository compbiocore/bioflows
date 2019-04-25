# Project Title


[![Travis](https://img.shields.io/travis/compbiocore/cbc-documentation-templates.svg?style=flat-square)](https://travis-ci.org/compbiocore/bioflows)
[![Coverage](https://img.shields.io/coveralls/github/jekyll/jekyll.svg?style=flat-square)](http://www.coverage.com)
[![Docs](https://img.shields.io/badge/docs-stable-blue.svg?style=flat-square)](https://compbiocore.github.io/bioflows)
[![License](https://img.shields.io/badge/license-GPL_3.0-orange.svg?style=flat-square)](https://raw.githubusercontent.com/compbiocore/cbc-documentation-templates/master/LICENSE.md)  
[![Conda](https://img.shields.io/conda/v/compbiocore/optitype.svg?style=flat-square)](https://anaconda.org/compbiocore/bioflows)


## Overview
**bioflows** is an user-friendly python implementation of a workflow manager. The user is expected to not have any programming knowledge and needs to only provide a control file in a YAML format, chosen for its human readability. The goal here is to provide users with a simple and straight-forward interface for processing NGS datasets with many samples using standard bioinformatics pipelines, e.g  RNA-seq, GATK variant calling etc. The tool is developed to alleviate some of the primary issues with scaling up pipelines, such as file naming, management of data, output and logs. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This package requires the `conda-forge` and the `compbiocore` conda channels to have a higher priority than that of defaults. So your `.condarc` should look like

```
channels
 - compbiocore
 - conda-forge
 - defaults
```

### Installing

Installation is simple using conda environments

```
conda install -c compbiocore bioflows
```

This will install bioflows and all the necessary bioinformatics tools that are part of the standard workflows. 

[//]: # (End with an example of getting some data out of the system or using it for a little demo)

## Tests

[//]: # (Explain how to run the automated tests for this system)


## Deployment

[//]: # (Add additional notes about how to deploy this on a local machine and in a cloud provider.)


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Release History
[//]: # (- 0.4)
 [//]: # ( - CHANGES:  )

[//]: # (- 0.3)
[//]: # (  - CHANGES:)


## Authors

[//]: # (List authors and affiliation.)
