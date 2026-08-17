from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .config import PROJECT_ROOT
from .paper_first_skill_validation_transfer_f0 import (
    CANDIDATE_ID,
    SOURCE_COMMIT,
    SOURCE_REPOSITORY,
    build_plan,
)

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-skill-validation-transfer-runtime-audit-20260817.json"
MODEL_PRESET = "gemini-3-flash"
RUNTIME_IMAGE = "agent-runtime:latest"
REQUIRED_PROVIDER_CREDENTIALS = ("GEMINI_API_KEY",)
BEDROCK_CREDENTIAL_REQUIRED = False


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _importable(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def probe_runtime_image(tag: str = RUNTIME_IMAGE) -> dict[str, Any]:
    builder = shutil.which("docker") or shutil.which("podman")
    if not builder:
        return {
            "tag": tag,
            "builder": None,
            "status": "BUILDER_UNAVAILABLE",
            "observable": False,
            "present": False,
            "probe_returncode": None,
        }

    proc = subprocess.run(
        [builder, "image", "inspect", tag],
        capture_output=True,
        text=True,
        check=False,
    )
    diagnostic = ((proc.stderr or "") + "\n" + (proc.stdout or "")).strip()
    folded = diagnostic.lower()
    if proc.returncode == 0:
        status = "PRESENT"
        observable = True
        present = True
    elif "permission denied" in folded or "permission" in folded and "docker.sock" in folded:
        status = "UNOBSERVABLE_PERMISSION_DENIED"
        observable = False
        present = False
    elif "no such image" in folded or "image not known" in folded or "not found" in folded:
        status = "ABSENT"
        observable = True
        present = False
    else:
        status = "UNOBSERVABLE_PROBE_ERROR"
        observable = False
        present = False

    # Preserve only a bounded diagnostic category/text; never include credentials.
    return {
        "tag": tag,
        "builder": Path(builder).name,
        "status": status,
        "observable": observable,
        "present": present,
        "probe_returncode": proc.returncode,
        "diagnostic": diagnostic[:800],
    }


def build_runtime_audit(
    *,
    env: Mapping[str, str] | None = None,
    host: str = "69",
    harbor_importable: bool | None = None,
    benchmark_python_ready: bool | None = None,
    runtime_image_probe: dict[str, Any] | None = None,
    gemini_credential_present: bool | None = None,
) -> dict[str, Any]:
    env = os.environ if env is None else env
    if harbor_importable is None:
        harbor_importable = _importable("harbor")
    if benchmark_python_ready is None:
        benchmark_python_ready = all(_importable(name) for name in ("pydantic", "yaml", "click"))
    if runtime_image_probe is None:
        runtime_image_probe = probe_runtime_image()
    if gemini_credential_present is None:
        gemini_credential_present = bool(env.get("GEMINI_API_KEY"))

    image_present = runtime_image_probe.get("status") == "PRESENT"
    execution_ready = bool(
        benchmark_python_ready
        and harbor_importable
        and image_present
        and gemini_credential_present
    )

    hold_reason: list[str] = []
    if not benchmark_python_ready:
        hold_reason.append("benchmark Python dependencies not present in the current execution Python")
    if not harbor_importable:
        hold_reason.append("Harbor SDK not importable in the current execution Python")
    if not image_present:
        image_status = str(runtime_image_probe.get("status") or "UNVERIFIED")
        hold_reason.append(f"{RUNTIME_IMAGE}:{image_status}")
    if not gemini_credential_present:
        hold_reason.append("GEMINI_API_KEY not loaded in the current execution environment")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "candidate_id": CANDIDATE_ID,
        "audit_scope": "ENGINEERING_RUNTIME_AVAILABILITY_ONLY_NO_MODEL_CALLS",
        "host": host,
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit_sha": SOURCE_COMMIT,
            "plan_sha256": build_plan()["plan_sha256"],
            "model_preset": MODEL_PRESET,
        },
        "provider_contract": {
            "agent_provider": "gemini",
            "host_skill_author_provider": "gemini",
            "host_skill_author_uses_run_model_preset": True,
            "required_credentials": list(REQUIRED_PROVIDER_CREDENTIALS),
            "bedrock_credential_required": BEDROCK_CREDENTIAL_REQUIRED,
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
            "benchmark_dependencies_present": bool(benchmark_python_ready),
            "harbor_importable": bool(harbor_importable),
        },
        "runtime_image": runtime_image_probe,
        "credentials": {
            "GEMINI_API_KEY_present": bool(gemini_credential_present),
            "secret_values_recorded": False,
        },
        "execution_ready": execution_ready,
        "hold_reason": hold_reason,
        "scientific_authority": False,
        "experiment_authority": False,
        "model_calls_executed": 0,
        "task_trials_executed": 0,
    }
    payload["audit_sha256"] = _canonical_sha({k: v for k, v in payload.items() if k != "audit_sha256"})
    return payload


def validate_runtime_audit(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = state.get("source") or {}
    if state.get("candidate_id") != CANDIDATE_ID:
        errors.append("runtime audit candidate identity drift")
    if source.get("repository") != SOURCE_REPOSITORY or source.get("commit_sha") != SOURCE_COMMIT:
        errors.append("runtime audit source identity drift")
    if source.get("plan_sha256") != build_plan()["plan_sha256"]:
        errors.append("runtime audit plan binding drift")
    contract = state.get("provider_contract") or {}
    if contract.get("required_credentials") != ["GEMINI_API_KEY"]:
        errors.append("Gemini F0 credential contract drift")
    if contract.get("bedrock_credential_required") is not False:
        errors.append("Bedrock credential must not gate the Gemini F0")
    credentials = state.get("credentials") or {}
    if credentials.get("secret_values_recorded") is not False:
        errors.append("runtime audit must never record secret values")
    if int(state.get("model_calls_executed") or 0) != 0 or int(state.get("task_trials_executed") or 0) != 0:
        errors.append("runtime audit must remain pre-model and pre-trial")
    if state.get("scientific_authority") is not False or state.get("experiment_authority") is not False:
        errors.append("runtime audit cannot carry scientific/experiment authority")
    expected = _canonical_sha({k: v for k, v in state.items() if k != "audit_sha256"})
    if state.get("audit_sha256") != expected:
        errors.append("runtime audit receipt hash mismatch")
    return errors


def write_runtime_audit(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    state = build_runtime_audit()
    errors = validate_runtime_audit(state)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_runtime_audit(), ensure_ascii=False, indent=2))
