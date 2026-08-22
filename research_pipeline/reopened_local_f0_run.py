from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .experiment_authority import validate_authority
from .resource_lease import acquire_gpu_lease, list_gpu_leases, release_gpu_lease
from .reopened_experiment_lease import validate_reopened_experiment_lease
from .reopened_experiment_lease_request import validate_experiment_lease_request
from .reopened_local_validation_authorization import validate_local_validation_authorization
from .reopened_pre_experiment_adapter import validate_reopened_pre_experiment

SCHEMA_VERSION = "1.0"
ACTIVE_STATUS = "REOPEN_LOCAL_F0_RUN_STARTED_RESOURCE_LEASE_ACTIVE"
STALE_STATUS = "REOPEN_LOCAL_F0_RUN_RESOURCE_LEASE_STALE_OR_RELEASED"
REQUIRED_STATUS = "REOPEN_LOCAL_F0_RUN_START_REQUIRED"
ZERO_SCIENTIFIC_AUTHORITY = {
    "scientific": False,
    "p0": False,
    "full_experiment": False,
    "submission": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def _recovery_contract(pre_experiment_receipt: Mapping[str, Any]) -> dict[str, Any]:
    card = pre_experiment_receipt.get("pre_experiment_card") or {}
    for gate in card.get("gates") or []:
        if isinstance(gate, Mapping) and gate.get("key") == "observability_recovery":
            detail = gate.get("detail") or {}
            return dict(detail) if isinstance(detail, Mapping) else {}
    return {}


def _expected_models(pre_experiment_receipt: Mapping[str, Any]) -> set[str]:
    card = pre_experiment_receipt.get("pre_experiment_card") or {}
    runtime = card.get("expected_runtime") or {}
    names = {str(x) for x in runtime.get("model_names") or [] if str(x).strip()}
    competence = _text(runtime.get("competence_model_name"))
    if competence:
        names.add(competence)
    return names


def run_start_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": receipt.get("contract_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "experiment_lease_sha256": receipt.get("experiment_lease_sha256"),
        "experiment_authority_id": receipt.get("experiment_authority_id"),
        "authority_epoch": receipt.get("authority_epoch"),
        "lease_request_sha256": receipt.get("lease_request_sha256"),
        "pre_experiment_adapter_sha256": receipt.get("pre_experiment_adapter_sha256"),
        "local_validation_authorization_sha256": receipt.get("local_validation_authorization_sha256"),
        "plan_hash": receipt.get("plan_hash"),
        "run_id": receipt.get("run_id"),
        "owner": receipt.get("owner"),
        "server_gpu_binding_sha256": receipt.get("server_gpu_binding_sha256"),
        "gpu_lease_id": receipt.get("gpu_lease_id"),
        "gpu_lease_epoch": receipt.get("gpu_lease_epoch"),
        "gpu_lease_expires_at": receipt.get("gpu_lease_expires_at"),
        "run_root_ref_sha256": receipt.get("run_root_ref_sha256"),
        "model_name": receipt.get("model_name"),
        "model_revision": receipt.get("model_revision"),
        "trace_recovery_policy_sha256": receipt.get("trace_recovery_policy_sha256"),
        "started_at": receipt.get("started_at"),
        "status": receipt.get("status"),
    }


def _validate_run_root(run_root: Path) -> None:
    if run_root.exists():
        raise RuntimeError("run root must be new and must not already exist")
    cursor = run_root.parent
    for parent in (cursor, *cursor.parents):
        if (parent / ".git").exists():
            raise RuntimeError("run root must live outside every git checkout/worktree")


