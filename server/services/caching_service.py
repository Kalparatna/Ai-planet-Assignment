"""Caching Service - Provides in-memory caching for API responses"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Union, Callable
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CachingService:
    """Service for caching API responses and LLM results"""
    
    def __init__(self):
        # In-memory cache
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache configuration
        self.default_ttl = 3600  # 1 hour default TTL
        self.max_memory_items = 1000  # Maximum items in memory cache
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from the input data"""
        if isinstance(data, str):
            serialized = data
        else:
            try:
                serialized = json.dumps(data, sort_keys=True)
            except (TypeError, ValueError):
                serialized = str(data)
        
        # Create hash of the serialized data
        key = hashlib.md5(serialized.encode()).hexdigest()
        return f"{prefix}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from in-memory cache"""
        # Get from memory cache
        cache_item = self.memory_cache.get(key)
        if cache_item:
            # Check if item is expired
            if cache_item.get("expires_at", 0) > time.time():
                logger.debug(f"Cache hit for key: {key}")
                return cache_item.get("data")
            else:
                # Remove expired item
                logger.debug(f"Removing expired cache item: {key}")
                del self.memory_cache[key]
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set item in in-memory cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Set in memory cache
        self.memory_cache[key] = {
            "data": value,
            "expires_at": time.time() + ttl
        }
        
        logger.debug(f"Cached item with key: {key}, TTL: {ttl}s")
        
        # Cleanup memory cache if it's too large
        if len(self.memory_cache) > self.max_memory_items:
            self._cleanup_memory_cache()
        
        return True
    
    def _cleanup_memory_cache(self):
        """Remove expired and oldest items from memory cache"""
        current_time = time.time()
        initial_size = len(self.memory_cache)
        
        # First remove expired items
        expired_keys = [k for k, v in self.memory_cache.items() 
                       if v.get("expires_at", 0) <= current_time]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired items from memory cache")
        
        # If still too many items, remove oldest based on expiration time
        if len(self.memory_cache) > self.max_memory_items:
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get("expires_at", 0)
            )
            
            # Remove oldest items to get back to 80% capacity
            items_to_remove = len(self.memory_cache) - int(self.max_memory_items * 0.8)
            removed_count = 0
            
            for i in range(items_to_remove):
                if i < len(sorted_items):
                    del self.memory_cache[sorted_items[i][0]]
                    removed_count += 1
            
            if removed_count > 0:
                logger.debug(f"Removed {removed_count} oldest items from memory cache")
        
        final_size = len(self.memory_cache)
        if initial_size != final_size:
            logger.debug(f"Memory cache cleanup: {initial_size} → {final_size} items")
    
    def invalidate(self, key: str) -> bool:
        """Remove item from in-memory cache"""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            logger.debug(f"Invalidated cache key: {key}")
            return True
        
        logger.debug(f"Cache key not found for invalidation: {key}")
        return False

# Create a decorator for caching function results
def cached(prefix: str, ttl: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine if this is a class method or a regular function
            is_method = args and hasattr(args[0], '__class__')
            
            # Get cache service instance
            cache_service = CachingService()
            
            # Generate cache key
            cache_key = cache_service._generate_key(
                prefix, {"args": args, "kwargs": kwargs}
            )
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator