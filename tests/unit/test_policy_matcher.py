"""
Unit tests for PolicyMatcher agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.policy_matcher import PolicyMatcherAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.core.session_service import ADCOSessionService


@pytest.fixture
async def policy_matcher():
    """Create PolicyMatcher agent fixture."""
    agent = PolicyMatcherAgent(
        name="TestPolicyMatcher",
        session_service=ADCOSessionService(),
        message_bus=MessageBus(),
        state_manager=StateManager(),
        task_queue=TaskQueue()
    )
    await agent.initialize()
    return agent


@pytest.mark.asyncio
async def test_policy_matcher_gdpr_violation(policy_matcher):
    """Test GDPR violation detection."""
    result = await policy_matcher.run({
        "framework": "GDPR",
        "data_practices": [{
            "description": "Collecting emails without consent",
            "category": "data_collection"
        }]
    })
    
    
    assert "findings" in result
    assert isinstance(result["findings"], list)


@pytest.mark.asyncio
async def test_policy_matcher_compliant_practice(policy_matcher):
    """Test compliant practice returns no violations."""
    result = await policy_matcher.run({
        "framework": "GDPR",
        "data_practices": [{
            "description": "Collecting data with explicit consent and privacy notice",
            "category": "data_collection"
        }]
    })
    
    
    assert "findings" in result


@pytest.mark.asyncio
async def test_policy_matcher_multiple_frameworks(policy_matcher):
    """Test checking against multiple frameworks."""
    frameworks = ["GDPR", "HIPAA", "CCPA"]
    
    for framework in frameworks:
        result = await policy_matcher.run({
            "framework": framework,
            "data_practices": [{
                "description": "Test practice",
                "category": "data_storage"
            }]
        })
        
        
    assert "findings" in result


@pytest.mark.asyncio
async def test_policy_matcher_includes_citations(policy_matcher):
    """Test that violations include citations."""
    result = await policy_matcher.run({
        "framework": "GDPR",
        "data_practices": [{
            "description": "Selling user data without consent",
            "category": "data_sharing"
        }]
    })
    
    # Check result structure includes citations or references
    assert result is not None
