from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-a5-history-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-a5-history-cpu.js"
SURFACES=("prompt","memory","workflow")
KEYS=("schema","retry","verify","ordering","tool","memory","budget","guard")
QUERIES=(3,6,9,12,15,18,22,26,30,34,37,39)


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _updates()->list[dict[str,Any]]:
    rows=[]
    for i in range(40):
        k1=KEYS[(3*i+1)%len(KEYS)]; k2=KEYS[(5*i+2)%len(KEYS)] if i%5==0 else None
        changes={k1:(i%7)-3}
        if k2 and k2!=k1: changes[k2]=((2*i)%5)-2
        rows.append({"update_id":f"u{i:02d}","surface":SURFACES[i%3],"changes":changes})
    return rows


def _states(updates:list[dict[str,Any]])->list[dict[str,int]]:
    state={k:0 for k in KEYS}; out=[]
    for row in updates:
        for key,delta in row["changes"].items(): state[key]+=delta
        out.append(dict(state))
    return out


def _diff(a:dict[str,int],b:dict[str,int])->dict[str,int]:
    return {k:b[k]-a[k] for k in KEYS if b[k]!=a[k]}


def _apply(state:dict[str,int],delta:dict[str,int])->dict[str,int]:
    out=dict(state)
    for k,v in delta.items(): out[k]+=v
    return out


def _semantic_compactor(updates:list[dict[str,Any]],states:list[dict[str,int]])->dict[str,Any]:
    # Frozen-query semantic segments: retain typed provenance plus the net effect per segment.
    base={k:0 for k in KEYS}; prev=-1; segments=[]
    for q in QUERIES:
        before=base if prev<0 else states[prev]; after=states[q]
        typed={s:[] for s in SURFACES}
        for row in updates[prev+1:q+1]: typed[row["surface"]].append(row["update_id"])
        delta=_diff(before,after); segments.append({"to":q,"delta":delta,"typed_provenance":typed}); prev=q
    storage=sum(len(x["delta"])+sum(bool(ids) for ids in x["typed_provenance"].values()) for x in segments)
    return {"segments":segments,"storage_cells":storage}


def _generic_diff(updates:list[dict[str,Any]],states:list[dict[str,int]])->dict[str,Any]:
    # Same frozen queries, but only generic state deltas; no update-surface semantics.
    base={k:0 for k in KEYS}; prev=-1; segments=[]
    for q in QUERIES:
        before=base if prev<0 else states[prev]; after=states[q]
        segments.append({"to":q,"delta":_diff(before,after)}); prev=q
    storage=sum(len(x["delta"]) for x in segments)
    return {"segments":segments,"storage_cells":storage}


def _rollback_eval(compacted:dict[str,Any],truth:list[dict[str,int]])->dict[str,Any]:
    state={k:0 for k in KEYS}; exact=0; replay_segments=[]; rows=[]
    for index,segment in enumerate(compacted["segments"],1):
        state=_apply(state,segment["delta"]); q=segment["to"]; ok=state==truth[q]; exact+=int(ok); replay_segments.append(index)
        rows.append({"query":q,"exact":ok,"replayed_segments_from_base":index})
    return {"queries":len(rows),"exact_queries":exact,"rollback_fidelity":exact/len(rows),"mean_segments_from_base":sum(replay_segments)/len(replay_segments),"max_segments_from_base":max(replay_segments),"rows":rows}


def _periodic(updates:list[dict[str,Any]],truth:list[dict[str,int]],storage_cap:int)->dict[str,Any]:
    # Full-state periodic checkpoints under the same scalar-cell storage cap.
    cells_per_checkpoint=len(KEYS); count=max(1,storage_cap//cells_per_checkpoint); spacing=max(1,len(updates)//count)
    points=sorted(set([min(len(updates)-1,(i+1)*spacing-1) for i in range(count)])); checkpoints={p:truth[p] for p in points}
    exact=0; replay=[]
    for q in QUERIES:
        prior=[p for p in points if p<=q]
        if prior: start=max(prior); state=dict(checkpoints[start]); begin=start+1
        else: state={k:0 for k in KEYS}; begin=0
        for row in updates[begin:q+1]:
            for key,delta in row["changes"].items(): state[key]+=delta
        exact+=int(state==truth[q]); replay.append(q-begin+1)
    return {"checkpoint_points":points,"storage_cells":len(points)*cells_per_checkpoint,"rollback_fidelity":exact/len(QUERIES),"mean_updates_replayed":sum(replay)/len(replay),"max_updates_replayed":max(replay)}


def run_a5_cpu_p0()->dict[str,Any]:
    updates=_updates(); truth=_states(updates); semantic=_semantic_compactor(updates,truth); generic=_generic_diff(updates,truth)
    seval=_rollback_eval(semantic,truth); geval=_rollback_eval(generic,truth); periodic=_periodic(updates,truth,semantic["storage_cells"])
    generic_dominates=(geval["rollback_fidelity"]>=seval["rollback_fidelity"] and generic["storage_cells"]<=semantic["storage_cells"] and geval["mean_segments_from_base"]<=seval["mean_segments_from_base"])
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"lineage-aware-rollback","code":"A-5",
      "scientific_role":"CPU rollback-equivalence P0 on a 40-update typed stream with 12 frozen rollback queries",
      "design":{"updates":len(updates),"surfaces":list(SURFACES),"state_keys":len(KEYS),"rollback_queries":list(QUERIES),"independent_truth":"exact full-history state replay"},
      "semantic_compactor":{"storage_cells":semantic["storage_cells"],"evaluation":seval},"generic_state_diff":{"storage_cells":generic["storage_cells"],"evaluation":geval},"periodic_checkpoint":periodic,
      "matched_simplification":{"baseline":"query-matched generic state-diff compaction with no Prompt/Memory/Workflow semantics","dominates_or_ties":generic_dominates,"storage_saving_cells":semantic["storage_cells"]-generic["storage_cells"]},
      "decision":"STOP_MATCHED_GENERIC_STATE_DIFF_DOMINATES" if generic_dominates else "P0_SIGNAL_CONTINUE",
      "standalone_claim_stop_authorized":generic_dominates,"p1_authorized":False,
      "next_action":"Merge A-5 into generic version/history infrastructure; do not spend GPU on a standalone semantic-compaction method." if generic_dominates else "Validate semantic compaction on a real 30–50 update stream only after human review."}


def write_a5_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_a5_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_A5_HISTORY_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_a5_cpu_p0(),ensure_ascii=False,indent=2))
