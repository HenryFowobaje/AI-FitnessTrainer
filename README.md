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
- Pip install requirements.txt

1. Clone the Repository
```
git clone https://github.com/yourusername/FitPal-AI-Trainer.git
cd FitPal-AI-Trainer
```

2. Set Up the Backend
```
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

```

➕ Run the Backend Server
```
python app.py
```
It will start the server on http://127.0.0.1:5000

3. Set Up the Frontend
```
cd ../frontend
npm install
npm start
```
It will launch React on http://localhost:3000 and connect to the backend API.

## 🧪 How to Use
- Visit the homepage and choose an exercise (Squats, Pushups, or Bicep Curls).

- Click Start Trainer – your webcam will be activated.

- Perform the reps. You’ll see visual feedback (rep count, posture alert, etc.).

- Click End Workout when done.

- ptionally, click Generate Report to view session summary (reps, time, estimated calories).

- Visit the About page for instructions or Reports tab to view logs (in progress).

## 🧠 Acknowledgments

FitPal was developed as part of a senior seminar capstone project by a team of passionate student developers. We thank all mentors, faculty, and peers who supported us through design, debugging, and testing.

## 📌 Future Features

- Workout history dashboard
- Authentication + cloud sync
- Mobile support (PWA or React Native)
- Voice guidance and audio alerts

