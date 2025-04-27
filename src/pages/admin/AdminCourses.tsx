import React, { useState, useEffect } from 'react';
import { 
import { SelectChangeEvent } from '@mui/material/Select';
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
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import RefreshIcon from '@mui/icons-material/Refresh';

const AdminCourses: React.FC = () => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [courses, setCourses] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentCourse, setCurrentCourse] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    grade_level: '',
    learning_style: '',
    duration: '',
    price: ''
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  useEffect(() => {
    const fetchCourses = async () => {
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

        // Fetch courses
        const response = await axios.get('/api/admin/courses/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setCourses(response.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load courses. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [navigate, refreshTrigger]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenAddDialog = () => {
    setCurrentCourse(null);
    setFormData({
      title: '',
      description: '',
      category: '',
      grade_level: '',
      learning_style: '',
      duration: '',
      price: ''
    });
    setOpenDialog(true);
  };

  const handleOpenEditDialog = (course: any) => {
    setCurrentCourse(course);
    setFormData({
      title: course.title,
      description: course.description,
      category: course.category,
      grade_level: course.grade_level,
      learning_style: course.learning_style,
      duration: course.duration,
      price: course.price.toString()
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Validate form
      if (!formData.title || !formData.description || !formData.category || 
          !formData.grade_level || !formData.learning_style || !formData.duration) {
        setError('Please fill in all required fields.');
        return;
      }

      const courseData = {
        title: formData.title,
        description: formData.description,
        category: formData.category,
        grade_level: formData.grade_level,
        learning_style: formData.learning_style,
        duration: formData.duration,
        price: parseFloat(formData.price) || 0
      };

      if (currentCourse) {
        // Update existing course
        await axios.put(`/api/admin/courses/${currentCourse.id}/`, courseData, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      } else {
        // Create new course
        await axios.post('/api/admin/courses/', courseData, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      }

      // Close dialog and refresh courses
      handleCloseDialog();
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to save course. Please try again.');
    }
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
          Manage Courses
        </Typography>
        
        <Box>
          <Button 
            variant="contained" 
            onClick={handleOpenAddDialog}
            sx={{ mr: 2 }}
          >
            Add Course
          </Button>
          
          <Tooltip title="Refresh">
            <IconButton onClick={() => setRefreshTrigger(prev => prev + 1)}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3 }}>
        <TableContainer>
          <Table sx={{ minWidth: 650 }} aria-label="courses table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Grade Level</TableCell>
                <TableCell>Learning Style</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {courses
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((course) => (
                  <TableRow key={course.id}>
                    <TableCell>{course.id}</TableCell>
                    <TableCell>{course.title}</TableCell>
                    <TableCell>{course.category}</TableCell>
                    <TableCell>{course.grade_level}</TableCell>
                    <TableCell>{course.learning_style}</TableCell>
                    <TableCell>{course.duration}</TableCell>
                    <TableCell>{course.price} AED</TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton onClick={() => handleOpenEditDialog(course)}>
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
          count={courses.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Add/Edit Course Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {currentCourse ? 'Edit Course' : 'Add New Course'}
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={12}>
              <TextField
                name="title"
                label="Course Title"
                fullWidth
                required
                value={formData.title}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={12}>
              <TextField
                name="description"
                label="Description"
                fullWidth
                required
                multiline
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="category"
                label="Category"
                fullWidth
                required
                value={formData.category}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="grade_level"
                label="Grade Level"
                fullWidth
                required
                value={formData.grade_level}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="learning_style"
                label="Learning Style"
                fullWidth
                required
                value={formData.learning_style}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="duration"
                label="Duration"
                fullWidth
                required
                value={formData.duration}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="price"
                label="Price (AED)"
                fullWidth
                required
                type="number"
                value={formData.price}
                onChange={handleInputChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {currentCourse ? 'Save Changes' : 'Add Course'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

const AdminRecommendations: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [recommendations, setRecommendations] = useState<any>(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    courses: [] as string[],
    learning_path: '',
    career_affinities: '',
    college_recommendations: '',
    global_exams: ''
  });
  
  useEffect(() => {
    const fetchRecommendations = async () => {
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

        // Fetch recommendations
        const response = await axios.get(`/api/recommendations/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setRecommendations(response.data);
        setFormData({
          courses: response.data.recommended_courses.map((course: any) => course.id.toString()),
          learning_path: response.data.learning_path,
          career_affinities: response.data.career_affinities,
          college_recommendations: response.data.college_recommendations,
          global_exams: response.data.global_exams
        });
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load recommendations. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchRecommendations();
    }
  }, [id, navigate]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSaveRecommendations = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Update recommendations
      await axios.put(`/api/admin/recommendations/${id}/`, {
        learning_path: formData.learning_path,
        career_affinities: formData.career_affinities,
        college_recommendations: formData.college_recommendations,
        global_exams: formData.global_exams
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setSuccess('Recommendations updated successfully.');
      setEditMode(false);
    } catch (err) {
      setError('Failed to update recommendations. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!recommendations) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Recommendations not found or could not be loaded.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Edit Recommendations
          </Typography>
          
          <Box>
            {editMode ? (
              <Button 
                variant="contained" 
                startIcon={<SaveIcon />}
                onClick={handleSaveRecommendations}
                disabled={saving}
                sx={{ mr: 2 }}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            ) : (
              <Button 
                variant="contained" 
                startIcon={<EditIcon />}
                onClick={() => setEditMode(true)}
                sx={{ mr: 2 }}
              >
                Edit Recommendations
              </Button>
            )}
            
            <Button 
              variant="outlined" 
              onClick={() => navigate('/admin/reports')}
            >
              Back to Reports
            </Button>
          </Box>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {success}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Student Information
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body1" gutterBottom>
                    <strong>Name:</strong> {recommendations.student_name}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Grade:</strong> {recommendations.grade}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <strong>Primary Learning Style:</strong> {recommendations.primary_learning_style}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommended Courses
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  {recommendations.recommended_courses.map((course: any) => (
                    <Typography key={course.id} variant="body1" gutterBottom>
                      • {course.title} ({course.category})
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid size={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Learning Path
                </Typography>
                
                {editMode ? (
                  <TextField
                    name="learning_path"
                    fullWidth
                    multiline
                    rows={6}
                    value={formData.learning_path}
                    onChange={handleInputChange}
                    sx={{ mt: 2 }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
                    {recommendations.learning_path}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Career Affinities
                </Typography>
                
                {editMode ? (
                  <TextField
                    name="career_affinities"
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.career_affinities}
                    onChange={handleInputChange}
                    sx={{ mt: 2 }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
                    {recommendations.career_affinities}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  College Recommendations
                </Typography>
                
                {editMode ? (
                  <TextField
                    name="college_recommendations"
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.college_recommendations}
                    onChange={handleInputChange}
                    sx={{ mt: 2 }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
                    {recommendations.college_recommendations}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid size={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Global Examination Recommendations
                </Typography>
                
                {editMode ? (
                  <TextField
                    name="global_exams"
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.global_exams}
                    onChange={handleInputChange}
                    sx={{ mt: 2 }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-line' }}>
                    {recommendations.global_exams}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export { AdminCourses, AdminRecommendations };