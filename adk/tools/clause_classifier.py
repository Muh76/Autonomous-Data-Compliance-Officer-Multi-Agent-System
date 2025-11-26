"""
Clause Classifier Tool for contract risk detection.
Uses ML model to classify contract clauses by risk level.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import re

from adk.core.logger import get_logger

logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels for contract clauses."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ClauseType(Enum):
    """Types of contract clauses."""
    TERMINATION = "termination"
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    CONFIDENTIALITY = "confidentiality"
    DATA_PROCESSING = "data_processing"
    PAYMENT = "payment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    DISPUTE_RESOLUTION = "dispute_resolution"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    OTHER = "other"


class ClauseClassifier:
    """
    Classifier for contract clauses.
    
    Uses rule-based patterns and keyword matching.
    Can be extended with ML model (e.g., fine-tuned BERT on CUAD dataset).
    """
    
    def __init__(self):
        """Initialize classifier with patterns."""
        self.patterns = self._initialize_patterns()
        logger.info("ClauseClassifier initialized")
    
    def _initialize_patterns(self) -> Dict[ClauseType, List[str]]:
        """Initialize keyword patterns for each clause type."""
        return {
            ClauseType.TERMINATION: [
                r"terminat(e|ion)",
                r"cancel(lation)?",
                r"end (of|the) agreement",
                r"notice period",
                r"early termination"
            ],
            ClauseType.LIABILITY: [
                r"liab(le|ility)",
                r"damages",
                r"limitation of liability",
                r"consequential damages",
                r"indirect damages"
            ],
            ClauseType.INDEMNIFICATION: [
                r"indemnif(y|ication)",
                r"hold harmless",
                r"defend.*against",
                r"third.?party claims"
            ],
            ClauseType.CONFIDENTIALITY: [
                r"confidential(ity)?",
                r"non.?disclosure",
                r"proprietary information",
                r"trade secrets"
            ],
            ClauseType.DATA_PROCESSING: [
                r"personal data",
                r"data processing",
                r"gdpr",
                r"data protection",
                r"data subject rights",
                r"data controller",
                r"data processor"
            ],
            ClauseType.PAYMENT: [
                r"payment",
                r"fees",
                r"invoic(e|ing)",
                r"compensation",
                r"price",
                r"cost"
            ],
            ClauseType.INTELLECTUAL_PROPERTY: [
                r"intellectual property",
                r"copyright",
                r"patent",
                r"trademark",
                r"ownership",
                r"ip rights"
            ],
            ClauseType.DISPUTE_RESOLUTION: [
                r"arbitration",
                r"mediation",
                r"dispute resolution",
                r"litigation",
                r"court"
            ],
            ClauseType.FORCE_MAJEURE: [
                r"force majeure",
                r"act of god",
                r"beyond.*control",
                r"natural disaster"
            ],
            ClauseType.GOVERNING_LAW: [
                r"governing law",
                r"jurisdiction",
                r"applicable law",
                r"venue"
            ]
        }
    
    def classify_clause(self, clause_text: str) -> Dict[str, Any]:
        """
        Classify a single clause.
        
        Args:
            clause_text: Text of the clause
            
        Returns:
            Classification result with type, risk level, and confidence
        """
        clause_lower = clause_text.lower()
        
        # Find matching clause type
        clause_type = ClauseType.OTHER
        max_matches = 0
        
        for ctype, patterns in self.patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, clause_lower))
            if matches > max_matches:
                max_matches = matches
                clause_type = ctype
        
        # Determine risk level based on clause type and content
        risk_level = self._assess_risk(clause_text, clause_type)
        
        # Calculate confidence (simple heuristic)
        confidence = min(max_matches / 3.0, 1.0) if max_matches > 0 else 0.1
        
        result = {
            "clause_type": clause_type.value,
            "risk_level": risk_level.value,
            "confidence": round(confidence, 2),
            "detected_keywords": max_matches,
            "clause_length": len(clause_text),
            "recommendations": self._get_recommendations(clause_type, risk_level)
        }
        
        logger.debug(
            "Clause classified",
            type=clause_type.value,
            risk=risk_level.value,
            confidence=confidence
        )
        
        return result
    
    def _assess_risk(self, clause_text: str, clause_type: ClauseType) -> RiskLevel:
        """
        Assess risk level of a clause.
        
        Args:
            clause_text: Clause text
            clause_type: Detected clause type
            
        Returns:
            Risk level
        """
        clause_lower = clause_text.lower()
        
        # High-risk keywords
        high_risk_keywords = [
            "unlimited liability",
            "no limitation",
            "perpetual",
            "irrevocable",
            "waive all rights",
            "automatic renewal",
            "unilateral"
        ]
        
        # Medium-risk keywords
        medium_risk_keywords = [
            "may terminate",
            "at will",
            "sole discretion",
            "without cause",
            "indemnify"
        ]
        
        # Check for high-risk keywords
        if any(keyword in clause_lower for keyword in high_risk_keywords):
            return RiskLevel.CRITICAL
        
        # Type-specific risk assessment
        if clause_type == ClauseType.LIABILITY:
            if "unlimited" in clause_lower or "no limit" in clause_lower:
                return RiskLevel.CRITICAL
            elif "limitation" in clause_lower:
                return RiskLevel.MEDIUM
        
        elif clause_type == ClauseType.DATA_PROCESSING:
            if "gdpr" in clause_lower or "personal data" in clause_lower:
                return RiskLevel.HIGH
        
        elif clause_type == ClauseType.TERMINATION:
            if "immediate" in clause_lower or "without notice" in clause_lower:
                return RiskLevel.HIGH
            elif "notice" in clause_lower:
                return RiskLevel.MEDIUM
        
        # Check for medium-risk keywords
        if any(keyword in clause_lower for keyword in medium_risk_keywords):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _get_recommendations(self, clause_type: ClauseType, risk_level: RiskLevel) -> List[str]:
        """
        Get recommendations for a clause.
        
        Args:
            clause_type: Clause type
            risk_level: Risk level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("⚠️ Have legal counsel review this clause")
        
        if clause_type == ClauseType.LIABILITY:
            if risk_level == RiskLevel.CRITICAL:
                recommendations.append("Negotiate liability cap")
                recommendations.append("Add mutual liability limitations")
        
        elif clause_type == ClauseType.DATA_PROCESSING:
            recommendations.append("Ensure GDPR compliance")
            recommendations.append("Add data processing agreement (DPA)")
            recommendations.append("Specify data retention periods")
        
        elif clause_type == ClauseType.TERMINATION:
            if risk_level == RiskLevel.HIGH:
                recommendations.append("Negotiate longer notice period")
                recommendations.append("Add termination for cause provisions")
        
        elif clause_type == ClauseType.INDEMNIFICATION:
            recommendations.append("Ensure mutual indemnification")
            recommendations.append("Cap indemnification obligations")
        
        return recommendations
    
    def classify_contract(self, contract_text: str) -> Dict[str, Any]:
        """
        Classify all clauses in a contract.
        
        Args:
            contract_text: Full contract text
            
        Returns:
            Classification results for all clauses
        """
        # Split contract into clauses (simple sentence-based split)
        clauses = self._split_into_clauses(contract_text)
        
        results = []
        risk_summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for i, clause in enumerate(clauses, 1):
            if len(clause.strip()) < 20:  # Skip very short clauses
                continue
            
            classification = self.classify_clause(clause)
            classification["clause_number"] = i
            classification["clause_text"] = clause[:100] + "..." if len(clause) > 100 else clause
            
            results.append(classification)
            risk_summary[classification["risk_level"]] += 1
        
        overall_risk = self._calculate_overall_risk(risk_summary)
        
        return {
            "total_clauses": len(results),
            "risk_summary": risk_summary,
            "overall_risk": overall_risk,
            "clauses": results,
            "high_risk_clauses": [c for c in results if c["risk_level"] in ["high", "critical"]]
        }
    
    def _split_into_clauses(self, contract_text: str) -> List[str]:
        """Split contract into clauses."""
        # Simple split by periods followed by newline or numbered sections
        clauses = re.split(r'\n\s*\d+\.|\n\n+', contract_text)
        return [c.strip() for c in clauses if c.strip()]
    
    def _calculate_overall_risk(self, risk_summary: Dict[str, int]) -> str:
        """Calculate overall contract risk."""
        if risk_summary["critical"] > 0:
            return "critical"
        elif risk_summary["high"] >= 3:
            return "high"
        elif risk_summary["high"] > 0 or risk_summary["medium"] >= 5:
            return "medium"
        else:
            return "low"


# Global classifier instance
_global_classifier: Optional[ClauseClassifier] = None


def get_classifier() -> ClauseClassifier:
    """Get global classifier instance."""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = ClauseClassifier()
    return _global_classifier
