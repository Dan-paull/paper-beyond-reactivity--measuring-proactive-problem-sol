"""
Benchmark runner for the PROBE evaluation framework.

Orchestrates task execution and agent evaluation.
"""

from typing import List, Dict, Any
from ..tasks.base import Task
from ..agents.base import Agent
from .metrics import calculate_proactivity_metrics, EvaluationResult, aggregate_metrics


class Benchmark:
    """
    Main benchmark class for evaluating agents on proactive problem-solving tasks.

    The benchmark:
    1. Runs agents on a suite of tasks
    2. Collects action traces and results
    3. Computes proactivity metrics
    4. Aggregates results across tasks
    """

    def __init__(self, tasks: List[Task], verbose: bool = False):
        """
        Initialize the benchmark.

        Args:
            tasks: List of tasks to evaluate on
            verbose: Whether to print detailed progress
        """
        self.tasks = tasks
        self.verbose = verbose
        self.results: List[EvaluationResult] = []

    def run_agent(self, agent: Agent, task: Task, max_iterations: int = 20) -> EvaluationResult:
        """
        Run a single agent on a single task.

        Args:
            agent: The agent to evaluate
            task: The task to run
            max_iterations: Maximum number of action iterations

        Returns:
            EvaluationResult with metrics and details
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Running: {agent.name} on {task.task_id}")
            print(f"Task: {task.description}")
            print(f"{'='*60}\n")

        # Reset agent and start task
        agent.reset()
        context = task.start()

        # Action loop
        iteration = 0
        action_history = []

        while iteration < max_iterations:
            # Agent decides next action
            action = agent.decide_action(context, action_history)

            if self.verbose:
                print(f"[Iteration {iteration + 1}] Action: {action.type}")
                if action.reasoning:
                    print(f"  Reasoning: {action.reasoning}")

            # Process action in task environment
            result = task.process_action(action.to_dict())

            if self.verbose:
                print(f"  Result: {result.get('status', 'unknown')}")
                if 'findings' in result:
                    print(f"  Findings: {result['findings']}")
                if 'message' in result:
                    print(f"  Message: {result['message']}")

            # Record history
            action_history.append({
                "iteration": iteration,
                "action": action.to_dict(),
                "result": result
            })

            # Check if agent wants to continue
            if not agent.should_continue(context, result):
                if self.verbose:
                    print(f"\n  Agent stopped after {iteration + 1} iterations")
                break

            iteration += 1

        # Evaluate task completion
        task_result = task.evaluate()

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Task Complete: {'SUCCESS' if task_result.success else 'FAILED'}")
            print(f"Proactivity Score: {task_result.proactivity_score:.3f}")
            print(f"Efficiency Score: {task_result.efficiency_score:.3f}")
            print(f"Bottlenecks Identified: {len(task_result.bottlenecks_identified)}/{task_result.details['bottlenecks_total']}")
            print(f"Bottlenecks Resolved: {len(task_result.bottlenecks_resolved)}/{task_result.details['bottlenecks_total']}")
            print(f"{'='*60}\n")

        # Calculate metrics
        metrics = calculate_proactivity_metrics(task_result)

        return EvaluationResult(
            task_id=task.task_id,
            agent_id=agent.agent_id,
            success=task_result.success,
            metrics=metrics,
            details={
                "task_description": task.description,
                "task_difficulty": task.difficulty,
                "total_iterations": iteration + 1,
                "action_history": action_history,
                **task_result.details
            }
        )

    def evaluate_agent(self, agent: Agent) -> Dict[str, Any]:
        """
        Evaluate an agent on all tasks in the benchmark.

        Args:
            agent: The agent to evaluate

        Returns:
            Dictionary with aggregated results and individual task results
        """
        print(f"\n{'#'*60}")
        print(f"# EVALUATING: {agent.name}")
        print(f"# Tasks: {len(self.tasks)}")
        print(f"{'#'*60}\n")

        results = []

        for task in self.tasks:
            result = self.run_agent(agent, task)
            results.append(result)
            self.results.append(result)

        # Aggregate metrics
        aggregated = aggregate_metrics(results)

        print(f"\n{'#'*60}")
        print(f"# FINAL RESULTS: {agent.name}")
        print(f"{'#'*60}")
        print(f"Overall Proactivity Score: {aggregated['mean_overall_proactivity']:.3f} ± {aggregated['std_overall_proactivity']:.3f}")
        print(f"Success Rate: {aggregated['success_rate']:.1%}")
        print(f"Search Score: {aggregated['mean_search_score']:.3f}")
        print(f"Identification Score: {aggregated['mean_identification_score']:.3f}")
        print(f"Resolution Score: {aggregated['mean_resolution_score']:.3f}")
        print(f"Efficiency Score: {aggregated['mean_efficiency_score']:.3f}")
        print(f"{'#'*60}\n")

        return {
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "aggregated_metrics": aggregated,
            "individual_results": [r.to_dict() for r in results]
        }

    def compare_agents(self, agents: List[Agent]) -> Dict[str, Any]:
        """
        Compare multiple agents on the benchmark.

        Args:
            agents: List of agents to compare

        Returns:
            Dictionary with comparison results
        """
        comparison_results = []

        for agent in agents:
            result = self.evaluate_agent(agent)
            comparison_results.append(result)

        # Create comparison summary
        print(f"\n{'='*60}")
        print("AGENT COMPARISON SUMMARY")
        print(f"{'='*60}")
        print(f"{'Agent':<25} {'Proactivity':<15} {'Success Rate':<15}")
        print(f"{'-'*60}")

        for result in comparison_results:
            agent_name = result["agent_name"]
            proactivity = result["aggregated_metrics"]["mean_overall_proactivity"]
            success_rate = result["aggregated_metrics"]["success_rate"]
            print(f"{agent_name:<25} {proactivity:<15.3f} {success_rate:<15.1%}")

        print(f"{'='*60}\n")

        return {
            "comparison_results": comparison_results,
            "benchmark_tasks": len(self.tasks)
        }
