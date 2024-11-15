import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css'; // Import the CSS file
import Home from './components/Home.js';
import Signup from './components/SignUp.js';
import Login from './components/Login.js';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="header">
          <div className="header-left">
            <h1 className="header-title">WEB APP</h1>
          </div>
          <div className="header-right">
            <ul className="nav-links">
              <li><Link to="/">HOME</Link></li>
              <li><Link to="/sign_up">SIGN UP</Link></li>
              <li><Link to="/login">LOGIN</Link></li>
            </ul>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sign_up" element={<Signup />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;