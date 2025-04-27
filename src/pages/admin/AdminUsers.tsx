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
  Tooltip,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  user_type: string;
  is_active: boolean;
  is_admin: boolean;
  date_joined: string;
  grade?: string;
}

const AdminUsers: React.FC = () => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    user_type: '',
    is_active: true,
    is_admin: false,
    grade: ''
  });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  useEffect(() => {
    const fetchUsers = async () => {
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

        // Fetch users
        const response = await axios.get('/api/admin/users/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        setUsers(response.data);
      } catch (err: any) {
        if (err.response && err.response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError('Failed to load users. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [navigate, refreshTrigger]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenEditDialog = (user: User) => {
    setCurrentUser(user);
    setFormData({
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      user_type: user.user_type,
      is_active: user.is_active,
      is_admin: user.is_admin,
      grade: user.grade || ''
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentUser(null);
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

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData({
      ...formData,
      [name]: checked
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
      if (!formData.email || !formData.first_name || !formData.last_name || !formData.user_type) {
        setError('Please fill in all required fields.');
        return;
      }

      if (!currentUser) return;
      
      // Update user
      await axios.put(`/api/admin/users/${currentUser.id}/`, {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        user_type: formData.user_type,
        is_active: formData.is_active,
        is_admin: formData.is_admin,
        grade: formData.user_type === 'student' ? formData.grade : null
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Close dialog and refresh users
      handleCloseDialog();
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to update user. Please try again.');
    }
  };

  const handleOpenDeleteDialog = (userId: number) => {
    setUserToDelete(userId);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setUserToDelete(null);
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.delete(`/api/admin/users/${userToDelete}/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Close dialog and refresh users
      handleCloseDeleteDialog();
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to delete user. Please try again.');
      handleCloseDeleteDialog();
    }
  };

  const getUserTypeChip = (userType: string) => {
    switch (userType) {
      case 'student':
        return <Chip label="Student" color="primary" size="small" />;
      case 'parent':
        return <Chip label="Parent" color="secondary" size="small" />;
      case 'teacher':
        return <Chip label="Teacher" color="info" size="small" />;
      default:
        return <Chip label={userType} size="small" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
          Manage Users
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
          <Table sx={{ minWidth: 650 }} aria-label="users table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Grade</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Admin</TableCell>
                <TableCell>Joined</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{getUserTypeChip(user.user_type)}</TableCell>
                    <TableCell>{user.grade || 'N/A'}</TableCell>
                    <TableCell>
                      {user.is_active ? (
                        <Chip label="Active" color="success" size="small" />
                      ) : (
                        <Chip label="Inactive" color="error" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {user.is_admin ? (
                        <Chip label="Yes" color="warning" size="small" />
                      ) : (
                        <Chip label="No" size="small" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell>{formatDate(user.date_joined)}</TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton onClick={() => handleOpenEditDialog(user)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      
                      {user.user_type === 'student' && (
                        <Tooltip title="View Assessments">
                          <IconButton onClick={() => navigate(`/admin/users/${user.id}/assessments`)}>
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Delete">
                        <IconButton onClick={() => handleOpenDeleteDialog(user.id)}>
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
          count={users.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Edit User Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit User
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="first_name"
                label="First Name"
                fullWidth
                required
                value={formData.first_name}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                name="last_name"
                label="Last Name"
                fullWidth
                required
                value={formData.last_name}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={12}>
              <TextField
                name="email"
                label="Email"
                fullWidth
                required
                value={formData.email}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required>
                <InputLabel>User Type</InputLabel>
                <Select
                  name="user_type"
                  value={formData.user_type}
                  label="User Type"
                  onChange={handleInputChange}
                >
                  <MenuItem value="student">Student</MenuItem>
                  <MenuItem value="parent">Parent</MenuItem>
                  <MenuItem value="teacher">Teacher</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {formData.user_type === 'student' && (
              <Grid size={{ xs: 12, sm: 6 }}>
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
            )}
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  name="is_active"
                  value={formData.is_active}
                  label="Status"
                  onChange={handleInputChange}
                >
                  <MenuItem value={true}>Active</MenuItem>
                  <MenuItem value={false}>Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Admin Access</InputLabel>
                <Select
                  name="is_admin"
                  value={formData.is_admin}
                  label="Admin Access"
                  onChange={handleInputChange}
                >
                  <MenuItem value={true}>Yes</MenuItem>
                  <MenuItem value={false}>No</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Delete</DialogTitle>
        
        <DialogContent>
          <Typography>
            Are you sure you want to delete this user? This action cannot be undone and will remove all associated data including assessments and results.
          </Typography>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteUser} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminUsers;