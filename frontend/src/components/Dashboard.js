import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileToUpload, setFileToUpload] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/cases/get_all_cases`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }

      if (!response.ok) {
        throw new Error('Failed to fetch cases');
      }

      const data = await response.json();
      setCases(data);
    } catch (err) {
      console.error('Error fetching cases:', err);
      setError(err.message || 'Failed to load your cases. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFileToUpload(e.target.files[0]);
    setUploadStatus('');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!fileToUpload) return;

    setUploadStatus('uploading');
    const formData = new FormData();
    formData.append('file', fileToUpload);

    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/cases/upload_case`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      setUploadStatus('success');
      setFileToUpload(null);
      // Refresh cases list
      fetchCases();
    } catch (err) {
      console.error('Error uploading file:', err);
      setUploadStatus('error');
      setError(err.message);
    }
  };

  const handleDeleteCase = async (caseId) => {
    if (!window.confirm('Are you sure you want to delete this case?')) return;

    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(`${API_URL}/cases/delete_case/${caseId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        throw new Error('Authentication failed. Please login again.');
      }

      if (!response.ok) {
        throw new Error('Failed to delete case');
      }

      // Update the cases list
      setCases(cases.filter(c => c.id !== caseId));
    } catch (err) {
      console.error('Error deleting case:', err);
      setError(err.message || 'Failed to delete case. Please try again.');
    }
  };

  const startChat = (caseId) => {
    navigate(`/chat?caseId=${caseId}`);
  };

  return (
    <div className="dashboard">
      <h1>Welcome to Your Dashboard, {user?.first_name}!</h1>
      
      <div className="dashboard-section">
        <h2>Upload Document</h2>
        <form onSubmit={handleUpload} className="upload-form">
          <input 
            type="file" 
            onChange={handleFileChange} 
            className="file-input"
            accept=".pdf,.doc,.docx,.txt"
          />
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={!fileToUpload || uploadStatus === 'uploading'}
          >
            {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
        {uploadStatus === 'success' && <p className="success-message">File uploaded successfully!</p>}
        {uploadStatus === 'error' && <p className="error-message">{error}</p>}
      </div>
      
      <div className="dashboard-section">
        <h2>Your Documents</h2>
        {loading ? (
          <p>Loading your documents...</p>
        ) : cases.length === 0 ? (
          <p>You haven't uploaded any documents yet.</p>
        ) : (
          <div className="cases-list">
            {cases.map(caseItem => (
              <div key={caseItem.id} className="case-item">
                <div className="case-info">
                  <h3>{caseItem.filename}</h3>
                  <p>Status: {caseItem.status}</p>
                </div>
                <div className="case-actions">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => startChat(caseItem.id)}
                  >
                    Chat about this case
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleDeleteCase(caseItem.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Dashboard;
