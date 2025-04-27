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
  Stepper,
  Step,
  StepLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  TextField,
  Divider
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Question {
  id: number;
  text: string;
  category: string;
  question_type: string;
  options: {
    id: number;
    text: string;
  }[];
}

interface AssessmentData {
  id: number;
  status: string;
  student: {
    id: number;
    first_name: string;
    last_name: string;
    grade: string;
  };
  questions: Question[];
  current_question_index: number;
}

const Assessment: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [assessment, setAssessment] = useState<AssessmentData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [openResponse, setOpenResponse] = useState('');
  
  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await axios.get(`/api/assessments/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setAssessment(response.data);
        setCurrentQuestionIndex(response.data.current_question_index || 0);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load assessment. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAssessment();
  }, [id, navigate]);

  const handleOptionSelect = (optionId: number) => {
    setSelectedOption(optionId);
  };

  const handleOpenResponseChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOpenResponse(e.target.value);
  };

  const handleSubmitResponse = async () => {
    if (!assessment) return;
    
    const currentQuestion = assessment.questions[currentQuestionIndex];
    
    // Validate response
    if (currentQuestion.question_type === 'MULTIPLE_CHOICE' && selectedOption === null) {
      setError('Please select an option.');
      return;
    }
    
    if (currentQuestion.question_type === 'OPEN_ENDED' && !openResponse.trim()) {
      setError('Please provide a response.');
      return;
    }
    
    setSubmitting(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Submit response
      await axios.post('/api/responses/', {
        assessment: assessment.id,
        question: currentQuestion.id,
        selected_option: selectedOption,
        open_response: openResponse
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Clear response for next question
      setSelectedOption(null);
      setOpenResponse('');
      
      // Move to next question or complete assessment
      if (currentQuestionIndex < assessment.questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
      } else {
        // Complete assessment
        await axios.post(`/api/assessments/${assessment.id}/complete/`, {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // Navigate to results page
        navigate(`/results/${assessment.id}`);
      }
    } catch (err) {
      setError('Failed to submit response. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!assessment) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Assessment not found or could not be loaded.
        </Alert>
      </Container>
    );
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];
  const progress = Math.round(((currentQuestionIndex + 1) / assessment.questions.length) * 100);

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Learning Style Assessment
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Student: {assessment.student.first_name} {assessment.student.last_name}
          </Typography>
          <Typography variant="body1" gutterBottom>
            Grade: {assessment.student.grade}
          </Typography>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Progress: {progress}% ({currentQuestionIndex + 1} of {assessment.questions.length})
          </Typography>
          <Box sx={{ width: '100%', bgcolor: '#e0e0e0', borderRadius: 1, height: 8, mb: 2 }}>
            <Box
              sx={{
                width: `${progress}%`,
                bgcolor: 'primary.main',
                borderRadius: 1,
                height: 8,
                transition: 'width 0.3s ease-in-out',
              }}
            />
          </Box>
        </Box>
        
        <Stepper activeStep={currentQuestionIndex} alternativeLabel sx={{ mb: 4 }}>
          {assessment.questions.map((_, index) => (
            <Step key={index}>
              <StepLabel></StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Category: {currentQuestion.category}
            </Typography>
            
            <Typography variant="h6" component="div" gutterBottom>
              {currentQuestion.text}
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            {currentQuestion.question_type === 'MULTIPLE_CHOICE' ? (
              <FormControl component="fieldset">
                <FormLabel component="legend">Select one option:</FormLabel>
                <RadioGroup value={selectedOption || ''} onChange={(e) => handleOptionSelect(Number(e.target.value))}>
                  {currentQuestion.options.map(option => (
                    <FormControlLabel
                      key={option.id}
                      value={option.id}
                      control={<Radio />}
                      label={option.text}
                    />
                  ))}
                </RadioGroup>
              </FormControl>
            ) : (
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your response"
                variant="outlined"
                value={openResponse}
                onChange={handleOpenResponseChange}
              />
            )}
          </CardContent>
        </Card>
        
        <Grid container spacing={2} justifyContent="space-between">
          <Grid >
            <Button
              variant="outlined"
              disabled={currentQuestionIndex === 0 || submitting}
              onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
            >
              Previous
            </Button>
          </Grid>
          <Grid >
            <Button
              variant="contained"
              onClick={handleSubmitResponse}
              disabled={submitting}
            >
              {submitting ? (
                <CircularProgress size={24} />
              ) : currentQuestionIndex < assessment.questions.length - 1 ? (
                'Next'
              ) : (
                'Complete Assessment'
              )}
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default Assessment;
