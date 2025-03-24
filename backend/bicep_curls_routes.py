from flask import Blueprint, Response, jsonify
import cv2
import mediapipe as mp
import logging
from models.bicep_curl import process_bicep_frame, save_progress, Smoother, SMOOTHING_WINDOW, GESTURE_FRAME_THRESHOLD, MODE_PIXEL_THRESHOLD
# The necessary functions (detect_pose, calc_angle, compute_shoulder_tilt) are imported within the model file via relative imports.

bicep_bp = Blueprint('bicep_curls', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Initialize MediaPipe Pose (we pass it in state)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Lazy camera initialization for bicep curls
camera = None
workout_started = False
state = None  # processing state for bicep curls

def init_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

@bicep_bp.route('/start-bicep-curls', methods=['GET'])
def start_bicep_curls():
    global workout_started, state
    cam = init_camera()
    if not cam.isOpened():
        return jsonify({"message": "Error: Unable to access camera."}), 500
    # Initialize state dictionary with all required parameters
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
        'pose': pose  # store the MediaPipe Pose instance in state
    }
    workout_started = True
    return jsonify({"message": "✅ Bicep curl trainer started successfully!"})

@bicep_bp.route('/video_feed/bicep_curls', methods=['GET'])
def video_feed_bicep_curls():
    if not workout_started:
        return jsonify({"message": "Camera not started. Start workout first."}), 403
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate_frames():
    global camera, state, pose
    cam = init_camera()
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        annotated_frame, state = process_bicep_frame(frame, state)
        ret2, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret2:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@bicep_bp.route('/end-bicep-curls', methods=['GET'])
def end_bicep_curls():
    global workout_started, camera
    if camera is not None:
        camera.release()  # Release the camera
        camera = None
    workout_started = False 
    return jsonify({"message": "Bicep curl workout ended."})