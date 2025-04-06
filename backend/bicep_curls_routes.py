from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.bicep_curl import process_bicep_frame, save_progress, Smoother, SMOOTHING_WINDOW, GESTURE_FRAME_THRESHOLD, MODE_PIXEL_THRESHOLD
from resource_manager import ResourceManager  # Centralized resource manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
bicep_bp = Blueprint('bicep_curls', __name__)

# Get the shared resource manager instance.
resource_manager = ResourceManager.get_instance()

def init_camera():
    return resource_manager.init_camera(source=0)

# Global configuration and state for bicep curls.
# (Adjust state initialization as per your existing implementation.)
from models.bicep_curl import SMOOTHING_WINDOW, GESTURE_FRAME_THRESHOLD, MODE_PIXEL_THRESHOLD
state = {
    'session_state': "waiting",
    'calibration_data': [],
    'calibration_target_frames': 30,
    'baseline_shoulder_tilt': None,
    'session_start_time': None,
    'left_count': 0,
    'right_count': 0,
    'left_flag': False,
    'right_flag': False,
    'left_smoother': Smoother(window_size=SMOOTHING_WINDOW),
    'right_smoother': Smoother(window_size=SMOOTHING_WINDOW),
    'left_angle': 0,
    'right_angle': 0,
    'posture_alert': False,
    'mode': "both",
    'left_mode_counter': 0,
    'right_mode_counter': 0,
    'both_mode_counter': 0,
    'gesture_frame_threshold': GESTURE_FRAME_THRESHOLD,
    'mode_pixel_threshold': MODE_PIXEL_THRESHOLD,
    'reset_gesture_counter': 0
}

# Shared Pose instance
pose = resource_manager.get_pose()

# Global flag to control streaming for bicep curls.
streaming_active_bicep = True

@bicep_bp.route('/start-bicep-curls', methods=['GET'])
def start_bicep_curls():
    global streaming_active_bicep, state
    streaming_active_bicep = True  # Enable streaming
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    # Reinitialize state if needed.
    state = {
        'session_state': "waiting",
        'calibration_data': [],
        'calibration_target_frames': 30,
        'baseline_shoulder_tilt': None,
        'session_start_time': None,
        'left_count': 0,
        'right_count': 0,
        'left_flag': False,
        'right_flag': False,
        'left_smoother': Smoother(window_size=SMOOTHING_WINDOW),
        'right_smoother': Smoother(window_size=SMOOTHING_WINDOW),
        'left_angle': 0,
        'right_angle': 0,
        'posture_alert': False,
        'mode': "both",
        'left_mode_counter': 0,
        'right_mode_counter': 0,
        'both_mode_counter': 0,
        'gesture_frame_threshold': GESTURE_FRAME_THRESHOLD,
        'mode_pixel_threshold': MODE_PIXEL_THRESHOLD,
        'reset_gesture_counter': 0,
        'pose': pose
    }
    return jsonify({"message": "✅ Bicep curl trainer started successfully!"})

@bicep_bp.route('/video_feed/bicep_curls', methods=['GET'])
def video_feed_bicep_curls():
    if not init_camera().isOpened():
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames_bicep(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames_bicep():
    global streaming_active_bicep, state
    cam = init_camera()
    while streaming_active_bicep:
        ret, frame = cam.read()
        if not ret:
            break
        frame, state = process_bicep_frame(frame, state)
        ret2, buffer = cv2.imencode('.jpg', frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return

@bicep_bp.route('/end-bicep-curls', methods=['GET'])
def end_bicep_curls():
    global streaming_active_bicep
    streaming_active_bicep = False  # Signal generator to stop streaming
    resource_manager.release_camera()  # Release shared camera
    return jsonify({"message": "Bicep curl workout ended."})
