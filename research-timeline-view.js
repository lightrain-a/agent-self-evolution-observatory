(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-timeline"] = {
    eyebrow:{en:"Research history",zh:"研究历史"},
    title:{en:"Research Timeline",zh:"研究时间轴"},
    lead:{en:"A read-only chronology of how research states changed over time. Key events are shown first; expand any row to inspect the decision basis, evidence, boundary, next action, reopen condition, source artifact, and authority scope.",zh:"按时间回看研究状态如何变化。默认只展示关键事件；点击任意事件即可展开原始裁决依据、证据、边界、下一步、重开条件、来源 artifact 与 authority 范围。"},
    callout:{en:"This page is a projection, not a scientific decision-maker. Runtime/API/provenance activity with zero authority remains System activity and cannot become a scientific result merely by appearing here.",zh:"本页只是只读投影，不参与科研裁决。runtime / API / provenance 中 scientific authority=0 的活动始终只显示为 System 事件，不会因为进入时间轴就变成科研结论。"},
    sections:[]
  };

  const state = {importance:"key",type:"all",range:"7",research:"all",query:""};
  const dataset = () => window.RESEARCH_TIMELINE || {events:[],summary:{}};
  const pick = (zh,en) => language === "zh" ? zh : en;
  const raw = (v) => String(v ?? "");
  const localText = (v) => raw(v?.[language] || v?.en || v?.zh || v);
  const classes = {
    scientific:{en:"Scientific",zh:"科学进展",tone:"scientific"},
    paper:{en:"Paper",zh:"论文进展",tone:"paper"},
    closure:{en:"Closure",zh:"科学关闭",tone:"closure"},
    blocker:{en:"Blocker",zh:"阻断",tone:"blocker"},
    system:{en:"System / provenance",zh:"系统 / provenance",tone:"system"}
  };
  const labelClass = (value) => pick(classes[value]?.zh || value, classes[value]?.en || value);
  const fmtDate = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return raw(iso).slice(0,10);
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {month:"short",day:"numeric",weekday:"short",timeZone:"UTC"}).format(d);
  };
  const fmtTime = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "--:--";
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {hour:"2-digit",minute:"2-digit",hour12:false,timeZone:"UTC"}).format(d);
  };
  const latestMs = () => Math.max(0,...dataset().events.map(e => Date.parse(e.occurred_at)||0));
  const searchable = (e) => [e.research_id,e.title,e.state_before,e.state_after,localText(e.summary),localText(e.why),localText(e.limitation),e.next_action,e.reopen_condition].join(" ").toLowerCase();
  const visible = () => {
    const latest = latestMs();
    const days = state.range === "all" ? Infinity : Number(state.range || 7);
    const floor = Number.isFinite(days) ? latest - (days - 1) * 86400000 : 0;
    const q = state.query.trim().toLowerCase();
    return dataset().events.filter(e => {
      if (state.importance === "key" && e.importance !== "key") return false;
      if (state.type !== "all" && e.event_class !== state.type) return false;
      if (state.research !== "all" && e.research_id !== state.research) return false;
      if ((Date.parse(e.occurred_at)||0) < floor) return false;
      if (q && !searchable(e).includes(q)) return false;
      return true;
    });
  };
  const grouped = (events) => events.reduce((acc,e) => {
    const key = raw(e.occurred_at).slice(0,10) || "unknown";
    (acc[key] ||= []).push(e);
    return acc;
  },{});
  const classBadge = (e) => `<span class="rt-badge rt-${esc(classes[e.event_class]?.tone || "system")}">${esc(labelClass(e.event_class))}</span>`;
  const authorityBadge = (e) => e.authority?.scientific
    ? `<span class="rt-authority scoped">${pick("已有 scoped scientific authority","Scoped scientific authority")}</span>`
    : `<span class="rt-authority zero">${pick("本事件不新增 scientific authority","No new scientific authority")}</span>`;
  const evidence = (items=[]) => items.length ? `<div class="rt-evidence">${items.map(item=>`<div><b>${esc(item.label)}</b><span>${esc(item.value)}</span></div>`).join("")}</div>` : "";
  const detailBlock = (labelZh,labelEn,value,cls="") => value ? `<section class="rt-detail-block ${cls}"><b>${pick(labelZh,labelEn)}</b><p>${esc(value)}</p></section>` : "";
  const sourceLinks = (e) => {
    const srcs = (e.sources||[]).map(s=>s.public === false
      ? `<span class="rt-source rt-source-private"><b>${esc(s.path.split("/").pop())}</b><code>sha256:${esc(raw(s.sha256).slice(0,12))} · ${pick("仅哈希审计","hash audit only")}</code></span>`
      : `<a class="rt-source" href="${esc(s.path)}" target="_blank" rel="noopener"><b>${esc(s.path.split("/").pop())}</b><code>sha256:${esc(raw(s.sha256).slice(0,12))}</code></a>`).join("");
    const links = (e.links||[]).map(l=>`<a class="link-btn" href="${esc(l.href)}">${esc(l.label)} ↗</a>`).join("");
    if (!srcs && !links) return "";
    return `<div class="rt-links">${srcs}${links}</div>`;
  };
  const eventRow = (e) => {
    const before = e.state_before ? `<div class="rt-transition"><div><span>${pick("之前","Before")}</span><strong>${esc(e.state_before)}</strong></div><i>→</i><div><span>${pick("现在","Now")}</span><strong>${esc(e.state_after)}</strong></div></div>` : "";
    const summary = localText(e.summary);
    const why = localText(e.why);
    const limitation = localText(e.limitation);
    return `<details class="rt-event" data-event-id="${esc(e.event_id)}" data-class="${esc(e.event_class)}"><summary><time>${esc(fmtTime(e.occurred_at))}</time><span class="rt-dot" aria-hidden="true"></span><div class="rt-summary-main"><div class="rt-summary-meta">${classBadge(e)}<span>${esc(e.research_id)}</span>${e.importance === "key" ? `<em>${pick("关键","KEY")}</em>`:""}</div><strong>${esc(e.title)}</strong><p>${esc(summary)}</p></div><div class="rt-state"><span>${pick("状态","STATE")}</span><b>${esc(e.state_after || "RECORDED")}</b></div></summary><div class="rt-expanded">${before}${detailBlock("发生了什么","What changed",summary,"change")}${detailBlock("原始裁决依据","Decision basis",why)}${detailBlock("边界 / 不能扩大到什么","Boundary / unsupported scope",limitation,"boundary")}${detailBlock("下一步","Next action",e.next_action,"next")}${detailBlock("什么情况下重开","Reopen only if",e.reopen_condition,"reopen")}${evidence(e.evidence)}<div class="rt-authority-row">${authorityBadge(e)}<span>${esc(e.authority?.scope || "projection-only")}</span></div>${sourceLinks(e)}</div></details>`;
  };
  const daySection = (date,events) => {
    const counts = events.reduce((m,e)=>(m[e.event_class]=(m[e.event_class]||0)+1,m),{});
    const tags = Object.entries(counts).map(([k,v])=>`<span>${esc(labelClass(k))} ${v}</span>`).join("");
    return `<section class="rt-day" id="timeline-${esc(date)}"><header><div><b>${esc(fmtDate(`${date}T12:00:00Z`))}</b><small>${esc(date)}</small></div><div>${tags}</div></header><div class="rt-day-events">${events.map(eventRow).join("")}</div></section>`;
  };
  const stats = (events) => {
    const days = new Set(events.map(e=>e.occurred_at.slice(0,10))).size;
    const scientific = events.filter(e=>e.event_class === "scientific").length;
    const paper = events.filter(e=>e.event_class === "paper").length;
    const closures = events.filter(e=>e.event_class === "closure").length;
    const system = events.filter(e=>e.event_class === "system").length;
    return `<div class="rt-stats"><article><b>${events.length}</b><span>${pick("当前可见事件","visible events")}</span></article><article><b>${days}</b><span>${pick("研究日","research days")}</span></article><article><b>${scientific + paper}</b><span>${pick("科学 / 论文推进","scientific / paper advances")}</span></article><article><b>${closures}</b><span>${pick("关闭事件","closures")}</span></article><article><b>${system}</b><span>${pick("系统 / provenance","system / provenance")}</span></article></div>`;
  };
  const researchOptions = () => [...new Set(dataset().events.map(e=>e.research_id).filter(Boolean))].sort((a,b)=>a.localeCompare(b)).map(r=>`<option value="${esc(r)}" ${state.research===r?"selected":""}>${esc(r)}</option>`).join("");
  const controls = () => `<section class="rt-controls" aria-label="Timeline filters"><div class="rt-control-group"><b>${pick("显示层级","Detail level")}</b><div class="rt-segment"><button type="button" data-rt-importance="key" class="${state.importance==="key"?"active":""}">${pick("关键事件","Key events")}</button><button type="button" data-rt-importance="all" class="${state.importance==="all"?"active":""}">${pick(`全部 ${dataset().events.length} 条`,`All ${dataset().events.length}`)}</button></div></div><div class="rt-control-group"><b>${pick("时间范围","Range")}</b><div class="rt-segment">${[["3","3D"],["7","7D"],["30","30D"],["all",pick("全部","All")]].map(([v,l])=>`<button type="button" data-rt-range="${v}" class="${state.range===v?"active":""}">${l}</button>`).join("")}</div></div><label class="rt-select"><span>${pick("研究对象","Research")}</span><select id="timeline-research"><option value="all">${pick("全部研究","All research")}</option>${researchOptions()}</select></label><label class="rt-select"><span>${pick("事件类型","Event type")}</span><select id="timeline-type"><option value="all">${pick("全部类型","All types")}</option>${Object.keys(classes).map(k=>`<option value="${k}" ${state.type===k?"selected":""}>${esc(labelClass(k))}</option>`).join("")}</select></label></section>`;
  const feed = (events) => {
    const groups = grouped(events);
    const dates = Object.keys(groups).sort().reverse();
    if (!dates.length) return `<div class="empty">${pick("没有符合当前筛选条件的时间事件。","No timeline events match the current filters.")}</div>`;
    return dates.map(date=>daySection(date,groups[date])).join("");
  };
  const overview = () => {
    const data = dataset(), s = data.summary || {};
    return `<section class="rt-overview"><div><b>${pick("真实 artifact 驱动的只读历史","Read-only history derived from real artifacts")}</b><p>${pick(`当前投影包含 ${s.events||0} 条事件、覆盖 ${s.days||0} 个研究日。默认只展示关键事件；大量历史 closure 和 P0 记录只有切到“全部”后才出现。`,`The projection contains ${s.events||0} events across ${s.days||0} research days. Key events are shown by default; detailed historical closures and P0 records appear only in All events.`)}</p></div><div class="rt-legend">${Object.keys(classes).map(k=>`<span class="rt-legend-item"><i class="rt-${classes[k].tone}"></i>${esc(labelClass(k))}</span>`).join("")}</div></section>`;
  };

  window.renderResearchTimeline = function(config){
    return `${pageHeader(config)}${overview()}<div id="research-timeline-controls">${controls()}</div><div id="research-timeline-stats">${stats(visible())}</div><div id="research-timeline-feed" class="rt-feed">${feed(visible())}</div><section class="rt-policy-note"><b>${pick("读取规则","Reading rule")}</b><span>${pick("未显式记录 Before 状态时，本页宁可省略 Before→Now，也不会根据文件名或结果反推一个旧状态。System/provenance 失败也不会自动变成 scientific failure。","If an explicit Before state is absent, the page omits Before→Now rather than inferring a prior state from filenames or outcomes. System/provenance failures never auto-convert into scientific failures.")}</span></section>`;
  };
  const rerender = () => {
    const c=document.getElementById("research-timeline-controls"), s=document.getElementById("research-timeline-stats"), f=document.getElementById("research-timeline-feed");
    const events=visible();
    if(c) c.innerHTML=controls();
    if(s) s.innerHTML=stats(events);
    if(f) f.innerHTML=feed(events);
    const counter=document.getElementById("result-count");
    if(counter) counter.textContent=pick(`${events.length} 条事件`,`${events.length} events`);
    bindControls();
  };
  const bindControls = () => {
    document.querySelectorAll("[data-rt-importance]").forEach(btn=>btn.addEventListener("click",()=>{state.importance=btn.dataset.rtImportance;rerender();}));
    document.querySelectorAll("[data-rt-range]").forEach(btn=>btn.addEventListener("click",()=>{state.range=btn.dataset.rtRange;rerender();}));
    document.getElementById("timeline-type")?.addEventListener("change",e=>{state.type=e.target.value;rerender();});
    document.getElementById("timeline-research")?.addEventListener("change",e=>{state.research=e.target.value;rerender();});
  };
  window.bindResearchTimelineEvents = function(){rerender();};
  window.applyResearchTimelineFilters = function(query){state.query=raw(query);rerender();};
})();
