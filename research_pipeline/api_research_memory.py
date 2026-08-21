from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .api_memory_store import (
    DATABASE_FILENAME,
    SCHEMA_VERSION,
    bind_run_artifact,
    connect,
    database_path,
    insert_run_stub,
    persistent_root,
    stage_from_name,
    store_artifact,
    upsert_call,
)
from .config import PROJECT_ROOT, StorageSettings


POLICY: dict[str, Any] = {
    "append_only_event_log": True,
    "content_addressed_artifact_store": True,
    "raw_output_archived_before_parse": True,
    "database_is_provenance_and_retrieval_memory_not_scientific_authority": True,
    "api_output_cannot_authorize_problem_gate_paper_method_experiment_p0_or_gpu": True,
    "execution_parse_transport_failures_have_zero_belief_authority": True,
    "research_memory_graph_projection_is_read_only": True,
    "same_run_manifest_conflict_fails_closed": True,
    "request_fingerprint_and_raw_sha_enable_zero_provider_replay": True,
}


def should_auto_record(run_root: Path) -> bool:
    explicit = os.getenv("RESEARCH_API_MEMORY_AUTO_RECORD", "").strip().lower()
    if explicit in {"0", "false", "no", "off"}:
        return False
    if explicit in {"1", "true", "yes", "on"}:
        return True
    try:
        resolved = Path(run_root).resolve()
        local_runs = (PROJECT_ROOT / "generated" / "research-data" / "runs").resolve()
        canonical_runs = (persistent_root() / "runs").resolve()
        return resolved.is_relative_to(local_runs) or resolved.is_relative_to(canonical_runs)
    except (OSError, RuntimeError, ValueError):
        return False


