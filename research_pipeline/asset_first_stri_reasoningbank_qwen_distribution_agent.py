"""Exactly-once Qwen coding trajectory execution on qualified SWE-bench images."""
from __future__ import annotations

import copy
import json
import shlex
import time
from pathlib import Path
from typing import Any, Mapping

from jinja2 import Template

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError, ArkReasoningBankClient, ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL, COMMAND_TIMEOUT_SECONDS, EVALUATOR_TIMEOUT_SECONDS, FORMAT_RE,
    ROOT, STEP_LIMIT, canonical_json, load_config, render_messages,
    render_timeout_observation, sha256_text, utcnow,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_qualify import (
    QualificationDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_evaluator import (
    grade_status_map, parse_status_map,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    edit_target_set, parse_hunks,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavior import (
    trajectory_observables,
)

MODEL = "qwen3-coder-next"


def make_client(*, timeout_seconds: float = 120.0) -> ArkReasoningBankClient:
    base = ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
    if base.base_url.rstrip("/") != BASE_URL:
        raise RuntimeError("Qwen provider base URL drift")
    return ArkReasoningBankClient(ArkReasoningBankSettings(
        api_key=base.api_key, base_url=BASE_URL, model=MODEL,
        timeout_seconds=timeout_seconds, max_retries=0))


def request_body(messages: list[dict[str, str]], sampling: Mapping[str, Any]) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": MODEL, "input": copy.deepcopy(messages),
        "temperature": float(sampling["temperature"]),
        "top_p": float(sampling["top_p"]),
        "max_output_tokens": int(sampling["max_output_tokens"]),
        "store": True,
    }
    if isinstance(sampling.get("top_k"), int):
        body["top_k"] = int(sampling["top_k"])
    return body


def safe_response(response: Mapping[str, Any]) -> dict[str, Any]:
    response_id = str(response.get("response_id") or "")
    text = str(response.get("raw_text", response.get("text", "")))
    return {
        "status": response.get("status"),
        "requested_model": response.get("requested_model"),
        "resolved_model": response.get("resolved_model"),
        "text": text, "text_sha256": sha256_text(text),
        "raw_payload_sha256": response.get("raw_payload_sha256"),
        "safe_rate_quota_headers": response.get("response_headers") or {},
        "usage": response.get("usage") or {},
        "transport_attempts": response.get("transport_attempts"),
        "response_id_sha256": sha256_text(response_id),
        "credential_material_present": False,
    }


def modified_files_from_status(status_output: str) -> list[str]:
    files: list[str] = []
    for line in status_output.splitlines():
        if len(line) >= 4:
            value = line[3:].strip()
            files.append(value.split(" -> ")[-1])
    return sorted(set(files))


def execute_trajectory(*, row: Mapping[str, Any], image_pull_reference: str,
                       selected_memory: str, run_id: str,
                       sampling: Mapping[str, Any],
                       client: ArkReasoningBankClient | None = None,
                       container: QualificationDockerRun | None = None) -> tuple[dict[str, Any], QualificationDockerRun]:
    task = str(row["problem_statement"])
    base_commit = str(row["base_commit"])
    messages = render_messages(task, selected_memory)
    config = load_config()
    policy = client or make_client()
    container = container or QualificationDockerRun(
        image=image_pull_reference, base_commit=base_commit, run_id=run_id)
    runtime = container.start()
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    failure: dict[str, Any] | None = None
    exit_status, submission = "", ""
    for step in range(1, STEP_LIMIT + 1):
        request = request_body(messages, sampling)
        requests.append({
            "step": step, "canonical_request": request,
            "request_sha256": sha256_text(canonical_json(request)),
            "attempt_count": 1,
        })
        call_started = time.monotonic()
        try:
            response = policy.create_response(
                input_items=request["input"], model=request["model"],
                temperature=request["temperature"], top_p=request["top_p"],
                top_k=request.get("top_k"),
                max_output_tokens=request["max_output_tokens"], store=True)
        except ArkCompatibilityError as error:
            failure = {
                "failure_layer": "provider", "error_type": type(error).__name__,
                "safe_receipt": error.safe_receipt(),
                "ambiguous_generation_reissued": False,
            }
            exit_status = "ProviderTerminalFailure"
            break
        receipt = safe_response(response)
        receipt["latency_seconds"] = round(time.monotonic() - call_started, 6)
        responses.append({"step": step, **receipt})
        if int(receipt.get("transport_attempts") or 0) != 1:
            failure = {"failure_layer": "provider", "error_type": "HiddenRetryDetected"}
            exit_status = "ProviderRetryPolicyViolation"
            break
        if receipt["resolved_model"] != MODEL:
            failure = {
                "failure_layer": "provider", "error_type": "ResolvedModelIdentityDrift",
                "expected": MODEL, "actual": receipt["resolved_model"],
            }
            exit_status = "ProviderIdentityDrift"
            break
        content = str(receipt["text"])
        if content:
            messages.append({"role": "assistant", "content": content})
        parsed = FORMAT_RE.findall(content)
        if len(parsed) != 1:
            visible = Template(config["agent"]["format_error_template"]).render(actions=parsed)
            messages.append({"role": "user", "content": visible})
            actions.append({
                "step": step, "type": "format_error",
                "candidate_action_count": len(parsed),
                "assistant_output_empty": not bool(content),
                "model_visible_observation": visible,
            })
            continue
        action = parsed[0].strip()
        output = container.exec(action, timeout=COMMAND_TIMEOUT_SECONDS)
        action_row = {
            "step": step, "type": "shell", "action": action,
            "returncode": output["returncode"], "timed_out": output["timed_out"],
            "started_at_utc": output["started_at_utc"],
            "finished_at_utc": output["finished_at_utc"],
            "raw_output": output["output"],
        }
        actions.append(action_row)
        if output["timed_out"]:
            visible = render_timeout_observation(config, action, output["output"])
            action_row["model_visible_observation"] = visible
            messages.append({"role": "user", "content": visible})
            continue
        lines = output["output"].lstrip().splitlines(keepends=True)
        if lines and lines[0].strip() in {
            "MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
        }:
            submission = "".join(lines[1:])
            exit_status = "Submitted"
            action_row["submission_marker"] = lines[0].strip()
            action_row["model_visible_observation"] = submission
            messages.append({"role": "user", "content": submission})
            break
        visible = Template(config["agent"]["action_observation_template"]).render(
            output={"returncode": output["returncode"], "output": output["output"]})
        action_row["model_visible_observation"] = visible
        messages.append({"role": "user", "content": visible})
    else:
        exit_status = "LimitsExceeded"
    patch_result = container.exec(
        f"git -c core.fileMode=false diff --binary {base_commit}", timeout=120)
    status_result = container.exec(
        "git status --porcelain=v1 --untracked-files=all", timeout=60)
    patch = patch_result["output"] if patch_result["returncode"] == 0 else ""
    status_output = status_result["output"] if status_result["returncode"] == 0 else ""
    trajectory = {
        "schema_version": 1, "run_id": run_id, "created_at_utc": utcnow(),
        "instance_id": row["instance_id"], "task_sha256": sha256_text(task),
        "problem_statement": task,
        "base_commit": base_commit, "image_pull_reference": image_pull_reference,
        "selected_memory": selected_memory,
        "selected_memory_sha256": sha256_text(selected_memory),
        "provider": {
            "base_url": BASE_URL, "requested_model": MODEL,
            "sampling": dict(sampling), "max_retries": 0,
            "streaming": False, "seed": "omitted",
        },
        "runtime_receipt": runtime,
        "messages": messages, "requests": requests, "responses": responses,
        "actions": actions, "model_call_count": len(requests),
        "accepted_response_count": len(responses),
        "exit_status": exit_status, "submission": submission,
        "failure": failure, "final_patch": patch,
        "final_patch_sha256": sha256_text(patch),
        "status_porcelain": status_output,
        "modified_files": modified_files_from_status(status_output),
        "attempt_count": 1, "automatic_retry": False, "replacement": False,
        "gold_patch_model_visible": False, "test_patch_model_visible": False,
        "evaluator_script_model_visible": False,
        "credential_material_present": False,
    }
    return trajectory, container


def evaluate(container: QualificationDockerRun, row: Mapping[str, Any]) -> dict[str, Any]:
    result = container.exec(str(row["eval_script"]), timeout=EVALUATOR_TIMEOUT_SECONDS)
    raw = str(result["output"])
    parser_family = str(row["log_parser"])
    status_map = parse_status_map(parser_family, raw)
    grade = grade_status_map(
        status_map, list(row["FAIL_TO_PASS"]), list(row["PASS_TO_PASS"]))
    markers = ">>>>> Start Test Output" in raw and ">>>>> End Test Output" in raw
    valid = bool(
        not result["timed_out"] and result["returncode"] == 0
        and markers and status_map)
    return {
        "evaluator": "pinned SWE-bench 5.0.2-compatible",
        "evaluator_returncode": result["returncode"],
        "evaluator_timed_out": result["timed_out"],
        "raw_output_sha256": sha256_text(raw),
        "raw_output": raw,
        "test_output_markers_valid": markers,
        "log_parser": parser_family, "status_map": status_map,
        **grade, "valid": valid,
        "resolved": bool(valid and grade["resolved"]),
        "gold_patch_used": False, "test_patch_model_visible": False,
    }


def frozen_base_files(container: QualificationDockerRun, base_commit: str,
                      patch: str) -> dict[str, str]:
    files = {}
    for hunk in parse_hunks(patch):
        path = hunk.old_path
        if path in {"/dev/null", ""} or not path.endswith(".py") or path in files:
            continue
        result = container.exec(
            "git show " + shlex.quote(f"{base_commit}:{path}"), timeout=60)
        if result["returncode"] == 0 and not result["timed_out"]:
            files[path] = result["output"]
    return files


def execute_behavioral_unit(*, row: Mapping[str, Any], image_pull_reference: str,
                            selected_memory: str, run_id: str,
                            sampling: Mapping[str, Any],
                            expected_R1_sha256: str) -> dict[str, Any]:
    container = QualificationDockerRun(
        image=image_pull_reference, base_commit=str(row["base_commit"]), run_id=run_id)
    trajectory: dict[str, Any] | None = None
    evaluator: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        trajectory, _ = execute_trajectory(
            row=row, image_pull_reference=image_pull_reference,
            selected_memory=selected_memory, run_id=run_id,
            sampling=sampling, container=container)
        first_request_sha = (
            trajectory["requests"][0]["request_sha256"]
            if trajectory.get("requests") else None)
        r1_exact = first_request_sha == expected_R1_sha256
        try:
            evaluator = evaluate(container, row)
        except Exception as error:
            evaluator = {
                "valid": False, "resolved": False,
                "failure": {"failure_layer": "evaluator",
                            "error_type": type(error).__name__, "message": str(error)},
            }
        patch = str(trajectory.get("final_patch") or "")
        base_files = frozen_base_files(
            container, str(row["base_commit"]), patch)
        edit_target = edit_target_set(patch, base_files)
        observables = trajectory_observables(
            actions=trajectory.get("actions") or [], patch=patch,
            modified_files=trajectory.get("modified_files") or [],
            edit_target=edit_target,
            model_call_count=int(trajectory.get("model_call_count") or 0),
            exit_status=str(trajectory.get("exit_status") or ""))
        complete_exit = trajectory.get("exit_status") in {"Submitted", "LimitsExceeded"}
        behavior_valid = bool(
            r1_exact and complete_exit and trajectory.get("failure") is None
            and trajectory.get("accepted_response_count", 0) > 0)
        status = "COMPLETED" if behavior_valid else "TERMINAL_INVALID_BEHAVIOR"
    except Exception as error:
        first_request_sha, r1_exact, behavior_valid = None, False, False
        observables = None
        failure = {
            "failure_layer": "runtime_or_implementation",
            "error_type": type(error).__name__, "message": str(error),
        }
        status = "TERMINAL_RUNTIME_OR_IMPLEMENTATION_FAILURE"
    cleanup = container.close()
    return {
        "schema_version": 1, "run_id": run_id, "created_at_utc": utcnow(),
        "instance_id": row["instance_id"], "attempt_count": 1,
        "execution_status": status, "behavior_valid": behavior_valid,
        "expected_R1_sha256": expected_R1_sha256,
        "first_actual_request_sha256": first_request_sha,
        "complete_R1_exact": r1_exact,
        "trajectory": trajectory, "behavior_observables": observables,
        "R4_terminal_outcome": evaluator, "failure": failure,
        "container_cleanup_receipt": cleanup,
        "automatic_retry": False, "replacement": False,
        "credential_material_present": False,
    }
