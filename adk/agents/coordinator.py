"""Coordinator agent for workflow orchestration."""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.message_bus import MessageType
from ..core.task_queue import TaskQueue, TaskPriority
from ..core.logger import get_logger
from ..core.workflow_patterns import WorkflowPatterns
from ..models.models import ScanResult, ComplianceFinding, RiskAssessment

logger = get_logger(__name__)


class CoordinatorAgent(BaseAgent):
    """Orchestrates workflow and coordinates other agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.agent_registry: Dict[str, str] = {}  # agent_type -> agent_id
        self.workflow_patterns = WorkflowPatterns()  # Multi-agent patterns
    
    async def initialize(self) -> None:
        """Initialize coordinator."""
        await super().initialize()
        self.logger.info("Coordinator agent initialized")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a compliance workflow.
        
        Args:
            input_data: Workflow input containing:
                - workflow_type: Type of workflow (scan, audit, report)
                - data_sources: List of data sources to scan
                - compliance_frameworks: List of frameworks to check
                
        Returns:
            Workflow result
        """
        workflow_id = str(uuid.uuid4())
        workflow_type = input_data.get("workflow_type", "scan")
        
        self.logger.info("Starting workflow", workflow_id=workflow_id, workflow_type=workflow_type)
        
        # Initialize workflow state
        self.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "results": {},
            "errors": [],
        }
        
        try:
            if workflow_type == "scan":
                result = await self._execute_scan_workflow(workflow_id, input_data)
            elif workflow_type == "audit":
                result = await self._execute_audit_workflow(workflow_id, input_data)
            elif workflow_type == "report":
                result = await self._execute_report_workflow(workflow_id, input_data)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.utcnow()
            self.active_workflows[workflow_id]["results"] = result
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": result,
            }
        except Exception as e:
            self.logger.error("Workflow failed", workflow_id=workflow_id, error=str(e))
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["errors"].append(str(e))
            raise
    
    async def _execute_scan_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data scanning workflow."""
        data_sources = input_data.get("data_sources", [])
        scan_results = []
        
        # Delegate to risk scanner
        if self.task_queue:
            for source in data_sources:
                task_id = await self.task_queue.enqueue(
                    task_type="scan",
                    agent_type="riskscanner",
                    payload={"source": source, "workflow_id": workflow_id},
                    priority=TaskPriority.HIGH
                )
                self.logger.info("Scan task enqueued", task_id=task_id, source=source)
        
        # Wait for results (in real implementation, use async coordination)
        # For now, return placeholder
        return {
            "scan_results": scan_results,
            "workflow_id": workflow_id,
        }
    
    async def _execute_audit_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a compliance audit workflow."""
        compliance_frameworks = input_data.get("compliance_frameworks", ["GDPR"])
        audit_results = []
        
        # 1. Scan data sources
        scan_result = await self._execute_scan_workflow(workflow_id, input_data)
        
        # 2. Match against policies
        if self.task_queue:
            for framework in compliance_frameworks:
                task_id = await self.task_queue.enqueue(
                    task_type="policy_match",
                    agent_type="policymatcher",
                    payload={
                        "framework": framework,
                        "scan_results": scan_result,
                        "workflow_id": workflow_id,
                    },
                    priority=TaskPriority.HIGH
                )
                self.logger.info("Policy match task enqueued", task_id=task_id, framework=framework)
        
        # 3. Generate report
        if self.task_queue:
            task_id = await self.task_queue.enqueue(
                task_type="generate_report",
                agent_type="reportwriter",
                payload={
                    "workflow_id": workflow_id,
                    "audit_results": audit_results,
                },
                priority=TaskPriority.MEDIUM
            )
            self.logger.info("Report generation task enqueued", task_id=task_id)
        
        return {
            "audit_results": audit_results,
            "workflow_id": workflow_id,
        }
    
    async def _execute_report_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a report generation workflow."""
        report_type = input_data.get("report_type", "compliance")
        
        if self.task_queue:
            task_id = await self.task_queue.enqueue(
                task_type="generate_report",
                agent_type="reportwriter",
                payload={
                    "workflow_id": workflow_id,
                    "report_type": report_type,
                    "input_data": input_data,
                },
                priority=TaskPriority.MEDIUM
            )
            self.logger.info("Report generation task enqueued", task_id=task_id)
        
        return {
            "workflow_id": workflow_id,
            "report_type": report_type,
        }
    
    async def register_agent(self, agent_type: str, agent_id: str) -> None:
        """Register an agent with the coordinator."""
        self.agent_registry[agent_type] = agent_id
        self.logger.info("Agent registered", agent_type=agent_type, agent_id=agent_id)
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow."""
        return self.active_workflows.get(workflow_id)
