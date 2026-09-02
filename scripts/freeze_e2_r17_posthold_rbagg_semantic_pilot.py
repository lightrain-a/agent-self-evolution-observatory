#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = "FROZEN_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT"
RB_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
REQUESTED_MODEL = "deepseek-v4-pro"
RESOLVED_MODEL = "deepseek-v4-pro-ga-260813"
ROUTE = "https://ark.cn-beijing.volces.com/api/plan/v3"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def binding(path: Path) -> dict[str, str]:
    require(path.is_file(), f"missing bound file: {path}")
    return {"path": str(path if path.is_absolute() else path.relative_to(ROOT)), "sha256": sha_file(path)}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--env-file", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "semantic-pilot contract already exists")
    require(not args.run_root.exists(), "semantic-pilot run root already exists")
    require(args.env_file.is_file(), "semantic-pilot env file missing")

    parent_closeout_path = ROOT / "generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json"
    parent_contract_path = ROOT / "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json"
    support_path = ROOT / "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json"
    review_adj_path = ROOT / "generated/e2-r17-posthold-rbagg-review-adjudication-20260902.json"
    review_ds_path = ROOT / "generated/e2-r17-posthold-rbagg-review-20260902/deepseek-v4-pro.json"
    review_kimi_path = ROOT / "generated/e2-r17-posthold-rbagg-review-20260902/kimi-k3.json"
    semantic_preflight_path = ROOT / "generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json"
    actual_preflight_path = ROOT / "generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json"
    split_path = Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json")
    rb_root = Path("/data/wyt/e2-r17-search-projection/baselines/published/reasoning-bank")
    mind_root = Path("/data/wyt/evidence-substrates/MindMemOS-20260817")

    closeout = load_json(parent_closeout_path)
    review_adj = load_json(review_adj_path)
    support = load_json(support_path)
    split = load_json(split_path)
    parent_contract = load_json(parent_contract_path)
    require(closeout.get("status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent closeout status drift")
    require(review_adj.get("status") == "PASS_DUAL_REVIEW_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_PROPOSAL_ONLY", "RB review adjudication not passing")
    require(review_adj.get("authority", {}).get("provider_io") is False, "review artifact must not self-authorize provider I/O")
    require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "pool support status drift")
    fixed_stream = "e1-agj-00"
    task_ids = list(split["e1_update_streams"][fixed_stream])
    require(len(task_ids) == 8, "fixed semantic-pilot stream cardinality drift")
    pool_root = Path(parent_contract["e1_a_pool_root"])
    pool_sha = {}
    for task_id in task_ids:
        pool_path = pool_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.is_file(), f"missing fixed pool: {task_id}")
        observed = sha_file(pool_path)
        require(observed == support["pool_sha256"][task_id], f"fixed pool SHA drift: {task_id}")
        pool_sha[task_id] = observed

    rb_head = subprocess.run(["git", "-C", str(rb_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(rb_head == RB_COMMIT, "ReasoningBank commit drift")
    mind_head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(mind_head == parent_contract["mindmemos"]["commit"], "MindMemOS commit drift")

    bound_files = {
        "pilot_runner": binding(ROOT / "scripts/run_e2_r17_posthold_rbagg_semantic_pilot.py"),
        "pilot_preflight_runner": binding(ROOT / "scripts/preflight_e2_r17_posthold_rbagg_semantic_pilot.py"),
        "pilot_authorizer": binding(ROOT / "scripts/authorize_e2_r17_posthold_rbagg_semantic_pilot.py"),
        "rbagg_semantic_adapter": binding(ROOT / "research_pipeline/e2_r17_rbagg_posthold.py"),
        "rbagg_mindmemos_updater": binding(ROOT / "research_pipeline/e2_r17_rbagg_mindmemos_updater.py"),
        "reasoningbank_style_renderer": binding(ROOT / "research_pipeline/e2_r17_reasoningbank_style.py"),
        "mindmemos_ark_adapter": binding(ROOT / "research_pipeline/e2_r17_mindmemos_ark_adapter.py"),
        "provider_budget": binding(ROOT / "research_pipeline/e2_r17_provider_budget.py"),
        "actor_pool_loader": binding(ROOT / "research_pipeline/e2_r17_actor_pool.py"),
        "evidence_renderer": binding(ROOT / "research_pipeline/e2_r17_evidence_window.py"),
        "search_projection_runner": binding(ROOT / "research_pipeline/e2_r17_search_projection_runner.py"),
        "rbagg_tests": binding(ROOT / "research_pipeline/test_e2_r17_rbagg_posthold.py"),
        "parent_closeout": binding(parent_closeout_path),
        "parent_repair2_contract": binding(parent_contract_path),
        "pool_support": binding(support_path),
        "review_adjudication": binding(review_adj_path),
        "review_deepseek": binding(review_ds_path),
        "review_kimi": binding(review_kimi_path),
        "semantic_zero_provider_preflight": binding(semantic_preflight_path),
        "actual_path_zero_provider_preflight": binding(actual_preflight_path),
        "split_manifest": binding(split_path),
        "reasoningbank_memory_instruction": binding(rb_root / "WebArena/prompts/memory_instruction.py"),
        "reasoningbank_induce_scaling": binding(rb_root / "WebArena/induce_scaling.py"),
        "mindmemos_evolution": binding(mind_root / "src/mindmemos/mindmemos/pipelines/skill/evolution.py"),
        "mindmemos_skill_typing": binding(mind_root / "src/mindmemos/mindmemos/typing/skill.py"),
        "mindmemos_skill_patch_prompt": binding(mind_root / "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py"),
        "mindmemos_skill_mapper": binding(mind_root / "src/mindmemos/mindmemos/mappers/skill.py"),
    }

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-contract",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": STATUS,
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "run_root": str(args.run_root),
        "env_file": str(args.env_file),
        "preflight_path": "generated/e2-r17-posthold-rbagg-semantic-pilot-preflight-20260902.json",
        "inputs": {
            "parent_closeout_path": "generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json",
            "parent_closeout_sha256": sha_file(parent_closeout_path),
            "parent_repair2_contract_path": "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json",
            "parent_repair2_contract_sha256": sha_file(parent_contract_path),
            "pool_support_path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
            "pool_support_sha256": sha_file(support_path),
            "split_manifest_path": str(split_path),
            "split_manifest_sha256": sha_file(split_path),
            "review_adjudication_path": "generated/e2-r17-posthold-rbagg-review-adjudication-20260902.json",
            "review_adjudication_sha256": sha_file(review_adj_path),
            "review_deepseek_sha256": sha_file(review_ds_path),
            "review_kimi_sha256": sha_file(review_kimi_path),
            "semantic_preflight_sha256": sha_file(semantic_preflight_path),
            "actual_path_preflight_sha256": sha_file(actual_preflight_path),
        },
        "model": {
            "route": ROUTE,
            "requested_model": REQUESTED_MODEL,
            "required_resolved_model": RESOLVED_MODEL,
            "thinking": "disabled",
            "provider_retry_limit": 0,
            "identity_evidence": "fresh independent DeepSeek reviewer call resolved to the same exact model before pilot authorization",
        },
        "reasoningbank": {
            "root": str(rb_root),
            "commit": RB_COMMIT,
            "prompt": "PARALLEL_SI",
            "per_trajectory_cap_tokens": 512,
            "aggregator_temperature": 0.7,
            "aggregator_max_output_tokens": 1024,
            "strict_memory_item_count_min": 1,
            "strict_memory_item_count_max": 5,
            "source_faithful_reproduction": False,
        },
        "mindmemos": {
            "root": str(mind_root),
            "commit": mind_head,
            "summary_stage": "replaced by precomputed ReasoningBank-style search-session summaries",
            "direct_trajectory_summary_calls": 0,
            "patch_proposer": "PROPOSE_PATCH_SCORED_SYSTEM",
            "use_trajectory_score": True,
            "score_semantics": "K=8 search-session acting_success equal to WIN selected winner score",
            "min_aggregate": 8,
            "max_aggregate": 8,
            "rewrite_skill": False,
            "patch_temperature": 0.0,
            "max_parse_attempts": 2,
        },
        "pilot": {
            "fixed_stream": fixed_stream,
            "task_ids": task_ids,
            "pool_sha256": pool_sha,
            "aggregation_calls": 8,
            "mindmemos_nominal_calls": 2,
            "mindmemos_hard_max_calls": 3,
            "total_nominal_calls": 10,
            "total_hard_max_calls": 11,
            "heldout_evaluations": 0,
            "scientific_effectiveness_evaluated": False,
            "pilot_skill_scientific_inclusion": False,
            "pilot_skill_quarantined": True,
        },
        "provider_budget": {
            "total_limit": 11,
            "per_unit_limit": 11,
            "claim_before_provider_io": True,
            "claims_never_released": True,
        },
        "exactly_once": {
            "authorized_runs": 1,
            "automatic_retry": False,
            "replacement_sampling": False,
            "pilot_skill_scientific_inclusion": False,
            "run_root_must_be_absent": True,
        },
        "bound_files": bound_files,
        "authority": {
            "semantic_provider_pilot": False,
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "paper_promotion": False,
            "public_benchmark": False,
            "second_backbone": False,
        },
        "next_gate": "ZERO_PROVIDER_PREFLIGHT_THEN_SEPARATE_SINGLE_USE_AUTHORIZATION",
    }
    atomic_json(args.output, payload)
    print(json.dumps({"status": payload["status"], "fixed_stream": fixed_stream, "task_count": len(task_ids), "run_root": str(args.run_root), "authority": payload["authority"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
