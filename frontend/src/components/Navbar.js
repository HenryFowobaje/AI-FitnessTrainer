import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <h2 className="logo">FitPal</h2>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/squats">Squats</Link></li>
        <li><Link to="/pushups">Pushups</Link></li>
        <li><Link to="/bicep-curls">Bicep Curls</Link></li>
        <li><Link to="/report">Report</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar; 