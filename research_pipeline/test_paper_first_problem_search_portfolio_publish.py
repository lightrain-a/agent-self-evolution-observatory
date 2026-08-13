from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import paper_first_problem_search_portfolio_publish as publisher


class SearchPortfolioPublishTest(unittest.TestCase):
    def test_publisher_writes_shadow_state_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "base.json").write_text(json.dumps({
                "summary": {"raw_seeds": 0, "semantic_unique": 0, "semantic_duplicates": 0, "structural_clusters": 0, "breadth_archive": 0, "archive_lane_coverage": 0},
                "archives": {"breadth": []},
                "unique_seeds": [],
                "lane_counts": {},
                "archive_lane_counts": {},
            }), encoding="utf-8")
            (root / "frozen-primary-evidence-pool.json").write_text(json.dumps({"frozen_pool_sha256": "a" * 64, "records": []}), encoding="utf-8")
            (root / "machine-audit.json").write_text(json.dumps({"summary": {"reviewable": 0, "blocked": 0}, "blocked": []}), encoding="utf-8")
            gen_json=root/"shadow-generator.json";gen_js=root/"shadow-generator.js";queue_json=root/"shadow-queue.json";queue_js=root/"shadow-queue.js"
            queue={"summary":{"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"paper_design_eligible":0},"passed":[],"policy":{}}
            with patch.object(publisher,"GEN_JSON",gen_json), patch.object(publisher,"GEN_JS",gen_js), patch.object(publisher,"QUEUE_JSON",queue_json), patch.object(publisher,"QUEUE_JS",queue_js), patch.object(publisher,"build_problem_gate_queue",return_value=queue):
                publisher.publish(root)
            state=json.loads(gen_json.read_text())
            shadow_queue=json.loads(queue_json.read_text())
        self.assertEqual(state["status"],"SHADOW_PORTFOLIO_COMPLETE")
        self.assertTrue(state["policy"]["shadow_only"])
        self.assertTrue(state["policy"]["canonical_primary_generator_queue_untouched"])
        self.assertEqual(state["search_portfolio"]["summary"]["live_paper_design_eligible"],0)
        self.assertNotIn("saturation_memory",state)
        self.assertFalse(state["scientific_authority"] if "scientific_authority" in state else False)
        self.assertTrue(shadow_queue["policy"]["shadow_only"])
        self.assertTrue(shadow_queue["policy"]["cannot_grant_live_paper_design_eligibility"])


if __name__ == "__main__":
    unittest.main()
