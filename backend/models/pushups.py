import cv2
import numpy as np
import time
import json
import mediapipe as mp
import logging
import os

from pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt, Smoother

# -------------------- Logging & Configuration --------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class Config:
    # Elbow angles for a proper push-up
    BENT_ANGLE = 90         # Elbow angle at the bottom (down phase)
    EXTENDED_ANGLE = 170    # Elbow angle at the top (up phase)
    SMOOTHING_WINDOW = 5    # Frames for angle smoothing
    # Body alignment: the torso (average shoulder to hip line) should be nearly horizontal.
    # In practice, allow a deviation up to 20°.
    BODY_ALIGNMENT_THRESHOLD = 20  
    TARGET_REPS = 20        # Target push-up count (for progress tracking)
    VIDEO_FILENAME = "pushupstest.mp4"  # Use this video file for testing; set to None to use webcam.
    VIDEO_SOURCE = 0        # Use webcam if VIDEO_FILENAME is None.

# Initialize MediaPipe for skeleton overlay drawing
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# -------------------- Helper Function --------------------
def compute_body_alignment_angle(left_shoulder, right_shoulder, left_hip, right_hip):
    """
    Computes the deviation (in degrees) between the line joining the average shoulder and hip 
    positions and the horizontal axis. A perfect push-up should keep the body nearly horizontal.
    """
    avg_shoulder = np.array([(left_shoulder[0] + right_shoulder[0]) / 2,
                             (left_shoulder[1] + right_shoulder[1]) / 2])
    avg_hip = np.array([(left_hip[0] + right_hip[0]) / 2,
                        (left_hip[1] + right_hip[1]) / 2])
    # Vector from shoulders to hips
    vec = avg_hip - avg_shoulder
    horizontal = np.array([1, 0], dtype=np.float32)
    mag = np.linalg.norm(vec)
    if mag == 0:
        return 0.0
    dot = np.dot(vec, horizontal)
    cos_theta = np.clip(dot / mag, -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_theta))
    # Lower angle means closer to horizontal.
    return angle

# -------------------- Pushup Counter Class --------------------
class PushupCounter:
    def __init__(self, config: Config):
        self.config = config
        self.pushup_count = 0
        self.pushup_flag = False  # True when user is in the "down" phase
        self.angle_smoother = Smoother(window_size=config.SMOOTHING_WINDOW)

    def process_keypoints(self, keypoints):
        """
        Processes keypoints and updates the push-up count if a proper rep is detected.
        Returns (avg_elbow_angle, feedback). If keypoints are insufficient, returns (None, error message).
        """
        if len(keypoints) < 17:
            return None, "Insufficient keypoints detected"
        
        # Extract key landmarks using MoveNet indices.
        left_shoulder  = keypoints[5]
        right_shoulder = keypoints[6]
        left_elbow     = keypoints[7]
        right_elbow    = keypoints[8]
        left_wrist     = keypoints[9]
        right_wrist    = keypoints[10]
        left_hip       = keypoints[11]
        right_hip      = keypoints[12]
        
        # Calculate the elbow angles (using shoulder->elbow->wrist).
        left_elbow_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calc_angle(right_shoulder, right_elbow, right_wrist)
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        avg_elbow_angle = self.angle_smoother.update(avg_elbow_angle)
        
        # Compute body alignment angle: deviation of the torso from horizontal.
        body_alignment_angle = compute_body_alignment_angle(left_shoulder, right_shoulder, left_hip, right_hip)
        proper_alignment = body_alignment_angle < self.config.BODY_ALIGNMENT_THRESHOLD
        
        # Only count a rep if alignment is proper.
        if proper_alignment:
            # Down phase: elbow angle goes below BENT_ANGLE.
            if avg_elbow_angle < self.config.BENT_ANGLE and not self.pushup_flag:
                self.pushup_flag = True
            # Up phase: elbow angle goes above EXTENDED_ANGLE, after a down phase.
            elif avg_elbow_angle > self.config.EXTENDED_ANGLE and self.pushup_flag:
                self.pushup_count += 1
                self.pushup_flag = False
        else:
            # If alignment fails, do not count and reset flag.
            self.pushup_flag = False

        feedback = "Fix Alignment" if not proper_alignment else ("Down" if self.pushup_flag else "Up")
        return avg_elbow_angle, feedback

