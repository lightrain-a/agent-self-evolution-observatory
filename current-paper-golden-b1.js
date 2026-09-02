window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-b1"]={
 scenario:{title:{zh:"为什么真实 memory 系统会关心‘这段记忆来自成功还是失败’？",en:"Why does memory provenance matter in real systems?"},lead:{zh:"长期记忆不只存内容，还常携带来源、置信度、成功/失败标签、时间等 metadata。系统可能据此决定是否复用、验证、降权或隔离一段经验，因此 provenance 天然可能进入控制链。",en:"Long-term memories often carry source/outcome metadata used for trust and reuse decisions."},reasons:[
  {t:{zh:"系统需要判断记忆可信度",en:"Systems need trust signals"},d:{zh:"来自失败的经验可能需要更多验证，但也可能包含最有价值的纠错信息。",en:"Failure-derived experience may require verification yet contain valuable diagnostics."}},
  {t:{zh:"治理层会读取 metadata",en:"Governance reads metadata"},d:{zh:"reuse / verify / escalate / abstain 等策略可能直接依赖来源身份。",en:"Reuse/verification policies can consume provenance metadata."}},
  {t:{zh:"来源和内容很容易纠缠",en:"Source and content are entangled"},d:{zh:"失败写入模块往往写得更谨慎、更强调 verification，所以看到行为差异不一定是 provenance 本身。",en:"Failure writers often change wording and strategy too."}},
  {t:{zh:"任务难度又是第三个混杂",en:"Task difficulty is another confound"},d:{zh:"更难任务更容易失败，也更容易在未来失败，强 association 可能完全由难度制造。",en:"Hard tasks can create spurious provenance associations."}}
 ],why:{zh:"如果不把这些通道拆开，系统很容易得出‘failure memory 有毒’或‘failure memory 更好’这种过早结论，并把错误规则写进 memory governance。B1 的目标是先把什么证据有资格支持什么因果说清楚。",en:"B1 prevents governance rules from being built on confounded provenance associations."}},
 worked:{title:{zh:"把两张记忆卡放在一起看：内容完全一样，只换‘来自成功/失败’标签",en:"Worked example: identical actionable memory, different provenance label"},lead:{zh:"教学示例，不是已经执行的 L2 数据。想象未来任务里 Agent 看到下面两张记忆卡；真正会影响操作的那句话完全一样。",en:"Teaching example; current L2 did not execute due to insufficient support."},steps:[
  {k:"01",t:{zh:"未来任务保持完全一样",en:"Fix future task"},d:{zh:"两边都让 Agent 完成同一个网页任务，页面状态、工具和用户目标都不变。",en:"Same future task."}},
  {k:"02",t:{zh:"记忆里的可操作建议也完全一样",en:"Fix actionable bytes"},d:{zh:"两边都只写：‘提交前复核关键字段。’这句真正可能影响操作的内容逐字相同。",en:"Both sides see identical actionable advice."}},
  {k:"03",t:{zh:"唯一差别是卡片上方的来源标签",en:"Change metadata only"},d:{zh:"记忆 A 写‘来自成功任务’，记忆 B 写‘来自失败任务’；除此之外不改任何内容。",en:"Only the success/failure provenance label changes."}},
  {k:"04",t:{zh:"再看 Agent 会不会因此区别对待",en:"Measure behavior"},d:{zh:"只有系统真的能看见这个来源标签，而且两边行为仍不同，才有资格说‘来源身份本身’可能有独立作用。",en:"A causal provenance effect requires a visible metadata channel."}}
 ],compare:[
  {a:{zh:"较弱的旧对照（L1）",en:"L1"},b:{zh:"记忆内容也跟着变了",en:"Writer-mode bundle"},d:{zh:"失败总结往往更谨慎、更强调检查，因此行为差异可能来自内容/语气，而不是‘来自失败’这个标签。",en:"Content/style still differ."}},
  {a:{zh:"真正想要的干净对照（L2）",en:"L2"},b:{zh:"只改来源标签，记忆正文逐字相同",en:"Byte-identical + metadata-only"},d:{zh:"目标需要 10 个这样干净的独立任务，目前只找到 5 个，所以模型调用是 0。",en:"The cleanest treatment is support-stopped at 5/10, zero calls."}}
 ],note:{zh:"最重要的一句话：5/10、0 calls 不是‘没有影响’，而是‘实验条件还不够干净，所以我们拒绝下结论’。",en:"Without L2, provenance causal sign remains unresolved."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"不同质量、误导或负面 memory 会怎样改变 Agent 的 experience-following 和错误传播？",en:"How do misleading or negative memories affect experience-following and error propagation?"},added:{zh:"ACL 2026 已经直接说明 memory 内容/价值会改变后续行为，因此‘坏 memory 会害 Agent’本身不是 B1 可以独占的新题。",en:"ACL 2026 directly shows memory content/value can change behavior."},method:{zh:"这类工作改变的是 memory 内容或管理方式。",en:"Such work varies memory content/management."},bridge:{zh:"B1 更苛刻：当 actionable content 已经匹配到完全一样时，仅仅‘这段 memory 来自失败’这个来源标签还有没有独立因果作用？当前证据还不足，所以 sign 必须 unresolved。",en:"B1 asks whether provenance metadata alone matters after content is identical."}},
 architecture:{lead:{zh:"L0–L3 不是四个可以混在一起平均的实验，而是四级‘证据可信度’：越往后，越接近真正只测试来源标签本身。",en:"B1's L0–L3 are identification rungs, not interchangeable experiments."},layers:[
  {k:"L0",t:{zh:"第 1 层：先看现象",en:"AgentDojo / ReasoningBank aggregate"},d:{zh:"公开数据里‘来自失败的记忆’确实更常和未来错误一起出现；但这只能提出问题，因为难任务本来就更容易前后都失败。",en:"Observational association only."}},
  {k:"L1",t:{zh:"第 2 层：把未来任务固定住",en:"WebArena writer-mode bridge"},d:{zh:"比观察关联更严格，但成功/失败两种总结方式仍会改变记忆的措辞和策略，所以还不能说差异只来自来源身份。",en:"Controlled future state, but writer content still differs."}},
  {k:"L2",t:{zh:"第 3 层：记忆正文逐字相同，只换来源标签",en:"Frozen 10-task metadata-only panel"},d:{zh:"这才是最干净的直接实验；目标 10 个独立任务，目前只有 5 个满足条件，因此在调用模型前就停止。",en:"True metadata-only treatment; support-stopped."}},
  {k:"L3",t:{zh:"第 4 层：再验证真实系统里这个来源标签真的一路被传给决策模块",en:"Source-faithful transport"},d:{zh:"未来还要证明来源信息在真实运行链里没有被丢掉，否则即使标签存在，也不可能影响 Agent。",en:"Future source-faithful transport rung."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先看公开数据里的现象",en:"L0"},q:{zh:"‘来自失败的记忆’是不是更常和未来错误一起出现？",en:"Is failure provenance associated with future error?"},found:{zh:"是，公开汇总里是 .931 vs .647。",en:"Strong aggregate association."},meaning:{zh:"这只能告诉我们‘值得研究’，还不能说明失败来源本身造成了错误。",en:"Motivation, not causality."}},
  {k:"B",t:{zh:"把未来任务固定住再比较",en:"L1"},q:{zh:"控制了一部分因素后，成功来源和失败来源会不会稳定指向同一个方向？",en:"Is the sign stable under a controlled bridge?"},found:{zh:"不会：最终结果是 +.1667，但前几步动作是 −.0942，两个方向相反，而且统计门都没过。",en:"Two endpoints point in opposite directions."},meaning:{zh:"不能挑一个自己喜欢的数字宣布‘失败记忆更好/更坏’。",en:"No directional upgrade."}},
  {k:"C",t:{zh:"检查两份记忆到底是不是‘同样内容’",en:"Stronger equivalence audit"},q:{zh:"旧对照里，除了来源身份，措辞和策略是不是也一起变了？",en:"Are L1 memories truly equivalent?"},found:{zh:"是，仍然能看到写作风格和策略差异。",en:"Residual style/strategy differences remain."},meaning:{zh:"所以旧实验最多说明‘两种写入方式整体不同’，不能归因给来源标签。",en:"L1 remains a writer bundle."}},
  {k:"D",t:{zh:"尝试最干净的‘只换来源标签’实验",en:"L2 support gate"},q:{zh:"能不能找到足够多‘记忆正文完全相同，只换成功/失败标签’的任务？",en:"Can the clean L2 treatment execute?"},found:{zh:"目标是 10 个，只找到 5 个满足严格条件，所以 0 次模型调用。",en:"5/10 eligible; zero calls."},meaning:{zh:"正确结论是‘目前无法判断’，而不是‘没有影响’或‘有害’。",en:"Correct verdict: unresolved."}}
 ]
};
