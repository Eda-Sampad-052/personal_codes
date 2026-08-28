import warnings 

# Suppress specific warning from google.protobuf to avoid unnecessary messages in the console.
warnings.filterwarnings('ignore', category=UserWarning, message='SymbolDatabase.GetPrototype() is deprecated')

# Import necessary libraries
import cv2  # Library for computer vision and image processing
import mediapipe as mp  # Library for hand detection and tracking
import pyautogui  # Library for simulating keyboard and mouse events
import math  # Library for mathematical functions

# Function to pause or play the video when fingers are closed
def press_space(prev_distance, curr_distance, fingers_closed): 
    # Check if fingers are closed and the distance to the screen has changed significantly
    if fingers_closed and prev_distance - curr_distance > 20:  # The threshold can be adjusted
        pyautogui.press('space')  # Simulate pressing the space bar to pause or play the video
        pyautogui.sleep(0.1)  # Small delay to prevent multiple presses

# Function to swipe left or right based on finger movement
def swipe(index_initial_x, index_final_x, fingers_open): 
    # Check if fingers are open and calculate the horizontal movement
    if fingers_open and index_final_x - index_initial_x > 200:  # Adjust the threshold as needed
        pyautogui.press('right')  # Simulate pressing the right arrow key
        pyautogui.sleep(0.1)  # Small delay to prevent multiple presses
    elif fingers_open and index_initial_x - index_final_x > 200:  # Check for left swipe
        pyautogui.press('left')  # Simulate pressing the left arrow key
        pyautogui.sleep(0.1)  # Small delay to prevent multiple presses

# Test the cameras and choose the first working one
for camera_index in range(1, 2):  # Check camera indices (can be adjusted if needed)
    cap = cv2.VideoCapture(camera_index)  # Attempt to access the camera
    if cap is None or not cap.isOpened():  # Check if the camera is accessible
        print('Warning: unable to open video source: ', camera_index)  # Inform if the camera can't be opened
    else:
        print('Success: able to open video source: ', camera_index)  # Inform if the camera is successfully opened
        break  # Exit the loop as we found a working camera

# Initialize hand detection using MediaPipe
hand_detection = mp.solutions.hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
drawing_utils = mp.solutions.drawing_utils  # Utility for drawing landmarks on hands
screen_width, screen_height = pyautogui.size()  # Get screen dimensions
middles_x, middles_y = screen_width // 2, screen_height // 2  # Calculate screen center coordinates

index_initial_x = None  # Variable to store the initial x-coordinate of the index finger
prev_distance = None  # Variable to store the previous distance from the center of the screen
frame_skip = 2  # Process every 2nd frame to reduce computational load
frame_count = 0  # Frame counter to keep track of processed frames

# Main loop to continuously capture video frames
while True:
    _, frame = cap.read()  # Read a frame from the camera
    frame = cv2.flip(frame, 1)  # Flip the frame horizontally for a mirror effect
    frame_height, frame_width, _ = frame.shape  # Get the dimensions of the frame

    # Skip frames to reduce processing load
    frame_count += 1  # Increment the frame count
    if frame_count % frame_skip != 0:  # Only process every 2nd frame
        continue  # Skip the rest of the loop and read the next frame

    # Reduce frame size for faster processing
    small_frame = cv2.resize(frame, (320, 240))  # Resize the frame to 320x240 pixels
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # Convert the frame from BGR to RGB color space
    output = hand_detection.process(rgb_frame)  # Process the frame to detect hands
    hands = output.multi_hand_landmarks  # Get the detected hand landmarks

    # Check if any hands are detected
    if hands:
        for hand in hands:  # Loop through detected hands
            fingers_open = True  # Assume fingers are open initially
            # Draw landmarks on the original frame
            drawing_utils.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)  # Draw landmarks and connections on the frame

            for id, lm in enumerate(hand.landmark):  # Loop through each landmark of the detected hand
                x, y = int(lm.x * frame_width), int(lm.y * frame_height)  # Get the x, y coordinates of the landmark
                if id == 8:  # If the landmark is the tip of the index finger
                    index_x, index_y = x, y  # Store the coordinates of the index finger tip
                if id in [6, 10, 14, 18]:  # Check for PIP joints (the second joints of the fingers)
                    pip_x, pip_y = x, y  # Store the coordinates of the PIP joint
                if id in [8, 12, 16, 20]:  # Check for tips of the fingers
                    if y >= pip_y:  # If the finger tip is below the PIP joint, it is considered closed
                        fingers_open = False  # Set fingers_open to False as the finger is not extended
            
            # If it's the first time detecting the index finger
            if index_initial_x is None:
                index_initial_x = index_x  # Store the initial position of the index finger
            else:
                # Call swipe function to check for swiping gestures
                swipe(index_initial_x, index_x, fingers_open)
                index_initial_x = index_x  # Update the index position for the next frame

            # Calculate the distance from the index finger to the center of the screen
            if prev_distance is None:
                prev_distance = math.hypot(index_x - middles_x, index_y - middles_y)  # Calculate initial distance
            else:
                curr_distance = math.hypot(index_x - middles_x, index_y - middles_y)  # Calculate current distance
                # Call function to pause the video if fingers are closed
                press_space(prev_distance, curr_distance, not fingers_open)
                prev_distance = curr_distance  # Update the previous distance for the next iteration

    # Display the processed frame with hand tracking and landmarks
    cv2.imshow('Hand Tracking', frame)  # Show the frame in a window
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Check if the user pressed the 'q' key
        break  # Exit the loop if 'q' is pressed

cap.release()  # Release the camera resource
cv2.destroyAllWindows()  # Close all OpenCV windows
