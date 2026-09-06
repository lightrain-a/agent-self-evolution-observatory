from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_bridge_v4r2_stage_a_support import MIXED_PER_STREAM_MINIMUM, evaluate_screen_support
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def pool(task_id: str, *, mixed: bool) -> SearchPool:
    scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0) if mixed else (1.0,) * 8
    refs = tuple(
        TrajectoryRef(
            task_id=task_id,
            rollout_index=i,
            score=score,
            trajectory_path=f"/tmp/{task_id}/{i}.json",
            trajectory_sha256=h(f"traj|{task_id}|{i}"),
            input_sha256=h(f"input|{task_id}"),
            prompt_sha256=h(f"prompt|{task_id}"),
            skill_pre_sha256=h("skill"),
            verifier_sha256=h("verifier"),
            requested_model="deepseek-v4-pro",
            resolved_model="deepseek-v4-pro-ga-260813",
            provider_call_id_sha256=h(f"call|{task_id}|{i}"),
            evidence_tokens=100,
        )
        for i, score in enumerate(scores)
    )
    return SearchPool.freeze(refs)


def support_map(*, bad_stream: str | None = None, bad_mixed: int = 3) -> dict[str, tuple[SearchPool, ...]]:
    out = {}
    for sid in stage_stream_ids(SCREEN):
        n = bad_mixed if sid == bad_stream else 4
        out[sid] = tuple(pool(tid, mixed=i < n) for i, tid in enumerate(update_tasks(sid)))
    return out


class BridgeV4R2StageASupportTests(unittest.TestCase):
    def test_all_six_streams_with_four_mixed_pass(self) -> None:
        result = evaluate_screen_support(support_map())
        self.assertTrue(result.all_streams_qualified)
        self.assertEqual(len(result.streams), 6)
        self.assertTrue(all(row.mixed_pool_count == 4 and row.qualifies for row in result.streams))
        self.assertEqual(result.required_mixed_pools_per_stream, 4)
        self.assertFalse(result.replacement_allowed)

    def test_one_stream_with_three_mixed_holds_entire_stage(self) -> None:
        sid = stage_stream_ids(SCREEN)[2]
        result = evaluate_screen_support(support_map(bad_stream=sid, bad_mixed=3))
        self.assertFalse(result.all_streams_qualified)
        row = next(row for row in result.streams if row.stream_id == sid)
        self.assertEqual(row.mixed_pool_count, 3)
        self.assertFalse(row.qualifies)

    def test_support_threshold_is_frozen_at_four(self) -> None:
        self.assertEqual(MIXED_PER_STREAM_MINIMUM, 4)

    def test_stream_order_drift_is_rejected(self) -> None:
        mapping = support_map()
        reversed_mapping = dict(reversed(list(mapping.items())))
        with self.assertRaisesRegex(ValueError, "stream identity/order drift"):
            evaluate_screen_support(reversed_mapping)

    def test_task_order_drift_is_rejected(self) -> None:
        mapping = support_map()
        sid = stage_stream_ids(SCREEN)[0]
        mapping[sid] = tuple(reversed(mapping[sid]))
        with self.assertRaisesRegex(ValueError, "task order drift"):
            evaluate_screen_support(mapping)

    def test_stage_a_runtime_contains_no_state_or_heldout_execution_path(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("run_bridge_free_update", source)
        self.assertNotIn("materialize_actor_visible_state", source)
        self.assertNotIn("stage_heldout", source)
        self.assertIn('"updater_calls":0', source)
        self.assertIn('"heldout_actor_calls":0', source)


if __name__ == "__main__":
    unittest.main()
