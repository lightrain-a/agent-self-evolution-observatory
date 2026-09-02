#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_actor_pool import ActorRolloutConfig, file_sha256, run_actor_rollout
from research_pipeline.e2_r17_local_openai_react import LocalOpenAIReactLLM

MODEL = "qwen2.5:32b"
MODEL_BLOB_SHA256 = "eabc98a9bcbfce7fd70f3e07de599f8fda98120fefed5881934161ede8bd1a41"
MODEL_MANIFEST_SHA256 = "9f13ba1299afea09d9a956fc6a85becc99115a6d596fae201a5487a03bdc4368"
SHOW_JSON_SHA256 = "e6e56810c471a24dace665dc07bc05cfbbef484969134c84468ab22a02d590e5"
MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
OLD_SUITE_MANIFEST_SHA256 = "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
OLD_SPLIT_MANIFEST_SHA256 = "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9"
TASK_IDS = (
    "r17-b0-agj-p4",
    "r17-b0-fmv-p1",
    "r17-b0-ioc-p3",
    "r17-b0-msp-p3",
    "r17-b0-ska-p3",
    "r17-b0-tsr-p3",
)
REPEATS = 3
SEED = 1717
MAX_TURNS = 10
MAX_OUTPUT_TOKENS = 4096


def canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    for source in reversed([root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv
    return ReactAgentFactory, SpreadsheetBenchEnv


def canonical_tool_semantics(message: dict[str, Any]) -> list[dict[str, Any]]:
    rows=[]
    for call in message.get("tool_calls") or []:
        fn=call.get("function") or {}
        raw=fn.get("arguments")
        try:
            args=json.loads(raw) if isinstance(raw,str) else raw
        except Exception:
            args=raw
        rows.append({"name":fn.get("name"),"arguments":args})
    return rows


def action_sequence(trajectory: dict[str, Any]) -> list[str]:
    out=[]
    for row in trajectory.get("messages") or []:
        if not isinstance(row,dict):
            continue
        for call in row.get("tool_calls") or []:
            fn=call.get("function") or {}
            if fn.get("name"):
                out.append(str(fn["name"]))
    return out


async def tool_probe(base_url: str) -> dict[str, Any]:
    messages=[
        {"role":"system","content":"Call the supplied function exactly once. Do not answer in prose."},
        {"role":"user","content":"Use add_numbers to calculate 7 + 5."},
    ]
    tools=[{"type":"function","function":{"name":"add_numbers","description":"Add two integers.","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"],"additionalProperties":False}}}]
    rows=[]
    for repeat in range(REPEATS):
        adapter=LocalOpenAIReactLLM(base_url=base_url,requested_model=MODEL,required_resolved_model=MODEL,max_output_tokens=256,seed=SEED)
        msg=await adapter(messages,tools)
        semantics=canonical_tool_semantics(msg)
        rows.append({"repeat":repeat,"semantic_tool_calls":semantics,"semantic_sha256":canonical_sha(semantics),"finish_reasons":[x["finish_reason"] for x in adapter.public_receipts()]})
    expected=[{"name":"add_numbers","arguments":{"a":7,"b":5}}]
    return {
        "rows":rows,
        "semantic_exact_reproduction":len({x["semantic_sha256"] for x in rows})==1,
        "expected_semantics":all(x["semantic_tool_calls"]==expected for x in rows),
    }


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    runtime=args.runtime_root
    blob=runtime / "models/blobs" / f"sha256-{MODEL_BLOB_SHA256}"
    manifest=runtime / "models/manifests/registry.ollama.ai/library/qwen2.5/32b"
    show=runtime / "qwen25-32b-show.json"
    if not blob.is_file() or file_sha256(blob)!=MODEL_BLOB_SHA256:
        raise RuntimeError("Qwen2.5-32B model blob drift")
    if not manifest.is_file() or file_sha256(manifest)!=MODEL_MANIFEST_SHA256:
        raise RuntimeError("Ollama model manifest drift")
    if not show.is_file() or file_sha256(show)!=SHOW_JSON_SHA256:
        raise RuntimeError("ollama show identity drift")
    show_payload=json.loads(show.read_text(encoding="utf-8"))
    details=show_payload.get("details") or {}
    if details.get("parameter_size")!="32.8B" or details.get("quantization_level")!="Q4_K_M":
        raise RuntimeError("Qwen local realization details drift")

    with urllib.request.urlopen(args.base_url.rstrip("/")+"/v1/models",timeout=3) as response:
        models=json.loads(response.read().decode("utf-8"))
    if MODEL not in {str(x.get("id")) for x in models.get("data") or []}:
        raise RuntimeError("Qwen2.5-32B not served by local endpoint")

    mind_head=subprocess.check_output(["git","-C",str(args.mindmemos_root),"rev-parse","HEAD"],text=True).strip()
    if mind_head!=MINDMEMOS_COMMIT:
        raise RuntimeError("MindMemOS commit drift")
    if subprocess.check_output(["git","-C",str(args.mindmemos_root),"status","--short"],text=True).strip():
        raise RuntimeError("MindMemOS tree dirty")
    split_path=args.suite_root / "r17_split_manifest.json"
    if file_sha256(args.suite_root/"suite_manifest.json")!=OLD_SUITE_MANIFEST_SHA256 or file_sha256(split_path)!=OLD_SPLIT_MANIFEST_SHA256:
        raise RuntimeError("development suite drift")
    split=json.loads(split_path.read_text(encoding="utf-8"))
    if not set(TASK_IDS).issubset(set(map(str,split["development"]))):
        raise RuntimeError("qualification tasks escaped development split")

    ReactAgentFactory, SpreadsheetBenchEnv=load_mindmemos(args.mindmemos_root)
    initial=args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_sha=file_sha256(initial/"SKILL.md")
    metadata={str(x["id"]):x for x in json.loads((args.suite_root/"r17_controlled_metadata.json").read_text(encoding="utf-8"))}
    evaluator_sources=[
        args.mindmemos_root/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]

    probe=await tool_probe(args.base_url)
    if not probe["semantic_exact_reproduction"] or not probe["expected_semantics"]:
        raise RuntimeError("semantic tool-call reproducibility failed")

    task_rows=[]
    for task_id in TASK_IDS:
        repeats=[]
        for repeat in range(REPEATS):
            rr=args.run_root / task_id / f"repeat_{repeat}"
            env=SpreadsheetBenchEnv(args.suite_root,rr)
            cases={case.id:case for case in env.load_cases("all")}
            adapter=LocalOpenAIReactLLM(base_url=args.base_url,requested_model=MODEL,required_resolved_model=MODEL,max_output_tokens=MAX_OUTPUT_TOKENS,seed=SEED)
            factory=ReactAgentFactory(adapter,max_turns=MAX_TURNS,skill_sources=[initial],python_path=sys.executable)
            config=ActorRolloutConfig(requested_model=MODEL,required_resolved_model=MODEL,max_turns=MAX_TURNS,skill_source=str(initial),skill_pre_sha256=skill_sha,failure_family=str(metadata[task_id]["primary_failure_family"]),experiment_mode="qwen25_32b_local_realization_qualification")
            ref=await run_actor_rollout(env=env,case=cases[task_id],rollout_index=0,agent_factory=factory,adapter=adapter,config=config,evaluator_sources=evaluator_sources)
            ref_path=rr/"cases"/task_id/"rollout_0"/"r17_trajectory_ref.json"
            trajectory=json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))
            receipts=adapter.public_receipts()
            repeats.append({
                "repeat":repeat,
                "score":float(ref.score),
                "provider_calls":len(receipts),
                "finish_reasons":[str(x.get("finish_reason") or "") for x in receipts],
                "trajectory_ref_path":str(ref_path),
                "trajectory_ref_sha256":file_sha256(ref_path),
                "action_tool_sequence":action_sequence(trajectory),
            })
        scores=[x["score"] for x in repeats]
        task_rows.append({
            "task_id":task_id,
            "failure_family":metadata[task_id]["primary_failure_family"],
            "repeats":repeats,
            "score_exact_reproduction":len(set(scores))==1,
            "score":scores[0] if len(set(scores))==1 else None,
            "action_tool_sequence_exact":len({tuple(x["action_tool_sequence"]) for x in repeats})==1,
        })

    all_complete=len(task_rows)==len(TASK_IDS) and all(len(x["repeats"])==REPEATS for x in task_rows)
    no_length=all("length" not in x["finish_reasons"] for row in task_rows for x in row["repeats"])
    score_repro=all(row["score_exact_reproduction"] for row in task_rows)
    success_tasks=sum(int(float(row["score"] or 0.0)==1.0) for row in task_rows if row["score"] is not None)
    nondegenerate=0 < success_tasks < len(TASK_IDS)
    pass_gate=all_complete and no_length and score_repro and nondegenerate
    return {
        "schema_version":"1.0",
        "artifact_type":"e2-r17-qwen25-32b-q4-local-realization-qualification",
        "created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status":"PASS_QWEN25_32B_Q4_LOCAL_REALIZATION_QUALIFICATION" if pass_gate else "FAIL_QWEN25_32B_Q4_LOCAL_REALIZATION_QUALIFICATION",
        "scientific_outcome":False,
        "old_deepseek_hold_reinterpreted":False,
        "new_cal_test_outcomes_accessed":False,
        "model_identity":{
            "served_model":MODEL,
            "base_model":"Qwen2.5-32B-Instruct",
            "parameter_size":"32.8B",
            "quantization":"Q4_K_M",
            "model_blob_sha256":MODEL_BLOB_SHA256,
            "ollama_manifest_sha256":MODEL_MANIFEST_SHA256,
            "ollama_show_sha256":SHOW_JSON_SHA256,
            "endpoint":args.base_url,
        },
        "decoding":{"temperature":0.0,"top_p":1.0,"seed":SEED,"thinking":False,"max_turns":MAX_TURNS,"max_output_tokens":MAX_OUTPUT_TOKENS,"provider_retry_limit":0},
        "tool_probe":probe,
        "development_task_ids":list(TASK_IDS),
        "repeats_per_task":REPEATS,
        "tasks":task_rows,
        "checks":{
            "technical_rollouts":sum(len(x["repeats"]) for x in task_rows),
            "technical_rollouts_expected":len(TASK_IDS)*REPEATS,
            "all_complete":all_complete,
            "no_length_truncation":no_length,
            "score_exact_reproduction_all_tasks":score_repro,
            "success_tasks":success_tasks,
            "failure_tasks":len(TASK_IDS)-success_tasks,
            "nondegenerate_headroom":nondegenerate,
            "action_tool_sequence_exact_tasks":sum(row["action_tool_sequence_exact"] for row in task_rows),
        },
        "interpretation_boundary":"Development-only qualification for a local quantized Qwen2.5-32B-Instruct realization. PASS does not authorize CAL/TEST science, does not convert the closed DeepSeek HOLD, and is not a full-precision Qwen2.5-32B result.",
        "authority":{"static_model_candidate":pass_gate,"updater_qualification":False,"cal_scientific_execution":False,"test_scientific_execution":False,"paper_promotion":False},
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-url",default="http://127.0.0.1:11444")
    ap.add_argument("--runtime-root",type=Path,required=True)
    ap.add_argument("--suite-root",type=Path,required=True)
    ap.add_argument("--mindmemos-root",type=Path,required=True)
    ap.add_argument("--run-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists(): raise RuntimeError("qualification output already exists")
    payload=asyncio.run(main_async(a))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":payload["status"],"checks":payload["checks"],"model_identity":payload["model_identity"]},ensure_ascii=False,indent=2))
    return 0 if payload["status"].startswith("PASS_") else 3

if __name__=="__main__": raise SystemExit(main())
