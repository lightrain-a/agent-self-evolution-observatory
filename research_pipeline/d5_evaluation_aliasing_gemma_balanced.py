from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .d5_state_sufficiency_f0 import ARMS, _read_jsonl, _sha_file, _stable_hash, _task_rel_id, historical_task_exposure
from .d5_state_sufficiency_gemma import MODEL_ID, _service_identity
from .p0_alfworld_adapter import ALFWorldGameRunner, load_config
from .p0_mem_xfer_support_enriched import _token_matched_placebo
from .vllm_alfworld_policy import VLLMAdmissiblePolicy

EXPERIMENT_ID = "D5-EVALUATION-ALIASING-GEMMA-BALANCED-v2"
REQUEST_SEED = 20260822
DEFAULT_BASE_URL = "http://127.0.0.1:18002"
FAMILIES = (
    "pick_and_place_simple",
    "pick_clean_then_place_in_recep",
    "pick_cool_then_place_in_recep",
    "pick_heat_then_place_in_recep",
)
MAX_STEPS = 50


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _public_service(identity: dict[str, Any]) -> dict[str, Any]:
    return {k: identity[k] for k in (
        "model_id", "max_model_len", "exact_revision", "formal_asset_receipt_sha256",
        "official_source_manifest_sha256", "verified_weight_digests",
    )}


