from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from .asset_first_stri_skillpro_p0 import (
    DEFAULT_THRESHOLD,
    SKILLPRO_ARCHIVE_SHA256,
    SKILLPRO_COMMIT,
    EXPECTED_SOURCE_SHA256,
    frozen_semantic_evidence,
    semantic_evidence_hash,
    sha256,
)


class DummyPool:
    def __init__(self, skills: Sequence[Any]):
        self.skills = list(skills)
        self.added: list[Any] = []

    def get_all(self):
        return list(self.skills)

    def add_skill(self, skill):
        self.skills.append(skill)
        self.added.append(skill)


def load_author_modules(source_root: Path):
    source_root = source_root.resolve()
    sys.path.insert(0, str(source_root))
    try:
        evolution = importlib.import_module("Skills.skill_evolution")
        structures = importlib.import_module("data_structures")
    except Exception:
        if sys.path and sys.path[0] == str(source_root):
            sys.path.pop(0)
        raise
    return evolution, structures


def make_probe_class(author_evolution, Skill):
    class ProbeSkillEvolution(author_evolution.SkillEvolution):
        """Execute the released scheduler unchanged while stubbing only post-readiness model hooks."""

        def __init__(self, threshold: int = DEFAULT_THRESHOLD):
            super().__init__(llm_agent=None, threshold=threshold, epsilon=0.2)
            self.probe_evolve_calls = 0
            self.probe_logprob_calls = 0

        def evolve(self, old_skill, sampled_experience):
            self.probe_evolve_calls += 1
            candidate = Skill(
                name=f"{old_skill.name}_probe_candidate",
                initiation=old_skill.initiation,
                policy=list(old_skill.policy),
                termination=old_skill.termination,
            )
            return candidate, "REFINE"

        def _compute_skill_logprobs(self, skill, states, actions, envs, build_prompt_fn):
            self.probe_logprob_calls += 1
            return author_evolution.np.zeros(len(states), dtype=float)

    return ProbeSkillEvolution


def make_skill(Skill, name: str):
    return Skill(
        name=name,
        initiation="frozen initiation",
        policy=["frozen policy step"],
        termination="frozen termination",
        frequency=15,
        avg_gain=0.0,
        maturity=4,
        success_count=0,
        last_evolved_iter=-100,
    )


def make_experiences(Experience, identities: Sequence[str]):
    evidence = frozen_semantic_evidence(len(identities))
    out = []
    for row, identity in zip(evidence, identities, strict=True):
        out.append(
            Experience(
                reward=float(row["reward"]),
                skill=identity,
                trajectory=str(row["trajectory"]),
                env_name=str(row["env_name"]),
                transitions=list(row["transitions"]),
            )
        )
    return evidence, out


def execute_once(ProbeSkillEvolution, Skill, Experience, identities: Sequence[str], active_names: Sequence[str]):
    evidence, experiences = make_experiences(Experience, identities)
    skills = [make_skill(Skill, name) for name in active_names]
    pool = DummyPool(skills)
    scheduler = ProbeSkillEvolution(threshold=DEFAULT_THRESHOLD)
    logs = scheduler.run_skill_evolution_with_verification(
        skill_pool=pool,
        new_experiences=experiences,
        build_prompt_fn=lambda state, skill_text, env: f"{state}|{skill_text}|{env}",
        baselines={"stri-skillpro-p0": 0.0},
        acceptance_margin=0.001,
        max_evolutions_per_step=2,
        best_of_n=1,
        current_iteration=100,
        ablation_type="none",
    )
    return {
        "semantic_evidence_sha256": semantic_evidence_hash(evidence),
        "identity_attribution": list(identities),
        "active_identities": list(active_names),
        "evolution_log_count": len(logs),
        "evolved_parents": [str(item.get("parent")) for item in logs],
        "actions": [str(item.get("action")) for item in logs],
        "probe_evolve_calls": scheduler.probe_evolve_calls,
        "probe_logprob_calls": scheduler.probe_logprob_calls,
        "added_candidate_count": len(pool.added),
        "buffer_counts_after_call": {key: len(value) for key, value in scheduler.experience_buffer.items()},
    }


def execute_late_dedup(ProbeSkillEvolution, Skill, Experience):
    evidence, experiences = make_experiences(Experience, ["skill_c_a"] * 3 + ["skill_c_b"] * 3)
    pool = DummyPool([make_skill(Skill, "skill_c_a"), make_skill(Skill, "skill_c_b")])
    scheduler = ProbeSkillEvolution(threshold=DEFAULT_THRESHOLD)

    first = scheduler.run_skill_evolution_with_verification(
        skill_pool=pool,
        new_experiences=experiences,
        build_prompt_fn=lambda state, skill_text, env: f"{state}|{skill_text}|{env}",
        baselines={"stri-skillpro-p0": 0.0},
        acceptance_margin=0.001,
        max_evolutions_per_step=2,
        best_of_n=1,
        current_iteration=100,
        ablation_type="none",
    )
    before = {key: len(value) for key, value in scheduler.experience_buffer.items()}

    # Identity-only semantic reunion after the released local gate: keep one alias,
    # deliberately do not merge evidence buffers. This is the location-specific
    # negative control, not a claim that the author maintenance literally performs
    # this exact operation on this synthetic pair.
    pool.skills = [skill for skill in pool.skills if skill.name == "skill_c_a"]
    second = scheduler.run_skill_evolution_with_verification(
        skill_pool=pool,
        new_experiences=[],
        build_prompt_fn=lambda state, skill_text, env: f"{state}|{skill_text}|{env}",
        baselines={"stri-skillpro-p0": 0.0},
        acceptance_margin=0.001,
        max_evolutions_per_step=2,
        best_of_n=1,
        current_iteration=101,
        ablation_type="none",
    )
    after = {key: len(value) for key, value in scheduler.experience_buffer.items()}
    return {
        "semantic_evidence_sha256": semantic_evidence_hash(evidence),
        "first_gate_log_count": len(first),
        "second_gate_after_identity_only_dedup_log_count": len(second),
        "buffer_counts_before_dedup": before,
        "buffer_counts_after_identity_only_dedup": after,
        "surviving_active_identities": [skill.name for skill in pool.skills],
        "probe_evolve_calls": scheduler.probe_evolve_calls,
        "probe_logprob_calls": scheduler.probe_logprob_calls,
    }


