import cv2
import numpy as np
import time
import json
import mediapipe as mp
import logging
import os
from .pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class Config:
    # Adjusted thresholds: these values may need further tuning for your use-case.
    MIN_SQUAT_ANGLE = 120          # Easier-to-reach deep squat position (degrees)
    MAX_SQUAT_ANGLE = 165         # More easily detected full-stand position (degrees)
    SMOOTHING_WINDOW = 3          # Smaller window for quicker responsiveness
    TORSO_ANGLE_THRESHOLD = 20    # Allow a bit of forward lean
    TARGET_REPS = 20              # Target squat count (if used for progress)
    VIDEO_SOURCE = 0              # Default webcam
    MIN_KEYPOINT_CONFIDENCE = 0.3 # Minimum confidence for keypoints to be considered valid
    MIN_REP_INTERVAL = 0.5        # Minimum seconds between rep counts

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def compute_torso_angle(shoulder, hip):
    """
    Computes the angle between the vector (shoulder -> hip) and a perfect vertical vector.
    Returns the angle in degrees, where 0° = perfectly vertical,
    and larger angles mean more forward/backward tilt.
    """
    dx = hip[0] - shoulder[0]
    dy = hip[1] - shoulder[1]
    
    vertical_ref = np.array([0, 1], dtype=np.float32)
    torso_vec = np.array([dx, dy], dtype=np.float32)

    ref_mag = np.linalg.norm(vertical_ref)
    torso_mag = np.linalg.norm(torso_vec)

    if ref_mag == 0 or torso_mag == 0:
        return 0.0

    dot = np.dot(vertical_ref, torso_vec)
    cos_theta = dot / (ref_mag * torso_mag)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    angle_deg = np.degrees(np.arccos(cos_theta))
    return angle_deg

class SquatCounter:
    def __init__(self, config: Config):
        self.config = config
        self.reset()  # Initialize state via reset method

    def reset(self):
        """Reset the internal state of the squat counter."""
        self.squat_count = 0
        self.squat_flag = False  # Reset the squat flag
        self.last_rep_time = 0   # Reset the last rep time
        # Reinitialize the angle smoother for a fresh start.
        self.angle_smoother = Smoother(window_size=self.config.SMOOTHING_WINDOW)

    def process_keypoints(self, keypoints):
        # Ensure sufficient keypoints are present
        if len(keypoints) < 17:
            return None, "Insufficient keypoints detected"

        # Check that keypoints for left shoulder, hip, knee, and ankle meet the confidence threshold.
        required_indices = [5, 11, 13, 15]
        for idx in required_indices:
            if keypoints[idx][2] < self.config.MIN_KEYPOINT_CONFIDENCE:
                return None, "Insufficient keypoints detected"

        # Use only the (x, y) parts for angle calculations.
        left_shoulder = keypoints[5][:2]
        left_hip = keypoints[11][:2]
        left_knee = keypoints[13][:2]
        left_ankle = keypoints[15][:2]

        # Calculate knee angle and smooth it
        knee_angle = calc_angle(left_hip, left_knee, left_ankle)
        avg_knee_angle = self.angle_smoother.update(knee_angle)

        # Calculate torso angle and check if upright (within TORSO_ANGLE_THRESHOLD)
        torso_angle = compute_torso_angle(left_shoulder, left_hip)
        upright_torso = torso_angle < self.config.TORSO_ANGLE_THRESHOLD

        current_time = time.time()

        # Simple state-based rep counting logic:
        if upright_torso:
            # If the knee is bent enough, mark that a squat "down" is detected.
            if avg_knee_angle < self.config.MIN_SQUAT_ANGLE:
                self.squat_flag = True
            # If the knee is extended and we previously detected a "down" phase, count a rep.
            elif avg_knee_angle > self.config.MAX_SQUAT_ANGLE and self.squat_flag:
                if (current_time - self.last_rep_time) >= self.config.MIN_REP_INTERVAL:
                    self.squat_count += 1
                    self.squat_flag = False
                    self.last_rep_time = current_time
        else:
            # If torso is not upright, reset the squat detection flag.
            self.squat_flag = False

        # Provide feedback based on current state
        if not upright_torso:
            feedback = "Fix Torso"
        elif self.squat_flag:
            feedback = "Down"
        else:
            feedback = "Up"
        return avg_knee_angle, feedback


