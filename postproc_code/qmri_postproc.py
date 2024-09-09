#!/usr/local/bin/python3
import os, glob, gzip, warnings
import nibabel
import matplotlib.pyplot as plt
import numpy as np
import ants
import pandas as pd
import nibabel as nib
import json
from scipy import ndimage

def replace_file_with_gzipped_version(file_path):
    '''Replace a file with a gzipped version of itself
    
    Parameters
    ----------
    file_path : str
        Path to the file to be gzipped
    
    '''
    
    #file_path = path to the file to be gzipped
    
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            f_out.writelines(f_in)
    os.remove(file_path)
    
    return file_path + '.gz'

def load_color_lut_df():
    '''Load a copy of the FreeSurfer Color Look Up Table

    Returns
    -------
    df : pandas.DataFrame
        A pandas dataframe with the FreeSurfer Color Look Up Table

    '''
    print('   Loading FreeSurfer Color Look Up Table')
    freesurfer_color_lut = '/postproc_code/FreeSurferColorLUT.txt'
    with open(freesurfer_color_lut, 'r') as f:
        lines = f.readlines()
    color_lut_dict = {'Region_Number': [], 'Region_Name': []}
    for temp_line in lines[4:-1]:
        if temp_line[0] == '#' or temp_line[0] == ' ' or temp_line[0] == '\n':
            continue
        color_lut_dict['Region_Number'].append(int(temp_line.split()[0]))
        color_lut_dict['Region_Name'].append(temp_line.split()[1])
    df = pd.DataFrame(color_lut_dict, index = color_lut_dict['Region_Number'])
    
    return df


def grab_anatomical_reference_metadata(anatomical_reference_path):
    '''Given a path to a nifti image, grab metadata from the corresponding json sidecar
    
    Parameters
    ----------
    anatomical_reference_path : str
        path to a nifti image that has a corresponding json sidecar

    Returns
    -------
    metadata_to_save : dict
        dictionary with metadata fields of interest

    '''
    
    #anatomical_reference_path = path to a nifti image that has a corresponding json sidecar
    
    print('   Grabbing metadata from anatomical reference image')
    json_path = anatomical_reference_path.replace('.nii' + anatomical_reference_path.split('.nii')[-1], '.json')
    with open(json_path, 'r') as f:
        contents = json.load(f)
        
    metadata_fields_to_grab = ['Manufacturer', 'ManufacturersModelName', 'DeviceSerialNumber' ,'PatientName', 'PatientBirthDate', 'AcquisitionDateTime']
    metadata_to_save = {}
    for temp_field in metadata_fields_to_grab:
        try:
            metadata_to_save[temp_field] = contents[temp_field]
        except:
            metadata_to_save[temp_field] = None
        
    return metadata_to_save
    
    
