#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import os, glob
import dipy
import nibabel as nib
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from dipy import align
import dipy
import argparse
import process
from dipy.align.imaffine import (AffineMap,
                                 MutualInformationMetric,
                                 AffineRegistration)
from dipy.align.transforms import (TranslationTransform3D,
                                   RigidTransform3D)


#Steps we want to take:
#1. Identify the T1, T2, PD files from SyMRI
#2. Identify the CABINET segmentation + brain mask file,
#   along with the corresponding T1w and/or T2w image.
#3. Create synthetic T1w image
#4. Register the synthetic T1w image to the real T1w image
#5. Make new copies of T1/T2/PD that are registered to T1w
#6. Grab T1/T2/PD values for different regions of interest
#7. Save registration between SyMRI and T1w



#Configure the commands that can be fed to the command line
parser = argparse.ArgumentParser()
parser.add_argument("bids_dir", help="The path to the BIDS directory for your study (this is the same for all subjects)", type=str)
parser.add_argument("output_dir", help="The path to the folder where outputs will be stored (this is the same for all subjects)", type=str)
parser.add_argument("analysis_level", help="Should always be participant", type=str)
parser.add_argument("symri_deriv_dir", "The path to the folder where the SyMRI Relaxometry Maps are stored (this is the same for all subjects)", type=str)
parser.add_argument("bibsnet_deriv_dir", "The path to the folder where the BIBSNET/CABINET segmentations are stored (this is the same for all subjects)", type=str)


parser.add_argument('--participant_label', '--participant-label', help="The name/label of the subject to be processed (i.e. sub-01 or 01)", type=str)
parser.add_argument('--session_id', '--session-id', help="OPTIONAL: the name of a specific session to be processed (i.e. ses-01)", type=str)
args = parser.parse_args()


#Get cwd in case relative paths are given
cwd = os.getcwd()

#reassign variables to command line input
bids_dir = args.bids_dir
if os.path.isabs(bids_dir) == False:
    bids_dir = os.path.join(cwd, bids_dir)
output_dir = args.output_dir
if os.path.isabs(output_dir) == False:
    output_dir = os.path.join(cwd, output_dir)
analysis_level = args.analysis_level
if analysis_level != 'participant':
    raise ValueError('Error: analysis level must be participant, but program received: ' + analysis_level)
symri_deriv_dir = args.symri_deriv_dir
if os.path.isabs(symri_deriv_dir) == False:
    symri_deriv_dir = os.path.join(cwd, symri_deriv_dir)
bibsnet_deriv_dir = args.bibsnet_deriv_dir
if os.path.isabs(bibsnet_deriv_dir) == False:
    bibsnet_deriv_dir = os.path.join(cwd, bibsnet_deriv_dir)

#Set session label
if args.session_id:
    session_label = args.session_id
    if 'ses-' not in session_label:
        session_label = 'ses-' + session_label
else:
    session_label = None
    
#Find participants to try running
if args.participant_label:
    participant_split = args.participant_label.split(' ')
    participants = []
    for temp_participant in participant_split:
        if 'sub-' not in temp_participant:
            participants.append('sub-' + temp_participant)
        else:
            participants.append(temp_participant)
else:
    os.chdir(bids_dir)
    participants = glob.glob('sub-*')
    
#Iterate through all participants
for temp_participant in participants:
    
    #Check that participant exists at expected path
    subject_path = os.path.join(bids_dir, temp_participant)
    if os.path.exists(subject_path):
        os.chdir(subject_path)
    else:
        raise AttributeError('Error: no directory found at: ' + subject_path)
    
    #Find session/sessions
    if session_label == None:
        sessions = glob.glob('ses*')
        if len(sessions) < 1:
            sessions = ['']
    elif os.path.exists(session_label):
        sessions = [session_label]
    else:
        raise AttributeError('Error: session with name ' + session_label + ' does not exist at ' + subject_path)

    #Iterate through sessions
    for temp_session in sessions:

        #If there is no session structure, this will go to the subject path
        session_path = os.path.join(subject_path, temp_session)

        #Grab T1w file
        anats_dict = {}
        t1_anats = glob.glob(os.path.join(session_path,'anat/*T1w.ni*'))
        anats_dict['T1w_images'] = t1_anats
        
        #Grab T2w file
        t2_anats = glob.glob(os.path.join(session_path,'anat/*T2w.ni*'))
        anats_dict['T2w_images'] = t2_anats
        
        for temp_t1w in anats_dict['T1w_images']:
            registered_nii_for_slice_img, masked_image = process.register_images(temp_t1w, output_dir)
            slice_img_path = registered_nii_for_slice_img.replace('T1w.nii', 'T1w_image-slice.png')
            slice_img_path = slice_img_path.replace('slice.png.gz', 'slice.png') #For case when nifti is compressed
            if matplotlib_contrast == False:
                process.make_slices_image(registered_nii_for_slice_img, slice_info_dict, slice_img_path, close_plot = True,
                        upsample_factor = 2, mask_path = masked_image)
            else:
                process.make_slices_image(registered_nii_for_slice_img, slice_info_dict, slice_img_path, close_plot = True,
                        upsample_factor = 2)
            
            
        for temp_t2w in anats_dict['T2w_images']:
            registered_nii_for_slice_img, masked_image = process.register_images(temp_t2w, output_dir)
            slice_img_path = registered_nii_for_slice_img.replace('T2w.nii', 'T2w_image-slice.png')
            slice_img_path = slice_img_path.replace('slice.png.gz', 'slice.png') #For case when nifti is compressed
            if matplotlib_contrast == False:
                process.make_slices_image(registered_nii_for_slice_img, slice_info_dict, slice_img_path, close_plot = True,
                        upsample_factor = 2, mask_path = masked_image)
            else:
                process.make_slices_image(registered_nii_for_slice_img, slice_info_dict, slice_img_path, close_plot = True,
                        upsample_factor = 2)

        print('Finished with: {}'.format(session_path))