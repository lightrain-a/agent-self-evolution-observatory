from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from statistics import median
from typing import Any

PRIMARY_REF = "arXiv:2608.14441"
SCHEMA_VERSION = "1.0"


class _EraseConstants(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        value = node.value
        if value is None:
            replacement: Any = None
        elif isinstance(value, bool):
            replacement = False
        elif isinstance(value, (int, float, complex)):
            replacement = 0
        elif isinstance(value, str):
            replacement = "STR"
        elif isinstance(value, bytes):
            replacement = b"BYTES"
        else:
            replacement = None
        return ast.copy_location(ast.Constant(value=replacement), node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node = self.generic_visit(node)
        node.name = "FUNC"
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node = self.generic_visit(node)
        node.name = "FUNC"
        return node


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(root: Path) -> str:
    import subprocess

    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _function_dump(code: str, name: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            clone = ast.parse(ast.unparse(node)).body[0]
            clone = _EraseConstants().visit(clone)
            ast.fix_missing_locations(clone)
            return ast.dump(clone, annotate_fields=True, include_attributes=False)
    return None


def _surface_class(source: str, target: str) -> str:
    source_build = _function_dump(source, "build_agent")
    source_action = _function_dump(source, "agent_action")
    target_build = _function_dump(target, "build_agent")
    target_action = _function_dump(target, "agent_action")
    build_same = source_build is not None and source_build == target_build
    action_same = source_action is not None and source_action == target_action
    if build_same and action_same:
        return "parameter_only"
    if not build_same and action_same:
        return "build_structural"
    if build_same and not action_same:
        return "control_structural"
    return "mixed_structural"


def _config(environment: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in ("terrain_config", "physics_config"):
        value = getattr(environment, name, None)
        if isinstance(value, dict):
            for key, item in value.items():
                out[f"{name}.{key}"] = item
    return out


def _result_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def build_audit(upstream_root: Path, results_root: Path) -> dict[str, Any]:
    # Import only after caller has supplied a first-party checkout with its runtime deps.
    import sys

    sys.path.insert(0, str(upstream_root / "src"))
    from pace_bench.core.types import EnvironmentId
    from pace_bench.tasks.registry import get_reference_solution, get_registry

    registry = get_registry()
    tasks = list(registry.benchmark_tasks)
    if len(tasks) != 36:
        raise ValueError(f"expected 36 benchmark tasks, found {len(tasks)}")

    stage_jaccard: list[float] = []
    same_changed_key_sets = 0
    topology_counts = {
        "parameter_only": 0,
        "build_structural": 0,
        "control_structural": 0,
        "mixed_structural": 0,
    }
    for task in tasks:
        environments = {str(row.environment_id): row for row in registry.environments(task)}
        initial_cfg = _config(environments["Initial"])
        stage1_cfg = _config(environments["Stage-1"])
        stage4_cfg = _config(environments["Stage-4"])
        stage1_keys = {key for key in set(initial_cfg) | set(stage1_cfg) if initial_cfg.get(key) != stage1_cfg.get(key)}
        stage4_keys = {key for key in set(initial_cfg) | set(stage4_cfg) if initial_cfg.get(key) != stage4_cfg.get(key)}
        same_changed_key_sets += int(stage1_keys == stage4_keys)
        union = stage1_keys | stage4_keys
        stage_jaccard.append(len(stage1_keys & stage4_keys) / len(union) if union else 1.0)

        source = get_reference_solution(task, EnvironmentId("Initial"))
        for stage in range(1, 5):
            target = get_reference_solution(task, EnvironmentId(f"Stage-{stage}"))
            topology_counts[_surface_class(source, target)] += 1

    files = _result_files(results_root)
    if len(files) != 24:
        raise ValueError(f"expected 24 real result JSONs, found {len(files)}")
    reference_censored = 0
    final_zero = 0
    best_revision_zero = 0
    positive_revision_gain = 0
    attempt_budgets: set[int] = set()
    result_hashes: list[dict[str, str]] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        attempts = list(payload.get("attempts") or [])
        attempt_budgets.add(int(payload.get("attempt_budget") or 0))
        reference_scores = [row.get("score") for row in attempts if row.get("phase") == "reference" and isinstance(row.get("score"), (int, float))]
        revision_scores = [row.get("score") for row in attempts if row.get("phase") == "revision" and isinstance(row.get("score"), (int, float))]
        all_scores = [row.get("score") for row in attempts if isinstance(row.get("score"), (int, float))]
        if len(reference_scores) != 1:
            raise ValueError(f"expected one reference score in {path}")
        reference = float(reference_scores[0])
        final_best = max(float(x) for x in all_scores)
        best_revision = max(float(x) for x in revision_scores) if revision_scores else float("-inf")
        reference_censored += int(abs(final_best - reference) < 1e-12)
        final_zero += int(abs(final_best) < 1e-12)
        best_revision_zero += int(best_revision != float("-inf") and abs(best_revision) < 1e-12)
        positive_revision_gain += int(best_revision > reference + 1e-12)
        result_hashes.append({"relative_path": str(path.relative_to(results_root)), "sha256": _sha(path)})

    readme = (upstream_root / "README.md").read_text(encoding="utf-8", errors="replace")
    paper_budget_match = re.search(r"Paper protocol:\*\*\s*two runs,\s*(\d+) attempts", readme)
    paper_attempt_budget = int(paper_budget_match.group(1)) if paper_budget_match else None

    structural_total = 144 - topology_counts["parameter_only"]
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "PACE-PARENT-MECHANISM-REDESIGN",
        "primary_ref": PRIMARY_REF,
        "scientific_authority": False,
        "upstream": {
            "git_head": _git_head(upstream_root),
            "benchmark_tasks": len(tasks),
            "source_target_pairs": 144,
            "paper_attempt_budget": paper_attempt_budget,
        },
        "treatment_semantics_audit": {
            "stage1_stage4_same_changed_key_sets": same_changed_key_sets,
            "tasks": 36,
            "changed_key_jaccard_median": median(stage_jaccard),
            "interpretation": "Stage index is not a single aligned causal-dose variable across tasks because Stage-1 and Stage-4 usually alter different physical-variable sets.",
        },
        "reference_solution_ast_oracle": {
            "normalization": "erase literal constant payloads and function names; preserve identifiers, calls, statements, and control-flow structure in root build_agent/agent_action functions",
            "counts": topology_counts,
            "parameter_only": topology_counts["parameter_only"],
            "structural_total": structural_total,
            "structural_fraction": structural_total / 144.0,
            "load_bearing_claim": "Only parameter-only versus structurally changed is used for principle evidence. The finer build/control split is root-function-only and is not used to certify the reduction because transitive helper semantics can change the finer label.",
        },
        "real_trajectory_audit": {
            "result_files": len(files),
            "attempt_budgets": sorted(attempt_budgets),
            "final_best_equals_reference": reference_censored,
            "final_best_equals_zero": final_zero,
            "best_revision_equals_zero": best_revision_zero,
            "positive_revision_gain": positive_revision_gain,
            "reference_censor_fraction": reference_censored / len(files),
            "result_file_hashes": result_hashes,
        },
        "operationalization_diagnosis": {
            "old_rank_reversal_child_valid_scientific_stop": False,
            "primary_stop_class": "PROTOCOL_STOP",
            "secondary_realization_issue": "REALIZATION_STOP",
            "reasons": [
                "Stage-1 to Stage-4 is not an aligned treatment dose across tasks.",
                "best_score frequently collapses to the shared reference/source score and therefore censors search-strategy differences.",
                "The bounded run used six revision attempts while the paper protocol uses twenty, so convergence behavior was computationally censored.",
                "The official reference solutions show that 140/144 source-to-stage adaptations require structural program change under the load-bearing root-AST oracle, so a rank reversal over stage depth does not isolate the benchmark's core know-how problem.",
            ],
        },
    }


def validate_audit(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("primary_ref") != PRIMARY_REF:
        errors.append("wrong PACE primary ref")
    treatment = state.get("treatment_semantics_audit") or {}
    if (treatment.get("stage1_stage4_same_changed_key_sets"), treatment.get("tasks")) != (3, 36):
        errors.append("PACE changed-key treatment-semantics count drift")
    if abs(float(treatment.get("changed_key_jaccard_median") or 0.0) - 0.30952380952380953) > 1e-12:
        errors.append("PACE changed-key Jaccard drift")
    oracle = state.get("reference_solution_ast_oracle") or {}
    if oracle.get("parameter_only") != 4 or oracle.get("structural_total") != 140:
        errors.append("PACE structural reference-oracle count drift")
    traj = state.get("real_trajectory_audit") or {}
    if traj.get("result_files") != 24 or traj.get("attempt_budgets") != [6]:
        errors.append("PACE real trajectory count/budget drift")
    if traj.get("final_best_equals_reference") != 17 or traj.get("final_best_equals_zero") != 15:
        errors.append("PACE source/reference censor counts drift")
    diagnosis = state.get("operationalization_diagnosis") or {}
    if diagnosis.get("old_rank_reversal_child_valid_scientific_stop") is not False or diagnosis.get("primary_stop_class") != "PROTOCOL_STOP":
        errors.append("PACE invalid operationalization must not be promoted to scientific stop")
    if state.get("scientific_authority") is not False:
        errors.append("PACE evidence audit is evidence-only")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Recompute PACE principle-level evidence from the first-party checkout and real 24-cell trajectories.")
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = build_audit(args.upstream_root, args.results_root)
    errors = validate_audit(state)
    if errors:
        raise SystemExit("invalid PACE evidence audit: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "parameter_only": state["reference_solution_ast_oracle"]["parameter_only"], "structural_total": state["reference_solution_ast_oracle"]["structural_total"], "reference_censored": state["real_trajectory_audit"]["final_best_equals_reference"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
