#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_evidence_window import (
    MatchedEvidenceWindowRenderer,
    TOKENIZER_ENCODING,
    TOKENIZER_PACKAGE,
    TOKENIZER_VERSION,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_reasoningbank_style import (
    RB_PINNED_COMMIT,
    render_rb_style_aggregation_prompt,
)
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    TrajectoryRef,
    project,
    validate_mixed_cloned_pair,
)

CONTRACT = ROOT / "generated/e2-r17-v3-runtime-pilot-contract-20260828.json"
V3 = ROOT / "generated/e2-r17-experiment-plan-v3-20260828.json"
ADJ = ROOT / "generated/e2-r17-experiment-plan-v3-review-adjudication-20260828.json"
EXPECTED_CONTRACT_STATUS = "AUTHORIZED_OUTCOME_BLIND_MECHANICAL_PILOT_ONLY"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def reconstruct_pool(payload: dict[str, Any]) -> SearchPool:
    rows = []
    fields = set(TrajectoryRef.__dataclass_fields__.keys())
    for row in payload["trajectories"]:
        rows.append(TrajectoryRef(**{key: row.get(key) for key in fields}))
    pool = SearchPool(
        pool_id=payload["pool_id"],
        task_id=payload["task_id"],
        k=int(payload["k"]),
        trajectories=tuple(rows),
        search_topology=payload["search_topology"],
    )
    pool.validate()
    return pool


def completed_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["unit_id"])] = row
    return rows


def verify_completed(row: dict[str, Any]) -> bool:
    path = Path(row["receipt_path"])
    return path.exists() and sha_file(path) == row["receipt_sha256"]


