#!/usr/bin/env python3
"""Resolve and freeze exact source/future SWE-bench image manifests for PACTA-MSR."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes,atomic_json,sha256_file
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import (
    ACCEPT_INDEX,ACCEPT_MANIFEST,CACHE,get_raw,image_ref,image_repo,unique_amd64
)
import requests

ROOT=Path(__file__).resolve().parents[1]
POOL=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json'
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-images-20260902-v1')


def image_units()->list[dict[str,str]]:
    p=json.loads(POOL.read_text());rows=[]
    for u in p['units']:
        rows.append({'role':'source','unit_id':u['unit_id'],'instance_id':u['source_task_id'],'base_commit':u['source_base_commit']})
        rows.append({'role':'future','unit_id':u['unit_id'],'instance_id':u['future_task_id'],'base_commit':u['future_base_commit']})
    if len(rows)!=20 or len({x['instance_id'] for x in rows})!=20:raise RuntimeError('image-unit geometry')
    return rows

def resolve_one(root:Path,pass_no:int,row:dict[str,str])->dict[str,Any]:
    instance=row['instance_id'];repo=image_repo(instance);session=requests.Session();retry=root/'transport-retries.jsonl'
    raw_i,h_i=get_raw(repo,'latest',ACCEPT_INDEX,session,retry);ip=root/'raw-manifests'/f'pass{pass_no}'/f'{instance}__index.json';isha=atomic_bytes(ip,raw_i) if not ip.exists() else sha256_file(ip)
    if ip.read_bytes()!=raw_i:raise RuntimeError(f'index bytes drift {instance} pass{pass_no}')
    if h_i.get('docker-content-digest','')!=f'sha256:{isha}':raise RuntimeError(f'index digest header mismatch {instance}')
    idx=json.loads(raw_i);child=unique_amd64(idx);digest=child['digest']
    raw_m,h_m=get_raw(repo,digest,ACCEPT_MANIFEST,session,retry);mp=root/'raw-manifests'/f'pass{pass_no}'/f'{instance}__amd64.json';msha=atomic_bytes(mp,raw_m) if not mp.exists() else sha256_file(mp)
    if mp.read_bytes()!=raw_m:raise RuntimeError(f'manifest bytes drift {instance} pass{pass_no}')
    if digest!=f'sha256:{msha}' or h_m.get('docker-content-digest','')!=digest:raise RuntimeError(f'child digest mismatch {instance}')
    return {**row,'pass':pass_no,'repository':repo,'image_reference':image_ref(instance),'index_sha256':isha,'amd64_sha256':msha,'index_path':str(ip),'amd64_path':str(mp)}

def freeze_from_rows(root:Path,base:list[dict[str,str]],rows:list[dict[str,Any]],*,recovery_mode:str)->dict[str,Any]:
    by={}
    for r in rows:by.setdefault(r['instance_id'],[]).append(r)
    stable=all(len(v)==2 and v[0]['index_sha256']==v[1]['index_sha256'] and v[0]['amd64_sha256']==v[1]['amd64_sha256'] for v in by.values())
    if not stable:raise RuntimeError('STOP_MSR_IMAGE_TAG_DRIFT')
    frozen=[];blobs={}
    for x in base:
        v=sorted(by[x['instance_id']],key=lambda z:z['pass'])[-1];manifest=json.loads(Path(v['amd64_path']).read_text());descriptors=[manifest['config'],*manifest['layers']]
        for d in descriptors:
            rec=blobs.setdefault(d['digest'],{'digest':d['digest'],'size':int(d['size']),'repositories':[]})
            if rec['size']!=int(d['size']):raise RuntimeError('shared blob size mismatch')
            rec['repositories'].append(v['repository'])
        frozen.append({**x,'image_reference':v['image_reference'],'repository':v['repository'],'index_digest':'sha256:'+v['index_sha256'],'amd64_digest':'sha256:'+v['amd64_sha256'],'config_digest':manifest['config']['digest'],'layer_count':len(manifest['layers']),'manifest_path':v['amd64_path']})
    b_rows=[]
    for d,rec in sorted(blobs.items()):
        p=CACHE/d[7:];ok=p.is_file() and p.stat().st_size==rec['size'] and sha256_file(p)==d[7:]
        b_rows.append({**rec,'cache_path':str(p),'reusable':ok})
    freeze={'schema_version':1,'status':'MSR_20_IMAGE_MANIFESTS_FROZEN','fresh_pool_sha256':sha256_file(POOL),'stable_twice':True,'image_count':20,'rows':frozen,'provider_calls':0,'scientific_calls':0,'recovery_mode':recovery_mode}
    plan={'schema_version':1,'status':'MSR_BLOB_PLAN_FROZEN','unique_blob_count':len(b_rows),'unique_blob_bytes':sum(x['size'] for x in b_rows),'reusable_blob_count':sum(x['reusable'] for x in b_rows),'reusable_blob_bytes':sum(x['size'] for x in b_rows if x['reusable']),'missing_blob_count':sum(not x['reusable'] for x in b_rows),'missing_blob_bytes':sum(x['size'] for x in b_rows if not x['reusable']),'rows':b_rows,'provider_calls':0,'scientific_calls':0,'recovery_mode':recovery_mode}
    atomic_json(root/'manifest-freeze.json',freeze);atomic_json(root/'blob-plan.json',plan)
    return {'status':freeze['status'],'image_count':20,'unique_blobs':plan['unique_blob_count'],'reusable_bytes':plan['reusable_blob_bytes'],'missing_bytes':plan['missing_blob_bytes'],'recovery_mode':recovery_mode}

def checkpoint_rows(root:Path)->list[dict[str,Any]]:
    base=image_units();rows=[]
    expected={x['instance_id']:x for x in base}
    for pass_no in (1,2):
        directory=root/'raw-manifests'/f'pass{pass_no}'
        if not directory.is_dir():raise RuntimeError(f'missing checkpoint pass{pass_no}')
        files=list(directory.glob('*.json'))
        if len(files)!=40:raise RuntimeError(f'checkpoint pass{pass_no} expected 40 raw files, got {len(files)}')
        for x in base:
            instance=x['instance_id'];ip=directory/f'{instance}__index.json';mp=directory/f'{instance}__amd64.json'
            if not ip.is_file() or not mp.is_file():raise RuntimeError(f'missing checkpoint manifest {instance} pass{pass_no}')
            isha=sha256_file(ip);msha=sha256_file(mp);idx=json.loads(ip.read_text());child=unique_amd64(idx)
            if child.get('digest')!=f'sha256:{msha}':raise RuntimeError(f'checkpoint child binding mismatch {instance} pass{pass_no}')
            manifest=json.loads(mp.read_text())
            if not isinstance(manifest.get('config'),dict) or not isinstance(manifest.get('layers'),list):raise RuntimeError(f'invalid checkpoint child manifest {instance} pass{pass_no}')
            rows.append({**expected[instance],'pass':pass_no,'repository':image_repo(instance),'image_reference':image_ref(instance),'index_sha256':isha,'amd64_sha256':msha,'index_path':str(ip),'amd64_path':str(mp)})
    return rows

def finalize_existing(root:Path)->dict[str,Any]:
    if not root.is_dir():raise RuntimeError('checkpoint root absent')
    if (root/'manifest-freeze.json').exists() or (root/'blob-plan.json').exists():raise RuntimeError('checkpoint already finalized; no overwrite')
    return freeze_from_rows(root,image_units(),checkpoint_rows(root),recovery_mode='checkpoint_finalize_after_transport_disconnect')

def resolve(root:Path)->dict[str,Any]:
    if root.exists():raise RuntimeError('image root exists; no overwrite')
    root.mkdir(parents=True);base=image_units();rows=[]
    for pass_no in (1,2):
        for row in base:
            out=resolve_one(root,pass_no,row);rows.append(out);print(json.dumps({'pass':pass_no,'role':out['role'],'instance':out['instance_id'],'amd64':out['amd64_sha256']}),flush=True)
    return freeze_from_rows(root,base,rows,recovery_mode='live_double_resolution')

def main()->None:
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT);a.add_argument('--phase',choices=('resolve','finalize-existing'),default='resolve');args=a.parse_args()
    result=resolve(args.root) if args.phase=='resolve' else finalize_existing(args.root)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
