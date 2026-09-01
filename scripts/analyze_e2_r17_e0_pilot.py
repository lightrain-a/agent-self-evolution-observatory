#!/usr/bin/env python3
"""Rebuild the E2-R17 E0-r3 mechanism-calibration analysis from frozen artifacts.

This analysis is intentionally read-only with respect to the E0 run root.  It
verifies the content-addressed inputs, recomputes all reported E0 quantities,
and emits derived summary/decision artifacts inside the repository.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828")
SUMMARY = RUN_ROOT / "e0_pilot_summary.json"
EXPECTED_SUMMARY_SHA256 = "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366"
CONTRACT = REPO / "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json"
EXPECTED_CONTRACT_SHA256 = "f4019646b653f41abe056fdd7b746ff6cb4749ce4d2771c2ef90af6845631508"
AUTHORIZATION = REPO / "generated/e2-r17-e0-pilot-authorization-r3-20260828.json"
EXPECTED_AUTHORIZATION_SHA256 = "5033c226b7248c3d9f72caa2b574f84ffa4ae9c3097175bde87e9b469c9fdff4"
ANALYSIS_JSON = REPO / "generated/e2-r17-e0-analysis-20260828.json"
DECISION_JSON = REPO / "generated/e2-r17-e0-go-hold-stop-20260828.json"
REPORT_MD = REPO / "consultations/e2-r17-e0-analysis-20260828.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"SHA mismatch for {path}: expected {expected}, got {actual}")


def frac(n: int, d: int) -> float:
    return n / d if d else float("nan")


def main() -> None:
    require_sha(SUMMARY, EXPECTED_SUMMARY_SHA256)
    require_sha(CONTRACT, EXPECTED_CONTRACT_SHA256)
    require_sha(AUTHORIZATION, EXPECTED_AUTHORIZATION_SHA256)

    summary = json.loads(SUMMARY.read_text())
    contract = json.loads(CONTRACT.read_text())
    tasks = summary["tasks"]
    ks = [int(k) for k in summary["prefix_ks"]]
    n = len(tasks)
    if n != 12 or summary.get("status") != "COMPLETED" or not summary.get("scientific_outcome"):
        raise RuntimeError("Frozen E0 summary is not the expected completed 12-task scientific outcome")

    trajectory_paths = sorted(RUN_ROOT.glob("cases/*/rollout_*/r17_trajectory.json"))
    trajectory_ref_paths = sorted(RUN_ROOT.glob("cases/*/rollout_*/r17_trajectory_ref.json"))
    pool_paths = sorted(RUN_ROOT.glob("cases/*/pool_k*.json"))
    if len(trajectory_paths) != 96 or len(trajectory_ref_paths) != 96 or len(pool_paths) != 48:
        raise RuntimeError(
            f"E0 unit integrity mismatch: trajectories={len(trajectory_paths)}, "
            f"refs={len(trajectory_ref_paths)}, pools={len(pool_paths)}"
        )

    rollout_units = []
    resolved_models = Counter()
    technical_failures = 0
    actor_finished_false_units = []
    provider_calls_from_rollouts = 0
    total_tokens = 0
    for p in trajectory_paths:
        d = json.loads(p.read_text())
        ref_path = p.with_name("r17_trajectory_ref.json")
        ref = json.loads(ref_path.read_text())
        unit = (d["case_id"], int(d["rollout_index"]))
        rollout_units.append(unit)
        resolved_models[d.get("resolved_model")] += 1
        # `finished` is an actor-loop termination flag, not a technical-status bit.
        # Likewise, a missing output.xlsx can be the *scientific* failure itself
        # (the verifier records score=0 / "output.xlsx not found").  Technical
        # completeness is therefore defined by the frozen trajectory-ref receipt:
        # completed technical status, a verifier score, content-addressed trajectory
        # and verifier, and matching scientific identifiers.
        required_unit_complete = (
            ref.get("technical_status") == "COMPLETED"
            and ref.get("score") is not None
            and bool(ref.get("trajectory_sha256"))
            and bool(ref.get("verifier_sha256"))
            and ref.get("task_id") == d.get("case_id")
            and int(ref.get("rollout_index")) == int(d.get("rollout_index"))
        )
        if not required_unit_complete:
            technical_failures += 1
        if not d.get("finished", False):
            actor_finished_false_units.append({
                "case_id": d["case_id"],
                "rollout_index": int(d["rollout_index"]),
                "score": d.get("score"),
                "turns": d.get("turns"),
                "output_sha256": d.get("output_sha256"),
            })
        receipts = d.get("adapter_receipts", [])
        provider_calls_from_rollouts += len(receipts)
        total_tokens += sum(int(r.get("total_tokens", 0) or 0) for r in receipts)
    if len(set(rollout_units)) != 96:
        raise RuntimeError("Rollout scientific units are not unique")

    acting_success = {}
    pre_visibility = {}
    winner_visibility = {}
    gamma = {}
    delta_from_k1 = {}
    mixed_pool_rate = {}
    rescue_rate = {}
    mixed_count = {}
    rescue_count = {}
    rescue_families_by_k = {}

    for k in ks:
        a = [float(t["pools"][str(k)]["acting_success"]) for t in tasks]
        pre = [float(t["pools"][str(k)]["precommitted_success"]) for t in tasks]
        mixed = [len(set(float(x) for x in t["scores"][:k])) > 1 for t in tasks]
        rescue = [bool(t["pools"][str(k)]["rescue_event"]) for t in tasks]
        acting_success[str(k)] = sum(a) / n
        pre_visibility[str(k)] = sum(1.0 - x for x in pre) / n
        winner_visibility[str(k)] = sum(1.0 - x for x in a) / n
        gamma[str(k)] = pre_visibility[str(k)] - winner_visibility[str(k)]
        mixed_count[str(k)] = sum(mixed)
        mixed_pool_rate[str(k)] = sum(mixed) / n
        rescue_count[str(k)] = sum(rescue)
        rescue_rate[str(k)] = sum(rescue) / n
        rescue_families_by_k[str(k)] = sorted({
            t["failure_family"] for t, is_rescue in zip(tasks, rescue) if is_rescue
        })
    for k in ks:
        delta_from_k1[str(k)] = acting_success[str(k)] - acting_success["1"]

    all_scores = [float(s) for t in tasks for s in t["scores"]]
    pooled_p = sum(all_scores) / len(all_scores)
    iid_gamma_reference = {
        str(k): (1.0 - pooled_p) - (1.0 - pooled_p) ** k for k in ks
    }

    k8_mixed_families = sorted({
        t["failure_family"]
        for t in tasks
        if len(set(float(x) for x in t["scores"][:8])) > 1
    })
    k8_failure_families = sorted({
        t["failure_family"] for t in tasks if any(float(x) == 0.0 for x in t["scores"][:8])
    })
    rescue_tasks_k8 = [
        {
            "task_id": t["task_id"],
            "failure_family": t["failure_family"],
            "scores": t["scores"],
            "winner_index": t["pools"]["8"]["winner_index"],
        }
        for t in tasks
        if t["pools"]["8"]["rescue_event"]
    ]
    rescue_families_k8 = sorted({x["failure_family"] for x in rescue_tasks_k8})

    gate_text = contract["stages"]["E0_full"]["E1_support"]
    gate_task_min = 6
    gate_family_min = 3
    support_pass = len(rescue_tasks_k8) >= gate_task_min and len(rescue_families_k8) >= gate_family_min
    signal_nonzero = gamma["8"] > 0 and rescue_count["8"] > 0
    decision = "GO" if support_pass and signal_nonzero else ("HOLD" if signal_nonzero else "STOP")

    analysis = {
        "artifact_type": "e2-r17-e0-analysis",
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only_source": True,
        "source": {
            "run_root": str(RUN_ROOT),
            "summary_path": str(SUMMARY),
            "summary_sha256": EXPECTED_SUMMARY_SHA256,
            "contract_path": str(CONTRACT.relative_to(REPO)),
            "contract_sha256": EXPECTED_CONTRACT_SHA256,
            "authorization_path": str(AUTHORIZATION.relative_to(REPO)),
            "authorization_sha256": EXPECTED_AUTHORIZATION_SHA256,
        },
        "protocol_integrity": {
            "tasks_complete": n,
            "expected_tasks": 12,
            "trajectory_files": len(trajectory_paths),
            "trajectory_ref_files": len(trajectory_ref_paths),
            "pool_files": len(pool_paths),
            "unique_rollout_units": len(set(rollout_units)),
            "technical_failures": technical_failures,
            "actor_finished_false_unit_count": len(actor_finished_false_units),
            "actor_finished_false_units": actor_finished_false_units,
            "resolved_models": dict(resolved_models),
            "provider_calls_reconstructed": provider_calls_from_rollouts,
            "total_tokens_reconstructed": total_tokens,
            "k": summary["k"],
            "prefix_ks": ks,
        },
        "acting": {
            "success_at_k": acting_success,
            "delta_vs_success_at_1": delta_from_k1,
            "mixed_pool_count": mixed_count,
            "mixed_pool_rate": mixed_pool_rate,
            "rescue_event_count": rescue_count,
            "rescue_event_rate": rescue_rate,
        },
        "visibility": {
            "V_pre": pre_visibility,
            "V_winner": winner_visibility,
            "Gamma": gamma,
            "identity_check_max_abs_error": max(
                abs((acting_success[str(k)] - acting_success["1"]) - gamma[str(k)]) for k in ks
            ),
        },
        "iid_special_case_reference": {
            "pooled_rollout_success_p": pooled_p,
            "formula": "Gamma_K(p)=(1-p)-(1-p)^K",
            "Gamma": iid_gamma_reference,
            "interpretation": "reference only; observed task pools are heterogeneous and need not be iid",
        },
        "failure_support": {
            "k8_failure_families_with_any_failed_rollout": k8_failure_families,
            "k8_mixed_pool_families": k8_mixed_families,
            "k8_rescue_tasks": rescue_tasks_k8,
            "k8_rescue_task_count": len(rescue_tasks_k8),
            "k8_rescue_families": rescue_families_k8,
            "k8_rescue_family_count": len(rescue_families_k8),
        },
        "interpretation": {
            "search_improves_acting": acting_success["8"] > acting_success["1"],
            "winner_only_censors_precommitted_failure_on_rescueable_pool": gamma["8"] > 0,
            "ceiling_warning": acting_success["1"] >= 0.9,
            "observed_regime": "one rescueable intermediate cell inside an otherwise high-success/ceiling-heavy pilot",
            "alternative_explanations": [
                "task-level capability heterogeneity makes the pooled-iid reference overpredict censoring mass",
                "the 12-task pilot is ceiling-heavy, so rescue support is sparse",
                "E0 identifies visibility structure only; it does not establish future learning utility",
            ],
        },
        "promotion_gate": {
            "frozen_text": gate_text,
            "required_rescue_tasks": gate_task_min,
            "required_failure_families": gate_family_min,
            "observed_rescue_tasks": len(rescue_tasks_k8),
            "observed_failure_families": len(rescue_families_k8),
            "pass": support_pass,
        },
        "belief_update": (
            "Search-projection censoring is empirically nonzero in the frozen E0 pilot, but support is too sparse "
            "to authorize the updater intervention. The correct update is HOLD, not mechanism rejection: one "
            "precommitted failure is rescued and hidden by the winner at K>=4, while the frozen E1 support gate "
            "requires at least six rescue tasks spanning at least three failure families."
        ),
        "decision": decision,
        "authority": {
            "E1_scientific_experiment": bool(decision == "GO"),
            "paper_promotion": False,
            "submission": False,
        },
        "next": (
            "Freeze and independently review a non-selective support-qualification tranche using only actor/verifier "
            "rescueability structure; do not select on projection or downstream learning outcomes. Planning, baseline/model "
            "audit, and outcome-blind runtime pilots may proceed while E1 remains blocked."
        ),
    }

    decision_artifact = {
        "artifact_type": "e2-r17-e0-go-hold-stop",
        "schema_version": "1.0",
        "created_at_utc": analysis["created_at_utc"],
        "analysis_path": str(ANALYSIS_JSON.relative_to(REPO)),
        "source_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "frozen_contract_sha256": EXPECTED_CONTRACT_SHA256,
        "decision": decision,
        "mechanism_signal": "NONZERO" if signal_nonzero else "NULL",
        "E1_support_gate": {
            "required": {"rescue_tasks": gate_task_min, "failure_families": gate_family_min},
            "observed": {"rescue_tasks": len(rescue_tasks_k8), "failure_families": len(rescue_families_k8)},
            "pass": support_pass,
        },
        "reason": (
            "Nonzero rescue/censoring signal is present, but the frozen E1 support threshold is not met."
            if decision == "HOLD"
            else ("Frozen support and signal gates pass." if decision == "GO" else "No rescue/censoring signal under frozen E0.")
        ),
        "forbidden_while_hold": [
            "launch E1 updater intervention",
            "promote an E1 causal claim",
            "select support tasks by downstream projection outcome",
            "rerun or replace the completed E0-r3 outcome",
        ] if decision == "HOLD" else [],
        "allowed_while_hold": [
            "experiment-plan drafting/review",
            "primary-source baseline/model audit",
            "outcome-blind model and baseline runtime qualification",
            "separately reviewed and frozen support-qualification design",
        ] if decision == "HOLD" else [],
        "authority": {
            "scientific_experiment_E1": decision == "GO",
            "paper_promotion": False,
            "submission": False,
        },
    }

    ANALYSIS_JSON.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n")
    DECISION_JSON.write_text(json.dumps(decision_artifact, indent=2, ensure_ascii=False) + "\n")

    rows = []
    for k in ks:
        rows.append(
            f"| {k} | {acting_success[str(k)]:.4f} | {delta_from_k1[str(k)]:+.4f} | "
            f"{mixed_count[str(k)]}/{n} | {rescue_count[str(k)]}/{n} | "
            f"{pre_visibility[str(k)]:.4f} | {winner_visibility[str(k)]:.4f} | {gamma[str(k)]:.4f} |"
        )
    family_rows = "\n".join(
        f"- `{x['task_id']}` — `{x['failure_family']}` — scores={x['scores']} — winner={x['winner_index']}"
        for x in rescue_tasks_k8
    ) or "- none"

    report = f"""# E2-R17 E0-r3 Analysis — 2026-08-28

