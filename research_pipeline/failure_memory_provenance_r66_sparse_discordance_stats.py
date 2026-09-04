#!/usr/bin/env python3
"""Conservative sparse-discordance inference for B1 R66 manuscript repair.

This is a post-confirmatory statistical audit only. It does not change the frozen
R56/R61 analyses or open scientific execution authority.

For paired binary outcomes, let p10=P(B=1,A=0) and p01=P(B=0,A=1), so the
paired risk difference is delta=p10-p01. We construct separate exact
Clopper-Pearson intervals for p10 and p01 at 97.5% marginal coverage and combine
them by Bonferroni. The resulting interval

    [L10-U01, U10-L01]

has at least 95% simultaneous coverage. It is deliberately conservative and is
used only to check whether the preregistered +/-15pp relevance margin is
actually excluded under sparse discordance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
MARGIN = 0.15
JOINT_COVERAGE = 0.95
MARGINAL_COVERAGE = 0.975


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected-object:{path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def binom_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, j) * (p ** j) * ((1.0 - p) ** (n - j)) for j in range(k + 1))


def bisect_decreasing(target: float, fn, *, iterations: int = 100) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        if fn(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def clopper_pearson(k: int, n: int, coverage: float = MARGINAL_COVERAGE) -> tuple[float, float]:
    if not 0 <= k <= n:
        raise ValueError("invalid-binomial-count")
    alpha = 1.0 - coverage
    tail = alpha / 2.0
    if k == 0:
        lower = 0.0
    else:
        # P_p(X <= k-1) = 1-tail
        lower = bisect_decreasing(1.0 - tail, lambda p: binom_cdf(k - 1, n, p))
    if k == n:
        upper = 1.0
    else:
        # P_p(X <= k) = tail
        upper = bisect_decreasing(tail, lambda p: binom_cdf(k, n, p))
    return lower, upper


def model_audit(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    n = int(payload.get("units") or 0)
    b_only = int(payload.get("B_only_success") or 0)
    a_only = int(payload.get("A_only_success") or 0)
    if n != 32 or b_only + a_only != int(payload.get("discordant_pairs") or 0):
        raise RuntimeError(f"unexpected-{name}-paired-counts")
    b_lo, b_hi = clopper_pearson(b_only, n)
    a_lo, a_hi = clopper_pearson(a_only, n)
    d_lo, d_hi = b_lo - a_hi, b_hi - a_lo
    observed = float(payload.get("effect") or 0.0)
    return {
        "model": name,
        "n_pairs": n,
        "B_only_success": b_only,
        "A_only_success": a_only,
        "discordant_pairs": b_only + a_only,
        "observed_paired_risk_difference": observed,
        "preregistered_bootstrap_ci95": payload.get("ci95_paired_cluster_bootstrap"),
        "exact_two_sided_signflip_p": payload.get("exact_two_sided_signflip_p"),
        "bonferroni_component_coverage": MARGINAL_COVERAGE,
        "p_B_only_clopper_pearson": [b_lo, b_hi],
        "p_A_only_clopper_pearson": [a_lo, a_hi],
        "conservative_paired_risk_difference_ci95": [d_lo, d_hi],
        "preregistered_margin_abs": MARGIN,
        "positive_15pp_effect_excluded": d_hi < MARGIN,
        "negative_15pp_effect_excluded": d_lo > -MARGIN,
        "plus_minus_15pp_equivalence_established": d_lo > -MARGIN and d_hi < MARGIN,
        "observed_effect_reaches_preregistered_margin": abs(observed) >= MARGIN,
    }


def build(qwen_path: Path, llama_path: Path) -> dict[str, Any]:
    qwen, llama = load(qwen_path), load(llama_path)
    if qwen.get("paper_id") != PAPER_ID or llama.get("paper_id") != PAPER_ID:
        raise RuntimeError("paper-id-drift")
    models = [
        model_audit("Qwen2.5-7B-Instruct", qwen),
        model_audit("Meta-Llama-3.1-8B-Instruct", llama),
    ]
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R66-SPARSE-DISCORDANCE-STATISTICAL-AUDIT",
        "recorded_date": "2026-09-03",
        "status": "POSTCONFIRMATORY_STATISTICAL_REPAIR_NO_NEW_EXECUTION",
        "role": "MANUSCRIPT_ONLY_CONSERVATIVE_PAIRED_RISK_DIFFERENCE_AUDIT",
        "inputs": {
            "qwen_path": str(qwen_path),
            "qwen_file_sha256": sha(qwen_path),
            "qwen_receipt_sha256": qwen.get("receipt_sha256"),
            "llama_path": str(llama_path),
            "llama_file_sha256": sha(llama_path),
            "llama_receipt_sha256": llama.get("receipt_sha256"),
        },
        "method": {
            "estimand": "p(B_success,A_fail)-p(A_success,B_fail)",
            "paired_binary_categories": True,
            "component_intervals": "two-sided exact Clopper-Pearson",
            "component_coverage_each": MARGINAL_COVERAGE,
            "joint_coverage_lower_bound": JOINT_COVERAGE,
            "combination": "Bonferroni: [L_Bonly-U_Aonly, U_Bonly-L_Aonly]",
            "purpose": "conservative sparse-discordance check of whether +/-15pp is excluded; does not replace preregistered analysis",
        },
        "models": models,
        "adjudication": {
            "preregistered_15pp_margin_changed": False,
            "preregistered_bootstrap_changed": False,
            "new_agent_execution": False,
            "new_provider_calls": 0,
            "population_plus_15pp_excluded_for_both_models": all(x["positive_15pp_effect_excluded"] for x in models),
            "plus_minus_15pp_equivalence_established_for_both_models": all(x["plus_minus_15pp_equivalence_established"] for x in models),
            "required_manuscript_wording": "Observed paired effects did not reach the preregistered 15pp threshold; sparse-discordance conservative intervals do not establish +/-15pp equivalence or rule out a +15pp population effect.",
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["receipt_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen", type=Path, default=Path("generated/d2-failure-memory-provenance-r56-qwen-ab-identification-result.json"))
    parser.add_argument("--llama", type=Path, default=Path("generated/d2-failure-memory-provenance-r61-llama-ab-identification-result.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.qwen, args.llama)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
