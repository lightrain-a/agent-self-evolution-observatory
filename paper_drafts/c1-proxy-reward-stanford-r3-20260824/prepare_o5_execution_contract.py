#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
OBJECTION_ID = "PROXY-O5"
AUTHORITY_TYPE = "human-c1-proxy-reward-stanford-repair-experiment-program"
EXPECTED_DESIGN_SHA256 = "4ba22e9dee9a753e6a2cf6e136259c0763f12f9503aef2ccc75285571b2817a9"
EXPECTED_SOURCE_MESSAGE_SHA256 = "7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62"
EXPECTED_INPUT_SHA256 = {
    "support": "b64635594251ac8f74251ea68b39a0c0c03b689b0708366be9c68ff193edd7ce",
    "parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "task_config": "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6",
    "evaluator": "f78eb61554c811f9411e7d72e0bdf2b5baa27379cbf632ade7fe49ce51a3f30d",
}
FUTURE_TASKS = ["164", "385", "387", "388"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile a fail-closed PROXY-O5 execution contract from external human authority.")
    ap.add_argument("--authority", required=True, type=Path)
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    ap.add_argument("--analysis", required=True, type=Path)
    ap.add_argument("--input-root", required=True, type=Path)
    ap.add_argument("--env-file", required=True, type=Path)
    ap.add_argument("--run-root", required=True, type=Path)
    args = ap.parse_args()

    authority_raw = args.authority.read_bytes()
    authority = json.loads(authority_raw.decode("utf-8"))
    design = json.loads(args.design.read_text(encoding="utf-8"))

    require(sha256(args.design) == EXPECTED_DESIGN_SHA256, "frozen O5 design SHA drift")
    require(authority.get("authority_type") == AUTHORITY_TYPE, "wrong human authority type")
    require(authority.get("decision") == "approve", "human authority is not approve")
    require(authority.get("reviewed_by") in {"user", "human-user"}, "authority reviewer is not the human user")
    require(authority.get("paper_id") == PAPER_ID, "authority paper mismatch")
    require(authority.get("source_message_sha256") == EXPECTED_SOURCE_MESSAGE_SHA256, "human source-message binding mismatch")
    require(authority.get("claim_expansion_authorized") is False, "master authority must not authorize claim expansion")
    require(authority.get("submission_authority") is False, "master authority must not authorize submission")
    require(authority.get("scientific_interpretation_authority") is False, "master authority must not pre-authorize scientific interpretation")

    o5 = authority.get("o5") or {}
    require(o5.get("objection_id") == OBJECTION_ID, "authority does not name PROXY-O5")
    require(o5.get("frozen_design_sha256") == EXPECTED_DESIGN_SHA256, "authority does not bind frozen O5 design")
    require(o5.get("provider_calls_authorized") is True, "O5 provider calls not authorized")
    require(int(o5.get("provider_call_ceiling") or 0) == 32, "O5 provider-call ceiling must be exactly 32")
    require(o5.get("single_frozen_attempt") is True, "O5 must remain a single frozen attempt")

    scientific = design["scientific_contract"]
    require(scientific["frozen_future_tasks"] == FUTURE_TASKS, "future task support drift")
    require(int(scientific["fresh_units"]["total_new_provider_calls"]) == 32, "design call-count drift")
    require(scientific["fresh_units"]["source_dimension_duplicated"] is False, "illegal source dimension in no-memory arm")
    require(scientific["fresh_units"]["existing_exploratory_no_memory_calls_reused"] == 0, "exploratory no-memory calls cannot enter O5")
    require(scientific["model"]["substitution_allowed"] is False, "model substitution must remain forbidden")
    require(scientific["model"]["provider_retries"] == 0, "provider retries must remain zero")

    input_paths = {
        "support": args.input_root / "generated/d2-proxy-reward-terminal-fixed-evidence-support.json",
        "parquet": args.input_root / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet",
        "task_config": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json",
        "evaluator": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py",
        "vendor": args.input_root / "generated/research-data/paper-yield-d5-c01/vendor",
    }
    for key in ("support", "parquet", "task_config", "evaluator"):
        require(input_paths[key].is_file(), f"missing frozen input: {key}")
        require(sha256(input_paths[key]) == EXPECTED_INPUT_SHA256[key], f"frozen input SHA drift: {key}")
    require(input_paths["vendor"].is_dir(), "historical vendor runtime missing")
    require(args.env_file.is_file(), "provider env file missing")
    require(args.runner.is_file(), "O5 runner missing")
    require(args.analysis.is_file(), "frozen O5 analysis missing")

    run_root = args.run_root.resolve()
    experiment_id = "D2-PROXY-O5-NO-MEMORY-CONFIRMATORY"
    contract = {
        "schema_version": "1.0",
        "experiment_id": experiment_id,
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "status": "FROZEN_BEFORE_PROVIDER_CALLS",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_root": str(run_root),
        "human_authority": {
            "path": str(args.authority.resolve()),
            "sha256": hashlib.sha256(authority_raw).hexdigest(),
            "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA256,
            "provider_calls_authorized": True,
            "provider_call_ceiling": 32,
        },
        "design": {"path": str(args.design.resolve()), "sha256": EXPECTED_DESIGN_SHA256},
        "code": {
            "runner": {"path": str(args.runner.resolve()), "sha256": sha256(args.runner)},
            "analysis": {"path": str(args.analysis.resolve()), "sha256": sha256(args.analysis)},
        },
        "source_artifacts": {
            key: {"path": str(path.resolve()), "sha256": EXPECTED_INPUT_SHA256[key]}
            for key, path in input_paths.items() if key in EXPECTED_INPUT_SHA256
        },
        "vendor_path": str(input_paths["vendor"].resolve()),
        "provider_env_file": str(args.env_file.resolve()),
        "future_tasks": FUTURE_TASKS,
        "condition": "no_memory",
        "rollouts_per_future_task": 8,
        "expected_provider_calls": 32,
        "model": scientific["model"],
        "evaluator_contract": scientific["evidence_and_evaluator"],
        "missingness_policy": scientific["missingness_policy"],
        "analysis_contract": design["analysis_contract"],
        "claim_boundary": design["claim_boundary"],
        "authority": {
            "scientific_reopen_authority": True,
            "experiment_authority": True,
            "provider_call_authority": True,
            "gpu_authority": False,
            "claim_expansion_authority": False,
            "submission_authority": False,
        },
    }
    contract_bytes = json.dumps(contract, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    contract_path = run_root / "o5-execution-contract.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_bytes(contract_bytes)
    contract_sha = hashlib.sha256(contract_bytes).hexdigest()

    receipt = {
        "schema_version": "1.0",
        "receipt_type": "scoped-experiment-authorization",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "experiment_id": experiment_id,
        "status": "O5_EXECUTION_AUTHORITY_VALID",
        "human_authority_sha256": hashlib.sha256(authority_raw).hexdigest(),
        "frozen_design_sha256": EXPECTED_DESIGN_SHA256,
        "execution_contract_sha256": contract_sha,
        "runner_sha256": contract["code"]["runner"]["sha256"],
        "analysis_sha256": contract["code"]["analysis"]["sha256"],
        "provider_call_ceiling": 32,
        "fresh_no_memory_only": True,
        "old_exploratory_calls_reused": 0,
        "authority": contract["authority"],
    }
    atomic_json(run_root / "o5-execution-authorization-receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "contract": str(contract_path), "contract_sha256": contract_sha, "receipt": str(run_root / "o5-execution-authorization-receipt.json"), "provider_call_ceiling": 32}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
