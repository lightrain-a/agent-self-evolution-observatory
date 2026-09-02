"""AtomGit CodingPlan / AtomCode-mediated Qwen3.8 source-trajectory runtime for PACTA-MSR T0.

This module adapts only the provider transport. Exact-base Docker normalization,
MiniSWEAgent message rendering, action parsing, environment execution, timeout
observation rendering, and trajectory persistence follow the already-qualified
ReasoningBank runtime semantics.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_provider import _message_text_from_jsonl
from research_pipeline.c1_pacta_rb_qwen397 import (
    atomic_bytes,
    atomic_json,
    canonical,
    render_writer_input,
    sha256_file,
    sha256_text,
)
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import (
    ACTION_RE,
    Container,
    append_jsonl,
    initial_messages,
    parse_action,
    render,
    render_timeout_observation,
)
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import (
    ATOMCODE,
    MODEL,
    PROFILE,
    serialize_messages,
    write_config,
)

SOURCE_MAX_COMPLETION_TOKENS = 16384
PACTA_FIRST_DECISION_BUDGET = 2048
ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS = 900
SAMPLING_CONTROL = "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"
PROVIDER_ID = "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_HEADLESS_SOURCE_V1"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class AtomCodeSourceProvider:
    def __init__(self, *, root: Path, config_path: Path, workdir: Path) -> None:
        self.root = root
        self.config_path = config_path
        self.workdir = workdir
        self.calls = 0
        self.transport_attempts = 0
        self.prompt_tokens = 0
        self.output_tokens = 0
        if not self.config_path.is_file():
            raise RuntimeError("STOP_ATOMCODE_SOURCE_CONFIG_MISSING")
        self.workdir.mkdir(parents=True, exist_ok=True)

    def call(self, messages: list[dict[str, str]], label: str) -> dict[str, Any]:
        self.calls += 1
        self.transport_attempts += 1
        logical = self.calls
        prompt = serialize_messages(messages)
        safe = {
            "schema_version": 1,
            "timestamp_utc": now(),
            "provider_id": PROVIDER_ID,
            "label": label,
            "logical_call": logical,
            "transport_attempt": 1,
            "provider_retries": 0,
            "profile": PROFILE,
            "resolved_model_expected": MODEL,
            "max_tokens": SOURCE_MAX_COMPLETION_TOKENS,
            "atomcode_subprocess_timeout_seconds": ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
            "sampling_control": SAMPLING_CONTROL,
            "prompt_sha256": sha256_text(prompt),
            "config_sha256": sha256_file(self.config_path),
            "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
            "authorization_material_persisted": False,
        }
        request_path = self.root / "raw" / f"request-{logical:04d}.json"
        stdout_path = self.root / "raw" / f"response-{logical:04d}.stdout.jsonl"
        stderr_path = self.root / "raw" / f"response-{logical:04d}.stderr.txt"
        request_sha = atomic_bytes(
            request_path,
            (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(),
        )
        fd, prompt_name = tempfile.mkstemp(prefix="c1-atomgit-source-", suffix=".txt", dir="/tmp")
        prompt_path = Path(prompt_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(prompt)
                handle.flush()
                os.fsync(handle.fileno())
            cmd = [
                str(ATOMCODE),
                "--config",
                str(self.config_path),
                "--provider",
                PROFILE,
                "--no-tools",
                "--ephemeral",
                "--no-telemetry",
                "--output-format",
                "jsonl",
                "-C",
                str(self.workdir),
                "--prompt-file",
                str(prompt_path),
            ]
            completed = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or ""
            err = exc.stderr or ""
            if isinstance(out, bytes):
                out = out.decode(errors="replace")
            if isinstance(err, bytes):
                err = err.decode(errors="replace")
            stdout_sha = atomic_bytes(stdout_path, out.encode())
            stderr_sha = atomic_bytes(stderr_path, err.encode())
            receipt = {
                **safe,
                "request_sha256": request_sha,
                "stdout_sha256": stdout_sha,
                "stderr_sha256": stderr_sha,
                "returncode": 124,
                "parse_status": "NOT_PARSED_TIMEOUT",
                "model_content_observed": False,
            }
            atomic_json(self.root / "calls" / f"{logical:04d}.json", receipt)
            raise RuntimeError("STOP_ATOMCODE_SOURCE_PROVIDER_TIMEOUT")
        finally:
            prompt_path.unlink(missing_ok=True)

        stdout_sha = atomic_bytes(stdout_path, completed.stdout.encode())
        stderr_sha = atomic_bytes(stderr_path, completed.stderr.encode())
        base = {
            **safe,
            "request_sha256": request_sha,
            "stdout_sha256": stdout_sha,
            "stderr_sha256": stderr_sha,
            "returncode": completed.returncode,
            "persisted_before_parse": True,
        }
        if completed.returncode != 0:
            receipt = {
                **base,
                "parse_status": "NOT_PARSED_ATOMCODE_NONZERO",
                "stderr_tail_sha256": sha256_text(completed.stderr[-1000:]),
                "model_content_observed": False,
            }
            atomic_json(self.root / "calls" / f"{logical:04d}.json", receipt)
            raise RuntimeError("STOP_ATOMCODE_SOURCE_PROVIDER_NONZERO")

        try:
            text, meta = _message_text_from_jsonl(completed.stdout)
        except Exception as exc:
            receipt = {
                **base,
                "parse_status": "JSONL_PARSE_FAILED",
                "failure": f"{type(exc).__name__}:{exc}",
                "model_content_observed": False,
            }
            atomic_json(self.root / "calls" / f"{logical:04d}.json", receipt)
            raise RuntimeError("STOP_ATOMCODE_SOURCE_JSONL_PARSE") from exc

        started = meta["started"]
        usage = meta["usage"]
        started_model = str(started.get("model", ""))
        identity = started_model in {MODEL, PROFILE}
        self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
        self.output_tokens += int(usage.get("completion_tokens") or 0)
        receipt = {
            **base,
            "parse_status": "JSONL_PARSED",
            "started_model": started_model,
            "model_drift": not identity,
            "usage": usage,
            "codingplan_requests": 1,
            "content_sha256": sha256_text(text),
            "model_content_observed": True,
        }
        atomic_json(self.root / "calls" / f"{logical:04d}.json", receipt)
        if not identity:
            raise RuntimeError("STOP_PROVIDER_IDENTITY_DRIFT")
        if not text.strip():
            raise RuntimeError("STOP_ATOMCODE_SOURCE_EMPTY_TEXT")
        return {"content": text, "provider": receipt}


def execute_trajectory(
    *,
    instance: str,
    task: str,
    digest_ref: str,
    unit_root: Path,
    config: dict[str, Any],
    provider_config_path: Path,
    provider_workdir: Path,
    base_commit: str,
) -> dict[str, Any]:
    if unit_root.exists():
        raise RuntimeError(f"exactly-once unit root exists: {unit_root}")
    unit_root.mkdir(parents=True)
    provider = AtomCodeSourceProvider(root=unit_root, config_path=provider_config_path, workdir=provider_workdir)
    container = None
    messages = initial_messages(task, config)
    variables = {"task": task, "selected_memory": ""}
    terminal = "NOT_STARTED"
    result_text = ""
    failure_layer = None
    try:
        container = Container(digest_ref, base_commit, unit_root)
        append_jsonl(
            unit_root / "step-journal.jsonl",
            {
                "event": "trajectory_start",
                "timestamp": now(),
                "messages": messages,
                "selected_memory": "",
                "provider": PROVIDER_ID,
                "sampling_control": SAMPLING_CONTROL,
            },
        )
        terminal = "LimitsExceeded"
        for step in range(1, int(config["agent"]["step_limit"]) + 1):
            response = provider.call(messages, f"{instance}-step-{step}")
            content = response["content"]
            messages.append({"role": "assistant", "content": content})
            try:
                action = parse_action(content)
            except Exception:
                error = render(
                    config["agent"]["format_error_template"],
                    variables,
                    actions=ACTION_RE.findall(content),
                )
                messages.append({"role": "user", "content": error})
                append_jsonl(
                    unit_root / "step-journal.jsonl",
                    {
                        "event": "format_error",
                        "step_index": step,
                        "response_sha256": response["provider"]["stdout_sha256"],
                        "error_message_sha256": sha256_text(error),
                    },
                )
                continue

            observation = container.execute(action)
            observation_path = unit_root / "raw" / f"observation-{step:04d}.json"
            observation_sha = atomic_bytes(
                observation_path,
                (json.dumps(observation, ensure_ascii=False, sort_keys=True) + "\n").encode(),
            )
            lines = observation["output"].lstrip().splitlines(keepends=True)
            if (
                not observation["timeout"]
                and lines
                and lines[0].strip() in ("MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")
            ):
                terminal = "Submitted"
                result_text = "".join(lines[1:])
                messages.append({"role": "user", "content": result_text})
                event = "submitted"
            elif observation["timeout"]:
                user = render_timeout_observation(config, action, observation["output"])
                messages.append({"role": "user", "content": user})
                event = "timeout"
            else:
                user = render(config["agent"]["action_observation_template"], variables, output=observation)
                messages.append({"role": "user", "content": user})
                event = "observation"
            append_jsonl(
                unit_root / "step-journal.jsonl",
                {
                    "event": event,
                    "step_index": step,
                    "response_sha256": response["provider"]["stdout_sha256"],
                    "parsed_action": action,
                    "canonical_action_signature": action.strip(),
                    "observation_path": str(observation_path),
                    "observation_sha256": observation_sha,
                    "returncode": observation["returncode"],
                },
            )
            if terminal == "Submitted":
                break
    except Exception as exc:
        terminal = type(exc).__name__
        result_text = str(exc)
        if "IDENTITY_DRIFT" in result_text:
            failure_layer = "provider_identity"
        elif "ATOMCODE_SOURCE_PROVIDER" in result_text or "ATOMCODE_SOURCE_JSONL" in result_text or "ATOMCODE_SOURCE_EMPTY" in result_text:
            failure_layer = "provider"
        else:
            failure_layer = "implementation"
        append_jsonl(
            unit_root / "step-journal.jsonl",
            {
                "event": "trajectory_exception",
                "timestamp": now(),
                "error_type": terminal,
                "failure_layer": failure_layer,
                "error": result_text[:1000],
            },
        )
    finally:
        if container is not None:
            container.cleanup()
        trajectory = {
            "schema_version": 1,
            "trajectory_format": "mini-swe-agent-1",
            "instance_id": instance,
            "messages": messages,
            "exit_status": terminal,
            "result": result_text,
            "failure_layer": failure_layer,
            "model_stats": {
                "logical_calls": provider.calls,
                "transport_attempts": provider.transport_attempts,
                "prompt_tokens": provider.prompt_tokens,
                "completion_tokens": provider.output_tokens,
                "codingplan_requests": provider.calls,
            },
        }
        trajectory_path = unit_root / "source_trajectory.json"
        atomic_json(trajectory_path, trajectory)
        writer_path = unit_root / "writer_input_trajectory.txt"
        writer_sha = atomic_bytes(writer_path, render_writer_input(messages).encode("utf-8"))
        hashes = {
            "source_trajectory_path": str(trajectory_path),
            "source_trajectory_sha256": sha256_file(trajectory_path),
            "writer_input_trajectory_path": str(writer_path),
            "writer_input_trajectory_sha256": writer_sha,
        }
        atomic_json(unit_root / "hashes.json", hashes)
        raw_responses = len(list((unit_root / "raw").glob("response-*.stdout.jsonl")))
        valid = failure_layer is None and provider.calls >= 1 and raw_responses == provider.calls
        run = {
            "schema_version": 1,
            "created_at_utc": now(),
            "source_task_id": instance,
            "task_sha256": sha256_text(task),
            "digest_ref": digest_ref,
            "frozen_base_commit": base_commit,
            "provider_id": PROVIDER_ID,
            "requested_profile": PROFILE,
            "resolved_model": MODEL,
            "source_max_completion_tokens": SOURCE_MAX_COMPLETION_TOKENS,
            "pacta_first_decision_budget": PACTA_FIRST_DECISION_BUDGET,
            "atomcode_subprocess_timeout_seconds": ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
            "sampling_control": SAMPLING_CONTROL,
            "logical_attempt": 1,
            "provider_logical_calls": provider.calls,
            "provider_transport_attempts": provider.transport_attempts,
            "codingplan_requests": provider.calls,
            "input_tokens": provider.prompt_tokens,
            "output_tokens": provider.output_tokens,
            "terminal_status": terminal,
            "failure_layer": failure_layer,
            "validity_status": "TRAJECTORY_BACKED_VALID" if valid else "INVALID",
            "invalid_reason": None if valid else (failure_layer or "provenance_incomplete"),
            "all_raw_responses_persisted": raw_responses == provider.calls,
            **hashes,
            "writer_calls": 0,
            "binder_calls": 0,
            "probe_calls": 0,
            "shadow_calls": 0,
            "final_measurement_calls": 0,
            "future_task_executions": 0,
        }
        atomic_json(unit_root / "run.json", run)
    return run
