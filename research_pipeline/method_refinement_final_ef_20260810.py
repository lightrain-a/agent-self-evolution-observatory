from __future__ import annotations

from .method_details_common import bi
from .method_refinement_final_common_20260810 import final, iteration

DETAILS = {
    "workflow-generalization-certificate": {
        "title": bi("条件编辑排序工作流策略", "Conditional Edit-Ranking Workflow Policy"),
        "core_idea": bi(
            "冻结 typed edit library 与 workflow 局部上下文表示。Source workflow 只做单编辑 paired before/after 干预得到 ΔU；学习同一 workflow 内 edit_i 与 edit_j 的 pairwise 排序或 normalized regret，而不是‘edit 是否有正收益’二分类。冻结后在未见 workflow 上禁止候选试跑，只允许直接选择并持久提交一个 edit。",
            "Freeze a typed edit library and local workflow-context representation. Source workflows provide paired single-edit before/after interventions yielding ΔU. Learn pairwise edit ranking or normalized regret within each workflow rather than binary positive-effect classification. Freeze before unseen workflows, forbid candidate trials, and allow exactly one edit selection and persistent commit.",
        ),
        "learning_signal": bi(
            "同一 source workflow 内不同 edit 的真实 paired ΔU 差/排序，直接监督 conditional best-edit ranking；不再用单个 edit 的正负标签替代论文主张。",
            "True paired ΔU differences/rankings among edits within the same source workflow directly supervise conditional best-edit ranking; binary positive-effect labels no longer substitute for the paper claim.",
        ),
        "strongest_baseline": bi(
            "global-best edit、nearest-neighbor historical edit reuse、同特征同容量 binary effect classifier，以及 CE-Graph propose-and-verify；所有方法共享 source paired-edit 数据，hidden 禁止候选试跑。",
            "Global-best edit, nearest-neighbor historical edit reuse, a capacity-matched binary effect classifier, and CE-Graph propose-and-verify; all share source paired-edit data and hidden workflows forbid candidate trials.",
        ),
        "pilot": bi(
            "先只做 offline calibration：按 workflow 留出，pairwise/listwise ranker 的 top-1 best-edit accuracy 必须比 global-best 高至少 25pp；未过门不得打开 fresh hidden。过门后才在 fresh hidden workflow 上一次 commit。",
            "Start with offline workflow-held-out calibration only. Pairwise/listwise ranking must exceed global-best top-1 best-edit accuracy by at least 25 points; fresh hidden workflows stay sealed until this gate passes. Only then allow one persistent commit on fresh hidden workflows.",
        ),
        "metric": bi("workflow-held-out top-1 best-edit accuracy、edit regret；只有 offline gate 通过后才看 fresh-hidden commit success / bad-commit rate。", "Workflow-held-out top-1 best-edit accuracy and edit regret; fresh-hidden commit success/bad-commit rate is measured only after the offline gate passes."),
        "fresh_reducibility_check": {
            "review_date":"2026-08-10",
            "summary":bi("GraphMind 已从 operational traces 自进化 workflow graph，COVENANT 编译并约束 workflow execution，CausalFlow 做 counterfactual repair；E-1 只剩 paired edit effect → frozen conditional ranker → hidden zero-search one-shot commit。","GraphMind evolves workflow graphs from operational traces, COVENANT compiles and constrains workflow execution, and CausalFlow performs counterfactual repair. E-1 survives only as paired edit effect → frozen conditional ranker → hidden zero-search one-shot commit."),
            "sources":[
                {"title":"GraphMind: From Operational Traces to Self-Evolving Workflow Automation","url":"https://arxiv.org/abs/2605.17617"},
                {"title":"COVENANT: Natural-Language Workflow Compilation for Aligned Agent Execution","url":"https://arxiv.org/abs/2607.25400"},
                {"title":"CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures","url":"https://arxiv.org/abs/2605.25338"},
            ],
        },
        "final_refinement": final(
            "advance-to-pre-p0-objective-gate",
            "复用已有 paired edit-effect matrix，不新增 rollout；pairwise/listwise objective 必须在 workflow-held-out calibration 上打赢 global-best/nearest-neighbor，才允许 fresh hidden。",
            "Reuse the existing paired edit-effect matrix with no new rollouts. A pairwise/listwise objective must beat global-best/nearest-neighbor on workflow-held-out calibration before fresh hidden workflows are opened.",
            "global-best / nearest-neighbor / 同容量 binary effect classifier。",
            "Global-best / nearest-neighbor / capacity-matched binary effect classifier.",
            "三模型为 2 keep / 1 merge。canonical Round-1 已证明 binary objective 与 paper claim 错位，因此本轮真正修复是 conditional ranking，而不是继续加 feature。",
            "The three models vote 2 keep / 1 merge. Canonical Round-1 showed the binary objective is misaligned with the paper claim; the material repair is conditional ranking rather than adding features.",
        ),
        "redesign_iteration": iteration(
            "pre-p0-objective-gate",
            "E-1 正式改成 conditional edit ranking：同一 workflow 内直接学哪个 edit 更好。先复用已有 paired matrix 做 workflow-held-out top-1/regret；打不赢 global-best 就停止，禁止再烧 GPU。",
            "E-1 is now conditional edit ranking: directly learn which edit is better within a workflow. Reuse the existing paired matrix for workflow-held-out top-1/regret; stop if it cannot beat global-best, with no further GPU spend.",
        ),
    },
    "workflow-branch-credit": {
        "final_refinement": final(
            "merge-into-E1",
            "不再单独推进；把 recurring failure motif / minimal causal subgraph 作为 E-1 local-context feature 或 edit explanation，在同一 paired-edit dataset 上做消融。",
            "Do not pursue standalone. Use recurring failure motifs/minimal causal subgraphs as E-1 local-context features or edit explanations and ablate them on the same paired-edit dataset.",
            "E-1 conditional edit ranker，不使用 motif feature。",
            "E-1 conditional edit ranker without motif features.",
            "三个模型一致 merge；CausalFlow 已直接做 causal attribution + minimal counterfactual repair，GraphMind/CE-Graph 也覆盖 workflow failure-driven graph adaptation。",
            "All three models recommend merge. CausalFlow directly performs causal attribution plus minimal counterfactual repair, while GraphMind/CE-Graph cover failure-driven workflow graph adaptation.",
            [
                {"title":"CausalFlow","url":"https://arxiv.org/abs/2605.25338"},
                {"title":"GraphMind","url":"https://arxiv.org/abs/2605.17617"},
            ],
        ),
        "redesign_iteration": iteration(
            "merge-into-E1",
            "E-2 不再作为独立论文方法。failure motif / causal subgraph 只保留为 E-1 conditional edit ranker 的结构化上下文特征；是否有增益用同一 paired matrix 做消融。",
            "E-2 is no longer a standalone paper method. Failure motifs/causal subgraphs remain only as structured context features for the E-1 conditional edit ranker, ablated on the same paired matrix.",
        ),
    },
    "world-model-error-gated-learning": {
        "final_refinement": final(
            "hold-scenario-check",
            "先用真实持续适应日志做 trace-only decision-switch audit：修正预测是否经常改变后续动作/风险/恢复决策，并检查该信号是否不等价于误差幅度；场景未确认前禁止设计 P0。",
            "Use real continual-adaptation logs for a trace-only decision-switch audit first: determine whether correcting predictions often changes subsequent action/risk/recovery decisions and whether that signal is non-equivalent to error magnitude. No P0 design before the setting is confirmed.",
            "largest-error / random equal-count transition admission。",
            "Largest-error / random equal-count transition admission.",
            "三模型为 2 hold / 1 keep。AAWM 已覆盖 decision-aware world-model target，因此当前只有真实 continual-adaptation 场景中的 fixed-budget transition admission 可能存活。",
            "The three models vote 2 hold / 1 keep. AAWM already covers decision-aware world-model targets, leaving only fixed-budget transition admission in a real continual-adaptation setting as a possible surviving boundary.",
        ),
        "redesign_iteration": iteration(
            "hold-scenario-check",
            "方法先暂停。和子龙确认真实持续适应场景，并用现有 transition log 做 decision-switch prevalence / error-magnitude non-equivalence 检查；没有现实信号就停止。",
            "Pause method work. Confirm the real continual-adaptation setting with Zilong and audit existing transition logs for decision-switch prevalence and non-equivalence to error magnitude; stop if the signal is absent.",
        ),
    },
    "irreversible-action-counterfactuals": {
        "final_refinement": final(
            "hold-reality-and-collision-check",
            "先在 exact simulator/program 环境验证不可逆事件是否跨 episode 重复、能否被紧凑 clause 覆盖，以及 clause reuse 是否比同总 simulator calls 的 test-time planner 少调用；任一不成立就停止。",
            "In an exact simulator/program environment, first verify that irreversible events recur across episodes, are covered by compact clauses, and clause reuse uses fewer calls than a test-time planner at the same total simulator budget. Stop if any condition fails.",
            "EvoCF/test-time counterfactual planner + deterministic safety predicates，同总 simulator calls。",
            "EvoCF/test-time counterfactual planner plus deterministic safety predicates at the same total simulator calls.",
            "三模型为 2 hold / 1 keep。EvoCF 已学习 failure-derived reusable constraints 并做 counterfactual planning，persistent irreversibility clause 必须先证明独立复用收益。",
            "The three models vote 2 hold / 1 keep. EvoCF already learns reusable failure-derived constraints and performs counterfactual planning, so persistent irreversibility clauses need an independent reuse advantage first.",
            [{"title":"EvoCF: Multi-Agent Collaboration via Agentic Memory-Driven Evolutionary Counterfactual Planning","url":"https://openreview.net/forum?id=zGKkewtb2w"}],
        ),
        "redesign_iteration": iteration(
            "hold-reality-simplification-check",
            "先确认真实不可逆事件与跨 episode 复用价值，再比较 persistent clause 与同调用 test-time counterfactual planner。未证明调用节省且不过度保守前，不进入 P0。",
            "First confirm real irreversible events and cross-episode reuse value, then compare persistent clauses with an equal-call test-time counterfactual planner. No P0 before showing call savings without excess conservatism.",
        ),
    },
    "recovery-conditioned-experience": {
        "fresh_reducibility_check": {
            "review_date":"2026-08-10",
            "summary":bi("MERIT 已把 verified successful corrections / unsuccessful directions 写入跨 episode memory，Human-Guided Harm Recovery 研究恢复本身；F-3 只保留 success label 过粗导致 success+nonzero residual 被错误写成正经验这一 failure mode。","MERIT stores verified corrections/unsuccessful directions across episodes and Human-Guided Harm Recovery studies recovery itself. F-3 survives only as the failure mode where a coarse success label admits success+nonzero-residual trajectories as positive experience."),
            "sources":[
                {"title":"Causal Episodic Memory for Feedback-Driven Agent Repair (MERIT)","url":"https://arxiv.org/abs/2608.05906"},
                {"title":"Human-Guided Harm Recovery for Computer Use Agents","url":"https://openreview.net/forum?id=joefYuOHWS"},
            ],
        },
        "final_refinement": final(
            "phenomenon-gate-before-learning",
            "只做 P0a trace/exact-state gate：统计 success+nonzero Δs prevalence、success-only writer 正向写入率，以及 residual 是否预测未来复用 harm；现象不足则停止，不训练 admission model。",
            "Run only the P0a trace/exact-state gate: estimate prevalence of success+nonzero Δs, positive-write rate of a success-only writer, and whether residuals predict future reuse harm. Stop without training an admission model if the phenomenon is weak.",
            "success-only admission + 手写 residual threshold，在同 exact-state truth 下比较。",
            "Success-only admission plus a hand-written residual threshold under the same exact-state truth.",
            "三个模型一致保留，但都放在 phenomenon gate 之后；最新 recovery-memory 工作说明贡献不能是‘从恢复轨迹学习’，只能是 residual-state admission。",
            "All three models retain it only after a phenomenon gate. Recent recovery-memory work rules out claiming learning from recovery trajectories itself; the contribution must be residual-state admission.",
        ),
        "redesign_iteration": iteration(
            "phenomenon-gate-first",
            "先证明‘任务成功但环境没有真正恢复’会被 success-only writer 当正经验写入，并且 residual Δs 对未来复用伤害有预测力。现象不存在就直接停；存在才设计 learner。",
            "First prove that task-success trajectories with incomplete state recovery are positively stored by a success-only writer and that residual Δs predicts future reuse harm. Stop if the phenomenon is absent; design a learner only if it exists.",
        ),
    },
}
