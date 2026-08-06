(() => {
  const bank = () => window.IDEA_DISCOVERY_V4 || {summary:{},repository_patterns:[],workflow_stages:[],pareto_front_ids:[],tournament_finalists:[],discussion:[],revival:[],repair:[],component:[]};
  const pick4 = (value) => textOf(value || "");
  const latestReview = (idea) => {
    const rows = idea?.external_reviews || [];
    return rows.length ? rows[rows.length - 1] : null;
  };
  const statusLabel = (value) => ({
    discussion:{zh:"讨论短名单",en:"Discussion shortlist"},
    revival:{zh:"条件复活",en:"Conditional revival"},
    repair:{zh:"需要补强",en:"Needs strengthening"},
    component:{zh:"作为组件保留",en:"Retain as component"},
  }[value]?.[language] || value);
  const lineageLabel = (value) => ({
    "new-combination":{zh:"新组合",en:"New composition"},
    revived:{zh:"旧方向复活",en:"Revived direction"},
    merged:{zh:"多父方向合并",en:"Merged parents"},
  }[value]?.[language] || value);
  const parentHref = (id) => {
    const v3 = (window.IDEA_DISCOVERY_V3?.all_children || []).some((row) => row.id === id);
    const v31 = (window.IDEA_DISCOVERY_V31?.children || []).some((row) => row.id === id);
    if (v3 || v31) return "paper-ideas.html#solution-first-v3";
    return `paper-ideas.html#iclr-${esc(id)}`;
  };
  const scoreRows = (idea) => Object.entries(idea.scores || {}).map(([key,value]) => `<div><span>${esc(key.replaceAll("_"," "))}</span><i><b style="width:${Number(value)*20}%"></b></i><strong>${Number(value)}/5</strong></div>`).join("");

  function reviewBlock(idea) {
    const review = latestReview(idea);
    if (!review) return "";
    const verdict = review.verdict || "pending";
    const action = window.localizedReviewAction ? window.localizedReviewAction(idea.id, review, language) : (language === "zh" ? review.required_action_zh || review.required_action : review.required_action);
    const finding = language === "zh" ? (review.finding_zh || review.finding) : review.finding;
    const audit = review.combination_audit || {};
    return `<div class="v4-review verdict-${esc(verdict)}"><header><b>${language === "zh" ? "v4 独立组合审查" : "v4 independent composition audit"}</b><span>${esc(String(verdict).toUpperCase())}</span></header><p>${esc(finding || "")}</p><dl><div><dt>${language === "zh" ? "全部组件必要" : "All atoms necessary"}</dt><dd>${esc(audit.all_atoms_necessary || "unknown")}</dd></div><div><dt>${language === "zh" ? "最简等价基线" : "Simplest equivalent baseline"}</dt><dd>${esc(audit.simplest_equivalent_baseline || review.strongest_baseline || "")}</dd></div></dl>${action ? `<small><b>${language === "zh" ? "审查后要求" : "Required action"}</b>${esc(action)}</small>` : ""}</div>`;
  }

  function ideaCard(idea, index) {
    const review = latestReview(idea);
    const verdict = review?.verdict || "pending";
    const revival = idea.revival_condition ? `<section class="v4-revival-condition"><h4 data-toc="false">${language === "zh" ? "复活条件" : "Revival condition"}</h4><p>${pick4(idea.revival_condition)}</p></section>` : "";
    return `<details id="v4-${esc(idea.id)}" class="v4-idea-card status-${esc(idea.internal_status)} verdict-${esc(verdict)}" ${index < 3 ? "open" : ""}><summary><div><span>#${idea.internal_rank}</span><b>${pick4(idea.title)}</b><small>${statusLabel(idea.internal_status)} · ${lineageLabel(idea.lineage_type)}</small></div><div><em>${verdict === "pending" ? "R2 PENDING" : `R2 ${String(verdict).toUpperCase()}`}</em><strong>${Number(idea.mean_score).toFixed(2)}</strong></div></summary><div class="v4-idea-body">
      <div class="v4-parent-row"><b>${language === "zh" ? "父方向" : "Parents"}</b>${(idea.parent_ids || []).map((id) => `<a href="${parentHref(id)}">${esc(id)}</a>`).join("")}</div>
      <div class="v4-mechanism-atoms"><b>${language === "zh" ? "机制原子" : "Mechanism atoms"}</b>${(idea.mechanism_atoms || []).map((atom) => `<span>${esc(atom)}</span>`).join("")}</div>
      <div class="v4-grid">
        <section><h4 data-toc="false">${language === "zh" ? "真实问题" : "Real problem"}</h4><p>${pick4(idea.real_problem)}</p></section>
        <section class="composition"><h4 data-toc="false">${language === "zh" ? "组合为何必要" : "Why the composition is necessary"}</h4><p>${pick4(idea.composition_logic)}</p><div class="v4-update-surface"><b>${language === "zh" ? "持久更新对象" : "Persistent update object"}</b>${esc(idea.persistent_update_object)}</div></section>
        <section><h4 data-toc="false">${language === "zh" ? "学习信号" : "Learning signal"}</h4><p>${pick4(idea.learning_signal)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "独立真值" : "Independent ground truth"}</h4><p>${pick4(idea.independent_ground_truth)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "最强基线" : "Strongest baseline"}</h4><p>${pick4(idea.strongest_baseline)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><p>${pick4(idea.decisive_pilot)}</p></section>
        <section><h4 data-toc="false">Stop</h4><p>${pick4(idea.stop_condition)}</p></section>
        ${revival}
      </div>
      <div class="v4-assets">${(idea.public_assets || []).map((item) => `<span>${esc(item)}</span>`).join("")}</div>
      <div class="v4-scores">${scoreRows(idea)}</div>
      ${reviewBlock(idea)}
    </div></details>`;
  }

  function group(titleZh, titleEn, rows, tone) {
    return `<section class="v4-group tone-${tone}"><h3 data-toc="false">${language === "zh" ? titleZh : titleEn}<span>${rows.length}</span></h3><div class="v4-list">${rows.map(ideaCard).join("")}</div></section>`;
  }

  window.renderIdeaDiscoveryV4 = function renderIdeaDiscoveryV4() {
    const data = bank();
    const summary = data.summary || {};
    const finalists = data.review_ranked_finalists || data.tournament_finalists || [];
    const reviewedLine = summary.external_reviewed
      ? (language === "zh" ? `R2 已复核 ${summary.external_reviewed}/${summary.tournament_finalists}：${summary.external_pass} PASS、${summary.external_revise} REVISE、${summary.external_block} BLOCK。` : `R2 reviewed ${summary.external_reviewed}/${summary.tournament_finalists}: ${summary.external_pass} PASS, ${summary.external_revise} REVISE, ${summary.external_block} BLOCK.`)
      : (language === "zh" ? `${summary.tournament_finalists || 0} 个 finalists 正在等待独立 R2。` : `${summary.tournament_finalists || 0} finalists are awaiting independent R2.`);
    return `<section class="panel v4-panel"><div class="idea-panel-heading"><div><h3 id="idea-discovery-v4">${language === "zh" ? "Idea Discovery v4：受约束组合与条件复活" : "Idea Discovery v4: constrained composition and conditional revival"}</h3><p class="section-intro">${language === "zh" ? "允许合理组合已有机制，但要求每个组件解决真实失败闭环中的不同必要环节。旧 REVISE/BLOCK 不永久删除；改变关键假设、学习对象、监督或部署边界后可重新进入候选池。" : "Known mechanisms may be composed when each addresses a distinct necessary link in a real failure loop. Earlier REVISE/BLOCK ideas are not permanently deleted; they may return after a material change to assumptions, learned object, supervision, or deployment boundary."}</p></div><strong>${reviewedLine}</strong></div>
      <div class="grid v4-stats"><div class="stat"><b>${summary.repository_patterns || 0}</b><span>${language === "zh" ? "个仓库工作流模式" : "repository patterns"}</span></div><div class="stat"><b>${summary.raw_candidates || 0}</b><span>${language === "zh" ? "个新增候选" : "new candidates"}</span></div><div class="stat"><b>${summary.discussion || 0}</b><span>${language === "zh" ? "讨论短名单" : "discussion"}</span></div><div class="stat"><b>${summary.revival || 0}</b><span>${language === "zh" ? "条件复活" : "revivals"}</span></div><div class="stat"><b>${summary.repair || 0}</b><span>${language === "zh" ? "需要补强" : "repair"}</span></div><div class="stat"><b>${summary.component || 0}</b><span>${language === "zh" ? "组件保留" : "components"}</span></div></div>
      <div class="v4-policy"><b>${language === "zh" ? "组合判据" : "Composition rule"}</b><span>${language === "zh" ? "组合不是原罪。只有当删除任一机制原子后，真实失败闭环仍能在相同数据和预算下被等价解决时，该原子才被判定为冗余。" : "Combination is not disqualifying. An atom is redundant only when removing it leaves an equivalent solution to the real failure loop under the same data and budget."}</span></div>
      <details class="v4-repo-patterns"><summary>${language === "zh" ? `查看 ${summary.repository_patterns || 0} 个自动科研系统工作流来源` : `See ${summary.repository_patterns || 0} automated-research workflow sources`}</summary><div>${(data.repository_patterns || []).map((item) => `<article><header><b>${esc(item.system)}</b><a href="${esc(item.official_repo)}" target="_blank" rel="noopener">GitHub ↗</a></header><p>${pick4(item.pattern)}</p><span>${esc(item.adopted_as)}</span></article>`).join("")}</div></details>
      <section class="v4-flow"><h3 data-toc="false">${language === "zh" ? "v4 数据流" : "v4 data flow"}</h3><div>${(data.workflow_stages || []).map((stage,index) => `<article><span>${esc(stage.id)}</span><b>${pick4(stage.name)}</b><p>${pick4(stage.output)}</p></article>${index < data.workflow_stages.length - 1 ? "<i>→</i>" : ""}`).join("")}</div></section>
      <section class="v4-finalists"><h3 data-toc="false">${language === "zh" ? "R2 排序的锦标赛 finalists" : "Tournament finalists ordered by R2"}<span>${finalists.length}</span></h3><div>${finalists.map((idea) => `<a href="#v4-${esc(idea.id)}"><b>#${idea.external_rank || idea.internal_rank}</b>${pick4(idea.title)}<small>R1 #${idea.internal_rank} · ${idea.external_verdict === "pending" ? "R2 pending" : String(idea.external_verdict).toUpperCase()}</small></a>`).join("")}</div></section>
      <div class="v4-pareto"><b>Pareto front</b>${(data.pareto_front_ids || []).map((id) => { const row = (data.all_candidates || []).find((item) => item.id === id); return row ? `<span>${pick4(row.title)}</span>` : ""; }).join("")}</div>
      ${group("全新组合方向", "New composition candidates", data.discussion || [], "discussion")}
      ${group("旧方向条件复活", "Conditional revivals", data.revival || [], "revival")}
      ${group("需要补强后再讨论", "Needs strengthening", data.repair || [], "repair")}
      ${group("作为组件或基线保留", "Retained as components or baselines", data.component || [], "component")}
    </section>`;
  };
})();
