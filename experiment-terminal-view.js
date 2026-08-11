function p0AdmissionState(){return window.P0_ADMISSION_STATE||window.RESEARCH_SYSTEM_STATE?.p0_admission||{summary:{},cards:[]};}
function p0AdmissionCard(ideaId){return (p0AdmissionState().cards||[]).find(x=>x.idea_id===ideaId)||null;}
function terminalExperimentRows(){
  const ledger=humanTerminalState(), rows=[];
  const parents=new Map((window.ICLR_LOW_RESOURCE_IDEAS?.passed_ideas||[]).map(x=>[x.id||x.idea_id,x]));
  const finals=new Map((window.CURRENT_FINAL_IDEAS?.ideas||[]).map(x=>[x.id||x.idea_id,x]));
  for(const [id,terminal] of Object.entries(ledger.parents||{})){
    if(!["p0","p0-ready"].includes(terminal.terminal_state)) continue;
    const rich=parents.get(id)||finals.get(id)||{};
    rows.push({id,source:"parent",terminal,code:terminal.code||"",title:textOf(rich.title||terminal.title||terminal.final_parent_mechanism||{})||id});
  }
  for(const [id,terminal] of Object.entries(ledger.independent_methods||{})){
    if(!["p0","p0-ready"].includes(terminal.terminal_state)) continue;
    const rich=finals.get(id)||{};
    rows.push({id,source:"independent",terminal,code:terminal.code||"",title:textOf(rich.title||terminal.title||terminal.final_parent_mechanism||{})||id});
  }
  const rank={p0:0,"p0-ready":1};
  return rows.sort((a,b)=>{const d=(rank[a.terminal.terminal_state]??9)-(rank[b.terminal.terminal_state]??9); if(d)return d; if(a.source!==b.source)return a.source==="parent"?-1:1; return String(a.code||a.id).localeCompare(String(b.code||b.id),undefined,{numeric:true});});
}
function terminalExperimentIdeaHref(row){
  return row.source==="parent"&&row.code?`paper-ideas.html#idea-${esc(String(row.code).toLowerCase())}`:`paper-ideas.html#new-${esc(row.id)}`;
}
function terminalExperimentEvidence(row){
  const {id,terminal}=row, lifecycle=terminal.terminal_state||"p0";
  const admission=p0AdmissionCard(id);
  const iteration=(experimentIterationState().nodes||[]).find(x=>x.idea_id===id)||null;
  const runtime=p0RuntimeExecutions().find(x=>x.idea_id===id)||null;
  const phase=experimentPilotPhase(id,"P0");
  const preGpu=(preGpuCandidateGateState().candidates||[]).find(x=>x.idea_id===id)||null;
  const mem=window.RESEARCH_SYSTEM_STATE?.mem_xfer_workflow||{};
  if(["replicated-effect-memory-gate","cross-task-effect-transport-certificate"].includes(id)){
    const support=mem.support_qualification||{}, supportProgress=support.progress||{}, supportDecision=support.decision||{};
    const full=mem.full_support||{}, fullProgress=full.progress||{}, fullDecision=full.decision||{};
    const fullLive=["full_qwen_support_running","full_qwen_support_checkpoint","full_support_complete"].includes(full.status);
    const status=fullLive?full.status:support.status;
    const progress=fullLive?fullProgress:supportProgress;
    const fullLabel=fullLive?(language==="zh"?"共享 P0 · full Qwen support 已启动":"Shared P0 · full Qwen support started"):null;
    const detail=fullLive?(language==="zh"?`support qualification 已 PASS；full Qwen support 最新 artifact 为 ${progress.completed_episodes||0}/${progress.total_episodes||216} executions、${progress.completed_units||0}/${progress.total_units||72} units，尚无最终 decision。`:`Support qualification passed; the latest full Qwen support artifact is ${progress.completed_episodes||0}/${progress.total_episodes||216} executions and ${progress.completed_units||0}/${progress.total_units||72} units, with no final decision yet.`):textOf(terminal.current_fact||{});
    return {current_started:true,category:"started",tone:full.status==="full_support_complete"?"pass":"running",label:fullLabel||(language==="zh"?`共享 P0 已开始 · ${String(status||"running").toUpperCase()}`:`Shared P0 started · ${String(status||"running").toUpperCase()}`),detail:detail||`${progress.completed_episodes||0}/${progress.total_episodes||0} executions`,next:fullDecision.next_action||supportDecision.next_action||(language==="zh"?"第二 backbone 仍 HOLD，直到 full-support CPU-only decision 显式授权。":"Second backbone remains on HOLD until the full-support CPU-only decision explicitly authorizes it."),evidence:`${progress.completed_episodes||0}/${progress.total_episodes||0} executions · ${progress.completed_units||0}/${progress.total_units||0} units · ${progress.new_model_calls||progress.model_calls||0} calls`};
  }
  const runtimeStatus=String(runtime?.status||"").toLowerCase();
  const registryStarted=!!phase?.result||Boolean(phase?.status&&phase.status!=="planned");
  const runtimeStarted=["running","collected","registered","failed"].includes(runtimeStatus);
  const historicalP0=String(admission?.p0_entry?.date||"")==="historical";
  if(historicalP0||registryStarted||runtimeStarted){
    const failed=runtimeStatus==="failed";
    return {current_started:true,category:"started",tone:failed?"revise":"check",label:failed?(language==="zh"?"P0 已开始 · runtime 失败后诊断":"P0 started · runtime failure under diagnosis"):(language==="zh"?"P0 已开始 · 当前处于诊断/重跑门禁":"P0 started · diagnosis/rerun gate"),detail:runtime?.diagnosis||textOf(terminal.terminal_reason||{})||iteration?.diagnosis||"P0 lifecycle entered.",next:textOf(terminal.pre_p0_gate||{})||phase?.next_action||(language==="zh"?"只允许冻结协议下的诊断或合格重跑。":"Only frozen-protocol diagnosis or a qualified rerun is allowed."),evidence:runtimeStatus?`${runtimeStatus.toUpperCase()}${iteration?.diagnosis?` · ${iteration.diagnosis}`:""}`:(iteration?.diagnosis||"P0 artifact in terminal ledger")};
  }
  if(iteration){
    return {current_started:false,category:"historical-only",tone:"check",label:language==="zh"?"历史 Pilot 已跑；当前冻结 P0 未启动":"Historical pilot exists; current frozen P0 not started",detail:textOf(terminal.terminal_reason||{})||iteration.diagnosis||"--",next:textOf(terminal.pre_p0_gate||{})||textOf(terminal.minimum_p0||{})||"--",evidence:iteration.diagnosis?`historical diagnosis · ${iteration.diagnosis}`:"historical pilot artifact"};
  }
  if(preGpu){
    const d=preGpuDecisionMeta(preGpu.decision);
    return {current_started:false,category:"pre-gpu-only",tone:d.tone,label:language==="zh"?`仅完成 GPU 前置门 · ${d.zh}`:`Pre-GPU only · ${d.en}`,detail:preGpu.reason||textOf(terminal.terminal_reason||{})||"--",next:preGpu.next_action||textOf(terminal.pre_p0_gate||{})||"--",evidence:`offline=${preGpu.offline||"--"} · reality=${preGpu.reality||"--"} · phenomenon=${preGpu.phenomenon||"--"}`};
  }
  const pre=admission?.execution_preflight?.pre_p0||{}, outer=admission?.execution_preflight?.pre_experiment||{}, gpu0=admission?.execution_preflight?.gpu0||{};
  const evidence=admission?`admission 10/10 · GPU-0 ${gpu0.phenomenon||"--"} · Pre-P0 ${pre.passed||0}/${pre.total||10} · Gate ${outer.passed||0}/${outer.total||8}`:(language==="zh"?"无真实 P0 execution artifact":"No real P0 execution artifact");
  return {current_started:false,category:"not-started",tone:"planned",label:language==="zh"?"P0 已准入 · execution 未授权":"P0 admitted · execution locked",detail:textOf(terminal.terminal_reason||{})||(language==="zh"?"P0 合同已冻结，但没有真实执行 artifact。":"The P0 contract is frozen, but no real execution artifact exists."),next:gpu0.next||textOf(terminal.pre_p0_gate||{})||textOf(terminal.minimum_p0||{})||(language==="zh"?"完成 execution preflight 后再启动。":"Clear execution preflight before launch."),evidence};
}
function terminalExperimentBadge(state){return `<span class="experiment-status-badge status-${esc(state.tone||"planned")}">${esc(state.label||"--")}</span>`;}
function renderTerminalExperimentPortfolio(){
  const rows=terminalExperimentRows().map(row=>({...row,experiment:terminalExperimentEvidence(row)}));
  if(!rows.length) return "";
  const p0=rows.filter(x=>x.terminal.terminal_state==="p0"), ready=rows.filter(x=>x.terminal.terminal_state==="p0-ready"), started=rows.filter(x=>x.experiment.current_started), pending=rows.filter(x=>!x.experiment.current_started), pre=rows.filter(x=>x.experiment.category==="pre-gpu-only"), historical=rows.filter(x=>x.experiment.category==="historical-only");
  const body=rows.map(row=>{
    const life=row.terminal.terminal_state, code=row.code||(row.source==="independent"?(language==="zh"?"独立":"Standalone"):"--");
    return `<tr class="terminal-experiment-row terminal-exp-${esc(row.experiment.category)}" data-current-p0-started="${row.experiment.current_started?"1":"0"}" data-terminal-lifecycle="${esc(life)}"><td><a href="${terminalExperimentIdeaHref(row)}"><strong>${esc(code)}</strong><span>${esc(row.title)}</span><small>${esc(row.id)}</small></a></td><td><span class="terminal-lifecycle-badge lifecycle-${esc(life)}">${esc(humanReviewStatusLabel(life))}</span></td><td>${terminalExperimentBadge(row.experiment)}<small class="terminal-exp-evidence">${esc(row.experiment.evidence||"--")}</small></td><td><p>${esc(row.experiment.detail||"--")}</p></td><td><p>${esc(row.experiment.next||"--")}</p></td></tr>`;
  }).join("");
  return `<section class="panel terminal-experiment-portfolio" id="terminal-experiment-portfolio"><div class="idea-panel-heading"><div><div class="eyebrow">H1 → EXPERIMENT · 2026-08-11</div><h2 data-toc="false">${language==="zh"?"与 Paper Ideas 对齐的 20 个活跃方向实验总表":"Experiment status for the 20 active Paper Ideas"}</h2><p class="section-intro">${language==="zh"?"以 human terminal ledger 为唯一方向清单：13 个 parent P0 + 7 个独立 P0，活跃池 20/20 已全部进入 P0。P0 只表示实验合同已冻结，不等于真实执行已经开始；‘已开始’仍只认真实 P0/Pilot artifact。":"The human terminal ledger is the only active-direction list: 13 parent P0 plus 7 standalone P0, so all 20 active directions have entered P0. P0 means the experiment contract is frozen, not that execution has started; ‘started’ still requires a real P0/Pilot artifact."}</p></div><strong>${started.length}/20<span>${language==="zh"?"当前 P0 已开始":"current P0 started"}</span></strong></div><div class="terminal-experiment-stats"><div><b>${p0.length}</b><span>P0</span></div><div><b>${ready.length}</b><span>P0-ready</span></div><div class="stat-started"><b>${started.length}</b><span>${language==="zh"?"当前实验已开始":"current experiments started"}</span></div><div class="stat-pending"><b>${pending.length}</b><span>${language==="zh"?"当前 P0 未启动":"current P0 not started"}</span></div><div><b>${pre.length}</b><span>${language==="zh"?"仅前置门":"pre-GPU only"}</span></div><div><b>${historical.length}</b><span>${language==="zh"?"仅历史 Pilot":"historical pilot only"}</span></div></div><div class="terminal-experiment-callout"><b>${language==="zh"?"当前结论":"Current conclusion"}</b><span>${language==="zh"?"20/20 已进入 P0；其中原来的 16 个 P0-ready 已完成 admission 与设置冻结。当前仍只有 4 个方向有真实/历史 P0 执行证据；新进入的 16 个需要逐项过 execution preflight。":"All 20 active directions have entered P0; the former 16 P0-ready directions now have frozen admission/settings. Only four directions have real/historical P0 execution evidence; the 16 newly admitted directions must clear execution preflight."}</span></div><div class="advisor-table-scroll"><table class="matrix terminal-experiment-table"><thead><tr><th>${language==="zh"?"方向":"Direction"}</th><th>${language==="zh"?"终态":"Lifecycle"}</th><th>${language==="zh"?"实验状态":"Experiment status"}</th><th>${language==="zh"?"真实证据 / 当前事实":"Evidence / current fact"}</th><th>${language==="zh"?"下一门":"Next gate"}</th></tr></thead><tbody>${body}</tbody></table></div></section>`;
}
function renderP0AdmissionSettingsPanel(){
  const state=p0AdmissionState(), cards=state.cards||[], summary=state.summary||{};
  if(!cards.length) return "";
  const rows=cards.filter(c=>String(c.p0_entry?.date||"")==="2026-08-11").map(c=>{
    const s=c.setup||{}, p=c.execution_preflight||{}, pre=p.pre_p0||{}, outer=p.pre_experiment||{}, g=p.gpu0||{};
    const blockers=(p.blockers||[]).join(" · ")||"--";
    return `<tr><td><strong>${esc(c.code||"")}</strong><small>${esc(c.idea_id||"")}</small></td><td><b>${esc(s.mode||"--")}</b><span>${esc(s.primary_substrate||"--")}</span></td><td>${s.screening_units||0} units · seed ${s.seed||42}<br>≤${s.max_gpus||1} GPU · ≤${s.gpu_hours_cap||12} GPUh · ≤${s.wall_hours_cap||12}h</td><td>Offline ${esc(g.offline||"--")} · Reality ${esc(g.reality||"--")} · Phenomenon ${esc(g.phenomenon||"--")}</td><td>Pre-P0 ${pre.passed||0}/${pre.total||10}<br>Outer Gate ${outer.passed||0}/${outer.total||8}</td><td><span class="experiment-status-badge status-${p.execution_authorized?"pass":"planned"}">${p.execution_authorized?"AUTHORIZED":"LOCKED"}</span><small>${esc(blockers)}</small></td></tr>`;
  }).join("");
  return `<section class="panel p0-admission-panel" id="p0-admission-settings"><div class="idea-panel-heading"><div><h3 data-toc="false">${language==="zh"?"16 个新 P0 的冻结设置与启动门禁":"Frozen settings and launch gates for the 16 newly admitted P0s"}</h3><p class="section-intro">${language==="zh"?"P0 admission 只确认研究对象与最小实验已经冻结；execution_authorized 仍必须逐项通过 GPU-0、Pre-P0 10 项、Updater Competence、Pre-Experiment 8 Gate 和 runtime/throughput。这里直接显示本轮补全的执行设置和剩余 blocker。":"P0 admission freezes the research object and minimum experiment only. execution_authorized still requires GPU-0, all ten Pre-P0 checks, updater competence, all eight Pre-Experiment gates, and runtime/throughput. This table shows the completed settings and remaining blockers."}</p></div><strong>${summary.settings_complete||0}/20<span>${language==="zh"?"设置完整":"settings complete"}</span></strong></div><div class="terminal-experiment-stats"><div><b>${summary.active_p0||0}</b><span>P0</span></div><div><b>${summary.transitioned_from_p0_ready||0}</b><span>${language==="zh"?"本轮迁入":"transitioned"}</span></div><div><b>${summary.admitted||0}</b><span>admitted</span></div><div><b>${summary.settings_complete||0}</b><span>${language==="zh"?"设置完整":"settings complete"}</span></div><div><b>${summary.execution_authorized||0}</b><span>execution authorized</span></div><div><b>${summary.execution_blocked_or_pending||0}</b><span>${language==="zh"?"待启动门":"launch-gated"}</span></div></div><div class="advisor-table-scroll"><table class="matrix p0-admission-table"><thead><tr><th>Idea</th><th>${language==="zh"?"P0 模式 / 第一基座":"P0 mode / first substrate"}</th><th>${language==="zh"?"冻结预算":"Frozen budget"}</th><th>GPU-0</th><th>${language==="zh"?"可识别性 / 8 Gate":"Identifiability / 8 Gates"}</th><th>${language==="zh"?"执行锁":"Execution lock"}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}
function renderTerminalUnstartedAuditPanel(){
  const rows=terminalExperimentRows().map(row=>({...row,experiment:terminalExperimentEvidence(row)})).filter(row=>String(p0AdmissionCard(row.id)?.p0_entry?.date||"")==="2026-08-11");
  if(!rows.length) return "";
  const p0=rows.filter(x=>x.terminal.terminal_state==="p0").length, ready=rows.filter(x=>x.terminal.terminal_state==="p0-ready").length;
  const items=rows.map((row,i)=>`<li class="terminal-audit-item audit-${esc(row.experiment.category)}"><span>${i+1}</span><div><a href="${terminalExperimentIdeaHref(row)}"><b>${esc(row.code||row.title)}</b><strong>${row.code?esc(row.title):esc(row.id)}</strong></a><small>${esc(row.id)} · ${esc(humanReviewStatusLabel(row.terminal.terminal_state))}</small><p>${esc(row.experiment.label)}。${esc(row.experiment.next||"--")}</p></div></li>`).join("");
  return `<section class="panel terminal-audit-queue" id="terminal-unstarted-audit"><div class="idea-panel-heading"><div><h3 data-toc="false">${language==="zh"?"本轮新进入 P0 的 16 个方向启动审计":"Launch audit for the 16 newly admitted P0 directions"}</h3><p class="section-intro">${language==="zh"?"这 16 个方向已经不是 P0-ready，而是正式 P0；本表专门审它们的 execution preflight。点击可回到 Paper Ideas 核对完整方法、最强对照、独立真值、Pre-P0 和 Stop。":"These 16 directions are now formal P0 rather than P0-ready; this table audits their execution preflight. Open each item to check the frozen method, baseline, independent truth, Pre-P0 contract, and stop rule."}</p></div><strong>${rows.length}<span>${language==="zh"?"待审计":"to audit"}</span></strong></div><div class="terminal-audit-split"><span><b>${p0}</b>P0 ${language==="zh"?"未启动":"not started"}</span><span><b>${ready}</b>P0-ready ${language==="zh"?"未启动":"not started"}</span></div><ol class="terminal-audit-list">${items}</ol></section>`;
}
function renderLegacyExperimentArchive(content,titleZh,titleEn,noteZh,noteEn){
  if(!content) return "";
  return `<details class="panel experiment-legacy-archive"><summary><div><b>${language==="zh"?titleZh:titleEn}</b><small>${language==="zh"?noteZh:noteEn}</small></div><span>${language==="zh"?"追溯":"traceability"}</span></summary><div class="experiment-legacy-body">${content}</div></details>`;
}
