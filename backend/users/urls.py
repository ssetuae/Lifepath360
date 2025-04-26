from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserViewSet,
    StudentViewSet,
    ParentViewSet,
    TeacherViewSet,
    CustomTokenObtainPairView
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'parents', ParentViewSet)
router.register(r'teachers', TeacherViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include router URLs
    path('', include(router.urls)),
]
