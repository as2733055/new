/**
 * Register Component
 */
import React, { useState } from 'react';
import './RegisterComponent.css';

function RegisterComponent({ onRegister, onSwitchToLogin, loading }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    try {
      await onRegister(username, email, password);
    } catch (err) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <h1>Create Account</h1>
        <p className="subtitle">Encrypted Messaging System</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
              disabled={loading}
              minLength="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min 8 characters"
              disabled={loading}
              minLength="8"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="register-btn">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="switch-auth">
          <p>Already have an account?</p>
          <button
            type="button"
            onClick={onSwitchToLogin}
            disabled={loading}
            className="switch-btn"
          >
            Login here
          </button>
        </div>

        <div className="info-box">
          <h3>🛡️ Security Features</h3>
          <ul>
            <li>Military-grade RSA-2048 encryption</li>
            <li>AES-256 message encryption</li>
            <li>Unique keys generated for each user</li>
            <li>No plaintext messages stored on server</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default RegisterComponent;
