(() => {
  const pick=(zh,en)=>language==="zh"?zh:en;
  const api=window.SYSTEM_OVERVIEW_SECTIONS=window.SYSTEM_OVERVIEW_SECTIONS||{};
  api.renderSystemMap=function(state){
    const s=state.summary||{},e=state.p0_economy_gate?.summary||{},l=state.p0_decision_ledger?.summary||{},a=state.ai_consultation_automation?.summary||{},p=state.paper_first_workflow?.summary||{},arch=state.system_architecture?.summary||{};
    const m=(v,zh,en)=>`<div><b>${esc(String(v??0))}</b><span>${pick(zh,en)}</span></div>`;
    return `<section class="system-map system-section"><div class="system-map-heading"><div><span class="system-kicker">CURRENT RESEARCH OS</span><h3>${pick("唯一主流程已经收口：Paper-first 生命周期驱动，职责层负责执行","One canonical flow: paper-first lifecycle, functional layers for execution")}</h3><p>${pick("系统不再把 Idea 搜索、P0 状态机和运行时管理当成三套并列流程。11 步生命周期决定什么时候继续，6 个职责层决定谁负责，Decision Ledger 只记录当前实验决策。","Idea search, the P0 state machine, and runtime control are no longer presented as parallel top-level workflows. Eleven temporal stages decide when work advances, six responsibility layers decide who owns it, and the Decision Ledger records only current experiment decisions.")}</p></div><em>${esc(String(state.health?.status||"unknown").toUpperCase())}</em></div><div class="system-map-metrics">${m(arch.temporal_stages,"时间阶段","temporal stages")}${m(arch.functional_layers,"职责层","responsibility layers")}${m(arch.assigned_components,"已归责后端组件","assigned backend components")}${m(p.paper_design_passed,"新版 Paper-first 卡","paper-first cards")}${m(e.economy_ready,"资源经济就绪","Economy-ready")}${m(l.launchable,"可启动实验","launchable")}${m(a.unresolved_high_risk,"AI 未处置高风险","unresolved AI high-risk")}</div></section>`;
  };
})();
