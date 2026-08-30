from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "generated" / "relational-constraint-capacity-pre-f0-20260830.json"
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
EXPECTED_BASE_SHA256 = "7fedadef0553f2b564e4d7b12ab75666134a356be2ba51e4c16a259f5efcdc5a"
EXPECTED_INSTRUCTSCENE_SHA = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"

PREDICATE_FAMILIES = {
    "vertical": ["above", "below"],
    "horizontal": ["left of", "right of"],
    "depth": ["in front of", "behind"],
    "close_horizontal": ["closely left of", "closely right of"],
    "close_depth": ["closely in front of", "closely behind"],
}
RELATION_COUNT_LEVELS = [1, 2, 3, 4, 5]
TOKEN_TARGETS = [52, 68]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return 0.0 if denom == 0 else sum(x * y for x, y in zip(dx, dy)) / denom


def build_permutations() -> list[dict[str, Any]]:
    families = list(PREDICATE_FAMILIES)
    permutations: list[dict[str, Any]] = []
    for rotation in range(len(families)):
        order = families[rotation:] + families[:rotation]
        for direction_phase in range(2):
            relations = []
            for position, family in enumerate(order, start=1):
                predicate = PREDICATE_FAMILIES[family][direction_phase]
                relations.append(
                    {
                        "relation_slot_id": f"{family}:{direction_phase}",
                        "family": family,
                        "predicate": predicate,
                        "subject_slot": f"{family}_subject",
                        "object_slot": f"{family}_object",
                        "addition_position": position,
                    }
                )
            permutations.append(
                {
                    "permutation_id": f"rotation-{rotation}-phase-{direction_phase}",
                    "rotation": rotation,
                    "direction_phase": direction_phase,
                    "relations": relations,
                }
            )
    return permutations


