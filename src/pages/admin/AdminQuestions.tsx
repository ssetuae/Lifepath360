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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';

interface Question {
  id: number;
  text: string;
  category: string;
  question_type: string;
  grade: string;
  options: {
    id: number;
    text: string;
  }[];
}

const AdminQuestions: React.FC = () => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit'>('add');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [formData, setFormData] = useState({
    text: '',
    category: '',
    question_type: '',
    grade: '',
    options: [{ text: '' }, { text: '' }, { text: '' }, { text: '' }]
  });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [questionToDelete, setQuestionToDelete] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  useEffect(() => {
    const fetchQuestions = async () => {
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

        // Fetch questions
        const response = await axios.get('/api/questions/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setQuestions(response.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load questions. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [navigate, refreshTrigger]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenAddDialog = () => {
    setDialogMode('add');
    setFormData({
      text: '',
      category: '',
      question_type: '',
      grade: '',
      options: [{ text: '' }, { text: '' }, { text: '' }, { text: '' }]
    });
    setOpenDialog(true);
  };

  const handleOpenEditDialog = (question: Question) => {
    setDialogMode('edit');
    setCurrentQuestion(question);
    
    // Prepare options array with at least 4 items
    const options = [...question.options];
    while (options.length < 4) {
      options.push({ id: -1 * options.length, text: '' });
    }
    
    setFormData({
      text: question.text,
      category: question.category,
      question_type: question.question_type,
      grade: question.grade,
      options: options.map(option => ({ text: option.text }))
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentQuestion(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    if (name) {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...formData.options];
    newOptions[index] = { text: value };
    setFormData({
      ...formData,
      options: newOptions
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
      if (!formData.text || !formData.category || !formData.question_type || !formData.grade) {
        setError('Please fill in all required fields.');
        return;
      }

      if (formData.question_type === 'MULTIPLE_CHOICE') {
        // Check if at least 2 options are provided
        const validOptions = formData.options.filter(option => option.text.trim() !== '');
        if (validOptions.length < 2) {
          setError('Please provide at least 2 options for multiple choice questions.');
          return;
        }
      }

      // Filter out empty options
      const filteredOptions = formData.options.filter(option => option.text.trim() !== '');

      if (dialogMode === 'add') {
        // Create new question
        await axios.post('/api/questions/', {
          text: formData.text,
          category: formData.category,
          question_type: formData.question_type,
          grade: formData.grade,
          options: filteredOptions
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      } else {
        // Update existing question
        if (!currentQuestion) return;
        
        await axios.put(`/api/questions/${currentQuestion.id}/`, {
          text: formData.text,
          category: formData.category,
          question_type: formData.question_type,
          grade: formData.grade,
          options: filteredOptions
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      }

      // Close dialog and refresh questions
      handleCloseDialog();
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to save question. Please try again.');
    }
  };

  const handleOpenDeleteDialog = (questionId: number) => {
    setQuestionToDelete(questionId);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setQuestionToDelete(null);
  };

  const handleDeleteQuestion = async () => {
    if (!questionToDelete) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.delete(`/api/questions/${questionToDelete}/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Close dialog and refresh questions
      handleCloseDeleteDialog();
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to delete question. Please try again.');
      handleCloseDeleteDialog();
    }
  };

  const handleGenerateAIQuestions = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.post('/api/ai/generate_questions/', {
        count: 5,  // Generate 5 questions
        grade: 'G6',  // For Grade 6
        categories: ['visual', 'auditory', 'kinesthetic', 'logical', 'social']
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Refresh questions
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to generate AI questions. Please try again.');
    } finally {
      setLoading(false);
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
          Manage Questions
        </Typography>
        
        <Box>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleOpenAddDialog}
            sx={{ mr: 2 }}
          >
            Add Question
          </Button>
          
          <Button 
            variant="outlined" 
            onClick={handleGenerateAIQuestions}
          >
            Generate AI Questions
          </Button>
        </Box>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Question List
          </Typography>
          
          <Tooltip title="Refresh">
            <IconButton onClick={() => setRefreshTrigger(prev => prev + 1)}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <TableContainer>
          <Table sx={{ minWidth: 650 }} aria-label="questions table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Question</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Grade</TableCell>
                <TableCell>Options</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {questions
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((question) => (
                  <TableRow key={question.id}>
                    <TableCell>{question.id}</TableCell>
                    <TableCell>{question.text}</TableCell>
                    <TableCell>{question.category}</TableCell>
                    <TableCell>{question.question_type}</TableCell>
                    <TableCell>{question.grade}</TableCell>
                    <TableCell>
                      {question.question_type === 'MULTIPLE_CHOICE' ? question.options.length : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton onClick={() => handleOpenEditDialog(question)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Delete">
                        <IconButton onClick={() => handleOpenDeleteDialog(question.id)}>
                          <DeleteIcon />
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
          count={questions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Add/Edit Question Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Question' : 'Edit Question'}
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid  xs={12}>
              <TextField
                name="text"
                label="Question Text"
                fullWidth
                required
                value={formData.text}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid  xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Category</InputLabel>
                <Select
                  name="category"
                  value={formData.category}
                  label="Category"
                  onChange={handleInputChange}
                >
                  <MenuItem value="visual">Visual</MenuItem>
                  <MenuItem value="auditory">Auditory</MenuItem>
                  <MenuItem value="kinesthetic">Kinesthetic</MenuItem>
                  <MenuItem value="logical">Logical</MenuItem>
                  <MenuItem value="social">Social</MenuItem>
                  <MenuItem value="solitary">Solitary</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid  xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Question Type</InputLabel>
                <Select
                  name="question_type"
                  value={formData.question_type}
                  label="Question Type"
                  onChange={handleInputChange}
                >
                  <MenuItem value="MULTIPLE_CHOICE">Multiple Choice</MenuItem>
                  <MenuItem value="OPEN_ENDED">Open Ended</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid  xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Grade</InputLabel>
                <Select
                  name="grade"
                  value={formData.grade}
                  label="Grade"
                  onChange={handleInputChange}
                >
                  <MenuItem value="K">Kindergarten</MenuItem>
                  <MenuItem value="G1">Grade 1</MenuItem>
                  <MenuItem value="G2">Grade 2</MenuItem>
                  <MenuItem value="G3">Grade 3</MenuItem>
                  <MenuItem value="G4">Grade 4</MenuItem>
                  <MenuItem value="G5">Grade 5</MenuItem>
                  <MenuItem value="G6">Grade 6</MenuItem>
                  <MenuItem value="G7">Grade 7</MenuItem>
                  <MenuItem value="G8">Grade 8</MenuItem>
                  <MenuItem value="G9">Grade 9</MenuItem>
                  <MenuItem value="G10">Grade 10</MenuItem>
                  <MenuItem value="G11">Grade 11</MenuItem>
                  <MenuItem value="G12">Grade 12</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {formData.question_type === 'MULTIPLE_CHOICE' && (
              <Grid  xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Options
                </Typography>
                
                {formData.options.map((option, index) => (
                  <TextField
                    key={index}
                    label={`Option ${index + 1}`}
                    fullWidth
                    value={option.text}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    sx={{ mb: 2 }}
                    required={index < 2}
                  />
                ))}
              </Grid>
            )}
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {dialogMode === 'add' ? 'Add Question' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Delete</DialogTitle>
        
        <DialogContent>
          <Typography>
            Are you sure you want to delete this question? This action cannot be undone.
          </Typography>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteQuestion} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminQuestions;
