.. HBCD_SYMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation
============

The intended use of this pipeline is through the use of a Singularity/Docker
image. The image can be built using the Dockerfile found in the repository,
or it can be pulled from DockerHub as a singularity using the following command: ::
    
        singularity pull docker://dcanumn/hbcd_symri_postproc:<version_num>

Where version_num denotes the specific version of the container. All available
versions of the container can be found `here <https://hub.docker.com/r/dcanumn/hbcd_symri_postproc/tags>`_.

BIDS directory
--------------

The BIDS directory should have exactly one T1w and/or T2w image
for each session that will be processed. The T1w and/or T2w image
should already be registered to the segmentation(s) found in the
segmentations directory. If both T1w/T2w images and segmentations
are present, the pipeline will currently (as of 6/5/24) give priority
to registering the relaxometry images to the T2w images.