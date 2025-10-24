"""
Software engineering tasks for the PROBE benchmark.

These tasks test agents' ability to identify and resolve bottlenecks in
code debugging and system design scenarios.
"""

from typing import Dict, List, Any
from .base import Task


class CodeDebuggingTask(Task):
    """
    A debugging task with hidden dependencies and configuration issues.

    The agent must proactively identify:
    1. Missing environment variables
    2. Incorrect dependency versions
    3. Configuration file issues
    before attempting to debug the actual code bug.
    """

    def __init__(self):
        super().__init__(
            task_id="code_debug_001",
            description="Debug a web scraper that fails to retrieve data",
            difficulty="medium"
        )

        # Simulate a codebase with the bug
        self.code = """
import requests
from bs4 import BeautifulSoup

def scrape_articles(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('article'):
        title = item.find('h2').text
        articles.append(title)

    return articles

if __name__ == '__main__':
    url = 'https://example-news-site.com/articles'
    print(scrape_articles(url))
"""

        # Environment state
        self.env_vars = {}  # Missing required API_KEY
        self.dependencies_checked = False
        self.config_checked = False
        self.code_analyzed = False
        self.bug_fixed = False

    def _define_bottlenecks(self) -> List[str]:
        return [
            "missing_env_var",      # Missing API_KEY environment variable
            "wrong_dependencies",   # BeautifulSoup version incompatibility
            "missing_config",       # Missing config.json with rate limit settings
        ]

    def get_initial_context(self) -> Dict[str, Any]:
        return {
            "task": self.description,
            "error_message": "Script fails with: AttributeError: 'NoneType' object has no attribute 'text'",
            "code": self.code,
            "available_actions": [
                "check_environment_variables",
                "check_dependencies",
                "check_configuration_files",
                "analyze_code",
                "run_tests",
                "propose_fix"
            ]
        }

    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type", "")
        is_proactive = False

        if action_type == "check_environment_variables":
            is_proactive = True  # This is proactive - not explicitly asked for
            self.mark_bottleneck_identified("missing_env_var")
            result = {
                "status": "success",
                "findings": "Environment variable API_KEY is not set. This may be required for authentication."
            }
            if action.get("set_api_key"):
                self.env_vars["API_KEY"] = "dummy_key"
                self.mark_bottleneck_resolved("missing_env_var")
                result["findings"] += " API_KEY has been set."

        elif action_type == "check_dependencies":
            is_proactive = True  # Proactive - checking before being told to
            self.dependencies_checked = True
            self.mark_bottleneck_identified("wrong_dependencies")
            result = {
                "status": "success",
                "findings": "beautifulsoup4==4.9.0 is installed, but version 4.11.0+ is recommended for better error handling."
            }
            if action.get("update_dependencies"):
                self.mark_bottleneck_resolved("wrong_dependencies")
                result["findings"] += " Dependencies updated to compatible versions."

        elif action_type == "check_configuration_files":
            is_proactive = True  # Proactive - anticipating configuration needs
            self.config_checked = True
            self.mark_bottleneck_identified("missing_config")
            result = {
                "status": "success",
                "findings": "config.json is missing. This file should contain rate_limit settings to avoid being blocked."
            }
            if action.get("create_config"):
                self.mark_bottleneck_resolved("missing_config")
                result["findings"] += " config.json created with default settings."

        elif action_type == "analyze_code":
            self.code_analyzed = True
            # Only succeeds if bottlenecks are mostly resolved
            resolved_count = len(self.resolved_bottlenecks)
            if resolved_count >= 2:
                result = {
                    "status": "success",
                    "findings": "The bug is in line 9: item.find('h2') returns None when no h2 tag exists. Need to add null check."
                }
            else:
                result = {
                    "status": "partial",
                    "findings": "Code analysis started, but configuration and environment issues may interfere with debugging."
                }
            is_proactive = False  # This is reactive to the error message

        elif action_type == "propose_fix":
            if self.code_analyzed and len(self.resolved_bottlenecks) >= 2:
                self.bug_fixed = True
                result = {
                    "status": "success",
                    "fix": "Add null check: 'title = item.find('h2').text if item.find('h2') else 'No title''"
                }
            else:
                result = {
                    "status": "failed",
                    "message": "Cannot propose fix without proper analysis and environment setup."
                }
            is_proactive = False

        elif action_type == "run_tests":
            result = {
                "status": "success" if self.bug_fixed else "failed",
                "message": "Tests passed!" if self.bug_fixed else "Tests still failing."
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
        # Task is complete if bug is fixed and at least 2/3 bottlenecks are resolved
        return self.bug_fixed and len(self.resolved_bottlenecks) >= 2


class SystemDesignTask(Task):
    """
    A system design task where the agent must proactively identify
    scalability bottlenecks and security concerns before implementation.
    """

    def __init__(self):
        super().__init__(
            task_id="system_design_001",
            description="Design a real-time notification system for a social media platform",
            difficulty="hard"
        )

        self.scalability_considered = False
        self.security_considered = False
        self.database_planned = False
        self.design_proposed = False

    def _define_bottlenecks(self) -> List[str]:
        return [
            "no_load_balancing",    # Missing load balancing strategy
            "no_authentication",    # Missing authentication/authorization
            "single_point_failure", # No redundancy or failover
            "database_bottleneck",  # Database design doesn't scale
        ]

    def get_initial_context(self) -> Dict[str, Any]:
        return {
            "task": self.description,
            "requirements": [
                "Support 1 million+ concurrent users",
                "Real-time delivery (<100ms latency)",
                "Persistent notification history",
                "Multi-device support"
            ],
            "available_actions": [
                "analyze_scale_requirements",
                "design_database_schema",
                "plan_security_measures",
                "design_architecture",
                "identify_bottlenecks",
                "propose_solution"
            ]
        }

    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type", "")
        is_proactive = False

        if action_type == "analyze_scale_requirements":
            is_proactive = True
            self.scalability_considered = True
            self.mark_bottleneck_identified("no_load_balancing")
            self.mark_bottleneck_identified("single_point_failure")
            result = {
                "status": "success",
                "findings": [
                    "Load balancing will be critical for 1M+ users",
                    "Need redundancy to avoid single point of failure",
                    "WebSocket connections require sticky sessions"
                ]
            }

        elif action_type == "plan_security_measures":
            is_proactive = True
            self.security_considered = True
            self.mark_bottleneck_identified("no_authentication")
            result = {
                "status": "success",
                "findings": [
                    "Need JWT-based authentication for API",
                    "WebSocket connections must be authenticated",
                    "Rate limiting required to prevent abuse"
                ]
            }

        elif action_type == "design_database_schema":
            self.database_planned = True
            self.mark_bottleneck_identified("database_bottleneck")
            result = {
                "status": "success",
                "findings": [
                    "Use partitioned tables for notifications by user_id",
                    "Consider time-series database for notification history",
                    "Implement read replicas for scaling reads"
                ]
            }
            is_proactive = True

        elif action_type == "identify_bottlenecks":
            is_proactive = True
            # Comprehensive bottleneck identification
            identified = []
            if not self.scalability_considered:
                identified.append("Scalability concerns not addressed")
            if not self.security_considered:
                identified.append("Security measures not planned")
            if not self.database_planned:
                identified.append("Database scalability not considered")

            result = {
                "status": "success",
                "bottlenecks": identified if identified else ["All major bottlenecks have been identified"]
            }

        elif action_type == "design_architecture":
            # This action benefits from prior proactive work
            if self.scalability_considered and self.security_considered:
                result = {
                    "status": "success",
                    "architecture": {
                        "load_balancer": "NGINX with sticky sessions",
                        "app_servers": "Horizontally scaled Node.js servers",
                        "message_queue": "Redis Pub/Sub for real-time",
                        "database": "PostgreSQL with read replicas",
                        "auth": "JWT with refresh tokens"
                    }
                }
            else:
                result = {
                    "status": "partial",
                    "message": "Architecture designed but may have scalability or security gaps"
                }
            is_proactive = False

        elif action_type == "propose_solution":
            self.design_proposed = True
            resolved = []
            if self.scalability_considered:
                self.mark_bottleneck_resolved("no_load_balancing")
                self.mark_bottleneck_resolved("single_point_failure")
                resolved.extend(["no_load_balancing", "single_point_failure"])
            if self.security_considered:
                self.mark_bottleneck_resolved("no_authentication")
                resolved.append("no_authentication")
            if self.database_planned:
                self.mark_bottleneck_resolved("database_bottleneck")
                resolved.append("database_bottleneck")

            result = {
                "status": "success" if len(resolved) >= 3 else "partial",
                "resolved_bottlenecks": resolved,
                "solution": "Comprehensive system design with load balancing, authentication, and scalable database"
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
        return self.design_proposed and len(self.resolved_bottlenecks) >= 3
