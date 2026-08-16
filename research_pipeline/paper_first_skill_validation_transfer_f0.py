from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

CANDIDATE_ID = "PA-05-SKILL-VALIDATION-TRANSFER"
CONTRACT_VERSION = "skill-validation-transfer-f0-v1"
SOURCE_REF = "arXiv:2605.24117"
SOURCE_REPOSITORY = "AIoT-MLSys-Lab/SkillEvolBench"
SOURCE_COMMIT = "9e3daa339987c3cfa624121e1be442593a53d43c"
SOURCE_ARCHIVE_SHA256 = "2892e337780746e547a748c947b379b3c55af09eea1d273ace383b80d2e569ee"
SOURCE_TASKS = 180
SOURCE_FAMILIES = 30
SOURCE_TASKS_PER_FAMILY = 6
SOURCE_LEARNING_ROLES = ("canonical", "enriched", "variant")
SOURCE_DEPLOYMENT_ROLES = ("context-shift", "adversarial", "composition")
ARMS = ("raw_trajectory_rag", "selfgen_experience_always")
ORDER_SEED = "A"
MODEL_PRESET = "gemini-3-flash"
SCHEDULE_TASKS_PER_ARM = 270
PRIMARY_TASKS_PER_ARM = 180
LEARNING_REPLAYS_PER_ARM = 90

# Frozen before any PA-05 model execution.
MIN_LOCAL_WINS_PER_ARM = 5
MIN_DEPLOYMENT_WINS_PER_ARM = 5
MIN_JOINT_DECISIVE_FAMILIES = 10
MIN_INVERSION_RATE = 0.40
MIN_ORACLE_MINUS_LOCAL_REGRET = 0.08
MIN_BOOTSTRAP_REGRET_LOWER95 = 0.03
MAX_LOCAL_SELECTOR_ADVANTAGE_OVER_BEST_GLOBAL = 0.03
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260817


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_plan() -> dict[str, Any]:
    plan = {
        "schema_version": "1.0-private",
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "paper_problem_claimed": False,
        "scientific_authority": False,
        "source": {
            "primary_ref": SOURCE_REF,
            "repository": SOURCE_REPOSITORY,
            "commit_sha": SOURCE_COMMIT,
            "archive_sha256": SOURCE_ARCHIVE_SHA256,
            "tasks": SOURCE_TASKS,
            "families": SOURCE_FAMILIES,
            "tasks_per_family": SOURCE_TASKS_PER_FAMILY,
        },
        "execution": {
            "arms": list(ARMS),
            "order_seed": ORDER_SEED,
            "model_preset": MODEL_PRESET,
            "tasks_per_arm": SCHEDULE_TASKS_PER_ARM,
            "primary_tasks_per_arm": PRIMARY_TASKS_PER_ARM,
            "learning_replays_per_arm": LEARNING_REPLAYS_PER_ARM,
            "run_count": len(ARMS),
            "first_positive_followup_only": "repeat with order seed B before any Problem-Gate submission",
        },
        "unit": {
            "primary_unit": "latent skill family",
            "family_count": SOURCE_FAMILIES,
            "local_validation_statistic": (
                "mean selfgen within-env replay success on T1-T3 minus mean raw-trajectory within-env replay success on T1-T3"
            ),
            "deployment_statistic": (
                "mean selfgen primary success on T4-T6 minus mean raw-trajectory primary success on T4-T6"
            ),
            "local_selector": "choose selfgen iff local_validation_statistic > 0; ties choose raw trajectory",
            "deployment_oracle": "choose the arm with higher T4-T6 mean success within the same family",
        },
        "matched_dimensions": [
            "exact SkillEvolBench commit and task assets",
            "same 30 latent families and role schedule",
            "same model preset",
            "same order seed",
            "same 270-trial schedule",
            "same 180 primary tasks",
            "same 90 T1-T3 within-env replays",
            "same verifier truth",
            "library/trajectory state frozen during T4-T6 and replay",
        ],
        "strongest_reductions": [
            "one arm globally dominates deployment",
            "local validation is already deployment-predictive",
            "family difficulty alone explains the apparent inversion",
            "raw trajectory reuse is simply globally better than distilled skill abstraction",
            "single-seed execution noise rather than selection-statistic failure",
        ],
        "decision_rule": {
            "coverage": {
                "families_exact": SOURCE_FAMILIES,
                "each_arm_primary_roles_per_family": list(SOURCE_LEARNING_ROLES + SOURCE_DEPLOYMENT_ROLES),
                "each_arm_replay_roles_per_family": list(SOURCE_LEARNING_ROLES),
            },
            "problem_f0_go_all_required": {
                "local_raw_wins_min": MIN_LOCAL_WINS_PER_ARM,
                "local_selfgen_wins_min": MIN_LOCAL_WINS_PER_ARM,
                "deployment_raw_wins_min": MIN_DEPLOYMENT_WINS_PER_ARM,
                "deployment_selfgen_wins_min": MIN_DEPLOYMENT_WINS_PER_ARM,
                "joint_decisive_families_min": MIN_JOINT_DECISIVE_FAMILIES,
                "local_deployment_inversion_rate_min": MIN_INVERSION_RATE,
                "oracle_minus_local_selector_regret_min": MIN_ORACLE_MINUS_LOCAL_REGRET,
                "bootstrap_regret_lower95_min": MIN_BOOTSTRAP_REGRET_LOWER95,
                "local_selector_advantage_over_best_global_max": MAX_LOCAL_SELECTOR_ADVANTAGE_OVER_BEST_GLOBAL,
            },
            "go": "GO_SELECTION_VALIDITY_PROBLEM_TO_SEED_B_REPLICATION_AND_CURRENT_SOURCE_REVIEW",
            "stop": "STOP_LOCAL_VALIDATION_PROBLEM_NOT_IDENTIFIED_OR_GLOBAL_ARM_REDUCTION_SUFFICIENT",
            "hold": "INCONCLUSIVE_SUPPORT_OR_PROTOCOL_MISMATCH",
        },
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }
    plan["plan_sha256"] = _canonical_sha({k: v for k, v in plan.items() if k != "plan_sha256"})
    return plan


