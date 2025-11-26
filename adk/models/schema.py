"""SQLAlchemy models for database persistence."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class SeverityEnum(str, enum.Enum):
    """Severity enumeration for database."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatusEnum(str, enum.Enum):
    """Compliance status enumeration for database."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ComplianceFindingDB(Base):
    """Database model for compliance findings."""
    __tablename__ = "compliance_findings"
    
    finding_id = Column(String, primary_key=True)
    regulation = Column(String, nullable=False)
    article = Column(String, nullable=True)
    status = Column(SQLEnum(ComplianceStatusEnum), nullable=False)
    severity = Column(SQLEnum(SeverityEnum), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    recommendation = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    agent_id = Column(String, nullable=False)
    report_id = Column(String, ForeignKey("reports.report_id"), nullable=True)
    
    report = relationship("ReportDB", back_populates="findings")


class RiskAssessmentDB(Base):
    """Database model for risk assessments."""
    __tablename__ = "risk_assessments"
    
    risk_id = Column(String, primary_key=True)
    category = Column(String, nullable=False)
    severity = Column(SQLEnum(SeverityEnum), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    likelihood = Column(Float, nullable=False)
    impact = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    affected_data = Column(JSON, nullable=True)
    mitigation = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    agent_id = Column(String, nullable=False)
    report_id = Column(String, ForeignKey("reports.report_id"), nullable=True)
    
    report = relationship("ReportDB", back_populates="risks")


class ReportDB(Base):
    """Database model for reports."""
    __tablename__ = "reports"
    
    report_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    format = Column(String, default="json")
    file_path = Column(String, nullable=True)
    
    findings = relationship("ComplianceFindingDB", back_populates="report")
    risks = relationship("RiskAssessmentDB", back_populates="report")


class ScanResultDB(Base):
    """Database model for scan results."""
    __tablename__ = "scan_results"
    
    scan_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    scan_type = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    items_scanned = Column(Integer, default=0)
    status = Column(String, default="completed")
    metadata = Column(JSON, nullable=True)


class PolicyRegulationDB(Base):
    """Database model for policy regulations."""
    __tablename__ = "policy_regulations"
    
    regulation_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, nullable=True)







