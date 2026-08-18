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
      <div class="system-hero-copy"><span class="system-kicker">${pick("PAPER-FIRST 科研操作系统","PAPER-FIRST RESEARCH OS")}</span><h3>${pick("整套系统只围绕一个问题推进：现在有没有一篇值得写、而且能用实验说清楚的论文？","The whole system advances one question: do we have a paper worth writing, with a claim that experiments can actually establish?")}</h3><p>${pick("实际顺序是：先从论文和已有实验找到一个具体问题，确认它没有被已有工作或简单解释覆盖；再写清论文贡献、方法和最强基线；然后只跑最便宜的决定性实验；证据稳定后才扩量。AI 评审、GPU 调度、失败诊断和历史记忆都只是这条主流程的辅助工具。","The actual order is: find a concrete problem from papers or prior experiments; verify that prior work or a simpler explanation does not already cover it; write down the paper claim, method, and strongest baseline; run only the cheapest decisive test; and scale only after the evidence is stable. AI review, GPU scheduling, failure diagnosis, and research memory are supporting tools for this one flow.")}</p></div>
      <div class="system-stat-grid system-hero-stats">
        ${stat(get(architecture.reader_chapters,7),"个阅读章节","reader chapters")}
        ${stat(get(architecture.temporal_stages,11),"个机器时间阶段","machine temporal stages")}
        ${stat(get(architecture.functional_layers,6),"个后端职责层","backend responsibility layers")}
        ${stat(get(architecture.assigned_components,running),"个已归责组件","assigned components",get(architecture.unassigned_components,0)?"warn":"good")}
        ${stat(get(architecture.cross_cutting_controls,3),"个横向方法学控制","cross-cutting controls")}
        ${stat(get(architecture.unassigned_components,0),"个未归责组件","unassigned components",get(architecture.unassigned_components,0)?"warn":"good")}
      </div>
    </section>
    <section class="system-principles system-section"><h3>${pick("六条最重要的工作规则","Six rules that every research run must follow")}</h3><p class="section-intro">${pick("不管换什么 Idea、模型或服务器，都先用这六条规则判断是否该继续。它们的目的很直接：少跑无效实验、避免把失败原因判断错、保证论文主张能追到真实证据。","These six rules apply regardless of the idea, model, or server. Their purpose is practical: avoid wasted runs, avoid misdiagnosing failures, and make every paper claim traceable to real evidence.")}</p><div class="system-principle-grid">
      ${principle(1,"先有证据，再写结论","Evidence before claims","论文说了什么就回到论文原文；实验数字来自哪次运行就保留对应日志和结果文件；不知道的地方直接写“不知道”，不能用模型猜测补齐。","Trace paper claims to the paper itself and experiment numbers to the exact run logs and result files. If something is unknown, keep it unknown rather than filling the gap with a model guess.")}
      ${principle(2,"先证明问题和贡献是新的，再写方法代码","Check novelty before implementation","开始实现前必须能用具体一句话回答：最接近的论文已经做了什么，我们还剩哪个没解决的问题，以及为什么这个差异值得单独写论文。答不出来就继续查文献或停止。","Before implementation, answer one concrete question: what did the closest paper already do, what exact problem remains unsolved, and why is that difference worth a paper? If the answer is unclear, search more or stop.")}
      ${principle(3,"跑实验前先写清要证明什么","Write the claim and comparison before the pilot","先固定核心机制、方法组件、最强简单基线和每条论文主张对应的实验。局部实验只能回答预先写好的问题，不能看到分数后不断改核心方法直到结果变好。","Fix the core mechanism, method components, strongest simple baseline, and the experiment for each claim. A pilot answers a preregistered question; it should not keep changing the core method until the score looks good.")}
      ${principle(4,"用 GPU 前先证明这个实验真的能回答问题","Prove the experiment can answer the question before GPU","先确认数据和环境能产生目标效应、最强基线公平、真值独立、样本量足够，而且实验无论成功或失败都会改变下一步。否则先修设计，不先跑大模型。","Before GPU use, confirm that the data/environment can realize the target effect, the strongest baseline is fair, truth is independent, the sample size is sufficient, and either outcome would change the next step. Otherwise fix the design first.")}
      ${principle(5,"实验失败时先判断到底什么失败了","Diagnose what failed before rejecting the idea","程序崩了、数据不够、指标测错、方法没实现出预期效果、只在更窄范围成立、核心科学预测被反驳，是六种不同结论。不能把前五种直接写成“科学想法失败”。","A crashed run, insufficient data, a wrong metric, an ineffective implementation, a narrower-than-expected scope, and a contradicted scientific prediction are different outcomes. Do not translate the first five into 'the scientific idea is false.'")}
      ${principle(6,"方法稳定后才扩量，重要决定由人确认","Scale only after the method is stable; humans confirm major decisions","如果局部实验迫使核心方法改变，就重新检查新颖性和实验设计；只有方法版本固定后才跑全量实验。扩大预算、改变论文核心解释和最终投稿主张必须由人工负责人确认。","If local evidence changes the core method, recheck novelty and experiment design. Run full experiments only after the method version is fixed. Budget expansion, changes to the paper's core interpretation, and final submission claims require human confirmation.")}
    </div></section>`;
  };
})();
