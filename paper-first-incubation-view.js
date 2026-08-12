(() => {
  const pick=(zh,en)=>language==="zh"?zh:en;
  const txt=(value)=>{if(value&&typeof value==="object"&&(value.zh||value.en)) return language==="zh"?(value.zh||value.en):(value.en||value.zh); return String(value||"");};
  const verdictMeta=(value)=>({
    ADVANCE_TO_PAPER_DESIGN:{tone:"advance",label:pick("Paper-first ADVANCE","ADVANCE · PAPER-FIRST")},
    REVISE_NOVELTY_BOUNDARY:{tone:"revise",label:pick("收紧 Novelty 边界","REVISE · NOVELTY")},
    BLOCK_COLLISION:{tone:"block",label:pick("直接碰撞 · 阻断","BLOCK · COLLISION")},
  }[value]||{tone:"neutral",label:String(value||"UNKNOWN")});
  const promotionFor=(row)=>{
    const independent=window.HUMAN_TERMINAL_IDEA_STATE?.independent_methods||{};
    return Object.entries(independent).find(([,meta])=>String(meta?.source_incubation_id||"")===String(row.id||""))||null;
  };
  const f0For=(ideaId)=> (window.RESEARCH_SYSTEM_STATE?.paper_first_p0_f0?.cards||[]).find(x=>String(x.idea_id||"")===String(ideaId||""))||null;
  const nearestLinks=(rows)=> (rows||[]).map(row=>{const ref=String(row.ref||""); const arxiv=ref.match(/arXiv:(\d+\.\d+)/i); const href=arxiv?`https://arxiv.org/abs/${arxiv[1]}`:"#"; return `<a href="${esc(href)}" target="_blank" rel="noopener"><b>${esc(row.title||ref)}</b><span>${esc(ref)}</span></a>`}).join("");
  const card=(row)=>{
    const v=verdictMeta(row.verdict), promotion=promotionFor(row), promoted=!!promotion;
    const ideaId=promotion?.[0]||row.p0_idea_id||"", meta=promotion?.[1]||{}; const f0=f0For(ideaId);
    const badge=promoted?`${meta.code||row.p0_code||"P0"} · P0 ${f0?.decision||"F0_PENDING"}`:v.label;
    const tone=promoted?"p0":v.tone;
    const next=promoted
      ? pick(`已进入 P0 lifecycle；当前只执行局部 F0/P0-Support。${f0?.gpu0?.evidence||"等待/执行局部支持验证"}。方法结论、第二 backbone 与全量实验仍锁定。`,`Promoted into the P0 lifecycle; only local F0/P0-Support is active. ${f0?.gpu0?.evidence||"Local support validation is pending/running."} Method conclusions, a second backbone, and full experiments remain locked.`)
      : row.verdict==="REVISE_NOVELTY_BOUNDARY"
        ? pick("继续查 closest work 与 irreducible difference；边界收紧前禁止实现和 P0。","Continue closest-work and irreducible-difference review; implementation/P0 remains blocked until the boundary is sharper.")
        : pick("作为 collision memory 保留；不生成实现或实验计划。","Retained as collision memory; no implementation or experiment plan is generated.");
    return `<details class="paper-incubation-card incubation-${tone}" id="incubation-${esc(String(row.id||"").toLowerCase())}"><summary><div><span>${esc(promoted?(meta.code||row.p0_code||row.id):row.id||"")}</span><b>${esc(txt(row.title))}</b><small>${esc(promoted?`${row.id} · ${row.theme||""}`:row.theme||"")}</small></div><em>${esc(badge)}</em></summary><div class="paper-incubation-body"><section class="incubation-wide"><h4 data-toc="false">${pick("论文问题","Paper problem")}</h4><p>${esc(txt(row.paper_problem))}</p></section><section class="incubation-wide novelty"><h4 data-toc="false">${pick("Novelty 边界／最近工作之后真正剩什么","Novelty boundary / what remains after closest work")}</h4><p>${esc(txt(row.novelty_boundary))}</p></section><section><h4 data-toc="false">${pick("原理直觉","Principle")}</h4><p>${esc(txt(row.principle))}</p></section><section><h4 data-toc="false">${pick("方法草图","Method sketch")}</h4><p>${esc(txt(row.method))}</p></section><section><h4 data-toc="false">${pick("最强同信息对照","Strongest same-information baseline")}</h4><p>${esc(txt(row.strongest_baseline))}</p></section><section><h4 data-toc="false">${pick("最便宜的局部证伪","Cheapest local falsifier")}</h4><p>${esc(txt(row.local_falsifier))}</p></section><section class="incubation-wide"><h4 data-toc="false">Closest work</h4><div class="incubation-nearest">${nearestLinks(row.nearest_work)}</div></section><section class="incubation-wide risk"><h4 data-toc="false">${pick("碰撞风险／当前动作","Collision risk / current action")}</h4><p>${esc(txt(row.collision_risk))}</p><small>${esc(next)}</small></section></div></details>`;
  };
  window.renderPaperFirstIdeaIncubation=function(){
    const state=window.PAPER_FIRST_IDEA_INCUBATION||{}, s=state.summary||{}, rows=state.candidates||[];
    if(!rows.length) return "";
    const promoted=rows.filter(r=>promotionFor(r)).length;
    return `<section class="panel paper-incubation-overview"><div class="idea-panel-heading"><div><span class="incubation-kicker">PAPER-FIRST · NEW PROBLEMS · ${esc(state.review_date||"")}</span><h3>${pick("Paper-first 新问题与独立方法放在同一章，但权限仍分层","Paper-first new problems share one chapter with standalone methods while authority remains layered")}</h3><p class="section-intro">${pick(`8 个新问题中 ${promoted} 个已经通过明确人工授权进入 P0 lifecycle；它们只运行 F0/P0-Support，不自动获得方法结论或 GPU 扩量权限。其余 REVISE/BLOCK 继续留在同一章方便横向比较。`,`Of eight new problems, ${promoted} have explicit human P0-lifecycle promotion. They run F0/P0-Support only and do not automatically gain method-conclusion or scale-up authority. REVISE/BLOCK candidates remain visible in the same chapter for comparison.`)}</p></div><strong>${promoted}/${s.candidates||0}<span>${pick("已进入 P0","promoted to P0")}</span></strong></div><div class="paper-incubation-stats"><div><b>${s.candidates||0}</b><span>${pick("新问题","new problems")}</span></div><div><b>${promoted}</b><span>P0 lifecycle</span></div><div><b>${s.revise_novelty_boundary||0}</b><span>REVISE</span></div><div><b>${s.blocked_collision||0}</b><span>BLOCK</span></div><div><b>${s.themes||0}</b><span>${pick("不同主题","themes")}</span></div><div><b>${s.gpu_authorized||0}</b><span>${pick("直接 GPU 权限","direct GPU authority")}</span></div></div><div class="incubation-rule"><b>${pick("硬规则","Hard rule")}</b><span>${pick("P0 lifecycle ≠ METHOD-PASS ≠ full experiment。新 4 项先完成局部 support/updater qualification；只有 support + Economy + Pre-Experiment + Method Freeze 全部满足才允许进一步扩量。","P0 lifecycle ≠ METHOD-PASS ≠ full experiment. The four promotions first complete local support/updater qualification; scale-up remains locked behind support, Economy, Pre-Experiment, and Method Freeze.")}</span></div></section><div class="paper-incubation-list">${rows.map(card).join("")}</div>`;
  };
})();
