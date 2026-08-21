from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_store import (
    SCHEMA_VERSION,
    bind_run_artifact,
    connect,
    database_path,
    insert_research_object,
    insert_run_stub,
    now_utc,
    safe_json,
    sha_bytes,
    sha_json,
    stage_from_name,
    store_artifact,
    upsert_call,
)
from .api_research_memory import (
    build_api_research_memory_state,
    lint_api_research_memory,
)
from .config import StorageSettings


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def raw_files(run_root: Path) -> dict[str, Path]:
    return {
        sha_bytes(path.read_bytes()): path
        for path in sorted((run_root / "raw").glob("*.txt"))
    }


def call_metadata(
    run_root: Path, raw_by_sha: dict[str, Path]
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted(run_root.glob("*.json")):
        payload = load_json(path)
        raw_sha = str(payload.get("raw_sha256") or "").strip().lower()
        if raw_sha not in raw_by_sha:
            continue
        attempts = [
            row
            for row in payload.get("transport_attempts") or []
            if isinstance(row, dict)
        ]
        attempt = attempts[-1] if attempts else {}
        error_artifact = path.name.startswith("error-")
        candidate = {
            "structured_path": path,
            "stage": stage_from_name(path.name),
            "role": raw_by_sha[raw_sha].stem.rsplit("-", 1)[0],
            "part": payload.get("part"),
            "requested_model": str(
                payload.get("requested_model") or attempt.get("requested_model") or ""
            ),
            "resolved_model": str(
                payload.get("resolved_model") or attempt.get("resolved_model") or ""
            ),
            "request_fingerprint": str(
                payload.get("request_fingerprint")
                or attempt.get("request_fingerprint")
                or ""
            ),
            "prompt_sha256": str(
                payload.get("prompt_sha256") or attempt.get("prompt_sha256") or ""
            ),
            "provider_calls_executed": int(
                payload.get("provider_calls_executed", 1) or 0
            ),
            "outcome_status": str(
                payload.get("status")
                or ("PARSE_ERROR_ZERO_AUTHORITY" if error_artifact else "SUCCESS")
            ),
            "parse_status": (
                "PARSE_ERROR"
                if error_artifact or "PARSE_ERROR" in str(payload.get("status") or "")
                else "PARSED"
            ),
            "failure_class": "execution" if error_artifact else "",
            "metadata": {
                "control_snapshot_sha256": str(
                    payload.get("control_snapshot_sha256") or ""
                ),
                "raw_archived_before_parse": (
                    payload.get("raw_archived_before_parse") is True
                ),
                "raw_replayed_without_provider": (
                    payload.get("raw_replayed_without_provider") is True
                ),
                "transport_fallback_used": (
                    payload.get("transport_fallback_used") is True
                ),
                "source_artifact": path.name,
            },
        }
        prior = rows.get(raw_sha)
        if (
            prior is None
            or prior["parse_status"] != "PARSED"
            and candidate["parse_status"] == "PARSED"
        ):
            rows[raw_sha] = candidate
    for raw_sha, path in raw_by_sha.items():
        if raw_sha in rows:
            continue
        stem = path.stem.rsplit("-", 1)[0]
        rows[raw_sha] = {
            "structured_path": None,
            "stage": stage_from_name(stem),
            "role": stem,
            "part": None,
            "requested_model": "",
            "resolved_model": "",
            "request_fingerprint": "",
            "prompt_sha256": "",
            "provider_calls_executed": 1,
            "outcome_status": "RAW_ARCHIVED_METADATA_PENDING",
            "parse_status": "UNKNOWN",
            "failure_class": "",
            "metadata": {
                "raw_archived_before_parse": True,
                "source_artifact": "",
            },
        }
    return rows


def object_rows(run_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add_many(
        path: Path,
        key: str,
        object_type: str,
        stage: str,
        disposition: str,
    ) -> None:
        payload = load_json(path)
        for index, item in enumerate(payload.get(key) or []):
            if not isinstance(item, dict):
                continue
            nested = item.get("candidate")
            nested = nested if isinstance(nested, dict) else item
            object_id = str(
                nested.get("candidate_id")
                or nested.get("seed_id")
                or item.get("candidate_id")
                or item.get("contract_sha256")
                or f"{path.stem}:{key}:{index}"
            )
            parent = str(
                nested.get("parent_id")
                or nested.get("source_branch_id")
                or item.get("source_branch_id")
                or ""
            )
            title = str(nested.get("title") or item.get("title") or object_id)
            actual_disposition = str(
                item.get("status") or nested.get("status") or disposition
            )
            rows.append(
                {
                    "object_type": object_type,
                    "object_id": object_id,
                    "parent_object_id": parent,
                    "stage": stage,
                    "title": title,
                    "disposition": actual_disposition,
                    "payload": {
                        "source_artifact": path.name,
                        "collection": key,
                        "payload": item,
                    },
                }
            )

    base = run_root / "base.json"
    if base.exists():
        add_many(
            base,
            "unique_seeds",
            "problem_seed",
            "assembled",
            "SEMANTIC_UNIQUE",
        )
    for path in sorted(run_root.glob("evolve-g*.json")):
        add_many(
            path,
            "children",
            "evolved_branch",
            stage_from_name(path.name),
            "GENERATED",
        )
    for path in sorted(run_root.glob("formulate-p*.json")):
        add_many(
            path, "candidates", "candidate", "formulation", "MACHINE_READY"
        )
        add_many(
            path,
            "reduction_pending",
            "candidate",
            "formulation",
            "REDUCTION_PENDING",
        )
        add_many(
            path,
            "rejected",
            "candidate",
            "formulation",
            "CONTRACT_REJECTED",
        )
    for path in sorted(run_root.glob("review-p*.json")):
        add_many(
            path,
            "candidates",
            "candidate_review",
            "semantic_review",
            "REVIEWED",
        )
    plan = run_root / "evidence-acquisition-plan.json"
    if plan.exists():
        add_many(
            plan,
            "entries",
            "evidence_contract",
            "bounded_evidence_design",
            "DESIGNED",
        )
    preflight = run_root / "evidence-substrate-preflight-request.json"
    if preflight.exists():
        add_many(
            preflight,
            "rows",
            "preflight_contract",
            "substrate_preflight",
            "READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT",
        )
    return rows


def import_run(
    run_root: Path,
    *,
    storage: StorageSettings | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    run_root = Path(run_root)
    manifest_path = run_root / "api-collision-execution-manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing API collision manifest: {manifest_path}")
    manifest = load_json(manifest_path)
    run_id = str(manifest.get("run_id") or run_root.name)
    manifest_sha = sha_bytes(manifest_path.read_bytes())
    raw_by_sha = raw_files(run_root)
    calls = call_metadata(run_root, raw_by_sha)
    objects = object_rows(run_root)
    json_artifacts = sorted(run_root.glob("*.json"))
    db = database_path(storage, root=root)

    with connect(db) as connection:
        existing = connection.execute(
            "SELECT manifest_sha256 FROM runs WHERE run_id=?", (run_id,)
        ).fetchone()
        if (
            existing is not None
            and str(existing["manifest_sha256"]) not in {"", manifest_sha}
        ):
            raise RuntimeError(f"run manifest conflict for {run_id}")
        insert_run_stub(
            connection,
            run_id,
            manifest_sha256=manifest_sha,
            metadata={"incremental": False},
        )
        manifest_artifact_sha, _, _ = store_artifact(
            connection, manifest_path, storage=storage, root=root
        )
        bind_run_artifact(connection,run_id=run_id,sha256=manifest_artifact_sha,role="run_manifest")
        structured_by_path: dict[Path, str] = {}
        for path in json_artifacts:
            digest, _, _ = store_artifact(
                connection, path, storage=storage, root=root
            )
            structured_by_path[path] = digest
            bind_run_artifact(connection,run_id=run_id,sha256=digest,role="structured_output")
        for raw_sha, path in raw_by_sha.items():
            actual_sha, _, _ = store_artifact(
                connection, path, storage=storage, root=root
            )
            if actual_sha != raw_sha:
                raise RuntimeError(f"raw artifact hash drift: {path}")
            bind_run_artifact(connection,run_id=run_id,sha256=raw_sha,role="raw_api_output")
            row = calls[raw_sha]
            structured_path = row.get("structured_path")
            upsert_call(
                connection,
                run_id=run_id,
                raw_sha256=raw_sha,
                structured_sha256=(
                    structured_by_path.get(structured_path)
                    if isinstance(structured_path, Path)
                    else None
                ),
                row=row,
                event_type="RUN_IMPORT_ENRICHED",
            )

        for row in objects:
            insert_research_object(
                connection,
                run_id=run_id,
                object_type=row["object_type"],
                object_id=row["object_id"],
                parent_object_id=row["parent_object_id"],
                stage=row["stage"],
                title=row["title"],
                disposition=row["disposition"],
                payload=row["payload"],
            )
            if row["parent_object_id"]:
                relation = (
                    "evolves_to"
                    if row["object_type"] == "evolved_branch"
                    else "formulates_as"
                )
                edge_id = sha_json(
                    {
                        "run_id": run_id,
                        "source": row["parent_object_id"],
                        "target": row["object_id"],
                        "relation": relation,
                    }
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO lineage_edges(
                      edge_id,run_id,source_object_id,target_object_id,
                      relation,scientific_authority
                    ) VALUES(?,?,?,?,?,0)
                    """,
                    (
                        edge_id,
                        run_id,
                        row["parent_object_id"],
                        row["object_id"],
                        relation,
                    ),
                )

        terminal = load_json(run_root / "evidence-substrate-preflight-request.json")
        status = str(
            terminal.get("status")
            or manifest.get("qualification_status")
            or manifest.get("admission_status")
            or "IMPORTED"
        )
        metadata = {
            "schema_version": str(manifest.get("schema_version") or ""),
            "manifest_artifact_sha256": manifest_artifact_sha,
            "execution": manifest.get("execution") or {},
            "search_funnel": manifest.get("search_funnel") or {},
        }
        artifact_count = int(
            connection.execute(
                "SELECT COUNT(DISTINCT sha256) AS n FROM run_artifacts WHERE run_id=?",(run_id,)
            ).fetchone()["n"]
        )
        call_count = int(
            connection.execute(
                "SELECT COUNT(*) AS n FROM api_calls WHERE run_id=?", (run_id,)
            ).fetchone()["n"]
        )
        object_count = int(
            connection.execute(
                "SELECT COUNT(*) AS n FROM research_objects WHERE run_id=?",
                (run_id,),
            ).fetchone()["n"]
        )
        connection.execute(
            """
            UPDATE runs SET
              manifest_sha256=?,transaction_kind=?,status=?,
              control_snapshot_sha256=?,frozen_pool_sha256=?,
              artifact_set_sha256=?,imported_at=?,artifact_count=?,
              call_count=?,object_count=?,metadata_json=?
            WHERE run_id=?
            """,
            (
                manifest_sha,
                str(manifest.get("transaction_kind") or "shadow_api_search"),
                status,
                str(manifest.get("control_snapshot_sha256") or ""),
                str(manifest.get("frozen_pool_sha256") or ""),
                str(manifest.get("artifact_set_sha256") or ""),
                now_utc(),
                artifact_count,
                call_count,
                object_count,
                safe_json(metadata),
                run_id,
            ),
        )

    state = build_api_research_memory_state(storage=storage, root=root)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "API_RESEARCH_RUN_IMPORTED",
        "run_id": run_id,
        "manifest_sha256": manifest_sha,
        "raw_calls": len(raw_by_sha),
        "objects": len(objects),
        "database": str(db),
        "memory_summary": state["summary"],
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Persistent API research memory")
    parser.add_argument("command", choices=("import-run", "status", "lint"))
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--persistent-root", type=Path)
    args = parser.parse_args()
    if args.command == "import-run":
        if args.run_root is None:
            parser.error("import-run requires --run-root")
        result = import_run(args.run_root, root=args.persistent_root)
    elif args.command == "lint":
        result = lint_api_research_memory(root=args.persistent_root)
    else:
        result = build_api_research_memory_state(root=args.persistent_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
