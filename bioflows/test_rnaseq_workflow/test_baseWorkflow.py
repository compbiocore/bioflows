import unittest,pytest
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import BaseWorkflow as bwf
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as mainwf

@pytest.fixture(params=["/Users/aragaven/PycharmProjects/bioflows/bioflows/test_rnaseq_workflow/test_run_localhost_slurm_pe_celegans.yaml"])
def baseWF(request):
    '''
    Create a baseworkflow instance for testing units
    :return:
    '''
    return bwf(request.param)

def test_find_command_rounds(baseWF):
    '''
    :param bwf:
    :return:
    '''
    new_key = 'fastqc'
    prog_list = ['fastqc_1','gsnap','fastqc_2']
    assert baseWF.find_command_rounds(new_key,prog_list) == 2
    return

def test_remove_prog_round_suffix(baseWF):
    assert baseWF.remove_prog_round_suffix('fastqc_round2') == 'fastqc'
    assert baseWF.remove_prog_round_suffix('samtools_view_round3') == 'samtools_view'
    return

def test_set_saga_parms(baseWF):
    baseWF.set_saga_parms()
    assert baseWF.job_params['saga_host'] == "localhost"
    assert baseWF.job_params['saga_scheduler'] == "slurm"

def test_parse_prog_info(baseWF):
    baseWF.parse_prog_info()
    print baseWF.prog_input_suffix
    print baseWF.prog_job_parms
    print baseWF.prog_output_suffix
    print baseWF.prog_suffix_type


@pytest.fixture(params=["/Users/aragaven/PycharmProjects/bioflows/bioflows/test_rnaseq_workflow/test_run_localhost_slurm_pe_celegans.yaml"])
def mainWF(request):
    '''
    Create a baseworkflow instance for testing units
    :return:
    '''
    return mainwf(request.param)

def test_chain_commands(mainWF):
        mainWF.sample_fastq_work = {'N2': '/gpfs/scratch/aragaven/test_workflow/sampN2.fq.gz',
                                      'N3': '/gpfs/scratch/aragaven/test_workflow/sampN3.fq.gz'}
        mainWF.set_base_kwargs()
        mainWF.parse_prog_info()
        print mainWF.prog_args
        print "\n***** Printing Chained Commands ******\n"
        #self.rw1.set_base_kwargs()
        mainWF.chain_commands()