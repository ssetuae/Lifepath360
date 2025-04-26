from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, QuestionOption
from .serializers import QuestionSerializer, QuestionCreateSerializer
from .ai_question_generator import AIQuestionGenerator
from users.models import Student

class AIQuestionViewSet(viewsets.ViewSet):
    """
    API endpoint for generating AI-driven questions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate AI-driven questions for a specific grade level.
        """
        grade = request.data.get('grade')
        num_questions = int(request.data.get('num_questions', 10))
        categories = request.data.get('categories', None)
        
        if not grade:
            return Response(
                {"error": "Grade level is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate grade level
        if grade not in dict(Student.Grade.choices):
            return Response(
                {"error": f"Invalid grade level: {grade}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate questions
        questions = AIQuestionGenerator.generate_questions_for_grade(
            grade, num_questions, categories
        )
        
        if not questions:
            return Response(
                {"error": "Failed to generate questions. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return generated questions
        return Response(
            {
                "message": f"Successfully generated {len(questions)} questions.",
                "questions": QuestionSerializer(questions, many=True).data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def generate_for_assessment(self, request):
        """
        Generate AI-driven questions for a specific assessment.
        """
        assessment_id = request.data.get('assessment_id')
        num_questions = int(request.data.get('num_questions', 30))
        
        if not assessment_id:
            return Response(
                {"error": "Assessment ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .models import Assessment
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Get student's grade level
            grade = assessment.student.grade
            
            # Generate questions
            questions = AIQuestionGenerator.generate_questions_for_grade(
                grade, num_questions
            )
            
            if not questions:
                return Response(
                    {"error": "Failed to generate questions. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create a questionnaire template for this assessment
            from .models import QuestionnaireTemplate, TemplateQuestion
            template = QuestionnaireTemplate.objects.create(
                name=f"Assessment {assessment_id} Template",
                description=f"AI-generated template for assessment {assessment_id}",
                grade_level=grade,
                is_active=True
            )
            
            # Add questions to template
            for i, question in enumerate(questions, start=1):
                TemplateQuestion.objects.create(
                    template=template,
                    question=question,
                    order=i
                )
            
            # Return success response
            return Response(
                {
                    "message": f"Successfully generated {len(questions)} questions for assessment {assessment_id}.",
                    "template_id": template.id,
                    "questions": QuestionSerializer(questions, many=True).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {assessment_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating questions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
