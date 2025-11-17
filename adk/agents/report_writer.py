"""Report writer agent for generating compliance reports."""

from typing import Dict, Any, List
import uuid
import os
from datetime import datetime
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.message_bus import MessageType
from ..core.logger import get_logger
from ..config import get_config
from ..models.models import Report, ComplianceFinding, RiskAssessment, ComplianceGap

logger = get_logger(__name__)


class ReportWriterAgent(BaseAgent):
    """Generates compliance reports in various formats."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_dir = Path(__file__).parent.parent / "tools" / "templates"
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """Initialize report writer."""
        await super().initialize()
        config = get_config()
        self.output_dir = Path(config.get("reports", {}).get("output_dir", "./data/reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Report writer agent initialized")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a compliance report.
        
        Args:
            input_data: Report input containing:
                - report_type: Type of report
                - findings: List of compliance findings
                - risks: List of risk assessments
                - gaps: List of compliance gaps
                - format: Output format (pdf, html, json)
                
        Returns:
            Report generation result
        """
        report_type = input_data.get("report_type", "compliance")
        findings = input_data.get("findings", [])
        risks = input_data.get("risks", [])
        gaps = input_data.get("gaps", [])
        output_format = input_data.get("format", "json")
        
        self.logger.info("Generating report", report_type=report_type, format=output_format)
        
        # Create report model
        report = Report(
            report_id=str(uuid.uuid4()),
            title=f"Compliance Report - {report_type.title()}",
            report_type=report_type,
            generated_at=datetime.utcnow(),
            generated_by=self.agent_id,
            summary=self._generate_summary(findings, risks, gaps),
            findings=[ComplianceFinding(**f) if isinstance(f, dict) else f for f in findings],
            risks=[RiskAssessment(**r) if isinstance(r, dict) else r for r in risks],
            gaps=[ComplianceGap(**g) if isinstance(g, dict) else g for g in gaps],
            recommendations=self._generate_recommendations(findings, risks, gaps),
            format=output_format,
        )
        
        # Generate report file
        file_path = await self._generate_report_file(report, output_format)
        report.metadata["file_path"] = str(file_path)
        
        # Notify coordinator
        if self.message_bus:
            await self.send_message(
                MessageType.RESULT,
                {
                    "report_id": report.report_id,
                    "file_path": str(file_path),
                    "format": output_format,
                },
                receiver="coordinator",
            )
        
        return {
            "report_id": report.report_id,
            "file_path": str(file_path),
            "format": output_format,
            "report": report.dict(),
        }
    
    def _generate_summary(
        self,
        findings: List[Any],
        risks: List[Any],
        gaps: List[Any]
    ) -> str:
        """Generate executive summary."""
        summary = f"""
        Compliance Report Summary
        
        Total Findings: {len(findings)}
        Total Risks: {len(risks)}
        Total Gaps: {len(gaps)}
        
        This report provides a comprehensive analysis of compliance status,
        identified risks, and compliance gaps requiring attention.
        """
        return summary.strip()
    
    def _generate_recommendations(
        self,
        findings: List[Any],
        risks: List[Any],
        gaps: List[Any]
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if findings:
            recommendations.append("Address all non-compliant findings identified in the report")
        
        if risks:
            recommendations.append("Implement risk mitigation strategies for high-severity risks")
        
        if gaps:
            recommendations.append("Close identified compliance gaps through process improvements")
        
        if not recommendations:
            recommendations.append("Continue monitoring compliance status")
        
        return recommendations
    
    async def _generate_report_file(self, report: Report, format: str) -> Path:
        """Generate report file in specified format."""
        if format == "json":
            return await self._generate_json_report(report)
        elif format == "html":
            return await self._generate_html_report(report)
        elif format == "pdf":
            return await self._generate_pdf_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def _generate_json_report(self, report: Report) -> Path:
        """Generate JSON report."""
        import json
        
        file_path = self.output_dir / f"{report.report_id}.json"
        
        with open(file_path, "w") as f:
            json.dump(report.dict(), f, indent=2, default=str)
        
        self.logger.info("JSON report generated", file_path=str(file_path))
        return file_path
    
    async def _generate_html_report(self, report: Report) -> Path:
        """Generate HTML report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 20px 0; }}
                .finding {{ border-left: 3px solid #007bff; padding: 10px; margin: 10px 0; }}
                .risk {{ border-left: 3px solid #dc3545; padding: 10px; margin: 10px 0; }}
                .gap {{ border-left: 3px solid #ffc107; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>{report.title}</h1>
            <p><strong>Generated:</strong> {report.generated_at}</p>
            <p><strong>Generated By:</strong> {report.generated_by}</p>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <p>{report.summary}</p>
            </div>
            
            <h2>Findings ({len(report.findings)})</h2>
            {''.join([f'<div class="finding"><h3>{f.regulation}</h3><p>{f.description}</p><p>Status: {f.status.value} | Severity: {f.severity.value}</p></div>' for f in report.findings])}
            
            <h2>Risks ({len(report.risks)})</h2>
            {''.join([f'<div class="risk"><h3>{r.title}</h3><p>{r.description}</p><p>Risk Score: {r.risk_score:.2f} | Severity: {r.severity.value}</p></div>' for r in report.risks])}
            
            <h2>Compliance Gaps ({len(report.gaps)})</h2>
            {''.join([f'<div class="gap"><h3>{g.regulation}</h3><p>{g.requirement}</p><p>Severity: {g.severity.value}</p></div>' for g in report.gaps])}
            
            <h2>Recommendations</h2>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
            </ul>
        </body>
        </html>
        """
        
        file_path = self.output_dir / f"{report.report_id}.html"
        
        with open(file_path, "w") as f:
            f.write(html_content)
        
        self.logger.info("HTML report generated", file_path=str(file_path))
        return file_path
    
    async def _generate_pdf_report(self, report: Report) -> Path:
        """Generate PDF report."""
        # First generate HTML, then convert to PDF
        html_path = await self._generate_html_report(report)
        
        try:
            from weasyprint import HTML
            pdf_path = self.output_dir / f"{report.report_id}.pdf"
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            self.logger.info("PDF report generated", file_path=str(pdf_path))
            return pdf_path
        except ImportError:
            self.logger.warning("WeasyPrint not available, returning HTML instead")
            return html_path
