// Frontend security measures for React application

import axios from 'axios';
import { useState, useEffect, createContext, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

// Create Authentication Context
const AuthContext = createContext(null);

// Security configuration for axios
const configureAxiosSecurity = () => {
  // Set base URL
  axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'https://api.learning-compass.render.com';
  
  // Add request interceptor to include JWT token in all requests
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  
  // Add response interceptor to handle authentication errors
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      if (error.response && error.response.status === 401) {
        // Clear token and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};

// Authentication Provider Component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    // Configure axios security
    configureAxiosSecurity();
    
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      try {
        setCurrentUser(JSON.parse(user));
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    
    setLoading(false);
  }, []);
  
  // Login function
  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/users/login/', { email, password });
      
      if (response.data && response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        setCurrentUser(response.data.user);
        
        // Log successful login
        logUserActivity('login', 'success');
        
        return { success: true, user: response.data.user };
      }
    } catch (error) {
      // Log failed login attempt
      logUserActivity('login', 'failure', error.response?.data?.error || 'Login failed');
      
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed. Please check your credentials.' 
      };
    }
  };
  
  // Logout function
  const logout = () => {
    // Log logout activity
    logUserActivity('logout', 'success');
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    navigate('/login');
  };
  
  // Register function
  const register = async (userData) => {
    try {
      const response = await axios.post('/api/users/register/', userData);
      
      if (response.status === 201) {
        // Log successful registration
        logUserActivity('register', 'success', null, userData.email);
        
        return { success: true };
      }
    } catch (error) {
      // Log failed registration
      logUserActivity('register', 'failure', error.response?.data?.error || 'Registration failed', userData.email);
      
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed. Please try again.' 
      };
    }
  };
  
  // Check if user has specific role
  const hasRole = (role) => {
    if (!currentUser) return false;
    
    if (role === 'admin') {
      return currentUser.is_admin;
    } else if (role === 'teacher') {
      return currentUser.is_admin || currentUser.user_type === 'teacher';
    } else if (role === 'parent') {
      return currentUser.user_type === 'parent';
    } else if (role === 'student') {
      return currentUser.user_type === 'student';
    }
    
    return false;
  };
  
  // Log user activity
  const logUserActivity = async (action, status, details = null, resourceId = null) => {
    if (!currentUser) return;
    
    try {
      await axios.post('/api/users/log-activity/', {
        action,
        status,
        details,
        resource_id: resourceId
      });
    } catch (error) {
      console.error('Error logging user activity:', error);
    }
  };
  
  // Context value
  const value = {
    currentUser,
    login,
    logout,
    register,
    hasRole,
    logUserActivity
  };
  
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Protected Route Component
export const PrivateRoute = ({ children }) => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!currentUser) {
      navigate('/login');
    }
  }, [currentUser, navigate]);
  
  return currentUser ? children : null;
};

// Admin Route Component
export const AdminRoute = ({ children }) => {
  const { currentUser, hasRole } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!currentUser || !hasRole('admin')) {
      navigate('/');
    }
  }, [currentUser, hasRole, navigate]);
  
  return currentUser && hasRole('admin') ? children : null;
};

// Teacher Route Component
export const TeacherRoute = ({ children }) => {
  const { currentUser, hasRole } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!currentUser || !hasRole('teacher')) {
      navigate('/');
    }
  }, [currentUser, hasRole, navigate]);
  
  return currentUser && hasRole('teacher') ? children : null;
};

// Security utility functions
export const securityUtils = {
  // Sanitize user input to prevent XSS
  sanitizeInput: (input) => {
    if (!input) return '';
    return input
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  },
  
  // Validate email format
  validateEmail: (email) => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  },
  
  // Validate password strength
  validatePassword: (password) => {
    // At least 10 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{10,}$/;
    return re.test(password);
  },
  
  // Get password strength feedback
  getPasswordStrength: (password) => {
    if (!password) return { score: 0, feedback: 'Password is required' };
    
    let score = 0;
    let feedback = [];
    
    // Length check
    if (password.length < 10) {
      feedback.push('Password should be at least 10 characters long');
    } else {
      score += 1;
    }
    
    // Uppercase check
    if (!/[A-Z]/.test(password)) {
      feedback.push('Password should contain at least one uppercase letter');
    } else {
      score += 1;
    }
    
    // Lowercase check
    if (!/[a-z]/.test(password)) {
      feedback.push('Password should contain at least one lowercase letter');
    } else {
      score += 1;
    }
    
    // Number check
    if (!/\d/.test(password)) {
      feedback.push('Password should contain at least one number');
    } else {
      score += 1;
    }
    
    // Special character check
    if (!/[@$!%*?&]/.test(password)) {
      feedback.push('Password should contain at least one special character (@$!%*?&)');
    } else {
      score += 1;
    }
    
    return {
      score,
      feedback: feedback.join('. ')
    };
  }
};

export default {
  AuthProvider,
  useAuth,
  PrivateRoute,
  AdminRoute,
  TeacherRoute,
  securityUtils
};
