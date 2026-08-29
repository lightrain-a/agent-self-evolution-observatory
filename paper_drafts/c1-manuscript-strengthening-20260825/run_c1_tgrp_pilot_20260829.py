from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file

RUN_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-pilot-v1")
MANIFEST = RUN_ROOT / "run-manifest.json"
SCHEDULE = RUN_ROOT / "schedule.jsonl"
CANONICAL_ENV = Path("/home/wyt/code/agent-self-evolution-observatory/.env")
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def action_signature(payload: dict[str, Any]) -> str:
    current = payload.get("current_state") or {}
    actions = payload.get("action") or (current.get("action") if isinstance(current, dict) else None) or []
    if not actions or not isinstance(actions[0], dict):
        return "NO_ACTION"
    action = actions[0]
    name = next(iter(action), "UNKNOWN")
    args = action.get(name) or {}
    if name == "click_element" and isinstance(args, dict):
        return f"click_element:{args.get('index')}"
    return name


def parse_output(text: str) -> tuple[str, str, bool]:
    try:
        payload = extract_json_object(text)
        sig = action_signature(payload)
        current = payload.get("current_state") or {}
        goal = str(current.get("next_goal") or "") if isinstance(current, dict) else ""
        return sig, goal, False
    except Exception as strict_error:
        match = re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]', text, re.DOTALL)
        if not match:
            raise strict_error
        name = match.group(1)
        body = match.group(2)
        if name == "click_element":
            index = re.search(r'"index"\s*:\s*(\d+)', body)
            if not index:
                raise strict_error
            sig = f"click_element:{index.group(1)}"
        else:
            sig = name
        goal_match = re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"', text, re.DOTALL)
        goal = ""
        if goal_match:
            try:
                goal = json.loads('"' + goal_match.group(1) + '"')
            except Exception:
                goal = goal_match.group(1)
        return sig, goal, True


def archive_raw(text: str) -> tuple[str, Path]:
    digest = sha_text(text)
    path = RUN_ROOT / "raw" / digest[:2] / f"{digest}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_text(encoding="utf-8") == text, "raw archive collision")
    else:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    return digest, path


def load_schedule() -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in SCHEDULE.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(rows) == 312, "schedule geometry drift")
    require([int(row["order"]) for row in rows] == list(range(1, 313)), "schedule order drift")
    return rows


def current_case_state(schedule: list[dict[str, Any]]) -> tuple[list[str], list[str], int]:
    completed: list[str] = []
    failed: list[str] = []
    next_order = 313
    for row in schedule:
        case_path = RUN_ROOT / "per_case" / f"{row['case_id']}.json"
        if not case_path.exists():
            if next_order == 313:
                next_order = int(row["order"])
            continue
        case = read_json(case_path)
        if case.get("status") == "complete":
            completed.append(row["case_id"])
        else:
            failed.append(row["case_id"])
    return completed, failed, next_order


