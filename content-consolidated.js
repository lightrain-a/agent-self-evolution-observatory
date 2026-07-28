(() => {
  const pages = window.PAGE_CONTENT || {};
  const sourceIds = [
    "foundations", "taxonomy",
    "model-improvement", "prompt-evolution", "memory-evolution", "tool-evolution", "workflow-evolution",
    "visual-multimodal", "gui-web", "embodied-world",
    "evaluation-safety", "datasets-benchmarks", "repositories",
    "coverage-method", "bibliography",
    "research-directions", "research-agenda",
    "paper-ideas", "direction-board",
    "paper-problem", "paper-experiments", "paper-roadmap", "review-log"
  ];
  const sources = {};
  sourceIds.forEach((id) => { if (pages[id]) sources[id] = pages[id]; });
  window.CONSOLIDATED_SOURCE_PAGES = sources;

  const group = (sourceId, title) => ({ sourceId, config: sources[sourceId], title });

  pages.foundations = {
    eyebrow:{en:"Foundations",zh:"基础总览"},
    title:{en:"Definitions, history, and taxonomy of agent self-evolution",zh:"Agent 自进化的定义、历史与分类体系"},
    lead:{en:"One foundation page now combines the field boundary, the published-paper historical overview, and the four-axis taxonomy that structures the rest of the observatory.",zh:"一个基础页面统一解释领域边界、基于已发表论文的历史全景，以及组织全站内容的四轴分类体系。"},
    callout:{en:"Read this page first: it separates retry and self-correction from persistent evolution, then explains how update surfaces, feedback signals, timescales, and release gates emerged.",zh:"建议从本页开始：先区分重试、自纠错与持久进化，再理解更新对象、反馈信号、时间尺度和发布门控如何形成。"},
    overviewFigure:{src:{en:"agent-self-evolution-history-en.svg",zh:"agent-self-evolution-history-zh.svg"},caption:{en:"Standalone vector overview for paper embedding. Milestones are grouped by method family and state the method action, update target, and feedback signal.",zh:"可直接嵌入论文的独立矢量总览图。正式发表里程碑按方法族组织，并标明核心做法、更新对象与反馈来源。"}},
    renderMode:"merged-hub",
    groups:[group("foundations"), group("taxonomy")]
  };

  pages.mechanisms = {
    eyebrow:{en:"Mechanisms",zh:"进化机制"},
    title:{en:"How agents evolve: parameters, prompts, memory, skills, and workflows",zh:"Agent 如何进化：参数、提示词、记忆、技能与工作流"},
    lead:{en:"A unified mechanism atlas organized by the persistent object being changed, the learning signal, the commitment gate, and the dominant failure mode.",zh:"按照被持久修改的对象、学习信号、提交门控和主要失败模式组织的统一机制图谱。"},
    callout:{en:"The five mechanism families are adjacent, not interchangeable. A good paper must state which surface changes and why a smaller intervention is insufficient.",zh:"五类机制彼此相邻但不可混用。可信论文必须说明究竟更新哪个表面，以及为什么更小的干预不足。"},
    renderMode:"merged-hub",
    groups:[
      group("model-improvement"), group("prompt-evolution"), group("memory-evolution"),
      group("tool-evolution"), group("workflow-evolution")
    ]
  };

  pages.domains = {
    eyebrow:{en:"Domains",zh:"视觉与交互领域"},
    title:{en:"Visual, GUI/web, and embodied self-evolving agents",zh:"视觉、GUI/Web 与具身自进化 Agent"},
    lead:{en:"Three application domains share multimodal perception and interaction, but differ in state observability, action cost, embodiment, and the evidence needed for persistent improvement.",zh:"三个应用领域都依赖多模态感知与交互，但在状态可观测性、动作成本、具身约束和持久改进证据上存在关键差异。"},
    callout:{en:"The page keeps domain-specific benchmarks and failure modes visible while making their shared visual-memory, tool, world-model, and adaptation mechanisms comparable.",zh:"本页保留各领域特有的基准与失败模式，同时对齐视觉记忆、工具、世界模型和适应机制。"},
    renderMode:"merged-hub",
    groups:[group("visual-multimodal"), group("gui-web"), group("embodied-world")]
  };

  pages.evaluation = {
    eyebrow:{en:"Evaluation & Infrastructure",zh:"评测与研究基础设施"},
    title:{en:"Evaluation, safety, benchmarks, and reproducible infrastructure",zh:"评测、安全、基准与可复现基础设施"},
    lead:{en:"A single evidence page connects longitudinal evaluation, negative evolution, governance, benchmark construction, datasets, environments, repositories, and reproduction readiness.",zh:"一个证据页面统一连接纵向评测、负向进化、安全治理、基准构建、数据环境、代码仓库与复现成熟度。"},
    callout:{en:"Evaluation is not an appendix to self-evolution: the release gate, task stream, statistical unit, and rollback protocol define whether an update counts as genuine improvement.",zh:"评测不是自进化的附录：发布门控、任务流、统计单位和回滚协议共同决定一次更新能否被视为真实改进。"},
    renderMode:"merged-hub",
    resourceModes:["benchmarks","repositories"],
    groups:[group("evaluation-safety"), group("datasets-benchmarks"), group("repositories")]
  };

  if (sources.bibliography) {
    pages.bibliography = Object.assign({}, sources.bibliography, {
      eyebrow:{en:"Literature",zh:"文献与覆盖"},
      title:{en:"Coverage protocol and live bibliography",zh:"覆盖协议与动态文献库"},
      lead:{en:"The search protocol, inclusion boundary, publication-status rules, deduplication audit, interactive maps, and searchable corpus now live on one canonical literature page.",zh:"检索协议、纳入边界、发表状态规则、去重审计、交互地图和可检索语料统一集中在一个文献页面。"},
      groupsBefore:[group("coverage-method")]
    });
  }

  if (sources["research-directions"]) {
    pages["research-directions"] = Object.assign({}, sources["research-directions"], {
      title:{en:"Research directions and long-term agenda",zh:"研究方向地图与长期议程"},
      lead:{en:"Ten stable scientific directions organize the concrete paper ideas; the same page now records the longer-term program, dependencies, and staged research priorities.",zh:"十个稳定科学方向组织具体论文 Idea；同一页面进一步给出长期研究计划、方向依赖和分阶段优先级。"},
      groupsAfter:[group("research-agenda")]
    });
  }

  if (sources["paper-ideas"]) {
    pages["paper-ideas"] = Object.assign({}, sources["paper-ideas"], {
      title:{en:"Concrete paper ideas and decision rankings",zh:"具体论文 Idea 与决策排名"},
      lead:{en:"All thirty-four concrete paper plans, their minimum experiments and stop rules, global ranking, within-direction ranking, and track-specific ranking are now presented together.",zh:"三十四个具体论文方案、最小实验与停止条件，以及总榜、方向内排序和赛道榜统一展示。"},
      includeRanking:true
    });
  }

  pages["selected-paper"] = {
    eyebrow:{en:"Selected Paper Workspace",zh:"选中论文工作区"},
    title:{en:"GroundEvo-Admission: problem, experiments, roadmap, and review",zh:"GroundEvo-Admission：问题、实验、路线图与评审"},
    lead:{en:"The currently selected idea is handled as one complete paper workspace rather than four disconnected pages.",zh:"当前选中的 Idea 以一个完整论文工作区呈现，不再拆成四个相互割裂的页面。"},
    callout:{en:"This workspace is specific to GroundEvo-Admission. Choosing another idea should create a new workspace rather than silently mixing claims and experiments.",zh:"该工作区只服务于 GroundEvo-Admission。若选择其他 Idea，应建立新的工作区，而不是悄悄混合主张和实验。"},
    renderMode:"merged-hub",
    groups:[group("paper-problem"), group("paper-experiments"), group("paper-roadmap"), group("review-log")]
  };
})();
