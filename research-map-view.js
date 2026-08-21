(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-map"] = {
    eyebrow:{en:"Research Planning · Current Portfolio Map",zh:"研究规划 · 当前组合图谱"},
    title:{en:"Current Research Portfolio Map",zh:"当前研究组合图谱"},
    lead:{en:"A high-level map of the current A–G research space. It shows where the authoritative ResearchItems, paper results, retained assets, terminal decisions, and evidence gaps sit without duplicating the full Research Portfolio.",zh:"用一张图看当前 A–G 研究空间：每一类现在覆盖了多少 ResearchItem、形成了什么结论、留下了哪些资产、哪里已经进入论文、哪里仍缺证据。这里不复制完整 ResearchItem；具体实验、证据与重开条件仍以“研究组合”页面为准。"},
    callout:{en:"This is a projection of the current portfolio, not a second state system. Click any A–G node to inspect the authoritative ResearchItems.",zh:"本页只是当前研究组合的只读投影，不建立第二套状态。点击任意 A–G 节点可直接进入权威 ResearchItem 账本。"},
    sections:[]
  };

  const mapPick = (zh,en) => language === "zh" ? zh : en;
  const currentStatus = () => window.CURRENT_RESEARCH_STATUS || {};
  const currentHeadline = () => currentStatus().headline || {};
  const currentPaper = () => currentStatus().leading_paper_track || {};
  const safetyState = () => window.AGENT_SAFETY_PROGRAM_STATE || {};

  const groupState = (group, rows, inv) => {
    const stops = rows.filter(row => row.meta.status === "stop").length;
    const merges = rows.filter(row => row.meta.status === "merge").length;
    if (group.id === "E" && Number(currentHeadline().paper_ready || 0) > 0) return {tone:"paper",label:mapPick("已有论文结果","Paper result"),note:mapPick("STRI 已从 ResearchItem 交接到 PaperState；本类仍保留研究链与结构方法资产。","STRI has handed off from ResearchItem to PaperState while its research lineage remains here.")};
    if (group.id === "G") {
      const safety = safetyState();
      const stage = safety.current_stage || safety.candidate_stage || "";
      return {tone:"hold",label:mapPick("安全主线 · 当前实现条件受阻","Safety line · current realization blocked"),note:mapPick(`当前安全问题没有被判死；现有实现停在 ${stage || "支持/实现检查"}，需要满足新的基座/运行时支持条件后再继续。`,`The safety question remains open; the current realization is stopped at ${stage || "support/realization checks"} and needs a fresh qualified substrate/runtime.`)};
    }
    if (inv.context > 0) return {tone:"hold",label:mapPick("仍有证据对象需要关注","Evidence objects remain"),note:mapPick("父级方向多数已有终态，但本类仍保留历史现象、条件重开或证据对象。","Most parent directions are terminal, while historical phenomena, conditional reopenings, or evidence objects remain.")};
    if (stops + merges === rows.length && rows.length) return {tone:"terminal",label:mapPick("父级方向已全部形成终态","All parent directions terminal"),note:mapPick(`父级方向：停止 ${stops} · 合并 ${merges}。当前没有新的正式实验授权。`,`Parent directions: ${stops} stopped · ${merges} merged. No new formal experiment is authorized.`)};
    if (!rows.length) return {tone:"gap",label:mapPick("当前父级 ResearchItem 覆盖较少","Limited current parent coverage"),note:mapPick("这里仍是领域问题空间的一部分，但当前组合没有独立父级 ResearchItem 正在推进。","This remains part of the problem space, but the current portfolio has no standalone parent ResearchItem advancing here.")};
    return {tone:"hold",label:mapPick("当前组合已覆盖","Covered by current portfolio"),note:mapPick("具体状态以 ResearchItem 当前科学决策为准。","See the authoritative ResearchItem decision for exact status.")};
  };

  const mapStats = (inventory, terminal) => {
    const h=currentHeadline(), paper=currentPaper();
    return `<section class="rpm-stats"><article><b>7</b><span>${mapPick("当前研究大类","current research categories")}</span></article><article><b>${inventory.parent}</b><span>${mapPick("父级 ResearchItem","parent ResearchItems")}</span></article><article><b>${terminal.stop||0}</b><span>${mapPick("当前已停止","currently stopped")}</span></article><article><b>${terminal.merge||0}</b><span>${mapPick("已合并为更大方向/资产","merged into larger lines/assets")}</span></article><article class="rpm-paper-stat"><b>${h.paper_ready||0}</b><span>${mapPick("论文就绪","paper-ready")}</span></article><article><b>${h.launchable_formal_experiments||0}</b><span>${mapPick("可启动正式实验","launchable formal experiments")}</span></article></section><section class="rpm-current-banner"><div><span>${mapPick("当前最明确的产出","CLEAREST CURRENT OUTPUT")}</span><b>${esc(paper.title || "STRI")}</b><p>${mapPick(`状态：${paper.submission_status || paper.status || "--"}。论文主张、图表、QA 与投稿状态只在 PaperState 维护。`,`Status: ${paper.submission_status || paper.status || "--"}. Claims, figures, QA, and submission state live only in PaperState.`)}</p></div><a class="link-btn" href="selected-paper.html">${mapPick("打开论文 · STRI →","Open Paper · STRI →")}</a></section>`;
  };

  const groupCard = (group, parents, inventory) => {
    const rows=parents.filter(row=>row.meta.group===group.id);
    const inv=inventory.byGroup[group.id] || {parent:0,related:0,context:0,closed:0,total:0};
    const status=groupState(group,rows,inv);
    const insight=CATEGORY_BRIEFING_ZH[group.id] || {};
    const stops=rows.filter(row=>row.meta.status==="stop").length;
    const merges=rows.filter(row=>row.meta.status==="merge").length;
    const max=Math.max(1,...Object.values(inventory.byGroup).map(row=>row.total||0));
    const width=Math.max(5,Math.round((inv.total/max)*100));
    return `<article class="rpm-node tone-${esc(status.tone)}" id="research-map-${esc(group.id.toLowerCase())}"><header><span>${esc(group.id)}</span><div><h2 data-toc="false">${textOf(group.title)}</h2><p>${textOf(group.question)}</p></div></header><div class="rpm-node-state"><b>${esc(status.label)}</b><span>${esc(status.note)}</span></div><div class="rpm-coverage"><div><i style="width:${width}%"></i></div><b>${inv.total}</b><span>${mapPick("个去重研究对象","deduplicated objects")}</span></div><div class="rpm-count-grid"><span><b>${inv.parent}</b>${mapPick("父级方向","parents")}</span><span><b>${inv.related}</b>${mapPick("方法/关联方向","methods / related")}</span><span><b>${inv.context}</b>${mapPick("论文/证据","paper / evidence")}</span><span><b>${inv.closed}</b>${mapPick("编号关闭方向","numbered closures")}</span></div>${rows.length?`<div class="rpm-parent-state"><span>${mapPick("父级终态","PARENT STATES")}</span><b>${mapPick(`停止 ${stops} · 合并 ${merges}`,`stopped ${stops} · merged ${merges}`)}</b></div>`:""}<section class="rpm-meaning"><div><b>${mapPick("现在研究什么","Research focus")}</b><p>${esc(insight.focus || textOf(group.question))}</p></div><div><b>${mapPick("当前总体判断","Current category judgment")}</b><p>${esc(insight.reason || mapPick("以每个 ResearchItem 当前裁决为准。","See individual ResearchItem decisions."))}</p></div><div><b>${mapPick("留下了什么","What survives")}</b><p>${esc(insight.survives || mapPick("保留有效组件、审计规则和负证据。","Useful components, audit rules, and negative evidence remain."))}</p></div></section><footer><a class="link-btn" href="paper-ideas.html#canonical-group-${esc(group.id.toLowerCase())}">${mapPick(`打开 ${group.id} 类 ResearchItems →`,`Open category ${group.id} ResearchItems →`)}</a></footer></article>`;
  };

  const coverageSummary = (groups, inventory) => {
    const rows=groups.map(group=>({group,inv:inventory.byGroup[group.id]||{total:0,parent:0,context:0}}));
    const most=[...rows].sort((a,b)=>b.inv.total-a.inv.total).slice(0,3);
    const least=[...rows].sort((a,b)=>a.inv.total-b.inv.total).slice(0,3);
    return `<section class="panel rpm-gap-panel"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("组合覆盖 · 不是优先级评分","PORTFOLIO COVERAGE · NOT A PRIORITY SCORE")}</div><h2>${mapPick("哪里搜索得多，哪里当前覆盖得少","Where the portfolio is dense and where coverage is thin")}</h2><p>${mapPick("这里只用透明对象数量描述覆盖，不生成主观 Work Score 或优先级。覆盖少不自动意味着应该立刻做；它只是下轮 Idea Search 可以增加 recall 的领域信号。","Only transparent object counts are used—no subjective work score or priority. Thin coverage is a discovery signal, not an automatic instruction to pursue the area.")}</p></div></div><div class="rpm-gap-grid"><article><b>${mapPick("当前覆盖较密","Denser current coverage")}</b>${most.map(row=>`<span><strong>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><i>${row.inv.total} ${mapPick("个对象","objects")}</i></span>`).join("")}</article><article><b>${mapPick("当前覆盖较少","Thinner current coverage")}</b>${least.map(row=>`<span><strong>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><i>${row.inv.total} ${mapPick("个对象","objects")}</i></span>`).join("")}</article></div></section>`;
  };

  const readingBridge = () => `<section class="panel rpm-bridge"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("两张图谱如何配合","HOW THE TWO MAPS WORK TOGETHER")}</div><h2>${mapPick("领域知识和当前科研状态分开维护","Separate field knowledge from current research state")}</h2></div></div><div class="rpm-bridge-grid"><a href="research-directions.html"><span>01</span><b>${mapPick("领域研究问题与历史方向","Field Problems & Historical Directions")}</b><p>${mapPick("看 D1–D10 历史 taxonomy、代表论文、方向边界、旧 Idea 谱系与历史长期议程。","See the historical D1–D10 taxonomy, representative papers, boundaries, idea lineage, and historical agenda.")}</p></a><i>→</i><a href="research-map.html"><span>02</span><b>${mapPick("当前研究组合图谱","Current Research Portfolio Map")}</b><p>${mapPick("看 A–G 当前覆盖、论文结果、终态、条件重开与组合空白。","See current A–G coverage, paper results, terminal decisions, conditional reopenings, and gaps.")}</p></a><i>→</i><a href="paper-ideas.html"><span>03</span><b>${mapPick("研究组合 · ResearchItems","Research Portfolio · ResearchItems")}</b><p>${mapPick("进入具体 Idea、实验、决定性证据、当前科学结论和重开条件。","Inspect the concrete idea, experiments, decisive evidence, current decision, and reopen condition.")}</p></a></div></section>`;

  window.renderCurrentResearchMap = function(config){
    const groups=canonicalIdeaGroups(), parents=canonicalParentRows(), independent=canonicalIndependentRows();
    const inventory=canonicalInventorySummary(groups,parents,independent), terminal=humanParentFinalSummary();
    return `${pageHeader(config)}${mapStats(inventory,terminal)}<section class="rpm-map-intro"><div><b>${mapPick("A–G 是当前正式坐标系","A–G IS THE CURRENT COORDINATE SYSTEM")}</b><p>${mapPick("D1–D10 仍保留在领域图谱中解释历史研究空间；今天的 ResearchItem、实验与 PaperState 统一使用 A–G。","D1–D10 remains in the field atlas as historical context; current ResearchItems, experiments, and PaperState use A–G.")}</p></div><a class="link-btn" href="research-directions.html">${mapPick("查看历史领域方向 →","Open historical field directions →")}</a></section><section class="rpm-map-grid">${groups.map(group=>groupCard(group,parents,inventory)).join("")}</section>${coverageSummary(groups,inventory)}${readingBridge()}`;
  };
})();
