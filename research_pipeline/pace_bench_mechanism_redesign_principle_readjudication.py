from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PRIMARY_REF = "arXiv:2608.14441"
EVIDENCE_AUDIT = PROJECT_ROOT / "generated" / "pace-bench-principle-evidence-audit-20260818.json"
OLD_F0 = PROJECT_ROOT / "generated" / "pace-bench-search-control-transport-f0-20260818.json"
PF2 = PROJECT_ROOT / "generated" / "paper-first-pf2-method-adjudication.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "pace-bench-mechanism-redesign-principle-readjudication-20260818.json"
SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def build_readjudication(
    *,
    evidence_audit: dict[str, Any] | None = None,
    old_f0: dict[str, Any] | None = None,
    pf2: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence_audit = evidence_audit or _load(EVIDENCE_AUDIT)
    old_f0 = old_f0 or _load(OLD_F0)
    pf2 = pf2 or _load(PF2)

    treatment = evidence_audit.get("treatment_semantics_audit") or {}
    oracle = evidence_audit.get("reference_solution_ast_oracle") or {}
    trajectory = evidence_audit.get("real_trajectory_audit") or {}
    operationalization = evidence_audit.get("operationalization_diagnosis") or {}
    old_analysis = old_f0.get("analysis") or {}
    old_pair = old_analysis.get("best_supported_strategy_pair") or {}

    same_information = {
        "known_repair_surface": "The broad writable source/program surface is already known and held fixed; the reduction is not a repair-surface router.",
        "candidate_state": "The current candidate program/code and all previous candidate programs are available to both formulations.",
        "feedback": "The complete verifier/test/physics feedback transcript observed so far is identical.",
        "budget": "The same remaining verifier and generation-call budget is available.",
        "specification": "The same target environment, success criteria, constraints, and executable interfaces are available.",
        "generator_capability": "The same LLM/program proposal mechanism is available; the candidate claim receives no hidden oracle reference program or privileged target outcome.",
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "candidate_id": "PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY",
        "parent_source": PRIMARY_REF,
        "title": "Surface-conditioned mechanism/program redesign identifiability reduces to generic feedback-guided program synthesis under the same information",
        "search_primitive": "IDENTIFIABILITY_GAP",
        "principle_dead_end_certified": True,
        "stop_class": "PRINCIPLE_STOP",
        "benchmark_level_dead_end_certified": False,
        "dead_end_scope": "Surface-conditioned mechanism/program redesign identifiability as a standalone PACE paper problem: after the broad repair surface is already known, finite verifier feedback is claimed to identify which concrete redesign should be taken.",
        "experiment_run_for_this_readjudication": False,
        "old_rank_reversal_child": {
            "candidate_id": "PA-06-PACE-SEARCH-CONTROL-TRANSPORT",
            "status": "ARCHIVED_INVALID_OPERATIONALIZATION",
            "stop_class": "PROTOCOL_STOP",
            "secondary_failure_class": "REALIZATION_STOP",
            "registered_prediction_rejected_in_old_measurement": old_f0.get("registered_prediction_rejected") is True,
            "principle_dead_end_certified": False,
            "strict_non_tied_tasks": old_pair.get("strict_non_tied_tasks"),
            "strict_reversals": old_pair.get("strict_reversals"),
            "reason": (
                "The old rank-reversal child cannot carry scientific STOP authority: Stage-1 to Stage-4 is not one aligned treatment dose, best_score is heavily reference-censored, "
                "the six-attempt execution truncates a twenty-attempt paper protocol, and the benchmark overwhelmingly requires structural program redesign rather than a scalar stage-depth response."
            ),
        },
        "primary_evidence": {
            "stage1_stage4_same_changed_key_sets": treatment.get("stage1_stage4_same_changed_key_sets"),
            "stage1_stage4_tasks": treatment.get("tasks"),
            "changed_key_jaccard_median": treatment.get("changed_key_jaccard_median"),
            "reference_censored_cells": trajectory.get("final_best_equals_reference"),
            "real_cells": trajectory.get("result_files"),
            "run_attempt_budget": (trajectory.get("attempt_budgets") or [None])[0],
            "paper_attempt_budget": (evidence_audit.get("upstream") or {}).get("paper_attempt_budget"),
            "parameter_only_oracle_pairs": oracle.get("parameter_only"),
            "structural_oracle_pairs": oracle.get("structural_total"),
            "source_target_pairs": (evidence_audit.get("upstream") or {}).get("source_target_pairs"),
            "old_operationalization_primary_stop_class": operationalization.get("primary_stop_class"),
        },
        "residual_formulation_tested": {
            "question": "Given the correct broad repair surface and the verifier feedback observed so far, is the successful concrete mechanism/program redesign itself identifiable?",
            "required_novelty_boundary": (
                "A PACE-specific structural fact must force a different ex-ante repair/search/convergence decision from the strongest generic program-synthesis/program-repair model when both receive exactly the same surface, candidate programs, verifier history, target specification, and budget."
            ),
        },
        "same_information_contract": same_information,
        "exact_reduction": {
            "status": "SAME_INFORMATION_REDUCTION_VERIFIED",
            "baseline_family": "generic counterexample/feedback-guided program synthesis and budgeted iterative program repair",
            "formal_correspondence": {
                "PACE_candidate_program": "synthesis hypothesis h in H_surface",
                "PACE_verifier_feedback_history": "counterexample/test-feedback transcript F_1:t",
                "PACE_remaining_redesigns_consistent_with_feedback": "version/compatible set V_t = {h in H_surface : h is not ruled out by F_1:t}",
                "PACE_next_revision_choice": "query/search policy over V_t or over refinement-tree arms",
                "PACE_success": "find any h satisfying the executable specification and physical constraints",
            },
            "why_identifiability_collapses": (
                "Finite verifier feedback can leave multiple candidate programs compatible with the transcript; that is ordinary version-space/partial-identification uncertainty. "
                "Program synthesis does not require point-identifying the unique hidden reference implementation: it requires finding any satisfying program. "
                "When the practical question is which candidate to refine under a finite call budget, the object becomes the established explore-exploit/search-allocation problem rather than a new identifiability primitive."
            ),
            "decision_equivalence": (
                "Under the same information contract, a generic synthesis/repair controller can represent the same compatible candidate set, the same ambiguity, the same failed-feedback history, and the same budgeted choice among refinement branches. "
                "The current PACE formulation introduces no additional pre-outcome structural constraint that changes those decisions."
            ),
        },
        "mature_boundary_audit": {
            "REx": {
                "ref": "arXiv:2405.17503",
                "role": "direct reduction for budgeted LLM code refinement: failed tests guide repeated refinement and the remaining problem is exploration versus exploitation among candidate programs",
                "closes_by_itself": False,
                "combined_reduction_role": "load-bearing search-allocation reduction",
            },
            "CEGIS_program_synthesis": {
                "ref": "mature counterexample-guided inductive synthesis family",
                "role": "direct formal reduction for learner-proposes/verifier-falsifies iteration and version-space elimination",
                "closes_by_itself": False,
                "combined_reduction_role": "load-bearing identification/specification reduction",
            },
            "generic_agentic_program_repair": {
                "refs": ["arXiv:2403.17134"],
                "role": "shows autonomous repair already interleaves information gathering, candidate repair, validation, and feedback-conditioned tool use",
                "combined_reduction_role": "scope/precedent support",
            },
            "MOSS": {
                "ref": "arXiv:2409.16120",
                "role": "establishes broad source/code-driven evolution capability and runtime context management, but does not by itself identify which within-surface redesign will satisfy a physical specification",
                "direct_collision": False,
            },
            "PF2": {
                "ref": "generated/paper-first-pf2-method-adjudication.json",
                "role": "PF-2 concerns where to repair and already reduces its RSIC method to generic partial identification; the current PACE residual conditions on the surface being known, so PF-2 is adjacent rather than the direct closure",
                "direct_collision": False,
                "pf2_method_status": pf2.get("method_status"),
            },
        },
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "SAME_INFORMATION_REDUCTION",
            "counter_explanation": {
                "type": "SAME_INFORMATION_REDUCTION",
                "statement": (
                    "Once the broad repair surface is conditioned on, the current PACE residual is isomorphic to generic feedback-guided program synthesis/repair: a learner searches candidate programs under an executable specification while verifier feedback eliminates or reprioritizes candidates. "
                    "Non-uniqueness of the hidden successful redesign is not itself a failure of synthesis, and budget-limited inability to find a satisfying redesign is already a search/query-allocation problem."
                ),
                "same_information_or_scope_matched": True,
                "same_information_reduction_verified": True,
                "positive_support": True,
                "evidence_refs": [
                    "arXiv:2608.14441",
                    "arXiv:2405.17503",
                    "arXiv:2403.17134",
                    "arXiv:2409.16120",
                    "generated/pace-bench-principle-evidence-audit-20260818.json",
                    "generated/paper-first-pf2-method-adjudication.json"
                ],
                "alternative_explanations_ruled_out": [
                    "Repair-surface identification is the missing novelty: ruled out because the residual explicitly conditions on the broad repair surface already being known, while PF-2 separately covers where-to-repair ambiguity.",
                    "The unique official reference implementation is the scientific target: ruled out because PACE success is executable specification satisfaction, so synthesis needs any satisfying program rather than recovery of one hidden reference code artifact.",
                    "Six-attempt non-convergence proves an intrinsic redesign impossibility: ruled out because the paper protocol uses twenty attempts and the old execution is computationally censored.",
                    "Stage depth is a valid common treatment dose that can define transport: ruled out by the 3/36 equal changed-key sets and median changed-key Jaccard near 0.31.",
                    "MOSS source-level editability alone creates a new identifiability object: ruled out because editability enlarges the action space but does not change the same-information compatible-program/search-state reduction."
                ],
                "opposite_prediction": (
                    "If two repair controllers receive the same known surface, target specification, candidate/history state, verifier transcript, generator, and budget, then a PACE-specific identifiability label alone should not predict a different optimal next refinement or convergence outcome beyond a sufficiently expressive generic synthesis/search model."
                ),
                "opposite_principle": (
                    "Within a known program-repair surface, finite verifier feedback defines a compatible-program/search state, not a new point-identification primitive. Scientific novelty requires a domain-specific structural constraint that changes an ex-ante decision or attainable guarantee under identical information."
                ),
                "opposite_search_seed": (
                    "Search PACE only for a pre-outcome physics/program structural variable that changes the value of a verifier feedback item, the reachable satisfying-program set, or the optimal refinement action while the generic synthesis/search baseline receives exactly the same observable transcript and budget. Do not use unique-reference recovery, broad repair-surface labels, stage depth, or another search scheduler as the novelty axis."
                ),
                "scope": "surface-conditioned mechanism/program redesign identifiability as a standalone PACE paper problem",
                "reopen_condition": (
                    "Reopen only if first-party or independently verified PACE evidence supplies matched states with the same known repair surface, target specification, complete pre-outcome verifier transcript, candidate-program/refinement history, generator capability, and remaining budget, yet a preregistered physics/program structural variable forces a different ex-ante next-repair or success/reachability prediction that generic CEGIS/version-space, REx-style search allocation, and standard program-repair models with the same information cannot express."
                ),
            },
        },
        "scientific_interpretation": {
            "pace_source_still_useful": True,
            "pace_benchmark_scientifically_exhausted": False,
            "current_residual_active": False,
            "revised_f0_authorized": False,
            "provider_formulation_review_required": False,
            "reason_provider_review_not_run": "The exact same-information reduction closes the current formulation before formulation/reviewer provider calls; provider review is reserved for a residual that survives reduction.",
            "next_action": "Archive the invalid rank-reversal child separately, persist this scoped principle closure, and return PACE to evidence-asset status until a genuinely different same-information residual is found.",
        },
        "authority": {
            "experiment_alone_authorizes_dead_end": False,
            "same_information_counter_explanation_authorizes_scoped_dead_end": True,
            "benchmark_level_dead_end": False,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "evidence_audit": _sha(EVIDENCE_AUDIT),
            "old_rank_reversal_f0": _sha(OLD_F0),
            "pf2_method_adjudication": _sha(PF2),
        },
    }


