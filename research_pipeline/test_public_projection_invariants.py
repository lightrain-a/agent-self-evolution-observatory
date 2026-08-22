from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .config import PROJECT_ROOT
from .public_projection_invariants import validate_public_control_plane


GEN = PROJECT_ROOT / "generated"


def load(name: str) -> dict:
    return json.loads((GEN / name).read_text(encoding="utf-8"))


class PublicProjectionInvariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.research = load("research-items.json")
        cls.registry = load("paper-registry.json")
        cls.system = load("research-system-state.json")
        cls.dashboard = load("research-dashboard.json")
        cls.memory = load("research-memory-wiki.json")

    def validate(self, **overrides) -> list[str]:
        return validate_public_control_plane(
            research_state=overrides.get("research", self.research),
            paper_registry=overrides.get("registry", self.registry),
            research_system=overrides.get("system", self.system),
            research_dashboard=overrides.get("dashboard", self.dashboard),
            research_memory=overrides.get("memory", self.memory),
        )

    def test_current_public_control_plane_is_cross_projection_consistent(self) -> None:
        self.assertEqual(self.validate(), [])

    def test_dashboard_research_action_drift_is_detected(self) -> None:
        dashboard = copy.deepcopy(self.dashboard)
        row = next(row for row in dashboard["attention"] if row["code"] == "E-7")
        row["next_action_class"] = "REOPEN_CONDITION_REQUIRED"
        errors = self.validate(dashboard=dashboard)
        self.assertIn("ResearchDashboard action mismatch:E-7", errors)

    def test_system_readiness_alias_drift_is_detected(self) -> None:
        system = copy.deepcopy(self.system)
        system["paper_acceptance"]["summary"]["gate_clean_submission_ready_papers"] = 5
        errors = self.validate(system=system)
        self.assertIn("ResearchSystem Paper Acceptance summary mismatch:gate_clean_submission_ready_papers", errors)

    def test_missing_review_lesson_is_detected(self) -> None:
        memory = copy.deepcopy(self.memory)
        lessons = [row for row in memory["entries"] if row.get("kind") == "REVIEW_LESSON"]
        victim = lessons[0]
        memory["entries"] = [row for row in memory["entries"] if row.get("memory_id") != victim.get("memory_id")]
        memory["summary"]["review_lessons"] = len(lessons) - 1
        errors = self.validate(memory=memory)
        self.assertIn("ResearchMemory review lessons do not match reviewed PaperStates", errors)

    def test_paper_next_action_drift_is_detected(self) -> None:
        registry = copy.deepcopy(self.registry)
        temporal = next(row for row in registry["papers"] if row["paper_id"] == "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK")
        temporal["primary_next_action"]["action_class"] = "NO_INTERNAL_ACTION"
        errors = self.validate(registry=registry)
        self.assertIn("Paper action mismatch:D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK:action_class", errors)


if __name__ == "__main__":
    unittest.main()
