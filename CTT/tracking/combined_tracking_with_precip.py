## This python script performs recombines detected and segmented features based on cloud top temperatures and combines those with precipitation to filter convective systems

import iris
import numpy as np
import pandas as pd
import os,sys
import datetime
from netCDF4 import Dataset
import tobac


## Recombination of feature dataframes (update framenumbers)

# read in HDF5 files with saved features
file_list= glob.glob(savedir  + '/Features_Precip??????.h5')  
file_list.sort()
print('nr. of monthly feature files:', len(file_list))


i = 0 
frames = 0 

for file in file_list: 
    if i == 0:
        Features = pd.read_hdf(file, 'table')
        # read in data mask with segments for tracked cells 
        date= file[len(file)-9: len(file)-3]
        ds = Dataset(savedir+ '/Mask_Segmentation_precip'+date+'.nc')
        mask = np.array(ds['segmentation_mask'])  
        # update total nr of frames 
        frames += np.shape(mask)[0] -1
        i = 1 
        print('file for: ',date, 'rows: ',features.shape[0], 'frames: ', frames)

    features = pd.read_hdf(file, 'table')
    # update frame number and make sure they are sequential
    features['frame'] = features['frame']  + frames
    # append dataframes 
    Features = Features.append(features, ignore_index=True)      
    # read in data mask with segments for tracked cells 
    date= file[len(file)-9: len(file)-3]
    ds = Dataset(savedir+ '/Mask_Segmentation_precip'+date+'.nc')
    mask = np.array(ds['segmentation_mask'])  
    #update total nr of frames
    frames += np.shape(mask)[0]
    print('file for: ',date, 'rows: ',features.shape[0], 'frames: ', frames)




## remove all features which do not meet heavy rain core criteria










    
## Perform trjactory linking with trackpy 
Track=tobac.linking_trackpy(Features,Precip,dt=dt,dxy=dxy,**parameters_linking)
Track.to_hdf(os.path.join(savedir,'Tracks_precip.h5'),'table')
