(() => {
  const data = () => window.ADVISOR_PRIORITY_IDEAS || {primary_shortlist:[],ranked_ideas:[],weights:{},meta_review_status:{}};
  const tx = (v) => textOf(v || "");
  const tierName = (v) => ({
    lead:{zh:"主线",en:"Lead"},
    "high-upside":{zh:"高上限",en:"High-upside"},
    "fast-pilot":{zh:"快速 P0",en:"Fast pilot"},
    "second-wave":{zh:"第二梯队",en:"Second wave"},
    supporting:{zh:"合并/支撑",en:"Supporting / merge"}
  }[v]?.[language] || v);
  const priorityName = (v) => ({high:{zh:"优先做 P0",en:"High P0 priority"},medium:{zh:"中等 P0 优先级",en:"Medium P0 priority"},low:{zh:"暂不优先",en:"Low P0 priority"}}[v]?.[language] || v);
  const reason = (x) => language === "zh" ? (x.meta_review?.reason_zh || x.rationale_zh || "") : (x.meta_review?.reason || x.rationale_en || "");

  function shortlistCard(x) {
    return `<article class="advisor-priority-card tier-${esc(x.relative_tier)}"><header><span>#${x.advisor_rank}</span><div><b>${tx(x.title)}</b><small>${tierName(x.relative_tier)} · ${priorityName(x.first_pilot_priority)}</small></div><strong>${Number(x.score).toFixed(2)}</strong></header><p>${esc(reason(x))}</p><div class="advisor-score-row"><span>${language === "zh" ? "问题" : "Problem"} ${x.importance}/5</span><span>${language === "zh" ? "机制" : "Mechanism"} ${x.distinctness}/5</span><span>${language === "zh" ? "证伪" : "Falsifiability"} ${x.falsifiability}/5</span><span>${language === "zh" ? "可做性" : "Feasibility"} ${x.feasibility}/5</span><span>ICLR ${x.story}/5</span></div>${(x.merge_with||[]).length?`<div class="advisor-merge"><b>${language === "zh" ? "同族合并/支撑" : "Merge/support"}</b>${x.merge_with.map(id=>`<span>${esc(id)}</span>`).join("")}</div>`:""}</article>`;
  }

  function rankRow(x) {
    return `<tr><td>${x.advisor_rank}</td><td><b>${tx(x.title)}</b><small>${esc(x.cluster)}</small></td><td>${tierName(x.relative_tier)}</td><td>${priorityName(x.first_pilot_priority)}</td><td>${Number(x.score).toFixed(2)}</td><td>${(x.merge_with||[]).map(id=>`<span>${esc(id)}</span>`).join(" ")||"—"}</td></tr>`;
  }

  window.renderAdvisorPriorityIdeas = function renderAdvisorPriorityIdeas() {
    const d=data(), shortlist=d.primary_shortlist||[], meta=d.meta_review_status||{};
    const comment=language==="zh"?(d.portfolio_comment_zh||""):(d.portfolio_comment||"");
    return `<section class="panel advisor-priority-panel"><div class="idea-panel-heading"><div><h3 id="advisor-priority-shortlist">${language === "zh" ? "师兄讨论 shortlist：22 → 8" : "Advisor discussion shortlist: 22 → 8"}</h3><p class="section-intro">${language === "zh" ? "22 个方向都已经独立通过严格 R2。本层不再判断‘能不能做’，而是比较‘先做哪几个’：对重叠主线去重，并综合科学问题、机制独立性、决定性实验、资源成本和 ICLR 叙事。" : "All 22 directions already passed strict independent R2. This layer compares which ones to prioritize, deduplicating overlapping theses and considering problem importance, mechanism independence, decisive experiments, cost, and ICLR story."}</p></div><strong>${meta.reviewed||0}/22 ${language === "zh" ? "相对元审查" : "comparative meta-review"}</strong></div>
      <div class="advisor-shortlist-grid">${shortlist.map(shortlistCard).join("")}</div>
      ${comment?`<div class="claim-box advisor-meta-comment"><b>${language === "zh" ? "独立 Reviewer 的组合判断" : "Independent portfolio judgment"}</b><p>${esc(comment)}</p></div>`:""}
      <details class="advisor-ranking"><summary>${language === "zh" ? "查看全部 22 个严格 PASS 的相对排名与合并关系" : "View relative ranking and merge relationships for all 22 strict PASS ideas"}</summary><div class="table-wrap"><table><thead><tr><th>#</th><th>Idea</th><th>${language === "zh" ? "定位" : "Tier"}</th><th>P0</th><th>${language === "zh" ? "比较分" : "Score"}</th><th>${language === "zh" ? "同族关系" : "Overlap"}</th></tr></thead><tbody>${(d.ranked_ideas||[]).map(rankRow).join("")}</tbody></table></div></details>
    </section>`;
  };
})();
