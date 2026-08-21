from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_ablation import build_relevant_escape_ablation_plan
from .api_memory_search_smoke import _canonical, _sha_text, _usage, _validate_ideas, generation_prompt
from .api_memory_search_smoke_staged import _client, _load, _lock, _write, context
from .api_research_memory import compile_api_memory_query_pack, record_provider_failure, record_raw_api_output
from .ark_provider import extract_json_object

ARMS = ("relevant", "relevant_escape")
GENERATOR_MODEL = "kimi-k3"
MAX_ITEMS = 4
MAX_ITEM_CHARS = 600
MAX_CHARS = 2406


def prepare(*, root: Path, study: Path, prefix: str) -> dict[str, Any]:
    output=study/"state-prepared.json"; lock=_lock(output,{"stage":"prepare","prefix":prefix})
    try:
        ctx=context();plan=build_relevant_escape_ablation_plan(context=ctx,run_id_prefix=prefix,stage="memory-escape-smoke",max_items=MAX_ITEMS,max_item_chars=MAX_ITEM_CHARS,root=root)
        if plan["status"]!="RELEVANT_ESCAPE_ABLATION_READY": raise RuntimeError(str(plan["invariants"]))
        packs={}
        for arm in ARMS:
            pack=compile_api_memory_query_pack(purpose="IDEA_DISCOVERY",context=ctx,run_id=f"{prefix}-{arm}",stage="memory-escape-smoke",variant=arm,max_items=MAX_ITEMS,max_chars=MAX_CHARS,max_item_chars=MAX_ITEM_CHARS,required=True,record_query=True,root=root)
            expected=plan["arms"][arm]
            if pack.get("selected_memory_ids")!=expected.get("selected_memory_ids") or pack.get("selected_scientific_signatures")!=expected.get("selected_scientific_signatures"): raise RuntimeError(f"pack drift:{arm}")
            if int((pack.get("summary") or {}).get("characters") or 0)!=MAX_CHARS: raise RuntimeError(f"memory character mismatch:{arm}")
            packs[arm]=pack
        if packs["relevant"]["selected_object_keys"]!=packs["relevant_escape"]["selected_object_keys"]: raise RuntimeError("escape treatment changed selected objects")
        state={"schema_version":"2.4","status":"PREPARED","prefix":prefix,"context":ctx,"plan":plan,"packs":packs,"scientific_authority":False,"belief_authority":False};state["state_sha256"]=_sha_text(_canonical(state));_write(output,state);return state
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def generate_arm(*, root: Path, study: Path, arm: str) -> dict[str, Any]:
    if arm not in ARMS: raise ValueError(arm)
    prep=_load(study/"state-prepared.json");prefix=str(prep["prefix"]);output=study/f"generation-{arm}.json";lock=_lock(output,{"stage":"generate","arm":arm,"prefix":prefix})
    try:
        pack=prep["packs"][arm];prompt=generation_prompt(prep["context"],pack);run_root=root/"runs"/f"{prefix}-{arm}";run_root.mkdir(parents=True,exist_ok=True)
        try: response=_client().respond(prompt,model=GENERATOR_MODEL,max_output_tokens=6000,temperature=0.0,thinking="disabled",store=True)
        except Exception as error:
            psha=_sha_text(prompt);fp=_sha_text(_canonical({"stage":"memory-escape-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":psha,"error_type":type(error).__name__,"error":str(error)[:500]}));receipt=record_provider_failure(run_root=run_root,stage="memory-escape-smoke",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":GENERATOR_MODEL,"error_fingerprint":fp,"prompt_sha256":psha},root=root);failed={"schema_version":"1.0","status":"PROVIDER_FAILURE","arm":arm,"error_type":type(error).__name__,"error":str(error)[:1200],"provider_failure":receipt,"scientific_authority":False,"belief_authority":False};_write(output,failed);return failed
        raw=str(response.get("text") or "");raw_file=run_root/"raw-generation.txt";raw_file.write_text(raw,encoding="utf-8");psha=_sha_text(prompt);fp=_sha_text(_canonical({"stage":"memory-escape-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":psha,"pack_sha256":pack["query_pack_sha256"]}));arch=record_raw_api_output(run_root=run_root,stage="memory-escape-smoke",raw_path=raw_file,requested_model=GENERATOR_MODEL,resolved_model=str(response.get("resolved_model") or GENERATOR_MODEL),request_fingerprint=fp,prompt_sha256=psha,root=root);ideas=_validate_ideas(extract_json_object(raw))
        result={"schema_version":"2.4","status":"GENERATION_COMPLETE_UNCOMMITTED","arm":arm,"run_id":f"{prefix}-{arm}","raw_sha256":arch["raw_sha256"],"prompt_sha256":psha,"resolved_model":str(response.get("resolved_model") or ""),"usage":_usage(response),"query_pack_sha256":pack["query_pack_sha256"],"selected_memory_ids":pack["selected_memory_ids"],"selected_memory_roles":pack.get("selected_memory_roles") or [],"ideas":ideas,"scientific_authority":False,"belief_authority":False};result["stage_sha256"]=_sha_text(_canonical(result));_write(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def prepare_review(*, root: Path, study: Path) -> dict[str, Any]:
    prep=_load(study/"state-prepared.json");prefix=str(prep["prefix"]);output=study/"review-prepared.json";lock=_lock(output,{"stage":"prepare-review","prefix":prefix})
    try:
        rows=[]
        for arm in ARMS:
            gen=_load(study/f"generation-{arm}.json")
            if gen.get("status")!="GENERATION_COMPLETE_UNCOMMITTED": raise RuntimeError(f"arm not complete:{arm}")
            for idea in gen["ideas"]:
                seed=_sha_text(f"memory-escape-smoke-v24:{arm}:{idea['id']}:{idea['scientific_object']}");rows.append({"blind_id":"B"+seed[:12],**{k:v for k,v in idea.items() if k!="id"},"_arm":arm,"_idea_id":idea["id"]})
        ordered=sorted(rows,key=lambda r:_sha_text("blind-order-v24:"+r["blind_id"]));public=[{k:v for k,v in r.items() if not k.startswith("_")} for r in ordered]
        review_context={"generated_ideas":public,"purpose":"hard blind history review for relevant escape framing smoke"};run_id=f"{prefix}-hard-review"
        history=compile_api_memory_query_pack(purpose="SEMANTIC_REVIEW",context=review_context,run_id=run_id,stage="memory-escape-hard-review",variant="relevant",max_items=24,max_chars=18000,required=True,record_query=True,root=root)
        result={"schema_version":"2.4","status":"REVIEW_PREPARED","hard_review_run_id":run_id,"history_pack":history,"blinded":public,"mapping":[{"blind_id":r["blind_id"],"arm":r["_arm"],"idea_id":r["_idea_id"]} for r in ordered],"scientific_authority":False,"belief_authority":False};result["stage_sha256"]=_sha_text(_canonical(result));_write(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def main()->None:
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    for cmd in ("prepare","prepare-review"):
        x=s.add_parser(cmd);x.add_argument("--persistent-root",type=Path,required=True);x.add_argument("--study",type=Path,required=True);x.add_argument("--prefix",default="api-memory-escape-smoke-v24-r1")
    x=s.add_parser("generate");x.add_argument("--persistent-root",type=Path,required=True);x.add_argument("--study",type=Path,required=True);x.add_argument("--arm",choices=ARMS,required=True)
    a=p.parse_args();out=prepare(root=a.persistent_root,study=a.study,prefix=a.prefix) if a.cmd=="prepare" else generate_arm(root=a.persistent_root,study=a.study,arm=a.arm) if a.cmd=="generate" else prepare_review(root=a.persistent_root,study=a.study);print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
