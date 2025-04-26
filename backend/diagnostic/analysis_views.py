from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Assessment
from .learning_style_analyzer import LearningStyleAnalyzer

class AnalysisViewSet(viewsets.ViewSet):
    """
    API endpoint for analyzing assessment results.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def analyze(self, request, pk=None):
        """
        Analyze an assessment to determine learning styles, cognitive strengths,
        behavior patterns, and interests.
        """
        try:
            assessment = Assessment.objects.get(id=pk)
            
            # Check if user has permission to access this assessment
            user = request.user
            if not (user.is_admin or user.is_teacher or 
                   (user.is_parent and assessment.student.parent and assessment.student.parent.user == user) or
                   (user.is_student and assessment.student.user == user)):
                return Response(
                    {"error": "You do not have permission to access this assessment."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if assessment is completed
            if assessment.status != Assessment.Status.COMPLETED:
                return Response(
                    {"error": "Assessment is not completed yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Analyze assessment
            analysis_results = LearningStyleAnalyzer.analyze_assessment(pk)
            
            if 'error' in analysis_results:
                return Response(
                    analysis_results,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(analysis_results)
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error analyzing assessment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def student_history(self, request):
        """
        Get analysis history for a student.
        """
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {"error": "Student ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import Student
            student = Student.objects.get(id=student_id)
            
            # Check if user has permission to access this student's data
            user = request.user
            if not (user.is_admin or user.is_teacher or 
                   (user.is_parent and student.parent and student.parent.user == user) or
                   (user.is_student and student.user == user)):
                return Response(
                    {"error": "You do not have permission to access this student's data."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get completed assessments for this student
            assessments = Assessment.objects.filter(
                student=student,
                status=Assessment.Status.COMPLETED
            ).order_by('-end_time')
            
            # Analyze each assessment
            analysis_history = []
            for assessment in assessments:
                analysis = LearningStyleAnalyzer.analyze_assessment(assessment.id)
                if 'error' not in analysis:
                    analysis_history.append({
                        'assessment_id': assessment.id,
                        'date': assessment.end_time,
                        'analysis': analysis
                    })
            
            return Response({
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'grade': student.grade,
                'analysis_history': analysis_history
            })
            
        except Student.DoesNotExist:
            return Response(
                {"error": f"Student with ID {student_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error retrieving analysis history: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
