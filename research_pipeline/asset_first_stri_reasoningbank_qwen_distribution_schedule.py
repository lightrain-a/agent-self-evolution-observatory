"""Deterministic balanced 432-unit confirmatory execution schedule."""
from __future__ import annotations

import hashlib
import random
from collections import Counter
from typing import Any, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import canonical_json, sha256_text

ARMS = ("A", "D", "N")
ROUNDS = 6


def schedule_seed(experiment_id: str, frozen_manifest_sha256: str) -> int:
    digest = hashlib.sha256(
        (experiment_id + "||" + frozen_manifest_sha256).encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:8], "big")


def build_schedule(task_ids: Sequence[str], *, experiment_id: str,
                   frozen_manifest_sha256: str) -> dict[str, Any]:
    tasks = list(task_ids)
    if len(tasks) != 24 or len(set(tasks)) != 24:
        raise ValueError("confirmatory schedule requires exactly 24 unique tasks")
    seed = schedule_seed(experiment_id, frozen_manifest_sha256)
    rng = random.Random(seed)
    units: list[dict[str, Any]] = []
    ordinal = 0
    for trial_round in range(1, ROUNDS + 1):
        task_order = list(tasks)
        rng.shuffle(task_order)
        for task_position, task_id in enumerate(task_order, start=1):
            arm_order = list(ARMS)
            rng.shuffle(arm_order)
            for within_task_position, arm in enumerate(arm_order, start=1):
                ordinal += 1
                units.append({
                    "ordinal": ordinal,
                    "run_id": f"QWEN-CONF-{ordinal:03d}",
                    "round": trial_round,
                    "task_position_within_round": task_position,
                    "arm_position_within_task": within_task_position,
                    "instance_id": task_id,
                    "arm": arm,
                    "attempt_count": 1,
                    "automatic_retry": False,
                    "replacement": False,
                })
    validate_schedule(units, tasks)
    return {
        "rng_seed": seed,
        "unit_count": len(units),
        "units": units,
        "schedule_sha256": sha256_text(canonical_json(units)),
        "execution_policy": {
            "exactly_once": True, "attempt_count": 1,
            "automatic_retry": False, "replacement": False,
            "global_order_immutable": True,
        },
    }


def validate_schedule(units: Sequence[dict[str, Any]],
                      task_ids: Sequence[str]) -> None:
    if len(units) != 432:
        raise ValueError("schedule must contain 432 units")
    if [row["ordinal"] for row in units] != list(range(1, 433)):
        raise ValueError("schedule ordinals are not contiguous")
    counts = Counter((row["instance_id"], row["arm"]) for row in units)
    if set(counts.values()) != {6} or len(counts) != len(task_ids) * 3:
        raise ValueError("each task-arm must occur exactly six times")
    if any(row["attempt_count"] != 1 or row["automatic_retry"] or row["replacement"]
           for row in units):
        raise ValueError("exactly-once policy drift")
    for trial_round in range(1, 7):
        rows = [row for row in units if row["round"] == trial_round]
        if len(rows) != 72:
            raise ValueError("each round must contain 72 units")
        if Counter(row["arm"] for row in rows) != Counter({"A": 24, "D": 24, "N": 24}):
            raise ValueError("round arm imbalance")
        for third in range(3):
            segment = rows[third * 24:(third + 1) * 24]
            if Counter(row["arm"] for row in segment) != Counter({"A": 8, "D": 8, "N": 8}):
                raise ValueError("early/middle/late arm imbalance")
