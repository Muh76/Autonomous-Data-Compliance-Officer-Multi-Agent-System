"""Load and index regulation documents."""

from typing import List, Dict, Any
from pathlib import Path
import uuid

from ..rag.vector_store import VectorStore, get_vector_store
from ..rag.embeddings import EmbeddingGenerator, get_embedding_generator
from ..core.logger import get_logger

logger = get_logger(__name__)


class RegulationLoader:
    """Load and index regulation documents."""
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        embedding_generator: EmbeddingGenerator = None
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_generator = embedding_generator or get_embedding_generator()
        logger.info("RegulationLoader initialized")
    
    async def load_from_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Load a regulation from text.
        
        Args:
            text: Regulation text
            metadata: Regulation metadata
            
        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())
        
        await self.vector_store.add_documents(
            texts=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.info("Regulation loaded", doc_id=doc_id, name=metadata.get("name"))
        return doc_id
    
    async def load_from_file(self, file_path: Path, metadata: Dict[str, Any] = None) -> str:
        """
        Load a regulation from a file.
        
        Args:
            file_path: Path to regulation file
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Regulation file not found: {file_path}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "source_file": str(file_path),
            "file_name": file_path.name,
        })
        
        return await self.load_from_text(text, metadata)
    
    async def load_directory(self, directory: Path, pattern: str = "*.txt") -> List[str]:
        """
        Load all regulations from a directory.
        
        Args:
            directory: Directory containing regulation files
            pattern: File pattern to match
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for file_path in directory.glob(pattern):
            try:
                doc_id = await self.load_from_file(file_path)
                doc_ids.append(doc_id)
            except Exception as e:
                logger.error("Failed to load regulation file", file=str(file_path), error=str(e))
        
        logger.info("Regulations loaded from directory", directory=str(directory), count=len(doc_ids))
        return doc_ids







