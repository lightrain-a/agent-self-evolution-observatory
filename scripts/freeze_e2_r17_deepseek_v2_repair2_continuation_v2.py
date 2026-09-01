#!/usr/bin/env python3
from __future__ import annotations
import copy,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p:Path):return json.loads(p.read_text())
def rows(p:Path):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def atom(p:Path,x):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(f".{p.name}.{os.getpid()}.tmp");t.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");os.replace(t,p)
v3p=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json";v3a=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json";base=obj(v3p)
pia_paths={"pia_adjudication":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-adjudication-20260901.json","canonical_lineage":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-canonical-v3-lineage-20260901.json","duplicate_quarantine":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-permanent-v1-quarantine-20260901.json"}
pia={k:{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for k,p in pia_paths.items()}
assert obj(pia_paths["pia_adjudication"])["status"]=="PIA1_PASS_V3_RESUME_CANONICAL_V1_PERMANENTLY_QUARANTINED"
passp=ROOT/"generated/e2-r17-deepseek-v2-repair2-pair29-recovery-m1-pass-20260901.json";ps=obj(passp);assert ps["status"]=="PAIR29_MEASUREMENT_RECOVERY_PASS" and ps["partial_effect_read"] is False
v3rows=rows(Path(base["valid_replicate_manifest"]["path"]));assert len(v3rows)==28
rvp=Path(ps["recovered_valid_pair_path"]);assert sha(rvp)==ps["recovered_valid_pair_sha256"];recovered=obj(rvp);assert recovered["unit_id"]=="e1-msp-01/rep0" and recovered["source"]=="repair2_v3_pair29_recovered"
valid=v3rows+[recovered];streams=list(map(str,base["streams"]));expected=[f"{s}/rep{r}" for s in streams for r in range(4)];assert [x["unit_id"] for x in valid]==expected[:29]
now=datetime.now(timezone.utc).isoformat(timespec="seconds")
inh={"schema_version":"1.0","artifact_type":"e2-r17-repair2-continuation-v2-canonical-inheritance","created_at_utc":now,"status":"PASS_CONTINUATION_V2_CANONICAL_INHERITANCE_29_PAIRS","source_counts":{"repair1_inherited":14,"repair2_m1_recovered":1,"repair2_v3_fresh":13,"repair2_v3_pair29_recovered":1},"pair_count":29,"learned_states":58,"heldout_units":1044,"canonical_prefix_units":expected[:29],"valid_rows":valid,"pia_adjudication_sha256":pia["pia_adjudication"]["sha256"],"pair29_recovery_pass_sha256":sha(passp),"partial_effect_read":False,"scientific_scores_read":False,"analyzer_run":False}
ip=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v2-inheritance-29-20260901.json";atom(ip,inh)
rem={"schema_version":"1.0","artifact_type":"e2-r17-repair2-continuation-v2-remaining-set","created_at_utc":now,"status":"PASS_CONTINUATION_V2_REMAINING_SET_19_PAIRS","completed_units":expected[:29],"remaining_units":expected[29:],"completed_count":29,"remaining_count":19,"intersection":[],"union_count":48,"first_remaining_unit":expected[29],"new_learned_states":38,"new_heldout_units":684,"task_order_changed":False,"replacement_sampling":False,"completed_unit_replay":False,"partial_effect_read":False}
rp=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v2-remaining-19-20260901.json";atom(rp,rem)
run_root="/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-continuation-v2-20260901";lease="/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-deepseek-v2-repair2-global-v1.json"
runner=ROOT/"scripts/run_e2_r17_deepseek_v2_repair2_continuation_v2.py";actor=ROOT/"scripts/run_e2_r17_actor_pool_repair2_continuation_v2.py";preflight=ROOT/"scripts/preflight_e2_r17_deepseek_v2_repair2_continuation_v2.py"
c=copy.deepcopy(base);c.update({"artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v2-contract","created_at_utc":now,"date":"2026-09-01","status":"FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2","purpose":"Finish exactly the 19-pair unexecuted suffix of the canonical original Repair2 design after PIA-1 and pair29 measurement recovery.","run_root":run_root})
c["authority"]={"scientific_experiment":False,"execute_deepseek_v2":False,"repair2_continuation_v2":False,"analyzer":False,"gpt_scientific_execution":False,"kimi_scientific_execution":False,"qwen_scientific_execution":False,"public_benchmark":False,"paper_promotion":False,"submission":False}
c["valid_replicate_manifest"]={"path":run_root+"/checkpoints/valid_replicates.jsonl","required_rows":48,"required_per_stream":4,"allowed_sources":["repair1_inherited","repair2_m1_recovered","repair2_v3_fresh","repair2_v3_pair29_recovered","repair2_continuation_v2_fresh"],"directory_discovery_forbidden":True}
c["pia1"]=pia;c["pair29_recovery"]={"pass_path":str(passp.relative_to(ROOT)),"pass_sha256":sha(passp),"run_root":str(Path(ps["run_summary_path"]).parents[1]),"recovered_valid_pair_path":str(rvp),"recovered_valid_pair_sha256":sha(rvp)}
c["lineage_inheritance_manifest"]={"path":str(ip.relative_to(ROOT)),"sha256":sha(ip)};c["remaining_set_manifest"]={"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)};c["remaining_units"]=expected[29:]
c["global_lineage_lease"]={"path":lease,"acquire":"O_EXCL_BEFORE_RUN_ROOT_AND_PROVIDER_IO","persistent_terminal_seal":True}
c["execution_plan"]={"inherited_pairs":29,"remaining_pairs":19,"new_learned_states":38,"new_heldout_units":684,"final_pairs":48,"final_learned_states":96,"final_heldout_units":1728,"completed_unit_replay":False,"partial_effect_read":False}
c["budget"]["states"]=38;c["budget"]["hard_max_provider_calls_structural"]=38*191
c["bound_code"]={"actor_runner_v2":{"path":str(actor.relative_to(ROOT)),"sha256":sha(actor)},"runner_v2":{"path":str(runner.relative_to(ROOT)),"sha256":sha(runner)},"preflight_v2":{"path":str(preflight.relative_to(ROOT)),"sha256":sha(preflight)},"provider_budget":base["bound_code"]["provider_budget"],"renderer":base["bound_code"]["renderer"],"updater_adapter":base["bound_code"]["updater_adapter"],"updater_wrapper":base["bound_code"]["updater_wrapper"]}
c["exactly_once"]={"authorized_runs":1,"automatic_retry":False,"replacement_sampling":False,"completed_unit_replay":False,"global_lineage_lease_required":True}
cp=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v2-contract-20260901.json";atom(cp,c);cs=sha(cp)
scope={"continuation_version":"repair2_continuation_v2","allowed_modes":["e1"],"allowed_task_ids":c["heldout"]["task_ids"],"exact_k":1,"allow_noninitial_skill":True,"replicates_per_stream":4,"remaining_units":expected[29:],"provider_budget":{"required":True,"total_limit":191,"per_unit_limit":11},"suite_manifest_sha256":c["suite"]["suite_manifest_sha256"],"split_manifest_sha256":c["suite"]["split_manifest_sha256"],"required_resolved_model":c["actor"]["resolved_model"],"identity_artifact_sha256":c["model_identity"]["sha256"],"max_turns":10,"max_output_tokens":8192,"global_lineage_lease_path":lease,"exactly_once":True,"completed_unit_replay":False,"partial_effect_read":False}
auth={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v2-authorization","created_at_utc":now,"status":"AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2","contract_path":str(cp),"contract_sha256":cs,"authority":{"scientific_experiment":True,"deepseek_v2":True,"repair2_continuation_v2":True,"analyzer":False,"gpt_scientific_execution":False,"kimi_scientific_execution":False,"qwen_scientific_execution":False,"public_benchmark":False,"mrw_causal_comparison":True,"paper_promotion":False},"execution_scope":scope,"pia1":pia,"pair29_recovery":c["pair29_recovery"],"mindmemos_commit":c["mindmemos"]["commit"],"provider_retry_limit":0}
ap=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v2-authorization-20260901.json";atom(ap,auth)
print(json.dumps({"inheritance_manifest_sha256":sha(ip),"remaining_set_manifest_sha256":sha(rp),"contract_sha256":cs,"authorization_sha256":sha(ap),"inherited_pairs":29,"remaining_pairs":19,"global_lineage_lease":lease,"partial_effect_read":False},indent=2,sort_keys=True))