def update_progress(schedule: list[dict[str, Any]], status: str) -> None:
    completed, failed, next_order = current_case_state(schedule)
    payload = {
        "status": status,
        "completed": len(completed),
        "expected": len(schedule),
        "failed": len(failed),
        "provider_posts": len(completed) + len(failed),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(RUN_ROOT / "progress.json", payload)
    write_json(RUN_ROOT / "resume.json", {
        "next_order": next_order,
        "completed_case_ids": completed,
        "failed_case_ids": failed,
        "updated_at": payload["updated_at"],
    })
    write_json(RUN_ROOT / "heartbeat.json", {"status": status, "updated_at": payload["updated_at"]})


def execute_case(client: ArkResponsesClient, row: dict[str, Any]) -> dict[str, Any]:
    case_id = str(row["case_id"])
    input_path = Path(row["input_file"])
    require(input_path.is_file(), f"input missing:{case_id}")
    packet = read_json(input_path)
    prompt = str(packet["prompt"])
    require(sha_text(prompt) == row["prompt_sha256"] == packet["prompt_sha256"], f"prompt hash drift:{case_id}")

    started = datetime.now(timezone.utc).isoformat()
    response: dict[str, Any] | None = None
    provider_response_path = RUN_ROOT / "provider-responses" / f"{case_id}.json"
    case_path = RUN_ROOT / "per_case" / f"{case_id}.json"
    base = {
        "schema_version": "1.0",
        "case_id": case_id,
        "order": int(row["order"]),
        "future_task": int(row["future_task"]),
        "intent_template_id": int(row["intent_template_id"]),
        "selected_source_task": int(row["selected_source_task"]),
        "arm": row["arm"],
        "branch": row["branch"],
        "rollout": int(row["rollout"]),
        "input_file": str(input_path),
        "input_file_sha256": sha_file(input_path),
        "system_instruction_sha256": packet["system_instruction_sha256"],
        "task_prompt_sha256": packet["task_prompt_sha256"],
        "current_state_sha256": packet["current_state_sha256"],
        "memory_wrapper_sha256": packet["memory_wrapper_sha256"],
        "prompt_sha256": packet["prompt_sha256"],
        "requested_model": MODEL,
        "started_at": started,
        "provider_post_attempted": True,
    }
    try:
        response = client.respond(
            prompt,
            model=MODEL,
            max_output_tokens=900,
            temperature=0.2,
            thinking="disabled",
            store=True,
            allow_thinking_compatibility_fallback=False,
        )
        text = str(response.get("text") or "")
        provider_payload = {
            **base,
            "response_id": response.get("response_id"),
            "provider_status": response.get("status"),
            "requested_model_returned": response.get("requested_model"),
            "resolved_model": response.get("resolved_model"),
            "thinking_requested": response.get("thinking_requested"),
            "thinking_effective": response.get("thinking_effective"),
            "thinking_compatibility_fallback": response.get("thinking_compatibility_fallback"),
            "usage": response.get("usage") or {},
            "text": text,
            "text_sha256": sha_text(text) if text else "",
        }
        write_json(provider_response_path, provider_payload)
        require(str(response.get("requested_model") or "") == MODEL, "requested model drift")
        require(str(response.get("resolved_model") or "") == RESOLVED, "resolved model drift")
        require(response.get("thinking_compatibility_fallback") is False, "thinking compatibility fallback")
        require(bool(text.strip()), "no assistant text")
        raw_sha, raw_path = archive_raw(text)
        action_sig, next_goal, parse_recovered = parse_output(text)
        result = {
            **base,
            "status": "complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "provider_response_path": str(provider_response_path),
            "provider_response_sha256": sha_file(provider_response_path),
            "response_id": response.get("response_id"),
            "provider_status": response.get("status"),
            "resolved_model": response.get("resolved_model"),
            "usage": response.get("usage") or {},
            "raw_text_path": str(raw_path),
            "raw_text_sha256": raw_sha,
            "action_signature": action_sig,
            "next_goal_sha256": sha_text(next_goal) if next_goal else "",
            "parse_recovered": parse_recovered,
        }
        write_json(case_path, result)
        return result
    except ArkResponseStateError as error:
        result = {
            **base,
            "status": "provider_response_state_failure",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "failure_type": type(error).__name__,
            "provider_receipt": error.receipt(),
        }
        write_json(case_path, result)
        append_jsonl(RUN_ROOT / "failures.jsonl", result)
        return result
    except Exception as error:
        result = {
            **base,
            "status": "provider_model_parse_or_runtime_failure",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "failure_type": type(error).__name__,
            "failure_message": str(error)[:1800],
            "provider_response_path": str(provider_response_path) if provider_response_path.exists() else "",
            "provider_response_sha256": sha_file(provider_response_path) if provider_response_path.exists() else "",
        }
        if response is not None:
            result["resolved_model"] = response.get("resolved_model")
            result["response_id"] = response.get("response_id")
        write_json(case_path, result)
        append_jsonl(RUN_ROOT / "failures.jsonl", result)
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-new-cases", type=int, default=24)
    args = parser.parse_args()
    require(args.max_new_cases >= 1, "max-new-cases must be positive")
    require(MANIFEST.is_file() and SCHEDULE.is_file(), "pilot manifest/schedule missing")
    manifest = read_json(MANIFEST)
    require(manifest["expected_provider_calls"] == 312, "manifest geometry drift")
    require(manifest["confirmatory_full_authorized"] is False, "confirmatory authority drift")
    require(manifest["model"]["requested"] == MODEL and manifest["model"]["expected_resolved"] == RESOLVED, "model manifest drift")
    require(manifest["schedule_sha256"] == sha_file(SCHEDULE), "schedule hash drift")
    require(git(["rev-parse", "HEAD"]) == manifest["git_sha"], "git SHA drift from frozen manifest")
    require(not git(["status", "--porcelain"]), "worktree must remain clean during scientific execution")
    require(CANONICAL_ENV.is_file(), "canonical provider env unavailable")

    lock_path = RUN_ROOT / ".pilot.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "TRANSACTION_ALREADY_RUNNING", "new_provider_posts": 0}))
            return 3

        schedule = load_schedule()
        completed, failed, _ = current_case_state(schedule)
        if failed:
            update_progress(schedule, "HOLD_EXISTING_FAILURE")
            print(json.dumps({"status": "HOLD_EXISTING_FAILURE", "completed": len(completed), "failed": len(failed), "new_provider_posts": 0}))
            return 4
        if len(completed) == len(schedule):
            update_progress(schedule, "EXECUTION_COMPLETE_AWAITING_ANALYSIS")
            print(json.dumps({"status": "EXECUTION_COMPLETE_AWAITING_ANALYSIS", "completed": len(completed), "new_provider_posts": 0}))
            return 0

        load_env_file(CANONICAL_ENV)
        raw = ArkSettings.from_env()
        settings = ArkSettings(
            api_key=raw.api_key,
            base_url=raw.base_url,
            default_model=raw.default_model,
            timeout_seconds=180.0,
            max_retries=0,
        )
        client = ArkResponsesClient(settings)

        new_cases = 0
        for row in schedule:
            case_path = RUN_ROOT / "per_case" / f"{row['case_id']}.json"
            if case_path.exists():
                continue
            if new_cases >= args.max_new_cases:
                break
            result = execute_case(client, row)
            new_cases += 1
            if result["status"] != "complete":
                update_progress(schedule, "HOLD_EXECUTION_FAILURE")
                print(json.dumps({
                    "status": "HOLD_EXECUTION_FAILURE",
                    "case_id": result["case_id"],
                    "failure_type": result.get("failure_type"),
                    "new_provider_posts": new_cases,
                }, ensure_ascii=False))
                return 5
            update_progress(schedule, "RUNNING")

        completed, failed, _ = current_case_state(schedule)
        if failed:
            status = "HOLD_EXECUTION_FAILURE"
        elif len(completed) == len(schedule):
            status = "EXECUTION_COMPLETE_AWAITING_ANALYSIS"
        else:
            status = "PARTIAL_RESUMABLE"
        update_progress(schedule, status)
        print(json.dumps({
            "status": status,
            "completed": len(completed),
            "expected": len(schedule),
            "failed": len(failed),
            "new_provider_posts": new_cases,
        }, ensure_ascii=False))
        return 0 if status != "HOLD_EXECUTION_FAILURE" else 5


if __name__ == "__main__":
    raise SystemExit(main())
