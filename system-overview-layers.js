(() => {
  const pick=(zh,en)=>language==="zh"?zh:en;
  const api=window.SYSTEM_OVERVIEW_SECTIONS=window.SYSTEM_OVERVIEW_SECTIONS||{};
  const row=(n,tag,zh,en,zhb,enb)=>`<article><span>${n}</span><div><small>${tag}</small><b>${pick(zh,en)}</b><p>${pick(zhb,enb)}</p></div></article>`;
  api.renderSystemLayers=function(){return `<section class="system-layers system-section"><h3>${pick("系统的六个职责层","Six responsibility layers")}</h3><div class="system-layer-list">
    ${row(1,"EVIDENCE","证据与研究问题","Evidence & framing","文献、证据图、撞车边界和主张范围。","Literature, evidence graph, collision boundary, and claim scope.")}
    ${row(2,"DISCOVERY","Idea 搜索与 AI 会诊","Idea search & AI clinic","宽搜索、人工终态、Premortem 与 Red Team。","Wide search, human terminal decisions, premortem, and red team.")}
    ${row(3,"ECONOMY","P0 经济门与实验编译","P0 Economy & compile","简化基线、底座库存、causal unit、VOI、8 Gate。","Matched simplifications, substrate inventory, causal unit, VOI, and eight gates.")}
    ${row(4,"SCIENCE","科学状态机","Scientific state machine","Problem → Substrate → F0 → P0-S → P0-M → P1 → Paper。","Problem → Substrate → F0 → P0-S → P0-M → P1 → Paper.")}
    ${row(5,"RUNTIME","执行与权限","Runtime & authority","single-writer、GPU lease、trace、预算、恢复。","Single-writer authority, GPU leases, traces, budgets, and recovery.")}
    ${row(6,"LEARN","决策回流与发布","Feedback & publication","Decision Ledger、repair queue、automation cycle、公开快照。","Decision Ledger, repair queue, automation cycle, and public snapshots.")}
  </div></section>`};
})();
