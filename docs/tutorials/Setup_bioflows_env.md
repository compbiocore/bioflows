# Setting up the environment for **bioflows**

This section is specifically aimed at users of Brown University's OSCAR HPC cluster. Users of other systems should pay close attention to the file paths used, as they may be different for their particular system.

## Setup conda environment
### Setup on OSCAR HPC Cluster at Brown University
First load the **cbc_conda** environment as follows:

```
source /gpfs/runtime/cbc_conda/bin/activate_cbc_conda
```

!!! note
    Sometimes it may appear that there is no response. In that case make sure to wait for 2-3 minutes and the use `cntrl-c` to interrupt. You should see something like the below in your command prompt
    ```
       (cbc_conda_v1) [your_ccv_username@login004 mydir]
    ```

run the `echo $PATH` command to confirm that `/gpfs/runtime/cbc_conda/cbc_conda_v1_root/envs/cbc_conda_v1/bin` is the first element in the list of paths in your output.

??? tip "Error in Paths"
    If  `/gpfs/runtime/cbc_conda/cbc_conda_v1_root/envs/cbc_conda_v1/bin` is not the first element in the list, then use the command

	```
	   export PATH=/gpfs/runtime/cbc_conda/cbc_conda_v1_root/envs/cbc_conda_v1/bin:$PATH
    ```
    
    This will add  `/gpfs/runtime/cbc_conda/cbc_conda_v1_root/envs/cbc_conda_v1/bin` to the beginning of your `PATH` variable

For convenience we will use `/users/username` as the working directory. You should modify this parameter to reflect the path to your own preferred working directory.

### Setup on other systems
Install conda from anaconda following their installation instruction
## Setup GNU screen session
These scripts should be run in a persistent terminal session and we will
use `GNU screen` to do that, which will allow us to disconnnect from our ssh
sessions without disrupting long running jobs. To learn more on how to use screen use
the following link
[gnu
screen tutorial](https://www.linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions)

Change into your working directiory and start a screen session naming it `test_bioflows` as shown below:

```
cd /users/username
screen -S test_bioflows
```

Once you are in your screen session, set up your `conda` environment containing **bioflows**
```
source /gpfs/runtime/cbc_conda/activate_cbc_conda
```

Activating the conda environment may take a few moments, but you should see a prompt that looks like

```
(cbc_conda_v1) [your_ccv_username@login004 ~]$
```
If you don't see the prompt, you may need to press enter again (or `cntrl-c`)to get your terminal window to refresh. Now you are ready to run the predefined workflows in the tutorials.