def source_hashes(source_root: Path) -> dict[str, str]:
    return {relative: sha256(source_root / relative) for relative in EXPECTED_SOURCE_SHA256}


def build_result(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    actual_hashes = source_hashes(source_root)
    if actual_hashes != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Skill-Pro source hashes do not match the frozen P0 pin")

    evolution, structures = load_author_modules(source_root)
    Skill = structures.Skill
    Experience = structures.Experience
    ProbeSkillEvolution = make_probe_class(evolution, Skill)

    canonical = execute_once(ProbeSkillEvolution, Skill, Experience, ["skill_c"] * 6, ["skill_c"])
    placebo = execute_once(ProbeSkillEvolution, Skill, Experience, ["skill_c_renamed"] * 6, ["skill_c_renamed"])
    exact_split = execute_once(
        ProbeSkillEvolution,
        Skill,
        Experience,
        ["skill_c_a"] * 3 + ["skill_c_b"] * 3,
        ["skill_c_a", "skill_c_b"],
    )
    pre_gate_quotient = execute_once(
        ProbeSkillEvolution,
        Skill,
        Experience,
        ["skill_c_a"] * 6,
        ["skill_c_a", "skill_c_b"],
    )
    late_dedup = execute_late_dedup(ProbeSkillEvolution, Skill, Experience)

    evidence_hash = canonical["semantic_evidence_sha256"]
    checks = {
        "source_hashes_match_frozen_pin": actual_hashes == EXPECTED_SOURCE_SHA256,
        "canonical_reaches_post_readiness_hooks": canonical["probe_evolve_calls"] == 1 and canonical["evolution_log_count"] == 1,
        "id_placebo_reaches_post_readiness_hooks": placebo["probe_evolve_calls"] == 1 and placebo["evolution_log_count"] == 1,
        "exact_split_returns_before_post_readiness_hooks": exact_split["probe_evolve_calls"] == 0 and exact_split["evolution_log_count"] == 0,
        "pre_gate_quotient_restores_author_scheduler_reachability": pre_gate_quotient["probe_evolve_calls"] == 1 and pre_gate_quotient["evolution_log_count"] == 1,
        "late_identity_only_dedup_still_returns_before_post_readiness_hooks": late_dedup["probe_evolve_calls"] == 0 and late_dedup["second_gate_after_identity_only_dedup_log_count"] == 0,
        "same_semantic_evidence_across_nonzero_arms": all(
            arm["semantic_evidence_sha256"] == evidence_hash
            for arm in (canonical, placebo, exact_split, pre_gate_quotient, late_dedup)
        ),
        "gpu_hidden_for_probe": os.environ.get("CUDA_VISIBLE_DEVICES") in {"", "-1"},
    }

    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "experiment_id": "ASSET-FIRST-STRI-SKILLPRO-AUTHOR-SCHEDULER-P0B-20260828",
        "stage": "RECENT_FLAGSHIP_CARRIER_AUTHOR_SCHEDULER_ZERO_PROVIDER_P0B",
        "date": "2026-08-28",
        "carrier": {
            "name": "Skill-Pro",
            "venue": "ICML 2026 Spotlight",
            "official_repository": "https://github.com/Miracle1207/Skill-Pro",
            "commit": SKILLPRO_COMMIT,
            "archive_sha256": SKILLPRO_ARCHIVE_SHA256,
            "source_sha256": actual_hashes,
        },
        "execution_contract": {
            "author_method_executed_unchanged": "Skills.skill_evolution.SkillEvolution.run_skill_evolution_with_verification",
            "subclass_overrides": ["evolve", "_compute_skill_logprobs"],
            "override_location": "post-readiness only: both hooks are reached after the author's Experience.skill distribution and len(buffered_exps) >= threshold branch",
            "model_calls": 0,
            "provider_calls": 0,
            "gpu_visible": False,
            "candidate_generation_semantics": "stub only; no candidate-quality or PPO claim is authorized",
        },
        "arms": {
            "canonical": canonical,
            "id_placebo": placebo,
            "exact_split_3_plus_3": exact_split,
            "pre_gate_quotient": pre_gate_quotient,
            "late_identity_only_dedup": late_dedup,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "qualified_conclusion": "The unchanged pinned author scheduler itself distinguishes 6 from exact 3+3 identity attribution before any model-dependent candidate-generation hook is reached. Pre-gate semantic reunion restores scheduler reachability; identity-only reunion after the first local gate does not.",
        "scientific_boundary": {
            "claim_expansion": False,
            "candidate_quality_claim": False,
            "ppo_gate_claim": False,
            "downstream_behavior_claim": False,
            "natural_prevalence_claim": False,
            "cross_system_generality_claim": False,
            "new_model_calls": 0,
            "new_gpu_runs": 0,
            "p1_authority": False,
            "p2_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result(args.source_root)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if result["all_checks_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
