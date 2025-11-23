"""
Metrics Calculator for Agent Evaluation.
Calculates precision, recall, F1, and other performance metrics.
"""

from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "accuracy": round(self.accuracy, 4),
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "true_negatives": self.true_negatives,
            "false_negatives": self.false_negatives
        }


class MetricsCalculator:
    """
    Calculate evaluation metrics for agent performance.
    
    Supports:
    - Binary classification metrics (precision, recall, F1)
    - Multi-label classification
    - Citation accuracy
    - Quality score aggregation
    """
    
    @staticmethod
    def calculate_binary_metrics(
        predictions: List[bool],
        ground_truth: List[bool]
    ) -> EvaluationMetrics:
        """
        Calculate binary classification metrics.
        
        Args:
            predictions: List of predicted labels (True/False)
            ground_truth: List of actual labels (True/False)
            
        Returns:
            EvaluationMetrics object
        """
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        tp = sum(1 for p, g in zip(predictions, ground_truth) if p and g)
        fp = sum(1 for p, g in zip(predictions, ground_truth) if p and not g)
        tn = sum(1 for p, g in zip(predictions, ground_truth) if not p and not g)
        fn = sum(1 for p, g in zip(predictions, ground_truth) if not p and g)
        
        # Calculate metrics with zero-division handling
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            accuracy=accuracy,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn
        )
    
    @staticmethod
    def calculate_multilabel_metrics(
        predicted_labels: List[Set[str]],
        ground_truth_labels: List[Set[str]]
    ) -> EvaluationMetrics:
        """
        Calculate metrics for multi-label classification.
        
        Args:
            predicted_labels: List of sets of predicted labels
            ground_truth_labels: List of sets of actual labels
            
        Returns:
            EvaluationMetrics object (micro-averaged)
        """
        if len(predicted_labels) != len(ground_truth_labels):
            raise ValueError("Predictions and ground truth must have same length")
        
        total_tp = 0
        total_fp = 0
        total_fn = 0
        
        for pred, truth in zip(predicted_labels, ground_truth_labels):
            tp = len(pred & truth)  # Intersection
            fp = len(pred - truth)  # Predicted but not in truth
            fn = len(truth - pred)  # In truth but not predicted
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
        
        # Micro-averaged metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # For multi-label, accuracy is harder to define, using Jaccard similarity
        total_samples = len(predicted_labels)
        jaccard_scores = [
            len(pred & truth) / len(pred | truth) if len(pred | truth) > 0 else 0.0
            for pred, truth in zip(predicted_labels, ground_truth_labels)
        ]
        accuracy = sum(jaccard_scores) / total_samples if total_samples > 0 else 0.0
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            accuracy=accuracy,
            true_positives=total_tp,
            false_positives=total_fp,
            true_negatives=0,  # Not applicable for multi-label
            false_negatives=total_fn
        )
    
    @staticmethod
    def check_citation_accuracy(
        agent_output: str,
        required_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Check if agent output includes proper citations.
        
        Args:
            agent_output: Text output from agent
            required_citations: Whether citations are required
            
        Returns:
            Dictionary with citation check results
        """
        # Simple heuristic: look for common citation patterns
        citation_patterns = [
            "GDPR Article",
            "HIPAA",
            "CCPA",
            "Section",
            "Regulation",
            "[Source:",
            "Reference:"
        ]
        
        has_citations = any(pattern in agent_output for pattern in citation_patterns)
        
        return {
            "has_citations": has_citations,
            "required": required_citations,
            "passed": has_citations if required_citations else True,
            "patterns_found": [p for p in citation_patterns if p in agent_output]
        }
    
    @staticmethod
    def calculate_quality_scores(
        quality_assessments: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate quality scores from multiple assessments.
        
        Args:
            quality_assessments: List of quality score dictionaries
            
        Returns:
            Aggregated quality metrics
        """
        if not quality_assessments:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "median": 0.0}
        
        # Extract all scores
        all_scores = []
        for assessment in quality_assessments:
            all_scores.extend(assessment.values())
        
        if not all_scores:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "median": 0.0}
        
        all_scores.sort()
        n = len(all_scores)
        
        return {
            "mean": sum(all_scores) / n,
            "min": min(all_scores),
            "max": max(all_scores),
            "median": all_scores[n // 2] if n > 0 else 0.0,
            "count": n
        }
    
    @staticmethod
    def generate_confusion_matrix(
        predictions: List[str],
        ground_truth: List[str],
        labels: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Generate confusion matrix for multi-class classification.
        
        Args:
            predictions: List of predicted class labels
            ground_truth: List of actual class labels
            labels: Optional list of all possible labels
            
        Returns:
            Confusion matrix as nested dictionary
        """
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        # Get all unique labels
        if labels is None:
            labels = sorted(set(predictions + ground_truth))
        
        # Initialize matrix
        matrix = {label: {label2: 0 for label2 in labels} for label in labels}
        
        # Fill matrix
        for pred, truth in zip(predictions, ground_truth):
            if pred in matrix and truth in matrix[pred]:
                matrix[truth][pred] += 1
        
        return matrix
    
    @staticmethod
    def save_metrics_report(
        metrics: Dict[str, Any],
        output_path: Path
    ) -> None:
        """
        Save metrics report to JSON file.
        
        Args:
            metrics: Dictionary of metrics
            output_path: Path to save report
        """
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    @staticmethod
    def format_metrics_table(metrics: EvaluationMetrics) -> str:
        """
        Format metrics as a readable table.
        
        Args:
            metrics: EvaluationMetrics object
            
        Returns:
            Formatted string table
        """
        return f"""
Evaluation Metrics
==================
Precision:  {metrics.precision:.4f}
Recall:     {metrics.recall:.4f}
F1 Score:   {metrics.f1_score:.4f}
Accuracy:   {metrics.accuracy:.4f}

Confusion Matrix
================
True Positives:  {metrics.true_positives}
False Positives: {metrics.false_positives}
True Negatives:  {metrics.true_negatives}
False Negatives: {metrics.false_negatives}
"""


# Example usage
if __name__ == "__main__":
    # Example: Binary classification
    predictions = [True, True, False, True, False, False, True, False]
    ground_truth = [True, False, False, True, False, True, True, False]
    
    calculator = MetricsCalculator()
    metrics = calculator.calculate_binary_metrics(predictions, ground_truth)
    
    print(calculator.format_metrics_table(metrics))
    print("\nMetrics Dict:", metrics.to_dict())
    
    # Example: Multi-label classification
    pred_labels = [
        {"PII", "GDPR"},
        {"HIPAA"},
        {"PII", "CCPA"},
        set()
    ]
    truth_labels = [
        {"PII", "GDPR", "CCPA"},
        {"HIPAA"},
        {"PII"},
        {"GDPR"}
    ]
    
    ml_metrics = calculator.calculate_multilabel_metrics(pred_labels, truth_labels)
    print("\nMulti-label Metrics:", ml_metrics.to_dict())
    
    # Example: Citation check
    output_with_citation = "This violates GDPR Article 6 regarding consent."
    output_without_citation = "This violates privacy rules."
    
    print("\nCitation Check (with):", calculator.check_citation_accuracy(output_with_citation))
    print("Citation Check (without):", calculator.check_citation_accuracy(output_without_citation))
