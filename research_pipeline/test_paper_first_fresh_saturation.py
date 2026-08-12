from __future__ import annotations

import unittest

from .paper_first_fresh_saturation import build_fresh_saturation_state


class PaperFirstFreshSaturationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=build_fresh_saturation_state()

    def test_current_scan_keeps_zero_survivors_instead_of_forcing_shortlist(self) -> None:
        s=self.state["summary"]
        self.assertEqual((s["drafts_reviewed"],s["survivors"],s["stopped"]),(14,0,14))
        self.assertEqual(self.state["decision"],"NO_FRESH_SURVIVOR_CURRENT_SCAN")
        self.assertTrue(self.state["policy"]["zero_survivors_is_valid_and_preferred_to_forced_shortlist"])
        self.assertFalse(self.state["policy"]["local_validation_authorized"])
        self.assertFalse(self.state["policy"]["p0_authorized"])
        self.assertFalse(self.state["policy"]["gpu_authorized"])

    def test_every_draft_is_reduced_or_collided_before_method_design(self) -> None:
        self.assertTrue(all(row["decision"].startswith("STOP_") for row in self.state["drafts"]))
        self.assertTrue(all(row.get("reduction") for row in self.state["drafts"]))

    def test_generator_is_now_contradiction_first_and_theory_first(self) -> None:
        revision=self.state["generator_revision"]
        self.assertIn("documented contradiction",revision["new_rule"])
        self.assertIn("mature-theory non-reducibility",revision["required_fields"])
        self.assertIn("same-information baseline",revision["required_fields"])
        self.assertIn("endpoint headroom",revision["required_fields"])

    def test_reduction_map_contains_load_bearing_recent_failures(self) -> None:
        keys={row["key"] for row in self.state["reduction_patterns"]}
        for key in ("verifier-exogeneity","evolution-induced-task-non-equivalence","persistent-update-vs-test-time-compute","typed-epistemic-authority"):
            self.assertIn(key,keys)


if __name__=="__main__": unittest.main()
