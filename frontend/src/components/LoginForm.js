import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './LoginForm.css';

// Validation schema
const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Invalid email')
    .required('Email is required'),
  password: Yup.string()
    .required('Password is required')
});

const LoginForm = () => {
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      // Convert to form data format for OAuth2 compatibility
      const formData = new FormData();
      formData.append('username', values.email);
      formData.append('password', values.password);

      // Make API call to your FastAPI backend
      const response = await axios.post('http://localhost:8000/auth/token', formData);
      
      // Fetch user info
      const userResponse = await axios.get('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${response.data.access_token}`
        }
      });
      
      // Use the login function from auth context
      login(userResponse.data, response.data.access_token);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error) {
      let errorMessage = 'Login failed. Please check your credentials.';
      
      if (error.response && error.response.data) {
        errorMessage = error.response.data.detail || errorMessage;
      }
      
      setError(errorMessage);
    }
    
    setSubmitting(false);
  };

  return (
    <div className="login-form">
      <h2>Login</h2>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}
      
      <Formik
        initialValues={{
          email: '',
          password: ''
        }}
        validationSchema={LoginSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <Field type="email" name="email" className="form-control" />
              <ErrorMessage name="email" component="div" className="error-message" />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <Field type="password" name="password" className="form-control" />
              <ErrorMessage name="password" component="div" className="error-message" />
            </div>

            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Logging in...' : 'Login'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default LoginForm;
