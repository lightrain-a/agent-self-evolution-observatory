from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-CONFIRMATORY-PREEXEC-FREEZE-20260904"
PANEL_ORDER_SALT = "ACE-CONFIRMATORY-PANEL-ORDER-20260904-V1"
ARMS = ("INDEPENDENT", "LOW", "HIGH")
BRANCHES = ("NO_UPDATE", "REAL_REPAIR")
DEV_FAMILY_COUNT = 6
R2_STABILITY_MAX = 0.10
R3_STABILITY_MAX = 0.20
TO_V_UPTAKE_MIN = 0.50
N_CANDIDATES = (12, 16, 20, 24)
PLANNING_SE_MAX = 0.10
PLANNING_MEANINGFUL_EFFECT = 0.20


class PreexecError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_crr(value: Any) -> float:
    x = float(value)
    if not 0.0 <= x <= 1.0:
        raise PreexecError(f"CRR outside [0,1]: {x}")
    return x


def _index_repeat_rows(rows: Iterable[dict[str, Any]], repeats: tuple[int, ...]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    rows = list(rows)
    families = sorted({str(row["family_id"]) for row in rows})
    if len(families) != DEV_FAMILY_COUNT:
        raise PreexecError(f"repeat qualification requires exactly {DEV_FAMILY_COUNT} development families")
    index: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["family_id"]), str(row["arm"]), str(row["branch"]), int(row["repeat"]))
        if key in index:
            raise PreexecError(f"duplicate repeat row: {key}")
        if key[1] not in ARMS or key[2] not in BRANCHES or key[3] not in repeats:
            raise PreexecError(f"row outside frozen repeat design: {key}")
        _validate_crr(row["crr"])
        if not isinstance(row.get("target_success"), bool):
            raise PreexecError(f"target_success must be bool: {key}")
        if not isinstance(row.get("valid"), bool):
            raise PreexecError(f"valid must be bool: {key}")
        index[key] = row
    expected = {
        (family, arm, branch, repeat)
        for family in families
        for arm in ARMS
        for branch in BRANCHES
        for repeat in repeats
    }
    if set(index) != expected:
        missing = sorted(expected - set(index))
        extra = sorted(set(index) - expected)
        raise PreexecError(f"repeat matrix mismatch missing={missing[:3]} extra={extra[:3]}")
    return index


