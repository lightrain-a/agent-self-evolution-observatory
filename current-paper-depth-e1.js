window.CURRENT_PAPER_DETAILS=window.CURRENT_PAPER_DETAILS||{papers:{}};
Object.assign(window.CURRENT_PAPER_DETAILS.papers["paper-e1"],{
 collection:{label:{zh:"① E1 · STRI",en:"① E1 · STRI"},type:{zh:"正式论文",en:"Formal paper"},status:{zh:"论文就绪 · 扩展 HOLD",en:"Paper ready · extension hold"},method:{zh:"表示不变性证书 R*(A;q)",en:"Representation-invariance certificate R*(A;q)"},model:{zh:"静态精确审计 + AutoSkill P19 + DeepSeek 扩展",en:"Exact static audit + AutoSkill P19 + DeepSeek extension"},data:{zh:"技能 support matrices / AutoSkill / SWE-bench Verified",en:"Skill support matrices / AutoSkill / SWE-bench Verified"},takeaway:{zh:"同样的语义能力，不应因技能包怎么拆而改变控制。",en:"Equivalent semantic capability should not change control merely because packaging changes."}},
 snapshot:[
  {k:{zh:"科学对象",en:"Scientific object"},v:{zh:"技能包表示不变性",en:"Skill-package representation invariance"}},
  {k:{zh:"核心方法",en:"Core method"},v:{zh:"R*(A;q) + semantic quotient",en:"R*(A;q) + semantic quotient"}},
  {k:{zh:"主证据",en:"Primary evidence"},v:{zh:"exact certificate + P19 行为链",en:"Exact certificate + P19 behavior chain"}},
  {k:{zh:"实验模型",en:"Models"},v:{zh:"静态求解 / AutoSkill / DeepSeek",en:"Static solver / AutoSkill / DeepSeek"}},
  {k:{zh:"数据对象",en:"Data"},v:{zh:"support matrix / AutoSkill / SWE-bench",en:"Support matrices / AutoSkill / SWE-bench"}},
  {k:{zh:"当前状态",en:"Current state"},v:{zh:"SUBMISSION_READY；Full-P1 HOLD",en:"SUBMISSION_READY; Full-P1 HOLD"}}
 ],
 contract:[
  {k:{zh:"实验单位",en:"Unit"},v:{zh:"一个 support matrix / 一个冻结行为场景 / 一个 Full-P1 task-arm run",en:"One support matrix, one frozen behavior scene, or one Full-P1 task-arm run"},why:{zh:"理论、行为 witness 与外部扩展分别记账，避免把 run 数量伪装成独立理论样本。",en:"Theory, behavioral witnesses, and the external extension remain separately accounted."}},
  {k:{zh:"处理变量",en:"Treatment"},v:{zh:"只改变 package identity：split / clone / regroup",en:"Change package identity only: split / clone / regroup"},why:{zh:"semantic support、能力内容与任务保持不变，才能识别表示本身。",en:"Semantic support, capability content, and task remain fixed to identify representation itself."}},
  {k:{zh:"关键对照",en:"Controls"},v:{zh:"ID placebo、semantic quotient、matched cleanup、mediator add-back",en:"ID placebo, semantic quotient, matched cleanup, mediator add-back"},why:{zh:"分别排除普通重命名、任意 cleanup 和非特异 mediator 解释。",en:"These rule out ordinary renaming, arbitrary cleanup, and non-specific mediator explanations."}},
  {k:{zh:"主估计量",en:"Estimands"},v:{zh:"R*(A;q)、destructive signature、mediator 恢复率",en:"R*(A;q), destructive signature, mediator restoration"},why:{zh:"一个回答结构可实现性，一个回答真实行为后果。",en:"One identifies structural realizability and the other bounded behavioral consequence."}},
  {k:{zh:"统计与判定",en:"Statistics / decision"},v:{zh:"精确可实现性；Fisher exact；冻结 finite witness",en:"Exact realizability; Fisher exact; frozen finite witness"},why:{zh:"不把小样本 witness 升级成 prevalence 或总体 effect size。",en:"The finite witness is not promoted into prevalence or population effect size."}},
  {k:{zh:"失败规则",en:"Fail-closed rule"},v:{zh:"evaluator invalid、provider quota、support drift 均阻断扩展 inference",en:"Evaluator invalidity, provider quota, or support drift blocks extension inference"},why:{zh:"Full-P1 的 40/40 执行完成不等于科学 PASS。",en:"Full-P1 completing 40/40 runs is not a scientific PASS."}}
 ],
 arms:[
  {name:"Original",kind:{zh:"基准表示",en:"Reference representation"},changes:{zh:"原 package identity",en:"Original package identity"},fixed:{zh:"语义 support / executor / task",en:"Semantic support / executor / task"},purpose:{zh:"给出原控制与行为。",en:"Provides reference control and behavior."}},
  {name:"Split-4",kind:{zh:"表示处理",en:"Representation treatment"},changes:{zh:"同一技能拆成 4 个 package",en:"One skill is split into four packages"},fixed:{zh:"可执行语义能力不变",en:"Executable semantic capability unchanged"},purpose:{zh:"检验 package granularity 是否改变控制。",en:"Tests whether package granularity changes control."}},
  {name:"ID placebo",kind:{zh:"身份安慰剂",en:"Identity placebo"},changes:{zh:"名字/identity 变化但不做语义拆分",en:"Names/identities change without semantic split"},fixed:{zh:"support 与内容",en:"Support and content"},purpose:{zh:"区分一般重命名与真实 split effect。",en:"Separates renaming from the split effect."}},
  {name:"Quotient",kind:{zh:"语义控制",en:"Semantic control"},changes:{zh:"先按 semantic class 聚合再分配",en:"Aggregate by semantic class before allocation"},fixed:{zh:"同一 target / support",en:"Same target and support"},purpose:{zh:"验证表示敏感性是否由 package-first basis 引起。",en:"Tests whether sensitivity comes from the package-first basis."}}
 ],
 analysis:[
  {name:{zh:"结构层",en:"Structural layer"},detail:{zh:"在冻结 support matrix 上计算 R*=1 与 R*>1 的 exact boundary，并用高-overlap但 R*=1 的反例拒绝 overlap heuristic。",en:"Compute the exact R*=1 versus R*>1 boundary and reject overlap heuristics with high-overlap equalizable counterexamples."}},
  {name:{zh:"行为层",en:"Behavior layer"},detail:{zh:"P19 original/split/placebo/quotient 与 mediator add-back / cleanup 形成 bounded representation→retrieval→mediator→behavior 链。",en:"P19 controls plus mediator add-back/cleanup form a bounded representation→retrieval→mediator→behavior chain."}},
  {name:{zh:"扩展层",en:"Extension layer"},detail:{zh:"ReasoningBank Full-P1 必须先满足 evaluator validity 与 provider completeness；当前 paired analysis 为空，不进入论文主张。",en:"ReasoningBank Full-P1 requires evaluator validity and provider completeness; paired analysis is empty and cannot enter the paper claim."}}
 ],
 interpretation:{proves:[{zh:"在 support 固定时，package identity 可能改变 package-first control。",en:"Package identity can change package-first control under fixed support."},{zh:"R*(A;q) 给出该表示不变量的精确可实现性边界。",en:"R*(A;q) gives an exact realizability boundary."},{zh:"一个冻结 AutoSkill 场景把表示差异连接到检索与执行行为。",en:"One frozen AutoSkill scene connects representation differences to retrieval and behavior."}],doesNot:[{zh:"不证明所有 skill system 都会发生该问题。",en:"It does not show every skill system has the problem."},{zh:"不证明 STRI 一定提升 task utility 或一般安全。",en:"It does not establish general task utility or safety improvement."},{zh:"不把 Full-P1 40/40 执行写成扩展科学结果。",en:"It does not treat 40/40 Full-P1 execution as a scientific result."}],importance:{zh:"它把“技能怎么拆”从工程习惯提升成一个可审计的 systems invariant，并给出何时可满足的精确边界。",en:"It turns skill packaging into an auditable systems invariant with an exact boundary."}},
 lineage:[
  {stage:"A",title:{zh:"为什么不是 Skill-SP 的简单复现",en:"Why this is not a Skill-SP replication"},body:{zh:"Skill-SP 等工作关注结构化技能如何帮助生成或训练；E1 固定语义 support，只问等价 package reparameterization 是否改变控制。",en:"Skill-SP-style work asks whether structured skills help; E1 fixes semantic support and asks whether equivalent package reparameterization changes control."}},
  {stage:"B",title:{zh:"为什么不把所有数学工具都写成贡献",en:"Why the mathematical tools are not all sold as contributions"},body:{zh:"quotient、LP 与 cone machinery 有成熟前置；论文真正的新轴是 systems invariant 与它的 exact audit mapping。",en:"Quotients, LPs, and cone machinery have prior art; the defended novelty is the systems invariant and its exact audit mapping."}},
  {stage:"C",title:{zh:"为什么 Full-P1 不能覆盖 canonical E1",en:"Why Full-P1 cannot overwrite canonical E1"},body:{zh:"Full-P1 是后来增加的外部有效性扩展，使用不同 substrate 和 model。它自己的 gate 失败，只能成为扩展 HOLD；不能倒灌推翻或强化已冻结主张。",en:"Full-P1 is a later external-validity extension on a different substrate/model. Its failed gate cannot weaken or strengthen frozen canonical claims."}}
 ],
 replayNotes:[{zh:"复盘时先区分 canonical E1 与 ReasoningBank 扩展。",en:"Separate canonical E1 from the ReasoningBank extension."},{zh:"所有“行为影响”措辞都保留 P19 bounded-substrate 限定。",en:"Every behavioral-impact statement retains the bounded P19 qualifier."}]
});
