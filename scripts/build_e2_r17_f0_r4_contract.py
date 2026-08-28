#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CODE = [
 "research_pipeline/e2_r17_search_projection_theory.py",
 "research_pipeline/e2_r17_search_projection_runner.py",
 "research_pipeline/e2_r17_ark_plan_react.py",
 "research_pipeline/e2_r17_actor_pool.py",
 "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
 "research_pipeline/e2_r17_mindmemos_updater.py",
 "scripts/run_e2_r17_actor_pool.py",
 "scripts/run_e2_r17_cloned_state_updates.py",
 "scripts/freeze_e2_r17_e0_pilot_manifest.py",
]

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p: Path) -> dict[str, Any]: return json.loads(p.read_text(encoding="utf-8"))
def ref(p: Path) -> dict[str,str]:
 try: name=str(p.resolve().relative_to(ROOT.resolve()))
 except ValueError: name=str(p.resolve())
 return {"path":name,"sha256":sha(p)}
def atom(p: Path, x: dict[str,Any]) -> None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp")
 t.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); os.replace(t,p)

def main() -> int:
 q=argparse.ArgumentParser()
 for name in ["identity","pilot","suite_qualification","updater_qualification","actor_smoke","debate","source_audit","public_audit"]: q.add_argument("--"+name.replace("_","-"),type=Path,required=True)
 q.add_argument("--suite-root",type=Path,required=True); q.add_argument("--mindmemos-root",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
 a=q.parse_args(); splitp=a.suite_root/"r17_split_manifest.json"; metap=a.suite_root/"r17_controlled_metadata.json"; suitep=a.suite_root/"suite_manifest.json"
 identity,pilot,sq,uq,smoke,debate=map(load,[a.identity,a.pilot,a.suite_qualification,a.updater_qualification,a.actor_smoke,a.debate]); split=load(splitp)
 mm=subprocess.check_output(["git","-C",str(a.mindmemos_root),"rev-parse","HEAD"],text=True).strip(); head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(); branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 deep=identity["requested_and_resolved"]["deepseek-v4-pro"]; kimi=identity["requested_and_resolved"]["kimi-k3"]
 checks={
  "identity":identity.get("status")=="PASS_CURRENT_REVIEW_TRANCHE",
  "pilot":pilot.get("status")=="FROZEN_PRE_OUTCOME",
  "suite":sq.get("status")=="PASS_ZERO_PROVIDER",
  "updater":uq.get("status")=="PASS_ZERO_PROVIDER",
  "smoke":smoke.get("status")=="COMPLETED" and not smoke.get("scientific_outcome"),
  "debate":debate.get("status")=="SURVIVES_AS_NARROW_F0_R4_CANDIDATE_NOT_EXPERIMENT_AUTHORIZED",
  "mindmemos":mm=="90491828726e1540442b17cd445d0308d0b8093c",
  "split":sha(splitp)=="aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
  "suite_hash":sha(suitep)=="2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
 }
 if not all(checks.values()): raise RuntimeError(checks)
 init=a.mindmemos_root/"resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
 x={
  "schema_version":"1.0","artifact_type":"e2-r17-f0-r4-frozen-candidate-contract","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
  "status":"CANDIDATE_REQUIRES_DUAL_PREEXECUTION_REVIEW","branch":branch,"head_before_contract":head,
  "r16":{"preserve":True,"mutated":False,"superseded":False},
  "working_title":"When Better Search Teaches Less: Serving-Induced Observation Kernels in Self-Evolving Agents",
  "scientific_object":"SERVING_INDUCED_OBSERVATION_KERNEL_FOR_PERSISTENT_SKILL_LEARNING",
  "claim":"A best-of-K serving selector can improve current acting while a tied winner-only logging policy removes a generated and verified failed witness from an external persistent updater; changing only that projection on an identical pool can change future frozen skill.",
  "not_claimed":["more compute inherently harms learning","failure utility is novel","success/failure contrast is novel","first divergence is novel","validation-gated editing is novel","CADP is novel"],
  "graph":{"search":"T_K~Q_K(.|x,S)","act":"tau+=a(T_K)","learn":"E=g(T_K)","update":"S'=U(S,E)","endpoint":"J(S') at common frozen K=1"},
  "theory":{
   "Y":"binary deterministic verifier","M":"Y_0=0 and max_i Y_i=1","Gamma":"P(M)",
   "identity":"A_K-A_1=V_pre-V_win=Gamma_K(Q), arbitrary rollout dependence",
   "iid_reference":"Gamma_K(p)=(1-p)-(1-p)^K; p*=1-K^(-1/(K-1))",
   "gated_effect":"g_RW=g_WIN outside M, hence E[D]=Gamma*E[D|M]",
   "families":"mutually exclusive primary_failure_family; overlapping post-hoc tags forbidden",
   "role":"measurement structure; novelty requires prospective prediction and causal intervention"
  },
  "invariants":[
   "same task/input/prompt/initial-skill/verifier/requested+resolved actor model within pool",
   "same exact K=8 pool and served winner across cloned arms",
   "selector=max binary score then lowest rollout index",
   "Rejected-Witness=rollout0 on M and winner outside M",
   "same MindMemOS updater/model/batch/evaluation probes across arms",
   "one add-record per task and same top-level acting-winner score; only evidence packet differs",
   "scientific unit is independently evolved eight-task stream-state, not rollout/probe"
  ],
  "route":{"base_url":"https://ark.cn-beijing.volces.com/api/plan/v3","forbidden":"https://ark.cn-beijing.volces.com/api/v3","config_default":"ark-code-latest","retry":0,"thinking":"disabled","temperature":0},
  "models":{"actor_updater":{"requested":deep["requested"],"resolved":deep["resolved"]},"reviewers":{"deepseek":deep["resolved"],"kimi":kimi["resolved"]},"drift":"stop tranche on any resolved-id change"},
  "substrate":{"root":str(a.mindmemos_root.resolve()),"commit":mm,"updater":"mindmemos.pipelines.skill.evolution.SkillEvolver","initial_skill":ref(init),"batch_tasks":8,"config":{"min_aggregate":8,"max_aggregate":8,"summary_concurrency":4,"rewrite_skill":False,"use_trajectory_score":True,"transcript_max_chars":16000,"slot_char_budget":6000,"max_parse_attempts":1}},
  "data":{
   "suite_root":str(a.suite_root.resolve()),"suite":ref(suitep),"split":ref(splitp),"metadata":ref(metap),
   "development":split["development"],"development_never_promoted":True,"e0_pilot":pilot["pilot_task_ids"],"e0_all_count":len(split["e0_calibration"]),
   "e1_streams":split["e1_update_streams"],"e1_probes":split["e1_common_heldout_probe"],"integrity_reserve":split["e1_update_reserve_integrity_only"],
   "public":{"primary":"SpreadsheetBench Verified-400","archive_sha256":"10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949","dataset_sha256":"bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7","secondary":"SpreadsheetBench 2 only after controlled+Verified GO","audit":ref(a.public_audit)}
  },
  "search":{"topology":"parallel_best_of_k","generate_once_k":8,"nested_prefixes":[1,2,4,8],"actor_max_turns":10,"actor_max_output_tokens":4096,"random_nonwinner_salt":"e2-r17-r4-random-nonwinner-v1"},
  "arms":{
   "winner_only":"winner","precommitted_always":"rollout0","rejected_witness":"rollout0 on M, winner otherwise",
   "duplicated_winner":"winner twice","winner_random_nonwinner":"winner + SHA-selected nonwinner",
   "skillcat_style_contrast":"winner+rollout0 failure on M, duplicate winner otherwise; matched control, not full SkillCAT reproduction"
  },
  "stages":{
   "E0_pilot":{"tasks":12,"run":"K8 then derive prefixes","stop":"zero rescue events or protocol failure; otherwise predeclared extension allowed"},
   "E0_full":{"tasks":54,"E1_support":"at least 6 rescue tasks and >=3 families; otherwise HOLD/STOP before updater"},
   "E1_pool_freeze":{"streams":12,"tasks_per_stream":8,"pools":96,"support":"at least 8 rescue task-packets and >=6 streams exposed; drop no stream; pass all or stop"},
   "E1_update":{"arms":6,"post_versions":"one content-addressed version per stream-arm","arm_order":"SHA256(E2-R17-F0-R4-CLONED-ARM-ORDER-v1|stream|arm)"},
   "E1_eval":{"probes_per_state":18,"K":1,"endpoint":"mean success across common probes"},
   "later_only_on_GO":["prospective prediction","multi-round evolution","Verified-400","topology x projection","SpreadsheetBench 2"]
  },
  "statistics":{
   "unit":"12 independently evolved stream-states","primary":"Delta_s=J_s(rejected_witness)-J_s(winner_only)","summary":"mean Delta_s",
   "ci":"95% percentile bootstrap over streams, 10000 draws","test":"exact one-sided 2^12 sign-flip","no_pseudoreplication":True,
   "controls":["RW-DUP","RW-random-nonwinner","SkillCAT-style-WIN","PRE-WIN","Delta versus rescue count"]
  },
  "gates":{
   "Identification_GO":["E0 and E1 support pass","provenance pass","mean RW-WIN>0","one-sided p<=0.05","95% CI lower>0","duplicated winner does not reproduce gain"],
   "STOP":["projection null/negative","duplicated-winner equivalence","post-outcome selection required","insufficient frozen rescue support","any cloned invariant fails"],
   "downgrade":["random nonwinner matches RW => generic diversity","SkillCAT-style dominates => keep prior method","RW sufficient => delete CADP"],
   "paper":"Identification+Prediction+longitudinal Closure required; E1 alone is insufficient"
  },
  "execution":{"pilot_first":True,"resume_missing_only":True,"raw_assets":["provider JSON","trajectory JSONL/JSON","pool+projection hashes","skill pre/post hashes","verifier","token ledger","CSV summary","integrity receipt","belief update"],"no_gpu_required":True,"server":"69","forbidden":["task replacement","dev promotion","taxonomy/threshold retuning","benchmark shopping","/api/v3","credential/raw response-id logging"]},
  "review_questions":["identifiable under provider stochasticity?","support gates non-selective?","evidence packet only treatment?","controls separate tokens/diversity?","n=12 statistics adequate?","closest-work reduction?"],
  "assets":{"identity":ref(a.identity),"pilot":ref(a.pilot),"suite_qualification":ref(a.suite_qualification),"updater_qualification":ref(a.updater_qualification),"actor_smoke":ref(a.actor_smoke),"debate":ref(a.debate),"source_audit":ref(a.source_audit),"public_audit":ref(a.public_audit)},
  "code":{p:sha(ROOT/p) for p in CODE},"prerequisite_checks":checks,
  "authority":{"preexecution_review":True,"scientific_experiment":False,"gpu":False,"paper_promotion":False,"front_end_claim":False,"submission":False},
  "next":"independent DeepSeek and Kimi reviews bound to exact contract SHA"
 }
 atom(a.output,x); print(json.dumps({"status":x["status"],"output":str(a.output),"sha256":sha(a.output),"checks":checks},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
