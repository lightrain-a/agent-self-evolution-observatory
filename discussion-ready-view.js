(() => {
  const data = () => window.DISCUSSION_READY_IDEAS || { target: 20, count: 0, ready: false, ideas: [] };
  const sourceLabels = {
    "main-r2": { zh: "主 ICLR Bank", en: "Main ICLR bank" },
    "v4-r2": { zh: "Idea Discovery v4", en: "Idea Discovery v4" },
    "v5-r2": { zh: "Idea Discovery v5", en: "Idea Discovery v5" },
    "v51-r2": { zh: "v5.1 定向修订", en: "v5.1 targeted repair" },
    "v52-r2": { zh: "v5.2 二阶修订", en: "v5.2 second-order repair" },
    "v53-r2": { zh: "v5.3 最终边界修订", en: "v5.3 final-boundary repair" },
  };
  const label = (source) => sourceLabels[source]?.[language] || source;

  window.renderDiscussionReadyPool = function renderDiscussionReadyPool() {
    const d = data();
    const groups = [];
    for (const idea of d.ideas || []) {
      let group = groups.find((item) => item.source === idea.source);
      if (!group) {
        group = { source: idea.source, ideas: [] };
        groups.push(group);
      }
      group.ideas.push(idea);
    }
    return `<section class="panel discussion-ready-panel"><div class="idea-panel-heading"><div><h3 id="discussion-ready-pool">${language === "zh" ? "师兄正式讨论池：22 个独立二审 PASS Idea" : "Senior discussion pool: 22 independently R2-PASS ideas"}</h3><p class="section-intro">${language === "zh" ? "进入本池的唯一条件是：Idea 已通过指定 Agent 项目网页版 ChatGPT 的独立官方来源二审。REVISE、内部 shortlist 和网络灵感补充批次不计入。达到至少 20 个后停止继续扩张，22 个全部交给师兄/老师讨论，不再由系统做额外 shortlist。" : "The only admission rule is an independent official-source R2 PASS from the designated Agent-project ChatGPT web review. REVISE, internal shortlists, and the supplementary inspired batch do not count. Expansion stops after at least 20 passes; all 22 are presented for senior/teacher discussion with no further system-side shortlist."}</p></div><strong>${d.count || 0}/${d.target || 20} · ${d.ready ? "READY" : "COLLECTING"}</strong></div><div class="discussion-ready-groups">${groups.map((group) => `<section><h4 data-toc="false">${label(group.source)}<span>${group.ideas.length}</span></h4><div>${group.ideas.map((idea) => `<article><b>${textOf(idea.title)}</b><small>R2 PASS · ${label(idea.source)}</small></article>`).join("")}</div></section>`).join("")}</div></section>`;
  };
})();
