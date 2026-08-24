from __future__ import annotations

import unittest

from .config import PROJECT_ROOT
from .feynman_socratic_gate import (
    audit_feynman_socratic_certificate,
    build_feynman_socratic_certificate,
    run_historical_replay,
)


class FeynmanSocraticGateTest(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "candidate_id": "C1",
            "irreducible_object": "Same frozen information yields a path-specific pre-outcome residual.",
            "same_information_nonreducibility": "The strongest path-integrated baseline receives the same ordered history but predicts no residual.",
            "exact_prediction": "The pre-outcome uptake observable differs under fixed support and content.",
            "reviewer_attack": "A generic continual-learning state may absorb the effect.",
            "endpoint_headroom_requirement": "The observable must be defined before outcome evaluation.",
            "strongest_same_information_baseline": "path-integrated continual-learning baseline",
            "cheapest_problem_falsifier": "Match ordered history and test whether the pre-outcome residual remains.",
        }

    def test_complete_certificate_is_zero_authority_clear(self) -> None:
        cert = build_feynman_socratic_certificate(self.candidate())
        audit = audit_feynman_socratic_certificate(cert)
        self.assertEqual(audit["status"], "CLEAR_FOR_PROBLEM_GATE_REVIEW")
        for key in ("scientific_authority", "problem_gate_authority", "method_authority", "experiment_authority", "p0_authority", "gpu_authority"):
            self.assertFalse(audit[key])

    def test_missing_plain_scientific_contract_requires_revision(self) -> None:
        candidate = self.candidate()
        candidate.pop("exact_prediction")
        cert = build_feynman_socratic_certificate(candidate)
        audit = audit_feynman_socratic_certificate(cert)
        self.assertEqual(audit["status"], "REVISE_CERTIFICATE")
        self.assertIn("decisive_observable", audit["missing_fields"])

    def test_problem_insight_certificate_is_shadow_and_does_not_change_live_clearance(self) -> None:
        candidate = self.candidate()
        candidate.update({
            "primary_contribution_type": "insight",
            "problem_importance": "The failure affects persistent agents across repeated reuse.",
            "under_explained_observation": "More retained experience can systematically worsen a bounded class of future decisions.",
            "missing_insight": "Applicability changes across context even when stored experience remains locally correct.",
            "minimal_decisive_test": "Hold stored content fixed and vary only applicability context.",
            "minimal_sufficient_intervention": "Apply an applicability check before reuse.",
            "insight_predictions": "The harm should concentrate where applicability flips and disappear when the check blocks reuse.",
        })
        audit = audit_feynman_socratic_certificate(build_feynman_socratic_certificate(candidate))
        self.assertEqual(audit["status"], "CLEAR_FOR_PROBLEM_GATE_REVIEW")
        self.assertEqual(audit["problem_insight_shadow"]["status"], "PROBLEM_INSIGHT_SHADOW_COMPLETE")
        self.assertTrue(audit["problem_insight_shadow"]["insight_dominant_candidate"])
        self.assertFalse(audit["problem_insight_shadow"]["live_problem_gate_authority"])

    def test_incomplete_problem_insight_shadow_does_not_retroactively_block_legacy_candidate(self) -> None:
        audit = audit_feynman_socratic_certificate(build_feynman_socratic_certificate(self.candidate()))
        self.assertEqual(audit["status"], "CLEAR_FOR_PROBLEM_GATE_REVIEW")
        self.assertEqual(audit["problem_insight_shadow"]["status"], "PROBLEM_INSIGHT_SHADOW_INCOMPLETE")

    def test_typed_existing_reduction_emits_warning_not_authority(self) -> None:
        candidate = self.candidate()
        candidate["semantic_reduction_review"] = {
            "verdict": "BLOCK",
            "reduction_class": "VALID_HARD_VETO",
            "strongest_reduction": "generic identifiability with the same information",
        }
        audit = audit_feynman_socratic_certificate(build_feynman_socratic_certificate(candidate))
        self.assertEqual(audit["status"], "MATURE_REDUCTION_ALERT")
        self.assertFalse(audit["machine_actionable"])
        self.assertFalse(audit["problem_gate_authority"])

    def test_later_method_failure_does_not_become_pre_problem_reduction(self) -> None:
        candidate = self.candidate()
        candidate.update({
            "search_closure_certified": True,
            "dead_end_certified": True,
            "closure_layer": "method_realization",
            "strongest_reduction": "simple matched method dominates after execution",
        })
        audit = audit_feynman_socratic_certificate(build_feynman_socratic_certificate(candidate))
        self.assertNotEqual(audit["status"], "MATURE_REDUCTION_ALERT")

    def test_twenty_case_canonical_retrospective_replay(self) -> None:
        replay = run_historical_replay(PROJECT_ROOT, 20)
        self.assertEqual(replay["status"], "PASS")
        self.assertEqual(replay["sample_size"], 20)
        self.assertEqual(replay["expected_mature_reductions"], 6)
        self.assertEqual(replay["detected_mature_reductions"], 6)
        self.assertEqual(replay["false_mature_reduction_alerts"], 0)
        self.assertTrue(replay["retrospective_only"])
        self.assertFalse(replay["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
