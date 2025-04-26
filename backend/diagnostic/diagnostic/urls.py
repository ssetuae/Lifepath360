from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuestionViewSet,
    AssessmentViewSet,
    ResponseViewSet,
    QuestionnaireTemplateViewSet
)
from .ai_views import AIQuestionViewSet
from .analysis_views import AnalysisViewSet
from .report_views import ReportViewSet
from .nlp_views import NLPViewSet
from .recommendation_views import RecommendationViewSet
from .payment_views import PaymentViewSet

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'responses', ResponseViewSet)
router.register(r'templates', QuestionnaireTemplateViewSet)
router.register(r'ai', AIQuestionViewSet, basename='ai')
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'nlp', NLPViewSet, basename='nlp')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
