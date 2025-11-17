"""Centralized state management with JSON file persistence (SIMPLIFIED)."""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json
from pathlib import Path
from collections import defaultdict

from ..core.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Manages shared state across agents with JSON file persistence."""
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to JSON file for persistence (default: ./data/state.json)
        """
        self._state: Dict[str, Any] = {}
        self._agent_contexts: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._task_states: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        # JSON file persistence
        if state_file is None:
            state_file = "./data/state.json"
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self._load_state()
        
        logger.info("StateManager initialized", state_file=str(self.state_file))
    
    def _load_state(self) -> None:
        """Load state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self._state = data.get("state", {})
                    self._agent_contexts = data.get("agent_contexts", {})
                    self._task_states = data.get("task_states", {})
                logger.info("State loaded from file", state_file=str(self.state_file))
            except Exception as e:
                logger.warning("Failed to load state", error=str(e))
    
    def _save_state(self) -> None:
        """Save state to JSON file."""
        try:
            data = {
                "state": self._state,
                "agent_contexts": dict(self._agent_contexts),
                "task_states": self._task_states,
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("State saved to file", state_file=str(self.state_file))
        except Exception as e:
            logger.error("Failed to save state", error=str(e))
    
    async def set_state(self, key: str, value: Any) -> None:
        """
        Set a global state value.
        
        Args:
            key: State key
            value: State value (must be JSON serializable)
        """
        async with self._lock:
            self._state[key] = {
                "value": value,
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._save_state()
            logger.debug("State updated", key=key)
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a global state value.
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            State value or default
        """
        async with self._lock:
            state_entry = self._state.get(key)
            if state_entry:
                return state_entry.get("value", default)
            return default
    
    async def delete_state(self, key: str) -> bool:
        """
        Delete a global state value.
        
        Args:
            key: State key
            
        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if key in self._state:
                del self._state[key]
                self._save_state()
                logger.debug("State deleted", key=key)
                return True
            return False
    
    async def set_agent_context(self, agent_id: str, key: str, value: Any) -> None:
        """
        Set context for a specific agent.
        
        Args:
            agent_id: Agent identifier
            key: Context key
            value: Context value (must be JSON serializable)
        """
        async with self._lock:
            self._agent_contexts[agent_id][key] = {
                "value": value,
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._save_state()
            logger.debug("Agent context updated", agent_id=agent_id, key=key)
    
    async def get_agent_context(self, agent_id: str, key: str, default: Any = None) -> Any:
        """
        Get context for a specific agent.
        
        Args:
            agent_id: Agent identifier
            key: Context key
            default: Default value if key doesn't exist
            
        Returns:
            Context value or default
        """
        async with self._lock:
            if agent_id in self._agent_contexts:
                context_entry = self._agent_contexts[agent_id].get(key)
                if context_entry:
                    return context_entry.get("value", default)
            return default
    
    async def set_task_state(self, task_id: str, state: Dict[str, Any]) -> None:
        """
        Set state for a specific task.
        
        Args:
            task_id: Task identifier
            state: Task state dictionary (must be JSON serializable)
        """
        async with self._lock:
            self._task_states[task_id] = {
                **state,
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._save_state()
            logger.debug("Task state updated", task_id=task_id)
    
    async def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state for a specific task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task state dictionary or None
        """
        async with self._lock:
            return self._task_states.get(task_id)
    
    async def clear_agent_context(self, agent_id: str) -> None:
        """
        Clear all context for an agent.
        
        Args:
            agent_id: Agent identifier
        """
        async with self._lock:
            if agent_id in self._agent_contexts:
                del self._agent_contexts[agent_id]
                self._save_state()
                logger.info("Agent context cleared", agent_id=agent_id)
    
    async def get_all_state(self) -> Dict[str, Any]:
        """Get all global state."""
        async with self._lock:
            return {k: v.get("value") for k, v in self._state.items()}
    
    async def clear_all_state(self) -> None:
        """Clear all state."""
        async with self._lock:
            self._state.clear()
            self._agent_contexts.clear()
            self._task_states.clear()
            self._save_state()
            logger.info("All state cleared")
