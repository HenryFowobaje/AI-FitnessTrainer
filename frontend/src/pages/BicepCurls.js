import React, { useState } from 'react';
import axios from 'axios';
import './BicepCurls.css';

function BicepCurls() {
  const [message, setMessage] = useState('');
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [repCount, setRepCount] = useState(null);

  const startBicepCurls = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/start-bicep-curls');
      setMessage(res.data.message);
      setWorkoutStarted(true);
    } catch (error) {
      setMessage('❌ Failed to start bicep curl trainer.');
    }
  };

  // Optional: If you have an end-bicep-curls route
  const endBicepCurls = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/end-bicep-curls');
      setMessage(res.data.message);
      setWorkoutStarted(false);
      if (res.data.reps !== undefined) {
        setRepCount(res.data.reps);
      }
    } catch (error) {
      setMessage('❌ Failed to end bicep curl workout.');
    }
  };

  return (
    <div className="bicep-curls-page">
      {/* Hero / Header Section */}
      <header className="bicep-hero">
        <div className="hero-content">
          <h1>Bicep Curls Trainer</h1>
          <p>
            Perfect your bicep curl form with real-time AI feedback. Position yourself in front
            of the camera and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startBicepCurls}>
              Start Bicep Curl Trainer
            </button>
          ) : (
            <button className="hero-button end-button" onClick={endBicepCurls}>
              End Workout
            </button>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

      {/* Main Content Section */}
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

        {!workoutStarted && repCount !== null && (
          <div className="summary-section">
            <h3>Workout Summary</h3>
            <p>You completed {repCount} bicep curls!</p>
          </div>
        )}
      </main>

      {/* Footer (matching the dark style) */}
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
