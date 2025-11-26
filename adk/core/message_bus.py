"""Event-driven communication system for agent coordination."""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
from collections import defaultdict

from ..core.logger import get_logger

logger = get_logger(__name__)


class MessageType(Enum):
    """Types of messages in the system."""
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    STATUS = "status"
    EVENT = "event"


@dataclass
class Message:
    """Message structure for agent communication."""
    message_id: str
    message_type: MessageType
    sender: str
    receiver: Optional[str]  # None for broadcast
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None  # For tracking related messages


class MessageBus:
    """Event-driven message bus for agent communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[Message] = []
        self._max_history: int = 1000
        self._lock = asyncio.Lock()
        logger.info("MessageBus initialized")
    
    async def subscribe(self, agent_id: str, handler: Callable[[Message], None]) -> None:
        """
        Subscribe an agent to receive messages.
        
        Args:
            agent_id: Agent identifier
            handler: Async function to handle messages
        """
        async with self._lock:
            self._subscribers[agent_id].append(handler)
            logger.info("Agent subscribed", agent_id=agent_id)
    
    async def unsubscribe(self, agent_id: str, handler: Callable[[Message], None]) -> None:
        """Unsubscribe an agent from receiving messages."""
        async with self._lock:
            if agent_id in self._subscribers:
                try:
                    self._subscribers[agent_id].remove(handler)
                    logger.info("Agent unsubscribed", agent_id=agent_id)
                except ValueError:
                    pass
    
    async def publish(
        self,
        message_type: MessageType,
        sender: str,
        payload: Dict[str, Any],
        receiver: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Publish a message to the bus.
        
        Args:
            message_type: Type of message
            sender: Sender agent ID
            payload: Message data
            receiver: Target agent ID (None for broadcast)
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Message ID
        """
        import uuid
        message_id = str(uuid.uuid4())
        
        message = Message(
            message_id=message_id,
            message_type=message_type,
            sender=sender,
            receiver=receiver,
            payload=payload,
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id,
        )
        
        async with self._lock:
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history.pop(0)
        
        # Deliver to subscribers
        if receiver:
            # Direct message
            if receiver in self._subscribers:
                await self._deliver_to_subscribers(receiver, message)
        else:
            # Broadcast to all subscribers
            for agent_id in self._subscribers:
                await self._deliver_to_subscribers(agent_id, message)
        
        logger.debug(
            "Message published",
            message_id=message_id,
            sender=sender,
            receiver=receiver or "broadcast",
            message_type=message_type.value,
        )
        
        return message_id
    
    async def _deliver_to_subscribers(self, agent_id: str, message: Message) -> None:
        """Deliver message to all subscribers of an agent."""
        if agent_id in self._subscribers:
            for handler in self._subscribers[agent_id]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(
                        "Error delivering message",
                        agent_id=agent_id,
                        message_id=message.message_id,
                        error=str(e),
                    )
    
    async def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Retrieve message history with optional filters.
        
        Args:
            agent_id: Filter by agent ID
            message_type: Filter by message type
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        async with self._lock:
            messages = self._message_history.copy()
        
        if agent_id:
            messages = [m for m in messages if m.sender == agent_id or m.receiver == agent_id]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]
    
    async def clear_history(self) -> None:
        """Clear message history."""
        async with self._lock:
            self._message_history.clear()
            logger.info("Message history cleared")







