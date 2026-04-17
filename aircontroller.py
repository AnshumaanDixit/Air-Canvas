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
import tkinter as tk
pg.FAILSAFE = True
pg.PAUSE = 0

current_dir = os.path.dirname(os.path.abspath(__file__))
model_file_path = os.path.join(current_dir, 'gesture_recognizer.task')
baseop = python.BaseOptions(model_asset_path = model_file_path,delegate=python.BaseOptions.Delegate.GPU) 
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
def press_key(key_val):
    """Function to trigger pyautogui when a Tkinter button is pressed."""
    if key_val == 'Space': pg.press('space')
    elif key_val == 'Enter': pg.press('enter')
    elif key_val == 'Backspace': pg.press('backspace')
    elif key_val == 'Tab': pg.press('tab')
    elif key_val == 'Caps': pg.press('capslock')
    elif key_val == 'Shift': pg.press('shift')
    else: pg.press(key_val)

root = tk.Tk()
root.title("Air Canvas Keyboard")
root.attributes('-topmost', True) 
root.configure(bg='#2b2b2b')

buffer_text = tk.StringVar()
buffer_text.set("")

display_label = tk.Label(
    root, 
    textvariable=buffer_text, 
    font=('Arial', 18, 'bold'), 
    bg='white', 
    fg='black', 
    height=2, 
    anchor='w', 
    padx=10
)

display_label.grid(row=0, column=0, columnspan=14, sticky='nsew', padx=5, pady=5)

keyboard_layout = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Clear', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Space']
]
flag_written = False
current_message = ""
def press_key(key_val):
    """Updates the buffer instead of typing instantly."""
    global current_message,flag_written
    current_message = buffer_text.get()
    
    if key_val == 'Backspace':
        buffer_text.set(current_message[:-1]) 
    elif key_val == 'Space':
        buffer_text.set(current_message + " ")
    elif key_val == 'Clear':
        buffer_text.set("") 
    else:
        buffer_text.set(current_message + key_val)
        current_message = buffer_text.get() 
        flag_written = False

for row_index, row_keys in enumerate(keyboard_layout, start=1):
    for col_index, key_val in enumerate(row_keys):
        colspan = 1
        width = 4
        if key_val in ['Backspace', 'Enter', 'Shift', 'Caps', 'Clear']:
            width = 8
        elif key_val == 'Space':
            colspan = 14
            width = 40
            
        btn = tk.Button(
            root, text=key_val, width=width, height=2,
            font=('Arial', 12, 'bold'), bg='#4a4a4a', fg='black',
            command=lambda k=key_val: press_key(k)
        )
        if key_val == 'Space':
            btn.grid(row=row_index, column=0, columnspan=colspan, padx=2, pady=2, sticky='nsew')
        else:
            btn.grid(row=row_index, column=col_index, padx=2, pady=2, sticky='nsew')

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
                if (hand_1_handedness == "Right" and hand_1_gesture == "Open_Palm"):
                    if (flag_written == False):
                        pg.write(current_message,interval = 0)
                        flag_written = True
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
                    if (hand_2_handedness == "Right" and hand_2_gesture == "Open_Palm"):
                        if (flag_written == False):
                            pg.write(current_message,interval = 0)
                            flag_written = True
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
        timestamp = int(t.time()*1000) 
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
    try:
        root.update_idletasks()
        root.update()
    except tk.TclError:
        pass
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
camera.release() 
cv2.destroyAllWindows() 
root.destroy()