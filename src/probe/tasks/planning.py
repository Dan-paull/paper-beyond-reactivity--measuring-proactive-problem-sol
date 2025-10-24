"""
Planning tasks for the PROBE benchmark.

These tasks test agents' ability to proactively anticipate dependencies
and potential failures in multi-step planning scenarios.
"""

from typing import Dict, List, Any
from .base import Task


class MultiStepPlanningTask(Task):
    """
    A multi-step planning task where the agent must proactively:
    1. Identify task dependencies
    2. Anticipate resource constraints
    3. Plan for failure scenarios
    before executing the plan.
    """

    def __init__(self):
        super().__init__(
            task_id="planning_001",
            description="Plan and coordinate a software deployment across multiple environments",
            difficulty="hard"
        )

        # Deployment state
        self.dependencies_mapped = False
        self.resources_checked = False
        self.rollback_planned = False
        self.testing_planned = False
        self.deployment_executed = False

        # Environments
        self.environments = {
            "dev": {"status": "ready", "deployed": False},
            "staging": {"status": "ready", "deployed": False},
            "prod": {"status": "ready", "deployed": False}
        }

    def _define_bottlenecks(self) -> List[str]:
        return [
            "missing_dependencies",   # Not identifying required dependencies
            "resource_constraints",   # Not checking resource availability
            "no_rollback_plan",      # No plan for deployment failure
            "no_testing_strategy",   # No validation between stages
        ]

    def get_initial_context(self) -> Dict[str, Any]:
        return {
            "task": self.description,
            "deployment_details": {
                "application": "payment-service",
                "version": "v2.0.0",
                "environments": ["dev", "staging", "prod"],
                "requirements": [
                    "Deploy to dev first for initial testing",
                    "Validate in staging before production",
                    "Zero-downtime deployment in production"
                ]
            },
            "available_actions": [
                "analyze_dependencies",
                "check_resource_availability",
                "create_rollback_plan",
                "design_testing_strategy",
                "deploy_to_environment",
                "validate_deployment",
                "execute_full_deployment"
            ]
        }

    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type", "")
        is_proactive = False

        if action_type == "analyze_dependencies":
            is_proactive = True
            self.dependencies_mapped = True
            self.mark_bottleneck_identified("missing_dependencies")

            result = {
                "status": "success",
                "dependencies": [
                    "database-migration-tool v3.2 required",
                    "redis cluster must be running",
                    "payment-gateway-client v1.5+ needed",
                    "Configuration secrets must be set in each environment"
                ],
                "critical_note": "Database migration must run before app deployment"
            }
            self.mark_bottleneck_resolved("missing_dependencies")

        elif action_type == "check_resource_availability":
            is_proactive = True
            self.resources_checked = True
            self.mark_bottleneck_identified("resource_constraints")

            result = {
                "status": "success",
                "resources": {
                    "dev": "Sufficient resources (2GB RAM, 1 CPU available)",
                    "staging": "Sufficient resources (4GB RAM, 2 CPU available)",
                    "prod": "WARNING: Only 60% capacity available, may need scaling"
                },
                "recommendation": "Scale production environment before deployment"
            }
            if action.get("scale_prod"):
                self.mark_bottleneck_resolved("resource_constraints")
                result["status"] = "success - production scaled"

        elif action_type == "create_rollback_plan":
            is_proactive = True
            self.rollback_planned = True
            self.mark_bottleneck_identified("no_rollback_plan")

            result = {
                "status": "success",
                "rollback_plan": {
                    "automated_checks": [
                        "Health check endpoints must respond within 2s",
                        "Error rate must stay below 1%",
                        "Payment processing success rate >= 99%"
                    ],
                    "rollback_trigger": "Automatic rollback if checks fail for 2 minutes",
                    "rollback_steps": [
                        "Switch load balancer to previous version",
                        "Revert database migration if needed",
                        "Notify on-call team"
                    ]
                }
            }
            self.mark_bottleneck_resolved("no_rollback_plan")

        elif action_type == "design_testing_strategy":
            is_proactive = True
            self.testing_planned = True
            self.mark_bottleneck_identified("no_testing_strategy")

            result = {
                "status": "success",
                "testing_strategy": {
                    "dev": ["Unit tests", "Integration tests", "Manual smoke test"],
                    "staging": ["Full regression suite", "Load testing", "Security scan"],
                    "prod": ["Canary deployment to 10% traffic", "Monitor for 30 minutes", "Gradual rollout"]
                },
                "validation_criteria": "All tests must pass before proceeding to next environment"
            }
            self.mark_bottleneck_resolved("no_testing_strategy")

        elif action_type == "deploy_to_environment":
            env = action.get("environment")
            if env not in self.environments:
                result = {"status": "error", "message": "Invalid environment"}
            elif not self.dependencies_mapped:
                result = {
                    "status": "failed",
                    "message": "Deployment failed: missing dependency information"
                }
            else:
                self.environments[env]["deployed"] = True
                result = {
                    "status": "success",
                    "message": f"Successfully deployed to {env}"
                }
            is_proactive = False

        elif action_type == "validate_deployment":
            env = action.get("environment")
            if env in self.environments and self.environments[env]["deployed"]:
                # Validation success depends on testing strategy
                if self.testing_planned:
                    result = {
                        "status": "success",
                        "message": f"Validation passed for {env}",
                        "tests_run": "All planned tests executed successfully"
                    }
                else:
                    result = {
                        "status": "partial",
                        "message": f"Basic validation passed for {env}, but comprehensive testing not planned"
                    }
            else:
                result = {
                    "status": "error",
                    "message": f"Cannot validate {env} - not deployed yet"
                }
            is_proactive = False

        elif action_type == "execute_full_deployment":
            # Success depends on how much proactive work was done
            bottlenecks_resolved = len(self.resolved_bottlenecks)

            if bottlenecks_resolved >= 3:
                self.deployment_executed = True
                # Deploy to all environments
                for env in self.environments:
                    self.environments[env]["deployed"] = True

                result = {
                    "status": "success",
                    "message": "Full deployment completed successfully across all environments",
                    "deployment_quality": "Excellent - all bottlenecks addressed",
                    "downtime": "Zero downtime achieved"
                }
            elif bottlenecks_resolved >= 2:
                self.deployment_executed = True
                result = {
                    "status": "partial",
                    "message": "Deployment completed but with some risks",
                    "warnings": "Some bottlenecks not addressed - monitoring closely"
                }
            else:
                result = {
                    "status": "failed",
                    "message": "Deployment failed due to unaddressed dependencies and lack of planning",
                    "errors": "Multiple critical issues encountered"
                }
            is_proactive = False

        else:
            result = {
                "status": "error",
                "message": f"Unknown action type: {action_type}"
            }

        self.record_action(action, is_proactive)
        return result

    def check_completion(self) -> bool:
        # Task complete if deployment executed successfully with at least 3/4 bottlenecks resolved
        return self.deployment_executed and len(self.resolved_bottlenecks) >= 3
