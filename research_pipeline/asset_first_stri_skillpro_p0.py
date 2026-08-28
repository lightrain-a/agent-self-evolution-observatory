from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_THRESHOLD = 6
SKILLPRO_COMMIT = "3be7a9be2d4c024d132efe394d537404eba7e4c8"
SKILLPRO_ARCHIVE_SHA256 = "33c4ba593595cca2bceec28e2c3c1426a158ffe29987f139c6bcc55d4e158bd6"
EXPECTED_SOURCE_SHA256 = {
    "Skills/skill_evolution.py": "134916242f5e7d04c2028478d1f2b46fcd3847905f008ee28a35cedd2e6cc73a",
    "Skills/skill_pool.py": "243e4108a040dd56cdba7999b64673d670571f015e26afc953325677ed6de461",
    "run.py": "90f418d6d2934d4743cac6a73c7f92abcfd6ff8b3502b505f598469ceaac7182",
    "data_structures.py": "c010655a8ea3ec4e56ce114e2cf92c91810426b4eac960ecf28a00564b922b10",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def frozen_semantic_evidence(count: int = DEFAULT_THRESHOLD) -> list[dict[str, Any]]:
    """Create deterministic evidence rows whose semantic content is independent of identity attribution."""
    if count <= 0:
        raise ValueError("count must be positive")
    return [
        {
            "evidence_id": f"e{i:02d}",
            "reward": 1.0,
            "trajectory": f"frozen-semantic-trajectory-{i:02d}",
            "env_name": "stri-skillpro-p0",
            "transitions": [
                {
                    "state": f"state-{i:02d}",
                    "action": f"action-{i:02d}",
                }
            ],
        }
        for i in range(count)
    ]


def semantic_evidence_hash(rows: Sequence[dict[str, Any]]) -> str:
    """Hash only evidence semantics; identity attribution is deliberately excluded."""
    projected = [
        {
            key: value
            for key, value in row.items()
            if key not in {"skill", "skill_name", "identity", "identity_bucket"}
        }
        for row in rows
    ]
    return canonical_json_sha256(projected)


def assign_identities(
    evidence: Sequence[dict[str, Any]],
    identities: Sequence[str],
) -> list[dict[str, Any]]:
    if len(evidence) != len(identities):
        raise ValueError("one identity attribution is required for every evidence row")
    out: list[dict[str, Any]] = []
    for row, identity in zip(evidence, identities, strict=True):
        item = dict(row)
        item["skill"] = str(identity)
        out.append(item)
    return out


def distribute_identity_buckets(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    """Project the released Skill-Pro distribution seam: split Experience.skill on ';' and append per name."""
    buckets: dict[str, int] = defaultdict(int)
    for row in rows:
        raw = str(row.get("skill") or "")
        if not raw or raw == "None":
            continue
        for skill_name in raw.split(";"):
            buckets[skill_name] += 1
    return dict(buckets)


def ready_identities(
    rows: Iterable[dict[str, Any]],
    active_identities: Sequence[str],
    *,
    threshold: int = DEFAULT_THRESHOLD,
) -> list[str]:
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    buckets = distribute_identity_buckets(rows)
    return [identity for identity in active_identities if buckets.get(identity, 0) >= threshold]


def semantic_quotient_ready(
    rows: Iterable[dict[str, Any]],
    semantic_members: Sequence[str],
    *,
    threshold: int = DEFAULT_THRESHOLD,
) -> bool:
    members = set(semantic_members)
    buckets = distribute_identity_buckets(rows)
    semantic_count = sum(count for identity, count in buckets.items() if identity in members)
    return semantic_count >= threshold


def readiness_coordinates(counts: Sequence[int], *, threshold: int = DEFAULT_THRESHOLD) -> dict[str, Any]:
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if not counts or any(int(value) < 0 for value in counts):
        raise ValueError("counts must be a nonempty sequence of nonnegative integers")
    normalized = [int(value) for value in counts]
    total = sum(normalized)
    peak = max(normalized)
    quotient_ready = total >= threshold
    native_ready = peak >= threshold
    if not quotient_ready:
        regime = "under_evidenced"
    elif not native_ready:
        regime = "evolution_fragmented"
    else:
        regime = "resolved"
    return {
        "counts": normalized,
        "N": total,
        "M": threshold,
        "q": total / threshold,
        "p": peak / threshold,
        "quotient_ready": quotient_ready,
        "native_any_identity_ready": native_ready,
        "regime": regime,
    }


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if total < 0 or parts <= 0:
        raise ValueError("total must be nonnegative and parts must be positive")
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            yield (first,) + tail


def partition_geometry(*, threshold: int = DEFAULT_THRESHOLD, max_parts: int = 4, max_total: int = 24) -> dict[str, Any]:
    cells = []
    total_compositions = 0
    fragmented_compositions = 0
    for k in range(1, max_parts + 1):
        for total in range(max_total + 1):
            compositions = list(weak_compositions(total, k))
            fragmented = [
                counts for counts in compositions
                if readiness_coordinates(counts, threshold=threshold)["regime"] == "evolution_fragmented"
            ]
            total_compositions += len(compositions)
            fragmented_compositions += len(fragmented)
            cells.append(
                {
                    "k": k,
                    "N": total,
                    "ordered_weak_compositions": len(compositions),
                    "evolution_fragmented": len(fragmented),
                }
            )
    return {
        "threshold": threshold,
        "max_parts": max_parts,
        "max_total": max_total,
        "cells": cells,
        "ordered_weak_compositions": total_compositions,
        "evolution_fragmented": fragmented_compositions,
    }


def frozen_arms(*, threshold: int = DEFAULT_THRESHOLD) -> dict[str, Any]:
    evidence = frozen_semantic_evidence(threshold)
    evidence_hash = semantic_evidence_hash(evidence)

    canonical = assign_identities(evidence, ["skill_c"] * threshold)
    placebo = assign_identities(evidence, ["skill_c_renamed"] * threshold)

    left = threshold // 2
    right = threshold - left
    split = assign_identities(evidence, ["skill_c_a"] * left + ["skill_c_b"] * right)

    quotient = assign_identities(evidence, ["skill_c_a"] * threshold)
    zero_evidence: list[dict[str, Any]] = []

    arms = {
        "canonical": {
            "active_identities": ["skill_c"],
            "rows": canonical,
            "ready_identities": ready_identities(canonical, ["skill_c"], threshold=threshold),
            "semantic_ready": semantic_quotient_ready(canonical, ["skill_c"], threshold=threshold),
            "coordinates": readiness_coordinates([threshold], threshold=threshold),
        },
        "id_placebo": {
            "active_identities": ["skill_c_renamed"],
            "rows": placebo,
            "ready_identities": ready_identities(placebo, ["skill_c_renamed"], threshold=threshold),
            "semantic_ready": semantic_quotient_ready(placebo, ["skill_c_renamed"], threshold=threshold),
            "coordinates": readiness_coordinates([threshold], threshold=threshold),
        },
        "exact_split": {
            "active_identities": ["skill_c_a", "skill_c_b"],
            "rows": split,
            "ready_identities": ready_identities(split, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "semantic_ready": semantic_quotient_ready(split, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "coordinates": readiness_coordinates([left, right], threshold=threshold),
        },
        "pre_gate_quotient": {
            "active_identities": ["skill_c_a", "skill_c_b"],
            "rows": quotient,
            "ready_identities": ready_identities(quotient, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "semantic_ready": semantic_quotient_ready(quotient, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "coordinates": readiness_coordinates([threshold, 0], threshold=threshold),
            "control_semantics": "design control: semantic evidence is reunited before the released identity-local threshold",
        },
        "late_dedup": {
            "active_identities_before_dedup": ["skill_c_a", "skill_c_b"],
            "active_identities_after_dedup": ["skill_c_a"],
            "rows": split,
            "ready_before_dedup": ready_identities(split, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "ready_after_identity_only_dedup": ready_identities(split, ["skill_c_a"], threshold=threshold),
            "semantic_ready": semantic_quotient_ready(split, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "coordinates": readiness_coordinates([left, right], threshold=threshold),
            "control_semantics": "negative control: delete an alias after the local gate without merging its evidence buffer",
        },
        "zero_evidence": {
            "active_identities": ["skill_c_a", "skill_c_b"],
            "rows": zero_evidence,
            "ready_identities": ready_identities(zero_evidence, ["skill_c_a", "skill_c_b"], threshold=threshold),
            "semantic_ready": False,
            "coordinates": readiness_coordinates([0, 0], threshold=threshold),
        },
    }

    for name in ("canonical", "id_placebo", "exact_split", "pre_gate_quotient"):
        arms[name]["semantic_evidence_sha256"] = semantic_evidence_hash(arms[name]["rows"])
    arms["late_dedup"]["semantic_evidence_sha256"] = semantic_evidence_hash(arms["late_dedup"]["rows"])
    arms["zero_evidence"]["semantic_evidence_sha256"] = semantic_evidence_hash(zero_evidence)

    return {
        "threshold": threshold,
        "frozen_semantic_evidence_sha256": evidence_hash,
        "arms": arms,
    }


def source_contract_audit(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    files = {relative: source_root / relative for relative in EXPECTED_SOURCE_SHA256}
    missing = [relative for relative, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing Skill-Pro source files: {missing}")

    actual_hashes = {relative: sha256(path) for relative, path in files.items()}
    evolution = files["Skills/skill_evolution.py"].read_text(encoding="utf-8")
    pool = files["Skills/skill_pool.py"].read_text(encoding="utf-8")
    run = files["run.py"].read_text(encoding="utf-8")
    structures = files["data_structures.py"].read_text(encoding="utf-8")

    anchors = {
        "threshold_default_6": bool(re.search(r"threshold:\s*int\s*=\s*6", evolution)),
        "buffer_keyed_by_skill_name_comment": "按 Skill Name 存储积累的经验轨迹" in evolution,
        "experience_skill_split": 'skill_names = exp.skill.split(";")' in evolution,
        "identity_local_append": "self.experience_buffer[sk_name].append(exp)" in evolution,
        "identity_local_readout": "self.experience_buffer.get(sk.name, [])" in evolution,
        "identity_local_threshold": "if len(buffered_exps) >= self.threshold:" in evolution,
        "evolution_before_maintenance": run.find("run_skill_evolution_with_verification") < run.find("maintain()"),
        "semantic_dedup_threshold_095": bool(re.search(r"thr\s*=\s*0\.95", pool)),
        "skill_name_is_explicit_field": bool(re.search(r"class Skill:.*?\n\s+name:\s*str", structures, flags=re.S)),
        "experience_identity_field": bool(re.search(r"class Experience:.*?\n\s+skill:\s*str", structures, flags=re.S)),
    }

    return {
        "source_root": str(source_root),
        "commit": SKILLPRO_COMMIT,
        "archive_sha256": SKILLPRO_ARCHIVE_SHA256,
        "source_sha256": actual_hashes,
        "source_sha256_match_frozen_pin": actual_hashes == EXPECTED_SOURCE_SHA256,
        "anchors": anchors,
        "all_required_anchors_present": all(anchors.values()),
        "qualified_source_seams": {
            "threshold": "Skills/skill_evolution.py:127-137",
            "distribution_and_readiness": "Skills/skill_evolution.py:386-405",
            "evolution_before_maintenance": "run.py:132-148",
            "semantic_dedup": "Skills/skill_pool.py:372-380,533-539",
            "identity_schema": "data_structures.py:12-27,97-106",
        },
    }


def build_result(source_root: Path | None = None) -> dict[str, Any]:
    arm_result = frozen_arms()
    source_audit = source_contract_audit(source_root) if source_root else None
    exact_split = arm_result["arms"]["exact_split"]
    canonical = arm_result["arms"]["canonical"]
    quotient = arm_result["arms"]["pre_gate_quotient"]
    late = arm_result["arms"]["late_dedup"]

    checks = {
        "canonical_reaches_identity_local_gate": bool(canonical["ready_identities"]),
        "id_placebo_reaches_identity_local_gate": bool(arm_result["arms"]["id_placebo"]["ready_identities"]),
        "exact_split_semantically_ready": bool(exact_split["semantic_ready"]),
        "exact_split_has_no_ready_identity": not bool(exact_split["ready_identities"]),
        "pre_gate_quotient_restores_readiness": bool(quotient["ready_identities"]),
        "late_identity_only_dedup_does_not_restore_readiness": not bool(late["ready_after_identity_only_dedup"]),
        "same_semantic_evidence_across_nonzero_arms": all(
            arm_result["arms"][name]["semantic_evidence_sha256"] == arm_result["frozen_semantic_evidence_sha256"]
            for name in ("canonical", "id_placebo", "exact_split", "pre_gate_quotient", "late_dedup")
        ),
        "exact_split_is_q1_p05_fragmented": (
            exact_split["coordinates"]["q"] == 1.0
            and exact_split["coordinates"]["p"] == 0.5
            and exact_split["coordinates"]["regime"] == "evolution_fragmented"
        ),
    }
    if source_audit:
        checks["pinned_source_hashes_match"] = source_audit["source_sha256_match_frozen_pin"]
        checks["pinned_source_contract_matches_projection"] = source_audit["all_required_anchors_present"]

    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "experiment_id": "ASSET-FIRST-STRI-SKILLPRO-P0-20260828",
        "stage": "RECENT_FLAGSHIP_CARRIER_ZERO_PROVIDER_P0",
        "date": "2026-08-28",
        "carrier": {
            "name": "Skill-Pro",
            "paper": "Skill-Pro: Learning Reusable Skills from Experience via Non-Parametric PPO for LLM Agents",
            "venue": "ICML 2026 Spotlight",
            "official_repository": "https://github.com/Miracle1207/Skill-Pro",
            "commit": SKILLPRO_COMMIT,
            "archive_sha256": SKILLPRO_ARCHIVE_SHA256,
        },
        "source_contract_audit": source_audit,
        "frozen_operator_projection": arm_result,
        "partition_geometry": partition_geometry(),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "qualified": "The pinned released source partitions Experience records by Skill name before applying an identity-local readiness threshold. Under the frozen six-record witness, 6 is ready while 3+3 is semantically sufficient but neither identity is ready; pre-gate reunion restores readiness and identity-only late dedup does not.",
            "not_yet_qualified": "This P0 is a pinned-source static contract audit plus an independent deterministic projection. It is not yet an import-and-execute run of the author's SkillEvolution class, does not execute semantic-gradient candidate generation or the PPO Gate, and does not establish downstream task-performance effects.",
            "paper_level_boundary": "Treat M=6 and q/p as a released-code specialization, not as a universal property of the Skill-Pro paper or of self-evolving agents generally.",
        },
        "next_gate": {
            "p0b": "Run the unchanged pinned SkillEvolution scheduler in an author-compatible dependency environment, with model-dependent calls stubbed only after the readiness branch, and verify the same arm reachability.",
            "p1": "Only after P0b passes, freeze real first-party trajectories and run candidate generation plus PPO Gate on matched canonical/split/quotient attribution.",
            "p2": "Only after P1 passes, evaluate frozen resulting skill pools on a preregistered held-out ALFWorld or Mastermind task set with repeated runs.",
        },
        "scientific_boundary": {
            "claim_expansion": False,
            "new_model_calls": 0,
            "new_gpu_runs": 0,
            "model_call_authority": False,
            "gpu_authority": False,
            "behavioral_claim_authorized": False,
            "cross_system_generality_authorized": False,
            "manuscript_rewrite_authorized_by_this_receipt": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
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
