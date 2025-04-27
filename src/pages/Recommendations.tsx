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
  CardMedia,
  CardActionArea,
  Divider,
  Alert,
  Chip,
  Rating
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import WorkIcon from '@mui/icons-material/Work';
import PublicIcon from '@mui/icons-material/Public';
import StarIcon from '@mui/icons-material/Star';

const Recommendations = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('courses');

  useEffect(() => {
    // Fetch recommendations data
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        // In a real implementation, this would be an API call
        // const response = await fetch(`/api/recommendations/${id}`);
        // const data = await response.json();
        
        // Mock data for development
        const mockRecommendations = {
          id: id,
          assessment_id: id,
          learning_style: {
            visual: 75,
            auditory: 45,
            kinesthetic: 60,
            logical: 80,
            social: 65,
            solitary: 70
          },
          courses: [
            {
              id: 1,
              title: "Advanced Mathematics for Visual Learners",
              description: "This course uses visual aids and graphical representations to teach advanced mathematical concepts.",
              match_percentage: 95,
              image_url: "https://source.unsplash.com/random/300x200/?math",
              provider: "Shining Star Education",
              duration: "12 weeks",
              level: "Intermediate"
            },
            {
              id: 2,
              title: "Critical Thinking and Problem Solving",
              description: "Develop logical reasoning and analytical skills through interactive problem-solving exercises.",
              match_percentage: 90,
              image_url: "https://source.unsplash.com/random/300x200/?thinking",
              provider: "Shining Star Education",
              duration: "8 weeks",
              level: "Advanced"
            },
            {
              id: 3,
              title: "Self-Paced Science Exploration",
              description: "A solitary learning experience focused on scientific discovery and experimentation.",
              match_percentage: 85,
              image_url: "https://source.unsplash.com/random/300x200/?science",
              provider: "Smartyca Learning",
              duration: "10 weeks",
              level: "Beginner"
            }
          ],
          career_paths: [
            {
              id: 1,
              title: "Data Scientist",
              description: "Analyze complex data and create visual representations to communicate insights.",
              match_percentage: 92,
              skills_required: ["Mathematics", "Statistics", "Programming", "Data Visualization"]
            },
            {
              id: 2,
              title: "Research Analyst",
              description: "Conduct in-depth research and analysis to solve complex problems.",
              match_percentage: 88,
              skills_required: ["Critical Thinking", "Research Methods", "Data Analysis", "Report Writing"]
            },
            {
              id: 3,
              title: "Software Engineer",
              description: "Design and develop software solutions through logical problem-solving.",
              match_percentage: 85,
              skills_required: ["Programming", "Algorithm Design", "System Architecture", "Testing"]
            }
          ],
          global_exams: [
            {
              id: 1,
              title: "International Mathematics Olympiad",
              description: "A global competition testing mathematical problem-solving skills.",
              match_percentage: 90,
              preparation_time: "6-12 months"
            },
            {
              id: 2,
              title: "Advanced Placement (AP) Computer Science",
              description: "College-level examination in computer science principles and programming.",
              match_percentage: 88,
              preparation_time: "9 months"
            },
            {
              id: 3,
              title: "International Science and Engineering Fair",
              description: "A competition for original scientific research projects.",
              match_percentage: 85,
              preparation_time: "3-6 months"
            }
          ]
        };
        
        setTimeout(() => {
          setRecommendations(mockRecommendations);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load recommendations. Please try again later.');
        setLoading(false);
      }
    };

    if (id) {
      fetchRecommendations();
    } else {
      setError('Assessment ID is missing');
      setLoading(false);
    }
  }, [id]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
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
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Personalized Recommendations
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Based on Your Learning Style Profile
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {Object.entries(recommendations.learning_style).map(([style, score]) => (
            <Grid key={style} size={{ xs: 6, sm: 4, md: 2 }}>
              <Paper 
                elevation={3} 
                sx={{ 
                  p: 2, 
                  textAlign: 'center',
                  background: score > 70 ? 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)' : 'white',
                  color: score > 70 ? 'white' : 'inherit'
                }}
              >
                <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                  {style}
                </Typography>
                <Typography variant="h6">
                  {score}%
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
        
        <Divider sx={{ my: 3 }} />
        
        {/* Navigation Tabs */}
        <Box sx={{ display: 'flex', mb: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Button 
            variant={activeTab === 'courses' ? 'contained' : 'text'} 
            onClick={() => handleTabChange('courses')}
            startIcon={<SchoolIcon />}
            sx={{ mr: 1 }}
          >
            Courses
          </Button>
          <Button 
            variant={activeTab === 'careers' ? 'contained' : 'text'} 
            onClick={() => handleTabChange('careers')}
            startIcon={<WorkIcon />}
            sx={{ mr: 1 }}
          >
            Career Paths
          </Button>
          <Button 
            variant={activeTab === 'exams' ? 'contained' : 'text'} 
            onClick={() => handleTabChange('exams')}
            startIcon={<PublicIcon />}
          >
            Global Exams
          </Button>
        </Box>
        
        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <Grid container spacing={3}>
            {recommendations.courses.map((course) => (
              <Grid key={course.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardActionArea>
                    <CardMedia
                      component="img"
                      height="140"
                      image={course.image_url}
                      alt={course.title}
                    />
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6" component="div" noWrap>
                          {course.title}
                        </Typography>
                        <Chip 
                          label={`${course.match_percentage}% Match`} 
                          color="primary" 
                          size="small" 
                          sx={{ fontWeight: 'bold' }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {course.description}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 'auto' }}>
                        <Typography variant="body2" color="text.secondary">
                          Duration: {course.duration}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Level: {course.level}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.primary" sx={{ mt: 1 }}>
                        Provider: {course.provider}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        
        {/* Career Paths Tab */}
        {activeTab === 'careers' && (
          <Grid container spacing={3}>
            {recommendations.career_paths.map((career) => (
              <Grid key={career.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" component="div">
                        {career.title}
                      </Typography>
                      <Chip 
                        label={`${career.match_percentage}% Match`} 
                        color="primary" 
                        size="small" 
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {career.description}
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Key Skills:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {career.skills_required.map((skill, index) => (
                        <Chip key={index} label={skill} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        
        {/* Global Exams Tab */}
        {activeTab === 'exams' && (
          <Grid container spacing={3}>
            {recommendations.global_exams.map((exam) => (
              <Grid key={exam.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" component="div">
                        {exam.title}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Rating
                          value={exam.match_percentage / 20}
                          readOnly
                          precision={0.5}
                          emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                          size="small"
                        />
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {exam.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Match: {exam.match_percentage}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Prep Time: {exam.preparation_time}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2, mb: 4 }}>
        <Button 
          variant="outlined" 
          onClick={() => navigate('/dashboard')}
          sx={{ mr: 2 }}
        >
          Back to Dashboard
        </Button>
        <Button 
          variant="contained" 
          onClick={() => navigate(`/reports/${id}`)}
        >
          View Full Report
        </Button>
      </Box>
    </Container>
  );
};

export default Recommendations;