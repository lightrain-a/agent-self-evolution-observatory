(() => {
  const state = () => window.E2_R17_FRONTEND_STATUS || {};
  const pick = (zh, en) => language === "zh" ? zh : en;
  const text = (obj, key) => language === "zh" ? (obj?.[`${key}_zh`] ?? obj?.[key]?.zh ?? obj?.[key] ?? "") : (obj?.[`${key}_en`] ?? obj?.[key]?.en ?? obj?.[key] ?? "");
  const hash12 = value => String(value || "--").slice(0,12);
  const tone = status => {
    const s=String(status||"").toUpperCase();
    if(s.includes("COMPLETE") && !s.includes("INCONCLUSIVE")) return "pass";
    if(s.includes("PASS")) return "pass";
    if(s.includes("INCONCLUSIVE") || s.includes("NEXT") || s.includes("NO_NEW_DATA") || s.includes("CONDITIONAL")) return "check";
    if(s.includes("LOCKED") || s.includes("NOT_AUTHORIZED") || s.includes("NOT_FROZEN")) return "planned";
    if(s.includes("FAIL") || s.includes("STOP")) return "fail";
    return "planned";
  };
  const badge = (status,label) => `<span class="experiment-status-badge status-${tone(status)}">${esc(label || status || "--")}</span>`;
  const statusLabel = status => {
    if(language!=="zh") return String(status||"").replaceAll("_"," ");
    return ({
      COMPLETE:"已完成",
      COMPLETE_INCONCLUSIVE:"已完成 · 全局收益未建立",
      NEXT_NOT_AUTHORIZED:"下一门禁 · 未授权",
      NEXT_EXECUTABLE:"下一门禁 · 可执行资格检查",
      PLANNED_LOCKED:"已冻结 · 未授权",
      CONDITIONAL_LOCKED:"条件开放 · 当前锁定",
      NO_NEW_DATA:"零新增数据 · 结果判定门",
      CONDITIONAL_NOT_FROZEN:"条件开放 · Public packet 未冻结"
    })[status] || String(status||"");
  };
  const authoritySummary = s => {
    const a=s.authority||{};
    const values=[a.stage_a,a.stage_b,a.public_p1];
    const enabled=values.filter(Boolean).length;
    return {enabled,total:values.length};
  };
  const stageCard = row => `<article class="e2r17-stage-card status-${tone(row.status)}"><header><span>${esc(row.id)}</span>${badge(row.status,statusLabel(row.status))}</header><h3 data-toc="false">${esc(text(row,"title"))}</h3><p class="e2r17-stage-scale">${esc(text(row,"scale"))}</p><p>${esc(text(row,"gate"))}</p></article>`;
  const evidenceCard = row => `<article class="e2r17-evidence-card status-${tone(row.status)}"><header><span>${esc(row.id)}</span>${badge(row.status,statusLabel(row.status))}</header><h3 data-toc="false">${esc(text(row,"title"))}</h3><p class="e2r17-stage-scale">${esc(text(row,"metrics"))}</p><p>${esc(text(row,"claim"))}</p></article>`;
  const rqStrip = s => `<div class="e2r17-rq-strip">${(s.rq||[]).map(row=>`<span><b>${esc(row.id)}</b>${esc(language==="zh"?row.zh:row.en)}</span>`).join("")}</div>`;
  const authorityBlock = s => {
    const a=s.authority||{}, x=authoritySummary(s);
    const identityState=a.fresh_identity_called?pick("已执行","executed"):(a.fresh_identity_qualification_permitted?pick("下一条可执行资格门","next executable qualification gate"):pick("关闭","closed"));
    return `<div class="e2r17-authority"><div><b>${pick("当前科学权限","Current scientific authorities")}</b><strong>${x.enabled}/${x.total}</strong></div><span>${pick(`identity qualification=${identityState} · Stage A=${a.stage_a?"已授权":"未授权"} · Stage B=${a.stage_b?"已授权":"未授权"} · Public P1=${a.public_p1?"已授权":"未授权"} · baseline execution=${a.baseline_execution?"已执行":"未执行"}`,`identity qualification=${identityState} · Stage A=${a.stage_a?"authorized":"not authorized"} · Stage B=${a.stage_b?"authorized":"not authorized"} · Public P1=${a.public_p1?"authorized":"not authorized"} · baseline execution=${a.baseline_execution?"executed":"not executed"}`)}</span></div>`;
  };
  const publicPanel = s => {
    const p=s.public_p1||{};
    const baselineRows=[...(p.anchors||[]).map(x=>["Anchor",x]),...(p.closest_baselines||[]).map(x=>["Closest",x])];
    return `<section class="e2r17-public-lane"><header><div><span>C · PUBLIC P1</span><h3 data-toc="false">${esc(p.substrate||"SpreadsheetBench Verified-400")}</h3><p>${esc(text(p,"purpose"))}</p></div>${badge(p.status,statusLabel(p.status))}</header><div class="e2r17-public-grid"><article><b>${pick("进入条件","Entry condition")}</b><p>${esc(text(p,"entry"))}</p><small>${pick("Exact public IDs 当前未冻结；任何 public outcome 前必须固定。","Exact public IDs are not yet frozen and must be pinned before any public outcome.")}</small></article><article><b>${pick("统一 split / 主模型","Unified split / primary model")}</b><p><strong>${esc(p.split_policy||"")}</strong></p><p>${esc(text(p,"primary_model"))}</p></article><article><b>${pick("一次完成两件事","One lane, two purposes")}</b><p>${pick("Natural transport + closest-method baseline comparison 共用同一 split、actor/updater role、harness、evaluator 与 heldout panel。","Natural transport and closest-method comparison share the same split, actor/updater role, harness, evaluator, and heldout panel.")}</p></article></div><div class="advisor-table-scroll"><table class="matrix e2r17-baseline-table"><thead><tr><th>${pick("层级","Type")}</th><th>Baseline</th><th>${pick("为什么需要","Why it is there")}</th></tr></thead><tbody>${baselineRows.map(([kind,name])=>`<tr><td>${esc(kind)}</td><td><strong>${esc(name)}</strong></td><td>${esc(kind==="Anchor"?pick("能力 / parent / tied-projection / fixed-alternative 锚点","Capability / parent / tied-projection / fixed-alternative anchor"):pick("与当前 self-evolving skill 文献做统一 harness 公平比较","Fair unified-harness comparison against current self-evolving-skill methods"))}</td></tr>`).join("")}<tr><td>Contrastive</td><td><strong>${pick("Trace2Skill（优先）或 SkillCAT-style","Trace2Skill (preferred) or SkillCAT-style")}</strong></td><td>${esc(text(p,"contrastive_baseline"))}</td></tr></tbody></table></div><div class="e2r17-public-footer"><span><b>${pick("统一 heldout","Unified heldout")}</b>${esc(text(p,"evaluation"))}</span><span><b>${pick("Transport STOP","Transport STOP")}</b>${esc(text(p,"transport_stop"))}</span></div></section>`;
  };
  const optionalPanel = s => `<details class="e2r17-optional"><summary><div><b>${pick("D · 可选 robustness / claim expansion","D · Optional robustness / claim expansion")}</b><span>${pick("只有 required ladder 完整后才考虑；不能 rescue earlier gate failure。","Consider only after the required ladder is complete; none may rescue an earlier gate failure.")}</span></div><strong>${(s.optional_after_required||[]).length}</strong></summary><div>${(s.optional_after_required||[]).map(row=>`<article><span>${esc(row.id)}</span><p>${esc(language==="zh"?row.zh:row.en)}</p></article>`).join("")}</div></details>`;
  const workloadPanel = s => {
    const w=s.workload_rule||{};
    const rules=language==="zh"?w.admit_if_zh:w.admit_if_en;
    return `<aside class="e2r17-workload"><header><span>${pick("有效工作量原则","EFFECTIVE WORKLOAD")}</span>${badge(w.verdict,pick("Controlled workload 已够","Controlled workload sufficient"))}</header><p>${esc(language==="zh"?w.zh:w.en)}</p><ul>${(rules||[]).map(x=>`<li>${esc(x)}</li>`).join("")}</ul></aside>`;
  };

  window.renderE2R17ExperimentPanel = function(){
    const s=state(); if(!s.project_track)return "";
    return `<section class="panel e2r17-project-panel" id="e2-r17-current-experiment"><header class="e2r17-project-head"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("当前 Project Track · 实验执行图","CURRENT PROJECT TRACK · EXPERIMENT EXECUTION MAP")} · ${esc(s.as_of_date||"")}</div><h2 data-toc="false">${esc(text(s,"title"))}</h2><p>${esc(text(s,"scientific_object"))}</p></div>${badge("NEXT_EXECUTABLE",pick("Identity qualification next · Stage A/B/Public P1 locked","Identity qualification next · Stage A/B/Public P1 locked"))}</header>${authorityBlock(s)}<div class="e2r17-next-gate"><b>${pick("下一条真正可执行门禁","Next executable gate")}</b><span>${esc(language==="zh"?s.next_gate?.zh:s.next_gate?.en)}</span></div>${rqStrip(s)}<h3 class="e2r17-section-title" data-toc="false">${pick("A · 已完成证据：不再重复跑","A · Completed evidence: do not rerun")}</h3><div class="e2r17-evidence-grid">${(s.completed_evidence||[]).map(evidenceCard).join("")}</div><h3 class="e2r17-section-title" data-toc="false">${pick("B · 必跑 Controlled V3：每一层都有硬门","B · Mandatory controlled V3: every stage has a hard gate")}</h3><div class="e2r17-stage-grid">${(s.mandatory_controlled||[]).map(stageCard).join("")}</div>${publicPanel(s)}${optionalPanel(s)}${workloadPanel(s)}<footer class="e2r17-provenance"><span>${pick("Frozen R2","Frozen R2")} · commit ${esc(hash12(s.frozen_scientific_r2?.commit))}… · contract ${esc(hash12(s.frozen_scientific_r2?.contract_sha256))}… · preflight ${esc(hash12(s.frozen_scientific_r2?.preflight_sha256))}…</span><span>${pick("前端更新不改变 R2 scientific object；identity qualification 仍是已允许的下一条非科学资格门，Stage-A / Stage-B / Public-P1 科学权限仍为 false。","This frontend update does not change the R2 scientific object; identity qualification remains the permitted next non-scientific qualification gate, while Stage-A / Stage-B / Public-P1 scientific authority remains false.")}</span></footer></section>`;
  };

  window.renderE2R17PortfolioAddendum = function(){
    const s=state(); if(!s.project_track)return "";
    const a=authoritySummary(s), b2=(s.mandatory_controlled||[]).find(x=>x.id==="B2")||{}, p=s.public_p1||{};
    return `<section class="portfolio-decision-console e2r17-portfolio-addendum" id="e2-r17-project-addendum"><header class="portfolio-decision-head"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("PROJECT TRACK ADDENDUM · 不覆盖 A–G canonical ledger","PROJECT TRACK ADDENDUM · DOES NOT OVERRIDE THE A–G CANONICAL LEDGER")}</div><h2 data-toc="false">${esc(text(s,"title"))}</h2><p>${esc(text(s,"scientific_object"))}</p></div><nav><a href="experiments.html#e2-r17-current-experiment">${pick("打开完整实验执行图 →","Open full experiment map →")}</a></nav></header><div class="portfolio-decision-metrics e2r17-portfolio-metrics"><span><b>2</b>${pick("已完成证据块","completed evidence blocks")}</span><span><b>4</b>${pick("Controlled V3 门禁","controlled V3 gates")}</span><span><b>${a.enabled}/${a.total}</b>${pick("Stage A/B/Public P1 科学权限","Stage A/B/Public P1 scientific authorities")}</span><span><b>1</b>${pick("计划中的 public lane","planned public lane")}</span></div><div class="e2r17-portfolio-summary"><article><b>${pick("论文身份","Paper identity")}</b><strong>${esc(s.paper_identity)}</strong><p>${pick("核心不是 failure-learning heuristic，而是 exact-same-pool、acting-fixed 的 serving→persistent-learning projection interface 因果识别。","The core is not a failure-learning heuristic, but exact-same-pool, acting-fixed causal identification of the serving→persistent-learning projection interface.")}</p></article><article><b>${pick("Controlled 主实验","Controlled main experiment")}</b>${badge(b2.status,statusLabel(b2.status))}<p>${esc(text(b2,"scale"))}</p></article><article><b>${pick("论文完整性缺口","Paper-completion gap")}</b>${badge(p.status,statusLabel(p.status))}<p>${pick(`${p.substrate||"SpreadsheetBench Verified-400"} 将 natural transport 与 closest-method baseline 主表合并成一条 public lane。`,`${p.substrate||"SpreadsheetBench Verified-400"} combines natural transport and the closest-method baseline table in one public lane.`)}</p></article></div><div class="e2r17-next-gate"><b>${pick("当前唯一下一步","Only current next step")}</b><span>${esc(language==="zh"?s.next_gate?.zh:s.next_gate?.en)}</span></div></section>`;
  };

  window.renderE2R17PaperAddendum = function(){
    const s=state(); if(!s.project_track)return "";
    return `<section class="paper-detail-section e2r17-paper-addendum" id="paper-e2-r17-project-track" data-paper-toc-root><header class="paper-detail-header"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("PROJECT PAPER ADDENDUM · 尚未写入 canonical PaperRegistry","PROJECT PAPER ADDENDUM · NOT YET IN THE CANONICAL PAPERREGISTRY")}</div><h2>${esc(text(s,"title"))}</h2><p>${esc(text(s,"subtitle"))}</p></div>${badge("NEXT_EXECUTABLE",pick("Identity gate next · scientific authority closed","Identity gate next · scientific authority closed"))}</header><div class="e2r17-paper-story"><article><b>${pick("一句话科学对象","Scientific object")}</b><p>${esc(text(s,"scientific_object"))}</p></article><article><b>${pick("RQ1–RQ5 证据链","RQ1–RQ5 evidence ladder")}</b>${rqStrip(s)}</article><article><b>${pick("当前 claim 边界","Current claim boundary")}</b><p>${pick("全局 MRW benefit 未建立；V3 interaction 尚无 outcome。即使 primary PASS + 5/5 procedural positive，也只能说明在这 5 个预注册 procedural skeleton 上，测试的 alternative learner projection 优于 WIN-C learning，同时 serving 固定；不能写成全局的 “best to learn”。","Global MRW benefit is not established and V3 has no outcome yet. Even primary PASS plus 5/5 positive procedural effects would only show that the tested alternative learner projection beats WIN-C learning on the five preregistered procedural skeletons while serving is fixed; it does not establish a globally 'best to learn' projection.")}</p></article></div><div class="e2r17-paper-links"><a class="link-btn" href="experiments.html#e2-r17-current-experiment">${pick("实验执行图 →","Experiment execution map →")}</a><a class="link-btn" href="paper-ideas.html#e2-r17-project-addendum">${pick("Research Portfolio 项目卡 →","Research Portfolio addendum →")}</a></div><small class="e2r17-paper-boundary">${pick("这是一条 project-level paper track 投影，不会修改现有 STRI / A–G ResearchItem / PaperRegistry 的 canonical 状态。","This is a project-level paper-track projection and does not modify the canonical STRI / A–G ResearchItem / PaperRegistry state.")}</small></section>`;
  };
})();
