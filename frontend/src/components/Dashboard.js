import React from 'react';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  
  return (
    <div className="dashboard">
      <h1>Welcome to Your Dashboard, {user?.first_name}!</h1>
      
      <div className="dashboard-section">
        <h2>Your Documents</h2>
        <p>You haven't uploaded any documents yet.</p>
        <button className="btn btn-primary">Upload Document</button>
      </div>
      
      <div className="dashboard-section">
        <h2>Recent Activity</h2>
        <p>No recent activity to display.</p>
      </div>
    </div>
  );
};

export default Dashboard;
