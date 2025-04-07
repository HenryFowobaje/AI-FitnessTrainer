import React, { useState } from "react";
import axios from "axios";
import "./Squats.css";
import { saveWorkoutReport } from "../reportService";

function Squats() {
  const [message, setMessage] = useState("");
  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [repData, setRepData] = useState(null);

  const startSquats = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/start-squats");
      setMessage(res.data.message);
      setWorkoutStarted(true);
      setRepData(null);
    } catch (error) {
      setMessage("❌ Failed to start squat trainer.");
    }
  };

  const endSquats = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/end-squats");
      setMessage(res.data.message);
      setWorkoutStarted(false);
    } catch (error) {
      setMessage("❌ Failed to end squat workout.");
    }
  };

  const generateReport = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/generate-squats-report');
      const reportData = res.data;
      setRepData(reportData);
      setMessage(reportData.message);

      // Prepare the report object for Firebase
      const reportToSave = {
        workout: "squats",
        timestamp: new Date().toISOString(),
        reps: reportData.reps,
        duration_sec: reportData.duration,
        mode: "default",
        calories: reportData.calories
      };

      await saveWorkoutReport(reportToSave);
    } catch (error) {
      setMessage("❌ Failed to generate report.");
    }
  };

  return (
    <div className="squats-page">
      <header className="squats-hero">
        <div className="hero-content">
          <h1 style={{ color: "#000" }}>Squats Trainer</h1>
          <p>
            Perfect your squat form with real-time AI feedback. Position
            yourself in front of the camera and follow the instructions.
          </p>
          {!workoutStarted ? (
            <button className="hero-button" onClick={startSquats}>
              Start Squat Trainer
            </button>
          ) : (
            <div className="button-group">
              <button className="hero-button end-button" onClick={endSquats}>
                End Workout
              </button>
              <button
                className="hero-button end-button"
                onClick={generateReport}
              >
                Generate Report
              </button>
            </div>
          )}
          {message && <p className="hero-message">{message}</p>}
        </div>
      </header>

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

        {!workoutStarted && repData && (
          <div className="summary-section">
            <h3>Workout Summary</h3>
            <p>
              ✅ You completed <strong>{repData.reps}</strong> squats!
            </p>
            <p>⏱️ Duration: {repData.duration} seconds</p>
            <p>🔥 Estimated Calories Burned: {repData.calories} kcal</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default Squats;
