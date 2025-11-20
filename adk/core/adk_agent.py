"""
ADK-based agent wrapper for ADCO system.
Integrates Google Agent Development Kit with existing infrastructure.
"""

from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, Session

# Existing infrastructure
from ..core.logger import get_logger
from ..core.message_bus import MessageBus, MessageType
from ..core.state_manager import StateManager
from ..core.task_queue import TaskQueue
from ..tools.llm_client import get_llm_client

logger = get_logger(__name__)


class ADKAgent(Agent):
    """
    ADK-based agent that integrates with ADCO infrastructure.
    
    This class bridges Google ADK's Agent with our existing:
    - Message bus for inter-agent communication
    - State manager for shared state
    - Task queue for async operations
    - LLM client for Vertex AI integration
    """
    
    def __init__(
        self,
        name: str,
        session_service: Optional[InMemorySessionService] = None,
        message_bus: Optional[MessageBus] = None,
        state_manager: Optional[StateManager] = None,
        task_queue: Optional[TaskQueue] = None,
    ):
        """
        Initialize ADK agent with ADCO infrastructure.
        
        Args:
            name: Agent name (e.g., "RiskScanner", "PolicyMatcher")
            session_service: ADK session service for memory management
            message_bus: Message bus for inter-agent communication
            state_manager: State manager for shared state
            task_queue: Task queue for async operations
        """
        # Initialize ADK Agent
        super().__init__(name=name)
        
        # Store ADCO-specific attributes in a separate dict to avoid Pydantic validation
        self._adco_context = {
            "agent_id": f"{name}_{uuid.uuid4().hex[:8]}",
            "session_service": session_service or InMemorySessionService(),
            "message_bus": message_bus,
            "state_manager": state_manager,
            "task_queue": task_queue,
            "llm_client": None,
            "logger": get_logger(self.__class__.__name__, agent_id=f"{name}_{uuid.uuid4().hex[:8]}")
        }
        
        self._adco_context["logger"].info("ADK agent initialized", agent_name=name)
    
    
    # Property accessors for ADCO context
    @property
    def agent_id(self):
        return self._adco_context["agent_id"]
    
    @property
    def session_service(self):
        return self._adco_context["session_service"]
    
    @property
    def message_bus(self):
        return self._adco_context["message_bus"]
    
    @property
    def state_manager(self):
        return self._adco_context["state_manager"]
    
    @property
    def task_queue(self):
        return self._adco_context["task_queue"]
    
    @property
    def llm_client(self):
        return self._adco_context["llm_client"]
    
    @llm_client.setter
    def llm_client(self, value):
        self._adco_context["llm_client"] = value
    
    @property
    def logger(self):
        return self._adco_context["logger"]
    
    async def initialize(self) -> None:
        """Initialize agent resources (LLM client, etc.)."""
        try:
            self.llm_client = get_llm_client()
            self.logger.info("LLM client initialized")
        except Exception as e:
            self.logger.warning("LLM client not available", error=str(e))
        
        self.logger.info("Agent initialization complete", agent_id=self.agent_id)
    
    async def process(
        self,
        input_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process input with session context.
        
        This is the main entry point that:
        1. Retrieves session context
        2. Executes agent logic (via run method)
        3. Updates session with results
        4. Sends messages to other agents
        
        Args:
            input_data: Input data for processing
            session_id: Session ID for context retrieval
            
        Returns:
            Processing result
        """
        # Create or retrieve session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = await self._get_or_create_session(session_id)
        
        # Add session context to input
        input_with_context = {
            **input_data,
            "session_context": session.state if hasattr(session, 'state') else {}
        }
        
        # Execute agent logic
        self.logger.info("Processing request", session_id=session_id)
        result = await self.run(input_with_context)
        
        # Update session with result
        await self._update_session(session_id, result)
        
        # Notify other agents via message bus
        if self.message_bus:
            await self.send_message(
                MessageType.RESULT,
                result,
                receiver="coordinator"
            )
        
        return result
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent-specific logic (to be overridden by subclasses).
        
        Args:
            input_data: Input data with session context
            
        Returns:
            Processing result
        """
        raise NotImplementedError("Subclasses must implement run method")
    
    async def _get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one."""
        try:
            session = await self.session_service.get_session(session_id)
            if not session:
                session = await self.session_service.create_session(
                    session_id=session_id,
                    state={"created_at": datetime.utcnow().isoformat()}
                )
            return session
        except Exception as e:
            self.logger.error("Session retrieval failed", error=str(e))
            # Create a minimal session object for fallback
            from google.adk.sessions import Session
            return Session(
                id=session_id,
                appName="ADCO",
                userId="system",
                state={}
            )
    
    async def _update_session(self, session_id: str, result: Dict[str, Any]) -> None:
        """Update session with processing result."""
        try:
            session = await self.session_service.get_session(session_id)
            if session:
                # Append result to session history
                if not hasattr(session, 'state'):
                    session.state = {}
                
                if 'history' not in session.state:
                    session.state['history'] = []
                
                session.state['history'].append({
                    "agent": self.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                })
                
                await self.session_service.update_session(session_id, session.state)
        except Exception as e:
            self.logger.error("Session update failed", error=str(e))
    
    async def send_message(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        receiver: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send message via message bus.
        
        Args:
            message_type: Type of message
            payload: Message data
            receiver: Target agent ID (None for broadcast)
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Message ID
        """
        if not self.message_bus:
            self.logger.warning("Message bus not available")
            return ""
        
        return await self.message_bus.publish(
            message_type=message_type,
            sender=self.agent_id,
            payload=payload,
            receiver=receiver,
            correlation_id=correlation_id,
        )
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get global state value."""
        if not self.state_manager:
            return default
        return await self.state_manager.get_state(key, default)
    
    async def set_state(self, key: str, value: Any) -> None:
        """Set global state value."""
        if self.state_manager:
            await self.state_manager.set_state(key, value)
    
    async def get_context(self, key: str, default: Any = None) -> Any:
        """Get agent-specific context."""
        if not self.state_manager:
            return default
        return await self.state_manager.get_agent_context(self.agent_id, key, default)
    
    async def set_context(self, key: str, value: Any) -> None:
        """Set agent-specific context."""
        if self.state_manager:
            await self.state_manager.set_agent_context(self.agent_id, key, value)
