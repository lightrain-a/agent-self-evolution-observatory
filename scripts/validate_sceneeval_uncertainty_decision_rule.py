from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import platform
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.special import gammaln, logsumexp

from validate_sceneeval_logistic_normal_topology import (
    FINAL_QUADRATURE_ORDER,
    correlation_from_covariance,
    fit_candidate,
    fit_n2,
    make_covariance,
    max_exchangeability_deviation,
    quadrature,
    simulate_dataset,
)

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "generated" / "sceneeval500-prerequisite-coupling-preregistration-draft-20260828.json"
TOPOLOGY_PREFLIGHT = ROOT / "generated" / "sceneeval500-logistic-normal-topology-implementation-preflight-20260828.json"
CALIBRATION_PREFLIGHT = ROOT / "generated" / "sceneeval500-marginal-calibration-implementation-preflight-20260828.json"

EXPECTED_PREREG_SHA = "269412b2b0ac270de00d1cca60f4e429ca3b48aae5d62359be073a6095abc365"
EXPECTED_TOPOLOGY_SHA = "4021b01498c5d6f18219fb1b3f34c4a77d2ed217f6dfeaba1a49cd7a83bb9f5a"
EXPECTED_CALIBRATION_SHA = "976870a4946d69222334c7330f7380112d91afd05be75c8e25e6afae34c28fbf"

