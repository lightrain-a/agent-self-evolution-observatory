window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-a"]={
 scenario:{title:{zh:"为什么 memory-enabled Agent 不能只看‘检索到了’或‘动作变了’？",en:"Why are retrieval and action shift insufficient evidence of memory use?"},lead:{zh:"在真实 memory Agent 里，往 context 多放一段文字本身就可能改变模型输出。工程上当然希望 memory 能影响决策，但科学上还必须证明：影响来自正确经验，而不是任意上下文扰动。",en:"Adding context can change actions even when the memory content is not causally relevant."},reasons:[
  {t:{zh:"检索命中只说明看见了",en:"Retrieval means visibility"},d:{zh:"memory 出现在 context，不代表 policy 真正依赖了它。",en:"Visible memory may be ignored."}},
  {t:{zh:"任意文本也可能让动作漂移",en:"Any context can perturb actions"},d:{zh:"wrong memory、placebo 或格式变化都可能造成 action distance。",en:"Wrong memory or placebo text can move actions."}},
  {t:{zh:"机器人动作是连续空间",en:"Robot actions are continuous"},d:{zh:"一个 L2 distance 很容易出现，但不等于方向对任务有帮助。",en:"Action distance need not be task-helpful."}},
  {t:{zh:"闭环成功还有很多中间因素",en:"Closed-loop success has many causes"},d:{zh:"即使最终成功，也不能把全部 credit 自动给某段 memory。",en:"Success alone cannot assign causal credit to memory."}}
 ],why:{zh:"如果没有 Influence × Fidelity 这把尺子，任何 memory-on/off action shift 都可能被包装成‘Agent 学会利用经验’，导致方法比较失真。",en:"A measurement ruler is needed before claiming faithful memory reuse."}},
 worked:{title:{zh:"一个具体例子：机器人动作变了，但到底是不是用了‘正确经验’？",en:"Worked example: action changed, but was the right experience used?"},lead:{zh:"教学示例，不是当前 LIBERO 的逐字 rollout。假设机器人要把红色杯子放进抽屉。",en:"Teaching example for a robot manipulation task."},steps:[
  {k:"01",t:{zh:"固定同一 observation/state",en:"Freeze the same state"},d:{zh:"相机画面、机器人关节状态、目标指令完全相同。",en:"Same visual/robot state and instruction."}},
  {k:"02",t:{zh:"正确 memory",en:"Correct memory"},d:{zh:"过去经验提醒‘先绕开把手，再从杯子侧面抓取’。",en:"Relevant past experience suggests an approach."}},
  {k:"03",t:{zh:"错误 / placebo memory",en:"Wrong / placebo memory"},d:{zh:"长度和格式匹配，但内容无关或方向相反。",en:"Matched format, irrelevant or opposing content."}},
  {k:"04",t:{zh:"同时看方向和后果",en:"Measure direction and consequence"},d:{zh:"不只比较 ||Δa||，还要看正确 memory 是否产生 source-consistent 改变并进入 repair / success。",en:"Measure source-consistent direction and downstream consequence."}}
 ],compare:[
  {a:{zh:"Influence",en:"Influence"},b:"||Δa||₂ ≈ 0.5541",d:{zh:"当前已证明 memory 通道会改变动作。",en:"Memory changes the action."}},
  {a:{zh:"Fidelity",en:"Fidelity"},b:{zh:"wrong / placebo pending",en:"wrong/placebo pending"},d:{zh:"还不能证明动作变化是因为正确经验内容。",en:"Content-faithful reuse is not yet established."}}
 ],note:{zh:"因此 Paper A 不是再造一个 memory module，而是规定‘什么证据才有资格叫真的用了经验’。",en:"Paper A is a measurement paper, not another memory module."}},
 spotlight:{title:"Global Prior Meets Local Consistency: Dual-Memory Augmented VLA (OptimusVLA)",problem:{zh:"VLA 在复杂操控里既需要跨任务的全局经验，也需要当前场景的局部一致性，单一 memory 很难同时覆盖。",en:"VLAs need both global prior experience and local consistency."},added:{zh:"OptimusVLA 用 dual-memory 把全局先验和局部一致性结合起来，是 CVPR 2026 memory-augmented VLA 的直接近邻。",en:"OptimusVLA combines global prior and local consistency through dual memory."},method:{zh:"它关注怎样把 memory 用进控制并提升任务表现。",en:"It focuses on using memory to improve control."},bridge:{zh:"Paper A 不和它竞争‘另一个 memory 架构’，而是问更基础的 measurement question：看到 action shift 时，怎么知道影响真来自正确 memory 内容，而不是 context perturbation？",en:"Paper A audits whether an observed action shift is faithful to the source memory."}},
 architecture:{lead:{zh:"Paper A 的数据/系统关系是‘任务底座 → 扰动 benchmark → memory carrier → 同状态反事实’。",en:"Paper A uses a task→robustness→memory-carrier→counterfactual chain."},layers:[
  {k:"A",t:"LIBERO",d:{zh:"提供语言条件机器人操控任务与官方成功判定。",en:"Base robot manipulation tasks."}},
  {k:"B",t:"LIBERO-Plus",d:{zh:"在相机、机器人状态、噪声、布局等维度加入可控扰动。",en:"Controlled robustness perturbations."}},
  {k:"C",t:"MemoryVLA",d:{zh:"作为 memory-enabled VLA carrier，让同一个 policy 真正接收 memory。",en:"Memory-enabled VLA carrier."}},
  {k:"D",t:"Same-state controls",d:{zh:"同一 state 下比较 off / correct / wrong / placebo，识别 Influence 与 Fidelity。",en:"Same-state memory counterfactuals."}}
 ]},
 arc:[
  {k:"A",t:{zh:"官方复现",en:"Official reproduction"},q:{zh:"底层 MemoryVLA 路线能可靠跑吗？",en:"Is the carrier trustworthy?"},found:{zh:"official task0 reproduction PASS。",en:"Official task0 reproduction passes."},meaning:{zh:"先排除实验底座没接对。",en:"Qualifies the substrate."}},
  {k:"B",t:{zh:"同状态 Influence",en:"Same-state influence"},q:{zh:"memory 真的会改变 policy action 吗？",en:"Does memory change action?"},found:{zh:"||Δa||₂≈0.5541。",en:"||Δa||₂≈0.5541."},meaning:{zh:"证明通道有因果影响力。",en:"Establishes influence."}},
  {k:"C",t:{zh:"Fidelity 对照",en:"Fidelity controls"},q:{zh:"正确 memory 是否比 wrong / placebo 更具方向性？",en:"Is the effect content-specific?"},found:{zh:"仍待完成。",en:"Pending."},meaning:{zh:"没过这一层不能把 action shift 叫 faithful reuse。",en:"No faithful-reuse claim yet."}},
  {k:"D",t:{zh:"闭环 consequence",en:"Closed-loop consequence"},q:{zh:"忠实 influence 能否进入 repair / rejoin / success？",en:"Does faithful influence improve closed-loop behavior?"},found:{zh:"在后续实验门之后。",en:"Future gate."},meaning:{zh:"最终才讨论任务级价值。",en:"Task-level value comes last."}}
 ]
};
