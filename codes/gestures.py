import warnings

# Suppress specific warning from google.protobuf
warnings.filterwarnings('ignore', category=UserWarning, message='SymbolDatabase.GetPrototype() is deprecated')

import cv2
import mediapipe as mp
import pyautogui
import math
import time

#fingers closed to pause video
def press_space(prev_distance, curr_distance, fingers_closed): 
    if fingers_closed and prev_distance - curr_distance > 20:    # Adjust the threshold as needed
        pyautogui.press('space')
        pyautogui.sleep(0.1)  # Adjust the sleep time as needed

#fingers open to swipe left or right
def swipe(index_initial_x, index_final_x, fingers_open): 
    if fingers_open and index_final_x - index_initial_x > 200:  # Adjust the threshold as needed
        pyautogui.press('right')
        pyautogui.sleep(0.1)  # Adjust the sleep time as needed
    elif fingers_open and index_initial_x - index_final_x > 200:  # Adjust the threshold as needed
        pyautogui.press('left')
        pyautogui.sleep(0.1)  # Adjust the sleep time as needed

# Test the cameras and choose the first working one
for camera_index in range(1, 2):  # Adjust the range as needed
    cap = cv2.VideoCapture(camera_index)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', camera_index)
    else:
        print('Success: able to open video source: ', camera_index)
        break

hand_detection = mp.solutions.hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size() 
middles_x, middles_y = screen_width//2, screen_height//2

index_initial_x = None
prev_distance = None
frame_skip = 2  # Process every 2nd frame
frame_count = 0

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape

    # Skip frames to reduce processing load
    frame_count += 1
    if frame_count % frame_skip != 0:
        continue

    # Reduce frame size for faster processing
    small_frame = cv2.resize(frame, (320, 240))
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    output = hand_detection.process(rgb_frame)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            fingers_open = True
            for id, lm in enumerate(hand.landmark):
                x, y = int(lm.x * frame_width), int(lm.y * frame_height)
                if id == 8:  # Index finger tip
                    index_x, index_y = x, y
                if id in [6, 10, 14, 18]:  # PIP joints
                    pip_x, pip_y = x, y
                if id in [8, 12, 16, 20]:  # Finger tips
                    if y >= pip_y:
                        fingers_open = False
            if index_initial_x is None:
                index_initial_x = index_x
            else:
                swipe(index_initial_x, index_x, fingers_open)
                index_initial_x = index_x

            if prev_distance is None:
                prev_distance = math.hypot(index_x - middles_x, index_y - middles_y)
            else:
                curr_distance = math.hypot(index_x - middles_x, index_y - middles_y)
                press_space(prev_distance, curr_distance, not fingers_open)
                prev_distance = curr_distance

    # Display the frame
    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()