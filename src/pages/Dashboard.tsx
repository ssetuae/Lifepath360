import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  Stack
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import HistoryIcon from '@mui/icons-material/History';

interface Assessment {
  id: number;
  status: string;
  start_time: string;
  end_time: string | null;
  student: {
    id: number;
    first_name: string;
    last_name: string;
    grade: string;
  };
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Get user from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    // Fetch assessments
    const fetchAssessments = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await axios.get('/api/assessments/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setAssessments(response.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load assessments. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAssessments();
  }, [navigate]);

  const startNewAssessment = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      setLoading(true);
      const response = await axios.post('/api/assessments/', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Navigate to the assessment page
      navigate(`/assessment/${response.data.id}`);
    } catch (err) {
      setError('Failed to start a new assessment. Please try again.');
      setLoading(false);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <Chip label="Not Started" color="default" size="small" />;
      case 'IN_PROGRESS':
        return <Chip label="In Progress" color="primary" size="small" />;
      case 'COMPLETED':
        return <Chip label="Completed" color="success" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <PersonIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
              <Typography component="h1" variant="h4">
                Welcome, {user?.first_name || 'Student'}!
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary">
              Learning Compass helps you discover your unique learning style and provides personalized recommendations to enhance your educational journey.
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                size="large" 
                onClick={startNewAssessment}
                startIcon={<AssessmentIcon />}
              >
                Start New Assessment
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Assessments */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <HistoryIcon sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
              <Typography component="h2" variant="h5">
                Recent Assessments
              </Typography>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            {assessments.length === 0 ? (
              <Typography variant="body1" color="text.secondary">
                You haven't taken any assessments yet. Start your first assessment to discover your learning style!
              </Typography>
            ) : (
              <Grid container spacing={2}>
                {assessments.map((assessment) => (
                  <Grid item xs={12} md={6} lg={4} key={assessment.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="h6" component="div">
                            Assessment #{assessment.id}
                          </Typography>
                          {getStatusChip(assessment.status)}
                        </Box>
                        
                        <Divider sx={{ my: 1 }} />
                        
                        <Stack spacing={1}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              Student:
                            </Typography>
                            <Typography variant="body2">
                              {assessment.student.first_name} {assessment.student.last_name}
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              Grade:
                            </Typography>
                            <Typography variant="body2">
                              {assessment.student.grade}
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              Started:
                            </Typography>
                            <Typography variant="body2">
                              {formatDate(assessment.start_time)}
                            </Typography>
                          </Box>
                          
                          {assessment.end_time && (
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Typography variant="body2" color="text.secondary">
                                Completed:
                              </Typography>
                              <Typography variant="body2">
                                {formatDate(assessment.end_time)}
                              </Typography>
                            </Box>
                          )}
                        </Stack>
                      </CardContent>
                      
                      <CardActions>
                        {assessment.status === 'PENDING' || assessment.status === 'IN_PROGRESS' ? (
                          <Button 
                            size="small" 
                            color="primary"
                            onClick={() => navigate(`/assessment/${assessment.id}`)}
                          >
                            Continue Assessment
                          </Button>
                        ) : (
                          <>
                            <Button 
                              size="small" 
                              color="primary"
                              onClick={() => navigate(`/results/${assessment.id}`)}
                            >
                              View Results
                            </Button>
                            <Button 
                              size="small" 
                              color="secondary"
                              onClick={() => navigate(`/reports/${assessment.id}`)}
                            >
                              View Reports
                            </Button>
                          </>
                        )}
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>

        {/* Learning Resources */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <SchoolIcon sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
              <Typography component="h2" variant="h5">
                Learning Resources
              </Typography>
            </Box>
            
            <Typography variant="body1" paragraph>
              Explore these resources to enhance your learning journey:
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" component="div" gutterBottom>
                      Learning Styles Guide
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Understand different learning styles and how to leverage your strengths for academic success.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Learn More</Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" component="div" gutterBottom>
                      Study Techniques
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Discover effective study methods tailored to different learning styles and subjects.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Learn More</Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" component="div" gutterBottom>
                      Course Catalog
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Browse our comprehensive catalog of courses designed to match various learning styles and interests.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Browse Courses</Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
