(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-timeline"] = {
    eyebrow:{en:"Research history",zh:"科研进展历史"},
    title:{en:"Research Timeline",zh:"研究时间轴"},
    lead:{
      en:"A workload-first chronology of the complete Observatory research history. Each month is shown as its own table, with the newest month and newest day first by default. Open any day row to inspect that day’s events from earlier to later.",
      zh:"回看 Observatory 从建立至今的完整研究历史。每个月单独一张表，默认最新月份、最新日期在前；每个研究日先压缩成一行，点开后再严格按时间从早到晚阅读当天发生的研究问题、实验、论文、系统更新与关闭过程。"
    },
    callout:{
      en:"This page is a read-only projection, not a scientific decision-maker. Runtime/API/provenance activity with zero authority remains system activity and cannot become a scientific result merely by appearing here.",
      zh:"本页只是只读历史投影，不参与科研裁决。运行、API 与追溯记录中原本没有科研权限的内容，进入时间轴后仍然没有科研权限；工程失败也不会被自动改写成科学失败。"
    },
    sections:[]
  };

  const CHINA_TZ = "Asia/Shanghai";
  const state = {importance:"all",type:"all",range:"all",research:"all",category:"all",query:"",order:"desc"};
  const dataset = () => window.RESEARCH_TIMELINE || {events:[],summary:{}};
  const initialParams = new URLSearchParams(window.location.search || "");
  if (initialParams.get("research")) state.research=`ri:${initialParams.get("research")}`;
  else if (initialParams.get("paper")) state.research=`paper:${initialParams.get("paper")}`;
  if (/^[A-G]$/i.test(initialParams.get("category")||"")) state.category=initialParams.get("category").toUpperCase();
  const pick = (zh,en) => language === "zh" ? zh : en;
  const raw = (v) => String(v ?? "");
  const zhPhraseMap = {
    "Default research timeline to Chinese":"时间轴默认显示中文",
    "Preserve full timeline in shallow Pages builds":"保留完整时间轴历史",
    "Expand timeline with full China-time history":"补全时间轴完整历史",
    "Add read-only research timeline view":"新增只读研究时间轴",
    "Add briefing-first idea portfolio view":"新增面向汇报的研究问题组合视图",
    "Show current final idea statuses":"展示当前研究问题终态",
    "Normalize numbered closure terminology":"统一编号关闭术语",
    "Harden closure ledger browser assertion":"加强关闭台账浏览器校验",
    "Merge closure records into numbered idea ledger":"将关闭记录合并进编号研究问题台账",
    "Expand CVPR candidate portfolio and add Friday decision board":"扩展 CVPR 候选组合并新增周五决策看板",
    "Expand self-evolution portfolio to twenty vetted ideas":"将自进化候选组合扩展至 20 个已审查研究问题",
    "Add published-paper historical overview":"新增已发表论文历史概览",
    "Add literature evidence to direction map":"为研究方向图谱补充文献证据",
    "Replace FakeMark R2 archive with fully audited reviewer-closure package.":"用完整审计的评审闭环包替换 FakeMark R2 归档",
    "Publish minimal FakeMark R2 submission package.":"发布 FakeMark R2 最小投稿包",
    "Prepare gated P0 experiment queue":"准备受门控的 P0 实验队列",
    "idea-discovery-v3-external-reviews":"研究问题发现 v3 外部评审",
    "current-final-ideas":"当前研究问题终态",
    "p0-offline-qualification":"P0 离线资格验证",
    "Canonical 双漏斗 研究问题 发现状态快照":"规范双漏斗研究问题发现状态快照"
  };
  const zhUiText = (value) => {
    let text = raw(value).replace(/北京时间/g,"").replace(/\bResearch Memory\b/g,"科研记忆").replace(/\bIdea\b/g,"研究问题");
    Object.entries(zhPhraseMap).forEach(([en,zh])=>{ text=text.split(en).join(zh); });
    return text.replace(/\s{2,}/g," ").replace(/（\s*，/g,"（").trim();
  };
  const localText = (v) => language === "zh" ? zhUiText(v?.zh || v?.en || v) : raw(v?.en || v?.zh || v);
  const localTitle = (e) => language === "zh" ? zhUiText(e.title_zh || e.title) : raw(e.title || e.title_zh);
  const localResearch = (e) => language === "zh" ? zhUiText(e.research_label_zh || e.research_id) : raw(e.research_id);
  const localNext = (e) => language === "zh" ? zhUiText(e.next_action_zh || e.next_action) : raw(e.next_action);
  const localReopen = (e) => language === "zh" ? zhUiText(e.reopen_condition_zh || e.reopen_condition) : raw(e.reopen_condition);
  const localAuthorityScope = (e) => language === "zh" ? zhUiText(e.authority?.scope_zh || e.authority?.scope) : raw(e.authority?.scope);

  const classes = {
    idea:{en:"Idea / problem",zh:"研究方向 / 问题发现",tone:"idea"},
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

  const chinaDateFormatter = new Intl.DateTimeFormat("en-US",{timeZone:CHINA_TZ,year:"numeric",month:"2-digit",day:"2-digit"});
  const chinaDateCache = new Map();
  const chinaDateKey = (iso) => {
    const key = raw(iso);
    if (chinaDateCache.has(key)) return chinaDateCache.get(key);
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) {
      const fallback = key.slice(0,10) || "unknown";
      chinaDateCache.set(key,fallback);
      return fallback;
    }
    const parts = chinaDateFormatter.formatToParts(d);
    const map = Object.fromEntries(parts.map(p=>[p.type,p.value]));
    const value = `${map.year}-${map.month}-${map.day}`;
    chinaDateCache.set(key,value);
    return value;
  };
  const fmtDate = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return raw(iso).slice(0,10);
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {year:"numeric",month:"long",day:"numeric",weekday:"short",timeZone:CHINA_TZ}).format(d);
  };
  let cachedResearchWeekAnchorMs;
  const researchWeekAnchorMs = () => {
    if (cachedResearchWeekAnchorMs !== undefined) return cachedResearchWeekAnchorMs;
    let earliest = "";
    dataset().events.forEach(e=>{
      const date = chinaDateKey(e.occurred_at);
      if (/^\d{4}-\d{2}-\d{2}$/.test(date) && (!earliest || date < earliest)) earliest = date;
    });
    if (!earliest) return (cachedResearchWeekAnchorMs = 0);
    const [year,month,day] = earliest.split("-").map(Number);
    const first = Date.UTC(year,month-1,day);
    const weekday = (new Date(first).getUTCDay()+6)%7;
    return (cachedResearchWeekAnchorMs = first - weekday * 86400000);
  };
  const researchWeekInfoCache=new Map();
  const researchWeekInfo = (date) => {
    const cacheKey=raw(date);
    if(researchWeekInfoCache.has(cacheKey)) return researchWeekInfoCache.get(cacheKey);
    const [year,month,day] = cacheKey.split("-").map(Number);
    if (!year || !month || !day) { const fallback={number:1,weekday:0,monday:date}; researchWeekInfoCache.set(cacheKey,fallback); return fallback; }
    const target = Date.UTC(year,month-1,day);
    const weekday = (new Date(target).getUTCDay()+6)%7;
    const mondayMs = target - weekday * 86400000;
    const anchor = researchWeekAnchorMs();
    const number = Math.max(1,anchor ? Math.floor((mondayMs-anchor)/(7*86400000))+1 : 1);
    const value={number,weekday,monday:new Date(mondayMs).toISOString().slice(0,10)};
    researchWeekInfoCache.set(cacheKey,value);
    return value;
  };
  const weekDayLabel = (date) => {
    const info = researchWeekInfo(date);
    const zhWeekdays = ["周一","周二","周三","周四","周五","周六","周日"];
    const enWeekdays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
    return language === "zh" ? `第${info.number}周 · ${zhWeekdays[info.weekday]}` : `Week ${info.number} · ${enWeekdays[info.weekday]}`;
  };
  const shortDateLabel = (date) => {
    const [year,month,day] = raw(date).split("-").map(Number);
    if (!year || !month || !day) return raw(date);
    return language === "zh" ? `${month}月${day}日` : new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",timeZone:"UTC"}).format(new Date(Date.UTC(year,month-1,day)));
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
      "raw seeds":"原始候选问题数","pre-f0 queued":"Pre-F0 候选数","support ready":"支持条件已就绪","support holds":"因支持不足暂缓",
      "formal launchable":"当前可启动正式实验数","commit":"提交","提交":"提交","提交次数":"提交次数","最新提交":"最新提交","代表变更":"代表变更",
      "原始状态码":"原始状态码"
    };
    if (exact[key]) return exact[key];
    if (key.startsWith("disposition ·")) return `处置结果 · ${l.split("·").slice(1).join("·").trim()}`;
    if (language === "zh" && !/[\u4e00-\u9fff]/.test(l) && /count|number|total|items|records|ideas|candidates|reviews|rows|calls|edges|files|runs/.test(key)) return `${l}（数量）`;
    return l;
  };

  const latestMs = () => Math.max(0,...dataset().events.map(e => Date.parse(e.occurred_at)||0));
  const refs = (e) => e.canonical_refs || {research_items:[],experiments:[],papers:[],categories:[]};
  const researchCodes = (e) => (refs(e).research_items||[]).map(row=>row.code).filter(Boolean);
  const paperCodes = (e) => (refs(e).papers||[]).map(row=>row.paper_id).filter(Boolean);
  const categoryCodes = (e) => (refs(e).categories||[]).filter(Boolean);
  const canonicalChips = (e) => {
    const r=refs(e), chunks=[];
    (r.research_items||[]).forEach(row=>chunks.push(`<a class="rt-canonical-chip rt-canonical-research" href="paper-ideas.html?research=${encodeURIComponent(row.code)}#canonical-group-${esc(String(row.category||"").toLowerCase())}"><b>${esc(row.code)}</b><span>${esc(language==="zh"?(row.title_zh||row.title_en||row.id):(row.title_en||row.title_zh||row.id))}</span></a>`));
    (r.experiments||[]).forEach(row=>chunks.push(`<a class="rt-canonical-chip rt-canonical-experiment" href="experiments.html"><b>${esc(row.portfolio_code||row.experiment_id)}</b><span>${pick("实验记录","Experiment record")}</span></a>`));
    (r.papers||[]).forEach(row=>chunks.push(`<a class="rt-canonical-chip rt-canonical-paper" href="selected-paper.html?paper=${encodeURIComponent(row.paper_id)}"><b>${esc(row.paper_id)}</b><span>${esc(row.paper_stage||pick("论文","Paper"))}</span></a>`));
    return chunks.length?`<div class="rt-canonical-refs"><span>${pick("Canonical 绑定","Canonical bindings")}</span>${chunks.join("")}</div>`:"";
  };
  const searchable = (e) => [e.research_id,e.research_label_zh,e.title,e.title_zh,e.state_before,e.state_after,localText(e.summary),localText(e.why),localText(e.limitation),e.next_action,e.next_action_zh,e.reopen_condition,e.reopen_condition_zh,researchCodes(e).join(" "),paperCodes(e).join(" "),categoryCodes(e).join(" ")].join(" ").toLowerCase();
  const visible = () => {
    const latest = latestMs();
    const days = state.range === "all" ? Infinity : Number(state.range || 7);
    const floor = Number.isFinite(days) ? latest - (days - 1) * 86400000 : 0;
    const q = state.query.trim().toLowerCase();
    return dataset().events.filter(e => {
      if (state.importance === "key" && e.importance !== "key") return false;
      if (state.type !== "all" && e.event_class !== state.type) return false;
      if (state.category !== "all" && !categoryCodes(e).includes(state.category)) return false;
      if (state.research !== "all") {
        if (state.research.startsWith("ri:") && !researchCodes(e).includes(state.research.slice(3))) return false;
        else if (state.research.startsWith("paper:") && !paperCodes(e).includes(state.research.slice(6))) return false;
        else if (!state.research.startsWith("ri:") && !state.research.startsWith("paper:") && e.research_id !== state.research) return false;
      }
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
    return `<details class="rt-event" data-event-id="${esc(e.event_id)}" data-class="${esc(e.event_class)}" data-canonical-research="${esc(researchCodes(e).join(" "))}" data-canonical-paper="${esc(paperCodes(e).join(" "))}"><summary><time>${esc(fmtTime(e))}</time><span class="rt-dot" aria-hidden="true"></span><div class="rt-summary-main"><div class="rt-summary-meta">${classBadge(e)}<span>${esc(localResearch(e))}</span>${e.importance === "key" ? `<em>${pick("关键","KEY")}</em>`:""}</div><strong>${esc(localTitle(e))}</strong><p>${esc(summary)}</p></div><div class="rt-state"><span>${pick("当前状态","STATE")}</span><b>${esc(statusDisplay(e.state_after || "RECORDED"))}</b>${language === "zh" ? `<small>${esc(e.state_after || "RECORDED")}</small>` : ""}</div></summary><div class="rt-expanded">${canonicalChips(e)}${before}${detailBlock("发生了什么","What changed",summary,"change")}${detailBlock("为什么这样裁决","Decision basis",why)}${detailBlock("边界 / 不能扩大到什么","Boundary / unsupported scope",limitation,"boundary")}${detailBlock("下一步","Next action",localNext(e),"next")}${detailBlock("什么情况下重开","Reopen only if",localReopen(e),"reopen")}${evidence(e.evidence)}<div class="rt-authority-row">${authorityBadge(e)}<span>${esc(localAuthorityScope(e) || pick("只读历史投影","read-only projection"))}</span></div>${sourceLinks(e)}</div></details>`;
  };

  const sortDayEvents = (events) => [...events].sort((a,b) => {
    const ap = a.time_precision === "date" ? 1 : 0, bp = b.time_precision === "date" ? 1 : 0;
    if (ap !== bp) return ap - bp;
    return (Date.parse(a.occurred_at)||0) - (Date.parse(b.occurred_at)||0);
  });
  const dayCounts = (events) => events.reduce((m,e)=>(m[e.event_class]=(m[e.event_class]||0)+1,m),{});
  const headlineTitle = (e) => {
    let title = localTitle(e).trim();
    if (language === "zh") title = title.replace(/^(系统建设里程碑|研究问题 \/ 研究问题相关提交|研究问题 \/ 问题发现记录|实验 \/ 证据相关提交|论文 \/ 评审相关提交|关闭 \/ 裁决相关提交|系统与治理记录|停止 \/ 关闭裁决)\s*[：:·]\s*/i, "");
    return title;
  };
  const headlineKey = (title) => raw(title).toLowerCase().replace(/[\s·：:—–_\-]+/g," ").trim();
  const headlineScore = (e) => {
    const classScore = {scientific:90,paper:80,experiment:70,idea:65,closure:60,blocker:55,system:15}[e.event_class] || 0;
    const importanceScore = e.importance === "key" ? 100 : 0;
    const originScore = e.origin === "artifact" ? 40 : e.origin === "artifact_full_history" ? 25 : e.origin === "research_memory_db" ? 5 : 0;
    const genericRuntime = /append-only research run imported|新的科研运行记录写入 research memory/i.test(`${e.title||""} ${e.title_zh||""}`) ? -140 : 0;
    return classScore + importanceScore + originScore + genericRuntime;
  };
  const headlineItems = (events,limit=4) => {
    const ordered = sortDayEvents(events);
    const source = ordered.filter(e => e.origin !== "git_daily_summary");
    const pool = source.length ? source : ordered;
    const unique = new Map();
    pool.forEach((e,index) => {
      const title = headlineTitle(e);
      const key = headlineKey(title);
      if (!key) return;
      const candidate = {e,title,index,score:headlineScore(e)};
      const existing = unique.get(key);
      if (!existing || candidate.score > existing.score) unique.set(key,candidate);
    });
    const ranked = [...unique.values()].sort((a,b)=>b.score-a.score || a.index-b.index);
    const selected = [], usedClasses = new Set();
    ranked.forEach(item=>{ if (selected.length < limit && !usedClasses.has(item.e.event_class)){ selected.push(item); usedClasses.add(item.e.event_class); } });
    ranked.forEach(item=>{ if (selected.length < limit && !selected.includes(item)) selected.push(item); });
    return selected.sort((a,b)=>a.index-b.index).map(item=>item.title);
  };
  const dayHeadline = (events) => {
    const chosen = headlineItems(events,4);
    return chosen.length ? chosen.join(" → ") : pick("当日以系统维护与追溯工作为主。","Primarily system/provenance work.");
  };
  const workloadSummary = (events,limit=3) => {
    const counts = dayCounts(events);
    return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,limit).map(([k,v])=>`${labelClass(k)} ${v}`).join(" · ");
  };
  const workloadBar = (events,label=pick("工作量构成","Workload composition")) => {
    const counts = dayCounts(events), total = Math.max(events.length,1);
    return `<div class="rt-workload-bar" aria-label="${esc(label)}">${Object.keys(classes).filter(k=>counts[k]).map(k=>`<i class="rt-work-${classes[k].tone}" style="width:${(counts[k]/total*100).toFixed(2)}%" title="${esc(labelClass(k))} ${counts[k]}"></i>`).join("")}</div>`;
  };
  const monthLabel = (month) => {
    const d = new Date(`${month}-15T12:00:00+08:00`);
    if (Number.isNaN(d.getTime())) return month;
    return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", {year:"numeric",month:"long",timeZone:CHINA_TZ}).format(d);
  };
  const dayRows = (date,events) => {
    const ordered = sortDayEvents(events);
    const keyChanges = ordered.filter(e=>e.importance === "key").length;
    const researchLines = new Set(ordered.map(e=>e.research_id).filter(Boolean)).size;
    const gitChanges = ordered.filter(e=>e.origin === "git_relevant_history").length;
    const artifactChanges = ordered.filter(e=>String(e.origin||"").startsWith("artifact")).length;
    const thread = dayHeadline(ordered), workload = workloadSummary(ordered,3);
    return `<tr class="rt-day-row" id="timeline-${esc(date)}" data-rt-day-toggle="${esc(date)}" tabindex="0" aria-expanded="false"><td class="rt-table-date"><div class="rt-table-date-inner"><button type="button" class="rt-day-toggle" aria-label="${pick("展开当天详情","Open day details")}">＋</button><div><b>${esc(weekDayLabel(date))}</b><small>${esc(date)}</small></div></div></td><td class="rt-num rt-activity-count"><b>${ordered.length}</b><span>${pick("条","events")}</span></td><td class="rt-num"><b>${keyChanges}</b></td><td class="rt-num"><b>${gitChanges}</b></td><td class="rt-num"><b>${artifactChanges}</b></td><td class="rt-num"><b>${researchLines}</b></td><td class="rt-table-thread"><p>${esc(thread)}</p>${workload?`<div class="rt-table-workload">${esc(workload)}</div>`:""}${workloadBar(ordered,pick("当日工作量构成","Daily workload composition"))}</td></tr><tr class="rt-day-detail-row" data-rt-day-detail="${esc(date)}" hidden><td colspan="7"><div class="rt-day-expanded"><div class="rt-order-note">${pick("以下严格按时间从早到晚排列，不按研究问题 / 实验 / 论文等类别重新分组，便于追踪“什么先发生 → 为什么后来改变研究或系统”。","Events below are strictly chronological rather than grouped by type.")}</div><div class="rt-day-events" data-rt-day-events="${esc(date)}" data-rendered="0"><span class="rt-lazy-placeholder">${pick("展开后加载当天详细事件…","Detailed events load on expansion…")}</span></div></div></td></tr>`;
  };
  const monthTable = (month,dates,groups,weekSummaries) => {
    const total = dates.reduce((n,date)=>n+(groups[date]?.length||0),0);
    const rows = dates.map(date=>`${dayRows(date,groups[date])}${weekSummaries.get(date)||""}`).join("");
    return `<section class="rt-month" data-rt-month="${esc(month)}"><header class="rt-month-header"><div><h2>${esc(monthLabel(month))}</h2><span>${esc(month)}</span></div><div><b>${dates.length}</b><span>${pick("个研究日","research days")}</span><b>${total}</b><span>${pick("条活动","activities")}</span></div></header><div class="rt-month-table-wrap"><table class="rt-month-table"><thead><tr><th>${pick("日期","Date")}</th><th>${pick("活动","Activity")}</th><th>${pick("关键变化","Key")}</th><th>${pick("代码 / 系统","Code / system")}</th><th>${pick("科研记录","Research")}</th><th>${pick("研究对象","Objects")}</th><th>${pick("主要脉络 / 工作量","Main thread / workload")}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  };

  const stats = (events) => {
    const days = new Set(events.map(e=>chinaDateKey(e.occurred_at))).size;
    const ideas = events.filter(e=>e.event_class === "idea").length;
    const experiments = events.filter(e=>e.event_class === "experiment").length;
    const advances = events.filter(e=>e.event_class === "scientific" || e.event_class === "paper").length;
    const stops = events.filter(e=>e.event_class === "closure" || e.event_class === "blocker").length;
    return `<div class="rt-stats"><article><b>${events.length}</b><span>${pick("当前展示事件","visible events")}</span></article><article><b>${days}</b><span>${pick("有记录的研究日","recorded research days")}</span></article><article><b>${ideas}</b><span>${pick("研究方向 / 问题发现","idea / problem events")}</span></article><article><b>${experiments}</b><span>${pick("实验 / 验证","experiment events")}</span></article><article><b>${advances}</b><span>${pick("科学结论 / 论文推进","scientific / paper advances")}</span></article><article><b>${stops}</b><span>${pick("停止 / 暂缓","closures / holds")}</span></article></div>`;
  };

  const canonicalResearchOptions = () => {
    const seen=new Map();
    dataset().events.forEach(e=>(refs(e).research_items||[]).forEach(row=>{if(row.code&&!seen.has(row.code))seen.set(row.code,row);}));
    return [...seen.values()].sort((a,b)=>a.code.localeCompare(b.code,undefined,{numeric:true})).map(row=>`<option value="ri:${esc(row.code)}" ${state.research===`ri:${row.code}`?"selected":""}>${esc(row.code)} · ${esc(language==="zh"?(row.title_zh||row.title_en||row.id):(row.title_en||row.title_zh||row.id))}</option>`).join("");
  };
  const canonicalPaperOptions = () => {
    const seen=new Map();
    dataset().events.forEach(e=>(refs(e).papers||[]).forEach(row=>{if(row.paper_id&&!seen.has(row.paper_id))seen.set(row.paper_id,row);}));
    return [...seen.values()].sort((a,b)=>a.paper_id.localeCompare(b.paper_id)).map(row=>`<option value="paper:${esc(row.paper_id)}" ${state.research===`paper:${row.paper_id}`?"selected":""}>${esc(row.paper_id)} · ${esc(row.paper_stage||"")}</option>`).join("");
  };
  const legacyResearchOptions = () => [...new Set(dataset().events.filter(e=>!(refs(e).research_items||[]).length&&!(refs(e).papers||[]).length).map(e=>e.research_id).filter(Boolean))].sort((a,b)=>a.localeCompare(b)).map(r=>{
    const sample = dataset().events.find(e=>e.research_id===r);
    const label = language === "zh" ? raw(sample?.research_label_zh || r) : r;
    return `<option value="${esc(r)}" ${state.research===r?"selected":""}>${esc(label)}</option>`;
  }).join("");
  const researchOptions = () => `<optgroup label="${pick("Canonical ResearchItem","Canonical ResearchItems")}">${canonicalResearchOptions()}</optgroup><optgroup label="${pick("PaperState","PaperStates")}">${canonicalPaperOptions()}</optgroup><optgroup label="${pick("系统 / 历史流","System / legacy streams")}">${legacyResearchOptions()}</optgroup>`;
  const categoryOptions = () => ["A","B","C","D","E","F","G"].map(code=>`<option value="${code}" ${state.category===code?"selected":""}>${code}</option>`).join("");
  const controls = () => `<section class="rt-controls" aria-label="${pick("时间轴筛选","Timeline filters")}"><div class="rt-control-group"><b>${pick("层级","Level")}</b><div class="rt-segment"><button type="button" data-rt-importance="all" class="${state.importance==="all"?"active":""}">${pick("全部","All")}</button><button type="button" data-rt-importance="key" class="${state.importance==="key"?"active":""}">${pick("关键","Key")}</button></div></div><div class="rt-control-group"><b>${pick("顺序","Order")}</b><div class="rt-segment"><button type="button" data-rt-order="asc" class="${state.order==="asc"?"active":""}">${pick("因果顺序","Old → new")}</button><button type="button" data-rt-order="desc" class="${state.order==="desc"?"active":""}">${pick("最新优先","New → old")}</button></div></div><div class="rt-control-group"><b>${pick("范围","Range")}</b><div class="rt-segment">${[["all",pick("全部","All")],["30",pick("30 天","30D")],["7",pick("7 天","7D")],["3",pick("3 天","3D")]].map(([v,l])=>`<button type="button" data-rt-range="${v}" class="${state.range===v?"active":""}">${l}</button>`).join("")}</div></div><label class="rt-select"><span>${pick("A–G 大类","A–G category")}</span><select id="timeline-category"><option value="all">${pick("全部大类","All categories")}</option>${categoryOptions()}</select></label><label class="rt-select rt-select-wide"><span>${pick("ResearchItem / Paper","ResearchItem / Paper")}</span><select id="timeline-research"><option value="all">${pick("全部研究对象","All research")}</option>${researchOptions()}</select></label><label class="rt-select"><span>${pick("类型","Type")}</span><select id="timeline-type"><option value="all">${pick("全部类型","All types")}</option>${Object.keys(classes).map(k=>`<option value="${k}" ${state.type===k?"selected":""}>${esc(labelClass(k))}</option>`).join("")}</select></label></section>`;

  const weeklySummaryRows = (events) => {
    const result = new Map();
    if (!events.length) return result;
    const weeks = new Map();
    events.forEach(e=>{
      const date = chinaDateKey(e.occurred_at), info = researchWeekInfo(date);
      const entry = weeks.get(info.number) || {number:info.number,events:[],dates:new Set()};
      entry.events.push(e); entry.dates.add(date); weeks.set(info.number,entry);
    });
    weeks.forEach(week=>{
      const dates=[...week.dates].sort(), rows=sortDayEvents(week.events), keyChanges=rows.filter(e=>e.importance === "key").length;
      const start=dates[0], end=dates[dates.length-1], range=start===end?shortDateLabel(start):`${shortDateLabel(start)}–${shortDateLabel(end)}`;
      const highlights=headlineItems(rows,4), summary=highlights.length?highlights.join("；"):pick("本周以系统维护与追溯工作为主。","Primarily system and provenance work this week.");
      const workload=workloadSummary(rows,4);
      const boundaryDate = state.order === "asc" ? dates[dates.length-1] : dates[0];
      result.set(boundaryDate,`<tr class="rt-week-summary-row" data-rt-week-summary="${week.number}"><td colspan="7"><div class="rt-week-inline"><header><div><b>${pick(`第${week.number}周总结`,`Week ${week.number} summary`)}</b><span>${esc(range)}</span></div><div><strong>${rows.length}</strong><span>${pick("条活动","events")}</span><strong>${dates.length}</strong><span>${pick("个研究日","research days")}</span><em>${pick(`${keyChanges} 个关键变化`,`${keyChanges} key changes`)}</em></div></header><p>${esc(summary)}</p><div class="rt-week-inline-workload"><span>${esc(workload)}</span>${workloadBar(rows,pick("本周工作量构成","Weekly workload composition"))}</div></div></td></tr>`);
    });
    return result;
  };

  const feed = (events) => {
    const groups = grouped(events);
    const dates = Object.keys(groups).sort((a,b)=>state.order === "asc" ? a.localeCompare(b) : b.localeCompare(a));
    if (!dates.length) return `<div class="empty">${pick("没有符合当前筛选条件的时间事件。","No timeline events match the current filters.")}</div>`;
    const months = [...new Set(dates.map(date=>date.slice(0,7)))];
    const weekSummaries = weeklySummaryRows(events);
    return months.map(month=>monthTable(month,dates.filter(date=>date.startsWith(`${month}-`)),groups,weekSummaries)).join("");
  };

  const activityHeatmap = (events) => {
    if (!events.length) return "";
    const counts = Object.fromEntries(Object.entries(grouped(events)).map(([d,rows])=>[d,rows.length]));
    const keys = Object.keys(counts).sort();
    const monthKeys = [...new Set(keys.map(day=>day.slice(0,7)))].sort((a,b)=>state.order === "asc" ? a.localeCompare(b) : b.localeCompare(a));
    const max=Math.max(1,...Object.values(counts));
    const monthCalendar = (month) => {
      const recorded = keys.filter(day=>day.startsWith(`${month}-`));
      const start = new Date(`${recorded[0]}T00:00:00+08:00`), end = new Date(`${recorded[recorded.length-1]}T00:00:00+08:00`);
      const days=[]; for(let d=new Date(start); d<=end; d=new Date(d.getTime()+86400000)) days.push(chinaDateKey(d.toISOString()));
      const [year,monthNumber] = month.split("-").map(Number);
      const firstDay = Number(recorded[0].slice(-2));
      const startColumn = ((new Date(Date.UTC(year,monthNumber-1,firstDay)).getUTCDay()+6)%7)+1;
      const total = recorded.reduce((sum,day)=>sum+(counts[day]||0),0);
      return `<section class="rt-heat-month" data-rt-heat-month="${esc(month)}"><header class="rt-heat-month-header"><div><b>${esc(monthLabel(month))}</b><span>${esc(month)}</span></div><div><strong>${recorded.length}</strong><span>${pick("个研究日","research days")}</span><strong>${total}</strong><span>${pick("条活动","activities")}</span></div></header><div class="rt-heat-weekdays"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div><div class="rt-heatmap">${days.map((day,i)=>{const n=counts[day]||0,level=n?Math.max(.12,n/max):0;return `<button type="button" class="rt-heat-cell" data-rt-day="${day}" style="--level:${level.toFixed(3)};${i===0?`grid-column-start:${startColumn};`:""}" title="${day} · ${n} ${pick("条活动","activities")}"><span class="rt-heat-date">${Number(day.slice(-2))}</span>${n?`<span class="rt-heat-activity"><b>${n}</b><small>${pick("次活动","activities")}</small></span>`:""}</button>`}).join("")}</div></section>`;
    };
    return `<section class="rt-heatmap-panel"><div class="rt-heatmap-heading"><b>${pick("每日工作量概览","Daily workload overview")}</b><span>${pick("按月分开查看；颜色越深，当天记录的操作越多，点击日期可直接展开当天。","Split by month; darker cells mean more recorded activity, and clicking a date opens that day.")}</span></div><div class="rt-heat-months">${monthKeys.map(monthCalendar).join("")}</div></section>`;
  };

  const compactHeader = (events) => {
    const days = new Set(events.map(e=>chinaDateKey(e.occurred_at))).size;
    const ideas = events.filter(e=>e.event_class === "idea").length;
    const experiments = events.filter(e=>e.event_class === "experiment").length;
    const advances = events.filter(e=>e.event_class === "scientific" || e.event_class === "paper").length;
    const stops = events.filter(e=>e.event_class === "closure" || e.event_class === "blocker").length;
    return `<section class="rt-hero"><div class="rt-hero-main"><div class="rt-hero-title"><span>${pick("科研进展历史","Research history")}</span><h1>${pick("研究时间轴","Research Timeline")}</h1></div><p>${pick("回看完整研究历史。月历先定位工作量变化，一周总结提炼阶段性推进，下面的月表再展开当天研究问题、实验、论文、裁决与系统更新；时间轴只读，不新增科研权限。","Review the complete research history. Use monthly calendars to locate workload changes, weekly summaries to capture progress, then expand daily idea, experiment, paper, decision, and system events below. This timeline is read-only and adds no scientific authority.")}</p><div class="rt-hero-kpis"><span><b>${events.length}</b>${pick("活动","events")}</span><span><b>${days}</b>${pick("研究日","days")}</span><span><b>${ideas}</b>${pick("研究问题","ideas")}</span><span><b>${experiments}</b>${pick("实验","experiments")}</span><span><b>${advances}</b>${pick("结论 / 论文","advances")}</span><span><b>${stops}</b>${pick("停止 / 暂缓","stops / holds")}</span></div></div><aside class="rt-hero-side"><div class="rt-legend" aria-label="${pick("事件颜色图例","Event color legend")}">${Object.keys(classes).map(k=>`<span class="rt-legend-item rt-legend-${classes[k].tone}" data-rt-legend="${classes[k].tone}"><i></i>${esc(labelClass(k))}</span>`).join("")}</div></aside><div class="rt-hero-boundary">${pick("本页只是只读历史投影；工程 / 运行 / 追溯记录不会因为进入时间轴而获得科研权限，工程失败也不会自动改写成科学失败。","Read-only history projection: engineering, runtime, and provenance records gain no scientific authority here, and engineering failures do not automatically become scientific failures.")}</div></section>`;
  };

  window.renderResearchTimeline = function(){
    const events=visible();
    return `<div id="research-timeline-summary">${compactHeader(events)}</div><div id="research-timeline-heatmap">${activityHeatmap(events)}</div><div id="research-timeline-controls">${controls()}</div><div id="research-timeline-feed" class="rt-feed">${feed(events)}</div><section class="rt-policy-note"><b>${pick("读取规则","Reading rule")}</b><span>${pick("① 月历仍按两个月一行，用于快速定位工作量高峰；② 月度明细表改为单列，8 月完整展示后再接 7 月；③ 每周每日记录结束后，在进入上一周前插入周总结；④ 点开当天后，事件严格按时间从早到晚排列；⑤ 无法可靠回填具体时刻的记录仍标记为日期精度，系统工程与追溯记录不会因此获得科研权限。","Calendars remain paired for workload scanning, while monthly detail tables are single-column and newest-first. A weekly summary is inserted at each week boundary before the previous week begins; expanded events remain chronological and date-only precision stays explicit.")}</span></section>`;
  };

  const rerender = () => {
    const summary=document.getElementById("research-timeline-summary"), c=document.getElementById("research-timeline-controls"), h=document.getElementById("research-timeline-heatmap"), f=document.getElementById("research-timeline-feed");
    const events=visible();
    if(summary) summary.innerHTML=compactHeader(events);
    if(c) c.innerHTML=controls();
    if(h) h.innerHTML=activityHeatmap(events);
    if(f) f.innerHTML=feed(events);
    const counter=document.getElementById("result-count");
    if(counter) counter.textContent=pick(`${events.length} 条事件`,`${events.length} events`);
    bindControls();
  };
  const renderDayEvents = (date,detail) => {
    const holder=detail?.querySelector(`[data-rt-day-events="${date}"]`);
    if(!holder || holder.dataset.rendered === "1") return;
    const ordered=sortDayEvents(visible().filter(e=>chinaDateKey(e.occurred_at)===date));
    const dateOnly=ordered.filter(e=>e.time_precision === "date"), exact=ordered.filter(e=>e.time_precision !== "date");
    const dateOnlyBlock=dateOnly.length?`<div class="rt-date-only-note">${pick(`另有 ${dateOnly.length} 条记录只有日期精度，无法可靠判断当天先后，因此放在精确时间事件之后。`,`Another ${dateOnly.length} records have date-only precision and are shown after exact-time events.`)}</div>${dateOnly.map(eventRow).join("")}`:"";
    holder.innerHTML=`${exact.map(eventRow).join("")}${dateOnlyBlock}`;
    holder.dataset.rendered="1";
  };
  const toggleDay = (date,forceOpen) => {
    const row=document.getElementById(`timeline-${date}`), detail=document.querySelector(`[data-rt-day-detail="${date}"]`);
    if(!row || !detail) return;
    const shouldOpen = forceOpen === undefined ? detail.hidden : Boolean(forceOpen);
    if(shouldOpen) renderDayEvents(date,detail);
    detail.hidden=!shouldOpen;
    row.classList.toggle("is-open",shouldOpen);
    row.setAttribute("aria-expanded",shouldOpen ? "true" : "false");
    const toggle=row.querySelector(".rt-day-toggle");
    if(toggle) toggle.textContent=shouldOpen ? "−" : "＋";
  };
  const syncUrl = () => {
    const url=new URL(window.location.href);
    url.searchParams.delete("research"); url.searchParams.delete("paper"); url.searchParams.delete("category");
    if(state.research.startsWith("ri:")) url.searchParams.set("research",state.research.slice(3));
    else if(state.research.startsWith("paper:")) url.searchParams.set("paper",state.research.slice(6));
    if(state.category!=="all") url.searchParams.set("category",state.category);
    window.history.replaceState(null,"",`${url.pathname}${url.search}${url.hash}`);
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
    document.getElementById("timeline-category")?.addEventListener("change",e=>{state.category=e.target.value;syncUrl();rerender();});
    document.getElementById("timeline-research")?.addEventListener("change",e=>{state.research=e.target.value;syncUrl();rerender();});
  };
  window.bindResearchTimelineEvents = function(){bindControls();};
  window.applyResearchTimelineFilters = function(query){state.query=raw(query);rerender();};
})();
