import bioflows.bioflowsutils.wrappers as genwr
import pytest
from bioflows.definedworkflows.rnaseq.rnaseqworkflow import GatkFlow as mainwf
import bioflows.bioflowsutils.new_wrappers as nwr

@pytest.fixture(params=["/Users/aragaven/Documents/Research/PycharmProjects/bioflows/bioflows/test_wrappers/test_wrappers_pe.yaml"])
def baseWrapper(request):
    return mainwf(request.param)

def test_gsnap(baseWrapper):
    baseWrapper.set_base_kwargs()
    baseWrapper.parse_prog_info()
    wrapper_name = 'gsnap'
    add_args = baseWrapper.prog_args[wrapper_name]
    new_base_kwargs = baseWrapper.update_prog_suffixes(wrapper_name)
    wrapper_def = '/Users/aragaven/Documents/Research/PycharmProjects/bioflows/bioflows/bioflowsutils/programs_config.yaml'
    #wrappers = nwr.create_wrapper_class(wrapper_def)
    #gsnap_test = wrappers['Gsnap'](wrapper_name, "test_samp", *add_args, **dict(new_base_kwargs))
    gsnap_test = baseWrapper.prog_wrappers['gsnap'](wrapper_name, "test_samp", *add_args, **dict(new_base_kwargs))
    print "\n ***** Testing gsnap command ********* \n"
    print gsnap_test.run_command
    print "\n\n"
    print gsnap_test.__dict__
    print "\n\n"
    return

def test_samtools_sort(baseWrapper):
    print "\n\n ***** Testing Samtools sort ********* \n\n"
    baseWrapper.set_base_kwargs()
    baseWrapper.parse_prog_info()
    wrapper_name = 'samtools_sort'
    add_args = baseWrapper.prog_args[wrapper_name]
    new_base_kwargs = baseWrapper.update_prog_suffixes(wrapper_name)
    wrapper_def = '/Users/aragaven/Documents/Research/PycharmProjects/bioflows/bioflows/bioflowsutils/programs_config.yaml'
    #wrappers = nwr.create_wrapper_class(wrapper_def)
    #gsnap_test = wrappers['Gsnap'](wrapper_name, "test_samp", *add_args, **dict(new_base_kwargs))
    samtools_sort_test = baseWrapper.prog_wrappers['samtools_sort'](wrapper_name+"_round_2", "test_samp", *add_args, **dict(new_base_kwargs))
    print "\n ***** Testing Samtools command ********* \n"
    print samtools_sort_test.run_command
    print "\n\n"
    print samtools_sort_test.__dict__
    print "\n\n"
    return
