from __future__ import annotations

from typing import Any

from .method_details_common import bi


def fresh(summary_zh: str, summary_en: str, sources: list[dict[str, str]]) -> dict[str, Any]:
    return {"review_date": "2026-08-10", "summary": bi(summary_zh, summary_en), "sources": sources}


DETAILS: dict[str, dict[str, Any]] = {
    "recovery-conditioned-experience": {
        "title": bi("残余状态效应驱动的经验准入", "Residual-State Effect Admission"),
        "purpose": bi("恢复轨迹、harm recovery 和 recovery memory 都已有工作；剩下的窄失败模式是：任务虽然 success，但扰动后终点/重汇合点仍有可执行残余状态，而 success-only writer 把这类轨迹正向写入并在未来复用时造成伤害。", "Recovery trajectories, harm recovery, and recovery memory are already studied. The narrow remaining failure mode is that a task succeeds while executable residual state remains after perturbation, a success-only writer stores the trajectory positively, and future reuse causes harm."),
        "core_idea": bi("先做 P0a 现象门：同起点配对正常成功与扰动后成功轨迹，读取 exact program state，计算对象位置、持有物、开关/权限/资源等 residual vector Δs，并审计 baseline writer 是否正向写入。只有发生率足够才做 P0b：用未来 matched reuse harm 监督 residual-effect admission score，决定 write/summarize/quarantine。", "First run a P0a phenomenon gate: pair normal and perturbed-success trajectories from the same start, read exact program state, compute a residual vector Δs over object locations, inventory, switches/permissions/resources, and audit whether a baseline writer stores them positively. Only if prevalence is sufficient run P0b: supervise a residual-effect admission score with future matched-reuse harm to choose write/summarize/quarantine."),
        "core_intuition": bi("最终 success 只说明目标完成，不说明环境状态已经恢复；真正决定经验能否安全复用的是那些被 success 指标忽略的残余状态。", "Final success says the goal was completed, not that the environment was restored. Safe reuse may depend on residual state ignored by success metrics."),
        "concrete_example": bi("正常成功轨迹结束时抽屉关闭、工具归位；扰动后成功轨迹虽然拿到目标物，但抽屉仍开、备用工具被占用。两条都 success=1。若 writer 都写成正经验，后者未来复用可能让另一个任务失败。", "A normal success ends with the drawer closed and tools restored; a perturbed success obtains the target object but leaves the drawer open and a spare tool occupied. Both have success=1. If both are stored positively, reusing the latter may harm a future task."),
        "method_logic": bi("P0a: 1) exact-state 环境；2) 同起点 normal/perturbed success 配对；3) 重汇合点/终点算 typed Δs；4) 审计 success-only writer；5) prevalence 不足立即停。P0b: 6) 对已写经验做 future memory OFF/ON matched reuse；7) 以真实 harm 监督 residual-effect score；8) 与 endpoint equality/手工 threshold 匹配 replay 比较。", "P0a: 1) exact-state environment; 2) pair same-start normal/perturbed successes; 3) compute typed Δs at rejoin/endpoints; 4) audit a success-only writer; 5) stop immediately if prevalence is low. P0b: 6) run future memory OFF/ON matched reuse for stored experiences; 7) supervise a residual-effect score with true harm; 8) compare with endpoint equality/hand thresholds at matched replay."),
        "comparative_advantage": bi("不主张‘学恢复经验’；Dejavu/Recovery work 已覆盖。唯一变量是 success + nonzero executable Δs 是否被误写，以及 Δs 是否对未来 reuse harm 有增量预测力。", "The claim is not learning from recovery experience, which prior recovery work covers. The only variable is whether success + nonzero executable Δs is wrongly stored and whether Δs adds predictive value for future reuse harm."),
        "strongest_baseline": bi("手工 residual threshold：相同 typed Δs 与 future replay truth，只按预注册关键变量/非零计数决定 write/quarantine，不学习 score。", "Hand residual threshold: same typed Δs and future-replay truth, using preregistered critical variables/nonzero counts for write/quarantine without a learned score."),
        "pilot": bi("P0a 至少 100 对 normal/perturbed successes；只有 success+Δs 非零且被 writer 正向写入达到预注册 prevalence 才启动 P0b。P0b 固定相同 future replay 数比较 success-only、endpoint equality、hand threshold、learned residual-effect。", "P0a uses at least 100 normal/perturbed-success pairs; P0b starts only if success+nonzero-Δs positive writes exceed a preregistered prevalence. P0b fixes the same future replay count across success-only, endpoint equality, hand threshold, and learned residual-effect arms."),
        "metric": bi("P0a prevalence、Δs 类型分布；P0b future harmful-reuse rate、task success、false quarantine、AUROC/AUPRC 和 matched replay cost。", "P0a prevalence and Δs-type distribution; P0b future harmful-reuse rate, task success, false quarantine, AUROC/AUPRC, and matched replay cost."),
        "stop": bi("若 success+nonzero Δs 的正向写入很少、Δs 对 future harm 无预测力、或手工 threshold 等效，则停止，不把 recovery 当论文贡献。", "Stop if positive writes of success+nonzero Δs are rare, Δs does not predict future harm, or the hand threshold matches; do not claim recovery as a contribution."),
        "persistent_update_object": bi("经验 write/summarize/quarantine 状态与 residual-effect admission score；原始 exact-state evidence 保留。", "Experience write/summarize/quarantine state and a residual-effect admission score, with raw exact-state evidence retained."),
        "learning_signal": bi("未来 matched memory OFF/ON reuse 的程序化 harm，监督 Δs 特征对应的经验准入。", "Programmatic harm from future matched memory OFF/ON reuse supervises admission from Δs features."),
        "independent_truth": bi("exact program state 与 future task execution；success-only writer/learned score 不提供自证标签。", "Exact program state and future task execution; the success-only writer/learned score cannot self-label."),
        "collision_boundary": bi("Dejavu/trajectory-memory methods 已从恢复轨迹生成经验，Human-Guided Harm Recovery 也直接研究 recovery。因此只保留 success-only writer 对 success+nonzero Δs 的误准入及其未来 reuse harm。", "Dejavu/trajectory-memory methods already learn from recovery trajectories, and Human-Guided Harm Recovery directly studies recovery. The surviving boundary is erroneous success-only admission of success+nonzero Δs and its future reuse harm."),
        "nearest_work": ["Trajectory-informed memory generation", "Human-Guided Harm Recovery", "ShiftBench"],
        "fresh_reducibility_check": fresh("恢复本身不新；先用 prevalence gate 验证窄 failure mode，再谈 learned admission。", "Recovery itself is not new; first verify the narrow failure mode with a prevalence gate before learning admission.", [
            {"title": "Human-Guided Harm Recovery for Computer Use Agents", "url": "https://openreview.net/forum?id=hHR39fUK3u"},
            {"title": "ShiftBench: Measuring Recovery of Agent Memory Under Distribution Shift", "url": "https://openreview.net/forum?id=CCSztIjmOy"},
        ]),
        "redesign_iteration": {"round": "2026-08-10", "verdict": "phenomenon-gate-first", "summary": bi("保留窄 failure mode：success-only writer 是否会正向写入 success+nonzero Δs。P0a 现象不存在就立即停，存在才学 residual-effect admission。", "Keep only the narrow failure mode: whether success-only writers admit success+nonzero Δs. Stop at P0a if absent; learn residual-effect admission only if real.")},
    },
}
