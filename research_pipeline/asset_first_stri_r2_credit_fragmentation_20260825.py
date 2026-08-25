from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-contract-20260825.json"
OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"
CSV_OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.csv"
AUTHOR_REPO = Path("/data/wyt/agent2-asset-first-external/skill-self-play-mechanism-20260824")
EXPECTED_COMMIT = "bb693c89fee66e1f824d6a777759a49b7a295a83"

FOCAL_NAME = "semantic-focal-skill"
BACKGROUND_NAME = "background-skill"
SEMANTIC_FEEDBACK = tuple({"p_hat": 0.90, "consistency": True} for _ in range(8))


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _canonical_sha(value: Any) -> str:
    return _sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def _skill(skill_id: str, name: str) -> dict[str, Any]:
    return {
        "id": skill_id,
        "name": name,
        "description": "Frozen synthetic controller-level skill used only to replay released per-ID stats and pruning logic.",
        "example": "controller-level deterministic replay",
        "added_iteration": 1,
        "stats": {},
    }


def _load_author_module(tmp: Path):
    os.environ["SKILL_SP_COPY_LIBRARY_TO_STORAGE"] = "0"
    os.environ["SKILL_SP_SYNC_INITIAL_PACKAGES"] = "0"
    os.environ["SKILL_SP_MATERIALIZE_PACKAGES"] = "0"
    os.environ["SKILL_SP_REFRESH_INITIAL_SKILLS"] = "0"
    os.environ["SKILL_SP_LOCAL_LOCK_DIR"] = str(tmp / "locks")
    if str(AUTHOR_REPO) not in sys.path:
        sys.path.insert(0, str(AUTHOR_REPO))
    module = importlib.import_module("skill_library.library")
    return module


