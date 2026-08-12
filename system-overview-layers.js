(() => {
  const pick=(zh,en)=>language==="zh"?zh:en;
  const api=window.SYSTEM_OVERVIEW_SECTIONS=window.SYSTEM_OVERVIEW_SECTIONS||{};
  const text=(value)=>typeof value==="object"&&value!==null?(language==="zh"?(value.zh||value.en):(value.en||value.zh)):String(value||"");
  api.renderSystemLayers=function(state){
    const architecture=state.system_architecture||{};
    const layers=architecture.functional_layers||[];
    const rows=layers.map((layer,index)=>`<article><span>${layer.index||index+1}</span><div><small>${esc(String(layer.key||"layer").toUpperCase())}</small><b>${esc(text(layer.label))}</b><p>${esc(text(layer.mandate))}</p><footer><strong>${layer.component_count||0}</strong><em>${pick("个主责组件","primary components")}</em></footer></div></article>`).join("");
    const summary=architecture.summary||{};
    return `<section class="system-layers system-section"><div class="preflight-heading"><div><span class="system-kicker">BACKEND ARCHITECTURE MANIFEST</span><h3>${pick("一条时间主流程 + 六个职责层","One temporal lifecycle + six responsibility layers")}</h3><p>${pick("11 步 Paper-first 生命周期回答“研究什么时候可以继续”；六个职责层回答“后端哪一层负责什么”。P0-System v2 的 7-stage 只是 Scientific Validation 层内部的实验状态机，不是第二套总流程。","The 11-stage paper-first lifecycle answers when research may advance; the six functional layers answer which backend layer owns each responsibility. The seven-stage P0-System v2 machine is nested inside Scientific Validation, not a competing top-level lifecycle.")}</p></div><div class="preflight-lock"><b>${summary.assigned_components||0}/${summary.components||0}</b><span>${pick("组件已归责","components assigned")}</span></div></div><div class="system-layer-list">${rows}</div><div class="system-retro-note"><b>${pick("唯一架构真源：","Architecture source of truth:")}</b> <code>research_pipeline/system_architecture.py</code> · ${summary.temporal_stages||0} ${pick("个时间阶段","temporal stages")} · ${summary.functional_layers||0} ${pick("个职责层","functional layers")} · ${summary.unassigned_components||0} ${pick("个未归责组件","unassigned components")}</div></section>`;
  };
})();
