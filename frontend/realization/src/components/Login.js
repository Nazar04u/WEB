import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

function Login() {
  // State for form fields and success/error messages
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      // Send a POST request to your Django API for login
      const response = await axios.post('http://localhost:8001/login/', {
        username,
        password,
      });

      // If the request is successful, save tokens to local storage
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      // Display a success message and optionally redirect the user
      setMessage("Login successful!");

      // Optionally, clear the form fields
      setUsername('');
      setPassword('');

      // Redirect to a protected route or home page if needed
      // window.location.href = '/'; // Uncomment if you want to redirect

    } catch (error) {
      // Handle errors
      if (error.response) {
        setMessage(error.response.data.error || "Login failed. Please check your credentials.");
      } else {
        setMessage("An error occurred. Please try again.");
      }
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="email">Your Username</label>
          <input
            type="text"
            id="email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="sign-in-button">
          Login
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default Login;