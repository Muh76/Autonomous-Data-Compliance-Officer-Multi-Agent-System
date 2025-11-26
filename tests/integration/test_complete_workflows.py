"""
Integration tests for complete workflows.
"""

import pytest
import asyncio

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.agents.policy_matcher import PolicyMatcherAgent
from adk.agents.report_writer import ReportWriterAgent
from adk.agents.critic import CriticAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.core.session_service import ADCOSessionService
from adk.core.workflow_patterns import WorkflowPatterns


@pytest.fixture
async def agents():
    """Create all agents for integration testing."""
    session_service = ADCOSessionService()
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    risk_scanner = RiskScannerAgent(
        name="RiskScanner",
        session_service=session_service,
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    
    policy_matcher = PolicyMatcherAgent(
        name="PolicyMatcher",
        session_service=session_service,
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    
    critic = CriticAgent(
        name="Critic",
        session_service=session_service,
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    
    await risk_scanner.initialize()
    await policy_matcher.initialize()
    await critic.initialize()
    
    return {
        "risk_scanner": risk_scanner,
        "policy_matcher": policy_matcher,
        "critic": critic
    }


@pytest.mark.asyncio
async def test_sequential_workflow(agents):
    """Test sequential workflow: RiskScanner -> PolicyMatcher."""
    result = await WorkflowPatterns.execute_sequential(
        agents=[
            (agents["risk_scanner"], None),
            (agents["policy_matcher"], None)
        ],
        initial_input={
            "source": "test_db",
            "source_type": "database"
        },
        session_id="integration_sequential_001"
    )
    
    assert result["pattern"] == "sequential"
    assert len(result["steps"]) == 2
    assert "final_result" in result


@pytest.mark.asyncio
async def test_parallel_workflow(agents):
    """Test parallel workflow: Multiple RiskScanners concurrently."""
    result = await WorkflowPatterns.execute_parallel(
        agents=[
            agents["risk_scanner"],
            agents["risk_scanner"],
            agents["risk_scanner"]
        ],
        inputs=[
            {"source": "db1", "source_type": "database"},
            {"source": "db2", "source_type": "database"},
            {"source": "db3", "source_type": "database"}
        ],
        session_id="integration_parallel_001"
    )
    
    assert result["pattern"] == "parallel"
    assert len(result["successful"]) + len(result["failed"]) == 3


@pytest.mark.asyncio
async def test_loop_workflow(agents):
    """Test loop workflow: PolicyMatcher with Critic feedback."""
    result = await WorkflowPatterns.execute_loop(
        agent=agents["policy_matcher"],
        critic_agent=agents["critic"],
        initial_input={
            "framework": "GDPR",
            "data_practices": [{
                "description": "Test practice",
                "category": "data_collection"
            }]
        },
        session_id="integration_loop_001",
        max_iterations=2,
        quality_threshold=0.7
    )
    
    assert result["pattern"] == "loop"
    assert result["iterations"] >= 1
    assert "final_result" in result


@pytest.mark.asyncio
async def test_end_to_end_compliance_audit(agents):
    """Test complete end-to-end compliance audit workflow."""
    # Step 1: Scan for risks
    scan_result = await agents["risk_scanner"].process({
        "source": "production_db",
        "source_type": "database"
    }, session_id="e2e_audit_001")
    
    assert "risks" in scan_result
    
    # Step 2: Check compliance
    compliance_result = await agents["policy_matcher"].process({
        "framework": "GDPR",
        "data_practices": [{
            "description": "Database contains PII",
            "category": "data_storage"
        }]
    }, session_id="e2e_audit_001")
    
    assert "violations" in compliance_result
    
    # Step 3: Validate with critic
    validation_result = await agents["critic"].process({
        "agent_output": compliance_result,
        "agent_type": "PolicyMatcher"
    }, session_id="e2e_audit_001")
    
    assert "is_valid" in validation_result
    assert "quality_scores" in validation_result
