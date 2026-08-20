from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT


SCHEMA_VERSION = "1.0"
CANDIDATE_ID = "PA-07-SCHEDULE-CONDITIONAL-EVOLUTION"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-schedule-conditional-evolution-scout-20260820.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical_sha256(payload: dict[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key not in {"generated_at", "receipt_sha256"}}
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_schedule_conditional_evolution_scout() -> dict[str, Any]:
    """Build a zero-authority paper-incubation receipt from independently reviewed primary sources."""
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "candidate_id": CANDIDATE_ID,
        "title": "Evolution Gain Is Schedule-Conditional: Separating Persistent Update from Endogenous Curriculum Effects",
        "status": "HOLD_SUBSTRATE_AUDIT",
        "paper_state": "INCUBATION_EVIDENCE_BOUND",
        "discovery_lane": "IDENTIFIABILITY_GAP",
        "paperability_axes": {
            "P": "REDUCED",
            "M": "NOT_CLAIMED",
            "E": "OPEN",
            "B": "PLAUSIBLE",
            "T": "NOT_CLAIMED",
            "S": "NOT_CLAIMED",
        },
        "primary_evidence": [
            {
                "source_ref": "arXiv:2607.29468",
                "title": "SESA: Self-Evolving Search Agents",
                "url": "https://arxiv.org/abs/2607.29468",
                "code_url": "https://github.com/Zenghuang-Fu/SESA-Self-Evolving-Search-Agents",
                "role": "EMPIRICAL_FACT",
                "source_grounded_observation": (
                    "SESA couples a problem proposer/challenger to a solver whose persistent skill state is updated "
                    "from failures; solver outcomes enter the proposer objective, so the training problem stream is "
                    "endogenous to solver behavior rather than a fixed external schedule."
                ),
                "does_not_establish": (
                    "It does not by itself identify the direct effect of the solver's persistent update separately "
                    "from the effect of the induced problem schedule."
                ),
            },
            {
                "source_ref": "arXiv:2606.02461",
                "title": "AgentCL: A Benchmark for Continual Learning in Language Agents",
                "url": "https://arxiv.org/abs/2606.02461",
                "role": "NEAREST_COLLISION",
                "source_grounded_observation": (
                    "AgentCL explicitly controls compositional versus naive sequential task streams and measures "
                    "continual-learning transfer, making generic task-order and non-stationarity claims occupied."
                ),
                "does_not_establish": (
                    "The reviewed paper does not claim the crossed replay decomposition of a schedule generated "
                    "endogenously by a co-evolving challenger."
                ),
            },
            {
                "source_ref": "arXiv:2608.06144",
                "title": "FinEvo-Bench",
                "url": "https://arxiv.org/abs/2608.06144",
                "role": "EMPIRICAL_FACT",
                "source_grounded_observation": (
                    "FinEvo-Bench evaluates self-evolution with paired non-evolving controls over independently "
                    "shuffled and interleaved streams, demonstrating that order-aware controls are already expected."
                ),
                "does_not_establish": "Its released evaluation is not the endogenous-challenger mediation decomposition proposed here.",
            },
            {
                "source_ref": "arXiv:2605.18421",
                "title": "EvoMemBench",
                "url": "https://arxiv.org/abs/2605.18421",
                "code_url": "https://github.com/DSAIL-Memory/EvoMemBench",
                "role": "EMPIRICAL_FACT",
                "source_grounded_observation": (
                    "EvoMemBench compares memory methods across task structures and reports that persistent-memory "
                    "benefit is not uniform, supporting task-structure sensitivity as a necessary baseline."
                ),
                "does_not_establish": "It does not isolate an endogenous schedule mediator in proposer-solver co-evolution.",
            },
            {
                "source_ref": "arXiv:2604.08988",
                "title": "SEA-Eval",
                "url": "https://arxiv.org/abs/2604.08988",
                "role": "EVALUATION_CONTEXT",
                "source_grounded_observation": (
                    "SEA-Eval treats self-evolution as sequential evaluation and shows that equal task success can "
                    "hide materially different cost and trajectory behavior."
                ),
                "does_not_establish": "It does not estimate direct persistent-update and schedule-mediated effects.",
            },
        ],
        "phenomenon": {
            "scientific_object": "coevolving-proposer-solver-evaluation",
            "mechanism_axis": "persistent-update-versus-endogenous-schedule-mediation",
            "claim_type": "benchmark-identifiability",
            "source_grounded": (
                "In co-evolving proposer-solver systems, the solver update changes solver outcomes while solver outcomes "
                "also affect the future problem distribution; an aggregate evolving-versus-static comparison therefore "
                "mixes at least two causal paths."
            ),
            "not_yet_observed": (
                "No reviewed source establishes that schedule mediation is nonzero, dominant, harmful, or beneficial "
                "for SESA or any other specific system."
            ),
        },
        "problem_contract": {
            "research_question": (
                "For a frozen proposer-generated task schedule, how much of held-out performance change is attributable "
                "to the solver's persistent update, and how much is attributable to the schedule induced by co-evolution?"
            ),
            "treatment": "solver persistent update enabled versus disabled",
            "mediator": "recorded task schedule generated by evolved versus control challenger",
            "outcome": "held-out success, token cost, and trajectory-level transfer under the same replayed prompts",
            "estimand": (
                "Direct update contrast within each frozen schedule plus the schedule contrast within each frozen solver "
                "state; interaction is reported but not interpreted as a new mechanism without a same-information residual."
            ),
            "strongest_same_information_reduction": (
                "ordinary curriculum/order effects plus additive skill-set quality and selector regret; AgentCL-style "
                "controlled streams are the nearest benchmark baseline"
            ),
            "narrow_candidate_claim": (
                "Aggregate self-evolution gain is not an identifiable estimate of persistent-update benefit when the "
                "training schedule is endogenous; a crossed frozen-schedule replay is required to separate the paths."
            ),
            "forbidden_claims": [
                "SESA gains are invalid",
                "endogenous curricula are harmful",
                "persistent memory has no direct benefit",
                "task order effects are novel",
                "a nonzero factorial interaction proves a self-evolution-specific principle",
            ],
        },
        "novelty_review": {
            "status": "PARTIAL_SURVIVOR_STRONG_COLLISION",
            "nearest_collision": "arXiv:2606.02461",
            "occupied_claim": "task order and controlled continual-learning streams affect agent adaptation",
            "surviving_narrow_gap": (
                "causal decomposition of persistent solver update and an endogenous challenger-generated schedule using "
                "crossed frozen replay"
            ),
            "stop_if": (
                "AgentCL or another current primary source already crosses persistent-state update with frozen schedules "
                "generated by an endogenous co-evolving challenger, or the distinction reduces completely to its existing metrics."
            ),
        },
        "substrate_audit": {
            "target": "official SESA repository",
            "repository": "https://github.com/Zenghuang-Fu/SESA-Self-Evolving-Search-Agents",
            "status": "HOLD_NATIVE_REPLAY_PATH_UNVERIFIED",
            "reviewed_release_surface": [
                "proposer and solver training configuration",
                "skill-bank update controls",
                "saved checkpoints, rollouts, trajectories, and skill-bank outputs",
            ],
            "inference_not_authority": (
                "Recorded questions/rollouts suggest replay may be implementable, but no native freeze-and-replay interface "
                "was verified from code during this audit."
            ),
            "required_before_f0_design": [
                "pin first-party commit and archive hash",
                "verify exact task/question lineage is persisted",
                "verify the same recorded prompts can be replayed across solver update states without wrapper-induced substrate change",
                "verify proposer and solver state checkpoints can be independently frozen",
                "define leakage-free held-out schedule construction",
            ],
            "acquisition_failure": {
                "failure_code": "RUNTIME_ERROR",
                "affected_layer": "execution-acquisition",
                "event": "official repository clone and ls-remote timed out through the remote transport",
                "belief_authority": False,
                "allowed_effect": ["require_repair"],
                "scientific_effect": "none",
            },
        },
        "cheapest_problem_falsifier": {
            "status": "DESIGNED_NOT_AUTHORIZED",
            "crossed_cells": [
                "update_on x evolved_schedule",
                "update_off x evolved_schedule",
                "update_on x control_schedule",
                "update_off x control_schedule",
            ],
            "frozen_controls": [
                "exact replay prompts and order within schedule",
                "base solver checkpoint",
                "inference budget and decoding",
                "evaluation harness and held-out outcomes",
            ],
            "decision_rule": (
                "Stop the paper direction if crossed replay is already available in prior work, cannot be implemented on "
                "the first-party substrate without changing the scientific object, or aggregate gain is fully explained by "
                "the strongest controlled-stream/additive baseline with no remaining evaluation-identifiability consequence."
            ),
            "model_calls_executed": 0,
            "task_trials_executed": 0,
        },
        "claim_ledger": [
            {
                "claim_id": "PA-07-C1",
                "statement": "SESA-like co-evolution makes the task schedule endogenous to solver behavior.",
                "status": "LITERATURE_SUPPORTED",
                "evidence_refs": ["arXiv:2607.29468"],
            },
            {
                "claim_id": "PA-07-C2",
                "statement": "Generic task-order sensitivity is not a novel contribution.",
                "status": "COLLISION_SUPPORTED",
                "evidence_refs": ["arXiv:2606.02461", "arXiv:2608.06144"],
            },
            {
                "claim_id": "PA-07-C3",
                "statement": "Persistent-update benefit and schedule-mediated benefit differ materially on SESA.",
                "status": "UNSUPPORTED_AWAIT_F0",
                "evidence_refs": [],
            },
            {
                "claim_id": "PA-07-C4",
                "statement": "Crossed replay improves scientific identifiability of co-evolution evaluations.",
                "status": "PROBLEM_CONTRACT_NOT_EMPIRICAL_CLAIM",
                "evidence_refs": [],
            },
        ],
        "paper_progression": [
            {"stage": "literature", "status": "PASS_PRIMARY_SOURCE_RECEIPT"},
            {"stage": "phenomenon", "status": "PASS_SOURCE_GROUNDED_COUPLING"},
            {"stage": "problem_contract", "status": "FORMULATED_ZERO_AUTHORITY"},
            {"stage": "novelty", "status": "HOLD_EXACT_COLLISION_REVIEW"},
            {"stage": "substrate", "status": "HOLD_NATIVE_REPLAY_PATH_UNVERIFIED"},
            {"stage": "f0_identifiability", "status": "BLOCKED_BY_SUBSTRATE_HOLD"},
            {"stage": "method", "status": "NOT_AUTHORIZED"},
            {"stage": "experiment", "status": "NOT_AUTHORIZED"},
            {"stage": "paper_evidence", "status": "NOT_STARTED"},
            {"stage": "paper", "status": "INCUBATION_ONLY"},
        ],
        "reopen_condition": (
            "Resume only after a pinned first-party SESA revision or verified code audit shows exact challenger schedule "
            "lineage plus native same-prompt replay across independently frozen solver update states."
        ),
        "provenance": {
            "parent_candidates": [],
            "source_count": 5,
            "elimination_count": 0,
            "review_receipt": "manual-primary-source-audit-20260820",
            "provenance_status": "PRIMARY_METADATA_BOUND_NOT_SOURCE_ARCHIVED",
        },
        "policy": {
            "memory_cannot_replace_scientific_judgment": True,
            "execution_failure_cannot_become_scientific_failure": True,
            "scientific_conclusions_are_not_mutated": True,
            "source_receipt_does_not_grant_problem_gate": True,
            "problem_contract_does_not_grant_method_authority": True,
            "substrate_hold_blocks_f0_and_all_downstream_stages": True,
            "paper_outline_is_not_paper_evidence": True,
        },
        "scientific_authority": False,
        "authority": {
            "canonical_generator": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
            "paper_claim": False,
        },
    }
    state["receipt_sha256"] = _canonical_sha256(state)
    return state


