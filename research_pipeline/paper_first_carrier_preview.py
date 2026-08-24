from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .paper_first_primary_evidence import DEFAULT_JSON as PRIMARY_JSON, build_primary_evidence_pool
from .paper_first_problem_generator import (
    DEFAULT_JSON as GENERATOR_JSON,
    _has_current_operator_receipt,
    _pool_sha,
)
from .paper_first_problem_gate_queue import DEFAULT_JSON as QUEUE_JSON


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preview_action(public: dict[str, Any], *, current_operator_receipt: bool | None = None) -> str:
    summary = public.get("summary") or {}
    if summary.get("source_retrieval_complete") is not True:
        return "RETRIEVAL_INCOMPLETE_NO_AUTHORITY"
    if int(summary.get("unreviewed_lane_linked_sources") or 0) > 0:
        return "NEW_LANE_GROUNDED_SOURCE_PRESENT"
    if int(summary.get("carrier_probe_pending") or 0) > 0:
        return "CARRIER_PROBE_PENDING_ZERO_CALL"
    if summary.get("source_coverage_exhausted") is True:
        if current_operator_receipt is True:
            return "SOURCE_COVERAGE_SATURATED_ZERO_CALL"
        if current_operator_receipt is False:
            return "SOURCE_COVERAGE_SATURATED_OPERATOR_RECOMPILE_REQUIRED"
        return "SOURCE_COVERAGE_SATURATED_OPERATOR_RECEIPT_UNKNOWN_NO_AUTHORITY"
    return "NO_LIVE_ACTION_PREVIEW_ONLY"