def compile_contract(*, source_memories_path: Path, historical_runs_root: Path, alfworld_root: Path,
                     alfworld_config: Path, service_base_url: str, model_receipt_path: Path) -> dict[str, Any]:
    memories = _read_jsonl(source_memories_path)
    heldout = [r for r in memories if str(r.get("candidate_role") or "") == "heldout_candidate"]
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in heldout:
        by_family[str(row.get("source_family") or "")].append(row)
    if tuple(sorted(by_family)) != tuple(sorted(FAMILIES)) or any(len(by_family[f]) != 1 for f in FAMILIES):
        raise ValueError("need exactly one heldout_candidate memory from every source family")
    pool = [by_family[f][0] for f in FAMILIES]
    memory_ids = [str(row["memory_id"]) for row in pool]

    exposed = historical_task_exposure(historical_runs_root)
    excluded = set(exposed)
    excluded.update(_task_rel_id(row.get("source_task_id") or "") for row in memories)
    task_root = alfworld_root / "json_2.1.1" / "valid_unseen"
    stage_a, stage_b, fresh_counts = [], [], {}
    for family in FAMILIES:
        candidates = sorted(
            _task_rel_id(path) for path in task_root.glob(f"{family}-*/**/game.tw-pddl")
            if _task_rel_id(path) not in excluded
        )
        fresh_counts[family] = len(candidates)
        if len(candidates) < 2:
            raise ValueError(f"insufficient fresh tasks for {family}: {len(candidates)}")
        stage_a.append({"target_family": family, "task_relpath": candidates[0]})
        stage_b.append({"target_family": family, "task_relpath": candidates[1]})

    frozen = []
    for row in pool:
        text = str(row.get("text") or "")
        frozen.append({
            "memory_id": str(row["memory_id"]),
            "source_family": str(row.get("source_family") or ""),
            "candidate_index": int(row.get("candidate_index") or 0),
            "candidate_role": str(row.get("candidate_role") or ""),
            "source_task_relpath": _task_rel_id(row.get("source_task_id") or ""),
            "memory_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        })

    supersession = Path("generated/d5-evaluation-aliasing-qwen-v2-supersession.json")
    problem_gate = Path("generated/d5-evaluation-aliasing-problem-gate.json")
    v1_quarantine = Path("generated/d5-evaluation-aliasing-gemma-balanced-v1-runtime-quarantine.json")
    seeded_smoke = Path("generated/d5-evaluation-aliasing-seeded-runtime-smoke.json")
    smoke = json.loads(seeded_smoke.read_text(encoding="utf-8"))
    if smoke.get("status") != "PASS_DETERMINISTIC_SUPPORT" or smoke.get("request_seed") != REQUEST_SEED:
        raise ValueError("seeded deterministic support smoke has not passed for the frozen request seed")
    service = _public_service(_service_identity(service_base_url, model_receipt_path))
    material = {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "status": "FROZEN_BEFORE_STAGE_A_OUTCOMES",
        "idea_id": "D5-EVALUATION-ALIASING",
        "scientific_question": "Does a finite current evaluation partition distinct persistent memories into an alias class whose members later have different controlled transfer effects?",
        "claim_boundary": "Tests evaluation-induced aliasing after one common current panel; ordinary cross-task transfer heterogeneity is not evidence unless memories first share an exact current signature.",
        "memory_pool": {
            "selection_rule": "Every historical memory with candidate_role=heldout_candidate: one from each of four frozen source families; metadata only, before common-panel outcomes.",
            "memory_ids": memory_ids,
            "memories": frozen,
        },
        "stage_a": {
            "name": "FRESH_COMMON_PANEL_ALIAS_DISCOVERY",
            "tasks": stage_a,
            "arms": list(ARMS),
            "episodes": len(memory_ids) * len(stage_a) * len(ARMS),
            "signature": "ordered per-task (retrieved_success, placebo_success, no_memory_success)",
            "alias_definition": "Two memories alias iff their complete Stage-A score signatures are exactly equal.",
            "qualification": "At least one alias class size>=2; per-task no-memory success+actions reproduce; alias signature is not complete all-zero or all-one.",
            "monotone_early_stop": "After each full task partial-signature classes only split. If every class is singleton, stop immediately.",
        },
        "stage_b": {
            "name": "SEALED_FUTURE_ALIAS_DIVERGENCE",
            "tasks": stage_b,
            "arms": list(ARMS),
            "sealed_before_stage_a_outcomes": True,
            "run_only_for_members_of_qualified_alias_classes": True,
            "controlled_delta": "retrieved_success - placebo_success",
            "go_rule": "At least one qualified alias class diverges on >=2 sealed tasks spanning >=2 target families, with reproducible no-memory success+actions.",
            "f0_go_means": "PROSPECTIVE_CONFIRMATION_ONLY",
        },
        "task_selection": {
            "rule": "Per family use lexicographically first two identities absent from every execution-bearing historical run; first Stage A, second sealed Stage B.",
            "outcome_independent": True,
            "historical_exposed_task_count": len(exposed),
            "historical_exposure_sha256": _stable_hash(sorted(exposed)),
            "fresh_counts_before_selection": fresh_counts,
        },
        "runtime": {
            "alfworld_asset": "ALFWorld json_2.1.1 valid_unseen",
            "alfworld_config": str(alfworld_config),
            "alfworld_config_sha256": _sha_file(alfworld_config),
            "policy_mode": "react-family", "max_steps": MAX_STEPS, "max_history": 6,
            "decoding": "vLLM chat temperature=0 with frozen request seed",
            "request_seed": REQUEST_SEED,
            "exclusive_transaction_lock_required": True,
            "placebo": "token-matched independently per memory; absolute token-count gap <=1",
            "outcome_truth": "ALFWorld environment won/success; no LLM judge",
        },
        "service_model": service,
        "source_artifacts": {
            "source_memories_asset": "p0-mem-xfer-support-enriched-qwen-v1/source-memories.jsonl",
            "source_memories_sha256": _sha_file(source_memories_path),
            "model_receipt_sha256": _sha_file(model_receipt_path),
            "qwen_v2_supersession": str(supersession), "qwen_v2_supersession_sha256": _sha_file(supersession),
            "problem_gate": str(problem_gate), "problem_gate_sha256": _sha_file(problem_gate),
            "balanced_v1_runtime_quarantine": str(v1_quarantine), "balanced_v1_runtime_quarantine_sha256": _sha_file(v1_quarantine),
            "seeded_runtime_smoke": str(seeded_smoke), "seeded_runtime_smoke_sha256": _sha_file(seeded_smoke),
        },
        "anti_outcome_shopping": [
            "Run all four metadata-selected memories on every Stage-A task.",
            "Do not alter Stage-B task identities after any Stage-A outcome.",
            "Open every qualified alias class, not only a favorable-looking class.",
            "If no qualified alias remains, stop; do not search replacements on the exposed panel.",
        ],
        "authority": {"scientific": False, "paper_design": False, "experiment": False, "gpu": False},
    }
    out = dict(material)
    out["contract_sha256"] = _stable_hash(material)
    out["created_at"] = _now()
    out["scientific_authority"] = False
    return out


def verify_contract(contract: dict[str, Any], *, source_memories_path: Path, service_base_url: str,
                    model_receipt_path: Path) -> None:
    material = {k: v for k, v in contract.items() if k not in {"contract_sha256", "created_at", "scientific_authority"}}
    if _stable_hash(material) != contract.get("contract_sha256"):
        raise RuntimeError("contract hash mismatch")
    if _sha_file(source_memories_path) != contract["source_artifacts"]["source_memories_sha256"]:
        raise RuntimeError("source memories changed")
    if _sha_file(model_receipt_path) != contract["source_artifacts"]["model_receipt_sha256"]:
        raise RuntimeError("model receipt changed")
    live = _public_service(_service_identity(service_base_url, model_receipt_path))
    for key in ("model_id", "exact_revision", "formal_asset_receipt_sha256", "official_source_manifest_sha256"):
        if live[key] != contract["service_model"][key]:
            raise RuntimeError(f"served model identity changed: {key}")


def _no_memory_repro(rows: list[dict[str, Any]], task: str, memory_ids: list[str]) -> bool:
    selected = [r for r in rows if r["task_relpath"] == task and r["arm"] == "no-memory"]
    return len(selected) == len(memory_ids) and len({(int(r["success"]), tuple(r.get("actions") or [])) for r in selected}) == 1


def _partial(rows: list[dict[str, Any]], contract: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[tuple[int, ...], list[str]]]:
    memory_ids = list(contract["memory_pool"]["memory_ids"])
    by: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by[(row["memory_id"], row["task_relpath"])][row["arm"]] = row
    completed, signatures = [], {mid: [] for mid in memory_ids}
    for spec in contract["stage_a"]["tasks"]:
        task = str(spec["task_relpath"])
        if any(set(by.get((mid, task), {})) != set(ARMS) for mid in memory_ids):
            continue
        triples = {}
        for mid in memory_ids:
            arms = by[(mid, task)]
            triple = (int(arms["retrieved"]["success"]), int(arms["placebo"]["success"]), int(arms["no-memory"]["success"]))
            triples[mid] = triple
            signatures[mid].extend(triple)
        completed.append({"task_relpath": task, "target_family": spec["target_family"], "triples": {k: list(v) for k, v in triples.items()}, "no_memory_reproducible": _no_memory_repro(rows, task, memory_ids)})
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for mid in memory_ids:
        groups[tuple(signatures[mid])].append(mid)
    return completed, dict(groups)


def analyze_stage_a(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    expected = int(contract["stage_a"]["episodes"])
    completed, groups = _partial(rows, contract)
    if completed and any(not row["no_memory_reproducible"] for row in completed):
        return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"EARLY_STOP_NO_MEMORY_NONREPRODUCIBLE","rows":len(rows),"expected":expected,"completed_tasks":completed,"decision":"STOP_GEMMA_BALANCED_REALIZATION","stage_b_authorized":False,"scientific_authority":False}
    viable = [members for members in groups.values() if len(members) >= 2]
    if completed and not viable:
        return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"EARLY_STOP_NO_ALIAS_CLASS_REMAINS","rows":len(rows),"expected":expected,"completed_tasks":completed,"partial_signature_groups":[{"signature":list(sig),"members":members} for sig,members in sorted(groups.items())],"decision":"STOP_GEMMA_BALANCED_REALIZATION","stage_b_authorized":False,"remaining_stage_a_rows_not_required":expected-len(rows),"scientific_authority":False}
    if len(rows) != expected:
        return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"INCOMPLETE","rows":len(rows),"expected":expected,"completed_tasks":completed,"partial_signature_groups":[{"signature":list(sig),"members":members} for sig,members in sorted(groups.items())],"scientific_authority":False}
    aliases=[]
    for signature,members in sorted(groups.items()):
        if len(members)<2: continue
        nondegenerate=not(all(v==0 for v in signature) or all(v==1 for v in signature))
        aliases.append({"alias_id":f"A{len(aliases)+1}","signature":list(signature),"members":members,"size":len(members),"nondegenerate":nondegenerate})
    qualified=[row for row in aliases if row["nondegenerate"]]
    return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"COMPLETE","rows":len(rows),"expected":expected,"completed_tasks":completed,"alias_classes":aliases,"qualified_alias_classes":qualified,"decision":"PASS_OPEN_SEALED_STAGE_B" if qualified else "STOP_GEMMA_BALANCED_NO_NONDEGENERATE_ALIAS","stage_b_authorized":bool(qualified),"scientific_authority":False}


