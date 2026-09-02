from __future__ import annotations

import argparse, hashlib, json, sys, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.relational_topology_official_training_dev_v14a import COMPONENTS, preflight
from research_pipeline.relational_topology_official_training_dev_run_v14a import train


def code_sha() -> str:
    paths=[
        ROOT/"research_pipeline/relational_topology_official_training_dev_v14a.py",
        ROOT/"research_pipeline/relational_topology_official_training_dev_run_v14a.py",
        Path(__file__).resolve(),
    ]
    h=hashlib.sha256()
    for path in paths:
        h.update(path.relative_to(ROOT).as_posix().encode()+b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--phase",required=True,choices=["preflight","train"])
    p.add_argument("--component",required=True,choices=list(COMPONENTS))
    p.add_argument("--run-root",required=True,type=Path)
    p.add_argument("--authority",required=True,type=Path)
    p.add_argument("--proposal",required=True,type=Path)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--bedroom",required=True,type=Path)
    p.add_argument("--split",required=True,type=Path)
    p.add_argument("--corpus-dir",required=True,type=Path)
    p.add_argument("--clip",required=True,type=Path)
    p.add_argument("--fvq",required=True,type=Path)
    p.add_argument("--bounds",required=True,type=Path)
    p.add_argument("--device",type=int,default=0)
    p.add_argument("--resume",type=Path)
    a=p.parse_args()
    common=dict(component=a.component,run_root=a.run_root,authority=a.authority,proposal=a.proposal,source=a.source,bedroom=a.bedroom,split=a.split,corpus_dir=a.corpus_dir,clip=a.clip,fvq=a.fvq,bounds=a.bounds,device_index=a.device)
    try:
        if a.phase=="preflight":
            if a.resume is not None: raise ValueError("--resume is invalid for preflight")
            out=preflight(**common)
        else:
            out=train(**common,code_sha=code_sha(),resume=a.resume)
    except Exception as exc:
        print(json.dumps({"phase":a.phase,"component":a.component,"status":"FAIL_CLOSED","error_type":type(exc).__name__,"error":str(exc),"traceback":traceback.format_exc(),"scientific_outcomes":0},ensure_ascii=False),file=sys.stderr)
        raise
    print(json.dumps({"phase":a.phase,"component":a.component,"status":out["state"],"scientific_outcomes":out.get("scientific_outcomes",0),"code_sha":code_sha()},sort_keys=True))

if __name__=="__main__": main()
