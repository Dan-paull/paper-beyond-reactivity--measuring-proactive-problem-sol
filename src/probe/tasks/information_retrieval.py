"""
Information retrieval tasks for the PROBE benchmark.

These tasks test agents' ability to proactively gather and verify information
before reaching conclusions.
"""

from typing import Dict, List, Any
from .base import Task


class ResearchTask(Task):
    """
    A research task where the agent must proactively:
    1. Verify source credibility
    2. Cross-reference information
    3. Identify knowledge gaps
    before compiling a report.
    """

    def __init__(self):
        super().__init__(
            task_id="research_001",
            description="Research the environmental impact of electric vehicles and compile a report",
            difficulty="medium"
        )

        # Simulated information sources
        self.sources = {
            "source_a": {
                "name": "EV Industry Blog",
                "credibility": "low",
                "data": "EVs reduce emissions by 90%",
                "checked": False
            },
            "source_b": {
                "name": "Scientific Journal Nature",
                "credibility": "high",
                "data": "EVs reduce lifecycle emissions by 30-50% depending on energy grid",
                "checked": False
            },
            "source_c": {
                "name": "Automotive Manufacturer Site",
                "credibility": "medium",
                "data": "EVs have zero tailpipe emissions",
                "checked": False
            }
        }

        self.credibility_checked = False
        self.cross_referenced = False
        self.gaps_identified = False
        self.report_compiled = False

    def _define_bottlenecks(self) -> List[str]:
        return [
            "unchecked_sources",      # Using sources without verifying credibility
            "conflicting_data",       # Not reconciling conflicting information
            "missing_context",        # Not identifying missing contextual data
        ]

    def get_initial_context(self) -> Dict[str, Any]:
        return {
            "task": self.description,
            "available_sources": [
                {"id": "source_a", "name": "EV Industry Blog"},
                {"id": "source_b", "name": "Scientific Journal Nature"},
                {"id": "source_c", "name": "Automotive Manufacturer Site"}
            ],
            "available_actions": [
                "check_source_credibility",
                "retrieve_data_from_source",
                "cross_reference_data",
                "identify_knowledge_gaps",
                "compile_report"
            ]
        }

    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type", "")
        is_proactive = False

        if action_type == "check_source_credibility":
            is_proactive = True
            self.credibility_checked = True
            self.mark_bottleneck_identified("unchecked_sources")

            source_id = action.get("source_id", "all")
            if source_id == "all":
                result = {
                    "status": "success",
                    "credibility_ratings": {
                        "source_a": "Low - industry promotional content",
                        "source_b": "High - peer-reviewed scientific journal",
                        "source_c": "Medium - manufacturer data, potential bias"
                    }
                }
                self.mark_bottleneck_resolved("unchecked_sources")
            else:
                if source_id in self.sources:
                    self.sources[source_id]["checked"] = True
                    result = {
                        "status": "success",
                        "credibility": self.sources[source_id]["credibility"],
                        "source": self.sources[source_id]["name"]
                    }
                else:
                    result = {"status": "error", "message": "Invalid source ID"}

        elif action_type == "retrieve_data_from_source":
            source_id = action.get("source_id")
            if source_id in self.sources:
                result = {
                    "status": "success",
                    "source": self.sources[source_id]["name"],
                    "data": self.sources[source_id]["data"]
                }
            else:
                result = {"status": "error", "message": "Invalid source ID"}
            is_proactive = False

        elif action_type == "cross_reference_data":
            is_proactive = True
            self.cross_referenced = True
            self.mark_bottleneck_identified("conflicting_data")

            result = {
                "status": "success",
                "findings": [
                    "Source A claims 90% reduction - appears exaggerated",
                    "Source B provides range (30-50%) with scientific backing",
                    "Source C focuses only on tailpipe emissions, ignores manufacturing",
                    "Discrepancy identified: need to clarify lifecycle vs operational emissions"
                ]
            }
            self.mark_bottleneck_resolved("conflicting_data")

        elif action_type == "identify_knowledge_gaps":
            is_proactive = True
            self.gaps_identified = True
            self.mark_bottleneck_identified("missing_context")

            result = {
                "status": "success",
                "gaps": [
                    "Battery manufacturing emissions not fully addressed",
                    "Energy grid composition varies by region",
                    "End-of-life battery recycling impact unclear",
                    "Comparison timeframe not specified (5 years? 10 years?)"
                ]
            }
            self.mark_bottleneck_resolved("missing_context")

        elif action_type == "compile_report":
            self.report_compiled = True

            # Quality depends on proactive work done beforehand
            quality_score = 0
            if self.credibility_checked:
                quality_score += 1
            if self.cross_referenced:
                quality_score += 1
            if self.gaps_identified:
                quality_score += 1

            if quality_score >= 2:
                result = {
                    "status": "success",
                    "report": "Comprehensive report compiled with verified sources and identified limitations",
                    "quality": "high" if quality_score == 3 else "medium"
                }
            else:
                result = {
                    "status": "partial",
                    "report": "Report compiled but may contain unverified claims or missing context",
                    "quality": "low"
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
        # Task complete if report is compiled with at least 2/3 bottlenecks resolved
        return self.report_compiled and len(self.resolved_bottlenecks) >= 2
