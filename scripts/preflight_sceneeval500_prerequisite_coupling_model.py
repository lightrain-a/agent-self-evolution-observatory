from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "generated" / "sceneeval500-outcome-blind-constraint-audit-20260828.json"
REVIEW = ROOT / "generated" / "constraint-integration-sceneeval-independent-review-20260828.json"
EXPECTED_AUDIT_SHA = "a3eaaa0571d51928e70f0094de1d0d4542211de165d1a196135be55df1247e45"
EXPECTED_REVIEW_SHA = "cb82ab4531dd1a76f05af2f027f3213ffc06b9e771beb45007a9446a55186862"
EXPECTED_ANNOTATIONS_SHA = "d770886e249e7be04cc3e183ddd1b9e23c2aa6a7666226b5fe5da17236286ae3"
CHANNELS = ("ObjAttr", "OORel", "OARel")
MIN_COMPOSITION_TOKEN_FREQUENCY = 10
POWER_SEED = 20260828
POWER_ALPHA = 0.05
POWER_NULL_SIMS = 1200
POWER_ALT_SIMS = 700
POWER_SAMPLE_SIZES = (402, 350, 300, 250, 200)
POWER_BASE_CORRELATIONS = (0.10, 0.25, 0.40)
POWER_TOPOLOGY_DELTAS = (0.10, 0.15, 0.20, 0.25)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec_list(value: str) -> list[list[str]]:
    return [
        [part.strip() for part in spec.strip().split(",")]
        for spec in str(value or "").split(";")
        if spec.strip()
    ]


