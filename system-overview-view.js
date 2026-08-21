(() => {
  window.renderSystemOverview = function renderSystemOverview(config) {
    const state = window.RESEARCH_SYSTEM_STATE || {};
    const s2 = window.S2_LITERATURE_META || {};
    const sections = window.SYSTEM_OVERVIEW_SECTIONS || {};
    const chapters = pageArchitecture("system-overview").chapters || [];
    const deep = sections.wrapDeepDive || ((zh,en,body)=>body||"");

    const architectureDetail = `${sections.renderLifecycle ? sections.renderLifecycle(state) : ""}${sections.renderSystemLayers ? sections.renderSystemLayers(state) : ""}${sections.renderMethodologyControls ? sections.renderMethodologyControls(state) : ""}`;
    const machineCompileDetail = sections.renderPreflight ? sections.renderPreflight(state) : "";
    const runtimeReference = sections.renderOperations ? sections.renderOperations(state) : "";
    const agentSafetySummary = window.renderAgentSafetySummary ? window.renderAgentSafetySummary() : "";

    const bodies = [
      `${sections.renderPurpose ? sections.renderPurpose(state,s2) : ""}${agentSafetySummary}${sections.renderAuthorityModel ? sections.renderAuthorityModel(state) : ""}${deep("后台架构与权限审计","Machine architecture, ownership, and authority audit",architectureDetail)}`,
      `${sections.renderProblemDiscoveryPhase ? sections.renderProblemDiscoveryPhase(state) : ""}${deep("证据入口与 AI 检查节点","Evidence intake and AI checkpoints",sections.renderResearchIntake ? sections.renderResearchIntake(state) : "")}`,
      `${sections.renderPaperDesignPhase ? sections.renderPaperDesignPhase(state) : ""}`,
      `${sections.renderExperimentCompilePhase ? sections.renderExperimentCompilePhase(state) : ""}${deep("问题发现与实验启动的后台审计","Backend audit for discovery and experiment launch",machineCompileDetail)}`,
      `${sections.renderValidationScalePhase ? sections.renderValidationScalePhase(state) : ""}${sections.renderGovernanceV2 ? sections.renderGovernanceV2(state) : ""}${sections.renderFailureSemantics ? sections.renderFailureSemantics(state) : ""}${deep("运行、资源、科研工件与组件审计","Runtime, resources, artifacts, and component audit",runtimeReference)}`,
      `${sections.renderPaperEvidencePhase ? sections.renderPaperEvidencePhase(state) : ""}`,
      `${sections.renderPaperConstructionPhase ? sections.renderPaperConstructionPhase(state) : ""}`,
      `${sections.renderReviewRepairPhase ? sections.renderReviewRepairPhase(state) : ""}`,
      `${sections.renderSubmissionClosurePhase ? sections.renderSubmissionClosurePhase(state) : ""}`,
      `${sections.renderSystemLearningPhase ? sections.renderSystemLearningPhase(state) : ""}${sections.renderClosure ? sections.renderClosure(state) : ""}${sections.renderLessons ? sections.renderLessons(state) : ""}`,
    ];
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${chapters.map((chapter,index)=>renderCustomChapter(chapter,index,bodies[index] || "")).join("")}`;
  };
})();
