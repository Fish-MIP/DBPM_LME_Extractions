#!/usr/bin/python

### Script to extract variables by LME for DBPM, for ISIMIP3a FishMIP protocol
### Author: Ryan Heneghan (r.heneghan@qut.edu.au)

import numpy as np
import xarray as xr
import pandas as pd
import glob
import netCDF4
import h5netcdf
from datetime import datetime
import calendar

## Resolution
resolutions = ["15arcmin", "onedeg"]

## Directory and file names for masks, make sure mask names in same order as resolutions
mask_dir = "/work/bb0820/ISIMIP/ISIMIP3b/InputData/geo_conditions/fishmip_regions/"
mask_names = ["LMEs66_masks_0.25deg.nc","LMEs66_masks_1deg.nc"]

## Directory and file names for grid area netcdfs, make sure names in same order as resolutions
area_dir = "/home/b/b380694/DBPM_Attribution/"
area_names = ["gridarea_0.25deg.nc", "gridarea_1deg.nc"] # Grid area files in m2

## Directory names for obsclim and ctrlclim (for variables with monthly time step)
experiments = ["obsclim", "ctrlclim"]

## Directory for non-fixed variables (all except deptho)
experiment_dirs = ["/work/bb0820/ISIMIP/ISIMIP3a/InputData/climate/ocean/obsclim/global/monthly/historical/GFDL-MOM6-COBALT2/", \
    "/work/bb0820/ISIMIP/ISIMIP3a/SecondaryInputData/climate/ocean/ctrlclim/global/monthly/historical/GFDL-MOM6-COBALT2/"]

## Deptho directory
fixed_dirs = ["/work/bb0820/ISIMIP/ISIMIP3a/InputData/climate/ocean/obsclim/global/fixed/historical/GFDL-MOM6-COBALT2/", \
                "/work/bb0820/ISIMIP/ISIMIP3a/SecondaryInputData/climate/ocean/ctrlclim/global/fixed/historical/GFDL-MOM6-COBALT2/"]

save_root = "/home/b/b380694/DBPM_Attribution/lme_output/"

## Variable names
vars = ["phyc-vint", "phypico-vint", "tos", "tob", "expc-bot", "deptho"] # Add chl, but it's 3D, so will crash for 0.25deg (haven't tried on tmux yet though)

