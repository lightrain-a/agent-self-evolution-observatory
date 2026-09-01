from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    TrajectoryRef,
    append_pool_jsonl,
    pools_from_jsonl,
    project,
    project_stream,
    validate_cloned_streams,
    validate_mixed_cloned_pair,
    validate_mixed_cloned_streams,
    validate_primary_cloned_pair,
    write_stream_receipt,
)


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def trajectory(task: str, index: int, score: int, *, skill: str = "skill") -> TrajectoryRef:
    return TrajectoryRef(
        task_id=task,
        rollout_index=index,
        score=float(score),
        trajectory_path=f"/frozen/{task}/rollout_{index}.json",
        trajectory_sha256=digest(f"trajectory:{task}:{index}:{score}"),
        input_sha256=digest(f"input:{task}"),
        prompt_sha256=digest(f"prompt:{task}"),
        skill_pre_sha256=digest(skill),
        verifier_sha256=digest("verifier-v1"),
        requested_model="deepseek-v4-pro",
        resolved_model="deepseek-v4-pro-ga-260813",
        provider_call_id_sha256=digest(f"call:{task}:{index}"),
        evidence_tokens=100 + index,
        failure_code=None if score else "controlled_failure",
    )


def pool(task: str, scores: list[int], *, skill: str = "skill") -> SearchPool:
    return SearchPool.freeze([trajectory(task, index, score, skill=skill) for index, score in enumerate(scores)])


