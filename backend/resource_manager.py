# resource_manager.py

import cv2
import threading
import mediapipe as mp

class ResourceManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.camera = None
        self.pose = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def init_camera(self, source=0):
        # If the camera is not initialized or not opened, create a new one.
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(source)
        return self.camera

    def release_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def get_pose(self):
        # Initialize the MediaPipe Pose instance if it doesn't exist.
        if self.pose is None:
            mp_pose = mp.solutions.pose
            self.pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        return self.pose

    def reset_pose(self):
        if self.pose is not None:
            self.pose.close()  # Release underlying resources.
            self.pose = None
