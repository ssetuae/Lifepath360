from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Student, Parent, Teacher
from .serializers import (
    UserSerializer, 
    StudentSerializer, 
    ParentSerializer, 
    TeacherSerializer,
    RegisterSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration with profile creation.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Custom permissions based on action.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for student profile management.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        """
        user = self.request.user
        
        if user.is_admin or user.is_teacher:
            return Student.objects.all()
        elif user.is_parent:
            try:
                parent = Parent.objects.get(user=user)
                return Student.objects.filter(parent=parent)
            except Parent.DoesNotExist:
                return Student.objects.none()
        elif user.is_student:
            try:
                student = Student.objects.get(user=user)
                return Student.objects.filter(id=student.id)
            except Student.DoesNotExist:
                return Student.objects.none()
        return Student.objects.none()


class ParentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for parent profile management.
    """
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        """
        user = self.request.user
        
        if user.is_admin or user.is_teacher:
            return Parent.objects.all()
        elif user.is_parent:
            return Parent.objects.filter(user=user)
        return Parent.objects.none()
    
    @action(detail=True, methods=['post'])
    def add_child(self, request, pk=None):
        """
        Add a child to a parent.
        """
        parent = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = Student.objects.get(id=student_id)
            student.parent = parent
            student.save()
            return Response({'message': 'Child added successfully'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


class TeacherViewSet(viewsets.ModelViewSet):
    """
    API endpoint for teacher profile management.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        """
        user = self.request.user
        
        if user.is_admin:
            return Teacher.objects.all()
        elif user.is_teacher:
            return Teacher.objects.filter(user=user)
        return Teacher.objects.none()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view to include user data in response.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from credentials
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                # Add user data to response
                response.data['user'] = UserSerializer(user).data
            except User.DoesNotExist:
                pass
                
        return response