def run_carrier_preview(
    *,
    storage: StorageSettings | None = None,
    primary_state_path: Path = PRIMARY_JSON,
    generator_state_path: Path = GENERATOR_JSON,
    queue_state_path: Path = QUEUE_JSON,
    output_dir: Path | None = None,
    now: datetime | None = None,
    primary_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a complete Primary-only preview and persist a private recovery receipt.

    This function may update private content-addressed primary/full-text caches.
    It never writes canonical Primary/Generator/Queue state and never calls a
    generator or reviewer. The private artifact exists so a client/MCP transport
    failure cannot erase the result of a long retrieval window.
    """
    storage = storage or StorageSettings.from_env()
    storage.ensure()
    output_dir = output_dir or (storage.run_dir / "paper-first-carrier-previews")
    output_dir.mkdir(parents=True, exist_ok=True)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    canonical_paths = {
        "primary": Path(primary_state_path),
        "generator": Path(generator_state_path),
        "queue": Path(queue_state_path),
    }
    before = {key: _file_sha256(path) for key, path in canonical_paths.items()}
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": current.replace(microsecond=0).isoformat(),
        "status": "PRIVATE_CARRIER_PREVIEW_RUNNING",
        "policy": {
            "scientific_authority": False,
            "canonical_public_state_mutation_forbidden": True,
            "generator_call_forbidden": True,
            "reviewer_call_forbidden": True,
            "preview_cannot_authorize_live_transaction": True,
            "private_content_addressed_cache_may_update": True,
            "complete_retrieval_window_required_for_live_interpretation": True,
        },
        "canonical_before_sha256": before,
        "generator_called": False,
        "reviewer_called": False,
        "scientific_authority": False,
    }
    try:
        kwargs = dict(primary_kwargs or {})
        kwargs.update(
            {
                "storage": storage,
                "portable_generator_state_path": Path(generator_state_path),
                "portable_primary_state_path": Path(primary_state_path),
                "now": current,
            }
        )
        public, private_pool = build_primary_evidence_pool(**kwargs)
        summary = public.get("summary") or {}
        carrier = public.get("carrier_probe") or {}
        generator_state: dict[str, Any] = {}
        try:
            loaded = json.loads(Path(generator_state_path).read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                generator_state = loaded
        except (OSError, json.JSONDecodeError):
            generator_state = {}
        portfolio_mode = (generator_state.get("policy") or {}).get("search_portfolio_enabled") is True
        pool_sha = _pool_sha(private_pool)
        portable_receipts = [
            dict(row)
            for row in ((private_pool.get("source_coverage") or {}).get("portable_review_receipts") or [])
            if isinstance(row, dict)
        ]
        current_operator_receipt = None
        if summary.get("source_coverage_exhausted") is True:
            current_operator_receipt = _has_current_operator_receipt(
                storage,
                pool_sha,
                portable_receipts,
                portfolio=portfolio_mode,
            )
        preview_action = _preview_action(public, current_operator_receipt=current_operator_receipt)
        base.update(
            {
                "status": "PRIVATE_CARRIER_PREVIEW_COMPLETE",
                "preview_action": preview_action,
                "transaction_preview": {
                    "source_pool_sha256": pool_sha,
                    "current_operator_receipt_present": current_operator_receipt,
                    "portfolio_mode": portfolio_mode,
                    "zero_call_saturation_eligible": bool(
                        preview_action == "SOURCE_COVERAGE_SATURATED_ZERO_CALL"
                    ),
                    "scientific_authority": False,
                },
                "primary_schema_version": str(public.get("schema_version") or ""),
                "primary_status": str(public.get("status") or ""),
                "primary_summary": {
                    key: summary.get(key)
                    for key in (
                        "discovery_mode",
                        "augmentation_discovered",
                        "augmentation_added",
                        "verified",
                        "prior_reviewed_sources",
                        "eligible_lane_linked_sources",
                        "reviewed_lane_linked_sources",
                        "unreviewed_lane_linked_sources",
                        "unreviewed_no_lane_sources",
                        "source_retrieval_complete",
                        "source_coverage_exhausted",
                        "carrier_probe_required",
                        "carrier_probe_attempted",
                        "carrier_probe_reused",
                        "carrier_probe_rescued",
                        "carrier_probe_pending",
                        "carrier_probe_complete",
                        "selected_unreviewed",
                        "selected_lane_unreviewed",
                        "candidate_generation_ready",
                    )
                },
                "discovery_errors": [str(value)[:500] for value in public.get("discovery_errors") or []],
                "primary_errors": [dict(row) for row in public.get("errors") or [] if isinstance(row, dict)],
                "carrier_probe": {
                    "enabled": carrier.get("enabled"),
                    "required": carrier.get("required"),
                    "classifier_version": carrier.get("classifier_version"),
                    "probe_limit": carrier.get("probe_limit"),
                    "attempted": carrier.get("attempted"),
                    "reused": carrier.get("reused"),
                    "rescued": carrier.get("rescued"),
                    "pending": carrier.get("pending"),
                    "complete": carrier.get("complete"),
                    "portable_receipts": [
                        {
                            "ref": row.get("ref"),
                            "primary_sha256": row.get("primary_sha256"),
                            "fulltext_sha256": row.get("fulltext_sha256"),
                            "classifier_version": row.get("classifier_version"),
                            "matched_existing_object_lanes": row.get("matched_existing_object_lanes") or [],
                            "live_rescue_eligible_lanes": row.get("live_rescue_eligible_lanes") or [],
                            "scientific_authority": False,
                        }
                        for row in carrier.get("portable_receipts") or []
                        if isinstance(row, dict)
                    ],
                    "errors": [dict(row) for row in carrier.get("errors") or [] if isinstance(row, dict)],
                    "scientific_authority": False,
                },
                "selected_evidence": [
                    {
                        "ref": row.get("ref"),
                        "source_sha256": row.get("source_sha256"),
                        "fulltext_sha256": row.get("fulltext_sha256"),
                    }
                    for row in public.get("records") or []
                    if isinstance(row, dict)
                ],
            }
        )
    except Exception as error:
        base.update(
            {
                "status": "PRIVATE_CARRIER_PREVIEW_ERROR",
                "preview_action": "NO_AUTHORITY_ERROR",
                "error": f"{type(error).__name__}:{str(error)[:500]}",
            }
        )
    after = {key: _file_sha256(path) for key, path in canonical_paths.items()}
    base["canonical_after_sha256"] = after
    base["canonical_public_state_unchanged"] = before == after
    if before != after:
        base["status"] = "PRIVATE_CARRIER_PREVIEW_CANONICAL_MUTATION_ERROR"
        base["preview_action"] = "NO_AUTHORITY_ERROR"
    material = {
        "generated_at": base.get("generated_at"),
        "status": base.get("status"),
        "preview_action": base.get("preview_action"),
        "canonical_before_sha256": before,
        "canonical_after_sha256": after,
        "primary_summary": base.get("primary_summary") or {},
        "carrier_probe": base.get("carrier_probe") or {},
        "selected_evidence": base.get("selected_evidence") or [],
        "transaction_preview": base.get("transaction_preview") or {},
    }
    digest = hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    base["preview_digest"] = digest
    artifact = output_dir / f"carrier-preview-{current.strftime('%Y%m%dT%H%M%SZ')}-{digest[:12]}.json"
    artifact.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "status": base["status"],
        "preview_action": base.get("preview_action"),
        "preview_digest": digest,
        "artifact_path": str(artifact),
        "canonical_public_state_unchanged": base["canonical_public_state_unchanged"],
        "generator_called": False,
        "reviewer_called": False,
        "scientific_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_carrier_preview(), ensure_ascii=False, indent=2))
