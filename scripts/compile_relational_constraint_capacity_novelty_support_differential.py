from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ = "RELATIONAL-CONSTRAINT-CAPACITY-20260830"
OLD_SHA = "0451add2c9bd28740b80f436e3c626b1957e3c3e"
BASE_SHA = "47a8ba35966149bfa6e205304b17c21af72d0804"
SN_SHA = "542b82ff0cda4e0350575ca8f1cd5d147529130c"
IS_SHA = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
H = {
 "sn_pdf":"682f59c77e9aa1caf41550fab959073cff7b506486435e7507555f69ad7dc970",
 "sn_src":"92263ceba8e7883c1bb6bf86c40fc536d44d144195a0a679b17b3bbcea13dfd5",
 "sn_readme":"3fd616a6d0ae41e9875aa78be863f02c48d688bbb9aa4f427c30cdba212f5955",
 "sn_text":"33ac4087f494cde06bf0b0de081f65af4d50726a4b5c903734c6fbee704ffab6",
 "sn_train":"49fe103c026b2ea59a5aea0856b92db86b02fc9758720751483f1ac3baa78665",
 "is_text":"3cafdca0515cf0dba8fec4eed9146cfa4c2c321f1199ba6cd27765527a6ab6d2",
 "is_gen":"ea6f532d12a7d511902e6e72d84e0c9e61ddee8b632061b518327bc8956753cd",
 "construct":"48a86fa4bb83cdb9308a1cd6a005cf8ea34033f8649cd579c15fbe3e8347317f",
 "old_adj":"cfc91edee5e6315f2e765628316a6ffa61f2521da4c5cfb557dd5c5b8edad92b",
 "port":"3594967e2e491984e522b4b53c10c0478848ecd34cc2287d718e175360861ebd",
}

def sha(path: Path) -> str:
 d=hashlib.sha256()
 with path.open("rb") as f:
  while b:=f.read(4*1024*1024): d.update(b)
 return d.hexdigest()

def check(path: Path, expected: str) -> None:
 actual=sha(path)
 if actual != expected: raise SystemExit(f"drift {path}: {actual}")

def repo(path: Path, expected: str, files: dict[str,str]) -> None:
 head=subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
 if head != expected: raise SystemExit(f"commit drift {path}: {head}")
 if subprocess.check_output(["git","-C",str(path),"status","--porcelain"],text=True):
  raise SystemExit(f"dirty repo: {path}")
 for name,digest in files.items(): check(path/name,digest)

def row(ours: str, theirs: str, level: str, residual: str, falsifier: str) -> dict:
 return {"ours_claim":ours,"scenenat_claim":theirs,"collision_level":level,
         "residual_novelty":residual,"required_falsifier":falsifier}

