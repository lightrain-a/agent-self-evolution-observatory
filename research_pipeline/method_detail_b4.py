from __future__ import annotations

from .method_details_common import bi

DETAIL = {
    "core_intuition": bi(
        "不要把一条经验重跑在大量无关任务上；先预测它可能影响谁，再把固定 replay 预算花在受影响、边界和预计不受影响的 sentinel 上。若记忆特有范围信息不比通用回归 Probe 有用，就并入 A-3。",
        "Do not replay one lesson on many unrelated tasks. Predict whom it can affect, then spend a fixed replay budget on affected, boundary, and predicted-unaffected sentinels. If memory-specific scope adds nothing beyond generic regression probes, merge into A-3.",
    ),
    "concrete_example": bi(
        "例如‘工具报错后先切换工具’能修复一类恢复任务，却会伤害必须重试同一工具才能保持状态的任务。范围模型只把 tool-switch/retry 相关任务放进有限 sentinel，而不是遍历整个任务库。",
        "Example: 'switch tools after an error' can fix one recovery family but harm tasks where retrying the same tool is required. The scope model spends its limited sentinel budget on tool-switch/retry families rather than sweeping the task library.",
    ),
    "method_logic": bi(
        "1) 为经验提取触发条件、工具/错误类型、检索位置和任务结构签名；2) 仅用 discovery 经验的真实 before/after 影响拟合小型 scope predictor；3) 每条新经验固定选 6 个 sentinel：2 个预计受影响、2 个边界、2 个预计不受影响；4) 做源任务 matched replay + 同一 6 个 sentinel before/after；5) 源收益为正且 sentinel 无实质回退才写入；6) 留出任务族前冻结 predictor/选样规则；7) 把完全相同 6 个 Probe 交给 A-3 做 parent-merge 对照。",
        "1) Extract lesson triggers, tool/error type, retrieval position, and task-structure signature. 2) Fit a small scope predictor only from discovery before/after effects. 3) Select exactly six sentinels per lesson: two predicted affected, two boundary, two predicted unaffected. 4) Run source matched replay plus before/after on the same six sentinels. 5) Persist only with positive source benefit and no material sentinel regression. 6) Freeze predictor/selection before the held-out family. 7) Give the exact same six probes to A-3 as the parent-merge control.",
    ),
    "comparative_advantage": bi(
        "优势必须来自记忆触发/适用范围对固定 Probe 预算的分配，而不是多跑测试；决定性对照是同样 6 次 Probe 的 A-3。",
        "Any advantage must come from memory trigger/applicability scope allocating a fixed probe budget, not extra testing; the decisive control is A-3 with the same six probes.",
    ),
    "strongest_baseline": bi(
        "A-3 通用回归门控：完全相同的 6 个 Probe、before/after 真值和阈值预算，但不使用记忆触发/适用范围特征。",
        "Generic A-3 regression gating with the same six probes, before/after truth, and threshold budget, but no memory trigger/applicability features.",
    ),
    "pilot": bi(
        "P0：约 24 条候选经验、4 个可程序验证任务族；3 族拟合 scope，1 族完整留出。每条经验只允许源任务 replay + 6 个 sentinel。比较 scope、A-3、源任务因果门控和语义相似度，主结果只看留出族。",
        "P0: about 24 candidate lessons across four programmatically verifiable task families; fit scope on three and hold one family out entirely. Each lesson gets only source replay plus six sentinels. Compare scope, A-3, source-only causal gating, and semantic similarity; primary results use the held-out family.",
    ),
    "metric": bi(
        "留出族 harmful-admission precision/recall、最坏原任务回退、有用经验保留、future-task gain、每次 replay 避免的有害 commit。",
        "Held-out harmful-admission precision/recall, worst original-task regression, useful lessons retained, future-task gain, and harmful commits avoided per replay.",
    ),
    "stop": bi(
        "若同样 6 个 Probe 的 A-3 在留出族等效，立即 parent-merge；若 scope 只能靠更多 replay 获胜也停止。",
        "If A-3 with the same six probes is equivalent on the held-out family, parent-merge immediately; also stop if scope wins only through extra replay.",
    ),
    "persistent_update_object": bi("带触发/适用范围签名的经验条目及其准入状态。", "A lesson with trigger/applicability metadata and its admission state."),
    "learning_signal": bi("discovery 经验在源任务和候选 sentinel 上的程序化 before/after 影响。", "Programmatic before/after effects on source tasks and candidate sentinels for discovery lessons."),
    "independent_truth": bi("留出任务族的环境/程序 checker；scope 分数不能作为真值。", "Environment/program checkers on the held-out task family; scope scores cannot serve as truth."),
    "parent_id": "regression-gated-self-evolution",
    "parent_merge_rule": bi("去掉记忆特有范围特征后，若同预算 A-3 等效，则并入 A-3。", "Merge into A-3 if equal-budget A-3 is equivalent after removing memory-specific scope features."),
    "fresh_reducibility_check": {"review_date":"2026-08-09","sources":[
        {"title":"MemoPilot: From Player to Master", "url":"https://arxiv.org/abs/2606.08656"},
        {"title":"SEAM: Beyond Experience Retrieval", "url":"https://aclanthology.org/2026.acl-long.1831/"},
        {"title":"Memory-Induced Tool-Drift in LLM Agents", "url":"https://arxiv.org/abs/2605.24941"},
    ]},
}
