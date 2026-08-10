from __future__ import annotations

from .method_details_common import bi
from .method_refinement_final_common_20260810 import final, iteration

DETAILS = {
    "regression-gated-self-evolution": {
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "只用历史版本做时间留出：固定 K 下 learned probe lifecycle 必须同时超过固定面板、随机轮换和简单历史敏感度排序；没有稳定未来版本增益就不跑 GPU。",
            "Use temporal holdout over historical versions only: at fixed K, learned probe lifecycle must beat fixed panels, random rotation, and simple historical-sensitivity ranking; no GPU run without stable future-version gain.",
            "同 K 固定/随机/历史敏感度 Probe 面板，不学习额外 gate。",
            "Equal-K fixed/random/historical-sensitivity probe panels with no additional learned gate.",
            "三套有效模型提案为 2 keep / 1 merge。generic pre-commit gating 已被 VaG 等覆盖，只保留固定预算下学习 Probe fidelity/lifecycle。",
            "The three valid model proposals vote 2 keep / 1 merge. Generic pre-commit gating is covered by VaG-like work; only learnable probe fidelity/lifecycle under a fixed budget survives.",
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "最终只保留固定 K 的 Probe fidelity/retirement policy。先做历史版本时间留出；固定/随机/简单敏感度面板同预算等效就合并，不再训练 learned gate。",
            "Only a fixed-K probe fidelity/retirement policy survives. Run temporal holdout on historical versions first; merge if fixed/random/simple-sensitivity panels match at equal budget.",
        ),
    },
    "compositional-update-compatibility": {
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "先在异构更新日志中确认非加性交互与顺序效应足够常见；pair 诱导 clause 后必须在完全未见 triples 上迁移。pairwise conflict score 已足够则停止。",
            "First verify that non-additive/order interactions are common in heterogeneous update logs; clauses induced from pairs must transfer to fully unseen triples. Stop if a pairwise conflict score is sufficient.",
            "等预算 pairwise conflict predictor + greedy ordering，看到相同 pair intervention 结果。",
            "Equal-budget pairwise conflict predictor plus greedy ordering with the same pair-intervention results.",
            "三个模型一致保留；现有工作覆盖 compositional model editing，但尚未直接覆盖 Prompt/Memory/Tool/Workflow 异构更新表面的冻结 typed repair grammar。",
            "All three models retain it. Existing work covers compositional model editing but not a frozen typed repair grammar across heterogeneous prompt/memory/tool/workflow update surfaces.",
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "不再主张‘更新会冲突’；只研究 pair intervention 能否编译成可复用 typed clause，并在未见 triples 上比 pairwise score 更少执行、更少回退。",
            "The claim is not that updates interact; it is whether pair interventions compile into reusable typed clauses that reduce executions and regressions on unseen triples beyond a pairwise score.",
        ),
    },
    "lineage-aware-rollback": {
        "purpose": bi(
            "版本化 rollback 已出现更直接的 Agent memory 系统，OS 层也已有高效增量 checkpoint/rollback；当前版本不再具备直接进入 P0 的新颖性边界。只有证明跨异构更新表面的固定存储预算行为等价压缩不能被 snapshot/delta checkpoint 解决，才值得复活。",
            "Direct agent-memory version control and efficient incremental checkpoint/rollback now exist. The current version is no longer P0-ready and is revivable only if cross-surface behavioral-equivalent compaction under a fixed storage budget cannot be solved by snapshot/delta checkpointing.",
        ),
        "fresh_reducibility_check": {
            "review_date": "2026-08-10",
            "summary": bi("ChronoMem 已直接做 Agent memory version control + semantic rollback，DeltaBox 做增量 checkpoint/rollback；A-5 暂停，除非能证明异构更新历史压缩有新的不可约变量。", "ChronoMem directly provides agent-memory version control and semantic rollback, while DeltaBox provides incremental checkpoint/rollback. Hold A-5 unless heterogeneous update-history compaction exposes a new irreducible variable."),
            "sources": [
                {"title": "ChronoMem: Version Control and Semantic Rollback for Large Language Model Agent Memory", "url": "https://arxiv.org/abs/2607.27773"},
                {"title": "DeltaBox: Scaling Stateful AI Agents with Millisecond-Level Sandbox Checkpoint/Rollback", "url": "https://arxiv.org/abs/2605.22781"},
            ],
        },
        "final_refinement": final(
            "hold-after-fresh-collision",
            "先做纯离线 storage-equivalence test：periodic snapshot、delta checkpoint 与 clause compactor 在同字节预算下若无稳定 rollback fidelity 差异，则永久停止。",
            "Run an offline storage-equivalence test first: if periodic snapshots, delta checkpoints, and the clause compactor show no stable rollback-fidelity difference at equal bytes, stop permanently.",
            "ChronoMem-style snapshots / DeltaBox-style delta checkpoints + deterministic replay。",
            "ChronoMem-style snapshots / DeltaBox-style delta checkpoints plus deterministic replay.",
            "三模型为 2 keep / 1 hold，但最新 ChronoMem 明显压缩 novelty；当前最合理状态是 HOLD。",
            "The three models vote 2 keep / 1 hold, but ChronoMem materially narrows novelty; HOLD is the defensible current state.",
            [
                {"title": "ChronoMem", "url": "https://arxiv.org/abs/2607.27773"},
                {"title": "DeltaBox", "url": "https://arxiv.org/abs/2605.22781"},
            ],
        ),
        "redesign_iteration": iteration(
            "hold-fresh-collision",
            "ChronoMem + DeltaBox 使版本控制/回滚/增量 checkpoint 已很拥挤。A-5 暂停；只有同存储预算下 snapshot/delta 无法保持而 learned compaction 能保持的跨表面行为等价出现时才复活。",
            "ChronoMem and DeltaBox make version control, rollback, and incremental checkpointing crowded. Hold A-5; revive only if equal-storage snapshot/delta baselines fail on a cross-surface behavioral-equivalence regime that learned compaction solves.",
        ),
    },
}
