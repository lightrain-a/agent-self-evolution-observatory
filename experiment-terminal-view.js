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
  const {id,terminal}=row, lifecycle=terminal.terminal_state||"p0-ready";
  const iteration=(experimentIterationState().nodes||[]).find(x=>x.idea_id===id)||null;
  const runtime=p0RuntimeExecutions().find(x=>x.idea_id===id)||null;
  const phase=experimentPilotPhase(id,"P0");
  const preGpu=(preGpuCandidateGateState().candidates||[]).find(x=>x.idea_id===id)||null;
  const mem=window.RESEARCH_SYSTEM_STATE?.mem_xfer_workflow||{};
  if(["replicated-effect-memory-gate","cross-task-effect-transport-certificate"].includes(id)){
    const support=mem.support_qualification||{}, progress=support.progress||{}, decision=support.decision||{};
    return {current_started:true,category:"started",tone:String(support.status||"").includes("pass")?"pass":"running",label:language==="zh"?`共享 P0 已开始 · ${String(support.status||"running").toUpperCase()}`:`Shared P0 started · ${String(support.status||"running").toUpperCase()}`,detail:textOf(terminal.current_fact||{})||`${progress.completed_episodes||0}/${progress.total_episodes||0} executions`,next:decision.next_action||(language==="zh"?"按冻结 support gate 继续；第二 backbone 仍 HOLD。":"Continue only under the frozen support gate; second backbone remains on HOLD."),evidence:`${progress.completed_episodes||0}/${progress.total_episodes||0} executions · ${progress.completed_units||0}/${progress.total_units||0} units · ${progress.model_calls||0} calls`};
  }
  const runtimeStatus=String(runtime?.status||"").toLowerCase();
  const registryStarted=!!phase?.result||Boolean(phase?.status&&phase.status!=="planned");
  const runtimeStarted=["running","collected","registered","failed"].includes(runtimeStatus);
  if(lifecycle==="p0"||registryStarted||runtimeStarted){
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
  return {current_started:false,category:"not-started",tone:"planned",label:language==="zh"?"当前冻结 P0 尚未启动":"Current frozen P0 not started",detail:textOf(terminal.terminal_reason||{})||(language==="zh"?"已完成方法终态化，但没有真实 P0 执行 artifact。":"Method is terminalized, but no real P0 execution artifact is registered."),next:textOf(terminal.pre_p0_gate||{})||textOf(terminal.minimum_p0||{})||(language==="zh"?"先审计 Pre-P0 合同，再决定是否启动。":"Audit the Pre-P0 contract before launch."),evidence:language==="zh"?"无真实 P0 execution artifact":"No real P0 execution artifact"};
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
  return `<section class="panel terminal-experiment-portfolio" id="terminal-experiment-portfolio"><div class="idea-panel-heading"><div><div class="eyebrow">H1 → EXPERIMENT · 2026-08-11</div><h2 data-toc="false">${language==="zh"?"与 Paper Ideas 对齐的 20 个活跃方向实验总表":"Experiment status for the 20 active Paper Ideas"}</h2><p class="section-intro">${language==="zh"?"以 human terminal ledger 为唯一方向清单：2 个 parent P0 + 11 个 parent P0-ready + 2 个独立 P0 + 5 个独立 P0-ready。旧 P0 计划、被合并 parent、被吸收 child 和历史诊断不再冒充当前独立实验队列。‘已开始’只指当前方向已有真实 P0/Pilot 执行证据；GPU 前置门或旧机制 Pilot 单独标记。":"The human terminal ledger is the only active-direction list: 2 parent P0 + 11 parent P0-ready + 2 standalone P0 + 5 standalone P0-ready. Legacy plans, merged parents, absorbed children, and historical diagnostics are traceability only. ‘Started’ requires real P0/Pilot execution evidence for the current direction."}</p></div><strong>${started.length}/20<span>${language==="zh"?"当前 P0 已开始":"current P0 started"}</span></strong></div><div class="terminal-experiment-stats"><div><b>${p0.length}</b><span>P0</span></div><div><b>${ready.length}</b><span>P0-ready</span></div><div class="stat-started"><b>${started.length}</b><span>${language==="zh"?"当前实验已开始":"current experiments started"}</span></div><div class="stat-pending"><b>${pending.length}</b><span>${language==="zh"?"当前 P0 未启动":"current P0 not started"}</span></div><div><b>${pre.length}</b><span>${language==="zh"?"仅前置门":"pre-GPU only"}</span></div><div><b>${historical.length}</b><span>${language==="zh"?"仅历史 Pilot":"historical pilot only"}</span></div></div><div class="terminal-experiment-callout"><b>${language==="zh"?"当前结论":"Current conclusion"}</b><span>${language==="zh"?"4 个 P0 都已经进入实验生命周期；16 个 P0-ready 的当前冻结 P0 尚未启动。下一轮主要审计这 16 个 P0-ready。":"All four P0 directions have entered the experiment lifecycle; the current frozen P0 has not started for the 16 P0-ready directions. Those 16 are the next audit queue."}</span></div><div class="advisor-table-scroll"><table class="matrix terminal-experiment-table"><thead><tr><th>${language==="zh"?"方向":"Direction"}</th><th>${language==="zh"?"终态":"Lifecycle"}</th><th>${language==="zh"?"实验状态":"Experiment status"}</th><th>${language==="zh"?"真实证据 / 当前事实":"Evidence / current fact"}</th><th>${language==="zh"?"下一门":"Next gate"}</th></tr></thead><tbody>${body}</tbody></table></div></section>`;
}
function renderTerminalUnstartedAuditPanel(){
  const rows=terminalExperimentRows().map(row=>({...row,experiment:terminalExperimentEvidence(row)})).filter(row=>!row.experiment.current_started);
  if(!rows.length) return "";
  const p0=rows.filter(x=>x.terminal.terminal_state==="p0").length, ready=rows.filter(x=>x.terminal.terminal_state==="p0-ready").length;
  const items=rows.map((row,i)=>`<li class="terminal-audit-item audit-${esc(row.experiment.category)}"><span>${i+1}</span><div><a href="${terminalExperimentIdeaHref(row)}"><b>${esc(row.code||row.title)}</b><strong>${row.code?esc(row.title):esc(row.id)}</strong></a><small>${esc(row.id)} · ${esc(humanReviewStatusLabel(row.terminal.terminal_state))}</small><p>${esc(row.experiment.label)}。${esc(row.experiment.next||"--")}</p></div></li>`).join("");
  return `<section class="panel terminal-audit-queue" id="terminal-unstarted-audit"><div class="idea-panel-heading"><div><h3 data-toc="false">${language==="zh"?"你下一轮要审计的未启动 P0 / P0-ready":"Unstarted P0 / P0-ready directions for the next audit"}</h3><p class="section-intro">${language==="zh"?"按当前冻结方法判断，不把旧机制 Pilot 或 GPU 前置门算成‘已经开始 P0’。点击可回到 Paper Ideas 审完整方法、最强对照、Pre-P0 门和 Stop 条件。":"This uses the current frozen mechanism; old-mechanism pilots and pre-GPU gates do not count as a started P0. Open each item to audit its method, baseline, Pre-P0 gate, and stop condition."}</p></div><strong>${rows.length}<span>${language==="zh"?"待审计":"to audit"}</span></strong></div><div class="terminal-audit-split"><span><b>${p0}</b>P0 ${language==="zh"?"未启动":"not started"}</span><span><b>${ready}</b>P0-ready ${language==="zh"?"未启动":"not started"}</span></div><ol class="terminal-audit-list">${items}</ol></section>`;
}
function renderLegacyExperimentArchive(content,titleZh,titleEn,noteZh,noteEn){
  if(!content) return "";
  return `<details class="panel experiment-legacy-archive"><summary><div><b>${language==="zh"?titleZh:titleEn}</b><small>${language==="zh"?noteZh:noteEn}</small></div><span>${language==="zh"?"追溯":"traceability"}</span></summary><div class="experiment-legacy-body">${content}</div></details>`;
}
