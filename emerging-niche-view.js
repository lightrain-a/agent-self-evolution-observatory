(() => {
  const allowed = new Set(["paper-ideas", "system-overview"]);
  if (!allowed.has(document.body.dataset.page || "")) return;

  function text(row, zh) { return zh ? (row.zh || row.en || "") : (row.en || row.zh || ""); }
  function renderEmergingNichePolicy() {
    const root = document.getElementById("dynamic-page");
    const policy = window.EMERGING_NICHE_POLICY;
    if (!root || !policy || document.getElementById("emerging-niche-score")) return;
    const zh = (document.documentElement.lang || "").toLowerCase().startsWith("zh") || localStorage.getItem("agent-evolution-language") === "zh";
    const labels = zh ? {
      kicker:"研究方向准入 · ENS 0–100", title:"新兴小众方向评分（Emerging-Niche Score）",
      intro:"用于决定哪些新候选优先接受最新文献碰撞审计和低成本 P0；它不是“通过分”，也不会推翻真实实验或人工终态。",
      weight:"权重", hard:"硬规则", bands:"解释", rule:"单纯冷门不加分：必须同时有新兴邻域、真实重要性和决定性 P0。",
      override:"直接碰撞、等信息简化、真实 P0 停止（STOP）和人工并入/弃掉（MERGE/DROP）永远覆盖 ENS。"
    } : {
      kicker:"IDEA GATE · ENS 0–100", title:"Emerging-Niche Score",
      intro:"Prioritizes which new candidates receive fresh collision audits and cheap P0s first. It is not a PASS score and cannot override experiments or human terminal decisions.",
      weight:"Weight", hard:"Hard rule", bands:"Interpretation", rule:"Rarity alone earns nothing: a forming neighborhood, real importance, and a decisive P0 are all required.",
      override:"Direct collision, matched simplification, real P0 STOP, and human MERGE/DROP always override ENS."
    };
    const keyZh={exact_problem_sparsity:"问题稀疏度",emerging_signal:"新兴信号",collision_margin:"碰撞余量",decisive_p0:"决定性 P0",importance_floor:"重要性底线"};
    const components = Object.entries(policy.components || {}).map(([key,row]) => `<article><span>${Math.round(Number(row.weight || 0)*100)}%</span><div><b>${text(row,zh)}</b><small>${zh?(keyZh[key]||key):key}</small></div></article>`).join("");
    const bands = (policy.bands || []).map(row => `<span><b>${row.min}+</b> ${text(row,zh)}</span>`).join("");
    const panel = document.createElement("section");
    panel.id = "emerging-niche-score";
    panel.className = "panel emerging-niche-panel";
    panel.innerHTML = `<div class="idea-panel-heading"><div><div class="eyebrow">${labels.kicker}</div><h2 data-toc="false">${labels.title}</h2><p class="section-intro">${labels.intro}</p></div><strong>${zh ? "新兴小众评分 ENS" : "ENS"}</strong></div><div class="reviewer-gate-grid">${components}</div><div class="idea-board-warning"><b>${labels.hard}:</b> ${labels.rule}</div><div class="idea-board-warning"><b>${labels.hard}:</b> ${labels.override}</div><div class="idea-board-filters"><b>${labels.bands}</b>${bands}</div>`;
    const architecture = root.querySelector(".page-architecture");
    if (architecture) architecture.insertAdjacentElement("afterend", panel);
    else root.prepend(panel);
    if (typeof localizeRenderedChinese === "function") localizeRenderedChinese(panel);
    if (typeof applyReadabilityFloor === "function") requestAnimationFrame(() => applyReadabilityFloor(panel));
  }

  const root = document.getElementById("dynamic-page");
  if (!root) return;
  const observer = new MutationObserver(() => {
    if (!document.getElementById("emerging-niche-score")) renderEmergingNichePolicy();
  });
  observer.observe(root, {childList:true, subtree:false});
  renderEmergingNichePolicy();
})();
