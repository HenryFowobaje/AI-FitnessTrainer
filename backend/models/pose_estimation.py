import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils  # Helps draw landmarks and connections
pose = mp_pose.Pose()

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the image to RGB (for MediaPipe)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # Convert back to BGR for OpenCV display
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw landmarks if a person is detected
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # **NEW: Label key points with index numbers**
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            h, w, _ = frame.shape
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.putText(image, str(idx), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Show the processed frame
    cv2.imshow("Pose Estimation", image)

    # Press 'q' to exit
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
