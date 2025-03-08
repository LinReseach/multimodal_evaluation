# Can probably remove ./motions due to force setting of the joints

#------------------------------- Preparations: -------------------------------#
# Imports
import time
from sic_framework.devices.common_naoqi.naoqi_motion import NaoqiIdlePostureRequest
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import PlayRecording, NaoqiMotionRecording
from sic_framework.devices.common_naoqi.naoqi_stiffness import Stiffness
from sic_framework.devices.pepper import Pepper

# Setup
pepper = None
chain = ["LShoulderRoll", "RShoulderRoll"]

#------------------------------- Functions: -------------------------------#
def move_joints(angle = 0, chain = chain):
    #global pepper
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, angle, 0], recorded_joints=[chain], recorded_times=[[0, 1, 2.5]])))
   # pepper.motion_record.request(PlayRecording(
        #NaoqiMotionRecording(recorded_angles=[angle, angle, 0], recorded_joints=[chain], recorded_times=[[0, 1, 2]])))
def move_shoulder_pitch():
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0.5, 1, 1.6], recorded_joints=["RShoulderPitch"], recorded_times=[[2, 4, 6]])))
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0.5, 1, 1.6], recorded_joints=["LShoulderPitch"], recorded_times=[[2, 4, 6]])))

def move_pepper_tpose():
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[1], recorded_joints=["LShoulderRoll"], recorded_times=[[1]])))
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[-1], recorded_joints=["RShoulderRoll"], recorded_times=[[1]])))

def move_pepper_right(angle = 1): # Note: This is the RIGHT arm when looking at Pepper, moves Pepper's LEFT arm.
    print("[MOVING] Right arm")
    move_joints(angle, chain[0]) # always positive

def move_pepper_left(angle = -1): # Note: This is the RIGHT arm when looking at Pepper, moves Pepper's LEFT arm.
    print("[MOVING] Left arm")
    #print(f'activated gesture at: {time.time()}')
    move_joints(angle, chain[1]) # always negative

def move_peppers_static():
    print("[MOVING] Resetting both arms")
    move_pepper_left(angle = -1)
    move_pepper_right(angle = 1)

def move_peppers_head():
    print("[MOVING] Calibrating Head")

    # This line for some reason causes a slight movement of the HeadYaw to the left or right.
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, -.4], recorded_joints=['HeadPitch'], recorded_times=[[0, 1]]))) 
    
    # Recalibrate the head yaw to be centered
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[-0.5, 0.5, 0], recorded_joints=['HeadYaw'], recorded_times=[[0, 1, 2]])))
    pepper.motion_record.request(PlayRecording(NaoqiMotionRecording(recorded_angles=[0, 0], recorded_joints=['HeadYaw'], recorded_times=[[0, 1]])))

def set_pepper_motion(_pepper):
    global pepper
    pepper = _pepper

    # Disable "alive" activity for the whole body and set stiffness of the arm to zero
    pepper.motion.request(NaoqiIdlePostureRequest("Body", False))
    pepper.stiffness.request(Stiffness(0.7, chain))
    pepper.stiffness.request(Stiffness(0.7, ["RShoulderPitch","LShoulderPitch"]))
    move_peppers_head()