from __future__ import annotations

import argparse, fcntl, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from .config import StorageSettings
from .discovery_engine_paper_yield_benchmark import ENGINE_SPECS, _audit, _engine_context, _gen_prompt, _memory_pack, _normalize, _primary_pack, _sha_json
from .paper_assertion_policy import PAPER_ASSERTION_POLICY

Responder=Callable[...,dict[str,Any]]
ENGINES=("D5","D2")
DEFAULT_CONTRACT=Path("generated/discovery-engine-terminal-replication-contract-20260821.json")
DEFAULT_OUTPUT=Path("generated/discovery-engine-terminal-replication-20260821.json")
DEFAULT_AMENDMENT=Path("generated/discovery-engine-terminal-replication-amendment-20260821.json")


def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def _sha(x:str): return hashlib.sha256(x.encode()).hexdigest()
def _jsha(x:Any): return _sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")))
def _spec(eid): return next(row for row in ENGINE_SPECS if row[0]==eid)

def _write_json(path:Path,payload:Any):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def _archive(root:Path,kind:str,text:str):
    sha=_sha(text);path=root/kind/sha[:2]/f"{sha}.txt";path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():path.write_text(text,encoding="utf-8")
    return {"sha256":sha,"path":str(path),"bytes":len(text.encode())}

def _call(responder:Responder,root:Path,tx:str,stage:str,eid:str,prompt:str,model:str,tokens:int,temp:float):
    pa=_archive(root,"prompts",prompt);material={"transaction_id":tx,"stage":stage,"engine_id":eid,"prompt_sha256":pa["sha256"],"requested_model":model,"max_output_tokens":tokens,"temperature":temp,"store":True};fp=_jsha(material)
    try:res=responder(prompt=prompt,model=model,max_output_tokens=tokens,temperature=temp)
    except Exception as err:
        rid=str(getattr(err,"response_id","") or "");private={"schema_version":"1.0","generated_at":_now(),"request":material,"request_fingerprint":fp,"provider_error":{"type":type(err).__name__,"detail_sha256":_sha(str(err)),"response_id":rid,"status":str(getattr(err,"response_status","") or "")},"scientific_authority":False};_write_json(root/"provider-receipts"/fp[:2]/f"{fp}.json",private)
        return None,{"stage":stage,"engine_id":eid,"requested_model":model,"prompt_sha256":pa["sha256"],"request_fingerprint":fp,"status":"PROVIDER_FAILURE","error_type":type(err).__name__,"error_detail_sha256":_sha(str(err)),"provider_response_id_archived_privately":bool(rid),"scientific_authority":False}
    raw=str(res.get("text") or "");ra=_archive(root,"raw",raw);private={"schema_version":"1.0","generated_at":_now(),"request":material,"request_fingerprint":fp,"response":{"response_id":str(res.get("response_id") or ""),"status":str(res.get("status") or ""),"resolved_model":str(res.get("resolved_model") or model),"usage":res.get("usage") or {},"raw_sha256":ra["sha256"]},"scientific_authority":False};_write_json(root/"provider-receipts"/fp[:2]/f"{fp}.json",private)
    pub={"stage":stage,"engine_id":eid,"requested_model":model,"resolved_model":str(res.get("resolved_model") or model),"prompt_sha256":pa["sha256"],"raw_sha256":ra["sha256"],"request_fingerprint":fp,"usage":res.get("usage") or {},"status":str(res.get("status") or ""),"provider_response_id_archived_privately":bool(res.get("response_id")),"scientific_authority":False}
    return res,pub

def validate_contract(c,pool,memory):
    if c.get("status")!="FROZEN_BEFORE_PROVIDER_CALLS":raise ValueError("contract-not-frozen")
    f=c.get("frozen_inputs") or {}
    if f.get("primary_pool_sha256")!=_sha_json(pool):raise ValueError("primary-pool-sha-drift")
    if f.get("research_memory_wiki_sha256")!=(memory.get("wiki_sha256") or _sha_json(memory)):raise ValueError("memory-sha-drift")
    rows=c.get("engines") or []
    if [r.get("engine_id") for r in rows]!=list(ENGINES) or any(int(r.get("candidate_budget") or 0)!=6 for r in rows):raise ValueError("engine-budget-drift")
    m=c.get("models") or {}
    if m.get("generator_requested")!="kimi-k3" or m.get("reviewer_requested")!="deepseek-v4-pro":raise ValueError("model-drift")
    p=c.get("terminal_scoring_policy") or {}
    if p.get("early_reviewer_score_is_terminal_metric") is not False or p.get("winner_may_be_declared_before_terminal_outcomes") is not False:raise ValueError("premature-ranking-forbidden")

