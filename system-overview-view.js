(() => {
  const get = (value, fallback = 0) => value === undefined || value === null ? fallback : value;
  const latestReview = (idea) => {
    const rows = idea?.external_reviews || [];
    return rows.length ? rows[rows.length - 1] : null;
  };
  const currentVerdict = (idea) => idea?.external_verdict || latestReview(idea)?.verdict || "pending";
  const titleOf = (idea) => textOf(idea?.title || idea?.name || "");
  const ideaHref = (idea) => idea?.final_status ? "paper-ideas.html#machine-school-inspired-ideas" : `paper-ideas.html#iclr-${esc(idea?.id || "low-resource-bank")}`;

  function stat(value, zh, en, tone = "") {
    return `<div class="system-stat ${tone}"><b>${esc(value)}</b><span>${language === "zh" ? zh : en}</span></div>`;
  }

  function pipelineStage(index, zhTitle, enTitle, zhBody, enBody, tag) {
    return `<article class="system-stage"><div class="system-stage-index">${String(index).padStart(2,"0")}</div><div><span>${esc(tag)}</span><h3 data-toc="false">${language === "zh" ? zhTitle : enTitle}</h3><p>${language === "zh" ? zhBody : enBody}</p></div></article>`;
  }

  function ideaCard(idea, extra = "") {
    const verdict = currentVerdict(idea);
    const review = latestReview(idea);
    const status = idea?.final_status || (verdict === "pass" ? "experiment-pending" : verdict);
    return `<a class="system-idea-card verdict-${esc(verdict)}" href="${ideaHref(idea)}"><header><span>${esc(String(verdict).toUpperCase())}</span><small>${esc(status)}</small></header><h4 data-toc="false">${esc(titleOf(idea))}</h4><p>${esc(textOf(idea?.purpose || idea?.problem || ""))}</p>${extra ? `<div class="system-idea-note">${extra}</div>` : ""}${review?.required_action ? `<div class="system-idea-action"><b>${language === "zh" ? "审查后要求" : "Required revision"}</b>${esc(review.required_action)}</div>` : ""}</a>`;
  }

  function verdictGroup(titleZh, titleEn, ideas, emptyZh, emptyEn) {
    return `<section class="system-idea-group"><h3>${language === "zh" ? titleZh : titleEn}<span>${ideas.length}</span></h3>${ideas.length ? `<div class="system-idea-grid">${ideas.map((idea) => ideaCard(idea)).join("")}</div>` : `<p class="empty">${language === "zh" ? emptyZh : emptyEn}</p>`}</section>`;
  }

  function renderSystemDesign() {
    const state = window.RESEARCH_SYSTEM_STATE || {};
    const summary = state.summary || {};
    const s2 = window.S2_LITERATURE_META || {};
    const stats = s2.statistics || {};
    const components = state.components || [];
    const running = components.filter((item) => item.status === "running").length;
    const pilot = state.pilot_registry?.summary || {};
    const routeCounts = stats.route_counts || {};
    const routeLabels = {
      seed:["种子论文","Seed papers"], topic:["同题工作","Direct topic"], failure:["失败模式","Failure modes"],
      mechanism:["机制迁移","Mechanisms"], analogy:["跨域类比","Cross-domain analogy"], citation:["引用扩展","Citations"], reference:["参考文献扩展","References"]
    };
    const routes = Object.entries(routeCounts).sort((a,b)=>b[1]-a[1]).map(([key,value]) => `<div><b>${value}</b><span>${language === "zh" ? routeLabels[key]?.[0] || key : routeLabels[key]?.[1] || key}</span></div>`).join("");
    const componentRows = components.map((item) => `<tr><td>${esc(item.name)}</td><td><span class="system-status ${esc(item.status)}">${esc(item.status)}</span></td><td>${esc(item.detail || item.description || "")}</td></tr>`).join("");

    return `<section class="system-live-summary">
      <div class="system-stat-grid">
        ${stat(get(summary.papers, stats.paper_count),"篇去重论文","deduplicated papers")}
        ${stat(get(summary.queries, stats.query_count),"个规划检索查询","planned queries")}
        ${stat(get(summary.evidence_nodes),"个证据节点","evidence nodes")}
        ${stat(get(summary.evidence_edges),"条证据关系","evidence edges")}
        ${stat(get(state.collision_engine?.summary?.pairwise_comparisons,406),"组 Idea 两两比较","idea-pair checks")}
        ${stat(get(summary.collision_flags),"个碰撞标记","collision flags")}
        ${stat(get(pilot.phases),"个 P0/P1/P2 阶段","P0/P1/P2 phases")}
        ${stat(get(summary.pilot_results),"个已回流实验结果","ingested pilot results", get(summary.pilot_results) ? "good" : "warn")}
      </div>
      <div class="system-source-grid">
        <section><h3>${language === "zh" ? "文献从哪里来" : "Where the literature comes from"}</h3><p>${language === "zh" ? "Semantic Scholar Academic Graph 提供元数据；种子论文、主题、失败模式、机制、跨领域类比和引用关系共同扩展语料。正式判断仍回到论文页、OpenReview、会议论文集、官方项目页和作者仓库。" : "Semantic Scholar Academic Graph supplies metadata. Seed papers, direct topics, failure modes, mechanisms, cross-domain analogies, citations, and references expand the corpus. Final judgments return to official papers, OpenReview, proceedings, project pages, and author repositories."}</p><div class="system-route-grid">${routes}</div></section>
        <section><h3>${language === "zh" ? "每篇论文抽取什么" : "What is extracted from each paper"}</h3><div class="system-field-list"><span>${language === "zh" ? "问题与动机" : "Problem and motivation"}</span><span>${language === "zh" ? "已有局限" : "Prior limitations"}</span><span>${language === "zh" ? "核心直觉" : "Core intuition"}</span><span>${language === "zh" ? "方法机制" : "Mechanism"}</span><span>${language === "zh" ? "成立假设" : "Assumptions"}</span><span>${language === "zh" ? "失效边界" : "Failure boundary"}</span><span>${language === "zh" ? "模型/API/训练" : "Models / APIs / training"}</span><span>${language === "zh" ? "数据与实验资源" : "Data and compute"}</span></div></section>
      </div>
    </section>
    <section class="system-pipeline" aria-label="research data flow">
      ${pipelineStage(1,"定义研究范围","Define scope","先冻结会议、研究边界、资源限制和“什么才算自进化”的判据。","Freeze the venue, field boundary, resource limits, and the criterion for genuine self-evolution.","SCOPE")}
      ${pipelineStage(2,"规划检索路径","Plan retrieval","同时检索同题工作、失败模式、可迁移机制、跨领域类比和引用邻域。","Retrieve direct competitors, failure modes, reusable mechanisms, structural analogies, and citation neighborhoods.","QUERY")}
      ${pipelineStage(3,"文献获取与去重","Retrieve and deduplicate","合并正式论文、预印本、项目页和仓库；重复版本归并，未知信息不猜测。","Merge papers, preprints, project pages, and repositories; resolve duplicate versions and preserve unknowns.","CORPUS")}
      ${pipelineStage(4,"构建证据图谱","Build evidence graph","把论文连接到问题、机制、假设、数据集、模型、实验和候选 Idea。","Connect papers to problems, mechanisms, assumptions, datasets, models, experiments, and candidate ideas.","EVIDENCE")}
      ${pipelineStage(5,"按固定算子生成 Idea","Generate with operators","使用限制反转、假设移除、目标—评测错位、矛盾消解、空白补全、跨域类比和指标替换等算子。","Use limitation inversion, assumption removal, objective-evaluation mismatch, contradiction resolution, missing-cell completion, analogy, and metric replacement.","SYNTHESIS")}
      ${pipelineStage(6,"内部七维筛查","Run internal gates","检查持久学习、更新表面、可识别归因、多轮稳定、圈外迁移、独立反馈和等预算可行性。","Test persistent learning, update surface, identifiable credit, multi-round stability, transfer, independent feedback, and matched-budget feasibility.","R1")}
      ${pipelineStage(7,"机制级碰撞与外部审查","Audit novelty","分别检查问题、机制、方法组合和决定性实验；再由 Oracle 调用指定 Agent 项目的网页版 ChatGPT 给出 PASS / REVISE / BLOCK。","Check problem, mechanism, combination, and decisive-experiment collisions, then obtain PASS / REVISE / BLOCK through the Oracle-mediated Agent-project web GPT.","R2")}
      ${pipelineStage(8,"P0/P1/P2 与结果回流","Plan and falsify","P0 验证现象，P1 验证机制，P2 冻结跨模型/跨域迁移；只有结构化结果才能改变 Idea 状态。","P0 checks the phenomenon, P1 tests the mechanism, and P2 freezes cross-model/domain transfer. Only structured results can change idea status.","PILOT")}
    </section>
    <section class="system-automation-panel">
      <div><h3>${language === "zh" ? "自动化边界" : "Automation boundary"}</h3><p>${language === "zh" ? `当前 ${running} 个核心组件运行中。每日任务重建证据、碰撞、谱系和 Pilot Registry；每周任务更新文献并进行有限外部修订审查。` : `${running} core components are running. Daily jobs rebuild evidence, collisions, lineage, and the pilot registry; weekly jobs refresh literature and request bounded external repair reviews.`}</p></div>
      <div class="warning-box"><b>${language === "zh" ? "有意不自动化的部分" : "Intentionally not automated"}</b>${language === "zh" ? "系统不会自动决定最终选题，也不会无限制执行和修改实验代码。老师、师兄和作者负责研究范围、主张边界、最终方向和正式实验。" : "The system does not autonomously select the final paper or execute and rewrite experiments without limits. Advisors and authors control scope, claim boundaries, final direction, and formal experiments."}</div>
      <div class="history-table-scroll"><table class="matrix"><thead><tr><th>${language === "zh" ? "模块" : "Component"}</th><th>${language === "zh" ? "状态" : "Status"}</th><th>${language === "zh" ? "说明" : "Detail"}</th></tr></thead><tbody>${componentRows}</tbody></table></div>
    </section>`;
  }

  function renderCurrentIdeas() {
    const bank = window.ICLR_LOW_RESOURCE_IDEAS || {summary:{},passed_ideas:[]};
    const inspired = window.MACHINE_SCHOOL_IDEAS || {summary:{},passed_ideas:[]};
    const summary = bank.summary || {};
    const all = bank.passed_ideas || [];
    const pass = all.filter((idea) => currentVerdict(idea) === "pass");
    const revise = all.filter((idea) => currentVerdict(idea) === "revise");
    const block = all.filter((idea) => currentVerdict(idea) === "block");
    const inspiredAll = inspired.passed_ideas || [];
    const inspiredPass = inspiredAll.filter((idea) => currentVerdict(idea) === "pass");
    const inspiredRevise = inspiredAll.filter((idea) => currentVerdict(idea) === "revise");
    const inspiredBlock = inspiredAll.filter((idea) => currentVerdict(idea) === "block");

    return `<section class="system-decision-summary">
      <div class="system-decision-head"><div><h3>${language === "zh" ? "主 ICLR Idea Bank" : "Main ICLR idea bank"}</h3><p>${language === "zh" ? "程序化首轮通过不等于最终保留；下方使用外部 R2 结论重新分层。" : "A programmatic first-round pass is not final acceptance; the portfolio below is stratified by the external R2 verdict."}</p></div><a class="link-btn system-primary-link" href="paper-ideas.html#iclr-low-resource-bank">${language === "zh" ? "打开完整 Idea 页面 →" : "Open the complete idea page →"}</a></div>
      <div class="system-funnel"><div><b>${get(summary.raw_candidates,41)}</b><span>${language === "zh" ? "原始候选" : "raw"}</span></div><i>→</i><div><b>${get(summary.structured_candidates,29)}</b><span>${language === "zh" ? "结构化候选" : "structured"}</span></div><i>→</i><div><b>${get(summary.passed,26)}</b><span>${language === "zh" ? "R1 通过" : "R1 pass"}</span></div><i>→</i><div class="pass"><b>${pass.length}</b><span>PASS</span></div><div class="revise"><b>${revise.length}</b><span>REVISE</span></div><div class="block"><b>${block.length}</b><span>BLOCK</span></div></div>
      ${verdictGroup("直接保留：进入现象与机制实验","PASS: ready for phenomenon and mechanism pilots",pass,"暂无直接 PASS","No direct PASS")}
      ${verdictGroup("修改后再决定","REVISE: repair before direction selection",revise,"暂无 REVISE","No revise items")}
      <details class="system-blocked-list"><summary>${language === "zh" ? `已停止作为独立论文的方向（${block.length}）` : `Blocked as standalone papers (${block.length})`}</summary><div class="system-blocked-chips">${block.map((idea) => `<a href="paper-ideas.html#iclr-${esc(idea.id)}">${esc(titleOf(idea))}</a>`).join("")}</div></details>
    </section>
    <section class="system-inspired-summary"><div class="system-decision-head"><div><h3>${language === "zh" ? "网络灵感补充批次" : "Internet-inspired supplementary batch"}</h3><p>${language === "zh" ? `24 个原始候选经过内部筛查和完整外部审查，最终 ${inspiredPass.length} 个可直接 Pilot、${inspiredRevise.length} 个需重构、${inspiredBlock.length} 个停止或合并。` : `Twenty-four raw candidates received internal and complete external review, leaving ${inspiredPass.length} pilot-now, ${inspiredRevise.length} repair candidates, and ${inspiredBlock.length} stop-or-merge items.`}</p></div><a class="link-btn" href="paper-ideas.html#machine-school-inspired-ideas">${language === "zh" ? "查看完整补充批次 →" : "View the full supplementary batch →"}</a></div>
      ${verdictGroup("可立即做 P0/P1","Pilot now",inspiredPass,"暂无","None")}
      ${verdictGroup("师兄与老师可讨论的重构候选","Repair then decide",inspiredRevise,"暂无","None")}
    </section>
    <section class="system-advisor-questions"><h3>${language === "zh" ? "希望师兄重点帮忙判断" : "Questions for advisor judgment"}</h3><ol><li>${language === "zh" ? "研究范围是否过宽，是否应只保留回归门控、记忆巩固和组合更新中的两条主线？" : "Is the scope too broad, and should we keep only two of regression gating, memory consolidation, and compositional updates?"}</li><li>${language === "zh" ? "4 个 R2 PASS 中，哪个最值得优先投入正式实验？" : "Which of the four R2 PASS directions deserves the first formal experiment?"}</li><li>${language === "zh" ? "当前审查是否过于保守，哪些 REVISE 值得通过现象实验而不是文献判断继续保留？" : "Is the review too conservative, and which REVISE ideas deserve a phenomenon pilot rather than a literature-only decision?"}</li><li>${language === "zh" ? "低资源约束和 P0/P1/P2 顺序是否合理，是否应为某个高潜力方向放宽预算？" : "Are the low-resource constraints and P0/P1/P2 order appropriate, or should one high-upside direction receive more budget?"}</li></ol></section>`;
  }

  window.renderSystemOverview = function renderSystemOverview(config) {
    const chapters = pageArchitecture("system-overview").chapters || [];
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${renderCustomChapter(chapters[0],0,renderSystemDesign())}${renderCustomChapter(chapters[1],1,renderCurrentIdeas())}`;
  };
})();
