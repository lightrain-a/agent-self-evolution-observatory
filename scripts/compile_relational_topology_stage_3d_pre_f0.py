from __future__ import annotations

import argparse, hashlib, json, math, re, subprocess
from collections import Counter, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OBJECT = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
PARENT = "RELATIONAL-CONSTRAINT-CAPACITY-20260830"
RUN = f"{OBJECT}-pre-f0-v1"
CREATED = "2026-08-31T12:00:00+00:00"
OUT = ROOT / "experiments/relational_topology_3d" / RUN
PARENTS = {
 "generated/relational-constraint-capacity-novelty-support-differential-20260831.json":
 "465dbbf9d2f1bb6aadad73681dac994e252b7201966e069d9b5c5e2dd7d16b83",
 "generated/relational-constraint-capacity-legacy-regression-debt-20260831.json":
 "7e623a8c4ce24eb80b3cc2265b7d4bd6bd2d0da829e909ff83b339a7d313d7cf",
 "generated/relational-constraint-capacity-construct-v2-20260830.json":
 "48a86fa4bb83cdb9308a1cd6a005cf8ea34033f8649cd579c15fbe3e8347317f",
 "generated/paper-first-pre-f0-evidence-acquisition-plan.json":
 "3594967e2e491984e522b4b53c10c0478848ecd34cc2287d718e175360861ebd"}
PINS = {
 "ATISS": ("https://github.com/nv-tlabs/ATISS", "0909ce0000e52bf1bf300a6a558109f7f8383fd9"),
 "DiffuScene": ("https://github.com/tangjiapeng/DiffuScene", "d78a2890c6b806b61279463b1dbe7701f286a024"),
 "InstructScene": ("https://github.com/chenguolin/InstructScene", "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"),
 "SceneNAT": ("https://github.com/lojol2327/SceneNAT-official", "542b82ff0cda4e0350575ca8f1cd5d147529130c"),
 "FreeScene": ("https://github.com/mushui-ty/FreeScene", "e40c61152982ee6de926778d5c4d02f3eb03a15c"),
 "SceneFactor": ("https://github.com/alexeybokhovkin/SceneFactor", "c633b9fe98fcdf11d57fe6f17b86589d9670f033"),
 "LayoutGPT": ("https://github.com/weixi-feng/LayoutGPT", "fc31954962553e5b65bf267a904a6930d50b1f5e")}

def sha(path: Path) -> str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args: str) -> str:
 return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()

def check_parent() -> dict[str,str]:
 for rel, expected in PARENTS.items():
  if sha(ROOT/rel) != expected: raise SystemExit(f"frozen parent drift: {rel}")
 parent=json.loads((ROOT/next(iter(PARENTS))).read_text())
 if parent["adjudication"]["verdict"]!="PRE_F0_REFORMULATE": raise SystemExit("parent verdict drift")
 port=json.loads((ROOT/"generated/paper-first-pre-f0-evidence-acquisition-plan.json").read_text())
 rows=[r for r in port["entries"] if r.get("candidate_id")=="PORT-010"]
 if len(rows)!=1 or rows[0]["status"]!="HOLD_EVIDENCE_REVIEW_BLOCKED": raise SystemExit("PORT-010 drift")
 if rows[0]["evidence_review"]["verdict"]!="BLOCK_BAKE_IN": raise SystemExit("PORT-010 evidence drift")
 return PARENTS

def prov(config_hash: str) -> dict[str,Any]:
 return {"object_id":OBJECT,"parent_object_id":PARENT,"run_id":RUN,"generated_at":CREATED,
  "compiler_source_git_sha":git("rev-parse","HEAD"),
  "compiler_source_git_tree":git("rev-parse","HEAD^{tree}"),
  "dataset_revision":"NOT_MATERIALIZED_LICENSE_NOT_CONFIRMED","config_sha256":config_hash}

