from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_shadow_near_miss_preflight import build_shadow_near_miss_preflight, compile_shadow_dead_end_rows

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.js"
SHADOW_PORTFOLIO_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-state.json"
SHADOW_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-queue-shadow.json"

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
    "canonical_generator_and_queue_untouched": True,
}


BASE_SHADOW_DEAD_END_MEMORY = {
    "memory_id": "shadow-paper-design-dead-ends-20260814-r1",
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
            "reopen_only_if": "Current primary evidence supports an ex-ante non-separability or impossibility prediction for the same skill under identical model/trigger/workflow/security/utility information that generic contextual governance cannot express.",
        },
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
            "reopen_only_if": "A new provenance-audited query-level unit shows that the same observable or information-equivalent query is compatible with multiple task semantics requiring incompatible sufficient skill sets, and a generic partial-identification/clarification baseline using the same information cannot absorb the claim.",
        },
    ],
}


def _prior_current_source_hard_veto_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = prior.get("shadow_dead_end_memory") or {}
    rows = []
    for row in memory.get("blocked_objects") or []:
        if not isinstance(row, dict) or not str(row.get("basin") or "").startswith("current-source-hard-veto-"):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("strongest_reduction") or "").strip() or not row.get("current_source_refs") or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
    return rows


def _prior_semantic_block_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = prior.get("shadow_dead_end_memory") or {}
    rows = []
    for row in memory.get("blocked_objects") or []:
        basin = str(row.get("basin") or "") if isinstance(row, dict) else ""
        if not basin.startswith(("semantic-exact-reduction-", "semantic-lane-contract-")):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
    return rows


def _prior_near_miss_rows(path: Path = DEFAULT_JSON) -> list[dict[str, Any]]:
    prior = _load_json(path)
    memory = prior.get("shadow_dead_end_memory") or {}
    rows = []
    for row in memory.get("blocked_objects") or []:
        basin = str(row.get("basin") or "") if isinstance(row, dict) else ""
        if not basin.startswith("near-miss-"):
            continue
        if row.get("scientific_authority") is not False or not str(row.get("reopen_only_if") or "").strip():
            continue
        rows.append(dict(row))
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
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": False,
        })
    return rows


