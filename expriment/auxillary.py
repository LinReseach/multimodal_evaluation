import os
import json
import pandas as pd
import time
import cv2 as cv
from time_frame_matching import execute_csv

# Pretty prints the current stage in the terminal
def show_current_stage(value):
    string_func = lambda x: ''.join(["=" for _ in range(len(x))])
    print("")
    print(f"====={string_func(value)}=====")
    print(f"===  {value}  ===")
    print(f"====={string_func(value)}=====")

# Determines for the first item if which direction it has to go.
def left_or_right(congruent, direction):
    if (congruent and direction == 'left') or (not congruent and direction == 'right'):
        return 'left'
    else: 
        return 'right'

# Checks with the participant if they are ready for the next set of trials.
def confirm_ready():
    ready_for_next = ''
    while not (ready_for_next == 'Y' or ready_for_next == 'y'):
        ready_for_next = input("Pausing. Ready to continue? [Y/n]")
    return True

# This function appends data to the end of a file (useful for saving trialdata)
folder_data = './data/'
def dump_trialset_to_json(data: pd.DataFrame, video_name):
    data = pd.DataFrame([{**{"index": k}, **v, **v.pop("keystroke")} for k, v in data.items()]).set_index('index')
    data.drop(columns='keystroke', inplace=True)
    #data['trial_round'] = trial_round
    if os.path.isfile(video_name):
        data = pd.concat([data, pd.read_csv(video_name)])
    #data_experiment_round_info = pd.concat([data_experiment_round_info, data])
    data.to_csv(video_name, sep = ';')


# This function creates the data folder and the folder for the data of a specific participant
def create_data_folders(participant_id):
    os.makedirs(folder_data, exist_ok = True)
    os.makedirs(get_participant_folder(participant_id), exist_ok = True)

def get_participant_folder(participant_id):
    return folder_data + f'part_{participant_id}/'

def save_dataframe_to_csv(filename, camera_info, camera_type: str, eyetracker_mode, calibration_formal_mode):
    execute_csv(filename, camera_info, camera_type, eyetracker_mode, calibration_formal_mode)
    print(f"[I/O] Finished writing {camera_type} to csv")

def append_info_to_list(_frameless_list, _i):
    formatted_i = '{:07}'.format(int(_i))
    _frameless_data = {
        'ID':formatted_i,
        'time':time.time()
    }
    _frameless_list.append(_frameless_data)
    _i = int(_i)
    _i += 1
    return _frameless_list, _i

def get_brio_id():
    v4l2path = "/sys/class/video4linux/"
    for camera_id in sorted(os.listdir(v4l2path)):
        camera_path = v4l2path + camera_id + '/name'
        camera_name = open(camera_path, 'r').read()
        #return 0
        #'''
        if "BRIO" in camera_name:
            camera_id = int(camera_id.replace('video',''))
            cap = cv.VideoCapture(camera_id)
            cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G')) 
            cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv.CAP_PROP_FRAME_HEIGHT,1080)
            cap.set(cv.CAP_PROP_FPS, 60)

            # Get the resolution
            width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv.CAP_PROP_FPS))
            #print(f"Resolution W: {width} - H: {height} - FPS: {fps}")
            if width < 1920 or height < 1080 or fps < 60:
                #print(f'cameraID: {camera_id} does not support 1080p 60fps - w:{width}, h:{height}, fps:{fps}')
                pass
            else:
                #print(f'cameraID: {camera_id} supports 1080p 60fps - w:{width}, h:{height}, fps:{fps}')
                return camera_id
        #'''

def csv_with_rounds_exists(participant_id, round, eyetracker_mode, calibration_formal_mode):
    etm = 'glasses' if eyetracker_mode else 'noglasses'
    path = f'./data/part_{participant_id}/{etm}_{calibration_formal_mode}_data.csv'
    if os.path.exists(path):
        input(f"WARNING: FILE ALREADY EXISTS! {path}")