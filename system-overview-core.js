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
      <div class="system-hero-copy"><span class="system-kicker">${pick("科研到论文的统一流程","RESEARCH-TO-PAPER WORKFLOW")}</span><h3>${pick("整套系统依次回答五个问题：问题重要吗？Insight 新在哪里？最小方法够不够？实验能判清吗？最终文字是否和证据完全一致？","The system answers five questions in order: is the problem important, where is the new insight, is a minimal intervention sufficient, can the experiment decide it, and does the final manuscript exactly match the evidence?")}</h3><p>${pick("当前主线是：从第一手论文和真实实验里寻找重要但没有解释清楚的问题；把贡献拆成 Problem / Phenomenon / Insight / Mechanism / Method / Evaluation / Theory / System 分别做 closest-work 与简化归因；先试最小充分干预，再运行最便宜的决定性实验；证据冻结以后才构造论文，并先核查事实、引用、数字、表格和 claim，再交给独立审稿。","The current flow starts from important under-explained problems in primary papers or real experiments; attributes novelty separately across Problem / Phenomenon / Insight / Mechanism / Method / Evaluation / Theory / System; tries the minimum sufficient intervention before complex machinery; runs the cheapest decisive experiment; freezes the evidence; then audits facts, citations, numbers, tables, and claims before independent review.")}</p></div>
      <div class="system-stat-grid system-hero-stats">
        ${stat(get(architecture.reader_chapters,10),"个阅读章节","reader chapters")}
        ${stat(get(architecture.temporal_stages,21),"个后台阶段","backend stages")}
        ${stat(get(architecture.functional_layers,6),"个后端职责层","backend responsibility layers")}
        ${stat(get(architecture.assigned_components,running),"个已分配职责的后台组件","assigned components",get(architecture.unassigned_components,0)?"warn":"good")}
        ${stat(get(architecture.cross_cutting_controls,3),"个跨阶段检查规则","cross-cutting controls")}
        ${stat(get(architecture.unassigned_components,0),"个尚未分配职责的组件","unassigned components",get(architecture.unassigned_components,0)?"warn":"good")}
      </div>
    </section>
    <section class="system-principles system-section"><h3>${pick("六条最重要的工作规则","Six rules that every research run must follow")}</h3><p class="section-intro">${pick("不管换什么 Idea、模型或服务器，都先用这六条规则判断是否该继续。它们的目的很直接：少跑无效实验、避免把失败原因判断错、保证论文主张能追到真实证据。","These six rules apply regardless of the idea, model, or server. Their purpose is practical: avoid wasted runs, avoid misdiagnosing failures, and make every paper claim traceable to real evidence.")}</p><div class="system-principle-grid">
      ${principle(1,"先有证据，再写结论","Evidence before claims","论文说了什么就回到论文原文；实验数字来自哪次运行就保留对应日志和结果文件；不知道的地方直接写“不知道”，不能用模型猜测补齐。","Trace paper claims to the paper itself and experiment numbers to the exact run logs and result files. If something is unknown, keep it unknown rather than filling the gap with a model guess.")}
      ${principle(2,"先判断贡献新在哪一层，不把方法复杂度当贡献度","Attribute the contribution before judging method novelty","开始实现前先判断真正的新意属于问题、现象、Insight、机制、方法、评测、理论还是系统。简单 baseline 只会削弱它实际复现的那一层；如果它只复现了解法，但问题和 Insight 仍然没被已有工作解释，论文不能因此整篇 STOP。","Before implementation, identify whether novelty lives in the problem, phenomenon, insight, mechanism, method, evaluation, theory, or system. A simple baseline weakens only the layer it actually reproduces; reproducing the solution does not kill the whole paper when the problem or insight remains unmatched.")}
      ${principle(3,"优先找最小充分干预，再写实验蓝图","Prefer the minimum sufficient intervention","先问 rule、filter、constraint、reweight 或简单 control 能不能直接由 Insight 推出来；只有额外复杂度能产生新的可证伪预测时，才加入 learned module 或更复杂 controller。随后再固定最强基线和每条主张对应的实验。","First ask whether a rule, filter, constraint, reweighting, or simple control follows directly from the insight. Add a learned module or more complex controller only when the extra complexity creates a new falsifiable prediction, then freeze the strongest baseline and claim-to-experiment map.")}
      ${principle(4,"用 GPU 前先证明这个实验真的能回答问题","Prove the experiment can answer the question before GPU","先确认数据和环境能产生目标效应、最强基线公平、真值独立、样本量足够，而且实验无论成功或失败都会改变下一步。否则先修设计，不先跑大模型。","Before GPU use, confirm that the data/environment can realize the target effect, the strongest baseline is fair, truth is independent, the sample size is sufficient, and either outcome would change the next step. Otherwise fix the design first.")}
      ${principle(5,"实验失败时先判断到底什么失败了","Diagnose what failed before rejecting the idea","可能是运行或实验设计出了问题，也可能是方法没有实现好、指标没有真正测到想验证的原理、适用范围需要收缩，最后才可能是核心科学预测被可靠反驳。这些结论必须分开，不能把一次实验没过直接写成“科学想法失败”。","Execution failure, non-identifiable design, inadequate optimization, a metric/representation that does not instantiate the principle, a method realization that loses to a fair baseline, a narrower scope, and a reliable contradiction of the core prediction are seven distinct outcomes. The first six cannot be translated directly into 'the scientific idea is false.'")}
      ${principle(6,"方法稳定后才扩量，重要决定由人确认","Scale only after the method is stable; humans confirm major decisions","如果局部实验迫使核心方法改变，就重新检查新颖性和实验设计；只有方法版本固定后才跑全量实验。扩大预算、改变论文核心解释和最终投稿主张必须由人工负责人确认。","If local evidence changes the core method, recheck novelty and experiment design. Run full experiments only after the method version is fixed. Budget expansion, changes to the paper's core interpretation, and final submission claims require human confirmation.")}
    </div></section>`;
  };
})();
