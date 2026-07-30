window.PAGE_ARCHITECTURES = {
  home:{
    chapters:[
      {id:"understand-field",title:{en:"Understand the field",zh:"理解领域"},question:{en:"What counts as self-evolution, what can change, and where does the field come from?",zh:"什么算自进化、哪些对象可以变化，以及这个领域从哪里发展而来？"},links:["foundations.html","mechanisms.html","domains.html","evaluation.html"]},
      {id:"select-research",title:{en:"Select a research direction",zh:"选择研究方向"},question:{en:"Which stable scientific problem and concrete paper idea should be pursued next?",zh:"下一步应该选择哪个稳定科学问题和具体论文 Idea？"},links:["research-directions.html","paper-ideas.html"]},
      {id:"execute-audit",title:{en:"Execute and audit",zh:"执行与审计"},question:{en:"How is one selected paper developed, and how is its evidence traced back to the literature?",zh:"一个选中论文如何被执行，以及其证据如何追溯到文献？"},links:["selected-paper.html","bibliography.html"]}
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
      {id:"evidence-pipeline",title:{en:"I · Evidence-to-idea pipeline",zh:"第一章 · 从证据到 Idea 的生成管线"},question:{en:"How are literature evidence, research gaps, idea operators, reviewers, and pilot gates connected?",zh:"文献证据、研究空缺、Idea 算子、评审与 Pilot 门槛如何连接？"}},
      {id:"advisor-board",title:{en:"II · Advisor decision board",zh:"第二章 · 师兄与老师决策板"},question:{en:"Which candidates deserve immediate expert attention, and what remains unresolved for each one?",zh:"哪些候选值得优先由师兄和老师判断，每个候选还缺什么证据？"}},
      {id:"shortlist-dossiers",title:{en:"III · Shortlist evidence dossiers",zh:"第三章 · 短名单完整论证卡"},question:{en:"For each shortlisted idea, what is the problem, mechanism, rationale, method logic, importance, advantage, and decisive pilot?",zh:"每个短名单 Idea 的问题、机制、合理性、方法逻辑、重要性、优势与决定性 Pilot 分别是什么？"}},
      {id:"candidate-archive",title:{en:"IV · Candidate archive and traceable ranking",zh:"第四章 · 完整候选归档与可追溯排序"},question:{en:"How are all retained ideas, held candidates, legacy scores, and direction-level decisions preserved for audit?",zh:"如何保留全部 Idea、暂缓候选、旧评分与方向决策供后续追溯？"}}
    ]
  },
  "selected-paper":{
    chapters:[
      {id:"problem-scope",title:{en:"I · Problem and claim boundary",zh:"第一章 · 问题与主张边界"},question:{en:"What failure does GroundEvo-Admission address, and what can the first paper legitimately claim?",zh:"GroundEvo-Admission 解决什么失败，首篇论文可以合法主张什么？"},sourceIds:["paper-problem"]},
      {id:"evidence-experiments",title:{en:"II · Evidence and experiments",zh:"第二章 · 证据与实验"},question:{en:"Which staged experiments can establish the intuition, causal mechanism, and practical value?",zh:"哪些分阶段实验能够验证直觉、因果机制和实际价值？"},sourceIds:["paper-experiments"]},
      {id:"narrative-execution",title:{en:"III · Paper narrative and execution roadmap",zh:"第三章 · 论文叙事与执行路线"},question:{en:"How should the contribution ladder, main table, decision tree, and implementation plan fit together?",zh:"贡献阶梯、主表、决策树和实现计划应如何衔接？"},sourceIds:["paper-roadmap"]},
      {id:"review-gates",title:{en:"IV · Review loop and maturity gates",zh:"第四章 · 评审闭环与成熟门槛"},question:{en:"Which objections remain unresolved, and what evidence is required before the direction is mature?",zh:"哪些质疑仍未解决，满足什么证据后方向才算成熟？"},sourceIds:["review-log"]}
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
