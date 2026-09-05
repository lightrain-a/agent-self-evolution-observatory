#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def req(c: bool, m: str) -> None:
    if not c: raise RuntimeError(m)

def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def bound(raw: str) -> Path:
    p=Path(raw); return p if p.is_absolute() else ROOT/p

def choose_four(stream_id: str, mixed: list[str]) -> list[str]:
    req(len(mixed)>=4,f"insufficient mixed pools: {stream_id}")
    return sorted(mixed,key=lambda t:hashlib.sha256(f"semantic-transfer-mrw4-v3|{stream_id}|{t}".encode()).hexdigest())[:4]

def choose_ten(scores: dict[str,float], *, descending: bool, salt: str) -> list[str]:
    req(len(scores)==20,"router stream universe drift")
    def key(s: str):
        primary=-scores[s] if descending else scores[s]
        return primary,hashlib.sha256(f"{salt}|{s}".encode()).hexdigest()
    return sorted(scores,key=key)[:10]

def failed_witness(rows: list[dict[str,Any]], winner: int) -> dict[str,Any]:
    xs=[r for r in rows if float(r["score"])==0.0 and int(r["rollout_index"])!=winner]
    req(bool(xs),"mixed pool lacks failed nonwinner")
    r=min(xs,key=lambda x:int(x["rollout_index"]))
    return {"rollout_index":int(r["rollout_index"]),"trajectory_path":str(r["trajectory_path"]),"trajectory_sha256":str(r["trajectory_sha256"]),"score":0.0,"selector":"lowest original rollout index among verifier-failure nonwinner trajectories"}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--authorization",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); req(not a.output.exists(),"R3 support adjudication already exists")
    c,auth,s=load(a.contract),load(a.authorization),load(a.summary)
    csha,asha=sha(a.contract),sha(a.authorization)
    req(c["status"]==CONTRACT_STATUS and auth["status"]==AUTH_STATUS,"R3 contract/auth status invalid")
    req(auth["contract_sha256"]==csha,"R3 auth contract drift")
    req(s["status"]==SUMMARY_STATUS and s["contract_sha256"]==csha and s["authorization_sha256"]==asha,"R3 terminal summary binding drift")
    req(s["planned_tasks"]==160 and s["provider_executable_tasks"]==158 and s["sealed_k8_pools"]==158,"R3 terminal accounting drift")
    req(s["terminal_technical_missing"]==1 and s["matched_no_provider_censor"]==1,"R3 exception accounting drift")
    req(s["support_inspected"] is False and s["updater_calls"]==0 and s["heldout_evaluations"]==0,"R3 crossed support/learning boundary")

    om=c["recovery_opportunity_manifest"]; opath=bound(om["path"])
    req(opath.is_file() and sha(opath)==om["sha256"],"R3 opportunity manifest drift")
    o=load(opath); stream_ids=[str(x) for x in o["ordered_stream_ids"]]
    streams={str(k):[str(x) for x in v] for k,v in o["support_eligible_task_ids_by_stream"].items()}
    req(list(streams)==stream_ids and len(stream_ids)==20,"R3 support stream order drift")
    req(len(streams["stv3-cgwb-00"])==len(streams["stv3-cgwp-00"])==7,"R3 matched 7/7 geometry drift")
    req(BURNED not in sum(streams.values(),[]) and CENSOR not in sum(streams.values(),[]),"excluded task leaked into R3 support")

    run=Path(c["run_root"])
    mixed_by:dict[str,int]={}; mixed_tasks:dict[str,list[str]]={}; success_by:dict[str,int]={}; pool_sha={}; witness={}; opp={}
    for sid,tids in streams.items():
        expected=7 if sid in {"stv3-cgwb-00","stv3-cgwp-00"} else 8
        req(len(tids)==expected,f"R3 support opportunity drift: {sid}"); opp[sid]=expected
        mx=[]; succ=0
        for tid in tids:
            pp=run/"cases"/tid/"pool_k8.json"; req(pp.is_file(),f"missing R3 K8 pool: {tid}")
            p=load(pp); req(p["task_id"]==tid and int(p["k"])==8,f"R3 pool identity/K drift: {tid}")
            rows=p.get("trajectories") or []; req(len(rows)==8,f"R3 trajectory count drift: {tid}")
            scores=[]; seen=set()
            for r in rows:
                i=int(r["rollout_index"]); req(i not in seen,f"duplicate rollout index: {tid}/{i}"); seen.add(i)
                tp=Path(r["trajectory_path"]); req(tp.is_file() and sha(tp)==r["trajectory_sha256"],f"trajectory SHA drift: {tid}/{i}")
                sc=float(r["score"]); req(sc in (0.0,1.0),f"nonbinary Stage-A score: {tid}/{i}"); scores.append(sc)
            req(seen==set(range(8)),f"R3 rollout indices drift: {tid}")
            win=min(rows,key=lambda r:(-float(r["score"]),int(r["rollout_index"]))); wi=int(win["rollout_index"])
            req(int(p["acting_winner_index"])==wi,f"R3 winner selector drift: {tid}")
            if min(scores)<1.0 and max(scores)>=1.0:
                mx.append(tid); witness[tid]=failed_witness(rows,wi)
            succ += int(sum(scores)); pool_sha[tid]=sha(pp)
        mixed_by[sid]=len(mx); mixed_tasks[sid]=sorted(mx); success_by[sid]=succ

    required=int(c["equal_dose_support"]["required_mixed_pools_per_stream"]); req(required==4,"R3 support threshold drift")
    failing=sorted(sid for sid in stream_ids if mixed_by[sid]<required); passed=not failing
    treated_by={}; rows=[]
    if passed:
        for sid in stream_ids:
            selected=choose_four(sid,mixed_tasks[sid]); treated_by[sid]=selected
            for tid in selected:
                rows.append({"stream_id":sid,"task_id":tid,"pool_k8_path":str(run/"cases"/tid/"pool_k8.json"),"pool_k8_sha256":pool_sha[tid],"failed_witness":witness[tid],"selection_key_sha256":hashlib.sha256(f"semantic-transfer-mrw4-v3|{sid}|{tid}".encode()).hexdigest()})
        req(len(rows)==80,"R3 treated pool total must be 80")

    # Secondary pre-learning reduction routers use opportunity-normalized rates,
    # because two prospectively matched streams have 7 rather than 8 pools.
    reduction={}
    if passed:
        difficulty={sid:success_by[sid]/float(8*opp[sid]) for sid in stream_ids}
        mixedness={sid:mixed_by[sid]/float(opp[sid]) for sid in stream_ids}
        d=choose_ten(difficulty,descending=False,salt="semantic-transfer-difficulty-v3-r3-rate")
        m=choose_ten(mixedness,descending=True,salt="semantic-transfer-mixedness-v3-r3-rate")
        reduction={
            "difficulty_only":{"score":"successful rollout rate over Stage-B-eligible Stage-A opportunities","mrw4_streams":d,"win_c_streams":[x for x in stream_ids if x not in set(d)],"success_rate_per_stream":difficulty},
            "mixedness_only":{"score":"mixed-pool rate over Stage-B-eligible Stage-A opportunities","mrw4_streams":m,"win_c_streams":[x for x in stream_ids if x not in set(m)],"mixed_rate_per_stream":mixedness},
            "opportunity_normalized_before_outcome":True,"extra_provider_calls":0,"extra_heldout_evaluations":0
        }

    split=load(Path(c["suite"]["root"])/"r17_split_manifest.json"); heldout=[str(x) for x in split["e1_common_heldout_probe"]]
    req(not [x for x in heldout if (run/"cases"/x).exists()],"R3 Stage A touched heldout")
    req(not (run/"cases"/BURNED).exists() and not (run/"cases"/CENSOR).exists(),"R3 excluded task case exists")
    status="PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN" if passed else "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT"
    out={
        "schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-matched-censor-equal-dose-adjudication","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,
        "contract_path":str(a.contract),"contract_sha256":csha,"authorization_path":str(a.authorization),"authorization_sha256":asha,"summary_path":str(a.summary),"summary_sha256":sha(a.summary),
        "integrity":{"planned_tasks":160,"sealed_k8_pools":158,"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"provider_executable_tasks":158,"heldout_tasks_touched":0,"updater_calls":0,"heldout_evaluations":0,"partial_effect_read":False},
        "support":{"required_mixed_pools_per_stream":4,"eligible_opportunities_per_stream":opp,"mixed_pools_per_stream":mixed_by,"failing_streams":failing,"pass":passed},
        "stage_b_eligible_pool_geometry":{"task_ids_by_stream":streams,"opportunity_count_by_stream":opp,"affected_exact_matched_streams":["stv3-cgwb-00","stv3-cgwp-00"],"within_stream_arm_pool_ids_must_be_identical":True},
        "equal_dose_treatment_manifest":{"candidate_domain":"mixed K8 pools within the prospectively frozen Stage-B-eligible opportunity set","treated_pools_per_stream":4 if passed else 0,"treated_pool_total":len(rows),"treated_task_ids_by_stream":treated_by,"rows":rows,"scientific_inclusion":passed},
        "stage_a_reduction_routers":reduction,
        "authority":{"prepare_stage_b_contract":passed,"execute_stage_b":False,"heldout_evaluation":False,"analyzer":False,"paper_promotion":False},
        "next_gate":"SEPARATE_R3_STAGE_B_CONTRACT_AND_PREEXECUTION_REVIEW" if passed else "CLOSE_R3_RECOVERY_SUPPORT_HOLD"
    }
    atomic(a.output,out); print(json.dumps({"status":status,"support":out["support"],"treated_pool_total":len(rows),"next_gate":out["next_gate"]},ensure_ascii=False,indent=2,sort_keys=True)); return 0 if passed else 3

if __name__=="__main__": raise SystemExit(main())
