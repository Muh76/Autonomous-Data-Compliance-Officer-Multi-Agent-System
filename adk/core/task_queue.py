"""Local Python queue for task distribution (SIMPLIFIED - not distributed)."""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import uuid

from ..core.logger import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Task structure."""
    task_id: str
    task_type: str
    agent_type: str  # Which agent should handle this
    payload: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class TaskQueue:
    """Local Python queue for task management (SIMPLIFIED - uses asyncio.Queue)."""
    
    def __init__(self, max_concurrent: int = 5):
        """
        Initialize task queue.
        
        Args:
            max_concurrent: Maximum number of concurrent tasks
        """
        self._tasks: Dict[str, Task] = {}
        # Use asyncio.Queue for local task queue (not distributed)
        self._queue: asyncio.Queue = asyncio.Queue()
        self._active_tasks: Dict[str, Task] = {}
        self._max_concurrent = max_concurrent
        self._lock = asyncio.Lock()
        logger.info("TaskQueue initialized (local)", max_concurrent=max_concurrent)
    
    async def enqueue(
        self,
        task_type: str,
        agent_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        max_retries: int = 3
    ) -> str:
        """
        Add a task to the local queue.
        
        Args:
            task_type: Type of task
            agent_type: Agent type that should handle this
            payload: Task data
            priority: Task priority
            max_retries: Maximum retry attempts
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            max_retries=max_retries,
        )
        
        async with self._lock:
            self._tasks[task_id] = task
        
        # Add to local queue with priority
        await self._queue.put((priority.value, task_id, task))
        logger.info("Task enqueued (local)", task_id=task_id, task_type=task_type, agent_type=agent_type)
        
        return task_id
    
    async def dequeue(self, agent_type: str) -> Optional[Task]:
        """
        Get the next task for an agent type from local queue.
        
        Args:
            agent_type: Agent type requesting a task
            
        Returns:
            Task or None if no tasks available
        """
        # Check if we're at max concurrent tasks
        async with self._lock:
            if len(self._active_tasks) >= self._max_concurrent:
                return None
        
        # Try to get a matching task from local queue
        temp_queue = []
        task = None
        
        while not self._queue.empty():
            try:
                priority, task_id, candidate_task = await asyncio.wait_for(
                    self._queue.get(), timeout=0.1
                )
            except asyncio.TimeoutError:
                break
            
            if candidate_task.agent_type == agent_type and candidate_task.status == TaskStatus.PENDING:
                task = candidate_task
                break
            else:
                temp_queue.append((priority, task_id, candidate_task))
        
        # Put non-matching tasks back
        for item in temp_queue:
            await self._queue.put(item)
        
        if task:
            async with self._lock:
                task.status = TaskStatus.ASSIGNED
                task.assigned_to = agent_type
                self._active_tasks[task.task_id] = task
            logger.info("Task assigned", task_id=task.task_id, agent_type=agent_type)
        
        return task
    
    async def start_task(self, task_id: str) -> bool:
        """
        Mark a task as in progress.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if successful
        """
        async with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.utcnow()
                logger.info("Task started", task_id=task_id)
                return True
            return False
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            result: Task result
            
        Returns:
            True if successful
        """
        async with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                del self._active_tasks[task_id]
                logger.info("Task completed", task_id=task_id)
                return True
            return False
    
    async def fail_task(self, task_id: str, error: str) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: Task identifier
            error: Error message
            
        Returns:
            True if successful
        """
        async with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = error
                task.retry_count += 1
                
                # Retry if possible
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.PENDING
                    task.assigned_to = None
                    task.started_at = None
                    await self._queue.put((task.priority.value, task.task_id, task))
                    logger.warning("Task retry scheduled", task_id=task_id, retry_count=task.retry_count)
                else:
                    del self._active_tasks[task_id]
                    logger.error("Task failed", task_id=task_id, error=error)
                
                return True
            return False
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        async with self._lock:
            return self._tasks.get(task_id)
    
    async def get_pending_tasks(self, agent_type: Optional[str] = None) -> List[Task]:
        """Get all pending tasks, optionally filtered by agent type."""
        async with self._lock:
            tasks = [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
            if agent_type:
                tasks = [t for t in tasks if t.agent_type == agent_type]
            return tasks
    
    async def get_active_tasks(self) -> List[Task]:
        """Get all active tasks."""
        async with self._lock:
            return list(self._active_tasks.values())
