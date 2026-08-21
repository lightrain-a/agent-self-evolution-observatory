from __future__ import annotations

import argparse
import fcntl
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, ArkSettings
from .config import StorageSettings
from .discovery_engine_terminal_replication import _call, _jsha, _write_json


def _import_pyarrow(vendor: Path):
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq
    return pq


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_'-]+", text.lower()))


def _jaccard_distance(a: str, b: str) -> float:
    aa, bb = _tokens(a), _tokens(b)
    union = aa | bb
    if not union:
        return 0.0
    return 1.0 - len(aa & bb) / len(union)


def _titles(text: str) -> list[str]:
    values = re.findall(r"^##\s*Title:\s*(.+?)\s*$", str(text or ""), flags=re.MULTILINE)
    return [_normalize_text(v) for v in values]


def _action_summary(trajectory_json: str) -> str:
    data = json.loads(trajectory_json)
    lines: list[str] = []
    for step_id, step in sorted((data.get("steps") or {}).items(), key=lambda kv: int(kv[0])):
        output = (step or {}).get("output_messages") or {}
        tool_call_message = output.get("tool_call_message") or {}
        calls = tool_call_message.get("tool_calls") or []
        if calls:
            args = calls[0].get("args") or {}
            current = args.get("current_state") or {}
            if current.get("evaluation_previous_goal"):
                lines.append(f"Step {step_id} evaluation: {_normalize_text(current['evaluation_previous_goal'])[:500]}")
            if current.get("next_goal"):
                lines.append(f"Step {step_id} next goal: {_normalize_text(current['next_goal'])[:500]}")
            for action in args.get("action") or []:
                lines.append(f"Step {step_id} action: {json.dumps(action, ensure_ascii=False, sort_keys=True)[:900]}")
        controller = (step or {}).get("controller_messages") or {}
        for result in controller.get("action_result") or []:
            content = result.get("content") if isinstance(result, dict) else str(result)
            if content:
                lines.append(f"Step {step_id} result: {_normalize_text(content)[:900]}")
        if len(lines) >= 36:
            break
    return "\n".join(lines)


def _select_rows(parquet_path: Path, vendor: Path) -> list[dict[str, Any]]:
    pq = _import_pyarrow(vendor)
    rows = pq.read_table(parquet_path, columns=["task_id", "task_prompt", "is_successful", "trajectory_json"]).to_pylist()
    valid = []
    for row in rows:
        try:
            summary = _action_summary(row["trajectory_json"])
        except Exception:
            continue
        if summary.strip():
            valid.append({**row, "action_summary": summary})
    chosen = []
    for outcome in (False, True):
        subset = sorted([r for r in valid if bool(r["is_successful"]) is outcome], key=lambda r: int(r["task_id"]))
        chosen.extend(subset[:3])
    return sorted(chosen, key=lambda r: int(r["task_id"]))


def _prompt(system_prompt: str, task: str, trajectory: str) -> str:
    return f"""{system_prompt.strip()}\n\nTask: {task}\n\nTrajectory:\n{trajectory}\n\nCreate memory items for the task above. Return only the requested Markdown memory-item format."""


