from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.pushups import Config, PushupCounter, process_pushup_frame
# Import shared pose_estimation functions if needed (they are already used in process_pushup_frame)
# from models.pose_estimation import detect_pose, calc_angle, compute_shoulder_tilt

pushups_bp = Blueprint('pushups', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Initialize MediaPipe Pose for drawing
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Lazy camera initialization for pushups
camera = None
workout_started = False
pushup_counter = None  # will be initialized in start route
config = Config()

def init_camera():
    global camera
    if camera is None:
        # Use video file if specified, otherwise use webcam.
        if config.VIDEO_FILENAME:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            video_path = os.path.join(script_dir, config.VIDEO_FILENAME)
            camera = cv2.VideoCapture(video_path)
        else:
            camera = cv2.VideoCapture(config.VIDEO_SOURCE)
    return camera

@pushups_bp.route('/start-pushups', methods=['GET'])
def start_pushups():
    global workout_started, pushup_counter
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    pushup_counter = PushupCounter(config)
    workout_started = True
    return jsonify({"message": "✅ Pushup trainer started successfully!"})

@pushups_bp.route('/video_feed/pushups', methods=['GET'])
def video_feed_pushups():
    if not workout_started:
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames():
    global camera, pushup_counter, pose
    cam = init_camera()
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        annotated_frame = process_pushup_frame(frame, pushup_counter, pose, config)
        ret2, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@pushups_bp.route('/end-pushups', methods=['GET'])
def end_pushups():
    global workout_started, camera
    if camera is not None:
        camera.release()  # Release the camera
        camera = None
    workout_started = False
    return jsonify({"message": "Pushup workout ended."})

