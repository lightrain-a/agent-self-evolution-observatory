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
      `${sections.renderPurpose ? sections.renderPurpose(state,s2) : ""}${sections.renderReaderRoadmap ? sections.renderReaderRoadmap(state) : ""}${agentSafetySummary}${sections.renderAuthorityModel ? sections.renderAuthorityModel(state) : ""}${deep("机器架构：11 个阶段、6 层职责与横向方法学控制","Machine architecture: 11 stages, six layers, and cross-cutting controls",architectureDetail)}`,
      `${sections.renderProblemDiscoveryPhase ? sections.renderProblemDiscoveryPhase(state) : ""}${deep("证据入口与 AI 会诊节点","Evidence intake and AI consultation checkpoints",sections.renderResearchIntake ? sections.renderResearchIntake(state) : "")}`,
      `${sections.renderPaperDesignPhase ? sections.renderPaperDesignPhase(state) : ""}`,
      `${sections.renderExperimentCompilePhase ? sections.renderExperimentCompilePhase(state) : ""}${deep("完整机器门 / 问题发现 / 论文设计编译细节","Full machine gates, discovery, and paper-design compiler detail",machineCompileDetail)}`,
      `${sections.renderValidationScalePhase ? sections.renderValidationScalePhase(state) : ""}${sections.renderGovernanceV2 ? sections.renderGovernanceV2(state) : ""}${sections.renderFailureSemantics ? sections.renderFailureSemantics(state) : ""}${deep("运行时、GPU、科研工件、自动化与组件清单","Runtime, GPU, artifacts, automation, and component inventory",runtimeReference)}`,
      `${sections.renderPaperEvidencePhase ? sections.renderPaperEvidencePhase(state) : ""}`,
      `${sections.renderSystemLearningPhase ? sections.renderSystemLearningPhase(state) : ""}${sections.renderClosure ? sections.renderClosure(state) : ""}${sections.renderLessons ? sections.renderLessons(state) : ""}`,
    ];
    return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("system-overview"))}${chapters.map((chapter,index)=>renderCustomChapter(chapter,index,bodies[index] || "")).join("")}`;
  };
})();
