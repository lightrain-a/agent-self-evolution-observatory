from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .config import PROJECT_ROOT

CANDIDATE_ID = "pace-search-control-transport"
CONTRACT_VERSION = "pace-search-control-transport-f0-v1"
PRIMARY_REF = "arXiv:2608.14441"
PACEVOLVE_REF = "arXiv:2601.10657"
MIN_TASKS = 6
MIN_REVERSALS = 2
MIN_REVERSAL_RATE = 0.25
LOW_STAGE, HIGH_STAGE = 1, 4
DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "pace-bench-search-control-transport-f0-20260818.json"
AUTHORITY = {key: False for key in ("canonical_generator", "canonical_problem_gate", "paper_design", "method", "experiment", "p0", "gpu")}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _stage(value: Any) -> int | None:
    match = re.search(r"Stage[-_ ]?(\d+)", str(value or ""), re.I)
    return int(match.group(1)) if match else None


def _sign(value: float, eps: float = 1e-9) -> int:
    return 1 if value > eps else -1 if value < -eps else 0


def _valid(row: dict[str, Any]) -> bool:
    return bool(row.get("task_id") and row.get("strategy") and _stage(row.get("target_environment")) and isinstance(row.get("attempts"), list) and isinstance(row.get("best_score"), (int, float)))


def _early(row: dict[str, Any], prefix: int = 2) -> dict[str, Any]:
    attempts = [a for a in row.get("attempts") or [] if isinstance(a, dict) and a.get("phase") != "reference"][:prefix]
    scores = [float(a.get("score") or 0.0) for a in attempts]
    codes = {str(a.get("code_sha256") or hashlib.sha1(str(a.get("code") or "").encode()).hexdigest()) for a in attempts}
    reasons = set()
    for a in attempts:
        outcome = a.get("outcome") or {}
        if isinstance(outcome, dict):
            reason = outcome.get("failure_reason") or outcome.get("error_type") or outcome.get("category")
            if reason:
                reasons.add(str(reason))
    return {"revision_count": len(attempts), "best_score": max(scores) if scores else None, "score_delta": scores[-1] - scores[0] if len(scores) > 1 else 0.0 if scores else None, "unique_codes": len(codes), "unique_failure_reasons": len(reasons)}


