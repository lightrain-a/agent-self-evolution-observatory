from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import statistics
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .config import StorageSettings
from .pilot_registry import validate_result

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(__file__).resolve().parent
READINESS_JSON = ROOT / "generated" / "p0-runtime-readiness.json"
READINESS_JS = ROOT / "generated" / "p0-runtime-readiness.js"
SUPPORTED_IDEAS = {"update-trust-region", "budgeted-evolution-controller"}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number} must be a JSON object")
        rows.append(row)
    return rows


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def rounded(value: float) -> float:
    return round(float(value), 6)


def balanced_assignments(candidate_ids: list[str], task_ids: list[str], per_candidate: int, seed: int = 42) -> dict[str, list[str]]:
    if per_candidate <= 0 or per_candidate > len(task_ids):
        raise ValueError("per_candidate must be between 1 and the task-pool size")
    counts = {task_id: 0 for task_id in task_ids}
    assignments: dict[str, list[str]] = {}
    ordered_candidates = sorted(candidate_ids, key=lambda cid: hashlib.sha256(f"{seed}|{cid}".encode()).hexdigest())
    for candidate_id in ordered_candidates:
        ranked = sorted(
            task_ids,
            key=lambda task_id: (
                counts[task_id],
                hashlib.sha256(f"{seed}|{candidate_id}|{task_id}".encode()).hexdigest(),
            ),
        )
        chosen = ranked[:per_candidate]
        assignments[candidate_id] = chosen
        for task_id in chosen:
            counts[task_id] += 1
    return assignments


def config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def gpu_summary() -> list[dict[str, Any]]:
    try:
        text = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    rows = []
    for line in text.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) == 3:
            rows.append({"name": parts[0], "memory_total_mib": int(parts[1]), "memory_free_mib": int(parts[2])})
    return rows


def _python_modules(python_path: Path, extra_pythonpath: Path | None = None) -> tuple[dict[str, bool], dict[str, str]]:
    extra_site = str(extra_pythonpath) if extra_pythonpath else ""
    script = """
import importlib.util, json, site
extra_site = __EXTRA_SITE__
if extra_site:
    site.addsitedir(extra_site)
mods = {}
vers = {}
for name in ('torch','transformers','alfworld','textworld'):
    ok = importlib.util.find_spec(name) is not None
    mods[name] = ok
    if ok:
        try:
            module = __import__(name)
            vers[name] = str(getattr(module, '__version__', 'unknown'))
        except Exception:
            vers[name] = 'import-error'
print(json.dumps({'modules':mods,'versions':vers}))
""".replace("__EXTRA_SITE__", repr(extra_site))
    try:
        payload = json.loads(subprocess.check_output([str(python_path), "-c", script], text=True, stderr=subprocess.DEVNULL))
        return dict(payload.get("modules") or {}), dict(payload.get("versions") or {})
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {name: False for name in ("torch", "transformers", "alfworld", "textworld")}, {}


