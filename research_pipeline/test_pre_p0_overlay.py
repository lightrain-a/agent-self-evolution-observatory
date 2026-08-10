from __future__ import annotations

import copy
import unittest

from .pre_p0_identifiability import CURRENT_CONTRACTS, apply_evidence_overlay, audit_contract


class PreP0EvidenceOverlayTest(unittest.TestCase):
    def test_development_positive_evidence_cannot_unblock_historical_failure(self) -> None:
        contract = copy.deepcopy(CURRENT_CONTRACTS["update-trust-region"])
        overlay = {
            "idea_id": "update-trust-region",
            "authorization_effect": "may-block-only",
            "independent_validation": False,
            "same_evaluation_batch_as_repair_selection": True,
            "check_updates": {"representability": {"pass": True, "evidence": "development AUC improved"}},
        }
        merged = apply_evidence_overlay(contract, overlay)
        self.assertFalse(merged["checks"]["representability"])
        node = audit_contract("update-trust-region", merged)
        self.assertIn("representability", node["blockers"])
        self.assertEqual(node["evidence_overlays"][0]["applied"][0]["action"], "positive-development-evidence-recorded-without-unblocking")

    def test_development_negative_evidence_can_add_blocker(self) -> None:
        contract = copy.deepcopy(CURRENT_CONTRACTS["update-trust-region"])
        self.assertTrue(contract["checks"]["effect_variation"])
        merged = apply_evidence_overlay(contract, {
            "idea_id": "update-trust-region",
            "authorization_effect": "may-block-only",
            "independent_validation": False,
            "check_updates": {"effect_variation": {"pass": False, "evidence": "no harmful updates"}},
        })
        self.assertFalse(merged["checks"]["effect_variation"])

    def test_only_independent_fresh_validation_can_unblock(self) -> None:
        contract = copy.deepcopy(CURRENT_CONTRACTS["update-trust-region"])
        merged = apply_evidence_overlay(contract, {
            "idea_id": "update-trust-region",
            "authorization_effect": "may-unblock",
            "independent_validation": True,
            "same_evaluation_batch_as_repair_selection": False,
            "excluded_qualification_task_keys": ["valid_seen/task-a/trial/game.tw-pddl"],
            "excluded_qualification_task_count": 1,
            "check_updates": {"representability": {"pass": True, "evidence": "fresh candidate batch LOO AUC > 0.65"}},
        })
        self.assertTrue(merged["checks"]["representability"])
        self.assertEqual(merged["evidence_overlays"][0]["applied"][0]["action"], "unblocked-by-independent-validation")
        self.assertEqual(merged["evidence_overlays"][0]["qualification_exclusion_evidence_id"], "update-trust-region")
        self.assertEqual(merged["evidence_overlays"][0]["excluded_qualification_task_count"], 1)
        self.assertEqual(merged["evidence_overlays"][0]["excluded_qualification_task_keys"], ["valid_seen/task-a/trial/game.tw-pddl"])


if __name__ == "__main__":
    unittest.main()
