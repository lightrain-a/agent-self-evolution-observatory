from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_diagnostic_witness import (
    ARMS,
    build_four_arm_evidence,
    make_diagnostic_stream,
    progress_matched_failed_nonwinner,
)

ROOT = Path(__file__).resolve().parents[1]
POOL_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828/cases")
S0 = ROOT / "generated/e2-r17-single-case-diagnostic-witness-s0-selector-freeze-20260902.json"
STREAM_TASKS = (
    "r17-b3-tsr-p7",
    "r17-b3-tsr-p0",
    "r17-b2-tsr-p3",
    "r17-b2-tsr-p8",
    "r17-b2-tsr-p2",
    "r17-b2-tsr-p5",
    "r17-b2-tsr-p4",
    "r17-b3-tsr-p8",
)


class DiagnosticWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pools = [load_frozen_pool(POOL_ROOT / task / "pool_k8.json") for task in STREAM_TASKS]
        cls.freeze = json.loads(S0.read_text(encoding="utf-8"))

    def test_progress_selector_matches_frozen_manifest(self) -> None:
        by_task = {row["task_id"]: row for row in self.freeze["units"]}
        changed = 0
        for pool in self.pools:
            row = by_task[pool.task_id]
            self.assertEqual(pool.winner.rollout_index, row["winner_rollout"])
            if not pool.mixed_pool:
                continue
            progress = progress_matched_failed_nonwinner(pool)
            self.assertEqual(progress.rollout_index, row["progress_fail_rollout"])
            first = pool.first_failed_nonwinner
            changed += int(first.rollout_index != progress.rollout_index)
        self.assertEqual(changed, 4)

    def test_diagnostic_stream_is_content_addressed_and_eight_pool_bound(self) -> None:
        units, _ = build_four_arm_evidence(
            self.pools,
            selector_freeze=self.freeze,
            final_block_cap_tokens=3072,
            transcript_max_chars=100000,
        )
        stream = make_diagnostic_stream(
            stream_id="e1-tsr-00::s1-rep0",
            initial_skill_sha256=self.pools[0].trajectories[0].skill_pre_sha256,
            pools=self.pools,
            arm="progress_fail",
            units=units["progress_fail"],
        )
        self.assertEqual(len(stream.packets), 8)
        self.assertEqual(len(stream.pools), 8)
        self.assertEqual(len(stream.stream_sha256), 64)
        self.assertEqual(stream.projection, "diagnostic_progress_fail")

    def test_four_arm_evidence_is_exactly_token_matched(self) -> None:
        units, receipts = build_four_arm_evidence(
            self.pools,
            selector_freeze=self.freeze,
            final_block_cap_tokens=3072,
            transcript_max_chars=100000,
        )
        self.assertEqual(set(units), set(ARMS))
        self.assertEqual(len(receipts), 8)
        for index, pool in enumerate(self.pools):
            token_counts = {units[arm][index].evidence_tokens for arm in ARMS}
            self.assertEqual(len(token_counts), 1)
            self.assertLessEqual(next(iter(token_counts)), 3072)
            if pool.mixed_pool:
                parity = receipts[index]["parity"]
                self.assertEqual(parity["contrast_source_allocation"], "50/50")
                self.assertLessEqual(abs(parity["contrast_winner_source_tokens"] - parity["contrast_failure_source_tokens"]), 1)
            if pool.mixed_pool:
                self.assertEqual(units["win_c"][index].source_score, 1.0)
                self.assertEqual(units["first_fail"][index].source_score, 0.0)
                self.assertEqual(units["progress_fail"][index].source_score, 0.0)
                self.assertEqual(units["progress_contrast"][index].source_score, 0.0)
            else:
                texts = {units[arm][index].evidence_text for arm in ARMS}
                self.assertEqual(len(texts), 1)

    def test_contrast_differs_only_on_mixed_pools(self) -> None:
        units, _ = build_four_arm_evidence(
            self.pools,
            selector_freeze=self.freeze,
            final_block_cap_tokens=3072,
            transcript_max_chars=100000,
        )
        for index, pool in enumerate(self.pools):
            if pool.mixed_pool:
                self.assertNotEqual(units["progress_contrast"][index].evidence_text, units["progress_fail"][index].evidence_text)
            else:
                self.assertEqual(units["progress_contrast"][index].evidence_text, units["progress_fail"][index].evidence_text)


if __name__ == "__main__":
    unittest.main()
