"""
Observability module - Tracing and metrics for agent execution.
Provides correlation ID tracking and performance monitoring.
"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextvars import ContextVar
from collections import defaultdict

from ..core.logger import get_logger

logger = get_logger(__name__)

# Context variable for trace ID (thread-safe)
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


class Tracer:
    """
    Distributed tracing for multi-agent workflows.
    
    Tracks agent execution flow using correlation IDs.
    """
    
    def __init__(self):
        """Initialize tracer."""
        self.traces: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        logger.info("Tracer initialized")
    
    @staticmethod
    def start_trace(trace_name: Optional[str] = None) -> str:
        """
        Start a new trace.
        
        Args:
            trace_name: Optional name for the trace
            
        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())
        trace_id_var.set(trace_id)
        
        logger.info(
            "Trace started",
            trace_id=trace_id,
            trace_name=trace_name or "unnamed"
        )
        
        return trace_id
    
    @staticmethod
    def get_trace_id() -> Optional[str]:
        """
        Get current trace ID.
        
        Returns:
            Current trace ID or None
        """
        return trace_id_var.get()
    
    @staticmethod
    def end_trace():
        """End current trace."""
        trace_id = trace_id_var.get()
        if trace_id:
            logger.info("Trace ended", trace_id=trace_id)
            trace_id_var.set(None)
    
    def log_event(
        self,
        event_type: str,
        agent_name: str,
        data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log a trace event.
        
        Args:
            event_type: Type of event (start, end, message, error)
            agent_name: Name of the agent
            data: Additional event data
            duration_ms: Optional duration in milliseconds
        """
        trace_id = self.get_trace_id()
        if not trace_id:
            return
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_name": agent_name,
            "data": data or {},
            "duration_ms": duration_ms
        }
        
        self.traces[trace_id].append(event)
        
        logger.debug(
            "Trace event",
            trace_id=trace_id,
            event_type=event_type,
            agent=agent_name
        )
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a trace.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            List of trace events
        """
        return self.traces.get(trace_id, [])
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """
        Get summary of a trace.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            Trace summary with statistics
        """
        events = self.get_trace(trace_id)
        if not events:
            return {"error": "Trace not found"}
        
        agents_involved = set(e["agent_name"] for e in events)
        total_duration = sum(e.get("duration_ms", 0) for e in events if e.get("duration_ms"))
        
        return {
            "trace_id": trace_id,
            "total_events": len(events),
            "agents_involved": list(agents_involved),
            "total_duration_ms": total_duration,
            "start_time": events[0]["timestamp"],
            "end_time": events[-1]["timestamp"],
            "events": events
        }


class MetricsCollector:
    """
    Collect and aggregate performance metrics.
    
    Tracks:
    - Agent execution times
    - Success/failure rates
    - Message counts
    - Resource usage
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        logger.info("Metrics collector initialized")
    
    def record_duration(self, metric_name: str, duration_ms: float):
        """
        Record a duration metric.
        
        Args:
            metric_name: Name of the metric
            duration_ms: Duration in milliseconds
        """
        self.metrics[metric_name].append(duration_ms)
        logger.debug("Duration recorded", metric=metric_name, duration_ms=duration_ms)
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """
        Increment a counter.
        
        Args:
            counter_name: Name of the counter
            value: Value to increment by
        """
        self.counters[counter_name] += value
        logger.debug("Counter incremented", counter=counter_name, value=self.counters[counter_name])
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Statistics (mean, median, min, max, p95, p99)
        """
        values = self.metrics.get(metric_name, [])
        if not values:
            return {"error": "No data"}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "mean": sum(values) / n,
            "median": sorted_values[n // 2],
            "min": min(values),
            "max": max(values),
            "p95": sorted_values[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_values[int(n * 0.99)] if n > 0 else 0
        }
    
    def get_counter(self, counter_name: str) -> int:
        """
        Get counter value.
        
        Args:
            counter_name: Name of the counter
            
        Returns:
            Counter value
        """
        return self.counters.get(counter_name, 0)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics and counters.
        
        Returns:
            All metrics data
        """
        metrics_stats = {
            name: self.get_metric_stats(name)
            for name in self.metrics.keys()
        }
        
        return {
            "metrics": metrics_stats,
            "counters": dict(self.counters)
        }
    
    def reset(self):
        """Reset all metrics and counters."""
        self.metrics.clear()
        self.counters.clear()
        logger.info("Metrics reset")


# Global instances
_tracer = Tracer()
_metrics = MetricsCollector()


def get_tracer() -> Tracer:
    """Get global tracer instance."""
    return _tracer


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance."""
    return _metrics


class traced:
    """
    Decorator for tracing function execution.
    
    Usage:
        @traced(agent_name="RiskScanner")
        async def scan_data(self, data):
            ...
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize decorator.
        
        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
    
    def __call__(self, func):
        """Wrap function with tracing."""
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            metrics = get_metrics()
            
            # Log start event
            tracer.log_event("start", self.agent_name, {"function": func.__name__})
            
            # Track execution time
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Log success
                duration_ms = (time.time() - start_time) * 1000
                tracer.log_event("end", self.agent_name, {"status": "success"}, duration_ms)
                
                # Record metrics
                metrics.record_duration(f"{self.agent_name}.{func.__name__}", duration_ms)
                metrics.increment_counter(f"{self.agent_name}.success")
                
                return result
                
            except Exception as e:
                # Log error
                duration_ms = (time.time() - start_time) * 1000
                tracer.log_event("error", self.agent_name, {"error": str(e)}, duration_ms)
                
                # Record metrics
                metrics.increment_counter(f"{self.agent_name}.error")
                
                raise
        
        return wrapper
