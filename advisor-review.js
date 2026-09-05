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
  const DECISION_KEY = `advisor-meeting-${DATA.meeting?.id||'2026-09-06'}-decision-lock-v1`;
  const loadDecisionLock = () => { try { return JSON.parse(localStorage.getItem(DECISION_KEY)||'{}'); } catch(_) { return {}; } };
  const saveDecisionLock = state => localStorage.setItem(DECISION_KEY, JSON.stringify(state));
  const suggestedPremise = p => String(reality(p).reality_verdict||'').includes('BOUNDARY') ? 'SOUND_IF_BOUNDED' : String(reality(p).reality_verdict||'').startsWith('SUPPORTED') ? 'SOUND' : 'UNRESOLVED_CONCERN';

  function renderNav(){
    const nav=$('.nav'); if(!nav)return;
    const groups=window.NAV_GROUPS||[];
    nav.innerHTML=groups.map(group=>`<details class="nav-group" open><summary class="nav-level1"><span>${esc(group.title?.[lang]||group.title?.en||'')}</span><span class="nav-chevron">⌃</span></summary><div class="nav-children">${(group.pages||[]).map(([href,label])=>`<a class="nav-level2 ${href==='advisor-review.html'?'active':''}" href="${esc(href)}">${esc(label?.[lang]||label?.en||href)}</a>`).join('')}</div></details>`).join('');
  }
  function renderToc(){
    const toc=$('#page-toc'); if(!toc)return;
    toc.innerHTML=`<div class="toc-title">${zh('会议导航','Meeting path')}</div><div class="toc-links"><a href="#portfolio">${zh('九篇总览','Portfolio')}</a><a href="#shared-risks">${zh('共同风险','Shared risks')}</a><a href="#cost-dependencies">${zh('成本与依赖','Cost & dependencies')}</a><a href="#paper-review">Decision Cards</a><a href="#decision-lock">${zh('现场锁结论','Decision Lock')}</a><a href="#schedule">${zh('3 小时议程','Schedule')}</a></div>`;
  }
  function renderHero(){
    const ready=DATA.papers.filter(p=>p.stanford?.status==='READY').length;
    const rs=DATA.route_summary||{};
    const oa=DATA.overlay_audit||{};
    const auditLabel=oa.postfix_status==='FIXES_APPLIED_DETERMINISTIC_PASS' ? zh('Reality/Cost 独立审查 · REVISE→FIXED','Reality/Cost independent audit · REVISE→FIXED') : zh('Reality/Cost 独立审查待闭合','Reality/Cost audit pending closure');
    const freezeLabel=DATA.meeting.freeze_status==='MEETING_CANDIDATE_FROZEN' ? `${zh('会议候选已冻结','Meeting candidate frozen')} · ${(DATA.meeting.candidate_hash||'').slice(0,12)}…` : zh('会议候选尚未冻结','Meeting candidate not frozen');
    return `<section class="advisor-hero"><div><div class="eyebrow">ADVISOR REVIEW · 2026-09-06</div><h1>${zh('九篇论文决策驾驶舱','Nine-paper advisor decision cockpit')}</h1><p>${zh('默认不是淘汰赛：九篇都继续推进，但推进方式不同。师兄现场只处理会改变路线的 premise、paper boundary、shared dependency、next closure 和 override；每篇论文与 Stanford 外审绑定同一个 PDF SHA。','This is not a paper-elimination contest. All nine advance, but through different routes. Senior time is reserved for premise, boundary, shared dependency, next closure, and overrides; advisor and Stanford review the same PDF SHA.')}</p><div class="advisor-hero-meta"><span>main · ${esc((DATA.meeting.main_ref||'').slice(0,12))}…</span><span>${zh('Paper Pack','Paper Pack')} · ${esc(DATA.meeting.status||'')}</span><span>${esc(freezeLabel)}</span><span>${zh('外审 advisory only','External review advisory only')}</span><span>${esc(auditLabel)}</span></div></div><div class="advisor-kpis"><article><b>9/9</b><span>${zh('论文可直接打开','papers directly readable')}</span></article><article><b>${ready}/9</b><span>${zh('Stanford 外审已返回','Stanford reviews ready')}</span></article><article><b>${rs.FREEZE_SUBMIT||0}</b><span>${zh('冻结 / 投稿','freeze / submit')}</span></article><article><b>${rs.EXECUTE_FROZEN||0}</b><span>${zh('按冻结协议执行','execute frozen')}</span></article><article><b>${rs.QUALIFY_FIRST||0}</b><span>${zh('先过资格门','qualify first')}</span></article><article><b>${rs.FORMALIZE_FIRST||0}</b><span>${zh('先形式化 scientific object','formalize first')}</span></article></div></section>`;
  }
  function renderPortfolio(){
    const rows=DATA.papers.map(p=>`<tr><td><div class="advisor-paper-name"><b>${esc(p.paper_id)} · ${esc(p.title)}</b><small>${paperType(p)} · ${p.pages}p · ${esc(p.pdf_sha256.slice(0,10))}…</small><a href="${esc(p.pdf)}" target="_blank" rel="noopener">${zh('打开 PDF ↗','Open PDF ↗')}</a></div></td><td><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><small class="advisor-default-action">${esc(p.default_action)}</small></td><td>${esc(compact(p.best_case,190))}</td><td>${esc(compact(p.next_closure,190))}</td><td><strong class="advisor-cost-class">${esc(p.cost_class)}</strong><small>${esc(compact(p.cost_to_next_decision,150))}</small></td><td><span class="advisor-review-state ${p.stanford?.status==='READY'?'ready':'processing'}">${reviewLabel(p)}</span>${p.stanford?.status==='READY'?`<div class="advisor-score-note">AI ref · ${esc(p.stanford.numerical_score??'–')} · ${esc(p.stanford.textual_signal||'')}</div>`:''}</td><td>${esc(compact(p.advisor_question,170))}</td></tr>`).join('');
    return `<section class="advisor-section" id="portfolio"><header><div><h2>${zh('九篇 Portfolio Decision Matrix','Nine-paper portfolio decision matrix')}</h2><p>${zh('每篇默认动作已经冻结；师兄只需要判断是否触发 override。成本只算到“下一道会改变判断的 gate”，不是把整篇最大实验量一次性承诺。','Each paper has a frozen default route. Senior review only needs to decide whether an override is warranted. Cost is measured to the next decision-changing gate, not the paper’s maximum possible workload.')}</p></div></header><div class="advisor-table-wrap"><table class="matrix advisor-table advisor-decision-table"><thead><tr><th>Paper</th><th>${zh('默认路线','Default route')}</th><th>Best Case</th><th>${zh('下一 closure','Next closure')}</th><th>${zh('到下一判断的成本','Cost to next decision')}</th><th>Stanford</th><th>${zh('师兄主问题','Senior decision')}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderRisks(){
    return `<section class="advisor-section" id="shared-risks"><header><div><h2>${zh('共同失效风险 / 跨论文信息杠杆','Shared invalidation risk / cross-paper leverage')}</h2><p>${zh('这部分优先找“一处判断错误会同时伤到多篇”的共同前提，而不是重复九次独立 reviewer objection。','Look for common premises whose failure would invalidate or duplicate several papers, rather than nine independent comment lists.')}</p></div></header><div class="advisor-risk-grid">${DATA.shared_risks.map(r=>`<article class="advisor-risk-card"><b>${esc(r.label)}</b><span>${esc(r.question)}</span><small>${r.papers.map(esc).join(' · ')}</small></article>`).join('')}</div></section>`;
  }
  function renderCostDependencies(){
    const lanes=(DATA.portfolio_schedule||[]).map(x=>`<article><b>${esc(x.lane)}</b><span>${esc((x.papers||[]).join(' · '))}</span><p>${esc(x.action)}</p></article>`).join('');
    const rows=DATA.papers.map(p=>{const r=resource(p),d=dims(p),op=r.operational_snapshot||{};return `<tr><td><b>${esc(p.paper_id)}</b><br><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span>${op.observed_at?`<small>Live · ${esc(op.observed_at)}</small>`:''}</td><td><p>${esc(d.api_cash||'UNKNOWN')}</p></td><td><p>${esc(d.local_gpu_occupancy||'UNKNOWN')}</p></td><td><p>${esc(d.human_time||'UNKNOWN')}</p></td><td><p>${esc(d.provider_credential_dependency||'UNKNOWN')}</p></td><td><p>${esc(d.calendar_latency||'UNKNOWN')}</p></td><td><p><b>NEXT</b> ${esc(r.next_if_pass||'')}</p><p><b>CONDITIONAL</b> ${esc(r.conditional_envelope||'')}</p></td></tr>`}).join('');
    return `<section class="advisor-section" id="cost-dependencies"><header><div><h2>${zh('资源、成本与并行调度','Resource, cost, and parallel scheduling')}</h2><p>${zh('每篇统一按 API cash → local GPU occupancy → human time → provider/credential dependency → calendar latency 五个维度展示。只有明确 authority 下的资源才算当前承诺；NEXT / CONDITIONAL 都不提前占预算。','Every paper uses the same five resource dimensions: API cash → local GPU occupancy → human time → provider/credential dependency → calendar latency. Only resources under explicit current authority are commitments; NEXT / CONDITIONAL are not pre-booked.')}</p></div></header><div class="advisor-scheduling-grid">${lanes}</div><div class="advisor-table-wrap"><table class="matrix advisor-cost-table"><thead><tr><th>Paper / Route</th><th>API cash</th><th>Local GPU</th><th>Human</th><th>Provider / Credential</th><th>Calendar</th><th>Next / Conditional</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function realitySupport(p){
    const r=reality(p); const cases=r.supporting_cases||[];
    return `<details class="advisor-reality-fold"><summary><span>${zh('Reality Support · 最支持真实场景的案例','Reality Support · strongest real-world cases')}</span><small>${esc(r.reality_verdict||'')}</small></summary><div class="advisor-reality-body"><div class="advisor-reality-cases">${cases.map(c=>`<a href="${esc(c.url)}" target="_blank" rel="noopener"><b>${esc(c.title)}</b><span>${esc(c.why)}</span></a>`).join('')}</div><div class="advisor-reality-boundary"><section><b>${zh('这些案例不能证明','What this does NOT prove')}</b><p>${esc(r.what_this_does_not_prove||'')}</p></section><section><b>${zh('最强工程逃逸 / 反例','Strongest escape / counter-case')}</b><p>${esc(r.strongest_escape||'')}</p></section></div></div></details>`;
  }
  function reviewDigest(p){
    const s=p.stanford||{};
    if(s.status!=='READY') return `<div class="advisor-processing">${zh('Stanford 外审已提交，当前仍在处理。PDF 已冻结；返回后只更新 review overlay，不更换审稿对象。','Stanford review is submitted and still processing. The PDF is frozen; only the review overlay will update.')}</div>`;
    const d=s.advisor_digest||{};
    return `<details class="advisor-review-fold"><summary><span>Stanford · ${esc(s.numerical_score??'–')} · ${esc(s.textual_signal||'')}</span><small>${zh('展开外部攻击证据','Open external review evidence')}</small></summary><div class="advisor-review-digest"><section><b>${zh('外审最强正向','Strongest positive')}</b><p>${esc(compact(d.strongest_positive,640))}</p></section><section><b>${zh('Decision-changing concern','Decision-changing concern')}</b><p>${esc(compact(d.decision_changing_concern,640))}</p></section><section><b>${zh('Reviewer question','Reviewer question')}</b><p>${esc(compact(d.reviewer_question,640))}</p></section></div></details>`;
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
  function receiptObject(){
    const state=loadDecisionLock();
    const decisions=DATA.papers.map(p=>({
      paper_id:p.paper_id,
      default_action:p.default_action,
      premise_verdict:state[p.paper_id]?.premise_verdict||'PENDING',
      route_resolution:state[p.paper_id]?.route_resolution||'PENDING',
      confidence:state[p.paper_id]?.confidence||'PENDING',
      note:state[p.paper_id]?.note||''
    }));
    return {
      schema_version:'1.0',meeting_id:DATA.meeting.id,candidate_hash:DATA.meeting.candidate_hash,
      captured_at:new Date().toISOString(),decisions,
      unresolved:decisions.filter(x=>x.premise_verdict==='PENDING'||x.route_resolution==='PENDING'||x.confidence==='PENDING').map(x=>x.paper_id),
      authority:{scientific:false,experiment:false,submission:false,advisor_judgment_only:true}
    };
  }
  function receiptMarkdown(){
    const r=receiptObject();
    const lines=[`# Advisor Meeting Receipt · ${r.meeting_id}`,'',`Candidate: \`${r.candidate_hash||''}\``,`Captured: ${r.captured_at}`,'', '| Paper | Premise | Route | Confidence | Note |','|---|---|---|---|---|'];
    r.decisions.forEach(x=>lines.push(`| ${x.paper_id} | ${x.premise_verdict} | ${x.route_resolution==='CONFIRM_DEFAULT'?`CONFIRM → ${x.default_action}`:x.route_resolution} | ${x.confidence} | ${(x.note||'').replace(/\|/g,'\\|')} |`));
    lines.push('',`Unresolved: ${r.unresolved.length?r.unresolved.join(', '):'NONE'}`,'','> Advisor judgment / scheduling receipt only. It does not grant scientific, experiment, or submission authority.');
    return lines.join('\n');
  }
  function downloadText(name,text,type='text/plain'){
    const blob=new Blob([text],{type});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);
  }
  function updateDecisionLockSummary(){
    const r=receiptObject();const el=$('#decision-lock-summary');if(el)el.textContent=`${r.decisions.length-r.unresolved.length}/9 ${zh('已锁定','locked')} · ${r.unresolved.length} ${zh('待确认','pending')}`;
  }
  function renderDecisionLock(){
    const state=loadDecisionLock();
    const rows=DATA.papers.map(p=>{const x=state[p.paper_id]||{};return `<tr class="advisor-lock-row" data-lock-paper="${esc(p.paper_id)}"><td><b>${esc(p.paper_id)}</b><small>${esc(routeLabel(p.route))}</small></td><td><small>${zh('建议','Suggested')}: ${esc(suggestedPremise(p))}</small><select data-lock-field="premise_verdict"><option value="PENDING" ${!x.premise_verdict||x.premise_verdict==='PENDING'?'selected':''}>PENDING</option><option value="SOUND" ${x.premise_verdict==='SOUND'?'selected':''}>SOUND</option><option value="SOUND_IF_BOUNDED" ${x.premise_verdict==='SOUND_IF_BOUNDED'?'selected':''}>SOUND_IF_BOUNDED</option><option value="UNRESOLVED_CONCERN" ${x.premise_verdict==='UNRESOLVED_CONCERN'?'selected':''}>UNRESOLVED_CONCERN</option></select></td><td><small>${esc(p.default_action)}</small><select data-lock-field="route_resolution"><option value="PENDING" ${!x.route_resolution||x.route_resolution==='PENDING'?'selected':''}>PENDING</option><option value="CONFIRM_DEFAULT" ${x.route_resolution==='CONFIRM_DEFAULT'?'selected':''}>CONFIRM_DEFAULT</option><option value="OVERRIDE_NARROW" ${x.route_resolution==='OVERRIDE_NARROW'?'selected':''}>OVERRIDE_NARROW</option><option value="OVERRIDE_MERGE" ${x.route_resolution==='OVERRIDE_MERGE'?'selected':''}>OVERRIDE_MERGE</option><option value="OVERRIDE_PIVOT" ${x.route_resolution==='OVERRIDE_PIVOT'?'selected':''}>OVERRIDE_PIVOT</option><option value="OVERRIDE_STOP" ${x.route_resolution==='OVERRIDE_STOP'?'selected':''}>OVERRIDE_STOP</option><option value="OVERRIDE_OTHER" ${x.route_resolution==='OVERRIDE_OTHER'?'selected':''}>OVERRIDE_OTHER</option></select></td><td><select data-lock-field="confidence"><option value="PENDING" ${!x.confidence||x.confidence==='PENDING'?'selected':''}>PENDING</option><option value="HIGH" ${x.confidence==='HIGH'?'selected':''}>HIGH</option><option value="MEDIUM" ${x.confidence==='MEDIUM'?'selected':''}>MEDIUM</option><option value="LOW" ${x.confidence==='LOW'?'selected':''}>LOW</option></select></td><td><input data-lock-field="note" type="text" value="${esc(x.note||'')}" placeholder="${zh('一句话理由 / follow-up','one-line rationale / follow-up')}"></td><td><button class="advisor-quick-confirm" type="button">✓ ${zh('按默认确认','Confirm default')}</button></td></tr>`}).join('');
    return `<section class="advisor-section advisor-decision-lock" id="decision-lock"><header><div><h2>${zh('现场 Decision Lock','Live decision lock')}</h2><p>${zh('只记录师兄判断，不修改 Research OS。每行可以一键按默认路线确认；任何 override 留一句原因即可。数据仅保存在当前浏览器 localStorage，会议结束后导出 receipt。','Captures advisor judgment only; it never changes Research OS. Confirm the default route in one click or record one-line rationale for an override. Data stays in this browser localStorage until exported.')}</p></div><strong id="decision-lock-summary"></strong></header><div class="advisor-lock-actions"><button id="export-advisor-json" type="button">${zh('导出 JSON Receipt','Export JSON receipt')}</button><button id="export-advisor-md" type="button">${zh('导出 Markdown','Export Markdown')}</button><button id="copy-advisor-md" type="button">${zh('复制 Markdown','Copy Markdown')}</button><button id="reset-advisor-lock" class="danger" type="button">${zh('清空现场记录','Reset local record')}</button></div><div class="advisor-table-wrap"><table class="matrix advisor-lock-table"><thead><tr><th>Paper</th><th>Premise</th><th>Route</th><th>Confidence</th><th>Note</th><th>${zh('快速操作','Quick')}</th></tr></thead><tbody>${rows}</tbody></table></div><div class="advisor-note"><strong>${zh('权限边界','Authority boundary')}</strong> · ${zh('导出的 receipt 是 advisor judgment / scheduling 输入。需要 scientific reopen、实验授权或 claim 修改时，仍必须回 Research OS 对应 gate。','The exported receipt is advisor judgment / scheduling input. Scientific reopen, experiment authority, or claim changes still require the corresponding Research OS gates.')}</div></section>`;
  }
  function bindDecisionLock(){
    document.querySelectorAll('[data-lock-paper]').forEach(row=>{
      const pid=row.dataset.lockPaper;
      row.querySelectorAll('[data-lock-field]').forEach(el=>{const event=el.tagName==='INPUT'?'input':'change';el.addEventListener(event,()=>{const state=loadDecisionLock();state[pid]=state[pid]||{};state[pid][el.dataset.lockField]=el.value;saveDecisionLock(state);updateDecisionLockSummary();});});
      row.querySelector('.advisor-quick-confirm')?.addEventListener('click',()=>{const state=loadDecisionLock();state[pid]={...(state[pid]||{}),premise_verdict:suggestedPremise(DATA.papers.find(p=>p.paper_id===pid)),route_resolution:'CONFIRM_DEFAULT',confidence:(state[pid]?.confidence&&state[pid].confidence!=='PENDING')?state[pid].confidence:'MEDIUM',note:state[pid]?.note||''};saveDecisionLock(state);render();});
    });
    $('#export-advisor-json')?.addEventListener('click',()=>downloadText(`advisor-meeting-${DATA.meeting.id}-receipt.json`,JSON.stringify(receiptObject(),null,2),'application/json'));
    $('#export-advisor-md')?.addEventListener('click',()=>downloadText(`advisor-meeting-${DATA.meeting.id}-receipt.md`,receiptMarkdown(),'text/markdown'));
    $('#copy-advisor-md')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(receiptMarkdown());}catch(_){}});
    $('#reset-advisor-lock')?.addEventListener('click',()=>{if(confirm(zh('确认清空当前浏览器里的会议记录？','Reset the meeting record stored in this browser?'))){localStorage.removeItem(DECISION_KEY);render();}});
    updateDecisionLockSummary();
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
    root.innerHTML=`${renderHero()}${renderSchedule()}${renderPortfolio()}${renderRisks()}${renderCostDependencies()}${renderCards()}${renderDecisionLock()}<div class="advisor-note"><strong>${zh('阅读纪律','Reading rule')}</strong> · ${zh('PDF_READY 是完整候选稿；ADVISOR_DRAFT_PRECONFIRMATORY 是为师兄和外审准备的完整可读草稿，但决定性实验仍是 prospective。任何 PDF 后新增 science delta 必须单独看，不能默认已经写进论文。Decision Card 与现场 receipt 都是 advisory projection，不改变 Research OS scientific/experiment authority。','PDF_READY is an integrated candidate. ADVISOR_DRAFT_PRECONFIRMATORY is a complete readable draft whose decisive evidence is still prospective. Post-PDF science deltas remain separate. Decision Cards and the live meeting receipt are advisory projections and cannot change Research OS scientific or experiment authority.')}</div>`;
    const b=$('#advisor-lang'); if(b)b.textContent=lang==='zh'?'EN':'中文';
    bind(); bindDecisionLock(); applyFilter();
  }
  render();
})();
