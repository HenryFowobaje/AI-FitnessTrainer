import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase'; // Adjust the path to your firebase.js file
import './Login.css';              // Import the CSS file
import { Link } from 'react-router-dom'; // For navigating to Sign Up
import { useNavigate } from 'react-router-dom';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate(); // Hook to navigate programmatically

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      console.log('User logged in:', userCredential.user);
      navigate('/'); // Redirect to the home page
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        {/* App Title and Subtitle */}
        <h1 className="app-title">FitPal</h1>
        <h2 className="welcome-text">Welcome to FitPal</h2>
        <p className="subtitle">Your AI-powered fitness trainer</p>

        {/* Tabs (Login / Sign Up) */}
        <div className="tabs">
          <button className="tab active">Login</button>
          <Link to="/signup">
            <button className="tab">Sign Up</button>
          </Link>
        </div>

        {/* Form Title & Subtitle */}
        <h3 className="form-title">Login to your account</h3>
        <p className="form-subtitle">
          Enter your email and password to access your fitness dashboard
        </p>

        {/* Login Form */}
        <form className="login-form" onSubmit={handleLogin}>
          <div className="field-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="field-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="actions-row">
            <div className="remember-me">
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember me</label>
            </div>
            <a href="#" className="forgot-link">Forgot password?</a>
          </div>

          {error && <p className="error-message">{error}</p>}

          <button type="submit" className="login-btn">Login</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
