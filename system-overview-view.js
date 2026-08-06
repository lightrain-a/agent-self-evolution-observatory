(() => {
  const get = (value, fallback = 0) => value === undefined || value === null ? fallback : value;
  const pick = (zh, en) => language === "zh" ? zh : en;
  const latestReview = (idea) => {
    const rows = idea?.external_reviews || [];
    return rows.length ? rows[rows.length - 1] : null;
  };
  const currentVerdict = (idea) => idea?.external_verdict || latestReview(idea)?.verdict || "pending";
  const titleOf = (idea) => textOf(idea?.title || idea?.name || "");
  const ideaHref = (idea) => idea?.final_status ? "paper-ideas.html#machine-school-inspired-ideas" : `paper-ideas.html#iclr-${esc(idea?.id || "low-resource-bank")}`;
  const reviewAction = (idea, review) => window.localizedReviewAction ? window.localizedReviewAction(idea?.id || "", review, language) : (review?.required_action || "");

  function stat(value, zh, en, tone = "") {
    return `<div class="system-stat ${tone}"><b>${esc(value)}</b><span>${pick(zh,en)}</span></div>`;
  }

  function layerCard(index, tag, zhTitle, enTitle, zhBody, enBody, examples = []) {
    return `<article class="system-layer"><header><span>${String(index).padStart(2,"0")}</span><small>${esc(tag)}</small></header><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4><p>${pick(zhBody,enBody)}</p>${examples.length ? `<div class="system-layer-chips">${examples.map((item) => `<span>${esc(item)}</span>`).join("")}</div>` : ""}</article>`;
  }

  function pipelineStage(index, tag, zhTitle, enTitle, zhInput, enInput, zhProcess, enProcess, zhOutput, enOutput) {
    return `<article class="system-stage"><div class="system-stage-head"><div class="system-stage-index">${String(index).padStart(2,"0")}</div><div><span>${esc(tag)}</span><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4></div></div><dl><div><dt>${pick("输入","Input")}</dt><dd>${pick(zhInput,enInput)}</dd></div><div><dt>${pick("处理","Process")}</dt><dd>${pick(zhProcess,enProcess)}</dd></div><div><dt>${pick("输出","Output")}</dt><dd>${pick(zhOutput,enOutput)}</dd></div></dl></article>`;
  }

  function artifactRow(name, visibility, zhPurpose, enPurpose, zhProducer, enProducer) {
    return `<tr><td><code>${esc(name)}</code></td><td><span class="system-visibility ${esc(visibility)}">${visibility === "public" ? pick("公开快照","Public snapshot") : pick("仅后台","Backend only")}</span></td><td>${pick(zhPurpose,enPurpose)}</td><td>${pick(zhProducer,enProducer)}</td></tr>`;
  }

  function boundaryCard(tone, zhTitle, enTitle, items) {
    return `<article class="system-boundary-card ${tone}"><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4><ul>${items.map(([zh,en]) => `<li>${pick(zh,en)}</li>`).join("")}</ul></article>`;
  }

  function ideaCard(idea) {
    const verdict = currentVerdict(idea);
    const review = latestReview(idea);
    const status = idea?.final_status || (verdict === "pass" ? "experiment-pending" : verdict);
    const action = reviewAction(idea, review);
    return `<a class="system-idea-card verdict-${esc(verdict)}" href="${ideaHref(idea)}"><header><span>${esc(String(verdict).toUpperCase())}</span><small>${esc(status)}</small></header><h4 data-toc="false">${esc(titleOf(idea))}</h4><p>${esc(textOf(idea?.purpose || idea?.problem || ""))}</p>${action ? `<div class="system-idea-action"><b>${pick("审查后要求","Required revision")}</b>${esc(action)}</div>` : ""}</a>`;
  }

  function verdictGroup(titleZh, titleEn, ideas, emptyZh, emptyEn) {
    return `<section class="system-idea-group"><h4 data-toc="false">${pick(titleZh,titleEn)}<span>${ideas.length}</span></h4>${ideas.length ? `<div class="system-idea-grid">${ideas.map(ideaCard).join("")}</div>` : `<p class="empty">${pick(emptyZh,emptyEn)}</p>`}</section>`;
  }

  function renderLiveArchitecture(state, s2) {
    const summary = state.summary || {};
    const stats = s2.statistics || {};
    const pilot = state.pilot_registry?.summary || {};
    const routeCounts = stats.route_counts || {};
    const routeLabels = {
      seed:["种子论文","Seed papers"], topic:["同题工作","Direct topic"], failure:["失败模式","Failure modes"],
      mechanism:["机制迁移","Mechanisms"], analogy:["跨域类比","Cross-domain analogy"], citation:["引用扩展","Citations"], reference:["参考文献扩展","References"]
    };
    const routes = Object.entries(routeCounts).sort((a,b)=>b[1]-a[1]).map(([key,value]) => `<div><b>${value}</b><span>${pick(routeLabels[key]?.[0] || key,routeLabels[key]?.[1] || key)}</span></div>`).join("");
    return `<section class="system-live-summary system-section"><h3>${pick("当前运行快照","Current runtime snapshot")}</h3><p class="section-intro">${pick("统计值直接读取后端发布的研究状态与文献快照，不在页面中手工维护。","The values below are read from backend-published research and literature snapshots rather than maintained manually in the page.")}</p><div class="system-stat-grid">
      ${stat(get(summary.papers,stats.paper_count),"篇去重论文","deduplicated papers")}
      ${stat(get(summary.queries,stats.query_count),"个规划检索查询","planned queries")}
      ${stat(get(summary.evidence_nodes),"个证据节点","evidence nodes")}
      ${stat(get(summary.evidence_edges),"条证据关系","evidence edges")}
      ${stat(get(state.collision_engine?.summary?.pairwise_comparisons,406),"组 Idea 两两比较","idea-pair checks")}
      ${stat(get(summary.collision_flags),"个碰撞标记","collision flags")}
      ${stat(get(pilot.phases),"个 P0/P1/P2 阶段","P0/P1/P2 phases")}
      ${stat(get(summary.pilot_results),"个已回流实验结果","ingested pilot results",get(summary.pilot_results)?"good":"warn")}
    </div></section>
    <section class="system-architecture system-section"><h3>${pick("后台分层架构","Backend layered architecture")}</h3><p class="section-intro">${pick("各层通过明确的静态工件连接。上一层失败时不会覆盖上一份有效快照，前端始终只读取最后一次通过校验的结果。","Layers communicate through explicit artifacts. A failed layer never overwrites the previous valid snapshot, and the frontend reads only the latest validated result.")}</p><div class="system-layer-grid">
      ${layerCard(1,"INGEST","文献与外部证据层","Literature and external evidence","负责检索、缓存、来源核对和版本归并。","Retrieval, caching, source verification, and version resolution.",["Semantic Scholar","OpenReview","Proceedings","Author repos"])}
      ${layerCard(2,"NORMALIZE","结构化语料层","Structured corpus","把论文转成统一字段，并保留 unknown 和字段级来源。","Converts papers into a common schema while preserving unknowns and provenance.",["paper cards","model/API audit","compute audit"])}
      ${layerCard(3,"EVIDENCE","证据与关系层","Evidence and relation layer","连接论文、问题、机制、数据集、模型、实验和候选 Idea。","Connects papers, problems, mechanisms, datasets, models, experiments, and ideas.",["evidence graph","collision graph","lineage graph"])}
      ${layerCard(4,"SYNTHESIZE","Idea 合成与修订层","Idea synthesis and repair","先用 8 个算子发现问题，再用 6 个 solution-first 算子检索机制、生成方法分支并根据 Reviewer／实验反馈修订。","Uses eight operators to discover problems, then six solution-first operators for mechanism retrieval, method branching, and reviewer/experiment-driven repair.",["14 operators","method tree","repair queue","branch history"])}
      ${layerCard(5,"REVIEW","审查编排层","Review orchestration","执行 R1、碰撞审计和 R2 外部审查，结果逐批原子保存。","Runs R1, collision audit, and R2 external review with atomic batch persistence.",["R1 gates","Oracle/web GPT","PASS/REVISE/BLOCK"])}
      ${layerCard(6,"EXPERIMENT","实验注册与结果层","Experiment registry and feedback","生成 P0/P1/P2 协议，接收合法结果并更新 Idea 状态。","Creates P0/P1/P2 protocols, accepts valid results, and updates idea state.",["Pilot Registry","result schema","Go/Stop"])}
      ${layerCard(7,"PUBLISH","快照与展示层","Snapshot and presentation","把公开字段编译成静态 JSON/JS；后台代码、密钥和运行数据不进入前端。","Compiles public fields into static JSON/JS; backend code, secrets, and run data stay private.",["generated/*.json","generated/*.js","frontend-only _site"])}
    </div></section>
    <section class="system-source-grid system-section"><section><h4 data-toc="false">${pick("文献从哪里来","Where literature comes from")}</h4><p>${pick("Semantic Scholar Academic Graph 提供高召回元数据；正式结论回到论文 PDF、OpenReview、会议论文集、官方项目页和作者仓库。查询不只搜同题论文，也主动搜失败模式、机制、跨域类比和引用邻域。","Semantic Scholar Academic Graph provides high-recall metadata. Final judgments return to paper PDFs, OpenReview, proceedings, official project pages, and author repositories. Retrieval also targets failures, mechanisms, analogies, and citation neighborhoods.")}</p><div class="system-route-grid">${routes}</div></section><section><h4 data-toc="false">${pick("每篇论文抽取的字段","Fields extracted per paper")}</h4><div class="system-field-list"><span>${pick("问题与动机","Problem and motivation")}</span><span>${pick("已有局限","Prior limitations")}</span><span>${pick("核心直觉","Core intuition")}</span><span>${pick("方法机制","Mechanism")}</span><span>${pick("成立假设","Assumptions")}</span><span>${pick("失效边界","Failure boundary")}</span><span>${pick("模型与 API","Models and APIs")}</span><span>${pick("更新对象与训练方式","Update surface and training")}</span><span>${pick("数据集与环境","Datasets and environments")}</span><span>${pick("硬件与成本","Hardware and cost")}</span><span>${pick("代码状态","Code availability")}</span><span>${pick("事实／推断／未知","Fact / inference / unknown")}</span></div></section></section>`;
  }

  function renderDetailedFlow() {
    return `${renderPipelineStages()}${renderDataContracts()}`;
  }

  function renderPipelineStages() {
    return `<section class="system-pipeline-panel system-section"><h3>${pick("详细后台数据流","Detailed backend data flow")}</h3><div class="system-pipeline">
      ${pipelineStage(1,"SCOPE","研究范围注册","Register research scope","会议、研究问题、资源与时间截止","Venue, research question, resources, cutoff","生成版本化范围配置和纳入／排除规则","Create versioned scope and inclusion/exclusion rules","查询约束、审查口径和资源政策","Query constraints, review contract, resource policy")}
      ${pipelineStage(2,"QUERY","规划检索路径","Plan retrieval routes","范围配置、种子论文、图谱空白","Scope, seeds, graph gaps","生成主题、失败、机制、类比、引用与参考文献查询","Generate topic, failure, mechanism, analogy, citation, and reference queries","带目的、优先级和路由类型的查询队列","Query queue with purpose, priority, and route")}
      ${pipelineStage(3,"CORPUS","获取、缓存与去重","Retrieve, cache, and deduplicate","API 返回、论文页、项目页和仓库","API results, paper pages, project pages, repositories","按 DOI／标题／作者／正式版本归并，保留来源状态","Resolve by DOI/title/authors/publication version and retain source state","去重语料、缓存和版本映射","Deduplicated corpus, cache, and version map")}
      ${pipelineStage(4,"PAPER","结构化论文记录","Structure paper records","论文正文、附录和官方说明","Paper text, appendices, official documentation","抽取问题—机制—假设—实验—资源—边界","Extract problem-mechanism-assumption-experiment-resource-boundary","可排序、可检索、可追溯的论文卡","Sortable, searchable, traceable paper cards")}
      ${pipelineStage(5,"GRAPH","构建证据图谱","Build evidence graph","论文卡、查询、机制词表和资产表","Paper cards, queries, mechanism vocabulary, asset registry","连接支持、冲突、使用、评测和派生关系","Link support, conflict, usage, evaluation, and derivation","证据节点、关系边和覆盖缺口","Evidence nodes, relation edges, coverage gaps")}
      ${pipelineStage(6,"IDEA","问题发现与解决方案分支搜索","Problem discovery and solution-branch search","问题胶囊、独立机制灵感、概念桥接路径、Reviewer 低分维度和历史实验反馈","Problem capsules, independent mechanism inspirations, concept paths, low reviewer dimensions, and experiment history","先生成问题，再为每个问题产生至少三个机制不同的子节点；明确变化假设、更新表面、学习信号、独立真值和算法规则，并做 Pareto 剪枝","Generate problems first, then at least three mechanism-distinct children per problem; specify changed assumption, update surface, learning signal, independent truth, and algorithm before Pareto pruning","包含方法树、父子谱系、公开资产、Baseline、Pilot 和 Stop 的候选子节点","Method-tree children with lineage, public assets, baseline, pilot, and Stop rule")}
      ${pipelineStage(7,"R1","内部结构化审查","Run internal structured review","候选 Idea 和会议／资源政策","Candidate ideas and venue/resource policy","检查持续学习真实性、更新表面、归因、稳定性、迁移、反馈和预算","Check persistent learning, update surface, credit, stability, transfer, feedback, and budget","R1 排名、通过／修改／阻断及审查理由","R1 rank, pass/revise/block, and reasons")}
      ${pipelineStage(8,"COLLISION","机制级碰撞审计","Audit mechanism-level collisions","R1 候选、最新论文和证据关系","R1 candidates, latest papers, evidence relations","分别检查问题、机制、组合和决定性实验碰撞","Check problem, mechanism, combination, and decisive-experiment collisions","碰撞标记、最近工作和 repair queue","Collision flags, nearest work, and repair queue")}
      ${pipelineStage(9,"R2","独立外部审查","Run independent external review","完整 Idea dossier 和正式来源约束","Complete idea dossier and official-source contract","Oracle 在指定 Agent 项目调用网页版模型，逐批检索与审查","Oracle invokes the signed-in Agent-project web model for batched search and review","PASS／REVISE／BLOCK、修改要求和原始响应","PASS/REVISE/BLOCK, required action, raw response")}
      ${pipelineStage(10,"PILOT","实验注册与结果回流","Register experiments and ingest results","冻结 Idea、P0/P1/P2 协议和结果 schema","Frozen idea, P0/P1/P2 protocol, result schema","验证结果完整性、预算、seed、对照和 Stop 规则","Validate completeness, budget, seeds, controls, and Stop rule","Idea 状态变化、失败记录和下一轮修订输入","Idea state transition, failure record, next repair input")}
    </div></section>`;
  }

  function renderDataContracts() {
    const rows = [
      ["S0",pick("范围注册","Scope registry"),pick("会议、截止日期、研究对象、资源上限","Venue, cutoff, target object, resource cap"),pick("版本化 scope 与纳入／排除规则","Versioned scope and inclusion/exclusion rules"),pick("变更必须人工确认；旧配置可回滚","Human-approved changes; old versions remain recoverable")],
      ["S1",pick("查询规划","Query planning"),pick("scope、种子论文、证据缺口","Scope, seeds, evidence gaps"),pick("带目的和优先级的多路查询队列","Multi-route query queue with purpose and priority"),pick("记录检索路由，失败查询可重试","Persist route logs; failed queries are retryable")],
      ["S2",pick("语料规范化","Corpus normalization"),pick("API 元数据与正式来源","API metadata and official sources"),pick("去重论文与版本映射","Deduplicated papers and version mapping"),pick("unknown 不猜测；缓存可重建","Unknowns stay explicit; cache is rebuildable")],
      ["S3",pick("论文结构化","Paper structuring"),pick("正文、附录、项目文档","Text, appendix, project docs"),pick("问题、机制、假设、实验、资源、边界","Problem, mechanism, assumptions, experiments, resources, boundary"),pick("字段级来源与事实／推断标记","Field-level provenance and fact/inference labels")],
      ["S4",pick("证据图谱","Evidence graph"),pick("论文卡、查询、资产与机制词表","Paper cards, queries, assets, mechanism vocabulary"),pick("支持、冲突、使用、评测、派生关系","Support, conflict, use, evaluation, derivation relations"),pick("低覆盖字段触发补检索，不覆盖有效图谱","Sparse coverage triggers retrieval without overwriting valid graph")],
      ["S5",pick("Idea 合成","Idea synthesis"),pick("局限、矛盾、空白单元、跨域机制","Limitations, contradictions, missing cells, analog mechanisms"),pick("结构完整的候选与谱系边","Structured candidates and lineage edges"),pick("缺少假设、Baseline、Pilot 或 Stop 即不入库","Reject candidates missing hypothesis, baseline, pilot, or Stop")],
      ["S6",pick("R1 审查","R1 review"),pick("候选 Idea 与资源政策","Candidate ideas and resource policy"),pick("七维通过／修改／阻断与冻结排名","Seven-gate verdict and frozen rank"),pick("保留原始审查轨迹，后续排序不篡改 R1","Preserve the original trace and R1 rank")],
      ["S7",pick("碰撞审计","Collision audit"),pick("Idea 对、证据图、最新论文","Idea pairs, evidence graph, latest papers"),pick("问题／机制／组合／实验碰撞与 repair queue","Four collision types and repair queue"),pick("标题相似不能单独构成碰撞结论","Title similarity alone is insufficient")],
      ["S8",pick("R2 外审","R2 external review"),pick("R1 通过项和正式来源审查合同","R1 passes and official-source review contract"),pick("PASS／REVISE／BLOCK、最近工作、required action","Verdict, nearest work, and required action"),pick("逐批原子保存；临时错误重试但不伪造","Atomic batch persistence; retry without fabrication")],
      ["S9",pick("实验回流","Experiment feedback"),pick("冻结协议与结构化结果文件","Frozen protocol and structured result files"),pick("planned／pilot-ready／selected-ready／stop","State transition"),pick("结果不完整或预算不匹配时拒绝晋级","Reject promotion if results or budgets are invalid")],
    ];
    return `<section class="system-contract-panel system-section"><h3>${pick("阶段数据合同","Stage data contracts")}</h3><p class="section-intro">${pick("每个阶段只消费上一阶段通过校验的结构化输出；原始模型文本不能直接改变最终 Idea 状态。","Each stage consumes validated structured output from the previous stage; raw model text cannot directly change final idea state.")}</p><div class="history-table-scroll"><table class="matrix system-contract-table"><thead><tr><th>ID</th><th>${pick("阶段","Stage")}</th><th>${pick("主要输入","Primary input")}</th><th>${pick("结构化输出","Structured output")}</th><th>${pick("持久化与失败策略","Persistence and failure policy")}</th></tr></thead><tbody>${rows.map((row)=>`<tr>${row.map((cell,index)=>`<${index===0?"th":"td"}>${cell}</${index===0?"th":"td"}>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
  }

  function renderArtifactsAutomation(state) {
    return `${renderArtifacts()}${renderAutomationBoundary(state)}${renderComponents(state)}`;
  }

  function renderArtifacts() {
    return `<section class="system-artifact-panel system-section"><h3>${pick("持久化工件与前后端边界","Persistent artifacts and frontend/backend boundary")}</h3><p class="section-intro">${pick("后台生成完整研究状态，再只把允许公开的静态快照编译到 Pages。原始响应、缓存、实验数据、密钥和执行代码不进入前端。","The backend builds the full research state, then compiles only approved static snapshots into Pages. Raw responses, caches, experiments, secrets, and execution code stay off the frontend.")}</p><div class="history-table-scroll"><table class="matrix system-artifact-table"><thead><tr><th>${pick("工件","Artifact")}</th><th>${pick("可见性","Visibility")}</th><th>${pick("用途","Purpose")}</th><th>${pick("生成者","Producer")}</th></tr></thead><tbody>
      ${artifactRow("generated/s2-literature.js","public","文献统计和前端可检索论文快照","Literature statistics and searchable frontend corpus","文献同步与规范化任务","Literature synchronization and normalization")}
      ${artifactRow("generated/research-system-state.json/js","public","系统健康、证据规模、碰撞、谱系和 Pilot 摘要","System health, evidence scale, collisions, lineage, and pilot summary","每日确定性重建","Daily deterministic rebuild")}
      ${artifactRow("generated/iclr-low-resource-ideas.json/js","public","主 Idea Bank、R1/R2 排名和实验协议","Main idea bank, R1/R2 ranks, and experiment protocols","Idea factory 与 review merge","Idea factory and review merge")}
      ${artifactRow("generated/iclr-external-reviews.json","public","26 个 R1 通过项的持久外部审查记录","Persistent external reviews for the 26 R1 passes","Oracle/web-GPT batch reviewer","Oracle/web-GPT batch reviewer")}
      ${artifactRow("generated/machine-school-inspired-ideas.json/js","public","补充候选、内部筛查和最终决策状态","Supplementary candidates, internal screen, and final decision state","Inspired idea factory","Inspired idea factory")}
      ${artifactRow("runs/reviews/**","backend","每批提示词、原始响应、失败和重试证据","Batch prompts, raw responses, failures, and retries","权威主机上的 review runner","Review runner on the authoritative host")}
      ${artifactRow("runs/pilots/**","backend","实验输出、日志、seed、预算和结果文件","Experiment outputs, logs, seeds, budgets, and result files","人工或沙箱实验执行","Manual or sandboxed experiment execution")}
      ${artifactRow("cache/** and raw PDFs","backend","可重建缓存和原始材料，不进入 Pages","Rebuildable caches and raw sources, excluded from Pages","Provider 和 acquisition jobs","Provider and acquisition jobs")}
    </tbody></table></div></section>`;
  }

  function renderAutomationBoundary(state) {
    const components = state.components || [];
    const running = components.filter((item) => item.status === "running").length;
    const automation = state.automation || {};
    const daily = automation.daily?.schedule || "02:15 server local time";
    const weekly = automation.weekly?.schedule || "Monday 03:15 server local time";
    return `<section class="system-automation-panel system-section"><h3>${pick("自动化边界与运行节奏","Automation boundary and operating cadence")}</h3><p class="section-intro">${pick(`当前 ${running} 个核心组件处于 running。每日任务：${daily}；每周任务：${weekly}。下面明确区分自动执行、条件自动和人工控制，避免把“自动生成”误解为“自动确认论文成立”。`,`${running} core components are running. Daily cadence: ${daily}; weekly cadence: ${weekly}. The categories below separate automatic execution, conditional automation, and human control.`)}</p><div class="system-boundary-grid">
      ${boundaryCard("auto","自动执行","Automatically executed",[["离线重建证据图、碰撞图、Idea 谱系和 Pilot Registry。","Offline rebuild of evidence, collision, lineage, and pilot registries."],["按 schema 校验后原子写入 JSON/JS 快照。","Validate schemas and atomically write JSON/JS snapshots."],["文献去重、查询缺口发现、R1 程序化检查和排序。","Deduplication, query-gap discovery, R1 checks, and ranking."],["上一轮有效工件在部分失败时继续保留。","Preserve the previous valid artifact after partial failure."]])}
      ${boundaryCard("conditional","条件自动","Conditionally automated",[["每周联网更新文献；网络或 Provider 失败时保留旧语料。","Weekly online literature refresh; provider failure preserves the old corpus."],["R2 仅在权威主机、已登录浏览器和正确 Agent 项目可用时运行。","R2 runs only on the authoritative host with a signed-in browser and exact Agent project."],["外部审查逐批保存；临时错误自动重试，但缺失结果不会被视为通过。","External reviews persist per batch; transient failures retry, but missing results never count as passes."],["Pages 只发布 frontend-only 静态快照；后台代码、密钥、缓存和运行目录不上传。","Pages publishes frontend-only snapshots; backend code, secrets, caches, and run directories are excluded."],["结构化实验结果通过完整性、预算和对照检查后才能回流。","Experiment results enter the system only after completeness, budget, and control checks."]])}
      ${boundaryCard("human","人工控制","Human-controlled",[["研究范围、会议目标、时间截止和资源上限。","Research scope, target venue, cutoff date, and resource cap."],["最终选题、论文主张、贡献边界和方向合并。","Final topic, paper claims, contribution boundary, and idea merging."],["正式实验代码、危险操作、服务器资源分配和预算扩展。","Formal experiment code, risky operations, server allocation, and budget expansion."],["对负结果、异常结果和 Stop 条件的科学解释。","Scientific interpretation of negative or anomalous results and Stop rules."],["没有 P0/P1/P2 证据时，不允许把 Idea 标记为 selected-ready。","No idea becomes selected-ready without P0/P1/P2 evidence."]])}
    </div><div class="system-fail-safe"><b>${pick("失败恢复原则","Failure-recovery policy")}</b><span>${pick("使用排他锁、schema 校验和原子写入；部分失败保留上一份有效公开工件，联网审查失败不会生成伪结果。","Use exclusive locks, schema validation, and atomic writes; partial failures preserve the previous valid public artifact, and failed online review never creates fabricated results.")}</span></div></section>`;
  }

  function renderComponents(state) {
    const components = state.components || [];
    const statusLabel = (value) => ({running:pick("运行中","running"),"intentionally-disabled":pick("有意禁用","intentionally disabled")}[value] || value || pick("未知","unknown"));
    const rows = components.map((item) => `<tr><td>${esc(textOf(item.component || item.name || pick("未知组件","Unknown component")))}</td><td>${esc(item.source || "-")}</td><td><span class="system-status ${esc(item.status || "unknown")}">${esc(statusLabel(item.status))}</span></td><td>${esc(textOf(item.evidence || item.detail || item.description || "-"))}</td></tr>`).join("");
    return `<section class="system-components-panel system-section"><h3>${pick("当前后台组件","Current backend components")}</h3><div class="history-table-scroll"><table class="matrix"><thead><tr><th>${pick("组件","Component")}</th><th>${pick("设计来源","Design source")}</th><th>${pick("状态","Status")}</th><th>${pick("当前证据","Current evidence")}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }

  function graphNodeLabel(node) {
    if (!node) return "";
    if (node.kind === "claim") return textOf(node.text || node.title || node.key || node.id);
    return textOf(node.title || node.text || node.key || node.id);
  }

  function renderEvidenceGraphPanel(state) {
    const graph = state.evidence_graph || {nodes:[],edges:[],summary:{}};
    const ideas = (graph.nodes || []).filter((node) => node.kind === "idea").sort((a,b) => Number(a.rank || 999) - Number(b.rank || 999));
    const summary = graph.summary || {};
    return `<section class="system-evidence-explorer system-section"><div class="system-evidence-head"><div><h3>${pick("引文与证据图谱","Citation and evidence graph")}</h3><p class="section-intro">${pick("选择一个 Idea，查看它与问题、机制、假设、最近论文、语义证据、数据集、模型、任务域和机制轨道之间的真实关系。图中只抽取当前 Idea 的局部邻域，避免把 555 个节点全部摊开后失去可读性。","Select an idea to inspect its real links to problem, mechanism, hypothesis, nearest papers, semantic evidence, datasets, models, domains, and mechanism track. The view samples a local neighborhood instead of rendering all nodes at once.")}</p></div><div class="system-evidence-counts"><span><b>${get(summary.nodes)}</b>${pick("节点","nodes")}</span><span><b>${get(summary.edges)}</b>${pick("关系","edges")}</span></div></div><div class="system-evidence-toolbar"><label>${pick("中心 Idea","Center idea")}<select id="system-evidence-idea">${ideas.map((idea) => `<option value="${esc(idea.id)}" ${idea.key === "regression-gated-self-evolution" ? "selected" : ""}>${esc(graphNodeLabel(idea))}</option>`).join("")}</select></label><div class="system-evidence-legend"><span data-kind="idea">Idea</span><span data-kind="claim">${pick("问题／机制／假设","Problem / mechanism / hypothesis")}</span><span data-kind="paper">${pick("论文证据","Paper evidence")}</span><span data-kind="asset">${pick("模型／数据／任务域","Model / data / domain")}</span><span data-kind="track">${pick("机制轨道","Track")}</span></div></div><div class="system-evidence-layout"><div class="system-evidence-canvas"><svg id="system-evidence-svg" viewBox="0 0 1200 660" role="img" aria-label="${pick("Idea 局部证据图","Local idea evidence graph")}"></svg></div><aside id="system-evidence-detail" class="system-evidence-detail"><h4 data-toc="false">${pick("节点详情","Node detail")}</h4><p>${pick("点击图中的节点查看字段、来源和关系。","Select a node to inspect its fields, provenance, and relations.")}</p></aside></div></section>`;
  }

  function bindEvidenceGraphExplorer() {
    const svg = document.getElementById("system-evidence-svg");
    const select = document.getElementById("system-evidence-idea");
    const detail = document.getElementById("system-evidence-detail");
    const graph = window.RESEARCH_SYSTEM_STATE?.evidence_graph;
    if (!svg || !select || !detail || !graph) return;
    const ns = "http://www.w3.org/2000/svg";
    const nodes = new Map((graph.nodes || []).map((node) => [node.id,node]));
    const allEdges = graph.edges || [];
    const relationZh = {"states-problem":"提出问题","uses-mechanism":"使用机制","tests-hypothesis":"检验假设","nearest-work":"最近工作","semantic-evidence":"语义证据","evaluates-on":"评测于","covers-domain":"覆盖任务域","uses-model":"使用模型","belongs-to":"属于轨道","citation":"引用","reference":"参考文献"};
    const relationLabel = (value) => language === "zh" ? (relationZh[value] || value) : value;
    const truncate = (value, max=28) => String(value || "").length > max ? `${String(value).slice(0,max-1)}…` : String(value || "");
    const kindGroup = (node) => node?.kind === "idea" ? "idea" : node?.kind === "claim" ? "claim" : ["paper","paper-alias"].includes(node?.kind) ? "paper" : node?.kind === "track" ? "track" : "asset";
    const nodeDetail = (node, incident) => {
      const label = graphNodeLabel(node);
      const metadata = [];
      if (node.kind === "claim") metadata.push([pick("字段","Field"), node.field || "-"]);
      if (node.year) metadata.push([pick("年份","Year"), node.year]);
      if (node.venue) metadata.push([pick("发表位置","Venue"), node.venue]);
      if (node.citation_count !== undefined) metadata.push([pick("引用量","Citations"), node.citation_count]);
      if (node.operator) metadata.push([pick("生成算子","Operator"), node.operator]);
      if (node.status) metadata.push([pick("状态","Status"), node.status]);
      const rows = incident.map((edge) => `<li><b>${esc(relationLabel(edge.relation))}</b> · ${esc(graphNodeLabel(nodes.get(edge.source === node.id ? edge.target : edge.source)))}</li>`).join("");
      detail.innerHTML = `<h4 data-toc="false">${esc(label)}</h4><span class="system-evidence-kind">${esc(node.kind)}</span>${metadata.length ? `<dl>${metadata.map(([key,value]) => `<div><dt>${esc(key)}</dt><dd>${esc(value)}</dd></div>`).join("")}</dl>` : ""}${node.url ? `<a class="link-btn" target="_blank" rel="noopener" href="${esc(node.url)}">${pick("打开论文来源 ↗","Open paper source ↗")}</a>` : ""}<h5 data-toc="false">${pick("当前局部关系","Relations in this view")}</h5><ul>${rows || `<li>${pick("无其他关系","No additional relation")}</li>`}</ul>`;
    };
    const draw = () => {
      const center = select.value;
      const direct = allEdges.filter((edge) => edge.source === center || edge.target === center);
      const limits = {"semantic-evidence":6,"nearest-work":4,"states-problem":1,"uses-mechanism":1,"tests-hypothesis":1,"evaluates-on":3,"covers-domain":3,"uses-model":3,"belongs-to":1};
      const counts = {};
      const chosen = direct.filter((edge) => {
        const limit = limits[edge.relation] ?? 0;
        counts[edge.relation] = (counts[edge.relation] || 0) + 1;
        return counts[edge.relation] <= limit;
      });
      const selectedIds = new Set([center]);
      chosen.forEach((edge) => {selectedIds.add(edge.source);selectedIds.add(edge.target);});
      const paperIds = new Set([...selectedIds].filter((id) => ["paper","paper-alias"].includes(nodes.get(id)?.kind)));
      const crossPaper = allEdges.filter((edge) => paperIds.has(edge.source) && paperIds.has(edge.target) && ["citation","reference"].includes(edge.relation));
      const edges = [...chosen,...crossPaper];
      const selectedNodes = [...selectedIds].map((id) => nodes.get(id)).filter(Boolean);
      const groups = {paper:[],claim:[],idea:[],asset:[],track:[]};
      selectedNodes.forEach((node) => groups[kindGroup(node)].push(node));
      const positions = new Map();
      const place = (rows,x,minY,maxY) => rows.forEach((node,index) => positions.set(node.id,{x,y:rows.length===1?(minY+maxY)/2:minY+(maxY-minY)*index/(rows.length-1)}));
      groups.paper.sort((a,b) => (a.kind === "paper-alias") - (b.kind === "paper-alias") || Number((b.citation_count || 0)-(a.citation_count || 0)));
      place(groups.paper,120,70,590); place(groups.claim,430,170,490); place(groups.idea,650,330,330); place(groups.track,1100,100,100); place(groups.asset,1010,190,590);
      svg.replaceChildren();
      const lineLayer = document.createElementNS(ns,"g"); lineLayer.setAttribute("class","system-evidence-lines"); svg.appendChild(lineLayer);
      edges.forEach((edge) => {
        const a=positions.get(edge.source), b=positions.get(edge.target); if(!a||!b) return;
        const line=document.createElementNS(ns,"line"); line.setAttribute("x1",a.x);line.setAttribute("y1",a.y);line.setAttribute("x2",b.x);line.setAttribute("y2",b.y);line.setAttribute("class",`relation-${edge.relation}`);lineLayer.appendChild(line);
        const title=document.createElementNS(ns,"title"); title.textContent=relationLabel(edge.relation); line.appendChild(title);
      });
      const nodeLayer=document.createElementNS(ns,"g"); nodeLayer.setAttribute("class","system-evidence-nodes"); svg.appendChild(nodeLayer);
      selectedNodes.forEach((node) => {
        const p=positions.get(node.id); if(!p) return;
        const group=document.createElementNS(ns,"g"); const kg=kindGroup(node); group.setAttribute("class",`system-evidence-node kind-${kg}`); group.setAttribute("tabindex","0"); group.setAttribute("transform",`translate(${p.x},${p.y})`);
        const w=kg==="idea"?230:kg==="claim"?230:kg==="paper"?250:190; const h=kg==="idea"?66:kg==="claim"?62:52;
        const rect=document.createElementNS(ns,"rect");rect.setAttribute("x",-w/2);rect.setAttribute("y",-h/2);rect.setAttribute("width",w);rect.setAttribute("height",h);rect.setAttribute("rx",12);group.appendChild(rect);
        const kind=document.createElementNS(ns,"text");kind.setAttribute("class","node-kind");kind.setAttribute("x",-w/2+12);kind.setAttribute("y",-h/2+15);kind.textContent=node.kind;group.appendChild(kind);
        const text=document.createElementNS(ns,"text");text.setAttribute("class","node-label");text.setAttribute("text-anchor","middle");text.setAttribute("y",7);text.textContent=truncate(graphNodeLabel(node),kg==="paper"?34:28);group.appendChild(text);
        const title=document.createElementNS(ns,"title");title.textContent=graphNodeLabel(node);group.appendChild(title);
        const incident=edges.filter((edge)=>edge.source===node.id||edge.target===node.id); const activate=()=>{svg.querySelectorAll(".system-evidence-node.active").forEach((item)=>item.classList.remove("active"));group.classList.add("active");nodeDetail(node,incident);};
        group.addEventListener("click",activate);group.addEventListener("keydown",(event)=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();activate();}});nodeLayer.appendChild(group);
      });
      const centerNode=nodes.get(center); if(centerNode) nodeDetail(centerNode,edges.filter((edge)=>edge.source===center||edge.target===center));
    };
    select.addEventListener("change",draw); draw();
  }

  function renderSystemDesign() {
    const state = window.RESEARCH_SYSTEM_STATE || {};
    const s2 = window.S2_LITERATURE_META || {};
    return `${renderLiveArchitecture(state,s2)}${renderEvidenceGraphPanel(state)}${renderDetailedFlow()}${renderArtifactsAutomation(state)}`;
  }

  function renderCurrentIdeas() {
    const bank = window.ICLR_LOW_RESOURCE_IDEAS || {summary:{},passed_ideas:[]};
    const inspired = window.MACHINE_SCHOOL_IDEAS || {summary:{},passed_ideas:[]};
    const discoveryV4 = window.IDEA_DISCOVERY_V4 || {summary:{},tournament_finalists:[],all_candidates:[],pareto_front_ids:[]};
    const discovery = window.IDEA_DISCOVERY_V3 || {summary:{},shortlist:[],repair:[],pareto_front_ids:[]};
    const repairRound = window.IDEA_DISCOVERY_V31 || {summary:{},children:[]};
    const summary = bank.summary || {};
    const all = bank.passed_ideas || [];
    const pass = all.filter((idea) => currentVerdict(idea) === "pass");
    const revise = all.filter((idea) => currentVerdict(idea) === "revise");
    const block = all.filter((idea) => currentVerdict(idea) === "block");
    const inspiredAll = inspired.passed_ideas || [];
    const inspiredPass = inspiredAll.filter((idea) => currentVerdict(idea) === "pass");
    const inspiredRevise = inspiredAll.filter((idea) => currentVerdict(idea) === "revise");
    const inspiredBlock = inspiredAll.filter((idea) => currentVerdict(idea) === "block");
    const v4Summary = discoveryV4.summary || {};
    const discoverySummary = discovery.summary || {};
    const repairSummary = repairRound.summary || {};
    const discoveryById = new Map([...(discovery.shortlist || []),...(discovery.repair || [])].map((idea) => [idea.id,idea]));
    const pareto = (discovery.pareto_front_ids || []).map((id) => discoveryById.get(id)).filter(Boolean);
    const v4ById = new Map((discoveryV4.all_candidates || []).map((idea) => [idea.id, idea]));
    const v4Pareto = (discoveryV4.pareto_front_ids || []).map((id) => v4ById.get(id)).filter(Boolean);

    return `<section class="system-decision-summary system-section"><div class="system-decision-head"><div><h3>${pick("主 ICLR Idea Bank","Main ICLR idea bank")}</h3><p>${pick("R1 是结构与可行性筛查，R2 是正式来源约束下的独立机制审查。PASS 表示可以进入实验，不表示论文结论已经成立。","R1 screens structure and feasibility; R2 is an independent mechanism audit under official-source constraints. PASS means ready for experiments, not that the paper claim is established.")}</p></div><a class="link-btn system-primary-link" href="paper-ideas.html#iclr-low-resource-bank">${pick("打开完整 Idea 页面 →","Open the complete idea page →")}</a></div><div class="system-funnel"><div><b>${get(summary.raw_candidates,41)}</b><span>${pick("原始候选","raw")}</span></div><i>→</i><div><b>${get(summary.structured_candidates,29)}</b><span>${pick("结构化候选","structured")}</span></div><i>→</i><div><b>${get(summary.passed,26)}</b><span>${pick("R1 通过","R1 pass")}</span></div><i>→</i><div class="pass"><b>${pass.length}</b><span>PASS</span></div><div class="revise"><b>${revise.length}</b><span>REVISE</span></div><div class="block"><b>${block.length}</b><span>BLOCK</span></div></div>
      ${verdictGroup("进入现象与机制实验","Ready for phenomenon and mechanism pilots",pass,"暂无直接 PASS","No direct PASS")}
      ${verdictGroup("按审查要求重构后再决定","Repair according to review before selection",revise,"暂无 REVISE","No revise items")}
      <details class="system-blocked-list"><summary>${pick(`已停止作为独立论文的方向（${block.length}）`,`Blocked as standalone papers (${block.length})`)}</summary><div class="system-blocked-chips">${block.map((idea) => `<a href="paper-ideas.html#iclr-${esc(idea.id)}">${esc(titleOf(idea))}</a>`).join("")}</div></details>
    </section>
    <section class="system-v4-summary system-section"><div class="system-decision-head"><div><h3>${pick("Idea Discovery v4：受约束组合与条件复活","Idea Discovery v4: constrained composition and conditional revival")}</h3><p>${pick(`新增 ${v4Summary.raw_candidates || 0} 个候选：${v4Summary.discussion || 0} 个全新组合、${v4Summary.revival || 0} 个条件复活、${v4Summary.repair || 0} 个待补强、${v4Summary.component || 0} 个组件保留。组合只要对应真实失败闭环且组件不可删除，就不会因“排列组合”本身被否定。`,`Added ${v4Summary.raw_candidates || 0} candidates: ${v4Summary.discussion || 0} new compositions, ${v4Summary.revival || 0} conditional revivals, ${v4Summary.repair || 0} repair candidates, and ${v4Summary.component || 0} retained components. Combinations are allowed when they close a real failure loop and their atoms are necessary.`)}</p></div><a class="link-btn" href="paper-ideas.html#idea-discovery-v4">${pick("查看全部 v4 候选 →","View all v4 candidates →")}</a></div><div class="system-v4-counts"><span><b>${v4Summary.repository_patterns || 0}</b>${pick("仓库工作流模式","repository patterns")}</span><span><b>${v4Summary.tournament_finalists || 0}</b>${pick("锦标赛 finalists","tournament finalists")}</span><span><b>${v4Summary.external_reviewed || 0}</b>${pick("已外审","externally reviewed")}</span><span><b>${v4Summary.external_pass || 0}</b>R2 PASS</span><span><b>${v4Summary.external_revise || 0}</b>R2 REVISE</span><span><b>${v4Summary.external_block || 0}</b>${pick("当前不独立推进","not standalone now")}</span></div><div class="system-v3-pareto"><b>v4 Pareto front</b>${v4Pareto.map((idea) => `<span>${esc(titleOf(idea))}</span>`).join("")}</div></section>
    <section class="system-solution-summary system-section"><div class="system-decision-head"><div><h3>${pick("Idea Discovery v3：解决方案优先分支","Idea Discovery v3: solution-first branches")}</h3><p>${pick(`针对原 REVISE 问题生成 ${discoverySummary.raw_children || 0} 个方法子节点，其中 ${discoverySummary.internal_shortlist || 0} 个通过内部机制筛查、${discoverySummary.repair || 0} 个仍需修订；外部 R2 已完成 ${discoverySummary.external_reviewed || 0}/${discoverySummary.internal_shortlist || 0}。这些子节点不会自动改变主 Bank 的 4 个正式 PASS。`,`Generated ${discoverySummary.raw_children || 0} method children from earlier REVISE problems: ${discoverySummary.internal_shortlist || 0} passed internal mechanism screening and ${discoverySummary.repair || 0} require repair; external R2 is complete for ${discoverySummary.external_reviewed || 0}/${discoverySummary.internal_shortlist || 0}. These children do not automatically change the four formal main-bank PASS ideas.`)}</p></div><a class="link-btn" href="paper-ideas.html#solution-first-v3">${pick("查看完整方法子节点 →","View all method children →")}</a></div><div class="system-v3-summary"><span><b>${discoverySummary.repository_patterns || 0}</b>${pick("GitHub 系统模式","GitHub patterns")}</span><span><b>${discoverySummary.workflow_stages || 0}</b>${pick("发现阶段","stages")}</span><span><b>${discoverySummary.internal_shortlist || 0}</b>${pick("v3 内部短名单","v3 shortlist")}</span><span><b>${discoverySummary.external_pass || 0}</b>v3 R2 PASS</span><span><b>${repairSummary.children || 0}</b>${pick("v3.1 修订子节点","v3.1 repairs")}</span><span><b>${repairSummary.external_pass || 0}</b>v3.1 R2 PASS</span></div><div class="system-v3-pareto"><b>Pareto front</b>${pareto.map((idea) => `<span>${esc(titleOf(idea))}</span>`).join("")}</div></section>
    <section class="system-inspired-summary system-section"><div class="system-decision-head"><div><h3>${pick("网络灵感补充批次","Internet-inspired supplementary batch")}</h3><p>${pick(`24 个原始候选完成内部筛查和外部审查：${inspiredPass.length} 个可直接 Pilot、${inspiredRevise.length} 个需重构、${inspiredBlock.length} 个停止或合并。`,`Twenty-four raw candidates completed internal and external review: ${inspiredPass.length} pilot-now, ${inspiredRevise.length} repair candidates, and ${inspiredBlock.length} stop-or-merge items.`)}</p></div><a class="link-btn" href="paper-ideas.html#machine-school-inspired-ideas">${pick("查看完整补充批次 →","View the full supplementary batch →")}</a></div>
      ${verdictGroup("可立即做 P0/P1","Pilot now",inspiredPass,"暂无","None")}
      ${verdictGroup("需要按外部审查重构","Repair according to external review",inspiredRevise,"暂无","None")}
    </section>
    <section class="system-status-guide system-section"><h3>${pick("Idea 状态如何解释","How to interpret idea states")}</h3><div class="system-status-grid"><article><b>PASS</b><p>${pick("新颖性和机制边界暂时成立，可以进入 P0/P1；仍需实验排除替代解释。","Novelty and mechanism boundary are provisionally viable; P0/P1 must still eliminate alternatives.")}</p></article><article><b>REVISE</b><p>${pick("问题可能重要，但机制、碰撞边界或决定性实验不足，必须按 required action 重写。","The problem may matter, but mechanism, collision boundary, or decisive experiment must be repaired.")}</p></article><article><b>BLOCK</b><p>${pick("当前版本不适合作为独立论文，但不会永久删除；可进入条件复活、组件、Baseline 或合并分支。","The current version is not suitable as a standalone paper, but it is not permanently deleted; it may return through conditional revival, component reuse, baselines, or merging.")}</p></article><article><b>PILOT-NOW</b><p>${pick("已具备低资源决定性实验，可以先验证现象而不开发完整系统。","A low-resource decisive experiment is specified, so the phenomenon can be tested before full development.")}</p></article></div></section>`;
  }

  window.renderSystemOverview = function renderSystemOverview(config) {
    const chapters = pageArchitecture("system-overview").chapters || [];
    requestAnimationFrame(() => bindEvidenceGraphExplorer());
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${renderCustomChapter(chapters[0],0,renderSystemDesign())}${renderCustomChapter(chapters[1],1,renderCurrentIdeas())}`;
  };
})();
