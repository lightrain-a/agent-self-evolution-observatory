from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .alfworld_react_scaffold import task_family_from_gamefile
from .config import StorageSettings, resolve_experiment_data_root
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_alfworld_collect import _task_family_order, generate_a1_candidates
from .p0_common import git_head, load_json


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


GATE_ROWS: tuple[dict[str, Any], ...] = (
    {"rank": 1, "idea_id": "active-causal-minimal-rollback", "offline": "conditional", "reality": "pass", "phenomenon": "hold", "decision": "hold", "reason": "Synthetic faults have independent truth, but real version histories still lack an independent oracle for the minimal restoring rollback set.", "next_action": "Mine real composition-regression cases where causal rollback disagrees with chronology/lineage before GPU use."},
    {"rank": 2, "idea_id": "future-reuse-harm-predictor", "offline": "pass", "reality": "pass", "phenomenon": "hold", "decision": "secondary", "reason": "Memory negative transfer is real, but the narrower residual/recovery-incompleteness harm claim is not independently established.", "next_action": "Keep as a preregistered secondary analysis inside #3 without extra executions."},
    {"rank": 3, "idea_id": "replicated-effect-memory-gate", "offline": "pass", "reality": "pass", "phenomenon": "pass", "decision": "small-p0", "reason": "Future-task memory harm is real; retrieved/no-memory/matched-placebo arms admit independent environment-scored truth and an identifiable replicated-effect boundary.", "next_action": "Enter the shared P0-MEM-XFER-CAUSAL run."},
    {"rank": 4, "idea_id": "version-differential-active-diagnosis", "offline": "pass", "reality": "stop", "phenomenon": "not-run", "decision": "stop", "reason": "The current thesis reduces to learned/probabilistic delta-debugging order and directly collides with ProbDD/PMA-style mechanisms.", "next_action": "Reopen only with a distinct persistent repair/rollback representation."},
    {"rank": 5, "idea_id": "cross-task-effect-transport-certificate", "offline": "pass", "reality": "pass", "phenomenon": "pass", "decision": "small-p0", "reason": "Cross-domain memory evidence shows source-task usefulness is not target-family transportability; zero-target-label effect-sign prediction with abstention remains identifiable.", "next_action": "Share the same treatment table with #3 inside P0-MEM-XFER-CAUSAL."},
    {"rank": 6, "idea_id": "precommit-workflow-transfer-certificate", "offline": "pass", "reality": "stop", "phenomenon": "not-run", "decision": "stop", "reason": "The current form remains a calibrated workflow-performance predictor/certificate; existing workflow predictors cover the main mechanism.", "next_action": "Reopen only as a risk-constrained workflow update operator rather than a predictor."},
    {"rank": 7, "idea_id": "simulator-distilled-risk-memory", "offline": "pass", "reality": "pass", "phenomenon": "hold", "decision": "hold", "reason": "The verifier-grounded simulator-off boundary is meaningful, but irreversible or goal-unreachable action-state prevalence must first be measured with CPU/PDDL checks.", "next_action": "Run CPU phenomenon qualification first and stop if prevalence is insufficient."},
    {"rank": 8, "idea_id": "actor-evaluator-residual-gate", "offline": "pass", "reality": "stop", "phenomenon": "not-run", "decision": "stop", "reason": "Interaction-residual factorization remains statistical bias detection and a commit gate; existing latent-score/evaluator-deviation/co-evolution work covers the core.", "next_action": "Reopen only with an explicit residual-corrected evaluator or policy-training rule."},
    {"rank": 9, "idea_id": "asset-level-model-swap-certificate", "offline": "pass", "reality": "stop", "phenomenon": "not-run", "decision": "stop", "reason": "Asset failure after model swaps is real, but a universal compatibility certificate remains an audit layer while asset-specialist migration work covers the central mechanism.", "next_action": "Reopen only after narrowing to one asset class and learning an actual migration operator."},
    {"rank": 10, "idea_id": "counterfactual-evolution-decision-controller", "offline": "hold", "reality": "pass", "phenomenon": "hold", "decision": "hold", "reason": "Same-state four-action replay is useful, but the prior A-2 substrate exposed no-label-variation; action support and target variation must be demonstrated first.", "next_action": "Construct the four-action support table first; require action/optimal-decision target entropy >= 0.6 bits before GPU use."}
)

