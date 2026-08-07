(() => {
  const data = () => window.DISCUSSION_READY_IDEAS || { target: 20, count: 0, ready: false, ideas: [] };
  const sourceLabels = {
    "main-r2": { zh: "主 ICLR Bank", en: "Main ICLR bank" },
    "v4-r2": { zh: "v4", en: "v4" },
    "v5-r2": { zh: "v5", en: "v5" },
    "v51-r2": { zh: "v5.1", en: "v5.1" },
    "v52-r2": { zh: "v5.2", en: "v5.2" },
    "v53-r2": { zh: "v5.3", en: "v5.3" },
  };
  const clusters = [
    {
      id: "reliable-updates",
      title: { zh: "A · 可靠更新、组合冲突与长期维护", en: "A · Reliable updates, composition, and long-term maintenance" },
      question: { zh: "Agent 持续更新时，如何避免回退、组合冲突和版本债务？", en: "How can persistent agent updates avoid regressions, composition failures, and version debt?" },
      ids: [
        "regression-gated-self-evolution",
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
        "effect-transport-lesson-specializer-v5",
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
    return sourceRows(idea.source).find((row) => row.id === idea.id) || {};
  }

  function recordById(id) {
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
    return tx(record.core_idea || record.exact_mechanism || record.composition_logic || record.material_change || "");
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
    if (record.collision_boundary) return tx(record.collision_boundary);
    if (language === "zh") return review.finding_zh || record.external_finding_zh || review.finding || record.external_finding || "";
    return review.finding || record.external_finding || review.finding_zh || record.external_finding_zh || "";
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
    const budget = budgetOf(record);
    return `<details class="discussion-idea-card" id="discussion-${escText(idea.id)}">
      <summary><div><span class="discussion-pass-badge">R2 PASS</span><b>${tx(idea.title)}</b><small>${label(idea.source)}${budget ? ` · ${escText(budget)}` : ""}</small></div><p><strong>${language === "zh" ? "问题" : "Problem"}</strong>${escText(problem)}</p></summary>
      <div class="discussion-idea-body">
        <section class="discussion-key-mechanism"><h4 data-toc="false">${language === "zh" ? "核心机制" : "Core mechanism"}</h4><p>${escText(mechanism)}</p></section>
        <div class="discussion-review-grid">
          <section><h4 data-toc="false">${language === "zh" ? "为什么能通过 R2" : "Why it passed R2"}</h4><p>${escText(boundaryOf(record, review))}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "最强替代方法" : "Strongest alternative"}</h4><p>${escText(baselineOf(record, review))}</p></section>
          <section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><p>${escText(pilotOf(record, review))}</p></section>
          <section><h4 data-toc="false">Stop</h4><p>${escText(stopOf(record, review))}</p></section>
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
    return `<section class="panel discussion-review-guide"><div class="idea-panel-heading"><div><h3 id="idea-review-reading-guide">${language === "zh" ? "这页怎么审：先看最终候选，再看证据" : "How to review this page: final candidates first, evidence second"}</h3><p class="section-intro">${language === "zh" ? "本页只服务于方向讨论，不重复展示完整后台。22 个 Idea 都已通过指定 Agent 项目网页版 ChatGPT 的独立官方来源 R2；R2 PASS 只表示问题、机制与新颖性边界值得进入讨论，并不代表实验结论已经成立。" : "This page is for direction review rather than backend inspection. All 22 ideas already passed independent official-source R2 in the designated Agent-project ChatGPT web review. PASS means the problem, mechanism, and novelty boundary merit discussion; it does not establish the experimental claim."}</p></div><strong>${d.count || 0}/${d.target || 20} R2 PASS</strong></div><div class="discussion-reading-steps"><article><span>1</span><b>${language === "zh" ? "先判断问题" : "Judge the problem"}</b><p>${language === "zh" ? "问题是否真实、重要，而且值得单独写一篇论文？" : "Is the failure real, important, and paper-worthy?"}</p></article><article><span>2</span><b>${language === "zh" ? "再看机制边界" : "Inspect the mechanism boundary"}</b><p>${language === "zh" ? "核心机制是否真的区别于最近工作和最强简化方法？" : "Is the mechanism genuinely distinct from closest work and the strongest simplification?"}</p></article><article><span>3</span><b>${language === "zh" ? "最后看决定性实验" : "Finish with the decisive test"}</b><p>${language === "zh" ? "Pilot 能否用一个主实验直接证伪核心主张，而不是靠很多次要指标？" : "Can one main experiment directly falsify the thesis rather than relying on many secondary metrics?"}</p></article></div><a class="discussion-system-link" href="system-overview.html">${language === "zh" ? "后台数据流、证据图谱与自动化细节见系统设计页 →" : "See the system-design page for backend data flow, evidence graph, and automation →"}</a></section>`;
  };

  window.renderDiscussionReadyPool = function renderDiscussionReadyPool() {
    const d = data();
    const allIdeas = d.ideas || [];
    return `<section class="panel discussion-ready-panel"><div class="idea-panel-heading"><div><h3 id="discussion-ready-pool">${language === "zh" ? "正式讨论池：22 个独立 R2 PASS Idea" : "Formal discussion pool: 22 independently R2-PASS ideas"}</h3><p class="section-intro">${language === "zh" ? "不再按 v4/v5 生成版本阅读，而按科学问题组织。每个卡片使用同一审查顺序：问题 → 核心机制 → R2 通过边界 → 最强替代方法 → 决定性 Pilot → Stop。22 个全部保留，没有额外 shortlist。" : "Ideas are organized by scientific question rather than generation version. Every card follows the same review order: problem → core mechanism → R2 boundary → strongest alternative → decisive pilot → Stop. All 22 remain; there is no extra shortlist."}</p></div><strong>${d.count || 0} PASS</strong></div><div class="discussion-cluster-nav">${clusters.map((cluster) => `<a href="#discussion-cluster-${cluster.id}">${tx(cluster.title)} <span>${orderedClusterIdeas(cluster, allIdeas).length}</span></a>`).join("")}</div><div class="discussion-clusters">${clusters.map((cluster) => { const rows = orderedClusterIdeas(cluster, allIdeas); return `<section class="discussion-cluster" id="discussion-cluster-${cluster.id}"><header><div><h3 data-toc="false">${tx(cluster.title)}</h3><p>${tx(cluster.question)}</p></div><strong>${rows.length}</strong></header><div class="discussion-idea-list">${rows.map(card).join("")}</div></section>`; }).join("")}</div></section>`;
  };
})();
