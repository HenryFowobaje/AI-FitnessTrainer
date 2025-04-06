# pose_estimation.py
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from collections import deque

# Load MoveNet model (Thunder version for better accuracy)
movenet = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/3")

def detect_pose(image):
    """
    Given an image (RGB), returns the detected keypoints from MoveNet.
    Each keypoint is returned as a tuple: (x, y, score).
    """
    input_image = tf.image.resize_with_pad(tf.expand_dims(image, axis=0), 256, 256)
    input_tensor = tf.cast(input_image, dtype=tf.int32)
    outputs = movenet.signatures["serving_default"](input_tensor)
    keypoints = outputs["output_0"].numpy()[0, 0]

    # Convert from (y, x, score) to (x, y, score) in pixel coordinates
    height, width = image.shape[:2]
    keypoints = [(kp[1] * width, kp[0] * height, kp[2]) for kp in keypoints]
    return keypoints

def calc_angle(a, b, c):
    """
    Calculates the angle (in degrees) at point b given three points (a, b, c).
    """
    a_arr, b_arr, c_arr = np.array(a), np.array(b), np.array(c)
    ba = a_arr - b_arr
    bc = c_arr - b_arr
    if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
        return 0.0
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    return round(np.degrees(np.arccos(cosine_angle)), 2)

def compute_shoulder_tilt(left_shoulder, right_shoulder):
    """
    Computes the tilt angle of the line between the left and right shoulder
    relative to the horizontal.
    """
    dx = right_shoulder[0] - left_shoulder[0]
    dy = right_shoulder[1] - left_shoulder[1]
    return np.degrees(np.arctan2(dy, dx))

class Smoother:
    """
    Helper class to smooth a stream of values using a fixed-size window.
    """
    def __init__(self, window_size=5):
        self.window = deque(maxlen=window_size)
    
    def update(self, value):
        self.window.append(value)
        return np.mean(self.window)
