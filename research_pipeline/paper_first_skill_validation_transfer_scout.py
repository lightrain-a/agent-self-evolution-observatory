from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_skill_validation_transfer_f0 import (
    CANDIDATE_ID,
    CONTRACT_VERSION,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_COMMIT,
    SOURCE_FAMILIES,
    SOURCE_REF,
    SOURCE_REPOSITORY,
    SOURCE_TASKS,
    build_plan,
)
from .paper_first_skill_validation_transfer_runtime_audit import (
    DEFAULT_JSON as RUNTIME_AUDIT_JSON,
    validate_runtime_audit,
)

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-skill-validation-transfer-scout-20260817.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-skill-validation-transfer-scout-20260817.js"
F0_HARNESS = PROJECT_ROOT / "research_pipeline" / "paper_first_skill_validation_transfer_f0.py"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def _load_runtime_audit() -> dict[str, Any] | None:
    if not RUNTIME_AUDIT_JSON.exists():
        return None
    state = json.loads(RUNTIME_AUDIT_JSON.read_text(encoding="utf-8"))
    errors = validate_runtime_audit(state)
    if errors:
        raise ValueError("invalid PA-05 runtime audit receipt: " + "; ".join(errors))
    return state


def build_skill_validation_transfer_scout(
    *,
    runtime_audit: dict[str, Any] | None = None,
    harbor_importable: bool | None = None,
    runtime_image_present: bool | None = None,
    gemini_credential_present: bool | None = None,
    benchmark_python_ready: bool | None = None,
    bedrock_credential_present: bool = False,
) -> dict[str, Any]:
    plan = build_plan()
    # The frozen gemini-3-flash preset routes both the Harbor agent and the
    # host-side LiteLLM components (including SkillAuthor) through Gemini.
    # Bedrock is informational only. Runtime readiness comes from a machine
    # audit receipt when present; explicit arguments remain available for tests.
    if runtime_audit is None and all(
        value is None
        for value in (
            harbor_importable,
            runtime_image_present,
            gemini_credential_present,
            benchmark_python_ready,
        )
    ):
        runtime_audit = _load_runtime_audit()
    if runtime_audit is not None:
        audit_errors = validate_runtime_audit(runtime_audit)
        if audit_errors:
            raise ValueError("invalid PA-05 runtime audit receipt: " + "; ".join(audit_errors))
        audit_python = runtime_audit.get("python") or {}
        audit_image = runtime_audit.get("runtime_image") or {}
        audit_credentials = runtime_audit.get("credentials") or {}
        harbor_importable = bool(audit_python.get("harbor_importable"))
        benchmark_python_ready = bool(audit_python.get("benchmark_dependencies_present"))
        runtime_image_present = audit_image.get("status") == "PRESENT"
        runtime_image_status = str(audit_image.get("status") or "UNVERIFIED")
        runtime_image_observable = bool(audit_image.get("observable"))
        gemini_credential_present = bool(audit_credentials.get("GEMINI_API_KEY_present"))
        execution_ready = bool(runtime_audit.get("execution_ready"))
        hold_reason = list(runtime_audit.get("hold_reason") or [])
    else:
        harbor_importable = bool(harbor_importable)
        runtime_image_present = bool(runtime_image_present)
        gemini_credential_present = bool(gemini_credential_present)
        benchmark_python_ready = True if benchmark_python_ready is None else bool(benchmark_python_ready)
        runtime_image_status = "PRESENT" if runtime_image_present else "UNVERIFIED"
        runtime_image_observable = bool(runtime_image_present)
        execution_ready = bool(
            benchmark_python_ready
            and harbor_importable
            and runtime_image_present
            and gemini_credential_present
        )
        hold_reason = [] if execution_ready else [
            name
            for name, ok in (
                ("benchmark Python dependencies", benchmark_python_ready),
                ("Harbor SDK", harbor_importable),
                ("agent-runtime:latest", runtime_image_present),
                ("Gemini credential for agent + host-side SkillAuthor", gemini_credential_present),
            )
            if not ok
        ]
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "candidate_id": CANDIDATE_ID,
        "status": "DESIGN_READY_EXECUTION_ENV_HOLD" if not execution_ready else "DESIGN_READY_EXECUTION_ENV_PRESENT",
        "scientific_authority": False,
        "paper_problem_claimed": False,
        "source": {
            "primary_ref": SOURCE_REF,
            "repository": SOURCE_REPOSITORY,
            "commit_sha": SOURCE_COMMIT,
            "archive_sha256": SOURCE_ARCHIVE_SHA256,
            "asset_validation": {
                "pass": True,
                "skill_families": 30,
                "tasks": SOURCE_TASKS,
                "task_roles": {
                    "canonical": 30,
                    "enriched": 30,
                    "variant": 30,
                    "context-shift": 30,
                    "adversarial": 30,
                    "composition": 30,
                },
                "config_validation_pass": True,
            },
        },
        "f0": {
            "contract_version": CONTRACT_VERSION,
            "design_ready": True,
            "plan_sha256": plan["plan_sha256"],
            "harness_sha256": _sha(F0_HARNESS),
            "primary_unit": "latent skill family",
            "families": SOURCE_FAMILIES,
            "arms": list(plan["execution"]["arms"]),
            "model_preset": plan["execution"]["model_preset"],
            "order_seed": plan["execution"]["order_seed"],
            "tasks_per_arm": plan["execution"]["tasks_per_arm"],
            "primary_tasks_per_arm": plan["execution"]["primary_tasks_per_arm"],
            "learning_replays_per_arm": plan["execution"]["learning_replays_per_arm"],
            "dry_run": {
                "raw_trajectory_rag": {"pass": True, "scheduled_tasks": 270},
                "selfgen_experience_always": {"pass": True, "scheduled_tasks": 270},
            },
            "model_calls_executed": 0,
            "task_trials_executed": 0,
        },
        "current_source_boundary": {
            "status": "SURVIVES_ONLY_AS_FALSIFIABLE_SELECTION_VALIDITY_PROBLEM_NOT_PAPER_CLAIM",
            "closest_work": [
                {
                    "ref": "arXiv:2605.24117",
                    "role": "SkillEvolBench defines acquisition/replay and frozen deployment axes and reports unstable skill gains plus raw-trajectory strength; it does not make local validation-statistic identifiability the scientific object.",
                },
                {
                    "ref": "arXiv:2603.25158",
                    "role": "Trace2Skill selects evolved skills using training/evolution-split validation before held-out evaluation, motivating rather than resolving whether local validation is deployment-identifying.",
                },
                {
                    "ref": "arXiv:2605.23904",
                    "role": "SkillOpt accepts edits by held-out validation and reports transfer; it does not test whether family-local validation ranks which persistent representation will transfer under context/adversarial/composition shift.",
                },
                {
                    "ref": "arXiv:2605.08693",
                    "role": "SkillMaster uses counterfactual utility on related probe tasks to train skill editing; the surviving question is whether such local/probe validation is itself an identifying statistic for shifted deployment.",
                },
                {
                    "ref": "arXiv:2603.02766",
                    "role": "EvoSkill retains skills that improve held-out validation and reports transfer; it does not isolate local validation versus deployment-optimal representation on matched family units.",
                },
            ],
            "surviving_problem": (
                "Under a frozen skill library and matched family schedule, does local T1-T3 replay preference between distilled skills and raw trajectory reuse identify the arm that actually wins on T4 context shift, T5 adversarial, and T6 composition?"
            ),
            "not_claimed": [
                "a new skill generator",
                "that skills generally fail to transfer",
                "that raw trajectories globally dominate skills",
                "a method improvement before the selection-validity F0 passes",
            ],
        },
        "execution_environment": {
            "host": "69",
            "asset_and_config_pass": True,
            "benchmark_python_ready": benchmark_python_ready,
            "harbor_importable": harbor_importable,
            "runtime_image_present": runtime_image_present,
            "runtime_image_status": runtime_image_status,
            "runtime_image_observable": runtime_image_observable,
            "gemini_credential_present": gemini_credential_present,
            "bedrock_credential_present": bedrock_credential_present,
            "bedrock_required_for_f0": False,
            "required_provider_credentials": ["GEMINI_API_KEY"],
            "provider_routing": {
                "model_preset": "gemini-3-flash",
                "agent_provider": "gemini",
                "agent_model": "google/gemini-3-flash-preview",
                "host_litellm_model": "gemini/gemini-3-flash-preview",
                "host_litellm_api_key_env": "GEMINI_API_KEY",
                "skill_author_uses_run_model_when_model_yaml_active": True,
                "model_preset_sha256": "103f7608956b8b5d27251b87b08ebaa2503f1be039204beac8fbc26e0811fbd1",
                "runtime_routing_sha256": "239040f5009fd7e551020c1ea82460a7d3aa4d656eaf752cb867d516802599f2",
            },
            "execution_ready": execution_ready,
            "hold_reason": hold_reason,
            "direct_execution_authorized": False,
            "controller_capability_required": True,
        },
        "cost_control": {
            "first_f0_arms": 2,
            "default_repo_estimator_opus_agent_cost_usd_per_180_primary_arm": 48.6,
            "selected_low_cost_agent_preset": "gemini-3-flash",
            "provider_price_must_be_rechecked_at_launch": True,
            "expensive_curated_revision_arm_deferred_until_first_f0_residual": True,
            "second_order_seed_deferred_until_first_f0_go": True,
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
        "source_bindings": {
            "f0_harness": {
                "path": str(F0_HARNESS.relative_to(PROJECT_ROOT)),
                "sha256": _sha(F0_HARNESS),
            },
            "runtime_audit": {
                "path": str(RUNTIME_AUDIT_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(RUNTIME_AUDIT_JSON),
            } if RUNTIME_AUDIT_JSON.exists() else None,
            "plan_sha256": plan["plan_sha256"],
        },
    }


def validate_skill_validation_transfer_scout(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("scientific_authority") is not False or state.get("paper_problem_claimed") is not False:
        errors.append("scout cannot carry paper/scientific authority")
    source = state.get("source") or {}
    if source.get("repository") != SOURCE_REPOSITORY or source.get("commit_sha") != SOURCE_COMMIT:
        errors.append("SkillEvolBench source identity drift")
    if source.get("archive_sha256") != SOURCE_ARCHIVE_SHA256:
        errors.append("SkillEvolBench archive digest drift")
    audit = source.get("asset_validation") or {}
    if audit.get("pass") is not True or audit.get("config_validation_pass") is not True:
        errors.append("source asset/config validation must pass")
    if int(audit.get("tasks") or 0) != SOURCE_TASKS or int(audit.get("skill_families") or 0) != SOURCE_FAMILIES:
        errors.append("source task/family cardinality drift")
    f0 = state.get("f0") or {}
    if f0.get("design_ready") is not True or int(f0.get("families") or 0) != SOURCE_FAMILIES:
        errors.append("F0 design is not frozen/complete")
    if f0.get("arms") != ["raw_trajectory_rag", "selfgen_experience_always"]:
        errors.append("F0 matched-arm contract drift")
    if any(int((f0.get("dry_run") or {}).get(arm, {}).get("scheduled_tasks") or 0) != 270 for arm in f0.get("arms") or []):
        errors.append("F0 dry-run schedule must be 270 tasks per arm")
    if int(f0.get("model_calls_executed") or 0) != 0 or int(f0.get("task_trials_executed") or 0) != 0:
        errors.append("scout receipt must remain pre-execution")
    boundary = state.get("current_source_boundary") or {}
    if boundary.get("status") != "SURVIVES_ONLY_AS_FALSIFIABLE_SELECTION_VALIDITY_PROBLEM_NOT_PAPER_CLAIM":
        errors.append("current-source claim boundary drift")
    env = state.get("execution_environment") or {}
    if env.get("direct_execution_authorized") is not False or env.get("controller_capability_required") is not True:
        errors.append("execution environment cannot self-authorize")
    routing = env.get("provider_routing") or {}
    if env.get("bedrock_required_for_f0") is not False:
        errors.append("Bedrock must not be required by the frozen Gemini F0 route")
    if env.get("required_provider_credentials") != ["GEMINI_API_KEY"]:
        errors.append("Gemini F0 credential contract drift")
    if (
        routing.get("model_preset") != "gemini-3-flash"
        or routing.get("agent_provider") != "gemini"
        or routing.get("host_litellm_api_key_env") != "GEMINI_API_KEY"
        or routing.get("skill_author_uses_run_model_when_model_yaml_active") is not True
        or routing.get("model_preset_sha256") != "103f7608956b8b5d27251b87b08ebaa2503f1be039204beac8fbc26e0811fbd1"
        or routing.get("runtime_routing_sha256") != "239040f5009fd7e551020c1ea82460a7d3aa4d656eaf752cb867d516802599f2"
    ):
        errors.append("frozen Gemini agent/SkillAuthor routing drift")
    if env.get("runtime_image_status") == "UNOBSERVABLE_PERMISSION_DENIED" and env.get("runtime_image_observable") is not False:
        errors.append("permission-denied runtime image probe cannot be marked observable")
    if env.get("execution_ready") is True and not all(
        bool(env.get(k))
        for k in ("benchmark_python_ready", "harbor_importable", "runtime_image_present", "gemini_credential_present")
    ):
        errors.append("execution-ready state is inconsistent with runtime requirements")
    authority = state.get("authority") or {}
    if any(bool(authority.get(k)) for k in ("problem_gate", "paper_design", "method", "experiment", "p0", "gpu", "full_experiment")):
        errors.append("scout illegally carries downstream authority")
    binding = (state.get("source_bindings") or {}).get("f0_harness") or {}
    if binding.get("sha256") != _sha(F0_HARNESS) or len(str(binding.get("sha256") or "")) != 64:
        errors.append("F0 harness source binding is stale")
    if (state.get("source_bindings") or {}).get("plan_sha256") != build_plan()["plan_sha256"]:
        errors.append("F0 plan source binding is stale")
    runtime_binding = (state.get("source_bindings") or {}).get("runtime_audit")
    if RUNTIME_AUDIT_JSON.exists():
        if not runtime_binding or runtime_binding.get("sha256") != _sha(RUNTIME_AUDIT_JSON):
            errors.append("PA-05 runtime audit source binding is stale")
    elif runtime_binding is not None:
        errors.append("PA-05 runtime audit binding exists without receipt")
    return errors


def write_skill_validation_transfer_scout(
    *,
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    state = build_skill_validation_transfer_scout()
    errors = validate_skill_validation_transfer_scout(state)
    if errors:
        raise ValueError("; ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.PAPER_FIRST_SKILL_VALIDATION_TRANSFER_SCOUT = "
        + json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return state


if __name__ == "__main__":
    print(json.dumps(write_skill_validation_transfer_scout(), ensure_ascii=False, indent=2))
