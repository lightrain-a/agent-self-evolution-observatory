from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_search_portfolio_design_adjudication import build_search_portfolio_design_adjudication
from .paper_first_support_release_watch import current_support_holds, load_private_support_release_watch

SCHEMA_VERSION = "1.0"
QUEUE_STATUS = "AWAIT_ASSET_RECHECK"
ALLOWED_RESOLUTIONS = {"RECHECKED_SUPPORT_STILL_UNAVAILABLE", "RECHECKED_RELEASE_IRRELEVANT"}


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "support-release-watch"


def _queue_path(storage: StorageSettings) -> Path:
    return _root(storage) / "asset-recheck-queue.json"


def _resolution_path(storage: StorageSettings) -> Path:
    return _root(storage) / "asset-recheck-resolutions.json"


def _bounded(value: Any, limit: int = 1800) -> str:
    return " ".join(str(value or "").split())[:limit]


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hold_source_refs(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted({
        str(value) for value in (row.get("evidence_basis") or []) + (row.get("current_source_refs") or [])
        if str(value).startswith("arXiv:")
    }))


def _support_hold_key(row: dict[str, Any]) -> str:
    material = "\n".join((
        str(row.get("source_candidate_id") or ""),
        str(row.get("source_run_id") or ""),
        str(row.get("basin") or ""),
        "|".join(_hold_source_refs(row)),
    ))
    return _sha(material)


def _current_holds(design_state: dict[str, Any], *, storage: StorageSettings) -> dict[str, dict[str, Any]]:
    """Return the exact support-HOLD population used by the release watcher."""
    out: dict[str, dict[str, Any]] = {}
    for row in current_support_holds(design_state, storage=storage):
        if not isinstance(row, dict) or row.get("scientific_authority") is not False:
            continue
        candidate_id = str(row.get("source_candidate_id") or "")
        if candidate_id and str(row.get("disposition") or "") == "HOLD_SUPPORT_UNAVAILABLE" and row.get("dead_end_certified") is not True:
            key = _support_hold_key(row)
            out.setdefault(key, dict(row))
    return out


