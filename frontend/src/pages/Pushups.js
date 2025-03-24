import React, { useState } from 'react';
import axios from 'axios';
import './Pushups.css'; // We'll define a matching CSS file for the hero layout

function Pushups() {
  const [message, setMessage] = useState('');
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [pushupCount, setPushupCount] = useState(null);

  const startPushups = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/start-pushups');
      setMessage(res.data.message);
      setWorkoutStarted(true);
    } catch (error) {
      setMessage('❌ Failed to start pushup trainer.');
    }
  };

  const endPushups = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/end-pushups');
      setMessage(res.data.message);
      setWorkoutStarted(false);
      if (res.data.pushups !== undefined) {
        setPushupCount(res.data.pushups);
      }
    } catch (error) {
      setMessage('❌ Failed to end workout.');
    }
  };

  return (
    <div className="pushups-page">
      {/* Hero / Header Section */}
      <header className="pushups-hero">
        <div className="hero-content">
          <h1>Pushups Trainer</h1>
          <p>
            Perfect your pushup form with real-time AI feedback. Position yourself in front of the camera
            and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startPushups}>
              Start Pushup Trainer
            </button>
          ) : (
            <button className="hero-button end-button" onClick={endPushups}>
              End Workout
            </button>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

      {/* Main Content Section */}
      <main className="pushups-main">
        {workoutStarted ? (
          <div className="live-feed-section">
            <h3>Live Camera Feed:</h3>
            <img
              src="http://127.0.0.1:5000/video_feed/pushups"
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

        {!workoutStarted && pushupCount !== null && (
          <div className="summary-section">
            <h3>Workout Summary</h3>
            <p>You completed {pushupCount} pushups!</p>
          </div>
        )}
      </main>

      {/* Footer (matching the dark style) */}
      <footer className="pushups-footer">
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

export default Pushups;
