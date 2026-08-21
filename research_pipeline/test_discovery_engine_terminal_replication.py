from __future__ import annotations

import json,tempfile,unittest
from pathlib import Path

from .discovery_engine_paper_yield_benchmark import _sha_json
from .discovery_engine_terminal_replication import _jsha,run_replication,validate_amendment,validate_contract


def _pool():
    return {"records":[{"ref":"arXiv:1","primary_source_verified":True,"title":"order memory failure","publication_date":"2026-08-01","empirical_facts":[{"text":"Task order changes outcomes."}],"typed_evidence":{"measured_failures":[{"text":"Shuffling reduces success."}],"boundary_observations":[],"operational_assumptions":[]}}]}

def _memory():return {"wiki_sha256":"a"*64,"entries":[]}

def _contract(pool,memory):
    return {"transaction_id":"test-tx","status":"FROZEN_BEFORE_PROVIDER_CALLS","frozen_inputs":{"primary_pool_sha256":_sha_json(pool),"research_memory_wiki_sha256":memory["wiki_sha256"]},"engines":[{"engine_id":"D5","candidate_budget":6},{"engine_id":"D2","candidate_budget":6}],"models":{"generator_requested":"kimi-k3","reviewer_requested":"deepseek-v4-pro"},"terminal_scoring_policy":{"early_reviewer_score_is_terminal_metric":False,"winner_may_be_declared_before_terminal_outcomes":False}}

def _candidate(title):
    return {"title":title,"birth_evidence_refs":["arXiv:1"],"memory_refs":[],"scientific_question":"Does history change later behavior?","observed_trigger":"Measured order sensitivity.","structural_variable":"Persistent update history.","strongest_same_information_baseline":"Matched current state without history difference.","baseline_counterexample":"Same state yields different future response.","cheapest_falsifier":{"setup":"Match current state.","intervention_or_comparison":"Vary prior history.","metric":"Future success.","stop_if":"No residual.","estimated_effort":"small"},"closest_known_explanation":"Task difficulty.","residual_after_reduction":"History-specific residual.","paper_level_claim":"History changes future behavior.","paperability_axis":"P","executable_now":True}


class TerminalReplicationTest(unittest.TestCase):
    def test_contract_rejects_source_drift(self):
        pool=_pool();memory=_memory();contract=_contract(pool,memory);pool["records"][0]["title"]="changed"
        with self.assertRaisesRegex(ValueError,"primary-pool-sha-drift"):validate_contract(contract,pool,memory)

    def test_operational_amendment_cannot_change_scientific_contract(self):
        pool=_pool();memory=_memory();contract=_contract(pool,memory)
        good={"status":"FROZEN_OPERATIONAL_AMENDMENT","transaction_id":"test-tx","original_contract_sha256":_jsha(contract),"trigger":{"class":"PROVIDER_SUPPORT_FAILURE","scientific_authority":False},"operational_change":{"generator_requested":"glm-5.3","frozen_evidence_unchanged":True,"terminal_scoring_policy_unchanged":True},"strict_transport":{"provider_post_retries":0,"single_post_per_request_fingerprint":True}}
        self.assertEqual(validate_amendment(good,contract)[0],"glm-5.3")
        bad=json.loads(json.dumps(good));bad["operational_change"]["frozen_evidence_unchanged"]=False
        with self.assertRaisesRegex(ValueError,"amendment-scope-invalid"):validate_amendment(bad,contract)

    def test_replication_uses_only_d5_d2_and_archives_raw(self):
        pool=_pool();memory=_memory();contract=_contract(pool,memory);calls=[]
        def gen(**kw):
            calls.append((kw["model"],kw["prompt"]));return {"text":json.dumps({"candidates":[_candidate(f"c{i}") for i in range(6)]}),"resolved_model":"kimi-k3-test","usage":{"input_tokens":1},"response_id":"private-generation","status":"completed"}
        def review(**kw):
            ids=[f"D5-C{i:02d}" for i in range(1,7)] if "D5-C01" in kw["prompt"] else [f"D2-C{i:02d}" for i in range(1,7)]
            rows=[{"candidate_id":cid,"provisional_basin_signature":"history","strongest_same_information_attack":"match state","possible_direct_counterevidence":"none yet","cheapest_decisive_falsifier":"matched state","support_blocker":"","duplicate_or_collision_target":"","what_must_be_true_for_paper":"residual","advisory_route":"FALSIFIER_NOW"} for cid in ids]
            return {"text":json.dumps({"triage":rows}),"resolved_model":"deepseek-v4-pro-test","usage":{"input_tokens":1},"response_id":"private-review","status":"completed"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report=run_replication(contract=contract,pool=pool,memory=memory,generator_responder=gen,reviewer_responder=review,private_root=root)
            self.assertEqual(report["summary"]["generated_candidates"],12)
            self.assertEqual({r["engine_id"] for r in report["candidates"]},{"D5","D2"})
            self.assertFalse(report["policy"]["winner_declared"])
            self.assertNotIn("paper_conversion_score",json.dumps(report))
            self.assertGreaterEqual(len(list((root/"raw").rglob("*.txt"))),2)
            self.assertEqual(len(list((root/"prompts").rglob("*.txt"))),4)
            self.assertEqual(len(list((root/"provider-receipts").rglob("*.json"))),4)
            self.assertEqual(len(report["provider_receipts"]["generation"])+len(report["provider_receipts"]["adversarial_triage"]),4)
            self.assertNotIn("private-generation",json.dumps(report))
            self.assertNotIn("private-review",json.dumps(report))

    def test_invalid_json_is_archived_before_parse_failure(self):
        pool=_pool();memory=_memory();contract=_contract(pool,memory)
        def bad(**kw):return {"text":"not-json","resolved_model":"kimi-k3-test","usage":{},"response_id":"private","status":"completed"}
        def review(**kw):raise AssertionError("review should not run")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report=run_replication(contract=contract,pool=pool,memory=memory,generator_responder=bad,reviewer_responder=review,private_root=root)
            self.assertEqual(report["summary"]["generated_candidates"],0)
            self.assertEqual(len(list((root/"raw").rglob("*.txt"))),1)
            self.assertTrue(any(r["status"]=="PARSE_FAILURE" for r in report["failures"]))


if __name__=="__main__":unittest.main()
