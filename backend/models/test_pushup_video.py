import os
import cv2
import mediapipe as mp
from pushups import Config, PushupCounter, process_pushup_frame

def run_test_video(video_path):
    # Create configuration instance.
    config = Config()
    
    # Open the video file.
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file:", video_path)
        return

    # Initialize MediaPipe Pose with desired confidence thresholds.
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    
    # Initialize push-up counter.
    pushup_counter = PushupCounter(config)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process each frame: detect pose, update push-up count, and render UI.
        frame = process_pushup_frame(frame, pushup_counter, pose, config)
        cv2.imshow("Pushup Trainer Test", frame)
        
        # Exit on 'Esc' key.
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Construct the absolute path to the video file relative to this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "pushon.mp4")
    run_test_video(video_path)
