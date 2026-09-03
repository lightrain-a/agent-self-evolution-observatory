#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh4_source_20260903 as base
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file

ROOT = Path(__file__).resolve().parents[1]
STRESS_RESULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-fresh4-q08-transport-stress-20260903-v1/stress-result.json")
STRESS_RESULT_SHA = "09da6fe0dd7b9c9e07093522c23fa2c72446a3ed29e2e0725752542c642a7a07"
STRESS_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-fresh4-q08-transport-stress-closure-20260903.json"
STRESS_CLOSURE_SHA = "79e8f680796ec358cac50db5fff11997fd4985e13ed61feb06e8df8523d0b319"
Q08_CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-q08-successor-statistics-contract-20260903.json"
Q08_CONTRACT_SHA = "b523187e431ec952d0ba5d3a960ae878a5c8e421d5498c736ff557413184df6d"


def assert_q08_source_authority() -> dict[str, Any]:
    for path, expected, label in (
        (STRESS_RESULT, STRESS_RESULT_SHA, "stress result"),
        (STRESS_CLOSURE, STRESS_CLOSURE_SHA, "stress closure"),
        (Q08_CONTRACT, Q08_CONTRACT_SHA, "Q08 successor statistics contract"),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"STOP_FRESH4_Q08_SOURCE_AUTHORITY_HASH_DRIFT:{label}")
    result = json.loads(STRESS_RESULT.read_text())
    closure = json.loads(STRESS_CLOSURE.read_text())
    q08 = json.loads(Q08_CONTRACT.read_text())
    if (
        result.get("status") != "FRESH4_Q08_REPEATED_TURN_FINALIZATION_STRESS_PASS"
        or result.get("pass") is not True
        or result.get("attempted") != 8
        or result.get("required") != 8
        or result.get("nonfinal_passed") != 7
        or result.get("final_json_pass") is not True
        or result.get("total_model_rounds") != 8
        or result.get("prohibited_tool_attempts") != 0
        or result.get("scientific_source_tasks_used") != 0
        or result.get("fresh4_source_authorized") is not True
    ):
        raise RuntimeError("STOP_FRESH4_Q08_TRANSPORT_STRESS_NOT_QUALIFIED")
    authority = closure.get("authority") or {}
    if closure.get("status") != result.get("status") or authority.get("fresh4_scientific_source_acquisition") is not True:
        raise RuntimeError("STOP_FRESH4_Q08_SOURCE_AUTHORITY_CLOSURE_INVALID")
    if (
        q08.get("status") != "Q08_SUCCESSOR_STATISTICS_FROZEN_PRE_FRESH4"
        or (q08.get("fresh4_transport_precondition") or {}).get("required_before_any_scientific_source_acquisition") is not True
        or (q08.get("final_primary_metric") or {}).get("estimator") != "unbiased exact-match-kernel MMD2 / collision U-statistic"
        or (q08.get("threshold_calibration") or {}).get("selected_mean_D_select_threshold") != 0.2
    ):
        raise RuntimeError("STOP_FRESH4_Q08_SUCCESSOR_CONTRACT_INVALID")
    return {"stress_result_sha256": STRESS_RESULT_SHA, "stress_closure_sha256": STRESS_CLOSURE_SHA, "q08_contract_sha256": Q08_CONTRACT_SHA}


def prepare(root: Path, runtime_sha: str) -> dict[str, Any]:
    authority = assert_q08_source_authority()
    result = base.prepare(root, runtime_sha)
    contract_path = root / "contract.json"
    contract = json.loads(contract_path.read_text())
    contract["q08_successor_statistics_contract_sha256"] = Q08_CONTRACT_SHA
    contract["q08_transport_stress_result_sha256"] = STRESS_RESULT_SHA
    contract["q08_transport_stress_closure_sha256"] = STRESS_CLOSURE_SHA
    contract["q08_transport_precondition_pass"] = True
    contract["successor_final_primary_metric"] = "unbiased exact-match-kernel MMD2 / collision U-statistic"
    contract["successor_mean_D_select_threshold"] = 0.20
    from research_pipeline.c1_pacta_rb_qwen397 import atomic_json
    atomic_json(contract_path, contract)
    result["q08_authority"] = authority
    result["contract_sha256"] = sha256_file(contract_path)
    return result


def prelaunch(root: Path, runtime_sha: str) -> dict[str, Any]:
    assert_q08_source_authority()
    return base.prelaunch(root, runtime_sha)


def smoke(root: Path, runtime_sha: str) -> dict[str, Any]:
    assert_q08_source_authority()
    return base.smoke(root, runtime_sha)


def acquire(root: Path, runtime_sha: str) -> dict[str, Any]:
    assert_q08_source_authority()
    return base.acquire(root, runtime_sha)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=base.DEFAULT)
    parser.add_argument("--phase", choices=("prepare", "prelaunch", "smoke", "acquire"), required=True)
    parser.add_argument("--runtime-qualification-sha", required=True)
    args = parser.parse_args()
    fn = {"prepare": prepare, "prelaunch": prelaunch, "smoke": smoke, "acquire": acquire}[args.phase]
    result = fn(args.root, args.runtime_qualification_sha)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
