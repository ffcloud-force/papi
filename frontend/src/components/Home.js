import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Home.css';

const Home = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="home">
      <h1>Wilkommen bei PAPI</h1>
      <p>Dein Assistent für die mündliche Approbationsprüfung als Psychotherapeut*in.</p>
      
      {!isAuthenticated ? (
        <div className="cta-buttons">
          <Link to="/register" className="btn btn-primary">Account erstellen</Link>
          <Link to="/login" className="btn btn-secondary">Login</Link>
        </div>
      ) : (
        <div className="cta-buttons">
          <Link to="/dashboard" className="btn btn-primary">Zum Dashboard</Link>
          <Link to="/chat" className="btn btn-secondary">Starten</Link>
        </div>
      )}
      
      <div className="features">
        <div className="feature">
          <h2>Fälle hochladen</h2>
          <p>Sicherer Upload und Verwaltung Ihrer Fälle.</p>
        </div>
        <div className="feature">
          <h2>Fragen stellen</h2>
          <p>Erhalte Antworten basierend auf Ihren hochgeladenen Fällen.</p>
        </div>
        <div className="feature">
          <h2>Sicherer Zugang</h2>
          <p>Ihre Daten sind gesichert und nur für Sie zugänglich.</p>
        </div>
      </div>
    </div>
  );
};

export default Home;
