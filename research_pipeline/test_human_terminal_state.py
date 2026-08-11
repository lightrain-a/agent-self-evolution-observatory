from __future__ import annotations

import unittest

from .human_terminal_state import (
    absorbed_child_ids,
    build_human_terminal_state,
    repair_allowed,
    standalone_allowed,
    terminal_parent_ids,
)


class HumanTerminalStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = build_human_terminal_state()

    def test_exact_parent_terminal_distribution(self) -> None:
        self.assertEqual(self.state["summary"]["human_parents"], 26)
        self.assertEqual(
            (self.state["summary"]["p0"], self.state["summary"]["p0_ready"], self.state["summary"]["merge"], self.state["summary"]["drop"]),
            (20, 0, 6, 0),
        )
        self.assertEqual(self.state["summary"]["p0_resolved_lineages"], 26)
        self.assertEqual(self.state["summary"]["revived_to_p0"], 7)
        self.assertEqual(len(terminal_parent_ids()), 26)

    def test_terminal_parents_and_absorbed_children_cannot_reenter_repair(self) -> None:
        self.assertEqual(len(absorbed_child_ids()), 17)
        self.assertTrue(all(not repair_allowed(idea_id) for idea_id in terminal_parent_ids()))
        self.assertTrue(all(not repair_allowed(idea_id) for idea_id in absorbed_child_ids()))
        self.assertTrue(all(not standalone_allowed(idea_id) for idea_id in absorbed_child_ids()))

    def test_required_merges_are_one_way(self) -> None:
        parents = self.state["parents"]
        self.assertEqual(parents["outcome-equivalent-trajectory-contrast"]["merge_into"], "replicated-effect-memory-gate")
        self.assertEqual(parents["causally-verified-experience-admission"]["merge_into"], "regression-gated-self-evolution")
        self.assertEqual(parents["workflow-branch-credit"]["terminal_state"], "p0")
        self.assertIn("failure-localization-before-reflection", parents["workflow-branch-credit"]["absorbed_children"])

    def test_only_seven_extra_methods_remain_standalone(self) -> None:
        independent = self.state["independent_methods"]
        self.assertEqual(len(independent), 7)
        self.assertEqual(sum(row["terminal_state"] == "p0" for row in independent.values()), 7)
        self.assertEqual(sum(row["terminal_state"] == "p0-ready" for row in independent.values()), 0)
        self.assertEqual({row.get("code") for row in independent.values()}, {"A-6","A-7","B-8","B-9","B-10","E-3","E-4"})
        self.assertIn("replicated-effect-memory-gate", independent)
        self.assertIn("cross-task-effect-transport-certificate", independent)


if __name__ == "__main__":
    unittest.main()