def record_raw_api_output(
    *,
    run_root: Path,
    stage: str,
    raw_path: Path,
    resolved_model: str = "",
    requested_model: str = "",
    request_fingerprint: str = "",
    prompt_sha256: str = "",
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    if not should_auto_record(run_root) and root is None:
        return {"status": "SKIPPED_NONCANONICAL_RUN_ROOT", "scientific_authority": False}
    run_id = Path(run_root).name
    db = database_path(storage, root=root)
    with connect(db) as connection:
        insert_run_stub(connection, run_id, metadata={"incremental": True})
        raw_sha, size_bytes, relpath = store_artifact(
            connection, Path(raw_path), storage=storage, root=root
        )
        bind_run_artifact(connection,run_id=run_id,sha256=raw_sha,role="raw_api_output")
        call_id = upsert_call(
            connection,
            run_id=run_id,
            raw_sha256=raw_sha,
            structured_sha256=None,
            row={
                "stage": stage_from_name(stage),
                "role": stage,
                "requested_model": requested_model,
                "resolved_model": resolved_model,
                "request_fingerprint": request_fingerprint,
                "prompt_sha256": prompt_sha256,
                "outcome_status": "RAW_ARCHIVED_METADATA_PENDING",
                "parse_status": "PENDING",
                "provider_calls_executed": 1,
                "failure_class": "",
                "metadata": {
                    "raw_archived_before_parse": True,
                    "artifact_storage_relpath": relpath,
                    "size_bytes": size_bytes,
                },
            },
            event_type="RAW_ARCHIVED",
        )
        connection.execute(
            """
            UPDATE runs SET
              artifact_count=(SELECT COUNT(DISTINCT sha256) FROM run_artifacts WHERE run_id=?),
              call_count=(SELECT COUNT(*) FROM api_calls WHERE run_id=?)
            WHERE run_id=?
            """,
            (run_id, run_id, run_id),
        )
    return {
        "status": "RAW_ARCHIVED",
        "run_id": run_id,
        "call_id": call_id,
        "raw_sha256": raw_sha,
        "scientific_authority": False,
    }


def record_provider_failure(
    *,
    run_root: Path,
    stage: str,
    payload: dict[str, Any],
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    if not should_auto_record(run_root) and root is None:
        return {"status": "SKIPPED_NONCANONICAL_RUN_ROOT", "scientific_authority": False}
    run_id = Path(run_root).name
    db = database_path(storage, root=root)
    with connect(db) as connection:
        insert_run_stub(connection, run_id, metadata={"incremental": True})
        call_id = upsert_call(
            connection,
            run_id=run_id,
            raw_sha256=None,
            structured_sha256=None,
            row={
                "stage": stage_from_name(stage),
                "role": stage,
                "requested_model": str(payload.get("requested_model") or ""),
                "resolved_model": "",
                "request_fingerprint": str(
                    payload.get("request_fingerprint")
                    or payload.get("error_fingerprint")
                    or ""
                ),
                "prompt_sha256": str(payload.get("prompt_sha256") or ""),
                "outcome_status": str(
                    payload.get("status") or "PROVIDER_ERROR_ZERO_AUTHORITY"
                ),
                "parse_status": "NO_RESPONSE",
                "provider_calls_executed": 1,
                "failure_class": "execution",
                "metadata": {
                    "error_fingerprint": str(payload.get("error_fingerprint") or "")
                },
            },
            event_type="PROVIDER_FAILURE",
        )
    return {
        "status": "PROVIDER_FAILURE_ARCHIVED",
        "run_id": run_id,
        "call_id": call_id,
        "scientific_authority": False,
    }


def _empty_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "API_RESEARCH_MEMORY_NOT_INITIALIZED",
        "policy": dict(POLICY),
        "summary": {
            "runs": 0,
            "calls": 0,
            "artifacts": 0,
            "artifact_bytes": 0,
            "research_objects": 0,
            "lineage_edges": 0,
            "execution_failures": 0,
            "preflight_candidates": 0,
            "raw_replayable_calls": 0,
            "fully_replay_addressed_calls": 0,
            "historical_fingerprint_gaps": 0,
        },
        "recent_runs": [],
        "graph_projection": {"candidates": [], "scientific_authority": False},
        "scientific_authority": False,
    }


def build_api_research_memory_state(
    *,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    db = database_path(storage, root=root)
    if not db.is_file():
        return _empty_state()
    with connect(db) as connection:
        def count(table: str) -> int:
            return int(
                connection.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            )

        summary = {
            "runs": count("runs"),
            "calls": count("api_calls"),
            "artifacts": count("artifacts"),
            "artifact_bytes": int(
                connection.execute(
                    "SELECT COALESCE(SUM(size_bytes),0) AS n FROM artifacts"
                ).fetchone()["n"]
            ),
            "research_objects": count("research_objects"),
            "lineage_edges": count("lineage_edges"),
            "execution_failures": int(
                connection.execute(
                    "SELECT COUNT(*) AS n FROM api_calls WHERE failure_class='execution'"
                ).fetchone()["n"]
            ),
            "preflight_candidates": int(
                connection.execute(
                    """
                    SELECT COUNT(*) AS n FROM research_objects
                    WHERE object_type='preflight_contract'
                    """
                ).fetchone()["n"]
            ),
            "raw_replayable_calls": int(connection.execute(
                "SELECT COUNT(*) AS n FROM api_calls WHERE length(raw_sha256)=64"
            ).fetchone()["n"]),
            "fully_replay_addressed_calls": int(connection.execute(
                "SELECT COUNT(*) AS n FROM api_calls WHERE length(raw_sha256)=64 AND length(request_fingerprint)=64"
            ).fetchone()["n"]),
        }
        summary["historical_fingerprint_gaps"] = summary["raw_replayable_calls"] - summary["fully_replay_addressed_calls"]
        recent_runs = [
            {
                "run_id": row["run_id"],
                "status": row["status"],
                "calls": row["call_count"],
                "objects": row["object_count"],
                "manifest_sha256": row["manifest_sha256"],
                "scientific_authority": False,
            }
            for row in connection.execute(
                """
                SELECT run_id,status,call_count,object_count,manifest_sha256
                FROM runs ORDER BY imported_at DESC,run_id DESC LIMIT 8
                """
            )
        ]
        candidates = []
        for row in connection.execute(
            """
            SELECT run_id,object_id,parent_object_id,title,disposition,payload_json
            FROM research_objects
            WHERE object_type='preflight_contract'
            ORDER BY run_id,object_id
            """
        ):
            payload = json.loads(row["payload_json"])
            body = payload.get("payload") if isinstance(payload, dict) else {}
            candidates.append(
                {
                    "candidate_id": row["object_id"],
                    "title": row["title"],
                    "status": row["disposition"],
                    "paper_state": row["disposition"],
                    "scientific_object": str(
                        (body or {}).get("scientific_object") or row["object_id"]
                    ),
                    "problem_contract": str(
                        (body or {}).get("reproduction_target")
                        or (body or {}).get("frozen_irreducible_object")
                        or ""
                    ),
                    "source_refs": list((body or {}).get("source_refs") or []),
                    "provenance": {
                        "provenance_status": "API_RESEARCH_MEMORY_BOUND",
                        "source_run_id": row["run_id"],
                        "parent_object_id": row["parent_object_id"],
                    },
                    "downstream_authorization_blocked": True,
                    "scientific_authority": False,
                    "authority": {
                        "problem_gate": False,
                        "paper_design": False,
                        "method": False,
                        "experiment": False,
                        "p0": False,
                        "gpu": False,
                    },
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "API_RESEARCH_MEMORY_READY",
        "database_uri": f"research-data://indexes/{DATABASE_FILENAME}",
        "policy": dict(POLICY),
        "summary": summary,
        "recent_runs": recent_runs,
        "graph_projection": {"candidates": candidates, "scientific_authority": False},
        "scientific_authority": False,
    }


def lint_api_research_memory(
    *,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    db = database_path(storage, root=root)
    errors: list[dict[str, Any]] = []
    if not db.is_file():
        errors.append({"code": "database-missing"})
    else:
        with connect(db) as connection:
            integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
            if integrity != "ok":
                errors.append({"code": "sqlite-integrity", "detail": integrity})
            for table in (
                "runs",
                "run_artifacts",
                "api_calls",
                "api_call_events",
                "research_objects",
                "lineage_edges",
            ):
                leaked = int(
                    connection.execute(
                        f"SELECT COUNT(*) AS n FROM {table} WHERE scientific_authority != 0"
                    ).fetchone()["n"]
                )
                if leaked:
                    errors.append(
                        {
                            "code": "scientific-authority-leak",
                            "table": table,
                            "rows": leaked,
                        }
                    )
            belief = int(
                connection.execute(
                    "SELECT COUNT(*) AS n FROM api_calls WHERE belief_authority != 0"
                ).fetchone()["n"]
            )
            if belief:
                errors.append({"code": "belief-authority-leak", "rows": belief})
            missing = int(
                connection.execute(
                    """
                    SELECT COUNT(*) AS n FROM api_calls c
                    LEFT JOIN artifacts a ON a.sha256=c.raw_sha256
                    WHERE c.raw_sha256 IS NOT NULL AND a.sha256 IS NULL
                    """
                ).fetchone()["n"]
            )
            if missing:
                errors.append({"code": "missing-raw-artifact-binding", "rows": missing})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {"errors": len(errors)},
        "scientific_authority": False,
    }
