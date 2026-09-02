#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json, require, sha_file


def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--preflight",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),"S1 authorization already exists")
    c=load_json(a.contract); p=load_json(a.preflight); csha=sha_file(a.contract)
    require(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1","S1 contract drift"); require(p.get("status")=="PASS_SINGLE_CASE_S1_ZERO_PROVIDER_PREFLIGHT","S1 preflight not passing"); require(p.get("contract_sha256")==csha,"S1 preflight contract drift"); require(int(p.get("provider_calls",-1))==0 and p.get("scientific_outcomes_read") is False,"S1 preflight crossed provider/outcome boundary")
    require(not Path(c["run_root"]).exists() and not Path(c["lineage_lease_path"]).exists(),"S1 root/lease no longer fresh")
    identity_sha=c["model_identity"]["sha256"]
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-s1-execution-authorization","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"AUTHORIZED_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1","contract_path":str(a.contract),"contract_sha256":csha,"preflight_path":str(a.preflight),"preflight_sha256":sha_file(a.preflight),"mindmemos_commit":c["mindmemos"]["commit"],"single_use":True,"authority":{"scientific_experiment":True,"single_case_s1":True,"provider_io":True,"updater":True,"heldout_evaluation":True,"analyzer":False,"second_backbone":False,"public_benchmark":False,"e3_confirmation":False,"paper_promotion":False,"submission":False},"execution_scope":{"phase":"single_case_s1","case_stream":"e1-tsr-00","arms":c["arms"],"replicates":[0],"allowed_modes":["e1"],"allowed_task_ids":c["heldout_task_ids"],"exact_k":1,"allow_noninitial_skill":True,"required_resolved_model":c["actor"]["resolved_model"],"identity_artifact_sha256":identity_sha,"suite_manifest_sha256":c["suite"]["suite_manifest_sha256"],"split_manifest_sha256":c["suite"]["split_manifest_sha256"],"max_turns":c["actor"]["max_turns"],"max_output_tokens":c["actor"]["max_output_tokens"],"provider_budget":{"required":True,"total_limit":c["budget"]["max_provider_calls_per_state"],"per_unit_limit":c["budget"]["max_provider_calls_per_unit"]},"exactly_once":True,"completed_unit_replay":False,"automatic_retry":False,"partial_effect_read":False,"lineage_lease_path":c["lineage_lease_path"]},"interpretation_boundary":"Authorizes exactly one development-only S1 run: e1-tsr-00, rep0, four frozen arms, 4 learned states, 72 heldout units. It grants no analyzer, E3 confirmation, second-backbone, public-benchmark, paper, or submission authority."}
    atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
