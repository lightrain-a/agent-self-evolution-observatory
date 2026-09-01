#!/usr/bin/env python3
"""Outcome-blind PIA-1 for E2-R17 DeepSeek V2 Repair2."""
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
V3=Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-v3-20260831")
V1=Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-continuation-v1-20260831")
RR=Path("/data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-deepseek-v2-repair2-v3-resume-v1-20260831")
ARMS=("win_c","mrw"); UNIT="e1-msp-01/rep0"; PR=V3/"states/e1-msp-01/replicate_0"
FAIL_ARM="win_c"; FAIL_TASK="r17-b4-ska-p8"
H={
"v3_contract":"312e970520794c564b23a9717f4c40d4baeb0674619da334c8fcc20ee95fc045",
"v3_auth":"7aa826db915b40840fb54ca2c269a23c4f74807bae74fd99285eac6875ee5b74",
"v3_runner":"a735c7cd15f10a4feb52cc171b5e906494ae53205e29f334ecd7e3afbf7efe30",
"v3_actor":"a04f36ba6270d51eedf3d4fde31028f6aa3fc50852a6ce58736c45ff98eff0d0",
"v3_completed":"ea4945723eda5b46643b65626f1300da0952870ed4fd122ec65e8341fc44acb8",
"v3_valid":"64c879e576e4da6ec4c40eede8c1ff0d2f26be0def22d4a1cf04a50464b1aab9",
"v3_lock":"8a64eca23c197ddfd83d51387491d1a2330be2ab2c3ba82d210fbcecabe9a888",
"v1_contract":"b944797b6333c66bf1edf9ae789aa16e8b19df8763dbf89280da1efd8dd1c2c2",
"v1_auth":"14df6c41e0ba3b0a300f341f5ed73599bf0545392aa86c888383dd4729e6d67b",
"v1_completed":"77b2753e2ad3b64bb1cbdeaa1981ac589f4e86cc95930225bebee1c7652d4a41",
"v1_valid":"9e8319ea9402aba748a7d12e9aa703154df1ac3d0873befa3faeaa2865f9733b",
"v1_lock":"be82d901c7a8bb8c87e263f060ed390b9645934e0e40d4dde2a17084f9a34c85",
"resume_auth":"cfd1fd9614bbbd09b72ff8ada4a74f6db412b3731de5e6d25b902a291a6081ff",
"resume_start":"9542cffe4bc9a7707acd4a5fc3838c846f54f97060b5524d74ceb7ecad9c9c90",
"resume_receipt":"98458a7a49101cef73d103433823782ccf6494e58fe4bd2115b3e039635afcd7",
"resume_audit":"7fa025b0bb38406cd628a66cf1e5ee644ce90fad596a360c500bd791be4ff78f",
"resume_inherit":"3ec1cc780e62afd0fa04ec5285097d26c5c4313b24d73b4b50fae7f4cbeec84a",
"resume_remaining":"3c1879db47283f48a4d6e21d3a2fda8b00fa8f3a32ab9c6b7ca5fa4c42213128",
"duplicate_stop":"e001e07e03a392c14733fa94c8e50aeb10cc80d995877f2b562d8fe93799e501",
"failure":"9d381657e4c526fe4014e96839203aad13aae81c7b3439f3be85a9bdabaf817c"}
RF={
"resume_auth":RR/"generated/e2-r17-deepseek-v2-repair2-v3-host-shutdown-resume-v1-authorization-20260831.json",
"resume_start":RR/"generated/e2-r17-deepseek-v2-repair2-v3-host-shutdown-resume-v1-start-adjudication-20260831.json",
"resume_receipt":V3/"resume_v1_start_receipt.json",
"resume_audit":RR/"generated/e2-r17-deepseek-v2-repair2-v3-host-shutdown-audit-20260831.json",
"resume_inherit":RR/"generated/e2-r17-deepseek-v2-repair2-v3-host-shutdown-inheritance-20260831.json",
"resume_remaining":RR/"generated/e2-r17-deepseek-v2-repair2-v3-host-shutdown-remaining-20260831.json",
"duplicate_stop":RR/"generated/e2-r17-deepseek-v2-repair2-duplicate-continuation-replay-stop-20260831.json"}

def req(x,m):
 if not x: raise RuntimeError(m)
def sha(p):
 p=Path(p); req(p.is_file(),f"missing: {p}"); h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def obj(p):
 x=json.loads(Path(p).read_text()); req(isinstance(x,dict),f"not object: {p}"); return x
