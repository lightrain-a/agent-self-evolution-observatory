from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "c1-transport-guided-repair-pilot-contract-20260828.json"
PREFLIGHT = HERE / "c1-transport-guided-repair-data-preflight-20260828.json"
B10_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824")
B10_CONTRACT = B10_ROOT / "b10-contract.json"
B10_RESULT = B10_ROOT / "b10-result.json"
RUN_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-smoke-v1")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def native_prompt(system: str, task: str, state: str, memory: str) -> str:
    mem = memory.strip() if memory.strip() else "No reusable memory is available for this decision."
    return (
        f"SYSTEM INSTRUCTION:\n{system}\n\n"
        f"REUSABLE MEMORY:\n{mem}\n\n"
        f"ULTIMATE TASK:\n{task}\n\n"
        f"CURRENT BROWSER STATE:\n{state}\n\n"
        "Choose the next browser-agent action now. Return only the JSON object required by the system instruction."
    )


def intervention_prompt(system: str, task: str, state: str, memory: str, clause: str) -> str:
    mem = memory.strip() if memory.strip() else "No reusable memory is available for this decision."
    return (
        f"SYSTEM INSTRUCTION:\n{system}\n\n"
        f"REUSABLE MEMORY:\n{mem}\n\n"
        f"ULTIMATE TASK:\n{task}\n\n"
        f"CURRENT BROWSER STATE:\n{state}\n\n"
        f"DECISION CHECK:\n{clause}\n\n"
        "Choose the next browser-agent action now. Return only the JSON object required by the system instruction."
    )


