from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from .api_memory_store import (
    DATABASE_FILENAME,
    SCHEMA_VERSION,
    bind_run_artifact,
    connect,
    database_path,
    insert_memory_consumption,
    insert_memory_query,
    insert_run_stub,
    invalidate_run,
    memory_instance_id,
    persistent_root,
    sha_json,
    stage_from_name,
    store_artifact,
    upsert_call,
    upsert_scientific_identity,
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
    "retrieval_is_search_context_not_scientific_verdict": True,
    "memory_consumption_is_receipted_before_effectiveness_attribution": True,
    "cross_run_identity_is_deterministic_exact_contract_not_semantic_authority": True,
    "canonical_run_memory_missing_fails_closed": True,
    "query_only_development_corrections_are_append_only_invalidations_not_deletes": True,
}

IDENTITY_SIGNATURE_VERSION = "api-scientific-object-v1"
API_MEMORY_PURPOSES = {
    "IDEA_DISCOVERY",
    "FORMULATION",
    "SEMANTIC_REVIEW",
    "EXPERIMENT_DESIGN",
    "PAPER_META_REVIEW",
}
API_MEMORY_VARIANTS = {"relevant", "random", "none"}

_PURPOSE_TYPE_PRIOR: dict[str, dict[str, float]] = {
    "IDEA_DISCOVERY": {
        "problem_seed": 1.0,
        "evolved_branch": 0.6,
        "candidate": 1.2,
        "candidate_review": 1.3,
        "evidence_contract": 0.7,
        "preflight_contract": 0.9,
    },
    "FORMULATION": {
        "problem_seed": 0.5,
        "evolved_branch": 0.7,
        "candidate": 1.2,
        "candidate_review": 1.4,
        "evidence_contract": 0.9,
        "preflight_contract": 1.0,
    },
    "SEMANTIC_REVIEW": {
        "candidate": 1.0,
        "candidate_review": 1.5,
        "evidence_contract": 1.0,
        "preflight_contract": 1.0,
    },
    "EXPERIMENT_DESIGN": {
        "candidate": 0.7,
        "candidate_review": 1.0,
        "evidence_contract": 1.5,
        "preflight_contract": 1.4,
    },
    "PAPER_META_REVIEW": {
        "candidate_review": 1.0,
        "evidence_contract": 1.4,
        "preflight_contract": 1.5,
    },
}


def _compact_text(value: Any, *, limit: int = 1800) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    else:
        text = str(value or "")
    text = " ".join(text.split())
    return text[:limit]


def _normalized_identity_text(value: Any) -> str:
    text = _compact_text(value, limit=2400).lower()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _unwrap_object_payload(payload: dict[str, Any]) -> dict[str, Any]:
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    body = dict(body) if isinstance(body, dict) else {}
    nested = body.get("candidate")
    if isinstance(nested, dict):
        merged = dict(nested)
        merged.update({key: value for key, value in body.items() if key != "candidate"})
        body = merged
    return body


