from __future__ import annotations

from .method_details_common import bi

DETAIL = {
    "core_intuition": bi(
        "记忆年龄应按真正发生的复用机会计数，而不是墙钟时间；只有记忆被激活时，才有机会观察它还在帮忙还是已开始害人。",
        "Memory age should be counted in actual reuse opportunities rather than wall-clock time; only activation reveals whether it still helps or has started to hurt.",
    ),
    "concrete_example": bi(
        "一个 API 重试规则两周没被调用、API 也没变，仍可能有效；另一个今天频繁使用的规则可在一次 schema 变更后下一次激活立刻失效。固定 TTL 会同时犯两类错误。",
        "An API retry rule unused for two weeks can remain valid if the API is unchanged, while a frequently used rule can fail on its next activation after a schema change. Fixed TTL makes both mistakes.",
    ),
    "method_logic": bi(
        "1) 每次真实激活记录任务族、API/schema 指纹、检索位置、状态谓词和 reuse index；2) 固定审计比例（如 20%）做 memory-on/off matched replay 得到边际效用；3) 用复用机会而非墙钟时间拟合条件 utility-drift/hazard；4) 仅当局部效用进入可能有害区时额外复验并隔离/删除；5) 留出 drift 前冻结；6) 与 LRU、LFU、TTL、定期复验和 recency+frequency 在相同审计预算下比较。",
        "1) Log task family, API/schema fingerprint, retrieval rank, state predicates, and reuse index on each real activation. 2) Audit a fixed fraction (e.g. 20%) with memory-on/off matched replay for marginal utility. 3) Fit conditional utility drift/hazard over reuse opportunities, not wall time. 4) Revalidate and quarantine/delete only when local utility enters a possibly harmful region. 5) Freeze before held-out drift. 6) Compare with LRU, LFU, TTL, periodic revalidation, and recency+frequency under the same audit budget.",
    ),
    "comparative_advantage": bi(
        "核心不是复杂缓存淘汰，而是用激活时的 memory-on/off 因果效用决定何时值得复验；所有基线共享相同审计比例和 replay 次数。",
        "The core is not complicated cache eviction but deciding when to revalidate from activation-time memory-on/off causal utility; all baselines share the same audit rate and replay count.",
    ),
    "strongest_baseline": bi(
        "容量匹配 recency+frequency 漂移预测器：相同激活日志、审计 replay 和模型容量，但不用 memory-on/off 效用或局部状态变化。",
        "Capacity-matched recency+frequency drift predictor using the same activation logs, audited replays, and model capacity, but no memory-on/off utility or local-state-change features.",
    ),
    "pilot": bi(
        "P0：可控 API/工具任务流中维护 30–40 条记忆，预注册局部 schema/API 变化与稳定区间，只审计 20% 真实激活；前半段拟合后冻结，在后半段未见 drift 上比较。",
        "P0: maintain 30–40 memories in a controlled API/tool stream with preregistered local schema/API changes and stable periods; audit only 20% of real activations, fit on the first half, freeze, and compare on unseen drift in the second half.",
    ),
    "metric": bi(
        "按复用机会计的 stale-memory 检出延迟、durable-memory 误删率、未来任务回退和每次审计 replay 的净收益。",
        "Stale-memory detection delay in reuse opportunities, durable-memory false-deletion rate, future-task regression, and net utility per audited replay.",
    ),
    "stop": bi(
        "若 recency+frequency、LRU/LFU 或 TTL 在同预算下等效，或 intervention utility/局部变化无额外预测力，则降级为缓存组件。",
        "If recency+frequency, LRU/LFU, or TTL is equivalent at the same budget, or intervention utility/local change adds no predictive value, demote to a cache component.",
    ),
    "persistent_update_object": bi("每条记忆的激活局部效用、复验和隔离/删除状态。", "Per-memory activation-local utility, revalidation, and quarantine/deletion state."),
    "learning_signal": bi("固定比例真实激活上的 memory-on/off replay 边际效用与后续真实任务结果。", "Memory-on/off replay marginal utility on a fixed fraction of activations plus subsequent real task outcomes."),
    "independent_truth": bi("真实工具/API 执行和预注册 drift；hazard/recency 分数不定义真值。", "Actual tool/API execution and preregistered drift; hazard/recency scores do not define truth."),
    "fresh_reducibility_check": {"review_date":"2026-08-09","sources":[
        {"title":"Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents", "url":"https://arxiv.org/abs/2606.27472"},
        {"title":"ShiftBench: Measuring Recovery of Agent Memory Under Distribution Shift", "url":"https://openreview.net/forum?id=CCSztIjmOy"},
        {"title":"Learning What to Remember", "url":"https://arxiv.org/abs/2606.12945"},
    ]},
}
