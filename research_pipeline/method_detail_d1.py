from __future__ import annotations

from .method_details_common import bi

DETAIL = {
    "core_intuition": bi(
        "生成模型只负责出题，不能同时判真；进入课程的样本必须被环境 verifier 证明能推翻当前规则，而且删掉任何剩余约束后就不再是有效反例。",
        "The generator proposes tasks but cannot adjudicate truth; a curriculum example must be verifier-confirmed to falsify the current rule and cease to be a valid counterexample if any remaining constraint is removed.",
    ),
    "concrete_example": bi(
        "Agent 归纳出‘条件 A 时总用工具 X’。强模型提出 A 附近带多个条件的任务，环境发现 X 在其中必败；delta debugging 逐项删条件，直到只剩 A + 资源锁定两个必要条件，才把这个 1-minimal 任务送进下一轮更新。",
        "An agent induces 'always use tool X under condition A.' A stronger model proposes boundary tasks; the environment finds one where X fails, then delta debugging removes conditions until only A + resource-locked remain necessary. Only this 1-minimal task enters the next update.",
    ),
    "method_logic": bi(
        "1) 从轨迹抽取可执行规则和参数化任务模板；2) 强模型在固定预算内只提边界候选；3) 环境/程序 verifier 判任务合法且当前规则是否失败；4) 对已验证反例逐约束 delta-debug 到 1-minimal；5) 只有最小反例进入固定 token 的一轮 Prompt/LoRA/skill 更新；6) 基线匹配生成、验证和训练 token；7) 更新冻结后在独立模板/seed 边界集测试。",
        "1) Extract an executable rule and parameterized task template. 2) A stronger model only proposes boundary candidates within a fixed budget. 3) An environment/program verifier judges task validity and rule failure. 4) Delta-debug each verified counterexample to 1-minimality. 5) Only minimal examples enter one fixed-token prompt/LoRA/skill update. 6) Match generation, verification, and training tokens across baselines. 7) Freeze the update and test on independent template/seed boundary sets.",
    ),
    "comparative_advantage": bi(
        "必须证明增益来自最小性，而非更强 teacher 或更多难题；最强对照是同一 verifier 已过滤但不做 delta-minimization 的课程。",
        "The gain must come from minimality, not a stronger teacher or more hard tasks; the strongest control is the same verifier-filtered curriculum without delta minimization.",
    ),
    "strongest_baseline": bi(
        "Verifier-filtered non-minimal：同生成器、同 verifier 调用、同最终训练样本/token 和同更新器，只保留第一个验证反例而不做 delta debugging。",
        "Verifier-filtered non-minimal: same generator, verifier calls, final training examples/tokens, and updater, but keep the first verified counterexample without delta debugging.",
    ),
    "pilot": bi(
        "P0：冻结约 20 条可执行规则，四臂为 1-minimal、verifier-filtered 非最小、随机扰动、失败重放；每臂训练 token 完全相同，只做一轮小更新，在独立模板/seed 且由程序 verifier 判真的边界集评估。",
        "P0: freeze about 20 executable rules and compare four arms: 1-minimal, verifier-filtered non-minimal, random perturbation, and failure replay. Match training tokens exactly, perform one small update, and evaluate on independently templated/seeded boundary sets judged by the program verifier.",
    ),
    "metric": bi(
        "未见边界成功率、规则违反率、每个有效训练样本的 verifier 调用、原任务回退和同 token 泛化增益。",
        "Unseen-boundary success, rule-violation rate, verifier calls per useful training example, original-task regression, and matched-token generalization gain.",
    ),
    "stop": bi(
        "若 proposer 必须参与判真、最小化相对 non-minimal 无增益、或收益只在生成器同分布任务出现，则停止。",
        "Stop if the proposer must adjudicate truth, minimization adds no gain over non-minimal controls, or gains occur only on generator-matched tasks.",
    ),
    "persistent_update_object": bi("verifier 确认的 1-minimal 反例课程及据此产生的一轮冻结更新。", "Verifier-confirmed 1-minimal counterexample curriculum and its resulting one-round frozen update."),
    "learning_signal": bi("程序 verifier 的合法性/规则证伪结果和 delta-deletion 轨迹；生成模型输出不是标签。", "Program-verifier validity/rule-falsification outcomes and delta-deletion traces; generator output is not a label."),
    "independent_truth": bi("环境/程序 verifier 对候选、规则失败和最终边界成功的执行真值。", "Execution truth from an environment/program verifier for candidates, rule failure, and final boundary success."),
    "fresh_reducibility_check": {"review_date":"2026-08-09","sources":[
        {"title":"Counterexample Guided Learning in the Large using Reasoning Agents", "url":"https://arxiv.org/abs/2606.11521"},
        {"title":"DDOR: Delta Debugging for Explainable Overrefusal Testing and Repair", "url":"https://arxiv.org/abs/2606.03601"},
    ]},
}
