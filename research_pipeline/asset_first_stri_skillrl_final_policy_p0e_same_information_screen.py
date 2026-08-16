from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
from typing import Any

ARMS = ("A_pristine", "B_displacement_clone", "C_identity_placebo", "D_exact_quotient")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def levenshtein(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def exact_binomial_ge(k: int, n: int) -> float:
    if n <= 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(k, n + 1)) / (2 ** n)


def exact_mcnemar_two_sided(left_only: int, right_only: int) -> float:
    n = left_only + right_only
    if n == 0:
        return 1.0
    k = min(left_only, right_only)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, p)


def compare(values_b: list[float], values_c: list[float], *, higher_is_more_specific: bool = True) -> dict[str, Any]:
    if len(values_b) != len(values_c):
        raise ValueError("paired-length")
    b_gt = sum(b > c for b, c in zip(values_b, values_c))
    c_gt = sum(c > b for b, c in zip(values_b, values_c))
    ties = len(values_b) - b_gt - c_gt
    n = b_gt + c_gt
    # One-sided sign test for the candidate claim that B is stronger than C.
    p_b_gt_c = exact_binomial_ge(b_gt, n)
    return {
        "n": len(values_b),
        "B_mean": sum(values_b) / len(values_b),
        "C_mean": sum(values_c) / len(values_c),
        "B_gt_C": b_gt,
        "C_gt_B": c_gt,
        "ties": ties,
        "one_sided_sign_p_for_B_gt_C": p_b_gt_c,
        "B_dominance_supported_at_0_05": bool(b_gt > c_gt and p_b_gt_c < 0.05),
        "higher_is_more_specific": higher_is_more_specific,
    }


def run(raw: pathlib.Path, diagnosis: pathlib.Path) -> dict[str, Any]:
    rows = [json.loads(x) for x in raw.read_text(encoding="utf-8").splitlines() if x.strip()]
    groups: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row["unit_id"]), {})[str(row["arm"])] = row
    if len(groups) != 24 or any(set(g) != set(ARMS) for g in groups.values()):
        raise ValueError("paired-unit-integrity")

    b_div, c_div = [], []
    b_edit, c_edit = [], []
    b_step, c_step = [], []
    b_early, c_early = [], []
    b_resp, c_resp = [], []
    b_only = c_only = 0
    by_family: dict[str, dict[str, int]] = {}
    for g in groups.values():
        a, b, c = g["A_pristine"], g["B_displacement_clone"], g["C_identity_placebo"]
        aa, ba, ca = list(a["projected_actions"]), list(b["projected_actions"]), list(c["projected_actions"])
        bd = int(a["projected_actions_sha256"] != b["projected_actions_sha256"])
        cd = int(a["projected_actions_sha256"] != c["projected_actions_sha256"])
        b_div.append(float(bd)); c_div.append(float(cd))
        b_only += int(bd == 1 and cd == 0); c_only += int(cd == 1 and bd == 0)
        b_edit.append(levenshtein(aa, ba) / max(1, len(aa), len(ba)))
        c_edit.append(levenshtein(aa, ca) / max(1, len(aa), len(ca)))
        b_step.append(float(abs(int(b["steps"]) - int(a["steps"]))))
        c_step.append(float(abs(int(c["steps"]) - int(a["steps"]))))
        def sensitivity(x: list[str]) -> float:
            n = min(len(aa), len(x))
            fd = next((i + 1 for i in range(n) if aa[i] != x[i]), None)
            if fd is None and len(aa) != len(x):
                fd = n + 1
            return 0.0 if fd is None else 1.0 / fd
        b_early.append(sensitivity(ba)); c_early.append(sensitivity(ca))
        b_resp.append(float(a["response_sha256s"] != b["response_sha256s"]))
        c_resp.append(float(a["response_sha256s"] != c["response_sha256s"]))
        f = str(a["task_family"])
        by_family.setdefault(f, {"units": 0, "B_action_diff": 0, "C_action_diff": 0})
        by_family[f]["units"] += 1
        by_family[f]["B_action_diff"] += bd
        by_family[f]["C_action_diff"] += cd

    action = compare(b_div, c_div)
    action["B_only_disagreement"] = b_only
    action["C_only_disagreement"] = c_only
    action["paired_mcnemar_two_sided_p"] = exact_mcnemar_two_sided(b_only, c_only)
    metrics = {
        "action_sequence_disagreement_indicator": action,
        "normalized_action_levenshtein_distance_from_A": compare(b_edit, c_edit),
        "absolute_step_count_delta_from_A": compare(b_step, c_step),
        "early_action_divergence_sensitivity_1_over_step": compare(b_early, c_early),
        "response_sequence_disagreement_indicator": compare(b_resp, c_resp),
    }
    any_b_dominance = any(v.get("B_dominance_supported_at_0_05") is True for v in metrics.values())
    diag = json.loads(diagnosis.read_text(encoding="utf-8"))
    if diag.get("disposition") != "QUALIFIED_TRUE_NEGATIVE_ENDPOINT_BRIDGE":
        raise ValueError("diagnosis-disposition")
    return {
        "schema_version": "1.0",
        "artifact_kind": "post-negative-same-information-reduction-screen",
        "experiment_id": diag.get("experiment_id"),
        "input_raw_path": str(raw),
        "input_raw_sha256": sha(raw),
        "diagnosis_path": str(diagnosis),
        "diagnosis_sha256": sha(diagnosis),
        "screen_role": "Post-negative reduction only. Not preregistered evidence and cannot rescue C4 or authorize a new paper claim.",
        "candidate_claim_screened": "Semantic displacement B has trajectory-level specificity beyond the same-information identity placebo C despite terminal endpoint equivalence.",
        "metrics": metrics,
        "by_family": dict(sorted(by_family.items())),
        "any_simple_B_over_C_dominance_supported": any_b_dominance,
        "verdict": "NO_SEMANTIC_SPECIFIC_TRAJECTORY_RESIDUAL_IN_SIMPLE_SAME_INFORMATION_SCREEN" if not any_b_dominance else "RESIDUAL_REQUIRES_PREDECLARED_NEW_CONTRACT",
        "interpretation": "Failure of B to dominate C on these simple paired trajectory summaries supports reduction to generic identity/order/prompt sensitivity. This is a screening result, not proof of equivalence.",
        "new_gpu_authorized": False,
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    ap.add_argument("--diagnosis", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = run(a.raw, a.diagnosis)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
