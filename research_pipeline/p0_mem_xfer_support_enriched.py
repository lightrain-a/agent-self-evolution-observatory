from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import p0_alfworld_adapter as _adapter_module
from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config

EXPERIMENT_ID = "P0-MEM-XFER-SUPPORT-ENRICHED"
RUN_ID = "p0-mem-xfer-support-enriched-qwen-v1"
FAMILIES = (
    "pick_and_place_simple",
    "pick_clean_then_place_in_recep",
    "pick_cool_then_place_in_recep",
    "pick_heat_then_place_in_recep",
)
ARMS = ("retrieved", "no-memory", "placebo")
PLACEBO_TEXT = (
    "Prior experience: compare calendar entries, copy the later date into a note, verify each month name, "
    "sort the notes alphabetically, and record the final date in a table. Repeat the check before finishing. "
)
SUPPORT_GATES = {
    "minimum_controlled_nonzero": 6,
    "minimum_target_families_with_nonzero": 3,
    "requires_controlled_harm_and_benefit": True,
    "minimum_memory_candidates_with_nonzero": 4,
}
FULL_SUPPORT_GATES = {
    "minimum_candidates": 8,
    "minimum_replicated_harm_candidates": 2,
    "minimum_replicated_benefit_candidates": 2,
    "replicated_effect_minimum_nonzero_units": 2,
    "candidate_level_independent_future_evaluation_required": True,
    "minimum_nonzero_controlled_effects": 12,
    "minimum_target_family_folds_with_two_nonzero": 3,
}

class SupportP0Error(RuntimeError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _hash(seed: int, *parts: object) -> str:
    return hashlib.sha256("|".join([str(seed), *map(str, parts)]).encode("utf-8")).hexdigest()
def _json_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _critical_source_snapshot() -> dict[str, dict[str, str]]:
    paths = {
        "p0_mem_xfer_support_enriched": Path(__file__).resolve(),
        "p0_alfworld_adapter": Path(str(_adapter_module.__file__)).resolve(),
    }
    return {name: {"path": str(path), "sha256": _file_hash(path)} for name, path in paths.items()}

def _snapshot_hashes(snapshot: dict[str, Any]) -> dict[str, str]:
    return {name: str((row or {}).get("sha256") or "") for name, row in snapshot.items()}

LOADED_SOURCE_SNAPSHOT = _critical_source_snapshot()

def _assert_loaded_sources_match_audit(audit: dict[str, Any]) -> None:
    expected = _snapshot_hashes(audit.get("source_snapshot") or {})
    loaded = _snapshot_hashes(LOADED_SOURCE_SNAPSHOT)
    if not expected or expected != loaded:
        raise SupportP0Error(f"loaded source snapshot mismatch: expected={expected}, loaded={loaded}")

def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n"); handle.flush()

def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

@contextmanager
def _exclusive_run_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise SupportP0Error(f"duplicate-process-lock-held: {path}") from error
        handle.seek(0); handle.truncate(0)
        handle.write(json.dumps({"pid": os.getpid(), "locked_at": _now()}) + "\n"); handle.flush()
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
def _load_trace_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line); trace = payload.get("trace") if isinstance(payload, dict) else None
                row = dict(trace) if isinstance(trace, dict) else dict(payload)
                row.setdefault("task_family", payload.get("family") if isinstance(payload, dict) else None)
                rows.append(row)
    return rows
def _task(row: dict[str, Any]) -> str:
    return str(row.get("task_id") or row.get("gamefile") or "")
def _family(row: dict[str, Any]) -> str:
    return str(row.get("task_family") or task_family_from_gamefile(_task(row)))
def _success(row: dict[str, Any]) -> int:
    return int(row.get("success") or row.get("won") or 0)
def _memory_text(row: dict[str, Any], memory_id: str) -> str:
    actions = []
    for raw in row.get("actions") or []:
        action = " ".join(str(raw).split())
        if action and (not actions or actions[-1] != action):
            actions.append(action)
    if len(actions) > 16:
        actions = actions[:8] + actions[-8:]
    steps = "\n".join(f"{index + 1}. {action}" for index, action in enumerate(actions))
    return (
        f"Experience {memory_id}. Goal pattern: {_family(row)}.\n"
        "A previous successful episode used this procedure:\n"
        f"{steps or '1. Track the goal and choose only admissible actions.'}\n"
        "Use it only when it fits the current goal and state."
    )

def _prior_tasks(signal_plan: Path, full_plan: Path) -> set[str]:
    excluded: set[str] = set()
    for path in (signal_plan, full_plan):
        plan = _load_json(path)
        excluded.update(str(row["source_task_id"]) for row in plan.get("source_memories") or [])
        excluded.update(str(row["target_task_id"]) for row in plan.get("units") or [])
    return excluded

