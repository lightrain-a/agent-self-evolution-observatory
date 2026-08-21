from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from research_pipeline.paper_first_agent_safety_r9_controlled_longitudinal import (
    CANONICAL_LAYERS,
    canonical,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def load(name: str) -> dict:
    return json.loads((GENERATED / name).read_text(encoding="utf-8"))


def verify_embedded_hash(value: dict, key: str) -> bool:
    copy = dict(value)
    expected = copy.pop(key)
    return hashlib.sha256(canonical(copy)).hexdigest() == expected


class ControlledLongitudinalProtocolTest(unittest.TestCase):
    def test_preregistration_is_hash_bound_and_non_authorizing(self) -> None:
        prereg = load("agent-safety-r9-controlled-longitudinal-preregistration-20260821.json")
        self.assertTrue(verify_embedded_hash(prereg, "preregistration_sha256"))
        self.assertEqual(prereg["budget"]["new_behavior_episodes"], 72)
        self.assertFalse(prereg["execution_authorized"])
        self.assertEqual(tuple(prereg["failure_semantics"]["layers"]), CANONICAL_LAYERS)
        self.assertFalse(prereg["pre_registered_analysis"]["population_hazard_estimate"])
        self.assertFalse(prereg["pre_registered_analysis"]["automatic_claim_upgrade"])

    def test_protocol_review_and_gate_bind_preregistration(self) -> None:
        prereg = load("agent-safety-r9-controlled-longitudinal-preregistration-20260821.json")
        review = load("agent-safety-r9-controlled-longitudinal-protocol-review-20260821.json")
        gate = load("agent-safety-r9-controlled-longitudinal-execution-gate-20260821.json")
        self.assertTrue(verify_embedded_hash(review, "review_sha256"))
        self.assertTrue(verify_embedded_hash(gate, "gate_sha256"))
        self.assertEqual(review["preregistration_sha256"], prereg["preregistration_sha256"])
        self.assertEqual(gate["preregistration_sha256"], prereg["preregistration_sha256"])
        self.assertEqual(gate["review_sha256"], review["review_sha256"])
        self.assertTrue(gate["execution_authorized"])
        self.assertTrue(gate["gpu_authorized"])

    def test_no_update_plan_changes_only_workflow_snapshot(self) -> None:
        prereg = load("agent-safety-r9-controlled-longitudinal-preregistration-20260821.json")
        control = load("agent-safety-r9-no-update-control-plan-20260821.json")
        self.assertTrue(verify_embedded_hash(control, "plan_sha256"))
        self.assertEqual(len(control["episodes"]), 36)
        source = {
            (row["state_id"], int(row["branch_seed"]), int(row["future_step"])): row
            for row in prereg["exact_heldout_schedule_manifest"]
        }
        for row in control["episodes"]:
            original = source[(row["state_id"], int(row["branch_seed"]), int(row["future_step"]))]
            self.assertEqual(int(row["behavior_id"]), int(original["behavior_id"]))
            self.assertEqual(int(row["seed"]), int(original["seed"]))
            self.assertFalse(row["update_enabled"])
            self.assertIsNone(row["appended_unit_sha256"])
            self.assertNotEqual(row["workflow_sha256"], original["treatment_workflow_sha256"])

    def test_fixed_probe_panel_is_read_only_and_complete(self) -> None:
        plan = load("agent-safety-r9-fixed-probe-snapshot-plan-20260821.json")
        self.assertTrue(verify_embedded_hash(plan, "plan_sha256"))
        self.assertEqual(len(plan["episodes"]), 36)
        keys = {
            (row["state_id"], int(row["future_step"]), int(row["behavior_id"]))
            for row in plan["episodes"]
        }
        self.assertEqual(len(keys), 36)
        self.assertEqual({key[1] for key in keys}, {1, 2, 3})
        self.assertEqual({key[2] for key in keys}, {14, 16, 18})
        self.assertTrue(all(row["probe_writeback_enabled"] is False for row in plan["episodes"]))

    def test_scientific_review_recomputes_controlled_results(self) -> None:
        review = load("agent-safety-r9-controlled-longitudinal-scientific-review-20260821.json")
        self.assertTrue(verify_embedded_hash(review, "review_sha256"))
        recomputed = review["row_level_recomputation"]
        self.assertEqual(recomputed["treatment_branch_events"], 8)
        self.assertEqual(recomputed["control_branch_events"], 4)
        self.assertEqual(
            recomputed["paired_discordance"],
            {"treatment_only": 4, "control_only": 0, "both_event": 4, "neither_event": 4},
        )
        self.assertEqual(recomputed["fixed_probe_event_trajectories"], 4)
        self.assertFalse(review["population_hazard_estimate"])

    def test_memory_graph_records_finite_reopen_resolution(self) -> None:
        table = load("agent-safety-r9-controlled-paper-claim-table-20260821.json")
        graph = load("agent-safety-r9-controlled-memory-graph21-inputs-20260821.json")
        self.assertTrue(verify_embedded_hash(table, "table_sha256"))
        self.assertTrue(verify_embedded_hash(graph, "bundle_sha256"))
        self.assertEqual(graph["schema_version"], "2.1")
        self.assertEqual(
            graph["reopen_condition"]["status"],
            "SATISFIED_FOR_FROZEN_R9_FINITE_DESIGN",
        )
        self.assertFalse(graph["reopen_condition"]["satisfied_for_population_claim"])
        self.assertFalse(graph["reopen_condition"]["new_behavior_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
