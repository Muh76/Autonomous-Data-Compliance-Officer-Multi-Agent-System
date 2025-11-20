"""Structured logging with agent context."""

import logging
import sys
from typing import Optional
import structlog


def get_logger(name: str, agent_id: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger with agent context.
    
    Args:
        name: Logger name (typically module or agent name)
        agent_id: Optional agent identifier for context
        
    Returns:
        Configured structured logger
    """
    logger = structlog.get_logger(name)
    
    if agent_id:
        logger = logger.bind(agent_id=agent_id)
    
    return logger


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )




