#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
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

from research_pipeline.e2_r17_evidence_window_v2 import (
    TOKENIZER_ENCODING,
    TOKENIZER_PACKAGE,
    TOKENIZER_VERSION,
    ExactMatchedEvidenceBlockRenderer,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    build_blinded_add_record_payload,
)
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    TrajectoryRef,
    project,
    validate_mixed_cloned_pair,
)

EXPECTED_STATUS = "AUTHORIZED_ZERO_PROVIDER_MECHANICAL_PILOT_ONLY"
FORBIDDEN_VISIBLE_MARKERS = (
    "PROJECTION:",
    "ROLE:",
    "SOURCE_ROLLOUT_INDEX",
    "SOURCE_TRAJECTORY_SHA256",
    "WINNER_ONLY",
    "MIXED_REJECTED_WITNESS",
    "mixed_rejected_witness",
    "winner_only",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def reconstruct_pool(payload: dict[str, Any]) -> SearchPool:
    fields = set(TrajectoryRef.__dataclass_fields__.keys())
    trajectories = tuple(
        TrajectoryRef(**{key: row.get(key) for key in fields})
        for row in payload["trajectories"]
    )
    pool = SearchPool(
        pool_id=payload["pool_id"],
        task_id=payload["task_id"],
        k=int(payload["k"]),
        trajectories=trajectories,
        search_topology=payload["search_topology"],
    )
    pool.validate()
    return pool


def completed_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["unit_id"])] = row
    return rows


def verify_completed(row: dict[str, Any]) -> bool:
    receipt = Path(row["receipt_path"])
    return receipt.exists() and sha_file(receipt) == row["receipt_sha256"]


