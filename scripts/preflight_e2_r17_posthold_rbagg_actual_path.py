#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_evidence_window import MatchedEvidenceWindowRenderer
from research_pipeline.e2_r17_reasoningbank_style import render_rb_style_aggregation_prompt
from research_pipeline.e2_r17_rbagg_mindmemos_updater import run_rbagg_update
from research_pipeline.e2_r17_rbagg_posthold import build_rb_aggregated_session_evidence

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


@dataclass
class _Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class _Response:
    content: str
    parsed: Any = None
    finish_reason: str = "completed"
    model: str = "FAKE_ZERO_PROVIDER"
    usage: _Usage = field(default_factory=_Usage)


class FakeNoProviderAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def chat(
        self,
        task: str,
        messages: list[dict[str, Any]],
        format_parser=None,
        *,
        feedback_on_parse_error: bool = False,
        **kwargs: Any,
    ) -> _Response:
        # If SkillEvolver unexpectedly calls trajectory summarization there would
        # be >2 calls and the task name would expose it; fail immediately.
        if "summary" in task.lower() or "trajectory" in task.lower():
            raise RuntimeError(f"RB actual-path preflight unexpectedly requested trajectory summary: {task}")
        if format_parser is None:
            content = "No edits are needed; the current skill already covers the fixture observations."
            parsed = None
        else:
            content = '{"edits": []}'
            parsed = format_parser(content)
        self.calls.append(
            {
                "task": task,
                "message_count": len(messages),
                "format_parser": format_parser is not None,
                "feedback_on_parse_error": bool(feedback_on_parse_error),
            }
        )
        return _Response(content=content, parsed=parsed)

    def public_receipts(self) -> list[dict[str, Any]]:
        return [
            {
                "call_index": i,
                "task": row["task"],
                "requested_model": "FAKE_ZERO_PROVIDER",
                "resolved_model": "FAKE_ZERO_PROVIDER",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "provider_status": "NOT_CALLED",
                "hidden_provider_retry_used": False,
            }
            for i, row in enumerate(self.calls)
        ]


