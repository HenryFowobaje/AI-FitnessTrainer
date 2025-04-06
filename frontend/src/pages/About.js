import React from "react";
import "./About.css"; // optional for styling

function About() {
  return (
    <div className="about-container">
      <h1>About FitPal</h1>
      <p>
        <strong>FitPal</strong> is a browser-based AI fitness trainer that
        provides real-time feedback on bodyweight exercises using computer
        vision and pose estimation. It’s designed to help users improve form,
        count reps accurately, and stay motivated—all without additional
        hardware.
      </p>

      <h2>Meet the Developers</h2>
      <p>
        FitPal was created by a team of senior Computer Science students at Fisk
        University as part of their capstone project. Driven by a shared passion
        for AI, computer vision, and health technology, the team aimed to build
        an intelligent and accessible fitness companion. From architecture to
        implementation, each member contributed to designing the real-time
        tracking system, refining exercise logic, and building the frontend
        experience.
      </p>

      <h2>How to Use FitPal</h2>
      <ol>
        <li>
          Navigate to the desired workout (Pushups, Squats, or Bicep Curls) from
          the homepage or navbar.
        </li>
        <li>
          Click the <strong>"Start Trainer"</strong> button to activate your
          webcam and begin the session.
        </li>
        <li>
          Perform reps while keeping proper form. The system will automatically
          count valid reps and display feedback.
        </li>
        <li>
          To end the session, click <strong>"End Workout"</strong>. Your
          progress will be saved.
        </li>
        <li>
          Visit the <strong>Reports</strong> tab to view your rep history
          (feature in development).
        </li>
      </ol>

      <h2>Technologies Used</h2>
      <ul>
        <li>
          <strong>Frontend:</strong> React.js
        </li>
        <li>
          <strong>Backend:</strong> Flask
        </li>
        <li>
          <strong>Pose Estimation:</strong> TensorFlow MoveNet
        </li>
        <li>
          <strong>Computer Vision:</strong> OpenCV
        </li>
      </ul>

      <p>Thanks for trying FitPal. Let's get stronger—rep by rep! 💪</p>
    </div>
  );
}

export default About;
