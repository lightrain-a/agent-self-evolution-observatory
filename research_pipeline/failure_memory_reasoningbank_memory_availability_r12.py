"""R12 zero-call census for exact ReasoningBank source-memory availability.

This census distinguishes (a) exact local memory bytes that can be reused now,
(b) historical ReasoningBank writer outputs whose exact bytes are no longer
locally available but whose generation is supported by archived receipts,
(c) generic explicit-cue guidance that is construct-invalid for R9/R11 L2B,
and (d) source tasks with no valid historical memory artifact discovered.

It performs no writer/model call and grants no execution authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID = "D2-C45-REASONINGBANK-MEMORY-AVAILABILITY-R12"
ARCHIVE_COMMIT = "a82901a9c29d59b0e9da2ae680fab30fa5e82d34"
R6_PATH = "generated/d2-failure-memory-provenance-r6-early-action.json"
R4_PATH = "generated/d2-failure-memory-provenance-r4-controlled-swap.json"
BRIDGE_SUPPORT_PATH = "generated/d2-failure-memory-provenance-bridge-support.json"
R6_MEMORIES_SHA256 = "a2a04f2fa6569b42c515662ef899c495d87b21fc3d70f803976a752b45aa345f"
R4_MEMORIES_SHA256 = "02623a2fdad5c87e17ecf175afe26df1d64cb8ac06a623ed3f1da99d1da15bf3"
EXPECTED_LOCAL_RUN_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-paper-failure-memory-provenance-20260822-c45")
GENERIC_BRIDGE_TASKS = {"125", "126", "228", "229", "360", "362"}


def stable_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git_json(ref: str, path: str) -> dict[str, Any]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
    return json.loads(raw)


def source_ids(r9: dict[str, Any]) -> list[str]:
    rows = r9.get("cohort") or []
    ids = [str(row["source_task_id"]) for row in rows]
    if len(ids) != 36 or len(set(ids)) != 36:
        raise ValueError("R9 must expose 36 unique source-task assignments")
    return ids


def historical_sets(r6: dict[str, Any], r4: dict[str, Any]) -> tuple[set[str], set[str]]:
    if (r6.get("source_execution") or {}).get("memories_sha256") != R6_MEMORIES_SHA256:
        raise ValueError("R6 memories aggregate digest drift")
    eq = r6.get("information_equivalence") or {}
    r6_ids = set(map(str, eq.get("eligible_pair_ids") or []))
    excluded = eq.get("excluded_pair_id")
    if excluded is not None:
        r6_ids.add(str(excluded))
    if len(r6_ids) != 24:
        raise ValueError(f"R6 candidate set drift: {len(r6_ids)}")
    if (r4.get("provenance") or {}).get("memory_generation_sha256") != R4_MEMORIES_SHA256:
        raise ValueError("R4 memory-generation aggregate digest drift")
    r4_ids = set(map(str, (r4.get("candidate_pairs") or {}).get("outcome_blind_candidate_task_ids") or []))
    if len(r4_ids) != 6:
        raise ValueError(f"R4 candidate set drift: {len(r4_ids)}")
    return r6_ids, r4_ids


def plausible_exact_memory_files(run_root: Path) -> list[str]:
    if not run_root.exists():
        return []
    out: list[str] = []
    needles = ("memories", "memory-generation", "memory_generation", "generated-memory", "generated_memory")
    for p in run_root.rglob("*"):
        if p.is_file() and any(n in p.name.lower() for n in needles):
            out.append(str(p))
    return sorted(out)


def build(r9: dict[str, Any], r6: dict[str, Any], r4: dict[str, Any], bridge: dict[str, Any]) -> dict[str, Any]:
    ids = source_ids(r9)
    r6_ids, r4_ids = historical_sets(r6, r4)
    bridge_ids = set(map(str, (bridge.get("selection_policy") or {}).get("task_ids_frozen_before_bridge_provider_calls") or []))
    if bridge_ids != GENERIC_BRIDGE_TASKS:
        raise ValueError(f"historical bridge task set drift: {sorted(bridge_ids)}")

    local_candidates = plausible_exact_memory_files(EXPECTED_LOCAL_RUN_ROOT)
    if local_candidates:
        raise ValueError(f"unexpected local exact-memory candidate files require adjudication: {local_candidates}")

    rows = []
    counts = {
        "local_exact_reasoningbank_bytes_verified": 0,
        "historical_reasoningbank_writer_output_hash_or_remote_only": 0,
        "generic_auxiliary_guidance_construct_invalid": 0,
        "no_valid_historical_memory_artifact_discovered": 0,
    }
    historical_rb: list[str] = []
    generic_invalid: list[str] = []
    no_artifact: list[str] = []
    for task_id in ids:
        if task_id in r6_ids:
            category = "HISTORICAL_REASONINGBANK_WRITER_OUTPUT_HASH_OR_REMOTE_ONLY"
            evidence = {
                "historical_stage": "R6",
                "aggregate_memories_sha256": R6_MEMORIES_SHA256,
                "remote_run_root": (r6.get("source_execution") or {}).get("run_root"),
                "remote_host": (r6.get("source_execution") or {}).get("host"),
                "exact_bytes_local": False,
            }
            counts["historical_reasoningbank_writer_output_hash_or_remote_only"] += 1
            historical_rb.append(task_id)
        elif task_id in r4_ids:
            category = "HISTORICAL_REASONINGBANK_WRITER_OUTPUT_HASH_OR_REMOTE_ONLY"
            evidence = {
                "historical_stage": "R4",
                "aggregate_memories_sha256": R4_MEMORIES_SHA256,
                "exact_bytes_local": False,
                "per_item_digest_available": False,
            }
            counts["historical_reasoningbank_writer_output_hash_or_remote_only"] += 1
            historical_rb.append(task_id)
        elif task_id in bridge_ids:
            category = "GENERIC_AUXILIARY_GUIDANCE_CONSTRUCT_INVALID"
            evidence = {
                "historical_stage": "EXPLICIT_CUE_BRIDGE",
                "reason_invalid": "fixed generic guidance is not a naturally generated ReasoningBank memory item",
                "may_substitute_for_r9_memory": False,
            }
            counts["generic_auxiliary_guidance_construct_invalid"] += 1
            generic_invalid.append(task_id)
        else:
            category = "NO_VALID_HISTORICAL_MEMORY_ARTIFACT_DISCOVERED"
            evidence = {"exact_bytes_local": False, "historical_reasoningbank_generation_receipt_discovered": False}
            counts["no_valid_historical_memory_artifact_discovered"] += 1
            no_artifact.append(task_id)
        rows.append({"source_task_id": task_id, "category": category, "evidence": evidence})

    if counts != {
        "local_exact_reasoningbank_bytes_verified": 0,
        "historical_reasoningbank_writer_output_hash_or_remote_only": 8,
        "generic_auxiliary_guidance_construct_invalid": 2,
        "no_valid_historical_memory_artifact_discovered": 26,
    }:
        raise ValueError(f"unexpected availability census: {counts}")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": RECEIPT_ID,
        "recorded_date": "2026-08-24",
        "status": "ZERO_LOCAL_EXACT_MEMORY_BYTES_UNIFORM_36_WRITER_REALIZATION_PREFERRED",
        "role": "ZERO_CALL_SOURCE_MEMORY_AVAILABILITY_CENSUS",
        "parent_r9": {
            "status": r9.get("status"),
            "source_task_count": 36,
            "source_task_ids": ids,
            "source_assignment_sha256": stable_sha(ids),
        },
        "bounded_census_scope": {
            "local_run_root": str(EXPECTED_LOCAL_RUN_ROOT),
            "local_plausible_exact_memory_files": local_candidates,
            "git_submission_package_result": "summary/aggregate receipts only; no exact R4/R6 memory text discovered in bounded audit",
            "r6_remote_recheck": "SSH_TIMEOUT_2026_08_24",
            "r6_remote_exact_bytes_counted_as_available": False,
        },
        "summary": {
            **counts,
            "historical_reasoningbank_hash_or_remote_task_ids": historical_rb,
            "generic_auxiliary_invalid_task_ids": generic_invalid,
            "no_valid_historical_artifact_task_ids": no_artifact,
            "exact_reasoningbank_memory_coverage_for_execution": "0/36",
            "support_gate_pass_for_immediate_l2_execution": False,
        },
        "source_memory_rows": rows,
        "adjudication": {
            "scientific_verdict": "NO_VERDICT_SOURCE_MEMORY_BYTES_UNAVAILABLE",
            "support_failure_is_scientific_failure": False,
            "recovering_only_historical_8_is_preferred": False,
            "hybrid_old_and_new_writer_outputs_is_preferred": False,
            "preferred_future_realization": "Generate one fixed ReasoningBank memory record for all 36 frozen source tasks under one common prospectively frozen writer contract, then content-address and freeze every memory record before any downstream L2 outcome.",
            "why_uniform_36": "A uniform writer realization avoids mixing historical R4/R6 writer configurations with newly generated memories and prevents availability-driven source-memory heterogeneity.",
            "actual_native_source_status_may_condition_writer": True,
            "downstream_metadata_treatment_must_not_regenerate_memory": True,
            "historical_r5_rescued": False,
            "o6_l3_unblocked": False,
        },
        "execution_gate": {
            "exact_memory_bytes_bound": False,
            "writer_contract_frozen": False,
            "writer_calls_permitted": False,
            "downstream_l2_outcomes_permitted": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r9", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-memory-availability-r12.json"))
    a = p.parse_args()
    r9 = json.loads(a.r9.read_text(encoding="utf-8"))
    payload = build(
        r9,
        git_json(ARCHIVE_COMMIT, R6_PATH),
        git_json(ARCHIVE_COMMIT, R4_PATH),
        git_json(ARCHIVE_COMMIT, BRIDGE_SUPPORT_PATH),
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "coverage": payload["summary"]["exact_reasoningbank_memory_coverage_for_execution"],
        "historical_hash_or_remote": payload["summary"]["historical_reasoningbank_writer_output_hash_or_remote_only"],
        "generic_invalid": payload["summary"]["generic_auxiliary_guidance_construct_invalid"],
        "no_artifact": payload["summary"]["no_valid_historical_memory_artifact_discovered"],
        "writer_calls_permitted": payload["execution_gate"]["writer_calls_permitted"],
    }))


if __name__ == "__main__":
    main()
