# To remove:
# open terminal: cd sic_framework\tests\demo_webserver\ ; python demo_pepper_guess_number.py

"""
To execute:
# Might be better to disable the Pepper's autonomous life before executing the code.

# confirm Docker Framework is running
# confirm TP-Link Wi-Fi
open terminal: cd sic_framework\services\dialogflow ; python dialogflow.py
open terminal: cd sic_framework\services\webserver ; python webserver_pepper_tablet.py

# confirm that the participant_id and capture_device are correct!
open terminal: cd experiment ; python experiment.py
"""

#------------------------------- Preparations: -------------------------------#
# Imports
import cv2 as cv
import time
import sys
import queue
from sic_framework.devices import Pepper

from sic_framework.core.message_python2 import CompressedImageMessage
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import PlayRecording, NaoqiMotionRecording
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoBasicAwarenessRequest, NaoBackgroundMovingRequest, NaoWakeUpRequest, NaoRestRequest
from sic_framework.devices.pepper import Pepper
from sic_framework.devices.common_naoqi.naoqi_camera import NaoqiCameraConf

from motions import move_pepper_left, move_pepper_right, set_pepper_motion, move_peppers_static
from tablet import show_tablet_empty, show_tablet_right, show_tablet_vu_logo, show_tablet_left, set_pepper_tablet
from speech import talk, talk_left, talk_right, set_pepper_speech, talk_intro, talk_preparations, talk_ready, finished_round, talk_response_slow, talk_wrong_key, talk_change_eyetracker, talk_is_training, talk_eyetracker_status, talk_response_correct
from auxillary import show_current_stage, confirm_ready, dump_trialset_to_json, create_data_folders, save_dataframe_to_csv, append_info_to_list, get_brio_id, csv_with_rounds_exists
from randomizer import create_random_trials
from recorder import Recorder
from threader import Threader, write_single_frame
from settings import participant_id, ip, has_eyetracker, is_training

#------------------------------- Functions: -------------------------------#
# This function executes the set of trials
def execute_set_of_trials(args):
    video_recorder, trial_round = args
    time.sleep(5)
    # If needed, grab a subset of the trials
    trials = create_random_trials()
    print(f'Amount of trails to complete: {len(trials)}')
    if video_recorder.get_is_training():
        trials = trials[0:5]
    current_trial = 0

    # Execute all the trials in the trials set
    show_current_stage(f"Executing trials nr. {trial_round} - Eye-tracker on: {video_recorder.get_is_eyetracker()}")
    print("[EXPERIMENT] NOW RECORDING!")
    trial_data = {}
    #print(len(trials))
    for trial in trials:
        print(f"** Executing trial: {current_trial + 1} / {len(trials)}**")
        if current_trial == 24:
            talk('Great! you have finished 20%. Now you have 20 seconds break before next trial!')
            time.sleep(20)
        elif current_trial == 48:
            talk('Good job! you have finished 40%. Now you have 20 seconds break before next trial!')
            time.sleep(20)
        elif current_trial == 72:
            talk('Continue! you have finished 60%. Now you have 20 seconds break before next trial!')
            time.sleep(20)
        elif current_trial == 96:
            talk('WoW! you have finished 80%, here is the last round. And you have 20 seconds break before next trial!')
            time.sleep(20)

        trial['start'] = time.time()
        talk_intro(trial["first_item"])
        #intro_end=time.time()
        #print('finish intro .........................................................................................')
        # Primary Instruction
        if trial['first_item'] == 'tablet':
            first_event = show_tablet_left if trial['direction'] == 'left' else show_tablet_right
        elif trial['first_item'] == 'gesture':
            first_event = move_pepper_left if trial['direction'] == 'left' else move_pepper_right
        else:
            first_event = talk_left if trial['direction'] == 'left' else talk_right
    
        # Secondary Instruction
        if trial['second_item'] == 'tablet':
            second_event = show_tablet_left if (trial['direction'] == 'left' and trial['congruent']) or (trial['direction'] =='right' and trial['congruent'] == False) else show_tablet_right
        elif trial['second_item'] == 'gesture':
            second_event = move_pepper_left if (trial['direction'] == 'left' and trial['congruent']) or (trial['direction'] =='right' and trial['congruent'] == False) else move_pepper_right
        else:
            second_event = talk_left if (trial['direction'] == 'left' and trial['congruent']) or (trial['direction'] =='right' and trial['congruent'] == False) else talk_right

        print(f"[EXPERIMENT] Expected direction: {trial['direction']}")

        # Execute the actual code.
        #print('thread start.......................................', time.time()-intro_end, 'passed after intro end')
        threader = Threader()
        #trial['response_start'] = time.time()
        threader.parallel(execute_single_trial, threader.start_listening, first_args = [first_event, second_event, threader])

        # Do something with the resulting trial
        #trial['round'] = trial_round
        trial['end'] = time.time()
        trial_keystroke = threader.get_resulting_output()
        trial['trial_id'] = current_trial
        trial['result'] = trial['direction'] == trial_keystroke['reason']
        print(f"KEYSTOKE WAS CORRECT: {trial['result']}")
        trial['keystroke'] = trial_keystroke
        trial_data[current_trial] = trial



        # Extra information for the participant during training:
        if video_recorder.get_is_training():
            # If response too slow:
            if trial_keystroke['reason'] == 'overtime':
                talk_response_slow()
            if trial_keystroke['valid'] and not trial['result']:
                talk_wrong_key()
            if trial_keystroke['valid'] and trial['result']:
                talk_response_correct()

        # Reset the PepperS
        show_tablet_empty()
        current_trial += 1
        #time.sleep(0.5) # Found by Lin and changed to 0.5 at 02-04-24 #time.sleep(3) # Remove later.
        print()

    #finished_round()
    #print(trial_data)
    dump_trialset_to_json(trial_data, video_recorder.get_video_name() + 'round_info.csv')
    video_recorder.stop_video_recording()

    # Save the datapoints to a file
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0], recorded_joints=["LShoulderRoll"], recorded_times=[[0]])))
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0], recorded_joints=["RShoulderRoll"], recorded_times=[[0]])))
    #video_recorder.stop_video_recording()
    print("[EXPERIMENT] Finished experiment recording")

