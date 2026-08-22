(() => {
  function bank() {
    return window.MACHINE_SCHOOL_IDEAS || {summary:{},inspirations:[],passed_ideas:[],revise_ideas:[],rejected_ideas:[],all_candidates:[]};
  }
  function latestReview(idea) {
    const reviews = idea.external_reviews || [];
    return reviews.length ? reviews[reviews.length - 1] : null;
  }
  function verdict(idea) {
    const review = latestReview(idea);
    return review?.verdict || (idea.internal_decision === "pass" ? "pending" : idea.internal_decision);
  }
  function card(idea, index) {
    const review = latestReview(idea);
    const v = verdict(idea);
    const budget = idea.budget || {};
    return `<details class="machine-school-idea verdict-${esc(v)}" ${index < 4 ? "open" : ""}>
      <summary><div><span>#${idea.external_rank || idea.screen_rank || index + 1}</span><b>${textOf(idea.title)}</b><small>${language === "zh" ? "原始序号" : "Raw #"} ${idea.raw_rank || "--"} · ${esc(idea.inspiration_id || "")}</small></div><div><em class="external-verdict-badge verdict-${esc(v)}">${esc(String(v).toUpperCase())}</em><strong>${budget.max_gpus || 0} GPU · ${budget.gpu_hours || 0}h</strong></div></summary>
      <div class="machine-school-idea-body"><div class="machine-school-grid">
        <section><b>${language === "zh" ? "问题" : "Problem"}</b><p>${textOf(idea.purpose)}</p></section>
        <section><b>${language === "zh" ? "机制" : "Mechanism"}</b><p>${textOf(idea.core_idea)}</p></section>
        <section><b>${language === "zh" ? "碰撞边界" : "Collision boundary"}</b><p>${textOf(idea.collision_boundary)}</p><div class="cvpr-chip-row">${(idea.nearest_work || []).map((x) => `<span>${esc(x)}</span>`).join("")}</div></section>
        <section><b>${language === "zh" ? "最小 Pilot" : "Minimum pilot"}</b><p>${textOf(idea.pilot)}</p></section>
        <section><b>${language === "zh" ? "最强基线" : "Strongest baseline"}</b><p>${textOf(idea.strongest_baseline)}</p></section>
        <section><b>Stop</b><p>${textOf(idea.stop_condition)}</p></section>
      </div>${review ? `<div class="project-web-gpt-review verdict-${esc(review.verdict)}"><header><b>${language === "zh" ? "Agent 项目网页版 GPT 独立审查" : "Agent-project web GPT independent review"}</b><span>${esc(String(review.verdict).toUpperCase())}</span></header><p>${esc(review.finding || "")}</p><small><strong>${language === "zh" ? "必须修改" : "Required action"}:</strong> ${esc(window.localizedReviewAction ? window.localizedReviewAction(idea.id, review, language) : (review.required_action || ""))}</small></div>` : ""}</div>
    </details>`;
  }
  function group(titleZh, titleEn, ideas, tone) {
    return `<section class="machine-school-group tone-${tone}"><h4 data-toc="false">${language === "zh" ? titleZh : titleEn}<span>${ideas.length}</span></h4><div class="machine-school-list">${ideas.map(card).join("")}</div></section>`;
  }
  window.renderMachineSchoolIdeas = function renderMachineSchoolIdeas() {
    const data = bank();
    const summary = data.summary || {};
    const discussionShortlist = data.teacher_shortlist || [];
    const reviewLine = summary.external_reviewed
      ? (language === "zh" ? `外部复核 ${summary.external_reviewed}/${summary.internal_pass}：${summary.external_pass} PASS、${summary.external_revise} REVISE、${summary.external_block} BLOCK。` : `External review ${summary.external_reviewed}/${summary.internal_pass}: ${summary.external_pass} PASS, ${summary.external_revise} REVISE, ${summary.external_block} BLOCK.`)
      : (language === "zh" ? "11 个内部通过项正在进入 Oracle／Agent 项目网页版 GPT 复核。" : "The 11 internally passed ideas are queued for Oracle / Agent-project web-GPT review.");
    return `<section class="panel machine-school-panel"><div class="idea-panel-heading"><div><h3 id="machine-school-inspired-ideas">${language === "zh" ? "网络灵感批次：把校园梗还原为可证伪研究变量" : "Internet-inspired batch: translating school metaphors into falsifiable variables"}</h3><p class="section-intro">${language === "zh" ? "六个梗只作为问题发现入口；最终 Idea 使用精确机制名称。24 个原始候选经过持续学习真实性、碰撞、新颖性、归因、稳定性、圈外迁移、等预算和低资源 Pilot 八项筛查。" : "The six metaphors are only problem-discovery prompts; final ideas use precise mechanism names. Twenty-four raw candidates are screened for persistent learning, collision, novelty, attribution, stability, transfer, matched budgets, and low-resource pilots."}</p></div><strong>${reviewLine}</strong></div>
      <div class="grid machine-school-stats"><div class="stat"><b>${summary.raw || 0}</b><span>${language === "zh" ? "原始候选" : "raw candidates"}</span></div><div class="stat"><b>${summary.internal_pass || 0}</b><span>${language === "zh" ? "内部通过" : "internal pass"}</span></div><div class="stat"><b>${summary.internal_revise || 0}</b><span>REVISE / MERGE</span></div><div class="stat"><b>${summary.internal_reject || 0}</b><span>${language === "zh" ? "直接淘汰" : "rejected"}</span></div><div class="stat"><b>${summary.external_pass || 0}</b><span>${language === "zh" ? "外部 PASS" : "external PASS"}</span></div></div>
      <div class="machine-school-inspirations">${(data.inspirations || []).map((item) => `<article><b>${textOf(item.meme)}</b><p>${textOf(item.research_variable)}</p></article>`).join("")}</div>
      ${discussionShortlist.length ? `<div class="claim-box"><b>${language === "zh" ? "优先讨论 shortlist" : "Priority shortlist for senior/teacher discussion"}</b><p>${language === "zh" ? "第 1 个可直接设计 P0/P1；其余必须先按外部审查的 required action 收缩机制边界。" : "The first idea can proceed to P0/P1; the others require mechanism repair according to the external required action."}</p>${discussionShortlist.map((idea) => `<span class="machine-shortlist-item verdict-${esc(idea.external_verdict || "pending")}">${textOf(idea.title)} · ${esc(String(idea.external_verdict || "pending").toUpperCase())}</span>`).join("")}</div>` : ""}
      ${group("内部通过项：按外部 PASS／REVISE／BLOCK 排序", "Internal passes ordered by external PASS / REVISE / BLOCK", data.passed_ideas || [], "pass")}
      ${group("保留为修改或合并候选", "Retained for revision or merge", data.revise_ideas || [], "revise")}
      ${group("碰撞后淘汰", "Rejected after collision review", data.rejected_ideas || [], "reject")}
    </section>`;
  };
})();
