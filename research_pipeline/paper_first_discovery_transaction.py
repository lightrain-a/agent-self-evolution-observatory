from __future__ import annotations

import fcntl
import hashlib
import json
import os
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
    write_primary_evidence_pool,
)
from .paper_first_problem_discovery_contract import DISCOVERY_LANES
from .paper_first_problem_generator import (
    DEFAULT_JSON as GENERATOR_JSON,
    DEFAULT_JS as GENERATOR_JS,
    _normalize_last_completed_lane_search_receipt,
    write_problem_generator_state,
)
from .paper_first_problem_gate_queue import (
    DEFAULT_JSON as QUEUE_JSON,
    DEFAULT_JS as QUEUE_JS,
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


@contextmanager
def _transaction_lock(storage: StorageSettings) -> Iterator[None]:
    path = storage.lock_dir / ".paper-first-discovery-transaction.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"Another paper-first discovery transaction is active: {path}") from error
        handle.seek(0); handle.truncate(); handle.write(json.dumps({"pid": os.getpid(), "started_at": _now()})); handle.flush()
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
        "carrier_probe_receipts": carrier_receipts,
        "carrier_probe_pending": int(((primary.get("carrier_probe") or {}).get("pending") or 0)),
        "generator_run_id": generator.get("run_id"),
        "generator_status": generator.get("status"),
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
            if not isinstance(row,dict) or row.get("scientific_authority") is not False or len(str(row.get("primary_sha256") or ""))!=64 or len(str(row.get("fulltext_sha256") or ""))!=64 or not str(row.get("classifier_version") or ""):
                errors.append("primary-carrier-probe-receipt-invalid"); break
            if any(str(value) not in allowed_objects for value in row.get("live_rescue_eligible_lanes") or []):
                errors.append("primary-carrier-probe-created-unknown-object"); break
    generator_status = str(generator.get("status") or "")
    generator_policy = generator.get("policy") or {}
    if generator_policy.get("search_portfolio_enabled") is True:
        errors.append("canonical-transaction-forbids-search-portfolio")
    if generator_policy.get("one_generator_call_max") is not True or generator_policy.get("one_semantic_reviewer_call_max") is not True:
        errors.append("canonical-transaction-requires-single-call-budget")
    allowed_generator_statuses = {"GENERATED_ZERO_CANDIDATES", "GENERATED_AWAIT_PROBLEM_GATE", "SKIPPED_SOURCE_COVERAGE_SATURATED", "SKIPPED_SOURCE_CARRIER_PROBE_PENDING"}
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
    if generator_status in {"SKIPPED_SOURCE_COVERAGE_SATURATED","SKIPPED_SOURCE_CARRIER_PROBE_PENDING"} and any(value != 0 for value in (submitted, audited_count, passed, blocked)):
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
        record: dict[str, Any] = {"schema_version":"1.0","started_at":started,"status":"running","scientific_authority":False}
        try:
            pkw=dict(primary_kwargs or {});pkw.update({"storage":storage,"json_path":p_json,"js_path":p_js,"portable_generator_state_path":generator_json,"portable_primary_state_path":primary_json})
            primary_internal=write_primary_evidence_pool(**pkw)
            gkw=dict(generator_kwargs or {});gkw.update({"storage":storage,"json_path":g_json,"js_path":g_js,"previous_public_state_path":generator_json})
            generator_internal=write_problem_generator_state(**gkw)
            qkw=dict(queue_kwargs or {});qkw.update({"storage":storage,"json_path":q_json,"js_path":q_js})
            queue_internal=write_problem_gate_queue(**qkw)
            primary_public=_load(p_json);generator_public=_load(g_json);queue_public=_load(q_json)
            errors=_validate(primary_public,generator_public,queue_public)
            if errors:
                raise RuntimeError("paper-first discovery transaction invalid: " + ",".join(errors))
            txn_id=_transaction_id(primary_public,generator_public,queue_public)
            primary_public=_stamp(p_json,p_js,"PAPER_FIRST_PRIMARY_EVIDENCE",txn_id,"primary")
            generator_public=_stamp(g_json,g_js,"PAPER_FIRST_PROBLEM_GENERATOR",txn_id,"generator")
            queue_public=_stamp(q_json,q_js,"PAPER_FIRST_PROBLEM_GATE_QUEUE",txn_id,"queue")
            _commit_files([(p_json,primary_json),(p_js,primary_js),(g_json,generator_json),(g_js,generator_js),(q_json,queue_json),(q_js,queue_js)])
            record.update({
                "status":"COMMITTED","completed_at":_now(),"transaction_id":txn_id,
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
            record.update({"status":"ABORTED_PUBLIC_STATE_PRESERVED","completed_at":_now(),"error":f"{type(error).__name__}: {error}","authority":{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False}})
            stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            (run_root/f"aborted-{stamp}-{os.getpid()}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            raise
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    print(json.dumps(write_problem_discovery_transaction(), ensure_ascii=False, indent=2))
