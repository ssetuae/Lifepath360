from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Response as StudentResponse, Assessment
from .nlp_analyzer import NLPResponseAnalyzer

class NLPViewSet(viewsets.ViewSet):
    """
    API endpoint for NLP analysis of open-ended responses.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def analyze_response(self, request, pk=None):
        """
        Analyze an open-ended response using NLP.
        """
        try:
            response = StudentResponse.objects.get(id=pk)
            
            # Check if user has permission to access this response
            user = request.user
            assessment = response.assessment
            if not (user.is_admin or user.is_teacher or 
                   (user.is_parent and assessment.student.parent and assessment.student.parent.user == user) or
                   (user.is_student and assessment.student.user == user)):
                return Response(
                    {"error": "You do not have permission to access this response."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Analyze response
            analysis_results = NLPResponseAnalyzer.analyze_open_response(pk)
            
            if 'error' in analysis_results:
                return Response(
                    analysis_results,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(analysis_results)
            
        except StudentResponse.DoesNotExist:
            return Response(
                {"error": f"Response with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error analyzing response: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def analyze_assessment(self, request, pk=None):
        """
        Analyze all open-ended responses for an assessment using NLP.
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
            
            # Analyze assessment responses
            analysis_results = NLPResponseAnalyzer.analyze_assessment_open_responses(pk)
            
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
                {"error": f"Error analyzing assessment responses: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def sentiment_analysis(self, request):
        """
        Analyze sentiment of provided text.
        """
        text = request.data.get('text')
        
        if not text:
            return Response(
                {"error": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze sentiment
        sentiment_scores = NLPResponseAnalyzer.get_sentiment_scores(text)
        
        if 'error' in sentiment_scores:
            return Response(
                sentiment_scores,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(sentiment_scores)
    
    @action(detail=False, methods=['post'])
    def extract_keywords(self, request):
        """
        Extract keywords and topics from provided text.
        """
        text = request.data.get('text')
        
        if not text:
            return Response(
                {"error": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract keywords
        keywords = NLPResponseAnalyzer.extract_keywords(text)
        
        if 'error' in keywords:
            return Response(
                keywords,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(keywords)
