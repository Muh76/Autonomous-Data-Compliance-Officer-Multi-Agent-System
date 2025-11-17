"""Simplified storage using SQLite + JSON (replaces SQLAlchemy for MVP)."""

import sqlite3
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import contextlib

from ..core.logger import get_logger

logger = get_logger(__name__)


class SimpleStorage:
    """Simple SQLite + JSON storage (MVP - no SQLAlchemy)."""
    
    def __init__(self, db_path: str = "./data/adco.db"):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info("SimpleStorage initialized", db_path=str(self.db_path))
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Compliance findings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_findings (
                    finding_id TEXT PRIMARY KEY,
                    regulation TEXT NOT NULL,
                    article TEXT,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    evidence TEXT,
                    recommendation TEXT,
                    detected_at TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    report_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Risk assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    risk_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    likelihood REAL NOT NULL,
                    impact REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    affected_data TEXT,
                    mitigation TEXT,
                    detected_at TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    report_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reports table (metadata only - files stored in filesystem)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    generated_by TEXT NOT NULL,
                    summary TEXT,
                    file_path TEXT,
                    format TEXT DEFAULT 'json',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Scan results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_results (
                    scan_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    items_scanned INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'completed',
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    @contextlib.contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_finding(self, finding: Dict[str, Any]) -> None:
        """Save a compliance finding."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO compliance_findings
                (finding_id, regulation, article, status, severity, description,
                 evidence, recommendation, detected_at, agent_id, report_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                finding.get("finding_id"),
                finding.get("regulation"),
                finding.get("article"),
                finding.get("status"),
                finding.get("severity"),
                finding.get("description"),
                json.dumps(finding.get("evidence", [])),
                finding.get("recommendation"),
                finding.get("detected_at"),
                finding.get("agent_id"),
                finding.get("report_id"),
            ))
            conn.commit()
    
    def get_findings(self, report_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get compliance findings, optionally filtered by report_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if report_id:
                cursor.execute(
                    "SELECT * FROM compliance_findings WHERE report_id = ?",
                    (report_id,)
                )
            else:
                cursor.execute("SELECT * FROM compliance_findings")
            
            rows = cursor.fetchall()
            findings = []
            for row in rows:
                finding = dict(row)
                finding["evidence"] = json.loads(finding.get("evidence", "[]"))
                findings.append(finding)
            return findings
    
    def save_risk(self, risk: Dict[str, Any]) -> None:
        """Save a risk assessment."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO risk_assessments
                (risk_id, category, severity, title, description, likelihood,
                 impact, risk_score, affected_data, mitigation, detected_at, agent_id, report_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                risk.get("risk_id"),
                risk.get("category"),
                risk.get("severity"),
                risk.get("title"),
                risk.get("description"),
                risk.get("likelihood"),
                risk.get("impact"),
                risk.get("risk_score"),
                json.dumps(risk.get("affected_data", [])),
                risk.get("mitigation"),
                risk.get("detected_at"),
                risk.get("agent_id"),
                risk.get("report_id"),
            ))
            conn.commit()
    
    def get_risks(self, report_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get risk assessments, optionally filtered by report_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if report_id:
                cursor.execute(
                    "SELECT * FROM risk_assessments WHERE report_id = ?",
                    (report_id,)
                )
            else:
                cursor.execute("SELECT * FROM risk_assessments")
            
            rows = cursor.fetchall()
            risks = []
            for row in rows:
                risk = dict(row)
                risk["affected_data"] = json.loads(risk.get("affected_data", "[]"))
                risks.append(risk)
            return risks
    
    def save_report_metadata(self, report: Dict[str, Any]) -> None:
        """Save report metadata (actual report stored in filesystem)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO reports
                (report_id, title, report_type, generated_at, generated_by, summary, file_path, format)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.get("report_id"),
                report.get("title"),
                report.get("report_type"),
                report.get("generated_at"),
                report.get("generated_by"),
                report.get("summary"),
                report.get("file_path"),
                report.get("format", "json"),
            ))
            conn.commit()
    
    def get_report_metadata(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report metadata by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent reports."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

