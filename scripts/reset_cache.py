import redis
from django.conf import settings

def reset_cache():
    """
    Clear all entries in the Redis cache.
    """
    redis_instance = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB
    )
    redis_instance.flushdb()

if __name__ == "__main__":
    reset_cache()
    print("Redis cache has been reset.")