def save_progress(user, squat_count, filename="squat_progress.json"):
    """Saves the squat progress to a JSON file with a timestamp."""
    data = {"user": user, "squats": squat_count, "timestamp": time.time()}
    try:
        with open(filename, "w") as f:
            json.dump(data, f)
        logging.info("Progress saved successfully.")
    except Exception as e:
        logging.error("Failed to save progress: %s", e)

def render_ui(frame, avg_knee_angle, feedback, squat_count, config: Config):
    """Renders the UI overlay (slider, rep counter, and feedback) on the frame."""
    height, width, _ = frame.shape
    overlay = frame.copy()

    # Draw rep counter at the top-left
    cv2.rectangle(overlay, (10, 10), (150, 70), (0, 0, 0), cv2.FILLED)
    cv2.putText(overlay, f"Reps: {squat_count}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw vertical slider on the right side
    slider_x = width - 50
    slider_top = 50
    slider_bottom = height - 50
    cv2.line(overlay, (slider_x, slider_top), (slider_x, slider_bottom), (200, 200, 200), 3)
    # Map knee angle to slider position
    slider_knob_y = int(np.interp(
        avg_knee_angle,
        [config.MIN_SQUAT_ANGLE, config.MAX_SQUAT_ANGLE],
        [slider_bottom, slider_top]
    ))
    # Change knob color based on state: red if "Down", green if "Up"
    knob_color = (0, 0, 255) if feedback == "Down" else (0, 255, 0)
    cv2.circle(overlay, (slider_x, slider_knob_y), 12, knob_color, -1)
    cv2.putText(overlay, f"{int(avg_knee_angle)}°", (slider_x - 70, slider_knob_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, knob_color, 2)

    # Draw feedback text at the bottom center
    cv2.rectangle(overlay, (width // 2 - 100, height - 80), (width // 2 + 100, height - 20), (0, 0, 0), cv2.FILLED)
    cv2.putText(overlay, feedback, (width // 2 - 60, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)

def process_squat_frame(frame, squat_counter, config, pose):
    """
    Processes a single frame:
      - Converts the frame to RGB.
      - Runs pose detection and keypoint extraction.
      - Uses the SquatCounter to compute the knee angle and rep logic.
      - Draws the UI overlay and skeleton if available.
    Returns the annotated frame.
    """
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    keypoints = detect_pose(image_rgb)
    avg_knee_angle, feedback = squat_counter.process_keypoints(keypoints)
    if avg_knee_angle is None:
        avg_knee_angle = config.MAX_SQUAT_ANGLE  
        feedback = "No user detected"
    processed_frame = render_ui(frame, avg_knee_angle, feedback, squat_counter.squat_count, config)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(processed_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return processed_frame

def run_squat_trainer():
    config = Config()
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    if not cap.isOpened():
        logging.error("Error: Could not open video source.")
        return
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    squat_counter = SquatCounter(config)
    user = "User1"
    try:
        while True:
            success, frame = cap.read()
            if not success:
                logging.info("End of video or cannot read frame.")
                break

            frame = process_squat_frame(frame, squat_counter, config, pose)
            cv2.imshow('Squat Trainer', frame)
            if cv2.waitKey(30) & 0xFF == 27:  # Exit on pressing Esc
                break
    except Exception as e:
        logging.exception("An error occurred during squat training: %s", e)
    finally:
        save_progress(user, squat_counter.squat_count)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_squat_trainer()