def runtime_contract_hash(model_path: Path, python_path: Path, versions: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path in (CONFIG_DIR / "p0_alfworld_adapter.py", CONFIG_DIR / "p0_alfworld_config.yaml"):
        if path.exists():
            digest.update(path.read_bytes())
    digest.update(json.dumps({
        "model_path": str(model_path),
        "python_path": str(python_path),
        "versions": versions,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    return digest.hexdigest()


def runtime_preflight(model_path: Path, data_root: Path, python_path: Path, extra_pythonpath: Path | None = None, alfworld_data: Path | None = None, smoke_path: Path | None = None) -> dict[str, Any]:
    modules, versions = _python_modules(python_path, extra_pythonpath)
    contract_hash = runtime_contract_hash(model_path, python_path, versions)
    gpus = gpu_summary()
    required_model_files = ("config.json", "tokenizer.json", "model.safetensors.index.json")
    model_ok = model_path.is_dir() and all((model_path / name).exists() for name in required_model_files)
    alfworld_data = (alfworld_data or Path(os.environ.get("ALFWORLD_DATA", str(data_root / "alfworld")))).expanduser()
    required_alfworld_data = (
        "json_2.1.1/train",
        "json_2.1.1/valid_seen",
        "json_2.1.1/valid_unseen",
        "logic/alfred.pddl",
        "logic/alfred.twl2",
    )
    alfworld_data_ok = all((alfworld_data / item).exists() for item in required_alfworld_data)
    probe = data_root
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    disk = shutil.disk_usage(probe)
    blockers: list[str] = []
    if not python_path.exists():
        blockers.append("runtime-python-missing")
    if not gpus:
        blockers.append("no-nvidia-gpu")
    if not model_ok:
        blockers.append("model-files-missing")
    blockers.extend(f"python-module-missing:{name}" for name, ok in modules.items() if not ok)
    if not alfworld_data_ok:
        blockers.append("alfworld-data-missing")
    if disk.free < 20 * 1024**3:
        blockers.append("data-disk-free-space-below-20GiB")
    smoke_path = smoke_path or (data_root / "p0-runtime-smoke.json")
    smoke_payload: dict[str, Any] = {}
    if smoke_path.exists():
        try:
            loaded = json.loads(smoke_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                smoke_payload = loaded
        except (OSError, json.JSONDecodeError):
            smoke_payload = {}
    smoke_ready = bool(
        smoke_payload.get("status") == "pass"
        and smoke_payload.get("model_path") == str(model_path)
        and smoke_payload.get("runtime_contract_hash") == contract_hash
    )
    execution_states: list[dict[str, Any]] = []
    execution_dir = data_root / "p0-executions"
    if execution_dir.exists():
        for state_path in sorted(execution_dir.glob("*.json")):
            try:
                loaded = json.loads(state_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    execution_states.append({"path": str(state_path), **loaded})
            except (OSError, json.JSONDecodeError):
                continue
    legacy_execution_state_path = data_root / "p0-execution-state.json"
    if legacy_execution_state_path.exists():
        try:
            loaded = json.loads(legacy_execution_state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                legacy_id = str(loaded.get("idea_id") or "")
                if not any(str(row.get("idea_id") or "") == legacy_id for row in execution_states):
                    execution_states.append({"path": str(legacy_execution_state_path), **loaded, "legacy": True})
        except (OSError, json.JSONDecodeError):
            pass
    execution_states.sort(key=lambda row: str(row.get("updated_at") or row.get("finished_at") or row.get("started_at") or ""), reverse=True)
    execution_state = execution_states[0] if execution_states else {"path": str(legacy_execution_state_path)}
    execution_started = any(str(row.get("status") or "") in {"running", "collected", "registered", "failed"} for row in execution_states)
    environment_ready = not blockers
    return {
        "schema_version": "1.1",
        "code_commit": git_head(),
        "environment_ready": environment_ready,
        "launch_ready": environment_ready and smoke_ready,
        "blockers": blockers,
        "runtime_python": str(python_path),
        "runtime_contract_hash": contract_hash,
        "extra_pythonpath": str(extra_pythonpath) if extra_pythonpath else "",
        "python_modules": modules,
        "python_versions": versions,
        "gpus": gpus,
        "model": {"path": str(model_path), "ready": model_ok},
        "alfworld_data": {"path": str(alfworld_data), "ready": alfworld_data_ok},
        "smoke_rollout": {"path": str(smoke_path), "ready": smoke_ready, "status": smoke_payload.get("status", "missing")},
        "execution_state": execution_state,
        "execution_states": execution_states,
        "stages": {
            "harness_ready": True,
            "package_ready": bool(modules.get("alfworld") and modules.get("textworld")),
            "data_ready": alfworld_data_ok,
            "smoke_rollout_ready": smoke_ready,
            "p0_execution_started": execution_started,
        },
        "data_root": str(data_root),
        "data_disk_free_gib": round(disk.free / 1024**3, 1),
        "supported_p0": sorted(SUPPORTED_IDEAS),
    }


def write_readiness(payload: dict[str, Any], json_path: Path = READINESS_JSON, js_path: Path = READINESS_JS) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.P0_RUNTIME_READINESS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def validate_measured_cost(config: dict[str, Any], cost: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("gpu_hours", "model_calls", "tokens", "input_tokens", "output_tokens", "wall_clock_hours", "environment_episodes", "accounting_consistent")
    for key in required:
        if key not in cost:
            errors.append(f"cost missing {key}")
    if errors:
        return errors
    try:
        gpu_hours = float(cost["gpu_hours"])
        model_calls = int(cost["model_calls"])
        tokens = int(cost["tokens"])
        input_tokens = int(cost["input_tokens"])
        output_tokens = int(cost["output_tokens"])
        wall_hours = float(cost["wall_clock_hours"])
        episodes = int(cost["environment_episodes"])
    except (TypeError, ValueError):
        return ["cost fields must be numeric"]
    if min(gpu_hours, wall_hours, model_calls, tokens, input_tokens, output_tokens, episodes) < 0:
        errors.append("cost fields must be non-negative")
    if model_calls <= 0 or episodes <= 0:
        errors.append("real P0 cost must contain positive model calls and environment episodes")
    if tokens <= 0 or tokens != input_tokens + output_tokens:
        errors.append("token accounting must be positive and equal input_tokens + output_tokens")
    if cost.get("accounting_consistent") is not True:
        errors.append("independent model-call accounting did not agree")
    cap = config.get("resource_cap") or {}
    if cap.get("gpu_hours") is not None and gpu_hours > float(cap["gpu_hours"]):
        errors.append(f"measured GPU-hours {gpu_hours} exceed cap {cap['gpu_hours']}")
    if cap.get("wall_hours") is not None and wall_hours > float(cap["wall_hours"]):
        errors.append(f"measured wall hours {wall_hours} exceed cap {cap['wall_hours']}")
    if cap.get("episodes") is not None and episodes > int(cap["episodes"]):
        errors.append(f"measured episodes {episodes} exceed cap {cap['episodes']}")
    return errors


def validate_collection_manifest(
    idea_id: str,
    config: dict[str, Any],
    input_path: Path,
    cost: dict[str, Any],
    manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if manifest.get("idea_id") != idea_id or manifest.get("phase") != "P0":
        errors.append("manifest idea_id/phase mismatch")
    if manifest.get("experiment_config_hash") != config_hash(config):
        errors.append("manifest config hash does not match analysis config")
    if Path(str(manifest.get("analysis_input") or "")).name != input_path.name:
        errors.append("manifest analysis_input does not match analyzed file")
    if int(manifest.get("actual_environment_episodes") or -1) != int(cost.get("environment_episodes") or -2):
        errors.append("manifest/cost environment episode counts disagree")
    if idea_id == "update-trust-region":
        contract = manifest.get("candidate_generation_contract") or {}
        forbidden = set(contract.get("forbidden_inputs") or [])
        if contract.get("generation_completed_before_probe_and_hidden_execution") is not True:
            errors.append("A-1 candidate generation was not frozen before probe/hidden execution")
        if not {"behavior-probe-results", "hidden-original-task-results"}.issubset(forbidden):
            errors.append("A-1 manifest does not forbid probe/hidden inputs during candidate generation")
    elif idea_id == "budgeted-evolution-controller":
        contract = manifest.get("sequence_generation_contract") or {}
        if contract.get("controller_access_during_generation") is not False:
            errors.append("A-2 controller must not participate in candidate-sequence generation")
        if contract.get("all_controllers_reuse_identical_saved_sequences") is not True:
            errors.append("A-2 methods must reuse identical frozen sequences")
        if contract.get("controller_fit_splits") != ["discovery", "calibration"] or contract.get("controller_test_split") != "hidden":
            errors.append("A-2 fit/test split contract is invalid")
    return errors


def result_payload(analysis: dict[str, Any], config: dict[str, Any], cost: dict[str, Any] | None = None) -> dict[str, Any]:
    proposed_name = "gain+behavior-drift" if analysis["idea_id"] == "update-trust-region" else "learned-linear-controller"
    proposed = next(row for row in analysis["table"] if row["policy"] == proposed_name)
    metrics = {key: value for key, value in proposed.items() if key not in {"policy", "tasks"}}
    for key in ("harmful_update_reduction", "target_gain_loss", "calls_saved_fraction", "success_loss"):
        if key in analysis:
            metrics[key] = analysis[key]
    payload = {
        "schema_version": "1.0",
        "idea_id": analysis["idea_id"],
        "phase": "P0",
        "result": analysis["decision"],
        "code_commit": git_head(),
        "config_hash": config_hash(config),
        "datasets": list(config.get("datasets") or ["ALFWorld"]),
        "models": list(config.get("models") or ["Qwen2.5-7B-Instruct"]),
        "seeds": list(config.get("seeds") or [42]),
        "metrics": metrics,
        "cost": cost or {"gpu_hours": 0.0, "model_calls": 0, "tokens": 0, "wall_clock_hours": 0.0},
        "diagnosis": analysis["diagnosis"],
        "next_action": "await-human-approval" if analysis["decision"] == "pass" else "stop-or-return-to-gap-mining",
    }
    errors = validate_result(payload)
    if errors:
        raise ValueError("invalid pilot result: " + "; ".join(errors))
    return payload


def register_result(payload: dict[str, Any]) -> Path:
    storage = StorageSettings.from_env()
    result_dir = storage.run_dir / "pilots" / "results" / str(payload["idea_id"])
    result_dir.mkdir(parents=True, exist_ok=True)
    target = result_dir / f"P0-{str(payload['config_hash'])[:12]}.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
