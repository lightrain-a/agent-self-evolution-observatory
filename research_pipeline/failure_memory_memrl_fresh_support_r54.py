#!/usr/bin/env python3
"""R54: zero-validation-outcome fresh support qualification for R53 full350.

Consumes the completed R53 source bank and validation *instructions/skill lists*
only.  It never resets a validation environment or calls an evaluator.  The
final source checkpoint is cloned, its absolute snapshot pointers are rebased
inside the copy, and native MemRL retrieval is run on fresh validation clusters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import shutil
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_source_execute_r53 as r53
except ImportError:
    import failure_memory_memrl_source_execute_r53 as r53  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
ROLE = "R54_FULL350_FRESH_SUPPORT_QUALIFICATION_ZERO_VALIDATION_OUTCOME"
STATUS_PASS = "FRESH_SUPPORT_QUALIFICATION_PASS_VALIDATION_STILL_SEALED"
STATUS_STOP = "SUPPORT_STOP_FRESH_VALIDATION_INSUFFICIENT_NO_TREATMENT"
VALIDATION_SEED = "B1-R53-VALIDATION-20260902"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ids_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _md5(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _meta_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "model_dump"):
        try:
            out = value.model_dump()
            return dict(out) if isinstance(out, dict) else {}
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            pass
    return {}


def _field(meta: dict[str, Any], key: str) -> Any:
    if key in meta:
        return meta.get(key)
    extra = meta.get("model_extra")
    return extra.get(key) if isinstance(extra, dict) else None


def _source_success(meta: dict[str, Any]) -> bool | None:
    raw = _field(meta, "success")
    if type(raw) is bool:
        return raw
    if isinstance(raw, int) and raw in (0, 1):
        return bool(raw)
    return None


def _completed_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            v = json.loads(line)
            if not isinstance(v, dict):
                raise RuntimeError("R54-invalid-completed-ledger-row")
            rows.append(v)
    return rows


def _snapshot_key_hashes(root: pathlib.Path) -> dict[str, str]:
    files = {
        "snapshot_meta_sha256": root / "snapshot_meta.json",
        "textual_memory_sha256": root / "cube" / "textual_memory.json",
        "qdrant_meta_sha256": root / "qdrant" / "meta.json",
    }
    for p in files.values():
        if not p.is_file():
            raise RuntimeError(f"R54-source-snapshot-key-file-missing:{p}")
    sqlite = sorted((root / "qdrant" / "collection").glob("*/storage.sqlite"))
    if len(sqlite) != 1:
        raise RuntimeError(f"R54-source-snapshot-qdrant-storage-count:{len(sqlite)}")
    out = {k: r53._sha(p) for k, p in files.items()}
    out["qdrant_storage_sha256"] = r53._sha(sqlite[0])
    return out


def _validate_snapshot_memories(textual: pathlib.Path, source_ids: list[str]) -> dict[str, Any]:
    value = json.loads(textual.read_text(encoding="utf-8"))
    if not isinstance(value, list) or len(value) != 350:
        raise RuntimeError("R54-source-snapshot-memory-count-drift")
    seen: set[str] = set()
    polarities: set[bool] = set()
    for i, row in enumerate(value):
        if not isinstance(row, dict) or not isinstance(row.get("payload"), dict):
            raise RuntimeError(f"R54-source-memory-row-invalid:{i}")
        payload = row["payload"]
        md = payload.get("metadata")
        if not isinstance(md, dict):
            raise RuntimeError(f"R54-source-memory-metadata-invalid:{i}")
        tid = md.get("sample_index", md.get("task_id"))
        success = md.get("success")
        memory = payload.get("memory")
        if tid is None or type(success) is not bool or not isinstance(memory, str) or not memory:
            raise RuntimeError(f"R54-source-memory-required-field-invalid:{i}")
        seen.add(str(tid)); polarities.add(success)
    if seen != set(source_ids):
        raise RuntimeError("R54-source-memory-task-universe-drift")
    if polarities != {False, True}:
        raise RuntimeError("R54-source-memory-polarity-missing")
    return {"memory_count": len(value), "unique_source_task_ids": len(seen), "source_polarities": [False, True]}


def _clone_and_rebase(original: pathlib.Path, working: pathlib.Path) -> dict[str, Any]:
    if working.exists():
        raise RuntimeError("R54-working-copy-already-exists")
    before = _snapshot_key_hashes(original)
    shutil.copytree(original, working)
    copied = _snapshot_key_hashes(working)
    if copied != before:
        raise RuntimeError("R54-working-copy-byte-drift")
    meta_path = working / "snapshot_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    old_cube, old_qdrant = str(meta.get("cube_dir") or ""), str(meta.get("qdrant_dir") or "")
    if not old_cube or not old_qdrant:
        raise RuntimeError("R54-working-copy-absolute-pointer-missing")
    preserved = {k: v for k, v in meta.items() if k not in {"cube_dir", "qdrant_dir"}}
    meta["cube_dir"] = str((working / "cube").resolve())
    meta["qdrant_dir"] = str((working / "qdrant").resolve())
    if preserved != {k: v for k, v in meta.items() if k not in {"cube_dir", "qdrant_dir"}}:
        raise RuntimeError("R54-working-copy-nonpointer-drift")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"original_preload_key_hashes": before, "old_cube_dir": old_cube, "old_qdrant_dir": old_qdrant,
            "working_cube_dir": meta["cube_dir"], "working_qdrant_dir": meta["qdrant_dir"],
            "working_snapshot_meta_sha256_after_rebase": r53._sha(meta_path)}


def _signature(entry: dict[str, Any]) -> tuple[str, ...]:
    skills = entry.get("skill_list") or []
    if not isinstance(skills, list) or not skills:
        raise RuntimeError("R54-validation-skill-list-missing")
    return tuple(sorted(str(x) for x in skills))


def _cluster_rank(sig: tuple[str, ...]) -> str:
    joined = "|".join(sig)
    return hashlib.sha256(f"{VALIDATION_SEED}|cluster|{joined}".encode()).hexdigest()


def _member_rank(task_id: str) -> str:
    return hashlib.sha256(f"{VALIDATION_SEED}|member|{task_id}".encode()).hexdigest()


def _fresh_cluster_records(dataset: dict[str, Any], old_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    old_sigs: set[tuple[str, ...]] = set()
    for section in ("validation_selection", "utilization_pilot_selection"):
        for row in (old_evidence.get(section) or {}).get("selected_clusters") or []:
            old_sigs.add(tuple(str(x) for x in row.get("signature") or []))
    if len(old_sigs) != 40:
        raise RuntimeError(f"R54-old-40-signature-count-drift:{len(old_sigs)}")
    clusters: dict[tuple[str, ...], list[str]] = {}
    for task_id, entry in dataset.items():
        if not isinstance(entry, dict):
            continue
        sig = _signature(entry)
        clusters.setdefault(sig, []).append(str(task_id))
    if len(clusters) != 148:
        raise RuntimeError(f"R54-validation-cluster-count-drift:{len(clusters)}")
    fresh: list[dict[str, Any]] = []
    for sig, members in clusters.items():
        if sig in old_sigs:
            continue
        rep = min(members, key=_member_rank)
        fresh.append({
            "signature": list(sig),
            "signature_sha256": hashlib.sha256("|".join(sig).encode()).hexdigest(),
            "member_count": len(members),
            "representative_id": rep,
            "representative_rank_sha256": _member_rank(rep),
            "cluster_rank_sha256": _cluster_rank(sig),
        })
    fresh.sort(key=lambda r: r["cluster_rank_sha256"])
    if len(fresh) != 108:
        raise RuntimeError(f"R54-fresh-cluster-count-drift:{len(fresh)}")
    return fresh


def build(program_path: pathlib.Path, manifest_path: pathlib.Path, source_receipt_path: pathlib.Path,
          completed_path: pathlib.Path, old_evidence_path: pathlib.Path, contract_path: pathlib.Path,
          outdir: pathlib.Path) -> dict[str, Any]:
    program = r53._load(program_path); manifest = r53._load(manifest_path); source_receipt = r53._load(source_receipt_path)
    old_evidence = r53._load(old_evidence_path); contract = r53._load(contract_path)
    for payload in (program, manifest, source_receipt, contract):
        if payload.get("paper_id") != PAPER_ID:
            raise RuntimeError("R54-paper-id-drift")
    if not r53._verify_receipt_hash(program) or not r53._verify_receipt_hash(manifest) or not r53._verify_receipt_hash(source_receipt) or not r53._verify_receipt_hash(contract):
        raise RuntimeError("R54-receipt-hash-invalid")
    bindings = contract.get("bindings") or {}
    if bindings.get("program_contract_file_sha256") != r53._sha(program_path) or bindings.get("source_manifest_file_sha256") != r53._sha(manifest_path):
        raise RuntimeError("R54-program-or-manifest-binding-drift")
    if bindings.get("source_receipt_file_sha256") != r53._sha(source_receipt_path) or bindings.get("completed_ledger_file_sha256") != r53._sha(completed_path):
        raise RuntimeError("R54-source-completion-binding-drift")
    if bindings.get("old_selection_evidence_file_sha256") != r53._sha(old_evidence_path):
        raise RuntimeError("R54-old-selection-binding-drift")
    if bindings.get("runner_sha256") != r53._sha(pathlib.Path(__file__).resolve()):
        raise RuntimeError("R54-runner-binding-drift")

    execution = manifest.get("execution_manifest") or {}; source_build = execution.get("source_build") or {}
    source_root = pathlib.Path(str((execution.get("source") or {}).get("checkout") or ""))
    train_path = source_root / str(source_build.get("split") or "")
    if r53._sha(train_path) != source_build.get("split_sha256"):
        raise RuntimeError("R54-train-split-drift")
    train = r53._load(train_path); source_ids = r53._materialize_full350_ids(train, source_build)
    if source_receipt.get("status") != "SOURCE_BUILD_COMPLETE" or int(source_receipt.get("selected_count") or 0) != 350 or int(source_receipt.get("completed_count") or 0) != 350:
        raise RuntimeError("R54-source-build-not-complete-350")
    if source_receipt.get("completed_ids_sha256") != r53._digest(source_ids) or source_receipt.get("validation_opened") is not False or int(source_receipt.get("confirmatory_outcomes_observed") or 0) != 0:
        raise RuntimeError("R54-source-receipt-scientific-drift")

    completed = _completed_rows(completed_path)
    if len(completed) != 350 or [str(x.get("task_id")) for x in completed] != source_ids:
        raise RuntimeError("R54-completed-ledger-order-drift")
    final_root = pathlib.Path(str(completed[-1].get("checkpoint_snapshot_root") or ""))
    if not final_root.is_dir() or int(completed[-1].get("checkpoint_visible_memories") or 0) != 350:
        raise RuntimeError("R54-final-checkpoint-invalid")
    meta = r53._load(final_root / "snapshot_meta.json")
    textual = final_root / "cube" / "textual_memory.json"
    if meta.get("checkpoint_id") != f"source-350-{source_ids[-1]}" or _md5(textual) != meta.get("textual_memory_md5") or _md5(textual) != completed[-1].get("checkpoint_textual_memory_md5"):
        raise RuntimeError("R54-final-checkpoint-content-drift")
    source_memory_audit = _validate_snapshot_memories(textual, source_ids)
    expected_key_hashes = bindings.get("final_checkpoint_key_hashes") or {}
    original_before = _snapshot_key_hashes(final_root)
    if original_before != expected_key_hashes:
        raise RuntimeError("R54-final-checkpoint-key-hash-drift")

    working = outdir / "source-snapshot-working-copy"
    pointer_audit = _clone_and_rebase(final_root, working)
    service, _runner = r53._build_service_and_runner(manifest, outdir / "qualification-runtime")
    loaded = service.load_checkpoint_snapshot(str(working))
    if int(loaded) < 0:
        raise RuntimeError("R54-source-checkpoint-load-failed")

    fresh_program = program.get("fresh_validation_program") or {}
    val_path = source_root / str(fresh_program.get("split") or "")
    if not val_path.is_file() or r53._sha(val_path) != fresh_program.get("split_sha256"):
        raise RuntimeError("R54-validation-split-drift")
    dataset = r53._load(val_path)
    fresh_clusters = _fresh_cluster_records(dataset, old_evidence)
    k = int((fresh_program.get("native_retrieval") or {}).get("k") or 0)
    threshold = float((fresh_program.get("native_retrieval") or {}).get("similarity_threshold") or 0.0)
    if k != 10 or abs(threshold - 0.5) > 1e-12:
        raise RuntimeError("R54-native-retrieval-contract-drift")
    rng_seed = int(source_build.get("random_seed") or 0)
    random.seed(rng_seed)
    source_set = set(source_ids)
    rows: list[dict[str, Any]] = []
    for order_index, cluster in enumerate(fresh_clusters):
        tid = str(cluster["representative_id"]); entry = dataset[tid]; instruction = str(entry.get("instruction") or "")
        if not instruction:
            raise RuntimeError(f"R54-validation-instruction-missing:{tid}")
        result = service.retrieve_query(task_description=instruction, k=k, threshold=threshold)
        retrieval, sim_pairs = result if isinstance(result, tuple) else (result, [])
        selected_raw = list((retrieval or {}).get("selected") or [])
        frozen: list[dict[str, Any]] = []
        for rank, candidate in enumerate(selected_raw):
            md = _meta_dict(candidate.get("metadata")); success = _source_success(md)
            stid = _field(md, "task_id"); stid = _field(md, "sample_index") if stid is None else stid
            stid = str(stid) if stid is not None else ""; content = str(candidate.get("content") or "")
            eligible = bool(candidate.get("memory_id") and content and success is not None and stid in source_set)
            frozen.append({"rank": rank, "memory_id": str(candidate.get("memory_id") or ""),
                           "memory_id_sha256": hashlib.sha256(str(candidate.get("memory_id") or "").encode()).hexdigest(),
                           "source_task_id": stid, "source_outcome_success": success, "content": content,
                           "content_utf8_sha256": _text_hash(content), "similarity": float(candidate.get("similarity") or 0.0),
                           "q_estimate": float(candidate.get("q_estimate") or 0.0), "score": float(candidate.get("score") or 0.0),
                           "eligible": eligible})
        eligible_count = sum(x["eligible"] for x in frozen)
        rows.append({**cluster, "order_index": order_index, "validation_task_id": tid,
                     "task_instruction": instruction, "task_instruction_utf8_sha256": _text_hash(instruction),
                     "native_retrieve_k": k, "native_similarity_threshold": threshold, "sim_pair_count": len(sim_pairs),
                     "selected_count": len(frozen), "eligible_retrieval_count": eligible_count,
                     "has_eligible_frozen_retrieval": eligible_count > 0, "selected": frozen})

    eligible_rows = [row for row in rows if row["has_eligible_frozen_retrieval"]]
    selected40 = eligible_rows[:40]
    primary = selected40[:32]; utilization = selected40[32:40]
    selected_polarities = {bool(c["source_outcome_success"]) for row in selected40 for c in row["selected"] if c["eligible"]}
    enough = len(eligible_rows) >= 40
    both = selected_polarities == {False, True}
    passed = enough and len(primary) == 32 and len(utilization) == 8 and both

    frozen = {"schema_version": "1.0", "paper_id": PAPER_ID, "role": "R54_FRESH_NATIVE_RETRIEVAL_FREEZE",
              "recorded_at": _now(), "source_build_receipt_sha256": source_receipt.get("receipt_sha256"),
              "source_checkpoint_root": str(final_root), "source_checkpoint_textual_memory_md5": completed[-1].get("checkpoint_textual_memory_md5"),
              "retrieval_rng_seed": rng_seed, "native_retrieve_k": k, "native_similarity_threshold": threshold,
              "old_40_cluster_signatures_excluded": True, "fresh_candidate_cluster_count": len(rows), "rows": rows,
              "validation_environment_resets": 0, "validation_evaluator_calls": 0, "validation_treatment_outcomes_observed": 0,
              "external_provider_calls": 0, "scientific_authority": False}
    frozen["receipt_sha256"] = r53._digest({k: v for k, v in frozen.items() if k != "receipt_sha256"})
    outdir.mkdir(parents=True, exist_ok=True)
    frozen_path = outdir / "fresh-frozen-retrieval.json"
    frozen_path.write_text(json.dumps(frozen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    selection = {"schema_version": "1.0", "paper_id": PAPER_ID, "role": "R54_FRESH_32_PLUS_8_SELECTION_BEFORE_TREATMENT",
                 "recorded_at": _now(), "selection_seed": VALIDATION_SEED,
                 "candidate_rank_encoding": "SHA256(seed|cluster|skill1|skill2|...)",
                 "representative_encoding": "SHA256(seed|member|task_id)",
                 "eligible_cluster_rule": fresh_program.get("eligible_cluster"),
                 "eligible_cluster_count": len(eligible_rows),
                 "primary_representative_ids": [str(r["validation_task_id"]) for r in primary],
                 "primary_representative_ids_sha256": _ids_hash([str(r["validation_task_id"]) for r in primary]) if len(primary)==32 else "",
                 "utilization_representative_ids": [str(r["validation_task_id"]) for r in utilization],
                 "utilization_representative_ids_sha256": _ids_hash([str(r["validation_task_id"]) for r in utilization]) if len(utilization)==8 else "",
                 "primary_records": primary, "utilization_records": utilization,
                 "selected_retrieval_polarities": sorted("success" if p else "failure" for p in selected_polarities),
                 "both_source_provenance_polarities_retrievable": both,
                 "selection_uses_validation_outcomes": False, "validation_environment_resets": 0,
                 "validation_evaluator_calls": 0, "validation_treatment_outcomes_observed": 0, "scientific_authority": False}
    selection["receipt_sha256"] = r53._digest({k: v for k, v in selection.items() if k != "receipt_sha256"})
    selection_path = outdir / "fresh-validation-selection.json"
    selection_path.write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    original_after = _snapshot_key_hashes(final_root)
    if original_after != original_before:
        raise RuntimeError("R54-original-source-snapshot-mutated")
    receipt = {"schema_version": "1.0", "paper_id": PAPER_ID, "role": ROLE, "recorded_at": _now(),
               "status": STATUS_PASS if passed else STATUS_STOP, "source_build_receipt_sha256": source_receipt.get("receipt_sha256"),
               "fresh_candidate_cluster_count": len(rows), "eligible_fresh_cluster_count": len(eligible_rows), "minimum_eligible_clusters": 40,
               "primary_selected_count": len(primary), "utilization_selected_count": len(utilization),
               "both_source_provenance_polarities_retrievable": both, "frozen_retrieval_file_sha256": r53._sha(frozen_path),
               "frozen_retrieval_receipt_sha256": frozen["receipt_sha256"], "selection_file_sha256": r53._sha(selection_path),
               "selection_receipt_sha256": selection["receipt_sha256"], "source_memory_audit": source_memory_audit,
               "copy_on_write_pointer_audit": pointer_audit,
               "original_source_snapshot_preload_key_hashes": original_before,
               "original_source_snapshot_postload_key_hashes": original_after,
               "validation_environment_resets": 0, "validation_evaluator_calls": 0, "validation_treatment_outcomes_observed": 0,
               "external_provider_calls": 0, "scientific_authority": False,
               "failure_route": None if passed else "SUPPORT_STOP_NO_BEHAVIORAL_VERDICT",
               "next_action": "FREEZE_UTILIZATION_EXECUTION_AUTHORITY" if passed else "STOP_WITHOUT_VALIDATION_TREATMENT"}
    receipt["receipt_sha256"] = r53._digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    receipt_path = outdir / "fresh-support-qualification-receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--program-contract", type=pathlib.Path, required=True)
    p.add_argument("--source-manifest", type=pathlib.Path, required=True)
    p.add_argument("--source-receipt", type=pathlib.Path, required=True)
    p.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    p.add_argument("--old-selection-evidence", type=pathlib.Path, required=True)
    p.add_argument("--qualification-contract", type=pathlib.Path, required=True)
    p.add_argument("--output-dir", type=pathlib.Path, required=True)
    a = p.parse_args()
    r = build(a.program_contract.resolve(), a.source_manifest.resolve(), a.source_receipt.resolve(), a.completed_ledger.resolve(),
              a.old_selection_evidence.resolve(), a.qualification_contract.resolve(), a.output_dir.resolve())
    print(json.dumps({"status": r["status"], "eligible_fresh_cluster_count": r["eligible_fresh_cluster_count"],
                      "primary_selected_count": r["primary_selected_count"], "utilization_selected_count": r["utilization_selected_count"],
                      "both_source_provenance_polarities_retrievable": r["both_source_provenance_polarities_retrievable"],
                      "validation_treatment_outcomes_observed": 0, "receipt_sha256": r["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
