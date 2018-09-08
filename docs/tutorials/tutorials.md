# bioflows Tutorials

This section provides an overview of how to run pre-defined workflows using
the **bioflows** package. The tutorials are based on presuming that the analysis is
conducted on the Brown [CCV](https://web1.ccv.brown.edu) compute cluster, to use on other systems please
check the installation instructions for setting up your environment. Currently, we have implemented an RNA-seq
workflow using the GSNAP RNAseq aligner. This will be updated as new workflows and enhancements are made to the BioFlows package.

!!! note
    If you are not sure what the console means or how to login to CCV go to this resource.


## Setup the Environment for bioflows

First make sure the conda environment is setup in your PATH
variable. In your CCV console type

```
    echo $PATH
```

and you should see `/gpfs/runtime/cbc_conda/bin/` as the first
element in the list of paths in your output.

if you do not see this then load the **cbc_conda** module as follows

```
module load cbc_conda
```
 run the `echo $PATH` command again.

    ??? tip "Error in Paths"
	If  `/gpfs/realtime/cbc_conda/bin/` is not the first element in the list then use the command 
	
	```
	   export PATH=/gpfs/data/cbc/cbc_conda_v1/bin/:$PATH 
    ```
      
	This will add  `/gpfs/realtime/cbc_conda_v1/bin/` to the beginning of your `PATH` variable

For convenience we will use `/users/username` as the working directory and you should modify
the path to the working directory accordingly.

These scripts should be run in a persistent terminal session and we will
use GNU screen to do that, so that the we can disconnnect from our ssh
sessions for long running jobs. To learn more on how to use screen use
the following link
[gnu
screen tutorial](https://www.linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions)

Start a screen session naming it `test_bioflows` as shown below

```
screen -S test_bioflows
``` 

once you are in your screen session you set up your python environment
with the following commands
```
source activate_cbc_conda
```

Now you are ready to run the predefined RNAseq workflow