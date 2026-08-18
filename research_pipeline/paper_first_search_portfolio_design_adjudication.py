from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .dead_end_failure_layers import (
    CLOSURE_LAYERS,
    MEMORY_CLASS_BY_CLOSURE_LAYER,
    PROBLEM_NOVELTY,
    SCIENTIFIC_FAILURE_LAYERS,
    audit_closed_row_layer,
    classify_readjudication,
    normalize_closed_row,
    problem_novelty_classification,
    summarize_closure_layers,
    summarize_scientific_failure_layers,
)
from .paper_first_shadow_near_miss_preflight import build_shadow_near_miss_preflight, compile_shadow_dead_end_rows
from .principle_adjudication import audit_dead_end_counter_explanation
from .positive_residual_assets import build_positive_residual_asset_registry

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.js"
SHADOW_PORTFOLIO_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-state.json"
SHADOW_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-queue-shadow.json"
PRINCIPLE_READJUDICATION_GLOB = "*principle-readjudication-*.json"
FRESH_PHENOMENON_SUPPORT_HOLD_GLOB = "*fresh-phenomenon-support-hold-*.json"
CONTINUATION_HOLD_GLOB = "*continuation-hold-*.json"

PRIMARY_SOURCES: dict[str, list[dict[str, str]]] = {
    "SP-09": [
        {
            "ref": "arXiv:2602.12430",
            "title": "Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward",
            "url": "https://arxiv.org/abs/2602.12430",
            "boundary_role": "Direct governance collision: four-stage verification gates map acquisition provenance to four graduated deployment-permission tiers with runtime trust evolution; deployment governance cannot be claimed as the new object.",
        },
        {
            "ref": "arXiv:2607.01136",
            "title": "Skills Are Not Islands: Measuring Dependency and Risk in Agent Skill Supply Chains",
            "url": "https://arxiv.org/abs/2607.01136",
            "boundary_role": "Dependency- and workflow-level risk is already a first-class skill-supply-chain object; single-skill inspection is explicitly shown insufficient.",
        },
        {
            "ref": "arXiv:2608.09732",
            "title": "ColluSkill: Adversarial Cross-Skill Composition for Evading Agent Skill Scanners",
            "url": "https://arxiv.org/abs/2608.09732",
            "boundary_role": "ChainGuard already analyzes candidate plus installed skills, dependencies, artifact flows, capability composition, and downstream behavior.",
        },
        {
            "ref": "arXiv:2608.09577",
            "title": "ElasticBack: Stealthy Conditional Backdoor in LLM-Agent Skills via Coupled Trigger-Rule Optimization",
            "url": "https://arxiv.org/abs/2608.09577",
            "boundary_role": "Conditional dormant trigger-risk with preserved clean accuracy and cross-model transfer is already directly demonstrated.",
        },
        {
            "ref": "arXiv:2605.30723",
            "title": "Skill is Not One-Size-Fits-All: Model-Aware Skill Alignment for LLM Agents",
            "url": "https://arxiv.org/abs/2605.30723",
            "boundary_role": "Target-backbone dependence of skill benefit/harm and model-conditioned skill adaptation are already occupied.",
        },
        {
            "ref": "arXiv:2608.10538",
            "title": "SKILLER: Language-Level Reinforcement Learning for Reusable Skill Extraction in Small Language Models",
            "url": "https://arxiv.org/abs/2608.10538",
            "boundary_role": "Executor-specific evolved-skill utility is directly optimized and empirically measured.",
        },
    ],
    "SP-15": [
        {
            "ref": "arXiv:2608.08640",
            "title": "SkillReason: Reasoning-Enhanced Agent Skill Retrieval for Implicit User Requests",
            "url": "https://arxiv.org/abs/2608.08640",
            "boundary_role": "Direct collision with concise underspecified implicit requests and query-only inference without autoregressive CoT; also reports a distinction between top-rank retrieval and complete capability coverage.",
        },
        {
            "ref": "arXiv:2606.18051",
            "title": "Compositional Skill Routing for LLM Agents: Decompose, Retrieve, and Compose",
            "url": "https://arxiv.org/abs/2606.18051",
            "boundary_role": "Task decomposition and multi-skill composition are already formalized; decomposition quality is identified as a primary retrieval bottleneck.",
        },
        {
            "ref": "arXiv:2607.06283",
            "title": "Task Decomposition-Guided Reranking for Adaptive Agent Skill Retrieval",
            "url": "https://arxiv.org/abs/2607.06283",
            "boundary_role": "Task/skill decomposition plus structured reranking already targets ambiguous skill selection.",
        },
        {
            "ref": "arXiv:2606.03565",
            "title": "Skill Is Not Document: A Query-Conditional Benchmark and Two-Stage Retriever for LLM Agent Skill Routing",
            "url": "https://arxiv.org/abs/2606.03565",
            "boundary_role": "Query-conditional joint skill-set compatibility is already a supervised retrieval object rather than independent relevance alone.",
        },
        {
            "ref": "arXiv:2606.10388",
            "title": "SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval",
            "url": "https://arxiv.org/abs/2606.10388",
            "boundary_role": "Query-specific same-capability ambiguity and procedural execution risk are already measured and resolved.",
        },
        {
            "ref": "arXiv:2606.03056",
            "title": "SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale",
            "url": "https://arxiv.org/abs/2606.03056",
            "boundary_role": "Inter-skill dependency/conflict/specialization structure is already exposed as a retrieval-time object.",
        },
        {
            "ref": "arXiv:2605.05726",
            "title": "SkillRet: A Large-Scale Benchmark for Skill Retrieval in LLM Agents",
            "url": "https://arxiv.org/abs/2605.05726",
            "boundary_role": "Large-scale realistic skill retrieval and query-signal limitations are already benchmarked with disjoint skill pools.",
        },
        {
            "ref": "arXiv:2607.19801",
            "title": "CIR at iKAT SCAI 2026: Exploring Clarification Need Prediction in Agentic Conversational Search",
            "url": "https://arxiv.org/abs/2607.19801",
            "boundary_role": "Generic ambiguity handling via clarification-need prediction is a mature same-information baseline for any proposed abstain/clarify policy.",
        },
    ],
}

SHADOW_MEMORY_MAINTENANCE_POLICY = {
    "terminal_run_ingestion_is_zero_authority_search_control": True,
    "terminal_run_need_not_remain_public_latest": True,
    "machine_only_blocks_do_not_become_persistent_semantic_dead_ends": True,
    "support_unavailable_is_a_reopenable_hold_not_scientific_failure": True,
    "lane_contract_failure_is_a_reopenable_hold_not_dead_end": True,
    "unresolved_exact_reduction_test_is_a_hold_not_dead_end": True,
    "persistent_dead_end_requires_positive_counter_explanation": True,
    "search_control_closure_is_not_scientific_dead_end": True,
    "only_core_principle_enters_shadow_dead_end_memory": True,
    "holds_live_only_in_shadow_search_memory": True,
    "closed_basin_must_name_closure_layer": True,
    "scientific_closed_basin_must_use_canonical_failure_layer": True,
    "problem_novelty_stop_is_upstream_not_experimental_failure_layer": True,
    "scoped_closed_basin_is_not_automatically_principle_stop": True,
    "principle_stop_does_not_imply_benchmark_level_dead_end": True,
    "principle_stop_requires_explicit_stop_class_or_broader_falsification": True,
    "canonical_generator_and_queue_untouched": True,
}


BASE_SHADOW_DEAD_END_MEMORY = {
    # Legacy constant name retained while the persisted state is split below into
    # shadow_search_memory (all exact formulation closures/HOLDs) and
    # shadow_dead_end_memory (core_principle only).
    "memory_id": "shadow-paper-design-search-memory-20260818-v4",
    "scientific_authority": False,
    "live_source_coverage_effect": False,
    "cannot_mutate_canonical_generator_or_queue": True,
    "search_escape_required": True,
    "blocked_objects": [
        {
            "source_candidate_id": "SP-09",
            "basin": "skill-deployment-governance-contextual-acceptance",
            "avoid": [
                "trust tiers or graduated deployment permission as the novelty",
                "context-aware scanner followed by install/update/block/escalate policy as the novelty",
                "model-conditioned skill utility or risk as the novelty",
                "generic contextual constrained or risk-sensitive scalar acceptance",
            ],
            "strongest_reduction": "generic contextual constrained governance using the same model, trigger, workflow, security, and utility information",
            "current_source_refs": ["arXiv:2602.12430", "arXiv:2607.01136", "arXiv:2608.09732", "arXiv:2605.30723"],
            "search_closure_certified": True,
            "dead_end_certified": False,
            **problem_novelty_classification(basis="historical-paper-design-collision-re-review-2026-08-18"),
            "counter_explanation": {
                "type": "SAME_INFORMATION_REDUCTION",
                "statement": "The proposed acceptance object is expressible as contextual constrained governance when the same model/trigger/workflow/security/utility observations are available.",
                "opposite_prediction": "A generic contextual constrained policy with identical information can reproduce the proposed install/update/block/escalate decisions, so no standalone irreducible acceptance principle is required.",
                "opposite_principle": "Contextual governance is sufficient unless an ex-ante non-separability or impossibility residual survives same-information control.",
                "opposite_search_seed": "Search for identical-information skill cases whose correct governance actions are provably non-separable for generic contextual constrained policies.",
                "scope": "SP-09 paper-problem formulation under the reviewed primary-source evidence",
                "same_information_or_scope_matched": True,
                "evidence_refs": ["arXiv:2602.12430", "arXiv:2607.01136", "arXiv:2608.09732", "arXiv:2605.30723"],
                "alternative_explanations_ruled_out": ["the proposal is not merely waiting for executable support", "the collision is not a provider/runtime failure", "the same-information governance baseline already receives the candidate's stated context variables"],
                "positive_support": True,
                "same_information_reduction_verified": True,
                "reopen_condition": "Current primary evidence supports an ex-ante non-separability or impossibility prediction for the same skill under identical model/trigger/workflow/security/utility information that generic contextual governance cannot express."
            },
            "reopen_only_if": "Current primary evidence supports an ex-ante non-separability or impossibility prediction for the same skill under identical model/trigger/workflow/security/utility information that generic contextual governance cannot express.",
            "scientific_authority": False
        }
    ],
    "hold_objects": [
        {
            "source_candidate_id": "SP-15",
            "basin": "implicit-query-decomposition-skill-routing",
            "avoid": [
                "implicit queries are harder",
                "task decomposition improves skill retrieval",
                "top-rank relevance differs from complete capability coverage",
                "query-conditional multi-skill compatibility alone",
                "generic abstention, uncertainty, or clarification policy",
            ],
            "dead_end_certified": False,
            "memory_class": "REOPENABLE_HOLD",
            "hold_reason": "The revised sufficient-skill-set identifiability problem still requires provenance-audited query-level support and therefore has not earned a principle dead-end or principle pass.",
            "reopen_only_if": "A new provenance-audited query-level unit shows that the same observable or information-equivalent query is compatible with multiple task semantics requiring incompatible sufficient skill sets, and a generic partial-identification/clarification baseline using the same information cannot absorb the claim.",
            "scientific_authority": False
        }
    ],
}


