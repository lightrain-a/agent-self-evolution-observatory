from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

INVENTORY = PROJECT_ROOT / "research_pipeline" / "paper_first_c2_support_inventory_20260812.json"
SUPPORT_ADJUDICATION = PROJECT_ROOT / "research_pipeline" / "paper_first_c2_support_adjudication_20260812.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-c2-contract.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-c2-contract.js"

MODEL_PATH_60 = "/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct"
DATA_ROOT_60 = "/home/hdd/yutong/agent-evolution-p0-data"
PARENT_RUN_60 = DATA_ROOT_60 + "/runs/p0-mem-xfer-support-enriched-qwen-v1"
GPU_UUID_60 = "GPU-814cd021-31d8-2c6f-76a5-b8d4739b34d1"
PROVENANCE_AUTHORITY_60 = "/home/hdd/yutong/agent-evolution-c2-paperfirst/provenance-final-decision.json"
PROVENANCE_AUTHORITY_SHA256 = "ad283b1098943d725553e38020851f654b5ce8b70a2a362ce5958a56f197ef0e"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_c2_contract() -> dict[str, Any]:
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    strict = [row for row in inv["units"] if row.get("matched_hardware_route_exact") is True]
    if len(strict) != 10:
        raise ValueError(f"C2 strict pool must remain exactly 10, got {len(strict)}")
    sign_flip = inv["same_candidate_sign_flip_example"]
    adjudication = json.loads(SUPPORT_ADJUDICATION.read_text(encoding="utf-8"))
    synthesis = adjudication["synthesis"]
    if synthesis.get("decision") != "FREEZE_EXACT_10_UNIT_C2_RULE_PENDING_STRUCTURAL_PRECHECK":
        raise ValueError("C2 numeric rule is not frozen by the support-aware synthesis")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": "trajectory-mediated-memory-effect-transport",
        "stage": "C2-local-falsifier",
        "decision_before_execution": "C2_LOCAL_FALSIFIER_FROZEN",
        "scientific_role": "local mechanism falsifier only; cannot confirm the paper or authorize C3/full experiment",
        "source_inventory": {
            "path": str(INVENTORY.relative_to(PROJECT_ROOT)),
            "sha256": _sha(INVENTORY),
            "paper_level_nonzero": int(inv["paper_level_authority"]["stable_controlled_nonzero"]),
            "raw_nonzero": int(inv["summary"]["raw_controlled_nonzero_units"]),
            "strict_route_reproducible": len(strict),
            "paper_authority_raw_discrepancy": int(inv["summary"]["paper_authority_raw_discrepancy"]),
        },
        "runtime": {
            "host": "222.20.126.60",
            "gpu_uuid": GPU_UUID_60,
            "model_path": MODEL_PATH_60,
            "model_config_sha256": "7463bb0ea78315365e6c6b74de4e73bbcc8359dfb0c5a737584e077d42c0b03c",
            "model_index_sha256": "624bf7c47cd12468fdc16e38a47cf4f19e0415b859a223ba3c027eed2f0e1028",
            "python": "/home/hdd/yutong/envs/vlm_fp_231_exact/bin/python",
            "python_version": "3.11.15",
            "torch_version": "2.4.0+cu121",
            "transformers_version": "5.12.1",
            "textworld_version": "1.7.0",
            "extra_pythonpath": "/home/hdd/yutong/agent-evolution-p0-site",
            "adapter_sha256": "7cb65832fefd882e560f47acbc7e8df9629fa6322115c375bed3fe31b41e030b",
            "alfworld_data": DATA_ROOT_60 + "/alfworld",
            "parent_run": PARENT_RUN_60,
            "policy_class": "HFAdmissiblePolicy",
            "policy_mode": "react-family",
            "memory_patch": "",
            "max_total_steps": 50,
            "split": "eval_out_of_distribution",
            "parent_manifest_gpu_match_required": True,
            "provenance_authority_path": PROVENANCE_AUTHORITY_60,
            "provenance_authority_sha256": PROVENANCE_AUTHORITY_SHA256,
            "provenance_authority_expected_gpu_uuid": GPU_UUID_60,
            "provenance_authority_expected_model_path": MODEL_PATH_60,
            "runtime_provenance_caveat": "Matched-hardware R3 records GPU0/model but not a standalone Python path; use the nearest auditable parent runtime from pre-GPU/live-source audit: vlm_fp_231_exact. Any runtime-version or provenance-authority mismatch blocks C2.",
        },
        "estimand": {
            "A1": "retrieved-arm first-divergent action",
            "A0": "token-matched-placebo-arm first-divergent action",
            "common_state": "fresh reset plus exact shared retrieved/placebo action prefix",
            "continuation": "same frozen memory-free react-family Qwen policy pi0 on both arms",
            "tau": "success(do(A1), S*, pi0) - success(do(A0), S*, pi0)",
            "natural_indirect_effect_claimed": False,
            "context_rule": "pre-treatment/external frozen context only",
        },
        "strict_units": [row["unit_id"] for row in strict],
        "excluded_units": [
            {
                "unit_id": row["unit_id"],
                "reason": row.get("route_mismatch_reason") or "not route-exact",
            }
            for row in inv["units"]
            if row.get("matched_hardware_route_exact") is not True
        ],
        "preconditions": {
            "valid_units_required": 10,
            "common_prefix_exact": "10/10",
            "A0_A1_simultaneously_admissible": "10/10",
            "same_action_null": "For each unit, repeat the A0 branch twice and A1 branch twice from fresh reset; each repeated branch must have identical success, score, action sequence, and observation-sequence hash.",
            "pi0_consistency": "Every continuation uses the same model path/config, policy_mode=react-family, empty memory patch, max total 50 steps, and no cross-unit hidden state.",
            "pi0_support": "Both forced-action states must expose non-empty admissible commands unless already terminal; every continuation action must be selected from the current admissible set.",
            "failure_action": "Any failed unit sets valid_units<=9 and therefore C2_STOP; no unit replacement or threshold relaxation.",
        },
        "frozen_gate": {
            "review_source": "Conservative intersection of traceable support-aware DeepSeek-v4-pro and GLM-5.2 raw outputs before structural-precheck outcome opening; Web GPT missing due browser 502. AI is advisory and does not authorize C2.",
            "support_adjudication": {
                "path": str(SUPPORT_ADJUDICATION.relative_to(PROJECT_ROOT)),
                "sha256": _sha(SUPPORT_ADJUDICATION),
            },
            "claim_limit": "existence/local mechanism falsifier only; no population inference, no C3, no full experiment",
            "go": {
                "valid_units": int(synthesis["valid_units_required"]),
                "minimum_nonzero_tau_units": int(synthesis["minimum_nonzero_tau_units"]),
                "minimum_parent_sign_concordant_units": int(synthesis["minimum_parent_sign_concordant_units"]),
                "same_memory_cross_context_sign_reversal_required": bool(synthesis["same_memory_three_context_sign_pattern_required"]),
                "sign_flip_memory_id": sign_flip["memory_id"],
                "required_context_parent_signs": {
                    row["target_family"]: int(row["controlled_delta"])
                    for row in sign_flip["context_effects"]
                },
                "parent_sign_concordance_role": "binding GO gate from the conservative reviewer intersection",
                "all_conjunctive": True,
            },
            "stop": "valid_units<=9 OR nonzero_tau_units<=8 OR parent_sign_concordant_units<=8 OR required same-memory 3-context sign pattern is false",
            "no_threshold_relaxation": True,
            "no_unit_rescue": True,
            "no_new_full_table": True,
            "no_second_backbone": True,
        },
        "post_c2": {
            "C2_GO": "return to paper-design/AI adjudication before any certificate training",
            "C2_STOP": "stop or redesign the paper mechanism; do not open C3",
            "C3_locked": True,
            "local_validation_authorized": False,
            "full_experiment_authorized": False,
        },
    }


def write_c2_contract(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_c2_contract()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_C2_CONTRACT = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_c2_contract(), ensure_ascii=False, indent=2))
