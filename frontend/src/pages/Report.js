import React, { useEffect, useState } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  query,
  where,
  orderBy,
  limit,
  getDocs
} from "firebase/firestore";
import "./Report.css";

function Report() {
  const [reportData, setReportData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch reports only after confirming the user is available.
  const fetchReports = async (user) => {
    try {
      const q = query(
        collection(db, "workouts"),
        where("userId", "==", user.uid),
        orderBy("timestamp", "desc"),
        limit(5)
      );

      const snapshot = await getDocs(q);
      console.log("📦 Docs found:", snapshot.docs.length);

      if (snapshot.empty) {
        console.log("🕳 No reports found for this user");
      }

      const data = snapshot.docs.map(doc => {
        const d = doc.data();
        return {
          type: d.workout?.charAt(0).toUpperCase() + d.workout?.slice(1),
          date: new Date(d.timestamp).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric"
          }),
          reps: d.reps,
          duration: `${Math.max(1, Math.round(d.duration_sec / 60))} min`,
          calories: d.calories ?? 0
        };
      });

      console.log("📊 Final report data:", data);
      setReportData(data);
    } catch (error) {
      console.error("❌ Error fetching workout reports:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(user => {
      console.log("👤 Auth state changed:", user);
      if (user) {
        // User is authenticated—fetch reports.
        fetchReports(user);
      } else {
        // No user is signed in, update UI accordingly.
        setLoading(false);
        console.warn("⚠️ No user logged in — can't fetch reports");
      }
    });

    // Cleanup the listener on unmount.
    return unsubscribe;
  }, []);

  return (
    <div className="report-page">
      <h2 className="report-title">Recent Workout History</h2>
      <p className="report-subtitle">Your last 5 workout sessions</p>

      {loading ? (
        <p>Loading your progress...</p>
      ) : reportData.length === 0 ? (
        <p>No workouts found yet. Try completing a workout first!</p>
      ) : (
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
                <div className="report-extra-row">
                  <span className="report-calories">🔥 {entry.calories} kcal</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Report;