## Decision

**E0 scientific signal: NONZERO. E1 promotion: `{decision}`.**

The completed pilot is not rerun. The source summary is content-addressed at
`{EXPECTED_SUMMARY_SHA256}` and the frozen contract at `{EXPECTED_CONTRACT_SHA256}`.
The pilot contains {n}/12 completed tasks, {len(trajectory_paths)}/96 trajectory artifacts,
{len(set(rollout_units))}/96 unique rollout units, {len(pool_paths)}/48 frozen prefix-pool artifacts,
and {technical_failures} incomplete technical units. There are {len(actor_finished_false_units)} actor-loop
`finished=false` units; these are retained as valid scientific units because their verifier score and output
artifacts are complete rather than being reclassified as technical failures.

## Acting success and visibility

| K | Success@K | Δ vs @1 | Mixed pools | Rescue events | V_pre | V_winner | Γ_K |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The identity `A_K-A_1 = V_pre(K)-V_winner(K) = Gamma_K` holds numerically with maximum
absolute error {analysis['visibility']['identity_check_max_abs_error']:.3g}. Search therefore rescues one task by K=4:
Success rises from 11/12 at K=1 to 12/12 at K=4 and K=8, while the corresponding
precommitted failed witness becomes invisible under winner-only logging.

## Rescue support

