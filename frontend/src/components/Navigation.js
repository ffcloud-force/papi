import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navigation.css';

const Navigation = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">PAPI</Link>
      </div>
      
      <ul className="navbar-nav">
        <li className="nav-item">
          <Link to="/" className="nav-link">Home</Link>
        </li>
        
        {isAuthenticated ? (
          // Menu items for logged-in users
          <>
            <li className="nav-item">
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
            </li>
            <li className="nav-item">
              <Link to="/chat" className="nav-link">Chat</Link>
            </li>
            <li className="nav-item">
              <Link to="/account" className="nav-link">My Account</Link>
            </li>
            <li className="nav-item">
              <button onClick={logout} className="nav-link logout-btn">Logout</button>
            </li>
            <li className="nav-item user-greeting">
              Hello, {user?.first_name || 'User'}
            </li>
          </>
        ) : (
          // Menu items for guests
          <>
            <li className="nav-item">
              <Link to="/register" className="nav-link">Register</Link>
            </li>
            <li className="nav-item">
              <Link to="/login" className="nav-link">Login</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navigation;
