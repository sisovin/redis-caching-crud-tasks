from django.utils.decorators import decorator_from_middleware_with_args
from django.views.decorators.cache import cache_page as django_cache_page

def cache_page(timeout, cache=None, key_prefix=None):
    """
    Decorator to cache views for a specified timeout period.
    """
    return decorator_from_middleware_with_args(django_cache_page)(timeout, cache=cache, key_prefix=key_prefix)
