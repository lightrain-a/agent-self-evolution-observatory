from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p22_retrieval_budget_harness import (
    CAL_IDS,
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EVAL_IDS,
    HARNESS_PLAN_SHA256,
    K_VALUES,
    build_pool,
    bm25_rank,
    load_rows,
)
from .p22_search_backend import install_original_transport_with_cache

AGENT_MODEL = "kimi-k3"
JUDGE_MODEL = "deepseek-v4-pro"
TASK_PROVIDER_CALL_CAP = 8
JUDGE_PROVIDER_CALL_CAP = 1


def _unit_lock_path(output: Path) -> Path:
    return Path(str(output) + ".lock")


def acquire_unit_lock(output: Path, *, phase: str, task_id: str, kval: int | str) -> Path:
    output = Path(output)
    if output.exists():
        raise RuntimeError(f"P22_UNIT_RECEIPT_ALREADY_EXISTS:{output}")
    lock = _unit_lock_path(output)
    lock.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "status": "P22_UNIT_EXECUTION_LOCKED",
        "pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "phase": str(phase),
        "task_id": str(task_id),
        "k": kval,
        "contract_sha256": CONTRACT_SHA256,
        "harness_plan_sha256": HARNESS_PLAN_SHA256,
        "scientific_authority": False,
        "belief_authority": False,
    }
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"P22_UNIT_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    return lock


