from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings, resolve_experiment_data_root

SCHEMA_VERSION = "1.0"
DATABASE_FILENAME = "api-research-memory.sqlite3"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_json(value: Any) -> str:
    return sha_bytes(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8"))


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def persistent_root(storage: StorageSettings | None = None) -> Path:
    return resolve_experiment_data_root(storage or StorageSettings.from_env())


def database_path(storage: StorageSettings | None = None, *, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else persistent_root(storage)
    return base / "indexes" / DATABASE_FILENAME


def artifact_root(storage: StorageSettings | None = None, *, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else persistent_root(storage)
    return base / "artifacts" / "api-research-memory" / "sha256"


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = FULL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_meta (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            manifest_sha256 TEXT NOT NULL,
            transaction_kind TEXT NOT NULL,
            status TEXT NOT NULL,
            control_snapshot_sha256 TEXT NOT NULL,
            frozen_pool_sha256 TEXT NOT NULL,
            artifact_set_sha256 TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            artifact_count INTEGER NOT NULL,
            call_count INTEGER NOT NULL,
            object_count INTEGER NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0),
            metadata_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS artifacts (
            sha256 TEXT PRIMARY KEY,
            size_bytes INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            storage_relpath TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0)
        );
        CREATE TABLE IF NOT EXISTS run_artifacts (
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            sha256 TEXT NOT NULL REFERENCES artifacts(sha256),
            role TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0),
            PRIMARY KEY(run_id, sha256, role)
        );
        CREATE TABLE IF NOT EXISTS api_calls (
            call_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            stage TEXT NOT NULL,
            role TEXT NOT NULL,
            part INTEGER,
            requested_model TEXT NOT NULL,
            resolved_model TEXT NOT NULL,
            request_fingerprint TEXT NOT NULL,
            prompt_sha256 TEXT NOT NULL,
            raw_sha256 TEXT REFERENCES artifacts(sha256),
            structured_sha256 TEXT REFERENCES artifacts(sha256),
            outcome_status TEXT NOT NULL,
            parse_status TEXT NOT NULL,
            provider_calls_executed INTEGER NOT NULL,
            failure_class TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0),
            belief_authority INTEGER NOT NULL DEFAULT 0 CHECK(belief_authority = 0),
            metadata_json TEXT NOT NULL,
            UNIQUE(run_id, stage, role, raw_sha256)
        );
        CREATE TABLE IF NOT EXISTS api_call_events (
            event_id TEXT PRIMARY KEY,
            call_id TEXT NOT NULL REFERENCES api_calls(call_id),
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            event_type TEXT NOT NULL,
            event_at TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0),
            belief_authority INTEGER NOT NULL DEFAULT 0 CHECK(belief_authority = 0)
        );
        CREATE TABLE IF NOT EXISTS research_objects (
            object_key TEXT PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            object_type TEXT NOT NULL,
            object_id TEXT NOT NULL,
            parent_object_id TEXT NOT NULL,
            stage TEXT NOT NULL,
            title TEXT NOT NULL,
            disposition TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0),
            UNIQUE(run_id, object_type, object_id, stage)
        );
        CREATE TABLE IF NOT EXISTS lineage_edges (
            edge_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES runs(run_id),
            source_object_id TEXT NOT NULL,
            target_object_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            scientific_authority INTEGER NOT NULL DEFAULT 0 CHECK(scientific_authority = 0)
        );
        CREATE INDEX IF NOT EXISTS idx_calls_run_stage ON api_calls(run_id, stage);
        CREATE INDEX IF NOT EXISTS idx_calls_request ON api_calls(request_fingerprint);
        CREATE INDEX IF NOT EXISTS idx_calls_raw ON api_calls(raw_sha256);
        CREATE INDEX IF NOT EXISTS idx_objects_run_stage ON research_objects(run_id, stage);
        CREATE INDEX IF NOT EXISTS idx_objects_identity ON research_objects(object_id);
        CREATE INDEX IF NOT EXISTS idx_edges_run_source ON lineage_edges(run_id, source_object_id);
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO schema_meta(key,value) VALUES('schema_version',?)",
        (SCHEMA_VERSION,),
    )
    row = connection.execute(
        "SELECT value FROM schema_meta WHERE key='schema_version'"
    ).fetchone()
    if row is None or str(row["value"]) != SCHEMA_VERSION:
        raise RuntimeError("api research memory schema version mismatch")
    return connection


def store_artifact(
    connection: sqlite3.Connection,
    source: Path,
    *,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> tuple[str, int, str]:
    data = source.read_bytes()
    digest = sha_bytes(data)
    base = artifact_root(storage, root=root)
    destination = base / digest[:2] / digest
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha_bytes(destination.read_bytes()) != digest:
            raise RuntimeError(f"content-addressed artifact conflict: {digest}")
    else:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, destination)
    media_type = "application/json" if source.suffix.lower() == ".json" else "text/plain"
    relpath = str(destination.relative_to(base.parent.parent.parent))
    connection.execute(
        """
        INSERT OR IGNORE INTO artifacts(
          sha256,size_bytes,media_type,storage_relpath,created_at,scientific_authority
        ) VALUES(?,?,?,?,?,0)
        """,
        (digest, len(data), media_type, relpath, now_utc()),
    )
    return digest, len(data), relpath


