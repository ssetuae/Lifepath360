import React from 'react';
import { Navigate } from 'react-router-dom';

interface AdminRouteProps {
  children: React.ReactElement; // 
}

const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  const userData = user ? JSON.parse(user) : null;
  const isAdmin = userData?.is_admin;

  if (!token || !isAdmin) {
    return <Navigate to="/login" replace />;
  }

  return children; // 
};

export default AdminRoute;