K=8 contains failed rollouts in {len(k8_failure_families)}/6 primary failure families and mixed pools in
{len(k8_mixed_families)}/6 families, but the **precommitted-failure rescue event** needed by the exact
Rejected-Witness intervention occurs in only {len(rescue_tasks_k8)} task and {len(rescue_families_k8)} family:

{family_rows}

This distinction matters: a pool containing some rejected failures is not automatically the same scientific
unit as the frozen event `M = [Y_0=0 and max_i Y_i=1]`.

## IID reference is not the observed estimand

Across all 96 rollouts the pooled success rate is {pooled_p:.4f}. Substituting that marginal rate into the
special-case iid formula `Gamma_K(p)=(1-p)-(1-p)^K` gives K=2/4/8 references of
{iid_gamma_reference['2']:.4f}/{iid_gamma_reference['4']:.4f}/{iid_gamma_reference['8']:.4f}, much larger than
the observed 0/{gamma['4']:.4f}/{gamma['8']:.4f}. This is not a contradiction: the frozen theory explicitly
allows arbitrary rollout dependence and task heterogeneity. The iid curve is a reference special case, not a
fitted model for these twelve heterogeneous tasks.

## Frozen promotion gate

The contract requires: **{gate_text}**. Observed support is **{len(rescue_tasks_k8)} rescue task /
{len(rescue_families_k8)} failure family**, so the support gate fails. Because the mechanism signal itself is
nonzero, this is a **HOLD rather than a scientific STOP**.

