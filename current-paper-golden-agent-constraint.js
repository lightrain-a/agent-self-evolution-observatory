window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-agent-constraint"]={
 scenario:{title:{zh:"为什么 self-evolving Agent 现实中一定会做‘局部修复’，而局部修复又可能伤到别处？",en:"Why do self-evolving agents make local repairs, and why can they propagate?"},lead:{zh:"遇到一次 failure 后，最便宜、最可回滚的改法往往不是重新训练整个模型，而是写一条 memory / skill / workflow repair。问题是 Agent 的工具和状态彼此共享，‘只针对一个问题写的规则’并不保证只影响一个地方。",en:"Local repairs are cheap and reversible, but shared tools/state can propagate their effects."},reasons:[
  {t:{zh:"局部 patch 成本低",en:"Local patches are cheap"},d:{zh:"相比重训参数，写一条可撤销 procedural note 更适合在线 self-evolution。",en:"Procedural notes are cheaper than retraining."}},
  {t:{zh:"工具共享可变状态",en:"Tools share mutable state"},d:{zh:"File、Gmail、Todo、Note 等 App 可能读写同一个文件、账号或任务对象。",en:"Apps can read/write shared resources."}},
  {t:{zh:"任务有前置依赖",en:"Tasks have prerequisites"},d:{zh:"一个步骤改掉 shared resource，后续本来正常的约束可能因此失效。",en:"Changing a prerequisite can affect later constraints."}},
  {t:{zh:"现有评估常只盯 target",en:"Evaluation often watches only the target"},d:{zh:"target 修好了就算成功，很容易漏掉新产生的 non-target regression。",en:"Target-only evaluation can miss collateral regressions."}}
 ],why:{zh:"自动修复一旦规模化，真正危险的不是某次 repair 无效，而是 repair 在别处制造新 failure。⑧研究的是这种副作用是否由结构耦合决定，而不是简单由 patch 大小决定。",en:"At scale, repair-induced collateral failures become a core reliability problem."}},
 worked:{title:{zh:"一个具体例子：只修‘邮件附件名错误’，为什么可能把另一个正常任务一起弄坏？",en:"Worked example: one file-repair rule, another task regresses"},lead:{zh:"教学示例，不是正式机制实验结果。当前 ⑧ 还没有科学结果。假设 Agent 同时负责发邮件和上传报告，这两个任务有时会碰同一个文件。",en:"Teaching example; no F0 outcome exists yet."},steps:[
  {k:"01",t:{zh:"先出现一个局部错误",en:"Target failure"},d:{zh:"Agent 发报告邮件时附件名经常写错，于是系统生成一条很局部的修正规则：发送前把当前报告统一改名为 final.pdf。",en:"A local rule renames the report before emailing."}},
  {k:"02",t:{zh:"邮件任务被修好了",en:"Target improves"},d:{zh:"下一次发邮件时，附件名符合要求。只看这个任务，会觉得修复成功。",en:"The email task is repaired."}},
  {k:"03",t:{zh:"但另一个任务也在用同一个文件",en:"Shared file state"},d:{zh:"后面的上传任务需要原文件名；刚才那条规则已经改掉了这个共享文件。",en:"Another task depends on the original filename."}},
  {k:"04",t:{zh:"于是出现‘修一处、坏一处’",en:"Collateral regression"},d:{zh:"修复的意图只针对邮件，但效果通过共享文件传到了别的任务。",en:"The local repair propagates through the shared resource."}}
 ],compare:[
  {a:{zh:"世界 A · 完全独立（INDEPENDENT）",en:"INDEPENDENT"},b:{zh:"邮件和上传各用各的文件/状态",en:"Disjoint resources"},d:{zh:"修邮件规则没有路径碰到上传任务，理论上最不容易产生连带副作用。",en:"Low structural exposure."}},
  {a:{zh:"世界 B · 少量共享（LOW）",en:"LOW"},b:{zh:"只有一个中间文件或前置步骤共享",en:"Limited sharing"},d:{zh:"修复有一条可能传播的路径，但不是所有任务都绑在一起。",en:"Limited structural exposure."}},
  {a:{zh:"世界 C · 强共享（HIGH）",en:"HIGH"},b:{zh:"多个任务依赖同一文件、状态或前置步骤",en:"Shared state/API/prerequisite"},d:{zh:"如果论文假设成立，同一条局部修复应该更容易在这里连带伤到其它任务。",en:"Mechanism predicts more collateral regression."}}
 ],note:{zh:"论文里的 INDEPENDENT / LOW / HIGH 就是在严格构造这三个世界。最关键的是：这些连接关系必须在看任何结果之前，按‘是否共享文件/状态/前置依赖’冻结，不能看到哪里失败后再事后画图。",en:"Coupling edges are frozen outcome-blind before execution."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"Agent 如何跟随、误用或被错误经验影响，说明 memory update 的副作用已经是实际问题。",en:"Memory can propagate useful and harmful experience."},added:{zh:"ACL 2026 系统研究 memory management 如何改变后续 experience-following，是‘更新会影响未来行为’的直接近邻。",en:"ACL 2026 studies behavioral consequences of memory management."},method:{zh:"它主要按 memory 内容/管理方式分析行为结果。",en:"It focuses on memory content/management effects."},bridge:{zh:"⑧ 不再只问‘更新有没有副作用’，而把同一 repair bytes 放进不同 coupling topology，问副作用是否沿共享状态/依赖结构传播。这个 topology treatment 是新的识别轴。",en:"The new axis is matched structural coupling under identical repair bytes."}},
 architecture:{lead:{zh:"这四层可以理解成：先用 AppWorld 提供真实的多 App 世界，再挑出 12 组能公平比较的任务，只改变‘任务之间共享多少状态/依赖’，最后对每个世界都比较‘不加修复’和‘加同一条修复’。",en:"The experiment is AppWorld→matched families→coupling treatment→replay."},layers:[
  {k:"A",t:"AppWorld",d:{zh:"提供邮件、文件、待办、笔记等会真正读写状态的 App；这里是一切任务发生的公共世界。",en:"Multi-app stateful benchmark."}},
  {k:"B",t:{zh:"12 组严格匹配的任务",en:"12 matched families"},d:{zh:"每一组都有同一个要修的问题和其它正常任务，尽量把任务数量、难度、工具都保持一致。",en:"Twelve matched target/non-target families."}},
  {k:"C",t:{zh:"三个‘共享程度不同的世界’",en:"INDEPENDENT / LOW / HIGH"},d:{zh:"同一条修复、同样任务难度，只改变其它任务和目标任务之间是否共享文件、状态或前置依赖。",en:"Topology-only treatment under matched controls."}},
  {k:"D",t:{zh:"每个世界都做‘不加修复 vs 加修复’",en:"No-update vs update replay"},d:{zh:"从完全相同的初始状态开始：既看目标问题有没有修好，也看其它原本正常的任务有没有被连带弄坏。",en:"Same-snapshot replay measuring target and collateral effects."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先把‘修一处会不会坏一处’变成可检验问题",en:"Form hypothesis"},q:{zh:"同一条局部修复，除了修好目标问题，会不会让其它原本正常任务新出错？",en:"Can local repairs create collateral failures?"},found:{zh:"这一步只提出问题，没有读取任何科学结果。",en:"Question only; no outcomes."},meaning:{zh:"避免把一个直觉先写成已经成立的结论。",en:"Keeps the mechanism hypothetical."}},
  {k:"B",t:{zh:"把三个世界做得真的可公平比较",en:"Build matched families"},q:{zh:"能不能做到只改变‘共享/依赖程度’，其它任务数量、难度和工具都尽量一样？",en:"Can topology be isolated?"},found:{zh:"12 组对照已经通过正式实验前的设计资格检查。",en:"Construct qualification passes."},meaning:{zh:"说明这个问题已经可以被公平地测，但还没有说明哪种世界真的更危险。",en:"Makes the question testable."}},
  {k:"C",t:{zh:"确认 Agent 自己真的能感知这种结构差异",en:"Repair treatment visibility"},q:{zh:"三个世界的差别是否真实存在于 Agent 会读到/操作到的状态里，而不是只写在评测表的备注中？",en:"Is the treatment agent-visible?"},found:{zh:"这个设计问题已经在看结果前修好。",en:"Fixed before outcomes."},meaning:{zh:"保证我们测试的不是‘纸面上有差别、Agent 实际看不见’的假实验。",en:"Avoids a metadata-only pseudo-treatment."}},
  {k:"D",t:{zh:"先确认基础 Agent 会做任务，再启动正式机制实验",en:"Capability calibration → F0"},q:{zh:"如果 Agent 本来就不会这些任务，怎么能判断后面的失败是局部修复造成的？",en:"Is the base agent competent before F0?"},found:{zh:"所以现在必须先做能力检查；正式机制结果仍然是 0。",en:"Calibration precedes any mechanism outcome."},meaning:{zh:"把‘实验能跑’和‘机制已经成立’严格分开。",en:"Separates qualification from science."}}
 ]
};
