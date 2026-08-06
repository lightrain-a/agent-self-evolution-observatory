from __future__ import annotations

import argparse
import json
import math
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v3 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v3, write_idea_discovery_v3

REVIEWER = "agent-project-web-gpt-solution-first-iclr-area-chair"


def load_bank(path: Path = DEFAULT_JSON) -> dict[str,Any]:
    if path.exists():
        payload=json.loads(path.read_text(encoding="utf-8"))
    else:
        payload=build_idea_discovery_v3()
    if not isinstance(payload.get("shortlist"),list):
        raise ValueError(f"{path} has no shortlist")
    return payload


def packet(idea: dict[str,Any]) -> dict[str,Any]:
    return {
        "idea_id":idea["id"],
        "parent_id":idea.get("parent_id"),
        "title":idea.get("title",{}).get("en",""),
        "inherited_problem":idea.get("problem",{}).get("en",""),
        "changed_assumption":idea.get("changed_assumption",{}).get("en",""),
        "exact_mechanism":idea.get("exact_mechanism",{}).get("en",""),
        "update_surface":idea.get("update_surface",""),
        "learning_signal":idea.get("learning_signal",{}).get("en",""),
        "independent_ground_truth":idea.get("independent_ground_truth",{}).get("en",""),
        "strongest_baseline":idea.get("strongest_baseline",{}).get("en",""),
        "decisive_pilot":idea.get("decisive_pilot",{}).get("en",""),
        "stop_condition":idea.get("stop_condition",{}).get("en",""),
        "public_assets":idea.get("public_assets",[]),
        "generation_mechanisms":idea.get("generation_mechanisms",[]),
        "internal_scores":idea.get("scores",{}),
    }


def build_prompt(ideas: Sequence[dict[str,Any]], *, batch_index: int, batch_count: int) -> str:
    schema={
        "reviewer":REVIEWER,
        "review_date":"YYYY-MM-DD",
        "ideas":[{
            "idea_id":"exact supplied id",
            "verdict":"pass|revise|block",
            "confidence":"high|medium|low",
            "finding":"independent mechanism-level judgment in English",
            "finding_zh":"same judgment in simplified Chinese",
            "required_action":"one material action before advancing in English",
            "required_action_zh":"same concrete action in simplified Chinese",
            "direct_collision":{"status":"none|partial|direct|unknown","closest_work":[{"title":"exact title","venue_year":"venue/year or arXiv date","official_url":"official paper/project/code URL","overlap":"problem|mechanism|combination|experiment"}],"surviving_difference":"exact remaining boundary or empty when blocked"},
            "solution_quality":{"mechanism_specificity":"strong|conditional|weak","learning_signal_identifiable":"yes|partial|no","ground_truth_independent":"yes|partial|no","update_surface_exact":"yes|partial|no"},
            "iclr_fit":"strong|conditional|weak",
            "strongest_baseline":"baseline most likely to erase the claim",
            "decisive_pilot":"one normal-setting comparison under matched budgets",
            "stop_rule":"specific falsification condition",
            "unknowns":["facts not verifiable from official sources"],
        }],
    }
    return f"""# Independent solution-first ICLR audit — batch {batch_index}/{batch_count}

Act as a strict ICLR area chair and method-invention auditor. These are solution-first children created after earlier problem formulations received REVISE. Do not reward specificity by itself. Determine whether each child now supplies a genuinely new and identifiable learning mechanism rather than a renamed audit, benchmark, predictor, controller, or combination of known components.

Use web search and consult only official paper pages/PDFs, OpenReview/CVF/ACL/NeurIPS proceedings, official project pages, and author-maintained repositories. Check work available through 2026-08-01. Never infer a method from a title.

For every child independently verify:
1. The changed assumption materially differs from the parent.
2. The exact update surface, learning signal, loss/decision rule, and persistent state are identifiable.
3. Independent ground truth does not come from the same model or circular evaluator.
4. The decisive pilot separates the mechanism from extra inference, search, retrieval, or test budget.
5. The problem–mechanism pair, method combination, and decisive experiment do not directly collide with recent work.
6. The method can survive a held-out model/domain/order test after freezing.
7. Public assets make P0/P1 executable within a low-resource budget.

Verdicts:
- `pass`: a standalone ICLR method thesis survives; the mechanism is precise, independently testable, and not directly covered.
- `revise`: the problem is useful and the child is more concrete, but one assumption, learning rule, collision boundary, or decisive experiment must materially change.
- `block`: the child is still an audit/benchmark, a direct recombination of known methods, circularly supervised, or experimentally non-identifiable.

Return exactly one JSON object and no prose outside JSON. Review all {len(ideas)} supplied children and preserve every exact `idea_id`.

Required schema:
```json
{json.dumps(schema,ensure_ascii=False,indent=2)}
```

Solution-first children:
```json
{json.dumps([packet(idea) for idea in ideas],ensure_ascii=False,indent=2)}
```
"""


