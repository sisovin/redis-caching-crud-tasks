"""
Middleware for monitoring and optimizing application performance.
"""
import time
import logging
from django.db import connection
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware that logs request performance metrics.
    
    This middleware tracks request processing time and database query counts,
    helping to identify slow endpoints or excessive database operations.
    """
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)
        
    def process_request(self, request):
        """
        Mark the start time of request processing.
        """
        request.start_time = time.time()
        
    def process_response(self, request, response):
        """
        Log performance metrics for the request.
        """
        # Skip performance tracking for certain paths
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Get query count if DEBUG is True
            query_count = len(connection.queries) if settings.DEBUG else 0
            
            # Add server timing header
            response['Server-Timing'] = f'total;dur={duration * 1000:.2f}'
            
            # Log slow requests (more than 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} took "
                    f"{duration:.4f}s with {query_count} queries"
                )
            else:
                logger.debug(
                    f"Request: {request.method} {request.path} took "
                    f"{duration:.4f}s with {query_count} queries"
                )
                
        return response

class CacheBustingMiddleware(MiddlewareMixin):
    """
    Middleware that allows for cache busting of static assets.
    
    This middleware appends a version number to static files URLs,
    ensuring browsers load fresh versions when the files change.
    """
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.version = getattr(settings, 'CACHE_VERSION', 1)
        super().__init__(get_response)
        
    def process_template_response(self, request, response):
        """
        Inject a cache_version variable into the template context.
        """
        if hasattr(response, 'context_data'):
            response.context_data['cache_version'] = self.version
            
        return response