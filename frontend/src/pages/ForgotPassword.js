// ForgotPassword.js
import React, { useState } from 'react';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../firebase';
import './ForgotPassword.css'; // Optional styling
import { Link } from 'react-router-dom';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleReset = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    try {
      await sendPasswordResetEmail(auth, email);
      setMessage('📧 Password reset email sent!');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="forgot-password-page">
      <div className="forgot-card">
        <h2>Reset Your Password</h2>
        <p>Enter the email associated with your account</p>
        <form onSubmit={handleReset}>
          <input
            type="email"
            placeholder="name@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit">Send Reset Link</button>
        </form>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <Link to="/login" className="back-link">← Back to Login</Link>
      </div>
    </div>
  );
}

export default ForgotPassword;