def _load_previous(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def load_private_support_asset_resolutions(
    *,
    storage: StorageSettings | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = path or _resolution_path(storage)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "status": "NOT_RUN", "resolutions": [], "scientific_authority": False}
    payload = _load_previous(path)
    return payload if payload else {"schema_version": SCHEMA_VERSION, "status": "STATE_UNREADABLE", "resolutions": [], "scientific_authority": False}


def validate_support_asset_resolution_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("scientific_authority") is not False:
        errors.append("support asset resolution cannot carry scientific authority")
    rows = [row for row in state.get("resolutions") or [] if isinstance(row, dict)]
    seen: set[str] = set()
    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        digest = str(row.get("resolved_trigger_digest") or "")
        disposition = str(row.get("disposition") or "")
        if not candidate_id or candidate_id in seen:
            errors.append("support asset resolution candidate ids must be nonempty and unique")
        seen.add(candidate_id)
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            errors.append("support asset resolution must bind one 64-hex trigger digest")
        if disposition not in ALLOWED_RESOLUTIONS:
            errors.append("support asset resolution disposition invalid")
        if not str(row.get("resolution_reason") or "").strip():
            errors.append("support asset resolution requires a bounded reason")
        if row.get("scientific_authority") is not False:
            errors.append("support asset resolution row cannot carry scientific authority")
        if row.get("support_qualified") is not False or row.get("generator_reopen_authorized") is not False or row.get("problem_gate_authorized") is not False:
            errors.append("support asset resolution cannot qualify support or reopen canonical discovery")
    return sorted(set(errors))


def write_private_support_asset_resolutions(
    resolutions: list[dict[str, Any]],
    *,
    storage: StorageSettings | None = None,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = path or _resolution_path(storage)
    state = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": "SUPPORT_ASSET_RESOLUTIONS_RECORDED" if resolutions else "SUPPORT_ASSET_RESOLUTIONS_EMPTY",
        "resolutions": [dict(row) for row in resolutions],
        "scientific_authority": False,
    }
    errors = validate_support_asset_resolution_state(state)
    if errors:
        raise ValueError("Invalid support asset resolution state: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state


def build_support_asset_recheck_queue(
    *,
    storage: StorageSettings | None = None,
    watch_state: dict[str, Any] | None = None,
    design_state: dict[str, Any] | None = None,
    previous_state: dict[str, Any] | None = None,
    resolution_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    watch_state = watch_state if watch_state is not None else load_private_support_release_watch(storage=storage)
    design_state = design_state if design_state is not None else build_search_portfolio_design_adjudication()
    previous_state = previous_state if previous_state is not None else _load_previous(_queue_path(storage))
    resolution_state = resolution_state if resolution_state is not None else load_private_support_asset_resolutions(storage=storage)
    resolution_errors = validate_support_asset_resolution_state(resolution_state)
    if resolution_errors:
        raise ValueError("Invalid support asset resolution state: " + ";".join(resolution_errors))
    resolutions = {
        str(row.get("candidate_id") or ""): dict(row)
        for row in resolution_state.get("resolutions") or []
        if isinstance(row, dict) and str(row.get("candidate_id") or "")
    }
    holds = _current_holds(design_state, storage=storage)
    prior_entries: dict[str, dict[str, Any]] = {}
    for row in previous_state.get("entries") or []:
        if not isinstance(row, dict) or row.get("queue_status") != QUEUE_STATUS:
            continue
        explicit_key = str(row.get("support_hold_key") or "")
        if explicit_key in holds:
            prior_entries[explicit_key] = dict(row)
            continue
        candidate_id = str(row.get("candidate_id") or "")
        source_run_id = str(row.get("source_run_id") or "")
        source_refs = {str(value) for value in row.get("source_refs") or [] if str(value)}
        matches = [
            key for key, hold in holds.items()
            if str(hold.get("source_candidate_id") or "") == candidate_id
            and (not source_run_id or str(hold.get("source_run_id") or "") == source_run_id)
            and (not source_refs or source_refs == set(_hold_source_refs(hold)))
        ]
        if len(matches) == 1:
            prior_entries[matches[0]] = dict(row)
    signals: dict[str, list[dict[str, Any]]] = {}
    for row in watch_state.get("rows") or []:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "")
        if not status.startswith("RECHECK_REQUIRED_"):
            continue
        candidate_id = str(row.get("candidate_id") or "")
        source_ref = str(row.get("source_ref") or "")
        if source_ref:
            matches = [
                key for key, hold in holds.items()
                if str(hold.get("source_candidate_id") or "") == candidate_id
                and source_ref in _hold_source_refs(hold)
            ]
        else:
            # Legacy watch rows did not publish source_ref.  Preserve them only
            # when candidate_id identifies exactly one current hold; reused ids
            # remain fail-closed until provenance is available.
            matches = [
                key for key, hold in holds.items()
                if str(hold.get("source_candidate_id") or "") == candidate_id
            ]
        # Shadow candidate ids are reused across runs; an ambiguous trigger is
        # safer to ignore than to attach to the wrong frozen support contract.
        if len(matches) == 1:
            signals.setdefault(matches[0], []).append(row)

    entries: list[dict[str, Any]] = []
    new_triggers = 0
    carried_forward = 0
    resolved = 0
    resolution_still_unavailable = 0
    resolution_irrelevant_release = 0
    for hold_key in sorted(set(prior_entries) | set(signals)):
        hold = holds[hold_key]
        candidate_id = str(hold.get("source_candidate_id") or "")
        prior = prior_entries.get(hold_key) or {}
        rows = signals.get(hold_key) or []
        fingerprints = sorted({str(row.get("fingerprint") or "") for row in rows if len(str(row.get("fingerprint") or "")) == 64})
        trigger_material = "\n".join(
            sorted(
                f"{str(row.get('declaration_kind') or '')}:{str(row.get('url') or '')}:{str(row.get('fingerprint') or '')}:{str(row.get('status') or '')}"
                for row in rows
            )
        )
        prior_trigger_digest = str(prior.get("latest_trigger_digest") or "")
        latest_trigger_digest = _sha(trigger_material) if trigger_material else prior_trigger_digest
        resolution = resolutions.get(candidate_id) or {}
        resolution_matches = bool(latest_trigger_digest and str(resolution.get("resolved_trigger_digest") or "") == latest_trigger_digest)
        if resolution_matches:
            resolved += 1
            disposition = str(resolution.get("disposition") or "")
            resolution_still_unavailable += int(disposition == "RECHECKED_SUPPORT_STILL_UNAVAILABLE")
            resolution_irrelevant_release += int(disposition == "RECHECKED_RELEASE_IRRELEVANT")
            continue
        if rows and latest_trigger_digest != prior_trigger_digest:
            new_triggers += 1
        elif prior:
            carried_forward += 1
        first_queued_at = str(prior.get("first_queued_at") or _now(now))
        source_refs = sorted({str(x) for x in (hold.get("evidence_basis") or []) + (hold.get("current_source_refs") or []) if str(x)})
        entries.append({
            "queue_id": _sha(f"{hold_key}\n{first_queued_at}"),
            "support_hold_key": hold_key,
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
            "recheck_instruction": "Re-audit the changed primary/author release through the existing support-inventory handoff. Check directly released units and first-party reconstruction under the frozen operationalization. A release change alone is not support; qualification still requires materialized units and provenance.",
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
        "resolved": resolved,
        "resolution_still_unavailable": resolution_still_unavailable,
        "resolution_irrelevant_release": resolution_irrelevant_release,
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
            "asset_resolution_must_bind_latest_trigger_digest": True,
            "asset_resolution_cannot_mark_support_qualified_or_reopen": True,
            "support_inventory_recheck_remains_queue_handoff_not_resolution": True,
            "support_inventory_recheck_considers_direct_or_reconstructed_truth": True,
            "reconstruction_requires_materialized_units_and_provenance": True,
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
        "support_holds", "release_recheck_signals", "queued", "new_triggers", "carried_forward", "resolved",
        "resolution_still_unavailable", "resolution_irrelevant_release",
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
            "asset_resolution_must_bind_latest_trigger_digest": True,
            "asset_resolution_cannot_mark_support_qualified_or_reopen": True,
            "support_inventory_recheck_remains_queue_handoff_not_resolution": True,
            "support_inventory_recheck_considers_direct_or_reconstructed_truth": True,
            "reconstruction_requires_materialized_units_and_provenance": True,
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
    resolution_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = _queue_path(storage)
    state = build_support_asset_recheck_queue(
        storage=storage,
        watch_state=watch_state,
        design_state=design_state,
        previous_state=_load_previous(path),
        resolution_state=resolution_state,
        now=now,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state
