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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import PeopleIcon from '@mui/icons-material/People';
import AssessmentIcon from '@mui/icons-material/Assessment';
import QuizIcon from '@mui/icons-material/Quiz';
import SchoolIcon from '@mui/icons-material/School';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [recentAssessments, setRecentAssessments] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
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

        // Fetch dashboard stats
        const statsResponse = await axios.get('/api/admin/stats/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setStats(statsResponse.data);

        // Fetch recent assessments
        const assessmentsResponse = await axios.get('/api/admin/assessments/recent/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setRecentAssessments(assessmentsResponse.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load dashboard data. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <PeopleIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h5" component="div">
                {stats?.total_users || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h5" component="div">
                {stats?.total_assessments || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Assessments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <QuizIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h5" component="div">
                {stats?.total_questions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Questions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <SchoolIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h5" component="div">
                {stats?.completed_assessments || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed Assessments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item>
            <Button 
              variant="contained" 
              onClick={() => navigate('/admin/questions')}
            >
              Manage Questions
            </Button>
          </Grid>
          
          <Grid item>
            <Button 
              variant="contained" 
              onClick={() => navigate('/admin/users')}
            >
              Manage Users
            </Button>
          </Grid>
          
          <Grid item>
            <Button 
              variant="contained" 
              onClick={() => navigate('/admin/reports')}
            >
              View Reports
            </Button>
          </Grid>
          
          <Grid item>
            <Button 
              variant="contained" 
              onClick={() => navigate('/admin/courses')}
            >
              Manage Courses
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Recent Assessments */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Assessments
        </Typography>
        
        <TableContainer>
          <Table sx={{ minWidth: 650 }} aria-label="recent assessments table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Student</TableCell>
                <TableCell>Grade</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Start Time</TableCell>
                <TableCell>End Time</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentAssessments
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((assessment) => (
                  <TableRow key={assessment.id}>
                    <TableCell>{assessment.id}</TableCell>
                    <TableCell>{`${assessment.student.first_name} ${assessment.student.last_name}`}</TableCell>
                    <TableCell>{assessment.student.grade}</TableCell>
                    <TableCell>{getStatusChip(assessment.status)}</TableCell>
                    <TableCell>{formatDate(assessment.start_time)}</TableCell>
                    <TableCell>{assessment.end_time ? formatDate(assessment.end_time) : 'N/A'}</TableCell>
                    <TableCell>
                      {assessment.status === 'COMPLETED' ? (
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={() => navigate(`/admin/reports/${assessment.id}`)}
                        >
                          View Report
                        </Button>
                      ) : (
                        <Button 
                          size="small" 
                          variant="outlined"
                          disabled
                        >
                          Pending
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={recentAssessments.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Container>
  );
};

export default AdminDashboard;
