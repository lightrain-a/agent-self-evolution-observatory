from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"generated"/"relational-constraint-capacity-novelty-support-differential-20260831.json"
OLD=ROOT/"generated"/"relational-constraint-capacity-construct-v2-20260830.json"
PORT=ROOT/"generated"/"paper-first-pre-f0-evidence-acquisition-plan.json"
EXPECTED="465dbbf9d2f1bb6aadad73681dac994e252b7201966e069d9b5c5e2dd7d16b83"

def sha(path: Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

class NoveltySupportDifferentialTest(unittest.TestCase):
 def setUp(self)->None:
  self.a=json.loads(ART.read_text(encoding="utf-8"))

 def test_content_address_and_parent_state(self)->None:
  self.assertEqual(sha(ART),EXPECTED)
  self.assertEqual(self.a["object_id"],"RELATIONAL-CONSTRAINT-CAPACITY-20260830")
  self.assertEqual(self.a["lifecycle_phase"],"PRE_F0")
  self.assertEqual(self.a["parent_status_preserved"],
                   "PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY")
  self.assertEqual(self.a["novelty_gate"],
                   "PRE_F0_NOVELTY_AND_SUPPORT_DIFFERENTIAL")
  self.assertFalse(self.a["revision_policy"]["overwrites_historical_construct"])
  self.assertEqual(self.a["revision_policy"]["scientific_gpu_runs"],0)
  self.assertEqual(sha(OLD),self.a["source_pins"]["prior_artifacts"]["construct_v2"])

 def test_sources_are_pinned(self)->None:
  sn=self.a["source_pins"]["scenenat"]
  self.assertEqual(sn["revision"],"v2")
  self.assertTrue(sn["latest_at_audit"])
  self.assertEqual(sn["repo_sha"],"542b82ff0cda4e0350575ca8f1cd5d147529130c")
  self.assertRegex(sn["pdf_sha256"],r"^[0-9a-f]{64}$")
  self.assertRegex(sn["source_tar_sha256"],r"^[0-9a-f]{64}$")
  self.assertEqual(
   self.a["source_pins"]["instructscene"]["repo_sha"],
   "a9097a62c484c56ac7be5ec2928ef497cbbaaf24")

 def test_collision_matrix_has_all_levels_and_rejects_scalar_story(self)->None:
  rows=self.a["scenenat_audit"]["collision_matrix"]
  self.assertEqual({r["collision_level"] for r in rows},
                   {"DIRECT_COLLISION","PARTIAL_COLLISION","NON_COLLISION"})
  self.assertGreaterEqual(len(rows),8)
  for r in rows:
   self.assertTrue(r["ours_claim"])
   self.assertTrue(r["scenenat_claim"])
   self.assertTrue(r["residual_novelty"])
   self.assertTrue(r["required_falsifier"])
  rejected=" ".join(self.a["rejected_claims"])
  self.assertIn("more relations lower iRecall",rejected)
  self.assertIn("relation-aware high-count superiority",rejected)
  self.assertIn("another three-baseline curve",rejected)

 def test_scenenat_protocol_audit(self)->None:
  s=self.a["scenenat_audit"]
  self.assertEqual(s["train_relation_support"],[1,2,3,4])
  self.assertEqual(s["evaluation"]["in_support"],[1,2,3,4])
  self.assertEqual(s["evaluation"]["ood"],[5,6])
  self.assertEqual(set(s["baselines"]),{"ATISS","DiffuScene","InstructScene","qualification"})
  self.assertIn("triplets",s["irecall_definition"])
  self.assertEqual(s["curve_scope"]["relation_counts"],[1,2,3,4,5,6])
  self.assertIn("without_rrm",s["rrm_ablations"])

 def test_training_support_is_not_confused_with_count(self)->None:
  t=self.a["training_support_audit"]
  self.assertEqual(t["original_instructscene"]["support"],[1,2])
  self.assertEqual(t["original_instructscene"]["labels"]["3"],
                   "OUT_OF_SUPPORT_RELATION_LOAD")
  self.assertEqual(t["scenenat_retrained_instructscene"]["support"],[1,2,3,4])
  self.assertIn("collinear",t["identifiability"]["single_original_checkpoint"])
  self.assertEqual(set(t["dose_fields"]),{
   "relation_count","training_support_status","exact_clip_token_count",
   "tokenizer_truncated","relation_family_composition",
   "graph_topology_statistics"})
  self.assertEqual(t["primary_exclusion"],"tokenizer_truncated == true")

 def test_revision_question_topology_and_analysis(self)->None:
  r=self.a["revision"]
  self.assertEqual(r["exact_question"],
   "What actually limits relational instruction following in 3D scene generation: "
   "semantic relation load, surface length, training-support shift, or relational "
   "topology, and at which generation stage does failure emerge?")
  self.assertIn("training_support_regime",r["response_surface"])
  self.assertFalse(r["breakpoint"]["mandatory"])
  self.assertIn("smooth degradation",r["breakpoint"]["rule"])
  self.assertEqual(set(r["topology"]["conditions"]),{
   "low_coupling_disjoint","shared_anchor_hub","chain",
   "long_range_coupling","high_degree_relation_graph"})
  self.assertIn("same relation count",r["topology"]["matching"])
  self.assertIn("relation_count_c * clip_token_count_c",
                r["analysis"]["formula"])
  self.assertIn("training_support_regime",r["analysis"]["formula"])
  self.assertIn("(1 + relation_count_c | base_scene_id)",
                r["analysis"]["formula"])

 def test_stage_localization_and_oracle_rule(self)->None:
  s=self.a["revision"]["stage"]
  self.assertEqual(s["observables"],[
   "text_to_graph_relation_recall","graph_to_scene_relation_retention",
   "end_to_end_relation_iRecall"])
  self.assertEqual(len(s["arms"]),2)
  self.assertIn("same fixed layout decoder",s["arms"][1])
  self.assertIn("instance IDs",s["identity_rule"])
  rules=s["interpretation"]
  self.assertEqual(rules["text_graph_down_oracle_stable"],
                   "OPERATIONAL_LOCALIZATION_TO_STRUCTURALIZATION")
  self.assertEqual(rules["text_graph_stable_scene_down"],
                   "OPERATIONAL_LOCALIZATION_TO_REALIZATION")
  self.assertEqual(rules["both_down"],"DISTRIBUTED_ATTENUATION")
  self.assertEqual(rules["oracle_cannot_repair"],
                   "LANGUAGE_TO_STRUCTURE_BOTTLENECK_CLAIM_FORBIDDEN")
  self.assertIn("!=",rules["boundary"])

 def test_verdict_and_authority_firewall(self)->None:
  self.assertEqual(self.a["adjudication"]["verdict"],"PRE_F0_REFORMULATE")
  self.assertEqual(self.a["revision"]["decisive_experiment"]["runs_this_round"],0)
  self.assertFalse(any(self.a["authority"].values()))
  self.assertEqual(self.a["baseline_policy"]["train_now"],[])
  self.assertEqual(self.a["gates"]["gpu"],"NOT_REQUESTED")
  self.assertEqual(self.a["gates"]["P1"],"NOT_AUTHORIZED")

 def test_port010_stays_held(self)->None:
  plan=json.loads(PORT.read_text(encoding="utf-8"))
  rows=[r for r in plan["entries"] if r.get("candidate_id")=="PORT-010"]
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]["status"],"HOLD_EVIDENCE_REVIEW_BLOCKED")
  self.assertEqual(rows[0]["evidence_review"]["verdict"],"BLOCK_BAKE_IN")
  self.assertEqual(self.a["relation_to_port010"]["status"],
                   "HOLD_EVIDENCE_REVIEW_BLOCKED")
  self.assertEqual(self.a["relation_to_port010"]["evidence_review"],
                   "BLOCK_BAKE_IN")
  self.assertFalse(self.a["relation_to_port010"]["changed"])

if __name__=="__main__": unittest.main()
