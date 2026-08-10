from __future__ import annotations

from .method_details_common import bi
from .method_refinement_final_common_20260810 import final, iteration

DETAILS = {
    "outcome-equivalent-trajectory-contrast": {
        "final_refinement": final(
            "merge-unless-disagreement-found",
            "禁止再跑 GPU；先在冻结 trajectory/lesson pool 上找 utility-only 与 process-robust 的排序分歧。若没有稳定分歧，直接并入普通 utility admission。",
            "No further GPU run: first mine a frozen trajectory/lesson pool for ranking disagreements between utility-only and process-robust admission. If stable disagreements do not exist, merge into ordinary utility admission.",
            "utility-only admission：完全相同 lesson、memory OFF/ON replay 和预算，只看平均干预效用。",
            "Utility-only admission with identical lessons, memory OFF/ON replays, and budget, using only mean intervention utility.",
            "三模型都认为理论机制可行，但 canonical Round-1 中四种策略选出相同 lesson；在真实 disagreement 出现前，process invariance 不是独立贡献。",
            "All three models find the mechanism plausible, but canonical Round-1 made all policies select the same lessons. Process invariance is not a standalone contribution until a real disagreement regime is found.",
        ),
        "redesign_iteration": iteration(
            "merge-unless-disagreement",
            "当前不扩样，先做 disagreement mining。找不到 utility-only 与 cross-process 的决策分歧就合并；只有分歧样本上后者减少负迁移才恢复独立方法。",
            "Do disagreement mining instead of scaling. Merge if utility-only and cross-process admission do not make different decisions; revive only if the latter reduces negative transfer on disagreement cases.",
        ),
    },
    "contradiction-preserving-consolidation": {
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "在已有 episode 日志上先验证：删除一个很小 contradiction core 是否会改变规则结论/适用边界；若结论不敏感，core 只是摘要装饰，不启动 P0。",
            "On existing episode logs, first verify that deleting a small contradiction core changes the rule conclusion/applicability boundary; if conclusions are insensitive, the core is decorative and P0 is blocked.",
            "immutable episodic-only memory：同 context/storage 预算直接检索原始 episode。",
            "Immutable episodic-only memory at the same context/storage budget, directly retrieving raw episodes.",
            "三模型一致保留。MERIT 等最新工作保存正/负经验，但没有直接构造 conclusion-changing evidence core，边界仍可辨识。",
            "All three models retain it. Recent work such as MERIT stores positive/negative experience but does not directly construct conclusion-changing evidence cores.",
            [{"title":"Causal Episodic Memory for Feedback-Driven Agent Repair (MERIT)","url":"https://arxiv.org/abs/2608.05906"}],
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "最终变量是‘规则必须携带能改变结论的最小原始证据核心’，不是更好的 summary。先离线证明 deletion sensitivity，再和 episodic-only 同预算比较。",
            "The final variable is that a rule must carry a minimal raw-evidence core that can change its conclusion, not a better summary. Prove deletion sensitivity offline, then compare with episodic-only memory at equal budget.",
        ),
    },
    "retrieval-interference-auditor": {
        "final_refinement": final(
            "phenomenon-gate-before-standalone",
            "只用历史 retrieval/intervention 日志测 pairwise residual：per-item CMI 已筛过后，A+B 的额外负效应必须足够常见且不能由共现频率解释；否则并入普通 memory selection。",
            "Use historical retrieval/intervention logs to estimate pairwise residuals after per-item CMI selection. A+B must show sufficiently prevalent extra harm not explained by co-occurrence frequency; otherwise merge into ordinary memory selection.",
            "per-item CMI + 简单 frequent-pair exclusion，同样 replay 预算。",
            "Per-item CMI plus simple frequent-pair exclusion at the same replay budget.",
            "两模型建议 merge、一模型保留；CMI、Causal-AgentIR、MERIT 让 generic harmful-memory selection 很拥挤。只有高 prevalence 不可加性交互残差才能支撑独立方法。",
            "Two models recommend merge and one retain. CMI, Causal-AgentIR, and MERIT make generic harmful-memory selection crowded; only a prevalent non-additive interaction residual can support a standalone method.",
            [
                {"title":"Causal Intervention-Based Memory Selection for Long-Horizon LLM Agents","url":"https://arxiv.org/abs/2605.17641"},
                {"title":"Causal-AgentIR","url":"https://arxiv.org/abs/2607.21125"},
                {"title":"MERIT","url":"https://arxiv.org/abs/2608.05906"},
            ],
        ),
        "redesign_iteration": iteration(
            "phenomenon-gate-first",
            "先证明‘单条都安全、一起检索才有额外伤害’在真实日志里足够常见。不存在高 prevalence pairwise residual 就并入 CMI/普通 memory selection。",
            "First prove that memories safe individually but harmful jointly occur often enough in real logs. Without a prevalent pairwise residual, merge into CMI/ordinary memory selection.",
        ),
    },
    "causally-verified-experience-admission": {
        "final_refinement": final(
            "merge-into-A3",
            "不再建立独立 P0；只把 memory-scope feature 加进 A-3 固定 K Probe allocator，离线看是否提高 probe-selection fidelity。",
            "Do not build a standalone P0; add memory-scope features only to A-3's fixed-K probe allocator and test offline whether probe-selection fidelity improves.",
            "A-3 通用 fixed-K regression panel，完全相同 K/hidden truth/candidate lessons。",
            "A-3 generic fixed-K regression panel with identical K, hidden truth, and candidate lessons.",
            "三个模型一致建议 merge；B-4 没有独立于 A-3 的持久学习对象，真正有价值的是 probe allocation feature。",
            "All three models recommend merge. B-4 lacks a persistent learned object independent of A-3; the useful part is a probe-allocation feature.",
        ),
        "redesign_iteration": iteration(
            "merge-into-A3",
            "B-4 不再作为独立论文方法；memory-specific influence scope 只作为 A-3 Probe allocator 的一个候选特征。",
            "B-4 is no longer a standalone paper method; memory-specific influence scope becomes a candidate feature inside the A-3 probe allocator.",
        ),
    },
    "local-counterexample-memory-repair": {
        "fresh_reducibility_check": {
            "review_date":"2026-08-10",
            "summary":bi("生产系统已有 deterministic executability gate；B-5 的边界只能是从真实 counterexample 学到最小单调适用边界，而不是一般 skill gating。","Production systems already use deterministic executability gates. B-5 survives only as learning a minimal monotone applicability boundary from verified counterexamples, not generic skill gating."),
            "sources":[
                {"title":"Don't Offer What Can't Be Done: Deterministic Executability Gating for LLM Skill Selection at Scale","url":"https://arxiv.org/abs/2608.01050"},
                {"title":"MEMOREPAIR","url":"https://arxiv.org/abs/2605.07242"},
            ],
        },
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "用历史正例/反例模拟 boundary growth：固定谓词词表下，最小单调排除必须覆盖反例且保留绝大多数旧正例；若需要自由 classifier 或复杂新谓词，停止。",
            "Simulate boundary growth on historical positives/counterexamples: under a fixed predicate vocabulary, minimal monotone exclusions must cover counterexamples while preserving most old positives; stop if a free classifier or complex new predicates are required.",
            "deterministic hard-stop predicate gate + unrestricted classifier，各自看到相同 counterexamples。",
            "Deterministic hard-stop predicate gate plus unrestricted classifier, each seeing the same counterexamples.",
            "三个模型一致保留；新 executability-gating 工作把边界压到‘从反例学习且只能最小单调收缩’。",
            "All three models retain it. New executability-gating work narrows the contribution to learning from counterexamples under a minimal monotone-shrink constraint.",
            [{"title":"Deterministic Executability Gating","url":"https://arxiv.org/abs/2608.01050"}],
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "skill body 永久冻结，只允许 external applicability gate 最小单调收缩。先离线证明固定谓词能排除反例并保持旧正例，再与 deterministic hard-stop 和自由 classifier 比。",
            "Freeze the skill body permanently and allow only minimal monotone shrinkage of an external applicability gate. Prove offline that fixed predicates exclude counterexamples while preserving old positives, then compare with deterministic hard-stops and a free classifier.",
        ),
    },
    "memory-half-life": {
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "对历史 activation + memory OFF/ON intervention 日志做时间切分；学习调度器必须在相同 audit fraction 下更早发现 utility drift，且不能比 recency/frequency 多用真值。",
            "Time-split historical activation plus memory OFF/ON intervention logs. The scheduler must detect utility drift earlier at the same audit fraction without using more truth than recency/frequency baselines.",
            "LRU/LFU/TTL/recency-frequency + 同比例随机 audit。",
            "LRU/LFU/TTL/recency-frequency plus equal-fraction random audit.",
            "三个模型一致保留；MemoPilot/ShiftBench 覆盖 memory learning/recovery，但固定 intervention-budget 下何时复验仍是窄调度问题。",
            "All three models retain it. MemoPilot/ShiftBench cover memory learning/recovery, while when to revalidate under a fixed intervention budget remains a narrow scheduling problem.",
            [
                {"title":"From Player to Master: Enhancing Test-Time Learning of LLM Agents via Reinforcement Learning over Memory","url":"https://openreview.net/forum?id=gNWNtstp3r"},
                {"title":"ShiftBench: Measuring Recovery of Agent Memory Under Distribution Shift","url":"https://openreview.net/forum?id=CCSztIjmOy"},
            ],
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "最终问题不是‘旧记忆多久删’，而是固定真实干预预算下‘哪些 activation 最值得复验’。先用时间留出日志打赢 LRU/LFU/TTL/recency-frequency，否则降级缓存组件。",
            "The final problem is not when old memories expire, but which activations deserve revalidation under a fixed intervention budget. Beat LRU/LFU/TTL/recency-frequency on temporal holdout first or demote to a cache component.",
        ),
    },
}
