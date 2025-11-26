"""Integration tests for workflows."""

import pytest
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.agents import CoordinatorAgent


@pytest.mark.asyncio
async def test_scan_workflow():
    """Test scan workflow."""
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    coordinator = CoordinatorAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    
    await coordinator.initialize()
    
    result = await coordinator.run({
        "workflow_type": "scan",
        "data_sources": ["test_source"],
    })
    
    assert result["status"] == "completed"
    assert "workflow_id" in result
    
    await coordinator.shutdown()







