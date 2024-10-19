import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { signup, googleSignIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await signup(email, password);
      navigate('/');
    } catch (error) {
      console.error("Error signing up:", error);
      setError(`Error signing up: ${error.message}`);
    }
  };

  const handleGoogleSignUp = async () => {
    try {
      setError('');
      await googleSignIn();
      navigate('/');
    } catch (error) {
      console.error("Error signing up with Google:", error);
      setError(`Error signing up with Google: ${error.message}`);
    }
  };

  return (
    <div className="auth-container">
      <h2>Sign Up</h2>
      {error && <p className="error-message">{error}</p>}
      
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Sign Up</button>
      </form>
      
      <button onClick={handleGoogleSignUp} className="google-signup-btn">
        Sign up with Google
      </button>
      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
};

export default Signup;
  