def _state_search_memory(state: dict[str, Any]) -> dict[str, Any]:
    """Read canonical search-control memory with legacy dead-end-memory fallback."""
    memory = state.get("shadow_search_memory") if isinstance(state, dict) else None
    if isinstance(memory, dict) and memory:
        return memory
    legacy = state.get("shadow_dead_end_memory") if isinstance(state, dict) else None
    return legacy if isinstance(legacy, dict) else {}


def _closed_objects(memory: dict[str, Any]) -> list[dict[str, Any]]:
    rows = memory.get("closed_objects") if isinstance(memory, dict) else None
    if not isinstance(rows, list):
        rows = memory.get("blocked_objects") if isinstance(memory, dict) else None
    return [row for row in (rows or []) if isinstance(row, dict)]


def _canonical_search_memory(memory: dict[str, Any]) -> dict[str, Any]:
    """Persist search-control closures/HOLDs without calling them scientific dead ends."""
    out = json.loads(json.dumps(memory, ensure_ascii=False))
    out["memory_id"] = "shadow-paper-design-search-control-memory-20260818-v4"
    closed = []
    for source in _closed_objects(out):
        row = dict(source)
        row["search_closure_certified"] = True
        # Legacy field is scientific-dead-end semantics only in canonical state.
        row["dead_end_certified"] = bool(row.get("failure_layer") == "core_principle" and row.get("principle_update_allowed") is True)
        closed.append(row)
    out["closed_objects"] = closed
    out.pop("blocked_objects", None)
    out["search_control_only"] = True
    out["closed_object_count"] = len(out["closed_objects"])
    out["scientific_authority"] = False
    out["cannot_mutate_canonical_generator_or_queue"] = True
    return out


def _principle_dead_end_projection(search_memory: dict[str, Any]) -> dict[str, Any]:
    rows = [
        dict(row)
        for row in _closed_objects(search_memory)
        if row.get("failure_layer") == "core_principle"
        and row.get("principle_update_allowed") is True
        and row.get("search_closure_certified") is True
    ]
    return {
        "memory_id": "shadow-paper-design-core-principle-dead-end-memory-20260818-v1",
        "scientific_authority": False,
        "persistent_dead_end_authority_scope": "core_principle-only",
        "only_principle_stop_may_enter_persistent_dead_end_memory": True,
        "blocked_objects": rows,
        "hold_objects": [],
        "principle_dead_end_count": len(rows),
        "scientific_authority_for_live_discovery": False,
        "cannot_mutate_canonical_generator_or_queue": True,
    }


def _prior_current_source_hard_veto_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = _state_search_memory(prior)
    rows = []
    for row in _closed_objects(memory) + list(memory.get("hold_objects") or []):
        if not isinstance(row, dict) or not str(row.get("basin") or "").startswith("current-source-hard-veto-"):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("strongest_reduction") or "").strip() or not row.get("current_source_refs") or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
    return rows


def _prior_semantic_block_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = _state_search_memory(prior)
    rows = []
    for row in _closed_objects(memory) + list(memory.get("hold_objects") or []):
        basin = str(row.get("basin") or "") if isinstance(row, dict) else ""
        if not basin.startswith(("semantic-exact-reduction-", "semantic-lane-contract-")):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
    return rows


def _prior_near_miss_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = _state_search_memory(prior)
    rows = []
    for row in _closed_objects(memory) + list(memory.get("hold_objects") or []):
        basin = str(row.get("basin") or "") if isinstance(row, dict) else ""
        if not basin.startswith("near-miss-"):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
    return rows


