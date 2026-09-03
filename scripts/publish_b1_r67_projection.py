#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index
from research_pipeline.research_item_state import build_paper_registry
PID="D2-PAPER-FAILURE-MEMORY-PROVENANCE";TITLE="Does Memory Provenance Matter? Explicit Source-Outcome Cues Shift Agent Actions but Rarely Change Terminal Outcomes";GEN=ROOT/"generated";DL=ROOT/"downloads"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write_pair(n,var,p):
 (GEN/f"{n}.json").write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");(GEN/f"{n}.js").write_text(f"window.{var} = "+json.dumps(p,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
def summary(rows,old):
 o=dict(old);o["papers"]=len(rows);o["submission_ready"]=sum(x.get("submission_ready") is True for x in rows);o["gate_clean_submission_ready"]=sum(x.get("gate_clean_submission_ready") is True for x in rows);o["paper_preparation_failed"]=sum((x.get("latest_paper_preparation") or {}).get("required_gates",0)>0 and (x.get("latest_paper_preparation") or {}).get("pass") is not True for x in rows);o["immediate_submission_holds"]=sum(x.get("immediate_submission_hold") is True for x in rows);o["internal_action_required"]=sum((x.get("primary_next_action") or {}).get("action_class")!="NO_INTERNAL_ACTION" for x in rows);o["no_internal_action"]=len(rows)-o["internal_action_required"];o["by_internal_action"]=dict(sorted(Counter((x.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for x in rows).items()));o["scientific_holds"]=sum(str(x.get("scientific_status"))!="READY" for x in rows);o["by_stage"]=dict(sorted(Counter(x.get("paper_stage") or x.get("current_state") or "UNKNOWN" for x in rows).items()));return o
def main():
 p=argparse.ArgumentParser();p.add_argument("--data-root",type=Path,default=Path("/data/wyt/agent-self-evolution-observatory"));a=p.parse_args();rel=json.loads((GEN/"d2-failure-memory-provenance-r66-postoracle-manuscript-release.json").read_text());expected={"pdf":rel["stable_hashes"]["pdf"],"source_zip":rel["stable_hashes"]["source_zip"],"supplement_zip":rel["stable_hashes"]["supplement_zip"]};stable={"pdf":DL/"B1-Failure-Memory.pdf","source_zip":DL/f"{PID}-source.zip","supplement_zip":DL/f"{PID}-supplement.zip"}
 for k,path in stable.items():
  if sha(path)!=expected[k]:raise RuntimeError(f"R67 stable artifact mismatch:{k}")
 old=json.loads((GEN/"paper-registry.json").read_text());old_other={x["paper_id"]:x for x in old["papers"] if x.get("paper_id")!=PID};state=json.loads((GEN/"research-system-state.json").read_text());old_entries=((state.get("paper_acceptance") or {}).get("ledger_index") or {}).get("entries") or [];old_state_other={x["paper_id"]:x for x in old_entries if x.get("paper_id")!=PID}
 live=build_paper_ledger_index(a.data_root);row=next(x for x in live["entries"] if x.get("paper_id")==PID)
 if row.get("title")!=TITLE or row.get("current_state")!="SUBMISSION_READY" or row.get("scientific_status")!="READY" or row.get("gate_clean_submission_ready") is not True or row.get("active_unrefuted_claims")!=0:raise RuntimeError(f"live R67 B1 not clean:{row}")
 candidate_full=build_paper_registry();candidate=next(x for x in candidate_full["papers"] if x.get("paper_id")==PID)
 if candidate.get("title")!=TITLE or candidate.get("contract_sha256")!=row.get("contract_sha256"):raise RuntimeError("R67 registry candidate mismatch")
 rows=[candidate if x.get("paper_id")==PID else x for x in old["papers"]];old["papers"]=rows;old["generated_at"]=candidate_full.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds");old["source_revision"]=candidate_full.get("source_revision") or old.get("source_revision");old["summary"]=summary(rows,old.get("summary") or {});write_pair("paper-registry","PAPER_REGISTRY",old)
 pa=state.get("paper_acceptance") or {};li=pa.get("ledger_index") or {};entries=[row if x.get("paper_id")==PID else x for x in (li.get("entries") or [])];li["entries"]=entries;pa["ledger_index"]=li;state["paper_acceptance"]=pa;write_pair("research-system-state","RESEARCH_SYSTEM_STATE",state)
 if old_other!={x["paper_id"]:x for x in old["papers"] if x.get("paper_id")!=PID} or old_state_other!={x["paper_id"]:x for x in entries if x.get("paper_id")!=PID}:raise RuntimeError("non-B1 projection changed")
 rec={"schema_version":"1.0","status":"B1_R67_SELECTIVE_PUBLIC_PROJECTION_PUBLISHED","paper_id":PID,"title":TITLE,"current_revision":"R67","contract_sha256":row.get("contract_sha256"),"scientific_status":row.get("scientific_status"),"current_state":row.get("current_state"),"gate_clean_submission_ready":row.get("gate_clean_submission_ready"),"supported_claims":row.get("supported_claims"),"active_unrefuted_claims":row.get("active_unrefuted_claims"),"stable_hashes":expected,"other_paper_rows_preserved":True,"other_paper_registry_digest":digest(old_other),"other_research_system_paper_digest":digest(old_state_other),"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False};rec["receipt_sha256"]=digest(rec);(GEN/"d2-failure-memory-provenance-r67-public-projection.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n");print(json.dumps(rec,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