def _shadow_dead_end_memory(portfolio: dict[str, Any], near_miss_state: dict[str, Any] | None = None, prior_hard_veto_rows: list[dict[str, Any]] | None = None, prior_semantic_rows: list[dict[str, Any]] | None = None, prior_near_miss_rows: list[dict[str, Any]] | None = None, extra_near_miss_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
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
            "source_run_id": str(latest.get("run_id") or ""),
            "source_stage_manifest_sha256": str(latest.get("stage_manifest_sha256") or ""),
            "scientific_authority": False,
        }
    hard_rows = [hard_by_basin[key] for key in sorted(hard_by_basin)]
    memory["blocked_objects"].extend(hard_rows)

    semantic_inherited = _prior_semantic_block_rows() if prior_semantic_rows is None else [dict(row) for row in prior_semantic_rows if isinstance(row, dict)]
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
                "scientific_authority": False,
            }
    semantic_rows = [semantic_by_basin[key] for key in sorted(semantic_by_basin)]
    memory["blocked_objects"].extend(semantic_rows)
    near_miss_state = near_miss_state or build_shadow_near_miss_preflight()
    base_near_miss_rows = compile_shadow_dead_end_rows(near_miss_state)
    near_inherited = _prior_near_miss_rows() if prior_near_miss_rows is None else [dict(row) for row in prior_near_miss_rows if isinstance(row, dict)]
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
    memory["memory_id"] = "shadow-paper-design-dead-ends-persistent-current-source-semantic-near-miss"
    memory["current_source_hard_veto_count"] = len(hard_rows)
    memory["current_source_hard_veto_added_from_latest_run"] = added
    memory["current_source_hard_veto_added_from_terminal_run"] = added
    memory["current_source_hard_veto_inherited"] = max(0, len(hard_rows) - added)
    memory["semantic_blocker_count"] = len(semantic_rows)
    memory["semantic_blocker_added_from_latest_run"] = semantic_added
    memory["semantic_blocker_added_from_terminal_run"] = semantic_added
    memory["semantic_blocker_inherited"] = max(0, len(semantic_rows) - semantic_added)
    memory["near_miss_preflight_count"] = len(near_miss_rows)
    memory["near_miss_base_preflight_count"] = len(base_near_miss_rows)
    memory["near_miss_terminal_support_hold_count"] = sum(str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-") for row in near_miss_rows)
    memory["scientific_authority"] = False
    return memory


def merge_shadow_terminal_run_memory(state: dict[str, Any], terminal_run: dict[str, Any], preflight: dict[str, Any] | None = None) -> dict[str, Any]:
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
    prior_memory = merged.get("shadow_dead_end_memory") or {}
    prior_blocked = [row for row in prior_memory.get("blocked_objects") or [] if isinstance(row, dict)]
    prior_hard = [dict(row) for row in prior_blocked if str(row.get("basin") or "").startswith("current-source-hard-veto-")]
    prior_semantic = [dict(row) for row in prior_blocked if str(row.get("basin") or "").startswith(("semantic-exact-reduction-", "semantic-lane-contract-"))]
    prior_near = [dict(row) for row in prior_blocked if str(row.get("basin") or "").startswith("near-miss-")]
    extra_near = _terminal_support_hold_rows(preflight, run_id=run_id, stage_manifest_sha256=stage_manifest_sha256)

    memory = _shadow_dead_end_memory(
        {"latest_run": terminal_run},
        near_miss_state=merged.get("shadow_near_miss_preflight") or build_shadow_near_miss_preflight(),
        prior_hard_veto_rows=prior_hard,
        prior_semantic_rows=prior_semantic,
        prior_near_miss_rows=prior_near,
        extra_near_miss_rows=extra_near,
    )
    merged["shadow_dead_end_memory"] = memory
    summary = merged.setdefault("summary", {})
    summary.update({
        "shadow_dead_end_objects": len(memory.get("blocked_objects") or []),
        "current_source_hard_veto_dead_ends": int(memory.get("current_source_hard_veto_count") or 0),
        "current_source_hard_veto_added_from_latest_run": 0,
        "current_source_hard_veto_added_from_terminal_run": int(memory.get("current_source_hard_veto_added_from_terminal_run") or 0),
        "current_source_hard_veto_inherited": int(memory.get("current_source_hard_veto_inherited") or 0),
        "semantic_blocker_dead_ends": int(memory.get("semantic_blocker_count") or 0),
        "semantic_blocker_added_from_latest_run": 0,
        "semantic_blocker_added_from_terminal_run": int(memory.get("semantic_blocker_added_from_terminal_run") or 0),
        "semantic_blocker_inherited": int(memory.get("semantic_blocker_inherited") or 0),
        "near_miss_preflight_dead_ends": int(memory.get("near_miss_preflight_count") or 0),
        "near_miss_terminal_support_holds": int(memory.get("near_miss_terminal_support_hold_count") or 0),
    })
    memory["current_source_hard_veto_added_from_latest_run"] = 0
    memory["semantic_blocker_added_from_latest_run"] = 0

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
        "semantic_blocker_added": max(0, int(memory.get("semantic_blocker_count") or 0) - before_semantic),
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
    state = _load_json(json_path)
    merged = merge_shadow_terminal_run_memory(state, terminal_run, preflight)
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
    dead_end_memory = _shadow_dead_end_memory(portfolio, near_miss_preflight)
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
            "semantic_blocker_memory_persists_across_shadow_runs": True,
            "semantic_soft_collision_alone_is_not_a_dead_end": True,
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
            "current_source_hard_veto_dead_ends": int(dead_end_memory.get("current_source_hard_veto_count") or 0),
            "current_source_hard_veto_added_from_latest_run": int(dead_end_memory.get("current_source_hard_veto_added_from_latest_run") or 0),
            "current_source_hard_veto_added_from_terminal_run": int(dead_end_memory.get("current_source_hard_veto_added_from_terminal_run") or 0),
            "current_source_hard_veto_inherited": int(dead_end_memory.get("current_source_hard_veto_inherited") or 0),
            "semantic_blocker_dead_ends": int(dead_end_memory.get("semantic_blocker_count") or 0),
            "semantic_blocker_added_from_latest_run": int(dead_end_memory.get("semantic_blocker_added_from_latest_run") or 0),
            "semantic_blocker_added_from_terminal_run": int(dead_end_memory.get("semantic_blocker_added_from_terminal_run") or 0),
            "semantic_blocker_inherited": int(dead_end_memory.get("semantic_blocker_inherited") or 0),
            "near_miss_preflight_dead_ends": int(dead_end_memory.get("near_miss_preflight_count") or 0),
            "near_miss_terminal_support_holds": int(dead_end_memory.get("near_miss_terminal_support_hold_count") or 0),
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
    if policy.get("source_is_shadow_search_portfolio") is not True or policy.get("shadow_queue_has_zero_paper_design_authority") is not True or policy.get("cannot_grant_or_revoke_live_paper_design_authority") is not True or policy.get("current_source_hard_veto_memory_persists_across_shadow_runs") is not True or policy.get("semantic_blocker_memory_persists_across_shadow_runs") is not True or policy.get("semantic_soft_collision_alone_is_not_a_dead_end") is not True:
        errors.append("SP design audit must remain retrospective shadow feedback with zero live Paper Design authority")
    if (state.get("advisory_consultation") or {}).get("scientific_authority") is not False or (state.get("advisory_consultation") or {}).get("failed_or_missing_review_is_not_pass") is not True:
        errors.append("unavailable AI premortem reviewers must remain zero-authority and cannot count as PASS")
    memory = state.get("shadow_dead_end_memory") or {}; blocked_objects=[row for row in memory.get("blocked_objects") or [] if isinstance(row,dict)]; blocked_ids={str(row.get("source_candidate_id") or "") for row in blocked_objects}
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True or not {"SP-09","SP-15"}.issubset(blocked_ids):
        errors.append("Paper Design dead-end memory must remain shadow-only and retain both SP-09/SP-15 basins")
    dynamic=[row for row in blocked_objects if str(row.get("basin") or "").startswith("current-source-hard-veto-")]
    hard_added=int(memory.get("current_source_hard_veto_added_from_terminal_run",memory.get("current_source_hard_veto_added_from_latest_run",0)) or 0)
    if int(memory.get("current_source_hard_veto_count") or 0)!=len(dynamic) or hard_added+int(memory.get("current_source_hard_veto_inherited") or 0)!=len(dynamic) or any(not str(row.get("strongest_reduction") or "").strip() or not row.get("current_source_refs") or not str(row.get("reopen_only_if") or "").strip() or row.get("scientific_authority") is not False for row in dynamic):
        errors.append("current-source hard vetoes must persist as bounded zero-authority shadow dead-end fingerprints")
    semantic_rows=[row for row in blocked_objects if str(row.get("basin") or "").startswith(("semantic-exact-reduction-","semantic-lane-contract-"))]
    semantic_added=int(memory.get("semantic_blocker_added_from_terminal_run",memory.get("semantic_blocker_added_from_latest_run",0)) or 0)
    if int(memory.get("semantic_blocker_count") or 0)!=len(semantic_rows) or semantic_added+int(memory.get("semantic_blocker_inherited") or 0)!=len(semantic_rows) or any(row.get("scientific_authority") is not False or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip() for row in semantic_rows):
        errors.append("semantic reduction/lane blockers must persist as bounded zero-authority shadow dead-end fingerprints")
    near_miss=state.get("shadow_near_miss_preflight") or {}; near_rows=[row for row in blocked_objects if str(row.get("basin") or "").startswith("near-miss-")]
    base_near=int(memory.get("near_miss_base_preflight_count",(near_miss.get("summary") or {}).get("receipts",0)) or 0);terminal_holds=int(memory.get("near_miss_terminal_support_hold_count") or 0)
    if int(memory.get("near_miss_preflight_count") or 0)!=len(near_rows) or base_near+terminal_holds!=len(near_rows) or int((near_miss.get("summary") or {}).get("receipts") or 0)!=base_near or any(row.get("scientific_authority") is not False or not str(row.get("reopen_only_if") or "").strip() for row in near_rows):
        errors.append("near-miss preflight and terminal support-hold receipts must compile into bounded zero-authority shadow dead-end fingerprints")
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
