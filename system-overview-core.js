(() => {
  const pick = (zh, en) => language === "zh" ? zh : en;
  const get = (value, fallback = 0) => value === undefined || value === null ? fallback : value;
  const api = window.SYSTEM_OVERVIEW_SECTIONS = window.SYSTEM_OVERVIEW_SECTIONS || {};

  const stat = (value, zh, en, tone = "") => `<div class="system-stat ${tone}"><b>${esc(value)}</b><span>${pick(zh,en)}</span></div>`;
  const principle = (index, zhTitle, enTitle, zhBody, enBody) => `<article class="system-principle"><span>${String(index).padStart(2,"0")}</span><div><h4 data-toc="false">${pick(zhTitle,enTitle)}</h4><p>${pick(zhBody,enBody)}</p></div></article>`;

  api.renderPurpose = function renderPurpose(state, s2) {
    const summary = state.summary || {};
    const stats = s2.statistics || {};
    const pre = state.pre_p0_identifiability?.summary || {};
    const running = (state.components || []).filter((item) => item.status === "running").length;
    return `<section class="system-hero system-section">
      <div class="system-hero-copy"><span class="system-kicker">RESEARCH SYSTEM CONTRACT</span><h3>${pick("这套系统不是为了自动“产出更多 Idea”，而是为了让研究过程更可验证、更少浪费、更容易复盘。","The system is not optimized to produce more ideas. It is optimized to make research auditable, less wasteful, and easier to repair.")}</h3><p>${pick("核心对象是一条可重复的科研链：证据如何进入、一个科学问题何时值得实验、实验在什么条件下才有资格给出结论、失败如何分类，以及经验如何回流成下一轮的启动规则。","The primary object is a repeatable research loop: how evidence enters, when a question deserves an experiment, when a run is identifiable enough to support a conclusion, how failures are classified, and how lessons become launch rules for the next run.")}</p></div>
      <div class="system-stat-grid system-hero-stats">
        ${stat(get(summary.papers,stats.paper_count),"篇去重文献","deduplicated papers")}
        ${stat(get(summary.evidence_nodes),"个证据节点","evidence nodes")}
        ${stat(get(summary.evidence_edges),"条证据关系","evidence relations")}
        ${stat(running,"个核心组件运行中","core components running",running?"good":"warn")}
        ${stat(get(pre.audited,0),"个设计已做 Pre-P0 回放","designs audited by Pre-P0")}
        ${stat(get(pre.execution_ready,0),"个当前可直接启动 P0","currently launch-ready P0s",get(pre.execution_ready,0)?"good":"warn")}
      </div>
    </section>
    <section class="system-principles system-section"><h3>${pick("先读这五条：系统到底保证什么","Five guarantees to read first")}</h3><p class="section-intro">${pick("它们比具体模型、Benchmark 或某一轮实验更稳定，是整个后台的设计约束。","These constraints are more stable than any model, benchmark, or individual experiment.")}</p><div class="system-principle-grid">
      ${principle(1,"证据先于结论","Evidence before claims","文献、Baseline、Pilot 和失败证据必须能追到来源；unknown 保持 unknown。","Literature, baselines, pilots, and failures remain traceable to source; unknown stays unknown.")}
      ${principle(2,"先证明实验可辨识，再消耗 GPU","Identifiability before GPU spend","如果实验区分不了“方法有效”和“Base agent 根本不会”，就没有启动资格。","A run that cannot distinguish method effect from an incapable base agent is not launchable.")}
      ${principle(3,"小实验负责筛信号，不负责误杀方向","Screening finds signal; it does not kill a direction","Screening 只产生 signal / no-signal / inconclusive；正式 Go/Stop 需要 confirmatory evidence。","Screening produces signal, no-signal, or inconclusive; formal Go/Stop requires confirmatory evidence.")}
      ${principle(4,"运行过程本身必须可恢复","Runs must be recoverable","每个 episode/candidate 增量写盘，预算在线检查，中断后保留已完成证据。","Episodes and candidates persist incrementally, budgets are checked online, and completed evidence survives interruption.")}
      ${principle(5,"自动化执行，人工控制科学主张","Automate execution; keep claims under human control","系统可以自动检索、校验、调度和汇总，但研究范围、主张边界、扩预算与最终解释保留人工门。","The system may retrieve, validate, schedule, and aggregate automatically, while scope, claim boundaries, budget escalation, and final interpretation remain human gates.")}
    </div></section>`;
  };
})();
