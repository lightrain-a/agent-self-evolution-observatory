window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-c1"]={
 scenario:{title:{zh:"为什么真实 memory Agent 一定要区分‘写进去了’和‘真正影响了行为’？",en:"Why must memory agents separate writing from behavioral use?"},lead:{zh:"长期记忆系统通常至少包含写入、检索、采用、行动和最终结果几个阶段。每一层都可能过滤或改写上游信息，所以‘memory 变了’天然不等于‘行为变了’。",en:"Long-term memory passes through writing, retrieval, uptake, action, and outcome."},reasons:[
  {t:{zh:"写入和使用是两个模块",en:"Writing and use are separate"},d:{zh:"writer 可以生成很不同的 memory，但未来 policy 完全可能不检索或不采纳。",en:"Different memories may never be retrieved or used."}},
  {t:{zh:"检索层会做筛选",en:"Retrieval filters state"},d:{zh:"长期库很大时，真正暴露给 policy 的只是一小部分。",en:"Only a small subset of memory reaches the policy."}},
  {t:{zh:"看到不等于采用",en:"Exposure is not uptake"},d:{zh:"memory 出现在 context 里，第一步动作仍可能保持不变。",en:"Visible memory need not alter the action."}},
  {t:{zh:"最终任务还有环境反馈",en:"Outcomes add another filter"},d:{zh:"即使第一步改变，后续环境和纠错也可能把差异重新吸收。",en:"Later interaction can absorb an early difference."}}
 ],why:{zh:"如果不分阶段，forced injection 的强效果很容易被写成真实部署效果，或者把‘写得不同’误写成‘长期行为已经改变’。C1 的价值就在于把这条链拆开。",en:"Stage separation prevents forced leverage from being mistaken for native end-to-end effect."}},
 worked:{title:{zh:"一个具体例子：两段长期记忆写得不同，但未来动作仍可能一样",en:"Worked example: divergent memories, similar future behavior"},lead:{zh:"教学示例，不是 C1 的逐字样本。假设同一购物轨迹只改变 success / failure reflection。",en:"Teaching example using one shopping trace."},steps:[
  {k:"01",t:{zh:"同一 source trajectory",en:"Same source trajectory"},d:{zh:"浏览、比较、下单过程完全一致。",en:"Identical source interaction."}},
  {k:"02",t:{zh:"只切 reflection branch",en:"Flip reflection branch"},d:{zh:"success writer 与 failure writer 写出不同长期记忆。",en:"Different reflection branches produce different durable memory."}},
  {k:"03",t:{zh:"未来任务原生检索",en:"Native future retrieval"},d:{zh:"系统自己决定是否把这段 memory 取出来，而不是实验者强塞。",en:"The system chooses whether to retrieve it."}},
  {k:"04",t:{zh:"逐层看传递",en:"Track stages"},d:{zh:"分别记录 retrieval hit、第一步动作分布、最终任务结果。",en:"Record retrieval, first action, and terminal outcome."}}
 ],compare:[
  {a:{zh:"写入层",en:"Write stage"},b:"20/20 diverge",d:{zh:"memory 确实稳定分叉。",en:"The durable state diverges."}},
  {a:{zh:"真实行为层",en:"Native behavior"},b:"125/172 → TV=.069 → |Δ|=.021",d:{zh:"经常检索，但动作和最终结果的稳定差异很弱。",en:"Retrieval is frequent while downstream transport is weak."}}
 ],note:{zh:"这就是 C1 的核心直觉：上游 state difference 很大，不代表 downstream behavioral transport 也很大。",en:"Large state divergence need not imply large behavioral transport."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"Agent 记住过去经验后，会在多大程度上遵循、误用或被负面经验带偏？",en:"How strongly do agents follow, misuse, or propagate stored experience?"},added:{zh:"这项 ACL 2026 工作把 memory management 与 experience-following behavior 直接联系起来，系统研究 misleading / negative memory 对后续行为的影响。",en:"ACL 2026 directly studies memory management and experience-following behavior."},method:{zh:"它更关心不同 memory 内容和管理策略造成什么行为后果。",en:"It studies behavioral consequences of memory content and management."},bridge:{zh:"C1 再往下拆一层：即使 writer 已经写出不同 durable state，差异到底是在检索、第一步动作还是最终结果那里消失？也就是说，C1 研究的是 transport，而不只是 memory quality。",en:"C1 localizes where a written difference attenuates along the transport path."}},
 architecture:{lead:{zh:"C1 的实验不是三个平级数据集，而是‘核心任务域 + 能力对照 + 跨域复现 + 外部扩展’。",en:"C1 separates core domain, capacity control, replication, and extension."},layers:[
  {k:"A",t:"Shopping",d:{zh:"核心 stage-resolved 主实验：写入 → 原生检索 → 第一动作 → 最终结果。",en:"Core stage-resolved experiment."}},
  {k:"B",t:"Forced fixed-evidence",d:{zh:"人为把 exposure 设为 1，只回答‘这段 memory 有没有能力影响下游’，不冒充真实 retrieval。",en:"Capacity control with exposure fixed to one."}},
  {k:"C",t:"Reddit",d:{zh:"用另一个任务域检查 write divergence / native transport 是否只在 Shopping 成立。",en:"Cross-domain replication."}},
  {k:"D",t:"PACTA / ReasoningBank",d:{zh:"后来的 fresh-source 扩展；provenance 没闭合前不进入新 inference。",en:"Later extension held behind provenance gates."}}
 ]},
 arc:[
  {k:"A",t:{zh:"写入预实验",en:"Write-stage pilot"},q:{zh:"同一轨迹只切 writer branch，memory 会不会稳定分叉？",en:"Does writer branch create durable divergence?"},found:{zh:"20/20 matched pairs 都发生 divergence。",en:"20/20 pairs diverged."},meaning:{zh:"先证明 treatment 真正改变了长期状态。",en:"The treatment changes persistent state."}},
  {k:"B",t:{zh:"wording 替代解释",en:"Wording control"},q:{zh:"会不会只是 prompt 换词？",en:"Is this ordinary wording sensitivity?"},found:{zh:"same-mode stronger paraphrase 不能吸收 reward-branch difference。",en:"A stronger same-mode paraphrase does not absorb the branch effect."},meaning:{zh:"排除最简单的提示词解释。",en:"Rules out the simplest wording account."}},
  {k:"C",t:{zh:"强制暴露能力实验",en:"Forced-capacity control"},q:{zh:"如果保证 policy 看见 memory，它有没有下游影响力？",en:"Does the memory have downstream leverage when exposed?"},found:{zh:"forced effect 明显。",en:"Forced exposure shows leverage."},meaning:{zh:"证明 capacity，但故意不等同 native transport。",en:"Shows capacity, not native transport."}},
  {k:"D",t:{zh:"原生传输实验",en:"Native transport"},q:{zh:"真实 pipeline 会自然把差异传到行为吗？",en:"Does the real pipeline transport it?"},found:{zh:"retrieval 频繁，但 first-action / terminal effect 很弱。",en:"Retrieval is frequent; stable downstream effects are weak."},meaning:{zh:"把 bottleneck 定位在 exposure 之后、stable uptake 之前。",en:"Localizes the attenuation boundary."}}
 ]
};