def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _qualification_state(experiment_root: Path) -> dict[str, Any]:
    canonical_path = experiment_root / "pre-experiment-qualification-qwen25-react-family-ood134.json"
    canonical = _read_json(canonical_path)
    run_id = "p0-mem-xfer-qwen-qualification"
    run_dir = experiment_root / "qualification" / run_id
    attempted = _read_json(run_dir / "summary.json")
    if canonical and bool((canonical.get("gate") or {}).get("passed")):
        gate = canonical.get("gate") or {}
        blocked_attempt = None
        if attempted and not bool((attempted.get("gate") or {}).get("passed")):
            blocked_attempt = {
                "run_id": run_id,
                "status": "runtime-model-selection-blocker",
                "model_path": attempted.get("model_path"),
                "successes": int(attempted.get("successes") or 0),
                "total": int(attempted.get("num_envs") or 0),
                "success_rate": float(attempted.get("success_rate") or 0.0),
                "scientific_result_available": False,
                "reason": "This calibration used a different local model path from the previously qualified Qwen2.5-7B-Instruct substrate; it is operational evidence only and cannot update the method belief.",
            }
        return {
            "run_id": str(canonical.get("evidence_id") or "qwen25-react-family-ood134"),
            "status": "pass",
            "stage": str(gate.get("stage") or "full-qualification"),
            "model_path": canonical.get("model_path"),
            "completed": int(canonical.get("num_envs") or 0),
            "total": int(canonical.get("num_envs") or 0),
            "successes": int(canonical.get("successes") or 0),
            "success_rate": float(canonical.get("success_rate") or 0.0),
            "task_types_with_success": int(canonical.get("task_types_with_success") or 0),
            "model_calls": int((canonical.get("usage") or {}).get("generation_calls") or 0),
            "gate": gate,
            "evidence_path": str(canonical_path),
            "blocked_attempt": blocked_attempt,
        }
    summary = attempted
    progress = _read_json(run_dir / "progress.json")
    if summary:
        gate = summary.get("gate") or {}
        return {
            "run_id": run_id,
            "status": "pass" if gate.get("passed") is True else "revise-base-agent",
            "stage": str(gate.get("stage") or "qualification"),
            "model_path": summary.get("model_path"),
            "completed": int(summary.get("num_envs") or 0),
            "total": int(summary.get("global_num_envs") or summary.get("num_envs") or 0),
            "successes": int(summary.get("successes") or 0),
            "success_rate": float(summary.get("success_rate") or 0.0),
            "task_types_with_success": int(summary.get("task_types_with_success") or 0),
            "model_calls": int((summary.get("usage") or {}).get("generation_calls") or 0),
            "gate": gate,
            "output_dir": str(run_dir),
        }
    if progress:
        return {
            "run_id": run_id,
            "status": str(progress.get("status") or "running"),
            "stage": "calibration",
            "completed": int(progress.get("completed") or 0),
            "total": int(progress.get("global_total") or progress.get("total") or 0),
            "successes": int(progress.get("success") or 0),
            "success_rate": float(progress.get("success_rate") or 0.0),
            "task_types_with_success": None,
            "model_calls": int(progress.get("model_calls") or 0),
            "gate": None,
            "output_dir": str(run_dir),
        }
    return {
        "run_id": run_id, "status": "planned", "stage": "calibration",
        "completed": 0, "total": 24, "successes": 0, "success_rate": 0.0,
        "task_types_with_success": None, "model_calls": 0, "gate": None,
        "output_dir": str(run_dir),
    }

def build_pre_gpu_candidate_gate_state() -> dict[str, Any]:
    storage = StorageSettings.from_env()
    experiment_root = resolve_experiment_data_root(storage)
    candidates = [dict(row) for row in GATE_ROWS]
    small_p0 = [row for row in candidates if row["decision"] == "small-p0"]
    qualification = _qualification_state(experiment_root)
    status = "qualification-pass" if qualification["status"] == "pass" else (
        "qualification-running" if qualification["status"] == "running" else qualification["status"]
    )
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "policy": {
            "gate_order": ["offline", "reality", "phenomenon"],
            "gpu_only_after_all_required_gates_pass": True,
            "hold_or_inconclusive_is_not_method_failure": True,
            "stop_before_gpu_when_current_thesis_is_collided_or_reducible": True,
            "screening_does_not_update_negative_scientific_belief": True,
            "parameter_provenance_required": True,
            "shared_rollouts_preferred_when_identical_truth_is_reused": True,
        },
        "summary": {
            "total": len(candidates),
            "small_p0": len(small_p0),
            "hold": sum(row["decision"] == "hold" for row in candidates),
            "stop": sum(row["decision"] == "stop" for row in candidates),
            "secondary": sum(row["decision"] == "secondary" for row in candidates),
        },
        "candidates": candidates,
        "small_p0_candidates": [row["idea_id"] for row in small_p0],
        "shared_p0": {
            "id": "P0-MEM-XFER-CAUSAL",
            "status": status,
            "ideas": ["replicated-effect-memory-gate", "cross-task-effect-transport-certificate"],
            "secondary_analysis": ["future-reuse-harm-predictor"],
            "core_unit": "same future task x same candidate memory x {retrieved, no-memory, token+position-matched irrelevant-memory placebo}",
            "target_design": {
                "task_families": 4,
                "future_tasks_per_family": 8,
                "arms": 3,
                "frozen_open_models": 2,
                "nominal_core_executions": 192,
            },
            "staging_rule": "Clear competence qualification first, then launch only on actually available public assets; never fabricate unavailable suites.",
            "p0_3_metrics": ["future-harm-rate", "net-utility", "selective-coverage", "calibration", "placebo-incremental-value"],
            "p0_5_metrics": ["effect-sign-error", "selective-coverage", "calibration", "negative-transfer", "net-utility"],
            "p0_5_baselines": ["semantic-similarity", "cross-fitted-treatment-effect-estimator"],
            "deployment_target_labels": 0,
            "qualification": qualification,
            "signal_stage": {
                "status": "complete",
                "decision": "signal-pass",
                "started_at": "2026-08-10T13:50:01Z",
                "finished_at": "2026-08-10T14:02:15Z",
                "server_id": "60",
                "gpu_uuid": "GPU-a7954f77-d6b5-8227-92ab-a757f1788ece",
                "model_path": "/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct",
                "qualification_source": "qwen25-react-family-ood134-s1",
                "run_id": "p0-mem-xfer-causal-signal-qwen-s1",
                "output_dir": "/home/hdd/yutong/agent-evolution-p0-data/runs/p0-mem-xfer-causal-signal-qwen-s1",
                "planned_executions": 24,
                "completed_executions": 24,
                "complete_units": 8,
                "outcome_disagreement_units": 2,
                "retrieved_harm_units": 1,
                "retrieved_benefit_units": 1,
                "placebo_nonzero_units": 1,
                "mean_retrieved_effect_vs_no_memory": 0.0,
                "mean_placebo_effect_vs_no_memory": 0.125,
                "mean_controlled_effect_vs_placebo": -0.125,
                "gpu_hours": 0.20073703511695687,
                "model_calls": 823,
                "tokens": 764363,
                "method_failure_authorized": False,
                "scientific_authority": "Development/sensitivity evidence only. Passing means the manipulation exposes arm-dependent outcomes; it is not evidence that either #3 or #5 already beats a baseline.",
            },
            "full_qwen_stage": {
                "status": "running",
                "started_at": "2026-08-10T14:06:51Z",
                "server_id": "60",
                "gpu_uuid": "GPU-814cd021-31d8-2c6f-76a5-b8d4739b34d1",
                "model_path": "/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct",
                "run_id": "p0-mem-xfer-causal-full-qwen-v1-r1",
                "output_dir": "/home/hdd/yutong/agent-evolution-p0-data/runs/p0-mem-xfer-causal-full-qwen-v1-r1",
                "target_selection": "Outcome-independent frozen hash over OOD tasks; all signal tasks and source-memory tasks excluded.",
                "task_families": 4,
                "future_tasks_per_family": 8,
                "units": 32,
                "planned_executions": 96,
                "method_failure_authorized": False,
                "prior_runtime_attempt": {
                    "run_id": "p0-mem-xfer-causal-full-qwen-v1",
                    "status": "runtime-error-before-first-episode",
                    "scientific_result_available": False,
                    "reason": "A signal-only qualification_baseline_success field was treated as required in the outcome-independent full plan; repaired without changing the frozen units/arm order.",
                    "frozen_plan_hash": "2e99261fcfe8a7b44fc53a95ad6788e9a4d8a558e2c40ba8592928f1014ea2c6",
                },
            },
            "next_gate": "Collect the 96-execution outcome-independent Qwen treatment table. Then run frozen offline #3 replicated-effect admission and #5 leave-one-family-out transport analyses on exactly that table before opening a second-model GPU run.",
        }
    }


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _jsonl_write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def _jsonl_read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _scoped_conditional(patch: str) -> bool:
    text = str(patch or "").strip().lower()
    return (text.startswith("if ") or text.startswith("when ")) and "then" in text


