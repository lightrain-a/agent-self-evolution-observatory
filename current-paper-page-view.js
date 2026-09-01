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
  const registryBox=(paper,reg)=>{
    if(!reg) return `<div class="cpp-registry-note working"><b>${isZh()?"身份说明":"Identity"}</b><p>${E(kindLabel(paper))}。${isZh()?"这是只读研究说明，不会因此创建正式论文编号，也不会授予科学、实验、GPU 或投稿权限。":"This is a read-only research explanation. It does not create a formal publication code or grant scientific, experiment, GPU, or submission authority."}</p></div>`;
    const claimAudit=reg.latest_claim_audit||{}, prep=reg.latest_paper_preparation||{}, prebuttal=reg.latest_prebuttal||{};
    const download=reg.publication_identity?.pdf||reg.downloads?.pdf||"";
    return `<section class="cpp-registry-note" id="paper-state"><div class="cpp-section-kicker">PaperRegistry</div><h2>${isZh()?"这篇论文当前正式状态":"Current formal paper state"}</h2><div class="cpp-registry-kpis"><span><b>${E(reg.paper_stage||reg.current_state||"--")}</b>${isZh()?"Paper stage":"Paper stage"}</span><span><b>${E(reg.scientific_status||"--")}</b>${isZh()?"科学状态":"Scientific status"}</span><span><b>${E(`${reg.supported_claims??reg.claims_supported??0}`)}</b>${isZh()?"supported claims":"supported claims"}</span><span><b>${E(claimAudit.pass?`${claimAudit.passed||claimAudit.checks||"PASS"}/${claimAudit.checks||claimAudit.passed||""}`:"--")}</b>Claim Audit</span><span><b>${E(prep.pass?`${prep.passed_gates||0}/${prep.required_gates||0}`:"--")}</b>Paper Prep</span><span><b>${E(prebuttal.pass?"PASS":`${prebuttal.unresolved_decision_critical??"--"} open`)}</b>Prebuttal</span></div><p>${isZh()?"这里保留的是正式 PaperState；本页上方的当前科学扩展（如 E1 Full-P1、E2 R17）不会自动改写已经冻结的 PaperRegistry 主张。":"This is the formal PaperState. Current scientific extensions shown above do not automatically rewrite the frozen PaperRegistry claims."}</p><div class="cpp-actions">${download?`<a href="${E(download)}">${isZh()?"论文 PDF":"Paper PDF"}</a>`:""}<a href="selected-paper.html">${isZh()?"← 返回论文合集":"← Back to paper collection"}</a></div></section>`;
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
    const reg=registryPaper(paper), detail=detailFor(pageId), story=storyFor(paper);
    return `<main class="cpp-page" data-paper-order="${paper.order}">
      <header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p><div class="cpp-hero-links"><a href="selected-paper.html">${isZh()?"← 论文合集":"← Paper collection"}</a><a href="research-map.html">${isZh()?"领域研究组合图谱":"Research map"}</a><a href="paper-ideas.html">${isZh()?"研究对象 · ResearchItems":"ResearchItems"}</a></div></header>
      ${snapshot(detail)}
      <section class="cpp-plain panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"速览版":"QUICK OVERVIEW"}</div><h2>${isZh()?"30 秒看懂这篇论文":"Understand the paper in 30 seconds"}</h2><p class="cpp-plain-lead">${E(T(paper.plain))}</p><div class="cpp-question"><b>${isZh()?"一句话问题":"One question"}</b><span>${E(T(paper.question))}</span></div><div class="cpp-thesis"><b>${isZh()?"当前核心判断":"Current thesis"}</b><span>${E(T(paper.thesis))}</span></div></section>
      ${problemOrigin(paper,story)}
      <section class="panel" id="mechanism"><div class="cpp-section-kicker">${isZh()?"方法 / 机制":"METHOD / MECHANISM"}</div><h2>${isZh()?"这篇论文到底怎么解决问题":"How the paper attacks the problem"}</h2>${mechanism(paper)}</section>
      <section class="panel" id="models-data"><div class="cpp-section-kicker">${isZh()?"实验对象":"EXPERIMENTAL SUBSTRATE"}</div><h2>${isZh()?"用了什么模型、数据集和实验环境":"Models, datasets, and environments"}</h2>${modelData(detail)}</section>
      ${detail.contract?.length?`<section class="panel" id="experiment-contract"><div class="cpp-section-kicker">${isZh()?"冻结实验合同":"FROZEN EXPERIMENT CONTRACT"}</div><h2>${isZh()?"实验单位、处理变量、对照与判定规则":"Units, treatment, controls, and decision rules"}</h2>${contract(detail)}</section>`:""}
      <section class="panel" id="experiment-design"><div class="cpp-section-kicker">${isZh()?"实验思路":"EXPERIMENT DESIGN"}</div><h2>${isZh()?"实验怎么设计，为什么这样能回答问题":"How the experiment identifies the scientific question"}</h2><p class="cpp-design-lead">${E(T(detail.design))}</p>${arms(detail)}${storyExperiments(story)}${analysisPlan(detail)}</section>
      <section class="panel" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"结果与证据":"RESULTS / EVIDENCE"}</div><h2>${isZh()?"当前实验结果，以及它真正证明了什么":"What the current evidence actually establishes"}</h2><p class="cpp-status-headline">${E(T(paper.experiment?.headline))}</p>${metrics(paper)}${proof(detail)}<div class="cpp-now"><b>${isZh()?"当前现场解释":"Current interpretation"}</b><p>${E(T(paper.experiment?.now))}</p></div>${interpretation(detail)}</section>
      <section class="panel" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"论文演变":"PAPER EVOLUTION"}</div><h2>${isZh()?"这篇论文怎么一步步演变到今天":"How the paper evolved into its current form"}</h2>${evolution(paper,detail)}${lineage(detail)}</section>
      <section class="cpp-claim-grid" id="claim-boundary"><article class="panel"><div class="cpp-section-kicker">${isZh()?"现在能说什么":"SUPPORTED / ALLOWED"}</div><h2>${isZh()?"当前允许的主张":"What we can currently claim"}</h2>${list(paper.claims,"good")}</article><article class="panel"><div class="cpp-section-kicker">${isZh()?"不能偷换什么":"BOUNDARY"}</div><h2>${isZh()?"明确不能写成什么":"What this paper does not claim"}</h2>${list(paper.boundaries,"boundary")}</article></section>
      ${failureBoundaries(story)}
      ${replayNotes(detail)}
      <section class="panel cpp-next" id="next-gate"><div class="cpp-section-kicker">${isZh()?"下一步":"NEXT GATE"}</div><h2>${isZh()?"接下来真正该做什么":"What should happen next"}</h2><p>${E(T(paper.next))}</p></section>
      ${registryBox(paper,reg)}
      <div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div>
    </main>`;
  };
})();
