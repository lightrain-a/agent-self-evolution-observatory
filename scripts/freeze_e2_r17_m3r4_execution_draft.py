#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_m3r4_execution_plan import (
    MAX_OUTPUT_TOKENS,
    MAX_TURNS,
    ORDER_SALT,
    PROVIDER_RETRY_LIMIT,
    REQUESTED_MODEL,
    REQUIRED_RESOLVED_MODEL,
    SCIENTIFIC_OBJECT,
    STATE_BINDINGS,
    TASK_IDS,
    TEMPERATURE,
    THINKING,
    canonical_sha256,
    order_manifest,
    sha256_file,
    structural_provider_budget,
    validate_state_bindings,
)


M3R4_PROTOCOL = ROOT / "generated/e2-r17-exact-evidence-frozen-state-regeneration-m3r4-proposal-20260904.md"
M3R4_PROTOCOL_SHA = "2ee4d928725fbb6a3dbe02b81ca4e8fcc69fe618c995593ed050e5e8c35381b6"
M3R4_REVIEW = ROOT / "generated/e2-r17-m3r4-preexecution-review-pass-20260904.json"
M3R4_REVIEW_SHA = "b9a6d50c9a84a16b11bbec92a74d987f7e62add1b1c63b6fd69f0acd5c167a32"
METRIC = ROOT / "research_pipeline/e2_r17_regeneration_metrics_v4.py"
METRIC_SHA = "998083d8e96254f634f609696fa3009792df9c198af8bffa3944a1229bf2620c"
OLD_IDENTITY = ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json"
OLD_IDENTITY_SHA = "491e4aa738260fab7c6331ee5a1e9a0d57b87df8411a01471c1df0564adf15ee"
RUNTIME_QUALIFICATION = ROOT / "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json"
RUNTIME_QUALIFICATION_SHA = "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b"
MINDMEMOS_ROOT = Path("/data/wyt/evidence-substrates/MindMemOS-20260817")
MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
ACTOR_PYTHON = Path("/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python")
RUNTIME_FREEZE = Path("/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt")
RUNTIME_FREEZE_SHA = "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e"
SUITE_ROOT = Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2")
SUITE_MANIFEST_SHA = "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
SPLIT_MANIFEST_SHA = "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9"
ENV_FILE = "/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/.env"
RUN_ROOT = "/data/wyt/e2-r17-search-projection/runs/m3r4-frozen-state-localization-20260904"
LEASE_PATH = "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-m3r4-frozen-state-localization-v1.json"
RECOVERY_V3_RUN_ROOT = "/data/wyt/e2-r17-search-projection/runs/single-case-constrained-state-micro-recovery2-v3-20260903"
RECOVERY_V3_LEASE = "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-single-case-constrained-state-micro-recovery2-v3.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _verify_static_inputs() -> None:
    require(M3R4_PROTOCOL.is_file() and sha256_file(M3R4_PROTOCOL) == M3R4_PROTOCOL_SHA, "M3R4 protocol drift")
    require(M3R4_REVIEW.is_file() and sha256_file(M3R4_REVIEW) == M3R4_REVIEW_SHA, "M3R4 review PASS drift")
    review = json.loads(M3R4_REVIEW.read_text(encoding="utf-8"))
    require(review.get("verdict") == "PASS_PREEXECUTION_DESIGN", "M3R4 independent preexecution review is not PASS")
    require((review.get("authority") or {}).get("m3r4_actor_execution") is False, "M3R4 review receipt must not carry actor authority")
    require(METRIC.is_file() and sha256_file(METRIC) == METRIC_SHA, "M3R4 metric drift")
    require(OLD_IDENTITY.is_file() and sha256_file(OLD_IDENTITY) == OLD_IDENTITY_SHA, "historical identity artifact drift")
    prior = json.loads(OLD_IDENTITY.read_text(encoding="utf-8"))
    require(prior.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "historical identity artifact status drift")
    adjudication = str(prior.get("adjudication") or "")
    require("must be requalified before any later scientific tranche" in adjudication, "historical identity artifact no longer records non-reusability")
    require(RUNTIME_QUALIFICATION.is_file() and sha256_file(RUNTIME_QUALIFICATION) == RUNTIME_QUALIFICATION_SHA, "actor runtime qualification drift")
    require(RUNTIME_FREEZE.is_file() and sha256_file(RUNTIME_FREEZE) == RUNTIME_FREEZE_SHA, "actor runtime freeze drift")
    require(ACTOR_PYTHON.is_file(), "actor python missing")
    require(SUITE_ROOT.joinpath("suite_manifest.json").is_file() and sha256_file(SUITE_ROOT / "suite_manifest.json") == SUITE_MANIFEST_SHA, "suite manifest drift")
    require(SUITE_ROOT.joinpath("r17_split_manifest.json").is_file() and sha256_file(SUITE_ROOT / "r17_split_manifest.json") == SPLIT_MANIFEST_SHA, "split manifest drift")
    observed_mindmemos = subprocess.check_output(["git", "-C", str(MINDMEMOS_ROOT), "rev-parse", "HEAD"], text=True).strip()
    require(observed_mindmemos == MINDMEMOS_COMMIT, "MindMemOS commit drift")
    validate_state_bindings()
    require(not Path(RUN_ROOT).exists(), "M3R4 run root must remain absent during zero-provider draft freeze")
    require(not Path(LEASE_PATH).exists(), "M3R4 lease must remain absent during zero-provider draft freeze")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order-output", type=Path, default=ROOT / "generated/e2-r17-m3r4-logical-unit-order-20260904.json")
    parser.add_argument("--contract-output", type=Path, default=ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json")
    args = parser.parse_args()

    _verify_static_inputs()
    order = order_manifest()
    atomic_json(args.order_output, order)
    order_sha = sha256_file(args.order_output)

    plan_path = ROOT / "research_pipeline/e2_r17_m3r4_execution_plan.py"
    plan_test_path = ROOT / "research_pipeline/test_e2_r17_m3r4_execution_plan.py"
    freeze_script_path = ROOT / "scripts/freeze_e2_r17_m3r4_execution_draft.py"
    budget = structural_provider_budget()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-execution-draft-contract",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "HOLD_FRESH_MODEL_IDENTITY_REQUALIFICATION_REQUIRED_ZERO_PROVIDER_PREP_ONLY",
        "scientific_object": SCIENTIFIC_OBJECT,
        "authority": {
            "scientific_experiment": False,
            "provider_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": False,
            "m4_bridge": False,
            "semantic_transfer": False,
            "e3": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "m3r4_protocol": {
            "path": str(M3R4_PROTOCOL.relative_to(ROOT)),
            "sha256": M3R4_PROTOCOL_SHA,
        },
        "independent_preexecution_review": {
            "path": str(M3R4_REVIEW.relative_to(ROOT)),
            "sha256": M3R4_REVIEW_SHA,
            "verdict": "PASS_PREEXECUTION_DESIGN",
            "execution_authority": False,
        },
        "scientific_scope": {
            "states": [row.state_id for row in STATE_BINDINGS],
            "state_count": 2,
            "task_ids": list(TASK_IDS),
            "task_count": 18,
            "actor_replicates_per_state_task": 2,
            "logical_units": 72,
            "new_learned_states": 0,
            "updater_calls": 0,
            "historical_actor_outcomes_in_gate": False,
            "historical_ff_hist_in_gate": False,
            "historical_win_common_in_gate": False,
            "analysis_metric": "E_REAL = D_X - D_A plus exact conditional state-label test",
        },
        "states": [asdict(row) for row in STATE_BINDINGS],
        "suite": {
            "root": str(SUITE_ROOT),
            "suite_manifest_sha256": SUITE_MANIFEST_SHA,
            "split_manifest_sha256": SPLIT_MANIFEST_SHA,
            "selected_panel_is_historical_outcome_selected": True,
            "population_sample_claimed": False,
        },
        "mindmemos": {
            "root": str(MINDMEMOS_ROOT),
            "commit": MINDMEMOS_COMMIT,
        },
        "actor_runtime": {
            "python_executable": str(ACTOR_PYTHON),
            "qualification_path": str(RUNTIME_QUALIFICATION.relative_to(ROOT)),
            "qualification_sha256": RUNTIME_QUALIFICATION_SHA,
            "freeze_path": str(RUNTIME_FREEZE),
            "freeze_sha256": RUNTIME_FREEZE_SHA,
        },
        "env_file": ENV_FILE,
        "actor": {
            "requested_model": REQUESTED_MODEL,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "temperature": TEMPERATURE,
            "thinking": THINKING,
            "k": 1,
            "max_turns": MAX_TURNS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "provider_retry_limit": PROVIDER_RETRY_LIMIT,
            "fresh_reset_runtime_per_logical_unit": True,
            "conversation_context_carryover": False,
        },
        "fresh_model_identity_gate": {
            "required_before_final_contract": True,
            "historical_identity_path": str(OLD_IDENTITY.relative_to(ROOT)),
            "historical_identity_sha256": OLD_IDENTITY_SHA,
            "historical_identity_reusable_for_m3r4": False,
            "reason": "Historical adjudication explicitly binds only its 2026-08-31 review tranche and requires requalification for any later scientific tranche.",
            "requested_model_must_remain": REQUESTED_MODEL,
            "resolved_model_must_remain": REQUIRED_RESOLVED_MODEL,
            "route_must_remain": "https://ark.cn-beijing.volces.com/api/plan/v3",
            "thinking_must_remain": THINKING,
            "provider_retry_limit_must_remain": 0,
            "max_output_tokens_smoke": MAX_OUTPUT_TOKENS,
            "if_resolved_identity_changes": "HOLD_REVIEW_REQUIRED_NO_AUTOMATIC_MODEL_SUBSTITUTION",
            "fresh_identity_artifact": None,
            "fresh_identity_sha256": None,
        },
        "logical_unit_order": {
            "path": str(args.order_output.relative_to(ROOT)),
            "sha256": order_sha,
            "logical_units_sha256": order["logical_units_sha256"],
            "order_salt": ORDER_SALT,
            "rule": order["ordering_rule"],
            "round_count": 4,
            "task_once_per_round": True,
            "round_treatment_counts": "4/4/5/5",
            "outcome_conditioned": False,
        },
        "provider_budget": budget,
        "inference_qualification": {
            "within_task_iid_stationarity_required_for_propensity_and_exact_test": True,
            "cross_task_conditional_factorization_required_for_binomial_tail": True,
            "detected_coupling_blocks_inference": True,
            "assumption_failure_automatic_rerun": False,
            "observed_e_real_descriptive_if_inference_blocked": True,
        },
        "resource_priority": {
            "recovery_v3_run_root": RECOVERY_V3_RUN_ROOT,
            "recovery_v3_lease": RECOVERY_V3_LEASE,
            "recovery_v3_currently_absent_at_draft_freeze": True,
            "rule": "Existing Recovery V3 scheduled continuation has priority after Ark quota reset. M3R4 provider authority must not compete with or pre-empt that recovery.",
            "m2_outcome_may_change_m3r4_design": False,
        },
        "run_root": RUN_ROOT,
        "lineage_lease_path": LEASE_PATH,
        "outcome_embargo": {
            "before_72_units_complete": True,
            "partial_effect_read": False,
            "analysis_authorized": False,
            "completed_unit_replay": False,
        },
        "bound_code": {
            "execution_plan": {"path": str(plan_path.relative_to(ROOT)), "sha256": sha256_file(plan_path)},
            "execution_plan_tests": {"path": str(plan_test_path.relative_to(ROOT)), "sha256": sha256_file(plan_test_path)},
            "draft_freezer": {"path": str(freeze_script_path.relative_to(ROOT)), "sha256": sha256_file(freeze_script_path)},
            "analysis_metric": {"path": str(METRIC.relative_to(ROOT)), "sha256": METRIC_SHA},
        },
        "git_commit_at_draft_freeze": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "next_gate": "FRESH_DEEPSEEK_MODEL_IDENTITY_REQUALIFICATION_AFTER_RESOURCE_PRIORITY_GATE_THEN_FINAL_CONTRACT_AND_ACTUAL_PATH_PREFLIGHT",
        "interpretation_boundary": "Zero-provider execution preparation only. This draft cannot reach actor/provider I/O. A fresh model-identity qualification, final content-addressed contract, actual-path zero-provider preflight, and separate explicit measurement authorization are still required.",
    }
    payload["draft_payload_sha256"] = canonical_sha256(payload)
    atomic_json(args.contract_output, payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "order_manifest": str(args.order_output),
                "order_manifest_sha256": order_sha,
                "logical_units_sha256": order["logical_units_sha256"],
                "draft_contract": str(args.contract_output),
                "draft_contract_sha256": sha256_file(args.contract_output),
                "logical_units": 72,
                "structural_provider_ceiling": budget["hard_max_provider_calls_structural"],
                "fresh_identity_required": True,
                "provider_authority": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