def audit_a1_updater(
    rows: Iterable[dict[str, Any]],
    *,
    minimum_positive: int = 8,
    minimum_fraction: float = 0.4,
    minimum_scoped_fraction: float = 0.8,
) -> dict[str, Any]:
    records = list(rows)
    positive = [row for row in records if float(row.get("current_task_gain") or 0.0) > 0.0]
    scoped = sum(_scoped_conditional(str(row.get("patch") or "")) for row in records)
    total = len(records)
    metrics = {
        "candidate_count": total,
        "positive_target_gain_candidates": len(positive),
        "effective_candidate_fraction": len(positive) / total if total else 0.0,
        "scoped_conditional_candidates": scoped,
        "scoped_conditional_fraction": scoped / total if total else 0.0,
    }
    blockers: list[str] = []
    if metrics["positive_target_gain_candidates"] < minimum_positive:
        blockers.append("positive-target-gain-candidates-below-minimum")
    if metrics["effective_candidate_fraction"] < minimum_fraction:
        blockers.append("effective-candidate-fraction-below-minimum")
    if metrics["scoped_conditional_fraction"] < minimum_scoped_fraction:
        blockers.append("scoped-conditional-fraction-below-minimum")
    return {
        "schema_version": "1.0",
        "artifact_kind": "updater-competence-audit",
        "idea_id": "update-trust-region",
        "metrics": metrics,
        "thresholds": {
            "positive_target_gain_candidates": minimum_positive,
            "effective_candidate_fraction": minimum_fraction,
            "scoped_conditional_fraction": minimum_scoped_fraction,
        },
        "gate": {"passed": not blockers, "blockers": blockers},
        "scientific_role": "hard precondition only; failure blocks downstream regression-gate learning and is not a failure of update governance",
    }


def _future_benefit_after_first(rounds: list[dict[str, Any]]) -> bool:
    if len(rounds) < 2:
        return False
    first_success = float(rounds[0].get("success") or 0.0)
    first_regression = float(rounds[0].get("regression") or 0.0)
    for row in rounds[1:]:
        success = float(row.get("success") or 0.0)
        regression = float(row.get("regression") or 0.0)
        if success > first_success or (success >= first_success and regression < first_regression):
            return True
    return False


def audit_a2_updater(
    sequences: Iterable[dict[str, Any]],
    *,
    minimum_positive_sequences: int = 4,
    minimum_nonpositive_sequences: int = 4,
    minimum_nonzero_fraction: float = 0.25,
) -> dict[str, Any]:
    records = list(sequences)
    positives = sum(_future_benefit_after_first(list(item.get("rounds") or [])) for item in records)
    nonpositives = len(records) - positives
    rounds = [row for item in records for row in list(item.get("rounds") or [])]
    nonzero = sum(abs(float(row.get("marginal_gain") or 0.0)) > 1e-12 for row in rounds)
    metrics = {
        "sequence_count": len(records),
        "future_benefit_positive_sequences": positives,
        "future_benefit_nonpositive_sequences": nonpositives,
        "update_rounds": len(rounds),
        "nonzero_target_effect_rounds": nonzero,
        "nonzero_update_effect_fraction": nonzero / len(rounds) if rounds else 0.0,
    }
    blockers: list[str] = []
    if positives < minimum_positive_sequences:
        blockers.append("future-benefit-positive-sequences-below-minimum")
    if nonpositives < minimum_nonpositive_sequences:
        blockers.append("future-benefit-nonpositive-sequences-below-minimum")
    if metrics["nonzero_update_effect_fraction"] < minimum_nonzero_fraction:
        blockers.append("nonzero-update-effect-fraction-below-minimum")
    return {
        "schema_version": "1.0",
        "artifact_kind": "updater-competence-audit",
        "idea_id": "budgeted-evolution-controller",
        "metrics": metrics,
        "thresholds": {
            "future_benefit_positive_sequences": minimum_positive_sequences,
            "future_benefit_nonpositive_sequences": minimum_nonpositive_sequences,
            "nonzero_update_effect_fraction": minimum_nonzero_fraction,
        },
        "gate": {"passed": not blockers, "blockers": blockers},
        "scientific_role": "hard precondition only; failure means the update action stream is too degenerate to identify a stopping controller",
    }


