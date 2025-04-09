// Report.js
import React from 'react';
import './Report.css'; // Optional: for styling if needed

const reportData = [
  { type: 'Pushups', date: 'March 22, 2025', reps: 35, duration: '15 min' },
  { type: 'Squats', date: 'March 21, 2025', reps: 30, duration: '20 min' },
  { type: 'Bicep Curls', date: 'March 20, 2025', reps: 25, duration: '12 min' },
  { type: 'Pushups', date: 'March 19, 2025', reps: 30, duration: '12 min' },
  { type: 'Squats', date: 'March 18, 2025', reps: 25, duration: '18 min' }
];

function Report() {
  return (
    <div className="report-page">
      <h2 className="report-title">Recent Workout History</h2>
      <p className="report-subtitle">Your last 5 workout sessions</p>

      <div className="report-list">
        {reportData.map((entry, index) => (
          <div key={index} className="report-card">
            <div className="report-color-bar" />
            <div className="report-info">
              <div className="report-top-row">
                <span className="report-type">{entry.type}</span>
                <span className="report-reps">{entry.reps} reps</span>
              </div>
              <div className="report-bottom-row">
                <span className="report-date">{entry.date}</span>
                <span className="report-duration">{entry.duration}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Report;
