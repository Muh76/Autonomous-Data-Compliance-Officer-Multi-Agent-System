"""Test real PII scanning with Presidio."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue

async def test_real_scanner():
    print("Testing Real Risk Scanner...")
    
    # Initialize
    scanner = RiskScannerAgent(
        message_bus=MessageBus(),
        state_manager=StateManager(),
        task_queue=TaskQueue()
    )
    await scanner.initialize()
    
    # Test Data with Real PII
    test_text = "My email is test@example.com and my phone is 415-555-0199."
    
    print(f"\nScanning text: '{test_text}'")
    
    # Run Scan
    # Note: We are calling the internal method for direct testing, 
    # or we can use .run() if we mock the source type correctly.
    # Let's use .run() with source_type="database" which triggers the simulated text scan loop
    # BUT wait, the current implementation of _scan_database uses HARDCODED simulated data.
    # We should probably update _scan_database to accept input or just test _scan_text directly.
    
    # Let's test _scan_text directly for verification
    risks = await scanner._scan_text(test_text, "test_source")
    
    print(f"\nFound {len(risks)} risks:")
    for risk in risks:
        print(f"- {risk.title}: {risk.description} (Score: {risk.risk_score:.2f})")
        
    # Assertions
    has_email = any("EMAIL" in r.title or "EMAIL" in r.description for r in risks)
    has_phone = any("PHONE" in r.title or "PHONE" in r.description for r in risks)
    
    if has_email and has_phone:
        print("\nSUCCESS: Detected both Email and Phone!")
    else:
        print("\nFAILURE: Missed some PII.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_real_scanner())
