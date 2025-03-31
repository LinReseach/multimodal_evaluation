# The functions in this file are mostly based from the OpenVC VideoCapture tutorial, which can be found here:
# https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

import os
import cv2 as cv
import time
from auxillary import get_participant_folder, save_dataframe_to_csv, append_info_to_list
from threader import write_single_frame

class Recorder():
    # PARAMETERS
    currently_recording = False
    participant_id = -1
    trial_set = -1
    capture_device = -1
    finished_up_recording = True
    current_focus_point = None
    cap: cv.VideoCapture = None
    calibration_formal_mode = None
    is_training = False
    is_eyetracker = None
    current_i = 0


    # GETTERS     
    def get_currently_recording(self):
        return self.currently_recording
    def get_calibration_formal_mode(self):
        return self.calibration_formal_mode
    def get_is_training(self):
        return self.is_training
    def get_is_eyetracker(self):
        return self.is_eyetracker
    def get_current_i(self):
        return self.current_i

    # SETTERS
    def set_participant_id(self,_participant_id):
        self.participant_id = _participant_id
    def set_trial_set(self,_trial_set):
        self.trial_set = _trial_set
    def set_calibration_formal_mode(self, _calibration_formal_mode):
        self.calibration_formal_mode = _calibration_formal_mode
    def set_is_training(self, _is_training):
        self.is_training = _is_training
    def set_capture_device(self, _capture_device):
        self.capture_device = _capture_device
    def set_currently_recording(self, _currently_recording):
        self.currently_recording = _currently_recording
    def set_is_eyetracker(self, _is_eyetracker):
        self.is_eyetracker = _is_eyetracker
    def set_current_i(self, _current_i):
        self.current_i = _current_i

    # FUNCTIONS TO RECORD
    def start_video_recording(self):
        ### Record_in_4K
        self.cap = cv.VideoCapture(self.capture_device)
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # Check if the camera is opened correctly
        if not self.cap.isOpened():
            print("ERROR: Can't initialize camera capture")
            exit(1)

        # Set properties: frame width, frame height, and frames per second (FPS)
        resolutions = { 0:{'w':4096, 'h': 2160, 'fps':30},
                        1:{'w':3840, 'h': 2160, 'fps':24},
                        2:{'w':1920, 'h': 1080, 'fps':30},
                        3:{'w':1920, 'h': 1080, 'fps':60},
                        4:{'w':1280, 'h': 720, 'fps':30}               
                    }
        resolution_choice = 2
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, resolutions[resolution_choice]['w'])
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, resolutions[resolution_choice]['h'])
        self.cap.set(cv.CAP_PROP_FPS, resolutions[resolution_choice]['fps'])


        # Get the resolution
        width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv.CAP_PROP_FPS))
        print(f"Resolution W: {width} - H: {height} - FPS: {fps}")

        # Only start when it is actually recording
        self.currently_recording = True
        self.finished_up_recording = False
        frameless = []
        i = self.get_current_i()
        #print(f"Getting value of I: {i}")
        num_frames = 0
        start_time = time.time()

        # The actual recording loop
        while self.cap.isOpened() and self.currently_recording:
            ret, frame = self.cap.read()
            if not ret:
                print("[VIDEO] Can't receive frame (stream end?). Exiting ...") # From the OpenCV tutorial
                break
        
            # Get the current time.
            frameless, _ = append_info_to_list(frameless, '{:07}'.format(int(i)))
            write_single_frame(i, frame, self.get_video_name(), True)
            i += 1
            self.set_current_i(i)
            if cv.waitKey(1) == ord('q'): # Press 'q' on the Python Window to stop the script
                break
            
            # Calculate FPS every second
            num_frames += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = num_frames / elapsed_time
                print("[4K] FPS:", fps)

                # Reset variables for the next FPS calculation
                start_time = time.time()
                num_frames = 0

        # Finish up recording and save the data to IO
        print("[VIDEO] Ended video recording loop 4K")
        self.finished_up_recording = True
        self.stop_video_recording()
        print(f"Setting value of I: {i}")
        self.set_current_i(i)
        cv.destroyAllWindows()
        print(f'[VIDEO] Starting to write the 4K dataframe to IO ({len(frameless)} items)')
        save_dataframe_to_csv(self.get_video_name(), frameless, '4K', self.get_is_eyetracker(), self.get_calibration_formal_mode())
        print("[VIDEO] Finished saving images from 4K")

    # Stop recording the video
    def stop_video_recording(self):
        self.currently_recording = False
        print("[VIDEO] Stopping Recording 4K")
        while not self.finished_up_recording:
            print("[VIDEO] Still stopping 4K")
            time.sleep(1)
        
        # Release everything if job is finished
        print("[VIDEO] Finished stopping 4K")
        self.cap.release()
        cv.destroyAllWindows()
        self.currently_recording = False

    # This function generates a folder for the output of the video with a name for a video, based on the current (date-)time.
    def get_video_name(self, allow_creating_folders = True):
        # Get the folder of this specific participant
        participant_folder = get_participant_folder(self.participant_id)
        os.makedirs(participant_folder, exist_ok=True)

        # Check if the current participant is in training, eyetracker or no-eyetracker mode
        train_eye_noeye = participant_folder
        if self.get_is_training():
            train_eye_noeye += 'training'
        elif self.get_is_eyetracker():
            train_eye_noeye += 'glasses'
        else:
            train_eye_noeye += 'noglasses'
        train_eye_noeye += '_'
        #os.makedirs(train_eye_noeye, exist_ok=True)

        # Check if the current participant is doing the calibration or the formal experiment
        calibration_or_formal = train_eye_noeye
        calibration_or_formal += self.get_calibration_formal_mode()
        calibration_or_formal += '_'
        #os.makedirs(calibration_or_formal, exist_ok=True)

        # Return the correct folder.
        return calibration_or_formal

    def clear_round_info_csv(self):
        path = self.get_video_name() + 'round_info.csv'
        os.remove(path)

