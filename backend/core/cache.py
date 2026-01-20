"""
Caching utilities using cachetools.
"""
from functools import wraps
from cachetools import TTLCache
import hashlib
import json

# Initialize caches with different TTLs
stock_details_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes
candles_cache = TTLCache(maxsize=500, ttl=1800)  # 30 minutes
model_cache = TTLCache(maxsize=100, ttl=600)  # 10 minutes
stock_list_cache = TTLCache(maxsize=10, ttl=3600)  # 1 hour


def create_cache_key(*args, **kwargs):
    """Create a unique cache key from arguments."""
    key_dict = {"args": args, "kwargs": kwargs}
    key_str = json.dumps(key_dict, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(cache, key_func=None):
    """
    Decorator for caching function results.
    
    Args:
        cache: TTLCache instance to use
        key_func: Optional function to generate cache key from args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = create_cache_key(*args, **kwargs)
            
            # Check cache
            if cache_key in cache:
                return cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = result
            return result
        
        return wrapper
    return decorator


def clear_cache(cache_name: str = "all"):
    """Clear specific or all caches."""
    if cache_name == "all":
        stock_details_cache.clear()
        candles_cache.clear()
        model_cache.clear()
        stock_list_cache.clear()
    elif cache_name == "stock_details":
        stock_details_cache.clear()
    elif cache_name == "candles":
        candles_cache.clear()
    elif cache_name == "model":
        model_cache.clear()
    elif cache_name == "stock_list":
        stock_list_cache.clear()


def get_cache_info():
    """Get information about cache usage."""
    return {
        "stock_details": {
            "size": len(stock_details_cache),
            "maxsize": stock_details_cache.maxsize
        },
        "candles": {
            "size": len(candles_cache),
            "maxsize": candles_cache.maxsize
        },
        "model": {
            "size": len(model_cache),
            "maxsize": model_cache.maxsize
        },
        "stock_list": {
            "size": len(stock_list_cache),
            "maxsize": stock_list_cache.maxsize
        }
    }
