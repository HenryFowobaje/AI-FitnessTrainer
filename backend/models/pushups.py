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
    # Elbow angles for a proper push-up
    BENT_ANGLE = 100         # Elbow angle at the bottom (down phase)
    EXTENDED_ANGLE = 170    # Elbow angle at the top (up phase)
    SMOOTHING_WINDOW = 5    # Frames for angle smoothing
    # Body alignment: the torso (average shoulder to hip line) should be nearly horizontal.
    BODY_ALIGNMENT_THRESHOLD = 10  
    TARGET_REPS = 20        # Target push-up count (for progress tracking)
    VIDEO_FILENAME = None   # Set to None to use webcam.
    VIDEO_SOURCE = 0        # Use webcam if VIDEO_FILENAME is None.

# Initialize MediaPipe for drawing landmarks
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class PushupCounter:
    def __init__(self, config: Config):
        self.config = config
        self.count = 0
        self.direction = "upwards"  # Can be "upwards" or "downwards"
        self.angle_smoother = Smoother(window_size=config.SMOOTHING_WINDOW)
        self.progress = 0  # Percent of the current push-up completion

    def process_keypoints(self, keypoints):
        """
        Processes keypoints and updates the push-up count.
        Returns (avg_elbow_angle, feedback). If insufficient keypoints, returns (None, error message).
        """
        if len(keypoints) < 17:
            return None, "Insufficient keypoints detected"

        # Extract relevant keypoints
        left_shoulder  = keypoints[5]
        right_shoulder = keypoints[6]
        left_elbow     = keypoints[7]
        right_elbow    = keypoints[8]
        left_wrist     = keypoints[9]
        right_wrist    = keypoints[10]
        left_hip       = keypoints[11]
        right_hip      = keypoints[12]

        # Calculate elbow angles
        left_elbow_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calc_angle(right_shoulder, right_elbow, right_wrist)
        raw_avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

        # Calculate body alignment
        body_alignment_angle = compute_body_alignment_angle(left_shoulder, right_shoulder, left_hip, right_hip)
        proper_alignment = True

        # Interpolate percentage (e.g. 0% at bent, 100% at extended)
        self.progress = np.interp(raw_avg_elbow_angle,
                                  (self.config.BENT_ANGLE, self.config.EXTENDED_ANGLE),
                                  (0, 100))

        # Count push-ups based on full rep completion (down then up)
        if proper_alignment:
            if self.progress < 5 and self.direction == "upwards":
                self.direction = "downwards"
            elif self.progress > 95 and self.direction == "downwards":
                self.count += 1
                self.direction = "upwards"
        else:
            self.direction = "upwards"  # Reset if misaligned

        # Smooth for UI
        avg_elbow_angle = self.angle_smoother.update(raw_avg_elbow_angle)

        feedback = "Fix Alignment" if not proper_alignment else ("Down" if self.direction == "downwards" else "Up")
        return avg_elbow_angle, feedback

def compute_body_alignment_angle(left_shoulder, right_shoulder, left_hip, right_hip):
    """
    Computes the deviation (in degrees) between the shoulder-hip line and the horizontal.
    """
    avg_shoulder = np.array([(left_shoulder[0] + right_shoulder[0]) / 2,
                             (left_shoulder[1] + right_shoulder[1]) / 2])
    avg_hip = np.array([(left_hip[0] + right_hip[0]) / 2,
                        (left_hip[1] + right_hip[1]) / 2])
    vec = avg_hip - avg_shoulder
    horizontal = np.array([1, 0], dtype=np.float32)
    mag = np.linalg.norm(vec)
    if mag == 0:
        return 0.0
    dot = np.dot(vec, horizontal)
    cos_theta = np.clip(dot / mag, -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_theta))
    return angle

def render_ui(frame, avg_elbow_angle, feedback, pushup_count, config: Config):
    """
    Draws an overlay with a vertical slider, rep counter, and feedback text.
    Returns the annotated frame.
    """
    height, width, _ = frame.shape
    overlay = frame.copy()
    # Vertical slider
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
    progress = np.interp(avg_elbow_angle,
                         (config.BENT_ANGLE, config.EXTENDED_ANGLE),
                         (0, 100))
    cv2.putText(overlay, f'{int(progress)}%', (slider_x - 30, slider_bottom + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.rectangle(overlay, (20, height - 100), (150, height - 20), (0, 255, 0), cv2.FILLED)
    cv2.putText(overlay, str(pushup_count), (50, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
    cv2.rectangle(overlay, (width // 2 - 70, 10), (width // 2 + 70, 50), (255, 255, 255), cv2.FILLED)
    cv2.putText(overlay, feedback, (width // 2 - 50, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

def process_pushup_frame(frame, pushup_counter, pose, config):
    """
    Processes a single frame for push-ups:
      - Converts the frame to RGB.
      - Uses MediaPipe to process the frame (for drawing landmarks).
      - Uses detect_pose to get keypoints.
      - Updates the pushup counter and gets the average elbow angle and feedback.
      - Renders an overlay onto the frame.
    Returns the annotated frame.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # ✅ Person presence check (using landmark[0] visibility)
    if not results.pose_landmarks or results.pose_landmarks.landmark[0].visibility < 0.5:
        return frame  # Person not confidently detected

    keypoints = detect_pose(rgb_frame)
    avg_elbow_angle, feedback = pushup_counter.process_keypoints(keypoints)
    if avg_elbow_angle is None:
        return frame  # Return unmodified if detection fails.

    frame_ui = render_ui(frame, avg_elbow_angle, feedback, pushup_counter.count, config)
    mp_drawing.draw_landmarks(frame_ui, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return frame_ui
