### Script to extract variables by LME for DBPM, for ISIMIP3a FishMIP protocol
### Author: Ryan Heneghan (r.heneghan@qut.edu.au)

*************
Note: 
1) You need to update area_dir and save_root in the script, specific to your own account. area_dir is wherever you have saved LMEs66_masks_* netcdfs and save_root is wherever you want to save output csvs
2) Update your variables for extraction by typing them in the 'vars' array. Note this script is only suitable for 2D variables, not 3D. Attempting to load a 3D netcdf at 0.25 degree resolution caused Levante to kill the script.
3) You can also extract for the open ocean, this script codes the open ocean as LME 67. To do that change the k loop initialisation (line 99) to be:

for k in range(0, len(lmes)+1)):

The +1 will run the open ocean region extraction. But note, the open ocean extractions are very large csvs.

*************

Can be run on Levante, do the following to run:

1) Set up save_root and area_dir, specific to your own account. Modify script to reflect changes, as well as the variables you need to extract.

2) Open a tmux screen by typing 'tmux', this will run the script even if you exit the dkrz server on your local machine (since script can take a while to run, depending on the number of variables you require)

3) Load python3: module load python3

4) Run script: python3 LME_extractions_DBPM_ISIMIP3a.py


