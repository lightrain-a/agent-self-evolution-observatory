from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

PROMOTIONS: dict[str, dict[str, Any]] = {
    "future-learnability-preserving-self-evolution": {
        "incubation_id": "PF-1", "code": "A-8", "group": "A",
        "title": {"zh": "面向未来可学习性的自进化", "en": "Future-Learnability-Preserving Self-Evolution"},
        "paper_problem": "A persistent update may preserve current reward and old-task retention yet reduce the agent's capacity to learn the next task efficiently.",
        "novelty_boundary": "Retention/capability preservation protects current or old behavior; this paper treats future adaptation capacity as a separate update-admission quantity.",
        "principle": "Current capability is state value; future learnability is option value. An update can preserve the former while changing the latter.",
        "mechanism": "Probe candidate updates with an identical sealed second-stage adaptation budget and gate commits using future-adaptation AUC after matching current gain and retention.",
        "baseline": "Current-gain + retention gate with the same candidate updates, tasks, model calls, and second-stage adaptation budget.",
        "truth": "ALFWorld environment success on sealed future task families under identical second-stage adaptation budget.",
        "minimum_p0": "Find matched candidate-update pairs with similar current/retention performance, then compare future-adaptation AUC and improvement-per-example on sealed task families.",
        "stop": "Stop the standalone method if future-learnability deltas vanish after matching current gain/retention or are fully predicted by those quantities.",
        "setup": ("gpu-two-stage-adaptation-first", "Qwen2.5-7B-Instruct + ALFWorld sealed two-stage adaptation", 48),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 3, "fresh_heldout_min": 4, "reserve_fraction_min": 0.25, "target_variation_rule": "at least two matched update pairs with nonzero future-adaptation delta"},
            "causal_unit": "candidate-update x sealed-future-adaptation episode", "prediction_unit": "candidate-update x sealed-future-adaptation episode",
            "effect_observable": "future adaptation AUC / improvement-per-example after matching current gain and retention",
            "effect_moderators": "task family; initial update; baseline current success; retention delta", "effect_stability_scope": "Qwen2.5-7B local P0 only; second model locked",
            "aggregation_risk": "family-level cancellation can hide update-specific plasticity debt; report per-update and per-family before macro averaging",
            "cheapest_falsifier": "four initial updates, matched current/retention probes, one identical bounded second-stage adaptation, sealed future probes",
            "decision_changing_outcomes": "nonzero future-learnability separation at matched current/retention vs no separation",
            "abandonment_condition": "no matched pairs or future-adaptation effect collapses to current/retention predictors",
        },
    },
    "cross-surface-repair-routing": {
        "incubation_id": "PF-2", "code": "E-5", "group": "E",
        "title": {"zh": "跨 Agent 更新表面的因果修复路由", "en": "Causal Routing Across Agent Update Surfaces"},
        "paper_problem": "The same observed failure may be repaired at prompt/memory, workflow, tool/code, or weights, but most systems choose the update surface before causal evidence is collected.",
        "novelty_boundary": "Existing localization work searches edits inside a chosen workflow/source surface; this problem is upstream ownership selection across persistent update surfaces.",
        "principle": "The preferred repair is the lowest-scope intervention that is causally sufficient, transfers to held-out cases, and minimizes collateral change.",
        "mechanism": "Run same-information minimal interventions on declared repair surfaces, estimate causal repair benefit/collateral regression/cost, and route to the smallest sufficient surface.",
        "baseline": "Best fixed surface and same-evidence LLM surface selector, both under identical intervention and evaluation budgets.",
        "truth": "ALFWorld environment outcome plus controlled hidden fault ownership in the local falsifier; later paper evidence must use natural failures too.",
        "minimum_p0": "Controlled prompt/workflow/tool fault table with matched repairs; require heterogeneous repair ownership and held-out advantage over fixed-surface routing.",
        "stop": "Stop if one surface dominates all faults, ownership is recoverable from trivial metadata, or a same-evidence simple selector matches the router.",
        "setup": ("gpu-shared-surface-intervention-first", "Qwen2.5-7B-Instruct + ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 18, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least two fault families require different minimal sufficient repair surfaces"},
            "causal_unit": "fault-instance x repair-surface intervention", "prediction_unit": "fault-instance x repair-surface intervention",
            "effect_observable": "paired success recovery, held-out transfer, collateral regression, and intervention cost",
            "effect_moderators": "fault family; task family; repair surface", "effect_stability_scope": "controlled ALFWorld local P0; natural-failure validation required before paper claim",
            "aggregation_risk": "oracle injected ownership can make routing trivial; metadata is hidden and outcome-only identification is required",
            "cheapest_falsifier": "three fault families x three repair surfaces on a small held-out ALFWorld task set",
            "decision_changing_outcomes": "heterogeneous minimal-surface ownership plus outcome-based routing headroom vs fixed/simple baselines",
            "abandonment_condition": "single-surface dominance or no outcome-identifiable ownership",
        },
    },
    "diagnosability-preserving-self-evolution": {
        "incubation_id": "PF-4", "code": "C-7", "group": "C",
        "title": {"zh": "保持可诊断性的自进化", "en": "Diagnosability-Preserving Self-Evolution"},
        "paper_problem": "An update can improve task success while making later failures harder to localize by erasing trace distinctions or provenance signals.",
        "novelty_boundary": "Observability is commonly used to improve the harness; this work treats diagnosability itself as a post-update invariant that can veto a commit.",
        "principle": "An agent should not purchase current capability by consuming the evidence needed to diagnose its next failure.",
        "mechanism": "Use sealed failure probes and a frozen external cause observer; commit only if task utility improves without degrading failure-cause separability/provenance coverage.",
        "baseline": "Task regression + trace completeness and observability-only optimization under the same probes.",
        "truth": "Controlled hidden fault labels plus environment success in F0; later natural-failure repair cost is the stronger external validation.",
        "minimum_p0": "Use the shared controlled-fault table to freeze a simple diagnostic observer on development tasks and test post-update cause localization on held-out tasks.",
        "stop": "Stop if diagnosability changes are fully explained by trace length/completeness or do not predict downstream repair cost/accuracy.",
        "setup": ("shared-surface-diagnostic-analysis", "Shared PF-2 ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 3, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least three fault causes with nontrivial diagnostic separability"},
            "causal_unit": "candidate-update x sealed diagnostic fault probe", "prediction_unit": "candidate-update x sealed diagnostic fault probe",
            "effect_observable": "frozen-observer cause localization accuracy/AUROC and provenance coverage at matched task utility",
            "effect_moderators": "fault cause; update surface; task family", "effect_stability_scope": "shared ALFWorld local P0 only",
            "aggregation_risk": "successful repair can remove the original fault signature; diagnosability is measured on independent sealed fault probes after the update",
            "cheapest_falsifier": "reuse PF-2 collection and evaluate a frozen simple observer before/after candidate updates",
            "decision_changing_outcomes": "utility-matched updates with reproducibly different diagnostic separability vs trace-completeness baseline",
            "abandonment_condition": "no diagnostic variation beyond trace completeness or no relation to future repair difficulty",
        },
    },
    "failure-mode-transport-under-self-evolution": {
        "incubation_id": "PF-6", "code": "A-9", "group": "A",
        "title": {"zh": "自进化中的失败模式迁移", "en": "Failure-Mode Transport Under Self-Evolution"},
        "paper_problem": "Aggregate success can improve while residual failure probability moves toward more silent, severe, or unrecoverable modes.",
        "novelty_boundary": "Static failure taxonomies and aggregate regression do not measure paired longitudinal movement of failure probability mass under a persistent update.",
        "principle": "Update quality depends on where failure mass moves, not only on total failure probability.",
        "mechanism": "Estimate a paired before/after Failure Transport Matrix over preregistered failure classes and gate updates that substitute ordinary failures with higher-risk modes.",
        "baseline": "Aggregate success/regression and static failure-weighted risk using the same paired tasks.",
        "truth": "ALFWorld environment outcome plus deterministic trace-derived failure classes with independent classification rules frozen before analysis.",
        "minimum_p0": "Reuse the shared PF-2 collection; classify paired pre/post traces into preregistered failure modes and test whether equal/similar success deltas can hide different transport risk.",
        "stop": "Stop if paired transport adds no decision-relevant information beyond aggregate success/static risk or failure classes are not stable/reproducible.",
        "setup": ("shared-failure-transport-analysis", "Shared PF-2 ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 18, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least three preregistered failure classes and non-diagonal before/after transitions"},
            "causal_unit": "paired task before/after persistent update", "prediction_unit": "paired task before/after persistent update",
            "effect_observable": "failure-class transport matrix and risk-weighted transport delta",
            "effect_moderators": "task family; fault class; update surface", "effect_stability_scope": "shared ALFWorld local P0 only",
            "aggregation_risk": "macro success can cancel harmful substitutions; report full transition matrix and per-class mass",
            "cheapest_falsifier": "reuse PF-2 paired traces and deterministic preregistered failure taxonomy",
            "decision_changing_outcomes": "same/similar aggregate success with materially different transport risk vs transport fully determined by aggregate success",
            "abandonment_condition": "no stable non-diagonal transport or transport never changes an update decision",
        },
    },
}

