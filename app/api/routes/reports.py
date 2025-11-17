"""Reports API routes."""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.agents import ReportWriterAgent
from app.api.main import get_agents

router = APIRouter()


@router.post("/reports/generate")
async def generate_report(
    report_data: Dict[str, Any],
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Generate a compliance report."""
    report_writer: ReportWriterAgent = agents.get("report_writer")
    
    if not report_writer:
        raise HTTPException(status_code=503, detail="Report writer agent not available")
    
    try:
        result = await report_writer.run(report_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Get report information."""
    # In a real implementation, retrieve from database
    return {
        "report_id": report_id,
        "status": "not_implemented",
    }


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = "json",
    agents: dict = Depends(get_agents),
):
    """Download a report file."""
    from fastapi.responses import FileResponse
    
    # In a real implementation, retrieve file path from database
    # For now, return placeholder
    raise HTTPException(status_code=501, detail="Not implemented")

