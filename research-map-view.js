(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-map"] = {
    eyebrow:{en:"Research Planning · Portfolio + Field Knowledge Graph",zh:"研究规划 · 当前组合 + 领域知识图谱"},
    title:{en:"Current Research Portfolio Map",zh:"当前研究组合图谱"},
    lead:{en:"One A–G map answers three questions at once: where our research stands, how the research lineage reached the current decision, and how far neighboring external work has progressed. Each collection keeps one color; color means research category, not good/bad or continue/stop.",zh:"这页同时回答三个问题：我们每个 A–G 方向现在做到哪里、为什么会走到今天这个结论、相邻的外部工作已经做到哪一步。每个集合固定一种颜色；颜色只表示研究类别，不表示好坏，也不表示继续或停止。"},
    callout:{en:"This page is for comparison and navigation; it does not change scientific decisions. A ResearchItem means one concrete research problem together with its experiments, evidence, current decision, and reopen condition. Final ResearchItem decisions remain on Research Portfolio. External papers show only public publication status and their main research advance.",zh:"这页用于对照和导航，不会改变任何科研结论。这里把“一个具体研究问题 + 相关实验 + 证据 + 当前结论 + 重开条件”统称为 ResearchItem；它的最终结论仍以“研究组合”页面为准。外部论文这里只展示公开发表情况和它实际推进了什么问题。"},
    sections:[]
  };

  const mapPick = (zh,en) => language === "zh" ? zh : en;
  const currentStatus = () => window.CURRENT_RESEARCH_STATUS || {};
  const currentHeadline = () => currentStatus().headline || {};
  const currentPaper = () => currentStatus().leading_paper_track || {};
  const safetyState = () => window.AGENT_SAFETY_PROGRAM_STATE || {};
  const researchState = () => window.RESEARCH_SYSTEM_STATE || {};
  const paperAcceptanceEntry = () => ((researchState().paper_acceptance?.ledger_index?.entries)||[]).find(row=>row.paper_id==="STRI-ICLR2027") || {};
  const PAPER_STAGE_ZH = {PAPER_EVIDENCE:"论文证据",PAPER_DESIGN:"论文设计",MANUSCRIPT:"成稿",MOCK_PC:"模拟审稿",TARGETED_REPAIR:"定向修复",CLAIM_AUDIT:"主张审计",PDF_QA:"PDF 检查",PREBUTTAL:"预答辩",SUBMISSION_READY:"可投稿",SUBMITTED:"已投稿",REBUTTAL:"Rebuttal",LEARN:"复盘"};
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
    if (group.id === "E" && Number(currentHeadline().paper_ready || 0) > 0) return {tone:"paper",label:mapPick("已有论文成果","Paper result"),note:mapPick("STRI 已进入论文阶段；这里继续保留它对应的研究问题、方法和证据链。","STRI is now in the paper stage while its problem, method, and evidence lineage remain visible here.")};
    if (group.id === "G") {
      const safety = safetyState();
      const stage = safety.current_stage || safety.candidate_stage || "";
      return {tone:"hold",label:mapPick("核心问题仍开放，当前实验条件不足","Core question open; current experiment conditions insufficient"),note:mapPick("现在还缺一组足够合格、当前都安全且能够公平匹配的状态；换到满足条件的模型和运行环境后才能重开。","A sufficiently qualified set of currently-safe, fairly matched states is still missing; the line can reopen on a suitable model/runtime substrate.")};
    }
    if (inv.context > 0) return {tone:"hold",label:mapPick("主要方向已有结论，但仍有证据值得保留","Main directions decided; evidence remains useful"),note:mapPick("本类的大多数主要方向已经停止或合并，但仍有历史现象、可重开条件或证据记录值得继续保留。","Most main directions have stopped or merged, while historical phenomena, reopen conditions, or evidence records remain useful.")};
    if (stops + merges === rows.length && rows.length) return {tone:"terminal",label:mapPick("主要方向都已有明确结论","All main directions have clear decisions"),note:mapPick(`当前主要方向中：停止 ${stops} 个，合并 ${merges} 个；现在没有新的正式实验可以启动。`,`Among current main directions, ${stops} are stopped and ${merges} merged; no new formal experiment can start now.`)};
    if (!rows.length) return {tone:"gap",label:mapPick("当前内部研究较少","Limited current internal coverage"),note:mapPick("这是一个真实的领域问题，但当前组合里没有独立的主要 ResearchItem 正在推进。","This is a real field problem, but the current portfolio has no standalone main ResearchItem advancing here.")};
    return {tone:"hold",label:mapPick("当前已有研究积累","Covered by current portfolio"),note:mapPick("具体为什么继续、停止或合并，请看对应 ResearchItem 的当前结论。","See the corresponding ResearchItem for why the direction continues, stops, or merges.")};
  };

  const colorLegend = groups => `<div class="rpm-color-legend">${groups.map(group=>`<a href="#research-map-${esc(group.id.toLowerCase())}" style="--group-color:${groupColor(group.id)}"><i></i><b>${esc(group.id)}</b><span>${textOf(group.title)}</span></a>`).join("")}</div>`;

  const portfolioSnapshot = (group, parents, inventory) => {
    const rows=parents.filter(row=>row.meta.group===group.id);
    const inv=inventory.byGroup[group.id] || {parent:0,related:0,context:0,closed:0,total:0};
    const status=groupState(group,rows,inv), insight=CATEGORY_BRIEFING_ZH[group.id] || {};
    const stops=rows.filter(row=>row.meta.status==="stop").length;
    const merges=rows.filter(row=>row.meta.status==="merge").length;
    return `<div class="rpm-internal-snapshot"><div class="rpm-lane-label"><b>${mapPick("我们现在做到哪里","Where our work stands")}</b><span>${mapPick("详细结论见 ResearchItem","details in ResearchItem")}</span></div><div class="rpm-snapshot-state"><b>${esc(status.label)}</b><span>${esc(status.note)}</span></div><div class="rpm-snapshot-counts"><span><b>${inv.total}</b>${mapPick("本类研究记录","records")}</span><span><b>${inv.parent}</b>${mapPick("主要方向","main directions")}</span><span><b>${inv.related}</b>${mapPick("关联方法","related methods")}</span><span><b>${inv.context}</b>${mapPick("论文/证据","paper/evidence")}</span></div>${rows.length?`<div class="rpm-snapshot-terminal"><span>${mapPick("主要方向当前结论","Main-direction decisions")}</span><b>${mapPick(`停止 ${stops} · 已合并 ${merges}`,`stopped ${stops} · merged ${merges}`)}</b></div>`:""}<div class="rpm-snapshot-judgment"><b>${mapPick("为什么现在这样处理","Why it stands here")}</b><p>${esc(insight.reason || mapPick("具体以对应 ResearchItem 当前结论为准。","See the corresponding ResearchItem decision."))}</p></div><div class="rpm-snapshot-survives"><b>${mapPick("哪些部分仍然有用","What remains useful")}</b><p>${esc(insight.survives || mapPick("保留仍有效的方法组件、审计规则和负证据。","Useful method components, audit rules, and negative evidence remain."))}</p></div><a class="link-btn" href="paper-ideas.html#canonical-group-${esc(group.id.toLowerCase())}">${mapPick(`查看 ${group.id} 类详细 ResearchItem →`,`Open detailed category ${group.id} ResearchItems →`)}</a></div>`;
  };

  const mapStats = (inventory, terminal) => {
    const h=currentHeadline(), paper=currentPaper(), sg=scientificGraph().summary||{}, acceptance=paperAcceptanceEntry();
    const graphCount=`${sg.nodes||0}/${sg.edges||0}`, paperStage=acceptance.current_state||"PAPER_EVIDENCE";
    const stageLabel=language==="zh"?(PAPER_STAGE_ZH[paperStage]||paperStage):paperStage.replaceAll("_"," ");
    const paperNote=paperStage==="TARGETED_REPAIR"
      ? mapPick("科学证据已经闭环，两轮模拟审稿（只看文稿 / 同时看论文工件）也已完成；当前正在按审稿意见做定向文稿修复。之后还要完成主张审计、PDF 与自动检查、预答辩和最终投稿检查，因此现在还不能正式提交。","Scientific evidence is closed and both mock-review modes are complete; the paper is currently in targeted manuscript repair. Claim audit, PDF/CI, prebuttal, and Submission Ready checks still remain, so it is not yet submission-ready.")
      : mapPick(`科学证据已闭环；论文接受流程当前处于“${stageLabel}”。是否可以提交，以论文页的最新 Paper Ledger 为准。`,`Scientific evidence is closed; the paper workflow is currently at ${stageLabel}. Submission readiness is governed by the latest Paper Ledger on the paper page.`);
    return `<section class="rpm-stats"><article><b>7</b><span>${mapPick("研究大类","research categories")}</span></article><article><b>${inventory.parent}</b><span>${mapPick("主要 ResearchItem","main ResearchItems")}</span></article><article><b>${(landscape().papers||[]).length}</b><span>${mapPick("代表性外部工作","representative external papers")}</span></article><article><b>${graphCount}</b><span>${mapPick("图谱节点 / 关系","graph nodes / edges")}</span></article><article class="rpm-paper-stat"><b>${h.paper_ready||0}</b><span>${mapPick("科学证据已闭环的论文","papers with closed scientific evidence")}</span></article><article><b>${h.launchable_formal_experiments||0}</b><span>${mapPick("现在可启动的正式实验","formal experiments launchable now")}</span></article></section><section class="rpm-current-banner"><div><span>${mapPick("当前最成熟成果","MOST MATURE CURRENT OUTPUT")} · ${esc(stageLabel)}</span><b>${esc(paper.title || acceptance.title || "STRI")}</b><p>${paperNote}</p></div><a class="link-btn" href="selected-paper.html">${mapPick("查看论文当前流程 →","Open current paper workflow →")}</a></section>`;
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
  const EDGE_LABELS_ZH = {"belongs-to":"归入","states-problem":"定义问题","nearest-work":"最近相关工作","tested-by":"实验验证","program-state":"项目状态","current-stage":"当前阶段","reopen-gate":"重开条件"};
  const graphEdge = relation => `<span class="rpm-graph-edge" title="${esc(relation)}"><i></i><em>${esc(language==="zh"?(EDGE_LABELS_ZH[relation]||relation):relation)}</em><i></i></span>`;

  const renderCanonicalChain = row => {
    const nearest=row.nearest||[];
    const experimentLabel=row.experiments.length ? `${row.experiments.length} ${mapPick("个实验记录","Experiment nodes")}` : mapPick("暂无对应实验记录","no projected Experiment");
    return `<div class="rpm-graph-chain">${graphNode("track",nodeText(row.track)||row.idea.track_id,mapPick("研究轨道","Track"))}${graphEdge("belongs-to")}${graphNode("idea",nodeText(row.idea),`${mapPick("研究问题","Idea")} · #${row.idea.rank||"--"}`)}${row.problem?`${graphEdge("states-problem")}${graphNode("claim",nodeText(row.problem),mapPick("问题 / 主张","Claim"))}`:""}</div><div class="rpm-graph-chain rpm-graph-chain-secondary">${graphNode("idea",nodeText(row.idea),mapPick("研究问题","Idea"))}${nearest.length?`${graphEdge("nearest-work")}${nearest.map(node=>graphNode("paper",nodeText(node),mapPick("相关论文","Paper alias"))).join("")}`:""}${graphEdge("tested-by")}${graphNode("experiment",experimentLabel,mapPick("实验记录","Scientific overlay"))}</div>`;
  };

  const renderSafetyChain = () => {
    const safety=safetyState();
    const stage=safety.current_stage||safety.candidate_stage||"CURRENT_SAFETY_SUPPORT_STOP";
    const gate=safety.next_gate?.name||"FRESH_BACKBONE_RUNTIME_SUPPORT_PREFLIGHT_REQUIRED";
    return `<div class="rpm-graph-chain">${graphNode("track",mapPick("Agent 自进化安全","Agent self-evolution safety"),"G")}${graphEdge("program-state")}${graphNode("idea",safety.program_id||"AGENT-SAFETY-R9",mapPick("安全研究主线","Research program"))}${graphEdge("current-stage")}${graphNode("claim",mapPick("当前实验条件不足，核心问题仍开放",stage),mapPick("当前状态","State"))}</div><div class="rpm-graph-chain rpm-graph-chain-secondary">${graphNode("idea",safety.program_id||"AGENT-SAFETY-R9",mapPick("安全研究主线","Research program"))}${graphEdge("reopen-gate")}${graphNode("experiment",mapPick("换到满足条件的模型和运行环境后重开",gate),mapPick("重开条件","resume only when satisfied"))}</div>`;
  };

  const externalPaperCard = (paper,aliasTitles) => {
    const linked=aliasTitles.some(title=>norm(title)===norm(paper.short)||norm(title)===norm(paper.title));
    const published=/正式发表|Published/.test(paper.status_zh||paper.status_en||"");
    return `<a class="rpm-external-paper ${published?"is-published":"is-preprint"}" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><b>${esc(paper.short||paper.title)}</b><span>${esc(mapPick(paper.status_zh,paper.status_en))}</span></header><p>${esc(mapPick(paper.advance_zh,paper.advance_en))}</p><small>${linked?mapPick("✓ 已与知识图谱中的相关工作节点匹配","✓ matched to an existing knowledge-graph paper node"):mapPick("代表性外部工作 · 仅用于领域对照","representative external work · for field comparison only")}</small></a>`;
  };

  const knowledgeLane = (group, parents, inventory) => {
    const projection=projectionForGroup(group.id), papers=externalPapers(group.id), color=groupColor(group.id);
    const aliasTitles=projection.nearestTitles||[];
    const inv=inventory.byGroup[group.id] || {total:0};
    const graphBody=group.id==="G"?renderSafetyChain():(projection.preview.length?projection.preview.map(renderCanonicalChain).join(""):`<div class="rpm-graph-empty">${mapPick("已有知识图谱在这一类还没有独立的历史研究问题节点；当前进展仍以左侧 ResearchItem 结论为准。","The existing knowledge graph has no standalone historical research-problem node in this collection; current progress remains defined by the ResearchItem decision on the left.")}</div>`);
    return `<section class="rpm-knowledge-lane" style="--group-color:${color}" id="research-map-${esc(group.id.toLowerCase())}"><header class="rpm-knowledge-lane-head"><span>${esc(group.id)}</span><div><b>${textOf(group.title)}</b><small>${group.id==="G"?mapPick("当前安全研究主线","current safety research line"):mapPick(`${projection.ideas.length} 个历史研究问题 · ${projection.relationEdges.length} 条关系`,`${projection.ideas.length} historical research problems · ${projection.relationEdges.length} relations`)}</small></div><div class="rpm-lane-scope-counts"><span><b>${inv.total}</b>${mapPick("内部研究记录","internal records")}</span><span><b>${papers.length}</b>${mapPick("代表性外部论文","representative papers")}</span></div></header><div class="rpm-knowledge-lane-body"><div class="rpm-internal-landscape">${portfolioSnapshot(group,parents,inventory)}</div><div class="rpm-canonical-projection"><div class="rpm-lane-label"><b>${mapPick("为什么走到这里（研究链）","How we got here (research lineage)")}</b><span>${mapPick("来自已有知识图谱；只显示最关键关系","from the existing knowledge graph; key relations only")}</span></div><div class="rpm-graph-chains">${graphBody}</div></div><div class="rpm-external-landscape"><div class="rpm-lane-label"><b>${mapPick("代表性外部工作（非完整综述）","Representative external work (not exhaustive)")}</b><span>${mapPick(`发表状态核验：${landscape().verified_at||"2026-08-21"}`,`publication status checked: ${landscape().verified_at||"2026-08-21"}`)}</span></div><div class="rpm-external-paper-list">${papers.map(p=>externalPaperCard(p,aliasTitles)).join("")}</div></div></div></section>`;
  };

  const graphSchemaDetails = () => {
    const sg=scientificGraph().summary||{}, kinds=sg.node_kinds||{}, relations=sg.relations||{};
    const kindRows=Object.entries(kinds).sort((a,b)=>b[1]-a[1]);
    const relationRows=Object.entries(relations).sort((a,b)=>b[1]-a[1]);
    return `<details class="rpm-graph-schema"><summary><div><b>${mapPick("图谱技术细节（可选）","Graph technical details (optional)")}</b><span>${mapPick(`${kindRows.length} 种节点 · ${relationRows.length} 种关系；需要审计图谱结构时再展开`,`${kindRows.length} node kinds · ${relationRows.length} relation types; expand only when auditing the graph structure`)}</span></div><strong>${sg.nodes||0} / ${sg.edges||0}</strong></summary><div class="rpm-schema-grid"><section><b>${mapPick("节点类型","Node kinds")}</b><div>${kindRows.map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section><section><b>${mapPick("边类型","Edge relations")}</b><div>${relationRows.map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section></div></details>`;
  };

  const knowledgeGraphPanel = (groups, parents, inventory) => {
    const sg=scientificGraph().summary||{}, base=scientificGraph().base_graph||{}, eg=evidenceGraph().summary||{};
    return `<section class="panel rpm-knowledge-panel"><div class="rpm-section-head rpm-knowledge-head"><div><div class="eyebrow">${mapPick("A–G 一体化研究地图","INTEGRATED A–G RESEARCH MAP")}</div><h2 id="current-knowledge-graph">${mapPick("同一行看：我们做到哪里、为什么走到这里、别人做到哪里","One row shows our status, the path here, and neighboring external work")}</h2><p>${mapPick(`每个 A–G 集合都按三栏阅读：左边看我们当前结论，中间看从历史研究问题到相关论文和实验的关键关系，右边看代表性外部工作已经公开做到哪一步。完整知识图谱共有 ${sg.nodes||0} 个节点 / ${sg.edges||0} 条关系；主页面只显示最关键的子图，技术细节默认折叠。`,`Each A–G collection has three columns: our current decision, the key lineage from earlier research problems to related papers and experiments, and representative external work. The full graph contains ${sg.nodes||0} nodes / ${sg.edges||0} relations; only the most useful subgraph is shown here, with technical details collapsed by default.`)}</p></div><div class="rpm-graph-summary"><span><b>${sg.nodes||0}</b>${mapPick("节点","nodes")}</span><span><b>${sg.edges||0}</b>${mapPick("边","edges")}</span><span><b>${(landscape().papers||[]).length}</b>${mapPick("代表性外部工作","representative external work")}</span></div></div>${graphSchemaDetails()}<div class="rpm-graph-legend"><span>${graphNode("track",mapPick("研究轨道","Track"),"")}${mapPick("研究轨道","research track")}</span><span>${graphNode("idea",mapPick("研究问题","Idea"),"")}${mapPick("研究问题","research problem")}</span><span>${graphNode("claim",mapPick("问题 / 主张","Claim"),"")}${mapPick("问题 / 主张","problem / claim")}</span><span>${graphNode("paper",mapPick("相关论文","Paper"),"")}${mapPick("相关论文","related paper")}</span><span>${graphNode("experiment",mapPick("实验记录","Experiment"),"")}${mapPick("实验记录","experiment record")}</span></div><div class="rpm-knowledge-lanes">${groups.map(group=>knowledgeLane(group,parents,inventory)).join("")}</div><div class="rpm-knowledge-policy">${mapPick("这里的外部论文只用于回答“别人公开做到哪里”，不会改变我们的 ResearchItem 结论、实验权限或论文状态。正式发表 / 预印本表示公开发表情况，不表示我们对论文科学质量的评分。","External papers answer only how far public work has progressed; they do not change our ResearchItem decisions, experiment permissions, or paper state. Published/preprint is publication status, not our scientific-quality rating.")}</div></section>`;
  };

  const coverageSummary = (groups, inventory) => {
    const rows=groups.map(group=>({group,inv:inventory.byGroup[group.id]||{total:0,parent:0,context:0}}));
    const most=[...rows].sort((a,b)=>b.inv.total-a.inv.total).slice(0,3);
    const least=[...rows].sort((a,b)=>a.inv.total-b.inv.total).slice(0,3);
    return `<section class="panel rpm-gap-panel"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("内部研究覆盖 · 不等于搜索次数","INTERNAL COVERAGE · NOT SEARCH FREQUENCY")}</div><h2>${mapPick("哪些方向我们已经积累得比较多，哪些目前覆盖较少","Where our internal research is dense and where coverage is thin")}</h2><p>${mapPick("这里统计的是已经记录下来的 ResearchItem、关联方法、论文/证据等对象数量，用来表示我们的内部研究积累。它不等于真正生成或搜索过多少 Idea，也不代表下一步优先级；外部论文数量同样不参与这个排序。","These counts summarize recorded ResearchItems, related methods, and paper/evidence objects. They indicate internal research accumulation, not how many ideas were actually generated or searched, and not what should be prioritized next. External-paper counts are not included in this ranking either.")}</p></div></div><div class="rpm-gap-grid"><article><b>${mapPick("内部积累较多","Denser internal accumulation")}</b>${most.map(row=>`<span style="--group-color:${groupColor(row.group.id)}"><strong><i class="rpm-category-dot"></i>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><em>${row.inv.total} ${mapPick("个对象","objects")}</em></span>`).join("")}</article><article><b>${mapPick("目前覆盖较少","Thinner current coverage")}</b>${least.map(row=>`<span style="--group-color:${groupColor(row.group.id)}"><strong><i class="rpm-category-dot"></i>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><em>${row.inv.total} ${mapPick("个对象","objects")}</em></span>`).join("")}</article></div></section>`;
  };

  const readingBridge = () => `<section class="panel rpm-bridge"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("先分清三层","THREE LAYERS TO KEEP SEPARATE")}</div><h2>${mapPick("领域怎么发展、我们为什么走到这里、每个 Idea 最终怎么判","Field history, the path to today's decisions, and final Idea decisions")}</h2></div></div><div class="rpm-bridge-grid"><a href="research-directions.html"><span>01</span><b>${mapPick("领域历史","Field history")}</b><p>${mapPick("解释 D1–D10 怎么形成、代表论文是什么，以及过去有哪些研究方向；它回答“这个领域有哪些问题”。","Explains how D1–D10 formed, representative papers, and historical directions; it answers what problems exist in the field.")}</p></a><i>→</i><a href="#current-knowledge-graph"><span>02</span><b>${mapPick("本页：研究全景","This page: research landscape")}</b><p>${mapPick("把我们现在的状态、过去的研究链和代表性外部论文放在 A–G 同一坐标系里比较。","Compares our current state, historical research lineage, and representative external work in the same A–G coordinates.")}</p></a><i>→</i><a href="paper-ideas.html"><span>03</span><b>${mapPick("研究组合：详细结论","Research Portfolio: detailed decisions")}</b><p>${mapPick("查看每个 ResearchItem 为什么继续、停止或合并，证据是什么，以及满足什么条件才能重开。","See why each ResearchItem continues, stops, or merges, what evidence supports that decision, and what would allow reopening.")}</p></a></div></section>`;

  window.renderCurrentResearchMap = function(config){
    const groups=canonicalIdeaGroups(), parents=canonicalParentRows(), independent=canonicalIndependentRows();
    const inventory=canonicalInventorySummary(groups,parents,independent), terminal=humanParentFinalSummary();
    return `${pageHeader(config)}${readingBridge()}${coverageSummary(groups,inventory)}${mapStats(inventory,terminal)}<section class="rpm-map-intro"><div><b>${mapPick("颜色只表示研究大类，不表示研究状态","Color shows research category, not research status")}</b><p>${mapPick("A–G 每类固定一种颜色。一个方向是继续、停止、合并还是已经进入论文阶段，直接看文字状态；不要根据颜色判断好坏或优先级。","Each A–G category keeps one color. Whether a direction continues, stops, merges, or has entered the paper stage is shown in text; color does not indicate quality or priority.")}</p></div><a class="link-btn" href="research-directions.html">${mapPick("查看历史领域方向 →","Open historical field directions →")}</a></section>${colorLegend(groups)}${knowledgeGraphPanel(groups,parents,inventory)}`;
  };
})();