def check_bound_path(path: Path, expected_sha: str, label: str) -> None:
    require(path.exists(), f"missing bound {label}: {path}")
    require(sha_file(path) == expected_sha, f"SHA drift for {label}: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args()

    started = time.monotonic()
    contract = load_json(args.contract)
    require(contract.get("status") == EXPECTED_STATUS, "V3.1 mechanical pilot lacks execution authorization")
    authority = contract.get("authority") or {}
    require(authority.get("execute_mechanical_pilot") is True, "mechanical-pilot authority false")
    for forbidden_authority in ("provider_runtime_pilot", "e1_a", "e1_b", "paper_promotion", "submission"):
        require(authority.get(forbidden_authority) is False, f"forbidden inherited authority: {forbidden_authority}")

    for key in ("repair", "upstream_prompt_dataflow_audit", "review_adjudication"):
        bound = contract[key]
        check_bound_path(ROOT / bound["path"], bound["sha256"], key)

    renderer_cfg = contract["renderer"]
    check_bound_path(ROOT / renderer_cfg["path"], renderer_cfg["sha256"], "renderer")
    updater_cfg = contract["updater_wrapper"]
    check_bound_path(ROOT / updater_cfg["path"], updater_cfg["sha256"], "updater wrapper")
    check_bound_path(ROOT / updater_cfg["test_path"], updater_cfg["test_sha256"], "updater V3.1 tests")

    observed_tiktoken = importlib.metadata.version(TOKENIZER_PACKAGE)
    require(observed_tiktoken == TOKENIZER_VERSION == renderer_cfg["tokenizer_version"], "tokenizer version drift")
    require(TOKENIZER_ENCODING == renderer_cfg["tokenizer_encoding"], "tokenizer encoding drift")

    mind = contract["mindmemos"]
    mind_root = Path(mind["root"])
    head = subprocess.run(
        ["git", "-C", str(mind_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(head == mind["commit"], "MindMemOS commit drift")
    dirty = subprocess.run(
        ["git", "-C", str(mind_root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(not dirty, "MindMemOS pinned checkout is dirty")
    for rel, expected in mind["bound_files"].items():
        check_bound_path(mind_root / rel, expected, f"MindMemOS:{rel}")

    hist = contract["historical_inputs"]
    e0_root = Path(hist["e0_root"])
    e0_summary = Path(hist["e0_summary"])
    check_bound_path(e0_summary, hist["e0_summary_sha256"], "historical E0 summary")
    pool_files = sorted((e0_root / "cases").glob("*/pool_k8.json"))
    require(len(pool_files) == int(hist["expected_k8_pools"]), "historical K8 pool cardinality drift")

    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=int(renderer_cfg["final_block_cap_tokens"]))
    transcript_max_chars = int(updater_cfg["transcript_max_chars"])
    require(transcript_max_chars >= 100000, "V3.1 transcript limit must be nonbinding by contract")

    run_root = Path(contract["run_root"])
    raw_root = run_root / "raw/pools"
    checkpoint = run_root / "checkpoints/completed_units.jsonl"
    summary_path = run_root / "summary/runtime_pilot_summary.json"
    completed = completed_rows(checkpoint)
    for unit_id, row in completed.items():
        require(verify_completed(row), f"resume SHA mismatch: {unit_id}")

    completed_now = 0
    reused = 0
    matched_tokens: list[int] = []
    selected_budget_gaps: list[int] = []
    visible_chars: list[int] = []
    mixed_count = 0
    nonmixed_count = 0

    for pool_file in pool_files:
        pool_payload = load_json(pool_file)
        pool = reconstruct_pool(pool_payload)
        unit_id = pool.pool_id
        if unit_id in completed:
            reused += 1
            continue

        payloads: dict[int, dict[str, Any]] = {}
        trajectories: dict[int, TrajectoryRef] = {}
        for trajectory in pool.trajectories:
            source_path = Path(trajectory.trajectory_path)
            require(sha_file(source_path) == trajectory.trajectory_sha256, f"trajectory SHA drift: {source_path}")
            source_payload = load_json(source_path)
            index = int(source_payload["rollout_index"])
            require(index == trajectory.rollout_index, "trajectory rollout index drift")
            payloads[index] = source_payload
            trajectories[index] = trajectory

        win = project(pool, ProjectionName.WINNER_ONLY)
        mrw = project(pool, ProjectionName.MIXED_REJECTED_WITNESS)
        validate_mixed_cloned_pair(pool, win, mrw)
        if pool.mixed_pool:
            mixed_count += 1
            require(win.selected_indices != mrw.selected_indices, "MRW failed to differ on mixed support")
        else:
            nonmixed_count += 1
            require(win.selected_indices == mrw.selected_indices, "MRW changed outside mixed support")

        win_idx = win.slots[0].rollout_index
        mrw_idx = mrw.slots[0].rollout_index
        win_source = trajectories[win_idx]
        mrw_source = trajectories[mrw_idx]
        win_text = canonical_trajectory_text(payloads[win_idx])
        mrw_text = canonical_trajectory_text(payloads[mrw_idx])
        win_block, mrw_block, block_receipt = renderer.render_pair(win_text, mrw_text)
        win_actual = len(renderer.encoding.encode(win_block))
        mrw_actual = len(renderer.encoding.encode(mrw_block))
        require(win_actual == mrw_actual == block_receipt.matched_final_block_tokens, "actual final token parity failed")
        if not pool.mixed_pool:
            require(win_block == mrw_block, "nonmixed evidence is not byte-identical")

        for visible in (win_block, mrw_block):
            require(len(f"[user] {visible}") <= transcript_max_chars, "first-party transcript would truncate V3.1 evidence")
            for marker in FORBIDDEN_VISIBLE_MARKERS:
                require(marker not in visible, f"arm/provenance marker leaked into updater evidence: {marker}")

        win_unit = BlindedEvidenceUnit(
            task_id=pool.task_id,
            pool_id=pool.pool_id,
            acting_winner_sha256=pool.winner.trajectory_sha256,
            source_rollout_index=win_idx,
            source_trajectory_sha256=win_source.trajectory_sha256,
            source_score=float(win_source.score),
            evidence_text=win_block,
            evidence_sha256=sha_bytes(win_block.encode("utf-8")),
            evidence_tokens=win_actual,
        )
        mrw_unit = BlindedEvidenceUnit(
            task_id=pool.task_id,
            pool_id=pool.pool_id,
            acting_winner_sha256=pool.winner.trajectory_sha256,
            source_rollout_index=mrw_idx,
            source_trajectory_sha256=mrw_source.trajectory_sha256,
            source_score=float(mrw_source.score),
            evidence_text=mrw_block,
            evidence_sha256=sha_bytes(mrw_block.encode("utf-8")),
            evidence_tokens=mrw_actual,
        )
        common = {
            "pool": pool,
            "project_id": "v31-mechanical-internal-project",
            "task_completed_at": "2026-08-28T00:00:00+00:00",
            "initial_skill_sha256": pool.trajectories[0].skill_pre_sha256,
            "root_version_id": "v31-mechanical-root-version",
        }
        win_payload = build_blinded_add_record_payload(unit=win_unit, projection_label="winner_only", **common)
        mrw_payload = build_blinded_add_record_payload(unit=mrw_unit, projection_label="mixed_rejected_witness", **common)

        require(win_payload["messages"] == [{"role": "user", "content": win_block}], "WIN model-visible payload drift")
        require(mrw_payload["messages"] == [{"role": "user", "content": mrw_block}], "MRW model-visible payload drift")
        require(float(win_payload["score"]) == float(win_source.score), "WIN selected-evidence score drift")
        require(float(mrw_payload["score"]) == float(mrw_source.score), "MRW selected-evidence score drift")
        require(win_payload["r17_acting_score"] == mrw_payload["r17_acting_score"] == pool.acting_success, "acting score differs across clones")
        require(win_payload["r17_acting_winner_sha256"] == mrw_payload["r17_acting_winner_sha256"] == pool.winner.trajectory_sha256, "acting winner differs across clones")
        if not pool.mixed_pool:
            require(win_payload["messages"] == mrw_payload["messages"], "nonmixed model-visible messages differ")
            require(win_payload["score"] == mrw_payload["score"], "nonmixed model-visible scores differ")
        else:
            require(float(win_payload["score"]) == 1.0, "mixed WIN should expose successful winner score")
            require(float(mrw_payload["score"]) == 0.0, "mixed MRW should expose failed witness score")

        matched_tokens.append(win_actual)
        selected_budget_gaps.append(abs(block_receipt.left_selected_source_tokens - block_receipt.right_selected_source_tokens))
        visible_chars.extend([len(win_block), len(mrw_block)])
        receipt = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-v3-1-mechanical-pilot-pool",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "unit_id": unit_id,
            "task_id": pool.task_id,
            "pool_file": str(pool_file),
            "pool_file_sha256": sha_file(pool_file),
            "mixed_pool": pool.mixed_pool,
            "winner_index": win_idx,
            "mrw_index": mrw_idx,
            "matched_evidence": block_receipt.to_dict(),
            "win_model_visible_message_sha256": sha_bytes(json.dumps(win_payload["messages"], ensure_ascii=False, sort_keys=True).encode("utf-8")),
            "mrw_model_visible_message_sha256": sha_bytes(json.dumps(mrw_payload["messages"], ensure_ascii=False, sort_keys=True).encode("utf-8")),
            "win_selected_evidence_score": win_payload["score"],
            "mrw_selected_evidence_score": mrw_payload["score"],
            "acting_score_identical": win_payload["r17_acting_score"] == mrw_payload["r17_acting_score"],
            "acting_winner_identical": win_payload["r17_acting_winner_sha256"] == mrw_payload["r17_acting_winner_sha256"],
            "arm_metadata_visible_in_messages": False,
            "downstream_transcript_truncation": False,
            "provider_calls": 0,
            "new_actor_rollouts": 0,
            "scientific_effectiveness_evaluated": False
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

    for unit_id, row in completed.items():
        require(verify_completed(row), f"post-write completed receipt SHA mismatch: {unit_id}")

    if reused:
        matched_tokens = []
        selected_budget_gaps = []
        visible_chars = []
        mixed_count = 0
        nonmixed_count = 0
        for row in completed.values():
            receipt = load_json(Path(row["receipt_path"]))
            block = receipt["matched_evidence"]
            matched_tokens.append(int(block["matched_final_block_tokens"]))
            selected_budget_gaps.append(abs(int(block["left_selected_source_tokens"]) - int(block["right_selected_source_tokens"])))
            mixed_count += int(bool(receipt["mixed_pool"]))
            nonmixed_count += int(not bool(receipt["mixed_pool"]))

    sample = next(iter(completed.values()))
    with tempfile.TemporaryDirectory() as temp_dir:
        corrupt = Path(temp_dir) / "corrupt.json"
        source = Path(sample["receipt_path"])
        corrupt.write_bytes(source.read_bytes() + b"\nCORRUPTION")
        corruption_detected = sha_file(corrupt) != sample["receipt_sha256"]
    require(corruption_detected, "receipt corruption detector failed")

    def stats(values: list[int]) -> dict[str, Any]:
        ordered = sorted(values)
        return {
            "n": len(ordered),
            "min": ordered[0],
            "median": (ordered[(len(ordered) - 1) // 2] + ordered[len(ordered) // 2]) / 2,
            "max": ordered[-1],
            "mean": sum(ordered) / len(ordered),
        }

    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-1-mechanical-pilot-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_MECHANICAL_PILOT",
        "contract": str(args.contract),
        "contract_sha256": sha_file(args.contract),
        "repair_sha256": contract["repair"]["sha256"],
        "upstream_prompt_dataflow_audit_sha256": contract["upstream_prompt_dataflow_audit"]["sha256"],
        "review_adjudication_sha256": contract["review_adjudication"]["sha256"],
        "historical_e0_summary_sha256": sha_file(e0_summary),
        "mindmemos_commit": head,
        "tokenizer": {
            "package": TOKENIZER_PACKAGE,
            "version": observed_tiktoken,
            "encoding": TOKENIZER_ENCODING,
        },
        "pools": len(completed),
        "mixed_pools": mixed_count,
        "nonmixed_pools": nonmixed_count,
        "completed_now": completed_now,
        "reused_after_sha_validation": reused,
        "matched_final_tokens": stats(matched_tokens),
        "selected_source_budget_gap": stats(selected_budget_gaps),
        "exact_final_retokenized_parity": True,
        "nonmixed_model_visible_identity": True,
        "arm_metadata_visible_in_messages": False,
        "selected_evidence_score_semantics": True,
        "acting_provenance_identical_across_clones": True,
        "downstream_transcript_truncation": False,
        "corruption_detection_simulation": corruption_detected,
        "provider_calls": 0,
        "new_actor_rollouts": 0,
        "scientific_effectiveness_evaluated": False,
        "wall_seconds": time.monotonic() - started,
        "next_authority": {
            "provider_runtime_pilot": False,
            "e1_a": False,
            "e1_b": False,
            "paper_promotion": False
        }
    }
    atomic_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
