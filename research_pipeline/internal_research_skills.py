from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "external_skill_packs_are_design_inputs_not_runtime_dependencies": True,
    "distilled_internal_skills_are_owned_by_research_os": True,
    "internal_skill_cannot_become_a_second_research_orchestration_authority": True,
    "internal_skill_cannot_grant_scientific_experiment_gpu_or_submission_authority": True,
    "domain_skill_routes_only_when_its_domain_capability_is_requested": True,
    "missing_evidence_must_surface_as_missing_input_not_invented_content": True,
    "outcome_contingent_analysis_tuning_is_forbidden": True,
    "writer_and_reviewer_roles_remain_separate": True,
}

# The external packs remain only as provenance for why a local rule exists. Nothing
# below requires those repositories at runtime, and their orchestration/install layers
# are deliberately not copied into Research OS.
EXTERNAL_SKILL_DISTILLATION: tuple[dict[str, Any], ...] = (
    {
        "source_pack": "Academic Research Skills",
        "decision": "DISTILLED",
        "kept": ["reference existence/provenance checks", "atomic research artifacts", "reviewer reports but does not edit"],
        "discarded": ["external project scaffold", "parallel end-to-end research orchestration", "duplicate paper workflow"],
        "internal_skills": ["source-evidence-integrity", "evidence-first-manuscript"],
    },
    {
        "source_pack": "Scientific Agent Skills",
        "decision": "DISTILLED",
        "kept": ["assumption-aware statistics", "effect size and uncertainty", "scientific-computing and visualization checks"],
        "discarded": ["large unrelated domain catalog", "package-specific tutorials that do not encode a scientific invariant"],
        "internal_skills": ["statistical-analysis-core", "signal-scientific-computing"],
    },
    {
        "source_pack": "nature-skills",
        "decision": "DISTILLED",
        "kept": ["evidence-first drafting", "claim-evidence adjacency", "verb strength calibrated to evidence", "missing-input placeholders", "adversarial self-review"],
        "discarded": ["Nature-specific stylistic imitation as a scientific criterion", "duplicate submission orchestration", "generic prose polishing with no research invariant"],
        "internal_skills": ["evidence-first-manuscript"],
    },
    {
        "source_pack": "Claude Scholar",
        "decision": "DISTILLED",
        "kept": ["reference metadata verification", "pre-submission deterministic checks", "math/figure verification principle"],
        "discarded": ["plugin command surface", "provider-specific installation workflow", "duplicate manuscript critique workflow"],
        "internal_skills": ["source-evidence-integrity", "formal-math-verification"],
    },
    {
        "source_pack": "Auto-Empirical Research Skills",
        "decision": "DISTILLED",
        "kept": ["estimand-first causal design", "identification assumptions", "placebo/robustness checks", "numeric benchmark mindset"],
        "discarded": ["thousands of vendored prompt skills", "paper-workflow meta-orchestrator", "domain methods not requested by the current task"],
        "internal_skills": ["causal-empirical-analysis", "statistical-analysis-core"],
    },
    {
        "source_pack": "AI-Research-SKILLs",
        "decision": "DISTILLED",
        "kept": ["reproducible ML training/evaluation practice", "evaluation contamination checks", "resource/runtime provenance", "domain-specific engineering troubleshooting"],
        "discarded": ["autoresearch orchestrator", "install-all behavior", "paper/idea authority", "continuous-loop authority"],
        "internal_skills": ["ai-ml-experiment-engineering"],
    },
    {
        "source_pack": "codex-claude-academic-skills",
        "decision": "DISTILLED",
        "kept": ["MATLAB/Python scientific computing", "signal-processing numerical checks", "unit/sample-rate/frequency-domain discipline"],
        "discarded": ["office-document skill", "duplicate research-writing skill", "generic formatting helpers"],
        "internal_skills": ["signal-scientific-computing"],
    },
    {
        "source_pack": "Research Paper Writing Skills",
        "decision": "DISTILLED",
        "kept": ["section/paragraph argument flow", "first-use terminology explanation", "claim-support alignment", "reviewer-facing self-check"],
        "discarded": ["standalone writer orchestration", "style rules already covered by evidence-first manuscript policy"],
        "internal_skills": ["evidence-first-manuscript"],
    },
)

