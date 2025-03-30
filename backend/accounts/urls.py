from django.urls import path
from .views import (
    UserProfileView,
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    CustomTokenRefreshView
)
# Add this import for TokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Simple, basic token generation
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Your enhanced refresh view
    
    # Change password endpoint
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # User profile endpoint
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]