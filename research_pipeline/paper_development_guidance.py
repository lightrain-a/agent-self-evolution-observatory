from __future__ import annotations

from typing import Any

from .iclr_agent_paper_template import TEMPLATE_ID as ICLR_TEMPLATE_ID, TEMPLATE_VERSION as ICLR_TEMPLATE_VERSION, audit_template_binding


SCHEMA_VERSION = "1.0"
GUIDANCE_ID = "SENIOR-PAPER-DEVELOPMENT-GUIDANCE-20260823"

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "human_advisor_guidance_is_development_context_not_scientific_truth": True,
    "scientific_evidence_closure_does_not_imply_manuscript_maturity": True,
    "initial_draft_status_does_not_demote_scientific_paper_state": True,
    "paper_development_guidance_cannot_change_paper_state": True,
    "paper_development_guidance_cannot_expand_claims": True,
    "paper_development_guidance_cannot_authorize_experiments": True,
    "new_experiment_requests_still_require_scientific_and_experiment_authority": True,
    "related_work_must_establish_problem_necessity_and_challenge_not_only_citations": True,
    "method_exposition_must_explain_intuition_design_principles_and_stepwise_details": True,
    "experiment_program_must_use_both_prior_work_protocols_and_method_specific_tests": True,
    "writing_must_prefer_clear_direct_concrete_language": True,
    "next_material_revision_should_bind_iclr_agent_paper_template_v1": True,
    "iclr_template_experiment_lane_planning_does_not_authorize_execution": True,
    "material_story_revision_after_results_requires_result_analysis": True,
    "result_analysis_must_separate_observed_supported_not_supported_and_failure_layer": True,
    "stopped_method_extension_may_redirect_paper_archetype_without_invalidating_independent_evidence": True,
}

CURRENT_PAPER_IDS = (
    "STRI",
    "AGENT-SAFETY-R9",
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
)

DIMENSIONS: tuple[dict[str, Any], ...] = (
    {
        "key": "problem_related_work",
        "title_zh": "问题必要性、Challenge 与 Related Work",
        "title_en": "Problem necessity, challenge, and related work",
        "goal_zh": "先让读者相信这个问题必须解决、为什么难，再说明现有方法分别做到哪里和还缺什么。Related Work 不是引用清单。",
        "goal_en": "First make the reader believe the problem matters and is genuinely difficult, then explain what existing method families solve and what remains. Related Work is not a citation list.",
        "required_fields": (
            "necessity_argument",
            "challenge_statement",
            "current_paradigm_map",
            "closest_work_boundaries",
            "residual_problem",
        ),
        "checks_zh": (
            "用具体场景和失败后果解释为什么值得做，而不是只说 benchmark 分数低。",
            "把 challenge 拆成可观察的困难：信息、优化、识别、长期性、组合性或系统约束。",
            "按方法族解释现有工作怎么做、为什么仍不够，再落到 closest-work novelty boundary。",
        ),
        "checks_en": (
            "Use concrete settings and failure consequences rather than only low benchmark scores.",
            "Decompose the challenge into observable difficulties such as information, optimization, identification, longitudinal, compositional, or system constraints.",
            "Explain how method families work and why they remain insufficient before stating the closest-work novelty boundary.",
        ),
    },
    {
        "key": "method_exposition",
        "title_zh": "方法核心 Intuition、设计理念与全部关键细节",
        "title_en": "Method intuition, design principles, and load-bearing details",
        "goal_zh": "方法章节必须先讲最简单的直觉，再讲为什么这样设计，然后逐步写清输入、状态、每个组件、操作顺序、假设、输出和失败边界。",
        "goal_en": "The method section must start from the simplest intuition, explain why the design follows, then specify inputs, state, each component, operation order, assumptions, outputs, and failure boundaries.",
        "required_fields": (
            "core_intuition",
            "design_principles",
            "input_output_contract",
            "step_by_step_flow",
            "component_rationales",
            "assumptions_and_held_fixed",
            "implementation_surface",
            "failure_modes",
        ),
        "checks_zh": (
            "每个组件都回答：为什么存在、拿掉会怎样、最简单替代是什么。",
            "区分核心科学机制与工程实现容器，不把 wrapper、prompt 或基础算法本身误卖成贡献。",
            "读者不看代码也能复述方法从输入到输出发生了什么。",
        ),
        "checks_en": (
            "For every component: why is it present, what should fail without it, and what is the simplest substitute?",
            "Separate the scientific mechanism from its engineering container; do not sell a wrapper, prompt, or standard primitive as the contribution.",
            "A reader should be able to restate the full input-to-output method without opening the code.",
        ),
    },
    {
        "key": "experiment_program",
        "title_zh": "更完整的实验 Program，而不是只有一张主表",
        "title_en": "A complete experimental program, not a single main table",
        "goal_zh": "实验一部分借鉴 closest work 的强 baseline / protocol，另一部分专门验证本文方法自己的结构特点；所有新增实验仍须单独过科学与执行门。",
        "goal_en": "Part of the experiment suite should borrow strong baselines/protocols from closest work, while another part should expose the proposed method's distinctive structure; every new execution still needs separate scientific and execution gates.",
        "required_fields": (
            "prior_work_inspired_baselines",
            "main_effects",
            "component_ablations",
            "method_characteristic_tests",
            "mechanism_tests",
            "robustness_and_generalization",
            "negative_and_failure_cases",
            "efficiency_and_cost",
            "statistical_plan",
        ),
        "checks_zh": (
            "从相关工作反推 reviewer 会期待哪些 baseline、数据切分和 robustness protocol。",
            "从方法自身反推独有实验：组件必要性、机制预测、边界条件、失败模式和复杂度/成本。",
            "不要为了‘实验多’而堆 benchmark；每个实验必须对应一个 claim、替代解释或 reviewer question。",
        ),
        "checks_en": (
            "Infer expected baselines, splits, and robustness protocols from the closest literature.",
            "Infer method-specific experiments from the proposed structure: component necessity, mechanism predictions, boundaries, failure modes, and cost/complexity.",
            "Do not add benchmarks for volume; every experiment must answer a claim, alternative explanation, or reviewer question.",
        ),
    },
    {
        "key": "writing_clarity",
        "title_zh": "讲人话：清晰、直白、易懂的论文写作",
        "title_en": "Plain, direct, reader-comprehensible writing",
        "goal_zh": "优先让读者一次读懂，再追求术语精确。能用普通动词和具体名词表达，就不要用抽象、堆叠、AI 味很重的词组。",
        "goal_en": "Optimize first-pass comprehension before stylistic sophistication. Prefer ordinary verbs and concrete nouns over abstract, stacked, AI-like phrasing whenever precision is preserved.",
        "required_fields": (
            "plain_language_summary",
            "term_definitions",
            "topic_sentence_rule",
            "one_sentence_one_job",
            "concrete_subject_verb_rule",
            "jargon_justification",
            "reader_simulation",
        ),
        "checks_zh": (
            "每节第一段先回答‘这一节要说明什么’，每个结果段先给答案再给数字。",
            "新术语首次出现必须用一句普通话解释；没有必要就不要造新术语。",
            "长句拆开，一句话只承担一个主要逻辑任务；减少名词堆叠、被动语态和空泛形容词。",
            "最终至少做一次不看内部项目背景的 reader simulation：读者能否复述问题、方法、实验和边界。",
        ),
        "checks_en": (
            "Open each section by saying what it establishes; open each result paragraph with the answer before the numbers.",
            "Define every new term in plain language on first use and avoid inventing jargon when ordinary language works.",
            "Split overloaded sentences; one sentence should carry one main logical job. Reduce noun stacks, passive voice, and vague adjectives.",
            "Run a reader simulation without internal project context: can a reader restate the problem, method, experiments, and boundaries?",
        ),
    },
)