def read_store(path:Path=DEFAULT_EXTERNAL_JSON)->dict[str,Any]:
    if path.exists():
        payload=json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and isinstance(payload.get("reviews"),dict): return payload
    return {"schema_version":"1.0","pipeline":"code-oracle -> signed-in ChatGPT web UI -> Agent project","required_host":EXPECTED_HOST,"reviews":{},"status":{"reviewed":0,"pending":10,"complete":False,"failed_batches":0}}


def prepare_batches(bank:dict[str,Any],output_dir:Path,*,batch_size:int=5,include_reviewed:bool=False,review_store:dict[str,Any]|None=None)->dict[str,Any]:
    store=review_store or read_store(); completed=store.get("reviews",{})
    ideas=[idea for idea in bank["shortlist"] if include_reviewed or not completed.get(idea["id"])]
    output_dir.mkdir(parents=True,exist_ok=True)
    count=math.ceil(len(ideas)/batch_size) if ideas else 0; batches=[]
    for index in range(count):
        chunk=ideas[index*batch_size:(index+1)*batch_size]
        prompt_path=output_dir/f"batch-{index+1:02d}-of-{count:02d}.md"
        response_path=output_dir/f"batch-{index+1:02d}-of-{count:02d}.response.md"
        prompt_path.write_text(build_prompt(chunk,batch_index=index+1,batch_count=count),encoding="utf-8")
        batches.append({"index":index+1,"idea_ids":[idea["id"] for idea in chunk],"prompt":str(prompt_path),"response":str(response_path),"status":"prepared"})
    manifest={"schema_version":"1.0","total_shortlist":len(bank["shortlist"]),"queued_ideas":len(ideas),"batch_size":batch_size,"batches":batches}
    _atomic_json(output_dir/"manifest.json",manifest)
    return manifest


def run_batches(bank:dict[str,Any],manifest:dict[str,Any],*,store_path:Path,timeout:int,max_attempts:int=3)->dict[str,Any]:
    host=socket.gethostname(); ids=[idea["id"] for idea in bank["shortlist"]]
    if host!=EXPECTED_HOST:
        store=update_store(read_store(store_path),{},all_ids=ids,attempt_result="blocked_wrong_host",attempt_host=host);_atomic_json(store_path,store)
        raise RuntimeError(f"external review requires {EXPECTED_HOST}; current host is {host}")
    runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py";store=read_store(store_path)
    for batch in manifest.get("batches",[]):
        prompt_path=Path(batch["prompt"]);response_path=Path(batch["response"]);last_error=""
        for attempt in range(1,max_attempts+1):
            response_path.unlink(missing_ok=True)
            command=[sys.executable,str(runner),"Review the attached solution-first ICLR idea batch. Return only the required JSON object.","--file",str(prompt_path),"--slug",f"solution-first-v3-{batch['index']:02d}-attempt-{attempt}","--timeout",str(timeout),"--output",str(response_path)]
            completed=subprocess.run(command,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if completed.returncode!=0: raise RuntimeError(completed.stderr[-3000:] or completed.stdout[-3000:] or "Oracle failed")
                payload=extract_json(response_path.read_text(encoding="utf-8"))
                reviews=normalize_response(payload,batch["idea_ids"],source_artifact=str(response_path))
                store=update_store(store,reviews,all_ids=ids,attempt_result=f"batch_{batch['index']}_completed",attempt_host=host)
                _atomic_json(store_path,store);write_idea_discovery_v3();break
            except Exception as error:
                last_error=str(error)
                if attempt<max_attempts: time.sleep(45*attempt)
        else:
            status=store.setdefault("status",{});status["failed_batches"]=int(status.get("failed_batches",0))+1
            store=update_store(store,{},all_ids=ids,attempt_result=f"batch_{batch['index']}_failed",attempt_host=host);_atomic_json(store_path,store)
            raise RuntimeError(last_error or f"batch {batch['index']} failed")
    return store


def parse_args(argv:Sequence[str]|None=None)->argparse.Namespace:
    parser=argparse.ArgumentParser(description="Externally review solution-first v3 method children.")
    parser.add_argument("--run",action="store_true");parser.add_argument("--batch-size",type=int,default=5);parser.add_argument("--timeout",type=int,default=900);parser.add_argument("--output-dir",type=Path);parser.add_argument("--include-reviewed",action="store_true")
    return parser.parse_args(argv)


def main(argv:Sequence[str]|None=None)->int:
    args=parse_args(argv);settings=StorageSettings.from_env();settings.ensure();bank=load_bank()
    output_dir=args.output_dir or settings.run_dir/"reviews"/"solution-first-v3-web-gpt";store=read_store()
    manifest=prepare_batches(bank,output_dir,batch_size=args.batch_size,include_reviewed=args.include_reviewed,review_store=store)
    if args.run:
        result=run_batches(bank,manifest,store_path=DEFAULT_EXTERNAL_JSON,timeout=args.timeout);print(json.dumps(result.get("status",{}),ensure_ascii=False))
    else: print(json.dumps({"output_dir":str(output_dir),"queued":manifest["queued_ideas"],"batches":len(manifest["batches"])},ensure_ascii=False))
    return 0


if __name__=="__main__": raise SystemExit(main())
