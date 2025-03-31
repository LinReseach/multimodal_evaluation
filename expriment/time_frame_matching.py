#####################################################################
## NOTE: YOU HAVE IMPORT THE CSV AND SELECT 'Text' FOR THE ID      ##
#####################################################################

import json
import os
import pandas as pd
import numpy as np
participant = '4'

file_round_info = 'round_info'
file_data = 'data'

def execute_csv(filename, camera_info: pd.DataFrame, camera_type: str, eyetracker_mode, calibration_formal_mode = 'formal'):
    ## Prepare the round_info and camera CSV's.
    csv_info = pd.read_csv(filename + file_round_info + '.csv', sep = ';', index_col=[0])    # Load the data into a DataFrame
    camera_info = pd.DataFrame(camera_info)
    camera_info['camera'] = camera_type
    camera_info['eyetracker_mode'] = eyetracker_mode
    camera_info['ID'] = camera_info['ID'].astype("string")
    camera_info['time'] # Add the two hour difference
    merged = merge_infos(csv_info, camera_info, is_calibration_mode(calibration_formal_mode))
    #print(f'Camera type: {camera_type}')
    #print('MERGED COLUMNS:')
    #print(merged.columns)
    
    # Now that the merged file was created, check if there was already an existing file with data.
    # If so, merge.
    filename = filename + file_data + '.csv'
    if os.path.isfile(filename):
        #print(f'filename: {filename}')
        previous_csv = pd.read_csv(filename, sep = ';', dtype={'ID':'str'}, index_col=[0])
        #print(f'Previous CSV columns 1st:')
        #print(previous_csv.columns)
        previous_csv['ID'] = previous_csv['ID'].astype("string")

        #print(f'Previous CSV columns 2nd:')
        #print(previous_csv.columns)
        merged = pd.concat([merged, previous_csv])
        #print("MERGED CONCATENATED")
        #print(merged.columns)
    
    #merged['time'] = pd.to_datetime(merged['time'])
    merged = merged.sort_values('time')
    merged.to_csv(filename, sep = ';')

def merge_infos(frame_info: pd.DataFrame, camera_info: pd.DataFrame, is_calibration):
    # Prepare the DataFrames for further processing (such as types, indexing, etc.)
    camera_info['ID'] = camera_info['ID'].astype("string")
    #camera_info['time'] = pd.to_datetime(camera_info['time'], unit='s') + pd.Timedelta('02:00:00')
    #camera_info['timestamp'] = camera_info['time']
    camera_info = camera_info.sort_values('time')
    frame_info['start']
    frame_info['end']
    #frame_info['start'] = pd.to_datetime(frame_info['start'], unit='s') + pd.Timedelta('02:00:00')
    #frame_info['end'] = pd.to_datetime(frame_info['end'], unit='s') + pd.Timedelta('02:00:00')
    if not is_calibration:
        #frame_info['duration'] = pd.to_datetime(frame_info['duration'], unit='s')
        frame_info['duration'] = frame_info['duration']
    
    # Create a boolean mask indicating which rows fall within the specified ranges
    within_ranges = (camera_info['time'].values[:, np.newaxis] >= frame_info['start'].values) & (camera_info['time'].values[:, np.newaxis] <= frame_info['end'].values)
    for column in frame_info.columns:
        camera_info[column] = np.nan
    camera_info[frame_info.columns] = np.where(within_ranges.any(axis=1)[:, np.newaxis], frame_info.values[np.argmax(within_ranges, axis=1)], np.nan)
    #print(data_experiment_camera.columns)
    if not is_calibration:
        camera_info = camera_info.rename(columns={  'valid':'wasakeypressed',
                                                'direction':'direction_of_focus',
                                                'first_item':'focus_modality',
                                                'second_item':'secondary_modality'
                                            })
        camera_info = camera_info.rename(columns={'duration':'response_time'})
        #camera_info = camera_info.drop('trial_id', axis=1)
    return camera_info

def is_calibration_mode(calibration_formal_mode):
    return True if calibration_formal_mode == 'calibration' else False