def rows(p):
 return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def put(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(p.name+f".tmp-{os.getpid()}")
 t.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); os.replace(t,p)
def no_live():
 out=subprocess.run(["ps","-eo","pid=,pgid=,stat=,args="],text=True,capture_output=True,check=True).stdout
 n=("run_e2_r17_deepseek_v2_repair2","run_e2_r17_actor_pool","deepseek-v2-repair2-v3-20260831","deepseek-v2-repair2-continuation-v1-20260831")
 return [x.strip() for x in out.splitlines() if any(y in x for y in n) and "pia1" not in x]

def design(c):
 ss=[str(x["stream_id"]) if isinstance(x,dict) else str(x) for x in c["streams"]]
 us=[f"{s}/rep{r}" for s in ss for r in range(4)]; ts=list(map(str,c["heldout"]["task_ids"]))
 req(len(ss)==12 and len(us)==48 and len(set(us))==48,"design drift")
 req(len(ts)==18 and len(set(ts))==18,"heldout drift"); return us,ts

def eval_manifest(p,expected,tasks,skill,receipt,contract=None,auth=None):
 req(sha(p)==expected,f"eval manifest drift: {p}"); rr=rows(p)
 req([str(x["task_id"]) for x in rr]==tasks,f"task order drift: {p}")
 for r in rr:
  tid=str(r["task_id"]); sp=Path(r["summary_path"]); rp=Path(r["trajectory_ref_path"])
  req(sha(sp)==r["summary_sha256"],f"summary drift: {tid}")
  req(sha(rp)==r["trajectory_ref_sha256"],f"ref drift: {tid}")
  s=obj(sp)
  req(s.get("status")=="COMPLETED" and s.get("mode")=="e1" and int(s.get("k"))==1,f"summary protocol: {tid}")
  req(int(s.get("max_turns"))==10 and int(s.get("provider_retry_limit"))==0,f"actor budget: {tid}")
  req(s.get("requested_model")=="deepseek-v4-pro" and s.get("resolved_model")=="deepseek-v4-pro-ga-260813",f"model drift: {tid}")
  req(len(s.get("tasks") or [])==1 and s["tasks"][0].get("task_id")==tid,f"summary task: {tid}")
  req(s.get("skill_pre_sha256")==skill and s.get("updater_receipt_sha256")==receipt,f"state bind: {tid}")
  if contract: req(s.get("contract_sha256")==contract,f"contract drift: {tid}")
  if auth: req(s.get("authorization_sha256")==auth,f"auth drift: {tid}")
  ref=obj(rp); req(ref.get("task_id")==tid and str(ref.get("technical_status")).lower()=="completed",f"ref status: {tid}")
  req(sha(Path(ref["trajectory_path"]))==ref["trajectory_sha256"],f"trajectory drift: {tid}")
  # Scores exist in source JSON but are deliberately never accessed.
 return len(rr)

def audit_v3(units,tasks):
 cp=V3/"checkpoints/completed_replicates.jsonl"; vp=V3/"checkpoints/valid_replicates.jsonl"
 req(sha(cp)==H["v3_completed"] and sha(vp)==H["v3_valid"],"V3 manifest SHA drift")
 req(sha(V3/".exclusive.lock")==H["v3_lock"],"V3 lock drift")
 cr,vr=rows(cp),rows(vp); req(len(cr)==len(vr)==28,"V3 count")
 req([x["unit_id"] for x in cr]==units[:28]==[x["unit_id"] for x in vr],"V3 not frozen prefix")
 req([(x["unit_id"],x["source"]) for x in cr]==[(x["unit_id"],x["source"]) for x in vr],"V3 source mismatch")
 req(Counter(x["source"] for x in vr)==Counter({"repair1_inherited":14,"repair2_m1_recovered":1,"repair2_v3_fresh":13}),"source counts")
 n=0
 for a,b in zip(cr,vr):
  req(sha(Path(a["summary_path"]))==a["summary_sha256"],f"pair summary: {a['unit_id']}")
  req(sha(Path(b["pair_summary_path"]))==b["pair_summary_sha256"],f"valid summary: {b['unit_id']}")
  for arm in ARMS:
   x=b["arms"][arm]; sr=Path(x["state_root"]); up=Path(x.get("update_receipt_path") or sr/"update/update_receipt.json"); sk=sr/"update/skill_post/SKILL.md"
   req(sha(up)==x["update_receipt_sha256"] and sha(sk)==x["skill_sha256"],f"state SHA: {b['unit_id']}/{arm}")
   u=obj(up); req(u.get("status")=="COMPLETED" and u.get("skill_post_sha256")==x["skill_sha256"],f"receipt: {b['unit_id']}/{arm}")
   ec=ea=None
   if b["source"]=="repair2_v3_fresh":
    req(u.get("contract_sha256")==H["v3_contract"] and u.get("authorization_sha256")==H["v3_auth"],f"V3 receipt bind: {b['unit_id']}/{arm}")
    ec,ea=H["v3_contract"],H["v3_auth"]
   n+=eval_manifest(Path(x["eval_manifest_path"]),x["eval_manifest_sha256"],tasks,x["skill_sha256"],x["update_receipt_sha256"],ec,ea)
 req(n==1008,"complete heldout count"); return vr

