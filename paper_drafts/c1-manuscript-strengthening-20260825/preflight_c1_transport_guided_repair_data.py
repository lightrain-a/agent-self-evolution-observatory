from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
B10_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824")
B10_CONTRACT = B10_ROOT / "b10-contract.json"
B10_RESULT = B10_ROOT / "b10-result.json"
OUTPUT = HERE / "c1-transport-guided-repair-data-preflight-20260828.json"

A1_CLAUSE = (
    "Before choosing the next action, explicitly assess whether the ULTIMATE TASK and CURRENT BROWSER STATE "
    "together change which action should be taken. If this check is relevant, incorporate it; otherwise proceed "
    "as usual. Do not add explanation."
)
A2_CLAUSE = (
    "Before choosing the next action, explicitly assess whether the REUSABLE MEMORY and CURRENT BROWSER STATE "
    "together change which action should be taken. If this check is relevant, incorporate it; otherwise proceed "
    "as usual. Do not add explanation."
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


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


def main() -> int:
    contract = json.loads(B10_CONTRACT.read_text(encoding="utf-8"))
    result = json.loads(B10_RESULT.read_text(encoding="utf-8"))

    require(contract["experiment_id"] == "D2-PROXY-B10-NATIVE-FIRST-ACTION-TRANSPORT", "B10 contract identity drift")
    require(result["experiment_id"] == contract["experiment_id"], "B10 result identity drift")
    require(len(contract["task_units"]) == 36, "B10 task-unit count drift")
    require(len(result["cell_results"]) == 36, "B10 result-cell count drift")
    require(result["summary"]["provider_calls_complete"] == 432, "B10 archived execution incomplete")
    require(result["summary"]["provider_failures_or_parse_failures"] == 0, "B10 archived execution has failures")

    parquet = Path(contract["source_bindings"]["parquet"]["path"])
    require(parquet.is_file(), "bound parquet missing")
    require(sha_file(parquet) == contract["source_bindings"]["parquet"]["sha256"], "bound parquet hash drift")

    vendor = Path(contract["vendor_path"])
    require(vendor.is_dir(), "bound vendor path missing")
    sys.path.insert(0, str(vendor))
    import pyarrow.parquet as pq  # type: ignore

    raw = {
        int(row["task_id"]): row
        for row in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()
    }
    result_cells = {int(row["future_task"]): row for row in result["cell_results"]}

    rows: list[dict[str, Any]] = []
    wrapper_count = 0
    archived_prompt_checks = 0
    for unit in sorted(contract["task_units"], key=lambda row: int(row["future_task"])):
        future_task = int(unit["future_task"])
        source_task = int(unit["selected_source_task"])
        require(future_task in raw, f"future task missing from parquet:{future_task}")
        require(future_task in result_cells, f"future task missing from B10 result:{future_task}")
        require(int(result_cells[future_task]["selected_source_task"]) == source_task, f"source-task drift:{future_task}")

        source_row = raw[future_task]
        task = str(source_row["task_prompt"])
        require(sha_text(task) == unit["task_prompt_sha256"], f"task-prompt hash drift:{future_task}")
        trajectory = json.loads(str(source_row["trajectory_json"]))
        step = (trajectory.get("steps") or {}).get("1")
        require(isinstance(step, dict), f"step-1 missing:{future_task}")
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        require(len(contents) >= 2, f"input-message contents missing:{future_task}")
        system = str(contents[0].get("content") or "")
        last = str(contents[-1].get("content") or "")
        marker = "[Current state starts here]"
        require(marker in last, f"current-state marker missing:{future_task}")
        state = last.split(marker, 1)[1].strip()
        require(sha_text(system) == unit["system_instruction_sha256"], f"system hash drift:{future_task}")
        require(sha_text(state) == unit["current_state_sha256"], f"state hash drift:{future_task}")

        prompt_hashes: dict[str, dict[str, str]] = {}
        wrapper_hashes: dict[str, str] = {}
        for branch, archived_condition in (("success", "success_memory"), ("failure", "failure_memory")):
            wrapper_ref = unit["memory_wrappers"][branch]
            wrapper_path = Path(wrapper_ref["path"])
            require(wrapper_path.is_file(), f"memory wrapper missing:{future_task}/{branch}")
            require(sha_file(wrapper_path) == wrapper_ref["sha256"], f"memory wrapper hash drift:{future_task}/{branch}")
            wrapper_count += 1
            memory = wrapper_path.read_text(encoding="utf-8")
            wrapper_hashes[branch] = wrapper_ref["sha256"]

            a0 = native_prompt(system, task, state, memory)
            a1 = intervention_prompt(system, task, state, memory, A1_CLAUSE)
            a2 = intervention_prompt(system, task, state, memory, A2_CLAUSE)
            require(a0 != a1 and a0 != a2 and a1 != a2, f"arm prompt collision:{future_task}/{branch}")

            archived_hashes = set()
            for rollout in range(1, 5):
                response_path = B10_ROOT / "private" / "provider-responses" / (
                    f"first-action-{future_task}-source-{source_task}-{archived_condition}-r{rollout}.json"
                )
                require(response_path.is_file(), f"archived provider response missing:{response_path.name}")
                response = json.loads(response_path.read_text(encoding="utf-8"))
                archived_hashes.add(str(response["prompt_sha256"]))
                archived_prompt_checks += 1
            require(len(archived_hashes) == 1, f"archived prompt hash varies across rollouts:{future_task}/{branch}")
            require(next(iter(archived_hashes)) == sha_text(a0), f"native prompt replay mismatch:{future_task}/{branch}")

            prompt_hashes[branch] = {
                "A0_NATIVE": sha_text(a0),
                "A1_MEMORY_BLIND_DECISION_CHECK": sha_text(a1),
                "A2_MEMORY_USE_CHECK": sha_text(a2),
            }

        rows.append(
            {
                "future_task": future_task,
                "selected_source_task": source_task,
                "intent_template_id": int(unit["intent_template_id"]),
                "task_prompt_sha256": unit["task_prompt_sha256"],
                "system_instruction_sha256": unit["system_instruction_sha256"],
                "current_state_sha256": unit["current_state_sha256"],
                "memory_wrapper_sha256": wrapper_hashes,
                "prompt_sha256": prompt_hashes,
            }
        )

    future_tasks = [row["future_task"] for row in rows]
    require(len(set(future_tasks)) == 36, "future-task uniqueness drift")
    require(wrapper_count == 72, "wrapper count drift")
    require(archived_prompt_checks == 288, "archived prompt-check count drift")

    clause_stats = {
        "A1_MEMORY_BLIND_DECISION_CHECK": {"chars": len(A1_CLAUSE), "words": len(A1_CLAUSE.split()), "sha256": sha_text(A1_CLAUSE)},
        "A2_MEMORY_USE_CHECK": {"chars": len(A2_CLAUSE), "words": len(A2_CLAUSE.split()), "sha256": sha_text(A2_CLAUSE)},
    }
    require(abs(clause_stats["A1_MEMORY_BLIND_DECISION_CHECK"]["words"] - clause_stats["A2_MEMORY_USE_CHECK"]["words"]) <= 1, "decision-check word-count mismatch")
    require(abs(clause_stats["A1_MEMORY_BLIND_DECISION_CHECK"]["chars"] - clause_stats["A2_MEMORY_USE_CHECK"]["chars"]) <= 16, "decision-check character-count mismatch")

    output = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TRANSPORT_GUIDED_REPAIR_DATA_PREFLIGHT",
        "paper_id": contract["paper_id"],
        "experiment_id": "C1-TGRP-P0-POSTEXPOSURE-UPTAKE-20260828",
        "generated_at": "2026-08-28",
        "status": "OFFLINE_PACKET_REPLAY_PREFLIGHT_PASS_NO_EXECUTION_AUTHORITY",
        "source": {
            "b10_contract_path": str(B10_CONTRACT),
            "b10_contract_sha256": sha_file(B10_CONTRACT),
            "b10_result_path": str(B10_RESULT),
            "b10_result_sha256": sha_file(B10_RESULT),
            "parquet_path": str(parquet),
            "parquet_sha256": sha_file(parquet),
        },
        "checks": {
            "frozen_task_units": len(rows),
            "unique_future_tasks": len(set(future_tasks)),
            "memory_wrappers_verified": wrapper_count,
            "archived_native_prompt_hash_checks": archived_prompt_checks,
            "native_prompt_exact_replay": True,
            "source_task_alignment": True,
            "system_task_state_hashes_verified": True,
            "a1_a2_clause_structure_matched": True,
            "provider_calls": 0,
            "model_actions": 0,
            "new_scientific_outcomes": 0,
        },
        "decision_check_clauses": clause_stats,
        "rows": rows,
        "scientific_interpretation": "None. This artifact establishes only that the 36 frozen B10 state packets and branch memories can be reconstructed content-addressedly and that A0 native prompts replay the archived request hashes. It does not show that the proposed A2 intervention changes uptake or outcome.",
        "next_gate": "A zero-provider engineering smoke may build append-safe run manifests and replay the first-action parser on archived outputs. Any new model/provider execution still requires explicit current authority and a qualified pilot contract.",
        "authority": {
            "scientific": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "submission": False,
        },
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "units": len(rows), "wrappers": wrapper_count, "archived_prompt_checks": archived_prompt_checks, "provider_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
