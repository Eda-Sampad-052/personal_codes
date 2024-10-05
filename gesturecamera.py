import cv2
import pyautogui
import mediapipe as mp
import time

# List all available camera devices
def list_cameras():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

# Prompt the user to select a camera device
def select_camera():
    cameras = list_cameras()
    if not cameras:
        print("No camera devices found.")
        return None
    print("Available camera devices:")
    for i, cam in enumerate(cameras):
        print(f"{i}: Camera {cam}")
    selected_index = int(input("Select a camera device by index: "))
    return cameras[selected_index]

#fingers closed to pause video
def press_space(prev_distance, curr_distance, fingers_closed): 
    if fingers_closed and prev_distance - curr_distance > 20:    # Adjust the threshold as needed
        pyautogui.press('space')
        time.sleep(0.1)  # Adjust the sleep time as needed

#fingers open to swipe left or right
def swipe(index_initial_x, index_final_x, fingers_open): 
    if fingers_open and index_final_x - index_initial_x > 200:  # Adjust the threshold as needed
        pyautogui.press('right')
        time.sleep(0.1)  # Adjust the sleep time as needed
    elif fingers_open and index_initial_x - index_final_x > 200:  # Adjust the threshold as needed
        pyautogui.press('left')
        time.sleep(0.1)  # Adjust the sleep time as needed

# Select and open the camera device
camera_index = select_camera()
if camera_index is None:
    exit()

cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    print(f"Warning: unable to open video source: {camera_index}")
    exit()
else:
    print(f"Success: able to open video source: {camera_index}")

hand_detection = mp.solutions.hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
middles_x, middles_y = screen_width // 2, screen_height // 2

index_initial_x = None
prev_distance = None
frame_skip = 2  # Process every 2nd frame
frame_count = 0

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and detect hands
    results = hand_detection.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
            
            # Get the coordinates of the index finger tip and middle finger tip
            index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
            
            index_x, index_y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)
            middle_x, middle_y = int(middle_finger_tip.x * screen_width), int(middle_finger_tip.y * screen_height)
            
            # Calculate the distance between the index finger tip and middle finger tip
            curr_distance = ((index_x - middle_x) ** 2 + (index_y - middle_y) ** 2) ** 0.5
            
            # Check if fingers are closed or open
            fingers_closed = curr_distance < 50  # Adjust the threshold as needed
            fingers_open = curr_distance > 200  # Adjust the threshold as needed
            
            # Perform actions based on finger positions
            if index_initial_x is None:
                index_initial_x = index_x
            else:
                swipe(index_initial_x, index_x, fingers_open)
                press_space(prev_distance, curr_distance, fingers_closed)
            
            prev_distance = curr_distance
    
    cv2.imshow('Hand Tracking', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()