OUTER_FOLDS = 5
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 2026083017
ALPHA = 0.05
MIN_CONFIRMATORY_SCENES = 350
PRACTICAL_EQUIVALENCE_MAX_DEVIATION = 0.10


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_digest(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise SystemExit(f"artifact digest drift: {path.name}: {actual} != {expected}")


def per_scene_loglik(
    y: np.ndarray,
    n: np.ndarray,
    eta: np.ndarray,
    covariance: np.ndarray,
    *,
    order: int = FINAL_QUADRATURE_ORDER,
) -> np.ndarray:
    if y.shape != n.shape or y.shape != eta.shape or y.ndim != 2 or y.shape[1] != 3:
        raise ValueError("y, n, eta must all have shape [scene, 3]")
    np.linalg.cholesky(covariance)
    grid, log_weights = quadrature(order)
    lower = np.linalg.cholesky(covariance)
    random_effects = grid @ lower.T
    logits = eta[:, None, :] + random_effects[None, :, :]
    log_coeff = (gammaln(n + 1) - gammaln(y + 1) - gammaln(n - y + 1))[:, None, :]
    success_logprob = -np.logaddexp(0.0, -logits)
    failure_logprob = -np.logaddexp(0.0, logits)
    conditional = log_coeff + y[:, None, :] * success_logprob + (n - y)[:, None, :] * failure_logprob
    return logsumexp(log_weights[None, :] + conditional.sum(axis=2), axis=1)


def paired_scene_bootstrap(score_delta: np.ndarray) -> dict[str, float]:
    if score_delta.ndim != 1 or len(score_delta) < 2:
        raise ValueError("score_delta must be a one-dimensional scene-level vector")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    scene_count = len(score_delta)
    # Chunking keeps memory bounded while preserving the exact fixed-seed resampling contract.
    means: list[np.ndarray] = []
    remaining = BOOTSTRAP_RESAMPLES
    while remaining:
        chunk = min(1000, remaining)
        indices = rng.integers(0, scene_count, size=(chunk, scene_count))
        means.append(score_delta[indices].mean(axis=1))
        remaining -= chunk
    bootstrap_means = np.concatenate(means)
    lower = float(np.quantile(bootstrap_means, ALPHA / 2.0))
    upper = float(np.quantile(bootstrap_means, 1.0 - ALPHA / 2.0))
    return {
        "mean_elpd_gain_per_scene": float(score_delta.mean()),
        "median_elpd_gain_per_scene": float(np.median(score_delta)),
        "ci95_lower": lower,
        "ci95_upper": upper,
        "total_elpd_gain": float(score_delta.sum()),
    }


def decision(*, scene_count: int, predictive: dict[str, float], topology_deviation: float) -> str:
    if scene_count < MIN_CONFIRMATORY_SCENES:
        return "HOLD_UNDERPOWERED_COMPLETE_CASE_AVAILABILITY"
    if predictive["ci95_upper"] <= 0.0:
        return "STOP_N2_PREDICTIVELY_EQUIVALENT_OR_BETTER"
    if topology_deviation <= PRACTICAL_EQUIVALENCE_MAX_DEVIATION:
        return "STOP_TOPOLOGY_WITHIN_PRACTICAL_EQUIVALENCE_REGION"
    if predictive["ci95_lower"] > 0.0:
        return "SYNTHETIC_SUPPORT_RULE_TRIGGERED_NO_SCIENTIFIC_AUTHORITY"
    return "HOLD_PREDICTIVE_UNCERTAINTY_CROSSES_ZERO"


def _fit_fold_task(payload: tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> dict[str, Any]:
    fold, y, n, eta, fold_ids = payload
    heldout = fold_ids == fold
    training = ~heldout
    n2 = fit_n2(y[training], n[training], eta[training])
    if not n2["success"]:
        raise RuntimeError(f"N2 synthetic cross-fit failed for fold{fold}: {n2['message']}")
    candidate = fit_candidate(y[training], n[training], eta[training], n2["covariance"])
    if not candidate["success"]:
        raise RuntimeError(f"candidate synthetic cross-fit failed for fold{fold}: {candidate['message']}")
    n2_score = per_scene_loglik(y[heldout], n[heldout], eta[heldout], n2["covariance"])
    candidate_score = per_scene_loglik(y[heldout], n[heldout], eta[heldout], candidate["covariance"])
    return {
        "fold": fold,
        "heldout_indices": np.flatnonzero(heldout),
        "score_delta": candidate_score - n2_score,
        "train_scene_count": int(training.sum()),
        "heldout_scene_count": int(heldout.sum()),
        "n2_iterations": int(n2["iterations"]),
        "candidate_iterations": int(candidate["iterations"]),
        "candidate_topology_deviation": float(max_exchangeability_deviation(candidate["correlation"])),
    }


def _fit_full_task(payload: tuple[np.ndarray, np.ndarray, np.ndarray]) -> dict[str, Any]:
    y, n, eta = payload
    n2 = fit_n2(y, n, eta)
    if not n2["success"]:
        raise RuntimeError(f"full N2 synthetic fit failed: {n2['message']}")
    candidate = fit_candidate(y, n, eta, n2["covariance"])
    if not candidate["success"]:
        raise RuntimeError(f"full candidate synthetic fit failed: {candidate['message']}")
    return {
        "correlation": candidate["correlation"],
        "topology_deviation": float(max_exchangeability_deviation(candidate["correlation"])),
    }


def crossfit_scenario(
    *,
    name: str,
    covariance: np.ndarray,
    seed: int,
    scene_count: int,
) -> dict[str, Any]:
    y, n, eta = simulate_dataset(scene_count, covariance, seed)
    fold_ids = np.arange(scene_count, dtype=int) % OUTER_FOLDS
    score_delta = np.full(scene_count, np.nan, dtype=float)
    folds: list[dict[str, Any]] = []

    workers = min(OUTER_FOLDS + 1, max(1, os.cpu_count() or 1))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        fold_futures = [
            pool.submit(_fit_fold_task, (fold, y, n, eta, fold_ids))
            for fold in range(OUTER_FOLDS)
        ]
        full_future = pool.submit(_fit_full_task, (y, n, eta))
        for future in fold_futures:
            row = future.result()
            score_delta[row["heldout_indices"]] = row["score_delta"]
            folds.append(
                {
                    "fold": int(row["fold"]),
                    "train_scene_count": int(row["train_scene_count"]),
                    "heldout_scene_count": int(row["heldout_scene_count"]),
                    "n2_iterations": int(row["n2_iterations"]),
                    "candidate_iterations": int(row["candidate_iterations"]),
                    "candidate_minus_n2_heldout_elpd": float(row["score_delta"].sum()),
                    "candidate_topology_deviation": float(row["candidate_topology_deviation"]),
                }
            )
        full = full_future.result()

    folds.sort(key=lambda row: row["fold"])
    if np.isnan(score_delta).any():
        raise SystemExit(f"cross-fit score vector incomplete for {name}")

    topology_deviation = float(full["topology_deviation"])
    predictive = paired_scene_bootstrap(score_delta)

    return {
        "name": name,
        "seed": seed,
        "scene_count": scene_count,
        "true_correlation": np.round(correlation_from_covariance(covariance), 6).tolist(),
        "fold_assignment": "synthetic scene index modulo 5; real analysis uses the already frozen SceneEval instruction-hash fold assignment",
        "folds": folds,
        "predictive_uncertainty": {k: round(v, 8) for k, v in predictive.items()},
        "full_fit_candidate_correlation": np.round(full["correlation"], 6).tolist(),
        "full_fit_topology_deviation": round(topology_deviation, 8),
        "decision": decision(scene_count=scene_count, predictive=predictive, topology_deviation=topology_deviation),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scene-count", type=int, default=400)
    args = parser.parse_args()

    require_digest(PREREG, EXPECTED_PREREG_SHA)
    require_digest(TOPOLOGY_PREFLIGHT, EXPECTED_TOPOLOGY_SHA)
    require_digest(CALIBRATION_PREFLIGHT, EXPECTED_CALIBRATION_SHA)
    if args.scene_count < MIN_CONFIRMATORY_SCENES:
        raise SystemExit(f"synthetic validation scene count must be >= {MIN_CONFIRMATORY_SCENES}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    power = prereg["power_design_preflight"]
    small_effect_warning = power["design_interpretation"]["small_effect_warning"]
    if "0.10-0.15" not in small_effect_warning:
        raise SystemExit("outcome-blind small-effect warning drifted")

    # A one-pair correlation increment delta maps to max_j |rho_j - mean(rho)| = 2*delta/3.
    # Delta=0.15 therefore maps exactly to 0.10. The existing outcome-blind power study warns
    # against treating 0.10-0.15 increments as reliably detectable evidence. We freeze that
    # boundary as the practical-equivalence region instead of learning a threshold from HSM.
    derived_boundary = 2.0 * 0.15 / 3.0
    if not math.isclose(derived_boundary, PRACTICAL_EQUIVALENCE_MAX_DEVIATION, rel_tol=0.0, abs_tol=1e-12):
        raise SystemExit("practical-equivalence derivation mismatch")

    null_covariance = make_covariance((1.0, 0.9, 1.1), (0.30, 0.30, 0.30))
    alternative_covariance = make_covariance((1.0, 0.9, 1.1), (0.65, 0.05, 0.05))

    null = crossfit_scenario(
        name="exchangeable_null",
        covariance=null_covariance,
        seed=2026083018,
        scene_count=args.scene_count,
    )
    alternative = crossfit_scenario(
        name="strong_nonexchangeable_alternative",
        covariance=alternative_covariance,
        seed=2026083019,
        scene_count=args.scene_count,
    )

    # Pure decision-function checks make the practical-equivalence logic explicit and do not
    # depend on selecting a favorable synthetic random seed.
    decision_unit_checks = {
        "underpowered_blocks_support": decision(
            scene_count=349,
            predictive={"ci95_lower": 0.02, "ci95_upper": 0.05},
            topology_deviation=0.20,
        ),
        "predictive_n2_win_stops": decision(
            scene_count=400,
            predictive={"ci95_lower": -0.04, "ci95_upper": -0.01},
            topology_deviation=0.20,
        ),
        "practical_equivalence_blocks_tiny_topology": decision(
            scene_count=400,
            predictive={"ci95_lower": 0.01, "ci95_upper": 0.05},
            topology_deviation=0.10,
        ),
        "uncertain_prediction_holds": decision(
            scene_count=400,
            predictive={"ci95_lower": -0.01, "ci95_upper": 0.04},
            topology_deviation=0.20,
        ),
        "joint_rule_supports_only_both": decision(
            scene_count=400,
            predictive={"ci95_lower": 0.01, "ci95_upper": 0.05},
            topology_deviation=0.11,
        ),
    }

    expected_unit = {
        "underpowered_blocks_support": "HOLD_UNDERPOWERED_COMPLETE_CASE_AVAILABILITY",
        "predictive_n2_win_stops": "STOP_N2_PREDICTIVELY_EQUIVALENT_OR_BETTER",
        "practical_equivalence_blocks_tiny_topology": "STOP_TOPOLOGY_WITHIN_PRACTICAL_EQUIVALENCE_REGION",
        "uncertain_prediction_holds": "HOLD_PREDICTIVE_UNCERTAINTY_CROSSES_ZERO",
        "joint_rule_supports_only_both": "SYNTHETIC_SUPPORT_RULE_TRIGGERED_NO_SCIENTIFIC_AUTHORITY",
    }
    if decision_unit_checks != expected_unit:
        raise SystemExit(f"decision-rule unit checks failed: {decision_unit_checks}")
    if null["decision"] == "SYNTHETIC_SUPPORT_RULE_TRIGGERED_NO_SCIENTIFIC_AUTHORITY":
        raise SystemExit("exchangeable-null synthetic scenario spuriously triggered support")
    if alternative["decision"] != "SYNTHETIC_SUPPORT_RULE_TRIGGERED_NO_SCIENTIFIC_AUTHORITY":
        raise SystemExit(f"strong alternative failed synthetic support rule: {alternative['decision']}")

    artifact = {
        "schema_version": "sceneeval-uncertainty-practical-equivalence-preflight-v1",
        "status": "UNCERTAINTY_AND_PRACTICAL_EQUIVALENCE_SYNTHETIC_PASS",
        "scientific_authority": False,
        "execution_authority": False,
        "input_artifacts": {
            "preregistration": str(PREREG.relative_to(ROOT)),
            "preregistration_sha256": EXPECTED_PREREG_SHA,
            "topology_preflight": str(TOPOLOGY_PREFLIGHT.relative_to(ROOT)),
            "topology_preflight_sha256": EXPECTED_TOPOLOGY_SHA,
            "marginal_calibration_preflight": str(CALIBRATION_PREFLIGHT.relative_to(ROOT)),
            "marginal_calibration_preflight_sha256": EXPECTED_CALIBRATION_SHA,
        },
        "outcome_exposure": {
            "sceneeval_generator_outputs_read": False,
            "sceneeval_matching_outputs_read": False,
            "sceneeval_metric_outputs_read": False,
            "synthetic_outcomes_only": True,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "required_runtime_on_69": "/home/wyt/anaconda3/bin/python",
            "new_packages_installed": False,
        },
        "frozen_real_analysis_decision_rule": {
            "unit": "scene; all downstream requirements from one SceneEval instruction stay in the same cluster",
            "prediction": "five frozen instruction-hash folds; N2 and candidate are fit only on each outer training fold, and every scene contributes exactly one held-out joint log-score difference",
            "uncertainty": "paired nonparametric scene-cluster bootstrap over the complete vector of out-of-fold candidate-minus-N2 scene log-score differences",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "confidence_level": 1.0 - ALPHA,
            "support_predictive_rule": "95% paired scene-bootstrap interval lower bound for mean held-out candidate-minus-N2 ELPD per scene must be > 0",
            "stop_predictive_rule": "95% paired scene-bootstrap interval upper bound <= 0 means N2 is predictively equivalent or better for this candidate",
            "otherwise_predictive_rule": "if the interval crosses 0, retain HOLD/INCONCLUSIVE; do not call independence",
            "practical_topology_statistic": "max absolute deviation of the three fitted candidate latent residual correlations from their common mean",
            "practical_equivalence_region": {
                "max_exchangeability_deviation_leq": PRACTICAL_EQUIVALENCE_MAX_DEVIATION,
                "derivation": "outcome-blind power design warned that one-pair increments of 0.10-0.15 are too small for independence claims; a one-pair increment delta=0.15 maps to max deviation 2*delta/3=0.10, so <=0.10 is frozen as practically exchangeable",
                "cannot_be_reestimated_from_hsm_outcomes": True,
            },
            "minimum_joint_prerequisite_eligible_scene_count": MIN_CONFIRMATORY_SCENES,
            "joint_support_rule": "only if scene count >=350, predictive CI lower >0, and full-data candidate topology deviation >0.10; this is a future problem-evidence decision rule, not execution authority",
            "decision_precedence": [
                "underpowered availability -> HOLD",
                "predictive CI upper <=0 -> STOP candidate",
                "topology deviation <=0.10 -> STOP candidate as practically exchangeable",
                "predictive CI lower >0 and topology deviation >0.10 -> candidate problem evidence may pass the frozen rule after all measurement/access gates",
                "otherwise -> HOLD predictive uncertainty",
            ],
            "individual_pair_correlations": "secondary only after the joint rule passes",
            "no_outcome_threshold_retuning": True,
            "no_scene_reclustering": True,
            "no_fold_reassignment": True,
        },
        "synthetic_validation": {
            "scene_count": args.scene_count,
            "exchangeable_null": null,
            "strong_nonexchangeable_alternative": alternative,
            "decision_unit_checks": decision_unit_checks,
        },
        "remaining_blockers": [
            "legitimate gated access to the author-released HSM SceneEval-500 scene bundle",
            "measurement-format/evaluator smoke while preserving raw object-matching/prerequisite state",
            "freeze official GPT-4o evaluator lane versus any separately named local evaluator lane before per-case semantic outcomes",
            "independent second-generator qualification before paper-level transport/generalization",
            "new canonical candidate identity remains unbound until the prior independent REVISE gate and access/measurement gates are satisfied",
        ],
        "does_not_authorize": [
            "HSM gated-dataset access by bypass",
            "SceneEval semantic provider calls",
            "P0",
            "GPU execution",
            "generator admission",
            "Problem Gate",
            "canonical candidate binding",
            "scientific PASS",
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

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "null_decision": null["decision"],
                "null_predictive": null["predictive_uncertainty"],
                "null_topology_deviation": null["full_fit_topology_deviation"],
                "alternative_decision": alternative["decision"],
                "alternative_predictive": alternative["predictive_uncertainty"],
                "alternative_topology_deviation": alternative["full_fit_topology_deviation"],
                "scientific_authority": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
