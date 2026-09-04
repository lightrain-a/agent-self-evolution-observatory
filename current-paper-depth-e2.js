window.CURRENT_PAPER_DETAILS=window.CURRENT_PAPER_DETAILS||{papers:{}};
Object.assign(window.CURRENT_PAPER_DETAILS.papers["paper-e2"],{
 collection:{
  label:{zh:"④ E2 · State Regeneration",en:"④ E2 · State Regeneration"},
  type:{zh:"正式 E2 谱系 + R17/R5 当前机制扩展",en:"Formal E2 lineage + current R17/R5 mechanism extension"},
  status:{zh:"R5 · M3R4 / Bridge V4-R2 pre-execution PASS",en:"R5 · M3R4 / Bridge V4-R2 pre-execution PASS"},
  method:{zh:"same-evidence regeneration audit + balanced Evidence×Generator bridge",en:"Same-evidence regeneration audit + balanced Evidence×Generator bridge"},
  model:{zh:"DeepSeek-V4-Pro primary；第二 backbone 仅在 Q1 通过后进入 publication transport",en:"DeepSeek-V4-Pro primary; a second backbone is publication transport only after Q1 passes"},
  data:{zh:"V2 48 pairs / 1,728 heldout；M3R4 72 actor units；Bridge 120 fresh tasks",en:"V2 48 pairs / 1,728 heldout; M3R4 72 actor units; Bridge 120 fresh tasks"},
  takeaway:{zh:"当前最强发现是 same evidence 不能稳定再生同一有用 persistent skill；接下来直接把 state generator 当实验变量。",en:"The strongest current finding is that the same evidence does not reliably regenerate the same useful persistent skill; the next test treats the state generator as an experimental variable."}
 },
 snapshot:[
  {k:{zh:"R5 标题",en:"R5 title"},v:{zh:"Same Evidence, Different Skill",en:"Same Evidence, Different Skill"}},
  {k:{zh:"已完成大样本",en:"Completed large study"},v:{zh:"48 pairs / 96 states / 1,728 held-out",en:"48 pairs / 96 states / 1,728 held-out"}},
  {k:{zh:"当前完成结论",en:"Completed claim"},v:{zh:"selected-case state-regeneration instability",en:"Selected-case state-regeneration instability"}},
  {k:{zh:"M2",en:"M2"},v:{zh:"Recovery V3 · 45 inherited + 27 remaining · outcome sealed",en:"Recovery V3 · 45 inherited + 27 remaining · outcome sealed"}},
  {k:{zh:"M3R4",en:"M3R4"},v:{zh:"72 fresh actor units · 0 updater · pre-execution PASS",en:"72 fresh actor units · 0 updater · pre-execution PASS"}},
  {k:{zh:"Bridge V4-R2",en:"Bridge V4-R2"},v:{zh:"120 fresh tasks · balanced 2×2 · pre-execution PASS",en:"120 fresh tasks · balanced 2×2 · pre-execution PASS"}},
  {k:{zh:"当前硬门",en:"Current hard gate"},v:{zh:"fresh DeepSeek model-identity requalification",en:"Fresh DeepSeek model-identity requalification"}},
  {k:{zh:"论文级缺口",en:"Publication gap"},v:{zh:"literature baseline + 2-domain×2-backbone transport",en:"Literature baseline + 2-domain×2-backbone transport"}}
 ],
 contract:[
  {k:{zh:"已完成证据 1",en:"Completed evidence 1"},v:{zh:"V2 rejected-witness effect 小且异质",en:"V2 rejected-witness effect is small and heterogeneous"},why:{zh:"mean +0.0231，CI 跨 0，说明论文不能卖“失败 evidence 普遍更好”。",en:"Mean +0.0231 with a confidence interval crossing zero rules out a universal failure-evidence story."}},
  {k:{zh:"已完成证据 2",en:"Completed evidence 2"},v:{zh:"historical strong state 冻结后仍方向性有效",en:"The historical strong state remains directionally useful when frozen"},why:{zh:"把“这个 state 本身有用”与“updater 能否重新生成它”分开。",en:"Separates state utility from the updater's ability to regenerate it."}},
  {k:{zh:"已完成证据 3",en:"Completed evidence 3"},v:{zh:"byte-identical evidence → 两个不同 fresh states → 历史优势未复现",en:"Byte-identical evidence → two fresh states → historical advantage not reproduced"},why:{zh:"把主要 bottleneck 从 evidence selection 推向 persistent-state materialization。",en:"Moves the main bottleneck from evidence selection toward persistent-state materialization."}},
  {k:{zh:"M3R4",en:"M3R4"},v:{zh:"FF_R1 / FF_R2 × 18 tasks × 2 post-freeze actor replicates",en:"FF_R1 / FF_R2 × 18 tasks × 2 post-freeze actor replicates"},why:{zh:"用 E_REAL=D_X−D_A 区分 same-evidence state separation 与 actor disagreement；历史 outcome 不进新 gate。",en:"Uses E_REAL=D_X−D_A to separate same-evidence state separation from actor disagreement; historical outcomes do not enter the new gate."}},
  {k:{zh:"Bridge Q1",en:"Bridge Q1"},v:{zh:"G_MAIN,A = ½[(W_COMP−W_FREE)+(FF4_COMP−FF4_FREE_A)]",en:"G_MAIN,A = ½[(W_COMP−W_FREE)+(FF4_COMP−FF4_FREE_A)]"},why:{zh:"把 state-generation method 作为 balanced 2×2 的主因子，不再依赖 First-Fail 优越性。",en:"Makes the state-generation method the primary factor in a balanced 2×2 rather than depending on First-Fail superiority."}},
  {k:{zh:"Bridge Q2",en:"Bridge Q2"},v:{zh:"FF4_COMP vs score-only / scope-matched generic",en:"FF4_COMP vs score-only / scope-matched generic"},why:{zh:"只解释 FF4 分支的方法实质，不能拿来解释 Winner 侧的 Q1。",en:"Classifies FF4 method substance only and cannot explain the Winner-side contribution to Q1."}},
  {k:{zh:"Publication gate",en:"Publication gate"},v:{zh:"Q1 先过，再开 literature baseline / public transport",en:"Q1 must pass before literature baselines / public transport open"},why:{zh:"避免用新 benchmark、第二模型或 baseline 去救一个失败的内部 method gate。",en:"Prevents new benchmarks, models, or baselines from rescuing a failed internal method gate."}}
 ],
 arms:[
  {name:"S0 / Initial",kind:{zh:"无新 persistent repair",en:"No new persistent repair"},changes:{zh:"初始 skill 不变",en:"Initial skill unchanged"},fixed:{zh:"actor / task / verifier",en:"Actor / task / verifier"},purpose:{zh:"publication 主表的自然下界。",en:"Natural lower anchor for the publication table."}},
  {name:"Native FREE",kind:{zh:"当前 strongest causal baseline",en:"Current strongest causal baseline"},changes:{zh:"原生 MindMemOS free-form state generation",en:"Native MindMemOS free-form state generation"},fixed:{zh:"对应 evidence bytes / score / actor",en:"Matched evidence bytes / score / actor"},purpose:{zh:"直接回答“compiler 是否优于当前真实 updater”。",en:"Directly tests whether the compiler improves over the deployed native updater."}},
  {name:"Typed Compiler",kind:{zh:"Our generator intervention",en:"Our generator intervention"},changes:{zh:"trajectory+score → typed repair primitives → canonical state",en:"Trajectory+score → typed repair primitives → canonical state"},fixed:{zh:"learner-visible evidence 与 actor",en:"Learner-visible evidence and actor"},purpose:{zh:"减少 free-form state-synthesis degrees of freedom。",en:"Reduces free-form state-synthesis degrees of freedom."}},
  {name:"Generic controls",kind:{zh:"机制 falsifier",en:"Mechanism falsifiers"},changes:{zh:"score-only / diagnosis-cardinality-informed generic state",en:"Score-only / diagnosis-cardinality-informed generic state"},fixed:{zh:"FF4 score pattern / state scope",en:"FF4 score pattern / state scope"},purpose:{zh:"排除 generic workflow hygiene / state sparsity 就足以解释 FF4_COMP。",en:"Tests whether generic workflow hygiene or state sparsity already explains FF4_COMP."}},
  {name:"SkillRevise-style",kind:{zh:"publication MUST baseline（Q1 PASS 后）",en:"Publication MUST baseline (after Q1 PASS)"},changes:{zh:"execution-grounded diagnosis + revision",en:"Execution-grounded diagnosis + revision"},fixed:{zh:"尽可能相同 evidence / task / budget",en:"Match evidence / task / budget where method contract permits"},purpose:{zh:"回答 reviewer 最直接的问题：相比现有 skill-revision method 是否仍有价值。",en:"Answers the reviewer-facing question of value beyond an existing skill-revision method."}},
  {name:"SkillOpt",kind:{zh:"publication SHOULD baseline",en:"Publication SHOULD baseline"},changes:{zh:"validation-gated text-space optimization",en:"Validation-gated text-space optimization"},fixed:{zh:"仅在可公平适配时纳入",en:"Include only if a fair adaptation is clean"},purpose:{zh:"强通用 optimizer 对照，但不能为了数量扭曲 protocol。",en:"A strong generic optimizer baseline, but not at the cost of protocol distortion."}}
 ],
 analysis:[
  {name:{zh:"M3R4 机制定位",en:"M3R4 localization"},detail:{zh:"72 个完全 post-freeze actor observations；E_REAL>0 + exact conditional p≤.05 + 两层 stochastic qualification 才允许 propensity-level selected-case claim。",en:"Uses 72 fully post-freeze actor observations; a propensity-level selected-case claim additionally requires E_REAL>0, exact conditional p≤.05, and both stochastic qualifications."}},
  {name:{zh:"M4 主方法",en:"M4 primary method"},detail:{zh:"SCREEN 和 VALIDATION 使用同一个 G_MAIN,A；FREE_B 永远只做 sensitivity/mechanism，不能替换 primary FREE_A。",en:"SCREEN and VALIDATION use the same G_MAIN,A; FREE_B is sensitivity/mechanism only and never replaces primary FREE_A."}},
  {name:{zh:"State identity",en:"State identity"},detail:{zh:"FREE / COMP / generic 任意 byte-identical skill SHA 都合并为同一 treatment observation，contrast 强制为 0。",en:"Any byte-identical FREE / COMP / generic skill SHA collapses to one treatment observation with exact-zero state contrast."}},
  {name:{zh:"Publication breadth",en:"Publication breadth"},detail:{zh:"内部机制通过后再做约 2 domains × 2 backbones；不是复制 SkillOpt 的 52 cells。",en:"After the internal mechanism passes, target roughly 2 domains × 2 backbones rather than copying SkillOpt's 52-cell breadth."}}
 ],
 interpretation:{
  proves:[
   {zh:"当前完成证据支持：一个 outcome-selected development case 存在 state-regeneration instability。",en:"Completed evidence supports a state-regeneration instability in one outcome-selected development case."},
   {zh:"M3R4 与 Bridge V4-R2 的实验设计已通过独立 GPT-5.6 Sol / Extra High pre-execution review。",en:"M3R4 and Bridge V4-R2 have independently passed GPT-5.6 Sol / Extra High pre-execution design review."},
   {zh:"M3R4 真实 actor path 已 zero-provider 打通到 provider-I/O 边界。",en:"The real M3R4 actor path has been traversed zero-provider up to the provider-I/O boundary."}
  ],
  doesNot:[
   {zh:"不声称 compiler 已经提高 utility；M4 尚未 scientific execution。",en:"No compiler utility claim: M4 has not been scientifically executed."},
   {zh:"不声称 updater variance 是 population-level 主导因素。",en:"No population-level claim that updater variance dominates."},
   {zh:"不声称 First-Fail / rejected failure 普遍更好。",en:"No universal First-Fail or rejected-failure superiority claim."},
   {zh:"不把 pre-execution PASS 当 scientific PASS。",en:"Pre-execution design PASS is not a scientific-result PASS."}
  ],
  importance:{zh:"现在真正的论文对象从“该选哪条失败轨迹”升级成“same evidence 如何被可靠地物化成 persistent state”。这能解释为什么一个有用 state 可以稳定存在，但原生 free-form updater 却不能稳定把它再写出来。",en:"The paper has moved from which failure to select to how the same evidence is reliably materialized into persistent state. This explains how a useful state can remain behaviorally real while the native free-form updater fails to regenerate it reliably."}
 },
 lineage:[
  {stage:"A",title:{zh:"V2：大样本 failure-evidence 故事变弱",en:"V2: the broad failure-evidence story weakens"},body:{zh:"48 pairs 的平均 MRW−WIN-C 只有 +0.0231，且 heterogeneity/CI 不支持“失败 evidence 普遍更好”。",en:"Across 48 pairs, mean MRW−WIN-C is only +0.0231 and heterogeneity/CI do not support a universal failure-evidence benefit."}},
  {stage:"B",title:{zh:"S1：更聪明的 witness selector 也没救起来",en:"S1: a smarter witness selector does not rescue the story"},body:{zh:"Progress-Fail / Progress-Contrast 都只有 14/18，预注册 selector story 停止。",en:"Progress-Fail and Progress-Contrast both reach only 14/18, stopping the preregistered selector story."}},
  {stage:"C",title:{zh:"Frozen state：历史 First-Fail state 本身是真的",en:"Frozen state: the historical First-Fail state is real"},body:{zh:"同一 state bytes 的两次 actor remeasurement 仍方向性优于 WIN-C，说明它不是单次 lucky rollout。",en:"Two frozen-state remeasurements remain directionally above WIN-C, arguing against a one-rollout lucky artifact."}},
  {stage:"D",title:{zh:"Exact evidence replay：问题转到 state generation",en:"Exact evidence replay: the bottleneck moves to state generation"},body:{zh:"byte-identical learner-visible evidence 重新调用 free-form updater，两次 fresh state 都没有稳定复现历史优势。",en:"Re-running the free-form updater on byte-identical learner-visible evidence does not stably reproduce the historical advantage."}},
  {stage:"E",title:{zh:"M3R4：先把 actor noise 从 selected case 里剥出来",en:"M3R4: isolate actor disagreement in the selected case"},body:{zh:"72 个完全 prospective actor observations，不再复用 outcome-consumed A1/B1，并用 exact conditional gate 约束 latent-propensity 解释。",en:"Seventy-two fully prospective actor observations avoid reusing outcome-consumed A1/B1 and constrain any latent-propensity interpretation with an exact conditional gate."}},
  {stage:"F",title:{zh:"Bridge V4-R2：直接操纵完整 state generator",en:"Bridge V4-R2: intervene on the complete state generator"},body:{zh:"balanced Winner/FF4 × FREE/COMP 把 generator main effect 设为主问题；generic controls、realization localization 和 rejected-source moderator 全部正交。",en:"The balanced Winner/FF4 × FREE/COMP design makes the generator main effect primary while generic controls, realization localization, and rejected-source moderation remain orthogonal."}},
  {stage:"G",title:{zh:"Publication plan：停止堆内部实验，补真正强 baseline 与 transport",en:"Publication plan: stop adding internal cells; add decisive baselines and transport"},body:{zh:"内部机制 workload 已足够；若 Q1 PASS，再补 SkillRevise-style strongest baseline、可公平适配的 SkillOpt、一个 diagnosis-vs-renderer ablation，以及约 2-domain×2-backbone transport。",en:"Internal mechanism workload is already sufficient. If Q1 passes, add a SkillRevise-style strongest baseline, SkillOpt where fair, one diagnosis-vs-renderer ablation, and roughly 2-domain×2-backbone transport."}}
 ],
 replayNotes:[
  {zh:"M2 Recovery V3 的 partial outcome 继续封存；页面只能显示 45 inherited complete / 27 remaining 与 quota blocker。",en:"M2 Recovery V3 partial outcomes remain sealed; the page may show only 45 inherited complete / 27 remaining and the quota blocker."},
  {zh:"M3R4 / Bridge 页面只能显示 pre-execution PASS，不得提前显示任何 method effect。",en:"M3R4 / Bridge may show pre-execution PASS only; no method effect may be displayed before execution."},
  {zh:"如果 M4 Q1 失败，不允许用 SkillRevise、SkillOpt、public benchmark、第二 backbone 或 E3 去救。",en:"If M4 Q1 fails, SkillRevise, SkillOpt, public benchmarks, a second backbone, or E3 cannot rescue it."}
 ]
});
