"""FastAPI application for ADCO system."""

# 🔧 FIX: Swap sqlite3 for pysqlite3 to satisfy ChromaDB requirements
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adk.config import get_config, get_settings
from adk.core.logger import setup_logging, get_logger
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.models.database import init_database
from adk.agents import (
    CoordinatorAgent,
    RiskScannerAgent,
    PolicyMatcherAgent,
    ReportWriterAgent,
    CriticAgent,
    WatchdogAgent,
)
from app.api.routes import compliance, reports, agents, health

logger = get_logger(__name__)

# Global instances
message_bus = None
state_manager = None
task_queue = None
agents_registry = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global message_bus, state_manager, task_queue, agents_registry
    
    # Initialize logging
    config = get_config()
    setup_logging(config.get("app", {}).get("log_level", "INFO"))
    
    # Initialize database
    db_config = config.get("database", {})
    init_database(db_config.get("url"))
    
    # Initialize core components
    message_bus = MessageBus()
    state_manager = StateManager()
    task_queue = TaskQueue(max_concurrent=config.get("agents", {}).get("max_concurrent", 5))
    
    # Initialize agents
    coordinator = CoordinatorAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await coordinator.initialize()
    
    risk_scanner = RiskScannerAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await risk_scanner.initialize()
    
    policy_matcher = PolicyMatcherAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await policy_matcher.initialize()
    
    report_writer = ReportWriterAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await report_writer.initialize()
    
    critic = CriticAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await critic.initialize()
    
    watchdog = WatchdogAgent(
        message_bus=message_bus,
        state_manager=state_manager,
        task_queue=task_queue,
    )
    await watchdog.initialize()
    
    agents_registry = {
        "coordinator": coordinator,
        "risk_scanner": risk_scanner,
        "policy_matcher": policy_matcher,
        "report_writer": report_writer,
        "critic": critic,
        "watchdog": watchdog,
    }
    
    logger.info("Application started")
    
    yield
    
    # Cleanup
    for agent in agents_registry.values():
        await agent.shutdown()
    
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="ADCO Multi-Agent System API",
    description="Autonomous Data & Compliance Officer Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get core components
def get_message_bus() -> MessageBus:
    """Get message bus instance."""
    if message_bus is None:
        raise HTTPException(status_code=503, detail="Message bus not initialized")
    return message_bus


def get_state_manager() -> StateManager:
    """Get state manager instance."""
    if state_manager is None:
        raise HTTPException(status_code=503, detail="State manager not initialized")
    return state_manager


def get_task_queue() -> TaskQueue:
    """Get task queue instance."""
    if task_queue is None:
        raise HTTPException(status_code=503, detail="Task queue not initialized")
    return task_queue


def get_agents() -> dict:
    """Get agents registry."""
    if not agents_registry:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    return agents_registry


# Include routers
app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ADCO Multi-Agent System",
        "version": "1.0.0",
        "status": "operational",
    }


if __name__ == "__main__":
    config = get_config()
    api_config = config.get("api", {})
    
    uvicorn.run(
        "app.api.main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=config.get("app", {}).get("debug", False),
    )