def _passed(row: dict[str, Any]) -> int:
    if "passed" in row:
        return int(bool(row["passed"]))
    if "verifier_passed" in row:
        return int(bool(row["verifier_passed"]))
    outcome = row.get("outcome") or {}
    if isinstance(outcome, dict) and "verifier_passed" in outcome:
        return int(bool(outcome["verifier_passed"]))
    raise ValueError("row lacks verifier_passed/passed outcome")


def _role(row: dict[str, Any]) -> str:
    return str(row.get("task_role") or row.get("role") or "")


def _mode(row: dict[str, Any]) -> str:
    return str(row.get("replay_mode") or "primary")


def _family(row: dict[str, Any]) -> str:
    return str(row.get("family_id") or "")


def _mean(values: Iterable[int | float]) -> float:
    xs = list(values)
    return sum(float(v) for v in xs) / len(xs) if xs else 0.0


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(len(xs) - 1, lo + 1)
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def _arm_family_table(rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], list[str]]:
    errors: list[str] = []
    grouped: dict[str, dict[tuple[str, str], list[int]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        family = _family(row)
        role = _role(row)
        mode = _mode(row)
        if not family or role not in set(SOURCE_LEARNING_ROLES + SOURCE_DEPLOYMENT_ROLES):
            continue
        if mode not in {"primary", "within_env_replay"}:
            continue
        grouped[family][(mode, role)].append(_passed(row))

    if len(grouped) != SOURCE_FAMILIES:
        errors.append(f"expected {SOURCE_FAMILIES} families, got {len(grouped)}")

    table: dict[str, dict[str, float]] = {}
    for family, cells in sorted(grouped.items()):
        for role in SOURCE_LEARNING_ROLES + SOURCE_DEPLOYMENT_ROLES:
            n = len(cells.get(("primary", role), []))
            if n != 1:
                errors.append(f"{family}:primary:{role}:expected1:got{n}")
        for role in SOURCE_LEARNING_ROLES:
            n = len(cells.get(("within_env_replay", role), []))
            if n != 1:
                errors.append(f"{family}:replay:{role}:expected1:got{n}")
        for role in SOURCE_DEPLOYMENT_ROLES:
            if cells.get(("within_env_replay", role)):
                errors.append(f"{family}:unexpected-eval-replay:{role}")
        table[family] = {
            "local_replay": _mean(cells.get(("within_env_replay", r), [])[0] for r in SOURCE_LEARNING_ROLES if cells.get(("within_env_replay", r))),
            "deployment": _mean(cells.get(("primary", r), [])[0] for r in SOURCE_DEPLOYMENT_ROLES if cells.get(("primary", r))),
            "learning_primary": _mean(cells.get(("primary", r), [])[0] for r in SOURCE_LEARNING_ROLES if cells.get(("primary", r))),
        }
    return table, errors


def analyze_rows(raw_rows: list[dict[str, Any]], selfgen_rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw, raw_errors = _arm_family_table(raw_rows)
    skill, skill_errors = _arm_family_table(selfgen_rows)
    errors = raw_errors + skill_errors
    if set(raw) != set(skill):
        errors.append("raw/selfgen family sets differ")
    if errors:
        return {
            "status": "INCONCLUSIVE_SUPPORT_OR_PROTOCOL_MISMATCH",
            "errors": errors,
            "paper_problem_authorized": False,
            "scientific_authority": False,
        }

    families: list[dict[str, Any]] = []
    for family in sorted(raw):
        local_delta = skill[family]["local_replay"] - raw[family]["local_replay"]
        deployment_delta = skill[family]["deployment"] - raw[family]["deployment"]
        selected = "selfgen" if local_delta > 0 else "raw"
        selected_deployment = skill[family]["deployment"] if selected == "selfgen" else raw[family]["deployment"]
        oracle_deployment = max(raw[family]["deployment"], skill[family]["deployment"])
        families.append({
            "family_id": family,
            "raw_local_replay": raw[family]["local_replay"],
            "selfgen_local_replay": skill[family]["local_replay"],
            "raw_deployment": raw[family]["deployment"],
            "selfgen_deployment": skill[family]["deployment"],
            "local_delta": local_delta,
            "deployment_delta": deployment_delta,
            "local_selector_arm": selected,
            "local_selector_deployment": selected_deployment,
            "deployment_oracle": oracle_deployment,
            "regret": oracle_deployment - selected_deployment,
            "joint_decisive": local_delta != 0 and deployment_delta != 0,
            "inversion": local_delta != 0 and deployment_delta != 0 and ((local_delta > 0) != (deployment_delta > 0)),
        })

    local_raw_wins = sum(row["local_delta"] < 0 for row in families)
    local_selfgen_wins = sum(row["local_delta"] > 0 for row in families)
    deployment_raw_wins = sum(row["deployment_delta"] < 0 for row in families)
    deployment_selfgen_wins = sum(row["deployment_delta"] > 0 for row in families)
    decisive = [row for row in families if row["joint_decisive"]]
    inversions = sum(row["inversion"] for row in decisive)
    inversion_rate = inversions / len(decisive) if decisive else 0.0

    local_selector_mean = _mean(row["local_selector_deployment"] for row in families)
    oracle_mean = _mean(row["deployment_oracle"] for row in families)
    raw_global_mean = _mean(row["raw_deployment"] for row in families)
    selfgen_global_mean = _mean(row["selfgen_deployment"] for row in families)
    best_global_mean = max(raw_global_mean, selfgen_global_mean)
    regret = oracle_mean - local_selector_mean
    selector_advantage = local_selector_mean - best_global_mean

    rng = random.Random(BOOTSTRAP_SEED)
    bootstrap_regrets: list[float] = []
    n = len(families)
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = [families[rng.randrange(n)] for _ in range(n)]
        bootstrap_regrets.append(
            _mean(row["deployment_oracle"] for row in sample)
            - _mean(row["local_selector_deployment"] for row in sample)
        )
    regret_lower95 = _percentile(bootstrap_regrets, 0.025)
    regret_upper95 = _percentile(bootstrap_regrets, 0.975)

    gates = {
        "local_raw_wins": local_raw_wins >= MIN_LOCAL_WINS_PER_ARM,
        "local_selfgen_wins": local_selfgen_wins >= MIN_LOCAL_WINS_PER_ARM,
        "deployment_raw_wins": deployment_raw_wins >= MIN_DEPLOYMENT_WINS_PER_ARM,
        "deployment_selfgen_wins": deployment_selfgen_wins >= MIN_DEPLOYMENT_WINS_PER_ARM,
        "joint_decisive_support": len(decisive) >= MIN_JOINT_DECISIVE_FAMILIES,
        "inversion_rate": inversion_rate >= MIN_INVERSION_RATE,
        "oracle_minus_local_regret": regret >= MIN_ORACLE_MINUS_LOCAL_REGRET,
        "bootstrap_regret_lower95": regret_lower95 >= MIN_BOOTSTRAP_REGRET_LOWER95,
        "local_selector_not_better_than_global": selector_advantage <= MAX_LOCAL_SELECTOR_ADVANTAGE_OVER_BEST_GLOBAL,
    }
    status = (
        "GO_SELECTION_VALIDITY_PROBLEM_TO_SEED_B_REPLICATION_AND_CURRENT_SOURCE_REVIEW"
        if all(gates.values())
        else "STOP_LOCAL_VALIDATION_PROBLEM_NOT_IDENTIFIED_OR_GLOBAL_ARM_REDUCTION_SUFFICIENT"
    )
    return {
        "status": status,
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "families": len(families),
        "support": {
            "local_raw_wins": local_raw_wins,
            "local_selfgen_wins": local_selfgen_wins,
            "deployment_raw_wins": deployment_raw_wins,
            "deployment_selfgen_wins": deployment_selfgen_wins,
            "joint_decisive_families": len(decisive),
            "inversions": inversions,
            "inversion_rate": inversion_rate,
        },
        "deployment": {
            "raw_global_mean": raw_global_mean,
            "selfgen_global_mean": selfgen_global_mean,
            "best_global_mean": best_global_mean,
            "local_selector_mean": local_selector_mean,
            "oracle_mean": oracle_mean,
            "oracle_minus_local_selector_regret": regret,
            "local_selector_advantage_over_best_global": selector_advantage,
            "bootstrap_regret_ci95": [regret_lower95, regret_upper95],
        },
        "gates": gates,
        "family_rows": families,
        "paper_problem_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
    }


def write_plan(path: Path) -> dict[str, Any]:
    plan = build_plan()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan


if __name__ == "__main__":
    print(json.dumps(build_plan(), ensure_ascii=False, indent=2))
