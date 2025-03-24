import json
import redis
from typing import Optional, Dict, Any
from datetime import timedelta

class RedisCacheManager:
    """Manages caching of model context using Redis."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600  # 1 hour default TTL
    ):
        """Initialize Redis cache manager.
        
        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis database number
            password (str, optional): Redis password
            default_ttl (int): Default time-to-live in seconds
        """
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # Automatically decode responses to strings
        )
        self.default_ttl = default_ttl

    def _generate_cache_key(self, query: str, additional_context: Optional[Dict] = None) -> str:
        """Generate a unique cache key for the query and context."""
        # Create a deterministic string representation of the context
        context_str = json.dumps(additional_context, sort_keys=True) if additional_context else ""
        # Combine query and context to create a unique key
        combined = f"{query}:{context_str}"
        # Create a hash of the combined string
        return f"model_context:{hash(combined)}"

    async def get_cached_context(self, query: str, additional_context: Optional[Dict] = None) -> Optional[Dict]:
        """Retrieve cached model context.
        
        Args:
            query (str): The original query
            additional_context (Dict, optional): Additional context
            
        Returns:
            Optional[Dict]: Cached context if found, None otherwise
        """
        cache_key = self._generate_cache_key(query, additional_context)
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None

    async def cache_context(
        self,
        query: str,
        context_data: Dict[str, Any],
        additional_context: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache model context data.
        
        Args:
            query (str): The original query
            context_data (Dict): The context data to cache
            additional_context (Dict, optional): Additional context
            ttl (int, optional): Time-to-live in seconds
            
        Returns:
            bool: True if caching was successful
        """
        try:
            cache_key = self._generate_cache_key(query, additional_context)
            ttl = ttl or self.default_ttl
            
            # Store the context data with TTL
            self.redis_client.setex(
                cache_key,
                timedelta(seconds=ttl),
                json.dumps(context_data)
            )
            return True
        except Exception as e:
            print(f"Error caching context: {e}")
            return False

    async def invalidate_cache(self, query: str, additional_context: Optional[Dict] = None) -> bool:
        """Invalidate cached context for a specific query.
        
        Args:
            query (str): The original query
            additional_context (Dict, optional): Additional context
            
        Returns:
            bool: True if invalidation was successful
        """
        try:
            cache_key = self._generate_cache_key(query, additional_context)
            self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            print(f"Error invalidating cache: {e}")
            return False

    async def clear_all_cache(self) -> bool:
        """Clear all cached model contexts.
        
        Returns:
            bool: True if clearing was successful
        """
        try:
            # Delete all keys matching the model_context pattern
            keys = self.redis_client.keys("model_context:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False 