def make_outline_overlay_underlay_plot_ribbon(path_to_underlay, path_to_overlay, ap_buffer_size = 3, crop_buffer=20, num_total_images=16, dpi=400,
                                      underlay_cmap='Greys', linewidths=.1, output_path=None, close_plot=True):

    """Function that makes contour plot with nifti mask and underlay.


    Takes paths to two nifti files, the overlay nifti file will
    be thresholded, and a contour created out of the resulting mask
    and then will be projected over the underlay.

    Parameters
    ----------
    path_to_underlay : str
        path to underlay file
    path_to_overlay : str
        path to overlay that will be masked and used
        to create contour
    ap_buffer_size : int
        ap buffer
    crob_buffer : int
        make this bigger to reduce cropping
    num_total_images : int
        number of images in the panel, must
        have a sqrt that is an integer so
        panel can be square
    underlay_cmap : str
        the matplotlib colormap to use for the
        underlay
    linewidths : float
        the width of contour line
    output_path : str or None
        optional path for file to be saved
        (do not include extension)

    """

    print('   Making overlay/underlay plot')

    underlay_path = path_to_underlay
    underlay_obj = nib.load(underlay_path)
    underlay_data = underlay_obj.get_fdata()
    overlay_img = nib.load(path_to_overlay)
    overlay_data = overlay_img.get_fdata()
    

    orig_overlay = overlay_data
    overlay_data = np.zeros(orig_overlay.shape)
    #overlay_data[orig_overlay == 2] = 1
    #overlay_data[orig_overlay == 41] = 1
    #overlay_data[orig_overlay == 3] = 2
    #overlay_data[orig_overlay == 42] = 2
    overlay_data[orig_overlay > 0.5] = 1

    masked_vals = underlay_data[overlay_data > 0.5]
    hist_results = np.histogram(masked_vals, bins = 100)
    modal_value = hist_results[1][np.argmax(hist_results[0])]
    vmin = modal_value*.3
    vmax = modal_value*1.7

    overlay_ap_max = np.max(overlay_data,axis=(0,1))
    non_zero_locations = np.where(overlay_ap_max > 0.5)[0]
    min_lim = np.min(non_zero_locations) - ap_buffer_size
    if min_lim < 0:
        min_lim = 0
    max_lim = np.max(non_zero_locations) + ap_buffer_size
    if max_lim >= overlay_data.shape[2]:
        max_lim = overlay_data.shape[2] - 1
    inds_to_capture = np.linspace(min_lim,max_lim,num_total_images,dtype=int)

    overlay_max_0 = np.max(overlay_data,axis=(1,2))
    overlay_max_1 = np.max(overlay_data,axis=(0,2))
    overlay_locations_0 = np.where(overlay_max_0 > 0.5)[0]
    overlay_locations_1 = np.where(overlay_max_1 > 0.5)[0]
    min0 = np.min(overlay_locations_0) - crop_buffer
    if min0 < 0:
        min0 = 0
    max0 = np.max(overlay_locations_0) + crop_buffer
    if max0 >= overlay_data.shape[0]:
        max0 = overlay_data.shape[0] - 1
    min1 = np.min(overlay_locations_1) - crop_buffer
    if min1 < 0:
        min1 = 0
    max1 = np.max(overlay_locations_1) + crop_buffer
    if max1 >= overlay_data.shape[1]:
        max1 = overlay_data.shape[1] - 1


    num_imgs_per_dim = int(np.sqrt(num_total_images))
    counting_index = 0
    for i in range(num_imgs_per_dim):

        temp_underlay_row = underlay_data[min0:max0,min1:max1,inds_to_capture[counting_index]]
        temp_overlay_row = overlay_data[min0:max0,min1:max1,inds_to_capture[counting_index]]
        counting_index += 1
        for j in range(1,num_imgs_per_dim):
            temp_underlay_row = np.vstack((temp_underlay_row,underlay_data[min0:max0,min1:max1,inds_to_capture[counting_index]]))
            temp_overlay_row = np.vstack((temp_overlay_row,overlay_data[min0:max0,min1:max1,inds_to_capture[counting_index]]))
            counting_index +=1
        if i == 0:
            temp_underlay_full = temp_underlay_row
            temp_overlay_full = temp_overlay_row
        else:
            temp_underlay_full = np.hstack((temp_underlay_full,temp_underlay_row))
            temp_overlay_full = np.hstack((temp_overlay_full,temp_overlay_row))

    underlay_panel = np.fliplr(np.rot90(temp_underlay_full,1))
    overlay_panel = np.fliplr(np.rot90(temp_overlay_full,1))

    plt.figure(dpi=dpi)
    im = plt.contour(overlay_panel, linewidths=linewidths, colors='m')
    
    #im = plt.imshow(underlay_panel, cmap=underlay_cmap, vmax = vmax, vmin = vmin)
    im = plt.imshow(underlay_panel, cmap='gist_gray', vmax = vmax, vmin = vmin)
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')

    if type(output_path) != type(None):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches = 0)

    if close_plot == True:
        plt.close()

    return