def bind_run_artifact(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    sha256: str,
    role: str,
) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO run_artifacts(
          run_id,sha256,role,scientific_authority
        ) VALUES(?,?,?,0)
        """,
        (run_id, sha256, role),
    )


def insert_run_stub(
    connection: sqlite3.Connection,
    run_id: str,
    *,
    manifest_sha256: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    existing = connection.execute(
        "SELECT manifest_sha256 FROM runs WHERE run_id=?", (run_id,)
    ).fetchone()
    if existing is not None:
        current = str(existing["manifest_sha256"])
        if manifest_sha256 and current and current != manifest_sha256:
            raise RuntimeError(f"run manifest conflict for {run_id}")
        return
    connection.execute(
        """
        INSERT INTO runs(
          run_id,manifest_sha256,transaction_kind,status,
          control_snapshot_sha256,frozen_pool_sha256,artifact_set_sha256,
          imported_at,artifact_count,call_count,object_count,
          scientific_authority,metadata_json
        ) VALUES(?,?,'shadow_api_search','INCREMENTAL_RAW_ARCHIVE',
                 '','','',?,0,0,0,0,?)
        """,
        (run_id, manifest_sha256, now_utc(), safe_json(metadata or {})),
    )


def insert_event(
    connection: sqlite3.Connection,
    *,
    call_id: str,
    run_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    payload = {**payload, "scientific_authority": False, "belief_authority": False}
    payload_sha = sha_json(payload)
    event_id = sha_json({
        "call_id": call_id, "event_type": event_type, "payload_sha256": payload_sha
    })
    connection.execute(
        """
        INSERT OR IGNORE INTO api_call_events(
          event_id,call_id,run_id,event_type,event_at,payload_sha256,payload_json,
          scientific_authority,belief_authority
        ) VALUES(?,?,?,?,?,?,?,0,0)
        """,
        (event_id, call_id, run_id, event_type, now_utc(), payload_sha, safe_json(payload)),
    )


def upsert_call(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    raw_sha256: str | None,
    structured_sha256: str | None,
    row: dict[str, Any],
    event_type: str,
) -> str:
    identity = {
        "run_id": run_id,
        "stage": str(row.get("stage") or "unknown"),
        "role": str(row.get("role") or row.get("stage") or "unknown"),
        "raw_sha256": str(raw_sha256 or ""),
    }
    call_id = sha_json(identity)
    connection.execute(
        """
        INSERT OR IGNORE INTO api_calls(
          call_id,run_id,stage,role,part,requested_model,resolved_model,
          request_fingerprint,prompt_sha256,raw_sha256,structured_sha256,
          outcome_status,parse_status,provider_calls_executed,failure_class,
          imported_at,scientific_authority,belief_authority,metadata_json
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0,?)
        """,
        (
            call_id, run_id, identity["stage"], identity["role"],
            row.get("part") if isinstance(row.get("part"), int) else None,
            str(row.get("requested_model") or ""), str(row.get("resolved_model") or ""),
            str(row.get("request_fingerprint") or ""), str(row.get("prompt_sha256") or ""),
            raw_sha256, structured_sha256, str(row.get("outcome_status") or "UNKNOWN"),
            str(row.get("parse_status") or "UNKNOWN"),
            int(row.get("provider_calls_executed", 1) or 0),
            str(row.get("failure_class") or ""), now_utc(),
            safe_json(row.get("metadata") or {}),
        ),
    )
    existing = connection.execute(
        "SELECT * FROM api_calls WHERE call_id=?", (call_id,)
    ).fetchone()
    if existing is None:
        raise RuntimeError("api call projection insert failed")
    metadata = {**json.loads(existing["metadata_json"]), **(row.get("metadata") or {})}
    connection.execute(
        """
        UPDATE api_calls SET
          requested_model=?,resolved_model=?,request_fingerprint=?,
          prompt_sha256=?,structured_sha256=?,outcome_status=?,parse_status=?,
          provider_calls_executed=?,failure_class=?,metadata_json=?
        WHERE call_id=?
        """,
        (
            str(row.get("requested_model") or existing["requested_model"]),
            str(row.get("resolved_model") or existing["resolved_model"]),
            str(row.get("request_fingerprint") or existing["request_fingerprint"]),
            str(row.get("prompt_sha256") or existing["prompt_sha256"]),
            structured_sha256 or existing["structured_sha256"],
            str(row.get("outcome_status") or existing["outcome_status"]),
            str(row.get("parse_status") or existing["parse_status"]),
            int(row.get("provider_calls_executed", existing["provider_calls_executed"]) or 0),
            str(row.get("failure_class") or existing["failure_class"]),
            safe_json(metadata), call_id,
        ),
    )
    insert_event(
        connection, call_id=call_id, run_id=run_id, event_type=event_type,
        payload={
            "raw_sha256": raw_sha256 or "",
            "structured_sha256": structured_sha256 or "",
            **{key: row.get(key) for key in (
                "stage", "role", "requested_model", "resolved_model",
                "request_fingerprint", "prompt_sha256", "outcome_status",
                "parse_status", "provider_calls_executed", "failure_class",
            )},
        },
    )
    return call_id


def stage_from_name(name: str) -> str:
    stem = Path(name).stem
    if stem.startswith("error-"):
        stem = stem[6:]
    if stem.startswith("repair-"):
        stem = stem[7:]
    for prefix, stage in (
        ("evidence-design", "bounded_evidence_design"),
        ("evidence-review", "independent_evidence_review"),
        ("evidence-recompile", "evidence_recompile"),
        ("formulate", "formulation"),
        ("review", "semantic_review"),
        ("evolve-g1", "evolution_g1"),
        ("evolve-g2", "evolution_g2"),
        ("expand", "expansion"),
    ):
        if stem.startswith(prefix):
            return stage
    return stem.split("-p", 1)[0].replace("-", "_")
