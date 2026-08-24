from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_pre_f0_falsifier_adjudication import DEFAULT_JSON, build_adjudication

QUEUE = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
PREFLIGHT = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"
TRANSACTION_QUEUE = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
BASE_URI = "run-data://external-fresh-primary-refresh-20260824-r11/operator-recompile-v18/"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt(role: str, rel: str, path: Path, status: str, metrics: dict[str, Any], interpretation: str) -> dict[str, Any]:
    return {"role": role, "artifact_uri": BASE_URI + rel, "sha256": _sha(path), "status": status,
            "protocol_valid": True, "provider_calls_executed": 0, "gpu_calls_executed": 0,
            "metrics": metrics, "interpretation": interpretation, "scientific_authority": False}


def build_port006(*, evidence_root: Path, generated_at: str | None = None) -> dict[str, Any]:
    root = Path(evidence_root)
    rels = {
        "exact": "experiments/port-006-spade-full-audit-exact-strata-r1/result.json",
        "adjusted": "experiments/port-006-spade-audit-adjusted-residual-r1/result.json",
        "r1_execution_plan": "evidence-plan-port006-prospective-execution-ready-r1.json",
        "r1_plan": "evidence-plan-port006-prospective-adjudicated-r1.json",
        "r1_receipt": "evidence-receipt-port006-prospective-r1.json",
        "r2_contract": "experiments/port-006-spade-prospective-reference-state-swap-r2/experiment-contract.json",
        "r2_result": "experiments/port-006-spade-prospective-reference-state-swap-r2/result.json",
        "r2_audit": "experiments/port-006-spade-prospective-reference-state-swap-r2/manipulation-audit.json",
    }
    paths = {key: root / rel for key, rel in rels.items()}
    data = {key: _load(path) for key, path in paths.items()}
    queue, preflight, transaction_queue = _load(QUEUE), _load(PREFLIGHT), _load(TRANSACTION_QUEUE)

    canonical_rows = [r for r in queue.get("rows") or [] if isinstance(r, dict) and r.get("candidate_id") == "PORT-006"]
    if len(canonical_rows) != 1:
        raise ValueError("current canonical Pre-F0 queue must contain exactly one PORT-006 alias")
    canonical_snapshot = str(canonical_rows[0].get("candidate_snapshot_sha256") or "").strip().lower()
    transaction_id = str(transaction_queue.get("discovery_transaction_id") or "").strip().lower()
    if transaction_queue.get("discovery_transaction_role") != "queue" or len(transaction_id) != 64:
        raise ValueError("sealed discovery transaction queue required")

    r1_execution_rows = [r for r in data["r1_execution_plan"].get("entries") or [] if isinstance(r, dict) and r.get("candidate_id") == "PORT-006"]
    r1_rows = [r for r in data["r1_plan"].get("entries") or [] if isinstance(r, dict) and r.get("candidate_id") == "PORT-006"]
    if len(r1_execution_rows) != 1 or len(r1_rows) != 1:
        raise ValueError("R1 execution/adjudication lineage must each contain exactly one PORT-006 alias")
    r1_execution_row, r1_row = r1_execution_rows[0], r1_rows[0]
    if str(r1_execution_row.get("candidate_snapshot_sha256") or "").lower() != canonical_snapshot or str(r1_row.get("candidate_snapshot_sha256") or "").lower() != canonical_snapshot:
        raise ValueError("R1 execution/adjudication plans do not bind the current canonical candidate snapshot")
    if r1_execution_row.get("execution_authorized") is not True or r1_execution_row.get("status") != "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION":
        raise ValueError("R1 bounded evidence execution was not explicitly authorized")
    if not r1_execution_row.get("contract_sha256") or r1_execution_row.get("contract_sha256") != r1_row.get("contract_sha256"):
        raise ValueError("R1 execution/adjudication contract binding drift")
    if r1_row.get("status") != "HOLD_INCONCLUSIVE_TREE_BUDGET_EXHAUSTED" or r1_row.get("next_action") != "stop-or-human-reformulation":
        raise ValueError("R1 did not terminate at the frozen human-reformulation boundary")
    r1_receipts = [r for r in data["r1_receipt"].get("receipts") or [] if isinstance(r, dict) and r.get("candidate_id") == "PORT-006"]
    if len(r1_receipts) != 1 or r1_receipts[0].get("outcome") != "INCONCLUSIVE" or r1_receipts[0].get("protocol_valid") is not True:
        raise ValueError("R1 evidence receipt drift")

    r2c, r2 = data["r2_contract"], data["r2_result"]
    r2s = r2.get("summary") or {}
    if not str(r2c.get("branch_relation") or "").startswith("HUMAN_REFORMULATION_AFTER_PARENT_INCONCLUSIVE"):
        raise ValueError("R2 is not the human-reformulated child")
    if r2c.get("candidate_id") != "PORT-006":
        raise ValueError("R2 run-local candidate alias drift")
    if r2c.get("parent_adjudicated_plan_sha256") != _sha(paths["r1_plan"]):
        raise ValueError("R2 parent plan digest mismatch")
    if r2.get("status") != "COMPLETE_ZERO_PROVIDER_CPU" or r2.get("decision") != "REDUCTION_SUPPORTED":
        raise ValueError("R2 decisive result drift")
    minimum = int((r2c.get("decision") or {}).get("minimum_qualified_units") or 0)
    if int(r2s.get("competence_qualified") or 0) < minimum or float(r2s.get("reset_failure_rate") or 0) > float(r2s.get("step_failure_rate") or 0):
        raise ValueError("R2 no longer satisfies the frozen reduction rule")
    if any(int(r2.get(k) or 0) for k in ("provider_calls_executed", "gpu_calls_executed", "llm_judge_calls_executed")):
        raise ValueError("R2 execution accounting drift")

    audit, auds = data["r2_audit"], data["r2_audit"].get("summary") or {}
    if audit.get("result_sha256") != _sha(paths["r2_result"]):
        raise ValueError("R2 manipulation audit/result mismatch")
    qualified = int(r2s.get("competence_qualified") or 0)
    if int(auds.get("qualified_audit_ok") or 0) != qualified or int(auds.get("state_fp_different_qualified") or 0) != qualified:
        raise ValueError("R2 manipulation audit does not cover distinct latent state on every qualified unit")

    exact, adjusted = data["exact"], data["adjusted"]
    exact_test = exact.get("exact_conditional_test") or {}
    if exact.get("status") != "COMPLETE_EXACT_CONDITIONAL_ZERO_PROVIDER" or float(exact_test.get("two_sided_p") or 0) <= 0.05:
        raise ValueError("exact-strata context no longer supports reset-specific reduction")
    if adjusted.get("status") != "COMPLETE_ZERO_PROVIDER_OFFLINE":
        raise ValueError("adjusted observational context missing")

    receipts = [
        _receipt("same_information_observational_exact_strata", rels["exact"], paths["exact"], exact["status"],
                 {"units": int((exact.get("overlap") or {}).get("units_in_eligible_strata") or 0),
                  "exact_two_sided_p": float(exact_test.get("two_sided_p") or 0),
                  "cmh_two_sided_p": float((exact.get("supporting_full_signature_cmh") or {}).get("p_two_sided") or 0)},
                 "Exact first-party audit-signature conditioning does not retain a significant reset-specific residual; this is diagnostic, not learner-training causality."),
        _receipt("conflicting_observational_adjusted_signal", rels["adjusted"], paths["adjusted"], adjusted["status"],
                 {"reset_odds_ratio": float((adjusted.get("reset_residual") or {}).get("odds_ratio") or 0),
                  "nested_lr_p": float((adjusted.get("nested_likelihood_ratio") or {}).get("p_value") or 0),
                  "cmh_two_sided_p": float((adjusted.get("nonparametric_cmh") or {}).get("p_two_sided") or 0)},
                 "An adjusted observational residual exists, but its frozen decision boundary forbids learner-training or longitudinal causal interpretation, so it cannot override matched prospective evidence."),
        _receipt("bounded_training_intervention_parent", rels["r1_receipt"], paths["r1_receipt"], r1_receipts[0]["outcome"],
                 {"qualified_units": int(r1_receipts[0].get("qualified_units") or 0), "headroom_qualified_units": 0},
                 "The preregistered learner-training parent was protocol-valid but had zero primary headroom and was correctly adjudicated INCONCLUSIVE."),
        _receipt("decisive_human_reformulated_reset_timing_intervention", rels["r2_result"], paths["r2_result"], r2["decision"],
                 {"selected_units": int(r2s.get("selected_units") or 0), "trace_evaluable": int(r2s.get("trace_evaluable") or 0),
                  "competence_qualified": qualified, "reset_failures": int(r2s.get("reset_failures") or 0),
                  "step_failures": int(r2s.get("step_failures") or 0),
                  "paired_reset_minus_step_failure_rate": float(r2s.get("paired_reset_minus_step_failure_rate") or 0),
                  "exact_two_sided_p": float(r2s.get("exact_two_sided_p") or 0)},
                 "On an independent non-reused population, sufficient competence-qualified units show reset-boundary whole-state mismatch no more harmful than the same mismatch after the first step, satisfying the preregistered environment-level reduction rule."),
        _receipt("decisive_intervention_manipulation_audit", rels["r2_audit"], paths["r2_audit"], str(audit.get("audit") or ""),
                 {"qualified_audit_ok": int(auds.get("qualified_audit_ok") or 0),
                  "state_fp_different_qualified": int(auds.get("state_fp_different_qualified") or 0),
                  "obs_different_qualified": int(auds.get("obs_different_qualified") or 0)},
                 "The audit binds the exact R2 result and verifies a distinct swapped latent-state fingerprint on every competence-qualified unit."),
    ]

    return build_adjudication(
        queue=queue, preflight=preflight, discovery_transaction_id=transaction_id,
        candidate_id="PORT-006", outcome="INCONCLUSIVE",
        evidence_receipts=receipts,
        current_formulation="The current PORT-006 Pre-F0 formulation requires a reset/initialization-specific causal bridge: successful-looking reset-semantic changes should be more damaging than matched step-dynamics/state-timing changes and thereby motivate a recurring reset-corruption failure regime.",
        strongest_reduction="The frozen R2 contract/result pair would satisfy its environment-level REDUCTION_SUPPORTED rule, but the archived R2 directory contains no contemporaneous single-use bounded-evidence execution-authority artifact. Because support qualification and human reformulation do not themselves authorize execution, that result is preserved as informative evidence but is not admissible for a canonical terminal scientific reduction. The older exact audit-strata result remains diagnostic only.",
        scope_limit="This is a protocol/control-plane HOLD, not a scientific negative. R2 was frozen before intervention outcome readout and used zero provider/GPU/LLM-judge calls, but execution authority is unproven; R1 had explicit bounded-evidence execution authority but was scientifically inconclusive because it lacked headroom. The current reset-specific formulation therefore remains open and no persistent scientific dead end is created.",
        reopen_only_if="Resolve the protocol hold only by locating a contemporaneous pre-outcome single-use authority artifact that cryptographically binds the archived R2 contract, or by using a fresh disjoint preregistered learner-training/repeated-round matched reset-only versus step-only study under explicit bounded-evidence execution authority. Do not retroactively authorize the already-observed R2 run, and do not reuse its selected units as a fresh confirmatory panel.",
        execution_lineage={
                           "r1_execution_ready_plan_uri": BASE_URI + rels["r1_execution_plan"],
                           "r1_execution_ready_plan_sha256": _sha(paths["r1_execution_plan"]),
                           "r1_execution_ready_candidate_snapshot_sha256": canonical_snapshot,
                           "r1_execution_was_authorized": True,
                           "r1_contract_sha256": str(r1_execution_row.get("contract_sha256") or ""),
                           "r1_adjudicated_plan_uri": BASE_URI + rels["r1_plan"],
                           "r1_adjudicated_plan_sha256": _sha(paths["r1_plan"]),
                           "r1_adjudicated_candidate_snapshot_sha256": canonical_snapshot,
                           "r1_status": r1_row["status"], "r1_next_action": r1_row["next_action"],
                           "r2_identity_binding": "TRANSITIVE_VIA_R1_ADJUDICATED_PLAN_SHA256",
                           "r2_candidate_id_is_run_local_alias": True,
                           "r2_branch_relation": r2c.get("branch_relation"), "r2_contract_uri": BASE_URI + rels["r2_contract"],
                           "r2_contract_sha256": _sha(paths["r2_contract"]), "r2_reuses_parent_selected_units": False,
                           "r2_frozen_scientific_decision": str(r2.get("decision") or ""),
                           "r2_execution_authority_artifact_present": False,
                           "r2_evidence_admitted_for_terminal_adjudication": False,
                           "r2_protocol_hold": "MISSING_CONTEMPORANEOUS_SINGLE_USE_EXECUTION_AUTHORITY",
                           "provider_calls_executed_in_r2": 0, "gpu_calls_executed_in_r2": 0, "scientific_authority": False},
        conflict_resolution={"observational_adjusted_signal_present": True,
                             "why_not_decisive": "The adjusted association is observational/diagnostic and its own artifact forbids learner-training or longitudinal causal interpretation. R2 is scientifically stronger but cannot be terminally admitted until its execution-authority provenance is proven.",
                             "decision_rule": "Prefer preregistered same-information prospective intervention over observational association only when the prospective execution also satisfies the control-plane authority contract; otherwise HOLD without scientific closure.",
                             "scientific_authority": False},
        generated_at=generated_at,
    )


def write_port006(*, evidence_root: Path, output: Path = DEFAULT_JSON) -> dict[str, Any]:
    state = build_port006(evidence_root=evidence_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    state = write_port006(evidence_root=args.evidence_root, output=args.output)
    print(json.dumps({"output": str(args.output), "summary": state["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