def build_design(permutations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for permutation in permutations:
        for count in RELATION_COUNT_LEVELS:
            relation_set = permutation["relations"][:count]
            for token_target in TOKEN_TARGETS:
                rows.append(
                    {
                        "design_cell_id": (
                            f'{permutation["permutation_id"]}-r{count}-t{token_target}'
                        ),
                        "permutation_id": permutation["permutation_id"],
                        "relation_count": count,
                        "target_clip_tokens_including_special": token_target,
                        "relation_slot_ids": [
                            row["relation_slot_id"] for row in relation_set
                        ],
                        "relation_families": [row["family"] for row in relation_set],
                        "predicates": [row["predicate"] for row in relation_set],
                    }
                )
    return rows


def validate_nested(permutations: list[dict[str, Any]]) -> bool:
    for permutation in permutations:
        ids = [row["relation_slot_id"] for row in permutation["relations"]]
        previous: set[str] = set()
        for count in RELATION_COUNT_LEVELS:
            current = set(ids[:count])
            if not previous.issubset(current) or len(current) != count:
                return False
            previous = current
    return True


def balance_audit(permutations: list[dict[str, Any]]) -> dict[str, Any]:
    by_dose: dict[str, Any] = {}
    pass_all = True
    for count in RELATION_COUNT_LEVELS:
        family_counts: Counter[str] = Counter()
        predicate_counts: Counter[str] = Counter()
        for permutation in permutations:
            for relation in permutation["relations"][:count]:
                family_counts[relation["family"]] += 1
                predicate_counts[relation["predicate"]] += 1
        family_values = list(family_counts.values())
        family_discrepancy = max(family_values) - min(family_values)
        direction_discrepancy = {}
        for family, pair in PREDICATE_FAMILIES.items():
            direction_discrepancy[family] = abs(
                predicate_counts[pair[0]] - predicate_counts[pair[1]]
            )
        dose_pass = family_discrepancy == 0 and max(direction_discrepancy.values()) == 0
        pass_all = pass_all and dose_pass
        by_dose[str(count)] = {
            "family_counts": dict(sorted(family_counts.items())),
            "family_max_minus_min": family_discrepancy,
            "direction_pair_abs_differences": direction_discrepancy,
            "pass": dose_pass,
        }
    return {"by_relation_count": by_dose, "pass": pass_all}


def factorial_audit(design: list[dict[str, Any]]) -> dict[str, Any]:
    counts = [float(row["relation_count"]) for row in design]
    lengths = [
        float(row["target_clip_tokens_including_special"]) for row in design
    ]
    cell_counts = Counter((int(c), int(t)) for c, t in zip(counts, lengths))
    complete = set(cell_counts) == {
        (count, target)
        for count in RELATION_COUNT_LEVELS
        for target in TOKEN_TARGETS
    }
    equal_replication = len(set(cell_counts.values())) == 1
    correlation = pearson(counts, lengths)
    return {
        "cell_replications": {
            f"r{count}_t{target}": cell_counts[(count, target)]
            for count in RELATION_COUNT_LEVELS
            for target in TOKEN_TARGETS
        },
        "complete_factorial": complete,
        "equal_replication": equal_replication,
        "pearson_relation_count_vs_target_tokens": correlation,
        "absolute_correlation_gate": 0.05,
        "pass": complete and equal_replication and abs(correlation) <= 0.05,
    }


def source_audit(instructscene_repo: Path) -> dict[str, Any]:
    import subprocess

    head = subprocess.check_output(
        ["git", "-C", str(instructscene_repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != EXPECTED_INSTRUCTSCENE_SHA:
        raise SystemExit(f"InstructScene revision drift: {head}")

    predicate_source = (
        instructscene_repo / "src" / "data" / "threed_front.py"
    ).read_text(encoding="utf-8")
    encoder_source = (
        instructscene_repo / "src" / "models" / "clip_encoders.py"
    ).read_text(encoding="utf-8")
    evaluator_source = (
        instructscene_repo / "src" / "generate_sg.py"
    ).read_text(encoding="utf-8")
    for predicate in {
        predicate
        for pair in PREDICATE_FAMILIES.values()
        for predicate in pair
    }:
        if f'"{predicate}"' not in predicate_source:
            raise SystemExit(f"official predicate missing: {predicate}")
    required_encoder_fragments = [
        'name="openai/clip-vit-base-patch32"',
        "max_length=77",
        "truncation=True",
    ]
    if not all(fragment in encoder_source for fragment in required_encoder_fragments):
        raise SystemExit("official CLIP encoder contract drift")
    required_evaluator_fragments = [
        "rel_counts += 1",
        "correct_rel_counts += 1",
        "if rel in relations:",
    ]
    if not all(fragment in evaluator_source for fragment in required_evaluator_fragments):
        raise SystemExit("official relation evaluator contract drift")
    return {
        "repository_commit": head,
        "predicate_source_sha256": sha256_file(
            instructscene_repo / "src" / "data" / "threed_front.py"
        ),
        "text_encoder_source_sha256": sha256_file(
            instructscene_repo / "src" / "models" / "clip_encoders.py"
        ),
        "evaluator_source_sha256": sha256_file(
            instructscene_repo / "src" / "generate_sg.py"
        ),
        "text_encoder": "openai/clip-vit-base-patch32",
        "model_max_length": 77,
        "truncation_in_official_code": True,
    }


def port010_snapshot() -> dict[str, Any]:
    plan = json.loads(PORT_PLAN.read_text(encoding="utf-8"))
    rows = [
        row
        for row in plan.get("entries") or []
        if row.get("candidate_id") == "PORT-010"
        and row.get("title")
        == "Complex-description boundary in end-to-end 3D world construction"
    ]
    if len(rows) != 1:
        raise SystemExit("exact PORT-010 row not found")
    row = rows[0]
    adjudication = row["release_change_adjudication"]
    expected_false = [
        "offline_replay_tier_authorized",
        "provider_authority",
        "gpu_authority",
        "scientific_execution_authority",
    ]
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED":
        raise SystemExit("PORT-010 status drift")
    if row["evidence_review"].get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 evidence verdict drift")
    if adjudication.get("remaining_reopen_components") != ["per_case_outcomes"]:
        raise SystemExit("PORT-010 reopen components drift")
    if any(adjudication.get(key) is not False for key in expected_false):
        raise SystemExit("PORT-010 authority drift")
    return {
        "candidate_id": "PORT-010",
        "status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
        "evidence_review": "BLOCK_BAKE_IN",
        "remaining_reopen_components": ["per_case_outcomes"],
        **{key: False for key in expected_false},
        "changed_by_this_object": False,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    if sha256_file(BASE) != EXPECTED_BASE_SHA256:
        raise SystemExit("base Pre-F0 artifact drift")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    if base["object_id"] != "RELATIONAL-CONSTRAINT-CAPACITY-20260830":
        raise SystemExit("object identity drift")
    sources = source_audit(args.instructscene_repo)
    permutations = build_permutations()
    design = build_design(permutations)
    nested_pass = validate_nested(permutations)
    balance = balance_audit(permutations)
    factorial = factorial_audit(design)
    construct_pass = nested_pass and balance["pass"] and factorial["pass"]

    return {
        "schema_version": "relational-constraint-capacity-construct-qualification-v2",
        "generated_at": "2026-08-30T18:20:00+00:00",
        "object_id": "RELATIONAL-CONSTRAINT-CAPACITY-20260830",
        "canonical_candidate_id": None,
        "status": "PRE_F0_HOLD_ASSET_AND_CONSTRUCT_QUALIFICATION",
        "base_pre_f0_artifact": {
            "path": str(BASE.relative_to(ROOT)),
            "sha256": EXPECTED_BASE_SHA256,
        },
        "construct_qualification_v2": {
            "verdict": "PASS" if construct_pass else "FAIL_CLOSED",
            "scope": (
                "Outcome-blind qualification of the construct, endpoint hierarchy, "
                "design identifiability, and analysis preregistration only."
            ),
            "scientific_outcomes_observed": 0,
            "source_audit": sources,
            "official_predicate_families": PREDICATE_FAMILIES,
            "relation_type_balanced_nested_permutations": {
                "relation_count_levels": RELATION_COUNT_LEVELS,
                "permutation_count": len(permutations),
                "construction": (
                    "five cyclic family rotations crossed with two inverse-direction phases; "
                    "each dose is the prefix of its permutation"
                ),
                "nested_prefix_check": nested_pass,
                "balance_audit": balance,
                "permutations": permutations,
            },
            "length_disentanglement": {
                "design": (
                    "Every permutation and relation-count dose is crossed with both exact "
                    "CLIP-token target arms."
                ),
                "target_clip_tokens_including_special": TOKEN_TARGETS,
                "encoder_max_length": 77,
                "headroom_tokens": 9,
                "no_truncation_gate": (
                    "Materialized prompts must tokenize to exactly the assigned target with "
                    "openai/clip-vit-base-patch32 and must retain EOS before position 77."
                ),
                "semantic_identity_gate": (
                    "The two length arms must compile to the identical ordered instructed "
                    "relation triplets; only preregistered meaning-preserving relation templates "
                    "and non-relational discourse wrappers may differ."
                ),
                "wrapper_sensitivity": (
                    "Use two counterbalanced wrapper banks; report their interaction and do not "
                    "interpret beta_length as a universal pure-token law if wrapper heterogeneity "
                    "is detected."
                ),
                "materialization_fail_closed": (
                    "Any object name or template that cannot reach both targets without relation "
                    "loss, truncation, or a new spatial/attribute constraint is excluded before "
                    "outcomes."
                ),
                "factorial_audit": factorial,
                "design_cells": design,
            },
            "endpoint_freeze": {
                "primary": {
                    "name": "relation_level_iRecall",
                    "unit": "one instructed relation triplet",
                    "record": "satisfied in {0,1}",
                    "aggregation": (
                        "sum(satisfied) / number of instructed relation triplets; preserve "
                        "one row per triplet before any scene aggregation"
                    ),
                    "matching": (
                        "official InstructScene exact relation occurrence evaluator; the easy "
                        "closely-collapsed score is diagnostic only"
                    ),
                },
                "secondary": {
                    "name": "exact_all_success",
                    "unit": "scene-generation case",
                    "record": "1 iff every instructed relation triplet is satisfied",
                },
                "diagnostic_only": [
                    "easy iRecall",
                    "scene-graph iRecall",
                    "object coverage",
                    "collision/physical validity",
                    "generation failure",
                    "runtime failure",
                ],
                "hierarchy_change_after_outcomes_forbidden": True,
            },
            "analysis_preregistration": {
                "population": (
                    "all qualified materialized base scenes, seeds, permutations, doses, "
                    "and both length arms; failures remain rows under the frozen failure policy"
                ),
                "primary_model": {
                    "family": "binomial logistic mixed-effects model",
                    "outcome": "relation-level satisfied",
                    "formula": (
                        "satisfied ~ relation_count_c * clip_token_count_c + relation_family "
                        "+ direction_phase + addition_position_c + wrapper_bank "
                        "+ relation_count_c:wrapper_bank + "
                        "(1 + relation_count_c | base_scene_id) + "
                        "(1 | base_scene_id:relation_triplet_id) + (1 | seed)"
                    ),
                    "primary_estimand": (
                        "average marginal relation-count contrast at each preregistered dose, "
                        "averaged over token targets, relation families, directions, wrappers, "
                        "base scenes, and seeds"
                    ),
                    "text_length_estimand": (
                        "average marginal contrast 68 versus 52 CLIP tokens at each dose"
                    ),
                    "simultaneous_effect_requirement": (
                        "relation-count and realized token-length terms remain in the same fitted "
                        "model regardless of individual significance"
                    ),
                },
                "secondary_model": {
                    "family": "binomial logistic mixed-effects model",
                    "outcome": "exact_all_success",
                    "formula": (
                        "exact_all_success ~ relation_count_c * clip_token_count_c "
                        "+ direction_phase + wrapper_bank + "
                        "(1 + relation_count_c | base_scene_id) + (1 | seed)"
                    ),
                    "multiplicity": (
                        "secondary endpoint is interpreted only after the primary hierarchy; "
                        "no substitution for relation-level iRecall"
                    ),
                },
                "boundary_modeling_after_primary": {
                    "candidate_models": [
                        "smooth logistic dose response",
                        "piecewise logistic",
                        "segmented/change-point logistic",
                    ],
                    "selection": (
                        "grouped cross-validation by base_scene_id; breakpoint claim requires "
                        "out-of-sample improvement and stable scene-cluster bootstrap interval"
                    ),
                    "no_breakpoint_policy": (
                        "report smooth capacity degradation and do not claim a boundary"
                    ),
                },
                "design_diagnostics_before_outcomes": {
                    "absolute_count_length_correlation_max": 0.05,
                    "all_factorial_cells_present": True,
                    "equal_replication_required": True,
                    "family_max_minus_min_at_each_dose": 0,
                    "direction_pair_abs_difference_at_each_dose": 0,
                    "no_truncation_required": True,
                    "same_relation_triplets_across_length_arms": True,
                },
                "missingness_and_failure": (
                    "No complete-case deletion for generation/evaluator failures. Fit the "
                    "relation model with failure-coded unsatisfied relations as primary and "
                    "repeat with failures separated as a sensitivity analysis."
                ),
            },
        },
        "dual_key_progression": {
            "construct_qualification_v2": "PASS" if construct_pass else "FAIL",
            "non_scientific_execution_smoke": "NOT_RUN",
            "proposal_gate": "CLOSED_REQUIRES_BOTH_PASS",
            "if_both_pass_only": [
                "propose confirmation of 3D-FRONT/3D-FUTURE license acceptance",
                "propose official two-stage InstructScene training GPU authority",
            ],
            "proposal_is_not_authority": True,
        },
        "unofficial_checkpoint_policy": {
            "allowed_scope": "NON_SCIENTIFIC_EXECUTION_SMOKE",
            "case_count_min": 3,
            "case_count_max": 10,
            "pipeline_components": [
                "inference",
                "evaluator",
                "checkpoint writer",
                "resume/idempotency",
            ],
            "scientific_evidence_eligible": False,
            "p1_projection_forbidden": True,
            "may_qualify_official_reproduction": False,
        },
        "relation_to_port010": port010_snapshot(),
        "authority": {
            "provider": False,
            "gpu": False,
            "scientific_execution": False,
            "p1": False,
            "official_training": False,
            "data_license_acceptance_inferred": False,
        },
        "scientific_authority": False,
        "execution_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--instructscene-repo",
        type=Path,
        default=Path(
            "/data/wyt/constraint-capacity-source-audit-20260829/"
            "InstructScene-a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
        ),
    )
    args = parser.parse_args()
    artifact = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