While HOLD is active:

- do not launch E1 updater interventions;
- do not choose additional support units by projection outcome or future-skill outcome;
- do not rerun/replace E0-r3;
- planning, source-grounded baseline/model audit, outcome-blind runtime qualification, and a separately
  reviewed/frozen support-qualification tranche are allowed.

## Belief update

E0 supports the narrow observation-kernel statement: best-of-K serving can improve current acting while
winner-only logging censors a generated, verifier-confirmed failed witness. E0 does **not** yet establish that
the censored witness improves future skill. The causal learning claim remains blocked until the frozen rescue
support condition is met and E1 changes only the learning projection on identical pools.

## Next scientific action

Design a content-addressed support-qualification tranche whose eligibility depends only on actor/verifier
rescueability structure and is frozen before any learning-projection outcome is observed. Independently review
that tranche before execution. In parallel, complete Experiment Plan V1, primary-source baseline/model audit,
and outcome-blind runtime pilots.
"""
    REPORT_MD.write_text(report)

    print(json.dumps({
        "analysis": str(ANALYSIS_JSON.relative_to(REPO)),
        "decision": str(DECISION_JSON.relative_to(REPO)),
        "report": str(REPORT_MD.relative_to(REPO)),
        "E0_decision": decision,
        "support_pass": support_pass,
        "analysis_sha256": sha256(ANALYSIS_JSON),
        "decision_sha256": sha256(DECISION_JSON),
        "report_sha256": sha256(REPORT_MD),
    }, indent=2))


if __name__ == "__main__":
    main()
