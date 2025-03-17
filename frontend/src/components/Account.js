import React from 'react';
import { useAuth } from '../context/AuthContext';
import './Account.css';

const Account = () => {
  const { user } = useAuth();

  return (
    <div className="account-container">
      <h1>My Account</h1>
      
      <div className="account-info">
        <h2>Personal Information</h2>
        <div className="info-group">
          <label>First Name:</label>
          <p>{user.first_name}</p>
        </div>
        <div className="info-group">
          <label>Last Name:</label>
          <p>{user.last_name}</p>
        </div>
        <div className="info-group">
          <label>Email:</label>
          <p>{user.email}</p>
        </div>
      </div>
      
      <div className="account-actions">
        <h2>Account Actions</h2>
        <button className="btn btn-primary">Edit Profile</button>
        <button className="btn btn-secondary">Change Password</button>
      </div>
    </div>
  );
};

export default Account;
