from typing import Dict, Optional, Any
from .rag_pipeline import RAGChain
from ..utils.redis_cache import RedisCacheManager
from ..utils.pydantic_classes import ContextMetadata, ModelContext

class ModelContextProtocol:
    """Implements the Model Context Protocol for enhanced RAG."""
    
    def __init__(
        self,
        rag_chain: RAGChain,
        max_context_documents: int = 4,
        context_window_size: int = 2000,
        use_cache: bool = True,
        cache_ttl: int = 3600
    ):
        """Initialize the Model Context Protocol.
        
        Args:
            rag_chain (RAGChain): The RAG chain instance
            max_context_documents (int): Maximum number of context documents to include
            context_window_size (int): Maximum size of the context window in tokens
            use_cache (bool): Whether to use Redis caching
            cache_ttl (int): Time-to-live for cached contexts in seconds
        """
        self.rag_chain = rag_chain
        self.max_context_documents = max_context_documents
        self.context_window_size = context_window_size
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Initialize Redis cache if enabled
        self.cache_manager = RedisCacheManager(default_ttl=cache_ttl) if use_cache else None

    def _create_context_metadata(self, doc: Dict) -> ContextMetadata:
        """Create metadata for a context document."""
        return ContextMetadata(
            source=doc.get("source", "Unknown"),
            relevance_score=doc.get("score", 0.0),
            chunk_info={
                "size": doc.get("chunk_size", "Unknown"),
                "overlap": doc.get("chunk_overlap", "Unknown")
            }
        )

    def _format_context_for_model(self, context: ModelContext) -> str:
        """Format the context for the model input."""
        context_parts = [
            "=== System Instructions ===\n",
            self.rag_chain.system_prompt,
            "\n=== Original Query ===\n",
            context.original_query,
            "\n=== Retrieved Context ===\n"
        ]
        
        for i, (doc, metadata) in enumerate(zip(context.retrieved_documents, context.metadata), 1):
            context_parts.append(
                f"Document {i} (Source: {metadata.source}, Relevance: {metadata.relevance_score:.2f}):\n"
                f"{doc['content']}\n"
            )
        
        if context.additional_context:
            context_parts.append("\n=== Additional Context ===\n")
            for key, value in context.additional_context.items():
                context_parts.append(f"{key}: {value}\n")
        
        return "\n".join(context_parts)

    async def process_query(
        self,
        query: str,
        additional_context: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Process a query using the Model Context Protocol.
        
        Args:
            query (str): The original query
            additional_context (Dict, optional): Additional context to include
            force_refresh (bool): Whether to force a refresh of the cache
            
        Returns:
            Dict containing the response and context information
        """
        # Check cache first if enabled and not forcing refresh
        if self.use_cache and not force_refresh:
            cached_result = await self.cache_manager.get_cached_context(query, additional_context)
            if cached_result:
                return cached_result

        # Retrieve relevant documents using RAG
        rag_result = await self.rag_chain.query(query, num_docs=self.max_context_documents)
        # Create context metadata
        context_metadata = [
            self._create_context_metadata(doc)
            for doc in rag_result["sources"]
        ]
        # Create model context
        model_context = ModelContext(
            original_query=query,
            retrieved_documents=rag_result["sources"],
            metadata=context_metadata,
            additional_context=additional_context
        )
        
        # Format context for model
        formatted_context = self._format_context_for_model(model_context)
        
        # Generate response using the formatted context
        response = await self.rag_chain.llm.ainvoke(formatted_context)
        
        result = {
            "response": response,
            "context": {
                "original_query": query,
                "retrieved_documents": rag_result["sources"],
                "metadata": [vars(m) for m in context_metadata],
                "additional_context": additional_context
            }
        }

        # Cache the result if enabled
        if self.use_cache:
            await self.cache_manager.cache_context(
                query=query,
                context_data=result,
                additional_context=additional_context,
                ttl=self.cache_ttl
            )

        return result

    async def invalidate_cache(self, query: str, additional_context: Optional[Dict] = None) -> bool:
        """Invalidate cached context for a specific query.
        
        Args:
            query (str): The query to invalidate cache for
            additional_context (Dict, optional): Additional context
            
        Returns:
            bool: True if invalidation was successful
        """
        if self.use_cache:
            return await self.cache_manager.invalidate_cache(query, additional_context)
        return False

    async def clear_all_cache(self) -> bool:
        """Clear all cached contexts.
        
        Returns:
            bool: True if clearing was successful
        """
        if self.use_cache:
            return await self.cache_manager.clear_all_cache()
        return False 