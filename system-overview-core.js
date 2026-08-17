(() => {
  const pick = (zh, en) => language === "zh" ? zh : en;
  const get = (value, fallback = 0) => value === undefined || value === null ? fallback : value;
  const api = window.SYSTEM_OVERVIEW_SECTIONS = window.SYSTEM_OVERVIEW_SECTIONS || {};

  const stat = (value, zh, en, tone = "") => `<div class="system-stat ${tone}"><b>${esc(value)}</b><span>${pick(zh,en)}</span></div>`;
  const principle = (index, zhTitle, enTitle, zhBody, enBody) => `<article class="system-principle"><span>${String(index).padStart(2,"0")}</span><div><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4><p>${pick(zhBody,enBody)}</p></div></article>`;

  api.renderPurpose = function renderPurpose(state, s2) {
    const summary = state.summary || {};
    const architecture = state.system_architecture?.summary || {};
    const running = (state.components || []).filter((item) => item.status === "running").length;
    return `<section class="system-hero system-section">
      <div class="system-hero-copy"><span class="system-kicker">PAPER-FIRST RESEARCH OS</span><h3>${pick("后端只保留一个科研主逻辑：先设计一篇有 Novelty 的论文，再设计方法和实验，局部验证后冻结，最后做全量证据。","The backend now has one research logic: design a paper-worthy contribution first, then the method and experiments, validate locally, freeze, and only then collect full-scale evidence.")}</h3><p>${pick("Idea 生成、AI 会诊、P0、实验调度、失败诊断和系统记忆都不再是各自独立的流程，而是服务于同一条 Paper-first 生命周期。后端 Architecture Manifest 负责把每个组件归到唯一主责层，前端直接读取这份结构。","Idea generation, AI consultation, P0, experiment scheduling, failure diagnosis, and scientific memory are no longer separate workflows; each serves the same paper-first lifecycle. A backend Architecture Manifest assigns every component to one primary responsibility layer and the frontend reads that structure directly.")}</p></div>
      <div class="system-stat-grid system-hero-stats">
        ${stat(get(architecture.reader_chapters,7),"个阅读章节","reader chapters")}
        ${stat(get(architecture.temporal_stages,11),"个机器时间阶段","machine temporal stages")}
        ${stat(get(architecture.functional_layers,6),"个后端职责层","backend responsibility layers")}
        ${stat(get(architecture.assigned_components,running),"个已归责组件","assigned components",get(architecture.unassigned_components,0)?"warn":"good")}
        ${stat(get(architecture.cross_cutting_controls,3),"个横向方法学控制","cross-cutting controls")}
        ${stat(get(architecture.unassigned_components,0),"个未归责组件","unassigned components",get(architecture.unassigned_components,0)?"warn":"good")}
      </div>
    </section>
    <section class="system-principles system-section"><h3>${pick("系统最终保留的六条科研硬约束","Six final research invariants")}</h3><p class="section-intro">${pick("这些约束比某个具体 Idea、模型或实验批次更高层；任何新模块都必须服从它们。","These constraints sit above any individual idea, model, or experiment batch; every new module must obey them.")}</p><div class="system-principle-grid">
      ${principle(1,"证据先于主张","Evidence before claims","文献、最近邻、Baseline、Pilot 与失败结论都必须能回到真实来源；unknown 保持 unknown。","Literature, closest work, baselines, pilots, and failure claims remain traceable to real sources; unknown stays unknown.")}
      ${principle(2,"Novelty 先于实现","Novelty before implementation","先回答论文为什么值得发表、和 closest work 的不可约差异是什么；说不清贡献就不进入实现。","First establish why the paper is publishable and what is irreducibly different from the closest work; no clear contribution means no implementation.")}
      ${principle(3,"原理、方法和实验蓝图先于 Pilot","Principle, method, and blueprint before pilots","先冻结机制、方法组件、最强简化和 Claim→Experiment 关系；局部实验只能验证预注册风险，不能边跑边发明核心方法。","Freeze mechanism, method components, strongest simplification, and Claim→Experiment mapping first; local pilots test preregistered risks and never invent the core method on the fly.")}
      ${principle(4,"先证明值得且可辨识，再消耗 GPU","Economy and identifiability before GPU","先用最强简化、底座库存、causal unit、VOI、Protocol 与 8 Gate 判断最便宜决定性实验是否有资格启动。","Use strongest simplifications, substrate inventory, causal units, VOI, protocol checks, and eight gates to qualify the cheapest decisive test before GPU spend.")}
      ${principle(5,"负结果只更新被证据击中的那一层","Negative evidence updates only the affected layer","运行、实验设计、测量桥、方法实现、适用范围和核心原理分开判断；P0 没过不等于 Idea/原理自动失败。","Execution, design, measurement bridge, method realization, scope, and core principle are adjudicated separately; a failed P0 is not an automatic idea/principle failure.")}
      ${principle(6,"方法冻结后再扩量；运行可恢复，最终主张有人类门","Freeze before scale; recoverable runs and human claim authority","核心方法若因局部结果改变，就回到 Novelty/Method/Blueprint；全量实验只执行冻结方案，且预算扩张、原理解释和最终论文主张保留人工科学权限。","If local evidence changes the core method, return to Novelty/Method/Blueprint. Full experiments execute only frozen designs, while budget escalation, principle interpretation, and final paper claims remain under human scientific authority.")}
    </div></section>`;
  };
})();
