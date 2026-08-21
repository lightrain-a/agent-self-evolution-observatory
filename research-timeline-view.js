(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-timeline"] = {
    eyebrow:{en:"Research history",zh:"科研进展历史"},
    title:{en:"Research Timeline",zh:"研究时间轴"},
    lead:{
      en:"A workload-first chronology of the complete Observatory research history. Each month is shown as its own table, with the newest month and newest day first by default. Open any day row to inspect that day’s events from earlier to later in China Standard Time (Asia/Shanghai, UTC+8).",
      zh:"按北京时间（Asia/Shanghai，UTC+8）回看 Observatory 从建立至今的完整研究历史。每个月单独一张表，默认最新月份、最新日期在前；每个研究日先压缩成一行，点开后再严格按时间从早到晚阅读当天发生的 Idea、实验、论文、系统更新与关闭过程。"
    },
    callout:{
      en:"This page is a read-only projection, not a scientific decision-maker. Runtime/API/provenance activity with zero authority remains system activity and cannot become a scientific result merely by appearing here.",
      zh:"本页只是只读历史投影，不参与科研裁决。运行、API 与追溯记录中原本没有科研权限的内容，进入时间轴后仍然没有科研权限；工程失败也不会被自动改写成科学失败。"
    },
    sections:[]
  };

  const CHINA_TZ = "Asia/Shanghai";
  const state = {importance:"all",type:"all",range:"all",research:"all",query:"",order:"desc"};
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

  const sortDayEvents = (events) => [...events].sort((a,b) => {
    const ap = a.time_precision === "date" ? 1 : 0, bp = b.time_precision === "date" ? 1 : 0;
    if (ap !== bp) return ap - bp;
    return (Date.parse(a.occurred_at)||0) - (Date.parse(b.occurred_at)||0);
  });
  const dayCounts = (events) => events.reduce((m,e)=>(m[e.event_class]=(m[e.event_class]||0)+1,m),{});
  const dayHeadline = (events) => {
    const ordered = sortDayEvents(events);
    const preferred = ordered.filter(e => e.importance === "key" && e.origin !== "git_daily_summary");
    const pool = preferred.length ? preferred : ordered.filter(e => e.origin !== "git_daily_summary" && e.event_class !== "system");
    const chosen = (pool.length ? pool : ordered).slice(0,3).map(e => localTitle(e)).filter(Boolean);
    return chosen.length ? chosen.join(" → ") : pick("当日以系统维护与追溯工作为主。","Primarily system/provenance work.");
  };
  const workloadBar = (events) => {
    const counts = dayCounts(events), total = Math.max(events.length,1);
    return `<div class="rt-workload-bar" aria-label="${pick("当日工作量构成","Daily workload composition")}">${Object.keys(classes).filter(k=>counts[k]).map(k=>`<i class="rt-work-${classes[k].tone}" style="width:${(counts[k]/total*100).toFixed(2)}%" title="${esc(labelClass(k))} ${counts[k]}"></i>`).join("")}</div>`;
  };
  const monthLabel = (month) => {
    const d = new Date(`${month}-15T12:00:00+08:00`);
    if (Number.isNaN(d.getTime())) return month;
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {year:"numeric",month:"long",timeZone:CHINA_TZ}).format(d);
  };
  const dayRows = (date,events) => {
    const ordered = sortDayEvents(events), counts = dayCounts(ordered);
    const tags = Object.entries(counts).map(([k,v])=>`<span>${esc(labelClass(k))} ${v}</span>`).join("");
    const keyChanges = ordered.filter(e=>e.importance === "key").length;
    const researchLines = new Set(ordered.map(e=>e.research_id).filter(Boolean)).size;
    const gitChanges = ordered.filter(e=>e.origin === "git_relevant_history").length;
    const artifactChanges = ordered.filter(e=>String(e.origin||"").startsWith("artifact")).length;
    const dateOnly = ordered.filter(e=>e.time_precision === "date");
    const exact = ordered.filter(e=>e.time_precision !== "date");
    const dateOnlyBlock = dateOnly.length ? `<div class="rt-date-only-note">${pick(`另有 ${dateOnly.length} 条记录只有日期精度，无法可靠判断当天先后，因此放在精确时间事件之后。`,`Another ${dateOnly.length} records have date-only precision and are shown after exact-time events.`)}</div>${dateOnly.map(eventRow).join("")}` : "";
    const thread = dayHeadline(ordered);
    return `<tr class="rt-day-row" id="timeline-${esc(date)}" data-rt-day-toggle="${esc(date)}" tabindex="0" aria-expanded="false"><td class="rt-table-date"><div class="rt-table-date-inner"><button type="button" class="rt-day-toggle" aria-label="${pick("展开当天详情","Open day details")}">＋</button><div><b>${esc(fmtDate(`${date}T12:00:00+08:00`))}</b><small>${esc(date)}</small></div></div></td><td class="rt-num rt-activity-count"><b>${ordered.length}</b><span>${pick("条","events")}</span></td><td class="rt-num"><b>${keyChanges}</b></td><td class="rt-num"><b>${gitChanges}</b></td><td class="rt-num"><b>${artifactChanges}</b></td><td class="rt-num"><b>${researchLines}</b></td><td class="rt-table-thread"><p>${esc(thread)}</p><div class="rt-day-tags">${tags}</div>${workloadBar(ordered)}</td></tr><tr class="rt-day-detail-row" data-rt-day-detail="${esc(date)}" hidden><td colspan="7"><div class="rt-day-expanded"><div class="rt-order-note">${pick("以下严格按北京时间从早到晚排列，不按 Idea / 实验 / 论文等类别重新分组，便于追踪“什么先发生 → 为什么后来改变研究或系统”。","Events below are strictly chronological rather than grouped by type.")}</div><div class="rt-day-events">${exact.map(eventRow).join("")}${dateOnlyBlock}</div></div></td></tr>`;
  };
  const monthTable = (month,dates,groups) => {
    const total = dates.reduce((n,date)=>n+(groups[date]?.length||0),0);
    return `<section class="rt-month" data-rt-month="${esc(month)}"><header class="rt-month-header"><div><h2>${esc(monthLabel(month))}</h2><span>${esc(month)} · ${pick("北京时间","China Standard Time")}</span></div><div><b>${dates.length}</b><span>${pick("个研究日","research days")}</span><b>${total}</b><span>${pick("条活动","activities")}</span></div></header><div class="rt-month-table-wrap"><table class="rt-month-table"><thead><tr><th>${pick("日期","Date")}</th><th>${pick("活动","Activity")}</th><th>${pick("关键变化","Key")}</th><th>${pick("代码 / 系统","Code / system")}</th><th>${pick("科研记录","Research")}</th><th>${pick("研究对象","Objects")}</th><th>${pick("主要脉络 / 工作量","Main thread / workload")}</th></tr></thead><tbody>${dates.map(date=>dayRows(date,groups[date])).join("")}</tbody></table></div></section>`;
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
  const controls = () => `<section class="rt-controls" aria-label="${pick("时间轴筛选","Timeline filters")}"><div class="rt-control-group"><b>${pick("显示层级","Detail level")}</b><div class="rt-segment"><button type="button" data-rt-importance="all" class="${state.importance==="all"?"active":""}">${pick(`全部 ${dataset().events.length} 条`,`All ${dataset().events.length}`)}</button><button type="button" data-rt-importance="key" class="${state.importance==="key"?"active":""}">${pick("只看关键事件","Key events only")}</button></div></div><div class="rt-control-group"><b>${pick("时间顺序","Chronology")}</b><div class="rt-segment"><button type="button" data-rt-order="asc" class="${state.order==="asc"?"active":""}">${pick("从早到晚 · 看因果","Old → new")}</button><button type="button" data-rt-order="desc" class="${state.order==="desc"?"active":""}">${pick("从新到旧 · 看最近","New → old")}</button></div></div><div class="rt-control-group"><b>${pick("时间范围","Range")}</b><div class="rt-segment">${[["all",pick("全部历史","All history")],["30",pick("近 30 天","30D")],["7",pick("近 7 天","7D")],["3",pick("近 3 天","3D")]].map(([v,l])=>`<button type="button" data-rt-range="${v}" class="${state.range===v?"active":""}">${l}</button>`).join("")}</div></div><label class="rt-select"><span>${pick("研究对象","Research")}</span><select id="timeline-research"><option value="all">${pick("全部研究对象","All research")}</option>${researchOptions()}</select></label><label class="rt-select"><span>${pick("事件类型","Event type")}</span><select id="timeline-type"><option value="all">${pick("全部类型","All types")}</option>${Object.keys(classes).map(k=>`<option value="${k}" ${state.type===k?"selected":""}>${esc(labelClass(k))}</option>`).join("")}</select></label></section>`;

  const feed = (events) => {
    const groups = grouped(events);
    const dates = Object.keys(groups).sort((a,b)=>state.order === "asc" ? a.localeCompare(b) : b.localeCompare(a));
    if (!dates.length) return `<div class="empty">${pick("没有符合当前筛选条件的时间事件。","No timeline events match the current filters.")}</div>`;
    const months = [...new Set(dates.map(date=>date.slice(0,7)))];
    return months.map(month=>monthTable(month,dates.filter(date=>date.startsWith(`${month}-`)),groups)).join("");
  };

  const activityHeatmap = (events) => {
    if (!events.length) return "";
    const counts = Object.fromEntries(Object.entries(grouped(events)).map(([d,rows])=>[d,rows.length]));
    const keys = Object.keys(counts).sort();
    const start = new Date(`${keys[0]}T00:00:00+08:00`), end = new Date(`${keys[keys.length-1]}T00:00:00+08:00`);
    const all=[]; for(let d=new Date(start); d<=end; d=new Date(d.getTime()+86400000)) all.push(chinaDateKey(d.toISOString()));
    const max=Math.max(1,...Object.values(counts));
    const weekdayRef=new Date(`${keys[0]}T12:00:00+08:00`), startColumn=((weekdayRef.getUTCDay()+6)%7)+1;
    return `<section class="rt-heatmap-panel"><div><b>${pick("每日工作量概览","Daily workload overview")}</b><span>${pick("颜色越深，当天记录的操作越多；点击日期可直接展开当天。","Darker cells mean more recorded activity; click a date to open it.")}</span></div><div class="rt-heat-weekdays"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div><div class="rt-heatmap">${all.map((day,i)=>{const n=counts[day]||0,level=n?Math.max(.12,n/max):0;return `<button type="button" class="rt-heat-cell" data-rt-day="${day}" style="--level:${level.toFixed(3)};${i===0?`grid-column-start:${startColumn};`:""}" title="${day} · ${n} ${pick("条活动","activities")}"><span>${Number(day.slice(-2))}</span><b>${n||""}</b></button>`}).join("")}</div></section>`;
  };

  const overview = () => {
    const s = dataset().summary || {};
    return `<section class="rt-overview"><div><b>${pick("完整历史 · 按月分表 · 北京时间 UTC+8","Full history · one table per month · Asia/Shanghai UTC+8")}</b><p>${pick(`当前投影共 ${s.events||0} 条事件，覆盖 ${s.days||0} 个有记录的研究日；其中 Research Memory 运行记录 ${s.runtime_memory_events||0} 条。历史按月份拆成独立表格，每个研究日先压缩成一行，便于先比较工作量与关键变化，再按需展开具体事件。`,`The projection contains ${s.events||0} events across ${s.days||0} recorded research days, including ${s.runtime_memory_events||0} Research Memory runtime events. History is split into one table per month, with each research day compressed into one row before its detailed events are opened on demand.`)}</p></div><div class="rt-overview-timezone"><strong>${pick("北京时间","China Standard Time")}</strong><span>Asia/Shanghai · UTC+8</span></div><div class="rt-legend" aria-label="${pick("事件颜色图例","Event color legend")}">${Object.keys(classes).map(k=>`<span class="rt-legend-item rt-legend-${classes[k].tone}" data-rt-legend="${classes[k].tone}"><i></i>${esc(labelClass(k))}</span>`).join("")}</div></section>`;
  };

  window.renderResearchTimeline = function(config){
    const events=visible();
    return `${pageHeader(config)}${overview()}<div id="research-timeline-controls">${controls()}</div><div id="research-timeline-stats">${stats(events)}</div><div id="research-timeline-heatmap">${activityHeatmap(events)}</div><div id="research-timeline-feed" class="rt-feed">${feed(events)}</div><section class="rt-policy-note"><b>${pick("读取规则","Reading rule")}</b><span>${pick("① 每个月单独一张表，默认最新月份、最新日期置顶；② 每个研究日先压缩为一行，直接比较活动量、关键变化、系统提交、科研记录和研究对象；③ 点开当天整行后，事件严格按北京时间从早到晚排列，不按类别重组；④ 无法可靠回填具体时刻的记录仍明确标记为日期精度；⑤ 系统工程与追溯记录不会因此获得科研权限。","Each month is a separate table, newest-first by default. Each research day is compressed into one row and expands into strictly chronological events. Date-only records remain explicitly marked when exact time cannot be recovered.")}</span></section>`;
  };

  const rerender = () => {
    const c=document.getElementById("research-timeline-controls"), s=document.getElementById("research-timeline-stats"), h=document.getElementById("research-timeline-heatmap"), f=document.getElementById("research-timeline-feed");
    const events=visible();
    if(c) c.innerHTML=controls();
    if(s) s.innerHTML=stats(events);
    if(h) h.innerHTML=activityHeatmap(events);
    if(f) f.innerHTML=feed(events);
    const counter=document.getElementById("result-count");
    if(counter) counter.textContent=pick(`${events.length} 条事件 · 北京时间`,`${events.length} events · UTC+8`);
    bindControls();
  };
  const toggleDay = (date,forceOpen) => {
    const row=document.getElementById(`timeline-${date}`), detail=document.querySelector(`[data-rt-day-detail="${date}"]`);
    if(!row || !detail) return;
    const shouldOpen = forceOpen === undefined ? detail.hidden : Boolean(forceOpen);
    detail.hidden=!shouldOpen;
    row.classList.toggle("is-open",shouldOpen);
    row.setAttribute("aria-expanded",shouldOpen ? "true" : "false");
    const toggle=row.querySelector(".rt-day-toggle");
    if(toggle) toggle.textContent=shouldOpen ? "−" : "＋";
  };
  const bindControls = () => {
    document.querySelectorAll("[data-rt-importance]").forEach(btn=>btn.addEventListener("click",()=>{state.importance=btn.dataset.rtImportance;rerender();}));
    document.querySelectorAll("[data-rt-range]").forEach(btn=>btn.addEventListener("click",()=>{state.range=btn.dataset.rtRange;rerender();}));
    document.querySelectorAll("[data-rt-order]").forEach(btn=>btn.addEventListener("click",()=>{state.order=btn.dataset.rtOrder;rerender();}));
    document.querySelectorAll("[data-rt-day-toggle]").forEach(row=>{
      row.addEventListener("click",()=>toggleDay(row.dataset.rtDayToggle));
      row.addEventListener("keydown",e=>{if(e.key === "Enter" || e.key === " "){e.preventDefault();toggleDay(row.dataset.rtDayToggle);}});
    });
    document.querySelectorAll("[data-rt-day]").forEach(btn=>btn.addEventListener("click",()=>{const date=btn.dataset.rtDay; toggleDay(date,true); const day=document.getElementById(`timeline-${date}`); if(day) day.scrollIntoView({behavior:"smooth",block:"center"});}));
    document.getElementById("timeline-type")?.addEventListener("change",e=>{state.type=e.target.value;rerender();});
    document.getElementById("timeline-research")?.addEventListener("change",e=>{state.research=e.target.value;rerender();});
  };
  window.bindResearchTimelineEvents = function(){rerender();};
  window.applyResearchTimelineFilters = function(query){state.query=raw(query);rerender();};
})();