def _operational_error_receipt(*, phase: str, task_id: str, kval: int | str, error: Exception) -> dict[str, Any]:
    core = {
        "schema_version": "1.0",
        "status": "OPERATIONAL_ERROR_ZERO_AUTHORITY",
        "candidate_id": CANDIDATE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "harness_plan_sha256": HARNESS_PLAN_SHA256,
        "phase": str(phase),
        "task_id": str(task_id),
        "k": kval,
        "error_type": type(error).__name__,
        "error": str(error)[:1200],
        "provider_call_attempts_total": 0,
        "scientific_authority": False,
        "belief_authority": False,
    }
    core["unit_receipt_sha256"] = hashlib.sha256(json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return core


def _k_int(value: int | str) -> int:
    return 30 if value == "all" else int(value)


def prediction_manifest_valid(path: Path) -> tuple[bool, str]:
    if not path.is_file(): return False, "prediction-manifest-missing"
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except Exception: return False, "prediction-manifest-invalid-json"
    if payload.get("status")!="P22_EVALUATION_PREDICTIONS_COMMITTED": return False, "prediction-manifest-status"
    if payload.get("candidate_id")!=CANDIDATE_ID or payload.get("contract_sha256")!=CONTRACT_SHA256: return False, "prediction-manifest-contract"
    if payload.get("harness_plan_sha256")!=HARNESS_PLAN_SHA256: return False, "prediction-manifest-harness-plan"
    embedded=str(payload.get("prediction_manifest_sha256") or "")
    core=dict(payload); core.pop("prediction_manifest_sha256",None)
    actual=hashlib.sha256(json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if embedded!=actual: return False, "prediction-manifest-digest"
    return True, embedded


def _install_third_party(memevolve_root: Path):
    flash=memevolve_root/"Flash-Searcher-main"
    if str(flash) not in sys.path: sys.path.insert(0,str(flash))
    transport = install_original_transport_with_cache()
    from FlashOAgents.models import OpenAIServerModel
    from EvolveLab.memory_types import MemoryItem, MemoryItemType, MemoryResponse, MemoryStatus, MemoryType
    from base_agent import MMSearchAgent
    from run_flash_searcher_mm_xbench import grade_question
    return OpenAIServerModel,MemoryItem,MemoryItemType,MemoryResponse,MemoryStatus,MemoryType,MMSearchAgent,grade_question,transport


def _capped_model(OpenAIServerModel, *, model_id: str, api_key: str, api_base: str, cap: int, max_completion_tokens: int):
    model=OpenAIServerModel(model_id=model_id,api_key=api_key,api_base=api_base,max_completion_tokens=max_completion_tokens)
    original=model.client.chat.completions
    counter={"attempts":0,"cap":int(cap)}; receipts=[]
    class Proxy:
        def __init__(self,inner): self.inner=inner
        def create(self,*args,**kwargs):
            if counter["attempts"]>=counter["cap"]: raise RuntimeError("P22_PROVIDER_CALL_CAP")
            counter["attempts"]+=1; attempt=counter["attempts"]
            try:
                response=self.inner.create(*args,**kwargs)
                usage=getattr(response,"usage",None)
                response_id=str(getattr(response,"id","") or "")
                receipts.append({"attempt":attempt,"status":"SUCCESS","requested_model":str(kwargs.get("model") or model_id),"resolved_model":str(getattr(response,"model","") or ""),"response_id_sha256":hashlib.sha256(response_id.encode()).hexdigest() if response_id else "","prompt_tokens":int(getattr(usage,"prompt_tokens",0) or 0),"completion_tokens":int(getattr(usage,"completion_tokens",0) or 0)})
                return response
            except Exception as error:
                receipts.append({"attempt":attempt,"status":"ERROR","requested_model":str(kwargs.get("model") or model_id),"error_type":type(error).__name__})
                raise
    model.client.chat.completions=Proxy(original)
    model._p22_provider_counter=counter; model._p22_provider_receipts=receipts
    return model


def _memory_provider(index_rows: list[dict[str, Any]], pool: list[dict[str,str]], kval: int | str, types):
    MemoryItem,MemoryItemType,MemoryResponse,MemoryStatus,MemoryType=types
    k=_k_int(kval); by_id={x["memory_id"]:x for x in pool}
    class FrozenProvider:
        def initialize(self): return True
        def get_memory_type(self): return MemoryType.AGENT_KB
        def provide_memory(self,request):
            if request.status!=MemoryStatus.BEGIN: return MemoryResponse(memories=[],memory_type=MemoryType.AGENT_KB,total_count=0)
            items=[]
            for rank,row in enumerate(index_rows[:k],1):
                art=by_id[row["memory_id"]]
                items.append(MemoryItem(id=art["memory_id"],content=f"[Retrieved procedural memory {rank}/{k}; source={art['source_task_id']}]\n{art['content']}",metadata={"source":"p22_frozen_bm25","source_task_id":art["source_task_id"],"score":row["score"],"content_sha256":art["content_sha256"]},score=float(row["score"]),type=MemoryItemType.TEXT))
            return MemoryResponse(memories=items,memory_type=MemoryType.AGENT_KB,total_count=len(items))
        def take_in_memory(self,trajectory_data): return True,"P22 frozen memory: no write"
    return FrozenProvider()


def _transport_failures(trajectory: list[dict[str, Any]]) -> list[str]:
    markers=("P22_UNSUPPORTED_JS_ONLY_PAGE","Search failed after","Error reading page:","TERMINATE_QUOTA")
    found=[]
    for step in trajectory or []:
        text=json.dumps(step.get("obs") if isinstance(step,dict) else step,ensure_ascii=False,default=str)
        for marker in markers:
            if marker in text and marker not in found: found.append(marker)
    return found


def execute_unit(*, phase: str, task_id: str, kval: int | str, memevolve_root: Path, xbench_root: Path, prediction_manifest: Path | None = None, agent_api_key: str | None = None, agent_api_base: str | None = None) -> dict[str, Any]:
    phase=str(phase).lower().strip()
    allowed=CAL_IDS if phase=="calibration" else EVAL_IDS if phase=="evaluation" else ()
    if task_id not in allowed: raise ValueError(f"task {task_id} is not in frozen {phase} split")
    if kval not in K_VALUES: raise ValueError(f"k not frozen: {kval}")
    prediction_sha=""
    if phase=="evaluation":
        ok,prediction_sha=prediction_manifest_valid(Path(prediction_manifest or ""))
        if not ok: raise RuntimeError(f"evaluation-locked:{prediction_sha}")
    api_key=str(agent_api_key or os.getenv("ARK_API_KEY") or "").strip(); api_base=str(agent_api_base or os.getenv("ARK_BASE_URL") or "").strip()
    if not api_key or not api_base: raise RuntimeError("P22 Ark OpenAI-compatible transport is not configured")
    web_cache=str(os.getenv("P22_WEB_CACHE_DIR") or "").strip()
    if not web_cache: raise RuntimeError("P22 frozen web cache is not configured")
    if not str(os.getenv("SERPER_API_KEY") or "").strip(): raise RuntimeError("P22 original Serper transport is not configured")
    if (os.getenv("WEB_ACCESS_PROVIDER") or "jina").lower()=="jina" and not str(os.getenv("JINA_API_KEY") or "").strip(): raise RuntimeError("P22 original Jina crawl transport is not configured")
    third=_install_third_party(memevolve_root)
    OpenAIServerModel,MemoryItem,MemoryItemType,MemoryResponse,MemoryStatus,MemoryType,MMSearchAgent,grade_question,transport=third
    rows=load_rows(xbench_root/"data/DeepSearch-2505.csv"); task=rows[task_id]; pool=build_pool(rows); ranking=bm25_rank(task["prompt"],pool)
    provider=_memory_provider(ranking,pool,kval,(MemoryItem,MemoryItemType,MemoryResponse,MemoryStatus,MemoryType))
    task_model=_capped_model(OpenAIServerModel,model_id=AGENT_MODEL,api_key=api_key,api_base=api_base,cap=TASK_PROVIDER_CALL_CAP,max_completion_tokens=32768)
    judge_model=_capped_model(OpenAIServerModel,model_id=JUDGE_MODEL,api_key=api_key,api_base=api_base,cap=JUDGE_PROVIDER_CALL_CAP,max_completion_tokens=4096)
    cap_censored=False; error=""; result={}; score=0; extracted=""; explanation=""
    try:
        agent=MMSearchAgent(task_model,summary_interval=8,prompts_type="default",max_steps=40,memory_provider=provider)
        result=agent(task["prompt"])
        response=result.get("agent_result","") if isinstance(result,dict) else result
        if isinstance(response,dict): response=response.get("answer") or json.dumps(response,ensure_ascii=False)
        score,extracted,explanation=grade_question(task["prompt"],task["answer"],str(response or ""),judge_model)
    except Exception as exc:
        error=f"{type(exc).__name__}: {str(exc)[:1200]}"; cap_censored="P22_PROVIDER_CALL_CAP" in error
    selected=ranking[:_k_int(kval)]
    agent_result=result.get("agent_result") if isinstance(result,dict) else result; trajectory=result.get("agent_trajectory",[]) if isinstance(result,dict) else []
    transport_failures=_transport_failures(trajectory)
    transport_censored=bool(transport_failures)
    result_sha=hashlib.sha256(json.dumps(agent_result,ensure_ascii=False,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest() if agent_result is not None else ""
    trajectory_sha=hashlib.sha256(json.dumps(trajectory,ensure_ascii=False,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest() if trajectory else ""
    core={"schema_version":"1.0","status":"CAP_CENSORED" if cap_censored else "TRANSPORT_CENSORED" if transport_censored else "EXECUTION_ERROR" if error else "UNIT_COMPLETE","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,"phase":phase,"task_id":task_id,"k":kval,"k_int":_k_int(kval),"agent_model_requested":AGENT_MODEL,"judge_model_requested":JUDGE_MODEL,"prediction_manifest_sha256":prediction_sha,"web_cache_dir":web_cache,"web_transport":transport,"selected_memory_ids":[x["memory_id"] for x in selected],"selected_memory_scores":[x["score"] for x in selected],"task_provider_call_attempts":task_model._p22_provider_counter["attempts"],"judge_provider_call_attempts":judge_model._p22_provider_counter["attempts"],"provider_call_attempts_total":task_model._p22_provider_counter["attempts"]+judge_model._p22_provider_counter["attempts"],"task_provider_receipts":task_model._p22_provider_receipts,"judge_provider_receipts":judge_model._p22_provider_receipts,"agent_result_sha256":result_sha,"agent_trajectory_sha256":trajectory_sha,"cap_censored":cap_censored,"transport_censored":transport_censored,"transport_failures":transport_failures,"downstream_success":int(score) if not error and not transport_censored else None,"extracted_answer":extracted if not error and not transport_censored else "","judge_explanation":explanation if not error and not transport_censored else "","error":error,"memory_evolution_disabled":True,"scientific_authority":False,"belief_authority":False}
    core["unit_receipt_sha256"]=hashlib.sha256(json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return core


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--phase",choices=["calibration","evaluation"],required=True); ap.add_argument("--task-id",required=True); ap.add_argument("--k",required=True); ap.add_argument("--memevolve-root",type=Path,required=True); ap.add_argument("--xbench-root",type=Path,required=True); ap.add_argument("--prediction-manifest",type=Path); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    kval="all" if a.k=="all" else int(a.k)
    lock = acquire_unit_lock(a.output, phase=a.phase, task_id=a.task_id, kval=kval)
    try:
        try:
            out=execute_unit(phase=a.phase,task_id=a.task_id,kval=kval,memevolve_root=a.memevolve_root,xbench_root=a.xbench_root,prediction_manifest=a.prediction_manifest)
        except Exception as error:
            out=_operational_error_receipt(phase=a.phase,task_id=a.task_id,kval=kval,error=error)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(out,ensure_ascii=False,indent=2))
    finally:
        if a.output.exists():
            lock.unlink(missing_ok=True)

if __name__=="__main__": main()
