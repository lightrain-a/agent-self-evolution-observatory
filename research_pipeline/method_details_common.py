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
        "split_rule": bi("原任务集与 discovery、更新构造、阈值校准、候选筛选完全不相交，并在更新前冻结。", "Original tasks are disjoint from discovery, update construction, threshold calibration, and candidate selection, and frozen before updates."),
        "paired_measurement": bi("同一原任务实例、同一基础模型和解码设置做 update-before / update-after paired 评测。", "Run update-before/update-after paired evaluation on the same original-task instances, base model, and decoding settings."),
        "independent_truth": bi("优先环境、程序 checker、精确匹配或已有金标；Judge 必须异构且冻结，并带程序化 sanity subset。", "Prefer environment truth, program checkers, exact match, or existing gold; judges must be heterogeneous and frozen with a programmatic sanity subset."),
        "primary_endpoints": bi("同时报告目标收益、最坏原任务回退、回退任务比例和持久更新保留率。", "Report target gain, worst original-task regression, fraction of tasks regressing, and persistent-update retention."),
        "budget_matching": bi("所有对照共享原任务、候选池和执行/调用/token 上限；额外 Probe、Judge、replay 全计预算。", "All controls share original tasks, candidate pool, and execution/call/token caps; extra probes, judges, and replay count against budget."),
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
