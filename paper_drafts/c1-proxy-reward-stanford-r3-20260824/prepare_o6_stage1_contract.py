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
EXPECTED_DESIGN_SHA256 = "e33996f4e4f00da7b162bf7e9c26ca004aaf7e5d04f2547aacbc04f47ad05c1e"
EXPECTED_SOURCE_MESSAGE_SHA256 = "7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62"
EXPECTED_INPUT_SHA256 = {
    "parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "success_prompt": "5d4893a5f3dc5fadda43f166d6f322d729c197d8a8a74ca953f7c10acabb940a",
    "failure_prompt": "9bd01483afd8f8366ade02c7d839657d38f3eb263daa5cbfe15445b956116b45",
    "original_f0": "f2e4f3424faf1e3a9ec7aba7958e538eac457e89308552ef7a9c3d69c6a914f9",
}
SOURCE_TASKS = ["21", "22", "23", "25"]


def sha256(path: Path) -> str:
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
    ap = argparse.ArgumentParser(description="Compile the fail-closed PROXY-O6 cross-writer Stage-1 execution contract.")
    ap.add_argument("--master-authority", required=True, type=Path)
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    ap.add_argument("--input-root", required=True, type=Path)
    ap.add_argument("--env-file", required=True, type=Path)
    ap.add_argument("--run-root", required=True, type=Path)
    args = ap.parse_args()

    require(sha256(args.design) == EXPECTED_DESIGN_SHA256, "O6 design SHA drift")
    design = load(args.design)
    master = load(args.master_authority)
    require(master.get("authority_type") == AUTHORITY_TYPE, "master authority type mismatch")
    require(master.get("decision") == "approve", "master authority not approved")
    require(master.get("reviewed_by") in {"user", "human-user"}, "master authority reviewer mismatch")
    require(master.get("paper_id") == PAPER_ID, "master authority paper mismatch")
    require(master.get("source_message_sha256") == EXPECTED_SOURCE_MESSAGE_SHA256, "master authority source-message mismatch")
    future = master.get("future_repair_experiments") or {}
    require(future.get("human_program_authorized") is True, "future C1 repair experiments not authorized")
    require(future.get("automatic_execution_without_frozen_subcontract") is False, "master authority must remain fail-closed")
    require(future.get("requires_per_experiment_preregistration") is True, "per-experiment preregistration required")
    require(future.get("requires_budget_and_stop_rule") is True, "budget/stop rule required")
    require(future.get("outcome_driven_scope_expansion_authorized") is False, "outcome-driven expansion forbidden")
    require(master.get("provider_credential_use_authorized_if_required_by_a_frozen_subcontract") is True, "provider credential use not program-authorized")
    require(master.get("claim_expansion_authorized") is False, "claim expansion must remain unauthorized")
    require(master.get("submission_authority") is False, "submission must remain unauthorized")

    stage1 = design["stage1_cross_writer_write_channel"]
    require(stage1["writer_model"]["requested"] == "glm-5.3", "writer-model drift")
    require(stage1["provider_calls"] == 8, "Stage-1 call budget drift")
    require(stage1["advance_to_stage2_if"]["exact_content_changed_pairs_min"] == 4, "content-change gate drift")
    require(stage1["advance_to_stage2_if"]["title_set_changed_pairs_min"] == 3, "title-set gate drift")
    require(stage1["advance_to_stage2_if"]["token_jaccard_threshold"] is None, "unexpected token-distance threshold")
    require(design["stage2_cross_writer_terminal_replication"]["support_if"] == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05}, "Stage-2 preregistered gate drift")

    input_paths = {
        "parquet": args.input_root / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet",
        "success_prompt": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_pass.md",
        "failure_prompt": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_fail.md",
        "vendor": args.input_root / "generated/research-data/paper-yield-d5-c01/vendor",
        "original_f0": Path(design["source_bindings"]["original_f0"]["path"]),
    }
    for key in EXPECTED_INPUT_SHA256:
        require(input_paths[key].is_file(), f"missing Stage-1 input: {key}")
        require(sha256(input_paths[key]) == EXPECTED_INPUT_SHA256[key], f"Stage-1 input SHA drift: {key}")
    require(input_paths["vendor"].is_dir(), "historical PyArrow vendor runtime missing")
    require(args.env_file.is_file(), "provider env file missing")
    require(args.runner.is_file(), "Stage-1 runner missing")

    original_f0 = load(input_paths["original_f0"])
    frozen = {row["task_id"]: row for row in design["frozen_source_units"]}
    pairs = {str(row["task_id"]): row for row in original_f0["pairs"]}
    require(set(frozen) == set(SOURCE_TASKS), "design source-task set drift")
    for task in SOURCE_TASKS:
        require(task in pairs, f"original F0 missing task {task}")
        require(pairs[task].get("success_memory_sha256") and pairs[task].get("failure_memory_sha256"), f"source task {task} is not an original complete F0 pair")
        require(pairs[task]["trajectory_summary_sha256"] == frozen[task]["trajectory_summary_sha256"], f"source trajectory binding drift: {task}")

    run_root = args.run_root.resolve()
    contract = {
        "schema_version": "1.0",
        "experiment_id": "D2-PROXY-O6-CROSS-WRITER-GLM53-STAGE1",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "status": "FROZEN_BEFORE_PROVIDER_CALLS",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_root": str(run_root),
        "human_authority": {
            "path": str(args.master_authority.resolve()),
            "sha256": sha256(args.master_authority),
            "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA256,
            "program_repair_authorized": True
        },
        "design": {"path": str(args.design.resolve()), "sha256": EXPECTED_DESIGN_SHA256},
        "code": {"runner": {"path": str(args.runner.resolve()), "sha256": sha256(args.runner)}},
        "source_artifacts": {
            key: {"path": str(path.resolve()), "sha256": EXPECTED_INPUT_SHA256[key]}
            for key, path in input_paths.items() if key in EXPECTED_INPUT_SHA256
        },
        "vendor_path": str(input_paths["vendor"].resolve()),
        "provider_env_file": str(args.env_file.resolve()),
        "source_tasks": SOURCE_TASKS,
        "source_bindings": [frozen[task] for task in SOURCE_TASKS],
        "conditions": ["success_label_memory", "failure_label_memory"],
        "expected_provider_calls": 8,
        "writer_model": stage1["writer_model"],
        "advance_to_stage2_if": stage1["advance_to_stage2_if"],
        "stage2_preregistered_gate": design["stage2_cross_writer_terminal_replication"]["support_if"],
        "authority": {
            "scientific_reopen_authority": True,
            "experiment_authority": True,
            "provider_call_authority": True,
            "gpu_authority": False,
            "claim_expansion_authority": False,
            "submission_authority": False
        }
    }
    contract_path = run_root / "o6-stage1-contract.json"
    atomic_json(contract_path, contract)
    receipt = {
        "schema_version": "1.0",
        "receipt_type": "scoped-experiment-authorization",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "experiment_id": contract["experiment_id"],
        "status": "O6_CROSS_WRITER_STAGE1_AUTHORIZED",
        "master_authority_sha256": sha256(args.master_authority),
        "design_sha256": EXPECTED_DESIGN_SHA256,
        "contract_sha256": sha256(contract_path),
        "runner_sha256": contract["code"]["runner"]["sha256"],
        "provider_call_ceiling": 8,
        "stage2_provider_calls_authorized_now": 0,
        "authority": contract["authority"]
    }
    atomic_json(run_root / "o6-stage1-authorization-receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "contract_sha256": receipt["contract_sha256"], "provider_call_ceiling": 8, "stage2_calls_now": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
