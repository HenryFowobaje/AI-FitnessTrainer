from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.squats import Config, SquatCounter, process_squat_frame, save_progress

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Define a blueprint for squats
squats_bp = Blueprint('squats', __name__)

# Lazy camera initialization: no camera is opened until needed.
camera = None
workout_started = False

def init_camera():
    global camera
    if camera is None:
        config = Config()
        camera = cv2.VideoCapture(config.VIDEO_SOURCE)
    return camera

# Global instances: configuration, squat counter, and MediaPipe Pose
config = Config()
squat_counter = SquatCounter(config)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

@squats_bp.route('/start-squats', methods=['GET'])
def start_squats():
    global workout_started
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    workout_started = True
    return jsonify({"message": "✅ Squat trainer started successfully!"})

@squats_bp.route('/video_feed/squats', methods=['GET'])
def video_feed_squats():
    if not workout_started:
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames():
    global camera, squat_counter, pose, config
    cam = init_camera()
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        # Process the frame using our helper from the model
        processed_frame = process_squat_frame(frame, squat_counter, config, pose)
        ret2, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@squats_bp.route('/end-squats', methods=['GET'])
def end_squats():
    global workout_started, camera
    if camera is not None:
        camera.release()  # Release the camera
        camera = None
    workout_started = False
    return jsonify({"message": "Squat workout ended."})