import os
import sys
import cv2
import mediapipe as mp
import time

# Add parent directory of `models/` (i.e., `backend/`) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from squats import Config, SquatCounter, process_squat_frame
from utils import save_report  # ✅ Now works because backend/ is in path

def run_test_video(video_path):
    config = Config()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file:", video_path)
        return

    pose = mp.solutions.pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    squat_counter = SquatCounter(config)

    print("📹 Starting test video...")
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = process_squat_frame(frame, squat_counter, config, pose)
        cv2.imshow("Squat Trainer Test", frame)
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    reps = squat_counter.squat_count

    # Save report
    report = save_report("squats", reps, duration)
    print("\n🎯 Workout Summary:")
    print(f"✅ Reps completed: {report['reps']}")
    print(f"⏱️ Duration: {report['duration_sec']} seconds")
    print(f"🔥 Estimated Calories Burned: {report['calories']} kcal")
    print(f"📁 Report saved to: reports.json")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "squats.mp4")
    run_test_video(video_path)
