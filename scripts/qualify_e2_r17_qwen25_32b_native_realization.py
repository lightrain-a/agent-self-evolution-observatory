#!/usr/bin/env python3
from __future__ import annotations

import argparse, asyncio, json, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from research_pipeline.e2_r17_actor_pool import ActorRolloutConfig, file_sha256, run_actor_rollout
from research_pipeline.e2_r17_local_ollama_react import LocalOllamaReactLLM
from scripts.qualify_e2_r17_qwen25_32b_local_realization import (
    MODEL, MODEL_BLOB_SHA256, MODEL_MANIFEST_SHA256, SHOW_JSON_SHA256,
    MINDMEMOS_COMMIT, OLD_SUITE_MANIFEST_SHA256, OLD_SPLIT_MANIFEST_SHA256,
    TASK_IDS, REPEATS, SEED, MAX_TURNS, MAX_OUTPUT_TOKENS,
    canonical_sha, canonical_tool_semantics, load_mindmemos, action_sequence,
)

async def tool_probe(base_url:str)->dict[str,Any]:
    messages=[{"role":"system","content":"Call the supplied function exactly once. Do not answer in prose."},{"role":"user","content":"Use add_numbers to calculate 7 + 5."}]
    tools=[{"type":"function","function":{"name":"add_numbers","description":"Add two integers.","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"],"additionalProperties":False}}}]
    rows=[]
    for repeat in range(REPEATS):
        adapter=LocalOllamaReactLLM(base_url=base_url,requested_model=MODEL,required_resolved_model=MODEL,max_output_tokens=256,seed=SEED)
        msg=await adapter(messages,tools); semantics=canonical_tool_semantics(msg)
        rows.append({"repeat":repeat,"semantic_tool_calls":semantics,"semantic_sha256":canonical_sha(semantics),"receipts":adapter.public_receipts()})
    expected=[{"name":"add_numbers","arguments":{"a":7,"b":5}}]
    return {"rows":rows,"semantic_exact_reproduction":len({x["semantic_sha256"] for x in rows})==1,"expected_semantics":all(x["semantic_tool_calls"]==expected for x in rows)}