def build() -> dict:
 matrix=[
  row("more relations -> lower iRecall","1-6 iRecall curves; InstructScene degrades with complexity",
      "DIRECT_COLLISION","NONE_AS_STANDALONE_CLAIM","remove from novelty core"),
  row("relation-aware model works better at high relation count",
      "SceneNAT attributes robustness to RRM auxiliary triplet supervision",
      "DIRECT_COLLISION","NONE_AS_MODEL_RANKING_CLAIM","no graph-vs-non-graph novelty claim"),
  row("ATISS/DiffuScene/InstructScene relation-count comparison",
      "same baselines are retrained and plotted at counts 1-6",
      "DIRECT_COLLISION","NONE_FROM_REPLOTTING","retain only a mechanism-discriminating baseline"),
  row("3-6 decline reveals intrinsic InstructScene capacity",
      "5-6 are tested above SceneNAT training maximum 4",
      "PARTIAL_COLLISION","separate support shift from count",
      "cross matched same-architecture 1-2 and 1-4 support regimes"),
  row("semantic load differs from surface/token length",
      "SceneNAT notes CLIP truncation and prunes 5-6 prompts but does not cross count and length",
      "PARTIAL_COLLISION","factorial count-by-exact-token response surface",
      "length explains outcome and adjusted count effect is negligible"),
  row("matched topology changes outcomes within count",
      "no matched fixed-count/fixed-length topology manipulation is reported",
      "NON_COLLISION","topology-sensitive response surface",
      "all topology contrasts meet equivalence bounds"),
  row("oracle graph localizes two-stage attenuation",
      "no same-decoder predicted-graph versus instructed-graph intervention is reported",
      "NON_COLLISION","stage-localized attenuation",
      "oracle graph cannot repair retention or pairing is invalid"),
  row("mandatory scalar breakpoint C*","no universal change point is established",
      "NON_COLLISION","mandatory breakpoint premise rejected",
      "C* only if segmented model beats smooth alternative"),
 ]
 authority={k:False for k in ["gpu","scientific_execution","official_training","p1",
                              "data_license_request","provider"]}
 return {
  "schema_version":"relational-constraint-capacity-novelty-support-differential-v1",
  "generated_at":"2026-08-31T00:00:00+00:00","object_id":OBJ,
  "lifecycle_phase":"PRE_F0",
  "parent_status_preserved":"PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY",
  "novelty_gate":"PRE_F0_NOVELTY_AND_SUPPORT_DIFFERENTIAL",
  "historical_canonical_sha":OLD_SHA,"base_canonical_sha":BASE_SHA,
  "revision_policy":{"mode":"VERSIONED_CHILD_PROPOSAL","overwrites_historical_construct":False,
   "historical_construct_sha256":H["construct"],"historical_smoke_overwritten":False,
   "scientific_gpu_runs":0},
  "source_pins":{
   "scenenat":{"arxiv_id":"2601.07218","revision":"v2","latest_at_audit":True,
    "v1_date":"2026-01-12","v2_date":"2026-08-11",
    "url":"https://arxiv.org/abs/2601.07218","pdf_sha256":H["sn_pdf"],
    "source_tar_sha256":H["sn_src"],
    "source_file_sha256":{"sec/4_experiment.tex":"5ea914ae960d2fe08988d3f4374050c64723e1c7924166dfdd49de86f028cc79",
     "figure/main_fig3_fig4.tex":"e3c1550574419f1474ca62f2d261260cbdbb763f3196a9662e358930c5bef8fd",
     "sec/appendix.tex":"698c1c8f5c6f31aa2e3b914b897cd091ff3616be96571e09e86fa8623950a6fa"},
    "official_repo":"https://github.com/lojol2327/SceneNAT-official",
    "repo_sha":SN_SHA,"repo_date":"2026-08-09T19:49:26+09:00",
    "repo_file_sha256":{"README.md":H["sn_readme"],"src/data/utils_text.py":H["sn_text"],
                        "src/tasks/train.py":H["sn_train"]}},
   "instructscene":{"official_repo":"https://github.com/chenguolin/InstructScene",
    "repo_sha":IS_SHA,"repo_date":"2026-02-25T23:56:30+08:00",
    "file_sha256":{"src/data/utils_text.py":H["is_text"],"src/generate_sg.py":H["is_gen"]}},
   "prior_artifacts":{"construct_v2":H["construct"],"pre_f0_adjudication":H["old_adj"],
                      "port_plan":H["port"]}},
  "scenenat_audit":{
   "dataset":"extended InstructScene 3D-FRONT/3D-FUTURE dataset",
   "instruction_construction":["diverse templates","symmetric-pair filtering",
     "discourse ordering with object reuse","regulated referring expressions"],
   "train_relation_support":[1,2,3,4],
   "train_sampling":"uniform randint 1..min(4, available unique relation pairs)",
   "evaluation":{"in_support":[1,2,3,4],"ood":[5,6],
     "ood_text_policy":"prune non-essential words to avoid truncation"},
   "baselines":{"ATISS":"autoregressive","DiffuScene":"continuous diffusion",
     "InstructScene":"two-stage semantic graph then layout diffusion",
     "qualification":"all reimplemented/retrained on SceneNAT refined 1-4 instructions"},
   "irecall_definition":"recall of instructed spatial-relation triplets realized in the scene",
   "curve_scope":{"room_types":["bedroom","living_room","dining_room"],
                  "models":["ATISS","DiffuScene","InstructScene","SceneNAT"],
                  "relation_counts":[1,2,3,4,5,6],"published_coordinates_pinned_in_source":True},
   "rrm_ablations":{"full_relation_supervision":{"fid":110.76,"irecall":65.16},
     "without_rrm":{"fid":110.91,"irecall":62.77},
     "full":{"fid":109.55,"irecall":70.45},
     "layers_irecall":{"1":65.87,"2":70.45,"3":68.50,"4":67.54},
     "relational_attention_irecall":65.04,
     "claim":"masked modeling plus RRM/triplet supervision supports robustness"},
   "collision_matrix":matrix,
  },
  "training_support_audit":{
   "original_instructscene":{"code_rule":"min(choice([1,2]), available); sample without replacement",
    "support":[1,2],"conditional_distribution":"50/50 if >=2 eligible; forced 1 if one eligible",
    "empirical_realized_distribution":"NOT_RECOVERABLE_WITHOUT_FROZEN_TRAINING_RNG_TRACE",
    "labels":{"1":"IN_SUPPORT_RELATION_LOAD","2":"IN_SUPPORT_RELATION_LOAD",
      "3":"OUT_OF_SUPPORT_RELATION_LOAD","4":"OUT_OF_SUPPORT_RELATION_LOAD",
      "5":"OUT_OF_SUPPORT_RELATION_LOAD","6":"OUT_OF_SUPPORT_RELATION_LOAD"},
    "forbidden":"3-6 decline is not direct evidence of intrinsic capacity"},
   "scenenat_retrained_instructscene":{"support":[1,2,3,4],"ood":[5,6],
    "warning":"counts 3-4 are in-support for this curve, unlike original InstructScene"},
   "identifiability":{"single_original_checkpoint":"count and support status are collinear",
    "required":"same architecture, matched corpus, 1-2 versus 1-4 support regimes on common doses",
    "status":"NOT_YET_CROSSED"},
   "dose_fields":["relation_count","training_support_status","exact_clip_token_count",
    "tokenizer_truncated","relation_family_composition","graph_topology_statistics"],
   "primary_exclusion":"tokenizer_truncated == true",
  },
  "revision":{
   "id":"RCC-20260830-R1-TOPOLOGY-STAGE-SUPPORT",
   "exact_question":("What actually limits relational instruction following in 3D scene generation: "
    "semantic relation load, surface length, training-support shift, or relational topology, "
    "and at which generation stage does failure emerge?"),
   "response_surface":"relation_count × exact_clip_token_count × training_support_regime × topology",
   "endpoints":{"primary":"relation_level_iRecall","secondary":"exact_all_success"},
   "breakpoint":{"mandatory":False,"role":"SECONDARY_DERIVED_ONLY",
    "rule":"report C* only if segmented/change-point model is supported; else smooth degradation"},
   "topology":{"matching":["same object-instance universe","same relation count",
      "matched relation-family composition","matched exact CLIP token count","no truncation"],
    "conditions":{"low_coupling_disjoint":"max degree 1; one component per edge",
      "shared_anchor_hub":"one anchor incident to every edge; high-degree extreme",
      "chain":"connected acyclic; max degree 2",
      "long_range_coupling":"upper-quantile base-graph distance/component-bridging pairs",
      "high_degree_relation_graph":"continuous max-degree/degree-concentration; hub is categorical extreme"},
    "statistics":["node_count","edge_count","connected_component_count",
      "largest_component_node_fraction","maximum_degree","mean_degree","degree_concentration",
      "cycle_rank","base_graph_pair_distance_mean","component_bridge_fraction"],
    "rule":"material within-count topology effect forbids scalar count-capacity mainline"},
   "stage":{"observables":["text_to_graph_relation_recall",
      "graph_to_scene_relation_retention","end_to_end_relation_iRecall"],
    "arms":["Text -> predicted graph -> fixed layout decoder",
            "Ground-truth instructed graph -> same fixed layout decoder"],
    "held_fixed":["SG2SC checkpoint/decoder","seed policy","floor plan",
      "scene/object-instance universe","object-feature/VQ carrier","evaluator"],
    "identity_rule":"stable instance IDs and one-to-one nodes; exclude ambiguous class aliases",
    "code_feasibility":"generate_sg.py exposes objs/edges before the SG2SC call and scores graph/layout",
    "interpretation":{"text_graph_down_oracle_stable":"OPERATIONAL_LOCALIZATION_TO_STRUCTURALIZATION",
      "text_graph_stable_scene_down":"OPERATIONAL_LOCALIZATION_TO_REALIZATION",
      "both_down":"DISTRIBUTED_ATTENUATION",
      "oracle_cannot_repair":"LANGUAGE_TO_STRUCTURE_BOTTLENECK_CLAIM_FORBIDDEN",
      "boundary":"where attenuation occurs != why attenuation occurs"}},
   "analysis":{"primary_unit":"instructed relation within scene-dose-seed",
    "primary_model":"binomial mixed-effects response surface",
    "formula":("realized ~ relation_count_c * clip_token_count_c * training_support_regime * "
      "topology + relation_family + (1 + relation_count_c | base_scene_id) + "
      "(1 | instruction_template_id) + (1 | seed_id)"),
    "support_rule":"cross 1-2 and 1-4 matched support regimes; do not fit support from one checkpoint",
    "stage_rule":"same fixed effects per observable plus paired oracle-minus-predicted contrasts",
    "secondary":"exact-all binomial mixed model with same fixed factors",
    "shape_rule":"smooth default; segmented comparison secondary; no forced C*",
    "exclusions":["truncated prompts from primary","no outcome-driven topology relabeling",
                  "no post-outcome endpoint reordering"]},
   "decisive_experiment":{"name":"MATCHED_TOPOLOGY_SUPPORT_CROSSOVER_WITH_ORACLE_GRAPH",
    "design":"cross count, token length, topology and matched 1-2/1-4 support regimes; paired graph arms",
    "readout":"within-count topology/support effects plus structuralization/realization localization",
    "runs_this_round":0},
  },
  "baseline_policy":{"full_suite":"PAUSED","minimum_after_requalification":{
    "InstructScene":"stage localization and matched support regimes",
    "SceneNAT":"relation-resistant comparator; source-reported first",
    "one_non_graph":"only if it distinguishes mechanism"},"train_now":[]},
  "mainline":{"claim":("Matched response surfaces and oracle graphs can distinguish count, length, "
    "support and topology while localizing two-stage attenuation."),
    "must_be_true":["topology or support adds beyond count/length","oracle pairing is valid",
                    "residual differs materially from SceneNAT"],
    "falsifiers":["topology equivalence","no crossed support effect","oracle cannot alter retention"]},
  "retained_claims":["count-length factorial separation","matched support-regime decomposition",
    "within-count topology construct","stage-localized oracle intervention","optional secondary C*"],
  "rejected_claims":["more relations lower iRecall as novelty",
    "relation-aware high-count superiority as novelty","another three-baseline curve as novelty",
    "3-6 decline equals intrinsic capacity","mandatory C*","where attenuation equals why"],
  "adjudication":{"verdict":"PRE_F0_REFORMULATE",
    "reason":"scalar capacity collides; topology/support/stage child remains but needs new qualification",
    "merge_or_stop_if":"child reduces to a count curve, repeated baseline table, or graph ranking",
    "next":"RESTART_PRE_F0_FOR_VERSIONED_CHILD",
    "data_license_proposed":False,"gpu_authority_proposed":False},
  "authority":authority,
  "gates":{"novelty":"REFORMULATE","support_crossover":"NOT_YET_QUALIFIED",
    "stage":"IDENTIFIABLE_NOT_EXECUTED","legacy_debt":"PENDING_EXACT_BASELINE",
    "data_license":"NOT_REQUESTED","gpu":"NOT_REQUESTED","P1":"NOT_AUTHORIZED"},
  "relation_to_port010":{"status":"HOLD_EVIDENCE_REVIEW_BLOCKED",
    "evidence_review":"BLOCK_BAKE_IN","changed":False},
  "scientific_outcomes_generated":0,
 }