def load_results(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not root.exists():
        return [], {"results_root": str(root), "present": False, "json_files": 0, "valid_pace_results": 0, "manifest_sha256": ""}
    files = sorted(root.rglob("*.json"))
    rows, manifest, invalid = [], [], 0
    for path in files:
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            invalid += 1
            continue
        if not isinstance(row, dict) or not _valid(row):
            invalid += 1
            continue
        row = dict(row)
        row["_early"] = _early(row)
        digest = _sha(path)
        row["_source_sha256"] = digest
        rows.append(row)
        manifest.append(f"{path.resolve()}\0{digest}")
    return rows, {"results_root": str(root), "present": True, "json_files": len(files), "valid_pace_results": len(rows), "invalid_or_nonresult_json": invalid, "manifest_sha256": hashlib.sha256("\n".join(manifest).encode()).hexdigest() if manifest else ""}


def _contract_log(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"present": False, "status": "NOT_PROVIDED"}
    if not path.exists():
        return {"present": False, "status": "MISSING", "path": str(path)}
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Validation complete:\s*(\d+) task\(s\),\s*(\d+) failure\(s\)", text)
    return {"present": True, "path": str(path), "sha256": _sha(path), "tasks": int(match.group(1)) if match else None, "failures": int(match.group(2)) if match else None, "all_pass": bool(match and int(match.group(2)) == 0), "status": "PARSED" if match else "UNPARSED"}


def audit_upstream(root: Path, contracts_log: Path | None = None, hf_status: str = "UNVERIFIED_NETWORK_TIMEOUT") -> dict[str, Any]:
    readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
    metrics = (root / "src/pace_bench/evaluation/metrics.py").read_text(encoding="utf-8", errors="replace")
    types = (root / "src/pace_bench/core/types.py").read_text(encoding="utf-8", errors="replace")
    stage_files = sorted(root.glob("src/pace_bench/tasks/categories/*/*/stages.py"))
    literal_four_stage = 0
    for path in stage_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        literal_four_stage += int(all(f"Stage-{n}" in text for n in range(1, 5)))
    contracts = _contract_log(contracts_log)
    runtime_task_contract = bool(
        contracts.get("all_pass")
        and int(contracts.get("tasks") or 0) == len(stage_files)
        and len(stage_files) > 0
    )
    methods = sorted(p.stem for p in (root / "methods").glob("*.py") if p.name != "__init__.py")
    released_results = [p for name in ("results", "results_scratch", "evaluation_results", "outputs") for p in (root / name).rglob("*.json")] if root.exists() else []
    hf = re.search(r"https://huggingface\.co/datasets/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", readme)
    return {
        "primary_ref": PRIMARY_REF,
        "upstream_root": str(root),
        "upstream_git_head": _git_head(root),
        "task_count": len(stage_files),
        "literal_four_stage_file_count": literal_four_stage,
        "runtime_four_stage_task_count": len(stage_files) if runtime_task_contract else literal_four_stage,
        "source_target_pair_count": (len(stage_files) if runtime_task_contract else literal_four_stage) * 4,
        "method_adapter_count": len(methods),
        "method_adapters": methods,
        "executable_release_static_contract": runtime_task_contract,
        "static_literal_stage_false_negative_expected": literal_four_stage != len(stage_files) and runtime_task_contract,
        "result_schema_has_attempt_trajectory": all(token in types for token in ("class AttemptRecord", "class EvaluationResult", "attempts")),
        "built_in_failure_taxonomy": all(label in metrics for label in ("design_fixation", "stagnation", "exploration", "late_convergence")),
        "built_in_strategy_complementarity_kappa": "_strategy_complementarity" in metrics and "_cohens_kappa" in metrics,
        "built_in_strategy_by_stage_transport": "by_strategy_and_stage" in metrics or "strategy_transport" in metrics,
        "github_released_result_json_count": len(released_results),
        "github_released_author_trajectories": bool(released_results),
        "huggingface_dataset_declared": bool(hf),
        "huggingface_dataset_url": hf.group(0) if hf else "",
        "huggingface_manifest_status": hf_status,
        "released_tasks_note_extra_difficulty_pass": "additional difficulty-escalation pass beyond the version evaluated in the paper" in readme,
        "contracts_validation": contracts,
    }


def _cell(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    labels = [str((row.get("analysis") or {}).get("error_type") or row.get("error_type") or "unknown") for row in rows]
    early = [row.get("_early") or _early(row) for row in rows]
    early_scores = [float(x["best_score"]) for x in early if x.get("best_score") is not None]
    return {
        "run_count": len(rows),
        "pass_rate": mean(float(bool(row.get("success"))) for row in rows) if rows else 0.0,
        "score_mean": mean(float(row["best_score"]) for row in rows) if rows else 0.0,
        "failure_label_majority": Counter(labels).most_common(1)[0][0] if labels else "unknown",
        "early_prefix_best_score_mean": mean(early_scores) if early_scores else None,
    }


def _loo_majority(labels: list[int]) -> dict[str, Any]:
    correct = predicted = 0
    for i, truth in enumerate(labels):
        train = labels[:i] + labels[i + 1 :]
        counts = Counter(train)
        if not train or counts[1] == counts[-1]:
            continue
        guess = 1 if counts[1] > counts[-1] else -1
        predicted += 1
        correct += int(guess == truth)
    return {"predicted_tasks": predicted, "correct_tasks": correct, "accuracy": correct / predicted if predicted else None}


def summarize_source_experiment(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize auditable provider cost already embedded in PACE result files.

    This intentionally does not infer missing provider response IDs.  Compact PACE
    results preserve per-generation resolved model and token usage, which is enough
    to prove real model execution and a lower bound on generation requests, but not
    an exact provider-level request count when external JSONL receipts are missing.
    """
    rows = [row for row in results if _valid(row)]
    token_usage = Counter({"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    generation_records = 0
    resolved_models: Counter[str] = Counter()
    for row in rows:
        usage = row.get("token_usage") or {}
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            token_usage[key] += int(usage.get(key) or 0)
        for attempt in row.get("attempts") or []:
            generation = attempt.get("generation") if isinstance(attempt, dict) else None
            if not isinstance(generation, dict):
                continue
            generation_records += 1
            resolved = str(generation.get("model") or "").strip()
            if resolved:
                resolved_models[resolved] += 1
    real_rows = [row for row in rows if str(row.get("provider") or "").lower() != "mock" and str(row.get("model") or "").lower() != "mock"]
    return {
        "real_provider_result_records": len(real_rows),
        "attempt_generation_records": generation_records,
        "provider_call_count_exact": None,
        "provider_call_count_provable_lower_bound": generation_records,
        "aggregate_token_usage": dict(token_usage),
        "resolved_models_in_attempt_records": dict(sorted(resolved_models.items())),
        "exact_provider_response_receipts_complete": False,
        "receipt_limitation": "Compact result files preserve model/token provenance but not a complete external response-id receipt ledger; do not infer exact provider call count.",
        "scientific_authority": False,
    }


def _source_revision_support(results: Iterable[dict[str, Any]], strategy: str = "codeevolve") -> dict[str, Any]:
    rows = [row for row in results if _valid(row) and str(row.get("strategy") or "") == strategy and _stage(row.get("target_environment")) == LOW_STAGE]
    units = []
    for row in sorted(rows, key=lambda value: str(value.get("task_id") or "")):
        attempts = [attempt for attempt in row.get("attempts") or [] if isinstance(attempt, dict)]
        reference = next((attempt for attempt in attempts if attempt.get("phase") == "reference" and attempt.get("score") is not None), None)
        revisions = [attempt for attempt in attempts if attempt.get("phase") != "reference" and attempt.get("score") is not None]
        if reference is None or not revisions:
            continue
        best = max(revisions, key=lambda attempt: float(attempt["score"]))
        effect = float(best["score"]) - float(reference["score"])
        units.append({"task_id": str(row.get("task_id") or ""), "reference_score": float(reference["score"]), "best_revision_score": float(best["score"]), "source_revision_effect": effect, "positive_source_revision": effect > 1e-9})
    positive = sum(unit["positive_source_revision"] for unit in units)
    return {
        "strategy": strategy,
        "eligible_source_stage_units": len(units),
        "positive_source_revision_units": positive,
        "positive_source_revision_fraction": positive / len(units) if units else None,
        "units": units,
        "interpretation": "Diagnostic support audit only. It does not create a new cross-stage patch-transport hypothesis or authorize more provider calls.",
        "scientific_authority": False,
    }


def analyze_transport(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for row in results if _valid(row)]
    real = [row for row in rows if str(row.get("provider") or "").lower() != "mock" and str(row.get("model") or "").lower() != "mock"]
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in real:
        cohort = (str(row.get("provider") or ""), str(row.get("model") or ""), str(row.get("mode") or "adaptation"), int(row.get("attempt_budget") or 0))
        grouped[(cohort, str(row["task_id"]), str(row["strategy"]), int(_stage(row["target_environment"]) or 0))].append(row)

    reports = []
    cohorts = sorted({key[0] for key in grouped}, key=str)
    for cohort in cohorts:
        strategies = sorted({key[2] for key in grouped if key[0] == cohort})
        tasks = sorted({key[1] for key in grouped if key[0] == cohort})
        for left, right in itertools.combinations(strategies, 2):
            units, directions, high_labels = [], Counter(), []
            for task in tasks:
                keys = {(strategy, stage): (cohort, task, strategy, stage) for strategy in (left, right) for stage in (LOW_STAGE, HIGH_STAGE)}
                if any(key not in grouped for key in keys.values()):
                    continue
                ll, lr = _cell(grouped[keys[(left, LOW_STAGE)]]), _cell(grouped[keys[(right, LOW_STAGE)]])
                hl, hr = _cell(grouped[keys[(left, HIGH_STAGE)]]), _cell(grouped[keys[(right, HIGH_STAGE)]])
                low_delta = ll["score_mean"] - lr["score_mean"]
                high_delta = hl["score_mean"] - hr["score_mean"]
                low_sign, high_sign = _sign(low_delta), _sign(high_delta)
                strict = bool(low_sign and high_sign)
                reversal = strict and low_sign != high_sign
                direction = ""
                if reversal:
                    direction = f"{left}_to_{right}" if low_sign > 0 else f"{right}_to_{left}"
                    directions[direction] += 1
                if high_sign:
                    high_labels.append(high_sign)
                units.append({
                    "task_id": task,
                    "stage1_score_delta_left_minus_right": low_delta,
                    "stage4_score_delta_left_minus_right": high_delta,
                    "strict_comparison": strict,
                    "strict_reversal": reversal,
                    "reversal_direction": direction,
                    "stage1_failure_labels": {left: ll["failure_label_majority"], right: lr["failure_label_majority"]},
                    "stage4_failure_labels": {left: hl["failure_label_majority"], right: hr["failure_label_majority"]},
                    "stage1_early_prefix_best_scores": {left: ll["early_prefix_best_score_mean"], right: lr["early_prefix_best_score_mean"]},
                })
            strict_units = [u for u in units if u["strict_comparison"]]
            reversals = [u for u in strict_units if u["strict_reversal"]]
            reports.append({
                "cohort": {"provider": cohort[0], "model": cohort[1], "mode": cohort[2], "attempt_budget": cohort[3]},
                "left_strategy": left,
                "right_strategy": right,
                "comparable_tasks": len(units),
                "strict_non_tied_tasks": len(strict_units),
                "strict_reversals": len(reversals),
                "strict_reversal_rate": len(reversals) / len(strict_units) if strict_units else None,
                "reversal_directions": dict(sorted(directions.items())),
                "bidirectional_reversal": len(directions) >= 2,
                "stage1_winner_transport_accuracy": 1.0 - len(reversals) / len(strict_units) if strict_units else None,
                "stage4_global_winner_loo_baseline": _loo_majority(high_labels),
                "units": units,
            })
    reports.sort(key=lambda row: (row["strict_non_tied_tasks"], row["strict_reversals"], row["comparable_tasks"]), reverse=True)
    best = reports[0] if reports else None
    if not real:
        decision, available = "HOLD_ONLY_SYNTHETIC_OR_MOCK_TRAJECTORIES", False
    elif not best or best["comparable_tasks"] < MIN_TASKS:
        decision, available = "HOLD_INSUFFICIENT_REAL_MULTISTRATEGY_STAGE_COVERAGE", False
    else:
        go = best["strict_non_tied_tasks"] >= MIN_TASKS and best["strict_reversals"] >= MIN_REVERSALS and float(best["strict_reversal_rate"] or 0.0) >= MIN_REVERSAL_RATE and best["bidirectional_reversal"]
        decision = "GO_SEARCH_CONTROL_TRANSPORT_FAILURE_PHENOMENON" if go else "STOP_OR_REDUCE_TO_STAGE_CONDITIONED_GLOBAL_SEARCH_CONTROL"
        available = True
    return {
        "real_result_count": len(real),
        "mock_or_synthetic_result_count": len(rows) - len(real),
        "real_tasks": sorted({str(row["task_id"]) for row in real}),
        "real_strategies": sorted({str(row["strategy"]) for row in real}),
        "real_stages": sorted({int(_stage(row["target_environment"]) or 0) for row in real}),
        "pair_reports": reports,
        "best_supported_strategy_pair": best,
        "decision": decision,
        "scientific_result_available": available,
    }


def build_receipt(upstream_root: Path, results_root: Path, contracts_log: Path | None = None, hf_status: str = "UNVERIFIED_NETWORK_TIMEOUT") -> dict[str, Any]:
    upstream = audit_upstream(upstream_root, contracts_log, hf_status)
    results, input_receipt = load_results(results_root)
    analysis = analyze_transport(results)
    source_experiment = summarize_source_experiment(results)
    source_revision_support = _source_revision_support(results)
    ready = bool(upstream["executable_release_static_contract"] and upstream["result_schema_has_attempt_trajectory"] and upstream["built_in_failure_taxonomy"] and upstream["built_in_strategy_complementarity_kappa"] and not upstream["built_in_strategy_by_stage_transport"])
    upstream_public = dict(upstream)
    upstream_public.pop("upstream_root", None)
    contracts_public = dict(upstream_public.get("contracts_validation") or {})
    contracts_public.pop("path", None)
    upstream_public["contracts_validation"] = contracts_public
    input_public = dict(input_receipt)
    input_public.pop("results_root", None)
    return {
        "schema_version": "1.1",
        "generated_at": _now(),
        "stage": "PACE_BENCH_SEARCH_CONTROL_TRANSPORT_F0",
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "primary_ref": PRIMARY_REF,
        "zero_gpu": True,
        "analysis_provider_calls": 0,
        "source_experiment_used_real_provider": bool(source_experiment["real_provider_result_records"]),
        "training_steps": 0,
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
        "policy": {
            "source_pool_exposure_is_not_executable_asset_review": True,
            "mock_trajectory_is_plumbing_only": True,
            "released_failure_taxonomy_cannot_be_reclaimed_as_novelty": True,
            "released_endpoint_strategy_complementarity_cannot_be_reclaimed_as_novelty": True,
            "generic_refine_explore_routing_is_reduced_by_progress_aware_adaptive_search": True,
            "same_task_cross_stage_transport_is_the_surviving_falsifier_object": True,
            "real_same_model_same_provider_same_budget_multistrategy_results_required": True,
            "bidirectional_stage1_to_stage4_rank_reversal_required_for_go": True,
            "no_method_or_p0_authority_from_this_receipt": True,
        },
        "upstream_release_receipt": upstream_public,
        "collision_audit": {
            "pace_bench_own_failure_taxonomy": upstream["built_in_failure_taxonomy"],
            "pace_bench_own_endpoint_strategy_complementarity": upstream["built_in_strategy_complementarity_kappa"],
            "pace_bench_own_strategy_by_stage_transport": upstream["built_in_strategy_by_stage_transport"],
            "generic_adaptive_search_closest_reduction": {"ref": PACEVOLVE_REF, "boundary": "progress-aware backtracking and self-adaptive exploration/exploitation coordination already reduce a generic early-stagnation search router"},
            "surviving_object": "Within one fixed task/model/provider/budget, does relative search-strategy utility reverse from mild Stage-1 mutation to severe Stage-4 mutation in both directions across tasks?",
        },
        "f0_contract": {
            "causal_unit": "same PACE task under Stage-1 and Stage-4 target mutations",
            "comparison_unit": "same pair of search strategies, same provider/model/mode/attempt budget",
            "primary_endpoint": "strict sign reversal of mean best-score difference between the two strategies",
            "go_thresholds": {"minimum_comparable_non_tied_tasks": MIN_TASKS, "minimum_strict_reversals": MIN_REVERSALS, "minimum_strict_reversal_rate": MIN_REVERSAL_RATE, "bidirectional_reversal_required": True},
            "strongest_same_information_reduction": "A global stage-conditioned strategy prior. Bidirectional within-stage task heterogeneity is required before any task-conditioned router is considered.",
            "recommended_low_cost_panel": {"tasks": ["S_01", "K_01", "D_01", "F_01", "C_01", "E_01"], "selection": "first registered task in each of six PACE categories; outcome-blind", "stages": ["Stage-1", "Stage-4"], "strategies": ["tree_of_thoughts", "codeevolve"], "runs": 1, "attempt_budget": 6, "real_model_required": True},
            "next_only_if_go": "Freeze an early-trajectory predictor of Stage-4 strategy utility and beat score-only, failure-label-only, global-stage-prior, and progress-aware adaptive-search reductions under the same information and verifier budget before method design.",
        },
        "input_receipt": input_public,
        "source_experiment_provenance": source_experiment,
        "secondary_source_revision_support": source_revision_support,
        "analysis": analysis,
        "decision": analysis["decision"] if ready else "HOLD_UPSTREAM_RELEASE_AUDIT_INCOMPLETE",
        "registered_prediction_rejected": bool(ready and analysis["decision"] == "STOP_OR_REDUCE_TO_STAGE_CONDITIONED_GLOBAL_SEARCH_CONTROL"),
        "principle_dead_end_certified": False,
        "f0_plumbing_ready": ready,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit PACE-Bench release assets and falsify cross-stage search-control transport.")
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--contracts-log", type=Path)
    parser.add_argument("--hf-manifest-status", default="UNVERIFIED_NETWORK_TIMEOUT", choices=("UNVERIFIED_NETWORK_TIMEOUT", "TASK_DATA_ONLY", "AUTHOR_TRAJECTORIES_RELEASED", "NO_DATASET_LINK"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    receipt = build_receipt(args.upstream_root, args.results_root, args.contracts_log, args.hf_manifest_status)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision": receipt["decision"], "f0_plumbing_ready": receipt["f0_plumbing_ready"], "upstream_head": receipt["upstream_release_receipt"]["upstream_git_head"], "valid_results": receipt["input_receipt"]["valid_pace_results"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