def decide_repeat_count_after_two(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Use only within-condition repeat disagreement; never compute treatment direction."""
    index = _index_repeat_rows(rows, (1, 2))
    if any(not bool(row["valid"]) for row in index.values()):
        return {
            "status": "REPEAT_QUALIFICATION_INVALID_TECHNICAL_UNIT",
            "R_star": None,
            "third_development_repeat_required": False,
        }
    cells = sorted({key[:3] for key in index})
    target_disagreement = 0
    crr_abs_diffs: list[float] = []
    for family, arm, branch in cells:
        left = index[(family, arm, branch, 1)]
        right = index[(family, arm, branch, 2)]
        target_disagreement += int(bool(left["target_success"]) != bool(right["target_success"]))
        crr_abs_diffs.append(abs(_validate_crr(left["crr"]) - _validate_crr(right["crr"])))
    target_rate = target_disagreement / len(cells)
    crr_mad = sum(crr_abs_diffs) / len(crr_abs_diffs)
    metrics = {
        "condition_cell_count": len(cells),
        "target_disagreement_rate": target_rate,
        "mean_absolute_crr_repeat_difference": crr_mad,
    }
    if target_rate <= R2_STABILITY_MAX and crr_mad <= R2_STABILITY_MAX:
        return {"status": "REPEAT_QUALIFICATION_PASS_R2", "R_star": 2, "third_development_repeat_required": False, **metrics}
    if target_rate <= R3_STABILITY_MAX and crr_mad <= R3_STABILITY_MAX:
        return {"status": "REPEAT_QUALIFICATION_REQUIRE_R3", "R_star": None, "third_development_repeat_required": True, **metrics}
    return {"status": "REPEAT_QUALIFICATION_STOP_STOCHASTICITY_TOO_HIGH", "R_star": None, "third_development_repeat_required": False, **metrics}


def decide_repeat_count_after_three(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Confirm that adding one repeat is enough; never authorize R>3."""
    index = _index_repeat_rows(rows, (1, 2, 3))
    if any(not bool(row["valid"]) for row in index.values()):
        return {"status": "REPEAT_QUALIFICATION_INVALID_TECHNICAL_UNIT", "R_star": None}
    cells = sorted({key[:3] for key in index})
    nonunanimous_target = 0
    crr_ranges: list[float] = []
    for family, arm, branch in cells:
        triple = [index[(family, arm, branch, repeat)] for repeat in (1, 2, 3)]
        targets = {bool(row["target_success"]) for row in triple}
        nonunanimous_target += int(len(targets) > 1)
        crrs = [_validate_crr(row["crr"]) for row in triple]
        crr_ranges.append(max(crrs) - min(crrs))
    target_rate = nonunanimous_target / len(cells)
    mean_range = sum(crr_ranges) / len(crr_ranges)
    metrics = {
        "condition_cell_count": len(cells),
        "target_nonunanimous_rate": target_rate,
        "mean_crr_three_repeat_range": mean_range,
    }
    if target_rate <= R3_STABILITY_MAX and mean_range <= R3_STABILITY_MAX:
        return {"status": "REPEAT_QUALIFICATION_PASS_R3", "R_star": 3, **metrics}
    return {"status": "REPEAT_QUALIFICATION_STOP_R3_STILL_UNSTABLE", "R_star": None, **metrics}


def decide_target_only_eligibility(
    *,
    source_failure_valid: bool,
    repair_artifact_valid: bool,
    interface_valid: bool,
    rows: Iterable[dict[str, Any]],
    R_star: int,
) -> dict[str, Any]:
    """Pre-topology eligibility only. The result must never be recomputed from I/L/H outcomes."""
    if R_star not in (2, 3):
        raise PreexecError("R_star must be frozen to 2 or 3 before TARGET_ONLY_VERIFICATION")
    rows = list(rows)
    expected = {(branch, repeat) for branch in BRANCHES for repeat in range(1, R_star + 1)}
    index: dict[tuple[str, int], dict[str, Any]] = {}
    snapshot_hashes: set[str] = set()
    repair_hashes: set[str] = set()
    for row in rows:
        key = (str(row["branch"]), int(row["repeat"]))
        if key in index:
            raise PreexecError(f"duplicate TO-V row: {key}")
        if key not in expected:
            raise PreexecError(f"TO-V row outside frozen matrix: {key}")
        if not isinstance(row.get("target_success"), bool) or not isinstance(row.get("valid"), bool):
            raise PreexecError("TO-V target_success/valid types are invalid")
        snapshot_hashes.add(str(row["snapshot_sha256"]))
        if key[0] == "REAL_REPAIR":
            repair_hashes.add(str(row["repair_sha256"]))
        index[key] = row
    if set(index) != expected:
        raise PreexecError("TO-V matrix is incomplete")
    matrix_valid = all(bool(row["valid"]) for row in index.values())
    same_snapshot = len(snapshot_hashes) == 1 and "" not in snapshot_hashes
    one_repair = len(repair_hashes) == 1 and "" not in repair_hashes
    real_rate = sum(int(index[("REAL_REPAIR", r)]["target_success"]) for r in range(1, R_star + 1)) / R_star
    no_rate = sum(int(index[("NO_UPDATE", r)]["target_success"]) for r in range(1, R_star + 1)) / R_star
    uptake_delta = real_rate - no_rate
    eligible = bool(
        source_failure_valid
        and repair_artifact_valid
        and interface_valid
        and matrix_valid
        and same_snapshot
        and one_repair
        and uptake_delta >= TO_V_UPTAKE_MIN
    )
    return {
        "eligible": eligible,
        "target_success_rate_real_repair": real_rate,
        "target_success_rate_no_update": no_rate,
        "target_uptake_delta": uptake_delta,
        "uptake_required_min": TO_V_UPTAKE_MIN,
        "matrix_valid": matrix_valid,
        "same_snapshot": same_snapshot,
        "one_frozen_repair": one_repair,
        "pre_topology_only": True,
        "post_topology_target_outcomes_may_change_eligibility": False,
    }


def _sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def conservative_loo_sd(values: list[float]) -> float:
    if len(values) < 4:
        raise PreexecError("precision qualification requires at least four development families")
    candidates = [_sample_sd(values)]
    for i in range(len(values)):
        subset = values[:i] + values[i + 1 :]
        candidates.append(_sample_sd(subset))
    return max(candidates)


def _family_effects_from_development(rows: Iterable[dict[str, Any]], R_star: int) -> tuple[list[float], list[float]]:
    """Compute variance inputs internally. Callers must not persist means or signs."""
    if R_star not in (2, 3):
        raise PreexecError("R_star must be 2 or 3")
    index = _index_repeat_rows(rows, tuple(range(1, R_star + 1)))
    families = sorted({key[0] for key in index})
    rq1_effects: list[float] = []
    rq2_effects: list[float] = []
    for family in families:
        ue: dict[str, float] = {}
        for arm in ARMS:
            crr = {}
            for branch in BRANCHES:
                vals = [_validate_crr(index[(family, arm, branch, r)]["crr"]) for r in range(1, R_star + 1)]
                crr[branch] = sum(vals) / len(vals)
            ue[arm] = crr["REAL_REPAIR"] - crr["NO_UPDATE"]
        rq1_effects.append(sum(ue.values()) / len(ARMS))
        rq2_effects.append(ue["HIGH"] - ue["INDEPENDENT"])
    return rq1_effects, rq2_effects


def decide_N_star(rows: Iterable[dict[str, Any]], R_star: int) -> dict[str, Any]:
    """Select N using dispersion only. No development mean/sign is returned or used."""
    rows = list(rows)
    if any(not bool(row.get("valid")) for row in rows):
        return {"status": "PRECISION_QUALIFICATION_INVALID_TECHNICAL_UNIT", "N_star": None}
    rq1_effects, rq2_effects = _family_effects_from_development(rows, R_star)
    sd_rq1 = conservative_loo_sd(rq1_effects)
    sd_rq2 = conservative_loo_sd(rq2_effects)
    selected = None
    table: list[dict[str, Any]] = []
    for n in N_CANDIDATES:
        se1 = sd_rq1 / math.sqrt(n)
        se2 = sd_rq2 / math.sqrt(n)
        qualifies = se1 <= PLANNING_SE_MAX and se2 <= PLANNING_SE_MAX
        table.append({"N": n, "rq1_planning_se": se1, "rq2_planning_se": se2, "qualifies": qualifies})
        if selected is None and qualifies:
            selected = n
    status = "PRECISION_QUALIFICATION_PASS" if selected is not None else "PRECISION_QUALIFICATION_STOP_N24_INSUFFICIENT"
    return {
        "status": status,
        "N_star": selected,
        "planning_meaningful_effect": PLANNING_MEANINGFUL_EFFECT,
        "planning_se_max": PLANNING_SE_MAX,
        "conservative_loo_sd_rq1": sd_rq1,
        "conservative_loo_sd_rq2": sd_rq2,
        "candidate_table": table,
        "development_effect_mean_emitted": False,
        "development_effect_sign_emitted": False,
        "selection_uses_effect_direction": False,
    }


def stable_family_order(family_ids: Iterable[str]) -> list[str]:
    unique = list(dict.fromkeys(str(x) for x in family_ids))
    if len(unique) != len(set(unique)):
        raise PreexecError("duplicate family ids")
    return sorted(unique, key=lambda fid: hashlib.sha256(f"{PANEL_ORDER_SALT}|{fid}".encode("utf-8")).hexdigest())


def select_confirmatory_panel(eligibility: dict[str, bool], N_star: int) -> dict[str, Any]:
    if N_star not in N_CANDIDATES:
        raise PreexecError("N_star outside frozen candidate set")
    if len(eligibility) != 24:
        raise PreexecError("confirmatory reserve must contain exactly 24 family ids")
    order = stable_family_order(eligibility)
    selected = [fid for fid in order if bool(eligibility[fid])][:N_star]
    if len(selected) < N_star:
        return {
            "status": "CONFIRMATORY_SUPPORT_STOP_INSUFFICIENT_PRE_TOPOLOGY_ELIGIBLE_FAMILIES",
            "selected_family_ids": selected,
            "N_star": N_star,
            "eligible_count": sum(bool(v) for v in eligibility.values()),
        }
    return {
        "status": "CONFIRMATORY_PANEL_FROZEN",
        "selected_family_ids": selected,
        "selected_family_ids_sha256": sha256_value(selected),
        "N_star": N_star,
        "eligible_count": sum(bool(v) for v in eligibility.values()),
        "selection_order": "stable_hash",
        "post_topology_backfill_allowed": False,
    }


def build_freeze_artifact() -> dict[str, Any]:
    plan = ROOT / "generated/agent-constraint-externality-minimum-effective-plan-r2-20260904.json"
    review = ROOT / "generated/agent-constraint-externality-minimum-r2-review-closeout-20260904.json"
    proposal = ROOT / "generated/agent-constraint-externality-confirmatory-execution-proposal-20260904.json"
    source = Path(__file__).resolve()
    for path in (plan, review, proposal):
        if not path.is_file():
            raise PreexecError(f"missing parent artifact: {path}")
    parent = json.loads(plan.read_text(encoding="utf-8"))
    prop = json.loads(proposal.read_text(encoding="utf-8"))
    if any(bool(v) for v in prop.get("authority", {}).values()):
        raise PreexecError("preexec freeze requires all execution authorities false")
    artifact = {
        "schema_version": 1,
        "object_id": OBJECT_ID,
        "recorded_date": "2026-09-04",
        "status": "ZERO_PROVIDER_PREEXEC_FREEZE_COMPLETE_EXECUTION_AUTHORITY_CLOSED",
        "parents": {
            "minimum_effective_plan_canonical_content_sha256": sha256_value(parent),
            "minimum_effective_plan_file_sha256": sha256_file(plan),
            "review_closeout_file_sha256": sha256_file(review),
            "execution_proposal_file_sha256": sha256_file(proposal),
        },
        "target_only_verification": {
            "surface_id": "TARGET_ONLY_VERIFICATION_V1",
            "construction": "same common pre-update snapshot; target instruction and TARGET constraints only; no non-target instruction, topology label, coupling context, or non-target evaluator readout",
            "branches": list(BRANCHES),
            "repeats": "use already-frozen R_star",
            "snapshot_rule": "NO_UPDATE and REAL_REPAIR reset to identical common_pre_update_snapshot_sha256 for every repeat",
            "repair_rule": "REAL_REPAIR uses exact frozen repair bytes; one repair_sha256 across all TO-V and later topology arms",
            "evaluator": "existing AppWorld semantic target evaluator only",
            "eligibility_uptake_delta_min": TO_V_UPTAKE_MIN,
            "all_units_normal_and_measurement_valid_required": True,
            "timing": "strictly before INDEPENDENT/LOW/HIGH exposure",
            "post_topology_target_outcomes_may_change_eligibility": False,
        },
        "repeat_qualification": {
            "development_family_count": DEV_FAMILY_COUNT,
            "permanently_excluded_from_confirmatory": True,
            "initial_repeats": 2,
            "condition_cells_per_family": len(ARMS) * len(BRANCHES),
            "R2_rule": f"target disagreement rate <= {R2_STABILITY_MAX:.2f} AND mean absolute CRR repeat difference <= {R2_STABILITY_MAX:.2f}",
            "R3_trigger": f"R2 fails but both metrics <= {R3_STABILITY_MAX:.2f}",
            "R3_rule": f"after one additional development repeat, target non-unanimous rate <= {R3_STABILITY_MAX:.2f} AND mean CRR three-repeat range <= {R3_STABILITY_MAX:.2f}",
            "hard_stop": "if any metric exceeds 0.20, any technical unit is invalid, or R3 remains unstable; R>3 forbidden",
            "selection_uses_treatment_direction": False,
        },
        "precision_freeze": {
            "N_candidates": list(N_CANDIDATES),
            "planning_meaningful_effect": PLANNING_MEANINGFUL_EFFECT,
            "planning_se_max": PLANNING_SE_MAX,
            "development_dispersion": "max(full-sample SD, every leave-one-family-out SD) for family-level pooled UE and family-level HIGH-minus-INDEPENDENT UE contrast",
            "selection": "smallest N candidate whose RQ1 and RQ2 planning SE are both <= 0.10",
            "development_means_or_signs_in_decision_artifact": False,
            "if_N24_fails": "STOP_PRECISION_QUALIFICATION; do not add families beyond reserve",
        },
        "panel_selection": {
            "reserve_family_count": 24,
            "stable_hash_salt": PANEL_ORDER_SALT,
            "eligibility_inputs": [
                "valid semantic source failure",
                "valid frozen repair artifact",
                "TO-V uptake delta >= 0.50",
                "no interface or measurement invalidity",
            ],
            "selection": "first N_star eligible family ids under frozen stable hash order",
            "reserve_activation": "pre-topology eligibility attrition only",
            "post_topology_backfill_allowed": False,
        },
        "post_treatment_guard": {
            "retain_every_frozen_family_in_every_I_L_H_arm": True,
            "topology_specific_target_success_used_for_deletion": False,
            "target_retention": "jointly report with collateral outcomes",
            "still_effective_repair_claim": "requires a prospectively specified panel-level target-gain inference; never family deletion",
        },
        "implementation": {
            "freeze_module": str(source.relative_to(ROOT)),
            "freeze_module_sha256": sha256_file(source),
        },
        "authority": {
            "provider_execution": False,
            "gate0": False,
            "gate1": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "scientific_provider_calls_created": 0,
        "scientific_outcomes_created": 0,
        "next_required_action": "NARROW_PREEXEC_CONSISTENCY_REVIEW_THEN_SEPARATE_HUMAN_EXECUTION_AUTHORITY",
    }
    artifact["content_sha256"] = sha256_value(artifact)
    return artifact


def main() -> None:
    output = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-freeze-20260904.json"
    artifact = build_freeze_artifact()
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "content_sha256": artifact["content_sha256"], "output": str(output.relative_to(ROOT))}, sort_keys=True))


if __name__ == "__main__":
    main()
