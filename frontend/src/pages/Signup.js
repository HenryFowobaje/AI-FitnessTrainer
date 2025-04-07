import React, { useState } from 'react';
import './Signup.css'; // Import the CSS file
import { useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase'; // Adjust the path as needed
import { Link } from 'react-router-dom';


function Signup() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName]  = useState('');
  const [email, setEmail]        = useState('');
  const [password, setPassword]  = useState('');
  const [confirm, setConfirm]    = useState('');
  const [agree, setAgree]        = useState(false);
  const [error, setError]        = useState('');

  const navigate = useNavigate(); // Hook for programmatic navigation

  const handleSignup = async (e) => {
    e.preventDefault();

    // Basic client-side validation
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (!agree) {
      setError('You must agree to the Terms of Service and Privacy Policy.');
      return;
    }

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      console.log('User signed up:', userCredential.user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-card">
        {/* Logo & Heading */}
        <h1 className="app-title">FitPal</h1>
        <h2 className="welcome-text">Welcome to FitPal</h2>
        <p className="subtitle">Your AI-powered fitness trainer</p>

        {/* Tabs (Static example; implement logic if needed) */}
        <div className="tabs">
        <Link to="/login"><button className="tab">Login</button></Link>
          <button className="tab active">Sign Up</button>
        </div>

        {/* Main Form Title */}
        <h3 className="form-title">Create an account</h3>
        <p className="form-subtitle">
          Enter your information to start your fitness journey
        </p>

        {/* Sign Up Form */}
        <form className="signup-form" onSubmit={handleSignup}>
          <div className="name-row">
            <div className="field-group">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                type="text"
                placeholder="John"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </div>
            <div className="field-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                type="text"
                placeholder="Doe"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </div>
          </div>

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

          <div className="field-group">
            <label htmlFor="confirm">Confirm Password</label>
            <input
              id="confirm"
              type="password"
              placeholder="••••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
            />
          </div>

          <div className="agree-row">
            <input
              type="checkbox"
              id="agree"
              checked={agree}
              onChange={() => setAgree(!agree)}
            />
            <label htmlFor="agree">
              I agree to the <a href="#">Terms of Service</a> and{' '}
              <a href="#">Privacy Policy</a>
            </label>
          </div>

          {error && <p className="error-message">{error}</p>}

          <button type="submit" className="create-account-btn">
            Create Account
          </button>
        </form>
      </div>
    </div>
  );
}

export default Signup;
