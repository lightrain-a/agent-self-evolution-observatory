#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_evidence_window import MatchedEvidenceWindowRenderer
from research_pipeline.e2_r17_reasoningbank_style import (
    RB_AGGREGATOR_MAX_OUTPUT_TOKENS,
    RB_AGGREGATOR_TEMPERATURE,
    RB_PER_TRAJECTORY_CAP_TOKENS,
    RB_PINNED_COMMIT,
    render_rb_style_aggregation_prompt,
)
from research_pipeline.e2_r17_rbagg_posthold import (
    build_rb_aggregated_session_evidence,
    build_rb_precomputed_summary_payload,
    build_rb_search_session_add_payload,
    validate_rb_add_summary_pair,
)
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project

_ID_NS = uuid.UUID("24631de6-d366-445b-815d-f931786abb17")
_FIXTURE_MEMORY = """# Memory Item 1
## Title Verify the transformed artifact
## Description Re-check structural invariants after applying a workbook transformation.
## Content Inspect the relevant sheet, cells, formulas, and references after the edit before finalizing the result.

# Memory Item 2
## Title Re-resolve dependent references
## Description Treat structural edits as potentially invalidating downstream references.
## Content After inserting, moving, or rewriting cells, verify that dependent formulas and ranges still point to the intended locations."""


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def deterministic_add_id(stream_id: str, task_id: str, pool_id: str) -> str:
    return str(uuid.uuid5(_ID_NS, f"{stream_id}|{task_id}|{pool_id}|rbagg"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-closeout", type=Path, required=True)
    ap.add_argument("--parent-contract", type=Path, required=True)
    ap.add_argument("--support", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--reasoningbank-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    closeout = load_json(args.parent_closeout)
    contract = load_json(args.parent_contract)
    support = load_json(args.support)
    split = load_json(args.split)
    require(closeout.get("status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent closeout must remain HOLD")
    require(closeout.get("execution_authority", {}).get("rb_agg_rescue") is False, "parent unexpectedly authorizes RB rescue")
    require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "parent pool support not passing")
    require(contract.get("initial_skill", {}).get("sha256"), "parent initial skill binding missing")
    require(contract.get("e1_a_pool_root"), "parent pool root missing")

    mind_root = Path(contract["mindmemos"]["root"])
    for rel, expected in contract["mindmemos"]["bound_files"].items():
        path = mind_root / rel
        require(path.is_file() and sha_file(path) == expected, f"MindMemOS source drift: {rel}")
    require(contract["updater"]["score_semantics"] == "selected_evidence_trajectory", "parent score semantics drift")
    initial_skill_path = Path(contract["initial_skill"]["path"])
    require(initial_skill_path.is_file() and sha_file(initial_skill_path) == contract["initial_skill"]["sha256"], "initial skill drift")
    initial_skill_md = initial_skill_path.read_text(encoding="utf-8")

    rb_head = subprocess.run(
        ["git", "-C", str(args.reasoningbank_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(rb_head == RB_PINNED_COMMIT, "ReasoningBank commit drift")

    sys.path.insert(0, str(mind_root / "src/mindmemos"))
    from mindmemos.prompts.EN.skills.skill_patch import (  # type: ignore
        PROPOSE_PATCH_SCORED_SYSTEM,
        PROPOSE_PATCH_SYSTEM,
        propose_patch_user,
    )

    renderer = MatchedEvidenceWindowRenderer(cap_tokens=3072)
    pool_root = Path(contract["e1_a_pool_root"])
    streams: dict[str, list[str]] = split["e1_update_streams"]
    require(len(streams) == 12 and all(len(tasks) == 8 for tasks in streams.values()), "parent stream split drift")
    require(sum(len(v) for v in streams.values()) == 96, "parent update task cardinality drift")

    task_rows: list[dict[str, Any]] = []
    stream_rows: list[dict[str, Any]] = []
    total_rb_input_tokens = 0
    mixed_count = 0
    score_vector_equal_to_win = True

    for stream_id, task_ids in sorted(streams.items()):
        summary_texts: list[str] = []
        scores: list[float] = []
        for ordinal, task_id in enumerate(task_ids):
            pool_path = pool_root / "cases" / task_id / "pool_k8.json"
            require(pool_path.is_file(), f"missing frozen pool: {task_id}")
            require(sha_file(pool_path) == support["pool_sha256"][task_id], f"pool SHA drift: {task_id}")
            pool = load_frozen_pool(pool_path)
            require(pool.k == 8 and pool.task_id == task_id, f"pool identity drift: {task_id}")
            if pool.mixed_pool:
                mixed_count += 1

            source_payloads: list[dict[str, Any]] = []
            source_shas: list[str] = []
            for trajectory in pool.trajectories:
                source_path = Path(trajectory.trajectory_path)
                observed_sha = sha_file(source_path)
                require(observed_sha == trajectory.trajectory_sha256, f"trajectory SHA drift: {task_id}/{trajectory.rollout_index}")
                source_payloads.append(load_json(source_path))
                source_shas.append(observed_sha)

            rb_system, rb_user, rb_receipt = render_rb_style_aggregation_prompt(
                trajectory_payloads=source_payloads,
                trajectory_sha256s=source_shas,
                reasoningbank_root=args.reasoningbank_root,
                renderer=renderer,
            )
            require(len(rb_receipt.sources) == 8, f"RB source count drift: {task_id}")
            require(rb_receipt.per_trajectory_cap_tokens == RB_PER_TRAJECTORY_CAP_TOKENS == 512, "RB source cap drift")
            require(rb_receipt.aggregator_temperature == RB_AGGREGATOR_TEMPERATURE == 0.7, "RB temperature drift")
            require(rb_receipt.aggregator_max_output_tokens == RB_AGGREGATOR_MAX_OUTPUT_TOKENS == 1024, "RB output cap drift")
            rb_tokens = len(renderer.encoding.encode(rb_system + "\n" + rb_user))
            total_rb_input_tokens += rb_tokens

            win = project(pool, ProjectionName.WINNER_ONLY)
            win_score = float(win.slots[0].score)
            session_score = float(pool.acting_success)
            require(session_score == win_score, f"RB session score differs from WIN selected score: {task_id}")
            score_vector_equal_to_win = score_vector_equal_to_win and session_score == win_score

            aggregate = build_rb_aggregated_session_evidence(
                task_id=task_id,
                pool_id=pool.pool_id,
                acting_score=session_score,
                raw_memory_items=_FIXTURE_MEMORY,
                aggregation_receipt=rb_receipt.to_dict(),
            )
            add_id = deterministic_add_id(stream_id, task_id, pool.pool_id)
            add_payload = build_rb_search_session_add_payload(
                unit=aggregate,
                project_id=f"e2-r17-rbagg-preflight-{stream_id}",
                task_completed_at=f"2026-09-02T00:{ordinal:02d}:00+00:00",
                initial_skill_sha256=contract["initial_skill"]["sha256"],
                root_version_id="PREFLIGHT_ROOT_VERSION",
                deterministic_add_record_id=add_id,
            )
            summary_payload = build_rb_precomputed_summary_payload(
                unit=aggregate,
                project_id=f"e2-r17-rbagg-preflight-{stream_id}",
                cloud_skill_id=f"rbagg-{stream_id}",
                skill_name="xlsx",
                deterministic_add_record_id=add_id,
                created_at=datetime(2026, 9, 2, 0, ordinal, tzinfo=timezone.utc),
            )
            validate_rb_add_summary_pair(add_payload, summary_payload)
            summary_texts.append(summary_payload["summary"])
            scores.append(float(summary_payload["score"]))
            task_rows.append(
                {
                    "stream_id": stream_id,
                    "task_id": task_id,
                    "pool_id": pool.pool_id,
                    "pool_sha256": sha_file(pool_path),
                    "mixed_pool": pool.mixed_pool,
                    "acting_score": session_score,
                    "win_selected_score": win_score,
                    "score_equal_to_win": session_score == win_score,
                    "rb_prompt_sha256": sha_text(rb_system + "\n" + rb_user),
                    "rb_prompt_tokens": rb_tokens,
                    "rb_source_count": 8,
                    "rb_success_sources": sum(1 for row in rb_receipt.sources if float(row.verifier_score) == 1.0),
                    "rb_failure_sources": sum(1 for row in rb_receipt.sources if float(row.verifier_score) == 0.0),
                    "fixture_memory_sha256": aggregate.memory_items_sha256,
                    "add_record_id": add_id,
                    "add_summary_one_to_one": True,
                }
            )

        use_scores = any(score is not None for score in scores)
        require(use_scores, f"RB stream fell to unscored proposer: {stream_id}")
        user_prompt = propose_patch_user("xlsx", initial_skill_md, summary_texts, scores)
        require("Using the scores as the PRIMARY signal" in user_prompt, f"scored user prompt not selected: {stream_id}")
        require("There is no success/failure label" not in PROPOSE_PATCH_SCORED_SYSTEM, "scored system prompt semantic drift")
        require(PROPOSE_PATCH_SCORED_SYSTEM != PROPOSE_PATCH_SYSTEM, "scored/unscored systems unexpectedly identical")
        require(user_prompt.count("(score:") == 8, f"not all eight RB summaries are scored: {stream_id}")
        stream_rows.append(
            {
                "stream_id": stream_id,
                "task_ids": task_ids,
                "score_vector": scores,
                "score_vector_sha256": sha_text(json.dumps(scores, separators=(",", ":"))),
                "scored_patch_system_sha256": sha_text(PROPOSE_PATCH_SCORED_SYSTEM),
                "scored_patch_user_fixture_sha256": sha_text(user_prompt),
                "summary_count": 8,
                "mindmemos_scored_path": True,
            }
        )

    require(len(task_rows) == 96 and len(stream_rows) == 12, "RB preflight cardinality drift")
    require(mixed_count == int(support["primary_support"]["mixed_pools"]), "mixed count drift")
    require(score_vector_equal_to_win, "RB score vector is not exactly WIN-equivalent")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_RBAGG_ZERO_PROVIDER_SEMANTIC_ADAPTER_PREFLIGHT",
        "parent_closeout_path": str(args.parent_closeout),
        "parent_closeout_sha256": sha_file(args.parent_closeout),
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "parent_rbagg_rescue_authority": False,
        "parent_pool_support_path": str(args.support),
        "parent_pool_support_sha256": sha_file(args.support),
        "pool_root": str(pool_root),
        "pool_count": 96,
        "mixed_pool_count": mixed_count,
        "stream_count": 12,
        "tasks_per_stream": 8,
        "reasoningbank_commit": rb_head,
        "reasoningbank_prompt": "PARALLEL_SI",
        "reasoningbank_per_trajectory_cap_tokens": RB_PER_TRAJECTORY_CAP_TOKENS,
        "reasoningbank_aggregator_temperature": RB_AGGREGATOR_TEMPERATURE,
        "reasoningbank_aggregator_max_output_tokens": RB_AGGREGATOR_MAX_OUTPUT_TOKENS,
        "rb_prompt_input_tokens_total_over_96_pools": total_rb_input_tokens,
        "semantic_adapter": {
            "aggregate_role": "precomputed task-level K=8 search-session SkillTraceSummary; never represented as a single rollout trajectory",
            "source_record_cardinality": "one explicit search-session add record per task, one-to-one with its precomputed summary",
            "score_semantics": "frozen best-of-K search-session acting_success",
            "score_vector_exactly_equal_to_win_selected_winner_scores": score_vector_equal_to_win,
            "direct_trajectory_summarization_of_synthetic_session_record": "forbidden",
            "mindmemos_patch_proposer": "PROPOSE_PATCH_SCORED_SYSTEM",
            "mindmemos_patch_prompt_parser_config_changed": False,
            "aggregation_provider_layer_is_extra_and_separately_accounted": True,
            "reasoningbank_source_faithful_label": False,
        },
        "fixture_only_fields": {
            "memory_items_output_is_synthetic_fixture": True,
            "purpose": "strict parser/add-summary/scored-patch structural validation only; no semantic effectiveness or provider output was observed",
        },
        "task_receipts": task_rows,
        "stream_receipts": stream_rows,
        "provider_calls": 0,
        "aggregator_provider_calls": 0,
        "mindmemos_provider_calls": 0,
        "heldout_evaluations": 0,
        "scientific_effectiveness_evaluated": False,
        "authority": {
            "semantic_provider_pilot": False,
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "provider_io": False,
            "paper_promotion": False,
        },
        "next_gate": "INDEPENDENT_REVIEW_OF_SESSION_SCORE_SEMANTICS_AND_PRECOMPUTED_SUMMARY_ADAPTER_BEFORE_ANY_PROVIDER_IO",
    }
    require(not args.output.exists(), "RB semantic adapter preflight already exists; do not overwrite")
    atomic_json(args.output, payload)
    print(json.dumps({k: payload[k] for k in ["status", "pool_count", "mixed_pool_count", "stream_count", "provider_calls", "next_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
