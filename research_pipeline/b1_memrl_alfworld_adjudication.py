from __future__ import annotations

import math
import json
from pathlib import Path
from typing import Any

from .b1_memrl_alfworld_target_plan import PAPER_ID, content_hash, load, now


def _binom_two_sided_p(wins: int, total: int) -> float:
    if total <= 0:
        return 1.0
    probs = [math.comb(total, k) / (2 ** total) for k in range(total + 1)]
    observed = probs[wins]
    return min(1.0, sum(p for p in probs if p <= observed + 1e-15))


def _betacf(a: float, b: float, x: float) -> float:
    eps, fmin = 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0; d = 1.0 - qab * x / qap; d = fmin if abs(d) < fmin else d; d = 1.0 / d; h = d
    for m in range(1, 301):
        m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = fmin if abs(d) < fmin else d; c = 1.0 + aa / c; c = fmin if abs(c) < fmin else c; d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2)); d = 1.0 + aa * d; d = fmin if abs(d) < fmin else d
        c = 1.0 + aa / c; c = fmin if abs(c) < fmin else c; d = 1.0 / d; delta = d * c; h *= delta
        if abs(delta - 1.0) < eps: break
    return h


def _betai(a: float, b: float, x: float) -> float:
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    return bt * _betacf(a, b, x) / a if x < (a + 1.0) / (a + b + 2.0) else 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _beta_ppf(q: float, a: float, b: float) -> float:
    if q <= 0.0: return 0.0
    if q >= 1.0: return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(120):
        mid = (lo + hi) / 2.0
        if _betai(a, b, mid) < q: lo = mid
        else: hi = mid
    return (lo + hi) / 2.0


def _clopper_pearson(successes: int, total: int, alpha: float = 0.05) -> list[float]:
    if total <= 0: return [0.0, 1.0]
    lo = 0.0 if successes == 0 else _beta_ppf(alpha / 2.0, successes, total - successes + 1)
    hi = 1.0 if successes == total else _beta_ppf(1.0 - alpha / 2.0, successes + 1, total - successes)
    return [lo, hi]


def adjudicate_confirmatory(*, preflight_path: Path, plan_path: Path, output_dir: Path) -> dict[str, Any]:
    preflight, plan = load(preflight_path), load(plan_path)
    collected = load(output_dir / "confirmatory-summary.json")
    if collected.get("status") != "CONFIRMATORY_COLLECTED": raise RuntimeError("confirmatory data are not complete/valid")
    if collected.get("plan_sha256") != plan.get("plan_sha256") or plan.get("preflight_manifest_sha256") != preflight.get("manifest_sha256"):
        raise RuntimeError("confirmatory provenance chain drift")
    targets = list(collected.get("targets") or []); n = int((preflight.get("statistics") or {}).get("confirmatory_n") or 0)
    if len(targets) != n: raise RuntimeError("confirmatory independent-unit count drift")

    success = lambda row, arm: int((row.get("terminal_success") or {}).get(arm) or 0)
    a2 = [success(row, "A2_TRUTHFUL_VISIBLE_PROVENANCE") for row in targets]
    a5 = [success(row, "A5_FLIPPED_VISIBLE_PROVENANCE") for row in targets]
    wins = sum(x == 1 and y == 0 for x, y in zip(a2, a5)); losses = sum(x == 0 and y == 1 for x, y in zip(a2, a5)); discordant = wins + losses
    effect = sum(x - y for x, y in zip(a2, a5)) / n
    def mean_diff(left: str, right: str) -> float: return sum(success(row, left) - success(row, right) for row in targets) / n
    first_truth_flip = sum(str((row.get("first_action") or {}).get("A2_TRUTHFUL_VISIBLE_PROVENANCE") or "") != str((row.get("first_action") or {}).get("A5_FLIPPED_VISIBLE_PROVENANCE") or "") for row in targets) / n
    first_memory = sum(any(bool(v) for v in (row.get("first_action_changed_vs_A0") or {}).values()) for row in targets) / n

    result: dict[str, Any] = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "status": "CONFIRMATORY_ADJUDICATED", "generated_at": now(),
        "preflight_manifest_sha256": preflight.get("manifest_sha256"), "plan_sha256": plan.get("plan_sha256"), "confirmatory_receipt_sha256": collected.get("receipt_sha256"),
        "independent_unit": (preflight.get("statistics") or {}).get("independent_unit"), "n": n,
        "primary": {"estimand": (preflight.get("estimands") or {}).get("primary"), "truthful_visible_successes": sum(a2), "flipped_visible_successes": sum(a5),
            "paired_mean_terminal_success_difference_A2_minus_A5": effect, "discordant_truthful_wins": wins, "discordant_flipped_wins": losses,
            "ties": n - discordant, "discordant_total": discordant, "exact_two_sided_sign_test_p": _binom_two_sided_p(wins, discordant),
            "exact_95pct_clopper_pearson_interval_for_truthful_win_probability_among_discordant": _clopper_pearson(wins, discordant),
            "interpretation_boundary": "The exact interval conditions on discordant targets and is not an interval for the paired mean effect. No effect-size or p-value promotion threshold was added post hoc."},
        "secondary": {"memory_marginal_utility_A1_minus_A0": mean_diff("A1_CONTENT_ONLY", "A0_NO_MEMORY"),
            "visible_provenance_increment_A2_minus_A1": mean_diff("A2_TRUTHFUL_VISIBLE_PROVENANCE", "A1_CONTENT_ONLY"),
            "first_action_truthful_vs_flipped_change_rate": first_truth_flip, "first_action_any_memory_vs_no_memory_change_rate": first_memory,
            "source_provenance_assignment_counts": {"success": sum(row.get("true_provenance") == "success" for row in targets), "failure": sum(row.get("true_provenance") == "failure" for row in targets)},
            "no_channel_negative_control_failures": int(collected.get("no_channel_negative_control_failures") or 0)},
        "reporting": {"all_confirmatory_targets_reported": len(targets) == n, "all_five_arms_reported": True, "pilot_targets_excluded": True,
            "historical_webarena_units_pooled": False, "requests_or_model_calls_treated_as_independent_n": False, "no_optional_stopping_on_effect_size": True},
        "scientific_authority": False, "submission_authority": False,
    }
    result["receipt_sha256"] = content_hash(result, exclude={"generated_at", "receipt_sha256"})
    (output_dir / "confirmatory-adjudication.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