def start_reopened_local_f0_run(
    *,
    root: Path,
    experiment_lease: Mapping[str, Any],
    lease_request: Mapping[str, Any],
    pre_experiment_receipt: Mapping[str, Any],
    local_authorization: Mapping[str, Any],
    server_id: str,
    gpu_uuid: str,
    owner: str,
    ttl_minutes: int,
    run_root: Path,
    model_name: str,
    model_revision: str,
) -> dict[str, Any]:
    root = Path(root)
    if not validate_reopened_experiment_lease(experiment_lease):
        raise RuntimeError("valid active experiment-lease receipt required")
    if not validate_experiment_lease_request(lease_request):
        raise RuntimeError("valid experiment lease request required")
    if not validate_reopened_pre_experiment(pre_experiment_receipt):
        raise RuntimeError("valid Pre-Experiment adapter receipt required")
    if not validate_local_validation_authorization(local_authorization):
        raise RuntimeError("valid local-validation authorization required")
    cid = _text(experiment_lease.get("contract_id"))
    if not cid:
        raise RuntimeError("contract id required")
    if _text(experiment_lease.get("lease_request_sha256")) != _text(lease_request.get("lease_request_sha256")):
        raise RuntimeError("run-start experiment-lease request mismatch")
    if _text(lease_request.get("pre_experiment_adapter_sha256")) != _text(pre_experiment_receipt.get("adapter_receipt_sha256")):
        raise RuntimeError("run-start Pre-Experiment lineage mismatch")
    if _text(pre_experiment_receipt.get("local_validation_authorization_sha256")) != _text(local_authorization.get("local_validation_authorization_sha256")):
        raise RuntimeError("run-start local-validation authority mismatch")
    authority_id = _text(experiment_lease.get("experiment_authority_id"))
    plan_hash = _text(experiment_lease.get("plan_hash"))
    run_id = _text(experiment_lease.get("run_id"))
    authority = validate_authority(root, cid, authority_id, plan_hash)
    if authority.get("valid") is not True:
        raise RuntimeError("experiment authority is no longer active")
    if _text((authority.get("authority") or {}).get("run_id")) != run_id:
        raise RuntimeError("experiment authority run mismatch")

    server_id = _text(server_id)
    gpu_uuid = _text(gpu_uuid)
    owner = _text(owner)
    model_name = _text(model_name)
    model_revision = _text(model_revision)
    if not server_id or not gpu_uuid or not owner:
        raise RuntimeError("server_id, gpu_uuid, and owner are required")
    if not model_name or not model_revision:
        raise RuntimeError("model_name and model_revision are required")
    expected_models = _expected_models(pre_experiment_receipt)
    if expected_models and model_name not in expected_models:
        raise RuntimeError("run-start model does not match Pre-Experiment expected runtime")
    recovery = _recovery_contract(pre_experiment_receipt)
    for key in ("incremental_trace", "atomic_progress", "heartbeat_state", "online_budget_watchdog", "per_run_lock", "gpu_uuid_binding"):
        if recovery.get(key) is not True:
            raise RuntimeError(f"run-start recovery capability missing: {key}")
    if not _text(recovery.get("restart_policy")) or not _text(recovery.get("partial_artifact_policy")):
        raise RuntimeError("run-start recovery policy incomplete")

    max_gpu_hours = float((local_authorization.get("authorized_budget") or {}).get("max_gpu_hours") or 0.0)
    if max_gpu_hours <= 0:
        raise RuntimeError("authorized GPU-hour cap missing")
    ttl_minutes = int(ttl_minutes)
    if ttl_minutes < 10 or ttl_minutes > math.ceil(max_gpu_hours * 60):
        raise RuntimeError("GPU lease TTL exceeds authorized local-validation GPU-hour cap")
    run_root = Path(run_root).expanduser().resolve()
    _validate_run_root(run_root)

    gpu_lease = acquire_gpu_lease(
        root,
        server_id,
        gpu_uuid,
        run_id,
        owner,
        idea_id=cid,
        authority_id=authority_id,
        plan_hash=plan_hash,
        ttl_minutes=ttl_minutes,
    )
    try:
        run_root.mkdir(parents=True, exist_ok=False)
        binding_sha = hashlib.sha256(f"{server_id}|{gpu_uuid}".encode()).hexdigest()
        receipt: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "receipt_type": "reopen-local-f0-run-start",
            "contract_id": cid,
            "contract_sha256": _text(experiment_lease.get("contract_sha256")),
            "experiment_lease_sha256": _text(experiment_lease.get("lease_acquisition_sha256")),
            "experiment_authority_id": authority_id,
            "authority_epoch": int(experiment_lease.get("authority_epoch") or 0),
            "lease_request_sha256": _text(lease_request.get("lease_request_sha256")),
            "pre_experiment_adapter_sha256": _text(pre_experiment_receipt.get("adapter_receipt_sha256")),
            "local_validation_authorization_sha256": _text(local_authorization.get("local_validation_authorization_sha256")),
            "plan_hash": plan_hash,
            "run_id": run_id,
            "owner": owner,
            "server_id": server_id,
            "gpu_uuid": gpu_uuid,
            "server_gpu_binding_sha256": binding_sha,
            "gpu_lease_id": _text(gpu_lease.get("lease_id")),
            "gpu_lease_epoch": int(gpu_lease.get("lease_epoch") or 0),
            "gpu_lease_expires_at": _text(gpu_lease.get("expires_at")),
            "run_root": str(run_root),
            "run_root_ref_sha256": hashlib.sha256(str(run_root).encode()).hexdigest(),
            "model_name": model_name,
            "model_revision": model_revision,
            "trace_recovery_policy": recovery,
            "trace_recovery_policy_sha256": _digest(recovery),
            "started_at": _now(),
            "status": ACTIVE_STATUS,
            "local_f0_scope_only": True,
            "experiment_authority_active_at_start": True,
            "gpu_resource_lease_active_at_start": True,
            "execution_started": True,
            "model_load_authorized": True,
            "model_loaded": False,
            "gpu_allocated": True,
            "scientific_authority": False,
            "p0_authority": False,
            "full_experiment_authority": False,
            "submission_authority": False,
        }
        receipt["run_start_sha256"] = _digest(run_start_identity(receipt))
        if not validate_reopened_local_f0_run_start(receipt):
            raise RuntimeError("generated run-start receipt failed validation")
        marker = run_root / "run-start.json"
        marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return receipt
    except Exception:
        try:
            release_gpu_lease(
                root,
                server_id,
                gpu_uuid,
                _text(gpu_lease.get("lease_id")),
                idea_id=cid,
                authority_id=authority_id,
                plan_hash=plan_hash,
                outcome="run-start-failed-before-receipt",
            )
        except Exception:
            pass
        if run_root.exists() and run_root.is_dir() and not any(run_root.iterdir()):
            run_root.rmdir()
        raise


