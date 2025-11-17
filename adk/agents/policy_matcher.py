"""Policy matcher agent for compliance matching."""

from typing import Dict, Any, List
import uuid
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.message_bus import MessageType
from ..core.logger import get_logger
from ..rag.retriever import Retriever
from ..tools.llm_client import get_llm_client
from ..models.models import ComplianceFinding, ComplianceStatus, Severity, ComplianceGap

logger = get_logger(__name__)


class PolicyMatcherAgent(BaseAgent):
    """Matches data practices against compliance regulations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = Retriever()
        self.llm_client = None
    
    async def initialize(self) -> None:
        """Initialize policy matcher."""
        await super().initialize()
        try:
            self.llm_client = get_llm_client()
        except Exception as e:
            self.logger.warning("LLM client not available", error=str(e))
        self.logger.info("Policy matcher agent initialized")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match data practices against compliance regulations.
        
        Args:
            input_data: Matching input containing:
                - framework: Compliance framework name
                - data_practices: List of data practices to check
                - scan_results: Results from risk scanner
                
        Returns:
            Compliance findings and gaps
        """
        framework = input_data.get("framework", "GDPR")
        data_practices = input_data.get("data_practices", [])
        scan_results = input_data.get("scan_results", {})
        
        self.logger.info("Starting policy matching", framework=framework)
        
        findings = []
        gaps = []
        
        # Retrieve relevant regulations
        for practice in data_practices:
            # Use RAG to find relevant regulations
            relevant_regs = await self.retriever.retrieve_relevant(
                data_practice=practice.get("description", ""),
                context=practice,
                top_k=5
            )
            
            # Analyze compliance for each practice
            for reg in relevant_regs:
                finding = await self._analyze_compliance(
                    practice,
                    reg,
                    framework
                )
                if finding:
                    findings.append(finding)
            
            # Identify gaps
            gap = await self._identify_gap(practice, relevant_regs, framework)
            if gap:
                gaps.append(gap)
        
        # Notify coordinator
        if self.message_bus:
            await self.send_message(
                MessageType.RESULT,
                {
                    "framework": framework,
                    "findings": [f.dict() for f in findings],
                    "gaps": [g.dict() for g in gaps],
                },
                receiver="coordinator",
            )
        
        return {
            "framework": framework,
            "findings": [f.dict() for f in findings],
            "gaps": [g.dict() for g in gaps],
        }
    
    async def _analyze_compliance(
        self,
        practice: Dict[str, Any],
        regulation: Dict[str, Any],
        framework: str
    ) -> ComplianceFinding:
        """Analyze compliance of a practice against a regulation."""
        # Use LLM to analyze compliance if available
        if self.llm_client:
            prompt = f"""
            Analyze the following data practice against this regulation:
            
            Data Practice: {practice.get('description', '')}
            Regulation: {regulation.get('text', '')[:500]}
            
            Determine:
            1. Compliance status (compliant, non_compliant, partial, unknown)
            2. Severity (low, medium, high, critical)
            3. Specific article or section if applicable
            4. Recommendation for remediation if non-compliant
            
            Respond in JSON format.
            """
            
            try:
                analysis = await self.llm_client.generate(prompt)
                # Parse LLM response (simplified)
                status = ComplianceStatus.NON_COMPLIANT
                severity = Severity.MEDIUM
            except Exception as e:
                self.logger.error("LLM analysis failed", error=str(e))
                status = ComplianceStatus.UNKNOWN
                severity = Severity.LOW
        
        finding = ComplianceFinding(
            finding_id=str(uuid.uuid4()),
            regulation=regulation.get("metadata", {}).get("name", framework),
            article=regulation.get("metadata", {}).get("article"),
            status=status,
            severity=severity,
            description=f"Compliance check for {practice.get('description', '')}",
            evidence=[regulation.get("text", "")[:200]],
            recommendation="Review and align data practices with regulation requirements",
            detected_at=datetime.utcnow(),
            agent_id=self.agent_id,
        )
        
        return finding
    
    async def _identify_gap(
        self,
        practice: Dict[str, Any],
        regulations: List[Dict[str, Any]],
        framework: str
    ) -> ComplianceGap:
        """Identify compliance gaps."""
        # Simplified gap identification
        gap = ComplianceGap(
            gap_id=str(uuid.uuid4()),
            regulation=framework,
            requirement="Data processing must comply with regulation",
            current_state=practice.get("description", "Unknown"),
            required_state="Compliant with regulation requirements",
            severity=Severity.MEDIUM,
            remediation_steps=[
                "Review current data practices",
                "Align with regulation requirements",
                "Implement necessary controls",
            ],
            detected_at=datetime.utcnow(),
        )
        
        return gap