for f in range(0, len(resolutions)): ## Loop over resolution
    curr_res = resolutions[f] # Current resolutions string

    curr_mask_path = mask_dir + mask_names[f] # Path to current mask file
    curr_mask = xr.open_dataset(curr_mask_path) # Load current mask with all LMEs
    lmes = list(curr_mask.keys()) # List of names of all lmes

    # Create map with all lmes (then invert to create map of open ocean, excluding lmes)
    all_lmes = xr.concat(curr_mask.values(),dim=lmes).data
    all_lmes[np.isnan(all_lmes)] = 0
    open_ocean = np.sum(all_lmes, axis = 0)
    open_ocean[open_ocean == 1] = np.nan
    open_ocean[open_ocean == 0] = 1

    curr_area_path = area_dir + area_names[f] # Path to current grid area file
    curr_grid_area = xr.open_dataset(curr_area_path)['cell_area'][:].values # Load grid area for current resolution

    lat_grid = np.transpose(np.tile(curr_mask['lat'][:].values, (int(curr_mask['lon'][:].values.size),1))) # Lat grid (for lme locations extraction)
    lon_grid = np.tile(curr_mask['lon'][:].values, (int(curr_mask['lat'][:].values.size),1)) # Lon grid (for lme locations extraction)

    for g in range(0, len(experiments)): ## Loop over experiment
        curr_experiment = experiments[g]
        curr_experiment_dir = experiment_dirs[g]

        for h in range(0, len(vars)): ## Loop over variables
            curr_var = vars[h]

            if curr_var != "deptho": # Different directory for non deptho variables
                curr_var_file_name = glob.glob(curr_experiment_dir + '*_' + curr_var + '_' + curr_res + '_*')

            if curr_var == "deptho": # Different directory for deptho
                curr_var_file_name = glob.glob(fixed_dirs[g] + '*_' + curr_var + '_' + curr_res + '_*')

            # Open netcdf, extract variable data
            print("Now opening " + curr_var + " " + curr_res + " " + curr_experiment)
            curr_ncfile = xr.open_dataset(curr_var_file_name[0])
            curr_data = curr_ncfile[curr_var][:].values

            if curr_var == "chl": # If current variable is chlorophyll, extract surface level only
                curr_data = curr_data[:,:,:,0]

            # Units of current variable will go into csv file name
            curr_units = curr_ncfile[curr_var].units
            curr_units = curr_units.replace(" ", "_")
            
            if curr_var != "deptho": # If not deptho, time dimension turned into column names for csv
                num_time = curr_data.shape[0]

                times = curr_ncfile.indexes['time']
                times = np.char.add(np.char.add([calendar.month_abbr[x] for x in times.month],"_"),[str(x) for x in times.year])
                col_names = np.append(np.array(['lat', 'lon', 'area_m2']), times)
        
            if curr_var == "deptho": # If deptho, we don't have a time columns in csv
                col_names = ['lat', 'lon', 'area_m2', 'm']

            for k in range(0, len(lmes)): ## Loop over LMEs (+1 at the end for open ocean)
                print(curr_res + " " + curr_experiment + " " + curr_var + " LME: " + str(int(k+1)))

                if k < len(lmes): # If you're not in the open ocean
                    curr_lme = lmes[k] # Identify current LME
                    curr_lme_mask = curr_mask[curr_lme][:].values # Load current lme mask
                    curr_lme_mask[np.isnan(curr_lme_mask)] = 0
                    curr_lme_mask = ~np.array(curr_lme_mask, dtype = bool)

                if k == len(lmes): # If you're in the open ocean
                    curr_lme = "open_ocean" # Identify current LME
                    curr_lme_mask =  open_ocean # Load current lme mask
                    curr_lme_mask[np.isnan(curr_lme_mask)] = 0
                    curr_lme_mask = ~np.array(curr_lme_mask, dtype = bool)

                # Extract lats
                lat_lme = np.ma.array(lat_grid, mask = curr_lme_mask) # Mask lats
                lat_lme_vals = lat_lme[~lat_lme.mask].data # Pull out unmasked lats (these are in the lme)

                # Extract lons
                lon_lme = np.ma.array(lon_grid, mask = curr_lme_mask) # Mask lons
                lon_lme_vals = lon_lme[~lon_lme.mask].data # Pull out unmasked lons (these are in the lme)

                # Extract areas
                area_lme = np.ma.array(curr_grid_area, mask = curr_lme_mask) # Mask area
                area_lme_vals = area_lme[~area_lme.mask].data # Pull out unmasked areas (these are in the lme)

                lat_lon_area =  np.column_stack([lat_lme_vals, lon_lme_vals, area_lme_vals])

                if curr_var != "deptho": # If not deptho, we need to handle time dimension
                    var_lme = np.ma.array(curr_data, mask=np.tile(curr_lme_mask, (curr_data.shape[0],1))) # Mask variable
                    var_lme_vals = var_lme[~var_lme.mask] # Pull out unmasked values (these are in the lme)

                    # Reshape into 2d matrix - nrows are locations, ncols are time
                    var_lme_vals_2d = np.reshape(var_lme_vals, (int(var_lme_vals.size/num_time),int(num_time)), order='F').data

                    # Append lats, lons and grid cell area to variable array
                    all_data = pd.DataFrame(np.append(lat_lon_area, var_lme_vals_2d, 1), columns = col_names).dropna() # Drop na rows to remove land cells

                if curr_var == "deptho": # If deptho, no time dimension to handle
                    var_lme = np.ma.array(curr_data, mask=curr_lme_mask) # Mask variable
                    var_lme_vals = var_lme[~var_lme.mask].data # Pull out unmasked values (these are in the lme)

                    # Append lats, lons and grid cell area to variable array
                    all_data = pd.DataFrame(np.column_stack([lat_lon_area, var_lme_vals]), columns = col_names).dropna() # Drop na rows to remove land cells

                # Get csv file name
                csv_file_name = save_root + "gfdl-mom6-cobalt2_" + curr_experiment + "_" + curr_var + "_" + curr_units + "_" + curr_res + "_LME_" + str(int(k+1)) + "_monthly_1961_2010.csv"
                    
                # Save file
                all_data.to_csv(csv_file_name, index = False)




                
