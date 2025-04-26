from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
import os
from .models import Assessment
from .report_generator import ReportGenerator

class ReportViewSet(viewsets.ViewSet):
    """
    API endpoint for generating and retrieving assessment reports.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Generate and retrieve a summary PDF report for an assessment.
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
            
            # Generate summary report
            report_path = ReportGenerator.generate_summary_report(pk)
            
            if not report_path:
                return Response(
                    {"error": "Failed to generate summary report."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return PDF file
            response = FileResponse(
                open(report_path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="summary_report_{pk}.pdf"'
            
            # Delete temporary file after response is sent
            os.unlink(report_path)
            
            return response
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating summary report: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def detailed(self, request, pk=None):
        """
        Generate and retrieve a detailed PDF report for an assessment.
        Requires payment verification.
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
            
            # TODO: Check if payment has been made for detailed report
            # This will be implemented in step 013 (implement_payment_integration_for_detailed_reports)
            payment_verified = False
            
            # For now, allow admins and teachers to access detailed reports without payment
            if user.is_admin or user.is_teacher:
                payment_verified = True
            
            if not payment_verified:
                return Response(
                    {
                        "error": "Payment required for detailed report.",
                        "message": "Please make a payment to access the detailed report."
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            
            # Generate detailed report
            report_path = ReportGenerator.generate_detailed_report(pk)
            
            if not report_path:
                return Response(
                    {"error": "Failed to generate detailed report."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return PDF file
            response = FileResponse(
                open(report_path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="detailed_report_{pk}.pdf"'
            
            # Delete temporary file after response is sent
            os.unlink(report_path)
            
            return response
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error generating detailed report: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
