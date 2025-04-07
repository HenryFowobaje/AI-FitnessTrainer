import React, { useState } from 'react';
import axios from 'axios';
import './Pushups.css';

function Pushups() {
  const [message, setMessage] = useState('');
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [repData, setRepData] = useState(null);

  const startPushups = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/start-pushups');
      setMessage(res.data.message);
      setWorkoutStarted(true);
      setRepData(null);
    } catch (error) {
      setMessage('❌ Failed to start pushup trainer.');
    }
  };

  const endPushups = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/end-pushups');
      setMessage(res.data.message);
      setWorkoutStarted(false);
    } catch (error) {
      setMessage('❌ Failed to end pushup workout.');
    }
  };

  const generateReport = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/generate-pushups-report');
      setRepData(res.data);
      setMessage(res.data.message);
    } catch (error) {
      setMessage('❌ Failed to generate report.');
    }
  };

  return (
    <div className="pushups-page">
      <header className="pushups-hero">
        <div className="hero-content">
          <h1 style={{ color: "#000" }}>Pushups Trainer</h1>
          <p>
            Perfect your pushup form with real-time AI feedback. Position yourself in front of the camera
            and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startPushups}>
              Start Pushup Trainer
            </button>
          ) : (
            <>
              <button className="hero-button end-button" onClick={endPushups}>
                End Workout
              </button>
              <button
                className="hero-button end-button"
                style={{ marginLeft: '10px' }}
                onClick={generateReport}
              >
                Generate Report
              </button>
            </>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

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

        {!workoutStarted && repData && (
          <div className="summary-section">
            <h3>Workout Summary</h3>
            <p>✅ You completed <strong>{repData.reps}</strong> pushups!</p>
            <p>⏱️ Duration: {repData.duration} seconds</p>
            <p>🔥 Estimated Calories Burned: {repData.calories} kcal</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default Pushups;
