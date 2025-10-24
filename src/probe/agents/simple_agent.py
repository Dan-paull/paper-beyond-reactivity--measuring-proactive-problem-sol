"""
Simple agent implementations for testing and demonstration.

Includes both reactive and proactive agent strategies.
"""

from typing import Dict, Any, List
from .base import Agent, AgentAction


class SimpleReactiveAgent(Agent):
    """
    A simple reactive agent that only responds to explicit errors/problems.

    This agent represents a baseline approach - it takes minimal actions
    and doesn't proactively investigate potential issues.
    """

    def __init__(self):
        super().__init__(
            agent_id="reactive_001",
            name="Simple Reactive Agent"
        )
        self.max_actions = 10
        self.current_action_count = 0

    def decide_action(self, context: Dict[str, Any], action_history: List[Dict[str, Any]]) -> AgentAction:
        """
        React to explicit problems only.

        Strategy: Take the most direct action to address the stated problem.
        """
        self.current_action_count += 1

        task_desc = context.get("task", "")
        error_msg = context.get("error_message", "")
        available_actions = context.get("available_actions", [])

        # Simple reactive logic - address the stated problem directly
        if "debug" in task_desc.lower() or error_msg:
            # Go straight to analyzing code
            return AgentAction(
                type="analyze_code",
                parameters={},
                reasoning="Responding to the reported error by analyzing the code"
            )
        elif "design" in task_desc.lower():
            # Go straight to designing
            return AgentAction(
                type="design_architecture",
                parameters={},
                reasoning="Addressing the design task directly"
            )
        elif "research" in task_desc.lower():
            # Retrieve data without checking sources
            return AgentAction(
                type="retrieve_data_from_source",
                parameters={"source_id": "source_a"},
                reasoning="Gathering information to complete the research"
            )
        elif "deployment" in task_desc.lower() or "deploy" in task_desc.lower():
            # Deploy without planning
            return AgentAction(
                type="deploy_to_environment",
                parameters={"environment": "dev"},
                reasoning="Starting deployment as requested"
            )
        else:
            # Default: compile/propose solution
            if "compile_report" in available_actions:
                return AgentAction(
                    type="compile_report",
                    parameters={},
                    reasoning="Completing the task"
                )
            elif "propose_solution" in available_actions:
                return AgentAction(
                    type="propose_solution",
                    parameters={},
                    reasoning="Proposing a solution"
                )
            else:
                # Use first available action
                action_type = available_actions[0] if available_actions else "unknown"
                return AgentAction(
                    type=action_type,
                    parameters={},
                    reasoning="Taking available action"
                )

    def should_continue(self, context: Dict[str, Any], last_result: Dict[str, Any]) -> bool:
        """Stop after a few actions or on success."""
        if self.current_action_count >= self.max_actions:
            return False
        if last_result.get("status") == "success":
            return False
        return True

    def reset(self):
        """Reset for a new task."""
        super().reset()
        self.current_action_count = 0