def qualify_a1_updater(
    experiment_config: Path,
    alfworld_config: Path,
    model_path: Path,
    output_dir: Path,
    *,
    candidate_target: int = 16,
) -> dict[str, Any]:
    experiment = load_json(experiment_config)
    if str(experiment.get("idea_id") or "") != "update-trust-region":
        raise ValueError("A-1 updater qualification requires update-trust-region config")
    world = load_config(alfworld_config)
    world.setdefault("general", {})["save_path"] = str(output_dir / "alfworld-runtime")
    scope = experiment.get("scope") or {}
    seed = int((experiment.get("seeds") or [42])[0])
    max_steps = int(scope.get("max_steps", 50))
    failure_target = int(scope.get("discovery_failures_target", 16))
    discovery_cap = int(scope.get("discovery_episode_cap", max(24, failure_target)))
    split = str((scope.get("splits") or {}).get("discovery") or "train")
    policy_mode = str(scope.get("policy_mode") or "react-family")
    contract = (experiment.get("pre_experiment") or {}).get("updater_competence") or {}
    thresholds = {str(row.get("metric")): row for row in contract.get("metrics") or [] if isinstance(row, dict)}
    minimum_positive = int((thresholds.get("positive_target_gain_candidates") or {}).get("minimum", 8))
    minimum_fraction = float((thresholds.get("effective_candidate_fraction") or {}).get("minimum", 0.4))
    minimum_scoped = float((thresholds.get("scoped_conditional_fraction") or {}).get("minimum", 0.8))
    if candidate_target < minimum_positive:
        raise ValueError("candidate_target is below the preregistered minimum-positive count")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite non-empty qualification directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    policy = HFAdmissiblePolicy(model_path, policy_mode=policy_mode)
    runner = ALFWorldGameRunner(world)
    started = time.time()
    discovery_files = _task_family_order(runner.available_game_files(split), seed, "a1-updater-qualification-discovery")
    discovery_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for game_file in discovery_files[:discovery_cap]:
        trace = runner.run_game_file(split, game_file, policy, max_steps=max_steps)
        discovery_rows.append(trace)
        if not trace["success"]:
            failures.append(trace)
        if len(failures) >= failure_target:
            break
    if len(failures) < failure_target:
        raise RuntimeError(f"only {len(failures)} failures found; need {failure_target}")

    candidates, patch_generation_calls = generate_a1_candidates(policy, failures, [candidate_target, candidate_target], seed)
    failure_by_id = {str(trace["task_id"]): trace for trace in failures}
    evaluation_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        source_id = str(candidate["source_task_id"])
        before = failure_by_id[source_id]
        after = runner.run_game_file(split, source_id, policy, str(candidate["patch"]), max_steps=max_steps)
        evaluation_rows.append({
            "candidate_id": str(candidate["candidate_id"]),
            "source_task_id": source_id,
            "source_task_family": str(before.get("task_family") or ""),
            "patch": str(candidate["patch"]),
            "edit_size": float(candidate["edit_size"]),
            "current_task_gain": float(after["success"]) - float(before["success"]),
            "source_before_success": float(before["success"]),
            "source_after_success": float(after["success"]),
            "hidden_before": [],
            "hidden_after": [],
        })

    evidence = audit_a1_updater(
        evaluation_rows,
        minimum_positive=minimum_positive,
        minimum_fraction=minimum_fraction,
        minimum_scoped_fraction=minimum_scoped,
    )
    usage = policy.usage_snapshot()
    evidence.update({
        "evidence_id": str(contract.get("evidence_id") or "a1-localized-updater-qualification-v1"),
        "candidate_generation_target": candidate_target,
        "discovery_failure_target": failure_target,
        "discovery_episodes": len(discovery_rows),
        "source_replay_episodes": len(evaluation_rows),
        "environment_episodes": len(discovery_rows) + len(evaluation_rows),
        "patch_generation_calls": patch_generation_calls,
        "model_calls": int(usage["generation_calls"]),
        "tokens": int(usage["tokens"]),
        "elapsed_hours": round((time.time() - started) / 3600.0, 6),
        "hidden_or_probe_execution_count": 0,
        "qualification_contract": "Only discovery failures and source-task replays are visible; probe and hidden tasks are structurally unavailable.",
    })
    _jsonl_write(output_dir / "discovery-traces.jsonl", discovery_rows)
    _jsonl_write(output_dir / "candidate-patches.jsonl", candidates)
    _jsonl_write(output_dir / "source-evaluation.jsonl", evaluation_rows)
    _atomic_json(output_dir / "evidence.json", evidence)
    return evidence


def smoke_a1_updater(experiment_config: Path, alfworld_config: Path, model_path: Path) -> dict[str, Any]:
    experiment = load_json(experiment_config)
    world = load_config(alfworld_config)
    scope = experiment.get("scope") or {}
    seed = int((experiment.get("seeds") or [42])[0])
    max_steps = int(scope.get("max_steps", 50))
    split = str((scope.get("splits") or {}).get("discovery") or "train")
    policy = HFAdmissiblePolicy(model_path, policy_mode=str(scope.get("policy_mode") or "react-family"))
    runner = ALFWorldGameRunner(world)
    files = _task_family_order(runner.available_game_files(split), seed, "a1-updater-smoke")
    before = None
    discovery_episodes = 0
    for game_file in files[:8]:
        trace = runner.run_game_file(split, game_file, policy, max_steps=max_steps)
        discovery_episodes += 1
        if not trace["success"]:
            before = trace
            break
    if before is None:
        raise RuntimeError("smoke found no baseline failure in first eight deterministic discovery tasks")
    candidates, patch_calls = generate_a1_candidates(policy, [before], [1, 1], seed)
    candidate = candidates[0]
    after = runner.run_game_file(split, str(before["task_id"]), policy, str(candidate["patch"]), max_steps=max_steps)
    patch = str(candidate["patch"])
    return {
        "schema_version": "1.0",
        "artifact_kind": "a1-updater-source-only-smoke",
        "source_task_id": str(before["task_id"]),
        "source_task_family": str(before.get("task_family") or ""),
        "patch": patch,
        "scoped_conditional": _scoped_conditional(patch),
        "before_success": float(before["success"]),
        "after_success": float(after["success"]),
        "current_task_gain": float(after["success"]) - float(before["success"]),
        "discovery_episodes": discovery_episodes,
        "source_replay_episodes": 1,
        "patch_generation_calls": patch_calls,
        "hidden_or_probe_execution_count": 0,
        "usage": policy.usage_snapshot(),
    }


