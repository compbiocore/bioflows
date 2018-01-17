from setuptools import setup

setup(
    name='bioflows',
    version='0.99',
    packages=['test_others','test_wrappers', 'test_rnaseq_workflow', 'bioutils',
              'bioutils.access_sra', 'bioutils.parse_fastqc', 'bioutils.convert_bam_fastq', 'bioflowutils', 'definedworkflows',
              'definedworkflows.rnaseq'],
    # install_requires= [luigi, saga-python, radical-utils, lxml, biopython, jsonpickle, pyyaml, xz, lftp],
    url='',
    license='GPLv2',
    author='Ashok Ragavendran',
    author_email='ashok_ragavendran@brown.edu',
    description='',
    entry_points={
        'console_scripts': ['bioflow-rnaseq = definedworkflows.rnaseq.rnaseqworkflow:main'],
    }
)
