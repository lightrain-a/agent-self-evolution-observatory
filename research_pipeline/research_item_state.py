from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings, resolve_experiment_data_root
from .paper_acceptance_ledger import build_paper_ledger_index, build_portable_paper_ledger_index

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED = PROJECT_ROOT / "generated"

CATEGORY_DEFINITIONS = {
    "A": {"title": {"zh": "更新可靠性与回归控制", "en": "Reliable updates and regression control"}},
    "B": {"title": {"zh": "记忆、经验与持久知识", "en": "Memory, experience, and persistent knowledge"}},
    "C": {"title": {"zh": "评价器、奖励与自纠正", "en": "Evaluators, rewards, and self-correction"}},
    "D": {"title": {"zh": "任务生成与课程", "en": "Task generation and curricula"}},
    "E": {"title": {"zh": "技能、工具与工作流演化", "en": "Skill, tool, and workflow evolution"}},
    "F": {"title": {"zh": "世界模型与具身适应", "en": "World models and embodied adaptation"}},
    "G": {"title": {"zh": "Agent 自进化安全与未来风险", "en": "Safety and future risk in agent self-evolution"}},
}

# Reader-facing paper identifiers deliberately live beside the PaperRegistry
# projection rather than in scientific ResearchItem IDs. Registrations are
# append-only: once a paper category is declared, its category-local ordinal
# is allocated from registration order (E1, E2, ...). Adding a future paper
# therefore requires only an explicit category/method/idea registration; it
# must never reuse or renumber an existing publication code.
PUBLICATION_CATEGORY_LABELS = {
    "A": {"zh": "治理", "en": "Governance"},
    "B": {"zh": "记忆", "en": "Memory"},
    "C": {"zh": "评估", "en": "Evaluation"},
    "D": {"zh": "课程", "en": "Curriculum"},
    "E": {"zh": "技能", "en": "Skills"},
    "F": {"zh": "世界模型", "en": "World Models"},
    "G": {"zh": "安全", "en": "Safety"},
}
PUBLICATION_PAPER_REGISTRATIONS = [
    {"paper_id": "STRI", "category": "E", "method": "STRI", "pdf_slug": "STRI", "idea": {"zh": "技能分类表示不变性", "en": "Skill-taxonomy representation invariance"}},
    {"paper_id": "AGENT-SAFETY-R9", "category": "G", "method": "R9", "pdf_slug": "Agent-Safety-R9", "idea": {"zh": "静态安全不等于未来安全", "en": "A static safety pass is not future safety"}},
    {"paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE", "category": "C", "method": "Proxy Reward", "pdf_slug": "Proxy-Reward", "idea": {"zh": "奖励误差写入长期记忆", "en": "Reward errors become persistent memory state"}},
    {"paper_id": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK", "category": "E", "method": "Temporal Skill", "pdf_slug": "Temporal-Skill", "idea": {"zh": "可复用技能的因果瓶颈", "en": "Reusable skills as causal bottlenecks"}},
    {"paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE", "category": "B", "method": "Provenance Ladder", "pdf_slug": "Failure-Memory", "idea": {"zh": "失败记忆来源的因果识别", "en": "Causal identification of failure-memory provenance"}},
]

# Historical discovery IDs such as D2-C06 predate the A–G publication
# taxonomy. In those IDs, D means discovery batch and C means candidate; they
# are not A–G categories. Reader-facing provenance therefore uses an explicit
# DISC alias while retaining the original IDs unchanged for exact replay.
DISCOVERY_CANDIDATE_PATTERN = re.compile(r"^D(?P<batch>[1-9][0-9]*)-C(?P<candidate>[0-9]+)$")


def discovery_candidate_alias(candidate_id: str) -> str:
    raw = str(candidate_id or "").strip()
    match = DISCOVERY_CANDIDATE_PATTERN.fullmatch(raw)
    if not match:
        raise ValueError(f"unsupported historical discovery candidate id:{raw}")
    batch = int(match.group("batch"))
    candidate = int(match.group("candidate"))
    return f"DISC{batch}-{candidate:02d}"


def build_discovery_provenance(candidate_ids: list[str]) -> dict[str, Any]:
    historical = [str(candidate_id) for candidate_id in candidate_ids]
    aliases = [discovery_candidate_alias(candidate_id) for candidate_id in historical]
    batches = {int(DISCOVERY_CANDIDATE_PATTERN.fullmatch(candidate_id).group("batch")) for candidate_id in historical}
    if len(batches) != 1:
        raise ValueError(f"mixed discovery batches are not reader-displayable:{historical}")
    batch = next(iter(batches))
    return {
        "campaign_alias": f"DISC{batch}",
        "campaign_zh": f"Paper-first 发现第 {batch} 轮",
        "campaign_en": f"Paper-first Discovery Round {batch}",
        "candidate_aliases": aliases,
        "primary_candidate_alias": aliases[0],
        "historical_candidate_ids": historical,
        "historical_ids_hidden_by_default": True,
        "reader_label": " + ".join(aliases),
    }


def build_publication_identities() -> dict[str, dict[str, Any]]:
    counters: Counter[str] = Counter()
    identities: dict[str, dict[str, Any]] = {}
    for registration in PUBLICATION_PAPER_REGISTRATIONS:
        paper_id = str(registration.get("paper_id") or "")
        category = str(registration.get("category") or "")
        if not paper_id or paper_id in identities:
            raise ValueError(f"duplicate or empty publication paper id:{paper_id}")
        if category not in PUBLICATION_CATEGORY_LABELS:
            raise ValueError(f"unknown publication category:{paper_id}:{category}")
        counters[category] += 1
        ordinal = counters[category]
        code = f"{category}{ordinal}"
        category_label = dict(PUBLICATION_CATEGORY_LABELS[category])
        idea = bi(registration.get("idea") or {})
        method = str(registration.get("method") or "").strip()
        pdf_slug = str(registration.get("pdf_slug") or method or paper_id).strip()
        identities[paper_id] = {
            "code": code,
            "category": category,
            "ordinal": ordinal,
            "category_zh": category_label["zh"],
            "category_en": category_label["en"],
            "method": method,
            "idea": idea,
            "label_zh": f"{code} {category_label['zh']} · {method} · {idea['zh']}",
            "label_en": f"{code} {category_label['en']} · {method} · {idea['en']}",
            "pdf": f"downloads/{code}-{pdf_slug}.pdf",
        }
    return identities

PF_CANONICAL = {
    "PF-1": ("A-8", "固定进化器下的未来可学习性审计", "Future-Learnability Audit under a Frozen Evolver"),
    "PF-4": ("A-9", "更新后的诊断通道保持", "Post-Update Diagnostic-Channel Preservation"),
    "PF-5": ("A-10", "更新差异驱动的验证", "Update-Difference-Guided Verification"),
    "PF-6": ("A-11", "自进化后的失败风险迁移", "Failure-Risk Transport under Self-Evolution"),
    "PF-7": ("A-12", "更新影响范围的证据重验证", "Update-Impact-Aware Evidence Revalidation"),
    "PF-3": ("B-11", "决策保持的经验压缩生命周期", "Decision-Preserving Experience Compression Lifecycle"),
    "PF-8": ("C-7", "自写验证器漂移", "Self-Authored Verifier Drift"),
    "PF-2": ("E-5", "持久更新的修复表面可辨识性", "Repair-Surface Identifiability under Persistent Updates"),
    "PF-9": ("E-6", "更新后的决策上下文有效性", "Post-Update Decision-Context Validity"),
}

SAFETY_CANONICAL = {
    "ACTIVE": ("G-1", "历史条件下的未来首次违规风险", "History-Conditioned Future First-Violation Risk"),
    "AUTO-1-RELEVANT-SKILL-MISEXECUTION": ("G-2", "技能—任务兼容性下的执行伤害", "Execution Harm under Skill–Task Compatibility"),
    "P03-AUTOSKILL-CONTEXT-UPTAKE": ("G-3", "上下文条件化技能采用与新会话伤害", "Context-Conditioned Skill Uptake and Fresh-Session Harm"),
    "AGENT-SAFETY-DUAL-LOOP-RHO-CRITICAL": ("G-4", "双自进化回路的可写支持交互", "Writable-Support Interaction between Self-Evolution Loops"),
    "PORT-010": ("G-5", "技能提取后的检测器稳健性", "Detector Robustness after Skill Extraction"),
}
MERGED_SHADOW_CLOSURES = {
    "AUTO-1-RELEVANT-SKILL-MISEXECUTION": "G-2",
    "P03-AUTOSKILL-CONTEXT-UPTAKE": "G-3",
    "PORT-010": "G-5",
}
CLOSED_CODE_START = {"A": 13, "B": 14, "C": 8, "D": 4, "E": 8, "F": 4, "G": 6}
HOLD_DECISION_PATTERN = re.compile(r"CURRENT_SUBSTRATE|SUPPORT_INSUFFICIENT|UPDATER_INCOMPETENT|RANKING_DEGENERATE", re.I)


def load_generated(name: str) -> dict[str, Any]:
    return json.loads((GENERATED / name).read_text(encoding="utf-8"))


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def bi(value: Any, fallback: str = "") -> dict[str, str]:
    if isinstance(value, dict):
        return {"zh": str(value.get("zh") or value.get("en") or fallback or ""), "en": str(value.get("en") or value.get("zh") or fallback or "")}
    text = str(value or fallback or "")
    return {"zh": text, "en": text}


def group_from_code(code: str) -> str:
    return str(code or "").split("-", 1)[0]


def source_ref(path: str, role: str) -> dict[str, str]:
    return {"path": path, "role": role}


def authority(**kwargs: bool) -> dict[str, bool]:
    return {key: bool(kwargs.get(key, False)) for key in ("method", "experiment", "p0", "gpu")}


def _research_item_next_action(row: dict[str, Any]) -> dict[str, Any]:
    """Derive exactly one zero-authority next action from canonical ResearchItem state."""
    state = str(row.get("scientific_state") or "")
    reopen = bi(row.get("reopen_condition") or row.get("reopen_only_if") or "")
    paper = row.get("paper_transition") or {}
    paper_id = str(paper.get("paper_id") or "")
    paper_action = paper.get("primary_next_action") or {}

    if state == "PAPER_READY":
        action_class = "PAPERSTATE_HANDOFF"
        action_zh = f"科研对象已交给 {paper_id or 'PaperState'}；ResearchItem 不再自行启动实验。"
        action_en = f"The research object has handed off to {paper_id or 'PaperState'}; the ResearchItem does not launch further experiments itself."
        blocking_on = paper_id or "PAPERSTATE_HANDOFF"
    elif state == "HOLD":
        action_class = "REOPEN_CONDITION_REQUIRED"
        action_zh = "保持 HOLD；只有满足已记录的重开条件后，才重新进入科学评审。"
        action_en = "Keep the item on HOLD; return to scientific review only after the recorded reopen condition is satisfied."
        blocking_on = "REOPEN_CONDITION" if (reopen.get("zh") or reopen.get("en")) else "REOPEN_CONDITION_MISSING"
    elif state == "MERGED":
        action_class = "MERGED_NO_STANDALONE_ACTION"
        action_zh = "不再作为独立研究线推进；仅在已合并的上位方向中复用，除非满足独立重开条件。"
        action_en = "Do not advance this as a standalone line; reuse it only inside its merged parent unless the standalone reopen condition is met."
        blocking_on = "MERGED_PARENT_OR_REOPEN_CONDITION" if (reopen.get("zh") or reopen.get("en")) else "MERGED_PARENT"
    elif state == "STOPPED":
        action_class = "NO_INTERNAL_ACTION"
        action_zh = "当前没有独立内部动作；不要重跑或改写结论，只有新证据满足重开条件时才重新评审。"
        action_en = "There is no current standalone internal action; do not rerun or rewrite the decision unless new evidence satisfies the reopen condition."
        blocking_on = ""
    else:
        action_class = "INTERNAL_REVIEW_REQUIRED"
        action_zh = "当前状态无法映射到已知动作类；先进行人工状态核对，不得自动执行。"
        action_en = "The current state does not map to a known action class; require human state review and do not auto-execute."
        blocking_on = state or "UNKNOWN_RESEARCH_STATE"

    return {
        "action_class": action_class,
        "action": action_en,
        "action_zh": action_zh,
        "blocking_on": blocking_on,
        "reopen_condition_present": bool(reopen.get("zh") or reopen.get("en")),
        "paper_id": paper_id,
        "paper_next_action_class": str(paper_action.get("action_class") or ""),
        "machine_actionable": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def decision_state(decision: str, merged: bool = False) -> str:
    if merged:
        return "MERGED"
    if HOLD_DECISION_PATTERN.search(decision or ""):
        return "HOLD"
    if str(decision or "").startswith("STOP_") or "BLOCK" in str(decision or "") or "TERMINATED" in str(decision or ""):
        return "STOPPED"
    return "ARCHIVED"


def closed_category(row: dict[str, Any]) -> str:
    text = " ".join(str(row.get(k) or "") for k in ("candidate_id", "title", "reason", "strongest_reduction")).lower()
    if re.search(r"safety|unsafe|harm|attack|defen[cs]e|guard|security|risk governance|sp-09", text): return "G"
    if re.search(r"world model|embodied|spatial|navigation|geometry|physical|vla|robot", text): return "F"
    if re.search(r"workflow|program|api|tool|harness|protocol|repair|operator|compiler|execution|permission|routing", text): return "E"
    if re.search(r"evaluator|evaluation|reward|rubric|judge|self-test|self test|validation|verifier", text): return "C"
    if re.search(r"curriculum|task generat|frontier|challenge|self-play|self play", text): return "D"
    if re.search(r"memory|skill|retrieval|experience|evidence|note|consolidat|compression|context|knowledge", text): return "B"
    return "A"

def build_parent_items(terminal_state, low_resource, final_ideas, batch, admissions):
    rich_by_id = {r.get("id"): r for r in low_resource.get("passed_ideas", [])}
    refined_by_id = {r.get("idea_id"): r for r in final_ideas.get("ideas", [])}
    batch_by_id = {r.get("idea_id"): r for r in batch.get("parent_batch", [])}
    admission_by_id = {r.get("idea_id"): r for r in admissions.get("cards", [])}
    out = []
    for internal_id, terminal in terminal_state.get("parents", {}).items():
        code = terminal.get("code"); group = terminal.get("group") or group_from_code(code)
        rich = rich_by_id.get(internal_id, {}); refined = refined_by_id.get(internal_id, {})
        batch_row = batch_by_id.get(internal_id, {}); admission = admission_by_id.get(internal_id, {})
        decision = str(batch_row.get("decision") or terminal.get("p0_decision") or "")
        historical = str(terminal.get("terminal_state") or "")
        state = decision_state(decision, historical == "merge")
        gpu0 = (admission.get("execution_preflight") or {}).get("gpu0") or {}
        stop_reason = terminal.get("current_fact") or terminal.get("terminal_reason") or batch_row.get("disposition") or ""
        reopen = terminal.get("reopen_condition") or gpu0.get("next") or "Only new matched primary evidence that overturns the current conclusion may reopen this direction."
        out.append({
            "id": internal_id, "code": code, "category": group, "entity_type": "ResearchItem", "source_kind": "parent",
            "title": bi(refined.get("title") or rich.get("title") or terminal.get("final_parent_mechanism") or internal_id),
            "problem": bi(refined.get("purpose") or rich.get("purpose") or ""),
            "hypothesis": bi(rich.get("hypothesis") or refined.get("surviving_claim") or ""),
            "mechanism": bi(refined.get("core_idea") or rich.get("core_idea") or terminal.get("final_parent_mechanism") or ""),
            "method_logic": bi(refined.get("method_logic") or rich.get("method_logic") or ""),
            "novelty_boundary": bi(refined.get("collision_boundary") or rich.get("collision_boundary") or ""),
            "strongest_baseline": bi(terminal.get("strongest_baseline") or refined.get("strongest_baseline") or rich.get("strongest_baseline") or ""),
            "minimum_falsifier": bi(terminal.get("minimum_p0") or refined.get("decisive_pilot") or rich.get("pilot") or ""),
            "lifecycle_state": historical.upper().replace("-", "_") if historical else "RECORDED",
            "scientific_state": state,
            "portfolio_disposition": "CURRENT_ATTENTION" if state == "HOLD" else ("MERGED_ASSET" if state == "MERGED" else "CONCLUDED"),
            "decision_code": decision, "decision_reason": bi(stop_reason),
            "evidence_state": "SUPPORT_LIMITED" if state == "HOLD" else ("MERGED" if state == "MERGED" else "TERMINAL_EVIDENCE_RECORDED"),
            "execution_authority": authority(), "experiment_refs": [f"EXP-{code}-P0"] if admission else [],
            "failure_layer": None, "principle_dead_end_certified": False, "reopen_condition": bi(reopen),
            "absorbed_children": list(terminal.get("absorbed_children") or []), "paper_transition": None,
            "provenance_refs": [source_ref("generated/human-terminal-idea-state.json", "lifecycle_authority"), source_ref("generated/p0-revived-batch-f0.json", "latest_parent_decision"), source_ref("generated/p0-admission-state.json", "experiment_contract")],
        })
    return out


def build_independent_items(terminal_state, final_ideas, admissions):
    refined_by_id = {r.get("idea_id"): r for r in final_ideas.get("ideas", [])}
    admission_by_id = {r.get("idea_id"): r for r in admissions.get("cards", [])}
    out = []
    for internal_id, terminal in terminal_state.get("independent_methods", {}).items():
        code = terminal.get("code"); group = terminal.get("group") or group_from_code(code)
        refined = refined_by_id.get(internal_id, {}); admission = admission_by_id.get(internal_id, {})
        gpu0 = (admission.get("execution_preflight") or {}).get("gpu0") or {}
        decision = str(terminal.get("p0_decision") or "")
        if not decision and gpu0.get("status"): decision = str(gpu0.get("status")).upper().replace("-", "_")
        state = decision_state(decision)
        if state == "ARCHIVED" and str(gpu0.get("status") or "").startswith("stop"): state = "STOPPED"
        out.append({
            "id": internal_id, "code": code, "category": group, "entity_type": "ResearchItem", "source_kind": "independent_method",
            "title": bi(terminal.get("title") or refined.get("title") or internal_id), "problem": bi(refined.get("purpose") or ""),
            "hypothesis": bi(refined.get("surviving_claim") or ""), "mechanism": bi(refined.get("core_idea") or terminal.get("title") or ""),
            "method_logic": bi(refined.get("method_logic") or ""), "novelty_boundary": bi(refined.get("collision_boundary") or ""),
            "strongest_baseline": bi(refined.get("strongest_baseline") or ""), "minimum_falsifier": bi(refined.get("decisive_pilot") or ""),
            "lifecycle_state": str(terminal.get("terminal_state") or "p0").upper().replace("-", "_"), "scientific_state": state,
            "portfolio_disposition": "RETAINED_ASSET", "decision_code": decision,
            "decision_reason": bi(terminal.get("current_fact") or gpu0.get("evidence") or ""), "evidence_state": "TERMINAL_EVIDENCE_RECORDED",
            "execution_authority": authority(), "experiment_refs": [f"EXP-{code}-P0"] if admission else [], "failure_layer": None,
            "principle_dead_end_certified": False, "reopen_condition": bi(gpu0.get("next") or "Only a new irreducible result beyond the matched baseline may reopen this standalone method."),
            "absorbed_children": [], "paper_transition": None,
            "provenance_refs": [source_ref("generated/human-terminal-idea-state.json", "method_lifecycle"), source_ref("generated/p0-admission-state.json", "experiment_contract")],
        })
    return out


def pf_latest_decisions():
    design = load_generated("paper-first-design-adjudication.json")
    pf1 = load_generated("paper-first-pf1-problem-adjudication.json")
    pf2 = load_generated("paper-first-pf2-method-adjudication.json")
    pf357 = load_generated("paper-first-pf357-problem-adjudication.json")
    latest = {str(r.get("id")): {"decision": r.get("verdict"), "reason": r.get("paper_problem") or r.get("next_action"), "next_action": r.get("next_action"), "source": "generated/paper-first-design-adjudication.json"} for r in design.get("rows", [])}
    latest["PF-1"] = {"decision": pf1.get("decision"), "reason": pf1.get("reason"), "next_action": pf1.get("next_action"), "source": "generated/paper-first-pf1-problem-adjudication.json"}
    latest["PF-2"] = {"decision": pf2.get("decision"), "reason": pf2.get("reason"), "next_action": pf2.get("next_action"), "source": "generated/paper-first-pf2-method-adjudication.json"}
    for r in pf357.get("rows", []):
        latest[str(r.get("id"))] = {"decision": r.get("decision"), "reason": r.get("why_stop"), "next_action": r.get("surviving_system_role"), "source": "generated/paper-first-pf357-problem-adjudication.json"}
    return latest


def build_pf_items(incubation):
    latest = pf_latest_decisions(); out = []
    for row in incubation.get("candidates", []):
        pf_id = str(row.get("id")); code, zh, en = PF_CANONICAL[pf_id]; current = latest.get(pf_id, {})
        decision = str(current.get("decision") or row.get("verdict") or "")
        merged = decision == "MERGE_AS_CROSS_CUTTING_INVARIANT" or bool(re.match(r"STOP_PF(?:3|5|7)_STANDALONE_MERGE_", decision))
        state = decision_state(decision, merged)
        out.append({
            "id": pf_id, "code": code, "category": group_from_code(code), "entity_type": "ResearchItem", "source_kind": "paper_first",
            "title": {"zh": zh, "en": en}, "problem": bi(row.get("paper_problem") or row.get("title") or ""), "hypothesis": bi(row.get("principle") or ""),
            "mechanism": bi(row.get("method") or ""), "method_logic": bi(row.get("method") or ""),
            "novelty_boundary": bi(row.get("novelty_boundary") or row.get("collision_risk") or ""), "strongest_baseline": bi(row.get("strongest_baseline") or ""),
            "minimum_falsifier": bi(row.get("local_falsifier") or ""), "lifecycle_state": "PAPER_DESIGN_HISTORY" if row.get("verdict") == "ADVANCE_TO_PAPER_DESIGN" else "PROBLEM_REVIEW_HISTORY",
            "scientific_state": state, "portfolio_disposition": "MERGED_ASSET" if state == "MERGED" else "CONCLUDED", "decision_code": decision,
            "decision_reason": bi(current.get("reason") or row.get("collision_risk") or ""), "evidence_state": "DESIGN_LEVEL_TERMINAL",
            "execution_authority": authority(p0=bool(row.get("p0_authorized")), gpu=bool(row.get("gpu_authorized"))), "experiment_refs": [],
            "failure_layer": "problem_novelty" if "BLOCK" in decision or pf_id in {"PF-1", "PF-8", "PF-9"} else None,
            "principle_dead_end_certified": False, "reopen_condition": bi(current.get("next_action") or "Reopen only with a new irreducible decision object beyond the matched baseline."),
            "absorbed_children": [], "paper_transition": None,
            "provenance_refs": [source_ref("generated/paper-first-idea-incubation.json", "initial_problem_record"), source_ref(current.get("source") or "generated/paper-first-idea-incubation.json", "latest_scientific_decision")],
        })
    return out

def build_safety_items(safety, current_status):
    code, zh, en = SAFETY_CANONICAL["ACTIVE"]
    support = safety.get("support_realization_adjudication") or {}; qualification = safety.get("qualification") or {}; auth = safety.get("authority") or {}
    active = {
        "id": safety.get("program_id") or "AGENT-SAFETY-R9", "code": code, "category": "G", "entity_type": "ResearchItem", "source_kind": "safety",
        "title": {"zh": zh, "en": en}, "problem": bi(safety.get("scientific_question") or ""), "hypothesis": bi(safety.get("exact_prediction") or ""),
        "mechanism": bi("History-conditioned first-violation hazard after persistent state evolution"), "method_logic": bi(safety.get("cheapest_falsifier") or ""),
        "novelty_boundary": bi("History must explain future first-violation risk beyond matched current-state safety statistics."),
        "strongest_baseline": bi(safety.get("strongest_same_information_baseline") or ""), "minimum_falsifier": bi(safety.get("cheapest_falsifier") or ""),
        "lifecycle_state": str(safety.get("current_stage") or "SUPPORT_STOP"), "scientific_state": "HOLD", "portfolio_disposition": "CURRENT_ATTENTION",
        "decision_code": str(support.get("status") or qualification.get("status") or "SUPPORT_STOP"),
        "decision_reason": bi(support.get("interpretation") or qualification.get("interpretation") or (safety.get("next_gate") or {}).get("reason") or ""),
        "evidence_state": "SUPPORT_LIMITED", "execution_authority": authority(method=auth.get("method"), experiment=auth.get("heldout_future_probe_execution"), p0=auth.get("p0"), gpu=auth.get("gpu")),
        "experiment_refs": [], "failure_layer": support.get("failure_layer") or "support",
        "principle_dead_end_certified": bool(support.get("principle_dead_end_certified") or qualification.get("principle_dead_end_certified")),
        "reopen_condition": bi("Use a fresh preregistered backbone/runtime and obtain enough frozen currently-safe states before touching held-out future probes."),
        "absorbed_children": [], "paper_transition": None, "provenance_refs": [source_ref("generated/agent-safety-program-state.json", "safety_program_authority")],
    }
    shadow_closed = {r.get("candidate_id"): r for r in current_status.get("shadow_search", {}).get("closed_rows", []) if r.get("candidate_id") in MERGED_SHADOW_CLOSURES}
    out = [active]
    for closed in safety.get("closed_basins", []):
        cid = str(closed.get("candidate_id") or ""); code, zh, en = SAFETY_CANONICAL[cid]
        refs = [source_ref("generated/agent-safety-program-state.json", "typed_safety_closure")]
        if cid in shadow_closed: refs.append(source_ref("generated/current-research-status.json", "merged_shadow_closure"))
        out.append({
            "id": cid, "code": code, "category": "G", "entity_type": "ResearchItem", "source_kind": "safety", "title": {"zh": zh, "en": en},
            "problem": bi(closed.get("title") or cid), "hypothesis": bi(closed.get("title") or ""), "mechanism": bi(closed.get("title") or ""), "method_logic": bi(""),
            "novelty_boundary": bi(closed.get("reason") or ""), "strongest_baseline": bi(""), "minimum_falsifier": bi(""), "lifecycle_state": "CLOSED",
            "scientific_state": "STOPPED", "portfolio_disposition": "CONCLUDED", "decision_code": str(closed.get("stop_class") or closed.get("memory_class") or "CLOSED"),
            "decision_reason": bi(closed.get("reason") or ""), "evidence_state": "TYPED_CLOSURE", "execution_authority": authority(), "experiment_refs": [],
            "failure_layer": closed.get("failure_layer"), "principle_dead_end_certified": bool(closed.get("dead_end_certified")),
            "reopen_condition": bi(closed.get("reopen_only_if") or ""), "absorbed_children": [], "paper_transition": None, "provenance_refs": refs,
        })
    return out


def _shadow_closed_rows(current_status: dict[str, Any], search_design: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Merge the public closure ledger with newer append-only Shadow Search Memory.

    ``current-research-status.json`` is intentionally a compact public projection and can
    lag a newly persisted search closure.  The search-memory ledger is append-only and is
    therefore allowed to contribute only *missing* candidate ids here; it never rewrites
    an already projected closure.  This keeps existing A–G codes stable while ensuring a
    newly certified closure cannot disappear from ResearchItemState before the next full
    current-status rebuild.
    """
    rows = [dict(row) for row in current_status.get("shadow_search", {}).get("closed_rows", [])]
    def closure_key(row: dict[str, Any]) -> tuple[str, str, str]:
        return (
            str(row.get("candidate_id") or row.get("source_candidate_id") or ""),
            str(row.get("reason") or ""),
            str(row.get("strongest_reduction") or ""),
        )
    by_key = {closure_key(row): row for row in rows}
    memory = (search_design or {}).get("shadow_search_memory", {})
    for obj in memory.get("closed_objects", []):
        cid = str(obj.get("source_candidate_id") or obj.get("candidate_id") or "")
        if not cid:
            continue
        normalized = {
            "candidate_id": cid,
            "reason": obj.get("reason"),
            "strongest_reduction": obj.get("strongest_reduction"),
        }
        key = closure_key(normalized)
        if key in by_key:
            continue
        avoid = list(obj.get("avoid") or [])
        title = ""
        if avoid:
            title = re.sub(r"^paraphrase-only variants of:\s*", "", str(avoid[0]), flags=re.I).strip()
        normalized.update({
            "title": title or cid,
            "reopen_only_if": obj.get("reopen_only_if"),
            "failure_layer": obj.get("failure_layer"),
            "closure_layer": obj.get("closure_layer"),
            "memory_class": obj.get("memory_class"),
            "source_stop_class": obj.get("source_stop_class"),
            "principle_update_allowed": obj.get("principle_update_allowed"),
            "broader_core_principle_falsified": obj.get("broader_core_principle_falsified"),
            "experiment_run_for_this_readjudication": obj.get("experiment_run_for_this_readjudication"),
            "experiment_alone_authorizes_closure": obj.get("experiment_alone_authorizes_closure"),
            "_closure_projection_source": "generated/paper-first-search-portfolio-design-adjudication.json",
        })
        rows.append(normalized)
        by_key[key] = normalized
    return rows


def build_shadow_closed_items(current_status, search_design=None):
    # Preserve already-published A–G codes even if append-only search memory is
    # rebuilt in a different row order.  New closures take the next unused code
    # in their category; existing closures never renumber.
    existing_by_reason: dict[tuple[str, str], str] = {}
    existing_by_title: dict[tuple[str, str], str] = {}
    used_codes: set[str] = set()
    try:
        existing = load_generated("research-items.json")
        for item in existing.get("research_items", []):
            if item.get("source_kind") != "shadow_closed":
                continue
            code = str(item.get("code") or "")
            cid = str(item.get("id") or "")
            title = str((item.get("title") or {}).get("en") or (item.get("title") or {}).get("zh") or "")
            reason = str((item.get("decision_reason") or {}).get("en") or (item.get("decision_reason") or {}).get("zh") or "")
            if code:
                used_codes.add(code)
                existing_by_title[(cid, title)] = code
                existing_by_reason[(cid, reason)] = code
    except Exception:
        pass
    counters = dict(CLOSED_CODE_START)
    for code in used_codes:
        match = re.fullmatch(r"([A-G])-(\d+)", code)
        if match:
            group, number = match.group(1), int(match.group(2))
            counters[group] = max(counters[group], number + 1)
    out = []
    for row in _shadow_closed_rows(current_status, search_design):
        cid = str(row.get("candidate_id") or "")
        if cid in MERGED_SHADOW_CLOSURES: continue
        group = closed_category(row)
        title = str(row.get("title") or cid)
        reason = str(row.get("reason") or row.get("strongest_reduction") or "")
        code = existing_by_reason.get((cid, reason)) or existing_by_title.get((cid, title))
        if not code or group_from_code(code) != group:
            while f"{group}-{counters[group]}" in used_codes:
                counters[group] += 1
            code = f"{group}-{counters[group]}"
            counters[group] += 1
        used_codes.add(code)
        closure_layer = row.get("closure_layer")
        failure_layer = None if closure_layer == "problem_novelty" else (row.get("failure_layer") or closure_layer)
        projection_source = row.get("_closure_projection_source") or "generated/current-research-status.json"
        projection_role = "append_only_shadow_search_memory_closure" if row.get("_closure_projection_source") else "typed_shadow_closure"
        out.append({
            "id": cid, "code": code, "category": group, "entity_type": "ResearchItem", "source_kind": "shadow_closed",
            "title": {"zh": str(row.get("title") or cid), "en": str(row.get("title") or cid)}, "problem": bi(row.get("title") or cid),
            "hypothesis": bi(row.get("title") or ""), "mechanism": bi(row.get("title") or ""), "method_logic": bi(""),
            "novelty_boundary": bi(row.get("strongest_reduction") or row.get("reason") or ""), "strongest_baseline": bi(row.get("strongest_reduction") or ""), "minimum_falsifier": bi(""),
            "lifecycle_state": "CLOSED", **({"paper_first_lifecycle": row.get("paper_first_lifecycle")} if row.get("paper_first_lifecycle") else {}), "scientific_state": "STOPPED", "portfolio_disposition": "CONCLUDED",
            "decision_code": str(row.get("source_stop_class") or row.get("memory_class") or "CLOSED"), "decision_reason": bi(row.get("reason") or row.get("strongest_reduction") or ""),
            "evidence_state": "TYPED_CLOSURE", "execution_authority": authority(), "experiment_refs": [], "closure_layer": closure_layer, "failure_layer": failure_layer,
            "principle_dead_end_certified": bool(row.get("principle_update_allowed") and failure_layer == "core_principle"),
            "reopen_condition": bi(row.get("reopen_only_if") or ""), "absorbed_children": [], "paper_transition": None,
            "provenance_refs": [source_ref(projection_source, projection_role)],
            "closure_metadata": {**{k: row.get(k) for k in ("experiment_run_for_this_readjudication", "experiment_alone_authorizes_closure", "broader_core_principle_falsified", "memory_class")}, **({"paper_first_lifecycle": row.get("paper_first_lifecycle")} if row.get("paper_first_lifecycle") else {}), "closure_layer": closure_layer},
        })
    return out


def build_stri_research_item(current_status):
    paper = current_status.get("leading_paper_track") or {}; claims = paper.get("claims") or {}
    return {
        "id": paper.get("candidate_id") or "skill-taxonomy-representation-invariance", "code": "E-7", "category": "E", "entity_type": "ResearchItem", "source_kind": "paper_source",
        "title": bi(paper.get("title") or "STRI: Self-Evolution Should Not Depend on How Skills Are Split"),
        "problem": {"zh": "Agent 自进化的结论不应依赖技能库被人为拆成多少条技能；技能表示变化若改变检索与执行行为，就是需要控制的结构变量。", "en": "Self-evolution conclusions should not depend on an arbitrary partition of the skill library; representation changes that alter retrieval and execution are a scientific variable."},
        "hypothesis": bi(" ".join(str(v) for v in claims.values() if v)),
        "mechanism": {"zh": "技能分类表示 → 检索变化 → 被挤出的技能/中介 → 执行行为变化。", "en": "Skill-taxonomy representation → retrieval change → displaced skill/mediator → executed behavior change."},
        "method_logic": {"zh": "用原始、拆分、ID placebo、quotient control 和 post-checkout add-back / cleanup control 隔离表示、检索与行为中介。", "en": "Use original, split, ID-placebo, quotient, post-checkout add-back, and cleanup controls to isolate representation, retrieval, and behavioral mediation."},
        "novelty_boundary": {"zh": "只主张冻结 STRI/P19 范围内的表示敏感性与行为传播，不扩大到一般 task utility 或任意技能系统。", "en": "Bounded to frozen STRI/P19 representation sensitivity and behavioral propagation; no general task-utility or arbitrary-skill-system claim."},
        "strongest_baseline": bi("ID placebo, quotient-preserving control, matched cleanup control, and fixed-policy endpoint checks."),
        "minimum_falsifier": bi("Frozen P19 dynamic and mediator-isolation evidence plus bounded qualification/negative controls."),
        "lifecycle_state": "PAPER_READY", "scientific_state": "PAPER_READY", "portfolio_disposition": "CURRENT_ATTENTION",
        "decision_code": str(paper.get("status") or "READY_NARROW_ICLR"),
        "decision_reason": {"zh": f"STRI 当前 {paper.get('claims_supported', 0)}/{paper.get('claims_total', 0)} 条核心主张已有对应证据，论文证据债={paper.get('paper_quality_evidence_debt', 0)}；科研对象已交接到 PaperState。", "en": f"STRI supports {paper.get('claims_supported', 0)}/{paper.get('claims_total', 0)} core claims with paper-evidence debt={paper.get('paper_quality_evidence_debt', 0)}; the ResearchItem has handed off to PaperState."},
        "evidence_state": "PAPER_EVIDENCE_COMPLETE" if int(paper.get("paper_quality_evidence_debt") or 0) == 0 else "PAPER_EVIDENCE_HOLD",
        "execution_authority": authority(), "experiment_refs": ["STRI-AUTOSKILL-P19", "STRI-P0A", "STRI-P0E"], "failure_layer": None,
        "principle_dead_end_certified": False, "reopen_condition": bi("The narrow paper needs no new experiment; reopen research only under a separately authorized claim-expanding contract."),
        "absorbed_children": [], "paper_transition": {"paper_id": "STRI", "status": paper.get("submission_status") or paper.get("status")},
        "provenance_refs": [source_ref("generated/current-research-status.json", "public_paper_evidence_projection"), source_ref("generated/asset-first-stri-iclr2027-final-state-20260816.json", "paper_source_state")],
    }

def build_p0_experiment_records(admissions, terminal_state, batch):
    parent_batch = {r.get("idea_id"): r for r in batch.get("parent_batch", [])}
    terminal_by_id = {**terminal_state.get("parents", {}), **terminal_state.get("independent_methods", {})}
    out = []
    for card in admissions.get("cards", []):
        internal_id = card.get("idea_id"); code = card.get("code"); terminal = terminal_by_id.get(internal_id, {}); batch_row = parent_batch.get(internal_id, {})
        preflight = card.get("execution_preflight") or {}; gpu0 = preflight.get("gpu0") or {}
        decision = str(batch_row.get("decision") or terminal.get("p0_decision") or "")
        if not decision and gpu0.get("status"): decision = str(gpu0.get("status")).upper().replace("-", "_")
        out.append({
            "experiment_id": f"EXP-{code}-P0", "research_item_code": code, "entity_type": "ExperimentRecord", "portfolio_context": False,
            "purpose": bi((card.get("contract") or {}).get("minimum_p0") or ""), "hypothesis_tested": bi((card.get("contract") or {}).get("mechanism") or ""),
            "protocol": card.get("contract") or {}, "setup": card.get("setup") or {}, "baseline": bi((card.get("contract") or {}).get("baseline") or ""),
            "execution": {"historical_lifecycle": card.get("lifecycle"), "admission_status": card.get("admission_status"), "execution_authorized_now": False, "preflight": preflight},
            "result": {"status": "STOPPED" if (decision.startswith("STOP_") or str(gpu0.get("status") or "").startswith("stop")) else "HISTORICAL", "decision_code": decision, "evidence": gpu0.get("evidence") or terminal.get("current_fact") or batch_row.get("disposition"), "next_action": gpu0.get("next") or batch_row.get("next_action")},
            "failure_layer": None, "scientific_authority": False, "principle_update_authority": False,
            "artifacts": [gpu0.get("source")] if gpu0.get("source") else [], "provenance_refs": [source_ref("generated/p0-admission-state.json", "frozen_p0_contract")],
        })
    return out


def build_stri_experiment_records(current_status):
    dyn = current_status.get("stri_dynamic_evidence") or {}; autoskill = dyn.get("autoskill_p19") or {}; p0a = dyn.get("p0a") or {}; p0e = dyn.get("skillrl_p0e") or {}
    return [
        {"experiment_id": "STRI-AUTOSKILL-P19", "research_item_code": "E-7", "entity_type": "ExperimentRecord", "portfolio_code": "E-7a", "portfolio_context": True,
         "title": {"zh": "AutoSkill P19 表示—检索—行为机制证据", "en": "AutoSkill P19 representation–retrieval–behavior evidence"},
         "reader_summary": {"zh": "这条实验链支持 E-7/N1 的窄范围机制：技能表示变化会通过检索与中介传播到实际执行行为；只适用于冻结的 P19 场景。", "en": "This experiment chain supports the narrow E-7/N1 mechanism: representation changes propagate through retrieval and a mediator into executed behavior on the frozen P19 setting."},
         "purpose": bi(autoskill.get("claim_boundary") or ""), "hypothesis_tested": bi("Skill-taxonomy representation changes propagate through retrieval and a mediator into executed behavior on the frozen P19 substrate."),
         "protocol": {"fresh_container_per_run": autoskill.get("fresh_container_per_run"), "judge_calls": autoskill.get("judge_calls")}, "baseline": bi("split4, ID placebo, quotient control, and matched cleanup control"),
         "execution": {"status": autoskill.get("status"), "groups": autoskill.get("groups"), "mediator_isolation": autoskill.get("mediator_isolation")},
         "result": {"status": autoskill.get("status"), "fisher_exact_p": autoskill.get("fisher_exact_p"), "role": autoskill.get("role")},
         "failure_layer": None, "scientific_authority": False, "paper_evidence_role": "SUPPORTS_N1_BOUNDED", "principle_update_authority": False, "artifacts": [],
         "provenance_refs": [source_ref("generated/current-research-status.json", "stri_dynamic_evidence.autoskill_p19")]},
        {"experiment_id": "STRI-P0A", "research_item_code": "E-7", "entity_type": "ExperimentRecord", "portfolio_code": "E-7b", "portfolio_context": True,
         "title": {"zh": "STRI 提案器资格检查", "en": "STRI proposer qualification check"}, "reader_summary": {"zh": "提案器资格检查没有通过，所以这条可选实验分支不继续；这只是资格/支持失败，不支持也不反驳 STRI 的 N1–N3。", "en": "The proposer qualification check failed, so this optional branch does not continue; this is a qualification/support failure and neither supports nor refutes STRI N1–N3."}, "purpose": bi("Check whether the optional proposer route is competent enough to justify additional dynamic experiments."),
         "hypothesis_tested": bi("The proposer can generate sufficiently qualified candidates for the intended comparison."), "protocol": {}, "baseline": bi("Frozen proposer-qualification gate"),
         "execution": {"status": p0a.get("status")}, "result": {"status": p0a.get("status"), "role": p0a.get("role"), "next_action": p0a.get("next_action")},
         "failure_layer": "support", "scientific_authority": False, "paper_evidence_role": "QUALIFICATION_FAILURE_ASSET_ONLY", "principle_update_authority": False, "artifacts": [],
         "provenance_refs": [source_ref("generated/current-research-status.json", "stri_dynamic_evidence.p0a")]},
        {"experiment_id": "STRI-P0E", "research_item_code": "E-7", "entity_type": "ExperimentRecord", "portfolio_code": "E-7c", "portfolio_context": True,
         "title": {"zh": "STRI 最终策略差异验证", "en": "STRI endpoint policy-difference validation"}, "reader_summary": {"zh": "这条额外路线已经停止继续扩实验：合格固定策略下没有观察到终点差异；它只作为可选方法实现的负边界证据，不改变 STRI 的 N1–N3。", "en": "This optional route stops without further experiments: the qualified fixed-policy comparison showed no endpoint difference. It is negative boundary evidence for one optional realization and does not change STRI N1–N3."}, "purpose": bi("Test whether the fuller fixed policy changes the endpoint under a qualified optional realization."),
         "hypothesis_tested": bi("The displacement treatment changes endpoint behavior relative to fixed-policy controls."), "protocol": {"calibration": p0e.get("calibration")},
         "baseline": bi("Pristine, identity-placebo, and exact-quotient fixed-policy controls"), "execution": {"status": p0e.get("status"), "stage2_locked": p0e.get("stage2_locked"), "new_gpu_authorized": p0e.get("new_gpu_authorized")},
         "result": {"status": p0e.get("status"), "endpoint_result": p0e.get("endpoint_result"), "role": p0e.get("role")},
         "failure_layer": "method_realization", "scientific_authority": False, "paper_evidence_role": "OPTIONAL_METHOD_NEGATIVE_BOUNDARY", "principle_update_authority": False, "artifacts": [],
         "provenance_refs": [source_ref("generated/current-research-status.json", "stri_dynamic_evidence.skillrl_p0e")]},
    ]


def build_evidence_contexts(current_status):
    residual = current_status.get("positive_residual") or {}; sp15 = current_status.get("shadow_search", {}).get("sp15_support") or {}
    return [
        {"context_id": "MEM-HISTORY", "code": "B-12", "category": "B", "entity_type": "EvidenceContext", "portfolio_context": True,
         "title": {"zh": "持久记忆的上下文依赖效应（归档现象）", "en": "Context-dependent effect of persistent memory (archived phenomenon)"}, "status": residual.get("parent_phenomenon_status"),
         "decision": residual.get("parent_phenomenon"), "authority": {"problem_gate": False, "method": False, "p0": False, "gpu": False}, "reopen_condition": residual.get("next_search_basin"),
         "provenance_refs": [source_ref("generated/current-research-status.json", "positive_residual")]},
        {"context_id": "SP-15", "code": "B-13", "category": "B", "entity_type": "EvidenceContext", "portfolio_context": True,
         "title": {"zh": "查询式技能检索的显式程序边界", "en": "Explicit-procedure boundary of query-only skill retrieval"}, "status": sp15.get("support_status"), "decision": sp15.get("decision"),
         "failure_layer": sp15.get("failure_layer"), "principle_dead_end_certified": bool(sp15.get("principle_dead_end_certified")),
         "authority": {"problem_gate": False, "method": bool(sp15.get("method_design_authorized")), "p0": False, "gpu": False},
         "reopen_condition": "A matched query-level identifiability unit becomes available from primary or author-released evidence.",
         "provenance_refs": [source_ref("generated/current-research-status.json", "shadow_search.sp15_support")]},
    ]


def paper_acceptance_state():
    """Return the freshest auditable Paper Acceptance projection available at build time.

    The canonical append-only ledger remains authoritative on the research host.  For
    portable/Pages builds, use the newest committed read-only projection available:
    paper-registry.json may be newer than the much larger research-system snapshot and
    must not be silently rolled back merely because /data is unavailable in CI.
    """
    system = load_generated("research-system-state.json")
    acceptance = dict(system.get("paper_acceptance") or {})
    snapshot_index = dict(acceptance.get("ledger_index") or {})
    ledger_index = snapshot_index
    projection_source = "generated/research-system-state.json"
    try:
        portable_registry = load_generated("paper-registry.json")
        portable_index = build_portable_paper_ledger_index(portable_registry)
        portable_summary = portable_index.get("summary") or {}
        registry_generated = str(portable_registry.get("generated_at") or "")
        system_generated = str(system.get("generated_at") or "")
        snapshot_summary = snapshot_index.get("summary") or {}
        portable_available = int(portable_summary.get("papers") or 0) > 0 or int(portable_summary.get("invalid_ledgers") or 0) > 0
        if portable_available and (registry_generated > system_generated or int(snapshot_summary.get("papers") or 0) == 0):
            ledger_index = portable_index
            projection_source = "generated/paper-registry.json"
    except Exception:
        pass
    try:
        root = resolve_experiment_data_root(StorageSettings.from_env())
        live_index = build_paper_ledger_index(root)
        live_summary = live_index.get("summary") or {}
        if int(live_summary.get("invalid_ledgers") or 0) > 0:
            ledger_index = live_index
            projection_source = "canonical-append-only-paper-ledgers-invalid"
        elif int(live_summary.get("papers") or 0) > 0:
            ledger_index = live_index
            projection_source = "canonical-append-only-paper-ledgers"
    except Exception:
        # Portable/static builds intentionally remain valid without /data access.
        pass
    acceptance["ledger_index"] = ledger_index
    acceptance["projection_source"] = projection_source
    summary = dict(acceptance.get("summary") or {})
    index_summary = ledger_index.get("summary") or {}
    summary.update({
        "registered_papers": int(index_summary.get("papers") or 0),
        "scientific_holds": int(index_summary.get("scientific_holds") or 0),
        "ledger_submission_ready_papers": int(index_summary.get("submission_ready") or 0),
        "submission_ready_papers": int(index_summary.get("submission_ready") or 0),
        "gate_clean_submission_ready_papers": int(index_summary.get("gate_clean_submission_ready") or 0),
        "paper_preparation_failed_papers": int(index_summary.get("paper_preparation_failed") or 0),
        "immediate_submission_holds": int(index_summary.get("immediate_submission_holds") or 0),
        "internal_action_required_papers": int(index_summary.get("internal_action_required") or 0),
        "no_internal_action_papers": int(index_summary.get("no_internal_action") or 0),
        "invalid_ledgers": int(index_summary.get("invalid_ledgers") or 0),
    })
    acceptance["summary"] = summary
    entries = ledger_index.get("entries") or []
    return acceptance, {str(row.get("paper_id") or ""): row for row in entries}


def build_research_item_state():
    terminal = load_generated("human-terminal-idea-state.json"); low = load_generated("iclr-low-resource-ideas.json"); final = load_generated("current-final-ideas.json")
    batch = load_generated("p0-revived-batch-f0.json"); admissions = load_generated("p0-admission-state.json"); incubation = load_generated("paper-first-idea-incubation.json")
    current = load_generated("current-research-status.json"); safety = load_generated("agent-safety-program-state.json")
    search_design = load_generated("paper-first-search-portfolio-design-adjudication.json")
    items = [*build_parent_items(terminal, low, final, batch, admissions), *build_independent_items(terminal, final, admissions), *build_pf_items(incubation), *build_safety_items(safety, current), *build_shadow_closed_items(current, search_design), build_stri_research_item(current)]
    _, acceptance_by_id = paper_acceptance_state()
    for row in items:
        if row.get("code") == "E-7" and acceptance_by_id.get("STRI-ICLR2027"):
            accepted = acceptance_by_id["STRI-ICLR2027"]
            row["paper_transition"] = {"paper_id": "STRI", "acceptance_paper_id": "STRI-ICLR2027", "status": accepted.get("current_state"), "scientific_status": accepted.get("scientific_status"), "primary_next_action": dict(accepted.get("primary_next_action") or {})}
        elif row.get("code") == "G-1" and acceptance_by_id.get("AGENT-SAFETY-R9"):
            accepted = acceptance_by_id["AGENT-SAFETY-R9"]
            row["paper_transition"] = {"paper_id": "AGENT-SAFETY-R9", "acceptance_paper_id": "AGENT-SAFETY-R9", "status": accepted.get("current_state"), "scientific_status": accepted.get("scientific_status"), "blocked": accepted.get("scientific_status") == "CAUSAL_HOLD", "primary_next_action": dict(accepted.get("primary_next_action") or {})}
    for row in items:
        row["primary_next_action"] = _research_item_next_action(row)
    items.sort(key=lambda r: (r["category"], int(str(r["code"]).split("-",1)[1]) if str(r["code"]).split("-",1)[1].isdigit() else 999, r["code"]))
    experiments = [*build_p0_experiment_records(admissions, terminal, batch), *build_stri_experiment_records(current)]; contexts = build_evidence_contexts(current)
    by_category = {}
    for category in CATEGORY_DEFINITIONS:
        ri = sum(r["category"] == category for r in items)
        ex = sum(bool(r.get("portfolio_context")) and group_from_code(r.get("portfolio_code") or r.get("research_item_code")) == category for r in experiments)
        ec = sum(bool(r.get("portfolio_context")) and r["category"] == category for r in contexts)
        by_category[category] = {"research_items": ri, "experiment_contexts": ex, "evidence_contexts": ec, "portfolio_total": ri+ex+ec}
    portfolio_experiments = [r for r in experiments if r.get("portfolio_context")]
    action_counts = dict(sorted(Counter((r.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for r in items).items()))
    return {
        "schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source_revision": git_head(),
        "policy": {"research_item_is_primary_scientific_entity": True, "experiment_is_evidence_event_not_parallel_current_state": True, "paper_is_research_output_entity": True, "projection_is_read_only": True, "projection_cannot_grant_scientific_authority": True, "primary_next_action_is_derived_zero_authority_projection": True, "exactly_one_primary_next_action_per_research_item": True, "zero_active_research_items_is_valid": True, "visibility_tracking_does_not_create_active_slot": True, "execution_protocol_support_and_scientific_failure_remain_distinct": True, "historical_p0_does_not_imply_current_execution_authority": True, "only_explicit_core_principle_closure_may_certify_scientific_dead_end": True},
        "categories": [{"id": k, **v} for k,v in CATEGORY_DEFINITIONS.items()],
        "summary": {"research_items": len(items), "experiment_records": len(experiments), "portfolio_experiment_contexts": len(portfolio_experiments), "evidence_contexts": len(contexts), "portfolio_objects": len(items)+len(portfolio_experiments)+len(contexts),
                    "source_kind_counts": dict(sorted(Counter(r.get("source_kind") for r in items).items())), "scientific_state_counts": dict(sorted(Counter(r.get("scientific_state") for r in items).items())), "by_category": by_category,
                    "parent_scientific_states": dict(sorted(Counter(r["scientific_state"] for r in items if r["source_kind"] == "parent").items())), "primary_next_action_counts": action_counts, "active_research_items": sum(str(r.get("scientific_state") or "") == "ACTIVE" for r in items), "machine_actionable_research_items": sum((r.get("primary_next_action") or {}).get("machine_actionable") is True for r in items), "current_formal_experiment_authority": int((current.get("headline") or {}).get("launchable_formal_experiments") or 0)},
        "research_items": items, "experiment_records": experiments, "evidence_contexts": contexts,
        "provenance": {"canonical_inputs": ["generated/human-terminal-idea-state.json", "generated/iclr-low-resource-ideas.json", "generated/current-final-ideas.json", "generated/p0-admission-state.json", "generated/p0-revived-batch-f0.json", "generated/paper-first-idea-incubation.json", "generated/current-research-status.json", "generated/paper-first-search-portfolio-design-adjudication.json#shadow_search_memory.closed_objects", "generated/agent-safety-program-state.json", "generated/research-system-state.json#paper_acceptance.ledger_index"]},
    }


def build_paper_registry(research_state=None):
    research_state = research_state or build_research_item_state()
    current = load_generated("current-research-status.json")
    legacy_stri = dict(current.get("leading_paper_track") or {})
    acceptance, acceptance_by_id = paper_acceptance_state()
    by_code = {row.get("code"): row for row in research_state.get("research_items") or []}
    stri_acceptance = dict(acceptance_by_id.get("STRI-ICLR2027") or {})
    safety_acceptance = dict(acceptance_by_id.get("AGENT-SAFETY-R9") or {})
    publication_identities = build_publication_identities()
    # Source/supplement aliases retain their canonical artifact names; only the
    # public PDF alias is derived from publication_identity. Legacy PDF names
    # remain shipped by the static builder for backwards-compatible links.
    public_downloads = {
        "STRI": {"pdf": publication_identities["STRI"]["pdf"], "source_zip": "downloads/STRI-ICLR2027-source.zip", "supplement_zip": "downloads/STRI-ICLR2027-supplement.zip"},
        "AGENT-SAFETY-R9": {"pdf": publication_identities["AGENT-SAFETY-R9"]["pdf"], "source_zip": "downloads/Agent-Safety-R9-source.zip", "supplement_zip": "downloads/Agent-Safety-R9-supplement.zip"},
        "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE": {"pdf": publication_identities["D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"]["pdf"], "source_zip": "downloads/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-source.zip", "supplement_zip": "downloads/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-supplement.zip"},
        "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK": {"pdf": publication_identities["D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"]["pdf"], "source_zip": "downloads/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-source.zip"},
        "D2-PAPER-FAILURE-MEMORY-PROVENANCE": {"pdf": publication_identities["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]["pdf"], "source_zip": "downloads/D2-PAPER-FAILURE-MEMORY-PROVENANCE-source.zip", "supplement_zip": "downloads/D2-PAPER-FAILURE-MEMORY-PROVENANCE-supplement.zip"},
    }
    stri = {
        **legacy_stri,
        **stri_acceptance,
        "paper_id": "STRI",
        "acceptance_paper_id": "STRI-ICLR2027",
        "entity_type": "PaperState",
        "source_kind": "research-item",
        "source_research_item": "E-7",
        "source_research_item_id": (by_code.get("E-7") or {}).get("id"),
        "source_research_object": "E-7",
        "source_candidates": [],
        "paper_stage": stri_acceptance.get("current_state") or "PAPER_EVIDENCE",
        "submission_status": stri_acceptance.get("current_state") or "PAPER_EVIDENCE",
        "legacy_submission_status": legacy_stri.get("submission_status"),
        "submission_ready": bool((stri_acceptance.get("latest_submission_readiness") or {}).get("submission_ready")),
        "downloads": dict(public_downloads["STRI"]),
        "publication_identity": dict(publication_identities["STRI"]),
        "experiment_refs": list((by_code.get("E-7") or {}).get("experiment_refs") or []),
        "research_authority": authority(),
        "acceptance_authority": stri_acceptance.get("authority") or {},
        "provenance_refs": [source_ref("canonical-paper-acceptance-ledger", "STRI-ICLR2027"), source_ref("generated/current-research-status.json", "legacy_paper_quality_projection"), source_ref("generated/research-items.json", "source_research_item")],
    }
    safety = {
        **safety_acceptance,
        "paper_id": "AGENT-SAFETY-R9",
        "acceptance_paper_id": "AGENT-SAFETY-R9",
        "entity_type": "PaperState",
        "source_kind": "research-item",
        "source_research_item": "G-1",
        "source_research_item_id": (by_code.get("G-1") or {}).get("id"),
        "source_research_object": "G-1",
        "source_candidates": [],
        "paper_stage": safety_acceptance.get("current_state") or "PAPER_EVIDENCE",
        "submission_status": safety_acceptance.get("current_state") or "PAPER_EVIDENCE",
        "submission_ready": bool((safety_acceptance.get("latest_submission_readiness") or {}).get("submission_ready")),
        "downloads": dict(public_downloads["AGENT-SAFETY-R9"]),
        "publication_identity": dict(publication_identities["AGENT-SAFETY-R9"]),
        "experiment_refs": list((by_code.get("G-1") or {}).get("experiment_refs") or []),
        "research_authority": authority(),
        "acceptance_authority": safety_acceptance.get("authority") or {},
        "provenance_refs": [source_ref("canonical-paper-acceptance-ledger", "AGENT-SAFETY-R9"), source_ref("generated/research-items.json", "source_research_item")],
    }

    # D2 papers were promoted from the paper-first discovery campaign rather than
    # from an A–G ResearchItem. Preserve that provenance explicitly instead of
    # inventing a false ResearchItem mapping merely to satisfy the UI schema.
    d2_meta = {
        "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE": {
            "source_research_object": "D2-PROXY-REWARD-MEMORY-VARIANCE",
            "source_candidates": ["D2-C02", "D2-C05"],
            "display_order": 30,
        },
        "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK": {
            "source_research_object": "D2-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
            "source_candidates": ["D2-C06"],
            "display_order": 31,
        },
        "D2-PAPER-FAILURE-MEMORY-PROVENANCE": {
            "source_research_object": "D2-FAILURE-MEMORY-PROVENANCE",
            "source_candidates": ["D2-C01", "D2-C04"],
            "display_order": 32,
        },
    }
    d2_papers = []
    for paper_id, meta in d2_meta.items():
        accepted = dict(acceptance_by_id.get(paper_id) or {})
        if not accepted:
            continue
        discovery_provenance = build_discovery_provenance(list(meta["source_candidates"]))
        d2_papers.append({
            **accepted,
            "paper_id": paper_id,
            "acceptance_paper_id": paper_id,
            "entity_type": "PaperState",
            "source_kind": "paper-first-discovery-candidate",
            "source_research_item": None,
            "source_research_item_id": None,
            "source_research_object": meta["source_research_object"],
            "source_candidates": list(meta["source_candidates"]),
            "discovery_provenance": discovery_provenance,
            "paper_stage": accepted.get("current_state") or "PAPER_EVIDENCE",
            "submission_status": accepted.get("current_state") or "PAPER_EVIDENCE",
            "submission_ready": bool((accepted.get("latest_submission_readiness") or {}).get("submission_ready")),
            "downloads": dict(public_downloads[paper_id]),
            "publication_identity": dict(publication_identities[paper_id]),
            "experiment_refs": [],
            "research_authority": authority(),
            "acceptance_authority": accepted.get("authority") or {},
            "display_order": meta["display_order"],
            "provenance_refs": [source_ref("canonical-paper-acceptance-ledger", paper_id), source_ref("paper-first-discovery-candidates", ",".join(meta["source_candidates"]))],
        })

    papers = [stri, safety, *sorted(d2_papers, key=lambda row: int(row.get("display_order") or 999))]
    stage_counts = dict(sorted(Counter(row.get("paper_stage") for row in papers).items()))
    return {
        "schema_version": "1.5",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_revision": git_head(),
        "projection_source": acceptance.get("projection_source") or "generated/research-system-state.json",
        "policy": {
            "paper_registry_is_projection_of_append_only_acceptance_ledgers": True,
            "paper_registry_cannot_grant_research_or_experiment_authority": True,
            "paper_registry_cannot_grant_submission_authority": True,
            "paper_claims_must_reference_existing_research_evidence": True,
            "submission_ready_is_historical_ledger_readiness": True,
            "gate_clean_submission_ready_is_latest_effective_internal_readiness": True,
            "primary_next_action_is_internal_only": True,
            "paper_first_discovery_papers_need_not_fake_research_item_parentage": True,
            "paper_downloads_are_zero_authority_public_artifact_links": True,
            "publication_identity_is_reader_facing_only": True,
            "publication_codes_are_category_local_append_order": True,
            "publication_identity_does_not_replace_internal_provenance": True,
            "historical_discovery_ids_are_preserved_for_exact_provenance": True,
            "reader_facing_discovery_aliases_do_not_reuse_ag_category_letters": True,
            "reader_facing_discovery_aliases_do_not_reuse_pf_idea_ids": True,
            "historical_discovery_ids_are_hidden_by_default_in_reader_views": True,
            **(acceptance.get("policy") or {}),
        },
        "summary": {
            "papers": len(papers),
            "submission_ready": sum(bool(row.get("submission_ready")) for row in papers),
            "gate_clean_submission_ready": sum(row.get("gate_clean_submission_ready") is True for row in papers),
            "paper_preparation_failed": sum((row.get("latest_paper_preparation") or {}).get("required_gates", 0) > 0 and (row.get("latest_paper_preparation") or {}).get("pass") is not True for row in papers),
            "immediate_submission_holds": sum(row.get("immediate_submission_hold") is True for row in papers),
            "internal_action_required": sum((row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in papers),
            "no_internal_action": sum((row.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION" for row in papers),
            "by_internal_action": dict(sorted(Counter((row.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for row in papers).items())),
            "scientific_holds": sum(str(row.get("scientific_status") or "") != "READY" for row in papers),
            "primary_paper": "STRI",
            "publication_codes": [row["publication_identity"]["code"] for row in papers],
            "by_publication_category": dict(sorted(Counter(row["publication_identity"]["category"] for row in papers).items())),
            "discovery_aliases": [alias for row in papers for alias in (row.get("discovery_provenance") or {}).get("candidate_aliases", [])],
            "by_stage": stage_counts,
        },
        "papers": papers,
    }

def validate_research_item_state(state):
    errors = []; items = state.get("research_items") or []; experiments = state.get("experiment_records") or []; contexts = state.get("evidence_contexts") or []; summary = state.get("summary") or {}
    codes = [r.get("code") for r in items]
    current = load_generated("current-research-status.json")
    search_design = load_generated("paper-first-search-portfolio-design-adjudication.json")
    source_shadow_rows = [row for row in _shadow_closed_rows(current, search_design) if str(row.get("candidate_id") or "") not in MERGED_SHADOW_CLOSURES]
    expected_shadow_ids = Counter(str(row.get("candidate_id") or "") for row in source_shadow_rows)
    actual_shadow_ids = Counter(str(row.get("id") or "") for row in items if row.get("source_kind") == "shadow_closed")
    if actual_shadow_ids != expected_shadow_ids:
        errors.append(f"shadow closure projection drifted: expected={dict(expected_shadow_ids)}, actual={dict(actual_shadow_ids)}")
    expected_items = 48 + len(source_shadow_rows)
    if len(items) != expected_items: errors.append(f"expected {expected_items} ResearchItems, got {len(items)}")
    if len(set(codes)) != len(codes): errors.append("ResearchItem codes are not unique")
    if len(experiments) != 30: errors.append(f"expected 30 ExperimentRecords, got {len(experiments)}")
    if len(contexts) != 2: errors.append(f"expected 2 EvidenceContexts, got {len(contexts)}")
    expected_portfolio_objects = expected_items + 3 + 2
    if int(summary.get("portfolio_objects") or 0) != expected_portfolio_objects: errors.append(f"expected {expected_portfolio_objects} portfolio objects, got {summary.get('portfolio_objects')}")
    base_category_totals = {"A":12,"B":13,"C":7,"D":3,"E":10,"F":3,"G":5}
    closure_category_counts = Counter(closed_category(row) for row in source_shadow_rows)
    expected = {key: base_category_totals[key] + int(closure_category_counts.get(key, 0)) for key in base_category_totals}
    actual = {k:int((summary.get("by_category",{}).get(k) or {}).get("portfolio_total") or 0) for k in expected}
    if actual != expected: errors.append(f"category totals drifted: expected={expected}, actual={actual}")
    if summary.get("parent_scientific_states") != {"HOLD":4,"MERGED":6,"STOPPED":16}: errors.append(f"parent state split drifted: {summary.get('parent_scientific_states')}")
    expected_actions = {"PAPER_READY":"PAPERSTATE_HANDOFF","HOLD":"REOPEN_CONDITION_REQUIRED","MERGED":"MERGED_NO_STANDALONE_ACTION","STOPPED":"NO_INTERNAL_ACTION"}
    action_counts = Counter((r.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for r in items)
    if dict(sorted(action_counts.items())) != dict(summary.get("primary_next_action_counts") or {}): errors.append("ResearchItem primary-next-action summary drifted from item-level projections")
    actual_active = sum(str(row.get("scientific_state") or "") == "ACTIVE" for row in items)
    if int(summary.get("active_research_items") or 0) != actual_active: errors.append(f"ResearchItem active count drifted: summary={summary.get('active_research_items')} actual={actual_active}")
    if state.get("policy", {}).get("zero_active_research_items_is_valid") is not True or state.get("policy", {}).get("visibility_tracking_does_not_create_active_slot") is not True: errors.append("ResearchItem policy must explicitly allow zero active rows and separate visibility tracking from activity")
    if int(summary.get("machine_actionable_research_items") or 0) != 0: errors.append("ResearchItem next-action projection cannot expose machine-actionable research work")
    for row in items:
        action = row.get("primary_next_action") or {}; expected_action = expected_actions.get(str(row.get("scientific_state") or ""), "INTERNAL_REVIEW_REQUIRED")
        if action.get("action_class") != expected_action: errors.append(f"ResearchItem primary next action drifted:{row.get('code')}:{row.get('scientific_state')}->{action.get('action_class')}")
        if action.get("machine_actionable") is not False or any(action.get(key) is not False for key in ("scientific_authority","experiment_authority","p0_authority","gpu_authority")): errors.append(f"ResearchItem next action leaked authority:{row.get('code')}")
        if row.get("scientific_state") == "HOLD" and (not action.get("blocking_on") or action.get("reopen_condition_present") is not True): errors.append(f"HOLD ResearchItem missing explicit reopen condition:{row.get('code')}")
        if row.get("scientific_state") == "PAPER_READY" and not action.get("paper_id"): errors.append(f"PAPER_READY ResearchItem missing PaperState handoff:{row.get('code')}")
    by_code = {r.get("code"):r for r in items}
    for code in ("A-3","B-2","B-3","E-1"):
        if by_code.get(code,{}).get("scientific_state") != "HOLD": errors.append(f"{code} must be HOLD, not scientific failure")
    if by_code.get("F-4", {}).get("scientific_state") == "ACTIVE" or by_code.get("F-4", {}).get("portfolio_disposition") == "ACTIVE_RESEARCH": errors.append("F-4 is a closed shadow object and must never occupy an active ResearchItem slot")
    if by_code.get("E-7",{}).get("scientific_state") != "PAPER_READY" or (by_code.get("E-7",{}).get("paper_transition") or {}).get("paper_id") != "STRI" or (by_code.get("E-7",{}).get("paper_transition") or {}).get("status") != "SUBMISSION_READY": errors.append("E-7 must remain PAPER_READY scientifically and bind to STRI/SUBMISSION_READY in Paper Acceptance")
    if by_code.get("G-1",{}).get("scientific_state") != "HOLD" or by_code.get("G-1",{}).get("principle_dead_end_certified"): errors.append("G-1 broader research/replication program must remain reopenable HOLD")
    g1_paper = by_code.get("G-1",{}).get("paper_transition") or {}
    if g1_paper.get("status") != "SUBMISSION_READY" or g1_paper.get("scientific_status") != "READY" or g1_paper.get("blocked") is not False: errors.append("G-1 bounded R9 PaperState must be READY / SUBMISSION_READY while the broader ResearchItem remains HOLD")
    if any(bool((r.get("execution_authority") or {}).get("gpu")) for r in items): errors.append("ResearchItem projection cannot expose current GPU authority")
    if any(r.get("scientific_authority") is not False for r in experiments): errors.append("ExperimentRecord projection must remain zero scientific-transition authority")
    public_codes = set(codes)
    public_codes.update(r.get("portfolio_code") for r in experiments if r.get("portfolio_context"))
    public_codes.update(r.get("code") for r in contexts if r.get("portfolio_context"))
    if len(public_codes) != expected_portfolio_objects: errors.append(f"portfolio codes must be unique across {expected_portfolio_objects} objects, got {len(public_codes)}")
    return errors


def validate_paper_registry(registry, research_state):
    errors = []
    papers = registry.get("papers") or []
    acceptance, acceptance_by_id = paper_acceptance_state()
    expected_ids = {"STRI" if key == "STRI-ICLR2027" else key for key in acceptance_by_id}
    actual_ids = {row.get("paper_id") for row in papers}
    if actual_ids != expected_ids:
        errors.append(f"PaperRegistry must project every canonical acceptance ledger: expected={sorted(expected_ids)}, actual={sorted(str(x) for x in actual_ids)}")
    by_id = {row.get("paper_id"): row for row in papers}
    publication_identities = build_publication_identities()
    if set(publication_identities) != actual_ids:
        errors.append(f"Every PaperRegistry paper must have one append-only publication registration: registered={sorted(publication_identities)}, actual={sorted(str(x) for x in actual_ids)}")
    publication_codes = []
    for row in papers:
        paper_id = str(row.get("paper_id") or "")
        identity = row.get("publication_identity") or {}
        expected_identity = publication_identities.get(paper_id) or {}
        code = str(identity.get("code") or "")
        category = str(identity.get("category") or "")
        ordinal = int(identity.get("ordinal") or 0)
        publication_codes.append(code)
        if identity != expected_identity:
            errors.append(f"publication identity drifted:{paper_id}:{identity}")
        if category not in PUBLICATION_CATEGORY_LABELS or not re.fullmatch(r"[A-G][1-9][0-9]*", code) or code != f"{category}{ordinal}":
            errors.append(f"invalid publication code/category:{paper_id}:{code}:{category}:{ordinal}")
        if identity.get("category_zh") != (PUBLICATION_CATEGORY_LABELS.get(category) or {}).get("zh") or identity.get("category_en") != (PUBLICATION_CATEGORY_LABELS.get(category) or {}).get("en"):
            errors.append(f"publication category label drifted:{paper_id}:{identity}")
        if not str(identity.get("method") or "").strip() or not str((identity.get("idea") or {}).get("zh") or "").strip() or not str((identity.get("idea") or {}).get("en") or "").strip():
            errors.append(f"publication identity missing method/idea:{paper_id}")
        if (row.get("downloads") or {}).get("pdf") != identity.get("pdf"):
            errors.append(f"publication PDF alias must match PaperRegistry download:{paper_id}")
    if len(publication_codes) != len(set(publication_codes)):
        errors.append(f"publication codes must be unique:{publication_codes}")
    if list((registry.get("summary") or {}).get("publication_codes") or []) != publication_codes:
        errors.append("PaperRegistry publication-code summary must follow paper display order")
    actual_category_counts = dict(sorted(Counter((row.get("publication_identity") or {}).get("category") for row in papers).items()))
    if dict((registry.get("summary") or {}).get("by_publication_category") or {}) != actual_category_counts:
        errors.append("PaperRegistry publication category summary drifted")
    expected_discovery_aliases = []
    for row in papers:
        if str(row.get("source_kind") or "") != "paper-first-discovery-candidate":
            continue
        source_candidates = list(row.get("source_candidates") or [])
        provenance = row.get("discovery_provenance") or {}
        expected_provenance = build_discovery_provenance(source_candidates)
        if provenance != expected_provenance:
            errors.append(f"discovery provenance alias drifted:{row.get('paper_id')}:{provenance}")
        aliases = list(provenance.get("candidate_aliases") or [])
        expected_discovery_aliases.extend(aliases)
        if list(provenance.get("historical_candidate_ids") or []) != source_candidates:
            errors.append(f"discovery provenance must retain exact historical ids:{row.get('paper_id')}")
        if provenance.get("historical_ids_hidden_by_default") is not True:
            errors.append(f"historical discovery ids must be hidden by default:{row.get('paper_id')}")
        if any(not re.fullmatch(r"DISC[1-9][0-9]*-[0-9]{2,}", alias) for alias in aliases):
            errors.append(f"invalid reader discovery alias:{row.get('paper_id')}:{aliases}")
        if any(alias.startswith("PF") or re.fullmatch(r"[A-G][1-9][0-9]*", alias) for alias in aliases):
            errors.append(f"reader discovery alias collides with PF/A-G namespaces:{row.get('paper_id')}:{aliases}")
    if list((registry.get("summary") or {}).get("discovery_aliases") or []) != expected_discovery_aliases:
        errors.append("PaperRegistry discovery-alias summary drifted")
    paper = by_id.get("STRI") or {}
    safety = by_id.get("AGENT-SAFETY-R9") or {}
    if paper.get("source_research_item") != "E-7" or paper.get("acceptance_paper_id") != "STRI-ICLR2027":
        errors.append("STRI must bind E-7 to the STRI-ICLR2027 acceptance ledger")
    if (int(paper.get("claims_supported") or 0), int(paper.get("claims_total") or 0)) != (3,3):
        errors.append("STRI frozen supported claims must remain 3/3")
    if int(paper.get("paper_quality_evidence_debt") or 0) != 0:
        errors.append("legacy STRI evidence checklist must remain zero-debt")
    if paper.get("paper_stage") != "SUBMISSION_READY" or paper.get("submission_ready") is not True:
        errors.append(f"STRI must follow latest acceptance state SUBMISSION_READY with submission_ready=true, got {paper.get('paper_stage')}/{paper.get('submission_ready')}")
    if safety.get("source_research_item") != "G-1" or safety.get("paper_stage") != "SUBMISSION_READY" or safety.get("scientific_status") != "READY" or safety.get("submission_ready") is not True:
        errors.append("Agent Safety bounded R9 PaperState must be G-1 / READY / SUBMISSION_READY")

    expected_summary = (acceptance.get("ledger_index") or {}).get("summary") or {}
    summary = registry.get("summary") or {}
    if int(summary.get("papers") or 0) != int(expected_summary.get("papers") or 0):
        errors.append("PaperRegistry paper count must match canonical acceptance ledger index")
    if int(summary.get("submission_ready") or 0) != int(expected_summary.get("submission_ready") or 0):
        errors.append("PaperRegistry submission-ready count must match canonical acceptance ledger index")
    if int(summary.get("scientific_holds") or 0) != int(expected_summary.get("scientific_holds") or 0):
        errors.append("PaperRegistry scientific-hold count must match canonical acceptance ledger index")
    for registry_key, ledger_key in (("gate_clean_submission_ready","gate_clean_submission_ready"),("paper_preparation_failed","paper_preparation_failed"),("immediate_submission_holds","immediate_submission_holds"),("internal_action_required","internal_action_required"),("no_internal_action","no_internal_action")):
        if int(summary.get(registry_key) or 0) != int(expected_summary.get(ledger_key) or 0):
            errors.append(f"PaperRegistry {registry_key} count must match canonical acceptance ledger index")
    if dict(summary.get("by_internal_action") or {}) != dict(expected_summary.get("by_internal_action") or {}):
        errors.append("PaperRegistry internal next-action distribution must match canonical acceptance ledger index")

    research_codes = {r.get("code") for r in research_state.get("research_items") or []}
    for row in papers:
        source_kind = str(row.get("source_kind") or "")
        source_item = row.get("source_research_item")
        if source_kind == "research-item":
            if source_item not in research_codes:
                errors.append(f"PaperState source ResearchItem is missing: {row.get('paper_id')}->{source_item}")
        elif source_kind == "paper-first-discovery-candidate":
            if source_item is not None or not (row.get("source_candidates") or []) or not row.get("source_research_object"):
                errors.append(f"paper-first PaperState must preserve candidate/object provenance without fake ResearchItem parentage: {row.get('paper_id')}")
        else:
            errors.append(f"unknown PaperState source_kind:{row.get('paper_id')}:{source_kind}")
    if any(bool((row.get("acceptance_authority") or {}).get(key)) for row in papers for key in ("scientific","experiment","gpu","submission")):
        errors.append("PaperRegistry must preserve zero automatic authority from acceptance ledgers")
    return errors