def _prior_source_tasks(signal_plan: Path, full_plan: Path) -> set[str]:
    source_tasks: set[str] = set()
    for path in (signal_plan, full_plan):
        plan = _load_json(path)
        source_tasks.update(str(row["source_task_id"]) for row in plan.get("source_memories") or [])
    return source_tasks

def _select_memories(rows: list[dict[str, Any]], excluded: set[str], seed: int) -> list[dict[str, Any]]:
    memories: list[dict[str, Any]] = []
    for family in FAMILIES:
        candidates = sorted(
            [row for row in rows if _family(row) == family and _success(row) == 1 and _task(row) not in excluded],
            key=lambda row: _hash(seed, "source-memory", family, _task(row)),
        )
        if len(candidates) < 3:
            raise SupportP0Error(f"need 3 fresh successful source trajectories for {family}; found {len(candidates)}")
        for index, source in enumerate(candidates[:3], 1):
            memory_id = f"se-m-{family}-{index}"
            memories.append({
                "memory_id": memory_id,
                "source_family": family,
                "candidate_index": index,
                "candidate_role": "development" if index <= 2 else "heldout_candidate",
                "source_task_id": _task(source),
                "text": _memory_text(source, memory_id),
            })
    return memories

def _target_schedule(source_index: int, candidate_index: int) -> list[str]:
    # Two same-family slots plus all three cross-family boundaries; the sixth
    # repeats a different cross-family per candidate. Across all 12 candidates
    # this yields exactly 18 units for each of the four target families.
    return [
        FAMILIES[source_index], FAMILIES[source_index],
        FAMILIES[(source_index + 1) % 4], FAMILIES[(source_index + 2) % 4],
        FAMILIES[(source_index + 3) % 4], FAMILIES[(source_index + candidate_index) % 4],
    ]

def _target_pools(runner: ALFWorldGameRunner, excluded: set[str], seed: int) -> dict[str, dict[str, list[str]]]:
    available = runner.available_game_files("eval_out_of_distribution")
    pools: dict[str, dict[str, list[str]]] = {}
    for family in FAMILIES:
        eligible = sorted(
            [task for task in available if task_family_from_gamefile(task) == family and task not in excluded],
            key=lambda task: _hash(seed, "fresh-target", family, task),
        )
        if len(eligible) < 8:
            raise SupportP0Error(f"need >=8 fresh outcome-independent target tasks for {family}; found {len(eligible)}")
        pools[family] = {"probe_development": eligible[:4], "future_eval": eligible[4:8]}
    return pools

def _choose_target(pool: list[str], seed: int, memory_id: str, slot: int, used_within_candidate: set[str]) -> str:
    ordered = sorted(pool, key=lambda task: _hash(seed, "candidate-target", memory_id, slot, task))
    choice = next((task for task in ordered if task not in used_within_candidate), None)
    if choice is None:
        raise SupportP0Error(f"cannot assign distinct candidate target for {memory_id} slot={slot}")
    used_within_candidate.add(choice)
    return choice

