"""
Performance caching layer for ADCO system.
Reduces redundant LLM calls and database queries.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import asyncio

from adk.core.logger import get_logger

logger = get_logger(__name__)


class CacheEntry:
    """Represents a cached entry with TTL."""
    
    def __init__(self, value: Any, ttl: int = 3600):
        """
        Initialize cache entry.
        
        Args:
            value: Cached value
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > self.ttl
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds."""
        return time.time() - self.created_at


class PerformanceCache:
    """
    In-memory cache for performance optimization.
    
    Features:
    - TTL-based expiration
    - LRU eviction
    - Hit/miss statistics
    - Async support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info("Cache initialized", max_size=max_size, default_ttl=default_ttl)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache:
            entry = self.cache[key]
            
            if entry.is_expired():
                # Remove expired entry
                del self.cache[key]
                self.misses += 1
                logger.debug("Cache miss (expired)", key=key[:8])
                return None
            
            self.hits += 1
            logger.debug("Cache hit", key=key[:8], age=f"{entry.get_age():.1f}s")
            return entry.value
        
        self.misses += 1
        logger.debug("Cache miss", key=key[:8])
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL
        """
        # Evict if at max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(value, ttl)
        logger.debug("Cache set", key=key[:8], ttl=ttl)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find oldest entry
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        del self.cache[oldest_key]
        self.evictions += 1
        logger.debug("Cache eviction (LRU)", key=oldest_key[:8])
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self.cache)
        self.cache.clear()
        logger.info("Cache cleared", entries_removed=count)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def decorator(self, ttl: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Optional custom TTL
            
        Example:
            @cache.decorator(ttl=600)
            async def expensive_function(arg1, arg2):
                return result
        """
        def wrapper(func: Callable):
            @wraps(func)
            async def async_wrapped(*args, **kwargs):
                # Generate cache key
                key = self._generate_key(func.__name__, *args, **kwargs)
                
                # Check cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Call function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.set(key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapped(*args, **kwargs):
                # Generate cache key
                key = self._generate_key(func.__name__, *args, **kwargs)
                
                # Check cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Call function
                result = func(*args, **kwargs)
                
                # Cache result
                self.set(key, result, ttl)
                
                return result
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapped
            else:
                return sync_wrapped
        
        return wrapper


# Global cache instance
_global_cache: Optional[PerformanceCache] = None


def get_cache() -> PerformanceCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = PerformanceCache(max_size=1000, default_ttl=3600)
    return _global_cache


# Example usage decorators
def cache_llm_response(ttl: int = 3600):
    """Cache LLM responses (1 hour default)."""
    return get_cache().decorator(ttl=ttl)


def cache_rag_results(ttl: int = 1800):
    """Cache RAG retrieval results (30 minutes default)."""
    return get_cache().decorator(ttl=ttl)


def cache_compliance_check(ttl: int = 7200):
    """Cache compliance check results (2 hours default)."""
    return get_cache().decorator(ttl=ttl)
