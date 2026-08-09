from __future__ import annotations

from typing import Any


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh.strip(), "en": en.strip()}


TRACK_UPDATE_OBJECTS: dict[str, dict[str, str]] = {
    "constrained": bi("版本化 Prompt、记忆或工作流状态及冻结提交规则。", "Versioned prompt, memory, or workflow state plus a frozen commit rule."),
    "credit": bi("经验/规则本体及其持久准入状态。", "The lesson/rule itself and its persistent admission state."),
    "memory": bi("持久记忆内容、检索元数据或复验状态。", "Persistent memory content, retrieval metadata, or revalidation state."),
    "correction": bi("跨 episode 复用的纠错策略或小型更新模块。", "A correction policy or small update module reused across episodes."),
    "curriculum": bi("被验证并持久加入后续更新轮次的任务/课程状态。", "Verified tasks/curriculum state persistently admitted to later update rounds."),
    "workflow": bi("版本化工作流图、结构编辑规则或冻结修复程序。", "A versioned workflow graph, structural edit rule, or frozen repair program."),
    "evaluator": bi("持久 evaluator/rubric 校准状态及更新准入规则。", "Persistent evaluator/rubric calibration state and update-admission rule."),
    "world": bi("持久世界状态/转移知识或经验准入状态。", "Persistent world-state/transition knowledge or experience-admission state."),
}


def generic_concrete_example(spec: Any) -> dict[str, str]:
    dataset = spec.datasets[0] if spec.datasets else "a held-out task set"
    return bi(
        f"例如在 {dataset} 中冻结原任务与候选更新，只允许声明的持久对象变化，再在未参与更新构造的同一批原任务上做 paired before/after；若简单等预算方法等效，就不保留额外机制。",
        f"For example on {dataset}, freeze original tasks and candidate updates, allow only the claimed persistent object to change, then run paired before/after on original tasks never used to construct the update. If a simpler equal-budget method matches it, the extra mechanism is not retained.",
    )


def original_task_evaluation() -> dict[str, Any]:
    return {
        "split_rule": bi("先冻结一个较大的原任务保护全集，完全不参与 discovery、更新构造、阈值拟合或候选选择。每次更新只从这个全集中按预注册影响范围与覆盖约束选固定小预算 sentinel；完整保护全集只用于低频审计。", "Freeze a larger protected universe of original tasks that never participates in discovery, update construction, threshold fitting, or candidate selection. Each update evaluates only a fixed-budget sentinel panel selected from that universe by preregistered impact and coverage rules; the full protected universe is reserved for low-frequency audits."),
        "paired_measurement": bi("同一原任务、同一基础模型、同一解码和同一随机种子做 update-before / update-after 配对。确定性任务默认单次配对；只有随机性较强或落在决策阈值附近的少数案例才自适应追加重复，不对 100+ 案例机械重复 2–3 次。", "Run paired update-before/update-after evaluation on the same original task, base model, decoding setup, and random seed. Deterministic tasks use one paired run by default; only stochastic or decision-boundary cases receive adaptive repeats rather than mechanically repeating 100+ tasks two or three times."),
        "independent_truth": bi("最终回退真值优先来自环境成功、程序 checker、精确匹配或已有金标。方法自己的 predictor/critic 可以选择 Probe，但不能兼任最终标签；Judge 若必须使用则异构、冻结，并带程序化 sanity subset。", "Final regression truth comes from environment success, program checkers, exact match, or existing gold labels. The method's own predictor/critic may select probes but cannot provide the final label; any necessary judge must be heterogeneous, frozen, and checked against a programmatic sanity subset."),
        "primary_endpoints": bi("同时报告目标收益、sentinel 上的配对回退、低频 full-audit 最坏回退、回退任务比例、sentinel→full-audit fidelity 和持久更新保留率。", "Report target gain, paired sentinel regression, worst regression on low-frequency full audits, fraction of tasks regressing, sentinel-to-full-audit fidelity, and persistent-update retention."),
        "budget_matching": bi("所有对照共享保护全集、候选池、固定 sentinel 数 K 和执行/调用/token 上限。Probe 选择、额外 Judge、replay、边界案例重复和 full audit 全部计入预算；full audit 只能在同样的低频 checkpoint 触发。", "All controls share the protected universe, candidate pool, fixed sentinel count K, and execution/call/token caps. Probe selection, extra judges, replay, adaptive repeats, and full audits all count against budget, and full audits may trigger only at the same low-frequency checkpoints."),
    }


def parent_merge_gate(fields: dict[str, Any]) -> dict[str, Any]:
    parent_id = str(fields.get("parent_id", ""))
    if parent_id:
        return {"status": "merge-if-tied", "parent_id": parent_id, "decision_rule": fields["parent_merge_rule"]}
    return {"status": "not-applicable", "parent_id": "", "decision_rule": bi("若 fresh collision 或 matched simplification 表明只剩已有 Idea 的子组件，先合并而不是新增名称。", "If fresh collision or matched simplification leaves only a component of an existing idea, merge before creating a new name.")}


def method_substance(fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "persistent_update_object": fields["persistent_update_object"],
        "learning_signal": fields["learning_signal"],
        "independent_truth": fields["independent_truth"],
        "matched_simplification": fields["strongest_baseline"],
        "decisive_falsifier": fields["stop"],
    }
