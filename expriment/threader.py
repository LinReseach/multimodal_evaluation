import time
from pynput import keyboard
import threading
from threading import Thread
import cv2
import queue
import os

class Threader():
    resulting_output = {}
    key_pressed = None
    #thread_stop = True
    def set_resulting_output(self, value):
        self.resulting_output = value
    def get_resulting_output(self):
        return self.resulting_output

    ############# PARALLELIZATION #############
    # This function runs two events in parallel.
    def parallel(self, first_event, second_event, first_args = None, second_args = None):
        if first_args == None:
            first_thread = threading.Thread(target=first_event)
        else:
            first_thread = threading.Thread(target=first_event, args=(first_args,))
        if second_args == None:
            second_thread = threading.Thread(target=second_event)
        else:
            second_thread = threading.Thread(target=second_event, args=(second_args,))

        first_thread.start()
        second_thread.start()
        first_thread.join()
        second_thread.join()
    
    # This function runs three threads at the same time.
    # Consider changing this to accept lists as inputs with a loop to enable scaling.
    def triple_parallel(self, first_event, second_event, third_event, first_args = None, second_args = None, third_args = None):
        if first_args == None:
            first_thread = threading.Thread(target=first_event)
        else:
            first_thread = threading.Thread(target=first_event, args=(first_args,))
        if second_args == None:
            second_thread = threading.Thread(target=second_event)
        else:
            second_thread = threading.Thread(target=second_event, args=(second_args,))
        if third_args == None:
            third_event = threading.Thread(target=third_event)
        else:
            third_event = threading.Thread(target=third_event, args=(third_args,))

        first_thread.start()
        second_thread.start()
        third_event.start()
        first_thread.join()
        second_thread.join()
        third_event.join()

    ############# KEY PRESS RECORDER #############
    # This function if for listening to the keystrokes.
    def start_listening(self):
        self.listen_for_keys()
        
    def show_press(self, _key):
        lr = (_key == keyboard.Key.left or _key == keyboard.Key.right)
        print(f'Key: {_key} - LR: {lr}')

        if lr:
            self.key_pressed = _key
            #print('stopped?')
            return False

    def listen_for_keys(self):
        self.set_resulting_output({'valid':False, 'reason': 'initialization', 'duration':-1})

        l = keyboard.Listener(on_press = self.show_press, suppress = True)
        l.start()
        start_time = time.time()
        print('response start time', start_time)
        while l.is_alive() and time.time() - start_time < 4:
            time.sleep(0.001)
        
        if l.is_alive():
            self.set_resulting_output({
                'valid':False, 
                'reason': 'overtime', 
                'response_start':start_time, 
                'duration':time.time() - start_time
                })
            print('Response time exceeded 4 seconds')
            l.stop()
        else:
            if self.key_pressed == keyboard.Key.left:
                reason = 'left'
            else:
                reason = 'right'
            self.set_resulting_output({'valid':True, 'reason': reason, 'duration':time.time() - start_time - 0.8})
            print('response start time', time.time() - start_time)
            #print('key was pressed')
    

############# IMAGE PROCESSING #############

# This function is a small passthrough wrapper for writing images 
def wsf(arguments):
    i, frame, video_name, _4K = arguments
    device = '4K' if _4K else 'Pepper'
    # os.makedirs(video_name + '/' + device + '/', exist_ok=True)
    # video_name += device + '_'

    video_name = video_name + device + '/'
    os.makedirs(video_name, exist_ok=True)
    _i = int(i)
    frame_id = '{:07}'.format(_i)
    output_file = f'{video_name}{frame_id}.jpg'

    cv2.imwrite(output_file, frame) # Update this to contain the get_video_name()
    
# This is the main function that gets called when saving a single frame to the disk.
# Note: beware of overloading the amount of Threads that can be started.
def write_single_frame(i, frame, video_name,_4K = True):
    #print(threading.active_count())
    #q.put([i, frame, video_name, _4K])
    Thread(target=wsf, args=((i, frame, video_name,_4K),)).start()

q = queue.Queue()
