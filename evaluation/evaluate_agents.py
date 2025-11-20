"""
Agent Evaluation Script for ADCO System.
Measures the performance of the RiskScannerAgent against synthetic data.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue

async def evaluate_risk_scanner():
    """Evaluate Risk Scanner Agent performance."""
    print("Starting Agent Evaluation...")
    
    # Initialize infrastructure
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue()
    
    # Initialize Agent
    scanner = RiskScannerAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue
    )
    await scanner.initialize()
    
    # Load Test Data
    data_path = Path(__file__).parent / "synthetic_data.json"
    with open(data_path, "r") as f:
        test_cases = json.load(f)
    
    results = []
    
    for case in test_cases:
        print(f"\nRunning Test Case: {case['id']} ({case['description']})")
        
        # Run Agent
        scan_result = await scanner.run({
            "source": case["source"],
            "source_type": case["source_type"]
        })
        
        # Analyze Results
        detected_risks = scan_result.get("risks", [])
        detected_categories = [r["category"] for r in detected_risks] if detected_risks else []
        
        # Simple matching logic (mocked for now as agent returns mock data)
        # In a real scenario, we'd match specific risk IDs or types
        
        # For this evaluation, we check if *any* risk was detected if expected
        success = len(detected_risks) > 0 if case["expected_risks"] else len(detected_risks) == 0
        
        results.append({
            "case_id": case["id"],
            "expected": case["expected_risks"],
            "detected_count": len(detected_risks),
            "success": success
        })
        
        print(f"  -> Detected {len(detected_risks)} risks. Success: {success}")

    # Calculate Metrics
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    score = (passed / total) * 100 if total > 0 else 0
    
    print(f"\nEvaluation Complete.")
    print(f"Total Cases: {total}")
    print(f"Passed: {passed}")
    print(f"Score: {score:.2f}%")
    
    # Generate Report
    report = {
        "timestamp": "2025-11-20T21:30:00Z",
        "agent": "RiskScannerAgent",
        "score": score,
        "details": results
    }
    
    with open(Path(__file__).parent / "evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Detailed report saved to evaluation/evaluation_report.json")

if __name__ == "__main__":
    asyncio.run(evaluate_risk_scanner())