def execute_single_trial(args):
     first_event, second_event, threader = args
     threader.parallel(first_event, second_event)
    
imgs = queue.Queue()
def on_image(image_message: CompressedImageMessage):
    imgs.put(image_message.image)

def record_pepper(video_recorder: Recorder):
    global i
    pepper_frameless = []
    print("[PEPPER] Info on Pepper recording:")
    i_await = 0
    while not video_recorder.get_currently_recording():
        sys.stdout.write(f'\r[PEPPER] Awaiting 4K start ({i_await} seconds passed)')
        sys.stdout.flush()
        time.sleep(1)
        i_await += 1
    print("[PEPPER] Starting to calibrate video")
    
    img = imgs.get()
    print(f'PEPPER Camera Resolution: {img.shape}')
    if img.shape[0] < 480 or img.shape[1] < 640:
        raise Exception("PEPPER CAMERA DOES NOT RUN AT REQUIRED RESOLUTION!")
    
    while video_recorder.get_currently_recording():
        img = imgs.get()
        pepper_frameless, _ = append_info_to_list(pepper_frameless, '{:07}'.format(int(i)))
        i += 1
        write_single_frame('{:07}'.format(i), img[..., ::-1], video_recorder.get_video_name(), _4K = False)
    
    print("[PEPPER] Ended video recording loop Pepper")
    cv.destroyAllWindows()
    save_dataframe_to_csv(video_recorder.get_video_name(), pepper_frameless, 'pepper', video_recorder.get_is_eyetracker(), video_recorder.get_calibration_formal_mode())
    print("[PEPPER] Finished saving images from Pepper")

#------------------------------- CODE: -------------------------------#

# Variables
port = 8080
folder_name = './experiment_images_output/'
imgs = queue.Queue()

# Pepper device setup
pepper = Pepper(ip,top_camera_conf = NaoqiCameraConf(vflip=0, res_id=2))#, motion_record_conf = conf_rec, top_camera_conf=conf_cam)
pepper.top_camera.register_callback(on_image)
pepper.autonomous.request(NaoWakeUpRequest())
pepper.autonomous.request(NaoBasicAwarenessRequest(False))
pepper.autonomous.request(NaoBackgroundMovingRequest(False))

# Preparations
show_current_stage("Starting preparations")

# Prepare Tablet/Screen
set_pepper_tablet(pepper)
show_tablet_empty()

# Prepare Motion/Gestures
set_pepper_motion(pepper)
move_peppers_static()

# Prepare Talk/Speech
set_pepper_speech(pepper)
talk_preparations()

# Finalizing
show_tablet_vu_logo()
show_current_stage("Finishing up")

if participant_id == -1:
    print("Warning: participant ID is currently at default (-1)")

create_data_folders(participant_id)

is_eyetracker = has_eyetracker
training = is_training
video_recorder = Recorder()
video_recorder.set_capture_device(get_brio_id())
video_recorder.set_participant_id(participant_id)
video_recorder.set_is_eyetracker(is_eyetracker)
video_recorder.set_calibration_formal_mode('experiment')
video_recorder.set_is_training(is_training)

i = 0 # Purpose of this i?

if training:
    another_one = True
    while another_one:
        talk_is_training()
        video_recorder.set_trial_set(0)
        threader = Threader()
        threader.triple_parallel(video_recorder.start_video_recording, record_pepper, execute_set_of_trials, second_args=video_recorder, third_args=[video_recorder, 0])
        video_recorder.stop_video_recording()
        if input("Another one? [Y/n]").upper() != 'Y':
            another_one = False

else:
    experiment_length = 1#............................................................................
    start = 0
    talk_eyetracker_status(video_recorder.get_is_eyetracker())
    # Confirm if the participant is ready to start a new trial
  
    for trial_round in range(start, start + experiment_length):
        # Check if the current status of the csv already contains this setting.
        csv_with_rounds_exists(video_recorder.participant_id, trial_round, video_recorder.get_is_eyetracker(), video_recorder.get_calibration_formal_mode())
        video_recorder.set_trial_set(trial_round)

        threader = Threader()
        threader.parallel(
            Threader().parallel(confirm_ready, talk_ready),
            threader.triple_parallel(video_recorder.start_video_recording, record_pepper, execute_set_of_trials, second_args=video_recorder, third_args=[video_recorder, trial_round])
        )
        video_recorder.stop_video_recording()
        print(f"TRIAL SET {trial_round} was completed!")
        #video_recorder.clear_round_info_csv() # Clear the round_info.csv from dir
        if trial_round ==  start + experiment_length - 1: # Last round. Change Eye-Tracker
            talk_change_eyetracker()
            print("END OF THIS SET OF (NON-) EYE-TRACKER")
        elif trial_round < experiment_length - 1:
            #confirm_ready()
            print("continuing")
            print()

show_current_stage("[EXPERIMENT] END OF EXPERIMENT!")
pepper.autonomous.request(NaoRestRequest())

print("fin")
