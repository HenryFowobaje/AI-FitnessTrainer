import React, { useState } from 'react';
import axios from 'axios';
import './BicepCurls.css';

function BicepCurls() {
  const [message, setMessage] = useState('');
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [repData, setRepData] = useState(null);

  const startBicepCurls = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/start-bicep-curls');
      setMessage(res.data.message);
      setWorkoutStarted(true);
      setRepData(null);
    } catch (error) {
      setMessage('❌ Failed to start bicep curl trainer.');
    }
  };

  const endBicepCurls = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/end-bicep-curls');
      setMessage(res.data.message);
      setWorkoutStarted(false);
    } catch (error) {
      setMessage('❌ Failed to end bicep curl workout.');
    }
  };

  const generateReport = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/generate-bicep-curls-report');
      setRepData(res.data);
      setMessage(res.data.message);
    } catch (error) {
      setMessage('❌ Failed to generate report.');
    }
  };

  return (
    <div className="bicep-curls-page">
      <header className="bicep-hero">
        <div className="hero-content">
          <h1 style={{ color: "#000" }}>Bicep Curls Trainer</h1>
          <p>
            Perfect your bicep curl form with real-time AI feedback. Position yourself in front
            of the camera and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startBicepCurls}>
              Start Bicep Curl Trainer
            </button>
          ) : (
            <>
              <button className="hero-button end-button" onClick={endBicepCurls}>
                End Workout
              </button>
              <button className="hero-button end-button" style={{ marginLeft: '10px' }} onClick={generateReport}>
                Generate Report
              </button>
            </>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

      <main className="bicep-main">
        {workoutStarted ? (
          <div className="live-feed-section">
            <h3>Live Camera Feed:</h3>
            <img
              src="http://127.0.0.1:5000/video_feed/bicep_curls"
              alt="Live Feed"
              width="640"
              height="480"
            />
          </div>
        ) : (
          <p className="waiting-message">
            Video feed will appear once the workout starts.
          </p>
        )}

        {!workoutStarted && repData && (
          <div className="summary-section">
            <h3>Workout Summary</h3>
            <p>✅ You completed <strong>{repData.reps}</strong> bicep curls!</p>
            <p>⏱️ Duration: {repData.duration} seconds</p>
            <p>🔥 Estimated Calories Burned: {repData.calories} kcal</p>
          </div>
        )}
      </main>

      <footer className="bicep-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <h3>FitPal</h3>
            <p>Your AI-powered fitness trainer for perfect form and personalized workouts.</p>
          </div>
          <div className="footer-links">
            <div>
              <h4>Exercises</h4>
              <ul>
                <li>Pushups</li>
                <li>Squats</li>
                <li>Bicep Curls</li>
              </ul>
            </div>
            <div>
              <h4>Resources</h4>
              <ul>
                <li>About Us</li>
                <li>Fitness Reports</li>
                <li>Blog</li>
                <li>FAQ</li>
              </ul>
            </div>
            <div>
              <h4>Legal</h4>
              <ul>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
                <li>Cookie Policy</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 FitPal. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default BicepCurls;
