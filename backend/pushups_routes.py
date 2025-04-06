from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.pushups import Config, PushupCounter, process_pushup_frame
from resource_manager import ResourceManager  # Centralized resource manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
pushups_bp = Blueprint('pushups', __name__)

# Get the shared resource manager instance.
resource_manager = ResourceManager.get_instance()

def init_camera():
    config = Config()
    # If a video file is specified, use it; otherwise, use the webcam.
    if config.VIDEO_FILENAME:
        import os
        script_dir = os.path.dirname(__file__)
        video_path = os.path.join(script_dir, config.VIDEO_FILENAME)
        return cv2.VideoCapture(video_path)
    else:
        return resource_manager.init_camera(source=config.VIDEO_SOURCE)

# Shared Pose instance
pose = resource_manager.get_pose()
config = Config()
pushup_counter = PushupCounter(config)

# Global flag to control streaming for pushups
streaming_active_pushups = True

@pushups_bp.route('/start-pushups', methods=['GET'])
def start_pushups():
    global streaming_active_pushups, pushup_counter
    streaming_active_pushups = True  # Enable streaming
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    pushup_counter = PushupCounter(config)  # Reinitialize counter if needed
    return jsonify({"message": "✅ Pushup trainer started successfully!"})

@pushups_bp.route('/video_feed/pushups', methods=['GET'])
def video_feed_pushups():
    if not init_camera().isOpened():
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames_pushups(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames_pushups():
    global streaming_active_pushups
    cam = init_camera()
    while streaming_active_pushups:
        ret, frame = cam.read()
        if not ret:
            break
        annotated_frame = process_pushup_frame(frame, pushup_counter, pose, config)
        ret2, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    # When streaming_active_pushups becomes False, the loop exits.
    return

@pushups_bp.route('/end-pushups', methods=['GET'])
def end_pushups():
    global streaming_active_pushups
    streaming_active_pushups = False  # Signal the generator to stop
    resource_manager.release_camera()  # Release the shared camera resource
    return jsonify({"message": "Pushup workout ended."})