def main() -> None:
 p=argparse.ArgumentParser()
 p.add_argument("--scenenat-pdf",type=Path,required=True)
 p.add_argument("--scenenat-source-tar",type=Path,required=True)
 p.add_argument("--scenenat-repo",type=Path,required=True)
 p.add_argument("--instructscene-repo",type=Path,required=True)
 p.add_argument("--output",type=Path,default=ROOT/"generated"/"relational-constraint-capacity-novelty-support-differential-20260831.json")
 a=p.parse_args()
 check(a.scenenat_pdf,H["sn_pdf"]); check(a.scenenat_source_tar,H["sn_src"])
 repo(a.scenenat_repo,SN_SHA,{"README.md":H["sn_readme"],"src/data/utils_text.py":H["sn_text"],"src/tasks/train.py":H["sn_train"]})
 repo(a.instructscene_repo,IS_SHA,{"src/data/utils_text.py":H["is_text"],"src/generate_sg.py":H["is_gen"]})
 for name,digest in {
  "generated/relational-constraint-capacity-construct-v2-20260830.json":H["construct"],
  "generated/relational-constraint-capacity-pre-f0-adjudication-20260830.json":H["old_adj"],
  "generated/paper-first-pre-f0-evidence-acquisition-plan.json":H["port"]}.items(): check(ROOT/name,digest)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(build(),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(a.output); print(sha(a.output))

if __name__=="__main__": main()
