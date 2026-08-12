from __future__ import annotations

import copy
import unittest

from .paper_first_c2_authorization import (
    EXPECTED_PROVENANCE_SHA256,
    EXPECTED_STRUCTURAL_SHA256,
    build_c2_authorization,
    evaluate_c2_authorization,
)
from .paper_first_c2_contract import build_c2_contract
from .paper_first_collision_review import build_fresh_collision_review
from .paper_first_stop_triage import build_paper_first_stop_triage
from .paper_first_c2_authorization import _load, REPLAY, SUPPORT, STRUCTURAL, PROVENANCE


class PaperFirstC2AuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_c2_authorization()

    def test_real_authorization_requires_all_machine_gates(self) -> None:
        self.assertEqual(self.state["decision"], "C2_LOCAL_VALIDATION_AUTHORIZED")
        self.assertTrue(self.state["local_validation_authorized"])
        self.assertEqual(self.state["checks_passed"], self.state["checks_total"])
        self.assertTrue(self.state["C3_locked"])
        self.assertFalse(self.state["full_experiment_authorized"])
        self.assertFalse(self.state["old_b9_formal_method_reopened"])

    def test_structural_artifact_failure_locks_c2(self) -> None:
        structural = copy.deepcopy(_load(STRUCTURAL))
        structural["valid_units"] = 9
        result = evaluate_c2_authorization(
            collision=build_fresh_collision_review(),
            triage=build_paper_first_stop_triage(),
            replay=_load(REPLAY),
            support=_load(SUPPORT),
            structural=structural,
            provenance=_load(PROVENANCE),
            contract=build_c2_contract(),
            structural_sha256=EXPECTED_STRUCTURAL_SHA256,
            provenance_sha256=EXPECTED_PROVENANCE_SHA256,
        )
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")
        self.assertFalse(result["local_validation_authorized"])

    def test_parent_provenance_must_remain_inconclusive(self) -> None:
        provenance = copy.deepcopy(_load(PROVENANCE))
        provenance["decision"] = "PROVENANCE_PASS"
        result = evaluate_c2_authorization(
            collision=build_fresh_collision_review(),
            triage=build_paper_first_stop_triage(),
            replay=_load(REPLAY),
            support=_load(SUPPORT),
            structural=_load(STRUCTURAL),
            provenance=provenance,
            contract=build_c2_contract(),
            structural_sha256=EXPECTED_STRUCTURAL_SHA256,
            provenance_sha256=EXPECTED_PROVENANCE_SHA256,
        )
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")
        self.assertFalse(result["old_b9_formal_method_reopened"])

    def test_threshold_relaxation_is_not_authorized(self) -> None:
        contract = build_c2_contract()
        contract["frozen_gate"]["go"]["minimum_nonzero_tau_units"] = 8
        result = evaluate_c2_authorization(
            collision=build_fresh_collision_review(),
            triage=build_paper_first_stop_triage(),
            replay=_load(REPLAY),
            support=_load(SUPPORT),
            structural=_load(STRUCTURAL),
            provenance=_load(PROVENANCE),
            contract=contract,
            structural_sha256=EXPECTED_STRUCTURAL_SHA256,
            provenance_sha256=EXPECTED_PROVENANCE_SHA256,
        )
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")


if __name__ == "__main__":
    unittest.main()
