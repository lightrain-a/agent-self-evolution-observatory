window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-g1"]={
 scenario:{title:{zh:"为什么真实的长期 Agent 一定会遇到‘今天安全、以后还安全吗？’这个问题？",en:"Why do persistent agents naturally create a temporal-safety problem?"},lead:{zh:"只要 Agent 会跨任务保存记忆、工作流或长期状态，它就不再是每次从零开始的静态模型。安全评估因此必须同时面对‘状态会继续变化’和‘谁来判定安全’。",en:"Persistent agents carry state across tasks, so safety evaluation must handle changing state and measurement."},reasons:[
  {t:{zh:"状态会继续积累",en:"State keeps changing"},d:{zh:"memory / workflow 会随着任务继续写入，今天检查的快照并不是明天执行时的状态。",en:"Memory/workflow keeps changing after today's evaluation."}},
  {t:{zh:"自动评价器不可避免",en:"Automated evaluation is unavoidable"},d:{zh:"长轨迹数量很大，研究里通常需要自动 judge 批量标记风险事件；这让 evaluator 本身成为测量系统的一部分。",en:"Long trajectories require scalable automated judges."}},
  {t:{zh:"安全结论会影响是否继续部署",en:"Safety decisions gate deployment"},d:{zh:"一个 PASS 往往被理解成‘可以继续使用’，所以必须知道这个结论能不能跨未来状态、跨评价器保持。",en:"A PASS often authorizes continued use, so stability matters."}},
  {t:{zh:"换 judge 翻方向意味着测量不稳",en:"Judge reversal means instability"},d:{zh:"同一轨迹若在不同独立评价器下得到相反排序，问题就不再只是 Agent 本身，而是结论是否被测量方式决定。",en:"Opposite rankings on identical trajectories expose measurement instability."}}
 ],why:{zh:"现实系统最终需要做的是‘是否允许继续运行/更新’的决策，而不是只得到一个离线安全分数。G1 研究的就是这个决策依据是否稳定。",en:"The real decision is whether deployment/update should continue, not merely an offline score."}},
 worked:{title:{zh:"一个具体例子：同一条浏览器轨迹，两个评价器为什么会给出不同结论？",en:"Worked example: one browser trajectory, two conclusions"},lead:{zh:"教学示例，不是 G1 的逐字实验轨迹。动作本身固定，我们只换评价器。",en:"Teaching example, not a verbatim G1 trajectory."},steps:[
  {k:"01",t:{zh:"固定 Agent 状态",en:"Freeze state"},d:{zh:"同一个 memory / workflow snapshot。",en:"Same persistent snapshot."}},
  {k:"02",t:{zh:"固定任务与动作",en:"Freeze task and actions"},d:{zh:"Agent 已经产生完全相同的浏览器行动轨迹。",en:"Exactly the same browser trajectory."}},
  {k:"03",t:{zh:"只换判分器",en:"Change evaluator only"},d:{zh:"HarmBench 与独立 DeepSeek 分别判断是否触发目标安全事件。",en:"Two frozen evaluators label the same trace."}},
  {k:"04",t:{zh:"看事件集合和排序是否翻转",en:"Check reversal"},d:{zh:"如果方向改变，就不能把单一评价器结果写成系统固有属性。",en:"A reversal blocks an intrinsic-system claim."}}
 ],compare:[
  {a:{zh:"评价器 A",en:"Evaluator A"},b:"updated > base > NullMemory",d:{zh:"看起来像‘更新越多越危险’。",en:"Looks like update-associated risk."}},
  {a:{zh:"评价器 B",en:"Evaluator B"},b:"NullMemory > updated ≈ base",d:{zh:"同一批轨迹却给出另一种方向。",en:"The same trajectories produce another ordering."}}
 ],note:{zh:"真正问题因此从‘哪个实验组更危险’变成‘这个方向有没有跨独立评价器被识别出来’。",en:"The question becomes whether the direction is identified across evaluators."}},
 spotlight:{title:"SafeAgent: Safeguarding LLM Agents via an Automated Risk Simulator",problem:{zh:"多轮、工具增强 Agent 的危险行为很难靠静态拒答测试覆盖，需要在可执行环境里主动暴露风险。",en:"Tool-using agents need executable risk scenarios rather than static refusal tests."},added:{zh:"SafeAgent 把自动 risk simulator 接进 Agent 安全流程，用模拟风险场景帮助发现并降低工具调用中的风险。",en:"SafeAgent adds an automated risk simulator to the safety loop."},method:{zh:"它的核心是‘怎样构造风险、怎样让 Agent 更安全’，被测对象和风险评估一起服务于安全改进。",en:"Its focus is risk construction and safety improvement."},bridge:{zh:"G1 不再提出一个新的 guard。它退一步问：即使轨迹已经固定，安全结论本身会不会因为 evaluator 不同而改变？这就是 SafeAgent 没有直接回答的 measurement layer。",en:"G1 audits evaluator stability on fixed trajectories rather than proposing another guard."}},
 architecture:{lead:{zh:"G1 不是把 BrowserART、AWM、HarmBench 当三个平级数据集，而是把它们放在一条‘任务 → 持久状态 → 测量’链上。",en:"G1 uses a task→persistent-state→measurement chain."},layers:[
  {k:"A",t:"BrowserART",d:{zh:"提供真实浏览器 Agent 安全任务与行动轨迹底座。",en:"Browser safety task/trajectory substrate."}},
  {k:"B",t:"Agent Workflow Memory",d:{zh:"提供会跨任务持续更新的 workflow / memory 状态机制。",en:"Persistent workflow/memory mechanism."}},
  {k:"C",t:"HarmBench + DeepSeek",d:{zh:"对同一冻结轨迹做两个独立测量，检查 premise、event set 与 ordering 是否稳定。",en:"Two independent measurements on identical traces."}},
  {k:"D",t:"PV1",d:{zh:"在新结果出现前冻结任务、评价器和 verdict rule，验证协议是否真的会保守停止。",en:"Prospective panel testing fail-closed behavior."}}
 ]},
 arc:[
  {k:"A",t:{zh:"单评价器初始结果",en:"Initial single-evaluator result"},q:{zh:"updated 是否比 base / NullMemory 更危险？",en:"Is updated riskier?"},found:{zh:"HarmBench 给出明显排序，最初很像 update-associated risk。",en:"HarmBench showed a directional ordering."},meaning:{zh:"只能形成候选故事，还不能证明测量稳定。",en:"Candidate story only."}},
  {k:"B",t:{zh:"第二评价器复核",en:"Second evaluator"},q:{zh:"同一批轨迹换 judge 后方向还在吗？",en:"Does the direction survive another judge?"},found:{zh:"current premise 和 future ordering 都发生变化。",en:"Premise and ordering changed."},meaning:{zh:"原‘更新更危险’故事被迫改写。",en:"The original risk story was no longer identified."}},
  {k:"C",t:"ERTA",q:{zh:"有分歧时还能确定什么？",en:"What remains identifiable?"},found:{zh:"保留 definite / possible sets 与 contrast envelope，而不是投票。",en:"Retains sets and contrast envelopes instead of voting."},meaning:{zh:"把不确定本身变成可报告结果。",en:"Uncertainty becomes an explicit result."}},
  {k:"D",t:"PV1",q:{zh:"新数据上协议会不会真的停止过度结论？",en:"Will the protocol fail closed prospectively?"},found:{zh:"fresh panel 仍分歧，冻结规则输出 measurement-inconclusive。",en:"Fresh disagreement produced the preregistered inconclusive verdict."},meaning:{zh:"证明不是事后看到结果才改口径。",en:"Shows the rule was not post-hoc."}}
 ]
};
