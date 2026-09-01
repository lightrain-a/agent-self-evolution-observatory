#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARENT_CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json"
PARENT_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-authorization-20260831.json"
M1_CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
M1_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-single-use-authorization-20260831.json"
M1_PASS = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-recovery-pass-adjudication-20260831.json"
V3_COMPAT = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-compatibility-manifest-20260831.json"
V3_CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json"
V3_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json"
RUN_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-v3-20260831")
ENV_FILE = Path("/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/.env")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite frozen artifact: {path}")
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def bound(path: str) -> dict[str, str]:
    target = ROOT / path
    require(target.is_file(), f"bound file missing: {path}")
    return {"path": path, "sha256": sha_file(target)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    require(not RUN_ROOT.exists(), "V3 run root already exists")
    require(ENV_FILE.is_file(), "V3 absolute env file missing")
    m1_pass = load_json(M1_PASS)
    require(m1_pass.get("status") == "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS_INTEGRITY_AUDITED", "M1 integrity PASS missing")
    require(m1_pass.get("partial_effect_read") is False and m1_pass.get("analyzer_run") is False, "M1 outcome boundary drift")
    compatibility = load_json(V3_COMPAT)
    require(compatibility.get("status") == "PASS_REPAIR2_V3_PREFIX_COMPATIBILITY_15_COMPLETE_PAIRS", "V3 compatibility PASS missing")
    require(compatibility.get("partial_effect_read") is False and compatibility.get("analyzer_run") is False, "V3 compatibility outcome boundary drift")

    parent_contract = load_json(PARENT_CONTRACT)
    parent_auth = load_json(PARENT_AUTH)
    contract = copy.deepcopy(parent_contract)
    contract["artifact_type"] = "e2-r17-deepseek-v2-repair2-continuation-v3-contract"
    contract["status"] = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V3"
    contract["protocol_version"] = "repair2-continuation-v3"
    contract["purpose"] = "Continue the frozen DeepSeek V2 replicated paired experiment from an outcome-blind 15-pair prefix: 14 Repair1 inherited pairs plus one Repair2-M1 measurement-only recovered pair."
    contract["date"] = "2026-08-31"
    contract["env_file"] = str(ENV_FILE)
    contract["run_root"] = str(RUN_ROOT)
    contract["checkpoint"] = {
        "completed_replicates": str(RUN_ROOT / "checkpoints/completed_replicates.jsonl"),
        "valid_replicates": str(RUN_ROOT / "checkpoints/valid_replicates.jsonl"),
        "fail_closed": True,
        "resume_policy": "same V3 run root only; never replay a completed provider unit",
    }
    contract["compatibility_manifest"] = {
        "path": str(V3_COMPAT.relative_to(ROOT)),
        "sha256": sha_file(V3_COMPAT),
        "required_status": "PASS_REPAIR2_V3_PREFIX_COMPATIBILITY_15_COMPLETE_PAIRS",
    }
    contract["valid_replicate_manifest"] = {
        "path": str(RUN_ROOT / "checkpoints/valid_replicates.jsonl"),
        "required_rows": 48,
        "required_per_stream": 4,
        "allowed_sources": ["repair1_inherited", "repair2_m1_recovered", "repair2_v3_fresh"],
        "directory_discovery_forbidden": True,
        "quarantined_repair1_state_root_excluded": True,
        "m1_recovered_unit_allowed": "e1-fmv-01/rep2",
    }
    contract["inheritance_policy"] = {
        "outcome_blind": True,
        "frozen_prefix_pairs": 15,
        "repair1_inherited_pairs": 14,
        "repair2_m1_recovered_pairs": 1,
        "fresh_v3_pairs": 33,
        "scientific_scores_read": False,
        "partial_effect_read": False,
    }
    contract["continuation_state"] = {
        "before_v3": {
            "paired_units": 15,
            "learned_states": 30,
            "heldout_units": 540,
        },
        "remaining": {
            "fresh_pairs": 33,
            "new_learned_states": 66,
            "heldout_units": 1188,
        },
        "terminal": {
            "paired_units": 48,
            "learned_states": 96,
            "heldout_units": 1728,
        },
    }
    contract["repair2_stopped_parent"] = {
        "contract_path": str(PARENT_CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha_file(PARENT_CONTRACT),
        "authorization_path": str(PARENT_AUTH.relative_to(ROOT)),
        "authorization_sha256": sha_file(PARENT_AUTH),
        "terminal_state": "STOP_AND_ADJUDICATE_ACTOR_AUTHORIZATION_STATUS_SCHEMA_MISMATCH",
        "updater_calls_sealed": 20,
        "fresh_learned_states_recovered_by_m1": 2,
        "restart_forbidden": True,
    }
    contract["repair2_m1_parent"] = {
        "contract_path": str(M1_CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha_file(M1_CONTRACT),
        "authorization_path": str(M1_AUTH.relative_to(ROOT)),
        "authorization_sha256": sha_file(M1_AUTH),
        "pass_path": str(M1_PASS.relative_to(ROOT)),
        "pass_sha256": sha_file(M1_PASS),
        "recovered_pairs": 1,
        "learned_states": 2,
        "heldout_units": 36,
        "updater_calls": 0,
        "partial_effect_read": False,
    }
    contract["authority"] = {
        "scientific_experiment": False,
        "execute_deepseek_v2": False,
        "repair2_continuation_v3": False,
        "analyzer": False,
        "paper_promotion": False,
        "submission": False,
        "gpt_scientific_execution": False,
        "kimi_scientific_execution": False,
        "qwen_scientific_execution": False,
        "public_benchmark": False,
    }
    contract["exactly_once"] = {
        "single_v3_root": str(RUN_ROOT),
        "inherited_provider_replay": False,
        "new_pair_count": 33,
        "new_state_count": 66,
        "ambiguous_provider_response_retry": False,
        "completed_unit_replay": False,
    }
    contract["budget"]["states"] = 66
    contract["budget"]["hard_max_provider_calls_structural"] = 66 * int(contract["budget"]["max_provider_calls_per_state"])
    contract["bound_code"] = {
        "actor_runner_v3": bound("scripts/run_e2_r17_actor_pool_repair2_v3.py"),
        "runner_v3": bound("scripts/run_e2_r17_deepseek_v2_repair2_continuation_v3.py"),
        "preflight_v3": bound("scripts/preflight_e2_r17_deepseek_v2_repair2_v3.py"),
        "repair2_v3_manifest": bound("research_pipeline/e2_r17_repair2_v3_manifest.py"),
        "provider_budget": bound("research_pipeline/e2_r17_provider_budget.py"),
        "renderer": bound("research_pipeline/e2_r17_evidence_window_v2.py"),
        "updater_adapter": bound("research_pipeline/e2_r17_mindmemos_ark_adapter.py"),
        "updater_wrapper": bound("research_pipeline/e2_r17_mindmemos_updater.py"),
    }
    contract["forbidden"] = sorted(set(contract.get("forbidden") or []) | {
        "read any 15/48 partial effect",
        "run analyzer before 48/48 integrity completion",
        "replay 14 Repair1 inherited pairs",
        "replay the M1 recovered pair",
        "restart parent Repair2",
        "use quarantined Repair1 learned state",
        "change sample, model, prompt, K, tasks, arms, metric, or statistics",
    })
    for stale in ("review_binding", "test_adjudication", "freeze_note", "repair_note"):
        contract.pop(stale, None)
    atomic_json(V3_CONTRACT, contract)
    contract_sha = sha_file(V3_CONTRACT)

    authorization = copy.deepcopy(parent_auth)
    authorization["artifact_type"] = "e2-r17-deepseek-v2-repair2-continuation-v3-authorization"
    authorization["status"] = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_V3"
    authorization["contract_path"] = str(V3_CONTRACT.relative_to(ROOT))
    authorization["contract_sha256"] = contract_sha
    authorization["authorized_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    authorization["authority"] = {
        "scientific_experiment": True,
        "deepseek_v2": True,
        "e1_b": True,
        "repair2_continuation_v3": True,
        "mrw_causal_comparison": True,
        "analyzer": False,
        "paper_promotion": False,
        "submission": False,
        "frontend_promotion": False,
        "second_backbone": False,
        "gpt_scientific_execution": False,
        "kimi_scientific_execution": False,
        "qwen_scientific_execution": False,
        "public_benchmark": False,
    }
    scope = authorization["execution_scope"]
    scope["continuation_version"] = "repair2_v3"
    scope["env_file"] = str(ENV_FILE)
    scope["inherited_pairs"] = 15
    scope["repair1_inherited_pairs"] = 14
    scope["repair2_m1_recovered_pairs"] = 1
    scope["fresh_pairs"] = 33
    scope["new_learned_states"] = 66
    scope["new_heldout_units"] = 1188
    scope["run_root"] = str(RUN_ROOT)
    scope["compatibility_manifest_sha256"] = sha_file(V3_COMPAT)
    scope["partial_effect_read"] = False
    scope["analyzer"] = False
    authorization["repair_lineage"] = {
        "repair1_inherited_pairs": 14,
        "repair2_m1_recovered_pairs": 1,
        "repair2_v3_fresh_pairs": 33,
        "parent_repair2_contract_sha256": sha_file(PARENT_CONTRACT),
        "parent_repair2_authorization_sha256": sha_file(PARENT_AUTH),
        "m1_pass_sha256": sha_file(M1_PASS),
    }
    authorization["single_use"] = {
        "run_root": str(RUN_ROOT),
        "launch_count": 1,
        "completed_unit_replay": False,
        "ambiguous_provider_response_retry": False,
    }
    authorization["partial_effect_read"] = False
    authorization["analyzer_run"] = False
    authorization["scientific_variables_changed"] = False
    atomic_json(V3_AUTH, authorization)

    result = {
        "status": "FROZEN_AND_AUTHORIZED_REPAIR2_CONTINUATION_V3_NOT_STARTED",
        "contract_path": str(V3_CONTRACT),
        "contract_sha256": contract_sha,
        "authorization_path": str(V3_AUTH),
        "authorization_sha256": sha_file(V3_AUTH),
        "compatibility_manifest_sha256": sha_file(V3_COMPAT),
        "inherited_pairs": 15,
        "remaining_fresh_pairs": 33,
        "remaining_new_learned_states": 66,
        "remaining_heldout_units": 1188,
        "run_root_absent": not RUN_ROOT.exists(),
        "partial_effect_read": False,
        "analyzer_run": False,
        "provider_calls": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