def build_plan_material(
    *, qualification_traces: list[Path], signal_plan: Path, full_plan: Path,
    alfworld_config: Path, seed: int = 20260811,
) -> dict[str, Any]:
    traces = _load_trace_rows(qualification_traces)
    prior = _prior_tasks(signal_plan, full_plan)
    # Source candidates are selected only from successful qualification trajectories.
    # Prior treatment outcomes are never consulted. Old source-memory trajectories are
    # excluded so every new candidate memory is treatment-fresh; a trajectory that only
    # appeared as an old target may remain eligible because its treatment outcome is not read.
    memories = _select_memories(traces, _prior_source_tasks(signal_plan, full_plan), seed)
    source_tasks = {str(row["source_task_id"]) for row in memories}
    runner = ALFWorldGameRunner(load_config(alfworld_config))
    pools = _target_pools(runner, prior | source_tasks, seed)
    units: list[dict[str, Any]] = []
    by_family = {family: index for index, family in enumerate(FAMILIES)}
    for memory in memories:
        source_index = by_family[str(memory["source_family"])]
        candidate_index = int(memory["candidate_index"])
        schedule = _target_schedule(source_index, candidate_index)
        used: set[str] = set()
        for slot, target_family in enumerate(schedule):
            evaluation_role = "probe_development" if slot in {0, 2, 4} else "future_eval"
            task = _choose_target(pools[target_family][evaluation_role], seed, str(memory["memory_id"]), slot, used)
            units.append({
                "unit_id": f"{memory['memory_id']}-u{slot + 1:02d}",
                "memory_id": memory["memory_id"], "source_family": memory["source_family"],
                "candidate_index": candidate_index, "candidate_role": memory["candidate_role"],
                "target_family": target_family, "target_task_id": task,
                "relation": "same-family" if target_family == memory["source_family"] else "cross-family",
                "evaluation_role": evaluation_role,
                "support_qualification_open": memory["candidate_role"] == "development" and evaluation_role == "probe_development",
                "arm_order": sorted(ARMS, key=lambda arm: _hash(seed, "arm", memory["memory_id"], task, arm)),
            })
    support_units = [row for row in units if row["support_qualification_open"]]
    target_counts = Counter(str(row["target_family"]) for row in units)
    support_target_counts = Counter(str(row["target_family"]) for row in support_units)
    if len(memories) != 12 or len(units) != 72 or len(support_units) != 24:
        raise SupportP0Error(
            f"plan cardinality mismatch: memories={len(memories)}, full={len(units)}, support={len(support_units)}"
        )
    if set(target_counts.values()) != {18} or set(support_target_counts.values()) != {6}:
        raise SupportP0Error(
            f"target-family balance failed: full={target_counts}, support={support_target_counts}"
        )
    if any(
        row["candidate_role"] == "heldout_candidate" and row["support_qualification_open"]
        for row in units
    ):
        raise SupportP0Error("held-out candidate leaked into support qualification")
    return {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
        "seed": seed, "split": "eval_out_of_distribution", "arms": list(ARMS),
        "source_families": list(FAMILIES), "target_families": list(FAMILIES),
        "source_memories": memories, "target_pools": pools, "units": units,
        "support_qualification_unit_ids": [row["unit_id"] for row in support_units],
        "full_units": 72, "full_executions": 216,
        "support_qualification_units": 24, "support_qualification_executions": 72,
        "candidate_split_rule": (
            "candidate 1/2 per source family are development; candidate 3 is completely held out "
            "from support qualification"
        ),
        "target_split_rule": (
            "each candidate freezes exactly 3 probe_development and 3 future_eval targets; "
            "probe and future target pools are disjoint within each target family"
        ),
        "target_selection_rule": (
            "deterministic hash over ALFWorld OOD game-file identity after excluding prior "
            "signal/full/source-memory tasks; no current-model success, treatment outcome, "
            "or preliminary effect is read"
        ),
        "target_reuse_rule": (
            "fresh targets may be reused across memory candidates within the same frozen split "
            "for matched comparisons; targets are distinct within each candidate"
        ),
        "independent_truth": "ALFWorld environment success/won; no LLM judge supplies outcome truth",
        "memory_renderer_contract": (
            "bit-for-bit algorithmic continuation of the server-60 P0-MEM-XFER-CAUSAL renderer; "
            "no text strengthening"
        ),
        "support_gates": SUPPORT_GATES,
        "typed_outcome": "SUPPORT_QUALIFICATION_HOLD is support/identifiability evidence, not METHOD-FAIL",
        "qualification_trace_files": [str(path) for path in qualification_traces],
        "excluded_signal_plan": str(signal_plan), "excluded_full_plan": str(full_plan),
    }

def plan_hash(material: dict[str, Any]) -> str:
    return _json_hash(material)

def _renderer_parity(qualification_traces: list[Path], old_full_plan: Path) -> dict[str, Any]:
    rows = _load_trace_rows(qualification_traces)
    by_task = {_task(row): row for row in rows}
    old_plan = _load_json(old_full_plan)
    comparisons = []
    for memory in old_plan.get("source_memories") or []:
        task = str(memory["source_task_id"])
        source = by_task.get(task)
        rendered = _memory_text(source, str(memory["memory_id"])) if source else None
        expected = str(memory.get("text") or "")
        comparisons.append({
            "memory_id": memory["memory_id"], "source_task_id": task,
            "source_trace_found": source is not None,
            "exact_text_match": rendered == expected if source is not None else False,
            "expected_sha256": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
            "rendered_sha256": hashlib.sha256((rendered or "").encode("utf-8")).hexdigest(),
        })
    return {
        "pass": bool(comparisons) and all(row["source_trace_found"] and row["exact_text_match"] for row in comparisons),
        "comparisons": comparisons,
    }

