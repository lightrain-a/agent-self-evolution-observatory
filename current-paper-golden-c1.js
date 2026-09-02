window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-c1"]={
 scenario:{title:{zh:"为什么真实 memory Agent 一定要区分‘写进去了’和‘真正影响了行为’？",en:"Why must memory agents separate writing from behavioral use?"},lead:{zh:"长期记忆系统通常至少包含写入、检索、采用、行动和最终结果几个阶段。每一层都可能过滤或改写上游信息，所以‘memory 变了’天然不等于‘行为变了’。",en:"Long-term memory passes through writing, retrieval, uptake, action, and outcome."},reasons:[
  {t:{zh:"写入和使用是两个模块",en:"Writing and use are separate"},d:{zh:"writer 可以生成很不同的 memory，但未来 policy 完全可能不检索或不采纳。",en:"Different memories may never be retrieved or used."}},
  {t:{zh:"检索层会做筛选",en:"Retrieval filters state"},d:{zh:"长期库很大时，真正暴露给 policy 的只是一小部分。",en:"Only a small subset of memory reaches the policy."}},
  {t:{zh:"看到不等于采用",en:"Exposure is not uptake"},d:{zh:"memory 出现在 context 里，第一步动作仍可能保持不变。",en:"Visible memory need not alter the action."}},
  {t:{zh:"最终任务还有环境反馈",en:"Outcomes add another filter"},d:{zh:"即使第一步改变，后续环境和纠错也可能把差异重新吸收。",en:"Later interaction can absorb an early difference."}}
 ],why:{zh:"如果不分阶段，forced injection 的强效果很容易被写成真实部署效果，或者把‘写得不同’误写成‘长期行为已经改变’。C1 的价值就在于把这条链拆开。",en:"Stage separation prevents forced leverage from being mistaken for native end-to-end effect."}},
 worked:{title:{zh:"一个具体购物例子：记忆明明写得不同，为什么后面可能还是做出一样的选择？",en:"Worked example: different written memories can still lead to the same future choice"},lead:{zh:"教学示例，不是 C1 的逐字样本。假设 Agent 上一次买耳机时，浏览、比较价格、下单的全过程完全相同；实验只改变系统最后怎样总结这次经历。",en:"Teaching example using one shopping trace."},steps:[
  {k:"01",t:{zh:"第一次购物经历完全一样",en:"Same shopping experience"},d:{zh:"两边都看了同样商品、比较了同样价格，也做了同样的下单操作。",en:"Identical source interaction."}},
  {k:"02",t:{zh:"只改变‘怎么总结这次经历’",en:"Change only the reflection"},d:{zh:"一边按‘成功经验’总结，一边按‘失败经验’总结，于是写进长期记忆的内容明显不同。",en:"Different reflection branches produce different durable memory."}},
  {k:"03",t:{zh:"下一次买显示器时，让系统自己决定要不要取这段记忆",en:"Let the real system decide whether to retrieve it"},d:{zh:"不是实验者把记忆硬塞给 Agent；只有系统真实流程把它检索出来，才算真正进入后续决策。",en:"The system chooses whether to retrieve it."}},
  {k:"04",t:{zh:"连续问三道门",en:"Check three gates"},d:{zh:"这段记忆取出来了吗？第一步选择因此变了吗？最后购买结果真的变了吗？",en:"Record retrieval, first action, and terminal outcome."}}
 ],compare:[
  {a:{zh:"第一道事实：记忆写得不同",en:"Written state"},b:"20/20",d:{zh:"20 组对照里，两份长期记忆都稳定写出了差异。",en:"The durable state diverges."}},
  {a:{zh:"第二道事实：差异有没有一路传到底",en:"Real deployment"},b:"125/172 → .069 → .021",d:{zh:"172 次机会里有 125 次真的检索到了记忆，但第一步动作差异已经很小，到了最终任务结果只剩更小的差异。",en:"Retrieval is frequent while downstream transport is weak."}}
 ],note:{zh:"所以 C1 不是在问‘记忆有没有变’，而是在问：写入的差异经过真实系统后，究竟在哪一步开始不再影响行为。",en:"Large state divergence need not imply large behavioral transport."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"Agent 记住过去经验后，会在多大程度上遵循、误用或被负面经验带偏？",en:"How strongly do agents follow, misuse, or propagate stored experience?"},added:{zh:"这项 ACL 2026 工作把 memory management 与 experience-following behavior 直接联系起来，系统研究 misleading / negative memory 对后续行为的影响。",en:"ACL 2026 directly studies memory management and experience-following behavior."},method:{zh:"它更关心不同 memory 内容和管理策略造成什么行为后果。",en:"It studies behavioral consequences of memory content and management."},bridge:{zh:"C1 再往下拆一层：即使 writer 已经写出不同 durable state，差异到底是在检索、第一步动作还是最终结果那里消失？也就是说，C1 研究的是 transport，而不只是 memory quality。",en:"C1 localizes where a written difference attenuates along the transport path."}},
 architecture:{lead:{zh:"这四块不是四个并列数据集，而是四个不同用途：先在购物任务里看完整传递链，再用一个强制记忆对照确认‘记忆本身有能力影响决策’，然后换到论坛任务复现，最后才是后来的外部扩展。",en:"C1 separates core domain, capacity control, replication, and extension."},layers:[
  {k:"A",t:"Shopping",d:{zh:"主实验：同一段经验从‘写进长期记忆’开始，一路检查有没有被检索、有没有改变第一步、有没有改变最后结果。",en:"Core stage-resolved experiment."}},
  {k:"B",t:{zh:"强制把记忆送到决策模块",en:"Forced fixed-evidence"},d:{zh:"这里只回答一个更简单的问题：如果保证 Agent 一定看见这段记忆，它本身有没有能力改变决策。这个结果不能冒充真实部署效果。",en:"Capacity control with exposure fixed to one."}},
  {k:"C",t:"Reddit",d:{zh:"把同样的检查换到论坛任务，看看‘写得不同但不一定传到底’是不是只发生在购物场景。",en:"Cross-domain replication."}},
  {k:"D",t:"PACTA / ReasoningBank",d:{zh:"后来增加的外部扩展；只有来源文件和执行记录完全闭合后，才允许它产生新的论文结论。",en:"Later extension held behind provenance gates."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先确认：两份长期记忆真的写得不同吗？",en:"Write-stage pilot"},q:{zh:"同一段购物经历，只改变最后的总结方式，能不能稳定写出两份不同记忆？",en:"Does writer branch create durable divergence?"},found:{zh:"20/20 组对照都写出了差异。",en:"20/20 pairs diverged."},meaning:{zh:"先证明实验真的改变了长期记忆，而不是只改了一个标签。",en:"The treatment changes persistent state."}},
  {k:"B",t:{zh:"再排除：是不是只是换了几句话？",en:"Wording control"},q:{zh:"如果在同一种总结方式里也大幅改写措辞，差异会不会同样大？",en:"Is this ordinary wording sensitivity?"},found:{zh:"普通措辞变化解释不了前面的分叉强度。",en:"A stronger same-mode paraphrase does not absorb the branch effect."},meaning:{zh:"说明差异不只是提示词换词造成的。",en:"Rules out the simplest wording account."}},
  {k:"C",t:{zh:"强制给它看：这段记忆本身有没有影响力？",en:"Forced-capacity control"},q:{zh:"如果我们保证 Agent 一定看到这段记忆，它会不会改变决策？",en:"Does the memory have downstream leverage when exposed?"},found:{zh:"会，强制提供时影响明显。",en:"Forced exposure shows leverage."},meaning:{zh:"这只证明‘记忆有能力影响’，还没有证明系统真实流程会自然用到它。",en:"Shows capacity, not native transport."}},
  {k:"D",t:{zh:"最后回到真实系统：差异到底传到哪一步？",en:"Native transport"},q:{zh:"让系统自己检索时，记忆差异会不会一路传到第一步动作和最终任务结果？",en:"Does the real pipeline transport it?"},found:{zh:"记忆经常被检索出来，但第一步动作和最终结果的稳定差异都很弱。",en:"Retrieval is frequent; stable downstream effects are weak."},meaning:{zh:"目前最清楚的边界是：系统常常‘看见’了不同记忆，但没有稳定地把差异变成下一步决策。",en:"Localizes the attenuation boundary."}}
 ]
};