def validate_readjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("parent_source") != PRIMARY_REF:
        errors.append("wrong PACE parent source")
    if state.get("stop_class") != "PRINCIPLE_STOP" or state.get("principle_dead_end_certified") is not True:
        errors.append("PACE current redesign-identifiability reduction must be a scoped PRINCIPLE_STOP")
    if state.get("benchmark_level_dead_end_certified") is not False:
        errors.append("PACE benchmark itself must not be globally dead-ended")
    old = state.get("old_rank_reversal_child") or {}
    if old.get("status") != "ARCHIVED_INVALID_OPERATIONALIZATION" or old.get("stop_class") != "PROTOCOL_STOP" or old.get("principle_dead_end_certified") is not False:
        errors.append("old PACE rank-reversal child must remain invalid-operationalization protocol stop")
    evidence = state.get("primary_evidence") or {}
    required = {
        "stage1_stage4_same_changed_key_sets": 3,
        "stage1_stage4_tasks": 36,
        "reference_censored_cells": 17,
        "real_cells": 24,
        "run_attempt_budget": 6,
        "paper_attempt_budget": 20,
        "parameter_only_oracle_pairs": 4,
        "structural_oracle_pairs": 140,
        "source_target_pairs": 144,
    }
    for key, expected in required.items():
        if evidence.get(key) != expected:
            errors.append(f"PACE primary evidence drift:{key}")
    reduction = state.get("exact_reduction") or {}
    if reduction.get("status") != "SAME_INFORMATION_REDUCTION_VERIFIED":
        errors.append("PACE same-information reduction is not verified")
    counter = ((state.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    if counter.get("same_information_or_scope_matched") is not True or counter.get("same_information_reduction_verified") is not True or not counter.get("reopen_condition"):
        errors.append("PACE principle closure lacks scope-matched counter-explanation/reopen condition")
    interpretation = state.get("scientific_interpretation") or {}
    if interpretation.get("revised_f0_authorized") is not False or interpretation.get("provider_formulation_review_required") is not False:
        errors.append("reduced PACE residual cannot authorize revised F0/provider formulation")
    return errors


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    state = build_readjudication()
    errors = validate_readjudication(state)
    if errors:
        raise ValueError("Invalid PACE principle readjudication: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
