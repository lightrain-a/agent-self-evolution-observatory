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
    eyebrow:{en:"Start Here · Definition",zh:"开始阅读 · 定义与边界"},
    title:{en:"What is agent self-evolution?",zh:"什么是 Agent 自进化？"},
    lead:{en:"Start here. This page does one job: separate persistent self-evolution from retrying, one-off self-correction, and temporary context adaptation, then give a compact vocabulary and four questions for classifying any system.",zh:"第一次看这个方向从这里开始。本页只做一件事：把“持久自进化”和重试、一次性自纠错、临时上下文适应分开，再给出一套核心名词和四个可以直接判断任何系统的问题。"},
    callout:{en:"A better answer after another retry is evidence of search, not evolution. The change must survive the current task boundary and alter later behavior before it enters the self-evolution map.",zh:"多重试一次得到更好答案，只能证明搜索更充分；只有变化跨过当前任务边界仍被保留，并继续改变后续行为，才进入自进化的讨论范围。"},
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
      title:{en:"Literature library: coverage, field maps, and reading guide",zh:"文献库 · 覆盖、领域地图与阅读指南"},
      lead:{en:"Use this page in four steps: first understand where the corpus comes from and which layers are manually verified; then inspect field density; next choose a reading path; only then search, filter, compare, cite, or export individual records.",zh:"建议按四步使用这页：先看文献从哪里来、哪些层级经过人工核验；再看领域文献分布；然后决定先读哪些论文；最后才进入单篇检索、筛选、比较、引用和导出。"},
      callout:{en:"Publication status, citation count, automatic taxonomy, and paper-specific analysis answer different questions. Published/preprint describes bibliographic status, citations describe historical visibility, automatic tags support navigation, and only source-grounded paper analysis should be used for scientific claims.",zh:"发表状态、引用量、自动分类和单篇论文梳理回答的是四个不同问题：正式发表／预印本只表示书目状态；引用量主要反映历史可见度；自动标签只用于导航；真正写进科研主张的内容仍应回到原文和可核验的一手来源。"},
      groupsBefore:[group("coverage-method")]
    });
  }

  if (sources["research-directions"]) {
    pages["research-directions"] = Object.assign({}, sources["research-directions"], {
      eyebrow:{en:"Field Atlas · Landscape",zh:"领域图谱 · 全景入口"},
      title:{en:"Field landscape: history and research-problem map",zh:"领域全景 · 历史与问题图谱"},
      lead:{en:"This is the field-atlas entry point. Read the historical expansion of update targets first, then the D1–D10 problem map, then continue through three orthogonal views—mechanism, application domain, and evaluation. Current A–G ResearchItems remain a separate live research layer.",zh:"这是领域图谱的总入口。先看 Agent 的更新对象如何从 Prompt / Model 逐步扩展到 Memory、Skill / Tool、Workflow 与 World，再看 D1–D10 研究问题怎样形成；随后从“进化机制、应用场景、评测证据”三个正交切面继续阅读。当前 A–G ResearchItem 仍单独属于实时科研层。"},
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
    eyebrow:{en:"Papers · PaperRegistry",zh:"论文 · PaperRegistry"},
    title:{en:"PaperRegistry: current paper states, evidence, review, and submission gates",zh:"PaperRegistry：当前论文状态、证据、审稿与投稿门禁"},
    lead:{en:"This is the canonical output workspace for every ResearchItem that has entered paper writing. PaperRegistry reads the append-only Paper Acceptance Ledger, so evidence sufficiency, scientific HOLD, manuscript repair, review, QA, prebuttal, and true Submission Ready are kept distinct. STRI and Agent Safety are currently registered; research discovery and experiment authority remain in the Research Portfolio.",zh:"这是所有已经进入论文阶段 ResearchItem 的 canonical 输出工作区。PaperRegistry 直接读取 append-only Paper Acceptance Ledger，把“科研证据够不够”“是否仍有科学 HOLD”“文稿修复到哪一步”“审稿/QA/Prebuttal 是否通过”“是否真正 Submission Ready”分开记录。当前已经注册 STRI 与 Agent Safety；新 Idea 与实验权限仍统一留在 Research Portfolio。"},
    callout:{en:"Current canonical state: both STRI and the bounded Agent Safety R9 paper are scientifically READY and have reached SUBMISSION_READY. Agent Safety closed its recorded evidence hold with the preregistered same-schedule no-update control (8/12 updated branches versus 4/12 base-workflow branches; paired discordance 4 update-only to 0 control-only), then passed Story Search, both Mock PC modes, Targeted Repair, Claim Audit, 9/9 Manuscript CI, PDF QA, and a 10-objection Prebuttal. The broader G-1 replication/support research program remains HOLD. Automatic scientific, experiment, GPU, and submission authority remain zero, so SUBMITTED still requires external human action.",zh:"当前 canonical 状态：STRI 与边界冻结的 Agent Safety R9 论文都已经达到科学 READY / SUBMISSION_READY。Agent Safety 用预注册的同 schedule no-update 对照关闭了原先的证据 HOLD：updated-workflow 为 8/12 个 first-violation branch，base-workflow 为 4/12，配对 discordance 为 4 个 update-only、0 个 control-only；随后完成 Story Search、双模式 Mock PC、Targeted Repair、Claim Audit、9/9 Manuscript CI、PDF QA 与覆盖 10 个 decision-critical objection 的 Prebuttal。更宽的 G-1 复现/支持研究线仍保持 HOLD。论文工作流的科学、实验、GPU 与自动投稿权限全部为 0，因此 SUBMITTED 仍必须由外部人工真实提交触发。"},
    renderMode:"selected-paper-current",
    chapters:chaptersFor("selected-paper")
  };
})();