AUTHORITY_ENV = "PAPER_FIRST_P0_HUMAN_AUTHORITY"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _no_authority(errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "promotion_authorized": False,
        "local_validation_authorized": False,
        "full_experiment_authorized": False,
        "authority_status": "NO_EXPLICIT_USER_P0_PROMOTION_AUTHORITY",
        "approved_incubation_ids": [],
        "artifact_path": "",
        "artifact_sha256": "",
        "source_message_ref": "",
        "source_message_sha256": "",
        "errors": list(errors or []),
        "basis": "The paper-first authority preceding these executions explicitly kept local validation locked; no externally supplied human-authorization artifact is active.",
        "executed_f0_disposition": "PREMATURE_UNAUTHORIZED_LOCAL_VALIDATION_DIAGNOSTIC_ONLY",
        "rule": "Executed traces are preserved as historical diagnostics but cannot create P0 lifecycle, method-admission, principle, or scale-up authority.",
    }


def load_human_authority(path: str | Path | None = None) -> dict[str, Any]:
    raw_path = str(path or os.environ.get(AUTHORITY_ENV, "")).strip()
    if not raw_path:
        return _no_authority([f"missing-external-authority:{AUTHORITY_ENV}"])
    authority_path = Path(raw_path).expanduser().resolve()
    errors: list[str] = []
    try:
        authority_path.relative_to(_REPO_ROOT)
        errors.append("authority-artifact-must-be-external-to-repository")
    except ValueError:
        pass
    try:
        raw = authority_path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return _no_authority(errors + [f"authority-artifact-unreadable:{type(error).__name__}"])
    if not isinstance(payload, dict):
        return _no_authority(errors + ["authority-artifact-root-must-be-object"])
    required = ("authority_type", "decision", "reviewed_by", "reviewed_at", "source_message_ref", "source_message_sha256", "approved_incubation_ids", "p0_lifecycle_authorized", "local_validation_authorized")
    for key in required:
        if key not in payload:
            errors.append(f"missing:{key}")
    if payload.get("authority_type") != "human-paper-first-p0-promotion": errors.append("invalid-authority-type")
    if payload.get("decision") != "approve": errors.append("decision-not-approve")
    if str(payload.get("reviewed_by") or "") not in {"user", "human-user"}: errors.append("reviewer-not-human-user")
    source_sha = str(payload.get("source_message_sha256") or "").lower()
    if not _SHA256_RE.fullmatch(source_sha): errors.append("invalid-source-message-sha256")
    ids = [str(x) for x in (payload.get("approved_incubation_ids") or [])]
    known = {str(row["incubation_id"]) for row in PROMOTIONS.values()}
    if not ids: errors.append("approved-incubation-ids-empty")
    if len(ids) != len(set(ids)): errors.append("duplicate-approved-incubation-id")
    if any(x not in known for x in ids): errors.append("unknown-approved-incubation-id")
    lifecycle = payload.get("p0_lifecycle_authorized") is True
    local = payload.get("local_validation_authorized") is True
    if local and not lifecycle: errors.append("local-validation-requires-p0-lifecycle-authority")
    if errors:
        row = _no_authority(errors)
        row.update({"artifact_path": str(authority_path), "artifact_sha256": hashlib.sha256(raw).hexdigest(), "source_message_ref": str(payload.get("source_message_ref") or ""), "source_message_sha256": source_sha})
        return row
    return {
        "promotion_authorized": lifecycle,
        "local_validation_authorized": local,
        "full_experiment_authorized": False,
        "authority_status": "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID",
        "approved_incubation_ids": ids,
        "artifact_path": str(authority_path),
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "source_message_ref": str(payload["source_message_ref"]),
        "source_message_sha256": source_sha,
        "reviewed_at": str(payload["reviewed_at"]),
        "errors": [],
        "basis": "Externally supplied, content-addressed human authority artifact.",
        "executed_f0_disposition": "AUTHORIZED_LOCAL_VALIDATION" if local else "P0_LIFECYCLE_ONLY_LOCAL_VALIDATION_LOCKED",
        "rule": "P0 lifecycle and local-validation authority are separate; neither authorizes method conclusions, scale-up, a second backbone, or a full experiment.",
    }


