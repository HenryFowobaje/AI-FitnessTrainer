# squats_routes.py

from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.squats import Config, SquatCounter, process_squat_frame, save_progress
from resource_manager import ResourceManager  # Import the resource manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

squats_bp = Blueprint('squats', __name__)

# Get the shared resource manager instance.
resource_manager = ResourceManager.get_instance()

def init_camera():
    return resource_manager.init_camera(source=0)

# Global instances for configuration and squat counter remain.
config = Config()
squat_counter = SquatCounter(config)
# Instead of creating a new Pose instance, get it from the resource manager.
pose = resource_manager.get_pose()

# Global flag to control streaming
streaming_active = True

@squats_bp.route('/start-squats', methods=['GET'])
def start_squats():
    global streaming_active
    streaming_active = True  # Enable streaming when starting
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    return jsonify({"message": "✅ Squat trainer started successfully!"})

@squats_bp.route('/video_feed/squats', methods=['GET'])
def video_feed_squats():
    if not init_camera().isOpened():
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames():
    global streaming_active
    cam = init_camera()
    while streaming_active:
        ret, frame = cam.read()
        if not ret:
            break
        processed_frame = process_squat_frame(frame, squat_counter, config, pose)
        ret2, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    # Once streaming is no longer active, stop the generator
    return

@squats_bp.route('/end-squats', methods=['GET'])
def end_squats():
    global streaming_active, squat_counter
    streaming_active = False  # Signal the generator loop to stop
    resource_manager.release_camera()  # Release via the resource manager
    squat_counter.reset()  # Fully reset the squat counter's internal state
    return jsonify({"message": "Squat workout ended."})