def append_manifest(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    args = parser.parse_args()

    started = time.monotonic()
    contract = load_json(args.contract)
    require(contract.get("status") == EXPECTED_CONTRACT_STATUS, "runtime pilot contract is not authorized")
    require(sha_file(V3) == contract["plan"]["sha256"], "V3 plan SHA drift")
    require(sha_file(ADJ) == contract["authority_parent"]["sha256"], "V3 review adjudication SHA drift")
    adj = load_json(ADJ)
    require(adj.get("status") == contract["authority_parent"]["required_status"], "V3 review adjudication status drift")
    require(adj["authority"]["outcome_blind_runtime_pilot"] is True, "runtime-pilot authority absent")
    require(adj["authority"]["e1_a_pool_generation"] is False, "contract must not inherit E1-A authority")
    require(adj["authority"]["e1_b_updater"] is False, "contract must not inherit E1-B authority")

    run_root = Path(contract["run_root"])
    raw_root = run_root / "raw/pools"
    checkpoint = run_root / "checkpoints/completed_units.jsonl"
    summary_path = run_root / "summary/runtime_pilot_summary.json"
    raw_root.mkdir(parents=True, exist_ok=True)

    e0_root = Path(contract["inputs"]["historical_e0_root"])
    e0_summary = e0_root / "e0_pilot_summary.json"
    require(sha_file(e0_summary) == contract["inputs"]["historical_e0_summary_sha256"], "historical E0 summary SHA drift")

    rb_root = Path(contract["inputs"]["reasoningbank_root"])
    rb_head = subprocess.run(["git", "-C", str(rb_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(rb_head == contract["inputs"]["reasoningbank_commit"] == RB_PINNED_COMMIT, "ReasoningBank commit drift")

    renderer = MatchedEvidenceWindowRenderer(cap_tokens=int(contract["frozen_renderer"]["cap_tokens"]))
    completed = completed_rows(checkpoint)
    for unit_id, row in completed.items():
        require(verify_completed(row), f"completed manifest SHA mismatch before resume: {unit_id}")

    pool_files = sorted((e0_root / "cases").glob("*/pool_k8.json"))
    require(len(pool_files) == 12, f"expected 12 historical E0 K8 pools, observed {len(pool_files)}")

    rendered_pair_tokens: list[int] = []
    rb_prompt_tokens: list[int] = []
    mixed_count = 0
    nonmixed_count = 0
    completed_now = 0
    reused = 0

    for pool_file in pool_files:
        pool_payload = load_json(pool_file)
        pool = reconstruct_pool(pool_payload)
        unit_id = pool.pool_id
        if unit_id in completed:
            reused += 1
            continue

        source_payloads: list[dict[str, Any]] = []
        source_shas: list[str] = []
        for trajectory in pool.trajectories:
            source_path = Path(trajectory.trajectory_path)
            observed_sha = sha_file(source_path)
            require(observed_sha == trajectory.trajectory_sha256, f"trajectory SHA mismatch: {source_path}")
            source_payloads.append(load_json(source_path))
            source_shas.append(observed_sha)

        win = project(pool, ProjectionName.WINNER_ONLY)
        mrw = project(pool, ProjectionName.MIXED_REJECTED_WITNESS)
        validate_mixed_cloned_pair(pool, win, mrw)
        if pool.mixed_pool:
            mixed_count += 1
            require(win.selected_indices != mrw.selected_indices, "MRW failed to differ on a mixed pool")
        else:
            nonmixed_count += 1
            require(win.selected_indices == mrw.selected_indices, "MRW differs outside mixed support")

        by_rollout = {int(payload["rollout_index"]): payload for payload in source_payloads}
        win_payload = by_rollout[win.slots[0].rollout_index]
        mrw_payload = by_rollout[mrw.slots[0].rollout_index]
        win_text = canonical_trajectory_text(win_payload)
        mrw_text = canonical_trajectory_text(mrw_payload)
        win_rendered, mrw_rendered, window_receipt = renderer.render_pair(win_text, mrw_text)
        win_tokens = renderer.encoding.encode(win_rendered)
        mrw_tokens = renderer.encoding.encode(mrw_rendered)
        require(len(win_tokens) == len(mrw_tokens) == window_receipt.matched_tokens, "WIN/MRW token parity failure")
        if not pool.mixed_pool:
            require(win_rendered == mrw_rendered, "nonmixed WIN/MRW evidence is not byte-identical")
        require("common system" not in win_rendered.lower(), "system text leaked into WIN evidence")

        rb_system, rb_user, rb_receipt = render_rb_style_aggregation_prompt(
            trajectory_payloads=source_payloads,
            trajectory_sha256s=source_shas,
            reasoningbank_root=rb_root,
            renderer=renderer,
        )
        require(len(rb_receipt.sources) == 8, "RB-AGG did not bind all eight source trajectories")
        require({row.verifier_label for row in rb_receipt.sources} <= {"SUCCESS", "FAILURE"}, "invalid RB verifier label")
        if pool.mixed_pool:
            require({row.verifier_label for row in rb_receipt.sources} == {"SUCCESS", "FAILURE"}, "mixed RB prompt lacks both labels")
        require(all(row.rendered_tokens <= 512 for row in rb_receipt.sources), "RB source token cap exceeded")

        # WIN-B is defined as a second updater invocation over the exact serialized
        # WIN-A input.  The runtime Pilot checks pre-provider byte identity only.
        win_a_input = json.dumps(
            {
                "pool_id": pool.pool_id,
                "acting_winner_sha256": win.acting_winner_sha256,
                "source_rollout": win.slots[0].rollout_index,
                "source_evidence": win_rendered,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        win_b_input = bytes(win_a_input, "utf-8").decode("utf-8")
        require(win_a_input == win_b_input, "WIN-A/WIN-B pre-provider serialization differs")

        rendered_pair_tokens.append(window_receipt.matched_tokens)
        rb_prompt_tokens.append(len(renderer.encoding.encode(rb_system + "\n" + rb_user)))
        receipt = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-v3-runtime-pilot-pool",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "unit_id": unit_id,
            "task_id": pool.task_id,
            "pool_file": str(pool_file),
            "pool_file_sha256": sha_file(pool_file),
            "pool_id": pool.pool_id,
            "mixed_pool": pool.mixed_pool,
            "winner_index": pool.winner.rollout_index,
            "mrw_index": mrw.slots[0].rollout_index,
            "win_mrw_source_different": win.selected_indices != mrw.selected_indices,
            "matched_window": window_receipt.to_dict(),
            "win_a_input_sha256": sha_bytes(win_a_input.encode("utf-8")),
            "win_b_input_sha256": sha_bytes(win_b_input.encode("utf-8")),
            "win_a_win_b_byte_identical": win_a_input == win_b_input,
            "rb_agg": rb_receipt.to_dict(),
            "rb_system_prompt_chars": len(rb_system),
            "rb_user_prompt_chars": len(rb_user),
            "rb_total_prompt_tokens": rb_prompt_tokens[-1],
            "provider_calls": 0,
            "scientific_effectiveness_evaluated": False,
        }
        receipt_path = raw_root / f"{pool.task_id}.json"
        atomic_json(receipt_path, receipt)
        manifest_row = {
            "unit_id": unit_id,
            "task_id": pool.task_id,
            "receipt_path": str(receipt_path),
            "receipt_sha256": sha_file(receipt_path),
        }
        append_manifest(checkpoint, manifest_row)
        completed[unit_id] = manifest_row
        completed_now += 1

    # Revalidate all manifest entries after write.
    for unit_id, row in completed.items():
        require(verify_completed(row), f"post-write completed manifest SHA mismatch: {unit_id}")

    # Non-destructive corruption detector simulation on a temporary copy.
    sample = next(iter(completed.values()))
    sample_path = Path(sample["receipt_path"])
    with tempfile.TemporaryDirectory() as temp:
        corrupt = Path(temp) / "corrupt.json"
        corrupt.write_bytes(sample_path.read_bytes() + b"\nCORRUPTION")
        corruption_detected = sha_file(corrupt) != sample["receipt_sha256"]
    require(corruption_detected, "SHA corruption simulation was not detected")

    # On a fully resumed run, recover token summaries from receipts.
    if reused and not rendered_pair_tokens:
        for row in completed.values():
            receipt = load_json(Path(row["receipt_path"]))
            rendered_pair_tokens.append(int(receipt["matched_window"]["matched_tokens"]))
            rb_prompt_tokens.append(int(receipt["rb_total_prompt_tokens"]))
            mixed_count += int(bool(receipt["mixed_pool"]))
            nonmixed_count += int(not bool(receipt["mixed_pool"]))

    def stats(values: list[int]) -> dict[str, Any]:
        ordered = sorted(values)
        return {
            "n": len(ordered),
            "min": ordered[0],
            "median": (ordered[(len(ordered)-1)//2] + ordered[len(ordered)//2]) / 2,
            "max": ordered[-1],
            "mean": sum(ordered) / len(ordered),
        }

    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-runtime-pilot-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_MECHANICAL_RUNTIME_PILOT",
        "contract": str(args.contract),
        "contract_sha256": sha_file(args.contract),
        "v3_plan_sha256": sha_file(V3),
        "authority_adjudication_sha256": sha_file(ADJ),
        "historical_e0_summary_sha256": sha_file(e0_summary),
        "reasoningbank_commit": rb_head,
        "tokenizer": {
            "package": TOKENIZER_PACKAGE,
            "version": TOKENIZER_VERSION,
            "encoding": TOKENIZER_ENCODING,
        },
        "pools": len(completed),
        "mixed_pools": mixed_count,
        "nonmixed_pools": nonmixed_count,
        "completed_now": completed_now,
        "reused_after_sha_validation": reused,
        "win_mrw_matched_tokens": stats(rendered_pair_tokens),
        "rb_style_total_prompt_tokens": stats(rb_prompt_tokens),
        "win_a_win_b_byte_identity": True,
        "corruption_detection_simulation": corruption_detected,
        "provider_calls": 0,
        "new_actor_rollouts": 0,
        "e1_pool_generation": 0,
        "scientific_effectiveness_evaluated": False,
        "wall_seconds": time.monotonic() - started,
        "next_authority": {
            "runtime_provider_budget_pilot": False,
            "e1_a": False,
            "e1_b": False,
        },
    }
    atomic_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
