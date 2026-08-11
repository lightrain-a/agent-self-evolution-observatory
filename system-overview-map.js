(() => {
  const pick=(zh,en)=>language==="zh"?zh:en;
  const api=window.SYSTEM_OVERVIEW_SECTIONS=window.SYSTEM_OVERVIEW_SECTIONS||{};
  api.renderSystemMap=function(state){
    const s=state.summary||{},e=state.p0_economy_gate?.summary||{},l=state.p0_decision_ledger?.summary||{},a=state.ai_consultation_automation?.summary||{};
    const m=(v,zh,en)=>`<div><b>${esc(String(v||0))}</b><span>${pick(zh,en)}</span></div>`;
    return `<section class="system-map system-section"><div class="system-map-heading"><div><span class="system-kicker">CURRENT SYSTEM MAP</span><h3>${pick("六层科研系统：先筛价值，再编译实验，再判断方法","Six layers: screen value, compile experiments, then judge methods")}</h3></div><em>${esc(String(state.health?.status||"unknown").toUpperCase())}</em></div><div class="system-map-metrics">${m(s.papers,"文献","papers")}${m(s.p0_admission_active,"P0 生命周期","P0 lifecycle")}${m(e.matched_simplification_stops,"简化 STOP","simplification stops")}${m(e.substrate_stops,"底座 STOP","substrate stops")}${m(l.launchable,"可启动","launchable")}${m(a.baseline_subjects,"AI baseline","AI baselines")}${m(a.unresolved_high_risk,"AI 高风险","AI high-risk")}</div></section>`;
  };
})();
