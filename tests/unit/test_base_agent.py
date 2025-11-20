"""Tests for base agent."""

import pytest
from adk.core.base_agent import BaseAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue


class TestAgent(BaseAgent):
    """Test agent implementation."""
    
    async def run(self, input_data):
        return {"result": "test"}


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = TestAgent()
    assert agent.agent_id is not None
    assert agent.agent_type == "test"
    
    await agent.initialize()
    await agent.shutdown()


@pytest.mark.asyncio
async def test_agent_with_components():
    """Test agent with core components."""
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    agent = TestAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    
    await agent.initialize()
    result = await agent.run({})
    assert result["result"] == "test"
    await agent.shutdown()




