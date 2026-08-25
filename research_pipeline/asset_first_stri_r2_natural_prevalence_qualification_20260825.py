from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = Path(os.environ.get(
    "STRI_R2_SKILLSP_REPO",
    "/data/wyt/agent-self-evolution-observatory/scout-assets/skill-self-play",
))
EXPECTED_COMMIT = "bb693c89fee66e1f824d6a777759a49b7a295a83"
OUTPUT = ROOT / "generated/asset-first-stri-r2-natural-prevalence-qualification-20260825.json"
MIRRORS = [
    Path("/data/wyt/agent-self-evolution-observatory/scout-assets/skill-self-play"),
    Path("/data/wyt/agent2-asset-first-external/skill-self-play-mechanism-20260824"),
    Path("/data/wyt/skill-self-play-agent3-20260816"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def extract_int(pattern: str, text: str, *, name: str) -> int:
    m = re.search(pattern, text)
    if not m:
        raise RuntimeError(f"missing {name}")
    return int(m.group(1))


def build(repo: Path = DEFAULT_REPO) -> dict[str, Any]:
    if not repo.is_dir():
        raise RuntimeError(f"Skill-SP repo missing: {repo}")
    commit = git(repo, "rev-parse", "HEAD")
    if commit != EXPECTED_COMMIT:
        raise RuntimeError(f"Skill-SP commit drift: {commit}")

    files = {
        "library": repo / "skill_library/library.py",
        "upload": repo / "question_evaluate/upload.py",
        "solver_loop": repo / "scripts/skill_solver_train.sh",
        "outer_loop": repo / "scripts/skill_main.sh",
        "train_launcher": repo / "train-tool-call-skill-qwen3-4b.sh",
        "gitignore": repo / ".gitignore",
    }
    for name, path in files.items():
        if not path.is_file():
            raise RuntimeError(f"missing first-party file {name}: {path}")

    lib = files["library"].read_text(encoding="utf-8")
    upload = files["upload"].read_text(encoding="utf-8")
    solver = files["solver_loop"].read_text(encoding="utf-8")
    outer = files["outer_loop"].read_text(encoding="utf-8")
    launcher = files["train_launcher"].read_text(encoding="utf-8")
    gitignore = files["gitignore"].read_text(encoding="utf-8")

    min_attempts = extract_int(r"SKILL_SP_EASY_SKILL_MIN_ATTEMPTS:-([0-9]+)", solver, name="prune min attempts")
    dataset_target = extract_int(r"SKILL_SP_SOLVER_DATASET_SIZE:-([0-9]+)", solver, name="solver dataset target")
    num_iterations = extract_int(r"SKILL_SP_NUM_ITERATIONS:-([0-9]+)", outer, name="self-play iterations")

    tracked = git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    tracked_runtime_states = sorted(
        p for p in tracked
        if p.endswith("/skills.json") or p == "skill_library/skills.json" or "retired" in p.lower() and p.endswith((".json", ".jsonl"))
    )
    initial_stats_paths = sorted(repo.glob("tool_call/packages/skill_*/stats.json")) + sorted(repo.glob("logical_reasoning/packages/skill_*/stats.json"))
    initial_stats = [json.loads(p.read_text(encoding="utf-8")) for p in initial_stats_paths]
    initial_nonzero_attempts = sum(int((row or {}).get("attempts", 0)) > 0 for row in initial_stats)

    mirror_rows = []
    for mirror in MIRRORS:
        row: dict[str, Any] = {"path": str(mirror), "present": mirror.is_dir()}
        if mirror.is_dir():
            try:
                row["commit"] = git(mirror, "rev-parse", "HEAD")
            except Exception:
                row["commit"] = ""
            evolved = sorted(
                str(p.relative_to(mirror))
                for p in mirror.rglob("*")
                if p.is_file() and (
                    p.name == "skills.json" or
                    ("retired" in p.name.lower() and p.suffix.lower() in {".json", ".jsonl"})
                )
            )
            row["evolved_runtime_state_files"] = evolved
            row["evolved_runtime_state_file_count"] = len(evolved)
        mirror_rows.append(row)

    checks = {
        "runtime_library_path_declared": "SKILL_SP_LIBRARY_PATH" in launcher and "skill_library/skills.json" in launcher,
        "runtime_library_ignored_by_git": "skill_library/skills.json" in gitignore,
        "feedback_stats_updated_in_official_loop": "--update_skill_stats" in solver and "update_skill_stats_from_records" in upload,
        "pruning_executed_in_official_loop": "--prune_easy_skills" in solver and "prune_easy_skills(" in upload,
        "per_id_attempts_persisted": 'stats["attempts"] = new_attempts' in lib,
        "per_id_avg_phat_persisted": 'stats["avg_p_hat"]' in lib,
        "retired_archive_written": "_default_retired_skill_path" in lib and 'f.write("\\n")' in lib,
        "five_iteration_default": num_iterations == 5,
        "default_prune_threshold_is_eight": min_attempts == 8,
        "default_solver_dataset_target_is_8000": dataset_target == 8000,
        "no_tracked_evolved_runtime_state": len(tracked_runtime_states) == 0,
        "all_released_package_stats_are_initial": initial_nonzero_attempts == 0,
        "no_evolved_runtime_state_in_three_local_release_mirrors": all(
            (not row.get("present")) or int(row.get("evolved_runtime_state_file_count") or 0) == 0
            for row in mirror_rows
        ),
    }
    if not all(checks.values()):
        raise RuntimeError("natural-prevalence qualification invariant failed: " + ", ".join(k for k, v in checks.items() if not v))

    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "object_id": "STRI-R2-CREDIT-FRAGMENTATION-NATURAL-PREVALENCE",
        "stage": "MECHANISM_REDESIGN_NATURAL_PREVALENCE_QUALIFICATION",
        "decision": "HOLD_NATURAL_PREVALENCE_UNRESOLVED_RUNTIME_OUTPUT_NOT_RELEASED",
        "pass_code_path_operational": True,
        "natural_prevalence_established": False,
        "author_release": {
            "repo": "https://github.com/Qwen-Applications/skill-self-play",
            "commit": commit,
            "file_sha256": {name: sha(path) for name, path in files.items()},
        },
        "released_loop": {
            "runtime_library_path": "${STORAGE_PATH}/skill_library/skills.json",
            "runtime_library_gitignored": True,
            "retired_archive_default": "${SKILL_SP_LIBRARY_PATH without extension}_retired.jsonl",
            "default_self_play_iterations": num_iterations,
            "default_solver_dataset_target_total_records": dataset_target,
            "default_prune_min_attempts_per_identity": min_attempts,
            "stats_updated_before_pruning": True,
            "stats_are_identity_local": True,
            "active_library_persists_into_later_iterations": True,
        },
        "release_inventory": {
            "tracked_runtime_state_paths": tracked_runtime_states,
            "tracked_runtime_state_count": len(tracked_runtime_states),
            "released_initial_stats_files": len(initial_stats_paths),
            "released_initial_stats_with_nonzero_attempts": initial_nonzero_attempts,
            "local_first_party_mirrors_checked": mirror_rows,
        },
        "opportunity_scale": {
            "threshold_M": min_attempts,
            "solver_dataset_target_total_records_per_collection": dataset_target,
            "dataset_target_to_threshold_ratio": dataset_target / min_attempts,
            "interpretation": "The released loop updates identity-local statistics on accepted skill-guided samples and uses M=8, while the default solver dataset target is 8000 total records. This supports that the trigger threshold is small relative to collection scale, but does not reveal the empirical per-skill attempt distribution or fragmentation-window prevalence.",
        },
        "checks": checks,
        "scientific_interpretation": "The first-party Skill-SP release operationalizes exactly the persistent state variables and per-ID pruning gate used by the R2 mechanism, so the mechanism is not an invented toy update rule. However, the public release intentionally gitignores runtime skills.json and does not include evolved skills.json or retired ledgers; three pinned local release mirrors likewise contain no evolved runtime state. Therefore natural entry frequency into M<=N<kM cannot be estimated from released artifacts.",
        "claim_boundary": "Supports first-party mechanism existence and trigger-opportunity plausibility only. It does not establish endogenous prevalence, downstream utility, cross-system generality, or task-general behavioral propagation.",
        "next_gate": "Keep R2 as a mechanism candidate with natural prevalence unresolved. Reopen prevalence only with a content-addressed evolved Skill-SP skills.json/retired ledger or a separately preregistered first-party run whose per-skill attempt distribution is frozen before evaluating the R2 phase law.",
        "new_model_calls": 0,
        "new_agent_runs": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["result_canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def write(repo: Path = DEFAULT_REPO, output: Path = OUTPUT) -> dict[str, Any]:
    result = build(repo)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(write(), ensure_ascii=False, indent=2))
