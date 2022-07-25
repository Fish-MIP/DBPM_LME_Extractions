### Script to extract variables by LME for DBPM, for ISIMIP3a FishMIP protocol
### Author: Ryan Heneghan (r.heneghan@qut.edu.au)

** Note: 
1) You need to update area_dir and save_root in the script, specific to your own account. area_dir is wherever you have saved LMEs66_masks_* netcdfs 
2) Update your variables for extraction by typing them in the 'vars' array, note 3D variables at 0.25deg resolution caused Levante to kill the script.

Can be run on Levante, do the following to run:

In Levante, open a tmux screen by typing 'tmux', this will run the script even if you exit the dkrz server on your local machine (since script can take a while to run, depending on the number of variables you require)

Load python3: module load python3

Run script: python3 LME_extractions_DBPM_ISIMIP3a.py


