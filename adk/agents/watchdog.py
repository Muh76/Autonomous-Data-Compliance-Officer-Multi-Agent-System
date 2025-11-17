"""Watchdog agent for continuous monitoring."""

from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta

from ..core.base_agent import BaseAgent
from ..core.message_bus import MessageType
from ..core.logger import get_logger
from ..config import get_config

logger = get_logger(__name__)


class WatchdogAgent(BaseAgent):
    """Monitors system continuously and triggers audits."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_monitoring = False
        self._monitor_task = None
        self.last_scan_time = None
    
    async def initialize(self) -> None:
        """Initialize watchdog."""
        await super().initialize()
        config = get_config()
        self.scan_interval = config.get("scanning", {}).get("interval", 3600)
        self.logger.info("Watchdog agent initialized", scan_interval=self.scan_interval)
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring."""
        if self._is_monitoring:
            self.logger.warning("Monitoring already started")
            return
        
        self._is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self._is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Monitoring stopped")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._is_monitoring:
            try:
                await self._perform_monitoring_cycle()
                await asyncio.sleep(self.scan_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitoring cycle error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_monitoring_cycle(self) -> None:
        """Perform a single monitoring cycle."""
        self.logger.info("Starting monitoring cycle")
        
        # Check if scan is needed
        if self._should_trigger_scan():
            await self._trigger_compliance_scan()
        
        # Check system health
        health_status = await self._check_system_health()
        
        # Send status update
        if self.message_bus:
            await self.send_message(
                MessageType.STATUS,
                {
                    "status": "monitoring",
                    "health": health_status,
                    "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
                },
                receiver="coordinator",
            )
        
        self.logger.info("Monitoring cycle completed")
    
    def _should_trigger_scan(self) -> bool:
        """Determine if a compliance scan should be triggered."""
        if self.last_scan_time is None:
            return True
        
        time_since_last_scan = datetime.utcnow() - self.last_scan_time
        return time_since_last_scan.total_seconds() >= self.scan_interval
    
    async def _trigger_compliance_scan(self) -> None:
        """Trigger a compliance scan via coordinator."""
        self.logger.info("Triggering compliance scan")
        
        if self.message_bus:
            await self.send_message(
                MessageType.TASK,
                {
                    "task_type": "audit",
                    "workflow_type": "audit",
                    "data_sources": ["default"],
                    "compliance_frameworks": ["GDPR"],
                },
                receiver="coordinator",
            )
        
        self.last_scan_time = datetime.utcnow()
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health status."""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
        }
        
        # Check message bus
        if self.message_bus:
            health["components"]["message_bus"] = "operational"
        else:
            health["components"]["message_bus"] = "unavailable"
            health["status"] = "degraded"
        
        # Check state manager
        if self.state_manager:
            health["components"]["state_manager"] = "operational"
        else:
            health["components"]["state_manager"] = "unavailable"
            health["status"] = "degraded"
        
        return health
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute watchdog operation.
        
        Args:
            input_data: Watchdog input containing:
                - action: Action to perform (start, stop, status)
                
        Returns:
            Operation result
        """
        action = input_data.get("action", "status")
        
        if action == "start":
            await self.start_monitoring()
            return {"status": "monitoring_started"}
        elif action == "stop":
            await self.stop_monitoring()
            return {"status": "monitoring_stopped"}
        elif action == "status":
            health = await self._check_system_health()
            return {
                "status": "monitoring" if self._is_monitoring else "stopped",
                "health": health,
                "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
            }
        else:
            raise ValueError(f"Unknown action: {action}")
