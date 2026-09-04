from __future__ import annotations
import hashlib,json,pathlib,unittest
from research_pipeline import failure_memory_semantic_control_r70 as r70
from research_pipeline import failure_memory_semantic_control_r71 as r71

ROOT=pathlib.Path(__file__).resolve().parents[1]
GEN=ROOT/"generated"
FILES={
 "panel":GEN/"d2-failure-memory-provenance-r68-semantic-control-panel.json",
 "token":GEN/"d2-failure-memory-provenance-r70-tokenizer-footprint-audit.json",
 "review":GEN/"d2-failure-memory-provenance-r70-independent-preexec-review-summary.json",
 "renderer":GEN/"d2-failure-memory-provenance-r70-semantic-control-r2-renderer-audit.json",
 "protocol":GEN/"d2-failure-memory-provenance-r70-semantic-control-r2-protocol.json",
 "hold":GEN/"d2-failure-memory-provenance-r70-semantic-control-r2-execution-hold.json",
}

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def valid(x):
 r=x["receipt_sha256"];y=dict(x);y.pop("receipt_sha256");return r==hashlib.sha256(json.dumps(y,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class SemanticControlR70Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.x={k:load(v) for k,v in FILES.items()}

 def test_all_checked_in_receipts_are_content_valid(self):
  for k,v in self.x.items():
   if k=="panel":self.assertTrue(valid(v),k)
   else:self.assertTrue(valid(v),k)

 def test_independent_review_is_reduce_or_redirect(self):
  r=self.x["review"]
  self.assertEqual(r["verdict"],"REDUCE_OR_REDIRECT")
  self.assertEqual(r["review_surface"]["model"],"GPT-5.6 Sol")
  self.assertEqual(r["review_surface"]["thinking_effort"],"Extra High, 4 of 5")
  self.assertFalse(r["review_surface"]["faster_model_retry_used"])
  self.assertEqual(r["recommended_matrix"]["total_new_trajectories"],321)

 def test_format_matching_blocker_is_repaired(self):
  t=self.x["token"];p=self.x["protocol"]
  self.assertEqual(t["field_schema"]["value_type"],"string")
  self.assertEqual(t["field_schema"]["codes"],{"success":"S","failure":"F","unknown":"U"})
  self.assertEqual(t["checks"]["token_count_mismatches"],0)
  for k in ["Qwen_P_T_equal_token_count_all_66","Qwen_P_T_S_equal_token_count_all_57_mixed","Llama_P_T_equal_token_count_all_66","Llama_P_T_S_equal_token_count_all_57_mixed"]:self.assertTrue(t["checks"][k])
  self.assertTrue(p["field_control"]["same_token_footprint_verified_for_both_executor_tokenizers"])

 def test_321_matrix_removes_non_verdict_changing_arms(self):
  p=self.x["protocol"];m=p["run_matrix"]
  self.assertEqual(m["Qwen"],{"P_neutral":66,"T_truthful":66,"S_shuffled":57,"total":189})
  self.assertEqual(m["Llama"],{"P_neutral":66,"T_truthful":66,"S_shuffled":0,"total":132})
  self.assertEqual(m["total_new_trajectories"],321)
  self.assertEqual(m["reduction_vs_rejected_R68_660"],339)
  self.assertTrue(p["hard_limits"]["no_N0_no_memory"] and p["hard_limits"]["no_M1_masked"] and p["hard_limits"]["no_R4_reversed"])

 def test_shuffle_is_only_mixed_and_count_preserving(self):
  p=self.x["protocol"];a=self.x["renderer"]
  self.assertEqual(p["units"]["mixed_provenance_count"],57)
  self.assertEqual(a["mixed_units"],57)
  self.assertTrue(a["checks"]["S_is_nonidentity_count_preserving_within_retrieval_shuffle"])
  mixed={x["task_id"] for x in a["rows"] if x["mixed_provenance"]}
  scheduled={x["task_id"] for x in p["staging"]["Qwen"]["schedule"] if x["arm"]=="S_shuffled"}
  self.assertEqual(mixed,scheduled)
  self.assertFalse(any(x["arm"]=="S_shuffled" for x in p["staging"]["Llama"]["schedule"]))

 def test_primary_hierarchy_cannot_be_rescued_by_diagnostics(self):
  a=self.x["protocol"]["analysis"]
  self.assertEqual(a["primary"]["contrast"],"T_truthful - P_neutral")
  self.assertEqual(a["primary"]["n"],66)
  self.assertTrue(a["gatekept_correctness"]["opens_confirmatory_interpretation_only_if_primary_EFFECT_DETECTED"])
  self.assertEqual(a["gatekept_correctness"]["contrast"],"T_truthful - S_shuffled")
  self.assertEqual(a["gatekept_correctness"]["n"],57)
  self.assertEqual(a["diagnostics"]["first_executable_action"],"descriptive_only")
  self.assertIn("does not imply equivalence",a["primary"]["decision"]["NO_EFFECT_DETECTED"])

 def test_llama_is_fixed_executor_only_replication(self):
  p=self.x["protocol"]
  self.assertTrue(p["staging"]["Llama"]["design_frozen_before_Qwen_exposure"])
  self.assertTrue(p["staging"]["Llama"]["commitment_to_run_independent_of_Qwen_result"])
  self.assertTrue(p["analysis"]["executor_replication"]["no_pooling"])
  self.assertTrue(p["hard_limits"]["no_change_to_Llama_design_or_run_commitment_after_Qwen_open"])

 def test_retry_boundary_is_treatment_exposure(self):
  f=self.x["protocol"]["failure_policy"]
  self.assertEqual(f["scientific_boundary"],"treatment exposure, not durable STARTED")
  self.assertEqual(f["pre_exposure_infrastructure_failure"]["max_total_attempts_same_unit_arm"],3)
  self.assertFalse(f["pre_exposure_infrastructure_failure"]["replacement"])
  self.assertIn("no rerun",f["post_exposure"]["genuine_external_technical_failure"])
  self.assertIn("worst/best",f["post_exposure"]["missing_pair_sensitivity"])

 def test_checked_in_execution_hold_remains_closed(self):
  h=self.x["hold"];self.assertEqual(h["planned_trajectories"],321)
  self.assertTrue(all(v is False for v in h["authority"].values()))
  self.assertFalse(h["scientific_authority"] or h["experiment_authority"] or h["gpu_authority"])

 def test_runner_is_bound_and_static_math_handles_missingness(self):
  p=self.x["protocol"]
  self.assertEqual(p["bindings"]["r71_execute_runner_sha256"],r70.sha(pathlib.Path(r71.__file__).resolve()))
  # One observed +1 among three planned pairs, two technical-missing pairs: sensitivity includes zero, so no confirmatory detection.
  st=r71.exact_stats([("x",True,False)],3)
  self.assertEqual(st["technical_missing_pairs"],2)
  self.assertLessEqual(st["technical_missing_worst_best_rd_bounds"][0],0)
  self.assertGreaterEqual(st["technical_missing_worst_best_rd_bounds"][1],0)
  self.assertFalse(st["effect_detected"])

if __name__=="__main__":unittest.main()
