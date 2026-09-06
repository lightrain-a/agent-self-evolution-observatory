from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import InsufficientMixedSupport
from research_pipeline.e2_r17_bridge_v4r2_stream_preparation import (
    STREAM_ARMS,
    prepare_stream_from_sealed_pools,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


INITIAL_MD = "skill"
INITIAL_SHA = h(INITIAL_MD)


def build_pool(root: Path, task_id: str, *, mixed: bool, all_failure: bool = False) -> SearchPool:
    if mixed:
        scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0)
    elif all_failure:
        scores = (0.0,) * 8
    else:
        scores = (1.0,) * 8
    rows: list[TrajectoryRef] = []
    task_root = root / task_id
    task_root.mkdir(parents=True, exist_ok=True)
    for index, score in enumerate(scores):
        payload = {
            "case_id": task_id,
            "rollout_index": index,
            "score": score,
            "score_message": "success" if score else "failed verification after stale worksheet operation",
            "messages": [
                {"role": "system", "content": "hidden common system prompt"},
                {
                    "role": "user",
                    "content": (
                        "Inspect the workbook, make the requested transformation, save output.xlsx, "
                        "reload output.xlsx, and verify the intended target values. "
                    ) * 6,
                },
                {
                    "role": "assistant",
                    "content": (
                        "I loaded the workbook and attempted the edit. "
                        + (
                            "I saved output.xlsx, reloaded output.xlsx, verified the target output, and completed the workflow. "
                            if score
                            else "A stale worksheet reference caused a tool error before a verified saved output; the call needs corrected arguments and retry. "
                        )
                    ) * 6,
                },
            ],
        }
        path = task_root / f"r{index}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        rows.append(
            TrajectoryRef(
                task_id=task_id,
                rollout_index=index,
                score=score,
                trajectory_path=str(path),
                trajectory_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                input_sha256=h(f"input|{task_id}"),
                prompt_sha256=h(f"prompt|{task_id}"),
                skill_pre_sha256=INITIAL_SHA,
                verifier_sha256=h("verifier"),
                requested_model="deepseek-v4-pro",
                resolved_model="deepseek-v4-pro-ga-260813",
                provider_call_id_sha256=h(f"call|{task_id}|{index}"),
                evidence_tokens=200,
            )
        )
    return SearchPool.freeze(rows)


def build_pools(root: Path, *, mixed_count: int = 6) -> tuple[SearchPool, ...]:
    return tuple(
        build_pool(
            root,
            f"r17-bridge-integrated-p{index}",
            mixed=index < mixed_count,
            all_failure=(index == 7 and index >= mixed_count),
        )
        for index in range(8)
    )


class BridgeV4R2StreamPreparationTests(unittest.TestCase):
    def test_integrated_object_covers_exact_six_scientific_arms(self) -> None:
        self.assertEqual(
            STREAM_ARMS,
            (
                "W_FREE",
                "W_COMP",
                "FF4_FREE",
                "FF4_COMP",
                "SCORE_ONLY_GENERIC_MAX",
                "SCOPE_MATCHED_GENERIC_MAX",
            ),
        )
        with tempfile.TemporaryDirectory() as td:
            prepared = prepare_stream_from_sealed_pools(
                stream_id="bridge-integrated-00",
                pools=build_pools(Path(td)),
                initial_skill_markdown=INITIAL_MD,
                initial_skill_sha256=INITIAL_SHA,
            )
        self.assertEqual(prepared.winner_package.projection, "WINNER")
        self.assertEqual(prepared.ff4_package.projection, "FIRST_FAIL_4")
        self.assertEqual(prepared.winner_updater_stream.projection, "WINNER")
        self.assertEqual(prepared.ff4_updater_stream.projection, "FIRST_FAIL_4")
        self.assertEqual(len(prepared.rendered.winner_free_units), 8)
        self.assertEqual(len(prepared.rendered.ff4_free_units), 8)
        self.assertEqual(len(prepared.state_sha256_by_deterministic_arm), 4)

    def test_free_and_comp_inputs_are_byte_and_score_identical_within_source_cell(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            prepared = prepare_stream_from_sealed_pools(
                stream_id="bridge-integrated-00",
                pools=build_pools(Path(td)),
                initial_skill_markdown=INITIAL_MD,
                initial_skill_sha256=INITIAL_SHA,
            )
        for free, comp in zip(prepared.rendered.winner_free_units, prepared.rendered.winner_compiler_units, strict=True):
            self.assertEqual(free.evidence_text, comp.evidence_text)
            self.assertEqual(free.evidence_sha256, comp.evidence_sha256)
            self.assertEqual(free.source_score, comp.selected_score)
        for free, comp in zip(prepared.rendered.ff4_free_units, prepared.rendered.ff4_compiler_units, strict=True):
            self.assertEqual(free.evidence_text, comp.evidence_text)
            self.assertEqual(free.evidence_sha256, comp.evidence_sha256)
            self.assertEqual(free.source_score, comp.selected_score)

    def test_ff4_controls_are_derived_only_from_ff4_scores_and_compiler_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            prepared = prepare_stream_from_sealed_pools(
                stream_id="bridge-integrated-00",
                pools=build_pools(Path(td)),
                initial_skill_markdown=INITIAL_MD,
                initial_skill_sha256=INITIAL_SHA,
            )
        self.assertIn(prepared.ff4_compiler_scope, (0, 1, 2))
        ff4_scores = tuple(unit.selected_score for unit in prepared.rendered.ff4_compiler_units)
        self.assertEqual(len(ff4_scores), 8)
        self.assertGreaterEqual(ff4_scores.count(0.0), 4)
        self.assertEqual(prepared.score_only_generic.diagnosis_sha256 != "", True)
        self.assertEqual(prepared.scope_matched_generic.diagnosis_sha256 != "", True)

    def test_preparation_is_content_deterministic_for_same_sealed_pools(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            a = prepare_stream_from_sealed_pools(
                stream_id="bridge-integrated-00",
                pools=pools,
                initial_skill_markdown=INITIAL_MD,
                initial_skill_sha256=INITIAL_SHA,
            )
            b = prepare_stream_from_sealed_pools(
                stream_id="bridge-integrated-00",
                pools=pools,
                initial_skill_markdown=INITIAL_MD,
                initial_skill_sha256=INITIAL_SHA,
            )
        self.assertEqual(a.preparation_sha256, b.preparation_sha256)
        self.assertEqual(a.state_sha256_by_deterministic_arm, b.state_sha256_by_deterministic_arm)

    def test_insufficient_mixed_support_stops_before_any_state_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(InsufficientMixedSupport, "HOLD_INSUFFICIENT_MIXED_SUPPORT"):
                prepare_stream_from_sealed_pools(
                    stream_id="bridge-integrated-00",
                    pools=build_pools(Path(td), mixed_count=3),
                    initial_skill_markdown=INITIAL_MD,
                    initial_skill_sha256=INITIAL_SHA,
                )

    def test_initial_skill_sha_is_load_bearing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "initial skill bytes/SHA drift"):
                prepare_stream_from_sealed_pools(
                    stream_id="bridge-integrated-00",
                    pools=build_pools(Path(td)),
                    initial_skill_markdown=INITIAL_MD,
                    initial_skill_sha256=h("different"),
                )


if __name__ == "__main__":
    unittest.main()
