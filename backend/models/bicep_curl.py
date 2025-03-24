import cv2
import numpy as np
import json
import time
from collections import deque

from .pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother
import mediapipe as mp

# ----- PARAMETERS & SETTINGS -----
BENT_ANGLE = 50       # Angle considered "fully bent"
EXTENDED_ANGLE = 160  # Angle considered "fully extended"
SMOOTHING_WINDOW = 5  # Number of frames for angle smoothing
POSTURE_THRESHOLD = 5  # Allowed deviation (in degrees) for shoulder tilt
TARGET_REPS = 20      # Target rep count for progress bar

GESTURE_FRAME_THRESHOLD = 30   # ~1 second at 30 FPS
MODE_PIXEL_THRESHOLD = 50      # How far the wrist must be from the shoulder

# Initialize MediaPipe for drawing landmarks (if needed)
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# ----- SAVE PROGRESS FUNCTION -----
def save_progress(user, left_reps, right_reps, filename="progress.json"):
    data = {"user": user, "left_reps": left_reps, "right_reps": right_reps, "timestamp": time.time()}
    with open(filename, "w") as f:
        json.dump(data, f)

# ----- PROCESSING FUNCTION FOR BICEP CURLS -----
def process_bicep_frame(frame, state):
    """
    Processes a single frame for bicep curls.
    
    The state dictionary holds:
      - session_state: "waiting", "calibrating", or "active"
      - calibration_data: list of shoulder tilt measurements during calibration
      - calibration_target_frames: number of frames to calibrate (e.g. 30)
      - baseline_shoulder_tilt: computed average from calibration
      - session_start_time: time when active session began
      - left_count, right_count: rep counters
      - left_flag, right_flag: booleans for rep detection
      - left_smoother, right_smoother: Smoother instances for angle smoothing
      - left_angle, right_angle: current smoothed elbow angles
      - posture_alert: boolean flag for poor posture
      - mode: "both", "left", or "right"
      - left_mode_counter, right_mode_counter, both_mode_counter: for gesture-based mode selection
      - reset_gesture_counter: for resetting the session
      - mode_pixel_threshold, gesture_frame_threshold: parameters for gestures
      - pose: MediaPipe Pose instance
    """
    # Mirror and prepare the frame
    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process pose using MediaPipe (for drawing later)
    results = state['pose'].process(rgb_frame)
    # Get keypoints using the shared detect_pose function
    keypoints = detect_pose(rgb_frame)
    if len(keypoints) < 11:
        return frame, state  # Not enough keypoints detected
    
    # Extract keypoints by index (MoveNet ordering)
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
    left_angle = state['left_smoother'].update(raw_left_angle)
    right_angle = state['right_smoother'].update(raw_right_angle)
    state['left_angle'] = left_angle
    state['right_angle'] = right_angle
    
    # Compute shoulder tilt for posture feedback
    current_shoulder_tilt = compute_shoulder_tilt(left_shoulder, right_shoulder)
    posture_alert = False
    if state['baseline_shoulder_tilt'] is not None and abs(current_shoulder_tilt - state['baseline_shoulder_tilt']) > POSTURE_THRESHOLD:
        posture_alert = True
    state['posture_alert'] = posture_alert
    
    # Session state management
    if state['session_state'] == "waiting":
        # Wait for a starting signal: arms crossed (wrists near opposite shoulders)
        shoulder_distance = np.linalg.norm(np.array(left_shoulder) - np.array(right_shoulder))
        cross_threshold = shoulder_distance * 0.6
        dist_left = np.linalg.norm(np.array(left_wrist) - np.array(right_shoulder))
        dist_right = np.linalg.norm(np.array(right_wrist) - np.array(left_shoulder))
        if dist_left < cross_threshold and dist_right < cross_threshold:
            state['session_state'] = "calibrating"
            state['calibration_data'] = []
        instruction = "Cross your arms to start"
        cv2.putText(frame, instruction, ((width - 300) // 2, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    elif state['session_state'] == "calibrating":
        instruction = "Hold a neutral pose for calibration..."
        cv2.putText(frame, instruction, ((width - 400) // 2, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        state['calibration_data'].append(current_shoulder_tilt)
        if len(state['calibration_data']) >= state['calibration_target_frames']:
            state['baseline_shoulder_tilt'] = np.mean(state['calibration_data'])
            state['session_state'] = "active"
            state['session_start_time'] = time.time()
    elif state['session_state'] == "active":
        # Mode-based rep counting
        if state['mode'] == "both":
            if left_angle > EXTENDED_ANGLE:
                state['left_flag'] = False
            if left_angle < BENT_ANGLE and not state['left_flag']:
                state['left_count'] += 1
                state['left_flag'] = True
            if right_angle > EXTENDED_ANGLE:
                state['right_flag'] = False
            if right_angle < BENT_ANGLE and not state['right_flag']:
                state['right_count'] += 1
                state['right_flag'] = True
        elif state['mode'] == "left":
            if left_angle > EXTENDED_ANGLE:
                state['left_flag'] = False
            if left_angle < BENT_ANGLE and not state['left_flag']:
                state['left_count'] += 1
                state['left_flag'] = True
        elif state['mode'] == "right":
            if right_angle > EXTENDED_ANGLE:
                state['right_flag'] = False
            if right_angle < BENT_ANGLE and not state['right_flag']:
                state['right_count'] += 1
                state['right_flag'] = True
        
        # Overlay information panel
        elapsed_time = time.time() - state['session_start_time'] if state['session_start_time'] else 0
        if state['mode'] == "both":
            total_reps = state['left_count'] + state['right_count']
        elif state['mode'] == "left":
            total_reps = state['left_count']
        else:
            total_reps = state['right_count']
        panel_height = 100
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, panel_height), (50, 50, 50), -1)
        cv2.putText(overlay, f"Time: {int(elapsed_time)} sec", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(overlay, f"Reps: {total_reps}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(overlay, f"Mode: {state['mode'].upper()} ARM", (width - 250, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
        progress_ratio = min(total_reps / TARGET_REPS, 1.0)
        bar_width = int(width * progress_ratio)
        cv2.rectangle(overlay, (0, panel_height - 10), (bar_width, panel_height), (0, 255, 0), -1)
        cv2.putText(overlay, "Reset: Raise both hands above your head", (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        if posture_alert:
            cv2.putText(overlay, "Adjust your posture!", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # Mode selection gesture detection
        left_gesture_active = left_wrist[0] < left_shoulder[0] - state['mode_pixel_threshold']
        right_gesture_active = right_wrist[0] > right_shoulder[0] + state['mode_pixel_threshold']
        if left_gesture_active and right_gesture_active:
            state['both_mode_counter'] += 1
            state['left_mode_counter'] = 0
            state['right_mode_counter'] = 0
        elif left_gesture_active and not right_gesture_active:
            state['left_mode_counter'] += 1
            state['both_mode_counter'] = 0
            state['right_mode_counter'] = 0
        elif right_gesture_active and not left_gesture_active:
            state['right_mode_counter'] += 1
            state['both_mode_counter'] = 0
            state['left_mode_counter'] = 0
        else:
            state['both_mode_counter'] = 0
            state['left_mode_counter'] = 0
            state['right_mode_counter'] = 0

        if state['both_mode_counter'] > state['gesture_frame_threshold']:
            state['mode'] = "both"
        elif state['left_mode_counter'] > state['gesture_frame_threshold']:
            state['mode'] = "left"
        elif state['right_mode_counter'] > state['gesture_frame_threshold']:
            state['mode'] = "right"

        # Gesture-based reset
        if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
            state['reset_gesture_counter'] += 1
            cv2.putText(frame, "Reset gesture detected...", (width - 300, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            state['reset_gesture_counter'] = 0

        if state['reset_gesture_counter'] > state['gesture_frame_threshold']:
            state['left_count'] = 0
            state['right_count'] = 0
            state['left_flag'] = False
            state['right_flag'] = False
            state['session_state'] = "waiting"
            state['calibration_data'] = []
            state['baseline_shoulder_tilt'] = None
            state['session_start_time'] = None
            state['reset_gesture_counter'] = 0
            cv2.putText(frame, "Session reset!", (10, height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Optionally draw landmarks from MediaPipe
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(255,0,0), thickness=2, circle_radius=2))
    
    return frame, state
