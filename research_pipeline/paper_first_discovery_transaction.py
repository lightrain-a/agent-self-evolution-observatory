from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import (
    DEFAULT_JSON as PRIMARY_JSON,
    DEFAULT_JS as PRIMARY_JS,
    load_private_primary_pool,
    private_primary_pool_path,
    project_recompiled_primary_public_state,
    recompile_frozen_primary_typed_evidence,
    write_primary_evidence_pool,
)
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION
from .paper_first_problem_generator import (
    DEFAULT_JSON as GENERATOR_JSON,
    DEFAULT_JS as GENERATOR_JS,
    _completed_lane_search_receipt_from_state,
    _load_saturation_ledger,
    _normalize_last_completed_lane_search_receipt,
    _pool_sha,
    _saturation_ledger_path,
    write_problem_generator_state,
    write_replayed_problem_generator_state,
)
from .paper_first_problem_gate_queue import (
    DEFAULT_JSON as QUEUE_JSON,
    DEFAULT_JS as QUEUE_JS,
    default_auto_inbox_path,
    write_problem_gate_queue,
)


PUBLIC_TARGETS = (
    ("primary", PRIMARY_JSON, PRIMARY_JS, "PAPER_FIRST_PRIMARY_EVIDENCE"),
    ("generator", GENERATOR_JSON, GENERATOR_JS, "PAPER_FIRST_PROBLEM_GENERATOR"),
    ("queue", QUEUE_JSON, QUEUE_JS, "PAPER_FIRST_PROBLEM_GATE_QUEUE"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _generator_operator_version(generator: dict[str, Any]) -> str:
    return str((generator.get("policy") or {}).get("discovery_operator_version") or "").strip()


def _generator_receipt(generator: dict[str, Any]) -> dict[str, Any]:
    receipt = (generator.get("saturation_memory") or {}).get("current_review_receipt") or {}
    return dict(receipt) if isinstance(receipt, dict) else {}


def _receipt_material(receipt: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, dict) or not receipt:
        return {}
    return {
        "run_id": str(receipt.get("run_id") or ""),
        "pool_sha256": str(receipt.get("pool_sha256") or ""),
        "negative_space_sha256": str(receipt.get("negative_space_sha256") or ""),
        "discovery_operator_version": str(receipt.get("discovery_operator_version") or ""),
        "source_refs": sorted(str(ref) for ref in receipt.get("source_refs") or [] if str(ref)),
        "status": str(receipt.get("status") or ""),
        "requested_model": str(receipt.get("requested_model") or ""),
        "resolved_model": str(receipt.get("resolved_model") or ""),
        "raw_sha256": str(receipt.get("raw_sha256") or ""),
        "scientific_authority": receipt.get("scientific_authority"),
    }


def _receipt_sha256(receipt: dict[str, Any]) -> str:
    material = _receipt_material(receipt)
    if not material:
        return ""
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _provider_call_accounting(generator_internal: dict[str, Any] | None) -> tuple[int, int]:
    artifacts = (generator_internal or {}).get("raw_artifacts") or {}
    raw = artifacts.get("generator") or {}
    generator_calls = int(raw.get("provider_calls_executed") or 0) if isinstance(raw, dict) else 0
    if not generator_calls and isinstance(raw, dict):
        generator_calls = len(raw.get("transport_attempts") or [])
        if not generator_calls and raw.get("sha256") and raw.get("raw_replayed_without_provider") is not True:
            generator_calls = 1
    semantic = artifacts.get("semantic_reviewer") or {}
    semantic_calls = int(semantic.get("provider_calls_executed") or semantic.get("calls") or 0) if isinstance(semantic, dict) else 0
    if not semantic_calls and isinstance(semantic, dict) and semantic.get("sha256") and semantic.get("raw_replayed_without_provider") is not True:
        semantic_calls = 1
    return generator_calls, semantic_calls


def _repair_close_envelope_generator_provenance(generator: dict[str, Any]) -> dict[str, Any]:
    """Rebuild a missing portable lane receipt from one frozen completed Generator state.

    Historical standalone Generator runs may predate the writer-side projection that
    copied a completed lane audit into ``last_completed_lane_search``. Closing such a
    run must not call a provider or reinterpret it under the runtime operator. The
    reconstruction is allowed only when the Generator's own current review receipt
    binds the same run, status, and declared operator and the completed lane audit can
    be normalized deterministically from the frozen state itself.
    """
    repaired = json.loads(json.dumps(generator, ensure_ascii=False))
    if str(repaired.get("schema_version") or "0") < "2.5":
        return repaired
    status = str(repaired.get("status") or "")
    if status not in {"GENERATED_ZERO_CANDIDATES", "GENERATED_AWAIT_PROBLEM_GATE"}:
        return repaired
    diagnostics = repaired.get("search_diagnostics") or {}
    if diagnostics.get("last_completed_lane_search"):
        return repaired
    if diagnostics.get("lane_search_complete") is not True:
        return repaired
    operator = _generator_operator_version(repaired)
    receipt = _receipt_material(_generator_receipt(repaired))
    if (
        not operator
        or receipt.get("scientific_authority") is not False
        or receipt.get("run_id") != str(repaired.get("run_id") or "")
        or receipt.get("status") != status
        or receipt.get("discovery_operator_version") != operator
    ):
        return repaired
    projected = _completed_lane_search_receipt_from_state(repaired)
    if (
        not projected
        or str(projected.get("run_id") or "") != str(repaired.get("run_id") or "")
        or str(projected.get("discovery_operator_version") or "") != operator
        or projected.get("lane_search") != diagnostics.get("lane_search")
        or projected.get("scientific_authority") is not False
    ):
        return repaired
    diagnostics["last_completed_lane_search"] = projected
    diagnostics["scientific_authority"] = False
    repaired["search_diagnostics"] = diagnostics
    repaired["provenance_replay"] = {
        "mode": "completed-lane-search-receipt-from-frozen-generator-state",
        "source_generator_run_id": str(repaired.get("run_id") or ""),
        "discovery_operator_version": operator,
        "runtime_discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
        "provider_calls_executed": 0,
        "source_scheduler_runs_executed": 0,
        "scientific_authority": False,
    }
    return repaired


def _transaction_lock_path(storage: StorageSettings) -> Path:
    """Return one host-wide lock shared by all checkouts/worktrees of this research system."""
    override = str(os.getenv("PAPER_FIRST_DISCOVERY_TRANSACTION_LOCK") or "").strip()
    if override:
        return Path(override).expanduser()
    # storage.lock_dir is checkout-relative in isolated worktrees, so it cannot prevent two
    # agents on the same host from entering Generator/Reviewer concurrently. Namespace by uid
    # to avoid cross-user interference while keeping every checkout for this project single-flight.
    return Path(tempfile.gettempdir()) / f".agent-self-evolution-observatory-paper-first-discovery-{os.getuid()}.lock"


@contextmanager
def _transaction_lock(storage: StorageSettings) -> Iterator[None]:
    path = _transaction_lock_path(storage)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            handle.seek(0);owner=handle.read(800).strip()
            raise RuntimeError(f"Another paper-first discovery transaction is active on this host: {path}; owner={owner or 'unknown'}") from error
        handle.seek(0); handle.truncate(); handle.write(json.dumps({"pid": os.getpid(), "started_at": _now(), "cwd": str(Path.cwd())})); handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _transaction_material(primary: dict[str, Any], generator: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    primary_records = [
        {
            "ref": row.get("ref"),
            "source_sha256": row.get("source_sha256"),
            "fulltext_sha256": row.get("fulltext_sha256"),
        }
        for row in primary.get("records") or []
        if isinstance(row, dict)
    ]
    carrier_receipts = sorted([
        {
            "ref": row.get("ref"),
            "primary_sha256": row.get("primary_sha256"),
            "fulltext_sha256": row.get("fulltext_sha256"),
            "classifier_version": row.get("classifier_version"),
            "live_rescue_eligible_lanes": sorted(str(value) for value in row.get("live_rescue_eligible_lanes") or []),
        }
        for row in (primary.get("carrier_probe") or {}).get("portable_receipts") or []
        if isinstance(row, dict)
    ], key=lambda row: str(row.get("ref") or ""))
    generator_raw = generator.get("raw_artifacts") or {}
    audited = [
        {
            "candidate_id": row.get("candidate_id"),
            "source_inbox": row.get("source_inbox"),
            "status": (row.get("audit") or {}).get("status"),
            "blockers": (row.get("audit") or {}).get("blockers") or [],
        }
        for row in queue.get("audited") or []
        if isinstance(row, dict)
    ]
    return {
        "primary_records": primary_records,
        "primary_typed_evidence_extraction_version": str((primary.get("policy") or {}).get("typed_evidence_extraction_version") or ""),
        "primary_typed_evidence_counts": dict((primary.get("summary") or {}).get("typed_evidence_candidates") or {}),
        "carrier_probe_receipts": carrier_receipts,
        "carrier_probe_pending": int(((primary.get("carrier_probe") or {}).get("pending") or 0)),
        "generator_run_id": generator.get("run_id"),
        "generator_status": generator.get("status"),
        "generator_discovery_operator_version": _generator_operator_version(generator),
        "generator_review_receipt": _receipt_material(_generator_receipt(generator)),
        "generator_last_completed_lane_search": (generator.get("search_diagnostics") or {}).get("last_completed_lane_search") or {},
        "generator_provenance_replay": generator.get("provenance_replay") or {},
        "generator_raw_sha256": (generator_raw.get("generator") or {}).get("sha256"),
        "semantic_review_raw_sha256": (generator_raw.get("semantic_reviewer") or {}).get("sha256"),
        "queue_audited": audited,
    }


def _transaction_id(primary: dict[str, Any], generator: dict[str, Any], queue: dict[str, Any]) -> str:
    material = _transaction_material(primary, generator, queue)
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate(primary: dict[str, Any], generator: dict[str, Any], queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ps = primary.get("summary") or {}; gs = generator.get("summary") or {}; qs = queue.get("summary") or {}
    verified = int(ps.get("verified") or 0)
    if primary.get("status") != "READY" or verified < 4:
        errors.append("primary-evidence-not-ready")
    carrier_probe=primary.get("carrier_probe") or {}
    if carrier_probe:
        carrier_pending=int(carrier_probe.get("pending") or 0)
        carrier_complete=carrier_probe.get("complete") is True
        if carrier_probe.get("scientific_authority") is not False or int(ps.get("carrier_probe_pending") or 0)!=carrier_pending or bool(ps.get("carrier_probe_complete"))!=carrier_complete:
            errors.append("primary-carrier-probe-accounting-invalid")
        allowed_objects=set(str(value) for value in ((primary.get("policy") or {}).get("scientific_object_lanes") or []))
        for row in carrier_probe.get("portable_receipts") or []:
            if not isinstance(row,dict):
                errors.append("primary-carrier-probe-receipt-invalid"); break
            scope_excluded=str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY"
            fulltext_ok=(scope_excluded and not str(row.get("fulltext_sha256") or "")) or len(str(row.get("fulltext_sha256") or ""))==64
            if row.get("scientific_authority") is not False or len(str(row.get("primary_sha256") or ""))!=64 or not fulltext_ok or not str(row.get("classifier_version") or ""):
                errors.append("primary-carrier-probe-receipt-invalid"); break
            if scope_excluded and (row.get("live_rescue_eligible_lanes") or []):
                errors.append("primary-carrier-scope-exclusion-cannot-rescue"); break
            if any(str(value) not in allowed_objects for value in row.get("live_rescue_eligible_lanes") or []):
                errors.append("primary-carrier-probe-created-unknown-object"); break
    generator_status = str(generator.get("status") or "")
    generator_policy = generator.get("policy") or {}
    if generator_policy.get("search_portfolio_enabled") is True:
        errors.append("canonical-transaction-forbids-search-portfolio")
    if generator_policy.get("one_generator_call_max") is not True or generator_policy.get("one_semantic_reviewer_call_max") is not True:
        errors.append("canonical-transaction-requires-single-call-budget")
    allowed_generator_statuses = {"GENERATED_ZERO_CANDIDATES", "GENERATED_AWAIT_PROBLEM_GATE", "SKIPPED_SOURCE_COVERAGE_SATURATED", "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE", "SKIPPED_SOURCE_CARRIER_PROBE_PENDING"}
    if generator_status not in allowed_generator_statuses:
        errors.append("generator-did-not-complete-discovery-transaction")
    generator_schema=str(generator.get("schema_version") or "0")
    generated = int(gs.get("generated") or 0)
    if int(gs.get("primary_evidence_records") or 0) != verified:
        errors.append("generator-primary-count-mismatch")
    if int(qs.get("primary_evidence_records") or 0) != verified:
        errors.append("queue-primary-count-mismatch")
    if int(gs.get("written_to_auto_inbox") or 0) != generated:
        errors.append("generator-auto-inbox-count-mismatch")
    if int(gs.get("semantic_clear") or 0) + int(gs.get("semantic_blocked") or 0) != generated:
        errors.append("generator-semantic-accounting-mismatch")
    if generator_schema >= "2.4" and generator_status in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}:
        diagnostics=generator.get("search_diagnostics") or {}; gp=generator.get("policy") or {}
        lane_rows=[row for row in diagnostics.get("lane_search") or [] if isinstance(row,dict)];lane_names={str(row.get("lane") or "") for row in lane_rows};lane_statuses={str(row.get("status") or "") for row in lane_rows}
        allowed_statuses={"EXPANDED","EMPTY"} if gp.get("search_portfolio_enabled") is True else {"NO_PAIR","REDUCIBLE","CANDIDATE"}
        if diagnostics.get("scientific_authority") is not False or diagnostics.get("lane_search_complete") is not True or len(lane_rows)!=len(DISCOVERY_LANES) or lane_names!=set(DISCOVERY_LANES) or not lane_statuses.issubset(allowed_statuses):
            errors.append("generator-lane-search-audit-incomplete")
    if generator_schema >= "2.5":
        gp=generator.get("policy") or {}; diagnostics=generator.get("search_diagnostics") or {}; last=diagnostics.get("last_completed_lane_search") or {}
        normalized_last=_normalize_last_completed_lane_search_receipt(last) if last else {}
        if gp.get("last_completed_lane_search_is_portable_zero_authority_receipt") is not True or gp.get("terminal_zero_call_skip_preserves_last_completed_lane_search") is not True: errors.append("generator-last-lane-search-receipt-policy-missing")
        if last and not normalized_last: errors.append("generator-last-lane-search-receipt-invalid")
        if generator_status in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}:
            current_rows=[row for row in diagnostics.get("lane_search") or [] if isinstance(row,dict)]
            if not normalized_last or str(normalized_last.get("run_id") or "")!=str(generator.get("run_id") or "") or normalized_last.get("lane_search")!=current_rows: errors.append("generator-last-lane-search-receipt-not-current")
    if generator_status == "GENERATED_ZERO_CANDIDATES" and generated != 0:
        errors.append("zero-status-with-nonzero-candidates")
    if generator_status == "GENERATED_AWAIT_PROBLEM_GATE" and generated <= 0:
        errors.append("await-gate-status-with-zero-candidates")
    if generator_status == "SKIPPED_SOURCE_COVERAGE_SATURATED":
        coverage = generator.get("source_coverage") or {}
        gp = generator.get("policy") or {}
        if generated != 0 or int(gs.get("written_to_auto_inbox") or 0) != 0 or int(gs.get("semantic_clear") or 0) != 0 or int(gs.get("semantic_blocked") or 0) != 0:
            errors.append("coverage-skip-generator-accounting-nonzero")
        if coverage.get("coverage_exhausted") is not True or coverage.get("unreviewed_lane_linked_sources") is None or int(coverage.get("unreviewed_lane_linked_sources")) != 0:
            errors.append("coverage-skip-not-exhausted")
        if coverage.get("carrier_probe_required") is True and (int(coverage.get("carrier_probe_pending") or 0)>0 or coverage.get("carrier_probe_complete") is not True):
            errors.append("coverage-skip-carrier-probe-incomplete")
        if ps.get("source_retrieval_complete") is False:
            errors.append("coverage-skip-retrieval-window-incomplete")
        if gp.get("source_coverage_saturation_skips_model_call") is not True or gp.get("source_coverage_saturation_is_compute_control_not_scientific_negative") is not True or gp.get("new_lane_grounded_primary_source_reopens_generation") is not True or gp.get("primary_source_coverage_receipts_are_inherited_transactionally") is not True:
            errors.append("coverage-skip-policy-missing")
        receipts=[row for row in ((generator.get("saturation_memory") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
        portable_refs={str(ref) for row in receipts if row.get("scientific_authority") is False for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
        prior_reviewed=int(ps.get("prior_reviewed_sources") or 0)
        if any(row.get("scientific_authority") is not False for row in receipts) or len(portable_refs) < prior_reviewed:
            errors.append("coverage-skip-portable-receipts-incomplete")
    if generator_status == "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE":
        coverage=generator.get("source_coverage") or {};gp=generator.get("policy") or {}
        if generated != 0 or int(gs.get("written_to_auto_inbox") or 0) != 0 or int(gs.get("semantic_clear") or 0) != 0 or int(gs.get("semantic_blocked") or 0) != 0:
            errors.append("retrieval-incomplete-skip-generator-accounting-nonzero")
        if coverage.get("source_retrieval_complete") is not False or coverage.get("coverage_exhausted") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0)!=0:
            errors.append("retrieval-incomplete-skip-state-invalid")
        if ps.get("source_retrieval_complete") is not False or int(ps.get("unreviewed_lane_linked_sources") or 0)!=0:
            errors.append("retrieval-incomplete-skip-primary-state-invalid")
        if gp.get("incomplete_retrieval_without_new_lane_source_skips_model_call") is not True or gp.get("retrieval_incomplete_is_compute_control_not_scientific_negative") is not True or gp.get("one_content_addressed_pool_allows_at_most_one_live_generator_call") is not True:
            errors.append("retrieval-incomplete-skip-policy-missing")
        receipts=[row for row in ((generator.get("saturation_memory") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
        portable_refs={str(ref) for row in receipts if row.get("scientific_authority") is False for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
        if any(row.get("scientific_authority") is not False for row in receipts) or len(portable_refs)<int(ps.get("prior_reviewed_sources") or 0):
            errors.append("retrieval-incomplete-skip-portable-review-receipts-incomplete")
    if generator_status == "SKIPPED_SOURCE_CARRIER_PROBE_PENDING":
        coverage=generator.get("source_coverage") or {};gp=generator.get("policy") or {}
        if generated != 0 or int(gs.get("written_to_auto_inbox") or 0) != 0 or int(gs.get("semantic_clear") or 0) != 0 or int(gs.get("semantic_blocked") or 0) != 0:
            errors.append("carrier-probe-skip-generator-accounting-nonzero")
        if coverage.get("coverage_exhausted") is True or coverage.get("carrier_probe_required") is not True or int(coverage.get("carrier_probe_pending") or 0)<=0 or coverage.get("carrier_probe_complete") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0)!=0:
            errors.append("carrier-probe-skip-state-invalid")
        if ps.get("source_retrieval_complete") is False or int(ps.get("carrier_probe_pending") or 0)<=0 or ps.get("carrier_probe_complete") is True:
            errors.append("carrier-probe-skip-primary-state-invalid")
        if gp.get("carrier_probe_pending_skips_model_call") is not True or gp.get("carrier_probe_pending_is_compute_control_not_scientific_negative") is not True or gp.get("one_content_addressed_pool_allows_at_most_one_live_generator_call") is not True:
            errors.append("carrier-probe-skip-policy-missing")
        receipts=[row for row in ((generator.get("saturation_memory") or {}).get("portable_review_receipts") or []) if isinstance(row,dict)]
        portable_refs={str(ref) for row in receipts if row.get("scientific_authority") is False for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
        if any(row.get("scientific_authority") is not False for row in receipts) or len(portable_refs)<int(ps.get("prior_reviewed_sources") or 0):
            errors.append("carrier-probe-skip-portable-review-receipts-incomplete")
    submitted = int(qs.get("submitted") or 0); audited_count = int(qs.get("audited") or 0)
    passed = int(qs.get("passed_problem_gate") or 0); blocked = int(qs.get("blocked_problem_gate") or 0)
    if int(qs.get("inbox_errors") or 0) != 0:
        errors.append("queue-inbox-errors")
    if submitted != audited_count or passed + blocked != audited_count:
        errors.append("queue-accounting-mismatch")
    if generator_status in {"SKIPPED_SOURCE_COVERAGE_SATURATED","SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE","SKIPPED_SOURCE_CARRIER_PROBE_PENDING"} and any(value != 0 for value in (submitted, audited_count, passed, blocked)):
        errors.append("coverage-skip-queue-must-be-empty")
    if any(int(qs.get(key) or 0) != 0 for key in ("method_authorized", "experiment_authorized", "p0_authorized")):
        errors.append("queue-illegal-downstream-authority")
    gp = generator.get("policy") or {}
    if any(gp.get(key) is not False for key in ("automatic_method_authority", "automatic_experiment_authority", "automatic_p0_authority")):
        errors.append("generator-illegal-downstream-authority")
    generator_ids = {str(row.get("candidate_id") or "") for row in generator.get("candidates") or [] if isinstance(row, dict) and row.get("candidate_id")}
    auto_audited = {
        str(row.get("candidate_id") or "")
        for row in queue.get("audited") or []
        if isinstance(row, dict) and "auto-candidate-inbox.json" in str(row.get("source_inbox") or "") and row.get("candidate_id")
    }
    if generator_ids != auto_audited:
        errors.append("generator-queue-auto-candidate-set-mismatch")
    return sorted(set(errors))


def _stamp(path: Path, js_path: Path, global_name: str, transaction_id: str, role: str) -> dict[str, Any]:
    payload = _load(path)
    if not payload:
        raise RuntimeError(f"transaction output unreadable: {path}")
    payload["discovery_transaction_id"] = transaction_id
    payload["discovery_transaction_role"] = role
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(f"window.{global_name} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


def _commit_files(temp_targets: list[tuple[Path, Path]]) -> None:
    backups: dict[Path, bytes | None] = {target: (target.read_bytes() if target.exists() else None) for _, target in temp_targets}
    replaced: list[Path] = []
    try:
        for source, target in temp_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)
            replaced.append(target)
    except Exception:
        for target in replaced:
            previous = backups[target]
            if previous is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(previous)
        raise


def close_existing_problem_discovery_transaction(
    *,
    storage: StorageSettings | None = None,
    primary_json: Path = PRIMARY_JSON,
    primary_js: Path = PRIMARY_JS,
    generator_json: Path = GENERATOR_JSON,
    generator_js: Path = GENERATOR_JS,
    queue_json: Path = QUEUE_JSON,
    queue_js: Path = QUEUE_JS,
    private_pool_source: Path | None = None,
) -> dict[str, Any]:
    """Atomically envelope an already-completed Primary -> Generator -> Queue state.

    This path is intentionally zero-provider and zero-retrieval. It exists for the
    case where the three canonical stages have already completed against one
    content-addressed Primary pool but were written by standalone stage writers.
    Re-running Primary merely to add a transaction id is unsafe once the source
    coverage scheduler has advanced, because that replay can silently select a
    different exploration tranche. Therefore this function requires an exact
    generator saturation receipt and an exact private-pool record match before it
    may stamp the existing closed state.
    """
    storage = storage or StorageSettings.from_env(); storage.ensure()
    primary = _load(primary_json); generator = _repair_close_envelope_generator_provenance(_load(generator_json)); queue = _load(queue_json)
    errors = _validate(primary, generator, queue)
    if errors:
        raise RuntimeError("existing paper-first discovery state invalid: " + ",".join(errors))
    public_records = [row for row in primary.get("records") or [] if isinstance(row, dict)]
    public_manifest = [
        (str(row.get("ref") or ""), str(row.get("source_sha256") or ""), str(row.get("fulltext_sha256") or ""))
        for row in public_records
    ]
    if not public_manifest or any(not ref or len(source_sha) != 64 for ref, source_sha, _ in public_manifest):
        raise RuntimeError("existing Primary manifest is incomplete")

    source_path = Path(private_pool_source) if private_pool_source is not None else private_primary_pool_path(storage)
    source_pool = load_private_primary_pool(source_path) or {}
    source_records = [row for row in source_pool.get("records") or [] if isinstance(row, dict)]
    source_manifest = [
        (str(row.get("ref") or ""), str(row.get("source_sha256") or ""), str(row.get("fulltext_sha256") or ""))
        for row in source_records
    ]
    if source_manifest != public_manifest:
        raise RuntimeError("private Primary replay source does not exactly match current public Primary records")
    source_pool_sha = _pool_sha(source_pool)

    generator_raw = ((generator.get("raw_artifacts") or {}).get("generator") or {})
    generator_raw_sha = str(generator_raw.get("sha256") or "")
    generator_run_id = str(generator.get("run_id") or "")
    generator_status = str(generator.get("status") or "")
    generator_operator = _generator_operator_version(generator)
    generator_receipt = _generator_receipt(generator)
    generator_receipt_material = _receipt_material(generator_receipt)
    if not generator_operator:
        raise RuntimeError("existing Generator does not declare its discovery operator")
    expected_receipt = {
        "run_id": generator_run_id,
        "pool_sha256": source_pool_sha,
        "discovery_operator_version": generator_operator,
        "status": generator_status,
        "raw_sha256": generator_raw_sha,
        "scientific_authority": False,
    }
    if any(generator_receipt_material.get(key) != value for key, value in expected_receipt.items()):
        raise RuntimeError("existing Generator current review receipt does not bind its exact frozen Primary, raw output, status, and operator")
    if generator_receipt_material.get("source_refs") != sorted(ref for ref, _, _ in public_manifest):
        raise RuntimeError("existing Generator current review receipt does not bind the exact public Primary refs")
    receipts = [row for row in _load_saturation_ledger(storage) if isinstance(row, dict)]
    receipt = next((
        row for row in reversed(receipts)
        if all(_receipt_material(row).get(key) == value for key, value in generator_receipt_material.items())
    ), None)
    if receipt is None:
        raise RuntimeError("no exact generator receipt binds the existing Primary and Generator state")

    txn_id = _transaction_id(primary, generator, queue)
    target_private = private_primary_pool_path(storage)
    replay_pool = json.loads(json.dumps(source_pool, ensure_ascii=False))
    replay_pool["generated_at"] = str(primary.get("generated_at") or "")
    replay_pool["transaction_replay"] = {
        "mode": "existing-closed-state-envelope",
        "source_generated_at": str(source_pool.get("generated_at") or ""),
        "source_pool_sha256": source_pool_sha,
        "generator_receipt_run_id": generator_run_id,
        "generator_receipt_sha256": _receipt_sha256(generator_receipt),
        "discovery_operator_version": generator_operator,
        "runtime_discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
        "operator_version_replayed_without_provider": generator_operator != DISCOVERY_OPERATOR_VERSION,
        "scientific_authority": False,
    }
    coverage = replay_pool.setdefault("source_coverage", {})
    portable = [dict(row) for row in coverage.get("portable_review_receipts") or [] if isinstance(row, dict)]
    key = (generator_run_id, source_pool_sha, generator_operator)
    by_key = {
        (str(row.get("run_id") or ""), str(row.get("pool_sha256") or ""), str(row.get("discovery_operator_version") or "")): row
        for row in portable
    }
    by_key[key] = {
        "run_id": generator_run_id,
        "pool_sha256": source_pool_sha,
        "negative_space_sha256": receipt.get("negative_space_sha256"),
        "discovery_operator_version": generator_operator,
        "source_refs": [ref for ref, _, _ in public_manifest],
        "status": generator_status,
        "requested_model": receipt.get("requested_model"),
        "resolved_model": receipt.get("resolved_model"),
        "raw_sha256": generator_raw_sha,
        "scientific_authority": False,
    }
    coverage["portable_review_receipts"] = list(by_key.values())
    coverage["portable_review_receipts_merged"] = len(coverage["portable_review_receipts"])
    coverage["saturation_ledger_runs"] = max(int(coverage.get("saturation_ledger_runs") or 0), len(receipts))
    if _pool_sha(replay_pool) != source_pool_sha:
        raise RuntimeError("private Primary replay changed the content-addressed pool")

    run_root = storage.run_dir / "paper-first-discovery-transactions"; run_root.mkdir(parents=True, exist_ok=True)
    started = _now()
    with _transaction_lock(storage):
        temp_root = Path(tempfile.mkdtemp(prefix=".paper-first-close-", dir=str(primary_json.parent)))
        try:
            targets: list[tuple[Path, Path]] = []
            for role, payload, out_json, out_js, global_name in (
                ("primary", primary, primary_json, primary_js, "PAPER_FIRST_PRIMARY_EVIDENCE"),
                ("generator", generator, generator_json, generator_js, "PAPER_FIRST_PROBLEM_GENERATOR"),
                ("queue", queue, queue_json, queue_js, "PAPER_FIRST_PROBLEM_GATE_QUEUE"),
            ):
                temp_json = temp_root / f"{role}.json"; temp_js = temp_root / f"{role}.js"
                clean = dict(payload); clean.pop("discovery_transaction_id", None); clean.pop("discovery_transaction_role", None)
                temp_json.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                _stamp(temp_json, temp_js, global_name, txn_id, role)
                targets.extend([(temp_json, out_json), (temp_js, out_js)])
            temp_private = temp_root / "primary-private.json"
            temp_private.write_text(json.dumps(replay_pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            targets.append((temp_private, target_private))
            _commit_files(targets)
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    record = {
        "schema_version": "1.0",
        "started_at": started,
        "completed_at": _now(),
        "status": "COMMITTED_EXISTING_CLOSED_STATE",
        "transaction_id": txn_id,
        "source_pool_sha256": source_pool_sha,
        "generator_receipt_run_id": generator_run_id,
        "generator_receipt_sha256": _receipt_sha256(generator_receipt),
        "generator_receipt_raw_sha256": generator_raw_sha,
        "discovery_operator_version": generator_operator,
        "runtime_discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
        "operator_version_replayed_without_provider": generator_operator != DISCOVERY_OPERATOR_VERSION,
        "provider_calls_executed": 0,
        "source_scheduler_runs_executed": 0,
        "scientific_authority": False,
        "authority": {"paper": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }
    (run_root / f"{txn_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def recompile_existing_problem_discovery_transaction(
    *,
    storage: StorageSettings | None = None,
    primary_json: Path = PRIMARY_JSON,
    primary_js: Path = PRIMARY_JS,
    generator_json: Path = GENERATOR_JSON,
    generator_js: Path = GENERATOR_JS,
    queue_json: Path = QUEUE_JSON,
    queue_js: Path = QUEUE_JS,
    private_pool_source: Path | None = None,
    generator_kwargs: dict[str, Any] | None = None,
    queue_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Recompile Generator -> Queue on one already-certified Primary transaction.

    This is the only live operator-upgrade path that is allowed to reuse an unchanged
    Primary without rerunning retrieval, the source-coverage scheduler, or carrier
    probing. The prior public Primary/Generator/Queue must be one closed zero-survivor
    transaction, the prior Generator must have been produced by an older discovery
    operator, and the supplied private Primary must match the public Primary manifest
    exactly. All outputs are staged under the host-wide transaction lock and committed
    atomically; any provider/reviewer/queue failure preserves every prior public/private
    control file.
    """
    storage = storage or StorageSettings.from_env(); storage.ensure()
    primary = _load(primary_json); previous_generator = _load(generator_json); previous_queue = _load(queue_json)
    errors = _validate(primary, previous_generator, previous_queue)
    if errors:
        raise RuntimeError("existing paper-first discovery state invalid: " + ",".join(errors))
    primary_tx=str(primary.get("discovery_transaction_id") or "").strip()
    generator_tx=str(previous_generator.get("discovery_transaction_id") or "").strip()
    queue_tx=str(previous_queue.get("discovery_transaction_id") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}",primary_tx) or primary_tx!=generator_tx or primary_tx!=queue_tx:
        raise RuntimeError("existing paper-first discovery transaction identity mismatch")
    previous_operator=str((previous_generator.get("policy") or {}).get("discovery_operator_version") or "")
    if not previous_operator or previous_operator==DISCOVERY_OPERATOR_VERSION:
        raise RuntimeError("operator recompile requires a closed transaction from an older discovery operator")
    previous_qs=previous_queue.get("summary") or {}
    if int(previous_qs.get("passed_problem_gate") or 0)!=0 or int(previous_qs.get("paper_design_eligible") or 0)!=0:
        raise RuntimeError("operator recompile cannot supersede a transaction with a Problem-Gate survivor")

    public_records=[row for row in primary.get("records") or [] if isinstance(row,dict)]
    public_manifest=[
        (str(row.get("ref") or ""),str(row.get("source_sha256") or ""),str(row.get("fulltext_sha256") or ""))
        for row in public_records
    ]
    if not public_manifest or any(not ref or len(source_sha)!=64 for ref,source_sha,_ in public_manifest):
        raise RuntimeError("existing Primary manifest is incomplete")
    source_path=Path(private_pool_source) if private_pool_source is not None else private_primary_pool_path(storage)
    source_pool=load_private_primary_pool(source_path) or {}
    source_records=[row for row in source_pool.get("records") or [] if isinstance(row,dict)]
    source_manifest=[
        (str(row.get("ref") or ""),str(row.get("source_sha256") or ""),str(row.get("fulltext_sha256") or ""))
        for row in source_records
    ]
    if source_pool.get("status")!="READY" or source_manifest!=public_manifest:
        raise RuntimeError("private Primary recompile source does not exactly match current public Primary records")
    source_pool_sha=_pool_sha(source_pool)
    prior_receipt=(previous_generator.get("saturation_memory") or {}).get("current_review_receipt") or {}
    if (
        str(prior_receipt.get("pool_sha256") or "")!=source_pool_sha
        or str(prior_receipt.get("discovery_operator_version") or "")!=previous_operator
        or prior_receipt.get("scientific_authority") is not False
    ):
        raise RuntimeError("prior Generator receipt does not bind the exact frozen Primary and prior operator")

    run_root=storage.run_dir/"paper-first-discovery-transactions";run_root.mkdir(parents=True,exist_ok=True)
    started=_now()
    with _transaction_lock(storage):
        temp_root=Path(tempfile.mkdtemp(prefix=".paper-first-recompile-",dir=str(primary_json.parent)))
        p_json=temp_root/"primary.json";p_js=temp_root/"primary.js";g_json=temp_root/"generator.json";g_js=temp_root/"generator.js";q_json=temp_root/"queue.json";q_js=temp_root/"queue.js"
        staged_private=temp_root/"primary-private.json";staged_auto=temp_root/"auto-candidate-inbox.json";staged_ledger=temp_root/"discovery-saturation-ledger.json"
        target_private=private_primary_pool_path(storage);target_auto=default_auto_inbox_path(storage);target_ledger=_saturation_ledger_path(storage)
        if target_auto.exists():shutil.copyfile(target_auto,staged_auto)
        if target_ledger.exists():shutil.copyfile(target_ledger,staged_ledger)
        staged_pool=json.loads(json.dumps(source_pool,ensure_ascii=False));staged_pool["generated_at"]=str(primary.get("generated_at") or staged_pool.get("generated_at") or "")
        staged_pool["operator_recompile"]={"prior_transaction_id":primary_tx,"prior_discovery_operator_version":previous_operator,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"source_scheduler_runs_executed":0,"scientific_authority":False}
        if _pool_sha(staged_pool)!=source_pool_sha:raise RuntimeError("operator recompile changed the content-addressed Primary pool")
        staged_private.write_text(json.dumps(staged_pool,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        clean_primary=dict(primary);clean_primary.pop("discovery_transaction_id",None);clean_primary.pop("discovery_transaction_role",None)
        p_json.write_text(json.dumps(clean_primary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        p_js.write_text("window.PAPER_FIRST_PRIMARY_EVIDENCE = "+json.dumps(clean_primary,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
        generator_internal:dict[str,Any]|None=None;queue_internal:dict[str,Any]|None=None
        record={"schema_version":"1.0","started_at":started,"status":"running","prior_transaction_id":primary_tx,"prior_discovery_operator_version":previous_operator,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"source_scheduler_runs_executed":0,"scientific_authority":False}
        try:
            gkw=dict(generator_kwargs or {});gkw.update({"storage":storage,"json_path":g_json,"js_path":g_js,"previous_public_state_path":generator_json,"primary_pool_path":staged_private,"auto_inbox_path":staged_auto,"saturation_ledger_path":staged_ledger})
            generator_internal=write_problem_generator_state(**gkw)
            qkw=dict(queue_kwargs or {});qkw.update({"storage":storage,"json_path":q_json,"js_path":q_js,"primary_pool_path":staged_private,"auto_inbox_path":staged_auto})
            queue_internal=write_problem_gate_queue(**qkw)
            primary_public=_load(p_json);generator_public=_load(g_json);queue_public=_load(q_json)
            validation=_validate(primary_public,generator_public,queue_public)
            if validation:raise RuntimeError("paper-first operator recompile transaction invalid: "+",".join(validation))
            transaction_operator=_generator_operator_version(generator_public)
            if transaction_operator!=DISCOVERY_OPERATOR_VERSION:
                raise RuntimeError("operator recompile Generator did not bind the current discovery operator")
            transaction_receipt=_generator_receipt(generator_public)
            transaction_receipt_material=_receipt_material(transaction_receipt)
            if transaction_receipt_material and (
                transaction_receipt_material.get("pool_sha256")!=source_pool_sha
                or transaction_receipt_material.get("discovery_operator_version")!=transaction_operator
                or transaction_receipt_material.get("run_id")!=str(generator_public.get("run_id") or "")
                or transaction_receipt_material.get("status")!=str(generator_public.get("status") or "")
                or transaction_receipt_material.get("scientific_authority") is not False
            ):
                raise RuntimeError("operator recompile Generator receipt does not bind the committed operator transaction")
            txn_id=_transaction_id(primary_public,generator_public,queue_public)
            primary_public=_stamp(p_json,p_js,"PAPER_FIRST_PRIMARY_EVIDENCE",txn_id,"primary")
            generator_public=_stamp(g_json,g_js,"PAPER_FIRST_PROBLEM_GENERATOR",txn_id,"generator")
            queue_public=_stamp(q_json,q_js,"PAPER_FIRST_PROBLEM_GATE_QUEUE",txn_id,"queue")
            private_targets=[(staged_private,target_private),(staged_auto,target_auto)]
            if staged_ledger.exists():private_targets.append((staged_ledger,target_ledger))
            _commit_files([(p_json,primary_json),(p_js,primary_js),(g_json,generator_json),(g_js,generator_js),(q_json,queue_json),(q_js,queue_js),*private_targets])
            generator_calls,semantic_calls=_provider_call_accounting(generator_internal)
            record.update({
                "status":"COMMITTED_OPERATOR_RECOMPILE","completed_at":_now(),"transaction_id":txn_id,"source_pool_sha256":source_pool_sha,
                "discovery_operator_version":transaction_operator,
                "generator_receipt_run_id":str(transaction_receipt_material.get("run_id") or ""),
                "generator_receipt_sha256":_receipt_sha256(transaction_receipt),
                "generator_receipt_raw_sha256":str(transaction_receipt_material.get("raw_sha256") or ""),
                "provider_calls_executed":generator_calls+semantic_calls,"generator_provider_calls_executed":generator_calls,"semantic_reviewer_calls_executed":semantic_calls,
                "summary":{"primary_status":primary_public.get("status"),"verified":(primary_public.get("summary") or {}).get("verified",0),"generator_status":generator_public.get("status"),"generated":(generator_public.get("summary") or {}).get("generated",0),"semantic_clear":(generator_public.get("summary") or {}).get("semantic_clear",0),"semantic_blocked":(generator_public.get("summary") or {}).get("semantic_blocked",0),"queue_submitted":(queue_public.get("summary") or {}).get("submitted",0),"queue_passed":(queue_public.get("summary") or {}).get("passed_problem_gate",0),"queue_blocked":(queue_public.get("summary") or {}).get("blocked_problem_gate",0)},
                "authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            })
            (run_root/f"{txn_id}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            return record
        except Exception as error:
            record.update({"status":"ABORTED_OPERATOR_RECOMPILE_PUBLIC_STATE_PRESERVED","completed_at":_now(),"error":f"{type(error).__name__}: {error}","stage_diagnostics":{"generator_status":str((generator_internal or {}).get("status") or "NOT_REACHED"),"generator_run_id":str((generator_internal or {}).get("run_id") or ""),"generator_error":" ".join(str((generator_internal or {}).get("error") or "").split())[:500],"queue_reached":queue_internal is not None,"queue_audited":int((((queue_internal or {}).get("summary") or {}).get("audited")) or 0),"scientific_authority":False},"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}})
            stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ");(run_root/f"aborted-recompile-{stamp}-{os.getpid()}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            raise
        finally:
            shutil.rmtree(temp_root,ignore_errors=True)


def recompile_primary_typed_evidence_with_generator_replay_transaction(
    *,
    storage: StorageSettings | None = None,
    primary_json: Path = PRIMARY_JSON,
    primary_js: Path = PRIMARY_JS,
    generator_json: Path = GENERATOR_JSON,
    generator_js: Path = GENERATOR_JS,
    queue_json: Path = QUEUE_JSON,
    queue_js: Path = QUEUE_JS,
    private_pool_source: Path | None = None,
    private_pool_target: Path | None = None,
    fulltext_cache_dir: Path | None = None,
    generator_raw_path: Path,
    queue_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Atomically re-derive typed evidence and replay an archived Generator with zero provider calls.

    This path is for monotone evidence correction: source/fulltext bytes and selected refs are frozen,
    while deterministic derived typed evidence is recompiled under the current extractor. The exact
    prior Generator raw is then parsed under the current discovery operator and corrected pool. If a
    semantic reviewer would still be required, the transaction aborts rather than making a model call.
    """
    storage = storage or StorageSettings.from_env(); storage.ensure()
    primary=_load(primary_json);previous_generator=_load(generator_json);previous_queue=_load(queue_json)
    errors=_validate(primary,previous_generator,previous_queue)
    if errors:raise RuntimeError("existing paper-first discovery state invalid: "+",".join(errors))
    primary_tx=str(primary.get("discovery_transaction_id") or "").strip();generator_tx=str(previous_generator.get("discovery_transaction_id") or "").strip();queue_tx=str(previous_queue.get("discovery_transaction_id") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}",primary_tx) or primary_tx!=generator_tx or primary_tx!=queue_tx:raise RuntimeError("existing paper-first discovery transaction identity mismatch")
    previous_qs=previous_queue.get("summary") or {}
    if int(previous_qs.get("passed_problem_gate") or 0)!=0 or int(previous_qs.get("paper_design_eligible") or 0)!=0:raise RuntimeError("derived-evidence recompile cannot supersede a transaction with a Problem-Gate survivor")
    previous_operator=_generator_operator_version(previous_generator)
    prior_receipt=_generator_receipt(previous_generator);prior_material=_receipt_material(prior_receipt)
    if not previous_operator or not prior_material:raise RuntimeError("derived-evidence recompile requires a provenance-bound prior Generator receipt")

    public_records=[row for row in primary.get("records") or [] if isinstance(row,dict)]
    public_manifest=[(str(row.get("ref") or ""),str(row.get("source_sha256") or ""),str(row.get("fulltext_sha256") or "")) for row in public_records]
    if not public_manifest or any(not ref or len(source_sha)!=64 or len(fulltext_sha)!=64 for ref,source_sha,fulltext_sha in public_manifest):raise RuntimeError("existing Primary manifest is incomplete")
    source_path=Path(private_pool_source) if private_pool_source is not None else private_primary_pool_path(storage);source_pool=load_private_primary_pool(source_path) or {}
    source_records=[row for row in source_pool.get("records") or [] if isinstance(row,dict)];source_manifest=[(str(row.get("ref") or ""),str(row.get("source_sha256") or ""),str(row.get("fulltext_sha256") or "")) for row in source_records]
    if source_pool.get("status")!="READY" or source_manifest!=public_manifest:raise RuntimeError("private Primary recompile source does not exactly match current public Primary records")
    old_pool_sha=_pool_sha(source_pool)
    if prior_material.get("pool_sha256")!=old_pool_sha or prior_material.get("discovery_operator_version")!=previous_operator or prior_material.get("scientific_authority") is not False:raise RuntimeError("prior Generator receipt does not bind the exact old frozen Primary and operator")
    raw_path=Path(generator_raw_path)
    try: raw_bytes=raw_path.read_bytes()
    except OSError as error:raise RuntimeError(f"archived Generator raw unavailable: {type(error).__name__}") from error
    raw_sha=hashlib.sha256(raw_bytes).hexdigest()
    if raw_sha!=str(prior_material.get("raw_sha256") or ""):raise RuntimeError("archived Generator raw SHA does not match prior receipt")
    cache_dir=Path(fulltext_cache_dir) if fulltext_cache_dir is not None else (source_path.parent/"primary-sources")
    recompiled_pool=recompile_frozen_primary_typed_evidence(source_pool,cache_dir=cache_dir)
    new_pool_sha=_pool_sha(recompiled_pool)
    if new_pool_sha==old_pool_sha and str((primary.get("policy") or {}).get("typed_evidence_extraction_version") or "")==str(recompiled_pool.get("typed_evidence_extraction_version") or ""):
        raise RuntimeError("derived-evidence recompile produced no pool or extractor change")
    recompiled_public=project_recompiled_primary_public_state(primary,recompiled_pool)
    recompiled_public.pop("discovery_transaction_id",None);recompiled_public.pop("discovery_transaction_role",None)
    recompiled_pool["generated_at"]=str(primary.get("generated_at") or recompiled_pool.get("generated_at") or "")
    recompiled_pool.setdefault("derived_evidence_recompile",{}).update({"prior_transaction_id":primary_tx,"prior_pool_sha256":old_pool_sha,"recompiled_pool_sha256":new_pool_sha,"source_discovery_operator_version":previous_operator,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"generator_raw_replay_required":True,"scientific_authority":False})

    run_root=storage.run_dir/"paper-first-discovery-transactions";run_root.mkdir(parents=True,exist_ok=True);started=_now()
    with _transaction_lock(storage):
        temp_root=Path(tempfile.mkdtemp(prefix=".paper-first-typed-recompile-",dir=str(primary_json.parent)))
        p_json=temp_root/"primary.json";p_js=temp_root/"primary.js";g_json=temp_root/"generator.json";g_js=temp_root/"generator.js";q_json=temp_root/"queue.json";q_js=temp_root/"queue.js"
        staged_private=temp_root/"primary-private.json";staged_auto=temp_root/"auto-candidate-inbox.json";staged_ledger=temp_root/"discovery-saturation-ledger.json"
        target_private=Path(private_pool_target) if private_pool_target is not None else private_primary_pool_path(storage);target_auto=default_auto_inbox_path(storage);target_ledger=_saturation_ledger_path(storage)
        if target_auto.exists():shutil.copyfile(target_auto,staged_auto)
        if target_ledger.exists():shutil.copyfile(target_ledger,staged_ledger)
        staged_private.write_text(json.dumps(recompiled_pool,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        p_json.write_text(json.dumps(recompiled_public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");p_js.write_text("window.PAPER_FIRST_PRIMARY_EVIDENCE = "+json.dumps(recompiled_public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
        generator_internal:dict[str,Any]|None=None;queue_internal:dict[str,Any]|None=None
        record={"schema_version":"1.0","started_at":started,"status":"running","prior_transaction_id":primary_tx,"prior_pool_sha256":old_pool_sha,"recompiled_pool_sha256":new_pool_sha,"prior_discovery_operator_version":previous_operator,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"source_scheduler_runs_executed":0,"primary_network_fetches_executed":0,"provider_calls_authorized":0,"scientific_authority":False}
        try:
            generator_internal=write_replayed_problem_generator_state(storage=storage,json_path=g_json,js_path=g_js,previous_public_state_path=generator_json,primary_pool_path=staged_private,generator_raw_path=raw_path,generator_raw_sha256=raw_sha,generator_requested_model=str(prior_material.get("requested_model") or ""),generator_resolved_model=str(prior_material.get("resolved_model") or ""),source_generator_run_id=str(prior_material.get("run_id") or ""),source_discovery_operator_version=previous_operator,auto_inbox_path=staged_auto,saturation_ledger_path=staged_ledger)
            generator_calls,semantic_calls=_provider_call_accounting(generator_internal)
            if generator_calls or semantic_calls or int((generator_internal or {}).get("provider_calls_executed") or 0)!=0 or int((generator_internal or {}).get("semantic_reviewer_calls_executed") or 0)!=0:raise RuntimeError("derived-evidence Generator replay attempted provider execution")
            if generator_internal.get("status") in {"REPLAY_REQUIRES_SEMANTIC_REVIEW","REPLAY_INPUT_INVALID","REPLAY_INSUFFICIENT_PRIMARY_EVIDENCE"}:raise RuntimeError(f"derived-evidence Generator replay did not close deterministically: {generator_internal.get('status')}")
            qkw=dict(queue_kwargs or {});qkw.update({"storage":storage,"json_path":q_json,"js_path":q_js,"primary_pool_path":staged_private,"auto_inbox_path":staged_auto});queue_internal=write_problem_gate_queue(**qkw)
            primary_public=_load(p_json);generator_public=_load(g_json);queue_public=_load(q_json);validation=_validate(primary_public,generator_public,queue_public)
            if validation:raise RuntimeError("paper-first derived-evidence replay transaction invalid: "+",".join(validation))
            if _generator_operator_version(generator_public)!=DISCOVERY_OPERATOR_VERSION:raise RuntimeError("derived-evidence replay did not bind current discovery operator")
            receipt=_generator_receipt(generator_public);material=_receipt_material(receipt)
            if not material or material.get("pool_sha256")!=new_pool_sha or material.get("discovery_operator_version")!=DISCOVERY_OPERATOR_VERSION or material.get("raw_sha256")!=raw_sha or material.get("scientific_authority") is not False:raise RuntimeError("derived-evidence replay receipt does not bind corrected pool/raw/operator")
            txn_id=_transaction_id(primary_public,generator_public,queue_public);primary_public=_stamp(p_json,p_js,"PAPER_FIRST_PRIMARY_EVIDENCE",txn_id,"primary");generator_public=_stamp(g_json,g_js,"PAPER_FIRST_PROBLEM_GENERATOR",txn_id,"generator");queue_public=_stamp(q_json,q_js,"PAPER_FIRST_PROBLEM_GATE_QUEUE",txn_id,"queue")
            private_targets=[(staged_private,target_private),(staged_auto,target_auto)];
            if staged_ledger.exists():private_targets.append((staged_ledger,target_ledger))
            _commit_files([(p_json,primary_json),(p_js,primary_js),(g_json,generator_json),(g_js,generator_js),(q_json,queue_json),(q_js,queue_js),*private_targets])
            record.update({"status":"COMMITTED_TYPED_EVIDENCE_RECOMPILE_ZERO_PROVIDER_REPLAY","completed_at":_now(),"transaction_id":txn_id,"generator_receipt_sha256":_receipt_sha256(receipt),"generator_receipt_raw_sha256":raw_sha,"provider_calls_executed":0,"generator_provider_calls_executed":0,"semantic_reviewer_calls_executed":0,"derived_evidence_recompile":dict(recompiled_pool.get("derived_evidence_recompile") or {}),"summary":{"primary_status":primary_public.get("status"),"typed_evidence_candidates":(primary_public.get("summary") or {}).get("typed_evidence_candidates",{}),"generator_status":generator_public.get("status"),"generated":(generator_public.get("summary") or {}).get("generated",0),"semantic_clear":(generator_public.get("summary") or {}).get("semantic_clear",0),"semantic_blocked":(generator_public.get("summary") or {}).get("semantic_blocked",0),"queue_submitted":(queue_public.get("summary") or {}).get("submitted",0),"queue_passed":(queue_public.get("summary") or {}).get("passed_problem_gate",0),"queue_blocked":(queue_public.get("summary") or {}).get("blocked_problem_gate",0)},"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}})
            (run_root/f"{txn_id}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return record
        except Exception as error:
            record.update({"status":"ABORTED_TYPED_EVIDENCE_RECOMPILE_PUBLIC_STATE_PRESERVED","completed_at":_now(),"error":f"{type(error).__name__}: {error}","stage_diagnostics":{"generator_status":str((generator_internal or {}).get("status") or "NOT_REACHED"),"generator_run_id":str((generator_internal or {}).get("run_id") or ""),"queue_reached":queue_internal is not None,"queue_audited":int((((queue_internal or {}).get("summary") or {}).get("audited")) or 0),"scientific_authority":False},"authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}});stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ");(run_root/f"aborted-typed-recompile-{stamp}-{os.getpid()}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise
        finally:
            shutil.rmtree(temp_root,ignore_errors=True)


def write_problem_discovery_transaction(
    *,
    storage: StorageSettings | None = None,
    primary_json: Path = PRIMARY_JSON,
    primary_js: Path = PRIMARY_JS,
    generator_json: Path = GENERATOR_JSON,
    generator_js: Path = GENERATOR_JS,
    queue_json: Path = QUEUE_JSON,
    queue_js: Path = QUEUE_JS,
    primary_kwargs: dict[str, Any] | None = None,
    generator_kwargs: dict[str, Any] | None = None,
    queue_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run Primary -> Generator -> Queue and expose the public state only as one transaction."""
    storage = storage or StorageSettings.from_env(); storage.ensure()
    run_root = storage.run_dir / "paper-first-discovery-transactions"; run_root.mkdir(parents=True, exist_ok=True)
    started = _now()
    with _transaction_lock(storage):
        primary_json.parent.mkdir(parents=True,exist_ok=True)
        temp_root = Path(tempfile.mkdtemp(prefix=".paper-first-txn-", dir=str(primary_json.parent)))
        p_json=temp_root/"primary.json";p_js=temp_root/"primary.js";g_json=temp_root/"generator.json";g_js=temp_root/"generator.js";q_json=temp_root/"queue.json";q_js=temp_root/"queue.js"
        staged_private=temp_root/"primary-private.json";staged_auto=temp_root/"auto-candidate-inbox.json";staged_ledger=temp_root/"discovery-saturation-ledger.json"
        target_private=private_primary_pool_path(storage);target_auto=default_auto_inbox_path(storage);target_ledger=_saturation_ledger_path(storage)
        if target_auto.exists(): shutil.copyfile(target_auto,staged_auto)
        if target_ledger.exists(): shutil.copyfile(target_ledger,staged_ledger)
        record: dict[str, Any] = {"schema_version":"1.0","started_at":started,"status":"running","scientific_authority":False}
        primary_internal: dict[str, Any] | None = None
        generator_internal: dict[str, Any] | None = None
        queue_internal: dict[str, Any] | None = None
        try:
            pkw=dict(primary_kwargs or {});pkw.update({"storage":storage,"json_path":p_json,"js_path":p_js,"portable_generator_state_path":generator_json,"portable_primary_state_path":primary_json,"private_pool_output_path":staged_private})
            primary_internal=write_primary_evidence_pool(**pkw)
            gkw=dict(generator_kwargs or {});gkw.update({"storage":storage,"json_path":g_json,"js_path":g_js,"previous_public_state_path":generator_json,"primary_pool_path":staged_private,"auto_inbox_path":staged_auto,"saturation_ledger_path":staged_ledger})
            generator_internal=write_problem_generator_state(**gkw)
            qkw=dict(queue_kwargs or {});qkw.update({"storage":storage,"json_path":q_json,"js_path":q_js,"primary_pool_path":staged_private,"auto_inbox_path":staged_auto})
            queue_internal=write_problem_gate_queue(**qkw)
            primary_public=_load(p_json);generator_public=_load(g_json);queue_public=_load(q_json)
            errors=_validate(primary_public,generator_public,queue_public)
            if errors:
                raise RuntimeError("paper-first discovery transaction invalid: " + ",".join(errors))
            transaction_operator=_generator_operator_version(generator_public)
            transaction_receipt=_generator_receipt(generator_public)
            transaction_receipt_material=_receipt_material(transaction_receipt)
            staged_pool=load_private_primary_pool(staged_private) or {}
            source_pool_sha=_pool_sha(staged_pool) if staged_pool else ""
            if transaction_receipt_material and (
                transaction_receipt_material.get("pool_sha256")!=source_pool_sha
                or transaction_receipt_material.get("discovery_operator_version")!=transaction_operator
                or transaction_receipt_material.get("run_id")!=str(generator_public.get("run_id") or "")
                or transaction_receipt_material.get("status")!=str(generator_public.get("status") or "")
                or transaction_receipt_material.get("scientific_authority") is not False
            ):
                raise RuntimeError("Generator receipt does not bind the full discovery transaction")
            generator_calls,semantic_calls=_provider_call_accounting(generator_internal)
            txn_id=_transaction_id(primary_public,generator_public,queue_public)
            primary_public=_stamp(p_json,p_js,"PAPER_FIRST_PRIMARY_EVIDENCE",txn_id,"primary")
            generator_public=_stamp(g_json,g_js,"PAPER_FIRST_PROBLEM_GENERATOR",txn_id,"generator")
            queue_public=_stamp(q_json,q_js,"PAPER_FIRST_PROBLEM_GATE_QUEUE",txn_id,"queue")
            private_targets=[(staged_private,target_private),(staged_auto,target_auto)]
            if staged_ledger.exists(): private_targets.append((staged_ledger,target_ledger))
            _commit_files([(p_json,primary_json),(p_js,primary_js),(g_json,generator_json),(g_js,generator_js),(q_json,queue_json),(q_js,queue_js),*private_targets])
            record.update({
                "status":"COMMITTED","completed_at":_now(),"transaction_id":txn_id,
                "source_pool_sha256":source_pool_sha,
                "discovery_operator_version":transaction_operator,
                "generator_receipt_run_id":str(transaction_receipt_material.get("run_id") or ""),
                "generator_receipt_sha256":_receipt_sha256(transaction_receipt),
                "generator_receipt_raw_sha256":str(transaction_receipt_material.get("raw_sha256") or ""),
                "provider_calls_executed":generator_calls+semantic_calls,
                "generator_provider_calls_executed":generator_calls,
                "semantic_reviewer_calls_executed":semantic_calls,
                "summary":{
                    "primary_status":primary_public.get("status"),"verified":(primary_public.get("summary") or {}).get("verified",0),
                    "eligible_unreviewed":(primary_public.get("summary") or {}).get("eligible_unreviewed",0),
                    "generator_status":generator_public.get("status"),"generated":(generator_public.get("summary") or {}).get("generated",0),
                    "source_coverage_exhausted":bool((primary_public.get("summary") or {}).get("source_coverage_exhausted")),
                    "source_retrieval_complete":bool((primary_public.get("summary") or {}).get("source_retrieval_complete")),
                    "unreviewed_lane_linked_sources":(primary_public.get("summary") or {}).get("unreviewed_lane_linked_sources",0),
                    "carrier_probe_required":bool((primary_public.get("summary") or {}).get("carrier_probe_required")),
                    "carrier_probe_attempted":int((primary_public.get("summary") or {}).get("carrier_probe_attempted") or 0),
                    "carrier_probe_rescued":int((primary_public.get("summary") or {}).get("carrier_probe_rescued") or 0),
                    "carrier_probe_pending":int((primary_public.get("summary") or {}).get("carrier_probe_pending") or 0),
                    "carrier_probe_complete":bool((primary_public.get("summary") or {}).get("carrier_probe_complete",True)),
                    "semantic_clear":(generator_public.get("summary") or {}).get("semantic_clear",0),"semantic_blocked":(generator_public.get("summary") or {}).get("semantic_blocked",0),
                    "queue_submitted":(queue_public.get("summary") or {}).get("submitted",0),"queue_passed":(queue_public.get("summary") or {}).get("passed_problem_gate",0),"queue_blocked":(queue_public.get("summary") or {}).get("blocked_problem_gate",0),
                },
                "authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False},
                "internal_status":{"primary":primary_internal.get("status"),"generator":generator_internal.get("status"),"queue_audited":(queue_internal.get("summary") or {}).get("audited",0)},
            })
            (run_root/f"{txn_id}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            return record
        except Exception as error:
            primary_summary=(primary_internal or {}).get("summary") or {}
            generator_artifacts=(generator_internal or {}).get("raw_artifacts") or {}
            generator_raw=generator_artifacts.get("generator") or {}
            transport_attempts=list(generator_raw.get("transport_attempts") or []) if isinstance(generator_raw,dict) else []
            record.update({
                "status":"ABORTED_PUBLIC_STATE_PRESERVED",
                "completed_at":_now(),
                "error":f"{type(error).__name__}: {error}",
                "stage_diagnostics":{
                    "primary_status":str((primary_internal or {}).get("status") or "NOT_REACHED"),
                    "primary_verified":int(primary_summary.get("verified") or 0),
                    "primary_selected_unreviewed":int(primary_summary.get("selected_unreviewed") or 0),
                    "primary_unreviewed_lane_linked_sources":int(primary_summary.get("unreviewed_lane_linked_sources") or 0),
                    "generator_status":str((generator_internal or {}).get("status") or "NOT_REACHED"),
                    "generator_run_id":str((generator_internal or {}).get("run_id") or ""),
                    "generator_error":" ".join(str((generator_internal or {}).get("error") or "").split())[:500],
                    "generator_raw_output_present":bool(isinstance(generator_raw,dict) and generator_raw.get("sha256")),
                    "generator_transport_attempts":transport_attempts[:2],
                    "queue_reached":queue_internal is not None,
                    "queue_audited":int((((queue_internal or {}).get("summary") or {}).get("audited")) or 0),
                    "scientific_authority":False,
                },
                "authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            })
            stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            (run_root/f"aborted-{stamp}-{os.getpid()}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            raise
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    print(json.dumps(write_problem_discovery_transaction(), ensure_ascii=False, indent=2))
