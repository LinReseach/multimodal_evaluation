
import queue
import cv2
from sic_framework.core.message_python2 import CompressedImageMessage
from sic_framework.devices import Nao
from sic_framework.devices.common_naoqi.naoqi_camera import NaoqiCameraConf
from sic_framework.devices.common_naoqi.naoqi_motion import NaoqiIdlePostureRequest
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import PlayRecording, NaoqiMotionRecording, NaoqiMotionRecorderConf
from sic_framework.devices.common_naoqi.naoqi_autonomous import NaoBasicAwarenessRequest, NaoBackgroundMovingRequest, NaoRestRequest, NaoWakeUpRequest
from sic_framework.devices.common_naoqi.naoqi_stiffness import Stiffness
from sic_framework.devices.pepper import Pepper
from sic_framework.devices.common_naoqi.naoqi_text_to_speech import NaoqiTextToSpeechRequest
# The functions in this file are mostly based from the OpenVC VideoCapture tutorial, which can be found here:
# https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

import cv2 as cv
import time
import pandas as pd
import sys

from settings import ip

_ip = [
    '10.0.0.148', # 148 = Alan
    '10.0.0.197', # 197 = Herbert
    '10.0.0.165', # 197 = Marvin
    '10.15.3.144', # 144 = Marvin,
    '10.15.2.168',
    '10.15.3.176' # Alan
    ][5]
folder_name = './calibration_images_output/'

# Pepper preparation
conf = NaoqiCameraConf(vflip=0, auto_focus=True) # You can also adjust the brightness, contrast, sharpness, etc. See "NaoqiCameraConf" for more
nao = Pepper(ip=ip, top_camera_conf=conf, motion_record_conf = NaoqiMotionRecorderConf(use_sensors=True, use_interpolation=True, samples_per_second=60))

nao.autonomous.request(NaoWakeUpRequest())
nao.autonomous.request(NaoBasicAwarenessRequest(False))
nao.autonomous.request(NaoBackgroundMovingRequest(False))

# Added moving the arms back down as to prevent overheating of the arms
#nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, 0], recorded_joints=["LShoulderRoll"], recorded_times=[[0, 1]])))
#nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, 0], recorded_joints=["RShoulderRoll"], recorded_times=[[0, 1]])))

nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, 1], recorded_joints=["LShoulderRoll"], recorded_times=[[0, 1]])))
nao.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, -1], recorded_joints=["RShoulderRoll"], recorded_times=[[0, 1]])))

time.sleep(10)
nao.tts.request(NaoqiTextToSpeechRequest('40 seconds left'))
time.sleep(10)
nao.tts.request(NaoqiTextToSpeechRequest('30 seconds left'))
time.sleep(10)
nao.tts.request(NaoqiTextToSpeechRequest('20 seconds left'))
time.sleep(10)
nao.tts.request(NaoqiTextToSpeechRequest('10 seconds left'))
time.sleep(10)
nao.autonomous.request(NaoRestRequest())

print("FIN with dropping arms")
