from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from .research_harness_meta_optimization import build_research_harness_meta_optimization, validate_meta_change_landing
from .research_integration_lint import build_research_integration_lint
from .research_stall_pivot_controller import load_research_stall_state, observe_research_stall

class ArisRound2ControlsTest(unittest.TestCase):
 def gen(self,cid=""):
  return {"run_id":"R","status":"GENERATED_ZERO_CANDIDATES","candidates":[{"candidate_id":cid}] if cid else [],"pre_f0_candidates":[],"saturation_memory":{"blocked_problem_memory":{"portable_blocked_problem_memory":[]}}}
 def test_integration_lint_live_wiring_and_orphan_detection(self):
  state=build_research_integration_lint();self.assertEqual(state["status"],"PASS_INTEGRATION_LINT");self.assertFalse(state["scientific_authority"])
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/"research_pipeline").mkdir();(root/"research_pipeline"/"research_memory_wiki.py").write_text("def compile_research_memory_query_pack():pass\nquery_pack_sha256='x'\nselected_memory_ids=[]\n")
   bad=build_research_integration_lint(root);self.assertEqual(bad["status"],"HOLD_INTEGRATION_LINT");self.assertGreater(bad["summary"]["orphan_required_integrations"],0)
 def test_stall_ladder_counts_new_findings_and_frame_change_resets(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"stall.jsonl";observe_research_stall(generator_state=self.gen("NEW"),operator_version="v1",path=path,generated_at="t0")
   one=observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,generated_at="t1");two=observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,generated_at="t2")
   self.assertEqual(one["summary"]["stale_count"],1);self.assertEqual(two["status"],"FORCE_STRUCTURAL_PIVOT")
   observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,generated_at="t3");four=observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,generated_at="t4");self.assertEqual(four["status"],"ESCALATE_HUMAN_REPLAN")
   changed=load_research_stall_state(path=path,current_frame_signature="different");self.assertEqual(changed["summary"]["stale_count"],0);self.assertTrue(changed["summary"]["frame_changed"])
 def test_execution_failure_is_not_scientific_stale(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"stall.jsonl";first=observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,execution_failed=True,generated_at="t")
   self.assertEqual(first["status"],"RECOVER_EXECUTION_WITHOUT_SCIENTIFIC_UPDATE");self.assertEqual(first["summary"]["stale_count"],0);self.assertFalse(first["scientific_authority"])
 def test_discovery_receipt_is_bound_into_stall_ledger(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"stall.jsonl"
   receipt={"status":"COMMITTED","transaction_id":"a"*64,"generator_receipt_sha256":"b"*64,"discovery_operator_version":"v1","scientific_authority":False}
   state=observe_research_stall(generator_state=self.gen("NEW"),operator_version="v1",path=path,transaction_receipt=receipt,generated_at="t")
   self.assertTrue(state["summary"]["discovery_receipt_bound"]);self.assertEqual(state["observation"]["discovery_transaction_id"],"a"*64)
   with self.assertRaises(ValueError):observe_research_stall(generator_state=self.gen(),operator_version="v1",path=path,transaction_receipt={**receipt,"scientific_authority":True})

 def test_meta_optimizer_proposes_and_separate_landing_gate_never_applies(self):
  state=build_research_harness_meta_optimization(integration_lint={"summary":{"failed":1}},stall_state={"summary":{"stale_count":2},"directive":{"action":"FORCE_STRUCTURAL_PIVOT"}},search_telemetry={"bottleneck":{"key":"FORMULATION_OR_EXACT_REDUCTION"}});self.assertGreaterEqual(state["summary"]["proposals"],2);self.assertFalse(state["authority"]["apply_patch"]);p=state["proposals"][0]
  bad=validate_meta_change_landing(p,{"explicit_human_approval":True,"author_model_family":"kimi","reviewer_model_family":"kimi","regression_tests_pass":True,"git_diff_sha256":"a"*64,"assurance_thresholds_unchanged":True});self.assertEqual(bad["status"],"LANDING_GATE_BLOCK")
  good=validate_meta_change_landing(p,{"explicit_human_approval":True,"author_model_family":"kimi","reviewer_model_family":"deepseek","regression_tests_pass":True,"git_diff_sha256":"a"*64,"assurance_thresholds_unchanged":True});self.assertEqual(good["status"],"LANDING_GATE_PASS");self.assertFalse(good["apply_authorized_by_this_function"])
if __name__=='__main__':unittest.main()
