#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    TrajectoryRef,
    canonical_sha256,
    project_stream,
)

ARMS = (
    ProjectionName.WINNER_ONLY,
    ProjectionName.PRECOMMITTED_ALWAYS,
    ProjectionName.REJECTED_WITNESS,
    ProjectionName.DUPLICATED_WINNER,
    ProjectionName.WINNER_RANDOM_NONWINNER,
    ProjectionName.SKILLCAT_STYLE_CONTRAST,
)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def bind_mindmemos(root: Path) -> None:
    for source in reversed(
        [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    ):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))


class FakeResponse:
    def __init__(self, *, content: str, parsed: Any = None) -> None:
        self.content = content
        self.parsed = parsed
        self.finish_reason = "completed"
        self.model = "fake-zero-provider"


class DeterministicUpdaterLLM:
    def __init__(self, initial_skill_md: str) -> None:
        self.initial_skill_md = initial_skill_md
        self.receipts: list[dict[str, Any]] = []
        self.plan_hash = ""

    async def chat(self, task: str, messages, format_parser=None, **kwargs):
        prompt = json.dumps(messages, ensure_ascii=False, sort_keys=True)
        if task == "skill_trajectory_summary":
            content = "summary-" + sha_text(prompt)[:20]
            parsed = None
        elif task == "skill_patch_propose":
            self.plan_hash = sha_text(prompt)[:20]
            content = f"append a qualification section keyed by {self.plan_hash}"
            parsed = None
        elif task == "skill_patch_apply":
            user = messages[-1]["content"]
            block = user.split("part of the file)\n", 1)[1].split("\n\n# Change plan", 1)[0]
            line_count = len(block.splitlines())
            new_skill = self.initial_skill_md.rstrip() + f"\n\n## Qualification Update\n\n- packet-plan: {self.plan_hash}\n"
            content = json.dumps(
                {"edits": [{"op": "replace", "start": 1, "end": line_count, "new": new_skill}]}
            )
            parsed = format_parser(content) if format_parser is not None else None
        else:
            raise AssertionError(f"unexpected first-party updater task: {task}")
        self.receipts.append(
            {
                "call_index": len(self.receipts),
                "task": task,
                "attempt": 0,
                "requested_model": "fake-zero-provider",
                "resolved_model": "fake-zero-provider",
                "prompt_sha256": sha_text(prompt),
                "response_sha256": sha_text(content),
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 2,
                "response_id_sha256": sha_text(f"fake-{len(self.receipts)}"),
                "provider_status": "completed",
                "thinking_requested": "disabled",
                "provider_retry_limit": 0,
                "message_count": len(messages),
                "parse_error": "",
                "record_path": None,
                "hidden_provider_retry_used": False,
            }
        )
        return FakeResponse(content=content, parsed=parsed)

    def public_receipts(self):
        return [dict(row) for row in self.receipts]

    @property
    def receipt_bundle_sha256(self):
        return canonical_sha256(self.receipts)


