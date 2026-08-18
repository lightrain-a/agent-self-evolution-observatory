(() => {
  const pick = (zh,en) => language === "zh" ? zh : en;
  const api = window.SYSTEM_OVERVIEW_SECTIONS = window.SYSTEM_OVERVIEW_SECTIONS || {};
  const fallbackStages = ["problem","substrate","f0-identifiability","p0-support","p0-method","p1-replication","paper-experiment"];
  const labels = {
    problem:["问题门","Problem Gate"], substrate:["实验底座资格","Substrate Qualification"],
    "f0-identifiability":["F0 · 离线可辨识性","F0 · Offline Identifiability"],
    "p0-support":["P0-S · 现象支持","P0-S · Support"], "p0-method":["P0-M · 方法实验","P0-M · Method"],
    "p1-replication":["P1 · 复现","P1 · Replication"], "paper-experiment":["论文实验","Paper Experiment"]
  };
  const stageCard = (row,index) => {
    const key = row.key || fallbackStages[index];
    const title = labels[key] || [key,key];
    const note = key === "p0-support" ? pick("只判断现象；不能 METHOD-FAIL","Phenomenon only; no METHOD-FAIL") : key === "p0-method" ? pick("必须有冻结 Support PASS","Requires frozen Support PASS") : "GATED";
    return `<div class="governance-stage-card"><span>${index+1}</span><div><b>${pick(title[0],title[1])}</b><small>${esc(key)}</small></div><em>${note}</em></div>`;
  };
  api.renderGovernanceV2 = function renderGovernanceV2(state) {
    const gov = state.research_governance_v2 || window.RESEARCH_GOVERNANCE_V2 || {};
    const policy = gov.policy || {};
    const runtime = gov.runtime || {};
    const stages = (gov.stages || fallbackStages.map((key,index)=>({key,index}))).map(stageCard).join("");
    const failures = gov.failure_classes || {};
    const failureTags = Object.keys(failures).length ? Object.keys(failures) : ["FAIL_SUBSTRATE","FAIL_TARGET_DEGENERACY","FAIL_REPRESENTATION","SUPPORT_INSUFFICIENT","METHOD_FAIL","IMPLEMENTATION_ERROR","RUNTIME_ERROR","PROVENANCE_INCONCLUSIVE"];
    return `<section class="preflight-outer system-section"><div class="preflight-heading"><div><span class="system-kicker">LOCAL VALIDATION SUB-MACHINE · P0-SYSTEM v2</span><h3>${pick("小规模验证要分两步：先确认现象真的存在，再比较方法是否更好","Local validation has two jobs: first confirm the phenomenon, then test whether the method is better")}</h3><p>${pick("系统不会因为一个小实验失败就直接判定论文 Idea 错了。先检查当前数据和环境能不能产生要研究的效应；现象证据足够后，才允许比较本文方法和最强基线。数据不足就记录“证据不足”，方法确实输给公平基线时才记录“方法失败”。","A failed local run does not automatically invalidate the paper idea. First check whether the current data and environment can realize the effect being studied. Only after the phenomenon has enough support may the proposed method be compared with the strongest baseline. Missing evidence is recorded as insufficient support; method failure is reserved for a fair comparison that actually loses.")}</p></div><div class="preflight-lock"><b>${(gov.stages || fallbackStages).length}</b><span>${pick("验证子阶段","validation sub-stages")}</span></div></div><div class="governance-stage-grid">${stages}</div>
    <div class="preflight-card-grid"><div><span>${pick("同一设置最多修几次","REPAIR LIMIT")}</span><b>${Number(policy.max_representation_or_objective_repairs_per_substrate || 2)}</b><p>${pick("同一批数据和同一实验环境里，关键表示或目标最多修两次。第三次还想继续，就必须说明换了新的数据/环境、并入别的方向，或停止当前方案，避免无限调参救旧 Idea。","On the same data and environment, at most two load-bearing representation/objective repairs are allowed. A third attempt must use a materially new setup, merge into another direction, or stop the current formulation rather than endlessly tuning it.")}</p></div><div><span>${pick("模型启动前检查","BEFORE MODEL LOAD")}</span><b>${pick("必须","REQUIRED")}</b><p>${pick("先确认代码版本、配置、数据、模型身份、依赖和输出目录都对，再加载模型，避免把环境错误误当成科研结果。","Verify code version, configuration, data, model identity, dependencies, and output directory before loading the model so environment mistakes are not mistaken for scientific results.")}</p></div><div><span>${pick("保存原始轨迹","SAVE RAW TRACE")}</span><b>${pick("必须","MANDATORY")}</b><p>${pick("观测、动作和模型原始选择必须原样保存。缺少这些记录时，后续无法判断错误来自模型、环境还是分析，因此不能登记正式科学结论。","Observations, actions, and raw model choices must be saved. Without them, later analysis cannot distinguish model, environment, and analysis errors, so the run cannot support a formal scientific conclusion.")}</p></div><div><span>${pick("GPU 独占记录","GPU OWNERSHIP")}</span><b>${runtime.active_gpu_leases || 0} ${pick("张卡正在使用","active")}</b><p>${pick("每张 GPU 在同一时间只属于一个运行任务；实验权限和 GPU 占用分别记录，避免多个窗口互相抢卡或误杀别人的进程。","Each GPU belongs to one run at a time. Scientific run approval and GPU occupancy are tracked separately to prevent parallel sessions from stealing a device or killing another run.")}</p></div></div>
    <div class="system-retro-note"><b>${pick("失败必须说明具体是哪一类：","Every failure must name the concrete cause:")}</b> ${failureTags.map(key=>`<code>${esc(key)}</code>`).join(" · ")}</div></section>`;
  };
})();
