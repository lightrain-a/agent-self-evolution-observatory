from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated/asset-first-stri-r2-second-system-credit-partition-20260825.json"
EXPECTED_RETHINK_COMMIT = "4138419afc00a1fa3ff0885c0bb1618e18258354"
EXPECTED_SKILLSVOTE_COMMIT = "55ea783d1818457e21ed12138309d8da7e58ceb8"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(repo: Path) -> str:
    import subprocess
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _semantic_subtask_payload(index: int) -> dict[str, Any]:
    return {
        "goal": f"Reusable procedure evidence item {index}",
        "summary": "The procedure succeeded and revealed the same reusable improvement pattern.",
        "exploration": "Apply the reusable improvement pattern before the fragile fallback.",
        "exploration_reason": "The successful trace exposes a reusable procedure improvement.",
        "judge": "environment",
        "judge_reason": "The environment verifies successful completion.",
        "attribution": "success_skill_used_with_extra_exploration",
        "attribution_reason": "The linked skill contributed and the trace added reusable exploration.",
        "skill_refs": [],
        "ground_truth_path": None,
    }


def build(rethink_repo: Path, skillsvote_repo: Path) -> dict[str, Any]:
    if git_head(rethink_repo) != EXPECTED_RETHINK_COMMIT:
        raise RuntimeError("RethinkSkill commit drift")
    if git_head(skillsvote_repo) != EXPECTED_SKILLSVOTE_COMMIT:
        raise RuntimeError("SkillsVote commit drift")

    rethink_loop = rethink_repo / "src/rethinkskill/evolution/loop.py"
    rethink_protocol = rethink_repo / "src/rethinkskill/evolution/protocol.py"
    sv_model = skillsvote_repo / "src/skills_vote/evolve/model.py"
    sv_codex = skillsvote_repo / "src/skills_vote/evolve/codex.py"
    sv_prompt = skillsvote_repo / "src/skills_vote/evolve/prompt.py"
    for path in (rethink_loop, rethink_protocol, sv_model, sv_codex, sv_prompt):
        if not path.is_file():
            raise RuntimeError(f"missing first-party source: {path}")

    rethink_loop_text = rethink_loop.read_text(encoding="utf-8")
    rethink_protocol_text = rethink_protocol.read_text(encoding="utf-8")
    rethink_checks = {
        "single_current_skill_state": "current_skill: str" in rethink_loop_text,
        "single_best_skill_state": "best_skill: str" in rethink_loop_text,
        "candidate_is_one_complete_skill": "candidate_skill: str" in rethink_loop_text,
        "validation_gate_is_round_candidate_level": "def gate_decision(" in rethink_protocol_text and "candidate" not in rethink_protocol_text[:1],
        "no_parallel_skill_identity_bucket_map_in_evolution_state": "dict[str, Skill" not in rethink_loop_text and "dict[str, str]" not in rethink_loop_text,
    }
    # The gate itself is real, but the released primary evolution state is one current skill artifact,
    # not a library of exchangeable exact-semantic identities. This makes it a closest-work control,
    # not a valid second identity-partition realization.
    rethink_qualifies = False

    sys.path.insert(0, str(skillsvote_repo / "src"))
    try:
        from skills_vote.feedback.model import FeedbackPayload, Subtask
        from skills_vote.evolve.model import feedback_to_evolve_requests
    finally:
        pass

    semantic_rows = [_semantic_subtask_payload(i) for i in range(1, 9)]
    semantic_sha = hashlib.sha256(canonical(semantic_rows).encode("utf-8")).hexdigest()

    def payload(links: list[str]) -> FeedbackPayload:
        rows = []
        for base, linked in zip(semantic_rows, links, strict=True):
            rows.append(Subtask(**base, skill_linked=linked))
        return FeedbackPayload(subtasks=rows)

    canonical_payload = payload(["focal"] * 8)
    split_payload = payload(["focal_a"] * 4 + ["focal_b"] * 4)
    quotient_payload = payload(["focal"] * 8)

    canonical_requests = feedback_to_evolve_requests(canonical_payload)
    split_requests = feedback_to_evolve_requests(split_payload)
    quotient_requests = feedback_to_evolve_requests(quotient_payload)

    def req_summary(requests: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "target_skill_name": r.target_skill_name,
                "subtask_count": len(r.subtasks),
                "request_dir_name": r.request_dir_name,
            }
            for r in requests
        ]

    def semantics_without_link(payload_obj: FeedbackPayload) -> str:
        rows = []
        for subtask in payload_obj.subtasks:
            row = subtask.model_dump()
            row.pop("skill_linked", None)
            rows.append(row)
        return hashlib.sha256(canonical(rows).encode("utf-8")).hexdigest()

    semantic_hashes = {
        "canonical": semantics_without_link(canonical_payload),
        "split": semantics_without_link(split_payload),
        "quotient": semantics_without_link(quotient_payload),
    }
    if len(set(semantic_hashes.values())) != 1:
        raise RuntimeError("semantic evidence changed across SkillsVote counterfactual arms")

    sv_model_text = sv_model.read_text(encoding="utf-8")
    sv_codex_text = sv_codex.read_text(encoding="utf-8")
    sv_prompt_text = sv_prompt.read_text(encoding="utf-8")
    structural_checks = {
        "feedback_grouped_by_skill_linked_identity": "edit_subtasks.setdefault(subtask.skill_linked, []).append(subtask)" in sv_model_text,
        "one_edit_request_per_identity_bucket": "for skill_name, subtasks in edit_subtasks.items():" in sv_model_text,
        "one_updater_invocation_per_request": "for request in requests:" in sv_codex_text and "evolve_output = await run_evolve_once(" in sv_codex_text,
        "request_targets_persistent_working_skill_identity": "working_skills_dir / target_skill_name" in sv_codex_text,
        "successful_edit_copied_back_to_persistent_library": "shutil.copytree(edit_dir, working_skill_dir, dirs_exist_ok=True)" in sv_codex_text,
        "within_request_evidence_consolidation_expected": "When multiple subtasks support the same improvement, produce one consolidated edit" in sv_prompt_text,
    }
    if not all(structural_checks.values()):
        raise RuntimeError("SkillsVote structural credit-partition qualification failed")

    csum = req_summary(canonical_requests)
    ssum = req_summary(split_requests)
    qsum = req_summary(quotient_requests)
    counterfactual_pass = (
        len(csum) == 1 and csum[0]["subtask_count"] == 8
        and len(ssum) == 2 and sorted(r["subtask_count"] for r in ssum) == [4, 4]
        and len(qsum) == 1 and qsum[0]["subtask_count"] == 8
    )
    if not counterfactual_pass:
        raise RuntimeError("SkillsVote request-topology counterfactual did not match frozen prediction")

    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "object_id": "STRI-R2-SECOND-SYSTEM-CREDIT-PARTITION",
        "stage": "MECHANISM_REDESIGN_SECOND_SYSTEM_QUALIFICATION",
        "decision": "QUALIFY_SKILLSVOTE_REQUEST_PARTITION_ANALOGUE_ONLY",
        "second_exact_phase_law_replication": False,
        "second_structural_partition_before_update_analogue": True,
        "rethinkskill": {
            "repo": "https://github.com/HKUST-KnowComp/rethinkskill",
            "commit": EXPECTED_RETHINK_COMMIT,
            "source_sha256": {
                "src/rethinkskill/evolution/loop.py": sha(rethink_loop),
                "src/rethinkskill/evolution/protocol.py": sha(rethink_protocol),
            },
            "checks": rethink_checks,
            "qualifies_as_identity_partition_realization": rethink_qualifies,
            "disposition": "CLOSEST_WORK_CONTROL_NOT_PARALLEL_IDENTITY_BUCKET_REALIZATION",
            "reason": "The released primary loop evolves one current skill artifact against candidate validation, rather than maintaining a parallel library of exact-semantic identities with identity-local evidence buckets. It is therefore a strong feedback-dynamics neighbor but not a same-object replication substrate.",
        },
        "skillsvote": {
            "repo": "https://github.com/MemTensor/skills-vote",
            "commit": EXPECTED_SKILLSVOTE_COMMIT,
            "source_sha256": {
                "src/skills_vote/evolve/model.py": sha(sv_model),
                "src/skills_vote/evolve/codex.py": sha(sv_codex),
                "src/skills_vote/evolve/prompt.py": sha(sv_prompt),
            },
            "semantic_feedback_records": 8,
            "semantic_feedback_sha256": semantic_sha,
            "semantic_payload_hashes_without_skill_link": semantic_hashes,
            "structural_checks": structural_checks,
            "arms": {
                "A_canonical_identity": {"links": {"focal": 8}, "requests": csum},
                "B_split2_identity": {"links": {"focal_a": 4, "focal_b": 4}, "requests": ssum},
                "C_semantic_quotient_link": {"links": {"focal": 8}, "requests": qsum},
            },
            "headline": {
                "canonical_edit_requests": len(csum),
                "split_edit_requests": len(ssum),
                "quotient_edit_requests": len(qsum),
                "canonical_evidence_per_request": [r["subtask_count"] for r in csum],
                "split_evidence_per_request": sorted(r["subtask_count"] for r in ssum),
                "quotient_evidence_per_request": [r["subtask_count"] for r in qsum],
            },
            "counterfactual_pass": counterfactual_pass,
            "mechanism_interpretation": "SkillsVote deterministically partitions evolvable feedback by skill_linked identity before invoking its updater. Exact identity refinement changes one eight-record edit context into two four-record edit contexts even when all non-identity semantic evidence is unchanged; semantic quotienting the links restores one eight-record request. Because the downstream editor is model-based rather than a released deterministic threshold gate, this establishes request-topology fragmentation before persistent update, not a second exact lifecycle phase-law replication.",
        },
        "cross_system_synthesis": {
            "shared_structure": "semantic evidence -> identity-keyed partition -> update/lifecycle stage -> persistent skill state",
            "skillsp_strength": "deterministic per-ID sufficient statistics plus nonlinear pruning gate, exact M<=N<kM phase law, lifecycle divergence",
            "skillsvote_strength": "independent first-party identity-keyed feedback partition before one updater invocation per identity bucket, with persistent working-skill targets",
            "what_is_not_shared": "SkillsVote does not expose the same deterministic M-threshold lifecycle gate; RethinkSkill does not expose parallel identity buckets in its primary loop.",
        },
        "claim_boundary": "Cross-system structural corroboration of partition-before-update only. It does not establish that SkillsVote clone splitting changes edited skill contents, task utility, or a second exact fragmentation phase law; no updater model call is executed.",
        "next_gate": "Use this as cross-system mechanism-structure evidence in R2 story synthesis. Do not run SkillsVote updater calls unless a separate preregistered counterfactual can define a deterministic downstream endpoint and justify the cost.",
        "new_model_calls": 0,
        "new_agent_runs": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    canon = canonical(result).encode("utf-8")
    result["result_canonical_sha256"] = hashlib.sha256(canon).hexdigest()
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rethink-repo", type=Path, required=True)
    ap.add_argument("--skillsvote-repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()
    result = build(args.rethink_repo, args.skillsvote_repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
