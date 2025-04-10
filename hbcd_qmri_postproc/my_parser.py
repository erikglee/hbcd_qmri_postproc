#!/usr/local/bin/python3
import argparse

def build_parser():

    #Configure the commands that can be fed to the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("bids_dir", help="The path to the BIDS directory for your study (this is the same for all subjects)", type=str)
    parser.add_argument("output_dir", help="The path to the folder where outputs will be stored (this is the same for all subjects)", type=str)
    parser.add_argument("analysis_level", help="Should always be participant", type=str)
    parser.add_argument("qmri_deriv_dir", help="The path to the folder where the qMRI Relaxometry Maps are stored (this is the same for all subjects)", type=str)
    parser.add_argument("bibsnet_deriv_dir", help="The path to the folder where the BIBSNET/CABINET segmentations are stored (this is the same for all subjects)", type=str)


    parser.add_argument('--participant_label', '--participant-label', help="The name/label of the subject to be processed (i.e. sub-01 or 01)", type=str)
    parser.add_argument('--session_id', '--session-id', help="OPTIONAL: the name of a specific session to be processed (i.e. ses-01)", type=str)
    parser.add_argument('--overwrite_existing', help='OPTIONAL: if flag is activated, the tool will delete the session folder where outputs are to be stored before processing if said folder already exists.', action='store_true')
    parser.add_argument('--skip_existing', help='OPTIONAL: if flag is activated, the tool will skip processing for a session if the session folder where outputs are to be stored already exists.', action='store_true')
    parser.add_argument('--region_groupings_json', nargs='+', help='OPTIONAL: the path to a json file containing region groupings for which to calculate statistics. Multiple files can be provided, resulting in multiple output csv files.', type=str)
    parser.add_argument('--sequence_name_source', help='OPTIONAL: the the key for the key/value pair to try and grab sequence name from. For example if the qMRI file is named sub-1_acq-QALAS.nii.gz, this should be "acq". If the sequence is found, it will be represented as "quant" in the output files.', type=str, default = 'acq')
    parser.add_argument('--ants_reg_metric', '--ants-reg-metric', help="The registration metric used in ANTS, options are mattes (default), GC, meansquares", type=str, choices=['mattes', 'GC', 'meansquares'], default='mattes')
    parser.add_argument('--ants_reg_type', '--ants-reg-type', help="The registration type used in ANTS, options are Rigid (default), Similarity, Affine", type=str, choices=['Rigid', 'Similarity', 'Affine'], default='Rigid')

    return parser