def analyze_stage_b(rows: list[dict[str, Any]], contract: dict[str, Any], stage_a: dict[str, Any]) -> dict[str, Any]:
    aliases=list(stage_a.get("qualified_alias_classes") or [])
    required=sorted({mid for alias in aliases for mid in alias["members"]})
    expected=len(required)*len(contract["stage_b"]["tasks"])*len(ARMS)
    if len(rows)!=expected:
        return {"status":"INCOMPLETE","rows":len(rows),"expected":expected,"scientific_authority":False}
    by:dict[tuple[str,str],dict[str,dict[str,Any]]]=defaultdict(dict)
    for row in rows: by[(row["memory_id"],row["task_relpath"])][row["arm"]]=row
    results=[]
    for alias in aliases:
        table=[]
        for spec in contract["stage_b"]["tasks"]:
            task=str(spec["task_relpath"])
            deltas={mid:int(by[(mid,task)]["retrieved"]["success"])-int(by[(mid,task)]["placebo"]["success"]) for mid in alias["members"]}
            table.append({"task_relpath":task,"target_family":spec["target_family"],"controlled_deltas":deltas,"divergent":len(set(deltas.values()))>1,"no_memory_reproducible":_no_memory_repro(rows,task,required)})
        divergent=[row for row in table if row["divergent"]]
        families=sorted({row["target_family"] for row in divergent})
        no_mem=all(row["no_memory_reproducible"] for row in table)
        results.append({"alias_id":alias["alias_id"],"members":alias["members"],"effect_table":table,"divergent_task_count":len(divergent),"divergent_target_families":families,"no_memory_reproducible":no_mem,"go":no_mem and len(divergent)>=2 and len(families)>=2})
    go_classes=[row["alias_id"] for row in results if row["go"]]
    return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"B","status":"COMPLETE","rows":len(rows),"expected":expected,"alias_results":results,"go_alias_classes":go_classes,"decision":"GO_PROSPECTIVE_CONFIRMATION" if go_classes else "STOP_CURRENT_EVALUATION_ALIASING_PAPER_ON_GEMMA","paper_authorized":False,"scientific_authority":False}


