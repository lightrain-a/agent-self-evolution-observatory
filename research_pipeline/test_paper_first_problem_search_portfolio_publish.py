from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import paper_first_problem_search_portfolio_publish as publisher


class SearchPortfolioPublishTest(unittest.TestCase):
    def test_formulation_exact_retry_counts_one_terminal_shard_and_actual_branch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            base={"parents":[{"seed_id":"B1"}]}
            (root/"error-formulate-p1-provider-a.json").write_text(json.dumps({"status":"PROVIDER_ERROR_ZERO_AUTHORITY","branch_ids":["B1"],"scientific_authority":False}),encoding="utf-8")
            (root/"error-formulate-p1-b.json").write_text(json.dumps({"status":"PARSE_ERROR_ZERO_AUTHORITY","raw_sha256":"f"*64,"scientific_authority":False}),encoding="utf-8")
            accounting=publisher._formulation_execution_accounting(root,base,[])
        self.assertEqual(accounting["requested_shards"],1)
        self.assertEqual(accounting["successful_shards"],0)
        self.assertEqual(accounting["provider_failures"],0)
        self.assertEqual(accounting["parse_failures"],1)
        self.assertEqual(accounting["requested_branches"],1)
        self.assertEqual(accounting["successful_branches"],0)
        self.assertEqual(accounting["censored_branches"],1)
        self.assertEqual(accounting["attempt_calls"],2)

    def test_model_identity_uses_real_provider_receipts_and_review_generator_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"expand-UNEXPLAINED_BOUNDARY-p1.json").write_text(json.dumps({"requested_model":"kimi-k3","resolved_model":"kimi-k3-endpoint","raw_sha256":"1"*64}),encoding="utf-8")
            (root/"formulate-p1.json").write_text(json.dumps({"requested_model":"glm-5.3","resolved_model":"glm-5.3-endpoint","raw_sha256":"2"*64}),encoding="utf-8")
            (root/"review-p1.json").write_text(json.dumps({"requested_model":"deepseek-v4-pro","resolved_model":"deepseek-v4-pro-endpoint","generator_resolved_model":"glm-5.3-endpoint","generator_receipts":[{"source_artifact":"formulate-p1.json","requested_model":"glm-5.3","resolved_model":"glm-5.3-endpoint","raw_sha256":"2"*64}],"candidates":[]}),encoding="utf-8")
            identity=publisher._model_identity_receipts(root)
        self.assertEqual(identity["generator_requested_model"],"glm-5.3|kimi-k3")
        self.assertEqual(identity["generator_resolved_model"],"glm-5.3-endpoint|kimi-k3-endpoint")
        self.assertEqual(identity["reviewer_requested_model"],"deepseek-v4-pro")
        self.assertEqual(identity["reviewer_resolved_model"],"deepseek-v4-pro-endpoint")
        self.assertEqual(identity["review_generator_resolved_model"],"glm-5.3-endpoint")
        self.assertTrue(identity["identity_complete_for_review_independence"])
        self.assertTrue(identity["all_review_batches_independent_resolved_model"])

    def test_missing_or_same_review_identity_never_counts_as_independent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"review-p1.json").write_text(json.dumps({"requested_model":"deepseek-v4-pro","resolved_model":"glm-5.3-endpoint","generator_resolved_model":"glm-5.3-endpoint","candidates":[]}),encoding="utf-8")
            same=publisher._model_identity_receipts(root)
            (root/"review-p1.json").write_text(json.dumps({"requested_model":"deepseek-v4-pro","resolved_model":"deepseek-v4-pro-endpoint","candidates":[]}),encoding="utf-8")
            missing=publisher._model_identity_receipts(root)
        self.assertFalse(same["all_review_batches_independent_resolved_model"])
        self.assertTrue(same["identity_complete_for_review_independence"])
        self.assertFalse(missing["all_review_batches_independent_resolved_model"])
        self.assertFalse(missing["identity_complete_for_review_independence"])

    def test_terminal_evidence_holds_close_frozen_transaction(self) -> None:
        summary={
            "provisional_problem_candidates": 4,
            "evidence_wait_primary_asset": 1,
            "evidence_substrate_hold": 1,
            "evidence_review_blocked": 1,
            "evidence_inconclusive": 1,
        }
        self.assertEqual(publisher._evidence_unresolved_count(summary),0)
        summary["provisional_problem_candidates"]=5
        self.assertEqual(publisher._evidence_unresolved_count(summary),1)

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
            (run/"shadow-run-qualification.json").write_text(json.dumps({"schema_version":"1.1","status":"READY_FOR_SHADOW_EXPANSION","source_generated_at":"2026-08-14T03:47:25+00:00","source_set_sha256":"1"*64,"source_primary_content_sha256":"3"*64,"source_pool_sha256":"2"*64,"stage_runner_required_schema":"1.4","control_snapshot_sha256":"c"*64,"main_commit":"d"*40,"scientific_authority":False}),encoding="utf-8")
            (run/"machine-audit.json").write_text(json.dumps({"control_snapshot_sha256":"c"*64,"summary":{"formulated":15,"reviewable":3,"reduction_pending":4,"blocked":8,"problem_falsifier_eligible":4},"blocked":[]}),encoding="utf-8")
            (run/"shadow-final-audit.json").write_text(json.dumps({"control_snapshot_sha256":"c"*64,"rows":[{"candidate_id":"S1","title":"blocked one","search_primitive":"UNEXPLAINED_BOUNDARY","shadow_clear":False,"candidate":{"title":"blocked one","irreducible_object":"layer-dependent selection sign inversion","exact_prediction":"sign flips by representation layer","empirical_evidence":{"source_a":{"ref":"arXiv:2608.11350","claim":"harness evolution improves success"},"source_b":{"ref":"arXiv:2608.11350","claim":"raw VLA voting degrades success"}},"semantic_reduction_review":{"verdict":"BLOCK","reduction_class":"NEEDS_EXACT_REDUCTION_TEST","lane_contract_verified":True,"matched_patterns":["persistent-update-vs-test-time-compute"],"strongest_reduction":"generic test-time scaling","exact_reduction_test":"match candidate quality and diversity","reason":"exact reduction remains unresolved","lane_contract_reason":"lane valid"}}},{"candidate_id":"S2","title":"blocked two","search_primitive":"CONVERGENT_FAILURE","shadow_clear":False,"candidate":{"title":"blocked two","irreducible_object":"optimizer capability threshold","exact_prediction":"weak optimizers fail under the same interface","empirical_evidence":{"source_a":{"ref":"arXiv:2608.09629","claim":"weak optimizer cannot operate interface"},"source_b":{"ref":"arXiv:2608.11340","claim":"weak coding agent fails to converge"}},"semantic_reduction_review":{"verdict":"BLOCK","reduction_class":"SOFT_COLLISION","lane_contract_verified":False,"matched_patterns":["model-scaffold-enactability"],"strongest_reduction":"cross-model instruction compatibility","exact_reduction_test":"hold budget fixed","reason":"lane contract fails","lane_contract_reason":"no shared bounded condition"}}},{"candidate_id":"S3","title":"semantic clear","search_primitive":"IDENTIFIABILITY_GAP","shadow_clear":True,"candidate":{"empirical_evidence":{"source_a":{"ref":"arXiv:2608.09168"}},"semantic_reduction_review":{"verdict":"CLEAR","reduction_class":"NONE","lane_contract_verified":True}}}]}),encoding="utf-8")
            (run/"shadow-terminal-current-source-gate.json").write_text(json.dumps({"control_snapshot_sha256":"c"*64,"status":"SHADOW_TERMINAL_COMPLETE","summary":{"current_source_clear":0,"current_source_blocked":1,"current_source_missing":0,"terminal_shadow_survivors":0,"live_problem_gate_compatible_survivors":0},"rows":[{"candidate_id":"S1","terminal_shadow_clear":False,"live_problem_gate_compatible":False},{"candidate_id":"S2","terminal_shadow_clear":False,"live_problem_gate_compatible":False},{"candidate_id":"S3","terminal_shadow_clear":False,"live_problem_gate_compatible":False,"current_source_review":{"status":"complete","verdict":"BLOCK","reduction_class":"VALID_HARD_VETO","strongest_reduction":"generic identifiability over an explicit omitted pipeline variable","reason":"The same-information claim is absorbed once the pipeline variable is instrumented.","sources":[{"ref":"arXiv:2605.10114"},{"ref":"arXiv:2608.05604"}]}}]}),encoding="utf-8")
            (run/"review-p1.json").write_text(json.dumps({"candidates":[{"candidate_id":"S1","semantic_reduction_review":{"verdict":"BLOCK"}},{"candidate_id":"S2","semantic_reduction_review":{"verdict":"BLOCK"}}]}),encoding="utf-8")
            (run/"review-p2.json").write_text(json.dumps({"candidates":[{"candidate_id":"S3","semantic_reduction_review":{"verdict":"CLEAR"}}]}),encoding="utf-8")
            (run/"evolve-g1-p1.json").write_text(json.dumps({"children":[{"branch_depth":1},{"branch_depth":1}]}),encoding="utf-8")
            (run/"formulate-p1.json").write_text(json.dumps({"branch_ids":["B1","B2"],"candidates":[{},{}],"reduction_pending":[{}],"rejected":[{}]}),encoding="utf-8")
            (run/"error-formulate-p1-oldparse.json").write_text(json.dumps({"status":"PARSE_ERROR_ZERO_AUTHORITY","raw_sha256":"9"*64,"scientific_authority":False}),encoding="utf-8")
            (run/"error-formulate-p2-provider-deadbeef.json").write_text(json.dumps({"status":"PROVIDER_TIMEOUT_ZERO_AUTHORITY","branch_ids":["B3","B4"],"scientific_authority":False}),encoding="utf-8")
            (run/"problem-falsifier-support-inventory-request.json").write_text(json.dumps({"status":"PROBLEM_FALSIFIER_SUPPORT_INVENTORY_REQUEST_READY","summary":{"queued":4,"inventory_requests":4},"scientific_authority":False}),encoding="utf-8")
            inventory_path=run/"problem-falsifier-support-inventory.json";inventory_path.write_text(json.dumps({"inventory_origin":"test-primary-release-audit","rows":[]}),encoding="utf-8")
            inventory_text=inventory_path.read_text();inventory_sha=hashlib.sha256(inventory_path.read_bytes()).hexdigest()
            (run/"problem-falsifier-preflight.json").write_text(json.dumps({"status":"PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE","support_inventory_sha256":inventory_sha,"summary":{"queued":4,"support_qualified":0,"hold_support_unavailable":4,"falsifier_executed":0},"scientific_authority":False}),encoding="utf-8")
            gen_json=root/"shadow-generator.json";gen_js=root/"shadow-generator.js";queue_json=root/"shadow-queue.json";queue_js=root/"shadow-queue.js"
            gen_json.write_text(json.dumps({"schema_version":"3.2-shadow-import","run_id":"r1","scientific_authority":False,"policy":{"shadow_only":True},"candidates":[{"candidate_id":"SP-09","historical_counterfactual_problem_gate_pass":True}]}),encoding="utf-8")
            queue_json.write_text(json.dumps({"schema_version":"1.0-shadow-import","scientific_authority":False,"policy":{"shadow_only":True,"cannot_mutate_canonical_queue":True},"historical_counterfactual_pass_ids":["SP-09","SP-15"]}),encoding="utf-8")
            with patch.object(publisher,"GEN_JSON",gen_json),patch.object(publisher,"GEN_JS",gen_js),patch.object(publisher,"QUEUE_JSON",queue_json),patch.object(publisher,"QUEUE_JS",queue_js),patch.object(publisher,"build_problem_gate_queue") as live_queue:
                publisher.publish(run)
                live_queue.assert_not_called()
            state=json.loads(gen_json.read_text());shadow_queue=json.loads(queue_json.read_text())
            inventory_path.write_text("{}",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"support inventory hash mismatch"):
                publisher._latest_shadow_run(run)
            inventory_path.write_text(inventory_text,encoding="utf-8")
            terminal_path=run/"shadow-terminal-current-source-gate.json";terminal_payload=json.loads(terminal_path.read_text());terminal_payload["control_snapshot_sha256"]="e"*64;terminal_path.write_text(json.dumps(terminal_payload),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"control mismatch:shadow-terminal-current-source-gate"):
                publisher._latest_shadow_run(run)
        self.assertEqual(state["run_id"],"r1")
        self.assertEqual(state["candidates"][0]["candidate_id"],"SP-09")
        self.assertEqual(state["latest_run_id"],"shadow-20260814-r2")
        latest=state["latest_run"]
        self.assertEqual(latest["schema_version"],"1.2-shadow-run")
        self.assertEqual(latest["stage_runner_required_schema"],"1.4")
        self.assertEqual(latest["control_snapshot_sha256"],"c"*64)
        self.assertEqual(latest["qualification_main_commit"],"d"*40)
        self.assertEqual(latest["source_generated_at"],"2026-08-14T03:47:25+00:00")
        self.assertEqual(latest["source_set_sha256"],"1"*64)
        self.assertEqual(latest["source_primary_content_sha256"],"3"*64)
        self.assertEqual(latest["source_pool_sha256"],"2"*64)
        self.assertTrue(latest["policy"]["source_identity_is_bounded_timestamp_and_sha_provenance"])
        self.assertTrue(latest["policy"]["control_snapshot_bound_run"])
        self.assertTrue(latest["policy"]["control_snapshot_terminal_provenance_verified"])
        self.assertTrue(latest["policy"]["control_snapshot_provenance_is_bounded_sha_only"])
        self.assertEqual((latest["summary"]["raw_seeds"],latest["summary"]["semantic_unique"],latest["summary"]["semantic_clear"],latest["summary"]["current_source_blocked"],latest["summary"]["terminal_shadow_survivors"]),(101,54,1,1,0))
        self.assertEqual(latest["summary"]["live_paper_design_eligible"],0)
        self.assertEqual((latest["summary"]["evolution_g1_requested"],latest["summary"]["evolution_g1_valid"],latest["summary"]["evolution_g2_requested"],latest["summary"]["evolution_g2_valid"]),(2,2,0,0))
        self.assertEqual((latest["summary"]["formulation_requested_shards"],latest["summary"]["formulation_successful_shards"],latest["summary"]["formulation_provider_failures"],latest["summary"]["formulation_parse_failures"],latest["summary"]["formulation_requested_branches"],latest["summary"]["formulation_successful_branches"],latest["summary"]["formulation_execution_censored_branches"]),(2,1,1,0,4,2,2))
        self.assertEqual((latest["summary"]["formulated_candidates"],latest["summary"]["formulation_reduction_pending"],latest["summary"]["formulation_rejected"],latest["summary"]["machine_reduction_pending"],latest["summary"]["machine_reduction_blocked"]),(2,1,1,4,8))
        self.assertEqual((latest["summary"]["problem_falsifier_eligible"],latest["summary"]["problem_falsifier_inventory_requested"],latest["summary"]["problem_falsifier_support_qualified"],latest["summary"]["problem_falsifier_hold_support_unavailable"],latest["summary"]["problem_falsifier_executed"]),(4,4,0,4,0))
        self.assertTrue(latest["policy"]["execution_loss_is_not_scientific_negative"])
        self.assertTrue(latest["policy"]["formulation_reduction_pending_is_not_scientific_block_or_pass"])
        self.assertTrue(latest["policy"]["machine_rechecks_reduction_pending_before_problem_falsifier"])
        self.assertTrue(latest["policy"]["problem_falsifier_preflight_must_cover_all_eligible_before_terminal_complete"])
        self.assertTrue(latest["policy"]["problem_falsifier_hold_is_not_scientific_fail"])
        self.assertTrue(latest["policy"]["problem_falsifier_support_inventory_hash_verified"])
        self.assertEqual(latest["problem_falsifier_support_inventory_sha256"],inventory_sha)
        current_block=next(row for row in latest["candidates"] if row["candidate_id"]=="S3")
        self.assertEqual(current_block["current_source_strongest_reduction"],"generic identifiability over an explicit omitted pipeline variable")
        self.assertEqual(current_block["current_source_source_refs"],["arXiv:2605.10114","arXiv:2608.05604"])
        self.assertIn("absorbed",current_block["current_source_reason"])
        exact_block=next(row for row in latest["candidates"] if row["candidate_id"]=="S1")
        self.assertEqual(exact_block["semantic_reduction_class"],"NEEDS_EXACT_REDUCTION_TEST")
        self.assertEqual(exact_block["semantic_matched_patterns"],["persistent-update-vs-test-time-compute"])
        self.assertEqual(exact_block["semantic_source_refs"],["arXiv:2608.11350"])
        self.assertEqual(exact_block["semantic_source_claims"],["harness evolution improves success","raw VLA voting degrades success"])
        self.assertIn("layer-dependent selection sign inversion",exact_block["semantic_problem_text"])
        lane_block=next(row for row in latest["candidates"] if row["candidate_id"]=="S2")
        self.assertFalse(lane_block["semantic_lane_contract_verified"])
        self.assertEqual(lane_block["semantic_lane_contract_reason"],"no shared bounded condition")
        self.assertEqual(lane_block["semantic_source_claims"],["weak optimizer cannot operate interface","weak coding agent fails to converge"])
        self.assertIn("optimizer capability threshold",lane_block["semantic_problem_text"])
        self.assertFalse(latest["authority"]["paper_design"])
        self.assertEqual(shadow_queue["historical_counterfactual_pass_ids"],["SP-09","SP-15"])
        self.assertEqual(shadow_queue["latest_run"]["summary"]["terminal_shadow_survivors"],0)
        self.assertEqual(shadow_queue["latest_run"]["summary"]["live_paper_design_eligible"],0)


if __name__ == "__main__":
    unittest.main()
