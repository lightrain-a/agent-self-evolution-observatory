#!/usr/bin/env python3
"""Snapshot-backed R46 qualification for the R45-M1 replacement lineage.

R46M3 repairs only a qualification-interface false negative discovered after the
single authorized source build completed and before any validation treatment
outcome was opened.  The frozen R46/R46M2 retrieval, RNG, support, unit, and
adjudication semantics are unchanged.

The original R46 helper rejected the final source checkpoint when
``snapshot_meta.visible_memories == 0``.  On the replacement MemoryOS/Qdrant
runtime that field is produced by ``mos.get_all`` and can be zero even when the
content-addressed cube contains all source memories and native retrieval works.
R46M3 therefore validates the source snapshot directly, clones it to a
copy-on-write qualification directory, and lets the unchanged R46/R46M2 code
load and retrieve from that clone.  The original R45-M1 checkpoint is never
passed to ``load_checkpoint_snapshot`` and must remain byte-stable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
from typing import Any

try:
    from . import failure_memory_memrl_source_qualification_r46m2 as strict
    from .failure_memory_memrl_source_execute_r45m1 import _digest, _load, _sha
except ImportError:
    import failure_memory_memrl_source_qualification_r46m2 as strict  # type: ignore
    from failure_memory_memrl_source_execute_r45m1 import _digest, _load, _sha  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
INTERFACE_REVISION = "R46M3_SNAPSHOT_BACKED_COPY_ON_WRITE"

_WORKING_COPY_ROOT: pathlib.Path | None = None
_SNAPSHOT_AUDIT: dict[str, Any] | None = None


def _md5(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _completed_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError("invalid-completed-ledger-row")
        rows.append(value)
    return rows


def _source_snapshot_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise RuntimeError("source-snapshot-textual-memory-not-list")
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(value):
        if not isinstance(row, dict):
            raise RuntimeError(f"source-snapshot-row-not-object:{i}")
        payload = row.get("payload")
        if not isinstance(payload, dict):
            raise RuntimeError(f"source-snapshot-payload-missing:{i}")
        memory = payload.get("memory")
        metadata = payload.get("metadata")
        memory_id = payload.get("id") or row.get("id")
        if not isinstance(memory_id, str) or not memory_id:
            raise RuntimeError(f"source-snapshot-memory-id-missing:{i}")
        if not isinstance(memory, str) or not memory:
            raise RuntimeError(f"source-snapshot-memory-content-missing:{i}")
        if not isinstance(metadata, dict):
            raise RuntimeError(f"source-snapshot-metadata-missing:{i}")
        success = metadata.get("success")
        if type(success) is not bool:
            raise RuntimeError(f"source-snapshot-success-not-boolean:{i}")
        task_id = metadata.get("sample_index", metadata.get("task_id"))
        if task_id is None:
            raise RuntimeError(f"source-snapshot-task-id-missing:{i}")
        rows.append({
            "memory_id": memory_id,
            "task_id": str(task_id),
            "success": success,
            "memory_utf8_sha256": hashlib.sha256(memory.encode("utf-8")).hexdigest(),
        })
    return rows


def _key_snapshot_hashes(root: pathlib.Path) -> dict[str, str]:
    meta = root / "snapshot_meta.json"
    textual = root / "cube" / "textual_memory.json"
    qmeta = root / "qdrant" / "meta.json"
    if not (meta.is_file() and textual.is_file() and qmeta.is_file()):
        raise RuntimeError("source-snapshot-key-file-missing")
    live = sorted((root / "qdrant" / "collection").glob("*/storage.sqlite"))
    if not live:
        raise RuntimeError("source-snapshot-qdrant-storage-missing")
    return {
        "snapshot_meta_sha256": _sha(meta),
        "textual_memory_sha256": _sha(textual),
        "qdrant_meta_sha256": _sha(qmeta),
        "qdrant_storage_sha256": _sha(live[0]),
    }


def snapshot_backed_last_checkpoint(
    completed_path: pathlib.Path, selected: list[str]
) -> tuple[pathlib.Path, dict[str, Any]]:
    global _SNAPSHOT_AUDIT
    if _WORKING_COPY_ROOT is None:
        raise RuntimeError("R46M3-working-copy-root-not-configured")
    rows = _completed_rows(completed_path)
    if len(rows) != len(selected) or [str(row.get("task_id")) for row in rows] != selected:
        raise RuntimeError("completed-ledger-not-exact-source-order")
    last = rows[-1]
    original = pathlib.Path(str(last.get("checkpoint_snapshot_root") or ""))
    if not original.is_dir():
        raise RuntimeError("final-source-checkpoint-missing")

    meta_path = original / "snapshot_meta.json"
    textual_path = original / "cube" / "textual_memory.json"
    meta = _load(meta_path)
    if meta.get("checkpoint_id") != f"source-{len(selected):03d}-{selected[-1]}":
        raise RuntimeError("final-source-checkpoint-id-drift")
    actual_md5 = _md5(textual_path)
    if actual_md5 != meta.get("textual_memory_md5") or actual_md5 != last.get("checkpoint_textual_memory_md5"):
        raise RuntimeError("final-source-textual-memory-md5-drift")

    memories = _source_snapshot_rows(textual_path)
    task_ids = [row["task_id"] for row in memories]
    if len(memories) != len(selected):
        raise RuntimeError("final-source-memory-count-drift")
    if len(set(task_ids)) != len(selected) or set(task_ids) != set(selected):
        raise RuntimeError("final-source-memory-task-support-drift")
    polarities = {bool(row["success"]) for row in memories}
    if polarities != {False, True}:
        raise RuntimeError("final-source-memory-provenance-polarity-missing")

    before = _key_snapshot_hashes(original)
    working = _WORKING_COPY_ROOT
    if working.exists():
        raise RuntimeError("R46M3-working-copy-already-exists")
    working.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(original, working)
    copied = _key_snapshot_hashes(working)
    if copied != before:
        raise RuntimeError("R46M3-working-copy-byte-drift")

    _SNAPSHOT_AUDIT = {
        "original_snapshot_root": str(original),
        "working_copy_root": str(working),
        "snapshot_meta_visible_memories_diagnostic": meta.get("visible_memories"),
        "visible_memories_field_used_for_qualification": False,
        "actual_textual_memory_entries": len(memories),
        "unique_source_task_ids": len(set(task_ids)),
        "source_success_memories": sum(row["success"] is True for row in memories),
        "source_failure_memories": sum(row["success"] is False for row in memories),
        "original_preload_key_hashes": before,
        "working_copy_preload_key_hashes": copied,
    }
    return working, last


def build(
    manifest: pathlib.Path,
    source_receipt: pathlib.Path,
    completed: pathlib.Path,
    outdir: pathlib.Path,
) -> dict[str, Any]:
    global _WORKING_COPY_ROOT, _SNAPSHOT_AUDIT
    _WORKING_COPY_ROOT = outdir / "source-snapshot-working-copy"
    _SNAPSHOT_AUDIT = None

    # Patch only the original R46 checkpoint-interface helper.  R46M1 service
    # binding and R46M2 strict 32/32 adjudication remain unchanged.
    strict.base.base._last_checkpoint = snapshot_backed_last_checkpoint
    result = strict.build(manifest, source_receipt, completed, outdir)
    if _SNAPSHOT_AUDIT is None:
        raise RuntimeError("R46M3-snapshot-audit-missing")

    original = pathlib.Path(_SNAPSHOT_AUDIT["original_snapshot_root"])
    after = _key_snapshot_hashes(original)
    if after != _SNAPSHOT_AUDIT["original_preload_key_hashes"]:
        raise RuntimeError("R46M3-original-source-snapshot-mutated")

    out = dict(result)
    out.pop("receipt_sha256", None)
    out.update({
        "qualification_interface_revision": INTERFACE_REVISION,
        "qualification_interface_change_only": True,
        "retrieval_algorithm_changed": False,
        "retrieval_threshold_changed": False,
        "retrieval_rng_changed": False,
        "validation_unit_selection_changed": False,
        "support_adjudication_changed_from_R46M2": False,
        "source_snapshot_audit": {**_SNAPSHOT_AUDIT, "original_postload_key_hashes": after},
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
        "scientific_authority": False,
    })
    out["receipt_sha256"] = _digest(out)
    path = outdir / "source-qualification-strict-r46m3-receipt.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=pathlib.Path, required=True)
    p.add_argument("--source-receipt", type=pathlib.Path, required=True)
    p.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    p.add_argument("--output-dir", type=pathlib.Path, required=True)
    a = p.parse_args()
    r = build(a.manifest.resolve(), a.source_receipt.resolve(), a.completed_ledger.resolve(), a.output_dir.resolve())
    print(json.dumps({
        "status": r["status"],
        "qualification_interface_revision": r["qualification_interface_revision"],
        "primary_clusters_with_eligible_frozen_retrieval": r["primary_clusters_with_eligible_frozen_retrieval"],
        "all_32_primary_clusters_supported": r["all_32_primary_clusters_supported"],
        "utilization_clusters_with_eligible_frozen_retrieval": r["utilization_clusters_with_eligible_frozen_retrieval"],
        "both_source_provenance_polarities_retrievable": r["both_source_provenance_polarities_retrievable"],
        "validation_treatment_outcomes_observed": 0,
        "receipt_sha256": r["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
