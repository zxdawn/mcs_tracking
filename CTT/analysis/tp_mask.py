import pandas as pd
import numpy as np
import xarray as xr





## elevation mask 
import xarray as xr 
dem = '/media/juli/Data/projects/data/elevation/elevation_600x350.nc'
elevations = xr.open_dataarray(dem)
# mask as coordinates 
dem_mask = elevations.where(elevations >= 3000)
dem_mask.coords['mask'] = (('lon', 'lat'), dem_mask)



# track files 
precipfile = '/media/juli/Elements/gpm_v06/Save/2000_2019/Tracks_precipitation_GPM_'+ str(y) + '.h5'
preciptracks= pd.read_hdf(precipfile, 'table')
preciptracks = ptracks[ptracks.cell >= 0]
preciptracks.timestr = pd.to_datetime(preciptracks.timestr)

years = np.arange(2000,2019)
for y in years:
    print(y)
    # read in precip tracks 
    f = '/media/juli/Elements/gpm_v06/Save/2000_2019/Tracks_precipitation_GPM_'+ str(y) + '.h5'
    ptracks= pd.read_hdf(f, 'table')
    # remove nan values to only save the linked features                                                                                                      
    ptracks = ptracks[ptracks.cell >= 0]
    ptracks.timestr = pd.to_datetime(ptracks.timestr)
    preciptracks = preciptracks.append(ptracks)


from scipy import ndimage
from scipy.ndimage import generate_binary_structure
s= generate_binary_structure(2,2)


def plateau_mask(tracks):

    removed = 0
    tracks['tp_flag'] = 0 

        # loop through cells 
        for cell in np.unique(tracks.cell.values):
            subset = tracks[tracks.cell == cell]
            tp_flag = 0 
            # loop through timesteps of features for specific cell 
            for idx in subset.idx.values: 
                # idx is the timestep index for respective timestep or mask file 

                # open corresponding precip and mask file 
                year = subset.time.values[0].year 
                month = subset.time.values[0].month
                if len(str(month))== 1: 
                    month= '0' + str(month)

                # check whether segmented feature is in area above 3000 m 
                maskfile = '/media/juli/Data/projects/data/satellite_data/ncep/ctt/Save/tbbtracking/Mask_Segmentation_'+str(year) + str(month) + '.nc'
                mask = xr.open_dataarray(maskfile)
                mask= mask[:,1:,1:].T

                # get right timestep frames 
                seg= mask[:,:,idx]

                # get write features from segmentation mask 
                labels, nr = ndimage.label(seg, structure = s)
                if featureid in seg:
                    label = np.unique(labels[ seg == featureid])[0]
                    seg_mask = seg.where(labels == label)
                    # create mask as coordinates                                                                                                               
                    seg_mask.coords['mask'] = (('lon', 'lat'), seg_mask)


                    # get feature ID for frame 
                    featureid= subset.feature[subset.idx== idx].values[0]

                    # Elevation mask                                                                                                                           
                    elevation_values = dem_mask.where(seg_mask.coords['mask'].values > 1)
                    arr= elevation_values.values.flatten()
                    values = arr[~np.isnan(arr)]     

                    mountain_features = values[values >=3000].shape[0]
                    tracks['tp_flag'][tracks.feature == featureid] =  mountain_features

                    if mountain_features == 0 : 
                        tracks = tracks.drop(tracks[tracks.cell == cell].index)
                    else:
                        tracks['tp_flag'][tracks.feature == featureid] =  mountain_features

        return tracks 


tracks = plateau_mask(preciptracks)
tracks.to_hdf(os.path.join(savedir,'Tracks_tbb_TPflag.h5'),'table')    
