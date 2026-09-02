window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-agent-constraint"]={
 scenario:{title:{zh:"为什么 self-evolving Agent 现实中一定会做‘局部修复’，而局部修复又可能伤到别处？",en:"Why do self-evolving agents make local repairs, and why can they propagate?"},lead:{zh:"遇到一次 failure 后，最便宜、最可回滚的改法往往不是重新训练整个模型，而是写一条 memory / skill / workflow repair。问题是 Agent 的工具和状态彼此共享，‘只针对一个问题写的规则’并不保证只影响一个地方。",en:"Local repairs are cheap and reversible, but shared tools/state can propagate their effects."},reasons:[
  {t:{zh:"局部 patch 成本低",en:"Local patches are cheap"},d:{zh:"相比重训参数，写一条可撤销 procedural note 更适合在线 self-evolution。",en:"Procedural notes are cheaper than retraining."}},
  {t:{zh:"工具共享可变状态",en:"Tools share mutable state"},d:{zh:"File、Gmail、Todo、Note 等 App 可能读写同一个文件、账号或任务对象。",en:"Apps can read/write shared resources."}},
  {t:{zh:"任务有前置依赖",en:"Tasks have prerequisites"},d:{zh:"一个步骤改掉 shared resource，后续本来正常的约束可能因此失效。",en:"Changing a prerequisite can affect later constraints."}},
  {t:{zh:"现有评估常只盯 target",en:"Evaluation often watches only the target"},d:{zh:"target 修好了就算成功，很容易漏掉新产生的 non-target regression。",en:"Target-only evaluation can miss collateral regressions."}}
 ],why:{zh:"自动修复一旦规模化，真正危险的不是某次 repair 无效，而是 repair 在别处制造新 failure。⑧研究的是这种副作用是否由结构耦合决定，而不是简单由 patch 大小决定。",en:"At scale, repair-induced collateral failures become a core reliability problem."}},
 worked:{title:{zh:"一个具体例子：只修‘发邮件附件名错误’，为什么可能破坏另一个正常任务？",en:"Worked example: one file-repair rule, another task regresses"},lead:{zh:"教学示例，不是 F0 outcome。当前 ⑧ 还没有科学结果。",en:"Teaching example; no F0 outcome exists yet."},steps:[
  {k:"01",t:{zh:"目标 failure",en:"Target failure"},d:{zh:"Agent 发报告邮件时附件名经常错误，于是生成局部规则：发送前把当前报告统一重命名为 final.pdf。",en:"A local rule renames the report before emailing."}},
  {k:"02",t:{zh:"target 被修好",en:"Target improves"},d:{zh:"邮件附件现在符合要求。",en:"The email task is repaired."}},
  {k:"03",t:{zh:"共享 File state",en:"Shared file state"},d:{zh:"另一个后续任务需要按原文件名上传同一报告；repair 已经改变共享资源。",en:"Another task depends on the original filename."}},
  {k:"04",t:{zh:"出现 collateral regression",en:"Collateral regression"},d:{zh:"局部规则意图只修邮件，却通过 shared resource 影响到上传任务。",en:"The local repair propagates through the shared resource."}}
 ],compare:[
  {a:"INDEPENDENT",b:{zh:"目标和非目标不共享 mutable resource",en:"Disjoint resources"},d:{zh:"理论上最不容易传播。",en:"Low structural exposure."}},
  {a:"HIGH",b:{zh:"共享 state / API / prerequisite",en:"Shared state/API/prerequisite"},d:{zh:"如果机制成立，non-target regression 应更容易出现。",en:"Mechanism predicts more collateral regression."}}
 ],note:{zh:"真正实验不会为了得到结果事后造图：coupling edge 必须在 outcome 前按 shared state/API/prerequisite 规则冻结。",en:"Coupling edges are frozen outcome-blind before execution."}},
 spotlight:{title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",problem:{zh:"Agent 如何跟随、误用或被错误经验影响，说明 memory update 的副作用已经是实际问题。",en:"Memory can propagate useful and harmful experience."},added:{zh:"ACL 2026 系统研究 memory management 如何改变后续 experience-following，是‘更新会影响未来行为’的直接近邻。",en:"ACL 2026 studies behavioral consequences of memory management."},method:{zh:"它主要按 memory 内容/管理方式分析行为结果。",en:"It focuses on memory content/management effects."},bridge:{zh:"⑧ 不再只问‘更新有没有副作用’，而把同一 repair bytes 放进不同 coupling topology，问副作用是否沿共享状态/依赖结构传播。这个 topology treatment 是新的识别轴。",en:"The new axis is matched structural coupling under identical repair bytes."}},
 architecture:{lead:{zh:"⑧ 的实验关系是‘公开 AppWorld 底座 → 项目匹配 family → coupling treatment → update/no-update replay’。",en:"The experiment is AppWorld→matched families→coupling treatment→replay."},layers:[
  {k:"A",t:"AppWorld",d:{zh:"提供多 App、真实 mutable state 和程序化任务判定。",en:"Multi-app stateful benchmark."}},
  {k:"B",t:"12 matched families",d:{zh:"从公开环境中构造 12 个 target/non-target family，并事先拆 calibration / F0。",en:"Twelve matched target/non-target families."}},
  {k:"C",t:"INDEPENDENT / LOW / HIGH",d:{zh:"同一 update bytes、同约束数和难度，只改变 coupling topology。",en:"Topology-only treatment under matched controls."}},
  {k:"D",t:"No-update vs update replay",d:{zh:"每个 probe 从同 snapshot reset，同时读 target repair 和 non-target regression。",en:"Same-snapshot replay measuring target and collateral effects."}}
 ]},
 arc:[
  {k:"A",t:{zh:"提出 externality hypothesis",en:"Form hypothesis"},q:{zh:"局部 repair 会不会在 non-target 产生新 failure？",en:"Can local repairs create collateral failures?"},found:{zh:"只形成问题，不读 outcome。",en:"Question only; no outcomes."},meaning:{zh:"不把直觉提前写成 finding。",en:"Keeps the mechanism hypothetical."}},
  {k:"B",t:{zh:"构造 12 个 matched families",en:"Build matched families"},q:{zh:"能否只改变 topology，不一起改变难度/约束数？",en:"Can topology be isolated?"},found:{zh:"PRE-F0.5 construct qualification PASS。",en:"Construct qualification passes."},meaning:{zh:"问题已经可公平测试。",en:"Makes the question testable."}},
  {k:"C",t:{zh:"修 treatment 可见性",en:"Repair treatment visibility"},q:{zh:"coupling 是否真的进入 Agent 可见世界，而不是只存在 evaluator metadata？",en:"Is the treatment agent-visible?"},found:{zh:"outcome 前修成 agent-visible matched context。",en:"Fixed before outcomes."},meaning:{zh:"避免伪 treatment。",en:"Avoids a metadata-only pseudo-treatment."}},
  {k:"D",t:"Capability calibration → F0",q:{zh:"基础 Agent 能力够不够，再正式测 externality？",en:"Is the base agent competent before F0?"},found:{zh:"当前必须先过 calibration；机制 outcome 仍不能提前解释。",en:"Calibration precedes any mechanism outcome."},meaning:{zh:"资格化和科学结果严格分离。",en:"Separates qualification from science."}}
 ]
};
