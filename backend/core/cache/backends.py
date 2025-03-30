"""
Custom Redis cache backends for specialized caching strategies.
"""
import time
import json
import logging
from django.core.cache.backends.base import BaseCache
from django.conf import settings
import redis

logger = logging.getLogger(__name__)

class HierarchicalRedisCache(BaseCache):
    """
    Redis cache with hierarchical key invalidation.
    
    Allows invalidating a group of related cache keys using a hierarchical structure.
    Example: 'tasks:user:1:list' can be invalidated with 'tasks:user:1:*'
    
    Usage in settings.py:
    
    CACHES = {
        "hierarchical": {
            "BACKEND": "core.cache.backends.HierarchicalRedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": REDIS_PASSWORD,
            }
        }
    }
    """
    
    def __init__(self, server, params):
        super().__init__(params)
        self._client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False  # Keep binary format for compatibility
        )
        self._options = params.get('OPTIONS', {})
    
    def add(self, key, value, timeout=None, version=None):
        """Add key if it doesn't exist"""
        key = self.make_key(key, version)
        if self._client.exists(key):
            return False
        
        return self.set(key, value, timeout)
    
    def get(self, key, default=None, version=None):
        """Get a value with automatic deserialization"""
        key = self.make_key(key, version)
        value = self._client.get(key)
        
        if value is None:
            return default
        
        return self.decode(value)
    
    def set(self, key, value, timeout=None, version=None):
        """Set a value with automatic serialization"""
        key = self.make_key(key, version)
        timeout = self.get_timeout(timeout)
        
        encoded_value = self.encode(value)
        
        if timeout is None:
            return self._client.set(key, encoded_value)
        
        return self._client.setex(key, timeout, encoded_value)
    
    def delete(self, key, version=None):
        """Delete a specific key"""
        key = self.make_key(key, version)
        self._client.delete(key)
    
    def delete_pattern(self, pattern, version=None):
        """Delete all keys matching a pattern"""
        pattern = self.make_key(pattern, version)
        cursor = '0'
        deleted = 0
        
        while cursor != 0:
            cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                deleted += self._client.delete(*keys)
            if cursor == '0' or not cursor:
                break
                
        return deleted
    
    def clear(self):
        """Clear the entire cache"""
        self._client.flushdb()
    
    def get_many(self, keys, version=None):
        """Get multiple keys at once"""
        versioned_keys = [self.make_key(key, version) for key in keys]
        values = self._client.mget(versioned_keys)
        
        result = {}
        for key, value in zip(keys, values):
            if value is not None:
                result[key] = self.decode(value)
                
        return result
    
    def set_many(self, mapping, timeout=None, version=None):
        """Set multiple key-value pairs at once"""
        if not mapping:
            return
            
        versioned_mapping = {
            self.make_key(key, version): self.encode(value)
            for key, value in mapping.items()
        }
        
        pipeline = self._client.pipeline()
        timeout = self.get_timeout(timeout)
        
        if timeout is None:
            pipeline.mset(versioned_mapping)
        else:
            for key, value in versioned_mapping.items():
                pipeline.setex(key, timeout, value)
                
        pipeline.execute()
    
    def delete_many(self, keys, version=None):
        """Delete multiple keys at once"""
        if not keys:
            return
            
        versioned_keys = [self.make_key(key, version) for key in keys]
        self._client.delete(*versioned_keys)
    
    def incr(self, key, delta=1, version=None):
        """Increment a key by delta"""
        key = self.make_key(key, version)
        value = self._client.incr(key, delta)
        return value
    
    def has_key(self, key, version=None):
        """Check if key exists"""
        key = self.make_key(key, version)
        return self._client.exists(key)

    def encode(self, obj):
        """Encode an object for storage"""
        if isinstance(obj, bool) or not isinstance(obj, (int, float, str, bytes)):
            return self._serialize(obj)
        return obj

    def decode(self, obj):
        """Decode an object from storage"""
        try:
            value = int(obj)
        except (ValueError, TypeError):
            try:
                value = float(obj)
            except (ValueError, TypeError):
                try:
                    value = self._deserialize(obj)
                except Exception:
                    value = obj
        return value

    def _serialize(self, obj):
        """Serialize an object to a string"""
        return json.dumps(obj).encode('utf-8')

    def _deserialize(self, data):
        """Deserialize an object from a string"""
        if isinstance(data, bytes):
            try:
                return json.loads(data.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return data
        return data