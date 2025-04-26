from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from .security_models import AccessLog
from django.utils import timezone

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require admin access for a view.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin
    
    def handle_no_permission(self):
        # Log unauthorized access attempt
        if self.request.user.is_authenticated:
            AccessLog.objects.create(
                user=self.request.user,
                action='admin_access_attempt',
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT'),
                status='denied',
                details=f"Attempted to access admin view: {self.request.path}"
            )
        
        raise PermissionDenied("You do not have permission to access this page.")


class TeacherRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require teacher or admin access for a view.
    """
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.user_type == 'teacher'
        )
    
    def handle_no_permission(self):
        # Log unauthorized access attempt
        if self.request.user.is_authenticated:
            AccessLog.objects.create(
                user=self.request.user,
                action='teacher_access_attempt',
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT'),
                status='denied',
                details=f"Attempted to access teacher view: {self.request.path}"
            )
        
        raise PermissionDenied("You do not have permission to access this page.")


class IsAdminUser(BasePermission):
    """
    Permission class for DRF to require admin access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.is_admin:
            # Log unauthorized access attempt
            AccessLog.objects.create(
                user=request.user,
                action='admin_api_access_attempt',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                status='denied',
                details=f"Attempted to access admin API: {request.path}"
            )
            return False
        
        # Log successful access
        AccessLog.objects.create(
            user=request.user,
            action='admin_api_access',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            status='success',
            details=f"Accessed admin API: {request.path}"
        )
        
        return True


class IsTeacherUser(BasePermission):
    """
    Permission class for DRF to require teacher or admin access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not (request.user.is_admin or request.user.user_type == 'teacher'):
            # Log unauthorized access attempt
            AccessLog.objects.create(
                user=request.user,
                action='teacher_api_access_attempt',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                status='denied',
                details=f"Attempted to access teacher API: {request.path}"
            )
            return False
        
        # Log successful access
        AccessLog.objects.create(
            user=request.user,
            action='teacher_api_access',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            status='success',
            details=f"Accessed teacher API: {request.path}"
        )
        
        return True


class HasStudentAccess(BasePermission):
    """
    Permission class for DRF to check if user has access to student data.
    """
    def has_object_permission(self, request, view, obj):
        # Admin and teachers have access to all students
        if request.user.is_admin or request.user.user_type == 'teacher':
            return True
        
        # Get student ID from object
        student_id = getattr(obj, 'student_id', None)
        if not student_id:
            student = getattr(obj, 'student', None)
            student_id = getattr(student, 'id', None) if student else None
        
        if not student_id:
            return False
        
        # Students can only access their own data
        if request.user.user_type == 'student' and hasattr(request.user, 'student'):
            if request.user.student.id == student_id:
                return True
        
        # Parents can only access their children's data
        if request.user.user_type == 'parent' and hasattr(request.user, 'parent'):
            children = request.user.parent.children.all()
            if children.filter(id=student_id).exists():
                return True
        
        # Log unauthorized access attempt
        AccessLog.objects.create(
            user=request.user,
            action='student_data_access_attempt',
            resource_type='student',
            resource_id=str(student_id),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            status='denied',
            details=f"Attempted to access student data: {student_id}"
        )
        
        return False


class HasSensitiveDataAccess(BasePermission):
    """
    Permission class for DRF to check if user has access to sensitive student data.
    """
    def has_permission(self, request, view):
        # Only admin and teachers can access sensitive data
        if not request.user.is_authenticated:
            return False
        
        if not (request.user.is_admin or request.user.user_type == 'teacher'):
            # Log unauthorized access attempt
            AccessLog.objects.create(
                user=request.user,
                action='sensitive_data_access_attempt',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                status='denied',
                details=f"Attempted to access sensitive data API: {request.path}"
            )
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Record access to sensitive data
        if hasattr(obj, 'record_access'):
            obj.record_access(request.user)
        
        return True


def log_user_activity(user, action, resource_type=None, resource_id=None, details=None, request=None, status='success'):
    """
    Helper function to log user activity for audit purposes.
    """
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
    
    AccessLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        timestamp=timezone.now()
    )
