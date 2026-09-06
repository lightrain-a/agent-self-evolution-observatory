from __future__ import annotations

import hashlib
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import build_ff4_package, build_winner_package
from research_pipeline.e2_r17_bridge_v4r2_updater_binding import (
    build_bridge_updater_stream,
    run_bridge_free_update,
    validate_blinded_bridge_units,
)
from research_pipeline.e2_r17_mindmemos_updater import BlindedEvidenceUnit, ProjectionUpdateResult, sha_text
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


INITIAL = h("skill")


def make_pool(task: str, mixed: bool) -> SearchPool:
    scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0) if mixed else (1.0,) * 8
    rows = []
    for index, score in enumerate(scores):
        rows.append(
            TrajectoryRef(
                task_id=task,
                rollout_index=index,
                score=score,
                trajectory_path=f"/tmp/{task}/{index}.json",
                trajectory_sha256=h(f"trajectory|{task}|{index}"),
                input_sha256=h(f"input|{task}"),
                prompt_sha256=h(f"prompt|{task}"),
                skill_pre_sha256=INITIAL,
                verifier_sha256=h("verifier"),
                requested_model="deepseek-v4-pro",
                resolved_model="deepseek-v4-pro-ga-260813",
                provider_call_id_sha256=h(f"call|{task}|{index}"),
                evidence_tokens=100,
            )
        )
    return SearchPool.freeze(rows)


def pools() -> tuple[SearchPool, ...]:
    return tuple(make_pool(f"r17-bridge-updater-p{i}", mixed=i < 6) for i in range(8))


def blinded_from_package(ps: tuple[SearchPool, ...], package) -> tuple[BlindedEvidenceUnit, ...]:
    out = []
    for pool, row in zip(ps, package.units, strict=True):
        source = next(x for x in pool.trajectories if x.rollout_index == row.learner_rollout_index)
        text = f"E2-R17 SELECTED EXPERIENCE\n{pool.task_id}\nselected score {source.score}\n" + ("evidence " * 80)
        out.append(
            BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=source.rollout_index,
                source_trajectory_sha256=source.trajectory_sha256,
                source_score=source.score,
                evidence_text=text,
                evidence_sha256=sha_text(text),
                evidence_tokens=120,
            )
        )
    return tuple(out)


