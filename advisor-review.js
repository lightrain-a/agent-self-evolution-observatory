(() => {
  const DATA = window.ADVISOR_MEETING_DATA || {papers:[],shared_risks:[],schedule:[],meeting:{}};
  const LANG_KEY = 'agent-evolution-language';
  let lang = localStorage.getItem(LANG_KEY) || 'zh';
  let filter = 'all';
  const MEETING_ORDER = ['E1','B1','C1','E2','PAPER_A','PAPER_B','G1','CONSTRAINT_EXTERNALITY','3D'];
  const CIRCLED = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨'];
  const DECISION_KEY = 'advisor-meeting-20260906-live-decisions-v1';
  const loadDecisions = () => { try { return JSON.parse(localStorage.getItem(DECISION_KEY) || '{}') || {}; } catch (_) { return {}; } };
  let decisions = loadDecisions();
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
  const meetingIndex = p => { const i=MEETING_ORDER.indexOf(p.paper_id); return i<0?99:i; };
  const orderedPapers = () => [...DATA.papers].sort((a,b)=>meetingIndex(a)-meetingIndex(b));
  const paperSeq = p => CIRCLED[meetingIndex(p)] || '•';
  const paperAnchor = p => `paper-${String(p.paper_id||'').toLowerCase()}`;
  const shortPaperName = p => ({PAPER_A:'Paper A',PAPER_B:'Paper B',CONSTRAINT_EXTERNALITY:zh('Constraint Externality','Constraint Externality')})[p.paper_id] || p.paper_id;
  const decisionLabel = status => ({KEEP:zh('KEEP · 保持当前路线','KEEP · current route'),MODIFY:zh('MODIFY · 修改路线','MODIFY · change route'),FOLLOW_UP:zh('FOLLOW-UP · 会后补决策','FOLLOW-UP · post-meeting decision')})[status] || zh('待现场拍板','Pending');
  const saveDecisions = () => localStorage.setItem(DECISION_KEY, JSON.stringify(decisions));
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
    const paperLinks=orderedPapers().map(p=>`<a href="#${esc(paperAnchor(p))}">${paperSeq(p)} ${esc(shortPaperName(p))}</a>`).join('');
    toc.innerHTML=`<div class="toc-title">${zh('会议导航 · 14:00–17:00','Meeting path · 14:00–17:00')}</div><div class="toc-links"><a href="#meeting-path">${zh('3 小时单一路线','3-hour single route')}</a><a href="#portfolio">${zh('九篇总览','Portfolio')}</a>${paperLinks}<a href="#shared-risks">${zh('跨论文 Exceptions / Ownership','Cross-paper exceptions / ownership')}</a><a href="#cost-dependencies">${zh('资源与 Authority','Resources & authority')}</a><a href="#decision-ledger">${zh('锁 Decision Ledger','Lock decision ledger')}</a><a href="#meeting-outputs">${zh('17:00 输出','17:00 outputs')}</a><a href="#readback">${zh('最终 Read-back','Final read-back')}</a></div>`;
  }
  function renderHero(){
    const ready=DATA.papers.filter(p=>p.stanford?.status==='READY').length;
    const rs=DATA.route_summary||{};
    const oa=DATA.overlay_audit||{};
    const auditLabel=oa.final_sufficiency_status==='VALID_INDEPENDENT_REVIEW' ? `${zh('Final sufficiency 独立审查','Final sufficiency independent review')} · ${esc(oa.final_sufficiency_verdict||'')}` : (oa.postfix_status==='FIXES_APPLIED_DETERMINISTIC_PASS' ? zh('Reality/Cost 独立审查 · REVISE→FIXED','Reality/Cost independent audit · REVISE→FIXED') : zh('Reality/Cost 独立审查待闭合','Reality/Cost audit pending closure'));
    const freezeLabel=DATA.meeting.freeze_status==='MEETING_CANDIDATE_FROZEN' ? `${zh('会议候选已冻结','Meeting candidate frozen')} · ${(DATA.meeting.candidate_hash||'').slice(0,12)}…` : zh('会议候选尚未冻结','Meeting candidate not frozen');
    return `<section class="advisor-hero"><div><div class="eyebrow">ADVISOR REVIEW · 2026-09-06</div><h1>${zh('九篇论文决策驾驶舱','Nine-paper advisor decision cockpit')}</h1><p>${zh('默认不是淘汰赛：九篇都继续推进，但推进方式不同。师兄现场只处理会改变路线的 premise、paper boundary、shared dependency、next closure 和 override；每篇论文与 Stanford 外审绑定同一个 PDF SHA。','This is not a paper-elimination contest. All nine advance, but through different routes. Senior time is reserved for premise, boundary, shared dependency, next closure, and overrides; advisor and Stanford review the same PDF SHA.')}</p><div class="advisor-hero-meta"><span>main · ${esc((DATA.meeting.main_ref||'').slice(0,12))}…</span><span>${zh('Paper Pack','Paper Pack')} · ${esc(DATA.meeting.status||'')}</span><span>${esc(freezeLabel)}</span><span>${zh('外审 advisory only','External review advisory only')}</span><span>${esc(auditLabel)}</span></div></div><div class="advisor-kpis"><article><b>9/9</b><span>${zh('论文可直接打开','papers directly readable')}</span></article><article><b>${ready}/9</b><span>${zh('Stanford 外审已返回','Stanford reviews ready')}</span></article><article><b>${rs.FREEZE_SUBMIT||0}</b><span>${zh('冻结 / 投稿','freeze / submit')}</span></article><article><b>${rs.EXECUTE_FROZEN||0}</b><span>${zh('按冻结协议执行','execute frozen')}</span></article><article><b>${rs.QUALIFY_FIRST||0}</b><span>${zh('先过资格门','qualify first')}</span></article><article><b>${rs.FORMALIZE_FIRST||0}</b><span>${zh('先形式化 scientific object','formalize first')}</span></article></div></section>`;
  }
  function renderMeetingPath(){
    const paperChip=p=>`<a class="advisor-path-paper" href="#${esc(paperAnchor(p))}"><span>${paperSeq(p)}</span><b>${esc(shortPaperName(p))}</b><small>${esc(routeLabel(p.route))}</small></a>`;
    const byId=id=>DATA.papers.find(p=>p.paper_id===id);
    const groups=[
      {time:'14:15–14:28',title:zh('先定 abstraction','Abstraction first'),papers:['E1']},
      {time:'14:28–15:28',title:'Memory / Provenance / Evolution',papers:['B1','C1','E2','PAPER_A','PAPER_B']},
      {time:'15:28–15:53',title:zh('Safety + Externality','Safety + Externality'),papers:['G1','CONSTRAINT_EXTERNALITY']},
      {time:'15:53–16:08',title:zh('3D topology premise','3D topology premise'),papers:['3D']}
    ];
    const body=groups.map(g=>`<section><header><b>${esc(g.time)}</b><span>${esc(g.title)}</span></header><div>${g.papers.map(byId).filter(Boolean).map(paperChip).join('')}</div></section>`).join('');
    return `<section class="advisor-section advisor-meeting-path" id="meeting-path"><header><div><div class="eyebrow">DURING MEETING · ${zh('按这个顺序讲','FOLLOW THIS ORDER')}</div><h2>${zh('九篇只走一条会议路径；①–⑨ 是现场讲述序号','One meeting route for all nine papers; ①–⑨ are the live speaking order')}</h2><p>${zh('14:00–14:15 先用 Portfolio Dashboard 校准全局；之后严格按下列序号进入论文。论文详情默认收进 Evidence Drawer，主屏只保留会改变路线的决策信息。','Use 14:00–14:15 for the portfolio dashboard, then enter papers strictly in the order below. Technical detail stays collapsed in the Evidence Drawer; the main surface keeps only route-changing decisions.')}</p></div><span class="advisor-live-mode">DURING MEETING</span></header><div class="advisor-path-groups">${body}</div><div class="advisor-path-tail"><span>16:08–16:28 · Exceptions / Ownership</span><span>16:28–16:40 · Resources / Authority</span><span>16:40–16:53 · Decision Ledger</span><span>16:53–17:00 · Read-back</span></div></section>`;
  }
  function renderPortfolio(){
    const rows=orderedPapers().map(p=>`<tr><td><div class="advisor-paper-name"><div class="advisor-paper-heading"><span class="advisor-paper-seq">${paperSeq(p)}</span><b>${esc(shortPaperName(p))} · ${esc(p.title)}</b></div><small>${paperType(p)} · ${p.pages}p · ${esc(p.pdf_sha256.slice(0,10))}…</small><a href="#${esc(paperAnchor(p))}">${zh('进入现场 Decision Card ↓','Open live Decision Card ↓')}</a><a href="${esc(p.pdf)}" target="_blank" rel="noopener">${zh('打开 PDF ↗','Open PDF ↗')}</a></div></td><td><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><small class="advisor-default-action">${esc(p.default_action)}</small></td><td>${esc(compact(p.best_case,190))}</td><td>${esc(compact(p.next_closure,190))}</td><td><strong class="advisor-cost-class">${esc(p.cost_class)}</strong><small>${esc(compact(p.cost_to_next_decision,150))}</small></td><td><span class="advisor-review-state ${p.stanford?.status==='READY'?'ready':'processing'}">${reviewLabel(p)}</span>${p.stanford?.status==='READY'?`<div class="advisor-score-note">AI ref · ${esc(p.stanford.numerical_score??'–')} · ${esc(p.stanford.textual_signal||'')}</div>`:''}</td><td>${esc(compact(p.advisor_question,170))}</td></tr>`).join('');
    return `<section class="advisor-section" id="portfolio"><header><div><h2>${zh('九篇 Portfolio Decision Matrix','Nine-paper portfolio decision matrix')}</h2><p>${zh('每篇默认动作已经冻结；师兄只需要判断是否触发 override。成本只算到“下一道会改变判断的 gate”，不是把整篇最大实验量一次性承诺。','Each paper has a frozen default route. Senior review only needs to decide whether an override is warranted. Cost is measured to the next decision-changing gate, not the paper’s maximum possible workload.')}</p></div></header><div class="advisor-table-wrap"><table class="matrix advisor-table advisor-decision-table"><thead><tr><th>Paper</th><th>${zh('默认路线','Default route')}</th><th>Best Case</th><th>${zh('下一 closure','Next closure')}</th><th>${zh('到下一判断的成本','Cost to next decision')}</th><th>Stanford</th><th>${zh('师兄主问题','Senior decision')}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderRisks(){
    const own=DATA.claim_ownership_map||{};
    const ownership=['B1','PAPER_A','PAPER_B'].map(pid=>{const x=own[pid]||{};return `<article><b>${esc(pid)}</b><strong>${esc(x.primary_claim_owner||'')}</strong><p>${esc(x.relationship||'')}</p></article>`}).join('');
    const reopen=(DATA.shared_risk_reopen_rules||[]).map(r=>`<tr><td><b>${esc(r.premise)}</b></td><td>${esc((r.directly_affected||[]).join(' · '))}</td><td>${esc((r.conditionally_affected||[]).join(' · ')||'—')}</td><td>${esc(r.reopen_threshold||'')}</td></tr>`).join('');
    return `<section class="advisor-section" id="shared-risks"><header><div><h2>${zh('共同失效风险 / Claim Ownership / Reopen Rule','Shared invalidation risk / claim ownership / reopen rule')}</h2><p>${zh('师兄不是泛泛讨论“要不要 merge”，而是先批准主 claim owner，再冻结 shared premise 失败时到底重开谁。','Do not stop at merge/no-merge. First approve the primary claim owner, then freeze exactly which papers reopen if a shared premise fails.')}</p></div></header><div class="advisor-ownership-grid">${ownership}</div><div class="advisor-note"><strong>${zh('Memory family 默认边界','Default memory-family boundary')}</strong> · ${esc(own.boundary_note||'')}</div><div class="advisor-risk-grid">${DATA.shared_risks.map(r=>`<article class="advisor-risk-card"><b>${esc(r.label)}</b><span>${esc(r.question)}</span><small>${r.papers.map(esc).join(' · ')}</small><p>${esc(r.reopen_rule||'')}</p></article>`).join('')}</div><div class="advisor-table-wrap"><table class="matrix advisor-reopen-table"><thead><tr><th>Shared premise</th><th>Direct</th><th>Conditional</th><th>Reopen threshold</th></tr></thead><tbody>${reopen}</tbody></table></div></section>`;
  }
  function renderMeetingOutputs(){
    const rows=(DATA.meeting_outputs||[]).map((x,i)=>`<article><span>${String(i+1).padStart(2,'0')}</span><p>${esc(x)}</p></article>`).join('');
    return `<section class="advisor-section" id="meeting-outputs"><header><div><h2>${zh('17:00 前必须锁定的 5 个输出','Five outputs that must be locked by 17:00')}</h2><p>${zh('会议成功标准不是“讨论了九篇”，而是这些 receipt-level outputs 都有明确结论、owner 与 follow-up。','The meeting succeeds only when these receipt-level outputs have a concrete decision, owner, and follow-up—not merely because all nine papers were discussed.')}</p></div></header><div class="advisor-output-grid">${rows}</div></section>`;
  }
  function renderCostDependencies(){
    const lanes=(DATA.portfolio_schedule||[]).map(x=>`<article><b>${esc(x.lane)}</b><span>${esc((x.papers||[]).join(' · '))}</span><p>${esc(x.action)}</p></article>`).join('');
    const rows=orderedPapers().map(p=>{const r=resource(p),d=dims(p),op=r.operational_snapshot||{};const condLabel=r.conditional_envelope_label||'FUTURE CONDITIONAL — not current commitment';return `<tr><td><b>${paperSeq(p)} ${esc(shortPaperName(p))}</b><br><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span>${op.observed_at?`<small>Operational snapshot · ${esc(op.observed_at)}</small>`:''}</td><td><p><b>CURRENT</b> ${esc(r.current_decision_cost||authorizedText(p))}</p><p>${esc(d.api_cash||'UNKNOWN')} · ${esc(d.local_gpu_occupancy||'UNKNOWN')}</p></td><td><p>${esc(d.post_meeting_execution_human_hours||'UNKNOWN')}</p></td><td><p>${esc(d.provider_credential_dependency||'UNKNOWN')}</p></td><td><p>${esc(d.calendar_latency||'UNKNOWN')}</p></td><td><p><b>STOP</b> ${esc(r.cost_to_stop||'')}</p></td><td><p><b>NEXT IF PASS</b> ${esc(r.next_if_pass||'')}</p><p class="advisor-conditional-envelope"><b>${esc(condLabel)}</b> ${esc(r.conditional_envelope||'')}</p></td></tr>`}).join('');
    return `<section class="advisor-section" id="cost-dependencies"><header><div><h2>${zh('跨论文资源冲突检查','Cross-paper resource conflict check')}</h2><p>${zh('这里只检查会改变调度的稀缺资源冲突。Human 列明确是会后执行工时，不是 14:00–17:00 的会议分钟；CURRENT、STOP 与 FUTURE CONDITIONAL 分开显示。','Only scarce-resource conflicts that change scheduling belong here. Human hours are post-meeting execution effort, not advisor-meeting minutes; CURRENT, STOP, and FUTURE CONDITIONAL are shown separately.')}</p></div></header><div class="advisor-scheduling-grid">${lanes}</div><div class="advisor-table-wrap"><table class="matrix advisor-cost-table"><thead><tr><th>Paper / Route</th><th>Current authorized cost</th><th>Post-meeting human-hours</th><th>Provider / Credential</th><th>Calendar</th><th>Cost-to-Stop</th><th>Next / Future conditional</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
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
  function decisionControl(p){
    const current=decisions[p.paper_id]||{};
    const options=[['KEEP',zh('KEEP','KEEP')],['MODIFY',zh('MODIFY','MODIFY')],['FOLLOW_UP',zh('FOLLOW-UP','FOLLOW-UP')]];
    return `<section class="advisor-live-decision" data-decision-paper="${esc(p.paper_id)}"><div class="advisor-live-decision-head"><div><b>${zh('现场拍板','LIVE DECISION')}</b><span data-current-decision>${esc(decisionLabel(current.status))}</span></div><small>${zh('只记录师兄对当前路线的 override；不自动改变 scientific authority','Records the advisor override only; never changes scientific authority automatically')}</small></div><div class="advisor-live-decision-actions">${options.map(([key,label])=>`<button type="button" data-decision-choice="${key}" class="${current.status===key?'selected':''}">${esc(label)}</button>`).join('')}</div><input type="text" data-decision-note value="${esc(current.note||'')}" placeholder="${zh('一句话备注：为什么改 / 谁 follow-up / 何时回看','One-line note: why / owner / follow-up trigger')}"></section>`;
  }
  function renderCards(){
    const groupStarts={
      E1:[zh('14:15–14:28 · ① E1','14:15–14:28 · ① E1'),zh('只判断 standalone abstraction / reality premise；不重开已经闭合的窄 claim。','Judge the standalone abstraction/reality premise only; do not reopen the closed narrow claim.')],
      B1:[zh('14:28–15:28 · ②–⑥ Memory / Provenance / Evolution','14:28–15:28 · ②–⑥ Memory / Provenance / Evolution'),zh('按 ②B1 → ③C1 → ④E2 → ⑤Paper A → ⑥Paper B 走；先看 ownership/boundary，再看各自唯一 senior decision。','Follow ②B1 → ③C1 → ④E2 → ⑤Paper A → ⑥Paper B; resolve ownership/boundary before each single senior decision.')],
      G1:[zh('15:28–15:53 · ⑦–⑧ G1 + Constraint Externality','15:28–15:53 · ⑦–⑧ G1 + Constraint Externality'),zh('只判断两条线的 standalone value 与最小下一 gate。','Judge standalone value and the smallest next gate only.')],
      '3D':[zh('15:53–16:08 · ⑨ 3D','15:53–16:08 · ⑨ 3D'),zh('只判断 realistic topology premise，不把会议拖进训练细节。','Judge the realistic topology premise only; do not drift into training details.')]
    };
    const cards=orderedPapers().map(p=>{
      const group=groupStarts[p.paper_id];
      const groupHtml=group?`<div class="advisor-card-group-label"><b>${esc(group[0])}</b><span>${esc(group[1])}</span></div>`:'';
      return `${groupHtml}<article class="advisor-card" id="${esc(paperAnchor(p))}" data-paper="${esc(p.paper_id)}"><header><div class="advisor-card-seq"><strong>${paperSeq(p)}</strong><span>${esc(shortPaperName(p))}</span></div><div><h3>${esc(p.title)}</h3><small>${paperType(p)} · ${p.pages}p · SHA ${esc(p.pdf_sha256.slice(0,12))}…</small></div><div class="advisor-card-actions"><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><a href="${esc(p.pdf)}" target="_blank" rel="noopener">PDF ↗</a></div></header><div class="advisor-card-body"><div class="advisor-live-summary"><section><b>ONE-SENTENCE STORY</b><p>${esc(p.story)}</p></section><section class="advisor-evidence-state"><b>EVIDENCE STATE</b><p>${esc(p.evidence_state)}</p></section><section class="advisor-risk-box"><b>DECISION-CHANGING RISK</b><p>${esc(p.risk)}</p></section><section class="advisor-next-closure"><b>NEXT CLOSURE</b><p>${esc(p.next_closure)}</p></section></div><section class="advisor-question advisor-question-live"><b>${zh('师兄只需拍板','SENIOR DECISION')}</b><p>${esc(p.advisor_question)}</p></section>${decisionControl(p)}<details class="advisor-evidence-drawer"><summary><span>${zh('Evidence Drawer · 展开实验、baseline、资源、Stanford 与版本细节','Evidence Drawer · experiments, baseline, resources, Stanford, version')}</span><small>${zh('默认折叠，问到再开','collapsed by default')}</small></summary><div class="advisor-evidence-drawer-body"><section class="advisor-best-case"><b>Best Case</b><p>${esc(p.best_case)}</p></section>${realitySupport(p)}<div class="advisor-decision-grid"><section><b>PREMISE TO CONFIRM</b><p>${esc(p.premise)}</p></section><section><b>STRONGEST SIMPLIFICATION / BASELINE</b><p>${esc(p.strongest_simplification)}</p></section></div><div class="advisor-closure-grid"><section><b>AUTHORIZED NOW</b><strong>${esc(authorizedText(p))}</strong><p>${esc(resource(p).priority_note||'')}</p></section><section><b>DEPENDENCIES</b><p>${esc(depText(p))}</p></section><section><b>COST TO NEXT DECISION</b><p>${esc(p.cost_to_next_decision||'')}</p></section></div><div class="advisor-action-grid"><section><b>DEFAULT ACTION</b><strong>${esc(p.default_action)}</strong></section><section><b>OVERRIDE TRIGGER</b><p>${esc(p.override_trigger)}</p></section></div><section class="advisor-cross-paper"><b>CROSS-PAPER LEVERAGE</b><p>${esc(p.cross_paper_leverage)}</p></section>${reviewDigest(p)}<section class="advisor-delta-box"><b>Science delta after PDF</b><p>${esc(p.science_delta)}</p></section><details class="advisor-version-fold"><summary>${zh('版本与权限信息','Version / authority detail')}</summary><div><b>Paper candidate</b>: ${esc(p.paper_candidate_ref)}<br><b>Scientific canonical</b>: ${esc(p.scientific_canonical_ref)}<br><b>PDF SHA256</b>: ${esc(p.pdf_sha256)}<br>${zh('Stanford 外审仅是 advisory overlay；不授予 scientific / experiment / submission authority。','Stanford review is advisory only and grants no scientific, experiment, or submission authority.')}</div></details></div></details></div></article>`;
    }).join('');
    return `<section class="advisor-section" id="paper-review"><header><div><h2>${zh('①–⑨ 现场 Decision Cards','①–⑨ live decision cards')}</h2><p>${zh('每篇主屏只保留：一句话故事、当前 evidence、route-changing risk、next closure、唯一 advisor question 和现场拍板。其余全部默认收进 Evidence Drawer。','Each main card keeps only the one-sentence story, current evidence, route-changing risk, next closure, the single advisor question, and the live decision. Everything else is collapsed into the Evidence Drawer.')}</p></div><div class="advisor-filter-row"><button class="advisor-filter active" data-filter="all">${zh('全部','All')}</button><button class="advisor-filter" data-filter="review-ready">Stanford Ready</button><button class="advisor-filter" data-filter="attention">${zh('外审需关注','Review attention')}</button><button class="advisor-filter" data-filter="preconfirm">Preconfirm</button></div></header><div class="advisor-cards">${cards}</div></section>`;
  }
  function renderDecisionLedger(){
    const rows=orderedPapers().map(p=>{const d=decisions[p.paper_id]||{};return `<tr><td><b>${paperSeq(p)} ${esc(shortPaperName(p))}</b></td><td>${esc(routeLabel(p.route))}</td><td><strong data-ledger-status="${esc(p.paper_id)}">${esc(decisionLabel(d.status))}</strong></td><td data-ledger-note="${esc(p.paper_id)}">${esc(d.note||'—')}</td><td>${esc(compact(p.next_closure,220))}</td></tr>`}).join('');
    const done=orderedPapers().filter(p=>decisions[p.paper_id]?.status).length;
    return `<section class="advisor-section" id="decision-ledger"><header><div><div class="eyebrow">16:40–16:53 · LOCK THE LEDGER</div><h2>${zh('九篇 disposition / override 现场账本','Nine-paper live disposition / override ledger')}</h2><p>${zh('卡片上的 KEEP / MODIFY / FOLLOW-UP 会保存在当前浏览器 localStorage，并同步到这里；它只是会议记录层，不会自动授予实验、GPU、provider 或投稿权限。','KEEP / MODIFY / FOLLOW-UP choices are stored in this browser localStorage and mirrored here. This is a meeting-record layer only; it never grants experiment, GPU, provider, or submission authority.')}</p></div><strong class="advisor-ledger-progress"><span id="advisor-decision-progress">${done}/9</span>${zh('已拍板','decided')}</strong></header><div class="advisor-table-wrap"><table class="matrix advisor-ledger-table"><thead><tr><th>Paper</th><th>${zh('冻结路线','Frozen route')}</th><th>${zh('现场决定','Live decision')}</th><th>${zh('一句话备注','One-line note')}</th><th>Next closure</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderReadback(){
    const unresolved=orderedPapers().filter(p=>!decisions[p.paper_id]?.status);
    return `<section class="advisor-section advisor-readback" id="readback"><header><div><div class="eyebrow">16:53–17:00 · READ-BACK</div><h2>${zh('最后 7 分钟只做逐项念回，不再开新讨论','Use the final seven minutes only to read decisions back')}</h2><p>${zh('确认九篇 disposition、跨论文 ownership/reopen、资源 authority 与所有 named follow-up。','Confirm nine dispositions, cross-paper ownership/reopen rules, resource authority, and every named follow-up.')}</p></div></header><div class="advisor-readback-status"><strong id="advisor-readback-count">${9-unresolved.length}/9</strong><div><b>${zh('论文决定已记录','paper decisions recorded')}</b><p id="advisor-readback-unresolved">${unresolved.length?`${zh('仍未拍板','Still pending')}: ${unresolved.map(p=>`${paperSeq(p)} ${shortPaperName(p)}`).join(' · ')}`:zh('九篇均已记录；现在核对 exceptions、resources、owner 与 follow-up。','All nine recorded; now confirm exceptions, resources, owners, and follow-ups.')}</p></div></div></section>`;
  }
  function renderSchedule(){
    return `<section class="advisor-section" id="schedule"><header><div><h2>${zh('14:00–17:00 最终议程','Final 14:00–17:00 route')}</h2><p>${zh('前半段解决 abstraction/boundary，后半段只做 exception-based closure 与资源调度。','Resolve abstraction and boundaries first; the second half only locks exceptions, closures, and scheduling.')}</p></div></header><div class="advisor-schedule">${DATA.schedule.map(x=>`<article><b>${esc(x.start)}–${esc(x.end)}</b><span>${esc(x.label)}</span></article>`).join('')}</div></section>`;
  }
  function applyFilter(){
    const q=($('#advisor-search')?.value||'').toLowerCase().trim(); let n=0;
    DATA.papers.forEach(p=>{const el=document.querySelector(`[data-paper="${CSS.escape(p.paper_id)}"]`); if(!el)return; const show=cardMatches(p,q); el.classList.toggle('hidden',!show); if(show)n++;});
    const c=$('#result-count'); if(c)c.textContent=`${n}/9 ${zh('篇','papers')}`;
  }
  function refreshDecisionSurfaces(){
    orderedPapers().forEach(p=>{
      const d=decisions[p.paper_id]||{};
      document.querySelectorAll('[data-decision-paper]').forEach(panel=>{if(panel.dataset.decisionPaper!==p.paper_id)return;const label=panel.querySelector('[data-current-decision]');if(label)label.textContent=decisionLabel(d.status);panel.querySelectorAll('[data-decision-choice]').forEach(btn=>btn.classList.toggle('selected',btn.dataset.decisionChoice===d.status));});
      document.querySelectorAll('[data-ledger-status]').forEach(el=>{if(el.dataset.ledgerStatus===p.paper_id)el.textContent=decisionLabel(d.status);});
      document.querySelectorAll('[data-ledger-note]').forEach(el=>{if(el.dataset.ledgerNote===p.paper_id)el.textContent=d.note||'—';});
    });
    const unresolved=orderedPapers().filter(p=>!decisions[p.paper_id]?.status);
    const progress=$('#advisor-decision-progress'); if(progress)progress.textContent=`${9-unresolved.length}/9`;
    const count=$('#advisor-readback-count'); if(count)count.textContent=`${9-unresolved.length}/9`;
    const pending=$('#advisor-readback-unresolved'); if(pending)pending.textContent=unresolved.length?`${zh('仍未拍板','Still pending')}: ${unresolved.map(p=>`${paperSeq(p)} ${shortPaperName(p)}`).join(' · ')}`:zh('九篇均已记录；现在核对 exceptions、resources、owner 与 follow-up。','All nine recorded; now confirm exceptions, resources, owners, and follow-ups.');
  }
  function bind(){
    const search=$('#advisor-search'); if(search) search.oninput=applyFilter;
    document.querySelectorAll('.advisor-filter').forEach(btn=>{btn.onclick=()=>{filter=btn.dataset.filter;document.querySelectorAll('.advisor-filter').forEach(x=>x.classList.toggle('active',x===btn));applyFilter();};});
    document.querySelectorAll('[data-decision-choice]').forEach(btn=>{btn.onclick=()=>{const panel=btn.closest('[data-decision-paper]');if(!panel)return;const id=panel.dataset.decisionPaper;decisions[id]={...(decisions[id]||{}),status:btn.dataset.decisionChoice};saveDecisions();refreshDecisionSurfaces();};});
    document.querySelectorAll('[data-decision-note]').forEach(input=>{input.oninput=()=>{const panel=input.closest('[data-decision-paper]');if(!panel)return;const id=panel.dataset.decisionPaper;decisions[id]={...(decisions[id]||{}),note:input.value};saveDecisions();refreshDecisionSurfaces();};});
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
    root.innerHTML=`${renderHero()}${renderMeetingPath()}${renderSchedule()}${renderPortfolio()}${renderCards()}${renderRisks()}${renderCostDependencies()}${renderMeetingOutputs()}${renderDecisionLedger()}${renderReadback()}<div class="advisor-note"><strong>${zh('阅读纪律','Reading rule')}</strong> · ${zh('PDF_READY 是完整候选稿；ADVISOR_DRAFT_PRECONFIRMATORY 是为师兄和外审准备的完整可读草稿，但决定性实验仍是 prospective。任何 PDF 后新增 science delta 必须单独看，不能默认已经写进论文。Decision Card 与现场 Decision Ledger 都只是 advisory projection，不改变 Research OS scientific/experiment authority。','PDF_READY is an integrated candidate. ADVISOR_DRAFT_PRECONFIRMATORY is a complete readable draft whose decisive evidence is still prospective. Post-PDF science deltas remain separate. Decision Cards and the live Decision Ledger are advisory projections and cannot change Research OS scientific or experiment authority.')}</div>`;
    const b=$('#advisor-lang'); if(b)b.textContent=lang==='zh'?'EN':'中文';
    bind(); applyFilter(); refreshDecisionSurfaces();
  }
  render();
})();
