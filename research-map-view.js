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
  const representativeItems = groupId => {
    const items=[...groupItems(groupId)].sort((a,b)=>(SOURCE_ORDER[a.source_kind]??9)-(SOURCE_ORDER[b.source_kind]??9)||String(a.code||"").localeCompare(String(b.code||""),undefined,{numeric:true}));
    const picked=[];
    const add=row=>{if(row&&!picked.includes(row)&&picked.length<4)picked.push(row);};
    items.filter(row=>["PAPER_READY","HOLD"].includes(row.scientific_state)).forEach(add);
    add(items.find(row=>row.scientific_state==="STOPPED"&&row.source_kind==="parent")||items.find(row=>row.scientific_state==="STOPPED"));
    add(items.find(row=>row.scientific_state==="MERGED"));
    [...items].filter(row=>row.source_kind!=="shadow_closed").sort((a,b)=>(STATE_ORDER[a.scientific_state]??9)-(STATE_ORDER[b.scientific_state]??9)).forEach(add);
    if(picked.length<3) [...items].filter(row=>row.source_kind==="shadow_closed").forEach(add);
    return picked;
  };

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

  const formalPaperRow = paper => `<a class="rpm-formal-paper-row" href="${esc(paper.url)}" target="_blank" rel="noopener"><span class="rpm-formal-venue"><b>${esc(paper.year)}</b>${esc(paper.venue)}</span><div><b>${esc(paper.short||paper.title)}</b><p>${esc(mapPick(paper.advance_zh,paper.advance_en)||paper.title)}</p></div><span class="rpm-formal-groups">${(paper.groups||[]).map(id=>`<i style="--group-color:${groupColor(id)}">${esc(id)}</i>`).join("")}</span></a>`;

  const formalPublicationTimeline = () => {
    const papers=formalPublishedPapers(), years=[...new Set(papers.map(row=>Number(row.year)))].sort((a,b)=>a-b), venues=[...new Set(papers.map(row=>String(row.venue)))];
    return `<section class="panel rpm-formal-timeline" id="formal-publication-lineage"><div class="rpm-section-head"><div><div class="eyebrow">${mapPick("正式发表主线 · 非 arXiv","FORMALLY PUBLISHED LINEAGE · NON-ARXIV")}</div><h2 data-toc="false">${mapPick(`把 ${papers.length} 篇正式会议 / 期刊论文按年份排开，看这个领域怎样一步步形成`,`Follow ${papers.length} formally published conference/journal papers across time`)}</h2><p>${mapPick("这里优先收录已经进入正式会议或期刊 proceedings 的工作；同一论文如果同时有 arXiv，只保留正式版本。收录范围以本研究站的 Agent self-evolution / persistent adaptation 语料为边界，并补充近期漏收的 ICLR、ICML、ACL、EMNLP、NAACL、CVPR 等正式论文。","This section prioritizes formal conference/journal proceedings; when a paper also has an arXiv version, only the formal version is kept. Coverage follows this observatory's agent self-evolution/persistent-adaptation corpus plus recently verified formal publications.")}</p></div><div class="rpm-formal-summary"><span><b>${papers.length}</b>${mapPick("正式论文","formal papers")}</span><span><b>${venues.length}</b>${mapPick("venue / track","venues / tracks")}</span><span><b>${years.length}</b>${mapPick("发表年份","publication years")}</span></div></div><div class="rpm-formal-years">${years.map(year=>{const rows=papers.filter(row=>Number(row.year)===year);return `<details class="rpm-formal-year" open><summary><b>${year}</b><span>${rows.length} ${mapPick("篇正式论文","formal papers")}</span></summary><div class="rpm-formal-paper-list">${rows.map(formalPaperRow).join("")}</div></details>`;}).join("")}</div></section>`;
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
  const itemCard = item => `<article class="rpm-item-card state-${String(item.scientific_state||"").toLowerCase()}"><header><span>${esc(item.code||item.id||"--")}</span><b>${esc(valueText(item.title)||item.id||"--")}</b><em>${esc(stateLabel(item.scientific_state))}</em></header><p>${esc(humanDecision(item))}</p>${humanNext(item)?`<small><b>${mapPick("下一步：","Next: ")}</b>${esc(humanNext(item))}</small>`:""}</article>`;

  const externalPaperCard = paper => `<a class="rpm-external-paper" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><b>${esc(paper.short||paper.title)}</b><span>${esc(mapPick(paper.status_zh,paper.status_en))}</span></header><p><strong>${mapPick("它做到：","What it establishes: ")}</strong>${esc(mapPick(paper.advance_zh,paper.advance_en))}</p></a>`;
  const formalPaperCard = paper => `<a class="rpm-formal-category-paper" href="${esc(paper.url)}" target="_blank" rel="noopener"><header><span>${esc(paper.year)} · ${esc(paper.venue)}</span><b>${esc(paper.short||paper.title)}</b></header><p><strong>${mapPick("推进到：","Advance: ")}</strong>${esc(mapPick(paper.advance_zh,paper.advance_en)||paper.title)}</p></a>`;

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
    const items=representativeItems(group.id), allItems=groupItems(group.id), inv=groupInventory(group.id), counts=groupStateCounts(group.id), formal=formalPapersForGroup(group.id), frontier=frontierPapersForGroup(group.id), insight=CATEGORY_BRIEFING_ZH[group.id]||{};
    const externalSummary=formal.length?mapPick(`已收录 ${formal.length} 篇正式发表论文；按年份全部列出。另有 ${frontier.length} 篇前沿预印本作为补充。`,`Includes ${formal.length} formally published papers, all listed by year, plus ${frontier.length} frontier preprints.`):mapPick(`当前正式发表语料中还没有归入本类的论文；另有 ${frontier.length} 篇前沿预印本。`,`No formal paper in the current corpus maps here yet; ${frontier.length} frontier preprints remain.`);
    return `<section class="rpm-category" id="research-map-${esc(group.id.toLowerCase())}" style="--group-color:${groupColor(group.id)}"><header class="rpm-category-header"><span>${esc(group.id)}</span><div><h2 data-toc="false">${textOf(group.title)}</h2><p>${textOf(group.question)}</p></div><div class="rpm-category-counts"><b>${inv.portfolio_total||0}</b><small>${mapPick("内部研究记录","internal records")}</small><b>${formal.length}</b><small>${mapPick("正式发表论文","formal papers")}</small><b>${frontier.length}</b><small>${mapPick("前沿预印本","frontier preprints")}</small></div></header><div class="rpm-category-headline"><b>${mapPick("一句话结论","ONE-LINE TAKEAWAY")}</b><p>${esc(categoryHeadline(group.id))}</p></div><div class="rpm-category-columns"><section class="rpm-ours"><div class="rpm-column-title"><b>${mapPick("我们现在做到哪里","Where our work stands")}</b><span>${mapPick(`${counts.HOLD||0} 等待条件 · ${counts.PAPER_READY||0} 论文 · ${counts.MERGED||0} 合并 · ${counts.STOPPED||0} 停止`,`${counts.HOLD||0} hold · ${counts.PAPER_READY||0} paper · ${counts.MERGED||0} merged · ${counts.STOPPED||0} stopped`)}</span></div><div class="rpm-item-list">${items.map(itemCard).join("")}</div><div class="rpm-category-judgment"><div><b>${mapPick("为什么形成这个结论","Why this is the current conclusion")}</b><p>${esc(insight.reason||"具体以 ResearchItem 当前证据为准。")}</p></div><div><b>${mapPick("哪些东西仍值得留下","What remains useful")}</b><p>${esc(insight.survives||"保留仍有效的方法组件、基线和负证据。")}</p></div></div><a class="link-btn" href="paper-ideas.html#canonical-group-${esc(group.id.toLowerCase())}">${mapPick(`查看 ${group.id} 类全部 ${allItems.length} 个 ResearchItem →`,`Open all ${allItems.length} category ${group.id} ResearchItems →`)}</a></section><section class="rpm-outside"><div class="rpm-column-title"><b>${mapPick("别人已经做到哪里","Where neighboring work stands")}</b><span>${esc(externalSummary)}</span></div><div class="rpm-formal-category-list">${formal.map(formalPaperCard).join("") || `<div class="rpm-empty">${mapPick("暂无正式发表论文记录","No formal publication mapped yet")}</div>`}</div>${frontier.length?`<details class="rpm-frontier-preprints"><summary><b>${mapPick("前沿补充：arXiv / preprint","Frontier supplement: arXiv / preprint")}</b><span>${frontier.length} ${mapPick("篇","papers")}</span></summary><div class="rpm-external-paper-list">${frontier.map(externalPaperCard).join("")}</div></details>`:""}</section></div><div class="rpm-lineage"><div class="rpm-column-title"><b>${mapPick("为什么会走到今天这个结论","Why the research path led here")}</b><span>${group.id==="G"?mapPick("用当前安全 ResearchItem 直接解释","explained directly from current safety ResearchItem"):mapPick("把旧知识图谱压成可读表格，不再画低密度节点串","the older graph is compressed into a readable table instead of low-density node chains")}</span></div>${lineageTable(group)}</div></section>`;
  };

  const graphTechnicalAppendix = () => {
    const sg=scientificGraph().summary||{}, kinds=sg.node_kinds||{}, relations=sg.relations||{};
    return `<details class="panel rpm-graph-schema"><summary><div><b>${mapPick("需要审计时再看：完整知识图谱技术结构","Optional audit: full knowledge-graph structure")}</b><span>${mapPick(`底层仍保留 ${sg.nodes||0} 个节点 / ${sg.edges||0} 条关系；主页面不再用它们占据主要阅读空间。`,`The underlying ${sg.nodes||0} nodes / ${sg.edges||0} relations remain available, but no longer dominate the main reading path.`)}</span></div><strong>${Object.keys(kinds).length} / ${Object.keys(relations).length}</strong></summary><div class="rpm-schema-grid"><section><b>${mapPick("节点类型","Node kinds")}</b><div>${Object.entries(kinds).sort((a,b)=>b[1]-a[1]).map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section><section><b>${mapPick("关系类型","Relations")}</b><div>${Object.entries(relations).sort((a,b)=>b[1]-a[1]).map(([name,count])=>`<span><code>${esc(name)}</code><strong>${count}</strong></span>`).join("")}</div></section></div></details>`;
  };

  window.renderCurrentResearchMap = function(config){
    const groups=mapGroups();
    const chapters=(window.PAGE_ARCHITECTURES?.["research-map"]?.chapters)||[];
    const layering=`${readingBridge()}${topStats(groups)}`;
    const coverage=coverageSummary(groups);
    const integrated=`${formalPublicationTimeline()}${overviewIndex(groups)}<section class="rpm-map-intro"><div><b>${mapPick("颜色只表示 A–G 研究大类","Color only identifies the A–G category")}</b><p>${mapPick("正式发表论文优先完整展示；arXiv / preprint 只作为前沿补充。继续、停止、合并、等待条件和论文状态全部直接写成文字。","Formal publications are shown first and as completely as the current corpus allows; arXiv/preprints are frontier supplements. Research states are written explicitly in text.")}</p></div><a class="link-btn" href="research-directions.html">${mapPick("查看领域全景 →","Open field landscape →")}</a></section><section class="rpm-category-stack">${groups.map(categorySection).join("")}</section>`;
    return `${pageHeader(config)}${renderArchitectureOverview(window.PAGE_ARCHITECTURES?.["research-map"])}${renderCustomChapter(chapters[0],0,layering)}${renderCustomChapter(chapters[1],1,coverage)}${renderCustomChapter(chapters[2],2,integrated)}${renderCustomChapter(chapters[3],3,graphTechnicalAppendix())}`;
  };
})();
