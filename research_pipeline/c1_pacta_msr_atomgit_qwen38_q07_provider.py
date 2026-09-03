"""AtomGit bridge providers for the frozen fresh3 PACTA-MSR downstream pilot.

No scientific execution occurs on import. Writer/binder use the Q0.4 plain-text
JSON bridge with Q0.5 ceilings. Shadow/final use the Q0.3 MiniSWEAgent JSON
bridge with the Q0.6 action ceiling. Temperature arguments from the legacy
Qwen397 call sites are recorded but never represented as supported controls.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file, sha256_text
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_text_bridge_20260903 as q03
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q04_plain_text_bridge_20260903 as q04

PROFILE = q03.PROFILE
MODEL = q03.MODEL
TIMEOUT_SECONDS = 900
SAMPLING_CONTROL = "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"
WRITER_MAX_TOKENS = 4096
BINDER_MAX_TOKENS = 2048
ACTION_MAX_TOKENS = 4096
MAX_SCIENTIFIC_REQUESTS = 816
MAX_COMPLETION_TOKENS_TOTAL = 3_276_800
STAGE_MAX = {"writer": WRITER_MAX_TOKENS, "binder": BINDER_MAX_TOKENS, "shadow": ACTION_MAX_TOKENS, "final": ACTION_MAX_TOKENS}
PLAIN_STAGES = {"writer", "binder"}
ACTION_STAGES = {"shadow", "final"}
PROVIDER_ID = "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_FRESH3_P0_BRIDGE_V1"


def safe_id(value: str) -> str:
    return sha256_text(value)[:12]


def write_configs(root: Path) -> dict[str, str]:
    config_root = root / "provider-configs"
    q04.write_config(config_root / "writer.toml", WRITER_MAX_TOKENS)
    q04.write_config(config_root / "binder.toml", BINDER_MAX_TOKENS)
    previous = q03.MAX_TOKENS
    try:
        q03.MAX_TOKENS = ACTION_MAX_TOKENS
        q03.write_config(config_root / "action.toml")
    finally:
        q03.MAX_TOKENS = previous
    return {
        "writer": sha256_file(config_root / "writer.toml"),
        "binder": sha256_file(config_root / "binder.toml"),
        "action": sha256_file(config_root / "action.toml"),
    }


def scan_usage(root: Path) -> tuple[int, int, int]:
    input_tokens = output_tokens = calls = 0
    for stage in ("writer", "binder", "shadow", "final"):
        calls_dir = root / stage / "calls"
        if not calls_dir.is_dir():
            continue
        for path in calls_dir.glob("*.json"):
            try:
                row = json.loads(path.read_text())
            except Exception:
                continue
            if row.get("logical_success_receipt") is not True:
                continue
            usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
            input_tokens += int(usage.get("prompt_tokens") or 0)
            output_tokens += int(usage.get("completion_tokens") or 0)
            calls += 1
    return input_tokens, output_tokens, calls


class Provider:
    """Drop-in provider for legacy PACTA-MSR stage functions."""

    def __init__(self, key: str, root: Path, stage: str) -> None:
        del key  # AtomCode consumes its local OAuth state; no credential enters artifacts.
        if stage not in STAGE_MAX:
            raise ValueError(stage)
        self.root = root
        self.stage = stage
        self.stage_root = root / stage
        self.calls = 0
        self.base_input, self.base_output, self.base_calls = scan_usage(root)
        self.input_tokens = self.base_input
        self.output_tokens = self.base_output
        self.total_success_calls = self.base_calls
        config_name = "action.toml" if stage in ACTION_STAGES else f"{stage}.toml"
        self.config_path = root / "provider-configs" / config_name
        if not self.config_path.is_file():
            raise RuntimeError("STOP_Q07_PROVIDER_CONFIG_MISSING:" + stage)
        self.workdir = root / "empty-provider-workdir"
        self.workdir.mkdir(parents=True, exist_ok=True)

    def _prompt(self, messages: list[dict[str, str]], label: str) -> tuple[str, str]:
        if self.stage in PLAIN_STAGES:
            return q04.bridge_prompt(messages, label, self.stage), q04.BRIDGE_SCHEMA
        return q03.bridge_prompt(messages, label), q03.BRIDGE_SCHEMA

    def _extract(self, parsed_text: str) -> tuple[str, bool, dict[str, Any]]:
        if self.stage in PLAIN_STAGES:
            text = q04.extract_text(parsed_text)
            format_ok, detail = q04.format_pass(self.stage, text)
            return text, format_ok, detail
        text = q03.extract_bridge_message(parsed_text)
        return text, True, {}

    def call(self, messages: list[dict[str, str]], label: str, *, max_tokens: int, temperature: float) -> dict[str, Any]:
        self.calls += 1
        logical = self.calls
        actual_max = STAGE_MAX[self.stage]
        prompt, bridge_schema = self._prompt(messages, label)
        safe = {
            "schema_version": 1,
            "stage": self.stage,
            "label": label,
            "logical_call": logical,
            "provider_id": PROVIDER_ID,
            "profile": PROFILE,
            "resolved_model_expected": MODEL,
            "bridge_schema": bridge_schema,
            "actual_max_tokens": actual_max,
            "legacy_callsite_max_tokens": max_tokens,
            "legacy_callsite_temperature": temperature,
            "temperature_control": SAMPLING_CONTROL,
            "timeout_seconds": TIMEOUT_SECONDS,
            "provider_retries": 0,
            "prompt_sha256": sha256_text(prompt),
            "config_sha256": sha256_file(self.config_path),
            "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
            "authorization_material_persisted": False,
        }
        raw_dir = self.stage_root / "raw"
        stem = f"{logical:04d}-{safe_id(label)}"
        req = raw_dir / f"{stem}.request.json"
        stdout_path = raw_dir / f"{stem}.stdout.jsonl"
        stderr_path = raw_dir / f"{stem}.stderr.txt"
        req_sha = atomic_bytes(req, (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
        fd, name = tempfile.mkstemp(prefix=f"c1-q07-{self.stage}-", suffix=".txt", dir="/tmp")
        prompt_path = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(prompt)
                handle.flush()
                os.fsync(handle.fileno())
            cmd = [
                str(q03.ATOMCODE), "--config", str(self.config_path), "--provider", PROFILE,
                "--no-tools", "--ephemeral", "--no-telemetry", "--output-format", "jsonl",
                "-C", str(self.workdir), "--prompt-file", str(prompt_path),
            ]
            try:
                completed = subprocess.run(cmd, text=True, capture_output=True, timeout=TIMEOUT_SECONDS, check=False)
            except subprocess.TimeoutExpired as exc:
                out = exc.stdout or ""; err = exc.stderr or ""
                if isinstance(out, bytes): out = out.decode(errors="replace")
                if isinstance(err, bytes): err = err.decode(errors="replace")
                stdout_sha = atomic_bytes(stdout_path, out.encode())
                stderr_sha = atomic_bytes(stderr_path, err.encode())
                parsed = q03.parse_jsonl(out)
                usage = parsed["usage_rows"][-1] if parsed["usage_rows"] else {}
                receipt = {
                    **safe, "request_sha256": req_sha, "stdout_sha256": stdout_sha,
                    "stderr_sha256": stderr_sha, "response_sha256": stdout_sha,
                    "returncode": 124, "parse_status": "NOT_PARSED_TIMEOUT",
                    "usage": usage, "codingplan_requests": len(parsed["usage_rows"]),
                    "tool_event_count": len(parsed["tool_events"]), "error_events": parsed["errors"],
                    "output_truncation": parsed["output_truncation"],
                    "model_content_observed": bool(parsed["text"] or usage or parsed["tool_events"]),
                    "logical_success_receipt": False,
                }
                atomic_json(self.stage_root / "calls" / f"{stem}.json", receipt)
                raise RuntimeError("STOP_Q07_PROVIDER_TIMEOUT")
        finally:
            prompt_path.unlink(missing_ok=True)

        stdout_sha = atomic_bytes(stdout_path, completed.stdout.encode())
        stderr_sha = atomic_bytes(stderr_path, completed.stderr.encode())
        parsed = q03.parse_jsonl(completed.stdout)
        usage_exact = len(parsed["usage_rows"]) == 1
        usage = parsed["usage_rows"][0] if usage_exact else {}
        started_model = str((parsed["started"] or {}).get("model") or "")
        identity = started_model in {MODEL, PROFILE}
        text = ""; format_ok = False; detail: dict[str, Any] = {}; failure = None
        try:
            text, format_ok, detail = self._extract(parsed["text"])
        except Exception as exc:
            failure = f"{type(exc).__name__}:{exc}"
        valid = (
            completed.returncode == 0 and identity and usage_exact and not parsed["errors"]
            and not parsed["output_truncation"] and not parsed["tool_events"] and format_ok and bool(text.strip())
        )
        receipt = {
            **safe, "request_sha256": req_sha, "stdout_sha256": stdout_sha,
            "stderr_sha256": stderr_sha, "response_sha256": stdout_sha,
            "returncode": completed.returncode, "persisted_before_parse": True,
            "started_model": started_model, "model_drift": not identity,
            "usage": usage, "codingplan_requests": len(parsed["usage_rows"]),
            "tool_event_count": len(parsed["tool_events"]), "error_events": parsed["errors"],
            "output_truncation": parsed["output_truncation"], "bridge_parse_pass": bool(text),
            "format_pass": format_ok, "content_sha256": sha256_text(text) if text else "",
            "failure": failure, "logical_success_receipt": valid, **detail,
        }
        atomic_json(self.stage_root / "calls" / f"{stem}.json", receipt)
        if not valid:
            raise RuntimeError("STOP_Q07_PROVIDER_OR_FORMAT_INVALID")
        self.input_tokens += int(usage.get("prompt_tokens") or 0)
        self.output_tokens += int(usage.get("completion_tokens") or 0)
        self.total_success_calls += 1
        if self.total_success_calls > MAX_SCIENTIFIC_REQUESTS:
            raise RuntimeError("STOP_Q07_SCIENTIFIC_REQUEST_CAP")
        if self.output_tokens > MAX_COMPLETION_TOKENS_TOTAL:
            raise RuntimeError("STOP_Q07_COMPLETION_ENVELOPE")
        return {"content": text, "receipt": receipt}


def phase_usage(provider: Provider) -> dict[str, int]:
    return {
        "phase_input_tokens": provider.input_tokens - provider.base_input,
        "phase_output_tokens": provider.output_tokens - provider.base_output,
        "cumulative_input_tokens": provider.input_tokens,
        "cumulative_output_tokens": provider.output_tokens,
        "cumulative_scientific_requests": provider.total_success_calls,
    }