async def run(args: argparse.Namespace) -> dict[str, Any]:
    closeout = load_json(args.parent_closeout)
    contract = load_json(args.parent_contract)
    support = load_json(args.support)
    split = load_json(args.split)
    semantic = load_json(args.semantic_preflight)
    require(closeout.get("status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent HOLD drift")
    require(semantic.get("status") == "PASS_RBAGG_ZERO_PROVIDER_SEMANTIC_ADAPTER_PREFLIGHT", "semantic preflight not passing")
    require(semantic.get("provider_calls") == 0, "semantic preflight crossed provider boundary")

    stream_id = sorted(split["e1_update_streams"])[0]
    task_ids = list(split["e1_update_streams"][stream_id])
    require(stream_id == "e1-agj-00" and len(task_ids) == 8, "fixed pilot stream selection drift")
    pool_root = Path(contract["e1_a_pool_root"])
    rb_root = args.reasoningbank_root
    renderer = MatchedEvidenceWindowRenderer(cap_tokens=3072)
    pools = []
    aggregates = []
    for task_id in task_ids:
        pool_path = pool_root / "cases" / task_id / "pool_k8.json"
        require(sha_file(pool_path) == support["pool_sha256"][task_id], f"pilot pool drift: {task_id}")
        pool = load_frozen_pool(pool_path)
        source_payloads = []
        source_shas = []
        for trajectory in pool.trajectories:
            path = Path(trajectory.trajectory_path)
            require(sha_file(path) == trajectory.trajectory_sha256, f"pilot trajectory drift: {task_id}/{trajectory.rollout_index}")
            source_payloads.append(load_json(path))
            source_shas.append(trajectory.trajectory_sha256)
        _, _, rb_receipt = render_rb_style_aggregation_prompt(
            trajectory_payloads=source_payloads,
            trajectory_sha256s=source_shas,
            reasoningbank_root=rb_root,
            renderer=renderer,
        )
        aggregates.append(
            build_rb_aggregated_session_evidence(
                task_id=task_id,
                pool_id=pool.pool_id,
                acting_score=float(pool.acting_success),
                raw_memory_items=_FIXTURE_MEMORY,
                aggregation_receipt=rb_receipt.to_dict(),
            )
        )
        pools.append(pool)

    initial_path = Path(contract["initial_skill"]["path"])
    require(sha_file(initial_path) == contract["initial_skill"]["sha256"], "initial skill drift")
    fake = FakeNoProviderAdapter()
    pilot_root = args.pilot_root
    require(not pilot_root.exists(), "RB actual-path preflight root already exists; do not replay")
    result = await run_rbagg_update(
        stream_id=stream_id,
        pools=pools,
        aggregates=aggregates,
        initial_skill_md=initial_path.read_text(encoding="utf-8"),
        initial_skill_sha256=contract["initial_skill"]["sha256"],
        run_dir=pilot_root,
        llm_adapter=fake,
        mindmemos_commit=contract["mindmemos"]["commit"],
        contract_sha256="ZERO_PROVIDER_PREFLIGHT_CONTRACT",
        authorization_sha256="ZERO_PROVIDER_PREFLIGHT_AUTHORIZATION",
        transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
    )
    receipt = load_json(Path(result.update_receipt_path))
    require(result.evolved, "RB actual-path preflight did not evolve")
    require(receipt["summary_count"] == 8, "RB actual-path summary count drift")
    require(receipt["new_first_party_trajectory_summaries"] == 0, "RB actual-path invoked trajectory summarization")
    require(receipt["precomputed_summary_consumed_count"] == 8, "RB actual-path did not consume all precomputed summaries")
    require(len(fake.calls) == 2, "RB actual-path must make exactly propose+apply fake calls")
    require(sum(1 for row in fake.calls if row["format_parser"]) == 1, "RB actual-path must exercise patch parser exactly once")
    post_text = Path(result.skill_post_path).read_text(encoding="utf-8")
    initial_text = initial_path.read_text(encoding="utf-8")
    require(post_text == initial_text.strip(), "fixture no-op patch changed semantic skill content")
    byte_change_is_trailing_whitespace_only = post_text != initial_text and post_text == initial_text.strip()

    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-zero-provider-actual-path-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_RBAGG_ZERO_PROVIDER_ACTUAL_MINDMEMOS_PATH",
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "semantic_preflight_path": str(args.semantic_preflight),
        "semantic_preflight_sha256": sha_file(args.semantic_preflight),
        "pilot_stream_id": stream_id,
        "pilot_task_count": 8,
        "precomputed_summary_count": 8,
        "first_party_trajectory_summary_calls": 0,
        "first_party_patch_interface_calls_fake": 2,
        "patch_parser_calls_fake": 1,
        "provider_calls": 0,
        "aggregator_provider_calls": 0,
        "mindmemos_provider_calls": 0,
        "heldout_evaluations": 0,
        "fixture_skill_semantically_unchanged": True,
        "fixture_skill_byte_change_is_trailing_whitespace_only": byte_change_is_trailing_whitespace_only,
        "update_receipt_path": result.update_receipt_path,
        "update_receipt_sha256": result.update_receipt_sha256,
        "skill_post_path": result.skill_post_path,
        "skill_post_sha256": result.skill_post_sha256,
        "direct_trajectory_summarization_forbidden_and_absent": True,
        "authority": {
            "semantic_provider_pilot": False,
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "provider_io": False,
            "paper_promotion": False,
        },
        "next_gate": "INDEPENDENT_REVIEW_THEN_SEPARATE_SINGLE_STREAM_SEMANTIC_PROVIDER_PILOT",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-closeout", type=Path, required=True)
    ap.add_argument("--parent-contract", type=Path, required=True)
    ap.add_argument("--support", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--semantic-preflight", type=Path, required=True)
    ap.add_argument("--reasoningbank-root", type=Path, required=True)
    ap.add_argument("--pilot-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "RB actual-path preflight artifact already exists")
    payload = asyncio.run(run(args))
    atomic_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