def guidance_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "guidance_id": GUIDANCE_ID,
        "recorded_at": "2026-08-23",
        "scope": {
            "current_papers": list(CURRENT_PAPER_IDS),
            "applies_to_future_paper_design": True,
            "applies_to_manuscript_revision": True,
            "applies_to_mock_pc": True,
        },
        "paper_development_backlog": [
            {
                "paper_id": paper_id,
                "maturity": "INITIAL_DRAFT_NEEDS_DEEPENING",
                "human_approved_action": "DEEPEN_MANUSCRIPT_ON_FROZEN_SCIENTIFIC_BASE",
                "paper_only_work_allowed": True,
                "may_expand_related_work_and_problem_motivation": True,
                "may_expand_method_exposition": True,
                "may_design_future_experiment_program": True,
                "may_improve_writing_clarity": True,
                "may_change_supported_claims": False,
                "may_execute_new_experiments": False,
                "may_use_new_model_or_gpu_calls": False,
                "new_execution_requires_separate_scientific_reopen": True,
                "manuscript_template_id": ICLR_TEMPLATE_ID,
                "manuscript_template_version": ICLR_TEMPLATE_VERSION,
                "template_binding_required_on_next_material_revision": True,
            }
            for paper_id in CURRENT_PAPER_IDS
        ],
        "manuscript_template": {
            "template_id": ICLR_TEMPLATE_ID,
            "template_version": ICLR_TEMPLATE_VERSION,
            "generated_ref": "generated/iclr-agent-paper-template.json",
            "binding_required_on_next_material_revision": True,
            "experiment_lane_planning_is_not_execution": True,
        },
        "result_interpretation_rule": {
            "required_before_material_story_revision_after_new_results": True,
            "required_fields": [
                "observed findings bound to evidence",
                "estimand / scientific object",
                "positive implication",
                "negative boundary / what is not established",
                "strongest alternative explanation and disposition",
                "typed failure layer for HOLD/STOP",
                "does-not-imply boundary",
                "next scientific action and reusable lesson"
            ],
            "paper_routing_rule": "A method-extension STOP changes only the contribution layer it actually tests. If independently established phenomenon/mechanism/measurement evidence survives, select the appropriate paper archetype instead of manufacturing another method.",
            "authority": {"scientific": False, "experiment": False, "gpu": False}
        },
        "advisor_assessment": {
            "problem_value": "WORTH_PURSUING",
            "method_direction": "PLAUSIBLE_FOR_THE_STATED_PROBLEM",
            "current_manuscript_maturity": "INITIAL_DRAFT_NEEDS_DEEPENING",
            "scientific_stop_implied": False,
            "immediate_experiment_execution_implied": False,
            "interpretation_zh": "问题值得继续做，当前方法方向基本合理；主要不足是论文完成度：Related Work/必要性与挑战、方法阐述、实验覆盖和写作清晰度都需要继续深化。",
            "interpretation_en": "The problems remain worth pursuing and the current method directions are broadly plausible; the main gap is manuscript maturity: related-work/problem motivation, method exposition, experimental coverage, and writing clarity all need substantial deepening.",
        },
        "dimensions": [dict(row) for row in DIMENSIONS],
        "execution_status": "HUMAN_APPROVED_PAPER_DEVELOPMENT_BACKLOG_NO_AUTO_EXPERIMENT",
        "policy": dict(POLICY),
        "authority": {
            "scientific": False,
            "method": False,
            "experiment": False,
            "gpu": False,
            "submission": False,
        },
    }


