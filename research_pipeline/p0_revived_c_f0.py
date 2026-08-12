from __future__ import annotations
from datetime import datetime, timezone
import json, os
from pathlib import Path
from typing import Any
from .config import StorageSettings, resolve_experiment_data_root
from .p0_c_shared_bridge import build_shared_card

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _ck(status: str, evidence: str) -> dict[str, Any]:
    return {"status": status, "evidence": evidence, "evidence_kind": "pending"}

def _shared_analysis() -> dict[str, Any]:
    roots=[]
    if os.getenv("P0_C_SHARED_ROOT"): roots.append(Path(os.environ["P0_C_SHARED_ROOT"]))
    try: roots.append(resolve_experiment_data_root(StorageSettings.from_env())/"runs"/"p0-c-shared-substrate-v1")
    except Exception: pass
    roots.append(Path("/data/wyt/agent-self-evolution-p0-52-data/runs/p0-c-shared-substrate-v1"))
    for root in roots:
        path=root/"analysis.json"
        try: return json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): pass
    return {}

def _hold(code: str, idea_id: str, label: str, required: str, next_action: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0", "generated_at": _now(), "idea_id": idea_id, "code": code,
        "scientific_role": "real-trace substrate inventory F0; missing support is an upstream HOLD only",
        "substrate": {"kind": label, "available_standardized_rows": 0, "required": required},
        "substrate_inventory": {"observed_effective_candidates": 0, "observed_fresh_heldout": 0, "observed_reserve_fraction": 0.0},
        "checks": {
            "target_variation": _ck("pending", f"No standardized {label} artifact is available."),
            "baseline_disagreement": _ck("pending", "Matched baseline headroom requires a real trace table."),
            "representability": _ck("pending", "Synthetic traces cannot authorize a real self-evolution claim."),
            "tiny_overfit": _ck("pending", "No held-out source/failure split exists."),
            "competence_window": _ck("pending", "Real action stream not qualified."),
            "effect_variation": _ck("pending", "No real effect table exists."),
        },
        "updater_competence": {"status": "blocked-substrate", "passed": False, "reason": "real trace/action substrate missing"},
        "gpu0": {"status": "hold-substrate-real-traces-missing", "evidence": f"No standardized {label} table satisfying {required}.", "evidence_kind": "real-substrate-inventory", "next": next_action},
        "decision": "HOLD_REAL_TRACE_SUBSTRATE_MISSING", "method_failure_authorized": False,
        "execution_authorized": False, "next_action": next_action,
    }

def run_c1_f0() -> dict[str, Any]:
    shared=_shared_analysis(); row=shared.get("C-1") or {}
    if row: return build_shared_card("C-1","self-label-confidence-flow","C-1",row,shared,_now())
    return _hold("C-1", "self-label-confidence-flow", "4-6-round lineage-linked pseudo-label log", ">=200 label decisions with repeated and independent ancestors", "Collect/freeze 4-6 real self-label rounds with >=200 lineage-linked decisions, ancestor IDs, independent truth, and ancestor-held-out split; rerun same-feature direct/shallow baselines.")

def run_c4_f0() -> dict[str, Any]:
    shared=_shared_analysis(); row=shared.get("C-4") or {}
    if row: return build_shared_card("C-4","self-correction-collapse-detector","C-4",row,shared,_now())
    return _hold("C-4", "self-correction-collapse-detector", "multi-mode self-correction traces", ">=30 failures with >=3 correction modes and order effects", "Collect/freeze >=30 real failures with replan/retrieve/rewrite/rollback/stop, verifier deltas, <=3 rounds, and failure-family holdout; compare repetition caps and depth-3 CART.")

def run_c5_f0() -> dict[str, Any]:
    shared=_shared_analysis(); row=shared.get("C-5") or {}
    if row: return build_shared_card("C-5","intervention-validated-self-correction","C-5",row,shared,_now())
    return _hold("C-5", "intervention-validated-self-correction", "matched correction delete/insert interventions", ">=24 correction candidates plus future-task truth", "Collect/freeze >=24 persistent correction candidates with matched deletion/insertion interventions, 8 probes and 24 hidden tasks; compare A-3 and same-feature thresholds at matched accepted count.")
