from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
import time
from models.pushups import Config, PushupCounter, process_pushup_frame
from resource_manager import ResourceManager
from utils import save_report  # ✅ NEW import

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
pushups_bp = Blueprint('pushups', __name__)

resource_manager = ResourceManager.get_instance()
pose = resource_manager.get_pose()
config = Config()
pushup_counter = PushupCounter(config)
streaming_active_pushups = True
session_start_time = None

@pushups_bp.route('/start-pushups', methods=['GET'])
def start_pushups():
    global streaming_active_pushups, pushup_counter, session_start_time
    streaming_active_pushups = True
    session_start_time = time.time()
    cam = resource_manager.init_camera(source=config.VIDEO_SOURCE)
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    pushup_counter = PushupCounter(config)
    return jsonify({"message": "✅ Pushup trainer started successfully!"})

@pushups_bp.route('/video_feed/pushups', methods=['GET'])
def video_feed_pushups():
    if not resource_manager.init_camera().isOpened():
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames_pushups(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames_pushups():
    global streaming_active_pushups
    cam = resource_manager.init_camera()
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

@pushups_bp.route('/end-pushups', methods=['GET'])
def end_pushups():
    global streaming_active_pushups
    streaming_active_pushups = False
    resource_manager.release_camera()
    return jsonify({"message": "Pushup workout ended.", "pushups": pushup_counter.count})

@pushups_bp.route('/generate-pushups-report', methods=['GET'])
def generate_pushups_report():
    global session_start_time
    end_time = time.time()
    duration = round(end_time - session_start_time, 2) if session_start_time else 0
    reps = pushup_counter.count

    report = save_report("pushups", reps, duration, mode="default")
    pushup_counter.count = 0  # Reset counter manually

    return jsonify({
        "message": "📄 Pushup report generated!",
        "reps": reps,
        "duration": duration,
        "calories": report["calories"]
    })