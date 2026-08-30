from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from typing import Any

from .b1_memrl_alfworld_fresh_preflight import render_memory_patch
from .b1_memrl_alfworld_target_plan import ARMS, PAPER_ID, PREFLIGHT_STATUS, content_hash, load, now, sha_file, sha_text
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config


def _source(output_dir: Path, index: int) -> dict[str, Any]:
    row = load(output_dir / "source" / f"{index:02d}.json")
    body = str(row.get("memory_body") or "")
    if row.get("execution_valid") is not True or sha_text(body) != row.get("memory_body_sha256"):
        raise RuntimeError(f"invalid source row:{index}")
    return row


def _arm_path(output_dir: Path, phase: str, target_index: int, arm: str) -> Path:
    return output_dir / "targets" / phase / f"{target_index:02d}" / f"{arm}.json"


def _trace_path(output_dir: Path, phase: str, target_index: int, arm: str) -> Path:
    return output_dir / "target-traces" / phase / f"{target_index:02d}" / f"{arm}.json"


def _summary_path(output_dir: Path, phase: str) -> Path:
    return output_dir / f"{phase}-summary.json"


def _changed(left: list[str], right: list[str]) -> bool:
    return list(left or []) != list(right or [])


def _pair_summary(rows: dict[str, dict[str, Any]], assignment: dict[str, Any]) -> dict[str, Any]:
    a0, a1, a2, a5, a7 = (rows[name] for name in ARMS)
    all_valid = all(row.get("execution_valid") is True for row in rows.values())
    no_channel = bool(all_valid and a1.get("patch_sha256") == a7.get("patch_sha256") and a1.get("actions") == a7.get("actions") and a1.get("terminal_success") == a7.get("terminal_success"))
    compare_arms = ("A1_CONTENT_ONLY", "A2_TRUTHFUL_VISIBLE_PROVENANCE", "A5_FLIPPED_VISIBLE_PROVENANCE")
    seq_change = {arm: _changed(a0.get("actions") or [], rows[arm].get("actions") or []) for arm in compare_arms}
    first_change = {arm: str(a0.get("first_action") or "") != str(rows[arm].get("first_action") or "") for arm in compare_arms}
    return {
        "target_index": int(assignment["target_index"]),
        "family": assignment.get("family"),
        "relative_gamefile": assignment.get("relative_gamefile"),
        "source_index": int(assignment["source_index"]),
        "source_memory_body_sha256": assignment.get("source_memory_body_sha256"),
        "true_provenance": assignment.get("true_provenance"),
        "all_arms_execution_valid": all_valid,
        "no_channel_negative_control_exact": no_channel,
        "action_sequence_changed_vs_A0": seq_change,
        "first_action_changed_vs_A0": first_change,
        "memory_utilization_observed": any(seq_change.values()),
        "terminal_success": {arm: int(rows[arm].get("terminal_success") or 0) for arm in ARMS},
        "first_action": {arm: rows[arm].get("first_action") or "" for arm in ARMS},
    }


