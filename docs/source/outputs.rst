.. HBCD_SYMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Outputs
=======

The application outputs will generally mirror the structure
of the inputs. If there is session structure in the inputs,
the primary output folder of interest will be as follows: ::

    <output_dir>/sub-{label}/ses-{label}/anat/

During processing, the application will generate synthetic T1w/T2w
images under the "qalas_derived_weighted_images" folder. These images
are created to have the following parameters: ::

    T1: TR = XXms, TE = XXms
    T2: TR = XXms, TE = XXms

These synthetic images will be used to register the relaxometry maps
to either the T1w or T2w image using a rigid transformation in ANTS.
New versions of the relaxometry maps in this new space will be created
using bSpline interpolation, with the following naming convention: ::

    <output_dir>/sub-{label}/ses-{label}/anat/sub-{label}_ses-{label}_space-{label}_desc-QALAS_T1map.nii.gz
    <output_dir>/sub-{label}/ses-{label}/anat/sub-{label}_ses-{label}_space-{label}_desc-QALAS_T2map.nii.gz
    <output_dir>/sub-{label}/ses-{label}/anat/sub-{label}_ses-{label}_space-{label}_desc-QALAS_PDmap.nii.gz

Where the space label will either be T1w or T2w, depending on which image
was used for registration.

Further, the described transformation will be reverse-applied to the
segmentation image so that the segmentation image is in the same space
as the original relaxometry maps. The updated segmentation will be generated
using nearest neighbor interpolation, and will have "space-QALAS" in the
naming convention to denote that it is in the same space as the relaxometry maps.

The values in the segmentation will be used with the FreeSurferColorLUT to define
region names. For every region found in the segmentation - mean, median,
1st percentile, 99th percentile, and standard deviation values will be calculated.
These summary values will be grabbed from the T1, T2, and PD map images. 

Summary statistics will then be saved in a CSV file with the following naming convention: ::

    <output_dir>/sub-{label}/ses-{label}/anat/sub-{label}_ses-{label}_desc-ParametricROIValues.csv

If a user also provides one or more custom ROI grouping files through the
region_groupings_json flag, there will be additional csv files that describe
the custom groupings. The name of the csv file will mimic the name of the input
json file that was used to define the groupings.

Finally, the application will produce a figure that can be used to visualize
the quality of the registration between the relaxometry maps and the T1w/T2w
anatomical reference. The figure will show the T2map that has been registered
to the anatomical reference, with the outlines of the segmentation overlaid
on top. The figure will be saved in the following location: ::

    <output_dir>/sub-{label}/ses-{label}/anat/sub-{label}_ses-{label}_desc-RegistrationQCAid.png


The units of the outputs will follow the units of the input relaxometry maps. In
the case where the inputs are SyMRI defined relaxometry maps, the units will be
as follows: ::

    T1: ms
    T2: ms
    PD: XX


.. toctree::
   :maxdepth: 2
   :caption: Contents: