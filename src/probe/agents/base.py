"""
Base agent interface for the PROBE benchmark.

Defines the abstract interface that all agents must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class AgentAction:
    """
    Represents an action taken by an agent.

    Attributes:
        type: The type of action being taken
        parameters: Additional parameters for the action
        reasoning: The agent's reasoning for taking this action
    """
    type: str
    parameters: Dict[str, Any]
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary format."""
        return {
            "type": self.type,
            **self.parameters
        }


class Agent(ABC):
    """
    Abstract base class for agents that interact with PROBE tasks.

    Agents must implement methods to:
    1. Process task context and available actions
    2. Decide what action to take next
    3. Determine when the task is complete
    """

    def __init__(self, agent_id: str, name: str):
        """
        Initialize the agent.

        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for the agent
        """
        self.agent_id = agent_id
        self.name = name
        self.action_history: List[AgentAction] = []

    @abstractmethod
    def decide_action(self, context: Dict[str, Any], action_history: List[Dict[str, Any]]) -> AgentAction:
        """
        Decide the next action to take given the current context.

        Args:
            context: Current task context and available information
            action_history: History of previous actions and their results

        Returns:
            The next action to take
        """
        pass

    @abstractmethod
    def should_continue(self, context: Dict[str, Any], last_result: Dict[str, Any]) -> bool:
        """
        Determine if the agent should continue taking actions.

        Args:
            context: Current task context
            last_result: Result of the last action taken

        Returns:
            True if the agent should continue, False otherwise
        """
        pass

    def reset(self):
        """Reset the agent's state for a new task."""
        self.action_history.clear()
