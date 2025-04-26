// Security middleware for the backend
// This file implements various security measures to protect user data

const jwt = require('jsonwebtoken');
const { User } = require('../users/models');
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const xss = require('xss-clean');
const hpp = require('hpp');
const cors = require('cors');

// Rate limiting configuration
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per windowMs
  message: 'Too many login attempts from this IP, please try again after 15 minutes'
});

const apiLimiter = rateLimit({
  windowMs: 10 * 60 * 1000, // 10 minutes
  max: 100, // 100 requests per windowMs
  message: 'Too many requests from this IP, please try again after 10 minutes'
});

// CORS configuration
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'https://learning-compass.render.com',
  optionsSuccessStatus: 200,
  credentials: true
};

// Function to verify JWT token
const verifyToken = async (req, res, next) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Access denied. No token provided.' });
    }

    const token = authHeader.split(' ')[1];
    
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Check if user exists and is active
    const user = await User.objects.get(id=decoded.user_id);
    if (!user || !user.is_active) {
      return res.status(401).json({ error: 'Invalid token or user is inactive.' });
    }
    
    // Add user to request object
    req.user = user;
    
    // Log access for audit trail
    logUserAccess(user.id, req.method, req.originalUrl);
    
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired. Please log in again.' });
    }
    return res.status(401).json({ error: 'Invalid token.' });
  }
};

// Function to check if user has admin role
const isAdmin = (req, res, next) => {
  if (!req.user || !req.user.is_admin) {
    return res.status(403).json({ error: 'Access denied. Admin privileges required.' });
  }
  next();
};

// Function to check if user has teacher role
const isTeacher = (req, res, next) => {
  if (!req.user || (req.user.user_type !== 'teacher' && !req.user.is_admin)) {
    return res.status(403).json({ error: 'Access denied. Teacher privileges required.' });
  }
  next();
};

// Function to check if user has access to student data
const hasStudentAccess = async (req, res, next) => {
  try {
    const studentId = req.params.student_id || req.body.student_id;
    if (!studentId) {
      return next();
    }
    
    // Admin and teachers have access to all students
    if (req.user.is_admin || req.user.user_type === 'teacher') {
      return next();
    }
    
    // Students can only access their own data
    if (req.user.user_type === 'student' && req.user.student && req.user.student.id.toString() === studentId) {
      return next();
    }
    
    // Parents can only access their children's data
    if (req.user.user_type === 'parent' && req.user.parent) {
      const children = await req.user.parent.children.all();
      if (children.some(child => child.id.toString() === studentId)) {
        return next();
      }
    }
    
    return res.status(403).json({ error: 'Access denied. You do not have permission to access this student\'s data.' });
  } catch (error) {
    return res.status(500).json({ error: 'Error checking student access permissions.' });
  }
};

// Function to check if user has access to assessment data
const hasAssessmentAccess = async (req, res, next) => {
  try {
    const assessmentId = req.params.id || req.params.assessment_id || req.body.assessment_id;
    if (!assessmentId) {
      return next();
    }
    
    // Admin and teachers have access to all assessments
    if (req.user.is_admin || req.user.user_type === 'teacher') {
      return next();
    }
    
    // Get assessment
    const assessment = await Assessment.objects.get(id=assessmentId);
    if (!assessment) {
      return res.status(404).json({ error: 'Assessment not found.' });
    }
    
    // Students can only access their own assessments
    if (req.user.user_type === 'student' && req.user.student && req.user.student.id === assessment.student.id) {
      return next();
    }
    
    // Parents can only access their children's assessments
    if (req.user.user_type === 'parent' && req.user.parent) {
      const children = await req.user.parent.children.all();
      if (children.some(child => child.id === assessment.student.id)) {
        return next();
      }
    }
    
    return res.status(403).json({ error: 'Access denied. You do not have permission to access this assessment.' });
  } catch (error) {
    return res.status(500).json({ error: 'Error checking assessment access permissions.' });
  }
};

// Function to encrypt sensitive data
const encryptData = (text) => {
  const algorithm = 'aes-256-cbc';
  const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return {
    iv: iv.toString('hex'),
    encryptedData: encrypted
  };
};

// Function to decrypt sensitive data
const decryptData = (encryptedText, iv) => {
  const algorithm = 'aes-256-cbc';
  const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
  const decipher = crypto.createDecipheriv(algorithm, key, Buffer.from(iv, 'hex'));
  let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
};

// Function to log user access for audit trail
const logUserAccess = async (userId, method, url) => {
  try {
    await AccessLog.objects.create({
      user_id: userId,
      method: method,
      url: url,
      timestamp: new Date(),
      ip_address: req.ip
    });
  } catch (error) {
    console.error('Error logging user access:', error);
  }
};

// Apply security middleware to app
const applySecurityMiddleware = (app) => {
  // Set security HTTP headers
  app.use(helmet());
  
  // Enable CORS
  app.use(cors(corsOptions));
  
  // Prevent XSS attacks
  app.use(xss());
  
  // Prevent HTTP Parameter Pollution
  app.use(hpp());
  
  // Rate limiting
  app.use('/api/users/login/', loginLimiter);
  app.use('/api/', apiLimiter);
  
  // JWT authentication for protected routes
  app.use('/api/', verifyToken);
  
  // Admin routes protection
  app.use('/api/admin/', isAdmin);
  
  // Set secure cookies
  app.use((req, res, next) => {
    res.cookie('secure', 'true', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    });
    next();
  });
  
  // Add security headers
  app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Content-Security-Policy', "default-src 'self'");
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
  });
};

module.exports = {
  verifyToken,
  isAdmin,
  isTeacher,
  hasStudentAccess,
  hasAssessmentAccess,
  encryptData,
  decryptData,
  applySecurityMiddleware,
  loginLimiter,
  apiLimiter
};