class BridgeV4R2UpdaterBindingTests(unittest.IsolatedAsyncioTestCase):
    def test_scientific_projection_label_is_separate_from_historical_projection_enum(self) -> None:
        ps = pools()
        w = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="WINNER",
        )
        f = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="FIRST_FAIL_4",
        )
        self.assertEqual(w.projection, "WINNER")
        self.assertEqual(f.projection, "FIRST_FAIL_4")
        self.assertNotIn("FIRST_FAIL_4", {str(x) for x in ProjectionName})
        self.assertTrue(all(packet.projection is ProjectionName.WINNER_ONLY for packet in f.packets))
        self.assertNotEqual(w.stream_sha256, f.stream_sha256)
        self.assertEqual(tuple(x.pool_id for x in w.pools), tuple(x.pool_id for x in f.pools))

    def test_ff4_blinded_units_bind_selected_failure_score_without_changing_served_winner(self) -> None:
        ps = pools()
        package = build_ff4_package("bridge-updater-00", ps)
        units = blinded_from_package(ps, package)
        stream = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="FIRST_FAIL_4",
        )
        validate_blinded_bridge_units(stream=stream, units=units)
        replaced = [
            (pool, row, unit)
            for pool, row, unit in zip(ps, package.units, units, strict=True)
            if row.ff4_replaced
        ]
        self.assertEqual(len(replaced), 4)
        for pool, _, unit in replaced:
            self.assertEqual(pool.winner.score, 1.0)
            self.assertEqual(unit.source_score, 0.0)
            self.assertEqual(unit.acting_winner_sha256, pool.winner.trajectory_sha256)

    def test_winner_blinded_units_all_bind_winner_sources(self) -> None:
        ps = pools()
        package = build_winner_package("bridge-updater-00", ps)
        units = blinded_from_package(ps, package)
        stream = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="WINNER",
        )
        validate_blinded_bridge_units(stream=stream, units=units)
        self.assertTrue(all(unit.source_trajectory_sha256 == pool.winner.trajectory_sha256 for pool, unit in zip(ps, units, strict=True)))

    def test_invalid_scientific_projection_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported Bridge FREE projection"):
            build_bridge_updater_stream(
                stream_id="bridge-updater-00",
                initial_skill_sha256=INITIAL,
                pools=pools(),
                scientific_projection="MIXED_REJECTED_WITNESS",
            )

    def test_selected_score_tamper_is_rejected(self) -> None:
        ps = pools()
        package = build_ff4_package("bridge-updater-00", ps)
        units = list(blinded_from_package(ps, package))
        original = units[0]
        units[0] = BlindedEvidenceUnit(
            task_id=original.task_id,
            pool_id=original.pool_id,
            acting_winner_sha256=original.acting_winner_sha256,
            source_rollout_index=original.source_rollout_index,
            source_trajectory_sha256=original.source_trajectory_sha256,
            source_score=1.0 - original.source_score,
            evidence_text=original.evidence_text,
            evidence_sha256=original.evidence_sha256,
            evidence_tokens=original.evidence_tokens,
        )
        stream = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="FIRST_FAIL_4",
        )
        with self.assertRaisesRegex(ValueError, "selected-evidence score drift"):
            validate_blinded_bridge_units(stream=stream, units=units)

    async def test_wrapper_passes_exact_blinded_treatment_to_first_party_updater_api(self) -> None:
        ps = pools()
        package = build_ff4_package("bridge-updater-00", ps)
        units = blinded_from_package(ps, package)
        stream = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="FIRST_FAIL_4",
        )
        expected = ProjectionUpdateResult(
            stream_id=stream.stream_id,
            projection="FIRST_FAIL_4",
            update_receipt_path="/tmp/receipt.json",
            update_receipt_sha256=h("receipt"),
            skill_post_path="/tmp/SKILL.md",
            skill_post_sha256=h("post-skill"),
            evolved=True,
            new_version_ids=("v1",),
            provider_calls=9,
            provider_total_tokens=1234,
        )
        fake = AsyncMock(return_value=expected)
        with patch(
            "research_pipeline.e2_r17_bridge_v4r2_updater_binding.run_projection_update",
            fake,
        ):
            result = await run_bridge_free_update(
                stream=stream,
                pools=ps,
                blinded_evidence_units=units,
                initial_skill_md="# initial",
                run_dir=Path("/tmp/not-executed"),
                llm_adapter=object(),
                mindmemos_commit="9049182",
                contract_sha256=h("contract"),
                authorization_sha256=h("auth"),
                transcript_max_chars=100000,
            )
        self.assertEqual(result, expected)
        kwargs = fake.await_args.kwargs
        self.assertIs(kwargs["stream"], stream)
        self.assertEqual(tuple(kwargs["pools"]), ps)
        self.assertEqual(tuple(kwargs["blinded_evidence_units"]), units)
        self.assertEqual(kwargs["transcript_max_chars"], 100000)

    async def test_wrapper_rejects_wrong_projection_in_returned_receipt(self) -> None:
        ps = pools()
        package = build_winner_package("bridge-updater-00", ps)
        units = blinded_from_package(ps, package)
        stream = build_bridge_updater_stream(
            stream_id="bridge-updater-00",
            initial_skill_sha256=INITIAL,
            pools=ps,
            scientific_projection="WINNER",
        )
        wrong = ProjectionUpdateResult(
            stream_id=stream.stream_id,
            projection="winner_only",
            update_receipt_path="/tmp/receipt.json",
            update_receipt_sha256=h("receipt"),
            skill_post_path="/tmp/SKILL.md",
            skill_post_sha256=h("post-skill"),
            evolved=True,
            new_version_ids=("v1",),
            provider_calls=9,
            provider_total_tokens=1234,
        )
        with patch(
            "research_pipeline.e2_r17_bridge_v4r2_updater_binding.run_projection_update",
            AsyncMock(return_value=wrong),
        ):
            with self.assertRaisesRegex(RuntimeError, "receipt projection label drift"):
                await run_bridge_free_update(
                    stream=stream,
                    pools=ps,
                    blinded_evidence_units=units,
                    initial_skill_md="# initial",
                    run_dir=Path("/tmp/not-executed"),
                    llm_adapter=object(),
                    mindmemos_commit="9049182",
                    contract_sha256=h("contract"),
                    authorization_sha256=h("auth"),
                    transcript_max_chars=100000,
                )


if __name__ == "__main__":
    unittest.main()