def calc_qmri_stats(bids_directory, bibsnet_directory,
                     qmri_directory, output_directory,
                     subject_name, session_name, custom_roi_groupings = None,
                     sequence_name_source = 'acq'):
    '''Function to generate items of interest based on quantitative MRI maps
    
    
    Parameters
    ----------
    bids_directory : str
        Path to the study-level BIDS directory
    bibsnet_directory : str
        Path to the study-level BIBSNET directory
    qmri_directory : str
        Path to the study-level qMRI directory
    output_directory : str
        Path to the study-level directory where output should be saved
    subject_name : str
        Name of the subject to be processed (i.e. sub-01)
    session_name : str
        Name of the session to be processed (i.e. ses-01). Since these
        scripts are designed for HBCD which has sessions in the BIDS structure,
        this is required.
    
    
    '''
    
    #Be sure that different directories ends in file seperator
    output_directory = os.path.join(output_directory, '')
    bibsnet_directory = os.path.join(bibsnet_directory, '')
    qmri_directory = os.path.join(qmri_directory, '')
    bids_directory = os.path.join(bids_directory, '')
    
    
    ##########################################################################################
    ##########################################################################################
    ##########Identify the images that should be used in processing###########################
    ##########################################################################################
    t1w_segs = glob.glob(os.path.join(bibsnet_directory, subject_name, session_name, 'anat', '*space-T1w_desc-aseg_dseg.nii.gz'))
    t2w_segs = glob.glob(os.path.join(bibsnet_directory, subject_name, session_name, 'anat', '*space-T2w_desc-aseg_dseg.nii.gz'))
    
    #If possible, use T2w image instead of T1w
    if len(t2w_segs):
        print('   Using segmentation in T2w space as reference image')
        anatomical_reference_modality = 'T2w'
        bibsnet_seg_path = t2w_segs[0]
        bibsnet_mask_path = bibsnet_seg_path.replace('desc-aseg_dseg.nii.gz', 'desc-brain_mask.nii.gz')
        if os.path.exists(bibsnet_mask_path) == False:
            raise ValueError('Error: A T2w BIBSNET segmentation was found without a corresponding mask. Expected to find mask with name: {}'.format(bibsnet_mask_path))
        possible_anatomical_references = glob.glob(os.path.join(bids_directory, subject_name, session_name, 'anat', '*T2w.nii.gz'))
        if len(possible_anatomical_references) != 1:
            raise ValueError('Error: If a T2w segmentation is to be used for processing, only 1 T2w reference found in the subjects anat directory must be present but {} were found'.format(len(possible_anatomical_references)))
        else:
            anatomical_reference_path = possible_anatomical_references[0]
    #Use T1w image if T2w seg not found
    elif len(t1w_segs):
        print('   Using segmentation in T1w space as reference image')
        anatomical_reference_modality = 'T1w'
        bibsnet_seg_path = t1w_segs[0]
        bibsnet_mask_path = bibsnet_seg_path.replace('desc-aseg_dseg.nii.gz', 'desc-brain_mask.nii.gz')
        if os.path.exists(bibsnet_mask_path) == False:
            raise ValueError('Error: A T1w BIBSNET segmentation was found without a corresponding mask. Expected to find mask with name: {}'.format(bibsnet_mask_path))
        possible_anatomical_references = glob.glob(os.path.join(bids_directory, subject_name, session_name, 'anat', '*T1w.nii.gz'))
        if len(possible_anatomical_references) != 1:
            raise ValueError('Error: If a T1w segmentation is to be used for processing, only 1 T1w reference found in the subjects anat directory must be present but {} were found'.format(len(possible_anatomical_references)))
        else:
            anatomical_reference_path = possible_anatomical_references[0]
    else:
        raise ValueError('No segmentation found for {} and {} within {}'.format(subject_name, session_name, bibsnet_directory))
        
        
    #Find the qMRI Maps
    qmri_t1 = glob.glob(os.path.join(qmri_directory, subject_name, 'ses*', 'anat', '*T1map.nii.gz'))
    qmri_t2 = glob.glob(os.path.join(qmri_directory, subject_name, 'ses*', 'anat', '*T2map.nii.gz'))
    qmri_pd = glob.glob(os.path.join(qmri_directory, subject_name, 'ses*', 'anat', '*PDmap.nii.gz')) 
    qmri_t1w_path = glob.glob(os.path.join(qmri_directory, subject_name, 'ses*', 'anat', '*T1w.nii.gz'))
    qmri_t2w_path = glob.glob(os.path.join(qmri_directory, subject_name, 'ses*', 'anat', '*T2w.nii.gz'))

    if len(qmri_t1w_path)*len(qmri_t2w_path) != 1:
        raise ValueError('Error: Expected to have exactly one T1w and T2w image, but found the following images {}.'.format(qmri_t1w_path + qmri_t2w_path))

    if (len(qmri_t1) + len(qmri_t2) + len(qmri_pd)) == 0:
        raise ValueError('Error: Expected to have at least one T1map, T2map, or PDmap, but found the following images {}.'.format(qmri_t1 + qmri_t2 + qmri_pd))
    else:
        qmri_map_path_dict = {}
        if len(qmri_t1):
            qmri_map_path_dict['T1'] = qmri_t1[0]
            example_img_name = qmri_t1[0]
        if len(qmri_t2):
            qmri_map_path_dict['T2'] = qmri_t2[0]
            example_img_name = qmri_t2[0]
        if len(qmri_pd):
            qmri_map_path_dict['PD'] = qmri_pd[0]
            example_img_name = qmri_pd[0]

    sequence_name = ''
    for temp_keyvalue in example_img_name.split('/')[-1].split('_'):
        if sequence_name_source == temp_keyvalue.split('-')[0]:
            sequence_name = temp_keyvalue.split('-')[1]
            break
    if sequence_name == '':
        sequence_name = 'quant'
        
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################

    #Define the out dir
    anat_out_dir = os.path.join(output_directory, subject_name, session_name, 'anat')
        
    #Load some of the images that will be used
    print('   Loading qMRI maps')
    anatomical_reference = ants.image_read(anatomical_reference_path)
    segmentation = ants.image_read(bibsnet_seg_path)
    qmri_image_dict = {}
    for temp_qmri_map in qmri_map_path_dict.keys():
        qmri_image_dict[temp_qmri_map] = ants.image_read(qmri_map_path_dict[temp_qmri_map])

    #Load the JSON metadata from one of original qmri outputs.
    #Also remove SeriesDescription/ImageType fields that are specific to weighting.
    map_json = next(iter(qmri_map_path_dict.values())).replace('.nii.gz', '.json')
    with open(map_json, 'r') as f:
        qmri_json_dict = json.load(f)
    try:
        del qmri_json_dict["SeriesDescription"]
        del qmri_json_dict["ImageType"]
    except:
        pass

    def remove_extra_clusters_from_mask(mask_image_ants):

        temp_data = np.round(mask_image_ants[:])
        labels, nb = ndimage.label(temp_data)
        largest_label_size = 0
        largest_label = 0
        for i in range(nb + 1):
            if i == 0:
                continue
            label_size = np.sum(labels == i)
            if label_size > largest_label_size:
                largest_label_size = label_size
                largest_label = i
        new_mask_data = np.zeros(temp_data.shape)
        new_mask_data[labels == largest_label] = 1
        new_mask = mask_image_ants.new_image_like(new_mask_data)

        return new_mask
    
    #Register to the anatomical reference space using either a T1w/T2w workflow
    print('   Registering qMRI synthetic weighted image to anatomical reference space')
    anatomical_reference = ants.image_read(anatomical_reference_path)
    bibsnet_mask = ants.image_read(bibsnet_mask_path)
    adjusted_bibsnet_mask = remove_extra_clusters_from_mask(bibsnet_mask)
    dilated_mask = ants.utils.morphology(adjusted_bibsnet_mask, 'dilate', 35)
    if anatomical_reference_modality == 'T1w':
        qmri_for_reg = ants.image_read(qmri_t1w_path[0])
        reg = ants.registration(anatomical_reference, qmri_for_reg, type_of_transform='Rigid', initial_transform=None, mask=dilated_mask)
    elif anatomical_reference_modality == 'T2w':
        qmri_for_reg = ants.image_read(qmri_t2w_path[0])
        reg = ants.registration(anatomical_reference, qmri_for_reg, type_of_transform='Rigid', initial_transform=None, mask=dilated_mask)

    #Apply the transform calculated above to the t1map, t2map, and pdmap images
    Map_Interpolation_Scheme = 'bSpline'
    maps_array_dict = {}
    registered_maps_paths = {}
    print('   Generating and saving registered qMRI maps')
    for temp_qmri_map in qmri_map_path_dict.keys():
        temp_map = ants.image_read(qmri_map_path_dict[temp_qmri_map])
        temp_map_transformed = ants.apply_transforms(anatomical_reference, temp_map, reg['fwdtransforms'], interpolator = Map_Interpolation_Scheme)
        maps_array_dict[temp_qmri_map] = np.array(temp_map[:])
        registered_temp_map_path = os.path.join(anat_out_dir, '{}_{}_space-{}_desc-{}_{}map.nii'.format(subject_name, session_name, anatomical_reference_modality, sequence_name, temp_qmri_map))
        print('      Saving {}'.format(registered_temp_map_path))
        if os.path.exists(anat_out_dir) == False:
            os.makedirs(anat_out_dir)
        ants.image_write(temp_map_transformed, registered_temp_map_path)
        replace_file_with_gzipped_version(registered_temp_map_path)
        registered_maps_paths[temp_qmri_map] = registered_temp_map_path + '.gz'
    #Also transform the segmentation image back to qMRI (i.e. T1map/T2map/PDmap) space
    Segmentation_Interpolation_Scheme = 'nearestNeighbor'
    segmentation_reverse_transformed = ants.apply_transforms(qmri_for_reg, segmentation, reg['fwdtransforms'], interpolator = Segmentation_Interpolation_Scheme, whichtoinvert = [True])
    bibnset_file = bibsnet_seg_path.split('/')[-1]
    registered_segmentation_path = os.path.join(anat_out_dir, bibnset_file.replace(bibnset_file.split('_')[-3], 'space-{}'.format(sequence_name))).replace('.gz', '')
    ants.image_write(segmentation_reverse_transformed, registered_segmentation_path)
    registered_segmentation_path = replace_file_with_gzipped_version(registered_segmentation_path)

    
    #Load the maps and registered segmentation as arrays to extract ROI values
    segmentation_reverse_transformed_arr = np.array(segmentation_reverse_transformed[:])
    mask_arr = np.array(ants.image_read(bibsnet_mask_path)[:])
    anatomical_reference_arr = np.array(anatomical_reference[:])

    #Load the freesurfer color lut
    color_lut_df = load_color_lut_df()
    
    #Initialize a dictionary to store all the ROI values/names
    measure_types = ['Mean', 'Median', '1-percentile', '99-percentile', 'Std']
    roi_params_dict = {'Region_Name' : []}
    for temp_image_type in maps_array_dict.keys():
        for temp_measure in measure_types:
            roi_params_dict[temp_image_type + '_' + temp_measure] = []
    
    #Find unique segmentation values########################################################
    ########################################################################################
    print('   Calculating Standard ROI Relaxometry Values')
    unique_segmentation_vals = np.unique(segmentation_reverse_transformed_arr)
    for seg_val in unique_segmentation_vals:
        if seg_val != 0: #Exclude 0 from analyses
            temp_df = color_lut_df[color_lut_df['Region_Number'] == seg_val]
            if temp_df.shape[0] == 0:
                raise ValueError('Error: Segmentation had value [{}] but there was no region with this value found in FreeSurfer Color LUT'.format(seg_val))
            else:
                temp_region_name = temp_df['Region_Name'].values[0]
                roi_params_dict['Region_Name'].append(temp_region_name)
                voxel_inds = segmentation_reverse_transformed_arr == seg_val
                for temp_image_type in maps_array_dict.keys():
                    temp_vals = maps_array_dict[temp_image_type][voxel_inds]
                    roi_params_dict[temp_image_type + '_Mean'].append(np.mean(temp_vals))
                    roi_params_dict[temp_image_type + '_Median'].append(np.median(temp_vals))
                    roi_params_dict[temp_image_type + '_1-percentile'].append(np.percentile(temp_vals, 1))
                    roi_params_dict[temp_image_type + '_99-percentile'].append(np.percentile(temp_vals, 99))
                    roi_params_dict[temp_image_type + '_Std'].append(np.std(temp_vals))

    if os.path.exists(anat_out_dir) == False:
        os.makedirs(anat_out_dir)
    output_tsv_path = os.path.join(anat_out_dir, '{}_{}_desc-ParametricROIValues.tsv'.format(subject_name, session_name))
    params_df = pd.DataFrame(roi_params_dict)
    params_df.to_csv(output_tsv_path, index=False, sep = '\t') 

    mask_inds = mask_arr > 0.5
    mask_corr_coef = np.corrcoef(reg['warpedmovout'][mask_inds], anatomical_reference_arr[mask_inds])[0,1]


    roi_params_metadata = {'Workflow_Description' : 'The values generated in the accompanying csv file are summary statistics from PD/T1/T2 maps that were generated using the qMRI pipeline. A registration was calculated from a high resolution anatomical image to the qMRI maps, and the inverse of this registration was applied to register the segmentation image to the original maps. Summary statistics were then applied within the different regions of interest for the different maps.',
                           'Original_Segmentation_Path' : ["bids:bibsnet:{}".format(bibsnet_seg_path.split(bibsnet_directory)[-1])],
                           'qMRI_Registered_Segmentation_Path' : ["bids:qmri_postproc:{}".format(registered_segmentation_path.split(output_directory)[-1])],
                           'Mask_Path' : ["bids:bibsnet:{}".format(bibsnet_mask_path.split(bibsnet_directory)[-1])],
                           'Anatomical_Reference_Path' : ["bids:assembly_bids:{}".format(anatomical_reference_path.split(bids_directory)[-1])],
                           'Anatomical_Reference_Modality' : anatomical_reference_modality,
                           'Segmentation_Resampling_Scheme' : Segmentation_Interpolation_Scheme,
                           'Voxel_Correlation_Within_Mask' : mask_corr_coef,
                           'Voxel_Correlation_Within_Mask_Description' : 'This is the correlation of voxel intensities between the anatomical reference image and the synthetic weighted image from qmri following registration, using only voxels defined in the brain mask.'}
    
    roi_params_metadata['Original_qMRI_Images'] = []
    for temp_qmri_map in qmri_map_path_dict.keys():
        roi_params_metadata['Original_qMRI_Images'].append("bids:qmri:{}".format(qmri_map_path_dict[temp_qmri_map].split(qmri_directory)[-1]))
    roi_params_metadata.update(grab_anatomical_reference_metadata(anatomical_reference_path))
    roi_params_metadata['Original_qMRI_JSON_Metadata'] = qmri_json_dict

    roi_params_metadata_json = json.dumps(roi_params_metadata, indent = 5)
    output_json_path = os.path.join(anat_out_dir, '{}_{}_desc-ParametricROIValues.json'.format(subject_name, session_name))
    with open(output_json_path, 'w') as f:
        f.write(roi_params_metadata_json)


    ##########################################################################################
    ##########################################################################################
    #Also create csv file for any custom groupings of regions
    if type(custom_roi_groupings) != type(None):
        for temp_grouping_path in custom_roi_groupings:
            print('   Calculating Custom ROI Relaxometry Values for {}'.format(temp_grouping_path))
            custom_roi_params_dict = {'Region_Name' : []}
            for temp_image_type in maps_array_dict.keys():
                for temp_measure in measure_types:
                    custom_roi_params_dict[temp_image_type + '_' + temp_measure] = []


            with open(temp_grouping_path, 'r') as f:
                temp_groupings = json.load(f)
            for temp_grouping in temp_groupings.keys():
                allowed_values = []
                for i, temp_region in enumerate(temp_groupings[temp_grouping]):
                    allowed_values.append(color_lut_df[color_lut_df['Region_Name'] == temp_region]['Region_Number'].values[0])
                
                voxel_inds = segmentation_reverse_transformed_arr == allowed_values[0]
                for i in range(len(allowed_values)):
                    voxel_inds = voxel_inds + (segmentation_reverse_transformed_arr == allowed_values[i])
                for x, temp_image_type in enumerate(maps_array_dict.keys()):
                    temp_vals = maps_array_dict[temp_image_type][voxel_inds]
                    try:
                        temp_mean = np.mean(temp_vals)
                        temp_median = np.median(temp_vals)
                        temp_1pct = np.percentile(temp_vals, 1)
                        temp_99pct = np.percentile(temp_vals, 99)
                        temp_std = np.std(temp_vals)

                        custom_roi_params_dict[temp_image_type + '_Mean'].append(temp_mean)
                        custom_roi_params_dict[temp_image_type + '_Median'].append(temp_median)
                        custom_roi_params_dict[temp_image_type + '_1-percentile'].append(temp_1pct)
                        custom_roi_params_dict[temp_image_type + '_99-percentile'].append(temp_99pct)
                        custom_roi_params_dict[temp_image_type + '_Std'].append(temp_std)
                        if x == 0:
                            custom_roi_params_dict['Region_Name'].append(temp_grouping)
                    except:
                        if temp_vals.shape[0] == 0:
                            print('   Warning: No voxels found in {}. Region will not be included in CSV.'.format(temp_grouping))
                        else:
                            raise ValueError('   Error: Unknown error when calculating custom summary statistics for {}.'.format(temp_grouping))

            temp_grouping_partial_name = temp_grouping_path.split('/')[-1].replace('.json', '')
            output_tsv_path = os.path.join(anat_out_dir, '{}_{}_desc-{}.tsv'.format(subject_name, session_name, temp_grouping_partial_name))
            params_df = pd.DataFrame(custom_roi_params_dict)
            params_df.to_csv(output_tsv_path, index=False, sep = '\t') 

            custom_roi_params_metadata = {'Workflow_Description' : 'The values generated in the accompanying csv file are summary statistics from PD/T1/T2 maps that were generated using the qMRI pipeline. A registration was calculated from a high resolution anatomical image to the qMRI maps, and the inverse of this registration was applied to register the segmentation image to the original maps. Summary statistics were then applied within the different regions of interest for the different maps.',
                           'Original_Segmentation_Path' : ["bids:bibsnet:{}".format(bibsnet_seg_path.split(bibsnet_directory)[-1])],
                           'qMRI_Registered_Segmentation_Path' : ["bids:qmri_postproc:{}".format(registered_segmentation_path.split(output_directory)[-1])],
                           'Mask_Path' : ["bids:bibsnet:{}".format(bibsnet_mask_path.split(bibsnet_directory)[-1])],
                           'Anatomical_Reference_Path' : ["bids:assembly_bids:{}".format(anatomical_reference_path.split(bids_directory)[-1])],
                           'Anatomical_Reference_Modality' : anatomical_reference_modality,
                           'Segmentation_Resampling_Scheme' : Segmentation_Interpolation_Scheme,
                           'Voxel_Correlation_Within_Mask' : mask_corr_coef,
                           'Voxel_Correlation_Within_Mask_Description' : 'This is the correlation of voxel intensities between the anatomical reference image and the synthetic weighted image from qmri following registration, using only voxels defined in the brain mask.'}
            custom_roi_params_metadata.update(grab_anatomical_reference_metadata(anatomical_reference_path))
            custom_roi_params_metadata['Original_qMRI_JSON_Metadata'] = qmri_json_dict
            custom_roi_params_metadata['Custom_ROI_Grouping'] = temp_groupings
            roi_params_metadata['Original_qMRI_Images'] = []
            for temp_qmri_map in qmri_map_path_dict.keys():
                roi_params_metadata['Original_qMRI_Images'].append("bids:qmri:{}".format(qmri_map_path_dict[temp_qmri_map].split(qmri_directory)[-1]))
            custom_roi_params_metadata_json = json.dumps(custom_roi_params_metadata, indent = 5)
            output_json_path = os.path.join(anat_out_dir, '{}_{}_desc-{}.json'.format(subject_name, session_name, temp_grouping_partial_name))

            with open(output_json_path, 'w') as f:
                f.write(custom_roi_params_metadata_json)


    #########################################################################################################
    #########################################################################################################
    
    #Add json metadata for the PD/T1/T2map images that have been registered to the anatomical template
    resampled_images_metadata = {'Workflow_Description' : 'The values generated in the accompanying images are the quantitative maps that have been registered and resampled to a high-resolution native image for the subject (see Anatomical_Reference_Path for the image that was registered to).',
                           'Segmentation_Path' : ["bids:bibsnet:{}".format(bibsnet_seg_path.split(bibsnet_directory)[-1])],
                           'Mask_Path' : ["bids:bibsnet:{}".format(bibsnet_mask_path.split(bibsnet_directory)[-1])],
                           'Anatomical_Reference_Path' : ["bids:assembly_bids:{}".format(anatomical_reference_path.split(bids_directory)[-1])],
                           'Anatomical_Reference_Modality' : anatomical_reference_modality,
                           'Resampling_Scheme' : Map_Interpolation_Scheme}
    roi_params_metadata['Original_qMRI_Images'] = []
    for temp_qmri_map in qmri_map_path_dict.keys():
        roi_params_metadata['Original_qMRI_Images'].append("bids:qmri:{}".format(qmri_map_path_dict[temp_qmri_map].split(qmri_directory)[-1]))
    resampled_images_metadata.update(grab_anatomical_reference_metadata(anatomical_reference_path))
    resampled_images_metadata['Original_qMRI_JSON_Metadata'] = qmri_json_dict
    resampled_images_metadata_json = json.dumps(resampled_images_metadata, indent = 5)
    for temp_qmri_map in qmri_map_path_dict.keys():
        output_json_path = os.path.join(anat_out_dir, '{}_{}_space-{}_desc-{}_{}map.json'.format(subject_name, session_name, anatomical_reference_modality, sequence_name, temp_qmri_map))
        with open(output_json_path, 'w') as f:
            f.write(resampled_images_metadata_json) 
    
    #Make a figure with the segmentation as overlay and t2map as underlay to assess registration quality
    alignment_figure_output = os.path.join(anat_out_dir, '{}_{}_desc-RegistrationQCAid.png'.format(subject_name, session_name))
    if 'T2' in registered_maps_paths.keys():
        registered_path_for_underlay = registered_maps_paths['T2']
    elif 'T1' in registered_maps_paths.keys():
        registered_path_for_underlay = registered_maps_paths['T1']
    elif 'PD' in registered_maps_paths.keys():
        registered_path_for_underlay = registered_maps_paths['PD']
    else:
        raise ValueError('Error: Expected to have at least one of T1, T2, or PD maps but none were found.')
    
    make_outline_overlay_underlay_plot_ribbon(registered_path_for_underlay, bibsnet_seg_path, ap_buffer_size = 3, crop_buffer=20, num_total_images=9, dpi=400,
                                    underlay_cmap='Greys', linewidths=.1, output_path=alignment_figure_output, close_plot=True)
    with open(alignment_figure_output.replace('.png', '.json'), 'w') as f:
        alignment_figure_metadata = {'Workflow_Description' : 'The image generated in the accompanying figure is a visual representation of the registration quality of the segmentation image to the high resolution anatomical image. The underlay is a quantitative image that has been registered to the anatomical image, and the overlay is the segmentation image that has been registered to the T2map image. The figure is intended to be used as a quality control aid to assess the registration quality of the segmentation image to the anatomical image.',
                                     'Segmentation_Path' : ["bids:bibsnet:{}".format(bibsnet_seg_path.split(bibsnet_directory)[-1])],
                                     'Underlay_Path' : ["bids:qmri_postproc:{}".format(registered_path_for_underlay.split(output_directory)[-1])],
                                     }
        json.dump(alignment_figure_metadata, f, indent = 5)

    return