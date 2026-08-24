#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
OBJECTION_ID = "PROXY-O6"
AUTHORITY_TYPE = "human-c1-proxy-reward-stanford-repair-experiment-program"
EXPECTED_O6_DESIGN_SHA = "e33996f4e4f00da7b162bf7e9c26ca004aaf7e5d04f2547aacbc04f47ad05c1e"
EXPECTED_STAGE1_HANDOFF_SHA = "1ec986064b4c497dd04cd11366b78c31548d1c1ce9b271c8cf5c1382b650d04b"
EXPECTED_SOURCE_MESSAGE_SHA = "7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62"
EXPECTED_INPUT_SHA = {
    "support": "b64635594251ac8f74251ea68b39a0c0c03b689b0708366be9c68ff193edd7ce",
    "parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "task_config": "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6",
    "evaluator": "f78eb61554c811f9411e7d72e0bdf2b5baa27379cbf632ade7fe49ce51a3f30d",
    "original_f2r1": "04db52a9c2a1eac28df4213e5041e2f20e8e4b3591d5941f9e6d889a8b8dc2e9",
    "o5_evidence": "202a253e9766221c4de727afc9aedb7b4395b4814f15c1f82db0b93c166ae7e8",
}
SOURCE_TASKS = ["21", "22", "23", "25"]
FUTURE_TASKS = ["164", "385", "387", "388"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile the fail-closed O6 cross-writer terminal Stage-2 contract.")
    ap.add_argument("--master-authority", required=True, type=Path)
    ap.add_argument("--o6-design", required=True, type=Path)
    ap.add_argument("--stage1-handoff", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    ap.add_argument("--input-root", required=True, type=Path)
    ap.add_argument("--env-file", required=True, type=Path)
    ap.add_argument("--run-root", required=True, type=Path)
    args = ap.parse_args()

    require(sha(args.o6_design) == EXPECTED_O6_DESIGN_SHA, "O6 design SHA drift")
    require(sha(args.stage1_handoff) == EXPECTED_STAGE1_HANDOFF_SHA, "Stage-1 handoff SHA drift")
    design = load(args.o6_design)
    handoff = load(args.stage1_handoff)
    master = load(args.master_authority)

    require(handoff["status"] == "STAGE1_R1_PASS_READY_FOR_SEPARATE_STAGE2_CONTRACT", "Stage-1 handoff not pass-ready")
    require(handoff["summary"]["stage1_gate_pass"] is True and handoff["summary"]["complete_pairs"] == 4, "Stage-1 gate not satisfied")
    require(handoff["stage2_provider_calls_authorized_by_handoff"] == 0 and handoff["stage2_requires_separate_execution_contract"] is True, "Stage-1 handoff leaked Stage-2 authority")
    require(handoff["stage2_gate_inherited_unchanged"] == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05}, "Stage-1 handoff Stage-2 gate drift")

    stage2 = design["stage2_cross_writer_terminal_replication"]
    require(stage2["source_memory_tasks"] == SOURCE_TASKS and stage2["future_tasks"] == FUTURE_TASKS, "Stage-2 support drift")
    require(stage2["provider_calls"] == 256 and stage2["rollouts_per_cell_per_condition"] == 8, "Stage-2 call geometry drift")
    require(stage2["support_if"] == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05}, "Stage-2 gate drift")
    require(stage2["permutation_repetitions"] == 100000 and stage2["permutation_seed"] == 20260824, "Stage-2 permutation contract drift")
    model = stage2["downstream_model"]
    require(model["requested"] == "doubao-seed-2.0-mini" and model["expected_resolved"] == "doubao-seed-2-0-mini-260215", "Stage-2 downstream model drift")
    require(model["temperature"] == 0.2 and model["max_output_tokens"] == 900 and model["thinking"] == "disabled", "Stage-2 downstream sampling drift")
    require(model["allow_thinking_compatibility_fallback"] is False and model["provider_retries"] == 0 and model["substitution_allowed"] is False, "Stage-2 downstream execution drift")
    require(stage2["primary_gate_uses_o5_no_memory"] is False, "O5 baseline must not enter Stage-2 primary gate")

    require(master.get("authority_type") == AUTHORITY_TYPE and master.get("decision") == "approve" and master.get("reviewed_by") in {"user", "human-user"}, "master human authority invalid")
    require(master.get("paper_id") == PAPER_ID and master.get("source_message_sha256") == EXPECTED_SOURCE_MESSAGE_SHA, "master authority binding mismatch")
    future = master.get("future_repair_experiments") or {}
    require(future.get("human_program_authorized") is True and future.get("requires_per_experiment_preregistration") is True and future.get("requires_budget_and_stop_rule") is True, "C1 repair-program authority insufficient")
    require(future.get("automatic_execution_without_frozen_subcontract") is False and future.get("outcome_driven_scope_expansion_authorized") is False, "master authority must remain fail-closed")
    require(master.get("provider_credential_use_authorized_if_required_by_a_frozen_subcontract") is True, "provider credential use not authorized")
    require(master.get("claim_expansion_authorized") is False and master.get("submission_authority") is False, "master authority scope expanded")

    input_paths = {
        "support": args.input_root / "generated/d2-proxy-reward-terminal-fixed-evidence-support.json",
        "parquet": args.input_root / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet",
        "task_config": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json",
        "evaluator": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py",
        "vendor": args.input_root / "generated/research-data/paper-yield-d5-c01/vendor",
        "original_f2r1": Path(design["source_bindings"]["original_f2r1"]["path"]),
        "o5_evidence": Path(design["source_bindings"]["fresh_o5_no_memory"]["path"]),
    }
    for key in EXPECTED_INPUT_SHA:
        require(input_paths[key].is_file(), f"missing Stage-2 input: {key}")
        require(sha(input_paths[key]) == EXPECTED_INPUT_SHA[key], f"Stage-2 input SHA drift: {key}")
    require(input_paths["vendor"].is_dir(), "historical PyArrow vendor runtime missing")
    require(args.env_file.is_file(), "provider env file missing")
    require(args.runner.is_file(), "Stage-2 runner missing")

    memory_rows = handoff["memory_objects"]
    require(len(memory_rows) == 8, "Stage-1 handoff must expose exactly eight memory objects")
    memory_map: dict[str, dict[str, dict[str, str]]] = {task: {} for task in SOURCE_TASKS}
    for row in memory_rows:
        task = str(row["source_memory_task"])
        condition = str(row["condition"])
        require(task in SOURCE_TASKS and condition in {"success_label_memory", "failure_label_memory"}, "unexpected Stage-1 memory object")
        raw = Path(row["raw_path"])
        require(raw.is_file() and sha(raw) == row["raw_sha256"], f"Stage-1 raw memory SHA drift: {task}/{condition}")
        memory_map[task][condition] = {"path": str(raw.resolve()), "sha256": row["raw_sha256"]}
    for task in SOURCE_TASKS:
        require(set(memory_map[task]) == {"success_label_memory", "failure_label_memory"}, f"missing Stage-1 memory condition: {task}")

    run_root = args.run_root.resolve()
    contract = {
        "schema_version": "1.0",
        "experiment_id": "D2-PROXY-O6-CROSS-WRITER-GLM53-TERMINAL-STAGE2",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "status": "FROZEN_BEFORE_PROVIDER_CALLS",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_root": str(run_root),
        "human_authority": {"path": str(args.master_authority.resolve()), "sha256": sha(args.master_authority), "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA},
        "design": {"path": str(args.o6_design.resolve()), "sha256": EXPECTED_O6_DESIGN_SHA},
        "stage1_handoff": {"path": str(args.stage1_handoff.resolve()), "sha256": EXPECTED_STAGE1_HANDOFF_SHA},
        "code": {"runner": {"path": str(args.runner.resolve()), "sha256": sha(args.runner)}},
        "source_artifacts": {key: {"path": str(path.resolve()), "sha256": EXPECTED_INPUT_SHA[key]} for key, path in input_paths.items() if key in EXPECTED_INPUT_SHA},
        "vendor_path": str(input_paths["vendor"].resolve()),
        "provider_env_file": str(args.env_file.resolve()),
        "source_memory_tasks": SOURCE_TASKS,
        "future_tasks": FUTURE_TASKS,
        "memory_objects": memory_map,
        "conditions": ["success_label_memory", "failure_label_memory"],
        "rollouts_per_cell_per_condition": 8,
        "expected_provider_calls": 256,
        "model": model,
        "terminal_gate": {
            "primary_statistic": stage2["primary_statistic"],
            "permutation_scheme": stage2["permutation_scheme"],
            "permutation_repetitions": 100000,
            "permutation_seed": 20260824,
            "alpha": 0.05,
            "min_mean_absolute_success_rate_difference": 0.15
        },
        "secondary_descriptives": stage2["secondary_descriptives"],
        "o5_no_memory": {"path": str(input_paths["o5_evidence"].resolve()), "sha256": EXPECTED_INPUT_SHA["o5_evidence"], "primary_gate_uses": False},
        "original_f2r1": {"path": str(input_paths["original_f2r1"].resolve()), "sha256": EXPECTED_INPUT_SHA["original_f2r1"], "primary_gate_uses": False},
        "missingness_policy": {"provider_retries": 0, "stop_after_first_no_text_provider_failure": True, "top_up_failed_units": False, "replace_cells": False, "text_bearing_provider_status_incomplete_is_scorable": True},
        "execution_guards": {"single_writer_transaction_lock_required": True, "response_first_archival_required": True, "resumable_content_addressed_stage_cache": True},
        "authority": {"scientific_reopen_authority": True, "experiment_authority": True, "provider_call_authority": True, "gpu_authority": False, "claim_expansion_authority": False, "submission_authority": False}
    }
    contract_path = run_root / "o6-stage2-contract.json"
    atomic_json(contract_path, contract)
    receipt = {
        "schema_version": "1.0", "receipt_type": "scoped-experiment-authorization",
        "paper_id": PAPER_ID, "objection_id": OBJECTION_ID, "experiment_id": contract["experiment_id"],
        "status": "O6_CROSS_WRITER_TERMINAL_STAGE2_AUTHORIZED",
        "master_authority_sha256": sha(args.master_authority), "design_sha256": EXPECTED_O6_DESIGN_SHA,
        "stage1_handoff_sha256": EXPECTED_STAGE1_HANDOFF_SHA, "contract_sha256": sha(contract_path), "runner_sha256": contract["code"]["runner"]["sha256"],
        "provider_call_ceiling": 256, "primary_gate": contract["terminal_gate"], "no_memory_calls": 0, "authority": contract["authority"]
    }
    atomic_json(run_root / "o6-stage2-authorization-receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "contract_sha256": receipt["contract_sha256"], "provider_call_ceiling": 256, "primary_gate": receipt["primary_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
