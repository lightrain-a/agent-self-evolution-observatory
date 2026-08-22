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
    eyebrow:{en:"Field Atlas · Definition & Boundary",zh:"领域图谱 · 定义与边界"},
    title:{en:"What is agent self-evolution?",zh:"什么是 Agent 自进化？"},
    lead:{en:"Start here. This page does one job: separate persistent self-evolution from retrying, one-off self-correction, and temporary context adaptation, then give a compact vocabulary and four questions for classifying any system.",zh:"第一次看这个方向从这里开始。本页只做一件事：把“持久自进化”和重试、一次性自纠错、临时上下文适应分开，再给出一套核心名词和四个可以直接判断任何系统的问题。"},
    callout:{en:"A better answer after another retry is evidence of search, not evolution. The change must survive the current task boundary and alter later behavior before it enters the self-evolution map.",zh:"多重试一次得到更好答案，只能证明搜索更充分；只有变化跨过当前任务边界仍被保留，并继续改变后续行为，才进入自进化的讨论范围。"},
    renderMode:"merged-hub",
    chapters:chaptersFor("foundations")
  };

  pages.mechanisms = {
    eyebrow:{en:"Field Atlas · Unified Matrix",zh:"领域图谱 · 统一矩阵"},
    title:{en:"Mechanism × domain × evidence: one field matrix for agent self-evolution",zh:"领域矩阵：机制 × 场景 × 评测，一张图读懂 Agent 自进化"},
    lead:{en:"Instead of treating mechanism, application domain, and evaluation as three separate mini-surveys, this page connects them. First identify the persistent update surface, then the environment constraints, then the evidence required to call the change a genuine improvement.",zh:"不再把“进化机制、应用场景、评测证据”拆成三个低密度小综述。本页把它们直接连起来：先判断 Agent 持久改了什么，再看环境带来哪些约束，最后检查什么证据才足以称为真正改进。"},
    callout:{en:"Read every result as one tuple: update surface × environment × evidence. A mechanism is not strong in the abstract; its value depends on what can be observed and reset, what failures cost, and whether future gains survive regression and safety checks.",zh:"任何结果都按一个三元组来读：更新对象 × 环境约束 × 证据标准。机制本身没有脱离场景的“绝对强弱”；能观察什么、能否重置、错误代价多大，以及未来收益能否通过回退与安全检查，都会改变结论。"},
    renderMode:"field-matrix",
    chapters:chaptersFor("mechanisms")
  };

  pages.domains = {
    eyebrow:{en:"Field Atlas · Application Domains",zh:"领域图谱 · 应用场景"},
    title:{en:"Application domains: multimodal, GUI/web, and embodied agents",zh:"应用场景图谱：多模态、GUI/Web 与具身 Agent"},
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
      eyebrow:{en:"Literature · Evidence Library",zh:"文献 · 证据库"},
      title:{en:"Literature library: published spine, idea-mining gaps, and full corpus",zh:"文献库 · 正式发表主线、研究空白与完整语料"},
      lead:{en:"Read the peer-reviewed spine first: start from the four lifecycle questions, see how concrete simple baselines evolved, compare published papers within the same problem, then convert covered territory, repeated failures, and interface gaps into an idea-mining search space. Only after that bring the preprint frontier back through the full maps and searchable corpus.",zh:"建议先用正式发表论文把领域读懂：从四个自进化生命周期问题进入，看简单方法怎样逐步演化，再在同一研究问题下横向比较正式论文；第三步把“已经做掉的主线、反复失败点、成熟方向之间的接口断层”整理成后续找新研究问题的搜索空间；最后才把预印本前沿放回来做最新碰撞检索。"},
      callout:{en:"A literature gap is not automatically an idea. The idea-mining layer first marks crowded motifs as exclusions, then records surviving failures, nearest published work, search terms, and a seven-field candidate contract. Nothing in this page can promote a gap into ResearchItem without the normal novelty and evidence gates.",zh:"文献空白不会自动升级成候选研究问题。Research Gap Mining 层先把已经拥挤的套路标成排除项，再记录真正还没解决的失败、最近正式工作、后续检索关键词和 7 项候选合同；它只负责缩小搜索空间，不会绕过正常 novelty / evidence gate 自动生成或晋级 ResearchItem。"},
      groupsBefore:[group("coverage-method")]
    });
  }

  if (sources["research-directions"]) {
    pages["research-directions"] = Object.assign({}, sources["research-directions"], {
      eyebrow:{en:"Field Atlas · Landscape",zh:"领域图谱 · 全景入口"},
      title:{en:"Field landscape: history and research-problem map",zh:"领域全景 · 历史与问题图谱"},
      lead:{en:"This is the field-atlas entry point. Read one compact historical spine, compare D1–D10 in a single problem table, then move to the unified mechanism × domain × evidence matrix. Current A–G ResearchItems remain a separate live research layer.",zh:"这是领域图谱的总入口。先用一条紧凑历史主线理解更新对象怎样扩展，再在一张表里横向比较 D1–D10；如果要判断一个具体方法，就进入“机制 × 场景 × 评测”统一矩阵。当前 A–G ResearchItem 仍单独属于实时科研层。"},
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
    eyebrow:{en:"Papers · read the science first",zh:"论文 · 先读科学结论"},
    title:{en:"PaperRegistry: what the five papers study, how strong the evidence is, and what remains",zh:"PaperRegistry：5 篇论文在研究什么、证据有多强、还差什么"},
    lead:{en:"Start with the five-paper comparison, then open each paper for its question, novelty boundary, method, strongest evidence, reviewer concerns, limitations, and next step. PaperState, ledger receipts, hashes, and the 12-stage workflow remain available in collapsed audit sections rather than occupying the first reading layer.",zh:"先用顶部横向表比较 5 篇论文，再进入每篇看“研究问题 → 新意边界 → 方法 → 最强证据 → 审稿关注 → limitation → 下一步”。PaperState、ledger receipt、hash 与 12-stage workflow 仍完整保留，但默认折叠到审计层，不再占第一阅读层。"},
    callout:{en:"Paper quality and scientific evidence are deliberately shown as separate axes. A paper can retain meaningful scientific evidence while a later manuscript/reviewer audit reopens paper repair. For example, Temporal Skills has direct three-arm source-native evidence with explicit negative boundaries, while Failure-Memory Provenance has a strong motivating association but an unresolved matched-swap causal sign. The live PaperRegistry below is authoritative for the current paper-quality gate; real submission remains a human-author action.",zh:"这里刻意把“科学证据有多强”和“论文质量门是否通过”分开显示：一篇论文可以保留有意义的科学证据，同时被更晚的成稿/审稿复核重新打开 paper repair。例如 Temporal Skills 已有三臂 source-native 证据并明确报告负边界；Failure-Memory Provenance 则是动机性关联很强、matched-swap 的 causal sign 仍未决。下面实时 PaperRegistry 才是当前论文质量门的真值；真实投稿仍由作者人工完成。"},
    renderMode:"selected-paper-current",
    chapters:chaptersFor("selected-paper")
  };
})();