def run_target_phase(*, phase: str, preflight_path: Path, plan_path: Path, output_dir: Path, config_path: Path, model_path: Path, alfworld_data: Path, device: str) -> dict[str, Any]:
    if phase not in {"pilot", "confirmatory"}:
        raise ValueError("phase must be pilot or confirmatory")
    preflight, plan = load(preflight_path), load(plan_path)
    if preflight.get("status") != PREFLIGHT_STATUS or plan.get("status") != "TARGET_EXECUTION_PLAN_FROZEN":
        raise RuntimeError("preflight/target plan not frozen")
    if plan.get("preflight_manifest_sha256") != preflight.get("manifest_sha256"):
        raise RuntimeError("target plan/preflight drift")
    if plan.get("plan_sha256") != content_hash(plan, exclude={"generated_at", "plan_sha256"}):
        raise RuntimeError("target execution plan hash drift")
    if phase == "confirmatory":
        pilot = load(_summary_path(output_dir, "pilot"))
        if pilot.get("status") != "PILOT_UTILIZATION_PASS" or pilot.get("confirmatory_execution_authorized") is not True:
            raise RuntimeError("confirmatory launch blocked until pilot utilization PASS")

    assignments = list((plan.get("assignments") or {}).get(phase) or [])
    expected_n = int((preflight.get("statistics") or {}).get(f"{phase}_n") or 0)
    if len(assignments) != expected_n:
        raise RuntimeError(f"{phase} target count drift")

    os.environ["ALFWORLD_DATA"] = str(alfworld_data.resolve())
    policy = HFAdmissiblePolicy(model_path, device=device, policy_mode=str((preflight.get("executor") or {}).get("policy_mode") or "react-family"))
    runner = ALFWorldGameRunner(load_config(config_path))
    pairs: list[dict[str, Any]] = []
    fatal, post_exposure = False, 0

    for assignment in assignments:
        source = _source(output_dir, int(assignment["source_index"]))
        body, provenance = str(source["memory_body"]), str(source["true_provenance"])
        target = alfworld_data / "json_2.1.1" / "valid_unseen" / str(assignment["relative_gamefile"])
        if sha_file(target) != assignment.get("expected_gamefile_sha256"):
            raise RuntimeError(f"target gamefile hash drift:{assignment.get('relative_gamefile')}")
        rows: dict[str, dict[str, Any]] = {}
        for arm in ARMS:
            patch = render_memory_patch(body, arm, provenance)
            patch_sha = sha_text(patch)
            if patch_sha != (assignment.get("arm_patch_sha256") or {}).get(arm):
                raise RuntimeError(f"arm patch drift:{phase}:{assignment['target_index']}:{arm}")
            receipt_path = _arm_path(output_dir, phase, int(assignment["target_index"]), arm)
            trace_path = _trace_path(output_dir, phase, int(assignment["target_index"]), arm)
            existing = load(receipt_path) if receipt_path.exists() else None
            if existing and existing.get("execution_valid") is True:
                rows[arm] = existing
                continue
            if existing and existing.get("executor_prompt_sent") is True:
                rows[arm] = existing; fatal = True; post_exposure += 1; continue
            retry = (int(existing.get("pre_exposure_retry_count") or 0) + 1) if existing else 0
            if retry > 1:
                rows[arm] = existing; fatal = True; continue

            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            before = policy.usage_snapshot()
            row: dict[str, Any] = {
                "schema_version": "1.0", "paper_id": PAPER_ID, "phase": phase,
                "target_index": int(assignment["target_index"]), "relative_gamefile": assignment.get("relative_gamefile"),
                "expected_gamefile_sha256": assignment.get("expected_gamefile_sha256"), "source_index": int(assignment["source_index"]),
                "source_memory_body_sha256": source.get("memory_body_sha256"), "true_provenance": provenance, "arm": arm,
                "patch_sha256": patch_sha, "plan_sha256": plan.get("plan_sha256"), "preflight_manifest_sha256": preflight.get("manifest_sha256"),
                "started_at": now(), "execution_valid": False, "executor_prompt_sent": False, "pre_exposure_retry_count": retry,
                "scientific_authority": False, "submission_authority": False,
            }
            try:
                trace = runner.run_game_file("eval_out_of_distribution", str(target), policy, patch=patch, max_steps=int((preflight.get("executor") or {}).get("max_steps") or 30))
                after = policy.usage_snapshot(); usage = {k: int(after.get(k, 0)) - int(before.get(k, 0)) for k in after}
                trace_path.write_text(json.dumps({"schema_version": "1.0", "paper_id": PAPER_ID, "phase": phase, "target_index": int(assignment["target_index"]), "arm": arm, "trace": trace}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                actions = list(trace.get("actions") or [])
                row.update({"finished_at": now(), "execution_valid": True, "executor_prompt_sent": int(usage.get("generation_calls") or 0) > 0,
                    "terminal_success": int(trace.get("success") or 0), "environment_score": float(trace.get("score") or 0.0), "terminated": bool(trace.get("terminated")),
                    "steps": int(trace.get("steps") or 0), "invalid_actions": int(trace.get("invalid_actions") or 0), "first_action": actions[0] if actions else "",
                    "actions": actions, "actions_sha256": sha_text(json.dumps(actions, ensure_ascii=False, separators=(",", ":"))), "trace_path": str(trace_path),
                    "trace_sha256": sha_file(trace_path), "usage": usage})
            except Exception as exc:
                after = policy.usage_snapshot(); usage = {k: int(after.get(k, 0)) - int(before.get(k, 0)) for k in after}; sent = int(usage.get("generation_calls") or 0) > 0
                row.update({"finished_at": now(), "execution_valid": False, "executor_prompt_sent": sent, "runtime_error_class": type(exc).__name__,
                    "runtime_error": str(exc)[:1000], "traceback_tail": traceback.format_exc()[-4000:], "usage": usage})
                fatal = True; post_exposure += int(sent)
            row["receipt_sha256"] = content_hash(row, exclude={"started_at", "finished_at", "receipt_sha256"})
            receipt_path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            rows[arm] = row
        if set(rows) == set(ARMS):
            pairs.append(_pair_summary(rows, assignment))
        else:
            fatal = True

    no_channel = sum(not row.get("no_channel_negative_control_exact") for row in pairs)
    all_valid = len(pairs) == len(assignments) and all(row.get("all_arms_execution_valid") for row in pairs)
    utilization = sum(bool(row.get("memory_utilization_observed")) for row in pairs)
    if fatal or not all_valid: status = "HOLD_RUNTIME_INVALID_POST_EXPOSURE" if post_exposure else "HOLD_RUNTIME_INVALID_PRE_EXPOSURE"
    elif no_channel: status = "HOLD_NO_CHANNEL_NEGATIVE_CONTROL_FAILED"
    elif phase == "pilot" and utilization == 0: status = "HOLD_MEMORY_UNUSED"
    elif phase == "pilot": status = "PILOT_UTILIZATION_PASS"
    else: status = "CONFIRMATORY_COLLECTED"

    out: dict[str, Any] = {"schema_version": "1.0", "paper_id": PAPER_ID, "phase": phase, "status": status, "generated_at": now(),
        "plan_sha256": plan.get("plan_sha256"), "preflight_manifest_sha256": preflight.get("manifest_sha256"), "target_count_expected": len(assignments),
        "target_count_complete": len(pairs), "all_arms_execution_valid": all_valid, "post_exposure_failures": post_exposure,
        "no_channel_negative_control_failures": no_channel, "memory_utilization_target_count": utilization, "targets": pairs,
        "confirmatory_execution_authorized": phase == "pilot" and status == "PILOT_UTILIZATION_PASS", "scientific_authority": False, "submission_authority": False}
    out["receipt_sha256"] = content_hash(out, exclude={"generated_at", "receipt_sha256"})
    _summary_path(output_dir, phase).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out
