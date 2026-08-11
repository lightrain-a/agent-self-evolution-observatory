from __future__ import annotations

import csv
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_mem_xfer_support_enriched import (
    ARMS, EXPERIMENT_ID, SupportP0Error, _append_jsonl, _atomic_json,
    _exclusive_run_lock, _file_hash, _load_json, _load_jsonl, _now,
    _token_matched_placebo, _usage_delta, _verified_material,
)

FULL_STAGE = "full-qwen-support-table"
FULL_SUPPORT_GATES = {
    "minimum_candidates": 8,
    "minimum_replicated_harm_candidates": 2,
    "minimum_replicated_benefit_candidates": 2,
    "candidate_level_independent_future_evaluation_required": True,
    "minimum_nonzero_controlled_effects": 12,
    "minimum_target_family_folds_with_two_nonzero": 3,
}


def _effect_sign(values: list[int]) -> int:
    total = sum(values)
    return 1 if total > 0 else (-1 if total < 0 else 0)


def _support_source_rows(run_dir: Path, plan: dict[str, Any], model_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    support_dir = run_dir / "support-qualification"
    decision = _load_json(support_dir / "decision.json")
    manifest = _load_json(support_dir / "manifest.json")
    if decision.get("decision") != "SUPPORT_QUALIFICATION_PASS":
        raise SupportP0Error("full stage requires SUPPORT_QUALIFICATION_PASS")
    if str(manifest.get("plan_hash") or "") != str(plan.get("plan_hash") or ""):
        raise SupportP0Error("support/full plan hash mismatch")
    if str(manifest.get("model_path") or "") != str(model_path):
        raise SupportP0Error("support/full model path mismatch")
    rows = _load_jsonl(support_dir / "raw-traces.jsonl")
    material = _verified_material(plan)
    support_ids = set(material["support_qualification_unit_ids"])
    expected = {(str(unit_id), arm) for unit_id in support_ids for arm in ARMS}
    actual = {(str(row.get("unit_id") or ""), str(row.get("arm") or "")) for row in rows}
    if len(rows) != 72 or len(actual) != 72 or actual != expected:
        raise SupportP0Error(f"support source integrity failed: rows={len(rows)}, unique={len(actual)}")
    if any(abs(int(row.get("token_match_gap") or 0)) > 1 for row in rows):
        raise SupportP0Error("support source contains placebo token mismatch")
    return rows, {
        "support_decision_sha256": _file_hash(support_dir / "decision.json"),
        "support_raw_sha256": _file_hash(support_dir / "raw-traces.jsonl"),
        "support_cost_sha256": _file_hash(support_dir / "cost.json"),
        "reused_support_executions": 72,
        "reused_support_units": 24,
    }


def analyze_full_support_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[str(row["unit_id"])][str(row["arm"])] = row
    units: list[dict[str, Any]] = []
    for unit_id, arms in sorted(grouped.items()):
        if not all(arm in arms for arm in ARMS):
            continue
        r = int(arms["retrieved"]["success"])
        n = int(arms["no-memory"]["success"])
        p = int(arms["placebo"]["success"])
        base = arms["retrieved"]
        units.append({
            "unit_id": unit_id, "memory_id": base["memory_id"],
            "source_family": base["source_family"], "target_family": base["target_family"],
            "target_task_id": base["target_task_id"], "candidate_index": int(base["candidate_index"]),
            "candidate_role": base["candidate_role"], "evaluation_role": base["evaluation_role"],
            "retrieved_success": r, "no_memory_success": n, "placebo_success": p,
            "retrieved_delta": r - n, "placebo_delta": p - n,
            "controlled_delta": r - p, "outcome_disagreement": len({r, n, p}) > 1,
        })
    if len(units) != 72:
        raise SupportP0Error(f"full support analysis requires 72 complete units; found {len(units)}")

    by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in units:
        by_candidate[str(row["memory_id"])].append(row)
    candidates: list[dict[str, Any]] = []
    for memory_id, items in sorted(by_candidate.items()):
        probe = [row for row in items if row["evaluation_role"] == "probe_development"]
        future = [row for row in items if row["evaluation_role"] == "future_eval"]
        if len(probe) != 3 or len(future) != 3:
            raise SupportP0Error(f"candidate split integrity failed for {memory_id}: probe={len(probe)}, future={len(future)}")
        pe = [int(row["controlled_delta"]) for row in probe]
        fe = [int(row["controlled_delta"]) for row in future]
        ps, fs = _effect_sign(pe), _effect_sign(fe)
        candidates.append({
            "memory_id": memory_id, "source_family": items[0]["source_family"],
            "candidate_index": items[0]["candidate_index"], "candidate_role": items[0]["candidate_role"],
            "probe_nonzero": sum(v != 0 for v in pe), "future_nonzero": sum(v != 0 for v in fe),
            "probe_harm": sum(v < 0 for v in pe), "future_harm": sum(v < 0 for v in fe),
            "probe_benefit": sum(v > 0 for v in pe), "future_benefit": sum(v > 0 for v in fe),
            "controlled_nonzero": sum(v != 0 for v in pe + fe),
            "probe_sign": ps, "future_sign": fs,
            "replicated_controlled_harm": any(v < 0 for v in pe) and any(v < 0 for v in fe),
            "replicated_controlled_benefit": any(v > 0 for v in pe) and any(v > 0 for v in fe),
            "probe_sign_predicts_future": ps != 0 and fs != 0 and ps == fs,
        })
    if len(candidates) != 12:
        raise SupportP0Error(f"full support analysis requires 12 memory candidates; found {len(candidates)}")

    nonzero = [row for row in units if int(row["controlled_delta"]) != 0]
    family_counts = Counter(str(row["target_family"]) for row in nonzero)
    eligible_folds = sorted(fam for fam, count in family_counts.items() if count >= 2)
    harm_candidates = sum(bool(row["replicated_controlled_harm"]) for row in candidates)
    benefit_candidates = sum(bool(row["replicated_controlled_benefit"]) for row in candidates)
    covered = [row for row in candidates if row["probe_sign"] != 0 and row["future_sign"] != 0]
    simple_correct = sum(bool(row["probe_sign_predicts_future"]) for row in covered)
    idea3 = {
        "candidate_count": {"required": 8, "actual": len(candidates), "pass": len(candidates) >= 8},
        "replicated_controlled_harm_candidates": {"required": 2, "actual": harm_candidates, "pass": harm_candidates >= 2},
        "replicated_controlled_benefit_candidates": {"required": 2, "actual": benefit_candidates, "pass": benefit_candidates >= 2},
        "candidate_level_independent_future_evaluation": {"required": True, "actual": True, "pass": True},
    }
    idea5 = {
        "total_nonzero_controlled_effects": {"required": 12, "actual": len(nonzero), "pass": len(nonzero) >= 12},
        "eligible_target_family_folds": {"required": 3, "actual": len(eligible_folds), "pass": len(eligible_folds) >= 3},
    }
    ready = all(x["pass"] for x in idea3.values()) and all(x["pass"] for x in idea5.values())
    return {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": FULL_STAGE,
        "complete_units": 72, "complete_executions": 216,
        "controlled_nonzero": len(nonzero),
        "controlled_harm": sum(int(row["controlled_delta"]) < 0 for row in units),
        "controlled_benefit": sum(int(row["controlled_delta"]) > 0 for row in units),
        "candidate_summary": candidates,
        "target_family_nonzero_counts": dict(sorted(family_counts.items())),
        "eligible_target_family_folds": eligible_folds,
        "idea3_support_checks": idea3, "idea5_support_checks": idea5,
        "strongest_simple_candidate_rule": {
            "name": "probe-sign predicts future-sign", "covered_candidates": len(covered),
            "correct_candidates": simple_correct,
            "accuracy_if_covered": simple_correct / len(covered) if covered else None,
            "scientific_role": "frozen simplification diagnostic; not an admission model",
        },
        "decision": "FULL_SUPPORT_ANALYSIS_READY" if ready else "FULL_SUPPORT_SUPPORT_INSUFFICIENT",
        "support_ready_for_cpu_method_analysis": ready,
        "method_failure_authorized": False,
        "admission_method_training_authorized": False,
        "second_model_authorized": False,
        "next_action": (
            "Run CPU-only candidate-level future evaluation and strongest-simplification analyses; do not train an admission classifier or open a second backbone yet."
            if ready else
            "HOLD method inference. Diagnose candidate replication and transport support without changing frozen thresholds; no second backbone."
        ),
        "unit_rows": units,
    }


def build_full_pre_gpu_audit(run_dir: Path, model_path: Path, *, wall_hours_cap: float = 3.0) -> dict[str, Any]:
    plan = _load_json(run_dir / "plan.json")
    material = _verified_material(plan)
    support_rows, support_source = _support_source_rows(run_dir, plan, model_path)
    support_cost = _load_json(run_dir / "support-qualification" / "cost.json")
    support_ids = set(material["support_qualification_unit_ids"])
    remaining = [row for row in material["units"] if row["unit_id"] not in support_ids]
    support_gpu_hours = float(support_cost.get("gpu_hours") or support_cost.get("wall_clock_hours") or 0.0)
    expected_new_gpu_hours = support_gpu_hours * (144 / 72)
    checks = {
        "support_qualification_pass": True,
        "frozen_plan_hash_verified": str(plan.get("plan_hash") or "") == _verified_plan_hash(plan),
        "reused_support_rows_exact": len(support_rows) == 72,
        "remaining_units_exact": len(remaining) == 48,
        "remaining_executions_exact": len(remaining) * 3 == 144,
        "candidate_future_split_frozen": all(row.get("evaluation_role") in {"probe_development", "future_eval"} for row in material["units"]),
        "wall_cap_sufficient": expected_new_gpu_hours > 0 and wall_hours_cap >= expected_new_gpu_hours * 1.25,
    }
    passed = all(checks.values())
    return {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID,
        "audit_id": "p0-mem-xfer-support-full-pre-gpu-v1", "created_at": _now(),
        "decision": "PASS" if passed else "HOLD", "execution_ready": passed,
        "plan_hash": plan["plan_hash"], "model_path": str(model_path),
        "checks": checks, "support_source": support_source,
        "budget": {
            "reused_support_executions": 72, "new_executions": 144, "full_executions": 216,
            "support_gpu_hours": support_gpu_hours,
            "expected_new_gpu_hours_from_support_throughput": expected_new_gpu_hours,
            "hard_wall_hours": wall_hours_cap,
        },
        "analysis_contract": {
            "candidate_replication": "same candidate must show the same controlled sign in both probe_development and future_eval; require >=2 harm candidates and >=2 benefit candidates",
            "candidate_count_minimum": 8,
            "transport_support": ">=12 controlled nonzero effects and >=3 target-family folds with >=2 nonzero each",
            "strongest_simple_candidate_rule": "probe-sign predicts future-sign",
            "global_behavior_drift_retired": True,
            "threshold_retuning_after_outcomes_forbidden": True,
            "method_pass_from_support_counts_forbidden": True,
        },
        "provenance_contract": {
            "exclusive_lock_before_model_load": True,
            "duplicate_process_contaminates_run": True,
            "support_rows_reused_not_rerun": True,
            "partial_full_run_has_no_scientific_authority": True,
        },
        "method_failure_authorized": False,
        "admission_method_training_authorized": False,
        "second_model_authorized": False,
    }


def _verified_plan_hash(plan: dict[str, Any]) -> str:
    material = {key: value for key, value in plan.items() if key not in {"created_at", "plan_hash", "pre_gpu_audit", "pre_gpu_audit_sha256", "immutable_after_creation"}}
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def run_full_qwen_support(
    *, run_dir: Path, alfworld_config: Path, model_path: Path,
    output_dir: Path, full_audit_path: Path, gpu_uuid: str,
    max_steps: int = 50, new_episode_cap: int = 144, wall_hours_cap: float = 3.0,
) -> dict[str, Any]:
    lock_path = run_dir / ".full-qwen.lock"
    with _exclusive_run_lock(lock_path):
        plan = _load_json(run_dir / "plan.json")
        material = _verified_material(plan)
        audit = _load_json(full_audit_path)
        if audit.get("decision") != "PASS" or audit.get("execution_ready") is not True:
            raise SupportP0Error("full pre-GPU audit did not PASS")
        if str(audit.get("plan_hash") or "") != str(plan.get("plan_hash") or ""):
            raise SupportP0Error("full audit/plan hash mismatch")
        if str(audit.get("model_path") or "") != str(model_path):
            raise SupportP0Error("full audit/model path mismatch")
        if new_episode_cap != 144:
            raise SupportP0Error(f"full new-episode budget must remain 144; got {new_episode_cap}")
        support_rows, support_source = _support_source_rows(run_dir, plan, model_path)
        support_ids = set(material["support_qualification_unit_ids"])
        remaining_units = [row for row in material["units"] if row["unit_id"] not in support_ids]
        if len(remaining_units) != 48:
            raise SupportP0Error(f"full remaining-unit contract mismatch: {len(remaining_units)} != 48")
        if output_dir.exists() and any(output_dir.iterdir()):
            raise SupportP0Error(f"refusing to overwrite non-empty full output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": FULL_STAGE,
            "plan_hash": plan["plan_hash"], "model_path": str(model_path), "gpu_uuid": gpu_uuid,
            "max_steps": max_steps, "new_episode_cap": new_episode_cap, "wall_hours_cap": wall_hours_cap,
            "reused_support_executions": 72, "new_executions": 144, "full_executions": 216,
            "full_units": 72, "support_source": support_source,
            "full_pre_gpu_audit": str(full_audit_path), "full_pre_gpu_audit_sha256": _file_hash(full_audit_path),
            "analysis_contract": audit.get("analysis_contract") or {},
            "provenance_contract": audit.get("provenance_contract") or {},
            "method_failure_authorized": False, "admission_method_training_authorized": False,
            "second_model_authorized": False,
        }
        _atomic_json(output_dir / "manifest.json", manifest)
        raw_path = output_dir / "raw-traces.jsonl"
        raw_path.write_bytes((run_dir / "support-qualification" / "raw-traces.jsonl").read_bytes())
        _atomic_json(output_dir / "progress.json", {
            "schema_version": "1.0", "status": "full_qwen_support_running",
            "completed_episodes": 72, "total_episodes": 216,
            "completed_units": 24, "total_units": 72,
            "reused_support_episodes": 72, "new_completed_episodes": 0,
            "gpu_uuid": gpu_uuid, "updated_at": _now(),
        })

        runner = ALFWorldGameRunner(load_config(alfworld_config))
        policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
        memory_map = {str(row["memory_id"]): row for row in material["source_memories"]}
        placebo_cache: dict[str, tuple[str, int, int]] = {}
        records: list[dict[str, Any]] = list(support_rows)
        started = time.monotonic()
        new_records = 0
        try:
            for full_index, unit in enumerate(remaining_units, 1):
                memory_id = str(unit["memory_id"])
                memory = str(memory_map[memory_id]["text"])
                if memory_id not in placebo_cache:
                    placebo_cache[memory_id] = _token_matched_placebo(policy, memory)
                placebo, memory_tokens, placebo_tokens = placebo_cache[memory_id]
                for arm in unit["arm_order"]:
                    elapsed = (time.monotonic() - started) / 3600.0
                    if new_records >= new_episode_cap:
                        raise SupportP0Error(f"BUDGET_STOP new episode cap reached: {new_records} >= {new_episode_cap}")
                    if elapsed >= wall_hours_cap:
                        raise SupportP0Error(f"BUDGET_STOP wall cap reached: {elapsed:.4f} >= {wall_hours_cap}")
                    context = "" if arm == "no-memory" else "MEMORY::" + (memory if arm == "retrieved" else placebo)
                    before = policy.usage_snapshot()
                    trace = runner.run_game_file(material["split"], str(unit["target_task_id"]), policy, context, max_steps=max_steps)
                    after = policy.usage_snapshot()
                    record = {
                        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": FULL_STAGE,
                        "unit_id": unit["unit_id"], "unit_index": 24 + full_index, "arm": arm,
                        "memory_id": memory_id, "source_family": unit["source_family"],
                        "target_family": unit["target_family"], "target_task_id": unit["target_task_id"],
                        "candidate_index": unit["candidate_index"], "candidate_role": unit["candidate_role"],
                        "evaluation_role": unit["evaluation_role"],
                        "memory_token_count": memory_tokens, "placebo_token_count": placebo_tokens,
                        "token_match_gap": abs(memory_tokens - placebo_tokens),
                        "success": int(trace.get("success") or trace.get("won") or 0),
                        "score": float(trace.get("score") or 0.0), "steps": int(trace.get("steps") or 0),
                        "invalid_actions": int(trace.get("invalid_actions") or 0), "actions": trace.get("actions") or [],
                        "usage": _usage_delta(before, after), "recorded_at": _now(),
                    }
                    records.append(record)
                    _append_jsonl(raw_path, record)
                    new_records += 1
                    _atomic_json(output_dir / "progress.json", {
                        "schema_version": "1.0", "status": "full_qwen_support_running",
                        "completed_episodes": len(records), "total_episodes": 216,
                        "completed_units": len(records) // 3, "total_units": 72,
                        "reused_support_episodes": 72, "new_completed_episodes": new_records,
                        "current_unit": unit["unit_id"], "current_arm": arm,
                        "elapsed_new_hours": (time.monotonic() - started) / 3600.0,
                        "new_model_calls": int(policy.usage_snapshot().get("generation_calls") or 0),
                        "gpu_uuid": gpu_uuid, "updated_at": _now(),
                    })
        except Exception as error:
            kind = "BUDGET-STOP" if str(error).startswith("BUDGET_STOP") else "RUNTIME-BLOCKER"
            _atomic_json(output_dir / "runtime-error.json", {
                "error_type": type(error).__name__, "typed_outcome": kind, "message": str(error),
                "scientific_result_available": False, "method_failure_authorized": False,
                "admission_method_training_authorized": False, "second_model_authorized": False,
                "recorded_at": _now(),
            })
            _atomic_json(output_dir / "progress.json", {
                "schema_version": "1.0", "status": "budget-stop" if kind == "BUDGET-STOP" else "runtime-blocker",
                "completed_episodes": len(records), "total_episodes": 216,
                "completed_units": len(records) // 3, "total_units": 72,
                "reused_support_episodes": 72, "new_completed_episodes": new_records,
                "scientific_result_available": False, "method_failure_authorized": False,
                "error": str(error), "gpu_uuid": gpu_uuid, "updated_at": _now(),
            })
            raise

        analysis = analyze_full_support_rows(records)
        elapsed_new = (time.monotonic() - started) / 3600.0
        new_usage = policy.usage_snapshot()
        support_cost = _load_json(run_dir / "support-qualification" / "cost.json")
        cost = {
            "schema_version": "1.0",
            "reused_support": support_cost,
            "new_full_extension": {
                "gpu_hours": elapsed_new, "wall_clock_hours": elapsed_new,
                "environment_episodes": new_records,
                "model_calls": int(new_usage.get("generation_calls") or 0),
                "input_tokens": int(new_usage.get("input_tokens") or 0),
                "output_tokens": int(new_usage.get("output_tokens") or 0),
                "tokens": int(new_usage.get("tokens") or 0),
            },
            "total_environment_episodes": 216,
            "total_gpu_hours": float(support_cost.get("gpu_hours") or 0.0) + elapsed_new,
            "total_model_calls": int(support_cost.get("model_calls") or 0) + int(new_usage.get("generation_calls") or 0),
            "accounting_consistent": len(records) == 216 and new_records == 144,
        }
        _atomic_json(output_dir / "analysis.json", analysis)
        _atomic_json(output_dir / "cost.json", cost)
        _atomic_json(output_dir / "decision.json", {
            "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": FULL_STAGE,
            "decision": analysis["decision"],
            "idea3_support_checks": analysis["idea3_support_checks"],
            "idea5_support_checks": analysis["idea5_support_checks"],
            "method_failure_authorized": False,
            "admission_method_training_authorized": False,
            "second_model_authorized": False,
            "next_action": analysis["next_action"], "created_at": _now(),
        })
        fields = [
            "unit_id", "memory_id", "source_family", "target_family", "target_task_id",
            "candidate_index", "candidate_role", "evaluation_role",
            "retrieved_success", "no_memory_success", "placebo_success",
            "retrieved_delta", "placebo_delta", "controlled_delta", "outcome_disagreement",
        ]
        with (output_dir / "main_table.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in analysis["unit_rows"]:
                writer.writerow({key: row.get(key) for key in fields})
        _atomic_json(output_dir / "progress.json", {
            "schema_version": "1.0", "status": "full_qwen_support_complete",
            "completed_episodes": 216, "total_episodes": 216,
            "completed_units": 72, "total_units": 72,
            "reused_support_episodes": 72, "new_completed_episodes": 144,
            "decision": analysis["decision"], "elapsed_new_hours": elapsed_new,
            "new_model_calls": int(new_usage.get("generation_calls") or 0),
            "gpu_uuid": gpu_uuid, "method_failure_authorized": False,
            "admission_method_training_authorized": False, "second_model_authorized": False,
            "updated_at": _now(),
        })
        return {"analysis": analysis, "cost": cost}
