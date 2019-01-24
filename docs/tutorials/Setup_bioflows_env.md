# Setting up the environment for **bioflows**

This section is specifically aimed at users of Brown University's OSCAR HPC cluster. Users of other systems should pay close attention to the ** what should they pay attention to? **

## Setup conda envinronment
First make sure the conda environment is setup in your `PATH`
variable. In your CCV console type

```
    echo $PATH
```

You should see `/gpfs/runtime/cbc_conda/bin/` as the first
element in the list of paths in your output. If you do not see this, then load the **cbc_conda** module as follows:

```
source /gpfs/runtime/cbc_conda/activate_cbc_conda
```

!!! note
    if the module command does not work then use
    ```
        export PATH=/gpfs/runtime/cbc_conda/bin/:$PATH
    ```

run the `echo $PATH` command again to confirm that `/gpfs/runtime/cbc_conda/bin/` is the first element in the list of paths in your output.

??? tip "Error in Paths"
    If  `/gpfs/realtime/cbc_conda/bin/` is not the first element in the list, then use the command

	```
	   export PATH=/gpfs/data/cbc/cbc_conda_v1/bin/:$PATH
    ```

    This will add  `/gpfs/realtime/cbc_conda_v1/bin/` to the beginning of your `PATH` variable

For convenience we will use `/users/username` as the working directory. You should modify this parameter to reflect the path to your own preferred working directory.

## Setup GNU screen session
These scripts should be run in a persistent terminal session and we will
use `GNU screen` to do that, which will allow us to disconnnect from our ssh
sessions without disrupting long running jobs. To learn more on how to use screen use
the following link
[gnu
screen tutorial](https://www.linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions)

Start a screen session naming it `test_bioflows` as shown below:

```
screen -S test_bioflows
```

Once you are in your screen session, set up your `conda` environment containing **bioflows**
with the following commands:
```
source /gpfs/runtime/cbc_conda/activate_cbc_conda
```
??? tip "activate with PATH/ variable set"
    if you have set the `PATH` variable instead as mentioned above the just use the command
    ```
        source activate_cbc_conda
    ```
Activating the conda environment may take a few moments, but you should see a prompt that looks like this:

```
(cbc_conda_v1) [your_ccv_username@login004 ~]$
```
If you don't see the prompt, you may need to press enter again to get your terminal window to refresh. Now you are ready to run the predefined workflows in specific tutorials.
