"""Agents API routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from ..main import get_agents

router = APIRouter()


@router.get("/agents")
async def list_agents(
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """List all agents."""
    return {
        "agents": [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
            }
            for agent in agents.values()
        ]
    }


@router.get("/agents/{agent_type}/status")
async def get_agent_status(
    agent_type: str,
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Get agent status."""
    agent = agents.get(agent_type)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
    
    return {
        "agent_id": agent.agent_id,
        "agent_type": agent.agent_type,
        "status": "operational",
    }




