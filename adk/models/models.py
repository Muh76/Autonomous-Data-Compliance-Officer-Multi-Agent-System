"""Pydantic models for data structures."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for findings and risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class RiskCategory(str, Enum):
    """Risk categories."""
    DATA_PRIVACY = "data_privacy"
    SECURITY = "security"
    ACCESS_CONTROL = "access_control"
    DATA_RETENTION = "data_retention"
    PROCESSING = "processing"
    TRANSFER = "transfer"
    OTHER = "other"


class ComplianceFinding(BaseModel):
    """Represents a compliance finding."""
    finding_id: str = Field(..., description="Unique finding identifier")
    regulation: str = Field(..., description="Regulation or standard name")
    article: Optional[str] = Field(None, description="Specific article or section")
    status: ComplianceStatus = Field(..., description="Compliance status")
    severity: Severity = Field(..., description="Severity of the finding")
    description: str = Field(..., description="Description of the finding")
    evidence: List[str] = Field(default_factory=list, description="Evidence items")
    recommendation: Optional[str] = Field(None, description="Recommendation for remediation")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str = Field(..., description="Agent that detected this finding")


class RiskAssessment(BaseModel):
    """Represents a risk assessment."""
    risk_id: str = Field(..., description="Unique risk identifier")
    category: RiskCategory = Field(..., description="Risk category")
    severity: Severity = Field(..., description="Risk severity")
    title: str = Field(..., description="Risk title")
    description: str = Field(..., description="Risk description")
    likelihood: float = Field(..., ge=0.0, le=1.0, description="Likelihood score (0-1)")
    impact: float = Field(..., ge=0.0, le=1.0, description="Impact score (0-1)")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    affected_data: List[str] = Field(default_factory=list, description="Affected data types")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str = Field(..., description="Agent that detected this risk")


class PolicyRegulation(BaseModel):
    """Represents a policy or regulation."""
    regulation_id: str = Field(..., description="Unique regulation identifier")
    name: str = Field(..., description="Regulation name")
    version: str = Field(..., description="Regulation version")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    content: str = Field(..., description="Regulation content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    indexed_at: Optional[datetime] = Field(None, description="When it was indexed")


class ComplianceGap(BaseModel):
    """Represents a gap between current state and compliance requirements."""
    gap_id: str = Field(..., description="Unique gap identifier")
    regulation: str = Field(..., description="Regulation name")
    requirement: str = Field(..., description="Specific requirement")
    current_state: str = Field(..., description="Current state description")
    required_state: str = Field(..., description="Required state description")
    severity: Severity = Field(..., description="Gap severity")
    remediation_steps: List[str] = Field(default_factory=list, description="Steps to remediate")
    estimated_effort: Optional[str] = Field(None, description="Estimated remediation effort")
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class ScanResult(BaseModel):
    """Represents a data scan result."""
    scan_id: str = Field(..., description="Unique scan identifier")
    source: str = Field(..., description="Data source identifier")
    scan_type: str = Field(..., description="Type of scan")
    started_at: datetime = Field(..., description="Scan start time")
    completed_at: Optional[datetime] = Field(None, description="Scan completion time")
    items_scanned: int = Field(default=0, description="Number of items scanned")
    findings: List[ComplianceFinding] = Field(default_factory=list, description="Findings from scan")
    risks: List[RiskAssessment] = Field(default_factory=list, description="Risks detected")
    status: str = Field(default="completed", description="Scan status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional scan metadata")


class Report(BaseModel):
    """Represents a compliance report."""
    report_id: str = Field(..., description="Unique report identifier")
    title: str = Field(..., description="Report title")
    report_type: str = Field(..., description="Type of report")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Agent that generated the report")
    summary: str = Field(..., description="Executive summary")
    findings: List[ComplianceFinding] = Field(default_factory=list, description="Compliance findings")
    risks: List[RiskAssessment] = Field(default_factory=list, description="Risk assessments")
    gaps: List[ComplianceGap] = Field(default_factory=list, description="Compliance gaps")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    format: str = Field(default="json", description="Report format")


class AgentMessage(BaseModel):
    """Represents a message between agents."""
    message_id: str = Field(..., description="Unique message identifier")
    sender: str = Field(..., description="Sender agent ID")
    receiver: Optional[str] = Field(None, description="Receiver agent ID (None for broadcast)")
    message_type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")




