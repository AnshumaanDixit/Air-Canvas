import os
import cv2
import time as t
import random as r
import threading as th
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision import drawing_styles as mp_drawing_styles
from mediapipe.tasks.python.vision import HandLandmarksConnections
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions
import pyautogui as pg
import pygame as pgg
pg.FAILSAFE = True
pg.PAUSE = 0
pgg.init()
clock = pgg.time.Clock()

FPS = 60 


current_dir = os.path.dirname(os.path.abspath(__file__))
model_file_path = os.path.join(current_dir, 'gesture_recognizer.task')
baseop = python.BaseOptions(model_asset_path = model_file_path) 
op = GestureRecognizerOptions(base_options=baseop, num_hands = 2, running_mode = vision.RunningMode.VIDEO) 
detector = GestureRecognizer.create_from_options(op) 

camera = cv2.VideoCapture(0) 
key = 0 
ret, frame = camera.read() 
lock = th.Lock()
flag = 0
result = 0 
output_frame=0 
dot_custom = mp_drawing.DrawingSpec(color=(1,255,31),thickness=10,circle_radius=10) 
line_custom = mp_drawing.DrawingSpec(color=(189,0,255),thickness=8) 
flag_mediapipe, flag_update_frame = 1,1
flag_prev_was_point_up= False

def hand_gesture_logic():
    global current_message,flag_written
    margin_x = 0.15  
    margin_y = 0.15
    while True:
        if(result!=0):
            if(result.gestures):
                global flag_prev_was_point_up
                handedness = {"Left":"Right","Right":"Left"}
                hand_1_gesture = result.gestures[0][0].category_name
                hand_1_handedness = handedness[result.handedness[0][0].category_name]
                print(f"Hand 1 is performing {hand_1_gesture} and it is a {hand_1_handedness} hand!",end="\n")
            
                if(hand_1_handedness == "Right" and hand_1_gesture == "Pointing_Up"):
                    hand_1_x = result.hand_landmarks[0][8].x
                    hand_1_y = result.hand_landmarks[0][8].y
                    screen_x,screen_y = pg.size()
                    target_x = (hand_1_x - margin_x) / (1.0 - 2 * margin_x) * screen_x
                    target_y = (hand_1_y - margin_y) / (1.0 - 2 * margin_y) * screen_y
                    pg.moveTo(target_x,target_y,duration=0)
                    flag_prev_was_point_up = True
                if(flag_prev_was_point_up and hand_1_handedness == "Right" and hand_1_gesture == "Closed_Fist"):
                    pg.click()
                    flag_prev_was_point_up = False
                if(len(result.gestures)>1):
                    hand_2_gesture = result.gestures[1][0].category_name
                    hand_2_handedness = handedness[result.handedness[1][0].category_name]
                    print(f"Hand 2 is performing {hand_2_gesture} and it is a {hand_2_handedness}")
                    if(hand_2_handedness == "Right" and hand_2_gesture == "Pointing_Up"):
                        hand_2_x = result.hand_landmarks[1][8].x
                        hand_2_y = result.hand_landmarks[1][8].y
                        screen_x,screen_y = pg.size()
                        target_x = (hand_2_x - margin_x) / (1.0 - 2 * margin_x) * screen_x
                        target_y = (hand_2_y - margin_y) / (1.0 - 2 * margin_y) * screen_y
                        pg.moveTo(target_x,target_y,duration=0)
                        flag_prev_was_point_up = True
                    if(flag_prev_was_point_up and hand_2_handedness == "Right" and hand_2_gesture == "Closed_Fist"):
                        pg.click()
                        flag_prev_was_point_up = False
'''
def update_frame():
    global flag
    flag = 0
    scale = 1.0 
    global ret, frame
    while flag_update_frame: 
        with lock:
            ret, frame = camera.read()
            if len(frame)!=0:
                frame = cv2.flip(frame, 1) 
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) 
            if flag==-1: 
                scale+=0.0025
            if flag==1: 
                scale -= 0.0025
            if frame is not None:
                frame = cv2.resize(frame, None, fx = scale, fy = scale) 
            flag = 0
'''
def mediapipe():
    global frame,result,output_frame,dot_custom,line_custom 
    while flag_mediapipe: 
        frame_1 = frame
        cv2.flip(frame_1,1)
        frame_for_landmark = mp.Image(image_format= mp.ImageFormat.SRGB, data = frame_1) 
        timestamp = pgg.time.get_ticks()
        result = detector.recognize_for_video(frame_for_landmark,timestamp) 
        '''
        with lock:
            output_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR) 
            for hand_landmarks in result.hand_landmarks: 
                mp_drawing.draw_landmarks( 
                            image = output_frame, 
                            landmark_list = hand_landmarks,
                            connections=HandLandmarksConnections.HAND_CONNECTIONS,
                            landmark_drawing_spec=dot_custom,
                            connection_drawing_spec=line_custom) 
        '''
        with lock:
            output_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            cv2.flip(output_frame,1)
cv2.namedWindow("webcam",cv2.WINDOW_AUTOSIZE) 
'''
updFrame = th.Thread(target = update_frame)
updFrame.daemon = True
updFrame.start()
'''
MediaThread = th.Thread(target = mediapipe)
MediaThread.daemon = True 
MediaThread.start()

CursorMove = th.Thread(target = hand_gesture_logic)
CursorMove.daemon = True
CursorMove.start()

while True:
    key = cv2.waitKey(1) 
    '''
    if key==ord('r'): 
        flag=1 
    elif key==ord('t'): 
        flag=-1 
    '''
    if key==ord('q'):
        flag_mediapipe, flag_update_frame=0,0 
        break
    elif key==ord("l"):
        if result!=0 and len(result.hand_landmarks)>0:
            print(f"\none hand index finger x:{result.hand_landmarks[0][8].x} y:{result.hand_landmarks[0][8].y} z:{result.hand_landmarks[0][8].z}")
            if len(result.hand_landmarks)>1:
                print(f"\nsecond hand index finger x:{result.hand_landmarks[1][8].x} y:{result.hand_landmarks[1][8].y} z:{result.hand_landmarks[1][8].z}")
    with lock:
        ret, frame = camera.read()
        if len(frame)!=0:
                frame = cv2.flip(frame, 1) 
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) 
        if ret and (output_frame is not None):
            cv2.imshow("webcam",output_frame) 
        elif not ret:
            print("Failed to read!") 
            break
    clock.tick(FPS)
camera.release() 
cv2.destroyAllWindows() 