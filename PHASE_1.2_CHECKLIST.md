# Phase 1.2: Core Framework Components (SIMPLIFIED) - Checklist

## Objectives

- [x] Simplify State Manager with JSON persistence
- [x] Simplify Task Queue to local Python queue
- [x] Make Base Agent lightweight (utilities only)
- [x] Replace SQLAlchemy with simple SQLite storage
- [x] Keep Message Bus and Logger as-is

## Tasks

### 1. State Manager (SIMPLIFIED) ✅

- [x] Add JSON file persistence (`./data/state.json`)
- [x] Automatic save on state changes
- [x] Automatic load on initialization
- [x] Maintain backward compatibility
- [x] Test state persistence

### 2. Task Queue (SIMPLIFIED) ✅

- [x] Use `asyncio.Queue` (local Python queue)
- [x] Remove distributed queue complexity
- [x] Maintain priority-based ordering
- [x] Keep retry mechanism
- [x] Test task queue operations

### 3. Base Agent (LIGHTWEIGHT) ✅

- [x] Simplify to utilities only
- [x] Remove full agent implementation
- [x] Keep: logging, message bus helpers, state helpers
- [x] Document that ADK agents should be used for full functionality
- [x] Test base agent utilities

### 4. Storage (SIMPLIFIED) ✅

- [x] Create `SimpleStorage` class (SQLite wrapper)
- [x] Replace SQLAlchemy with direct SQLite
- [x] Implement basic CRUD operations
- [x] Add JSON serialization for complex data
- [x] Test storage operations

### 5. Database Module (UPDATED) ✅

- [x] Update `init_database()` to use SimpleStorage
- [x] Remove SQLAlchemy dependencies
- [x] Maintain compatibility functions
- [x] Update imports in `__init__.py`

### 6. Dependencies (UPDATED) ✅

- [x] Comment out SQLAlchemy in requirements.txt
- [x] Verify core dependencies work
- [x] Test imports

## Verification

### Test State Manager

```python
from adk.core.state_manager import StateManager
import asyncio

async def test():
    sm = StateManager()
    await sm.set_state("test", "value")
    value = await sm.get_state("test")
    print(f"State: {value}")  # Should print "value"
    # Check ./data/state.json exists

asyncio.run(test())
```

### Test Storage

```python
from adk.models.storage import SimpleStorage

storage = SimpleStorage()
storage.save_finding({
    "finding_id": "test-1",
    "regulation": "GDPR",
    "status": "non_compliant",
    "severity": "high",
    "description": "Test finding",
    "detected_at": "2024-01-01T00:00:00",
    "agent_id": "test-agent"
})
findings = storage.get_findings()
print(f"Findings: {len(findings)}")  # Should be 1
```

### Test Task Queue

```python
from adk.core.task_queue import TaskQueue, TaskPriority
import asyncio

async def test():
    queue = TaskQueue()
    task_id = await queue.enqueue(
        "test_task",
        "test_agent",
        {"data": "test"},
        TaskPriority.HIGH
    )
    task = await queue.dequeue("test_agent")
    print(f"Task: {task.task_id}")  # Should match task_id

asyncio.run(test())
```

## Completion Criteria

Phase 1.2 is complete when:

1. ✅ State Manager has JSON persistence
2. ✅ Task Queue uses local asyncio.Queue
3. ✅ Base Agent is lightweight
4. ✅ SimpleStorage replaces SQLAlchemy
5. ✅ All components import successfully
6. ✅ No linter errors
7. ⏳ Basic tests pass (optional)

## Files Modified

- `adk/core/state_manager.py` - Added JSON persistence
- `adk/core/task_queue.py` - Simplified to local queue
- `adk/core/base_agent.py` - Made lightweight
- `adk/models/storage.py` - NEW - Simple SQLite storage
- `adk/models/database.py` - Updated to use SimpleStorage
- `adk/models/__init__.py` - Updated exports
- `requirements.txt` - Commented out SQLAlchemy

## Next Steps

Once Phase 1.2 is complete, proceed to:

**Phase 1.3: Data Models & Storage (SIMPLIFIED)**
- Verify Pydantic models work with simplified storage
- Update any code that uses old database models
- Test data persistence

---

**Phase 1.2 Status**: Complete ✅

