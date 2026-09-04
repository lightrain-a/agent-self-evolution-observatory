from __future__ import annotations
import json, pathlib, tempfile, unittest
from research_pipeline import failure_memory_semantic_control_r68 as r68
from research_pipeline import failure_memory_semantic_control_r69 as r69

ROOT=pathlib.Path(__file__).resolve().parents[1]


def selected(i:int,success:bool=True):
 content=f"memory-{i}"
 import hashlib
 return {"rank":0,"memory_id":f"m{i}","memory_id_sha256":hashlib.sha256(f"m{i}".encode()).hexdigest(),"source_task_id":str(1000+i),"source_outcome_success":success,"content":content,"content_utf8_sha256":hashlib.sha256(content.encode()).hexdigest(),"eligible":True}


class SemanticControlR68Tests(unittest.TestCase):
 def test_renderer_decomposes_five_baselines(self):
  rec={"validation_task_id":"x","selected":[selected(1,True),selected(2,False)]}
  ctx=r68.render_arms(rec)
  self.assertEqual(set(ctx),set(r68.ARMS));self.assertEqual(ctx["N0_no_memory"],"")
  def payload(arm): return json.loads(ctx[arm].split("\n",1)[1])
  m,u,t,rv=map(payload,["M1_masked","P2_unknown","T3_truthful","R4_reversed"])
  self.assertNotIn(r68.FIELD,m[0]);self.assertEqual([x[r68.FIELD] for x in u],[r68.UNKNOWN,r68.UNKNOWN])
  self.assertEqual([x[r68.FIELD] for x in t],[True,False]);self.assertEqual([x[r68.FIELD] for x in rv],[False,True])
  core=lambda xs:[(x["position"],x["content"]) for x in xs]
  self.assertEqual(core(m),core(u));self.assertEqual(core(u),core(t));self.assertEqual(core(t),core(rv))
  self.assertEqual([set(x) for x in u],[set(x) for x in t]);self.assertEqual([set(x) for x in t],[set(x) for x in rv])

 def test_remaining_panel_is_all_unexposed_suffix(self):
  rows=[]
  for i in range(106):
   rows.append({"validation_task_id":str(i),"has_eligible_frozen_retrieval":True,"task_instruction":f"task-{i}","selected":[selected(i,i%2==0)]})
  frozen={"paper_id":r68.PAPER_ID,"validation_treatment_outcomes_observed":0,"rows":rows}
  old={"paper_id":r68.PAPER_ID,"selection_uses_validation_outcomes":False,"primary_representative_ids":[str(i) for i in range(32)],"utilization_representative_ids":[str(i) for i in range(32,40)]}
  old_hash=r68.PANEL_ID_SHA;r68.PANEL_ID_SHA=r68.ids_hash([str(i) for i in range(40,106)])
  try: panel=r68.select_panel(frozen,old)
  finally: r68.PANEL_ID_SHA=old_hash
  self.assertEqual(panel["fresh_unexposed_panel_count"],66);self.assertEqual(panel["representative_ids"][0],"40");self.assertEqual(panel["representative_ids"][-1],"105")
  self.assertEqual(panel["prior_primary_or_utilization_overlap_count"],0);self.assertFalse(panel["panel_selection_uses_new_outcomes"])

 def test_arm_randomization_is_frozen_per_model_and_task(self):
  for model in r68.MODELS:
   a=r68.arm_order(model,"377");b=r68.arm_order(model,"377")
   self.assertEqual(a,b);self.assertEqual(set(a),set(r68.ARMS));self.assertEqual(len(a),5)

 def test_checked_in_freeze_objects_are_zero_authority(self):
  names=["d2-failure-memory-provenance-r68-semantic-control-panel.json","d2-failure-memory-provenance-r68-semantic-control-renderer-audit.json","d2-failure-memory-provenance-r68-semantic-control-protocol.json","d2-failure-memory-provenance-r68-semantic-control-execution-hold.json"]
  paths=[ROOT/"generated"/n for n in names]
  if not all(p.exists() for p in paths): self.skipTest("R68 generated freeze artifacts not materialized yet")
  panel,audit,protocol,hold=[json.loads(p.read_text()) for p in paths]
  for x in [panel,audit,protocol,hold]: self.assertTrue(r68.valid(x))
  self.assertEqual(panel["fresh_unexposed_panel_count"],66);self.assertEqual(panel["representative_ids_sha256"],r68.PANEL_ID_SHA)
  self.assertEqual(protocol["execution"]["planned_arm_runs"],660);self.assertEqual(protocol["analysis"]["primary_contrast"],["T3_truthful","P2_unknown"])
  self.assertFalse(hold["authority"]["semantic_control_execution"]);self.assertEqual(hold["new_treatment_outcomes_observed"],0)
  qm=json.loads((ROOT/"generated/d2-failure-memory-provenance-r53-full350-source-execution-manifest.json").read_text());lm=json.loads((ROOT/"generated/d2-failure-memory-provenance-r59-llama-executor-replication-manifest.json").read_text())
  r54path=pathlib.Path('/tmp/b1-r68-r54/fresh-frozen-retrieval.json')
  if r54path.exists():
   r54=json.loads(r54path.read_text());patched=r69.static_preflight(protocol,panel,hold,qm,lm,r54,r54path);self.assertEqual(set(patched),{"qwen","llama"})
  else:self.assertEqual(protocol["bindings"]["r54_frozen_retrieval_file_sha256"],r68.R54_FROZEN_SHA)

 def test_execution_runner_refuses_checked_in_hold(self):
  protocol={"receipt_sha256":"p"};authority={"protocol_receipt_sha256":"p","authority":{"semantic_control_execution":False},"receipt_sha256":"bad"}
  with self.assertRaises(RuntimeError): r69.authorized(authority,protocol)


if __name__=="__main__": unittest.main()
