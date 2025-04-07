import os
import cv2
import time
import mediapipe as mp
from models.pushups import Config, PushupCounter, process_pushup_frame
from utils import save_report  # ✅ to store the report locally

def run_test_video(video_path):
    config = Config()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file:", video_path)
        return

    pose = mp.solutions.pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    pushup_counter = PushupCounter(config)

    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process and display the annotated frame
        frame = process_pushup_frame(frame, pushup_counter, pose, config)
        cv2.imshow("Pushup Trainer Test", frame)

        # Press Esc to exit
        if cv2.waitKey(30) & 0xFF == 27:
            break

    duration = round(time.time() - start_time, 2)
    reps = pushup_counter.count
    report = save_report("pushups", reps, duration)

    print("\n✅ Workout Summary")
    print(f"Reps Completed: {report['reps']}")
    print(f"Duration: {report['duration_sec']} sec")
    print(f"Estimated Calories Burned: {report['calories']} kcal")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "pushon.mp4")
    run_test_video(video_path)