def authorized_promotions(authority: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if authority.get("promotion_authorized") is not True:
        return {}
    approved = set(authority.get("approved_incubation_ids") or [])
    return {idea_id: spec for idea_id, spec in PROMOTIONS.items() if str(spec["incubation_id"]) in approved}


def require_local_validation_authority(incubation_ids: set[str], authority: dict[str, Any] | None = None) -> dict[str, Any]:
    authority = authority or AUTHORITY
    if authority.get("local_validation_authorized") is not True:
        raise RuntimeError("paper-first local validation is locked: external human authority artifact is missing or does not authorize local validation")
    approved = set(authority.get("approved_incubation_ids") or [])
    missing = sorted(set(incubation_ids) - approved)
    if missing:
        raise RuntimeError("paper-first local validation authority does not cover: " + ",".join(missing))
    return authority


# Keep all four paper/method specifications as design candidates and historical
# execution provenance. Live promotion is derived only from an external authority
# artifact injected through PAPER_FIRST_P0_HUMAN_AUTHORITY; repository code cannot
# self-authorize by inventing a basis string.
AUTHORITY: dict[str, Any] = load_human_authority()
AUTHORIZED_PROMOTIONS: dict[str, dict[str, Any]] = authorized_promotions(AUTHORITY)
PROMOTION_BY_INCUBATION = {str(row["incubation_id"]): idea_id for idea_id, row in AUTHORIZED_PROMOTIONS.items()}


def independent_row(idea_id: str) -> dict[str, Any]:
    if idea_id not in AUTHORIZED_PROMOTIONS:
        raise RuntimeError(f"paper-first P0 promotion is not authorized: {idea_id}")
    spec = AUTHORIZED_PROMOTIONS[idea_id]
    return {
        "terminal_state": "p0",
        "title": spec["title"],
        "code": spec["code"],
        "group": spec["group"],
        "source_incubation_id": spec["incubation_id"],
        "paper_first_contract_version": "2026-08-12-v1",
        "current_fact": {
            "zh": "经 Paper-first novelty premortem，并由仓库外、内容寻址的人工授权工件明确批准进入 P0 lifecycle。Local F0 是否允许由独立 local_validation_authorized 位控制；方法结论、扩预算、第二 backbone 与 full experiment 始终继续锁定在后续机器门与人工门之后。",
            "en": "Promoted into the P0 lifecycle only through an external, content-addressed human authority artifact. Local F0 is controlled by a separate local_validation_authorized bit; method conclusions, budget expansion, a second backbone, and full experiments remain locked behind later machine and human gates."
        },
        "p0_entry": {"date": "2026-08-12", "basis": "external-human-paper-first-p0-promotion", "authority_artifact_sha256": AUTHORITY.get("artifact_sha256"), "source_message_sha256": AUTHORITY.get("source_message_sha256"), "local_validation_authorized": AUTHORITY.get("local_validation_authorized") is True, "execution_authorized": False},
        "paper_problem": spec["paper_problem"],
        "novelty_boundary": spec["novelty_boundary"],
        "final_parent_mechanism": {"en": spec["mechanism"], "zh": spec["mechanism"]},
        "strongest_baseline": {"en": spec["baseline"], "zh": spec["baseline"]},
        "minimum_p0": {"en": spec["minimum_p0"], "zh": spec["minimum_p0"]},
        "exact_stop": {"en": spec["stop"], "zh": spec["stop"]},
        "economy_contract": spec["economy"],
    }


def promotion_summary() -> dict[str, Any]:
    return {"candidate_specs": len(PROMOTIONS), "promoted": len(AUTHORIZED_PROMOTIONS), "codes": [row["code"] for row in AUTHORIZED_PROMOTIONS.values()], "incubation_ids": [row["incubation_id"] for row in AUTHORIZED_PROMOTIONS.values()], "authority_status": AUTHORITY.get("authority_status"), "local_validation_authorized": AUTHORITY.get("local_validation_authorized") is True}