def validate_amendment(amendment,contract):
    if amendment is None:return "","",{}
    if amendment.get("status")!="FROZEN_OPERATIONAL_AMENDMENT":raise ValueError("amendment-not-frozen")
    if amendment.get("transaction_id")!=contract.get("transaction_id"):raise ValueError("amendment-transaction-mismatch")
    if amendment.get("original_contract_sha256")!=_jsha(contract):raise ValueError("amendment-contract-sha-mismatch")
    trigger=amendment.get("trigger") or {};change=amendment.get("operational_change") or {};strict=amendment.get("strict_transport") or {};model=str(change.get("generator_requested") or "")
    if trigger.get("class")!="PROVIDER_SUPPORT_FAILURE" or trigger.get("scientific_authority") is not False:raise ValueError("amendment-trigger-invalid")
    if model not in {"glm-5.3","doubao-seed-2.0-mini"} or change.get("frozen_evidence_unchanged") is not True or change.get("terminal_scoring_policy_unchanged") is not True:raise ValueError("amendment-scope-invalid")
    if change.get("scientific_gates_unchanged") is False:raise ValueError("amendment-scientific-gate-drift")
    gs=int(change.get("generation_shards_per_engine") or 1);gn=int(change.get("candidates_per_generation_shard") or 6);ts=int(change.get("triage_shards_per_engine") or 1);tn=int(change.get("candidates_per_triage_shard") or 6)
    if gs*gn!=6 or ts*tn!=6:raise ValueError("amendment-shard-budget-drift")
    if strict.get("provider_post_retries")!=0 or strict.get("single_post_per_request_fingerprint") is not True:raise ValueError("amendment-transport-not-strict")
    return model,_jsha(amendment),change

def _triage_prompt(rows,prefs,mids):
    slim=[{k:r.get(k) for k in ("candidate_id","engine_id","title","birth_evidence_refs","memory_refs","scientific_question","observed_trigger","structural_variable","strongest_same_information_baseline","baseline_counterexample","cheapest_falsifier","closest_known_explanation","residual_after_reduction","paper_level_claim")} for r in rows]
    shape={"triage":[{"candidate_id":"D5-C01","provisional_basin_signature":"","strongest_same_information_attack":"","possible_direct_counterevidence":"","cheapest_decisive_falsifier":"","support_blocker":"","duplicate_or_collision_target":"","what_must_be_true_for_paper":"","advisory_route":"ATTACK_NOW|FALSIFIER_NOW|SUPPORT_HOLD|DUPLICATE_CHECK"}]}
    return f'''You are an adversarial scientific triage reviewer with ZERO scientific authority. You cannot close or promote a claim. Missing evidence creates experiment debt. Scientific closure requires direct counterevidence, exact same-information reduction, or a scope-matched principle counter-explanation. Do not rank engines and do not use novelty scores. For each candidate identify the strongest same-information attack, one decisive falsifier, and any duplicate scientific basin. Keep each text field under 35 words.\nVALID PRIMARY REFS: {sorted(prefs)}\nVALID MEMORY IDS: {sorted(mids)}\nCANDIDATES:\n{json.dumps(slim,ensure_ascii=False)}\nReturn strict JSON only:\n{json.dumps(shape,ensure_ascii=False)}'''

def _dedup(rows):
    seen={};dups=[]
    for r in rows:
        mat={k:" ".join(str(r.get(k) or "").lower().split()) for k in ("scientific_question","structural_variable","paper_level_claim")};fp=_jsha(mat);r["deterministic_candidate_fingerprint"]=fp
        if fp in seen:r["exact_duplicate_of"]=seen[fp];dups.append({"candidate_id":r["candidate_id"],"duplicate_of":seen[fp],"fingerprint":fp,"scientific_authority":False})
        else:seen[fp]=r["candidate_id"];r["exact_duplicate_of"]=""
    return rows,dups

