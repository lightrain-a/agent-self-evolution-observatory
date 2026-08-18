from __future__ import annotations

import json
import unittest
from pathlib import Path

from .paper_first_auto1_formulation_readjudication import validate_readjudication
from .paper_first_lopd_fixed_budget_asset_hold import validate_hold
from .paper_first_pace_reopen_support_inventory import validate_inventory

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"


def load(name: str) -> dict:
    return json.loads((GEN / name).read_text(encoding="utf-8"))


class ContinuationFailureArtifactsTest(unittest.TestCase):
    def test_pace_reopen_inventory_is_support_stop_not_principle_stop(self) -> None:
        state=load("auto1-pace-reopen-support-inventory-20260818.json")
        self.assertEqual(validate_inventory(state),[])
        summary=state["summary"];diagnosis=state["support_diagnosis"]
        self.assertEqual((summary["attempt_states"],summary["same_information_duplicate_groups"],summary["eligible_physics_program_structural_contrast_groups"]),(162,12,0))
        self.assertEqual((diagnosis["stop_class"],diagnosis["failure_layer"]),("SUPPORT_STOP","experiment_identifiability"))
        self.assertFalse(diagnosis["principle_dead_end_certified"])

    def test_auto1_is_formulation_hold_not_dead_end(self) -> None:
        state=load("auto1-formulation-continuation-hold-20260818.json")
        self.assertEqual(validate_readjudication(state),[])
        failure=state["failure_diagnosis"];review=state["reviewer_adjudication"]
        self.assertEqual((failure["stop_class"],failure["failure_layer"],failure["failure_subtype"]),("PROTOCOL_STOP","assumption_scope","FORMULATION_LANE_MISMATCH"))
        self.assertEqual((review["reduction_class"],review["lane_contract_verified"]),("NONE",False))
        self.assertFalse(failure["principle_dead_end_certified"])
        self.assertFalse(failure["core_principle_rejected"])

    def test_lopd_fixed_budget_child_is_source_asset_hold_not_dead_end(self) -> None:
        state=load("lopd-fixed-budget-continuation-hold-20260818.json")
        self.assertEqual(validate_hold(state),[])
        support=state["support_diagnosis"]
        self.assertEqual((support["status"],support["stop_class"],support["failure_layer"]),("WAIT_PRIMARY_ASSET_RELEASE","SUPPORT_STOP","experiment_identifiability"))
        self.assertFalse(support["source_faithful_execution_available"])
        self.assertFalse(support["principle_dead_end_certified"])
        self.assertTrue(all(row["total_latent_positions_JxK"]==64 for row in state["frozen_problem"]["arms"]))


if __name__ == "__main__":
    unittest.main()
