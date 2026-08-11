from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .iclr_external_review import build_prompt, extract_json, normalize_response, prepare_batches, update_store


def sample_idea(index: int) -> dict:
    idea_id = f"idea-{index}"
    return {
        "id": idea_id,
        "rank": index,
        "title": {"en": f"Idea {index}", "zh": f"方向 {index}"},
        "track": {"en": "Test track", "zh": "测试"},
        "purpose": {"en": "A falsifiable problem", "zh": "问题"},
        "core_idea": {"en": "A persistent update mechanism", "zh": "机制"},
        "collision_boundary": {"en": "Nearest work lacks the gate", "zh": "边界"},
        "nearest_work": ["Paper A"],
        "hypothesis": {"en": "The gate improves future utility", "zh": "假设"},
        "strongest_baseline": {"en": "Equal-budget baseline", "zh": "基线"},
        "pilot": {"en": "Two-model pilot", "zh": "实验"},
        "stop_condition": {"en": "Stop on no transfer", "zh": "停止"},
        "domains": ["text", "web"],
        "budget": {"max_gpus": 1, "gpu_hours": 12},
    }


class IclrExternalReviewTest(unittest.TestCase):
    def test_prepare_batches_skips_reviewed(self) -> None:
        bank = {"passed_ideas": [sample_idea(i) for i in range(1, 7)]}
        store = {"reviews": {"idea-1": [{"reviewer": "existing", "verdict": "pass"}]}}
        with tempfile.TemporaryDirectory() as tmp:
            manifest = prepare_batches(bank, Path(tmp), batch_size=2, review_store=store)
            self.assertEqual(manifest["total_passed_ideas"], 6)
            self.assertEqual(manifest["already_reviewed"], 1)
            self.assertEqual(manifest["queued_ideas"], 5)
            self.assertEqual(len(manifest["batches"]), 3)
            first_prompt = Path(manifest["batches"][0]["prompt"]).read_text(encoding="utf-8")
            self.assertNotIn('"idea_id": "idea-1"', first_prompt)
            self.assertIn('"idea_id": "idea-2"', first_prompt)

    def test_prompt_and_fenced_json_parser(self) -> None:
        prompt = build_prompt([sample_idea(1)], batch_index=1, batch_count=1)
        self.assertIn("strict ICLR area chair", prompt)
        self.assertIn("idea-1", prompt)
        self.assertIn("emerging_niche", prompt)
        response = {
            "reviewer": "agent-project-web-gpt-iclr-area-chair",
            "review_date": "2026-08-01",
            "ideas": [{
                "idea_id": "idea-1",
                "verdict": "revise",
                "confidence": "high",
                "finding": "The mechanism is promising but the collision boundary is not frozen.",
                "required_action": "Compare against the nearest direct mechanism under matched cost.",
                "direct_collision": {"status": "partial", "closest_work": [], "surviving_difference": "Persistent update admission."},
                "emerging_niche": {"evidence_fresh": True, "exact_problem_sparsity": 5, "emerging_signal": 4, "collision_margin": 4, "decisive_p0": 5, "importance_floor": 4, "evidence_note": "Fresh primary-source audit.", "neighbors": []},
                "iclr_fit": "conditional",
                "strongest_baseline": "Equal-budget baseline",
                "decisive_pilot": "Matched-cost future-task utility.",
                "stop_rule": "Stop if the baseline matches transfer.",
                "unknowns": [],
            }],
        }
        parsed = extract_json("```json\n" + json.dumps(response) + "\n```")
        normalized = normalize_response(parsed, ["idea-1"], source_artifact="response.md")
        self.assertEqual(normalized["idea-1"]["verdict"], "revise")
        self.assertEqual(normalized["idea-1"]["emerging_niche"]["score"], 90.0)
        self.assertTrue(normalized["idea-1"]["emerging_niche"]["priority_eligible"])
        self.assertEqual(normalized["idea-1"]["source_artifact"], "response.md")

    def test_update_store_counts_all_ideas(self) -> None:
        store = {"reviews": {"idea-1": [{"reviewer": "old", "verdict": "pass"}]}, "status": {}}
        result = update_store(
            store,
            {"idea-2": {"reviewer": "new", "verdict": "block", "finding": "x", "required_action": "y"}},
            all_ids=["idea-1", "idea-2", "idea-3"],
            attempt_result="batch_1_completed",
            attempt_host="admin01-NF5468M5",
        )
        self.assertEqual(result["status"]["reviewed"], 2)
        self.assertEqual(result["status"]["pending"], 1)
        self.assertFalse(result["status"]["complete"])
        self.assertEqual(result["status"]["verdict_counts"], {"pass": 1, "revise": 0, "block": 1, "unknown": 1})


if __name__ == "__main__":
    unittest.main()
