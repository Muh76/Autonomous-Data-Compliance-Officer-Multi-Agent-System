"""Health check API routes."""

from fastapi import APIRouter, Depends
from typing import Dict, Any

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from app.api.main import get_message_bus, get_state_manager, get_agents

router = APIRouter()


@router.get("/health")
async def health_check(
    message_bus: MessageBus = Depends(get_message_bus),
    state_manager: StateManager = Depends(get_state_manager),
    agents: dict = Depends(get_agents),
) -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "message_bus": "operational",
            "state_manager": "operational",
            "agents": {
                agent_type: "operational"
                for agent_type in agents.keys()
            },
        },
    }

