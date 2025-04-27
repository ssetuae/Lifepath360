import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Button,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Tooltip,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';

const AdminReports: React.FC = () => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reports, setReports] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [reportLoading, setReportLoading] = useState(false);
  
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Check if user is admin
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (!user.is_admin) {
          navigate('/');
          return;
        }

        // Fetch reports
        const response = await axios.get('/api/admin/reports/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setReports(response.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load reports. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [navigate, refreshTrigger]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleDownloadReport = async (assessmentId: number, reportType: 'summary' | 'detailed') => {
    try {
      setReportLoading(true);
      
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const endpoint = reportType === 'summary' ? 'summary' : 'detailed';
      const response = await axios.get(`/api/reports/${assessmentId}/${endpoint}/`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        responseType: 'blob'
      });

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportType}_report_${assessmentId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(`Failed to download ${reportType} report. Please try again.`);
    } finally {
      setReportLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Assessment Reports
        </Typography>
        
        <Tooltip title="Refresh">
          <IconButton onClick={() => setRefreshTrigger(prev => prev + 1)}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3 }}>
        <TableContainer>
          <Table sx={{ minWidth: 650 }} aria-label="reports table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Student</TableCell>
                <TableCell>Grade</TableCell>
                <TableCell>Completion Date</TableCell>
                <TableCell>Primary Learning Style</TableCell>
                <TableCell>Payment Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((report) => (
                  <TableRow key={report.assessment_id}>
                    <TableCell>{report.assessment_id}</TableCell>
                    <TableCell>{report.student_name}</TableCell>
                    <TableCell>{report.grade}</TableCell>
                    <TableCell>{formatDate(report.completion_date)}</TableCell>
                    <TableCell>
                      <Chip 
                        label={report.primary_learning_style.charAt(0).toUpperCase() + report.primary_learning_style.slice(1)} 
                        color="primary" 
                        size="small" 
                      />
                    </TableCell>
                    <TableCell>
                      {report.payment_status === 'COMPLETED' ? (
                        <Chip label="Paid" color="success" size="small" />
                      ) : (
                        <Chip label="Free" color="default" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Results">
                        <IconButton onClick={() => navigate(`/admin/results/${report.assessment_id}`)}>
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Download Summary Report">
                        <IconButton 
                          onClick={() => handleDownloadReport(report.assessment_id, 'summary')}
                          disabled={reportLoading}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      
                      {report.payment_status === 'COMPLETED' && (
                        <Tooltip title="Download Detailed Report">
                          <IconButton 
                            onClick={() => handleDownloadReport(report.assessment_id, 'detailed')}
                            disabled={reportLoading}
                            color="secondary"
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Edit Recommendations">
                        <IconButton onClick={() => navigate(`/admin/recommendations/${report.assessment_id}`)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={reports.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Container>
  );
};

const AdminReportView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [results, setResults] = useState<any>(null);
  
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Check if user is admin
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (!user.is_admin) {
          navigate('/');
          return;
        }

        // Fetch analysis results
        const response = await axios.get(`/api/admin/analysis/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setResults(response.data);
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

    if (id) {
      fetchResults();
    }
  }, [id, navigate]);

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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Assessment Results
          </Typography>
          
          <Button 
            variant="outlined" 
            onClick={() => navigate('/admin/reports')}
          >
            Back to Reports
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          <Grid  xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Student Information
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body1" gutterBottom>
                    <strong>Name:</strong> {results.student_name}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Grade:</strong> {results.grade}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Assessment Date:</strong> {new Date(results.assessment_date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Assessment ID:</strong> {results.assessment_id}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid  xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Learning Style Profile
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body1" gutterBottom>
                    <strong>Primary Learning Style:</strong> {results.learning_styles.primary.charAt(0).toUpperCase() + results.learning_styles.primary.slice(1)}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Secondary Learning Style:</strong> {results.learning_styles.secondary.charAt(0).toUpperCase() + results.learning_styles.secondary.slice(1)}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Primary Cognitive Strength:</strong> {results.cognitive_strengths.primary.charAt(0).toUpperCase() + results.cognitive_strengths.primary.slice(1)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid  xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Learning Styles Breakdown
                </Typography>
                
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Learning Style</TableCell>
                        <TableCell>Score</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(results.learning_styles.scores).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell>{key.charAt(0).toUpperCase() + key.slice(1)}</TableCell>
                          <TableCell>{value}/10</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid  xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cognitive Strengths Breakdown
                </Typography>
                
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Cognitive Area</TableCell>
                        <TableCell>Score</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(results.cognitive_strengths.scores).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell>{key.charAt(0).toUpperCase() + key.slice(1)}</TableCell>
                          <TableCell>{value}/10</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid  xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ideal Learning Environment
                </Typography>
                
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid  xs={12} sm={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Structure:
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {results.ideal_learning_environment.structure}
                    </Typography>
                  </Grid>
                  
                  <Grid  xs={12} sm={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Social Setting:
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {results.ideal_learning_environment.social}
                    </Typography>
                  </Grid>
                  
                  <Grid  xs={12} sm={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Pace:
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {results.ideal_learning_environment.pace}
                    </Typography>
                  </Grid>
                  
                  <Grid  xs={12} sm={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Feedback:
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {results.ideal_learning_environment.feedback}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid  xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Button 
                variant="contained" 
                onClick={() => navigate(`/admin/recommendations/${id}`)}
              >
                Edit Recommendations
              </Button>
              
              <Button 
                variant="outlined" 
                onClick={() => navigate('/admin/reports')}
              >
                Back to Reports
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export { AdminReports, AdminReportView };
