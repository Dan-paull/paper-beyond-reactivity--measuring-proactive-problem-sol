"""
Base classes for PROBE benchmark tasks.

This module defines the core abstractions for creating proactive problem-solving tasks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime


class TaskState(Enum):
    """Represents the current state of a task."""
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """
    Encapsulates the result of a task execution.

    Attributes:
        success: Whether the task objective was achieved
        proactivity_score: Score measuring proactive behavior (0-1)
        efficiency_score: Score measuring resource efficiency (0-1)
        actions_taken: List of actions the agent took
        bottlenecks_identified: List of bottlenecks the agent identified
        bottlenecks_resolved: List of bottlenecks the agent resolved
        completion_time: Time taken to complete the task
        details: Additional details about the execution
    """
    success: bool
    proactivity_score: float
    efficiency_score: float
    actions_taken: List[str] = field(default_factory=list)
    bottlenecks_identified: List[str] = field(default_factory=list)
    bottlenecks_resolved: List[str] = field(default_factory=list)
    completion_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class Task(ABC):
    """
    Abstract base class for PROBE benchmark tasks.

    Each task contains strategic bottlenecks that require proactive problem-solving.
    Tasks evaluate an agent's ability to:
    1. Search for unspecified issues
    2. Identify specific bottlenecks
    3. Execute appropriate resolutions
    """

    def __init__(self, task_id: str, description: str, difficulty: str = "medium"):
        """
        Initialize a task.

        Args:
            task_id: Unique identifier for the task
            description: Description of the task objective
            difficulty: Task difficulty level (easy, medium, hard)
        """
        self.task_id = task_id
        self.description = description
        self.difficulty = difficulty
        self.state = TaskState.INITIALIZED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Track agent behavior
        self.action_history: List[Dict[str, Any]] = []
        self.proactive_actions: List[str] = []
        self.reactive_actions: List[str] = []

        # Task-specific bottlenecks
        self.bottlenecks = self._define_bottlenecks()
        self.identified_bottlenecks: List[str] = []
        self.resolved_bottlenecks: List[str] = []

    @abstractmethod
    def _define_bottlenecks(self) -> List[str]:
        """
        Define the bottlenecks embedded in this task.

        Returns:
            List of bottleneck identifiers
        """
        pass

    @abstractmethod
    def get_initial_context(self) -> Dict[str, Any]:
        """
        Get the initial context presented to the agent.

        Returns:
            Dictionary containing initial task information
        """
        pass

    @abstractmethod
    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an action taken by the agent.

        Args:
            action: Dictionary describing the agent's action

        Returns:
            Dictionary containing the result/feedback from the action
        """
        pass

    @abstractmethod
    def check_completion(self) -> bool:
        """
        Check if the task has been completed successfully.

        Returns:
            True if the task objective has been achieved
        """
        pass

    def start(self) -> Dict[str, Any]:
        """
        Start the task and return initial context.

        Returns:
            Initial context dictionary
        """
        self.state = TaskState.IN_PROGRESS
        self.start_time = datetime.now()
        return self.get_initial_context()

    def record_action(self, action: Dict[str, Any], is_proactive: bool = False):
        """
        Record an action taken by the agent.

        Args:
            action: The action taken
            is_proactive: Whether this action was proactive or reactive
        """
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "is_proactive": is_proactive
        }
        self.action_history.append(action_record)

        action_desc = str(action)
        if is_proactive:
            self.proactive_actions.append(action_desc)
        else:
            self.reactive_actions.append(action_desc)

    def mark_bottleneck_identified(self, bottleneck_id: str):
        """Mark a bottleneck as identified by the agent."""
        if bottleneck_id in self.bottlenecks and bottleneck_id not in self.identified_bottlenecks:
            self.identified_bottlenecks.append(bottleneck_id)

    def mark_bottleneck_resolved(self, bottleneck_id: str):
        """Mark a bottleneck as resolved by the agent."""
        if bottleneck_id in self.bottlenecks and bottleneck_id not in self.resolved_bottlenecks:
            self.resolved_bottlenecks.append(bottleneck_id)

    def evaluate(self) -> TaskResult:
        """
        Evaluate the task execution and compute scores.

        Returns:
            TaskResult containing evaluation metrics
        """
        self.state = TaskState.COMPLETED if self.check_completion() else TaskState.FAILED
        self.end_time = datetime.now()

        # Calculate completion time
        completion_time = 0.0
        if self.start_time and self.end_time:
            completion_time = (self.end_time - self.start_time).total_seconds()

        # Calculate proactivity score
        proactivity_score = self._calculate_proactivity_score()

        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score()

        return TaskResult(
            success=self.state == TaskState.COMPLETED,
            proactivity_score=proactivity_score,
            efficiency_score=efficiency_score,
            actions_taken=[str(a["action"]) for a in self.action_history],
            bottlenecks_identified=self.identified_bottlenecks.copy(),
            bottlenecks_resolved=self.resolved_bottlenecks.copy(),
            completion_time=completion_time,
            details={
                "total_actions": len(self.action_history),
                "proactive_actions": len(self.proactive_actions),
                "reactive_actions": len(self.reactive_actions),
                "bottlenecks_total": len(self.bottlenecks),
                "bottlenecks_identified": len(self.identified_bottlenecks),
                "bottlenecks_resolved": len(self.resolved_bottlenecks),
            }
        )

    def _calculate_proactivity_score(self) -> float:
        """
        Calculate the proactivity score based on agent behavior.

        The score considers:
        - Ratio of proactive to total actions
        - Bottlenecks identified before being prompted
        - Early problem anticipation

        Returns:
            Score between 0 and 1
        """
        if not self.action_history:
            return 0.0

        # Component 1: Proactive action ratio (40%)
        proactive_ratio = len(self.proactive_actions) / len(self.action_history)

        # Component 2: Bottleneck identification rate (30%)
        bottleneck_id_rate = len(self.identified_bottlenecks) / len(self.bottlenecks) if self.bottlenecks else 0.0

        # Component 3: Bottleneck resolution rate (30%)
        bottleneck_res_rate = len(self.resolved_bottlenecks) / len(self.bottlenecks) if self.bottlenecks else 0.0

        score = (0.4 * proactive_ratio + 0.3 * bottleneck_id_rate + 0.3 * bottleneck_res_rate)
        return min(1.0, max(0.0, score))

    def _calculate_efficiency_score(self) -> float:
        """
        Calculate the efficiency score based on resource usage.

        Considers:
        - Number of actions taken vs. minimum required
        - Time to completion
        - Redundant actions

        Returns:
            Score between 0 and 1
        """
        if not self.action_history:
            return 0.0

        # Simple heuristic: fewer actions (but still successful) = higher efficiency
        # Baseline: assume optimal is about 3 actions per bottleneck
        optimal_actions = max(3, len(self.bottlenecks) * 3)
        actual_actions = len(self.action_history)

        if actual_actions <= optimal_actions:
            return 1.0
        else:
            # Penalize excessive actions
            efficiency = optimal_actions / actual_actions
            return max(0.0, min(1.0, efficiency))
