from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_pre_f0_queue import DEFAULT_JSON as PRE_F0_JSON, load_pre_f0_queue
from .paper_first_primary_evidence import (
    EMPIRICAL_FACT_EXTRACTION_VERSION,
    TYPED_EVIDENCE_EXTRACTION_VERSION,
    _paper_lane_keys,
    extract_empirical_fact_candidates,
    extract_typed_evidence_candidates,
    load_private_primary_pool,
    load_primary_evidence_state,
    parse_arxiv_page,
    private_primary_pool_path,
)
from .paper_first_problem_generator import _pool_sha, load_problem_generator_state
from .paper_first_problem_gate_queue import load_problem_gate_queue_state
from .paper_first_shadow_search_admission import primary_content_sha256, source_set_sha256
from .problem_search_control_snapshot import write_shadow_run_qualification
from .problem_search_shadow_launcher import _frozen_memory_payload

DEFAULT_INTAKE = PROJECT_ROOT / "generated" / "paper-first-external-fresh-intake-20260818.json"
DEFAULT_SUPPORT_PREFLIGHT = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"
DEFAULT_ROUND3_MANIFEST = PROJECT_ROOT / "generated" / "round3-provenance-manifest.json"
DEFAULT_MEMORY = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"
SEARCH_HOLD_MIN_TARGET = 5
ALLOWED_DELTA_DISPOSITIONS = {"CAPABILITY_EVIDENCE_ONLY"}