CANONICAL_INTERNAL_SKILLS: tuple[dict[str, Any], ...] = (
    {
        "skill_id": "source-evidence-integrity",
        "version": "1.0",
        "capabilities": ["literature", "citation", "reviewing"],
        "task_families": ["literature", "citation-audit", "manuscript-integrity"],
        "required_inputs": ["claim_or_reference_inventory", "primary_or_official_source_access", "frozen_cutoff_or_version"],
        "procedure": [
            "resolve reference identity against primary/official scholarly metadata",
            "bind exact passage or authoritative metadata to the claim",
            "check directionality, numerical agreement, and citation scope",
            "surface NOT_FOUND/MISMATCH/UNSUPPORTED instead of guessing",
        ],
        "quality_gates": ["reference-existence", "metadata-identity", "passage-support", "directionality", "numeric-match", "scope-match"],
        "expected_artifacts": ["citation-integrity-receipt", "claim-source-binding"],
        "forbidden_actions": ["invent-reference", "infer-source-support-from-title-only", "silently-correct-unverified-metadata"],
        "authority": "evidence-verification-only",
    },
    {
        "skill_id": "statistical-analysis-core",
        "version": "1.0",
        "capabilities": ["statistics", "experiment"],
        "task_families": ["analysis", "experiment-analysis", "paper-results"],
        "required_inputs": ["frozen_analysis_question", "immutable_data_or_metric_table", "analysis_plan_or_declared_exploratory_status"],
        "procedure": [
            "identify estimand/quantity and comparison unit before choosing a test",
            "check distributional/design assumptions and paired/cluster structure",
            "report effect size and uncertainty, not only p-values",
            "run preregistered robustness/sensitivity checks and preserve negative results",
        ],
        "quality_gates": ["estimand-defined", "assumptions-checked", "effect-size-reported", "uncertainty-reported", "multiplicity-or-selection-accounted", "analysis-provenance-bound"],
        "expected_artifacts": ["analysis-receipt", "statistical-result-table", "assumption-diagnostics"],
        "forbidden_actions": ["outcome-driven-test-selection", "posthoc-exclusion-without-disclosure", "pvalue-only-claim", "hide-null-result"],
        "authority": "interpretation-proposal-only",
    },
    {
        "skill_id": "causal-empirical-analysis",
        "version": "1.0",
        "capabilities": ["causal-inference", "statistics", "coding"],
        "task_families": ["causal-empirical"],
        "requires_explicit_domain_capability": "causal-inference",
        "required_inputs": ["target_estimand", "treatment_or_exposure", "outcome", "identification_assumptions", "data_provenance"],
        "procedure": [
            "state estimand and identification strategy before estimation",
            "make identifying assumptions testable where possible",
            "run design-specific diagnostics/placebos/negative controls",
            "separate identification failure from estimator/runtime failure",
            "bind tables/figures to reproducible code and data versions",
        ],
        "quality_gates": ["estimand-frozen", "identification-assumptions-explicit", "diagnostics-run", "robustness-run", "data-code-provenance-bound"],
        "expected_artifacts": ["identification-certificate", "causal-analysis-receipt", "robustness-table"],
        "forbidden_actions": ["causal-language-from-association-only", "choose-design-after-seeing-effect", "silent-sample-redefinition"],
        "authority": "interpretation-proposal-only",
    },
    {
        "skill_id": "ai-ml-experiment-engineering",
        "version": "1.0",
        "capabilities": ["ml-research", "experiment", "coding"],
        "task_families": ["ai-ml-experiment"],
        "requires_explicit_domain_capability": "ml-research",
        "required_inputs": ["execution_authorized_manifest", "frozen_model_and_data_identity", "evaluation_protocol", "resource_contract"],
        "procedure": [
            "freeze model/checkpoint/data split/prompt/inference and evaluator versions before confirmatory outcomes",
            "run smoke/pilot before expensive scale-up and persist incremental artifacts",
            "match baseline information/calls/tokens/optimization and hardware where load-bearing",
            "audit benchmark/web contamination and hidden-evaluation access",
            "record seeds, runtime, resources, failures, and all completed branches",
        ],
        "quality_gates": ["execution-identity-frozen", "smoke-pass", "baseline-fairness", "contamination-audit", "resource-provenance", "all-results-retained"],
        "expected_artifacts": ["experiment-manifest", "raw-trace", "progress-cursor", "metric-table", "runtime-provenance"],
        "forbidden_actions": ["self-authorize-experiment", "self-authorize-gpu", "retune-on-hidden-outcome", "drop-negative-branch", "become-autoresearch-orchestrator"],
        "authority": "execution-only-after-external-authority",
    },
    {
        "skill_id": "signal-scientific-computing",
        "version": "1.0",
        "capabilities": ["signal-processing", "statistics", "coding", "visualization"],
        "task_families": ["signal-processing", "scientific-computing"],
        "requires_explicit_domain_capability": "signal-processing",
        "required_inputs": ["signal_definition_and_units", "sampling_rate_or_axis", "frozen_processing_chain", "reference_or_synthetic_sanity_case"],
        "procedure": [
            "verify units, axes, sampling assumptions, Nyquist/aliasing and windowing before interpretation",
            "cross-check time-domain and frequency-domain quantities when applicable",
            "validate filters/transforms on a known synthetic or analytical sanity case",
            "separate numerical/implementation failure from scientific effect",
            "save code, parameters, source data and figure-data provenance",
        ],
        "quality_gates": ["units-and-axis-explicit", "sampling-valid", "numerical-sanity-pass", "transform-or-filter-parameters-frozen", "figure-data-bound"],
        "expected_artifacts": ["scientific-computing-receipt", "parameter-manifest", "numeric-sanity-result", "figure-data"],
        "forbidden_actions": ["ignore-unit-mismatch", "interpret-aliased-spectrum", "posthoc-filter-for-desired-result", "figure-without-source-data"],
        "authority": "diagnostic-or-execution-only-after-external-authority",
    },
    {
        "skill_id": "formal-math-verification",
        "version": "1.0",
        "capabilities": ["reviewing", "coding"],
        "task_families": ["math-verification", "theory-audit"],
        "required_inputs": ["frozen_statement", "definitions_and_assumptions", "derivation_or_proof_steps"],
        "procedure": [
            "check symbol/definition consistency and assumption use",
            "verify algebraic steps with symbolic/numeric tools where appropriate",
            "construct boundary/counterexample checks for claimed generality",
            "report unresolved steps rather than completing them by invention",
        ],
        "quality_gates": ["definitions-complete", "assumptions-traceable", "derivation-checked", "boundary-or-counterexample-checked"],
        "expected_artifacts": ["math-verification-receipt", "checked-derivation"],
        "forbidden_actions": ["invent-missing-assumption", "treat-numeric-check-as-general-proof", "silently-rewrite-theorem"],
        "authority": "verification-only",
    },
    {
        "skill_id": "evidence-first-manuscript",
        "version": "1.0",
        "capabilities": ["writing", "reviewing", "visualization"],
        "task_families": ["paper-writing", "paper-revision", "manuscript-polish"],
        "required_inputs": ["frozen_claim_boundary", "claim_evidence_graph", "paper_archetype_or_story_contract", "venue_constraints"],
        "procedure": [
            "plan argument/section flow before long prose when structure is material",
            "draft outward from evidence and keep claims adjacent to supporting data",
            "calibrate verbs and causal language to evidence strength",
            "define terminology and components at first use with input/output/purpose",
            "use placeholders/missing-input list instead of inventing facts, numbers, mechanisms or references",
            "run reader-comprehension and reviewer-facing self-check after drafting",
        ],
        "quality_gates": ["claim-evidence-adjacency", "evidence-strength-language", "first-use-definitions", "missing-inputs-surfaced", "limitations-preserved", "machine-like-prose-lint"],
        "expected_artifacts": ["manuscript-draft", "claim-evidence-map", "missing-input-checklist", "editorial-audit"],
        "forbidden_actions": ["invent-data", "invent-reference", "strengthen-claim-for-story", "add-method-complexity-for-novelty", "edit-scientific-truth"],
        "authority": "editorial-only",
    },
)


