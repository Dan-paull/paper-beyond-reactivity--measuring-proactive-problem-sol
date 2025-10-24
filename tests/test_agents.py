"""
Tests for PROBE benchmark agents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from probe.agents import SimpleReactiveAgent, SimpleProactiveAgent
from probe.tasks import CodeDebuggingTask


def test_reactive_agent():
    """Test reactive agent behavior."""
    agent = SimpleReactiveAgent()

    assert agent.agent_id == "reactive_001"
    assert agent.name == "Simple Reactive Agent"

    # Create a simple context
    context = {
        "task": "Debug a web scraper",
        "error_message": "AttributeError",
        "available_actions": ["analyze_code", "check_environment_variables"]
    }

    action = agent.decide_action(context, [])

    # Reactive agent should go straight to analyzing code
    assert action.type == "analyze_code"
    assert len(agent.action_history) == 0  # Not recorded yet

    print("✓ ReactiveAgent tests passed")


def test_proactive_agent():
    """Test proactive agent behavior."""
    agent = SimpleProactiveAgent()

    assert agent.agent_id == "proactive_001"
    assert agent.name == "Simple Proactive Agent"

    context = {
        "task": "Debug a web scraper",
        "error_message": "AttributeError",
        "available_actions": ["analyze_code", "check_environment_variables", "check_dependencies"]
    }

    action = agent.decide_action(context, [])

    # Proactive agent should check environment first
    assert action.type in ["check_environment_variables", "check_dependencies", "check_configuration_files"]
    assert agent.phase == "investigation"

    print("✓ ProactiveAgent tests passed")


def test_agent_on_task():
    """Test agent execution on a full task."""
    agent = SimpleProactiveAgent()
    task = CodeDebuggingTask()

    context = task.start()
    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        action = agent.decide_action(context, [])
        result = task.process_action(action.to_dict())

        if not agent.should_continue(context, result):
            break

        iteration += 1

    task_result = task.evaluate()

    # Proactive agent should achieve reasonable success
    assert task_result.proactivity_score > 0.3
    assert len(task_result.bottlenecks_identified) > 0

    print("✓ Agent-on-task integration tests passed")


def test_agent_reset():
    """Test agent reset functionality."""
    agent = SimpleProactiveAgent()

    # Simulate some actions
    agent.current_action_count = 5
    agent.phase = "completion"

    agent.reset()

    assert agent.current_action_count == 0
    assert agent.phase == "investigation"
    assert len(agent.action_history) == 0

    print("✓ Agent reset tests passed")


if __name__ == "__main__":
    test_reactive_agent()
    test_proactive_agent()
    test_agent_on_task()
    test_agent_reset()

    print("\n✓ All agent tests passed!")
