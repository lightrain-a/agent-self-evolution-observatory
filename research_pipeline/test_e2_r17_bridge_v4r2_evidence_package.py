from __future__ import annotations

import hashlib
import unittest

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import (
    FF4_ALLOCATION_SALT,
    InsufficientMixedSupport,
    build_ff4_package,
    build_winner_package,
    ff4_allocation_sha256,
    ff4_selected_pool_ids,
    validate_paired_packages,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pool(task_id: str, kind: str) -> SearchPool:
    if kind == "mixed":
        scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0)
    elif kind == "all_success":
        scores = (1.0,) * 8
    elif kind == "all_failure":
        scores = (0.0,) * 8
    else:
        raise ValueError(kind)
    rows = []
    for index, score in enumerate(scores):
        rows.append(
            TrajectoryRef(
                task_id=task_id,
                rollout_index=index,
                score=score,
                trajectory_path=f"/tmp/{task_id}/r{index}.json",
                trajectory_sha256=h(f"trajectory|{task_id}|{index}"),
                input_sha256=h(f"input|{task_id}"),
                prompt_sha256=h(f"prompt|{task_id}"),
                skill_pre_sha256=h("skill"),
                verifier_sha256=h("verifier"),
                requested_model="deepseek-v4-pro",
                resolved_model="deepseek-v4-pro-ga-260813",
                provider_call_id_sha256=h(f"call|{task_id}|{index}"),
                evidence_tokens=100 + index,
            )
        )
    return SearchPool.freeze(rows)


def stream_pools(mixed_count: int) -> tuple[SearchPool, ...]:
    kinds = ["mixed"] * mixed_count
    while len(kinds) < 8:
        kinds.append("all_failure" if len(kinds) % 2 else "all_success")
    # Preserve this non-semantic task order as the stream's frozen eight-pool aggregation order.
    task_order = ("p6", "p1", "p7", "p0", "p5", "p2", "p4", "p3")
    return tuple(pool(f"r17-bridge-test-{task}", kind) for task, kind in zip(task_order, kinds, strict=True))


class BridgeV4R2EvidencePackageTests(unittest.TestCase):
    def test_exact_frozen_hash_rule_selects_lowest_four_mixed_pools(self) -> None:
        stream = "bridge-test-00"
        pools = stream_pools(7)
        eligible = [row for row in pools if row.mixed_pool]
        expected = tuple(
            row.pool_id
            for row in sorted(
                eligible,
                key=lambda row: (ff4_allocation_sha256(stream, row.pool_id), row.pool_id),
            )[:4]
        )
        self.assertEqual(ff4_selected_pool_ids(stream, pools), expected)
        self.assertEqual(FF4_ALLOCATION_SALT, "E2-R17-BRIDGE-FF4-v1")

    def test_less_than_four_mixed_pools_holds_without_replacement(self) -> None:
        with self.assertRaisesRegex(InsufficientMixedSupport, "HOLD_INSUFFICIENT_MIXED_SUPPORT"):
            build_ff4_package("bridge-test-00", stream_pools(3))

    def test_five_to_eight_mixed_pools_still_get_exactly_four_replacements(self) -> None:
        for count in range(4, 9):
            ff4 = build_ff4_package("bridge-test-00", stream_pools(count))
            self.assertEqual(ff4.mixed_pool_count, count)
            self.assertEqual(ff4.ff4_replacement_count, 4)
            self.assertEqual(sum(unit.ff4_replaced for unit in ff4.units), 4)

    def test_replacement_is_deterministic_first_failed_nonwinner(self) -> None:
        pools = stream_pools(8)
        ff4 = build_ff4_package("bridge-test-00", pools)
        by_id = {row.pool_id: row for row in pools}
        for unit in ff4.units:
            source = by_id[unit.pool_id]
            if unit.ff4_replaced:
                self.assertEqual(unit.learner_rollout_index, source.first_failed_nonwinner.rollout_index)
                self.assertEqual(unit.learner_trajectory_sha256, source.first_failed_nonwinner.trajectory_sha256)
                self.assertEqual(unit.learner_score, 0.0)

    def test_winner_and_ff4_share_identical_served_winner_and_pool_order(self) -> None:
        pools = stream_pools(6)
        winner = build_winner_package("bridge-test-00", pools)
        ff4 = build_ff4_package("bridge-test-00", pools)
        validate_paired_packages(winner, ff4)
        self.assertEqual(winner.served_winner_sha256s, ff4.served_winner_sha256s)
        self.assertEqual(tuple(unit.pool_id for unit in winner.units), tuple(row.pool_id for row in pools))
        self.assertEqual(tuple(unit.pool_id for unit in ff4.units), tuple(row.pool_id for row in pools))
        for w, f in zip(winner.units, ff4.units, strict=True):
            if not f.ff4_replaced:
                self.assertEqual(f.learner_trajectory_sha256, w.learner_trajectory_sha256)

    def test_unchanged_winner_can_be_failure_outside_mixed_pool(self) -> None:
        pools = stream_pools(4)
        winner = build_winner_package("bridge-test-00", pools)
        ff4 = build_ff4_package("bridge-test-00", pools)
        validate_paired_packages(winner, ff4)
        unchanged_failure_units = [
            unit for unit in ff4.units if not unit.ff4_replaced and unit.learner_score == 0.0
        ]
        self.assertGreaterEqual(len(unchanged_failure_units), 1)

    def test_packages_are_content_addressed_and_repeat_deterministically(self) -> None:
        pools = stream_pools(7)
        w1 = build_winner_package("bridge-test-00", pools)
        w2 = build_winner_package("bridge-test-00", pools)
        f1 = build_ff4_package("bridge-test-00", pools)
        f2 = build_ff4_package("bridge-test-00", pools)
        self.assertEqual(w1.package_sha256, w2.package_sha256)
        self.assertEqual(f1.package_sha256, f2.package_sha256)
        self.assertNotEqual(w1.package_sha256, f1.package_sha256)

    def test_duplicate_pool_or_task_is_rejected(self) -> None:
        pools = list(stream_pools(5))
        pools[-1] = pools[0]
        with self.assertRaisesRegex(ValueError, "duplicate pool_id"):
            build_winner_package("bridge-test-00", pools)


if __name__ == "__main__":
    unittest.main()
