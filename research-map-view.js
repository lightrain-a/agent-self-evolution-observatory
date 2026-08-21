(() => {
  window.PAGE_CONTENT = window.PAGE_CONTENT || {};
  window.PAGE_CONTENT["research-map"] = {
    eyebrow:{en:"Current Research · Human-readable field + portfolio map",zh:"当前科研 · 面向理解的领域与研究组合图谱"},
    title:{en:"Current Research Portfolio Map",zh:"当前研究组合图谱"},
    lead:{en:"Read this page by question, not by database object: what each A–G area is asking, where our work stands, what neighboring papers have already established, and why our current decision follows from the evidence.",zh:"这页不要求先理解数据库或状态机。按 A–G 七个问题读即可：这个方向在研究什么、我们现在做到哪里、别人已经做到哪里、为什么我们会形成今天这个结论。"},
    callout:{en:"ResearchItem is the system's canonical record for one concrete research problem and its evidence. This page summarizes those records for people; the Research Portfolio remains the place to inspect the full decision and evidence trail.",zh:"系统内部把“一条具体研究问题及其实验、证据、当前结论和重开条件”记作 ResearchItem。本页只做人能快速理解的摘要；要核查完整证据和正式裁决，再进入“研究组合”页面。"},
    sections:[]
  };

  const mapPick = (zh,en) => language === "zh" ? zh : en;
  const researchItemsState = () => window.RESEARCH_ITEM_STATE || {categories:[],summary:{},research_items:[],experiment_records:[],evidence_contexts:[]};
  const paperRegistry = () => window.PAPER_REGISTRY || {summary:{},papers:[]};
  const dashboard = () => window.RESEARCH_DASHBOARD || {summary:{},attention:[],papers:[],week:{highlights:[]}};
  const currentStatus = () => window.CURRENT_RESEARCH_STATUS || {};
  const researchState = () => window.RESEARCH_SYSTEM_STATE || {};
  const evidenceGraph = () => researchState().evidence_graph || {summary:{},nodes:[],edges:[]};
  const scientificGraph = () => researchState().scientific_research_graph || {summary:{},base_graph:{},overlay_nodes:[],overlay_edges:[]};
  const landscape = () => window.RESEARCH_LANDSCAPE || {verified_at:"",colors:{},papers:[]};
  const GROUP_TRACKS = {A:["constrained","credit"],B:["memory"],C:["evaluator","correction"],D:["curriculum"],E:["workflow"],F:["world"],G:[]};
  const DEFAULT_COLORS = {A:"#2f6fd6",B:"#0f8a7a",C:"#7c3aed",D:"#d97706",E:"#c2415d",F:"#2f855a",G:"#b42318"};
  const STATE_LABELS = {
    PAPER_READY:{zh:"已进入论文",en:"Paper result"},
    HOLD:{zh:"等待明确条件",en:"Waiting on a condition"},
    MERGED:{zh:"已并入更大方向",en:"Merged into a larger line"},
    STOPPED:{zh:"已形成停止结论",en:"Stopped with a clear decision"}
  };
  const SOURCE_ORDER = {paper_source:0,parent:1,safety:1,paper_first:2,independent_method:3,shadow_closed:4};
  const STATE_ORDER = {PAPER_READY:0,HOLD:1,MERGED:2,STOPPED:3};
  const PAPER_STAGE_ZH = {PAPER_EVIDENCE:"论文证据",PAPER_DESIGN:"论文设计",MANUSCRIPT:"成稿",MOCK_PC:"模拟审稿",TARGETED_REPAIR:"定向修复",CLAIM_AUDIT:"主张审计",PDF_QA:"PDF 检查",PREBUTTAL:"预答辩",SUBMISSION_READY:"可投稿",SUBMITTED:"已投稿",REBUTTAL:"答辩",LEARN:"复盘"};

  const groupColor = id => landscape().colors?.[id] || DEFAULT_COLORS[id] || "#667085";
  const externalPapers = id => (landscape().papers || []).filter(row => row.group === id);
  const normTitle = value => String(value||"").toLowerCase().replace(/[^a-z0-9]+/g,"");
  const isFormalVenue = venue => Boolean(venue) && !/arxiv|openreview|workshop|poster/i.test(String(venue));
  const FORMAL_TITLE_GROUPS = {
    "STaR: Bootstrapping Reasoning With Reasoning":["D"],
    "ReAct: Synergizing Reasoning and Acting in Language Models":["E"],
    "Self-Instruct: Aligning Language Models with Self-Generated Instructions":["D"],
    "Toolformer: Language Models Can Teach Themselves to Use Tools":["E"],
    "Reflexion: Language Agents with Verbal Reinforcement Learning":["B","C"],
    "Self-Refine: Iterative Refinement with Self-Feedback":["C"],
    "Large Language Models as Optimizers":["A"],
    "Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization":["A"],
    "Voyager: An Open-Ended Embodied Agent with Large Language Models":["E","F"],
    "Self-Rewarding Language Models":["C"],
    "Self-Evolving Visual Concept Library using Vision-Language Critics":["B"],
    "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning":["C"],
    "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning":["C"],
    "Can Large Vision-Language Models Correct Semantic Grounding Errors By Themselves?":["C"],
    "Phoenix: A Motion-based Self-Reflection Framework for Fine-grained Robotic Action Correction":["C","F"],
    "CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update":["E"],
    "Self-Training Large Language Models for Improved Visual Program Synthesis with Visual Reinforcement":["D"],
    "Visual Agentic AI for Spatial Reasoning with a Dynamic API":["E"],
    "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning":["D"],
    "Automated Design of Agentic Systems":["E"],
    "AFlow: Automating Agentic Workflow Generation":["E"],
    "Multi-agent Architecture Search via Agentic Supernet":["E"],
    "LensWalk: Agentic Video Understanding by Planning How You See in Videos":["F"],
    "VisPlay: Self-Evolving Vision-Language Models":["D"],
    "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding":["E"],
    "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval":["B"],
    "JarvisEvo: Towards a Self-Evolving Photo Editing Agent with Synergistic Editor-Evaluator Optimization":["C"],
    "OctoT2I: A Self-Evolving Agentic Text-to-Image Router":["E"],
    "VISTA: A Test-Time Self-Improving Video Generation Agent":["C"],
    "OVOD-Agent: A Markov-Bandit Framework for Proactive Visual Reasoning and Self-Evolving Detection":["C"],
    "Learning to Adapt: Self-Improving Web Agent via Cognitive-Aware Exploration":["D"],
    "History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation":["B","F"],
    "Agentic Video Summarization via Self-Reflecting Multimodal Understanding":["C"],
    "MIRA: Multimodal Iterative Reasoning Agent for Image Editing":["C"],
    "ReFAct: Empowering Multimodal Web Agents with Visual and Context Focusing":["E"],
    "Unified Multimodal Models as Auto-Encoders":["C"],
    "SciEducator: Scientific Video Understanding and Educating via Deming-Cycle Multi-Agent System":["E"],
    "OSPO: Object-Centric Self-Improving Preference Optimization for Text-to-Image Generation":["C"],
    "Seeing is Improving: Visual Feedback for Iterative Text Layout Refinement":["C"],
    "WorldMM: Dynamic Multimodal Memory Agent for Long Video Reasoning":["B"],
    "ViLoMem: Agentic Learner with Grow-and-Refine Multimodal Semantic Memory":["B"],
    "PersonaVLM: Long-Term Personalized Multimodal LLMs":["B"],
    "Explore with Long-term Memory: A Benchmark and Multimodal LLM-based Reinforcement Learning Framework for Embodied Exploration":["B","F"],
    "R4: Retrieval-Augmented Reasoning for Vision-Language Models in 4D Spatio-Temporal Space":["B","F"],
    "VideoARM: Agentic Reasoning over Hierarchical Memory for Long-Form Video Understanding":["B"]
  };
  const formalGroupsFor = row => {
    if (Array.isArray(row.groups) && row.groups.length) return row.groups;
    if (FORMAL_TITLE_GROUPS[row.title]) return FORMAL_TITLE_GROUPS[row.title];
    const category=String(row.category||""), target=String(row.updateTarget||"");
    if (/Safety/i.test(category)) return ["G"];
    if (/Memory/i.test(category)||/Personalization/i.test(category)) return ["B"];
    if (/Tool|Skill|Workflow/i.test(category)||/tool\/skill|workflow\/scaffold/i.test(target)) return ["E"];
    if (/Embodied/i.test(category)) return ["F"];
    if (/Related Self-Correction|Prompt Evolution/i.test(category)) return ["C"];
    if (/GUI & Web/i.test(category)) return ["D"];
    if (/Model Improvement/i.test(category)) return ["D"];
    if (/Visual & Multimodal/i.test(category)) {
      if (/memory/i.test(target)) return ["B"];
      if (/tool|skill|workflow/i.test(target)) return ["E"];
      if (/prompt|model parameters/i.test(target)) return ["C"];
    }
    return [];
  };
  const formalBaseRelevant = row => {
    if (!isFormalVenue(row.venue) || Number(row.year||0)<2022) return false;
    if (row.category==="Foundations") return false;
    if (row.category==="Agent Foundations") return row.title==="ReAct: Synergizing Reasoning and Acting in Language Models";
    return formalGroupsFor(row).length>0;
  };
  const formalPublishedPapers = () => {
    const raw=[...(window.SUPPLEMENTAL_PAPERS||[]).filter(formalBaseRelevant),...(landscape().formal_papers||[])];
    const seen=new Set(), rows=[];
    raw.forEach(row=>{
      const key=normTitle(row.title); if(!key||seen.has(key)) return; seen.add(key);
      const groups=formalGroupsFor(row); if(!groups.length) return;
      rows.push({...row,groups,short:row.short||row.title,advance_zh:row.advance_zh||row.summaryZh||row.summary||"",advance_en:row.advance_en||row.summary||row.summaryZh||""});
    });
    return rows.sort((a,b)=>Number(a.year)-Number(b.year)||String(a.venue).localeCompare(String(b.venue))||String(a.title).localeCompare(String(b.title)));
  };
  const formalPapersForGroup = id => formalPublishedPapers().filter(row=>(row.groups||[]).includes(id));
  const frontierPapersForGroup = id => externalPapers(id).filter(row=>!/正式发表|Published/.test(String(row.status_zh||row.status_en||"")) && !formalPublishedPapers().some(formal=>normTitle(formal.title)===normTitle(row.title)));
  const compact = (value,max=170) => { const text=String(value||"").replace(/\s+/g," ").trim(); return text.length>max?`${text.slice(0,max-1)}…`:text; };
  const valueText = value => {
    if (!value) return "";
    if (typeof value === "object") return textOf(value);
    return String(value);
  };
  const stateLabel = state => mapPick(STATE_LABELS[state]?.zh || state || "--", STATE_LABELS[state]?.en || state || "--");

  const mapGroups = () => {
    const oldGroups = new Map((window.HUMAN_REVIEW_IDEA_MAP?.groups || []).map(row=>[row.id,row]));
    const categories = researchItemsState().categories || [];
    const categoryIds=new Set(categories.map(row=>row.id));
    const complete=["A","B","C","D","E","F","G"].every(id=>categoryIds.has(id));
    if (complete) {
      return categories.filter(row=>["A","B","C","D","E","F","G"].includes(row.id)).map(row=>({
        id:row.id,
        title:row.title,
        question:oldGroups.get(row.id)?.question || (row.id==="G"
          ? {zh:"当前静态安全检查能否预测持久状态与经验继续演化后的未来首次违规风险？",en:"Can current static safety evaluation predict future first-violation risk after persistent state and experience continue to evolve?"}
          : {zh:"",en:""})
      }));
    }
    return canonicalIdeaGroups();
  };

  const groupItems = groupId => (researchItemsState().research_items || []).filter(row=>row.category===groupId);
  const groupInventory = groupId => researchItemsState().summary?.by_category?.[groupId] || {research_items:0,experiment_contexts:0,evidence_contexts:0,portfolio_total:0};
  const groupStateCounts = groupId => groupItems(groupId).reduce((acc,row)=>{acc[row.scientific_state]=(acc[row.scientific_state]||0)+1; return acc;},{});

  const paperForGroup = groupId => (paperRegistry().papers || []).filter(row=>String(row.source_research_item||"").startsWith(`${groupId}-`));
  const primaryItems = groupId => groupItems(groupId)
    .filter(row=>row.source_kind!=="shadow_closed")
    .sort((a,b)=>(STATE_ORDER[a.scientific_state]??9)-(STATE_ORDER[b.scientific_state]??9)||(SOURCE_ORDER[a.source_kind]??9)-(SOURCE_ORDER[b.source_kind]??9)||String(a.code||"").localeCompare(String(b.code||""),undefined,{numeric:true}));
  const attentionItems = groupId => primaryItems(groupId).filter(row=>["PAPER_READY","HOLD"].includes(row.scientific_state));
  const settledPrimaryItems = groupId => primaryItems(groupId).filter(row=>!["PAPER_READY","HOLD"].includes(row.scientific_state));

  const categoryHeadline = groupId => {
    const counts=groupStateCounts(groupId), papers=paperForGroup(groupId);
    if (papers.some(row=>row.scientific_status==="READY")) {
      const paper=papers.find(row=>row.scientific_status==="READY")||papers[0], stage=paper.paper_stage||paper.current_state||"PAPER_EVIDENCE";
      const stageText=language==="zh"?(PAPER_STAGE_ZH[stage]||stage):stage.replaceAll("_"," ");
      const hold=counts.HOLD||0;
      return mapPick(`已有论文成果：STRI 科学证据已闭环，论文流程在“${stageText}”；本类另有 ${hold} 个问题仍等待条件满足。`,`Paper result: STRI has closed scientific evidence and is at ${stageText}; ${hold} other item(s) remain on hold.`);
    }
    if ((counts.HOLD||0)>0) return mapPick(`${counts.HOLD} 个问题仍值得保留，但当前缺少继续推进所需的明确条件或可执行证据。`,`${counts.HOLD} item(s) remain scientifically interesting but are waiting for specific conditions or executable evidence.`);
    return mapPick("当前没有独立推进中的 ResearchItem；这一类主要由已经停止的路线和并入系统的有效资产构成。","No standalone ResearchItem is currently advancing; this category is mainly composed of stopped lines and retained/merged assets.");
  };

  const readingBridge = () => `<section class="panel rpm-bridge"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("先知道这三页分别回答什么","THREE PAGES, THREE QUESTIONS")}</div><h2 data-toc="false">${mapPick("领域有什么问题、我们现在在哪里、每个 Idea 为什么这样判","Field questions, our current position, and the evidence behind each decision")}</h2></div></div><div class="rpm-bridge-grid"><a href="research-directions.html"><span>01</span><b>${mapPick("领域历史","Field history")}</b><p>${mapPick("回答“这个领域有哪些问题、过去怎么分类、代表论文是什么”。","Answers what problems exist, how the field was historically organized, and which papers define it.")}</p></a><i>→</i><a href="#a-g-overview"><span>02</span><b>${mapPick("本页：当前全景","This page: current landscape")}</b><p>${mapPick("回答“我们在哪些问题上做得多、现在是什么结论、别人已经做到哪里”。","Answers where we have worked, what we currently conclude, and how far neighboring public work has progressed.")}</p></a><i>→</i><a href="paper-ideas.html"><span>03</span><b>${mapPick("研究组合：完整证据","Research Portfolio: full evidence")}</b><p>${mapPick("回答“某个具体 Idea 为什么继续、停止或合并，证据和重开条件是什么”。","Answers why a concrete idea continues, stops, or merges, with the full evidence and reopen condition.")}</p></a></div></section>`;

  const coverageSummary = groups => {
    const rows=groups.map(group=>({group,inv:groupInventory(group.id)}));
    const most=[...rows].sort((a,b)=>(b.inv.portfolio_total||0)-(a.inv.portfolio_total||0)).slice(0,3);
    const least=[...rows].sort((a,b)=>(a.inv.portfolio_total||0)-(b.inv.portfolio_total||0)).slice(0,3);
    const rowHtml=row=>`<span style="--group-color:${groupColor(row.group.id)}"><strong><i class="rpm-category-dot"></i>${esc(row.group.id)} · ${textOf(row.group.title)}</strong><em>${row.inv.portfolio_total||0} ${mapPick("条内部记录","internal records")}</em></span>`;
    return `<section class="panel rpm-gap-panel"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("内部研究积累 · 不等于搜索次数","INTERNAL ACCUMULATION · NOT SEARCH FREQUENCY")}</div><h2 data-toc="false">${mapPick("哪些方向我们已经研究得比较多，哪些目前覆盖较少","Where we have accumulated more research and where coverage remains thin")}</h2><p>${mapPick("这里直接读取 canonical ResearchItem 总账，统计已经沉淀成研究记录的对象数量。它不表示真正生成过多少 Idea，也不自动代表下一步优先级。","These counts come directly from the canonical ResearchItem ledger. They measure recorded research objects, not the number of ideas ever generated and not automatic priority.")}</p></div></div><div class="rpm-gap-grid"><article><b>${mapPick("内部积累较多","More internal accumulation")}</b>${most.map(rowHtml).join("")}</article><article><b>${mapPick("目前覆盖较少","Thinner current coverage")}</b>${least.map(rowHtml).join("")}</article></div></section>`;
  };

  const topStats = groups => {
    const s=researchItemsState().summary||{}, states=s.scientific_state_counts||{}, ps=paperRegistry().summary||{}, formal=formalPublishedPapers();
    const frontier=(landscape().papers||[]).filter(row=>!/正式发表|Published/.test(String(row.status_zh||row.status_en||"")));
    return `<section class="rpm-stats"><article><b>${groups.length}</b><span>${mapPick("研究大类","research categories")}</span></article><article><b>${s.portfolio_objects||0}</b><span>${mapPick("内部研究记录","internal research records")}</span></article><article><b>${states.HOLD||0}</b><span>${mapPick("仍等待条件的 ResearchItem","ResearchItems on hold")}</span></article><article class="rpm-paper-stat"><b>${formal.length}</b><span>${mapPick("已收录正式发表论文","formally published papers")}</span></article><article><b>${frontier.length}</b><span>${mapPick("前沿预印本补充","frontier preprints")}</span></article><article><b>${ps.submission_ready||0}</b><span>${mapPick("我们真正可投稿","our truly submission-ready papers")}</span></article></section>`;
  };

  const currentControlBoard = () => {
    const d=dashboard(), s=d.summary||{}, rows=d.attention||[], week=d.week||{};
    if(!rows.length) return "";
    const primary=rows.find(row=>row.scientific_state==="PAPER_READY")||rows[0];
    const holds=rows.filter(row=>row.scientific_state==="HOLD");
    const label=row=>stateLabel(row.scientific_state);
    const brief=row=>mapPick(row.briefing_zh||row.current_reason_zh||"",row.briefing_en||row.current_reason_zh||"");
    const next=row=>mapPick(row.next_step_zh||row.reopen_condition_zh||"",row.next_step_en||row.reopen_condition_zh||"");
    const stage=stageValue=>language==="zh"?(PAPER_STAGE_ZH[stageValue]||stageValue||"--"):String(stageValue||"--").replaceAll("_"," ");
    const rowCard=row=>`<article class="rpm-control-row state-${String(row.scientific_state||"").toLowerCase()}" data-dashboard-research="${esc(row.code)}"><header><span>${esc(row.code)}</span><b>${esc(valueText(row.title)||row.code)}</b><em>${esc(label(row))}</em></header><p>${esc(brief(row))}</p><small><b>${mapPick("下一步 / 重开前置：","Next / reopen prerequisite: ")}</b>${esc(next(row))}</small><footer><a href="${esc(row.portfolio_href||"paper-ideas.html")}">${mapPick("完整证据","Full evidence")}</a><a href="${esc(row.timeline_href||"research-timeline.html")}">${mapPick("时间线","Timeline")}</a>${row.paper_href?`<a href="${esc(row.paper_href)}">PaperState</a>`:""}</footer></article>`;
    const highlights=(week.highlights||[]).slice(0,4).map(row=>`<a class="rpm-control-highlight" href="${esc(row.href||"research-timeline.html")}"><span>${esc(row.date||"")}</span><b>${esc(mapPick(row.title_zh||row.title_en||"",row.title_en||row.title_zh||""))}</b><small>${esc((row.research_items||[]).join(" · ") || (row.papers||[]).join(" · ") || row.event_class || "")}</small></a>`).join("");
    const primaryPaper=primary.paper_id?`${primary.paper_id} · ${stage(primary.paper_stage)}`:label(primary);
    const readyText=mapPick(s.submission_ready?`${s.submission_ready} 篇论文已投稿就绪`:`${s.paper_ready||0} 条论文线`,s.submission_ready?`${s.submission_ready} submission-ready paper`:`${s.paper_ready||0} paper line`);
    const readyKpi=s.submission_ready||s.paper_ready||0, readyKpiLabel=mapPick(s.submission_ready?"真正投稿就绪":"论文线",s.submission_ready?"truly submission-ready":"paper-ready line");
    return `<section class="panel rpm-control-board" id="current-control-board"><header class="rpm-control-head"><div><div class="eyebrow">${mapPick("当前队列 · 只看需要行动的对象","CURRENT QUEUE · ACTIONABLE OBJECTS ONLY")} · ${esc(d.as_of_date||"")}</div><h2 data-toc="false">${mapPick(`现在真正需要盯住的只有 ${rows.length} 个对象：${readyText}，${holds.length} 个条件 HOLD，正式实验权限=${s.launchable_formal_experiments||0}`,`Only ${rows.length} objects need active attention: ${readyText}, ${holds.length} conditional HOLDs, formal experiment authority=${s.launchable_formal_experiments||0}`)}</h2><p>${mapPick("这里不把 STOP/MERGED 的历史方向重新塞回待办。HOLD 也不是原理失败：只有各自写明的重开条件满足后，才回到 ResearchItem 重新评审。","Stopped/merged historical lines do not re-enter the queue. HOLD is not a principle failure: each line returns to review only after its explicit reopen condition is satisfied.")}</p></div><a class="link-btn" href="paper-ideas.html">${mapPick("打开完整研究组合 →","Open full portfolio →")}</a></header><div class="rpm-control-kpis"><span><b>${s.current_attention||rows.length}</b>${mapPick("当前关注对象","current attention")}</span><span><b>${readyKpi}</b>${readyKpiLabel}</span><span><b>${s.holds||0}</b>${mapPick("条件 HOLD","conditional HOLDs")}</span><span><b>${s.launchable_formal_experiments||0}</b>${mapPick("可启动正式实验","launchable formal experiments")}</span></div><div class="rpm-control-grid"><section class="rpm-control-main"><article class="rpm-control-primary" data-dashboard-research="${esc(primary.code)}"><header><span>${esc(primary.code)} → ${esc(primary.paper_id||"PaperState")}</span><em>${esc(primaryPaper)}</em></header><h3 data-toc="false">${esc(valueText(primary.title)||primary.code)}</h3><p>${esc(brief(primary))}</p><div><b>${mapPick("现在做什么","What happens now")}</b><span>${esc(next(primary))}</span></div><footer><a class="link-btn" href="${esc(primary.paper_href||"selected-paper.html")}">PaperState →</a><a class="link-btn" href="${esc(primary.timeline_href||"research-timeline.html")}">${mapPick("完整时间线 →","Full timeline →")}</a></footer></article><div class="rpm-control-list">${holds.map(rowCard).join("")}</div></section><aside class="rpm-control-week"><header><div><b>${mapPick("最近一周的关键变化","Key changes this week")}</b><span>${esc(week.start_date||"")} → ${esc(week.end_date||"")}</span></div><a href="${esc(week.timeline_href||"research-timeline.html")}">${mapPick("全部 →","All →")}</a></header><div class="rpm-control-week-kpis"><span><b>${week.research_days||0}</b>${mapPick("研究日","days")}</span><span><b>${week.substantive_events||0}</b>${mapPick("科研事件","research events")}</span><span><b>${week.key_changes||0}</b>${mapPick("关键变化","key changes")}</span></div><div class="rpm-control-highlights">${highlights}</div><p class="rpm-control-note">${mapPick("周摘要用于快速定位变化；具体科研结论与权限继续以对应 ResearchItem / PaperState 为准。","Weekly highlights locate change quickly; exact scientific decisions and authority remain in the linked ResearchItem / PaperState.")}</p></aside></div></section>`;
  };

  const formalPaperRow = paper => `<a class="rpm-formal-paper-row" href="${esc(paper.url)}" target="_blank" rel="noopener"><span class="rpm-formal-venue"><b>${esc(paper.year)}</b>${esc(paper.venue)}</span><div><b>${esc(paper.short||paper.title)}</b><p>${esc(mapPick(paper.advance_zh,paper.advance_en)||paper.title)}</p></div><span class="rpm-formal-groups">${(paper.groups||[]).map(id=>`<i style="--group-color:${groupColor(id)}">${esc(id)}</i>`).join("")}</span></a>`;

  const formalPublicationTimeline = () => {
    const papers=formalPublishedPapers(), years=[...new Set(papers.map(row=>Number(row.year)))].sort((a,b)=>a-b), venues=[...new Set(papers.map(row=>String(row.venue)))];
    return `<section class="panel rpm-formal-timeline" id="formal-publication-lineage"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("正式发表主线 · 非 arXiv","FORMALLY PUBLISHED LINEAGE · NON-ARXIV")}</div><h3 id="formal-publication-lineage-heading" data-toc-label="${esc(mapPick("正式发表论文的发展主线","Formal publication lineage"))}">${mapPick(`把 ${papers.length} 篇正式会议 / 期刊论文按年份排开，看这个领域怎样一步步形成`,`Follow ${papers.length} formally published conference/journal papers across time`)}</h3><p>${mapPick("这里优先收录已经进入正式会议或期刊 proceedings 的工作；同一论文如果同时有 arXiv，只保留正式版本。收录范围以本研究站的 Agent self-evolution / persistent adaptation 语料为边界，并补充近期漏收的 ICLR、ICML、ACL、EMNLP、NAACL、CVPR 等正式论文。","This section prioritizes formal conference/journal proceedings; when a paper also has an arXiv version, only the formal version is kept. Coverage follows this observatory's agent self-evolution/persistent-adaptation corpus plus recently verified formal publications.")}</p></div><div class="rpm-formal-summary"><span><b>${papers.length}</b>${mapPick("正式论文","formal papers")}</span><span><b>${venues.length}</b>${mapPick("venue / track","venues / tracks")}</span><span><b>${years.length}</b>${mapPick("发表年份","publication years")}</span></div></div><div class="rpm-formal-years">${years.map(year=>{const rows=papers.filter(row=>Number(row.year)===year);return `<details class="rpm-formal-year" open><summary><b>${year}</b><span>${rows.length} ${mapPick("篇正式论文","formal papers")}</span></summary><div class="rpm-formal-paper-list">${rows.map(formalPaperRow).join("")}</div></details>`;}).join("")}</div></section>`;
  };

  const overviewIndex = groups => `<section class="panel rpm-overview" id="a-g-overview"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("A–G 快速总览","A–G AT A GLANCE")}</div><h2 data-toc="false">${mapPick("先用 30 秒看完七个方向，再决定往下读哪一类","Scan all seven areas in 30 seconds, then open the ones that matter")}</h2><p>${mapPick("每张卡显示：这个方向问什么、我们现在是什么状态、正式发表论文有多少、前沿预印本有多少。","Each card shows the question, our current state, formally published literature, and frontier preprints.")}</p></div></div><div class="rpm-overview-grid">${groups.map(group=>{const inv=groupInventory(group.id),formal=formalPapersForGroup(group.id),frontier=frontierPapersForGroup(group.id),counts=groupStateCounts(group.id);return `<a href="#research-map-${esc(group.id.toLowerCase())}" class="rpm-overview-card" style="--group-color:${groupColor(group.id)}"><header><span>${esc(group.id)}</span><b>${textOf(group.title)}</b></header><p>${textOf(group.question)}</p><small>${counts.PAPER_READY?mapPick("已有论文成果","paper result"):counts.HOLD?mapPick(`${counts.HOLD} 个问题等待条件`,`${counts.HOLD} on hold`):mapPick("当前无独立推进方向","no standalone active line")}</small><footer><span>${inv.portfolio_total||0} ${mapPick("内部记录","internal")}</span><span>${formal.length} ${mapPick("正式论文","formal")}</span><span>${frontier.length} ${mapPick("预印本","preprints")}</span></footer></a>`;}).join("")}</div></section>`;

  const humanDecision = item => {
    const code=String(item.decision_code||""), layer=String(item.failure_layer||"");
    if(item.scientific_state==="PAPER_READY") return mapPick("核心科学主张已有对应证据，科研对象已经交给论文流程；现在主要是文稿与投稿质量控制。","Core scientific claims are evidence-backed and the research object has handed off to the paper workflow.");
    if(item.scientific_state==="HOLD") return mapPick("这个科学问题没有被否定；当前数据、更新器或运行环境还不足以做一次公平、能改变结论的实验。","The scientific question is not rejected; the current data, updater, or runtime cannot yet support a fair decision-changing test.");
    if(item.scientific_state==="MERGED") return mapPick("独立成篇的价值不足，但其中有用的方法、分析或约束已经并入更大的研究方向继续复用。","The standalone paper case is weak, but useful methods, analyses, or constraints have been absorbed into a larger research line.");
    if(/SIMPLE|MATCHED|EQUIVALENT|DOMINATES|CEILING|NO_HEADROOM/.test(code)) return mapPick("复杂方案没有超过拿到相同信息的更简单方法，因此不再作为独立研究方向继续投入。","A simpler method with the same information matched or beat the proposed mechanism, so the standalone line stops here.");
    if(layer==="problem_novelty") return mapPick("问题与最近工作或成熟理论高度重叠，目前没有留下足够独立的新科学问题。","The problem overlaps strongly with recent work or mature theory, leaving no sufficiently distinct scientific question.");
    if(layer==="experiment_identifiability") return mapPick("当前实验无法把目标机制和替代解释区分开，因此不能用结果支持这条主张。","The experiment cannot distinguish the target mechanism from alternative explanations, so it cannot support the claim.");
    if(layer==="operationalization") return mapPick("当前定义或测量方式没有真正测到想研究的变量，需要换一种可识别的实验定义。","The current operationalization does not actually isolate the intended variable and needs a different identifiable setup.");
    if(layer==="assumption_scope") return mapPick("关键比较前提不成立，当前两组结果并不是同一个可直接比较的科学对象。","A key comparison assumption fails, so the current observations are not the same scientific object under a fair comparison.");
    if(layer==="core_principle"||item.principle_dead_end_certified) return mapPick("关键预测已经被足够强的证据否定；除非出现能推翻它的新证据，否则不再重开。","The key prediction has been contradicted by sufficiently strong evidence and stays closed absent overturning evidence.");
    return mapPick("这一条已经形成明确停止结论；详细原因和证据保留在 ResearchItem 中。","This line has a clear stop decision; the detailed reason and evidence remain in its ResearchItem.");
  };
  const humanNext = item => {
    const specific={
      "A-3":"换一个能稳定产生有效更新的新底座，再重新冻结候选更新与验证集。",
      "B-2":"先收集足够多可重复的“删除一条记忆会改变结论”案例，再重新做准入实验。",
      "B-3":"换到能提供足够多独立、未见共检索组合的新数据环境，再测试记忆交互。",
      "E-1":"重新构造一张不同编辑确实会产生可排序效果的 paired-edit 表，再训练或比较编辑策略。",
      "G-1":"需要新的合格模型/运行环境，并先得到足够多当前都通过安全检查、又能公平匹配的持久状态。"
    };
    if(language==="zh"&&specific[item.code]) return specific[item.code];
    if(item.scientific_state==="HOLD") return mapPick("满足该 ResearchItem 写明的支持条件后再重新评审。","Reopen only after the ResearchItem's stated support condition is satisfied.");
    return "";
  };
  const HUMAN_EVIDENCE_ZH = {
    "A-1":"36 个 development unit 选审计 horizon，36 个 future_eval unit 冻结验证。h=1 只召回 2/5 个 nonzero effect（40%），成本 624/2813=22.2%；更简单的 target-family prior 以 613 steps 召回 3/5（60%）。因此只保留早期 branch signal 作为 soft-audit 排序，不再做独立方法。",
    "A-2":"开发集上的自适应 horizon 可召回 5/6（83.3%），但冻结 future_eval 只剩 2/5（40%）。固定 h=1 同样召回 2/5，却只花 22.2% 成本，严格优于所有自适应版本，因此 controller 不再继续。",
    "A-3":"当前 prompt-patch 底座的 8 个候选更新里只有 1 个带来正 target gain，有效候选比例 12.5%，低于预注册 40% 门。回归面板本身还没有在 fresh candidate × hidden original 上被公平检验，所以这是底座 HOLD，不是方法失败。",
    "A-4":"20 个未见 update identity 的 held-out triple 上，typed registry 与直接 order-aware risk + repair 都达到 prediction=1.0、repair=1.0，49 vs 49 次 candidate checks；复杂 registry 没有增加价值。",
    "A-5":"40 个顺序更新、12 个冻结 rollback query 上，semantic compactor 与通用 state-diff 都是 12/12 rollback fidelity；通用方法只需 38 storage cells，而 semantic 需要 73。相近存储预算的 periodic checkpoint 也 12/12。",
    "B-1":"真实 matched 实验中，cross-process invariance 与更简单的 utility-only 准入基本打平，hidden effect≈0.0139，因此不再独立成篇，保留为经验效用分析资产。",
    "B-2":"当前 72-unit memory 表只有 11 个 controlled-nonzero memory effect，而且专门的 conclusion-change deletion case 为 0，达不到预注册 ≥30 个可重复结论改变案例的前置门；hidden E_orig 没有打开。",
    "B-3":"synthetic screening 有 pathway signal，但严格排除旧 source/target 和重复 target 后，真实 fresh co-retrieval 场景只剩 5 个，低于冻结的 6-pair gate；因此停止当前 ALFWorld 实例，不判方法失败。",
    "B-5":"12/12 个 skill 上，monotone applicability repair 与 complexity-matched ILP 学到完全相同的 gate；两者 true-gate recovery 都是 10/12，连失败案例也一致，因此独立机制被简单 ILP 完整复现。",
    "B-6":"12 memories × 25 reuse opportunities、严格 20% audit budget 下，learned utility-hazard 在 future reuse 仍漏留 16 个 harmful memory；简单 recency≥4 且 frequency≤2 规则为 0 harmful retained、0 beneficial quarantine，且保留 benefit 相同。",
    "C-1":"已有 400 条 lineage-linked label 决策，确实观察到谱系相关性，但与同信息直接/简单 source-discount 规则的决策分歧只有 2.5%，没有留下足够方法 headroom。",
    "C-2":"3×3 actor/evaluator cross-score 中，跨版本归因与简单 anchor-residual 都 3/3 正确定位 evaluator drift；简单 intercept+shortcut calibration 与 causal neutralization 的修复结果逐项相同，而后者额外需要 54 次 intervention calls。",
    "C-4":"30 个失败、≤3 轮纠正的共享 F0 中，learned policy≈0.80，depth-3 CART≈0.767，决策分歧约 6.7%，没有达到独立方法所需的 headroom。",
    "C-5":"24 个 correction candidate 的共享 F0 中，同特征简单阈值准确率约 0.792，高于 learned gate 的 0.625；因此不再开方法 GPU run。",
    "D-1":"20 条规则 × 4 个 verifier-confirmed counterexample。1-minimal arm 额外做了 320 次 verifier call，但与直接取 verified counterexample constraint intersection 得到完全相同的 20 个更新；hidden boundary 都是 60/60。",
    "D-2":"跨版本 mutation ranking 有变化，但使用完全相同信息的 direct per-operator yield predictor 做出了相同的 held-out 决策，所以独立 curriculum-frontier selector 没有剩余价值。",
    "E-1":"16 个 workflow × 5 个 edit 的 frozen source table 中，只有 4/16 workflow 存在任何正 edit，只有 3 个 workflow 的 edit delta 能唯一排序，有效比例 25%。hidden workflow 未打开，因此这是当前 edit table 的支持失败，不是方法失败。",
    "E-2":"16 个 source workflow、4 类 failure motif 上，两种方法都用 32 次 source call；冻结后在 8 个 API/identity-disjoint hidden workflow 上，causal grammar 与直接 paired edit-effect reuse 都是 8/8 success、0 harmful rewrite，而且 8/8 选择完全相同。",
    "F-1":"decision-switch 选择与同数据 direct action-disagreement selector 在精确动力学表上完全等价；同时真实 continual-adaptation 场景还未完成独立确认，因此不再为 standalone 方法扩实验。",
    "F-2":"在 ≥40 个不可逆失败与 matched safe case 的有限状态测试里，容量匹配的直接 shield 能复现全部 hidden 决策；typed irreversibility clause 没有超出 generic shielding 的独立价值。",
    "F-3":"现象层要求先有至少 100 对 same-start normal/perturbed success、直接 residual Δs 和 success-only writer audit。当前该 exact-state phenomenon artifact 尚未满足；同数据 direct recovery policy 也能复现现有决策。",
    "G-1":"核心问题仍开放。当前 SecureClaw context 只在两个已知 failure probe 上恢复 headroom，但在预注册 fresh development panel 上不能泛化；还缺新的合格 backbone/runtime，以及足够多“当前都安全且可公平匹配”的冻结持久状态。"
  };
  const humanEvidence = item => {
    if(language==="zh"&&item.code==="E-7") {
      const paper=(paperForGroup("E").find(row=>row.source_research_item==="E-7")||{});
      return paper.submission_ready
        ? "STRI 的 3/3 条核心主张已有对应证据，论文证据债为 0；最新 PaperRegistry 已到 Submission Ready。科研实验线已闭环，当前工作转为正式投稿与后续审稿流程。"
        : "STRI 的 3/3 条核心主张已有对应证据，论文证据债为 0；科研实验线已闭环，当前工作已经转入 PaperRegistry 的论文质量与投稿流程。";
    }
    if(language==="zh"&&HUMAN_EVIDENCE_ZH[item.code]) return HUMAN_EVIDENCE_ZH[item.code];
    const raw=valueText(item.decision_reason);
    return compact(raw||humanDecision(item),420);
  };
  const researchField = (label,value,max=260) => value ? `<div class="rpm-research-field"><b>${label}</b><p>${esc(compact(value,max))}</p></div>` : "";
  const attentionCard = item => `<article class="rpm-attention-card state-${String(item.scientific_state||"").toLowerCase()}"><header><span>${esc(item.code||item.id||"--")}</span><div><b>${esc(valueText(item.title)||item.id||"--")}</b><em>${esc(stateLabel(item.scientific_state))}</em></div></header>${researchField(mapPick("研究问题","Research problem"),valueText(item.problem),300)}${researchField(mapPick("我们怎么做","Our approach"),valueText(item.mechanism)||valueText(item.method_logic),280)}${researchField(mapPick("最强对照","Strongest baseline"),valueText(item.strongest_baseline),260)}${researchField(mapPick("已经拿到的证据","Evidence so far"),humanEvidence(item),520)}${humanNext(item)?`<footer><b>${mapPick("下一步要满足：","Next condition: ")}</b>${esc(humanNext(item))}</footer>`:""}</article>`;
  const primaryLedger = (groupId,items) => `<div class="rpm-primary-ledger"><div class="rpm-subsection-title"><b>${mapPick("研究方向完整进展","Complete progress of research lines")}</b><span>${mapPick(`${items.length} 条可读研究方向全部列出；先看一句话结论，需要数字时再展开。`,`${items.length} reader-facing lines are all listed; scan the one-line decision first, then expand for methods and numbers.`)}</span></div>${items.map(item=>`<details class="rpm-primary-row"><summary><span>${esc(item.code||"--")}</span><b>${esc(valueText(item.title)||item.id||"--")}</b><em>${esc(stateLabel(item.scientific_state))}</em><small>${esc(humanDecision(item))}</small></summary><div class="rpm-primary-row-body">${researchField(mapPick("想解决什么","Problem"),valueText(item.problem),260)}${researchField(mapPick("核心做法","Approach"),valueText(item.mechanism)||valueText(item.method_logic),240)}${researchField(mapPick("最强简单/同信息对照","Strongest matched baseline"),valueText(item.strongest_baseline),240)}${researchField(mapPick("关键实验与当前结论","Evidence and current decision"),humanEvidence(item),520)}</div></details>`).join("")}</div>`;

  const externalPaperCard = paper => `<a class="rpm-external-paper" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><b>${esc(paper.short||paper.title)}</b><span>${esc(mapPick(paper.status_zh,paper.status_en))}</span></header><p><strong>${mapPick("它做到：","What it establishes: ")}</strong>${esc(mapPick(paper.advance_zh,paper.advance_en))}</p></a>`;
  const formalPaperCard = paper => `<a class="rpm-formal-category-paper" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><span>${esc(paper.year)} · ${esc(paper.venue)}</span><b>${esc(paper.short||paper.title)}</b></header><p><strong>${mapPick("推进到：","Advance: ")}</strong>${esc(mapPick(paper.advance_zh,paper.advance_en)||paper.title)}</p></a>`;
  const formalCategoryList = papers => {
    const years=[...new Set(papers.map(row=>Number(row.year)))].sort((a,b)=>b-a);
    return `<div class="rpm-formal-category-years">${years.map(year=>{const rows=papers.filter(row=>Number(row.year)===year);return `<section class="rpm-formal-category-year"><header><b>${year}</b><span>${rows.length} ${mapPick("篇","papers")}</span></header><div class="rpm-formal-category-list">${rows.map(formalPaperCard).join("")}</div></section>`;}).join("")}</div>`;
  };

  const graphIndex = () => {
    const g=evidenceGraph();
    return {nodes:new Map((g.nodes||[]).map(node=>[node.id,node])),edges:g.edges||[],overlay:scientificGraph().overlay_nodes||[]};
  };
  const nodeText = node => {
    if (!node) return "";
    if (node.title && typeof node.title === "object") return textOf(node.title);
    if (node.text && typeof node.text === "object") return textOf(node.text);
    if (node.label && typeof node.label === "object") return textOf(node.label);
    return String(node.title || node.text || node.label || node.key || node.id || "");
  };
  const projectionForGroup = groupId => {
    const {nodes,edges,overlay}=graphIndex(), trackKeys=new Set(GROUP_TRACKS[groupId]||[]);
    const ideas=[...nodes.values()].filter(node=>node.kind==="idea"&&trackKeys.has(node.track_id)).sort((a,b)=>(Number(a.rank)||999)-(Number(b.rank)||999));
    const ideaIds=new Set(ideas.map(node=>node.id)), relationEdges=edges.filter(edge=>ideaIds.has(edge.source));
    const rows=ideas.slice(0,4).map(idea=>{
      const problemEdge=relationEdges.find(edge=>edge.source===idea.id&&edge.relation==="states-problem"), problem=problemEdge?nodes.get(problemEdge.target):null;
      const nearest=relationEdges.filter(edge=>edge.source===idea.id&&edge.relation==="nearest-work").slice(0,3).map(edge=>nodes.get(edge.target)).filter(Boolean);
      const experiments=overlay.filter(node=>node.kind==="experiment"&&String(node.id||"").startsWith(`experiment:${idea.key}:`));
      return {idea,problem,nearest,experiments};
    });
    return {ideas,relationEdges,rows};
  };

  const lineageTable = group => {
    if(group.id==="G") {
      const safety=(groupItems("G").find(row=>row.code==="G-1")||{});
      return `<div class="rpm-lineage-table"><div class="rpm-lineage-row rpm-lineage-head"><span>${mapPick("研究问题","Research problem")}</span><span>${mapPick("为什么停在这里","Why it is here")}</span><span>${mapPick("下一次重开需要什么","What would reopen it")}</span></div><div class="rpm-lineage-row"><span><b>G-1 · ${esc(valueText(safety.title)||"Agent Safety")}</b></span><span>${esc(compact(valueText(safety.decision_reason),220))}</span><span>${esc(compact(valueText(safety.reopen_condition),200))}</span></div></div>`;
    }
    const projection=projectionForGroup(group.id);
    if(!projection.rows.length) return `<div class="rpm-lineage-empty">${mapPick("旧知识图谱里这一类还没有足够的历史关系；当前判断直接来自上面的 canonical ResearchItem。","The older knowledge graph has little historical structure here; the current decision comes directly from the canonical ResearchItems above.")}</div>`;
    return `<div class="rpm-lineage-table"><div class="rpm-lineage-row rpm-lineage-head"><span>${mapPick("历史研究问题","Historical problem")}</span><span>${mapPick("当时真正想解释什么","What it tried to explain")}</span><span>${mapPick("最近相关工作","Nearest work")}</span><span>${mapPick("实验记录","Experiment record")}</span></div>${projection.rows.map(row=>`<div class="rpm-lineage-row"><span><b>#${esc(row.idea.rank||"--")} · ${esc(compact(nodeText(row.idea),90))}</b></span><span>${esc(compact(nodeText(row.problem),150)||"—")}</span><span>${row.nearest.length?row.nearest.map(node=>`<i>${esc(compact(nodeText(node),70))}</i>`).join(""):"—"}</span><span>${row.experiments.length?mapPick(`${row.experiments.length} 条实验节点`,`${row.experiments.length} experiment node(s)`):mapPick("暂无独立实验节点","No separate experiment node")}</span></div>`).join("")}</div>`;
  };

  const categorySection = group => {
    const allItems=groupItems(group.id), readableItems=primaryItems(group.id), attention=attentionItems(group.id), inv=groupInventory(group.id), counts=groupStateCounts(group.id), formal=formalPapersForGroup(group.id), frontier=frontierPapersForGroup(group.id), insight=CATEGORY_BRIEFING_ZH[group.id]||{};
    const backgroundCount=Math.max(0,allItems.length-readableItems.length);
    const externalSummary=formal.length?mapPick(`正式发表 ${formal.length} 篇，按年份全部列出；另有 ${frontier.length} 篇 arXiv / preprint 作为前沿补充。`,`All ${formal.length} formal publications are listed by year, plus ${frontier.length} arXiv/preprint frontier papers.`):mapPick(`当前正式发表语料中还没有归入本类的论文；另有 ${frontier.length} 篇前沿预印本。`,`No formal paper in the current corpus maps here yet; ${frontier.length} frontier preprints remain.`);
    const attentionBlock=attention.length
      ? `<div class="rpm-subsection-title"><b>${mapPick("当前还需要继续处理的方向","Current lines that still need action")}</b><span>${mapPick("论文与 HOLD 方向在这里展开到问题、方法、对照、证据和下一步。","Paper/HOLD lines are expanded through problem, method, baseline, evidence, and next condition.")}</span></div><div class="rpm-attention-list">${attention.map(attentionCard).join("")}</div>`
      : `<div class="rpm-no-attention"><b>${mapPick("当前没有仍在推进或等待条件的主线","No main line is currently advancing or waiting on support")}</b><p>${mapPick("下面仍完整列出本类已经研究过的主要方向、最强对照和停止/合并证据，避免把“没有 active 项目”误读成“没有做过工作”。","The complete set of studied lines, baselines, and stop/merge evidence remains listed below so 'no active line' is not mistaken for 'little work done'.")}</p></div>`;
    return `<section class="rpm-category" id="research-map-${esc(group.id.toLowerCase())}" style="--group-color:${groupColor(group.id)}"><header class="rpm-category-header"><span>${esc(group.id)}</span><div><h3 id="research-map-${esc(group.id.toLowerCase())}-heading" data-toc-label="${esc(`${group.id} · ${textOf(group.title)}`)}">${textOf(group.title)}</h3><p>${textOf(group.question)}</p></div><div class="rpm-category-counts"><b>${inv.portfolio_total||0}</b><small>${mapPick("内部研究记录","internal records")}</small><b>${formal.length}</b><small>${mapPick("正式发表论文","formal papers")}</small><b>${frontier.length}</b><small>${mapPick("前沿预印本","frontier preprints")}</small></div></header><div class="rpm-category-headline"><b>${mapPick("一句话结论","ONE-LINE TAKEAWAY")}</b><p>${esc(categoryHeadline(group.id))}</p></div><div class="rpm-category-columns"><section class="rpm-ours"><div class="rpm-column-title"><b>${mapPick("我们做到哪里 · 完整主线摘要","Our progress · complete readable summary")}</b><span>${mapPick(`${readableItems.length} 条主阅读层研究方向全部列出 · ${backgroundCount} 条历史碰撞/关闭对象留在完整 ResearchItem 总账`,`${readableItems.length} reader-facing research lines listed · ${backgroundCount} historical collision/closure objects remain in the full ledger`)}</span></div><small class="rpm-state-scope-label">${mapPick(`全部 ${allItems.length} 个 ResearchItem 的当前状态`,`Current state of all ${allItems.length} ResearchItems`)}</small><div class="rpm-ours-state-strip"><span><b>${counts.PAPER_READY||0}</b>${mapPick("论文","paper")}</span><span><b>${counts.HOLD||0}</b>${mapPick("等待条件","hold")}</span><span><b>${counts.MERGED||0}</b>${mapPick("合并","merged")}</span><span><b>${counts.STOPPED||0}</b>${mapPick("停止","stopped")}</span></div><div class="rpm-ours-explanation"><div><b>${mapPick("这类问题我们总体学到了什么","What we learned overall")}</b><p>${esc(insight.reason||"具体以 ResearchItem 当前证据为准。")}</p></div><div><b>${mapPick("哪些资产仍继续复用","What still survives as assets")}</b><p>${esc(insight.survives||"保留仍有效的方法组件、基线和负证据。")}</p></div></div>${attentionBlock}${primaryLedger(group.id,readableItems)}<div class="rpm-ledger-note">${mapPick(`本栏不是抽样：除 ${backgroundCount} 条仅用于 provenance / collision memory 的历史关闭对象外，本类 ${readableItems.length} 条可读研究方向全部列在上面。完整 ${allItems.length} 个 ResearchItem 及实验记录继续以“研究组合”页为权威。`,`This is not a sample: except for ${backgroundCount} provenance/collision-memory closures, all ${readableItems.length} reader-facing lines are listed above. The full ${allItems.length}-item ledger remains authoritative on Research Portfolio.`)}</div><a class="link-btn" href="paper-ideas.html#canonical-group-${esc(group.id.toLowerCase())}">${mapPick(`查看 ${group.id} 类全部 ${allItems.length} 个 ResearchItem →`,`Open all ${allItems.length} category ${group.id} ResearchItems →`)}</a></section><section class="rpm-outside"><div class="rpm-column-title"><b>${mapPick("现有工作做到哪里 · 正式论文主视图","Where existing work stands · formal literature first")}</b><span>${esc(externalSummary)}</span></div>${formal.length?formalCategoryList(formal):`<div class="rpm-empty">${mapPick("暂无正式发表论文记录","No formal publication mapped yet")}</div>`}${frontier.length?`<details class="rpm-frontier-preprints"><summary><b>${mapPick("前沿补充：arXiv / preprint","Frontier supplement: arXiv / preprint")}</b><span>${frontier.length} ${mapPick("篇","papers")}</span></summary><div class="rpm-external-paper-list">${frontier.map(externalPaperCard).join("")}</div></details>`:""}</section></div><div class="rpm-lineage"><div class="rpm-column-title"><b>${mapPick("为什么会走到今天这个结论","Why the research path led here")}</b><span>${group.id==="G"?mapPick("用当前安全 ResearchItem 直接解释","explained directly from current safety ResearchItem"):mapPick("历史知识图谱只保留能解释选题与裁决的关系","the historical graph keeps only relations that explain topic choice and decisions")}</span></div>${lineageTable(group)}</div></section>`;
  };

  const graphTechnicalAppendix = () => {
    const sg=scientificGraph().summary||{}, kinds=sg.node_kinds||{}, relations=sg.relations||{};
    return `<details class="panel rpm-graph-schema"><summary><div><b>${mapPick("需要审计时再看：完整知识图谱技术结构","Optional audit: full knowledge-graph structure")}</b><span>${mapPick(`底层仍保留 ${sg.nodes||0} 个节点 / ${sg.edges||0} 条关系；主页面不再用它们占据主要阅读空间。`,`The underlying ${sg.nodes||0} nodes / ${sg.edges||0} relations remain available, but no longer dominate the main reading path.`)}</span></div><strong>${Object.keys(kinds).length} / ${Object.keys(relations).length}</strong></summary><div class="rpm-schema-grid"><section><b>${mapPick("节点类型","Node kinds")}</b><div>${Object.entries(kinds).sort((a,b)=>b[1]-a[1]).map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section><section><b>${mapPick("关系类型","Relations")}</b><div>${Object.entries(relations).sort((a,b)=>b[1]-a[1]).map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section></div></details>`;
  };

  window.renderCurrentResearchMap = function(config){
    const groups=mapGroups();
    const chapters=(window.PAGE_ARCHITECTURES?.["research-map"]?.chapters)||[];
    const layering=`${currentControlBoard()}${readingBridge()}${topStats(groups)}`;
    const coverage=coverageSummary(groups);
    const integrated=`${overviewIndex(groups)}<section class="rpm-map-intro"><div><b>${mapPick("先逐个读 A–G，再用正式论文时间线回看全局","Read A–G first, then use the formal-paper timeline to review the field")}</b><p>${mapPick("每个 A–G 先把我们的完整研究进展与现有正式工作放在一起比较；七个方向读完后，再用正式发表论文时间线回看整个领域怎样发展。arXiv / preprint 仍只作为各方向的前沿补充。","Each A–G section first compares our complete progress with formally published work. After all seven areas, the formal-publication timeline summarizes how the field developed; arXiv/preprints remain frontier supplements within each area.")}</p></div><a class="link-btn" href="research-directions.html">${mapPick("查看领域全景 →","Open field landscape →")}</a></section><section class="rpm-category-stack">${groups.map(categorySection).join("")}</section>${formalPublicationTimeline()}`;
    return `${pageHeader(config)}${renderArchitectureOverview(window.PAGE_ARCHITECTURES?.["research-map"])}${renderCustomChapter(chapters[0],0,layering)}${renderCustomChapter(chapters[1],1,coverage)}${renderCustomChapter(chapters[2],2,integrated)}${renderCustomChapter(chapters[3],3,graphTechnicalAppendix())}`;
  };
})();
