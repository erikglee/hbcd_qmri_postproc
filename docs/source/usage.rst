.. HBCD_SYMRI_POSTPROC documentation master file, created by
   sphinx-quickstart on Wed Jun  5 10:48:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _usage:
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

The design of the application is meant to follow general 
`BIDS-App guidelines <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005209>`_.
For more details on general usage principles of BIDS-Apps, see the linked documentation.

As described in the installation section, this tool is meant to be
interacted with in containerized form. The example below shows the
general layout for how you may want to interact with the container
to conduct processing if you have the container downloaded as a
singularity image: ::


      container_path=/path/to/container.sif
      bids_dir=/path/to/bids
      output_dir=/path/to/output
      symri_dir=/path/to/symri
      bibsnet_dir=/path/to/bibsnet

      singularity run -B $bids_dir:/bids \
            -B $output_dir:/output \
            -B $symri_dir:/symri \
            -B $bibsnet_dir:/bibsnet \
            $container_path /data /output participant /symri /bibsnet

To see more specific information about how this tool expects
the inputs to be formatted (i.e. file naming conventions), 
see the inputs formatting page.


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