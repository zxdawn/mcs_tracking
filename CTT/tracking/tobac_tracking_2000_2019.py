## This python script performs a tracking cloud-features based tobac (Heikenfeld et al., 2019) on NCEP brightness temperatures. The specific tracking here aims for mesoscale convective systems in the Tibetan Plateau region, whereby a meso-scale convective system is defined as a cloud complex with
 

# Note that the input files are monthly files of merged 30-min data aggregated in one file, so that the feature detection and segmentation step of the tracking can be performed per month, whereby the linking is is conducted in the way that it can even link systems at the boundaries of two months.  


# created by Julia Kukulies, julia.kukulies@gu.se 



#####################################################################################################################
import warnings
import iris
import numpy as np
import pandas as pd
import datetime
from netCDF4 import Dataset
import tobac
import glob
import os 
import gc
############################### Parameters ###############################################################################################

# specify output directory 
data_dir = '/media/juli/Elements/gpm_v06/'
savedir = '/media/juli/Data/projects/data/satellite_data/ncep/ctt/Save/precip_tracking/'
os.makedirs(savedir,exist_ok=True)

# temporal and spatial resolution
dt= 1800
dxy = 14126.0


## Feature detection
# Dictionary containing keyword options (could also be directly given to the function)
parameters_features={}
parameters_features['position_threshold']='weighted_diff' # diff between specific value and threshold for weighting when finding the center location (instead of just mean lon/lat)
parameters_features['min_distance']=0 # minimum distance between features 
parameters_features['sigma_threshold']=0.5 # for slightly smoothing (gaussian filter)
parameters_features['n_erosion_threshold']=0 # pixel erosion (for more robust results)
parameters_features['threshold']=[1,2,3] #mm/h, step-wise threshold for feature detection 
parameters_features['n_min_threshold']=18 # minimum nr of contiguous pixels for thresholds, 10 pixels = ca. 2000 km2, 50 pixel ca. 10 000 km2
parameters_features['target']= 'maximum'


## Segmentation
# Dictionary containing keyword arguments for segmentation step:
parameters_segmentation={}
parameters_segmentation['target'] = 'minimum'
parameters_segmentation['method']='watershed'
parameters_segmentation['threshold']= 1  # mm/h mixing ratio (until which threshold the area is taken into account)


## Tracking 
# Dictionary containing keyword arguments for the linking step:
parameters_linking={}
parameters_linking['adaptive_stop']=0.2
parameters_linking['adaptive_step']=0.95
parameters_linking['extrapolate']=0
parameters_linking['order']=1
parameters_linking['subnetwork_size']= 1000 # maximum size of subnetwork used for linking 
parameters_linking['memory']=0
parameters_linking['time_cell_min']= 6*dt 
parameters_linking['method_linking']='predict'
#parameters_linking['method_detection']='threshold'
parameters_linking['v_max']= 10
#parameters_linking['d_min']=2000
parameters_linking['d_min']=4*dxy # four times the grid spacing ?

############################################################## Tracking : Feature detection and Segmentation ###################################################################################################
import glob


def get_files(year):
    # list with all files by month
    file_list= glob.glob(data_dir + year+ '/gpm_*monthly.nc4')
    file_list.sort()
    return file_list


def feature_detection(Precip, i):
    print('starting feature detection based on multiple thresholds')
    Features=tobac.feature_detection_multithreshold(Precip,dxy,**parameters_features)
    print('feature detection done')
    Features.to_hdf(os.path.join(savedir,'Features_' + str(i) + '.h5'),'table')
    print('features saved', Features.shape)

    return Features 


def segmentation(Features,Precip, i):
    print('Starting segmentation based on surface precipitation')
    Mask,Features_Precip=tobac.segmentation_2D(Features,Precip,dxy,**parameters_segmentation)
    iris.save([Mask],os.path.join(savedir,'Mask_Segmentation_' + str(i) + '.nc'),zlib=True,complevel=4)
    Features_Precip.to_hdf(os.path.join(savedir,'Features_cells_' + str(i) + '.h5'),'table')
    print('segmentation surface precipitation performed and saved')

    
def main(y): 
    file_list = get_files(year = y)
    file_list.sort()
    for f in file_list[5:9]:
        i= f[34:50]
        print('start process for file.....', i)
        
        ## load data 
        Precip=iris.load_cube(f, 'precipitationCal')
        #Precip.data[Precip.data > 300] = np.nan
        Precip.data[Precip.data< 0] = np.nan

        print('starting feature detection based on multiple thresholds')
        Features=tobac.feature_detection_multithreshold(Precip,dxy,**parameters_features)
        print('feature detection done')
        Features.to_hdf(os.path.join(savedir,'Features_' + str(i) + '.h5'),'table')
        print('features saved', Features.shape)

        print('Starting segmentation based on surface precipitation')
        Mask,Features_Precip=tobac.segmentation_2D(Features,Precip,dxy,**parameters_segmentation)
        iris.save([Mask],os.path.join(savedir,'Mask_Segmentation_' + str(i) + '.nc'),zlib=True,complevel=4)
        Features_Precip.to_hdf(os.path.join(savedir,'Features_cells_' + str(i) + '.h5'),'table')
        print('segmentation surface precipitation performed and saved')

        del Precip
        

for y in np.arange(2016,2020):
    main(str(y))
