(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-timeline"] = {
    eyebrow:{en:"Research history",zh:"科研进展历史"},
    title:{en:"Research Timeline",zh:"研究时间轴"},
    lead:{
      en:"A read-only chronology of the complete Observatory research history. Events are grouped in China Standard Time (Asia/Shanghai, UTC+8). All recorded events are shown by default; expand any row for evidence, decision basis, boundaries, next actions, reopen conditions, provenance, and authority scope.",
      zh:"按北京时间（Asia/Shanghai，UTC+8）回看 Observatory 从建立至今的完整研究历史。页面默认展示全部已记录事件；每条事件仍保持折叠，点击后再查看证据、裁决依据、边界、下一步、重开条件、来源追溯与权限范围。"
    },
    callout:{
      en:"This page is a read-only projection, not a scientific decision-maker. Runtime/API/provenance activity with zero authority remains system activity and cannot become a scientific result merely by appearing here.",
      zh:"本页只是只读历史投影，不参与科研裁决。运行、API 与追溯记录中原本没有科研权限的内容，进入时间轴后仍然没有科研权限；工程失败也不会被自动改写成科学失败。"
    },
    sections:[]
  };

  const CHINA_TZ = "Asia/Shanghai";
  const state = {importance:"all",type:"all",range:"all",research:"all",query:""};
  const dataset = () => window.RESEARCH_TIMELINE || {events:[],summary:{}};
  const pick = (zh,en) => language === "zh" ? zh : en;
  const raw = (v) => String(v ?? "");
  const localText = (v) => raw(v?.[language] || v?.en || v?.zh || v);
  const localTitle = (e) => language === "zh" ? raw(e.title_zh || e.title) : raw(e.title || e.title_zh);
  const localResearch = (e) => language === "zh" ? raw(e.research_label_zh || e.research_id) : raw(e.research_id);
  const localNext = (e) => language === "zh" ? raw(e.next_action_zh || e.next_action) : raw(e.next_action);
  const localReopen = (e) => language === "zh" ? raw(e.reopen_condition_zh || e.reopen_condition) : raw(e.reopen_condition);
  const localAuthorityScope = (e) => language === "zh" ? raw(e.authority?.scope_zh || e.authority?.scope) : raw(e.authority?.scope);

  const classes = {
    idea:{en:"Idea / problem",zh:"Idea / 问题发现",tone:"idea"},
    experiment:{en:"Experiment",zh:"实验 / 验证",tone:"experiment"},
    scientific:{en:"Scientific result",zh:"科学结论",tone:"scientific"},
    paper:{en:"Paper",zh:"论文推进",tone:"paper"},
    closure:{en:"Closure",zh:"停止 / 关闭",tone:"closure"},
    blocker:{en:"Blocker / hold",zh:"阻断 / 暂缓",tone:"blocker"},
    system:{en:"System / provenance",zh:"系统 / 追溯",tone:"system"}
  };
  const labelClass = (value) => pick(classes[value]?.zh || value, classes[value]?.en || value);

  const statusZh = (value) => {
    const s = raw(value), u = s.toUpperCase();
    if (!s || u === "ARTIFACT_RECORDED") return "已记录";
    if (u === "COMMIT_RECORDED") return "系统里程碑已记录";
    if (u === "DAILY_ACTIVITY_RECORDED") return "当日系统活动已记录";
    if (u.includes("READY_TO_SUBMIT")) return "论文就绪，待人工确认并提交";
    if (u.includes("SUBMISSION") && (u.includes("READY") || u.includes("PASS"))) return "投稿材料已就绪";
    if (u.includes("PAPER") && u.includes("READY")) return "论文阶段已就绪";
    if (u.includes("ADVANCE") || u.startsWith("GO_")) return "通过当前门槛，继续推进";
    if (u.includes("SUPPORTED")) return "已有证据支持";
    if (u.includes("MERGE")) return "已合并，不再独立推进";
    if (u.includes("INCONCLUSIVE")) return "证据不足，当前不可判定";
    if (u.includes("INVALID")) return "当前实现无效，不更新科学结论";
    if (u.includes("HOLD") || u.includes("WAIT") || u.includes("PENDING")) return "暂缓，等待条件满足";
    if (u.includes("BLOCK")) return "已阻断";
    if (u.includes("STOP") || u.includes("TERMINAT") || u.includes("DEAD_END") || u.includes("REJECT") || u.includes("FAIL")) return "已停止 / 关闭";
    if (u.includes("PASS") || u.includes("READY") || u.includes("CLEAR")) return "通过 / 就绪";
    if (u.includes("REVIEW")) return "已完成评审";
    if (u.includes("DESIGN")) return "进入设计阶段";
    return s;
  };
  const statusDisplay = (value) => language === "zh" ? statusZh(value) : raw(value || "RECORDED");

  const chinaDateKey = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return raw(iso).slice(0,10) || "unknown";
    const parts = new Intl.DateTimeFormat("en-US",{timeZone:CHINA_TZ,year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(d);
    const map = Object.fromEntries(parts.map(p=>[p.type,p.value]));
    return `${map.year}-${map.month}-${map.day}`;
  };
  const fmtDate = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return raw(iso).slice(0,10);
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {year:"numeric",month:"long",day:"numeric",weekday:"short",timeZone:CHINA_TZ}).format(d);
  };
  const fmtTime = (e) => {
    if (e.time_precision === "date") return pick("日期记录","date record");
    const d = new Date(e.occurred_at);
    if (Number.isNaN(d.getTime())) return "--:--";
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false,timeZone:CHINA_TZ}).format(d);
  };

  const metricLabelZh = (label) => {
    const l = raw(label), key = l.toLowerCase();
    const exact = {
      "api calls":"API 调用次数","research objects":"研究对象数","lineage edges":"谱系边数","preflight-ready objects":"可进入 preflight 的对象数",
      "recorded call failures":"记录到的调用失败","experiment run":"是否运行实验","closure layer":"关闭层级","fisher p":"Fisher 检验 p 值",
      "exact p":"精确检验 p 值","replay agreement":"回放一致率","official review":"正式评审","supplement tests":"补充材料测试",
      "paper evidence":"论文证据状态","claims":"主张支持数","qa":"质量检查","evidence debt":"未完成证据项","human signoff pending":"是否等待作者确认",
      "raw seeds":"原始 Idea seed 数","pre-f0 queued":"Pre-F0 候选数","support ready":"支持条件已就绪","support holds":"因支持不足暂缓",
      "formal launchable":"当前可启动正式实验数","commit":"提交","提交":"提交","提交次数":"提交次数","最新提交":"最新提交","代表变更":"代表变更",
      "原始状态码":"原始状态码"
    };
    if (exact[key]) return exact[key];
    if (key.startsWith("disposition ·")) return `处置结果 · ${l.split("·").slice(1).join("·").trim()}`;
    if (language === "zh" && !/[\u4e00-\u9fff]/.test(l) && /count|number|total|items|records|ideas|candidates|reviews|rows|calls|edges|files|runs/.test(key)) return `${l}（数量）`;
    return l;
  };

  const latestMs = () => Math.max(0,...dataset().events.map(e => Date.parse(e.occurred_at)||0));
  const searchable = (e) => [e.research_id,e.research_label_zh,e.title,e.title_zh,e.state_before,e.state_after,localText(e.summary),localText(e.why),localText(e.limitation),e.next_action,e.next_action_zh,e.reopen_condition,e.reopen_condition_zh].join(" ").toLowerCase();
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
    const key = chinaDateKey(e.occurred_at);
    (acc[key] ||= []).push(e);
    return acc;
  },{});

  const classBadge = (e) => `<span class="rt-badge rt-${esc(classes[e.event_class]?.tone || "system")}">${esc(labelClass(e.event_class))}</span>`;
  const authorityBadge = (e) => e.authority?.scientific
    ? `<span class="rt-authority scoped">${pick("原始记录已有窄范围科研权限","Source has scoped scientific authority")}</span>`
    : `<span class="rt-authority zero">${pick("本事件不新增科研权限","No new scientific authority")}</span>`;
  const evidence = (items=[]) => items.length ? `<div class="rt-evidence">${items.map(item=>`<div><b>${esc(language === "zh" ? metricLabelZh(item.label) : item.label)}</b><span>${esc(item.value)}</span></div>`).join("")}</div>` : "";
  const detailBlock = (labelZh,labelEn,value,cls="") => value ? `<section class="rt-detail-block ${cls}"><b>${pick(labelZh,labelEn)}</b><p>${esc(value)}</p></section>` : "";
  const linkLabel = (label) => {
    if (language !== "zh") return raw(label);
    return ({paper:"论文",experiments:"实验",research:"研究方向",system:"科研系统"})[raw(label)] || raw(label);
  };
  const sourceLinks = (e) => {
    const srcs = (e.sources||[]).map(s=>s.public === false
      ? `<span class="rt-source rt-source-private"><b>${pick("非公开来源","Non-public source")}</b><code>sha256:${esc(raw(s.sha256).slice(0,12))} · ${pick("仅用于哈希审计","hash audit only")}</code></span>`
      : `<a class="rt-source" href="${esc(s.path)}" target="_blank" rel="noopener"><b>${esc(s.path.split("/").pop())}</b><code>sha256:${esc(raw(s.sha256).slice(0,12))}</code></a>`).join("");
    const links = (e.links||[]).map(l=>`<a class="link-btn" href="${esc(l.href)}">${esc(linkLabel(l.label))} ↗</a>`).join("");
    if (!srcs && !links) return "";
    return `<div class="rt-links">${srcs}${links}</div>`;
  };

  const eventRow = (e) => {
    const before = e.state_before ? `<div class="rt-transition"><div><span>${pick("之前","Before")}</span><strong>${esc(statusDisplay(e.state_before))}</strong><small>${language === "zh" ? esc(e.state_before) : ""}</small></div><i>→</i><div><span>${pick("现在","Now")}</span><strong>${esc(statusDisplay(e.state_after))}</strong><small>${language === "zh" ? esc(e.state_after) : ""}</small></div></div>` : "";
    const summary = localText(e.summary);
    const why = localText(e.why);
    const limitation = localText(e.limitation);
    return `<details class="rt-event" data-event-id="${esc(e.event_id)}" data-class="${esc(e.event_class)}"><summary><time>${esc(fmtTime(e))}</time><span class="rt-dot" aria-hidden="true"></span><div class="rt-summary-main"><div class="rt-summary-meta">${classBadge(e)}<span>${esc(localResearch(e))}</span>${e.importance === "key" ? `<em>${pick("关键","KEY")}</em>`:""}</div><strong>${esc(localTitle(e))}</strong><p>${esc(summary)}</p></div><div class="rt-state"><span>${pick("当前状态","STATE")}</span><b>${esc(statusDisplay(e.state_after || "RECORDED"))}</b>${language === "zh" ? `<small>${esc(e.state_after || "RECORDED")}</small>` : ""}</div></summary><div class="rt-expanded">${before}${detailBlock("发生了什么","What changed",summary,"change")}${detailBlock("为什么这样裁决","Decision basis",why)}${detailBlock("边界 / 不能扩大到什么","Boundary / unsupported scope",limitation,"boundary")}${detailBlock("下一步","Next action",localNext(e),"next")}${detailBlock("什么情况下重开","Reopen only if",localReopen(e),"reopen")}${evidence(e.evidence)}<div class="rt-authority-row">${authorityBadge(e)}<span>${esc(localAuthorityScope(e) || pick("只读历史投影","read-only projection"))}</span></div>${sourceLinks(e)}</div></details>`;
  };

  const daySection = (date,events) => {
    const counts = events.reduce((m,e)=>(m[e.event_class]=(m[e.event_class]||0)+1,m),{});
    const tags = Object.entries(counts).map(([k,v])=>`<span>${esc(labelClass(k))} ${v}</span>`).join("");
    return `<section class="rt-day" id="timeline-${esc(date)}"><header><div><b>${esc(fmtDate(`${date}T12:00:00+08:00`))}</b><small>${esc(date)} · ${pick("北京时间","China Standard Time")}</small></div><div>${tags}</div></header><div class="rt-day-events">${events.map(eventRow).join("")}</div></section>`;
  };

  const stats = (events) => {
    const days = new Set(events.map(e=>chinaDateKey(e.occurred_at))).size;
    const ideas = events.filter(e=>e.event_class === "idea").length;
    const experiments = events.filter(e=>e.event_class === "experiment").length;
    const advances = events.filter(e=>e.event_class === "scientific" || e.event_class === "paper").length;
    const stops = events.filter(e=>e.event_class === "closure" || e.event_class === "blocker").length;
    return `<div class="rt-stats"><article><b>${events.length}</b><span>${pick("当前展示事件","visible events")}</span></article><article><b>${days}</b><span>${pick("有记录的研究日","recorded research days")}</span></article><article><b>${ideas}</b><span>${pick("Idea / 问题发现","idea / problem events")}</span></article><article><b>${experiments}</b><span>${pick("实验 / 验证","experiment events")}</span></article><article><b>${advances}</b><span>${pick("科学结论 / 论文推进","scientific / paper advances")}</span></article><article><b>${stops}</b><span>${pick("停止 / 暂缓","closures / holds")}</span></article></div>`;
  };

  const researchOptions = () => [...new Set(dataset().events.map(e=>e.research_id).filter(Boolean))].sort((a,b)=>a.localeCompare(b)).map(r=>{
    const sample = dataset().events.find(e=>e.research_id===r);
    const label = language === "zh" ? raw(sample?.research_label_zh || r) : r;
    return `<option value="${esc(r)}" ${state.research===r?"selected":""}>${esc(label)}</option>`;
  }).join("");
  const controls = () => `<section class="rt-controls" aria-label="${pick("时间轴筛选","Timeline filters")}"><div class="rt-control-group"><b>${pick("显示层级","Detail level")}</b><div class="rt-segment"><button type="button" data-rt-importance="all" class="${state.importance==="all"?"active":""}">${pick(`全部 ${dataset().events.length} 条`,`All ${dataset().events.length}`)}</button><button type="button" data-rt-importance="key" class="${state.importance==="key"?"active":""}">${pick("只看关键事件","Key events only")}</button></div></div><div class="rt-control-group"><b>${pick("时间范围","Range")}</b><div class="rt-segment">${[["all",pick("全部历史","All history")],["30",pick("近 30 天","30D")],["7",pick("近 7 天","7D")],["3",pick("近 3 天","3D")]].map(([v,l])=>`<button type="button" data-rt-range="${v}" class="${state.range===v?"active":""}">${l}</button>`).join("")}</div></div><label class="rt-select"><span>${pick("研究对象","Research")}</span><select id="timeline-research"><option value="all">${pick("全部研究对象","All research")}</option>${researchOptions()}</select></label><label class="rt-select"><span>${pick("事件类型","Event type")}</span><select id="timeline-type"><option value="all">${pick("全部类型","All types")}</option>${Object.keys(classes).map(k=>`<option value="${k}" ${state.type===k?"selected":""}>${esc(labelClass(k))}</option>`).join("")}</select></label></section>`;

  const feed = (events) => {
    const groups = grouped(events);
    const dates = Object.keys(groups).sort().reverse();
    if (!dates.length) return `<div class="empty">${pick("没有符合当前筛选条件的时间事件。","No timeline events match the current filters.")}</div>`;
    return dates.map(date=>daySection(date,groups[date])).join("");
  };

  const overview = () => {
    const s = dataset().summary || {};
    return `<section class="rt-overview"><div><b>${pick("完整历史 · 默认全部展示 · 北京时间 UTC+8","Full history · all events by default · Asia/Shanghai UTC+8")}</b><p>${pick(`当前投影共 ${s.events||0} 条事件，覆盖 ${s.days||0} 个有记录的研究日；其中 Research Memory 运行记录 ${s.runtime_memory_events||0} 条。历史从 Observatory 早期系统建设开始，并继续覆盖结构化 Idea、实验、论文、关闭与治理记录。每条记录默认折叠，避免完整历史一次展开造成阅读负担。`,`The projection contains ${s.events||0} events across ${s.days||0} recorded research days, including ${s.runtime_memory_events||0} Research Memory runtime events. It begins with early Observatory development and continues through structured idea, experiment, paper, closure, and governance artifacts.`)}</p></div><div class="rt-overview-timezone"><strong>${pick("北京时间","China Standard Time")}</strong><span>Asia/Shanghai · UTC+8</span></div><div class="rt-legend">${Object.keys(classes).map(k=>`<span class="rt-legend-item"><i class="rt-${classes[k].tone}"></i>${esc(labelClass(k))}</span>`).join("")}</div></section>`;
  };

  window.renderResearchTimeline = function(config){
    return `${pageHeader(config)}${overview()}<div id="research-timeline-controls">${controls()}</div><div id="research-timeline-stats">${stats(visible())}</div><div id="research-timeline-feed" class="rt-feed">${feed(visible())}</div><section class="rt-policy-note"><b>${pick("读取规则","Reading rule")}</b><span>${pick("① 所有日期和具体时间都按北京时间显示；② 只有原始记录明确存在旧状态时才显示“之前 → 现在”，不会根据结果倒推旧状态；③ 完整历史包含系统工程与追溯记录，但这些记录不会获得科研权限；④ 中文页优先解释阶段含义，原始英文状态码和技术字段保留用于审计。","All dates use Asia/Shanghai. Before→Now is shown only when an explicit prior state exists. Engineering/provenance history remains non-authoritative. Raw technical codes are preserved for auditability.")}</span></section>`;
  };

  const rerender = () => {
    const c=document.getElementById("research-timeline-controls"), s=document.getElementById("research-timeline-stats"), f=document.getElementById("research-timeline-feed");
    const events=visible();
    if(c) c.innerHTML=controls();
    if(s) s.innerHTML=stats(events);
    if(f) f.innerHTML=feed(events);
    const counter=document.getElementById("result-count");
    if(counter) counter.textContent=pick(`${events.length} 条事件 · 北京时间`,`${events.length} events · UTC+8`);
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
