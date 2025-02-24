import cv2
import numpy as np
import time
import json
import os
from pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother
import mediapipe as mp

# ----- PARAMETERS & SETTINGS -----
BENT_ANGLE = 50       # Angle considered "fully bent"
EXTENDED_ANGLE = 160  # Angle considered "fully extended"
SMOOTHING_WINDOW = 5  # Number of frames for angle smoothing
POSTURE_THRESHOLD = 5  # Allowed deviation (in degrees) for shoulder tilt
TARGET_REPS = 20      # Optional target rep count for progress bar

# Gesture detection settings for mode selection (in pixels and frames)
GESTURE_FRAME_THRESHOLD = 30   # ~1 second at 30 FPS
MODE_PIXEL_THRESHOLD = 50      # How far the wrist must be from the shoulder

# Initialize MediaPipe for drawing landmarks
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# ----- SAVE PROGRESS FUNCTION -----
def save_progress(user, left_reps, right_reps):
    data = {"user": user, "left_reps": left_reps, "right_reps": right_reps}
    with open("progress.json", "w") as f:
        json.dump(data, f)

# ----- MAIN FUNCTION FOR BICEP CURLS -----
def run_bicep_curls():
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # video_path = os.path.join(script_dir, "pushupstest.mp4")
    # cap = cv2.VideoCapture(video_path)
    cap = cv2.VideoCapture(0)
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

    # Session states: "waiting" -> "calibrating" -> "active"
    session_state = "waiting"
    calibration_data = []
    calibration_target_frames = 30  # frames for calibration
    baseline_shoulder_tilt = None
    session_start_time = None

    # Rep counting variables (separate for left and right)
    left_count = 0
    right_count = 0
    left_flag = False  # to track left arm state
    right_flag = False

    left_smoother = Smoother(window_size=SMOOTHING_WINDOW)
    right_smoother = Smoother(window_size=SMOOTHING_WINDOW)

    # Reset gesture: both hands raised above the nose for consecutive frames
    reset_gesture_counter = 0

    # Mode selection variables
    mode = "both"  # default mode is both arms
    left_mode_counter = 0
    right_mode_counter = 0
    both_mode_counter = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # mirror view for natural feedback
        height, width, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process pose using MediaPipe (for drawing) and MoveNet (for keypoints)
        results = pose.process(image)
        keypoints = detect_pose(image)

        # Extract keypoints by index (MoveNet ordering)
        # Index 0: nose, 5: left_shoulder, 6: right_shoulder,
        # 7: left_elbow, 8: right_elbow, 9: left_wrist, 10: right_wrist.
        nose = keypoints[0]
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_elbow = keypoints[7]
        right_elbow = keypoints[8]
        left_wrist = keypoints[9]
        right_wrist = keypoints[10]

        # Calculate elbow angles and smooth them
        raw_left_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
        raw_right_angle = calc_angle(right_shoulder, right_elbow, right_wrist)
        left_angle = left_smoother.update(raw_left_angle)
        right_angle = right_smoother.update(raw_right_angle)

        # Compute shoulder tilt (for posture feedback)
        current_shoulder_tilt = compute_shoulder_tilt(left_shoulder, right_shoulder)
        posture_alert = False
        if baseline_shoulder_tilt is not None and abs(current_shoulder_tilt - baseline_shoulder_tilt) > POSTURE_THRESHOLD:
            posture_alert = True

        # ----------- SESSION STATE MANAGEMENT -----------
        if session_state == "waiting":
            # Wait for a starting signal: arms crossed (wrists near opposite shoulders)
            shoulder_distance = np.linalg.norm(np.array(left_shoulder) - np.array(right_shoulder))
            cross_threshold = shoulder_distance * 0.6
            dist_left = np.linalg.norm(np.array(left_wrist) - np.array(right_shoulder))
            dist_right = np.linalg.norm(np.array(right_wrist) - np.array(left_shoulder))
            if dist_left < cross_threshold and dist_right < cross_threshold:
                session_state = "calibrating"
                calibration_data = []
            instruction = "Cross your arms to start"
            (tw, th), _ = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            cv2.putText(frame, instruction, ((width - tw) // 2, (height + th) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        elif session_state == "calibrating":
            instruction = "Hold a neutral pose for calibration..."
            (tw, th), _ = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            cv2.putText(frame, instruction, ((width - tw) // 2, (height + th) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
            calibration_data.append(current_shoulder_tilt)
            if len(calibration_data) >= calibration_target_frames:
                baseline_shoulder_tilt = np.mean(calibration_data)
                session_state = "active"
                session_start_time = time.time()

        elif session_state == "active":
            # --------- MODE-BASED REP COUNTING ---------
            # Count only for the selected mode:
            if mode == "both":
                # Count both arms
                if left_angle > EXTENDED_ANGLE:
                    left_flag = False
                if left_angle < BENT_ANGLE and not left_flag:
                    left_count += 1
                    left_flag = True

                if right_angle > EXTENDED_ANGLE:
                    right_flag = False
                if right_angle < BENT_ANGLE and not right_flag:
                    right_count += 1
                    right_flag = True

            elif mode == "left":
                if left_angle > EXTENDED_ANGLE:
                    left_flag = False
                if left_angle < BENT_ANGLE and not left_flag:
                    left_count += 1
                    left_flag = True

            elif mode == "right":
                if right_angle > EXTENDED_ANGLE:
                    right_flag = False
                if right_angle < BENT_ANGLE and not right_flag:
                    right_count += 1
                    right_flag = True

            # Elapsed time and total reps (depending on mode)
            elapsed_time = time.time() - session_start_time
            if mode == "both":
                total_reps = left_count + right_count
            elif mode == "left":
                total_reps = left_count
            else:  # mode == "right"
                total_reps = right_count

            # Information panel (time, reps, current mode)
            panel_height = 100
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, panel_height), (50, 50, 50), -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
            cv2.putText(frame, f"Time: {int(elapsed_time)} sec", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Reps: {total_reps}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Mode: {mode.upper()} ARM", (width - 250, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
            progress_ratio = min(total_reps / TARGET_REPS, 1.0)
            bar_width = int(width * progress_ratio)
            cv2.rectangle(frame, (0, panel_height - 10), (bar_width, panel_height), (0, 255, 0), -1)
            cv2.putText(frame, "Reset: Raise both hands above your head", (10, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            if posture_alert:
                cv2.putText(frame, "Adjust your posture!", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # --------- GESTURE-BASED RESET ---------
        # Reset if both wrists are above the nose
        if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
            reset_gesture_counter += 1
            cv2.putText(frame, "Reset gesture detected...", (width - 300, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            reset_gesture_counter = 0

        if reset_gesture_counter > GESTURE_FRAME_THRESHOLD:
            left_count = 0
            right_count = 0
            left_flag = False
            right_flag = False
            session_state = "waiting"
            calibration_data = []
            baseline_shoulder_tilt = None
            session_start_time = None
            reset_gesture_counter = 0
            cv2.putText(frame, "Session reset!", (10, height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # --------- MODE SELECTION GESTURE DETECTION ---------
        # Define gestures based on lateral wrist movement relative to shoulder.
        left_gesture_active = left_wrist[0] < left_shoulder[0] - MODE_PIXEL_THRESHOLD
        right_gesture_active = right_wrist[0] > right_shoulder[0] + MODE_PIXEL_THRESHOLD

        # Use counters for consecutive frames to update the mode:
        if left_gesture_active and right_gesture_active:
            both_mode_counter += 1
            left_mode_counter = 0
            right_mode_counter = 0
        elif left_gesture_active and not right_gesture_active:
            left_mode_counter += 1
            both_mode_counter = 0
            right_mode_counter = 0
        elif right_gesture_active and not left_gesture_active:
            right_mode_counter += 1
            both_mode_counter = 0
            left_mode_counter = 0
        else:
            both_mode_counter = 0
            left_mode_counter = 0
            right_mode_counter = 0

        if both_mode_counter > GESTURE_FRAME_THRESHOLD:
            mode = "both"
        elif left_mode_counter > GESTURE_FRAME_THRESHOLD:
            mode = "left"
        elif right_mode_counter > GESTURE_FRAME_THRESHOLD:
            mode = "right"

        # --------- DRAW LANDMARKS ---------
        # Change landmark color based on posture (green if good, red if alert)
        landmark_color = (0, 255, 0) if not posture_alert else (0, 0, 255)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=landmark_color, thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2))

        cv2.imshow('AI Fitness Trainer - Bicep Curls', frame)
        key = cv2.waitKey(30) & 0xFF
        if key == 27:  # ESC to exit
            break

    save_progress("User1", left_count, right_count)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_bicep_curls()
