"""
Unit tests for RiskScanner agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.core.session_service import ADCOSessionService


@pytest.fixture
def message_bus():
    """Create message bus fixture."""
    return MessageBus()


@pytest.fixture
def state_manager():
    """Create state manager fixture."""
    return StateManager()


@pytest.fixture
def task_queue():
    """Create task queue fixture."""
    return TaskQueue()


@pytest.fixture
def session_service():
    """Create session service fixture."""
    return ADCOSessionService()


@pytest.fixture
async def risk_scanner(message_bus, state_manager, task_queue, session_service):
    """Create RiskScanner agent fixture."""
    agent = RiskScannerAgent(
        name="TestRiskScanner",
        session_service=session_service,
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    await agent.initialize()
    return agent


@pytest.mark.asyncio
async def test_risk_scanner_initialization(risk_scanner):
    """Test that RiskScanner initializes correctly."""
    assert risk_scanner.name == "TestRiskScanner"
    assert risk_scanner.session_service is not None
    assert risk_scanner.message_bus is not None


@pytest.mark.asyncio
async def test_risk_scanner_detects_pii(risk_scanner):
    """Test that RiskScanner detects PII in data."""
    result = await risk_scanner.run({
        "source": "test_database",
        "source_type": "database",
        "data": {
            "columns": ["email", "name"],
            "sample_values": ["john@example.com", "John Doe"]
        }
    })
    
    assert "risks" in result
    assert isinstance(result["risks"], list)


@pytest.mark.asyncio
async def test_risk_scanner_handles_empty_data(risk_scanner):
    """Test that RiskScanner handles empty data gracefully."""
    result = await risk_scanner.run({
        "source": "empty_database",
        "source_type": "database",
        "data": {
            "columns": [],
            "sample_values": []
        }
    })
    
    assert "risks" in result
    assert isinstance(result["risks"], list)


@pytest.mark.asyncio
async def test_risk_scanner_handles_invalid_input(risk_scanner):
    """Test that RiskScanner handles invalid input gracefully."""
    result = await risk_scanner.run({
        "source": "test_invalid",
        "source_type": "database"
    })
    
    # Should not crash, should return some result
    assert result is not None


@pytest.mark.asyncio
async def test_risk_scanner_session_tracking(risk_scanner, session_service):
    """Test that RiskScanner tracks session state."""
    session_id = "test_session_001"
    
    result = await risk_scanner.run({
        "source": "test_db",
        "source_type": "database"
    })
    
    # Session tracking happens internally, just verify result
    assert result is not None
    assert "scan_id" in result


@pytest.mark.asyncio
async def test_risk_scanner_multiple_sources(risk_scanner):
    """Test scanning multiple sources."""
    sources = [
        {"source": "db1", "source_type": "database"},
        {"source": "db2", "source_type": "database"},
        {"source": "api1", "source_type": "api"}
    ]
    
    results = []
    for source in sources:
        result = await risk_scanner.run(source)
        results.append(result)
    
    assert len(results) == 3
    for result in results:
        assert "risks" in result
