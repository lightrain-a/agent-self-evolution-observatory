#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
V3C=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json"
V3A=ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json"
AUDIT=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-interruption-audit-20260831.json"
INHERIT=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-inheritance-manifest-20260831.json"
REMAIN=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-remaining-set-20260831.json"
OUTC=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-contract-20260831.json"
OUTA=ROOT/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-authorization-20260831.json"
RUNROOT=Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-continuation-v1-20260831")
V3CSHA="312e970520794c564b23a9717f4c40d4baeb0674619da334c8fcc20ee95fc045"
V3ASHA="7aa826db915b40840fb54ca2c269a23c4f74807bae74fd99285eac6875ee5b74"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def write(p:Path,x:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(p.name+".tmp")
 t.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n"); t.replace(p)

def main()->None:
 assert sha(V3C)==V3CSHA and sha(V3A)==V3ASHA
 c,oldauth,im,rs=load(V3C),load(V3A),load(INHERIT),load(REMAIN)
 assert load(AUDIT)["status"]=="PASS_CONTINUATION_BOUNDARY_PROVEN"
 assert im["status"]=="PASS_IMMUTABLE_INHERITANCE_17_PAIRS_PLUS_CLEAN_PARTIAL_PAIR"
 assert rs["status"]=="PASS_REMAINING_SET_EXACT_PARTITION"
 c["status"]="FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V1"
 c["protocol_version"]="repair2-continuation-v1-after-v3-host-interruption"
 c["purpose"]="Finish exactly the unexecuted remainder of the original frozen Repair2 V3 design after a proven clean host-shutdown boundary; no new scientific branch."
 c["run_root"]=str(RUNROOT)
 c["valid_replicate_manifest"]["path"]=str(RUNROOT/"checkpoints/valid_replicates.jsonl")
 c["continuation_evidence"]={
  "interruption_audit":{"path":str(AUDIT.relative_to(ROOT)),"sha256":sha(AUDIT)},
  "inheritance_manifest":{"path":str(INHERIT.relative_to(ROOT)),"sha256":sha(INHERIT)},
  "remaining_set":{"path":str(REMAIN.relative_to(ROOT)),"sha256":sha(REMAIN)}}
 c["v3_parent"]={"contract":str(V3C.relative_to(ROOT)),"contract_sha256":V3CSHA,
  "authorization":str(V3A.relative_to(ROOT)),"authorization_sha256":V3ASHA,
  "run_root":im["v3_run_root"],"provider_claims":609,
  "preflight":{"path":"generated/e2-r17-deepseek-v2-repair2-v3-frozen-preflight-adjudication-20260831.json",
   "sha256":sha(ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-frozen-preflight-adjudication-20260831.json")},
  "start_receipt":{"path":"generated/e2-r17-deepseek-v2-repair2-v3-run-start-adjudication-20260831.json",
   "sha256":sha(ROOT/"generated/e2-r17-deepseek-v2-repair2-v3-run-start-adjudication-20260831.json")}}
 for k in ("scientific_design_changed","prompt_changed","model_changed","task_order_changed",
  "correction_budget_changed","analysis_changed","inherited_provider_replay","partial_effect_read"): c[k]=False
 c["continuation_execution"]={"completed_pairs_inherited":17,"immutable_learned_states":36,
  "immutable_heldout_units":636,"remaining_pairs":31,"remaining_new_learned_states":60,
  "remaining_heldout_units":1092,"first_unit":"e1-ioc-00/rep1","exactly_once":True,
  "automatic_retry":False,"replacement_sampling":False,"completed_unit_replay":False}
 code={"continuation_runner":"scripts/run_e2_r17_deepseek_v2_repair2_continuation_v1.py",
  "continuation_actor":"scripts/run_e2_r17_actor_pool_repair2_continuation_v1.py",
  "continuation_preflight":"scripts/preflight_e2_r17_deepseek_v2_repair2_continuation_v1.py",
  "interruption_auditor":"scripts/audit_e2_r17_deepseek_v2_repair2_continuation_v1_interruption.py",
  "v3_runner_library":"scripts/run_e2_r17_deepseek_v2_repair2_continuation_v3.py",
  "v3_manifest_validator":"research_pipeline/e2_r17_repair2_v3_manifest.py"}
 for label,path in code.items(): c["bound_code"][label]={"path":path,"sha256":sha(ROOT/path)}
 write(OUTC,c); csha=sha(OUTC)
 heldout=c["heldout"]["task_ids"]; boundary=im["partial_boundary"]; blist=[]; byarm={}
 for arm in ("win_c","mrw"):
  x=boundary["arms"][arm]; done={str(r["task_id"]) for r in x["heldout_tasks"]}
  tasks=[t for t in heldout if t not in done]; assert len(tasks)==6
  row={"arm":arm,"skill_post_path":x["skill_path"],"skill_post_sha256":x["skill_sha256"],
   "update_receipt_path":x["update_receipt_path"],"update_receipt_sha256":x["update_receipt_sha256"],
   "update_checkpoint_path":x["update_checkpoint_path"],"update_checkpoint_sha256":x["update_checkpoint_sha256"],
   "parent_claim_count":int(x["parent_claim_count"]),"child_total_limit":191-int(x["parent_claim_count"]),
   "remaining_task_ids":tasks,"updater_replay":False}
  blist.append(row); byarm[arm]=row
 scope=dict(oldauth["execution_scope"])
 scope.update({"continuation_version":"repair2_continuation_v1","run_root":str(RUNROOT),
  "inherited_pairs":17,"remaining_pairs":31,"remaining_new_learned_states":60,"remaining_heldout_units":1092,
  "fresh_pairs":30,"completed_unit_replay":False,"inherited_provider_replay":False,"partial_effect_read":False,
  "inheritance_manifest_sha256":sha(INHERIT),"interruption_boundary_sha256":sha(AUDIT),
  "remaining_set_manifest_sha256":sha(REMAIN),"boundary_learned_states":blist,
  "boundary_learned_states_by_arm":byarm})
 auth={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v1-authorization",
  "date":"2026-08-31","authorized_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
  "status":"AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V1",
  "contract_path":str(OUTC.relative_to(ROOT)),"contract_sha256":csha,
  "authority":{"scientific_experiment":True,"deepseek_v2":True,"e1_b":True,"mrw_causal_comparison":True,
   "repair2_continuation_v1":True,"analyzer":False,"gpt_scientific_execution":False,
   "kimi_scientific_execution":False,"qwen_scientific_execution":False,"public_benchmark":False,
   "paper_promotion":False,"frontend_promotion":False,"submission":False,"second_backbone":False},
  "execution_scope":scope,"mindmemos_commit":oldauth["mindmemos_commit"],
  "v3_parent_provenance":{"contract_path":str(V3C.relative_to(ROOT)),"contract_sha256":V3CSHA,
   "authorization_path":str(V3A.relative_to(ROOT)),"authorization_sha256":V3ASHA,
   "run_root":im["v3_run_root"]},
  "original_repair2_parent_provenance":{"contract_sha256":c["repair2_stopped_parent"]["contract_sha256"],
   "authorization_sha256":c["repair2_stopped_parent"]["authorization_sha256"]},
  "scientific_design_changed":False,"partial_effect_read":False,"analyzer_run":False,
  "interpretation_boundary":"Single-use execution authority only for the mechanically proven unexecuted remainder of the original Repair2 V3 design.",
  "single_use":{"launch_count":1,"run_root":str(RUNROOT),"completed_unit_replay":False,
   "ambiguous_provider_response_retry":False,"automatic_v2":False},
  "private_credentials_included":False,"raw_response_ids_included":False}
 write(OUTA,auth)
 print(json.dumps({"contract":str(OUTC),"contract_sha256":csha,"authorization":str(OUTA),
  "authorization_sha256":sha(OUTA)},indent=2))
if __name__=="__main__":main()
