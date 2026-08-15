from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_key(skill: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(skill.get("title") or ""),
        str(skill.get("principle") or ""),
        str(skill.get("when_to_apply") or ""),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    c = load(args.contract)
    repo = Path(c["author_asset"]["repo"])
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    checks = {
        "commit": commit == c["author_asset"]["commit"],
        "skills_only_memory_sha": sha(repo / "agent_system/memory/skills_only_memory.py") == c["author_asset"]["skills_only_memory_sha256"],
        "skill_updater_sha": sha(repo / "agent_system/memory/skill_updater.py") == c["author_asset"]["skill_updater_sha256"],
        "skillbank_sha": sha(repo / "memory_data/alfworld/claude_style_skills.json") == c["author_asset"]["alfworld_skillbank_sha256"],
        "released_memories_sha": sha(repo / "memory_data/alfworld/generated_memories_alfworld_total.json") == c["author_asset"]["alfworld_released_memories_sha256"],
    }
    if not all(checks.values()):
        raise RuntimeError(f"preflight hash failure: {checks}")
    # Direct-load the two pinned author modules without importing
    # agent_system.memory.__init__, which eagerly imports optional embedding
    # retrieval dependencies unrelated to this frozen template-mode probe.
    memory_dir = repo / "agent_system/memory"
    probe_pkg = "_skillrl_memory_probe"
    pkg = types.ModuleType(probe_pkg)
    pkg.__path__ = [str(memory_dir)]
    sys.modules[probe_pkg] = pkg
    for module_name in ("base", "skills_only_memory"):
        module_path = memory_dir / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location(f"{probe_pkg}.{module_name}", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot direct-load pinned author module: {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    SkillsOnlyMemory = sys.modules[f"{probe_pkg}.skills_only_memory"].SkillsOnlyMemory

    bank_path = repo / "memory_data/alfworld/claude_style_skills.json"
    pristine_bank = load(bank_path)
    tasks_raw = load(repo / "memory_data/alfworld/generated_memories_alfworld_total.json")
    tasks = [str(x["contextual_description"]) for x in tasks_raw]
    if len(tasks) != int(c["selection"]["task_count"]):
        raise RuntimeError(f"task-count drift: {len(tasks)}")
    general = pristine_bank.get("general_skills", [])
    if len(general) != 12:
        raise RuntimeError(f"general skill count drift: {len(general)}")

    with contextlib.redirect_stdout(io.StringIO()):
        baseline_memory = SkillsOnlyMemory(str(bank_path), retrieval_mode="template")
    baseline = []
    for task in tasks:
        r = baseline_memory.retrieve(task, top_k=6)
        general_semantics = [semantic_key(s) for s in r["general_skills"]]
        baseline.append({
            "task": task,
            "prompt": baseline_memory.format_for_prompt(r),
            "general_semantics": general_semantics,
            "general_unique": set(general_semantics),
        })

    target_results: list[dict[str, Any]] = []
    total_prompt_comparisons = 0
    total_prompt_changes = 0
    admitted = 0
    semantic_set_change_targets = 0
    unique_count_reduction_targets = 0

    for target_index, target in enumerate(general):
        clone = copy.deepcopy(target)
        clone["skill_id"] = f"dyn_{900 + target_index:03d}"
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=True) as tmp:
            json.dump(pristine_bank, tmp)
            tmp.flush()
            with contextlib.redirect_stdout(io.StringIO()):
                mem = SkillsOnlyMemory(tmp.name, retrieval_mode="template")
                added = mem.add_skills([clone], category="general")
            admitted += int(added == 1)

            changed = 0
            set_changed = 0
            unique_reduced = 0
            example = None
            for row_idx, task in enumerate(tasks):
                r = mem.retrieve(task, top_k=6)
                prompt = mem.format_for_prompt(r)
                sem = [semantic_key(s) for s in r["general_skills"]]
                sem_set = set(sem)
                base = baseline[row_idx]
                total_prompt_comparisons += 1
                if prompt != base["prompt"]:
                    total_prompt_changes += 1
                    changed += 1
                if sem_set != base["general_unique"]:
                    set_changed += 1
                if len(sem_set) < len(base["general_unique"]):
                    unique_reduced += 1
                if example is None and (prompt != base["prompt"] or sem_set != base["general_unique"]):
                    example = {
                        "task": task,
                        "baseline_general_titles": [x[0] for x in base["general_semantics"]],
                        "counterfactual_general_titles": [x[0] for x in sem],
                        "baseline_unique_general_count": len(base["general_unique"]),
                        "counterfactual_unique_general_count": len(sem_set),
                    }

            target_set_changes = set_changed > 0
            target_unique_reduction = unique_reduced > 0
            semantic_set_change_targets += int(target_set_changes)
            unique_count_reduction_targets += int(target_unique_reduction)
            target_results.append({
                "target_skill_id": target.get("skill_id"),
                "target_title": target.get("title"),
                "clone_skill_id": clone["skill_id"],
                "clone_content_exact": semantic_key(clone) == semantic_key(target),
                "clone_admitted": added == 1,
                "tasks": len(tasks),
                "prompt_changed_rows": changed,
                "prompt_changed_fraction": changed / len(tasks),
                "unique_semantic_retrieval_set_changed_rows": set_changed,
                "unique_semantic_retrieval_set_changed_fraction": set_changed / len(tasks),
                "unique_general_content_count_reduced_rows": unique_reduced,
                "unique_general_content_count_reduced_fraction": unique_reduced / len(tasks),
                "example": example,
            })

    gate = c["frozen_gate"]
    clone_admission_fraction = admitted / len(general)
    prompt_change_fraction = total_prompt_changes / total_prompt_comparisons
    gate_checks = {
        "clone_admission_fraction": {"actual": clone_admission_fraction, "required_min": gate["clone_admission_fraction_min"], "pass": clone_admission_fraction >= gate["clone_admission_fraction_min"]},
        "prompt_change_fraction": {"actual": prompt_change_fraction, "required_min": gate["prompt_change_fraction_min"], "pass": prompt_change_fraction >= gate["prompt_change_fraction_min"]},
        "targets_changing_unique_semantic_retrieval_set": {"actual": semantic_set_change_targets, "required_min": gate["targets_changing_unique_semantic_retrieval_set_min"], "pass": semantic_set_change_targets >= gate["targets_changing_unique_semantic_retrieval_set_min"]},
        "targets_reducing_unique_general_content_count": {"actual": unique_count_reduction_targets, "required_min": gate["targets_reducing_unique_general_content_count_min"], "pass": unique_count_reduction_targets >= gate["targets_reducing_unique_general_content_count_min"]},
    }
    positive = all(v["pass"] for v in gate_checks.values())
    result = {
        "schema_version": "1.0",
        "experiment_id": c["experiment_id"],
        "candidate_id": c["candidate_id"],
        "decision": "INDEPENDENT_SYSTEM_REPRESENTATION_SENSITIVITY_SUPPORTED" if positive else "STOP_SECOND_SYSTEM_REPLICATION_GATE_NOT_MET",
        "scientific_result_available": True,
        "primary_mechanism_positive": positive,
        "scientific_disposition": "REPLICATED_MECHANISM_NOVELTY_UNRESOLVED" if positive else "SKILLSP_SPECIFIC_ONLY",
        "preflight": checks,
        "tasks": len(tasks),
        "general_skill_targets": len(general),
        "clone_admitted_targets": admitted,
        "clone_admission_fraction": clone_admission_fraction,
        "prompt_comparisons": total_prompt_comparisons,
        "prompt_changed_comparisons": total_prompt_changes,
        "prompt_change_fraction": prompt_change_fraction,
        "targets_changing_unique_semantic_retrieval_set": semantic_set_change_targets,
        "targets_reducing_unique_general_content_count": unique_count_reduction_targets,
        "target_results": target_results,
        "checks": gate_checks,
        "semantic_library_change": "none up to an exact duplicate; every counterfactual adds only an exact content copy with a fresh dynamic ID",
        "strongest_reduction": c["strongest_reduction"],
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "gpu_hours": 0,
        "model_calls": 0,
        "author_commit": commit,
        "next_action": c["next_if_positive"] if positive else c["next_if_negative"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": result["decision"],
        "clone_admission_fraction": clone_admission_fraction,
        "prompt_change_fraction": prompt_change_fraction,
        "targets_changing_unique_semantic_retrieval_set": semantic_set_change_targets,
        "targets_reducing_unique_general_content_count": unique_count_reduction_targets,
        "checks": gate_checks,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