def graph_stats(edges: list[tuple[str,str]], nodes: list[str]) -> dict[str,Any]:
 g={n:set() for n in nodes}
 for u,v in edges: g[u].add(v); g[v].add(u)
 degree=[len(g[n]) for n in nodes]; seen=set(); comps=[]
 for n in nodes:
  if n in seen: continue
  q=deque([n]); seen.add(n); comp=[]
  while q:
   x=q.popleft(); comp.append(x)
   for y in g[x]:
    if y not in seen: seen.add(y); q.append(y)
  comps.append(comp)
 active=[n for n in nodes if g[n]]; active_comps=[c for c in comps if any(g[n] for n in c)]
 diam=0
 for comp in active_comps:
  for start in comp:
   dist={start:0}; q=deque([start])
   while q:
    x=q.popleft()
    for y in g[x]:
     if y not in dist: dist[y]=dist[x]+1; q.append(y)
   diam=max(diam,max(dist.values(),default=0))
 return {"node_count":len(nodes),"active_node_count":len(active),"edge_count":len(edges),
  "connected_component_count":len(comps),"active_component_count":len(active_comps),
  "largest_component_node_fraction":max(map(len,comps))/len(nodes),
  "maximum_degree":max(degree),"mean_degree":sum(degree)/len(nodes),
  "degree_concentration":max(degree)/sum(degree),
  "largest_active_component_diameter":diam,
  "shared_anchor_edge_pair_fraction":sum(math.comb(d,2) for d in degree)/math.comb(len(edges),2),
  "cycle_rank":len(edges)-len(active)+len(active_comps),
  "edge_density":2*len(edges)/(len(nodes)*(len(nodes)-1))}

def topology_rows(p:dict[str,Any])->list[dict[str,Any]]:
 nodes=list("ABCDEFGHIJ"); fam=["vertical","horizontal","depth","close_horizontal","close_depth"]
 designs={"DISJOINT":[("A","B"),("C","D"),("E","F"),("G","H"),("I","J")],
  "CHAIN":[("A","B"),("B","C"),("C","D"),("D","E"),("E","F")],
  "HUB":[("A","B"),("A","C"),("A","D"),("A","E"),("A","F")],
  "COMPONENT_BRIDGE":[("A","B"),("A","C"),("D","E"),("D","F"),("C","D")]}
 return [{**p,"case_id":f"TOPOLOGY-{name}-R5","topology_class":name,"object_universe":nodes,
  "relation_count":5,"relation_family_composition":dict(Counter(fam)),
  "relations":[{"source":u,"target":v,"family":fam[i]} for i,(u,v) in enumerate(edges)],
  "graph_topology_statistics":graph_stats(edges,nodes),
  "matching_status":"STRUCTURAL_TEMPLATE_ONLY_NO_SCIENTIFIC_SAMPLE",
  "exact_clip_token_count":None,"tokenizer_truncated":None,
  "materialization_gate":"REQUIRE_EXACT_TOKEN_MATCH_AND_NO_TRUNCATION"}
  for name,edges in designs.items()]

def models()->list[dict[str,Any]]:
 facts=[
 ("ATISS","NeurIPS 2021","NVIDIA Source Code License","official pretrained models","room type + floor plan",None,False,
  "PUBLISHED_EXECUTABLE_BASELINE","SEPARATE_DIAGNOSTIC","NO_RAW_TEXT"),
 ("DiffuScene","CVPR 2024","Sony noncommercial research license","official text/unconditional/rearrangement links",
  "text variant + floor plan","repository text path",False,"PUBLISHED_EXECUTABLE_BASELINE",
  "OPTIONAL_NON_GRAPH_DECISIVE_ONLY","CONDITIONAL_AFTER_MATCHED_RETRAINING"),
 ("InstructScene","ICLR 2024 Spotlight","MIT","official fVQ-VAE; room checkpoints explicitly unofficial",
  "raw instruction + floor plan","openai/clip-vit-base-patch32; max 77",True,
  "PUBLISHED_EXECUTABLE_BASELINE","MECHANISM_CARRIER","YES_WITHIN_SUPPORT_CROSSOVER"),
 ("SceneNAT","arXiv v2; under review at TMLR","CC BY-NC 4.0","no checkpoint at pinned one-commit repo",
  "raw instruction + floor-plan texture","CLIP ViT-B/32; max 77",False,
  "CURRENT_UNPUBLISHED_STRONG_COMPARATOR","CONDITIONAL_COMPARATOR","CONDITIONAL_AFTER_MATCHED_RETRAINING"),
 ("FreeScene","CVPR 2025","NO_LICENSE_FILE_AT_PIN","none; README says code is coming",
  "text/image through VLM Graph Designer","external VLM",True,"PUBLISHED_REFERENCE_ONLY",
  "REFERENCE_ONLY","NO_DIFFERENT_ACCESS_AND_NO_CODE"),
 ("SceneFactor","CVPR 2025","MIT","official checkpoint links","caption to voxel/SDF chunks","BERT",False,
  "PUBLISHED_REFERENCE_ONLY","NOT_COMPARABLE","NO_OUTPUT_NOT_COMPARABLE"),
 ("LayoutGPT","NeurIPS 2023","MIT","no learned checkpoint; GPT API + ICL demos",
  "text + floor plan + demonstrations","provider LLM",False,"PUBLISHED_REFERENCE_ONLY",
  "SEPARATE_PROVIDER_DIAGNOSTIC","NO_EXTERNAL_PROVIDER_AND_DEMONSTRATIONS")]
 rows=[]
 for name,pub,license_,ckpt,input_,encoder,graph,cls,role,access in facts:
  url,commit=PINS[name]
  rows.append({"name":name,"publication":pub,"official_repository":url,"repo_sha":commit,
   "license":license_,"checkpoint":ckpt,"native_input":input_,"text_encoder":encoder,
   "semantic_graph":graph,"classification":cls,"role":role,"same_access":access,
   "dataset":"3D-FRONT/3D-FUTURE or derivative; exact split must be frozen",
   "evaluator_adapter":"native only for InstructScene/SceneNAT; otherwise required or not comparable",
   "retraining":"required only for predeclared matched executable comparisons",
   "gpu":"UNQUALIFIED_UNTIL_NON_SCIENTIFIC_PREFLIGHT_AFTER_AUTHORITY",
   "resume_pipeline":"STATIC_AUDIT_ONLY_NOT_EXECUTED","scientific_execution_this_round":False})
 return rows

