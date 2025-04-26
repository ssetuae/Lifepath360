from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model for Learning Compass application.
    Extends Django's AbstractUser to add role-based authentication.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        TEACHER = 'TEACHER', _('Teacher')
        PARENT = 'PARENT', _('Parent')
        STUDENT = 'STUDENT', _('Student')
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    
    # Fields to track user profile completion
    is_profile_complete = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class Student(models.Model):
    """
    Student profile model with grade-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    class Grade(models.TextChoices):
        K = 'K', _('Kindergarten')
        G1 = 'G1', _('Grade 1')
        G2 = 'G2', _('Grade 2')
        G3 = 'G3', _('Grade 3')
        G4 = 'G4', _('Grade 4')
        G5 = 'G5', _('Grade 5')
        G6 = 'G6', _('Grade 6')
        G7 = 'G7', _('Grade 7')
        G8 = 'G8', _('Grade 8')
        G9 = 'G9', _('Grade 9')
        G10 = 'G10', _('Grade 10')
        G11 = 'G11', _('Grade 11')
        G12 = 'G12', _('Grade 12')
    
    grade = models.CharField(
        max_length=3,
        choices=Grade.choices,
        default=Grade.K,
    )
    
    age = models.PositiveIntegerField()
    school = models.CharField(max_length=200)
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, related_name='children')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_grade_display()}"


class Parent(models.Model):
    """
    Parent profile model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(models.Model):
    """
    Teacher profile model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subject_specialty = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject_specialty}"