def build_pre_gpu_audit(
    *, material: dict[str, Any], qualification_summary: Path,
    qualification_traces: list[Path], signal_plan: Path, old_full_plan: Path,
    offline_decision: Path, transport_analysis: Path, novelty_evidence: Path,
    old_full_cost: Path, runtime_python: Path, model_path: Path,
    alfworld_data: Path, extra_site: Path,
) -> dict[str, Any]:
    qualification = _load_json(qualification_summary)
    offline = _load_json(offline_decision)
    transport = _load_json(transport_analysis)
    novelty = _load_json(novelty_evidence)
    observed = offline.get("full_qwen_observed") or {}
    support = transport.get("support") or {}
    parity = _renderer_parity(qualification_traces, old_full_plan)
    family_stats = qualification.get("task_families") or {}
    competence = {
        family: {
            "success": int((family_stats.get(family) or {}).get("success") or 0),
            "n": int((family_stats.get(family) or {}).get("n") or 0),
        }
        for family in FAMILIES
    }
    for row in competence.values():
        row["rate"] = row["success"] / row["n"] if row["n"] else 0.0
    prior = _prior_tasks(signal_plan, old_full_plan)
    source_tasks = {str(row["source_task_id"]) for row in material["source_memories"]}
    target_tasks = {str(row["target_task_id"]) for row in material["units"]}
    split_disjoint = all(
        set(material["target_pools"][family]["probe_development"]).isdisjoint(
            material["target_pools"][family]["future_eval"]
        ) for family in FAMILIES
    )
    no_target_leak = target_tasks.isdisjoint(prior | source_tasks)
    no_candidate_leak = not any(
        row["candidate_role"] == "heldout_candidate" and row["support_qualification_open"]
        for row in material["units"]
    )
    old_cost = _load_json(old_full_cost)
    prior_gpu_hours = float(old_cost.get("gpu_hours") or old_cost.get("wall_clock_hours") or 0.0)
    prior_calls = int(old_cost.get("model_calls") or 0)
    prior_tokens = int(old_cost.get("tokens") or 0)
    scale = 72 / 96
    budget = {
        "support_executions": 72,
        "episode_cap": 72,
        "hard_wall_hours": 2.0,
        "estimated_gpu_hours_from_frozen_full": prior_gpu_hours * scale,
        "estimated_model_calls_from_frozen_full": round(prior_calls * scale),
        "estimated_tokens_from_frozen_full": round(prior_tokens * scale),
        "reference_full_gpu_hours": prior_gpu_hours,
        "reference_full_executions": 96,
    }
    runtime_ok = (
        Path(runtime_python).exists()
        and Path(model_path).exists()
        and Path(alfworld_data).exists()
        and Path(extra_site).exists()
        and Path(sys.executable).resolve() == Path(runtime_python).resolve()
        and str(qualification.get("model_path") or "") == str(model_path)
        and os.environ.get("ALFWORLD_DATA", "") == str(alfworld_data)
        and os.environ.get("P0_EXTRA_SITE", "") == str(extra_site)
    )
    loto = transport.get("strongest_simplification") or {}
    checks = [
        {
            "rank": 1, "key": "novelty_collision",
            "pass": novelty.get("status") == "PASS_WITH_NARROWING" and novelty.get("support_experiment_authorized") is True and novelty.get("paper_method_novelty_authorized") is False,
            "evidence": novelty,
        },
        {
            "rank": 2, "key": "real_problem",
            "pass": int(observed.get("placebo_nonzero") or 0) >= 1 and int(observed.get("controlled_nonzero") or 0) >= 1,
            "evidence": {"placebo_nonzero": observed.get("placebo_nonzero"), "controlled_nonzero": observed.get("controlled_nonzero")},
        },
        {
            "rank": 3, "key": "base_agent_competence",
            "pass": bool((qualification.get("gate") or {}).get("passed")) and all(row["rate"] >= 0.20 for row in competence.values()),
            "evidence": {"overall": {"success": qualification.get("successes"), "n": qualification.get("num_envs"), "rate": qualification.get("success_rate")}, "families": competence},
        },
        {
            "rank": 4, "key": "phenomenon_existence",
            "pass": int(observed.get("outcome_disagreement") or 0) >= 2 and int(support.get("controlled_harm") or 0) > 0 and int(support.get("controlled_benefit") or 0) > 0,
            "evidence": {"outcome_disagreement": observed.get("outcome_disagreement"), "controlled_harm": support.get("controlled_harm"), "controlled_benefit": support.get("controlled_benefit")},
        },
        {
            "rank": 5, "key": "independent_truth",
            "pass": material.get("independent_truth") == "ALFWorld environment success/won; no LLM judge supplies outcome truth",
            "evidence": material.get("independent_truth"),
        },
        {
            "rank": 6, "key": "manipulation_validity",
            "pass": parity["pass"] is True and list(material.get("arms") or []) == list(ARMS),
            "evidence": {"renderer_parity": parity, "arms": material.get("arms"), "placebo": "token matched within one tokenizer token at runtime"},
        },
        {
            "rank": 7, "key": "shortcut_leakage",
            "pass": no_target_leak and no_candidate_leak and split_disjoint,
            "evidence": {"fresh_targets_vs_prior_and_sources": no_target_leak, "heldout_candidate_closed": no_candidate_leak, "probe_future_pools_disjoint": split_disjoint, "selection_reads_treatment_outcomes": False},
        },
        {
            "rank": 8, "key": "matched_simplification",
            "pass": loto.get("name") == "source-family mean LOTO" and int(loto.get("covered") or 0) == 4 and int(loto.get("covered_sign_correct") or 0) == 4,
            "evidence": {"current_strongest": {key: loto.get(key) for key in ("name", "evaluated_nonzero_effects", "covered", "coverage", "covered_sign_correct", "covered_sign_accuracy")}, "idea3_baselines": ["no-memory", "write-all memory", "two-arm shrinkage", "placebo-calibrated three-arm gate", "candidate mean/confidence threshold"], "idea5_baselines": ["semantic similarity", "source-family mean LOTO", "source-family causal effect only", "nearest-family/task-signature", "cross-fitted treatment-effect/R-learner-style", "proposed transport certificate"]},
        },
        {
            "rank": 9, "key": "support_identifiability",
            "pass": len(material["source_memories"]) == 12 and len(material["support_qualification_unit_ids"]) == 24 and len(material["units"]) == 72 and sum(row["candidate_role"] == "heldout_candidate" for row in material["source_memories"]) == 4,
            "evidence": {"candidates": len(material["source_memories"]), "support_units": len(material["support_qualification_unit_ids"]), "full_units": len(material["units"]), "heldout_candidates": sum(row["candidate_role"] == "heldout_candidate" for row in material["source_memories"]), "support_target_family_counts": dict(Counter(row["target_family"] for row in material["units"] if row["support_qualification_open"]))},
        },
        {
            "rank": 10, "key": "budget_sufficiency",
            "pass": budget["support_executions"] == 72 and 0 < budget["estimated_gpu_hours_from_frozen_full"] < budget["hard_wall_hours"],
            "evidence": budget,
        },
        {
            "rank": 11, "key": "runtime_model_path_consistency",
            "pass": runtime_ok,
            "evidence": {"runtime_python": str(runtime_python), "current_python": sys.executable, "model_path": str(model_path), "qualified_model_path": qualification.get("model_path"), "alfworld_data": str(alfworld_data), "extra_site": str(extra_site)},
        },
        {
            "rank": 12, "key": "frozen_stop_expand_gates",
            "pass": material.get("support_gates") == SUPPORT_GATES and offline.get("workflow_decision") == "EXPAND" and offline.get("second_model_authorized") is False,
            "evidence": {"support_gates": material.get("support_gates"), "offline_workflow_decision": offline.get("workflow_decision"), "second_model_authorized": offline.get("second_model_authorized"), "hold_is_method_failure": False},
        },
    ]
    blockers = [row["key"] for row in checks if not row["pass"]]
    return {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID,
        "audit_id": "p0-mem-xfer-support-enriched-pre-gpu-v1", "created_at": _now(),
        "decision": "PASS" if not blockers else "HOLD", "execution_ready": not blockers,
        "blockers": blockers, "checks": checks, "preview_plan_hash": plan_hash(material),
        "source_snapshot": _critical_source_snapshot(),
        "provenance_contract": {
            "exclusive_lock_before_model_load": True,
            "loaded_source_sha_must_match_pre_gpu_audit": True,
            "duplicate_process_contaminates_run": True,
        },
        "scientific_authority": "Authorizes only the 24-unit/72-execution Qwen support qualification; it does not authorize a method PASS or a second backbone.",
        "typed_failure_policy": ["METHOD-FAIL", "PHENOMENON-FAIL", "SUPPORT-INSUFFICIENT", "COMPETENCE-FAIL", "RUNTIME-BLOCKER", "BUDGET-STOP", "HOLD", "INCONCLUSIVE"],
    }

