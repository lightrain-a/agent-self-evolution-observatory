#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p:Path):return json.loads(p.read_text())
def atom(p:Path,x):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(f".{p.name}.{os.getpid()}.tmp"); t.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); os.replace(t,p)
v3p=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json"; v3a=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json"; v3=obj(v3p)
pia_paths={
"pia_adjudication":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-adjudication-20260901.json",
"canonical_lineage":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-canonical-v3-lineage-20260901.json",
"duplicate_quarantine":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-permanent-v1-quarantine-20260901.json",
"recovery_set":ROOT/"generated/e2-r17-deepseek-v2-repair2-pia1-pair29-recovery-set-20260901.json"}
pia={k:{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for k,p in pia_paths.items()}
assert obj(pia_paths["pia_adjudication"])["status"]=="PIA1_PASS_V3_RESUME_CANONICAL_V1_PERMANENTLY_QUARANTINED"
rec=obj(pia_paths["recovery_set"]); assert rec["status"]=="PIA1_PASS_PAIR29_MEASUREMENT_ONLY_RECOVERY_ELIGIBLE"
learn=[]
for arm in ("win_c","mrw"):
 b=rec["state_bindings"][arm]; sr=Path(b["state_root"]); uc=sr/"checkpoints/update_completed.json"
 learn.append({"arm":arm,"state_root":str(sr),"skill_post_path":b["skill_path"],"skill_post_sha256":b["skill_sha256"],"update_receipt_path":b["update_receipt_path"],"update_receipt_sha256":b["update_receipt_sha256"],"update_completed_path":str(uc),"update_completed_sha256":sha(uc),"parent_completed_eval_manifest_path":b["completed_eval_manifest_path"],"parent_completed_eval_manifest_sha256":b["completed_eval_manifest_sha256"],"parent_completed_task_ids":b["completed_tasks"],"parent_claim_count":b["parent_claims"],"child_provider_total_limit":191-int(b["parent_claims"]),"updater_calls":10,"attempt0_success":True,"correction_required":False})
allowed=[{"arm":x["arm"],"task_id":x["task_id"],"classification":x["classification"]} for x in rec["missing_measurements_in_frozen_order"]]
parent={"contract_path":str(v3p),"contract_sha256":sha(v3p),"authorization_path":str(v3a),"authorization_sha256":sha(v3a),"run_root":str(Path(v3["run_root"])),"completed_manifest_sha256":obj(pia_paths["canonical_lineage"])["completed_manifest_sha256"],"valid_manifest_sha256":obj(pia_paths["canonical_lineage"])["valid_manifest_sha256"]}
actor=ROOT/"scripts/run_e2_r17_actor_pool_pair29_recovery_compat_v1.py"; runner=ROOT/"scripts/run_e2_r17_deepseek_v2_repair2_pair29_recovery_m1.py"
budget={"required":True,"allowed_total_limits":[74,98],"per_unit_limit":11,"original_per_state_limit":191,"claims_never_released":True}
run_root="/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-pair29-recovery-m1-20260901"
contract={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-pair29-recovery-m1-contract","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1_MEASUREMENT_ONLY","title":"E2-R17 DeepSeek V2 Repair2 Pair29 Measurement-Only Recovery M1","scientific_design_changed":False,"prompt_changed":False,"model_changed":False,"task_order_changed":False,"correction_budget_changed":False,"analysis_changed":False,"run_root":run_root,"env_file":".env","authority":{"updater":False,"analyzer":False,"paper_promotion":False,"public_benchmark":False},"measurement":{"new_updater_calls":0,"replayed_updater_calls":0,"measurement_states":2,"heldout_evaluations":7,"unique_429_logical_unit_recoveries":1,"never_started_measurements":6,"partial_effect_read":False},"pia1":pia,"parent_v3_provenance":parent,"learned_states":learn,"allowed_measurements":allowed,"heldout":{"task_ids":v3["heldout"]["task_ids"],"k":1},"actor":v3["actor"],"actor_runtime":v3["actor_runtime"],"model_identity":v3["model_identity"],"suite":v3["suite"],"mindmemos":v3["mindmemos"],"provider_budget":budget,"bound_code":{"measurement_actor":{"path":str(actor.relative_to(ROOT)),"sha256":sha(actor)},"recovery_runner":{"path":str(runner.relative_to(ROOT)),"sha256":sha(runner)}},"exactly_once":{"authorized_runs":1,"automatic_retry":False,"replacement_sampling":False,"completed_unit_replay":False}}
cp=ROOT/"generated/e2-r17-deepseek-v2-repair2-pair29-recovery-m1-contract-20260901.json"; atom(cp,contract); cs=sha(cp)
auth={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-pair29-recovery-m1-authorization","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1_MEASUREMENT_ONLY","contract_path":str(cp),"contract_sha256":cs,"authority":{"measurement_only":True,"scientific_experiment":True,"updater":False,"analyzer":False,"paper_promotion":False,"public_benchmark":False},"execution_scope":{"measurement_child":"E2-R17-DEEPSEEK-V2-REPAIR2-PAIR29-RECOVERY-M1","allowed_modes":["e1"],"exact_k":1,"allowed_measurements":allowed,"learned_states":learn,"allow_noninitial_skill":True,"required_resolved_model":v3["actor"]["resolved_model"],"identity_artifact_sha256":v3["model_identity"]["sha256"],"max_turns":v3["actor"]["max_turns"],"max_output_tokens":v3["actor"]["max_output_tokens"],"suite_manifest_sha256":v3["suite"]["suite_manifest_sha256"],"split_manifest_sha256":v3["suite"]["split_manifest_sha256"],"provider_budget":budget,"run_root":run_root,"exactly_once":True,"automatic_retry":False,"completed_unit_replay":False,"partial_effect_read":False},"parent_v3_provenance":parent,"pia1":pia,"mindmemos_commit":v3["mindmemos"]["commit"],"provider_retry_limit":0}
ap=ROOT/"generated/e2-r17-deepseek-v2-repair2-pair29-recovery-m1-authorization-20260901.json"; atom(ap,auth)
print(json.dumps({"contract_path":str(cp),"contract_sha256":cs,"authorization_path":str(ap),"authorization_sha256":sha(ap),"allowed_measurements":len(allowed),"unique_429":1,"new_updater_calls":0,"partial_effect_read":False},indent=2,sort_keys=True))
