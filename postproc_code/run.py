#!/usr/local/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import qmri_postproc
import os, glob, shutil
import argparse
from my_parser import build_parser



def main():
    parser = build_parser()
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
    qmri_deriv_dir = args.qmri_deriv_dir
    if os.path.isabs(qmri_deriv_dir) == False:
        qmri_deriv_dir = os.path.join(cwd, qmri_deriv_dir)
    bibsnet_deriv_dir = args.bibsnet_deriv_dir
    if os.path.isabs(bibsnet_deriv_dir) == False:
        bibsnet_deriv_dir = os.path.join(cwd, bibsnet_deriv_dir)
    if type(args.region_groupings_json) != type(None):
        region_groupings_json = []
        for temp_grouping_json in args.region_groupings_json:
            if os.path.isabs(temp_grouping_json) == False:
                temp_grouping_json = os.path.join(cwd, temp_grouping_json)
            region_groupings_json.append(temp_grouping_json)
    else:
        region_groupings_json = None

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

            session_path = os.path.join(output_dir, temp_participant, temp_session)
            if os.path.exists(session_path) and args.skip_existing:
                print('Session folder already exists at the following path. Skipping: ' + session_path)
                continue
            elif os.path.exists(session_path) and args.overwrite_existing:
                shutil.rmtree(session_path)
                print('Removing existing session folder at: ' + session_path)
            elif os.path.exists(session_path):
                print('Session folder already exists at the following path. Either delete folder, run with --overwrite_existing flag to reprocess, or with --skip_existing to ignore existing folders: ' + session_path)
                continue
            print('Starting processing for: {}, {}'.format(temp_participant, temp_session))
            if os.path.exists(os.path.join(qmri_deriv_dir, temp_participant, temp_session)) == False:
                print('   No qMRI Relaxometry Maps directory found for the following, skipping processing: {}, {}'.format(temp_participant, temp_session))
                continue
            if os.path.exists(os.path.join(bibsnet_deriv_dir, temp_participant, temp_session)) == False:
                print('   No BIBSNET/CABINET segmentations directory found for the following, skipping processing: {}, {}'.format(temp_participant, temp_session))
                continue
            qmri_postproc.calc_qmri_stats(bids_dir, bibsnet_deriv_dir,
                                        qmri_deriv_dir, output_dir,
                                        temp_participant, temp_session,
                                        custom_roi_groupings = region_groupings_json,
                                        sequence_name_source = args.sequence_name_source)
            print('Finished with: {}, {}'.format(temp_participant, temp_session))

if __name__ == "__main__":
    main()