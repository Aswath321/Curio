import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './auth.css';
import { FaGoogle } from 'react-icons/fa';
import { RobotCanvas } from './RobotModel';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [role, setRole] = useState('student'); // Default role
  const { login, googleSignIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await login(email, password);
      // Navigate based on selected role
      if (role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (error) {
      console.error('Error logging in:', error);
      setError(`Error logging in: ${error.message}`);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      setError('');
      await googleSignIn();
      // Navigate based on selected role for Google sign-in as well
      if (role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (error) {
      console.error('Error signing in with Google:', error);
      setError(`Error signing in with Google: ${error.message}`);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-page-wrapper">
        <div className="auth-page-form fade-in">
          <div className="auth-page-logo">Curio Assistant</div>
          <h2 className="auth-page-heading">Welcome Back</h2>
          {error && <p className="error-message">{error}</p>}
          <form onSubmit={handleSubmit} className="auth-page-form">
            <div className="role-selector">
              <select 
                value={role} 
                onChange={(e) => setRole(e.target.value)}
                className="auth-page-input"
              >
                <option value="student">Student</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <input
              className="auth-page-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
            />
            <input
              className="auth-page-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
            <button type="submit" className="auth-page-button">
              Sign In
            </button>
          </form>
          <div className="social-login">
            <div className="social-icon" onClick={handleGoogleSignIn}>
              <FaGoogle />
            </div>
          </div>
          <p className="auth-link">
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </div>

        <div className="auth-page-sidebar fade-in">
          <div className="auth-page-robot-section">
            <RobotCanvas />
          </div>
          <h2 className="auth-page-heading">First Time Here?</h2>
          <p>Sign up and discover a great amount of new opportunities!</p>
          <Link to="/signup">
            <button className="auth-page-button">Sign Up</button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;