"""
Example script demonstrating how to run the PROBE benchmark.

This script:
1. Creates a set of tasks
2. Initializes reactive and proactive agents
3. Runs the benchmark
4. Compares agent performance
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from probe.tasks import (
    CodeDebuggingTask,
    SystemDesignTask,
    ResearchTask,
    MultiStepPlanningTask
)
from probe.agents import SimpleReactiveAgent, SimpleProactiveAgent
from probe.evaluation import Benchmark


def main():
    """Run the PROBE benchmark comparing reactive and proactive agents."""

    print("\n" + "="*80)
    print("PROBE: Proactive Resolution Of BottlEnecks")
    print("Benchmark Evaluation")
    print("="*80 + "\n")

    # Create task suite
    tasks = [
        CodeDebuggingTask(),
        SystemDesignTask(),
        ResearchTask(),
        MultiStepPlanningTask(),
    ]

    print(f"Created {len(tasks)} tasks:")
    for task in tasks:
        print(f"  - {task.task_id}: {task.description} [{task.difficulty}]")

    # Initialize agents
    reactive_agent = SimpleReactiveAgent()
    proactive_agent = SimpleProactiveAgent()

    agents = [reactive_agent, proactive_agent]

    # Run benchmark
    benchmark = Benchmark(tasks, verbose=True)
    results = benchmark.compare_agents(agents)

    # Print final comparison
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)

    for result in results["comparison_results"]:
        agent_name = result["agent_name"]
        metrics = result["aggregated_metrics"]

        print(f"\n{agent_name}:")
        print(f"  Overall Proactivity: {metrics['mean_overall_proactivity']:.3f}")
        print(f"  Success Rate: {metrics['success_rate']:.1%}")
        print(f"  Breakdown:")
        print(f"    - Search (finding issues): {metrics['mean_search_score']:.3f}")
        print(f"    - Identification (pinpointing bottlenecks): {metrics['mean_identification_score']:.3f}")
        print(f"    - Resolution (executing solutions): {metrics['mean_resolution_score']:.3f}")

    # Calculate improvement
    reactive_score = results["comparison_results"][0]["aggregated_metrics"]["mean_overall_proactivity"]
    proactive_score = results["comparison_results"][1]["aggregated_metrics"]["mean_overall_proactivity"]

    if reactive_score > 0:
        improvement = ((proactive_score - reactive_score) / reactive_score) * 100
        print(f"\nProactive agent shows {improvement:.1f}% improvement in proactivity")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
