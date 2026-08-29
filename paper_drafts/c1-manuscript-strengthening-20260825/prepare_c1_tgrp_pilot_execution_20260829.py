from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = HERE / "c1-transport-guided-repair-pilot-contract-20260828.json"
FREEZE = HERE / "c1-transport-guided-repair-pilot-freeze-20260828.json"
PREFLIGHT = HERE / "c1-transport-guided-repair-data-preflight-20260828.json"
AUTH = HERE / "c1-tgrp-pilot-human-authorization-20260829.json"
SUPPORT = HERE / "c1-tgrp-provider-support-requalification-20260829.json"
RECONCILIATION = HERE / "c1-r7-engineering-version-reconciliation-20260829.json"
SMOKE_RECEIPT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-smoke-v1/smoke-receipt.json")
B10_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824")
B10_CONTRACT = B10_ROOT / "b10-contract.json"
RUN_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-pilot-v1")

EXPECTED = {
    CONTRACT: "38c6cceee240ebb523c226fc370b6a03d6f4080c890c8fb49fec8d86a94488af",
    FREEZE: "478251986c2e54dabafc2980504693c706515fed5badd4aebc4b20140a23245d",
    PREFLIGHT: "aff2b75f06847e924d967674c6df870df889baf50cc6beea71e68dc201e92b0a",
    B10_CONTRACT: "c2a54c928d74ccb7a153166a02ef0ef7a1504a93b5895952380a95b0277a3436",
}

ARMS = ("A0_NATIVE", "A1_MEMORY_BLIND_DECISION_CHECK", "A2_MEMORY_USE_CHECK")
BRANCHES = ("success_memory", "failure_memory")
ROLLOUTS = (1, 2, 3, 4)
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def native_prompt(system: str, task: str, state: str, memory: str) -> str:
    return (
        f"SYSTEM INSTRUCTION:\n{system}\n\n"
        f"REUSABLE MEMORY:\n{memory.strip()}\n\n"
        f"ULTIMATE TASK:\n{task}\n\n"
        f"CURRENT BROWSER STATE:\n{state}\n\n"
        "Choose the next browser-agent action now. Return only the JSON object required by the system instruction."
    )


def intervention_prompt(system: str, task: str, state: str, memory: str, clause: str) -> str:
    return (
        f"SYSTEM INSTRUCTION:\n{system}\n\n"
        f"REUSABLE MEMORY:\n{memory.strip()}\n\n"
        f"ULTIMATE TASK:\n{task}\n\n"
        f"CURRENT BROWSER STATE:\n{state}\n\n"
        f"DECISION CHECK:\n{clause}\n\n"
        "Choose the next browser-agent action now. Return only the JSON object required by the system instruction."
    )


