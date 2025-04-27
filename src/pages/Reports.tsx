import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  Button, 
  CircularProgress, 
  Card, 
  CardContent,
  CardActions,
  Divider,
  Alert
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import PaymentIcon from '@mui/icons-material/Payment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const Reports = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('unpaid'); // unpaid, processing, paid

  useEffect(() => {
    // Fetch report data
    const fetchReport = async () => {
      try {
        setLoading(true);
        // In a real implementation, this would be an API call
        // const response = await fetch(`/api/reports/${id}`);
        // const data = await response.json();
        
        // Mock data for development
        const mockReport = {
          id: id,
          title: 'Learning Style Assessment Report',
          summary_available: true,
          detailed_available: false,
          summary_url: '#',
          detailed_url: null,
          assessment_date: new Date().toLocaleDateString(),
          payment_required: true,
          payment_amount: 49.99,
          payment_status: 'unpaid'
        };
        
        setTimeout(() => {
          setReport(mockReport);
          setPaymentStatus(mockReport.payment_status);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load report. Please try again later.');
        setLoading(false);
      }
    };

    if (id) {
      fetchReport();
    } else {
      setError('Report ID is missing');
      setLoading(false);
    }
  }, [id]);

  const handleDownloadSummary = () => {
    // In a real implementation, this would download the PDF
    alert('Downloading summary report...');
  };

  const handleDownloadDetailed = () => {
    // In a real implementation, this would download the PDF
    alert('Downloading detailed report...');
  };

  const handlePayment = () => {
    // In a real implementation, this would redirect to payment page
    setPaymentStatus('processing');
    
    // Simulate payment processing
    setTimeout(() => {
      setPaymentStatus('paid');
      setReport({
        ...report,
        detailed_available: true,
        detailed_url: '#',
        payment_status: 'paid'
      });
    }, 2000);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button 
          variant="contained" 
          sx={{ mt: 2 }}
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Assessment Reports
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          {report.title}
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Assessment Date: {report.assessment_date}
        </Typography>
        
        <Divider sx={{ my: 3 }} />
        
        <Grid container spacing={3}>
          {/* Summary Report Card */}
          <Grid  xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Summary Report
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  A brief overview of your learning style assessment results.
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  startIcon={<DownloadIcon />}
                  variant="contained" 
                  color="primary"
                  disabled={!report.summary_available}
                  onClick={handleDownloadSummary}
                  fullWidth
                >
                  Download Free Summary
                </Button>
              </CardActions>
            </Card>
          </Grid>
          
          {/* Detailed Report Card */}
          <Grid  xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Detailed Report
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Comprehensive 20-30 page analysis of your learning style, strengths, and personalized recommendations.
                </Typography>
                {report.payment_required && (
                  <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body1" fontWeight="bold" color="primary">
                      ${report.payment_amount}
                    </Typography>
                    {paymentStatus === 'paid' && (
                      <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', color: 'success.main' }}>
                        <CheckCircleIcon fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="body2">Purchased</Typography>
                      </Box>
                    )}
                  </Box>
                )}
              </CardContent>
              <CardActions>
                {paymentStatus === 'unpaid' ? (
                  <Button 
                    startIcon={<PaymentIcon />}
                    variant="contained" 
                    color="secondary"
                    onClick={handlePayment}
                    fullWidth
                  >
                    Purchase Detailed Report
                  </Button>
                ) : paymentStatus === 'processing' ? (
                  <Button 
                    variant="contained" 
                    color="secondary"
                    disabled
                    fullWidth
                  >
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Processing...
                  </Button>
                ) : (
                  <Button 
                    startIcon={<DownloadIcon />}
                    variant="contained" 
                    color="secondary"
                    onClick={handleDownloadDetailed}
                    fullWidth
                  >
                    Download Detailed Report
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Button 
          variant="outlined" 
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default Reports;
