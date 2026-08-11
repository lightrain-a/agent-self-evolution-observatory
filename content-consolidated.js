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
  const architecture = (pageId) => (window.PAGE_ARCHITECTURES || {})[pageId] || { chapters:[] };
  const chaptersFor = (pageId) => architecture(pageId).chapters.map((chapter) => ({
    ...chapter,
    groups:(chapter.sourceIds || []).map((sourceId) => group(sourceId))
  }));

  pages.foundations = {
    eyebrow:{en:"Foundations",zh:"基础总览"},
    title:{en:"Definitions, history, and taxonomy of agent self-evolution",zh:"Agent 自进化的定义、历史与分类体系"},
    lead:{en:"One foundation page now combines the field boundary, the published-paper historical overview, and the four-axis taxonomy that structures the rest of the observatory.",zh:"一个基础页面统一解释领域边界、基于已发表论文的历史全景，以及组织全站内容的四轴分类体系。"},
    callout:{en:"Read this page first: it separates retry and self-correction from persistent evolution, then explains how update surfaces, feedback signals, timescales, and release gates emerged.",zh:"建议从本页开始：先区分重试、自纠错与持久进化，再理解更新对象、反馈信号、时间尺度和发布门控如何形成。"},
    overviewFigure:{src:{en:"agent-self-evolution-history-en.svg",zh:"agent-self-evolution-history-zh.svg"},caption:{en:"Standalone vector overview for paper embedding. Milestones are grouped by method family and state the method action, update target, and feedback signal.",zh:"可直接嵌入论文的独立矢量总览图。正式发表里程碑按方法族组织，并标明核心做法、更新对象与反馈来源。"}},
    renderMode:"merged-hub",
    chapters:chaptersFor("foundations")
  };

  pages.mechanisms = {
    eyebrow:{en:"Mechanisms",zh:"进化机制"},
    title:{en:"How agents evolve: parameters, prompts, memory, skills, and workflows",zh:"Agent 如何进化：参数、提示词、记忆、技能与工作流"},
    lead:{en:"A unified mechanism atlas organized by the persistent object being changed, the learning signal, the commitment gate, and the dominant failure mode.",zh:"按照被持久修改的对象、学习信号、提交门控和主要失败模式组织的统一机制图谱。"},
    callout:{en:"The five mechanism families are adjacent, not interchangeable. A good paper must state which surface changes and why a smaller intervention is insufficient.",zh:"五类机制彼此相邻但不可混用。可信论文必须说明究竟更新哪个表面，以及为什么更小的干预不足。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("mechanisms")
  };

  pages.domains = {
    eyebrow:{en:"Domains",zh:"视觉与交互领域"},
    title:{en:"Visual, GUI/web, and embodied self-evolving agents",zh:"视觉、GUI/Web 与具身自进化 Agent"},
    lead:{en:"Three application domains share multimodal perception and interaction, but differ in state observability, action cost, embodiment, and the evidence needed for persistent improvement.",zh:"三个应用领域都依赖多模态感知与交互，但在状态可观测性、动作成本、具身约束和持久改进证据上存在关键差异。"},
    callout:{en:"The page keeps domain-specific benchmarks and failure modes visible while making their shared visual-memory, tool, world-model, and adaptation mechanisms comparable.",zh:"本页保留各领域特有的基准与失败模式，同时对齐视觉记忆、工具、世界模型和适应机制。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("domains")
  };

  pages.evaluation = {
    eyebrow:{en:"Evaluation & Infrastructure",zh:"评测与研究基础设施"},
    title:{en:"Evaluation, safety, benchmarks, and reproducible infrastructure",zh:"评测、安全、基准与可复现基础设施"},
    lead:{en:"A single evidence page connects longitudinal evaluation, negative evolution, governance, benchmark construction, datasets, environments, repositories, and reproduction readiness.",zh:"一个证据页面统一连接纵向评测、负向进化、安全治理、基准构建、数据环境、代码仓库与复现成熟度。"},
    callout:{en:"Evaluation is not an appendix to self-evolution: the release gate, task stream, statistical unit, and rollback protocol define whether an update counts as genuine improvement.",zh:"评测不是自进化的附录：发布门控、任务流、统计单位和回滚协议共同决定一次更新能否被视为真实改进。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("evaluation")
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
      lead:{en:"Ten stable scientific directions organize the field. The historical idea lineage explains how the search evolved, while the 20 current FINAL-PASS contracts and all current experiment decisions live on Paper Ideas and Experiments respectively.",zh:"十个稳定科学方向组织领域结构。历史 Idea 谱系解释搜索如何演化；20 个当前 FINAL-PASS 合同与所有当前实验决策分别由 Paper Ideas 和 Experiments 负责。"},
      groupsAfter:[group("research-agenda")]
    });
  }

  if (sources["paper-ideas"]) {
    pages["paper-ideas"] = Object.assign({}, sources["paper-ideas"], {
      title:{en:"ICLR-first current research contracts and terminal decisions",zh:"ICLR-first 当前研究合同与终态决策"},
      lead:{en:"The canonical page now centers the 20 current FINAL-PASS formulations and their human-terminal/P0 contracts. Earlier 26-idea R1/R2 banks, advisor rankings, and visual specialization rounds are retained only as provenance for how the current contracts were produced.",zh:"规范页面现在以 20 个当前 FINAL-PASS 表述及其人工终态/P0 合同为主；更早的 26-Idea R1/R2 候选池、导师排序和视觉专门化轮次仅作为形成当前合同的历史溯源。"},
      includeRanking:true
    });
  }

  pages["selected-paper"] = {
    eyebrow:{en:"Historical ICLR Paper Workspace",zh:"历史 ICLR 论文工作区"},
    title:{en:"Regression-Gated Self-Evolution: archived formulation, protocol, and failure evidence",zh:"Regression-Gated Self-Evolution：归档表述、实验协议与失败证据"},
    lead:{en:"This archived workspace preserves the original constrained-improvement formulation and proposed matched-budget protocol so later STOP evidence can be interpreted against the exact claim that was being tested. It is not the current selected paper or an active execution plan.",zh:"本历史工作区保留当时的受约束改进表述与拟定的等预算协议，方便把后续 STOP 证据对应回最初被检验的精确主张；它不再代表当前选中论文或活跃执行计划。"},
    callout:{en:"Current decision: the Regression-Gated formulation is stopped under the unified experiment ledger. Keep this page only as provenance; use Paper Ideas for current research contracts and Experiments for current execution decisions.",zh:"当前决策：Regression-Gated formulation 已在统一实验账本中停止。本页只保留为溯源档案；当前研究合同请看 Paper Ideas，当前执行结论请看 Experiments。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("selected-paper")
  };
})();
