from __future__ import annotations

from .method_details_common import bi
from .method_refinement_final_common_20260810 import final, iteration

DETAILS = {
    "self-label-confidence-flow": {
        "final_refinement": final(
            "hold-reality-check",
            "先在真实多轮 self-labeling 日志中计算 wrong-ancestor → descendant error amplification；若继承稀少或简单 independent-anchor threshold 已足够，则停止。",
            "First measure wrong-ancestor to descendant error amplification in real multi-round self-labeling logs. Stop if inheritance is rare or a simple independent-anchor threshold is sufficient.",
            "independent-anchor threshold / source-level reliability weighting，不建 provenance DAG。",
            "Independent-anchor threshold/source-level reliability weighting without a provenance DAG.",
            "三个有效模型一致 HOLD。问题在真实系统中的普遍性尚未得到证据，继续设计更复杂 confidence flow 没有意义。",
            "All three valid models vote HOLD. The prevalence of the problem in real systems is unverified, so further confidence-flow design is premature.",
        ),
        "redesign_iteration": iteration(
            "hold-reality-check",
            "暂停方法设计。先证明同祖先/同来源标签在多轮 self-evolution 中真的造成可测错误放大；没有现象就停止，不因为理论上可能而造问题。",
            "Pause method design. First prove that shared-ancestor/shared-source labels cause measurable error amplification across self-evolution rounds; stop if the phenomenon is absent rather than manufacturing it.",
        ),
    },
    "evaluator-coadaptation-guard": {
        "fresh_reducibility_check": {
            "review_date":"2026-08-10",
            "summary":bi("SERPO 已共同进化 rubric/policy，REFORM 自修 reward model，rubric-RL reward hacking 也显示训练 evaluator 与参考质量会分离；C-2 只保留 actor-fixed cross-version attribution + evaluator-only repair。","SERPO co-evolves rubric/policy, REFORM self-repairs reward models, and rubric-RL reward hacking shows divergence from reference quality. C-2 survives only as actor-fixed cross-version attribution followed by evaluator-only repair."),
            "sources":[
                {"title":"SERPO: Self-Evolving Rubric Policy Optimization","url":"https://arxiv.org/abs/2607.26873"},
                {"title":"Teach a Reward Model to Correct Itself (REFORM)","url":"https://openreview.net/forum?id=F8RVIIdkkY"},
                {"title":"Reward Hacking in Rubric-Based Reinforcement Learning","url":"https://arxiv.org/abs/2605.12474"},
            ],
        },
        "final_refinement": final(
            "advance-to-pre-p0-reality-gate",
            "先用已有 actor/evaluator checkpoint 做 version matrix：同一冻结 actor 输出被 evaluator 版本变化显著重排时，才允许做 rubric intervention；否则简单 anchor calibration 已足够。",
            "Build a version matrix from existing actor/evaluator checkpoints first. Rubric intervention is allowed only if the same frozen actor outputs are materially re-ranked by evaluator-version changes; otherwise simple anchor calibration is sufficient.",
            "frozen independent-anchor calibration / evaluator threshold calibration。",
            "Frozen independent-anchor calibration / evaluator threshold calibration.",
            "三模型为 2 keep / 1 hold。最新 reward/rubric 工作很拥挤，因此只保留 actor-fixed attribution 后 evaluator-only sparse repair 这一窄变量。",
            "The three models vote 2 keep / 1 hold. Recent reward/rubric work is crowded, so only actor-fixed attribution followed by evaluator-only sparse repair survives.",
        ),
        "redesign_iteration": iteration(
            "pre-p0-reality-gate",
            "先做跨版本 actor-fixed score matrix，证明 evaluator 漂移能与 actor 改进分开识别；没有归因信号就不修 rubric。通过后再比较 sparse rubric repair 与简单 anchor calibration。",
            "First build an actor-fixed cross-version score matrix and prove evaluator drift is separately identifiable from actor improvement. No attribution signal means no rubric repair; only then compare sparse repair with simple anchor calibration.",
        ),
    },
    "counterexample-generating-curriculum": {
        "final_refinement": final(
            "advance-to-pre-p0-offline-gate",
            "GPU 前先在现有 counterexample pool 做 delta-debug：1-minimal 化必须显著去掉无关因素，并让错误边界更局部；若 non-minimal 同 verifier 同预算已等效，则停止。",
            "Before GPU training, delta-debug an existing counterexample pool. 1-minimalization must remove irrelevant factors and localize the error boundary; stop if non-minimal examples with the same verifier and budget are equivalent.",
            "同 proposer / verifier / 任务数的 non-minimal counterexample curriculum。",
            "Non-minimal counterexample curriculum with the same proposer, verifier, and task count.",
            "三个模型一致保留；已有工作覆盖 counterexample learning，独立价值只能来自 1-minimality 这一 curriculum variable。",
            "All three models retain it. Counterexample learning itself is covered; the independent value can only come from 1-minimality as a curriculum variable.",
        ),
        "redesign_iteration": iteration(
            "pre-p0-offline-gate",
            "强 proposer 全程冻结，verifier 独立判真。只研究 1-minimality 本身：同样 verified counterexamples，做/不做 delta-debug 是否改变样本效率和边界泛化。",
            "Freeze the strong proposer and use independent verifier truth. Study 1-minimality itself: with the same verified counterexamples, does delta-debugging improve sample efficiency and boundary generalization over no minimization?",
        ),
    },
}