def validate_schedule_conditional_evolution_scout(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate id drift")
    if state.get("status") != "HOLD_SUBSTRATE_AUDIT":
        errors.append("unverified substrate must remain HOLD_SUBSTRATE_AUDIT")
    if state.get("paper_state") != "INCUBATION_EVIDENCE_BOUND":
        errors.append("scout cannot claim paper-ready status")
    if state.get("receipt_sha256") != _canonical_sha256(state):
        errors.append("receipt hash mismatch")
    evidence = [row for row in state.get("primary_evidence") or [] if isinstance(row, dict)]
    if len(evidence) < 4 or any(not row.get("source_ref") or not row.get("url") or not row.get("does_not_establish") for row in evidence):
        errors.append("primary evidence boundary incomplete")
    novelty = state.get("novelty_review") or {}
    if novelty.get("nearest_collision") != "arXiv:2606.02461" or not novelty.get("stop_if"):
        errors.append("nearest collision or novelty stop missing")
    substrate = state.get("substrate_audit") or {}
    failure = substrate.get("acquisition_failure") or {}
    if substrate.get("status") != "HOLD_NATIVE_REPLAY_PATH_UNVERIFIED":
        errors.append("substrate audit status drift")
    if failure.get("belief_authority") is not False or failure.get("scientific_effect") != "none":
        errors.append("execution acquisition failure leaked scientific authority")
    falsifier = state.get("cheapest_problem_falsifier") or {}
    if len(falsifier.get("crossed_cells") or []) != 4 or falsifier.get("model_calls_executed") != 0:
        errors.append("crossed zero-execution falsifier contract incomplete")
    claims = {row.get("claim_id"): row for row in state.get("claim_ledger") or [] if isinstance(row, dict)}
    if (claims.get("PA-07-C3") or {}).get("status") != "UNSUPPORTED_AWAIT_F0":
        errors.append("unobserved causal effect became supported")
    if state.get("scientific_authority") is not False or any(bool(value) for value in (state.get("authority") or {}).values()):
        errors.append("scout illegally carries downstream authority")
    progression = {row.get("stage"): row.get("status") for row in state.get("paper_progression") or [] if isinstance(row, dict)}
    if progression.get("f0_identifiability") != "BLOCKED_BY_SUBSTRATE_HOLD" or progression.get("paper") != "INCUBATION_ONLY":
        errors.append("paper progression bypassed substrate hold")
    return errors


def write_schedule_conditional_evolution_scout(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    state = build_schedule_conditional_evolution_scout()
    errors = validate_schedule_conditional_evolution_scout(state)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_schedule_conditional_evolution_scout(), ensure_ascii=False, indent=2))
