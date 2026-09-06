from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import (
    build_ff4_package,
    build_winner_package,
)
from research_pipeline.e2_r17_bridge_v4r2_evidence_rendering import render_paired_packages
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_pool(root: Path, task_id: str, *, mixed: bool, all_failure: bool = False) -> SearchPool:
    if mixed:
        scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0)
    elif all_failure:
        scores = (0.0,) * 8
    else:
        scores = (1.0,) * 8
    rows = []
    task_root = root / task_id
    task_root.mkdir(parents=True, exist_ok=True)
    for index, score in enumerate(scores):
        payload = {
            "case_id": task_id,
            "rollout_index": index,
            "score": score,
            "score_message": "success" if score else "failed verification after workbook operation",
            "messages": [
                {"role": "system", "content": "hidden common system prompt"},
                {
                    "role": "user",
                    "content": (
                        "Edit the spreadsheet and preserve unrelated content. "
                        "Inspect the workbook, make the requested transformation, save output.xlsx, "
                        "reload the saved artifact, and verify the target values. "
                    ) * 5,
                },
                {
                    "role": "assistant",
                    "content": (
                        "I inspected the workbook and attempted the requested edit. "
                        + ("The operation completed and I reloaded the saved artifact for verification. " if score else "A stale worksheet reference caused the operation to fail before a verified output. ")
                    ) * 5,
                },
            ],
        }
        path = task_root / f"r{index}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(
            TrajectoryRef(
                task_id=task_id,
                rollout_index=index,
                score=score,
                trajectory_path=str(path),
                trajectory_sha256=digest,
                input_sha256=h(f"input|{task_id}"),
                prompt_sha256=h(f"prompt|{task_id}"),
                skill_pre_sha256=h("skill"),
                verifier_sha256=h("verifier"),
                requested_model="deepseek-v4-pro",
                resolved_model="deepseek-v4-pro-ga-260813",
                provider_call_id_sha256=h(f"call|{task_id}|{index}"),
                evidence_tokens=200,
            )
        )
    return SearchPool.freeze(rows)


def build_pools(root: Path) -> tuple[SearchPool, ...]:
    return tuple(
        build_pool(
            root,
            f"r17-bridge-render-p{index}",
            mixed=index < 6,
            all_failure=index == 7,
        )
        for index in range(8)
    )


class BridgeV4R2EvidenceRenderingTests(unittest.TestCase):
    def test_free_and_comp_receive_exact_same_bytes_and_selected_scores(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            winner = build_winner_package("bridge-render-00", pools)
            ff4 = build_ff4_package("bridge-render-00", pools)
            rendered = render_paired_packages(pools=pools, winner_package=winner, ff4_package=ff4)
            self.assertEqual(len(rendered.winner_free_units), 8)
            self.assertEqual(len(rendered.ff4_free_units), 8)
            for free, comp in zip(rendered.winner_free_units, rendered.winner_compiler_units, strict=True):
                self.assertEqual(free.evidence_text, comp.evidence_text)
                self.assertEqual(free.evidence_sha256, comp.evidence_sha256)
                self.assertEqual(free.source_score, comp.selected_score)
            for free, comp in zip(rendered.ff4_free_units, rendered.ff4_compiler_units, strict=True):
                self.assertEqual(free.evidence_text, comp.evidence_text)
                self.assertEqual(free.evidence_sha256, comp.evidence_sha256)
                self.assertEqual(free.source_score, comp.selected_score)

    def test_each_winner_ff4_pair_has_exact_provider_visible_token_parity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            rendered = render_paired_packages(
                pools=pools,
                winner_package=build_winner_package("bridge-render-00", pools),
                ff4_package=build_ff4_package("bridge-render-00", pools),
            )
            self.assertEqual(len(rendered.pair_receipts), 8)
            for row in rendered.pair_receipts:
                self.assertGreater(row.matched_final_block_tokens, 0)
                self.assertEqual(
                    row.parity_receipt["matched_final_block_tokens"],
                    row.matched_final_block_tokens,
                )
                self.assertFalse(row.parity_receipt["padding_used"])
                self.assertFalse(row.parity_receipt["arm_metadata_visible"])

    def test_exactly_four_replaced_pairs_use_failure_score_while_serving_stays_winner(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            rendered = render_paired_packages(
                pools=pools,
                winner_package=build_winner_package("bridge-render-00", pools),
                ff4_package=build_ff4_package("bridge-render-00", pools),
            )
            replaced = [row for row in rendered.pair_receipts if row.ff4_replaced]
            unchanged = [row for row in rendered.pair_receipts if not row.ff4_replaced]
            self.assertEqual(len(replaced), 4)
            self.assertEqual(len(unchanged), 4)
            for row in replaced:
                self.assertEqual(row.winner_selected_score, 1.0)
                self.assertEqual(row.ff4_selected_score, 0.0)
                self.assertNotEqual(row.winner_source_sha256, row.ff4_source_sha256)
            for row in unchanged:
                self.assertTrue(row.unchanged_pool_byte_identical)
                self.assertEqual(row.winner_source_sha256, row.ff4_source_sha256)
            for w, f in zip(rendered.winner_free_units, rendered.ff4_free_units, strict=True):
                self.assertEqual(w.acting_winner_sha256, f.acting_winner_sha256)

    def test_unchanged_all_failure_winner_score_can_remain_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            rendered = render_paired_packages(
                pools=pools,
                winner_package=build_winner_package("bridge-render-00", pools),
                ff4_package=build_ff4_package("bridge-render-00", pools),
            )
            rows = [row for row in rendered.pair_receipts if not row.ff4_replaced and row.ff4_selected_score == 0.0]
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0].unchanged_pool_byte_identical)

    def test_model_visible_evidence_contains_no_projection_or_provenance_labels(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            rendered = render_paired_packages(
                pools=pools,
                winner_package=build_winner_package("bridge-render-00", pools),
                ff4_package=build_ff4_package("bridge-render-00", pools),
            )
            forbidden = ("FIRST_FAIL_4", "FF4_COMP", "FF4_FREE", "PROJECTION:", "POOL_ID:", "ACTING_WINNER")
            for unit in rendered.winner_free_units + rendered.ff4_free_units:
                for marker in forbidden:
                    self.assertNotIn(marker, unit.evidence_text)
                self.assertNotIn("hidden common system prompt", unit.evidence_text)

    def test_rendering_receipt_is_content_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pools = build_pools(Path(td))
            winner = build_winner_package("bridge-render-00", pools)
            ff4 = build_ff4_package("bridge-render-00", pools)
            a = render_paired_packages(pools=pools, winner_package=winner, ff4_package=ff4)
            b = render_paired_packages(pools=pools, winner_package=winner, ff4_package=ff4)
            self.assertEqual(a.receipt_sha256, b.receipt_sha256)

    def test_trajectory_sha_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pools = build_pools(root)
            winner = build_winner_package("bridge-render-00", pools)
            ff4 = build_ff4_package("bridge-render-00", pools)
            path = Path(pools[0].trajectories[0].trajectory_path)
            path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "trajectory file/SHA drift"):
                render_paired_packages(pools=pools, winner_package=winner, ff4_package=ff4)


if __name__ == "__main__":
    unittest.main()
