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
  {k:"C",t:"HarmBench + DeepSeek",d:{zh:"让两个独立判分器看完全相同的轨迹，检查‘当前是否安全’‘哪些未来轨迹算问题’以及‘哪个实验组更危险’这三件事是否一致。",en:"Two independent measurements on identical traces."}},
  {k:"D",t:{zh:"新数据前先把‘意见不一致时怎么办’写死",en:"PV1"},d:{zh:"在新结果出现之前，先把任务、两个判分器和‘意见不一致时怎么办’的规则写死，再看新数据到来时协议会不会真的保守停止。",en:"Prospective panel testing fail-closed behavior."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先看一个判分器会得出什么故事",en:"Initial single-evaluator result"},q:{zh:"只看 HarmBench 时，更新后的 Agent 是不是显得更危险？",en:"Is updated riskier?"},found:{zh:"是，三个实验组出现很明显的排序，很容易讲成‘更新越多越危险’。",en:"HarmBench showed a directional ordering."},meaning:{zh:"但这时只能说‘一个判分器看起来是这样’，还不能说这是 Agent 的稳定属性。",en:"Candidate story only."}},
  {k:"B",t:{zh:"把完全相同的轨迹交给第二个判分器",en:"Second evaluator"},q:{zh:"如果换一个独立判分器，‘哪个组更危险’这个方向还在吗？",en:"Does the direction survive another judge?"},found:{zh:"不在：连‘当前是否安全’这个前提和未来三个组的排序都发生变化。",en:"Premise and ordering changed."},meaning:{zh:"所以原来的‘更新更危险’不能再当成稳定结论。",en:"The original risk story was no longer identified."}},
  {k:"C",t:{zh:"两个判分器有分歧时，先只报告还能确定的部分",en:"ERTA"},q:{zh:"两个判分器意见不一致时，是不是只能投票选一个？",en:"What remains identifiable?"},found:{zh:"不是。论文保留‘两个判分器都同意的确定部分’和‘至少一个判分器认为可能有问题的部分’，同时报告效果方向可能落在哪个范围。",en:"Retains sets and contrast envelopes instead of voting."},meaning:{zh:"这样‘我们其实不知道方向’本身也成为一个诚实、可计算的结果。",en:"Uncertainty becomes an explicit result."}},
  {k:"D",t:{zh:"再用一批全新数据验证这套保守规则",en:"PV1"},q:{zh:"这套‘意见不一致就保守停止’的规则，会不会只是看到旧结果后才临时想出来？",en:"Will the protocol fail closed prospectively?"},found:{zh:"在全新的 12 个回合出现结果之前就冻结任务、判分器和判定规则；新数据仍然分歧，协议按预先规则输出‘测量无法确定’。",en:"Fresh disagreement produced the preregistered inconclusive verdict."},meaning:{zh:"说明不是事后为了配合结果才改口径。",en:"Shows the rule was not post-hoc."}}
 ]
};
