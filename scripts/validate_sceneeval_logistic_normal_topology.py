from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import minimize
from scipy.special import expit, gammaln, logsumexp

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "generated" / "sceneeval500-prerequisite-coupling-preregistration-draft-20260828.json"
EXPECTED_PREREG_SHA = "269412b2b0ac270de00d1cca60f4e429ca3b48aae5d62359be073a6095abc365"
CHANNELS = ("ObjAttr", "OORel", "OARel")
FINAL_QUADRATURE_ORDER = 7
FIT_MAXITER = 220


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = hermgauss(order)
    meshes = np.meshgrid(nodes, nodes, nodes, indexing="ij")
    grid = np.stack(meshes, axis=-1).reshape(-1, 3) * math.sqrt(2.0)
    wmeshes = np.meshgrid(weights, weights, weights, indexing="ij")
    product_weights = (wmeshes[0] * wmeshes[1] * wmeshes[2]).reshape(-1)
    log_weights = np.log(product_weights) - 1.5 * math.log(math.pi)
    return grid, log_weights


def _rho_from_raw(raw: float) -> float:
    # An exchangeable 3x3 correlation matrix is positive definite for -1/2 < rho < 1.
    return -0.5 + 1.5 * float(expit(raw))


def _raw_from_rho(rho: float) -> float:
    if not -0.5 < rho < 1.0:
        raise ValueError("exchangeable rho outside (-0.5, 1)")
    unit = (rho + 0.5) / 1.5
    return math.log(unit / (1.0 - unit))


def covariance_n2(params: np.ndarray) -> tuple[np.ndarray, float]:
    if len(params) != 4:
        raise ValueError("N2 requires three log-scales and one exchangeable-correlation parameter")
    scales = np.exp(params[:3])
    rho = _rho_from_raw(float(params[3]))
    correlation = np.full((3, 3), rho, dtype=float)
    np.fill_diagonal(correlation, 1.0)
    covariance = np.diag(scales) @ correlation @ np.diag(scales)
    return covariance, rho


def covariance_candidate(params: np.ndarray) -> np.ndarray:
    if len(params) != 6:
        raise ValueError("candidate requires six Cholesky parameters")
    lower = np.array(
        [
            [math.exp(float(params[0])), 0.0, 0.0],
            [float(params[1]), math.exp(float(params[2])), 0.0],
            [float(params[3]), float(params[4]), math.exp(float(params[5]))],
        ],
        dtype=float,
    )
    return lower @ lower.T


def candidate_params_from_covariance(covariance: np.ndarray) -> np.ndarray:
    lower = np.linalg.cholesky(covariance)
    return np.array(
        [
            math.log(float(lower[0, 0])),
            float(lower[1, 0]),
            math.log(float(lower[1, 1])),
            float(lower[2, 0]),
            float(lower[2, 1]),
            math.log(float(lower[2, 2])),
        ],
        dtype=float,
    )


def correlation_from_covariance(covariance: np.ndarray) -> np.ndarray:
    scales = np.sqrt(np.diag(covariance))
    return covariance / np.outer(scales, scales)


def binomial_logistic_normal_loglik(
    y: np.ndarray,
    n: np.ndarray,
    eta: np.ndarray,
    covariance: np.ndarray,
    *,
    order: int = FINAL_QUADRATURE_ORDER,
) -> float:
    if y.shape != n.shape or y.shape != eta.shape or y.ndim != 2 or y.shape[1] != 3:
        raise ValueError("y, n, eta must all have shape [scene, 3]")
    if np.any(y < 0) or np.any(n < 0) or np.any(y > n):
        raise ValueError("invalid binomial counts")
    np.linalg.cholesky(covariance)  # fail closed before quadrature
    grid, log_weights = quadrature(order)
    lower = np.linalg.cholesky(covariance)
    random_effects = grid @ lower.T  # [quadrature, channel]
    logits = eta[:, None, :] + random_effects[None, :, :]
    log_coeff = (gammaln(n + 1) - gammaln(y + 1) - gammaln(n - y + 1))[:, None, :]
    success_logprob = -np.logaddexp(0.0, -logits)
    failure_logprob = -np.logaddexp(0.0, logits)
    conditional = log_coeff + y[:, None, :] * success_logprob + (n - y)[:, None, :] * failure_logprob
    per_scene = logsumexp(log_weights[None, :] + conditional.sum(axis=2), axis=1)
    return float(per_scene.sum())