def _continuation_hold_rows(paths: list[Path] | None = None) -> list[dict[str, Any]]:
    """Load provenance-bound post-transaction holds without turning them into dead ends.

    A continuation artifact is produced only after a separate reviewer, replay, support
    inventory, or source-asset audit has already finished.  Its `persistent_hold` row is
    search-control memory: it can stop the *current formulation/execution route* and state
    a reopen condition, but it cannot grant or revoke scientific authority and it can
    never become a PRINCIPLE_DEAD_END merely because it is persisted here.
    """
    candidates = paths if paths is not None else sorted((PROJECT_ROOT / "generated").glob(CONTINUATION_HOLD_GLOB))
    rows: list[dict[str, Any]] = []
    for path in candidates:
        payload = _load_json(path)
        if payload.get("scientific_authority") is not False:
            continue
        authority = payload.get("authority") or {}
        if any(bool(value) for value in authority.values()):
            continue
        raw = payload.get("persistent_hold") or {}
        if not isinstance(raw, dict) or raw.get("scientific_authority") is not False or raw.get("dead_end_certified") is not False:
            continue
        row = dict(raw)
        basin = str(row.get("basin") or "")
        memory_class = str(row.get("memory_class") or "")
        if memory_class == "FORMULATION_HOLD":
            if not basin.startswith("semantic-lane-contract-") or not str(row.get("lane_contract_reason") or "").strip():
                continue
        elif memory_class == "REOPENABLE_HOLD":
            if not basin.startswith("near-miss-terminal-support-hold-") or not str(row.get("required_unit") or "").strip():
                continue
        else:
            continue
        if not str(row.get("source_candidate_id") or "").strip() or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip():
            continue
        try:
            artifact_ref = str(path.relative_to(PROJECT_ROOT))
        except ValueError:
            artifact_ref = str(path)
        row["source_hold_artifact"] = artifact_ref
        row["source_hold_artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        row["scientific_authority"] = False
        row["dead_end_certified"] = False
        rows.append(row)
    return rows


def _terminal_support_hold_rows(preflight: dict[str, Any] | None, *, run_id: str, stage_manifest_sha256: str) -> list[dict[str, Any]]:
    rows = []
    for row in (preflight or {}).get("rows") or []:
        if not isinstance(row, dict) or str(row.get("disposition") or "") != "HOLD_SUPPORT_UNAVAILABLE":
            continue
        candidate_id = str(row.get("candidate_id") or "").strip()
        title = " ".join(str(row.get("title") or "").split())[:300]
        required_unit = " ".join(str(row.get("required_unit") or "").split())[:1600]
        asset_audit = " ".join(str(row.get("asset_audit") or "").split())[:1800]
        reopen_only_if = " ".join(str(row.get("reopen_only_if") or "").split())[:1600]
        refs = sorted({str(ref) for ref in row.get("primary_refs") or [] if str(ref).startswith("arXiv:")})
        if not candidate_id or not required_unit or not asset_audit or not reopen_only_if or not refs:
            continue
        signature = hashlib.sha256(json.dumps({"required_unit": required_unit, "primary_refs": refs}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        rows.append({
            "source_candidate_id": candidate_id,
            "basin": f"near-miss-terminal-support-hold-{signature}",
            "title": title,
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
            "required_unit": required_unit,
            "evidence_basis": refs,
            "strongest_reduction": "the proposed residual remains unsupported until the frozen same-information falsifier can be executed on released or provenance-audited units",
            "reason": asset_audit,
            "avoid": [
                f"re-proposing the unsupported problem object without the required released unit: {title}",
                "manufacturing synthetic support that bakes the candidate mechanism into the data",
                "treating absence of released matched units as scientific evidence for or against the candidate",
            ],
            "reopen_only_if": reopen_only_if,
            "source_run_id": run_id,
            "source_stage_manifest_sha256": stage_manifest_sha256,
            "dead_end_certified": False,
            "memory_class": "REOPENABLE_HOLD",
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": False,
        })
    return rows


def _terminal_evidence_hold_rows(plan: dict[str, Any] | None, *, run_id: str, stage_manifest_sha256: str, fallback_primary_refs: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    """Persist terminal evidence-acquisition asset/support holds as reopenable memory.

    Evidence acquisition is newer than the legacy problem-falsifier preflight. A
    source-specific WAIT must survive terminal publication just like a legacy
    support-unavailable receipt, but it remains explicitly non-dead-end.
    """
    rows: list[dict[str, Any]] = []
    fallback_primary_refs = fallback_primary_refs or {}
    terminal_statuses = {
        "WAIT_PRIMARY_ASSET_RELEASE": "SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE",
        "HOLD_SUBSTRATE_UNAVAILABLE": "SUBSTRATE_UNAVAILABLE_FOR_FROZEN_FALSIFIER",
        "HOLD_SUBSTRATE_BUDGET_INFEASIBLE": "SUBSTRATE_BUDGET_INFEASIBLE_FOR_FROZEN_FALSIFIER",
    }
    for entry in (plan or {}).get("entries") or []:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("status") or "")
        support_status = terminal_statuses.get(status)
        if not support_status:
            continue
        candidate_id = str(entry.get("candidate_id") or "").strip()
        title = " ".join(str(entry.get("title") or "").split())[:300]
        required_unit = " ".join(str(entry.get("frozen_falsifier_expression") or "").split())[:1800]
        reason = " ".join(str(entry.get("review_feedback") or ((entry.get("substrate_preflight") or {}).get("reason")) or "").split())[:2200]
        refs = sorted({str(ref) for ref in (entry.get("source_refs") or fallback_primary_refs.get(candidate_id) or []) if str(ref).startswith("arXiv:")})
        if not candidate_id or not required_unit or not reason or not refs:
            continue
        reopen = (
            "Reopen only when the source-specific/released assets required by the frozen falsifier become available with provenance sufficient to execute the same scientific object, "
            "or when an independently reviewed operationalization proves equivalent without changing the frozen prediction, same-information baseline, or causal unit."
        )
        signature = hashlib.sha256(json.dumps({"candidate_id": candidate_id, "required_unit": required_unit, "primary_refs": refs, "status": status}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        rows.append({
            "source_candidate_id": candidate_id,
            "basin": f"near-miss-terminal-support-hold-{signature}",
            "title": title,
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "support_status": support_status,
            "required_unit": required_unit,
            "evidence_basis": refs,
            "strongest_reduction": "the proposed residual remains unresolved until the frozen same-information falsifier can be executed on source-faithful or independently equivalent assets",
            "reason": reason,
            "avoid": [
                f"re-proposing the unsupported problem object without resolving its frozen asset dependency: {title}",
                "substituting a locally invented, randomly initialized, differently trained, or outcome-tuned asset for the source-specific scientific object",
                "treating missing source assets as scientific evidence for or against the proposed residual",
            ],
            "reopen_only_if": reopen,
            "source_run_id": run_id,
            "source_stage_manifest_sha256": stage_manifest_sha256,
            "hold_origin": "bounded-evidence-acquisition",
            "dead_end_certified": False,
            "memory_class": "REOPENABLE_HOLD",
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": False,
        })
    return rows


def _run_formulation_primary_refs(run_root: Path) -> dict[str, list[str]]:
    refs: dict[str, set[str]] = {}
    for path in sorted(run_root.glob("formulate-p*.json")):
        payload = _load_json(path)
        for bucket in ("candidates", "reduction_pending", "rejected"):
            for outer in payload.get(bucket) or []:
                if not isinstance(outer, dict):
                    continue
                candidate = outer.get("candidate") or outer
                cid = str(outer.get("candidate_id") or candidate.get("candidate_id") or "").strip()
                evidence = candidate.get("empirical_evidence") or {}
                values = {str((evidence.get(key) or {}).get("ref") or "") for key in ("source_a", "source_b")}
                values = {value for value in values if value.startswith("arXiv:")}
                if cid and values:
                    refs.setdefault(cid, set()).update(values)
    return {key: sorted(values) for key, values in refs.items()}


def _principle_readjudication_rows(paths: list[Path] | None = None) -> list[dict[str, Any]]:
    candidates = paths if paths is not None else sorted((PROJECT_ROOT / "generated").glob(PRINCIPLE_READJUDICATION_GLOB))
    rows: list[dict[str, Any]] = []
    for path in candidates:
        payload = _load_json(path)
        if payload.get("principle_dead_end_certified") is not True:
            continue
        diagnosis = payload.get("principle_diagnosis") or {}
        counter = diagnosis.get("counter_explanation") or {}
        audit = audit_dead_end_counter_explanation(counter)
        if audit.get("passed") is not True:
            continue
        candidate_id = str(payload.get("candidate_id") or "").strip()
        title = str(payload.get("title") or "").strip()
        scope = str(payload.get("dead_end_scope") or counter.get("scope") or "").strip()
        if not candidate_id or not scope:
            continue
        signature = hashlib.sha256(json.dumps({"candidate_id": candidate_id, "scope": scope, "statement": counter.get("statement")}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        evidence_refs = [str(ref) for ref in counter.get("evidence_refs") or [] if str(ref)]
        primary_refs = sorted({ref for ref in evidence_refs if ref.startswith("arXiv:")})
        reopen = str(counter.get("reopen_condition") or "").strip()
        try:
            artifact_ref = str(path.relative_to(PROJECT_ROOT))
        except ValueError:
            artifact_ref = str(path)
        closure = payload.get("fresh_phenomenon_closure") or {}
        closure_row: dict[str, Any] = {}
        if isinstance(closure, dict) and closure:
            closure_ref = str(closure.get("source_ref") or "").strip()
            closure_hashes = sorted({str(value).strip().lower() for value in closure.get("closed_evidence_sha256") or [] if re.fullmatch(r"[0-9a-f]{64}", str(value).strip().lower())})
            closure_scope = " ".join(str(closure.get("closure_scope") or "").split())
            if closure_ref.startswith("arXiv:") and closure_hashes and closure_scope and closure.get("scientific_authority") is False:
                closure_row = {
                    "source_ref": closure_ref,
                    "closed_evidence_sha256": closure_hashes,
                    "closure_scope": closure_scope[:1200],
                    "source_readjudication_artifact": artifact_ref,
                    "scientific_authority": False,
                }
        asset = payload.get("opposite_search_asset_evidence") or {}
        asset_row: dict[str, Any] = {}
        if isinstance(asset, dict) and asset:
            asset_ref = str(asset.get("asset_ref") or "").strip()
            source_sha = str(asset.get("source_sha256") or "").strip().lower()
            manifest_file_sha = str(asset.get("asset_manifest_file_sha256") or "").strip().lower()
            commit = str(asset.get("commit") or "").strip().lower()
            manifest_artifact = str(asset.get("asset_manifest_artifact") or "").strip()
            facts = [" ".join(str(value or "").split()) for value in asset.get("empirical_facts") or [] if str(value or "").strip()]
            if asset_ref.startswith("first-party-asset:") and re.fullmatch(r"[0-9a-f]{64}", source_sha) and re.fullmatch(r"[0-9a-f]{64}", manifest_file_sha) and re.fullmatch(r"[0-9a-f]{40}", commit) and manifest_artifact.startswith("generated/") and str(asset.get("primary_url") or "").startswith("https://") and facts:
                asset_row = {
                    "asset_ref": asset_ref,
                    "title": str(asset.get("title") or title).strip(),
                    "primary_url": str(asset.get("primary_url") or "").strip(),
                    "source_sha256": source_sha,
                    "asset_manifest_artifact": manifest_artifact,
                    "asset_manifest_file_sha256": manifest_file_sha,
                    "commit": commit,
                    "empirical_facts": facts[:8],
                    "source_readjudication_artifact": artifact_ref,
                    "search_active": asset.get("search_active") is not False,
                    "search_closed_by": str(asset.get("search_closed_by") or "").strip(),
                    "search_closed_by_sha256": str(asset.get("search_closed_by_sha256") or "").strip().lower(),
                    "search_closed_reason": str(asset.get("search_closed_reason") or "").strip(),
                    "scientific_authority": False,
                }
        failure_layer = classify_readjudication(payload, artifact_ref)
        rows.append({
            "source_candidate_id": candidate_id,
            "basin": f"principle-readjudication-{signature}",
            "search_primitive": str(payload.get("search_primitive") or ""),
            "title": title,
            "avoid": [
                f"re-proposing the certified scoped closure without satisfying its reopen condition: {title}",
                "using the negative experiment metric alone as the reason for a scientific dead end",
                "discarding the opposite principle/search seed instead of testing its fresh-evidence boundary",
            ],
            "strongest_reduction": str(counter.get("statement") or ""),
            "current_source_refs": primary_refs,
            "evidence_basis": evidence_refs,
            "problem_text": scope,
            "reason": str((payload.get("scientific_interpretation") or {}).get("safe_claim") or counter.get("statement") or ""),
            "reopen_only_if": reopen,
            "search_closure_certified": True,
            "dead_end_certified": failure_layer.get("failure_layer") == "core_principle",
            **failure_layer,
            "counter_explanation": dict(counter),
            "source_readjudication_artifact": artifact_ref,
            "opposite_search_asset_evidence": asset_row,
            "fresh_phenomenon_closure": closure_row,
            "search_control_scope": "prompt-inversion-prior; semantic machine block only when a typed search primitive is present",
            "scientific_authority": False,
        })
    return rows


def _fresh_phenomenon_support_hold_rows(paths: list[Path] | None = None) -> list[dict[str, Any]]:
    """Compile provenance-bound evidence-level support holds into reopenable memory.

    These rows are operational search control only. They pause one exact primary
    evidence object while required first-party support is unavailable; they are
    never scientific dead ends and cannot authorize a Problem/Method/P0/GPU step.
    The existing support-release watch may later request a re-audit, but release
    discovery alone never clears the hold automatically.
    """
    candidates = paths if paths is not None else sorted((PROJECT_ROOT / "generated").glob(FRESH_PHENOMENON_SUPPORT_HOLD_GLOB))
    rows: list[dict[str, Any]] = []
    for path in candidates:
        payload = _load_json(path)
        if str(payload.get("status") or "") not in {"HOLD_SUPPORT", "HOLD_SUPPORT_UNAVAILABLE", "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT"}:
            continue
        if payload.get("scientific_authority") is not False:
            continue
        ref = str(payload.get("source_ref") or "").strip()
        sha = str(payload.get("phenomenon_id") or payload.get("evidence_sha256") or "").strip().lower()
        required = " ".join(str(payload.get("required_unit") or "").split())
        reopen = " ".join(str(payload.get("reopen_only_if") or "").split())
        audit_artifact = str(payload.get("support_audit_artifact") or "").strip()
        audit_sha = str(payload.get("support_audit_sha256") or "").strip().lower()
        if not ref.startswith("arXiv:") or not re.fullmatch(r"[0-9a-f]{64}", sha) or not required or not reopen:
            continue
        if not audit_artifact.startswith("generated/") or not re.fullmatch(r"[0-9a-f]{64}", audit_sha):
            continue
        audit_path = PROJECT_ROOT / audit_artifact
        if not audit_path.exists() or hashlib.sha256(audit_path.read_bytes()).hexdigest() != audit_sha:
            continue
        try:
            artifact_ref = str(path.relative_to(PROJECT_ROOT))
        except ValueError:
            artifact_ref = str(path)
        signature = hashlib.sha256(json.dumps({"ref": ref, "sha": sha, "required": required}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        rows.append({
            "source_candidate_id": str(payload.get("candidate_id") or "").strip() or f"fresh-hold-{sha[:12]}",
            "basin": f"fresh-phenomenon-support-hold-{signature}",
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "memory_class": "REOPENABLE_HOLD",
            "dead_end_certified": False,
            "strongest_reduction": "support unavailable; no scientific reduction authorized",
            "current_source_refs": [ref],
            "evidence_basis": [ref, f"repo:{audit_artifact}#sha256={audit_sha}"],
            "reason": " ".join(str(payload.get("reason") or payload.get("why_hold") or required).split())[:1600],
            "reopen_only_if": reopen[:1600],
            "required_unit": required[:1600],
            "fresh_phenomenon_hold": {
                "source_ref": ref,
                "evidence_sha256": sha,
                "support_audit_artifact": audit_artifact,
                "support_audit_sha256": audit_sha,
                "scientific_authority": False,
            },
            "source_hold_artifact": artifact_ref,
            "scientific_authority": False,
        })
    return rows


def _shadow_dead_end_memory(portfolio: dict[str, Any], near_miss_state: dict[str, Any] | None = None, prior_hard_veto_rows: list[dict[str, Any]] | None = None, prior_semantic_rows: list[dict[str, Any]] | None = None, prior_near_miss_rows: list[dict[str, Any]] | None = None, extra_near_miss_rows: list[dict[str, Any]] | None = None, principle_readjudication_rows: list[dict[str, Any]] | None = None, fresh_phenomenon_support_hold_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    memory = json.loads(json.dumps(BASE_SHADOW_DEAD_END_MEMORY, ensure_ascii=False))
    latest = portfolio.get("latest_run") or {}
    inherited = _prior_current_source_hard_veto_rows() if prior_hard_veto_rows is None else [dict(row) for row in prior_hard_veto_rows if isinstance(row, dict)]
    hard_by_basin = {str(row.get("basin")): row for row in inherited if str(row.get("basin") or "").startswith("current-source-hard-veto-") and row.get("scientific_authority") is False}
    added = 0
    for row in latest.get("candidates") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("current_source_status") or "") != "complete" or str(row.get("current_source_verdict") or "") != "BLOCK" or str(row.get("current_source_reduction_class") or "") != "VALID_HARD_VETO":
            continue
        strongest = " ".join(str(row.get("current_source_strongest_reduction") or "").split())[:800]
        reason = " ".join(str(row.get("current_source_reason") or "").split())[:1200]
        refs = sorted({str(ref) for ref in row.get("current_source_source_refs") or [] if str(ref).startswith("arXiv:")})
        if not strongest or not reason or not refs:
            continue
        candidate_id = str(row.get("candidate_id") or "").strip()
        primitive = str(row.get("search_primitive") or "").strip()
        title = " ".join(str(row.get("title") or "").split())[:300]
        signature = hashlib.sha256(json.dumps({"strongest_reduction": strongest, "source_refs": refs}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        basin = f"current-source-hard-veto-{signature}"
        if basin not in hard_by_basin:
            added += 1
        hard_by_basin[basin] = {
            "source_candidate_id": candidate_id,
            "basin": basin,
            "search_primitive": primitive,
            "avoid": [
                f"paraphrase-only variants of: {title}",
                f"problem formulations exactly reducible to: {strongest}",
                "domain- or terminology-swapped variants that do not add an ex-ante same-information residual beyond the recorded current-source reduction",
            ],
            "strongest_reduction": strongest,
            "current_source_refs": refs,
            "reason": reason,
            "reopen_only_if": "New primary evidence supplies an ex-ante same-information prediction that the recorded current-source reduction cannot express under matched information, budget, and operational scope; renaming components, changing application domain, or proposing an unexecuted ablation does not reopen the basin.",
            "search_closure_certified": True,
            "dead_end_certified": False,
            **problem_novelty_classification(basis="current-primary-collision-re-review-2026-08-18"),
            "counter_explanation": {
                "type": "SAME_INFORMATION_REDUCTION",
                "statement": strongest,
                "opposite_prediction": "Under matched information, budget, and operational scope, the cited current-source mechanism explains the proposed prediction without the candidate's standalone principle.",
                "opposite_principle": "The cited same-information mechanism is sufficient on this bounded formulation.",
                "opposite_search_seed": "Search for a bounded condition where the cited mechanism receives identical information but makes a distinct falsifiable prediction from the candidate mechanism.",
                "scope": "the bounded candidate problem formulation and current-source collision review",
                "same_information_or_scope_matched": True,
                "evidence_refs": refs,
                "alternative_explanations_ruled_out": ["missing execution support", "provider/runtime failure", "mere terminology or application-domain change"],
                "positive_support": True,
                "same_information_reduction_verified": True,
                "reopen_condition": "New primary evidence supplies an ex-ante same-information prediction that the recorded current-source reduction cannot express under matched information, budget, and operational scope."
            },
            "source_run_id": str(latest.get("run_id") or ""),
            "source_stage_manifest_sha256": str(latest.get("stage_manifest_sha256") or ""),
            "scientific_authority": False,
        }
    hard_rows = [hard_by_basin[key] for key in sorted(hard_by_basin)]
    memory["blocked_objects"].extend(hard_rows)

    semantic_inherited = _prior_semantic_block_rows() if prior_semantic_rows is None else [dict(row) for row in prior_semantic_rows if isinstance(row, dict)]
    continuation_rows = _continuation_hold_rows()
    if prior_semantic_rows is None:
        semantic_inherited.extend(dict(row) for row in continuation_rows if str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-")))
    semantic_by_basin = {str(row.get("basin")): row for row in semantic_inherited if str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-")) and row.get("scientific_authority") is False}
    semantic_added = 0
    latest_pool_sha = str(latest.get("frozen_pool_sha256") or "").strip()
    for row in latest.get("candidates") or []:
        if not isinstance(row, dict) or str(row.get("semantic_verdict") or "") != "BLOCK":
            continue
        reduction_class = str(row.get("semantic_reduction_class") or "").strip()
        lane_verified = row.get("semantic_lane_contract_verified") is True
        strongest = " ".join(str(row.get("semantic_strongest_reduction") or "").split())[:800]
        reason = " ".join(str(row.get("semantic_reason") or "").split())[:1200]
        exact_test = " ".join(str(row.get("semantic_exact_reduction_test") or "").split())[:1200]
        lane_reason = " ".join(str(row.get("semantic_lane_contract_reason") or "").split())[:1000]
        refs = sorted({str(ref) for ref in row.get("semantic_source_refs") or [] if str(ref).startswith("arXiv:")})
        claims = [" ".join(str(value or "").split())[:1200] for value in row.get("semantic_source_claims") or [] if str(value or "").strip()]
        problem_text = " ".join(str(row.get("semantic_problem_text") or row.get("title") or "").split())[:2400]
        patterns = sorted({str(value) for value in row.get("semantic_matched_patterns") or [] if str(value)})
        candidate_id = str(row.get("candidate_id") or "").strip()
        primitive = str(row.get("search_primitive") or "").strip()
        title = " ".join(str(row.get("title") or "").split())[:300]
        if not lane_verified and strongest and reason and lane_reason:
            signature = hashlib.sha256(json.dumps({"strongest_reduction": strongest, "lane_contract_reason": lane_reason, "search_primitive": primitive}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
            basin = f"semantic-lane-contract-{signature}"
            if basin not in semantic_by_basin:
                semantic_added += 1
            semantic_by_basin[basin] = {
                "source_candidate_id": candidate_id,
                "basin": basin,
                "search_primitive": primitive,
                "avoid": [f"paraphrase-only variants of: {title}", "combining heterogeneous failures without one explicitly shared bounded operational condition", "using a generic optimizer/model-capability story as a convergent-failure object without a common measured failure variable"],
                "strongest_reduction": strongest,
                "matched_patterns": patterns,
                "reduction_class": reduction_class,
                "lane_contract_reason": lane_reason,
                "exact_reduction_test": exact_test,
                "current_source_refs": refs,
                "evidence_claims": claims,
                "problem_text": problem_text,
                "frozen_pool_sha256": latest_pool_sha,
                "reason": reason,
                "reopen_only_if": "New primary evidence supplies the missing lane-contract elements explicitly (shared bounded condition, common failure object, and correctly typed evidence roles) and the resulting formulation still leaves a same-information residual beyond the recorded strongest reduction.",
                "dead_end_certified": False,
                "memory_class": "FORMULATION_HOLD",
                "scientific_authority": False,
            }
        elif reduction_class == "NEEDS_EXACT_REDUCTION_TEST" and strongest and exact_test and exact_test.lower() != "none" and reason:
            signature = hashlib.sha256(json.dumps({"strongest_reduction": strongest, "matched_patterns": patterns, "exact_reduction_test": exact_test}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
            basin = f"semantic-exact-reduction-{signature}"
            if basin not in semantic_by_basin:
                semantic_added += 1
            semantic_by_basin[basin] = {
                "source_candidate_id": candidate_id,
                "basin": basin,
                "search_primitive": primitive,
                "avoid": [f"paraphrase-only variants of: {title}", f"domain-swapped variants still explained by: {strongest}", "claiming a new structural boundary without resolving the recorded same-information exact reduction test"],
                "strongest_reduction": strongest,
                "matched_patterns": patterns,
                "reduction_class": reduction_class,
                "exact_reduction_test": exact_test,
                "current_source_refs": refs,
                "evidence_claims": claims,
                "problem_text": problem_text,
                "frozen_pool_sha256": latest_pool_sha,
                "reason": reason,
                "reopen_only_if": "New primary evidence directly instantiates the recorded exact reduction test under matched information and leaves a residual prediction the named mature reduction cannot express; new wording, a new application domain, or an unexecuted proposed falsifier does not reopen this basin.",
                "dead_end_certified": False,
                "memory_class": "REDUCTION_TEST_HOLD",
                "scientific_authority": False,
            }
    semantic_rows = [semantic_by_basin[key] for key in sorted(semantic_by_basin)]
    memory["blocked_objects"].extend(semantic_rows)
    near_miss_state = near_miss_state or build_shadow_near_miss_preflight()
    base_near_miss_rows = compile_shadow_dead_end_rows(near_miss_state)
    near_inherited = _prior_near_miss_rows() if prior_near_miss_rows is None else [dict(row) for row in prior_near_miss_rows if isinstance(row, dict)]
    if prior_near_miss_rows is None:
        near_inherited.extend(dict(row) for row in continuation_rows if str(row.get("basin") or "").startswith("near-miss-"))
    def near_key(row: dict[str, Any]) -> tuple[str, str]:
        return (str(row.get("basin") or ""), str(row.get("source_candidate_id") or ""))
    near_by_key = {near_key(row): row for row in near_inherited if str(row.get("basin") or "").startswith("near-miss-") and row.get("scientific_authority") is False}
    for row in base_near_miss_rows:
        if isinstance(row, dict) and str(row.get("basin") or "").startswith("near-miss-"):
            near_by_key[near_key(row)] = dict(row)
    for row in extra_near_miss_rows or []:
        if isinstance(row, dict) and str(row.get("basin") or "").startswith("near-miss-") and row.get("scientific_authority") is False:
            near_by_key[near_key(row)] = dict(row)
    near_miss_rows = [near_by_key[key] for key in sorted(near_by_key)]
    memory["blocked_objects"].extend(near_miss_rows)
    readjudication_rows = [dict(row) for row in (principle_readjudication_rows or []) if isinstance(row, dict) and (row.get("search_closure_certified") is True or row.get("dead_end_certified") is True)]
    readjudication_by_basin = {str(row.get("basin") or ""): row for row in readjudication_rows if str(row.get("basin") or "")}
    memory["blocked_objects"].extend(readjudication_by_basin[key] for key in sorted(readjudication_by_basin))
    # A certified scoped closure supersedes an older support-unavailable hold for
    # the exact same fresh candidate. Keep the release audit as provenance/reopen
    # evidence, but do not expose contradictory live memory saying the same exact
    # formulation is simultaneously closed and a REOPENABLE_HOLD.
    principle_closed_candidate_ids = {
        str(row.get("source_candidate_id") or "")
        for row in readjudication_rows
        if str(row.get("source_candidate_id") or "")
        and isinstance(row.get("fresh_phenomenon_closure"), dict)
        and bool(row.get("fresh_phenomenon_closure"))
    }
    exact_support_holds = fresh_phenomenon_support_hold_rows if fresh_phenomenon_support_hold_rows is not None else _fresh_phenomenon_support_hold_rows()
    hold_by_basin = {
        str(row.get("basin") or ""): dict(row)
        for row in exact_support_holds
        if isinstance(row, dict)
        and str(row.get("basin") or "").startswith("fresh-phenomenon-support-hold-")
        and row.get("scientific_authority") is False
        and row.get("dead_end_certified") is False
        and str(row.get("source_candidate_id") or "") not in principle_closed_candidate_ids
    }
    memory["hold_objects"].extend(hold_by_basin[key] for key in sorted(hold_by_basin))

    # Migrate legacy memory into the stricter epistemic split. Only rows with an
    # affirmative reduction/collision explanation remain persistent closed basins.
    # Their memory_class is then typed by the scientific layer that actually failed;
    # a scoped closure is not automatically a core-principle falsification. Missing
    # support, lane-contract failures, and unresolved reduction tests remain holds.
    all_rows = [dict(row) for row in list(memory.get("blocked_objects") or []) + list(memory.get("hold_objects") or []) if isinstance(row, dict)]
    certified_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    for item in all_rows:
        basin = str(item.get("basin") or "")
        disposition = str(item.get("disposition") or "")
        legacy_reduction_dead_end = basin.startswith("current-source-hard-veto-") or disposition in {"STOP_CURRENT_PRIMARY_COLLISION", "STOP_MATURE_THEORY_REDUCTION"}
        certified = item.get("search_closure_certified") is True or item.get("dead_end_certified") is True or legacy_reduction_dead_end
        if certified:
            item = normalize_closed_row(item)
            item["search_closure_certified"] = True
            item["dead_end_certified"] = bool(item.get("failure_layer") == "core_principle" and item.get("principle_update_allowed") is True)
            strongest = str(item.get("strongest_reduction") or "").strip()
            refs = list(item.get("current_source_refs") or item.get("evidence_basis") or [])
            reopen = str(item.get("reopen_only_if") or "").strip()
            if not isinstance(item.get("counter_explanation"), dict):
                item["counter_explanation"] = {
                    "type": "SAME_INFORMATION_REDUCTION",
                    "statement": strongest,
                    "opposite_prediction": "Under the same information and bounded operational scope, the recorded reduction explains the candidate prediction without the proposed standalone principle.",
                    "opposite_principle": "The recorded same-information reduction is sufficient within this basin.",
                    "opposite_search_seed": "Search only for a bounded same-information case where the recorded reduction cannot express the candidate's residual prediction.",
                    "scope": "the recorded shadow paper-problem basin",
                    "same_information_or_scope_matched": True,
                    "evidence_refs": refs,
                    "positive_support": True,
                    "same_information_reduction_verified": True,
                    "reopen_condition": reopen,
                }
            else:
                counter = dict(item["counter_explanation"])
                counter.setdefault("opposite_principle", strongest or "The recorded same-information reduction is sufficient within this basin.")
                counter.setdefault("opposite_search_seed", "Search only for a bounded same-information case where the recorded reduction cannot express the candidate's residual prediction.")
                counter.setdefault("reopen_condition", reopen)
                item["counter_explanation"] = counter
            certified_rows.append(item)
        else:
            item["dead_end_certified"] = False
            if not str(item.get("memory_class") or "").strip():
                item["memory_class"] = "REOPENABLE_HOLD"
            hold_rows.append(item)

    # Compatibility return view: callers of the historical helper still receive
    # blocked_objects, but canonical persistence below uses closed_objects under
    # shadow_search_memory. Scientific dead-end persistence is projected separately.
    memory["blocked_objects"] = certified_rows
    memory["closed_objects"] = certified_rows
    memory["hold_objects"] = hold_rows
    memory["memory_id"] = "shadow-paper-design-search-control-memory-compat-v4"
    closure_counts = summarize_closure_layers(certified_rows)
    scientific_counts = summarize_scientific_failure_layers(certified_rows)
    memory["closed_basin_count"] = len(certified_rows)
    memory["closure_layer_counts"] = closure_counts
    memory["failure_layer_counts"] = scientific_counts
    memory["problem_novelty_stop_count"] = closure_counts["problem_novelty"]
    memory["execution_stop_count"] = scientific_counts["execution"]
    memory["experiment_identifiability_stop_count"] = scientific_counts["experiment_identifiability"]
    memory["optimization_stop_count"] = scientific_counts["optimization"]
    memory["operationalization_stop_count"] = scientific_counts["operationalization"]
    memory["method_realization_stop_count"] = scientific_counts["method_realization"]
    memory["assumption_scope_stop_count"] = scientific_counts["assumption_scope"]
    memory["core_principle_stop_count"] = scientific_counts["core_principle"]
    memory["broader_core_principle_falsification_count"] = sum(row.get("broader_core_principle_falsified") is True for row in certified_rows)
    # Legacy compatibility: a principle dead end is now exactly a canonical
    # core_principle-layer scoped stop, while broader benchmark/phenomenon
    # falsification is counted separately above.
    memory["principle_dead_end_count"] = scientific_counts["core_principle"]
    memory["core_principle_dead_end_count"] = scientific_counts["core_principle"]
    memory["principle_readjudication_closed_basin_count"] = sum(str(row.get("basin") or "").startswith("principle-readjudication-") for row in certified_rows)
    memory["principle_readjudication_dead_end_count"] = sum(str(row.get("basin") or "").startswith("principle-readjudication-") and row.get("failure_layer") == "core_principle" for row in certified_rows)
    closure_rows=[row.get("fresh_phenomenon_closure") or {} for row in certified_rows if isinstance(row.get("fresh_phenomenon_closure"),dict) and row.get("fresh_phenomenon_closure")]
    memory["fresh_phenomenon_closure_count"] = len(closure_rows)
    memory["fresh_phenomenon_closed_evidence_count"] = sum(len(row.get("closed_evidence_sha256") or []) for row in closure_rows)
    asset_by_ref: dict[str, dict[str, Any]] = {}
    for row in certified_rows:
        asset = row.get("opposite_search_asset_evidence") or {}
        if isinstance(asset, dict) and str(asset.get("asset_ref") or "").startswith("first-party-asset:") and asset.get("scientific_authority") is False:
            ref = str(asset["asset_ref"])
            incoming = dict(asset)
            current = asset_by_ref.get(ref)
            # Closure is monotone: a later principle certificate may retire a
            # previously active search asset, but an older active receipt must
            # never reopen it merely because file/order traversal changes.
            if current is None or current.get("search_active") is not False:
                asset_by_ref[ref] = incoming
            if incoming.get("search_active") is False:
                asset_by_ref[ref] = incoming
    memory["inversion_asset_evidence"] = [asset_by_ref[key] for key in sorted(asset_by_ref)]
    memory["inversion_asset_evidence_count"] = len(asset_by_ref)
    memory["inversion_asset_search_active_count"] = sum(row.get("search_active") is not False for row in memory["inversion_asset_evidence"])
    positive_registry = build_positive_residual_asset_registry()
    positive_assets = [dict(row) for row in positive_registry.get("assets") or [] if isinstance(row, dict) and row.get("scientific_authority") is False]
    memory["positive_residual_asset_evidence"] = positive_assets
    memory["positive_residual_asset_evidence_count"] = len(positive_assets)
    memory["positive_residual_search_active_count"] = sum(row.get("search_active") is True for row in positive_assets)
    memory["positive_residual_asset_registry_id"] = positive_registry.get("registry_id")
    memory["hold_object_count"] = len(hold_rows)
    memory["current_source_hard_veto_count"] = len(hard_rows)
    memory["current_source_hard_veto_added_from_latest_run"] = added
    memory["current_source_hard_veto_added_from_terminal_run"] = added
    memory["current_source_hard_veto_inherited"] = max(0, len(hard_rows) - added)
    memory["semantic_blocker_count"] = 0
    memory["semantic_hold_count"] = len(semantic_rows)
    memory["semantic_blocker_added_from_latest_run"] = 0
    memory["semantic_blocker_added_from_terminal_run"] = 0
    memory["semantic_blocker_inherited"] = 0
    memory["semantic_hold_added_from_latest_run"] = semantic_added
    memory["semantic_hold_added_from_terminal_run"] = semantic_added
    memory["semantic_hold_inherited"] = max(0, len(semantic_rows) - semantic_added)
    certified_near = [row for row in near_miss_rows if row.get("dead_end_certified") is True or str(row.get("disposition") or "") in {"STOP_CURRENT_PRIMARY_COLLISION", "STOP_MATURE_THEORY_REDUCTION"}]
    held_near = [row for row in near_miss_rows if row not in certified_near]
    memory["near_miss_preflight_count"] = len(certified_near)
    memory["near_miss_hold_count"] = len(held_near)
    memory["near_miss_base_preflight_count"] = len(base_near_miss_rows)
    memory["near_miss_terminal_support_hold_count"] = sum(str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-") for row in near_miss_rows)
    memory["scientific_authority"] = False
    return memory


def merge_shadow_terminal_run_memory(state: dict[str, Any], terminal_run: dict[str, Any], preflight: dict[str, Any] | None = None, *, evidence_plan: dict[str, Any] | None = None, evidence_fallback_primary_refs: dict[str, list[str]] | None = None) -> dict[str, Any]:
    run_id = str(terminal_run.get("run_id") or "").strip()
    stage_manifest_sha256 = str(terminal_run.get("stage_manifest_sha256") or "").strip()
    policy = terminal_run.get("policy") or {}
    if not run_id or str(terminal_run.get("status") or "") != "SHADOW_TERMINAL_COMPLETE":
        raise ValueError("terminal shadow run must be complete before dead-end-memory ingestion")
    if terminal_run.get("scientific_authority") is not False or policy.get("shadow_only") is not True or policy.get("canonical_primary_generator_queue_untouched") is not True:
        raise ValueError("terminal shadow run memory ingestion requires zero-authority shadow provenance")
    if not stage_manifest_sha256:
        raise ValueError("terminal shadow run memory ingestion requires stage manifest provenance")

    merged = json.loads(json.dumps(state, ensure_ascii=False))
    prior_memory = _state_search_memory(merged)
    prior_rows = [row for row in _closed_objects(prior_memory) + list(prior_memory.get("hold_objects") or []) if isinstance(row, dict)]
    prior_hard = [dict(row) for row in prior_rows if str(row.get("basin") or "").startswith("current-source-hard-veto-")]
    prior_semantic = [dict(row) for row in prior_rows if str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-"))]
    prior_near = [dict(row) for row in prior_rows if str(row.get("basin") or "").startswith("near-miss-")]
    prior_principle = [dict(row) for row in prior_rows if str(row.get("basin") or "").startswith("principle-readjudication-")]
    current_principle = _principle_readjudication_rows()
    principle_by_basin = {str(row.get("basin") or ""): row for row in prior_principle + current_principle if str(row.get("basin") or "")}
    extra_near = _terminal_support_hold_rows(preflight, run_id=run_id, stage_manifest_sha256=stage_manifest_sha256)
    extra_near.extend(_terminal_evidence_hold_rows(evidence_plan, run_id=run_id, stage_manifest_sha256=stage_manifest_sha256, fallback_primary_refs=evidence_fallback_primary_refs))

    memory_compat = _shadow_dead_end_memory(
        {"latest_run": terminal_run},
        near_miss_state=merged.get("shadow_near_miss_preflight") or build_shadow_near_miss_preflight(),
        prior_hard_veto_rows=prior_hard,
        prior_semantic_rows=prior_semantic,
        prior_near_miss_rows=prior_near,
        extra_near_miss_rows=extra_near,
        principle_readjudication_rows=[principle_by_basin[key] for key in sorted(principle_by_basin)],
    )
    search_memory = _canonical_search_memory(memory_compat)
    dead_end_memory = _principle_dead_end_projection(search_memory)
    merged["shadow_search_memory"] = search_memory
    merged["shadow_dead_end_memory"] = dead_end_memory
    memory = search_memory
    summary = merged.setdefault("summary", {})
    summary.update({
        "shadow_dead_end_objects": len(dead_end_memory.get("blocked_objects") or []),
        "shadow_closed_basins": int(memory.get("closed_basin_count") or 0),
        "principle_readjudication_dead_ends": int(memory.get("principle_readjudication_dead_end_count") or 0),
        "principle_readjudication_closed_basins": int(memory.get("principle_readjudication_closed_basin_count") or 0),
        "problem_novelty_stops": int(memory.get("problem_novelty_stop_count") or 0),
        "execution_stops": int(memory.get("execution_stop_count") or 0),
        "experiment_identifiability_stops": int(memory.get("experiment_identifiability_stop_count") or 0),
        "optimization_stops": int(memory.get("optimization_stop_count") or 0),
        "operationalization_stops": int(memory.get("operationalization_stop_count") or 0),
        "method_realization_stops": int(memory.get("method_realization_stop_count") or 0),
        "assumption_scope_stops": int(memory.get("assumption_scope_stop_count") or 0),
        "core_principle_stops": int(memory.get("core_principle_stop_count") or 0),
        "broader_core_principle_falsifications": int(memory.get("broader_core_principle_falsification_count") or 0),
        "core_principle_dead_ends": int(memory.get("core_principle_dead_end_count") or 0),
        "shadow_hold_objects": len(memory.get("hold_objects") or []),
        "current_source_hard_veto_dead_ends": int(memory.get("current_source_hard_veto_count") or 0),
        "current_source_hard_veto_added_from_latest_run": 0,
        "current_source_hard_veto_added_from_terminal_run": int(memory.get("current_source_hard_veto_added_from_terminal_run") or 0),
        "current_source_hard_veto_inherited": int(memory.get("current_source_hard_veto_inherited") or 0),
        "semantic_blocker_dead_ends": 0,
        "semantic_hold_objects": int(memory.get("semantic_hold_count") or 0),
        "semantic_blocker_added_from_latest_run": 0,
        "semantic_blocker_added_from_terminal_run": 0,
        "semantic_blocker_inherited": 0,
        "semantic_hold_added_from_terminal_run": int(memory.get("semantic_hold_added_from_terminal_run") or 0),
        "near_miss_preflight_dead_ends": int(memory.get("near_miss_preflight_count") or 0),
        "near_miss_holds": int(memory.get("near_miss_hold_count") or 0),
        "near_miss_terminal_support_holds": int(memory.get("near_miss_terminal_support_hold_count") or 0),
    })
    memory["current_source_hard_veto_added_from_latest_run"] = 0
    memory["semantic_blocker_added_from_latest_run"] = 0
    memory["semantic_hold_added_from_latest_run"] = 0

    prior_maintenance = merged.get("shadow_memory_maintenance") or {}
    receipts = [dict(row) for row in prior_maintenance.get("receipts") or [] if isinstance(row, dict)]
    before_hard = len(prior_hard)
    before_semantic = len(prior_semantic)
    before_terminal_holds = sum(str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-") for row in prior_near)
    receipt = {
        "run_id": run_id,
        "stage_manifest_sha256": stage_manifest_sha256,
        "terminal_generated_at": terminal_run.get("generated_at"),
        "hard_veto_added": max(0, int(memory.get("current_source_hard_veto_count") or 0) - before_hard),
        "semantic_blocker_added": 0,
        "semantic_hold_added": max(0, int(memory.get("semantic_hold_count") or 0) - before_semantic),
        "support_hold_added": max(0, int(memory.get("near_miss_terminal_support_hold_count") or 0) - before_terminal_holds),
        "scientific_authority": False,
    }
    receipt_key = (run_id, stage_manifest_sha256)
    by_key = {(str(row.get("run_id") or ""), str(row.get("stage_manifest_sha256") or "")): row for row in receipts}
    by_key[receipt_key] = receipt
    receipts = list(by_key.values())[-64:]
    merged["shadow_memory_maintenance"] = {
        "policy": dict(SHADOW_MEMORY_MAINTENANCE_POLICY),
        "last_ingested_run_id": run_id,
        "last_ingested_stage_manifest_sha256": stage_manifest_sha256,
        "receipts": receipts,
        "scientific_authority": False,
    }
    merged["generated_at"] = _now()
    return merged


def merge_terminal_shadow_run_memory(*, run_root: Path, json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    from .paper_first_problem_search_portfolio_publish import _latest_shadow_run

    terminal_run = _latest_shadow_run(run_root)
    preflight_path = run_root / "problem-falsifier-preflight.json"
    preflight = _load_json(preflight_path) if preflight_path.exists() else {}
    evidence_plan_path = run_root / "evidence-acquisition-plan.json"
    evidence_plan = _load_json(evidence_plan_path) if evidence_plan_path.exists() else {}
    state = _load_json(json_path)
    merged = merge_shadow_terminal_run_memory(
        state,
        terminal_run,
        preflight,
        evidence_plan=evidence_plan,
        evidence_fallback_primary_refs=_run_formulation_primary_refs(run_root),
    )
    errors = validate_search_portfolio_design_adjudication(merged)
    if errors:
        raise ValueError("Invalid Search Portfolio dead-end memory maintenance:\n- " + "\n- ".join(errors))
    json_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION = " + json.dumps(merged, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return {
        "run_id": terminal_run.get("run_id"),
        "stage_manifest_sha256": terminal_run.get("stage_manifest_sha256"),
        "summary": merged.get("summary") or {},
        "maintenance": merged.get("shadow_memory_maintenance") or {},
        "scientific_authority": False,
    }


ADVISORY_CONSULTATION = {
    "run_root": "generated/research-data/runs/ai-consultation/cases/sp-paper-design-20260814",
    "checkpoint": "idea_premortem",
    "reviewers": [
        {
            "reviewer": "glm-5.2",
            "SP-09": "missing:model-output-no-json",
            "SP-15": "missing:output-length-ceiling",
        },
        {
            "reviewer": "deepseek-v4-pro",
            "SP-09": "missing:reasoning-output-length-ceiling",
            "SP-15": "missing:reasoning-output-length-ceiling",
        },
    ],
    "failed_or_missing_review_is_not_pass": True,
    "scientific_authority": False,
}

ROWS: tuple[dict[str, Any], ...] = (
    {
        "id": "SP-09",
        "verdict": "STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS",
        "original_problem": "Model-trigger-skill-context acceptance object with a compositional-risk veto for evolved skill deployment.",
        "collision_status": "DIRECT_PLUS_COMPOSITIONAL",
        "paper_problem_status": "STOP_STANDALONE",
        "collision_reason": "The original novelty bundle is occupied in pieces that together reproduce the claimed paper object: lifecycle governance already maps verification to graduated deployment permissions; dependency/context-aware skill-chain risk is explicit; conditional dormant attacks and model-dependent skill behavior are already empirical first-class objects. A new install/update/block/escalate acceptance object therefore reduces to a contextual security/utility policy unless it proves a stronger impossibility or decision-theoretic phenomenon.",
        "surviving_risk_axis": "Context-dependent admissibility of the same evolved skill across target model × trigger × installed-skill/workflow context remains a useful evaluation axis, but not a standalone paper thesis under the current formulation.",
        "strongest_same_information_baselines": [
            "Skill Trust and Lifecycle Governance gates/tiers with context-aware verification features",
            "ChainGuard-style candidate+installed-skill context analysis followed by graduated permission assignment",
            "generic contextual constrained decision/risk-sensitive policy using identical model/trigger/workflow/security/utility features",
            "MASA-style model-conditioned skill adaptation plus a security gate",
        ],
        "revival_requirements": [
            "State an ex-ante prediction that cannot be expressed by a contextual constrained policy using exactly the same model/trigger/workflow/utility/security evidence.",
            "Show that the same skill's admissibility has a structural non-separability/impossibility property, not merely model dependence or composition dependence.",
            "Beat lifecycle-governance and ChainGuard-derived decision rules under the same information and false-positive/utility budget.",
            "Do not use a new scalar score, trust tier, permission tier, scanner, or hard veto as the novelty claim.",
        ],
        "cheapest_problem_falsifier": "Construct the candidate's intended install/update/block/escalate labels on a small matched table, then fit or hand-compile a generic contextual constrained policy with the identical target-model, trigger, installed-skill/workflow, utility, and security observations. If it reproduces the decisions, the revised object has no irreducible paper novelty.",
        "method_design_authorized": False,
        "experiment_blueprint_authorized": False,
        "local_validation_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "next_action": "Stop standalone SP-09. Preserve context-dependent admissibility as a risk/baseline axis for future skill-evolution papers; reopen only with a non-separability/impossibility result beyond contextual governance.",
    },
    {
        "id": "SP-15",
        "verdict": "REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED",
        "original_problem": "The explicit-procedure boundary of query-only skill retrieval.",
        "collision_status": "DIRECT_ON_IMPLICIT_RETRIEVAL_AND_DECOMPOSITION",
        "paper_problem_status": "REVISE_BEFORE_METHOD_DESIGN",
        "collision_reason": "Implicit query difficulty, reasoning-enhanced query-only retrieval, task decomposition, structured multi-skill routing, query-conditional skill-set compatibility, same-capability ambiguity, and typed structural retrieval are already occupied. The original explicit-versus-implicit procedural boundary is therefore not sufficient novelty.",
        "revised_problem": "Given an observable user query q and a fixed skill library L under query-only inference, is the minimally sufficient capability/skill set point-identifiable from q at all? If multiple task semantics that are observationally compatible with the same q require incompatible sufficient skill sets, retrieval is structurally non-identifiable and a system must abstain or acquire additional information rather than merely rerank more strongly.",
        "irreducible_boundary_required": "The claim must be about observational non-identifiability of the sufficient skill set, not about implicit queries being harder, decomposition improving retrieval, multi-skill compatibility, same-capability representative risk, or a new clarification policy. The paper must separate 'retriever failed to infer latent steps' from 'no query-only retriever can identify one sufficient set from the available information'.",
        "strongest_same_information_baselines": [
            "SkillReason query-only reasoning-enhanced embedding",
            "SkillWeaver / SkillReranker task decomposition and structured reranking",
            "R3-Skill query-conditional set compatibility",
            "SkillResolve same-capability query-conditioned utility/representative selection",
            "SkillDAG structural relation/conflict retrieval",
            "generic selective prediction / calibrated abstention",
            "generic partial identification over latent task interpretations",
            "generic clarification-need prediction / active query refinement",
        ],
        "required_problem_revision": [
            "Define an observational equivalence relation over task semantics that produce the same available query representation and map each semantic state to a sufficient capability/skill set.",
            "Define point-identifiable, set-identifiable, and non-identifiable retrieval cases before introducing any learned method.",
            "Require matched examples where the observable query is held fixed or information-equivalent while compatible latent task semantics require incompatible sufficient skill sets; simple short-vs-long or explicit-vs-implicit pairs are insufficient.",
            "Show that an oracle ranker with the same query information cannot resolve the non-identifiable cases; otherwise the issue is model quality rather than information structure.",
            "Audit against generic selective prediction, partial identification, and clarification policies using exactly the same ambiguity set/evidence.",
            "Do not claim task decomposition, capability reasoning, top-rank-versus-coverage metrics, or abstention itself as novelty.",
        ],
        "cheapest_problem_falsifier": "Before method design, inventory existing SkillReason/SkillRet/CompSkillBench/R3-Skill/SkillResolve-style assets for query-level units where one observable or information-equivalent query admits multiple plausible task semantics with incompatible sufficient skill sets. If no such units exist, or if a generic uncertainty/clarification baseline using the same information resolves them, stop the revised problem.",
        "method_design_authorized": False,
        "experiment_blueprint_authorized": False,
        "local_validation_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "next_action": "Run a data-only support inventory for query-level non-identifiability. Advance to method design only if nonzero matched units survive source/provenance and generic partial-identification/clarification reduction checks.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def build_search_portfolio_design_adjudication() -> dict[str, Any]:
    portfolio = _load_json(SHADOW_PORTFOLIO_JSON)
    queue_shadow = _load_json(SHADOW_QUEUE_JSON)
    prior_state = _load_json(DEFAULT_JSON)
    portfolio_policy = portfolio.get("policy") or {}
    queue_policy = queue_shadow.get("policy") or {}
    if portfolio.get("scientific_authority") is not False or portfolio_policy.get("shadow_only") is not True or portfolio_policy.get("canonical_primary_generator_queue_untouched") is not True:
        raise ValueError("Search Portfolio Paper Design audit requires the zero-authority shadow portfolio state")
    if queue_shadow.get("scientific_authority") is not False or queue_policy.get("shadow_only") is not True or queue_policy.get("cannot_mutate_canonical_queue") is not True:
        raise ValueError("Search Portfolio Paper Design audit requires the zero-authority counterfactual queue shadow")
    candidates = {str(row.get("candidate_id")): row for row in portfolio.get("candidates") or [] if isinstance(row, dict) and row.get("historical_counterfactual_problem_gate_pass") is True}
    counterfactual_pass_ids = {str(value) for value in queue_shadow.get("historical_counterfactual_pass_ids") or []}
    reviewed_ids = [str(row["id"]) for row in ROWS]
    missing = sorted(set(reviewed_ids) - set(candidates) | (set(reviewed_ids) - counterfactual_pass_ids))
    if missing:
        raise ValueError("Search Portfolio design audit requires historical shadow counterfactual survivors: " + ",".join(missing))
    rows = []
    for template in ROWS:
        row = dict(template)
        source = candidates[row["id"]]
        row["shadow_candidate_title"] = source.get("title")
        row["shadow_search_primitive"] = source.get("search_primitive")
        row["historical_counterfactual_problem_gate_pass"] = True
        row["live_paper_design_eligible"] = False
        row["primary_sources"] = PRIMARY_SOURCES[row["id"]]
        row["counterfactual_problem_gate_pass_does_not_grant_live_paper_design"] = True
        rows.append(row)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    near_miss_preflight = build_shadow_near_miss_preflight()
    memory_compat = _shadow_dead_end_memory(portfolio, near_miss_preflight, principle_readjudication_rows=_principle_readjudication_rows())
    search_memory = _canonical_search_memory(memory_compat)
    dead_end_memory = _principle_dead_end_projection(search_memory)
    prior_maintenance = prior_state.get("shadow_memory_maintenance") or {}
    maintenance = json.loads(json.dumps(prior_maintenance, ensure_ascii=False)) if prior_maintenance else {
        "policy": dict(SHADOW_MEMORY_MAINTENANCE_POLICY),
        "last_ingested_run_id": "",
        "last_ingested_stage_manifest_sha256": "",
        "receipts": [],
        "scientific_authority": False,
    }
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "review_id": "search-portfolio-sp09-sp15-paper-design-20260814",
        "target_venue": "ICLR",
        "component_owner": "paper-design-contract",
        "source_state": "shadow-search-portfolio",
        "policy": {
            "this_is_a_substate_not_a_new_backend_component": True,
            "source_is_shadow_search_portfolio": True,
            "shadow_queue_has_zero_paper_design_authority": True,
            "cannot_grant_or_revoke_live_paper_design_authority": True,
            "counterfactual_problem_gate_pass_only_triggers_retrospective_collision_audit": True,
            "current_source_hard_veto_memory_persists_across_shadow_runs": True,
            "semantic_hold_memory_persists_across_shadow_runs": True,
            "semantic_lane_or_pending_reduction_is_not_a_dead_end": True,
            "semantic_soft_collision_alone_is_not_a_dead_end": True,
            "persistent_dead_end_requires_positive_counter_explanation": True,
            "search_control_closure_is_not_scientific_dead_end": True,
            "only_core_principle_enters_shadow_dead_end_memory": True,
            "holds_live_only_in_shadow_search_memory": True,
            "closed_basin_must_name_closure_layer": True,
            "scientific_closed_basin_must_use_canonical_failure_layer": True,
            "problem_novelty_stop_is_upstream_not_experimental_failure_layer": True,
            "scoped_closed_basin_is_not_automatically_principle_stop": True,
            "principle_stop_does_not_imply_benchmark_level_dead_end": True,
            "principle_stop_requires_explicit_stop_class_or_broader_falsification": True,
            "principle_readjudications_feed_opposite_search_control_only": True,
            "current_primary_source_collision_review_required": True,
            "same_information_reduction_required_before_method_design": True,
            "failed_or_missing_ai_reviewer_is_not_pass": True,
            "paper_problem_support_inventory_precedes_method_design_when_identifiability_is_claimed": True,
            "method_design_authorized": False,
            "experiment_blueprint_authorized": False,
            "local_validation_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
        },
        "advisory_consultation": ADVISORY_CONSULTATION,
        "shadow_near_miss_preflight": near_miss_preflight,
        "shadow_memory_maintenance": maintenance,
        "shadow_search_memory": search_memory,
        "shadow_dead_end_memory": dead_end_memory,
        "shadow_source": {
            "portfolio_status": portfolio.get("status"),
            "portfolio_schema_version": portfolio.get("schema_version"),
            "historical_source_commit": portfolio.get("historical_source_commit"),
            "frozen_pool_sha256": portfolio.get("frozen_pool_sha256"),
            "summary": dict(portfolio.get("summary") or {}),
            "queue_summary": dict(queue_shadow.get("summary") or {}),
            "scientific_authority": False,
        },
        "summary": {
            "reviewed": len(rows),
            "advance_to_method_design": 0,
            "revise_paper_problem": counts.get("REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED", 0),
            "stop_standalone": counts.get("STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS", 0),
            "support_inventory_required": counts.get("REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED", 0),
            "shadow_dead_end_objects": len(dead_end_memory.get("blocked_objects") or []),
            "shadow_closed_basins": int(search_memory.get("closed_basin_count") or 0),
            "principle_readjudication_dead_ends": int(search_memory.get("principle_readjudication_dead_end_count") or 0),
            "principle_readjudication_closed_basins": int(search_memory.get("principle_readjudication_closed_basin_count") or 0),
            "problem_novelty_stops": int(search_memory.get("problem_novelty_stop_count") or 0),
            "execution_stops": int(search_memory.get("execution_stop_count") or 0),
            "experiment_identifiability_stops": int(search_memory.get("experiment_identifiability_stop_count") or 0),
            "optimization_stops": int(search_memory.get("optimization_stop_count") or 0),
            "operationalization_stops": int(search_memory.get("operationalization_stop_count") or 0),
            "method_realization_stops": int(search_memory.get("method_realization_stop_count") or 0),
            "assumption_scope_stops": int(search_memory.get("assumption_scope_stop_count") or 0),
            "core_principle_stops": int(search_memory.get("core_principle_stop_count") or 0),
            "broader_core_principle_falsifications": int(search_memory.get("broader_core_principle_falsification_count") or 0),
            "core_principle_dead_ends": int(dead_end_memory.get("principle_dead_end_count") or 0),
            "shadow_hold_objects": len(search_memory.get("hold_objects") or []),
            "current_source_hard_veto_dead_ends": int(search_memory.get("current_source_hard_veto_count") or 0),
            "current_source_hard_veto_added_from_latest_run": int(search_memory.get("current_source_hard_veto_added_from_latest_run") or 0),
            "current_source_hard_veto_added_from_terminal_run": int(search_memory.get("current_source_hard_veto_added_from_terminal_run") or 0),
            "current_source_hard_veto_inherited": int(search_memory.get("current_source_hard_veto_inherited") or 0),
            "semantic_blocker_dead_ends": 0,
            "semantic_hold_objects": int(search_memory.get("semantic_hold_count") or 0),
            "semantic_hold_added_from_latest_run": int(search_memory.get("semantic_hold_added_from_latest_run") or 0),
            "semantic_hold_added_from_terminal_run": int(search_memory.get("semantic_hold_added_from_terminal_run") or 0),
            "semantic_hold_inherited": int(search_memory.get("semantic_hold_inherited") or 0),
            "near_miss_preflight_dead_ends": int(search_memory.get("near_miss_preflight_count") or 0),
            "near_miss_holds": int(search_memory.get("near_miss_hold_count") or 0),
            "near_miss_terminal_support_holds": int(search_memory.get("near_miss_terminal_support_hold_count") or 0),
            "near_miss_support_holds": int((near_miss_preflight.get("summary") or {}).get("support_holds") or 0),
            "near_miss_current_primary_stops": int((near_miss_preflight.get("summary") or {}).get("current_primary_stops") or 0),
            "near_miss_mature_theory_stops": int((near_miss_preflight.get("summary") or {}).get("mature_theory_stops") or 0),
            "method_design_authorized": 0,
            "experiment_blueprint_authorized": 0,
            "local_validation_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "portfolio_priority": ["SP-15", "SP-09"],
        "rows": rows,
        "portfolio_decision": "Retrospective shadow audit only: SP-09 stops standalone after direct governance/context/model-dependence collisions. SP-15 is revised from an explicit-procedure retrieval boundary to query-only sufficient-skill-set identifiability, but remains blocked from Method Design until query-level support inventory establishes nonzero observationally non-identifiable units and generic partial-identification/clarification baselines do not absorb the object. Neither shadow candidate has live Paper Design authority.",
        "next_action": "Use these outcomes only as zero-authority shadow-search feedback. Do not design a method, compile an Experiment Blueprint, mutate the canonical Problem-Gate queue, start P0, or use GPU for either candidate.",
    }


def validate_search_portfolio_design_adjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = state.get("summary") or {}
    policy = state.get("policy") or {}
    rows = state.get("rows") or []
    if len(rows) != 2 or {str(row.get("id")) for row in rows} != {"SP-09", "SP-15"}:
        errors.append("SP design adjudication must review exactly SP-09 and SP-15")
    if (summary.get("reviewed"), summary.get("advance_to_method_design"), summary.get("revise_paper_problem"), summary.get("stop_standalone")) != (2, 0, 1, 1):
        errors.append("SP design routing must be 0 advance / 1 revise / 1 stop")
    if any(int(summary.get(key) or 0) != 0 for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("SP design adjudication cannot authorize downstream work")
    if policy.get("this_is_a_substate_not_a_new_backend_component") is not True or policy.get("paper_problem_support_inventory_precedes_method_design_when_identifiability_is_claimed") is not True:
        errors.append("SP design must remain a Paper Design substate and gate identifiability on support inventory")
    if policy.get("source_is_shadow_search_portfolio") is not True or policy.get("shadow_queue_has_zero_paper_design_authority") is not True or policy.get("cannot_grant_or_revoke_live_paper_design_authority") is not True or policy.get("current_source_hard_veto_memory_persists_across_shadow_runs") is not True or policy.get("semantic_hold_memory_persists_across_shadow_runs") is not True or policy.get("semantic_lane_or_pending_reduction_is_not_a_dead_end") is not True or policy.get("persistent_dead_end_requires_positive_counter_explanation") is not True or policy.get("search_control_closure_is_not_scientific_dead_end") is not True or policy.get("only_core_principle_enters_shadow_dead_end_memory") is not True or policy.get("holds_live_only_in_shadow_search_memory") is not True or policy.get("closed_basin_must_name_closure_layer") is not True or policy.get("scientific_closed_basin_must_use_canonical_failure_layer") is not True or policy.get("problem_novelty_stop_is_upstream_not_experimental_failure_layer") is not True or policy.get("scoped_closed_basin_is_not_automatically_principle_stop") is not True or policy.get("principle_stop_does_not_imply_benchmark_level_dead_end") is not True or policy.get("principle_stop_requires_explicit_stop_class_or_broader_falsification") is not True or policy.get("principle_readjudications_feed_opposite_search_control_only") is not True or policy.get("semantic_soft_collision_alone_is_not_a_dead_end") is not True:
        errors.append("SP design audit must remain retrospective zero-authority search control; upstream problem/novelty stops are separate and all scientific closures must use the canonical failure-layer schema")
    if (state.get("advisory_consultation") or {}).get("scientific_authority") is not False or (state.get("advisory_consultation") or {}).get("failed_or_missing_review_is_not_pass") is not True:
        errors.append("unavailable AI premortem reviewers must remain zero-authority and cannot count as PASS")
    search_memory = state.get("shadow_search_memory") or {}; closed_objects=_closed_objects(search_memory); hold_objects=[row for row in search_memory.get("hold_objects") or [] if isinstance(row,dict)]; closed_ids={str(row.get("source_candidate_id") or "") for row in closed_objects}; hold_ids={str(row.get("source_candidate_id") or "") for row in hold_objects}
    dead_memory = state.get("shadow_dead_end_memory") or {}; dead_objects=[row for row in dead_memory.get("blocked_objects") or [] if isinstance(row,dict)]
    if search_memory.get("scientific_authority") is not False or search_memory.get("live_source_coverage_effect") is not False or search_memory.get("cannot_mutate_canonical_generator_or_queue") is not True or search_memory.get("search_control_only") is not True or "blocked_objects" in search_memory or "SP-09" not in closed_ids or "SP-15" not in hold_ids or "SP-15" in closed_ids:
        errors.append("canonical shadow_search_memory must hold SP-09 as an upstream problem/novelty closure and SP-15 only as a reopenable HOLD, without using scientific dead-end container semantics")
    if any(row.get("search_closure_certified") is not True or audit_closed_row_layer(row).get("passed") is not True or row.get("dead_end_certified") is not (row.get("failure_layer") == "core_principle") or not isinstance(row.get("counter_explanation"),dict) or not str((row.get("counter_explanation") or {}).get("statement") or "").strip() or not str((row.get("counter_explanation") or {}).get("opposite_principle") or "").strip() or not str((row.get("counter_explanation") or {}).get("opposite_search_seed") or "").strip() or not (row.get("counter_explanation") or {}).get("evidence_refs") or not str(row.get("reopen_only_if") or "").strip() for row in closed_objects):
        errors.append("every search closure must carry a valid closure/failure layer and reopen contract; only core_principle closures may retain dead_end_certified=true")
    closure_counts = summarize_closure_layers(closed_objects)
    scientific_counts = summarize_scientific_failure_layers(closed_objects)
    broader_count=sum(row.get("broader_core_principle_falsified") is True for row in closed_objects)
    if int(search_memory.get("closed_basin_count") or 0) != len(closed_objects) or int(search_memory.get("closed_object_count") or 0) != len(closed_objects) or dict(search_memory.get("closure_layer_counts") or {}) != closure_counts or dict(search_memory.get("failure_layer_counts") or {}) != scientific_counts or int(search_memory.get("problem_novelty_stop_count") or 0) != closure_counts["problem_novelty"] or int(search_memory.get("execution_stop_count") or 0) != scientific_counts["execution"] or int(search_memory.get("experiment_identifiability_stop_count") or 0) != scientific_counts["experiment_identifiability"] or int(search_memory.get("optimization_stop_count") or 0) != scientific_counts["optimization"] or int(search_memory.get("operationalization_stop_count") or 0) != scientific_counts["operationalization"] or int(search_memory.get("method_realization_stop_count") or 0) != scientific_counts["method_realization"] or int(search_memory.get("assumption_scope_stop_count") or 0) != scientific_counts["assumption_scope"] or int(search_memory.get("core_principle_stop_count") or 0) != scientific_counts["core_principle"] or int(search_memory.get("broader_core_principle_falsification_count") or 0) != broader_count:
        errors.append("shadow_search_memory accounting must match upstream problem/novelty closures plus the canonical seven scientific failure layers")
    readjudicated=[row for row in closed_objects if str(row.get("basin") or "").startswith("principle-readjudication-")]
    readjudicated_core=[row for row in readjudicated if row.get("failure_layer")=="core_principle"]
    if int(search_memory.get("principle_readjudication_closed_basin_count") or 0)!=len(readjudicated) or int(search_memory.get("principle_readjudication_dead_end_count") or 0)!=len(readjudicated_core) or any(not str(row.get("source_readjudication_artifact") or "").strip() or row.get("scientific_authority") is not False for row in readjudicated):
        errors.append("principle readjudications must enter search memory as provenance-bound typed closures; only core_principle rows may project into scientific dead-end memory")
    closures=[row.get("fresh_phenomenon_closure") or {} for row in closed_objects if isinstance(row.get("fresh_phenomenon_closure"),dict) and row.get("fresh_phenomenon_closure")]
    if int(search_memory.get("fresh_phenomenon_closure_count") or 0)!=len(closures) or int(search_memory.get("fresh_phenomenon_closed_evidence_count") or 0)!=sum(len(row.get("closed_evidence_sha256") or []) for row in closures) or any(not str(row.get("source_ref") or "").startswith("arXiv:") or not row.get("closed_evidence_sha256") or row.get("scientific_authority") is not False or any(not re.fullmatch(r"[0-9a-f]{64}",str(value or "")) for value in row.get("closed_evidence_sha256") or []) for row in closures):
        errors.append("fresh phenomenon closures must remain exact-evidence, provenance-preserving search control")
    expected_dead=[row for row in closed_objects if row.get("failure_layer")=="core_principle" and row.get("principle_update_allowed") is True]
    if dead_memory.get("scientific_authority") is not False or dead_memory.get("persistent_dead_end_authority_scope") != "core_principle-only" or dead_memory.get("only_principle_stop_may_enter_persistent_dead_end_memory") is not True or dead_memory.get("hold_objects") not in ([],None) or int(dead_memory.get("principle_dead_end_count") or 0)!=len(expected_dead) or dead_objects!=expected_dead or any(row.get("failure_layer")!="core_principle" or row.get("principle_update_allowed") is not True or row.get("dead_end_certified") is not True for row in dead_objects):
        errors.append("shadow_dead_end_memory must be a core_principle-only projection of shadow_search_memory and must never contain HOLD or non-principle closures")
    if any(row.get("dead_end_certified") is not False for row in hold_objects):
        errors.append("reopenable HOLD objects cannot be scientific dead ends")
    dynamic=[row for row in closed_objects if str(row.get("basin") or "").startswith("current-source-hard-veto-")]
    hard_added=int(search_memory.get("current_source_hard_veto_added_from_terminal_run",search_memory.get("current_source_hard_veto_added_from_latest_run",0)) or 0)
    if int(search_memory.get("current_source_hard_veto_count") or 0)!=len(dynamic) or hard_added+int(search_memory.get("current_source_hard_veto_inherited") or 0)!=len(dynamic) or any(not str(row.get("strongest_reduction") or "").strip() or not row.get("current_source_refs") or not str(row.get("reopen_only_if") or "").strip() or row.get("scientific_authority") is not False for row in dynamic):
        errors.append("current-source hard vetoes must persist as bounded zero-authority search-closure fingerprints")
    semantic_dead=[row for row in closed_objects if str(row.get("basin") or "").startswith(("semantic-exact-reduction-","semantic-lane-contract-"))]
    semantic_holds=[row for row in hold_objects if str(row.get("basin") or "").startswith(("semantic-exact-reduction-","semantic-lane-contract-"))]
    semantic_hold_added=int(search_memory.get("semantic_hold_added_from_terminal_run",search_memory.get("semantic_hold_added_from_latest_run",0)) or 0)
    if semantic_dead or int(search_memory.get("semantic_blocker_count") or 0)!=0 or int(search_memory.get("semantic_hold_count") or 0)!=len(semantic_holds) or semantic_hold_added+int(search_memory.get("semantic_hold_inherited") or 0)!=len(semantic_holds) or any(row.get("scientific_authority") is not False or row.get("dead_end_certified") is not False or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip() for row in semantic_holds):
        errors.append("lane-contract and unresolved exact-reduction records must persist only as zero-authority reopenable holds")
    near_miss=state.get("shadow_near_miss_preflight") or {}; near_dead=[row for row in closed_objects if str(row.get("basin") or "").startswith("near-miss-")]; near_holds=[row for row in hold_objects if str(row.get("basin") or "").startswith("near-miss-")]
    base_near=int(search_memory.get("near_miss_base_preflight_count",(near_miss.get("summary") or {}).get("receipts",0)) or 0);terminal_holds=int(search_memory.get("near_miss_terminal_support_hold_count") or 0)
    if int(search_memory.get("near_miss_preflight_count") or 0)!=len(near_dead) or int(search_memory.get("near_miss_hold_count") or 0)!=len(near_holds) or int((near_miss.get("summary") or {}).get("receipts") or 0)!=base_near or terminal_holds>len(near_holds) or any(row.get("scientific_authority") is not False or not str(row.get("reopen_only_if") or "").strip() for row in near_dead+near_holds):
        errors.append("near-miss reductions/collisions must split into certified search closures while support-unavailable records remain holds")
    maintenance=state.get("shadow_memory_maintenance") or {}
    if maintenance and (maintenance.get("scientific_authority") is not False or (maintenance.get("policy") or {}).get("terminal_run_ingestion_is_zero_authority_search_control") is not True or (maintenance.get("policy") or {}).get("canonical_generator_and_queue_untouched") is not True or any(row.get("scientific_authority") is not False or not row.get("run_id") or not row.get("stage_manifest_sha256") for row in maintenance.get("receipts") or [] if isinstance(row,dict))):
        errors.append("terminal shadow-run memory maintenance must remain bounded zero-authority search control")
    for row in rows:
        if not row.get("primary_sources") or not row.get("cheapest_problem_falsifier") or row.get("method_design_authorized") is not False or row.get("gpu_authorized") is not False or row.get("live_paper_design_eligible") is not False or row.get("counterfactual_problem_gate_pass_does_not_grant_live_paper_design") is not True:
            errors.append(f"SP design row incomplete or illegally authoritative:{row.get('id')}")
    return sorted(set(errors))


def write_search_portfolio_design_adjudication(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_search_portfolio_design_adjudication()
    errors = validate_search_portfolio_design_adjudication(state)
    if errors:
        raise ValueError("Invalid Search Portfolio Paper Design adjudication:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SEARCH_PORTFOLIO_DESIGN_ADJUDICATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--merge-terminal-run-root", type=Path)
    args = parser.parse_args()
    result = merge_terminal_shadow_run_memory(run_root=args.merge_terminal_run_root) if args.merge_terminal_run_root else write_search_portfolio_design_adjudication()
    print(json.dumps(result, ensure_ascii=False, indent=2))
