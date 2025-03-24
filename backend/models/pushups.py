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
    BENT_ANGLE = 90         # Elbow angle at the bottom (down phase)
    EXTENDED_ANGLE = 170    # Elbow angle at the top (up phase)
    SMOOTHING_WINDOW = 5    # Frames for angle smoothing
    # Body alignment: the torso (average shoulder to hip line) should be nearly horizontal.
    BODY_ALIGNMENT_THRESHOLD = 20  
    TARGET_REPS = 20        # Target push-up count (for progress tracking)
    VIDEO_FILENAME = None   # Set to None to use webcam.
    VIDEO_SOURCE = 0        # Use webcam if VIDEO_FILENAME is None.

# Initialize MediaPipe for drawing landmarks
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class PushupCounter:
    def __init__(self, config: Config):
        self.config = config
        self.pushup_count = 0
        self.pushup_flag = False  # True when user is in the "down" phase
        self.angle_smoother = Smoother(window_size=config.SMOOTHING_WINDOW)

    def process_keypoints(self, keypoints):
        """
        Processes keypoints and updates the push-up count.
        Returns (avg_elbow_angle, feedback). If insufficient keypoints, returns (None, error message).
        """
        if len(keypoints) < 17:
            return None, "Insufficient keypoints detected"
        
        # Extract key landmarks using MoveNet ordering.
        left_shoulder  = keypoints[5]
        right_shoulder = keypoints[6]
        left_elbow     = keypoints[7]
        right_elbow    = keypoints[8]
        left_wrist     = keypoints[9]
        right_wrist    = keypoints[10]
        left_hip       = keypoints[11]
        right_hip      = keypoints[12]
        
        # Calculate the elbow angles (shoulder->elbow->wrist).
        left_elbow_angle = calc_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calc_angle(right_shoulder, right_elbow, right_wrist)
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        avg_elbow_angle = self.angle_smoother.update(avg_elbow_angle)
        
        # Compute body alignment angle.
        body_alignment_angle = compute_body_alignment_angle(left_shoulder, right_shoulder, left_hip, right_hip)
        proper_alignment = body_alignment_angle < self.config.BODY_ALIGNMENT_THRESHOLD
        
        # Only count a rep if alignment is proper.
        if proper_alignment:
            if avg_elbow_angle < self.config.BENT_ANGLE and not self.pushup_flag:
                self.pushup_flag = True
            elif avg_elbow_angle > self.config.EXTENDED_ANGLE and self.pushup_flag:
                self.pushup_count += 1
                self.pushup_flag = False
        else:
            self.pushup_flag = False
        
        feedback = "Fix Alignment" if not proper_alignment else ("Down" if self.pushup_flag else "Up")
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
    # (Optional: Flip the frame if needed)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    keypoints = detect_pose(rgb_frame)
    avg_elbow_angle, feedback = pushup_counter.process_keypoints(keypoints)
    if avg_elbow_angle is None:
        return frame  # Return unmodified if detection fails.
    frame_ui = render_ui(frame, avg_elbow_angle, feedback, pushup_counter.pushup_count, config)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_ui, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return frame_ui
