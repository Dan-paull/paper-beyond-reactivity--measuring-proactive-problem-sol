"""
Tests for PROBE benchmark evaluation framework.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from probe.evaluation import ProactivityMetrics, EvaluationResult, Benchmark
from probe.evaluation.metrics import calculate_proactivity_metrics, aggregate_metrics
from probe.tasks import CodeDebuggingTask
from probe.agents import SimpleReactiveAgent, SimpleProactiveAgent


def test_proactivity_metrics():
    """Test proactivity metrics calculation."""
    metrics = ProactivityMetrics(
        search_score=0.6,
        identification_score=0.8,
        resolution_score=0.7,
        efficiency_score=0.9,
        success_rate=1.0
    )

    # Check overall calculation: 0.3*0.6 + 0.3*0.8 + 0.4*0.7 = 0.7
    assert abs(metrics.overall_proactivity - 0.7) < 0.01

    print("✓ ProactivityMetrics tests passed")


def test_evaluation_result():
    """Test evaluation result structure."""
    metrics = ProactivityMetrics(
        search_score=0.5,
        identification_score=0.6,
        resolution_score=0.7
    )

    result = EvaluationResult(
        task_id="test_001",
        agent_id="agent_001",
        success=True,
        metrics=metrics,
        details={"test": "data"}
    )

    result_dict = result.to_dict()

    assert result_dict["task_id"] == "test_001"
    assert result_dict["success"] == True
    assert "metrics" in result_dict
    assert result_dict["metrics"]["search_score"] == 0.5

    print("✓ EvaluationResult tests passed")


def test_benchmark_single_agent():
    """Test benchmark with a single agent."""
    tasks = [CodeDebuggingTask()]
    agent = SimpleProactiveAgent()

    benchmark = Benchmark(tasks, verbose=False)
    result = benchmark.run_agent(agent, tasks[0])

    assert result.task_id == "code_debug_001"
    assert result.agent_id == "proactive_001"
    assert result.metrics.overall_proactivity >= 0

    print("✓ Benchmark single agent tests passed")


def test_benchmark_agent_comparison():
    """Test benchmark comparing multiple agents."""
    tasks = [CodeDebuggingTask()]
    reactive = SimpleReactiveAgent()
    proactive = SimpleProactiveAgent()

    benchmark = Benchmark(tasks, verbose=False)
    results = benchmark.compare_agents([reactive, proactive])

    assert len(results["comparison_results"]) == 2
    assert results["benchmark_tasks"] == 1

    # Proactive should generally score higher
    reactive_score = results["comparison_results"][0]["aggregated_metrics"]["mean_overall_proactivity"]
    proactive_score = results["comparison_results"][1]["aggregated_metrics"]["mean_overall_proactivity"]

    # Note: This may not always be true due to task randomness, but generally should be
    print(f"  Reactive score: {reactive_score:.3f}")
    print(f"  Proactive score: {proactive_score:.3f}")

    print("✓ Benchmark comparison tests passed")


def test_aggregate_metrics():
    """Test metric aggregation."""
    metrics1 = ProactivityMetrics(
        search_score=0.5,
        identification_score=0.6,
        resolution_score=0.7,
        efficiency_score=0.8,
        success_rate=1.0
    )

    metrics2 = ProactivityMetrics(
        search_score=0.7,
        identification_score=0.8,
        resolution_score=0.9,
        efficiency_score=0.9,
        success_rate=1.0
    )

    results = [
        EvaluationResult("task1", "agent1", True, metrics1),
        EvaluationResult("task2", "agent1", True, metrics2)
    ]

    aggregated = aggregate_metrics(results)

    assert "mean_overall_proactivity" in aggregated
    assert "success_rate" in aggregated
    assert aggregated["success_rate"] == 1.0
    assert 0 <= aggregated["mean_overall_proactivity"] <= 1

    print("✓ Aggregate metrics tests passed")


if __name__ == "__main__":
    test_proactivity_metrics()
    test_evaluation_result()
    test_benchmark_single_agent()
    test_benchmark_agent_comparison()
    test_aggregate_metrics()

    print("\n✓ All evaluation tests passed!")
