from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def analyze(*, author_repo: Path, structural_witness: Path) -> dict[str, Any]:
    qgen = author_repo / "question_generate" / "question_generate.py"
    library = author_repo / "skill_library" / "library.py"
    commit = subprocess.check_output(["git", "-C", str(author_repo), "rev-parse", "HEAD"], text=True).strip()
    qtext = qgen.read_text(encoding="utf-8")
    ltext = library.read_text(encoding="utf-8")

    sample_pos = qtext.find("skill = sample_skill(")
    prompt_pos = qtext.find("chat = build_questioner_messages(expanded_skill")
    if sample_pos < 0 or prompt_pos < 0 or not sample_pos < prompt_pos:
        raise RuntimeError("author question-generation call order is not sample_skill -> build_questioner_messages")
    if "generator.choices(list(skills), weights=weights, k=1)" not in ltext:
        raise RuntimeError("author sample_skill no longer selects exactly one package from categorical weights")
    if not all(token in ltext for token in ("quality_multiplier(skill)", "exploration_multiplier(skill)", "weights.append(weight)")):
        raise RuntimeError("author sampling_weights contract changed")

    witness = load_json(structural_witness)
    lower_bound = float(
        witness.get("global_nonnegative_package_weight_exposure_ratio_lower_bound")
        or witness.get("tight_global_package_exposure_ratio_lower_bound")
        or 0.0
    )
    witness_count = int(witness.get("witness_count") or 0)
    if witness_count < 1 or lower_bound <= 1.0:
        raise RuntimeError("structural witness does not establish a nontrivial package-weight lower bound")

    return {
        "schema_version": "1.0",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "analysis_type": "decision-time controller-class reduction theorem",
        "author_asset": {
            "repo": str(author_repo),
            "commit": commit,
            "question_generate_sha256": sha256(qgen),
            "skill_library_sha256": sha256(library),
        },
        "verified_causal_order": "sample one skill package before build_questioner_messages(skill); the generated task therefore does not exist at the upstream curriculum decision time",
        "verified_action_space": "one package identity selected by categorical generator.choices over nonnegative sampling_weights",
        "same_information_class": {
            "allowed": [
                "frozen current skill library/package metadata",
                "precomputed support/applicability fingerprints",
                "skill-level quality/exploration/decay statistics",
                "randomness available before task generation",
            ],
            "forbidden": ["future generated task", "post-generation validator outcome", "hidden downstream reward"],
        },
        "theorem": {
            "name": "Pre-context single-package controller reduction",
            "statement": "At any frozen pre-task library/statistics state z, every randomized controller that must choose exactly one package before the task exists induces only a categorical probability vector p(s|z). For a released semantic support row x with package-incidence set A(x), its additive package exposure is E_z(x)=sum_{s in A(x)} p(s|z). Therefore, pointwise in z, the full same-information class of pre-context single-package controllers is exactly the nonnegative global package-weight class already audited by the structural lower bound.",
            "consequence": f"Because the released Skill-SP support graph contains {witness_count} mandatory-overlap witness pairs, every such controller has max/min positive semantic-context exposure ratio >= {lower_bound:.1f} on the frozen support graph. Neural capacity, bandit learning, or a more complex rule cannot remove this bound without changing the action space or using post-decision information.",
        },
        "strongest_reduction_verdict": "PRE_CONTEXT_SINGLE_PACKAGE_CONTROLLER_CLASS_REDUCED_TO_GLOBAL_WEIGHTS",
        "remaining_method_competitors": [
            "support-conditioned realization using the same frozen support information",
            "matched validator-gated/rejection realization with the same proposer/validator call budget",
            "post-context context-conditioned router for retrieval/credit surfaces",
        ],
        "claim_boundary": "This is a control-law/class-reduction result on the released support graph. It does not establish downstream task-performance harm, end-of-evolution utility gain, or that SQC beats matched support-conditioned realization.",
        "paper_design_authorized": False,
        "method_execution_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author-repo", type=Path, required=True)
    ap.add_argument("--structural-witness", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = analyze(author_repo=args.author_repo, structural_witness=args.structural_witness)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": result["strongest_reduction_verdict"], "commit": result["author_asset"]["commit"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