def _skill_index() -> dict[str, dict[str, Any]]:
    return {str(row["skill_id"]): dict(row) for row in CANONICAL_INTERNAL_SKILLS}


def validate_internal_skill_library() -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for row in CANONICAL_INTERNAL_SKILLS:
        sid = str(row.get("skill_id") or "")
        if not sid or sid in ids:
            errors.append(f"internal-skill-id-invalid:{sid or 'EMPTY'}")
        ids.add(sid)
        for field in ("capabilities", "required_inputs", "procedure", "quality_gates", "expected_artifacts", "forbidden_actions", "authority"):
            if not row.get(field):
                errors.append(f"internal-skill-field-missing:{sid}:{field}")
        if any(token in str(row.get("authority") or "").lower() for token in ("scientific-authority", "gpu-authority", "submission-authority")):
            errors.append(f"internal-skill-authority-invalid:{sid}")
    known = ids
    for source in EXTERNAL_SKILL_DISTILLATION:
        targets = [str(x) for x in source.get("internal_skills") or []]
        if not targets:
            errors.append(f"external-distillation-has-no-target:{source.get('source_pack')}")
        for target in targets:
            if target not in known:
                errors.append(f"external-distillation-target-missing:{source.get('source_pack')}:{target}")
    return errors


def compile_internal_skill_job(skill_id: str, task: dict[str, Any]) -> dict[str, Any]:
    skill = _skill_index().get(str(skill_id))
    if not skill:
        return {"schema_version": SCHEMA_VERSION, "status": "INTERNAL_SKILL_JOB_HOLD", "skill_id": str(skill_id), "blockers": ["unknown-internal-skill"], "scientific_authority": False, "experiment_authority": False, "gpu_authority": False}
    provided = {str(x) for x in task.get("provided_inputs") or []}
    missing = [str(x) for x in skill.get("required_inputs") or [] if str(x) not in provided]
    explicit = str(skill.get("requires_explicit_domain_capability") or "")
    requested_caps = {str(x) for x in task.get("capability_types") or []}
    blockers = [f"missing-skill-input:{value}" for value in missing]
    if explicit and explicit not in requested_caps:
        blockers.append(f"domain-skill-requires-explicit-capability:{explicit}")
    if task.get("requests_scientific_authority") is True or task.get("requests_experiment_authority") is True or task.get("requests_gpu_authority") is True:
        blockers.append("internal-skill-cannot-grant-requested-authority")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "INTERNAL_SKILL_JOB_READY" if not blockers else "INTERNAL_SKILL_JOB_HOLD",
        "skill_id": skill_id,
        "skill_version": skill.get("version"),
        "capabilities": list(skill.get("capabilities") or []),
        "procedure": list(skill.get("procedure") or []),
        "quality_gates": list(skill.get("quality_gates") or []),
        "expected_artifacts": list(skill.get("expected_artifacts") or []),
        "forbidden_actions": list(skill.get("forbidden_actions") or []),
        "blockers": blockers,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def route_internal_skills(requirements: dict[str, Any]) -> dict[str, Any]:
    required = {str(x).strip().lower() for x in requirements.get("capability_types") or [] if str(x).strip()}
    task_family = str(requirements.get("task_family") or "").strip().lower()
    candidates: list[tuple[int, int, str, dict[str, Any], set[str]]] = []
    for skill in CANONICAL_INTERNAL_SKILLS:
        caps = {str(x) for x in skill.get("capabilities") or []}
        covers = required.intersection(caps)
        if not covers:
            continue
        explicit = str(skill.get("requires_explicit_domain_capability") or "")
        if explicit and explicit not in required:
            continue
        families = {str(x).lower() for x in skill.get("task_families") or []}
        family_penalty = 0 if task_family and task_family in families else 1
        candidates.append((family_penalty, -len(covers), str(skill.get("skill_id") or ""), skill, covers))
    selected: list[dict[str, Any]] = []
    uncovered = set(required)
    while uncovered:
        live = [row for row in candidates if row[4].intersection(uncovered)]
        if not live:
            break
        family_penalty, _, _, skill, _ = min(live, key=lambda row: (row[0], -len(row[4].intersection(uncovered)), row[2]))
        covers = {str(x) for x in skill.get("capabilities") or []}.intersection(uncovered)
        selected.append({"skill_id": skill.get("skill_id"), "skill_version": skill.get("version"), "covers": sorted(covers), "task_family_match": family_penalty == 0})
        uncovered -= covers
    blockers: list[str] = []
    if uncovered:
        blockers.append("internal-capability-unavailable:" + ",".join(sorted(uncovered)))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "INTERNAL_SKILL_ROUTE_READY" if not blockers else "INTERNAL_SKILL_ROUTE_HOLD",
        "task_family": task_family,
        "required_capabilities": sorted(required),
        "selected_skills": selected,
        "uncovered_capabilities": sorted(uncovered),
        "blockers": blockers,
        "external_runtime_dependencies": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def build_internal_research_skill_state() -> dict[str, Any]:
    errors = validate_internal_skill_library()
    source_counts = Counter(str(row.get("decision") or "") for row in EXTERNAL_SKILL_DISTILLATION)
    discarded_items = sum(len(row.get("discarded") or []) for row in EXTERNAL_SKILL_DISTILLATION)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "INTERNAL_RESEARCH_SKILLS_READY" if not errors else "INTERNAL_RESEARCH_SKILLS_INVALID",
        "policy": dict(POLICY),
        "external_distillation": [dict(row) for row in EXTERNAL_SKILL_DISTILLATION],
        "skills": [dict(row) for row in CANONICAL_INTERNAL_SKILLS],
        "validation_errors": errors,
        "summary": {
            "external_skill_packs_reviewed": len(EXTERNAL_SKILL_DISTILLATION),
            "external_skill_packs_distilled": source_counts.get("DISTILLED", 0),
            "external_skill_packs_left_catalogued": 0,
            "canonical_internal_skills": len(CANONICAL_INTERNAL_SKILLS),
            "discarded_external_surfaces": discarded_items,
            "external_runtime_dependencies": 0,
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
        },
        "scientific_authority": False,
    }
