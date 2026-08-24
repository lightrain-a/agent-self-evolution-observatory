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

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = Path(os.environ.get("SKILLSBENCH_REPO", str(ROOT / "external" / "skillsbench")))
DEFAULT_JSON = ROOT / "generated" / "asset-first-stri-skillsbench-support-qualification-20260824.json"
DEFAULT_CSV = ROOT / "generated" / "asset-first-stri-skillsbench-support-qualification-20260824.csv"
EXPECTED_COMMIT = "9a1f4dd5f7659f75707435da3ce854b6e48321d1"


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---") or "\n---\n" not in text[3:]:
        return {}
    _, block, _ = text.split("---", 2)
    value = yaml.safe_load(block) or {}
    return value if isinstance(value, dict) else {}


def build(repo: Path = DEFAULT_REPO) -> dict[str, Any]:
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if commit != EXPECTED_COMMIT:
        raise RuntimeError(f"SkillsBench commit drift: {commit}")
    task_root = repo / "tasks"
    rows = []
    for task_dir in sorted(p for p in task_root.iterdir() if p.is_dir() and (p / "task.md").is_file()):
        meta = _frontmatter(task_dir / "task.md")
        metadata = meta.get("metadata") if isinstance(meta.get("metadata"), dict) else {}
        required = sorted(str(x) for x in (metadata.get("required_skills") or []))
        skill_root = task_dir / "environment" / "skills"
        present = sorted(p.name for p in skill_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()) if skill_root.is_dir() else []
        rows.append({
            "task": task_dir.name,
            "category": str(metadata.get("category") or ""),
            "required_skills": required,
            "task_local_skill_dirs": present,
            "required_count": len(required),
            "task_local_count": len(present),
            "exact_match": required == present,
        })
    required_counts = Counter(row["required_count"] for row in rows)
    present_counts = Counter(row["task_local_count"] for row in rows)
    categories = Counter(row["category"] for row in rows)
    mismatch = sum(not row["exact_match"] for row in rows)
    required_empty = sum(row["required_count"] == 0 for row in rows)
    local_empty = sum(row["task_local_count"] == 0 for row in rows)
    unique_names = {s for row in rows for s in row["task_local_skill_dirs"]}
    decision = "STOP_AS_EXACT_SUPPORT_SUBSTRATE"
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "skillsbench-support-qualification",
        "source": {"repo": "https://github.com/benchflow-ai/skillsbench", "commit": commit},
        "summary": {
            "tasks": len(rows),
            "required_skills_empty_tasks": required_empty,
            "task_local_skills_empty_tasks": local_empty,
            "required_vs_task_local_exact_match_tasks": len(rows) - mismatch,
            "required_vs_task_local_mismatch_tasks": mismatch,
            "task_local_skill_files": sum(row["task_local_count"] for row in rows),
            "unique_task_local_skill_names": len(unique_names),
            "required_count_distribution": {str(k): v for k, v in sorted(required_counts.items())},
            "task_local_count_distribution": {str(k): v for k, v in sorted(present_counts.items())},
            "category_counts": dict(sorted(categories.items())),
        },
        "rows": rows,
        "decision": decision,
        "reason": "Task-local skill availability and metadata required_skills are not the same observable: 79/87 task records disagree and 75/87 required_skills lists are empty while every task has at least one local skill directory. Treating task-local availability as complete semantic support would therefore invent negative support labels for absent skills.",
        "reopen_condition": "Use SkillsBench as an exact STRI support substrate only if an independently validated query-by-skill support/acceptability matrix is released or constructed under a preregistered labeling protocol; task-local availability alone is insufficient.",
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
    }


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["task", "category", "required_count", "task_local_count", "exact_match", "required_skills", "task_local_skill_dirs"]
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({**{k: row[k] for k in fields[:5]}, "required_skills": ";".join(row["required_skills"]), "task_local_skill_dirs": ";".join(row["task_local_skill_dirs"])})


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo", type=Path, default=DEFAULT_REPO); parser.add_argument("--json", type=Path, default=DEFAULT_JSON); parser.add_argument("--csv", type=Path, default=DEFAULT_CSV); args = parser.parse_args()
    payload = build(args.repo); write_outputs(payload, args.json, args.csv); print(json.dumps({"summary": payload["summary"], "decision": payload["decision"], "json": str(args.json), "csv": str(args.csv)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
