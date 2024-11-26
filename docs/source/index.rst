.. HBCD_qMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to hbcd_qmri_postproc's documentation!
===============================================

.. image:: https://zenodo.org/badge/648286022.svg
   :target: https://zenodo.org/doi/10.5281/zenodo.13743262

This tool is used in the Healthy Brain and Child Development (HBCD) study
to run minimal post-processing on synthetic images generated from `SyMRI <https://syntheticmr.com/products/symri-neuro/>`_
tools using the `QALAS acquisition <https://pubmed.ncbi.nlm.nih.gov/25526880/>`_.
The purpose of the tool is to take quantitative maps, register them to
either raw T1w or T2w images where anatomical segmentations have already
been performed, and then extract quantitative values within regions of interest.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   usage
   inputs_formatting
   outputs
