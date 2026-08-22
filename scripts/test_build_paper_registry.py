#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import build_paper_registry as registry


class PaperRegistryProjectionTest(unittest.TestCase):
    def test_c01_targeted_repair_boundary_is_public_and_decision_complete(self) -> None:
        boundary = registry.targeted_repair_boundary(registry.C01_ID)
        self.assertEqual(boundary["scheduler_state"], "HOLD_SUPPORT_AND_IDENTIFICATION")
        primary = boundary["primary_result"]
        self.assertAlmostEqual(primary["success_minus_failure"], 0.166667, places=6)
        self.assertAlmostEqual(primary["permutation_p_success_greater"], 0.07853921460785392, places=12)
        self.assertFalse(primary["support_gate_pass"])
        self.assertFalse(primary["counterevidence_gate_pass"])
        self.assertEqual(primary["verdict"], "INCONCLUSIVE_NO_THRESHOLD_CHANGE")
        power = boundary["power"]
        self.assertEqual(power["independent_pairs_for_80pct_power_range"], [18, 22])
        self.assertEqual(power["four_pair_power_range"], [0.280479, 0.351994])
        ident = boundary["identification"]
        self.assertEqual(ident["primary_pairs"], 4)
        self.assertEqual(ident["original_verifier_strict_pass"], 4)
        self.assertEqual(ident["deepseek_strict_pass"], 0)
        self.assertEqual(ident["kimi_strict_pass"], 1)
        self.assertEqual(ident["three_reviewer_unanimous_strict_pass"], 0)
        confirm = boundary["independent_confirmation"]
        self.assertEqual(confirm["fresh_same_release_qualified_tasks"], 0)
        self.assertFalse(confirm["same_release_confirmation_available"])
        self.assertEqual(len(boundary["reopen_conditions"]), 2)
        self.assertGreaterEqual(len(boundary["forbidden_repairs"]), 4)

    @unittest.skipUnless(registry.DEFAULT_LEDGER_ROOT is not None and registry.DEFAULT_LEDGER_ROOT.exists(), "canonical Paper Acceptance ledger unavailable")
    def test_public_projection_has_no_backend_path_or_provider_identifier(self) -> None:
        state = registry.build(registry.DEFAULT_LEDGER_ROOT, registry.DEFAULT_ARTIFACT_ROOT, registry.DEFAULT_FREEZE_ROOT)
        self.assertEqual(state["schema_version"], "1.1")
        self.assertEqual(state["source"], "canonical_paper_acceptance_ledger")
        self.assertNotIn("canonical_ledger_root", state)
        raw = json.dumps(state, ensure_ascii=False)
        for forbidden in ("/data/wyt", "/home/wyt", "ARK_API_KEY", "Bearer ", "resp_"):
            self.assertNotIn(forbidden, raw)
        papers = state["papers"]
        summary = state["summary"]
        self.assertGreaterEqual(len(papers), 5)
        self.assertEqual(summary["papers"], len(papers))
        self.assertEqual(summary["submission_ready"], sum(p["current_state"] == "SUBMISSION_READY" for p in papers))
        self.assertEqual(summary["targeted_repair"], sum(p["current_state"] == "TARGETED_REPAIR" for p in papers))
        self.assertEqual(summary["preparation_pass"], sum(p["paper_preparation"]["status"] == "PASS" for p in papers))
        self.assertEqual(summary["preparation_blocked"], sum(p["paper_preparation"]["status"] == "BLOCKED" for p in papers))
        self.assertEqual(summary["machine_frozen_candidates"], sum(p["submission_freeze"]["status"] == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" for p in papers))
        c01 = next(row for row in papers if row["paper_id"] == registry.C01_ID)
        if c01["current_state"] == "TARGETED_REPAIR":
            self.assertEqual(c01["targeted_repair_boundary"]["scheduler_state"], "HOLD_SUPPORT_AND_IDENTIFICATION")
        else:
            self.assertEqual(c01["targeted_repair_boundary"], {})

    def test_checked_in_snapshot_obeys_public_boundary(self) -> None:
        state = json.loads(registry.DEFAULT_JSON.read_text(encoding="utf-8"))
        raw = json.dumps(state, ensure_ascii=False)
        self.assertNotIn("canonical_ledger_root", state)
        self.assertNotIn("/data/wyt", raw)
        self.assertNotIn("/home/wyt", raw)
        papers = state["papers"]
        summary = state["summary"]
        self.assertEqual(summary["papers"], len(papers))
        self.assertEqual(summary["human_submission_signoff_pending"], summary["machine_frozen_candidates"])
        temporal = next(row for row in papers if row["paper_id"] == "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK")
        self.assertEqual(temporal["paper_preparation"]["status"], "BLOCKED")
        self.assertEqual(temporal["submission_freeze"]["status"], "PREPARATION_BLOCKED")
        c01 = next(row for row in papers if row["paper_id"] == registry.C01_ID)
        if c01["current_state"] != "TARGETED_REPAIR":
            self.assertEqual(c01["targeted_repair_boundary"], {})
        direct = registry.targeted_repair_boundary(registry.C01_ID)
        self.assertEqual(direct["power"]["independent_pairs_for_80pct_power_range"], [18, 22])
        self.assertEqual(direct["identification"]["three_reviewer_unanimous_strict_pass"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
