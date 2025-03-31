
# introduction
This code include calibration and experiment:

1 In calibration, the robot guided human to looka at five dot on its body.

2 In the experiment, the robot will simultaneously present two modalities out of
three options (gesture, speech, and tablet). One modality will serve as the primary
cue, which participants are instructed to focus on, while the other acts as a
distracting cue that can be either congruent or incongruent with the primary cue.

Throughout the experiment, participants' faces will be recorded by Pepper's
built-in camera and a 4K camera mounted on top of the robot's head. These
recordings will serve as input to the L2CS deep learning model to predict
participants' gaze direction. Additionally, participants will wear eye-tracking
glasses to capture their gaze behavior. The experiment will also track
participants' keypress responses.

# code in /experiment
+calibration.py: make robot to guide human to look at five dots on its body.
+experiment.py: controls the procedure of starting the cameras, instruct the participants, and control the trials

+ motions.py: control the actuators to make robot raise arms and head
+ speech.py: use the speakers to vocalize commands.
+ tablet.py: show webpages on the tablet.

+ recorder.py: recording of the 4k camera
+ threader.py: enables multithreading and key-capturing.
+ settings.py: contains parameters for ip, eye-tracking status, participant information.
+ randomizer.py: shuffle trials.
+ auxillary.py: supplementary functions
+ time_frame_matching.py: merge the different camera0-output .csv files to a single file, based on the .csv of the trials.
+ pepper_drop_arms.py: raise the arms of the Pepper robot to confirm actuator control.

# code in /sic framework
this code is based on the environment of sic framework

