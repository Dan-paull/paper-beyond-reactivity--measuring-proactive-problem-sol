"""
Tests for PROBE benchmark tasks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from probe.tasks import CodeDebuggingTask, SystemDesignTask, ResearchTask, MultiStepPlanningTask


def test_code_debugging_task():
    """Test code debugging task initialization and basic operations."""
    task = CodeDebuggingTask()

    assert task.task_id == "code_debug_001"
    assert len(task.bottlenecks) == 3
    assert task.state.value == "initialized"

    # Start task
    context = task.start()
    assert "error_message" in context
    assert "available_actions" in context
    assert task.state.value == "in_progress"

    # Test proactive action
    result = task.process_action({
        "type": "check_environment_variables",
        "set_api_key": True
    })
    assert result["status"] == "success"
    assert "missing_env_var" in task.identified_bottlenecks
    assert "missing_env_var" in task.resolved_bottlenecks

    print("✓ CodeDebuggingTask tests passed")


def test_system_design_task():
    """Test system design task."""
    task = SystemDesignTask()

    assert task.task_id == "system_design_001"
    assert len(task.bottlenecks) == 4

    context = task.start()
    assert "requirements" in context

    # Test proactive scalability analysis
    result = task.process_action({"type": "analyze_scale_requirements"})
    assert result["status"] == "success"
    assert len(task.identified_bottlenecks) > 0

    print("✓ SystemDesignTask tests passed")


def test_research_task():
    """Test research task."""
    task = ResearchTask()

    assert task.task_id == "research_001"
    assert len(task.bottlenecks) == 3

    context = task.start()
    assert "available_sources" in context

    # Test proactive source checking
    result = task.process_action({
        "type": "check_source_credibility",
        "source_id": "all"
    })
    assert result["status"] == "success"
    assert "unchecked_sources" in task.identified_bottlenecks

    print("✓ ResearchTask tests passed")


def test_planning_task():
    """Test multi-step planning task."""
    task = MultiStepPlanningTask()

    assert task.task_id == "planning_001"
    assert len(task.bottlenecks) == 4

    context = task.start()
    assert "deployment_details" in context

    # Test proactive dependency analysis
    result = task.process_action({"type": "analyze_dependencies"})
    assert result["status"] == "success"
    assert "missing_dependencies" in task.identified_bottlenecks

    print("✓ MultiStepPlanningTask tests passed")


def test_task_evaluation():
    """Test task evaluation metrics."""
    task = CodeDebuggingTask()
    task.start()

    # Simulate some actions
    task.process_action({"type": "check_environment_variables", "set_api_key": True})
    task.process_action({"type": "check_dependencies", "update_dependencies": True})
    task.process_action({"type": "analyze_code"})
    task.process_action({"type": "propose_fix"})

    result = task.evaluate()

    assert result.success == True
    assert result.proactivity_score > 0
    assert result.efficiency_score > 0
    assert len(result.bottlenecks_identified) > 0
    assert len(result.bottlenecks_resolved) > 0

    print("✓ Task evaluation tests passed")


if __name__ == "__main__":
    test_code_debugging_task()
    test_system_design_task()
    test_research_task()
    test_planning_task()
    test_task_evaluation()

    print("\n✓ All task tests passed!")
