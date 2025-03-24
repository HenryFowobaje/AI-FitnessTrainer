// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';

import Home from './pages/Home';
import Squats from './pages/Squats';
import Pushups from './pages/Pushups';
import BicepCurls from './pages/BicepCurls';
import About from './pages/About';
import Report from './pages/Report';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/squats" element={<Squats />} />
        <Route path="/pushups" element={<Pushups />} />
        <Route path="/bicep-curls" element={<BicepCurls />} />
        <Route path="/about" element={<About />} />
        <Route path="/report" element={<Report />} />
      </Routes>
    </Router>
  );
}

export default App;
