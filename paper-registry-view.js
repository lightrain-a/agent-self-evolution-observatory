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
  const fmtBytes = (value) => { const n=Number(value||0); if(n>=1024*1024) return `${(n/1024/1024).toFixed(2)} MB`; if(n>=1024) return `${(n/1024).toFixed(1)} KB`; return `${n} B`; };
  const handoffChecklistLabel = (value) => {
    const zh={
      "confirm complete author list and OpenReview profiles":"确认完整作者名单，并逐一确认 OpenReview profile / email / affiliation。",
      "confirm author quota and reciprocal-reviewing obligations":"确认作者投稿配额与 reciprocal reviewing 义务。",
      "confirm dual-submission compliance":"确认不存在违反 venue policy 的实质相同稿件并行投稿。",
      "acknowledge ICLR Code of Ethics":"所有作者确认 ICLR Code of Ethics / Conduct 要求。",
      "review and approve mandatory AI-use disclosure":"所有作者审阅并批准强制 AI-use disclosure。",
      "verify final PDF/source/supplement hashes immediately before upload":"上传前最后一次核对 PDF / source / supplement 的 SHA256。",
      "confirm title and abstract used for reviewer bidding are the intended final submission metadata":"确认用于 reviewer bidding 的标题与摘要就是计划提交的正式 metadata。",
      "confirm every author accepts responsibility for the final manuscript and AI-assisted artifacts":"确认每位作者对最终稿及 AI-assisted artifacts 承担责任。",
      "recompute and compare every frozen artifact SHA256 immediately before upload":"真实上传前重新计算并逐项比对所有冻结工件 SHA256。",
    };
    return language==="zh"?(zh[value]||value):value;
  };
  const handoffDetails = (handoff) => {
    if(handoff.status!=="MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED") return "";
    const artifacts=(handoff.artifacts||[]).map(item=>`<tr><td>${e(item.label)}</td><td><code>${e(item.filename)}</code></td><td>${e(fmtBytes(item.bytes))}</td><td><code>${e(String(item.sha256||"").slice(0,16))}</code></td></tr>`).join("");
    const checks=(handoff.human_checklist||[]).map(item=>`<li>☐ ${e(handoffChecklistLabel(item))}</li>`).join("");
    return `<details class="paper-registry-handoff"><summary>${pickR("展开作者投稿交接清单","Open human submission handoff")}</summary><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${pickR("工件","Artifact")}</th><th>${pickR("文件","File")}</th><th>${pickR("大小","Size")}</th><th>SHA256</th></tr></thead><tbody>${artifacts}</tbody></table></div><div class="reader-rule"><b>${pickR("作者逐项确认","Human confirmation")}</b><ul>${checks}</ul></div><div class="current-status-rule"><b>${pickR("上传硬规则","Upload hard rule")}</b><span>${pickR("任何文件 SHA 不一致或 freeze stale，立即撤回当前 handoff；重新 freeze + handoff 后才能上传。","Any hash mismatch or stale freeze revokes this handoff; re-freeze and rebuild the handoff before upload.")}</span></div></details>`;
  };
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
    const prep=paper.paper_preparation||{}, freeze=paper.submission_freeze||{}, handoff=paper.submission_handoff||{}, signoff=paper.human_signoff||{}, gates=paper.gates||{}, layers=paper.layers||{};
    const id=`paper-${String(paper.paper_id||index).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")}`;
    const ready=paper.current_state==="SUBMISSION_READY";
    const gateRows=[
      ["Claim Audit",gates.claim_audit],
      ["Manuscript CI",gates.manuscript_ci],
      ["Prebuttal",gates.prebuttal],
      ["Submission Readiness",gates.submission_readiness],
    ].map(([name,ok])=>`<tr><td>${e(name)}</td><td>${pill(ok?"PASS":"HOLD",ok?"PASS":"—")}</td></tr>`).join("");
    const boundary=repairBoundary(paper);
    let nextStep;
    if(!ready) nextStep=boundary?pickR("当前 realization 已停在 support + identification boundary。只有下方冻结的 reopen condition 成立后才允许重开；不能继续给同一批 pair 加样本或改门槛。","This realization is held at a support + identification boundary. It may reopen only when one of the frozen conditions below is satisfied; the same pairs cannot receive more samples and the gates cannot be relaxed."):pickR("继续当前论文修复；Paper Preparation 不拥有改变科学结论或授权实验的权限。","Continue paper repair. Paper Preparation has no authority to change science or authorize experiments.");
    else if(!prep.pass) nextStep=prep.status==="BLOCKED"?pickR("Paper Acceptance 已到 SUBMISSION_READY，但新准备协议明确阻断 human handoff；按上面的 blocker 修复，不自动开新实验。","Paper Acceptance is SUBMISSION_READY, but the preparation protocol explicitly blocks human handoff; repair the blockers above without automatically authorizing new experiments."):pickR("论文是 legacy SUBMISSION_READY；补做新 Paper Preparation migration。","This is legacy SUBMISSION_READY; migrate the new Paper Preparation protocol.");
    else if(freeze.status==="MACHINE_FREEZE_STALE") nextStep=pickR("冻结后的投稿字节已经漂移；机器交接自动撤回。重新核验当前 PDF/source/supplement 后生成新的 freeze checkpoint。","Frozen submission bytes have drifted, so machine handoff is automatically revoked. Re-verify the current PDF/source/supplement and create a new freeze checkpoint.");
    else if(freeze.status!=="MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING") nextStep=pickR("Paper Preparation 已通过；先生成 pre-submission freeze checkpoint。","Paper Preparation passed; create a pre-submission freeze checkpoint first.");
    else if(handoff.status==="MACHINE_HANDOFF_STALE") nextStep=pickR("Freeze 仍有效，但作者交接包已与当前 freeze 不一致；重建 handoff packet 后再请求人工确认。","The freeze is current, but the author handoff packet no longer matches it. Rebuild the handoff packet before requesting human confirmation.");
    else if(handoff.status!=="MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED") nextStep=pickR("机器版本已冻结；生成与该 freeze SHA 精确绑定的作者交接包。","The machine candidate is frozen; build the author handoff packet bound exactly to this freeze SHA.");
    else if(signoff.status==="HUMAN_SIGNOFF_STALE") nextStep=pickR("旧的人类签字已与当前 handoff/freeze 脱钩；作者必须基于当前 SHA 重新逐项确认。","The previous human signoff is stale relative to the current handoff/freeze; authors must confirm again against the current SHAs.");
    else if(signoff.status==="HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING") nextStep=pickR("作者签字已闭合，但论文仍未投稿；下一步必须是独立、显式的人类 OpenReview 上传动作，并记录真实 submission receipt。","Human signoff is complete, but the paper is still not submitted. The next step is a separate explicit human OpenReview upload and a real submission receipt.");
    else nextStep=pickR("机器交接包已固定；现在由作者逐项确认作者名单/OpenReview/双投/伦理/AI-use 与最终文件 SHA。系统不会代替作者打勾，也不会自动投稿。","The machine handoff packet is fixed. Human authors now confirm authors/OpenReview/dual-submission/ethics/AI-use and final file hashes. The system will neither tick these boxes nor submit automatically.");
    return `<section class="panel paper-registry-paper" data-paper-id="${e(paper.paper_id)}"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER ${String(index+1).padStart(2,"0")} · ${e(paper.paper_id)}</div><h2 id="${e(id)}">${e(paper.title)}</h2><p class="section-intro">${e(paper.central_question||pickR("canonical contract 未填写 central question","central question unavailable in canonical contract"))}</p></div>${pill(paper.current_state, paper.current_state)}</div><div class="current-experiment-grid paper-registry-layers">${Object.entries(layers).map(([key,value])=>layerLabel(key,value)).join("")}</div><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${pickR("已有 Paper Acceptance 门","Existing Paper Acceptance gate")}</th><th>${pickR("状态","Status")}</th></tr></thead><tbody>${gateRows}</tbody></table></div><div class="reader-metrics"><div><b>${paper.supported_claims||0}</b><span>${pickR("冻结支持主张","frozen supported claims")}</span></div><div><b>${paper.active_unrefuted_claims||0}</b><span>${pickR("活跃未反驳主张","active unrefuted claims")}</span></div><div><b>${paper.ledger_summary?.mock_reviews||0}</b><span>${pickR("Mock PC reviews","Mock PC reviews")}</span></div><div><b>${paper.ledger_events||0}</b><span>${pickR("append-only events","append-only events")}</span></div></div>${boundary}<h3>${pickR("Paper Preparation Protocol · 8 个投稿准备门","Paper Preparation Protocol · eight submission-preparation gates")}</h3>${prepGrid(paper)}${freeze.status==="MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING"?`<div class="current-status-rule"><b>${pickR("Pre-Submission Freeze · 已冻结机器候选版本","Pre-Submission Freeze · machine candidate frozen")}</b><span>${pickR("Freeze SHA","Freeze SHA")}: <code>${e(String(freeze.freeze_sha256||"").slice(0,16))}</code> · ${freeze.frozen_artifacts||0} ${pickR("个上传工件已绑定。任何后续字节变化都必须产生新的 freeze checkpoint。","upload artifacts are bound. Any later byte change must create a new freeze checkpoint.")}</span></div>`:""}${handoff.status==="MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED"?`<div class="current-status-rule"><b>${pickR("Human Submission Handoff · 机器交接包已固定","Human Submission Handoff · machine packet fixed")}</b><span>${pickR("Handoff SHA","Handoff SHA")}: <code>${e(String(handoff.handoff_sha256||"").slice(0,16))}</code> · ${handoff.frozen_artifacts||0} ${pickR("个冻结上传工件已写入作者核对包。当前仍为 PENDING_HUMAN，不是 SUBMITTED。","frozen upload artifacts are listed in the author handoff. Status remains PENDING_HUMAN, not SUBMITTED.")}</span></div>`:""}${handoffDetails(handoff)}${handoff.status==="MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED"?`<div class="current-status-rule"><b>${pickR("Human Signoff","Human Signoff")}</b><span>${signoff.status==="HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING"?`${pill("PASS",pickR("人工确认完成","HUMAN SIGNOFF COMPLETE"))} · ${pickR("Signoff SHA","Signoff SHA")}: <code>${e(String(signoff.signoff_sha256||"").slice(0,16))}</code> · ${pickR("真实投稿仍未执行。","Actual submission has still not been performed.")}`:`${pill("PENDING",pickR("等待作者确认","PENDING HUMAN"))} · ${(handoff.human_checklist||[]).length} ${pickR("项必须由人逐项确认；系统不能自动完成。","items require explicit human confirmation and cannot be completed automatically.")}`}</span></div>`:""}<div class="current-status-rule"><b>${pickR("当前下一步","Current next step")}</b><span>${nextStep}</span></div><small>${pickR("Canonical contract SHA", "Canonical contract SHA")}: <code>${e(String(paper.contract_sha256||"").slice(0,16))}</code>${prep.receipt_sha256?` · ${pickR("Preparation receipt","Preparation receipt")}: <code>${e(prep.receipt_sha256.slice(0,16))}</code>`:""}</small></section>`;
  };

  window.renderPaperRegistryOverview = function renderPaperRegistryOverview() {
    const state=window.PAPER_REGISTRY_STATE||{}, summary=state.summary||{}, papers=state.papers||[];
    if(!papers.length) return "";
    const intro=`<section class="panel paper-registry-hero" id="paper-registry"><div class="idea-panel-heading"><div><div class="eyebrow">PAPER REGISTRY · CANONICAL LEDGER PROJECTION</div><h2 data-toc="false">${pickR("现在不是一篇“选中论文”，而是 "+(summary.papers||papers.length)+" 篇 canonical paper 的统一状态表","This is now a registry of "+(summary.papers||papers.length)+" canonical papers, not a single selected paper")}</h2><p class="section-intro">${pickR("这里直接读取 Paper Acceptance append-only ledger。科学状态、论文质量状态、新增的 8 门投稿准备状态和人工提交状态分开显示，避免把“科学上 ready”“论文工件完整”“已经可以由人投稿”混成一个 READY 标签。","This view projects the append-only Paper Acceptance ledgers directly. Scientific state, paper-quality state, the new eight-gate preparation state, and human submission state are shown separately so one READY label cannot conflate them.")}</p></div><strong>${summary.submission_ready||0}/${summary.papers||0}<span>${pickR("已到 SUBMISSION_READY","at SUBMISSION_READY")}</span></strong></div><div class="current-research-stats"><div class="stat-started"><b>${summary.submission_ready||0}</b><span>${pickR("SUBMISSION_READY","SUBMISSION_READY")}</span></div><div class="stat-pending"><b>${summary.targeted_repair||0}</b><span>${pickR("TARGETED_REPAIR","TARGETED_REPAIR")}</span></div><div><b>${summary.preparation_pass||0}</b><span>${pickR("新 8 门已迁移 PASS","new 8-gate migrations PASS")}</span></div><div class="stat-pending"><b>${summary.preparation_blocked||0}</b><span>${pickR("Preparation BLOCKED","Preparation BLOCKED")}</span></div><div class="stat-pending"><b>${summary.legacy_ready_needs_preparation_migration||0}</b><span>${pickR("legacy ready 待迁移","legacy ready awaiting migration")}</span></div><div><b>${summary.machine_frozen_candidates||0}</b><span>${pickR("机器候选版本已冻结","machine candidates frozen")}</span></div><div class="stat-pending"><b>${summary.machine_freeze_stale||0}</b><span>${pickR("Freeze 漂移","stale freezes")}</span></div><div><b>${summary.machine_handoff_ready||0}</b><span>${pickR("机器交接包已固定","machine handoff packets ready")}</span></div><div class="stat-pending"><b>${summary.machine_handoff_stale||0}</b><span>${pickR("Handoff 漂移","stale handoffs")}</span></div><div class="stat-pending"><b>${summary.human_submission_signoff_pending||0}</b><span>${pickR("等待作者逐项确认","awaiting human confirmation")}</span></div><div><b>${summary.human_signoff_complete||0}</b><span>${pickR("人工签字完成","human signoffs complete")}</span></div><div><b>${summary.submitted||0}</b><span>${pickR("真实已投稿","actually submitted")}</span></div></div><div class="reader-rule"><b>${pickR("状态解释","How to read this")}</b><span>${pickR("Paper Preparation migration 只增加审计工件，不会倒写旧合同，也不会把 support failure 变成 scientific negative。只有 human authority 能进入真实 SUBMITTED。","Paper Preparation migration adds audit artifacts only. It never rewrites legacy contracts or turns support failures into scientific negatives. Only human authority may enter the actual SUBMITTED state.")}</span></div></section>`;
    return `${intro}${papers.map(paperCard).join("")}`;
  };
})();
