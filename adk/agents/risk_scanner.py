"""Risk scanner agent for data scanning and risk detection."""

from typing import Dict, Any, List
import uuid
from datetime import datetime

from ..core.adk_agent import ADKAgent
from ..core.message_bus import MessageType
from ..core.logger import get_logger
from ..models.models import RiskAssessment, Severity, RiskCategory, ScanResult
from presidio_analyzer import AnalyzerEngine

logger = get_logger(__name__)


class RiskScannerAgent(ADKAgent):
    """Scans data sources and detects risks using Presidio."""
    
    def __init__(self, name: str = "RiskScanner", **kwargs):
        super().__init__(name=name, **kwargs)
        # Store agent-specific attributes in context dict
        self._adco_context["analyzer"] = AnalyzerEngine()
        self._adco_context["scan_patterns"] = {
            "pii": ["email", "ssn", "credit_card", "phone", "address"],
            "sensitive": ["password", "token", "secret", "key"],
            "access": ["permission", "role", "privilege"],
        }
    
    @property
    def analyzer(self):
        return self._adco_context["analyzer"]
    
    @property
    def scan_patterns(self):
        return self._adco_context["scan_patterns"]
    
    async def initialize(self) -> None:
        """Initialize risk scanner."""
        await super().initialize()
        self.logger.info("Risk scanner agent initialized")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan a data source for risks.
        
        Args:
            input_data: Scan input containing:
                - source: Data source identifier
                - source_type: Type of source (database, file, api)
                - scan_depth: Maximum depth to scan
                
        Returns:
            Scan result with detected risks
        """
        source = input_data.get("source")
        source_type = input_data.get("source_type", "database")
        scan_depth = input_data.get("scan_depth", 1000)
        
        self.logger.info("Starting scan", source=source, source_type=source_type)
        
        scan_id = str(uuid.uuid4())
        risks = []
        
        # Perform scan based on source type
        if source_type == "database":
            risks = await self._scan_database(source, scan_depth)
        elif source_type == "file":
            risks = await self._scan_file_system(source, scan_depth)
        elif source_type == "api":
            risks = await self._scan_api(source, scan_depth)
        else:
            self.logger.warning("Unknown source type", source_type=source_type)
        
        # Create scan result
        scan_result = ScanResult(
            scan_id=scan_id,
            source=source,
            scan_type=source_type,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            items_scanned=len(risks),
            risks=risks,
            status="completed",
        )
        
        # Notify coordinator
        if self.message_bus:
            await self.send_message(
                MessageType.RESULT,
                {
                    "scan_id": scan_id,
                    "risks": [r.dict() for r in risks],
                    "source": source,
                },
                receiver="coordinator",
            )
        
        return {
            "scan_id": scan_id,
            "risks": [r.dict() for r in risks],
            "items_scanned": len(risks),
        }
    
    async def _scan_database(self, source: str, depth: int) -> List[RiskAssessment]:
        """Scan a database for risks."""
        # In a real scenario, we would connect to the DB.
        # For this demo, we will simulate scanning text data that represents DB content.
        risks = []
        
        # Simulated data (replace with actual DB fetch in production)
        simulated_data = [
            "User: john.doe@example.com, Phone: 555-0123",
            "API Key: sk-1234567890abcdef",
            "Address: 123 Main St, New York, NY"
        ]
        
        for text in simulated_data:
            detected_risks = await self._scan_text(text, source)
            risks.extend(detected_risks)
            
        return risks

    async def _scan_text(self, text: str, source: str) -> List[RiskAssessment]:
        """Scan text for PII using Presidio."""
        risks = []
        results = self.analyzer.analyze(text=text, language='en')
        
        for result in results:
            risk = RiskAssessment(
                risk_id=str(uuid.uuid4()),
                category=RiskCategory.DATA_PRIVACY,
                severity=Severity.HIGH if result.score > 0.8 else Severity.MEDIUM,
                title=f"Detected {result.entity_type}",
                description=f"Found {result.entity_type} in {source} with confidence {result.score:.2f}",
                likelihood=result.score,
                impact=0.8, # Default high impact for PII
                risk_score=result.score * 0.8,
                affected_data=[result.entity_type],
                detected_at=datetime.utcnow(),
                agent_id=self.agent_id,
            )
            risks.append(risk)
            
        return risks
    
    async def _scan_file_system(self, source: str, depth: int) -> List[RiskAssessment]:
        """Scan file system for risks."""
        # Placeholder implementation
        risks = []
        
        risk = RiskAssessment(
            risk_id=str(uuid.uuid4()),
            category=RiskCategory.ACCESS_CONTROL,
            severity=Severity.MEDIUM,
            title="Insufficient File Permissions",
            description=f"Files in {source} may have overly permissive access controls",
            likelihood=0.6,
            impact=0.5,
            risk_score=0.55,
            affected_data=["file_permissions"],
            detected_at=datetime.utcnow(),
            agent_id=self.agent_id,
        )
        risks.append(risk)
        
        return risks
    
    async def _scan_api(self, source: str, depth: int) -> List[RiskAssessment]:
        """Scan API endpoints for risks."""
        # Placeholder implementation
        risks = []
        
        risk = RiskAssessment(
            risk_id=str(uuid.uuid4()),
            category=RiskCategory.SECURITY,
            severity=Severity.HIGH,
            title="API Authentication Risk",
            description=f"API {source} may lack proper authentication",
            likelihood=0.5,
            impact=0.9,
            risk_score=0.7,
            affected_data=["api_endpoints"],
            detected_at=datetime.utcnow(),
            agent_id=self.agent_id,
        )
        risks.append(risk)
        
        return risks
