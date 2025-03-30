import json
import logging
import redis
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Redis client for operations not supported by Django's cache
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def get_cache(key):
    """Get a value from cache."""
    return cache.get(key)

def set_cache(key, value, timeout=None):
    """Set a value in cache."""
    return cache.set(key, value, timeout)

def delete_cache(key):
    """Delete a key from cache."""
    return cache.delete(key)

def get_task_cache_key(task_id):
    """Get cache key for a specific task."""
    return f"task_{task_id}"

def get_tasks_list_key():
    """Get cache key for tasks list."""
    return "tasks"

def invalidate_cache_prefix(prefix):
    """
    Delete all cache keys with a given prefix.
    """
    try:
        pattern = f"{prefix}*"
        logger.info(f"Invalidating cache keys with pattern: {pattern}")
        
        cursor = '0'
        deleted_count = 0
        
        while cursor != 0:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                redis_client.delete(*keys)
                deleted_count += len(keys)
                
            if cursor == '0' or cursor == 0:
                break
                
        logger.info(f"Invalidated {deleted_count} cache keys with prefix {prefix}")
        return deleted_count
    except Exception as e:
        logger.error(f"Error invalidating cache prefix {prefix}: {str(e)}")
        return 0