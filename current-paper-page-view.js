(()=>{
  const E=(v)=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const isZh=()=>document.documentElement.lang==="zh-CN";
  const T=(v)=>v&&typeof v==="object"?(isZh()?v.zh:v.en)||v.zh||v.en||"":v||"";
  const registryPaper=(paper)=>paper.registryPaperId?(window.PAPER_REGISTRY?.papers||[]).find(p=>p.paper_id===paper.registryPaperId):null;
  const kindLabel=(paper)=>{
    if(paper.kind==="registry") return isZh()?"正式 PaperRegistry":"Formal PaperRegistry";
    if(paper.kind==="registry-extension") return isZh()?"正式 E2 + 当前科学扩展":"Formal E2 + current extension";
    if(paper.kind==="scientific-object") return isZh()?"独立 Scientific Object · 未入 PaperRegistry":"Independent scientific object · not in PaperRegistry";
    return isZh()?"工作论文 · 未入 PaperRegistry":"Working paper · not in PaperRegistry";
  };
  const statusBadge=(paper,reg)=>{
    if(reg){
      const state=reg.paper_stage||reg.current_state||"PaperRegistry";
      return `<span class="cpp-badge cpp-badge-strong">${E(state)}</span><span class="cpp-badge">${E(reg.scientific_status||"")}</span>`;
    }
    return `<span class="cpp-badge cpp-badge-working">${E(kindLabel(paper))}</span>`;
  };
  const mechanism=(paper)=>`<div class="cpp-flow">${(paper.mechanism||[]).map((s,i)=>`<article class="cpp-flow-step"><span>${E(s.n)}</span><strong>${E(isZh()?s.zh:s.en)}</strong><p>${E(isZh()?s.dzh:s.den)}</p></article>${i<(paper.mechanism.length-1)?'<i aria-hidden="true">→</i>':''}`).join("")}</div>`;
  const metrics=(paper)=>`<div class="cpp-metrics">${(paper.experiment?.metrics||[]).map(m=>`<div><span>${E(T(m.k))}</span><strong>${E(m.v)}</strong></div>`).join("")}</div>`;
  const evolution=(paper)=>`<div class="cpp-evolution">${(paper.evolution||[]).map((x,i)=>`<article><span>${String(i+1).padStart(2,"0")}</span><div><strong>${E(T(x.t))}</strong><p>${E(T(x.b))}</p></div></article>`).join("")}</div>`;
  const bullets=(rows,klass="")=>`<ul class="cpp-list ${klass}">${(rows||[]).map(x=>`<li>${E(T(x))}</li>`).join("")}</ul>`;
  const pager=(pageId)=>{
    const data=window.CURRENT_PAPER_PAGES;
    const ix=data.order.indexOf(pageId);
    const prev=ix>0?data.papers[data.order[ix-1]]:null;
    const next=ix>=0&&ix<data.order.length-1?data.papers[data.order[ix+1]]:null;
    return `<nav class="cpp-pager" aria-label="${isZh()?"论文顺序":"Paper order"}">${prev?`<a href="${E(prev.href)}"><small>${isZh()?"上一篇":"Previous"}</small><strong>← ${E(prev.order)} · ${E(prev.code)}</strong><span>${E(T(prev.short))}</span></a>`:'<span></span>'}${next?`<a class="next" href="${E(next.href)}"><small>${isZh()?"下一篇":"Next"}</small><strong>${E(next.order)} · ${E(next.code)} →</strong><span>${E(T(next.short))}</span></a>`:'<span></span>'}</nav>`;
  };
  const registryBox=(paper,reg)=>{
    if(!reg) return `<div class="cpp-registry-note working"><b>${isZh()?"身份说明":"Identity"}</b><p>${E(kindLabel(paper))}。${isZh()?"这个页面是只读研究说明，不会因此创建正式论文编号，也不会授予科学、实验、GPU 或投稿权限。":"This is a read-only research explanation. It does not create a formal publication code or grant scientific, experiment, GPU, or submission authority."}</p></div>`;
    const download=reg.publication_identity?.pdf||reg.downloads?.pdf||"";
    return `<div class="cpp-registry-note"><b>${isZh()?"Canonical PaperRegistry":"Canonical PaperRegistry"}</b><p>${E(reg.publication_identity?.label_zh&&isZh()?reg.publication_identity.label_zh:(reg.publication_identity?.label_en||paper.code))} · ${E(reg.paper_stage||reg.current_state||"")} · scientific ${E(reg.scientific_status||"")}</p><div class="cpp-actions"><a href="selected-paper.html?paper=${encodeURIComponent(reg.paper_id)}">${isZh()?"打开技术/审计总览":"Open technical/audit view"}</a>${download?`<a href="${E(download)}">${isZh()?"论文 PDF":"Paper PDF"}</a>`:""}</div></div>`;
  };
  const orderMark=(n)=>["①","②","③","④","⑤","⑥","⑦","⑧","⑨"][Number(n)-1]||String(n||"");
  window.renderCurrentPaperShelf=(opts={})=>{
    const data=window.CURRENT_PAPER_PAGES||{}, current=opts.current||"";
    const rows=(data.order||[]).map(id=>[id,data.papers?.[id]]).filter(([,paper])=>paper);
    return `<section class="cpp-shelf panel" id="current-paper-pages"><div class="cpp-shelf-head"><div><div class="cpp-section-kicker">${isZh()?"当前论文组合":"CURRENT PAPER PORTFOLIO"}</div><h2 data-toc="false">${isZh()?"九篇论文 / scientific object，一篇一个阅读页":"Nine papers / scientific objects, one reader page each"}</h2><p>${isZh()?"①–⑤ 是正式 PaperRegistry；⑥–⑨ 明确保留为工作论文或独立 scientific object，不伪造 E3 / G2 等正式编号。":"①–⑤ are formal PaperRegistry entries. ⑥–⑨ remain explicitly working papers or independent scientific objects; no publication codes are invented."}</p></div><a class="link-btn" href="selected-paper.html">${isZh()?"正式 PaperRegistry 总账 →":"Formal PaperRegistry ledger →"}</a></div><div class="cpp-shelf-grid">${rows.map(([id,paper])=>{const reg=registryPaper(paper);const state=paper.displayState||(reg?(reg.paper_stage||reg.current_state||"PaperRegistry"):(paper.kind==="scientific-object"?"PRE-F0":"WORKING"));return `<a class="cpp-shelf-card ${id===current?"active":""}" href="${E(paper.href)}"><span>${orderMark(paper.order)}</span><div><small>${E(paper.code)} · ${E(kindLabel(paper))}</small><b>${E(T(paper.short))}</b><p>${E(T(paper.title))}</p></div><em>${E(state)}</em></a>`;}).join("")}</div></section>`;
  };
  window.renderCurrentPaperPage=(pageId)=>{
    const paper=window.CURRENT_PAPER_PAGES?.papers?.[pageId];
    if(!paper) return `<div class="empty">Paper page unavailable.</div>`;
    const reg=registryPaper(paper);
    return `<main class="cpp-page" data-paper-order="${paper.order}">
      ${window.renderCurrentPaperShelf({current:pageId})}
      <header class="cpp-hero">
        <div class="cpp-hero-top"><span class="cpp-index">${String(paper.order).padStart(2,"0")}</span><div class="cpp-badges">${statusBadge(paper,reg)}</div></div>
        <div class="eyebrow">${E(T(paper.area))}</div>
        <h1>${E(T(paper.title))}</h1>
        <p class="cpp-canonical-title">${E(paper.canonicalTitle)}</p>
        <div class="cpp-hero-links"><a href="research-map.html">${isZh()?"领域研究组合图谱":"Research map"}</a><a href="paper-ideas.html">${isZh()?"研究组合 / ResearchItems":"Research portfolio"}</a><a href="selected-paper.html">${isZh()?"PaperRegistry 总览":"PaperRegistry overview"}</a></div>
      </header>

      <section class="cpp-plain panel" id="plain-language"><div class="cpp-section-kicker">${isZh()?"30 秒版":"30-second version"}</div><h2>${isZh()?"讲给小白听":"Explain it to a newcomer"}</h2><p class="cpp-plain-lead">${E(T(paper.plain))}</p><div class="cpp-question"><b>${isZh()?"一句话问题":"One question"}</b><span>${E(T(paper.question))}</span></div><div class="cpp-thesis"><b>${isZh()?"当前核心判断":"Current thesis"}</b><span>${E(T(paper.thesis))}</span></div></section>

      <section class="panel" id="mechanism"><div class="cpp-section-kicker">${isZh()?"机制":"Mechanism"}</div><h2>${isZh()?"这篇论文到底怎么想的":"How the mechanism is supposed to work"}</h2>${mechanism(paper)}</section>

      <section class="panel" id="experiment-status"><div class="cpp-section-kicker">${isZh()?"当前实验":"Current experiment"}</div><h2>${isZh()?"实验现在做到哪了":"Where the experiments stand"}</h2><p class="cpp-status-headline">${E(T(paper.experiment?.headline))}</p>${metrics(paper)}<div class="cpp-now"><b>${isZh()?"现场解释":"What this means"}</b><p>${E(T(paper.experiment?.now))}</p></div></section>

      <section class="panel" id="paper-evolution"><div class="cpp-section-kicker">${isZh()?"演变过程":"Evolution"}</div><h2>${isZh()?"这篇论文怎么一步步演变到今天":"How the paper evolved into its current form"}</h2>${evolution(paper)}</section>

      <section class="cpp-claim-grid" id="claim-boundary"><article class="panel"><div class="cpp-section-kicker">${isZh()?"现在能说什么":"Supported / allowed"}</div><h2>${isZh()?"当前允许的主张":"What we can currently claim"}</h2>${bullets(paper.claims,"good")}</article><article class="panel"><div class="cpp-section-kicker">${isZh()?"不能偷换什么":"Boundary"}</div><h2>${isZh()?"明确不能写成什么":"What this paper does not claim"}</h2>${bullets(paper.boundaries,"boundary")}</article></section>

      <section class="panel cpp-next" id="next-gate"><div class="cpp-section-kicker">${isZh()?"下一步":"Next gate"}</div><h2>${isZh()?"接下来真正该做什么":"What should happen next"}</h2><p>${E(T(paper.next))}</p></section>
      ${registryBox(paper,reg)}
      ${pager(pageId)}
    </main>`;
  };
})();