def main() -> int:
    for path, expected in EXPECTED.items():
        require(path.is_file(), f"missing frozen input:{path}")
        require(sha_file(path) == expected, f"frozen input drift:{path}")

    require(AUTH.is_file() and SUPPORT.is_file() and RECONCILIATION.is_file() and SMOKE_RECEIPT.is_file(), "authorization/support/reconciliation/smoke missing")
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    smoke = json.loads(SMOKE_RECEIPT.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    b10 = json.loads(B10_CONTRACT.read_text(encoding="utf-8"))

    require(auth["authority"]["experiment_pilot"] is True and auth["authority"]["provider_pilot"] is True, "pilot authority absent")
    require(auth["authority"]["confirmatory_full"] is False, "confirmatory authority must remain false")
    require(support["status"] == "SUPPORT_PASS", "provider support not qualified")
    require(smoke["status"] == "PASS_ZERO_PROVIDER_ENGINEERING_SMOKE_ONLY", "fresh smoke not qualified")
    require((smoke.get("checks") or {}).get("provider_calls") == 0 and (smoke.get("checks") or {}).get("model_actions") == 0, "fresh smoke authority drift")
    require((support.get("response") or {}).get("resolved_model") == RESOLVED, "support resolved-model drift")
    require((support.get("response") or {}).get("thinking_compatibility_fallback") is False, "support thinking fallback")
    require(preflight["status"] == "OFFLINE_PACKET_REPLAY_PREFLIGHT_PASS_NO_EXECUTION_AUTHORITY", "preflight drift")
    require(freeze["status"] == "PILOT_PROTOCOL_FROZEN_EXECUTION_LOCKED", "freeze status drift")
    require(freeze["execution_geometry"]["pilot_provider_calls_if_authorized"] == 312, "pilot geometry drift")
    require(freeze["model"]["requested"] == MODEL and freeze["model"]["expected_resolved"] == RESOLVED, "model freeze drift")

    current_branch = git(["branch", "--show-current"])
    head = git(["rev-parse", "HEAD"])
    require(current_branch == "experiment/c1-tgrp-pilot-20260829", f"wrong branch:{current_branch}")
    require(not git(["status", "--porcelain"]), "worktree must be clean before scientific manifest freeze")

    require(not RUN_ROOT.exists(), f"run root already exists:{RUN_ROOT}")

    vendor = Path(b10["vendor_path"])
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq

    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    require(parquet.is_file() and sha_file(parquet) == b10["source_bindings"]["parquet"]["sha256"], "parquet drift")
    raw_rows = {int(r["task_id"]): r for r in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()}
    b10_units = {int(u["future_task"]): u for u in b10["task_units"]}
    preflight_rows = {int(r["future_task"]): r for r in preflight["rows"]}

    clauses = {row["id"]: row.get("clause", "") for row in contract["design"]["arms"]}
    a1_clause = clauses["A1_MEMORY_BLIND_DECISION_CHECK"]
    a2_clause = clauses["A2_MEMORY_USE_CHECK"]

    pilot_units = list(freeze["selection"]["pilot"])
    require(len(pilot_units) == 13, "pilot unit count drift")
    holdout_units = list(freeze["selection"]["confirmatory_holdout"])
    require(len(holdout_units) == 23, "holdout unit count drift")
    require(not ({int(x["future_task"]) for x in pilot_units} & {int(x["future_task"]) for x in holdout_units}), "pilot/holdout overlap")

    case_inputs: dict[tuple[int, str, str], dict[str, Any]] = {}
    input_index: list[dict[str, Any]] = []
    for frozen in pilot_units:
        task_id = int(frozen["future_task"])
        unit = b10_units[task_id]
        pf = preflight_rows[task_id]
        row = raw_rows[task_id]
        task = str(row["task_prompt"])
        trajectory = json.loads(str(row["trajectory_json"]))
        step = (trajectory.get("steps") or {}).get("1")
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        system = str(contents[0].get("content") or "")
        last = str(contents[-1].get("content") or "")
        marker = "[Current state starts here]"
        require(marker in last, f"state marker missing:{task_id}")
        state = last.split(marker, 1)[1].strip()
        require(sha_text(task) == frozen["task_prompt_sha256"] == unit["task_prompt_sha256"], f"task hash drift:{task_id}")
        require(sha_text(system) == frozen["system_instruction_sha256"] == unit["system_instruction_sha256"], f"system hash drift:{task_id}")
        require(sha_text(state) == frozen["current_state_sha256"] == unit["current_state_sha256"], f"state hash drift:{task_id}")
        require(int(unit["selected_source_task"]) == int(frozen["selected_source_task"]), f"source task drift:{task_id}")

        for branch in BRANCHES:
            key = "success" if branch == "success_memory" else "failure"
            wrapper = Path(unit["memory_wrappers"][key]["path"])
            require(wrapper.is_file(), f"wrapper missing:{task_id}/{branch}")
            require(sha_file(wrapper) == unit["memory_wrappers"][key]["sha256"], f"wrapper hash drift:{task_id}/{branch}")
            require(sha_file(wrapper) == frozen[f"{key}_memory_wrapper_sha256"], f"freeze wrapper drift:{task_id}/{branch}")
            memory = wrapper.read_text(encoding="utf-8")
            prompts = {
                "A0_NATIVE": native_prompt(system, task, state, memory),
                "A1_MEMORY_BLIND_DECISION_CHECK": intervention_prompt(system, task, state, memory, a1_clause),
                "A2_MEMORY_USE_CHECK": intervention_prompt(system, task, state, memory, a2_clause),
            }
            for arm, prompt in prompts.items():
                expected_prompt_hash = pf["prompt_sha256"][key][arm]
                require(sha_text(prompt) == expected_prompt_hash, f"prompt hash drift:{task_id}/{branch}/{arm}")
                payload = {
                    "future_task": task_id,
                    "intent_template_id": int(frozen["intent_template_id"]),
                    "selected_source_task": int(frozen["selected_source_task"]),
                    "arm": arm,
                    "branch": branch,
                    "system_instruction_sha256": sha_text(system),
                    "task_prompt_sha256": sha_text(task),
                    "current_state_sha256": sha_text(state),
                    "memory_wrapper_sha256": sha_file(wrapper),
                    "prompt_sha256": sha_text(prompt),
                    "prompt": prompt,
                }
                case_inputs[(task_id, arm, branch)] = payload
                input_index.append({k: v for k, v in payload.items() if k != "prompt"})

    schedule: list[dict[str, Any]] = []
    for rollout in ROLLOUTS:
        for state_index, frozen in enumerate(pilot_units):
            task_id = int(frozen["future_task"])
            rotation = (state_index + rollout - 1) % len(ARMS)
            arm_order = list(ARMS[rotation:] + ARMS[:rotation])
            for arm_pos, arm in enumerate(arm_order):
                branch_order = list(BRANCHES if (state_index + rollout + arm_pos) % 2 == 0 else tuple(reversed(BRANCHES)))
                for branch in branch_order:
                    case_id = f"task-{task_id}__{arm}__{branch}__r{rollout}"
                    input_file = RUN_ROOT / "inputs" / f"{case_id}.json"
                    payload = {**case_inputs[(task_id, arm, branch)], "rollout": rollout, "case_id": case_id}
                    schedule.append({
                        "order": len(schedule) + 1,
                        "case_id": case_id,
                        "future_task": task_id,
                        "intent_template_id": int(frozen["intent_template_id"]),
                        "selected_source_task": int(frozen["selected_source_task"]),
                        "arm": arm,
                        "branch": branch,
                        "rollout": rollout,
                        "input_file": str(input_file),
                        "prompt_sha256": payload["prompt_sha256"],
                    })
                    write_json(input_file, payload)

    require(len(schedule) == 312, "schedule length drift")
    require(len({r["case_id"] for r in schedule}) == 312, "duplicate case id")

    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    (RUN_ROOT / "per_case").mkdir(exist_ok=True)
    (RUN_ROOT / "provider-responses").mkdir(exist_ok=True)
    (RUN_ROOT / "raw").mkdir(exist_ok=True)
    schedule_path = RUN_ROOT / "schedule.jsonl"
    input_index_path = RUN_ROOT / "input-index.jsonl"
    write_jsonl(schedule_path, schedule)
    write_jsonl(input_index_path, input_index)
    (RUN_ROOT / "failures.jsonl").write_text("", encoding="utf-8")

    manifest = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TGRP_PILOT_RUN_MANIFEST",
        "run_id": RUN_ROOT.name,
        "paper_id": contract["paper_id"],
        "experiment_id": contract["experiment_id"],
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "design_base": contract["canonical_base"],
        "execution_base": auth["execution_base"],
        "git_sha": head,
        "branch": current_branch,
        "authority_sha256": sha_file(AUTH),
        "support_requalification_sha256": sha_file(SUPPORT),
        "fresh_smoke_receipt_sha256": sha_file(SMOKE_RECEIPT),
        "fresh_smoke_run_id": smoke["run_id"],
        "pilot_contract_sha256": sha_file(CONTRACT),
        "pilot_freeze_sha256": sha_file(FREEZE),
        "data_preflight_sha256": sha_file(PREFLIGHT),
        "version_reconciliation_sha256": sha_file(RECONCILIATION),
        "b10_contract_sha256": sha_file(B10_CONTRACT),
        "pilot_state_count": 13,
        "pilot_state_ids": [int(x["future_task"]) for x in pilot_units],
        "pilot_ids_sha256": freeze["selection"]["pilot_ids_sha256"],
        "confirmatory_holdout_count": 23,
        "confirmatory_holdout_ids_sha256": freeze["selection"]["holdout_ids_sha256"],
        "confirmatory_full_authorized": False,
        "arms": list(ARMS),
        "branches": list(BRANCHES),
        "rollouts_per_branch_per_arm_per_state": 4,
        "expected_provider_calls": 312,
        "execution_order": "For rollout 1..4 and frozen pilot-state order, rotate A0/A1/A2 by (state_index+rollout-1) mod 3; alternate success/failure branch order by parity. This schedule is frozen before provider execution and never depends on outcomes.",
        "schedule_sha256": sha_file(schedule_path),
        "input_index_sha256": sha_file(input_index_path),
        "model": {
            "requested": MODEL,
            "expected_resolved": RESOLVED,
            "temperature": 0.2,
            "max_output_tokens": 900,
            "thinking": "disabled",
            "provider_retries": 0,
            "substitution_allowed": False,
            "thinking_compatibility_fallback_allowed": False,
        },
        "clauses": {
            "A1_MEMORY_BLIND_DECISION_CHECK": {"text": a1_clause, "sha256": sha_text(a1_clause)},
            "A2_MEMORY_USE_CHECK": {"text": a2_clause, "sha256": sha_text(a2_clause)},
        },
        "parser": {
            "semantics": "Exact B10 action_signature semantics: first structured action name; click_element includes index; strict JSON extraction with the frozen regex fallback.",
            "historical_b10_result_sha256": "e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6",
        },
        "missingness": {
            "provider_retries": 0,
            "replace_units": False,
            "top_up_failed_units": False,
            "impute": False,
            "stop_after_first_provider_model_or_parse_failure": True,
        },
        "artifact_paths": {
            "inputs": str(RUN_ROOT / "inputs"),
            "per_case": str(RUN_ROOT / "per_case"),
            "provider_responses": str(RUN_ROOT / "provider-responses"),
            "raw": str(RUN_ROOT / "raw"),
            "progress": str(RUN_ROOT / "progress.json"),
            "heartbeat": str(RUN_ROOT / "heartbeat.json"),
            "resume": str(RUN_ROOT / "resume.json"),
            "failures": str(RUN_ROOT / "failures.jsonl"),
        },
        "scientific_boundary": "Pilot only. No terminal outcome repair and no 23-state confirmatory execution. A pilot PASS authorizes only a recommendation to request future confirmatory authority.",
    }
    manifest_path = RUN_ROOT / "run-manifest.json"
    write_json(manifest_path, manifest)
    write_json(RUN_ROOT / "progress.json", {"status": "READY", "completed": 0, "expected": 312, "failed": 0, "provider_posts": 0})
    write_json(RUN_ROOT / "heartbeat.json", {"status": "READY", "updated_at": datetime.now(timezone.utc).isoformat()})
    write_json(RUN_ROOT / "resume.json", {"next_order": 1, "completed_case_ids": [], "failed_case_ids": []})

    print(json.dumps({
        "status": "PILOT_MANIFEST_FROZEN_READY_FOR_EXECUTION",
        "run_root": str(RUN_ROOT),
        "git_sha": head,
        "cases": len(schedule),
        "schedule_sha256": manifest["schedule_sha256"],
        "support_sha256": manifest["support_requalification_sha256"],
        "provider_calls": 0,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
