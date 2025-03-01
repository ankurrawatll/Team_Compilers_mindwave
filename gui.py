# import cv2
# import dlib
# import numpy as np
# from scipy.spatial import distance

# # Load dlib's face detector and landmark predictor
# face_detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# # Function to calculate Eye Aspect Ratio (EAR)
# def eye_aspect_ratio(eye):
#     A = distance.euclidean(eye[1], eye[5])
#     B = distance.euclidean(eye[2], eye[4])
#     C = distance.euclidean(eye[0], eye[3])
#     ear = (A + B) / (2.0 * C)
#     return ear

# # Start video capture
# cap = cv2.VideoCapture(0)

# # Sensitivity settings
# EAR_THRESHOLD = 0.22  # Blink detection threshold
# EYE_MOVEMENT_THRESHOLD = 2  # Adjust sensitivity for left/right detection
# prev_pupil_x = None

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
    
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_detector(gray)
    
#     for face in faces:
#         landmarks = predictor(gray, face)
#         landmarks_points = np.array([[landmarks.part(n).x, landmarks.part(n).y] for n in range(68)])
        
#         left_eye = landmarks_points[36:42]
#         right_eye = landmarks_points[42:48]
        
#         left_ear = eye_aspect_ratio(left_eye)
#         right_ear = eye_aspect_ratio(right_eye)
#         ear = (left_ear + right_ear) / 2.0
        
#         # Detect blinking
#         if ear < EAR_THRESHOLD:
#             cv2.putText(frame, "Blink Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
#         # Pupil position tracking (horizontal movement)
#         pupil_x = (landmarks.part(42).x + landmarks.part(45).x) // 2  # Avg of right eye corners
#         if prev_pupil_x is not None:
#             movement = pupil_x - prev_pupil_x
#             if movement > EYE_MOVEMENT_THRESHOLD:
#                 cv2.putText(frame, "Looking Right", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
#             elif movement < -EYE_MOVEMENT_THRESHOLD:
#                 cv2.putText(frame, "Looking Left", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
#         prev_pupil_x = pupil_x
    
#     cv2.imshow("Eye Tracking", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


# import cv2
# import dlib
# import numpy as np
# from pynput.keyboard import Controller
# from scipy.spatial import distance

# # Initialize keyboard controller
# keyboard = Controller()

# # Load face detector and landmark predictor
# face_detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Ensure the file is in the same folder

# # Function to get the eye center
# def get_eye_center(eye):
#     return np.mean(eye, axis=0).astype(int)

# # Start video capture
# cap = cv2.VideoCapture(0)

# # Sensitivity settings
# MOVEMENT_THRESHOLD = 1.5  # Lower = More sensitivity
# CENTER_TOLERANCE = 2      # How much movement is considered "center"

# prev_pupil_x = None
# screen_center_x = None
# key_pressed = None

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.flip(frame, 1)  # Flip horizontally to correct the mirrored effect
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_detector(gray)

#     for face in faces:
#         landmarks = predictor(gray, face)
#         landmarks_points = np.array([[landmarks.part(n).x, landmarks.part(n).y] for n in range(68)])

#         right_eye = landmarks_points[42:48]
#         pupil_x = get_eye_center(right_eye)[0]  # Get X position of the right eye center
        
#         # Set screen center (first detected position as reference)
#         if screen_center_x is None:
#             screen_center_x = pupil_x
        
#         relative_movement = pupil_x - screen_center_x  # Difference from center
        
#         if relative_movement > MOVEMENT_THRESHOLD:
#             if key_pressed != 'd':
#                 keyboard.release('a')  # Release 'A'
#                 keyboard.press('d')  # Press 'D'
#                 key_pressed = 'd'
#                 print("Looking Right → Pressing 'D'")

#         elif relative_movement < -MOVEMENT_THRESHOLD:
#             if key_pressed != 'a':
#                 keyboard.release('d')  # Release 'D'
#                 keyboard.press('a')  # Press 'A'
#                 key_pressed = 'a'
#                 print("Looking Left → Pressing 'A'")

#         elif abs(relative_movement) < CENTER_TOLERANCE:
#             keyboard.release('a')
#             keyboard.release('d')
#             key_pressed = None
#             print("Centered → Releasing Keys")

#     cv2.imshow("Eye Tracker", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# keyboard.release('a')
# keyboard.release('d')

import cv2
import dlib
import numpy as np
from pynput.keyboard import Controller
from collections import deque

# Initialize keyboard controller
keyboard = Controller()

# Load face detector and landmark predictor
face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Ensure this file is in the same folder

# Function to get the eye center
def get_eye_center(eye):
    return np.mean(eye, axis=0).astype(int)

# Start video capture
cap = cv2.VideoCapture(0)

# Sensitivity settings
MOVEMENT_THRESHOLD = 1.5  # Lower = More sensitivity
CENTER_TOLERANCE = 2      # Small movements don't trigger action
RESET_FRAMES = 100        # Reset center every 100 frames (adaptive)
SMOOTHING_SIZE = 5        # Number of frames to smooth out movements

prev_pupil_x = None
screen_center_x = None
key_pressed = None
frame_count = 0
movement_history = deque(maxlen=SMOOTHING_SIZE)  # Stores past pupil positions

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip horizontally to correct the mirrored effect
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks_points = np.array([[landmarks.part(n).x, landmarks.part(n).y] for n in range(68)])

        right_eye = landmarks_points[42:48]
        pupil_x = get_eye_center(right_eye)[0]  # Get X position of the right eye center
        
        # Store recent positions for smoothing
        movement_history.append(pupil_x)
        smoothed_pupil_x = int(np.mean(movement_history))  # Apply rolling average

        # Set screen center (dynamically resets every RESET_FRAMES)
        if screen_center_x is None or frame_count % RESET_FRAMES == 0:
            screen_center_x = smoothed_pupil_x
            print("🔄 Recalibrating Center...")

        relative_movement = smoothed_pupil_x - screen_center_x  # Difference from center
        
        if relative_movement > MOVEMENT_THRESHOLD:
            if key_pressed != 'd':
                keyboard.release('a')  # Release 'A'
                keyboard.press('d')  # Press 'D'
                key_pressed = 'd'
                print("➡️ Looking Right → Pressing 'D'")

        elif relative_movement < -MOVEMENT_THRESHOLD:
            if key_pressed != 'a':
                keyboard.release('d')  # Release 'D'
                keyboard.press('a')  # Press 'A'
                key_pressed = 'a'
                print("⬅️ Looking Left → Pressing 'A'")

        elif abs(relative_movement) < CENTER_TOLERANCE:
            keyboard.release('a')
            keyboard.release('d')
            key_pressed = None
            print("⏹️ Centered → Releasing Keys")

    frame_count += 1  # Increment frame count
    cv2.imshow("Eye Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
keyboard.release('a')
keyboard.release('d')