# -------------------- Utility Functions --------------------
def save_progress(user, pushup_count, filename="pushup_progress.json"):
    """Saves push-up progress to a JSON file with a timestamp."""
    data = {"user": user, "pushups": pushup_count, "timestamp": time.time()}
    try:
        with open(filename, "w") as f:
            json.dump(data, f)
        logging.info("Progress saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save progress: {e}")

def render_ui(frame, avg_elbow_angle, feedback, pushup_count, config: Config):
    """
    Renders an overlay with a vertical slider, rep counter, and feedback text.
    Returns the annotated frame.
    """
    height, width, _ = frame.shape
    overlay = frame.copy()

    # Vertical slider for elbow angle.
    slider_x = width - 50
    slider_top = 50
    slider_bottom = 380
    cv2.line(overlay, (slider_x, slider_top), (slider_x, slider_bottom), (0, 255, 0), 3)
    slider_knob_y = int(np.interp(avg_elbow_angle,
                                    [config.BENT_ANGLE, config.EXTENDED_ANGLE],
                                    [slider_bottom, slider_top]))
    cv2.circle(overlay, (slider_x, slider_knob_y), 12, (0, 255, 0), -1)
    cv2.putText(overlay, feedback, (slider_x - 70, slider_knob_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Progress percentage based on elbow angle.
    progress = np.interp(avg_elbow_angle,
                         (config.BENT_ANGLE, config.EXTENDED_ANGLE),
                         (0, 100))
    cv2.putText(overlay, f'{int(progress)}%', (slider_x - 30, slider_bottom + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Push-up counter box (bottom-left).
    cv2.rectangle(overlay, (20, height - 100), (150, height - 20), (0, 255, 0), cv2.FILLED)
    cv2.putText(overlay, str(pushup_count), (50, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

    # Feedback text (center top).
    cv2.rectangle(overlay, (width // 2 - 70, 10), (width // 2 + 70, 50), (255, 255, 255), cv2.FILLED)
    cv2.putText(overlay, feedback, (width // 2 - 50, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

# -------------------- Main Function --------------------
def run_pushups():
    config = Config()

    # Open the video file if specified; otherwise, use the webcam.
    if config.VIDEO_FILENAME:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.join(script_dir, config.VIDEO_FILENAME)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Could not open video file: {video_path}")
            return
    else:
        cap = cv2.VideoCapture(config.VIDEO_SOURCE)
        if not cap.isOpened():
            logging.error("Error opening webcam. Exiting.")
            return

    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    pushup_counter = PushupCounter(config)
    user = "User1"

    try:
        while True:
            success, frame = cap.read()
            if not success:
                logging.info("End of video or unable to read frame.")
                break

            # For recorded video, do not mirror (or uncomment if needed)
            # frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            keypoints = detect_pose(image_rgb)
            avg_elbow_angle, feedback = pushup_counter.process_keypoints(keypoints)
            if avg_elbow_angle is None:
                cv2.imshow('Push-Up Trainer', frame)
                if cv2.waitKey(30) & 0xFF == 27:
                    break
                continue

            frame_ui = render_ui(frame, avg_elbow_angle, feedback, pushup_counter.pushup_count, config)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame_ui, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Push-Up Trainer', frame_ui)
            if cv2.waitKey(30) & 0xFF == 27:
                break
    except Exception as e:
        logging.exception("An error occurred during push-up training: %s", e)
    finally:
        save_progress(user, pushup_counter.pushup_count)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_pushups()
