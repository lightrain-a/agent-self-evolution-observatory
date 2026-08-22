from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .governance_protocol import build_governance_state
from .research_governance_layer import (
    build_aris_governance_layer,
    candidate_lineage_records,
    candidate_stage_receipts,
    experiment_authorization_records,
    failure_authority_record,
    repair_budget_summary,
    repair_history_records,
    scientific_transitions,
)
from .round3_provenance_manifest import AUTHORITY as ROUND3_AUTHORITY
from .round3_provenance_manifest import POLICY as ROUND3_POLICY
from .round3_provenance_manifest import SCHEMA_VERSION as ROUND3_SCHEMA_VERSION
from .round3_provenance_manifest import _sha as round3_sha
from .scientific_research_graph import build_scientific_research_graph


class ArisGovernanceLayerTest(unittest.TestCase):
    def test_scientific_transitions_are_ordered_and_fail_closed(self) -> None:
        rows = scientific_transitions()
        self.assertEqual(
            [row["to_stage"] for row in rows],
            [
                "problem",
                "substrate",
                "f0-identifiability",
                "p0-support",
                "p0-method",
                "p1-replication",
                "paper-experiment",
            ],
        )
        self.assertEqual(rows[3]["evidence_required"], ["f0_evidence"])
        self.assertIn("method_freeze", rows[-1]["evidence_required"])
        self.assertTrue(all(row["automatic_transition"] is False for row in rows))

    def test_failure_belief_authority_never_becomes_automatic_claim_mutation(self) -> None:
        runtime = failure_authority_record(
            {"idea_id": "x", "signature": "runtime:provider-timeout", "affected_layer": "runtime"}
        )
        method = failure_authority_record(
            {"idea_id": "x", "signature": "method:baseline-tie", "affected_layer": "method"}
        )
        principle = failure_authority_record(
            {
                "idea_id": "x",
                "signature": "principle:exact-reduction",
                "affected_layer": "principle",
                "principle_dead_end_certified": True,
            }
        )
        self.assertEqual(runtime["failure_code"], "RUNTIME_ERROR")
        self.assertFalse(runtime["belief_authority"])
        self.assertIn("invalidate_claim", runtime["forbidden_effects"])
        self.assertEqual(method["failure_code"], "METHOD_FAIL")
        self.assertTrue(method["belief_authority"])
        self.assertTrue(method["claim_mutation_requires_independent_adjudication"])
        self.assertEqual(principle["failure_code"], "PRINCIPLE_DEAD_END")
        self.assertTrue(principle["persistent_dead_end_authority"])
        self.assertIn("automatic_scientific_closure", principle["forbidden_effects"])

    def test_experiment_authorization_is_fail_closed(self) -> None:
        registry = {
            "phases": [
                {
                    "idea_id": "blocked",
                    "phase": "P0",
                    "execution_authorized": False,
                    "blocked_by": "f0-identifiability",
                },
                {
                    "idea_id": "paper-missing-freeze",
                    "phase": "P2",
                    "execution_authorized": True,
                },
                {
                    "idea_id": "paper-frozen",
                    "phase": "P2",
                    "execution_authorized": True,
                    "method_freeze_sha256": "a" * 64,
                    "experiment_blueprint_sha256": "b" * 64,
                },
            ]
        }
        rows = experiment_authorization_records(registry)
        self.assertFalse(rows[0]["effective_execution_authorized"])
        self.assertFalse(rows[1]["effective_execution_authorized"])
        self.assertIn("method_freeze-missing", rows[1]["blockers"])
        self.assertTrue(rows[2]["effective_execution_authorized"])
        self.assertFalse(rows[2]["automatic_authorization"])

    def test_recorded_repair_budget_and_proposals_remain_distinct(self) -> None:
        iteration = {
            "nodes": [
                {
                    "idea_id": "idea",
                    "artifact_dir": "substrate",
                    "code": "A",
                    "repair_children": [
                        {
                            "child": "child-1",
                            "operator": "representation-child",
                            "changed_variable": "representation only",
                            "precondition": "frozen check",
                        }
                    ],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            root.mkdir(parents=True, exist_ok=True)
            (root / "idea.json").write_text(
                json.dumps(
                    {
                        "idea_id": "idea",
                        "repairs": [
                            {
                                "repair_id": "r1",
                                "substrate_id": "substrate",
                                "child_id": "child-1",
                                "repair_kind": "representation",
                            },
                            {
                                "repair_id": "r2",
                                "substrate_id": "substrate",
                                "child_id": "child-1",
                                "repair_kind": "objective",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = repair_history_records(iteration, root)
        summary = repair_budget_summary(rows)
        self.assertEqual(summary["recorded_repairs"], 2)
        self.assertEqual(summary["proposal_only_repairs"], 1)
        self.assertEqual(summary["budget_consuming_repairs"], 2)
        self.assertTrue(summary["review_required"])
        self.assertEqual(
            summary["one_load_bearing_repair_per_child_violations"][0]["child_id"],
            "child-1",
        )

    def test_candidate_lineage_missing_review_is_provenance_hold(self) -> None:
        generator = {
            "run_id": "run",
            "discovery_transaction_id": "c" * 64,
            "raw_artifacts": {"generator": {"sha256": "a" * 64}},
            "pre_f0_candidates": [
                {"candidate_id": "C1", "source_branch_id": "root", "route_reason": "READY"}
            ],
        }
        pre_f0 = {
            "rows": [
                {
                    "candidate_id": "C1",
                    "candidate_snapshot_sha256": "b" * 64,
                    "source_branch_id": "root",
                }
            ]
        }
        records = candidate_lineage_records(
            generator_state=generator,
            pre_f0_state=pre_f0,
            problem_gate_state={},
            candidate_portfolio={"rows": [{"candidate_id": "C1", "portfolio_state": "SEARCH_HOLD"}]},
        )
        self.assertEqual(records[0]["provenance_status"], "PROVENANCE_INCONCLUSIVE")
        self.assertTrue(records[0]["downstream_authorization_blocked"])
        generator["pre_f0_candidates"][0]["semantic_reduction_review"] = {"sha256": "d" * 64}
        records = candidate_lineage_records(
            generator_state=generator,
            pre_f0_state=pre_f0,
            problem_gate_state={},
            candidate_portfolio={"rows": [{"candidate_id": "C1"}]},
        )
        self.assertTrue(records[0]["lineage_complete"])

    def test_recovered_pre_f0_lineage_uses_formulation_and_machine_route_receipts(self) -> None:
        candidate = {
            "candidate_id": "PORT-002",
            "candidate_snapshot_sha256": "b" * 64,
            "source_branch_id": "branch-r1",
            "route_reason": "EXACT_REDUCTION_PENDING",
            "reduction_blockers": ["unresolved-exact-reduction-test:1"],
        }
        generator = {
            "run_id": "recovery-run",
            "raw_artifacts": {"generator": {"sha256": "a" * 64}},
            "pre_f0_candidates": [candidate],
            "portfolio_ingestion_recovery": {
                "source_transaction_id": "c" * 64,
                "recovery_sha256": "d" * 64,
                "recovered_candidates": 2,
                "formulation_receipts": [
                    {
                        "role": "formulate-1",
                        "complete_candidates": 1,
                        "source_raw_sha256": "e" * 64,
                        "request_fingerprint": "1" * 64,
                    },
                    {
                        "role": "formulate-2",
                        "complete_candidates": 1,
                        "source_raw_sha256": "f" * 64,
                        "request_fingerprint": "2" * 64,
                    },
                ],
            },
        }
        records = candidate_lineage_records(
            generator_state=generator,
            pre_f0_state={"rows": [candidate]},
            problem_gate_state={},
            candidate_portfolio={"rows": [candidate]},
        )
        row = records[0]
        self.assertTrue(row["lineage_complete"])
        self.assertEqual(row["provenance_status"], "COMPLETE")
        self.assertEqual(row["discovery_transaction_id"], "c" * 64)
        self.assertEqual(row["formulation_origin_role"], "formulate-2")
        self.assertEqual(row["formulation_raw_sha256"], "f" * 64)
        self.assertFalse(row["review_receipt_complete"])
        self.assertTrue(row["disposition_receipt_complete"])
        self.assertEqual(row["disposition_receipt_kind"], "PRE_F0_MACHINE_ROUTE_ZERO_AUTHORITY")
        self.assertFalse(row["pre_f0_route_has_scientific_authority"])
        self.assertFalse(row["downstream_authorization_blocked"])

    def test_recovered_pre_f0_lineage_fails_closed_on_malformed_origin_receipt(self) -> None:
        candidate = {
            "candidate_id": "PORT-001",
            "candidate_snapshot_sha256": "b" * 64,
            "source_branch_id": "branch-r1",
            "route_reason": "EXACT_REDUCTION_PENDING",
        }
        generator = {
            "run_id": "recovery-run",
            "raw_artifacts": {"generator": {"sha256": "a" * 64}},
            "pre_f0_candidates": [candidate],
            "portfolio_ingestion_recovery": {
                "source_transaction_id": "c" * 64,
                "recovery_sha256": "d" * 64,
                "recovered_candidates": 1,
                "formulation_receipts": [{
                    "role": "formulate-1",
                    "complete_candidates": 1,
                    "source_raw_sha256": "not-a-sha",
                }],
            },
        }
        row = candidate_lineage_records(
            generator_state=generator,
            pre_f0_state={"rows": [candidate]},
            problem_gate_state={},
            candidate_portfolio={"rows": [candidate]},
        )[0]
        self.assertFalse(row["lineage_complete"])
        self.assertEqual(row["provenance_status"], "PROVENANCE_INCONCLUSIVE")
        self.assertTrue(row["downstream_authorization_blocked"])

    def test_generation_target_and_problem_hold_are_not_fabricated_eliminations(self) -> None:
        receipts = candidate_stage_receipts(
            generator_state={
                "run_id": "run",
                "search_portfolio": {
                    "config": {"requested_raw_seeds": 120},
                    "summary": {"raw_seeds": 2, "semantic_unique": 2, "pre_f0_eligible": 2},
                },
            },
            candidate_portfolio={"summary": {"visible_candidates": 2}},
            problem_gate_state={"summary": {"passed_problem_gate": 0}},
        )
        by_stage = {row["stage"]: row for row in receipts}
        self.assertEqual(by_stage["generation-target"]["unrealized_target"], 118)
        self.assertEqual(by_stage["generation-target"]["eliminated_count"], 0)
        self.assertEqual(by_stage["problem-gate"]["held_count"], 2)
        self.assertEqual(by_stage["problem-gate"]["eliminated_count"], 0)

    def test_stage_receipts_ignore_historical_portfolio_rows_for_zero_candidate_transaction(self) -> None:
        receipts = candidate_stage_receipts(
            generator_state={
                "run_id": "current-zero",
                "pre_f0_candidates": [],
                "search_portfolio": {
                    "config": {"requested_raw_seeds": 0},
                    "summary": {"raw_seeds": 0, "semantic_unique": 0, "pre_f0_eligible": 0},
                },
            },
            candidate_portfolio={
                "summary": {"visible_candidates": 3},
                "rows": [
                    {"candidate_id": "OLD-1", "stage": "PRE_F0_EVIDENCE_ACQUISITION"},
                    {"candidate_id": "OLD-2", "stage": "PRE_F0_EVIDENCE_ACQUISITION"},
                    {"candidate_id": "OLD-3", "stage": "PRE_F0_EVIDENCE_ACQUISITION"},
                ],
            },
            problem_gate_state={"summary": {"passed_problem_gate": 0}},
        )
        by_stage = {row["stage"]: row for row in receipts}
        self.assertEqual(by_stage["portfolio-visibility"]["input_count"], 0)
        self.assertEqual(by_stage["portfolio-visibility"]["output_count"], 0)
        self.assertEqual(by_stage["problem-gate"]["input_count"], 0)

    def test_stage_receipts_expose_unreceipted_elimination_lineage(self) -> None:
        receipts = candidate_stage_receipts(
            generator_state={
                "run_id": "run",
                "search_portfolio": {
                    "config": {"requested_raw_seeds": 4},
                    "summary": {"raw_seeds": 4, "semantic_unique": 2, "pre_f0_eligible": 1},
                },
            },
            candidate_portfolio={"summary": {"visible_candidates": 1}},
            problem_gate_state={"summary": {"passed_problem_gate": 0}},
        )
        by_stage = {row["stage"]: row for row in receipts}
        self.assertEqual(by_stage["semantic-uniqueness"]["eliminated_count"], 2)
        self.assertFalse(by_stage["semantic-uniqueness"]["record_level_elimination_reasons_complete"])
        self.assertEqual(by_stage["pre-f0-route"]["eliminated_count"], 0)
        self.assertEqual(by_stage["pre-f0-route"]["unresolved_lineage_count"], 1)
        self.assertTrue(by_stage["pre-f0-route"]["record_level_elimination_reasons_complete"])

    def test_complete_round3_manifest_replaces_aggregate_lineage_gap_with_typed_dispositions(self) -> None:
        manifest = {
            "schema_version": ROUND3_SCHEMA_VERSION,
            "generated_at": "2026-08-21T00:00:00+00:00",
            "status": "ROUND3_PROVENANCE_COMPLETE",
            "policy": dict(ROUND3_POLICY),
            "transaction": {"status": "COMMITTED"},
            "coverage": {"record_level_lineage_complete": True},
            "summary": {
                "requested_generation_slots": 120,
                "valid_raw_seeds": 90,
                "raw_seed_dispositions": 90,
                "semantic_unique_kept": 36,
                "dedup_dropped": 54,
                "branch_nodes": 92,
                "formulation_inputs": 24,
                "recovered_candidates": 6,
                "model_rejected_zero_authority": 12,
                "inputs_without_complete_output_object": 6,
                "pre_f0_routes": 3,
                "machine_blocked_routes": 3,
            },
            "generation_slots": [],
            "raw_seed_dispositions": [],
            "branch_nodes": [],
            "formulation_inputs": [],
            "candidate_routes": [],
            "scientific_authority": False,
            "authority": dict(ROUND3_AUTHORITY),
        }
        manifest["manifest_content_sha256"] = round3_sha(
            {
                key: value
                for key, value in manifest.items()
                if key not in {"generated_at", "manifest_content_sha256"}
            }
        )
        receipts = candidate_stage_receipts(
            generator_state={"run_id": "run", "pre_f0_candidates": [{}, {}, {}]},
            candidate_portfolio={"summary": {"visible_candidates": 3}},
            problem_gate_state={"summary": {"passed_problem_gate": 0}},
            provenance_manifest=manifest,
        )
        by_stage = {row["stage"]: row for row in receipts}
        self.assertEqual(by_stage["generation-target"]["unrealized_target"], 30)
        self.assertEqual(by_stage["semantic-uniqueness"]["eliminated_count"], 54)
        self.assertTrue(by_stage["semantic-uniqueness"]["record_level_elimination_reasons_complete"])
        self.assertEqual(by_stage["branch-dag"]["input_count"], 92)
        self.assertEqual(by_stage["formulation"]["search_disposition_count"], 18)
        self.assertEqual(by_stage["machine-route"]["held_count"], 3)
        self.assertTrue(all(row["unresolved_lineage_count"] == 0 for row in receipts))
        self.assertTrue(all(row["scientific_authority"] is False for row in receipts))
        self.assertTrue(
            all(
                row["input_count"]
                == sum(
                    row[key]
                    for key in (
                        "output_count",
                        "held_count",
                        "eliminated_count",
                        "search_disposition_count",
                        "unrealized_target",
                        "unresolved_lineage_count",
                    )
                )
                for row in receipts
            )
        )

    def test_memory_graph_binds_governance_without_new_truth_nodes(self) -> None:
        pilot_registry = {
            "phases": [
                {
                    "idea_id": "idea",
                    "phase": "P0",
                    "title": "P0",
                    "status": "planned",
                    "execution_authorized": False,
                    "blocked_by": "f0",
                }
            ]
        }
        failure_library = {
            "assets": [
                {
                    "idea_id": "idea",
                    "phase": "P0",
                    "signature": "runtime:timeout",
                    "affected_layer": "runtime",
                }
            ],
            "dead_end_registry": {},
        }
        candidate = {
            "candidate_id": "C1",
            "title": "candidate",
            "stage": "PRE_F0",
            "portfolio_state": "SEARCH_HOLD",
            "source_branch_id": "root",
            "candidate_snapshot_sha256": "b" * 64,
            "semantic_reduction_review": {"sha256": "d" * 64},
        }
        generator = {
            "run_id": "run",
            "discovery_transaction_id": "c" * 64,
            "raw_artifacts": {"generator": {"sha256": "a" * 64}},
            "pre_f0_candidates": [candidate],
            "search_portfolio": {
                "config": {"requested_raw_seeds": 1},
                "summary": {"raw_seeds": 1, "semantic_unique": 1, "pre_f0_eligible": 1},
            },
        }
        layer = build_aris_governance_layer(
            governance_state=build_governance_state(),
            pilot_registry=pilot_registry,
            failure_asset_library=failure_library,
            experiment_iteration={"nodes": []},
            generator_state=generator,
            pre_f0_state={"rows": [candidate]},
            problem_gate_state={"summary": {"passed_problem_gate": 0}},
            candidate_portfolio={"rows": [candidate], "summary": {"visible_candidates": 1}},
            repair_budget_root=None,
        )
        self.assertEqual(layer["status"], "GOVERNANCE_COMPILED")
        graph = build_scientific_research_graph(
            evidence_graph={"nodes": [], "edges": []},
            candidate_portfolio={"rows": [candidate]},
            scientific_meta_trace={},
            failure_asset_library=failure_library,
            pilot_registry=pilot_registry,
            governance_layer=layer,
        )
        self.assertEqual(graph["schema_version"], "2.1")
        self.assertEqual(graph["lint"]["summary"]["errors"], 0)
        self.assertEqual(graph["governance_bindings"]["failure_records_bound"], 1)
        self.assertEqual(graph["governance_bindings"]["experiment_authorizations_bound"], 1)
        self.assertEqual(graph["governance_bindings"]["candidate_lineage_bound"], 1)
        failure = next(row for row in graph["overlay_nodes"] if row["kind"] == "failure_asset")
        self.assertEqual(failure["failure_code"], "RUNTIME_ERROR")
        self.assertFalse(failure["belief_authority"])


if __name__ == "__main__":
    unittest.main()
