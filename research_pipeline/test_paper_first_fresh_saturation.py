from __future__ import annotations

import unittest

from .paper_first_fresh_saturation import build_fresh_saturation_state, reduction_pattern_audit


class PaperFirstFreshSaturationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=build_fresh_saturation_state()

    def test_current_scan_keeps_zero_survivors_instead_of_forcing_shortlist(self) -> None:
        s=self.state["summary"]
        self.assertEqual((s["drafts_reviewed"],s["survivors"],s["stopped"]),(41,0,41))
        self.assertEqual(self.state["decision"],"NO_FRESH_SURVIVOR_CURRENT_SCAN")
        self.assertTrue(self.state["policy"]["zero_survivors_is_valid_and_preferred_to_forced_shortlist"])
        self.assertFalse(self.state["policy"]["local_validation_authorized"])
        self.assertFalse(self.state["policy"]["p0_authorized"])
        self.assertFalse(self.state["policy"]["gpu_authorized"])

    def test_every_draft_is_reduced_or_collided_before_method_design(self) -> None:
        self.assertTrue(all(row["decision"].startswith("STOP_") for row in self.state["drafts"]))
        self.assertTrue(all(row.get("reduction") for row in self.state["drafts"]))

    def test_historical_scan_is_diagnostic_and_current_search_delays_reduction(self) -> None:
        revision=self.state["generator_revision"]
        self.assertIn("remains diagnostic",revision["historical_rule"])
        self.assertIn("four empirical discovery lanes",revision["new_rule"])
        self.assertIn("zero-authority shadow search lab",revision["new_rule"])
        self.assertIn("at most one live generator call",revision["new_rule"])
        self.assertIn("zero calls",self.state["next_action"])
        self.assertIn("Reduction Falsifiability Contract",revision["new_rule"])
        self.assertIn("discovery lane",revision["required_fields"])
        self.assertIn("mature-theory non-reducibility",revision["required_fields"])
        self.assertIn("same-information baseline",revision["required_fields"])
        self.assertIn("endpoint headroom",revision["required_fields"])
        audit=reduction_pattern_audit()
        self.assertEqual(len(audit),34)
        self.assertTrue(all(row["automatic_veto"] is False for row in audit))
        self.assertEqual({row["audit_class"] for row in audit},{"VALID_HARD_VETO","SOFT_COLLISION","NEEDS_EXACT_REDUCTION_TEST","TOO_GENERIC_TO_VETO"})

    def test_reduction_map_contains_load_bearing_recent_failures(self) -> None:
        keys={row["key"] for row in self.state["reduction_patterns"]}
        for key in ("verifier-exogeneity","evolution-induced-task-non-equivalence","persistent-update-vs-test-time-compute","typed-epistemic-authority","model-scaffold-enactability","artifact-uptake-after-retrieval","environment-mediated-history","multimodal-procedural-compression","externalization-internalization-portability","horizon-censored-attribution","future-evolvability-debt","persistent-world-gain-decomposition","self-play-evidence-endogeneity","population-lineage-generic-evolution","cross-layer-behavior-persistence","experience-sharing-sign-reversal","feedback-polarity-by-update-surface","harness-update-scope-heterogeneity","procedural-memory-nonmonotonicity"):
            self.assertIn(key,keys)


if __name__=="__main__": unittest.main()
