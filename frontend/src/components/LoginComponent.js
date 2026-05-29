/**
 * Login Component
 */
import React, { useState } from 'react';
import './LoginComponent.css';

function LoginComponent({ onLogin, onSwitchToRegister, loading }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      await onLogin(email, password);
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Encrypted Messaging</h1>
        <p className="subtitle">Secure communication when Signal is down</p>
        
        <form onSubmit={handleSubmit}>
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
              placeholder="Enter your password"
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="login-btn">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="switch-auth">
          <p>Don't have an account?</p>
          <button
            type="button"
            onClick={onSwitchToRegister}
            disabled={loading}
            className="switch-btn"
          >
            Create one
          </button>
        </div>

        <div className="info-box">
          <h3>🔒 Your Privacy Matters</h3>
          <ul>
            <li>End-to-end encryption on all messages</li>
            <li>Only you and the recipient can read your messages</li>
            <li>Works when other services are unavailable</li>
            <li>Open source and auditable</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default LoginComponent;
