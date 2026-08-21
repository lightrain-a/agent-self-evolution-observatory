(() => {
  const data = () => window.ADVISOR_PRIORITY_IDEAS || {discussion_pool:[],priority_first_read:[],ranked_ideas:[],weights:{},meta_review_status:{}};
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

  function priorityCard(x) {
    return `<article class="advisor-priority-card tier-${esc(x.relative_tier)}"><header><span>#${x.advisor_rank}</span><div><b>${tx(x.title)}</b><small>${tierName(x.relative_tier)} · ${priorityName(x.first_pilot_priority)}</small></div><strong>${Number(x.score).toFixed(2)}</strong></header><p>${esc(reason(x))}</p><div class="advisor-score-row"><span>${language === "zh" ? "问题" : "Problem"} ${x.importance}/5</span><span>${language === "zh" ? "机制" : "Mechanism"} ${x.distinctness}/5</span><span>${language === "zh" ? "证伪" : "Falsifiability"} ${x.falsifiability}/5</span><span>${language === "zh" ? "可做性" : "Feasibility"} ${x.feasibility}/5</span><span>ICLR ${x.story}/5</span></div>${(x.merge_with||[]).length?`<div class="advisor-merge"><b>${language === "zh" ? "同族合并/支撑" : "Merge/support"}</b>${x.merge_with.map(id=>`<span>${esc(id)}</span>`).join("")}</div>`:""}</article>`;
  }

  function rankRow(x) {
    return `<tr><td>${x.advisor_rank}</td><td><b>${tx(x.title)}</b><small>${esc(x.cluster)}</small></td><td>${tierName(x.relative_tier)}</td><td>${priorityName(x.first_pilot_priority)}</td><td>${Number(x.score).toFixed(2)}</td><td>${(x.merge_with||[]).map(id=>`<span>${esc(id)}</span>`).join(" ")||"—"}</td></tr>`;
  }

  window.renderAdvisorPriorityIdeas = function renderAdvisorPriorityIdeas() {
    const d=data(), pool=d.discussion_pool||d.ranked_ideas||[], priority=d.priority_first_read||[], meta=d.meta_review_status||{};
    const comment=language==="zh"?(d.portfolio_comment_zh||""):(d.portfolio_comment||"");
    return `<section class="panel advisor-priority-panel"><div class="idea-panel-heading"><div><h3 id="advisor-priority-shortlist">${language === "zh" ? "正式讨论池：22 个严格 R2 PASS" : "Discussion pool: 22 strict R2 PASS ideas"}</h3><p class="section-intro">${language === "zh" ? "这 22 个方向全部达到此前约定的讨论门槛，都会完整进入人工讨论，不再由系统先删减。相对元审查只负责排序、标注重叠关系和 P0 优先级，帮助更快浏览。" : "All 22 directions meet the agreed discussion threshold and enter human discussion without system-side pruning. Comparative meta-review only ranks them, marks overlap, and adds P0 priority for faster review."}</p></div><strong>${pool.length}/${d.discussion_target||20} ${language === "zh" ? "正式讨论候选" : "discussion-ready"}</strong></div>
      <section class="advisor-priority-first-read"><h3 data-toc="false">${language === "zh" ? "优先阅读 8 个（不是 shortlist）" : "Eight first-read priorities (not a shortlist)"}</h3><p>${language === "zh" ? "这 8 个只是建议师兄先看；其余 14 个仍属于正式讨论池，并完整保留在下方 1–22 相对排名中。" : "These eight are only suggested first reads; the other fourteen remain full discussion candidates and are preserved in the 1–22 ranking below."}</p><div class="advisor-shortlist-grid">${priority.map(priorityCard).join("")}</div></section>
      ${comment?`<div class="claim-box advisor-meta-comment"><b>${language === "zh" ? "独立 Reviewer 的组合判断" : "Independent portfolio judgment"}</b><p>${esc(comment)}</p></div>`:""}
      <section class="advisor-ranking advisor-ranking-open"><h3 data-toc="false">${language === "zh" ? "全部 22 个正式讨论 Idea" : "All 22 discussion-ready ideas"}</h3><div class="table-wrap"><table><thead><tr><th>#</th><th>Idea</th><th>${language === "zh" ? "定位" : "Tier"}</th><th>P0</th><th>${language === "zh" ? "比较分" : "Score"}</th><th>${language === "zh" ? "同族关系" : "Overlap"}</th></tr></thead><tbody>${pool.map(rankRow).join("")}</tbody></table></div></section>
    </section>`;
  };
})();
