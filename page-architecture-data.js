window.PAGE_ARCHITECTURES = {
  home:{
    chapters:[
      {id:"understand-field",title:{en:"Understand the field",zh:"理解领域"},question:{en:"What counts as self-evolution, how did the field form, and how do mechanism, environment, and evidence interact?",zh:"什么算自进化、这个领域怎样形成，以及更新机制、环境约束和证据标准如何相互作用？"},links:["foundations.html","research-directions.html","mechanisms.html"]},
      {id:"select-research",title:{en:"Understand current research",zh:"理解当前科研"},question:{en:"Where are our current A–G ResearchItems in the field, what is each authoritative decision, how did those decisions change over time, and which workflow produced them?",zh:"我们的 A–G ResearchItem 在领域里处于什么位置、每个对象当前的权威结论是什么、这些结论怎样随时间变化，以及科研系统怎样产生这些状态？"},links:["research-map.html","paper-ideas.html","research-timeline.html","system-overview.html"]},

      {id:"execute-audit",title:{en:"Run, inspect, and submit",zh:"运行、核查与投稿"},question:{en:"Which experiments are still allowed to run, what exact evidence supports the current STRI submission, and how can old projects be inspected without mistaking their archived plans for today's work?",zh:"哪些实验现在仍允许运行、STRI 当前投稿具体由哪些证据支持，以及怎样查看旧项目而不把它们已经归档的计划误当成今天的待办？"},links:["experiments.html","selected-paper.html","bibliography.html"]}
    ]
  },
  foundations:{
    chapters:[
      {id:"boundary",title:{en:"I · Definition and boundary",zh:"第一章 · 定义与边界"},question:{en:"What is the minimum condition for self-evolution, and how is it different from retrying, self-correction, or temporary context adaptation?",zh:"什么条件下才能称为自进化？它与重试、自纠错和临时上下文适应到底有什么区别？"},sourceIds:["foundations"]},
      {id:"taxonomy-evidence",title:{en:"II · Four questions for classifying any system",zh:"第二章 · 用四个问题判断任何系统"},question:{en:"What changes, what feedback drives the change, when is the new state reused, and what gate decides whether the change is kept?",zh:"到底改了什么、什么反馈驱动修改、新状态什么时候再次被使用，以及通过什么门控才决定保留这次修改？"},sourceIds:["taxonomy"]}
    ]
  },
  mechanisms:{
    chapters:[
      {id:"mechanism-axis",title:{en:"I · What does the agent actually change?",zh:"第一章 · Agent 到底改什么？"},question:{en:"Compare parameter, prompt, memory, skill/tool, and workflow updates by persistent artifact, feedback, cost, rollback, and characteristic failure mode.",zh:"把参数、Prompt、Memory、Skill / Tool、Workflow 放到同一套维度里比较：留下什么持久产物、由什么反馈驱动、成本多高、能否回滚、最容易怎样失败？"}},
      {id:"domain-axis",title:{en:"II · What changes when the environment changes?",zh:"第二章 · 换一个场景，哪些条件会变？"},question:{en:"Compare multimodal, GUI/Web, and embodied settings by observability, action space, resetability, failure cost, and transfer assumptions.",zh:"比较多模态、GUI/Web 与具身场景的可观测性、动作空间、可重置性、错误代价和迁移假设，判断同一种机制为什么不能直接跨场景外推。"}},
      {id:"evidence-axis",title:{en:"III · What evidence is enough to call it improvement?",zh:"第三章 · 什么证据才足以叫“改进”？"},question:{en:"Move from current-task score to future gain, regression, persistence, safety, rollback, and reproducibility; use the bibliography for concrete benchmark and repository records.",zh:"从当前任务分数继续检查未来收益、旧能力回退、跨回合持久性、安全、回滚与可复现性；具体 benchmark 和代码仓库统一去文献库检索。"}}
    ]
  },
  "system-overview":{
    chapters:[
      {id:"overview",title:{en:"I · Overall workflow and authority — from research question to experiment to paper",zh:"第一章 · 整体流程与权限：从研究问题到实验，再到论文"},navTitle:{en:"Workflow & authority",zh:"整体流程与权限"},question:{en:"What are the actual steps from new evidence to a research question, a decisive experiment, a paper, and submission—and who is allowed to make each decision?",zh:"从新证据形成研究问题，到设计决定性实验、冻结论文证据并进入投稿，实际依次做哪些事？每一步又是谁有权决定？"}},

      {id:"problem-discovery",title:{en:"II · Decide whether there is a genuinely new scientific problem",zh:"第二章 · 确认是否真的存在新的科学问题"},navTitle:{en:"Confirm a new problem",zh:"确认新问题"},question:{en:"When a paper or experiment shows an unusual result, how do we check whether prior work or a mature explanation already accounts for it before inventing a new method?",zh:"当论文或实验出现异常结果时，怎样先确认它真实存在，并检查已有工作或成熟解释是否已经能说明它？"}},

      {id:"scientific-design",title:{en:"III · Design the scientific contribution before coding",zh:"第三章 · 写代码前先把科学贡献设计完整"},navTitle:{en:"Design the contribution",zh:"设计科学贡献"},question:{en:"Before implementation, can we state the exact new claim, why the mechanism should work, the strongest comparison, the required ablations, and the evidence that would convince a reviewer?",zh:"实现方法之前，能否先写清新贡献、机制假设、最强对照、必要消融，以及最终要用什么证据说服审稿人？"}},

      {id:"experiment-compile",title:{en:"IV · Find the cheapest experiment that can change the decision",zh:"第四章 · 找到最便宜、但足以改变结论的实验"},navTitle:{en:"Compile the smallest test",zh:"编译最小实验"},question:{en:"Before using GPU, have we verified that the dataset/environment can realize the effect, the baseline is strong and equally informed, the truth label is independent, the sample size is enough, and a positive or negative result would actually change what we do next?",zh:"用 GPU 前，是否已经确认数据和环境能产生目标效应、基线公平、真值独立、样本量够用，而且无论结果正负都会改变下一步？"}},

      {id:"validation-scale",title:{en:"V · Run small, identify what failed, then decide whether to scale",zh:"第五章 · 先小规模验证，弄清失败原因，再决定是否扩量"},navTitle:{en:"Validate & scale",zh:"小规模验证与扩量"},question:{en:"If a local test fails, how do we tell whether the cause is broken code, a bad experiment design, an incapable update mechanism, insufficient data, or a false scientific idea—and when is the method stable enough for full experiments?",zh:"局部实验没过时，怎样判断是运行或实验设计出了问题、方法实现不够好、适用范围不对，还是核心科学预测真的被否定？"}},

      {id:"paper-evidence",title:{en:"VI · Freeze the scientific evidence for the paper",zh:"第六章 · 冻结论文科学证据"},navTitle:{en:"Freeze paper evidence",zh:"冻结论文证据"},question:{en:"For each headline claim, is there direct evidence, a strongest baseline, required ablations and analyses, and a reproducible claim-to-evidence binding that is no broader than the data?",zh:"对每条核心主张，是否都有直接证据、最强基线、必要消融与分析，并形成不超出数据范围的“主张—证据”绑定？"}},

      {id:"paper-construction",title:{en:"VII · Choose the strongest story, then build the manuscript",zh:"第七章 · 先选出最佳故事线，再形成成稿"},navTitle:{en:"Story & manuscript",zh:"故事线与成稿"},question:{en:"Within the frozen claim set, which story presents the contribution most clearly, and does the manuscript stay bound to that winning story?",zh:"在冻结的科学主张范围内，哪条故事线最能把贡献讲清楚？成稿是否始终遵守这条故事线和证据边界？"}},

      {id:"review-repair",title:{en:"VIII · Mock review, targeted repair, claim audit, and PDF QA",zh:"第八章 · 模拟审稿、定向修稿与主张审计"},navTitle:{en:"Review & repair",zh:"模拟审稿与修稿"},question:{en:"What would cause rejection when reading the manuscript alone versus checking the underlying artifacts, which issues can be repaired without new science, and does the repaired PDF remain strictly evidence-bound?",zh:"只看论文本身会因什么被拒？再检查代码、数据和证据会发现什么问题？哪些可以在不新增科学结论的前提下修复？"}},

      {id:"submission-closure",title:{en:"IX · Prebuttal, submission authority, and real review",zh:"第九章 · 投稿准备、人工授权与真实审稿"},navTitle:{en:"Submission & review",zh:"投稿与真实审稿"},question:{en:"Are decision-critical objections resolved, all manuscript checks passed, external human submission authority explicit, and real reviewer feedback routed without silently changing scientific truth?",zh:"关键质疑是否已经提前回答、文稿检查是否全部通过、人工投稿授权是否明确，以及真实审稿意见应该如何进入后续修稿或科学重开？"}},

      {id:"system-learning",title:{en:"X · Remember why we continued, stopped, were accepted, or were rejected",zh:"第十章 · 记住为什么继续、停止、被接收或被拒绝"},navTitle:{en:"Learn from outcomes",zh:"复盘与系统学习"},question:{en:"After scientific and submission outcomes, what evidence, failure pattern, reviewer risk, reopen condition, and cheap pre-check should be saved so the next agent learns without rewriting old decisions?",zh:"科研与投稿结束后，应该保存为什么继续或停止、什么新证据值得重开，以及下一次最便宜应该先检查什么？"}}

    ]
  },
  "research-directions":{
    chapters:[
      {id:"orientation",title:{en:"I · Field spine: how self-evolution expanded",zh:"第一章 · 领域主线：自进化对象怎样扩展"},question:{en:"Build one compact historical spine from prompt/model adaptation to persistent memory, skills/tools, workflow evolution, world adaptation, and governance.",zh:"用一条紧凑历史主线看清更新对象怎样从 Prompt / Model 扩展到 Memory、Skill / Tool、Workflow、World 与治理，不在首页式结构中重复三种切面。"}},
      {id:"direction-atlas",title:{en:"II · D1–D10 problem atlas",zh:"第二章 · D1–D10 问题图谱"},question:{en:"Read all ten historical problem directions in one comparison table first, then open a direction only when its boundary, literature, or historical idea lineage is needed.",zh:"先在一张表里横向比较 D1–D10 的问题、通俗解释、典型案例、当前 A–G 落点与代表文献；需要边界或谱系时再展开单个方向。"}},
      {id:"current-bridge",title:{en:"III · From field history to current A–G and open questions",zh:"第三章 · 从领域历史连接到当前 A–G 与开放问题"},question:{en:"Keep the D1–D10 → A–G migration and older open questions visible without treating the historical agenda as today's research queue.",zh:"保留 D1–D10 → A–G 的迁移关系和长期开放问题，但不把历史议程误当成今天的研究待办。"}}
    ]
  },
  "research-map":{
    chapters:[
      {id:"layering",title:{en:"I · Keep field history, the relationship map, and final ResearchItem decisions separate",zh:"第一章 · 分清领域历史、关系图谱和 ResearchItem 最终结论"},question:{en:"Where do we read the field's history, where do we inspect research relationships, and where do final scientific decisions live?",zh:"想看领域怎么发展、研究之间怎么关联、以及每个 Idea 最终为什么继续或停止，分别应该去哪里？"}},
      {id:"coverage-gaps",title:{en:"II · Internal research accumulation and gaps",zh:"第二章 · 哪里内部积累多，哪里当前覆盖少"},question:{en:"Which regions have accumulated more internal research records and which have fewer, without confusing record count with search frequency or priority?",zh:"哪些区域已经积累了较多 ResearchItem、方法和证据记录，哪些区域当前较少，同时避免把记录数量误当成真正搜索次数或优先级？"}},
      {id:"integrated-map",title:{en:"III · Read each A–G research story first, then the formal publication lineage",zh:"第三章 · 先读每个 A–G 研究故事，再看正式发表论文的发展主线"},question:{en:"For each A–G category, where do our work and the public literature now stand, and how does the full formal publication lineage connect these areas over time?",zh:"先逐个看 A–G：这个方向研究什么、我们做到哪里、现有工作做到哪里、为什么形成今天的结论；最后再按年份汇总正式会议/期刊论文，回看整个领域的发展主线。"}},
      {id:"handoff",title:{en:"IV · Technical graph structure is optional audit detail",zh:"第四章 · 图谱技术结构只在需要审计时展开"},question:{en:"How can we preserve the full graph and provenance without making node/edge notation dominate the human reading path?",zh:"怎样完整保留节点、关系和 provenance，同时不让图谱符号占据主要阅读空间？"}}
    ]
  },
  "paper-ideas":{
    chapters:[
      {id:"discussed-ideas",title:{en:"I · Current decisions first",zh:"第一章 · 先看当前结论"},question:{en:"Which idea is an active paper, which ideas can still be investigated, which ones are waiting for one specific missing piece of evidence, and which ones are closed because a simpler explanation or prior work already covers them?",zh:"哪些 Idea 是当前论文、哪些还值得继续查、哪些只差一项明确证据、哪些因为已有工作或更简单解释已经足够而正式关闭？"}},

      {id:"new-ideas",title:{en:"II · Why each newer idea advanced, merged, or stopped",zh:"第二章 · 每个新 Idea 为什么推进、并入或停止"},question:{en:"For each newer proposal, what is the exact problem, what prior work or simple baseline threatens it, what evidence would be needed to keep it alive, and is any experiment actually authorized now?",zh:"对每个较新的提案，具体问题是什么、最接近的已有工作或简单基线是什么、还需要什么证据才能继续，以及现在到底有没有实验获得授权？"}}

    ]
  },
  experiments:{
    chapters:[
      {id:"experiment-queue",title:{en:"I · What can still run, and what has stopped?",zh:"第一章 · 哪些还能跑，哪些已经停止？"},question:{en:"For every experiment direction, what is the current decision, what exact result caused it, and does that result stop only this experiment setup or the scientific idea itself?",zh:"对每个实验方向，现在的结论是什么、是哪条具体结果决定的，以及它只是停止当前实验方案，还是连科学想法本身也已经被否定？"}},

      {id:"experiment-evidence",title:{en:"II · Open the evidence only when you need to verify a decision",zh:"第二章 · 需要核查结论时再展开证据"},question:{en:"Which dataset, model, budget, hidden test, baseline, and pass/stop threshold were fixed before the run, and do the recorded results actually satisfy that rule?",zh:"这次实验在运行前固定了哪些数据、模型、预算、隐藏测试、基线和通过/停止阈值？记录下来的结果是否真的符合当时的规则？"}},

      {id:"experiment-traceability",title:{en:"III · Old logs and approvals",zh:"第三章 · 旧日志、旧审批和旧运行记录"},question:{en:"Which earlier launch checks, runtime logs, pilot records, GPU/resource records, and approvals are kept only so we can reconstruct what happened, while the current decision remains the one shown in Chapter I?",zh:"哪些旧启动检查、运行日志、Pilot 记录、GPU/资源记录和审批只为了以后能复盘当时发生了什么，而不能覆盖第一章给出的当前结论？"}}

    ]
  },
  "selected-paper":{
    chapters:[
      {id:"paper-stri",title:{en:"Paper 1 · STRI",zh:"论文 1 · STRI"},navTitle:{en:"STRI",zh:"STRI"},question:{en:"If semantic skill support is unchanged, can repackaging skills alone change self-evolution control, and what exact certificate identifies when that distortion can be removed?",zh:"如果技能的语义支持不变，仅仅重新拆分或分组 skill package 会不会改变自进化控制？什么精确证书能判断这种表示失真何时可被消除？"}},

      {id:"paper-agent-safety",title:{en:"Paper 2 · Agent Safety R9",zh:"论文 2 · Agent Safety R9"},navTitle:{en:"Agent Safety R9",zh:"Agent Safety R9"},question:{en:"Does passing a safety panel now certify a declared future, and what changes when the same future schedule is run with versus without workflow updates?",zh:"Agent 现在通过安全检查，是否能保证声明的未来 horizon 内也不会首次违规？同一未来 schedule 在更新与不更新 workflow 时会有什么差异？"}},

      {id:"paper-d2-paper-proxy-reward-memory-variance",title:{en:"Paper 3 · Noisy Rewards Write Noisy Memories",zh:"论文 3 · 奖励噪声写入记忆"},navTitle:{en:"Reward → Memory",zh:"奖励 → 记忆"},question:{en:"Can a wrong terminal reward label become durable memory state and measurably change later actions and terminal outcome distributions under fixed future evidence?",zh:"错误的终点 reward 标签能否变成 durable memory state，并在固定 future evidence 下真正改变后续 action 与 terminal outcome distribution？"}},

      {id:"paper-d2-paper-temporal-skill-causal-bottleneck",title:{en:"Paper 4 · Temporal Skill Causal Bottleneck",zh:"论文 4 · 时间技能因果瓶颈"},navTitle:{en:"Temporal Skills",zh:"时间技能"},question:{en:"When do recurring temporal failures actually diagnose a missing reusable procedure, and does a targeted skill repair the original agent rather than merely outperforming a harmful generic helper?",zh:"重复 temporal failure 什么时候真的说明缺少可复用 procedure？targeted skill 是否同时修复原始 Agent，而不只是比一个有害的 generic helper 更好？"}},

      {id:"paper-d2-paper-failure-memory-provenance",title:{en:"Paper 5 · Failure-Memory Provenance",zh:"论文 5 · 失败记忆来源"},navTitle:{en:"Failure Provenance",zh:"失败来源"},question:{en:"After matching actionable guidance and future difficulty, does success-versus-failure trajectory provenance itself change future behavior, and what does the current inconclusive matched swap actually allow us to claim?",zh:"在 actionable guidance 与 future difficulty 尽量匹配后，memory 来自成功还是失败 trajectory 本身会不会改变未来行为？当前未决的 matched swap 到底允许我们声称什么？"}}
    ],
    archiveChapters:[
      {id:"problem-scope",title:{en:"Historical archive · What the older Regression-Gated project was trying to solve",zh:"历史归档 · 旧 Regression-Gated 项目当时想解决什么"},question:{en:"What failure was the older project trying to prevent, what mechanism did it propose, and which assumptions later turned out to need stronger evidence?",zh:"旧项目当时想防止什么具体失败、提出了什么机制，以及后来哪些假设被证明还需要更强证据？"},sourceIds:["paper-problem"]},
      {id:"evidence-experiments",title:{en:"Historical experiment plan",zh:"历史实验计划"},question:{en:"What exact comparisons, models, tasks, and stop conditions were planned, and which of those runs were never authorized after later evidence changed the project?",zh:"当时计划比较哪些方法、模型和任务，停止条件是什么？后续证据改变项目后，其中哪些实验实际上从未获得运行授权？"},sourceIds:["paper-experiments"]},
      {id:"narrative-execution",title:{en:"The old plan we no longer execute",zh:"已经不再执行的旧计划"},question:{en:"What did the earlier project plan propose to run, which later evidence made that plan obsolete, and why should none of those old steps be treated as pending work now?",zh:"旧方案当时计划跑什么、后来的哪类证据让这条路线失效，以及为什么这些旧步骤现在都不能再当成待办任务？"},sourceIds:["paper-roadmap"]},
      {id:"review-gates",title:{en:"What the failed project taught the research system",zh:"旧项目失败后，系统具体学到了什么"},question:{en:"Which concrete results showed that the data/environment could not support the intended test or that a simpler baseline already matched the method, and what checks were added so future projects catch those problems earlier?",zh:"哪些具体结果说明当时的数据/环境不足以支撑目标实验，或更简单基线已经能做到同样效果？系统后来增加了哪些检查，让后续项目更早发现这些问题？"},sourceIds:["review-log"]}
    ]
  },
  bibliography:{
    chapters:[
      {id:"published-spine",title:{en:"I · Build the field spine from formally published work",zh:"第一章 · 先用正式发表论文建立研究主线"},question:{en:"Across the four lifecycle questions, how did simple baselines evolve into memory, skill, workflow, adaptation, evaluation, and governance methods—and which peer-reviewed gaps remain?",zh:"围绕四个自进化生命周期问题，简单方法怎样逐步发展成记忆、技能、工作流、适应、评价与治理方法？哪些方向在正式发表文献里仍然明显稀疏？"}},
      {id:"published-comparison",title:{en:"II · Compare published papers against concrete simple baselines",zh:"第二章 · 横向比较正式论文：简单方法、本文方法与证据边界"},question:{en:"For papers studying the same problem, what does the simple approach actually do, what mechanism does each paper add, what evidence is currently verified, and how does it relate to our research directions?",zh:"研究同一个问题的论文里，简单方法到底怎么做、每篇论文具体增加了什么、当前证据核到了哪里，以及它和我们的研究方向是什么关系？"}},
      {id:"idea-mining",title:{en:"III · Turn the literature into an idea-mining search space",zh:"第三章 · 把文献整理成可用于后续找新研究问题的搜索空间"},question:{en:"Which motifs are already crowded, which failures recur without a stable solution, which interfaces between mature lines remain open, and what must a gap specify before entering idea generation?",zh:"哪些套路已经很拥挤、哪些失败在多篇论文里反复出现却没有稳定解、哪些成熟方向的接口仍有断层，以及一个文献空白要补齐什么才值得进入后续候选生成？"}},
      {id:"field-maps",title:{en:"IV · Use the full corpus maps after the idea-mining gaps are clear",zh:"第四章 · 研究空白搜索空间看清以后，再看完整语料的领域分布"},question:{en:"Where is the complete corpus dense by year, update surface, feedback signal, and publication type, including the preprint frontier?",zh:"把预印本前沿也放回来以后，按年份、更新对象、反馈信号和发表类型看，完整语料主要集中在哪里？"}},
      {id:"search-corpus",title:{en:"V · Search the complete library, including the preprint frontier",zh:"第五章 · 检索全部文献，包括预印本前沿"},question:{en:"How can readers locate, filter, compare, cite, and export exactly the published or frontier records they need?",zh:"怎样定位、筛选、比较、引用和导出真正需要的正式论文或前沿预印本？"}},
      {id:"coverage-protocol",title:{en:"VI · Finally audit corpus provenance, coverage, and trust",zh:"第六章 · 最后检查语料来源、覆盖范围与可信度"},question:{en:"Which sources feed the corpus, how are duplicate versions merged, and which fields are manually verified versus automatically derived?",zh:"这份文献库由哪些来源组成、重复版本怎样合并，以及哪些内容经过人工核验、哪些只是自动归纳？"},sourceIds:["coverage-method"]}
    ]
  }
};
