from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Assessment
from .course_recommender import CourseRecommender

class RecommendationViewSet(viewsets.ViewSet):
    """
    API endpoint for course recommendations.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Get course recommendations based on assessment results.
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
            
            # Get number of recommendations to return
            num_recommendations = int(request.query_params.get('num', 3))
            
            # Get course recommendations
            recommendations = CourseRecommender.get_course_recommendations(pk, num_recommendations)
            
            if 'error' in recommendations:
                return Response(
                    recommendations,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(recommendations)
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating course recommendations: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def learning_journey(self, request, pk=None):
        """
        Get learning journey for a specific course recommendation.
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
            
            # Get course name and category
            course_name = request.query_params.get('course_name')
            category = request.query_params.get('category')
            
            if not course_name or not category:
                return Response(
                    {"error": "Course name and category are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate learning journey
            learning_journey = CourseRecommender._generate_learning_journey(
                course_name, category, assessment.student.grade
            )
            
            return Response({
                'assessment_id': pk,
                'course_name': course_name,
                'category': category,
                'learning_journey': learning_journey
            })
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating learning journey: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def career_college(self, request, pk=None):
        """
        Get career and college affinities based on assessment results.
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
            
            # Get analysis results
            from .learning_style_analyzer import LearningStyleAnalyzer
            analysis_results = LearningStyleAnalyzer.analyze_assessment(pk)
            
            if 'error' in analysis_results:
                return Response(
                    analysis_results,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate career and college affinities
            affinities = CourseRecommender._generate_career_college_affinities(
                analysis_results['interests']['scores'],
                analysis_results['cognitive_strengths']['scores']
            )
            
            return Response({
                'assessment_id': pk,
                'student_name': analysis_results['student_name'],
                'affinities': affinities
            })
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating career and college affinities: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def global_exams(self, request, pk=None):
        """
        Get global examination recommendations based on assessment results.
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
            
            # Get analysis results
            from .learning_style_analyzer import LearningStyleAnalyzer
            analysis_results = LearningStyleAnalyzer.analyze_assessment(pk)
            
            if 'error' in analysis_results:
                return Response(
                    analysis_results,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate global exam recommendations
            exams = CourseRecommender._generate_global_exam_recommendations(
                assessment.student.grade,
                analysis_results['interests']['scores'],
                analysis_results['cognitive_strengths']['scores']
            )
            
            return Response({
                'assessment_id': pk,
                'student_name': analysis_results['student_name'],
                'grade': assessment.student.grade,
                'exams': exams
            })
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating global exam recommendations: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
