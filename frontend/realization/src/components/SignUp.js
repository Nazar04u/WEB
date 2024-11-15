import React, { useState } from 'react';
import axios from 'axios';
import "./Login.css";

function Signup() {
    // State for form fields and success/error messages
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    // Handle form submission
    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            // Send a POST request to your Django API
            const response = await axios.post('http://localhost:8001/sign_up/', {
                username,
                password,
            });

            // If the request is successful, display a success message
            setMessage(response.data.message || "Signup successful. Please log in to continue.");

            // Optionally, clear the form fields
            setUsername('');
            setPassword('');
        } catch (error) {
            // Handle errors
            if (error.response) {
                setMessage(error.response.data.message || "Signup failed. Please try again.");
            } else {
                setMessage("An error occurred. Please try again.");
            }
        }
    };

    return (
        <div className="login-container">
          <h2>Sign Up</h2>
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
              Sign Up
            </button>
          </form>
          {message && <p className="message">{message}</p>}
        </div>
      );
}

export default Signup;
