"""
Test multi-agent workflow patterns.
Demonstrates sequential, parallel, and loop execution.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.agents.policy_matcher import PolicyMatcherAgent
from adk.agents.critic import CriticAgent
from adk.core.session_service import ADCOSessionService
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.core.workflow_patterns import WorkflowPatterns


async def test_workflow_patterns():
    """Test all three workflow patterns."""
    print("=" * 70)
    print("MULTI-AGENT WORKFLOW PATTERNS DEMONSTRATION")
    print("=" * 70)
    
    # Initialize infrastructure
    session_service = ADCOSessionService()
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    # Initialize agents
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
    
    print("\n✅ All agents initialized\n")
    
    # Test 1: Sequential Pattern
    print("=" * 70)
    print("TEST 1: SEQUENTIAL WORKFLOW (RiskScanner → PolicyMatcher)")
    print("=" * 70)
    
    sequential_result = await WorkflowPatterns.execute_sequential(
        agents=[
            (risk_scanner, None),  # Pass through input directly
            (policy_matcher, None)  # Pass through previous result
        ],
        initial_input={"source": "production_db", "source_type": "database"},
        session_id="sequential_test_001"
    )
    
    print(f"\n✅ Sequential workflow completed")
    print(f"   Total steps: {len(sequential_result['steps'])}")
    print(f"   Pattern: {sequential_result['pattern']}")
    for i, step in enumerate(sequential_result['steps']):
        print(f"   Step {i+1}: {step['agent']} ({step['duration']:.2f}s)")
    
    # Test 2: Parallel Pattern
    print("\n" + "=" * 70)
    print("TEST 2: PARALLEL WORKFLOW (3 RiskScanners concurrently)")
    print("=" * 70)
    
    parallel_result = await WorkflowPatterns.execute_parallel(
        agents=[risk_scanner, risk_scanner, risk_scanner],
        inputs=[
            {"source": "database_1", "source_type": "database"},
            {"source": "database_2", "source_type": "database"},
            {"source": "database_3", "source_type": "database"}
        ],
        session_id="parallel_test_001"
    )
    
    print(f"\n✅ Parallel workflow completed")
    print(f"   Total agents: {len(parallel_result['successful']) + len(parallel_result['failed'])}")
    print(f"   Successful: {len(parallel_result['successful'])}")
    print(f"   Failed: {len(parallel_result['failed'])}")
    print(f"   Total duration: {parallel_result['duration']:.2f}s")
    print(f"   Pattern: {parallel_result['pattern']}")
    
    # Test 3: Loop Pattern (Critic Feedback)
    print("\n" + "=" * 70)
    print("TEST 3: LOOP WORKFLOW (PolicyMatcher with Critic feedback)")
    print("=" * 70)
    
    loop_result = await WorkflowPatterns.execute_loop(
        agent=policy_matcher,
        critic_agent=critic,
        initial_input={
            "framework": "GDPR",
            "data_practices": [
                {"description": "User email collection without consent"}
            ]
        },
        session_id="loop_test_001",
        max_iterations=3,
        quality_threshold=0.7
    )
    
    print(f"\n✅ Loop workflow completed")
    print(f"   Iterations: {loop_result['iterations']}")
    print(f"   Final quality: {loop_result['final_quality']:.2f}")
    print(f"   Pattern: {loop_result['pattern']}")
    if "warning" in loop_result:
        print(f"   ⚠️  {loop_result['warning']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("WORKFLOW PATTERNS SUMMARY")
    print("=" * 70)
    print("\n✅ All 3 patterns successfully demonstrated:")
    print("   1. Sequential: Step-by-step pipeline execution")
    print("   2. Parallel: Concurrent multi-agent execution")
    print("   3. Loop: Critic-driven refinement with feedback")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_workflow_patterns())
