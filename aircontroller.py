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
baseop = python.BaseOptions(model_asset_path = model_file_path) #used as a variable to store the base options for getting the options used to create detector object, used for better readability
op = GestureRecognizerOptions(base_options=baseop, num_hands = 2, running_mode = vision.RunningMode.VIDEO) #used as a variable to store the options for creation of detector object, for better readability
detector = GestureRecognizer.create_from_options(op) #create a object from mediapipe that detects for hand in the given frame

camera = cv2.VideoCapture(0) #create a webcam object to read from
key = 0 #a variable to store and check if the user pressed the closing key
ret, frame = camera.read() #read the webcam object, ret is true if it successfully read and frame is the numpy array, ret is false if it fails and frame is empty
lock = th.Lock() #used to prevent corruption caused from interruption of read or write operation between multiple threads
flag = 0 #used for controlling the scale in the updFrame thread, to resize the image and window
result = 0 #a variable to store the data of the hands returned by the mediapipe model
output_frame=0 #a variable to store the final frame with landmarks
dot_custom = mp_drawing.DrawingSpec(color=(1,255,31),thickness=10,circle_radius=10) #editable style for landmarks and connection
line_custom = mp_drawing.DrawingSpec(color=(189,0,255),thickness=8) #editable style for landmark and connection
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

keyboard_layout = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Space']
]

for row_index, row_keys in enumerate(keyboard_layout):
    for col_index, key_val in enumerate(row_keys):
        colspan = 1
        width = 4
        if key_val in ['Backspace', 'Enter', 'Shift', 'Caps', 'Tab']:
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
                    hand_1_y = result.hand_landmarks[0][0].y
                    screen_x,screen_y = pg.size()
                    pg.moveTo(hand_1_x*screen_x,hand_1_y*screen_y,duration=0)
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
                        hand_2_y = result.hand_landmarks[1][0].y
                        screen_x,screen_y = pg.size()
                        pg.moveTo(hand_2_x*screen_x,hand_2_y*screen_y,duration=0)
                        flag_prev_was_point_up = True
'''
def update_frame():
    global flag
    flag = 0
    scale = 1.0 #since the cv2.resize() works scales with percentage with fx and fy variable, WITH RESPECT to the original size, that is by default 16:9 ratio, so a variable scale, that updates keeps the relative size together as increasing
    global ret, frame
    while flag_update_frame: #a flag to control the start and end of this thread
        with lock:
            ret, frame = camera.read()
            if len(frame)!=0:
                frame = cv2.flip(frame, 1) #the reading returns a flipped image, creating a mirror effect, it must be flipped back, cv2.flip() takes the frame as parameter, and the 2nd parameter is for its mode, 1 for horizontal flip, 0 for vertical flip and -1 for both
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #opencv is a old library, so it follows the BGR method that was standard before RGB became universal, mediapipe takes RGB so it must be converted
            if flag==-1: #a basic mode for increasing of window size controlled by main thread
                scale+=0.0025
            if flag==1: #a basic mode for decreasing of window size controlled by main thread
                scale -= 0.0025
            if frame is not None:
                frame = cv2.resize(frame, None, fx = scale, fy = scale) #resizes the window with percentage to the original 16:9 ratio
            flag = 0
'''
def mediapipe():
    global frame,result,output_frame,dot_custom,line_custom #global keyword so when this is run on a thread, its variables refer to the global of the main thread, so that the code inside the thread can be controlled
    while flag_mediapipe: #a flag to control the start and end of this thread
        frame_1 = frame
        cv2.flip(frame_1,1)
        frame_for_landmark = mp.Image(image_format= mp.ImageFormat.SRGB, data = frame_1) #a special image object that is defined and used by mediapipe for detection of hand
        timestamp = int(t.time()*1000) #timestamp reference to be used as a parameter for detect_for_video for better and faster result
        result = detector.recognize_for_video(frame_for_landmark,timestamp) #the detector object defined before has an attribute for detect_for_video that takes its own specialized image object, and returns the location of hands in the image/frame IN PERCENTAGE,timestamp parameter is used for better optimization, also a side note, it also has a detect attribute that will detect on a single image, but detect_for_video is better optimized for videos, since the previous image is similar to next one, essentially a frame
        '''
        with lock:
            output_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR) #a final finished variable to avoid corruption of frame or any unexpected behavior
            for hand_landmarks in result.hand_landmarks: #so results contains 3 objects, hand_landmarks, world_landmarks, and handedness, hand_landmarks are the percentage position on the screen of hands, world_landmarks is a physical coordinate system result used for 3d space, and handedness is just another object that tells if the hand is left or right, here result will have 2 element in the hand_landmarks object list, those will be the coordinate of the 21 landmark points, given in percentage style, for two hands so a 2d array, 
                mp_drawing.draw_landmarks( 
                            image = output_frame, 
                            landmark_list = hand_landmarks,
                            connections=HandLandmarksConnections.HAND_CONNECTIONS,
                            landmark_drawing_spec=dot_custom,
                            connection_drawing_spec=line_custom) #draw_landmarks() is a attribute of the drawing_utils object, that takes the image, AND DRAWS ON THE EXISTING ONE! DOES NOT RETURN OR CREATE A NEW ONE, image:takes the numpy array, landmarks_list:take the percentage position of the 21 landmarks of one hand, hence inside a loop for both hands, connections:data for this parameter is pulled from the mediapipe module itself, it basically tells the code which landmarks connects to which so it represents a hand, landmarks_drawing_style and connection_drawing_style: they take exactly what they say, the style for the lines(connections) and dots(landmarks) for the hand representation, its default style can be obtained from drawing_styles by drawing_styles.get_default_hand_landmarks/connections_style()
        '''
        with lock:
            output_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            cv2.flip(output_frame,1)
