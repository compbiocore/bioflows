# Setting up the environment for **bioflows**

This section is specifically aimed at users of Brown University's OSCAR HPC cluster. Users of other systems should pay close attention to the 

## Setup conda envinronment
First make sure the conda environment is setup in your `PATH`
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

!!! note
   if the module command does not work then use   
   ```
        export PATH=/gpfs/runtime/cbc_conda/bin/:$PATH
   ```
 
run the `echo $PATH` command again.

??? tip "Error in Paths"
    If  `/gpfs/realtime/cbc_conda/bin/` is not the first element in the list then use the command 
	
	```
	   export PATH=/gpfs/data/cbc/cbc_conda_v1/bin/:$PATH 
    ```
      
    This will add  `/gpfs/realtime/cbc_conda_v1/bin/` to the beginning of your `PATH` variable

For convenience we will use `/users/username` as the working directory and you should modify
the path to your working directory accordingly.

## Setup GNU screen session
These scripts should be run in a persistent terminal session and we will
use `GNU screen` to do that, so that the we can disconnnect from our ssh
sessions for long running jobs. To learn more on how to use screen use
the following link
[gnu
screen tutorial](https://www.linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions)

Start a screen session naming it `test_bioflows` as shown below

```
screen -S test_bioflows
``` 

once you are in your screen session you set up your `conda` environment containing **bioflows** as follows
with the following commands
```
source activate_cbc_conda
```

Now you are ready to run the predefined workflows in specific tutorials