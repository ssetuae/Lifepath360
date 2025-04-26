from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import (
    Question, 
    QuestionOption, 
    Assessment, 
    Response, 
    QuestionnaireTemplate,
    TemplateQuestion
)
from .serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
    QuestionOptionSerializer,
    AssessmentSerializer,
    AssessmentCreateSerializer,
    ResponseSerializer,
    ResponseCreateSerializer,
    QuestionnaireTemplateSerializer,
    QuestionnaireTemplateCreateSerializer
)
from users.models import Student

class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing diagnostic questions.
    """
    queryset = Question.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateSerializer
        return QuestionSerializer
    
    def get_queryset(self):
        """
        Optionally filter questions by grade level, category, or type.
        """
        queryset = Question.objects.all()
        
        # Filter by grade level
        grade_level = self.request.query_params.get('grade_level')
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by question type
        question_type = self.request.query_params.get('question_type')
        if question_type:
            queryset = queryset.filter(question_type=question_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_grade(self, request):
        """
        Get questions grouped by grade level.
        """
        grade_levels = Student.Grade.values
        result = {}
        
        for grade in grade_levels:
            questions = Question.objects.filter(grade_level=grade, is_active=True)
            result[grade] = QuestionSerializer(questions, many=True).data
        
        return Response(result)


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student assessments.
    """
    queryset = Assessment.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AssessmentCreateSerializer
        return AssessmentSerializer
    
    def get_queryset(self):
        """
        Filter assessments based on user role.
        """
        user = self.request.user
        
        if user.is_admin or user.is_teacher:
            return Assessment.objects.all()
        elif user.is_parent:
            try:
                parent = user.parent_profile
                return Assessment.objects.filter(student__parent=parent)
            except:
                return Assessment.objects.none()
        elif user.is_student:
            try:
                student = user.student_profile
                return Assessment.objects.filter(student=student)
            except:
                return Assessment.objects.none()
        return Assessment.objects.none()
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an assessment as completed.
        """
        assessment = self.get_object()
        
        if assessment.status != Assessment.Status.IN_PROGRESS:
            return Response(
                {"error": "Only in-progress assessments can be completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assessment.status = Assessment.Status.COMPLETED
        assessment.save()
        
        return Response(
            {"message": "Assessment marked as completed."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        Get questions for an assessment based on student's grade level.
        """
        assessment = self.get_object()
        student = assessment.student
        
        # Check if a template exists for this grade level
        template = QuestionnaireTemplate.objects.filter(
            grade_level=student.grade,
            is_active=True
        ).first()
        
        if template:
            # Get questions from template in order
            template_questions = TemplateQuestion.objects.filter(
                template=template
            ).order_by('order')
            
            questions = [tq.question for tq in template_questions]
            return Response(QuestionSerializer(questions, many=True).data)
        else:
            # Fallback to getting questions by grade level
            questions = Question.objects.filter(
                grade_level=student.grade,
                is_active=True
            )
            return Response(QuestionSerializer(questions, many=True).data)


class ResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student responses.
    """
    queryset = Response.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ResponseCreateSerializer
        return ResponseSerializer
    
    def get_queryset(self):
        """
        Filter responses based on user role and assessment.
        """
        user = self.request.user
        
        # Filter by assessment if provided
        assessment_id = self.request.query_params.get('assessment')
        queryset = Response.objects.all()
        
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)
        
        # Apply role-based filtering
        if user.is_admin or user.is_teacher:
            return queryset
        elif user.is_parent:
            try:
                parent = user.parent_profile
                return queryset.filter(assessment__student__parent=parent)
            except:
                return Response.objects.none()
        elif user.is_student:
            try:
                student = user.student_profile
                return queryset.filter(assessment__student=student)
            except:
                return Response.objects.none()
        return Response.objects.none()
    
    @action(detail=False, methods=['post'])
    def submit_batch(self, request):
        """
        Submit multiple responses at once.
        """
        responses_data = request.data.get('responses', [])
        created_responses = []
        
        for response_data in responses_data:
            serializer = ResponseCreateSerializer(data=response_data)
            if serializer.is_valid():
                response = serializer.save()
                created_responses.append(ResponseSerializer(response).data)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            created_responses,
            status=status.HTTP_201_CREATED
        )


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing questionnaire templates.
    """
    queryset = QuestionnaireTemplate.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QuestionnaireTemplateCreateSerializer
        return QuestionnaireTemplateSerializer
    
    def get_queryset(self):
        """
        Optionally filter templates by grade level or active status.
        """
        queryset = QuestionnaireTemplate.objects.all()
        
        # Filter by grade level
        grade_level = self.request.query_params.get('grade_level')
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        Get questions for a template in order.
        """
        template = self.get_object()
        template_questions = TemplateQuestion.objects.filter(
            template=template
        ).order_by('order')
        
        result = []
        for tq in template_questions:
            question_data = QuestionSerializer(tq.question).data
            question_data['order'] = tq.order
            result.append(question_data)
        
        return Response(result)
