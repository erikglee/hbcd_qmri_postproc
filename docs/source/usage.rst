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

| **Positional:**
|
| **bids_dir**

   Path to study-wide BIDS directory.
|
| **output_dir**

   Path to study-wide output directory.
|
| **analysis_level** - Always "participant". Meant to represent that processing only occurs within a given participant.
|
| **symri_deriv_dir** - Path to study-wide SyMRI/Relaxometry directory.
|
| **bibsnet_deriv_dir** - Path to study-wide BIBSNET/Segmentation directory.
|
| **Optional Flags:**
|
| **--participant_label** - List of space-delimited participant identifiers to process. If flag isn't provided all subjects will be processed.
|
| **--session_id** - The name of a single session to process. If flag isn't provided all sessions will be processed.
|
| **--overwrite_existing** - If flag is activated, the tool will delete the session folder where outputs are to be stored before processing if said folder already exists.
|
| **--skip_existing** - If flag is activated, the tool will skip processing for a session if the session folder where outputs are to be stored already exists.
|
| **--region_groupings_json** - The path to a json file containing region groupings for which to calculate statistics. Multiple files can be provided, resulting in multiple output csv files.
|

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
