window.PAGE_ARCHITECTURES = {
  home:{
    chapters:[
      {id:"understand-field",title:{en:"Understand the field",zh:"理解领域"},question:{en:"What counts as self-evolution, what can change, where does the field come from, and which structural research problems have emerged?",zh:"什么算自进化、哪些对象可以变化、这个领域从哪里发展而来，以及已经形成了哪些结构性研究问题？"},links:["foundations.html","mechanisms.html","domains.html","evaluation.html","research-directions.html"]},
      {id:"select-research",title:{en:"Choose the next research problem",zh:"选择下一轮研究问题"},question:{en:"How do we turn new paper evidence into candidate problems, reject ideas already explained by prior work or simpler theory, and decide which surviving problem is worth a small decisive experiment?",zh:"怎样把最新论文证据变成候选问题、淘汰已经被已有工作或更简单理论解释的 Idea，并决定哪个真正剩下的问题值得做一次小规模决定性实验？"},links:["system-overview.html","research-map.html","paper-ideas.html","research-timeline.html"]},

      {id:"execute-audit",title:{en:"Run, inspect, and submit",zh:"运行、核查与投稿"},question:{en:"Which experiments are still allowed to run, what exact evidence supports the current STRI submission, and how can old projects be inspected without mistaking their archived plans for today's work?",zh:"哪些实验现在仍允许运行、STRI 当前投稿具体由哪些证据支持，以及怎样查看旧项目而不把它们已经归档的计划误当成今天的待办？"},links:["experiments.html","selected-paper.html","bibliography.html"]}
    ]
  },
  foundations:{
    chapters:[
      {id:"boundary-history",title:{en:"Field boundary and historical evolution",zh:"领域边界与历史演化"},question:{en:"How do we distinguish persistent evolution from retries and self-correction, and how did the field emerge?",zh:"如何区分持久进化、重试与自纠错，这个领域又如何形成？"},sourceIds:["foundations"],includeOverview:true},
      {id:"taxonomy-evidence",title:{en:"Taxonomy and evidence requirements",zh:"分类体系与证据要求"},question:{en:"What changes, what drives it, when is it committed, and what evidence validates the claim?",zh:"更新什么、由什么驱动、何时提交，以及什么证据才能支持主张？"},sourceIds:["taxonomy"]}
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
      {id:"overview",title:{en:"I · Start here — what happens from a paper to a finished experiment",zh:"第一章 · 从这里开始——一篇论文怎样一路变成可执行实验"},question:{en:"What are the actual steps from reading new evidence to choosing a problem, designing a paper, approving an experiment, running it, and recording the result—and who is allowed to make each decision?",zh:"从读到新证据，到选问题、设计论文、批准实验、真正运行、记录结果，实际依次做哪些事？每一步又是谁有权决定？"}},

      {id:"problem-discovery",title:{en:"II · Decide whether there is a new problem at all",zh:"第二章 · 先判断到底有没有新的科学问题"},question:{en:"When a paper or experiment shows an unusual failure, how do we check whether prior work or a known explanation already accounts for it before spending time inventing a method?",zh:"当论文或实验出现一个异常失败时，怎样先检查已有工作或成熟解释是否已经能说明它，而不是马上开始想新方法？"}},

      {id:"scientific-design",title:{en:"III · Design the scientific contribution before coding",zh:"第三章 · 写代码前先把科学贡献设计完整"},question:{en:"Before implementation, can we state the exact new claim, why the mechanism should work, the strongest comparison, the required ablations, and the evidence that would convince a reviewer?",zh:"实现方法之前，能否先明确写出：新贡献到底是什么、为什么应该有效、最强对照是谁、必须做哪些消融，以及什么证据能真正说服审稿人？"}},

      {id:"experiment-compile",title:{en:"IV · Find the cheapest experiment that can change the decision",zh:"第四章 · 找到最便宜、但足以改变结论的实验"},question:{en:"Before using GPU, have we verified that the dataset/environment can realize the effect, the baseline is strong and equally informed, the truth label is independent, the sample size is enough, and a positive or negative result would actually change what we do next?",zh:"用 GPU 前是否已经确认：数据/环境真的能产生目标效应、基线足够强且拿到同样信息、真值独立、样本量够用，而且无论结果正负都能真正改变下一步决策？"}},

      {id:"validation-scale",title:{en:"V · Run small, identify what failed, then decide whether to scale",zh:"第五章 · 先小规模运行，弄清哪里失败，再决定是否扩量"},question:{en:"If a local test fails, how do we tell whether the cause is broken code, a bad experiment design, an incapable update mechanism, insufficient data, or a false scientific idea—and when is the method stable enough for full experiments?",zh:"局部实验没过时，怎样区分是代码坏了、实验设计有问题、更新机制本身做不到、数据不够，还是科学想法真的错了？又要到什么程度才允许冻结方法并做全量实验？"}},

      {id:"paper-evidence",title:{en:"VI · Freeze the scientific paper evidence",zh:"第六章 · 冻结论文科学证据"},question:{en:"For each headline claim, is there direct evidence, a strongest baseline, required ablations and analyses, and a reproducible claim-to-evidence binding that is no broader than the data?",zh:"对每条核心主张，是否都有直接证据、最强基线、必要消融与分析，并形成不宽于数据的可复现 claim–evidence 绑定？"}},

      {id:"paper-construction",title:{en:"VII · Search the story, then construct the manuscript",zh:"第七章 · 先竞争故事线，再形成成稿"},question:{en:"Within the frozen claim set, which story should win, and is the manuscript explicitly bound to that Story Search receipt?",zh:"在冻结主张集合内，哪条故事线应该获胜？成稿是否明确绑定到这一 Story Search receipt？"}},

      {id:"review-repair",title:{en:"VIII · Mock review, targeted repair, claim audit, and PDF QA",zh:"第八章 · 模拟审稿、定向修复、主张审计与 PDF QA"},question:{en:"What would cause rejection in blind and artifact-aware review, which issues can be repaired without new science, and does the repaired PDF remain strictly evidence-bound?",zh:"Blind 与 Artifact-aware 两种审稿分别会因什么拒稿？哪些问题能在不新增科学结论的前提下修复，修复后的 PDF 是否仍严格绑定证据？"}},

      {id:"submission-closure",title:{en:"IX · Prebuttal, submission authority, and real reviewer decisions",zh:"第九章 · 预答辩、投稿权限与真实审稿决策"},question:{en:"Are decision-critical objections resolved, all manuscript checks passed, external human submission authority explicit, and real reviewer feedback routed without silently changing scientific truth?",zh:"决策关键质疑是否解决、文稿检查是否全部通过、外部人工投稿权限是否明确，以及真实 reviewer 意见是否在不偷改科学真值的前提下被正确处理？"}},

      {id:"system-learning",title:{en:"X · Remember why we stopped, continued, were accepted, or were rejected",zh:"第十章 · 记住为什么继续、停止、被接收或被拒绝"},question:{en:"After scientific and submission outcomes, what evidence, failure pattern, reviewer risk, reopen condition, and cheap pre-check should be saved so the next agent learns without rewriting old decisions?",zh:"科研与投稿结果产生后，应该保存哪些证据、失败模式、审稿风险、重开条件和廉价前置检查，才能让下一轮 Agent 真正学习，又不会悄悄改写旧结论？"}}

    ]
  },
  "research-directions":{
    chapters:[
      {id:"orientation",title:{en:"I · How the historical field taxonomy was formed",zh:"第一章 · 历史领域分类怎样形成"},question:{en:"How did the ten D1–D10 directions decompose the agent self-evolution lifecycle, and what field questions were they trying to make explicit?",zh:"D1–D10 十个历史方向怎样拆解 Agent 自进化生命周期，它们分别把哪些领域问题显式化？"}},
      {id:"landscape",title:{en:"II · Historical D1–D10 and current A–G",zh:"第二章 · 历史 D1–D10 与当前 A–G 的关系"},question:{en:"How did the historical taxonomy and former idea lineage migrate into the A–G coordinate system used by today's ResearchItems?",zh:"历史方向分类与旧 Idea 谱系怎样迁移到今天 ResearchItem 使用的 A–G 坐标系？"}},
      {id:"direction-clusters",title:{en:"III · Ten historical directions, boundaries, and literature",zh:"第三章 · 十个历史方向、科学边界与代表文献"},question:{en:"What did each direction study, how did it differ from neighboring questions, and which papers grounded the boundary?",zh:"每个历史方向研究什么、与相邻问题有何区别、哪些代表论文支撑了它的边界？"}},
      {id:"long-term-agenda",title:{en:"IV · Former agenda and still-open field questions",zh:"第四章 · 历史长期议程与仍开放的领域问题"},question:{en:"Which older program-level questions remain useful as field knowledge even though today's work is scheduled by ResearchItems rather than a static agenda?",zh:"哪些过去的项目级长期问题仍值得作为领域知识保留，即使今天的研究调度已经由 ResearchItem 而不是静态议程决定？"},sourceIds:["research-agenda"]}
    ]
  },
  "research-map":{
    chapters:[
      {id:"current-overview",title:{en:"I · A–G coordinate system and collection colors",zh:"第一章 · A–G 坐标系与集合颜色"},question:{en:"How are current ResearchItems organized so each collection keeps one stable color without conflating category with scientific status?",zh:"当前 ResearchItem 如何按 A–G 组织，并让每个集合固定一种颜色而不把类别颜色误当成科学状态？"}},
      {id:"knowledge-graph",title:{en:"II · Canonical knowledge graph and public research status",zh:"第二章 · Canonical 知识图谱与外部研究现状"},question:{en:"Which Track, Idea, Claim, nearest-work, and Experiment nodes and edges already exist, and how far have representative external papers publicly progressed?",zh:"已有 Track、Idea、Claim、nearest-work、Experiment 等哪些真实节点与边，同时代表性外部论文公开研究已经推进到哪一步？"}},
      {id:"current-coverage",title:{en:"III · What our A–G portfolio means now",zh:"第三章 · 我们的 A–G 组合现在做到哪里"},question:{en:"For each category, what has our own portfolio decided, what survives, and where has a ResearchItem handed off to PaperState?",zh:"对每一类，我们自己的研究组合已经形成什么结论、留下什么资产、哪些 ResearchItem 已经交接到 PaperState？"}},
      {id:"coverage-gaps",title:{en:"IV · Internal coverage density and gaps",zh:"第四章 · 内部覆盖密度与空白"},question:{en:"Which regions have been searched heavily and which have relatively few internal research objects without turning paper or object counts into a priority score?",zh:"哪些区域已经被大量搜索、哪些区域内部研究对象较少，同时避免把论文数或对象数误当成优先级评分？"}},
      {id:"handoff",title:{en:"V · From map to ResearchItem, Timeline, and Paper",zh:"第五章 · 从图谱进入 ResearchItem、时间轴与论文"},question:{en:"Where should a reader go for authoritative decisions, chronological causal history, or submission-ready paper state?",zh:"要查看权威当前结论、按时间的因果历史或已进入投稿阶段的论文状态，分别应该去哪里？"}}
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
      {id:"current-stri",title:{en:"I · Current selected paper — STRI",zh:"第一章 · 当前选中论文 — STRI"},question:{en:"What exactly is submission-ready, which claims are supported, what is explicitly excluded, and what human handoff remains?",zh:"STRI 当前究竟哪些内容已经达到投稿就绪、哪些主张得到支持、哪些内容明确不主张，以及还剩什么人工交接？"}},
      {id:"problem-scope",title:{en:"II · Historical archive — what the older Regression-Gated project was trying to solve",zh:"第二章 · 历史归档 — 旧 Regression-Gated 项目当时想解决什么"},question:{en:"What failure was the older project trying to prevent, what mechanism did it propose, and which assumptions later turned out to need stronger evidence?",zh:"旧项目当时想防止什么具体失败、提出了什么机制，以及后来哪些假设被证明还需要更强证据？"},sourceIds:["paper-problem"]},
      {id:"evidence-experiments",title:{en:"III · Historical experiment plan",zh:"第三章 · 历史实验计划"},question:{en:"What exact comparisons, models, tasks, and stop conditions were planned, and which of those runs were never authorized after later evidence changed the project?",zh:"当时计划比较哪些方法、模型和任务，停止条件是什么？后续证据改变项目后，其中哪些实验实际上从未获得运行授权？"},sourceIds:["paper-experiments"]},
      {id:"narrative-execution",title:{en:"IV · The old plan we no longer execute",zh:"第四章 · 已经不再执行的旧计划"},question:{en:"What did the earlier project plan propose to run, which later evidence made that plan obsolete, and why should none of those old steps be treated as pending work now?",zh:"旧方案当时计划跑什么、后来的哪类证据让这条路线失效，以及为什么这些旧步骤现在都不能再当成待办任务？"},sourceIds:["paper-roadmap"]},

      {id:"review-gates",title:{en:"V · What the failed project taught the research system",zh:"第五章 · 旧项目失败后，系统具体学到了什么"},question:{en:"Which concrete results showed that the data/environment could not support the intended test or that a simpler baseline already matched the method, and what checks were added so future projects catch those problems earlier?",zh:"哪些具体结果说明当时的数据/环境不足以支撑目标实验，或更简单基线已经能做到同样效果？系统后来增加了哪些检查，让后续项目更早发现这些问题？"},sourceIds:["review-log"]}
    ]
  },
  bibliography:{
    chapters:[
      {id:"coverage-protocol",title:{en:"I · Corpus construction and coverage protocol",zh:"第一章 · 语料构建与覆盖协议"},question:{en:"Which papers enter the corpus, how are duplicates resolved, and what uncertainty remains?",zh:"哪些论文进入语料、重复版本如何处理、还剩哪些不确定性？"},sourceIds:["coverage-method"]},
      {id:"ranking-reading",title:{en:"II · Ranking and structured reading",zh:"第二章 · 排序与结构化阅读"},question:{en:"How are papers prioritized, and how is each paper summarized without overstating evidence?",zh:"论文如何排序，又如何在不过度声称的前提下结构化梳理？"}},
      {id:"field-maps",title:{en:"III · Field maps",zh:"第三章 · 领域地图"},question:{en:"How do publication time, update surface, feedback signal, and method family shape the field?",zh:"发表时间、更新对象、反馈信号和方法族如何共同塑造领域？"}},
      {id:"search-corpus",title:{en:"IV · Search, filter, and export the corpus",zh:"第四章 · 检索、筛选与导出语料"},question:{en:"How can readers find, compare, cite, and export individual records?",zh:"读者如何查找、比较、引用和导出单篇记录？"}}
    ]
  }
};
