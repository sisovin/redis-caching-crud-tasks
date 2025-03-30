from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.utils import timezone 
from rest_framework_simplejwt.tokens import RefreshToken
from core.cache.utils import invalidate_cache_prefix
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from django_redis import get_redis_connection
# Add the import at the top:
from core.authentication import RedisTokenStore
from django.conf import settings  # Add this import
# Import the token_refresh_view
from rest_framework_simplejwt.views import TokenRefreshView
import json
from django.core.files.base import ContentFile
import os

User = get_user_model()

class RegisterView(APIView):
    """
    API view for user registration.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'bio': openapi.Schema(type=openapi.TYPE_STRING),
                                'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                            }
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="JWT refresh token"
                        ),
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="JWT access token"
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request - Invalid registration data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'email': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'password': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'password_confirm': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                    }
                )
            )
        },
        operation_description="Register a new user and return JWT tokens",
        operation_summary="Register new user",
        tags=['auth']
    )
    def post(self, request):
        """
        Register a new user.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Calculate expiration times
            access_exp = timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            refresh_exp = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            
            # Format expiration times in a human-readable way
            access_expiry = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            refresh_expiry = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            
            # Store token in Redis
            token_store = RedisTokenStore()
            token_store.add_token(
                user_id=user.id,
                jti=refresh['jti'],
                token_data=str(refresh),
                expires_at=refresh_exp
            )
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'expires': {
                    'access': access_exp.isoformat(),
                    'refresh': refresh_exp.isoformat(),
                },
                'expiry': {
                    'access': f"{access_expiry.seconds // 3600}h",
                    'refresh': f"{refresh_expiry.days}d"
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API view for user login.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(  # or 201 for register
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT, description="User information"),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                    'expires': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token expiration timestamp"),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token expiration timestamp"),
                        }
                    ),
                    'expiry': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING, description="Human-readable access token lifetime (e.g. '1h')"),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Human-readable refresh token lifetime (e.g. '7d')"),
                        }
                    ),
                }
            )
            ),
            401: openapi.Response(description="Invalid credentials")
        },
        operation_description="Login user and return JWT tokens",
        operation_summary="Login user",
        tags=['auth']
    )
    def post(self, request):
        """
        Login a user and return tokens.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Calculate expiration times
                access_exp = timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                refresh_exp = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                
                # Format expiration times in a human-readable way
                access_expiry = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                refresh_expiry = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                
                # Store token in Redis
                token_store = RedisTokenStore()
                token_store.add_token(
                    user_id=user.id,
                    jti=refresh['jti'],
                    token_data=str(refresh),
                    expires_at=refresh_exp
                )
                
                # Try to login user through Django's session mechanism
                try:
                    login(request, user)
                except Exception as e:
                    # Just log the error but continue - we're using JWT tokens anyway
                    print(f"Session login error (non-fatal): {e}")
                
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'expires': {
                        'access': access_exp.isoformat(),
                        'refresh': refresh_exp.isoformat(),
                    },
                    'expiry': {
                        'access': f"{access_expiry.seconds // 3600}h",
                        'refresh': f"{refresh_expiry.days}d"
                    }
                })
            # Rest of your code...
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# In your accounts/views.py
class ChangePasswordView(APIView):
    """
    API view for changing user password.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password'],
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request - Password change failed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        operation_description="Change the authenticated user's password",
        operation_summary="Change password",
        tags=['auth']
    )
    def post(self, request):
        """
        Change the authenticated user's password.
        """
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': 'Both old and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            
            # Invalidate cache for user data
            invalidate_cache_prefix(f'user-detail:{user.pk}')
            invalidate_cache_prefix(f'user-profile:{user.pk}')
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Old password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token to blacklist"),
            }
        ),
        responses={
            200: openapi.Response(description="Successfully logged out"),
            401: openapi.Response(description="Authentication failed"),
            400: openapi.Response(description="Invalid refresh token")
        },
        operation_description="Logout and blacklist the refresh token",
        operation_summary="Logout user",
        tags=['auth']
    )
    def post(self, request):
        try:
            # Get refresh token from request data
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse the token
            token = RefreshToken(refresh_token)
            token_jti = token.get('jti')
            
            # Add to Django's blacklist (for SimpleJWT compatibility)
            token.blacklist()
            
            # Also blacklist in Redis
            token_store = RedisTokenStore()
            token_store.blacklist_token(token_jti)
            
            # Clear session if using session authentication as well
            logout(request)
            
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   