def write_trajectory(
    root: Path,
    task_id: str,
    rollout: int,
    score: float,
    *,
    skill_pre_sha256: str,
) -> TrajectoryRef:
    path = root / task_id / f"trajectory-{rollout}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "case_id": task_id,
        "rollout_index": rollout,
        "score": score,
        "score_message": "qualified",
        "messages": [
            {"role": "user", "content": f"perform {task_id}"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": f"call-{task_id}-{rollout}",
                        "type": "function",
                        "function": {
                            "name": "shell",
                            "arguments": json.dumps({"commands": [f"echo {task_id}-{rollout}"]}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": f"call-{task_id}-{rollout}",
                "name": "shell",
                "content": f"result-{task_id}-{rollout}",
            },
            {"role": "assistant", "content": "done"},
        ],
    }
    atomic_json(path, payload)
    common = {
        "input_sha256": sha_text(f"input-{task_id}"),
        "prompt_sha256": sha_text(f"prompt-{task_id}"),
        "skill_pre_sha256": skill_pre_sha256,
        "verifier_sha256": sha_text(f"verifier-{task_id}"),
        "requested_model": "fake-actor",
        "resolved_model": "fake-actor-v1",
    }
    return TrajectoryRef(
        task_id=task_id,
        rollout_index=rollout,
        score=score,
        trajectory_path=str(path.resolve()),
        trajectory_sha256=sha_file(path),
        provider_call_id_sha256=sha_text(f"call-{task_id}-{rollout}"),
        evidence_tokens=100 + rollout,
        technical_status="COMPLETED",
        failure_code="qualified_failure" if score < 1.0 else None,
        **common,
    )


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    bind_mindmemos(args.mindmemos_root)
    if args.run_root.exists():
        shutil.rmtree(args.run_root)
    trajectories_root = args.run_root / "synthetic-trajectories"
    initial_skill_path = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    initial_skill_md = initial_skill_path.read_text(encoding="utf-8")
    initial_skill_sha = sha_file(initial_skill_path)
    pools: list[SearchPool] = []
    for index in range(8):
        task_id = f"qualification-task-{index}"
        # Four rescue pools and four non-rescue success pools exercise both the
        # event-gated replacement and its equality outside the event.
        score0 = 0.0 if index < 4 else 1.0
        refs = (
            write_trajectory(
                trajectories_root,
                task_id,
                0,
                score0,
                skill_pre_sha256=initial_skill_sha,
            ),
            write_trajectory(
                trajectories_root,
                task_id,
                1,
                1.0,
                skill_pre_sha256=initial_skill_sha,
            ),
        )
        pools.append(SearchPool.freeze(refs))

    results: list[dict[str, Any]] = []
    post_hashes: dict[str, str] = {}
    for arm in ARMS:
        stream = project_stream(
            stream_id="qualification-stream",
            initial_skill_sha256=initial_skill_sha,
            pools=pools,
            projection=arm,
        )
        adapter = DeterministicUpdaterLLM(initial_skill_md)
        result = await run_projection_update(
            stream=stream,
            pools=pools,
            initial_skill_md=initial_skill_md,
            run_dir=args.run_root / "arms" / arm.value,
            llm_adapter=adapter,
            mindmemos_commit=args.mindmemos_commit,
            contract_sha256=sha_text("qualification-contract"),
            authorization_sha256=sha_text("qualification-zero-authority"),
        )
        receipt = json.loads(Path(result.update_receipt_path).read_text(encoding="utf-8"))
        checks = {
            "evolved": result.evolved,
            "one_new_version": len(result.new_version_ids) == 1,
            "eight_summaries": receipt.get("summarized_count") == 8,
            "eight_consumed": receipt.get("consumed_count") == 8,
            "ten_updater_calls": result.provider_calls == 10,
            "skill_content_addressed": sha_file(Path(result.skill_post_path)) == result.skill_post_sha256,
            "same_acting_scores": [row["acting_score"] for row in receipt["packets"]]
            == [pool.acting_success for pool in pools],
        }
        results.append(
            {
                "arm": arm.value,
                "checks": checks,
                "stream_sha256": stream.stream_sha256,
                "skill_post_sha256": result.skill_post_sha256,
                "update_receipt_sha256": result.update_receipt_sha256,
            }
        )
        post_hashes[arm.value] = result.skill_post_sha256

    global_checks = {
        "all_arms_pass": all(all(row["checks"].values()) for row in results),
        "winner_and_precommitted_diverge_on_rescue_stream": (
            post_hashes[ProjectionName.WINNER_ONLY.value]
            != post_hashes[ProjectionName.PRECOMMITTED_ALWAYS.value]
        ),
        "winner_and_rejected_witness_diverge_on_rescue_stream": (
            post_hashes[ProjectionName.WINNER_ONLY.value] != post_hashes[ProjectionName.REJECTED_WITNESS.value]
        ),
        "duplicate_and_skillcat_packets_are_not_collapsed": (
            post_hashes[ProjectionName.DUPLICATED_WINNER.value]
            != post_hashes[ProjectionName.SKILLCAT_STYLE_CONTRAST.value]
        ),
        "six_isolated_post_states": len(set(post_hashes.values())) == len(ARMS),
        "four_rescue_and_four_nonrescue_pools": sum(pool.rescue_event for pool in pools) == 4,
    }
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-cloned-state-first-party-updater-qualification",
        "status": "PASS_ZERO_PROVIDER" if all(global_checks.values()) else "FAIL",
        "mindmemos_commit": args.mindmemos_commit,
        "pools": [
            {
                "pool_id": pool.pool_id,
                "task_id": pool.task_id,
                "rescue_event": pool.rescue_event,
                "winner_index": pool.winner.rollout_index,
            }
            for pool in pools
        ],
        "arms": results,
        "global_checks": global_checks,
        "provider_calls": 0,
        "scientific_outcome": False,
        "authority": {
            "experiment": False,
            "gpu": False,
            "paper_promotion": False,
            "submission": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--mindmemos-commit", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = asyncio.run(main_async(args))
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_ZERO_PROVIDER" else 2


if __name__ == "__main__":
    raise SystemExit(main())
