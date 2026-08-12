(() => {
  window.renderSystemOverview = function renderSystemOverview(config) {
    const state = window.RESEARCH_SYSTEM_STATE || {};
    const s2 = window.S2_LITERATURE_META || {};
    const sections = window.SYSTEM_OVERVIEW_SECTIONS || {};
    const chapters = pageArchitecture("system-overview").chapters || [];
    const bodies = [
      `${sections.renderPurpose ? sections.renderPurpose(state,s2) : ""}${sections.renderSystemMap ? sections.renderSystemMap(state) : ""}${sections.renderSystemLayers ? sections.renderSystemLayers(state) : ""}${sections.renderMethodologyControls ? sections.renderMethodologyControls(state) : ""}${sections.renderLifecycle ? sections.renderLifecycle(state) : ""}`,
      sections.renderResearchIntake ? sections.renderResearchIntake(state) : "",
      sections.renderPreflight ? sections.renderPreflight(state) : "",
      `${sections.renderGovernanceV2 ? sections.renderGovernanceV2(state) : ""}${sections.renderFailureSemantics ? sections.renderFailureSemantics(state) : ""}`,
      sections.renderOperations ? sections.renderOperations(state) : "",
      `${sections.renderClosure ? sections.renderClosure(state) : ""}${sections.renderLessons ? sections.renderLessons(state) : ""}`,
    ];
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${chapters.map((chapter,index)=>renderCustomChapter(chapter,index,bodies[index] || "")).join("")}`;
  };
})();
