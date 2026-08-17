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


def runtime_contract_payload(state: dict[str, Any]) -> dict[str, Any]:
    python = state.get("python") or {}
    image = state.get("runtime_image") or {}
    preflight = state.get("exact_first_party_preflight") or {}
    return {
        "candidate_id": state.get("candidate_id"),
        "host": state.get("host"),
        "source": state.get("source"),
        "provider_contract": state.get("provider_contract"),
        "python": {
            "version": python.get("version"),
            "benchmark_dependencies_present": python.get("benchmark_dependencies_present"),
            "harbor_importable": python.get("harbor_importable"),
        },
        "runtime_image": {
            "tag": image.get("tag"),
            "builder": image.get("builder"),
            "status": image.get("status"),
            "observable": image.get("observable"),
            "present": image.get("present"),
            "image_id": image.get("image_id"),
            "repo_tags": image.get("repo_tags") or [],
        },
        "exact_first_party_preflight": preflight,
    }


def runtime_contract_sha256(state: dict[str, Any]) -> str:
    return _canonical_sha(runtime_contract_payload(state))


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
    image_id = ""
    repo_tags: list[str] = []
    if proc.returncode == 0:
        status = "PRESENT"
        observable = True
        present = True
        try:
            rows = json.loads(proc.stdout or "[]")
            row = rows[0] if isinstance(rows, list) and rows and isinstance(rows[0], dict) else {}
            image_id = str(row.get("Id") or "")
            repo_tags = [str(v) for v in (row.get("RepoTags") or []) if str(v)]
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
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

    # Never persist raw docker-inspect output: image metadata may contain Env.
    return {
        "tag": tag,
        "builder": Path(builder).name,
        "status": status,
        "observable": observable,
        "present": present,
        "probe_returncode": proc.returncode,
        "image_id": image_id,
        "repo_tags": repo_tags,
    }


def probe_exact_first_party_preflight(source_root: Path | None) -> dict[str, Any]:
    if source_root is None:
        return {
            "status": "NOT_RUN",
            "source_commit": SOURCE_COMMIT,
            "strict_exit_code": None,
        }
    root = Path(source_root)
    if not root.is_dir():
        return {
            "status": "SOURCE_ROOT_MISSING",
            "source_commit": SOURCE_COMMIT,
            "strict_exit_code": None,
        }
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.preflight", "--strict", "--json"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "status": "PROBE_ERROR",
            "source_commit": SOURCE_COMMIT,
            "strict_exit_code": None,
        }
    try:
        report = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        report = {}
    passed = bool(
        proc.returncode == 0
        and report.get("asset_pass") is True
        and report.get("config_pass") is True
        and report.get("harbor_importable") is True
        and report.get("runtime_image_present") is True
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "source_commit": SOURCE_COMMIT,
        "strict_exit_code": proc.returncode,
        "asset_pass": report.get("asset_pass") is True,
        "config_pass": report.get("config_pass") is True,
        "harbor_importable": report.get("harbor_importable") is True,
        "runtime_image_present": report.get("runtime_image_present") is True,
        "n_asset_errors": int(report.get("n_asset_errors") or 0),
        "n_config_errors": int(report.get("n_config_errors") or 0),
    }