def fit_n2(y: np.ndarray, n: np.ndarray, eta: np.ndarray) -> dict[str, Any]:
    initial = np.array([math.log(0.8)] * 3 + [_raw_from_rho(0.20)], dtype=float)
    bounds = [(-3.0, 2.0), (-3.0, 2.0), (-3.0, 2.0), (-6.0, 6.0)]
    result = minimize(
        lambda params: -binomial_logistic_normal_loglik(y, n, eta, covariance_n2(params)[0]),
        initial,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": FIT_MAXITER, "ftol": 1e-9},
    )
    covariance, rho = covariance_n2(result.x)
    return {
        "success": bool(result.success),
        "message": str(result.message),
        "iterations": int(result.nit),
        "log_likelihood": float(-result.fun),
        "params": result.x,
        "covariance": covariance,
        "correlation": correlation_from_covariance(covariance),
        "exchangeable_rho": rho,
    }


def fit_candidate(y: np.ndarray, n: np.ndarray, eta: np.ndarray, initial_covariance: np.ndarray) -> dict[str, Any]:
    initial = candidate_params_from_covariance(initial_covariance)
    bounds = [(-3.0, 2.0), (-3.0, 3.0), (-3.0, 2.0), (-3.0, 3.0), (-3.0, 3.0), (-3.0, 2.0)]
    result = minimize(
        lambda params: -binomial_logistic_normal_loglik(y, n, eta, covariance_candidate(params)),
        initial,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": FIT_MAXITER, "ftol": 1e-9},
    )
    covariance = covariance_candidate(result.x)
    return {
        "success": bool(result.success),
        "message": str(result.message),
        "iterations": int(result.nit),
        "log_likelihood": float(-result.fun),
        "params": result.x,
        "covariance": covariance,
        "correlation": correlation_from_covariance(covariance),
    }


def make_covariance(scales: tuple[float, float, float], correlations: tuple[float, float, float]) -> np.ndarray:
    correlation = np.eye(3, dtype=float)
    correlation[0, 1] = correlation[1, 0] = correlations[0]
    correlation[0, 2] = correlation[2, 0] = correlations[1]
    correlation[1, 2] = correlation[2, 1] = correlations[2]
    covariance = np.diag(scales) @ correlation @ np.diag(scales)
    np.linalg.cholesky(covariance)
    return covariance


