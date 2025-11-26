"""Vector store integration for regulation storage and retrieval."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import os

from ..config import get_config
from ..core.logger import get_logger

logger = get_logger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        pass


class ChromaVectorStore(VectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(self, persist_dir: str = "./data/chroma_db", collection_name: str = "regulations"):
        try:
            import chromadb
            from chromadb.config import Settings
            
            os.makedirs(persist_dir, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB vector store initialized", collection=collection_name)
        except ImportError:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
    
    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Add documents to ChromaDB."""
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("Documents added to vector store", count=len(texts))
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "id": results["ids"][0][i] if results["ids"] else None,
                })
        
        return documents
    
    async def delete(self, ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        self.collection.delete(ids=ids)
        logger.info("Documents deleted from vector store", count=len(ids))


def get_vector_store() -> VectorStore:
    """
    Get vector store based on configuration.
    
    Returns:
        Vector store instance
    """
    config = get_config()
    vs_config = config.get("vector_store", {})
    
    store_type = vs_config.get("type", "chroma")
    
    if store_type == "chroma":
        persist_dir = vs_config.get("chroma_persist_dir", "./data/chroma_db")
        return ChromaVectorStore(persist_dir=persist_dir)
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")







