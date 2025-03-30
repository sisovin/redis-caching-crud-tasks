"""
Caching patterns and key generation strategies for various use cases.
"""
import hashlib
import pickle

def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate consistent cache keys with hashing for complex arguments.
    
    Args:
        prefix (str): The cache key prefix
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        str: A consistent cache key string
    """
    key_parts = [prefix]
    
    # Add positional args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)) or arg is None:
            key_parts.append(str(arg))
        else:
            # Hash complex objects
            key_parts.append(hashlib.md5(pickle.dumps(arg)).hexdigest()[:8])
    
    # Add keyword args (sorted for consistency)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        for k, v in sorted_items:
            if isinstance(v, (str, int, float, bool)) or v is None:
                key_parts.append(f"{k}={v}")
            else:
                key_parts.append(f"{k}={hashlib.md5(pickle.dumps(v)).hexdigest()[:8]}")
    
    return ":".join(key_parts)

def user_specific_key(prefix, user_id, resource_id=None):
    """
    Generate a cache key specific to a user and optionally a resource.
    
    Args:
        prefix (str): The cache key prefix
        user_id (int): The user ID
        resource_id (int, optional): Optional resource ID
        
    Returns:
        str: A user-specific cache key
    """
    if resource_id is not None:
        return f"{prefix}:user:{user_id}:resource:{resource_id}"
    return f"{prefix}:user:{user_id}"