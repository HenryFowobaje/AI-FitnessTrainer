import React from 'react';
import { Link } from 'react-router-dom'; // <-- Import Link for routing
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>Your AI Fitness Trainer</h1>
          <p>
            Get real-time form correction, personalized workouts, and join a
            motivating fitness community.
          </p>
          <button className="cta-button">Get Started</button>
        </div>
      </section>

      {/* How FitPal Works */}
      <section className="how-it-works">
        <h2>How FitPal Works</h2>
        <div className="features">
          <div className="feature-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/brain.png"
              alt="Form Correction"
            />
            <h3>Real-time Form Correction</h3>
            <p>
              Our AI analyzes your posture in real-time and provides instant
              feedback to ensure proper form.
            </p>
          </div>
          <div className="feature-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/task.png"
              alt="Personalized Workouts"
            />
            <h3>Personalized Workouts</h3>
            <p>
              Get custom workout plans based on your goals, fitness level, and
              progress.
            </p>
          </div>
          <div className="feature-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/conference-call.png"
              alt="Community"
            />
            <h3>Community Motivation</h3>
            <p>
              Join challenges, share achievements, and stay motivated with our
              fitness community.
            </p>
          </div>
        </div>
      </section>

      {/* Start Training Now */}
      <section className="start-training">
        <h2>Start Training Now</h2>
        <div className="training-cards">
          <div className="training-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/handstand-push-ups.png"
              alt="Pushups"
            />
            <h3>Pushups</h3>
            <p>Perfect your pushup form with real-time feedback.</p>
            {/* Link to /pushups */}
            <Link to="/pushups" className="training-button">
              Start Training
            </Link>
          </div>
          <div className="training-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/dumbbell.png"
              alt="Squats"
            />
            <h3>Squats</h3>
            <p>Build lower body strength with proper form.</p>
            {/* Link to /squats */}
            <Link to="/squats" className="training-button">
              Start Training
            </Link>
          </div>
          <div className="training-card">
            <img
              src="https://img.icons8.com/ios-filled/100/000000/biceps.png"
              alt="Bicep Curls"
            />
            <h3>Bicep Curls</h3>
            <p>Build arm strength with guided bicep curl training.</p>
            {/* Link to /bicep-curls */}
            <Link to="/bicep-curls" className="training-button">
              Start Training
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stat-card">
          <h3>1000+</h3>
          <p>Active Users</p>
        </div>
        <div className="stat-card">
          <h3>50K+</h3>
          <p>Workouts Completed</p>
        </div>
        <div className="stat-card">
          <h3>95%</h3>
          <p>Form Accuracy</p>
        </div>
        <div className="stat-card">
          <h3>3</h3>
          <p>Exercise Types</p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h2>Ready to Transform Your Fitness Journey?</h2>
        <p>
          Join FitPal today and experience the future of fitness training with
          AI-powered form correction.
        </p>
        <button className="cta-button">Get Started Now</button>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-brand">
          <h3>FitPal</h3>
          <p>
            Your AI-powered fitness trainer for perfect form and personalized
            workouts.
          </p>
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
        <div className="footer-bottom">
          <p>© 2025 FitPal. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Home;