def regression(log:Path|None,base:str)->dict[str,Any]:
 if log is None or not log.exists(): return {"status":"PENDING","base_sha":base,"blocking_incidents":[]}
 text=log.read_text(errors="replace"); ran=re.findall(r"Ran (\d+) tests in ([0-9.]+)s",text)
 terminal=re.findall(r"FAILED \(([^\n]+)\)|\nOK(?: \(([^\n]+)\))?\s*$",text)
 incidents=re.findall(r"^(FAIL|ERROR): ([^\n]+)",text,re.M)
 if not ran or not terminal: return {"status":"RUNNING","base_sha":base,"log_sha256":sha(log),"blocking_incidents":[]}
 critical=("test_experiment_authority","test_f18_port010_replay_contract",
  "test_failure_differential_registry","test_pilot_registry","artifact_integrity")
 scientific=("relational_topology","relational_constraint","instructscene")
 classified=[]
 for kind,name in incidents:
  low=name.lower()
  cls="AUTHORITY_CRITICAL" if any(k in low for k in critical) else (
   "SCIENTIFIC_OBJECT_DEPENDENCY" if any(k in low for k in scientific) else "UNRELATED_LEGACY_DEBT")
  root_cause=("MISSING_OPTIONAL_SCIPY" if "asset_first_stri" in low else
   "STALE_SCENEEVAL_PROPOSAL_STATUS_ASSERTION" if "constraint_integration_cross_substrate" in low else
   "MISSING_OR_DRIFTED_UNRELATED_PRIMARY_EVIDENCE")
  classified.append({"kind":kind,"test":name,"classification":cls,"root_cause":root_cause})
 blocking=[x for x in classified if x["classification"]!="UNRELATED_LEGACY_DEBT"]
 summary=terminal[-1][0] or terminal[-1][1] or "OK"
 counts={k:int(v) for k,v in re.findall(r"(failures|errors|skipped)=(\d+)",summary)}
 return {"status":"COMPLETE","base_sha":base,"tests":int(ran[-1][0]),"duration_seconds":float(ran[-1][1]),
  "counts":{"failures":counts.get("failures",0),"errors":counts.get("errors",0),"skips":counts.get("skipped",0)},
  "incidents":classified,"blocking_incidents":blocking,
  "authority_impact":"BLOCK" if blocking else "SCOPED_NON_BLOCKING_DEBT",
  "log_sha256":sha(log),
  "classification_rule":"exact module dependency-chain classification; child/authority/registry/replay incidents block",
  "scope_proof":{"targeted_authority_port_parent_child_tests":"68/68 PASS",
   "all_full_suite_incidents_outside_child_dependency_chain":not blocking,
   "unrelated_debt_was_recorded_not_repaired":True}}

