from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .failure_asset_library import build_failure_asset_library
from .paper_first_p0_f0 import build_paper_first_p0_f0_state, resolve_paper_first_p0_f0_state


class PaperFirstP0F0StateTest(unittest.TestCase):
    def test_premature_f0_is_preserved_but_quarantined_from_scientific_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "runs" / "paper-first-p0-20260812"
            future = run / "future-learnability"
            shared = run / "shared-surface"
            future.mkdir(parents=True); shared.mkdir(parents=True)
            (future / "result.json").write_text(json.dumps({"status":"complete","analysis":{"support_pass":True,"matched_candidates":3,"nonzero_matched_candidates":1,"future_learnability_range":0.25,"baseline":{}}}))
            (shared / "result.json").write_text(json.dumps({"status":"complete","analysis":{
                "pf2":{"support_pass":False,"heldout_oracle_repair_rate":.889,"best_fixed_surface_rate":.778,"ownership_accuracy":.778,"distinct_best_surfaces":3},
                "pf4":{"support_pass":True,"baseline_diagnostic_accuracy":.667,"post_update_wrong_surface_accuracy":{"workflow":.5},"diagnostic_drop":{"workflow":.167}},
                "pf6":{"support_pass":False,"failure_modes":["success","loop-timeout","missing-required-transform"],"non_diagonal_transitions":5,"repair_summaries":{},"decision_relevant_pair":None},
            }}))
            state = build_paper_first_p0_f0_state(root)
        self.assertEqual(state["summary"]["ideas"], 4)
        self.assertEqual((state["summary"]["observed_support_pass"], state["summary"]["observed_support_hold"]), (2, 2))
        self.assertEqual((state["summary"]["support_pass"], state["summary"]["support_hold"]), (0, 0))
        self.assertEqual((state["summary"]["quarantined"], state["summary"]["scientifically_authorized"], state["summary"]["method_fail_authorized"]), (4, 0, 0))
        by = {row["idea_id"]: row for row in state["cards"]}
        self.assertEqual(by["future-learnability-preserving-self-evolution"]["observed_f0_decision"], "F0_SUPPORT_PASS")
        self.assertEqual(by["diagnosability-preserving-self-evolution"]["observed_f0_decision"], "F0_SUPPORT_PASS")
        corrected = by["diagnosability-preserving-self-evolution"].get("corrected_bounded_falsifier") or {}
        self.assertEqual(corrected.get("status"), "INCONCLUSIVE_FUNCTIONAL_EQUIVALENCE_QUALIFICATION_FAILED")
        self.assertFalse(corrected.get("qualification_passed"))
        self.assertFalse(corrected.get("fault_phase_executed"))
        self.assertFalse(corrected.get("broader_principle_falsified"))
        self.assertEqual(corrected.get("scientific_update"), "NO_BELIEF_UPDATE_FUNCTIONAL_EQUIVALENCE_NOT_ESTABLISHED")
        self.assertEqual(state["summary"].get("corrected_bounded_falsifier_inconclusive"), 1)
        self.assertEqual(by["cross-surface-repair-routing"]["observed_f0_decision"], "HOLD_F0_SUPPORT_INSUFFICIENT")
        self.assertEqual(by["failure-mode-transport-under-self-evolution"]["observed_f0_decision"], "HOLD_F0_SUPPORT_INSUFFICIENT")
        self.assertTrue(all(row["decision"] == "PREMATURE_UNAUTHORIZED_LOCAL_VALIDATION_DIAGNOSTIC" for row in state["cards"]))
        self.assertTrue(all(row["scientific_gate_authority"] is False for row in state["cards"]))
        self.assertTrue(all(row["method_failure_authorized"] is False for row in state["cards"]))
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, None, state)
        asset = next(row for row in library["assets"] if row["diagnosis"] == "authority-provenance-mismatch")
        self.assertEqual(asset["affected_layer"], "authority-protocol")
        self.assertFalse(asset["can_authorize_p0"])
        self.assertFalse(asset["can_authorize_method_or_principle"])

    def test_resolver_preserves_completed_frozen_diagnostic_when_local_history_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); complete=root/"complete"; run=complete/"runs"/"paper-first-p0-20260812"; future=run/"future-learnability"; shared=run/"shared-surface"; future.mkdir(parents=True); shared.mkdir(parents=True)
            (future/"result.json").write_text(json.dumps({"status":"complete","analysis":{"support_pass":True,"matched_candidates":3,"nonzero_matched_candidates":1,"future_learnability_range":0.25}}))
            (shared/"result.json").write_text(json.dumps({"status":"complete","analysis":{"pf2":{"support_pass":False},"pf4":{"support_pass":True},"pf6":{"support_pass":False}}}))
            frozen_state=build_paper_first_p0_f0_state(complete); frozen=root/"frozen.json"; frozen.write_text(json.dumps(frozen_state))
            resolved=resolve_paper_first_p0_f0_state(root/"missing-host",frozen)
        self.assertEqual((resolved["summary"]["observed_support_pass"],resolved["summary"]["observed_support_hold"]),(2,2))
        self.assertEqual((resolved["summary"]["quarantined"],resolved["summary"]["scientifically_authorized"]),(4,0))

    def test_resolver_does_not_promote_incomplete_frozen_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); frozen=root/"frozen.json"; frozen.write_text(json.dumps({"summary":{"ideas":4,"quarantined":4,"observed_support_pass":0,"observed_support_hold":0},"authority":{"promotion_authorized":False,"local_validation_authorized":False,"full_experiment_authorized":False},"cards":[]}))
            resolved=resolve_paper_first_p0_f0_state(root/"missing-host",frozen)
        self.assertEqual((resolved["summary"]["observed_support_pass"],resolved["summary"]["observed_support_hold"]),(0,0))
        self.assertEqual(resolved["summary"]["quarantined"],4)


if __name__ == "__main__":
    unittest.main()
