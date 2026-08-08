(() => {
  const data = () => window.DISCUSSION_READY_IDEAS || { target: 20, count: 0, ready: false, ideas: [] };
  const currentData = () => window.CURRENT_FINAL_IDEAS || { ideas: [] };
  const finalAuditData = () => window.FINAL_ADVISOR_AUDIT || { summary: { pass: 0, revise: 0, block: 0, ready: false }, ideas: [] };
  const collisionData = () => window.FINAL_COLLISION_RECHECK || { ideas: [] };
  const sourceLabels = {
    "main-r2": { zh: "主 ICLR Bank", en: "Main ICLR bank" },
    "v4-r2": { zh: "v4", en: "v4" },
    "v5-r2": { zh: "v5", en: "v5" },
    "v51-r2": { zh: "v5.1", en: "v5.1" },
    "v52-r2": { zh: "v5.2", en: "v5.2" },
    "v53-r2": { zh: "v5.3", en: "v5.3" },
    "r32-final": { zh: "当前最终版", en: "Current final" },
  };
  const clusters = [
    {
      id: "reliable-updates",
      title: { zh: "A · 可靠更新、组合冲突与长期维护", en: "A · Reliable updates, composition, and long-term maintenance" },
      question: { zh: "Agent 持续更新时，如何避免回退、组合冲突和版本债务？", en: "How can persistent agent updates avoid regressions, composition failures, and version debt?" },
      ids: [
        "compositional-update-compatibility",
        "update-trust-region",
        "update-composition-repair-compiler",
        "restoration-clause-induction-v5",
        "update-history-semantic-compactor",
        "certified-out-of-span-interaction-inverter-v53",
      ],
    },
    {
      id: "memory-knowledge",
      title: { zh: "B · 记忆、经验与适用边界", en: "B · Memory, experience, and applicability boundaries" },
      question: { zh: "学到的经验何时应保留、拆分、排序或修复，才能避免负迁移？", en: "When should learned experience be preserved, split, ordered, or repaired to avoid negative transfer?" },
      ids: [
        "contradiction-preserving-consolidation",
        "memory-interaction-clause-learner",
        "monotone-applicability-specializer-v4",
        "nested-pathway-memory-repair",
        "constraint-complete-typed-memory-order-logic",
      ],
    },
    {
      id: "tools-workflows",
      title: { zh: "C · 工具、API 与工作流迁移", en: "C · Tools, APIs, and workflow transfer" },
      question: { zh: "工具/API/工作流变化后，如何把修复迁移成可复用的持久结构？", en: "How can repairs survive tool, API, and workflow changes as reusable persistent structures?" },
      ids: [
        "correction-action-causal-compiler",
        "api-error-semantic-adapter",
        "workflow-repair-grammar-v5",
        "bounded-probe-api-transition-operator",
        "compiler-residual-contract-editor-v53",
      ],
    },
    {
      id: "evaluation-governance",
      title: { zh: "D · 评测、权限与治理", en: "D · Evaluation, permission, and governance" },
      question: { zh: "Agent 版本变化后，测试、评价器与权限治理如何继续可靠？", en: "How can tests, evaluators, and permission governance remain reliable across agent versions?" },
      ids: [
        "probe-mutation-retirement-policy",
        "rubric-intervention-sparse-solver",
        "interventional-permission-triage-under-ceiling",
        "filtered-chronological-evaluator-state-v53",
      ],
    },
  ];

  const label = (source) => sourceLabels[source]?.[language] || source;
  const tx = (value) => textOf(value || "");
  const escText = (value) => esc(String(value || ""));
  const finalFor = (id) => (finalAuditData().ideas || []).find((row) => row.idea_id === id) || { verdict: "pending", revision: "", reviewers: {}, collision_gate: "pending", finding: "" };
  const collisionFor = (id) => (collisionData().ideas || []).find((row) => row.idea_id === id) || { status: "pending", closest_work: [], surviving_difference: "", sources: [] };
  const freshCollisionZh = {
    "contradiction-preserving-consolidation": "当前边界不是一般的矛盾检索或动态图记忆，而是在固定容量下，以 oracle 验证的‘删除后会改变结论’作为 consolidation-time 准入规则，并用交叉删除干预识别其因果价值。",
    "compositional-update-compatibility": "AFlow 等工作主要搜索或生成 Agent workflow；当前边界是对预注册、冻结的 Prompt/工具更新集合预测组合干扰，并用完全相同的图编码器、仅改变 interaction edge feature 来隔离交互信息本身的作用。",
    "update-trust-region": "TeamTR 已在多 Agent 参数微调内部使用 divergence control；当前主张更窄：对异构离散 Agent patch 在提出后使用冻结、非参数行为散度门控，并与等预算 outcome/current-gain/text-edit gate 比较，不主张一般 trust-region 新颖性。",
    "correction-action-causal-compiler": "DoVer、CausalFlow、ANNEAL 已覆盖干预式调试、反事实修复或符号 patch 学习；当前仅主张冻结的最小因果必要 typed-action conjunction，在未见 failure composition 上必须同时胜过单修复检索与等预算 chained-repair 检索。",
    "memory-interaction-clause-learner": "已有方法会选择或重排单条记忆；当前边界是学习并冻结 type-level 兼容／排斥／优先子句，在未见 memory identity 与未见 composition type 上，对比接收相同特征与预算的 pair/triple contextual gate。",
    "probe-mutation-retirement-policy": "mutation-guided suite augmentation 与长期 mutant 管理本身并不新；当前只检验 structural mutation 在相同 learned future-value + diversity selector 之上，是否还能改善 prequential future-regression-recall / execution-cost frontier。",
    "update-composition-repair-compiler": "局部修复、知识复用、可回滚执行轨迹和符号 patch 已被覆盖；当前边界是冻结的 no-test-time-search compiler，能否在 held-out incompatibility-template × update-surface 单元上，以相同 expansion/testing budget 胜过 constrained search。",
    "monotone-applicability-specializer-v4": "SkillAdaptor／SkillTracer 已覆盖 trajectory-driven skill repair；当前不主张一般 skill refinement 新颖性，而只检验在同一冻结 predicate vocabulary 上，monotone、positive-preserving 的适用域收窄是否优于 complexity-matched ILP/rule-list/precondition-only 方法。",
    "api-error-semantic-adapter": "恢复训练、Agent-oriented API 语义设计和结构化 recovery message 已有工作覆盖；当前可发表边界是 learned discrete recovery taxonomy 与等基数 human-designed taxonomy、matched flat classifier 的可识别对照，human design 一旦追平就终止 learned-structure 主张。",
    "workflow-repair-grammar-v5": "Failure-Driven Workflow Refinement 与 HarnessFix 已覆盖 failure-aware graph edit 和 harness attribution/patch；当前只主张冻结 production composition 本身是跨 API×motif transfer 因素，并要求所有控制都在完整 held-out failure distribution 上公平运行。",
    "restoration-clause-induction-v5": "持久 symbolic patch、compatibility 与 rollback governance 已非新颖点；当前主张仅是 explicit no-good/compatibility/precedence clause 相对等资源 direct order-aware composition-risk model 在 unseen composition template 上的归纳偏置优势。",
    "rubric-intervention-sparse-solver": "rubric 生成、改进和 learned rubric design 已有充分工作；当前仅检验 causal atom-effect estimation × sparsity-constrained editing 这一交叉机制，是否在独立 ground-truth ranking 下实现更小偏差且更好保持 neutral dimension。",
    "update-history-semantic-compactor": "versioned memory、rollback 和 trustworthy consolidation 已非常拥挤；当前只主张 typed behavioral-constraint graph 在 non-local/order-sensitive history 上比等资源 semantic-dedup compactor 更能同时保持行为等价与 rollback，而该优势应在 local/commutative history 上显著缩小。",
    "bounded-probe-api-transition-operator": "Agent-First Tool API 与 ProEvolve 已覆盖语义接口和 tool/schema evolution；当前识别比较是：在完全相同 P/E/X 表示、相同 N target probes、相同 compilation/budget 下，cross-source learned parameterization 是否胜过经过质量验证的 non-learned instantiation。",
    "interventional-permission-triage-under-ceiling": "运行时最小权限、commit-time freshness、permission graph、durable authorization consumption 和低权限工具选择都已有工作；当前边界严格收缩为：Agent 更新后、硬权限上限不变时，哪些既有 grant 必须重新授权的等安全、等预算筛选效率。",
    "nested-pathway-memory-repair": "已有工作已研究因果 memory usefulness、memory-induced drift 和 boundary-aware memory selection；当前边界是随机化分解 inclusion/content/rank/co-retrieval 四条 pathway，并做 pathway-specific persistent repair，且必须胜过接收相同结构标签的 direct repair learner。",
    "constraint-complete-typed-memory-order-logic": "neuro-symbolic clause induction 与 order-aware compositional reasoning 本身已有先例；当前只做 representation × decoder factorization：symbolic clause 必须在同一 solver 下胜过 equally expressive typed n-ary factor 的 compositional extrapolation 或 compilation cost，而非声称表达能力不可替代。",
    "certified-out-of-span-interaction-inverter-v53": "null-space／orthogonal-subspace editing 已确立几何原语；当前不主张正交性新颖，而只在 Farkas-certified in-span-infeasible composition failure 上，检验 pure orthogonal repair 是否以同 rank、同预算胜过 mixed-parameterization 与 full-space solver。",
    "compiler-residual-contract-editor-v53": "structural/localized editing 已有充分先例；当前边界是在 deterministic contract compilation 后，对 typed relational edit whitelist 与同监督 generic local-delta editor 做严格匹配，在 model+harness swap 下检验 transfer inductive bias。",
    "filtered-chronological-evaluator-state-v53": "sequential evaluator adaptation、benchmark aging 与在线 judge-vs-system drift attribution 都已有工作；当前只主张冻结 filtered state-space transition 对 zero-anchor future judge version 的外推优于等训练 recurrent chronological control，并由 state×correspondence-corruption interaction 与 inference-only transition-prior ablation 识别。",
  };
  const importanceNotes = {
    "regression-gated-self-evolution": {zh:"直接回答自进化系统最核心的可靠性问题：一次更新的局部收益，不能以牺牲已掌握能力和圈外任务为代价。",en:"Addresses the central reliability problem in self-evolution: a locally useful update must not trade away mastered or out-of-loop capabilities."},
    "contradiction-preserving-consolidation": {zh:"记忆是最低成本、最常用的持久更新表面；如果压缩时丢掉能推翻规则的反证，Agent 会把局部经验固化成系统性负迁移。",en:"Memory is a common low-cost persistent update surface; losing conclusion-changing counterevidence during consolidation can turn local experience into systematic negative transfer."},
    "compositional-update-compatibility": {zh:"真实 Agent 会连续接受多个 Prompt、记忆、技能和工作流更新；单个更新都有效并不保证组合后仍然有效，因此组合稳定性是长期自进化的基础问题。",en:"Real agents accumulate prompt, memory, skill, and workflow updates; individually useful updates need not remain useful when composed, making compositional stability fundamental to long-running evolution."},
    "update-trust-region": {zh:"平均收益无法刻画一次离散 Agent 更新改变行为分布的幅度；若没有可测的行为信赖域，多轮更新很容易在看似有收益时发生隐性漂移。",en:"Average gain does not measure how far a discrete agent update shifts behavior; without a measurable behavioral trust region, multi-round evolution can drift despite apparent gains."},
    "correction-action-causal-compiler": {zh:"反思与自纠错已经很常见，但成功轨迹并不能说明到底是哪一种纠错动作真正必要；若能识别并编译必要纠错动作，就能把一次性修复变成可迁移的持久能力。",en:"Reflection and self-correction are common, but a successful trajectory does not reveal which correction action was necessary; identifying and compiling necessary corrections can turn one-off fixes into transferable persistent capability."},
    "memory-interaction-clause-learner": {zh:"随着记忆库增长，失败越来越可能来自多条记忆共同检索后的相互作用，而不是某一条记忆本身错误；显式学习兼容、排斥和优先关系是可扩展记忆管理的关键。",en:"As memory banks grow, failures increasingly arise from interactions among jointly retrieved memories rather than one bad item; learning compatibility, exclusion, and precedence is central to scalable memory management."},
    "probe-mutation-retirement-policy": {zh:"自进化系统的回归测试也会随版本老化；如果测试集本身不能持续更新，就无法长期判断 Agent 是否真的在进步而不是只适配旧测试。",en:"Regression tests themselves age across agent versions; without an evolving test portfolio, long-running systems cannot tell genuine improvement from adaptation to stale tests."},
    "update-composition-repair-compiler": {zh:"只检测冲突或回滚最后一次更新会浪费已经获得的能力；更有价值的问题是能否自动修复冲突，同时最大化保留已有有效更新。",en:"Detecting a conflict or rolling back the latest update wastes acquired capability; the more consequential question is whether incompatibilities can be repaired while preserving as many useful updates as possible."},
    "monotone-applicability-specializer-v4": {zh:"经验复用的主要风险不是完全错误，而是适用范围过宽；能够只缩小错误边界、同时保持正确区域，是安全持久学习的重要原子能力。",en:"A major risk in experience reuse is over-broad applicability rather than total incorrectness; shrinking only the failing boundary while preserving correct regions is a key primitive for safe persistent learning."},
    "api-error-semantic-adapter": {zh:"Agent 的工具生态会更换 Provider 和 API，即使功能等价，错误语义和恢复动作也可能完全不同；恢复策略不能迁移会直接破坏长期可维护性。",en:"Tool providers and APIs change even when capabilities are equivalent, while error semantics and recovery actions may differ; non-transferable recovery policies undermine long-term maintainability."},
    "workflow-repair-grammar-v5": {zh:"结构化工作流会反复出现相似故障；如果每次仍靠测试时搜索重新修补，就没有真正学会可复用的修复知识。",en:"Structured workflows repeatedly exhibit similar failures; if every repair still requires fresh test-time search, the agent has not learned reusable repair knowledge."},
    "restoration-clause-induction-v5": {zh:"回滚只能解决当前一次故障；把干预结果转成可复用的兼容、禁配和顺序约束，才能避免同类组合回归反复发生。",en:"Rollback solves only the current failure; converting intervention outcomes into reusable compatibility, no-good, and precedence constraints is needed to prevent recurring composition regressions."},
    "rubric-intervention-sparse-solver": {zh:"评价器是自进化的反馈源；若 rubric 本身带有系统偏差，Agent 会稳定地学向错误目标，因此修复评价器等价于修复学习信号。",en:"Evaluators provide the learning signal for self-evolution; systematic rubric bias can drive stable optimization toward the wrong objective, so repairing the evaluator repairs the feedback channel itself."},
    "update-history-semantic-compactor": {zh:"持续更新会积累冗余、遮蔽和顺序依赖，形成版本债务；如果历史不能压缩成行为等价的规范状态，系统复杂度会随轮次持续增长。",en:"Persistent updates accumulate redundancy, shadowing, and order dependencies as version debt; without behavior-preserving canonicalization, system complexity grows with every evolution round."},
    "effect-transport-lesson-specializer-v5": {zh:"同一条经验在不同任务族上可能正迁移也可能负迁移；只有让持久知识本身随效应边界分裂，而不只是测试时 gate，才能真正解决错误泛化。",en:"The same lesson can help one task family and harm another; repairing the persistent knowledge itself by effect-bounded specialization, rather than merely gating at inference, directly addresses negative transfer."},
    "bounded-probe-api-transition-operator": {zh:"跨 API 迁移是实际 Agent 系统的常见维护任务；在目标 API 只允许固定少量 probe 的情况下仍能冻结迁移，才体现真正可复用的语义学习。",en:"API migration is a routine maintenance task for deployed agents; transfer that succeeds after only a fixed number of target probes better demonstrates reusable semantic learning."},
    "interventional-permission-triage-under-ceiling": {zh:"Agent 更新后可达行为会变化，但每次全量重新授权成本很高；在绝不扩大权限上限的前提下只重验高风险 grant，是安全治理与可持续更新之间的关键接口。",en:"Agent updates can change reachable effects while full reauthorization is costly; triaging which existing grants require revalidation without ever expanding authority is a key interface between safety governance and sustainable evolution."},
    "nested-pathway-memory-repair": {zh:"记忆复用失败可能来自是否检索、内容、排序或共同检索等不同因果路径；修错路径会误删有用知识，因此需要机制级归因而非二元 harmful 标签。",en:"Memory reuse can fail through inclusion, content, rank, or co-retrieval pathways; repairing the wrong pathway destroys useful knowledge, motivating mechanism-level attribution rather than a binary harmful-memory label."},
    "constraint-complete-typed-memory-order-logic": {zh:"多条正确记忆共同出现时，执行顺序本身可能决定成败；能够跨未见组合复用变量化约束，是从记忆检索走向系统组合推理的重要一步。",en:"When multiple correct memories co-occur, ordering alone can determine success; reusable variable-bound constraints over unseen compositions move memory systems toward systematic compositional reasoning."},
    "certified-out-of-span-interaction-inverter-v53": {zh:"有些组合回归不是重排已有更新就能修复；如果能先证明旧更新空间中不存在可行解，再学习新的修复方向，就能区分‘组合已有知识’与‘必须产生新知识’。",en:"Some composition regressions cannot be fixed by recombining stored updates; certifying infeasibility in the old update span before learning a new direction distinguishes recombination from genuinely necessary new knowledge."},
    "compiler-residual-contract-editor-v53": {zh:"跨系统迁移中，大部分 schema 转换往往可以确定性完成，真正困难的是少量关系残差；只学习欠定残差能把学习能力集中到最需要的部分，并提高迁移可解释性。",en:"Most schema migration can often be deterministic, while a small relational residual remains underdetermined; learning only that residual concentrates capacity on what truly requires learning and improves interpretability."},
    "filtered-chronological-evaluator-state-v53": {zh:"自进化长期依赖 evaluator，但 evaluator 自身也会随版本漂移；若不区分 Agent 变化和评价标准变化，系统可能把评测漂移误当成学习进步。",en:"Long-running self-evolution depends on evaluators that themselves drift over versions; without separating agent change from evaluator change, the system can mistake evaluation drift for learning progress."},
  };

  function sourceRows(source) {
    if (source === "main-r2") return window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas || [];
    if (source === "v4-r2") return window.IDEA_DISCOVERY_V4?.all_candidates || [];
    if (source === "v5-r2") return window.IDEA_DISCOVERY_V5?.all_candidates || [];
    if (source === "v51-r2") return window.IDEA_DISCOVERY_V51?.children || [];
    if (source === "v52-r2") return window.IDEA_DISCOVERY_V52?.children || [];
    if (source === "v53-r2") return window.IDEA_DISCOVERY_V53?.children || [];
    return [];
  }

  function recordFor(idea) {
    const current = (currentData().ideas || []).find((row) => row.idea_id === idea.id);
    if (current) return current;
    return sourceRows(idea.source).find((row) => row.id === idea.id) || {};
  }

  function recordById(id) {
    const current = (currentData().ideas || []).find((row) => row.idea_id === id);
    if (current) return current;
    const pools = [
      window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas || [],
      window.IDEA_DISCOVERY_V4?.all_candidates || [],
      window.IDEA_DISCOVERY_V5?.all_candidates || [],
      window.IDEA_DISCOVERY_V51?.children || [],
      window.IDEA_DISCOVERY_V52?.children || [],
      window.IDEA_DISCOVERY_V53?.children || [],
    ];
    for (const pool of pools) {
      const hit = pool.find((row) => row.id === id);
      if (hit) return hit;
    }
    return {};
  }

  function latestReview(record) {
    const rows = record.external_reviews || [];
    return rows.length ? rows[rows.length - 1] : {};
  }

  function problemOf(record, depth = 0) {
    const direct = record.purpose || record.real_problem || record.problem;
    if (direct) return tx(direct);
    if (depth < 4) {
      const parentId = record.parent_id || (record.parent_ids || [])[0];
      if (parentId) {
        const parent = recordById(parentId);
        if (parent.id) return problemOf(parent, depth + 1);
      }
    }
    return tx(record.changed_assumption || "");
  }

  function mechanismOf(record) {
    if (record.core_idea) return tx(record.core_idea);
    const object = tx(record.persistent_update_object || record.update_surface || "");
    const why = tx(record.necessity_logic || record.composition_logic || record.material_change || record.changed_assumption || "");
    if (object && why) return language === "zh" ? `把持久学习对象明确为“${object}”：${why}` : `Make “${object}” the persistent learned object: ${why}`;
    return object || why || tx(record.exact_mechanism || "");
  }

  function importanceOf(idea, record) {
    return tx(record.importance || importanceNotes[idea.id] || "");
  }

  function intuitionOf(record, review) {
    const audit = review.combination_audit || {};
    return tx(record.necessity_logic || record.rationale || audit.closed_failure_loop || record.changed_assumption || record.material_change || record.composition_logic || "");
  }

  function learningSignalOf(record) {
    if (record.learning_signal) return tx(record.learning_signal);
    return language === "zh"
      ? "候选更新在隔离 discovery / calibration / regression 划分上的任务结果、成本、安全与回归信号。"
      : "Task outcomes, cost, safety, and regression signals for candidate updates on isolated discovery/calibration/regression splits.";
  }

  function truthOf(record) {
    if (record.independent_ground_truth) return tx(record.independent_ground_truth);
    return tx(record.decisive_metric || record.hypothesis || "");
  }

  function rationaleOf(record) {
    if (record.rationale) return tx(record.rationale);
    const signal = learningSignalOf(record);
    const truth = truthOf(record);
    return language === "zh"
      ? `成立依据来自可干预的学习信号与独立终点分离：方法从“${signal}”学习，但最终是否成立由“${truth}”判定，避免用同一个 Judge 自证。`
      : `The rationale is separation between intervention-derived learning signals and an independent endpoint: the method learns from “${signal}” but is judged by “${truth}”, avoiding self-certification by the same judge.`;
  }

  function methodLogicOf(record) {
    return tx(record.method_logic || record.exact_mechanism || record.composition_logic || record.material_change || "");
  }

  function updateObjectOf(record) {
    return tx(record.persistent_update_object || record.update_surface || record.core_idea || "persistent agent update");
  }

  function advantageOf(record, review) {
    if (record.comparative_advantage) return tx(record.comparative_advantage);
    const baseline = baselineOf(record, review);
    const object = updateObjectOf(record);
    const truth = truthOf(record);
    return language === "zh"
      ? `相对“${baseline}”，这里的优势不应来自更多调用或更大容量，而应来自学习并冻结“${object}”，且该对象必须在“${truth}”上带来等预算 baseline 无法复现的收益。`
      : `Relative to “${baseline}”, the advantage must not come from more calls or capacity; it must come from learning and freezing “${object}”, with gains on “${truth}” that the matched-budget baseline cannot reproduce.`;
  }

  function nearestWorkOf(record, review, ideaId = "") {
    const fresh = collisionFor(ideaId || record.idea_id || record.id || "");
    if ((fresh.closest_work || []).length) return fresh.closest_work.slice(0, 5);
    const direct = review.direct_collision || {};
    const rows = record.nearest_work || direct.closest_work || [];
    return rows.map((item) => typeof item === "string" ? item : (item.title || item.name || "")).filter(Boolean).slice(0, 5);
  }

  function collisionOf(record, review, ideaId = "") {
    const fresh = collisionFor(ideaId || record.idea_id || record.id || "");
    if (fresh.surviving_difference) {
      const zhBoundary = freshCollisionZh[ideaId || record.idea_id || record.id || ""] || tx(record.collision_boundary || "") || fresh.surviving_difference;
      return language === "zh"
        ? `2026-08-08 最新碰撞复核：${fresh.status || "pass"}。最接近工作：${(fresh.closest_work || []).join("、")}。当前仍存活的边界：${zhBoundary}`
        : `Fresh 2026-08-08 collision recheck: ${fresh.status || "pass"}. Closest work: ${(fresh.closest_work || []).join(", ")}. Surviving boundary: ${fresh.surviving_difference}`;
    }
    if (record.collision_boundary) return tx(record.collision_boundary);
    const direct = review.direct_collision || {};
    const status = direct.status || "partial";
    const names = nearestWorkOf(record, review, ideaId);
    return language === "zh"
      ? `直接碰撞状态：${status}。最接近工作包括 ${names.join("、") || "已在 R2 中核查的直接工作"}。`
      : `Direct-collision status: ${status}. Closest work includes ${names.join(", ") || "the direct work checked in R2"}.`;
  }

  function methodFlowOf(record) {
    const signal = learningSignalOf(record);
    const object = updateObjectOf(record);
    const mechanism = methodLogicOf(record);
    const truth = truthOf(record);
    return [
      language === "zh" ? `收集／构造学习信号：${signal}` : `Collect/construct the learning signal: ${signal}`,
      language === "zh" ? `执行机制并更新持久对象：${mechanism}` : `Apply the mechanism and update the persistent object: ${mechanism}`,
      language === "zh" ? `冻结更新对象后，在未见任务、组合、版本或 API 上部署：${object}` : `Freeze the updated object and deploy it on unseen tasks, compositions, versions, or APIs: ${object}`,
      language === "zh" ? `用独立真值而非训练反馈判定：${truth}` : `Judge with independent ground truth rather than the training feedback: ${truth}`,
    ];
  }

  function baselineOf(record, review) {
    const simplification = review.simplification_challenge || {};
    return tx(record.strongest_baseline || record.simplest_baseline || review.strongest_baseline || simplification.simplest_equivalent_method || "");
  }

  function pilotOf(record, review) {
    return tx(record.decisive_pilot || record.pilot || review.decisive_pilot || "");
  }

  function stopOf(record, review) {
    return tx(record.stop_condition || review.stop_rule || "");
  }

  function boundaryOf(record, review) {
    const localized = window.localizedReviewFinding ? window.localizedReviewFinding(record.id, review, language) : "";
    if (localized) return localized;
    if (language === "zh") return review.finding_zh || record.external_finding_zh || review.finding || record.external_finding || tx(record.collision_boundary || "");
    return review.finding || record.external_finding || review.finding_zh || record.external_finding_zh || tx(record.collision_boundary || "");
  }

  function budgetOf(record) {
    const b = record.budget || {};
    if (!b.max_gpus && !b.gpu_hours) return "";
    return `${b.max_gpus || 0} GPU · ${b.gpu_hours || 0}h`;
  }

  function card(idea, index) {
    const record = recordFor(idea);
    const review = latestReview(record);
    const problem = problemOf(record);
    const mechanism = mechanismOf(record);
    const importance = importanceOf(idea, record);
    const intuition = intuitionOf(record, review);
    const rationale = rationaleOf(record);
    const logic = methodLogicOf(record);
    const advantage = advantageOf(record, review);
    const baseline = baselineOf(record, review);
    const pilot = pilotOf(record, review);
    const stop = stopOf(record, review);
    const truth = truthOf(record);
    const nearest = nearestWorkOf(record, review, idea.id);
    const flow = methodFlowOf(record);
    const budget = budgetOf(record);
    const finalAudit = finalFor(idea.id);
    const finalVerdict = String(finalAudit.verdict || "pending").toLowerCase();
    const revision = finalAudit.revision || idea.revision || record.revision || "R3.1";
    const finalFinding = language === "zh"
      ? (tx(record.r3_repair_summary || "") || `当前 ${revision} 版本已通过 GLM-5.2 与 DeepSeek V4 Pro 独立复审，并通过 2026-08-08 最新 primary-source 碰撞复核。`)
      : (finalAudit.finding || tx(record.r3_repair_summary || "") || `The current ${revision} version passed independent GLM-5.2 and DeepSeek V4 Pro review plus the fresh 2026-08-08 primary-source collision recheck.`);
    const remainingRisk = tx(record.remaining_risk || "");
    const reviewerState = finalAudit.reviewers || { "glm-5.2": finalAudit["glm-5.2"], "deepseek-v4-pro": finalAudit["deepseek-v4-pro"] };
    const reviewerLine = Object.entries(reviewerState).filter(([, verdict]) => verdict).map(([name, verdict]) => `${name} ${String(verdict || "pending").toUpperCase()}`).join(" · ");
    const survivingClaim = tx(record.surviving_claim || "");
    return `<details class="discussion-idea-card r3-card-${escText(finalVerdict)}" id="discussion-${escText(idea.id)}">
      <summary><div><span class="discussion-pass-badge discussion-r2-badge">R2 provenance</span><span class="discussion-r3-badge r3-${escText(finalVerdict)}">${escText(revision)} FINAL ${escText(finalVerdict.toUpperCase())}</span><b>${tx(idea.title)}</b><small>${label(idea.source)}${budget ? ` · ${escText(budget)}` : ""}</small></div><p><strong>${language === "zh" ? "问题" : "Problem"}</strong>${escText(problem)}</p></summary>
      <div class="discussion-idea-body">
        <section class="discussion-r3-gate r3-${escText(finalVerdict)}"><div class="discussion-r3-gate-head"><b>${language === "zh" ? "最终师兄讨论门槛" : "Final pre-advisor gate"}</b><span>${escText(revision)} · ${escText(finalVerdict.toUpperCase())}</span></div><p>${escText(finalFinding)}</p><div><strong>${language === "zh" ? "独立复审：" : "Independent review:"}</strong> ${escText(reviewerLine)} · collision ${escText(String(finalAudit.collision_gate || "pending").toUpperCase())}</div>${remainingRisk ? `<div><strong>${language === "zh" ? "剩余风险：" : "Remaining risk:"}</strong> ${escText(remainingRisk)}</div>` : ""}</section>
        <div class="discussion-section-title">${language === "zh" ? "一 · 研究论证" : "I · Research argument"}</div>
        <div class="discussion-argument-grid">
          <section><h4 data-toc="false">${language === "zh" ? "目的／要解决的问题" : "Purpose / problem"}</h4><p>${escText(problem)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "研究重要性" : "Research importance"}</h4><p>${escText(importance)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "核心思想" : "Core idea"}</h4><p>${escText(mechanism)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "核心直觉" : "Core intuition"}</h4><p>${escText(intuition)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "成立依据／合理性" : "Why it is reasonable"}</h4><p>${escText(rationale)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "相对优势" : "Comparative advantage"}</h4><p>${escText(advantage)}</p></section>
        </div>

        <div class="discussion-section-title">${language === "zh" ? "二 · 方法设计" : "II · Method design"}</div>
        <section class="discussion-method-logic"><h4 data-toc="false">${language === "zh" ? "方法逻辑" : "Method logic"}</h4><p>${escText(logic)}</p></section>
        <div class="discussion-method-meta"><div><b>${language === "zh" ? "持久更新对象" : "Persistent update object"}</b><span>${escText(updateObjectOf(record))}</span></div><div><b>${language === "zh" ? "学习信号" : "Learning signal"}</b><span>${escText(learningSignalOf(record))}</span></div></div>
        <section class="discussion-method-flow"><h4 data-toc="false">${language === "zh" ? "方法流程" : "Method flow"}</h4><ol>${flow.map((step) => `<li>${escText(step)}</li>`).join("")}</ol></section>

        <div class="discussion-section-title">${language === "zh" ? "三 · 文献与独立审查" : "III · Literature and independent review"}</div>
        <div class="discussion-review-grid discussion-review-grid-three">
          <section><h4 data-toc="false">${language === "zh" ? "最近工作与碰撞边界" : "Nearest work and collision boundary"}</h4><p>${escText(collisionOf(record, review, idea.id))}</p>${nearest.length ? `<div class="discussion-nearest-work">${nearest.map((name) => `<span>${escText(name)}</span>`).join("")}</div>` : ""}</section>
          <section><h4 data-toc="false">${language === "zh" ? "当前最终可发表边界" : "Current surviving publication claim"}</h4><p>${escText(survivingClaim || boundaryOf(record, review))}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "最强 Baseline／替代方法" : "Strongest baseline / alternative"}</h4><p>${escText(baseline)}</p></section>
        </div>

        <div class="discussion-section-title">${language === "zh" ? "四 · 实验验证" : "IV · Experimental validation"}</div>
        <div class="discussion-validation-grid">
          <section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><p>${escText(pilot)}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "独立真值／主验证信号" : "Independent ground truth / primary validation"}</h4><p>${escText(truth)}</p></section>
          <section class="discussion-stop"><h4 data-toc="false">Stop</h4><p>${escText(stop)}</p></section>
        </div>
      </div>
    </details>`;
  }

  function orderedClusterIdeas(cluster, allIdeas) {
    const byId = new Map(allIdeas.map((idea) => [idea.id, idea]));
    return cluster.ids.map((id) => byId.get(id)).filter(Boolean);
  }

  window.renderDiscussionReviewGuide = function renderDiscussionReviewGuide() {
    const d = data();
    const s = finalAuditData().summary || d.final_summary || { pass: 0, revise: 0, block: 0, ready: false };
    return `<section class="panel discussion-review-guide"><div class="idea-panel-heading"><div><h3 id="idea-review-reading-guide">${language === "zh" ? "这页怎么审：只看当前 20 个 FINAL PASS 版本" : "How to review this page: only the current 20 FINAL-PASS versions count"}</h3><p class="section-intro">${language === "zh" ? `R2 只保留来源追溯；原始 R3 也只保留历史诊断。当前门槛是修复后的 R3.1/R3.2 页面版本：其中 14 个在 R3.1 获得 GLM-5.2 与 DeepSeek V4 Pro 双 PASS，另外 6 个完成 R3.2 定向修复后再次获得双 PASS；随后 20 个当前版本全部补做 2026-08-08 primary-source collision recheck。最终结果为 ${s.pass || 0} PASS / ${s.revise || 0} REVISE / ${s.block || 0} BLOCK。两个旧 R3 BLOCK 版本已退出师兄讨论池，仅在历史审计中保留。` : `R2 is provenance only, and the original R3 is retained only as a historical diagnostic. The current gate is the repaired R3.1/R3.2 page-facing version: 14 ideas received unanimous GLM-5.2 + DeepSeek V4 Pro PASS at R3.1; the other 6 were surgically repaired at R3.2 and then received unanimous PASS. All 20 current versions then received a fresh 2026-08-08 primary-source collision recheck. Final result: ${s.pass || 0} PASS / ${s.revise || 0} REVISE / ${s.block || 0} BLOCK. The two historical R3-BLOCK versions are retired from the advisor pool but preserved in the audit archive.`}</p></div><strong>FINAL ${s.pass || 0}P · ${s.revise || 0}R · ${s.block || 0}B</strong></div><div class="discussion-reading-steps"><article><span>1</span><b>${language === "zh" ? "先看最终存活边界" : "Read the surviving claim first"}</b><p>${language === "zh" ? "最近工作已经覆盖了什么？当前版本到底只剩哪一个可证伪的机制差异？" : "What is already covered by the closest work, and what falsifiable mechanism difference actually remains?"}</p></article><article><span>2</span><b>${language === "zh" ? "再核问题—机制对齐" : "Check problem–method alignment"}</b><p>${language === "zh" ? "修订后的机制是否仍在解决原问题，而不是为了过审迭代成另一个问题？" : "Does the repaired mechanism still solve the stated problem rather than drifting merely to survive review?"}</p></article><article><span>3</span><b>${language === "zh" ? "最后看决定性 Pilot" : "Finish with the decisive pilot"}</b><p>${language === "zh" ? "最强简化基线、独立真值、冻结学习和等预算是否能一次实验真正证伪主张？" : "Can the strongest simplification, independent truth, frozen learning, and matched budget genuinely falsify the thesis in one experiment?"}</p></article></div><a class="discussion-system-link" href="system-overview.html">${language === "zh" ? "后台数据流、证据图谱与自动化细节见系统设计页 →" : "See the system-design page for backend data flow, evidence graph, and automation →"}</a></section>`;
  };

  window.renderDiscussionReadyPool = function renderDiscussionReadyPool() {
    const d = data();
    const provenance = new Map((d.ideas || []).map((idea) => [idea.id, idea]));
    const finalIds = new Set((finalAuditData().ideas || []).filter((row) => row.verdict === "pass").map((row) => row.idea_id));
    const allIdeas = (currentData().ideas || []).filter((row) => finalIds.has(row.idea_id)).map((row) => {
      const prior = provenance.get(row.idea_id) || {};
      return { ...prior, id: row.idea_id, title: row.title || prior.title || {}, revision: row.revision || prior.revision || "R3.1", source: prior.source || "r32-final" };
    });
    const s = finalAuditData().summary || d.final_summary || { pass: 0, revise: 0, block: 0, ready: false };
    return `<section class="panel discussion-ready-panel"><div class="idea-panel-heading"><div><h3 id="discussion-ready-pool">${language === "zh" ? "师兄讨论池：20 个 FINAL PASS Idea" : "Advisor discussion pool: 20 FINAL-PASS ideas"}</h3><p class="section-intro">${language === "zh" ? "这里不做 shortlist、优先级或 Top-8。只展示真正通过最终门槛的 20 个当前版本，并继续按科学问题分组帮助阅读。每张卡顶部给出 revision、双模型独立复审与最新碰撞门槛；正文展开问题动机、重要性、核心思想、直觉与成立依据、方法逻辑、持久更新对象、最近工作、最强 baseline、决定性 pilot、独立真值和 stop condition。" : "There is no shortlist, priority tier, or Top-8 here. The page shows only the 20 current versions that passed the final gate, grouped solely by scientific question for readability. Each card starts with revision, two-model independent review, and the fresh collision gate, then expands the problem, importance, core idea, intuition/rationale, method logic, persistent update object, closest work, strongest baseline, decisive pilot, independent truth, and stop condition."}</p></div><strong>${s.pass || 0} FINAL PASS</strong></div><div class="discussion-cluster-nav">${clusters.map((cluster) => `<a href="#discussion-cluster-${cluster.id}">${tx(cluster.title)} <span>${orderedClusterIdeas(cluster, allIdeas).length}</span></a>`).join("")}</div><div class="discussion-clusters">${clusters.map((cluster) => { const rows = orderedClusterIdeas(cluster, allIdeas); return `<section class="discussion-cluster" id="discussion-cluster-${cluster.id}"><header><div><h3 data-toc="false">${tx(cluster.title)}</h3><p>${tx(cluster.question)}</p></div><strong>${rows.length}</strong></header><div class="discussion-idea-list">${rows.map(card).join("")}</div></section>`; }).join("")}</div></section>`;
  };
})();
