from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from .asset_first_stri_practical_baselines_20260824 import evaluate_regime

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = Path(os.environ.get("SKILLROUTER_REPO", str(ROOT / "external" / "SkillRouter")))
DEFAULT_JSON = ROOT / "generated" / "asset-first-stri-skillrouter-relevance-analogue-20260824.json"
DEFAULT_CSV = ROOT / "generated" / "asset-first-stri-skillrouter-relevance-analogue-20260824.csv"
EXPECTED = {
    "commit": "2f0c69fe6786bfee6312a1ab5d5f69abdc6bd245",
    "data/eval_core/tasks.jsonl": "760b9d5b345b929ded9eb14e8ef2fd61422a1fb63b6607facaed4fc3baf2634e",
    "data/eval_core/relevance.json": "7a908f387b8f1c795897b0984f417a055774d99a60d7496ee4f5e06d6b5ad0fe",
    "data/eval_core/README.md": "7594035d36892440be416567848567ed425b1b7212385f41508310c890a1d367",
    "data/eval_core/manifest.json": "d472ca7ad3455179f984ac20be835575519f2aa28bfc4aaac0ccfc5123101615",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight(repo: Path) -> dict[str, bool]:
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    checks = {"commit": commit == EXPECTED["commit"]}
    for rel, expected in EXPECTED.items():
        if rel == "commit":
            continue
        checks[f"sha:{rel}"] = sha(repo / rel) == expected
    if not all(checks.values()):
        raise RuntimeError(f"SkillRouter preflight failed: {checks}")
    return checks


def _rows(relevance: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id, rel in relevance.items():
        if rel.get("task_type") == "generic_only":
            continue
        if mode == "core_gt":
            skills = list(rel.get("core_gt_ids") or [])
        elif mode == "all_gt":
            skills = list(rel.get("gt_skill_ids") or [])
        elif mode == "graded_ge_1":
            skills = [str(skill) for skill, grade in (rel.get("relevance") or {}).items() if float(grade) >= 1.0]
        else:
            raise ValueError(mode)
        if not skills:
            continue
        task = tasks_by_id.get(task_id) or {}
        rows.append({
            "level": "skillrouter",
            "index": len(rows),
            "tool": task_id,
            "domain": task.get("domain"),
            "task_type": rel.get("task_type"),
            "accepted_skill_ids": skills,
            "membership_cardinality": len(skills),
        })
    return rows


def _compact_eval(rows: list[dict[str, Any]]) -> dict[str, Any]:
    full = evaluate_regime(rows)
    keep = {"released_uniform", "inverse_support_size", "inverse_sqrt_support", "nnls_l2", "exact_min_cover_uniform", "maxmin_fair", "exact_rstar", "semantic_first_upper_bound"}
    return {
        "covered_rows": full["covered_rows"],
        "packages": full["packages"],
        "multi_membership_rows": full["multi_membership_rows"],
        "exact_R_star": full["exact_R_star"],
        "baselines": [row for row in full["baselines"] if row["baseline"] in keep],
    }


def build(repo: Path = DEFAULT_REPO) -> dict[str, Any]:
    checks = preflight(repo)
    tasks = [json.loads(line) for line in (repo / "data/eval_core/tasks.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    tasks_by_id = {str(row["task_id"]): row for row in tasks}
    relevance = json.loads((repo / "data/eval_core/relevance.json").read_text(encoding="utf-8"))
    task_types = Counter(str(row.get("task_type") or "") for row in relevance.values())
    regimes = {}
    for mode in ("core_gt", "all_gt", "graded_ge_1"):
        rows = _rows(relevance, tasks_by_id, mode)
        regimes[mode] = {
            **_compact_eval(rows),
            "domains": len({str(row.get("domain") or "") for row in rows}),
            "single_membership_rows": sum(len(row["accepted_skill_ids"]) == 1 for row in rows),
            "mean_membership": sum(len(row["accepted_skill_ids"]) for row in rows) / len(rows),
            "maximum_membership": max(len(row["accepted_skill_ids"]) for row in rows),
        }
    core = regimes["core_gt"]
    all_gt = regimes["all_gt"]
    graded = regimes["graded_ge_1"]
    def baseline(regime: dict[str, Any], name: str) -> dict[str, Any]:
        return next(row for row in regime["baselines"] if row["baseline"] == name)
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "external-retrieval-relevance-analogue",
        "source": {
            "paper": "SkillRouter: Retrieve-and-Rerank Skill Selection for LLM Agents at Scale",
            "repo": str(repo),
            "commit": EXPECTED["commit"],
            "tasks_sha256": EXPECTED["data/eval_core/tasks.jsonl"],
            "relevance_sha256": EXPECTED["data/eval_core/relevance.json"],
        },
        "task_inventory": {
            "released_rows": len(relevance),
            "scored_rows_after_generic_only_exclusion": core["covered_rows"],
            "task_type_counts": dict(sorted(task_types.items())),
        },
        "preflight": checks,
        "regimes": regimes,
        "headline": {
            "core_rows": core["covered_rows"],
            "core_single": core["single_membership_rows"],
            "core_multi": core["multi_membership_rows"],
            "core_packages": core["packages"],
            "core_uniform_ratio": baseline(core, "released_uniform")["metrics"]["distortion_ratio"],
            "core_R_star": core["exact_R_star"],
            "all_gt_uniform_ratio": baseline(all_gt, "released_uniform")["metrics"]["distortion_ratio"],
            "all_gt_R_star": all_gt["exact_R_star"],
            "graded_ge_1_uniform_ratio": baseline(graded, "released_uniform")["metrics"]["distortion_ratio"],
            "graded_ge_1_R_star": graded["exact_R_star"],
            "interpretation": "An independent expert relevance graph is exactly equalizable even though naive uniform package mass creates 7x (gold/core) to 21x (graded) query-exposure spread. This is an external negative analogue for overlap/count-based explanations, not executable-support evidence.",
        },
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_boundary": "SkillRouter relevance labels encode retrieval acceptability rather than executable semantic support. Results are reported only as an external relevance-graph analogue and cannot be used as a second exact-support STRI certificate.",
    }


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["regime", "baseline", "rows", "packages", "multi_rows", "distortion_ratio", "coefficient_of_variation", "max_package_share", "effective_package_count"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for regime_name, regime in payload["regimes"].items():
            for row in regime["baselines"]:
                m = row["metrics"]
                writer.writerow({
                    "regime": regime_name, "baseline": row["baseline"], "rows": regime["covered_rows"], "packages": regime["packages"], "multi_rows": regime["multi_membership_rows"],
                    "distortion_ratio": m.get("distortion_ratio"), "coefficient_of_variation": m.get("coefficient_of_variation"), "max_package_share": m.get("max_package_share"), "effective_package_count": m.get("effective_package_count"),
                })


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--repo", type=Path, default=DEFAULT_REPO); ap.add_argument("--json", type=Path, default=DEFAULT_JSON); ap.add_argument("--csv", type=Path, default=DEFAULT_CSV); args = ap.parse_args()
    payload = build(args.repo); write_outputs(payload, args.json, args.csv)
    print(json.dumps({"headline": payload["headline"], "json": str(args.json), "csv": str(args.csv)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
