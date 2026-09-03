#!/usr/bin/env python3
"""Freeze B1 MemRL source retrieval support before any validation treatment.

R46 consumes only the completed R45 source-memory snapshot plus the already
preregistered validation task *instructions*.  It never resets a validation
environment, never calls the terminal evaluator, and never observes a
validation outcome.  Its job is to freeze native retrieval once for all 40
preregistered validation dependency-cluster representatives and fail closed
unless the R40 source-support gate is satisfied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
from datetime import datetime, timezone
from typing import Any

try:
    from .failure_memory_memrl_source_execute_r45 import (
        PAPER_ID,
        _build_service_and_runner,
        _digest,
        _load,
        _sha,
        _verify_receipt_hash,
    )
except ImportError:  # direct execution from the frozen runtime directory on host 60
    from failure_memory_memrl_source_execute_r45 import (  # type: ignore
        PAPER_ID,
        _build_service_and_runner,
        _digest,
        _load,
        _sha,
        _verify_receipt_hash,
    )

ROLE = "R46_SOURCE_QUALIFICATION_AND_RETRIEVAL_FREEZE_ZERO_VALIDATION_OUTCOME"
STATUS_PASS = "SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED"
STATUS_STOP = "SUPPORT_STOP_SOURCE_QUALIFICATION_FAILED_NO_VALIDATION_TREATMENT"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def _source_success(meta: dict[str, Any]) -> bool | None:
    raw = meta.get("success")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int) and raw in (0, 1):
        return bool(raw)
    extra = meta.get("model_extra")
    if isinstance(extra, dict):
        raw = extra.get("success")
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, int) and raw in (0, 1):
            return bool(raw)
    return None


def _field(meta: dict[str, Any], key: str) -> Any:
    if key in meta:
        return meta.get(key)
    extra = meta.get("model_extra")
    return extra.get(key) if isinstance(extra, dict) else None


def _text_bytes_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ids_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def _validate_source_receipt(receipt: dict[str, Any], source_build: dict[str, Any]) -> None:
    if receipt.get("paper_id") != PAPER_ID or receipt.get("status") != "SOURCE_BUILD_COMPLETE":
        raise RuntimeError("source-build-not-complete")
    if not _verify_receipt_hash(receipt):
        raise RuntimeError("source-build-receipt-hash-invalid")
    if int(receipt.get("selected_count") or 0) != 128 or int(receipt.get("completed_count") or 0) != 128:
        raise RuntimeError("source-build-count-drift")
    selected = [str(x) for x in source_build.get("selected_ids") or []]
    if receipt.get("completed_ids_sha256") != _digest(selected):
        raise RuntimeError("source-build-completed-id-drift")
    if receipt.get("validation_opened") is not False or int(receipt.get("confirmatory_outcomes_observed") or 0) != 0:
        raise RuntimeError("source-build-opened-validation")
    if int(receipt.get("external_provider_calls") or 0) != 0:
        raise RuntimeError("source-build-external-provider-drift")


def _last_checkpoint(completed_path: pathlib.Path, selected: list[str]) -> tuple[pathlib.Path, dict[str, Any]]:
    rows = [json.loads(line) for line in completed_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != len(selected) or [str(row.get("task_id")) for row in rows] != selected:
        raise RuntimeError("completed-ledger-not-exact-source-order")
    last = rows[-1]
    root = pathlib.Path(str(last.get("checkpoint_snapshot_root") or ""))
    if not root.is_dir():
        raise RuntimeError("final-source-checkpoint-missing")
    if int(last.get("checkpoint_visible_memories") or 0) < 1:
        raise RuntimeError("final-source-checkpoint-empty")
    return root, last


def build(
    manifest_path: pathlib.Path,
    source_receipt_path: pathlib.Path,
    completed_path: pathlib.Path,
    outdir: pathlib.Path,
) -> dict[str, Any]:
    manifest = _load(manifest_path)
    source_receipt = _load(source_receipt_path)
    if manifest.get("paper_id") != PAPER_ID:
        raise RuntimeError("paper-id-drift")
    execution = manifest.get("execution_manifest") or {}
    source_build = execution.get("source_build") or {}
    _validate_source_receipt(source_receipt, source_build)

    selected_source_ids = [str(x) for x in source_build.get("selected_ids") or []]
    checkpoint_root, last_checkpoint = _last_checkpoint(completed_path, selected_source_ids)

    # Build the exact same frozen service configuration, then switch it to the
    # completed source-memory snapshot. No validation environment is created.
    service, _runner = _build_service_and_runner(manifest, outdir / "qualification-runtime")
    loaded = service.load_checkpoint_snapshot(str(checkpoint_root))
    if int(loaded) < 0:
        raise RuntimeError("source-checkpoint-load-failed")

    validation = execution.get("confirmatory_units") or {}
    utilization = execution.get("utilization_qualification") or {}
    primary_ids = [str(x) for x in validation.get("representative_ids") or []]
    utilization_ids = [str(x) for x in utilization.get("representative_ids") or []]
    if len(primary_ids) != 32 or len(set(primary_ids)) != 32 or _ids_hash(primary_ids) != validation.get("representative_ids_sha256"):
        raise RuntimeError("primary-id-contract-drift")
    if len(utilization_ids) != 8 or len(set(utilization_ids)) != 8 or _ids_hash(utilization_ids) != utilization.get("representative_ids_sha256"):
        raise RuntimeError("utilization-id-contract-drift")
    if set(primary_ids) & set(utilization_ids):
        raise RuntimeError("qualification-primary-overlap")
    all_ids = primary_ids + utilization_ids

    val_path = pathlib.Path(str((execution.get("source") or {}).get("checkout") or "")) / str(validation.get("split") or "")
    if not val_path.is_file() or _sha(val_path) != validation.get("split_sha256") or validation.get("split_sha256") != utilization.get("split_sha256"):
        raise RuntimeError("validation-split-drift")
    dataset = _load(val_path)
    if any(task_id not in dataset for task_id in all_ids):
        raise RuntimeError("validation-representative-missing")

    retrieve_k = int(source_build.get("retrieve_k") or 0)
    threshold = float(((source_build.get("rl") or {}).get("sim_threshold_os") or 0.0))
    if retrieve_k != 10 or abs(threshold - 0.5) > 1e-12:
        raise RuntimeError("native-retrieval-contract-drift")

    # The native MemRL retriever includes epsilon-greedy selection. Freeze its
    # RNG once, before all retrievals, using the already-frozen R43 random seed.
    rng_seed = int(source_build.get("random_seed") or 0)
    random.seed(rng_seed)

    rows: list[dict[str, Any]] = []
    all_retrieved_polarities: set[bool] = set()
    for order_index, task_id in enumerate(all_ids):
        entry = dataset[task_id]
        instruction = str(entry.get("instruction") or "")
        if not instruction:
            raise RuntimeError(f"validation-instruction-missing:{task_id}")
        result = service.retrieve_query(task_description=instruction, k=retrieve_k, threshold=threshold)
        if isinstance(result, tuple):
            retrieval, sim_pairs = result
        else:
            retrieval, sim_pairs = result, []
        selected = list((retrieval or {}).get("selected") or [])
        frozen: list[dict[str, Any]] = []
        for rank, candidate in enumerate(selected):
            meta = _meta_dict(candidate.get("metadata"))
            success = _source_success(meta)
            source_task_id = _field(meta, "task_id")
            if source_task_id is None:
                source_task_id = _field(meta, "sample_index")
            source_task_id = str(source_task_id) if source_task_id is not None else ""
            content = candidate.get("content")
            content = str(content) if content is not None else ""
            eligible = bool(
                candidate.get("memory_id")
                and content
                and success is not None
                and source_task_id in set(selected_source_ids)
            )
            if eligible:
                all_retrieved_polarities.add(bool(success))
            frozen.append(
                {
                    "rank": rank,
                    "memory_id": str(candidate.get("memory_id") or ""),
                    "memory_id_sha256": hashlib.sha256(str(candidate.get("memory_id") or "").encode()).hexdigest(),
                    "source_task_id": source_task_id,
                    "source_outcome_success": success,
                    "content": content,
                    "content_utf8_sha256": _text_bytes_hash(content),
                    "similarity": float(candidate.get("similarity") or 0.0),
                    "q_estimate": float(candidate.get("q_estimate") or 0.0),
                    "score": float(candidate.get("score") or 0.0),
                    "eligible": eligible,
                }
            )
        eligible_count = sum(row["eligible"] for row in frozen)
        rows.append(
            {
                "order_index": order_index,
                "cohort": "primary" if task_id in set(primary_ids) else "utilization",
                "validation_task_id": task_id,
                "task_instruction": instruction,
                "task_instruction_utf8_sha256": _text_bytes_hash(instruction),
                "native_retrieve_k": retrieve_k,
                "native_similarity_threshold": threshold,
                "sim_pair_count": len(sim_pairs),
                "selected_count": len(frozen),
                "eligible_retrieval_count": eligible_count,
                "has_eligible_frozen_retrieval": eligible_count > 0,
                "selected": frozen,
            }
        )

    eligible_units = sum(row["has_eligible_frozen_retrieval"] for row in rows)
    both_polarities = all_retrieved_polarities == {False, True}
    support_pass = bool(eligible_units >= 32 and both_polarities and len(rows) == 40)
    frozen_retrieval = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "role": "R46_FROZEN_NATIVE_RETRIEVAL_BEFORE_ANY_ARM_PROJECTION",
        "recorded_at": _now(),
        "source_build_receipt_sha256": source_receipt.get("receipt_sha256"),
        "source_checkpoint_root": str(checkpoint_root),
        "source_checkpoint_textual_memory_md5": last_checkpoint.get("checkpoint_textual_memory_md5"),
        "retrieval_rng_seed": rng_seed,
        "native_retrieve_k": retrieve_k,
        "native_similarity_threshold": threshold,
        "primary_ids_sha256": _ids_hash(primary_ids),
        "utilization_ids_sha256": _ids_hash(utilization_ids),
        "all_ids_sha256": _ids_hash(all_ids),
        "rows": rows,
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
        "external_provider_calls": 0,
        "scientific_authority": False,
    }
    frozen_retrieval["receipt_sha256"] = _digest({k: v for k, v in frozen_retrieval.items() if k != "receipt_sha256"})

    outdir.mkdir(parents=True, exist_ok=True)
    retrieval_path = outdir / "frozen-retrieval.json"
    retrieval_path.write_text(json.dumps(frozen_retrieval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qualification = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "role": ROLE,
        "recorded_at": _now(),
        "status": STATUS_PASS if support_pass else STATUS_STOP,
        "source_build_receipt_sha256": source_receipt.get("receipt_sha256"),
        "frozen_retrieval_path": str(retrieval_path),
        "frozen_retrieval_file_sha256": _sha(retrieval_path),
        "frozen_retrieval_receipt_sha256": frozen_retrieval.get("receipt_sha256"),
        "total_preregistered_validation_clusters": 40,
        "eligible_frozen_retrieval_clusters": eligible_units,
        "minimum_required_eligible_clusters": 32,
        "retrievable_source_provenance_polarities": sorted("success" if x else "failure" for x in all_retrieved_polarities),
        "both_source_provenance_polarities_retrievable": both_polarities,
        "source_build_complete_without_support_retry": True,
        "retrieval_frozen_before_arm_projection": True,
        "utilization_execution_authorized_by_this_receipt": support_pass,
        "primary_confirmatory_execution_authorized_by_this_receipt": False,
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
        "external_provider_calls": 0,
        "scientific_authority": False,
        "failure_route": None if support_pass else "SUPPORT_STOP_NO_BEHAVIORAL_VERDICT",
        "next_action": (
            "RUN_ONLY_THE_FROZEN_8_CLUSTER_UTILIZATION_QUALIFICATION"
            if support_pass
            else "STOP_WITHOUT_OPENING_ANY_VALIDATION_TREATMENT"
        ),
    }
    qualification["receipt_sha256"] = _digest({k: v for k, v in qualification.items() if k != "receipt_sha256"})
    (outdir / "source-qualification-receipt.json").write_text(json.dumps(qualification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qualification


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--source-receipt", type=pathlib.Path, required=True)
    parser.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = build(args.manifest.resolve(), args.source_receipt.resolve(), args.completed_ledger.resolve(), args.output_dir.resolve())
    print(json.dumps({
        "status": result["status"],
        "eligible_frozen_retrieval_clusters": result["eligible_frozen_retrieval_clusters"],
        "both_source_provenance_polarities_retrievable": result["both_source_provenance_polarities_retrievable"],
        "validation_treatment_outcomes_observed": 0,
        "receipt_sha256": result["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
