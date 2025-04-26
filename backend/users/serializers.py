from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Student, Parent, Teacher

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'role', 'is_profile_complete')
        read_only_fields = ('id', 'is_profile_complete')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Student model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Student
        fields = ('id', 'user', 'user_email', 'first_name', 'last_name', 'grade', 'age', 'school', 'parent')
        read_only_fields = ('id', 'user_email')


class ParentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Parent model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    children = StudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Parent
        fields = ('id', 'user', 'user_email', 'first_name', 'last_name', 'phone', 'children')
        read_only_fields = ('id', 'user_email', 'children')


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Teacher model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ('id', 'user', 'user_email', 'first_name', 'last_name', 'subject_specialty')
        read_only_fields = ('id', 'user_email')


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration with profile creation.
    """
    # User fields
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)
    
    # Profile fields - conditionally required based on role
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    # Student specific fields
    grade = serializers.ChoiceField(choices=Student.Grade.choices, required=False)
    age = serializers.IntegerField(required=False)
    school = serializers.CharField(required=False)
    
    # Parent specific fields
    phone = serializers.CharField(required=False)
    
    # Teacher specific fields
    subject_specialty = serializers.CharField(required=False)
    
    def validate(self, data):
        """
        Validate that required fields for specific roles are provided.
        """
        role = data.get('role')
        
        # Common profile fields required for all roles except ADMIN
        if role != User.Role.ADMIN:
            if not data.get('first_name'):
                raise serializers.ValidationError({"first_name": "First name is required."})
            if not data.get('last_name'):
                raise serializers.ValidationError({"last_name": "Last name is required."})
        
        # Role-specific validation
        if role == User.Role.STUDENT:
            if not data.get('grade'):
                raise serializers.ValidationError({"grade": "Grade is required for students."})
            if not data.get('age'):
                raise serializers.ValidationError({"age": "Age is required for students."})
            if not data.get('school'):
                raise serializers.ValidationError({"school": "School is required for students."})
        
        elif role == User.Role.PARENT:
            if not data.get('phone'):
                raise serializers.ValidationError({"phone": "Phone number is required for parents."})
        
        elif role == User.Role.TEACHER:
            if not data.get('subject_specialty'):
                raise serializers.ValidationError({"subject_specialty": "Subject specialty is required for teachers."})
        
        return data
    
    def create(self, validated_data):
        """
        Create a new user with the appropriate profile based on role.
        """
        role = validated_data.get('role')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=role
        )
        
        # Create profile based on role
        if role == User.Role.STUDENT:
            Student.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                grade=validated_data['grade'],
                age=validated_data['age'],
                school=validated_data['school']
            )
        
        elif role == User.Role.PARENT:
            Parent.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                phone=validated_data['phone']
            )
        
        elif role == User.Role.TEACHER:
            Teacher.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                subject_specialty=validated_data['subject_specialty']
            )
        
        # Mark profile as complete
        user.is_profile_complete = True
        user.save()
        
        return user
