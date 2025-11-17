"""Compliance API routes."""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.core.message_bus import MessageBus, MessageType
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.agents import CoordinatorAgent
from app.api.main import get_message_bus, get_state_manager, get_task_queue, get_agents

router = APIRouter()


class ScanRequest(BaseModel):
    """Scan request model."""
    data_sources: List[str]
    source_type: str = "database"
    scan_depth: int = 1000


class AuditRequest(BaseModel):
    """Audit request model."""
    data_sources: List[str]
    compliance_frameworks: List[str] = ["GDPR"]


@router.post("/compliance/scan")
async def trigger_scan(
    request: ScanRequest,
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Trigger a compliance scan."""
    coordinator: CoordinatorAgent = agents.get("coordinator")
    
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator agent not available")
    
    try:
        result = await coordinator.run({
            "workflow_type": "scan",
            "data_sources": request.data_sources,
            "source_type": request.source_type,
            "scan_depth": request.scan_depth,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/audit")
async def trigger_audit(
    request: AuditRequest,
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Trigger a compliance audit."""
    coordinator: CoordinatorAgent = agents.get("coordinator")
    
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator agent not available")
    
    try:
        result = await coordinator.run({
            "workflow_type": "audit",
            "data_sources": request.data_sources,
            "compliance_frameworks": request.compliance_frameworks,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/workflow/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Get workflow status."""
    coordinator: CoordinatorAgent = agents.get("coordinator")
    
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator agent not available")
    
    status = await coordinator.get_workflow_status(workflow_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return status

