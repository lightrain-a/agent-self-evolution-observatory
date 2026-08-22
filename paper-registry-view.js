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
  const fmt = (value, digits=3) => Number.isFinite(Number(value)) ? Number(value).toFixed(digits).replace(/0+$/,"" ).replace(/\.$/,"") : "--";
  const repairBoundary = (paper) => {
    const b=paper.targeted_repair_boundary||{};
    if(!b.scheduler_state) return "";
    const r=b.primary_result||{}, power=b.power||{}, ident=b.identification||{}, confirm=b.independent_confirmation||{};
    const pwr=power.four_pair_power_range||[], need=power.independent_pairs_for_80pct_power_range||[];
    const reopen=(b.reopen_conditions||[]).map(x=>`<li>${e(x)}</li>`).join("");
    const frozen=(b.forbidden_repairs||[]).slice(0,4).map(x=>`<li>${e(x)}</li>`).join("");
    return `<div class="paper-registry-boundary"><div class="reader-rule"><b>${pickR("为什么仍停在 Targeted Repair","Why this remains in Targeted Repair")}</b><span>${pickR(`R4 的方向性效应是 +${fmt(r.success_minus_failure,4)}，超过冻结的 ${fmt(r.effect_floor,2)} effect floor；但单侧 permutation p=${fmt(r.permutation_p_success_greater,5)} 没有通过 ${fmt(r.p_threshold,2)} 门。更关键的是，matched-content 识别不稳定，所以这条结果仍不能升级为 provenance 的因果支持。`,`R4 shows a directional +${fmt(r.success_minus_failure,4)} effect above the frozen ${fmt(r.effect_floor,2)} floor, while the one-sided permutation p=${fmt(r.permutation_p_success_greater,5)} misses the ${fmt(r.p_threshold,2)} gate. More importantly, matched-content identification is unstable, so this result cannot yet be promoted to causal provenance support.`)}</span></div><div class="current-experiment-grid paper-registry-boundary-grid"><article><b>${pickR("统计门","Statistical gate")}</b>${pill(r.verdict||b.scheduler_state,r.verdict||b.scheduler_state)}<p>${pickR(`4 个独立 pair 的近似 power 只有 ${fmt(pwr[0],3)}–${fmt(pwr[1],3)}；达到约 80% power 需要约 ${e(need[0])}–${e(need[1])} 个独立 eligible pairs。`,`Approximate power with four independent pairs is only ${fmt(pwr[0],3)}–${fmt(pwr[1],3)}; roughly ${e(need[0])}–${e(need[1])} independent eligible pairs are needed for about 80% power.`)}</p></article><article><b>${pickR("信息等价识别门","Information-equivalence gate")}</b>${pill("REPAIR",`${e(ident.three_reviewer_unanimous_strict_pass||0)}/${e(ident.primary_pairs||0)} unanimous`)}<p>${pickR(`原 verifier ${e(ident.original_verifier_strict_pass||0)}/${e(ident.primary_pairs||0)} 通过；DeepSeek ${e(ident.deepseek_strict_pass||0)}/${e(ident.primary_pairs||0)}；Kimi ${e(ident.kimi_strict_pass||0)}/${e(ident.primary_pairs||0)}。最低 cosine 仍有 ${fmt(ident.minimum_embedding_cosine,3)}，所以主要问题是 actionable guidance 是否真的相同。`,`Original verifier: ${e(ident.original_verifier_strict_pass||0)}/${e(ident.primary_pairs||0)} strict passes; DeepSeek: ${e(ident.deepseek_strict_pass||0)}/${e(ident.primary_pairs||0)}; Kimi: ${e(ident.kimi_strict_pass||0)}/${e(ident.primary_pairs||0)}. Minimum cosine remains ${fmt(ident.minimum_embedding_cosine,3)}, so the main weakness is whether actionable guidance is truly matched.`)}</p></article><article><b>${pickR("独立确认资源","Independent confirmation support")}</b>${pill(confirm.same_release_confirmation_available?"PASS":"HOLD",confirm.same_release_confirmation_available?"AVAILABLE":"0 FRESH TASKS")}<p>${pickR(`按原冻结结构规则重扫同一 WebArena release 后，fresh qualified task=${e(confirm.fresh_same_release_qualified_tasks||0)}。因此不能在看过 R4 后再挑新 task 来救 p 值。`,`Rescanning the same WebArena release under the frozen structural rule leaves ${e(confirm.fresh_same_release_qualified_tasks||0)} fresh qualified tasks. New tasks therefore cannot be selected post hoc to rescue the p-value.`)}</p></article></div><div class="paper-registry-reopen"><div><b>${pickR("只有这些变化才允许重开","Only these changes may reopen the experiment")}</b><ul>${reopen}</ul></div><div><b>${pickR("当前明确禁止","Explicitly frozen now")}</b><ul>${frozen}</ul></div></div></div>`;
  };
  const prepActions = (prep) => {
    const blockers=prep.blockers||[], out=[];
    if(blockers.some(x=>/claim-evidence|method-experiment|evidence_sufficiency|unresolved-critical/.test(x))) out.push(pickR("闭合决定性 claim↔evidence 缺口；support 不可用只记支持债，不改写科学结论。","Close decision-critical claim↔evidence gaps; unavailable support remains support debt and does not rewrite the science."));
    if(blockers.some(x=>/visual-story|visual-evidence/.test(x))) out.push(pickR("把核心主张与边界结果绑定到主文 visual contract。","Bind core claims and boundary evidence to the main-text visual contract."));
    if(blockers.some(x=>/reproducibility/.test(x))) out.push(pickR("补 self-contained source/reproduction bundle，并在干净环境重编译与重算关键数值。","Build a self-contained reproduction bundle and recompile/recompute key numbers in a clean environment."));
    if(blockers.some(x=>/agent-native|claim-raw/.test(x))) out.push(pickR("补 claim→raw evidence roundtrip。","Close the claim→raw-evidence roundtrip."));
    if(blockers.some(x=>/reader-mode|reader-paper/.test(x))) out.push(pickR("完成 figure-first / reproducibility reader，并关闭 decision-critical objection。","Complete figure-first/reproducibility readers and close decision-critical objections."));
    if(blockers.some(x=>/submission-package/.test(x))) out.push(pickR("补 venue policy、AI-use/作者清单、supplement 一致性和 fresh-source compile。","Complete venue policy, AI-use/authorship checklists, supplement consistency, and fresh-source compile."));
    return out;
  };
  const prepGrid = (paper) => {
    const prep=paper.paper_preparation||{}, passes=prep.gate_pass||{};
    if(prep.status==="NOT_YET_ELIGIBLE") return `<div class="current-status-rule"><b>${pickR("Paper Preparation 尚未启动","Paper Preparation has not started")}</b><span>${pickR("当前论文仍在 Targeted Repair 或更早阶段。先完成科学/论文修复，再进入这 8 个投稿准备门。","The paper is still in Targeted Repair or earlier. Finish scientific/manuscript repair before entering these eight submission-preparation gates.")}</span></div>`;
    const hasReceipt=Boolean(prep.receipt_sha256);
    const grid=`<div class="preflight-card-grid paper-registry-prep-grid">${gateOrder.map(([key,zh,en])=>{
      const value=hasReceipt?(passes[key]===true?"PASS":"HOLD"):"PENDING_MIGRATION";
      const label=hasReceipt?(passes[key]===true?"PASS":"BLOCKED"):pickR("待迁移","MIGRATION PENDING");
      const text=!hasReceipt?pickR("尚未生成这一门的独立 receipt。","This gate has no independent receipt yet."):(passes[key]===true?pickR("已有 content-addressed preparation receipt。","Bound to a content-addressed preparation receipt."):pickR("已完成迁移，但这一门存在明确 blocker；不是 legacy pending。","Migration is complete, but this gate has explicit blockers; this is not legacy pending."));
      return `<article class="preflight-card"><header><b>${pickR(zh,en)}</b>${pill(value,label)}</header><p>${text}</p></article>`;
    }).join("")}</div>`;
    const actions=prep.status==="BLOCKED"?prepActions(prep):[];
    const note=actions.length?`<div class="current-status-rule"><b>${pickR("为什么还不能交给作者投稿","Why human submission handoff is still blocked")}</b><span>${actions.map((x,i)=>`${i+1}. ${e(x)}`).join(" ")}</span></div>`:"";
    return grid+note;
  };
  const paperCard = (paper, index) => {
    const prep=paper.paper_preparation||{}, freeze=paper.submission_freeze||{}, gates=paper.gates||{}, layers=paper.layers||{};
    const id=`paper-${String(paper.paper_id||index).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")}`;
    const ready=paper.current_state==="SUBMISSION_READY";
    const gateRows=[
      ["Claim Audit",gates.claim_audit],
      ["Manuscript CI",gates.manuscript_ci],
      ["Prebuttal",gates.prebuttal],
      ["Submission Readiness",gates.submission_readiness],
    ].map(([name,ok])=>`<tr><td>${e(name)}</td><td>${pill(ok?"PASS":"HOLD",ok?"PASS":"—")}</td></tr>`).join("");
    const boundary=repairBoundary(paper);
    const nextStep=ready?(prep.pass?(freeze.status==="MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING"?pickR("机器版本已冻结；只剩作者名单/OpenReview/伦理与 AI-use statement 的人工确认，以及真实上传。","The machine candidate is frozen; only human confirmation of authors/OpenReview/ethics/AI-use statement and the actual upload remain."):pickR("Paper Preparation 已通过；生成 pre-submission freeze checkpoint 后再交给作者。","Paper Preparation passed; create a pre-submission freeze checkpoint before author handoff.")):(prep.status==="BLOCKED"?pickR("Paper Acceptance 已到 SUBMISSION_READY，但新准备协议明确阻断 human handoff；按上面的 blocker 修复，不自动开新实验。","Paper Acceptance is SUBMISSION_READY, but the preparation protocol explicitly blocks human handoff; repair the blockers above without automatically authorizing new experiments."):pickR("论文是 legacy SUBMISSION_READY；补做新 Paper Preparation migration。","This is legacy SUBMISSION_READY; migrate the new Paper Preparation protocol."))):(boundary?pickR("当前 realization 已停在 support + identification boundary。只有下方冻结的 reopen condition 成立后才允许重开；不能继续给同一批 pair 加样本或改门槛。","This realization is held at a support + identification boundary. It may reopen only when one of the frozen conditions below is satisfied; the same pairs cannot receive more samples and the gates cannot be relaxed."):pickR("继续当前论文修复；Paper Preparation 不拥有改变科学结论或授权实验的权限。","Continue paper repair. Paper Preparation has no authority to change science or authorize experiments."));
    return `<section class="panel paper-registry-paper" data-paper-id="${e(paper.paper_id)}"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER ${String(index+1).padStart(2,"0")} · ${e(paper.paper_id)}</div><h2 id="${e(id)}">${e(paper.title)}</h2><p class="section-intro">${e(paper.central_question||pickR("canonical contract 未填写 central question","central question unavailable in canonical contract"))}</p></div>${pill(paper.current_state, paper.current_state)}</div><div class="current-experiment-grid paper-registry-layers">${Object.entries(layers).map(([key,value])=>layerLabel(key,value)).join("")}</div><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${pickR("已有 Paper Acceptance 门","Existing Paper Acceptance gate")}</th><th>${pickR("状态","Status")}</th></tr></thead><tbody>${gateRows}</tbody></table></div><div class="reader-metrics"><div><b>${paper.supported_claims||0}</b><span>${pickR("冻结支持主张","frozen supported claims")}</span></div><div><b>${paper.active_unrefuted_claims||0}</b><span>${pickR("活跃未反驳主张","active unrefuted claims")}</span></div><div><b>${paper.ledger_summary?.mock_reviews||0}</b><span>${pickR("Mock PC reviews","Mock PC reviews")}</span></div><div><b>${paper.ledger_events||0}</b><span>${pickR("append-only events","append-only events")}</span></div></div>${boundary}<h3>${pickR("Paper Preparation Protocol · 8 个投稿准备门","Paper Preparation Protocol · eight submission-preparation gates")}</h3>${prepGrid(paper)}${freeze.status==="MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING"?`<div class="current-status-rule"><b>${pickR("Pre-Submission Freeze · 已冻结机器候选版本","Pre-Submission Freeze · machine candidate frozen")}</b><span>${pickR("Freeze SHA","Freeze SHA")}: <code>${e(String(freeze.freeze_sha256||"").slice(0,16))}</code> · ${freeze.frozen_artifacts||0} ${pickR("个上传工件已绑定。任何后续字节变化都必须产生新的 freeze checkpoint，并重新进入作者确认；当前仍不是 SUBMITTED。","upload artifacts are bound. Any later byte change must create a new freeze checkpoint and return to author confirmation; this is still not SUBMITTED.")}</span></div>`:""}<div class="current-status-rule"><b>${pickR("当前下一步","Current next step")}</b><span>${nextStep}</span></div><small>${pickR("Canonical contract SHA", "Canonical contract SHA")}: <code>${e(String(paper.contract_sha256||"").slice(0,16))}</code>${prep.receipt_sha256?` · ${pickR("Preparation receipt","Preparation receipt")}: <code>${e(prep.receipt_sha256.slice(0,16))}</code>`:""}</small></section>`;
  };

  window.renderPaperRegistryOverview = function renderPaperRegistryOverview() {
    const state=window.PAPER_REGISTRY_STATE||{}, summary=state.summary||{}, papers=state.papers||[];
    if(!papers.length) return "";
    const intro=`<section class="panel paper-registry-hero" id="paper-registry"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER REGISTRY · CANONICAL LEDGER PROJECTION</div><h2 data-toc="false">${pickR("现在不是一篇“选中论文”，而是 "+(summary.papers||papers.length)+" 篇 canonical paper 的统一状态表","This is now a registry of "+(summary.papers||papers.length)+" canonical papers, not a single selected paper")}</h2><p class="section-intro">${pickR("这里直接读取 Paper Acceptance append-only ledger。科学状态、论文质量状态、新增的 8 门投稿准备状态和人工提交状态分开显示，避免把“科学上 ready”“论文工件完整”“已经可以由人投稿”混成一个 READY 标签。","This view projects the append-only Paper Acceptance ledgers directly. Scientific state, paper-quality state, the new eight-gate preparation state, and human submission state are shown separately so one READY label cannot conflate them.")}</p></div><strong>${summary.submission_ready||0}/${summary.papers||0}<span>${pickR("已到 SUBMISSION_READY","at SUBMISSION_READY")}</span></strong></div><div class="current-research-stats"><div class="stat-started"><b>${summary.submission_ready||0}</b><span>${pickR("SUBMISSION_READY","SUBMISSION_READY")}</span></div><div class="stat-pending"><b>${summary.targeted_repair||0}</b><span>${pickR("TARGETED_REPAIR","TARGETED_REPAIR")}</span></div><div><b>${summary.preparation_pass||0}</b><span>${pickR("新 8 门已迁移 PASS","new 8-gate migrations PASS")}</span></div><div class="stat-pending"><b>${summary.preparation_blocked||0}</b><span>${pickR("Preparation BLOCKED","Preparation BLOCKED")}</span></div><div class="stat-pending"><b>${summary.legacy_ready_needs_preparation_migration||0}</b><span>${pickR("legacy ready 待迁移","legacy ready awaiting migration")}</span></div><div><b>${summary.machine_frozen_candidates||0}</b><span>${pickR("机器候选版本已冻结","machine candidates frozen")}</span></div><div class="stat-pending"><b>${summary.human_submission_signoff_pending||0}</b><span>${pickR("等待人工投稿签字","awaiting human submission signoff")}</span></div></div><div class="reader-rule"><b>${pickR("状态解释","How to read this")}</b><span>${pickR("Paper Preparation migration 只增加审计工件，不会倒写旧合同，也不会把 support failure 变成 scientific negative。只有 human authority 能进入真实 SUBMITTED。","Paper Preparation migration adds audit artifacts only. It never rewrites legacy contracts or turns support failures into scientific negatives. Only human authority may enter the actual SUBMITTED state.")}</span></div></section>`;
    return `${intro}${papers.map(paperCard).join("")}`;
  };
})();
