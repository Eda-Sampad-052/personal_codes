import cv2  # Importing the OpenCV library for video and image processing
from deepface import DeepFace  # Importing DeepFace for facial analysis, including gender detection

def detect_gender(frame):
    # This function analyzes a given image (frame) to detect gender
    result = DeepFace.analyze(frame, actions=['gender'], enforce_detection=False)
    # The function returns the detected gender from the analysis result
    return result[0]['gender']  # Return the detected gender (e.g., 'Male' or 'Female')

# Start video capture from the webcam
cap = cv2.VideoCapture(0)  # 0 is the index for the default webcam. Change it if you have multiple cameras.

# Check if the webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")  # Print an error message if the webcam cannot be accessed
    exit()  # Exit the program

# Set desired window size for displaying the video
window_width = 640  # Width of the video window in pixels
window_height = 480  # Height of the video window in pixels

while True:  # Start an infinite loop to continuously capture video frames
    # Capture a single frame from the webcam
    ret, frame = cap.read()  # ret is a boolean indicating if the frame was captured successfully, and frame contains the captured image
    if not ret:
        print("Error: Could not read frame.")  # Print an error message if the frame could not be read
        break  # Exit the loop

    # Flip the frame horizontally to create a mirror effect
    frame = cv2.flip(frame, 1)  # 1 indicates a horizontal flip

    # Convert the captured frame from BGR (OpenCV format) to RGB (format expected by DeepFace)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    try:
        # Call the detect_gender function to find out the gender of the person in the frame
        gender = detect_gender(rgb_frame)

        # Display the detected gender on the video frame
        cv2.putText(frame, f"Gender: {gender}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # (10, 30) specifies the position where the text will appear, and (255, 0, 0) specifies the text color (red)).
    except Exception as e:
        # If there is an error (like no face detected), display a message on the frame
        cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # (0, 0, 255) specifies the text color (red).

    # Resize the video frame to fit the specified window size
    resized_frame = cv2.resize(frame, (window_width, window_height))

    # Show the video frame with the gender text in a window
    cv2.imshow("Gender Detection", resized_frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Exit the loop

# Release the video capture object to free up resources and close all OpenCV windows
cap.release()  # Release the webcam
cv2.destroyAllWindows()  # Close all OpenCV windows
