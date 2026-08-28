from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

EXPECTED_P1A_AGGREGATE = "a1c0070075d1d27a5cc5b7ea3bb3af4e51d6c077f38f132643565c720f4af2a5"
FOCAL = "HypothesisElimination"
ALIAS_A = "HypothesisElimination_A"
ALIAS_B = "HypothesisElimination_B"
RENAMED = "HypothesisElimination_Renamed"
ALLOWED_ARMS = {"A_canonical", "B_id_placebo", "C_exact_split", "D_pre_gate_quotient", "E_late_identity_dedup"}
MODEL_ARMS = {"A_canonical", "B_id_placebo", "D_pre_gate_quotient"}
BASELINE = 2.5 / 6.0


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


def semantic_fields(exp_dict: dict[str, Any]) -> dict[str, Any]:
    return {
        "reward": exp_dict["reward"],
        "trajectory": exp_dict["trajectory"],
        "env_name": exp_dict["env_name"],
        "transitions": exp_dict["transitions"],
        "step_count": exp_dict["step_count"],
        "total_added_tokens": exp_dict["total_added_tokens"],
    }


def load_frozen_evidence(evidence_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    final = json.loads((evidence_dir / "manifest.final.json").read_text(encoding="utf-8"))
    if final.get("decision") != "P1A_SIX_REAL_EXPERIENCES_FROZEN":
        raise RuntimeError(f"P1a final manifest is not qualified: {final.get('decision')}")
    if final.get("aggregate_semantic_evidence_sha256") != EXPECTED_P1A_AGGREGATE:
        raise RuntimeError("P1a aggregate semantic hash drift")
    rows, hashes = [], []
    for idx in range(1, 7):
        row = json.loads((evidence_dir / f"episode-{idx:02d}.json").read_text(encoding="utf-8"))
        if not row.get("runtime_valid"):
            raise RuntimeError(f"P1a episode {idx} is not runtime-valid")
        recomputed = sha256_json(semantic_fields(row["experience"]))
        if recomputed != row["semantic_evidence_sha256"]:
            raise RuntimeError(f"P1a episode {idx} semantic hash mismatch")
        rows.append(row)
        hashes.append(recomputed)
    if sha256_json(hashes) != EXPECTED_P1A_AGGREGATE:
        raise RuntimeError("P1a aggregate semantic hash recomputation mismatch")
    return rows, final


def make_seed_pool(SkillPool):
    pool = SkillPool.__new__(SkillPool)
    pool.max_size = 10
    pool.skills = []
    pool._skill_embs = {}
    pool._update_emb_cache = lambda _skill: None
    SkillPool._initialize_seeds(pool)
    return pool


def find_skill(pool, name: str):
    for skill in pool.skills:
        if skill.name == name:
            return skill
    raise KeyError(name)


def replace_focal(pool, names: list[str]):
    focal = find_skill(pool, FOCAL)
    idx = pool.skills.index(focal)
    clones = []
    for name in names:
        clone = copy.deepcopy(focal)
        clone.name = name
        clone.frequency = 0
        clone.avg_gain = 0.0
        clone.total_gain = 0.0
        clone.success_count = 0
        clone.maturity = 0
        clone.last_evolved_iter = 0
        clone.parent_id = ""
        clone.version = 0
        clones.append(clone)
    pool.skills[idx:idx + 1] = clones
    return clones


def reconstruct_stats(skill, rows: list[dict[str, Any]], episode_indices: Iterable[int]) -> None:
    selected = [rows[i - 1] for i in episode_indices]
    frequency = sum(len(row["usage_history"]) for row in selected)
    total_gain = sum(float(row["reward"]) for row in selected)
    skill.frequency = frequency
    skill.total_gain = total_gain
    skill.avg_gain = total_gain / max(frequency, 1)
    skill.success_count = sum(float(row["reward"]) > 0 for row in selected)
    skill.maturity = 1
    skill.last_evolved_iter = 0


def prepare_pool_and_assignments(pool, rows: list[dict[str, Any]], arm: str):
    for skill in pool.skills:
        skill.maturity = 1

    if arm in {"A_canonical", "D_pre_gate_quotient"}:
        focal = find_skill(pool, FOCAL)
        reconstruct_stats(focal, rows, range(1, 7))
        assignments = [FOCAL] * 6
        representation = {
            "runtime_identities": [FOCAL],
            "pre_intervention_counts": [6] if arm == "A_canonical" else [3, 3],
            "post_intervention_counts": [6],
        }
    elif arm == "B_id_placebo":
        (renamed,) = replace_focal(pool, [RENAMED])
        reconstruct_stats(renamed, rows, range(1, 7))
        assignments = [RENAMED] * 6
        representation = {"runtime_identities": [RENAMED], "post_intervention_counts": [6]}
    elif arm in {"C_exact_split", "E_late_identity_dedup"}:
        a, b = replace_focal(pool, [ALIAS_A, ALIAS_B])
        reconstruct_stats(a, rows, [1, 2, 3])
        reconstruct_stats(b, rows, [4, 5, 6])
        assignments = [ALIAS_A] * 3 + [ALIAS_B] * 3
        representation = {"runtime_identities": [ALIAS_A, ALIAS_B], "post_intervention_counts": [3, 3]}
    else:
        raise ValueError(arm)
    return assignments, representation


def pool_snapshot(pool) -> list[dict[str, Any]]:
    out = []
    for s in pool.get_all():
        out.append({
            "name": s.name,
            "initiation": s.initiation,
            "policy": list(s.policy),
            "termination": s.termination,
            "frequency": int(s.frequency),
            "avg_gain": float(s.avg_gain),
            "total_gain": float(s.total_gain),
            "maturity": int(s.maturity),
            "success_count": int(s.success_count),
            "last_evolved_iter": int(s.last_evolved_iter),
            "parent_id": s.parent_id,
            "version": int(s.version),
        })
    return out


class NoCallLLM:
    use_vllm = False

    def __call__(self, _prompt: str) -> str:
        raise RuntimeError("MODEL_CALL_FORBIDDEN_IN_ZERO_CALL_ARM")

    def compute_logprob_batch(self, *_args, **_kwargs):
        raise RuntimeError("LOGPROB_CALL_FORBIDDEN_IN_ZERO_CALL_ARM")


class LoggingLLM:
    def __init__(self, inner, out_dir: Path):
        self.inner = inner
        self.out_dir = out_dir
        self.model_call_count = 0
        self.logprob_call_count = 0

    def __getattr__(self, name: str):
        return getattr(self.inner, name)

    def __call__(self, prompt: str) -> str:
        self.model_call_count += 1
        idx = self.model_call_count
        response = self.inner(prompt)
        write_new_json(self.out_dir / f"model-call-{idx:03d}.json", {
            "call_index": idx,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt": prompt,
            "raw_output": response,
            "raw_output_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
        })
        return response

    def compute_logprob_batch(self, prompts, targets, *args, **kwargs):
        # Runtime-only adaptation frozen after the pre-candidate 80-item OOM:
        # preserve every prompt/target and concatenate released per-example
        # logprobs in the original order, while limiting physical vLLM batches.
        import torch

        self.logprob_call_count += 1
        idx = self.logprob_call_count
        microbatch_size = 1
        chunks = []
        for start in range(0, len(prompts), microbatch_size):
            end = min(start + microbatch_size, len(prompts))
            chunks.append(
                self.inner.compute_logprob_batch(
                    prompts[start:end], targets[start:end], *args, **kwargs
                )
            )
        result = torch.cat(chunks, dim=0) if chunks else torch.empty(0, dtype=torch.float32)
        write_new_json(self.out_dir / f"logprob-call-{idx:03d}.json", {
            "call_index": idx,
            "logical_batch_size": len(prompts),
            "physical_microbatch_size": microbatch_size,
            "physical_microbatch_count": len(chunks),
            "prompt_sha256": [hashlib.sha256(p.encode("utf-8")).hexdigest() for p in prompts],
            "target_sha256": [hashlib.sha256(t.encode("utf-8")).hexdigest() for t in targets],
            "logprobs": [float(x) for x in result.detach().cpu().tolist()],
        })
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--arm", required=True, choices=sorted(ALLOWED_ARMS))
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    arm = args.arm
    if arm in {"A_canonical", "D_pre_gate_quotient"} and args.seed not in {42, 43, 44}:
        raise SystemExit("Frozen paired A/D seeds are 42,43,44")
    if arm == "B_id_placebo" and args.seed != 42:
        raise SystemExit("Frozen B seed is 42")
    if arm in {"C_exact_split", "E_late_identity_dedup"} and args.seed != 42:
        raise SystemExit("Frozen zero-call control seed is 42")

    source = Path(args.source).resolve()
    evidence_dir = Path(args.evidence_dir).resolve()
    out = Path(args.output_dir).resolve()
    if out.exists():
        raise SystemExit(f"Refuse overwrite existing P1b run directory: {out}")
    out.mkdir(parents=True, exist_ok=False)

    try:
        rows, _p1a_final = load_frozen_evidence(evidence_dir)
        sys.path.insert(0, str(source))
        from data_structures import Experience
        from run import SkillMDP
        from Skills.skill_evolution import SkillEvolution
        from Skills.skill_pool import SkillPool
        from utils.utils import set_seed

        set_seed(args.seed)
        random.seed(args.seed)
        pool = make_seed_pool(SkillPool)
        assignments, representation = prepare_pool_and_assignments(pool, rows, arm)

        experiences = []
        per_episode_semantic_hashes = []
        for row, identity in zip(rows, assignments):
            payload = copy.deepcopy(row["experience"])
            if sha256_json(semantic_fields(payload)) != row["semantic_evidence_sha256"]:
                raise RuntimeError("semantic evidence changed before identity attribution")
            payload["skill"] = identity
            experiences.append(Experience(**payload))
            per_episode_semantic_hashes.append(sha256_json(semantic_fields(payload)))
        if sha256_json(per_episode_semantic_hashes) != EXPECTED_P1A_AGGREGATE:
            raise RuntimeError("identity attribution changed frozen semantic evidence")

        before_pool = pool_snapshot(pool)
        before_pool_hash = sha256_json(before_pool)
        manifest_pre = {
            "schema_version": "1.0",
            "paper_id": "STRI",
            "stage": "SKILLPRO_P1B_REAL_EVOLUTION",
            "arm": arm,
            "seed": args.seed,
            "source": str(source),
            "model": str(Path(args.model).resolve()),
            "evidence_dir": str(evidence_dir),
            "p1a_aggregate_semantic_evidence_sha256": EXPECTED_P1A_AGGREGATE,
            "identity_assignments": assignments,
            "representation": representation,
            "author_parameters": {
                "threshold": 6,
                "best_of_n": 3,
                "acceptance_margin": 0.0,
                "epsilon": 0.2,
                "current_iteration": 1,
                "baseline": {"Mastermind-v0": BASELINE},
                "ablation_type": "none",
                "vllm_gpu_utilization": 0.55,
                "logprob_microbatch_size": 1
            },
            "pool_before_sha256": before_pool_hash,
            "pool_before": before_pool
        }
        write_new_json(out / "manifest.pre.json", manifest_pre)

        if arm in MODEL_ARMS:
            from utils.local_llm import LocalLLM
            raw_llm = LocalLLM(
                model_path=str(Path(args.model).resolve()),
                use_vllm=True,
                vllm_gpu_util=0.55,
            )
            llm = LoggingLLM(raw_llm, out)
        else:
            llm = NoCallLLM()

        evolver = SkillEvolution(llm_agent=llm, threshold=6, epsilon=0.2)
        mdp_stub = SkillMDP.__new__(SkillMDP)
        mdp_stub.args = SimpleNamespace(MDP_type="SMDP")

        def build_prompt_fn(state, skill_text, env_name):
            return SkillMDP.build_decision_prompt(
                mdp_stub, state, skill_text, env_name, admissible_commands=None
            )

        first_logs = evolver.run_skill_evolution_with_verification(
            skill_pool=pool,
            new_experiences=experiences,
            build_prompt_fn=build_prompt_fn,
            baselines={"Mastermind-v0": BASELINE},
            acceptance_margin=0.0,
            max_evolutions_per_step=2,
            best_of_n=3,
            current_iteration=1,
            ablation_type="none",
        )
        buffer_after_first = {k: len(v) for k, v in sorted(evolver.experience_buffer.items())}

        late_dedup = None
        second_logs = None
        if arm == "E_late_identity_dedup":
            before_names = [s.name for s in pool.get_all()]
            victim = find_skill(pool, ALIAS_B)
            pool.skills.remove(victim)
            after_names = [s.name for s in pool.get_all()]
            buffer_before_second = {k: len(v) for k, v in sorted(evolver.experience_buffer.items())}
            second_logs = evolver.run_skill_evolution_with_verification(
                skill_pool=pool,
                new_experiences=[],
                build_prompt_fn=build_prompt_fn,
                baselines={"Mastermind-v0": BASELINE},
                acceptance_margin=0.0,
                max_evolutions_per_step=2,
                best_of_n=3,
                current_iteration=1,
                ablation_type="none",
            )
            late_dedup = {
                "pool_names_before_identity_only_dedup": before_names,
                "pool_names_after_identity_only_dedup": after_names,
                "buffer_counts_before_second_gate": buffer_before_second,
                "buffer_counts_after_second_gate": {k: len(v) for k, v in sorted(evolver.experience_buffer.items())},
                "second_scheduler_logs": second_logs,
            }

        after_pool = pool_snapshot(pool)
        final = {
            **manifest_pre,
            "first_scheduler_logs": first_logs,
            "first_scheduler_log_count": len(first_logs),
            "buffer_counts_after_first_scheduler": buffer_after_first,
            "late_dedup": late_dedup,
            "pool_after": after_pool,
            "pool_after_sha256": sha256_json(after_pool),
            "pool_changed": sha256_json(after_pool) != before_pool_hash,
            "model_call_count": int(getattr(llm, "model_call_count", 0)),
            "logprob_call_count": int(getattr(llm, "logprob_call_count", 0)),
            "semantic_evidence_preserved": True,
        }
        if arm == "C_exact_split":
            final["decision"] = "P1B_SPLIT_RETURNED_BEFORE_MODEL_PATH" if not first_logs else "P1B_SPLIT_UNEXPECTEDLY_EVOLVED"
        elif arm == "E_late_identity_dedup":
            final["decision"] = "P1B_LATE_DEDUP_DID_NOT_RESTORE_MISSED_EVOLUTION" if not first_logs and not second_logs else "P1B_LATE_DEDUP_UNEXPECTED_EVOLUTION"
        else:
            final["decision"] = "P1B_MODEL_PATH_COMPLETED"
        write_new_json(out / "manifest.final.json", final)
        return 0
    except Exception as exc:
        failure = {
            "schema_version": "1.0",
            "paper_id": "STRI",
            "stage": "SKILLPRO_P1B_REAL_EVOLUTION_FAILURE",
            "arm": arm,
            "seed": args.seed,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        try:
            write_new_json(out / "failure.json", failure)
        except FileExistsError:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
