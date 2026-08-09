from __future__ import annotations

from .method_details_common import bi

DETAIL = {
    "core_intuition": bi(
        "任务成功只说明目标最后达成，不说明世界已恢复到正常成功轨迹应有的状态；先确认‘成功但有残余状态’真的被正向写入，再学习准入器。",
        "Task success only says the target was eventually achieved, not that the world returned to a normal successful state; first confirm that success-with-residual-state is actually stored positively before learning an admission rule.",
    ),
    "concrete_example": bi(
        "Agent 最终把目标物放进柜子而成功，但绕路时移动了另一物体、打开设备或消耗资源且终点未恢复；success-only 记忆仍可能把这条过程写成好经验并在以后复用副作用。",
        "An agent completes the target placement but moved another object, toggled a device, or consumed a resource during a detour and never restored it; success-only memory may still store the process as good experience and later transfer the side effects.",
    ),
    "method_logic": bi(
        "P0a：1) 选能读精确程序状态的环境；2) 配对同起点的正常成功与扰动后成功轨迹；3) 在重汇合点/终点对对象位置、持有物、开关、资源等算 Δs；4) 审计真实/公开 success-only writer 是否正向写入 success + 非零 Δs；5) 发生率不足立即停。P0b：6) 对被写入经验做未来 matched reuse replay 得到程序化 harm；7) 仅用紧凑 Δs 特征学 residual-effect score 决定 write/summarize/quarantine；8) 与 success-only、endpoint equality、手工 residual threshold 匹配容量/replay 比较。",
        "P0a: 1) use an environment exposing exact program state; 2) pair normal and perturbed successes from the same start; 3) compute Δs over object locations, inventory, toggles, and resources at rejoin/terminal; 4) audit whether real/public success-only writers positively store success + nonzero Δs; 5) stop if incidence is low. P0b: 6) run future matched reuse replay for stored lessons to obtain programmatic harm; 7) learn a residual-effect score from compact Δs features only to choose write/summarize/quarantine; 8) compare with success-only, endpoint equality, and hand residual thresholds at matched capacity/replay.",
    ),
    "comparative_advantage": bi(
        "先验证 failure mode，再学规则；决定性增量是精确 Δs 能否预测未来复用伤害并超过 endpoint equality/手工阈值，不堆抽象 recovery score。",
        "Validate the failure mode before learning a rule; the decisive increment is whether exact Δs predicts future reuse harm beyond endpoint equality/hand thresholds, without stacking an abstract recovery score.",
    ),
    "strongest_baseline": bi(
        "手工 residual threshold：相同 Δs 变量和 replay 真值，只按预注册关键状态差/非零变量数决定 write/quarantine，不学习分数。",
        "Hand-coded residual threshold using the same Δs variables and replay truth, deciding write/quarantine from preregistered key-state differences/counts without a learned score.",
    ),
    "pilot": bi(
        "P0a 只做小规模现象审计：exact-state simulator 中配对同起点正常成功/扰动成功，统计非零 Δs 且被 success-only writer 正向保存的比例；达到预注册发生率才进 P0b，再用 matched future reuse harm 训练并冻结轻量准入器。",
        "P0a is a small phenomenon audit: pair same-start normal/perturbed successes in an exact-state simulator and measure how often nonzero-Δs trajectories are stored positively by a success-only writer. Proceed to P0b only above a preregistered incidence floor, then train/freeze a lightweight admission rule from matched future-reuse harm.",
    ),
    "metric": bi(
        "P0a：success + residual 发生率与正向写入率；P0b：future reuse negative transfer、好经验保留、原任务成功和每次 replay 净收益。",
        "P0a: success + residual incidence and positive-write rate; P0b: future-reuse negative transfer, good-experience retention, original-task success, and net utility per replay.",
    ),
    "stop": bi(
        "若 success + 非零 Δs 的正向写入很少、Δs 不能稳定预测未来 harm，或手工阈值等效，则停止。",
        "Stop if positive storage of success + nonzero Δs is rare, Δs does not stably predict future harm, or the hand threshold is equivalent.",
    ),
    "persistent_update_object": bi("带 residual-state 证据的经验准入状态：write / summarize / quarantine。", "Experience-admission state conditioned on residual-state evidence: write, summarize, or quarantine."),
    "learning_signal": bi("同起点参考轨迹的精确 Δs 与候选经验在未来 matched reuse 中造成的程序化收益/伤害。", "Exact Δs to same-start reference trajectories plus programmatic benefit/harm from future matched reuse."),
    "independent_truth": bi("环境真实状态向量和未来任务 checker；任务 success 或准入分数不能替代状态真值。", "Environment state vectors and future task checkers; task success or admission scores cannot replace state truth."),
    "fresh_reducibility_check": {"review_date":"2026-08-09","sources":[
        {"title":"Dejavu: Towards Experience Feedback Learning for Embodied Intelligence", "url":"https://openaccess.thecvf.com/content/CVPR2026/html/Wu_Dejavu_Towards_Experience_Feedback_Learning_for_Embodied_Intelligence_CVPR_2026_paper.html"},
        {"title":"Trajectory-Informed Memory Generation for Self-Improving Agent Systems", "url":"https://arxiv.org/abs/2603.10600"},
        {"title":"The Compliance Trap: Diagnosing How AI Agents Consume Conflicting Memory", "url":"https://arxiv.org/abs/2607.10608"},
        {"title":"Experience Memory Graph: One-Shot Error Correction for Agents", "url":"https://arxiv.org/abs/2607.13884"},
    ]},
}
