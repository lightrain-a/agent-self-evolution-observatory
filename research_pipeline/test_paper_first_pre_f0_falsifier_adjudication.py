from __future__ import annotations

import copy
import unittest

from .candidate_identity import attach_candidate_identity
from .paper_first_pre_f0_falsifier_adjudication import STOP_STATUS, build_adjudication, validate_adjudication
from .research_candidate_portfolio import build_research_candidate_portfolio


TXN = "d" * 64


def _states() -> tuple[dict, dict]:
    candidate = attach_candidate_identity({
        "candidate_id": "PORT-006",
        "title": "Reset-specific test object",
        "discovery_lane": "CONVERGENT_FAILURE",
        "source_branch_id": "branch-a",
        "primary_refs": ["arXiv:1", "arXiv:2"],
        "exact_prediction": "reset-only is worse than step-only",
        "strongest_same_information_baseline": "generic stale-state timing",
        "cheapest_problem_falsifier": "matched reset versus step intervention",
        "endpoint_headroom_requirement": "positive reset-specific residual",
        "scientific_authority": False,
        "authority": {"paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    })
    queue = {"status": "PRE_F0_QUEUE_READY", "source_generator_run_id": "run-r11", "rows": [candidate], "scientific_authority": False}
    preflight = {
        "status": "PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE",
        "rows": [{"candidate_id": "PORT-006", "candidate_identity_version": candidate["candidate_identity_version"],
                  "candidate_snapshot_sha256": candidate["candidate_snapshot_sha256"], "disposition": "SUPPORT_QUALIFIED",
                  "support_scope": "bounded matched unit", "scientific_authority": False}],
        "scientific_authority": False,
    }
    return queue, preflight


def _evidence() -> list[dict]:
    return [{"role": "decisive", "artifact_uri": "run-data://r11/result.json", "sha256": "a" * 64,
             "status": "REDUCTION_SUPPORTED", "protocol_valid": True, "provider_calls_executed": 0,
             "gpu_calls_executed": 0, "metrics": {"qualified": 40}, "interpretation": "matched baseline explains result",
             "scientific_authority": False}]


class PreF0FalsifierAdjudicationTest(unittest.TestCase):
    def test_reduction_supported_stops_only_current_formulation(self) -> None:
        queue, preflight = _states()
        state = build_adjudication(
            queue=queue, preflight=preflight, discovery_transaction_id=TXN,
            candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED",
            evidence_receipts=_evidence(), current_formulation="reset-specific bridge",
            strongest_reduction="generic stale-state timing", scope_limit="does not prove reset can never matter",
            reopen_only_if="fresh matched learner-training residual survives", generated_at="2026-08-24T12:00:00+00:00",
        )
        self.assertEqual(validate_adjudication(state, queue=queue, preflight=preflight), [])
        row = state["entries"][0]
        self.assertEqual(row["status"], STOP_STATUS)
        self.assertEqual(row["portfolio_state"], "SEARCH_STOP_CURRENT_FORMULATION")
        self.assertFalse(row["current_formulation_open"])
        self.assertFalse(row["persistent_dead_end_memory_authorized"])
        self.assertFalse(row["principle_dead_end_certified"])
        self.assertEqual(state["summary"]["persistent_dead_end_created"], 0)
        self.assertEqual(state["summary"]["problem_gate_authorized"], 0)

    def test_snapshot_mismatch_and_private_uri_fail_closed(self) -> None:
        queue, preflight = _states()
        broken = copy.deepcopy(preflight)
        broken["rows"][0]["candidate_snapshot_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            build_adjudication(queue=queue, preflight=broken, discovery_transaction_id=TXN,
                               candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED",
                               evidence_receipts=_evidence(), current_formulation="x", strongest_reduction="y",
                               scope_limit="z", reopen_only_if="fresh residual")
        state = build_adjudication(queue=queue, preflight=preflight, discovery_transaction_id=TXN,
                                   candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED",
                                   evidence_receipts=_evidence(), current_formulation="x", strongest_reduction="y",
                                   scope_limit="z", reopen_only_if="fresh residual")
        state["entries"][0]["evidence_receipts"][0]["artifact_uri"] = "/data/private/result.json"
        self.assertIn("private evidence URI:PORT-006", validate_adjudication(state, queue=queue, preflight=preflight))

    def test_transaction_and_snapshot_bound_lineage_fail_closed(self) -> None:
        queue, preflight = _states()
        state = build_adjudication(
            queue=queue, preflight=preflight, discovery_transaction_id=TXN,
            candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED", evidence_receipts=_evidence(),
            current_formulation="x", strongest_reduction="y", scope_limit="z", reopen_only_if="fresh residual",
        )
        transaction_queue = {"discovery_transaction_role": "queue", "discovery_transaction_id": TXN}
        self.assertEqual(validate_adjudication(state, queue=queue, preflight=preflight, transaction_queue=transaction_queue), [])
        broken = copy.deepcopy(state)
        broken["entries"][0]["execution_lineage"]["candidate_snapshot_sha256"] = "f" * 64
        self.assertIn("execution lineage snapshot mismatch:PORT-006", validate_adjudication(broken, queue=queue, preflight=preflight, transaction_queue=transaction_queue))
        broken = copy.deepcopy(state)
        broken["discovery_transaction_id"] = "e" * 64
        self.assertIn("sealed discovery transaction mismatch", validate_adjudication(broken, queue=queue, preflight=preflight, transaction_queue=transaction_queue))

    def test_human_reformulation_cannot_terminally_reduce_without_r2_execution_authority(self) -> None:
        queue, preflight = _states()
        snapshot = queue["rows"][0]["candidate_snapshot_sha256"]
        lineage = {
            "r2_branch_relation": "HUMAN_REFORMULATION_AFTER_PARENT_INCONCLUSIVE; disjoint units",
            "r2_identity_binding": "TRANSITIVE_VIA_R1_ADJUDICATED_PLAN_SHA256",
            "r2_candidate_id_is_run_local_alias": True,
            "r1_execution_ready_candidate_snapshot_sha256": snapshot,
            "r1_adjudicated_candidate_snapshot_sha256": snapshot,
            "r1_execution_ready_plan_sha256": "1" * 64,
            "r1_adjudicated_plan_sha256": "2" * 64,
            "r1_contract_sha256": "3" * 64,
            "r2_contract_sha256": "4" * 64,
            "r1_execution_was_authorized": True,
            "r2_execution_authority_artifact_present": False,
            "r2_evidence_admitted_for_terminal_adjudication": False,
        }
        with self.assertRaisesRegex(ValueError, "terminal reduction lacks R2 execution-authority provenance"):
            build_adjudication(
                queue=queue, preflight=preflight, discovery_transaction_id=TXN,
                candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED", evidence_receipts=_evidence(),
                current_formulation="x", strongest_reduction="y", scope_limit="z", reopen_only_if="fresh residual",
                execution_lineage=lineage,
            )

    def test_portfolio_overlay_hides_stopped_formulation_from_search_holds_without_promotion(self) -> None:
        queue, preflight = _states()
        adjudication = build_adjudication(queue=queue, preflight=preflight, discovery_transaction_id=TXN,
                                           candidate_id="PORT-006", outcome="REDUCTION_SUPPORTED",
                                           evidence_receipts=_evidence(), current_formulation="x", strongest_reduction="y",
                                           scope_limit="z", reopen_only_if="fresh residual")
        portfolio = build_research_candidate_portfolio(
            generator_state={"status": "GENERATED_PRE_F0_EVIDENCE_ACQUISITION", "candidates": []},
            pre_f0_state=queue, problem_gate_state={"audited": [], "passed": [], "blocked": []},
            paper_design_backlog_state={"entries": []}, pre_f0_adjudication_state=adjudication,
        )
        self.assertEqual(portfolio["summary"]["visible_candidates"], 1)
        self.assertEqual(portfolio["summary"]["search_holds"], 0)
        self.assertEqual(portfolio["summary"]["search_stopped_current_formulation"], 1)
        self.assertEqual(portfolio["summary"]["active_problem_lines"], 0)
        row = portfolio["rows"][0]
        self.assertEqual(row["stage"], "PRE_F0_ADJUDICATION")
        self.assertEqual(row["portfolio_state"], "SEARCH_STOP_CURRENT_FORMULATION")
        self.assertFalse(row["paper_design_eligible"])
        self.assertFalse(row["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