def write_frozen_plan(material: dict[str, Any], audit_path: Path, run_dir: Path) -> dict[str, Any]:
    audit = _load_json(audit_path)
    frozen_hash = plan_hash(material)
    if audit.get("decision") != "PASS" or audit.get("execution_ready") is not True:
        raise SupportP0Error("pre-GPU audit did not PASS; refusing to generate frozen plan")
    if str(audit.get("preview_plan_hash") or "") != frozen_hash:
        raise SupportP0Error("plan changed after pre-GPU audit; refusing to freeze")
    if run_dir.exists() and any(run_dir.iterdir()):
        raise SupportP0Error(f"refusing to overwrite non-empty run directory: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = {**material, "created_at": _now(), "plan_hash": frozen_hash, "pre_gpu_audit": str(audit_path), "pre_gpu_audit_sha256": _file_hash(audit_path), "immutable_after_creation": True}
    _atomic_json(run_dir / "plan.json", payload)
    _write_jsonl(run_dir / "source-memories.jsonl", list(material["source_memories"]))
    _write_jsonl(run_dir / "full-treatment-plan.jsonl", list(material["units"]))
    support = [row for row in material["units"] if row["support_qualification_open"]]
    _write_jsonl(run_dir / "support-qualification-plan.jsonl", support)
    manifest = {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID, "plan_hash": frozen_hash, "pre_gpu_audit_sha256": _file_hash(audit_path), "source_memories": 12, "full_units": 72, "full_executions": 216, "support_qualification_units": 24, "support_qualification_executions": 72, "second_model_authorized": False}
    _atomic_json(run_dir / "manifest.json", manifest)
    (run_dir / "PLAN_SHA256").write_text(frozen_hash + "\n", encoding="utf-8")
    return {"run_dir": str(run_dir), "plan_hash": frozen_hash, "support_units": len(support), "support_executions": len(support) * len(ARMS)}

def _token_matched_placebo(policy: HFAdmissiblePolicy, memory: str) -> tuple[str, int, int]:
    target = policy.token_count(memory)
    corpus = PLACEBO_TEXT
    while len(policy.tokenizer.encode(corpus, add_special_tokens=False)) < target + 12:
        corpus += PLACEBO_TEXT
    ids = policy.tokenizer.encode(corpus, add_special_tokens=False)
    best = ("", 0, 10**9)
    for length in range(max(1, target - 8), min(len(ids), target + 8) + 1):
        text = policy.tokenizer.decode(ids[:length], skip_special_tokens=True).strip()
        count = policy.token_count(text); gap = abs(count - target)
        if gap < best[2]:
            best = (text, count, gap)
        if gap == 0:
            break
    if best[2] > 1:
        raise SupportP0Error(f"token-matched placebo unavailable: memory={target}, placebo={best[1]}")
    return best[0], target, best[1]

def _usage_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {key: int(after.get(key, 0)) - int(before.get(key, 0)) for key in set(before) | set(after)}

def _verified_material(plan: dict[str, Any]) -> dict[str, Any]:
    material = {key: value for key, value in plan.items() if key not in {"created_at", "plan_hash", "pre_gpu_audit", "pre_gpu_audit_sha256", "immutable_after_creation"}}
    actual = plan_hash(material)
    if actual != str(plan.get("plan_hash") or ""):
        raise SupportP0Error(f"frozen plan hash mismatch: {actual} != {plan.get('plan_hash')}")
    return material

def analyze_support_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[str(row["unit_id"])][str(row["arm"])] = row
    units = []
    for unit_id, arms in sorted(grouped.items()):
        if not all(arm in arms for arm in ARMS):
            continue
        retrieved = int(arms["retrieved"]["success"]); no_memory = int(arms["no-memory"]["success"]); placebo = int(arms["placebo"]["success"])
        base = arms["retrieved"]
        units.append({
            "unit_id": unit_id, "memory_id": base["memory_id"], "source_family": base["source_family"],
            "target_family": base["target_family"], "target_task_id": base["target_task_id"],
            "retrieved_success": retrieved, "no_memory_success": no_memory, "placebo_success": placebo,
            "retrieved_delta": retrieved - no_memory, "placebo_delta": placebo - no_memory,
            "controlled_delta": retrieved - placebo, "outcome_disagreement": len({retrieved, no_memory, placebo}) > 1,
        })
    nonzero = [row for row in units if row["controlled_delta"] != 0]
    family_nonzero = sorted({row["target_family"] for row in nonzero})
    memory_nonzero = sorted({row["memory_id"] for row in nonzero})
    harm = sum(row["controlled_delta"] < 0 for row in units); benefit = sum(row["controlled_delta"] > 0 for row in units)
    checks = {
        "controlled_nonzero": {"required": 6, "actual": len(nonzero), "pass": len(nonzero) >= 6},
        "target_families_with_nonzero": {"required": 3, "actual": len(family_nonzero), "pass": len(family_nonzero) >= 3},
        "controlled_harm_and_benefit": {"required": True, "actual": harm > 0 and benefit > 0, "pass": harm > 0 and benefit > 0},
        "memory_candidates_with_nonzero": {"required": 4, "actual": len(memory_nonzero), "pass": len(memory_nonzero) >= 4},
    }
    passed = len(units) == 24 and all(item["pass"] for item in checks.values())
    diagnostics = []
    if len(nonzero) < 6: diagnostics.append("support_sparsity")
    if len(family_nonzero) < 3: diagnostics.append("task_family_concentration")
    if not (harm > 0 and benefit > 0): diagnostics.append("intervention_sign_asymmetry")
    if len(memory_nonzero) < 4: diagnostics.append("candidate_diversity_insufficient")
    return {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "support-qualification",
        "complete_units": len(units), "complete_executions": len(units) * 3,
        "controlled_nonzero": len(nonzero), "controlled_harm": harm, "controlled_benefit": benefit,
        "target_families_with_nonzero": family_nonzero, "memory_candidates_with_nonzero": memory_nonzero,
        "gate_checks": checks, "decision": "SUPPORT_QUALIFICATION_PASS" if passed else "SUPPORT_QUALIFICATION_HOLD",
        "method_failure_authorized": False, "second_model_authorized": False,
        "diagnostics_if_hold": diagnostics,
        "next_action": "Open the frozen 72-unit full Qwen support table; keep second backbone on HOLD." if passed else "Do not expand GPU budget; diagnose support sparsity, family concentration, intervention strength, and candidate diversity without changing frozen thresholds.",
        "unit_rows": units,
    }

def _run_support_qualification_unlocked(
    *, run_dir: Path, alfworld_config: Path, model_path: Path,
    output_dir: Path, gpu_uuid: str, max_steps: int = 50,
    episode_cap: int = 72, wall_hours_cap: float = 2.0,
) -> dict[str, Any]:
    plan = _load_json(run_dir / "plan.json")
    material = _verified_material(plan)
    audit = _load_json(Path(str(plan["pre_gpu_audit"])))
    if audit.get("decision") != "PASS" or audit.get("preview_plan_hash") != plan["plan_hash"]:
        raise SupportP0Error("frozen pre-GPU audit no longer authorizes this plan")
    _assert_loaded_sources_match_audit(audit)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SupportP0Error(f"refusing to overwrite non-empty support qualification directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    support_ids = set(material["support_qualification_unit_ids"])
    units = [row for row in material["units"] if row["unit_id"] in support_ids]
    if len(units) != 24 or episode_cap != 72:
        raise SupportP0Error(f"support budget contract mismatch: units={len(units)}, episode_cap={episode_cap}")
    memory_map = {str(row["memory_id"]): row for row in material["source_memories"]}
    _atomic_json(output_dir / "manifest.json", {
        "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "support-qualification",
        "plan_hash": plan["plan_hash"], "model_path": str(model_path), "gpu_uuid": gpu_uuid,
        "max_steps": max_steps, "episode_cap": episode_cap, "wall_hours_cap": wall_hours_cap,
        "arms": list(ARMS), "independent_truth": material["independent_truth"],
        "loaded_source_snapshot": LOADED_SOURCE_SNAPSHOT,
        "method_failure_authorized": False, "second_model_authorized": False,
    })
    raw_path = output_dir / "raw-traces.jsonl"; raw_path.write_text("", encoding="utf-8")
    _atomic_json(output_dir / "progress.json", {
        "schema_version": "1.0", "status": "support_qualification_running", "completed_episodes": 0,
        "total_episodes": 72, "completed_units": 0, "total_units": 24, "gpu_uuid": gpu_uuid, "updated_at": _now(),
    })
    runner = ALFWorldGameRunner(load_config(alfworld_config))
    policy = HFAdmissiblePolicy(model_path, policy_mode="react-family")
    placebo_cache: dict[str, tuple[str, int, int]] = {}
    records: list[dict[str, Any]] = []
    started = time.monotonic()
    try:
        for unit_index, unit in enumerate(units, 1):
            memory_id = str(unit["memory_id"]); memory = str(memory_map[memory_id]["text"])
            if memory_id not in placebo_cache:
                placebo_cache[memory_id] = _token_matched_placebo(policy, memory)
            placebo, memory_tokens, placebo_tokens = placebo_cache[memory_id]
            for arm in unit["arm_order"]:
                elapsed = (time.monotonic() - started) / 3600.0
                if len(records) >= episode_cap:
                    raise SupportP0Error(f"BUDGET_STOP episode cap reached: {len(records)} >= {episode_cap}")
                if elapsed >= wall_hours_cap:
                    raise SupportP0Error(f"BUDGET_STOP wall cap reached: {elapsed:.4f} >= {wall_hours_cap}")
                context = "" if arm == "no-memory" else "MEMORY::" + (memory if arm == "retrieved" else placebo)
                before = policy.usage_snapshot()
                trace = runner.run_game_file(material["split"], str(unit["target_task_id"]), policy, context, max_steps=max_steps)
                after = policy.usage_snapshot()
                record = {
                    "schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "support-qualification",
                    "unit_id": unit["unit_id"], "unit_index": unit_index, "arm": arm,
                    "memory_id": memory_id, "source_family": unit["source_family"],
                    "target_family": unit["target_family"], "target_task_id": unit["target_task_id"],
                    "candidate_index": unit["candidate_index"], "candidate_role": unit["candidate_role"],
                    "evaluation_role": unit["evaluation_role"],
                    "memory_token_count": memory_tokens, "placebo_token_count": placebo_tokens,
                    "token_match_gap": abs(memory_tokens - placebo_tokens),
                    "success": int(trace.get("success") or trace.get("won") or 0),
                    "score": float(trace.get("score") or 0.0), "steps": int(trace.get("steps") or 0),
                    "invalid_actions": int(trace.get("invalid_actions") or 0), "actions": trace.get("actions") or [],
                    "usage": _usage_delta(before, after), "recorded_at": _now(),
                }
                records.append(record); _append_jsonl(raw_path, record)
                _atomic_json(output_dir / "progress.json", {
                    "schema_version": "1.0", "status": "support_qualification_running",
                    "completed_episodes": len(records), "total_episodes": 72,
                    "completed_units": len(records) // 3, "total_units": 24,
                    "current_unit": unit["unit_id"], "current_arm": arm,
                    "elapsed_hours": (time.monotonic() - started) / 3600.0,
                    "model_calls": int(policy.usage_snapshot().get("generation_calls") or 0),
                    "gpu_uuid": gpu_uuid, "updated_at": _now(),
                })
    except Exception as error:
        kind = "BUDGET-STOP" if str(error).startswith("BUDGET_STOP") else "RUNTIME-BLOCKER"
        _atomic_json(output_dir / "runtime-error.json", {"error_type": type(error).__name__, "typed_outcome": kind, "message": str(error), "scientific_result_available": False, "method_failure_authorized": False, "recorded_at": _now()})
        _atomic_json(output_dir / "progress.json", {"schema_version": "1.0", "status": "budget-stop" if kind == "BUDGET-STOP" else "runtime-blocker", "completed_episodes": len(records), "total_episodes": 72, "scientific_result_available": False, "method_failure_authorized": False, "error": str(error), "gpu_uuid": gpu_uuid, "updated_at": _now()})
        raise
    analysis = analyze_support_rows(records)
    elapsed = (time.monotonic() - started) / 3600.0
    usage = policy.usage_snapshot()
    cost = {"gpu_hours": elapsed, "wall_clock_hours": elapsed, "environment_episodes": len(records), "model_calls": int(usage.get("generation_calls") or 0), "input_tokens": int(usage.get("input_tokens") or 0), "output_tokens": int(usage.get("output_tokens") or 0), "tokens": int(usage.get("tokens") or 0), "accounting_consistent": True}
    _atomic_json(output_dir / "analysis.json", analysis)
    _atomic_json(output_dir / "cost.json", cost)
    _atomic_json(output_dir / "decision.json", {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "support-qualification", "decision": analysis["decision"], "gate_checks": analysis["gate_checks"], "diagnostics_if_hold": analysis["diagnostics_if_hold"], "method_failure_authorized": False, "second_model_authorized": False, "next_action": analysis["next_action"], "created_at": _now()})
    fields = ["unit_id", "memory_id", "source_family", "target_family", "target_task_id", "retrieved_success", "no_memory_success", "placebo_success", "retrieved_delta", "placebo_delta", "controlled_delta", "outcome_disagreement"]
    with (output_dir / "main_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in analysis["unit_rows"]:
            writer.writerow({key: row.get(key) for key in fields})
    terminal_status = "support_qualification_pass" if analysis["decision"] == "SUPPORT_QUALIFICATION_PASS" else "support_qualification_hold"
    _atomic_json(output_dir / "progress.json", {"schema_version": "1.0", "status": terminal_status, "completed_episodes": len(records), "total_episodes": 72, "completed_units": analysis["complete_units"], "total_units": 24, "decision": analysis["decision"], "elapsed_hours": elapsed, "model_calls": int(usage.get("generation_calls") or 0), "gpu_uuid": gpu_uuid, "method_failure_authorized": False, "second_model_authorized": False, "updated_at": _now()})
    return {"analysis": analysis, "cost": cost}


def run_support_qualification(
    *, run_dir: Path, alfworld_config: Path, model_path: Path,
    output_dir: Path, gpu_uuid: str, max_steps: int = 50,
    episode_cap: int = 72, wall_hours_cap: float = 2.0,
) -> dict[str, Any]:
    with _exclusive_run_lock(run_dir / ".support-qualification.lock"):
        return _run_support_qualification_unlocked(
            run_dir=run_dir, alfworld_config=alfworld_config, model_path=model_path,
            output_dir=output_dir, gpu_uuid=gpu_uuid, max_steps=max_steps,
            episode_cap=episode_cap, wall_hours_cap=wall_hours_cap,
        )


def _support_source_rows(run_dir: Path, plan: dict[str, Any], model_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    support_dir = run_dir / "support-qualification"
    decision = _load_json(support_dir / "decision.json")
    manifest = _load_json(support_dir / "manifest.json")
    if decision.get("decision") != "SUPPORT_QUALIFICATION_PASS":
        raise SupportP0Error("full stage requires SUPPORT_QUALIFICATION_PASS")
    if str(manifest.get("plan_hash") or "") != str(plan.get("plan_hash") or ""):
        raise SupportP0Error("support/full plan hash mismatch")
    if str(manifest.get("model_path") or "") != str(model_path):
        raise SupportP0Error("support/full model path mismatch")
    rows = _load_jsonl(support_dir / "raw-traces.jsonl")
    material = _verified_material(plan)
    support_ids = set(material["support_qualification_unit_ids"])
    expected = {(str(unit_id), arm) for unit_id in support_ids for arm in ARMS}
    actual = {(str(row.get("unit_id") or ""), str(row.get("arm") or "")) for row in rows}
    if len(rows) != 72 or len(actual) != 72 or actual != expected:
        raise SupportP0Error(f"support source integrity failed: rows={len(rows)}, unique={len(actual)}")
    if any(abs(int(row.get("token_match_gap") or 0)) > 1 for row in rows):
        raise SupportP0Error("support source contains placebo token mismatch")
    return rows, {
        "support_decision_sha256": _file_hash(support_dir / "decision.json"),
        "support_raw_sha256": _file_hash(support_dir / "raw-traces.jsonl"),
        "support_cost_sha256": _file_hash(support_dir / "cost.json"),
        "reused_support_executions": len(rows),
        "reused_support_units": len(support_ids),
    }