def validate_reopened_local_f0_run_start(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-local-f0-run-start" or receipt.get("status") != ACTIVE_STATUS:
        return False
    if receipt.get("local_f0_scope_only") is not True:
        return False
    if receipt.get("experiment_authority_active_at_start") is not True or receipt.get("gpu_resource_lease_active_at_start") is not True:
        return False
    if receipt.get("execution_started") is not True or receipt.get("gpu_allocated") is not True:
        return False
    if receipt.get("model_load_authorized") is not True or receipt.get("model_loaded") is not False:
        return False
    if any(receipt.get(key) is not False for key in ("scientific_authority", "p0_authority", "full_experiment_authority", "submission_authority")):
        return False
    for key in (
        "contract_id", "contract_sha256", "experiment_lease_sha256", "experiment_authority_id", "lease_request_sha256",
        "pre_experiment_adapter_sha256", "local_validation_authorization_sha256", "plan_hash", "run_id", "server_id", "gpu_uuid",
        "server_gpu_binding_sha256", "gpu_lease_id", "gpu_lease_expires_at", "run_root", "run_root_ref_sha256", "model_name", "model_revision",
        "trace_recovery_policy_sha256", "started_at", "owner",
    ):
        if not _text(receipt.get(key)):
            return False
    if int(receipt.get("authority_epoch") or 0) <= 0 or int(receipt.get("gpu_lease_epoch") or 0) <= 0:
        return False
    if hashlib.sha256(f"{receipt.get('server_id')}|{receipt.get('gpu_uuid')}".encode()).hexdigest() != _text(receipt.get("server_gpu_binding_sha256")):
        return False
    if hashlib.sha256(_text(receipt.get("run_root")).encode()).hexdigest() != _text(receipt.get("run_root_ref_sha256")):
        return False
    if _digest(receipt.get("trace_recovery_policy") or {}) != _text(receipt.get("trace_recovery_policy_sha256")):
        return False
    return _text(receipt.get("run_start_sha256")) == _digest(run_start_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-run-starts" else root / "scientific-contract-run-starts"


def _ledger_paths(root: Path, contract_id: str) -> tuple[Path, Path]:
    directory = _directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(contract_id)
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def validate_run_start_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    cid = _text(ledger.get("contract_id")); csha = _text(ledger.get("contract_sha256")); seen: set[str] = set(); seen_experiment_leases: set[str] = set()
    if not cid or not csha:
        errors.append("run-start-ledger-identity-missing")
    if (ledger.get("authority") or {}) != ZERO_SCIENTIFIC_AUTHORITY:
        errors.append("run-start-ledger-scientific-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        if not isinstance(event, Mapping) or event.get("event_type") != "reopen-local-f0-run-start":
            errors.append("run-start-event-invalid"); continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_reopened_local_f0_run_start(receipt):
            errors.append("run-start-receipt-invalid"); continue
        if _text(receipt.get("contract_id")) != cid or _text(receipt.get("contract_sha256")) != csha:
            errors.append("run-start-contract-lineage-mismatch")
        sha = _text(receipt.get("run_start_sha256"))
        if sha in seen:
            errors.append("run-start-duplicate-receipt")
        experiment_lease_sha = _text(receipt.get("experiment_lease_sha256"))
        if experiment_lease_sha in seen_experiment_leases:
            errors.append("run-start-experiment-lease-reused")
        expected = _digest([cid, index, sha, _text(event.get("recorded_at"))])[:24]
        if _text(event.get("event_id")) != expected:
            errors.append("run-start-event-id-invalid")
        seen.add(sha); seen_experiment_leases.add(experiment_lease_sha)
    return list(dict.fromkeys(errors))


def _append_run_start_unlocked(path: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    cid = _text(receipt.get("contract_id"))
    ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "schema_version": SCHEMA_VERSION,
        "contract_id": cid,
        "contract_sha256": _text(receipt.get("contract_sha256")),
        "events": [],
        "authority": dict(ZERO_SCIENTIFIC_AUTHORITY),
    }
    if _text(ledger.get("contract_sha256")) != _text(receipt.get("contract_sha256")):
        raise RuntimeError("run-start ledger contract SHA mismatch")
    sha = _text(receipt.get("run_start_sha256"))
    for event in ledger.get("events") or []:
        prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if isinstance(prior, Mapping) and _text(prior.get("run_start_sha256")) == sha:
            return ledger
    at = _text(receipt.get("started_at"))
    event = {"event_type": "reopen-local-f0-run-start", "receipt": dict(receipt), "recorded_at": at, "scientific_authority": False, "p0_authority": False}
    event["event_id"] = _digest([cid, len(ledger.get("events") or []), sha, at])[:24]
    ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
    errors = validate_run_start_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); os.replace(tmp, path)
    return ledger


def publish_reopened_local_f0_run_start(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopened_local_f0_run_start(receipt):
        raise RuntimeError("invalid reopened local-F0 run-start receipt")
    cid = _text(receipt.get("contract_id")); path, lock = _ledger_paths(root, cid)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return _append_run_start_unlocked(path, receipt)


def start_and_publish_reopened_local_f0_run(**kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(kwargs.get("root"))
    experiment_lease = kwargs.get("experiment_lease") or {}
    cid = _text(experiment_lease.get("contract_id"))
    if not cid:
        raise RuntimeError("contract id required before atomic run start")
    path, lock = _ledger_paths(root, cid)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        lease_sha = _text(experiment_lease.get("lease_acquisition_sha256"))
        for event in existing.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if not isinstance(prior, Mapping) or _text(prior.get("experiment_lease_sha256")) != lease_sha:
                continue
            same = (
                _text(prior.get("run_id")) == _text(experiment_lease.get("run_id"))
                and _text(prior.get("server_id")) == _text(kwargs.get("server_id"))
                and _text(prior.get("gpu_uuid")) == _text(kwargs.get("gpu_uuid"))
                and Path(_text(prior.get("run_root"))).expanduser().resolve() == Path(kwargs.get("run_root")).expanduser().resolve()
                and _text(prior.get("model_name")) == _text(kwargs.get("model_name"))
                and _text(prior.get("model_revision")) == _text(kwargs.get("model_revision"))
            )
            if same and validate_reopened_local_f0_run_start(prior):
                current = public_reopened_local_f0_run(root, cid)
                if current.get("status") == ACTIVE_STATUS:
                    return dict(prior), existing
                raise RuntimeError("this experiment lease already has a stale/released formal run start and cannot be reused")
            raise RuntimeError("this experiment lease already has a different formal run start")
        receipt = start_reopened_local_f0_run(**kwargs)
        try:
            ledger = _append_run_start_unlocked(path, receipt)
            return receipt, ledger
        except Exception:
            try:
                release_gpu_lease(
                    root,
                    _text(receipt.get("server_id")),
                    _text(receipt.get("gpu_uuid")),
                    _text(receipt.get("gpu_lease_id")),
                    idea_id=cid,
                    authority_id=_text(receipt.get("experiment_authority_id")),
                    plan_hash=_text(receipt.get("plan_hash")),
                    outcome="run-start-ledger-publish-failed",
                )
            except Exception:
                pass
            run_root = Path(_text(receipt.get("run_root")))
            marker = run_root / "run-start.json"
            try:
                if marker.exists(): marker.unlink()
                if run_root.exists() and run_root.is_dir() and not any(run_root.iterdir()): run_root.rmdir()
            except OSError:
                pass
            raise


def public_reopened_local_f0_run(root: Path, contract_id: str, *, resource_root: Path | None = None, authority_root: Path | None = None) -> dict[str, Any]:
    empty = {
        "status": REQUIRED_STATUS,
        "contract_id": contract_id,
        "run_start_sha256": "",
        "run_id": "",
        "model_name": "",
        "model_revision": "",
        "server_gpu_binding_sha256": "",
        "gpu_lease_id": "",
        "experiment_authority_active": False,
        "resource_lease_active": False,
        "execution_started": False,
        "model_loaded": False,
        "gpu_allocated": False,
        "authority": dict(ZERO_SCIENTIFIC_AUTHORITY),
    }
    path = _directory(root) / f"{_slug(contract_id)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {**empty, "status": "REOPEN_LOCAL_F0_RUN_LEDGER_INVALID"}
    if validate_run_start_ledger(ledger):
        return {**empty, "status": "REOPEN_LOCAL_F0_RUN_LEDGER_INVALID"}
    receipts = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)]
    receipt = receipts[-1] if receipts else {}
    if not receipt or not validate_reopened_local_f0_run_start(receipt):
        return {**empty, "status": "REOPEN_LOCAL_F0_RUN_LEDGER_INVALID"}
    ledger_root = Path(root)
    inferred_base = ledger_root.parent if ledger_root.name == "scientific-contract-run-starts" else ledger_root
    authority_base = Path(authority_root) if authority_root is not None else inferred_base
    resource_base = Path(resource_root) if resource_root is not None else inferred_base
    exp = validate_authority(authority_base, contract_id, _text(receipt.get("experiment_authority_id")), _text(receipt.get("plan_hash")))
    resource = next((row for row in list_gpu_leases(resource_base, active_only=False) if _text(row.get("lease_id")) == _text(receipt.get("gpu_lease_id"))), {})
    resource_lineage_ok = bool(resource) and all((
        _text(resource.get("run_id")) == _text(receipt.get("run_id")),
        _text(resource.get("idea_id")) == contract_id,
        _text(resource.get("plan_hash")) == _text(receipt.get("plan_hash")),
        _text(resource.get("authority_id")) == _text(receipt.get("experiment_authority_id")),
        hashlib.sha256(f"{resource.get('server_id')}|{resource.get('gpu_uuid')}".encode()).hexdigest() == _text(receipt.get("server_gpu_binding_sha256")),
    ))
    resource_active = resource_lineage_ok and resource.get("status") == "active"
    if resource_active:
        try:
            resource_active = datetime.fromisoformat(_text(resource.get("expires_at"))) > datetime.now(timezone.utc)
        except ValueError:
            resource_active = True
    current = exp.get("valid") is True and resource_active
    return {
        **empty,
        "status": ACTIVE_STATUS if current else STALE_STATUS,
        "run_start_sha256": _text(receipt.get("run_start_sha256")),
        "run_id": _text(receipt.get("run_id")),
        "model_name": _text(receipt.get("model_name")),
        "model_revision": _text(receipt.get("model_revision")),
        "server_gpu_binding_sha256": _text(receipt.get("server_gpu_binding_sha256")),
        "gpu_lease_id": _text(receipt.get("gpu_lease_id")),
        "experiment_authority_active": exp.get("valid") is True,
        "resource_lease_active": resource_active,
        "execution_started": current,
        "model_loaded": False,
        "gpu_allocated": current,
    }