def audit_development_quality(value: Any, *, required: bool) -> dict[str, Any]:
    contract = value if isinstance(value, dict) else {}
    blockers: list[str] = []
    dimension_status: dict[str, Any] = {}
    template_audit = audit_template_binding(contract.get("manuscript_template"), required=required)
    for spec in DIMENSIONS:
        key = str(spec["key"])
        row = contract.get(key) if isinstance(contract.get(key), dict) else {}
        missing = [field for field in spec["required_fields"] if not _nonempty(row.get(field))]
        dimension_status[key] = {
            "required_fields": len(spec["required_fields"]),
            "present_fields": len(spec["required_fields"]) - len(missing),
            "missing_fields": missing,
            "pass": not missing,
        }
        if required:
            blockers.extend(f"paper-development-field-missing:{key}:{field}" for field in missing)
    if required and not template_audit.get("passed"):
        blockers.extend(str(item) for item in template_audit.get("blockers") or [])
    if not required and not contract:
        return {
            "schema_version": SCHEMA_VERSION,
            "required": False,
            "passed": True,
            "status": "INITIAL_DRAFT_GUIDANCE_NOT_YET_BOUND",
            "blockers": [],
            "warnings": ["paper-development-quality-guidance-should-be-bound-on-next-material-paper-design-or-manuscript-revision"],
            "dimensions": dimension_status,
            "template_binding": template_audit,
            "policy": dict(POLICY),
            "scientific_authority": False,
        }
    passed = not blockers
    return {
        "schema_version": SCHEMA_VERSION,
        "required": required,
        "passed": passed,
        "status": "MATURE_DEVELOPMENT_CONTRACT" if passed else "DEVELOPMENT_REPAIR_REQUIRED",
        "blockers": sorted(set(blockers)),
        "warnings": [],
        "dimensions": dimension_status,
        "template_binding": template_audit,
        "policy": dict(POLICY),
        "scientific_authority": False,
    }


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None


def research_memory_entry() -> dict[str, Any]:
    payload = guidance_payload()
    return {
        "memory_id": "MEM-PDEV-SENIOR-20260823",
        "kind": "PAPER_DEVELOPMENT_GUIDANCE",
        "title": "Senior paper-development guidance: treat current versions as initial drafts",
        "summary": payload["advisor_assessment"]["interpretation_en"],
        "candidate_id": "",
        "scope": "current-five-papers-and-future-paper-design",
        "affected_layer": "paper_development",
        "memory_class": "HUMAN_ADVISOR_PAPER_DEVELOPMENT_GUIDANCE",
        "durability_class": "recurring-systemic",
        "prompt_eligible": True,
        "search_closure_certified": False,
        "scientific_dead_end_certified": False,
        "principle_update_allowed": False,
        "reopen_condition": "",
        "opposite_search_seed": "",
        "reusable_precheck": f"Bind {ICLR_TEMPLATE_ID} v{ICLR_TEMPLATE_VERSION} on the next material revision and fill E1-E6 as experiment-planning slots (or archetype-justified N/A); planning never authorizes execution. After any new result, first bind a result-analysis receipt that separates observed evidence, estimand, positive implication, negative boundary, strongest alternative explanation, typed failure layer, does-not-imply scope, next action, and reusable lesson. Then verify four dimensions: problem necessity/challenge and related-work map; method intuition/design principles/load-bearing details; experiments inspired by closest-work protocols and method-specific predictions; and plain, direct, reader-comprehensible writing. Treat missing depth as manuscript-development debt, not a scientific STOP, and treat a stopped method extension as a contribution-layer routing event rather than automatic whole-paper failure.",
        "source_refs": ["human-advisor-guidance:2026-08-23"],
        "source_artifact": GUIDANCE_ID,
        "guidance": payload,
        "reuse_effectiveness": {},
        "scientific_authority": False,
    }
