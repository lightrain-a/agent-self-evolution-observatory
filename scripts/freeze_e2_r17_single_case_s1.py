#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_actor_pool import load_frozen_pool


def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--parent",type=Path,required=True); ap.add_argument("--design",type=Path,required=True); ap.add_argument("--selector-freeze",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    req(not a.output.exists(),"S1 contract already exists")
    parent=load(a.parent); design=load(a.design); s0=load(a.selector_freeze)
    req(parent.get("status")=="FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2","parent V2 contract drift")
    req(design.get("status")=="DESIGN_ONLY_ZERO_AUTHORITY" and not any((design.get("authority") or {}).values()),"S1 design not zero-authority")
    req(s0.get("status")=="S0_SELECTOR_FREEZE_PASS_ZERO_PROVIDER" and int(s0.get("provider_calls",-1))==0,"S0 selector freeze not passing")
    req(s0.get("case_stream")==design["case"]["stream_id"]=="e1-tsr-00","S1 case stream drift")
    suite=Path(parent["suite"]["root"]); split=load(suite/"r17_split_manifest.json"); tasks=list(map(str,split["e1_update_streams"]["e1-tsr-00"])); req(len(tasks)==8,"S1 stream must have eight tasks")
    by_s0={r["task_id"]:r for r in s0["units"]}; bindings=[]
    for task in tasks:
        p=Path(parent["e1_a_pool_root"])/"cases"/task/"pool_k8.json"; req(p.is_file(),f"pool missing {task}"); pool=load_frozen_pool(p); req(pool.pool_id==by_s0[task]["pool_id"] and sha(p)==by_s0[task]["pool_sha256"],f"pool/S0 drift {task}"); bindings.append({"task_id":task,"path":str(p),"sha256":sha(p),"pool_id":pool.pool_id})
    code_paths={
      "diagnostic_witness":"research_pipeline/e2_r17_diagnostic_witness.py",
      "s1_runner":"scripts/run_e2_r17_single_case_s1.py",
      "s1_actor_wrapper":"scripts/run_e2_r17_actor_pool_single_case_s1.py",
      "base_actor_runner":"scripts/run_e2_r17_actor_pool_repair2_continuation_v2.py",
      "base_runner_helpers":"scripts/run_e2_r17_deepseek_v2_repair2_continuation_v2.py",
      "updater_wrapper":"research_pipeline/e2_r17_mindmemos_updater.py",
      "updater_adapter":"research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "provider_budget":"research_pipeline/e2_r17_provider_budget.py",
      "frozen_renderer":"research_pipeline/e2_r17_evidence_window_v2.py",
      "frozen_projection":"research_pipeline/e2_r17_search_projection_runner.py",
      "preflight":"scripts/preflight_e2_r17_single_case_s1.py",
      "authorizer":"scripts/authorize_e2_r17_single_case_s1.py",
    }
    bound={k:{"path":v,"sha256":sha(ROOT/v)} for k,v in code_paths.items()}
    payload={
      "schema_version":"1.0","artifact_type":"e2-r17-single-case-diagnostic-witness-s1-contract","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1",
      "scientific_object":"E2-R17-SINGLE-CASE-DIAGNOSTIC-WITNESS-PILOT-20260902","case_stream":"e1-tsr-00","replicate":0,"arms":["win_c","first_fail","progress_fail","progress_contrast"],"scientific_scope":{"states":4,"heldout_units":72,"replicates":1},
      "authority":{"scientific_experiment":False,"single_case_s1":False,"provider_io":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"e3_confirmation":False,"paper_promotion":False,"submission":False},
      "design":{"path":str(a.design.relative_to(ROOT)),"sha256":sha(a.design)},"selector_freeze":{"path":str(a.selector_freeze.relative_to(ROOT)),"sha256":sha(a.selector_freeze)},"parent_v2":{"path":str(a.parent.relative_to(ROOT)),"sha256":sha(a.parent),"scientific_status":"HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"},
      "pool_bindings":bindings,"heldout_task_ids":list(map(str,parent["heldout"]["task_ids"])),"e3_untouched_assets_consumed":False,
      "suite":parent["suite"],"e1_a_pool_root":parent["e1_a_pool_root"],"mindmemos":parent["mindmemos"],"initial_skill":parent["initial_skill"],"model_identity":parent["model_identity"],"updater_runtime":parent["updater_runtime"],"actor_runtime":parent["actor_runtime"],"updater":parent["updater"],"actor":parent["actor"],"renderer":{"final_block_cap_tokens":3072,"tokenizer_encoding":"cl100k_base","tokenizer_version":"0.11.0","four_way_exact_retokenized_parity_required":True,"contrast_source_allocation":"50/50","padding":False},"budget":{"max_provider_calls_per_unit":11,"max_provider_calls_per_state":191},"env_file":parent["env_file"],"bound_code":bound,
      "run_root":"/data/wyt/e2-r17-search-projection/runs/single-case-diagnostic-witness-s1-20260902","lineage_lease_path":"/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-single-case-diagnostic-witness-s1-v1.json","exactly_once":{"authorized_runs":1,"automatic_retry":False,"completed_unit_replay":False,"replacement_sampling":False},
      "outcome_embargo":{"before_4_states_72_heldout":True,"partial_effect_read":False,"analyzer_authorized":False},"git_commit_at_freeze":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    }
    atomic(a.output,payload); print(json.dumps({"status":payload["status"],"output":str(a.output),"sha256":sha(a.output),"states":4,"heldout":72},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
