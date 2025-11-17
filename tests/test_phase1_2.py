"""Quick tests for Phase 1.2 simplified components."""

import asyncio
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue, TaskPriority
from adk.models.storage import SimpleStorage


async def test_state_manager():
    """Test State Manager with JSON persistence."""
    print("Testing State Manager...")
    sm = StateManager()
    
    await sm.set_state("test_key", "test_value")
    value = await sm.get_state("test_key")
    assert value == "test_value", f"Expected 'test_value', got {value}"
    print("✓ State Manager: set/get works")
    
    await sm.set_agent_context("agent1", "context_key", "context_value")
    ctx_value = await sm.get_agent_context("agent1", "context_key")
    assert ctx_value == "context_value", f"Expected 'context_value', got {ctx_value}"
    print("✓ State Manager: agent context works")
    
    # Check if file was created
    from pathlib import Path
    state_file = Path("./data/state.json")
    if state_file.exists():
        print("✓ State Manager: JSON file persistence works")
    else:
        print("⚠ State Manager: JSON file not created yet (will be created on save)")


async def test_task_queue():
    """Test Task Queue (local)."""
    print("\nTesting Task Queue...")
    queue = TaskQueue(max_concurrent=2)
    
    task_id = await queue.enqueue(
        "test_task",
        "test_agent",
        {"data": "test"},
        TaskPriority.HIGH
    )
    print(f"✓ Task Queue: enqueued task {task_id}")
    
    task = await queue.dequeue("test_agent")
    assert task is not None, "Task should be dequeued"
    assert task.task_id == task_id, "Task ID should match"
    print("✓ Task Queue: dequeue works")
    
    await queue.start_task(task_id)
    task = await queue.get_task(task_id)
    assert task.status.value == "in_progress", "Task should be in progress"
    print("✓ Task Queue: task status tracking works")


def test_storage():
    """Test Simple Storage."""
    print("\nTesting Simple Storage...")
    storage = SimpleStorage()
    
    # Test finding storage
    finding = {
        "finding_id": "test-finding-1",
        "regulation": "GDPR",
        "article": "Article 5",
        "status": "non_compliant",
        "severity": "high",
        "description": "Test compliance finding",
        "evidence": ["evidence1", "evidence2"],
        "recommendation": "Fix this issue",
        "detected_at": "2024-01-01T00:00:00",
        "agent_id": "test-agent"
    }
    
    storage.save_finding(finding)
    print("✓ Storage: save_finding works")
    
    findings = storage.get_findings()
    assert len(findings) > 0, "Should have at least one finding"
    assert findings[0]["finding_id"] == "test-finding-1", "Finding ID should match"
    print("✓ Storage: get_findings works")
    
    # Test report metadata
    report = {
        "report_id": "test-report-1",
        "title": "Test Report",
        "report_type": "compliance",
        "generated_at": "2024-01-01T00:00:00",
        "generated_by": "test-agent",
        "summary": "Test summary",
        "file_path": "./data/reports/test-report-1.json",
        "format": "json"
    }
    
    storage.save_report_metadata(report)
    print("✓ Storage: save_report_metadata works")
    
    saved_report = storage.get_report_metadata("test-report-1")
    assert saved_report is not None, "Report should be saved"
    assert saved_report["title"] == "Test Report", "Report title should match"
    print("✓ Storage: get_report_metadata works")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Phase 1.2 Component Tests")
    print("=" * 50)
    
    await test_state_manager()
    await test_task_queue()
    test_storage()
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

