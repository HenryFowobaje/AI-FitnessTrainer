import os
import cv2
import mediapipe as mp
from squats import Config, SquatCounter, process_squat_frame

def run_test_video(video_path):
    config = Config()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file:", video_path)
        return

    # Initialize MediaPipe Pose
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    squat_counter = SquatCounter(config)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process each frame
        frame = process_squat_frame(frame, squat_counter, config, pose)
        cv2.imshow("Squat Trainer Test", frame)
        if cv2.waitKey(30) & 0xFF == 27:  # Exit on 'Esc' key
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Build an absolute path to the video file based on the script's location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "one.mp4")
    run_test_video(video_path)
