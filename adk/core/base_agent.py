"""Lightweight base class for shared utilities (logging, typing) - NOT full agent implementation.

This is a minimal base class for shared functionality. 
For full agent implementations, use ADK agent classes or extend this minimally.
"""

from typing import Dict, Any, Optional
import uuid

from ..core.logger import get_logger
from ..core.message_bus import MessageBus, MessageType
from ..core.state_manager import StateManager
from ..core.task_queue import TaskQueue

logger = get_logger(__name__)


class BaseAgent:
    """
    Lightweight base class for shared agent utilities.
    
    This provides minimal shared functionality:
    - Logging with agent context
    - Basic message bus integration
    - State management helpers
    - Agent identification
    
    For full agent functionality, use ADK agent classes or implement custom agents.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        message_bus: Optional[MessageBus] = None,
        state_manager: Optional[StateManager] = None,
        task_queue: Optional[TaskQueue] = None,
    ):
        """
        Initialize the base agent with shared utilities.
        
        Args:
            agent_id: Unique agent identifier
            message_bus: Message bus for communication (optional)
            state_manager: State manager for shared state (optional)
            task_queue: Task queue for task management (optional)
        """
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.agent_type = self.__class__.__name__.lower().replace("agent", "")
        self.message_bus = message_bus
        self.state_manager = state_manager
        self.task_queue = task_queue
        self.logger = get_logger(self.__class__.__name__, agent_id=self.agent_id)
        
        self.logger.info("Base agent utilities initialized", agent_type=self.agent_type)
    
    async def initialize(self) -> None:
        """Initialize the agent (async hook)."""
        self.logger.info("Agent initializing", agent_id=self.agent_id)
    
    async def send_message(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        receiver: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send a message via the message bus (if available).
        
        Args:
            message_type: Type of message
            payload: Message data
            receiver: Target agent ID (None for broadcast)
            correlation_id: Optional correlation ID
            
        Returns:
            Message ID
        """
        if not self.message_bus:
            raise RuntimeError("Message bus not available")
        
        return await self.message_bus.publish(
            message_type=message_type,
            sender=self.agent_id,
            payload=payload,
            receiver=receiver,
            correlation_id=correlation_id,
        )
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get global state value (if state manager available)."""
        if not self.state_manager:
            return default
        return await self.state_manager.get_state(key, default)
    
    async def set_state(self, key: str, value: Any) -> None:
        """Set global state value (if state manager available)."""
        if self.state_manager:
            await self.state_manager.set_state(key, value)
    
    async def get_context(self, key: str, default: Any = None) -> Any:
        """Get agent-specific context (if state manager available)."""
        if not self.state_manager:
            return default
        return await self.state_manager.get_agent_context(self.agent_id, key, default)
    
    async def set_context(self, key: str, value: Any) -> None:
        """Set agent-specific context (if state manager available)."""
        if self.state_manager:
            await self.state_manager.set_agent_context(self.agent_id, key, value)