def _first_text(body: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = body.get(key)
        text = _compact_text(value)
        if text:
            return text
    return ""


def scientific_identity_components(
    *, object_type: str, title: str, payload: dict[str, Any]
) -> dict[str, str]:
    body = _unwrap_object_payload(payload)
    components = {
        "scientific_object": _first_text(
            body,
            "scientific_object",
            "frozen_irreducible_object",
            "irreducible_object",
            "problem_seed",
            "reproduction_target",
        )
        or title,
        "mechanism": _first_text(
            body,
            "mechanism",
            "agent_specific_constraint",
            "structural_signature",
            "composition_rule",
        ),
        "claim_type": _first_text(body, "claim_type", "discovery_lane") or object_type,
        "prediction": _first_text(
            body, "exact_prediction", "frozen_exact_prediction", "reproduction_target"
        ),
        "same_information_baseline": _first_text(
            body,
            "strongest_same_information_baseline",
            "frozen_same_information_baseline",
            "matched_mature_theory",
        ),
        "independent_truth": _first_text(body, "independent_truth"),
    }
    return {key: _normalized_identity_text(value) for key, value in components.items()}


def scientific_object_signature(
    *, object_type: str, title: str, payload: dict[str, Any]
) -> tuple[str, dict[str, str]]:
    components = scientific_identity_components(
        object_type=object_type, title=title, payload=payload
    )
    return sha_json(
        {"version": IDENTITY_SIGNATURE_VERSION, "components": components}
    ), components


def _ensure_scientific_identity_index(connection: Any) -> int:
    inserted = 0
    for row in connection.execute(
        """
        SELECT o.object_key,o.object_type,o.title,o.payload_json
        FROM research_objects o
        LEFT JOIN scientific_identities i ON i.object_key=o.object_key
        WHERE i.object_key IS NULL
        ORDER BY o.run_id,o.stage,o.object_id
        """
    ):
        try:
            payload = json.loads(row["payload_json"])
        except (TypeError, json.JSONDecodeError):
            payload = {}
        signature, components = scientific_object_signature(
            object_type=str(row["object_type"]),
            title=str(row["title"]),
            payload=payload if isinstance(payload, dict) else {},
        )
        upsert_scientific_identity(
            connection,
            object_key=str(row["object_key"]),
            scientific_signature=signature,
            signature_version=IDENTITY_SIGNATURE_VERSION,
            components=components,
        )
        inserted += 1
    return inserted


def _token_set(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[\w]+", _compact_text(value, limit=12000).lower(), flags=re.UNICODE)
        if len(token) > 1
    }


def _memory_digest(row: dict[str, Any]) -> str:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    body = _unwrap_object_payload(payload)
    fields = [
        ("problem", _first_text(body, "problem_seed", "scientific_tension", "irreducible_object", "frozen_irreducible_object", "reproduction_target")),
        ("prediction", _first_text(body, "exact_prediction", "frozen_exact_prediction", "reproduction_target")),
        ("baseline", _first_text(body, "strongest_same_information_baseline", "frozen_same_information_baseline", "matched_mature_theory")),
        ("truth", _first_text(body, "independent_truth")),
        ("falsifier", _first_text(body, "cheapest_problem_falsifier", "cheapest_scientific_falsifier")),
        ("reason", _first_text(body, "reason", "required_revision", "reduction_class")),
        ("blockers", _first_text(body, "blockers")),
    ]
    parts = [
        f"id={row.get('object_id','')}",
        f"type={row.get('object_type','')}",
        f"stage={row.get('stage','')}",
        f"disposition={row.get('disposition','')}",
        f"scientific_signature={row.get('scientific_signature','')}",
        f"title={_compact_text(row.get('title'), limit=420)}",
    ]
    parts.extend(f"{label}={_compact_text(text, limit=900)}" for label, text in fields if text)
    return "[API_RESEARCH_MEMORY] " + " | ".join(parts)


def _empty_query_pack(
    *, purpose: str, stage: str, variant: str, status: str, context_sha256: str = ""
) -> dict[str, Any]:
    core = {
        "schema_version": "2.2",
        "purpose": purpose,
        "stage": stage,
        "variant": variant,
        "memory_instance_id": "",
        "context_sha256": context_sha256,
        "selected_memory_ids": [],
        "selected_object_keys": [],
        "selected_scientific_signatures": [],
        "text": "",
        "policy": {
            "memory_is_search_context_not_scientific_verdict": True,
            "past_failure_is_not_automatic_veto": True,
            "past_success_is_not_automatic_generalization": True,
            "downstream_scientific_gates_unchanged": True,
        },
        "scientific_authority": False,
    }
    core["query_pack_sha256"] = sha_json(core)
    core["query_id"] = ""
    core["status"] = status
    core["summary"] = {"selected": 0, "characters": 0, "available": 0}
    return core


def compile_api_memory_query_pack(
    *,
    purpose: str,
    context: Any,
    run_id: str = "",
    stage: str = "",
    variant: str = "relevant",
    max_items: int = 16,
    max_chars: int = 6000,
    required: bool = False,
    record_query: bool = True,
    enabled: bool = True,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    purpose = str(purpose or "").strip().upper()
    if purpose not in API_MEMORY_PURPOSES:
        raise ValueError(f"unsupported API research memory purpose: {purpose}")
    variant = str(variant or "relevant").strip().lower()
    if variant not in API_MEMORY_VARIANTS:
        raise ValueError(f"unsupported API research memory variant: {variant}")
    max_items = max(0, int(max_items))
    max_chars = max(0, int(max_chars))
    context_sha = sha_json(context if context is not None else {})
    if not enabled:
        return _empty_query_pack(
            purpose=purpose,
            stage=stage,
            variant=variant,
            status="API_MEMORY_DISABLED_NONCANONICAL",
            context_sha256=context_sha,
        )
    db = database_path(storage, root=root)
    if not db.is_file():
        if required:
            raise RuntimeError(f"canonical API research memory missing: {db}")
        return _empty_query_pack(
            purpose=purpose,
            stage=stage,
            variant=variant,
            status="API_MEMORY_UNAVAILABLE_OPTIONAL",
            context_sha256=context_sha,
        )
    with connect(db) as connection:
        _ensure_scientific_identity_index(connection)
        instance = memory_instance_id(connection)
        rows: list[dict[str, Any]] = []
        query = """
            SELECT o.object_key,o.run_id,o.object_type,o.object_id,o.stage,o.title,
                   o.disposition,o.payload_json,i.scientific_signature
            FROM research_objects o
            JOIN scientific_identities i ON i.object_key=o.object_key
            LEFT JOIN run_invalidations ri ON ri.run_id=o.run_id
            WHERE ri.run_id IS NULL
        """
        params: tuple[Any, ...] = ()
        if run_id:
            query += " AND o.run_id != ?"
            params = (run_id,)
        query += " ORDER BY o.run_id,o.stage,o.object_id"
        context_tokens = _token_set(context)
        priors = _PURPOSE_TYPE_PRIOR.get(purpose, {})
        for raw in connection.execute(query, params):
            try:
                payload = json.loads(raw["payload_json"])
            except (TypeError, json.JSONDecodeError):
                payload = {}
            row = dict(raw)
            row["payload"] = payload if isinstance(payload, dict) else {}
            digest = _memory_digest(row)
            memory_tokens = _token_set(digest)
            overlap = len(context_tokens & memory_tokens)
            union = len(context_tokens | memory_tokens)
            lexical = overlap / union if union else 0.0
            disposition = str(row.get("disposition") or "").upper()
            disposition_prior = 0.0
            if "PREFLIGHT" in disposition or "CLEAR" in disposition:
                disposition_prior += 0.6
            if "REDUCTION" in disposition or "REJECT" in disposition or "BLOCK" in disposition:
                disposition_prior += 0.5
            row["digest"] = digest
            row["score"] = round(
                lexical * 12.0
                + float(priors.get(str(row.get("object_type") or ""), 0.0))
                + disposition_prior,
                6,
            )
            rows.append(row)
        if variant == "none":
            ordered: list[dict[str, Any]] = []
        elif variant == "random":
            ordered = sorted(
                rows,
                key=lambda row: hashlib.sha256(
                    f"{context_sha}:{row['object_key']}".encode("utf-8")
                ).hexdigest(),
            )
        else:
            ordered = sorted(
                rows,
                key=lambda row: (-float(row["score"]), str(row["object_key"])),
            )
        selected: list[dict[str, Any]] = []
        seen_signatures: set[str] = set()
        characters = 0
        for row in ordered:
            signature = str(row.get("scientific_signature") or "")
            if signature and signature in seen_signatures:
                continue
            digest = str(row.get("digest") or "")
            additional = len(digest) + (2 if selected else 0)
            if selected and characters + additional > max_chars:
                continue
            if not selected and additional > max_chars:
                digest = digest[:max_chars]
                additional = len(digest)
            if max_chars <= 0 or max_items <= 0:
                break
            copy = dict(row)
            copy["digest"] = digest
            selected.append(copy)
            characters += additional
            if signature:
                seen_signatures.add(signature)
            if len(selected) >= max_items:
                break
        text = "\n\n".join(str(row["digest"]) for row in selected)
        selected_keys = [str(row["object_key"]) for row in selected]
        signatures = [str(row["scientific_signature"]) for row in selected]
        memory_ids = [f"api:{key[:16]}" for key in selected_keys]
        core = {
            "schema_version": "2.2",
            "purpose": purpose,
            "stage": stage,
            "variant": variant,
            "memory_instance_id": instance,
            "context_sha256": context_sha,
            "selected_memory_ids": memory_ids,
            "selected_object_keys": selected_keys,
            "selected_scientific_signatures": signatures,
            "text": text,
            "policy": {
                "memory_is_search_context_not_scientific_verdict": True,
                "past_failure_is_not_automatic_veto": True,
                "past_success_is_not_automatic_generalization": True,
                "cross_run_identity_is_exact_contract_only": True,
                "downstream_scientific_gates_unchanged": True,
            },
            "scientific_authority": False,
        }
        pack_sha = sha_json(core)
        query_id = ""
        if run_id and record_query:
            query_id = insert_memory_query(
                connection,
                run_id=run_id,
                purpose=purpose,
                stage=stage,
                variant=variant,
                context_sha256=context_sha,
                query_pack_sha256=pack_sha,
                selected_object_keys=selected_keys,
                selected_signatures=signatures,
            )
        core["query_pack_sha256"] = pack_sha
        core["query_id"] = query_id
        core["status"] = "API_MEMORY_QUERY_COMPILED"
        core["summary"] = {
            "selected": len(selected),
            "characters": len(text),
            "available": len(rows),
            "unique_scientific_signatures": len({str(row.get("scientific_signature") or "") for row in rows}),
        }
        return core


def record_api_memory_consumption(
    *,
    run_id: str,
    stage: str,
    pack: dict[str, Any],
    raw_sha256: str,
    output_object_ids: list[str],
    outcome_status: str = "GENERATED",
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    query_id = str(pack.get("query_id") or "")
    if not query_id:
        return {"status": "SKIPPED_NO_API_MEMORY_QUERY", "scientific_authority": False}
    db = database_path(storage, root=root)
    if not db.is_file():
        raise RuntimeError(f"API research memory disappeared after query: {db}")
    with connect(db) as connection:
        consumption_id = insert_memory_consumption(
            connection,
            query_id=query_id,
            run_id=run_id,
            stage=stage,
            raw_sha256=str(raw_sha256 or ""),
            output_object_ids=[str(value) for value in output_object_ids if str(value)],
            outcome_status=str(outcome_status or "GENERATED"),
        )
    return {
        "status": "API_MEMORY_CONSUMPTION_RECORDED",
        "query_id": query_id,
        "consumption_id": consumption_id,
        "scientific_authority": False,
    }


def invalidate_query_only_memory_run(
    *,
    run_id: str,
    reason: str,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    """Append an invalidation for a query-only development stub.

    This deliberately cannot invalidate a run that has provider calls, research
    objects, or persisted artifacts. Scientific history is never editable
    through this maintenance path.
    """
    db = database_path(storage, root=root)
    if not db.is_file():
        raise RuntimeError(f"API research memory missing: {db}")
    with connect(db) as connection:
        row = connection.execute(
            "SELECT run_id,call_count,object_count,artifact_count,metadata_json FROM runs WHERE run_id=?",
            (str(run_id),),
        ).fetchone()
        if row is None:
            raise ValueError(f"unknown API memory run: {run_id}")
        try:
            metadata = json.loads(row["metadata_json"])
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        if any(int(row[key] or 0) != 0 for key in ("call_count", "object_count", "artifact_count")):
            raise ValueError(f"cannot invalidate nonempty research run: {run_id}")
        if not isinstance(metadata, dict) or metadata.get("memory_query") is not True:
            raise ValueError(f"run is not a query-only memory stub: {run_id}")
        invalidate_run(connection, run_id=str(run_id), reason=str(reason))
    return {
        "status": "QUERY_ONLY_RUN_INVALIDATED",
        "run_id": str(run_id),
        "reason": str(reason),
        "scientific_authority": False,
        "belief_authority": False,
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
            "raw_runs": 0,
            "invalidated_runs": 0,
            "calls": 0,
            "artifacts": 0,
            "artifact_bytes": 0,
            "research_objects": 0,
            "lineage_edges": 0,
            "scientific_identities": 0,
            "memory_queries": 0,
            "raw_memory_queries": 0,
            "memory_consumptions": 0,
            "raw_memory_consumptions": 0,
            "execution_failures": 0,
            "preflight_candidates": 0,
            "raw_replayable_calls": 0,
            "fully_replay_addressed_calls": 0,
            "historical_fingerprint_gaps": 0,
        },
        "memory_instance_id": "",
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
        _ensure_scientific_identity_index(connection)
        instance = memory_instance_id(connection)

        def count(table: str) -> int:
            return int(
                connection.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            )

        active_runs = int(connection.execute(
            "SELECT COUNT(*) AS n FROM runs r LEFT JOIN run_invalidations ri ON ri.run_id=r.run_id WHERE ri.run_id IS NULL"
        ).fetchone()["n"])
        invalidated_runs = count("run_invalidations")
        active_queries = int(connection.execute(
            "SELECT COUNT(*) AS n FROM memory_queries q LEFT JOIN run_invalidations ri ON ri.run_id=q.run_id WHERE ri.run_id IS NULL"
        ).fetchone()["n"])
        active_consumptions = int(connection.execute(
            "SELECT COUNT(*) AS n FROM memory_consumptions c LEFT JOIN run_invalidations ri ON ri.run_id=c.run_id WHERE ri.run_id IS NULL"
        ).fetchone()["n"])
        summary = {
            "runs": active_runs,
            "raw_runs": count("runs"),
            "invalidated_runs": invalidated_runs,
            "calls": count("api_calls"),
            "artifacts": count("artifacts"),
            "artifact_bytes": int(
                connection.execute(
                    "SELECT COALESCE(SUM(size_bytes),0) AS n FROM artifacts"
                ).fetchone()["n"]
            ),
            "research_objects": count("research_objects"),
            "lineage_edges": count("lineage_edges"),
            "scientific_identities": count("scientific_identities"),
            "memory_queries": active_queries,
            "raw_memory_queries": count("memory_queries"),
            "memory_consumptions": active_consumptions,
            "raw_memory_consumptions": count("memory_consumptions"),
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
                SELECT r.run_id,r.status,r.call_count,r.object_count,r.manifest_sha256
                FROM runs r
                LEFT JOIN run_invalidations ri ON ri.run_id=r.run_id
                WHERE ri.run_id IS NULL
                ORDER BY r.imported_at DESC,r.run_id DESC LIMIT 8
                """
            )
        ]
        candidates = []
        for row in connection.execute(
            """
            SELECT o.run_id,o.object_id,o.parent_object_id,o.title,o.disposition,
                   o.payload_json,i.scientific_signature
            FROM research_objects o
            JOIN scientific_identities i ON i.object_key=o.object_key
            LEFT JOIN run_invalidations ri ON ri.run_id=o.run_id
            WHERE o.object_type='preflight_contract' AND ri.run_id IS NULL
            ORDER BY o.run_id,o.object_id
            """
        ):
            payload = json.loads(row["payload_json"])
            body = payload.get("payload") if isinstance(payload, dict) else {}
            candidates.append(
                {
                    "candidate_id": f"API::{row['run_id']}::{row['object_id']}",
                    "source_candidate_id": row["object_id"],
                    "scientific_object_signature": row["scientific_signature"],
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
        "memory_instance_id": instance,
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
            _ensure_scientific_identity_index(connection)
            for table in (
                "runs",
                "run_artifacts",
                "api_calls",
                "api_call_events",
                "research_objects",
                "lineage_edges",
                "scientific_identities",
                "run_invalidations",
                "memory_queries",
                "memory_consumptions",
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
            for table in (
                "api_calls",
                "scientific_identities",
                "run_invalidations",
                "memory_queries",
                "memory_consumptions",
            ):
                belief = int(
                    connection.execute(
                        f"SELECT COUNT(*) AS n FROM {table} WHERE belief_authority != 0"
                    ).fetchone()["n"]
                )
                if belief:
                    errors.append({"code": "belief-authority-leak", "table": table, "rows": belief})
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
            identity_gap = int(
                connection.execute(
                    """
                    SELECT COUNT(*) AS n FROM research_objects o
                    LEFT JOIN scientific_identities i ON i.object_key=o.object_key
                    WHERE i.object_key IS NULL
                    """
                ).fetchone()["n"]
            )
            if identity_gap:
                errors.append({"code": "scientific-identity-index-gap", "rows": identity_gap})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {"errors": len(errors)},
        "scientific_authority": False,
    }
