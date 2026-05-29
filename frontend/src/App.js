/**
 * Main Application Component
 */
import React, { useState, useEffect } from 'react';
import './App.css';
import LoginComponent from './components/LoginComponent';
import RegisterComponent from './components/RegisterComponent';
import ChatInterface from './components/ChatInterface';
import apiService from './services/apiService';

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      setCurrentPage('chat');
      // TODO: Load current user profile
    }
  }, []);

  const handleLogin = async (email, password) => {
    setLoading(true);
    try {
      const response = await apiService.loginUser(email, password);
      setCurrentUser(response.user);
      setIsAuthenticated(true);
      setCurrentPage('chat');
    } catch (error) {
      alert('Login failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (username, email, password) => {
    setLoading(true);
    try {
      await apiService.registerUser(username, email, password);
      alert('Registration successful! Please log in.');
      setCurrentPage('login');
    } catch (error) {
      alert('Registration failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.clearToken();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCurrentPage('login');
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        <ChatInterface currentUser={currentUser} onLogout={handleLogout} />
      ) : currentPage === 'login' ? (
        <LoginComponent
          onLogin={handleLogin}
          onSwitchToRegister={() => setCurrentPage('register')}
          loading={loading}
        />
      ) : (
        <RegisterComponent
          onRegister={handleRegister}
          onSwitchToLogin={() => setCurrentPage('login')}
          loading={loading}
        />
      )}
    </div>
  );
}

export default App;