def build_metadata_vocabulary(rows: list[dict[str, str]]) -> dict[str, Any]:
    attr_tokens: Counter[str] = Counter()
    relation_tokens: dict[str, Counter[str]] = {"OORel": Counter(), "OARel": Counter()}
    object_categories: Counter[str] = Counter()
    for row in rows:
        for parts in spec_list(row["ObjAttr"]):
            if len(parts) >= 4:
                object_categories[parts[2]] += 1
                attr_tokens.update(parts[3:])
        for parts in spec_list(row["OORel"]):
            if len(parts) >= 5:
                relation_tokens["OORel"][parts[2]] += 1
                for ref in parts[4:]:
                    category = ref.split(":", 1)[0].strip()
                    if category:
                        object_categories[category] += 1
        for parts in spec_list(row["OARel"]):
            if len(parts) >= 4:
                relation_tokens["OARel"][parts[2]] += 1
                category = parts[3].split(":", 1)[0].strip()
                if category:
                    object_categories[category] += 1

    def freeze(counter: Counter[str]) -> list[dict[str, Any]]:
        return [
            {"token": token, "frequency": count}
            for token, count in sorted(counter.items())
            if count >= MIN_COMPOSITION_TOKEN_FREQUENCY
        ]

    frozen = {
        "minimum_frequency": MIN_COMPOSITION_TOKEN_FREQUENCY,
        "rare_token_policy": "all lower-frequency tokens map to a channel-specific OTHER bucket; no post-outcome vocabulary expansion",
        "ObjAttr_attribute_tokens": freeze(attr_tokens),
        "OORel_relationship_tokens": freeze(relation_tokens["OORel"]),
        "OARel_relationship_tokens": freeze(relation_tokens["OARel"]),
        "downstream_object_categories": freeze(object_categories),
    }
    frozen["vocabulary_sha256"] = hashlib.sha256(
        json.dumps(frozen, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return frozen


def annotated_availability(rows: list[dict[str, str]]) -> dict[str, Any]:
    present = [
        {channel: bool(row[channel].strip()) for channel in CHANNELS}
        for row in rows
    ]
    pair_counts: dict[str, int] = {}
    for i, left in enumerate(CHANNELS):
        for right in CHANNELS[i + 1 :]:
            pair_counts[f"{left}__{right}"] = sum(row[left] and row[right] for row in present)
    all_three = sum(all(row[channel] for channel in CHANNELS) for row in present)
    return {
        "annotated_channel_scene_counts": {
            channel: sum(row[channel] for row in present) for channel in CHANNELS
        },
        "annotated_pair_scene_counts": pair_counts,
        "annotated_all_three_scene_count": all_three,
        "note": "annotation availability is not evaluator prerequisite eligibility; actual matching-derived eligibility remains outcome-unread and must not be inferred from these counts",
    }


def _cholesky3(cov: list[list[float]]) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    l00 = math.sqrt(cov[0][0])
    l10 = cov[1][0] / l00
    l20 = cov[2][0] / l00
    d11 = cov[1][1] - l10 * l10
    if d11 <= 0:
        raise ValueError("covariance is not positive definite at d11")
    l11 = math.sqrt(d11)
    l21 = (cov[2][1] - l20 * l10) / l11
    d22 = cov[2][2] - l20 * l20 - l21 * l21
    if d22 <= 0:
        raise ValueError("covariance is not positive definite at d22")
    l22 = math.sqrt(d22)
    return ((l00, 0.0, 0.0), (l10, l11, 0.0), (l20, l21, l22))


def _covariance_determinant3(cov: list[list[float]]) -> float:
    a, b, c = cov[0]
    d, e, f = cov[1]
    g, h, i = cov[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def topology_statistic_from_cov(corr01: float, corr02: float, corr12: float) -> float:
    mean = (corr01 + corr02 + corr12) / 3.0
    return max(abs(corr01 - mean), abs(corr02 - mean), abs(corr12 - mean))


def _simulate_topology_statistic(rng: random.Random, sample_size: int, cov: list[list[float]]) -> float:
    chol = _cholesky3(cov)
    sums = [0.0, 0.0, 0.0]
    squares = [0.0, 0.0, 0.0]
    cross01 = cross02 = cross12 = 0.0
    for _ in range(sample_size):
        z0, z1, z2 = rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)
        x0 = chol[0][0] * z0
        x1 = chol[1][0] * z0 + chol[1][1] * z1
        x2 = chol[2][0] * z0 + chol[2][1] * z1 + chol[2][2] * z2
        xs = (x0, x1, x2)
        for idx, value in enumerate(xs):
            sums[idx] += value
            squares[idx] += value * value
        cross01 += x0 * x1
        cross02 += x0 * x2
        cross12 += x1 * x2

    def corr(left: int, right: int, cross: float) -> float:
        numerator = cross - sums[left] * sums[right] / sample_size
        left_ss = squares[left] - sums[left] * sums[left] / sample_size
        right_ss = squares[right] - sums[right] * sums[right] / sample_size
        return numerator / math.sqrt(left_ss * right_ss)

    return topology_statistic_from_cov(
        corr(0, 1, cross01),
        corr(0, 2, cross02),
        corr(1, 2, cross12),
    )


def _quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def simulate_power() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for sample_size in POWER_SAMPLE_SIZES:
        for rho0 in POWER_BASE_CORRELATIONS:
            seed = POWER_SEED + sample_size * 1000 + int(rho0 * 1000)
            rng = random.Random(seed)
            null_cov = [[1.0, rho0, rho0], [rho0, 1.0, rho0], [rho0, rho0, 1.0]]
            null_stats = [
                _simulate_topology_statistic(rng, sample_size, null_cov)
                for _ in range(POWER_NULL_SIMS)
            ]
            critical = _quantile(null_stats, 1.0 - POWER_ALPHA)
            for delta in POWER_TOPOLOGY_DELTAS:
                alt_cov = [[1.0, rho0 + delta, rho0], [rho0 + delta, 1.0, rho0], [rho0, rho0, 1.0]]
                determinant = _covariance_determinant3(alt_cov)
                _cholesky3(alt_cov)
                hits = 0
                for _ in range(POWER_ALT_SIMS):
                    stat = _simulate_topology_statistic(rng, sample_size, alt_cov)
                    hits += stat > critical
                scenarios.append({
                    "complete_case_scene_count": sample_size,
                    "exchangeable_base_residual_correlation": rho0,
                    "one_pair_topology_increment": delta,
                    "null_95pct_critical_statistic": round(critical, 6),
                    "estimated_power": round(hits / POWER_ALT_SIMS, 6),
                    "covariance_determinant": round(determinant, 6),
                })

    worst_case: list[dict[str, Any]] = []
    for sample_size in POWER_SAMPLE_SIZES:
        for delta in POWER_TOPOLOGY_DELTAS:
            values = [
                row["estimated_power"]
                for row in scenarios
                if row["complete_case_scene_count"] == sample_size
                and math.isclose(row["one_pair_topology_increment"], delta)
            ]
            worst_case.append({
                "complete_case_scene_count": sample_size,
                "one_pair_topology_increment": delta,
                "worst_case_power_across_base_correlations": round(min(values), 6),
            })
    return {
        "simulation_kind": "latent-residual-topology design sensitivity only; not a substitute for the preregistered binomial mixed-model inference and not scientific evidence",
        "seed": POWER_SEED,
        "alpha": POWER_ALPHA,
        "null_simulations_per_n_rho": POWER_NULL_SIMS,
        "alternative_simulations_per_n_rho_delta": POWER_ALT_SIMS,
        "test_statistic": "max absolute deviation of the three downstream pairwise residual correlations from their within-sample mean; null is exchangeable residual correlation",
        "base_residual_correlations": list(POWER_BASE_CORRELATIONS),
        "topology_increments": list(POWER_TOPOLOGY_DELTAS),
        "sample_sizes": list(POWER_SAMPLE_SIZES),
        "scenarios": scenarios,
        "worst_case_summary": worst_case,
        "design_interpretation": {
            "confirmatory_sensitivity_target": "at least 350 scenes jointly prerequisite-eligible across ObjAttr/OORel/OARel gives >=80% simulated worst-case sensitivity to a 0.20 one-pair latent residual-correlation topology increment under this conservative complete-case proxy",
            "below_350_complete_cases": "do not reinterpret a null result as independence; remain underpowered for the frozen moderate topology increment and retain HOLD/INCONCLUSIVE unless the preregistered full joint model has independently justified power",
            "small_effect_warning": "the design is not powered to treat failure to detect 0.10-0.15 residual-correlation increments as evidence for conditional independence",
        },
    }


def build_contract(annotations: Path) -> dict[str, Any]:
    if sha256_file(AUDIT) != EXPECTED_AUDIT_SHA:
        raise SystemExit("SceneEval audit digest drifted")
    if sha256_file(REVIEW) != EXPECTED_REVIEW_SHA:
        raise SystemExit("independent review digest drifted")
    if sha256_file(annotations) != EXPECTED_ANNOTATIONS_SHA:
        raise SystemExit("SceneEval annotations digest drifted")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    if review.get("status") != "REVISE_BEFORE_PREREGISTRATION":
        raise SystemExit("review gate is not REVISE")
    measurement = audit.get("measurement_dependency_preflight") or {}
    if measurement.get("verified") is not True or measurement.get("raw_matching_observable") is not True:
        raise SystemExit("matching prerequisite state is not auditable")
    with annotations.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 500:
        raise SystemExit("unexpected SceneEval row count")
    vocabulary = build_metadata_vocabulary(rows)
    availability = annotated_availability(rows)
    power = simulate_power()
    return {
        "schema_version": "sceneeval500-prerequisite-coupling-preregistration-draft-v1",
        "status": "MODEL_REVISION_COMPILED_POWER_PREFLIGHT_ONLY",
        "scientific_authority": False,
        "execution_authority": False,
        "outcome_exposure": {
            "hsm_scene_contents_read": False,
            "object_matching_results_read": False,
            "sceneeval_metric_results_read": False,
            "performance_conditioned_feature_or_threshold_selection": False,
            "only_inputs": ["released SceneEval annotations", "verified SceneEval evaluator source", "independent outcome-blind reviews", "synthetic power simulation"],
        },
        "review_binding": {
            "artifact": str(REVIEW.relative_to(ROOT)),
            "sha256": EXPECTED_REVIEW_SHA,
            "verdict": review["status"],
            "consensus_null": review["consensus"]["strongest_null"],
        },
        "measurement_contract": {
            "stage_P_prerequisite": {
                "definition": "official shared ObjMatching and per-spec prerequisite flags are a separate measurement stage",
                "ObjCount_role": "matching-derived prerequisite/control and secondary diagnostic; never a peer primary downstream coupling outcome",
                "ObjAttr_eligibility": "required object category has at least one official matched object; preserve official num_category_in_scene",
                "OORel_eligibility": "official all_objects_present is true for the relationship spec",
                "OARel_eligibility": "official obj_present is true for the architecture-relation spec",
                "prerequisite_failures": "reported separately and never recoded as downstream interaction failures",
            },
            "stage_D_downstream": {
                "primary_channels": list(CHANNELS),
                "scene_channel_observation": "Y_ic = failed prerequisite-eligible downstream specs; n_ic = number prerequisite-eligible downstream specs",
                "primary_distribution": "Y_ic | n_ic,p_ic ~ Binomial(n_ic,p_ic); scenes/channels with n_ic=0 contribute only to prerequisite-stage summaries",
                "scope": "operational residual dependence conditional on the frozen evaluator/matching system; not a causal representation-mechanism claim",
            },
            "raw_matching_artifacts_required": measurement["raw_matching_artifacts"],
            "official_semantic_vlm": measurement["official_semantic_vlm"],
            "local_vlm_substitution_policy": "a local evaluator must be independently validated and separately named; it cannot be aliased to official SceneEval",
        },
        "same_information_metadata_block": {
            "always_include": [
                "generator identity",
                "benchmark-authored difficulty",
                "standardized instruction word count with frozen nonlinear spline/basis shared by null and candidate",
                "total explicit spec count",
                "ObjAttr/OORel/OARel spec counts",
                "official matching coverage fraction and not-matched object count",
                "channel identity",
            ],
            "composition_vocabulary": vocabulary,
            "composition_effect_policy": "released attribute/relation/object-category main effects enter both null and candidate with the same training-fold-only ridge/shrinkage rule; no outcome-based vocabulary pruning or feature addition",
        },
        "nested_model_contract": {
            "N0": "channel-specific binomial-logit fixed effects using the same-information metadata block except matching coverage; no latent cross-channel residual structure",
            "N1": "N0 plus official matching/prerequisite coverage covariates; prerequisite failures remain in stage P rather than downstream Y_ic",
            "N2_strongest_null": "N1 plus a three-channel logistic-normal scene residual u_i with channel-specific latent scales D=diag(s_Attr,s_OOR,s_OAR) and an exchangeable correlation matrix R_eq(rho), where all three off-diagonal correlations equal the same nuisance rho. This absorbs arbitrary-strength generic shared scene frailty while allowing channel-specific overdispersion, but forbids type-specific correlation topology.",
            "candidate": "same fixed effects and channel-specific latent scales as N2, but replace R_eq(rho) with one positive-semidefinite unstructured 3x3 correlation matrix R_unstructured. The scientific disagreement is nonexchangeability: the three pairwise correlations need not be equal.",
            "nesting": "N2 is the candidate subspace rho_Attr,OOR = rho_Attr,OAR = rho_OOR,OAR. Relative to the one-rho N2 nuisance structure, the unstructured three-correlation candidate adds exactly two nonexchangeability degrees of freedom.",
            "scientific_parameter": "two-dimensional departure of the three downstream latent residual correlations from their common mean/exchangeable subspace; the average/shared correlation itself is nuisance, not evidence for the candidate",
            "identifiability_constraints": [
                "do not separately decompose shared covariance into a common random intercept plus correlated channel residuals; only the total three-channel logistic-normal covariance is estimated",
                "channel latent scales are positive and the correlation matrix is positive semidefinite",
                "candidate correlation matrix uses a frozen Cholesky/partial-correlation parameterization so every fitted value is valid",
                "fixed-effect and metadata-composition design matrices are identical between N2 and candidate",
                "no downstream outcome from one channel is used as a predictor for another channel",
            ],
        },
        "primary_confirmatory_test": {
            "population": "all available SceneEval-500 scenes for a preregistered generator lane; held-out split is the frozen hash-based instruction fold assignment already content-addressed in the construct audit",
            "metric": "grouped held-out joint predictive log loss / ELPD for the downstream three-channel counts",
            "disagreement": "candidate must improve held-out joint predictive performance over N2 and the joint two-degree nonexchangeability departure of the three latent residual correlations from the exchangeable subspace must exceed the frozen practical-equivalence region; a positive average/shared correlation alone does not support the candidate",
            "uncertainty_calibration": "cluster bootstrap or parametric bootstrap resampling at the scene level only, with model fitting entirely inside each training fold; exact implementation must be frozen before S2 evaluator smoke outputs are read",
            "practical_equivalence_region": "to be fixed from outcome-blind design simulation, not estimated from HSM outcomes",
            "multiple_testing": "the two-degree joint nonexchangeability/topology test is primary; individual pair correlations and contrasts are secondary only if the joint test passes",
            "matched_panel_role": "52 outcome-blind pairs are robustness only; they cannot replace the full-population primary test or be rematched after outcomes",
        },
        "power_design_preflight": power,
        "annotation_availability": availability,
        "gates_after_this_preflight": {
            "model_revision_satisfied": True,
            "power_preflight_satisfied": True,
            "formal_preregistration_clear": False,
            "why_not_clear": [
                "HSM scene contents remain gated/unmaterialized on the current server identity",
                "official evaluator measurement smoke has not been run",
                "the exact mixed-model implementation/bootstrap code has not yet been frozen and validated on synthetic data",
                "second generator lane remains unqualified for paper-level transport/generalization",
            ],
            "bounded_p0_may_later_use_single_hsm": True,
            "paper_level_requires_second_generator": True,
        },
        "stop_hold_rules": [
            "STOP scientific interpretation if raw official object-matching/prerequisite state cannot be preserved alongside semantic outcomes",
            "HOLD full three-channel confirmatory interpretation if fewer than 350 scenes are jointly prerequisite-eligible, unless a separately frozen full joint-model power analysis justifies lower availability without outcome-dependent changes",
            "STOP the candidate if N2 is predictively equivalent to or better than the candidate under the frozen uncertainty rule",
            "STOP generator-side interpretation if coupling disappears on the oracle/verified-matching negative control",
            "HOLD paper-level generalization until a second independently qualified generator/external scene lane is evaluated under the same frozen contract",
        ],
        "forbidden_claims_even_if_positive": [
            "generic causal representation bottleneck without a controlled intervention",
            "universal 3D-generator constraint-coupling law from HSM alone",
            "naive four-way ObjCount/ObjAttr/OORel/OARel co-failure as evidence of generator interaction",
            "local-evaluator results labeled as official SceneEval unless independently validated against the frozen official evaluator",
        ],
        "authority": {
            "canonical_generator": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "local_validation": False,
            "p0": False,
            "provider": False,
            "gpu": False,
            "scientific": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = build_contract(args.annotations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    power = contract["power_design_preflight"]
    print(json.dumps({
        "status": contract["status"],
        "vocabulary_sha256": contract["same_information_metadata_block"]["composition_vocabulary"]["vocabulary_sha256"],
        "annotated_all_three": contract["annotation_availability"]["annotated_all_three_scene_count"],
        "power_worst_case": power["worst_case_summary"],
        "formal_preregistration_clear": contract["gates_after_this_preflight"]["formal_preregistration_clear"],
        "scientific_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
