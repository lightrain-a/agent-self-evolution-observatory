from __future__ import annotations

import json,tempfile,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path

from .config import StorageSettings
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .paper_first_problem_generator import run_problem_generator


class PaperFirstProblemGeneratorTest(unittest.TestCase):
    def storage(self,root:Path)->StorageSettings:
        return StorageSettings(data_root=root,corpus_dir=root/"corpora",dataset_dir=root/"datasets",paper_dir=root/"papers",index_dir=root/"indexes",run_dir=root/"runs",cache_dir=root/"cache",lock_dir=root/"locks",site_artifact_dir=root/"site")
    def pool(self,root:Path,now:datetime)->Path:
        records=[]
        for i in range(1,5):
            ref=f"arXiv:2608.1000{i}";records.append({"ref":ref,"title":f"Primary {i}","primary_url":f"https://arxiv.org/abs/2608.1000{i}","source_sha256":str(i)*64,"abstract_sha256":str(i+4)*64,"abstract":f"Primary abstract fact {i} about self-evolving agents.","primary_source_verified":True})
        p=root/"primary.json";p.write_text(json.dumps({"status":"READY","generated_at":now.isoformat(),"records":records}),encoding="utf-8");return p
    def raw_candidate(self)->dict:
        return {"candidate_id":"AUTO-1","title":"Contradiction candidate","empirical_contradiction":{"source_a":{"ref":"arXiv:2608.10001","claim":"Fact A was observed."},"source_b":{"ref":"arXiv:2608.10002","claim":"Fact B was observed."},"tension":"A and B contradict the current explanation."},"irreducible_object":"Object Q","mature_theory_baselines":[{"name":"Theory A","same_information_projection":"same variables","reduction_test":"cannot predict Q"},{"name":"Theory B","same_information_projection":"same variables","reduction_test":"cannot predict Q"}],"same_information_nonreducibility":{"claim":"Q remains","why_each_baseline_cannot_express_prediction":"A lacks X and B lacks Y"},"exact_prediction":"Prediction Q changes sign.","strongest_same_information_baseline":"Theory A+B","domain_transfer_audit":{"mature_source_domain":"generic","mature_object":"Z","why_not_domain_transfer":"Q is not Z"},"saturation_scan":{"checked":True,"matched_patterns":[]},"cheapest_problem_falsifier":"Check Q before method design.","endpoint_headroom_requirement":"Two non-censored outcomes."}
    def gen(self,candidates,resolved="doubao-seed-evolving"):
        def responder(**kwargs):return {"text":json.dumps({"candidates":candidates}),"resolved_model":resolved}
        return responder
    def review(self,verdict="CLEAR",resolved="glm-5-2-260617",matched=None):
        def responder(**kwargs):return {"text":json.dumps({"reviews":[{"candidate_id":"AUTO-1","verdict":verdict,"matched_patterns":matched or [],"strongest_reduction":"none" if verdict=="CLEAR" else "mature reduction","reason":"review"}]}),"resolved_model":resolved}
        return responder

    def test_zero_candidates_is_valid_and_skips_reviewer(self)->None:
        calls=[]
        def reviewer(**kwargs):calls.append(1);raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json"
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=auto,generator_responder=self.gen([]),reviewer_responder=reviewer,now=now)
            inbox=json.loads(auto.read_text())
        self.assertEqual(state["status"],"GENERATED_ZERO_CANDIDATES");self.assertEqual(calls,[]);self.assertEqual(inbox["candidates"],[])

    def test_stale_pool_makes_zero_api_calls(self)->None:
        calls=[]
        def responder(**kwargs):calls.append(1);raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);old=now-timedelta(hours=72)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,old),auto_inbox_path=root/"auto.json",generator_responder=responder,reviewer_responder=responder,now=now)
        self.assertEqual(state["status"],"SKIPPED_STALE_PRIMARY_EVIDENCE");self.assertEqual(calls,[])

    def test_malformed_generator_archives_raw_and_clears_auto_inbox(self)->None:
        def bad(**kwargs):return {"text":"{bad json","resolved_model":"doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";auto.write_text(json.dumps({"candidates":[{"candidate_id":"OLD"}]}))
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=auto,generator_responder=bad,now=now);inbox=json.loads(auto.read_text())
            raw=Path(state["raw_artifacts"]["generator"]["path"]); raw_exists=raw.exists()
        self.assertEqual(state["status"],"GENERATOR_ERROR_ZERO_AUTHORITY");self.assertTrue(raw_exists);self.assertEqual(inbox["candidates"],[]);self.assertTrue(state["archived_previous_auto_inbox"])

    def test_clear_independent_review_can_only_reach_human_paper_design_queue(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([self.raw_candidate()]),reviewer_responder=self.review(),now=now)
            inbox=json.loads(auto.read_text());manual=root/"manual.json"
            queue=build_problem_gate_queue(manual,auto_inbox_path=auto,primary_pool_path=pool,storage=self.storage(root))
        c=inbox["candidates"][0]
        self.assertEqual(state["summary"]["semantic_clear"],1);self.assertEqual(c["empirical_contradiction"]["source_a"]["source_sha256"],"1"*64)
        self.assertEqual((queue["summary"]["passed_problem_gate"],queue["summary"]["paper_design_eligible"]),(1,1));self.assertEqual((queue["summary"]["method_authorized"],queue["summary"]["p0_authorized"]),(0,0))

    def test_semantic_blocker_prevents_problem_gate_pass(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([self.raw_candidate()]),reviewer_responder=self.review("BLOCK",matched=["update-order-path-dependence"]),now=now)
            queue=build_problem_gate_queue(root/"manual.json",auto_inbox_path=auto,primary_pool_path=pool,storage=self.storage(root))
        self.assertEqual(state["summary"]["semantic_blocked"],1);self.assertEqual(queue["summary"]["passed_problem_gate"],0);self.assertTrue(any("semantic-reduction-review-block"==x or x.startswith("saturation-pattern-match:") for x in queue["blocked"][0]["blockers"]))

    def test_same_resolved_model_is_not_independent(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([self.raw_candidate()],resolved="glm-5-2-260617"),reviewer_responder=self.review("CLEAR",resolved="glm-5-2-260617"),now=now)
            inbox=json.loads(auto.read_text())
        review=inbox["candidates"][0]["semantic_reduction_review"];self.assertFalse(review["independent_resolved_model"]);self.assertEqual(review["verdict"],"BLOCK");self.assertEqual(state["summary"]["semantic_clear"],0)


if __name__=="__main__":unittest.main()
