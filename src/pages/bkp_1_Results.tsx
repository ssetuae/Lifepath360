import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [results, setResults] = useState<any>(null);
  const [tabValue, setTabValue] = useState(0);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState<any>(null);
  const [paymentLoading, setPaymentLoading] = useState(false);
  
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Fetch analysis results
        const response = await axios.get(`/api/analysis/${id}/analyze/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setResults(response.data);
        
        // Check payment status for detailed report
        checkPaymentStatus();
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load results. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [id, navigate]);
  
  const checkPaymentStatus = async () => {
    try {
      setPaymentLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.get(`/api/payments/${id}/check_payment_status/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setPaymentStatus(response.data);
    } catch (err) {
      console.error('Error checking payment status:', err);
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const handleDownloadSummaryReport = async () => {
    try {
      setReportLoading(true);
      setReportError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.get(`/api/reports/${id}/summary/`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        responseType: 'blob'
      });

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `summary_report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setReportError('Failed to download summary report. Please try again.');
    } finally {
      setReportLoading(false);
    }
  };
  
  const handleInitiatePayment = async () => {
    try {
      setPaymentLoading(true);
      
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.post(`/api/payments/${id}/create_payment_intent/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Navigate to payment page
      navigate(`/reports/${id}`, { state: { paymentIntent: response.data } });
    } catch (err) {
      console.error('Error initiating payment:', err);
    } finally {
      setPaymentLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!results) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Results not found or could not be loaded.
        </Alert>
      </Container>
    );
  }

  // Prepare data for charts
  const learningStylesData = Object.entries(results.learning_styles.scores).map(([key, value]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    A: value,
    fullMark: 10,
  }));
  
  const cognitiveStrengthsData = Object.entries(results.cognitive_strengths.scores).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    score: value,
  }));

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Assessment Results
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Student: {results.student_name}
          </Typography>
          <Typography variant="body1" gutterBottom>
            Grade: {results.grade}
          </Typography>
          <Typography variant="body1" gutterBottom>
            Assessment Date: {new Date(results.assessment_date).toLocaleDateString()}
          </Typography>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Button 
            variant="contained" 
            onClick={handleDownloadSummaryReport}
            disabled={reportLoading}
            sx={{ mr: 2 }}
          >
            {reportLoading ? <CircularProgress size={24} /> : 'Download Summary Report'}
          </Button>
          
          {paymentStatus && !paymentStatus.is_paid ? (
            <Button 
              variant="outlined" 
              color="secondary"
              onClick={handleInitiatePayment}
              disabled={paymentLoading}
            >
              {paymentLoading ? <CircularProgress size={24} /> : 'Get Detailed Report (100 AED)'}
            </Button>
          ) : paymentStatus && paymentStatus.is_paid ? (
            <Button 
              variant="outlined" 
              color="secondary"
              onClick={() => navigate(`/reports/${id}`)}
            >
              View Detailed Report
            </Button>
          ) : null}
          
          {reportError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {reportError}
            </Alert>
          )}
        </Box>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="results tabs">
            <Tab label="Learning Styles" />
            <Tab label="Cognitive Strengths" />
            <Tab label="Ideal Learning Environment" />
            <Tab label="Recommendations" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Your Learning Style Profile
                  </Typography>
                  
                  <Typography variant="body1" paragraph>
                    Your primary learning style is <strong>{results.learning_styles.primary.toUpperCase()}</strong> with a secondary preference for <strong>{results.learning_styles.secondary.toUpperCase()}</strong> learning.
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle1" gutterBottom>
                    What this means:
                  </Typography>
                  
                  {results.learning_styles.primary === 'visual' && (
                    <Typography variant="body2" paragraph>
                      As a visual learner, you learn best through seeing information. You benefit from diagrams, charts, videos, and written instructions. You likely have a good visual memory and can easily recall what you've seen.
                    </Typography>
                  )}
                  
                  {results.learning_styles.primary === 'auditory' && (
                    <Typography variant="body2" paragraph>
                      As an auditory learner, you learn best through listening and speaking. You benefit from lectures, discussions, and verbal instructions. You likely have a good auditory memory and can easily recall what you've heard.
                    </Typography>
                  )}
                  
                  {results.learning_styles.primary === 'kinesthetic' && (
                    <Typography variant="body2" paragraph>
                      As a kinesthetic learner, you learn best through physical activities and hands-on experiences. You benefit from experiments, role-playing, and building models. You likely have a good physical memory and can easily recall what you've done.
                    </Typography>
                  )}
                  
                  {results.learning_styles.primary === 'logical' && (
                    <Typography variant="body2" paragraph>
                      As a logical learner, you learn best through reasoning and systems. You benefit from patterns, categories, and step-by-step processes. You likely have strong analytical skills and enjoy problem-solving.
                    </Typography>
                  )}
                  
                  {results.learning_styles.primary === 'social' && (
                    <Typography variant="body2" paragraph>
                      As a social learner, you learn best through interaction with others. You benefit from group work, discussions, and collaborative projects. You likely have strong communication skills and enjoy working with others.
                    </Typography>
                  )}
                  
                  {results.learning_styles.primary === 'solitary' && (
                    <Typography variant="body2" paragraph>
                      As a solitary learner, you learn best through independent study. You benefit from self-paced learning, quiet reflection, and individual projects. You likely have strong self-discipline and enjoy working alone.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Learning Styles Breakdown
                  </Typography>
                  
                  <Box sx={{ height: 300, mt: 2 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={learningStylesData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="subject" />
                        <PolarRadiusAxis angle={30} domain={[0, 10]} />
                        <Radar name="Learning Style" dataKey="A" stroke="#4a6fa5" fill="#4a6fa5" fillOpacity={0.6} />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle1" gutterBottom>
                    Your Learning Badge:
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Chip 
                      label={
                        results.learning_styles.primary === 'visual' ? 'Visual Voyager' :
                        results.learning_styles.primary === 'auditory' ? 'Sound Scholar' :
                        results.learning_styles.primary === 'kinesthetic' ? 'Hands-On Hero' :
                        results.learning_styles.primary === 'logical' ? 'Logic Legend' :
                        results.learning_styles.primary === 'social' ? 'Team Thinker' :
                        results.learning_styles.primary === 'solitary' ? 'Solo Scholar' :
                        'Learning Explorer'
                      } 
                      color="primary" 
                      sx={{ fontSize: '1.2rem', py: 2, px: 3 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Your Cognitive Strengths
                  </Typography>
                  
                  <Typography variant="body1" paragraph>
                    Your primary cognitive strength is <strong>{results.cognitive_strengths.primary.toUpperCase()}</strong>.
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle1" gutterBottom>
                    What this means:
                  </Typography>
                  
                  {results.cognitive_strengths.primary === 'analytical' && (
                    <Typography variant="body2" paragraph>
                      You excel at breaking down complex problems into smaller parts and examining them systematically. You have strong critical thinking skills and can identify patterns and relationships.
                    </Typography>
                  )}
                  
                  {results.cognitive_strengths.primary === 'creative' && (
                    <Typography variant="body2" paragraph>
                      You excel at generating new ideas and thinking outside the box. You have strong imaginative skills and can approach problems from unique perspectives.
                    </Typography>
                  )}
                  
                  {results.cognitive_strengths.primary === 'practical' && (
                    <Typography variant="body2" paragraph>
                      You excel at applying knowledge to real-world situations. You have strong hands-on skills and can find practical solutions to problems.
                    </Typography>
                  )}
                  
                  {results.cognitive_strengths.primary === 'reflective' && (
                    <Typography variant="body2" paragraph>
                      You excel at thinking deeply about concepts and experiences. You have strong introspective skills and can learn effectively from past experiences.
                    </Typography>
              
(Content truncated due to size limit. Use line ranges to read in chunks)