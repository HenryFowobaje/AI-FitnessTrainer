import cv2
import numpy as np
import time
import json
import mediapipe as mp
from pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother

# ----- PARAMETERS -----
BENT_ANGLE = 90        # Elbow angle at the lowest push-up position
EXTENDED_ANGLE = 160   # Elbow angle at the highest push-up position
SMOOTHING_WINDOW = 5   # Number of frames for angle smoothing
POSTURE_THRESHOLD = 5  # Allowed deviation for shoulder tilt (in degrees)
TARGET_REPS = 20       # Example target for progress tracking

# Initialize MediaPipe for drawing the skeleton overlay
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def save_progress(user, pushup_count):
    """Saves push-up progress in a JSON file."""
    data = {"user": user, "pushups": pushup_count}
    with open("pushup_progress.json", "w") as f:
        json.dump(data, f)

def run_pushups():
    cap = cv2.VideoCapture(0)
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

    # Push-up counting variables
    pushup_count = 0
    pushup_flag = False  # True when user is in the "down" position
    form = 0             # 0 means form not detected yet, 1 means good form

    angle_smoother = Smoother(window_size=SMOOTHING_WINDOW)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Flip the frame for a mirrored (selfie) view
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 1) Use MediaPipe for drawing the skeleton
        results = pose.process(image)

        # 2) Use MoveNet (detect_pose) for keypoints
        keypoints = detect_pose(image)

        # Basic check: ensure we have enough keypoints from MoveNet
        if len(keypoints) < 17:
            cv2.imshow('Push-Up Trainer', frame)
            if cv2.waitKey(30) & 0xFF == 27:
                break
            continue

        # Extract key landmarks (based on MoveNet indexing)
        left_shoulder, right_shoulder = keypoints[5], keypoints[6]
        left_elbow, right_elbow       = keypoints[7], keypoints[8]
        left_hip, right_hip           = keypoints[11], keypoints[12]

        # Calculate elbow angles (left & right)
        left_elbow_angle = calc_angle(left_shoulder, left_elbow, left_hip)
        right_elbow_angle = calc_angle(right_shoulder, right_elbow, right_hip)
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

        # Smooth the elbow angle for stability
        avg_elbow_angle = angle_smoother.update(avg_elbow_angle)

        # Calculate shoulder tilt to check posture
        shoulder_tilt = compute_shoulder_tilt(left_shoulder, right_shoulder)

        # Check if the user has correct form (arms extended & minimal shoulder tilt)
        if avg_elbow_angle > EXTENDED_ANGLE and abs(shoulder_tilt) < POSTURE_THRESHOLD:
            form = 1  # Good form detected
        else:
            # If posture breaks, set form back to 0 if you want strict form requirement
            # But you can keep it at 1 if you only require form at the start of each rep
            pass

        # Provide feedback
        feedback = "Fix Form" if form == 0 else ("Down" if pushup_flag else "Up")

        # --- Rep Counting Logic ---
        if form == 1:
            if avg_elbow_angle < BENT_ANGLE and not pushup_flag:
                # User has reached the "down" position
                pushup_flag = True
            if avg_elbow_angle > EXTENDED_ANGLE and pushup_flag:
                # Completed a push-up
                pushup_count += 1
                pushup_flag = False

        # ---------- UI OVERLAY ----------
        overlay = frame.copy()

        # 1) Vertical Slider (Line + Moving Knob)
        slider_x = width - 50
        slider_top = 50
        slider_bottom = 380
        # Draw the slider line
        cv2.line(overlay, (slider_x, slider_top), (slider_x, slider_bottom), (0, 255, 0), 3)

        # Map the elbow angle to a slider knob position
        slider_knob_y = int(np.interp(avg_elbow_angle, 
                                      [BENT_ANGLE, EXTENDED_ANGLE],
                                      [slider_bottom, slider_top]))
        # Draw the knob as a filled circle
        cv2.circle(overlay, (slider_x, slider_knob_y), 12, (0, 255, 0), -1)

        # Display the "Up"/"Down" text next to the knob
        cv2.putText(overlay, "Up" if pushup_flag == False else "Down",
                    (slider_x - 70, slider_knob_y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # 2) Show progress percentage below the slider
        progress = np.interp(avg_elbow_angle, (BENT_ANGLE, EXTENDED_ANGLE), (0, 100))
        cv2.putText(overlay, f'{int(progress)}%', (slider_x - 30, slider_bottom + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 3) Push-up counter box (bottom-left)
        cv2.rectangle(overlay, (20, height - 100), (150, height - 20), (0, 255, 0), cv2.FILLED)
        cv2.putText(overlay, str(pushup_count), (50, height - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        # 4) Feedback text (center top)
        cv2.rectangle(overlay, (width // 2 - 70, 10), (width // 2 + 70, 50), (255, 255, 255), cv2.FILLED)
        cv2.putText(overlay, feedback, (width // 2 - 50, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Blend the overlay with the original frame
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        # Draw the skeleton via MediaPipe if available
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Push-Up Trainer', frame)
        key = cv2.waitKey(30) & 0xFF
        if key == 27:  # ESC to exit
            break

    save_progress("User1", pushup_count)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_pushups()
