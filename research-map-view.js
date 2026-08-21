(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-map"] = {
    eyebrow:{en:"Research Planning · Portfolio + Field Knowledge Graph",zh:"研究规划 · 当前组合 + 领域知识图谱"},
    title:{en:"Current Research Portfolio Map",zh:"当前研究组合图谱"},
    lead:{en:"A unified A–G map that overlays our current ResearchItems on the existing Scientific Research Graph and a verified public-literature layer. One color means one research collection; colors no longer double as PASS/HOLD/STOP semantics.",zh:"把当前 A–G ResearchItem、已有 Scientific Research Graph 和最新核验的公开论文放进同一张研究地图。每个集合固定一种颜色；颜色只表示“属于哪个研究集合”，不再同时承担 PASS / HOLD / STOP 状态含义。"},
    callout:{en:"The canonical graph remains read-only and has zero scientific authority. External-paper labels report public bibliographic status, not our internal scientific verdict. Open any collection to trace real graph nodes and edges, then enter Research Portfolio for authoritative decisions.",zh:"底层 canonical graph 仍是只读投影，不新增科研权限。外部论文只显示公开书目状态（正式发表 / 预印本）和它推进到的研究问题，不使用我们的内部科学裁决。图谱关系用于理解研究空间；权威 ResearchItem 决策仍在“研究组合”页面。"},
    sections:[]
  };

  const mapPick = (zh,en) => language === "zh" ? zh : en;
  const currentStatus = () => window.CURRENT_RESEARCH_STATUS || {};
  const currentHeadline = () => currentStatus().headline || {};
  const currentPaper = () => currentStatus().leading_paper_track || {};
  const safetyState = () => window.AGENT_SAFETY_PROGRAM_STATE || {};
  const researchState = () => window.RESEARCH_SYSTEM_STATE || {};
  const evidenceGraph = () => researchState().evidence_graph || {summary:{},nodes:[],edges:[]};
  const scientificGraph = () => researchState().scientific_research_graph || {summary:{},base_graph:{},overlay_nodes:[],overlay_edges:[]};
  const landscape = () => window.RESEARCH_LANDSCAPE || {verified_at:"",colors:{},papers:[]};
  const GROUP_TRACKS = {A:["constrained","credit"],B:["memory"],C:["evaluator","correction"],D:["curriculum"],E:["workflow"],F:["world"],G:[]};
  const DEFAULT_COLORS = {A:"#2f6fd6",B:"#0f8a7a",C:"#7c3aed",D:"#d97706",E:"#c2415d",F:"#2f855a",G:"#b42318"};
  const groupColor = id => landscape().colors?.[id] || DEFAULT_COLORS[id] || "#667085";
  const externalPapers = id => (landscape().papers || []).filter(row => row.group === id);
  const nodeText = node => {
    if (!node) return "";
    if (node.title && typeof node.title === "object") return textOf(node.title);
    if (node.text && typeof node.text === "object") return textOf(node.text);
    if (node.label && typeof node.label === "object") return textOf(node.label);
    return String(node.title || node.text || node.label || node.key || node.id || "");
  };
  const compact = (value,max=108) => { const text=String(value||"").replace(/\s+/g," ").trim(); return text.length>max?`${text.slice(0,max-1)}…`:text; };
  const norm = value => String(value||"").toLowerCase().replace(/[^a-z0-9]+/g,"");

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

  const colorLegend = groups => `<div class="rpm-color-legend">${groups.map(group=>`<a href="#research-map-${esc(group.id.toLowerCase())}" style="--group-color:${groupColor(group.id)}"><i></i><b>${esc(group.id)}</b><span>${textOf(group.title)}</span></a>`).join("")}</div>`;

  const portfolioSnapshot = (group, parents, inventory) => {
    const rows=parents.filter(row=>row.meta.group===group.id);
    const inv=inventory.byGroup[group.id] || {parent:0,related:0,context:0,closed:0,total:0};
    const status=groupState(group,rows,inv), insight=CATEGORY_BRIEFING_ZH[group.id] || {};
    const stops=rows.filter(row=>row.meta.status==="stop").length;
    const merges=rows.filter(row=>row.meta.status==="merge").length;
    return `<div class="rpm-internal-snapshot"><div class="rpm-lane-label"><b>${mapPick("我们的当前状态","Our current portfolio")}</b><span>${mapPick("权威状态在 ResearchItem","authoritative state in ResearchItem")}</span></div><div class="rpm-snapshot-state"><b>${esc(status.label)}</b><span>${esc(status.note)}</span></div><div class="rpm-snapshot-counts"><span><b>${inv.total}</b>${mapPick("总对象","objects")}</span><span><b>${inv.parent}</b>${mapPick("父级","parents")}</span><span><b>${inv.related}</b>${mapPick("方法","methods")}</span><span><b>${inv.context}</b>${mapPick("论文/证据","paper/evidence")}</span></div>${rows.length?`<div class="rpm-snapshot-terminal"><span>${mapPick("父级终态","Parent states")}</span><b>${mapPick(`停止 ${stops} · 合并 ${merges}`,`stopped ${stops} · merged ${merges}`)}</b></div>`:""}<div class="rpm-snapshot-judgment"><b>${mapPick("当前总体判断","Current judgment")}</b><p>${esc(insight.reason || mapPick("以每个 ResearchItem 当前裁决为准。","See individual ResearchItem decisions."))}</p></div><div class="rpm-snapshot-survives"><b>${mapPick("留下了什么","What survives")}</b><p>${esc(insight.survives || mapPick("保留有效组件、审计规则和负证据。","Useful components, audit rules, and negative evidence remain."))}</p></div><a class="link-btn" href="paper-ideas.html#canonical-group-${esc(group.id.toLowerCase())}">${mapPick(`打开 ${group.id} 类 ResearchItems →`,`Open category ${group.id} ResearchItems →`)}</a></div>`;
  };

  const mapStats = (inventory, terminal) => {
    const h=currentHeadline(), paper=currentPaper(), sg=scientificGraph().summary||{};
    return `<section class="rpm-stats"><article><b>7</b><span>${mapPick("当前研究集合","current research collections")}</span></article><article><b>${inventory.parent}</b><span>${mapPick("父级 ResearchItem","parent ResearchItems")}</span></article><article><b>${sg.nodes||0}</b><span>${mapPick("知识图谱节点","knowledge-graph nodes")}</span></article><article><b>${sg.edges||0}</b><span>${mapPick("知识图谱边","knowledge-graph edges")}</span></article><article class="rpm-paper-stat"><b>${h.paper_ready||0}</b><span>${mapPick("论文就绪","paper-ready")}</span></article><article><b>${h.launchable_formal_experiments||0}</b><span>${mapPick("可启动正式实验","launchable formal experiments")}</span></article></section><section class="rpm-current-banner"><div><span>${mapPick("当前最明确的内部产出","CLEAREST CURRENT INTERNAL OUTPUT")}</span><b>${esc(paper.title || "STRI")}</b><p>${mapPick(`状态：${paper.submission_status || paper.status || "--"}。论文主张、图表、QA 与投稿状态只在 PaperState 维护；图谱只引用这个状态。`,`Status: ${paper.submission_status || paper.status || "--"}. Claims, figures, QA, and submission state live only in PaperState; this graph only references that state.`)}</p></div><a class="link-btn" href="selected-paper.html">${mapPick("打开论文 · STRI →","Open Paper · STRI →")}</a></section>`;
  };

  const graphIndex = () => {
    const g=evidenceGraph();
    return {nodes:new Map((g.nodes||[]).map(node=>[node.id,node])),edges:g.edges||[],overlay:scientificGraph().overlay_nodes||[]};
  };

  const projectionForGroup = groupId => {
    const {nodes,edges,overlay}=graphIndex();
    const trackKeys=new Set(GROUP_TRACKS[groupId]||[]);
    const tracks=[...nodes.values()].filter(node=>node.kind==="track"&&trackKeys.has(node.key));
    const trackByKey=new Map(tracks.map(node=>[node.key,node]));
    const ideas=[...nodes.values()].filter(node=>node.kind==="idea"&&trackKeys.has(node.track_id)).sort((a,b)=>(Number(a.rank)||999)-(Number(b.rank)||999));
    const ideaIds=new Set(ideas.map(node=>node.id));
    const relationEdges=edges.filter(edge=>ideaIds.has(edge.source));
    const nearestTitles=relationEdges.filter(edge=>edge.relation==="nearest-work").map(edge=>nodeText(nodes.get(edge.target))).filter(Boolean);
    const preview=ideas.slice(0,3).map(idea=>{
      const problemEdge=relationEdges.find(edge=>edge.source===idea.id&&edge.relation==="states-problem");
      const problem=problemEdge?nodes.get(problemEdge.target):null;
      const nearest=relationEdges.filter(edge=>edge.source===idea.id&&edge.relation==="nearest-work").slice(0,3).map(edge=>nodes.get(edge.target)).filter(Boolean);
      const experiments=overlay.filter(node=>node.kind==="experiment"&&String(node.id||"").startsWith(`experiment:${idea.key}:`));
      return {idea,track:trackByKey.get(idea.track_id),problem,nearest,experiments};
    });
    return {tracks,ideas,relationEdges,nearestTitles,preview};
  };

  const graphNode = (kind,label,extra="") => `<span class="rpm-graph-node node-${esc(kind)}" title="${esc(label)}"><small>${esc(extra)}</small><b>${esc(compact(label,76))}</b></span>`;
  const graphEdge = relation => `<span class="rpm-graph-edge"><i></i><em>${esc(relation)}</em><i></i></span>`;

  const renderCanonicalChain = row => {
    const nearest=row.nearest||[];
    const experimentLabel=row.experiments.length ? `${row.experiments.length} ${mapPick("个 Experiment 节点","Experiment nodes")}` : mapPick("无投影 Experiment","no projected Experiment");
    return `<div class="rpm-graph-chain">${graphNode("track",nodeText(row.track)||row.idea.track_id,"Track")}${graphEdge("belongs-to")}${graphNode("idea",nodeText(row.idea),`Idea · #${row.idea.rank||"--"}`)}${row.problem?`${graphEdge("states-problem")}${graphNode("claim",nodeText(row.problem),"Claim")}`:""}</div><div class="rpm-graph-chain rpm-graph-chain-secondary">${graphNode("idea",nodeText(row.idea),"Idea")}${nearest.length?`${graphEdge("nearest-work")}${nearest.map(node=>graphNode("paper",nodeText(node),"Paper alias")).join("")}`:""}${graphEdge("tested-by")}${graphNode("experiment",experimentLabel,"Scientific overlay")}</div>`;
  };

  const renderSafetyChain = () => {
    const safety=safetyState();
    const stage=safety.current_stage||safety.candidate_stage||"CURRENT_SAFETY_SUPPORT_STOP";
    const gate=safety.next_gate?.name||"FRESH_BACKBONE_RUNTIME_SUPPORT_PREFLIGHT_REQUIRED";
    return `<div class="rpm-graph-chain">${graphNode("track",mapPick("Agent 自进化安全","Agent self-evolution safety"),"G")}${graphEdge("program-state")}${graphNode("idea",safety.program_id||"AGENT-SAFETY-R9","Research program")}${graphEdge("current-stage")}${graphNode("claim",stage,"State")}</div><div class="rpm-graph-chain rpm-graph-chain-secondary">${graphNode("idea",safety.program_id||"AGENT-SAFETY-R9","Research program")}${graphEdge("reopen-gate")}${graphNode("experiment",gate,mapPick("条件满足后再继续","resume only when satisfied"))}</div>`;
  };

  const externalPaperCard = (paper,aliasTitles) => {
    const linked=aliasTitles.some(title=>norm(title)===norm(paper.short)||norm(title)===norm(paper.title));
    const published=/正式发表|Published/.test(paper.status_zh||paper.status_en||"");
    return `<a class="rpm-external-paper ${published?"is-published":"is-preprint"}" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><b>${esc(paper.short||paper.title)}</b><span>${esc(mapPick(paper.status_zh,paper.status_en))}</span></header><p>${esc(mapPick(paper.advance_zh,paper.advance_en))}</p><small>${linked?mapPick("✓ canonical KG 中已有 nearest-work 对应节点","✓ matched to an existing canonical nearest-work node"):mapPick("公开文献覆盖层 · 不新增科研权限","public-literature overlay · no scientific authority")}</small></a>`;
  };

  const knowledgeLane = (group, parents, inventory) => {
    const projection=projectionForGroup(group.id), papers=externalPapers(group.id), color=groupColor(group.id);
    const aliasTitles=projection.nearestTitles||[];
    const inv=inventory.byGroup[group.id] || {total:0};
    const graphBody=group.id==="G"?renderSafetyChain():(projection.preview.length?projection.preview.map(renderCanonicalChain).join(""):`<div class="rpm-graph-empty">${mapPick("旧 evidence graph 在这一类还没有独立 Idea 节点；当前对象仍以 Research Portfolio 为准。","The older evidence graph has no standalone Idea node in this collection; current objects remain in Research Portfolio.")}</div>`);
    return `<section class="rpm-knowledge-lane" style="--group-color:${color}" id="research-map-${esc(group.id.toLowerCase())}"><header class="rpm-knowledge-lane-head"><span>${esc(group.id)}</span><div><b>${textOf(group.title)}</b><small>${group.id==="G"?mapPick("当前安全 program overlay","current safety program overlay"):mapPick(`${projection.ideas.length} 个历史 Idea 节点 · ${projection.relationEdges.length} 条关联边`,`${projection.ideas.length} historical Idea nodes · ${projection.relationEdges.length} relation edges`)}</small></div><div class="rpm-lane-scope-counts"><span><b>${inv.total}</b>${mapPick("我们的对象","our objects")}</span><span><b>${papers.length}</b>${mapPick("外部论文","external papers")}</span></div></header><div class="rpm-knowledge-lane-body"><div class="rpm-internal-landscape">${portfolioSnapshot(group,parents,inventory)}</div><div class="rpm-canonical-projection"><div class="rpm-lane-label"><b>${mapPick("我们的研究链 / Canonical KG","Our research lineage / Canonical KG")}</b><span>${mapPick("真实节点/边类型；这里只展示高价值子图","real node/edge types; high-value subgraph only")}</span></div><div class="rpm-graph-chains">${graphBody}</div></div><div class="rpm-external-landscape"><div class="rpm-lane-label"><b>${mapPick("其他团队公开研究现状","Public research status from other teams")}</b><span>${mapPick(`公开状态核验：${landscape().verified_at||"2026-08-21"}`,`public status checked: ${landscape().verified_at||"2026-08-21"}`)}</span></div><div class="rpm-external-paper-list">${papers.map(p=>externalPaperCard(p,aliasTitles)).join("")}</div></div></div></section>`;
  };

  const graphSchemaDetails = () => {
    const sg=scientificGraph().summary||{}, kinds=sg.node_kinds||{}, relations=sg.relations||{};
    const kindRows=Object.entries(kinds).sort((a,b)=>b[1]-a[1]);
    const relationRows=Object.entries(relations).sort((a,b)=>b[1]-a[1]);
    return `<details class="rpm-graph-schema"><summary><div><b>${mapPick("完整图谱类型与关系词典","Full graph type/relation dictionary")}</b><span>${mapPick(`${kindRows.length} 种节点 · ${relationRows.length} 种边；默认折叠，避免主图过载`,`${kindRows.length} node kinds · ${relationRows.length} edge types; collapsed by default to keep the main view readable`)}</span></div><strong>${sg.nodes||0} / ${sg.edges||0}</strong></summary><div class="rpm-schema-grid"><section><b>${mapPick("节点类型","Node kinds")}</b><div>${kindRows.map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section><section><b>${mapPick("边类型","Edge relations")}</b><div>${relationRows.map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section></div></details>`;
  };

  const knowledgeGraphPanel = (groups, parents, inventory) => {
    const sg=scientificGraph().summary||{}, base=scientificGraph().base_graph||{}, eg=evidenceGraph().summary||{};
    return `<section class="panel rpm-knowledge-panel"><div class="rpm-section-head rpm-knowledge-head"><div><div class="eyebrow">${mapPick("A–G 一体化研究地图","INTEGRATED A–G RESEARCH MAP")}</div><h2 id="current-knowledge-graph">${mapPick("我们的当前状态、研究链和外部论文放在同一坐标系","Our current portfolio, research lineage, and external papers in one coordinate system")}</h2><p>${mapPick(`每个 A–G 集合现在横向对齐三层：我们的 ResearchItem 当前状态、canonical graph 的 Track → Idea → Claim / nearest-work / Experiment 研究链，以及其他团队论文的公开研究状态。底层已有 ${sg.nodes||0} 个节点 / ${sg.edges||0} 条边，其中 evidence graph=${base.nodes||eg.nodes||0}/${base.edges||eg.edges||0}，scientific overlay=${sg.overlay_nodes||0}/${sg.overlay_edges||0}；主视图只投影高价值子图，避免变成“毛线团”。`,`Each A–G collection now aligns three layers horizontally: our current ResearchItem state, the canonical Track → Idea → Claim / nearest-work / Experiment lineage, and public research status from other teams. The underlying graph has ${sg.nodes||0} nodes / ${sg.edges||0} edges, including evidence graph=${base.nodes||eg.nodes||0}/${base.edges||eg.edges||0} and scientific overlay=${sg.overlay_nodes||0}/${sg.overlay_edges||0}; only high-value subgraphs are projected in the main view.`)}</p></div><div class="rpm-graph-summary"><span><b>${sg.nodes||0}</b>${mapPick("节点","nodes")}</span><span><b>${sg.edges||0}</b>${mapPick("边","edges")}</span><span><b>${(landscape().papers||[]).length}</b>${mapPick("核验外部论文","verified external papers")}</span></div></div>${graphSchemaDetails()}<div class="rpm-graph-legend"><span>${graphNode("track","Track","")}${mapPick("研究轨道","research track")}</span><span>${graphNode("idea","Idea","")}${mapPick("研究问题","research problem")}</span><span>${graphNode("claim","Claim","")}${mapPick("问题/主张","problem / claim")}</span><span>${graphNode("paper","Paper","")}${mapPick("最近工作","nearest work")}</span><span>${graphNode("experiment","Experiment","")}${mapPick("实验节点","experiment node")}</span></div><div class="rpm-knowledge-lanes">${groups.map(group=>knowledgeLane(group,parents,inventory)).join("")}</div><div class="rpm-knowledge-policy">${mapPick("外部论文的“正式发表 / 预印本”只是公开书目状态；canonical KG 和外部文献覆盖层都没有权限改变 ResearchItem 的 PASS / HOLD / STOP、实验授权或 PaperState。","Published/preprint is bibliographic status only. Neither the canonical KG nor the public-literature overlay can change ResearchItem decisions, experiment authority, or PaperState.")}</div></section>`;
  };

  const coverageSummary = (groups, inventory) => {
    const rows=groups.map(group=>({group,inv:inventory.byGroup[group.id]||{total:0,parent:0,context:0}}));
    const most=[...rows].sort((a,b)=>b.inv.total-a.inv.total).slice(0,3);
    const least=[...rows].sort((a,b)=>a.inv.total-b.inv.total).slice(0,3);
    return `<section class="panel rpm-gap-panel"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("组合覆盖 · 不是优先级评分","PORTFOLIO COVERAGE · NOT A PRIORITY SCORE")}</div><h2>${mapPick("哪里搜索得多，哪里当前覆盖得少","Where the portfolio is dense and where coverage is thin")}</h2><p>${mapPick("这里只用透明对象数量描述我们的内部组合覆盖，不把外部论文数量混进优先级，也不生成主观 Work Score。外部论文用于判断领域拥挤度和相邻工作，不自动决定下一轮做什么。","Only transparent internal-object counts describe our portfolio coverage. External-paper counts are not mixed into a priority score; they describe field activity and neighboring work rather than automatically deciding what to pursue next.")}</p></div></div><div class="rpm-gap-grid"><article><b>${mapPick("当前覆盖较密","Denser current coverage")}</b>${most.map(row=>`<span style="--group-color:${groupColor(row.group.id)}"><strong><i class="rpm-category-dot"></i>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><em>${row.inv.total} ${mapPick("个对象","objects")}</em></span>`).join("")}</article><article><b>${mapPick("当前覆盖较少","Thinner current coverage")}</b>${least.map(row=>`<span style="--group-color:${groupColor(row.group.id)}"><strong><i class="rpm-category-dot"></i>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><em>${row.inv.total} ${mapPick("个对象","objects")}</em></span>`).join("")}</article></div></section>`;
  };

  const readingBridge = () => `<section class="panel rpm-bridge"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("页面之间如何配合","HOW THE PAGES WORK TOGETHER")}</div><h2>${mapPick("领域历史、当前知识图谱和权威 ResearchItem 分层维护","Historical field knowledge, the current graph, and authoritative ResearchItems stay layered")}</h2></div></div><div class="rpm-bridge-grid"><a href="research-directions.html"><span>01</span><b>${mapPick("领域研究问题与历史方向","Field Problems & Historical Directions")}</b><p>${mapPick("看 D1–D10 历史 taxonomy、代表论文、方向边界、旧 Idea 谱系与历史长期议程。","See the historical D1–D10 taxonomy, representative papers, boundaries, idea lineage, and historical agenda.")}</p></a><i>→</i><a href="research-map.html"><span>02</span><b>${mapPick("当前研究组合 + 知识图谱","Current Portfolio + Knowledge Graph")}</b><p>${mapPick("把 A–G 当前组合、canonical graph 节点/边和其他团队公开论文状态放在同一个坐标系。","Overlay current A–G portfolio state, canonical graph nodes/edges, and public paper status from other teams.")}</p></a><i>→</i><a href="paper-ideas.html"><span>03</span><b>${mapPick("研究组合 · ResearchItems","Research Portfolio · ResearchItems")}</b><p>${mapPick("进入具体 Idea、实验、决定性证据、当前科学结论和重开条件；这里才是状态权威。","Inspect the concrete idea, experiments, decisive evidence, current decision, and reopen condition; this is the authoritative state layer.")}</p></a></div></section>`;

  window.renderCurrentResearchMap = function(config){
    const groups=canonicalIdeaGroups(), parents=canonicalParentRows(), independent=canonicalIndependentRows();
    const inventory=canonicalInventorySummary(groups,parents,independent), terminal=humanParentFinalSummary();
    return `${pageHeader(config)}${readingBridge()}${coverageSummary(groups,inventory)}${mapStats(inventory,terminal)}<section class="rpm-map-intro"><div><b>${mapPick("A–G 是当前正式坐标系；一个集合固定一种颜色","A–G is the current coordinate system; one collection uses one color")}</b><p>${mapPick("颜色只编码研究集合，不编码科学结论。PASS / HOLD / STOP、论文状态和实验权限继续用文字与独立标签表达，避免一张图里一套颜色承担两种语义。","Color encodes collection membership only, not scientific verdict. PASS / HOLD / STOP, paper status, and execution authority remain textual or independently labeled so one color never carries two meanings.")}</p></div><a class="link-btn" href="research-directions.html">${mapPick("查看历史领域方向 →","Open historical field directions →")}</a></section>${colorLegend(groups)}${knowledgeGraphPanel(groups,parents,inventory)}`;
  };
})();
