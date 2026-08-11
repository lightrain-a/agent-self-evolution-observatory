from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .p0_mem_xfer_support_enriched import (
    ARMS, SupportP0Error, _exclusive_run_lock,
    _assert_loaded_sources_match_audit as _assert_support_loaded_sources_match_audit,
    _critical_source_snapshot as _support_critical_source_snapshot,
)
from .p0_mem_xfer_support_full import (
    _assert_loaded_sources_match_audit,
    _critical_source_snapshot,
    analyze_full_support_rows,
)

FAMILIES = (
    "pick_and_place_simple", "pick_clean_then_place_in_recep",
    "pick_cool_then_place_in_recep", "pick_heat_then_place_in_recep",
)


def synthetic_full_rows() -> list[dict]:
    rows = []
    for candidate in range(12):
        effects = [0] * 6
        if candidate in {0, 1}:
            effects[0] = -1; effects[3] = -1
        elif candidate in {2, 3}:
            effects[1] = 1; effects[4] = 1
        elif candidate in {4, 5}:
            effects[2] = 1; effects[5] = 1
        for slot, effect in enumerate(effects):
            role = "probe_development" if slot < 3 else "future_eval"
            target_family = FAMILIES[slot % 4]
            unit_id = f"m{candidate}-u{slot}"
            for arm in ARMS:
                success = 0
                if effect > 0 and arm == "retrieved": success = 1
                if effect < 0 and arm == "placebo": success = 1
                rows.append({
                    "unit_id": unit_id, "arm": arm, "memory_id": f"m{candidate}",
                    "source_family": FAMILIES[candidate % 4], "target_family": target_family,
                    "target_task_id": f"task-{candidate}-{slot}", "candidate_index": candidate % 3 + 1,
                    "candidate_role": "heldout_candidate" if candidate % 3 == 2 else "development",
                    "evaluation_role": role, "success": success,
                })
    return rows


class FullSupportTest(unittest.TestCase):
    def test_full_support_gate_uses_cross_split_replication(self) -> None:
        analysis = analyze_full_support_rows(synthetic_full_rows())
        self.assertEqual(analysis["complete_units"], 72)
        self.assertEqual(analysis["complete_executions"], 216)
        self.assertEqual(analysis["controlled_nonzero"], 12)
        self.assertEqual(analysis["idea3_support_checks"]["replicated_controlled_harm_candidates"]["actual"], 2)
        self.assertEqual(analysis["idea3_support_checks"]["replicated_controlled_benefit_candidates"]["actual"], 4)
        self.assertEqual(analysis["idea5_support_checks"]["eligible_target_family_folds"]["actual"], 4)
        self.assertEqual(analysis["decision"], "FULL_SUPPORT_ANALYSIS_READY")
        self.assertFalse(analysis["method_failure_authorized"])
        self.assertFalse(analysis["admission_method_training_authorized"])
        self.assertFalse(analysis["second_model_authorized"])

    def test_missing_unit_blocks_full_analysis(self) -> None:
        rows = synthetic_full_rows()[:-3]
        with self.assertRaises(SupportP0Error):
            analyze_full_support_rows(rows)

    def test_duplicate_process_lock_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            lock = Path(td) / "run.lock"
            with _exclusive_run_lock(lock):
                with self.assertRaises(SupportP0Error):
                    with _exclusive_run_lock(lock):
                        pass

    def test_loaded_source_snapshot_must_match_pre_gpu_audit(self) -> None:
        snapshot = _critical_source_snapshot()
        self.assertEqual(set(snapshot), {
            "p0_mem_xfer_support_full", "p0_mem_xfer_support_enriched", "p0_alfworld_adapter",
        })
        self.assertTrue(all(len(row["sha256"]) == 64 for row in snapshot.values()))
        _assert_loaded_sources_match_audit({"source_snapshot": snapshot})
        bad = {name: dict(row) for name, row in snapshot.items()}
        bad["p0_mem_xfer_support_full"]["sha256"] = "0" * 64
        with self.assertRaises(SupportP0Error):
            _assert_loaded_sources_match_audit({"source_snapshot": bad})

    def test_support_stage_loaded_source_snapshot_must_match_audit(self) -> None:
        snapshot = _support_critical_source_snapshot()
        self.assertEqual(set(snapshot), {"p0_mem_xfer_support_enriched", "p0_alfworld_adapter"})
        self.assertTrue(all(len(row["sha256"]) == 64 for row in snapshot.values()))
        _assert_support_loaded_sources_match_audit({"source_snapshot": snapshot})
        bad = {name: dict(row) for name, row in snapshot.items()}
        bad["p0_alfworld_adapter"]["sha256"] = "0" * 64
        with self.assertRaises(SupportP0Error):
            _assert_support_loaded_sources_match_audit({"source_snapshot": bad})


if __name__ == "__main__":
    unittest.main()
