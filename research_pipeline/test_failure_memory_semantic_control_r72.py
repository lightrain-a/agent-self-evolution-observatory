from __future__ import annotations
import hashlib,json,pathlib,unittest
from research_pipeline import failure_memory_semantic_control_r72 as r72
from research_pipeline import failure_memory_semantic_control_r73 as r73

ROOT=pathlib.Path(__file__).resolve().parents[1];GEN=ROOT/"generated"
FILES={
 "panel":GEN/"d2-failure-memory-provenance-r68-semantic-control-panel.json",
 "r70":GEN/"d2-failure-memory-provenance-r70-semantic-control-r2-protocol.json",
 "r2":GEN/"d2-failure-memory-provenance-r72-independent-r2-review-summary.json",
 "renderer":GEN/"d2-failure-memory-provenance-r72-semantic-control-r3-renderer-audit.json",
 "protocol":GEN/"d2-failure-memory-provenance-r72-semantic-control-r3-protocol.json",
 "hold":GEN/"d2-failure-memory-provenance-r72-semantic-control-r3-execution-hold.json",
}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def valid(x):
 r=x["receipt_sha256"];y=dict(x);y.pop("receipt_sha256");return r==hashlib.sha256(json.dumps(y,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class SemanticControlR72Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x={k:load(v) for k,v in FILES.items()}

 def test_receipts_valid_and_r2_is_real_finished_review(self):
  for k,v in self.x.items():self.assertTrue(valid(v),k)
  r=self.x["r2"];self.assertEqual(r["verdict"],"REVISE_R70_BEFORE_EXECUTION")
  self.assertTrue(r["review_surface"]["assistant_end_turn"])
  self.assertEqual(r["review_surface"]["assistant_message_status"],"finished_successfully")
  self.assertEqual(r["review_surface"]["resolved_model_slug"],"gpt-5-6-thinking")
  self.assertEqual(r["review_surface"]["assistant_text_sha256"],"a135d5d8033c12d721ef73f11411528645d34c9afb7be645245be4fdef9438b5")

 def test_r72_is_versioned_successor_not_silent_r70_mutation(self):
  p=self.x["protocol"];old=self.x["r70"]
  self.assertEqual(p["status"],r72.STATUS)
  self.assertEqual(p["bindings"]["parent_r70_protocol_file_sha256"],r72.R70_PROTOCOL_FILE_SHA)
  self.assertEqual(p["bindings"]["parent_r70_protocol_receipt_sha256"],old["receipt_sha256"])
  self.assertEqual(p["bindings"]["r72_r2_review_receipt_sha256"],self.x["r2"]["receipt_sha256"])
  self.assertEqual(p["run_matrix"]["total_new_trajectories"],321)
  self.assertEqual(p["run_matrix"],old["run_matrix"])

 def test_exact_shuffle_realizations_are_content_addressed(self):
  p=self.x["protocol"];sf=p["shuffle_freeze"];rows=sf["assignments"]
  self.assertEqual(sf["seed"],r72.SHUFFLE_SEED);self.assertEqual(len(rows),57)
  self.assertEqual(sf["assignments_sha256"],r72.digest(rows))
  tids=set()
  for row in rows:
   tid=str(row["task_id"]);self.assertNotIn(tid,tids);tids.add(tid)
   truth=list(row["truthful_code_sequence"]);shuf=list(row["shuffled_code_sequence"])
   self.assertEqual(sorted(truth),sorted(shuf));self.assertNotEqual(truth,shuf)
   self.assertEqual(row["truthful_code_sequence_sha256"],r72.digest(truth))
   self.assertEqual(row["shuffled_code_sequence_sha256"],r72.digest(shuf))
   self.assertEqual(shuf,r72.shuffled_codes(tid,truth))
  self.assertEqual(tids,set(p["units"]["mixed_provenance_ids"]))

 def test_renderer_freezes_exact_sequences(self):
  a=self.x["renderer"]
  self.assertTrue(a["checks"]["exact_per_unit_S_sequence_content_addressed"])
  self.assertTrue(a["checks"]["preexposure_retries_must_reuse_exact_S_sequence"])
  mixed=[x for x in a["rows"] if x["mixed_provenance"]]
  self.assertEqual(len(mixed),57)
  self.assertTrue(all(isinstance(x["truthful_code_sequence"],list) and isinstance(x["shuffled_code_sequence"],list) for x in mixed))

 def test_worst_case_sign_test_blocks_reviewer_counterexample(self):
  effects=[(str(i),True,False) for i in range(6)]
  s=r73.exact_stats(effects,7)
  self.assertAlmostEqual(s["exact_two_sided_signflip_p"],0.03125)
  self.assertGreater(s["technical_missing_worst_best_rd_bounds"][0],0)
  self.assertAlmostEqual(s["technical_missing_worst_case_signflip_p"],0.125)
  self.assertEqual(s["technical_missing_worst_case_signflip_completion"]["right_only_added"],1)
  self.assertFalse(s["technical_missing_significance_robust"])
  self.assertFalse(s["effect_detected"])

 def test_no_missing_six_zero_can_still_detect(self):
  s=r73.exact_stats([(str(i),True,False) for i in range(6)],6)
  self.assertAlmostEqual(s["technical_missing_worst_case_signflip_p"],0.03125)
  self.assertTrue(s["technical_missing_rd_direction_robust"])
  self.assertTrue(s["technical_missing_significance_robust"])
  self.assertTrue(s["effect_detected"])

 def test_all_confirmatory_gates_share_robust_missingness_rule(self):
  a=self.x["protocol"]["analysis"]
  for text in [a["primary"]["decision"]["EFFECT_DETECTED"],a["gatekept_correctness"]["correctness_sensitive"],a["executor_replication"]["successful_replication"]]:
   self.assertIn("worst-case",text)
  self.assertIn("maximum two-sided exact paired sign-test p-value",self.x["protocol"]["failure_policy"]["post_exposure"]["missing_pair_sensitivity"])

 def test_r73_runner_bound_and_execution_still_closed(self):
  p=self.x["protocol"];h=self.x["hold"]
  self.assertEqual(p["bindings"]["r73_execute_runner_sha256"],r72.sha(pathlib.Path(r73.__file__).resolve()))
  self.assertEqual(h["status"],"HOLD_R72_REQUIRES_INDEPENDENT_R3_REVIEW_BEFORE_EXECUTION")
  self.assertTrue(all(v is False for v in h["authority"].values()))
  self.assertFalse(h["scientific_authority"] or h["experiment_authority"] or h["gpu_authority"])

if __name__=="__main__":unittest.main()
