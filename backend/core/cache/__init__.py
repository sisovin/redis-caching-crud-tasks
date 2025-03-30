"""
Caching module that provides Redis-based caching utilities.
Import the main utilities directly from this module.
"""
from .utils import get_cache, set_cache, invalidate_cache_prefix
from .decorators import cache_view, cache_method, invalidate_cache_on_change
from .patterns import generate_cache_key, user_specific_key