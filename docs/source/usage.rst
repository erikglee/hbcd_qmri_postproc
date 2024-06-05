.. HBCD_SYMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HBCD_SYMRI_POSTPROC Usage
===============================================

There are three primary inputs to the HBCD_SYMRI_POSTPROC tool.
In each case, the input is provided as a "study-wide" folder, such
that the tool can be run on multiple subjects at once. These three
directories include the BIDS directory, the output directory, the
relaxometry maps directory, and the segmentations directory.

At the time this application is run, there should be subject (and session,
if desired) specific folders for each subject you want to process under the
BIDS, relaxometry, and segmentation directories. Processing will iterate
through each subject in the BIDS directory, find the associated sessions
having the relevant data, and create the necessary folders and files in the
output directory. Processing is totally independent across subjects and sessions,
so that the results will be the same if the subjects are processed in parallel or
through a single call of this application.

Example: ::

   hbcd_symri_postproc /bids_root /out participant /symri_deriv_dir /bibsnet_deriv_dir


Command-Line Arguments
----------------------
.. argparse::
   :ref: code.cli.parser._build_parser
   :prog: code
   :nodefault:
   :nodefaultconst:

This tool is used in the Healthy Brain and Child Development (HBCD) study
following the conversion of QALAS acquisitions to T1, T2, and PD maps.
The purpose of the tool is to take quantitative maps, register them to
either raw T1w or T2w images where anatomical segmentations have already
been performed, and then extract quantitative values from the segmentations.

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