def run_replication(*,contract,pool,memory,generator_responder:Responder,reviewer_responder:Responder,private_root:Path,amendment=None):
    validate_contract(contract,pool,memory);tx=str(contract["transaction_id"]);csha=_jsha(contract);override,asha,op=validate_amendment(amendment,contract);primary=_primary_pack(pool);mem=_memory_pack(memory);prefs={str(r.get("ref")) for r in primary if r.get("ref")};mids={str(r.get("memory_id")) for r in mem if r.get("memory_id")};models=contract.get("models") or {};gm=override or str(models["generator_requested"]);rm=str(models["reviewer_requested"]);gsh=int(op.get("generation_shards_per_engine") or 1);gn=int(op.get("candidates_per_generation_shard") or 6);gtok=int(op.get("generator_max_output_tokens") or 11000);tsh=int(op.get("triage_shards_per_engine") or 1);tn=int(op.get("candidates_per_triage_shard") or 6);ttok=int(op.get("reviewer_max_output_tokens") or 8500)
    candidates=[];grec=[];trec=[];fail=[]
    for eid in ENGINES:
        spec=_spec(eid);ep,em=_engine_context(spec,primary,mem)
        for shard in range(gsh):
            prompt=_gen_prompt(spec,ep,em,gn)+f"\nGENERATION SHARD {shard+1}/{gsh}: fill this shard with distinct scientific basins. Candidate IDs are assigned after parsing.";res,receipt=_call(generator_responder,private_root,tx,f"generation-shard-{shard+1}",eid,prompt,gm,gtok,.15);grec.append(receipt)
            if res is None:fail.append(dict(receipt));continue
            try:payload=extract_json_object(str(res.get("text") or ""))
            except Exception as err:fail.append({"stage":"generation_parse","engine_id":eid,"shard":shard+1,"status":"PARSE_FAILURE","raw_sha256":receipt.get("raw_sha256"),"error_type":type(err).__name__,"error_detail_sha256":_sha(str(err)),"scientific_authority":False});continue
            for i,raw in enumerate([x for x in (payload.get("candidates") or []) if isinstance(x,dict)][:gn],1):
                idx=shard*gn+i;row=_normalize(raw,spec,idx);row["deterministic_audit"]=_audit(row,prefs,mids);row["birth_receipt"]={"transaction_id":tx,"contract_sha256":csha,"operational_amendment_sha256":asha,"generation_shard":shard+1,"generation_raw_sha256":receipt.get("raw_sha256"),"generation_prompt_sha256":receipt.get("prompt_sha256"),"generator_requested_model":gm,"generator_resolved_model":receipt.get("resolved_model"),"derivation_type":"independent_generation","scientific_authority":False};candidates.append(row)
    unique,dups=_dedup(candidates);triage={}
    for eid in ENGINES:
        erows=[r for r in unique if r["engine_id"]==eid]
        for shard in range(tsh):
            batch=erows[shard*tn:(shard+1)*tn]
            if not batch:continue
            prompt=_triage_prompt(batch,prefs,mids);res,receipt=_call(reviewer_responder,private_root,tx,f"adversarial-triage-shard-{shard+1}",eid,prompt,rm,ttok,0.0);trec.append(receipt)
            if res is None:fail.append(dict(receipt));continue
            try:payload=extract_json_object(str(res.get("text") or ""))
            except Exception as err:fail.append({"stage":"triage_parse","engine_id":eid,"shard":shard+1,"status":"PARSE_FAILURE","raw_sha256":receipt.get("raw_sha256"),"error_type":type(err).__name__,"error_detail_sha256":_sha(str(err)),"scientific_authority":False});continue
            for row in payload.get("triage") or []:
                if isinstance(row,dict) and row.get("candidate_id"):row=dict(row);row["triage_raw_sha256"]=receipt.get("raw_sha256");row["scientific_authority"]=False;triage[str(row["candidate_id"])]=row
    for row in unique:
        row["adversarial_triage"]=triage.get(row["candidate_id"],{"candidate_id":row["candidate_id"],"advisory_route":"UNAVAILABLE","scientific_authority":False});row["terminal_state"]="PENDING_CHEAPEST_FALSIFIER";row["manuscript_stance_if_unrefuted"]="ACTIVE_UNREFUTED_HYPOTHESIS";row["experiment_debt"]=[];row["scientific_authority"]=False
    estate=[]
    for eid in ENGINES:
        erows=[r for r in unique if r["engine_id"]==eid];estate.append({"engine_id":eid,"generated":len(erows),"deterministic_unique":len({r.get("deterministic_candidate_fingerprint") for r in erows}),"provenance_valid":sum((r.get("deterministic_audit") or {}).get("provenance_valid") is True for r in erows),"schema_complete":sum((r.get("deterministic_audit") or {}).get("schema_complete") is True for r in erows),"terminal_complete_papers":0,"terminal_scientific_stops":0,"active_unrefuted":0,"pending_terminal_adjudication":len(erows),"winner_declared":False,"scientific_authority":False})
    return {"schema_version":"1.0","transaction_id":tx,"generated_at":_now(),"status":"GENERATION_AND_ADVERSARIAL_TRIAGE_COMPLETE","contract_sha256":csha,"operational_amendment_sha256":asha,"frozen_inputs":contract.get("frozen_inputs") or {},"models":{"generator_requested":gm,"original_generator_requested":str(models["generator_requested"]),"reviewer_requested":rm,"generation_resolved_models":sorted({str(r.get('resolved_model') or '') for r in grec if r.get('resolved_model')}),"triage_resolved_models":sorted({str(r.get('resolved_model') or '') for r in trec if r.get('resolved_model')})},"execution_shape":{"generation_shards_per_engine":gsh,"candidates_per_generation_shard":gn,"triage_shards_per_engine":tsh,"candidates_per_triage_shard":tn},"policy":{"terminal_outcomes_only_for_engine_comparison":True,"early_reviewer_score_is_terminal_metric":False,"winner_declared":False,"reviewer_is_adversarial_zero_authority":True,"operational_fallback_has_scientific_authority":False,"unrefuted_hypothesis_stays_active":PAPER_ASSERTION_POLICY["unrefuted_hypothesis_stays_active"],"missing_evidence_creates_experiment_debt":PAPER_ASSERTION_POLICY["missing_evidence_creates_experiment_debt"]},"summary":{"engines":2,"requested_candidates":12,"generated_candidates":len(candidates),"deterministic_unique_candidates":len({r.get('deterministic_candidate_fingerprint') for r in unique}),"exact_duplicate_candidates":len(dups),"generation_provider_calls":sum(r.get("status")!="PROVIDER_FAILURE" for r in grec),"triage_provider_calls":sum(r.get("status")!="PROVIDER_FAILURE" for r in trec),"provider_or_parse_failures":len(fail),"terminal_outcomes_resolved":0},"engine_state":estate,"exact_duplicate_receipts":dups,"candidates":unique,"provider_receipts":{"generation":grec,"adversarial_triage":trec},"failures":fail,"private_raw_root":str(private_root),"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}

def main():
    p=argparse.ArgumentParser();p.add_argument("--contract",type=Path,default=DEFAULT_CONTRACT);p.add_argument("--amendment",type=Path);p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT);p.add_argument("--private-root",type=Path);a=p.parse_args();contract=json.loads(a.contract.read_text());amendment=json.loads(a.amendment.read_text()) if a.amendment else None;f=contract["frozen_inputs"];pool=json.loads(Path(f["primary_pool_path"]).read_text());memory=json.loads(Path(f["research_memory_path"]).read_text());private=a.private_root or StorageSettings.from_env().data_root/"discovery-engine-terminal-replication-20260821";private.mkdir(parents=True,exist_ok=True);lock=(private/"transaction.lock").open("a+")
    try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:print(json.dumps({"status":"TRANSACTION_ALREADY_RUNNING","transaction_id":contract.get("transaction_id")},ensure_ascii=False));return
    csha=_jsha(contract);_,asha,_=validate_amendment(amendment,contract)
    if a.output.exists():
        existing=json.loads(a.output.read_text());
        if existing.get("status")=="GENERATION_AND_ADVERSARIAL_TRIAGE_COMPLETE" and existing.get("contract_sha256")==csha and str(existing.get("operational_amendment_sha256") or "")==asha:print(json.dumps({"status":"REPLAY_COMPLETED_PUBLIC_STATE","summary":existing.get("summary"),"engine_state":existing.get("engine_state")},ensure_ascii=False,indent=2));return
    base=ArkSettings.from_env();strict=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0);client=ArkResponsesClient(strict)
    def call(**kw):return client.respond(kw["prompt"],model=kw["model"],max_output_tokens=kw["max_output_tokens"],temperature=kw["temperature"],thinking=None,store=True)
    report=run_replication(contract=contract,pool=pool,memory=memory,generator_responder=call,reviewer_responder=call,private_root=private,amendment=amendment);_write_json(a.output,report);print(json.dumps({"status":report["status"],"summary":report["summary"],"engine_state":report["engine_state"]},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