def simulate_dataset(scene_count: int, covariance: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    covariate = rng.normal(size=scene_count)
    eta = np.stack(
        [
            -1.00 + 0.25 * covariate,
            -0.80 - 0.15 * covariate,
            -1.10 + 0.10 * covariate,
        ],
        axis=1,
    )
    n = rng.integers(6, 13, size=(scene_count, 3))
    random_effects = rng.multivariate_normal(np.zeros(3), covariance, size=scene_count)
    probabilities = expit(eta + random_effects)
    y = rng.binomial(n, probabilities)
    return y.astype(float), n.astype(float), eta.astype(float)


def pair_correlations(correlation: np.ndarray) -> list[float]:
    return [float(correlation[0, 1]), float(correlation[0, 2]), float(correlation[1, 2])]


def max_exchangeability_deviation(correlation: np.ndarray) -> float:
    values = pair_correlations(correlation)
    mean = sum(values) / 3.0
    return max(abs(value - mean) for value in values)


def fit_and_score_scenario(
    *,
    name: str,
    true_covariance: np.ndarray,
    seed: int,
    train_count: int = 800,
    test_count: int = 400,
) -> dict[str, Any]:
    y, n, eta = simulate_dataset(train_count + test_count, true_covariance, seed)
    y_train, y_test = y[:train_count], y[train_count:]
    n_train, n_test = n[:train_count], n[train_count:]
    eta_train, eta_test = eta[:train_count], eta[train_count:]
    n2 = fit_n2(y_train, n_train, eta_train)
    if not n2["success"]:
        raise SystemExit(f"N2 synthetic fit failed for {name}: {n2['message']}")
    candidate = fit_candidate(y_train, n_train, eta_train, n2["covariance"])
    if not candidate["success"]:
        raise SystemExit(f"candidate synthetic fit failed for {name}: {candidate['message']}")
    n2_test = binomial_logistic_normal_loglik(y_test, n_test, eta_test, n2["covariance"])
    candidate_test = binomial_logistic_normal_loglik(y_test, n_test, eta_test, candidate["covariance"])
    # Quadrature stability is evaluated at frozen fitted covariances, not used for model selection.
    candidate_test_q9 = binomial_logistic_normal_loglik(y_test, n_test, eta_test, candidate["covariance"], order=9)
    return {
        "name": name,
        "seed": seed,
        "train_scene_count": train_count,
        "test_scene_count": test_count,
        "true_correlation": np.round(correlation_from_covariance(true_covariance), 6).tolist(),
        "n2": {
            "success": n2["success"],
            "iterations": n2["iterations"],
            "train_log_likelihood": round(n2["log_likelihood"], 6),
            "test_log_likelihood_q7": round(n2_test, 6),
            "exchangeable_rho": round(float(n2["exchangeable_rho"]), 6),
            "fitted_correlation": np.round(n2["correlation"], 6).tolist(),
        },
        "candidate": {
            "success": candidate["success"],
            "iterations": candidate["iterations"],
            "train_log_likelihood": round(candidate["log_likelihood"], 6),
            "test_log_likelihood_q7": round(candidate_test, 6),
            "test_log_likelihood_q9": round(candidate_test_q9, 6),
            "q7_q9_per_test_scene_difference": round(abs(candidate_test - candidate_test_q9) / test_count, 8),
            "fitted_correlation": np.round(candidate["correlation"], 6).tolist(),
            "max_exchangeability_deviation": round(max_exchangeability_deviation(candidate["correlation"]), 6),
        },
        "heldout_candidate_minus_n2_log_likelihood": round(candidate_test - n2_test, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sha256_file(PREREG) != EXPECTED_PREREG_SHA:
        raise SystemExit("preregistration draft digest drifted")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    nesting = prereg["nested_model_contract"]["nesting"]
    if "exactly two nonexchangeability degrees of freedom" not in nesting:
        raise SystemExit("preregistration no longer binds the 2-df topology test")

    true_null = make_covariance((1.0, 0.9, 1.1), (0.30, 0.30, 0.30))
    true_alt = make_covariance((1.0, 0.9, 1.1), (0.65, 0.05, 0.05))

    # Exact nesting check: candidate and N2 must produce identical likelihood at the same covariance.
    nested_params = np.array([math.log(1.0), math.log(0.9), math.log(1.1), _raw_from_rho(0.30)], dtype=float)
    nested_covariance, _ = covariance_n2(nested_params)
    candidate_nested_covariance = covariance_candidate(candidate_params_from_covariance(nested_covariance))
    y_nested, n_nested, eta_nested = simulate_dataset(40, nested_covariance, 2026082801)
    nested_n2_ll = binomial_logistic_normal_loglik(y_nested, n_nested, eta_nested, nested_covariance)
    nested_candidate_ll = binomial_logistic_normal_loglik(y_nested, n_nested, eta_nested, candidate_nested_covariance)
    nesting_error = abs(nested_n2_ll - nested_candidate_ll)
    if nesting_error > 1e-9:
        raise SystemExit(f"candidate/N2 nesting likelihood mismatch: {nesting_error}")

    null_scenario = fit_and_score_scenario(name="exchangeable_null", true_covariance=true_null, seed=2026082802)
    alt_scenario = fit_and_score_scenario(name="nonexchangeable_alternative", true_covariance=true_alt, seed=2026082803)

    null_dev = null_scenario["candidate"]["max_exchangeability_deviation"]
    alt_dev = alt_scenario["candidate"]["max_exchangeability_deviation"]
    null_heldout = null_scenario["heldout_candidate_minus_n2_log_likelihood"]
    alt_heldout = alt_scenario["heldout_candidate_minus_n2_log_likelihood"]
    if null_dev >= 0.08:
        raise SystemExit(f"null synthetic fit spuriously nonexchangeable: {null_dev}")
    if null_heldout >= 1.5:
        raise SystemExit(f"candidate spuriously improves heldout null likelihood: {null_heldout}")
    if alt_dev <= 0.20:
        raise SystemExit(f"alternative synthetic topology not recovered: {alt_dev}")
    if alt_heldout <= 5.0:
        raise SystemExit(f"candidate failed to improve heldout alternative likelihood: {alt_heldout}")
    if alt_scenario["candidate"]["q7_q9_per_test_scene_difference"] >= 0.005:
        raise SystemExit("Gauss-Hermite q7/q9 heldout score drift exceeds frozen tolerance")

    artifact = {
        "schema_version": "sceneeval-logistic-normal-topology-implementation-preflight-v1",
        "status": "CORE_TOPOLOGY_LIKELIHOOD_SYNTHETIC_PASS",
        "preregistration_artifact": str(PREREG.relative_to(ROOT)),
        "preregistration_sha256": EXPECTED_PREREG_SHA,
        "scientific_authority": False,
        "execution_authority": False,
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
        "implementation_contract": {
            "likelihood": "three-channel binomial logistic-normal marginal likelihood integrated with tensor-product Gauss-Hermite quadrature",
            "quadrature_order": FINAL_QUADRATURE_ORDER,
            "N2_parameter_count_for_covariance": 4,
            "candidate_parameter_count_for_covariance": 6,
            "candidate_minus_N2_degrees_of_freedom": 2,
            "N2_covariance": "channel-specific positive scales plus one exchangeable correlation rho in (-0.5,1)",
            "candidate_covariance": "unrestricted SPD 3x3 covariance through lower-Cholesky parameterization",
            "nested_subspace": "candidate pair correlations all equal",
            "fixed_effect_interface": "eta[scene,channel] is supplied as a frozen marginal offset; marginal metadata-calibration implementation remains a separate prerequisite gate",
        },
        "synthetic_validation": {
            "exact_nesting_loglik_absolute_error": nesting_error,
            "exchangeable_null": null_scenario,
            "nonexchangeable_alternative": alt_scenario,
            "acceptance_rules": {
                "nesting_error_max": 1e-9,
                "null_candidate_max_exchangeability_deviation_max": 0.08,
                "null_heldout_candidate_improvement_max": 1.5,
                "alternative_candidate_exchangeability_deviation_min": 0.20,
                "alternative_heldout_candidate_improvement_min": 5.0,
                "candidate_q7_q9_per_scene_score_difference_max": 0.005,
            },
        },
        "remaining_implementation_blockers": [
            "freeze and synthetic-test the high-dimensional same-information marginal metadata calibration that produces eta offsets inside each training fold",
            "freeze the scene-level bootstrap/uncertainty and practical-equivalence implementation",
            "run a measurement-format smoke only after legitimate HSM content access; synthetic topology PASS is not evaluator PASS",
        ],
        "does_not_authorize": [
            "HSM gated-dataset access",
            "SceneEval semantic provider calls",
            "P0",
            "GPU execution",
            "generator admission",
            "Problem Gate",
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
    print(json.dumps({
        "status": artifact["status"],
        "nesting_error": nesting_error,
        "null_heldout_delta": null_heldout,
        "null_topology_deviation": null_dev,
        "alternative_heldout_delta": alt_heldout,
        "alternative_topology_deviation": alt_dev,
        "q7_q9_per_scene_difference": alt_scenario["candidate"]["q7_q9_per_test_scene_difference"],
        "scientific_authority": False,
    }, indent=2))


if __name__ == "__main__":
    main()
