"""
Session service wrapper for Google ADK InMemorySessionService.
Provides session management and long-term memory integration.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from google.adk.sessions import InMemorySessionService, Session

from ..core.logger import get_logger
from ..rag.vector_store import VectorStore, get_vector_store

logger = get_logger(__name__)


class ADCOSessionService:
    """
    Enhanced session service with long-term memory.
    
    Combines ADK's InMemorySessionService with ChromaDB for:
    - Short-term memory: Session state (in-memory)
    - Long-term memory: Historical reports (ChromaDB)
    """
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize session service.
        
        Args:
            vector_store: Vector store for long-term memory (defaults to ChromaDB)
        """
        self.session_service = InMemorySessionService()
        self.vector_store = vector_store or get_vector_store()
        self.memory_collection = "session_memory"
        
        logger.info("ADCO Session Service initialized")
    
    async def create_session(
        self,
        session_id: str,
        state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create new session.
        
        Args:
            session_id: Unique session identifier
            state: Initial session state
            
        Returns:
            Created session
        """
        initial_state = state or {}
        initial_state["created_at"] = datetime.utcnow().isoformat()
        initial_state["history"] = []
        
        # ADK Session requires specific fields
        session = await self.session_service.create_session(
            id=session_id,
            appName="ADCO",
            userId="system",
            state=initial_state
        )
        
        logger.info("Session created", session_id=session_id)
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if exists, None otherwise
        """
        return await self.session_service.get_session(session_id)
    
    async def update_session(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            state: Updated state
        """
        await self.session_service.update_session(session_id, state)
        logger.debug("Session updated", session_id=session_id)
    
    async def delete_session(self, session_id: str) -> None:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        """
        await self.session_service.delete_session(session_id)
        logger.info("Session deleted", session_id=session_id)
    
    async def store_in_long_term_memory(
        self,
        session_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store session data in long-term memory (ChromaDB).
        
        Args:
            session_id: Session identifier
            content: Content to store
            metadata: Associated metadata
        """
        try:
            memory_id = f"{session_id}_{datetime.utcnow().timestamp()}"
            metadata["session_id"] = session_id
            metadata["stored_at"] = datetime.utcnow().isoformat()
            
            await self.vector_store.add_documents(
                texts=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            logger.info("Stored in long-term memory", session_id=session_id)
        except Exception as e:
            logger.error("Failed to store in long-term memory", error=str(e))
    
    async def recall_from_long_term_memory(
        self,
        query: str,
        top_k: int = 5
    ) -> list:
        """
        Recall similar memories from long-term storage.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar memories
        """
        try:
            results = await self.vector_store.search(query, top_k=top_k)
            logger.info("Recalled from long-term memory", count=len(results))
            return results
        except Exception as e:
            logger.error("Failed to recall from long-term memory", error=str(e))
            return []
    
    async def get_session_history(self, session_id: str) -> list:
        """
        Get session history.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of historical events
        """
        session = await self.get_session(session_id)
        if session and hasattr(session, 'state'):
            return session.state.get('history', [])
        return []