def _updater_evidence_path(data_root: Path, evidence_id: str) -> Path:
    return data_root / "pre-experiment" / "evidence" / "updater-competence" / f"{evidence_id}.json"


def _parse_updater_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-GPU candidate gates and updater competence qualification.")
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke-a1-updater")
    smoke.add_argument("--config", type=Path, required=True)
    smoke.add_argument("--alfworld-config", type=Path, required=True)
    smoke.add_argument("--model-path", type=Path, required=True)
    smoke.add_argument("--output", type=Path)
    a1 = sub.add_parser("qualify-a1-updater")
    a1.add_argument("--config", type=Path, required=True)
    a1.add_argument("--alfworld-config", type=Path, required=True)
    a1.add_argument("--model-path", type=Path, required=True)
    a1.add_argument("--output-dir", type=Path, required=True)
    a1.add_argument("--candidate-target", type=int, default=16)
    a1.add_argument("--data-root", type=Path, required=True)
    a2 = sub.add_parser("audit-a2-updater")
    a2.add_argument("--fixed-sequences", type=Path, required=True)
    a2.add_argument("--data-root", type=Path, required=True)
    a2.add_argument("--evidence-id", default="a2-update-sequence-support-v1")
    return parser.parse_args()


def _updater_main() -> None:
    args = _parse_updater_args()
    if args.command == "smoke-a1-updater":
        try:
            evidence = smoke_a1_updater(args.config, args.alfworld_config, args.model_path)
        except Exception as error:
            evidence = {
                "schema_version": "1.0",
                "artifact_kind": "a1-updater-source-only-smoke",
                "status": "error",
                "error_type": type(error).__name__,
                "message": str(error),
                "hidden_or_probe_execution_count": 0,
            }
            if args.output is not None:
                _atomic_json(args.output, evidence)
            print(json.dumps(evidence, ensure_ascii=False, indent=2))
            raise
        if args.output is not None:
            _atomic_json(args.output, evidence)
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        return
    if args.command == "qualify-a1-updater":
        evidence = qualify_a1_updater(args.config, args.alfworld_config, args.model_path, args.output_dir, candidate_target=args.candidate_target)
        target = _updater_evidence_path(args.data_root, str(evidence["evidence_id"]))
    else:
        evidence = audit_a2_updater(_jsonl_read(args.fixed_sequences))
        evidence["evidence_id"] = args.evidence_id
        target = _updater_evidence_path(args.data_root, args.evidence_id)
    _atomic_json(target, evidence)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if evidence["gate"]["passed"] is not True:
        raise SystemExit(3)


# Shared P0-MEM-XFER-CAUSAL signal runner. This is intentionally kept in the
# gate module so the pre-GPU decision, frozen manipulation, and typed outcome
# semantics cannot drift apart before the first confirmatory table exists.
MEM_XFER_SOURCE_FAMILIES = (
    "look_at_obj_in_light",
    "pick_and_place_simple",
    "pick_clean_then_place_in_recep",
    "pick_cool_then_place_in_recep",
)
MEM_XFER_TARGET_FAMILIES = (
    "pick_and_place_simple",
    "pick_clean_then_place_in_recep",
)
MEM_XFER_ARMS = ("retrieved", "no-memory", "placebo")
MEM_XFER_PLACEBO_TEXT = (
    "Prior experience: compare calendar entries, copy the later date into a note, verify each month name, "
    "sort the notes alphabetically, and record the final date in a table. Repeat the check before finishing. "
)


def _hash_order(seed: int, *parts: object) -> str:
    return hashlib.sha256("|".join([str(seed), *map(str, parts)]).encode("utf-8")).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            trace = payload.get("trace") if isinstance(payload, dict) else None
            if isinstance(trace, dict):
                row = dict(trace)
                row.setdefault("qualification_index", payload.get("global_index", payload.get("index")))
                row.setdefault("task_family", payload.get("family"))
                rows.append(row)
            else:
                rows.append(payload)
    return rows


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def _trace_task(row: dict[str, Any]) -> str:
    return str(row.get("task_id") or row.get("gamefile") or "")


def _trace_family(row: dict[str, Any]) -> str:
    return str(row.get("task_family") or task_family_from_gamefile(_trace_task(row)))