def run_stage(*, stage: str, contract_path: Path, source_memories_path: Path, alfworld_root: Path,
              alfworld_config: Path, model_receipt_path: Path, service_base_url: str, output_dir: Path,
              max_new_rows: int = 0) -> dict[str, Any]:
    contract=json.loads(contract_path.read_text(encoding="utf-8"))
    verify_contract(contract,source_memories_path=source_memories_path,service_base_url=service_base_url,model_receipt_path=model_receipt_path)
    output_dir.mkdir(parents=True,exist_ok=True)
    stage_a_path=output_dir/"stage-a-analysis.json"
    stage_a=json.loads(stage_a_path.read_text(encoding="utf-8")) if stage_a_path.exists() else None
    if stage=="B" and (not stage_a or stage_a.get("decision")!="PASS_OPEN_SEALED_STAGE_B"):
        raise RuntimeError("Stage B locked")
    all_memories={str(row["memory_id"]):row for row in _read_jsonl(source_memories_path)}
    if stage=="A":
        memory_ids=list(contract["memory_pool"]["memory_ids"]);tasks=list(contract["stage_a"]["tasks"])
    else:
        memory_ids=sorted({mid for alias in stage_a["qualified_alias_classes"] for mid in alias["members"]});tasks=list(contract["stage_b"]["tasks"])
    raw_path=output_dir/f"stage-{stage.lower()}-raw.jsonl"
    prior=_read_jsonl(raw_path) if raw_path.exists() else []
    expected={(mid,str(task["task_relpath"]),arm) for task in tasks for mid in memory_ids for arm in ARMS}
    done={(row["memory_id"],row["task_relpath"],row["arm"]):row for row in prior}
    if any(key not in expected for key in done):raise RuntimeError("existing row outside frozen grid")
    os.environ["ALFWORLD_DATA"]=str(alfworld_root)
    runner=ALFWorldGameRunner(load_config(alfworld_config))
    policy=VLLMAdmissiblePolicy(base_url=service_base_url,model=MODEL_ID,policy_mode="react-family",seed=int(contract["runtime"]["request_seed"]))
    placebo={};placebo_audit={}
    for mid in memory_ids:
        text=str(all_memories[mid]["text"]);fake,mt,pt=_token_matched_placebo(policy,text)
        if abs(mt-pt)>1:raise RuntimeError(f"placebo mismatch {mid}: {mt}/{pt}")
        placebo[mid]=fake;placebo_audit[mid]={"memory_tokens":mt,"placebo_tokens":pt,"gap":abs(mt-pt)}
    rows=list(prior);new_rows=0;started=time.monotonic();stop=False
    for task in tasks:
        if stop:break
        rel=str(task["task_relpath"]);task_path=alfworld_root/rel
        if not task_path.exists():raise FileNotFoundError(task_path)
        for mid in memory_ids:
            if stop:break
            memory=str(all_memories[mid]["text"])
            for arm in ARMS:
                if max_new_rows and new_rows>=max_new_rows:stop=True;break
                key=(mid,rel,arm)
                if key in done:continue
                patch="" if arm=="no-memory" else "MEMORY::"+(memory if arm=="retrieved" else placebo[mid])
                trace=runner.run_game_file("eval_out_of_distribution",str(task_path),policy,patch,max_steps=MAX_STEPS)
                row={"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":stage,"contract_sha256":contract["contract_sha256"],"memory_id":mid,"task_relpath":rel,"target_family":str(task["target_family"]),"arm":arm,"success":int(trace.get("success") or 0),"score":float(trace.get("score") or 0),"steps":int(trace.get("steps") or 0),"invalid_actions":int(trace.get("invalid_actions") or 0),"actions":trace.get("actions") or [],"model_calls":int(trace.get("model_calls") or 0),"recorded_at":_now()}
                with raw_path.open("a",encoding="utf-8") as handle:handle.write(json.dumps(row,ensure_ascii=False)+"\n")
                rows.append(row);done[key]=row;new_rows+=1
                (output_dir/f"stage-{stage.lower()}-progress.json").write_text(json.dumps({"status":"RUNNING","contract_sha256":contract["contract_sha256"],"completed_rows":len(rows),"expected_rows":len(expected),"new_rows_this_invocation":new_rows,"elapsed_hours":(time.monotonic()-started)/3600,"updated_at":_now()},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        if stage=="A":
            interim=analyze_stage_a(rows,contract)
            if str(interim.get("status") or "").startswith("EARLY_STOP"):stop=True
    analysis=analyze_stage_a(rows,contract) if stage=="A" else analyze_stage_b(rows,contract,stage_a)
    analysis["new_rows_this_invocation"]=new_rows
    analysis_path=output_dir/f"stage-{stage.lower()}-analysis.json";analysis_path.write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest={"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":stage,"contract_sha256":contract["contract_sha256"],"raw_sha256":_sha_file(raw_path),"analysis_sha256":_sha_file(analysis_path),"rows":len(rows),"placebo_audit":placebo_audit,"model":contract["service_model"],"elapsed_hours_this_invocation":(time.monotonic()-started)/3600,"scientific_authority":False}
    (output_dir/f"stage-{stage.lower()}-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return analysis


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("phase",choices=("compile","run-a","run-b","analyze-a","analyze-b"));parser.add_argument("--source-memories",type=Path,required=True);parser.add_argument("--historical-runs-root",type=Path,required=True);parser.add_argument("--alfworld-root",type=Path,required=True);parser.add_argument("--config",type=Path,required=True);parser.add_argument("--model-receipt",type=Path,required=True);parser.add_argument("--service-base-url",default=DEFAULT_BASE_URL);parser.add_argument("--contract",type=Path,required=True);parser.add_argument("--output-dir",type=Path);parser.add_argument("--max-new-rows",type=int,default=0);args=parser.parse_args()
    if args.phase=="compile":
        contract=compile_contract(source_memories_path=args.source_memories,historical_runs_root=args.historical_runs_root,alfworld_root=args.alfworld_root,alfworld_config=args.config,service_base_url=args.service_base_url,model_receipt_path=args.model_receipt);args.contract.parent.mkdir(parents=True,exist_ok=True);args.contract.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"FROZEN","contract_sha256":contract["contract_sha256"],"memory_pool":contract["memory_pool"],"stage_a":contract["stage_a"],"stage_b":contract["stage_b"]},ensure_ascii=False,indent=2));return
    if args.output_dir is None:parser.error("--output-dir required")
    if args.phase in {"run-a","run-b"}:
        args.output_dir.mkdir(parents=True,exist_ok=True)
        with (args.output_dir/"transaction.lock").open("a+",encoding="utf-8") as lock:
            try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                print(json.dumps({"status":"TRANSACTION_ALREADY_RUNNING","experiment_id":EXPERIMENT_ID},ensure_ascii=False));return
            result=run_stage(stage="A" if args.phase=="run-a" else "B",contract_path=args.contract,source_memories_path=args.source_memories,alfworld_root=args.alfworld_root,alfworld_config=args.config,model_receipt_path=args.model_receipt,service_base_url=args.service_base_url,output_dir=args.output_dir,max_new_rows=max(0,args.max_new_rows))
    else:
        contract=json.loads(args.contract.read_text(encoding="utf-8"));stage="A" if args.phase=="analyze-a" else "B";rows=_read_jsonl(args.output_dir/f"stage-{stage.lower()}-raw.jsonl")
        result=analyze_stage_a(rows,contract) if stage=="A" else analyze_stage_b(rows,contract,json.loads((args.output_dir/"stage-a-analysis.json").read_text(encoding="utf-8")))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