class CustomTokenRefreshView(TokenRefreshView):
    """
    Enhanced API view for refreshing JWT tokens.
    Takes a refresh token and returns a new access token with expiration information.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
            }
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="New access token"),
                        'expires': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token expiration timestamp"),
                            }
                        ),
                        'expiry': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access': openapi.Schema(type=openapi.TYPE_STRING, description="Human-readable access token lifetime (e.g. '1h')"),
                            }
                        ),
                    }
                )
            ),
            401: openapi.Response(description="Invalid refresh token")
        },
        operation_description="Refresh the JWT access token using a valid refresh token",
        operation_summary="Refresh token",
        tags=['auth']
    )
    def post(self, request, *args, **kwargs):
        """
        Enhanced token refresh that also provides expiration information.
        """
        # Call the parent implementation to get the new access token
        response = super().post(request, *args, **kwargs)
        
        # If the refresh was successful, add expiration info
        if response.status_code == status.HTTP_200_OK:
            # Calculate access token expiry
            access_exp = timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            access_expiry = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            
            # Add expiration information to response
            response.data.update({
                'expires': {
                    'access': access_exp.isoformat(),
                },
                'expiry': {
                    'access': f"{access_expiry.seconds // 3600}h",
                }
            })
            
            # If using token rotation, handle the new refresh token
            if 'refresh' in response.data:
                refresh_exp = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                refresh_expiry = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                
                # Add refresh token expiration information
                response.data['expires']['refresh'] = refresh_exp.isoformat()
                response.data['expiry']['refresh'] = f"{refresh_expiry.days}d"
                
                # Store the new refresh token in Redis if needed
                # (This happens when ROTATE_REFRESH_TOKENS is True)
                try:
                    refresh_token = response.data['refresh']
                    token = RefreshToken(refresh_token)
                    token_jti = token.get('jti')
                    user_id = token.get('user_id')
                    
                    token_store = RedisTokenStore()
                    token_store.add_token(
                        user_id=user_id,
                        jti=token_jti,
                        token_data=refresh_token,
                        expires_at=refresh_exp
                    )
                except Exception as e:
                    # Just log the error but continue - token renewal still works
                    print(f"Redis token storage error (non-fatal): {e}")
        
        return response
    
class UserProfileView(APIView):
    """
    API endpoint for user profile management.
    
    This endpoint allows for retrieving and updating a user's profile information.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully",
                schema=UserSerializer
            ),
            401: openapi.Response(description="Authentication credentials were not provided")
        },
        operation_description="Retrieve the authenticated user's profile information",
        operation_summary="Get user profile",
        tags=['profile']
    )
    def get(self, request):
        """
        Retrieve the authenticated user's profile.
        
        Returns the user's profile data including personal information and settings.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="User profile updated successfully",
                schema=UserSerializer
            ),
            400: openapi.Response(description="Invalid data provided"),
            401: openapi.Response(description="Authentication credentials were not provided")
        },
        operation_description="Update the authenticated user's profile information",
        operation_summary="Update user profile",
        tags=['profile']
    )
    def put(self, request):
        """
        Update the authenticated user's profile.
        
        Allows updating user profile information such as name, bio, and other details.
        """
        # Create a copy of the data to avoid modifying the original request
        data = request.data.copy()
        
        # Handle the avatar field when provided as a string filename
        avatar_file = data.get('avatar')
        
        # If avatar is coming as a string but not a file object
        if 'avatar' in data and isinstance(avatar_file, str):
            # If it's a simple filename without path information
            if not avatar_file.startswith('/media/') and not avatar_file.startswith('http'):
                # Keep it in the data, but ensure your serializer/model will handle this correctly
                # For example, your model might need a custom save method to process the filename
                pass
                
        serializer = UserSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            # For debugging
            print(f"Valid data: {serializer.validated_data}")
            
            user = serializer.save()
            
            # If avatar is a string filename, handle it manually
            if 'avatar' in data and isinstance(data['avatar'], str) and not data['avatar'].startswith('/media/') and not data['avatar'].startswith('http'):
                # This assumes you have a method to handle filenames in your User model
                # You might need to add this method to your User model
                
                # Example of handling a filename
                # This assumes avatar files exist in a media directory accessible to your app
                avatar_path = os.path.join('avatars', data['avatar'])
                user.avatar = avatar_path
                user.save(update_fields=['avatar'])
                
            # Invalidate cache for user data
            invalidate_cache_prefix(f'user-detail:{request.user.pk}')
            invalidate_cache_prefix(f'user-profile:{request.user.pk}')
            
            # Re-serialize to get updated data including the avatar
            updated_serializer = UserSerializer(user)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)