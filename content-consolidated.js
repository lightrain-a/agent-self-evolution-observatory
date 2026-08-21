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
    lead:{en:"Start here if you are new to the topic. The page first defines the minimum condition for agent self-evolution, then shows the main historical milestones, and finally gives four questions you can use to classify any system.",zh:"如果第一次看这个方向，建议从这里开始。本页先说明什么条件下才能称为 Agent 自进化，再按时间梳理主要论文，最后给出四个可以直接用来判断任何系统的分类问题。"},
    callout:{en:"The key distinction is simple: a better answer after another retry is not enough. A change must persist beyond the current task and still affect later tasks before we call it evolution.",zh:"最重要的区别很简单：多重试一次得到更好答案还不算进化。只有变化在当前任务结束后仍被保存，并继续影响后续任务，才算持久自进化。"},
    overviewFigure:{src:{en:"agent-self-evolution-history-en.svg",zh:"agent-self-evolution-history-zh.svg"},caption:{en:"Standalone vector overview for paper embedding. Milestones are grouped by method family and state the method action, update target, and feedback signal.",zh:"可直接嵌入论文的独立矢量总览图。正式发表里程碑按方法族组织，并标明核心做法、更新对象与反馈来源。"}},
    renderMode:"merged-hub",
    chapters:chaptersFor("foundations")
  };

  pages.mechanisms = {
    eyebrow:{en:"Mechanisms",zh:"进化机制"},
    title:{en:"How agents evolve: parameters, prompts, memory, skills, and workflows",zh:"Agent 如何进化：参数、提示词、记忆、技能与工作流"},
    lead:{en:"This page compares five concrete ways an agent can change itself: update model parameters, rewrite prompts, store or revise memory, create or modify skills/tools, or change the workflow that coordinates them.",zh:"本页比较 Agent 改变自己的五种具体方式：更新模型参数、改写提示词、写入或修订记忆、创建或修改技能/工具，以及改变这些组件如何协作的工作流。"},
    callout:{en:"For each mechanism, look for three things: what state is actually changed, what evidence justifies keeping the change, and what simpler update would solve the same problem with less cost or risk.",zh:"看每种机制时重点问三件事：到底改了什么状态、凭什么证据保留这次修改、是否存在成本和风险更低但能解决同一问题的更简单更新。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("mechanisms")
  };

  pages.domains = {
    eyebrow:{en:"Domains",zh:"视觉与交互领域"},
    title:{en:"Visual, GUI/web, and embodied self-evolving agents",zh:"视觉、GUI/Web 与具身自进化 Agent"},
    lead:{en:"The same update can behave very differently in images, web interfaces, and robots. This page compares what each agent can observe, what actions it can take, how costly a wrong action is, and whether the environment provides exact state for evaluation.",zh:"同一种更新方法放到图像、网页和机器人上，效果可能完全不同。本页比较三类 Agent 能观察到什么、能执行什么动作、错误动作代价多大，以及评测时能否拿到精确环境状态。"},
    callout:{en:"Use the comparison to decide whether a result really transfers across domains. A method that works because a GUI can be reset exactly may not transfer unchanged to a physical robot with irreversible actions.",zh:"这张对照表用来判断实验结果能否真的跨领域迁移。例如，依赖 GUI 精确重置的方法，不能默认直接迁移到动作不可逆的实体机器人。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("domains")
  };

  pages.evaluation = {
    eyebrow:{en:"Evaluation & Infrastructure",zh:"评测与研究基础设施"},
    title:{en:"Evaluation, safety, benchmarks, and reproducible infrastructure",zh:"评测、安全、基准与可复现基础设施"},
    lead:{en:"This page explains how to prove that an update is genuinely useful: test later tasks, measure damage to earlier tasks, count harmful updates, report recovery after rollback, and keep the data, environments, code, and statistical unit explicit.",zh:"本页说明怎样证明一次更新真的有用：测试后续任务、测量对旧任务的伤害、统计有害更新、报告回滚后的恢复情况，并明确写清数据、环境、代码和统计单位。"},
    callout:{en:"An update should not be called an improvement just because the current task score rises. The evaluation must also show what happens to future tasks, old capabilities, safety, cost, and recovery.",zh:"不能因为当前任务分数提高就把更新称为改进。至少还要说明它对后续任务、旧能力、安全性、成本和回滚恢复分别产生了什么影响。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("evaluation")
  };

  if (sources.bibliography) {
    pages.bibliography = Object.assign({}, sources.bibliography, {
      eyebrow:{en:"Literature",zh:"文献与覆盖"},
      title:{en:"Coverage protocol and live bibliography",zh:"覆盖协议与动态文献库"},
      lead:{en:"This page shows exactly how the literature list is built: which queries are used, which papers are included or excluded, how duplicate preprint/published versions are merged, when records were last updated, and where to search or export the resulting corpus.",zh:"本页具体说明文献库怎样产生：用了哪些检索词、哪些论文会纳入或排除、预印本与正式版本怎样去重合并、记录何时更新，以及怎样搜索或导出最终文献表。"},
      groupsBefore:[group("coverage-method")]
    });
  }

  if (sources["research-directions"]) {
    pages["research-directions"] = Object.assign({}, sources["research-directions"], {
      title:{en:"Research directions and long-term agenda",zh:"研究方向地图与长期议程"},
      lead:{en:"The page groups the field into ten long-term research questions. For each direction it shows the motivating failure, representative papers, what a new paper would still need to prove, and whether that direction is part of our current research program or only a longer-term option.",zh:"本页把领域整理为十个长期研究问题。每个方向都会写清楚它由什么具体失败推动、有哪些代表论文、新论文还必须证明什么，以及它属于当前研究计划还是仅作为长期备选。"},
      groupsAfter:[group("research-agenda")]
    });
  }

  if (sources["paper-ideas"]) {
    pages["paper-ideas"] = Object.assign({}, sources["paper-ideas"], {
      title:{en:"Research Portfolio: ideas, experiments, evidence, and decisions",zh:"研究组合：Idea、实验、证据与当前决策"},
      lead:{en:"This is the canonical workspace before paper writing. Research is grouped by A–G scientific themes, and every ResearchItem keeps the problem, proposed mechanism, strongest same-information baseline, experiment/evidence trail, current scientific decision, execution authority, and reopen condition together. Historical P0 is a milestone inside the item—not a separate queue.",zh:"这是进入论文阶段之前的统一科研工作区。所有研究按 A–G 科学问题大类组织；每个 ResearchItem 在同一张卡里串起问题、候选机制、最强同信息简单对照、实验/证据轨迹、当前科学结论、执行权限和重开条件。历史 P0 只是 ResearchItem 内的里程碑，不再是一张平行实验队列。"},
      includeRanking:true
    });
  }

  pages["selected-paper"] = {
    eyebrow:{en:"Papers · STRI",zh:"论文 · STRI"},
    title:{en:"STRI: Self-Evolution Should Not Depend on How Skills Are Split",zh:"STRI：技能如何拆分不应影响自进化（Self-Evolution Should Not Depend on How Skills Are Split）"},
    lead:{en:"This is the PaperState workspace for research that has already passed into writing. It only manages STRI's supported and excluded claims, claim–evidence mapping, manuscript figures, QA, supplement, release artifacts, and submission handoff. Research discovery, stopped ideas, and experiment queues remain in the Research Portfolio.",zh:"这是已经通过科研阶段、进入论文阶段后的 PaperState 工作区。这里只管理 STRI 的支持/排除主张、主张—证据映射、论文图表、文稿 QA、补充材料、发布工件和投稿交接。新 Idea、停止方向和实验运行状态统一留在 Research Portfolio。"},
    callout:{en:"Submission status: all three STRI claims are supported, the evidence checklist has no remaining debt, the main text is within the 9-page limit, and the anonymous supplement is ready. The remaining work is human author/signoff and deadline/account verification before OpenReview submission; no new experiment is required for the current narrow paper.",zh:"投稿状态：STRI 的 3 条主张都有对应证据，证据清单没有未完成项，正文符合 9 页限制，匿名补充材料也已就绪。当前剩余工作是作者责任确认、截止日期和 OpenReview 账号等人工核验；这篇窄范围论文不需要再补新的实验。"},
    renderMode:"selected-paper-current",
    chapters:chaptersFor("selected-paper")
  };
})();
