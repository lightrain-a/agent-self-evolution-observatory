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
  const reviewLabel = p => p.stanford?.status==='READY' ? zh('当前稿外审已返回','Current review ready') : p.stanford?.status==='PRIOR_VERSION' ? zh('上一版外审参考','Prior-version review') : zh('外审处理中','Review processing');
  const routeLabel = route => ({FREEZE_SUBMIT:zh('冻结 / 投稿','Freeze / submit'),EXECUTE_FROZEN:zh('按冻结协议执行','Execute frozen'),QUALIFY_FIRST:zh('先资格化','Qualify first'),FORMALIZE_FIRST:zh('先形式化','Formalize first')})[route] || route;
  const routeClass = route => String(route||'').toLowerCase().replace(/_/g,'-');
  const depText = p => (p.dependencies||[]).join(' · ');
  const resource = p => p.resource_plan || {};
  const reality = p => p.reality_support || {};
  const dims = p => resource(p).resource_dimensions || {};
  const authorizedText = p => {
    const a=resource(p).authorized_now||{};
    return [a.gpu?`GPU ${a.gpu}`:'',a.api_units!==undefined?`API ${a.api_units}`:'',a.cash_cny!==undefined?`cash ${a.cash_cny}`:'',a.work||''].filter(Boolean).join(' · ');
  };

  function renderNav(){
    const nav=$('.nav'); if(!nav)return;
    const groups=window.NAV_GROUPS||[];
    nav.innerHTML=groups.map(group=>`<details class="nav-group" open><summary class="nav-level1"><span>${esc(group.title?.[lang]||group.title?.en||'')}</span><span class="nav-chevron">⌃</span></summary><div class="nav-children">${(group.pages||[]).map(([href,label])=>`<a class="nav-level2 ${href==='advisor-review.html'?'active':''}" href="${esc(href)}">${esc(label?.[lang]||label?.en||href)}</a>`).join('')}</div></details>`).join('');
  }
  function renderToc(){
    const toc=$('#page-toc'); if(!toc)return;
    toc.innerHTML=`<div class="toc-title">${zh('会议导航','Meeting path')}</div><div class="toc-links"><a href="#portfolio">${zh('九篇总览','Portfolio')}</a><a href="#shared-risks">${zh('共同风险 / Ownership','Shared risks / ownership')}</a><a href="#meeting-outputs">${zh('17:00 输出','17:00 outputs')}</a><a href="#spinoffs">${zh('分叉候选','Spinoffs')}</a><a href="#cost-dependencies">${zh('成本与依赖','Cost & dependencies')}</a><a href="#paper-review">Decision Cards</a><a href="#schedule">${zh('3 小时议程','Schedule')}</a></div>`;
  }
  function renderHero(){
    const ready=DATA.papers.filter(p=>p.stanford?.status==='READY').length;
    const prior=DATA.papers.filter(p=>p.stanford?.status==='PRIOR_VERSION').length;
    const rs=DATA.route_summary||{};
    const oa=DATA.overlay_audit||{};
    const auditLabel=(oa.stale_for_papers||[]).length ? `${zh('Reality/Cost 旧审查已部分过期','Reality/Cost prior audit partially stale')} · ${(oa.stale_for_papers||[]).join('/')}` : (oa.postfix_status==='FIXES_APPLIED_DETERMINISTIC_PASS' ? zh('Reality/Cost 独立审查 · REVISE→FIXED','Reality/Cost independent audit · REVISE→FIXED') : zh('Reality/Cost 独立审查待闭合','Reality/Cost audit pending closure'));
    const freezeLabel=DATA.meeting.freeze_status==='MEETING_CANDIDATE_FROZEN' ? `${zh('会议候选已冻结','Meeting candidate frozen')} · ${(DATA.meeting.candidate_hash||'').slice(0,12)}…` : zh('会议候选尚未冻结','Meeting candidate not frozen');
    return `<section class="advisor-hero"><div><div class="eyebrow">ADVISOR REVIEW · 2026-09-06</div><h1>${zh('九篇论文决策驾驶舱','Nine-paper advisor decision cockpit')}</h1><p>${zh('默认不是淘汰赛：九篇都继续推进，但推进方式不同。师兄现场只处理会改变路线的 premise、paper boundary、shared dependency、next closure 和 override；当前稿若已有 Stanford 外审则严格绑定同一 PDF SHA；刚发生实质性改稿的论文只显示明确标注的上一版外审，不混用 SHA。','This is not a paper-elimination contest. All nine advance, but through different routes. Senior time is reserved for premise, boundary, shared dependency, next closure, and overrides; exact current reviews are SHA-bound; materially changed manuscripts show prior-version reviews explicitly rather than reusing them as current evidence.')}</p><div class="advisor-hero-meta"><span>main · ${esc((DATA.meeting.main_ref||'').slice(0,12))}…</span><span>${zh('Paper Pack','Paper Pack')} · ${esc(DATA.meeting.status||'')}</span><span>${esc(freezeLabel)}</span><span>${zh('外审 advisory only','External review advisory only')}</span><span>${esc(auditLabel)}</span></div></div><div class="advisor-kpis"><article><b>9/9</b><span>${zh('论文可直接打开','papers directly readable')}</span></article><article><b>${ready}/9</b><span>${zh('当前 SHA 外审已返回','exact-current reviews')}</span></article><article><b>${prior}</b><span>${zh('上一版外审参考','prior-version review')}</span></article><article><b>${rs.FREEZE_SUBMIT||0}</b><span>${zh('冻结 / 投稿','freeze / submit')}</span></article><article><b>${rs.EXECUTE_FROZEN||0}</b><span>${zh('按冻结协议执行','execute frozen')}</span></article><article><b>${rs.QUALIFY_FIRST||0}</b><span>${zh('先过资格门','qualify first')}</span></article><article><b>${rs.FORMALIZE_FIRST||0}</b><span>${zh('先形式化 scientific object','formalize first')}</span></article></div></section>`;
  }
  function renderPortfolio(){
    const rows=DATA.papers.map(p=>`<tr><td><div class="advisor-paper-name"><b>${esc(p.paper_id)} · ${esc(p.title)}</b><small>${paperType(p)} · ${p.pages}p · ${esc(p.pdf_sha256.slice(0,10))}…</small><a href="${esc(p.pdf)}" target="_blank" rel="noopener">${zh('打开 PDF ↗','Open PDF ↗')}</a></div></td><td><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><small class="advisor-default-action">${esc(p.default_action)}</small></td><td>${esc(compact(p.best_case,190))}</td><td>${esc(compact(p.next_closure,190))}</td><td><strong class="advisor-cost-class">${esc(p.cost_class)}</strong><small>${esc(compact(p.cost_to_next_decision,150))}</small></td><td><span class="advisor-review-state ${p.stanford?.status==='READY'?'ready':p.stanford?.status==='PRIOR_VERSION'?'prior':'processing'}">${reviewLabel(p)}</span>${['READY','PRIOR_VERSION'].includes(p.stanford?.status)?`<div class="advisor-score-note">${p.stanford.status==='PRIOR_VERSION'?'Prior AI ref':'AI ref'} · ${esc(p.stanford.numerical_score??'–')} · ${esc(p.stanford.textual_signal||'')}</div>`:''}</td><td>${esc(compact(p.advisor_question,170))}</td></tr>`).join('');
    return `<section class="advisor-section" id="portfolio"><header><div><h2>${zh('九篇 Portfolio Decision Matrix','Nine-paper portfolio decision matrix')}</h2><p>${zh('每篇默认动作已经冻结；师兄只需要判断是否触发 override。成本只算到“下一道会改变判断的 gate”，不是把整篇最大实验量一次性承诺。','Each paper has a frozen default route. Senior review only needs to decide whether an override is warranted. Cost is measured to the next decision-changing gate, not the paper’s maximum possible workload.')}</p></div></header><div class="advisor-table-wrap"><table class="matrix advisor-table advisor-decision-table"><thead><tr><th>Paper</th><th>${zh('默认路线','Default route')}</th><th>Best Case</th><th>${zh('下一 closure','Next closure')}</th><th>${zh('到下一判断的成本','Cost to next decision')}</th><th>Stanford</th><th>${zh('师兄主问题','Senior decision')}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderRisks(){
    const own=DATA.claim_ownership_map||{};
    const primary=['B1','PAPER_A','PAPER_B','C1','E2','G1'].map(pid=>{const x=own[pid]||{};return `<article><b>${esc(pid)}</b><strong>${esc(x.primary_claim_owner||'')}</strong><p>${esc(x.relationship||'')}</p></article>`}).join('');
    const reopen=(DATA.shared_risk_reopen_rules||[]).map(r=>`<tr><td><b>${esc(r.premise)}</b></td><td>${esc((r.directly_affected||[]).join(' · '))}</td><td>${esc((r.conditionally_affected||[]).join(' · ')||'—')}</td><td>${esc(r.reopen_threshold||'')}</td></tr>`).join('');
    return `<section class="advisor-section" id="shared-risks"><header><div><h2>${zh('共同失效风险 / Claim Ownership / Reopen Rule','Shared invalidation risk / claim ownership / reopen rule')}</h2><p>${zh('先批准每篇主 claim owner，再冻结 shared premise 失败时到底重开谁；不要因为都讲 memory / measurement 就整簇重开。','Approve the primary claim owner first, then freeze exactly which papers reopen if a shared premise fails; shared vocabulary alone must not trigger a family-wide reopen.')}</p></div></header><div class="advisor-ownership-grid">${primary}</div><div class="advisor-note"><strong>${zh('Memory family architecture owner','Memory family architecture owner')}</strong> · ${esc(own.memory_family_architecture_decision_owner||'—')} · ${esc(own.memory_family_architecture_rule||'')}<br><strong>${zh('默认边界','Default boundary')}</strong> · ${esc(own.boundary_note||'')}</div><div class="advisor-risk-grid">${DATA.shared_risks.map(r=>`<article class="advisor-risk-card"><b>${esc(r.label)}</b><span>${esc(r.question)}</span><small>${r.papers.map(esc).join(' · ')}</small><p>${esc(r.reopen_rule||'')}</p></article>`).join('')}</div><div class="advisor-table-wrap"><table class="matrix advisor-reopen-table"><thead><tr><th>Shared premise</th><th>Direct</th><th>Conditional</th><th>Reopen threshold</th></tr></thead><tbody>${reopen}</tbody></table></div></section>`;
  }
  function renderMeetingOutputs(){
    const rows=(DATA.meeting_outputs||[]).map((x,i)=>`<article><span>${String(i+1).padStart(2,'0')}</span><p>${esc(x)}</p></article>`).join('');
    return `<section class="advisor-section" id="meeting-outputs"><header><div><h2>${zh('17:00 前必须锁定的 5 个输出','Five outputs that must be locked by 17:00')}</h2><p>${zh('会议成功标准不是“九篇都聊过”，而是这五个 receipt-level 输出都有明确结论、owner 与 follow-up。','The meeting succeeds only when these five receipt-level outputs have a concrete decision, owner, and follow-up—not merely because all nine papers were discussed.')}</p></div></header><div class="advisor-output-grid">${rows}</div></section>`;
  }
  function renderCostDependencies(){
    const lanes=(DATA.portfolio_schedule||[]).map(x=>`<article><b>${esc(x.lane)}</b><span>${esc((x.papers||[]).join(' · '))}</span><p>${esc(x.action)}</p></article>`).join('');
    const rows=DATA.papers.map(p=>{const r=resource(p),d=dims(p),op=r.operational_snapshot||{};const condLabel=r.conditional_envelope_label||'FUTURE CONDITIONAL — not current commitment';return `<tr><td><b>${esc(p.paper_id)}</b><br><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span>${op.observed_at?`<small>Operational snapshot · ${esc(op.observed_at)}</small>`:''}</td><td><p><b>CURRENT</b> ${esc(r.current_decision_cost||authorizedText(p))}</p><p>${esc(d.api_cash||'UNKNOWN')} · ${esc(d.local_gpu_occupancy||'UNKNOWN')}</p></td><td><p>${esc(d.post_meeting_execution_human_hours||'UNKNOWN')}</p></td><td><p>${esc(d.provider_credential_dependency||'UNKNOWN')}</p></td><td><p>${esc(d.calendar_latency||'UNKNOWN')}</p></td><td><p><b>STOP</b> ${esc(r.cost_to_stop||'')}</p></td><td><p><b>NEXT IF PASS</b> ${esc(r.next_if_pass||'')}</p><p><b>NEXT AUTHORITY</b> ${esc(r.next_authority_gate||'')}</p><p class="advisor-conditional-envelope"><b>${esc(condLabel)}</b> ${esc(r.conditional_envelope||'')}</p><p class="advisor-non-authority"><b>NON-AUTHORITY</b> ${esc(r.explicit_non_authority||'')}</p></td></tr>`}).join('');
    return `<section class="advisor-section" id="cost-dependencies"><header><div><h2>${zh('跨论文资源冲突检查','Cross-paper resource conflict check')}</h2><p>${zh('这里只检查会改变调度的稀缺资源冲突。Human 列是会后执行工时，不是 14:00–17:00 的会议分钟；CURRENT、STOP 与 FUTURE CONDITIONAL 分开显示。','Only scarce-resource conflicts that change scheduling belong here. Human hours are post-meeting execution effort, not advisor-meeting minutes; CURRENT, STOP, and FUTURE CONDITIONAL are shown separately.')}</p></div></header><div class="advisor-scheduling-grid">${lanes}</div><div class="advisor-table-wrap"><table class="matrix advisor-cost-table"><thead><tr><th>Paper / Route</th><th>Current authorized cost</th><th>Post-meeting human-hours</th><th>Provider / Credential</th><th>Calendar</th><th>Cost-to-Stop</th><th>Next / Future conditional</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function realitySupport(p){
    const r=reality(p); const cases=r.supporting_cases||[];
    return `<details class="advisor-reality-fold"><summary><span>${zh('Reality Support · 最支持真实场景的案例','Reality Support · strongest real-world cases')}</span><small>${esc(r.reality_verdict||'')}</small></summary><div class="advisor-reality-body"><div class="advisor-reality-cases">${cases.map(c=>`<a href="${esc(c.url)}" target="_blank" rel="noopener"><b>${esc(c.title)}</b><span>${esc(c.why)}</span></a>`).join('')}</div><div class="advisor-reality-boundary"><section><b>${zh('这些案例不能证明','What this does NOT prove')}</b><p>${esc(r.what_this_does_not_prove||'')}</p></section><section><b>${zh('最强工程逃逸 / 反例','Strongest escape / counter-case')}</b><p>${esc(r.strongest_escape||'')}</p></section></div></div></details>`;
  }
  function reviewDigest(p){
    const s=p.stanford||{};
    if(!['READY','PRIOR_VERSION'].includes(s.status)) return `<div class="advisor-processing">${zh('Stanford 外审已提交，当前仍在处理。PDF 已冻结；返回后只更新 review overlay，不更换审稿对象。','Stanford review is submitted and still processing. The PDF is frozen; only the review overlay will update.')}</div>`;
    const d=s.advisor_digest||{};
    const prior=s.status==='PRIOR_VERSION';
    return `<details class="advisor-review-fold ${prior?'advisor-review-prior':''}"><summary><span>${prior?'Stanford PRIOR':'Stanford'} · ${esc(s.numerical_score??'–')} · ${esc(s.textual_signal||'')}</span><small>${prior?zh('上一版 PDF，仅作历史参考','Prior PDF, historical guidance only'):zh('展开外部攻击证据','Open external review evidence')}</small></summary>${prior?`<div class="advisor-prior-review">${zh('这份外审对应紧邻上一版 PDF SHA，不是当前 meeting candidate；当前稿已发生 story framing 变化。','This review is bound to the immediately preceding PDF SHA, not the current meeting candidate; the current manuscript has materially changed framing.')}</div>`:''}<div class="advisor-review-digest"><section><b>${zh('外审最强正向','Strongest positive')}</b><p>${esc(compact(d.strongest_positive,640))}</p></section><section><b>${zh('Decision-changing concern','Decision-changing concern')}</b><p>${esc(compact(d.decision_changing_concern,640))}</p></section><section><b>${zh('Reviewer question','Reviewer question')}</b><p>${esc(compact(d.reviewer_question,640))}</p></section></div></details>`;
  }
  function cardMatches(p,q){
    if(filter==='preconfirm' && p.paper_status!=='ADVISOR_DRAFT_PRECONFIRMATORY') return false;
    if(filter==='review-ready' && p.stanford?.status!=='READY') return false;
    if(filter==='attention' && !['CRITICAL','MIXED_POSITIVE'].includes(p.stanford?.textual_signal)) return false;
    if(!q)return true;
    const d=p.stanford?.advisor_digest||{};
    const rr=reality(p);const rp=resource(p);const realityText=(rr.supporting_cases||[]).map(x=>`${x.title} ${x.why}`).join(' ');
    return [p.paper_id,p.title,p.route,p.best_case,p.story,p.premise,p.risk,p.strongest_simplification,p.evidence_state,p.next_closure,p.cost_class,p.cost_to_next_decision,depText(p),p.default_action,p.override_trigger,p.cross_paper_leverage,p.science_delta,p.advisor_question,realityText,rr.what_this_does_not_prove,rr.strongest_escape,authorizedText(p),rp.next_if_pass,rp.conditional_envelope,d.strongest_positive,d.decision_changing_concern,d.reviewer_question].join(' ').toLowerCase().includes(q);
  }
  function renderCards(){
    const cards=DATA.papers.map(p=>`<article class="advisor-card" id="paper-${esc(p.paper_id.toLowerCase())}" data-paper="${esc(p.paper_id)}"><header><span class="advisor-card-code">${esc(p.paper_id)}</span><div><h3>${esc(p.title)}</h3><small>${paperType(p)} · ${p.pages}p · SHA ${esc(p.pdf_sha256.slice(0,12))}…</small></div><div class="advisor-card-actions"><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><a href="${esc(p.pdf)}" target="_blank" rel="noopener">PDF ↗</a></div></header><div class="advisor-card-body"><section class="advisor-best-case"><b>Best Case</b><p>${esc(p.best_case)}</p></section>${realitySupport(p)}<div class="advisor-decision-grid"><section><b>ONE-SENTENCE STORY</b><p>${esc(p.story)}</p></section><section><b>PREMISE TO CONFIRM</b><p>${esc(p.premise)}</p></section><section class="advisor-risk-box"><b>DECISION-CHANGING RISK</b><p>${esc(p.risk)}</p></section><section><b>STRONGEST SIMPLIFICATION / BASELINE</b><p>${esc(p.strongest_simplification)}</p></section></div><section class="advisor-evidence-state"><b>EVIDENCE STATE</b><p>${esc(p.evidence_state)}</p></section><div class="advisor-closure-grid"><section><b>NEXT CLOSURE</b><p>${esc(p.next_closure)}</p></section><section><b>AUTHORIZED NOW</b><strong>${esc(authorizedText(p))}</strong><p>${esc(resource(p).priority_note||'')}</p></section><section><b>DEPENDENCIES</b><p>${esc(depText(p))}</p></section></div><div class="advisor-action-grid"><section><b>DEFAULT ACTION</b><strong>${esc(p.default_action)}</strong></section><section><b>OVERRIDE TRIGGER</b><p>${esc(p.override_trigger)}</p></section></div><section class="advisor-cross-paper"><b>CROSS-PAPER LEVERAGE</b><p>${esc(p.cross_paper_leverage)}</p></section><section class="advisor-question"><b>${zh('师兄只需拍板','Senior decision')}</b><p>${esc(p.advisor_question)}</p></section>${reviewDigest(p)}<section class="advisor-delta-box"><b>Science delta after PDF</b><p>${esc(p.science_delta)}</p></section></div><details class="advisor-version-fold"><summary>${zh('版本与权限信息','Version / authority detail')}</summary><div><b>Paper candidate</b>: ${esc(p.paper_candidate_ref)}<br><b>Scientific canonical</b>: ${esc(p.scientific_canonical_ref)}<br><b>PDF SHA256</b>: ${esc(p.pdf_sha256)}<br>${zh('Stanford 外审仅是 advisory overlay；不授予 scientific / experiment / submission authority。','Stanford review is advisory only and grants no scientific, experiment, or submission authority.')}</div></details></article>`).join('');
    return `<section class="advisor-section" id="paper-review"><header><div><h2>${zh('九篇 Decision Cards','Nine decision cards')}</h2><p>${zh('默认先看综合判断：story、premise、route-changing risk、strongest simplification、next closure 和 override。Stanford 外审被折叠为 secondary evidence，避免 AI review 反客为主。','Read the synthesized decision object first: story, premise, route-changing risk, strongest simplification, next closure, and override. Stanford is collapsed as secondary evidence so the AI review cannot dominate the meeting.')}</p></div><div class="advisor-filter-row"><button class="advisor-filter active" data-filter="all">${zh('全部','All')}</button><button class="advisor-filter" data-filter="review-ready">Stanford Ready</button><button class="advisor-filter" data-filter="attention">${zh('外审需关注','Review attention')}</button><button class="advisor-filter" data-filter="preconfirm">Preconfirm</button></div></header><div class="advisor-cards">${cards}</div></section>`;
  }
  function renderSpinoffs(){
    if(!(DATA.spinoffs||[]).length) return '';
    return `<section class="advisor-section" id="spinoffs"><header><div><h2>${zh('独立分叉候选','Separate spinoff candidates')}</h2><p>${zh('这些对象不计入当前九篇主 Portfolio，也不能画进原论文的版本分数折线。','These objects are outside the nine-paper main portfolio and must not be plotted as later revisions of their parent paper.')}</p></div></header><div class="advisor-risk-grid">${DATA.spinoffs.map(x=>`<article class="advisor-risk-card"><b>${esc(x.paper_id)} · ${esc(x.title)}</b><span>${esc(x.relation)} ${zh('当前状态','Status')}: ${esc(x.status)}.</span><small>Stanford AI ref · ${esc(x.stanford?.numerical_score??'–')} · ${esc(x.stanford?.textual_signal||'')}</small></article>`).join('')}</div></section>`;
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
    root.innerHTML=`${renderHero()}${renderSchedule()}${renderPortfolio()}${renderRisks()}${renderMeetingOutputs()}${renderSpinoffs()}${renderCostDependencies()}${renderCards()}<div class="advisor-note"><strong>${zh('阅读纪律','Reading rule')}</strong> · ${zh('PDF_READY 是完整候选稿；ADVISOR_DRAFT_PRECONFIRMATORY 是为师兄和外审准备的完整可读草稿，但决定性实验仍是 prospective。任何 PDF 后新增 science delta 必须单独看，不能默认已经写进论文。Decision Card 是 advisory projection，不改变 Research OS scientific/experiment authority。','PDF_READY is an integrated candidate. ADVISOR_DRAFT_PRECONFIRMATORY is a complete readable draft whose decisive evidence is still prospective. Post-PDF science deltas remain separate. Decision Cards are advisory projections and cannot change Research OS scientific or experiment authority.')}</div>`;
    const b=$('#advisor-lang'); if(b)b.textContent=lang==='zh'?'EN':'中文';
    bind(); applyFilter();
  }
  render();
})();
