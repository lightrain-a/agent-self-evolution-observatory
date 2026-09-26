/* Planning visibility only. Never interpret a complete card as scientific PASS. */
(() => {
  const escape = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  window.renderDiscoveryMethodFormation = function (lang = "en") {
    const state = window.DISCOVERY_METHOD_FORMATION;
    if (!state) return "";
    const pick = (zh, en) => lang === "zh" ? zh : en;
    const count = value => Number.isFinite(Number(value)) ? Math.max(0, Math.floor(Number(value))) : 0;
    const summary = state.summary || {};
    const steps = lang === "zh"
      ? ["已有系统与文献", "已审计异常", "结构化类比", "竞争假设", "最低成本区分实验", "限定范围的证据判断", "最小方法", "冻结与前瞻验证", "主张—证据闭合"]
      : state.workflow || [];
    const rows = (state.rows || []).slice(0, 30).map(row => `<tr><td>${escape(row.candidate_id)}</td><td>${pick(row.planning_status === "PLAN_FIELDS_COMPLETE" ? "计划字段齐全，尚未验证" : "需要补计划或来源", row.planning_status === "PLAN_FIELDS_COMPLETE" ? "Plan fields complete; unverified" : "Plan or sources missing")}</td><td>${count(row.analogies)} / ${count(row.hypotheses)}</td><td>${escape((row.missing || []).join(", ") || pick("仍需独立语义审核和执行授权", "Independent semantic review and execution authorization still required"))}</td></tr>`).join("");
    return `<details id="discovery-method-formation" class="canonical-related-bank discovery-formation-panel">
      <summary><div><b>${pick("Idea 发现 → 方法形成", "Idea discovery → method formation")}</b><span>${pick("类比、竞争假设、区分性实验；不替代导师判断", "Analogies, competing hypotheses and discriminating tests; human judgment remains external")}</span></div><strong>${count(summary.plans_complete)} / ${count(summary.candidates)}</strong></summary>
      <div class="discovery-formation-body">
        <p>${pick("数字表示工作卡字段完整度，不是科研通过率。旧候选缺少新字段时只提示补充，不撤销或升级原有裁决。", "Counts describe planning completeness, not scientific acceptance. Missing fields on old candidates do not revoke or promote existing decisions.")}</p>
        <div class="discovery-formation-flow">${steps.map((step, i) => `<span><small>${String(i + 1).padStart(2, "0")}</small>${escape(step)}</span>`).join("")}</div>
        <div class="discovery-formation-notes"><section><h3>${pick("类比必须说明哪里不成立", "State where an analogy breaks")}</h3><p>${pick("逐项映射对象、更新、反馈、选择、部署变化和预算。神经网络的权重平均不能直接等同于文本 Skill 合并。", "Map the object, update, feedback, selection, deployment shift and budget. Weight averaging does not directly justify merging textual Skills.")}</p></section><section><h3>${pick("实验必须能区分不同解释", "Require different predictions")}</h3><p>${pick("保留主假设与替代解释，明确对照、数据身份、调用预算、时间估计以及不确定和技术失败的处理。", "Keep a leading explanation and alternatives; specify controls, data identity, call/time estimates, inconclusive outcomes and execution failures.")}</p></section></div>
        ${rows ? `<div class="discovery-formation-table"><table><thead><tr><th>ID</th><th>${pick("当前计划状态", "Planning status")}</th><th>${pick("类比 / 假设", "Analogies / hypotheses")}</th><th>${pick("待补字段", "Missing fields")}</th></tr></thead><tbody>${rows}</tbody></table></div>` : `<p>${pick("当前发布的生成器没有候选可编译。本次已安装流程与检查器，没有虚构新 Idea，也没有启动模型调用或实验。", "The published generator currently has no candidates to compile. The workflow and auditor are installed; no ideas, provider calls or experiment results were invented.")}</p>`}
        <p>${pick("生成的假设统一标记为“待验证”；真实结果继续由现有实验记录、限定范围的失败记忆和科学门控处理。人类咨询独立保留。", "Generated hypotheses remain proposed. Actual results stay with the existing experiment records, scoped failure memory and scientific gates. Human consultation remains separate.")}</p>
        <a class="link-btn" href="https://github.com/lightrain-a/agent-self-evolution-observatory/blob/main/docs/heirs-discovery-methodology.md">${pick("查看完整方法论、组件核对与接入说明 →", "Methodology, component audit and integration notes →")}</a>
      </div></details>`;
  };
})();
