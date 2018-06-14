.. contents::

3 Wrappers
==========
This section provides an overview of all the bioinformatic programs
that currenlty have wrappers implemented internally in BioFlows. For
each tool all the options are shown and any of these options can be
provided under options in the YAML file.

3.1 Fastqc
----------

Fastqc is a java program to undertake QC for fastq reads produced by
NGS, primarily illumina sequencing. More details on the tool as well
as the documentation from the original developers is available from the
`Fastqc <https://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`_
website. The following options are
currently available through the fastqc program wrapper in the bioflows package

.. command-output:: fastqc -h

3.2 GSNAP
---------

GSNAP is a splice aware RNAseq aligner, which is consistently among
the top aligners in the DREAM challenge (ref required).

.. command-output:: gsnap --help

3.3 Qualimap
------------

Qualimap is the suite of tools for generating metrics associated with
alginment of fastq reads. This tool provides multiple modules
including a module for collecting metrics to RNA-seq alignments. We
use the rnaseq module for generating metrics towards QC of the
alignments.

.. command-output:: qualimap rnaseq --help

3.4 HTSeq Counts
----------------

This script takes one or more alignment files in SAM/BAM format and a feature
file in GFF format and calculates for each feature the number of reads mapping
to it. See `the htseq docs <http://htseq.readthedocs.io/en/master/count.html>`_ for
details.

.. command-output:: htseq-count -h
