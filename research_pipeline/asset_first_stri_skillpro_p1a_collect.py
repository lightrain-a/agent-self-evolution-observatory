from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def write_new_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, sort_keys=True, indent=2)
            fh.write("\n")
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def build_focal_skill(Skill):
    # Exact pinned-source semantics from Skills/skill_pool.py @ 3be7a9be...
    return Skill(
        name="HypothesisElimination",
        initiation="When multiple past guesses with feedback exist and more than one hidden hypothesis remains plausible.",
        policy=[
            "Enumerate the main plausible hypotheses consistent with all past feedback.",
            "Eliminate hypotheses that contradict any feedback in the history.",
            "Identify what information is still uncertain among the remaining hypotheses.",
            "Choose an action that best distinguishes among these remaining hypotheses.",
        ],
        termination="An action aimed at reducing hypothesis uncertainty is selected.",
    )


class ForcedFocalPool:
    """Collection-only selector isolation required by the frozen P1a contract."""

    def __init__(self, focal):
        self.focal = focal

    def select_skill(self, **_: Any):
        return self.focal

    def get_all(self):
        return [self.focal]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--runtime-python", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--episodes", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.episodes != 6:
        raise SystemExit("Frozen contract requires exactly 6 P1a episodes")
    if args.seed != 42:
        raise SystemExit("Frozen contract requires seed=42")

    source = Path(args.source).resolve()
    out = Path(args.output_dir).resolve()
    if out.exists():
        raise SystemExit(f"Refuse overwrite existing P1a run directory: {out}")
    out.mkdir(parents=True, exist_ok=False)

    sys.path.insert(0, str(source))
    import swanlab
    from data_structures import Skill
    from run import SkillMDP
    from utils.local_llm import LocalLLM
    from utils.utils import set_seed

    swanlab.init(mode="disabled", project="STRI-SkillPro-P1a")
    set_seed(args.seed)

    focal = build_focal_skill(Skill)
    focal_semantics = {
        "initiation": focal.initiation,
        "policy": focal.policy,
        "termination": focal.termination,
    }
    focal_semantic_sha256 = sha256_json(focal_semantics)

    mdp = SkillMDP.__new__(SkillMDP)
    mdp.args = SimpleNamespace(
        MDP_type="SMDP",
        skill_select_k=1,
        select_type="FORCED_FOCAL_CONTRACT",
    )
    mdp.warm_up_flag = False
    mdp.record_tokens = True
    mdp.task_baselines = {"Mastermind-v0": 0.0}
    mdp.skill_pool = ForcedFocalPool(focal)
    mdp.llm_policy = LocalLLM(
        model_path=str(Path(args.model).resolve()),
        use_vllm=True,
        vllm_gpu_util=0.75,
    )

    manifest = {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "stage": "SKILLPRO_P1A_REAL_EVIDENCE_COLLECTION",
        "source": str(source),
        "runtime_python": args.runtime_python,
        "model": str(Path(args.model).resolve()),
        "seed": args.seed,
        "episode_count": args.episodes,
        "environment": "Mastermind-v0",
        "focal_skill": focal.name,
        "focal_semantics": focal_semantics,
        "focal_semantic_sha256": focal_semantic_sha256,
        "selection_isolation": "ForcedFocalPool always returns the pinned HypothesisElimination Skill; author run_single_episode remains unchanged.",
        "swanlab_mode": "disabled",
        "episodes": [],
    }
    write_new_json(out / "manifest.pre.json", manifest)

    for ep in range(1, args.episodes + 1):
        reward, used_skills, exp, usage_history = mdp.run_single_episode("Mastermind-v0", epsilon=0.0)
        exp_dict = dataclasses.asdict(exp)
        semantic_evidence = {
            "reward": exp_dict["reward"],
            "trajectory": exp_dict["trajectory"],
            "env_name": exp_dict["env_name"],
            "transitions": exp_dict["transitions"],
            "step_count": exp_dict["step_count"],
            "total_added_tokens": exp_dict["total_added_tokens"],
        }
        record = {
            "episode_index": ep,
            "runtime_valid": bool(exp_dict["transitions"]) and exp_dict["step_count"] > 0,
            "reward": reward,
            "used_skill_names": [s.name for s in used_skills],
            "usage_history": usage_history,
            "experience": exp_dict,
            "semantic_evidence_sha256": sha256_json(semantic_evidence),
            "experience_full_sha256": sha256_json(exp_dict),
        }
        write_new_json(out / f"episode-{ep:02d}.json", record)
        manifest["episodes"].append({
            "episode_index": ep,
            "file": f"episode-{ep:02d}.json",
            "runtime_valid": record["runtime_valid"],
            "reward": reward,
            "semantic_evidence_sha256": record["semantic_evidence_sha256"],
            "experience_full_sha256": record["experience_full_sha256"],
        })
        if not record["runtime_valid"]:
            manifest["decision"] = "COLLECTION_INVALID_STOP_NO_REPLACEMENT"
            write_new_json(out / "manifest.final.json", manifest)
            return 2

    manifest["all_runtime_valid"] = all(x["runtime_valid"] for x in manifest["episodes"])
    manifest["decision"] = "P1A_SIX_REAL_EXPERIENCES_FROZEN" if manifest["all_runtime_valid"] else "COLLECTION_INVALID"
    manifest["aggregate_semantic_evidence_sha256"] = sha256_json(
        [x["semantic_evidence_sha256"] for x in manifest["episodes"]]
    )
    write_new_json(out / "manifest.final.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
