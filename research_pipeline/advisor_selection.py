from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .discussion_portfolio import build_discussion_portfolio

DEFAULT_JSON = PROJECT_ROOT / "generated" / "advisor-priority-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "advisor-priority-ideas.js"
DEFAULT_REVIEW_JSON = PROJECT_ROOT / "generated" / "advisor-priority-meta-review.json"
DEFAULT_REVIEW_RESPONSE = PROJECT_ROOT / "generated" / "advisor-priority-meta-review.response.md"

# This layer is deliberately comparative. All entries already passed their own R2.
# Scores answer a different question: which subset gives the strongest, most diverse
# ICLR portfolio under our actual low-resource constraints?
CURATED: dict[str, dict[str, Any]] = {
    "regression-gated-self-evolution": dict(cluster="governed-update", importance=5, distinctness=5, falsifiability=5, feasibility=4, story=5, diversity=5, complexity=1, tier="lead", rationale_zh="最宽且最直接的自进化可靠性主线；提交/回滚对象清楚，P0 可直接检验‘收益是否只是额外推理’，适合作为第一篇总叙事。", rationale_en="Broad and direct reliability thesis for self-evolution; commit/rollback is exact and P0 directly tests whether gains are merely extra inference."),
    "correction-action-causal-compiler": dict(cluster="causal-correction", importance=5, distinctness=5, falsifiability=5, feasibility=4, story=5, diversity=5, complexity=2, tier="lead", rationale_zh="把反思从自然语言总结推进到可干预验证的最小纠错动作组合，再编译成持久程序；机制和实验都很像 ICLR 方法论文。", rationale_en="Moves reflection from prose to intervention-verified minimal correction-action compositions compiled into persistent programs."),
    "update-composition-repair-compiler": dict(cluster="update-composition", importance=5, distinctness=5, falsifiability=5, feasibility=4, story=5, diversity=4, complexity=2, tier="lead", rationale_zh="不只检测更新冲突，而是学习兼容子句并保留尽量多的已有更新，故事比单纯 compatibility 更完整。", rationale_en="Goes beyond detecting update conflicts by learning compatibility clauses and preserving as many valid updates as possible."),
    "nested-pathway-memory-repair": dict(cluster="memory-causal-repair", importance=5, distinctness=5, falsifiability=5, feasibility=3, story=5, diversity=5, complexity=3, tier="lead", rationale_zh="把记忆伤害拆成纳入、内容、位置、共同检索等路径，嵌套随机化提供独立因果真值；是记忆方向里最完整的机制修复。", rationale_en="Decomposes memory harm into inclusion, content, rank, and co-retrieval pathways with nested randomized identification."),
    "bounded-probe-api-transition-operator": dict(cluster="api-transfer", importance=5, distinctness=5, falsifiability=5, feasibility=4, story=5, diversity=5, complexity=2, tier="lead", rationale_zh="P/E/X 转移对象明确，目标 API 只允许固定 N 个 probe，迁移和预算边界非常干净，适合作为工具/API 迁移主线。", rationale_en="The P/E/X transition object is exact and target adaptation is limited to a preregistered N-probe budget, yielding a clean transfer thesis."),
    "certified-out-of-span-interaction-inverter-v53": dict(cluster="parameter-update", importance=4, distinctness=5, falsifiability=5, feasibility=3, story=5, diversity=5, complexity=4, tier="high-upside", rationale_zh="理论/算法感最强：先认证历史更新张成空间内无可行修复，再学习新的空间外方向；2×2 机制实验把归因问题处理得很干净。", rationale_en="Most algorithmic/theory-flavored option: certify infeasibility inside the stored-update span, then learn a new out-of-span direction with a crossed mechanism test."),
    "workflow-repair-grammar-v5": dict(cluster="workflow-repair", importance=4, distinctness=5, falsifiability=4, feasibility=4, story=5, diversity=4, complexity=2, tier="high-upside", rationale_zh="冻结图重写产生式并禁止测试时搜索，API-disjoint × motif-disjoint 的组合迁移很容易形成清晰主表。", rationale_en="Frozen graph-rewrite productions with no test-time search and API-disjoint × motif-disjoint transfer provide a clean main experiment."),
    "rubric-intervention-sparse-solver": dict(cluster="evaluator-repair", importance=4, distinctness=5, falsifiability=5, feasibility=4, story=4, diversity=5, complexity=2, tier="high-upside", rationale_zh="独立干预识别 rubric 原子效应，再在中性维度保持约束下最小编辑；是 Critic/Evaluator 方向最清楚的持久修复对象。", rationale_en="Interventionally identifies rubric-atom effects and performs minimal persistent edits under neutral-dimension preservation constraints."),

    "contradiction-preserving-consolidation": dict(cluster="memory-consolidation", importance=4, distinctness=4, falsifiability=4, feasibility=5, story=4, diversity=3, complexity=1, tier="fast-pilot", rationale_zh="资源低、实验容易，但与后续记忆交互/路径修复相比机制上限较低；适合快速 P0 或作为记忆主线 baseline。", rationale_en="Cheap and easy to test, but later memory-interaction/causal-repair ideas have higher mechanism ceiling; useful as a fast P0 or baseline."),
    "probe-mutation-retirement-policy": dict(cluster="regression-testing", importance=4, distinctness=4, falsifiability=5, feasibility=5, story=4, diversity=5, complexity=2, tier="fast-pilot", rationale_zh="不训练基础模型，固定 probe 预算即可做多版本实验；适合低成本对冲，但更偏评测生命周期。", rationale_en="No foundation-model training is needed and fixed-budget version streams give a cheap decisive experiment, though the contribution leans toward evaluation lifecycle."),
    "monotone-applicability-specializer-v4": dict(cluster="rule-specialization", importance=4, distinctness=5, falsifiability=5, feasibility=5, story=4, diversity=5, complexity=2, tier="fast-pilot", rationale_zh="冻结可执行假设语言后，最小单调收缩非常容易做决定性实验；问题是任务特定规则语言可能限制普适性。", rationale_en="Minimal monotone specialization in a frozen executable language is easy to falsify, but task-specific rule languages may limit generality."),

    "compositional-update-compatibility": dict(cluster="update-composition", importance=5, distinctness=4, falsifiability=5, feasibility=4, story=4, diversity=2, complexity=1, tier="supporting", rationale_zh="问题非常核心，但 v4 的 Repair Compiler 已把 detection 推进到 repair；更适合作为其现象/P0 与 baseline。", rationale_en="Core problem, but the v4 Repair Compiler extends detection into repair; better as its phenomenon/P0 and baseline."),
    "restoration-clause-induction-v5": dict(cluster="update-composition", importance=4, distinctness=5, falsifiability=4, feasibility=3, story=4, diversity=2, complexity=3, tier="supporting", rationale_zh="关系子句本身新，但和 Update-Composition Repair Compiler 属于同一主线，可作为后者的轻量/可解释变体。", rationale_en="Novel relational clauses, but overlaps the update-composition family and is best treated as an interpretable variant."),
    "update-trust-region": dict(cluster="governed-update", importance=5, distinctness=4, falsifiability=4, feasibility=4, story=4, diversity=2, complexity=2, tier="supporting", rationale_zh="适合作为 Regression-Gated 的连续约束机制或强 baseline；单独做主线会分散可靠更新故事。", rationale_en="Useful as a continuous constraint or strong baseline for Regression-Gated, but separate positioning fragments the reliable-update story."),
    "memory-interaction-clause-learner": dict(cluster="memory-causal-repair", importance=4, distinctness=5, falsifiability=4, feasibility=4, story=4, diversity=2, complexity=2, tier="supporting", rationale_zh="很好的高阶记忆关系机制，但 Nested-Pathway Memory Repair 覆盖的失败机制更完整；可作为其交互路径后的持久约束层。", rationale_en="Strong higher-order memory relation mechanism, but Nested-Pathway Repair covers a broader causal failure decomposition; useful as a downstream constraint layer."),
    "constraint-complete-typed-memory-order-logic": dict(cluster="memory-causal-repair", importance=4, distinctness=5, falsifiability=5, feasibility=3, story=4, diversity=2, complexity=3, tier="supporting", rationale_zh="系统组合泛化很强，但与记忆交互子句同族；若保留记忆主线，适合做最强符号方法扩展。", rationale_en="Strong systematic-composition thesis, but overlaps the memory-interaction family; best as the symbolic extension of a memory mainline."),
    "effect-transport-lesson-specializer-v5": dict(cluster="knowledge-transfer", importance=5, distinctness=5, falsifiability=4, feasibility=2, story=5, diversity=5, complexity=4, tier="high-upside", rationale_zh="负迁移问题真实且重要，能把 gate 推进到持久 lineage bifurcation；但需要足够多任务族做 effect transport，实验资源较重。", rationale_en="Important negative-transfer problem and persistent lineage bifurcation beyond gating, but transport identification needs many task families and heavier experiments."),
    "api-error-semantic-adapter": dict(cluster="api-transfer", importance=4, distinctness=5, falsifiability=4, feasibility=4, story=4, diversity=2, complexity=2, tier="supporting", rationale_zh="很干净，但 Bounded-Probe API Transition Operator 的 P/E/X 对象和 N-probe 边界更完整；可做其中 error branch 或强 baseline。", rationale_en="Clean idea, but the bounded-probe P/E/X operator offers a more complete object and adaptation boundary; keep as an error-branch baseline."),
    "compiler-residual-contract-editor-v53": dict(cluster="api-transfer", importance=4, distinctness=5, falsifiability=5, feasibility=3, story=4, diversity=2, complexity=3, tier="supporting", rationale_zh="细粒度迁移编辑很扎实，但问题面较窄，适合与 API Transition Operator 合并成 compiler + residual 两阶段系统。", rationale_en="Rigorous fine-grained migration edit, but narrower; best merged with the API Transition Operator as a compiler-plus-residual system."),
    "update-history-semantic-compactor": dict(cluster="update-maintenance", importance=4, distinctness=5, falsifiability=4, feasibility=4, story=4, diversity=4, complexity=3, tier="second-wave", rationale_zh="多轮更新债务是真实长期问题，行为保持压缩有独立价值；但第一篇需要先证明频繁更新确实形成可观测历史负担。", rationale_en="Real long-horizon update-debt problem with behavior-preserving compression value, but a first paper must first establish measurable history burden."),
    "interventional-permission-triage-under-ceiling": dict(cluster="safety-governance", importance=5, distinctness=5, falsifiability=5, feasibility=4, story=4, diversity=5, complexity=2, tier="second-wave", rationale_zh="安全/权限方向很清楚，且 learner 不扩权只决定重验证对象；适合系统安全投稿或第二篇，不建议抢占 ICLR 主线。", rationale_en="Clear safety/permission thesis where the learner never expands authority, only triages revalidation; strong second-wave/system-safety direction."),
    "filtered-chronological-evaluator-state-v53": dict(cluster="evaluator-repair", importance=4, distinctness=5, falsifiability=5, feasibility=3, story=4, diversity=3, complexity=4, tier="second-wave", rationale_zh="纵向 evaluator drift 的识别做得非常严谨，但离‘Agent 自进化方法’主轴稍远，更像 evaluator infrastructure。", rationale_en="Very rigorous longitudinal evaluator-drift identification, but farther from the core self-evolution method thesis and closer to evaluator infrastructure."),
}

