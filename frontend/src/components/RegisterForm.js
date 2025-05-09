import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

// Validation schema
const RegisterSchema = Yup.object().shape({
  first_name: Yup.string()
    .min(2, 'Too Short!')
    .max(50, 'Too Long!')
    .required('First name is required'),
  last_name: Yup.string()
    .min(2, 'Too Short!')
    .max(50, 'Too Long!')
    .required('Last name is required'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .max(20, 'Password must be less than 20 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwords must match')
    .required('Confirm password is required')
});

const RegisterForm = () => {
  const [status, setStatus] = useState({
    submitted: false,
    success: false,
    message: ''
  });

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      // Remove confirmPassword as it's not needed in the API
      const { confirmPassword, ...userData } = values;
      
      // Add confirm_password to match backend schema
      const apiData = {
        ...userData,
        confirm_password: confirmPassword
      };
      
      // Make API call to your FastAPI backend
      const response = await axios.post('http://localhost:8000/users/', apiData);
      
      setStatus({
        submitted: true,
        success: true,
        message: 'Registration successful! You can now log in.'
      });
      
      resetForm();
    } catch (error) {
      let errorMessage = 'Registration failed. Please try again.';
      
      if (error.response && error.response.data) {
        // Handle validation errors from FastAPI
        if (Array.isArray(error.response.data.detail)) {
          // Format validation errors
          errorMessage = error.response.data.detail
            .map(err => `${err.loc[err.loc.length - 1]}: ${err.msg}`)
            .join('\n');
        } else {
          // Handle single error message
          errorMessage = error.response.data.detail || errorMessage;
        }
      }
      
      setStatus({
        submitted: true,
        success: false,
        message: errorMessage
      });
    }
    
    setSubmitting(false);
  };

  return (
    <div className="register-form">
      <h2>Create an Account</h2>
      
      {status.submitted && (
        <div className={`alert ${status.success ? 'alert-success' : 'alert-danger'}`}>
          {status.message.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}
      
      <Formik
        initialValues={{
          first_name: '',
          last_name: '',
          email: '',
          password: '',
          confirmPassword: ''
        }}
        validationSchema={RegisterSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <Field type="text" name="first_name" className="form-control" />
              <ErrorMessage name="first_name" component="div" className="error-message" />
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <Field type="text" name="last_name" className="form-control" />
              <ErrorMessage name="last_name" component="div" className="error-message" />
            </div>

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

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <Field type="password" name="confirmPassword" className="form-control" />
              <ErrorMessage name="confirmPassword" component="div" className="error-message" />
            </div>

            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Registering...' : 'Register'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default RegisterForm;
