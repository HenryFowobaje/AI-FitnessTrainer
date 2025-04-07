from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
import time
from models.squats import Config, SquatCounter, process_squat_frame, save_progress
from resource_manager import ResourceManager
from utils import save_report  # ⬅️ Import the new save_report utility

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

squats_bp = Blueprint('squats', __name__)
resource_manager = ResourceManager.get_instance()

config = Config()
squat_counter = SquatCounter(config)
pose = resource_manager.get_pose()

streaming_active = True
session_start_time = None

@squats_bp.route('/start-squats', methods=['GET'])
def start_squats():
    global streaming_active, session_start_time
    streaming_active = True
    session_start_time = time.time()
    cam = resource_manager.init_camera(source=0)
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    return jsonify({"message": "✅ Squat trainer started successfully!"})

@squats_bp.route('/video_feed/squats', methods=['GET'])
def video_feed_squats():
    if not resource_manager.init_camera().isOpened():
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames():
    global streaming_active
    cam = resource_manager.init_camera()
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

@squats_bp.route('/end-squats', methods=['GET'])
def end_squats():
    global streaming_active
    streaming_active = False
    resource_manager.release_camera()
    return jsonify({"message": "🏁 Squat workout ended.", "reps": squat_counter.squat_count})

@squats_bp.route('/generate-squats-report', methods=['GET'])
def generate_report():
    global session_start_time
    end_time = time.time()
    duration = round(end_time - session_start_time, 2) if session_start_time else 0
    reps = squat_counter.squat_count

    report = save_report("squats", reps, duration, mode="default")
    squat_counter.reset()

    return jsonify({
        "message": "📄 Report generated successfully!",
        "reps": reps,
        "duration": duration,
        "calories": report["calories"]
    })