def _write_library(path: Path, skills: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(skills, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _semantic_feedback_hash() -> str:
    return _canonical_sha(list(SEMANTIC_FEEDBACK))


def _records_for(ids: list[str]) -> list[dict[str, Any]]:
    records = []
    for i, evidence in enumerate(SEMANTIC_FEEDBACK):
        skill_id = ids[i % len(ids)]
        records.append({"skill_id": skill_id, **evidence})
    return records


def _stats_by_id(module, library_path: Path) -> dict[str, dict[str, Any]]:
    skills = module.load_skill_library(str(library_path), create=False)
    return {str(skill["id"]): module.normalize_skill_stats(skill.get("stats", {})) for skill in skills}


def _sampling_semantic_probability(module, library_path: Path, focal_ids: set[str]) -> float:
    skills = module.load_skill_library(str(library_path), create=False)
    if not skills:
        return 0.0
    weights = module.sampling_weights(skills, current_iteration=2, use_quality=True, use_exploration=True, use_decay=False)
    total = float(sum(weights))
    if total <= 0:
        return 0.0
    return float(sum(w for skill, w in zip(skills, weights) if str(skill["id"]) in focal_ids) / total)


def _run_native_arm(module, root: Path, arm: str, focal_ids: list[str], feedback_ids: list[str]) -> dict[str, Any]:
    library = root / f"{arm}.json"
    skills = [_skill(fid, FOCAL_NAME) for fid in focal_ids] + [_skill("background", BACKGROUND_NAME)]
    _write_library(library, skills)
    records = _records_for(feedback_ids)
    module.update_skill_stats_from_records(records, path=str(library), iteration=1)
    pre_prune_stats = _stats_by_id(module, library)
    retired = module.prune_easy_skills(path=str(library), preserve_initial_skills=True)
    active = module.load_skill_library(str(library), create=False)
    active_ids = {str(skill["id"]) for skill in active}
    retired_ids = {str(skill["id"]) for skill in retired}
    focal_active = any(fid in active_ids for fid in focal_ids)
    return {
        "arm": arm,
        "focal_ids": focal_ids,
        "feedback_record_count": len(records),
        "semantic_feedback_sha256": _semantic_feedback_hash(),
        "pre_prune_stats": {fid: pre_prune_stats[fid] for fid in focal_ids},
        "retired_focal_ids": sorted(retired_ids.intersection(focal_ids)),
        "active_focal_ids": sorted(active_ids.intersection(focal_ids)),
        "focal_semantic_class_active": focal_active,
        "post_update_focal_native_sampling_probability": _sampling_semantic_probability(module, library, set(focal_ids)),
        "library_sha256": _sha_file(library),
    }


def build(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_sha = _sha_file(CONTRACT)
    head = _git_head(AUTHOR_REPO)
    if head != EXPECTED_COMMIT:
        raise RuntimeError(f"author release drift: {head} != {EXPECTED_COMMIT}")
    source_file = AUTHOR_REPO / "skill_library/library.py"

    with tempfile.TemporaryDirectory(prefix="stri-r2-credit-fragmentation-") as td:
        tmp = Path(td)
        module = _load_author_module(tmp)

        # Runtime verification of the released pruning defaults used by the frozen contract.
        defaults = module.prune_easy_skills.__defaults__
        if defaults is None:
            raise RuntimeError("released prune_easy_skills defaults unavailable")
        # path, min_attempts, avg_p_hat_threshold, too_easy_rate_threshold, archive_path, preserve_initial_skills
        observed_defaults = {
            "min_attempts": int(defaults[1]),
            "avg_p_hat_threshold": float(defaults[2]),
            "too_easy_rate_threshold": float(defaults[3]),
        }
        expected_defaults = {
            "min_attempts": 8,
            "avg_p_hat_threshold": 0.75,
            "too_easy_rate_threshold": 0.6,
        }
        if observed_defaults != expected_defaults:
            raise RuntimeError(f"released pruning defaults drift: {observed_defaults}")

        canonical = _run_native_arm(module, tmp, "A_canonical_native", ["focal"], ["focal"])
        split = _run_native_arm(module, tmp, "B_split2_native", ["focal_a", "focal_b"], ["focal_a", "focal_b"])

        # Quotient-credit control: the split representation remains conceptual, but the identical
        # semantic evidence is merged to one class representative before the same released gate.
        quotient_rep = _run_native_arm(module, tmp, "C_split2_quotient_credit_representative", ["focal_q"], ["focal_q"])
        quotient = {
            **quotient_rep,
            "arm": "C_split2_quotient_credit",
            "represented_member_ids": ["focal_a", "focal_b"],
            "class_representative_id": "focal_q",
            "projected_active_focal_ids": [] if not quotient_rep["focal_semantic_class_active"] else ["focal_a", "focal_b"],
            "focal_semantic_class_active": quotient_rep["focal_semantic_class_active"],
            "post_update_focal_native_sampling_probability": 0.0 if not quotient_rep["focal_semantic_class_active"] else quotient_rep["post_update_focal_native_sampling_probability"],
        }

    same_feedback = len({canonical["semantic_feedback_sha256"], split["semantic_feedback_sha256"], quotient["semantic_feedback_sha256"]}) == 1
    pass_gate = (
        same_feedback
        and canonical["focal_semantic_class_active"] is False
        and split["focal_semantic_class_active"] is True
        and quotient["focal_semantic_class_active"] is False
        and canonical["pre_prune_stats"]["focal"]["attempts"] == 8
        and split["pre_prune_stats"]["focal_a"]["attempts"] == 4
        and split["pre_prune_stats"]["focal_b"]["attempts"] == 4
        and quotient["pre_prune_stats"]["focal_q"]["attempts"] == 8
    )
    decision = "PASS_RELEASED_CREDIT_FRAGMENTATION_MECHANISM" if pass_gate else "STOP_REDESIGN_FROZEN_P0_FAILED"

    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "experiment_id": contract["experiment_id"],
        "stage": "MECHANISM_REDESIGN_DETERMINISTIC_P0_RESULT",
        "decision": decision,
        "pass_gate": pass_gate,
        "contract_sha256": contract_sha,
        "contract_git_commit": "873a3685066fca11c3bf0853484088e6256e9f81",
        "author_release": {
            "repo": contract["first_party_release"]["repo"],
            "commit": head,
            "source_file": "skill_library/library.py",
            "source_file_sha256": _sha_file(source_file),
            "observed_pruning_defaults": observed_defaults,
        },
        "semantic_feedback": {
            "records": len(SEMANTIC_FEEDBACK),
            "values": list(SEMANTIC_FEEDBACK),
            "semantic_feedback_sha256": _semantic_feedback_hash(),
            "identical_across_arms": same_feedback,
            "selection_or_retrieval_executed_before_feedback": False,
        },
        "arms": {
            "A_canonical_native": canonical,
            "B_split2_native": split,
            "C_split2_quotient_credit": quotient,
        },
        "headline": {
            "canonical_attempts": canonical["pre_prune_stats"]["focal"]["attempts"],
            "split_attempts_per_id": [split["pre_prune_stats"]["focal_a"]["attempts"], split["pre_prune_stats"]["focal_b"]["attempts"]],
            "canonical_focal_active_after_prune": canonical["focal_semantic_class_active"],
            "split_focal_active_after_prune": split["focal_semantic_class_active"],
            "quotient_credit_focal_active_after_prune": quotient["focal_semantic_class_active"],
            "canonical_future_focal_sampling_probability": canonical["post_update_focal_native_sampling_probability"],
            "split_future_focal_sampling_probability": split["post_update_focal_native_sampling_probability"],
            "quotient_credit_future_focal_sampling_probability": quotient["post_update_focal_native_sampling_probability"],
        },
        "mechanism_interpretation": "With selection removed and semantic feedback held byte-identical, the released per-ID sufficient-statistic containers and thresholded pruning gate do not commute with exact identity refinement. Evidence fragmentation alone changes the persistent active skill library; quotient-credit restores the canonical class decision.",
        "claim_boundary": "Deterministic controller-level replay of one released Skill-SP update/pruning mechanism. This does not establish downstream task utility, prevalence under endogenous sampling, cross-system generality, or task-general behavioral propagation.",
        "next_gate": "Closest-work/reduction audit plus natural released-state prevalence check before any R2 manuscript rewrite or agent/model experiment.",
        "new_model_calls": 0,
        "new_agent_runs": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["result_canonical_sha256"] = _canonical_sha(result)
    return result


def write_outputs(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    result = build(project_root)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = []
    for key in ("A_canonical_native", "B_split2_native", "C_split2_quotient_credit"):
        arm = result["arms"][key]
        rows.append({
            "arm": key,
            "focal_active_after_prune": arm["focal_semantic_class_active"],
            "active_focal_ids": ";".join(arm.get("active_focal_ids") or arm.get("projected_active_focal_ids") or []),
            "retired_focal_ids": ";".join(arm.get("retired_focal_ids") or []),
            "future_focal_sampling_probability": arm["post_update_focal_native_sampling_probability"],
            "semantic_feedback_sha256": arm["semantic_feedback_sha256"],
        })
    import csv
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    return result


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
