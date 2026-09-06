(() => {
  const DATA = window.ADVISOR_MEETING_DATA || {papers:[],shared_risks:[],schedule:[],meeting:{}};
  const LANG_KEY = 'advisor-review-language';
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
  const reviewLabel = p => p.stanford?.status==='READY' ? zh('当前稿外审已返回','Current review ready') : p.stanford?.status==='PRIOR_VERSION' ? zh('上一版外审参考','Prior-version review') : zh('外审还在返回中','Review processing');
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
  const shortPaperName = p => ({PAPER_A:zh('论文 A','Paper A'),PAPER_B:zh('论文 B','Paper B'),CONSTRAINT_EXTERNALITY:zh('约束外部性','Constraint Externality')})[p.paper_id] || p.paper_id;
  const PAPER_TITLES_ZH={E1:'技能怎么拆，不该改变智能体能用到什么',B1:'失败记忆的“来源信息”到底有没有用',C1:'差异怎么写进记忆，又为什么不一定传到行为',G1:'安全结论为什么会随评测器而变',E2:'同一证据为什么会再生成出不同技能状态',PAPER_A:'失败记忆真的来自原始失败吗：来源忠实度因果审计',CONSTRAINT_EXTERNALITY:'修一个约束，会不会伤到别的能力',PAPER_B:'智能体什么时候才算真正“自我进化”', '3D':'3D 场景里，不只关系数量，关系拓扑也重要'};
  const paperTitle = p => lang==='zh'?(PAPER_TITLES_ZH[p.paper_id]||p.title):p.title;
  const BEGINNER_ZH={
    E1:{story:'同样的技能知识，如果只是拆分方式不同，智能体最后能用到的能力不应该跟着变；这篇研究“表示方式不能左右能力”的条件。',evidence:'主结论已经闭合：Skill-SP、SkillRL 和 AutoSkill 提供了三类互补证据；当前没有必须补的主实验。',risk:'风险是这个问题可能只在特定技能系统成立；现有行为层证据仍有限，不能把结果写成普遍的效用或安全结论。',next:'当前窄版不新增实验；师兄只需决定直接冻结投稿，还是以后单开可选扩展。',question:'这个问题在真实智能体技能系统里是否足够常见、足够重要，值得单独成篇？'},
    B1:{story:'记忆内容完全一样，只多给模型看“这条记忆来自成功还是失败”，行为会不会变？这篇就在测来源信息本身有没有因果价值。',evidence:'Qwen 189 已封存；Llama 阶段已有 R82 执行权限，运行状态看下方资源表。此前少数翻转可以重复，但效果依赖执行模型。',risk:'风险是最终成功/失败的变化比较少，而且主要发生在特定执行模型；如果效果不稳定，独立成篇价值会下降。',next:'先让已授权阶段按冻结协议完成并封存；中途不看科学结果，也不临时加实验。',question:'在效果较少且依赖执行模型的情况下，这篇应独立成篇，还是作为论文 A 的补充证据？'},
    C1:{story:'反馈可以先被写进长期记忆，但“写进去”不等于以后一定会影响行为；这篇把“怎么写进去”和“为什么传不下去”放在同一条链路里研究。',evidence:'当前主张已闭合：写入、措辞对照、强制暴露、原生暴露/采纳/结果链条都有对应证据，不再新增实验。',risk:'写入实验同时改变了指令和结果语义，所以不能说成“纯奖励位因果”；后半段也只能定位传输在哪一阶段变弱，不能说成完整因果中介。',next:'不跑新实验；只收敛统一叙事，师兄决定合成一篇还是拆出 C2。',question:'把“差异怎么写进记忆”和“为什么不一定传到行为”合成一篇，是否比拆成 C1/C2 更完整、更有说服力？'},
    E2:{story:'给模型完全相同的证据，再生成一次长期技能/状态，结果可能变得很不一样；这篇研究这种“状态再生成不稳定”。',evidence:'历史证据显示同一证据再生成状态会不稳定；当前新阶段先做模型身份资格确认，避免把路由或模型混乱误当成科学现象。',risk:'如果所谓不稳定其实来自模型身份、路由或实现细节混乱，它就不是可靠的科学现象。',next:'只做一次模型身份/路由资格确认；过关后才考虑另行授权 M3R4。',question:'“同一证据重新生成状态会不稳定”是不是一个足够基础、足够重要的科学问题？'},
    PAPER_A:{story:'失败经历被写成记忆后，我们要问：这条记忆究竟忠实保留了原始失败，还是只产生了看似合理但来源不忠实的影响？',evidence:'目前是预确证设计：因果对象和“来源忠实度”正在形式化，128 次 VLA 实验还没有授权。',risk:'来源忠实度可能被简单的提示词或格式差异解释，所以必须先把最小因果对象和对照定义死。',next:'先把因果对象、忠实度定义和空操作对照写清楚；没冻结之前不跑 128 次 VLA。',question:'“记忆是否忠实于来源”这个因果问题是否足够独立，还是更适合作为论文 B 或 B1 的一部分？'},
    PAPER_B:{story:'真正的自我进化不只是当前回合变好，而是一次经验形成的持久状态要跨回合继续影响后续行为；这篇要因果确认这件事。',evidence:'目前是预确证设计：精确状态分叉和因果对象还要形式化，阶段 A 的 128 次 VLA 尚未授权。',risk:'跨回合差异可能来自其他上下文变化，而不是持久记忆本身，所以必须用精确分叉控制其他因素。',next:'先把精确持久状态分叉和因果估计对象形式化；通过后才申请 阶段 A 的 128 次 VLA。',question:'如果论文 A 负责“来源是否忠实”，论文 B 是否应该专门负责“持久状态跨回合是否真的产生因果影响”？'},
    G1:{story:'同一批智能体轨迹，换一个安全评测器可能得到不同结论；所以长期安全结论不能假装与评测器无关。',evidence:'同一轨迹在 HarmBench 与 DeepSeek 评测器下会给出不同当前通过结论和时间排序；剩余关键缺口是人工语义裁决。',risk:'目前主要是一套 主模型/基准；缺人工语义裁决前，不能把评测器分歧直接当成真实有害行为差异。',next:'补完 24 项人工语义标注/裁决，然后冻结 ERTA 稿件；不启动 MCTA。',question:'“同一轨迹会因评测器不同而得到不同安全结论”本身是否足够重要，值得独立成篇？'},
    CONSTRAINT_EXTERNALITY:{story:'修好一个局部规则时，可能无意中伤到其他能力；这篇要测这种“修一处、坏别处”的外部性。',evidence:'科学实验尚未启动；先恢复模型服务额度/接口，并通过一次就绪性资格门。',risk:'局部修复后的副作用可能只是模型随机波动或任务耦合，所以后续必须使用严格配对的对照。',next:'先恢复额度/接口，再单独申请一次非科学的就绪性请求；没过关就不跑后续。',question:'在做更大实验前，是否值得优先把“修一个约束会伤到别处”这个问题单独验证？'},
    '3D':{story:'生成 3D 场景时，不只是“有多少关系”重要，关系共享端点、形成链或枢纽等拓扑结构也可能决定模型难度。',evidence:'当前主线是已授权的两路训练；本页不读取验证、测试或拓扑结果，P1 验证要等训练封存后再单独授权。',risk:'难度可能只是因为关系数量更多，而不是拓扑本身，所以必须做“关系数量相同、拓扑不同”的配对对照。',next:'只让当前已授权训练跑到封存；封存后再单独决定 P1 验证，不提前增加随机种子或关系。',question:'“关系拓扑”是不是 3D 指令理解里一个足够独立的新难点，值得作为这篇论文的核心？'}
  };
  const beginner = (p,key) => {if(lang==='zh'&&BEGINNER_ZH[p.paper_id]?.[key])return BEGINNER_ZH[p.paper_id][key];return ({story:p.story,evidence:p.evidence_state,risk:p.risk,next:p.next_closure,question:p.advisor_question})[key]||'';};
  const CN_TERMS=[['The advisor meeting is strategy/scheduling guidance only and grants no scientific, experiment, provider, GPU, or submission authority.','师兄交流只提供策略和排期建议，不会自动授予科学结论、实验、模型服务、GPU 或投稿权限。'],['Finish manuscript/advisor decisions immediately; no scarce compute.','立即完成论文和师兄决策，不占稀缺算力。'],['Let frozen jobs run uninterrupted; collect only operational receipts, no interim science.','让已经冻结的任务继续跑完，只收运行记录，中途不做科学结论分析。'],['Resolve credential/identity/credit gates one at a time; spend only the next-gate budget.','逐个解决凭证、模型身份和额度问题，只花到下一道关键门所需的资源。'],['Use Web GPT + human review to freeze the causal objects before allocating VLA GPU runs.','先用网页版 GPT 和人工评审把因果对象定义清楚，再决定是否分配 VLA GPU 实验。'],['A · cheap closure','A · 低成本收口'],['B · already-running compute','B · 已经在跑的计算'],['C · near-zero qualification','C · 近零成本资格确认'],['D · formalize before compute','D · 先定义清楚再用算力'],['author/advisor positioning and submission signoff only','只需作者/师兄确认定位并完成投稿确认'],['human signoff only; not compute-bound','只等人工确认；不受算力限制'],['human/editorial only; not compute-bound','只需人工编辑；不受算力限制'],['human-review bound, not compute-bound','主要受人工评审时间限制，不受算力限制'],['one request once provider is available','模型服务恢复后只需 1 次请求'],['same-condition replay contract','同条件重放协议'],['fidelity signature','忠实度特征'],['no-op tolerance','空操作容忍度'],['semantic sensitivity','语义敏感性'],['persistent-state','持久状态'],['source/mechanism blocks','来源/机制实验块'],['provider calls','模型服务调用'],['GPU-hours','GPU 小时'],['wall-clock','实际耗时'],['shared decoder','共享解码器'],['shared-decoder','共享解码器'],['already-running','已经在跑'],['actively serving','正在运行'],['planned cap','计划上限'],['active monitoring','主动监控'],['scientific formalization','科学问题形式化'],['operational recovery','运行恢复'],['current decision cost','当前决策成本'],['separate successor authority','后续单独授权'],['fresh experiment authority','新的实验授权'],['fresh protocol approval','新的协议批准'],['fresh compute authority','新的算力授权'],['separate authority','单独授权'],['current claim','当前主张'],['No new compute','不新增计算'],['No new experiment','不新增实验'],['No new science execution','不新增科学实验'],['not compute-bound','不受算力限制'],['formalization first','先完成形式化'],['requires','需要'],['require','需要'],['optional','可选'],['future','未来'],['separate','单独'],['existing','现有'],['current','当前'],['fresh','新的'],['new','新增'],['scientific','科学'],['experiment','实验'],['submission','投稿'],['review','评审'],['compute','计算'],['analysis','分析'],['training','训练'],['validation','验证'],['replication','复现'],['monitoring','监控'],['qualification','资格确认'],['formalization','形式化'],['execution','执行'],['request','请求'],['calls','次调用'],['call','调用'],['identity','身份'],['model','模型'],['runtime','运行时'],['throughput','吞吐'],['frozen','已冻结'],['seal','封存'],['decoder','解码器'],['credit/interface','额度/接口'],['readiness','就绪性'],['account funding','账户充值'],['call budget','调用预算'],['seeds','随机种子'],['relations','关系'],['fork','分叉'],['N/A','无'],['UNKNOWN','待确认'],['human-hours','人工工时'],['human','人工'],['abstraction','抽象'],['Agent','智能体'],['agent','智能体'],['package','技能包'],['support geometry','支持结构'],['residual/equalizable regimes','残差/可均衡区间'],['fresh-ID','新 ID'],['identity sensitivity','身份敏感性'],['bounded witness','有界证据'],['held-out','留出'],['propagation','传播'],['access-level','访问层'],['access','访问'],['utility/safety','效用/安全'],['narrow','窄版'],['contract','协议'],['follow-up','跟进'],['ZERO_REQUIRED / OPTIONAL_MEDIUM','当前无需新增资源 / 可选扩展中等'],['MEDIUM / ALREADY_RUNNING','中等 / 已在运行'],['NEAR_ZERO_NOW / HIGH_IF_QUALIFIED','当前近零 / 资格通过后较高'],['LOW_NOW / MEDIUM_IF_QUALIFIED','当前较低 / 资格通过后中等'],['HUMAN_ONLY','只需人工'],['VERY_HIGH / ALREADY_RUNNING','很高 / 已在运行'],['CURRENT CLAIM SCIENCE CLOSED','当前主张：科学结论已闭合'],['FUTURE CONDITIONAL','未来条件项'],['same-information controls','同信息对照'],['same-information control','同信息对照'],['same-trajectory','同轨迹'],['forced exposure','强制暴露'],['native exposure','原生暴露'],['current-pass','当前通过情况'],['first-action','首个动作'],['exact rerun','精确复跑'],['source outcome','来源结果'],['decision boundary','判断边界'],['human semantic','人工语义'],['claim-expansion','主张扩展'],['representation invariance','表示不变性'],['finite-budget','有限预算'],['semantic projection','语义投影'],['skill ecosystem','技能生态'],['evaluator-independent','独立于评测器'],['load-bearing','关键承重'],['standalone','独立成篇'],['prospective','前瞻计划'],['integrated','整合版'],['provider','模型/API 服务'],['executor','执行模型'],['evaluator','评测器'],['trajectory','轨迹'],['baseline','基线'],['premise','前提'],['override','改路线条件'],['closure','收口'],['authority','权限'],['claim','主张'],['evidence','证据'],['capability','能力'],['skill','技能'],['memory','记忆'],['feedback','反馈'],['behavior','行为'],['state','状态'],['writer','写入器'],['native','原生'],['stage','阶段'],['terminal','最终结果'],['uptake','采纳'],['outcome','结果'],['route','路线'],['task','任务'],['paper','论文'],['CURRENT','当前'],['STOP','停止'],['HOLD','保留'],['CRITICAL','关键风险'],['MIXED_POSITIVE','总体积极但有保留'],['POSITIVE','积极']];
  const cn = v => {let x=String(v??'');if(lang!=='zh')return x;for(const [a,b] of CN_TERMS)x=x.split(a).join(b);return x;};
  const decisionLabel = status => ({KEEP:zh('保持当前路线','KEEP · current route'),MODIFY:zh('修改当前路线','MODIFY · change route'),FOLLOW_UP:zh('会后再决定','FOLLOW-UP · post-meeting decision')})[status] || zh('待现场拍板','Pending');
  const saveDecisions = () => localStorage.setItem(DECISION_KEY, JSON.stringify(decisions));
  const buildMeetingReceipt = () => ({
    schema_version:'1.0',
    receipt_type:'advisor-meeting-decision-receipt',
    meeting_id:DATA.meeting?.id||'2026-09-06-advisor',
    meeting_candidate_hash:DATA.meeting?.candidate_hash||'',
    recorded_at:new Date().toISOString(),
    decisions:orderedPapers().map(p=>({paper_id:p.paper_id,sequence:paperSeq(p),frozen_route:p.route,decision:(decisions[p.paper_id]||{}).status||'PENDING',note:(decisions[p.paper_id]||{}).note||'',next_closure:p.next_closure,advisor_question:p.advisor_question})),
    claim_ownership_map:DATA.claim_ownership_map||{},
    shared_risk_reopen_rules:DATA.shared_risk_reopen_rules||[],
    resource_authority:orderedPapers().map(p=>({paper_id:p.paper_id,authorized_now:resource(p).authorized_now||{},cost_to_stop:resource(p).cost_to_stop||'',next_authority_gate:resource(p).next_authority_gate||'',future_conditional:resource(p).conditional_envelope||'',explicit_non_authority:resource(p).explicit_non_authority||''})),
    operational_overlay:DATA.operational_overlay||{},
    authority:{scientific:false,experiment:false,provider:false,gpu:false,submission:false,advisor_meeting_projection_only:true}
  });
  const mdCell = v => String(v||'').replace(/\|/g,'\\|').replace(/\s*\n\s*/g,' ');
  const receiptMarkdown = () => {
    const r=buildMeetingReceipt();
    const rows=r.decisions.map(x=>`| ${x.sequence} ${mdCell(x.paper_id)} | ${mdCell(x.frozen_route)} | ${mdCell(x.decision)} | ${mdCell(x.note)||'—'} | ${mdCell(x.next_closure)} |`).join('\n');
    const ownership=Object.entries(r.claim_ownership_map||{}).map(([k,v])=>`- **${mdCell(k)}**: ${mdCell(typeof v==='string'?v:JSON.stringify(v))}`).join('\n');
    const reopen=(r.shared_risk_reopen_rules||[]).map(x=>`- **${mdCell(x.premise||x.primitive||'shared risk')}** → direct: ${mdCell((x.directly_affected||[]).join(', '))}; conditional: ${mdCell((x.conditional_papers||x.conditionally_affected||[]).join(', '))}; threshold: ${mdCell(x.reopen_threshold||'')}`).join('\n');
    return `# 师兄交流决策记录 · 2026-09-06\n\n- 会议候选: \`${r.meeting_candidate_hash}\`\n- 记录时间: ${r.recorded_at}\n- 权限说明：这只是师兄交流记录，不会自动授予科学结论、实验、模型服务、GPU 或投稿权限。\n\n## 九篇论文决策\n\n| Paper | 冻结路线 | 现场决定 | Note | 下一步收口 |\n|---|---|---|---|---|\n${rows}\n\n## 主张归属\n${ownership||'- none'}\n\n## 共同风险重开规则\n${reopen||'- none'}\n`;
  };
  const copyReceiptMarkdown = async () => {
    const text=receiptMarkdown();
    try {
      if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);return true;}
    } catch (_) {}
    const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok;
  };
  const downloadReceiptMarkdown = () => {
    const blob=new Blob([receiptMarkdown()],{type:'text/markdown;charset=utf-8'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='advisor-meeting-receipt-20260906.md';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);
  };
  const downloadReceiptJson = () => {
    const blob=new Blob([JSON.stringify(buildMeetingReceipt(),null,2)+'\n'],{type:'application/json'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='advisor-meeting-receipt-20260906.json';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);
  };
  const authorizedText = p => {
    const a=resource(p).authorized_now||{};
    return [a.gpu?`GPU ${a.gpu}`:'',a.api_units!==undefined?`API ${a.api_units}`:'',a.cash_cny!==undefined?`cash ${a.cash_cny}`:'',a.work||''].filter(Boolean).join(' · ');
  };

  function renderNav(){
    const nav=$('.nav'); if(!nav)return;
    const groups=window.NAV_GROUPS||[];
    nav.innerHTML=groups.map(group=>{const localLabel=v=>lang==='zh'?String(v||'').replace('Agent','智能体').replace('ResearchItems','九篇论文').replace('Paper A','论文 A').replace('Paper B','论文 B').replace('Influence–Fidelity','来源忠实度'):String(v||'');return `<details class="nav-group" open><summary class="nav-level1"><span>${esc(localLabel(group.title?.[lang]||group.title?.en||''))}</span><span class="nav-chevron">⌃</span></summary><div class="nav-children">${(group.pages||[]).map(([href,label])=>`<a class="nav-level2 ${href==='advisor-review.html'?'active':''}" href="${esc(href)}">${esc(localLabel(label?.[lang]||label?.en||href))}</a>`).join('')}</div></details>`}).join('');
  }
  function renderToc(){
    const toc=$('#page-toc'); if(!toc)return;
    const paperLinks=orderedPapers().map(p=>`<a href="#${esc(paperAnchor(p))}">${paperSeq(p)} ${esc(shortPaperName(p))}</a>`).join('');
    toc.innerHTML=`<div class="toc-title">${zh('会议导航 · 14:00–17:00','Meeting path · 14:00–17:00')}</div><div class="toc-links"><a href="#meeting-path">${zh('3 小时单一路线','3-hour single route')}</a><a href="#portfolio">${zh('九篇总览','Portfolio')}</a>${paperLinks}<a href="#shared-risks">${zh('跨论文风险 / 共用前提','Cross-paper exceptions / shared risks')}</a><a href="#cost-dependencies">${zh('资源与权限','Resources & authority')}</a><a href="#decision-ledger">${zh('锁定决策记录','Lock decision ledger')}</a><a href="#readback">${zh('最后逐项确认','Final read-back')}</a><a href="#spinoffs">${zh('会后分叉候选','Post-meeting spinoffs')}</a></div>`;
  }
  function renderHero(){
    const ready=DATA.papers.filter(p=>p.stanford?.status==='READY').length;
    const prior=DATA.papers.filter(p=>p.stanford?.status==='PRIOR_VERSION').length;
    const rs=DATA.route_summary||{};
    const oa=DATA.overlay_audit||{};
    const auditLabel=(oa.stale_for_papers||[]).length ? `${zh('现实依据/成本审查需按当前版本理解','Reality/Cost prior audit partially stale')} · ${(oa.stale_for_papers||[]).join('/')}` : (oa.postfix_status==='FIXES_APPLIED_DETERMINISTIC_PASS' ? zh('现实依据/成本独立审查 · 已修正','Reality/Cost independent audit · REVISE→FIXED') : zh('现实依据/成本审查待收口','Reality/Cost audit pending closure'));
    const freezeLabel=DATA.meeting.freeze_status==='MEETING_CANDIDATE_FROZEN' ? `${zh('会议候选已冻结','Meeting candidate frozen')} · ${(DATA.meeting.candidate_hash||'').slice(0,12)}…` : zh('会议候选尚未冻结','Meeting candidate not frozen');
    return `<section class="advisor-hero"><div><div class="eyebrow">师兄审阅 · 2026-09-06</div><h1>${zh('九篇论文决策驾驶舱','Nine-paper advisor decision cockpit')}</h1><p>${zh('这不是淘汰赛。九篇都继续，但推进方式不同。现场只回答几类关键问题：论文前提是否成立、边界有没有说过头、是否依赖别的论文、下一步最小要补什么、有没有理由改变当前路线。外审只作为参考，而且严格对应具体 PDF 版本。','This is not a paper-elimination contest. All nine advance, but through different routes. Senior time is reserved for premise, boundary, shared dependency, next closure, and overrides; exact current reviews are SHA-bound; materially changed manuscripts show prior-version reviews explicitly rather than reusing them as current evidence.')}</p><div class="advisor-hero-meta"><span>${zh('主分支','main')} · ${esc((DATA.meeting.main_ref||'').slice(0,12))}…</span><span>${zh('九篇论文包','Paper Pack')} · ${esc(DATA.meeting.status||'')}</span><span>${esc(freezeLabel)}</span><span>${zh('外审仅供参考','External review advisory only')}</span><span>${esc(auditLabel)}</span></div></div><div class="advisor-kpis"><article><b>9/9</b><span>${zh('论文可直接打开','papers directly readable')}</span></article><article><b>${ready}/9</b><span>${zh('当前版本外审已返回','exact-current reviews')}</span></article><article><b>${prior}</b><span>${zh('上一版外审参考','prior-version review')}</span></article><article><b>${rs.FREEZE_SUBMIT||0}</b><span>${zh('冻结 / 投稿','freeze / submit')}</span></article><article><b>${rs.EXECUTE_FROZEN||0}</b><span>${zh('按冻结协议执行','execute frozen')}</span></article><article><b>${rs.QUALIFY_FIRST||0}</b><span>${zh('先过资格门','qualify first')}</span></article><article><b>${rs.FORMALIZE_FIRST||0}</b><span>${zh('先把科学问题定义清楚','formalize first')}</span></article></div></section>`;
  }
  function renderMeetingPath(){
    const paperChip=p=>`<a class="advisor-path-paper" href="#${esc(paperAnchor(p))}"><span>${paperSeq(p)}</span><b>${esc(shortPaperName(p))}</b><small>${esc(routeLabel(p.route))}</small></a>`;
    const byId=id=>DATA.papers.find(p=>p.paper_id===id);
    const groups=[
      {time:'14:15–14:28',title:zh('先定核心抽象','Abstraction first'),papers:['E1']},
      {time:'14:28–15:28',title:zh('记忆 / 来源信息 / 自我进化','Memory / Provenance / Evolution'),papers:['B1','C1','E2','PAPER_A','PAPER_B']},
      {time:'15:28–15:53',title:zh('安全评测 + 约束外部性','Safety + Externality'),papers:['G1','CONSTRAINT_EXTERNALITY']},
      {time:'15:53–16:08',title:zh('3D 关系拓扑前提','3D topology premise'),papers:['3D']}
    ];
    const body=groups.map(g=>`<section><header><b>${esc(g.time)}</b><span>${esc(g.title)}</span></header><div>${g.papers.map(byId).filter(Boolean).map(paperChip).join('')}</div></section>`).join('');
    return `<section class="advisor-section advisor-meeting-path" id="meeting-path"><header><div><div class="eyebrow">${zh('现场交流 · 按这个顺序讲','DURING MEETING · FOLLOW THIS ORDER')}</div><h2>${zh('九篇只走一条会议路径；①–⑨ 是现场讲述序号','One meeting route for all nine papers; ①–⑨ are the live speaking order')}</h2><p>${zh('14:00–14:15 先用九篇总览校准全局；之后严格按下列序号进入论文。论文技术细节默认折叠，主屏只保留会改变路线的决策信息。','Use 14:00–14:15 for the portfolio dashboard, then enter papers strictly in the order below. Technical detail stays collapsed in the Evidence Drawer; the main surface keeps only 会改变路线的决策.')}</p></div><span class="advisor-live-mode">${zh('现场讲述','DURING MEETING')}</span></header><div class="advisor-path-groups">${body}</div><div class="advisor-path-tail"><span>16:08–16:28 · 跨论文风险 / 归属</span><span>16:28–16:40 · 资源 / 权限</span><span>16:40–16:53 · 锁定决策记录</span><span>16:53–17:00 · 逐项复述确认</span></div></section>`;
  }
  function renderPortfolio(){
    const rows=orderedPapers().map(p=>`<tr><td><div class="advisor-paper-name"><div class="advisor-paper-heading"><span class="advisor-paper-seq">${paperSeq(p)}</span><b>${esc(shortPaperName(p))} · ${esc(paperTitle(p))}</b></div><small>${paperType(p)} · ${p.pages} 页</small><a href="#${esc(paperAnchor(p))}">${zh('查看这篇 ↓','Open live card ↓')}</a><a href="${esc(p.pdf)}" target="_blank" rel="noopener">${zh('打开 PDF ↗','Open PDF ↗')}</a></div></td><td>${esc(beginner(p,'story'))}</td><td><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span></td><td>${esc(beginner(p,'next'))}</td><td><span class="advisor-review-state ${p.stanford?.status==='READY'?'ready':p.stanford?.status==='PRIOR_VERSION'?'prior':'processing'}">${reviewLabel(p)}</span>${['READY','PRIOR_VERSION'].includes(p.stanford?.status)?`<div class="advisor-score-note">${zh('外审参考','AI ref')} · ${esc(p.stanford.numerical_score??'–')} · ${esc(cn(p.stanford.textual_signal||''))}</div>`:''}</td><td>${esc(beginner(p,'question'))}</td></tr>`).join('');
    return `<section class="advisor-section" id="portfolio"><header><div><h2>${zh('九篇总览：每篇现在怎么推进','Nine-paper portfolio overview')}</h2><p>${zh('这张表只留现场讲述真正需要的六件事：这篇讲什么、默认怎么走、下一步只做什么、外审状态，以及师兄只需要判断哪一个问题。','This table keeps only the six fields needed for the live discussion.')}</p></div></header><div class="advisor-table-wrap"><table class="matrix advisor-table advisor-decision-table"><thead><tr><th>论文</th><th>${zh('一句话讲什么','One-line story')}</th><th>${zh('默认怎么推进','Default route')}</th><th>${zh('下一步只做什么','Next step')}</th><th>${zh('Stanford 外审','Stanford review')}</th><th>${zh('师兄只判断什么','Senior decision')}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderRisks(){
    const owners=[['B1','来源字段是否提供额外决策信息','可以为论文 A/B 提供前置对照，但不负责“来源是否忠实”或跨回合总因果效应。'],['论文 A','记忆是否忠实传递原始来源信息','负责来源忠实度和机制读出；如果与论文 B 同时保留，它不是跨回合总效应的主负责人。'],['论文 B','持久更新是否跨回合造成因果影响','负责完整的跨回合因果链；论文 A 的忠实度可作为机制证据，但不是主结论。'],['C1','反馈 → 记忆写入 → 行为传输','负责“怎么写进去、为什么不一定传下去”的两幕链。'],['E2','同一证据 → 状态再生成不稳定','负责状态生成不稳定，不等同于 C1 的写入/传输问题。'],['G1','长期安全结论对评测器的依赖','ERTA 是 G1 主论文；MCTA 是另一个候选，不应因为 MCTA 成败而重开 G1。']];
    const primary=owners.map(x=>`<article><b>${esc(x[0])}</b><strong>${esc(x[1])}</strong><p>${esc(x[2])}</p></article>`).join('');
    const rules=[['技能表示 / 身份','E1','E2、C1','只有同一个技能包身份/访问机制对 E2 或 C1 也是真正关键前提时才重开；否则只重开 E1。'],['记忆 / 状态定义','B1、论文 A、论文 B','C1、E2','只重开实际依赖同一记忆/状态定义的论文，不能因为都谈“记忆”就整组重开。'],['来源信息三篇的归属','B1、论文 A、论文 B','—','B1=来源字段的增量价值；论文 A=来源忠实度；论文 B=跨回合总因果效应。只有边界真的重叠才考虑合并。'],['评测有效性','G1','C1、B1','G1 直接依赖评测器有效性；C1/B1 只有在自己的终点也依赖同一假设时才重开。']];
    const reopen=rules.map(r=>`<tr><td><b>${esc(r[0])}</b></td><td>${esc(r[1])}</td><td>${esc(r[2])}</td><td>${esc(r[3])}</td></tr>`).join('');
    return `<section class="advisor-section" id="shared-risks"><header><div><h2>${zh('共同风险、论文归属和重开规则','Shared invalidation risk / claim ownership / reopen rule')}</h2><p>${zh('先说清每篇到底负责哪个核心结论，再约定共同前提失败时只重开真正受影响的论文。不要因为几篇都谈“记忆”就一起推倒。','Clarify ownership first, then reopen only papers directly affected by a failed shared premise.')}</p></div></header><div class="advisor-ownership-grid">${primary}</div><div class="advisor-table-wrap"><table class="matrix advisor-reopen-table"><thead><tr><th>共同前提</th><th>直接影响</th><th>可能连带</th><th>什么时候才重开</th></tr></thead><tbody>${reopen}</tbody></table></div></section>`;
  }
  function renderMeetingOutputs(){
    const items=['九篇论文都要有一个明确决定：继续当前路线、修改路线，或会后再定。','明确 B1 / 论文 A / 论文 B 的边界；C1、E2、G1 的主结论默认保持各自独立。','锁定共同风险重开规则：哪个前提失败、直接影响谁、什么条件下才连带重开。','锁定资源安排：当前允许做什么、做到哪里停、通过后才做什么；所有新增实验仍需单独授权。','所有没当场解决的问题，都必须有明确负责人、明确输出和明确回看时间，不能只写“再想想”。'];
    const rows=items.map((x,i)=>`<article><span>${String(i+1).padStart(2,'0')}</span><p>${esc(x)}</p></article>`).join('');
    return `<section class="advisor-section" id="meeting-outputs"><header><div><h2>${zh('17:00 前必须锁定的 5 件事','Five outputs that must be locked by 17:00')}</h2><p>${zh('会议成功不是“九篇都聊过”，而是这五件事都留下清楚的决定和负责人。','The meeting succeeds only when these five outputs are concrete.')}</p></div></header><div class="advisor-output-grid">${rows}</div></section>`;
  }
  function resourceBrief(p){
    const op=resource(p).operational_snapshot||{};
    const base={
      E1:{now:'¥0；不占 GPU。只需论文定位、师兄确认和投稿准备。',human:'1–3 小时',wait:'不等模型服务；只等人工确认。',stop:'不新增计算。若现实前提不成立，就冻结窄版或合并，不打开可选扩展。',next:'当前窄版没有必须新增的实验；V4 只有明确重开并重新授权后才做。'},
      B1:{now:`Qwen 189 已封存；Llama 132 已有 R82 权限${op.llama_process_detected?'，当前正在 231 / cuda:0 运行':'，运行状态以最新运行快照为准'}。`,human:'少于 1 小时主动监控',wait:'不等模型服务；只等已授权阶段完成，不根据中途进度推断科学结果。',stop:'不临时发明新实验，也不改正在跑的 Llama 阶段；技术失败按冻结规则停。',next:'封存后若要做跨模型分析、强模型规模检查或改论文主张，都要另行授权。'},
      C1:{now:'¥0；不占 GPU。只做统一叙事、PDF 检查和师兄评审。',human:'2–4 小时',wait:'不等模型服务；只需人工编辑。',stop:'不新增计算。若两幕统一故事不成立，就用现有证据拆分/改写，不重开实验。',next:'当前主张不需要新实验；任何拆分后的新实验都必须明确重开科学问题。'},
      E2:{now:'只做 1 次非科学的模型身份/路由确认；按计费量估算约 ¥0.02。',human:'少于 1 小时',wait:'等 Ark/模型服务可用，并确认实际 DeepSeek 模型身份。',stop:'单次身份确认失败就停，不打开 72 个单元的 M3R4。',next:'只有身份门通过后，才能另行授权 M3R4：72 个逻辑单元，模型调用硬上限 720 次。'},
      G1:{now:'¥0；不占 GPU，也不新增模型调用。只做已有 24 项人工语义标注/裁决和论文收口。',human:'4–8 小时（计划上限）',wait:'主要等人工评审，不受算力限制。',stop:'不新增模型/GPU 工作；如果评测器相对性不够独立成篇，就收窄或合并，不为“工作量”再加第三评测器。',next:'人工证据整合后冻结 ERTA；第三评测器、跨模型复现或 MCTA 都是另外的新科学问题。'},
      PAPER_A:{now:'当前 ¥0、0 GPU；先把因果对象和来源忠实度定义清楚。128 次 VLA 只是未来条件项。',human:'2–5 小时',wait:'当前不等模型服务；先完成形式化。后续 GPU 类型、数量和运行时要在预检查里冻结。',stop:'如果忠实度特征、空操作容忍度、终点指标或同条件重放协议无法冻结，就不跑 128 次 VLA。',next:'通过后才申请 阶段 A：32 单元 × 4 条件 = 128 次本地 VLA；需要新的协议和执行授权。'},
      CONSTRAINT_EXTERNALITY:{now:'当前 ¥0，承诺的模型调用数为 0；只恢复额度/接口。',human:'少于 1 小时运行恢复',wait:'先恢复同一模型服务的额度/接口，再单独申请 1 次就绪性请求权限。',stop:'额度/接口恢复不了，或单次就绪性门失败，就不进入来源/机制实验。',next:'只有新的就绪性请求通过后，才可能进入后续门；每一道后续门 都要单独授权。'},
      PAPER_B:{now:'当前 ¥0、0 GPU；只做因果估计对象和精确持久状态分叉的形式化。128 次 VLA 只是未来条件项。',human:'2–5 小时',wait:'当前不等模型服务；先完成形式化，后续运行时再单独预检查。',stop:'如果精确持久状态分叉无法稳定复现，就不进 阶段 A；如果 阶段 A 语义敏感性失败，就不进 阶段 B。',next:'阶段 A 通过后才可申请 128 次本地 VLA；阶段 B 仍需要另一份独立授权。'},
      '3D':{now:`只运行已经授权的两路训练${op.shared_decoder?.process_alive&&op.sgp14?.process_alive?'：共享解码器 GPU3 + SGP-14 GPU4':'；当前运行状态以最新快照为准'}，不打开验证/测试结果。`,human:'3–6 小时总监控预算',wait:'只等当前两路训练封存；不根据训练日志推断科学结论。',stop:'先让已授权训练封存；之后最先做词汇/显著性检查和 P1。P1 失败就不加随机种子或关系。',next:'两路训练都封存后，P1 验证仍要单独授权；复现种子/更多关系更要另行申请算力。'}
    };
    return base[p.paper_id]||{now:cn(resource(p).current_decision_cost||authorizedText(p)),human:cn(dims(p).post_meeting_execution_human_hours||'待确认'),wait:cn(dims(p).calendar_latency||'待确认'),stop:cn(resource(p).cost_to_stop||''),next:cn(resource(p).next_if_pass||'')};
  }
  function renderCostDependencies(){
    const lanes=(DATA.portfolio_schedule||[]).map(x=>`<article><b>${esc(cn(x.lane))}</b><span>${esc((x.papers||[]).map(id=>id==='PAPER_A'?'论文 A':id==='PAPER_B'?'论文 B':id==='CONSTRAINT_EXTERNALITY'?'约束外部性':id).join(' · '))}</span><p>${esc(cn(x.action))}</p></article>`).join('');
    const rows=orderedPapers().map(p=>{const b=resourceBrief(p);return `<tr><td><b>${paperSeq(p)} ${esc(shortPaperName(p))}</b><br><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span></td><td>${esc(b.now)}</td><td>${esc(b.human)}</td><td>${esc(b.wait)}</td><td>${esc(b.stop)}</td><td>${esc(b.next)}</td></tr>`}).join('');
    return `<section class="advisor-section" id="cost-dependencies"><header><div><h2>${zh('资源怎么排：哪些现在能做，哪些必须等','Resource, cost, and scheduling')}</h2><p>${zh('这里只保留现场排期需要的信息：现在占什么资源、还要多少人工、在等什么、什么情况下立即停、通过后才做什么。','Only the scheduling facts needed in the meeting are shown here.')}</p></div></header><div class="advisor-scheduling-grid">${lanes}</div><div class="advisor-table-wrap"><table class="matrix advisor-cost-table"><thead><tr><th>论文 / 路线</th><th>现在占什么资源</th><th>会后人工时间</th><th>还在等什么</th><th>什么情况下立即停</th><th>通过后才做什么</th></tr></thead><tbody>${rows}</tbody></table></div><div class="advisor-note"><strong>权限提醒</strong> · 师兄交流只决定策略和排期，不会自动打开任何新增实验、GPU、模型服务或投稿权限。</div></section>`;
  }
  function realitySupport(p){
    const r=reality(p); const cases=r.supporting_cases||[];
    return `<details class="advisor-reality-fold"><summary><span>${zh('现实依据：最支持这篇的真实案例','Reality Support · strongest real-world cases')}</span><small>${esc(r.reality_verdict||'')}</small></summary><div class="advisor-reality-body"><div class="advisor-reality-cases">${cases.map(c=>`<a href="${esc(c.url)}" target="_blank" rel="noopener"><b>${esc(c.title)}</b><span>${esc(c.why)}</span></a>`).join('')}</div><div class="advisor-reality-boundary"><section><b>${zh('这些案例不能证明','What this does NOT prove')}</b><p>${esc(r.what_this_does_not_prove||'')}</p></section><section><b>${zh('最强工程逃逸 / 反例','Strongest escape / counter-case')}</b><p>${esc(r.strongest_escape||'')}</p></section></div></div></details>`;
  }
  function reviewDigest(p){
    const s=p.stanford||{};
    if(!['READY','PRIOR_VERSION'].includes(s.status)) return `<div class="advisor-processing">${zh('Stanford 外审已提交，当前仍在处理。PDF 已冻结；返回后只更新 review overlay，不更换审稿对象。','Stanford review is submitted and still processing. The PDF is frozen; only the review overlay will update.')}</div>`;
    const d=s.advisor_digest||{};
    const prior=s.status==='PRIOR_VERSION';
    return `<details class="advisor-review-fold ${prior?'advisor-review-prior':''}"><summary><span>${prior?zh('Stanford 上一版外审','Stanford PRIOR'):zh('Stanford 当前外审','Stanford')} · ${esc(s.numerical_score??'–')} · ${esc(s.textual_signal||'')}</span><small>${prior?zh('上一版 PDF，仅作历史参考','Prior PDF, historical guidance only'):zh('展开外部攻击证据','Open external review evidence')}</small></summary>${prior?`<div class="advisor-prior-review">${zh('这份外审对应紧邻上一版 PDF SHA，不是当前 meeting candidate；当前稿已发生 story framing 变化。','This review is bound to the immediately preceding PDF SHA, not the current meeting candidate; the current manuscript has materially changed framing.')}</div>`:''}<div class="advisor-review-digest"><section><b>${zh('外审最强正向','Strongest positive')}</b><p>${esc(compact(d.strongest_positive,640))}</p></section><section><b>${zh('可能改变结论的问题','可能改变结论的问题')}</b><p>${esc(compact(d.decision_changing_concern,640))}</p></section><section><b>${zh('审稿人最想追问','审稿人最想追问')}</b><p>${esc(compact(d.reviewer_question,640))}</p></section></div></details>`;
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
    const options=[['KEEP',zh('保持当前路线','KEEP')],['MODIFY',zh('修改路线','MODIFY')],['FOLLOW_UP',zh('会后再定','FOLLOW-UP')]];
    return `<section class="advisor-live-decision" data-decision-paper="${esc(p.paper_id)}"><div class="advisor-live-decision-head"><div><b>${zh('现场拍板','现场拍板')}</b><span data-current-decision>${esc(decisionLabel(current.status))}</span></div><small>${zh('这里只记录师兄是否建议改变当前路线；不会自动改变科学结论或实验权限','Records the advisor override only; never changes scientific authority automatically')}</small></div><div class="advisor-live-decision-actions">${options.map(([key,label])=>`<button type="button" data-decision-choice="${key}" class="${current.status===key?'selected':''}">${esc(label)}</button>`).join('')}</div><input type="text" data-decision-note value="${esc(current.note||'')}" placeholder="${zh('一句话备注：为什么改 / 谁 follow-up / 何时回看','一句话备注: why / owner / follow-up trigger')}"></section>`;
  }
  function renderCards(){
    const groupStarts={
      E1:[zh('14:15–14:28 · ① E1','14:15–14:28 · ① E1'),zh('只判断这个核心抽象在真实系统里是否成立、是否值得独立成篇；不重开已经闭合的窄结论。','只判断这个抽象在真实智能体系统里是否成立、是否值得独立成篇；不重开已经闭合的窄结论。')],
      B1:[zh('14:28–15:28 · ②–⑥ 记忆 / 来源信息 / 自我进化','14:28–15:28 · ②–⑥ 记忆 / 来源信息 / 自我进化'),zh('按 ②B1 → ③C1 → ④E2 → ⑤论文 A → ⑥论文 B 走；先看每篇负责什么结论、边界在哪里，再回答唯一的师兄问题。','按 ②B1 → ③C1 → ④E2 → ⑤论文 A → ⑥论文 B 走；每篇先看它到底负责什么结论、边界在哪里，再回答唯一的师兄问题。')],
      G1:[zh('15:28–15:53 · ⑦–⑧ 安全评测 + 约束外部性','15:28–15:53 · ⑦–⑧ 安全评测 + 约束外部性'),zh('只判断两条线是否值得独立成篇，以及最小下一步是什么。','只判断这条线是否值得独立成篇，以及下一步最小需要补什么。')],
      '3D':[zh('15:53–16:08 · ⑨ 3D','15:53–16:08 · ⑨ 3D'),zh('只判断真实 3D 场景里“关系拓扑”这个前提是否成立，不把会议拖进训练细节。','只判断真实 3D 场景里“关系拓扑”这个前提是否成立，不把会议拖进训练细节。')]
    };
    const cards=orderedPapers().map(p=>{
      const group=groupStarts[p.paper_id];
      const groupHtml=group?`<div class="advisor-card-group-label"><b>${esc(group[0])}</b><span>${esc(group[1])}</span></div>`:'';
      return `${groupHtml}<article class="advisor-card" id="${esc(paperAnchor(p))}" data-paper="${esc(p.paper_id)}"><header><div class="advisor-card-seq"><strong>${paperSeq(p)}</strong><span>${esc(shortPaperName(p))}</span></div><div><h3>${esc(paperTitle(p))}</h3><small>${paperType(p)} · ${p.pages} 页 · 版本指纹 ${esc(p.pdf_sha256.slice(0,12))}…</small></div><div class="advisor-card-actions"><span class="advisor-route ${routeClass(p.route)}">${esc(routeLabel(p.route))}</span><a href="${esc(p.pdf)}" target="_blank" rel="noopener">PDF ↗</a></div></header><div class="advisor-card-body"><div class="advisor-live-summary"><section><b>一句话讲明白</b><p>${esc(beginner(p,'story'))}</p></section><section class="advisor-evidence-state"><b>现在我们手里有什么证据</b><p>${esc(beginner(p,'evidence'))}</p></section><section class="advisor-risk-box"><b>最大风险是什么</b><p>${esc(beginner(p,'risk'))}</p></section><section class="advisor-next-closure"><b>下一步只做什么</b><p>${esc(beginner(p,'next'))}</p></section></div><section class="advisor-question advisor-question-live"><b>${zh('师兄只要回答这一句','SENIOR DECISION')}</b><p>${esc(beginner(p,'question'))}</p></section>${decisionControl(p)}<details class="advisor-evidence-drawer"><summary><span>${zh('详细证据 · 展开实验、基线、资源、Stanford 与版本细节','Evidence Drawer · experiments, baseline, resources, Stanford, version')}</span><small>${zh('默认折叠，问到再开','collapsed by default')}</small></summary><div class="advisor-evidence-drawer-body"><section class="advisor-best-case"><b>最理想情况</b><p>${esc(cn(p.best_case))}</p></section>${realitySupport(p)}<div class="advisor-decision-grid"><section><b>最需要确认的前提</b><p>${esc(cn(p.premise))}</p></section><section><b>最强简化解释 / 基线</b><p>${esc(cn(p.strongest_simplification))}</p></section></div><div class="advisor-closure-grid"><section><b>现在允许做什么</b><strong>${esc(authorizedText(p))}</strong><p>${esc(cn(resource(p).priority_note||''))}</p></section><section><b>依赖什么</b><p>${esc(cn(depText(p)))}</p></section><section><b>到下一次关键判断的成本</b><p>${esc(cn(p.cost_to_next_decision||''))}</p></section></div><div class="advisor-action-grid"><section><b>默认怎么推进</b><strong>${esc(cn(p.default_action))}</strong></section><section><b>什么情况下改路线</b><p>${esc(cn(p.override_trigger))}</p></section></div><section class="advisor-cross-paper"><b>对其他论文有什么帮助</b><p>${esc(cn(p.cross_paper_leverage))}</p></section>${reviewDigest(p)}<section class="advisor-delta-box"><b>论文 PDF 之后新增了什么</b><p>${esc(cn(p.science_delta))}</p></section><details class="advisor-version-fold"><summary>${zh('版本与权限信息','版本与权限信息')}</summary><div><b>论文候选版本</b>: ${esc(p.paper_candidate_ref)}<br><b>科学结论基准版本</b>: ${esc(p.scientific_canonical_ref)}<br><b>PDF 指纹</b>: ${esc(p.pdf_sha256)}<br>${zh('Stanford 外审只作为参考，不会自动授予科学结论、实验或投稿权限。','Stanford review is advisory only and grants no scientific, experiment, or submission authority.')}</div></details></div></details></div></article>`;
    }).join('');
    return `<section class="advisor-section" id="paper-review"><header><div><h2>${zh('①–⑨ 现场论文卡片','①–⑨ live decision cards')}</h2><p>${zh('每篇主屏只保留：一句话讲什么、现在有什么证据、最大风险、下一步只做什么、师兄只要回答哪一句。其他技术细节默认折叠，问到再展开。','Each main card keeps only the one-sentence story, current evidence, route-changing risk, next closure, the single advisor question, and the live decision. Everything else is collapsed into the Evidence Drawer.')}</p></div><div class="advisor-filter-row"><button class="advisor-filter active" data-filter="all">${zh('全部','All')}</button><button class="advisor-filter" data-filter="review-ready">${zh('Stanford 外审已返回','Stanford Ready')}</button><button class="advisor-filter" data-filter="attention">${zh('外审需关注','外审需关注')}</button><button class="advisor-filter" data-filter="preconfirm">${zh('待关键实验','Preconfirm')}</button></div></header><div class="advisor-cards">${cards}</div></section>`;
  }
  function renderDecisionLedger(){
    const rows=orderedPapers().map(p=>{const d=decisions[p.paper_id]||{};return `<tr><td><b>${paperSeq(p)} ${esc(shortPaperName(p))}</b></td><td>${esc(routeLabel(p.route))}</td><td><strong data-ledger-status="${esc(p.paper_id)}">${esc(decisionLabel(d.status))}</strong></td><td data-ledger-note="${esc(p.paper_id)}">${esc(d.note||'—')}</td><td>${esc(beginner(p,'next'))}</td></tr>`}).join('');
    const done=orderedPapers().filter(p=>decisions[p.paper_id]?.status).length;
    return `<section class="advisor-section" id="decision-ledger"><header><div><div class="eyebrow">16:40–16:53 · 锁定决策记录</div><h2>${zh('九篇论文现场决策记录','九篇论文现场决策记录')}</h2><p>${zh('卡片上的 现场的“保持路线 / 修改路线 / 会后再定”会自动汇总到这里。会议结束前导出一份记录即可；这里的选择只是会议意见，不会自动授予实验、GPU、模型服务或投稿权限。','KEEP / MODIFY / FOLLOW-UP choices are stored in this browser localStorage and mirrored here. Export the receipt before the meeting ends so the record is not trapped in one browser. This layer never grants experiment, GPU, provider, or submission authority.')}</p></div><div class="advisor-ledger-tools"><strong class="advisor-ledger-progress"><span id="advisor-decision-progress">${done}/9</span>${zh('已拍板','decided')}</strong><div class="advisor-receipt-actions"><button type="button" id="advisor-copy-receipt">${zh('复制会议记录','Copy Markdown')}</button><button type="button" id="advisor-download-md-receipt">${zh('下载会议记录','Download Markdown')}</button><button type="button" id="advisor-download-receipt">${zh('导出结构化记录','Download JSON')}</button></div></div></header><div class="advisor-table-wrap"><table class="matrix advisor-ledger-table"><thead><tr><th>论文</th><th>${zh('冻结路线','冻结路线')}</th><th>${zh('现场决定','现场决定')}</th><th>${zh('一句话备注','一句话备注')}</th><th>下一步收口</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  function renderReadback(){
    const unresolved=orderedPapers().filter(p=>!decisions[p.paper_id]?.status);
    return `<section class="advisor-section advisor-readback" id="readback"><header><div><div class="eyebrow">16:53–17:00 · 逐项复述确认</div><h2>${zh('最后 7 分钟只做逐项念回，不再开新讨论','Use the final seven minutes only to read decisions back')}</h2><p>${zh('逐项确认九篇怎么推进、跨论文结论归属、哪些情况需要重开、资源权限，以及每个会后任务由谁负责。','Confirm nine dispositions, cross-paper ownership/reopen rules, resource authority, and every named follow-up.')}</p></div></header><div class="advisor-readback-status"><strong id="advisor-readback-count">${9-unresolved.length}/9</strong><div><b>${zh('论文决定已记录','paper decisions recorded')}</b><p id="advisor-readback-unresolved">${unresolved.length?`${zh('仍未拍板','Still pending')}: ${unresolved.map(p=>`${paperSeq(p)} ${shortPaperName(p)}`).join(' · ')}`:zh('九篇均已记录；现在核对 exceptions、resources、owner 与 follow-up。','All nine recorded; now confirm exceptions, resources, owners, and follow-ups.')}</p></div></div></section>`;
  }
  function renderSpinoffs(){
    if(!(DATA.spinoffs||[]).length) return '';
    return `<section class="advisor-section" id="spinoffs"><header><div><h2>${zh('独立分叉候选','Separate spinoff candidates')}</h2><p>${zh('这些对象不计入当前九篇主论文，也不能当成原论文的后续版本放进同一条评分折线。','These objects are outside the nine-paper main portfolio and must not be plotted as later revisions of their parent paper.')}</p></div></header><div class="advisor-risk-grid">${DATA.spinoffs.map(x=>`<article class="advisor-risk-card"><b>${zh('G2 候选 · 能力解锁与安全漂移要分开测',esc(x.paper_id)+' · '+esc(x.title))}</b><span>${zh('这是 MCTA 能力匹配的独立候选，不是 G1/ERTA 的下一版。当前：暂缓，等待识别设计。',esc(x.relation)+' Status: '+esc(x.status)+'.')}</span><small>Stanford 外审参考 · ${esc(x.stanford?.numerical_score??'–')} · ${esc(cn(x.stanford?.textual_signal||''))}</small></article>`).join('')}</div></section>`;
  }

  function renderSchedule(){
    const zhLabels=['九篇总览 + 共同风险扫描','E1：只讨论核心抽象是否成立','记忆 / 来源信息论文组：先定归属和边界','G1 + 约束外部性：只判断独立价值和最小下一步','3D：只判断关系拓扑前提','处理仍未解决的例外和结论归属冲突','核对跨论文资源冲突','锁定九篇决策、重开规则和会后负责人','逐项念回并确认会议记录'];
    return `<section class="advisor-section" id="schedule"><header><div><h2>${zh('14:00–17:00 最终议程','Final 14:00–17:00 route')}</h2><p>${zh('前半段先把核心问题和论文边界讲清楚；后半段只处理例外、收口和资源安排。','Resolve core questions and boundaries first, then lock exceptions and scheduling.')}</p></div></header><div class="advisor-schedule">${DATA.schedule.map((x,i)=>`<article><b>${esc(x.start)}–${esc(x.end)}</b><span>${esc(lang==='zh'?(zhLabels[i]||cn(x.label)):x.label)}</span></article>`).join('')}</div></section>`;
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
    const copyReceipt=$('#advisor-copy-receipt'); if(copyReceipt) copyReceipt.onclick=async()=>{const original=copyReceipt.textContent;try{const ok=await copyReceiptMarkdown();copyReceipt.textContent=ok?zh('已复制 ✓','Copied ✓'):zh('复制受限，请下载','Copy blocked; download');setTimeout(()=>copyReceipt.textContent=original,1800);}catch(_){copyReceipt.textContent=zh('复制受限，请下载','Copy blocked; download');setTimeout(()=>copyReceipt.textContent=original,1800);}};
    const downloadMd=$('#advisor-download-md-receipt'); if(downloadMd) downloadMd.onclick=downloadReceiptMarkdown;
    const downloadReceipt=$('#advisor-download-receipt'); if(downloadReceipt) downloadReceipt.onclick=downloadReceiptJson;
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
    root.innerHTML=`${renderHero()}${renderMeetingPath()}${renderSchedule()}${renderPortfolio()}${renderCards()}${renderRisks()}${renderMeetingOutputs()}${renderCostDependencies()}${renderDecisionLedger()}${renderReadback()}${renderSpinoffs()}<div class="advisor-note"><strong>${zh('阅读规则','Reading rule')}</strong> · ${zh('本页优先服务现场讲述：主屏用中文讲结论和决策，技术细节需要时再展开。预确证草稿仍有关键实验尚未完成；论文 PDF 之后新增的科学结果必须单独标明，不能默认已经写进稿件。现场决策只是师兄意见，不会自动改变 Research OS 的科学结论或实验权限。','PDF_READY is an integrated candidate. ADVISOR_DRAFT_PRECONFIRMATORY is a complete readable draft whose decisive evidence is still prospective. Post-PDF science deltas remain separate. Decision Cards and the live Decision Ledger are advisory projections and cannot change Research OS scientific or experiment authority.')}</div>`;
    const b=$('#advisor-lang'); if(b)b.textContent=lang==='zh'?'EN':'中文';
    bind(); applyFilter(); refreshDecisionSurfaces();
  }
  render();
})();