def extract_json_object_local(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
        require(isinstance(payload, dict), "archived output is not a JSON object")
        return payload
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        require(start >= 0 and end > start, "no JSON object found in archived output")
        payload = json.loads(cleaned[start : end + 1])
        require(isinstance(payload, dict), "extracted archived output is not a JSON object")
        return payload


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
    return str(name)


def parse_action_signature(text: str) -> str:
    try:
        return action_signature(extract_json_object_local(text))
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
            return f"click_element:{index.group(1)}"
        return name


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    b10 = json.loads(B10_CONTRACT.read_text(encoding="utf-8"))
    b10_result = json.loads(B10_RESULT.read_text(encoding="utf-8"))
    require(preflight["status"] == "OFFLINE_PACKET_REPLAY_PREFLIGHT_PASS_NO_EXECUTION_AUTHORITY", "preflight not qualified")
    require(not any(contract["authority"].values()), "pilot contract unexpectedly carries authority")

    unit = sorted(b10["task_units"], key=lambda row: int(row["future_task"]))[0]
    future_task = int(unit["future_task"])
    source_task = int(unit["selected_source_task"])
    row = next(row for row in preflight["rows"] if int(row["future_task"]) == future_task)

    vendor = Path(b10["vendor_path"])
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq  # type: ignore

    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    source_rows = {int(item["task_id"]): item for item in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()}
    source = source_rows[future_task]
    task = str(source["task_prompt"])
    trajectory = json.loads(str(source["trajectory_json"]))
    contents = ((((trajectory.get("steps") or {}).get("1") or {}).get("input_messages") or {}).get("contents") or [])
    system = str(contents[0].get("content") or "")
    last = str(contents[-1].get("content") or "")
    marker = "[Current state starts here]"
    require(marker in last, "current-state marker missing")
    state = last.split(marker, 1)[1].strip()
    require(sha_text(task) == unit["task_prompt_sha256"], "task hash drift")
    require(sha_text(system) == unit["system_instruction_sha256"], "system hash drift")
    require(sha_text(state) == unit["current_state_sha256"], "state hash drift")

    arms = {arm["id"]: arm for arm in contract["design"]["arms"]}
    a1_clause = arms["A1_MEMORY_BLIND_DECISION_CHECK"]["clause"]
    a2_clause = arms["A2_MEMORY_USE_CHECK"]["clause"]

    started_at = datetime.now(timezone.utc).isoformat()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "run_id": RUN_ROOT.name,
        "paper": contract["paper_id"],
        "experiment_id": contract["experiment_id"],
        "scientific_question": contract["scientific_question"],
        "server": "69",
        "working_directory": str(HERE),
        "git_base_sha": contract["canonical_base"],
        "branch": "research/c1-transport-governance-20260828",
        "smoke_script_sha256": sha_file(Path(__file__)),
        "pilot_contract_sha256": sha_file(CONTRACT),
        "data_preflight_sha256": sha_file(PREFLIGHT),
        "b10_contract_sha256": sha_file(B10_CONTRACT),
        "b10_result_sha256": sha_file(B10_RESULT),
        "gpu": "none",
        "provider_calls_allowed": False,
        "model_actions_allowed": False,
        "started_at": started_at,
        "log_path": str(RUN_ROOT / "smoke.log"),
        "cases_path": str(RUN_ROOT / "cases.jsonl"),
        "progress_path": str(RUN_ROOT / "progress.json"),
        "receipt_path": str(RUN_ROOT / "smoke-receipt.json"),
        "resume": f"python3 {Path(__file__)}",
        "completion_condition": "packet-structure checks and archived-parser replay pass with zero provider/model execution",
        "failure_policy": "fail closed; no scientific interpretation",
        "selected_smoke_unit_rule": "lowest future_task in the frozen 36-unit B10 contract",
        "selected_future_task": future_task,
        "selected_source_task": source_task,
    }
    write_json(RUN_ROOT / "manifest.json", manifest)
    write_json(RUN_ROOT / "progress.json", {"status": "STARTED", "completed_cases": 0, "provider_calls": 0, "model_actions": 0})
    (RUN_ROOT / "cases.jsonl").write_text("", encoding="utf-8")
    (RUN_ROOT / "smoke.log").write_text(f"{started_at} zero-provider engineering smoke started\n", encoding="utf-8")

    prompt_cases = 0
    for branch, condition in (("success", "success_memory"), ("failure", "failure_memory")):
        wrapper = Path(unit["memory_wrappers"][branch]["path"])
        require(wrapper.is_file() and sha_file(wrapper) == unit["memory_wrappers"][branch]["sha256"], f"wrapper drift:{branch}")
        memory = wrapper.read_text(encoding="utf-8")
        a0 = native_prompt(system, task, state, memory)
        a1 = intervention_prompt(system, task, state, memory, a1_clause)
        a2 = intervention_prompt(system, task, state, memory, a2_clause)
        require(sha_text(a0) == row["prompt_sha256"][branch]["A0_NATIVE"], f"A0 replay drift:{branch}")
        require(sha_text(a1) == row["prompt_sha256"][branch]["A1_MEMORY_BLIND_DECISION_CHECK"], f"A1 replay drift:{branch}")
        require(sha_text(a2) == row["prompt_sha256"][branch]["A2_MEMORY_USE_CHECK"], f"A2 replay drift:{branch}")
        require(a1.replace(a1_clause, "<DECISION_CHECK>") == a2.replace(a2_clause, "<DECISION_CHECK>"), f"A1/A2 non-clause packet drift:{branch}")
        upstream = {
            "system_instruction_sha256": sha_text(system),
            "task_prompt_sha256": sha_text(task),
            "current_state_sha256": sha_text(state),
            "memory_wrapper_sha256": sha_file(wrapper),
        }
        for arm_id, prompt in (("A0_NATIVE", a0), ("A1_MEMORY_BLIND_DECISION_CHECK", a1), ("A2_MEMORY_USE_CHECK", a2)):
            append_jsonl(
                RUN_ROOT / "cases.jsonl",
                {
                    "case_type": "prompt_packet",
                    "future_task": future_task,
                    "selected_source_task": source_task,
                    "branch": branch,
                    "arm": arm_id,
                    "upstream": upstream,
                    "prompt_sha256": sha_text(prompt),
                    "provider_calls": 0,
                    "model_actions": 0,
                },
            )
            prompt_cases += 1

    expected_rollouts = {
        (int(row["future_task"]), str(row["condition"]), int(row["rollout"])): str(row["action_signature"])
        for row in b10_result["rollouts"]
        if int(row["future_task"]) == future_task
    }
    parser_checks = 0
    for condition in ("success_memory", "failure_memory", "no_memory"):
        for rollout in range(1, 5):
            archived = B10_ROOT / "private" / "provider-responses" / f"first-action-{future_task}-source-{source_task}-{condition}-r{rollout}.json"
            require(archived.is_file(), f"archived response missing:{archived.name}")
            payload = json.loads(archived.read_text(encoding="utf-8"))
            parsed = parse_action_signature(str(payload.get("text") or ""))
            expected = expected_rollouts[(future_task, condition, rollout)]
            require(parsed == expected, f"archived parser replay drift:{condition}/r{rollout}: {parsed} != {expected}")
            append_jsonl(
                RUN_ROOT / "cases.jsonl",
                {
                    "case_type": "archived_parser_replay",
                    "future_task": future_task,
                    "condition": condition,
                    "rollout": rollout,
                    "archived_response_sha256": sha_file(archived),
                    "action_signature": parsed,
                    "matches_frozen_result": True,
                    "provider_calls": 0,
                    "model_actions": 0,
                },
            )
            parser_checks += 1

    write_json(RUN_ROOT / "progress.json", {"status": "COMPLETE", "completed_cases": prompt_cases + parser_checks, "provider_calls": 0, "model_actions": 0})
    receipt = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TRANSPORT_GUIDED_REPAIR_ZERO_PROVIDER_SMOKE",
        "run_id": RUN_ROOT.name,
        "status": "PASS_ZERO_PROVIDER_ENGINEERING_SMOKE_ONLY",
        "selected_future_task": future_task,
        "selected_source_task": source_task,
        "checks": {
            "frozen_upstream_packet_hashes_verified": True,
            "native_A0_prompt_exact_replay": True,
            "A1_A2_identical_outside_decision_check_clause": True,
            "prompt_packet_cases": prompt_cases,
            "archived_first_action_parser_replays": parser_checks,
            "archived_parser_matches_frozen_result": True,
            "append_safe_cases_materialized": True,
            "progress_and_resume_materialized": True,
            "provider_calls": 0,
            "model_actions": 0,
            "new_scientific_outcomes": 0,
        },
        "manifest_sha256": sha_file(RUN_ROOT / "manifest.json"),
        "cases_sha256": sha_file(RUN_ROOT / "cases.jsonl"),
        "progress_sha256": sha_file(RUN_ROOT / "progress.json"),
        "scientific_interpretation": "None. Smoke PASS validates packet construction, artifact persistence, and archived parser replay only. It does not support the A2 treatment, uptake, outcome, or repair efficacy.",
        "next_gate": "Pilot remains unauthorized. Before any new model/provider call, require explicit current experiment/provider authority and freeze pilot subset plus inference rule.",
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    write_json(RUN_ROOT / "smoke-receipt.json", receipt)
    with (RUN_ROOT / "smoke.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now(timezone.utc).isoformat()} smoke PASS; provider_calls=0; model_actions=0\n")
    print(json.dumps({"status": receipt["status"], "future_task": future_task, "prompt_cases": prompt_cases, "parser_checks": parser_checks, "provider_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
