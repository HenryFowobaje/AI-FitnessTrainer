import React, { useState } from 'react';
import axios from 'axios';
import './Squats.css';

function Squats() {
  const [message, setMessage] = useState('');
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [repCount, setRepCount] = useState(null);

  const startSquats = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/start-squats');
      setMessage(res.data.message);
      setWorkoutStarted(true);
    } catch (error) {
      setMessage('❌ Failed to start squat trainer.');
    }
  };

  // Optional: If you have an end-squats route
  const endSquats = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/end-squats');
      setMessage(res.data.message);
      setWorkoutStarted(false);
      if (res.data.reps !== undefined) {
        setRepCount(res.data.reps);
      }
    } catch (error) {
      setMessage('❌ Failed to end squat workout.');
    }
  };

  return (
    <div className="squats-page">
      {/* Hero / Header Section */}
      <header className="squats-hero">
        <div className="hero-content">
          <h1>Squats Trainer</h1>
          <p>
            Perfect your squat form with real-time AI feedback. Position yourself in front of the camera
            and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startSquats}>
              Start Squat Trainer
            </button>
          ) : (
            <button className="hero-button end-button" onClick={endSquats}>
              End Workout
            </button>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

      {/* Main Content Section */}
      <main className="squats-main">
        {workoutStarted ? (
          <div className="live-feed-section">
            <h3>Live Camera Feed:</h3>
            <img
              src="http://127.0.0.1:5000/video_feed/squats"
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
            <p>You completed {repCount} squats!</p>
          </div>
        )}
      </main>

      {/* Footer (matching the dark style) */}
      <footer className="squats-footer">
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

export default Squats;
