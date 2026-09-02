from __future__ import annotations

from datetime import datetime, timezone
import unittest

from research_pipeline.e2_r17_rbagg_posthold import (
    build_rb_aggregated_session_evidence,
    build_rb_precomputed_summary_payload,
    build_rb_search_session_add_payload,
    normalize_rb_memory_items,
    parse_rb_memory_items,
    validate_rb_add_summary_pair,
)


VALID = """# Memory Item 1
## Title Verify output structure
## Description Check the workbook structure before finalizing.
## Content Inspect the relevant sheet, cells, and formulas before returning the result.

# Memory Item 2
## Title Avoid stale references
## Description Re-resolve references after structural edits.
## Content After moving or inserting cells, verify that dependent formulas still point to the intended ranges."""


class RBAggPostholdTest(unittest.TestCase):
    def receipt(self):
        return {
            "sources": [
                {
                    "rollout_index": i,
                    "trajectory_sha256": f"sha-{i}",
                    "verifier_score": 1.0 if i == 3 else 0.0,
                    "verifier_label": "SUCCESS" if i == 3 else "FAILURE",
                    "raw_tokens": 1000 + i,
                    "rendered_tokens": 512,
                    "rendered_sha256": f"rendered-{i}",
                }
                for i in range(8)
            ]
        }

    def test_parser_and_canonicalization(self):
        items = parse_rb_memory_items(VALID)
        self.assertEqual(2, len(items))
        self.assertEqual(VALID, normalize_rb_memory_items(items))

    def test_parser_rejects_extra_prose(self):
        with self.assertRaises(ValueError):
            parse_rb_memory_items("Here are the memories:\n" + VALID)

    def test_parser_rejects_index_gap(self):
        with self.assertRaises(ValueError):
            parse_rb_memory_items(VALID.replace("# Memory Item 2", "# Memory Item 3"))

    def test_session_score_must_match_pool_source_max(self):
        with self.assertRaises(ValueError):
            build_rb_aggregated_session_evidence(
                task_id="task",
                pool_id="pool",
                acting_score=0.0,
                raw_memory_items=VALID,
                aggregation_receipt=self.receipt(),
            )

    def test_add_summary_pair_is_one_to_one_and_scored(self):
        unit = build_rb_aggregated_session_evidence(
            task_id="task",
            pool_id="pool",
            acting_score=1.0,
            raw_memory_items=VALID,
            aggregation_receipt=self.receipt(),
        )
        add = build_rb_search_session_add_payload(
            unit=unit,
            project_id="project",
            task_completed_at="2026-09-02T00:00:00+00:00",
            initial_skill_sha256="skill-sha",
            root_version_id="root-version",
            deterministic_add_record_id="rbagg-id",
        )
        summary = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id="project",
            cloud_skill_id="cloud",
            skill_name="xlsx",
            deterministic_add_record_id="rbagg-id",
            created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        )
        validate_rb_add_summary_pair(add, summary)
        self.assertEqual(1.0, add["score"])
        self.assertEqual(1.0, summary["score"])
        self.assertTrue(add["r17_rbagg_precomputed_summary_required"])
        self.assertTrue(add["r17_rbagg_direct_trajectory_summarization_forbidden"])

    def test_add_summary_pair_rejects_score_drift(self):
        unit = build_rb_aggregated_session_evidence(
            task_id="task",
            pool_id="pool",
            acting_score=1.0,
            raw_memory_items=VALID,
            aggregation_receipt=self.receipt(),
        )
        add = build_rb_search_session_add_payload(
            unit=unit,
            project_id="project",
            task_completed_at="2026-09-02T00:00:00+00:00",
            initial_skill_sha256="skill-sha",
            root_version_id="root-version",
            deterministic_add_record_id="rbagg-id",
        )
        summary = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id="project",
            cloud_skill_id="cloud",
            skill_name="xlsx",
            deterministic_add_record_id="rbagg-id",
            created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        )
        summary["score"] = 0.0
        with self.assertRaises(ValueError):
            validate_rb_add_summary_pair(add, summary)


if __name__ == "__main__":
    unittest.main()
