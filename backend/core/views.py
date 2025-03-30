# filepath: d:\VueProjects\redis-caching-crud-tasks\backend\core\views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
import redis

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Service is running correctly'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
    
def api_status(request):
    """Simple view to check API status and configuration."""
    # Check Redis connection
    redis_status = "Not configured"
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            socket_connect_timeout=1,
        )
        if r.ping():
            redis_status = "Connected"
        else:
            redis_status = "Connection failed"
    except Exception as e:
        redis_status = f"Error: {str(e)}"
    
    return JsonResponse({
        'status': 'ok',
        'redis': redis_status,
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
    })
    

