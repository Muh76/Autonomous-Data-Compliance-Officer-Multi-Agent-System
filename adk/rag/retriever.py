"""Semantic search for regulations."""

from typing import List, Dict, Any
from ..rag.vector_store import VectorStore, get_vector_store
from ..rag.embeddings import EmbeddingGenerator, get_embedding_generator
from ..core.logger import get_logger

logger = get_logger(__name__)


class Retriever:
    """Retriever for semantic search of regulations."""
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        embedding_generator: EmbeddingGenerator = None
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_generator = embedding_generator or get_embedding_generator()
        logger.info("Retriever initialized")
    
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant regulations for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant regulation documents
        """
        results = await self.vector_store.search(query, top_k=top_k)
        logger.info("Regulations retrieved", query=query, count=len(results))
        return results
    
    async def retrieve_relevant(
        self,
        data_practice: str,
        context: Dict[str, Any] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant regulations for a data practice.
        
        Args:
            data_practice: Description of the data practice
            context: Additional context
            top_k: Number of results to return
            
        Returns:
            List of relevant regulation documents
        """
        # Build enhanced query
        query = data_practice
        if context:
            query += f" Context: {context.get('description', '')}"
        
        return await self.retrieve(query, top_k=top_k)

