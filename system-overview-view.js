(() => {
  window.renderSystemOverview = function renderSystemOverview(config) {
    const state = window.RESEARCH_SYSTEM_STATE || {};
    const s2 = window.S2_LITERATURE_META || {};
    const sections = window.SYSTEM_OVERVIEW_SECTIONS || {};
    const chapters = pageArchitecture("system-overview").chapters || [];
    const bodies = [
      sections.renderPurpose ? sections.renderPurpose(state,s2) : "",
      sections.renderLifecycle ? sections.renderLifecycle() : "",
      sections.renderPreflight ? sections.renderPreflight(state) : "",
      sections.renderOperations ? sections.renderOperations(state) : "",
    ];
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${chapters.map((chapter,index)=>renderCustomChapter(chapter,index,bodies[index] || "")).join("")}`;
  };
})();
