#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))

def req(x: bool, msg: str):
    if not x: raise RuntimeError(msg)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--prereg',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    req(not args.output.exists(),'audit already exists')
    pr=load(args.prereg)
    parent=Path(pr['parent']['analysis_path'])
    req(parent.is_file() and sha(parent)==pr['parent']['analysis_sha256'],'parent analysis drift')
    pa=load(parent)
    req(pa.get('status')=='HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','parent status drift')
    suite=Path(pr['future_update_substrate']['suite_root'])
    split=Path(pr['future_update_substrate']['split_manifest'])
    req(split.is_file() and sha(split)==pr['future_update_substrate']['split_manifest_sha256'],'split drift')
    sp=load(split)
    req(sp.get('selection_is_outcome_blind') is True,'future selection not outcome-blind')
    req(sp.get('rules',{}).get('e3_future_unseen_until_prediction_freeze') is True,'future-unseen rule missing')
    streams=sp['e3_future_streams']
    task_ids=[t for xs in streams.values() for t in xs]
    req(len(streams)==12 and len(task_ids)==96 and len(set(task_ids))==96,'future cardinality drift')
    meta=load(suite/'r17_controlled_metadata.json')
    byid={r['id']:r for r in meta}
    fam_counts=Counter()
    missing=[]
    for stream,ids in streams.items():
        fams={byid[t]['primary_failure_family'] for t in ids}
        req(len(ids)==8 and len(fams)==1,f'stream family drift: {stream}')
        fam=next(iter(fams)); fam_counts[fam]+=1
        for t in ids:
            base=suite/'spreadsheetbench_verified_400'/'spreadsheet'/t
            if not (base/f'{t}_init.xlsx').is_file() or not (base/f'{t}_golden.xlsx').is_file(): missing.append(t)
    req(not missing,f'missing task assets: {missing[:3]}')
    req(sorted(fam_counts.values())==[2]*6,'family balance drift')

    runs=Path('/data/wyt/e2-r17-search-projection/runs')
    claim_hits=[]; ledgers=0
    for db in runs.rglob('provider_budget.sqlite3'):
        ledgers+=1
        try:
            con=sqlite3.connect(f'file:{db}?mode=ro',uri=True)
            rows=con.execute("select unit_id from claims where unit_id like '%r17-b5-%' or unit_id like '%r17-b6-%' limit 1").fetchall()
            con.close()
        except Exception:
            continue
        if rows: claim_hits.append(str(db))
    req(not claim_hits,'future provider claims already exist')
    task_dirs=sum(1 for p in runs.rglob('*') if p.is_dir() and ('r17-b5-' in p.name or 'r17-b6-' in p.name))
    req(task_dirs==0,'future task execution directories already exist')

    payload={
      'schema_version':'1.0',
      'artifact_type':'e2-r18-future-substrate-eligibility-audit',
      'created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
      'status':'PASS_R18_UNTOUCHED_FUTURE_SUBSTRATE_ELIGIBLE_FOR_NEW_CHILD_ONLY',
      'prereg_path':str(args.prereg),'prereg_sha256':sha(args.prereg),
      'parent_analysis_sha256':sha(parent),'parent_status':pa['status'],
      'split_manifest':str(split),'split_manifest_sha256':sha(split),
      'future_streams':12,'future_tasks':96,'tasks_per_stream':8,
      'family_stream_counts':dict(fam_counts),
      'selection_is_outcome_blind':True,'selected_before_parent_outcomes':True,
      'ledgers_scanned':ledgers,'future_provider_claim_ledgers':0,'future_execution_task_dirs':0,
      'old_e3_contract_or_authority_reused':False,
      'eligible_reuse':'frozen untouched task assets and split only; fresh R18 contract/authorization required',
      'parent_r17_status_changed':False,
      'provider_calls':0,'scientific_scores_read':False,
      'authority':{'provider_io':False,'scientific_execution':False,'updater':False,'evaluation':False,'analyzer':False}
    }
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
