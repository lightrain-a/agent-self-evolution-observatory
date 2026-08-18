from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
SOURCE_CANDIDATE_ID = "AUTO-1"
CANDIDATE_ID = "AUTO-1-AGENT-SAFETY-20260818T060955Z"
EXPECTED_GENERATOR_SHA = "9ea2415ba3d651c5124f3276c49d284c1f32d44d0b21a982655144aab490a938"
PACE_REF = "arXiv:2608.14441"
SKILL_REF = "arXiv:2608.14036"
PACE_CLOSURE_ID = "PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _candidate_from_inbox(inbox: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in inbox.get("candidates") or [] if isinstance(row, dict) and row.get("candidate_id") == SOURCE_CANDIDATE_ID]
    if len(rows) != 1:
        raise ValueError(f"expected one {SOURCE_CANDIDATE_ID} candidate in semantic-review inbox")
    return rows[0]


def build_readjudication(
    *,
    review_state_path: Path,
    semantic_inbox_path: Path,
    reviewer_raw_path: Path,
    generator_raw_path: Path,
    pace_support_inventory_path: Path,
    pace_principle_closure_path: Path,
) -> dict[str, Any]:
    review_state = _load(review_state_path)
    inbox = _load(semantic_inbox_path)
    candidate = _candidate_from_inbox(inbox)
    semantic = candidate.get("semantic_reduction_review") or {}
    pace_support = _load(pace_support_inventory_path)
    pace_closure = _load(pace_principle_closure_path)

    generator_sha = _sha(generator_raw_path)
    reviewer_sha = _sha(reviewer_raw_path)
    if generator_sha != EXPECTED_GENERATOR_SHA or review_state.get("source_generator_raw_sha256") != EXPECTED_GENERATOR_SHA:
        raise ValueError("AUTO-1 generator content identity mismatch")
    if reviewer_sha != str(semantic.get("raw_sha256") or ""):
        raise ValueError("AUTO-1 reviewer raw identity mismatch")
    reviewer_artifact = (review_state.get("raw_artifacts") or {}).get("semantic_reviewer") or {}
    if reviewer_sha != str(reviewer_artifact.get("sha256") or ""):
        raise ValueError("AUTO-1 reviewer state/raw digest mismatch")

    refs = sorted({
        str(((candidate.get("empirical_evidence") or {}).get(key) or {}).get("ref") or "")
        for key in ("source_a", "source_b")
        if str(((candidate.get("empirical_evidence") or {}).get(key) or {}).get("ref") or "")
    })
    if refs != sorted([PACE_REF, SKILL_REF]):
        raise ValueError(f"AUTO-1 source refs drift:{refs}")

    lane_reason = " ".join(str(semantic.get("lane_contract_reason") or "").split())
    reviewer_reason = " ".join(str(semantic.get("reason") or "").split())
    reduction_class = str(semantic.get("reduction_class") or "").strip().upper()
    strongest = " ".join(str(semantic.get("strongest_reduction") or "").split())
    if semantic.get("reviewed") is not True or semantic.get("verdict") != "BLOCK":
        raise ValueError("AUTO-1 expected completed block-only reviewer decision")
    if semantic.get("independent_resolved_model") is not True:
        raise ValueError("AUTO-1 reviewer is not independently resolved")
    if semantic.get("source_claims_grounded") is not True:
        raise ValueError("AUTO-1 reviewer source grounding did not pass")
    if semantic.get("lane_contract_verified") is not False:
        raise ValueError("AUTO-1 expected lane-contract failure")
    if reduction_class != "NONE" or strongest.lower() != "none":
        raise ValueError("AUTO-1 formulation readjudication only applies when reviewer found no mature-theory reduction")

    support_summary = pace_support.get("summary") or {}
    support_diagnosis = pace_support.get("support_diagnosis") or {}
    if support_diagnosis.get("status") != "INSUFFICIENT_FOR_PACE_REOPEN_CONTRACT" or support_summary.get("eligible_physics_program_structural_contrast_groups") != 0:
        raise ValueError("PACE-only rescue support inventory no longer matches the frozen readjudication")

    closure_counter = ((pace_closure.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    if (
        pace_closure.get("candidate_id") != PACE_CLOSURE_ID
        or pace_closure.get("principle_dead_end_certified") is not True
        or pace_closure.get("stop_class") != "PRINCIPLE_STOP"
        or pace_closure.get("benchmark_level_dead_end_certified") is not False
        or closure_counter.get("same_information_reduction_verified") is not True
    ):
        raise ValueError("PACE scoped principle closure is missing or has drifted")

    policy = review_state.get("policy") or {}
    if policy.get("reviewer_only_resume") is not True or policy.get("generator_calls_authorized") != 0 or policy.get("prior_reviewer_verdict_reuse_forbidden") is not True:
        raise ValueError("AUTO-1 reviewer-only control contract drift")
    hold_signature = hashlib.sha256(json.dumps({
        "candidate_id": CANDIDATE_ID,
        "generator_raw_sha256": generator_sha,
        "reviewer_raw_sha256": reviewer_sha,
        "lane_contract_reason": lane_reason,
        "source_refs": refs,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    hold_reopen = "New primary evidence supplies the missing CONVERGENT_FAILURE lane-contract elements explicitly: one shared bounded operational condition, one common measured failure object, and correctly typed evidence roles; the repaired formulation must then survive same-information reduction. Alternatively, a PACE-only child must first satisfy the existing PACE principle reopen contract."
    hold_strongest = "no mature-theory reduction identified; the current failure is the cross-source lane-contract/formulation mismatch"

    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": CANDIDATE_ID,
        "source_candidate_id": SOURCE_CANDIDATE_ID,
        "title": candidate.get("title"),
        "source_refs": refs,
        "discovery_lane": candidate.get("discovery_lane"),
        "source_transaction": {
            "source_generator_run_id": review_state.get("source_generator_run_id"),
            "generator_requested_model": review_state.get("generator_requested_model"),
            "generator_resolved_model": review_state.get("generator_resolved_model"),
            "generator_raw_sha256": generator_sha,
            "reviewer_requested_model": reviewer_artifact.get("requested_model"),
            "reviewer_resolved_model": reviewer_artifact.get("resolved_model"),
            "reviewer_raw_sha256": reviewer_sha,
            "reviewer_only_resume": True,
            "generator_calls_authorized": 0,
            "prior_reviewer_verdict_reused": False,
        },
        "reviewer_adjudication": {
            "semantic_verdict": semantic.get("verdict"),
            "source_claims_grounded": semantic.get("source_claims_grounded"),
            "independent_resolved_model": semantic.get("independent_resolved_model"),
            "lane_contract_verified": semantic.get("lane_contract_verified"),
            "lane_contract_reason": lane_reason,
            "reduction_class": reduction_class,
            "strongest_reduction": strongest,
            "reviewer_reason": reviewer_reason,
            "matched_patterns": semantic.get("matched_patterns") or [],
        },
        "failure_diagnosis": {
            "current_disposition": "STOP_CURRENT_FORMULATION_LANE_CONTRACT",
            "stop_class": "PROTOCOL_STOP",
            "failure_layer": "assumption_scope",
            "failure_subtype": "FORMULATION_LANE_MISMATCH",
            "memory_class": "FORMULATION_HOLD",
            "principle_dead_end_certified": False,
            "principle_update_allowed": False,
            "core_principle_rejected": False,
            "reason": "The independent reviewer grounded both primary-source claims and found no mature-theory reduction, but rejected the CONVERGENT_FAILURE formulation because PACE mechanism/program redesign in dynamic physics and skill-retrieval reformulation failures are not one shared bounded operational condition or common measured failure object. This stops the current cross-source formulation only; it is not a scientific dead end.",
            "next_action": "Do not rerun the same cross-source reviewer. Reopen the cross-source formulation only with new primary evidence that supplies one explicitly shared bounded operational condition and common measured failure object. A PACE-only child is separately constrained by the existing scoped PACE principle closure and its same-information reopen contract.",
        },
        "pace_only_rescue_audit": {
            "support_inventory_artifact_sha256": _sha(pace_support_inventory_path),
            "support_status": support_diagnosis.get("status"),
            "attempt_states": support_summary.get("attempt_states"),
            "same_information_duplicate_groups": support_summary.get("same_information_duplicate_groups"),
            "eligible_structural_contrast_groups": support_summary.get("eligible_physics_program_structural_contrast_groups"),
            "same_initial_program_cross_target_groups": support_summary.get("same_initial_program_cross_target_groups"),
            "existing_scoped_principle_closure_id": PACE_CLOSURE_ID,
            "existing_scoped_principle_closure_sha256": _sha(pace_principle_closure_path),
            "existing_scoped_principle_dead_end_certified": True,
            "pace_benchmark_dead_end_certified": False,
            "reopen_condition": closure_counter.get("reopen_condition"),
            "interpretation": "Removing the skill paper does not automatically rescue AUTO-1. Current PACE trajectories contain no same-information matched structural contrast satisfying the existing reopen contract, and the surface-conditioned redesign-identifiability formulation is already scoped-closed by a same-information program-synthesis/search reduction.",
        },
        "memory_projection": {
            "basin_prefix": "semantic-lane-contract-",
            "memory_class": "FORMULATION_HOLD",
            "dead_end_certified": False,
            "strongest_reduction": hold_strongest,
            "reopen_only_if": hold_reopen,
            "avoid": [
                "repeating the same PACE plus skill-retrieval analogy as a CONVERGENT_FAILURE candidate",
                "treating an independent reviewer BLOCK as a principle dead end when reduction_class is NONE",
                "relabeling the PACE-only child without satisfying the existing same-information reopen condition",
            ],
        },
        "persistent_hold": {
            "source_candidate_id": CANDIDATE_ID,
            "original_candidate_id": SOURCE_CANDIDATE_ID,
            "basin": f"semantic-lane-contract-{hold_signature}",
            "search_primitive": candidate.get("discovery_lane"),
            "title": candidate.get("title"),
            "disposition": "STOP_CURRENT_FORMULATION_LANE_CONTRACT",
            "stop_class": "PROTOCOL_STOP",
            "failure_layer": "assumption_scope",
            "failure_subtype": "FORMULATION_LANE_MISMATCH",
            "memory_class": "FORMULATION_HOLD",
            "dead_end_certified": False,
            "strongest_reduction": hold_strongest,
            "reduction_class": reduction_class,
            "lane_contract_reason": lane_reason,
            "exact_reduction_test": "none",
            "current_source_refs": refs,
            "problem_text": candidate.get("title"),
            "reason": reviewer_reason,
            "avoid": [
                "repeating the same PACE plus skill-retrieval analogy as a CONVERGENT_FAILURE candidate",
                "treating an independent reviewer BLOCK as a principle dead end when reduction_class is NONE",
                "relabeling the PACE-only child without satisfying the existing same-information reopen condition",
            ],
            "reopen_only_if": hold_reopen,
            "source_generator_raw_sha256": generator_sha,
            "source_reviewer_raw_sha256": reviewer_sha,
            "principle_dead_end_certified": False,
            "scientific_authority": False,
        },
        "authority": {
            "paper": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
        "scientific_authority": False,
    }


def validate_readjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    failure = state.get("failure_diagnosis") or {}
    reviewer = state.get("reviewer_adjudication") or {}
    pace = state.get("pace_only_rescue_audit") or {}
    projection = state.get("memory_projection") or {}
    persistent = state.get("persistent_hold") or {}
    source = state.get("source_transaction") or {}
    if state.get("source_candidate_id") != SOURCE_CANDIDATE_ID or sorted(state.get("source_refs") or []) != sorted([PACE_REF, SKILL_REF]):
        errors.append("AUTO-1 identity/source refs drift")
    if source.get("generator_raw_sha256") != EXPECTED_GENERATOR_SHA or source.get("generator_calls_authorized") != 0 or source.get("reviewer_only_resume") is not True:
        errors.append("AUTO-1 reviewer-only source transaction drift")
    if source.get("reviewer_resolved_model") == source.get("generator_resolved_model") or source.get("prior_reviewer_verdict_reused") is not False:
        errors.append("AUTO-1 independent review provenance invalid")
    if reviewer.get("semantic_verdict") != "BLOCK" or reviewer.get("source_claims_grounded") is not True or reviewer.get("independent_resolved_model") is not True:
        errors.append("AUTO-1 independent semantic review is incomplete")
    if reviewer.get("lane_contract_verified") is not False or reviewer.get("reduction_class") != "NONE" or str(reviewer.get("strongest_reduction") or "").lower() != "none":
        errors.append("AUTO-1 must remain a lane/formulation failure without mature-theory reduction")
    if failure.get("stop_class") != "PROTOCOL_STOP" or failure.get("failure_layer") != "assumption_scope" or failure.get("failure_subtype") != "FORMULATION_LANE_MISMATCH":
        errors.append("AUTO-1 typed formulation disposition drift")
    if failure.get("memory_class") != "FORMULATION_HOLD" or failure.get("principle_dead_end_certified") is not False or failure.get("principle_update_allowed") is not False or failure.get("core_principle_rejected") is not False:
        errors.append("AUTO-1 formulation failure cannot enter persistent dead-end memory")
    if pace.get("support_status") != "INSUFFICIENT_FOR_PACE_REOPEN_CONTRACT" or pace.get("attempt_states") != 162 or pace.get("eligible_structural_contrast_groups") != 0 or pace.get("same_initial_program_cross_target_groups") != 6:
        errors.append("AUTO-1 PACE-only rescue support audit drift")
    if pace.get("existing_scoped_principle_dead_end_certified") is not True or pace.get("pace_benchmark_dead_end_certified") is not False or not str(pace.get("reopen_condition") or "").strip():
        errors.append("AUTO-1 PACE-only rescue must preserve scoped closure and benchmark openness")
    if projection.get("memory_class") != "FORMULATION_HOLD" or projection.get("dead_end_certified") is not False or not str(projection.get("reopen_only_if") or "").strip():
        errors.append("AUTO-1 memory projection must be a reopenable formulation hold")
    if not str(persistent.get("basin") or "").startswith("semantic-lane-contract-") or persistent.get("memory_class") != "FORMULATION_HOLD" or persistent.get("dead_end_certified") is not False or persistent.get("stop_class") != "PROTOCOL_STOP" or persistent.get("failure_layer") != "assumption_scope" or persistent.get("scientific_authority") is not False:
        errors.append("AUTO-1 persistent formulation hold is invalid")
    if state.get("scientific_authority") is not False or any((state.get("authority") or {}).values()):
        errors.append("AUTO-1 formulation readjudication must have zero downstream authority")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the reviewed AUTO-1 failure at the correct scientific layer without creating a dead end.")
    parser.add_argument("--review-state", type=Path, required=True)
    parser.add_argument("--semantic-inbox", type=Path, required=True)
    parser.add_argument("--reviewer-raw", type=Path, required=True)
    parser.add_argument("--generator-raw", type=Path, required=True)
    parser.add_argument("--pace-support-inventory", type=Path, required=True)
    parser.add_argument("--pace-principle-closure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = build_readjudication(
        review_state_path=args.review_state,
        semantic_inbox_path=args.semantic_inbox,
        reviewer_raw_path=args.reviewer_raw,
        generator_raw_path=args.generator_raw,
        pace_support_inventory_path=args.pace_support_inventory,
        pace_principle_closure_path=args.pace_principle_closure,
    )
    errors = validate_readjudication(state)
    if errors:
        raise SystemExit("invalid AUTO-1 formulation readjudication: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "disposition": state["failure_diagnosis"]["current_disposition"], "stop_class": state["failure_diagnosis"]["stop_class"], "failure_layer": state["failure_diagnosis"]["failure_layer"], "dead_end": state["failure_diagnosis"]["principle_dead_end_certified"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
