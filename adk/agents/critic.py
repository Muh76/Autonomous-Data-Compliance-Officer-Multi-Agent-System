"""Critic agent for quality validation."""

from typing import Dict, Any, List
from datetime import datetime

from ..core.adk_agent import ADKAgent
from ..core.message_bus import MessageType
from ..core.logger import get_logger
from ..tools.llm_client import get_llm_client

logger = get_logger(__name__)


class CriticAgent(ADKAgent):
    """Validates quality and consistency of agent outputs."""
    
    def __init__(self, name: str = "Critic", **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def initialize(self) -> None:
        """Initialize critic."""
        await super().initialize()
        try:
            self.llm_client = get_llm_client()
        except Exception as e:
            self.logger.warning("LLM client not available", error=str(e))
        self.logger.info("Critic agent initialized")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate agent output quality.
        
        Args:
            input_data: Validation input containing:
                - agent_output: Output from another agent
                - agent_type: Type of agent that produced output
                - validation_criteria: Criteria for validation
                
        Returns:
            Validation result with quality scores and feedback
        """
        agent_output = input_data.get("agent_output", {})
        agent_type = input_data.get("agent_type", "unknown")
        criteria = input_data.get("validation_criteria", {})
        
        self.logger.info("Validating output", agent_type=agent_type)
        
        validation_result = {
            "validated_at": datetime.utcnow(),
            "agent_type": agent_type,
            "quality_scores": {},
            "issues": [],
            "recommendations": [],
            "is_valid": True,
        }
        
        # Validate completeness
        completeness = await self._validate_completeness(agent_output, agent_type)
        validation_result["quality_scores"]["completeness"] = completeness["score"]
        validation_result["issues"].extend(completeness["issues"])
        
        # Validate consistency
        consistency = await self._validate_consistency(agent_output, agent_type)
        validation_result["quality_scores"]["consistency"] = consistency["score"]
        validation_result["issues"].extend(consistency["issues"])
        
        # Validate accuracy (if LLM available)
        if self.llm_client:
            accuracy = await self._validate_accuracy(agent_output, agent_type)
            validation_result["quality_scores"]["accuracy"] = accuracy["score"]
            validation_result["issues"].extend(accuracy["issues"])
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_recommendations(
            validation_result["issues"]
        )
        
        # Determine overall validity
        avg_score = sum(validation_result["quality_scores"].values()) / len(validation_result["quality_scores"])
        validation_result["is_valid"] = avg_score >= 0.7
        
        # Notify coordinator
        if self.message_bus:
            await self.send_message(
                MessageType.RESULT,
                {
                    "validation_result": validation_result,
                    "agent_type": agent_type,
                },
                receiver="coordinator",
            )
        
        return validation_result
    
    async def _validate_completeness(
        self,
        output: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """Validate output completeness."""
        issues = []
        score = 1.0
        
        # Check required fields based on agent type
        if agent_type == "riskscanner":
            if "risks" not in output:
                issues.append("Missing risks in output")
                score -= 0.3
            if "scan_id" not in output:
                issues.append("Missing scan_id in output")
                score -= 0.2
        
        elif agent_type == "policymatcher":
            if "findings" not in output:
                issues.append("Missing findings in output")
                score -= 0.3
            if "framework" not in output:
                issues.append("Missing framework in output")
                score -= 0.2
        
        elif agent_type == "reportwriter":
            if "report_id" not in output:
                issues.append("Missing report_id in output")
                score -= 0.3
            if "file_path" not in output:
                issues.append("Missing file_path in output")
                score -= 0.2
        
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "issues": issues,
        }
    
    async def _validate_consistency(
        self,
        output: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """Validate output consistency."""
        issues = []
        score = 1.0
        
        # Check for internal consistency
        if agent_type == "riskscanner" and "risks" in output:
            risks = output["risks"]
            if isinstance(risks, list):
                # Check for duplicate risks
                risk_ids = [r.get("risk_id") for r in risks if isinstance(r, dict)]
                if len(risk_ids) != len(set(risk_ids)):
                    issues.append("Duplicate risk IDs found")
                    score -= 0.2
        
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "issues": issues,
        }
    
    async def _validate_accuracy(
        self,
        output: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """Validate output accuracy using LLM."""
        issues = []
        score = 1.0
        
        if not self.llm_client:
            return {"score": 1.0, "issues": []}
        
        # Use LLM to validate accuracy
        prompt = f"""
        Review the following agent output for accuracy and correctness:
        
        Agent Type: {agent_type}
        Output: {str(output)[:1000]}
        
        Identify any inaccuracies, errors, or inconsistencies.
        """
        
        try:
            analysis = await self.llm_client.generate(prompt)
            self.logger.info("Critic LLM Analysis", analysis=analysis)
            
            # Simple parsing of LLM feedback
            analysis_lower = analysis.lower()
            if "inaccurate" in analysis_lower or "error" in analysis_lower or "incorrect" in analysis_lower:
                issues.append("LLM validation identified potential inaccuracies: " + analysis[:100] + "...")
                score -= 0.3
            elif "consistent" in analysis_lower and "accurate" in analysis_lower:
                score = 1.0
            else:
                # Ambiguous result
                score -= 0.1
                
        except Exception as e:
            self.logger.error("LLM validation failed", error=str(e))
            # Don't penalize score if LLM fails
            pass
        
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "issues": issues,
        }
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        if any("Missing" in issue for issue in issues):
            recommendations.append("Ensure all required fields are present in output")
        
        if any("Duplicate" in issue for issue in issues):
            recommendations.append("Review and remove duplicate entries")
        
        if any("accuracy" in issue.lower() for issue in issues):
            recommendations.append("Review output for accuracy and correctness")
        
        if not recommendations:
            recommendations.append("Output quality is acceptable")
        
        return recommendations
