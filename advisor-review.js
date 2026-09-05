(() => {
  const DATA = window.ADVISOR_MEETING_DATA || {papers:[],shared_risks:[],schedule:[],meeting:{}};
  const LANG_KEY = 'agent-evolution-language';
  let lang = localStorage.getItem(LANG_KEY) || 'zh';
  let filter = 'all';
  const $ = (s) => document.querySelector(s);
  const esc = (v='') => String(v).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const compact = (v='', n=270) => { const s=String(v||'').replace(/\s+/g,' ').trim(); return s.length>n?s.slice(0,n-1)+'…':s; };
  const zh = (a,b) => lang==='zh'?a:b;
  const signalClass = (s='') => String(s).toLowerCase().replace(/_/g,'-');
  const paperType = p => p.paper_status==='ADVISOR_DRAFT_PRECONFIRMATORY' ? zh('预确证草稿','Preconfirmatory draft') : zh('完整候选稿','Integrated candidate');
  const reviewLabel = p => (p.stanford?.status==='READY') ? zh('外审已返回','Review ready') : zh('外审处理中','Review processing');

  function renderNav(){
    const nav=$('.nav'); if(!nav)return;
    const groups=window.NAV_GROUPS||[];
    nav.innerHTML=groups.map(group=>`<details class="nav-group" open><summary class="nav-level1"><span>${esc(group.title?.[lang]||group.title?.en||'')}</span><span class="nav-chevron">⌃</span></summary><div class="nav-children">${(group.pages||[]).map(([href,label])=>`<a class="nav-level2 ${href==='advisor-review.html'?'active':''}" href="${esc(href)}">${esc(label?.[lang]||label?.en||href)}</a>`).join('')}</div></details>`).join('');
  }
  function renderToc(){
    const toc=$('#page-toc'); if(!toc)return;
    toc.innerHTML=`<div class="toc-title">${zh('会议导航','Meeting path')}</div><div class="toc-links"><a href="#portfolio">${zh('九篇总览','Portfolio')}</a><a href="#shared-risks">${zh('共同风险','Shared risks')}</a><a href="#paper-review">${zh('论文与外审','Papers & reviews')}</a><a href="#schedule">${zh('3 小时议程','Schedule')}</a></div>`;
  }
  function renderHero(){
    const ready=DATA.papers.filter(p=>p.stanford?.status==='READY').length;
    const pre=DATA.papers.filter(p=>p.paper_status==='ADVISOR_DRAFT_PRECONFIRMATORY').length;
    return `<section class="advisor-hero"><div><div class="eyebrow">ADVISOR REVIEW · 2026-09-06</div><h1>${zh('九篇论文决策驾驶舱','Nine-paper advisor decision cockpit')}</h1><p>${zh('默认不是淘汰赛：九篇都继续推进。师兄现场只处理会改变路线的 premise、paper boundary、shared dependency、next closure 和 scheduling exception。每篇论文与 Stanford 外审绑定同一个 PDF SHA。','This is not a paper-elimination contest. All nine advance by default; senior time is reserved for premise, boundary, shared-dependency, next-closure, and scheduling exceptions. Advisor and Stanford review the same PDF SHA.')}</p><div class="advisor-hero-meta"><span>main · ${esc((DATA.meeting.main_ref||'').slice(0,12))}…</span><span>${zh('Paper Pack','Paper Pack')} · ${esc(DATA.meeting.status||'')}</span><span>${zh('外审 advisory only','External review advisory only')}</span></div></div><div class="advisor-kpis"><article><b>9/9</b><span>${zh('论文可直接打开','papers directly readable')}</span></article><article><b>${ready}/9</b><span>${zh('Stanford 外审已返回','Stanford reviews ready')}</span></article><article><b>${9-pre}</b><span>${zh('完整候选稿','integrated candidates')}</span></article><article><b>${pre}</b><span>${zh('预确证 Advisor Draft','preconfirmatory advisor drafts')}</span></article></div></section>`;
  }
  function renderPortfolio(){
    const rows=DATA.papers.map(p=>`<tr><td><div class="advisor-paper-name"><b>${esc(p.paper_id)} · ${esc(p.title)}</b><small>${paperType(p)} · ${p.pages}p · ${esc(p.pdf_sha256.slice(0,10))}…</small><a href="${esc(p.pdf)}" target="_blank" rel="noopener">${zh('打开 PDF ↗','Open PDF ↗')}</a></div></td><td><span class="advisor-type ${p.paper_status==='ADVISOR_DRAFT_PRECONFIRMATORY'?'preconfirm':'ready'}">${paperType(p)}</span></td><td>${esc(compact(p.best_case,220))}</td><td class="advisor-delta">${esc(compact(p.science_delta,170))}</td><td><span class="advisor-review-state ${p.stanford?.status==='READY'?'ready':'processing'}">${reviewLabel(p)}</span>${p.stanford?.status==='READY'?`<div class="advisor-score-note">AI ref · ${esc(p.stanford.numerical_score??'–')} · ${esc(p.stanford.textual_signal||'')}</div>`:''}</td><td>${esc(compact(p.advisor_question,180))}</td></tr>`).join('');
    return `<section class="advisor-section" id="portfolio"><header><div><h2>${zh('九篇 Portfolio Dashboard','Nine-paper portfolio dashboard')}</h2><p>${zh('先看为什么值得继续、当前稿件边界和师兄需要拍板的问题；外审分数只作为弱参考，不作为 scientific authority。','Start with the continuation case, manuscript boundary, and senior decision. Scores are weak reference signals, never scientific authority.')}</p></div></header><div class="advisor-table-wrap"><table class="matrix advisor-table"><thead><tr><th>Paper</th><th>${zh('稿件','Draft')}</th><th>Best Case</th><th>Science delta after PDF</th><th>Stanford</th><th>${zh('师兄主问题','Senior decision')}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderRisks(){
    return `<section class="advisor-section" id="shared-risks"><header><div><h2>${zh('共同失效风险 / 跨论文信息杠杆','Shared invalidation risk / cross-paper leverage')}</h2><p>${zh('这部分优先找“一处判断错误会同时伤到多篇”的共同前提，而不是重复九次独立 reviewer objection。','Look for common premises whose failure would invalidate or duplicate several papers, rather than nine independent comment lists.')}</p></div></header><div class="advisor-risk-grid">${DATA.shared_risks.map(r=>`<article class="advisor-risk-card"><b>${esc(r.label)}</b><span>${esc(r.question)}</span><small>${r.papers.map(esc).join(' · ')}</small></article>`).join('')}</div></section>`;
  }
  function reviewDigest(p){
    const s=p.stanford||{};
    if(s.status!=='READY') return `<div class="advisor-processing">${zh('Stanford 外审已提交，当前仍在处理。PDF 已冻结；返回后只更新 review overlay，不更换审稿对象。','Stanford review is submitted and still processing. The PDF is frozen; only the review overlay will update.')}</div>`;
    const d=s.advisor_digest||{};
    return `<div class="advisor-review-digest"><section><b>${zh('外审最强正向','Strongest positive')}</b><p>${esc(compact(d.strongest_positive,640))}</p></section><section><b>${zh('Decision-changing concern','Decision-changing concern')}</b><p>${esc(compact(d.decision_changing_concern,640))}</p></section><section><b>${zh('Reviewer question','Reviewer question')}</b><p>${esc(compact(d.reviewer_question,640))}</p></section></div>`;
  }
  function cardMatches(p,q){
    if(filter==='preconfirm' && p.paper_status!=='ADVISOR_DRAFT_PRECONFIRMATORY') return false;
    if(filter==='review-ready' && p.stanford?.status!=='READY') return false;
    if(filter==='attention' && !['CRITICAL','MIXED_POSITIVE'].includes(p.stanford?.textual_signal)) return false;
    if(!q)return true;
    const d=p.stanford?.advisor_digest||{};
    return [p.paper_id,p.title,p.best_case,p.science_delta,p.advisor_question,d.strongest_positive,d.decision_changing_concern,d.reviewer_question].join(' ').toLowerCase().includes(q);
  }
  function renderCards(){
    const cards=DATA.papers.map(p=>`<article class="advisor-card" id="paper-${esc(p.paper_id.toLowerCase())}" data-paper="${esc(p.paper_id)}"><header><span class="advisor-card-code">${esc(p.paper_id)}</span><div><h3>${esc(p.title)}</h3><small>${paperType(p)} · ${p.pages}p · SHA ${esc(p.pdf_sha256.slice(0,12))}… ${p.stanford?.status==='READY'?`· Stanford ${esc(p.stanford.numerical_score??'–')}`:''}</small></div><div class="advisor-card-actions"><a href="${esc(p.pdf)}" target="_blank" rel="noopener">PDF ↗</a>${p.stanford?.status==='READY'?`<span class="advisor-signal ${signalClass(p.stanford.textual_signal)}">${esc(p.stanford.textual_signal)}</span>`:''}</div></header><div class="advisor-card-body"><section class="advisor-best-case"><b>Best Case</b><p>${esc(p.best_case)}</p></section><section class="advisor-question"><b>${zh('师兄只需拍板','Senior decision')}</b><p>${esc(p.advisor_question)}</p></section>${reviewDigest(p)}<section class="advisor-delta-box"><b>Science delta after PDF</b><p>${esc(p.science_delta)}</p></section></div><details><summary>${zh('版本与权限信息','Version / authority detail')}</summary><div><b>Paper candidate</b>: ${esc(p.paper_candidate_ref)}<br><b>Scientific canonical</b>: ${esc(p.scientific_canonical_ref)}<br><b>PDF SHA256</b>: ${esc(p.pdf_sha256)}<br>${zh('Stanford 外审仅是 advisory overlay；不授予 scientific / experiment / submission authority。','Stanford review is advisory only and grants no scientific, experiment, or submission authority.')}</div></details></article>`).join('');
    return `<section class="advisor-section" id="paper-review"><header><div><h2>${zh('论文与 Stanford 外审','Papers and Stanford external review')}</h2><p>${zh('师兄可以直接打开九篇固定 PDF。默认显示外审最强正向、一个会改变路线的 concern、一个 reviewer question；全文只在需要时另开。','Open any frozen PDF directly. The default overlay shows one positive case, one decision-changing concern, and one reviewer question.')}</p></div><div class="advisor-filter-row"><button class="advisor-filter active" data-filter="all">${zh('全部','All')}</button><button class="advisor-filter" data-filter="review-ready">Stanford Ready</button><button class="advisor-filter" data-filter="attention">${zh('外审需关注','Review attention')}</button><button class="advisor-filter" data-filter="preconfirm">Preconfirm</button></div></header><div class="advisor-cards">${cards}</div></section>`;
  }
  function renderSchedule(){
    return `<section class="advisor-section" id="schedule"><header><div><h2>${zh('14:00–17:00 最终议程','Final 14:00–17:00 route')}</h2><p>${zh('前半段解决 abstraction/boundary，后半段只做 exception-based closure 与资源调度。','Resolve abstraction and boundaries first; the second half only locks exceptions, closures, and scheduling.')}</p></div></header><div class="advisor-schedule">${DATA.schedule.map(x=>`<article><b>${esc(x.start)}–${esc(x.end)}</b><span>${esc(x.label)}</span></article>`).join('')}</div></section>`;
  }
  function applyFilter(){
    const q=($('#advisor-search')?.value||'').toLowerCase().trim(); let n=0;
    DATA.papers.forEach(p=>{const el=document.querySelector(`[data-paper="${CSS.escape(p.paper_id)}"]`); if(!el)return; const show=cardMatches(p,q); el.classList.toggle('hidden',!show); if(show)n++;});
    const c=$('#result-count'); if(c)c.textContent=`${n}/9 ${zh('篇','papers')}`;
  }
  function bind(){
    const search=$('#advisor-search'); if(search) search.oninput=applyFilter;
    document.querySelectorAll('.advisor-filter').forEach(btn=>{btn.onclick=()=>{filter=btn.dataset.filter;document.querySelectorAll('.advisor-filter').forEach(x=>x.classList.toggle('active',x===btn));applyFilter();};});
    const langBtn=$('#advisor-lang'); if(langBtn) langBtn.onclick=()=>{lang=lang==='zh'?'en':'zh';localStorage.setItem(LANG_KEY,lang);document.documentElement.lang=lang==='zh'?'zh-CN':'en';render();};
    const sidebar=$('.sidebar');
    if(sidebar && !sidebar.querySelector('.sidebar-close')) sidebar.insertAdjacentHTML('afterbegin','<button class="sidebar-close" aria-label="Close navigation">×</button>');
    let overlay=$('.sidebar-overlay');
    if(!overlay){document.body.insertAdjacentHTML('afterbegin','<button class="sidebar-overlay" aria-label="Close navigation" hidden></button>');overlay=$('.sidebar-overlay');}
    const close=()=>{sidebar?.classList.remove('open'); if(overlay) overlay.hidden=true;};
    const mobile=$('.mobile-toggle'); if(mobile) mobile.onclick=()=>{sidebar?.classList.add('open'); if(overlay) overlay.hidden=false;};
    const closeBtn=sidebar?.querySelector('.sidebar-close'); if(closeBtn) closeBtn.onclick=close;
    if(overlay) overlay.onclick=close;
  }
  function render(){
    document.documentElement.lang=lang==='zh'?'zh-CN':'en';
    renderNav(); renderToc();
    const root=$('#advisor-page');
    root.innerHTML=`${renderHero()}${renderSchedule()}${renderPortfolio()}${renderRisks()}${renderCards()}<div class="advisor-note"><strong>${zh('阅读纪律','Reading rule')}</strong> · ${zh('PDF_READY 是完整候选稿；ADVISOR_DRAFT_PRECONFIRMATORY 是为师兄和外审准备的完整可读草稿，但决定性实验仍是 prospective。任何 PDF 后新增 science delta 必须单独看，不能默认已经写进论文。','PDF_READY is an integrated candidate. ADVISOR_DRAFT_PRECONFIRMATORY is a complete readable draft whose decisive evidence is still prospective. Post-PDF science deltas are separate and must not be assumed to be integrated into manuscript claims.')}</div>`;
    const b=$('#advisor-lang'); if(b)b.textContent=lang==='zh'?'EN':'中文';
    bind(); applyFilter();
  }
  render();
})();
