import asyncio
from typing import Dict, Optional
from ..embeddings.vector_store import VectorStoreManager
from .rag_pipeline import RAGChain
from .model_context_protocol import ModelContextProtocol
from ..utils.redis_cache import RedisCacheManager
vstoreindex_directory = 'backend/vstore_artifacts'

class IntegratedRAGSystem:
    """Complete integration of RAG, Model Context Protocol, and Redis caching."""
    
    def __init__(
        self,
        use_cache: bool = True,
        cache_ttl: int = 3600,
        max_context_documents: int = 4,
        context_window_size: int = 2000
    ):
        """Initialize the integrated system.
        
        Args:
            use_cache (bool): Whether to use Redis caching
            cache_ttl (int): Cache time-to-live in seconds
            max_context_documents (int): Maximum number of context documents
            context_window_size (int): Maximum context window size
        """
        # Initialize core components
        self.vector_store = VectorStoreManager()
        self.vector_store.load(vstoreindex_directory)
        self.rag_chain = RAGChain(
            vector_store=self.vector_store,
            max_tokens=context_window_size
        )
        
        # Initialize Model Context Protocol with caching
        self.context_protocol = ModelContextProtocol(
            rag_chain=self.rag_chain,
            max_context_documents=max_context_documents,
            context_window_size=context_window_size,
            use_cache=use_cache,
            cache_ttl=cache_ttl
        )
        
        # Initialize Redis cache manager if caching is enabled
        self.cache_manager = RedisCacheManager(default_ttl=cache_ttl) if use_cache else None

    async def process_query(
        self,
        query: str,
        additional_context: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> Dict:
        """Process a query through the complete pipeline.
        
        Args:
            query (str): The query to process
            additional_context (Dict, optional): Additional context
            force_refresh (bool): Whether to force cache refresh
            
        Returns:
            Dict containing the response and context information
        """
        # Process query through Model Context Protocol
        result = await self.context_protocol.process_query(
            query=query,
            additional_context=additional_context,
            force_refresh=force_refresh
        )
        
        return result

    async def invalidate_cache(self, query: str, additional_context: Optional[Dict] = None) -> bool:
        """Invalidate cache for a specific query."""
        return await self.context_protocol.invalidate_cache(query, additional_context)

    async def clear_all_cache(self) -> bool:
        """Clear all cached contexts."""
        return await self.context_protocol.clear_all_cache()
