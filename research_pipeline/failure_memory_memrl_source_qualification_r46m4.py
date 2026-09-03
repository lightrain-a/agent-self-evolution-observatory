#!/usr/bin/env python3
"""R46M4: copy-on-write snapshot pointer repair for R45-M1 qualification.

R46M3 correctly cloned the final source snapshot, but the cloned
``snapshot_meta.json`` retained absolute ``cube_dir`` / ``qdrant_dir`` paths to
the original R45-M1 checkpoint.  MemoryOS therefore followed those pointers
back to the original Qdrant directory during load.  R46M4 changes only those
two paths inside the qualification working copy before native loading.

All R46M3 snapshot integrity checks and all R46/R46M2 retrieval/support
semantics remain unchanged.  Validation environments/evaluators are still
sealed.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

try:
    from . import failure_memory_memrl_source_qualification_r46m3 as m3
    from .failure_memory_memrl_source_execute_r45m1 import _digest, _sha
except ImportError:
    import failure_memory_memrl_source_qualification_r46m3 as m3  # type: ignore
    from failure_memory_memrl_source_execute_r45m1 import _digest, _sha  # type: ignore

INTERFACE_REVISION = "R46M4_COPY_ON_WRITE_POINTER_REBASE"
_M3_LAST_CHECKPOINT = m3.snapshot_backed_last_checkpoint
_POINTER_AUDIT: dict[str, Any] | None = None


def rebase_working_copy_pointers(working: pathlib.Path) -> dict[str, Any]:
    meta_path = working / "snapshot_meta.json"
    if not meta_path.is_file():
        raise RuntimeError("R46M4-working-snapshot-meta-missing")
    before_bytes = meta_path.read_bytes()
    meta = json.loads(before_bytes.decode("utf-8"))
    if not isinstance(meta, dict):
        raise RuntimeError("R46M4-working-snapshot-meta-not-object")
    old_cube = str(meta.get("cube_dir") or "")
    old_qdrant = str(meta.get("qdrant_dir") or "")
    new_cube = str((working / "cube").resolve())
    new_qdrant = str((working / "qdrant").resolve())
    if not (old_cube and old_qdrant):
        raise RuntimeError("R46M4-working-snapshot-absolute-pointers-missing")
    if old_cube == new_cube or old_qdrant == new_qdrant:
        raise RuntimeError("R46M4-working-snapshot-pointer-already-rebased")
    if not pathlib.Path(new_cube).is_dir() or not pathlib.Path(new_qdrant).is_dir():
        raise RuntimeError("R46M4-working-snapshot-target-dir-missing")

    preserved = {k: v for k, v in meta.items() if k not in {"cube_dir", "qdrant_dir"}}
    meta["cube_dir"] = new_cube
    meta["qdrant_dir"] = new_qdrant
    after_preserved = {k: v for k, v in meta.items() if k not in {"cube_dir", "qdrant_dir"}}
    if preserved != after_preserved:
        raise RuntimeError("R46M4-nonpointer-snapshot-meta-drift")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "working_snapshot_meta_pre_rebase_sha256": __import__("hashlib").sha256(before_bytes).hexdigest(),
        "working_snapshot_meta_post_rebase_sha256": _sha(meta_path),
        "old_cube_dir": old_cube,
        "old_qdrant_dir": old_qdrant,
        "new_cube_dir": new_cube,
        "new_qdrant_dir": new_qdrant,
        "changed_fields": ["cube_dir", "qdrant_dir"],
        "nonpointer_fields_byte_semantics_preserved": True,
    }


def pointer_rebased_last_checkpoint(
    completed_path: pathlib.Path, selected: list[str]
):
    global _POINTER_AUDIT
    working, last = _M3_LAST_CHECKPOINT(completed_path, selected)
    _POINTER_AUDIT = rebase_working_copy_pointers(working)
    if m3._SNAPSHOT_AUDIT is not None:
        m3._SNAPSHOT_AUDIT["working_copy_pointer_rebase"] = dict(_POINTER_AUDIT)
    return working, last


def build(
    manifest: pathlib.Path,
    source_receipt: pathlib.Path,
    completed: pathlib.Path,
    outdir: pathlib.Path,
) -> dict[str, Any]:
    global _POINTER_AUDIT
    _POINTER_AUDIT = None
    # m3.build resolves this module-global at execution time when rebinding the
    # original R46 helper, so replace it only for this R46M4 process.
    m3.snapshot_backed_last_checkpoint = pointer_rebased_last_checkpoint
    out = m3.build(manifest, source_receipt, completed, outdir)
    if _POINTER_AUDIT is None:
        raise RuntimeError("R46M4-pointer-audit-missing")
    out = dict(out)
    out.pop("receipt_sha256", None)
    out.update({
        "qualification_interface_revision": INTERFACE_REVISION,
        "R46M3_result_admissible": False,
        "working_copy_absolute_pointer_repair_only": True,
        "working_copy_pointer_audit": _POINTER_AUDIT,
        "retrieval_algorithm_changed": False,
        "retrieval_threshold_changed": False,
        "retrieval_rng_changed": False,
        "R46M2_strict_support_adjudication_changed": False,
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
        "scientific_authority": False,
    })
    out["receipt_sha256"] = _digest(out)
    p = outdir / "source-qualification-strict-r46m4-receipt.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