class SearchProjectionRunnerTest(unittest.TestCase):
    def test_winner_selector_is_score_then_lowest_index(self) -> None:
        p = pool("t", [0, 1, 1, 0])
        self.assertEqual(p.winner.rollout_index, 1)
        self.assertEqual(p.acting_success, 1.0)
        self.assertTrue(p.rescue_event)

    def test_rejected_witness_differs_only_on_rescue_event(self) -> None:
        rescue = pool("rescue", [0, 1, 0, 0])
        win = project(rescue, ProjectionName.WINNER_ONLY)
        rw = project(rescue, ProjectionName.REJECTED_WITNESS)
        validate_primary_cloned_pair(rescue, win, rw)
        self.assertEqual(win.selected_indices, (1,))
        self.assertEqual(rw.selected_indices, (0,))
        self.assertEqual(rw.slots[0].score, 0.0)

        for name, scores in (("all_success", [1, 1, 1, 1]), ("all_fail", [0, 0, 0, 0]), ("rollout0_success", [1, 0, 1, 0])):
            p = pool(name, scores)
            win = project(p, ProjectionName.WINNER_ONLY)
            rw = project(p, ProjectionName.REJECTED_WITNESS)
            validate_primary_cloned_pair(p, win, rw)
            self.assertEqual(win.selected_indices, rw.selected_indices)

    def test_mixed_rejected_witness_differs_on_any_mixed_pool(self) -> None:
        cases = (
            ("rescue", [0, 1, 0, 1], 0),
            ("rollout0_success", [1, 0, 1, 0], 1),
        )
        for name, scores, expected_failure_index in cases:
            p = pool(name, scores)
            self.assertTrue(p.mixed_pool)
            win = project(p, ProjectionName.WINNER_ONLY)
            mrw = project(p, ProjectionName.MIXED_REJECTED_WITNESS)
            validate_mixed_cloned_pair(p, win, mrw)
            self.assertEqual(mrw.selected_indices, (expected_failure_index,))
            self.assertEqual(mrw.slots[0].score, 0.0)
            self.assertNotEqual(win.selected_indices, mrw.selected_indices)

        for name, scores in (("all_success", [1, 1, 1, 1]), ("all_fail", [0, 0, 0, 0])):
            p = pool(name, scores)
            self.assertFalse(p.mixed_pool)
            win = project(p, ProjectionName.WINNER_ONLY)
            mrw = project(p, ProjectionName.MIXED_REJECTED_WITNESS)
            validate_mixed_cloned_pair(p, win, mrw)
            self.assertEqual(win.selected_indices, mrw.selected_indices)

    def test_precommitted_always_is_not_relabelled_no_censoring(self) -> None:
        p = pool("pre", [1, 0, 1, 0])
        pre = project(p, ProjectionName.PRECOMMITTED_ALWAYS)
        rw = project(p, ProjectionName.REJECTED_WITNESS)
        self.assertEqual(pre.selected_indices, (0,))
        self.assertEqual(rw.selected_indices, (0,))
        self.assertEqual(pre.projection, ProjectionName.PRECOMMITTED_ALWAYS)
        self.assertEqual(rw.projection, ProjectionName.REJECTED_WITNESS)

    def test_duplicate_and_random_controls_are_pool_bound(self) -> None:
        p = pool("controls", [0, 1, 0, 0])
        duplicate = project(p, ProjectionName.DUPLICATED_WINNER)
        random_a = project(p, ProjectionName.WINNER_RANDOM_NONWINNER)
        random_b = project(p, ProjectionName.WINNER_RANDOM_NONWINNER)
        contrast = project(p, ProjectionName.SKILLCAT_STYLE_CONTRAST)
        self.assertEqual(duplicate.selected_indices, (1, 1))
        self.assertEqual(random_a.packet_sha256, random_b.packet_sha256)
        self.assertEqual(random_a.selected_indices[0], p.winner.rollout_index)
        self.assertNotEqual(random_a.selected_indices[1], p.winner.rollout_index)
        self.assertEqual(contrast.selected_indices, (1, 0))
        allowed = {row.trajectory_sha256 for row in p.trajectories}
        for packet in (duplicate, random_a, contrast):
            self.assertTrue(all(slot.trajectory_sha256 in allowed for slot in packet.slots))

    def test_pool_rejects_cross_state_or_nonbinary_contamination(self) -> None:
        rows = [trajectory("bad", 0, 0, skill="a"), trajectory("bad", 1, 1, skill="b")]
        with self.assertRaisesRegex(ValueError, "skill_pre_sha256"):
            SearchPool.freeze(rows)
        bad = trajectory("bad-score", 0, 0)
        object.__setattr__(bad, "score", 0.5)
        with self.assertRaisesRegex(ValueError, "binary"):
            SearchPool.freeze([bad])

    def test_cloned_streams_share_exact_eight_pools(self) -> None:
        initial_skill = digest("skill")
        pools = [pool(f"stream-task-{index}", [0, 1, 0, 1, 0, 0, 0, 0]) for index in range(8)]
        winner = project_stream(
            stream_id="stream_00",
            initial_skill_sha256=initial_skill,
            pools=pools,
            projection=ProjectionName.WINNER_ONLY,
        )
        witness = project_stream(
            stream_id="stream_00",
            initial_skill_sha256=initial_skill,
            pools=pools,
            projection=ProjectionName.REJECTED_WITNESS,
        )
        validate_cloned_streams(winner, witness)
        self.assertNotEqual(winner.stream_sha256, witness.stream_sha256)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "receipt.json"
            write_stream_receipt(path, witness)
            self.assertTrue(path.exists())

    def test_mixed_cloned_streams_share_exact_eight_pools(self) -> None:
        initial_skill = digest("skill")
        pools = [
            pool(f"mixed-stream-task-{index}", [1, 0, 1, 1, 0, 1, 1, 1])
            for index in range(8)
        ]
        winner = project_stream(
            stream_id="mixed_stream_00",
            initial_skill_sha256=initial_skill,
            pools=pools,
            projection=ProjectionName.WINNER_ONLY,
        )
        witness = project_stream(
            stream_id="mixed_stream_00",
            initial_skill_sha256=initial_skill,
            pools=pools,
            projection=ProjectionName.MIXED_REJECTED_WITNESS,
        )
        validate_mixed_cloned_streams(winner, witness)
        self.assertTrue(all(pool_.mixed_pool for pool_ in pools))
        self.assertTrue(all(packet.slots[0].score == 0.0 for packet in witness.packets))

    def test_pool_jsonl_roundtrip_is_content_addressed(self) -> None:
        original = [pool("roundtrip-a", [0, 1]), pool("roundtrip-b", [1, 0])]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pools.jsonl"
            for item in original:
                append_pool_jsonl(path, item)
            restored = pools_from_jsonl(path)
        self.assertEqual([item.pool_id for item in original], [item.pool_id for item in restored])

    def test_stream_rejects_wrong_batch_size(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 8"):
            project_stream(
                stream_id="bad",
                initial_skill_sha256=digest("skill"),
                pools=[pool("only-one", [0, 1])],
                projection=ProjectionName.WINNER_ONLY,
            )


if __name__ == "__main__":
    unittest.main()
