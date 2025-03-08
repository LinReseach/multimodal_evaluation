import queue
import cv2
from sic_framework.core.message_python2 import CompressedImageMessage
from sic_framework.devices.common_naoqi.naoqi_camera import NaoqiCameraConf
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import PlayRecording, NaoqiMotionRecording
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoBasicAwarenessRequest, NaoBackgroundMovingRequest, NaoWakeUpRequest
from sic_framework.devices.pepper import Pepper
from sic_framework.devices.common_naoqi.naoqi_text_to_speech import NaoqiTextToSpeechRequest
# The functions in this file are mostly based from the OpenVC VideoCapture tutorial, which can be found here:
# https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

import cv2 as cv
import time
import pandas as pd
import sys
import os

from auxillary import show_current_stage,  save_dataframe_to_csv, append_info_to_list, get_brio_id, create_data_folders
from recorder import Recorder
from threader import Threader, write_single_frame
from settings import participant_id, ip, has_eyetracker, is_training
from tablet import show_tablet_empty, set_pepper_tablet

############################################################
def run_calibration(video_recorder: Recorder):
    # Parameters
    current_focus_point = 0
    time_inbetween = 4
    
    '''
    focus_point = [
        ' ',
        'please look at my head camera',
        'please look at my face',
        'please look at my tablet',
        'please look at  left elbow',
        'please look at  right elbow',
        'the part ended, please take off your glasses',
        ' ',
        'please look at my head camera',
        'please look at my face ',
        'please look at my tablet',
        'please look at  left elbow',
        'please look at  right elbow',
        'calibration finished! thank you very much!',
        '']
    '''
    
    focus_point = [
        f'This calibration is for {"with" if video_recorder.get_is_eyetracker() else "without"} eyetracker',
        ' ',
        'please look at my head camera',
        'please look at my nose',
        'please look at my tablet',
        'please look at  left elbow',
        'please look at  right elbow',
        'calibration finished! thank you very much!',
        '',
        '']

    '''
    focus_point = [
        ' ',
        'please look at my head camera',
        'please look at my face']
    #'''

    time.sleep(2)
    nao.tts.request(NaoqiTextToSpeechRequest('please get in front of the Pepper'))
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[1], recorded_joints=["LShoulderRoll"], recorded_times=[[1]])))
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[-1], recorded_joints=["RShoulderRoll"], recorded_times=[[1]])))
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, -.3], recorded_joints=['HeadPitch'], recorded_times=[[0, 1]])))
    
    # This line for some reason causes a slight movement of the HeadYaw to the left or right.
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, -.4], recorded_joints=['HeadPitch'], recorded_times=[[0, 1]]))) 
    
    # Recalibrate the head yaw to be centered
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[-0.5, 0.5, 0], recorded_joints=['HeadYaw'], recorded_times=[[0, 1, 2]])))
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, 0], recorded_joints=['HeadYaw'], recorded_times=[[0, 1]])))

    # Time tracking
    current_time = time.time()
    start_time = time.time()

    # Actually execute the motions
    round_info = pd.DataFrame(columns = ['start','end','speech'])
    print(f"4K Starting I: {video_recorder.get_current_i()}")
    while len(focus_point) > current_focus_point:       
        if current_time > start_time + time_inbetween:
            # Finish up the previous instruction
            print(f"4K's Finishing I: {video_recorder.get_current_i()}")
            print(f'Just executed: {focus_point[current_focus_point]}')
            new_data = {
                'start': start_time,
                'end': current_time, # This is the start_time + time_inbetween combined.
                'speech':focus_point[current_focus_point]}
            round_info.loc[len(round_info.index)] = new_data

            # Start the new instruction
            print()
            current_focus_point += 1
            if current_focus_point == len(focus_point):
                print('[CALIBRATION] Finished all instructions')
                break

            print(f"Now executing: {focus_point[current_focus_point]}")
            nao.tts.request(NaoqiTextToSpeechRequest(focus_point[current_focus_point]))
            start_time = time.time()
            print(f"4K's Start Time I: {video_recorder.get_current_i()}")

        else:
            current_time = time.time()
            time.sleep(0.1)

    # Save the datapoints to a file
    print(round_info)
    data = pd.DataFrame(round_info) 
    print(data)
    data.to_csv(video_recorder.get_video_name() + 'round_info.csv', sep = ';')

    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0], recorded_joints=["LShoulderRoll"], recorded_times=[[0]])))
    nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0], recorded_joints=["RShoulderRoll"], recorded_times=[[0]])))
    video_recorder.stop_video_recording()
    print("[CALIBRATION] Finished calibration recording")
    
