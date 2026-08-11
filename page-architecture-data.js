window.PAGE_ARCHITECTURES = {
  home:{
    chapters:[
      {id:"understand-field",title:{en:"Understand the field",zh:"理解领域"},question:{en:"What counts as self-evolution, what can change, and where does the field come from?",zh:"什么算自进化、哪些对象可以变化，以及这个领域从哪里发展而来？"},links:["foundations.html","mechanisms.html","domains.html","evaluation.html"]},
      {id:"select-research",title:{en:"Select a research direction",zh:"选择研究方向"},question:{en:"How does the research system produce candidates, and which concrete paper idea should be pursued next?",zh:"科研系统如何产生候选，下一步又应该选择哪个具体论文 Idea？"},links:["system-overview.html","research-directions.html","paper-ideas.html"]},
      {id:"execute-audit",title:{en:"Execute and audit",zh:"执行与审计"},question:{en:"How are pilots tracked, how is one selected paper developed, and how is its evidence traced back to the literature?",zh:"Pilot 如何跟踪，一个选中论文如何继续执行，以及证据如何追溯到文献？"},links:["experiments.html","selected-paper.html","bibliography.html"]}
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
      {id:"reproducibility",title:{en:"III · How can evidence be reproduced?",zh:"第三章 · 证据如何被复现？"},question:{en:"Which repositories, artifacts, version records, and reporting standards make claims auditable?",zh:"哪些代码仓库、研究工件、版本记录和报告标准能让主张可审计？"},sourceIds:["repositories"],resourceModes:["repositories"]}
    ]
  },
  "system-overview":{
    chapters:[
      {id:"system-map",title:{en:"I · System map and current operating state",zh:"第一章 · 系统全景与当前运行状态"},question:{en:"What are the major layers of the research system, and where is the current bottleneck?",zh:"整套科研系统由哪些层组成，当前真正的瓶颈在哪里？"}},
      {id:"evidence-consultation",title:{en:"II · Evidence, idea formation, and AI consultation",zh:"第二章 · 证据、Idea 形成与 AI 会诊"},question:{en:"How do literature, evidence graphs, collision review, idea search, and multi-model consultation turn a broad problem into a falsifiable research contract?",zh:"文献、证据图、撞车审查、Idea 搜索和多模型会诊如何把宽泛问题压成可证伪研究合同？"}},
      {id:"economy-compile",title:{en:"III · P0 Economy Gate and experiment compilation",zh:"第三章 · P0 经济门与实验启动前编译"},question:{en:"How does the system reject reducible, unsupported, mis-specified, or low-VOI experiments before expensive execution?",zh:"系统如何在昂贵执行前淘汰可约简、底座不足、建模错误或低 VOI 的实验？"}},
      {id:"scientific-state-machine",title:{en:"IV · Scientific state machine and failure semantics",zh:"第四章 · 科学状态机与失败语义"},question:{en:"How are phenomenon support, method evaluation, replication, and typed failure classes kept scientifically distinct?",zh:"现象支持、方法实验、复现和各种失败类型如何保持科学语义分离？"}},
      {id:"runtime-authority",title:{en:"V · Runtime, authority, automation, and recovery",zh:"第五章 · 运行时、权限、自动化与恢复"},question:{en:"How are servers, GPU leases, single-writer authority, traces, budgets, AI triggers, and recovery managed safely?",zh:"服务器、GPU 租约、单写者权限、Trace、预算、AI 自动触发与恢复如何安全管理？"}},
      {id:"learning-publication",title:{en:"VI · Decision feedback, learning, and publication",zh:"第六章 · 决策回流、经验沉淀与发布"},question:{en:"How do experiment decisions become repair rules, system constraints, durable artifacts, and public snapshots without rewriting scientific history?",zh:"实验决策如何变成修复规则、系统约束、长期工件和公开快照，同时不改写科学历史？"}}
    ]
  },
  "research-directions":{
    chapters:[
      {id:"orientation",title:{en:"I · Orientation: four lifecycle questions",zh:"第一章 · 入门：四个生命周期问题"},question:{en:"How do the ten directions fit into one evolution lifecycle?",zh:"十个方向如何放进同一条自进化生命周期？"}},
      {id:"landscape",title:{en:"II · Field landscape and direction map",zh:"第二章 · 领域全景与方向地图"},question:{en:"How are directions, paper ideas, and the selected-paper workspace related?",zh:"研究方向、论文 Idea 与选中论文工作区之间是什么关系？"}},
      {id:"direction-clusters",title:{en:"III · Ten directions grouped by four big questions",zh:"第三章 · 按四个大问题组织十个方向"},question:{en:"What does each direction study, and how is it different from its neighbors?",zh:"每个方向研究什么，又与相邻方向有何区别？"}},
      {id:"long-term-agenda",title:{en:"IV · Long-term research agenda",zh:"第四章 · 长期研究议程"},question:{en:"Which dependencies and staged priorities turn the direction map into a research program?",zh:"哪些依赖关系和阶段优先级能把方向地图转化为研究计划？"},sourceIds:["research-agenda"]}
    ]
  },
  "paper-ideas":{
    chapters:[
      {id:"discussed-ideas",title:{en:"I · Discussed ideas",zh:"第一章 · 已讨论 Idea"},question:{en:"Which reviewed scientific directions have entered P0, and which parents are terminally merged or dropped?",zh:"哪些已审科学方向已经进入 P0，哪些 parent 已终态合并或弃掉？"}},
      {id:"new-ideas",title:{en:"II · Standalone methods outside the original parent set",zh:"第二章 · 原 Parent 集之外的独立方法"},question:{en:"Which standalone methods survive outside the original 26 parents, what stable codes do they use, and what is their P0 contract?",zh:"哪些方法在原 26 个 parent 之外仍独立存活，它们的正式编号是什么，P0 合同是什么？"}}
    ]
  },
  experiments:{
    chapters:[
      {id:"experiment-queue",title:{en:"I · Current terminal decisions",zh:"第一章 · 当前终态决策"},question:{en:"What is the single current decision for each of the 20 active P0 directions, and what evidence is decisive for that decision?",zh:"20 个活跃 P0 方向现在各自唯一的终态结论是什么，哪条证据真正决定了这个结论？"}},
      {id:"experiment-evidence",title:{en:"II · Current evidence audit",zh:"第二章 · 当前证据审计"},question:{en:"When a row needs auditing, which frozen P0 contract and qualification evidence support it without restating the verdict?",zh:"当需要核查某一行时，应查看哪些冻结 P0 合同与资格证据，而不再重复终态结论？"}},
      {id:"experiment-traceability",title:{en:"III · Historical traceability archive",zh:"第三章 · 历史追溯档案"},question:{en:"Which earlier Pre-GPU, runtime, pilot-registry, resource, and approval artifacts are retained for provenance without competing with the current decision table?",zh:"哪些旧 Pre-GPU、runtime、Pilot Registry、资源与审批工件需要保留追溯，但不能再与当前终态总表竞争主叙事？"}}
    ]
  },
  "selected-paper":{
    chapters:[
      {id:"problem-scope",title:{en:"I · ICLR learning problem and claim boundary",zh:"第一章 · ICLR 学习问题与主张边界"},question:{en:"Why is local repair not reliable self-evolution, and what can Regression-Gated Self-Evolution legitimately claim?",zh:"为什么局部修复不等于可靠自进化，Regression-Gated Self-Evolution 可以合法主张什么？"},sourceIds:["paper-problem"]},
      {id:"evidence-experiments",title:{en:"II · Persistent-learning and regression experiments",zh:"第二章 · 持久学习与非回退实验"},question:{en:"Which matched-budget, multi-round experiments distinguish learning from extra inference and establish stability?",zh:"哪些等预算、多轮实验能够区分学习与额外推理并验证稳定性？"},sourceIds:["paper-experiments"]},
      {id:"narrative-execution",title:{en:"III · ICLR narrative and execution roadmap",zh:"第三章 · ICLR 论文叙事与执行路线"},question:{en:"How do the constrained-improvement formulation, main table, four-week plan, and CVPR follow-ups fit together?",zh:"受约束改进形式化、主表、四周计划与 CVPR 后续如何衔接？"},sourceIds:["paper-roadmap"]},
      {id:"review-gates",title:{en:"IV · ICLR review loop and maturity gates",zh:"第四章 · ICLR 评审闭环与成熟门槛"},question:{en:"Which learning-dynamics objections remain unresolved before submission?",zh:"投稿前还需解决哪些学习动力学质疑？"},sourceIds:["review-log"]}
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
