#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def digest_without_receipt(obj: dict) -> str:
    payload = {k: v for k, v in obj.items() if k != "receipt_sha256"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def exact_two_sided_sign(b_only: int, a_only: int) -> float:
    m = b_only + a_only
    if m == 0:
        return 1.0
    lo = min(b_only, a_only)
    tail = sum(math.comb(m, k) for k in range(lo + 1)) / (2 ** m)
    return min(1.0, 2.0 * tail)


def percentile_ci(effects: list[int], seed: int, reps: int) -> list[float]:
    rng = random.Random(seed)
    n = len(effects)
    vals = [sum(effects[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    vals.sort()
    lo = vals[math.floor(0.025 * (reps - 1))]
    hi = vals[math.ceil(0.975 * (reps - 1))]
    return [float(lo), float(hi)]


def recompute_ab(name: str) -> dict:
    obj = load(name)
    assert digest_without_receipt(obj) == obj["receipt_sha256"], f"receipt hash mismatch: {name}"
    rows = obj["unit_rows"]
    assert len(rows) == 32
    effects = [int(r["B_terminal_success"]) - int(r["A_terminal_success"]) for r in rows]
    b_only = sum(r["B_terminal_success"] and not r["A_terminal_success"] for r in rows)
    a_only = sum(r["A_terminal_success"] and not r["B_terminal_success"] for r in rows)
    effect = sum(effects) / len(effects)
    p = exact_two_sided_sign(b_only, a_only)
    ci = percentile_ci(effects, int(obj["bootstrap_seed"]), int(obj["bootstrap_repetitions"]))
    assert effect == obj["effect"]
    assert b_only == obj["B_only_success"] and a_only == obj["A_only_success"]
    assert p == obj["exact_two_sided_signflip_p"]
    assert ci == obj["ci95_paired_cluster_bootstrap"]
    return {
        "effect": effect,
        "B_only_success": b_only,
        "A_only_success": a_only,
        "discordant_pairs": b_only + a_only,
        "exact_two_sided_signflip_p": p,
        "ci95_paired_cluster_bootstrap": ci,
        "effect_relevance_floor_abs": obj["effect_relevance_floor_abs"],
        "effect_relevance_floor_met": abs(effect) >= float(obj["effect_relevance_floor_abs"]),
    }


def main() -> None:
    qwen = recompute_ab("qwen_ab.json")
    llama = recompute_ab("llama_ab.json")
    q_util = load("qwen_utilization.json")
    l_util = load("llama_utilization.json")
    for name, obj in [("qwen_utilization.json", q_util), ("llama_utilization.json", l_util)]:
        assert digest_without_receipt(obj) == obj["receipt_sha256"], f"receipt hash mismatch: {name}"
        assert obj["pass"] is True
    out = {
        "Qwen2.5-7B-Instruct": qwen,
        "Meta-Llama-3.1-8B-Instruct": llama,
        "Qwen_utilization": {
            "u1_specific": q_util["u1_specific_first_action_units"],
            "placebo_u2_vs_u0": q_util["u2_vs_u0_divergence_units"],
        },
        "Llama_utilization": {
            "u1_specific": l_util["u1_specific_first_action_units"],
            "placebo_u2_vs_u0": l_util["u2_vs_u0_divergence_units"],
        },
        "cross_model_pooling_performed": False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
