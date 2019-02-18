from setuptools import setup

setup(
    name='bioflows',
    version='0.99',
    packages=['bioflows','bioflows.test_others','bioflows.test_wrappers', 'bioflows.test_rnaseq_workflow', 'bioflows.bioutils',
              'bioflows.bioutils.access_sra', 'bioflows.bioutils.parse_fastqc', 'bioflows.bioutils.convert_bam_to_fastq',
              'bioflows.bioflowsutils', 'bioflows.definedworkflows',
              'bioflows.definedworkflows.rnaseq'],
    # install_requires= [luigi, saga-python, radical-utils, lxml, biopython, jsonpickle, pyyaml, xz, lftp],
    url='',
    license='GPLv2',
    author='Ashok Ragavendran',
    author_email='ashok_ragavendran@brown.edu',
    description='',
    entry_points={
        'console_scripts': ['bioflows-rnaseq = bioflows.definedworkflows.rnaseq.rnaseqworkflow:rna_seq_main',
                            'bioflows-dnaseq = bioflows.definedworkflows.rnaseq.rnaseqworkflow:dna_seq_main',
                            'bioflows-gatk = bioflows.definedworkflows.rnaseq.rnaseqworkflow:gatk_main'],
    },
    include_package_data=True,
)
