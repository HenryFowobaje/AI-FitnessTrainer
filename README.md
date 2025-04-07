# 🏋️‍♂️ FitPal – Your AI-Powered Fitness Trainer

FitPal is a real-time fitness trainer powered by AI. It helps users perform common bodyweight exercises (squats, pushups, bicep curls) with correct form using pose estimation, geometric analysis, and real-time feedback—all through your browser without requiring extra hardware.

This project is built with React (frontend) and Flask (backend) and uses TensorFlow MoveNet and OpenCV under the hood.

## 📸 Features

- Real-time form correction with webcam
- Accurate rep counting using angle-based analysis
- Live feedback overlay and posture alerts
- Optional session report generation (reps, time, calories burned)
- Clean, responsive UI built with React

## 📁 Project Structure

```
AI-FitnessTrainer/
├── backend/
│   ├── app.py
│   ├── squats_routes.py
│   ├── pushups_routes.py
│   ├── bicep_curls_routes.py
│   ├── models/
│   ├── utils.py
│   └── resource_manager.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Squats.js
│   │   │   ├── Pushups.js
│   │   │   ├── BicepCurls.js
│   │   │   ├── Report.js
│   │   │   ├── About.js
│   │   ├── components/
│   │   │   ├── Navbar.js
│   │   ├── App.js
│   └── ...
```

## 🔧 Technologies Used

### Frontend

- React.js
- Axios
- CSS Modules

### Backend

- Flask + Flask-CORS
- OpenCV
- TensorFlow MoveNet
- MediaPipe
- JSON storage for reports

## 🚀 How to Run the Project Locally

### ⚙️ Prerequisites

- Python 3.8+
- Node.js & npm
- OpenCV installed (for Python)
- Git

1. Clone the Repository

## 🧠 Acknowledgments

FitPal was developed as part of a senior seminar capstone project by a team of passionate student developers. We thank all mentors, faculty, and peers who supported us through design, debugging, and testing.

## 📌 Future Features

- Workout history dashboard
- Authentication + cloud sync
- Mobile support (PWA or React Native)
- Voice guidance and audio alerts

