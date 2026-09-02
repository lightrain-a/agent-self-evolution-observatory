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
  const statusPlainShort=(paper,reg)=>{
    if(!isZh())return "";
    const raw=String(paperState(paper,reg)||"");
    if(/SUBMISSION_READY/i.test(raw))return "内部投稿准备";
    if(/PREBUTTAL/i.test(raw))return "仍需补关键证据";
    if(/HOLD/i.test(raw))return "等待明确重开条件";
    if(/PRE[-_ ]?F0/i.test(raw))return "仅前置资格化";
    if(!reg)return "工作中 · 未进入正式论文状态";
    return "研究系统内部状态";
  };
  const statusBadge=(paper,reg)=>`<span class="cpp-badge cpp-badge-strong">${E(paperState(paper,reg))}</span><span class="cpp-badge">${E(kindLabel(paper))}</span>${statusPlainShort(paper,reg)?`<span class="cpp-badge cpp-badge-plain">${E(statusPlainShort(paper,reg))}</span>`:""}`;
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
    const raw=String(work?.venue||"").trim();
    const embeddedYear=(raw.match(/\b(20\d{2})\b/)||[])[1]||"";
    const year=embeddedYear||String(work?.year||"").trim();
    const yy=year.length>=2?year.slice(-2):year;
    if(!raw&&!yy)return "";
    if(/^arxiv/i.test(raw))return `arXiv${yy?`'${yy}`:""}`;
    if(/^iclr/i.test(raw))return `ICLR${yy?`'${yy}`:""}${/workshop/i.test(raw)?" Wkshp":""}`;
    if(/^neurips/i.test(raw))return `NeurIPS${yy?`'${yy}`:""}${/datasets|d&b/i.test(raw)?" D&B":""}`;
    if(/^cvpr/i.test(raw))return `CVPR${yy?`'${yy}`:""}`;
    if(/^iccv/i.test(raw))return `ICCV${yy?`'${yy}`:""}`;
    if(/^icml/i.test(raw))return `ICML${yy?`'${yy}`:""}`;
    if(/^acl/i.test(raw))return `ACL${yy?`'${yy}`:""}`;
    if(/^kdd/i.test(raw))return `KDD${yy?`'${yy}`:""}`;
    if(/^sigir/i.test(raw))return `SIGIR${yy?`'${yy}`:""}`;
    if(/findings.*acl|acl.*findings/i.test(raw))return `ACL Findings${yy?`'${yy}`:""}`;
    if(/findings.*naacl|naacl.*findings/i.test(raw))return `NAACL Findings${yy?`'${yy}`:""}`;
    if(/^npj artificial intelligence/i.test(raw))return `npj AI${yy?`'${yy}`:""}`;
    const venue=raw.replace(/\b20\d{2}\b/g,"").replace(/\s{2,}/g," ").trim();
    return `${venue||"Year"}${yy?`'${yy}`:""}`;
  };
  const publicationPriority=(w)=>{
    const venue=String(w?.venue||"").toLowerCase(),year=Number(w?.year||0);
    const top=/^(acl|iclr|icml|neurips|cvpr|iccv|kdd|sigir)\b/.test(venue)&&!/findings|workshop|d&b|datasets/.test(venue);
    const formal=Boolean(venue)&&!/^arxiv/.test(venue)&&!/project construct|public data source|released substrate|public asset lineage/.test(venue);
    const secondary=/findings|workshop|d&b|datasets/.test(venue);
    const tier=top?0:(formal&&!secondary?1:(secondary?2:(/^arxiv/.test(venue)?4:3)));
    return [tier,-year];
  };
  const rankedWorks=(rows)=>[...(rows||[])].sort((a,b)=>{const A=publicationPriority(a),B=publicationPriority(b);return A[0]-B[0]||A[1]-B[1]||String(a.title||"").localeCompare(String(b.title||""));});
  const evidenceProfile=(pageId)=>window.CURRENT_PAPER_EVIDENCE_PROFILES?.[pageId]||null;
  const sourceBadge=(source)=>{
    const raw=String(source?.venue||"");
    if(/^project construct/i.test(raw))return isZh()?"本项目构造":"Project construct";
    if(/^public data sources/i.test(raw))return isZh()?"真实公开数据源":"Public data source";
    if(/^released substrate/i.test(raw))return isZh()?"公开 substrate":"Released substrate";
    if(/^public asset lineage/i.test(raw))return isZh()?"公开资产谱系":"Public asset lineage";
    return venueYearTag(source);
  };
  const datasetPrimer=(e)=>{
    const rows=(e?.sources||[]).map(s=>({s,p:window.CURRENT_PAPER_DATASET_PRIMER?.[s.name]})).filter(x=>x.p);
    if(!rows.length)return "";
    return `<section class="cpp-dataset-primer"><header><span>${isZh()?"先认识数据 / 环境":"MEET THE DATA / ENVIRONMENT"}</span><h4>${isZh()?"别先记 benchmark 名字：先看一条数据到底长什么样":"Before benchmark names, understand what one task actually looks like"}</h4><p>${isZh()?"这里把数据集、环境、判分器和方法来源分开讲。看完后应该能知道模型实际看到什么、要做什么、原 benchmark 怎么判对错，以及为什么我们选它。":"This separates datasets, environments, evaluators, and method lineages so the actual task/input/output/evaluation is clear."}</p></header><div class="cpp-dataset-primer-grid">${rows.map(({s,p},i)=>`<article><header><span>${String(i+1).padStart(2,"0")}</span><div><b>${E(s.name||"")}</b><small>${E(T(p.kind))}</small></div>${sourceBadge(s)?`<em class="cpp-venue-tag">${E(sourceBadge(s))}</em>`:""}</header><p class="what">${E(plainExperimentLabel(T(p.what)))}</p><dl><div><dt>${isZh()?"一条数据 / 任务长什么样？":"What does one task look like?"}</dt><dd>${E(plainExperimentLabel(T(p.sample)))}</dd></div><div><dt>${isZh()?"模型看到什么、要做什么？":"What goes in and out?"}</dt><dd>${E(plainExperimentLabel(T(p.io)))}</dd></div><div><dt>${isZh()?"原来怎么判对错？":"How is it evaluated?"}</dt><dd>${E(plainExperimentLabel(T(p.score)))}</dd></div><div><dt>${isZh()?"为什么我们要用它？":"Why do we use it?"}</dt><dd>${E(plainExperimentLabel(T(p.why)))}</dd></div></dl></article>`).join("")}</div></section>`;
  };
  const termPrimer=(pageId)=>{
    const cfg=window.CURRENT_PAPER_TERM_PRIMER,keys=cfg?.pages?.[pageId]||[];
    if(!keys.length)return "";
    return `<aside class="cpp-term-primer"><header><b>${isZh()?"后面会反复出现的词，先翻成人话":"Terms worth decoding before the technical sections"}</b><span>${isZh()?"不要求记英文；先理解它在实验里扮演什么角色。":"Remember the role, not the jargon."}</span></header><div>${keys.map(k=>{const d=cfg.definitions?.[k];return d?`<article><strong>${E(plainUiLabel(k))}</strong><p>${E(T(d))}</p></article>`:""}).join("")}</div></aside>`;
  };
  const plainTermLabel=(value)=>{
    const raw=String(value??""); if(!isZh())return raw;
    const map={
      "Skill package":"技能包","Semantic capability":"真实语义能力","Representation invariance":"表示不变性",
      "Persistent state":"持久状态","Evaluator":"判分器","Fail closed":"证据不足时保守停止",
      "Durable memory":"持久记忆","Native retrieval":"原生检索","Transport":"影响传递",
      "Winner projection":"只保留最佳轨迹","Learning evidence":"学习证据","Held-out":"留出测试",
      "Provenance":"来源身份","Confound":"混杂因素","Matched swap":"匹配交换",
      "Influence":"是否真的影响决策","Fidelity":"是否忠实于来源","Same-state counterfactual":"同状态反事实对照",
      "Fast loop":"当前回合快速环","Slow loop":"跨回合慢速环","Persistent reuse":"未来持续复用",
      "Local repair":"局部修复","Coupling":"结构耦合","Collateral regression":"非目标退化",
      "Relational topology":"关系拓扑","Stage localization":"阶段定位","iRecall":"关系满足率 iRecall"
    };
    const lower={treatment:"实验变量",counterfactual:"反事实对照",mediator:"中间环节",retrieval:"检索",support:"支持条件",failclosed:"证据不足时保守停止",writer:"写入模块",native:"原生流程",terminal:"最终结果",trajectory:"行动轨迹",backbone:"主模型",substrate:"实验底座",ir:"关系满足率 iRecall",pair:"成对比较",heldout:"留出测试",provenance:"来源身份",evaluator:"判分器",arm:"实验组"};
    return map[raw]||lower[raw.toLowerCase()]||raw;
  };
  const readableParagraphs=(value)=>{
    const raw=String(value??"");
    if(!isZh()||raw.length<130)return `<p>${E(raw)}</p>`;
    const parts=(raw.match(/[^。！？；]+[。！？；]?/g)||[raw]).map(x=>x.trim()).filter(Boolean);
    return `<div class="cpp-readable-paragraphs">${parts.map(x=>`<p>${E(x)}</p>`).join("")}</div>`;
  };
  const plainUiLabel=(value)=>{
    const raw=String(value??""); if(!isZh())return raw;
    const direct=plainTermLabel(raw); if(direct!==raw)return direct;
    return [[/\bprovenance[- ]only\b/gi,"仅来源身份"],[/\bprovenance\b/gi,"来源身份"],[/\bwriter[- ]mode\b/gi,"写入模式"],[/\bwriter\b/gi,"写入模块"],[/\btreatment\b/gi,"实验变量"],[/\bcontent\b/gi,"内容"],[/\brelevance\b/gi,"相关性"],[/\branking\b/gi,"排序"],[/\bsource\b/gi,"来源"],[/\bauthority\b/gi,"权限"],[/\btracking\b/gi,"追踪"],[/\blearning\b/gi,"学习"],[/\bfailure\b/gi,"失败"],[/\bmetadata\b/gi,"元数据"],[/\bequivalence\b/gi,"等价性"],[/\bgate\b/gi,"门禁"],[/\bexact-information\b/gi,"精确信息"],[/\bsupport\b/gi,"支持"],[/\baudit\b/gi,"审计"],[/\bcross-rung\b/gi,"跨层级"],[/\bendpoint\b/gi,"结果端点"],[/\badjudication\b/gi,"裁决"],[/\breproduction\b/gi,"复现"],[/\bdevelopment\b/gi,"开发"],[/\bconfirmatory\b/gi,"确证性"],[/\bpending\b/gi,"待完成"],[/\bpass\b/gi,"通过"]].reduce((s,[p,r])=>s.replace(p,r),raw);
  };
  const plainExperimentLabel=(value)=>{
    const raw=String(value??""); if(!isZh())return raw;
    const rules=[
      [/provenance-only causal sign only after L2 executes/gi,"只有 L2 真正执行后才能判断‘来源身份’的因果方向"],[/forced latent capacity vs native transport/gi,"强制提供记忆时的潜在能力 vs 系统真实流程中的传递"],[/extension integrity before paired inference/gi,"扩展实验先通过完整性检查，之后才比较两组效果"],[/graph distance \/ shared-resource propagation/gi,"副作用是否沿图距离 / 共享资源传播"],[/topology × training-support interaction/gi,"拓扑结构 × 训练覆盖范围的交互影响"],[/future retrieval \/ reuse \/ benefit/gi,"未来是否再次检索、复用并真正受益"],[/source-direction fidelity/gi,"动作变化是否与来源经验方向一致"],[/same-state action influence/gi,"同状态下记忆是否真的改变动作"],[/stage-localized recovery/gi,"给某一阶段补信息后能否恢复"],[/retrieval \/ mediator restoration/gi,"记忆检索 / 恢复关键中间环节"],[/specific mediator add-back vs matched cleanup/gi,"恢复关键中间环节 vs 同规模普通清理"],[/post-learning held-out performance/gi,"学习后在未见测试任务上的表现"],[/prospective fail-closed verdict/gi,"新数据上是否按预先规则保守停止"],[/updated\/base\/NullMemory ordering/gi,"更新记忆 / 基准 / 无记忆三组的排序"],[/definite \/ possible sets/gi,"确定事件集合 / 可能事件集合"],[/current-pass premise/gi,"‘当前安全’这个前提是否成立"],[/first-event sets/gi,"未来第一次出现问题的位置"],[/contrast envelope/gi,"不同判分器给出的效果范围"],[/interface integrity/gi,"记忆接口是否真的接到了策略"],[/content specificity/gi,"效果是否只对正确内容出现"],[/corridor \/ rejoin/gi,"是否先回到可行区域 / 再真正回到正确轨迹"],[/terminal task consequence/gi,"最终任务是否真的受影响"],[/action influence/gi,"动作是否被记忆改变"],[/target repair/gi,"目标问题是否修好"],[/collateral effect/gi,"其它原本正常部分有没有被伤到"],[/sustained rejoin/gi,"是否持续回到正确轨迹"],[/terminal success/gi,"最终任务是否成功"],[/Target Repair Gain/gi,"目标修复收益"],[/Collateral Regression Rate/gi,"非目标退化率"],[/Update Externality/gi,"更新带来的新增副作用"],[/official iRecall/gi,"官方关系满足率 iRecall"],[/exact-all-relations/gi,"所有指定关系是否同时满足"],[/coverage \/ physical validity/gi,"场景覆盖率 / 物理有效性"],[/aggregate association/gi,"总体相关性"],[/terminal outcome/gi,"最终任务结果"],[/early action/gi,"前几步动作"],[/support eligibility/gi,"是否有足够合格样本支持实验"],[/durable-state divergence/gi,"写入后的长期记忆是否真的不同"],[/retrieval exposure/gi,"未来任务是否真正检索到这段记忆"],[/first-action TV \/ modal change/gi,"第一步动作分布是否改变"],[/stream-level D_s/gi,"每个数据流的学习差异"],[/pair-level d_sr/gi,"每组成对实验的差异"],[/sign-flip \/ bootstrap \/ TOST/gi,"方向检验 / 重采样区间 / 等价性检验"],[/heterogeneity/gi,"不同任务之间的差异是否一致"],[/destructive signature/gi,"异常行为标记"],[/bounded behavior/gi,"限定场景里的真实行为"],[/structural exact-realizability endpoint/gi,"结构上能否精确实现目标"],[/Full-P1 frozen tasks × arms = runs/gi,"Full-P1 冻结任务 × 实验组 = 执行次数"]
    ];
    const first=rules.reduce((s,[p,r])=>s.replace(p,r),raw);
    return [[/\bwriter\b/gi,"写入模块"],[/\bevaluator\b/gi,"判分器"],[/\bbackbone\b/gi,"主模型"],[/\bexecutor\b/gi,"执行器"],[/\btrajectory\b/gi,"行动轨迹"],[/\btreatment\b/gi,"实验变量"],[/\bprovenance\b/gi,"来源身份"],[/\bheld-out\b/gi,"留出测试"],[/\bsubstrate\b/gi,"实验底座"],[/\bcounterfactual\b/gi,"反事实对照"],[/\bmediator\b/gi,"中间环节"]].reduce((s,[p,r])=>s.replace(p,r),first);
  };
  const statePrimer=(paper,reg)=>{
    const raw=String(paperState(paper,reg)||"");
    let text=isZh()?"这是研究系统里的内部状态，不等于论文已经投稿或被录用。":"This is an internal research state, not a submission or acceptance decision.";
    if(/SUBMISSION_READY/i.test(raw))text=isZh()?"表示核心证据与文稿已经达到内部投稿准备标准；仍不等于已经投稿，更不等于录用。":"Internally submission-ready; not yet submitted or accepted.";
    else if(/PREBUTTAL/i.test(raw))text=isZh()?"表示论文主线已形成，但还有关键证据或审稿风险需要补，不应该把当前版本当最终稿。":"The story is formed, but critical evidence/review risks remain.";
    else if(/HOLD/i.test(raw))text=isZh()?"表示当前应暂停继续推进，等待明确的重开条件；HOLD 不是负结果，也不是论文失败。":"Work is paused pending a specific reopen condition; HOLD is not a negative result.";
    else if(/PRE[-_ ]?F0/i.test(raw))text=isZh()?"表示实验设计、数据或实现只完成了前置资格化；还没有产生可以写进论文的科学结果。":"Only pre-experiment qualification is complete; no scientific result is established yet.";
    else if(!reg)text=isZh()?"这是工作论文 / 科学对象：问题和实验正在形成，还没有进入正式 PaperRegistry 的完整论文状态。":"This is a working paper/scientific object, not yet a formal PaperRegistry paper.";
    return `<div class="cpp-status-plain"><b>${isZh()?"这个状态用人话怎么理解？":"What does this status mean?"}</b><p>${E(text)}</p></div>`;
  };
  const featuredPublishedWork=(pageId)=>{
    const rows=evidenceProfile(pageId)?.featured||[];
    if(!rows.length)return "";
    return `<div class="cpp-featured-literature"><header><div><span>${isZh()?"优先对标 · 最近正式发表":"PRIORITY · RECENT PUBLISHED WORK"}</span><b>${isZh()?"先看最近的顶会 / 正式论文，再用 arXiv 补最直接碰撞":"Recent peer-reviewed work first; preprints only fill direct gaps"}</b></div><small>${isZh()?"排序原则：相关性优先，其次正式主会/期刊与年份；不因为预印本更新更晚就挤掉已发表近邻。":"Ranking favors relevance, then peer-reviewed venue and recency; a newer preprint does not automatically displace a published neighbor."}</small></header><div class="cpp-featured-literature-grid">${rows.map((w,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><h4><a href="${E(w.url||"#")}" target="_blank" rel="noopener">${E(w.title||"")}</a>${venueYearTag(w)?`<em class="cpp-venue-tag">${E(venueYearTag(w))}</em>`:""}</h4><p><strong>${isZh()?"为什么是直接近邻：":"Why it is close: "}</strong>${E(T(w.relation))}</p><p><strong>${isZh()?"为什么还不是我们的问题：":"Why the gap remains: "}</strong>${E(T(w.boundary))}</p></div></article>`).join("")}</div></div>`;
  };
  const experimentProvenance=(pageId)=>{
    const e=evidenceProfile(pageId)?.experiment;
    if(!e)return "";
    const sourceRows=e.sources||[],modelRows=e.models||[],readoutRows=e.readouts||[];
    const sources=sourceRows.map((s,i)=>`<article class="cpp-exp-source"><header><span>${String(i+1).padStart(2,"0")}</span><div><b>${E(s.name||"")}</b><small>${E(s.paper||"")}</small></div>${sourceBadge(s)?`<em class="cpp-venue-tag">${E(sourceBadge(s))}</em>`:""}</header>${s.url?`<a class="cpp-source-link" href="${E(s.url)}" target="_blank" rel="noopener">${isZh()?"原始论文 / 来源 ↗":"Source paper ↗"}</a>`:""}<dl><div><dt>${isZh()?"原始数据是什么":"Original source"}</dt><dd>${E(T(s.original))}</dd></div><div><dt>${isZh()?"我们实际用了哪一部分":"Our slice"}</dt><dd>${E(T(s.slice))}</dd></div><div><dt>${isZh()?"我们在此基础上怎么改":"How we transform it"}</dt><dd>${E(T(s.transform))}</dd></div></dl></article>`).join("");
    const models=modelRows.map(m=>`<article><b>${E(m.name||"")}</b><p>${E(T(m.role))}</p><small>${E(T(m.status))}</small></article>`).join("");
    const quantities=(e.quantities||[]).map(q=>`<span><b>${E(q.v||"")}</b><small>${E(plainExperimentLabel(T(q.k)))}</small></span>`).join("");
    const readouts=readoutRows.map(x=>`<span>${E(plainExperimentLabel(x))}</span>`).join("");
    const sourceNames=sourceRows.slice(0,4).map(s=>`<span><b>${E(s.name||"")}</b>${sourceBadge(s)?`<em class="cpp-venue-tag">${E(sourceBadge(s))}</em>`:""}</span>`).join("");
    const sliceItems=sourceRows.slice(0,4).map(s=>`<li><b>${E(s.name||"")}</b><span>${E(plainExperimentLabel(T(s.slice)))}</span></li>`).join("");
    const modelItems=modelRows.map(m=>`<li><b>${E(plainExperimentLabel(m.name||""))}</b><span>${E(plainExperimentLabel(T(m.role)))}</span></li>`).join("");
    const readoutItems=readoutRows.map(x=>`<span>${E(plainExperimentLabel(x))}</span>`).join("");
    return `<div class="cpp-experiment-provenance" id="experiment-provenance"><header><div><span>${isZh()?"实验怎么做 · 小白版":"EXPERIMENT · PLAIN LANGUAGE"}</span><h4>${isZh()?"先回答 5 个问题，再看下面的严谨实验账本":"Five questions explain the experiment before the audit details"}</h4></div><p>${E(plainExperimentLabel(T(e.intro)))}</p></header>${datasetPrimer(e)}<div class="cpp-exp-beginner-grid"><article><span>01</span><b>${isZh()?"数据从哪里来？":"Where does the data come from?"}</b><p>${isZh()?"先认清原始 benchmark / 数据集是谁做的。我们不是自己凭空造一套任务。":"Start from the original benchmark or dataset rather than an invented task collection."}</p><div class="cpp-exp-beginner-sources">${sourceNames}</div></article><article><span>02</span><b>${isZh()?"我们实际拿了哪一部分？":"Which part do we actually use?"}</b><p>${isZh()?"不会把原论文全部样本都算成我们的实验量；下面只列真正进入当前实验的 slice。":"We do not count the full source benchmark as our sample; only the actual experimental slice matters."}</p><ul>${sliceItems}</ul></article><article><span>03</span><b>${isZh()?"实验里唯一改什么？":"What do we change?"}</b><p>${E(plainExperimentLabel(T(e.treatment)))}</p><small>${isZh()?"其它关键条件尽量保持一样，这样差异才有资格归因给这个变量。":"Other important conditions stay matched so the contrast is interpretable."}</small></article><article><span>04</span><b>${isZh()?"拿谁来测？":"What models or judges are tested?"}</b><p>${isZh()?"把真正做任务的主模型、负责写记忆/更新的模块、执行器，以及负责判分的模型或规则分开写，避免把“被测对象”和“裁判”混成一个东西。":"Backbones, writers, executors, and evaluators are separated rather than conflated."}</p><ul>${modelItems}</ul></article><article><span>05</span><b>${isZh()?"最后怎么看结果？":"How do we decide what happened?"}</b><p>${isZh()?"不是只看一个总成功率，而是看与论文问题直接对应的结果。":"We read outcomes tied directly to the scientific question rather than one aggregate success score."}</p><div class="cpp-exp-beginner-readouts">${readoutItems}</div></article></div><section class="cpp-exp-scale"><header><b>${isZh()?"这些数字分别在数什么？":"What exactly do these numbers count?"}</b><p>${isZh()?"原 benchmark 的总规模、我们真正使用的样本、成对实验、独立任务、回合和留出测试不能混成同一个 n。":"Source-benchmark size, actual samples, pairs, tasks, episodes, and held-out evaluations are different quantities."}</p></header><div class="cpp-exp-quantity-strip">${quantities}</div></section><details class="cpp-exp-ledger"><summary><div><b>${isZh()?"展开完整实验账本":"Open the full experiment ledger"}</b><span>${isZh()?"原始数据规模、具体 slice、改造方式、模型职责、统计单位与完整 readout 都保留在这里。":"Original scale, exact slice, transformation, model roles, statistical unit, and readouts remain here."}</span></div><em>${isZh()?"严谨细节":"AUDIT"}</em></summary><div class="cpp-exp-ledger-body"><section><h4>${isZh()?"A · 数据 / benchmark 来源，以及我们怎么改造成实验":"A · Dataset / benchmark provenance and transformation"}</h4><div class="cpp-exp-source-grid">${sources}</div></section><section><h4>${isZh()?"B · 被测模型 / evaluator / backbone 分别负责什么":"B · Roles of models / evaluators / backbones"}</h4><div class="cpp-exp-model-grid">${models}</div></section><div class="cpp-exp-identification"><article><b>${isZh()?"一个独立样本到底是什么？":"What counts as one independent unit?"}</b><p>${E(T(e.unit))}</p></article><article><b>${isZh()?"实验里唯一操纵的变量":"The manipulated variable"}</b><p>${E(T(e.treatment))}</p></article><article class="readouts"><b>${isZh()?"完整结果清单":"Full readout list"}</b><div>${readouts}</div></article></div></div></details></div>`;
  };
  const relatedWorkComparison=(story)=>{
    if(!story?.approaches?.length)return "";
    return `<section class="panel cpp-related-work" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"现有工作对比":"RELATED WORK COMPARISON"}</div><h2>${isZh()?"现有方法已经做到什么，我们到底还剩什么新东西":"What prior work already solves, and what remains scientifically distinct"}</h2><p class="cpp-design-lead">${isZh()?"这一节完整迁自原 PaperRegistry 的 Paper Story V3。不是只列引用，而是逐个比较：现有范式怎么做、为什么还不能回答我们的科学问题，以及正文必须守住哪条 novelty boundary。":"Migrated from the former PaperRegistry Paper Story V3. It compares what each paradigm does, why it does not answer this paper's exact question, and the novelty boundary the manuscript must preserve."}</p><div class="cpp-related-stack">${story.approaches.map((a,i)=>`<article class="cpp-related-approach"><header><span>${String(i+1).padStart(2,"0")}</span><div><h3>${E(a.name||"")}</h3><p><b>${isZh()?"现有范式：":"Current paradigm: "}</b>${E(storyText(a,"how"))}</p><p><b>${isZh()?"仍然缺什么：":"Why insufficient: "}</b>${E(storyText(a,"problem"))}</p></div></header>${a.closest_work?.length?`<div class="advisor-table-scroll"><table class="matrix cpp-nearest-table"><thead><tr><th>${isZh()?"最近工作":"Closest work"}</th><th>${isZh()?"它解决了什么":"What it solves"}</th><th>${isZh()?"和我们重叠什么":"Overlap"}</th><th>${isZh()?"它没回答什么":"Missing object"}</th><th>${isZh()?"我们必须守住的边界":"Our boundary"}</th></tr></thead><tbody>${rankedWorks(a.closest_work).map(w=>`<tr><th><a href="${E(w.url||w.u||"#")}" target="_blank" rel="noopener">${E(w.title||w.t||"")}</a>${venueYearTag(w)?`<span class="cpp-venue-tag">${E(venueYearTag(w))}</span>`:""}<p>${E(T(w.what||w.d))}</p></th><td>${E(T(w.solves))}</td><td>${E(T(w.overlap))}</td><td>${E(T(w.missing))}</td><td>${E(T(w.boundary))}</td></tr>`).join("")}</tbody></table></div>`:""}</article>`).join("")}</div></section>`;
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
    const approachRefs=(story?.approaches||[]).map(a=>rankedWorks(a.closest_work||[]));
    return `<section class="panel cpp-related-summary" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"2 · 现有研究缺什么":"2 · WHAT PRIOR WORK STILL MISSES"}</div><h3 class="cpp-subsection-title">${isZh()?"现有方法已经很会“找技能、拆技能、调权重”，但还缺一个更基础的问题":"Prior work is good at finding, splitting, and weighting skills—but misses a more basic question"}</h3>${featuredPublishedWork("paper-e1")}<div class="cpp-related-summary-grid">${rows.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><b>${E(x[0])}</b><p><strong>${isZh()?"已经会做：":"Already solves: "}</strong>${E(x[1])}</p><p><strong>${isZh()?"还没有回答：":"Still unanswered: "}</strong>${E(x[2])}</p>${approachRefs[i]?.length?`<div class="cpp-summary-refs"><strong>${isZh()?"代表工作":"Representative work"}</strong>${approachRefs[i].map(w=>`<a href="${E(w.url||w.u||"#")}" target="_blank" rel="noopener"><span>${E(w.title||w.t||"")}</span>${venueYearTag(w)?`<em class="cpp-venue-tag">${E(venueYearTag(w))}</em>`:""}</a>`).join("")}</div>`:""}</article>`).join("")}</div><div class="cpp-gap-callout"><b>${isZh()?"E1 的位置":"Where E1 enters"}</b><p>${isZh()?"我们不再发明一种新的技能拆分或路由算法，而是把一个更基础的原则变成可检查对象：如果 Agent 真正会做的事情没变，技能怎么包装就不应该改变它的语义控制。":"We do not propose another decomposition or routing algorithm. We turn a more basic principle into an auditable object: if capability is unchanged, packaging alone should not change semantic control."}</p></div></section>`;
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
    return `<section class="cpp-plain cpp-e1-overview panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"0 · 先看懂问题":"0 · START HERE"}</div><h3 class="cpp-subsection-title">${isZh()?"30 秒先抓住这篇论文在研究什么":"The paper in 30 seconds"}</h3><p class="cpp-e1-hook">${isZh()?"如果 Agent 会的东西完全没变，仅仅把一个技能拆成四个，它为什么会做出不同决定？":"If an agent's capabilities do not change, why should splitting one skill into four change its decisions?"}</p><div class="cpp-e1-overview-grid"><article><span>${isZh()?"先看一个例子":"ONE EXAMPLE"}</span><p>${E(example)}</p></article><article><span>${isZh()?"本文真正的问题":"THE QUESTION"}</span><p>${E(question)}</p></article><article class="answer"><span>${isZh()?"一句话答案":"THE ANSWER"}</span>${readableParagraphs(answer)}</article></div><div class="cpp-e1-findings"><b>${isZh()?"如果只想先建立直觉，可以先看这三条":"Three intuition-building takeaways before the full story"}</b><div>${findings.map((x,i)=>`<article><span>0${i+1}</span><p>${E(x)}</p></article>`).join("")}</div></div><div class="cpp-term-strip"><span><b>${E(plainTermLabel("Skill package"))}</b>${isZh()?"一个被控制器单独看待的技能单元":"a skill unit the controller treats separately"}</span><span><b>${E(plainTermLabel("Semantic capability"))}</b>${isZh()?"Agent 真正会做什么":"what the agent can actually do"}</span><span><b>${E(plainTermLabel("Representation invariance"))}</b>${isZh()?"能力不变时，换包装不应改变控制":"repackaging alone should not change control"}</span></div><div class="cpp-e1-status-strip"><span><b>${isZh()?"核心 E1":"Canonical E1"}</b>${isZh()?"3/3 核心窄主张已有证据支持":"3/3 narrow claims supported"}</span><span><b>${isZh()?"外部扩展":"External extension"}</b>${isZh()?"已执行，但当前不纳入论文结论":"executed, but not used in the paper claim"}</span></div></section>`;
  };
  const e1OriginRows=()=>isZh()?[
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
  const e1ProblemOrigin=(story)=>{
    const rows=e1OriginRows();
    return `<section class="panel cpp-origin cpp-e1-origin" id="problem-origin"><div class="cpp-section-kicker">${isZh()?"1 · 为什么会有这个问题":"1 · WHY THIS PROBLEM EXISTS"}</div><h3 class="cpp-subsection-title">${isZh()?"“技能怎么拆”为什么不只是一个工程细节？":"Why is skill packaging more than an engineering detail?"}</h3><p class="cpp-reader-long-lead">${isZh()?"先把方法放到一边：E1 之所以值得成为一篇论文，是因为一个看似无关紧要的工程操作——拆技能包——可能在能力完全不变时改变控制权分配。下面先把这个矛盾完整建立起来。":"Before the method, establish the contradiction: a seemingly harmless engineering operation—repackaging skills—can alter control allocation even when capability is unchanged."}</p><div class="cpp-e1-funnel"><span>${isZh()?"同样能力":"Same capability"}</span><i>→</i><span>split / clone / regroup</span><i>→</i><span>${isZh()?"按 package 分配控制":"package-level control"}</span><i>→</i><span>${isZh()?"检索内容变化":"retrieval changes"}</span><i>→</i><strong>${isZh()?"行为也可能变化":"behavior may change"}</strong></div><div class="cpp-origin-grid">${rows.map(([k,v])=>`<article><b>${E(k)}</b><p>${E(v)}</p></article>`).join("")}</div></section>`;
  };
  const e1Work=(paper,story,detail)=>{
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
    return `<section class="panel cpp-e1-work" id="mechanism"><div class="cpp-section-kicker">${isZh()?"3 · 我们做了什么":"3 · WHAT WE DID"}</div><h3 class="cpp-subsection-title">${isZh()?"从工程现象到可证伪问题：我们做了哪些工作，为什么都需要？":"From an engineering observation to a falsifiable question: what did we do, and why?"}</h3><div class="cpp-work-grid">${work.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><b>${E(x[0])}</b><strong>${E(x[1])}</strong><p>${E(x[2])}</p><small>${E(x[3])}</small></div></article>`).join("")}</div><div class="cpp-simple-chain"><b>${isZh()?"先用一条简单链理解整篇论文":"A simple way to read the paper's chain"}</b><div>${chain.map((x,i)=>`${i?'<i>→</i>':''}<span>${E(x)}</span>`).join("")}</div><p>${isZh()?"STRI 先检查“只换表示，控制是否会不合理地改变”，再用 P19 验证这种差异能否继续传到后面的真实行为。":"STRI audits unwanted sensitivity at the representation/control boundary; P19 then checks whether that difference propagates to real behavior."}</p></div>${experimentProvenance("paper-e1")}${readerDesignDetails(detail,story)}</section>`;
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
    return `<section class="panel cpp-e1-results" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"4 · 实验回答了什么":"4 · WHAT THE EXPERIMENTS ANSWER"}</div><h3 class="cpp-subsection-title">${isZh()?"按科学问题读结果：哪些已经回答，哪些边界仍然必须保留？":"Read the evidence by scientific question: what is answered, and what boundaries remain?"}</h3><div class="cpp-e1-rq-grid">${rows.map(x=>`<article><header><span>${E(x[0])}</span><b>${E(x[1])}</b></header><p class="cpp-rq-how"><strong>${isZh()?"怎么测：":"How: "}</strong>${E(x[2])}</p><div class="cpp-rq-answer"><strong>${isZh()?"看到什么":"What we found"}</strong><p>${E(x[3])}</p></div></article>`).join("")}</div><h3 data-toc="false">${isZh()?"目前最关键的证据":"Evidence worth remembering"}</h3><div class="cpp-proof-grid cpp-proof-grid-three">${evidence.map(x=>`<article><strong>${E(x[0])}</strong><p>${E(x[1])}</p></article>`).join("")}</div><div class="cpp-now"><b>${isZh()?"这些结果合起来说明什么":"What the evidence means together"}</b><p>${isZh()?"“技能怎么拆”不是永远无害的实现细节。E1 先把这种表示敏感性单独隔离出来，再给出它什么时候能靠调权重修复、什么时候会受结构限制的精确边界，并在一个冻结 Agent 场景里看到它确实可以传到执行行为。":"Skill packaging is not always a harmless implementation detail. E1 isolates representation sensitivity, identifies when package weights can or cannot repair it, and shows on one frozen agent substrate that it can propagate to executed behavior."}</p></div>${readerEvidenceDetails(detail,story)}</section>`;
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
    return `<section class="panel cpp-e1-contributions" id="claim-boundary"><div class="cpp-section-kicker">${isZh()?"5 · 最终贡献与边界":"5 · CONTRIBUTIONS & BOUNDARIES"}</div><h3 class="cpp-subsection-title">${isZh()?"所以这篇论文最终让我们多知道了什么？":"What do we know now that we did not know before?"}</h3><div class="cpp-contribution-grid">${contributions.map(x=>`<article><span>${E(x[0])}</span><div><b>${E(x[1])}</b><p>${E(x[2])}</p></div></article>`).join("")}</div>${detail?.interpretation?.importance?`<div class="cpp-contribution-why"><b>${isZh()?"为什么这件事值得读者在意":"Why this matters beyond this one experiment"}</b><p>${E(T(detail.interpretation.importance))}</p></div>`:""}<div class="cpp-boundary-box"><b>${isZh()?"同样重要：这些结果没有证明什么":"Equally important: what the paper does not establish"}</b>${list(limits.map(x=>({zh:x,en:x})),"boundary")}</div></section>`;
  };
  const e1Evolution=(paper,detail)=>{
    const origin=e1OriginRows();
    const rows=isZh()?[
      ["06","先构造真正公平的 representation counterfactual","只有 semantic support、任务和能力内容都冻结，只改 split / clone / regroup，后面的差异才有资格解释成 representation effect。"],
      ["07","“重叠越多越糟”被反例推翻","高 overlap 也可能完全可均衡；这一步迫使我们放弃简单 overlap heuristic，转向 package-to-capability support geometry。"],
      ["08","从经验现象推进到 exact realizability","R*(A;q) 把“看起来受包装影响”升级成精确问题：同一个语义目标究竟能不能只靠 package reweighting 恢复。"],
      ["09","semantic quotient 成为机制性对照","如果先按语义类聚合再分配，表示敏感性应该消失；这个对照把问题从一般权重调参收窄到 package-first basis。"],
      ["10","纯理论证书仍然不够","即使静态 control surface 有差异，审稿人仍可以问：真实 Agent 会不会根本不受影响？因此必须补动态行为桥。"],
      ["11","AutoSkill P19 补上 representation → retrieval → mediator → behavior","原表示、split、ID placebo、semantic quotient 与 mediator add-back / cleanup 共同形成一个限定但完整的行为证据链。"],
      ["12","ReasoningBank 扩展用于挑战外部有效性，而不是重写 E1","Full-P1 后来加入；40/40 执行完成但 evaluator invalid + provider quota 让 paired inference 关闭，因此正确结论是 extension HOLD，而不是把不完整扩展写进 canonical claim。"]
    ]:[
      ["06","Construct a fair representation counterfactual","Semantic support, task, and capability content must stay fixed while only split/clone/regroup changes."],
      ["07","The overlap heuristic failed","High-overlap cases can remain fully equalizable, forcing the analysis toward package-to-capability support geometry."],
      ["08","Move from observation to exact realizability","R*(A;q) asks exactly whether package reweighting can recover the same semantic target."],
      ["09","Use the semantic quotient as a mechanistic control","Aggregating by semantic class before allocation tests whether the sensitivity comes from the package-first basis."],
      ["10","A static certificate was still insufficient","A reviewer could still ask whether a real agent ever feels the static difference, motivating a behavioral bridge."],
      ["11","AutoSkill P19 adds representation → retrieval → mediator → behavior","Original/split/placebo/quotient and mediator controls form a bounded but complete behavioral chain."],
      ["12","ReasoningBank challenges external validity without rewriting E1","Full-P1 completed execution but failed evaluator/provider integrity, so the correct disposition is an extension HOLD rather than a canonical claim update."]
    ];
    const decisions=detail?.lineage||[];
    return `<div class="cpp-evolution-phase origin"><header><span>${isZh()?"起点与问题形成":"ORIGIN & PROBLEM FORMATION"}</span><b>${isZh()?"为什么一个工程细节最终变成了科学问题":"Why an engineering detail became a scientific question"}</b></header><div class="cpp-evolution cpp-evolution-detailed">${origin.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><strong>${E(cleanEvolutionTitle(x[0]))}</strong><p>${E(x[1])}</p></div></article>`).join("")}</div></div><div class="cpp-evolution-phase"><header><span>${isZh()?"证据如何改写故事":"EVIDENCE-DRIVEN REFORMULATION"}</span><b>${isZh()?"哪些反例、控制和验证把 STRI 一步步收窄到今天":"Which counterexamples and controls sharpened STRI"}</b></header><div class="cpp-evolution cpp-evolution-detailed cpp-e1-evolution">${rows.map(x=>`<article><span>${E(x[0])}</span><div><strong>${E(x[1])}</strong><p>${E(x[2])}</p></div></article>`).join("")}</div></div>${decisions.length?`<div class="cpp-evolution-phase decision"><header><span>${isZh()?"关键科研决策":"RESEARCH DECISIONS"}</span><b>${isZh()?"哪些路线被主动放弃，哪些边界必须一直保留":"What was deliberately abandoned, and which boundaries must remain"}</b></header><div class="cpp-lineage">${decisions.map((x,i)=>`<article><span>${String(13+i).padStart(2,"0")}</span><div><b>${E(T(x.title))}</b><p>${E(T(x.body))}</p></div></article>`).join("")}</div></div>`:""}<div class="cpp-evolution-current"><b>${isZh()?"为什么今天是这个版本":"Why the paper has this form today"}</b><p>${E(T(paper.thesis))}</p><p>${isZh()?"核心 E1 已经有自己的 exact certificate 与限定行为桥；ReasoningBank 是后来增加的外部有效性扩展，它的 evaluator/provider gate 失败只能让扩展 HOLD，不能倒灌改写 canonical 结论。":"Canonical E1 already has its exact certificate and bounded behavioral bridge. ReasoningBank is a later external-validity extension; its evaluator/provider gate failure can only hold the extension, not rewrite the canonical result."}</p></div>`;
  };
  const e1EvolutionSection=(paper,detail)=>`<section class="panel cpp-full-evolution" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"6 · 完整研究演变与关键决策":"6 · FULL RESEARCH EVOLUTION & DECISIONS"}</div><h3 class="cpp-subsection-title">${isZh()?"这不是一开始就定好的故事：反例、边界和外部验证一步步把论文收窄成今天的 STRI":"The paper was not predetermined: counterexamples, boundaries, and external validation progressively shaped STRI"}</h3><p class="cpp-reader-long-lead">${isZh()?"下面保留完整主线，而不是为了版式把它压成固定六步。每次转向都对应一个真实原因：旧解释被反例推翻、理论对象变清楚、行为证据补上，或扩展自己的 gate 没过。":"The full arc is preserved rather than compressed into a fixed number of steps. Each turn has a concrete reason: a counterexample rejected an explanation, the theoretical object sharpened, behavioral evidence was added, or an extension failed its own gate."}</p>${e1Evolution(paper,detail)}</section>`;
  const e1Status=(paper,reg,detail)=>{
    return `<section class="panel cpp-next cpp-e1-status" id="next-gate"><div class="cpp-section-kicker">${isZh()?"7 · 当前状态与下一步":"7 · CURRENT STATE & NEXT"}</div><h3 class="cpp-subsection-title">${isZh()?"核心论文和外部扩展要分开看":"Separate the canonical paper from the external extension"}</h3>${statePrimer(paper,reg)}<div class="cpp-e1-state-grid"><article><span>${isZh()?"核心 E1":"CANONICAL E1"}</span><strong>3 / 3</strong><p>${isZh()?"三个核心窄主张已有冻结证据支持，PaperRegistry 当前为 SUBMISSION_READY。简单说：E1 的核心故事已经有自己的理论边界和 P19 行为证据。":"All three narrow claims have frozen support and PaperRegistry is SUBMISSION_READY. The core E1 story already has its theoretical boundary and P19 behavioral evidence."}</p></article><article class="hold"><span>${isZh()?"外部扩展":"REASONINGBANK EXTENSION"}</span><strong>40 / 40 · HOLD</strong><p>${isZh()?"40 个实验运行的“程序执行完了”不等于“实验结论成立”。部分评测器无效，另有模型服务配额中断，因此成对科学分析不能打开；这条扩展既不加强，也不推翻核心 E1。":"Completing 40 runs is not the same as obtaining a valid scientific result. Evaluator invalidity and provider quota interruptions block paired inference, so the extension neither strengthens nor overturns canonical E1."}</p></article></div><div class="cpp-next-action"><b>${isZh()?"下一步用一句话说":"Next, in plain language"}</b><p>${isZh()?"核心 E1 不需要为了“追更多分数”重新跑。若要继续扩大外部有效性，先修好 ReasoningBank 扩展自己的评测有效性和模型服务完整性，再按原先冻结规则继续。":"Do not rerun canonical E1 merely to chase more scores. Any broader-validity continuation should first repair the ReasoningBank extension's evaluator validity and provider completeness under its frozen rules."}</p></div>${registryBox(paper,reg)}</section>`;
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
  const renderE1Page=(paper,reg,detail,story)=>`<main class="cpp-page cpp-e1-page" data-paper-order="${paper.order}"><header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-hero-subtitle">${isZh()?"如果 Agent 会的东西完全没变，仅仅把一个技能拆成四个，它为什么会做出不同决定？":"If an agent's capabilities stay identical, why should splitting one skill into four change its decisions?"}</p><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>${heroLinks(paper,reg)}</header>${readerChapter("reader-understand","01","先理解这篇论文","Understand the paper","先建立直觉和问题来源：它在研究什么、为什么这个矛盾会出现。","Start with the intuition and origin: what the paper studies and why the contradiction exists.",e1QuickOverview(paper,story,detail)+termPrimer("paper-e1")+e1ProblemOrigin(story))}${readerChapter("reader-position","02","为什么现有研究还不够","Why prior work is not enough","把最近工作、缺失 scientific object 和论文真正的位置放在一起看。","Read closest work, the missing scientific object, and the paper's defended position together.",relatedWorkSummary(story)+readerGapDetails(story)+readerPaperCase(paper,story,detail))}${readerChapter("reader-evidence","03","我们怎么把问题变成可验证实验","How we test the claim","先看方法为什么这样设计，再看证据到底回答了哪些科学问题。","See why the design identifies the question, then what the evidence actually answers.",e1Work(paper,story,detail)+e1Results(paper,story,detail))}${readerChapter("reader-conclusion","04","结论、边界与完整研究演变","Conclusions, boundaries, and evolution","最后把贡献、不能说什么、完整研究转向和当前状态放回同一条故事线。","Bring contributions, boundaries, the full research evolution, and current state into one final arc.",e1Contributions(paper,detail)+e1EvolutionSection(paper,detail)+e1Status(paper,reg,detail))}${e1DeepDive(paper,reg,detail,story)}<div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div></main>`;
  const readerChapter=(id,index,titleZh,titleEn,leadZh,leadEn,body)=>`<section class="cpp-reader-chapter" id="${E(id)}"><header class="cpp-reader-chapter-head"><span>${E(index)}</span><div><div class="cpp-reader-chapter-kicker">${isZh()?"论文阅读主线":"PAPER READING PATH"}</div><h2>${E(isZh()?titleZh:titleEn)}</h2><p>${E(isZh()?leadZh:leadEn)}</p></div></header><div class="cpp-reader-chapter-body">${body}</div></section>`;
  const beginnerSpec=(pageId)=>{
    const factory=window.CURRENT_PAPER_BEGINNER_FACTORIES?.[pageId];
    return factory?factory((zh,en)=>isZh()?zh:en):null;
  };
  const beginnerQuick=(paper,spec)=>`<section class="cpp-plain cpp-e1-overview cpp-beginner-overview panel" id="quick-overview"><div class="cpp-section-kicker">${isZh()?"0 · 先看懂问题":"0 · START HERE"}</div><h3 class="cpp-subsection-title">${isZh()?"30 秒先抓住这篇论文在研究什么":"The paper in 30 seconds"}</h3><p class="cpp-e1-hook">${E(spec.hook)}</p><div class="cpp-e1-overview-grid"><article><span>${isZh()?"先看一个例子":"ONE EXAMPLE"}</span><p>${E(spec.example)}</p></article><article><span>${isZh()?"本文真正的问题":"THE QUESTION"}</span><p>${E(T(paper.question))}</p></article><article class="answer"><span>${isZh()?"一句话答案":"THE ANSWER"}</span>${readableParagraphs(spec.answer)}</article></div><div class="cpp-term-strip">${spec.terms.map(x=>`<span><b>${E(plainTermLabel(x[0]))}</b>${E(x[1])}</span>`).join("")}</div></section>`;
  const beginnerOrigin=(spec)=>`<section class="panel cpp-origin cpp-e1-origin cpp-beginner-origin" id="problem-origin"><div class="cpp-section-kicker">${isZh()?"1 · 为什么会有这个问题":"1 · WHY THIS PROBLEM EXISTS"}</div><h3 class="cpp-subsection-title">${isZh()?"这个研究问题是怎么一步步冒出来的？":"How did this research problem emerge?"}</h3><p class="cpp-reader-long-lead">${isZh()?"这里先不急着讲方法。先把论文出现之前的现实矛盾说清楚：研究者原本默认什么、哪个现象让这个默认开始可疑，以及为什么最后必须把它变成一个单独的科学问题。":"Before methods, reconstruct the contradiction that created the paper: what was originally assumed, what observation made that assumption doubtful, and why it became a standalone scientific question."}</p><div class="cpp-origin-grid">${spec.origin.map(x=>`<article><b>${E(x[0])}</b><p>${E(x[1])}</p></article>`).join("")}</div></section>`;
  const summaryLiterature=(dossier)=>{
    const groups=(dossier?.approaches||[]).map(a=>({name:a.name||"",works:rankedWorks(a.closest_work||[]).slice(0,2)})).filter(x=>x.works.length);
    if(!groups.length)return "";
    return `<div class="cpp-gap-literature"><div class="cpp-gap-literature-head"><b>${isZh()?"代表工作 · 会议 / 年份":"Representative work · venue / year"}</b><span>${isZh()?"正式发表显示 venue；未正式发表保留 arXiv。":"Published work shows its venue; preprints remain arXiv."}</span></div><div class="cpp-gap-literature-grid">${groups.map(g=>`<article><strong>${E(plainUiLabel(g.name))}</strong>${g.works.map(w=>`<a href="${E(w.url||w.u||"#")}" target="_blank" rel="noopener"><span>${E(w.title||w.t||"")}</span>${venueYearTag(w)?`<em class="cpp-venue-tag">${E(venueYearTag(w))}</em>`:""}</a>`).join("")}</article>`).join("")}</div></div>`;
  };
  const readerGapDetails=(dossier)=>{
    const gaps=(dossier?.gaps||[]).filter(x=>x&&typeof x==="object");
    const approaches=(dossier?.approaches||[]);
    if(!gaps.length&&!approaches.length)return "";
    return `<details class="cpp-reader-context cpp-reader-gap-context cpp-layered-detail"><summary><div><b>${isZh()?"想继续追：每一类现有方法为什么还不够？":"Open the paradigm-by-paradigm gap analysis"}</b><span>${isZh()?"默认正文已经给出最近论文和核心缺口；这里保留更细的范式分析。":"The default story already gives recent papers and core gaps; this preserves the deeper paradigm analysis."}</span></div><em>${isZh()?"深入一层":"DETAIL"}</em></summary><div class="cpp-layered-detail-body">${gaps.length?`<div class="cpp-reader-gap-grid">${gaps.map(x=>`<article><b>${E(isZh()?(x.title_zh||x.title_en):(x.title_en||x.title_zh))}</b><p>${E(isZh()?(x.text_zh||x.text_en):(x.text_en||x.text_zh))}</p></article>`).join("")}</div>`:""}${approaches.length?`<div class="cpp-reader-approach-list">${approaches.map(a=>`<article><b>${E(plainUiLabel(a.name||""))}</b><p><strong>${isZh()?"现有方法在做什么：":"What it does: "}</strong>${E(storyText(a,"how"))}</p><p><strong>${isZh()?"为什么还不够：":"Why it is still insufficient: "}</strong>${E(storyText(a,"problem"))}</p></article>`).join("")}</div>`:""}</div></details>`;
  };
  const readerPaperCase=(paper,dossier,detail)=>{
    const audit=detail?.working_novelty_audit;
    const prior=(dossier?.approaches||[]).map(a=>plainUiLabel(a.name)).filter(Boolean).join(" · ");
    const object=T(paper?.thesis)||T(audit?.defended_residual)||T(audit?.surviving_axis)||T(dossier?.missing_scientific_object);
    const why=T(detail?.interpretation?.importance)||T(dossier?.why_better);
    const formalBoundary=(paper?.boundaries||[]).slice(0,2).map(T).filter(Boolean).join(" ");
    const stop=T(audit?.stop_rule)||formalBoundary||T(dossier?.boundary);
    const rows=[];
    if(audit?.surrender)rows.push([isZh()?"我们主动不再卖什么":"What we explicitly surrender",T(audit.surrender),"surrender"]);
    else if(prior)rows.push([isZh()?"已有工作已经覆盖什么":"What prior work already covers",prior,"covered"]);
    if(object)rows.push([isZh()?"真正还缺的科学问题":"The scientific object that remains",object,"object"]);
    if(why)rows.push([isZh()?"为什么这件事值得单独研究":"Why this deserves a standalone study",why,"why"]);
    if(stop)rows.push([isZh()?(audit?"什么结果会让这个故事停下来":"当前必须守住的结论边界"):(audit?"What would stop or falsify this story":"Current claim boundary"),stop,"stop"]);
    if(!rows.length)return "";
    return `<div class="cpp-paper-case"><header><span>${isZh()?"为什么值得单独写成一篇论文":"WHY THIS DESERVES A PAPER"}</span><h3 data-toc="false">${isZh()?"把 novelty、必要性和可证伪边界一次说透":"Make the novelty, necessity, and falsification boundary explicit"}</h3><p>${isZh()?"这里不靠“我们的方法更好”来劝读者，而是把论证责任摊开：哪些东西别人已经做了、我们真正还缺什么、为什么当前实验能识别它，以及出现什么结果时我们应该放弃这个故事。":"This section does not sell the paper through a generic performance claim. It exposes the burden of proof: what prior work already covers, what object is still missing, why the design identifies it, and what result should make us abandon the story."}</p></header><div class="cpp-paper-case-grid">${rows.map(([k,v,c])=>`<article class="${c}"><b>${E(k)}</b><p>${E(v)}</p></article>`).join("")}</div></div>`;
  };
  const readerDesignDetails=(detail,story)=>{
    if(!detail)return "";
    const requirements=(story?.design_requirements||[]),primary=requirements.slice(0,3);
    const audit=requirements.length||detail.contract?.length||detail.arms?.length||detail.analysis?.length;
    return `<div class="cpp-reader-context cpp-reader-design-context"><h3 data-toc="false">${isZh()?"为什么这个实验设计能回答问题，而不是只做一个漂亮对比？":"Why this design identifies the question instead of merely producing a comparison"}</h3><p class="cpp-reader-long-lead">${isZh()?"先看三个原则：只改一个关键条件；其它重要条件尽量保持一致；最后用与论文问题直接对应的结果判断，而不是挑一个好看的总分。":"Start with three principles: change one key condition, match the other important conditions, and judge the result with outcomes tied directly to the claim."}</p>${primary.length?`<div class="cpp-design-principles">${primary.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><p>${E(T(x))}</p></article>`).join("")}</div>`:""}${audit?`<details class="cpp-layered-detail cpp-design-audit"><summary><div><b>${isZh()?"展开完整实验设计：所有固定条件、实验组和分析规则":"Open the full design contract, arms, and analysis rules"}</b><span>${isZh()?"第一次阅读先理解上面的公平比较原则；复现或审稿时再看这里。":"Understand the fairness principles first; use this layer for reproduction or review."}</span></div><em>${isZh()?"严谨设计":"AUDIT"}</em></summary><div class="cpp-layered-detail-body">${detail.design?`<p class="cpp-reader-long-lead">${E(T(detail.design))}</p>`:""}${requirements.length?`<div class="cpp-reader-requirements"><b>${isZh()?"完整设计要求":"Full design requirements"}</b>${list(requirements,"good")}</div>`:""}${detail.contract?.length?`<h4>${isZh()?"哪些东西必须保持不变":"What must stay fixed"}</h4>${contract(detail)}`:""}${detail.arms?.length?`<h4>${isZh()?"每个实验组分别在排除什么解释":"What each experimental arm rules out"}</h4>${arms(detail)}`:""}${detail.analysis?.length?`<h4>${isZh()?"分析时真正看什么":"What the analysis reads"}</h4>${analysisPlan(detail)}`:""}</div></details>`:""}</div>`;
  };
  const readerEvidenceDetails=(detail,story)=>{
    const fullRqs=storyExperiments(story),meaning=interpretation(detail);
    if(!fullRqs&&!meaning)return "";
    return `<div class="cpp-reader-context cpp-reader-evidence-context"><h3 data-toc="false">${isZh()?"把结果翻成人话：它支持什么，又没有证明什么？":"Translate the evidence: what is supported and what is not?"}</h3>${meaning}${fullRqs?`<details class="cpp-layered-detail cpp-rq-audit"><summary><div><b>${isZh()?"展开完整 RQ / 对照 / 当前答案账本":"Open the full RQ/control/answer ledger"}</b><span>${isZh()?"默认先记住结论边界；需要逐个核实验时再展开。":"Remember the claim boundary first; open this to audit every research question."}</span></div><em>${isZh()?"完整 RQ":"AUDIT"}</em></summary><div class="cpp-layered-detail-body">${fullRqs}</div></details>`:""}</div>`;
  };
  const cleanEvolutionTitle=(v)=>String(T(v)||"").replace(/^\s*\d+\s*[·.、:-]\s*/,"");
  const evolutionRows=(rows,start=1)=>`<div class="cpp-evolution cpp-evolution-detailed">${(rows||[]).map((x,i)=>`<article><span>${String(start+i).padStart(2,"0")}</span><div><strong>${E(cleanEvolutionTitle(x.title||x.t))}</strong><p>${E(T(x.body||x.b))}</p></div></article>`).join("")}</div>`;
  const readerEvolution=(paper,detail,spec,customRows=null)=>{
    const origins=(spec.origin||[]).map(x=>({title:x[0],body:x[1]}));
    const chronology=customRows||(paper.evolution||[]);
    const decisions=detail?.lineage||[];
    const chronologyStart=origins.length+1, decisionStart=chronologyStart+chronology.length;
    return `<section class="panel cpp-beginner-evolution cpp-full-evolution" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"6 · 完整研究演变与关键决策":"6 · FULL RESEARCH EVOLUTION & DECISIONS"}</div><h3 class="cpp-subsection-title">${E(spec.evolutionTitle)}</h3><p class="cpp-reader-long-lead">${isZh()?"这里按真实研究顺序把整条路线重新走一遍，而不是只总结最终版本。前面第 1 节讲过的早期矛盾也会重新并入时间线，因为只有把起点、反例、改判、放弃路线和当前 formulation 连起来，才能看懂这篇论文为什么值得相信。":"This section replays the whole project in research order rather than summarizing only the final formulation. Early contradictions from Section 1 are intentionally reintroduced so the reader can connect the starting assumption, counterexamples, reversals, abandoned routes, and current formulation."}</p>${origins.length?`<div class="cpp-evolution-phase origin"><header><span>${isZh()?"起点与早期直觉":"ORIGIN & EARLY INTUITION"}</span><b>${isZh()?"论文出现以前，我们原本怎么理解这个问题":"What we believed before the paper existed"}</b></header>${evolutionRows(origins,1)}</div>`:""}${chronology.length?`<div class="cpp-evolution-phase"><header><span>${isZh()?"证据如何改写问题":"EVIDENCE-DRIVEN REFORMULATION"}</span><b>${isZh()?"哪些观察、反例或实验迫使故事发生转向":"Which observations or counterexamples forced the story to change"}</b></header>${evolutionRows(chronology,chronologyStart)}</div>`:""}${decisions.length?`<div class="cpp-evolution-phase decision"><header><span>${isZh()?"关键科研决策":"RESEARCH DECISIONS"}</span><b>${isZh()?"哪些路线被主动放弃，为什么不能再往回走":"What was deliberately abandoned, and why"}</b></header><div class="cpp-lineage">${decisions.map((x,i)=>`<article><span>${String(decisionStart+i).padStart(2,"0")}</span><div><b>${E(T(x.title))}</b><p>${E(T(x.body))}</p></div></article>`).join("")}</div></div>`:""}<div class="cpp-evolution-current"><b>${isZh()?"为什么今天是这个版本":"Why the paper has this form today"}</b><p>${E(T(paper.thesis))}</p><p><strong>${isZh()?"当前状态：":"Current state: "}</strong>${E(spec.statusHeadline||T(paper.experiment?.headline))}</p><p><strong>${isZh()?"下一步不是随便补实验，而是：":"The next step is not arbitrary extra experimentation: "}</strong>${E(spec.nextPlain||T(paper.next))}</p></div></section>`;
  };
  const beginnerGaps=(pageId,paper,spec,dossier,detail)=>`<section class="panel cpp-related-summary cpp-beginner-gaps" id="related-work-comparison"><div class="cpp-section-kicker">${isZh()?"2 · 现有研究缺什么":"2 · WHAT PRIOR WORK STILL MISSES"}</div><h3 class="cpp-subsection-title">${isZh()?"为什么不能直接用现有思路回答？":"Why do existing approaches not answer the exact question?"}</h3><p class="cpp-design-lead">${E(spec.gapLead)}</p>${featuredPublishedWork(pageId)}<div class="cpp-related-summary-grid">${spec.gaps.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><b>${E(x[0])}</b><p><strong>${isZh()?"已经能做：":"What it already does: "}</strong>${E(x[1])}</p><p><strong>${isZh()?"还缺：":"What is still missing: "}</strong>${E(x[2])}</p></article>`).join("")}</div>${summaryLiterature(dossier)}${readerGapDetails(dossier)}${readerPaperCase(paper,dossier,detail)}<div class="cpp-gap-callout"><b>${isZh()?`${paper.code} 真正切入的位置`:`Where ${paper.code} enters`}</b><p>${E(T(paper.thesis))}</p></div></section>`;
  const beginnerWork=(pageId,spec,detail,story)=>`<section class="panel cpp-e1-work cpp-beginner-work" id="mechanism"><div class="cpp-section-kicker">${isZh()?"3 · 我们具体做了什么":"3 · WHAT WE DID"}</div><h3 class="cpp-subsection-title">${isZh()?"我们围绕这个问题做了哪些工作，为什么每一层都需要？":"What did we build around this question, and why is each layer necessary?"}</h3><div class="cpp-work-grid">${spec.work.map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><b>${E(plainUiLabel(x[0]))}</b><strong>${E(plainUiLabel(x[1]))}</strong><p>${E(x[2])}</p></div></article>`).join("")}</div><div class="cpp-simple-chain"><b>${isZh()?"先用一条简单链理解整篇论文":"A simple chain for the whole paper"}</b><div>${spec.chain.map((x,i)=>`${i?'<i>→</i>':''}<span>${E(x)}</span>`).join("")}</div></div>${experimentProvenance(pageId)}${readerDesignDetails(detail,story)}</section>`;
  const beginnerResults=(spec,detail,story)=>`<section class="panel cpp-e1-results cpp-beginner-results" id="experiment-results"><div class="cpp-section-kicker">${isZh()?"4 · 实验现在回答了什么":"4 · WHAT THE EVIDENCE ANSWERS"}</div><h3 class="cpp-subsection-title">${isZh()?"按科学问题读结果：已经回答什么，还没回答什么？":"Read the evidence by scientific question: what is answered and what is not?"}</h3><div class="cpp-e1-rq-grid">${spec.rqs.map(x=>`<article><header><span>${E(x[0])}</span><b>${E(x[1])}</b></header><p class="cpp-rq-how"><strong>${isZh()?"怎么测：":"How: "}</strong>${E(x[2])}</p><div class="cpp-rq-answer"><strong>${isZh()?"当前答案":"Current answer"}</strong><p>${E(x[3])}</p></div></article>`).join("")}</div><h3 data-toc="false">${isZh()?"目前最关键的证据":"Evidence worth remembering"}</h3><div class="cpp-proof-grid cpp-proof-grid-three">${spec.evidence.map(x=>`<article><strong>${E(plainUiLabel(x[0]))}</strong><p>${E(x[1])}</p></article>`).join("")}</div>${readerEvidenceDetails(detail,story)}</section>`;
  const beginnerContributions=(spec,detail)=>`<section class="panel cpp-e1-contributions cpp-beginner-contributions" id="claim-boundary"><div class="cpp-section-kicker">${isZh()?"5 · 最终贡献与边界":"5 · CONTRIBUTIONS & BOUNDARIES"}</div><h3 class="cpp-subsection-title">${isZh()?"所以这篇论文 / 科学对象真正让我们多知道了什么？":"What do we know because of this paper or scientific object?"}</h3><div class="cpp-contribution-grid">${spec.contributions.map(x=>`<article><span>${E(x[0])}</span><div><b>${E(x[1])}</b><p>${E(x[2])}</p></div></article>`).join("")}</div>${detail?.interpretation?.importance?`<div class="cpp-contribution-why"><b>${isZh()?"为什么读者应该在意这件事":"Why this matters beyond this one experiment"}</b><p>${E(T(detail.interpretation.importance))}</p></div>`:""}<div class="cpp-boundary-box"><b>${isZh()?"同样重要：现在明确不能写成什么":"Equally important: what cannot currently be claimed"}</b>${list(spec.limits.map(x=>({zh:x,en:x})),"boundary")}</div></section>`;
  const beginnerStatus=(paper,reg,spec)=>`<section class="panel cpp-next cpp-e1-status cpp-beginner-status" id="next-gate"><div class="cpp-section-kicker">${isZh()?"7 · 当前状态与下一步":"7 · CURRENT STATE & NEXT"}</div><h3 class="cpp-subsection-title">${E(spec.statusHeadline)}</h3>${statePrimer(paper,reg)}<div class="cpp-e1-state-grid">${spec.statusCards.map((x,i)=>`<article class="${i?"hold":""}"><span>${E(x[0])}</span><strong>${E(x[1])}</strong><p>${E(x[2])}</p></article>`).join("")}</div><div class="cpp-next-action"><b>${isZh()?"下一步用一句话说":"Next, in plain language"}</b><p>${E(spec.nextPlain)}</p></div>${registryBox(paper,reg)}</section>`;
  const beginnerDeepDive=(paper,reg,detail,story,spec)=>{
    const dossier=story||detail;
    const fullRelated=relatedWorkComparison(dossier).replace('id="related-work-comparison"','id="related-work-full"');
    const legacy=reg&&window.renderPaperLegacyAuditBundle?window.renderPaperLegacyAuditBundle(paper.registryPaperId):"";
    return `<details class="cpp-deep-dive system-deep-dive" id="research-archive"><summary><span><b>${isZh()?"研究档案 / 想看严谨细节时再展开":"Research dossier / open for rigorous detail"}</b><small>${isZh()?"默认正文已经讲完论文故事；这里保留模型、数据、冻结合同、完整设计、逐篇 Related Work collision 与审计记录。":"The default story is complete above; this fold preserves models, data, frozen contracts, full design, paper-by-paper related-work collisions, and audit records."}</small></span><em>${isZh()?"展开细节":"Open details"}</em></summary><div class="cpp-deep-dive-body"><section class="panel cpp-glossary"><div class="cpp-section-kicker">${isZh()?"先把术语翻成人话":"PLAIN-LANGUAGE GLOSSARY"}</div><h2 data-toc="false">${isZh()?"上面最容易卡住的三个词是什么意思？":"Three terms that make the page easier to read"}</h2><div class="cpp-glossary-grid">${spec.terms.map(x=>`<article><b>${E(x[0])}</b><p>${E(x[1])}</p></article>`).join("")}</div></section>${snapshot(detail)}<section class="panel" id="models-data"><div class="cpp-section-kicker">${isZh()?"实验对象":"EXPERIMENTAL SUBSTRATE"}</div><h2>${isZh()?"具体用了什么模型、数据和环境？":"Which models, data, and environments were used?"}</h2>${modelData(detail)}</section>${detail.contract?.length?`<section class="panel" id="experiment-contract"><div class="cpp-section-kicker">${isZh()?"冻结实验合同":"FROZEN EXPERIMENT CONTRACT"}</div><h2>${isZh()?"为了保证比较公平，哪些东西必须固定？":"What must stay fixed for a fair comparison?"}</h2>${contract(detail)}</section>`:""}<section class="panel" id="experiment-design"><div class="cpp-section-kicker">${isZh()?"完整实验设计":"FULL EXPERIMENT DESIGN"}</div><h2>${isZh()?"严谨版本：实验到底怎么识别这个问题？":"Rigorous version: how does the experiment identify the question?"}</h2><p class="cpp-design-lead">${E(T(detail.design))}</p>${arms(detail)}${storyExperiments(dossier)}${analysisPlan(detail)}</section>${fullRelated}${fullStoryArchive(dossier)}${failureBoundaries(dossier)}${!reg?workingNoveltyAudit(detail):""}${replayNotes(detail)}${legacy}</div></details>`;
  };
  const renderBeginnerPage=(pageId,paper,reg,detail,story)=>{
    const spec=beginnerSpec(pageId); if(!spec)return "";
    const dossier=story||detail;
    return `<main class="cpp-page cpp-e1-page cpp-beginner-page" data-paper-order="${paper.order}"><header class="cpp-hero"><div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div><div class="eyebrow">${E(T(paper.area))}</div><h1>${E(T(paper.title))}</h1><p class="cpp-hero-subtitle">${E(spec.hook)}</p><p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>${heroLinks(paper,reg)}</header>${readerChapter("reader-understand","01","先理解这篇论文","Understand the paper","先建立问题直觉和研究起点，不急着进入方法细节。","Establish the intuition and research origin before entering method details.",beginnerQuick(paper,spec)+termPrimer(pageId)+beginnerOrigin(spec))}${readerChapter("reader-position","02","为什么现有研究还不够","Why prior work is not enough","把 closest work、研究缺口、novelty boundary 和值得成文的理由放在同一层。","Put closest work, gaps, novelty boundaries, and the case for a standalone paper in one layer.",beginnerGaps(pageId,paper,spec,dossier,detail))}${readerChapter("reader-evidence","03","我们怎么验证这个问题","How we test the claim","方法与实验不分开讲：先解释为什么设计可识别，再看证据支持到哪里。","Method and experiment stay together: why the design identifies the question, then what the evidence supports.",beginnerWork(pageId,spec,detail,story)+beginnerResults(spec,detail,story))}${readerChapter("reader-conclusion","04","结论、边界与完整研究演变","Conclusions, boundaries, and evolution","把贡献、不能说什么、研究转向和下一步放在一个完整收口章节里。","Close with contributions, unsupported claims, research turns, and the actual next step.",beginnerContributions(spec,detail)+readerEvolution(paper,detail,spec)+beginnerStatus(paper,reg,spec))}${beginnerDeepDive(paper,reg,detail,story,spec)}<div class="cpp-back-collection"><a href="selected-paper.html">${isZh()?"← 返回当前论文合集":"← Back to current paper collection"}</a></div></main>`;
  };
  const collectionCard=(id,paper)=>{
    const d=detailFor(id), reg=registryPaper(paper), label=T(d.collectionLabel)||`${orderMark(paper.order)} ${paper.code}`;
    const models=(d.models||[]).slice(0,2).map(x=>x.name).join(" · ")||"—";
    const datasets=(d.datasets||[]).slice(0,2).map(x=>x.name).join(" · ")||"—";
    return `<a class="cpp-collection-card" href="${E(paper.href)}"><header><span>${E(label)}</span><em title="${E(paperState(paper,reg))}">${E(paper.displayStateShort||paperState(paper,reg))}</em></header><h3>${E(T(paper.title))}</h3><p>${E(T(paper.question))}</p><dl><div><dt>${isZh()?"模型":"Model"}</dt><dd>${E(models)}</dd></div><div><dt>${isZh()?"数据":"Data"}</dt><dd>${E(datasets)}</dd></div></dl><footer><span>${E(kindLabel(paper))}</span><b>${isZh()?"打开单篇 →":"Open paper →"}</b></footer></a>`;
  };
  const budgetTier=(tier)=>({low:isZh()?"低":"Low",medium:isZh()?"中":"Medium",high:isZh()?"高":"High","very-high":isZh()?"最高":"Very high"}[tier]||tier||"—");
  const atomgitKind=(status)=>({engineering:isZh()?"工程可用":"Engineering",conditional:isZh()?"条件式科学候选":"Conditional science",future:isZh()?"未来新 arm 候选":"Future new-arm candidate"}[status]||status||"—");
  const budgetSection=()=>{
    const d=window.CURRENT_PAPER_BUDGET;
    if(!d?.rows?.length)return "";
    const a=d.atomgit||{}, s=d.spendPlan||{}, rows=d.rows;
    const localGpu=rows.filter(x=>/A100|VLA GPU|local VLA/i.test(`${T(x.gpu)} ${T(x.costDriver)}`)).length;
    const apiSensitive=rows.filter(x=>/DeepSeek|Qwen397|LLM actor|provider/i.test(`${T(x.api)} ${T(x.costDriver)}`) && !/external provider calls = 0|no commercial LLM API|没有商业 LLM/i.test(T(x.api))).length;
    const directCandidate=rows.filter(x=>x.atomgit?.status==="conditional").length;
    const sourceLinks=(a.sources||[]).map(s=>`<a href="${E(s.url)}" target="_blank" rel="noopener noreferrer">${E(s.label)} ↗</a>`).join("");
    const spendSourceLinks=(s.sources||[]).map(x=>`<a href="${E(x.url)}" target="_blank" rel="noopener noreferrer">${E(x.label)} ↗</a>`).join("");
    const spendCards=(s.pools||[]).map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><b>${E(x.name)}</b><strong>${E(T(x.cash))}</strong><p>${E(T(x.papers))}</p><small>${E(T(x.rule))}</small></article>`).join("");
    const atomgitModels=(a.models||[]).map(x=>`<span>${E(x)}</span>`).join("");
    const tableRows=rows.map((r,i)=>`<tr>
      <th scope="row"><span class="cpp-budget-paper-index">${String(i+1).padStart(2,"0")}</span><a href="${E(window.CURRENT_PAPER_PAGES?.papers?.[r.id]?.href||"#")}">${E(r.paper)}</a><small>${E(T(r.costDriver))}</small></th>
      <td><b>${E(T(r.gpu))}</b><span>${E(T(r.cpu))}</span></td>
      <td><b>${E(T(r.api))}</b><span>${E(T(r.envelope))}</span></td>
      <td><span class="cpp-budget-tier cpp-budget-tier-${E(r.tier)}">${E(budgetTier(r.tier))}</span><p>${E(T(r.cash))}</p></td>
      <td><span class="cpp-atomgit-tag cpp-atomgit-${E(r.atomgit?.status)}">${E(atomgitKind(r.atomgit?.status))}</span><b>${E(T(r.atomgit?.label))}</b><p>${E(T(r.atomgit?.use))}</p></td>
    </tr>`).join("");
    return `<section class="cpp-collection-group cpp-budget" id="paper-resource-budget"><header><div><span>成本</span><div><h2>${isZh()?"9 篇论文的实验资源与剩余成本账本":"Resource and remaining-cost ledger for all nine papers"}</h2><p>${isZh()?`截至 ${d.as_of}。这里区分本地 GPU、CPU/环境、商业模型 API 与 AtomGit Pro；hard cap 只是 fail-closed 上限，不等于一定会花满。`:`As of ${d.as_of}. This ledger separates local GPU, CPU/environment work, commercial model APIs, and AtomGit Pro; hard caps are fail-closed ceilings, not expected spend.`}</p></div></div></header>
      <div class="cpp-budget-kpis"><article><span>${isZh()?"本地 GPU 主导 / 显著":"Local-GPU material"}</span><b>${localGpu}</b><p>${isZh()?"B1、Paper A/B、3D 等以本地卡为主":"B1, Papers A/B, 3D and related local-GPU lanes"}</p></article><article><span>${isZh()?"API 敏感线":"API-sensitive lanes"}</span><b>${apiSensitive}</b><p>${isZh()?"冻结模型服务商的旧实验不能为了省钱换模型":"Frozen provider/model identities cannot be changed to save money"}</p></article><article><span>AtomGit Pro</span><b>500 / 5h</b><p>${isZh()?"滚动请求窗口；总 Token 不设月度总量上限":"rolling requests; no monthly total-token cap"}</p></article><article><span>${isZh()?"可直接研究候选":"Direct science candidate"}</span><b>${directCandidate} / 9</b><p>${isZh()?"当前 frozen / active scientific lane 均不应直接改用 CodingPlan":"No current frozen/active scientific lane should be switched directly to CodingPlan"}</p></article></div>
      <div class="cpp-budget-note"><b>${isZh()?"怎么算成本":"Budget convention"}</b><p>${isZh()?"已有服务器上的 GPU 记为“占卡 / 电力 / 机会成本”，商业 API 才记为直接 Token / 请求现金成本。已经完成的实验算 sunk cost；HOLD 线在合法 reopen 前按 0 新增科学开销处理。":"GPU use on owned servers is counted as occupancy/electricity/opportunity cost, while commercial APIs create direct token/request cash cost. Completed experiments are sunk cost; HOLD lanes carry zero new scientific spend until a valid reopen."}</p></div>
      <div class="cpp-budget-table-wrap"><table class="cpp-budget-table"><thead><tr><th>${isZh()?"论文":"Paper"}</th><th>${isZh()?"GPU / CPU / 环境":"GPU / CPU / environment"}</th><th>${isZh()?"模型 API / 当前 envelope":"Model API / current envelope"}</th><th>${isZh()?"边际成本":"Marginal cost"}</th><th>${isZh()?"AtomGit Pro 怎么分配":"How to allocate AtomGit Pro"}</th></tr></thead><tbody>${tableRows}</tbody></table></div>
      ${spendCards?`<section class="cpp-cash-plan" id="cash-budget-plan"><header><div class="cpp-section-kicker">${isZh()?"人民币预算口径":"CASH BUDGET"}</div><h3>${isZh()?"订阅、按量 API 和自有 GPU 分开记账":"Separate subscriptions, metered APIs, and owned GPUs"}</h3><p>${E(T(s.headline))}</p><strong>${E(T(s.monthly))}</strong></header><div class="cpp-cash-grid">${spendCards}</div>${spendSourceLinks?`<div class="cpp-budget-sources"><span>${isZh()?"价格 / 套餐参考":"Pricing references"}</span>${spendSourceLinks}</div>`:""}</section>`:""}
      <section class="cpp-atomgit-plan" id="atomgit-pro-allocation"><div><div class="cpp-section-kicker">AtomGit CodingPlan Pro</div><h3>${isZh()?"把 500 次 / 5h 当科研工程池，而不是第十个实验变量":"Use the 500 / 5h window as an engineering pool, not a tenth experimental variable"}</h3><p>${E(T(a.rule))}</p>${atomgitModels?`<div class="cpp-atomgit-models"><b>${isZh()?"当前 Pro 模型":"Current Pro models"}</b>${atomgitModels}</div>`:""}</div><div class="cpp-atomgit-grid"><article><span>01</span><b>${isZh()?"9/9：都能分工程任务":"9/9: engineering work fits"}</b><p>${E(T(a.automation))}</p></article><article><span>02</span><b>${isZh()?"E1 / C1 / E2：不替换冻结执行模型":"E1 / C1 / E2: do not replace frozen actors"}</b><p>${isZh()?"用 Pro 修 runner、preflight、ledger、provenance 与论文，不把 Flash/27B 偷换成 Pro/397B。":"Use Pro for runners, preflight, ledgers, provenance, and paper work; never swap Flash/27B into Pro/397B treatments."}</p></article><article><span>03</span><b>${isZh()?"Constraint：未来第二主干模型最合适":"Constraint: best future second-backbone fit"}</b><p>${isZh()?"当前 qwen3.7-plus 已在能力资格验证中，不能中途替换；以后若需要外部有效性，可从零开始预注册 AtomGit 独立实验臂。":"qwen3.7-plus is already in capability qualification and should not be replaced midstream; a future external-validity study can preregister a fresh AtomGit arm from scratch."}</p></article><article><span>04</span><b>${isZh()?"GPU 论文：Pro 只省人力，不省显存":"GPU papers: saves engineering time, not VRAM"}</b><p>${isZh()?"B1、Paper A/B、3D 的科学算力仍来自本地 GPU；Pro 最适合调度、监控、测试与故障恢复。":"B1, Papers A/B, and 3D still need local GPU compute; Pro is best for orchestration, monitoring, testing, and recovery."}</p></article></div><div class="cpp-budget-sources"><span>${isZh()?"计划说明来源":"Plan references"}</span>${sourceLinks}</div></section>
    </section>`;
  };
  window.renderCurrentPaperCollection=()=>{
    const data=window.CURRENT_PAPER_PAGES||{}, ids=data.order||[];
    const formal=ids.slice(0,5).map(id=>[id,data.papers?.[id]]).filter(([,p])=>p);
    const working=ids.slice(5).map(id=>[id,data.papers?.[id]]).filter(([,p])=>p);
    return `<main class="cpp-collection"><header class="cpp-collection-hero"><div class="eyebrow">${isZh()?"当前科研 · 论文合集":"CURRENT RESEARCH · PAPER COLLECTION"}</div><h1>${isZh()?"9 篇论文，一页先看清楚，再进入单篇":"Nine papers: compare here, read details on each paper page"}</h1><p>${isZh()?"①–⑤ 是正式 PaperRegistry；⑥–⑦ 是工作论文；⑧–⑨ 是独立 Scientific Object。合集页只显示定位、状态、模型/数据和入口，不再重复单篇正文。":"①–⑤ are formal PaperRegistry papers; ⑥–⑦ are working papers; ⑧–⑨ are independent scientific objects. This collection shows positioning, status, model/data, and navigation only."}</p><div class="cpp-collection-stats"><span><b>5</b>${isZh()?"正式论文":"formal papers"}</span><span><b>2</b>${isZh()?"工作论文":"working papers"}</span><span><b>2</b>${isZh()?"独立科学对象":"Scientific objects"}</span><span><b>9</b>${isZh()?"独立阅读页":"reader pages"}</span></div></header>${budgetSection()}<section class="cpp-collection-group" id="formal-paper-collection"><header><div><span>01–05</span><div><h2>${isZh()?"正式 PaperRegistry 主线":"Formal PaperRegistry portfolio"}</h2><p>${isZh()?"论文状态仍以 canonical PaperRegistry 为准；当前扩展不会自动改写正式主张。":"Formal state remains canonical in PaperRegistry; current extensions do not automatically rewrite frozen claims."}</p></div></div></header><div class="cpp-collection-grid">${formal.map(([id,p])=>collectionCard(id,p)).join("")}</div></section><section class="cpp-collection-group" id="working-paper-collection"><header><div><span>06–09</span><div><h2>${isZh()?"工作论文与独立 Scientific Object":"Working papers and independent scientific objects"}</h2><p>${isZh()?"没有人为补 E3/G2 等正式编号；达到独立 paper gate 后再进入 PaperRegistry。":"No formal publication codes are invented; PaperRegistry promotion happens only after an independent paper gate."}</p></div></div></header><div class="cpp-collection-grid">${working.map(([id,p])=>collectionCard(id,p)).join("")}</div></section></main>`;
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
