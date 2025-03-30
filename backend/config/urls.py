from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.views import api_status
from core.views import health_check

# Create schema view for API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Redis Caching CRUD Tasks API",
      default_version='v1',
      description="A Django API for task management with Redis caching",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
        
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<str:format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/tasks/', include('task_manager.urls')),
    path('api/status/', api_status, name='api-status'),
    path('api/health/', health_check, name='api-health'),
]

# Add this for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)