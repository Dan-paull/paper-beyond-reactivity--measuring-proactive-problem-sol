"""
Evaluation metrics for the PROBE benchmark.

Implements the three-stage evaluation framework:
1. Searching for unspecified issues
2. Identifying specific bottlenecks
3. Executing appropriate resolutions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import numpy as np


@dataclass
class ProactivityMetrics:
    """
    Comprehensive metrics for measuring proactive behavior.

    Attributes:
        search_score: Score for discovering unspecified issues (0-1)
        identification_score: Score for identifying bottlenecks (0-1)
        resolution_score: Score for executing solutions (0-1)
        overall_proactivity: Combined proactivity score (0-1)
        efficiency_score: Resource efficiency score (0-1)
        success_rate: Task completion success (0-1)
    """
    search_score: float = 0.0
    identification_score: float = 0.0
    resolution_score: float = 0.0
    overall_proactivity: float = 0.0
    efficiency_score: float = 0.0
    success_rate: float = 0.0

    def __post_init__(self):
        """Calculate overall proactivity score."""
        # Three-stage pipeline weights: Search (30%), Identify (30%), Resolve (40%)
        self.overall_proactivity = (
            0.3 * self.search_score +
            0.3 * self.identification_score +
            0.4 * self.resolution_score
        )


@dataclass
class EvaluationResult:
    """
    Complete evaluation result for an agent on a task.

    Attributes:
        task_id: Identifier of the evaluated task
        agent_id: Identifier of the agent
        success: Whether the task was completed successfully
        metrics: Proactivity and efficiency metrics
        details: Additional details about the evaluation
    """
    task_id: str
    agent_id: str
    success: bool
    metrics: ProactivityMetrics
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "metrics": {
                "search_score": self.metrics.search_score,
                "identification_score": self.metrics.identification_score,
                "resolution_score": self.metrics.resolution_score,
                "overall_proactivity": self.metrics.overall_proactivity,
                "efficiency_score": self.metrics.efficiency_score,
                "success_rate": self.metrics.success_rate,
            },
            "details": self.details
        }


def calculate_proactivity_metrics(task_result: Any) -> ProactivityMetrics:
    """
    Calculate comprehensive proactivity metrics from task result.

    Args:
        task_result: TaskResult object containing execution details

    Returns:
        ProactivityMetrics with calculated scores
    """
    # Stage 1: Search for unspecified issues (proactive action ratio)
    total_actions = task_result.details.get("total_actions", 1)
    proactive_actions = task_result.details.get("proactive_actions", 0)
    search_score = proactive_actions / total_actions if total_actions > 0 else 0.0

    # Stage 2: Identify specific bottlenecks
    total_bottlenecks = task_result.details.get("bottlenecks_total", 1)
    identified_bottlenecks = task_result.details.get("bottlenecks_identified", 0)
    identification_score = identified_bottlenecks / total_bottlenecks if total_bottlenecks > 0 else 0.0

    # Stage 3: Execute resolutions
    resolved_bottlenecks = task_result.details.get("bottlenecks_resolved", 0)
    resolution_score = resolved_bottlenecks / total_bottlenecks if total_bottlenecks > 0 else 0.0

    # Efficiency and success
    efficiency_score = task_result.efficiency_score
    success_rate = 1.0 if task_result.success else 0.0

    return ProactivityMetrics(
        search_score=search_score,
        identification_score=identification_score,
        resolution_score=resolution_score,
        efficiency_score=efficiency_score,
        success_rate=success_rate
    )


def aggregate_metrics(results: List[EvaluationResult]) -> Dict[str, float]:
    """
    Aggregate metrics across multiple evaluation results.

    Args:
        results: List of EvaluationResult objects

    Returns:
        Dictionary with aggregated metrics
    """
    if not results:
        return {
            "mean_search_score": 0.0,
            "mean_identification_score": 0.0,
            "mean_resolution_score": 0.0,
            "mean_overall_proactivity": 0.0,
            "mean_efficiency_score": 0.0,
            "success_rate": 0.0,
            "std_overall_proactivity": 0.0,
        }

    search_scores = [r.metrics.search_score for r in results]
    identification_scores = [r.metrics.identification_score for r in results]
    resolution_scores = [r.metrics.resolution_score for r in results]
    overall_scores = [r.metrics.overall_proactivity for r in results]
    efficiency_scores = [r.metrics.efficiency_score for r in results]
    successes = [1.0 if r.success else 0.0 for r in results]

    return {
        "mean_search_score": float(np.mean(search_scores)),
        "mean_identification_score": float(np.mean(identification_scores)),
        "mean_resolution_score": float(np.mean(resolution_scores)),
        "mean_overall_proactivity": float(np.mean(overall_scores)),
        "mean_efficiency_score": float(np.mean(efficiency_scores)),
        "success_rate": float(np.mean(successes)),
        "std_overall_proactivity": float(np.std(overall_scores)),
    }
