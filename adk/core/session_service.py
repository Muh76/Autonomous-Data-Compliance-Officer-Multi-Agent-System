"""
Session service wrapper for Google ADK InMemorySessionService.
Provides session management and long-term memory integration.
"""

from typing import Dict, Any, Optional, List
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
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to conversation history.
        
        Supports multi-turn conversations with context preservation.
        
        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata (agent name, timestamp, etc.)
        """
        session = await self.get_session(session_id)
        if not session:
            # Create session if it doesn't exist
            session = await self.create_session(session_id)
        
        # Get current state
        state = session.state if hasattr(session, 'state') else {}
        
        # Initialize conversation history if not exists
        if 'conversation_history' not in state:
            state['conversation_history'] = []
        
        # Create message object
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to history
        state['conversation_history'].append(message)
        
        # Update session
        await self.update_session(session_id, state)
        
        logger.debug(
            "Message added to conversation",
            session_id=session_id,
            role=role,
            message_count=len(state['conversation_history'])
        )
    
    async def get_conversation_history(
        self,
        session_id: str,
        max_messages: Optional[int] = None,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages to return
            role_filter: Filter by role ('user', 'assistant', 'system')
            
        Returns:
            List of messages in chronological order
        """
        session = await self.get_session(session_id)
        if not session or not hasattr(session, 'state'):
            return []
        
        history = session.state.get('conversation_history', [])
        
        # Apply role filter if specified
        if role_filter:
            history = [msg for msg in history if msg.get('role') == role_filter]
        
        # Apply max_messages limit (most recent)
        if max_messages and len(history) > max_messages:
            history = history[-max_messages:]
        
        return history
    
    async def get_conversation_context(
        self,
        session_id: str,
        max_tokens: int = 4000,
        include_system: bool = True
    ) -> str:
        """
        Get conversation context as formatted string for LLM.
        
        Implements context window management by truncating old messages.
        
        Args:
            session_id: Session identifier
            max_tokens: Approximate max tokens (rough estimate: 4 chars = 1 token)
            include_system: Whether to include system messages
            
        Returns:
            Formatted conversation context
        """
        history = await self.get_conversation_history(session_id)
        
        # Filter out system messages if requested
        if not include_system:
            history = [msg for msg in history if msg.get('role') != 'system']
        
        # Build context string
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough estimate
        
        # Add messages from most recent backwards
        for msg in reversed(history):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            msg_text = f"{role.upper()}: {content}\n\n"
            msg_chars = len(msg_text)
            
            if total_chars + msg_chars > max_chars:
                # Would exceed limit, stop here
                break
            
            context_parts.insert(0, msg_text)
            total_chars += msg_chars
        
        context = "".join(context_parts)
        
        logger.debug(
            "Generated conversation context",
            session_id=session_id,
            messages_included=len(context_parts),
            total_chars=total_chars
        )
        
        return context
    
    async def clear_conversation_history(
        self,
        session_id: str,
        keep_last_n: int = 0
    ) -> None:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
            keep_last_n: Number of recent messages to keep (0 = clear all)
        """
        session = await self.get_session(session_id)
        if not session or not hasattr(session, 'state'):
            return
        
        state = session.state
        
        if 'conversation_history' in state:
            if keep_last_n > 0:
                state['conversation_history'] = state['conversation_history'][-keep_last_n:]
            else:
                state['conversation_history'] = []
            
            await self.update_session(session_id, state)
            logger.info(
                "Conversation history cleared",
                session_id=session_id,
                kept_messages=keep_last_n
            )
    
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
        Get session history (legacy method for backward compatibility).
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of historical events
        """
        session = await self.get_session(session_id)
        if session and hasattr(session, 'state'):
            return session.state.get('history', [])
        return []