AUTHORITY = {
    "canonical_primary": False,
    "canonical_generator": False,
    "canonical_queue": False,
    "problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _latest_cache(root: Path, pattern: str) -> Path:
    rows = sorted(root.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    if not rows:
        raise ValueError(f"parallel delta source cache unavailable:{pattern}")
    return rows[0]


def _verified_delta_record(*, source_root: Path, intake_row: dict[str, Any]) -> dict[str, Any]:
    ref = str(intake_row.get("ref") or "").strip()
    if not re.fullmatch(r"arXiv:[0-9]{4}\.[0-9]{4,5}", ref):
        raise ValueError(f"parallel delta source ref invalid:{ref}")
    if intake_row.get("identity_verified") is not True:
        raise ValueError(f"parallel delta source identity is not verified:{ref}")
    disposition = str(intake_row.get("disposition") or "").strip()
    if disposition not in ALLOWED_DELTA_DISPOSITIONS:
        raise ValueError(f"parallel delta source disposition cannot reopen search:{ref}:{disposition}")
    aid = ref.split(":", 1)[1]
    primary_path = _latest_cache(source_root, f"arxiv-{aid}-*.html")
    fulltext_path = _latest_cache(source_root, f"arxiv-full-{aid}-*.html")
    primary_bytes = primary_path.read_bytes()
    fulltext_bytes = fulltext_path.read_bytes()
    source_sha = _sha_bytes(primary_bytes)
    fulltext_sha = _sha_bytes(fulltext_bytes)
    if not primary_path.stem.endswith(source_sha[:12]) or not fulltext_path.stem.endswith(fulltext_sha[:12]):
        raise ValueError(f"parallel delta source cache digest mismatch:{ref}")
    parsed = parse_arxiv_page(primary_bytes.decode("utf-8", errors="replace"))
    expected_title = " ".join(str(intake_row.get("title") or "").split())
    actual_title = " ".join(str(parsed.get("title") or "").split())
    if not actual_title or actual_title != expected_title or not parsed.get("abstract"):
        raise ValueError(f"parallel delta source title or abstract mismatch:{ref}")
    lane_keys = list(_paper_lane_keys(parsed))
    if not lane_keys:
        raise ValueError(f"parallel delta source is not lane grounded:{ref}")
    fulltext = fulltext_bytes.decode("utf-8", errors="replace")
    published = str(intake_row.get("published") or "").strip()
    return {
        "evidence_id": f"EVID-{aid.replace('.', '-')}",
        "ref": ref,
        "s2_paper_id": "",
        "title": actual_title,
        "year": int(published[:4]) if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", published) else 0,
        "publication_date": published,
        "abstract": str(parsed["abstract"]),
        "primary_url": f"https://arxiv.org/abs/{aid}",
        "fulltext_url": f"https://arxiv.org/html/{aid}",
        "source_sha256": source_sha,
        "abstract_sha256": _sha_bytes(str(parsed["abstract"]).encode()),
        "fulltext_sha256": fulltext_sha,
        "cache_path": str(primary_path),
        "fulltext_cache_path": str(fulltext_path),
        "fetched_at": _now(),
        "s2_retrieved_at": "",
        "title_similarity": 1.0,
        "primary_source_verified": True,
        "lane_keys": lane_keys,
        "empirical_facts": extract_empirical_fact_candidates(fulltext),
        "typed_evidence": extract_typed_evidence_candidates(fulltext),
        "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
        "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
        "parallel_delta_provenance": {
            "intake_disposition": disposition,
            "candidate_source_only": True,
            "disposition_has_no_scientific_negative_authority": True,
            "scientific_authority": False,
        },
    }


def build_parallel_search_admission(
    *,
    primary_state: dict[str, Any],
    generator_state: dict[str, Any],
    queue_state: dict[str, Any],
    pre_f0_state: dict[str, Any],
    support_preflight: dict[str, Any],
    round3_manifest: dict[str, Any],
    canonical_private_pool: dict[str, Any],
    delta_records: list[dict[str, Any]],
) -> dict[str, Any]:
    primary_tx = str(primary_state.get("discovery_transaction_id") or "")
    generator_tx = str(generator_state.get("discovery_transaction_id") or "")
    queue_tx = str(queue_state.get("discovery_transaction_id") or "")
    queue_summary = queue_state.get("summary") or {}
    support_summary = support_preflight.get("summary") or {}
    current_rows = [row for row in pre_f0_state.get("rows") or [] if isinstance(row, dict)]
    current_snapshots = sorted(
        {
            str(row.get("candidate_snapshot_sha256") or "")
            for row in current_rows
            if re.fullmatch(r"[0-9a-f]{64}", str(row.get("candidate_snapshot_sha256") or ""))
        }
    )
    canonical_pool_sha = _pool_sha(canonical_private_pool)
    recovery = generator_state.get("portfolio_ingestion_recovery") or {}
    round3_tx = round3_manifest.get("transaction") or {}
    round3_sources = round3_manifest.get("source_artifacts") or {}
    round3_coverage = round3_manifest.get("coverage") or {}
    stamped_transaction = bool(re.fullmatch(r"[0-9a-f]{64}", primary_tx)) and primary_tx == generator_tx == queue_tx
    recovery_lineage = (
        bool(re.fullmatch(r"[0-9a-f]{64}", primary_tx))
        and primary_tx == queue_tx
        and not generator_tx
        and round3_manifest.get("status") == "ROUND3_PROVENANCE_COMPLETE"
        and all(value is True for value in round3_coverage.values())
        and str(recovery.get("source_transaction_id") or "") == primary_tx == str(round3_tx.get("transaction_id") or "")
        and str(round3_tx.get("source_pool_sha256") or "") == canonical_pool_sha
        and str(recovery.get("source_portfolio_sha256") or "") == str(round3_sources.get("portfolio_sha256") or "")
        and str(recovery.get("recovery_sha256") or "") == str(round3_sources.get("ingestion_recovery_sha256") or "")
        and str(recovery.get("recovery_sha256") or "") == str((((generator_state.get("raw_artifacts") or {}).get("generator") or {}).get("sha256") or ""))
    )
    canonical_records = [row for row in canonical_private_pool.get("records") or [] if isinstance(row, dict)]
    canonical_refs = {str(row.get("ref") or "") for row in canonical_records}
    delta_refs = [str(row.get("ref") or "") for row in delta_records]
    checks = [
        {"key": "canonical-primary-ready", "pass": primary_state.get("status") == "READY"},
        {"key": "canonical-private-pool-ready", "pass": canonical_private_pool.get("status") == "READY"},
        {"key": "canonical-transaction-or-round3-recovery-bound", "pass": stamped_transaction or recovery_lineage},
        {"key": "canonical-private-pool-receipt-bound", "pass": str((((generator_state.get("saturation_memory") or {}).get("current_review_receipt") or {}).get("pool_sha256") or "")) == canonical_pool_sha},
        {"key": "no-problem-gate-survivor", "pass": int(queue_summary.get("passed_problem_gate") or 0) == 0 and int(queue_summary.get("paper_design_eligible") or 0) == 0},
        {"key": "pre-f0-hold-snapshots-complete", "pass": bool(current_rows) and len(current_snapshots) == len(current_rows)},
        {"key": "support-preflight-covers-current-holds", "pass": int(support_summary.get("queued") or 0) == len(current_rows) and int(support_summary.get("support_qualified") or 0) == 0 and int(support_summary.get("hold_support_unavailable") or 0) == len(current_rows) and int(support_summary.get("falsifier_executed") or 0) == 0},
        {"key": "search-hold-capacity-shortfall", "pass": len(current_rows) < SEARCH_HOLD_MIN_TARGET},
        {"key": "delta-source-present", "pass": bool(delta_records)},
        {"key": "delta-source-refs-unique", "pass": len(delta_refs) == len(set(delta_refs))},
        {"key": "delta-source-not-canonical", "pass": bool(delta_refs) and all(ref not in canonical_refs for ref in delta_refs)},
        {"key": "delta-source-primary-verified", "pass": bool(delta_records) and all(row.get("primary_source_verified") is True for row in delta_records)},
        {"key": "delta-source-lane-grounded", "pass": bool(delta_records) and all(bool(row.get("lane_keys")) for row in delta_records)},
        {"key": "delta-source-zero-authority", "pass": bool(delta_records) and all(((row.get("parallel_delta_provenance") or {}).get("scientific_authority") is False) for row in delta_records)},
    ]
    ready = all(row["pass"] is True for row in checks)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "status": "READY_FOR_PARALLEL_SEARCH_QUALIFICATION" if ready else "HOLD_PARALLEL_SEARCH_ADMISSION",
        "policy": {
            "scientific_authority": False,
            "parallel_search_is_capacity_recovery_not_scientific_adjudication": True,
            "current_candidate_snapshots_are_immutable_inputs": True,
            "parallel_search_cannot_mutate_current_candidate_dispositions": True,
            "capability_evidence_can_reopen_search_but_cannot_create_a_claim": True,
            "external_intake_disposition_cannot_be_reinterpreted_as_scientific_failure": True,
            "canonical_primary_generator_queue_untouched": True,
            "round3_recovery_lineage_may_bind_missing_generator_envelope_stamp": True,
            "recovery_lineage_requires_complete_record_level_provenance_manifest": True,
            "qualification_receipt_required_before_provider_calls": True,
            "provider_failure_has_no_scientific_authority": True,
        },
        "summary": {
            "checks": len(checks),
            "passed_checks": sum(row["pass"] is True for row in checks),
            "failed_checks": sum(row["pass"] is not True for row in checks),
            "current_pre_f0_holds": len(current_rows),
            "search_hold_min_target": SEARCH_HOLD_MIN_TARGET,
            "search_hold_shortfall": max(0, SEARCH_HOLD_MIN_TARGET - len(current_rows)),
            "delta_sources": len(delta_records),
            "canonical_records": len(canonical_records),
            "parallel_records": len(canonical_records) + len(delta_records),
            "automatic_provider_calls_authorized": 0,
        },
        "canonical_binding": {
            "mode": "STAMPED_TRANSACTION" if stamped_transaction else ("ROUND3_RECOVERY_LINEAGE" if recovery_lineage else "UNBOUND"),
            "discovery_transaction_id": primary_tx,
            "canonical_pool_sha256": canonical_pool_sha,
            "round3_manifest_content_sha256": str(round3_manifest.get("manifest_content_sha256") or ""),
            "current_candidate_snapshot_sha256": current_snapshots,
        },
        "delta_binding": {
            "refs": sorted(delta_refs),
            "source_set_sha256": source_set_sha256(delta_records),
            "primary_content_sha256": primary_content_sha256(delta_records),
        },
        "checks": checks,
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def prepare_parallel_search_run(
    *,
    run_root: Path,
    delta_refs: tuple[str, ...],
    storage: StorageSettings | None = None,
    intake_path: Path = DEFAULT_INTAKE,
    memory_path: Path = DEFAULT_MEMORY,
    support_preflight_path: Path = DEFAULT_SUPPORT_PREFLIGHT,
    round3_manifest_path: Path = DEFAULT_ROUND3_MANIFEST,
    require_clean_control: bool = True,
) -> dict[str, Any]:
    if not run_root.name.startswith("shadow-"):
        raise ValueError("parallel search run root must start with shadow-")
    if run_root.exists() and any(run_root.iterdir()):
        raise ValueError("parallel search run root must be absent or empty")
    storage = storage or StorageSettings.from_env()
    primary = load_primary_evidence_state()
    generator = load_problem_generator_state()
    queue = load_problem_gate_queue_state()
    pre_f0 = load_pre_f0_queue(PRE_F0_JSON)
    support = _load(support_preflight_path)
    round3_manifest = _load(round3_manifest_path)
    private_path = private_primary_pool_path(storage)
    canonical_pool = load_private_primary_pool(private_path) or {}
    intake = _load(intake_path)
    intake_by_ref = {str(row.get("ref") or ""): row for row in intake.get("sources") or [] if isinstance(row, dict)}
    if not delta_refs or len(delta_refs) != len(set(delta_refs)):
        raise ValueError("parallel search requires unique explicit delta refs")
    source_root = private_path.parent / "primary-sources"
    delta_records = []
    for ref in delta_refs:
        if ref not in intake_by_ref:
            raise ValueError(f"parallel delta ref absent from reviewed external intake:{ref}")
        delta_records.append(_verified_delta_record(source_root=source_root, intake_row=intake_by_ref[ref]))
    admission = build_parallel_search_admission(
        primary_state=primary,
        generator_state=generator,
        queue_state=queue,
        pre_f0_state=pre_f0,
        support_preflight=support,
        round3_manifest=round3_manifest,
        canonical_private_pool=canonical_pool,
        delta_records=delta_records,
    )
    if admission["status"] != "READY_FOR_PARALLEL_SEARCH_QUALIFICATION":
        return admission
    memory = _frozen_memory_payload(memory_path)
    records = json.loads(json.dumps([*canonical_pool.get("records", []), *delta_records], ensure_ascii=False))
    source_generated_at = _now()
    pool = {
        "schema_version": "1.2-parallel-primary-delta-pool",
        "status": "READY",
        "generated_at": source_generated_at,
        "source_generated_at": source_generated_at,
        "scientific_authority": False,
        "summary": {
            "selected": len(records),
            "verified": sum(row.get("primary_source_verified") is True for row in records),
            "canonical_records": len(canonical_pool.get("records") or []),
            "delta_records": len(delta_records),
        },
        "policy": {
            "pool_source_kind": "parallel_primary_delta_pool",
            "canonical_primary_generator_queue_untouched": True,
            "delta_sources_are_candidate_sources_only": True,
            "delta_dispositions_have_zero_scientific_authority": True,
            "automatic_provider_authority": False,
            "candidate_generation_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "gpu_authority": False,
        },
        "parallel_search_admission": admission,
        "records": records,
    }
    pool["source_set_sha256"] = source_set_sha256(records)
    pool["source_primary_content_sha256"] = primary_content_sha256(records)
    pool["source_pool_sha256"] = _pool_sha(pool)
    canonical = json.dumps(pool, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    pool["frozen_pool_sha256"] = _sha_bytes(canonical)
    run_root.mkdir(parents=True, exist_ok=False)
    pool_path = run_root / "frozen-primary-evidence-pool.json"
    memory_out = run_root / "shadow-search-memory.json"
    admission_path = run_root / "parallel-search-admission.json"
    pool_path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    memory_out.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    admission_path.write_text(json.dumps(admission, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qualification = write_shadow_run_qualification(
        run_root=run_root,
        pool_path=pool_path,
        memory_path=memory_out,
        require_clean_control=require_clean_control,
    )
    return {
        **admission,
        "status": "READY_FOR_PARALLEL_SEARCH_EXPANSION",
        "run_id": run_root.name,
        "qualification": {
            "status": qualification.get("status"),
            "stage_runner_required_schema": qualification.get("stage_runner_required_schema"),
            "control_snapshot_sha256": qualification.get("control_snapshot_sha256"),
            "frozen_pool_sha256": qualification.get("frozen_pool_sha256"),
            "scientific_authority": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--delta-ref", action="append", required=True)
    args = parser.parse_args()
    state = prepare_parallel_search_run(run_root=args.run_root, delta_refs=tuple(args.delta_ref))
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
