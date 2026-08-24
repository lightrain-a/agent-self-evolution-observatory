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
EXPECTED_REPAIR_DESIGN_SHA = "19b3ea55704f4774405713f285b29d53f0ece7d78f9299fbb81ae86939f879b8"
EXPECTED_PARENT_DESIGN_SHA = "e33996f4e4f00da7b162bf7e9c26ca004aaf7e5d04f2547aacbc04f47ad05c1e"
EXPECTED_PARENT_CONTRACT_SHA = "7103efdbf1739638d815f9b0960462d7302821c91c063f42c5a6fcd331b46bfa"
EXPECTED_FAILURE_ASSET_SHA = "f7c204ea3f68a87082c729d5f6206077e04d995c93242af8baf8caa803bf7112"
EXPECTED_SOURCE_MESSAGE_SHA = "7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62"
EXPECTED_INPUT_SHA = {
    "parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "success_prompt": "5d4893a5f3dc5fadda43f166d6f322d729c197d8a8a74ca953f7c10acabb940a",
    "failure_prompt": "9bd01483afd8f8366ade02c7d839657d38f3eb263daa5cbfe15445b956116b45",
    "original_f0": "f2e4f3424faf1e3a9ec7aba7958e538eac457e89308552ef7a9c3d69c6a914f9",
}
SOURCE_TASKS = ["21", "22", "23", "25"]
TRAJECTORY_SUMMARY_SHA = {
    "21": "0697e64ba5a6c805cf0ce929ac1d947d2e884b75073c73ec63ec30f26156acab",
    "22": "ce3161ff3c47c24a5f96b109162935aa3d8126c47559aca38c6cd3c77c121446",
    "23": "4471ab8874a465680a66b48fe06b09633785d46fb549195b04d75e1d58646d23",
    "25": "9355929e90fb70ba7b554630fa21b93dfcc0117586a73cae1020782ace41444a",
}


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
    ap = argparse.ArgumentParser(description="Compile O6 GLM-5.3 Stage-1 R1 4096-token repair contract.")
    ap.add_argument("--master-authority", required=True, type=Path)
    ap.add_argument("--repair-design", required=True, type=Path)
    ap.add_argument("--parent-design", required=True, type=Path)
    ap.add_argument("--failure-asset", required=True, type=Path)
    ap.add_argument("--parent-run", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    ap.add_argument("--input-root", required=True, type=Path)
    ap.add_argument("--env-file", required=True, type=Path)
    ap.add_argument("--run-root", required=True, type=Path)
    args = ap.parse_args()

    require(sha(args.repair_design) == EXPECTED_REPAIR_DESIGN_SHA, "repair design SHA drift")
    require(sha(args.parent_design) == EXPECTED_PARENT_DESIGN_SHA, "parent design SHA drift")
    require(sha(args.failure_asset) == EXPECTED_FAILURE_ASSET_SHA, "failure asset SHA drift")
    require(sha(args.parent_run / "o6-stage1-contract.json") == EXPECTED_PARENT_CONTRACT_SHA, "parent contract SHA drift")
    repair = load(args.repair_design)
    failure = load(args.failure_asset)
    master = load(args.master_authority)

    require(repair["repair_id"] == "O6-CROSS-WRITER-STAGE1-R1-OUTPUT-CAP", "wrong repair id")
    require(repair["changed_scientific_variable"] == {"field": "writer_model.max_output_tokens", "parent": 2200, "repair": 4096, "rationale": repair["changed_scientific_variable"]["rationale"]}, "repair must change only output cap")
    require(repair["freshness"]["reuse_parent_successful_outputs"] is False and repair["freshness"]["fresh_provider_calls_if_complete"] == 8, "repair freshness drift")
    require(repair["stop_rule"]["further_output_cap_repairs_allowed"] is False, "repair budget must end after R1")
    require(repair["unchanged_contract"]["stage1_gate"] == {"all_8_provider_calls_complete": True, "exact_content_changed_pairs_min": 4, "title_set_changed_pairs_min": 3, "token_jaccard_threshold": None}, "Stage-1 gate drift")
    require(repair["unchanged_contract"]["stage2_gate"] == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05}, "Stage-2 gate drift")
    require(failure["scientific_decision"] == "STOP_PARENT_STAGE1_NO_STAGE2_AUTHORITY", "parent failure decision drift")
    require(failure["provider_incomplete"]["reason_counts"].get("length", 0) >= 2, "repair lacks repeated length-censoring evidence")
    require(failure["execution_concurrency_failure"]["parent_harness_transaction_lock_present"] is False, "unexpected parent concurrency state")

    require(master.get("authority_type") == AUTHORITY_TYPE and master.get("decision") == "approve" and master.get("reviewed_by") in {"user", "human-user"}, "master human authority invalid")
    require(master.get("paper_id") == PAPER_ID and master.get("source_message_sha256") == EXPECTED_SOURCE_MESSAGE_SHA, "master authority binding mismatch")
    future = master.get("future_repair_experiments") or {}
    require(future.get("human_program_authorized") is True and future.get("requires_per_experiment_preregistration") is True and future.get("requires_budget_and_stop_rule") is True, "C1 repair program authority insufficient")
    require(future.get("automatic_execution_without_frozen_subcontract") is False and future.get("outcome_driven_scope_expansion_authorized") is False, "master authority must remain fail-closed")
    require(master.get("provider_credential_use_authorized_if_required_by_a_frozen_subcontract") is True, "provider credential use not authorized")
    require(master.get("claim_expansion_authorized") is False and master.get("submission_authority") is False, "master authority scope expanded")

    input_paths = {
        "parquet": args.input_root / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet",
        "success_prompt": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_pass.md",
        "failure_prompt": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_fail.md",
        "vendor": args.input_root / "generated/research-data/paper-yield-d5-c01/vendor",
        "original_f0": Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f0-write-channel.json"),
    }
    for key in EXPECTED_INPUT_SHA:
        require(input_paths[key].is_file(), f"missing repair input: {key}")
        require(sha(input_paths[key]) == EXPECTED_INPUT_SHA[key], f"repair input SHA drift: {key}")
    require(input_paths["vendor"].is_dir(), "historical PyArrow vendor runtime missing")
    require(args.env_file.is_file(), "provider env file missing")
    require(args.runner.is_file(), "repair runner missing")

    old_f0 = load(input_paths["original_f0"])
    old_pairs = {str(row["task_id"]): row for row in old_f0["pairs"]}
    for task in SOURCE_TASKS:
        require(task in old_pairs and old_pairs[task].get("success_memory_sha256") and old_pairs[task].get("failure_memory_sha256"), f"original complete F0 pair missing: {task}")
        require(old_pairs[task]["trajectory_summary_sha256"] == TRAJECTORY_SUMMARY_SHA[task], f"trajectory summary binding drift: {task}")

    run_root = args.run_root.resolve()
    contract = {
        "schema_version": "1.0",
        "experiment_id": "D2-PROXY-O6-CROSS-WRITER-GLM53-STAGE1-R1-4096",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "repair_id": repair["repair_id"],
        "status": "FROZEN_BEFORE_PROVIDER_CALLS",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_root": str(run_root),
        "parent": {
            "design_path": str(args.parent_design.resolve()), "design_sha256": EXPECTED_PARENT_DESIGN_SHA,
            "contract_path": str((args.parent_run / "o6-stage1-contract.json").resolve()), "contract_sha256": EXPECTED_PARENT_CONTRACT_SHA,
            "failure_asset_path": str(args.failure_asset.resolve()), "failure_asset_sha256": EXPECTED_FAILURE_ASSET_SHA,
            "scientific_decision": failure["scientific_decision"]
        },
        "human_authority": {"path": str(args.master_authority.resolve()), "sha256": sha(args.master_authority), "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA},
        "design": {"path": str(args.repair_design.resolve()), "sha256": EXPECTED_REPAIR_DESIGN_SHA},
        "code": {"runner": {"path": str(args.runner.resolve()), "sha256": sha(args.runner)}},
        "source_artifacts": {key: {"path": str(path.resolve()), "sha256": EXPECTED_INPUT_SHA[key]} for key, path in input_paths.items() if key in EXPECTED_INPUT_SHA},
        "vendor_path": str(input_paths["vendor"].resolve()),
        "provider_env_file": str(args.env_file.resolve()),
        "source_tasks": SOURCE_TASKS,
        "source_bindings": [{"task_id": task, "trajectory_summary_sha256": TRAJECTORY_SUMMARY_SHA[task]} for task in SOURCE_TASKS],
        "conditions": ["success_label_memory", "failure_label_memory"],
        "expected_provider_calls": 8,
        "writer_model": {"requested": "glm-5.3", "temperature": 0.0, "max_output_tokens": 4096, "thinking": None, "provider_retries": 0, "store": True, "resolved_model_family_rule": "normalized resolved model starts with glm53", "substitution_allowed": False},
        "advance_to_stage2_if": repair["unchanged_contract"]["stage1_gate"],
        "stage2_preregistered_gate": repair["unchanged_contract"]["stage2_gate"],
        "repair_stop_rule": repair["stop_rule"],
        "execution_guards": {"single_writer_transaction_lock_required": True, "stop_after_first_incomplete": True, "response_first_archival_required": True},
        "authority": {"scientific_reopen_authority": True, "experiment_authority": True, "provider_call_authority": True, "gpu_authority": False, "claim_expansion_authority": False, "submission_authority": False}
    }
    contract_path = run_root / "o6-stage1-r1-contract.json"
    atomic_json(contract_path, contract)
    receipt = {
        "schema_version": "1.0", "receipt_type": "scoped-operationalization-repair-authorization",
        "paper_id": PAPER_ID, "objection_id": OBJECTION_ID, "repair_id": repair["repair_id"], "experiment_id": contract["experiment_id"],
        "status": "O6_STAGE1_R1_4096_AUTHORIZED", "master_authority_sha256": sha(args.master_authority),
        "repair_design_sha256": EXPECTED_REPAIR_DESIGN_SHA, "parent_failure_asset_sha256": EXPECTED_FAILURE_ASSET_SHA,
        "contract_sha256": sha(contract_path), "runner_sha256": contract["code"]["runner"]["sha256"],
        "provider_call_ceiling": 8, "stage2_provider_calls_authorized_now": 0, "further_output_cap_repairs_allowed": False,
        "authority": contract["authority"]
    }
    atomic_json(run_root / "o6-stage1-r1-authorization-receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "contract_sha256": receipt["contract_sha256"], "provider_call_ceiling": 8, "stage2_calls_now": 0, "further_output_cap_repairs_allowed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