def run(contract: dict[str, Any], *, private_root: Path, output: Path) -> dict[str, Any]:
    if contract.get("status") != "FROZEN_BEFORE_PROVIDER_CALLS":
        raise ValueError("f0-contract-not-frozen")
    source = contract["frozen_source"]
    parquet = Path(source["trajectory_parquet"])
    success_prompt = Path(source["reasoningbank_success_prompt"]).read_text(encoding="utf-8")
    failure_prompt = Path(source["reasoningbank_failure_prompt"]).read_text(encoding="utf-8")
    vendor = Path("generated/research-data/paper-yield-d5-c01/vendor")
    selected = _select_rows(parquet, vendor)
    if len(selected) != 6 or sum(bool(r["is_successful"]) for r in selected) != 3:
        raise ValueError("balanced-six-trajectory-sample-not-available")
    model_cfg = contract["model"]
    base = ArkSettings.from_env()
    settings = ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0)
    client = ArkResponsesClient(settings)

    def responder(**kwargs: Any) -> dict[str, Any]:
        return client.respond(kwargs["prompt"], model=kwargs["model"], max_output_tokens=kwargs["max_output_tokens"], temperature=kwargs["temperature"], thinking=None, store=True)

    pairs = []
    receipts = []
    failures = []
    for row in selected:
        memories = {}
        for label, system_prompt in (("success", success_prompt), ("failure", failure_prompt)):
            prompt = _prompt(system_prompt, row["task_prompt"], row["action_summary"])
            result, receipt = _call(responder, private_root, str(contract["experiment_id"]), f"memory-{label}", f"task-{row['task_id']}", prompt, str(model_cfg["requested"]), int(model_cfg["max_output_tokens"]), float(model_cfg["temperature"]))
            receipts.append(receipt)
            if result is None:
                failures.append({"task_id": str(row["task_id"]), "label": label, **receipt})
                memories[label] = ""
            else:
                memories[label] = str(result.get("text") or "")
        success = memories["success"]
        failure = memories["failure"]
        pairs.append({
            "task_id": str(row["task_id"]),
            "task_prompt": row["task_prompt"],
            "original_is_successful": bool(row["is_successful"]),
            "trajectory_summary_sha256": _jsha(row["action_summary"]),
            "success_memory_sha256": next((r.get("raw_sha256") for r in receipts[::-1] if r.get("engine_id") == f"task-{row['task_id']}" and r.get("stage") == "memory-success"), ""),
            "failure_memory_sha256": next((r.get("raw_sha256") for r in receipts[::-1] if r.get("engine_id") == f"task-{row['task_id']}" and r.get("stage") == "memory-failure"), ""),
            "exact_content_changed": bool(success and failure and _normalize_text(success) != _normalize_text(failure)),
            "token_jaccard_distance": round(_jaccard_distance(success, failure), 6) if success and failure else None,
            "success_titles": _titles(success),
            "failure_titles": _titles(failure),
            "title_set_changed": bool(success and failure and set(_titles(success)) != set(_titles(failure))),
            "scientific_authority": False,
        })
    complete = [p for p in pairs if p["token_jaccard_distance"] is not None]
    report = {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "status": "F0_COMPLETE" if len(complete) == 6 else "F0_SUPPORT_INCOMPLETE",
        "contract_sha256": _jsha(contract),
        "hypothesis": contract["hypothesis"],
        "sample": [{"task_id": p["task_id"], "original_is_successful": p["original_is_successful"], "task_prompt": p["task_prompt"]} for p in pairs],
        "summary": {
            "paired_trajectories_requested": 6,
            "paired_trajectories_complete": len(complete),
            "paired_exact_content_change_rate": round(sum(p["exact_content_changed"] for p in complete) / len(complete), 6) if complete else None,
            "paired_title_set_change_rate": round(sum(p["title_set_changed"] for p in complete) / len(complete), 6) if complete else None,
            "mean_token_jaccard_distance": round(sum(p["token_jaccard_distance"] for p in complete) / len(complete), 6) if complete else None,
            "min_token_jaccard_distance": min((p["token_jaccard_distance"] for p in complete), default=None),
            "max_token_jaccard_distance": max((p["token_jaccard_distance"] for p in complete), default=None),
            "provider_failures": len(failures),
        },
        "falsifier_result": "SURVIVES_F0" if complete and any(p["exact_content_changed"] for p in complete) else "FALSIFIED_OR_INCOMPLETE",
        "pairs": pairs,
        "provider_receipts": receipts,
        "failures": failures,
        "experiment_debt": contract["experiment_debt_after_f0"],
        "scientific_authority": False,
        "authority": {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }
    _write_json(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path("generated/d2-proxy-reward-memory-f0-contract.json"))
    parser.add_argument("--output", type=Path, default=Path("generated/d2-proxy-reward-memory-f0.json"))
    parser.add_argument("--private-root", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    root = args.private_root or StorageSettings.from_env().data_root / "d2-proxy-reward-memory-f0"
    root.mkdir(parents=True, exist_ok=True)
    lock = (root / "transaction.lock").open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "experiment_id": contract["experiment_id"]}))
        return
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing.get("status") == "F0_COMPLETE" and existing.get("contract_sha256") == _jsha(contract):
            print(json.dumps({"status": "REPLAY_COMPLETED_PUBLIC_STATE", "summary": existing.get("summary"), "falsifier_result": existing.get("falsifier_result")}, ensure_ascii=False, indent=2))
            return
    report = run(contract, private_root=root, output=args.output)
    print(json.dumps({"status": report["status"], "summary": report["summary"], "falsifier_result": report["falsifier_result"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