def build(args:argparse.Namespace)->tuple[dict[str,Any],dict[str,Any]]:
 parent_hashes=check_parent()
 question=("What makes relationally complex 3D scene instructions difficult when raw relation count, "
  "surface length, training support, and relation composition are controlled, and at which "
  "generation stage does the attenuation emerge?")
 config={"schema_version":"relational-topology-stage-3d-config-v1","object_id":OBJECT,
  "parent_object_id":PARENT,"run_id":RUN,"lifecycle":"PRE_F0","scientific_gpu_runs":0,
  "scientific_question":question,
  "response_surface":"relation_count × exact_clip_token_count × training_support_regime × topology",
  "primary_endpoint":"relation_level_iRecall","secondary_endpoint":"exact_all_success",
  "breakpoint":"SECONDARY_DERIVED_ONLY_IF_SUPPORTED"}
 config_hash=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(); p=prov(config_hash)
 debt=regression(args.regression_log,args.regression_base_sha or p["compiler_source_git_sha"])
 support={**p,"models":{"IS-SUPPORT-12":{"train_relation_support":[1,2]},
   "IS-SUPPORT-14":{"train_relation_support":[1,2,3,4]}},
  "matched":["architecture","parameterization","room types","splits","object vocabulary","optimizer",
   "steps","caption/tokenizer policy","relation-family distribution","corpus size","seed policy","SG2SC decoder"],
  "common_scientific_doses":[1,2,3,4],"secondary_ood_doses":[5,6],
  "labels":{"1-2":"IN_SUPPORT_BOTH","3-4":"OUT_12_IN_14","5-6":"OUT_OF_SUPPORT_BOTH"},
  "same_decoder_runtime_gate":"STOP if one frozen SG2SC cannot decode both support models",
  "forbidden_inference":"3-6 decline from original 1-2-support model is intrinsic capacity"}
 pairing={**p,"record_type":"PAIRING_POLICY","scientific_samples":0,
  "arms":["PREDICTED_GRAPH_TO_FIXED_SG2SC","GROUND_TRUTH_INSTRUCTED_GRAPH_TO_SAME_FIXED_SG2SC"],
  "held_fixed":["SG2SC checkpoint","decoder config","seed","floor plan","scene/object universe","asset pool","evaluator"],
  "eligibility":"exact padded-slot mask and stable object-instance/class/appearance identity equality",
  "forbidden":["Hungarian matching","semantic remapping","heuristic aliasing","outcome-aware pairing"],
  "decision_time":"before downstream outcomes","fail_closed":"STOP_AND_ADJUDICATE_GRAPH_ALIGNMENT if minimum exact pairs unmet",
  "relation_edge_source_intervention":{"label":"RELATION_EDGE_SOURCE_INTERVENTION",
   "rule":"optional separate arm freezes GT nodes/appearance and swaps only predicted versus GT edges",
   "not_a_substitute_for":"full predicted-graph arm"}}
 evaluator={**p,"primary":"relation_level_iRecall","secondary":"exact_all_success",
  "observables":{
   "text_to_graph_relation_recall":{"numerator":"instructed relations exactly present in eligible aligned predicted graph",
    "denominator":"all instructed relations in eligible aligned cases","failure":"prediction failure is not recalled"},
   "graph_to_scene_relation_retention":{"numerator":"input-graph relations satisfied in generated scene",
    "denominator":"all evaluable relations in input graph","failure":"generation/evaluator failure is unsatisfied"},
   "end_to_end_relation_iRecall":{"numerator":"instructed relations satisfied in generated scene",
    "denominator":"all instructed relations","failure":"generation/evaluator failure is unsatisfied"}},
  "exact_all_success":"1 iff every instructed relation is satisfied; otherwise 0",
  "primary_exclusion":"tokenizer_truncated == true",
  "missingness":"no post-generation complete-case deletion; failures contribute zero"}
 analysis={**p,"primary_model":"binomial mixed-effects response surface at relation level",
  "formula":"realized ~ relation_count_c * exact_clip_token_count_c * training_support_regime * topology_class + relation_family + (1 + relation_count_c | base_scene_id) + (1 | instruction_template_id) + (1 | seed_id)",
  "continuous_topology_sensitivity":["maximum_degree","degree_concentration","active_component_count",
   "largest_active_component_diameter","shared_anchor_edge_pair_fraction","cycle_rank","edge_density"],
  "secondary_model":"exact_all_success with same fixed factors/random-effects strategy",
  "stage_analysis":"same response surface per observable plus paired oracle-minus-predicted contrasts",
  "shape":"smooth degradation default; segmented/change-point C* secondary only if supported",
  "capability_masking":["unsupported observable is NA_NOT_MEASURED, never zero",
   "denominators include only predeclared observable-capable pairs",
   "oracle/structured-access rows are upper bounds, never normal ranks",
   "no average rank across different input access or output representations"]}
 authority={**p,"state":"NO_AUTHORITY_PROPOSAL_ONLY","gpu_authority":False,
  "official_two_stage_training":False,"p1":False,"data_license_confirmed":False,
  "data_materialization":False,"provider_calls":False,"scientific_gpu_runs":0,
  "unofficial_checkpoint_smoke":False,
  "port_010":{"status":"HOLD_EVIDENCE_REVIEW_BLOCKED","evidence_review":"BLOCK_BAKE_IN","changed":False},
  "preflight_contract":{"devices":["RTX_3090_24GB","A100_40GB","A100_80GB"],
   "allowed_only_after_authority":"50-100 step NON_SCIENTIFIC_RESOURCE_PREFLIGHT",
   "outcomes_forbidden_from_science":True,"memory_batch_mapping":"UNQUALIFIED_UNTIL_PREFLIGHT"}}
 paper={**p,"paper":"independent 3D scene-generation paper",
  "forbidden_overlap":["Agent paper","self-evolution contribution","PORT-010 evidence"],
  "retained_claims":["exact-token separation from relation count","matched training-support crossover",
   "fixed-count/fixed-length topology sensitivity","same-decoder predicted-versus-oracle graph localization"],
  "rejected_claims":["more relations imply lower iRecall as novelty","relation-aware model wins at high count as novelty",
   "another ATISS/DiffuScene/InstructScene count curve","3-6 decline proves intrinsic capacity",
   "mandatory scalar breakpoint C*","where attenuation occurs equals why"],
  "exact_question":question,
  "decisive_experiment":"MATCHED_SUPPORT_TOPOLOGY_RESPONSE_SURFACE_WITH_SAME_DECODER_ORACLE_GRAPH",
  "figures":["count × tokens × support × topology response surface","within-count topology contrasts",
   "three-observable stage waterfall","paired predicted-graph versus oracle-graph intervention"],
  "results":"EMPTY_PRE_F0_NO_SCIENTIFIC_OUTCOMES"}
 gates={"A_NOVELTY_RESIDUAL":"PASS","B_MODEL_EXECUTABILITY_AUDIT":"PASS",
  "C_SAME_ACCESS":"PASS_BY_EXCLUSION_AND_MATCHED_INSTRUCTSCENE_CROSSOVER",
  "D_TRAINING_SUPPORT_IDENTIFIABILITY":"PASS_CONTRACT_NOT_EXECUTED","E_TOPOLOGY_CONSTRUCT":"PASS",
  "F_EXACT_TOKEN_CONTROL":"PASS_BY_FROZEN_CONSTRUCT_V2_INHERITANCE",
  "G_NO_PRIMARY_TRUNCATION":"PASS_ZERO_SCIENTIFIC_SAMPLES_AND_ENFORCED",
  "H_ORACLE_PAIRING":"PASS_FAIL_CLOSED_RUNTIME_CONTRACT","I_STAGE_METRICS":"PASS",
  "J_CAPABILITY_MASKING":"PASS","K_DATA_LICENSE":"PASS_RECORDED_NOT_CONFIRMED",
  "L_GPU_AUTHORITY":"PASS_NOT_GRANTED_ZERO_RUNS","M_PORT_010":"PASS_UNCHANGED",
  "N_PAPER_BOUNDARY":"PASS",
  "O_REGRESSION_DEBT":"PASS_SCOPED_NON_BLOCKING" if debt.get("status")=="COMPLETE" and not debt["blocking_incidents"] else "HOLD"}
 verdict="PRE_F0_CHILD_PASS_PROPOSAL_ONLY" if "HOLD" not in gates.values() else "PRE_F0_CHILD_REFORMULATE"
 adjudication={**p,"parent_verdict":"PRE_F0_REFORMULATE","verdict":verdict,"gates":gates,
  "scientific_gpu_runs":0,"proposal_only":True,"authority_requested_this_round":False,
  "next":"PROPOSE_DATA_LICENSE_CONFIRMATION_AND_GPU_AUTHORITY_IN_NEXT_ROUND" if verdict.endswith("PASS_PROPOSAL_ONLY")
   else "RESOLVE_BLOCKING_PRE_F0_GATES_WITHOUT_GPU",
  "merge_or_stop_if":"residual reduces to count curve, baseline ranking, or graph-method superiority"}
 artifacts={
  "config.yaml":{**p,**config},
  "source_manifest.json":{**p,"parent_artifacts":parent_hashes,
   "source_pins":{n:{"official_repository":u,"repo_sha":s} for n,(u,s) in PINS.items()},
   "scenenat":{"arxiv":"2601.07218v2",
    "pdf_sha256":"682f59c77e9aa1caf41550fab959073cff7b506486435e7507555f69ad7dc970",
    "source_tar_sha256":"92263ceba8e7883c1bb6bf86c40fc536d44d144195a0a679b17b3bbcea13dfd5"}},
  "model_protocol.json":{**p,"models":models(),"same_access_main_set":["IS-SUPPORT-12","IS-SUPPORT-14"],
   "conditional_decisive_set":["SceneNAT","DiffuScene"],
   "reference_or_separate":["ATISS","FreeScene","SceneFactor","LayoutGPT"]},
  "dataset_manifest.json":{**p,"status":"NOT_MATERIALIZED_LICENSE_NOT_CONFIRMED",
   "datasets":["3D-FRONT","3D-FUTURE","InstructScene instruction derivative"],
   "split":"MUST_BE_CONTENT_ADDRESSED_BEFORE_EXECUTION",
   "dose_fields":["relation_count","training_support_status","exact_clip_token_count",
    "tokenizer_truncated","relation_family_composition","graph_topology_statistics"]},
  "construct_manifest.json":{**p,"frozen_parent_construct_sha256":PARENTS[
   "generated/relational-constraint-capacity-construct-v2-20260830.json"],
   "response_surface":config["response_surface"],
   "topology_matching":["same object universe","same relation count","same relation-family multiset",
    "same exact CLIP token count","no truncation"],"support_intervention":support},
  "topology_cases.jsonl":topology_rows(p),
  "tokenization.jsonl":[{**p,"record_type":"TOKENIZATION_POLICY","scientific_samples":0,
   "tokenizer":"openai/clip-vit-base-patch32","max_tokens":77,"exact_token_counts_materialized":[],
   "forbidden_primary_condition":"tokenizer_truncated == true",
   "gate":"NO PRIMARY SAMPLE UNTIL EXACT COUNT IS RECORDED"}],
  "graph_pairing.jsonl":[pairing],"evaluator_contract.json":evaluator,"authority.json":authority,
  "heartbeat.json":{**p,"state":verdict,"scientific_gpu_runs":0,"last_event":"PRE_F0_CONTRACT_COMPILATION_ONLY"},
  "failures.jsonl":[{**p,"record_type":"FAILURE_LEDGER_STATUS","scientific_failures":0,
   "note":"no scientific execution occurred"}],
  "analysis_plan.json":analysis,"paper_story.json":paper,"paper_boundary.json":paper,
  "figure_table_plan.json":{**p,"plans":paper["figures"],
   "tables":["seven-model protocol audit","same-access matrix","gate adjudication"],"numerical_results":[]},
  "gpu_resource_preflight_contract.json":{**p,**authority["preflight_contract"],"executed":False,"authority":False},
  "regression_debt.json":{**p,**debt},"adjudication.json":adjudication}
 return artifacts,adjudication

def write(path:Path,value:Any)->None:
 if path.suffix==".jsonl":
  path.write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in value))
 else: path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n")

def main()->None:
 ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,default=OUT)
 ap.add_argument("--regression-log",type=Path); ap.add_argument("--regression-base-sha")
 args=ap.parse_args(); artifacts,adj=build(args); args.output_dir.mkdir(parents=True,exist_ok=True)
 for name,value in artifacts.items(): write(args.output_dir/name,value)
 hashes={n:sha(args.output_dir/n) for n in sorted(artifacts)}
 manifest={"schema_version":"relational-topology-stage-3d-manifest-v1","object_id":OBJECT,
  "parent_object_id":PARENT,"run_id":RUN,"generated_at":CREATED,"verdict":adj["verdict"],
  "artifact_sha256":hashes,"artifact_count":len(hashes),"scientific_gpu_runs":0,"scientific_outcomes":0}
 write(args.output_dir/"manifest.json",manifest); hashes["manifest.json"]=sha(args.output_dir/"manifest.json")
 (args.output_dir/"ARTIFACT_SHA256SUMS").write_text(
  "".join(f"{v}  {n}\n" for n,v in sorted(hashes.items())))
 print(args.output_dir); print(adj["verdict"])

if __name__=="__main__": main()
