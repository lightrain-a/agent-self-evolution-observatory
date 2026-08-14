from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_search_portfolio_design_adjudication import build_search_portfolio_design_adjudication
from .paper_first_support_release_watch import load_private_support_release_watch

SCHEMA_VERSION = "1.0"
QUEUE_STATUS = "AWAIT_ASSET_RECHECK"


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "support-release-watch"


def _queue_path(storage: StorageSettings) -> Path:
    return _root(storage) / "asset-recheck-queue.json"


def _bounded(value: Any, limit: int = 1800) -> str:
    return " ".join(str(value or "").split())[:limit]


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _current_holds(design_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    memory = design_state.get("shadow_dead_end_memory") or {}
    rows = memory.get("blocked_objects") or []
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        candidate_id = str(row.get("source_candidate_id") or "")
        if (
            candidate_id
            and str(row.get("disposition") or "") == "HOLD_SUPPORT_UNAVAILABLE"
            and str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-")
        ):
            out[candidate_id] = row
    return out


def _load_previous(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def build_support_asset_recheck_queue(
    *,
    storage: StorageSettings | None = None,
    watch_state: dict[str, Any] | None = None,
    design_state: dict[str, Any] | None = None,
    previous_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    watch_state = watch_state if watch_state is not None else load_private_support_release_watch(storage=storage)
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    previous_state = previous_state if previous_state is not None else _load_previous(_queue_path(storage))
    holds = _current_holds(design_state)
    prior_entries = {
        str(row.get("candidate_id") or ""): dict(row)
        for row in previous_state.get("entries") or []
        if isinstance(row, dict)
        and row.get("queue_status") == QUEUE_STATUS
        and str(row.get("candidate_id") or "") in holds
    }
    signals: dict[str, list[dict[str, Any]]] = {}
    for row in watch_state.get("rows") or []:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "")
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in holds and status.startswith("RECHECK_REQUIRED_"):
            signals.setdefault(candidate_id, []).append(row)

    entries: list[dict[str, Any]] = []
    new_triggers = 0
    carried_forward = 0
    for candidate_id in sorted(set(prior_entries) | set(signals)):
        hold = holds[candidate_id]
        prior = prior_entries.get(candidate_id) or {}
        rows = signals.get(candidate_id) or []
        fingerprints = sorted({str(row.get("fingerprint") or "") for row in rows if len(str(row.get("fingerprint") or "")) == 64})
        trigger_material = "\n".join(
            sorted(
                f"{str(row.get('declaration_kind') or '')}:{str(row.get('url') or '')}:{str(row.get('fingerprint') or '')}:{str(row.get('status') or '')}"
                for row in rows
            )
        )
        prior_trigger_digest = str(prior.get("latest_trigger_digest") or "")
        latest_trigger_digest = _sha(trigger_material) if trigger_material else prior_trigger_digest
        if rows and latest_trigger_digest != prior_trigger_digest:
            new_triggers += 1
        elif prior:
            carried_forward += 1
        first_queued_at = str(prior.get("first_queued_at") or _now(now))
        source_refs = sorted({str(x) for x in (hold.get("evidence_basis") or []) + (hold.get("current_source_refs") or []) if str(x)})
        entries.append({
            "queue_id": _sha(f"{candidate_id}\n{first_queued_at}"),
            "candidate_id": candidate_id,
            "queue_status": QUEUE_STATUS,
            "trigger_statuses": sorted({str(row.get("status") or "") for row in rows}) or list(prior.get("trigger_statuses") or []),
            "trigger_fingerprints": fingerprints or list(prior.get("trigger_fingerprints") or []),
            "latest_trigger_digest": latest_trigger_digest,
            "first_queued_at": first_queued_at,
            "last_triggered_at": _now(now) if rows else str(prior.get("last_triggered_at") or first_queued_at),
            "source_refs": source_refs,
            "source_run_id": str(hold.get("source_run_id") or ""),
            "source_stage_manifest_sha256": str(hold.get("source_stage_manifest_sha256") or ""),
            "required_unit": _bounded(hold.get("required_unit")),
            "reopen_only_if": _bounded(hold.get("reopen_only_if")),
            "strongest_reduction": _bounded(hold.get("strongest_reduction")),
            "recheck_instruction": "Re-audit the changed primary/author release against the frozen required unit. A release change is not support; only an explicit asset-resolution artifact may resolve this queue entry.",
            "support_qualified": False,
            "generator_reopen_authorized": False,
            "problem_gate_authorized": False,
            "method_authorized": False,
            "experiment_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "scientific_authority": False,
        })

    summary = {
        "support_holds": len(holds),
        "release_recheck_signals": sum(len(rows) for rows in signals.values()),
        "queued": len(entries),
        "new_triggers": new_triggers,
        "carried_forward": carried_forward,
        "support_qualified": 0,
        "generator_reopen_authorized": 0,
        "problem_gate_authorized": 0,
        "method_authorized": 0,
        "experiment_authorized": 0,
        "p0_authorized": 0,
        "gpu_authorized": 0,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": "SUPPORT_ASSET_RECHECK_QUEUE_READY" if entries else "SUPPORT_ASSET_RECHECK_QUEUE_EMPTY",
        "policy": {
            "scientific_authority": False,
            "release_change_only_creates_asset_recheck_task": True,
            "queue_is_durable_across_release_watch_cooldown": True,
            "queue_only_tracks_current_support_holds": True,
            "queue_cannot_mark_support_qualified": True,
            "queue_cannot_reopen_generator_or_problem_gate": True,
            "queue_cannot_authorize_method_experiment_p0_gpu": True,
            "explicit_asset_resolution_required_to_clear_entry": True,
            "automatic_provider_calls_authorized": False,
        },
        "summary": summary,
        "entries": entries,
        "scientific_authority": False,
    }


def load_private_support_asset_recheck_queue(
    *,
    storage: StorageSettings | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = path or _queue_path(storage)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "status": "NOT_RUN", "policy": {"scientific_authority": False}, "summary": {}, "entries": [], "scientific_authority": False}
    payload = _load_previous(path)
    return payload if payload else {"schema_version": SCHEMA_VERSION, "status": "STATE_UNREADABLE", "policy": {"scientific_authority": False}, "summary": {}, "entries": [], "scientific_authority": False}


def public_support_asset_recheck_summary(state: dict[str, Any]) -> dict[str, Any]:
    summary = state.get("summary") or {}
    safe_keys = (
        "support_holds", "release_recheck_signals", "queued", "new_triggers", "carried_forward",
        "support_qualified", "generator_reopen_authorized", "problem_gate_authorized",
        "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": str(state.get("status") or "NOT_RUN"),
        "policy": {
            "scientific_authority": False,
            "release_change_only_creates_asset_recheck_task": True,
            "queue_is_durable_across_release_watch_cooldown": True,
            "queue_only_tracks_current_support_holds": True,
            "queue_cannot_mark_support_qualified": True,
            "queue_cannot_reopen_generator_or_problem_gate": True,
            "queue_cannot_authorize_method_experiment_p0_gpu": True,
            "explicit_asset_resolution_required_to_clear_entry": True,
            "automatic_provider_calls_authorized": False,
            "public_summary_excludes_entries_refs_urls_required_units_and_private_paths": True,
        },
        "summary": {key: summary[key] for key in safe_keys if key in summary},
        "scientific_authority": False,
    }


def write_private_support_asset_recheck_queue(
    *,
    storage: StorageSettings | None = None,
    watch_state: dict[str, Any] | None = None,
    design_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = _queue_path(storage)
    state = build_support_asset_recheck_queue(
        storage=storage,
        watch_state=watch_state,
        design_state=design_state,
        previous_state=_load_previous(path),
        now=now,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state
