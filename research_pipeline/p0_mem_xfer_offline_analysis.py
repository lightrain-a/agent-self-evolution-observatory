from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_mem_xfer_support_analysis import ensure_analysis as ensure_support_enriched_analysis

EXPERIMENT_ID = "P0-MEM-XFER-CAUSAL"
IDEA_3 = "replicated-effect-memory-gate"
IDEA_5 = "cross-task-effect-transport-certificate"
REPLICATED_GATE = {"minimum_candidates": 8, "minimum_replicated_harm_candidates": 2, "minimum_replicated_benefit_candidates": 2, "replicated_effect_minimum_nonzero_units": 2, "candidate_level_independent_future_evaluation_required": True}
TRANSPORT_GATE = {"minimum_nonzero_controlled_effects": 12, "minimum_target_family_folds_with_two_nonzero": 3, "minimum_nonzero_per_eligible_fold": 2}

class OfflineAnalysisError(RuntimeError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
def _sign(value: float) -> int:
    return 1 if value > 0 else (-1 if value < 0 else 0)
def _load_table(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise OfflineAnalysisError(f"missing immutable main table: {path}")
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            for key in ("retrieved_success", "no_memory_success", "placebo_success", "retrieved_delta", "placebo_delta", "controlled_delta"):
                row[key] = int(row[key])
            row["outcome_disagreement"] = str(row.get("outcome_disagreement") or "").lower() in {"1", "true", "yes"}
            rows.append(row)
    return rows
def _validate_run(run_dir: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = ["analysis.json", "cost.json", "decision.json", "main_table.csv", "progress.json", "raw-traces.jsonl"]
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise OfflineAnalysisError(f"frozen evidence set incomplete: {missing}")
    progress = json.loads((run_dir / "progress.json").read_text(encoding="utf-8"))
    if progress.get("status") != "complete" or int(progress.get("completed_episodes") or 0) != 96 or int(progress.get("completed_units") or 0) != 32 or len(rows) != 32:
        raise OfflineAnalysisError(f"frozen full table integrity failed: {progress}, rows={len(rows)}")
    return {"run_dir": str(run_dir.resolve()), "immutable": True, "completed_executions": 96, "completed_units": 32, "model_calls": int(progress.get("model_calls") or 0), "evidence_sha256": {name: _sha256(run_dir / name) for name in required}}

def _candidate_analysis(rows: list[dict[str, Any]], source: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["memory_id"])].append(row)
    candidates = []
    for memory_id in sorted(grouped):
        items = grouped[memory_id]
        effects = [int(row["controlled_delta"]) for row in items]
        harm = sum(v < 0 for v in effects); benefit = sum(v > 0 for v in effects)
        candidates.append({"memory_id": memory_id, "source_family": items[0]["source_family"], "n": len(items), "controlled_harm_units": harm, "controlled_benefit_units": benefit, "controlled_zero_units": sum(v == 0 for v in effects), "mean_controlled_effect": _mean(effects), "controlled_effect_histogram": {str(k): v for k, v in sorted(Counter(effects).items())}, "replicated_controlled_harm": harm >= 2, "replicated_controlled_benefit": benefit >= 2})
    changed = [row for row in rows if row["retrieved_delta"] != row["controlled_delta"]]
    transitions = Counter((row["retrieved_delta"], row["controlled_delta"]) for row in changed)
    harm_candidates = sum(row["replicated_controlled_harm"] for row in candidates)
    benefit_candidates = sum(row["replicated_controlled_benefit"] for row in candidates)
    checks = {"candidate_count": {"required": 8, "actual": len(candidates), "pass": len(candidates) >= 8}, "replicated_controlled_harm_candidates": {"required": 2, "actual": harm_candidates, "pass": harm_candidates >= 2}, "replicated_controlled_benefit_candidates": {"required": 2, "actual": benefit_candidates, "pass": benefit_candidates >= 2}, "candidate_level_independent_future_evaluation": {"required": True, "actual": False, "pass": False}}
    labels = {(-1, 0): "two-arm -1 -> controlled 0", (1, 0): "two-arm +1 -> controlled 0", (0, -1): "two-arm 0 -> controlled -1", (0, 1): "two-arm 0 -> controlled +1"}
    return {
        "schema_version": "1.0", "analysis_id": "p0-mem-xfer-offline-replicated-effect-v1", "created_at": _now(),
        "experiment_id": EXPERIMENT_ID, "idea_id": IDEA_3, "source_evidence": source, "frozen_gate": REPLICATED_GATE,
        "candidate_summary": candidates,
        "placebo_attribution": {
            "changed_units": len(changed), "total_units": len(rows),
            "transitions": [{"two_arm_effect": old, "placebo_controlled_effect": new, "label": labels.get((old, new), f"two-arm {old:+d} -> controlled {new:+d}"), "count": count} for (old, new), count in sorted(transitions.items())],
            "interpretation": "Matched placebo changes attribution, so retrieved-vs-no-memory alone confounds semantic memory effects with generic context perturbation.",
        },
        "gate_checks": checks, "gate_pass": all(x["pass"] for x in checks.values()),
        "verdict": "PHENOMENON_PASS_METHOD_INCONCLUSIVE", "reason": "candidate_support_insufficient",
        "method_failure_authorized": False,
        "next_action": "Run the preregistered support-enriched Qwen P0 before any method PASS/FAIL claim.",
    }

def _source_family_mean_loto(rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = []
    for row in [r for r in rows if int(r["controlled_delta"]) != 0]:
        training = [int(other["controlled_delta"]) for other in rows if other["source_family"] == row["source_family"] and other["target_family"] != row["target_family"]]
        mean = _mean(training); predicted = _sign(mean); actual = _sign(int(row["controlled_delta"])); covered = predicted != 0
        evaluated.append({"unit_id": row["unit_id"], "source_family": row["source_family"], "heldout_target_family": row["target_family"], "training_units": len(training), "source_family_other_target_mean": mean, "predicted_sign": predicted, "actual_sign": actual, "covered": covered, "correct_if_covered": bool(covered and predicted == actual)})
    covered = [row for row in evaluated if row["covered"]]
    correct = sum(row["correct_if_covered"] for row in covered)
    return {
        "name": "source-family mean LOTO",
        "protocol": "Hold out one target family. Predict only from the same source family's controlled effects on other target families; never read held-out target-family outcomes.",
        "evaluated_nonzero_effects": len(evaluated), "covered": len(covered),
        "coverage": len(covered) / len(evaluated) if evaluated else 0.0,
        "covered_sign_correct": correct, "covered_sign_accuracy": correct / len(covered) if covered else None,
        "claim_authority": "strongest simplification diagnostic only; support is too small for a success claim",
        "rows": evaluated,
    }

def _transport_analysis(rows: list[dict[str, Any]], source: dict[str, Any]) -> dict[str, Any]:
    nonzero = [row for row in rows if int(row["controlled_delta"]) != 0]
    counts = Counter(str(row["target_family"]) for row in nonzero)
    families = sorted({str(row["target_family"]) for row in rows})
    folds = [{"target_family": family, "nonzero_controlled_effects": counts.get(family, 0), "eligible": counts.get(family, 0) >= 2} for family in families]
    eligible = sum(row["eligible"] for row in folds)
    checks = {
        "total_nonzero_controlled_effects": {"required": 12, "actual": len(nonzero), "pass": len(nonzero) >= 12},
        "eligible_target_family_folds": {"required": 3, "actual": eligible, "pass": eligible >= 3},
    }
    return {
        "schema_version": "1.0", "analysis_id": "p0-mem-xfer-offline-transport-v1", "created_at": _now(),
        "experiment_id": EXPERIMENT_ID, "idea_id": IDEA_5, "source_evidence": source, "frozen_support_gate": TRANSPORT_GATE,
        "support": {"controlled_nonzero": len(nonzero), "controlled_harm": sum(int(row["controlled_delta"]) < 0 for row in rows), "controlled_benefit": sum(int(row["controlled_delta"]) > 0 for row in rows), "target_family_folds": folds},
        "strongest_simplification": _source_family_mean_loto(rows),
        "gate_checks": checks, "gate_pass": all(x["pass"] for x in checks.values()),
        "verdict": "PHENOMENON_PASS_TRANSPORT_SUPPORT_INSUFFICIENT", "reason": "controlled_effect_support_insufficient",
        "method_failure_authorized": False,
        "next_action": "Run support-enriched Qwen data; future transport must beat source-family mean LOTO and other frozen simplifications under strict LOTO.",
    }

def analyze_full_table(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    rows = _load_table(run_dir / "main_table.csv")
    source = _validate_run(run_dir, rows)
    observed = {
        "units": len(rows),
        "outcome_disagreement": sum(bool(row["outcome_disagreement"]) for row in rows),
        "retrieved_harm": sum(row["retrieved_delta"] < 0 for row in rows),
        "retrieved_benefit": sum(row["retrieved_delta"] > 0 for row in rows),
        "placebo_nonzero": sum(row["placebo_delta"] != 0 for row in rows),
        "controlled_nonzero": sum(row["controlled_delta"] != 0 for row in rows),
        "mean_retrieved_effect_vs_no_memory": _mean([row["retrieved_delta"] for row in rows]),
        "mean_placebo_effect_vs_no_memory": _mean([row["placebo_delta"] for row in rows]),
        "mean_controlled_effect_vs_placebo": _mean([row["controlled_delta"] for row in rows]),
    }
    expected = {"units": 32, "outcome_disagreement": 8, "retrieved_harm": 3, "retrieved_benefit": 3, "placebo_nonzero": 5, "controlled_nonzero": 5}
    mismatches = {key: (observed[key], value) for key, value in expected.items() if observed[key] != value}
    if mismatches:
        raise OfflineAnalysisError(f"frozen evidence mismatch: {mismatches}")
    idea3 = _candidate_analysis(rows, source)
    idea5 = _transport_analysis(rows, source)
    decision = {
        "schema_version": "1.0", "analysis_id": "p0-mem-xfer-offline-decision-v1", "created_at": _now(),
        "experiment_id": EXPERIMENT_ID, "source_evidence": source, "full_qwen_observed": observed,
        "idea_3": {"idea_id": IDEA_3, "verdict": idea3["verdict"], "reason": idea3["reason"], "method_failure_authorized": False},
        "idea_5": {"idea_id": IDEA_5, "verdict": idea5["verdict"], "reason": idea5["reason"], "method_failure_authorized": False},
        "workflow_decision": "EXPAND",
        "authorized_scope": ["P0-MEM-XFER-SUPPORT-ENRICHED Qwen support qualification only"],
        "next_experiment": "P0-MEM-XFER-SUPPORT-ENRICHED", "next_status": "support_qualification_pending",
        "second_model_status": "second_model_hold", "second_model_authorized": False, "method_failure_authorized": False,
        "interpretation": "Phenomenon replicated; candidate-level and transport support are insufficient. Expand only the Qwen support substrate.",
    }
    return {"idea3": idea3, "idea5": idea5, "decision": decision, "rows": rows}

def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})

def write_offline_analysis(run_dir: Path, output_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        raise OfflineAnalysisError(f"refusing to overwrite non-empty offline analysis directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    result = analyze_full_table(run_dir)
    outputs = {
        "replicated_effect_memory_gate.json": result["idea3"],
        "cross_task_effect_transport.json": result["idea5"],
        "offline_decision.json": result["decision"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(output_dir / "candidate_effects.csv", result["idea3"]["candidate_summary"], ["memory_id", "source_family", "n", "controlled_harm_units", "controlled_benefit_units", "controlled_zero_units", "mean_controlled_effect", "replicated_controlled_harm", "replicated_controlled_benefit"])
    _write_csv(output_dir / "source_family_mean_loto.csv", result["idea5"]["strongest_simplification"]["rows"], ["unit_id", "source_family", "heldout_target_family", "training_units", "source_family_other_target_mean", "predicted_sign", "actual_sign", "covered", "correct_if_covered"])
    _write_csv(output_dir / "unit_effect_attribution.csv", result["rows"], ["unit_id", "source_family", "target_family", "memory_id", "retrieved_success", "no_memory_success", "placebo_success", "retrieved_delta", "placebo_delta", "controlled_delta", "outcome_disagreement"])
    manifest = {"schema_version": "1.0", "analysis_id": "p0-mem-xfer-offline-analysis-v1", "created_at": _now(), "cpu_only": True, "source_files_modified": False, "run_dir": str(run_dir.resolve()), "output_dir": str(output_dir.resolve()), "source_evidence_sha256": result["decision"]["source_evidence"]["evidence_sha256"], "outputs": sorted([*outputs, "candidate_effects.csv", "source_family_mean_loto.csv", "unit_effect_attribution.csv"])}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**result["decision"], "output_dir": str(output_dir.resolve())}

def ensure_offline_analysis(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    decision = output_dir / "offline_decision.json"
    manifest = output_dir / "manifest.json"
    if decision.exists() and manifest.exists():
        return json.loads(decision.read_text(encoding="utf-8"))
    return write_offline_analysis(run_dir, output_dir)

def main() -> None:
    parser = argparse.ArgumentParser(description="CPU-only frozen analyzer for P0-MEM-XFER-CAUSAL.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    out = args.output_dir or (args.run_dir / "offline-analysis")
    print(json.dumps(write_offline_analysis(args.run_dir, out, args.overwrite), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

FULL_RUN_ID = "p0-mem-xfer-causal-full-qwen-v1-r1"
SUPPORT_RUN_ID = "p0-mem-xfer-support-enriched-qwen-v1"

def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def build_mem_xfer_workflow_state(experiment_root: Path) -> dict[str, Any]:
    full_dir = experiment_root / "runs" / FULL_RUN_ID
    offline_dir = full_dir / "offline-analysis"
    full_progress = _read_json(full_dir / "progress.json") or {}
    full_complete = (
        full_progress.get("status") == "complete"
        and int(full_progress.get("completed_episodes") or 0) == 96
        and int(full_progress.get("completed_units") or 0) == 32
    )
    offline_decision = None
    offline_error = None
    if full_complete:
        try:
            offline_decision = ensure_offline_analysis(full_dir, offline_dir)
        except Exception as error:
            offline_error = f"{type(error).__name__}: {error}"
    offline_complete = bool(_read_json(offline_dir / "offline_decision.json")) and offline_error is None
    if offline_complete:
        offline_decision = _read_json(offline_dir / "offline_decision.json")

    support_dir = experiment_root / "runs" / SUPPORT_RUN_ID
    support_progress = _read_json(support_dir / "support-qualification" / "progress.json") or _read_json(support_dir / "progress.json") or {}
    support_decision = _read_json(support_dir / "support-qualification" / "decision.json") or _read_json(support_dir / "decision.json")
    full_support_candidates = (
        support_dir / "full-support-table",
        support_dir / "full-qwen-support-table",
        support_dir / "full-qwen",
    )
    completed_full_support_dirs = []
    for candidate in full_support_candidates:
        candidate_progress = _read_json(candidate / "progress.json") or {}
        candidate_decision = _read_json(candidate / "decision.json") or {}
        candidate_completed = int(candidate_progress.get("completed_executions") or candidate_progress.get("completed_episodes") or 0)
        candidate_units = int(candidate_progress.get("completed_units") or 0)
        if candidate_decision.get("decision") == "FULL_SUPPORT_TABLE_COLLECTED" and candidate_completed == 216 and candidate_units == 72:
            completed_full_support_dirs.append(candidate)
    if len(completed_full_support_dirs) > 1:
        raise OfflineAnalysisError(f"multiple completed full-support streams found: {[str(path) for path in completed_full_support_dirs]}")
    full_support_dir = completed_full_support_dirs[0] if completed_full_support_dirs else next(
        (path for path in full_support_candidates if (path / "progress.json").exists()),
        full_support_candidates[0],
    )
    full_support_audit = _read_json(support_dir / "full-pre-gpu-audit.json") or _read_json(experiment_root / "pre-gpu" / "p0-mem-xfer-support-full-audit.json")
    full_support_progress_raw = _read_json(full_support_dir / "progress.json") or {}
    completed_full_support_executions = int(full_support_progress_raw.get("completed_executions") or full_support_progress_raw.get("completed_episodes") or 0)
    total_full_support_executions = int(full_support_progress_raw.get("total_executions") or full_support_progress_raw.get("total_episodes") or 216)
    full_support_progress = {
        **full_support_progress_raw,
        "completed_episodes": completed_full_support_executions,
        "total_episodes": total_full_support_executions,
        "selected_evidence_dir": str(full_support_dir),
    }
    full_support_decision = _read_json(full_support_dir / "decision.json")
    full_support_provenance_deviation = _read_json(full_support_dir / "source-provenance-deviation.json")
    full_support_sequencing_deviation = _read_json(full_support_dir / "sequencing-deviation.json")
    full_support_complete = bool(
        full_support_decision
        and full_support_decision.get("decision") == "FULL_SUPPORT_TABLE_COLLECTED"
        and completed_full_support_executions == 216
        and int(full_support_progress_raw.get("completed_units") or 0) == 72
    )
    expand_allowed = bool(offline_decision and offline_decision.get("workflow_decision") == "EXPAND")
    if not expand_allowed:
        support_status = "support_qualification_hold"
    elif support_decision and support_decision.get("decision") == "SUPPORT_QUALIFICATION_PASS":
        support_status = "support_qualification_pass"
    elif support_decision and support_decision.get("decision") == "SUPPORT_QUALIFICATION_HOLD":
        support_status = "support_qualification_hold"
    elif support_progress.get("status") in {"running", "support_qualification_running"}:
        support_status = "support_qualification_running"
    else:
        support_status = "support_qualification_pending"

    if support_status != "support_qualification_pass":
        full_support_status = "full_support_hold"
    elif full_support_complete:
        full_support_status = "full_support_complete"
    elif full_support_progress_raw.get("status") in {"full_qwen_support_running", "full_support_table_running", "full_support_running"}:
        full_support_status = "full_qwen_support_running"
    elif full_support_progress_raw.get("status") in {"full_qwen_support_checkpoint", "full_support_table_checkpoint", "runtime-blocker", "budget-stop"}:
        full_support_status = "full_qwen_support_checkpoint"
    elif full_support_audit and full_support_audit.get("decision") == "PASS" and full_support_audit.get("execution_ready") is True:
        full_support_status = "full_support_ready"
    else:
        full_support_status = "full_support_pending"

    support_analysis_dir = support_dir / "support-enriched-analysis"
    support_analysis_error = None
    support_analysis_decision = _read_json(support_analysis_dir / "offline_decision.json")
    if full_support_complete and support_analysis_decision is None:
        try:
            support_analysis_decision = ensure_support_enriched_analysis(support_dir, support_analysis_dir)
        except Exception as error:
            support_analysis_error = f"{type(error).__name__}: {error}"
    support_analysis_complete = bool(support_analysis_decision) and support_analysis_error is None
    second_model_authorized = bool(support_analysis_complete and support_analysis_decision.get("second_model_authorized") is True)
    second_model_status = "second_model_authorized" if second_model_authorized else "second_model_hold"
    return {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "full_run_id": FULL_RUN_ID,
        "support_run_id": SUPPORT_RUN_ID,
        "allowed_statuses": [
            "full_table_collected", "offline_analysis_pending", "offline_analysis_complete",
            "support_qualification_pending", "support_qualification_running",
            "support_qualification_hold", "support_qualification_pass",
            "full_support_pending", "full_support_ready", "full_qwen_support_running", "full_qwen_support_checkpoint",
            "full_support_hold", "full_support_complete", "support_enriched_analysis_pending", "support_enriched_analysis_complete",
            "support_enriched_analysis_blocked", "second_model_hold", "second_model_authorized",
        ],
        "full_table": {
            "status": "full_table_collected" if full_complete else "collecting",
            "complete": full_complete, "progress": full_progress,
        },
        "offline_analysis": {
            "status": "offline_analysis_complete" if offline_complete else "offline_analysis_pending",
            "complete": offline_complete, "error": offline_error,
            "decision": offline_decision,
            "automatic_trigger": "full_table_collected",
        },
        "support_qualification": {
            "status": support_status, "progress": support_progress,
            "decision": support_decision, "authorized": expand_allowed,
        },
        "full_support": {
            "status": full_support_status, "progress": full_support_progress,
            "decision": full_support_decision, "pre_gpu_audit": full_support_audit,
            "provenance_deviation": full_support_provenance_deviation,
            "sequencing_deviation": full_support_sequencing_deviation,
            "scientific_authority": "provisional-only" if full_support_provenance_deviation else ("decision-authority" if full_support_decision else "incomplete"),
            "authorized": support_status == "support_qualification_pass" and bool(full_support_audit and full_support_audit.get("execution_ready") is True),
        },
        "support_enriched_analysis": {
            "status": "support_enriched_analysis_complete" if support_analysis_complete else ("support_enriched_analysis_pending" if not full_support_complete else "support_enriched_analysis_blocked"),
            "complete": support_analysis_complete,
            "error": support_analysis_error,
            "decision": support_analysis_decision,
            "automatic_trigger": "full_support_complete",
        },
        "second_model": {
            "status": second_model_status, "authorized": second_model_authorized,
            "rule": "Remain HOLD through support qualification and the full Qwen support table; second-backbone authorization requires an explicit CPU-only full-support decision and is never implied by the old full table or qualification PASS alone.",
        },
        "dependencies": [
            {"from": "full_table_collected", "to": "offline_analysis_complete", "automatic": True, "action": "run CPU-only frozen offline analyzer"},
            {"from": "offline_analysis_complete", "to": "support_qualification_pending", "condition": "workflow_decision == EXPAND"},
            {"from": "support_qualification_pass", "to": "full_support_pending", "condition": "same frozen plan; reuse 72 support episodes and collect only remaining 144"},
            {"from": "full_support_complete", "to": "support_enriched_analysis_complete", "automatic": True, "action": "run frozen CPU-only #3 candidate support/gate and #5 strict LOTO support analysis"},
            {"from": "support_enriched_analysis_complete", "to": "second_model_authorized", "condition": "explicit CPU decision authorizes second model; support counts alone do not imply method PASS"},
        ],
    }
