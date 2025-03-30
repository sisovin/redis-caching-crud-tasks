import redis
from django.conf import settings

redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def get_cache(key):
    """
    Retrieve a value from the Redis cache.
    """
    value = redis_instance.get(key)
    if value:
        return value.decode('utf-8')
    return None

def set_cache(key, value, timeout=None):
    """
    Set a value in the Redis cache with an optional timeout.
    """
    redis_instance.set(key, value, ex=timeout)
