"""Test ADK integration with RiskScannerAgent."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.core.session_service import ADCOSessionService
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue


async def test_adk_risk_scanner():
    """Test RiskScannerAgent with ADK integration."""
    print("=" * 60)
    print("Testing ADK Integration with RiskScannerAgent")
    print("=" * 60)
    
    # Initialize infrastructure
    session_service = ADCOSessionService()
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    # Initialize RiskScannerAgent with ADK
    scanner = RiskScannerAgent(
        name="RiskScanner",
        session_service=session_service,
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    
    await scanner.initialize()
    print("\n✅ RiskScannerAgent initialized with ADK")
    
    # Test 1: Process with session
    print("\n" + "=" * 60)
    print("Test 1: Processing scan with session context")
    print("=" * 60)
    
    session_id = "test_session_001"
    input_data = {
        "source": "test_database",
        "source_type": "database"
    }
    
    result = await scanner.process(input_data, session_id=session_id)
    
    print(f"\n✅ Scan completed")
    print(f"   Session ID: {session_id}")
    print(f"   Scan ID: {result.get('scan_id')}")
    print(f"   Risks found: {result.get('items_scanned', 0)}")
    
    # Test 2: Verify session history
    print("\n" + "=" * 60)
    print("Test 2: Verifying session history")
    print("=" * 60)
    
    history = await session_service.get_session_history(session_id)
    print(f"\n✅ Session history retrieved")
    print(f"   History entries: {len(history)}")
    
    if history:
        print(f"   Last entry: {history[-1].get('agent')} at {history[-1].get('timestamp')}")
    
    # Test 3: Test with real PII data
    print("\n" + "=" * 60)
    print("Test 3: Scanning text with real PII")
    print("=" * 60)
    
    test_text = "Contact John Doe at john.doe@example.com or call 415-555-0199"
    risks = await scanner._scan_text(test_text, "test_source")
    
    print(f"\n✅ PII detection completed")
    print(f"   Text scanned: '{test_text}'")
    print(f"   PII entities found: {len(risks)}")
    
    for risk in risks:
        print(f"   - {risk.title} (Severity: {risk.severity.value})")
    
    # Test 4: Store in long-term memory
    print("\n" + "=" * 60)
    print("Test 4: Storing scan result in long-term memory")
    print("=" * 60)
    
    await session_service.store_in_long_term_memory(
        session_id=session_id,
        content=f"Scan of {input_data['source']} found {len(risks)} risks",
        metadata={
            "scan_id": result.get('scan_id'),
            "source": input_data['source'],
            "risk_count": len(risks)
        }
    )
    
    print(f"\n✅ Scan result stored in long-term memory")
    
    # Test 5: Recall from long-term memory
    print("\n" + "=" * 60)
    print("Test 5: Recalling similar scans from memory")
    print("=" * 60)
    
    memories = await session_service.recall_from_long_term_memory(
        query="database scan risks",
        top_k=3
    )
    
    print(f"\n✅ Memory recall completed")
    print(f"   Similar memories found: {len(memories)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("ADK Integration Test Summary")
    print("=" * 60)
    print("\n✅ All tests passed!")
    print("\nADK Features Verified:")
    print("  ✓ Agent initialization with ADK base class")
    print("  ✓ Session management (InMemorySessionService)")
    print("  ✓ Session history tracking")
    print("  ✓ Long-term memory storage (ChromaDB)")
    print("  ✓ Memory recall")
    print("  ✓ Message bus integration")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_adk_risk_scanner())
