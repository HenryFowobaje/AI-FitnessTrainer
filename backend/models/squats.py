import cv2
import numpy as np
import time
import json
import mediapipe as mp
import logging
import os
from pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother

# ---------- Logging & Configuration ----------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class Config:
    MIN_SQUAT_ANGLE = 80     # Deep squat position
    MAX_SQUAT_ANGLE = 170    # Fully standing position
    SMOOTHING_WINDOW = 5     # Frames for angle smoothing
    TORSO_ANGLE_THRESHOLD = 15  # Max degrees from vertical to consider "upright"
    TARGET_REPS = 20         # Target squat count (if used for progress)
    VIDEO_SOURCE = 0         # Default webcam

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
    
    # Reference vector for "perfectly vertical" pointing down: (0, 1)
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

# ---------- Squat Counter Class ----------
class SquatCounter:
    def __init__(self, config: Config):
        self.config = config
        self.squat_count = 0
        self.squat_flag = False  # True when user is in "down" position
        self.angle_smoother = Smoother(window_size=config.SMOOTHING_WINDOW)

    def process_keypoints(self, keypoints):
        """Process keypoints to update the squat count and determine feedback."""
        if len(keypoints) < 17:
            return None, "Insufficient keypoints detected"

        # Landmarks for left side (side-view assumption):
        left_shoulder = keypoints[5]
        left_hip = keypoints[11]
        left_knee = keypoints[13]
        left_ankle = keypoints[15]

        # Calculate knee angle
        avg_knee_angle = calc_angle(left_hip, left_knee, left_ankle)
        avg_knee_angle = self.angle_smoother.update(avg_knee_angle)

        # Calculate torso angle
        torso_angle = compute_torso_angle(left_shoulder, left_hip)
        upright_torso = torso_angle < self.config.TORSO_ANGLE_THRESHOLD

        # Rep counting logic
        if upright_torso:
            # "down" if knee angle < MIN_SQUAT_ANGLE
            if avg_knee_angle < self.config.MIN_SQUAT_ANGLE and not self.squat_flag:
                self.squat_flag = True
            # "up" if knee angle > MAX_SQUAT_ANGLE
            elif avg_knee_angle > self.config.MAX_SQUAT_ANGLE and self.squat_flag:
                self.squat_count += 1
                self.squat_flag = False

        # Feedback
        if not upright_torso:
            feedback = "Fix Torso"
        else:
            feedback = "Down" if self.squat_flag else "Up"

        return avg_knee_angle, feedback

# ---------- Utility Functions ----------
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
    """Renders the UI overlay (slider, progress, rep counter, feedback) on the frame."""
    height, width, _ = frame.shape
    overlay = frame.copy()

    # 1) Vertical Slider
    slider_x = width - 50
    slider_top = 50
    slider_bottom = 380
    cv2.line(overlay, (slider_x, slider_top), (slider_x, slider_bottom), (0, 255, 0), 3)
    
    # Map knee angle to slider knob position
    slider_knob_y = int(np.interp(
        avg_knee_angle, 
        [config.MIN_SQUAT_ANGLE, config.MAX_SQUAT_ANGLE],
        [slider_bottom, slider_top]
    ))
    cv2.circle(overlay, (slider_x, slider_knob_y), 12, (0, 255, 0), -1)
    cv2.putText(overlay, feedback,
                (slider_x - 70, slider_knob_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # 2) Progress percentage
    progress = np.interp(
        avg_knee_angle, 
        (config.MIN_SQUAT_ANGLE, config.MAX_SQUAT_ANGLE), 
        (0, 100)
    )
    cv2.putText(overlay, f'{int(progress)}%', (slider_x - 30, slider_bottom + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # 3) Squat counter box
    cv2.rectangle(overlay, (20, height - 100), (150, height - 20), (0, 255, 0), cv2.FILLED)
    cv2.putText(overlay, str(squat_count), (50, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
    
    # 4) Feedback text
    cv2.rectangle(overlay, (width // 2 - 70, 10), (width // 2 + 70, 50), (255, 255, 255), cv2.FILLED)
    cv2.putText(overlay, feedback, (width // 2 - 50, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Blend the overlay with the original frame
    return cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

# ---------- Main Function ----------
def run_squat_trainer():
    config = Config()
    
    # If using a video file for testing, set up the path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "squats.mp4")
    cap = cv2.VideoCapture(video_path)
    
    # If you want to use the webcam instead, comment out the lines above
    # and uncomment these:
    # cap = cv2.VideoCapture(config.VIDEO_SOURCE)

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

            # For testing with a recorded video, you may not want to mirror the frame
            # frame = cv2.flip(frame, 1)

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            # Get keypoints from MoveNet
            keypoints = detect_pose(image_rgb)
            avg_knee_angle, feedback = squat_counter.process_keypoints(keypoints)
            if avg_knee_angle is None:
                cv2.imshow('Squat Trainer', frame)
                if cv2.waitKey(30) & 0xFF == 27:  # ESC to exit
                    break
                continue

            # Render UI
            frame = render_ui(frame, avg_knee_angle, feedback, squat_counter.squat_count, config)

            # Draw skeleton if available
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Squat Trainer', frame)
            if cv2.waitKey(30) & 0xFF == 27:  # ESC to exit
                break
    except Exception as e:
        logging.exception("An error occurred during squat training: %s", e)
    finally:
        save_progress(user, squat_counter.squat_count)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_squat_trainer()
