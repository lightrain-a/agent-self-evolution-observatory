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
      lead:{en:"Ten stable scientific directions organize the field. Historical idea lineages explain how the search evolved; the current STRI paper, zero-authority positive-residual search, canonical/shadow discovery state, and terminal experiment ledger are synchronized on Paper Ideas and Experiments.",zh:"十个稳定科学方向组织领域结构。历史 Idea 谱系用于解释搜索如何演化；当前 STRI 论文、零权限正向残余搜索、正式/Shadow 问题发现状态与终态实验账本，统一同步到“论文 Idea”和“实验决策”页面。"},
      groupsAfter:[group("research-agenda")]
    });
  }

  if (sources["paper-ideas"]) {
    pages["paper-ideas"] = Object.assign({}, sources["paper-ideas"], {
      title:{en:"ICLR-first current research contracts and terminal decisions",zh:"ICLR 优先：当前研究合同与终态决策"},
      lead:{en:"The canonical page starts from one current-status ledger: STRI is paper-ready after Paper Quality v2 closes with zero evidence debt; canonical live ideas remain zero; the memory positive residual is shadow-only; shadow holds/dead ends and the 27 legacy P0 lifecycle records are shown as separate authority layers. Older candidate banks remain provenance only.",zh:"本页先看统一的“当前状态账本”：STRI 的论文证据质量（Paper Quality v2）已经闭环、证据欠账清零并达到论文就绪；正式活跃 Idea 仍为 0；Memory 正向残余只保留在 Shadow 搜索层；Shadow 暂缓/死路与 27 个历史 P0 生命周期按权限层分开显示。更早候选池仅作溯源。"},
      includeRanking:true
    });
  }

  pages["selected-paper"] = {
    eyebrow:{en:"Selected ICLR Paper · STRI",zh:"当前选中 ICLR 论文 · STRI"},
    title:{en:"STRI: Self-Evolution Should Not Depend on How Skills Are Split",zh:"STRI：技能如何拆分不应影响自进化（Self-Evolution Should Not Depend on How Skills Are Split）"},
    lead:{en:"The current selected paper is STRI. This page starts from its exact paper-ready state, claim boundary, evidence completeness, downloads, and human handoff. The former Regression-Gated Self-Evolution workspace is preserved below as a clearly separated historical archive.",zh:"当前选中论文是 STRI。本页首先展示它精确的论文就绪状态、主张边界、证据完整性、下载与人工提交交接；旧 Regression-Gated Self-Evolution 工作区整体下沉为明确分隔的历史归档。"},
    callout:{en:"Current state: READY_NARROW_ICLR · Paper Quality v2 PASS · N1–N3 3/3 supported · evidence debt 0 · 9/9 main-text pages · anonymous supplement ready. Only human author signoff and OpenReview handoff remain; this asset-first paper-ready state does not create canonical Problem-Gate, Method, P0, or GPU authority.",zh:"当前状态：READY_NARROW_ICLR · 论文证据质量 v2 通过 · N1–N3 3/3 已支持 · 证据欠账 0 · 正文 9/9 页 · 匿名补充材料就绪。当前只剩作者责任确认与 OpenReview 提交交接；该“工件优先（Asset-first）”论文就绪状态不会创建正式问题门、方法、P0 或 GPU 权限。"},
    renderMode:"selected-paper-current",
    chapters:chaptersFor("selected-paper")
  };
})();
