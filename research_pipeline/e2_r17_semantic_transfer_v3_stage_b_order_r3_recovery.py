from __future__ import annotations

import hashlib
from collections.abc import Iterable

ARMS = ("WIN-C", "MRW4")


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def update_pool_order(
    stream_id: str,
    replicate_index: int,
    task_ids: Iterable[str],
    *,
    expected_count: int,
) -> tuple[str, ...]:
    """Arm-blind update order for the R3 matched-censor geometry.

    Only 7 or 8 eligible Stage-A pool IDs are legal. The arm is deliberately
    absent from the ordering key, while task_id remains inside the key.
    """
    task_ids = tuple(str(task_id) for task_id in task_ids)
    if int(expected_count) not in (7, 8):
        raise ValueError("R3 Stage-B expected update count must be 7 or 8")
    if len(task_ids) != int(expected_count) or len(set(task_ids)) != int(expected_count):
        raise ValueError(f"R3 Stage-B update order requires exactly {expected_count} unique task IDs")
    return tuple(
        sorted(
            task_ids,
            key=lambda task_id: _digest(
                f"semantic-transfer-v3-update-order|{stream_id}|{int(replicate_index)}|{task_id}"
            ),
        )
    )


def state_arm_order(stream_id: str, replicate_index: int, arms: Iterable[str] = ARMS) -> tuple[str, ...]:
    arms = tuple(str(arm) for arm in arms)
    if set(arms) != set(ARMS) or len(arms) != 2:
        raise ValueError("R3 Stage-B arm schedule must contain WIN-C and MRW4 exactly once")
    return tuple(
        sorted(
            arms,
            key=lambda arm: _digest(
                f"semantic-transfer-v3-state-arm-order|{stream_id}|{int(replicate_index)}|{arm}"
            ),
        )
    )


def heldout_evaluation_schedule(
    stream_id: str,
    replicate_index: int,
    heldout_task_ids: Iterable[str],
    arms: Iterable[str] = ARMS,
) -> tuple[tuple[str, str], ...]:
    heldout = tuple(str(task_id) for task_id in heldout_task_ids)
    arms = tuple(str(arm) for arm in arms)
    if len(heldout) != 20 or len(set(heldout)) != 20:
        raise ValueError("R3 Stage-B heldout schedule requires exactly 20 unique heldout task IDs")
    if set(arms) != set(ARMS) or len(arms) != 2:
        raise ValueError("R3 Stage-B heldout schedule must contain WIN-C and MRW4 exactly once")
    pairs = [(task_id, arm) for task_id in heldout for arm in arms]
    return tuple(
        sorted(
            pairs,
            key=lambda pair: _digest(
                "semantic-transfer-v3-heldout-eval-order|"
                f"{stream_id}|{int(replicate_index)}|{pair[0]}|{pair[1]}"
            ),
        )
    )
