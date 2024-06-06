.. HBCD_SYMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Usage
=====

There are three primary inputs to the HBCD_SYMRI_POSTPROC tool.
In each case, the input is provided as a "study-wide" folder, such
that the tool can be run on multiple subjects at once. These three
directories include the BIDS directory, the
relaxometry maps directory, and the segmentations directory.

At the time this application is run, there should be subject (and session,
if desired) specific folders for each subject you want to process. Processing will iterate
through each subject in the BIDS directory, find associated sessions
with the relevant data, and create the necessary folders and files in the
output directory. Processing is totally independent across subjects and sessions,
so that the results will be the same if the subjects are processed in parallel or
through a single call of this application.



Example: ::

   hbcd_symri_postproc /bids_root /out participant /symri_deriv_dir /bibsnet_deriv_dir

To see more specific information about how this tool expects
the inputs to be formatted, see the inputs formatting page.


Command-Line Arguments
======================
.. argparse::
   :ref: postproc_code.my_parser.build_parser
   :prog: hbcd_symri_postproc
   :nodefault:
   :nodefaultconst:

.. toctree::
   :maxdepth: 2
   :caption: Contents: