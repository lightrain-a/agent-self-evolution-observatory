from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import load_private_primary_pool, private_primary_pool_path
from .paper_first_problem_generator import _pool_sha
from .paper_first_problem_discovery_contract import DISCOVERY_OPERATOR_VERSION
from .paper_first_search_portfolio_design_adjudication import DEFAULT_JSON as DEFAULT_SHADOW_MEMORY_PATH
from .paper_first_shadow_search_admission import (
    build_shadow_search_admission,
    primary_content_sha256,
    source_set_sha256,
    validate_shadow_search_admission,
)
from .problem_search_control_snapshot import CONTROL_FILES, write_shadow_run_qualification

READY_STATUS = "READY_FOR_SHADOW_QUALIFICATION"
HANDOFF_STATUS = "READY_FOR_SHADOW_EXPANSION_ZERO_PROVIDER_HANDOFF"
AUTHORITY = {
    "canonical_generator": False,
    "canonical_queue": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _bounded_result(status: str, *, admission: dict[str, Any], reason: str, run_root: Path | None = None, **summary: Any) -> dict[str, Any]:
    admission_summary = admission.get("summary") or {}
    return {
        "schema_version": "1.0",
        "status": status,
        "reason": reason[:1000],
        "run_id": run_root.name if run_root is not None else "",
        "admission_status": str(admission.get("status") or ""),
        "summary": {
            "canonical_transaction_closed": bool(admission_summary.get("canonical_transaction_closed")),
            "same_source_transaction": bool(admission_summary.get("same_source_transaction")),
            "qualification_allowed": bool(admission_summary.get("qualification_allowed")),
            "frozen_pool_created": bool(summary.get("frozen_pool_created", False)),
            "frozen_memory_created": bool(summary.get("frozen_memory_created", False)),
            "qualification_created": bool(summary.get("qualification_created", False)),
            "automatic_provider_calls_authorized": 0,
            "model_calls_executed": 0,
        },
        "provenance": {
            key: summary.get(key, "")
            for key in (
                "source_generated_at",
                "source_set_sha256",
                "source_primary_content_sha256",
                "source_pool_sha256",
                "frozen_pool_sha256",
                "discovery_operator_version",
                "memory_sha256",
                "control_snapshot_sha256",
                "stage_runner_required_schema",
                "main_commit",
            )
        },
        "policy": {
            "launcher_runs_only_after_shadow_admission": True,
            "canonical_main_private_pool_is_required": True,
            "private_pool_identity_must_match_current_admitted_primary": True,
            "launcher_can_only_freeze_pool_memory_and_qualification": True,
            "run_local_memory_is_frozen_before_qualification": True,
            "launcher_never_calls_model_provider": True,
            "stage_runner_still_requires_qualification_receipt": True,
            "scientific_authority": False,
        },
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def _frozen_memory_payload(memory_path: Path) -> dict[str, Any]:
    try:
        payload=json.loads(memory_path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as error:
        raise ValueError(f"shadow dead-end memory unreadable: {error}") from error
    memory=payload.get("shadow_dead_end_memory") if isinstance(payload,dict) else None
    if not isinstance(memory,dict):
        memory=payload if isinstance(payload,dict) else {}
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True:
        raise ValueError("shadow dead-end memory must be zero-authority and unable to mutate canonical discovery")
    rows=memory.get("blocked_objects") or []
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
        raise ValueError("shadow dead-end memory blocked_objects must be a list of objects")
    return json.loads(json.dumps(memory,ensure_ascii=False))


def _frozen_pool_payload(private_pool: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    records = [json.loads(json.dumps(row, ensure_ascii=False)) for row in private_pool.get("records") or [] if isinstance(row, dict)]
    source = admission.get("source_identity") or {}
    generated_at = str(private_pool.get("generated_at") or "").strip()
    source_set_sha = source_set_sha256(records)
    source_content_sha = primary_content_sha256(records)
    source_pool_sha = _pool_sha(private_pool)
    expected_generated_at = str(source.get("current_source_generated_at") or "").strip()
    expected_set_sha = str(source.get("current_source_set_sha256") or "").strip().lower()
    expected_content_sha = str(source.get("current_primary_content_sha256") or "").strip().lower()
    if generated_at != expected_generated_at:
        raise ValueError("canonical private pool generated_at does not match admitted Primary")
    if source_set_sha != expected_set_sha:
        raise ValueError("canonical private pool source-set digest does not match admitted Primary")
    if source_content_sha != expected_content_sha:
        raise ValueError("canonical private pool primary-content digest does not match admitted Primary")
    if not re.fullmatch(r"[0-9a-f]{64}", source_pool_sha):
        raise ValueError("canonical private pool digest invalid")
    payload = {
        "schema_version": "1.1-shadow-frozen-pool",
        "status": "READY",
        "generated_at": generated_at,
        "source_generated_at": generated_at,
        "source_pool_sha256": source_pool_sha,
        "source_set_sha256": source_set_sha,
        "source_primary_content_sha256": source_content_sha,
        "frozen_for_shadow_search_portfolio": True,
        "discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
        "scientific_authority": False,
        "summary": {
            "selected": len(records),
            "verified": sum(row.get("primary_source_verified") is True for row in records),
            "fulltext_verified": sum(bool(row.get("fulltext_sha256")) for row in records),
            "candidate_generation_ready": bool(records),
        },
        "policy": {
            "canonical_private_pool_source": True,
            "source_identity_bound_before_copy": True,
            "admission_precedes_freeze": True,
            "automatic_provider_authority": False,
            "candidate_generation_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "gpu_authority": False,
        },
        "records": records,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    import hashlib
    payload["frozen_pool_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def prepare_shadow_run(
    *,
    run_root: Path,
    private_pool_path: Path | None = None,
    memory_path: Path = DEFAULT_SHADOW_MEMORY_PATH,
    project_root: Path = PROJECT_ROOT,
    admission_state: dict[str, Any] | None = None,
    require_clean_control: bool = True,
    control_files: Iterable[str] = CONTROL_FILES,
) -> dict[str, Any]:
    admission = admission_state if admission_state is not None else build_shadow_search_admission()
    admission_errors = validate_shadow_search_admission(admission)
    if admission_errors:
        raise ValueError("invalid shadow admission: " + ";".join(admission_errors))
    if admission.get("status") != READY_STATUS:
        return _bounded_result(
            str(admission.get("status") or "HOLD_SHADOW_ADMISSION"),
            admission=admission,
            reason=str(admission.get("reason") or "Shadow admission did not open qualification."),
        )
    if not run_root.name.startswith("shadow-"):
        raise ValueError("shadow launcher run_root name must start with shadow-")
    if run_root.exists() and any(run_root.iterdir()):
        raise ValueError("shadow launcher requires an absent or empty run root before freeze")
    if not memory_path.is_file():
        return _bounded_result("HOLD_SHADOW_MEMORY_UNAVAILABLE", admission=admission, reason=f"Shadow dead-end memory unavailable: {memory_path}", run_root=run_root)
    try:
        frozen_memory=_frozen_memory_payload(memory_path)
    except ValueError as error:
        return _bounded_result("HOLD_SHADOW_MEMORY_INVALID",admission=admission,reason=str(error),run_root=run_root)
    if private_pool_path is None:
        private_pool_path = private_primary_pool_path(StorageSettings.from_env())
    if not private_pool_path.is_file():
        return _bounded_result("HOLD_CANONICAL_PRIVATE_POOL_UNAVAILABLE", admission=admission, reason=f"Canonical private primary pool unavailable: {private_pool_path}", run_root=run_root)
    private_pool = load_private_primary_pool(private_pool_path) or {}
    try:
        frozen = _frozen_pool_payload(private_pool, admission)
    except ValueError as error:
        return _bounded_result("HOLD_CANONICAL_PRIVATE_POOL_IDENTITY_MISMATCH", admission=admission, reason=str(error), run_root=run_root)
    if not run_root.exists():
        run_root.mkdir(parents=True, exist_ok=False)
    frozen_path = run_root / "frozen-primary-evidence-pool.json"
    frozen_memory_path=run_root/"shadow-dead-end-memory.json"
    frozen_path.write_text(json.dumps(frozen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    frozen_memory_path.write_text(json.dumps(frozen_memory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    try:
        qualification = write_shadow_run_qualification(
            run_root=run_root,
            pool_path=frozen_path,
            memory_path=frozen_memory_path,
            project_root=project_root,
            require_clean_control=require_clean_control,
            control_files=control_files,
        )
    except Exception:
        frozen_path.unlink(missing_ok=True)
        frozen_memory_path.unlink(missing_ok=True)
        try:
            run_root.rmdir()
        except OSError:
            pass
        raise
    return _bounded_result(
        HANDOFF_STATUS,
        admission=admission,
        reason="Canonical private Primary and shadow dead-end memory were frozen into the run root and a schema-bound zero-authority qualification receipt was created. Provider execution remains unauthorized by this launcher.",
        run_root=run_root,
        frozen_pool_created=True,
        frozen_memory_created=True,
        qualification_created=True,
        source_generated_at=qualification.get("source_generated_at"),
        source_set_sha256=qualification.get("source_set_sha256"),
        source_primary_content_sha256=qualification.get("source_primary_content_sha256"),
        source_pool_sha256=qualification.get("source_pool_sha256"),
        frozen_pool_sha256=qualification.get("frozen_pool_sha256"),
        memory_sha256=qualification.get("memory_sha256"),
        control_snapshot_sha256=qualification.get("control_snapshot_sha256"),
        stage_runner_required_schema=qualification.get("stage_runner_required_schema"),
        main_commit=qualification.get("main_commit"),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--private-pool", type=Path)
    parser.add_argument("--memory", type=Path, default=DEFAULT_SHADOW_MEMORY_PATH)
    args = parser.parse_args()
    state = prepare_shadow_run(run_root=args.run_root, private_pool_path=args.private_pool, memory_path=args.memory)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
