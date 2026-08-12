(() => {
  const pick = (zh, en) => language === "zh" ? zh : en;
  const get = (value, fallback = 0) => value === undefined || value === null ? fallback : value;
  const api = window.SYSTEM_OVERVIEW_SECTIONS = window.SYSTEM_OVERVIEW_SECTIONS || {};

  const stat = (value, zh, en, tone = "") => `<div class="system-stat ${tone}"><b>${esc(value)}</b><span>${pick(zh,en)}</span></div>`;
  const principle = (index, zhTitle, enTitle, zhBody, enBody) => `<article class="system-principle"><span>${String(index).padStart(2,"0")}</span><div><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4><p>${pick(zhBody,enBody)}</p></div></article>`;

  api.renderPurpose = function renderPurpose(state, s2) {
    const summary = state.summary || {};
    const stats = s2.statistics || {};
    const economy = state.p0_economy_gate?.summary || {};
    const ledger = state.p0_decision_ledger?.summary || {};
    const ai = state.ai_consultation_automation?.summary || {};
    const running = (state.components || []).filter((item) => item.status === "running").length;
    return `<section class="system-hero system-section">
      <div class="system-hero-copy"><span class="system-kicker">RESEARCH SYSTEM CONTRACT</span><h3>${pick("这套系统不是为了自动“产出更多 Idea”，而是为了让研究过程更可验证、更少浪费、更容易复盘。","The system is not optimized to produce more ideas. It is optimized to make research auditable, less wasteful, and easier to repair.")}</h3><p>${pick("核心对象是一条可重复的科研链：证据如何进入、一个科学问题何时值得实验、实验在什么条件下才有资格给出结论、失败如何分类，以及经验如何回流成下一轮的启动规则。","The primary object is a repeatable research loop: how evidence enters, when a question deserves an experiment, when a run is identifiable enough to support a conclusion, how failures are classified, and how lessons become launch rules for the next run.")}</p></div>
      <div class="system-stat-grid system-hero-stats">
        ${stat(get(summary.papers,stats.paper_count),"篇去重文献","deduplicated papers")}
        ${stat(get(summary.evidence_nodes),"个证据节点","evidence nodes")}
        ${stat(get(summary.evidence_edges),"条证据关系","evidence relations")}
        ${stat(running,"个核心组件运行中","core components running",running?"good":"warn")}
        ${stat(get(summary.p0_admission_active,0),"个 active P0 生命周期方向","active P0 lifecycle directions")}
        ${stat(get(economy.economy_ready,0),"个 Economy-ready","currently Economy-ready",get(economy.economy_ready,0)?"good":"warn")}
        ${stat(get(ledger.experiment_stopped,0),"个实验 STOP 待人工","experiment STOPs awaiting review")}
        ${stat(get(ai.unresolved_high_risk,0),"个未处置 AI 高风险","unresolved AI high-risk",get(ai.unresolved_high_risk,0)?"warn":"good")}
      </div>
    </section>
    <section class="system-principles system-section"><h3>${pick("先读这六条：系统到底保证什么","Six guarantees to read first")}</h3><p class="section-intro">${pick("它们比具体模型、Benchmark 或某一轮实验更稳定，是整个后台的设计约束。","These constraints are more stable than any model, benchmark, or individual experiment.")}</p><div class="system-principle-grid">
      ${principle(1,"证据先于结论","Evidence before claims","文献、Baseline、Pilot 和失败证据必须能追到来源；unknown 保持 unknown。","Literature, baselines, pilots, and failures remain traceable to source; unknown stays unknown.")}
      ${principle(2,"原理先于实验","Principle before experiment","先冻结原语、假设、机制、适用范围、可观测预测和真正反证条件；实验只是检验这条证据链的接口，不是一张对 Idea 投 PASS/FAIL 的票。","Freeze primitives, assumptions, mechanism, scope, observable predictions, and genuine falsifiers first; an experiment is an evidence interface, not a PASS/FAIL vote on an idea.")}
      ${principle(3,"先证明实验可辨识，再消耗 GPU","Identifiability before GPU spend","如果实验区分不了“方法有效”和“Base agent 根本不会”，就没有启动资格。","A run that cannot distinguish method effect from an incapable base agent is not launchable.")}
      ${principle(4,"负结果先定位更新哪一层","Negative evidence updates a layer, not everything","运行、实验设计、测量桥、方法实现、适用范围和核心机制是不同层；只有预注册原理预测在全部前置条件成立时被稳定反驳，才允许原理级 falsification。","Execution, design, operationalization, method realization, scope, and core mechanism are distinct layers; principle falsification requires a registered prediction contradicted with every prerequisite intact.")}
      ${principle(5,"小实验负责筛信号，不负责误杀方向","Screening finds signal; it does not kill a direction","Screening 只产生 signal / no-signal / inconclusive；正式方法结论仍需要 confirmatory evidence。","Screening produces signal, no-signal, or inconclusive; formal method conclusions require confirmatory evidence.")}
      ${principle(6,"运行可恢复，科学主张有人类门","Recoverable runs; human-controlled claims","实验增量落盘、预算在线检查；自动化可以执行检索、校验、调度和汇总，但主张边界、扩预算与最终原理解释保留人工门。","Runs persist incrementally with online budget checks; automation may retrieve, validate, schedule, and aggregate, while claim boundaries, budget escalation, and final principle interpretation remain human gates.")}
    </div></section>`;
  };
})();
