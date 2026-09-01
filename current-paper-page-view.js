(()=>{
  const E=(v)=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const isZh=()=>document.documentElement.lang==="zh-CN";
  const T=(v)=>v&&typeof v==="object"?(isZh()?v.zh:v.en)||v.zh||v.en||"":v||"";
  const registryPaper=(paper)=>paper?.registryPaperId?(window.PAPER_REGISTRY?.papers||[]).find(p=>p.paper_id===paper.registryPaperId):null;
  const detailFor=(pageId)=>window.CURRENT_PAPER_DETAILS?.papers?.[pageId]||{};
  const storyFor=(paper)=>paper?.registryPaperId?window.PAPER_STORY_DATA?.papers?.[paper.registryPaperId]||null:null;
  const orderMark=(n)=>["①","②","③","④","⑤","⑥","⑦","⑧","⑨"][Number(n)-1]||String(n||"");
  const paperState=(paper,reg)=>paper.displayState||(reg?(reg.paper_stage||reg.current_state||"PaperRegistry"):(paper.kind==="scientific-object"?"PRE-F0":"WORKING"));
  const kindLabel=(paper)=>{
    if(paper.kind==="registry") return isZh()?"正式 PaperRegistry":"Formal PaperRegistry";
    if(paper.kind==="registry-extension") return isZh()?"正式论文谱系 + 当前扩展":"Formal lineage + current extension";
    if(paper.kind==="scientific-object") return isZh()?"独立科学对象":"Independent scientific object";
    return isZh()?"工作论文":"Working paper";
  };
  const statusBadge=(paper,reg)=>`<span class="cpp-badge cpp-badge-strong">${E(paperState(paper,reg))}</span><span class="cpp-badge">${E(kindLabel(paper))}</span>`;
  const list=(rows,klass="")=>`<ul class="cpp-list ${klass}">${(rows||[]).map(x=>`<li>${E(T(x))}</li>`).join("")}</ul>`;
  const mechanism=(paper)=>`<div class="cpp-flow">${(paper.mechanism||[]).map((s,i)=>`<article class="cpp-flow-step"><span>${E(s.n)}</span><strong>${E(isZh()?s.zh:s.en)}</strong><p>${E(isZh()?s.dzh:s.den)}</p></article>${i<(paper.mechanism.length-1)?'<i aria-hidden="true">→</i>':''}`).join("")}</div>`;
  const metrics=(paper)=>`<div class="cpp-metrics">${(paper.experiment?.metrics||[]).map(m=>`<div><span>${E(T(m.k))}</span><strong>${E(m.v)}</strong></div>`).join("")}</div>`;
  const snapshot=(detail)=>detail.snapshot?.length?`<section class="cpp-snapshot" id="paper-snapshot"><div class="cpp-snapshot-grid">${detail.snapshot.map(x=>`<article><span>${E(T(x.k))}</span><strong>${E(T(x.v))}</strong></article>`).join("")}</div></section>`:"";
  const contract=(detail)=>detail.contract?.length?`<div class="cpp-contract-grid">${detail.contract.map(x=>`<article><span>${E(T(x.k))}</span><strong>${E(T(x.v))}</strong><p>${E(T(x.why))}</p></article>`).join("")}</div>`:"";
  const arms=(detail)=>detail.arms?.length?`<div class="cpp-arm-grid">${detail.arms.map(x=>`<article><header><b>${E(x.name)}</b><span>${E(T(x.kind))}</span></header><p><strong>${isZh()?"变化":"Changed"} · </strong>${E(T(x.changes))}</p><p><strong>${isZh()?"保持固定":"Fixed"} · </strong>${E(T(x.fixed))}</p><small>${E(T(x.purpose))}</small></article>`).join("")}</div>`:"";
  const analysisPlan=(detail)=>detail.analysis?.length?`<div class="cpp-analysis-grid">${detail.analysis.map(x=>`<article><b>${E(T(x.name))}</b><p>${E(T(x.detail))}</p></article>`).join("")}</div>`:"";
  const interpretation=(detail)=>detail.interpretation?`<div class="cpp-interpretation"><section><b>${isZh()?"这组证据真正支持什么":"What the evidence supports"}</b>${list(detail.interpretation.proves||[],"good")}</section><section><b>${isZh()?"明确没有证明什么":"What it does not establish"}</b>${list(detail.interpretation.doesNot||[],"boundary")}</section>${detail.interpretation.importance?`<aside><b>${isZh()?"为什么这个结果重要":"Why this matters"}</b><p>${E(T(detail.interpretation.importance))}</p></aside>`:""}</div>`:"";
  const lineage=(detail)=>detail.lineage?.length?`<div class="cpp-lineage">${detail.lineage.map((x,i)=>`<article><span>${E(x.stage||String(i+1).padStart(2,"0"))}</span><div><b>${E(T(x.title))}</b><p>${E(T(x.body))}</p></div></article>`).join("")}</div>`:"";
  const replayNotes=(detail)=>detail.replayNotes?.length?`<section class="panel cpp-replay" id="replay-notes"><div class="cpp-section-kicker">${isZh()?"复盘注意":"REPLAY NOTES"}</div><h2>${isZh()?"以后回看这篇论文时最容易混淆的点":"What future readers should not conflate"}</h2>${list(detail.replayNotes,"boundary")}</section>`:"";
  const modelData=(detail)=>{
    const cards=(rows,type)=>(rows||[]).map(x=>`<article class="cpp-resource-card"><span>${E(type)}</span><strong>${E(x.name)}</strong><b>${E(T(x.role))}</b><p>${E(T(x.note))}</p></article>`).join("");
    return `<div class="cpp-resource-columns"><section><h3>${isZh()?"实验模型 / 系统":"Models / systems"}</h3><div class="cpp-resource-grid">${cards(detail.models,isZh()?"模型":"MODEL")}</div></section><section><h3>${isZh()?"数据集 / 实验环境":"Datasets / environments"}</h3><div class="cpp-resource-grid">${cards(detail.datasets,isZh()?"数据":"DATA")}</div></section></div>`;
  };
  const problemOrigin=(paper,story)=>{
    if(!story) return "";
    const blocks=[
      [isZh()?"现实场景":"Scene",T(story.scene)],
      [isZh()?"为什么值得研究":"Why it matters",T(story.value)],
      [isZh()?"典型失败例子":"Concrete failure",T(story.failure_example)],
      [isZh()?"真正缺的科学对象":"Missing scientific object",T(story.missing_scientific_object)]
    ].filter(([,v])=>v);
    return `<section class="panel cpp-origin" id="problem-origin"><div class="cpp-section-kicker">${isZh()?"问题来源":"Problem origin"}</div><h2>${isZh()?"为什么会演变成今天这个论文问题":"Why this became the current scientific question"}</h2><div class="cpp-origin-grid">${blocks.map(([k,v])=>`<article><b>${E(k)}</b><p>${E(v)}</p></article>`).join("")}</div></section>`;
  };
  const storyExperiments=(story)=>{
    if(!story?.experiments?.length) return "";
    return `<div class="cpp-rq-list"><h3>${isZh()?"冻结 RQ / 对照 / 当前答案":"Frozen RQs / controls / current answers"}</h3>${story.experiments.map(x=>`<article><span>${E(x.rq||"RQ")}</span><div><b>${E(isZh()?x.q_zh:x.q_en)}</b><p><strong>${isZh()?"对照：":"Control: "}</strong>${E(isZh()?x.baseline_zh:x.baseline_en)}</p><p><strong>${isZh()?"结果：":"Answer: "}</strong>${E(isZh()?x.answer_zh:x.answer_en)}</p></div></article>`).join("")}</div>`;
  };
  const storyText=(row,key)=>{
    if(!row)return "";
    const zh=row[`${key}_zh`],en=row[`${key}_en`];
    if(zh!==undefined||en!==undefined)return isZh()?(zh??en??""):(en??zh??"");
    return T(row[key]);
  };
  const venueYearTag=(work)=>{
    const venue=String(work?.venue||"").trim();
    const year=String(work?.year||"").trim();
    const shortYear=year.length>=2?year.slice(-2):year;
    if(!venue&&!shortYear)return "";
    return `${venue||"Year"}${shortYear?`'${shortYear}`:""}`;
  };
  const relatedWorkComparison=(story)=>{
    if(!story?.approaches?.length)return "";
    return `<section class="panel cpp-related-work" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"现有工作对比":"RELATED WORK COMPARISON"}</div><h2>${isZh()?"现有方法已经做到什么，我们到底还剩什么新东西":"What prior work already solves, and what remains scientifically distinct"}</h2><p class="cpp-design-lead">${isZh()?"这一节完整迁自原 PaperRegistry 的 Paper Story V3。不是只列引用，而是逐个比较：现有范式怎么做、为什么还不能回答我们的科学问题，以及正文必须守住哪条 novelty boundary。":"Migrated from the former PaperRegistry Paper Story V3. It compares what each paradigm does, why it does not answer this paper's exact question, and the novelty boundary the manuscript must preserve."}</p><div class="cpp-related-stack">${story.approaches.map((a,i)=>`<article class="cpp-related-approach"><header><span>${String(i+1).padStart(2,"0")}</span><div><h3>${E(a.name||"")}</h3><p><b>${isZh()?"现有范式：":"Current paradigm: "}</b>${E(storyText(a,"how"))}</p><p><b>${isZh()?"仍然缺什么：":"Why insufficient: "}</b>${E(storyText(a,"problem"))}</p></div></header>${a.closest_work?.length?`<div class="advisor-table-scroll"><table class="matrix cpp-nearest-table"><thead><tr><th>${isZh()?"最近工作":"Closest work"}</th><th>${isZh()?"它解决了什么":"What it solves"}</th><th>${isZh()?"和我们重叠什么":"Overlap"}</th><th>${isZh()?"它没回答什么":"Missing object"}</th><th>${isZh()?"我们必须守住的边界":"Our boundary"}</th></tr></thead><tbody>${a.closest_work.map(w=>`<tr><th><a href="${E(w.url||w.u||"#")}" target="_blank" rel="noopener">${E(w.title||w.t||"")}</a>${venueYearTag(w)?`<span class="cpp-venue-tag">${E(venueYearTag(w))}</span>`:""}<p>${E(T(w.what||w.d))}</p></th><td>${E(T(w.solves))}</td><td>${E(T(w.overlap))}</td><td>${E(T(w.missing))}</td><td>${E(T(w.boundary))}</td></tr>`).join("")}</tbody></table></div>`:""}</article>`).join("")}</div></section>`;
  };
  const fullStoryArchive=(story)=>{
    if(!story)return "";
    const isFormalStory=Boolean(story.paper_archetype||story.thesis||story.research_question);
    const gaps=(story.gaps||[]).map(x=>`<article><b>${E(isZh()?(x.title_zh||x.title_en):(x.title_en||x.title_zh))}</b><p>${E(isZh()?(x.text_zh||x.text_en):(x.text_en||x.text_zh))}</p></article>`).join("");
    const requirements=(story.design_requirements||[]).map(x=>`<li>${E(T(x))}</li>`).join("");
    const predictions=(story.mechanism_predictions||[]).map(x=>`<article><b>${E(isZh()?(x.prediction_zh||x.prediction_en):(x.prediction_en||x.prediction_zh))}</b><p><strong>${isZh()?"如何检验：":"Tested by: "}</strong>${E(x.tested_by||"")}</p></article>`).join("");
    const alternatives=(story.alternative_explanations||[]).map(x=>`<article><b>${E(x.name||"")}</b><p>${E(isZh()?(x.control_zh||x.control_en):(x.control_en||x.control_zh))}</p></article>`).join("");
    const ec=story.evaluation_contract||{};
    const evalRows=[
      [isZh()?"最强对照":"Strongest baseline",isZh()?(ec.strongest_baseline_zh||ec.strongest_baseline_en):(ec.strongest_baseline_en||ec.strongest_baseline_zh)],
      [isZh()?"保持固定":"Held fixed",isZh()?(ec.held_fixed_zh||ec.held_fixed_en):(ec.held_fixed_en||ec.held_fixed_zh)],
      [isZh()?"统计单位":"Unit",isZh()?(ec.unit_zh||ec.unit_en):(ec.unit_en||ec.unit_zh)],
      [isZh()?"成功判定":"Success rule",isZh()?(ec.success_rule_zh||ec.success_rule_en):(ec.success_rule_en||ec.success_rule_zh)]
    ].filter(([,v])=>v).map(([k,v])=>`<article><b>${E(k)}</b><p>${E(v)}</p></article>`).join("");
    const components=(story.components||[]).map(x=>`<article><span>${E(x.solves||"")}</span><b>${E(x.name||"")}</b><p>${E(isZh()?(x.role_zh||x.role_en):(x.role_en||x.role_zh))}</p></article>`).join("");
    const componentEvidence=(story.component_evidence||[]).map(x=>`<tr><th>${E(x.component||"")}</th><td>${E(isZh()?(x.evidence_zh||x.evidence_en):(x.evidence_en||x.evidence_zh))}</td><td>${E(isZh()?(x.meaning_zh||x.meaning_en):(x.meaning_en||x.meaning_zh))}</td></tr>`).join("");
    const mechanismTests=(story.mechanism_tests||[]).map(x=>`<tr><th>${E(x.name||"")}</th><td>${E(isZh()?(x.prediction_zh||x.prediction_en):(x.prediction_en||x.prediction_zh))}</td><td>${E(isZh()?(x.result_zh||x.result_en):(x.result_en||x.result_zh))}</td></tr>`).join("");
    const chain=(story.chain_of_evidence||[]).map(x=>`<tr><th>${E(x.claim||"")}</th><td>${E(x.evidence||"")}</td><td>${E(isZh()?(x.boundary_zh||x.boundary_en):(x.boundary_en||x.boundary_zh))}</td></tr>`).join("");
    const outline=(story.outline||[]).map(x=>`<li>${E(x)}</li>`).join("");
    return `<section class="panel cpp-story-archive" id="paper-story-complete"><div class="cpp-section-kicker">${isFormalStory?`Paper Story V3 · ${isZh()?"完整迁移":"FULL MIGRATION"}`:(isZh()?"研究设计档案 · 工作版":"RESEARCH DOSSIER · WORKING")}</div><h2>${isFormalStory?(isZh()?"原合集页里的完整研究设计档案":"Complete research-design dossier from the former collection page"):(isZh()?"这篇新论文的研究缺口、机制预测与决定性实验":"Research gaps, mechanism predictions, and decisive design for this new paper")}</h2><p class="cpp-design-lead">${E(T(story.motivation)||T(story.thesis)||T(story.why_better)||T(story.interpretation?.importance))}</p>${gaps?`<h3>${isZh()?"研究缺口":"Research gaps"}</h3><div class="cpp-story-grid">${gaps}</div>`:""}${requirements?`<h3>${isZh()?"设计必须满足什么":"Design requirements"}</h3><ul class="cpp-list good">${requirements}</ul>`:""}${predictions?`<h3>${isZh()?"机制预测与可证伪测试":"Mechanism predictions and falsifiers"}</h3><div class="cpp-story-grid">${predictions}</div>`:""}${alternatives?`<h3>${isZh()?"替代解释与控制":"Alternative explanations and controls"}</h3><div class="cpp-story-grid">${alternatives}</div>`:""}${evalRows?`<h3>${isZh()?"完整评测合同":"Evaluation contract"}</h3><div class="cpp-story-grid">${evalRows}</div>`:""}${components?`<h3>${isZh()?"方法组件分别解决什么":"What each component is for"}</h3><div class="cpp-component-grid">${components}</div>`:""}${story.why_better?`<div class="cpp-now"><b>${isZh()?"为什么比普通对比更强":"Why this design is stronger"}</b><p>${E(T(story.why_better))}</p></div>`:""}${componentEvidence?`<h3>${isZh()?"组件证据":"Component evidence"}</h3><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${isZh()?"组件":"Component"}</th><th>${isZh()?"证据":"Evidence"}</th><th>${isZh()?"说明什么":"Meaning"}</th></tr></thead><tbody>${componentEvidence}</tbody></table></div>`:""}${mechanismTests?`<h3>${isZh()?"机制测试":"Mechanism tests"}</h3><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>${isZh()?"测试":"Test"}</th><th>${isZh()?"预测":"Prediction"}</th><th>${isZh()?"当前结果":"Result"}</th></tr></thead><tbody>${mechanismTests}</tbody></table></div>`:""}${story.generalization?`<div class="cpp-generalization"><b>${isZh()?"外部有效性 / 泛化边界":"Generalization boundary"}</b><p>${E(T(story.generalization))}</p></div>`:""}${chain?`<h3>${isZh()?"主张—证据—边界链":"Claim → evidence → boundary"}</h3><div class="advisor-table-scroll"><table class="matrix"><thead><tr><th>Claim</th><th>Evidence</th><th>Boundary</th></tr></thead><tbody>${chain}</tbody></table></div>`:""}${outline?`<h3>${isZh()?"当前论文故事结构":"Current paper outline"}</h3><ol class="cpp-outline">${outline}</ol>`:""}</section>`;
  };
  const proof=(detail)=>`<div class="cpp-proof-grid">${(detail.proof||[]).map(x=>`<article><strong>${E(x.result)}</strong><p>${E(T(x.meaning))}</p></article>`).join("")}</div>`;
  const evolution=(paper,detail)=>{
    const rows=detail.evolution?.length?detail.evolution:(paper.evolution||[]).map(x=>({title:x.t,body:x.b}));
    return `<div class="cpp-evolution cpp-evolution-detailed">${rows.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><strong>${E(T(x.title))}</strong><p>${E(T(x.body))}</p></div></article>`).join("")}</div>`;
  };
  const failureBoundaries=(story)=>{
    if(!story) return "";
    const regimes=(story.failure_regimes||[]).map(x=>T(x)).filter(Boolean);
    const boundary=T(story.boundary);
    if(!regimes.length&&!boundary) return "";
    return `<details class="cpp-story-boundary"><summary>${isZh()?"更严格的实验失败边界 / 未证明项":"Stricter failure regimes / unsupported claims"}</summary>${regimes.length?list(regimes.map(x=>({zh:x,en:x})),"boundary"):""}${boundary?`<p><b>${isZh()?"论文边界：":"Paper boundary: "}</b>${E(boundary)}</p>`:""}</details>`;
  };
  const workingNoveltyAudit=(detail)=>{
    const a=detail?.working_novelty_audit;if(!a)return "";
    const rows=[[isZh()?"最强 novelty attack":"Strongest novelty attack",a.strongest_attack,"attack"],[isZh()?"主动让出":"Surrender",a.surrender,"surrender"],[isZh()?"仍能守住的新轴":"Defended residual",a.defended_residual,"defend"],[isZh()?"决定性实验":"Decisive test",a.decisive_test,"test"],[isZh()?"停止条件":"Stop rule",a.stop_rule,"stop"]];
    return `<section class="panel cpp-working-audit" id="working-novelty-audit"><div class="cpp-working-audit-head"><div><div class="cpp-section-kicker">${isZh()?"工作级创新性审计":"WORKING NOVELTY AUDIT"}</div><h2>${isZh()?"最近工作已经撞到哪里，这篇还剩什么值得做":"What recent work already covers, and what still deserves a decisive test"}</h2></div><span class="cpp-working-risk">${isZh()?"碰撞风险":"collision risk"} · ${E(a.risk||"--")}</span></div><div class="cpp-working-axis"><b>${isZh()?"当前 surviving axis":"Current surviving axis"}</b><p>${E(T(a.surviving_axis))}</p></div><div class="cpp-working-audit-grid">${rows.map(([k,v,c])=>`<article class="${c}"><b>${E(k)}</b><p>${E(T(v))}</p></article>`).join("")}</div><small>${isZh()?"这是一层只读工作审计：不等于正式 PaperRegistry novelty verdict，也不授予 scientific / experiment / GPU / submission authority。":"Read-only working audit: not a formal PaperRegistry novelty verdict and grants no scientific, experiment, GPU, or submission authority."}</small></section>`;
  };
  const registryBox=(paper,reg)=>{
    if(!reg) return `<div class="cpp-registry-note working"><b>${isZh()?"身份说明":"Identity"}</b><p>${E(kindLabel(paper))}。${isZh()?"这是只读研究说明，不会因此创建正式论文编号，也不会授予科学、实验、GPU 或投稿权限。":"This is a read-only research explanation. It does not create a formal publication code or grant scientific, experiment, GPU, or submission authority."}</p></div>`;
    const claimAudit=reg.latest_claim_audit||{}, prep=reg.latest_paper_preparation||{}, prebuttal=reg.latest_prebuttal||{};
    return `<div class="cpp-registry-note" id="paper-state"><div class="cpp-section-kicker">PaperRegistry</div><h3 data-toc="false">${isZh()?"正式 PaperState":"Formal PaperState"}</h3><div class="cpp-registry-kpis"><span><b>${E(reg.paper_stage||reg.current_state||"--")}</b>${isZh()?"Paper stage":"Paper stage"}</span><span><b>${E(reg.scientific_status||"--")}</b>${isZh()?"科学状态":"Scientific status"}</span><span><b>${E(`${reg.supported_claims??reg.claims_supported??0}`)}</b>${isZh()?"supported claims":"supported claims"}</span><span><b>${E(claimAudit.pass?`${claimAudit.passed||claimAudit.checks||"PASS"}/${claimAudit.checks||claimAudit.passed||""}`:"--")}</b>Claim Audit</span><span><b>${E(prep.pass?`${prep.passed_gates||0}/${prep.required_gates||0}`:"--")}</b>Paper Prep</span><span><b>${E(prebuttal.pass?"PASS":`${prebuttal.unresolved_decision_critical??"--"} open`)}</b>Prebuttal</span></div><p>${isZh()?"这里保留正式 PaperState；当前扩展不会自动改写已经冻结的论文主张。":"This preserves the formal PaperState; current extensions do not automatically rewrite frozen claims."}</p></div>`;
  };
  const paperDownload=(reg)=>reg?(reg.publication_identity?.pdf||reg.downloads?.pdf||""):"";
  const heroLinks=(paper,reg)=>{
    const download=paperDownload(reg);
    return `<div class="cpp-hero-links">${download?`<a class="cpp-download-primary" href="${E(download)}" download>${isZh()?"↓ 下载论文 PDF":"↓ Download paper PDF"}</a>`:""}<a href="selected-paper.html">${isZh()?"← 论文合集":"← Paper collection"}</a><a href="research-map.html">${isZh()?"领域研究组合图谱":"Research map"}</a><a href="paper-ideas.html">${isZh()?"研究对象 · ResearchItems":"ResearchItems"}</a></div>`;
  };
  const relatedWorkSummary=(story)=>{
    const rows=isZh()?[
      ["语义检索 / Routing","根据任务和技能描述的相似度，尽量找到合适的技能。","它主要关心“找得准不准”，通常不测试：Agent 会的东西完全一样、只换技能包装时，控制是否也应该完全一样。"],
      ["技能拆分 / Composition","把一个大技能拆成多个小技能，再组合起来完成复杂任务。","拆分时常常连技能内容和粒度也一起变了，因此很难判断：表现变化来自能力真的变了，还是只来自包装变了。"],
      ["Exposure / 权重平衡","重新调整不同技能包获得多少曝光、检索机会或权重。","它能在给定表示上做优化，但没有回答：某些技能覆盖结构是否让“只调技能包权重”从数学上就不可能恢复同一个语义目标。"]
    ]:[
      ["Semantic retrieval / routing","Match tasks to skill descriptions and retrieve the most relevant skills.","It optimizes retrieval quality but usually does not test whether repackaging identical capabilities must preserve control."],
      ["Skill decomposition / composition","Split a large skill into smaller pieces and compose them for complex tasks.","Decomposition often changes content granularity too, making capability change and representation change hard to separate."],
      ["Exposure / weight balancing","Reweight how much exposure, retrieval opportunity, or control each package receives.","It optimizes a fixed representation but does not ask when package-only reweighting is mathematically unable to recover the same semantic target."]
    ];
    const approachRefs=(story?.approaches||[]).map(a=>a.closest_work||[]);
    return `<section class="panel cpp-related-summary" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"2 · 现有研究缺什么":"2 · WHAT PRIOR WORK STILL MISSES"}</div><h2>${isZh()?"现有方法已经很会“找技能、拆技能、调权重”，但还缺一个更基础的问题":"Prior work is good at finding, splitting, and weighting skills—but misses a more basic question"}</h2><div class="cpp-related-summary-grid">${rows.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><b>${E(x[0])}</b><p><strong>${isZh()?"已经会做：":"Already solves: "}</strong>${E(x[1])}</p><p><strong>${isZh()?"还没有回答：":"Still unanswered: "}</strong>${E(x[2])}</p>${approachRefs[i]?.length?`<div class="cpp-summary-refs"><strong>${isZh()?"代表工作":"Representative work"}</strong>${approachRefs[i].map(w=>`<a href="${E(w.url||w.u||"#")}" target="_blank" rel="noopener"><span>${E(w.title||w.t||"")}</span>${venueYearTag(w)?`<em class="cpp-venue-tag">${E(venueYearTag(w))}</em>`:""}</a>`).join("")}</div>`:""}</article>`).join("")}</div><div class="cpp-gap-callout"><b>${isZh()?"E1 的位置":"Where E1 enters"}</b><p>${isZh()?"我们不再发明一种新的技能拆分或路由算法，而是把一个更基础的原则变成可检查对象：如果 Agent 真正会做的事情没变，技能怎么包装就不应该改变它的语义控制。":"We do not propose another decomposition or routing algorithm. We turn a more basic principle into an auditable object: if capability is unchanged, packaging alone should not change semantic control."}</p></div></section>`;
  };
  const e1QuickOverview=(paper,story,detail)=>{
    const example=isZh()?"比如，Agent 原来有一个“查航班并比较价格”的技能。我们只把它拆成 4 个技能包，并没有让 Agent 学会任何新能力。如果控制器因此改变了技能分配和最终行为，那么变化来自“怎么包装”，而不是“会什么”。":"For example, an agent may already have one skill for finding flights and comparing prices. Splitting that same capability into four packages adds no new ability. If control and behavior change anyway, the cause is packaging rather than capability.";
    const question=isZh()?"当 Agent 真正会做的事情完全不变时，只改技能的拆分、复制或分组方式，会不会让自进化控制器做出不同决定？":"When the agent's actual capabilities stay identical, can changing only how skills are split, cloned, or grouped make the self-evolution controller behave differently?";
    const answer=isZh()?"原则上不应该；但 E1 的证据显示，一些按“技能包身份”分配控制权的系统确实会受这种包装影响。STRI 就是用来检查这种不该出现的敏感性。":"It should not. Yet E1 shows that controllers allocating control over package identities can be sensitive to packaging alone. STRI audits this unwanted sensitivity.";
    const findings=isZh()?[
      "只换包装，也可能改变控制：能力不变，并不保证按技能包逐个分配资源的控制器得到同样结果。",
      "问题不是“技能重叠越多就越糟”：真正关键的是哪些技能包覆盖哪些语义能力，也就是“技能包—能力覆盖结构”。",
      "我们还能判断“能不能只靠调权重修回来”：R*(A;q) 给出精确边界，再用 AutoSkill P19 检查这种差异是否会传到真实执行行为。"
    ]:[
      "Packaging alone can change control: unchanged capability does not guarantee unchanged allocation in a package-first controller.",
      "The issue is not simply 'more overlap is worse'. What matters is the structural pattern of which packages cover which capabilities—support geometry.",
      "We can also ask whether reweighting alone can repair the problem: R*(A;q) gives the exact boundary, and AutoSkill P19 tests whether the effect reaches executed behavior."
    ];
    return `<section class="cpp-plain cpp-e1-overview panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"0 · 先看懂问题":"0 · START HERE"}</div><h2>${isZh()?"30 秒先抓住这篇论文在研究什么":"The paper in 30 seconds"}</h2><p class="cpp-e1-hook">${isZh()?"如果 Agent 会的东西完全没变，仅仅把一个技能拆成四个，它为什么会做出不同决定？":"If an agent's capabilities do not change, why should splitting one skill into four change its decisions?"}</p><div class="cpp-e1-overview-grid"><article><span>${isZh()?"先看一个例子":"ONE EXAMPLE"}</span><p>${E(example)}</p></article><article><span>${isZh()?"本文真正的问题":"THE QUESTION"}</span><p>${E(question)}</p></article><article class="answer"><span>${isZh()?"一句话答案":"THE ANSWER"}</span><p>${E(answer)}</p></article></div><div class="cpp-e1-findings"><b>${isZh()?"读完整页，只需要记住这三件事":"Three things to remember"}</b><div>${findings.map((x,i)=>`<article><span>0${i+1}</span><p>${E(x)}</p></article>`).join("")}</div></div><div class="cpp-term-strip"><span><b>Skill package</b>${isZh()?"一个被控制器单独看待的技能单元":"a skill unit the controller treats separately"}</span><span><b>Semantic capability</b>${isZh()?"Agent 真正会做什么":"what the agent can actually do"}</span><span><b>Representation invariance</b>${isZh()?"能力不变时，换包装不应改变控制":"repackaging alone should not change control"}</span></div><div class="cpp-e1-status-strip"><span><b>${isZh()?"核心 E1":"Canonical E1"}</b>${isZh()?"3/3 核心窄主张已有证据支持":"3/3 narrow claims supported"}</span><span><b>${isZh()?"外部扩展":"External extension"}</b>${isZh()?"已执行，但当前不纳入论文结论":"executed, but not used in the paper claim"}</span></div></section>`;
  };
  const e1ProblemOrigin=(story)=>{
    const rows=isZh()?[
      ["01 · Skill library 会不断变化","Agent 会积累、拆分、合并和复用技能，所以同一种能力经常会有不同的“包装方式”。"],
      ["02 · 但“包装变了”不等于“能力变了”","把一个技能拆成四个、复制一份或重新分组，都可以做到 Agent 真正会做的事情完全不变。"],
      ["03 · 麻烦在于控制器往往先看到“技能包”","如果控制器按技能包逐个分配曝光、检索机会或更新权重，那么多一个技能包身份，就可能多拿一份控制资源。"],
      ["04 · 于是工程细节可能改变未来行为","同一个 Agent 仅仅因为技能怎么打包，就可能检索到不同内容，进而走向不同的执行结果和自进化轨迹。"],
      ["05 · 所以缺的是一个“不变量”","我们真正要检查的是：能力相同的两种表示，是否会得到相同的语义控制。这个性质就是本文所说的 representation invariance。"]
    ]:[
      ["01 · Skill libraries keep changing","Agents accumulate, split, merge, and reuse skills, so the same capability can appear under different packaging schemes."],
      ["02 · Different packaging need not mean different capability","Splitting, cloning, or regrouping can leave what the agent can actually do completely unchanged."],
      ["03 · Controllers often see packages first","If exposure or retrieval is allocated package by package, an extra package identity can receive extra control resources."],
      ["04 · An engineering detail can therefore alter behavior","The same agent may retrieve different content and follow a different evolution trajectory solely because the library was packaged differently."],
      ["05 · The missing object is an invariant","We ask whether two representations with the same capabilities receive the same semantic control. This is representation invariance."]
    ];
    return `<section class="panel cpp-origin cpp-e1-origin" id="problem-origin"><div class="cpp-section-kicker">${isZh()?"1 · 为什么会有这个问题":"1 · WHY THIS PROBLEM EXISTS"}</div><h2>${isZh()?"“技能怎么拆”为什么不只是一个工程细节？":"Why is skill packaging more than an engineering detail?"}</h2><div class="cpp-e1-funnel"><span>${isZh()?"同样能力":"Same capability"}</span><i>→</i><span>split / clone / regroup</span><i>→</i><span>${isZh()?"按 package 分配控制":"package-level control"}</span><i>→</i><span>${isZh()?"检索内容变化":"retrieval changes"}</span><i>→</i><strong>${isZh()?"行为也可能变化":"behavior may change"}</strong></div><div class="cpp-origin-grid">${rows.map(([k,v])=>`<article><b>${E(k)}</b><p>${E(v)}</p></article>`).join("")}</div></section>`;
  };
  const e1Work=(paper,story)=>{
    const work=isZh()?[
      ["先做公平对比","能力不变，只换包装","冻结 Agent 真正会做什么，只改变技能的拆分、复制和重新分组。这样后面看到的差异才可以归因到“表示方式”，而不是技能内容变了。","Frozen support matrix A"],
      ["把直觉变成可检查规则","定义 STRI","我们把“等价技能表示应该得到相同控制”正式定义为 Skill-Taxonomy Representation Invariance（STRI）。","Representation invariance"],
      ["判断到底能不能修回来","计算 R*(A;q)","看到差异后继续问：只重新调每个技能包的权重，能否恢复同一个语义目标？R*(A;q) 给出精确的“能 / 不能”边界。","Exact certificate"],
      ["确认不是纸上问题","做 AutoSkill P19 行为验证","最后检查表示差异是否真的会改变检索、中间技能和执行行为，并用“只恢复关键中间技能”与“普通清理”做区分。","Behavioral witness"]
    ]:[
      ["Make the comparison fair","Keep capability fixed; change packaging only","Freeze what the agent can do and vary only split / clone / regroup so any difference can be attributed to representation.","Frozen support matrix A"],
      ["Turn the intuition into a testable rule","Define STRI","Formalize the requirement that equivalent skill representations should receive equivalent semantic control.","Representation invariance"],
      ["Ask whether the effect is repairable","Compute R*(A;q)","Test whether package reweighting alone can recover the same semantic target. R*(A;q) gives an exact yes/no boundary.","Exact certificate"],
      ["Check that it matters to a real agent","Run the AutoSkill P19 witness","Test whether representation changes retrieval, an intermediate skill, and executed behavior; compare specific mediator restoration against generic cleanup.","Behavioral witness"]
    ];
    const chain=isZh()?["同样能力","只换技能包装","控制分配改变","检索内容改变","行为可能改变"]:["Same capability","Repackage only","Control allocation changes","Retrieval changes","Behavior may change"];
    return `<section class="panel cpp-e1-work" id="mechanism"><div class="cpp-section-kicker">${isZh()?"3 · 我们做了什么":"3 · WHAT WE DID"}</div><h2>${isZh()?"从一个工程现象，到一个能被严格验证的科学问题，我们做了四步":"Four steps turn a packaging observation into a scientific result"}</h2><div class="cpp-work-grid">${work.map((x,i)=>`<article><span>0${i+1}</span><div><b>${E(x[0])}</b><strong>${E(x[1])}</strong><p>${E(x[2])}</p><small>${E(x[3])}</small></div></article>`).join("")}</div><div class="cpp-simple-chain"><b>${isZh()?"整篇论文的逻辑链可以先这样理解":"A simple way to read the paper's chain"}</b><div>${chain.map((x,i)=>`${i?'<i>→</i>':''}<span>${E(x)}</span>`).join("")}</div><p>${isZh()?"STRI 先检查“只换表示，控制是否会不合理地改变”，再用 P19 验证这种差异能否继续传到后面的真实行为。":"STRI audits unwanted sensitivity at the representation/control boundary; P19 then checks whether that difference propagates to real behavior."}</p></div></section>`;
  };
  const e1Results=(paper,story,detail)=>{
    const rows=isZh()?[
      ["RQ1","同样会的东西，只换技能包装，控制会变吗？","固定 Agent 真正会做的能力，只改变 split / clone / regroup，也就是只动“包装”。","会。当前审计里确实存在“对包装敏感”的情况：能力没变，但按技能包逐个分配控制资源时，结果会变。"],
      ["RQ2","是不是因为“技能重叠越多就越容易出问题”？","专门加入“重叠很高、但仍然可以完全均衡”的反例，再和真正无法均衡的结构比较。","不是。简单数技能重叠量解释不了结果；真正关键的是技能包如何覆盖语义能力，也就是“技能包—能力覆盖结构”。"],
      ["RQ3","这种表示差异真的会传到 Agent 行为吗？","在同一个 AutoSkill P19 场景中比较原表示、split-4、安慰剂对照和语义聚合对照，再比较“恢复关键中间技能”和“普通清理”。","在这个冻结场景里会：原表示 6/6 出现异常行为标记，split-4 后变成 0/6；只恢复那个关键中间技能时 3/3 恢复，而普通清理为 0/3。"]
    ]:[
      ["RQ1","Can packaging alone change control when capability is identical?","Freeze the agent's actual capability and vary only split / clone / regroup.","Yes. The audit contains representation-sensitive regimes where package-level allocation changes despite unchanged capability."],
      ["RQ2","Is the problem simply that more skill overlap is worse?","Include high-overlap cases that remain fully equalizable and compare them with truly non-equalizable structures.","No. Raw overlap count does not explain the result; the decisive object is the package-to-capability coverage structure, or support geometry."],
      ["RQ3","Does the representation difference reach actual agent behavior?","Compare original, split-4, placebo, and semantic-quotient controls on frozen AutoSkill P19, then specific mediator restoration versus generic cleanup.","On this frozen substrate, yes: 6/6 destructive signatures under the original representation become 0/6 under split-4; specific mediator restoration is 3/3 while matched cleanup is 0/3."]
    ];
    const evidence=isZh()?[
      ["R*(A;q)","它不是一个“看起来差不多”的经验分数，而是精确判断：同一个语义目标能不能只靠重新分配技能包权重实现。"],
      ["6/6 → 0/6","Agent 会的东西没变，只把表示换成 split-4，P19 的异常行为标记从 6 个都出现变成 6 个都不出现。"],
      ["3/3 vs 0/3","只加回被挤掉的关键中间技能，3 个案例都恢复；换成同规模的普通清理，0 个恢复。说明不是“随便清理一下都有效”。"]
    ]:[
      ["R*(A;q)","An exact audit of whether package weights alone can realize the same semantic target, rather than a heuristic score."],
      ["6/6 → 0/6","With capability fixed, switching to split-4 changes the P19 destructive signature from all six cases to none."],
      ["3/3 vs 0/3","Restoring the specific crowded-out mediator restores all three cases, while matched generic cleanup restores none."]
    ];
    return `<section class="panel cpp-e1-results" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"4 · 实验回答了什么":"4 · WHAT THE EXPERIMENTS ANSWER"}</div><h2>${isZh()?"不要记一堆实验名：三个 RQ 分别回答三个核心疑问":"Do not memorize experiment names: three RQs carry the paper"}</h2><div class="cpp-e1-rq-grid">${rows.map(x=>`<article><header><span>${E(x[0])}</span><b>${E(x[1])}</b></header><p class="cpp-rq-how"><strong>${isZh()?"怎么测：":"How: "}</strong>${E(x[2])}</p><div class="cpp-rq-answer"><strong>${isZh()?"看到什么":"What we found"}</strong><p>${E(x[3])}</p></div></article>`).join("")}</div><h3 data-toc="false">${isZh()?"最值得记住的三个证据":"Three pieces of decisive evidence"}</h3><div class="cpp-proof-grid cpp-proof-grid-three">${evidence.map(x=>`<article><strong>${E(x[0])}</strong><p>${E(x[1])}</p></article>`).join("")}</div><div class="cpp-now"><b>${isZh()?"这些结果合起来说明什么":"What the evidence means together"}</b><p>${isZh()?"“技能怎么拆”不是永远无害的实现细节。E1 先把这种表示敏感性单独隔离出来，再给出它什么时候能靠调权重修复、什么时候会受结构限制的精确边界，并在一个冻结 Agent 场景里看到它确实可以传到执行行为。":"Skill packaging is not always a harmless implementation detail. E1 isolates representation sensitivity, identifies when package weights can or cannot repair it, and shows on one frozen agent substrate that it can propagate to executed behavior."}</p></div></section>`;
  };
  const e1Contributions=(paper,detail)=>{
    const contributions=isZh()?[
      ["C1","把“技能包装”变成一个新的系统检查问题","我们不问哪种拆法分数更高，而问：同样能力换一种等价表示后，控制是否仍然相同。"],
      ["C2","给出一个精确的“能不能修”判断","R*(A;q) 告诉我们：差异只是权重没调好，还是当前技能包—能力结构让“只调 package 权重”本身就无法精确恢复目标。"],
      ["C3","把静态问题连接到真实行为","AutoSkill P19 提供一条限定但完整的“表示 → 检索 → 中间技能 → 行为”证据链，说明这个问题不只存在于数学表述中。"]
    ]:[
      ["C1","Turn packaging into a systems-level audit question","Rather than asking which split scores higher, ask whether equivalent representations of the same capability preserve control."],
      ["C2","Provide an exact repairability test","R*(A;q) distinguishes a bad weighting choice from a package/capability structure that package-only reweighting cannot exactly repair."],
      ["C3","Connect the static issue to behavior","AutoSkill P19 supplies a bounded representation → retrieval → mediator → behavior chain, showing that the issue is not purely mathematical."]
    ];
    const limits=isZh()?[
      "这不等于所有 skill system 都一定有这个问题；当前行为证据只覆盖一个冻结的 AutoSkill P19 场景。",
      "STRI 不是一个新的 LP 求解算法；数学工具服务于“表示不变量怎么审计”这个新问题。",
      "我们没有证明 STRI 一定提高总体任务成功率、长期安全或所有 Agent 的效用。",
      "ReasoningBank Full-P1 虽然执行了 40/40，但因为评测有效性和模型服务完整性门没有通过，不能当作新的科学结果。"
    ]:[
      "This does not mean every skill system has the problem; the behavioral evidence is bounded to one frozen AutoSkill P19 substrate.",
      "STRI is not a new LP solver; the mathematics serves the representation-invariance audit object.",
      "The paper does not establish universal task utility, longitudinal safety, or agent-wide performance gains.",
      "ReasoningBank Full-P1 completed 40/40 executions, but failed evaluator/provider eligibility and therefore is not a scientific result."
    ];
    return `<section class="panel cpp-e1-contributions" id="claim-boundary"><div class="cpp-section-kicker">${isZh()?"5 · 最终贡献与边界":"5 · CONTRIBUTIONS & BOUNDARIES"}</div><h2>${isZh()?"所以这篇论文最终让我们多知道了什么？":"What do we know now that we did not know before?"}</h2><div class="cpp-contribution-grid">${contributions.map(x=>`<article><span>${E(x[0])}</span><div><b>${E(x[1])}</b><p>${E(x[2])}</p></div></article>`).join("")}</div><div class="cpp-boundary-box"><b>${isZh()?"同样重要：这些结果没有证明什么":"Equally important: what the paper does not establish"}</b>${list(limits.map(x=>({zh:x,en:x})),"boundary")}</div></section>`;
  };
  const e1Evolution=()=>{
    const rows=isZh()?[
      ["01","最初只是工程问题","一开始我们只是在想：skill library 到底应该怎么拆、怎么检索、怎么组合。"],
      ["02","发现“能力没变，控制却变了”","真正的转折是发现控制器按技能包身份分配控制资源，于是技能包装方式本身可能改变结果。"],
      ["03","从“现象”升级成表示不变性","问题不再是“哪种拆法更好”，而是“语义等价的重新打包，本来就应该保持控制不变”。"],
      ["04","简单的“重叠越多越糟”被反例推翻","我们发现重叠很多也可以完全均衡，所以不能只数重叠多少，必须转向“技能包—能力覆盖结构”。"],
      ["05","R*(A;q) 给出精确边界","论文从经验现象推进到：什么时候只调技能包权重就能修，什么时候从结构上就做不到。"],
      ["06","补上真实 Agent 行为链","因为纯数学证书还不够，我们加入 AutoSkill P19 和中间技能对照，验证表示差异确实能沿检索传到执行行为。"],
      ["07","外部扩展保持独立","ReasoningBank Full-P1 用来尝试扩大外部有效性；它自己的评测和模型服务门没有通过，所以保持 HOLD，不倒灌修改已经成立的 E1 核心结论。"]
    ]:[
      ["01","It began as an engineering question","How should a skill library be split, retrieved, and composed?"],
      ["02","Capability stayed fixed but control changed","Controllers allocate resources over package identities, so packaging itself could affect outcomes."],
      ["03","The question became representation invariance","The paper shifted from 'which split is better?' to whether semantically equivalent repackaging should preserve control."],
      ["04","Simple overlap explanations failed","High-overlap counterexamples remained fully equalizable, forcing the story toward support geometry."],
      ["05","R*(A;q) gave the exact boundary","The paper moved from observing a phenomenon to deciding when package reweighting can and cannot repair it."],
      ["06","A behavioral bridge was added","AutoSkill P19 and mediator controls test whether representation differences reach executed behavior."],
      ["07","The external extension remains separate","ReasoningBank Full-P1 targets broader validity, but its own evaluator/provider gates failed, so it remains held outside the canonical claim."]
    ];
    return `<div class="cpp-evolution cpp-evolution-detailed cpp-e1-evolution">${rows.map(x=>`<article><span>${E(x[0])}</span><div><strong>${E(x[1])}</strong><p>${E(x[2])}</p></div></article>`).join("")}</div>`;
  };
  const e1Status=(paper,reg,detail)=>{
    return `<section class="panel cpp-next cpp-e1-status" id="next-gate"><div class="cpp-section-kicker">${isZh()?"7 · 当前状态与下一步":"7 · CURRENT STATE & NEXT"}</div><h2>${isZh()?"核心论文和外部扩展要分开看":"Separate the canonical paper from the external extension"}</h2><div class="cpp-e1-state-grid"><article><span>${isZh()?"核心 E1":"CANONICAL E1"}</span><strong>3 / 3</strong><p>${isZh()?"三个核心窄主张已有冻结证据支持，PaperRegistry 当前为 SUBMISSION_READY。简单说：E1 的核心故事已经有自己的理论边界和 P19 行为证据。":"All three narrow claims have frozen support and PaperRegistry is SUBMISSION_READY. The core E1 story already has its theoretical boundary and P19 behavioral evidence."}</p></article><article class="hold"><span>${isZh()?"外部扩展":"REASONINGBANK EXTENSION"}</span><strong>40 / 40 · HOLD</strong><p>${isZh()?"40 个实验运行的“程序执行完了”不等于“实验结论成立”。部分评测器无效，另有模型服务配额中断，因此成对科学分析不能打开；这条扩展既不加强，也不推翻核心 E1。":"Completing 40 runs is not the same as obtaining a valid scientific result. Evaluator invalidity and provider quota interruptions block paired inference, so the extension neither strengthens nor overturns canonical E1."}</p></article></div><div class="cpp-next-action"><b>${isZh()?"下一步用一句话说":"Next, in plain language"}</b><p>${isZh()?"核心 E1 不需要为了“追更多分数”重新跑。若要继续扩大外部有效性，先修好 ReasoningBank 扩展自己的评测有效性和模型服务完整性，再按原先冻结规则继续。":"Do not rerun canonical E1 merely to chase more scores. Any broader-validity continuation should first repair the ReasoningBank extension's evaluator validity and provider completeness under its frozen rules."}</p></div>${registryBox(paper,reg)}</section>`;
  };
  const e1DeepDive=(paper,reg,detail,story)=>{
    const fullRelated=relatedWorkComparison(story).replace('id="related-work-comparison"','id="related-work-full"');
    const legacy=reg&&window.renderPaperLegacyAuditBundle?window.renderPaperLegacyAuditBundle(paper.registryPaperId):"";
    const glossary=isZh()?[
      ["semantic support","Agent 真正具备哪些能力；主实验里这一层保持不变。"],
      ["package identity","控制器眼里一个独立的技能包/技能条目；我们只改变这一层的拆分与分组。"],
      ["support geometry","哪些技能包覆盖哪些语义能力形成的结构关系，不是简单的“重叠数量”。"],
      ["quotient","先把语义等价的 package 合并成同一类，再做控制；可以理解为“先看能力，再看包装”。"],
      ["certificate / R*(A;q)","一个精确审计：告诉我们同一个语义目标能不能只靠重新分配 package 权重实现。"],
      ["mediator","表示变化影响最终行为之前经过的中间环节；P19 中对应被挤掉、后来又被恢复的关键技能。"]
    ]:[
      ["semantic support","Which capabilities the agent actually has; this layer stays fixed in the main treatment."],
      ["package identity","A skill entry treated separately by the controller; only this packaging layer is split or regrouped."],
      ["support geometry","The structural pattern linking packages to capabilities, rather than a simple overlap count."],
      ["quotient","Merge semantically equivalent packages before control—conceptually, capability first and packaging second."],
      ["certificate / R*(A;q)","An exact audit of whether the target can be achieved by package reweighting alone."],
      ["mediator","An intermediate step between representation and final behavior; in P19, the specific skill that is crowded out and restored."]
    ];
    return `<details class="cpp-deep-dive system-deep-dive" id="research-archive"><summary><span><b>${isZh()?"研究档案 / 想看严谨细节时再展开":"Research dossier / open for rigorous detail"}</b><small>${isZh()?"默认正文已经讲完论文故事；这里保留模型、数据、冻结合同、完整 Related Work、审稿与证据链。":"The default story is complete above; this fold preserves models, data, frozen contracts, full related work, reviews, and evidence chains."}</small></span><em>${isZh()?"展开细节":"Open details"}</em></summary><div class="cpp-deep-dive-body"><section class="panel cpp-glossary"><div class="cpp-section-kicker">${isZh()?"先把术语翻成人话":"PLAIN-LANGUAGE GLOSSARY"}</div><h2 data-toc="false">${isZh()?"下面技术档案里最常见的 6 个词是什么意思？":"Six terms used in the technical dossier"}</h2><div class="cpp-glossary-grid">${glossary.map(x=>`<article><b>${E(x[0])}</b><p>${E(x[1])}</p></article>`).join("")}</div></section>${snapshot(detail)}<section class="panel" id="models-data"><div class="cpp-section-kicker">${isZh()?"实验对象":"EXPERIMENTAL SUBSTRATE"}</div><h2>${isZh()?"具体用了什么模型、数据和环境？":"Which models, data, and environments were used?"}</h2>${modelData(detail)}</section>${detail.contract?.length?`<section class="panel" id="experiment-contract"><div class="cpp-section-kicker">${isZh()?"冻结实验合同":"FROZEN EXPERIMENT CONTRACT"}</div><h2>${isZh()?"为了保证比较公平，哪些东西必须固定？":"What must stay fixed for a fair comparison?"}</h2>${contract(detail)}</section>`:""}<section class="panel" id="experiment-design"><div class="cpp-section-kicker">${isZh()?"完整实验设计":"FULL EXPERIMENT DESIGN"}</div><h2>${isZh()?"各个对照组分别在排除什么替代解释？":"What alternative explanation does each control rule out?"}</h2><p class="cpp-design-lead">${E(T(detail.design))}</p>${arms(detail)}${analysisPlan(detail)}</section>${fullRelated}${fullStoryArchive(story)}${failureBoundaries(story)}${replayNotes(detail)}${legacy}</div></details>`;
  };
  const renderE1Page=(paper,reg,detail,story)=>`<main class="cpp-page cpp-e1-page" data-paper-order="${paper.order}"><header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-hero-subtitle">${isZh()?"如果 Agent 会的东西完全没变，仅仅把一个技能拆成四个，它为什么会做出不同决定？":"If an agent's capabilities stay identical, why should splitting one skill into four change its decisions?"}</p><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>${heroLinks(paper,reg)}</header>${e1QuickOverview(paper,story,detail)}${e1ProblemOrigin(story)}${relatedWorkSummary(story)}${e1Work(paper,story)}${e1Results(paper,story,detail)}${e1Contributions(paper,detail)}<section class="panel" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"6 · 论文怎么演变到今天":"6 · HOW THE PAPER EVOLVED"}</div><h2>${isZh()?"这不是一开始就定好的故事，而是被反例和实验一步步收窄出来的":"The story was narrowed step by step by counterexamples and evidence"}</h2>${e1Evolution()}</section>${e1Status(paper,reg,detail)}${e1DeepDive(paper,reg,detail,story)}<div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div></main>`;
  const beginnerSpec=(pageId)=>{
    const factory=window.CURRENT_PAPER_BEGINNER_FACTORIES?.[pageId];
    return factory?factory((zh,en)=>isZh()?zh:en):null;
  };
  const beginnerQuick=(paper,spec)=>`<section class="cpp-plain cpp-e1-overview cpp-beginner-overview panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"0 · 先看懂问题":"0 · START HERE"}</div><h2>${isZh()?"30 秒先抓住这篇论文在研究什么":"The paper in 30 seconds"}</h2><p class="cpp-e1-hook">${E(spec.hook)}</p><div class="cpp-e1-overview-grid"><article><span>${isZh()?"先看一个例子":"ONE EXAMPLE"}</span><p>${E(spec.example)}</p></article><article><span>${isZh()?"本文真正的问题":"THE QUESTION"}</span><p>${E(T(paper.question))}</p></article><article class="answer"><span>${isZh()?"一句话答案":"THE ANSWER"}</span><p>${E(spec.answer)}</p></article></div><div class="cpp-term-strip">${spec.terms.map(x=>`<span><b>${E(x[0])}</b>${E(x[1])}</span>`).join("")}</div></section>`;
  const beginnerOrigin=(spec)=>`<section class="panel cpp-origin cpp-e1-origin cpp-beginner-origin" id="problem-origin"><div class="cpp-section-kicker">${isZh()?"1 · 为什么会有这个问题":"1 · WHY THIS PROBLEM EXISTS"}</div><h2>${isZh()?"这个研究问题是怎么一步步冒出来的？":"How did this research problem emerge?"}</h2><div class="cpp-origin-grid">${spec.origin.map(x=>`<article><b>${E(x[0])}</b><p>${E(x[1])}</p></article>`).join("")}</div></section>`;
  const beginnerGaps=(paper,spec)=>`<section class="panel cpp-related-summary cpp-beginner-gaps" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"2 · 现有研究缺什么":"2 · WHAT PRIOR WORK STILL MISSES"}</div><h2>${isZh()?"为什么不能直接用现有思路回答？":"Why do existing approaches not answer the exact question?"}</h2><p class="cpp-design-lead">${E(spec.gapLead)}</p><div class="cpp-related-summary-grid">${spec.gaps.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><b>${E(x[0])}</b><p><strong>${isZh()?"已经能做：":"What it already does: "}</strong>${E(x[1])}</p><p><strong>${isZh()?"还缺：":"What is still missing: "}</strong>${E(x[2])}</p></article>`).join("")}</div><div class="cpp-gap-callout"><b>${isZh()?`${paper.code} 真正切入的位置`:`Where ${paper.code} enters`}</b><p>${E(T(paper.thesis))}</p></div></section>`;
  const beginnerWork=(spec)=>`<section class="panel cpp-e1-work cpp-beginner-work" id="mechanism"><div class="cpp-section-kicker">${isZh()?"3 · 我们具体做了什么":"3 · WHAT WE DID"}</div><h2>${isZh()?"把问题变成一个可被证伪的实验，我们做了四步":"Four steps turn the question into a falsifiable experiment"}</h2><div class="cpp-work-grid">${spec.work.map((x,i)=>`<article><span>0${i+1}</span><div><b>${E(x[0])}</b><strong>${E(x[1])}</strong><p>${E(x[2])}</p></div></article>`).join("")}</div><div class="cpp-simple-chain"><b>${isZh()?"整篇论文可以先沿这条链理解":"A simple way to read the paper"}</b><div>${spec.chain.map((x,i)=>`${i?'<i>→</i>':''}<span>${E(x)}</span>`).join("")}</div></div></section>`;
  const beginnerResults=(spec)=>`<section class="panel cpp-e1-results cpp-beginner-results" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"4 · 实验现在回答了什么":"4 · WHAT THE EVIDENCE ANSWERS"}</div><h2>${isZh()?"不要按实验编号记：直接看三个核心问题的当前答案":"Read the evidence by question, not by experiment ID"}</h2><div class="cpp-e1-rq-grid">${spec.rqs.map(x=>`<article><header><span>${E(x[0])}</span><b>${E(x[1])}</b></header><p class="cpp-rq-how"><strong>${isZh()?"怎么测：":"How: "}</strong>${E(x[2])}</p><div class="cpp-rq-answer"><strong>${isZh()?"当前答案":"Current answer"}</strong><p>${E(x[3])}</p></div></article>`).join("")}</div><h3 data-toc="false">${isZh()?"最值得记住的三个证据":"Three pieces of evidence to remember"}</h3><div class="cpp-proof-grid cpp-proof-grid-three">${spec.evidence.map(x=>`<article><strong>${E(x[0])}</strong><p>${E(x[1])}</p></article>`).join("")}</div></section>`;
  const beginnerContributions=(spec)=>`<section class="panel cpp-e1-contributions cpp-beginner-contributions" id="claim-boundary"><div class="cpp-section-kicker">${isZh()?"5 · 最终贡献与边界":"5 · CONTRIBUTIONS & BOUNDARIES"}</div><h2>${isZh()?"所以这篇论文 / 科学对象真正多做了什么？":"What does this paper or scientific object actually add?"}</h2><div class="cpp-contribution-grid">${spec.contributions.map(x=>`<article><span>${E(x[0])}</span><div><b>${E(x[1])}</b><p>${E(x[2])}</p></div></article>`).join("")}</div><div class="cpp-boundary-box"><b>${isZh()?"同样重要：现在明确不能写成什么":"Equally important: what cannot currently be claimed"}</b>${list(spec.limits.map(x=>({zh:x,en:x})),"boundary")}</div></section>`;
  const beginnerEvolution=(paper,detail,spec)=>`<section class="panel cpp-beginner-evolution" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"6 · 论文怎么演变到今天":"6 · HOW THE PAPER EVOLVED"}</div><h2>${E(spec.evolutionTitle)}</h2>${evolution(paper,detail)}${lineage(detail)}</section>`;
  const beginnerStatus=(paper,reg,spec)=>`<section class="panel cpp-next cpp-e1-status cpp-beginner-status" id="next-gate"><div class="cpp-section-kicker">${isZh()?"7 · 当前状态与下一步":"7 · CURRENT STATE & NEXT"}</div><h2>${E(spec.statusHeadline)}</h2><div class="cpp-e1-state-grid">${spec.statusCards.map((x,i)=>`<article class="${i?"hold":""}"><span>${E(x[0])}</span><strong>${E(x[1])}</strong><p>${E(x[2])}</p></article>`).join("")}</div><div class="cpp-next-action"><b>${isZh()?"下一步用一句话说":"Next, in plain language"}</b><p>${E(spec.nextPlain)}</p></div>${registryBox(paper,reg)}</section>`;
  const beginnerDeepDive=(paper,reg,detail,story,spec)=>{
    const fullRelated=story?relatedWorkComparison(story).replace('id="related-work-comparison"','id="related-work-full"'):"";
    const legacy=reg&&window.renderPaperLegacyAuditBundle?window.renderPaperLegacyAuditBundle(paper.registryPaperId):"";
    return `<details class="cpp-deep-dive system-deep-dive" id="research-archive"><summary><span><b>${isZh()?"研究档案 / 想看严谨细节时再展开":"Research dossier / open for rigorous detail"}</b><small>${isZh()?"默认正文已经讲完论文故事；这里保留模型、数据、冻结合同、完整设计、Related Work 与审计记录。":"The default story is complete above; this fold preserves models, data, frozen contracts, full design, related work, and audit records."}</small></span><em>${isZh()?"展开细节":"Open details"}</em></summary><div class="cpp-deep-dive-body"><section class="panel cpp-glossary"><div class="cpp-section-kicker">${isZh()?"先把术语翻成人话":"PLAIN-LANGUAGE GLOSSARY"}</div><h2 data-toc="false">${isZh()?"上面最容易卡住的三个词是什么意思？":"Three terms that make the page easier to read"}</h2><div class="cpp-glossary-grid">${spec.terms.map(x=>`<article><b>${E(x[0])}</b><p>${E(x[1])}</p></article>`).join("")}</div></section>${snapshot(detail)}<section class="panel" id="models-data"><div class="cpp-section-kicker">${isZh()?"实验对象":"EXPERIMENTAL SUBSTRATE"}</div><h2>${isZh()?"具体用了什么模型、数据和环境？":"Which models, data, and environments were used?"}</h2>${modelData(detail)}</section>${detail.contract?.length?`<section class="panel" id="experiment-contract"><div class="cpp-section-kicker">${isZh()?"冻结实验合同":"FROZEN EXPERIMENT CONTRACT"}</div><h2>${isZh()?"为了保证比较公平，哪些东西必须固定？":"What must stay fixed for a fair comparison?"}</h2>${contract(detail)}</section>`:""}<section class="panel" id="experiment-design"><div class="cpp-section-kicker">${isZh()?"完整实验设计":"FULL EXPERIMENT DESIGN"}</div><h2>${isZh()?"严谨版本：实验到底怎么识别这个问题？":"Rigorous version: how does the experiment identify the question?"}</h2><p class="cpp-design-lead">${E(T(detail.design))}</p>${arms(detail)}${storyExperiments(story)}${analysisPlan(detail)}</section>${fullRelated}${story?fullStoryArchive(story):""}${failureBoundaries(story||detail)}${!reg?workingNoveltyAudit(detail):""}${replayNotes(detail)}${legacy}</div></details>`;
  };
  const renderBeginnerPage=(pageId,paper,reg,detail,story)=>{
    const spec=beginnerSpec(pageId); if(!spec)return "";
    return `<main class="cpp-page cpp-e1-page cpp-beginner-page" data-paper-order="${paper.order}"><header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-hero-subtitle">${E(spec.hook)}</p><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>${heroLinks(paper,reg)}</header>${beginnerQuick(paper,spec)}${beginnerOrigin(spec)}${beginnerGaps(paper,spec)}${beginnerWork(spec)}${beginnerResults(spec)}${beginnerContributions(spec)}${beginnerEvolution(paper,detail,spec)}${beginnerStatus(paper,reg,spec)}${beginnerDeepDive(paper,reg,detail,story,spec)}<div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div></main>`;
  };
  const collectionCard=(id,paper)=>{
    const d=detailFor(id), reg=registryPaper(paper), label=T(d.collectionLabel)||`${orderMark(paper.order)} ${paper.code}`;
    const models=(d.models||[]).slice(0,2).map(x=>x.name).join(" · ")||"—";
    const datasets=(d.datasets||[]).slice(0,2).map(x=>x.name).join(" · ")||"—";
    return `<a class="cpp-collection-card" href="${E(paper.href)}"><header><span>${E(label)}</span><em title="${E(paperState(paper,reg))}">${E(paper.displayStateShort||paperState(paper,reg))}</em></header><h3>${E(T(paper.title))}</h3><p>${E(T(paper.question))}</p><dl><div><dt>${isZh()?"模型":"Model"}</dt><dd>${E(models)}</dd></div><div><dt>${isZh()?"数据":"Data"}</dt><dd>${E(datasets)}</dd></div></dl><footer><span>${E(kindLabel(paper))}</span><b>${isZh()?"打开单篇 →":"Open paper →"}</b></footer></a>`;
  };
  window.renderCurrentPaperCollection=()=>{
    const data=window.CURRENT_PAPER_PAGES||{}, ids=data.order||[];
    const formal=ids.slice(0,5).map(id=>[id,data.papers?.[id]]).filter(([,p])=>p);
    const working=ids.slice(5).map(id=>[id,data.papers?.[id]]).filter(([,p])=>p);
    return `<main class="cpp-collection"><header class="cpp-collection-hero"><div class="eyebrow">${isZh()?"当前科研 · 论文合集":"CURRENT RESEARCH · PAPER COLLECTION"}</div><h1>${isZh()?"9 篇论文，一页先看清楚，再进入单篇":"Nine papers: compare here, read details on each paper page"}</h1><p>${isZh()?"①–⑤ 是正式 PaperRegistry；⑥–⑦ 是工作论文；⑧–⑨ 是独立 Scientific Object。合集页只显示定位、状态、模型/数据和入口，不再重复单篇正文。":"①–⑤ are formal PaperRegistry papers; ⑥–⑦ are working papers; ⑧–⑨ are independent scientific objects. This collection shows positioning, status, model/data, and navigation only."}</p><div class="cpp-collection-stats"><span><b>5</b>${isZh()?"正式论文":"formal papers"}</span><span><b>2</b>${isZh()?"工作论文":"working papers"}</span><span><b>2</b>${isZh()?"独立科学对象":"Scientific objects"}</span><span><b>9</b>${isZh()?"独立阅读页":"reader pages"}</span></div></header><section class="cpp-collection-group" id="formal-paper-collection"><header><div><span>01–05</span><div><h2>${isZh()?"正式 PaperRegistry 主线":"Formal PaperRegistry portfolio"}</h2><p>${isZh()?"论文状态仍以 canonical PaperRegistry 为准；当前扩展不会自动改写正式主张。":"Formal state remains canonical in PaperRegistry; current extensions do not automatically rewrite frozen claims."}</p></div></div></header><div class="cpp-collection-grid">${formal.map(([id,p])=>collectionCard(id,p)).join("")}</div></section><section class="cpp-collection-group" id="working-paper-collection"><header><div><span>06–09</span><div><h2>${isZh()?"工作论文与独立 Scientific Object":"Working papers and independent scientific objects"}</h2><p>${isZh()?"没有人为补 E3/G2 等正式编号；达到独立 paper gate 后再进入 PaperRegistry。":"No formal publication codes are invented; PaperRegistry promotion happens only after an independent paper gate."}</p></div></div></header><div class="cpp-collection-grid">${working.map(([id,p])=>collectionCard(id,p)).join("")}</div></section></main>`;
  };
  window.renderCurrentPaperPage=(pageId)=>{
    const paper=window.CURRENT_PAPER_PAGES?.papers?.[pageId];
    if(!paper) return `<div class="empty">Paper page unavailable.</div>`;
    const reg=registryPaper(paper), detail=detailFor(pageId), story=storyFor(paper), dossier=story||detail;
    if(pageId==="paper-e1"&&story) return renderE1Page(paper,reg,detail,story);
    const beginner=renderBeginnerPage(pageId,paper,reg,detail,story);
    if(beginner) return beginner;
    return `<main class="cpp-page" data-paper-order="${paper.order}">
      <header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>${heroLinks(paper,reg)}</header>
      ${snapshot(detail)}
      <section class="cpp-plain panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"速览版":"QUICK OVERVIEW"}</div><h2>${isZh()?"30 秒看懂这篇论文":"Understand the paper in 30 seconds"}</h2><p class="cpp-plain-lead">${E(T(paper.plain))}</p><div class="cpp-question"><b>${isZh()?"一句话问题":"One question"}</b><span>${E(T(paper.question))}</span></div><div class="cpp-thesis"><b>${isZh()?"当前核心判断":"Current thesis"}</b><span>${E(T(paper.thesis))}</span></div></section>
      ${problemOrigin(paper,story)}
      ${relatedWorkComparison(dossier)}
      <section class="panel" id="mechanism"><div class="cpp-section-kicker">${isZh()?"方法 / 机制":"METHOD / MECHANISM"}</div><h2>${isZh()?"这篇论文到底怎么解决问题":"How the paper attacks the problem"}</h2>${mechanism(paper)}</section>
      <section class="panel" id="models-data"><div class="cpp-section-kicker">${isZh()?"实验对象":"EXPERIMENTAL SUBSTRATE"}</div><h2>${isZh()?"用了什么模型、数据集和实验环境":"Models, datasets, and environments"}</h2>${modelData(detail)}</section>
      ${detail.contract?.length?`<section class="panel" id="experiment-contract"><div class="cpp-section-kicker">${isZh()?"冻结实验合同":"FROZEN EXPERIMENT CONTRACT"}</div><h2>${isZh()?"实验单位、处理变量、对照与判定规则":"Units, treatment, controls, and decision rules"}</h2>${contract(detail)}</section>`:""}
      <section class="panel" id="experiment-design"><div class="cpp-section-kicker">${isZh()?"实验思路":"EXPERIMENT DESIGN"}</div><h2>${isZh()?"实验怎么设计，为什么这样能回答问题":"How the experiment identifies the scientific question"}</h2><p class="cpp-design-lead">${E(T(detail.design))}</p>${arms(detail)}${storyExperiments(story)}${analysisPlan(detail)}</section>
      ${fullStoryArchive(dossier)}
      <section class="panel" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"结果与证据":"RESULTS / EVIDENCE"}</div><h2>${isZh()?"当前实验结果，以及它真正证明了什么":"What the current evidence actually establishes"}</h2><p class="cpp-status-headline">${E(T(paper.experiment?.headline))}</p>${metrics(paper)}${proof(detail)}<div class="cpp-now"><b>${isZh()?"当前现场解释":"Current interpretation"}</b><p>${E(T(paper.experiment?.now))}</p></div>${interpretation(detail)}</section>
      <section class="panel" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"论文演变":"PAPER EVOLUTION"}</div><h2>${isZh()?"这篇论文怎么一步步演变到今天":"How the paper evolved into its current form"}</h2>${evolution(paper,detail)}${lineage(detail)}</section>
      <section class="cpp-claim-grid" id="claim-boundary"><article class="panel"><div class="cpp-section-kicker">${isZh()?"现在能说什么":"SUPPORTED / ALLOWED"}</div><h2>${isZh()?"当前允许的主张":"What we can currently claim"}</h2>${list(paper.claims,"good")}</article><article class="panel"><div class="cpp-section-kicker">${isZh()?"不能偷换什么":"BOUNDARY"}</div><h2>${isZh()?"明确不能写成什么":"What this paper does not claim"}</h2>${list(paper.boundaries,"boundary")}</article></section>
      ${failureBoundaries(dossier)}
      ${!reg?workingNoveltyAudit(detail):""}
      ${replayNotes(detail)}
      ${reg&&window.renderPaperLegacyAuditBundle?window.renderPaperLegacyAuditBundle(paper.registryPaperId):""}
      <section class="panel cpp-next" id="next-gate"><div class="cpp-section-kicker">${isZh()?"下一步":"NEXT GATE"}</div><h2>${isZh()?"接下来真正该做什么":"What should happen next"}</h2><p>${E(T(paper.next))}</p>${registryBox(paper,reg)}</section>
      <div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div>
    </main>`;
  };
})();
