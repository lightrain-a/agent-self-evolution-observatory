from __future__ import annotations

import hashlib
import unittest

from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    build_blinded_add_record_payload,
    sha_text,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def trajectory(task: str, index: int, score: int) -> TrajectoryRef:
    return TrajectoryRef(
        task_id=task,
        rollout_index=index,
        score=float(score),
        trajectory_path=f"/frozen/{task}/rollout_{index}.json",
        trajectory_sha256=digest(f"trajectory:{task}:{index}:{score}"),
        input_sha256=digest(f"input:{task}"),
        prompt_sha256=digest(f"prompt:{task}"),
        skill_pre_sha256=digest("skill"),
        verifier_sha256=digest("verifier-v1"),
        requested_model="deepseek-v4-pro",
        resolved_model="deepseek-v4-pro-ga-260813",
        provider_call_id_sha256=digest(f"call:{task}:{index}"),
        evidence_tokens=100 + index,
        failure_code=None if score else "controlled_failure",
    )


def pool(task: str, scores: list[int]) -> SearchPool:
    return SearchPool.freeze([trajectory(task, index, score) for index, score in enumerate(scores)])


def unit_for(p: SearchPool, source_index: int, text: str) -> BlindedEvidenceUnit:
    source = p.trajectories[source_index]
    return BlindedEvidenceUnit(
        task_id=p.task_id,
        pool_id=p.pool_id,
        acting_winner_sha256=p.winner.trajectory_sha256,
        source_rollout_index=source.rollout_index,
        source_trajectory_sha256=source.trajectory_sha256,
        source_score=source.score,
        evidence_text=text,
        evidence_sha256=sha_text(text),
        evidence_tokens=321,
    )


class MindMemOSUpdaterV31Test(unittest.TestCase):
    def test_selected_evidence_score_is_separate_from_acting_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        self.assertEqual(payload["score"], 0.0)
        self.assertEqual(payload["r17_selected_evidence_score"], 0.0)
        self.assertEqual(payload["r17_acting_score"], 1.0)
        self.assertEqual(payload["messages"], [{"role": "user", "content": failure.evidence_text}])

    def test_projection_and_rollout_metadata_are_not_in_model_visible_messages(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        visible = payload["messages"][0]["content"]
        for forbidden in [
            "mixed_rejected_witness",
            "SOURCE_ROLLOUT_INDEX",
            "ROLE:",
            failure.source_trajectory_sha256,
            p.pool_id,
        ]:
            self.assertNotIn(forbidden, visible)
        self.assertEqual(payload["r17_projection"], "mixed_rejected_witness")
        self.assertEqual(payload["r17_source_rollout_index"], 1)

    def test_winner_and_failure_can_share_acting_provenance_but_not_learning_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        winner = unit_for(p, 0, "E2-R17 SELECTED EXPERIENCE\nwinner evidence")
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailure evidence")
        common = dict(
            pool=p,
            project_id="internal",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
        )
        win_payload = build_blinded_add_record_payload(
            unit=winner, projection_label="winner_only", **common
        )
        mrw_payload = build_blinded_add_record_payload(
            unit=failure, projection_label="mixed_rejected_witness", **common
        )
        self.assertEqual(win_payload["r17_acting_winner_sha256"], mrw_payload["r17_acting_winner_sha256"])
        self.assertEqual(win_payload["r17_acting_score"], mrw_payload["r17_acting_score"])
        self.assertEqual(win_payload["score"], 1.0)
        self.assertEqual(mrw_payload["score"], 0.0)

    def test_sha_drift_is_rejected(self) -> None:
        p = pool("mixed", [1, 0])
        broken = BlindedEvidenceUnit(
            task_id=p.task_id,
            pool_id=p.pool_id,
            acting_winner_sha256=p.winner.trajectory_sha256,
            source_rollout_index=1,
            source_trajectory_sha256=p.trajectories[1].trajectory_sha256,
            source_score=0.0,
            evidence_text="failure evidence",
            evidence_sha256=digest("different text"),
            evidence_tokens=10,
        )
        with self.assertRaises(ValueError):
            broken.validate()


if __name__ == "__main__":
    unittest.main()
