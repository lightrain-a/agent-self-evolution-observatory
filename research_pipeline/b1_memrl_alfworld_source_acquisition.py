from __future__ import annotations

import argparse
import hashlib
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config

EXPECTED_PREFLIGHT_STATUS = "FRESH_SUBSTRATE_G1_G8_PREFLIGHT_PASS"
SOURCE_BATCH_SIZE = 6


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _memory_body(trace: dict[str, Any]) -> str:
    parts = [f"Task: {trace.get('task_goal') or ''}", "", "Archived Trajectory:"]
    observations = list(trace.get("observations") or [])
    actions = list(trace.get("actions") or [])
    if observations:
        parts.append("Observation: " + str(observations[0]).strip())
    for index, action in enumerate(actions):
        parts.append("Action: " + str(action).strip())
        if index + 1 < len(observations):
            parts.append("Observation: " + str(observations[index + 1]).strip())
    return "\n".join(parts).strip()


def _source_rows(output_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((output_dir / "source").glob("*.json")) if (output_dir / "source").exists() else []:
        try:
            row = _load(path)
        except Exception:
            continue
        rows.append(row)
    return rows


def _support_summary(rows: list[dict[str, Any]], preflight: dict[str, Any]) -> dict[str, Any]:
    valid = [r for r in rows if r.get("execution_valid") is True]
    successes = [r for r in valid if r.get("true_provenance") == "success"]
    failures = [r for r in valid if r.get("true_provenance") == "failure"]
    gate = preflight.get("source_acquisition_gate") or {}
    min_s = int(gate.get("minimum_environment_success_sources") or 2)
    min_f = int(gate.get("minimum_environment_failure_sources") or 2)
    next_boundary = len(rows) > 0 and len(rows) % SOURCE_BATCH_SIZE == 0
    support_met = len(successes) >= min_s and len(failures) >= min_f and next_boundary
    return {
        "attempted_sources": len(rows),
        "execution_valid_sources": len(valid),
        "environment_success_sources": len(successes),
        "environment_failure_sources": len(failures),
        "runtime_invalid_sources": len(rows) - len(valid),
        "batch_boundary": next_boundary,
        "support_met": support_met,
        "success_source_indices": [int(r["source_index"]) for r in successes],
        "failure_source_indices": [int(r["source_index"]) for r in failures],
    }


def acquire_next_batch(
    *,
    preflight_path: Path,
    output_dir: Path,
    config_path: Path,
    model_path: Path,
    alfworld_data: Path,
    device: str,
) -> dict[str, Any]:
    preflight = _load(preflight_path)
    if preflight.get("status") != EXPECTED_PREFLIGHT_STATUS:
        raise RuntimeError("fresh preflight is not PASS")
    if any((preflight.get("authority") or {}).get(k) is not False for k in ("scientific", "paper", "experiment", "provider", "gpu", "submission")):
        raise RuntimeError("preflight authority boundary drift")
    pool = list((preflight.get("task_partition") or {}).get("source_pool") or [])
    gate = preflight.get("source_acquisition_gate") or {}
    if int(gate.get("initial_batch") or 0) != SOURCE_BATCH_SIZE or int(gate.get("extension_batch") or 0) != SOURCE_BATCH_SIZE:
        raise RuntimeError("source batch contract drift")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "source").mkdir(parents=True, exist_ok=True)

    existing = _source_rows(output_dir)
    summary_before = _support_summary(existing, preflight)
    if summary_before["support_met"]:
        return {"status": "SOURCE_SUPPORT_ALREADY_PASS", "summary": summary_before, "new_sources": 0}
    start = len(existing)
    if start >= len(pool):
        return {"status": "HOLD_SOURCE_PROVENANCE_SUPPORT", "summary": summary_before, "new_sources": 0}
    end = min(start + SOURCE_BATCH_SIZE, len(pool))

    os.environ["ALFWORLD_DATA"] = str(alfworld_data.resolve())
    config = load_config(config_path)
    policy = HFAdmissiblePolicy(model_path, device=device, policy_mode="react-family")
    runner = ALFWorldGameRunner(config)
    new_rows = []
    for index in range(start, end):
        source = pool[index]
        gamefile = alfworld_data / "json_2.1.1" / "train" / source["relative_gamefile"]
        row: dict[str, Any] = {
            "schema_version": "1.0",
            "paper_id": preflight.get("paper_id"),
            "preflight_manifest_sha256": preflight.get("manifest_sha256"),
            "source_index": index,
            "family": source.get("family"),
            "relative_gamefile": source.get("relative_gamefile"),
            "expected_gamefile_sha256": source.get("gamefile_sha256"),
            "gamefile_sha256": hashlib.sha256(gamefile.read_bytes()).hexdigest(),
            "started_at": _now(),
            "execution_valid": False,
            "scientific_authority": False,
        }
        usage_before = policy.usage_snapshot()
        try:
            trace = runner.run_game_file("train", str(gamefile), policy, patch="", max_steps=int((preflight.get("executor") or {}).get("max_steps") or 30))
            body = _memory_body(trace)
            usage_after = policy.usage_snapshot()
            usage = {k: int(usage_after.get(k, 0)) - int(usage_before.get(k, 0)) for k in usage_after}
            row.update({
                "finished_at": _now(),
                "execution_valid": True,
                "true_provenance": "success" if int(trace.get("success") or 0) == 1 else "failure",
                "environment_success": int(trace.get("success") or 0),
                "environment_score": float(trace.get("score") or 0.0),
                "terminated": bool(trace.get("terminated")),
                "steps": int(trace.get("steps") or 0),
                "invalid_actions": int(trace.get("invalid_actions") or 0),
                "task_goal": trace.get("task_goal") or "",
                "actions": trace.get("actions") or [],
                "observations": trace.get("observations") or [],
                "raw_choices": trace.get("raw_choices") or [],
                "memory_body": body,
                "memory_body_sha256": _sha_text(body),
                "usage": usage,
            })
        except Exception as exc:
            row.update({
                "finished_at": _now(),
                "execution_valid": False,
                "runtime_error_class": type(exc).__name__,
                "runtime_error": str(exc)[:1000],
                "traceback_tail": traceback.format_exc()[-4000:],
                "true_provenance": None,
            })
        target = output_dir / "source" / f"{index:02d}.json"
        target.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        new_rows.append(row)

    all_rows = _source_rows(output_dir)
    summary = _support_summary(all_rows, preflight)
    max_sources = int(gate.get("maximum_sources") or len(pool))
    status = "SOURCE_PROVENANCE_SUPPORT_PASS" if summary["support_met"] else ("HOLD_SOURCE_PROVENANCE_SUPPORT" if len(all_rows) >= max_sources else "SOURCE_PROVENANCE_SUPPORT_INCOMPLETE")
    receipt = {
        "schema_version": "1.0",
        "paper_id": preflight.get("paper_id"),
        "status": status,
        "updated_at": _now(),
        "preflight_manifest_sha256": preflight.get("manifest_sha256"),
        "source_acquisition_rule": gate,
        "summary": summary,
        "new_source_indices": [int(r["source_index"]) for r in new_rows],
        "target_outcomes_opened": False,
        "pilot_execution_authorized": status == "SOURCE_PROVENANCE_SUPPORT_PASS",
        "confirmatory_execution_authorized": False,
        "scientific_authority": False,
        "submission_authority": False,
    }
    receipt["receipt_sha256"] = _sha_text(json.dumps({k: v for k, v in receipt.items() if k not in {"updated_at", "receipt_sha256"}}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    (output_dir / "source-support.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": status, "summary": summary, "new_sources": len(new_rows), "receipt_sha256": receipt["receipt_sha256"]}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--preflight", type=Path, default=Path("generated/b1-memrl-alfworld-fresh-preflight-20260830.json"))
    p.add_argument("--output-dir", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/runs/b1-memrl-alfworld-fresh-20260830"))
    p.add_argument("--config", type=Path, default=Path("research_pipeline/p0_alfworld_config.yaml"))
    p.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    p.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    p.add_argument("--device", default="cuda:0")
    a = p.parse_args()
    result = acquire_next_batch(preflight_path=a.preflight, output_dir=a.output_dir, config_path=a.config, model_path=a.model_path, alfworld_data=a.alfworld_data, device=a.device)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
