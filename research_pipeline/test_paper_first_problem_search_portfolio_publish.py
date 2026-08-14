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

    def test_latest_terminal_run_is_appended_without_erasing_historical_shadow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/"shadow-20260814-r2";run.mkdir()
            (run/"base.json").write_text(json.dumps({"summary":{"raw_seeds":101,"semantic_unique":54,"semantic_duplicates":47,"structural_clusters":54,"breadth_archive":48,"archive_lane_coverage":10},"archives":{"breadth":[]},"unique_seeds":[],"lane_counts":{"IDENTIFIABILITY_GAP":12},"archive_lane_counts":{"IDENTIFIABILITY_GAP":4}}),encoding="utf-8")
            (run/"frozen-primary-evidence-pool.json").write_text(json.dumps({"frozen_pool_sha256":"f"*64,"records":[]}),encoding="utf-8")
            (run/"machine-audit.json").write_text(json.dumps({"summary":{"formulated":15,"reviewable":3,"blocked":12},"blocked":[]}),encoding="utf-8")
            (run/"shadow-final-audit.json").write_text(json.dumps({"rows":[{"candidate_id":"S1","title":"blocked one","search_primitive":"COMPOSITION_INTERACTION","shadow_clear":False},{"candidate_id":"S2","title":"blocked two","search_primitive":"CONVERGENT_FAILURE","shadow_clear":False},{"candidate_id":"S3","title":"semantic clear","search_primitive":"IDENTIFIABILITY_GAP","shadow_clear":True}]}),encoding="utf-8")
            (run/"shadow-terminal-current-source-gate.json").write_text(json.dumps({"status":"SHADOW_TERMINAL_COMPLETE","summary":{"current_source_clear":0,"current_source_blocked":1,"current_source_missing":0,"terminal_shadow_survivors":0,"live_problem_gate_compatible_survivors":0},"rows":[{"candidate_id":"S1","terminal_shadow_clear":False,"live_problem_gate_compatible":False},{"candidate_id":"S2","terminal_shadow_clear":False,"live_problem_gate_compatible":False},{"candidate_id":"S3","terminal_shadow_clear":False,"live_problem_gate_compatible":False,"current_source_review":{"status":"complete","verdict":"BLOCK","reduction_class":"VALID_HARD_VETO"}}]}),encoding="utf-8")
            (run/"review-p1.json").write_text(json.dumps({"candidates":[{"candidate_id":"S1","semantic_reduction_review":{"verdict":"BLOCK"}},{"candidate_id":"S2","semantic_reduction_review":{"verdict":"BLOCK"}}]}),encoding="utf-8")
            (run/"review-p2.json").write_text(json.dumps({"candidates":[{"candidate_id":"S3","semantic_reduction_review":{"verdict":"CLEAR"}}]}),encoding="utf-8")
            (run/"evolve-g1-p1.json").write_text(json.dumps({"children":[{"branch_depth":1},{"branch_depth":1}]}),encoding="utf-8")
            (run/"formulate-p1.json").write_text(json.dumps({"candidates":[{},{}],"rejected":[{}]}),encoding="utf-8")
            gen_json=root/"shadow-generator.json";gen_js=root/"shadow-generator.js";queue_json=root/"shadow-queue.json";queue_js=root/"shadow-queue.js"
            gen_json.write_text(json.dumps({"schema_version":"3.2-shadow-import","run_id":"r1","scientific_authority":False,"policy":{"shadow_only":True},"candidates":[{"candidate_id":"SP-09","historical_counterfactual_problem_gate_pass":True}]}),encoding="utf-8")
            queue_json.write_text(json.dumps({"schema_version":"1.0-shadow-import","scientific_authority":False,"policy":{"shadow_only":True,"cannot_mutate_canonical_queue":True},"historical_counterfactual_pass_ids":["SP-09","SP-15"]}),encoding="utf-8")
            with patch.object(publisher,"GEN_JSON",gen_json),patch.object(publisher,"GEN_JS",gen_js),patch.object(publisher,"QUEUE_JSON",queue_json),patch.object(publisher,"QUEUE_JS",queue_js),patch.object(publisher,"build_problem_gate_queue") as live_queue:
                publisher.publish(run)
                live_queue.assert_not_called()
            state=json.loads(gen_json.read_text());shadow_queue=json.loads(queue_json.read_text())
        self.assertEqual(state["run_id"],"r1")
        self.assertEqual(state["candidates"][0]["candidate_id"],"SP-09")
        self.assertEqual(state["latest_run_id"],"shadow-20260814-r2")
        latest=state["latest_run"]
        self.assertEqual((latest["summary"]["raw_seeds"],latest["summary"]["semantic_unique"],latest["summary"]["semantic_clear"],latest["summary"]["current_source_blocked"],latest["summary"]["terminal_shadow_survivors"]),(101,54,1,1,0))
        self.assertEqual(latest["summary"]["live_paper_design_eligible"],0)
        self.assertFalse(latest["authority"]["paper_design"])
        self.assertEqual(shadow_queue["historical_counterfactual_pass_ids"],["SP-09","SP-15"])
        self.assertEqual(shadow_queue["latest_run"]["summary"]["terminal_shadow_survivors"],0)
        self.assertEqual(shadow_queue["latest_run"]["summary"]["live_paper_design_eligible"],0)


if __name__ == "__main__":
    unittest.main()
