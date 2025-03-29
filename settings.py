# settings.py

# Redis configuration settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Configure Django to use Redis as the cache backend
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
