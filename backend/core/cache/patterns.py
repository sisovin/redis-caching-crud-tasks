def cache_key(prefix, *args):
    """
    Generate a cache key using the given prefix and arguments.
    """
    key = prefix
    for arg in args:
        key += f":{arg}"
    return key
