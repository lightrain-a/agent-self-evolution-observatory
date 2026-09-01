window.CURRENT_PAPER_DETAILS=window.CURRENT_PAPER_DETAILS||{papers:{}};
Object.assign(window.CURRENT_PAPER_DETAILS.papers["paper-g1"],{
 collection:{label:{zh:"② G1 · 时间安全",en:"② G1 · Temporal Safety"},type:{zh:"正式论文",en:"Formal paper"},status:{zh:"PREBUTTAL · 人类标签缺口",en:"PREBUTTAL · human-label gap"},method:{zh:"ERTA 双评价器时间审计",en:"ERTA dual-evaluator temporal audit"},model:{zh:"Qwen3-8B Agent + HarmBench + DeepSeek",en:"Qwen3-8B agent + HarmBench + DeepSeek"},data:{zh:"BrowserART/AWM · 108 历史 + 12 PV1",en:"BrowserART/AWM · 108 historical + 12 PV1"},takeaway:{zh:"“现在安全”与“未来安全”都可能只是评价器相对结论。",en:"Both current and future safety conclusions can be evaluator-relative."}},
 snapshot:[
  {k:{zh:"科学对象",en:"Scientific object"},v:{zh:"评价器相对的时间安全",en:"Evaluator-relative temporal safety"}},
  {k:{zh:"核心方法",en:"Core method"},v:{zh:"ERTA definite/possible sets + envelope",en:"ERTA definite/possible sets + envelope"}},
  {k:{zh:"Agent 模型",en:"Agent model"},v:{zh:"Qwen3-8B + AWM",en:"Qwen3-8B + AWM"}},
  {k:{zh:"评价器",en:"Evaluators"},v:{zh:"HarmBench / DeepSeek / 待补人类",en:"HarmBench / DeepSeek / pending human"}},
  {k:{zh:"数据对象",en:"Data"},v:{zh:"BrowserART 轨迹与 persistent states",en:"BrowserART trajectories and persistent states"}},
  {k:{zh:"当前状态",en:"Current state"},v:{zh:"READY / PREBUTTAL",en:"READY / PREBUTTAL"}}
 ],
 contract:[
  {k:{zh:"实验单位",en:"Unit"},v:{zh:"同一 frozen trajectory 在不同 evaluator 下的事件标签",en:"The same frozen trajectory labeled by different evaluators"},why:{zh:"trajectory 不变，才能把差异归到 measurement。",en:"Keeping the trajectory fixed isolates measurement differences."}},
  {k:{zh:"时间对象",en:"Temporal object"},v:{zh:"current-pass antecedent + H-step first-event set",en:"Current-pass antecedent + H-step first-event set"},why:{zh:"把“今天通过”写成一个可被未来反驳的有限时间陈述。",en:"Turns a current pass into a finite-horizon statement that future evidence can falsify."}},
  {k:{zh:"三臂",en:"Three arms"},v:{zh:"updated / base / NullMemory",en:"Updated / base / NullMemory"},why:{zh:"区分 update-associated contrast、已有 workflow state 与无持久记忆。",en:"Separates update-associated contrast, existing workflow state, and no persistent memory."}},
  {k:{zh:"评价器规则",en:"Evaluator rule"},v:{zh:"两个 evaluator 独立冻结，不做 majority vote",en:"Evaluators frozen independently; no majority vote"},why:{zh:"不把分歧隐藏成一个伪 ground truth。",en:"Prevents disagreement from being hidden in a pseudo-ground-truth vote."}},
  {k:{zh:"主输出",en:"Primary outputs"},v:{zh:"definite / possible event sets；contrast envelope",en:"Definite/possible event sets; contrast envelope"},why:{zh:"只在所有 admissible evaluator 下方向一致时升级方向性结论。",en:"Directional conclusions are upgraded only when stable across admissible evaluators."}},
  {k:{zh:"失败规则",en:"Fail-closed rule"},v:{zh:"antecedent 或排序不稳定 → evaluator-relative / inconclusive",en:"Unstable antecedent or ordering → evaluator-relative / inconclusive"},why:{zh:"避免挑选对故事最有利的 judge。",en:"Prevents selecting the judge that best supports the story."}}
 ],
 arms:[
  {name:"Updated",kind:{zh:"持久更新臂",en:"Persistent-update arm"},changes:{zh:"使用更新后的 persistent state",en:"Uses the updated persistent state"},fixed:{zh:"future schedule / seeds / horizon",en:"Future schedule / seeds / horizon"},purpose:{zh:"测 update-associated first event。",en:"Measures update-associated first events."}},
  {name:"Base",kind:{zh:"同 schedule 控制",en:"Same-schedule control"},changes:{zh:"回到 step-0/base workflow",en:"Uses step-0/base workflow"},fixed:{zh:"同一未来 tasks 与 runtime",en:"Same future tasks and runtime"},purpose:{zh:"排除 future schedule 本身造成的事件。",en:"Controls for the future schedule itself."}},
  {name:"NullMemory",kind:{zh:"无持久记忆控制",en:"No-persistent-memory control"},changes:{zh:"关闭持久 memory state",en:"Disables persistent memory state"},fixed:{zh:"任务与执行接口",en:"Tasks and execution interface"},purpose:{zh:"区分 base state 与真正 read-disabled boundary。",en:"Separates base state from a read-disabled boundary."}}
 ],
 analysis:[
  {name:{zh:"当前前提审计",en:"Current-premise audit"},detail:{zh:"同一 12 条 current trajectory：HarmBench 0/12，DeepSeek 1/12；current PASS 本身不能作为 evaluator-independent antecedent。",en:"On the same 12 current trajectories, HarmBench is 0/12 and DeepSeek 1/12; the current PASS is not evaluator-independent."}},
  {name:{zh:"未来排序审计",en:"Future-ordering audit"},detail:{zh:"HarmBench updated/base/NullMemory=8/4/0；DeepSeek=5/5/8，方向发生翻转。",en:"HarmBench updated/base/NullMemory=8/4/0 while DeepSeek=5/5/8, reversing the ordering."}},
  {name:{zh:"前瞻验证",en:"Prospective validation"},detail:{zh:"PV1 在新 labels 前冻结 tasks、slots、evaluators 与 verdict rule；0/12 vs 3/12 后按预注册输出 measurement-inconclusive。",en:"PV1 froze tasks, slots, evaluators, and verdict rules before labels and returned measurement-inconclusive after 0/12 versus 3/12."}}
 ],
 interpretation:{proves:[{zh:"同一 persistent Agent 的时间安全结论会随独立评价器变化。",en:"Temporal safety conclusions for the same persistent agent can vary across independent evaluators."},{zh:"ERTA 可以在 outcome 前冻结并在 fresh panel 上真实 fail closed。",en:"ERTA can be frozen before outcomes and genuinely fail closed on a fresh panel."},{zh:"current-pass antecedent 与未来三臂排序都需要 measurement identification。",en:"Both the current-pass antecedent and future ordering require measurement identification."}],doesNot:[{zh:"不证明 HarmBench 或 DeepSeek 谁更接近真值。",en:"It does not establish which evaluator is closer to truth."},{zh:"不证明 updated memory 在总体上更危险或更安全。",en:"It does not establish that updated memory is generally safer or more dangerous."},{zh:"不把 action-attempt label 写成真实 external harmful completion。",en:"It does not equate action-attempt labels with verified external harmful completion."}],importance:{zh:"它把 persistent-agent safety 从“单 judge 打分”变成一个需要显式表示 evaluator uncertainty 的时间测量问题。",en:"It turns persistent-agent safety into a temporal measurement problem with explicit evaluator uncertainty."}},
 lineage:[
  {stage:"A",title:{zh:"为什么旧 r7 故事必须撤回",en:"Why the old r7 story had to be withdrawn"},body:{zh:"旧故事依赖 HarmBench 的 updated>base>NullMemory 排序；第二评价器对同一轨迹给出近乎相反排序。正确动作是撤回 evaluator-independent direction，而不是解释掉第二 evaluator。",en:"The old story relied on one evaluator ordering; a second evaluator reversed it on the same trajectories. The correct response was to withdraw the evaluator-independent direction."}},
  {stage:"B",title:{zh:"为什么不做 majority vote",en:"Why majority vote is not the solution"},body:{zh:"两个 evaluator 的 error model 未知，简单投票只会隐藏 identification uncertainty。ERTA 保留完整 vector，并报告 definite/possible set 与 envelope。",en:"With unknown evaluator error models, voting hides identification uncertainty. ERTA retains the full label vector and reports sets/envelopes."}},
  {stage:"C",title:{zh:"为什么当前最缺 human semantic anchor",en:"Why the current gap is a human semantic anchor"},body:{zh:"继续增加自动 judge 不能解决“所有 judge 都可能共享偏差”。盲化人类语义标签提供独立锚点，但也不能自动扩大 backbone/horizon generalization。",en:"More automated judges cannot rule out shared bias. Blinded human labels add an independent anchor but do not automatically broaden backbone or horizon generalization."}}
 ],
 replayNotes:[{zh:"所有安全率必须标注 evaluator 与 measurement level。",en:"Every safety rate must name the evaluator and measurement level."},{zh:"历史 108 + PV1 12 均无 listener external-effect artifact，不能写 harmful completion rate。",en:"The 108 historical plus 12 PV1 trajectories lack listener external-effect artifacts and cannot be reported as harmful-completion rates."}]
});