class SimpleProactiveAgent(Agent):
    """
    A simple proactive agent that anticipates issues before being told.

    This agent follows a systematic approach:
    1. First, investigate potential bottlenecks
    2. Then, address identified issues
    3. Finally, complete the main task
    """

    def __init__(self):
        super().__init__(
            agent_id="proactive_001",
            name="Simple Proactive Agent"
        )
        self.max_actions = 15
        self.current_action_count = 0
        self.phase = "investigation"  # investigation -> resolution -> completion

    def decide_action(self, context: Dict[str, Any], action_history: List[Dict[str, Any]]) -> AgentAction:
        """
        Proactively investigate and resolve issues.

        Strategy:
        1. Investigation phase: Check for potential problems
        2. Resolution phase: Fix identified issues
        3. Completion phase: Complete the main task
        """
        self.current_action_count += 1

        task_desc = context.get("task", "")
        available_actions = context.get("available_actions", [])

        # Phase 1: Investigation - proactively look for issues
        if self.phase == "investigation":
            return self._investigate_action(task_desc, available_actions, action_history)

        # Phase 2: Resolution - fix identified issues
        elif self.phase == "resolution":
            return self._resolution_action(task_desc, available_actions, action_history)

        # Phase 3: Completion - complete the task
        else:
            return self._completion_action(task_desc, available_actions, action_history)

    def _investigate_action(self, task_desc: str, available_actions: List[str],
                           action_history: List[Dict[str, Any]]) -> AgentAction:
        """Proactively investigate potential issues."""

        # Check what we've already investigated
        investigated = [a.get("action", {}).get("type", "") for a in action_history]

        if "debug" in task_desc.lower():
            # Proactively check environment, dependencies, and config
            if "check_environment_variables" in available_actions and "check_environment_variables" not in investigated:
                return AgentAction(
                    type="check_environment_variables",
                    parameters={"set_api_key": True},
                    reasoning="Proactively checking environment setup before debugging"
                )
            elif "check_dependencies" in available_actions and "check_dependencies" not in investigated:
                return AgentAction(
                    type="check_dependencies",
                    parameters={"update_dependencies": True},
                    reasoning="Verifying dependencies are correct before debugging"
                )
            elif "check_configuration_files" in available_actions and "check_configuration_files" not in investigated:
                return AgentAction(
                    type="check_configuration_files",
                    parameters={"create_config": True},
                    reasoning="Ensuring configuration is complete before debugging"
                )
            else:
                self.phase = "resolution"
                return self._resolution_action(task_desc, available_actions, action_history)

        elif "design" in task_desc.lower():
            # Proactively consider scalability, security, bottlenecks
            if "analyze_scale_requirements" in available_actions and "analyze_scale_requirements" not in investigated:
                return AgentAction(
                    type="analyze_scale_requirements",
                    parameters={},
                    reasoning="Proactively analyzing scalability requirements"
                )
            elif "plan_security_measures" in available_actions and "plan_security_measures" not in investigated:
                return AgentAction(
                    type="plan_security_measures",
                    parameters={},
                    reasoning="Proactively planning security measures"
                )
            elif "design_database_schema" in available_actions and "design_database_schema" not in investigated:
                return AgentAction(
                    type="design_database_schema",
                    parameters={},
                    reasoning="Proactively designing scalable database schema"
                )
            else:
                self.phase = "resolution"
                return self._resolution_action(task_desc, available_actions, action_history)

        elif "research" in task_desc.lower():
            # Proactively check sources and cross-reference
            if "check_source_credibility" in available_actions and "check_source_credibility" not in investigated:
                return AgentAction(
                    type="check_source_credibility",
                    parameters={"source_id": "all"},
                    reasoning="Proactively verifying source credibility"
                )
            elif "cross_reference_data" in available_actions and "cross_reference_data" not in investigated:
                return AgentAction(
                    type="cross_reference_data",
                    parameters={},
                    reasoning="Proactively cross-referencing data from multiple sources"
                )
            elif "identify_knowledge_gaps" in available_actions and "identify_knowledge_gaps" not in investigated:
                return AgentAction(
                    type="identify_knowledge_gaps",
                    parameters={},
                    reasoning="Proactively identifying missing information"
                )
            else:
                self.phase = "resolution"
                return self._resolution_action(task_desc, available_actions, action_history)

        elif "deployment" in task_desc.lower() or "deploy" in task_desc.lower():
            # Proactively plan deployment
            if "analyze_dependencies" in available_actions and "analyze_dependencies" not in investigated:
                return AgentAction(
                    type="analyze_dependencies",
                    parameters={},
                    reasoning="Proactively analyzing deployment dependencies"
                )
            elif "check_resource_availability" in available_actions and "check_resource_availability" not in investigated:
                return AgentAction(
                    type="check_resource_availability",
                    parameters={"scale_prod": True},
                    reasoning="Proactively checking resource constraints"
                )
            elif "create_rollback_plan" in available_actions and "create_rollback_plan" not in investigated:
                return AgentAction(
                    type="create_rollback_plan",
                    parameters={},
                    reasoning="Proactively planning for potential failures"
                )
            elif "design_testing_strategy" in available_actions and "design_testing_strategy" not in investigated:
                return AgentAction(
                    type="design_testing_strategy",
                    parameters={},
                    reasoning="Proactively designing validation strategy"
                )
            else:
                self.phase = "resolution"
                return self._resolution_action(task_desc, available_actions, action_history)

        else:
            self.phase = "completion"
            return self._completion_action(task_desc, available_actions, action_history)

    def _resolution_action(self, task_desc: str, available_actions: List[str],
                          action_history: List[Dict[str, Any]]) -> AgentAction:
        """Address the core task after investigation."""

        if "debug" in task_desc.lower():
            self.phase = "completion"
            return AgentAction(
                type="analyze_code",
                parameters={},
                reasoning="Now analyzing code after ensuring environment is ready"
            )
        elif "design" in task_desc.lower():
            self.phase = "completion"
            return AgentAction(
                type="design_architecture",
                parameters={},
                reasoning="Creating architecture design with bottlenecks addressed"
            )
        elif "research" in task_desc.lower():
            self.phase = "completion"
            # Retrieve data from high-credibility source
            return AgentAction(
                type="retrieve_data_from_source",
                parameters={"source_id": "source_b"},
                reasoning="Retrieving data from verified high-credibility source"
            )
        else:
            self.phase = "completion"
            return self._completion_action(task_desc, available_actions, action_history)

    def _completion_action(self, task_desc: str, available_actions: List[str],
                          action_history: List[Dict[str, Any]]) -> AgentAction:
        """Complete the task."""

        if "debug" in task_desc.lower():
            if "propose_fix" in available_actions:
                return AgentAction(
                    type="propose_fix",
                    parameters={},
                    reasoning="Proposing fix after thorough preparation"
                )
        elif "design" in task_desc.lower():
            if "propose_solution" in available_actions:
                return AgentAction(
                    type="propose_solution",
                    parameters={},
                    reasoning="Proposing comprehensive solution"
                )
        elif "research" in task_desc.lower():
            if "compile_report" in available_actions:
                return AgentAction(
                    type="compile_report",
                    parameters={},
                    reasoning="Compiling report with verified information"
                )
        elif "deploy" in task_desc.lower():
            if "execute_full_deployment" in available_actions:
                return AgentAction(
                    type="execute_full_deployment",
                    parameters={},
                    reasoning="Executing deployment with all preparations complete"
                )

        # Fallback
        if available_actions:
            return AgentAction(
                type=available_actions[0],
                parameters={},
                reasoning="Completing task"
            )

        return AgentAction(
            type="complete",
            parameters={},
            reasoning="Task complete"
        )

    def should_continue(self, context: Dict[str, Any], last_result: Dict[str, Any]) -> bool:
        """Continue until success or max actions reached."""
        if self.current_action_count >= self.max_actions:
            return False
        if last_result.get("status") == "success" and self.phase == "completion":
            return False
        return True

    def reset(self):
        """Reset for a new task."""
        super().reset()
        self.current_action_count = 0
        self.phase = "investigation"