def build_runtime_audit(
    *,
    env: Mapping[str, str] | None = None,
    host: str = "69",
    harbor_importable: bool | None = None,
    benchmark_python_ready: bool | None = None,
    runtime_image_probe: dict[str, Any] | None = None,
    exact_source_root: Path | None = None,
    exact_preflight_probe: dict[str, Any] | None = None,
    gemini_credential_present: bool | None = None,
) -> dict[str, Any]:
    env = os.environ if env is None else env
    if harbor_importable is None:
        harbor_importable = _importable("harbor")
    if benchmark_python_ready is None:
        benchmark_python_ready = all(_importable(name) for name in ("pydantic", "yaml", "click"))
    if runtime_image_probe is None:
        runtime_image_probe = probe_runtime_image()
    if exact_preflight_probe is None:
        exact_preflight_probe = probe_exact_first_party_preflight(exact_source_root)
    if gemini_credential_present is None:
        gemini_credential_present = bool(env.get("GEMINI_API_KEY"))

    image_present = runtime_image_probe.get("status") == "PRESENT"
    exact_preflight_pass = exact_preflight_probe.get("status") == "PASS"
    runtime_infrastructure_ready = bool(
        benchmark_python_ready
        and harbor_importable
        and image_present
        and exact_preflight_pass
    )
    provider_credential_ready = bool(gemini_credential_present)
    execution_ready = bool(runtime_infrastructure_ready and provider_credential_ready)

    hold_reason: list[str] = []
    if not benchmark_python_ready:
        hold_reason.append("benchmark Python dependencies not present in the current execution Python")
    if not harbor_importable:
        hold_reason.append("Harbor SDK not importable in the current execution Python")
    if not image_present:
        image_status = str(runtime_image_probe.get("status") or "UNVERIFIED")
        hold_reason.append(f"{RUNTIME_IMAGE}:{image_status}")
    if benchmark_python_ready and harbor_importable and image_present and not exact_preflight_pass:
        hold_reason.append(
            "exact first-party strict preflight not passed:"
            + str(exact_preflight_probe.get("status") or "UNVERIFIED")
        )
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
        "exact_first_party_preflight": exact_preflight_probe,
        "credentials": {
            "GEMINI_API_KEY_present": bool(gemini_credential_present),
            "secret_values_recorded": False,
        },
        "runtime_infrastructure_ready": runtime_infrastructure_ready,
        "provider_credential_ready": provider_credential_ready,
        "execution_ready": execution_ready,
        "hold_reason": hold_reason,
        "scientific_authority": False,
        "experiment_authority": False,
        "model_calls_executed": 0,
        "task_trials_executed": 0,
    }
    payload["runtime_contract_sha256"] = runtime_contract_sha256(payload)
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
    if not str(state.get("host") or "").strip():
        errors.append("runtime audit host is required")
    contract = state.get("provider_contract") or {}
    if contract.get("required_credentials") != ["GEMINI_API_KEY"]:
        errors.append("Gemini F0 credential contract drift")
    if contract.get("bedrock_credential_required") is not False:
        errors.append("Bedrock credential must not gate the Gemini F0")
    image = state.get("runtime_image") or {}
    if image.get("status") == "PRESENT" and str(image.get("diagnostic") or ""):
        errors.append("present runtime image receipt must not persist raw docker-inspect diagnostics")
    credentials = state.get("credentials") or {}
    if credentials.get("secret_values_recorded") is not False:
        errors.append("runtime audit must never record secret values")
    preflight = state.get("exact_first_party_preflight") or {}
    infrastructure_ready = state.get("runtime_infrastructure_ready") is True
    if infrastructure_ready and not (
        preflight.get("status") == "PASS"
        and preflight.get("source_commit") == SOURCE_COMMIT
        and int(preflight.get("strict_exit_code") or 0) == 0
        and preflight.get("asset_pass") is True
        and preflight.get("config_pass") is True
        and preflight.get("harbor_importable") is True
        and preflight.get("runtime_image_present") is True
        and (state.get("python") or {}).get("benchmark_dependencies_present") is True
        and (state.get("python") or {}).get("harbor_importable") is True
        and image.get("status") == "PRESENT"
    ):
        errors.append("runtime infrastructure readiness lacks exact first-party strict-preflight evidence")
    if state.get("provider_credential_ready") is not bool(credentials.get("GEMINI_API_KEY_present")):
        errors.append("provider credential readiness drift")
    if state.get("execution_ready") is True and not (
        state.get("runtime_infrastructure_ready") is True
        and state.get("provider_credential_ready") is True
    ):
        errors.append("execution readiness exceeds runtime/credential readiness")
    if int(state.get("model_calls_executed") or 0) != 0 or int(state.get("task_trials_executed") or 0) != 0:
        errors.append("runtime audit must remain pre-model and pre-trial")
    if state.get("scientific_authority") is not False or state.get("experiment_authority") is not False:
        errors.append("runtime audit cannot carry scientific/experiment authority")
    expected_contract = runtime_contract_sha256(state)
    if state.get("runtime_contract_sha256") != expected_contract:
        errors.append("runtime contract hash mismatch")
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