def base_payload(args:argparse.Namespace)->dict[str,Any]:
    return {"schema_version":"1.0","artifact_type":"e2-r17-qwen25-32b-q4-native-realization-qualification","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"scientific_outcome":False,"old_deepseek_hold_reinterpreted":False,"new_cal_test_outcomes_accessed":False,"model_identity":{"served_model":MODEL,"base_model":"Qwen2.5-32B-Instruct","parameter_size":"32.8B","quantization":"Q4_K_M","model_blob_sha256":MODEL_BLOB_SHA256,"ollama_manifest_sha256":MODEL_MANIFEST_SHA256,"ollama_show_sha256":SHOW_JSON_SHA256,"transport":"native_ollama_api_chat","endpoint":args.base_url},"decoding":{"temperature":0.0,"top_p":1.0,"seed":SEED,"thinking":False,"max_turns":MAX_TURNS,"max_output_tokens":MAX_OUTPUT_TOKENS,"provider_retry_limit":0},"development_task_ids":list(TASK_IDS),"repeats_per_task":REPEATS,"tasks":[]}

async def run(args:argparse.Namespace)->dict[str,Any]:
    out=base_payload(args); runtime=args.runtime_root
    blob=runtime/"models/blobs"/f"sha256-{MODEL_BLOB_SHA256}"; manifest=runtime/"models/manifests/registry.ollama.ai/library/qwen2.5/32b"; show=runtime/"qwen25-32b-show.json"
    if not blob.is_file() or file_sha256(blob)!=MODEL_BLOB_SHA256: raise RuntimeError("model blob drift")
    if not manifest.is_file() or file_sha256(manifest)!=MODEL_MANIFEST_SHA256: raise RuntimeError("manifest drift")
    if not show.is_file() or file_sha256(show)!=SHOW_JSON_SHA256: raise RuntimeError("show identity drift")
    with urllib.request.urlopen(args.base_url.rstrip("/")+"/api/tags",timeout=3) as response: tags=json.loads(response.read().decode())
    if MODEL not in {str(x.get("name")) for x in tags.get("models") or []}: raise RuntimeError("model not served")
    if subprocess.check_output(["git","-C",str(args.mindmemos_root),"rev-parse","HEAD"],text=True).strip()!=MINDMEMOS_COMMIT: raise RuntimeError("MindMemOS drift")
    if subprocess.check_output(["git","-C",str(args.mindmemos_root),"status","--short"],text=True).strip(): raise RuntimeError("MindMemOS dirty")
    split_path=args.suite_root/"r17_split_manifest.json"
    if file_sha256(args.suite_root/"suite_manifest.json")!=OLD_SUITE_MANIFEST_SHA256 or file_sha256(split_path)!=OLD_SPLIT_MANIFEST_SHA256: raise RuntimeError("suite drift")
    split=json.loads(split_path.read_text());
    if not set(TASK_IDS).issubset(set(map(str,split["development"]))): raise RuntimeError("task escaped development")
    ReactAgentFactory,SpreadsheetBenchEnv=load_mindmemos(args.mindmemos_root)
    initial=args.mindmemos_root/"resources/skill_evolve/spreadsheetbench_init_skill/xlsx"; skill_sha=file_sha256(initial/"SKILL.md")
    metadata={str(x["id"]):x for x in json.loads((args.suite_root/"r17_controlled_metadata.json").read_text())}
    evaluator_sources=[args.mindmemos_root/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",args.mindmemos_root/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py"]
    probe=await tool_probe(args.base_url); out["tool_probe"]={k:v for k,v in probe.items() if k!="rows"}; out["tool_probe"]["rows"]=probe["rows"]
    if not probe["semantic_exact_reproduction"] or not probe["expected_semantics"]:
        out.update(status="FAIL_QWEN25_32B_Q4_NATIVE_TOOL_REPRODUCIBILITY",checks={"tool_probe_pass":False},authority={"cal_scientific_execution":False,"updater_qualification":False}); return out
    for task_id in TASK_IDS:
        repeats=[]
        for repeat in range(REPEATS):
            rr=args.run_root/task_id/f"repeat_{repeat}"; env=SpreadsheetBenchEnv(args.suite_root,rr); cases={c.id:c for c in env.load_cases("all")}
            adapter=LocalOllamaReactLLM(base_url=args.base_url,requested_model=MODEL,required_resolved_model=MODEL,max_output_tokens=MAX_OUTPUT_TOKENS,seed=SEED)
            factory=ReactAgentFactory(adapter,max_turns=MAX_TURNS,skill_sources=[initial],python_path=sys.executable)
            config=ActorRolloutConfig(requested_model=MODEL,required_resolved_model=MODEL,max_turns=MAX_TURNS,skill_source=str(initial),skill_pre_sha256=skill_sha,failure_family=str(metadata[task_id]["primary_failure_family"]),experiment_mode="qwen25_32b_native_realization_qualification")
            ref=await run_actor_rollout(env=env,case=cases[task_id],rollout_index=0,agent_factory=factory,adapter=adapter,config=config,evaluator_sources=evaluator_sources)
            ref_path=rr/"cases"/task_id/"rollout_0"/"r17_trajectory_ref.json"; trajectory=json.loads(Path(ref.trajectory_path).read_text()); receipts=adapter.public_receipts()
            repeats.append({"repeat":repeat,"score":float(ref.score),"provider_calls":len(receipts),"finish_reasons":[str(x.get("finish_reason") or "") for x in receipts],"trajectory_ref_path":str(ref_path),"trajectory_ref_sha256":file_sha256(ref_path),"action_tool_sequence":action_sequence(trajectory)})
        scores=[x["score"] for x in repeats]; exact=len(set(scores))==1
        row={"task_id":task_id,"failure_family":metadata[task_id]["primary_failure_family"],"repeats":repeats,"score_exact_reproduction":exact,"score":scores[0] if exact else None,"action_tool_sequence_exact":len({tuple(x["action_tool_sequence"]) for x in repeats})==1}; out["tasks"].append(row)
        if not exact:
            out.update(status="FAIL_QWEN25_32B_Q4_NATIVE_SCORE_REPRODUCIBILITY",fail_fast_task=task_id,checks={"tool_probe_pass":True,"completed_rollouts":sum(len(x["repeats"]) for x in out["tasks"]),"score_exact_reproduction_all_completed_tasks":False},authority={"qwen_actor_realization":False,"updater_qualification":False,"cal_scientific_execution":False,"test_scientific_execution":False}); return out
    no_length=all("length" not in x["finish_reasons"] for row in out["tasks"] for x in row["repeats"]); success_tasks=sum(float(row["score"])==1.0 for row in out["tasks"]); nondegenerate=0<success_tasks<len(TASK_IDS)
    passed=no_length and nondegenerate
    out.update(status="PASS_QWEN25_32B_Q4_NATIVE_REALIZATION_QUALIFICATION" if passed else "FAIL_QWEN25_32B_Q4_NATIVE_HEADROOM",checks={"tool_probe_pass":True,"technical_rollouts":len(TASK_IDS)*REPEATS,"no_length_truncation":no_length,"score_exact_reproduction_all_tasks":True,"success_tasks":success_tasks,"failure_tasks":len(TASK_IDS)-success_tasks,"nondegenerate_headroom":nondegenerate,"action_tool_sequence_exact_tasks":sum(x["action_tool_sequence_exact"] for x in out["tasks"])},interpretation_boundary="Development-only qualification of a local Q4 Qwen2.5-32B native-Ollama realization; no CAL/TEST or old DeepSeek claim authority.",authority={"qwen_actor_realization":passed,"updater_qualification":False,"cal_scientific_execution":False,"test_scientific_execution":False,"paper_promotion":False}); return out

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--base-url",default="http://127.0.0.1:11444"); ap.add_argument("--runtime-root",type=Path,required=True); ap.add_argument("--suite-root",type=Path,required=True); ap.add_argument("--mindmemos-root",type=Path,required=True); ap.add_argument("--run-root",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    if a.output.exists() or a.run_root.exists(): raise RuntimeError("fresh qualification root/output required")
    payload=asyncio.run(run(a)); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":payload["status"],"checks":payload.get("checks"),"fail_fast_task":payload.get("fail_fast_task")},indent=2)); return 0 if payload["status"].startswith("PASS_") else 3
if __name__=="__main__": raise SystemExit(main())
