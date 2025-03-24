from typing import List, Dict, Optional
from langchain_community.llms import Ollama
from ..embeddings.vector_store import VectorStoreManager

class RAGChain:
    def __init__(
        self,
        vector_store: VectorStoreManager,
        max_tokens=None,
        context_window=None,
        system_prompt=
        """
        You are an AI assistant helping with IT platform support issues. Your responses should be clear, concise, and well-structured.

        When providing resolutions:
        1. Format each issue title as a level 2 heading (##)
        2. Include an "Impact Level" tag (High/Medium/Low)
        3. Use clear section headings for:
        - Resolution Steps (as a numbered list)
        - Knowledge Base Reference (with proper markdown links)

        For similar but distinct issues:
        - Keep them as separate sections
        - Highlight key differences in their nature or resolution
        - Use horizontal rules (---) to separate them
        - Include specific details that make each issue unique

        Example format:
        ## Database Connection Pool Exhaustion - Primary DB (Impact Level: High)

        ### Resolution Steps:
        1. Check current connection pool metrics
        2. Identify connection leaks
        3. Implement connection timeout
        4. Verify pool size configuration
        5. Monitor for improvements

        ### Knowledge Base Reference:
        [Connection Pool Best Practices](kb-link)

        ---

        ## Database Connection Pool Exhaustion - Replica DB (Impact Level: Medium)
        [... different steps for replica DB ...]

        Remember:
        - Remove exact duplicates but keep similar issues that require different handling
        - Use only information from the provided context
        - If no relevant information is found, say so clearly."""
    ):
        """Initialize the RAG chain.
        
        Args:
            vector_store (VectorStoreManager): Vector store for document retrieval
            max_tokens (int, optional): Maximum number of tokens to generate
            context_window (int, optional): Maximum number of tokens in the context window
            system_prompt (str, optional): Custom system prompt
        """
        self.vector_store = vector_store
        self.max_tokens = max_tokens
        self.context_window = context_window
        
        # Initialize Ollama with configurable parameters
        self.llm = Ollama(
            model="mistral",
            temperature=0.7
        )
        
        self.system_prompt = system_prompt

    def _format_context(self, documents: List[Dict]) -> str:
        """Format the context documents for the LLM."""
        # Only deduplicate exact matches, keeping similar but distinct issues
        seen_contents = set()
        unique_docs = []
        
        for doc in documents:
            # Create a normalized version of the content for exact match comparison
            # This will only match if the content is exactly the same (ignoring case and whitespace)
            normalized_content = ' '.join(doc['content'].strip().lower().split())
            
            # Skip only if it's an exact duplicate
            if normalized_content in seen_contents:
                continue
                
            seen_contents.add(normalized_content)
            unique_docs.append(doc)
        
        # Format the unique documents
        context_parts = []
        for i, doc in enumerate(unique_docs, 1):
            source = doc["metadata"].get("source", "Unknown")
            chunk_size = doc["metadata"].get("chunk_size", "Unknown")
            chunk_overlap = doc["metadata"].get("chunk_overlap", "Unknown")
            context_parts.append(
                f"Document {i} (from {source}, chunk_size={chunk_size}, chunk_overlap={chunk_overlap}):\n{doc['content']}\n"
            )
        return "\n".join(context_parts)

    async def query(self, query: str, num_docs: Optional[int] = None) -> Dict:
        """Process a query through the RAG chain.
        
        Args:
            query (str): The query to process
            num_docs (int, optional): Override the default number of context documents
        """
        # Retrieve relevant documents
        k = 4 if num_docs is None else num_docs
        relevant_docs = self.vector_store.similarity_search(query, k=k)
        
        if not relevant_docs:
            return {
                "response": "I don't have any relevant information in my knowledge base to answer this query.",
                "sources": []
            }

        # Format context and create prompt
        context = self._format_context(relevant_docs)
        prompt = self._create_prompt(query, context)
        
        # Generate response
        response = await self.llm.ainvoke(prompt)
        
        # Return response with sources
        sources = [
            {
                "source": doc["metadata"].get("source", "Unknown"),
                "score": doc.get("score", 0.0),
                "chunk_size": doc["metadata"].get("chunk_size", "Unknown"),
                "chunk_overlap": doc["metadata"].get("chunk_overlap", "Unknown")
            }
            for doc in relevant_docs
        ]

        return {
            "response": response,
            "sources": sources
        }

    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM."""
        return f"""{self.system_prompt}

    Context:{context}

    Question/Incident: {query}

    Please provide a clear, step-by-step response. If there are multiple similar but distinct issues:
    1. Keep them separate and clearly labeled
    2. Highlight the key differences between them
    3. Present each with its own resolution steps
    4. Use "---" to separate different issues
    """ 