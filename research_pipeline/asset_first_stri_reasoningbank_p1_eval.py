"""SWE-Bench evaluation and per-case artifact persistence for ReasoningBank P1."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    EVALUATOR_TIMEOUT_SECONDS,
    MODEL,
    ROOT,
    DockerRun,
    execute_agent,
    sha256_text,
    utcnow,
    write_json,
)

PASSING = {"PASSED", "XFAIL"}
MAINTAINED = {"PASSED", "XFAIL", "SKIPPED"}


def parse_pytest(log: str) -> dict[str, str]:
    statuses = {"PASSED", "FAILED", "ERROR", "SKIPPED", "XFAIL", "XPASS"}
    out: dict[str, str] = {}
    for line in log.splitlines():
        if not any(line.startswith(value) for value in statuses):
            continue
        if line.startswith("FAILED"):
            line = line.replace(" - ", " ")
        parts = line.split()
        if len(parts) > 1:
            out[parts[1]] = parts[0]
    return out


def parse_sympy(log: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in log.splitlines():
        line = line.strip()
        if not line.startswith("test_"):
            continue
        if line.endswith(" E"):
            out[line.split()[0]] = "ERROR"
        elif line.endswith(" F"):
            out[line.split()[0]] = "FAILED"
        elif line.endswith(" ok"):
            out[line.split()[0]] = "PASSED"
    return out


def evaluate(container: DockerRun, fixture: dict[str, Any]) -> dict[str, Any]:
    evaluator = fixture["evaluator_only"]
    result = container.exec(evaluator["eval_script"], timeout=EVALUATOR_TIMEOUT_SECONDS)
    raw = result["output"]
    start_marker = ">>>>> Start Test Output"
    end_marker = ">>>>> End Test Output"
    valid_markers = start_marker in raw and end_marker in raw
    sliced = raw
    if valid_markers:
        sliced = raw.split(start_marker, 1)[1].split(end_marker, 1)[0]
    if evaluator["log_parser"] == "parse_log_pytest":
        status_map = parse_pytest(sliced)
    elif evaluator["log_parser"] == "parse_log_sympy":
        status_map = parse_sympy(sliced)
    else:
        raise RuntimeError(f"unsupported frozen parser {evaluator['log_parser']}")
    f2p = {case: status_map.get(case, "MISSING") for case in evaluator["FAIL_TO_PASS"]}
    p2p = {case: status_map.get(case, "MISSING") for case in evaluator["PASS_TO_PASS"]}
    all_f2p = all(value in PASSING for value in f2p.values())
    all_p2p = all(value in MAINTAINED for value in p2p.values())
    valid = valid_markers and bool(status_map) and not result["timed_out"]
    return {
        "evaluator": "SWE-bench 5.0.2-equivalent frozen pass_and_fail logic",
        "swebench_wheel_sha256": "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62",
        "eval_script_sha256": sha256_text(evaluator["eval_script"]),
        "test_patch_sha256": sha256_text(evaluator["test_patch"]),
        "log_parser": evaluator["log_parser"], "raw_execution": result,
        "status_map": status_map, "FAIL_TO_PASS": f2p, "PASS_TO_PASS": p2p,
        "valid": valid, "resolved": bool(valid and all_f2p and all_p2p),
        "all_fail_to_pass": all_f2p, "all_pass_to_pass": all_p2p,
    }


def run_case(
    fixture: dict[str, Any], *, selected_memory: str, run_id: str,
    output_dir: Path, r0: dict[str, Any],
) -> dict[str, Any]:
    container: DockerRun | None = None
    try:
        trajectory, container = execute_agent(
            fixture, selected_memory=selected_memory, run_id=run_id
        )
        trajectory["R0_representation_retrieval_state"] = copy.deepcopy(r0)
        trajectory["R4_terminal_outcome"] = evaluate(container, fixture)
        trajectory["scientific_boundary"] = {
            "gold_patch_model_visible": False, "test_patch_model_visible": False,
            "evaluator_script_model_visible": False,
        }
    except Exception as error:
        trajectory = {
            "schema_version": 1, "run_id": run_id, "created_at_utc": utcnow(),
            "instance_id": fixture["instance_id"],
            "R0_representation_retrieval_state": copy.deepcopy(r0),
            "execution_status": "IMPLEMENTATION_FAILURE",
            "failure": {
                "failure_layer": "runtime", "error_type": type(error).__name__,
                "message": str(error),
            },
            "scientific_outcome_authorized": False,
            "credential_material_present": False,
        }
    finally:
        if container is not None:
            container.close()
    out_path = output_dir / run_id / "run.json"
    file_sha = write_json(out_path, trajectory)
    return {
        "run_id": run_id, "instance_id": fixture["instance_id"],
        "path": str(out_path.relative_to(ROOT)), "file_sha256": file_sha,
        "exit_status": trajectory.get("exit_status", trajectory.get("execution_status")),
        "resolved": (trajectory.get("R4_terminal_outcome") or {}).get("resolved"),
        "failure": trajectory.get("failure"),
        "model": MODEL,
    }
