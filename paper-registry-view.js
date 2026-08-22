(() => {
  const gateOrder = [
    ["hierarchical-rubric", "分层论文 Rubric", "Hierarchical rubric"],
    ["verification-refinement", "验证→定向修复", "Verification → refinement"],
    ["citation-integrity", "引用完整性", "Citation integrity"],
    ["visual-story", "视觉叙事", "Visual story"],
    ["reproducibility-bundle", "复现包", "Reproducibility bundle"],
    ["agent-native-artifact", "Agent-native 工件", "Agent-native artifact"],
    ["reader-simulation", "读者模拟", "Reader simulation"],
    ["submission-package", "投稿包 Dry-run", "Submission package dry-run"],
  ];
  const pickR = (zh, en) => language === "zh" ? zh : en;
  const e = (value) => esc(String(value ?? ""));
  const tone = (value) => {
    const s=String(value||"").toUpperCase();
    if(s==="PASS"||s.includes("SUPPORTED")||s==="SUBMISSION_READY") return "pass";
    if(s.includes("REPAIR")||s.includes("PENDING")||s.includes("MIGRATION")||s.includes("IN_PROGRESS")) return "check";
    return "hold";
  };
  const pill = (value, label) => `<span class="experiment-status-badge status-${tone(value)}">${e(label || value || "--")}</span>`;
  const layerLabel = (key, value) => {
    const labels={
      scientific:{zh:"科学证据",en:"Scientific evidence"},
      paper_quality:{zh:"论文质量",en:"Paper quality"},
      paper_preparation:{zh:"投稿准备 8 门",en:"8-gate preparation"},
      submission:{zh:"人工投稿",en:"Human submission"},
    };
    const l=labels[key]||{zh:key,en:key};
    return `<article><b>${pickR(l.zh,l.en)}</b>${pill(value)}<p>${key==="paper_preparation"?pickR("这是独立于旧 SUBMISSION_READY 的新协议状态；未迁移不等于科学失败。","This is independent of the legacy SUBMISSION_READY state; not-yet-migrated never means scientific failure."):""}</p></article>`;
  };
  const prepGrid = (paper) => {
    const prep=paper.paper_preparation||{}, passes=prep.gate_pass||{};
    if(prep.status==="NOT_YET_ELIGIBLE") return `<div class="current-status-rule"><b>${pickR("Paper Preparation 尚未启动","Paper Preparation has not started")}</b><span>${pickR("当前论文仍在 Targeted Repair 或更早阶段。先完成科学/论文修复，再进入这 8 个投稿准备门。","The paper is still in Targeted Repair or earlier. Finish scientific/manuscript repair before entering these eight submission-preparation gates.")}</span></div>`;
    const migrated=prep.pass===true;
    return `<div class="preflight-card-grid paper-registry-prep-grid">${gateOrder.map(([key,zh,en])=>{
      const value=migrated?(passes[key]===true?"PASS":"HOLD"):"PENDING_MIGRATION";
      const label=migrated?(passes[key]===true?"PASS":"HOLD"):pickR("待迁移","MIGRATION PENDING");
      return `<article class="preflight-card"><header><b>${pickR(zh,en)}</b>${pill(value,label)}</header><p>${migrated?pickR("已有 content-addressed preparation receipt。","Bound to a content-addressed preparation receipt."):pickR("旧论文已达到 SUBMISSION_READY，但尚未按新协议生成这一门的独立 receipt。","Legacy paper is SUBMISSION_READY, but this independent gate has not yet been migrated to the new protocol.")}</p></article>`;
    }).join("")}</div>`;
  };
  const paperCard = (paper, index) => {
    const prep=paper.paper_preparation||{}, gates=paper.gates||{}, layers=paper.layers||{};
    const id=`paper-${String(paper.paper_id||index).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")}`;
    const ready=paper.current_state==="SUBMISSION_READY";
    const gateRows=[
      ["Claim Audit",gates.claim_audit],
      ["Manuscript CI",gates.manuscript_ci],
      ["Prebuttal",gates.prebuttal],
      ["Submission Readiness",gates.submission_readiness],
    ].map(([name,ok])=>`<tr><td>${e(name)}</td><td>${pill(ok?"PASS":"HOLD",ok?"PASS":"—")}</td></tr>`).join("");
    return `<section class="panel paper-registry-paper" data-paper-id="${e(paper.paper_id)}"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER ${String(index+1).padStart(2,"0")} · ${e(paper.paper_id)}</div><h2 id="${e(id)}">${e(paper.title)}</h2><p class="section-intro">${e(paper.central_question||pickR("canonical contract 未填写 central question","central question unavailable in canonical contract"))}</p></div>${pill(paper.current_state, paper.current_state)}</div><div class="current-experiment-grid paper-registry-layers">${Object.entries(layers).map(([key,value])=>layerLabel(key,value)).join("")}</div><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${pickR("已有 Paper Acceptance 门","Existing Paper Acceptance gate")}</th><th>${pickR("状态","Status")}</th></tr></thead><tbody>${gateRows}</tbody></table></div><div class="reader-metrics"><div><b>${paper.supported_claims||0}</b><span>${pickR("冻结支持主张","frozen supported claims")}</span></div><div><b>${paper.active_unrefuted_claims||0}</b><span>${pickR("活跃未反驳主张","active unrefuted claims")}</span></div><div><b>${paper.ledger_summary?.mock_reviews||0}</b><span>${pickR("Mock PC reviews","Mock PC reviews")}</span></div><div><b>${paper.ledger_events||0}</b><span>${pickR("append-only events","append-only events")}</span></div></div><h3>${pickR("Paper Preparation Protocol · 8 个投稿准备门","Paper Preparation Protocol · eight submission-preparation gates")}</h3>${prepGrid(paper)}<div class="current-status-rule"><b>${pickR("当前下一步","Current next step")}</b><span>${ready?(prep.pass?pickR("科学与投稿准备均已闭合；仅保留人工作者责任、OpenReview/venue policy 核验与真实提交。","Scientific and preparation gates are closed; only human author responsibility, OpenReview/venue-policy checks, and the actual submission remain."):pickR("论文已是 legacy SUBMISSION_READY；补做新 Paper Preparation migration，但不得借迁移扩大 claim 或启动新实验。","This is legacy SUBMISSION_READY. Migrate the new preparation protocol without expanding claims or launching new experiments.")):pickR("继续当前 Targeted Repair；Paper Preparation 不拥有改变科学结论或授权实验的权限。","Continue the current Targeted Repair. Paper Preparation has no authority to change science or authorize experiments.")}</span></div><small>${pickR("Canonical contract SHA", "Canonical contract SHA")}: <code>${e(String(paper.contract_sha256||"").slice(0,16))}</code>${prep.receipt_sha256?` · ${pickR("Preparation receipt","Preparation receipt")}: <code>${e(prep.receipt_sha256.slice(0,16))}</code>`:""}</small></section>`;
  };

  window.renderPaperRegistryOverview = function renderPaperRegistryOverview() {
    const state=window.PAPER_REGISTRY_STATE||{}, summary=state.summary||{}, papers=state.papers||[];
    if(!papers.length) return "";
    const intro=`<section class="panel paper-registry-hero" id="paper-registry"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER REGISTRY · CANONICAL LEDGER PROJECTION</div><h2 data-toc="false">${pickR("现在不是一篇“选中论文”，而是 5 篇 canonical paper 的统一状态表","This is now a registry of five canonical papers, not a single selected paper")}</h2><p class="section-intro">${pickR("这里直接读取 Paper Acceptance append-only ledger。科学状态、论文质量状态、新增的 8 门投稿准备状态和人工提交状态分开显示，避免把“科学上 ready”“论文工件完整”“已经可以由人投稿”混成一个 READY 标签。","This view projects the append-only Paper Acceptance ledgers directly. Scientific state, paper-quality state, the new eight-gate preparation state, and human submission state are shown separately so one READY label cannot conflate them.")}</p></div><strong>${summary.submission_ready||0}/${summary.papers||0}<span>${pickR("已到 SUBMISSION_READY","at SUBMISSION_READY")}</span></strong></div><div class="current-research-stats"><div class="stat-started"><b>${summary.submission_ready||0}</b><span>${pickR("SUBMISSION_READY","SUBMISSION_READY")}</span></div><div class="stat-pending"><b>${summary.targeted_repair||0}</b><span>${pickR("TARGETED_REPAIR","TARGETED_REPAIR")}</span></div><div><b>${summary.preparation_pass||0}</b><span>${pickR("新 8 门已迁移 PASS","new 8-gate migrations PASS")}</span></div><div class="stat-pending"><b>${summary.legacy_ready_needs_preparation_migration||0}</b><span>${pickR("legacy ready 待迁移","legacy ready awaiting migration")}</span></div><div class="stat-pending"><b>${summary.human_submission_signoff_pending||0}</b><span>${pickR("等待人工投稿签字","awaiting human submission signoff")}</span></div></div><div class="reader-rule"><b>${pickR("状态解释","How to read this")}</b><span>${pickR("Paper Preparation migration 只增加审计工件，不会倒写旧合同，也不会把 support failure 变成 scientific negative。只有 human authority 能进入真实 SUBMITTED。","Paper Preparation migration adds audit artifacts only. It never rewrites legacy contracts or turns support failures into scientific negatives. Only human authority may enter the actual SUBMITTED state.")}</span></div></section>`;
    return `${intro}${papers.map(paperCard).join("")}`;
  };
})();
