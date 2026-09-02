window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-b1"]={
 scenario:{title:{zh:"为什么真实 memory 系统会关心‘这段记忆来自成功还是失败’？",en:"Why does memory provenance matter in real systems?"},lead:{zh:"长期记忆不只存内容，还常携带来源、置信度、成功/失败标签、时间等 metadata。系统可能据此决定是否复用、验证、降权或隔离一段经验，因此 provenance 天然可能进入控制链。",en:"Long-term memories often carry source/outcome metadata used for trust and reuse decisions."},reasons:[
  {t:{zh:"系统需要判断记忆可信度",en:"Systems need trust signals"},d:{zh:"来自失败的经验可能需要更多验证，但也可能包含最有价值的纠错信息。",en:"Failure-derived experience may require verification yet contain valuable diagnostics."}},
  {t:{zh:"治理层会读取 metadata",en:"Governance reads metadata"},d:{zh:"reuse / verify / escalate / abstain 等策略可能直接依赖来源身份。",en:"Reuse/verification policies can consume provenance metadata."}},
  {t:{zh:"来源和内容很容易纠缠",en:"Source and content are entangled"},d:{zh:"失败写入模块往往写得更谨慎、更强调 verification，所以看到行为差异不一定是 provenance 本身。",en:"Failure writers often change wording and strategy too."}},
  {t:{zh:"任务难度又是第三个混杂",en:"Task difficulty is another confound"},d:{zh:"更难任务更容易失败，也更容易在未来失败，强 association 可能完全由难度制造。",en:"Hard tasks can create spurious provenance associations."}}
 ],why:{zh:"如果不把这些通道拆开，系统很容易得出‘failure memory 有毒’或‘failure memory 更好’这种过早结论，并把错误规则写进 memory governance。B1 的目标是先把什么证据有资格支持什么因果说清楚。",en:"B1 prevents governance rules from being built on confounded provenance associations."}},
 worked:{title:{zh:"一个具体例子：两段可操作内容相同，只改‘来自成功/失败’标签，才是真正 provenance-only 问题",en:"Worked example: identical actionable memory, different provenance label"},lead:{zh:"教学示例，不是已经执行的 L2 数据。B1 当前正是因为找不到足够这种干净对象而 STOP。",en:"Teaching example; current L2 did not execute due to insufficient support."},steps:[
  {k:"01",t:{zh:"固定 future task",en:"Fix future task"},d:{zh:"Agent 要完成完全相同的未来网页任务。",en:"Same future task."}},
  {k:"02",t:{zh:"固定 actionable memory bytes",en:"Fix actionable bytes"},d:{zh:"两边都看到同一句可操作建议，例如‘提交前复核关键字段’。",en:"Both sides see identical actionable advice."}},
  {k:"03",t:{zh:"只改 metadata",en:"Change metadata only"},d:{zh:"一边标‘来自成功轨迹’，另一边标‘来自失败轨迹’。",en:"Only the success/failure provenance label changes."}},
  {k:"04",t:{zh:"看行为是否改变",en:"Measure behavior"},d:{zh:"只有 executor / governor 真读取 provenance，才有资格讨论 provenance-only effect。",en:"A causal provenance effect requires a visible metadata channel."}}
 ],compare:[
  {a:"L1",b:{zh:"写入模式 bundle",en:"Writer-mode bundle"},d:{zh:"内容、语气、策略仍一起变化，所以不是干净 provenance-only。",en:"Content/style still differ."}},
  {a:"L2",b:{zh:"byte-identical + metadata-only",en:"Byte-identical + metadata-only"},d:{zh:"这才是最干净 treatment；当前只有 5/10 eligible，0 calls。",en:"The cleanest treatment is support-stopped at 5/10, zero calls."}}
 ],note:{zh:"所以 B1 的关键不是把 L1 做得更大，而是守住‘没有 L2 就不能宣布 provenance causal sign’这条识别边界。",en:"Without L2, provenance causal sign remains unresolved."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"不同质量、误导或负面 memory 会怎样改变 Agent 的 experience-following 和错误传播？",en:"How do misleading or negative memories affect experience-following and error propagation?"},added:{zh:"ACL 2026 已经直接说明 memory 内容/价值会改变后续行为，因此‘坏 memory 会害 Agent’本身不是 B1 可以独占的新题。",en:"ACL 2026 directly shows memory content/value can change behavior."},method:{zh:"这类工作改变的是 memory 内容或管理方式。",en:"Such work varies memory content/management."},bridge:{zh:"B1 更苛刻：当 actionable content 已经匹配到完全一样时，仅仅‘这段 memory 来自失败’这个来源标签还有没有独立因果作用？当前证据还不足，所以 sign 必须 unresolved。",en:"B1 asks whether provenance metadata alone matters after content is identical."}},
 architecture:{lead:{zh:"B1 的 L0–L3 是识别强度阶梯，不是四个可以平均起来的实验。",en:"B1's L0–L3 are identification rungs, not interchangeable experiments."},layers:[
  {k:"L0",t:"AgentDojo / ReasoningBank aggregate",d:{zh:"只看来源与结果的观察关联；能做动机，不能给 causal sign。",en:"Observational association only."}},
  {k:"L1",t:"WebArena 写入模式 bridge",d:{zh:"固定 future state，但 成功/失败写入模块仍会改变 wording / strategy。",en:"Controlled future state, but writer content still differs."}},
  {k:"L2",t:"Frozen 10-task metadata-only panel",d:{zh:"要求 actionable bytes 完全相同，只改 visible provenance；当前 5/10 support，0 calls。",en:"True metadata-only treatment; support-stopped."}},
  {k:"L3",t:"Source-faithful transport",d:{zh:"未来还要恢复真实来源链，验证 provenance 从 source 到 executor 的完整运输。",en:"Future source-faithful transport rung."}}
 ]},
 arc:[
  {k:"A",t:"L0",q:{zh:"failure-derived memory 和未来错误有关联吗？",en:"Is failure provenance associated with future error?"},found:{zh:"公开 aggregate 很强：.931 vs .647。",en:"Strong aggregate association."},meaning:{zh:"只能提出问题，不能证明因果。",en:"Motivation, not causality."}},
  {k:"B",t:"L1",q:{zh:"固定 future state 后方向稳定吗？",en:"Is the sign stable under a controlled bridge?"},found:{zh:"terminal +.1667，early action −.0942，方向相反且都未过 gate。",en:"Two endpoints point in opposite directions."},meaning:{zh:"不能 cherry-pick 一个方向。",en:"No directional upgrade."}},
  {k:"C",t:{zh:"更强等价性审计",en:"Stronger equivalence audit"},q:{zh:"L1 memory 真能看作‘同信息’吗？",en:"Are L1 memories truly equivalent?"},found:{zh:"style / strategy residual 仍存在。",en:"Residual style/strategy differences remain."},meaning:{zh:"L1 必须降格为写入模块 bundle。",en:"L1 remains a writer bundle."}},
  {k:"D",t:"L2 support gate",q:{zh:"真正 metadata-only treatment 能执行吗？",en:"Can the clean L2 treatment execute?"},found:{zh:"只有 5/10 eligible，因此 0 model calls。",en:"5/10 eligible; zero calls."},meaning:{zh:"正确结果是 unresolved，而不是 null / harm。",en:"Correct verdict: unresolved."}}
 ]
};