def on_image(image_message: CompressedImageMessage):
    imgs.put(image_message.image)

def record_pepper(video_recorder: Recorder):
    pepper_frameless = []
    i = 0
    print("[PEPPER] Info on Pepper recording:")
    i_await = 0
    while not video_recorder.get_currently_recording():
        sys.stdout.write(f'\r[PEPPER] Awaiting 4K start ({i_await} seconds passed)')
        sys.stdout.flush()
        time.sleep(1)
        i_await += 1
    print("[PEPPER] Starting to calibrate video")
    
    img = imgs.get()
    print(f"PEPPER SHAPE: {img.shape}")
    while video_recorder.get_currently_recording():
        #pass
        img = imgs.get()
        pepper_frameless , i = append_info_to_list(pepper_frameless, i)
        write_single_frame(i, img[..., ::-1], video_recorder.get_video_name(), _4K = False)
    print("[PEPPER] Ended video recording loop Pepper")
    cv.destroyAllWindows()    
    print(f'[PEPPER] Starting to write the Pepper dataframe to IO ({len(pepper_frameless)} items)')
    save_dataframe_to_csv(video_recorder.get_video_name(), pepper_frameless, 'pepper', video_recorder.get_is_eyetracker(), video_recorder.get_calibration_formal_mode())
    print("[PEPPER] Finished saving images from Pepper")

######################## PARAMETER SETUP ########################
imgs = queue.Queue()

# Pepper preparation
nao = Pepper(ip,top_camera_conf = NaoqiCameraConf(vflip=0, res_id=2))#, motion_record_conf = conf_rec, top_camera_conf=conf_cam)

nao.top_camera.register_callback(on_image)
nao.autonomous.request(NaoWakeUpRequest())
nao.autonomous.request(NaoBasicAwarenessRequest(False))
nao.autonomous.request(NaoBackgroundMovingRequest(False))

set_pepper_tablet(nao)
show_tablet_empty()


# Prepare the recorder
is_eyetracker = has_eyetracker
training = is_training
video_recorder = Recorder()
video_recorder.set_capture_device(get_brio_id())
video_recorder.set_participant_id(participant_id)
video_recorder.set_is_eyetracker(is_eyetracker)
video_recorder.set_calibration_formal_mode('calibration')
video_recorder.set_is_training(False)

threader = Threader()

create_data_folders(participant_id)

#if len(os.listdir(video_recorder.get_video_name())) > 0:
#    input("WARNING: DIRECTORY ALREADY EXISTS!")
#csv_with_rounds_exists(video_recorder.participant_id, trial_round, video_recorder.get_is_eyetracker(), video_recorder.get_calibration_formal_mode())

# Execute the actual calibration
show_current_stage('STARTING CALIBRATION')
def run_nothing():
    pass

if video_recorder.participant_id == -1:
    if str.lower(input("WARNING: PARTICIPANT ID IS -1. CHECK IF CORRECT!! continue [Y/n]?")) != 'y':
        raise Exception

threader.triple_parallel(video_recorder.start_video_recording, record_pepper, run_calibration, second_args=video_recorder, third_args=video_recorder)
print("[CALIBRATION] Finished executing the calibration")

nao.tts.request(NaoqiTextToSpeechRequest('Saved images. Calibration test is over.'))
print("fin")