cv2.namedWindow("webcam",cv2.WINDOW_AUTOSIZE) #the window to show it on created first, for its mode to be editable, the 2nd parameter cv2.WINDOW_AUTOSIZE defines the type of window, here the window fits to size of the image on it, in our case it is a frame
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
#the daemon property refers to whether the thread is terminated when the main thread is terminated or not
#th.Thread() creates a thread object, and target: runs the function that has ALREADY been defined, can also used args: for if the function needs arguements
#above are the two threads in which one updates the global frame numpy array, and the 2nd is for calculation of landmarks and detection of hand, both were moved to a thread to keep the main thread and showing of image fast, especially the detection of landmarks, in the main thread it is too slow, and the result is choppy, but inside the thread it runs parallel to the main thread and stops the frame from being displayed before it is done processing on it parallel to the other threads, only the displaying and editing of frame part is stopped, so the main program still runs smooth while it is running,
while True:
    try:
        root.update_idletasks()
        root.update()
    except tk.TclError:
        pass
    key = cv2.waitKey(1) #detects for key press, takes ms as arguement for how much time to wait, returns the ord value of the key pressed, in our case we use the ord of 'q' that is 113 for ending of the program
    if key==ord('r'): #detect if key r was pressed to shrink the window
        flag=1 #shrink mode to control the code inside thread
    elif key==ord('t'): #detect if t was pressed to expand the window insteadq
        flag=-1 #expand mode to control the code inside thread
    elif key==ord('q'):
        flag_mediapipe, flag_update_frame=0,0 #so the threads run for a bit while longer even after the webcam has been stopped, that results in a none frame, and that crashes the two threads, it dosent matter though since the main thread is suppose to close after that, but if we close the two threads before breaking the main thread's loop, we avoid the error message
        break
    elif key==ord("l"):
        if result!=0 and len(result.hand_landmarks)>0:
            print(f"\none hand index finger x:{result.hand_landmarks[0][8].x} y:{result.hand_landmarks[0][8].y} z:{result.hand_landmarks[0][8].z}")
            if len(result.hand_landmarks)>1:
                print(f"\nsecond hand index finger x:{result.hand_landmarks[1][8].x} y:{result.hand_landmarks[1][8].y} z:{result.hand_landmarks[1][8].z}")
    with lock:
        ret, frame = camera.read()
        if len(frame)!=0:
                frame = cv2.flip(frame, 1) #the reading returns a flipped image, creating a mirror effect, it must be flipped back, cv2.flip() takes the frame as parameter, and the 2nd parameter is for its mode, 1 for horizontal flip, 0 for vertical flip and -1 for both
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #opencv is a old library, so it follows the BGR method that was standard before RGB became universal, mediapipe takes RGB so it must be converted
        if ret and (output_frame is not None):
            cv2.imshow("webcam",output_frame) #a basic cv2 function to show the image, with the name of the window being as first parameter, and the actual numpy array as 2nd parameter, uses the BGR format for displaying
        elif not ret:
            print("Failed to read!") #incase the reading of camera fails this returns 
            break
camera.release() #release the camera rom capturing anything more
cv2.destroyAllWindows() #destroy any lingering window made by cv2
root.destroy()