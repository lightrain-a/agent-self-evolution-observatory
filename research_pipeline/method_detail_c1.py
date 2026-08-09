from __future__ import annotations

from .method_details_common import bi

DETAIL = {
    "core_intuition": bi(
        "同一个错误标签产生的十个后代，不是十票独立证据；跨轮自标注要先去掉同祖先、同来源的重复计票，再让标签驱动持久更新。",
        "Ten descendants of one wrong label are not ten independent votes; multi-round self-labeling must de-correlate shared ancestors/sources before labels drive persistent updates.",
    ),
    "concrete_example": bi(
        "第 1 轮把失败工具调用误标成成功，第 2 轮同源 evaluator 据此接受 Prompt 改写，第 3 轮又把这个改写当成新成功证据。普通置信度越积越高，但三轮其实继承自同一个错误。",
        "Round 1 mislabels a failed tool call as success; a same-family evaluator accepts a prompt rewrite in round 2; round 3 reuses that rewrite as fresh success evidence. Naive confidence rises although all evidence descends from one error.",
    ),
    "method_logic": bi(
        "0) 先在真实/公开日志测标签跨轮继承、同源 evaluator 复用和谱系错误富集；1) 若现象存在，记录 4–6 轮 Prompt/记忆/rubric 更新的 label-event DAG，节点含 generation、producer/evaluator family、parent IDs、confidence；2) 小型冻结独立 anchor 估计来源可靠度；3) 对共享祖先/来源的后代做有效样本数或协方差惩罚；4) 权重只控制持久轻量更新准入，不要求反复全参数训练；5) 比 current confidence、self-consistency、独立 anchor 阈值和 ancestry-blind 平均；6) 最后两轮和第二 evaluator family 前冻结。",
        "0) First measure cross-round inheritance, same-source evaluator reuse, and lineage error enrichment in real/public logs. 1) If present, record a label-event DAG over 4–6 prompt/memory/rubric update rounds with generation, producer/evaluator family, parent IDs, and confidence. 2) Estimate source reliability on small frozen independent anchors. 3) Penalize descendants sharing ancestors/sources via effective sample size or covariance. 4) Use the weight only for lightweight persistent-update admission, not repeated full-model training. 5) Compare current confidence, self-consistency, an independent-anchor threshold, and ancestry-blind averaging. 6) Freeze before the final two rounds and second evaluator family.",
    ),
    "comparative_advantage": bi(
        "最强简化是用同一个独立 anchor 集做单阈值准入；若它已经阻断相同错误，就没有必要保留谱系模型。",
        "The strongest simplification is a single-threshold rule on the exact same independent anchors; if it blocks the same errors, the lineage model is unnecessary.",
    ),
    "strongest_baseline": bi(
        "独立 anchor 阈值准入：相同 anchor、调用、标签和候选更新，只按当前候选的 anchor 通过率用冻结阈值判定，不建 provenance DAG。",
        "Independent-anchor threshold admission using the same anchors, calls, labels, and candidate updates; decide from current anchor pass rate with a frozen threshold and no provenance DAG.",
    ),
    "pilot": bi(
        "P0a 只审日志：至少 4 轮，先验证 lineage prevalence 和 lineage-conditioned error amplification；达到预注册门槛才进 P0b。P0b 只做 4–6 轮轻量 Prompt/记忆/rubric 更新，最后两轮和第二 evaluator family 留出。",
        "P0a is log-only: across at least four rounds, verify lineage prevalence and lineage-conditioned error amplification; proceed to P0b only above a preregistered threshold. P0b uses only 4–6 lightweight prompt/memory/rubric update rounds, holding out the final two rounds and a second evaluator family.",
    ),
    "metric": bi(
        "同源错误 amplification depth、harmful-update admission、useful-update retention、anchor 校准误差和第二 evaluator family 的未来任务表现。",
        "Same-source error amplification depth, harmful-update admission, useful-update retention, anchor calibration error, and future-task performance under a second evaluator family.",
    ),
    "stop": bi(
        "若真实日志的继承/同源复用低于现象门槛，或同一 anchor 的简单阈值与谱系去相关等效，则停止独立方法主张。",
        "Stop the standalone claim if real-log inheritance/same-source reuse is below the phenomenon threshold or a simple threshold on the same anchors is equivalent to lineage de-correlation.",
    ),
    "persistent_update_object": bi("候选 Prompt、记忆或 rubric 更新的谱系去相关准入状态；基础模型冻结。", "Lineage-decorrelated admission state for candidate prompt, memory, or rubric updates; the foundation model remains frozen."),
    "learning_signal": bi("label-event DAG、独立 anchor 正误标签和历史更新后的真实任务结果。", "Label-event DAG structure, independent-anchor correctness, and real task outcomes after historical updates."),
    "independent_truth": bi("冻结独立 anchor 和程序化任务结果；同源 actor/evaluator 的自信不能当最终真值。", "Frozen independent anchors and programmatic task outcomes; same-family actor/evaluator confidence cannot be final truth."),
    "fresh_reducibility_check": {"review_date":"2026-08-09","sources":[
        {"title":"Enhancing GUI Agent with Uncertainty-Aware Self-Trained Evaluator", "url":"https://proceedings.neurips.cc/paper_files/paper/2025/hash/d067d16e3e5fe8fa8a3e62909907659a-Abstract-Conference.html"},
        {"title":"SERM: Self-Evolving Relevance Model with Agent-Driven Learning from Massive Query Streams", "url":"https://aclanthology.org/2026.findings-acl.823/"},
    ]},
}
