(() => {
  const bank = () => window.IDEA_DISCOVERY_V3 || {summary:{},repository_patterns:[],workflow_stages:[],shortlist:[],repair:[],pareto_front_ids:[]};
  const repairBank = () => window.IDEA_DISCOVERY_V31 || {summary:{},children:[]};
  const decisionLabel = (value) => ({shortlist:{zh:"内部短名单",en:"Internal shortlist"},repair:{zh:"需要修订",en:"Repair"},stop:{zh:"停止",en:"Stop"}}[value]?.[language] || value);
  const parentHref = (idea) => `paper-ideas.html#iclr-${esc(idea.parent_id || "iclr-low-resource-bank")}`;
  const scoreRows = (idea) => Object.entries(idea.scores || {}).map(([key,value]) => `<div><span>${esc(key.replaceAll("_"," "))}</span><i><b style="width:${Number(value)*20}%"></b></i><strong>${Number(value)}/5</strong></div>`).join("");
  const latestReview = (idea) => { const rows=idea.external_reviews || []; return rows.length ? rows[rows.length-1] : null; };
  const externalLabel = (idea) => idea.external_review_status === "reviewed" ? `R2 ${String(idea.external_verdict || "unknown").toUpperCase()}` : (language === "zh" ? "R2 待审查" : "R2 pending");

  function ideaCard(idea,index,round="v3") {
    const review=latestReview(idea); const verdict=idea.external_verdict || "pending";
    const finding=language === "zh" ? (review?.finding_zh || review?.finding || "") : (review?.finding || "");
    const action=language === "zh" ? (review?.required_action_zh || review?.required_action || "") : (review?.required_action || "");
    return `<details class="solution-v3-card decision-${esc(idea.internal_decision)} verdict-${esc(verdict)}" ${index < 3 ? "open" : ""}><summary><div><span>#${idea.internal_rank}</span><b>${textOf(idea.title)}</b><small>${decisionLabel(idea.internal_decision)} · ${esc(idea.update_surface)}</small></div><div><em class="external-verdict-badge verdict-${esc(verdict)}">${esc(externalLabel(idea))}</em><strong>${Number(idea.mean_score).toFixed(2)}</strong><small>${language === "zh" ? "内部均分" : "internal mean"}</small></div></summary><div class="solution-v3-body"><div class="solution-v3-grid">
      <section><h4 data-toc="false">${language === "zh" ? "继承的问题" : "Inherited problem"}</h4><p>${textOf(idea.problem)}</p><a href="${round === "v31" ? "paper-ideas.html#solution-first-v3" : parentHref(idea)}">${round === "v31" ? (language === "zh" ? "查看上一轮子节点 →" : "Open previous-round child →") : (language === "zh" ? "查看父 Idea →" : "Open parent idea →")}</a></section>
      <section><h4 data-toc="false">${language === "zh" ? "变化的假设" : "Changed assumption"}</h4><p>${textOf(idea.changed_assumption)}</p></section>
      <section class="mechanism"><h4 data-toc="false">${language === "zh" ? "精确解决机制" : "Exact solution mechanism"}</h4><p>${textOf(idea.exact_mechanism)}</p><div class="solution-v3-surface"><b>${language === "zh" ? "更新表面" : "Update surface"}</b>${esc(idea.update_surface)}</div></section>
      <section><h4 data-toc="false">${language === "zh" ? "学习信号" : "Learning signal"}</h4><p>${textOf(idea.learning_signal)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "独立真值" : "Independent ground truth"}</h4><p>${textOf(idea.independent_ground_truth)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "最强基线" : "Strongest baseline"}</h4><p>${textOf(idea.strongest_baseline)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><p>${textOf(idea.decisive_pilot)}</p></section>
      <section><h4 data-toc="false">Stop</h4><p>${textOf(idea.stop_condition)}</p></section>
    </div>${review ? `<div class="solution-v3-review verdict-${esc(verdict)}"><header><b>${language === "zh" ? "独立 R2 机制审查" : "Independent R2 mechanism review"}</b><span>${esc(String(verdict).toUpperCase())}</span></header><p>${esc(finding)}</p><small><strong>${language === "zh" ? "下一步要求" : "Required action"}:</strong> ${esc(action)}</small></div>` : ""}<div class="solution-v3-footer"><div class="solution-v3-assets">${(idea.public_assets || []).map((item) => `<span>${esc(item)}</span>`).join("")}</div><div class="solution-v3-operators">${(idea.generation_mechanisms || []).map((item) => `<span>${esc(item)}</span>`).join("")}</div></div><div class="solution-v3-scores">${scoreRows(idea)}</div></div></details>`;
  }

  function group(titleZh,titleEn,rows,tone,round="v3") {
    return `<section class="solution-v3-group tone-${tone}"><h3 data-toc="false">${language === "zh" ? titleZh : titleEn}<span>${rows.length}</span></h3><div class="solution-v3-list">${rows.map((idea,index)=>ideaCard(idea,index,round)).join("")}</div></section>`;
  }

  function renderReviewerRepairRound() {
    const data=repairBank(), summary=data.summary || {};
    if (!(data.children || []).length) return "";
    return `<section class="solution-v31-round"><div class="solution-v31-head"><div><h3 data-toc="false">${language === "zh" ? "v3.1：Reviewer 向量修订轮" : "v3.1: reviewer-vector repair round"}</h3><p>${language === "zh" ? "仅对 v3 的 6 个 REVISE 继续生成；4 个 BLOCK 已停止。每个修订子节点补齐上一轮要求的后验、目标函数、随机化、支持假设或约束解码器。" : "Only the six v3 REVISE children continue; four BLOCK children stop. Each repair supplies the posterior, objective, randomization, support assumption, or constrained decoder requested by R2."}</p></div><div class="solution-v31-counts"><span><b>${summary.children || 0}</b>${language === "zh" ? "修订子节点" : "repair children"}</span><span><b>${summary.external_reviewed || 0}</b>${language === "zh" ? "已完成 R2" : "R2 reviewed"}</span><span><b>${summary.external_pass || 0}</b>PASS</span><span><b>${summary.external_revise || 0}</b>REVISE</span><span><b>${summary.external_block || 0}</b>BLOCK</span></div></div>${group("Reviewer 修订子节点","Reviewer-repaired children",data.children || [],"repair","v31")}</section>`;
  }

  window.renderSolutionFirstIdeas = function renderSolutionFirstIdeas() {
    const data=bank(), summary=data.summary || {};
    return `<section class="panel solution-v3-panel"><div class="idea-panel-heading"><div><h3 id="solution-first-v3">${language === "zh" ? "Idea Discovery v3：解决方案优先的分支搜索" : "Idea Discovery v3: solution-first branch search"}</h3><p class="section-intro">${language === "zh" ? "该批次针对现有 REVISE 的关键问题重新生成方法子节点。内部短名单不等于 R2 PASS；必须完成独立文献碰撞和外部机制审查后，才能并入主 Idea Bank。" : "This batch regenerates method children for existing REVISE problems. Internal shortlist is not R2 PASS; independent collision and external mechanism review are required before merging into the main bank."}</p></div><strong>${summary.internal_shortlist || 0} ${language === "zh" ? "个内部短名单" : "internal shortlist"}</strong></div>
      <div class="grid solution-v3-stats"><div class="stat"><b>${summary.repository_patterns || 0}</b><span>${language === "zh" ? "个 GitHub 系统模式" : "GitHub system patterns"}</span></div><div class="stat"><b>${summary.workflow_stages || 0}</b><span>${language === "zh" ? "个发现阶段" : "discovery stages"}</span></div><div class="stat"><b>${summary.raw_children || 0}</b><span>${language === "zh" ? "个方法子节点" : "method children"}</span></div><div class="stat"><b>${summary.internal_shortlist || 0}</b><span>${language === "zh" ? "内部短名单" : "internal shortlist"}</span></div><div class="stat"><b>${summary.external_pass || 0}</b><span>${language === "zh" ? "外部 PASS" : "external PASS"}</span></div></div>
      <div class="solution-v3-warning"><b>${language === "zh" ? "状态边界" : "Status boundary"}</b>${summary.external_reviewed ? (language === "zh" ? `已完成 ${summary.external_reviewed}/${summary.internal_shortlist} 个独立 R2：${summary.external_pass || 0} PASS、${summary.external_revise || 0} REVISE、${summary.external_block || 0} BLOCK。即使外部 PASS，也需完成主 Bank 对账后才会增加当前 4 个正式 PASS。` : `${summary.external_reviewed}/${summary.internal_shortlist} independent R2 reviews are complete: ${summary.external_pass || 0} PASS, ${summary.external_revise || 0} REVISE, ${summary.external_block || 0} BLOCK. External PASS still requires reconciliation before changing the four formal main-bank PASS ideas.`) : (language === "zh" ? "当前 10 个只说明解决机制已经具体到可审查、可实验；它们没有增加主 Bank 的 4 个 PASS。" : "The ten candidates are concrete enough to review and test, but they do not increase the four PASS ideas in the main bank.")}</div>
      <section class="solution-v3-repos"><h3 data-toc="false">${language === "zh" ? "从官方 GitHub 仓库吸收的机制" : "Mechanisms adopted from official GitHub repositories"}</h3><div>${(data.repository_patterns || []).map((item) => `<article><header><b>${esc(item.system)}</b><a target="_blank" rel="noopener" href="${esc(item.official_repo)}">GitHub ↗</a></header><p>${textOf(item.pattern)}</p><span>${esc(item.adopted_as)}</span></article>`).join("")}</div></section>
      <section class="solution-v3-flow"><h3 data-toc="false">${language === "zh" ? "新的 Idea 数据流" : "New idea data flow"}</h3><div>${(data.workflow_stages || []).map((stage,index) => `<article><span>${esc(stage.id)}</span><b>${textOf(stage.name)}</b><p>${textOf(stage.output)}</p></article>${index < data.workflow_stages.length-1 ? "<i>→</i>" : ""}`).join("")}</div></section>
      <section class="solution-v3-gates"><h3 data-toc="false">${language === "zh" ? "新增的机制不可归约性门槛" : "New mechanism-irreducibility gates"}</h3><div>${(data.solution_gates || []).map((gate) => `<article><b>${esc(gate.id)}</b><p>${textOf(gate)}</p></article>`).join("")}</div></section>
      <div class="solution-v3-pareto"><b>Pareto front</b>${(data.pareto_front_ids || []).map((id) => {const item=(data.shortlist || []).find((row)=>row.id===id)||(data.repair || []).find((row)=>row.id===id);return item?`<span>${textOf(item.title)}</span>`:"";}).join("")}</div>
      ${group("内部机制短名单","Internal mechanism shortlist",data.shortlist || [],"shortlist")}
      ${group("需要进一步修订","Requires further repair",data.repair || [],"repair")}
      ${renderReviewerRepairRound()}
    </section>`;
  };
})();
