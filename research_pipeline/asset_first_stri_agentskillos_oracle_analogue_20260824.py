from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from .asset_first_stri_certificate import optimal_target_package_ratio, support_matrix

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = Path("/data/wyt/agent2-asset-first-external/AgentSkillOS")
DEFAULT_JSON = ROOT / "generated" / "asset-first-stri-agentskillos-oracle-analogue-20260824.json"
DEFAULT_CSV = ROOT / "generated" / "asset-first-stri-agentskillos-oracle-analogue-20260824.csv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(repo: Path) -> list[dict[str, Any]]:
    paths = sorted((repo / "benchmark" / "AgentSkillOS_bench" / "tasks").glob("*.json"))
    rows: list[dict[str, Any]] = []
    for path in paths:
        task = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "level": 0,
            "index": str(task["task_id"]),
            "tool": str(task["category"]),
            "task_name": str(task["task_name"]),
            "category": str(task["category"]),
            "accepted_skill_ids": [str(x) for x in task.get("skills") or []],
            "evaluator_count": len(task.get("evaluators") or []),
        })
    return rows


def _regime(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    covered, skills, A = support_matrix(rows)
    result = optimal_target_package_ratio(rows)
    if not result.get("pass"):
        raise RuntimeError(f"R* failed for {name}: {result.get('reason')}")
    uniform = A.sum(axis=1)
    return {
        "regime": name,
        "tasks": len(covered),
        "skills": len(skills),
        "skill_names": skills,
        "multi_skill_tasks": int((A.sum(axis=1) > 1).sum()),
        "multi_skill_fraction": float((A.sum(axis=1) > 1).mean()),
        "minimum_oracle_set_size": int(A.sum(axis=1).min()),
        "maximum_oracle_set_size": int(A.sum(axis=1).max()),
        "uniform_oracle_set_exposure_ratio": float(uniform.max() / uniform.min()),
        "oracle_set_R_star_analogue": float(result["ratio"]),
        "optimal_active_skills": int(sum(float(v) > 1e-9 for v in (result.get("weights") or {}).values())),
    }


def build(repo: Path = DEFAULT_REPO) -> dict[str, Any]:
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    readme = repo / "benchmark" / "AgentSkillOS_bench" / "README.md"
    executor = repo / "src" / "workflow" / "executor.py"
    models = repo / "src" / "workflow" / "models.py"
    readme_text = readme.read_text(encoding="utf-8")
    executor_text = executor.read_text(encoding="utf-8")
    models_text = models.read_text(encoding="utf-8")
    rows = _rows(repo)
    categories = sorted({row["category"] for row in rows})
    regimes = [_regime("full", rows)] + [
        _regime(category, [row for row in rows if row["category"] == category])
        for category in categories
    ]
    degree = Counter(len(row["accepted_skill_ids"]) for row in rows)
    all_skills = sorted({skill for row in rows for skill in row["accepted_skill_ids"]})
    full = regimes[0]
    residual_categories = [row["regime"] for row in regimes[1:] if row["oracle_set_R_star_analogue"] > 1.0 + 1e-9]
    equalizable_categories = [row["regime"] for row in regimes[1:] if abs(row["oracle_set_R_star_analogue"] - 1.0) <= 1e-9]
    preflight = {
        "task_count_30": len(rows) == 30,
        "five_categories_six_each": len(categories) == 5 and all(sum(r["category"] == c for r in rows) == 6 for c in categories),
        "all_tasks_have_nonempty_oracle_skill_list": all(bool(row["accepted_skill_ids"]) for row in rows),
        "benchmark_readme_calls_skills_expected_to_retrieve_and_use": "Skills the agent is expected to retrieve and use" in readme_text,
        "specified_mode_passes_task_skills_directly": 'if tc.skill_mode == "specified":' in executor_text and "skills = tc.skills" in executor_text,
        "specified_mode_documented_as_user_specified_skills": '"specified" = use user-specified skills' in models_text,
    }
    if not all(preflight.values()):
        raise RuntimeError(f"AgentSkillOS oracle-set preflight failed: {preflight}")
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "agentskillos-author-oracle-set-analogue",
        "source": {
            "paper": "Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale",
            "arxiv": "2603.02176",
            "repo": "https://github.com/ynulihao/AgentSkillOS",
            "author_commit": commit,
            "benchmark_readme_sha256": sha(readme),
            "specified_executor_sha256": sha(executor),
            "task_model_sha256": sha(models),
        },
        "preflight": preflight,
        "task_count": len(rows),
        "category_counts": dict(sorted(Counter(row["category"] for row in rows).items())),
        "unique_oracle_skill_names": len(all_skills),
        "oracle_set_size_distribution": {str(k): int(v) for k, v in sorted(degree.items())},
        "regimes": regimes,
        "headline": {
            "tasks": len(rows),
            "categories": len(categories),
            "unique_oracle_skills": len(all_skills),
            "multi_skill_tasks": full["multi_skill_tasks"],
            "full_uniform_exposure_ratio": full["uniform_oracle_set_exposure_ratio"],
            "full_oracle_set_R_star_analogue": full["oracle_set_R_star_analogue"],
            "residual_categories": residual_categories,
            "equalizable_categories": equalizable_categories,
            "interpretation": "An independent author-specified multi-skill oracle graph contains both residual and exactly equalizable category geometries. Multi-skill prevalence alone does not determine the oracle-set realizability analogue.",
        },
        "decision": "QUALIFY_AUTHOR_ORACLE_SET_ANALOGUE_ONLY",
        "scientific_boundary": "AgentSkillOS task.skills is an author-specified/oracle selection set used to bypass discovery, not a complete executable semantic-support relation. Omitted skills are not proven incapable of supporting a task. Therefore this graph is an oracle-set geometry analogue only and cannot serve as a second exact STRI support certificate.",
        "new_support_annotations": 0,
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
    }


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "regime", "tasks", "skills", "multi_skill_tasks", "multi_skill_fraction",
            "minimum_oracle_set_size", "maximum_oracle_set_size",
            "uniform_oracle_set_exposure_ratio", "oracle_set_R_star_analogue", "optimal_active_skills",
        ])
        writer.writeheader()
        for row in payload["regimes"]:
            writer.writerow({key: row[key] for key in writer.fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    payload = build(args.repo)
    write_outputs(payload, args.json, args.csv)
    print(json.dumps({"headline": payload["headline"], "decision": payload["decision"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
