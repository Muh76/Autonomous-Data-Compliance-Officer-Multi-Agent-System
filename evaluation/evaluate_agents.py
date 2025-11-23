"""
Comprehensive Agent Evaluation Script for ADCO System.
Evaluates all 6 agents with precision, recall, F1 metrics.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.agents.risk_scanner import RiskScannerAgent
from adk.agents.policy_matcher import PolicyMatcherAgent
from adk.agents.report_writer import ReportWriterAgent
from adk.agents.critic import CriticAgent
from adk.agents.watchdog import WatchdogAgent
from adk.agents.coordinator import CoordinatorAgent
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.core.session_service import ADCOSessionService
from evaluation.metrics_calculator import MetricsCalculator, EvaluationMetrics


class ComprehensiveEvaluator:
    """Comprehensive evaluation framework for all ADCO agents."""
    
    def __init__(self):
        """Initialize evaluator with all agents."""
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.task_queue = TaskQueue()
        self.session_service = ADCOSessionService()
        self.calculator = MetricsCalculator()
        
        # Initialize agents
        self.agents = {}
        self.results = {}
        
    async def initialize_agents(self):
        """Initialize all agents."""
        print("Initializing agents...")
        
        self.agents['RiskScanner'] = RiskScannerAgent(
            name="RiskScanner",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        self.agents['PolicyMatcher'] = PolicyMatcherAgent(
            name="PolicyMatcher",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        self.agents['ReportWriter'] = ReportWriterAgent(
            name="ReportWriter",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        self.agents['Critic'] = CriticAgent(
            name="Critic",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        self.agents['Watchdog'] = WatchdogAgent(
            name="Watchdog",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        self.agents['Coordinator'] = CoordinatorAgent(
            name="Coordinator",
            session_service=self.session_service,
            message_bus=self.message_bus,
            state_manager=self.state_manager,
            task_queue=self.task_queue
        )
        
        # Initialize all agents
        for agent in self.agents.values():
            await agent.initialize()
        
        print(f"✅ Initialized {len(self.agents)} agents\n")
    
    async def evaluate_risk_scanner(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Evaluate RiskScanner agent."""
        print("=" * 70)
        print("EVALUATING: RiskScanner Agent")
        print("=" * 70)
        
        agent = self.agents['RiskScanner']
        scanner_cases = [tc for tc in test_cases if tc.get('agent') == 'RiskScanner']
        
        predictions = []
        ground_truth = []
        detailed_results = []
        
        for case in scanner_cases:
            print(f"\nTest {case['id']}: {case['description']}")
            
            try:
                # Run agent
                result = await agent.process({
                    "source": case.get("source", ""),
                    "source_type": case.get("source_type", "database")
                }, session_id=f"eval_{case['id']}")
                
                # Extract detected risks
                detected_risks = set(result.get("risks", []))
                if isinstance(detected_risks, list) and detected_risks:
                    # Handle case where risks are dicts
                    if isinstance(detected_risks[0], dict):
                        detected_risks = {r.get("category", "") for r in detected_risks}
                
                expected_risks = set(case.get("expected_risks", []))
                
                # Calculate match
                has_risks_predicted = len(detected_risks) > 0
                has_risks_actual = len(expected_risks) > 0
                
                predictions.append(has_risks_predicted)
                ground_truth.append(has_risks_actual)
                
                # Detailed multi-label evaluation
                tp = len(detected_risks & expected_risks)
                fp = len(detected_risks - expected_risks)
                fn = len(expected_risks - detected_risks)
                
                detailed_results.append({
                    "case_id": case['id'],
                    "detected": list(detected_risks),
                    "expected": list(expected_risks),
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "success": tp > 0 if expected_risks else len(detected_risks) == 0
                })
                
                print(f"  Detected: {detected_risks}")
                print(f"  Expected: {expected_risks}")
                print(f"  TP: {tp}, FP: {fp}, FN: {fn}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                predictions.append(False)
                ground_truth.append(len(case.get("expected_risks", [])) > 0)
                detailed_results.append({
                    "case_id": case['id'],
                    "error": str(e),
                    "success": False
                })
        
        # Calculate metrics
        metrics = self.calculator.calculate_binary_metrics(predictions, ground_truth)
        
        print(f"\n{self.calculator.format_metrics_table(metrics)}")
        
        return {
            "agent": "RiskScanner",
            "test_cases": len(scanner_cases),
            "metrics": metrics.to_dict(),
            "detailed_results": detailed_results
        }
    
    async def evaluate_policy_matcher(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Evaluate PolicyMatcher agent."""
        print("=" * 70)
        print("EVALUATING: PolicyMatcher Agent")
        print("=" * 70)
        
        agent = self.agents['PolicyMatcher']
        matcher_cases = [tc for tc in test_cases if tc.get('agent') == 'PolicyMatcher']
        
        predictions = []
        ground_truth = []
        detailed_results = []
        citation_checks = []
        
        for case in matcher_cases:
            print(f"\nTest {case['id']}: {case['description']}")
            
            try:
                # Run agent
                result = await agent.process({
                    "framework": case.get("framework", "GDPR"),
                    "data_practices": case.get("data_practices", [])
                }, session_id=f"eval_{case['id']}")
                
                # Extract violations
                violations = result.get("violations", [])
                expected_violations = case.get("expected_violations", [])
                
                has_violations_predicted = len(violations) > 0
                has_violations_actual = len(expected_violations) > 0
                
                predictions.append(has_violations_predicted)
                ground_truth.append(has_violations_actual)
                
                # Check citations
                output_text = json.dumps(result)
                citation_check = self.calculator.check_citation_accuracy(output_text)
                citation_checks.append(citation_check)
                
                detailed_results.append({
                    "case_id": case['id'],
                    "violations_found": len(violations),
                    "violations_expected": len(expected_violations),
                    "has_citations": citation_check["has_citations"],
                    "success": has_violations_predicted == has_violations_actual
                })
                
                print(f"  Violations found: {len(violations)}")
                print(f"  Violations expected: {len(expected_violations)}")
                print(f"  Citations present: {citation_check['has_citations']}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                predictions.append(False)
                ground_truth.append(len(case.get("expected_violations", [])) > 0)
                detailed_results.append({
                    "case_id": case['id'],
                    "error": str(e),
                    "success": False
                })
        
        # Calculate metrics
        metrics = self.calculator.calculate_binary_metrics(predictions, ground_truth)
        
        # Citation accuracy
        citation_accuracy = sum(1 for c in citation_checks if c["has_citations"]) / len(citation_checks) if citation_checks else 0
        
        print(f"\n{self.calculator.format_metrics_table(metrics)}")
        print(f"Citation Accuracy: {citation_accuracy:.2%}")
        
        return {
            "agent": "PolicyMatcher",
            "test_cases": len(matcher_cases),
            "metrics": metrics.to_dict(),
            "citation_accuracy": citation_accuracy,
            "detailed_results": detailed_results
        }
    
    async def evaluate_critic(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Evaluate Critic agent."""
        print("=" * 70)
        print("EVALUATING: Critic Agent")
        print("=" * 70)
        
        agent = self.agents['Critic']
        critic_cases = [tc for tc in test_cases if tc.get('agent') == 'Critic']
        
        predictions = []
        ground_truth = []
        quality_scores = []
        
        for case in critic_cases:
            print(f"\nTest {case['id']}: {case['description']}")
            
            try:
                # Run agent
                result = await agent.process({
                    "agent_output": case.get("agent_output", {}),
                    "agent_type": case.get("agent_output", {}).get("type", "unknown")
                }, session_id=f"eval_{case['id']}")
                
                is_valid = result.get("is_valid", False)
                expected_valid = case.get("expected_is_valid", True)
                
                predictions.append(is_valid)
                ground_truth.append(expected_valid)
                
                # Quality scores
                scores = result.get("quality_scores", {})
                quality_scores.append(scores)
                
                print(f"  Valid: {is_valid} (expected: {expected_valid})")
                print(f"  Quality scores: {scores}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                predictions.append(False)
                ground_truth.append(case.get("expected_is_valid", True))
        
        # Calculate metrics
        metrics = self.calculator.calculate_binary_metrics(predictions, ground_truth)
        quality_stats = self.calculator.calculate_quality_scores(quality_scores)
        
        print(f"\n{self.calculator.format_metrics_table(metrics)}")
        print(f"Quality Score Stats: {quality_stats}")
        
        return {
            "agent": "Critic",
            "test_cases": len(critic_cases),
            "metrics": metrics.to_dict(),
            "quality_stats": quality_stats
        }
    
    async def run_full_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation on all agents."""
        print("=" * 70)
        print("ADCO COMPREHENSIVE AGENT EVALUATION")
        print("=" * 70)
        print(f"Started: {datetime.utcnow().isoformat()}\n")
        
        # Load test cases
        data_path = Path(__file__).parent / "synthetic_data.json"
        with open(data_path, "r") as f:
            test_cases = json.load(f)
        
        print(f"Loaded {len(test_cases)} test cases\n")
        
        # Initialize agents
        await self.initialize_agents()
        
        # Run evaluations
        results = {}
        
        # Evaluate each agent
        results['RiskScanner'] = await self.evaluate_risk_scanner(test_cases)
        results['PolicyMatcher'] = await self.evaluate_policy_matcher(test_cases)
        results['Critic'] = await self.evaluate_critic(test_cases)
        
        # Calculate overall metrics
        all_metrics = [r['metrics'] for r in results.values() if 'metrics' in r]
        
        if all_metrics:
            avg_precision = sum(m['precision'] for m in all_metrics) / len(all_metrics)
            avg_recall = sum(m['recall'] for m in all_metrics) / len(all_metrics)
            avg_f1 = sum(m['f1_score'] for m in all_metrics) / len(all_metrics)
            avg_accuracy = sum(m['accuracy'] for m in all_metrics) / len(all_metrics)
        else:
            avg_precision = avg_recall = avg_f1 = avg_accuracy = 0.0
        
        overall_summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_test_cases": len(test_cases),
            "agents_evaluated": list(results.keys()),
            "overall_metrics": {
                "avg_precision": round(avg_precision, 4),
                "avg_recall": round(avg_recall, 4),
                "avg_f1_score": round(avg_f1, 4),
                "avg_accuracy": round(avg_accuracy, 4)
            },
            "agent_results": results
        }
        
        # Print summary
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        print(f"\nTotal Test Cases: {len(test_cases)}")
        print(f"Agents Evaluated: {len(results)}")
        print(f"\nOverall Performance:")
        print(f"  Average Precision: {avg_precision:.2%}")
        print(f"  Average Recall:    {avg_recall:.2%}")
        print(f"  Average F1 Score:  {avg_f1:.2%}")
        print(f"  Average Accuracy:  {avg_accuracy:.2%}")
        
        # Save results
        output_path = Path(__file__).parent / "evaluation_report.json"
        with open(output_path, 'w') as f:
            json.dump(overall_summary, f, indent=2)
        
        print(f"\n✅ Detailed report saved to: {output_path}")
        print("=" * 70)
        
        return overall_summary


async def main():
    """Main evaluation entry point."""
    evaluator = ComprehensiveEvaluator()
    results = await evaluator.run_full_evaluation()
    return results


if __name__ == "__main__":
    asyncio.run(main())
