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
    return `<section class="preflight-outer system-section"><div class="preflight-heading"><div><span class="system-kicker">LOCAL VALIDATION SUB-MACHINE · P0-SYSTEM v2</span><h3>${pick("这是 11 步 Paper-first 主流程中的科学验证子状态机","This is the scientific-validation sub-machine inside the 11-stage paper-first lifecycle")}</h3><p>${pick("Problem → Substrate → F0 → P0-Support → P0-Method → P1 → Paper 只负责实验/证据状态，不负责重新定义论文 Novelty 或核心方法。Support 不足只能返回 SUPPORT_INSUFFICIENT；正式方法实验必须读取冻结的 Support PASS。","Problem → Substrate → F0 → P0-Support → P0-Method → P1 → Paper governs experiment/evidence state only; it does not redefine paper novelty or the core method. Insufficient support returns SUPPORT_INSUFFICIENT, and formal method work requires a frozen Support PASS.")}</p></div><div class="preflight-lock"><b>${(gov.stages || fallbackStages).length}</b><span>${pick("验证子阶段","validation sub-stages")}</span></div></div><div class="governance-stage-grid">${stages}</div>
    <div class="preflight-card-grid"><div><span>REPAIR BUDGET</span><b>${Number(policy.max_representation_or_objective_repairs_per_substrate || 2)}</b><p>${pick("同一 substrate 最多两次 representation/objective 级修复；之后必须换 substrate、合并或停止。","At most two representation/objective repairs per substrate; then change substrate, merge, or stop.")}</p></div><div><span>PRE-MODEL LOAD</span><b>REQUIRED</b><p>${pick("加载模型前检查代码、配置、数据、模型身份、依赖和输出目录。","Verify code, config, data, model identity, dependencies, and output directory before model load.")}</p></div><div><span>RAW TRACE</span><b>MANDATORY</b><p>${pick("一次保存 observation / action / raw choice；Trace 不完整不得登记科学结果。","Persist observations/actions/raw choices once; incomplete traces cannot become scientific results.")}</p></div><div><span>GPU LEASE</span><b>${runtime.active_gpu_leases || 0} ${pick("活跃","active")}</b><p>${pick("Idea authority 与 GPU UUID 分离租约，避免多窗口互相抢卡或杀进程。","Separate idea authority and GPU UUID leases prevent cross-window resource conflicts.")}</p></div></div>
    <div class="system-retro-note"><b>${pick("Typed outcomes：","Typed outcomes:")}</b> ${failureTags.map(key=>`<code>${esc(key)}</code>`).join(" · ")}</div></section>`;
  };
})();
