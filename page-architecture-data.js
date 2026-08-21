window.PAGE_ARCHITECTURES = {
  home:{
    chapters:[
      {id:"understand-field",title:{en:"Understand the field",zh:"理解领域"},question:{en:"What counts as self-evolution, how did the field form, and how can it be read through mechanism, application domain, and evaluation evidence?",zh:"什么算自进化、这个领域怎样形成，以及怎样分别从进化机制、应用场景和评测证据三个切面理解它？"},links:["foundations.html","research-directions.html","mechanisms.html","domains.html","evaluation.html"]},
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
      {id:"model-internal",title:{en:"I · Model-internal adaptation",zh:"第一章 · 模型内部适应"},question:{en:"When should the agent change parameters, prompts, context, or reasoning traces?",zh:"Agent 何时应修改参数、提示词、上下文或推理轨迹？"},relation:{en:"Closest to the foundation model; potentially broad transfer but increasing cost and irreversibility.",zh:"最接近基础模型；迁移范围可能更广，但成本和不可逆性也更高。"},sourceIds:["model-improvement","prompt-evolution"]},
      {id:"externalized-experience",title:{en:"II · Externalized experience and capability",zh:"第二章 · 外部化经验与能力"},question:{en:"How can experience persist outside model weights as memory, skills, and tools?",zh:"经验如何不依赖模型权重，而以记忆、技能和工具持续存在？"},relation:{en:"More inspectable and reversible than parameter updates; more persistent than one-session context.",zh:"比参数更新更可检查和可回滚；比单次上下文更具持久性。"},sourceIds:["memory-evolution","tool-evolution"]},
      {id:"system-level",title:{en:"III · System-level self-design",zh:"第三章 · 系统级自设计"},question:{en:"How can the agent change routing, control flow, component composition, and its own improvement harness?",zh:"Agent 如何改变路由、控制流、组件组合和自身改进框架？"},relation:{en:"Coordinates all lower-level update surfaces and determines how they are searched, tested, and released.",zh:"协调所有低层更新对象，并决定它们如何被搜索、测试和发布。"},sourceIds:["workflow-evolution"]}
    ]
  },
  domains:{
    chapters:[
      {id:"multimodal-reasoning",title:{en:"I · Multimodal perception and reasoning",zh:"第一章 · 多模态感知与推理"},question:{en:"How do visual evidence, critique, self-play, and multimodal memory support persistent improvement?",zh:"视觉证据、批评、自博弈和多模态记忆如何支持持久改进？"},sourceIds:["visual-multimodal"]},
      {id:"digital-interaction",title:{en:"II · Digital interaction: GUI and Web",zh:"第二章 · 数字交互：GUI 与 Web"},question:{en:"How does a visual agent learn from websites, interfaces, tools, and partially observable interaction histories?",zh:"视觉 Agent 如何从网站、界面、工具和部分可观测交互历史中学习？"},sourceIds:["gui-web"]},
      {id:"physical-world",title:{en:"III · Embodiment and world adaptation",zh:"第三章 · 具身与世界适应"},question:{en:"How should agents adapt when bodies, sensors, dynamics, and physical environments change?",zh:"当身体、传感器、动力学和物理环境变化时，Agent 应如何适应？"},sourceIds:["embodied-world"]}
    ]
  },
  evaluation:{
    chapters:[
      {id:"validity-safety",title:{en:"I · What counts as improvement?",zh:"第一章 · 什么才算改进？"},question:{en:"How should persistent gain, regression, negative evolution, safety, and rollback be measured?",zh:"如何测量持久收益、回退、负向进化、安全与回滚？"},sourceIds:["evaluation-safety"]},
      {id:"tasks-benchmarks",title:{en:"II · Where should evolution be tested?",zh:"第二章 · 应该在哪里测试进化？"},question:{en:"Which task streams, environments, datasets, and benchmarks expose genuine longitudinal behavior?",zh:"哪些任务流、环境、数据集和基准能够暴露真实纵向行为？"},sourceIds:["datasets-benchmarks"],resourceModes:["benchmarks"]},
      {id:"reproducibility",title:{en:"III · Can another person rerun the result?",zh:"第三章 · 别人能否重新跑出同样结果？"},question:{en:"Which code, data, environment versions, commands, logs, and reporting details must be saved so another researcher can reproduce the key result rather than merely read a summary?",zh:"需要保存哪些代码、数据、环境版本、运行命令、日志和报告细节，才能让另一位研究者真正重新跑出关键结果，而不是只能阅读摘要？"},sourceIds:["repositories"],resourceModes:["repositories"]}
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
      {id:"orientation",title:{en:"I · Field evolution and three reading axes",zh:"第一章 · 领域怎样形成，以及三种阅读切面"},question:{en:"How did self-evolution expand from local model/prompt changes to memory, skills, workflows, and world adaptation, and how should the field now be read through mechanism, application domain, and evaluation?",zh:"Agent 自进化怎样从局部模型/Prompt 更新扩展到记忆、技能、工作流和世界适应？今天又该怎样分别从机制、场景和评测三个切面理解这个领域？"}},
      {id:"landscape",title:{en:"II · Historical problem map and migration to current A–G",zh:"第二章 · 历史问题图谱，以及如何迁移到当前 A–G"},question:{en:"How did D1–D10 form from the historical evolution of the field, and how does that field-history coordinate system connect to today's authoritative A–G ResearchItems?",zh:"D1–D10 怎样从领域历史中形成？这套“理解领域”的历史坐标又怎样连接到今天真正维护 ResearchItem 的 A–G 坐标？"}},
      {id:"direction-clusters",title:{en:"III · Ten historical directions, boundaries, and literature",zh:"第三章 · 十个历史方向、科学边界与代表文献"},question:{en:"What did each direction study, how did it differ from neighboring questions, and which papers grounded the boundary?",zh:"每个历史方向研究什么、与相邻问题有何区别、哪些代表论文支撑了它的边界？"}},
      {id:"long-term-agenda",title:{en:"IV · Former agenda and still-open field questions",zh:"第四章 · 历史长期议程与仍开放的领域问题"},question:{en:"Which older program-level questions remain useful as field knowledge even though today's work is scheduled by ResearchItems rather than a static agenda?",zh:"哪些过去的项目级长期问题仍值得作为领域知识保留，即使今天的研究调度已经由 ResearchItem 而不是静态议程决定？"},sourceIds:["research-agenda"]}
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
      {id:"paper-stri",title:{en:"Paper 1 · STRI",zh:"论文 1 · STRI"},navTitle:{en:"STRI",zh:"STRI"},question:{en:"What is STRI's current scientific claim boundary, evidence state, Paper Acceptance progress, and submission package?",zh:"STRI 当前的科学主张边界、证据状态、Paper Acceptance 进度和投稿工件分别是什么？"}},
      {id:"paper-agent-safety",title:{en:"Paper 2 · Agent Safety R9",zh:"论文 2 · Agent Safety R9"},navTitle:{en:"Agent Safety R9",zh:"Agent Safety R9"},question:{en:"What controlled first-violation evidence supports Agent Safety R9, which broader claims remain excluded, and what is its submission state?",zh:"Agent Safety R9 由哪些受控 first-violation 证据支撑、哪些更宽结论仍明确排除，以及它当前处于什么投稿状态？"}}
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
      {id:"coverage-protocol",title:{en:"I · Where the corpus comes from and how much to trust each layer",zh:"第一章 · 文献从哪里来，以及不同层级能信到什么程度"},question:{en:"Which sources feed the corpus, what enters or stays outside the core, how are duplicate versions merged, and which parts are manually verified versus automatically classified?",zh:"这份文献库由哪些来源组成、什么会进入核心或只作为邻接工作、重复版本怎样合并，以及哪些内容经过人工核验、哪些只是自动分类？"},sourceIds:["coverage-method"]},
      {id:"field-maps",title:{en:"II · See the field distribution before opening individual papers",zh:"第二章 · 先看领域分布，再决定往哪里深入"},question:{en:"Where is the literature dense by year, update surface, feedback signal, and publication type—and what do those counts describe without turning them into a research-priority score?",zh:"按年份、更新对象、反馈信号和发表类型看，文献主要集中在哪里？这些数量能说明什么，又不能被误读成什么研究优先级？"}},
      {id:"ranking-reading",title:{en:"III · Decide what to read and how deeply to trust the summary",zh:"第三章 · 再决定先读什么，以及单篇梳理能信到哪一层"},question:{en:"What is the recommended reading path from field overviews to direct self-evolution work and foundations, and which paper summaries are manually curated versus metadata-derived?",zh:"从领域综述、直接自进化方法到基础工作应该按什么顺序读？单篇论文的哪些梳理是人工深度整理，哪些只是基于摘要或元数据的保守归纳？"}},
      {id:"search-corpus",title:{en:"IV · Search, narrow, compare, cite, and export",zh:"第四章 · 最后检索、缩小范围、比较、引用与导出"},question:{en:"How can readers quickly locate a paper, narrow the corpus by year/publication/signal/update surface, preserve the filter state, and export exactly the records they need?",zh:"怎样快速定位一篇论文，再按年份、发表类型、反馈信号和更新对象缩小范围，并保留筛选状态、导出真正需要的记录？"}}
    ]
  }
};
