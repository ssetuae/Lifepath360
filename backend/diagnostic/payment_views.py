from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import stripe
import os
from dotenv import load_dotenv
from .payment_models import Payment
from .models import Assessment

# Load environment variables
load_dotenv()

# Set Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'your-stripe-secret-key')

class PaymentViewSet(viewsets.ViewSet):
    """
    API endpoint for payment processing.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        """
        Create a payment intent for a detailed report.
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
            
            # Check if payment already exists and is completed
            existing_payment = Payment.objects.filter(
                assessment=assessment,
                user=user,
                status=Payment.Status.COMPLETED
            ).first()
            
            if existing_payment:
                return Response({
                    "message": "Payment already completed for this assessment.",
                    "payment_id": existing_payment.id,
                    "status": existing_payment.status
                })
            
            # Set amount for detailed report (in AED)
            amount = 100  # 100 AED
            
            # Create payment record
            payment = Payment.objects.create(
                user=user,
                assessment=assessment,
                amount=amount,
                currency='AED',
                status=Payment.Status.PENDING
            )
            
            # Create payment intent with Stripe
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency='aed',
                    metadata={
                        'payment_id': payment.id,
                        'assessment_id': assessment.id,
                        'user_id': user.id
                    }
                )
                
                # Update payment with transaction ID
                payment.transaction_id = payment_intent.id
                payment.save()
                
                return Response({
                    "payment_id": payment.id,
                    "client_secret": payment_intent.client_secret,
                    "amount": amount,
                    "currency": "AED"
                })
                
            except Exception as e:
                # Update payment status to failed
                payment.status = Payment.Status.FAILED
                payment.save()
                
                return Response(
                    {"error": f"Error creating payment intent: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error processing payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """
        Confirm a payment for a detailed report.
        """
        try:
            payment = Payment.objects.get(id=pk)
            
            # Check if user has permission to access this payment
            user = request.user
            if payment.user != user and not user.is_admin:
                return Response(
                    {"error": "You do not have permission to access this payment."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get payment intent ID from request
            payment_intent_id = request.data.get('payment_intent_id')
            
            if not payment_intent_id:
                return Response(
                    {"error": "Payment intent ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify payment intent with Stripe
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                # Check if payment intent is successful
                if payment_intent.status == 'succeeded':
                    # Update payment status to completed
                    payment.status = Payment.Status.COMPLETED
                    payment.transaction_id = payment_intent_id
                    payment.payment_method = payment_intent.payment_method_types[0] if payment_intent.payment_method_types else 'card'
                    payment.save()
                    
                    return Response({
                        "message": "Payment confirmed successfully.",
                        "payment_id": payment.id,
                        "status": payment.status
                    })
                else:
                    # Update payment status based on payment intent status
                    if payment_intent.status == 'canceled':
                        payment.status = Payment.Status.FAILED
                    else:
                        payment.status = Payment.Status.PENDING
                    
                    payment.transaction_id = payment_intent_id
                    payment.save()
                    
                    return Response({
                        "message": f"Payment not completed. Status: {payment_intent.status}",
                        "payment_id": payment.id,
                        "status": payment.status
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response(
                    {"error": f"Error confirming payment: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Payment.DoesNotExist:
            return Response(
                {"error": f"Payment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error confirming payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def check_payment_status(self, request, pk=None):
        """
        Check the status of a payment for a detailed report.
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
            
            # Get latest payment for this assessment
            payment = Payment.objects.filter(
                assessment=assessment,
                user=user
            ).order_by('-created_at').first()
            
            if not payment:
                return Response({
                    "has_payment": False,
                    "message": "No payment found for this assessment."
                })
            
            # Check if payment is completed
            if payment.status == Payment.Status.COMPLETED:
                return Response({
                    "has_payment": True,
                    "is_paid": True,
                    "payment_id": payment.id,
                    "status": payment.status,
                    "created_at": payment.created_at,
                    "updated_at": payment.updated_at
                })
            else:
                return Response({
                    "has_payment": True,
                    "is_paid": False,
                    "payment_id": payment.id,
                    "status": payment.status,
                    "created_at": payment.created_at,
                    "updated_at": payment.updated_at
                })
            
        except Assessment.DoesNotExist:
            return Response(
                {"error": f"Assessment with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error checking payment status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def payment_history(self, request):
        """
        Get payment history for the current user.
        """
        try:
            user = request.user
            
            # Get all payments for this user
            payments = Payment.objects.filter(user=user).order_by('-created_at')
            
            # Format payment data
            payment_data = []
            for payment in payments:
                payment_data.append({
                    "payment_id": payment.id,
                    "assessment_id": payment.assessment.id,
                    "student_name": f"{payment.assessment.student.first_name} {payment.assessment.student.last_name}",
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status,
                    "created_at": payment.created_at,
                    "updated_at": payment.updated_at
                })
            
            return Response({
                "user_id": user.id,
                "email": user.email,
                "payments": payment_data
            })
            
        except Exception as e:
            return Response(
                {"error": f"Error retrieving payment history: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