def audit_timing():
 for k,p in RF.items(): req(sha(p)==H[k],f"resume evidence: {k}")
 a=obj(RF["resume_receipt"]); b=obj(V1/"checkpoints/run_start_receipt.json")
 from datetime import datetime as D
 ta=D.fromisoformat(a["started_at_utc"]); tb=D.fromisoformat(b["created_at_utc"])
 req(ta<tb and int(a["pid"])==int(a["pgid"])==584224 and int(b["pid"])==int(b["pgid"])==832381,"lineage timing")
 return {"resume_started":a["started_at_utc"],"duplicate_started":b["created_at_utc"],"lead_seconds":int((tb-ta).total_seconds())}

def audit_v1(v3):
 cp=V1/"checkpoints/completed_replicates.jsonl"; vp=V1/"checkpoints/valid_replicates.jsonl"
 req(sha(cp)==H["v1_completed"] and sha(vp)==H["v1_valid"] and sha(V1/".exclusive.lock")==H["v1_lock"],"V1 drift")
 cr,vr=rows(cp),rows(vp); req(len(cr)==len(vr)==17,"V1 count")
 req([x["unit_id"] for x in cr]==[x["unit_id"] for x in v3[:17]],"V1 inheritance")
 req(all(x.get("execution_segment")=="v3_pre_exit_inherited" and x.get("provider_replay") is False for x in cr),"V1 row flags")
 req(not list(V1.glob("**/update/update_receipt.json")),"V1 updater replay")
 ss=sorted(V1.glob("boundary/**/evaluation_summary.json")); req(len(ss)==12,"V1 eval count")
 dr=[]
 for p in ss:
  s=obj(p); req(s.get("status")=="COMPLETED" and s.get("contract_sha256")==H["v1_contract"] and s.get("authorization_sha256")==H["v1_auth"],f"V1 summary: {p}")
  tid=str(s["tasks"][0]["task_id"]); arm="win_c" if "/win_c/" in str(p) else "mrw"
  pp=V3/"states/e1-ioc-00/replicate_1"/arm/"evaluation"/tid/"evaluation_summary.json"; req(pp.is_file(),f"no canonical counterpart: {arm}/{tid}")
  dr.append({"unit_id":"e1-ioc-00/rep1","arm":arm,"task_id":tid,"child_summary_path":str(p),"child_summary_sha256":sha(p),"canonical_summary_path":str(pp),"canonical_summary_sha256":sha(pp),"scientific_inclusion":False})
 es={"r17-b4-ska-p4","r17-b4-ska-p5","r17-b4-ska-p8","r17-b4-tsr-p0","r17-b4-tsr-p6","r17-b4-tsr-p8"}
 for arm in ARMS: req({x["task_id"] for x in dr if x["arm"]==arm}==es,f"V1 task set: {arm}")
 inv=[{"relative_path":str(p.relative_to(V1)),"path":str(p),"size_bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(x for x in V1.rglob("*") if x.is_file())]
 return dr,inv

def pair29(tasks):
 miss=[]; counts={}; claims={}; binds={}
 for arm in ARMS:
  sr=PR/arm; up=sr/"update/update_receipt.json"; sk=sr/"update/skill_post/SKILL.md"; mp=sr/"checkpoints/completed_eval_tasks.jsonl"
  u=obj(up); req(u.get("status")=="COMPLETED" and u.get("contract_sha256")==H["v3_contract"] and u.get("authorization_sha256")==H["v3_auth"],f"pair29 receipt: {arm}")
  ss,us=sha(sk),sha(up); req(u.get("skill_post_sha256")==ss,f"pair29 skill: {arm}")
  rr=rows(mp); done=[str(x["task_id"]) for x in rr]; req(done==tasks[:len(done)],f"pair29 order: {arm}")
  for x in rr: req(sha(Path(x["summary_path"]))==x["summary_sha256"] and sha(Path(x["trajectory_ref_path"]))==x["trajectory_ref_sha256"],f"pair29 artifact: {arm}/{x['task_id']}")
  counts[arm]=len(rr)
  con=sqlite3.connect(f"file:{sr/'checkpoints/provider_budget.sqlite3'}?mode=ro&immutable=1",uri=True)
  try: claims[arm]=int(con.execute("select count(*) from claims").fetchone()[0])
  finally: con.close()
  binds[arm]={"state_root":str(sr),"skill_path":str(sk),"skill_sha256":ss,"update_receipt_path":str(up),"update_receipt_sha256":us,"completed_eval_manifest_path":str(mp),"completed_eval_manifest_sha256":sha(mp),"completed_tasks":done,"parent_claims":claims[arm]}
  for tid in tasks:
   if tid not in done: miss.append({"unit_id":UNIT,"arm":arm,"task_id":tid,"classification":"explicit_429_logical_unit_recovery" if (arm,tid)==(FAIL_ARM,FAIL_TASK) else "never_started_measurement","parent_state_root":str(sr),"parent_skill_sha256":ss,"parent_update_receipt_sha256":us,"parent_contract_sha256":H["v3_contract"],"parent_authorization_sha256":H["v3_auth"],"provider_replay_of_completed_unit":False})
 req(counts=={"win_c":14,"mrw":15} and claims=={"win_c":93,"mrw":117},"pair29 counts")
 req(len(miss)==7 and sum(x["classification"].startswith("explicit_429") for x in miss)==1,"recovery set")
 fp=PR/FAIL_ARM/"evaluation"/FAIL_TASK/"cases"/FAIL_TASK/"rollout_0/r17_technical_failure.json"; req(sha(fp)==H["failure"],"failure SHA")
 f=obj(fp); ar=f.get("adapter_receipts") or []; pc=f.get("provider_budget_claims") or []
 req([int(x["provider_budget_claim_id"]) for x in ar]==[89,90,91,92] and all(x.get("provider_status")=="completed" and x.get("hidden_provider_retry_used") is False for x in ar),"429 prefix")
 req(
[int(x["claim_id"]) for x in pc]==[89,90,91,92,93] and "HTTP 429" in str(f.get("error")) and "AccountQuotaExceeded" in str(f.get("error")),"429 evidence")
 req(f.get("scientific_outcome") is False and int(f.get("provider_retry_limit"))==0 and not (PR/FAIL_ARM/"evaluation"/FAIL_TASK/"evaluation_summary.json").exists(),"429 boundary")
 return {"pair29_unit_id":UNIT,"completed_counts_by_arm":counts,"parent_claim_counts_by_arm":claims,"state_bindings":binds,"missing_measurements_in_frozen_order":miss,"missing_measurement_count":7,"unique_429_recovery_count":1,"never_started_measurement_count":6,"failed_429_evidence":{"path":str(fp),"sha256":H["failure"],"completed_adapter_claim_ids":[89,90,91,92],"explicit_429_claim_id":93,"ambiguous_completion":False,"scientific_outcome":False,"old_partial_directory_quarantined":True}}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",default="generated"); a=ap.parse_args(); out=REPO/a.output_dir
 req(not no_live(),"related process alive")
 cp=REPO/"generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json"; au=REPO/"generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json"; c1=REPO/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-contract-20260831.json"; a1=REPO/"generated/e2-r17-deepseek-v2-repair2-continuation-v1-authorization-20260831.json"
 req(sha(cp)==H["v3_contract"] and sha(au)==H["v3_auth"] and sha(c1)==H["v1_contract"] and sha(a1)==H["v1_auth"],"contract/auth drift")
 req(sha(REPO/"scripts/run_e2_r17_deepseek_v2_repair2_continuation_v3.py")==H["v3_runner"] and sha(REPO/"scripts/run_e2_r17_actor_pool_repair2_v3.py")==H["v3_actor"],"runner drift")
 units,tasks=design(obj(cp)); timing=audit_timing(); vv=audit_v3(units,tasks); dup,inv=audit_v1(vv); rec=pair29(tasks); now=datetime.now(timezone.utc).isoformat(timespec="seconds")
 canon={"schema_version":"1.0","artifact_type":"e2-r17-repair2-pia1-canonical-lineage","created_at_utc":now,"status":"PIA1_PASS_V3_RESUME_CANONICAL_LINEAGE","canonical_run_root":str(V3),"canonical_contract_sha256":H["v3_contract"],"canonical_authorization_sha256":H["v3_auth"],"canonical_runner_sha256":H["v3_runner"],"canonical_actor_sha256":H["v3_actor"],"completed_manifest_sha256":H["v3_completed"],"valid_manifest_sha256":H["v3_valid"],"completed_prefix":[x["unit_id"] for x in vv],"counts":{"complete_pairs":28,"complete_learned_states":56,"total_learned_states_including_pair29":58,"complete_heldout":1037},"incomplete_boundary_unit":UNIT,"timing":timing,"canonicality_basis":["earlier same-root V3 resume authority","unchanged original V3 contract/auth/runner/actor/order","duplicate child used distinct contract/auth/root","duplicate child updater calls=0","duplicate outputs never entered V3 manifests","whole duplicate child root permanently excluded"],"provider_calls":0,"partial_effect_read":False,"scientific_scores_read":False,"analyzer_run":False}
 q={"schema_version":"1.0","artifact_type":"e2-r17-repair2-pia1-permanent-v1-quarantine","created_at_utc":now,"status":"PERMANENTLY_QUARANTINED_DUPLICATE_CONTINUATION_V1","root":str(V1),"contract_sha256":H["v1_contract"],"authorization_sha256":H["v1_auth"],"child_manifest_pairs":17,"new_updater_calls":0,"duplicate_heldout_evaluations":12,"duplicate_rows":dup,"file_inventory":inv,"scientific_inclusion":False,"mutation":"forbidden","reuse":"forbidden","analysis":"forbidden","partial_effect_read":False,"scientific_scores_read":False}
 r={"schema_version":"1.0","artifact_type":"e2-r17-repair2-pia1-pair29-recovery-set","created_at_utc":now,"status":"PIA1_PASS_PAIR29_MEASUREMENT_ONLY_RECOVERY_ELIGIBLE","canonical_lineage_only":True,"updater_calls_authorized":0,"scientific_design_changed":False,"prompt_changed":False,"model_changed":False,"task_order_changed":False,"correction_budget_changed":False,"analysis_changed":False,"partial_effect_read":False,"scientific_scores_read":False,"analyzer_run":False,**rec}
 pc=out/"e2-r17-deepseek-v2-repair2-pia1-canonical-v3-lineage-20260901.json"; pq=out/"e2-r17-deepseek-v2-repair2-pia1-permanent-v1-quarantine-20260901.json"; pr=out/"e2-r17-deepseek-v2-repair2-pia1-pair29-recovery-set-20260901.json"
 put(pc,canon); put(pq,q); put(pr,r)
 adj={"schema_version":"1.0","artifact_type":"e2-r17-repair2-outcome-blind-pia","created_at_utc":now,"status":"PIA1_PASS_V3_RESUME_CANONICAL_V1_PERMANENTLY_QUARANTINED","decision":"V3_HOST_SHUTDOWN_RESUME_IS_CANONICAL_LINEAGE","duplicate_decision":"CONTINUATION_V1_PERMANENTLY_EXCLUDED","canonical_lineage_manifest_path":str(pc.relative_to(REPO)),"canonical_lineage_manifest_sha256":sha(pc),"duplicate_quarantine_manifest_path":str(pq.relative_to(REPO)),"duplicate_quarantine_manifest_sha256":sha(pq),"pair29_recovery_set_path":str(pr.relative_to(REPO)),"pair29_recovery_set_sha256":sha(pr),"verified_canonical_pairs":28,"verified_canonical_heldout_including_pair29":1037,"duplicate_child_updater_calls":0,"duplicate_child_heldout_evaluations":12,"provider_calls_during_pia":0,"partial_effect_read":False,"scientific_scores_read":False,"analyzer_run":False,"scientific_belief_update":"NONE","next_gate":"SEPARATELY_AUTHORIZED_PAIR29_MEASUREMENT_ONLY_RECOVERY"}
 pa=out/"e2-r17-deepseek-v2-repair2-pia1-adjudication-20260901.json"; put(pa,adj)
 print(json.dumps({"status":adj["status"],"canonical_pairs":28,"duplicate_heldout_quarantined":12,"pair29_missing_measurements":7,"unique_429_recovery":1,"provider_calls":0,"partial_effect_read":False,"artifacts":{str(x.relative_to(REPO)):sha(x) for x in (pc,pq,pr,pa)}},indent=2,sort_keys=True))
if __name__=="__main__": main()