WEIGHTS = {
    "importance": 0.23,
    "distinctness": 0.24,
    "falsifiability": 0.18,
    "feasibility": 0.13,
    "story": 0.15,
    "diversity": 0.07,
}


def _load_meta_review() -> dict[str, Any]:
    if DEFAULT_REVIEW_JSON.exists():
        try:
            return json.loads(DEFAULT_REVIEW_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if DEFAULT_REVIEW_RESPONSE.exists():
        try:
            from .iclr_external_review import extract_json
            return extract_json(DEFAULT_REVIEW_RESPONSE.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    return {}


def _score(row: dict[str, Any]) -> float:
    base = sum(float(row[k]) * w for k, w in WEIGHTS.items())
    return round(base - 0.10 * float(row.get("complexity", 0)), 3)


def build_advisor_selection() -> dict[str, Any]:
    portfolio = build_discussion_portfolio()
    meta = _load_meta_review()
    meta_rows = {x.get("idea_id"): x for x in meta.get("ideas", []) if isinstance(x, dict)}
    rows = []
    for idea in portfolio["ideas"]:
        cfg = CURATED.get(idea["id"])
        if not cfg:
            raise ValueError(f"Missing advisor scorecard for {idea['id']}")
        row = {**idea, **cfg}
        row["score"] = _score(row)
        row["meta_review"] = meta_rows.get(idea["id"])
        rows.append(row)
    meta_rank = {x.get("idea_id"): int(x.get("advisor_rank", 999)) for x in meta.get("ideas", []) if isinstance(x, dict)}
    rows.sort(key=lambda x: (meta_rank.get(x["id"], 999), -x["score"], x["cluster"], x["id"]))
    for fallback_rank, row in enumerate(rows, 1):
        row["advisor_rank"] = meta_rank.get(row["id"], fallback_rank)
        if row.get("meta_review"):
            row["relative_tier"] = row["meta_review"].get("relative_tier", row["tier"])
            row["first_pilot_priority"] = row["meta_review"].get("first_pilot_priority", "medium")
            row["merge_with"] = row["meta_review"].get("merge_with", [])
        else:
            row["relative_tier"] = row["tier"]
            row["first_pilot_priority"] = "medium"
            row["merge_with"] = []

    by_id = {row["id"]: row for row in rows}
    meta_priority = meta.get("priority_first_read", meta.get("primary_shortlist", []))
    meta_primary = [idea_id for idea_id in meta_priority if idea_id in by_id]
    if meta_primary:
        primary = [by_id[idea_id] for idea_id in meta_primary[:8]]
    else:
        # Prefer one representative per overlapping mechanism family in the primary set.
        primary = []
        seen_clusters = set()
        for row in rows:
            if row["tier"] not in {"lead", "high-upside"} or row["cluster"] in seen_clusters:
                continue
            primary.append(row)
            seen_clusters.add(row["cluster"])
            if len(primary) == 8:
                break
        if len(primary) < 8:
            for row in rows:
                if row in primary or row["cluster"] in seen_clusters or row["tier"] == "supporting":
                    continue
                primary.append(row); seen_clusters.add(row["cluster"])
                if len(primary) == 8:
                    break

    return {
        "schema_version": "1.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_count": portfolio["count"],
        "discussion_target": portfolio["target"],
        "discussion_pool_count": len(rows),
        "priority_first_read_target": 8,
        "weights": WEIGHTS,
        "policy": {
            "all_inputs_already_r2_pass": True,
            "all_strict_passes_remain_in_discussion_pool": True,
            "comparative_not_absolute_review": True,
            "priority_first_read_is_navigation_only": True,
            "pilot_results_not_yet_available": True,
            "selection_is_not_selected_ready": True,
        },
        "discussion_pool": rows,
        "priority_first_read": primary,
        "ranked_ideas": rows,
        "clusters": sorted({x["cluster"] for x in rows}),
        "meta_review_status": meta.get("status", {"reviewed": len(meta.get("ideas", [])), "complete": len(meta.get("ideas", [])) == portfolio["count"]}),
        "portfolio_comment": "The comparative meta-review ranks all 22 discussion-ready ideas and suggests eight first reads to reduce review effort. These eight are not a shortlist that removes the other fourteen; all 22 remain formal candidates for senior/teacher discussion.",
        "portfolio_comment_zh": "相对元审查对全部 22 个正式讨论 Idea 做排序，并建议 8 个优先阅读方向以降低浏览成本。这 8 个不是替代其余 14 个的 shortlist；22 个方向都会完整进入人工讨论。",
    }


def write_advisor_selection(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    meta = _load_meta_review()
    if meta:
        public_meta = dict(meta)
        raw_priority = public_meta.pop("primary_shortlist", public_meta.get("priority_first_read", []))
        public_meta["priority_first_read"] = raw_priority
        public_meta["interpretation"] = "All 22 strict R2 PASS ideas remain in the formal senior-discussion pool. priority_first_read is only a navigation aid and does not remove the other ideas."
        public_meta["interpretation_zh"] = "22 个严格 R2 PASS 全部保留在正式师兄讨论池中；priority_first_read 只是优先阅读建议，不会移除其他 Idea。"
        public_meta["portfolio_comment"] = "The meta-review ranks all 22 formal discussion candidates and suggests eight first reads to reduce review effort; it does not reduce the discussion pool."
        public_meta["portfolio_comment_zh"] = "元审查对全部 22 个正式讨论候选做相对排序，并建议 8 个优先阅读方向以降低浏览成本；它不会把讨论池缩减到 8 个。"
        DEFAULT_REVIEW_JSON.write_text(json.dumps(public_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload = build_advisor_selection()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.ADVISOR_PRIORITY_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = write_advisor_selection()
    print(json.dumps({"discussion_pool": result["discussion_pool_count"], "priority_first_read": [x["id"] for x in result["priority_first_read"]]}, ensure_ascii=False))
