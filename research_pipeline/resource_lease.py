from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .experiment_authority import validate_authority


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "resource"


def _paths(root: Path, server_id: str, gpu_uuid: str) -> tuple[Path, Path]:
    directory = root / "resource-leases"
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(f"{server_id}-{gpu_uuid}")
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _atomic(path: Path, row: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _active(row: dict[str, Any]) -> bool:
    if row.get("status") != "active":
        return False
    try:
        return datetime.fromisoformat(str(row.get("expires_at"))) > _now()
    except ValueError:
        return True


def _require_authority(
    root: Path,
    *,
    idea_id: str,
    authority_id: str,
    run_id: str,
    plan_hash: str = "",
) -> dict[str, Any]:
    if not idea_id or not authority_id:
        raise RuntimeError("GPU lease requires active experiment authority")
    validation = validate_authority(root, idea_id, authority_id, plan_hash)
    if validation.get("valid") is not True:
        raise RuntimeError("GPU lease requires active experiment authority")
    authority = validation.get("authority") or {}
    if str(authority.get("run_id") or "") != str(run_id):
        raise RuntimeError("GPU lease authority run mismatch")
    return authority


def _acquire_gpu_lease_unchecked(
    root: Path,
    server_id: str,
    gpu_uuid: str,
    run_id: str,
    owner: str,
    authority: dict[str, Any],
    ttl_minutes: int,
) -> dict[str, Any]:
    path, lock = _paths(root, server_id, gpu_uuid)
    with lock.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        old = _read(path)
        if _active(old):
            if old.get("run_id") == run_id and old.get("authority_id") == authority.get("authority_id"):
                return old
            raise RuntimeError(f"GPU lease already active on {server_id}:{gpu_uuid}: run={old.get('run_id')}")
        epoch = int(old.get("lease_epoch") or 0) + 1
        now = _now()
        lease_id = hashlib.sha256(f"{server_id}|{gpu_uuid}|{run_id}|{epoch}".encode()).hexdigest()[:24]
        row = {
            "schema_version": "1.1",
            "server_id": server_id,
            "gpu_uuid": gpu_uuid,
            "run_id": run_id,
            "owner": owner,
            "idea_id": str(authority.get("idea_id") or ""),
            "plan_hash": str(authority.get("plan_hash") or ""),
            "authority_id": str(authority.get("authority_id") or ""),
            "authority_epoch": int(authority.get("authority_epoch") or 0),
            "lease_epoch": epoch,
            "lease_id": lease_id,
            "status": "active",
            "acquired_at": _iso(now),
            "expires_at": _iso(now + timedelta(minutes=max(10, ttl_minutes))),
        }
        _atomic(path, row)
        return row


def acquire_gpu_lease(
    root: Path,
    server_id: str,
    gpu_uuid: str,
    run_id: str,
    owner: str,
    *,
    idea_id: str,
    authority_id: str,
    plan_hash: str = "",
    ttl_minutes: int = 720,
) -> dict[str, Any]:
    """Acquire a GPU capability only under a live matching experiment authority."""
    authority = _require_authority(
        root,
        idea_id=idea_id,
        authority_id=authority_id,
        run_id=run_id,
        plan_hash=plan_hash,
    )
    return _acquire_gpu_lease_unchecked(root, server_id, gpu_uuid, run_id, owner, authority, ttl_minutes)


def _release_gpu_lease_unchecked(
    root: Path,
    server_id: str,
    gpu_uuid: str,
    lease_id: str,
    outcome: str,
) -> dict[str, Any]:
    path, lock = _paths(root, server_id, gpu_uuid)
    with lock.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = _read(path)
        if row.get("status") != "active" or row.get("lease_id") != lease_id:
            raise RuntimeError("GPU lease release mismatch")
        row = {**row, "status": "released", "release_outcome": outcome, "released_at": _iso(_now())}
        _atomic(path, row)
        return row


def release_gpu_lease(
    root: Path,
    server_id: str,
    gpu_uuid: str,
    lease_id: str,
    *,
    idea_id: str,
    authority_id: str,
    plan_hash: str = "",
    outcome: str = "released",
) -> dict[str, Any]:
    """Release a live GPU lease under the same authority that acquired it."""
    path, _ = _paths(root, server_id, gpu_uuid)
    row = _read(path)
    if row.get("status") != "active" or row.get("lease_id") != lease_id:
        raise RuntimeError("GPU lease release mismatch")
    authority = _require_authority(
        root,
        idea_id=idea_id,
        authority_id=authority_id,
        run_id=str(row.get("run_id") or ""),
        plan_hash=plan_hash or str(row.get("plan_hash") or ""),
    )
    if str(row.get("authority_id") or "") != str(authority.get("authority_id") or ""):
        raise RuntimeError("GPU lease release authority mismatch")
    return _release_gpu_lease_unchecked(root, server_id, gpu_uuid, lease_id, outcome)


def list_gpu_leases(root: Path, active_only: bool = True) -> list[dict[str, Any]]:
    directory = root / "resource-leases"
    rows: list[dict[str, Any]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json")):
        row = _read(path)
        if not row:
            continue
        if active_only and not _active(row):
            continue
        rows.append({"path": str(path), **row})
    return rows


def active_gpu_uuids(root: Path) -> set[str]:
    return {str(row.get("gpu_uuid")) for row in list_gpu_leases(root, True) if row.get("gpu_uuid")}


def reconcile_gpu_leases(root: Path, active_run_ids: set[str], grace_seconds: int = 300) -> list[dict[str, Any]]:
    """Controller-owned orphan cleanup; this is not a path for acquiring new capability."""
    released: list[dict[str, Any]] = []
    now = _now()
    for row in list_gpu_leases(root, True):
        if str(row.get("run_id")) in active_run_ids:
            continue
        try:
            acquired = datetime.fromisoformat(str(row.get("acquired_at")))
        except ValueError:
            continue
        if (now - acquired).total_seconds() < grace_seconds:
            continue
        try:
            released.append(
                _release_gpu_lease_unchecked(
                    root,
                    str(row.get("server_id")),
                    str(row.get("gpu_uuid")),
                    str(row.get("lease_id")),
                    "reconciled-no-active-run",
                )
            )
        except RuntimeError:
            pass
    return released
