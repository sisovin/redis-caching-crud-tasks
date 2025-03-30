"""
Decorators for caching Django views, REST Framework views, and class methods.
"""
import functools
import logging
import time
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from django.http import HttpResponse
from .utils import get_cache, set_cache, invalidate_cache_prefix

logger = logging.getLogger(__name__)

def cache_view(prefix, timeout=300, include_user_id=False, vary_on_headers=None):
    """
    Cache the response of a Django or DRF view.
    
    Args:
        prefix (str): Cache key prefix
        timeout (int): Cache timeout in seconds
        include_user_id (bool): Whether to include user ID in cache key
        vary_on_headers (list): List of headers to include in cache key
        
    Returns:
        function: Decorator function
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key components
            key_parts = [prefix, request.path]
            
            # Add query params
            if request.GET:
                key_parts.append(request.GET.urlencode())
                
            # Add user ID if requested and authenticated
            if include_user_id and hasattr(request, 'user') and request.user.is_authenticated:
                key_parts.append(f"user:{request.user.id}")
            
            # Add specified headers
            if vary_on_headers:
                for header in vary_on_headers:
                    if header in request.headers:
                        key_parts.append(f"{header}:{request.headers[header]}")
            
            # Add route kwargs
            for k, v in kwargs.items():
                key_parts.append(f"{k}:{v}")
                
            # Generate final cache key
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_response = get_cache(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for view: {view_func.__name__} with key: {cache_key}")
                
                # Check response type (Django HttpResponse or DRF Response)
                if isinstance(cached_response, dict) and 'content' in cached_response:
                    # Django HttpResponse
                    return HttpResponse(
                        content=cached_response.get('content'),
                        status=cached_response.get('status_code', 200),
                        content_type=cached_response.get('content_type', 'application/json')
                    )
                else:
                    # DRF Response
                    return Response(cached_response)
            
            # Call the view function and cache its response
            start_time = time.time()
            response = view_func(request, *args, **kwargs)
            execution_time = time.time() - start_time
            
            # Only cache if response is successful
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                logger.debug(f"Caching view result for: {view_func.__name__} (took {execution_time:.4f}s)")
                
                # Different handling for Django and DRF responses
                if isinstance(response, HttpResponse):
                    cache_data = {
                        'content': response.content,
                        'status_code': response.status_code,
                        'content_type': response.get('Content-Type', 'application/json')
                    }
                    set_cache(cache_key, cache_data, timeout)
                elif isinstance(response, Response):
                    set_cache(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator

def cache_method(prefix, timeout=3600, arg_positions=None, kwarg_keys=None):
    """
    Cache results of a class method.
    
    Args:
        prefix (str): Cache key prefix
        timeout (int): Cache timeout in seconds
        arg_positions (list): List of arg positions to include in cache key
        kwarg_keys (list): List of kwarg keys to include in cache key
        
    Returns:
        function: Decorator function
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # Create a signature based on specified args and kwargs
            key_parts = [prefix]
            
            # Add class and method names
            key_parts.append(f"{self.__class__.__name__}.{method.__name__}")
            
            # Add selected positional args
            if arg_positions:
                for pos in arg_positions:
                    if pos < len(args):
                        key_parts.append(str(args[pos]))
            
            # Add selected keyword args
            if kwarg_keys:
                for key in kwarg_keys:
                    if key in kwargs:
                        key_parts.append(f"{key}:{kwargs[key]}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for method: {method.__name__} with key: {cache_key}")
                return cached_result
            
            # Execute method and cache result
            start_time = time.time()
            result = method(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(f"Caching method result for: {method.__name__} (took {execution_time:.4f}s)")
            set_cache(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def invalidate_cache_on_change(prefixes):
    """
    Decorator to invalidate cache after a function/method executes.
    
    Args:
        prefixes (list): List of cache prefixes to invalidate
        
    Returns:
        function: Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Invalidate specified cache prefixes
            for prefix in prefixes:
                invalidate_cache_prefix(prefix)
                logger.info(f"Invalidated cache prefix: {prefix}")
                
            return result
        return wrapper
    return decorator