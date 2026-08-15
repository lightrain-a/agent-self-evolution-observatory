from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_support_asset_recheck import load_private_support_asset_recheck_queue

SCHEMA_VERSION = "1.0"


def _now(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _root(storage: StorageSettings) -> Path:
    return storage.data_root / "paper-first-problem-discovery" / "support-release-watch"


def _path(storage: StorageSettings) -> Path:
    return _root(storage) / "asset-recheck-handoff.json"


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_sha(value: Any) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", str(value or "")))


def build_support_asset_recheck_handoff(
    *,
    storage: StorageSettings | None = None,
    queue_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    queue_state = queue_state if queue_state is not None else load_private_support_asset_recheck_queue(storage=storage)
    entries: list[dict[str, Any]] = []
    ready = incomplete = 0
    for row in queue_state.get("entries") or []:
        if not isinstance(row, dict) or str(row.get("queue_status") or "") != "AWAIT_ASSET_RECHECK":
            continue
        candidate_id = str(row.get("candidate_id") or "")
        queue_id = str(row.get("queue_id") or "")
        trigger_digest = str(row.get("latest_trigger_digest") or "")
        source_run_id = str(row.get("source_run_id") or "")
        stage_sha = str(row.get("source_stage_manifest_sha256") or "")
        provenance_ok = bool(candidate_id and _valid_sha(queue_id) and _valid_sha(trigger_digest) and source_run_id and _valid_sha(stage_sha))
        handoff_status = "READY_FOR_SUPPORT_INVENTORY_RECHECK" if provenance_ok else "HOLD_RECHECK_HANDOFF_PROVENANCE_INCOMPLETE"
        ready += int(provenance_ok)
        incomplete += int(not provenance_ok)
        entries.append({
            "handoff_id": _sha(f"{queue_id}\n{trigger_digest}\n{source_run_id}"),
            "queue_id": queue_id,
            "candidate_id": candidate_id,
            "handoff_status": handoff_status,
            "latest_trigger_digest": trigger_digest,
            "source_run_id": source_run_id,
            "source_stage_manifest_sha256": stage_sha,
            "source_refs": list(row.get("source_refs") or []),
            "required_unit": str(row.get("required_unit") or ""),
            "reopen_only_if": str(row.get("reopen_only_if") or ""),
            "next_entrypoint": "research_pipeline.paper_first_problem_falsifier_preflight",
            "next_action": "support-inventory-recheck",
            "support_inventory_scope": "direct released units or materialized independent truth from first-party code / existing provenance substrate",
            "support_inventory_request_required": True,
            "automatic_execution_authorized": False,
            "provider_calls_authorized": False,
            "support_qualified": False,
            "falsifier_execution_authorized": False,
            "generator_reopen_authorized": False,
            "problem_gate_authorized": False,
            "method_authorized": False,
            "experiment_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "scientific_authority": False,
        })
    summary = {
        "queued_asset_rechecks": len(entries),
        "support_inventory_recheck_ready": ready,
        "provenance_incomplete": incomplete,
        "automatic_execution_authorized": 0,
        "provider_calls_authorized": 0,
        "support_qualified": 0,
        "falsifier_execution_authorized": 0,
        "generator_reopen_authorized": 0,
        "problem_gate_authorized": 0,
        "method_authorized": 0,
        "experiment_authorized": 0,
        "p0_authorized": 0,
        "gpu_authorized": 0,
    }
    if not entries:
        status = "SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY"
    elif incomplete:
        status = "SUPPORT_ASSET_RECHECK_HANDOFF_HOLD_PROVENANCE"
    else:
        status = "SUPPORT_ASSET_RECHECK_HANDOFF_READY"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(now),
        "status": status,
        "policy": {
            "scientific_authority": False,
            "handoff_reuses_existing_problem_falsifier_support_inventory": True,
            "asset_recheck_cannot_define_a_parallel_support_gate": True,
            "release_change_is_not_support_qualification": True,
            "support_inventory_receipt_required_before_any_support_decision": True,
            "support_inventory_must_consider_direct_or_reconstructed_truth": True,
            "reconstructed_truth_requires_materialized_units_and_provenance_before_qualification": True,
            "problem_falsifier_preflight_remains_support_authority_boundary": True,
            "handoff_cannot_execute_falsifier_automatically": True,
            "handoff_cannot_reopen_generator_or_problem_gate": True,
            "handoff_cannot_authorize_method_experiment_p0_gpu": True,
            "automatic_provider_calls_authorized": False,
        },
        "summary": summary,
        "entries": entries,
        "scientific_authority": False,
    }


def load_private_support_asset_recheck_handoff(
    *,
    storage: StorageSettings | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    path = path or _path(storage)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "status": "NOT_RUN", "policy": {"scientific_authority": False}, "summary": {}, "entries": [], "scientific_authority": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": SCHEMA_VERSION, "status": "STATE_UNREADABLE", "policy": {"scientific_authority": False}, "summary": {}, "entries": [], "scientific_authority": False}
    return payload if isinstance(payload, dict) else {"schema_version": SCHEMA_VERSION, "status": "STATE_INVALID", "policy": {"scientific_authority": False}, "summary": {}, "entries": [], "scientific_authority": False}


def public_support_asset_recheck_handoff_summary(state: dict[str, Any]) -> dict[str, Any]:
    summary = state.get("summary") or {}
    safe_keys = (
        "queued_asset_rechecks", "support_inventory_recheck_ready", "provenance_incomplete",
        "automatic_execution_authorized", "provider_calls_authorized", "support_qualified",
        "falsifier_execution_authorized", "generator_reopen_authorized", "problem_gate_authorized",
        "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": str(state.get("status") or "NOT_RUN"),
        "policy": {
            "scientific_authority": False,
            "handoff_reuses_existing_problem_falsifier_support_inventory": True,
            "asset_recheck_cannot_define_a_parallel_support_gate": True,
            "release_change_is_not_support_qualification": True,
            "support_inventory_receipt_required_before_any_support_decision": True,
            "support_inventory_must_consider_direct_or_reconstructed_truth": True,
            "reconstructed_truth_requires_materialized_units_and_provenance_before_qualification": True,
            "problem_falsifier_preflight_remains_support_authority_boundary": True,
            "handoff_cannot_execute_falsifier_automatically": True,
            "handoff_cannot_reopen_generator_or_problem_gate": True,
            "handoff_cannot_authorize_method_experiment_p0_gpu": True,
            "automatic_provider_calls_authorized": False,
            "public_summary_excludes_entries_refs_urls_required_units_and_private_paths": True,
        },
        "summary": {key: int(summary.get(key) or 0) for key in safe_keys},
        "scientific_authority": False,
    }


def write_private_support_asset_recheck_handoff(
    *,
    storage: StorageSettings | None = None,
    queue_state: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state = build_support_asset_recheck_handoff(storage=storage, queue_state=queue_state, now=now)
    path = _path(storage)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return state
