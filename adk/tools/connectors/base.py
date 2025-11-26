"""Base connector class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseConnector(ABC):
    """Base class for data source connectors."""
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to data source."""
        pass
    
    @abstractmethod
    async def scan(self, depth: int = 1000) -> List[Dict[str, Any]]:
        """Scan data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from data source."""
        pass