def _compact_action(action: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\b\d+\b", "", str(action))).strip()


def _memory_from_success(row: dict[str, Any], memory_id: str) -> str:
    actions = [_compact_action(action) for action in list(row.get("actions") or [])]
    compact: list[str] = []
    for action in actions:
        if action and (not compact or action != compact[-1]):
            compact.append(action)
    if len(compact) > 16:
        compact = compact[:8] + compact[-8:]
    steps = "\n".join(f"{index + 1}. {action}" for index, action in enumerate(compact))
    return (
        f"Experience {memory_id}. Goal pattern: {_trace_family(row)}.\n"
        "A previous successful episode used this procedure:\n"
        f"{steps or '1. Track the goal and choose only admissible actions.'}\n"
        "Use it only when it fits the current goal and state."
    )


def build_mem_xfer_signal_plan(
    qualification_traces: Path,
    *,
    seed: int = 42,
    target_tasks_per_family: int = 4,
) -> dict[str, Any]:
    rows = _load_jsonl(qualification_traces)
    successes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        family = _trace_family(row)
        all_by_family[family].append(row)
        if int(row.get("success") or row.get("won") or 0) == 1:
            successes[family].append(row)
    memories: list[dict[str, Any]] = []
    source_tasks: set[str] = set()
    for family in MEM_XFER_SOURCE_FAMILIES:
        candidates = sorted(successes.get(family, []), key=lambda row: _hash_order(seed, "memory", family, _trace_task(row)))
        if not candidates:
            raise RuntimeError(f"no successful qualification trace available for source family {family}")
        source = candidates[0]
        memory_id = f"m-{family}-1"
        source_tasks.add(_trace_task(source))
        memories.append({
            "memory_id": memory_id,
            "source_family": family,
            "source_task_id": _trace_task(source),
            "text": _memory_from_success(source, memory_id),
        })
    future: dict[str, list[str]] = {}
    baseline_outcomes: dict[str, int] = {}
    for family in MEM_XFER_TARGET_FAMILIES:
        eligible = [row for row in all_by_family.get(family, []) if _trace_task(row) not in source_tasks]
        positives = sorted([row for row in eligible if int(row.get("success") or row.get("won") or 0) == 1], key=lambda row: _hash_order(seed, "target-positive", family, _trace_task(row)))
        negatives = sorted([row for row in eligible if int(row.get("success") or row.get("won") or 0) == 0], key=lambda row: _hash_order(seed, "target-negative", family, _trace_task(row)))
        positive_n = min(len(positives), max(1, target_tasks_per_family // 2))
        chosen = positives[:positive_n] + negatives[: max(0, target_tasks_per_family - positive_n)]
        if len(chosen) < target_tasks_per_family:
            used = {_trace_task(row) for row in chosen}
            remainder = sorted([row for row in eligible if _trace_task(row) not in used], key=lambda row: _hash_order(seed, "target-fill", family, _trace_task(row)))
            chosen.extend(remainder[: target_tasks_per_family - len(chosen)])
        if len(chosen) < target_tasks_per_family:
            raise RuntimeError(f"not enough frozen qualification tasks for target family {family}")
        future[family] = [_trace_task(row) for row in chosen[:target_tasks_per_family]]
        baseline_outcomes.update({_trace_task(row): int(row.get("success") or row.get("won") or 0) for row in chosen[:target_tasks_per_family]})
    memory_by_family = {str(row["source_family"]): row for row in memories}
    units: list[dict[str, Any]] = []
    for target_index, family in enumerate(MEM_XFER_TARGET_FAMILIES):
        for task_index, task_id in enumerate(future[family]):
            source_family = MEM_XFER_SOURCE_FAMILIES[(task_index + target_index) % len(MEM_XFER_SOURCE_FAMILIES)]
            memory = memory_by_family[source_family]
            arm_order = sorted(MEM_XFER_ARMS, key=lambda arm: _hash_order(seed, "arm", task_id, memory["memory_id"], arm))
            units.append({
                "unit_id": f"signal-{family}-{task_index + 1:02d}",
                "target_family": family,
                "target_task_id": task_id,
                "qualification_baseline_success": baseline_outcomes[task_id],
                "source_family": source_family,
                "memory_id": memory["memory_id"],
                "arm_order": arm_order,
            })
    return {
        "schema_version": "1.0",
        "experiment_id": "P0-MEM-XFER-CAUSAL",
        "stage": "signal",
        "created_at": _now(),
        "seed": seed,
        "split": "eval_out_of_distribution",
        "source_families": list(MEM_XFER_SOURCE_FAMILIES),
        "target_families": list(MEM_XFER_TARGET_FAMILIES),
        "target_tasks_per_family": target_tasks_per_family,
        "source_memories": memories,
        "units": units,
        "arms": list(MEM_XFER_ARMS),
        "core_executions": len(units) * len(MEM_XFER_ARMS),
        "qualification_traces": str(qualification_traces),
        "screening_selection": "Outcome-balanced source qualification tasks are used only for this small manipulation/sensitivity screen; confirmatory target tasks must be reselected without outcome conditioning and must exclude these signal tasks.",
        "independent_truth": "ALFWorld environment success/won; no LLM judge supplies outcome truth.",
        "placebo_contract": "Same system-prompt position; unrelated calendar-note content; tokenizer length must match retrieved memory within one token.",
        "typed_outcome": "No-signal, budget-stop, runtime error, or baseline-floor are INCONCLUSIVE/development outcomes and cannot emit METHOD-FAIL.",
    }


def _token_matched_placebo(policy: HFAdmissiblePolicy, memory: str) -> tuple[str, int, int]:
    target = policy.token_count(memory)
    corpus = MEM_XFER_PLACEBO_TEXT
    while len(policy.tokenizer.encode(corpus, add_special_tokens=False)) < target + 12:
        corpus += MEM_XFER_PLACEBO_TEXT
    token_ids = policy.tokenizer.encode(corpus, add_special_tokens=False)
    best = ("", 0, 10**9)
    for length in range(max(1, target - 8), min(len(token_ids), target + 8) + 1):
        text = policy.tokenizer.decode(token_ids[:length], skip_special_tokens=True).strip()
        count = policy.token_count(text)
        gap = abs(count - target)
        if gap < best[2]:
            best = (text, count, gap)
        if gap == 0:
            break
    if best[2] > 1:
        raise RuntimeError(f"token-matched placebo unavailable: memory={target}, placebo={best[1]}")
    return best[0], target, best[1]


def _usage_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {key: int(after.get(key, 0)) - int(before.get(key, 0)) for key in set(before) | set(after)}


def analyze_mem_xfer_signal(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[str(row["unit_id"])][str(row["arm"])] = row
    units: list[dict[str, Any]] = []
    pair_effects: dict[str, list[float]] = defaultdict(list)
    for unit_id, arms in sorted(grouped.items()):
        if not all(arm in arms for arm in MEM_XFER_ARMS):
            continue
        retrieved = int(arms["retrieved"]["success"])
        baseline = int(arms["no-memory"]["success"])
        placebo = int(arms["placebo"]["success"])
        base = arms["retrieved"]
        controlled = retrieved - placebo
        row = {
            "unit_id": unit_id,
            "source_family": base["source_family"],
            "target_family": base["target_family"],
            "memory_id": base["memory_id"],
            "retrieved_success": retrieved,
            "no_memory_success": baseline,
            "placebo_success": placebo,
            "retrieved_delta": retrieved - baseline,
            "placebo_delta": placebo - baseline,
            "controlled_delta": controlled,
            "outcome_disagreement": len({retrieved, baseline, placebo}) > 1,
        }
        units.append(row)
        pair_effects[f"{row['source_family']}->{row['target_family']}"] .append(float(controlled))
    disagreements = sum(bool(row["outcome_disagreement"]) for row in units)
    if disagreements >= 2:
        decision = "signal-pass"
        next_action = "Open the frozen full Qwen treatment table with outcome-independent target selection; exclude all signal tasks."
    elif disagreements == 1:
        decision = "borderline-extend-signal"
        next_action = "Run one additional preregistered signal block before spending the full P0 budget."
    else:
        decision = "inconclusive-no-outcome-disagreement"
        next_action = "Do not call either idea failed; repair the memory manipulation or task sensitivity before more GPU use."
    mean = lambda values: sum(values) / len(values) if values else 0.0
    return {
        "schema_version": "1.0",
        "experiment_id": "P0-MEM-XFER-CAUSAL",
        "stage": "signal",
        "complete_units": len(units),
        "outcome_disagreement_units": disagreements,
        "retrieved_harm_units": sum(row["retrieved_delta"] < 0 for row in units),
        "retrieved_benefit_units": sum(row["retrieved_delta"] > 0 for row in units),
        "placebo_nonzero_units": sum(row["placebo_delta"] != 0 for row in units),
        "mean_retrieved_effect_vs_no_memory": mean([float(row["retrieved_delta"]) for row in units]),
        "mean_placebo_effect_vs_no_memory": mean([float(row["placebo_delta"]) for row in units]),
        "mean_controlled_effect_vs_placebo": mean([float(row["controlled_delta"]) for row in units]),
        "source_target_controlled_effects": {key: mean(values) for key, values in sorted(pair_effects.items())},
        "decision": decision,
        "next_action": next_action,
        "scientific_authority": "development/signal only; METHOD-FAIL forbidden",
        "unit_rows": units,
    }


def run_mem_xfer_signal(
    *,
    plan: dict[str, Any],
    alfworld_config: Path,
    model_path: Path,
    output_dir: Path,
    max_steps: int = 50,
    episode_cap: int = 24,
    wall_hours_cap: float = 4.0,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw-traces.jsonl"
    raw_path.write_text("", encoding="utf-8")
    _atomic_write_json(output_dir / "plan.json", plan)
    _write_jsonl(output_dir / "source-memories.jsonl", plan["source_memories"])
    _write_jsonl(output_dir / "treatment-plan.jsonl", plan["units"])
    _atomic_write_json(output_dir / "manifest.json", {
        "schema_version": "1.0",
        "experiment_id": "P0-MEM-XFER-CAUSAL",
        "stage": "signal",
        "model_path": str(model_path),
        "code_commit": git_head(),
        "max_steps": max_steps,
        "episode_cap": episode_cap,
        "wall_hours_cap": wall_hours_cap,
        "arms": list(MEM_XFER_ARMS),
        "independent_truth": plan["independent_truth"],
        "placebo_contract": plan["placebo_contract"],
        "screening_selection": plan["screening_selection"],
        "incremental_trace": True,
        "method_failure_authorized": False,
    })
    runner = ALFWorldGameRunner(load_config(alfworld_config))
    policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
    memory_map = {str(item["memory_id"]): item for item in plan["source_memories"]}
    placebo_cache: dict[str, tuple[str, int, int]] = {}
    rows: list[dict[str, Any]] = []
    started = time.monotonic()
    for unit_index, unit in enumerate(plan["units"], 1):
        memory = str(memory_map[str(unit["memory_id"])]["text"])
        if str(unit["memory_id"]) not in placebo_cache:
            placebo_cache[str(unit["memory_id"])] = _token_matched_placebo(policy, memory)
        placebo, memory_tokens, placebo_tokens = placebo_cache[str(unit["memory_id"])]
        for arm in unit["arm_order"]:
            elapsed = (time.monotonic() - started) / 3600.0
            if len(rows) >= episode_cap:
                raise RuntimeError(f"BUDGET_STOP episode cap reached: {len(rows)} >= {episode_cap}")
            if elapsed >= wall_hours_cap:
                raise RuntimeError(f"BUDGET_STOP wall cap reached: {elapsed:.4f} >= {wall_hours_cap}")
            context = "" if arm == "no-memory" else "MEMORY::" + (memory if arm == "retrieved" else placebo)
            before = policy.usage_snapshot()
            trace = runner.run_game_file(plan["split"], str(unit["target_task_id"]), policy, context, max_steps=max_steps)
            after = policy.usage_snapshot()
            record = {
                "schema_version": "1.0",
                "experiment_id": "P0-MEM-XFER-CAUSAL",
                "stage": "signal",
                "unit_id": unit["unit_id"],
                "unit_index": unit_index,
                "units_total": len(plan["units"]),
                "arm": arm,
                "target_family": unit["target_family"],
                "target_task_id": unit["target_task_id"],
                "qualification_baseline_success": unit["qualification_baseline_success"],
                "source_family": unit["source_family"],
                "memory_id": unit["memory_id"],
                "memory_token_count": memory_tokens,
                "placebo_token_count": placebo_tokens,
                "token_match_gap": abs(memory_tokens - placebo_tokens),
                "success": int(trace.get("success") or 0),
                "score": float(trace.get("score") or 0.0),
                "steps": int(trace.get("steps") or 0),
                "invalid_actions": int(trace.get("invalid_actions") or 0),
                "actions": trace.get("actions") or [],
                "usage": _usage_delta(before, after),
                "recorded_at": _now(),
            }
            rows.append(record)
            _append_jsonl(raw_path, record)
            _atomic_write_json(output_dir / "progress.json", {
                "schema_version": "1.0", "status": "running", "experiment_id": "P0-MEM-XFER-CAUSAL",
                "stage": "signal", "completed_episodes": len(rows), "episode_cap": episode_cap,
                "total_episodes": plan["core_executions"], "current_unit": unit["unit_id"], "current_arm": arm,
                "elapsed_hours": (time.monotonic() - started) / 3600.0,
                "model_calls": int(policy.usage_snapshot().get("generation_calls") or 0), "updated_at": _now(),
            })
    analysis = analyze_mem_xfer_signal(rows)
    elapsed = (time.monotonic() - started) / 3600.0
    usage = policy.usage_snapshot()
    cost = {
        "gpu_hours": elapsed, "wall_clock_hours": elapsed, "environment_episodes": len(rows),
        "model_calls": int(usage.get("generation_calls") or 0), "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0), "tokens": int(usage.get("tokens") or 0),
        "accounting_consistent": True,
    }
    _atomic_write_json(output_dir / "analysis.json", analysis)
    _atomic_write_json(output_dir / "cost.json", cost)
    _atomic_write_json(output_dir / "decision.json", {
        "experiment_id": "P0-MEM-XFER-CAUSAL", "stage": "signal", "decision": analysis["decision"],
        "next_action": analysis["next_action"], "method_failure_authorized": False, "created_at": _now(),
    })
    fields = ["unit_id", "source_family", "target_family", "memory_id", "retrieved_success", "no_memory_success", "placebo_success", "retrieved_delta", "placebo_delta", "controlled_delta", "outcome_disagreement"]
    with (output_dir / "main_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in analysis["unit_rows"]:
            writer.writerow({key: row.get(key) for key in fields})
    _atomic_write_json(output_dir / "progress.json", {
        "schema_version": "1.0", "status": "complete", "experiment_id": "P0-MEM-XFER-CAUSAL",
        "stage": "signal", "completed_episodes": len(rows), "total_episodes": plan["core_executions"],
        "completed_units": analysis["complete_units"], "total_units": len(plan["units"]), "elapsed_hours": elapsed,
        "model_calls": int(usage.get("generation_calls") or 0), "decision": analysis["decision"], "updated_at": _now(),
    })
    return {"analysis": analysis, "cost": cost}


def _mem_xfer_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-GPU survivor state and shared memory-transfer P0 signal runner.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("mem-xfer-plan", "mem-xfer-signal"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--qualification-traces", type=Path, required=True)
        cmd.add_argument("--output-dir", type=Path, required=True)
        cmd.add_argument("--seed", type=int, default=42)
        cmd.add_argument("--target-tasks-per-family", type=int, default=4)
    run = sub.choices["mem-xfer-signal"]
    run.add_argument("--alfworld-config", type=Path, required=True)
    run.add_argument("--model-path", type=Path, required=True)
    run.add_argument("--max-steps", type=int, default=50)
    run.add_argument("--episode-cap", type=int, default=24)
    run.add_argument("--wall-hours-cap", type=float, default=4.0)
    return parser.parse_args()


def main() -> None:
    args = _mem_xfer_cli()
    plan = build_mem_xfer_signal_plan(args.qualification_traces, seed=args.seed, target_tasks_per_family=args.target_tasks_per_family)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(args.output_dir / "plan.json", plan)
    _write_jsonl(args.output_dir / "source-memories.jsonl", plan["source_memories"])
    _write_jsonl(args.output_dir / "treatment-plan.jsonl", plan["units"])
    if args.command == "mem-xfer-plan":
        print(json.dumps({"experiment_id": plan["experiment_id"], "stage": "signal", "units": len(plan["units"]), "core_executions": plan["core_executions"], "target_families": plan["target_families"], "output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))
        return
    try:
        result = run_mem_xfer_signal(plan=plan, alfworld_config=args.alfworld_config, model_path=args.model_path, output_dir=args.output_dir, max_steps=args.max_steps, episode_cap=args.episode_cap, wall_hours_cap=args.wall_hours_cap)
    except Exception as error:
        _atomic_write_json(args.output_dir / "runtime-error.json", {"schema_version": "1.0", "experiment_id": "P0-MEM-XFER-CAUSAL", "stage": "signal", "error_type": type(error).__name__, "message": str(error), "scientific_result_available": False, "recorded_at": _now()})
        progress = _read_json(args.output_dir / "progress.json") or {}
        _atomic_write_json(args.output_dir / "progress.json", {**progress, "status": "budget-stop" if str(error).startswith("BUDGET_STOP") else "runtime-error", "scientific_result_available": False, "error": str(error), "updated_at": _now()})
        raise
    print(json.dumps({"analysis": result["analysis"], "cost": result["cost"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"smoke-a1-updater", "qualify-a1-updater", "audit-a2-updater"}:
        _updater_main()
    else:
        main()

