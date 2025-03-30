"""
Middleware for handling cache-related HTTP headers and behaviors.
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware that sets Cache-Control headers for responses.
    
    This middleware allows for fine-grained control over how responses
    should be cached by browsers and CDNs based on the view, content type,
    or other criteria.
    """
    
    # Paths that should never be cached
    NEVER_CACHE_PATHS = [
        '/admin/',
        '/api/auth/',
        '/api/token/',
    ]
    
    # Paths that can be cached for a moderate amount of time
    MODERATE_CACHE_PATHS = [
        '/api/tasks/',
        '/api/users/',
    ]
    
    # Paths that can be cached for a long time
    LONG_CACHE_PATHS = [
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)
        
    def process_response(self, request, response):
        """
        Process the response and set appropriate caching headers.
        """
        path = request.path
        
        # Never cache certain paths
        if any(path.startswith(p) for p in self.NEVER_CACHE_PATHS):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
            
        # Long cache for static assets
        if any(path.startswith(p) for p in self.LONG_CACHE_PATHS):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            return response
            
        # Moderate cache for API responses
        if any(path.startswith(p) for p in self.MODERATE_CACHE_PATHS):
            # Only cache GET requests
            if request.method == 'GET':
                response['Cache-Control'] = 'public, max-age=60, s-maxage=300'  # 1 min browser, 5 min CDN
            else:
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return response
            
        # Default: no caching
        if 'Cache-Control' not in response:
            response['Cache-Control'] = 'no-cache, private'
            
        return response

class WebSecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that sets security-related HTTP headers.
    
    This middleware adds headers like Content-Security-Policy, 
    X-Content-Type-Options, and others to improve web security.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Enable browser XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy (CSP)
        csp_directives = [
            "default-src 'self'",
            "img-src 'self' data:",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "connect-src 'self'",
            "font-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response