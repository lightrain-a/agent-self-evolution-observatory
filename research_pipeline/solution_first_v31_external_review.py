from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v31 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v31, write_idea_discovery_v31
from .solution_first_external_review import build_prompt, prepare_batches


def load_bank(path:Path=DEFAULT_JSON)->dict[str,Any]:
    payload=json.loads(path.read_text(encoding="utf-8")) if path.exists() else build_idea_discovery_v31()
    return {"shortlist":payload.get("children",[])}


def read_store(path:Path=DEFAULT_EXTERNAL_JSON)->dict[str,Any]:
    if path.exists():
        payload=json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and isinstance(payload.get("reviews"),dict): return payload
    return {"schema_version":"1.0","pipeline":"code-oracle -> signed-in ChatGPT web UI -> Agent project","required_host":EXPECTED_HOST,"reviews":{},"status":{"reviewed":0,"pending":6,"complete":False,"failed_batches":0}}


def run_batches(bank:dict[str,Any],manifest:dict[str,Any],*,store_path:Path,timeout:int,max_attempts:int=3)->dict[str,Any]:
    host=socket.gethostname(); ids=[idea["id"] for idea in bank["shortlist"]]
    if host!=EXPECTED_HOST:
        store=update_store(read_store(store_path),{},all_ids=ids,attempt_result="blocked_wrong_host",attempt_host=host);_atomic_json(store_path,store);raise RuntimeError(f"external review requires {EXPECTED_HOST}; current host is {host}")
    runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py";store=read_store(store_path)
    for batch in manifest.get("batches",[]):
        prompt_path=Path(batch["prompt"]);response_path=Path(batch["response"]);last_error=""
        for attempt in range(1,max_attempts+1):
            response_path.unlink(missing_ok=True)
            command=[sys.executable,str(runner),"Review the attached reviewer-repaired solution-first ICLR idea batch. Return only the required JSON object.","--file",str(prompt_path),"--slug",f"solution-first-v31-{batch['index']:02d}-attempt-{attempt}","--timeout",str(timeout),"--output",str(response_path)]
            completed=subprocess.run(command,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if completed.returncode!=0: raise RuntimeError(completed.stderr[-3000:] or completed.stdout[-3000:] or "Oracle failed")
                payload=extract_json(response_path.read_text(encoding="utf-8"));reviews=normalize_response(payload,batch["idea_ids"],source_artifact=str(response_path))
                store=update_store(store,reviews,all_ids=ids,attempt_result=f"batch_{batch['index']}_completed",attempt_host=host);_atomic_json(store_path,store);write_idea_discovery_v31();break
            except Exception as error:
                last_error=str(error)
                if attempt<max_attempts: time.sleep(45*attempt)
        else:
            status=store.setdefault("status",{});status["failed_batches"]=int(status.get("failed_batches",0))+1
            store=update_store(store,{},all_ids=ids,attempt_result=f"batch_{batch['index']}_failed",attempt_host=host);_atomic_json(store_path,store);raise RuntimeError(last_error or f"batch {batch['index']} failed")
    return store


def main(argv:Sequence[str]|None=None)->int:
    parser=argparse.ArgumentParser();parser.add_argument("--run",action="store_true");parser.add_argument("--batch-size",type=int,default=3);parser.add_argument("--timeout",type=int,default=900);parser.add_argument("--output-dir",type=Path);args=parser.parse_args(argv)
    settings=StorageSettings.from_env();settings.ensure();bank=load_bank();output=args.output_dir or settings.run_dir/"reviews"/"solution-first-v31-web-gpt";store=read_store()
    manifest=prepare_batches(bank,output,batch_size=args.batch_size,include_reviewed=False,review_store=store)
    if args.run: print(json.dumps(run_batches(bank,manifest,store_path=DEFAULT_EXTERNAL_JSON,timeout=args.timeout).get("status",{}),ensure_ascii=False))
    else: print(json.dumps({"output_dir":str(output),"queued":manifest["queued_ideas"],"batches":len(manifest["batches"])},ensure_ascii=False))
    return 0


if __name__=="__main__": raise SystemExit(main())
