const DATA = [...(window.S2_LIVE_PAPERS || []), ...(window.SUPPLEMENTAL_PAPERS || [])];
const PAGES = window.PAGE_CONTENT || {};
const NAV_GROUPS = window.NAV_GROUPS || [];
const CATALOG_SOURCES = [
  {
    name: "Self-Improvements survey catalog",
    parser: "survey",
    urls: [
      "https://api.github.com/repos/selfimproving-agent/Awesome-Self-Improving-Agents/contents/README.md",
      "https://raw.githubusercontent.com/selfimproving-agent/Awesome-Self-Improving-Agents/main/README.md",
      "https://cdn.jsdelivr.net/gh/selfimproving-agent/Awesome-Self-Improving-Agents@main/README.md",
    ],
  },
  {
    name: "Experience-era survey catalog",
    parser: "frontis",
    urls: [
      "https://api.github.com/repos/FrontisAI/Awesome-Self-Improving-Agents/contents/README.md",
      "https://raw.githubusercontent.com/FrontisAI/Awesome-Self-Improving-Agents/main/README.md",
      "https://cdn.jsdelivr.net/gh/FrontisAI/Awesome-Self-Improving-Agents@main/README.md",
    ],
  },
];
const CATALOG_CACHE_KEY = "agent-evolution-upstream-catalog-v2";
const CATALOG_CACHE_MAX_AGE = 6 * 60 * 60 * 1000;
const CITATION_CONFIG = window.CITATION_RANKING_CONFIG || {sourceName:"OpenAlex",cacheVersion:"v2",cacheMaxAgeDays:7,topVenuePatterns:[],readingRoles:[],enablingCategories:[],sortModes:[]};
const CITATION_CACHE_KEY = `agent-evolution-citations-${CITATION_CONFIG.cacheVersion || "v1"}`;
const CITATION_CACHE_MAX_AGE = (CITATION_CONFIG.cacheMaxAgeDays || 7) * 24 * 60 * 60 * 1000;
const pageId = document.body.dataset.page || "home";
const NAVIGATION_TYPE = performance.getEntriesByType?.("navigation")?.[0]?.type || "navigate";
if (pageId === "paper-ideas" && "scrollRestoration" in history) history.scrollRestoration = "manual";
const initialQuery = new URLSearchParams(location.search);
let language = localStorage.getItem("agent-evolution-language") || "en";
let catalog = [];
let activeFilter = initialQuery.get("method") || "all";
let activeYear = initialQuery.get("year") || "all";
let activePublicationType = initialQuery.get("publication") || "all";
let activeSignal = initialQuery.get("signal") || "all";
let visionOnly = initialQuery.get("vision") === "1";
let bibliographySort = initialQuery.get("sort") || localStorage.getItem("agent-evolution-bibliography-sort") || "priority";
let bibliographyLimit = 80;
let citationIndex = new Map();
let citationCache = loadCitationCache();
let citationRefreshState = {running:false,total:0,completed:0,matched:0,failed:0,startedAt:null};
const PAGE_CITATIONS = {
  "home": [
    ["Self-Improvements in Modern Agentic Systems: A Survey", "A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve"],
    ["Self-Rewarding Language Models", "A-MEM: Agentic Memory for LLM Agents", "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
  ],
  "foundations": [
    ["Self-Refine: Iterative Refinement with Self-Feedback", "Reflexion: Language Agents with Verbal Reinforcement Learning"],
    ["Voyager: An Open-Ended Embodied Agent with Large Language Models", "Automated Design of Agentic Systems"],
    ["A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve", "Self-Improvements in Modern Agentic Systems: A Survey"],
    ["A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems"],
  ],
  "taxonomy": [
    ["Self-Improvements in Modern Agentic Systems: A Survey", "Agent Harness Engineering: A Survey"],
    ["A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve"],
    ["A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems"],
    ["Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity", "VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents"],
  ],
  "model-improvement": [
    ["WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning", "Agent0: Unleashing Self-Evolving Agents from Zero Data", "VisPlay: Self-Evolving Vision-Language Models"],
    ["Active Zero: Self-Evolving Vision-Language Models through Active Environment Exploration", "RISE: Reliable Improvement in Self-Evolving Vision-Language Models"],
    ["Self-Rewarding Language Models", "Reflexion: Language Agents with Verbal Reinforcement Learning"],
    ["Continual Harness: Online Adaptation for Self-Improving Foundation Agents"],
  ],
  "prompt-evolution": [
    ["Large Language Models as Optimizers", "TextGrad: Automatic Differentiation via Text", "Self-Refine: Iterative Refinement with Self-Feedback"],
    ["EvoPrompt: Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers", "Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution"],
    ["GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning", "Trace is the Next AutoDiff: Generative Optimization with Rich Feedback, Execution Traces, and LLMs"],
  ],
  "memory-evolution": [
    ["ExpeL: LLM Agents Are Experiential Learners", "Agent Workflow Memory", "A-MEM: Agentic Memory for LLM Agents"],
    ["MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory", "EvolveMem: Self-Evolving Memory Architecture via AutoResearch for LLM Agents"],
    ["MemEye: Visual-Centric Evaluation for Multimodal Agent Memory", "MemLens: Benchmarking Multimodal Long-Term Memory"],
    ["UI-Mem: Self-Evolving Experience Memory for Online Reinforcement Learning in Mobile GUI Agents", "MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", "Hidden in Memory: Sleeper Memory Poisoning in LLM Agents"],
    ["MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", "From Memory to Skills: Evidence-Grounded Co-Evolution Governance for Long-Horizon LLM Agents", "FSFM: A Biologically-Inspired Framework for Selective Forgetting of Agent Memory"],
    ["EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective", "MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents"],
  ],
  "tool-evolution": [
    ["Voyager: An Open-Ended Embodied Agent with Large Language Models", "SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills"],
    ["META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding", "OpenSkill: Open-World Self-Evolution for LLM Agents"],
    ["SkillOpt: Executive Strategy for Self-Evolving Agent Skills", "CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification"],
    ["SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems", "MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation"],
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "Counterfactual Trace Auditing of LLM Agent Skills"],
  ],
  "workflow-evolution": [
    ["Self-Improvements in Modern Agentic Systems: A Survey", "Agent Harness Engineering: A Survey"],
    ["Language Agents as Optimizable Graphs", "Automated Design of Agentic Systems", "AFlow: Automating Agentic Workflow Generation", "Multi-agent Architecture Search via Agentic Supernet", "Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents"],
    ["HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry", "Autogenesis: A Self-Evolving Agent Protocol"],
    ["AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity"],
    ["Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning", "The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators"],
    ["Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams", "AFlow: Automating Agentic Workflow Generation"],
  ],
  "visual-multimodal": [
    ["VisPlay: Self-Evolving Vision-Language Models", "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding", "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval"],
    ["Active Zero: Self-Evolving Vision-Language Models through Active Environment Exploration", "RISE: Reliable Improvement in Self-Evolving Vision-Language Models", "Agent0-VL: Exploring Self-Evolving Agent for Tool-Integrated Vision-Language Reasoning"],
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning", "Can Large Vision-Language Models Correct Semantic Grounding Errors By Themselves?"],
    ["Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", "MemEye: Visual-Centric Evaluation for Multimodal Agent Memory"],
    ["Unified Multimodal Models as Auto-Encoders", "SciEducator: Scientific Video Understanding and Educating via Deming-Cycle Multi-Agent System", "JarvisEvo: Towards a Self-Evolving Photo Editing Agent with Synergistic Editor-Evaluator Optimization", "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding"],
  ],
  "gui-web": [
    ["WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning", "SEAgent: Self-Evolving Computer Use Agent", "Mobile-Agent-E: Self-Evolving Mobile Assistant for Complex Tasks"],
    ["SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills", "WebEvolver: Enhancing Web Agent Self-Improvement with Coevolving World Model"],
    ["VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks", "WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks?"],
    ["ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents"],
  ],
  "embodied-world": [
    ["Self-evolving Embodied AI", "History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation"],
    ["NavMorph: A Self-Evolving World Model for Vision-and-Language Navigation in Continuous Environments", "World Model Implanting for Test-Time Adaptation of Embodied Agents"],
    ["Phoenix: A Motion-based Self-Reflection Framework for Fine-grained Robotic Action Correction", "RISE: Self-Improving Robot Policy with Compositional World Model"],
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents"],
  ],
  "evaluation-safety": [
    ["Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks"],
    ["MemEye: Visual-Centric Evaluation for Multimodal Agent Memory", "MemLens: Benchmarking Multimodal Long-Term Memory", "MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity"],
    ["DrunkAgent: Stealthy Memory Corruption in LLM-Powered Recommender Agents", "ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents"],
    ["Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents", "Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use", "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents"],
  ],
  "datasets-benchmarks": [
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "AgentGym: Evolving Large Language Model-Based Agents across Diverse Environments"],
    ["VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks", "ManiSkill2: A Unified Benchmark for Generalizable Manipulation Skills", "DiscoveryWorld: A Virtual Environment for Developing and Evaluating Automated Scientific Discovery Agents"],
    ["MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks", "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks", "MemEye: Visual-Centric Evaluation for Multimodal Agent Memory"],
    ["Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
  ],
  "repositories": [
    ["Self-Improvements in Modern Agentic Systems: A Survey", "Agent Harness Engineering: A Survey"],
    ["Voyager: An Open-Ended Embodied Agent with Large Language Models", "A-MEM: Agentic Memory for LLM Agents", "AFlow: Automating Agentic Workflow Generation"],
    ["Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams"],
    ["VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks", "MemEye: Visual-Centric Evaluation for Multimodal Agent Memory"],
  ],
  "research-agenda": [
    ["Counterfactual Trace Auditing of LLM Agent Skills", "EVE-Agent: Evidence-Verifiable Self-Evolving Agents"],
    ["MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", "SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems", "From Memory to Skills: Evidence-Grounded Co-Evolution Governance for Long-Horizon LLM Agents"],
    ["AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity", "Autogenesis: A Self-Evolving Agent Protocol", "HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry"],
    ["Self-evolving Embodied AI", "WorldEvolver: Self-Evolving World Models for LLM Agent Planning"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry", "MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", "Hidden in Memory: Sleeper Memory Poisoning in LLM Agents", "Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning", "From Memory to Skills: Evidence-Grounded Co-Evolution Governance for Long-Horizon LLM Agents", "FSFM: A Biologically-Inspired Framework for Selective Forgetting of Agent Memory"],
    ["Partially Performative Prediction", "Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback", "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", "Self-Evolving Software Agents", "Accelerating Scientific Discovery with Autonomous Goal-evolving Agents", "AI Agent Pull Requests on GitHub: Frequency, Structure, and Merge Conflict Rates"],
    ["Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents", "Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use", "Agentic Uncertainty Quantification", "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents"],
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "MemLens: Benchmarking Multimodal Long-Term Memory", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
  ],
  "paper-problem": [
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["EVE-Agent: Evidence-Verifiable Self-Evolving Agents", "Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity"],
    ["MemEye: Visual-Centric Evaluation for Multimodal Agent Memory"],
  ],
  "paper-ideas": [
    ["VisPlay: Self-Evolving Vision-Language Models", "Agent0-VL: Exploring Self-Evolving Agent for Tool-Integrated Vision-Language Reasoning", "Counterfactual Trace Auditing of LLM Agent Skills", "SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems", "MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
    ["EVE-Agent: Evidence-Verifiable Self-Evolving Agents", "Counterfactual Trace Auditing of LLM Agent Skills", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["Self-evolving Embodied AI", "From Fixed to Free Cameras: Calibration-Free View-Robust Vision-Language-Action Model"],
    ["MemEye: Visual-Centric Evaluation for Multimodal Agent Memory", "WorldMemArena: Evaluating Multimodal Agent Memory Through Action-World Interaction", "EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective"],
    ["MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", "SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["Active Zero: Self-Evolving Vision-Language Models through Active Environment Exploration", "Agent-World: Scaling Real-World Environment Synthesis for Evolving General Agent Intelligence"],
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "EvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification"],
    ["Agent-World: Scaling Real-World Environment Synthesis for Evolving General Agent Intelligence", "SimWorld Studio: Automatic Environment Generation with Evolving Coding Agent for Embodied Agent Learning"],
    ["A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve", "Self-Improvements in Modern Agentic Systems: A Survey"],
  ],
  "direction-board": [
    ["Self-Improvements in Modern Agentic Systems: A Survey", "A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve", "Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies"],
    ["Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Agentic Uncertainty Quantification", "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents", "Self-Evolving Multi-Agent Systems via Decentralized Memory"],
    ["VisPlay: Self-Evolving Vision-Language Models", "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding", "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval", "The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators", "AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents", "Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use"],
    ["Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents", "Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use", "Agentic Uncertainty Quantification"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "Self-Improvements in Modern Agentic Systems: A Survey"],
    ["Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", "MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", "Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Agentic Uncertainty Quantification"],
    ["LensWalk: Agentic Video Understanding by Planning How You See in Videos", "From Fixed to Free Cameras: Calibration-Free View-Robust Vision-Language-Action Model", "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", "Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback", "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents"],
    ["Self-Evolving Software Agents", "Accelerating Scientific Discovery with Autonomous Goal-evolving Agents", "The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators", "Self-Evolving Multi-Agent Systems via Decentralized Memory"],
    ["VisPlay: Self-Evolving Vision-Language Models", "Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "Agentic Uncertainty Quantification"],
    ["A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems", "Self-Improvements in Modern Agentic Systems: A Survey", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
  ],
  "paper-experiments": [
    ["VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks", "WebArena: A Realistic Web Environment for Building Autonomous Agents"],
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["MemEye: Visual-Centric Evaluation for Multimodal Agent Memory"],
  ],
  "paper-roadmap": [
    ["VisPlay: Self-Evolving Vision-Language Models", "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding"],
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity"],
  ],
  "review-log": [
    ["A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve", "Self-Improvements in Modern Agentic Systems: A Survey", "Counterfactual Trace Auditing of LLM Agent Skills", "SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems", "MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
  ],
};

function esc(value = "") {
  return String(value).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}
function normalizeTitle(value = "") {
  return value.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, " ").trim();
}
function slugify(value = "section") {
  return value.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9\u4e00-\u9fff]+/g, "-").replace(/^-|-$/g, "") || "section";
}
function textOf(value) {
  if (typeof value === "string") return value;
  if (!value) return "";
  return value[language] || value.en || value.zh || "";
}
function resetPaperIdeasAfterReload() {
  if (pageId !== "paper-ideas" || NAVIGATION_TYPE !== "reload") return;
  const root = document.getElementById("dynamic-page");
  root?.querySelectorAll("details[open]").forEach((node) => { node.open = false; });
  const reset = () => window.scrollTo(0, 0);
  reset();
  requestAnimationFrame(() => requestAnimationFrame(reset));
  setTimeout(reset, 120);
}
function setLanguage(next) {
  const oldHeight = Math.max(document.documentElement.scrollHeight, 1);
  const ratio = window.scrollY / oldHeight;
  language = next;
  localStorage.setItem("agent-evolution-language", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  renderPage();
  requestAnimationFrame(() => window.scrollTo(0, ratio * document.documentElement.scrollHeight));
}

function renderFooter() {
  const footer = document.querySelector(".footer");
  if (footer) footer.innerHTML = `${language === "zh" ? "Agent 自进化研究站" : "Agent Self-Evolution Observatory"} · <a href="bibliography.html#group-coverage-method">${language === "zh" ? "覆盖协议" : "Coverage protocol"}</a> · <a href="bibliography.html">${language === "zh" ? "动态文献库" : "Live bibliography"}</a> · <a href="https://www.semanticscholar.org/product/api" target="_blank" rel="noopener">${language === "zh" ? "文献元数据由 Semantic Scholar 提供" : "Literature metadata powered by Semantic Scholar"}</a> · <a href="https://github.com/lightrain-a/agent-self-evolution-observatory" target="_blank" rel="noopener">GitHub</a> · 8 August 2026`;
}
function renderSemanticScholarStatus() {
  const meta = window.S2_LITERATURE_META;
  if (!meta) return `<div class="integrity-status warn s2-provider-status"><strong>S2 SNAPSHOT</strong><span>${language === "zh" ? "尚未加载 Semantic Scholar 同步快照；当前仍可使用人工文献库。" : "No Semantic Scholar sync snapshot is loaded; the curated literature corpus remains available."}</span></div>`;
  const stats = meta.statistics || {};
  const retrieved = meta.retrieved_at ? new Date(meta.retrieved_at).toLocaleString(language === "zh" ? "zh-CN" : "en-US") : (language === "zh" ? "未知" : "unknown");
  const expanded = meta.seed_expansion?.expanded_count || 0;
  return `<div class="integrity-status pass s2-provider-status"><strong>S2 LIVE</strong><span>${language === "zh" ? `已同步 ${stats.paper_count || 0} 篇候选文献，覆盖 ${stats.query_count || 0} 条五路检索，并通过引用图补充 ${expanded} 篇；更新时间 ${retrieved}。这些结果用于发现最近工作，不自动等同于新颖性判断。` : `${stats.paper_count || 0} candidate papers from ${stats.query_count || 0} five-route queries, including ${expanded} citation-graph additions; updated ${retrieved}. These matches support discovery and do not constitute an automatic novelty verdict.`}</span></div>`;
}
function renderShell() {
  if (!document.querySelector('link[rel="icon"]')) document.head.insertAdjacentHTML("beforeend", '<link rel="icon" href="favicon.svg" type="image/svg+xml">');
  if (!document.querySelector('link[rel="manifest"]')) document.head.insertAdjacentHTML("beforeend", '<link rel="manifest" href="site.webmanifest">');
  document.body.insertAdjacentHTML("afterbegin", `<a class="skip-link" href="#main-content">Skip to content</a><button class="sidebar-overlay" aria-label="Close navigation" hidden></button><button class="back-to-top" type="button" aria-label="Back to top">↑</button>`);
  const sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;
  sidebar.insertAdjacentHTML("afterbegin", `<button class="sidebar-close" aria-label="Close navigation">×</button>`);
  const nav = sidebar.querySelector(".nav");
  nav.innerHTML = NAV_GROUPS.map((group) => {
    const isOpen = group.pages.some(([href]) => href.replace(".html", "") === pageId) || group.open;
    return `<details class="nav-group" ${isOpen ? "open" : ""}><summary class="nav-level1"><span>${esc(textOf(group.title))}</span><span class="nav-chevron">⌄</span></summary><div class="nav-children">${group.pages.map(([href, label]) => {
      const active = href.replace(".html", "") === pageId || (href === "index.html" && pageId === "home");
      return `<a class="nav-level2 ${active ? "active" : ""}" href="${href}">${esc(textOf(label))}</a>`;
    }).join("")}</div></details>`;
  }).join("");
  const topbar = document.querySelector(".topbar");
  const searchInput = document.getElementById("site-search");
  if (pageId === "bibliography" && initialQuery.get("q") && searchInput) searchInput.value = initialQuery.get("q");
  if (topbar && !topbar.querySelector(".language-toggle")) {
    topbar.insertAdjacentHTML("beforeend", `<button class="language-toggle" type="button">${language === "en" ? "中文" : "English"}</button>`);
  }
  renderFooter();
  document.querySelector(".language-toggle")?.addEventListener("click", () => setLanguage(language === "en" ? "zh" : "en"));
  const mobileToggle = document.querySelector(".mobile-toggle");
  const overlay = document.querySelector(".sidebar-overlay");
  const close = () => { sidebar.classList.remove("open"); overlay.hidden = true; };
  mobileToggle?.addEventListener("click", () => { sidebar.classList.add("open"); overlay.hidden = false; });
  sidebar.querySelector(".sidebar-close")?.addEventListener("click", close);
  overlay?.addEventListener("click", close);
  const backToTop = document.querySelector(".back-to-top");
  const updateBackToTop = () => backToTop?.classList.toggle("visible", window.scrollY > 700);
  window.addEventListener("scroll", updateBackToTop, { passive: true });
  backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
    if (event.key === "/" && !/input|textarea|select/i.test(document.activeElement?.tagName || "")) {
      event.preventDefault(); document.getElementById("site-search")?.focus();
    }
  });
}

function parseAwesomeMarkdown(markdown) {
  const rows = [];
  let major = "Unclassified";
  let minor = "General";
  for (const raw of markdown.split(/\r?\n/)) {
    let match = raw.match(/^####\s+(.+)/);
    if (match) major = match[1].replace(/[🟦🟩📊📚🧭]/g, "").trim();
    match = raw.match(/^<summary><b>(.+?)<\/b><\/summary>/);
    if (match) minor = match[1].replace(/<[^>]+>/g, "").trim();
    match = raw.match(/^\s*-\s+\*\*(.+?)\*\*/);
    if (match) minor = match[1].trim();
    match = raw.match(/^\s*\|\s*(20\d\d)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[paper\]\((.*?)\)\s*\|\s*(.*?)\s*\|\s*$/i);
    if (!match || !match[4]) continue;
    const codeMatch = match[5].match(/\[code\]\((.*?)\)/i);
    rows.push({
      year: Number(match[1]), title: match[2].trim(), venue: match[3].trim(), url: match[4].trim(),
      repo: codeMatch ? codeMatch[1].trim() : "", category: major, subcategory: minor,
      updateTarget: inferUpdateTarget(`${major} ${minor} ${match[2]}`), signal: inferSignal(`${major} ${minor} ${match[2]}`),
      vision: inferVision(`${major} ${minor} ${match[2]}`), source: "awesome-survey"
    });
  }
  return rows;
}
function parseFrontisMarkdown(markdown) {
  const rows = [];
  let major = "Unclassified";
  let minor = "General";
  for (const raw of markdown.split(/\r?\n/)) {
    let match = raw.match(/^##\s+(.+)/);
    if (match) major = match[1].replace(/[📚🧠🛠️🧪🧭📊]/g, "").trim();
    match = raw.match(/^###\s+(.+)/);
    if (match) minor = match[1].replace(/[📚🧠🛠️🧪🧭📊]/g, "").trim();
    match = raw.match(/^\|\s*(20\d\d)(?:-\d\d)?\s*\|\s*`?[^|`]*`?\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$/);
    if (!match) continue;
    const paperLinks = [...match[3].matchAll(/\]\((https?:\/\/[^)]+)\)/g)].map((m) => m[1]);
    const repoLinks = [...match[4].matchAll(/\]\((https?:\/\/[^)]+)\)/g)].map((m) => m[1]);
    const url = paperLinks.at(-1) || "";
    if (!url) continue;
    const title = match[2].replace(/<[^>]+>/g, "").trim();
    const context = `${major} ${minor} ${title}`;
    rows.push({
      year: Number(match[1]), title, venue: inferVenue(url), url,
      repo: repoLinks.at(-1) || "", category: major, subcategory: minor,
      updateTarget: inferUpdateTarget(context), signal: inferSignal(context),
      vision: inferVision(context), source: "experience-survey"
    });
  }
  return rows;
}
function inferVenue(url = "") {
  const u = url.toLowerCase();
  if (u.includes("arxiv.org")) return "arXiv";
  if (u.includes("openreview.net")) return "OpenReview";
  if (u.includes("openaccess.thecvf.com")) return "CVF Open Access";
  if (u.includes("aclanthology.org")) return "ACL Anthology";
  if (u.includes("proceedings.mlr.press")) return "PMLR";
  if (u.includes("github.com")) return "Repository";
  return "Paper / technical report";
}
function inferUpdateTarget(text) {
  const t = text.toLowerCase();
  if (/memory|experience graph|cheatsheet|context engineering/.test(t)) return "memory";
  if (/prompt|instruction|textual gradient/.test(t)) return "prompt";
  if (/tool|skill|api|mcp/.test(t)) return "tool/skill";
  if (/world model|environment model/.test(t)) return "world model";
  if (/workflow|graph|scaffold|gödel|harness|architecture|multi-agent/.test(t)) return "workflow/scaffold";
  if (/reward|rl|finetun|training|model|reasoning/.test(t)) return "model parameters";
  return "agent component";
}
function inferSignal(text) {
  const t = text.toLowerCase();
  if (/critic|feedback|reflection|judge|evaluation/.test(t)) return "critique/evaluation";
  if (/environment|web|robot|embodied|interaction|exploration/.test(t)) return "environment interaction";
  if (/self-play|population|evolution|tournament/.test(t)) return "population/self-play";
  if (/reward|reinforcement|rl/.test(t)) return "scalar reward";
  if (/memory|experience/.test(t)) return "experience reuse";
  return "self-generated artifact";
}
function inferVision(text) {
  return /vision|visual|image|video|multimodal|vln|robot|embodied|gui|web|photo|t2i|text-to-image|world model/i.test(text);
}
function publicationType(record) {
  const venue = String(record.venue || "").toLowerCase();
  const url = String(record.url || "").toLowerCase();
  if (/repository|github/.test(venue) || url.includes("github.com")) return "Repository";
  if (/blog|technical report|paper \/ technical report/.test(venue) || /substack|martinfowler|anthropic\.com\/engineering|openai\.com\/index/.test(url)) return "Blog/Report";
  if (/arxiv|preprint|ssrn/.test(venue) || url.includes("arxiv.org") || url.includes("ssrn.com")) return "Preprint";
  if (/cvpr|iccv|eccv|iclr|icml|neurips|aaai|acl|emnlp|colm|kdd|www|rss|uist|tmrl|tmlr|pmlr|openreview/.test(venue) || /openaccess\.thecvf|aclanthology|proceedings\.mlr|proceedings\.iclr/.test(url)) return "Published";
  return "Other";
}
function loadCitationCache() {
  const staticChunks = Array.isArray(window.CITATION_CACHE_CHUNKS) ? window.CITATION_CACHE_CHUNKS : [];
  const staticRecords = {...(CITATION_CONFIG.seedRecords || {})};
  let staticUpdatedAt = CITATION_CONFIG.snapshotUpdatedAt || null;
  staticChunks.forEach((chunk) => {
    Object.assign(staticRecords, chunk?.records || {});
    if (chunk?.updatedAt && (!staticUpdatedAt || Date.parse(chunk.updatedAt) > Date.parse(staticUpdatedAt))) staticUpdatedAt = chunk.updatedAt;
  });
  try {
    const cached = JSON.parse(localStorage.getItem(CITATION_CACHE_KEY) || "null");
    if (cached && cached.records && typeof cached.records === "object") {
      return {source:CITATION_CONFIG.sourceName || "OpenAlex",updatedAt:cached.updatedAt || staticUpdatedAt,records:{...staticRecords,...cached.records}};
    }
  } catch (error) {
    console.warn("Citation cache could not be read", error);
  }
  return {source:CITATION_CONFIG.sourceName || "OpenAlex",updatedAt:staticUpdatedAt,records:staticRecords};
}
function saveCitationCache() {
  citationCache.source = CITATION_CONFIG.sourceName || "OpenAlex";
  citationCache.updatedAt = new Date().toISOString();
  try { localStorage.setItem(CITATION_CACHE_KEY, JSON.stringify(citationCache)); }
  catch (error) { console.warn("Citation cache could not be saved", error); }
}
function citationMetadata(record) {
  return citationCache.records?.[normalizeTitle(record.title)] || null;
}
function citationCount(record) {
  const value = citationMetadata(record)?.citationCount;
  return Number.isFinite(value) ? value : null;
}
function topVenueInfo(record) {
  const text = `${record.venue || ""} ${citationMetadata(record)?.matchedVenue || ""}`.toLowerCase();
  for (const entry of CITATION_CONFIG.topVenuePatterns || []) {
    try { if (new RegExp(entry.pattern, "i").test(text)) return entry; }
    catch (error) { console.warn("Invalid top-venue pattern", entry, error); }
  }
  return null;
}
function publicationTier(record) {
  if (topVenueInfo(record) && publicationType(record) === "Published") return 0;
  const type = publicationType(record);
  if (type === "Published") return 1;
  if (type === "Preprint") return 2;
  if (type === "Other") return 3;
  return 4;
}
function publicationTierLabel(record) {
  const top = topVenueInfo(record);
  if (top && publicationType(record) === "Published") return language === "zh" ? `顶会／顶刊 · ${top.label}` : `top venue · ${top.label}`;
  const type = publicationType(record);
  const labels = {
    Published:{en:"peer-reviewed publication",zh:"其他正式发表"},
    Preprint:{en:"preprint / arXiv",zh:"预印本／arXiv"},
    Other:{en:"other scholarly record",zh:"其他学术条目"},
    Repository:{en:"repository",zh:"代码仓库"},
    "Blog/Report":{en:"report / blog",zh:"报告／博客"},
  };
  return textOf(labels[type] || labels.Other);
}
function readingRoleInfo(record) {
  const roles = CITATION_CONFIG.readingRoles || [];
  const findRole = (id) => roles.find((role) => role.id === id) || {id,rank:99,title:{en:id,zh:id},description:{en:"",zh:""}};
  const category = String(record.category || "").toLowerCase();
  const subcategory = String(record.subcategory || "").toLowerCase();
  const title = String(record.title || "").toLowerCase();
  const text = `${title} ${category} ${subcategory}`;
  const titleAndTask = `${title} ${subcategory}`;
  if (category === "foundations") return findRole("model-foundation");
  if (category === "agent foundations") return findRole("agent-foundation");
  if (category === "survey" || /\bsurvey\b|taxonomy|systematic review/.test(title)) return findRole("field-overview");
  const evaluationPattern = CITATION_CONFIG.evaluationPattern || "benchmark|evaluation|safety|security|verification|governance|provenance|audit|rollback";
  try { if (new RegExp(evaluationPattern, "i").test(text)) return findRole("evaluation-governance"); }
  catch (error) { console.warn("Invalid evaluation reading-role pattern", error); }
  const directPattern = CITATION_CONFIG.directEvolutionPattern || "self[- ]?(evolv|improv)|evolution";
  try { if (new RegExp(directPattern, "i").test(titleAndTask)) return findRole("core-evolution"); }
  catch (error) { console.warn("Invalid direct-evolution reading-role pattern", error); }
  const enabling = (CITATION_CONFIG.enablingCategories || []).map((value) => String(value).toLowerCase());
  if (enabling.some((value) => category.includes(value)) || /memory|skill|tool|workflow|agent graph|world model|online curriculum|reflection|critic|prompt optim/.test(text)) return findRole("enabling-mechanism");
  return findRole("adjacent");
}
function readingRoleRank(record) { return Number(readingRoleInfo(record).rank ?? 99); }
function readingRoleLabel(record) { return textOf(readingRoleInfo(record).title); }
function compareCitationValues(a, b) {
  const ac = citationCount(a), bc = citationCount(b);
  if (ac === null && bc !== null) return 1;
  if (ac !== null && bc === null) return -1;
  if (ac !== null && bc !== null && ac !== bc) return bc - ac;
  return 0;
}
function compareRecommendedWithinRole(a, b, roleId) {
  if (roleId === "model-foundation" || roleId === "agent-foundation") {
    return (a.year || 0) - (b.year || 0) || publicationTier(a) - publicationTier(b) || compareCitationValues(a, b) || a.title.localeCompare(b.title);
  }
  if (roleId === "field-overview") {
    return (b.year || 0) - (a.year || 0) || publicationTier(a) - publicationTier(b) || compareCitationValues(a, b) || a.title.localeCompare(b.title);
  }
  return publicationTier(a) - publicationTier(b) || (b.year || 0) - (a.year || 0) || compareCitationValues(a, b) || a.title.localeCompare(b.title);
}
function compareBibliographyRecords(a, b, mode = bibliographySort) {
  if (mode === "citations") return compareCitationValues(a, b) || readingRoleRank(a) - readingRoleRank(b) || publicationTier(a) - publicationTier(b) || (b.year || 0) - (a.year || 0) || a.title.localeCompare(b.title);
  if (mode === "venue") return publicationTier(a) - publicationTier(b) || readingRoleRank(a) - readingRoleRank(b) || (b.year || 0) - (a.year || 0) || compareCitationValues(a, b) || a.title.localeCompare(b.title);
  if (mode === "recent") return (b.year || 0) - (a.year || 0) || readingRoleRank(a) - readingRoleRank(b) || publicationTier(a) - publicationTier(b) || compareCitationValues(a, b) || a.title.localeCompare(b.title);
  const roleDelta = readingRoleRank(a) - readingRoleRank(b);
  if (roleDelta) return roleDelta;
  return compareRecommendedWithinRole(a, b, readingRoleInfo(a).id);
}
function sortBibliographyRecords(records, mode = bibliographySort) {
  return [...records].sort((a, b) => compareBibliographyRecords(a, b, mode));
}
function citationCoverage(records = catalog) {
  const matched = records.filter((record) => citationCount(record) !== null).length;
  return {matched,total:records.length,ratio:records.length ? matched / records.length : 0};
}
function titleMatchScore(query, candidate, queryYear, candidateYear) {
  const q = normalizeTitle(query), c = normalizeTitle(candidate);
  if (!q || !c) return 0;
  if (q === c) return 1;
  const qTokens = new Set(q.split(/\s+/)), cTokens = new Set(c.split(/\s+/));
  const overlap = [...qTokens].filter((token) => cTokens.has(token)).length;
  const union = new Set([...qTokens, ...cTokens]).size || 1;
  let score = overlap / union;
  if (q.includes(c) || c.includes(q)) score = Math.max(score, Math.min(q.length, c.length) / Math.max(q.length, c.length));
  if (queryYear && candidateYear) {
    const gap = Math.abs(Number(queryYear) - Number(candidateYear));
    if (gap === 0) score += .04;
    else if (gap > 2) score -= .12;
  }
  return Math.max(0, Math.min(1, score));
}
async function fetchOpenAlexCitation(record, retries = 3) {
  const params = new URLSearchParams({search:record.title,"per-page":"5",select:"id,display_name,cited_by_count,publication_year,primary_location",mailto:CITATION_CONFIG.mailto || "contact@lightrain.asia"});
  for (let attempt = 0; attempt < retries; attempt += 1) {
    try {
      const response = await fetch(`https://api.openalex.org/works?${params.toString()}`, {headers:{Accept:"application/json"}});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      const candidates = (payload.results || []).map((candidate) => ({candidate,score:titleMatchScore(record.title,candidate.display_name,record.year,candidate.publication_year)})).sort((a,b) => b.score - a.score);
      const best = candidates[0];
      if (!best || best.score < .78) return {matched:false};
      return {matched:true,citationCount:Number(best.candidate.cited_by_count || 0),openAlexId:best.candidate.id,matchedTitle:best.candidate.display_name,matchedYear:best.candidate.publication_year,matchedVenue:best.candidate.primary_location?.source?.display_name || "",matchScore:Number(best.score.toFixed(3)),fetchedAt:new Date().toISOString()};
    } catch (error) {
      if (attempt === retries - 1) return {matched:false,error:String(error)};
      await new Promise((resolve) => setTimeout(resolve, 600 * (attempt + 1)));
    }
  }
  return {matched:false};
}
async function refreshCitationMetadata({force=false} = {}) {
  if (citationRefreshState.running || !catalog.length) return;
  const now = Date.now();
  const pending = [...catalog].sort((a, b) => {
    const aCore = (window.TOP_PAPER_ANALYSES || {})[a.title] ? 0 : 1;
    const bCore = (window.TOP_PAPER_ANALYSES || {})[b.title] ? 0 : 1;
    return aCore - bCore || publicationTier(a) - publicationTier(b) || (b.year || 0) - (a.year || 0) || a.title.localeCompare(b.title);
  }).filter((record) => {
    const cached = citationMetadata(record);
    if (force || !cached) return true;
    const fetched = Date.parse(cached.fetchedAt || "");
    return !Number.isFinite(fetched) || now - fetched > CITATION_CACHE_MAX_AGE;
  });
  citationRefreshState = {running:true,total:pending.length,completed:0,matched:0,failed:0,startedAt:new Date().toISOString()};
  updateCitationStatus();
  let cursor = 0;
  const workers = Array.from({length:Math.min(6, pending.length)}, async () => {
    while (cursor < pending.length) {
      const index = cursor++;
      const record = pending[index];
      const result = await fetchOpenAlexCitation(record);
      citationRefreshState.completed += 1;
      if (result.matched) {
        citationCache.records[normalizeTitle(record.title)] = result;
        citationRefreshState.matched += 1;
        updateCitationCard(record);
      } else citationRefreshState.failed += 1;
      if (citationRefreshState.completed % 20 === 0 || citationRefreshState.completed === pending.length) {
        saveCitationCache();
        updateCitationStatus();
      }
      if (citationRefreshState.completed % 100 === 0 || citationRefreshState.completed === pending.length) {
        if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
      }
      await new Promise((resolve) => setTimeout(resolve, 80));
    }
  });
  await Promise.all(workers);
  citationRefreshState.running = false;
  saveCitationCache();
  updateCitationStatus();
  if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
}
function updateCitationStatus() {
  const node = document.getElementById("citation-ranking-status");
  if (!node) return;
  const coverage = citationCoverage();
  if (citationRefreshState.running) {
    node.innerHTML = `<strong>${language === "zh" ? "引用量匹配中" : "Matching citations"}</strong><span>${citationRefreshState.completed}/${citationRefreshState.total} · ${language === "zh" ? `当前覆盖 ${coverage.matched}/${coverage.total}` : `coverage ${coverage.matched}/${coverage.total}`}</span>`;
    return;
  }
  const updated = citationCache.updatedAt ? new Date(citationCache.updatedAt).toLocaleDateString(language === "zh" ? "zh-CN" : "en-US") : (language === "zh" ? "尚未更新" : "not updated");
  node.innerHTML = `<strong>${CITATION_CONFIG.sourceName || "OpenAlex"}</strong><span>${language === "zh" ? `引用覆盖 ${coverage.matched}/${coverage.total} · 更新 ${updated}` : `${coverage.matched}/${coverage.total} citation matches · updated ${updated}`}</span>`;
}
function updateCitationCard(record) {
  const metadata = citationMetadata(record);
  if (!metadata) return;
  const card = document.getElementById(`ref-${record.slug || slugify(record.title)}`);
  if (!card) return;
  card.dataset.citations = String(metadata.citationCount ?? -1);
  const badge = card.querySelector(".citation-count");
  if (badge) {
    badge.classList.remove("citation-pending");
    badge.textContent = `${Number(metadata.citationCount || 0).toLocaleString(language === "zh" ? "zh-CN" : "en-US")} ${language === "zh" ? "次引用" : "citations"}`;
  }
  let note = card.querySelector(".citation-source-note");
  if (!note) {
    note = document.createElement("div");
    note.className = "citation-source-note";
    card.querySelector(".card-top")?.insertAdjacentElement("afterend", note);
  }
  note.textContent = `${language === "zh" ? "引用数据" : "Citation data"}: ${CITATION_CONFIG.sourceName || "OpenAlex"} · ${language === "zh" ? "匹配" : "match"} ${Math.round((metadata.matchScore || 0) * 100)}%`;
}
function signalFamily(record) {
  const text = `${record.signal || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
  if (/counterfactual|formal|test|verification|validity|unit test|sealed/.test(text)) return "verification/tests";
  if (/critic|critique|judge|evaluation|feedback|reflection/.test(text)) return "critique/evaluation";
  if (/environment|web|robot|embodied|interaction|exploration|world/.test(text)) return "environment interaction";
  if (/reward|reinforcement|rl|preference/.test(text)) return "scalar/preference reward";
  if (/self-play|population|tournament|quality-diversity|multi-agent/.test(text)) return "population/self-play";
  if (/memory|experience|trajectory|reuse|retrieval/.test(text)) return "experience reuse";
  return "self-generated artifact";
}
function mergeCatalog(primary, supplemental) {
  const map = new Map();
  [...primary, ...supplemental].forEach((item) => {
    const key = normalizeTitle(item.title);
    if (!key) return;
    const existing = map.get(key) || {};
    map.set(key, { ...existing, ...item, source: existing.source && item.source ? `${existing.source}+${item.source}` : (item.source || existing.source || "curated") });
  });
  return [...map.values()].sort((a, b) => (b.year || 0) - (a.year || 0) || a.title.localeCompare(b.title));
}
async function fetchCatalogMarkdown(source) {
  const failures = [];
  for (const url of source.urls) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 18000);
    try {
      const response = await fetch(url, { cache: "no-store", signal: controller.signal, headers: { "Accept": "text/plain, application/vnd.github+json" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (url.includes("api.github.com")) {
        const payload = await response.json();
        if (!payload.content) throw new Error("GitHub API response has no content");
        return decodeURIComponent(escape(atob(payload.content.replace(/\s/g, ""))));
      }
      return await response.text();
    } catch (error) {
      failures.push(`${url}: ${error.message || error}`);
    } finally {
      clearTimeout(timer);
    }
  }
  throw new Error(`${source.name}: ${failures.join(" | ")}`);
}
async function fetchSemanticScholarSnapshot() {
  try {
    const response = await fetch("generated/semantic-scholar-corpus.json", { cache: "no-store", headers: { "Accept": "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const siteRecords = Array.isArray(payload.site_records) ? payload.site_records : [];
    window.S2_LITERATURE_META = {
      schema_version: payload.schema_version,
      retrieved_at: payload.retrieved_at,
      provider: payload.provider,
      statistics: payload.statistics,
      seed_expansion: payload.seed_expansion,
    };
    return siteRecords;
  } catch (error) {
    console.warn("Semantic Scholar snapshot is unavailable; using the curated corpus.", error);
    return [];
  }
}
function indexCatalog(records) {
  return sortBibliographyRecords(records, "priority").map((record, index) => ({ ...record, refNo: index + 1, slug: slugify(record.title) })).map((record) => {
    citationIndex.set(normalizeTitle(record.title), record);
    return record;
  });
}
function refreshAfterCatalogUpdate() {
  if (pageId === "paper-ideas") {
    const root = document.getElementById("dynamic-page");
    if (root) hydrateCitations(root);
    updateCitationStatus();
    return;
  }
  updateCounter();
  renderPage();
}
async function loadCatalog() {
  citationIndex = new Map();
  catalog = indexCatalog(mergeCatalog([], DATA));
  refreshAfterCatalogUpdate();
  let upstream = [];
  let semanticScholar = [];
  try {
    const cached = JSON.parse(localStorage.getItem(CATALOG_CACHE_KEY) || "null");
    if (cached && Array.isArray(cached.records) && Date.now() - cached.savedAt < CATALOG_CACHE_MAX_AGE) {
      upstream = cached.records;
    } else {
      const batches = await Promise.all(CATALOG_SOURCES.map(async (source) => {
        try {
          const markdown = await fetchCatalogMarkdown(source);
          return source.parser === "frontis" ? parseFrontisMarkdown(markdown) : parseAwesomeMarkdown(markdown);
        } catch (error) {
          console.warn(error);
          return [];
        }
      }));
      upstream = batches.flat();
      localStorage.setItem(CATALOG_CACHE_KEY, JSON.stringify({ savedAt: Date.now(), records: upstream }));
    }
  } catch (error) {
    console.warn("Live literature synchronization failed; using curated snapshot.", error);
  }
  semanticScholar = await fetchSemanticScholarSnapshot();
  citationIndex = new Map();
  catalog = indexCatalog(mergeCatalog(upstream, [...semanticScholar, ...DATA]));
  refreshAfterCatalogUpdate();
}
function updateCounter(extra = "") {
  const counter = document.getElementById("result-count");
  if (!counter) return;
  const label = language === "zh" ? `${catalog.length || DATA.length} 篇论文${extra}` : `${catalog.length || DATA.length} papers${extra}`;
  counter.textContent = label;
}

function pageHeader(config) {
  return `<div class="eyebrow">${esc(textOf(config.eyebrow))}</div><h1>${textOf(config.title)}</h1><p class="lead">${textOf(config.lead)}</p>${config.callout ? `<div class="callout">${textOf(config.callout)}</div>` : ""}`;
}
function renderSectionForPage(section, index, citationPageId = pageId, extraClass = "", headingLevel = 2) {
  const title = textOf(section.title);
  const id = section.id || `${citationPageId}-${slugify(title || `section-${index + 1}`)}`;
  const citations = PAGE_CITATIONS[citationPageId]?.[index] || [];
  const referenceNote = citations.length ? `<div class="section-reference-note"><span>${language === "zh" ? "代表文献" : "Representative references"}</span><span data-cite="${esc(citations.join("||"))}"></span></div>` : "";
  const level = Math.min(4, Math.max(2, Number(headingLevel) || 2));
  return `<section class="panel topic-section ${esc(extraClass)}"><h${level} id="${id}">${title}</h${level}>${section.intro ? `<p class="section-intro">${textOf(section.intro)}</p>` : ""}<div class="section-body">${textOf(section.body)}${referenceNote}</div></section>`;
}
function renderSection(section, index) {
  return renderSectionForPage(section, index, pageId);
}
function sourceGroupAnchor(group) {
  return `group-${group.sourceId}`;
}
function renderGroupNav(groups = []) {
  if (!groups.length) return "";
  return `<nav class="merged-group-nav" aria-label="${language === "zh" ? "本章主题" : "Chapter topics"}">${groups.map((group, index) => `<a href="#${sourceGroupAnchor(group)}"><span>${index + 1}</span>${textOf(group.title || group.config?.title)}</a>`).join("")}</nav>`;
}
function renderMergedGroups(groups = []) {
  return groups.filter((group) => group?.config).map((group, groupIndex) => {
    const config = group.config;
    const sections = (config.sections || []).map((section, index) => renderSectionForPage(section, index, group.sourceId, "merged-topic-section", 4)).join("");
    return `<section class="merged-group" data-source-page="${esc(group.sourceId)}"><header class="merged-group-header"><div class="merged-group-number">${String(groupIndex + 1).padStart(2, "0")}</div><div><div class="eyebrow">${textOf(config.eyebrow || {en:"Topic",zh:"主题"})}</div><h3 id="${sourceGroupAnchor(group)}">${textOf(group.title || config.title)}</h3>${config.lead ? `<p>${textOf(config.lead)}</p>` : ""}${config.callout ? `<div class="merged-group-callout">${textOf(config.callout)}</div>` : ""}</div></header>${sections}</section>`;
  }).join("");
}
function pageArchitecture(page = pageId) {
  return (window.PAGE_ARCHITECTURES || {})[page] || {chapters:[]};
}
function renderArchitectureOverview(architecture = pageArchitecture()) {
  const chapters = architecture.chapters || [];
  if (!chapters.length) return "";
  return `<section class="panel page-architecture"><h2 id="page-framework">${language === "zh" ? "本页框架与阅读顺序" : "Page framework and reading order"}</h2><p class="section-intro">${language === "zh" ? "先理解各章解决的主问题，再进入方法族、任务域或具体子问题。箭头表示推荐阅读顺序，不表示严格因果关系。" : "Start with the main question of each chapter, then move to method families, domains, or concrete subproblems. Arrows indicate the recommended reading order rather than strict causality."}</p><div class="page-architecture-flow">${chapters.map((chapter, index) => `<a class="page-architecture-card" href="#chapter-${esc(chapter.id)}"><span>${String(index + 1).padStart(2,"0")}</span><div><b>${textOf(chapter.title)}</b><small>${textOf(chapter.question)}</small></div></a>`).join("<i>→</i>")}</div></section>`;
}
function renderPageChapter(chapter, chapterIndex, config) {
  const groups = chapter.groups || [];
  const overview = chapter.includeOverview && config.overviewFigure ? renderOverviewFigure(config, language === "zh" ? "Agent 自进化历史、能力、方向与代表方法总览" : "Agent self-evolution history, capabilities, directions, and representative methods") : "";
  const resources = (chapter.resourceModes || []).map((mode) => renderResourceIndexSection(mode, 3)).join("");
  return renderCustomChapter(chapter, chapterIndex, `${overview}${renderGroupNav(groups)}${renderMergedGroups(groups)}${resources}`);
}
function renderCustomChapter(chapter, chapterIndex, body) {
  return `<section class="page-chapter" data-chapter="${esc(chapter.id)}"><header class="page-chapter-header"><div class="page-chapter-number">${String(chapterIndex + 1).padStart(2,"0")}</div><div><h2 id="chapter-${esc(chapter.id)}">${textOf(chapter.title)}</h2><p>${textOf(chapter.question)}</p>${chapter.relation ? `<div class="page-chapter-relation"><b>${language === "zh" ? "框架关系" : "Framework relation"}</b>${textOf(chapter.relation)}</div>` : ""}</div></header>${body}</section>`;
}
function renderMergedHub(config) {
  const chapters = config.chapters || [];
  const fallbackOverview = !chapters.some((chapter) => chapter.includeOverview) && config.overviewFigure ? renderOverviewFigure(config) : "";
  return `${pageHeader(config)}${renderArchitectureOverview()}${fallbackOverview}${chapters.map((chapter, index) => renderPageChapter(chapter, index, config)).join("")}`;
}
function renderOverviewFigure(config, altText = "Agent self-evolution research map") {
  if (!config?.overviewFigure) return "";
  const src = textOf(config.overviewFigure.src);
  if (!src) return "";
  return `<figure class="overview-figure"><a href="${esc(src)}" target="_blank" rel="noopener"><img src="${esc(src)}" alt="${esc(altText)}"></a><figcaption><span>${textOf(config.overviewFigure.caption)}</span><a class="link-btn figure-source-link" href="${esc(src)}" target="_blank" rel="noopener">${language === "zh" ? "打开独立 SVG ↗" : "Open standalone SVG ↗"}</a></figcaption></figure>`;
}
function portfolioDirections() { return window.RESEARCH_DIRECTIONS || []; }
function portfolioIdeas() { return window.PAPER_IDEAS || []; }
function portfolioTracks() { return window.PAPER_TRACKS || []; }
function directionById(id) { return portfolioDirections().find((direction) => direction.id === id); }
function ideaByName(name) { return portfolioIdeas().find((idea) => idea.name === name); }
function ideaAnchor(name) { return `idea-${slugify(name)}`; }
function directionGuideData() { return window.DIRECTION_GUIDE || { macroGroups:[], directions:{} }; }
function directionGuide(id) { return directionGuideData().directions?.[id] || {}; }
function directionLiterature(id) { return (window.DIRECTION_LITERATURE || {})[id] || []; }
function directionPaperHref(title) { const slug = slugify(title); return `bibliography.html?paper=${encodeURIComponent(slug)}#ref-${slug}`; }
function renderDirectionLiterature(direction) {
  const papers = directionLiterature(direction.id);
  if (!papers.length) return "";
  const rows = papers.map((paper) => `<article class="direction-paper-evidence"><header><span data-cite="${esc(paper.title)}"></span><a href="${directionPaperHref(paper.title)}"><strong>${esc(paper.short || paper.title)}</strong></a><small>${esc(String(paper.year || ""))} · ${esc(paper.venue || "")}</small></header><p>${textOf(paper.method)}</p><div><b>${language === "zh" ? "方向关联" : "Why here"}</b>${textOf(paper.fit)}</div></article>`).join("");
  return `<section class="direction-literature"><h5>${language === "zh" ? "代表论文与一句话方法" : "Representative papers and one-line methods"}</h5><p class="direction-literature-note">${language === "zh" ? "这些论文用于支撑方向边界；点击论文名可进入完整六项论文梳理。" : "These papers ground the direction boundary; open a title for the full six-part analysis."}</p><div class="direction-paper-list">${rows}</div></section>`;
}
function renderDirectionCard(direction) {
  const directionIdeas = direction.ideaIds.map(ideaByName).filter(Boolean).sort((a, b) => a.rank - b.rank);
  const detail = directionGuide(direction.id);
  return `<article class="direction-card" style="--direction-color:${esc(direction.color || "#5b5bd6")}"><div class="direction-card-head"><span class="direction-code">${esc(direction.code)}</span><span class="direction-count">${directionIdeas.length} ${language === "zh" ? "个 Idea" : "ideas"}</span></div><h4 id="${esc(direction.id)}">${textOf(direction.title)}</h4><p class="direction-question">${textOf(direction.question)}</p><div class="direction-plain"><b>${language === "zh" ? "通俗理解" : "In plain language"}</b><span>${textOf(detail.plain)}</span></div><div class="direction-explanation-grid"><div><b>${language === "zh" ? "主要研究对象" : "Main object"}</b><p>${textOf(detail.object)}</p></div><div><b>${language === "zh" ? "典型例子" : "Typical example"}</b><p>${textOf(detail.example)}</p></div><div><b>${language === "zh" ? "与邻近方向的区别" : "Difference from neighbors"}</b><p>${textOf(detail.distinction)}</p></div><div><b>${language === "zh" ? "科学边界" : "Scientific boundary"}</b><p>${textOf(direction.boundary)}</p></div></div>${renderDirectionLiterature(direction)}<div class="idea-chip-list">${directionIdeas.map((idea) => `<a class="idea-chip" href="paper-ideas.html#${ideaAnchor(idea.name)}"><span>#${idea.rank}</span>${esc(idea.name)}</a>`).join("")}</div></article>`;
}
function renderDirectionMap(config) {
  const directions = portfolioDirections();
  const ideas = portfolioIdeas();
  const guide = directionGuideData();
  const chapters = pageArchitecture("research-directions").chapters || [];
  const macroCards = (guide.macroGroups || []).map((group) => `<article class="direction-macro-card"><span>${esc(group.code)}</span><h4>${textOf(group.title)}</h4><p>${textOf(group.plain)}</p><div>${(group.directionIds || []).map((id) => { const direction = directionById(id); return direction ? `<a href="#${esc(id)}">${esc(direction.code)} · ${textOf(direction.title)}</a>` : ""; }).join("")}</div></article>`).join("");
  const exampleRows = directions.map((direction) => { const detail = directionGuide(direction.id); return `<tr><th>${esc(direction.code)}</th><td><a href="#${esc(direction.id)}"><strong>${textOf(direction.title)}</strong></a><span>${textOf(detail.plain)}</span></td><td>${textOf(detail.example)}</td></tr>`; }).join("");
  const orientation = `<section class="panel direction-primer"><h3 id="four-big-questions">${language === "zh" ? "四个大问题" : "Four big questions"}</h3><p class="section-intro">${language === "zh" ? "十个方向不是十种互相竞争的方法，而是自进化生命周期中四类大问题的进一步拆分。" : "The ten directions are not ten competing methods. They decompose four large questions across the evolution lifecycle."}</p><div class="direction-macro-grid">${macroCards}</div></section><section class="panel direction-running-example"><h3 id="running-example">${textOf(guide.runningExample?.title)}</h3><p class="section-intro">${textOf(guide.runningExample?.intro)}</p><div class="history-table-scroll"><table class="matrix"><thead><tr><th>ID</th><th>${language === "zh" ? "这个方向在研究什么" : "What the direction studies"}</th><th>${language === "zh" ? "在这个案例中会问什么" : "Question in this example"}</th></tr></thead><tbody>${exampleRows}</tbody></table></div></section>${(config.sections || []).map((section, index) => renderSectionForPage(section, index, pageId, "direction-foundation-section", 3)).join("")}`;
  const stats = `<div class="grid direction-stats"><div class="stat"><b>${directions.length}</b><span>${language === "zh" ? "个研究方向" : "research directions"}</span></div><div class="stat"><b>${ideas.length}</b><span>${language === "zh" ? "个具体论文 Idea" : "concrete paper ideas"}</span></div><div class="stat"><b>${portfolioTracks().length}</b><span>${language === "zh" ? "类论文赛道" : "paper tracks"}</span></div></div>`;
  const landscape = `${renderOverviewFigure(config, language === "zh" ? "Agent 自进化研究方向与论文 Idea 地图" : "Agent self-evolution direction and paper-idea map")}${stats}`;
  const clusters = (guide.macroGroups || []).map((group, index) => { const groupDirections = (group.directionIds || []).map(directionById).filter(Boolean); return `<section class="direction-cluster"><header><span>${esc(group.code)}</span><div><h3 id="direction-cluster-${esc(group.id)}">${textOf(group.title)}</h3><p>${textOf(group.plain)}</p></div></header><div class="direction-grid">${groupDirections.map(renderDirectionCard).join("")}</div></section>`; }).join("");
  const agendaGroups = config.groupsAfter || [];
  const agenda = `${renderGroupNav(agendaGroups)}${renderMergedGroups(agendaGroups)}`;
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("research-directions"))}${renderCustomChapter(chapters[0],0,orientation)}${renderCustomChapter(chapters[1],1,landscape)}${renderCustomChapter(chapters[2],2,clusters)}${renderCustomChapter(chapters[3],3,agenda)}`;
}
function ideaExplanation(name) { return (window.IDEA_EXPLANATIONS || {})[name] || {}; }
function ideaComparison(name) { return (window.IDEA_COMPARISONS || {})[name] || {}; }
function ideaPipelineMeta() { return window.IDEA_PIPELINE_META || {funnel:[],operators:[],reviewers:[],advisorShortlist:[],stages:{},warnings:[]}; }
function advisorIdeaNames() { return new Set(ideaPipelineMeta().advisorShortlist || []); }
function ideaIsVisual(idea) {
  const direction = directionById(idea.directionId);
  const value = `${textOf(idea.track)} ${idea.directionId} ${textOf(direction?.boundary || {})}`.toLowerCase();
  return /visual|cvpr|multimodal|embodied|vision|视觉|具身/.test(value);
}
function ideaDecisionState(idea) {
  const meta = ideaPipelineMeta();
  let stage = "review";
  if (idea.name === meta.selectedIdea) stage = "selected";
  else if ((meta.advisorShortlist || []).includes(idea.name) && idea.confidence === "H" && ideaIsVisual(idea)) stage = "collision-check";
  else if (!(meta.advisorShortlist || []).includes(idea.name) && idea.confidence === "L") stage = "archived";
  const stageMeta = meta.stages?.[stage] || {label:{en:stage,zh:stage},tone:"review"};
  const decision = stage === "selected" ? "advance" : stage === "archived" ? "hold" : "investigate";
  return {stage,decision,tone:stageMeta.tone || "review",label:textOf(stageMeta.label || {en:stage,zh:stage})};
}
function renderIdeaBackendArchitecture() {
  const stages = language === "zh" ? [
    ["01","检索规划","主题、引用、失败模式、机制与跨领域五路查询"],
    ["02","证据图谱","论文六项卡、Claim–Evidence、引用邻域与概念实体"],
    ["03","空缺实验室","限制、矛盾、假设、缺失单元与目标—评测错位"],
    ["04","受控生成","一次只应用一个 Idea 算子，并保留父节点与生成理由"],
    ["05","碰撞检索","分别检查相同问题、机制、组合和实验设计"],
    ["06","ICLR 独立评审","真实进化、机制、归因、稳定性、圈外泛化、反馈完整性与等预算复现分别审查"],
    ["07","最小证伪","先跑能推翻 Idea 的 Pilot，再决定是否开发完整方法"],
    ["08","导师决策","只展示短名单、未决证据、资源需求与 Go／Stop"],
  ] : [
    ["01","Query planning","Topic, citation, failure-mode, mechanism, and cross-domain searches"],
    ["02","Evidence graph","Six-part paper cards, claim–evidence links, citations, and entities"],
    ["03","Gap laboratory","Limitations, contradictions, assumptions, missing cells, and metric mismatch"],
    ["04","Controlled generation","Apply one named operator and preserve its parent evidence and rationale"],
    ["05","Collision search","Check the same problem, mechanism, combination, and experiment separately"],
    ["06","ICLR review","Persistent learning, mechanism, attribution, stability, out-of-loop generalization, feedback integrity, and matched-budget reproducibility are reviewed separately"],
    ["07","Minimal falsification","Run the pilot most capable of disproving the idea before full development"],
    ["08","Advisor decision","Expose only shortlist, missing evidence, resource needs, and Go/Stop"],
  ];
  return `<section class="panel"><h3 id="backend-pipeline-architecture">${language === "zh" ? "后端架构：从论文到可立项 Idea" : "Backend architecture: from papers to project-ready ideas"}</h3><p class="section-intro">${language === "zh" ? "每一阶段都有独立输入、输出和阻断条件；生成 Agent 无权直接把 Idea 标记为通过。" : "Every stage has explicit inputs, outputs, and blocking conditions. A generation agent cannot directly mark an idea as accepted."}</p><div class="idea-backend-flow">${stages.map(([code,title,desc]) => `<article><span>${code}</span><div><b>${title}</b><p>${desc}</p></div></article>`).join("")}</div></section>`;
}
function renderIdeaFunnel() {
  const stages = ideaPipelineMeta().funnel || [];
  return `<section class="panel idea-pipeline-panel"><div class="idea-panel-heading"><div><h3 id="candidate-funnel">${language === "zh" ? "候选漏斗：发散生成与收敛筛选分离" : "Candidate funnel: separate generation from selection"}</h3><p class="section-intro">${language === "zh" ? "后端保留高召回候选，但只有通过结构完整性、文献碰撞、独立评审和有界 Pilot 的方案才进入资源决策。" : "The backend keeps a high-recall pool, but only candidates that pass structural completeness, literature collision, independent review, and a bounded pilot enter resource allocation."}</p></div><span class="architecture-version">${esc(ideaPipelineMeta().architectureVersion || "")}</span></div><div class="idea-funnel">${stages.map((stage,index) => `<article class="idea-funnel-stage"><span>${String(index + 1).padStart(2,"0")}</span><strong>${stage.count}</strong><b>${textOf(stage.label)}</b><small>${textOf(stage.desc)}</small></article>`).join("<i>→</i>")}</div></section>`;
}
function renderIdeaOperators() {
  const operators = ideaPipelineMeta().operators || [];
  return `<section class="panel"><h3 id="idea-generation-operators">${language === "zh" ? "八类受控 Idea 生成算子" : "Eight controlled idea-generation operators"}</h3><p class="section-intro">${language === "zh" ? "每次只应用一个命名算子，并记录它使用了哪类文献证据，避免无约束脑暴和模块拼接。" : "Each proposal applies one named operator and records the evidence it used, avoiding unconstrained brainstorming and module stacking."}</p><div class="idea-operator-grid">${operators.map((operator,index) => `<article><span>${index + 1}</span><div><b>${textOf(operator.name)}</b><p>${textOf(operator.question)}</p></div></article>`).join("")}</div></section>`;
}
function renderReviewerPipeline() {
  const reviewers = ideaPipelineMeta().reviewers || [];
  return `<section class="panel"><h3 id="independent-review-gates">${language === "zh" ? "独立 Reviewer 门槛" : "Independent reviewer gates"}</h3><p class="section-intro">${language === "zh" ? "Reviewer 不是共同润色同一个答案，而是分别寻找能够阻断立项的证据；每项质疑都必须转成可执行补充实验或停止条件。" : "Reviewers do not jointly polish one answer. Each searches for evidence that can block the project, and every objection must become an executable test or Stop condition."}</p><div class="reviewer-gate-grid">${reviewers.map((reviewer) => `<article><span>${esc(reviewer.key.slice(0,2).toUpperCase())}</span><div><b>${textOf(reviewer.name)}</b><p>${textOf(reviewer.question)}</p></div></article>`).join("")}</div></section>`;
}
function ideaGateStatus(idea, key) {
  const selected = idea.name === ideaPipelineMeta().selectedIdea;
  if (key === "novelty") return selected ? "pass" : "pending";
  if (key === "scientific") return idea.confidence === "L" ? "revise" : "pass";
  if (key === "experiment") return idea.rank <= 20 ? "pass" : "revise";
  if (key === "feasibility") return idea.confidence === "H" || selected ? "pass" : "revise";
  if (key === "venue") return ideaIsVisual(idea) ? "pass" : "revise";
  return "pending";
}
function renderIdeaGateStrip(idea) {
  const labels = language === "zh" ? {novelty:"碰撞",scientific:"成立性",experiment:"主表",feasibility:"Pilot",venue:"ICLR"} : {novelty:"Collision",scientific:"Validity",experiment:"Main table",feasibility:"Pilot",venue:"ICLR"};
  return `<div class="idea-gate-strip">${Object.keys(labels).map((key) => { const status = ideaGateStatus(idea,key); return `<span class="gate-${status}"><i>${status === "pass" ? "✓" : status === "pending" ? "?" : "!"}</i>${labels[key]}</span>`; }).join("")}</div>`;
}
function renderIdeaEvidenceNeighborhood(idea) {
  const papers = directionLiterature(idea.directionId).slice(0,3);
  const comparison = ideaComparison(idea.name);
  if (!papers.length) return `<div class="idea-evidence-empty">${language === "zh" ? "尚未绑定直接近邻论文。" : "No direct neighboring papers are bound yet."}</div>`;
  return `<div class="idea-evidence-list">${papers.map((paper) => `<article><header><span data-cite="${esc(paper.title)}"></span><a href="${directionPaperHref(paper.title)}"><b>${esc(paper.short || paper.title)}</b></a><small>${esc(String(paper.year || ""))} · ${esc(paper.venue || "")}</small></header><p>${textOf(paper.method)}</p></article>`).join("")}</div><div class="idea-collision-note"><b>${language === "zh" ? "待核验的精确差异" : "Exact difference still to verify"}</b><span>${textOf(comparison.advantage)}</span></div>`;
}
function renderAdvisorDecisionTable(ideas) {
  const rows = ideas.map((idea) => {
    const state = ideaDecisionState(idea);
    const explanation = ideaExplanation(idea.name);
    const comparison = ideaComparison(idea.name);
    return `<tr class="idea-filter-target" data-idea-stage="${esc(state.stage)}" data-idea-track="${ideaIsVisual(idea) ? "visual" : "general"}"><td><span class="idea-stage-badge tone-${esc(state.tone)}">${esc(state.label)}</span></td><td><a href="#${ideaAnchor(idea.name)}"><strong>${esc(idea.name)}</strong></a><small>${textOf(idea.thesis)}</small></td><td>${textOf(explanation.purpose)}</td><td>${textOf(explanation.core)}</td><td>${textOf(comparison.advantage)}</td><td>${textOf(idea.go)}</td></tr>`;
  }).join("");
  return `<div class="advisor-table-scroll"><table class="matrix advisor-decision-table"><thead><tr><th>${language === "zh" ? "阶段" : "Stage"}</th><th>Idea</th><th>${language === "zh" ? "要解决的问题" : "Problem"}</th><th>${language === "zh" ? "核心机制" : "Core mechanism"}</th><th>${language === "zh" ? "相对优势" : "Comparative advantage"}</th><th>${language === "zh" ? "Go 证据" : "Go evidence"}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}
function renderAdvisorBoard(ideas) {
  const meta = ideaPipelineMeta();
  const filters = [
    ["all",language === "zh" ? "全部短名单" : "All shortlist"],
    ["selected",language === "zh" ? "已选中" : "Selected"],
    ["collision-check",language === "zh" ? "待新颖性核验" : "Novelty check"],
    ["review",language === "zh" ? "待 Reviewer 判断" : "Reviewer check"],
    ["visual",language === "zh" ? "CVPR 后续视觉方向" : "CVPR visual follow-up"],
  ];
  return `<section class="panel advisor-board"><div class="idea-panel-heading"><div><h3 id="advisor-comparison-board">${language === "zh" ? "师兄与老师横向决策板" : "Advisor comparison board"}</h3><p class="section-intro">${language === "zh" ? "先横向比较问题、机制、优势和决定性证据，再打开下方完整论证卡。这里的阶段是资源决策，不是论文质量结论。" : "Compare the problem, mechanism, advantage, and decisive evidence first, then open the full dossiers below. Stages are resource decisions, not paper-quality claims."}</p></div><strong>${ideas.length} ${language === "zh" ? "个优先候选" : "priority candidates"}</strong></div><div class="idea-board-filters">${filters.map(([key,label],index) => `<button class="idea-board-filter ${index === 0 ? "active" : ""}" data-idea-filter="${key}">${label}</button>`).join("")}</div>${renderAdvisorDecisionTable(ideas)}${(meta.warnings || []).map((warning) => `<div class="idea-board-warning">${textOf(warning)}</div>`).join("")}</section>`;
}
function renderAdvisorDossier(idea, index) {
  const direction = directionById(idea.directionId);
  const explanation = ideaExplanation(idea.name);
  const comparison = ideaComparison(idea.name);
  const state = ideaDecisionState(idea);
  return `<details class="idea-dossier idea-filter-target" id="${ideaAnchor(idea.name)}" data-idea-stage="${esc(state.stage)}" data-idea-track="${ideaIsVisual(idea) ? "visual" : "general"}" ${index < 3 ? "open" : ""}><summary><div><span class="idea-stage-badge tone-${esc(state.tone)}">${esc(state.label)}</span><b>${esc(idea.name)}</b><small>${direction ? `${esc(direction.code)} · ${textOf(direction.title)}` : ""}</small></div><p>${textOf(idea.thesis)}</p></summary><div class="idea-dossier-body">${renderIdeaGateStrip(idea)}<div class="idea-dossier-grid"><section><h4 data-toc="false">${language === "zh" ? "1 · 目的／要解决的问题" : "1 · Purpose / problem"}</h4><p>${textOf(explanation.purpose)}</p></section><section><h4 data-toc="false">${language === "zh" ? "2 · 核心思想" : "2 · Core idea"}</h4><p>${textOf(explanation.core)}</p></section><section><h4 data-toc="false">${language === "zh" ? "3 · 为什么合理" : "3 · Why it is reasonable"}</h4><p>${textOf(explanation.rationale)}</p></section><section><h4 data-toc="false">${language === "zh" ? "4 · 方法逻辑" : "4 · Method logic"}</h4><p>${textOf(explanation.logic)}</p></section><section><h4 data-toc="false">${language === "zh" ? "5 · 研究重要性" : "5 · Research importance"}</h4><p>${textOf(comparison.importance)}</p></section><section><h4 data-toc="false">${language === "zh" ? "6 · 相对优势" : "6 · Comparative advantage"}</h4><p>${textOf(comparison.advantage)}</p></section></div><div class="idea-decision-evidence"><section><h4 data-toc="false">${language === "zh" ? "最近论文与碰撞边界" : "Nearest literature and collision boundary"}</h4>${renderIdeaEvidenceNeighborhood(idea)}</section><section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><dl><dt>${language === "zh" ? "最小实验" : "Minimum experiment"}</dt><dd>${textOf(idea.experiment)}</dd><dt>${language === "zh" ? "最强对照" : "Strongest comparison"}</dt><dd>${textOf(idea.baseline)}</dd><dt>Go</dt><dd>${textOf(idea.go)}</dd><dt>Stop</dt><dd>${textOf(idea.stop)}</dd></dl></section></div><div class="idea-unresolved-risk"><b>${language === "zh" ? "当前最关键未决风险" : "Most important unresolved risk"}</b><span>${textOf(idea.stop)}</span></div></div></details>`;
}
function renderShortlistDossiers(ideas) {
  return `<section class="shortlist-dossiers"><div class="shortlist-intro"><h3 id="advisor-shortlist-dossiers">${language === "zh" ? "逐个 Idea 完整论证卡" : "Complete evidence dossier for each idea"}</h3><p>${language === "zh" ? "默认展开前三项；其余候选按需打开。所有“优势”均是待实验验证的条件性优势。" : "The first three are expanded by default. Every stated advantage is conditional and remains to be tested."}</p></div>${ideas.map(renderAdvisorDossier).join("")}</section>`;
}
function renderCandidateArchive(ideas) {
  const shortlist = advisorIdeaNames();
  const directionSections = portfolioDirections().map((direction) => {
    const rows = direction.ideaIds.map(ideaByName).filter(Boolean).sort((a,b) => a.rank - b.rank);
    const content = rows.map((idea) => shortlist.has(idea.name) ? `<a class="archive-shortlist-link" href="#${ideaAnchor(idea.name)}"><span>${language === "zh" ? "短名单" : "Shortlist"}</span><b>${esc(idea.name)}</b><small>#${idea.rank} · ${esc(idea.confidence)}</small></a>` : renderIdeaPlanCard(idea)).join("");
    return `<details class="idea-archive-direction"><summary><div><span>${esc(direction.code)}</span><b>${textOf(direction.title)}</b></div><small>${rows.length} ${language === "zh" ? "个 Idea" : "ideas"}</small></summary><div class="idea-archive-body">${content}</div></details>`;
  }).join("");
  return `<section class="panel"><h3 id="complete-candidate-archive">${language === "zh" ? "34 个保留 Idea 完整归档" : "Complete archive of 34 retained ideas"}</h3><p class="section-intro">${language === "zh" ? "短名单之外的候选仍完整保留，避免一次筛选永久丢失潜在线索。旧排名和小数分数仅用于追溯历史决策，不直接决定是否立项。" : "Candidates outside the shortlist remain fully preserved so one selection round does not destroy useful branches. Legacy ranks and decimal scores are traceability metadata only."}</p>${directionSections}</section>${renderIdeaRankingPanels()}`;
}
function renderIdeaPlanCard(idea) {
  const direction = directionById(idea.directionId);
  const explanation = ideaExplanation(idea.name);
  const comparison = ideaComparison(idea.name);
  const state = ideaDecisionState(idea);
  return `<article class="idea-plan-card" id="${ideaAnchor(idea.name)}"><div class="idea-card-top"><div><span class="idea-stage-badge tone-${esc(state.tone)}">${esc(state.label)}</span><h5>${esc(idea.name)}</h5><a class="idea-direction-link" href="research-directions.html#${esc(idea.directionId)}">${direction ? `${esc(direction.code)} · ${textOf(direction.title)}` : ""}</a></div><div class="idea-legacy-trace"><b>#${idea.rank}</b><span>${language === "zh" ? "旧排序" : "legacy rank"} · ${idea.score.toFixed(1)} · ${esc(idea.confidence)}</span></div></div><div class="idea-section-title">${language === "zh" ? "研究论证" : "Research argument"}</div><div class="idea-plan-grid idea-argument-grid"><div><b>${language === "zh" ? "目的／要解决的问题" : "Purpose / problem"}</b><p>${textOf(explanation.purpose)}</p></div><div><b>${language === "zh" ? "核心思想" : "Core idea"}</b><p>${textOf(explanation.core)}</p></div><div><b>${language === "zh" ? "合理性" : "Why it is reasonable"}</b><p>${textOf(explanation.rationale)}</p></div><div><b>${language === "zh" ? "方法逻辑" : "Method logic"}</b><p>${textOf(explanation.logic)}</p></div><div><b>${language === "zh" ? "研究重要性" : "Why it matters"}</b><p>${textOf(comparison.importance)}</p></div><div><b>${language === "zh" ? "相对优势" : "Comparative advantage"}</b><p>${textOf(comparison.advantage)}</p></div></div><div class="idea-section-title">${language === "zh" ? "实验验证" : "Validation plan"}</div><div class="idea-plan-grid"><div><b>${language === "zh" ? "最小实验" : "Minimum experiment"}</b><p>${textOf(idea.experiment)}</p></div><div><b>${language === "zh" ? "最强对照" : "Strongest comparison"}</b><p>${textOf(idea.baseline)}</p></div><div><b>Go</b><p>${textOf(idea.go)}</p></div><div><b>Stop</b><p>${textOf(idea.stop)}</p></div><div><b>${language === "zh" ? "最适赛道" : "Best track"}</b><p>${textOf(idea.track)} · ${language === "zh" ? `证据置信度 ${idea.confidence}` : `${idea.confidence} evidence confidence`}</p></div><div><b>${language === "zh" ? "一句话命题" : "One-line thesis"}</b><p>${textOf(idea.thesis)}</p></div></div></article>`;
}
function renderIdeaRankingPanels() {
  const ideas = [...portfolioIdeas()].sort((a, b) => a.rank - b.rank);
  const directions = portfolioDirections();
  const globalRows = ideas.map((idea) => { const direction = directionById(idea.directionId); return `<tr><td><strong>${idea.rank}</strong></td><td><a href="#${ideaAnchor(idea.name)}"><strong>${esc(idea.name)}</strong></a></td><td>${direction ? `${esc(direction.code)} · ${textOf(direction.title)}` : ""}</td><td>${idea.score.toFixed(1)}</td><td>${esc(idea.confidence)}</td><td>${textOf(idea.track)}</td></tr>`; }).join("");
  const withinDirections = directions.map((direction) => { const directionIdeas = direction.ideaIds.map(ideaByName).filter(Boolean).sort((a, b) => a.rank - b.rank); return `<article class="direction-rank-card"><h4>${esc(direction.code)} · ${textOf(direction.title)}</h4><ol>${directionIdeas.map((idea) => `<li><a href="#${ideaAnchor(idea.name)}">${esc(idea.name)}</a><span>#${idea.rank} · ${idea.score.toFixed(1)}</span></li>`).join("")}</ol></article>`; }).join("");
  const tracks = portfolioTracks().map((track) => `<article class="track-rank-card"><h4>${textOf(track.title)}</h4><ol>${track.ideaNames.map((name, index) => { const idea = ideaByName(name); return idea ? `<li><span>${index + 1}</span><a href="#${ideaAnchor(idea.name)}">${esc(idea.name)}</a><small>#${idea.rank}</small></li>` : ""; }).join("")}</ol></article>`).join("");
  return `<section class="panel" id="idea-ranking"><h3 id="global-idea-ranking">${language === "zh" ? "论文 Idea 总榜" : "Global paper-idea ranking"}</h3><p class="section-intro">${language === "zh" ? "总榜用于跨方向资源决策；方向内排序和赛道榜用于选择真正可执行的下一篇论文。" : "The global table supports cross-direction resource decisions; within-direction and track rankings are better for selecting the next executable paper."}</p><table class="matrix comparison-table"><thead><tr><th>${language === "zh" ? "排名" : "Rank"}</th><th>Idea</th><th>${language === "zh" ? "研究方向" : "Research direction"}</th><th>${language === "zh" ? "得分" : "Score"}</th><th>${language === "zh" ? "置信度" : "Conf."}</th><th>${language === "zh" ? "最适赛道" : "Best track"}</th></tr></thead><tbody>${globalRows}</tbody></table></section><section class="panel"><h3 id="within-direction-ranking">${language === "zh" ? "方向内排序" : "Within-direction ranking"}</h3><p class="section-intro">${language === "zh" ? "这比跨方向总榜更适合决定同一个科学问题下先做哪个论文方案。" : "This view is more useful than the global table when choosing among papers that answer the same scientific question."}</p><div class="direction-rank-grid">${withinDirections}</div></section><section class="panel"><h3 id="track-ranking">${language === "zh" ? "按论文赛道排序" : "Track-specific ranking"}</h3><div class="track-rank-grid">${tracks}</div></section>`;
}
function researchSystemState() {
  return window.RESEARCH_SYSTEM_STATE || {summary:{},health:{status:"unknown",checks:[]},components:[],collision_engine:{summary:{},pairs:[]},pilot_registry:{summary:{},ideas:[]},repair_queue:{summary:{},queue:[]}};
}
function renderResearchSystemState() {
  const state = researchSystemState();
  const summary = state.summary || {};
  const health = state.health || {};
  const componentStatus = (value) => ({running:{zh:"运行中",en:"running"},"intentionally-disabled":{zh:"有意禁用",en:"intentionally disabled"}}[value]?.[language] || value || "unknown");
  const componentRows = (state.components || []).map((item) => `<article class="automation-component tone-${esc(item.status)}"><header><b>${esc(item.source)}</b><span>${esc(componentStatus(item.status))}</span></header><h4 data-toc="false">${esc(textOf(item.component))}</h4><p>${esc(textOf(item.evidence))}</p></article>`).join("");
  const collisionRows = ((state.collision_engine || {}).pairs || []).slice(0,8).map((pair) => `<tr><td>${esc(pair.left_id)}</td><td>${esc(pair.right_id)}</td><td><span class="collision-relation">${esc(pair.relation)}</span></td><td>${Number(pair.scores?.hybrid || 0).toFixed(3)}</td><td>${esc(pair.recommended_action)}</td></tr>`).join("");
  const repairRows = ((state.repair_queue || {}).queue || []).slice(0,6).map((item) => `<li><div><b>${textOf(item.title)}</b><small>${esc(item.source)} · ${esc(item.current_status || "")}</small></div><span>${(item.recommended_repairs || []).map((repair) => esc(repair.operator)).join(" / ")}</span></li>`).join("");
  const pilot = (state.pilot_registry || {}).summary || {};
  const automation = state.automation || {};
  const latestCycle = automation.latest_report || {};
  return `<section class="panel automation-system-panel"><div class="idea-panel-heading"><div><h3 id="automatic-research-system">${language === "zh" ? "全自动研究后端：证据、碰撞、谱系与实验回流" : "Autonomous research backend: evidence, collisions, lineage, and experiment feedback"}</h3><p class="section-intro">${language === "zh" ? "该面板显示系统真实运行的组件，而不是规划图。自动化可以生成候选、发现碰撞、建立谱系、排队修订并接收 Pilot 结果，但不能在没有实验或可追溯证据时自动选中论文。" : "This panel reports components that actually ran, not planned architecture. Automation may generate candidates, detect collisions, preserve lineage, queue repairs, and ingest pilot results, but it cannot select a paper without traceable evidence or experiments."}</p></div><strong class="system-health health-${esc(health.status || "unknown")}">${language === "zh" ? "系统状态" : "System"}: ${esc(health.status || "unknown")}</strong></div><div class="grid automation-stats"><div class="stat"><b>${summary.papers || 0}</b><span>${language === "zh" ? "篇检索论文" : "retrieved papers"}</span></div><div class="stat"><b>${summary.evidence_nodes || 0}</b><span>${language === "zh" ? "个证据节点" : "evidence nodes"}</span></div><div class="stat"><b>${summary.evidence_edges || 0}</b><span>${language === "zh" ? "条证据边" : "evidence edges"}</span></div><div class="stat"><b>${summary.collision_flags || 0}</b><span>${language === "zh" ? "个碰撞标记" : "collision flags"}</span></div><div class="stat"><b>${summary.lineage_edges || 0}</b><span>${language === "zh" ? "条谱系边" : "lineage edges"}</span></div><div class="stat"><b>${summary.repair_queue || 0}</b><span>${language === "zh" ? "个修复队列项" : "repair queue items"}</span></div></div><div class="automation-component-grid">${componentRows}</div><div class="automation-detail-grid"><section><h4 data-toc="false">${language === "zh" ? "混合语义碰撞：最高风险 Pair" : "Hybrid semantic collisions: highest-risk pairs"}</h4><div class="advisor-table-scroll"><table class="matrix automation-collision-table"><thead><tr><th>Idea A</th><th>Idea B</th><th>${language === "zh" ? "关系" : "Relation"}</th><th>${language === "zh" ? "分数" : "Score"}</th><th>${language === "zh" ? "动作" : "Action"}</th></tr></thead><tbody>${collisionRows}</tbody></table></div></section><section><h4 data-toc="false">${language === "zh" ? "自动修订队列" : "Automatic repair queue"}</h4><ul class="automation-repair-list">${repairRows}</ul></section></div><div class="automation-pilot-status"><b>${language === "zh" ? "Pilot 结果回流" : "Pilot result feedback"}</b><span>${pilot.phases || 0} ${language === "zh" ? "个已注册阶段" : "registered phases"} · ${pilot.valid_result_files || 0} ${language === "zh" ? "个真实结果" : "executed results"} · ${pilot.invalid_result_files || 0} ${language === "zh" ? "个无效结果文件" : "invalid result files"}</span><small>${language === "zh" ? "P0/P1/P2 结果写入服务器 registry 后，将自动改变 Idea 的 planned / revise / pilot-ready / selected-ready / stop 状态。" : "Once P0/P1/P2 results enter the server registry, idea state automatically changes among planned, revise, pilot-ready, selected-ready, and stop."}</small></div><div class="automation-schedule"><b>${language === "zh" ? "持续运行计划" : "Continuous schedule"}</b><span>${language === "zh" ? `每日 ${esc(automation.daily?.schedule || "--")}：离线重建；每周 ${esc(automation.weekly?.schedule || "--")}：文献同步与最多两个修订审查。` : `Daily ${esc(automation.daily?.schedule || "--")}: offline rebuild; weekly ${esc(automation.weekly?.schedule || "--")}: literature sync and at most two repair reviews.`}</span><small>${latestCycle.status ? `${language === "zh" ? "最近周期" : "Latest cycle"}: ${esc(latestCycle.status)} · ${esc(latestCycle.completed_at || latestCycle.started_at || "")}` : (language === "zh" ? "尚未读取服务器周期报告。" : "No server cycle report is loaded yet.")}</small></div></section>`;
}
function iclrIdeaBank() {
  return window.ICLR_LOW_RESOURCE_IDEAS || {summary:{raw_candidates:0,passed:0,early_rejected:0,tracks:0},policy:{},tracks:{},passed_ideas:[],blocked_ideas:[],early_rejected:[],iclr_review_dimensions:[]};
}
function iclrExperimentAudit() {
  return window.ICLR_EXPERIMENT_AUDIT || {summary:{papers:0},papers:[]};
}
function renderIclrReviewDimensions() {
  const dimensions = iclrIdeaBank().iclr_review_dimensions || [];
  return `<section class="panel iclr-review-dimensions"><h3 id="iclr-review-dimensions">${language === "zh" ? "ICLR 七个立项审查维度" : "Seven ICLR project-review dimensions"}</h3><p class="section-intro">${language === "zh" ? "视觉不可替代性不再是硬门槛；核心改为学习是否真实持久、机制是否明确、更新是否可归因、稳定、圈外泛化、反馈可靠且等预算可复现。" : "Visual necessity is no longer a hard gate. The primary questions are persistent learning, mechanistic specificity, attribution, stability, out-of-loop generalization, feedback integrity, and matched-budget reproducibility."}</p><div class="reviewer-gate-grid iclr-dimension-grid">${dimensions.map((item,index) => `<article><span>${index + 1}</span><div><b>${textOf(item.label)}</b><p>${textOf(item.question)}</p></div></article>`).join("")}</div></section>`;
}
function renderIclrExperimentAudit() {
  const audit = iclrExperimentAudit();
  const rows = (audit.papers || []).map((paper) => `<tr><td><a href="${esc(paper.source)}" target="_blank" rel="noopener"><strong>${esc(paper.title)}</strong></a><small>${esc(paper.venue)}</small></td><td><span class="substrate-badge">${esc(substrateLabel(paper.substrate))}</span><p>${esc(textOf(paper.actor))}</p></td><td><p>${esc(textOf(paper.api_role))}</p></td><td><p>${esc(textOf(paper.parameter_updates))}</p></td><td><p>${esc(textOf(paper.data))}</p><small>${esc(textOf(paper.hardware))}</small></td><td><span class="verification-badge">${esc(verificationLabel(paper.verification))}</span><p>${textOf(paper.implication)}</p></td></tr>`).join("");
  return `<section class="panel published-audit-panel iclr-audit-panel"><div class="idea-panel-heading"><div><h3 id="iclr-experiment-substrate-audit">${language === "zh" ? "ICLR 已发表 Agent 学习论文：模型、API 与训练基座审计" : "Published ICLR agent-learning papers: model, API, and training substrate audit"}</h3><p class="section-intro">${language === "zh" ? "覆盖 Retroformer、AFlow、WebRL、SCoRe、自进化 Reward、WorfBench、世界模型 Web Agent 与 AgentRefine 等直接基线。商业 API、开放权重、参数训练、搜索调用和外部工具分别报告。" : "Covers direct baselines including Retroformer, AFlow, WebRL, SCoRe, self-evolved rewards, WorfBench, world-model web agents, and AgentRefine. Proprietary APIs, open weights, parameter training, search calls, and external tools are reported separately."}</p></div><strong>${audit.summary?.papers || 0} ${language === "zh" ? "篇 ICLR 论文" : "ICLR papers"}</strong></div><div class="advisor-table-scroll"><table class="matrix published-audit-table"><thead><tr><th>${language === "zh" ? "论文" : "Paper"}</th><th>${language === "zh" ? "模型／基座" : "Model / substrate"}</th><th>${language === "zh" ? "API 角色" : "API role"}</th><th>${language === "zh" ? "更新对象" : "Updated object"}</th><th>${language === "zh" ? "数据与资源" : "Data and resources"}</th><th>${language === "zh" ? "对当前方案的启示" : "Implication for our design"}</th></tr></thead><tbody>${rows}</tbody></table></div><div class="published-audit-conclusion"><b>${language === "zh" ? "ICLR 基座结论" : "ICLR substrate conclusion"}</b><span>${textOf(audit.summary?.primary_recommendation || {})}</span></div></section>`;
}
function renderIclrIdeaCard(idea, index) {
  const budget = idea.budget || {};
  const reviews = idea.reviews || [];
  const externalReviews = idea.external_reviews || [];
  const externalVerdict = idea.external_verdict || "pending";
  const externalLabel = externalVerdict === "pass" ? "PASS" : externalVerdict === "revise" ? "REVISE" : externalVerdict === "block" ? "BLOCK" : "PENDING";
  return `<details class="cvpr-idea-card iclr-idea-card iclr-filter-target verdict-${esc(externalVerdict)}" data-iclr-track="${esc(idea.track_id || "")}" data-iclr-gpu-hours="${Number(budget.gpu_hours || 0)}" data-external-verdict="${esc(externalVerdict)}" ${index < 5 ? "open" : ""}><summary><div><span class="cvpr-rank">#${idea.rank}</span><b>${textOf(idea.title)}</b><small>${language === "zh" ? `R1 原排名 #${idea.programmatic_rank || idea.rank}` : `R1 rank #${idea.programmatic_rank || idea.rank}`} · ${textOf(idea.track)} · ${(idea.domains || []).map(esc).join(" / ")}</small></div><div class="cvpr-budget"><span class="external-verdict-badge verdict-${esc(externalVerdict)}">R2 ${externalLabel}</span><strong>${budget.max_gpus || 0} GPU · ${budget.gpu_hours || 0}h</strong><span>${budget.wall_days || 0} ${language === "zh" ? "天 Pilot" : "day pilot"}</span></div></summary><div class="cvpr-idea-body"><div class="cvpr-six-grid"><section><h4 data-toc="false">${language === "zh" ? "学习问题" : "Learning problem"}</h4><p>${textOf(idea.purpose)}</p></section><section><h4 data-toc="false">${language === "zh" ? "核心更新机制" : "Core update mechanism"}</h4><p>${textOf(idea.core_idea)}</p></section><section><h4 data-toc="false">${language === "zh" ? "为什么合理" : "Why it should work"}</h4><p>${textOf(idea.rationale)}</p></section><section><h4 data-toc="false">${language === "zh" ? "方法逻辑" : "Method logic"}</h4><p>${textOf(idea.method_logic)}</p></section><section><h4 data-toc="false">${language === "zh" ? "ICLR 重要性" : "Why it matters for ICLR"}</h4><p>${textOf(idea.importance)}</p></section><section><h4 data-toc="false">${language === "zh" ? "相对优势" : "Comparative advantage"}</h4><p>${textOf(idea.comparative_advantage)}</p></section></div><div class="cvpr-proof-grid"><section><h4 data-toc="false">${language === "zh" ? "最近工作与碰撞边界" : "Nearest work and collision boundary"}</h4><p>${textOf(idea.collision_boundary)}</p><div class="cvpr-chip-row">${(idea.nearest_work || []).map((name) => `<span>${esc(name)}</span>`).join("")}</div></section><section><h4 data-toc="false">${language === "zh" ? "跨域公开资产" : "Cross-domain public assets"}</h4><p><b>${language === "zh" ? "数据集" : "Datasets"}:</b> ${(idea.datasets || []).map(esc).join(" · ")}</p><p><b>${language === "zh" ? "模型" : "Models"}:</b> ${(idea.models || []).map(esc).join(" · ")}</p></section><section><h4 data-toc="false">${language === "zh" ? "可证伪假设" : "Falsifiable hypothesis"}</h4><p>${textOf(idea.hypothesis)}</p><p><b>${language === "zh" ? "主指标" : "Primary metrics"}:</b> ${textOf(idea.decisive_metric)}</p></section><section><h4 data-toc="false">${language === "zh" ? "最强对照与停止条件" : "Strongest baseline and Stop rule"}</h4><p>${textOf(idea.strongest_baseline)}</p><p class="cvpr-stop"><b>Stop:</b> ${textOf(idea.stop_condition)}</p></section></div>${renderExperimentProtocol(idea, "ICLR")}${externalReviews.map((review) => `<div class="project-web-gpt-review verdict-${esc(review.verdict)}"><header><b>${language === "zh" ? "agent 项目网页版 GPT · ICLR 严格审查" : "Agent-project web GPT · strict ICLR review"}</b><span>${esc(String(review.verdict || "").toUpperCase())}</span></header><p>${esc(review.finding || "")}</p><small><strong>${language === "zh" ? "要求" : "Required action"}:</strong> ${esc(window.localizedReviewAction ? window.localizedReviewAction(idea.id, review, language) : (review.required_action || ""))}</small></div>`).join("")}<div class="cvpr-review-strip iclr-review-strip">${reviews.map((review) => `<span class="cvpr-review-pass" title="${esc(textOf(review.finding))}"><i>✓</i>${esc(textOf(review.label))} <b>${review.score}/5</b></span>`).join("")}</div></div></details>`;
}
function renderIclrIdeaBank() {
  const bank = iclrIdeaBank();
  const ideas = bank.passed_ideas || [];
  if (!ideas.length) return `<section class="panel"><h3>${language === "zh" ? "ICLR Idea Bank 尚未生成" : "ICLR idea bank is not generated"}</h3></section>`;
  const trackButtons = [["all",language === "zh" ? "全部机制轨道" : "All mechanism tracks"], ...Object.entries(bank.tracks || {}).map(([key,label]) => [key,textOf(label)])];
  const topRows = ideas.slice(0,15).map((idea) => `<tr><td><strong>#${idea.rank}</strong><small>R1 #${idea.programmatic_rank || idea.rank}</small></td><td><a href="#iclr-${esc(idea.id)}" class="iclr-jump" data-iclr-id="${esc(idea.id)}"><b>${textOf(idea.title)}</b></a><small>${textOf(idea.track)}</small></td><td><span class="external-verdict-badge verdict-${esc(idea.external_verdict || "pending")}">${esc(String(idea.external_verdict || "pending").toUpperCase())}</span></td><td>${textOf(idea.purpose)}</td><td>${textOf(idea.core_idea)}</td><td>${(idea.domains || []).map(esc).join(" · ")}</td><td>${idea.budget.max_gpus} GPU · ${idea.budget.gpu_hours}h</td><td>${idea.priority}</td></tr>`).join("");
  const structuredBlocked = (bank.blocked_ideas || []).map((item) => `<li class="structured-blocked"><b>${textOf(item.title)}</b><span>${(item.blocking_reasons || []).map(esc).join("；")}</span></li>`);
  const earlyRejected = (bank.early_rejected || []).map((item) => `<li><b>${esc(item.title)}</b><span>${esc(item.reason)}</span></li>`);
  return `<section class="panel cvpr-bank-panel iclr-bank-panel"><div class="idea-panel-heading"><div><h3 id="iclr-low-resource-bank">${language === "zh" ? "ICLR-first 低资源 Agent 自进化 Idea Bank" : "ICLR-first low-resource agent self-evolution idea bank"}</h3><p class="section-intro">${language === "zh" ? "自动后端先用七维 Reviewer 检查真实持续进化、机制明确性、信用分配、稳定性、圈外泛化、反馈完整性和等预算复现；每个通过项必须覆盖至少两个任务域，并使用开放权重完成主结果。" : "The automatic backend reviews reality of evolution, mechanistic specificity, credit assignment, stability, out-of-loop generalization, feedback integrity, and matched-budget reproducibility. Every passed idea covers at least two domains and uses open weights for the primary result."}</p></div><strong>${ideas.length} ${language === "zh" ? "个 R1 通过项" : "R1-passed ideas"}</strong></div><div class="grid cvpr-bank-stats iclr-bank-stats"><div class="stat"><b>${bank.summary.raw_candidates}</b><span>${language === "zh" ? "个原始候选" : "raw candidates"}</span></div><div class="stat"><b>${ideas.length}</b><span>${language === "zh" ? "个七审通过" : "passed seven reviews"}</span></div><div class="stat"><b>${bank.summary.blocked_after_structured_review || 0}</b><span>${language === "zh" ? "个结构化阻断" : "structured blocked"}</span></div><div class="stat"><b>${bank.summary.early_rejected}</b><span>${language === "zh" ? "个前置淘汰" : "early rejected"}</span></div><div class="stat"><b>${bank.summary.tracks}</b><span>${language === "zh" ? "个机制轨道" : "mechanism tracks"}</span></div><div class="stat"><b>${bank.summary.project_web_gpt_reviewed || 0}/${ideas.length}</b><span>${language === "zh" ? "Oracle／网页版 GPT 已复核" : "Oracle / web-GPT reviewed"}</span></div></div><div class="external-review-progress ${bank.summary.project_web_gpt_complete ? "complete" : "pending"}"><b>${language === "zh" ? "外部二审" : "External second review"}</b><span>${bank.summary.project_web_gpt_complete ? (language === "zh" ? `26 个首轮通过项已全部完成独立复核：${bank.summary.external_pass || 0} PASS、${bank.summary.external_revise || 0} REVISE、${bank.summary.external_block || 0} BLOCK。当前列表按二审结论排序，并保留 R1 原排名。` : `All 26 first-round passes have independent reviews: ${bank.summary.external_pass || 0} PASS, ${bank.summary.external_revise || 0} REVISE, and ${bank.summary.external_block || 0} BLOCK. The list is ordered by R2 verdict while preserving the R1 rank.`) : (language === "zh" ? `已完成 ${bank.summary.project_web_gpt_reviewed || 0} 个，待复核 ${bank.summary.project_web_gpt_pending ?? ideas.length} 个；结果只在 Oracle 调用 Agent 项目网页版 ChatGPT 后计入。` : `${bank.summary.project_web_gpt_reviewed || 0} complete and ${bank.summary.project_web_gpt_pending ?? ideas.length} pending; only Oracle-mediated Agent-project web-GPT results count.`)}</span></div><div class="cvpr-filter-bar iclr-filter-bar"><div class="cvpr-track-filters">${trackButtons.map(([key,label],index) => `<button class="cvpr-filter-btn iclr-filter-btn ${index === 0 ? "active" : ""}" data-iclr-filter-type="track" data-iclr-filter-value="${esc(key)}">${esc(label)}</button>`).join("")}</div><div class="cvpr-budget-filters"><button class="cvpr-filter-btn iclr-filter-btn active" data-iclr-filter-type="budget" data-iclr-filter-value="48">≤48 GPUh</button><button class="cvpr-filter-btn iclr-filter-btn" data-iclr-filter-type="budget" data-iclr-filter-value="32">≤32 GPUh</button><button class="cvpr-filter-btn iclr-filter-btn" data-iclr-filter-type="budget" data-iclr-filter-value="24">≤24 GPUh</button></div></div><div class="advisor-table-scroll"><table class="matrix cvpr-top-table iclr-top-table"><thead><tr><th>${language === "zh" ? "R2 排序" : "R2 rank"}</th><th>Idea</th><th>${language === "zh" ? "二审" : "R2 verdict"}</th><th>${language === "zh" ? "学习问题" : "Learning problem"}</th><th>${language === "zh" ? "更新机制" : "Update mechanism"}</th><th>${language === "zh" ? "任务域" : "Domains"}</th><th>${language === "zh" ? "预算" : "Budget"}</th><th>${language === "zh" ? "R1 优先值" : "R1 priority"}</th></tr></thead><tbody>${topRows}</tbody></table></div><div id="iclr-idea-list" class="cvpr-idea-list iclr-idea-list">${ideas.map((idea,index) => `<div id="iclr-${esc(idea.id)}">${renderIclrIdeaCard(idea,index)}</div>`).join("")}</div><details class="cvpr-rejected"><summary>${language === "zh" ? `查看 ${(bank.summary.early_rejected || 0) + (bank.summary.blocked_after_structured_review || 0)} 个阻断／淘汰方向` : `See ${(bank.summary.early_rejected || 0) + (bank.summary.blocked_after_structured_review || 0)} blocked/rejected directions`}</summary><ul>${[...structuredBlocked,...earlyRejected].join("")}</ul></details></section>`;
}
function humanReviewData() {
  return window.HUMAN_REVIEW_IDEA_MAP || {review_date:"",status_order:[],status_labels:{},groups:[],ideas:{}};
}
function canonicalHumanReviewData() {
  return window.HUMAN_REVIEW_CANONICAL_20260810 || {review_date:"",category_labels:{},principles:{},original_task_evaluation:{},ideas:{}};
}
function humanRecommendationLabel(category) {
  return textOf(canonicalHumanReviewData().category_labels?.[category] || {zh:category,en:category});
}
function humanRecommendationTone(category) {
  if (category === "pilot") return "pilot";
  if (category === "redesign") return "redesign";
  if (category === "pause") return "pause";
  return "unreviewed";
}
function renderHumanReviewMethodology() {
  const canonical = canonicalHumanReviewData();
  const entries = Object.values(canonical.ideas || {});
  if (!entries.length) return "";
  const counts = entries.reduce((acc,row) => { acc[row.category] = (acc[row.category] || 0) + 1; return acc; }, {});
  const principles = canonical.principles || {};
  const evaluation = canonical.original_task_evaluation || {};
  const sources = (evaluation.sources || []).map((source) => `<a href="${esc(source.url)}" target="_blank" rel="noopener"><b>${esc(source.title)}</b><span>${textOf(source.lesson)}</span></a>`).join("");
  return `<section class="panel human-review-methodology">
    <div class="human-review-methodology-head"><div><b>${language === "zh" ? "人工意见复核 · 2026-08-10" : "Human-opinion audit · 2026-08-10"}</b><p>${language === "zh" ? "下面的“人工建议”是原讨论意见；卡片里的“当前门禁”是后续 novelty / collision / reducibility 审查后的状态。两者分开保存，不再互相覆盖。" : "Human recommendations preserve the original discussion judgment; current gates reflect later novelty/collision/reducibility reviews. They are stored separately and never overwrite one another."}</p></div><span>${entries.length}/26</span></div>
    <div class="human-recommendation-stats">${["pilot","redesign","pause","unreviewed"].map((category) => `<div class="human-recommendation-stat tone-${humanRecommendationTone(category)}"><b>${counts[category] || 0}</b><span>${esc(humanRecommendationLabel(category))}</span></div>`).join("")}</div>
    <div class="human-review-principles">
      <section><h4 data-toc="false">${language === "zh" ? "可实验类怎么走" : "Pilot-class workflow"}</h4><p>${textOf(principles.pilot)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "方法继续打磨怎么走" : "Method-redesign workflow"}</h4><p>${textOf(principles.redesign)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "暂停／合并类" : "Pause / merge"}</h4><p>${textOf(principles.pause)}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "后续系统生成硬规则" : "System-generation hard rule"}</h4><p>${textOf(principles.readability)}</p></section>
    </div>
    <details class="human-original-eval-guide"><summary><div><b>${textOf(evaluation.title)}</b><small>${language === "zh" ? "回答：隔离回归集怎么得到，100+ 原任务怎么避免每次全量重复评测" : "How to build isolated regression evaluation without rerunning 100+ tasks every update"}</small></div></summary><div class="human-original-eval-grid">
      <section><b>${language === "zh" ? "1 · 冻结保护全集" : "1 · Protected universe"}</b><p>${textOf(evaluation.protected_universe)}</p></section>
      <section><b>${language === "zh" ? "2 · 每次只跑 Sentinel" : "2 · Per-update sentinels"}</b><p>${textOf(evaluation.sentinel_panel)}</p></section>
      <section><b>${language === "zh" ? "3 · 配对评测" : "3 · Paired evaluation"}</b><p>${textOf(evaluation.paired_test)}</p></section>
      <section><b>${language === "zh" ? "4 · 只对边界案例重复" : "4 · Adaptive repeats only"}</b><p>${textOf(evaluation.adaptive_repeat)}</p></section>
      <section><b>${language === "zh" ? "5 · 低频 Full Audit" : "5 · Low-frequency full audit"}</b><p>${textOf(evaluation.full_audit)}</p></section>
      <section><b>${language === "zh" ? "6 · 独立真值" : "6 · Independent truth"}</b><p>${textOf(evaluation.independent_truth)}</p></section>
    </div><nav class="human-original-eval-sources">${sources}</nav></details>
  </section>`;
}
function humanReviewStatusLabel(status) {
  const row = humanReviewData().status_labels?.[status] || {zh:status,en:status};
  return textOf(row);
}
function humanReviewStatusTone(status) {
  if (status === "p0-ready") return "ready";
  if (status === "method-redesign") return "redesign";
  return "paused";
}
function currentFinalIdeaById(id) {
  return (window.CURRENT_FINAL_IDEAS?.ideas || []).find((idea) => (idea.idea_id || idea.id) === id) || null;
}
function experimentStateCopy(status) {
  if (status === "p0-ready") return language === "zh"
    ? {title:"怎么验证这个 Idea（P0）",note:"先只做最小实验，回答“这个机制到底有没有用”。P0 做完先汇报，人工批准后才能进入更大实验。"}
    : {title:"How to test this idea (P0)",note:"Run only the smallest experiment needed to answer whether the mechanism works. Report P0 first; larger experiments require explicit human approval."};
  if (status === "method-redesign") return language === "zh"
    ? {title:"怎么验证这个 Idea",note:"这里先把最小可证伪实验讲清楚。方法改完后再冻结具体参数，不把一份旧协议和一份新草案重复展示。"}
    : {title:"How to test this idea",note:"This states the smallest falsifiable test. Freeze exact parameters only after the method is finalized, rather than showing a draft and a duplicate protocol."};
  if (status === "paused-merged") return language === "zh"
    ? {title:"历史验证方案（暂不执行）",note:"这个方向当前暂停或已并入其他 Idea；只保留验证思路方便追溯，不启动实验。"}
    : {title:"Historical validation plan (do not run)",note:"This direction is paused or merged elsewhere. Keep the validation logic for traceability, but do not run it."};
  return language === "zh"
    ? {title:"怎么验证这个 Idea（待讨论）",note:"下面只回答实验上最重要的几个问题，方便先判断这个方向值不值得继续。"}
    : {title:"How to test this idea (for review)",note:"The section answers only the experiment questions needed to decide whether this direction is worth pursuing."};
}
function renderMatchedResourceList(items) {
  if (!Array.isArray(items) || !items.length) return "";
  const visible = items.slice(0,6).map((item) => `<li>${esc(item)}</li>`).join("");
  const remainder = items.length > 6 ? `<li class="human-resource-more">+${items.length - 6} ${language === "zh" ? "项匹配约束" : "more matched constraints"}</li>` : "";
  return `<ul class="human-resource-list">${visible}${remainder}</ul>`;
}
function humanPilotSummary(idea, fallback = "") {
  const id = idea.id || idea.idea_id || "";
  const zh = {
    "update-trust-region":"拿一批候选更新，先在固定 Probe 上记录更新前后行为怎么变，再到隐藏原任务上看哪些更新真的造成回退。比较三种接纳方式：只看当前收益、只看编辑大小、看行为漂移。只有行为漂移能更准地挡住坏更新、同时不过度拒绝好更新，才值得继续。",
    "budgeted-evolution-controller":"让同一批任务分别使用“固定更新轮数”和“学会自己决定继续 / 回滚 / 停止”的控制器。在最终成功率接近的前提下比较调用数和回退；如果控制器省不下明显调用，或者省调用会伤害任务表现，就停止。",
    "outcome-equivalent-trajectory-contrast":"固定同一成功终点的不同有效过程，用同一个抽取器提候选 lesson。不是做文字共识，而是对每条 lesson 做 memory OFF/ON 干预，并 leave-one-process-family-out 验证；只有平均效用为正、最差过程也不有害的经验才写入。和 consensus、单轨迹、utility-only 在同 replay 预算下比较。",
    "workflow-generalization-certificate":"把旧 certificate 彻底换成 paired edit-effect editor：在 source workflows 上记录同一个局部 edit 前后的真实执行增量，学习一个冻结编辑策略；到未见 API/任务图时禁止试跑候选，只允许直接选择并提交一个 edit，再和 Agentic Predictor、最近邻 edit reuse、failure heuristic 比较。",
    "world-model-error-gated-learning":"固定能进入更新的 transition 数量。对每条真实 transition，把 world-model 预测单独替换成真值，检查冻结 policy 的动作 / 风险 / 恢复决策是否会翻转；只优先学习真正会改变决策的 transition，再和 uniform、最大误差、uncertainty、AAWM-style 选样比较。"
  };
  const en = {
    "update-trust-region":"Take a batch of candidate updates, measure how behavior changes on fixed probes, then use hidden original tasks to see which updates actually cause regressions. Compare admission by current gain, edit size, and behavioral shift. Continue only if behavioral shift blocks harmful updates more accurately without rejecting too many useful ones.",
    "budgeted-evolution-controller":"Run the same tasks with a fixed update count and with a controller that chooses continue, rollback, or stop. Compare calls and regressions at similar final success. Stop if the controller does not save substantial calls or saves calls only by hurting performance.",
    "outcome-equivalent-trajectory-contrast":"Freeze distinct valid process families that reach the same successful outcome and use one extractor for candidate lessons. Instead of textual consensus, run memory OFF/ON interventions with leave-one-process-family-out validation; persist only lessons with positive mean utility and non-harmful worst-process effect. Compare against consensus, single-trajectory, and utility-only admission at matched replay budget.",
    "workflow-generalization-certificate":"Replace the old certificate with a paired edit-effect editor: learn from true before/after execution deltas of typed local edits on source workflows, freeze the editor, and on unseen APIs/task graphs forbid candidate trials and allow exactly one direct edit commit. Compare with Agentic Predictor, nearest-neighbor edit reuse, and failure heuristics.",
    "world-model-error-gated-learning":"Fix the number of transitions allowed into updates. For each true transition, replace only the world-model prediction with truth and test whether the frozen policy changes its action, risk, or recovery decision. Prioritize decision-switch transitions and compare with uniform, largest-error, uncertainty, and AAWM-style selection."
  };
  return (language === "zh" ? zh[id] : en[id]) || fallback;
}
function humanMetricSummary(idea, fallback = "") {
  const id = idea.id || idea.idea_id || "";
  const zh = {
    "update-trust-region":"重点看三件事：坏更新识别得准不准、隐藏任务最坏回退有多大、好更新被误拒绝多少。",
    "budgeted-evolution-controller":"重点看同等任务成功率下节省了多少调用、是否减少无效更新轮次，以及跨任务后还能不能保持这种节省。",
    "outcome-equivalent-trajectory-contrast":"重点看同 replay 预算下 future-task success、负迁移率和 worst-process effect；utility-only 若等效就停止 process-invariance 主张。",
    "workflow-generalization-certificate":"重点看 hidden workflow 零搜索直接 edit 后的真实成功增量、坏 edit 率和执行数；absolute predictor 若等效就停止。",
    "world-model-error-gated-learning":"重点看相同 transition-update 数下的任务成功、action regret、风险 / 恢复错误，以及 decision-switch 选样是否比误差大小更省更新。"
  };
  const en = {
    "update-trust-region":"Focus on harmful-update detection, worst hidden-task regression, and how many useful updates are falsely rejected.",
    "budgeted-evolution-controller":"Focus on calls saved at equal task success, wasted update rounds avoided, and whether the saving transfers across tasks.",
    "outcome-equivalent-trajectory-contrast":"Focus on future-task success, negative transfer, and worst-process effect at matched replay budget; stop the process-invariance claim if utility-only admission matches.",
    "workflow-generalization-certificate":"Focus on true post-edit success delta, harmful-edit rate, and executions for zero-search direct edits on hidden workflows; stop if absolute prediction matches.",
    "world-model-error-gated-learning":"Focus on task success, action regret, risk/recovery errors, and whether decision-switch selection uses the fixed transition-update budget more effectively than error magnitude."
  };
  return (language === "zh" ? zh[id] : en[id]) || fallback;
}
function renderIdeaExperimentSection(idea, meta = {}, sourceIdeas = []) {
  const sources = (sourceIdeas || []).filter(Boolean);
  const exactFinal = currentFinalIdeaById(idea.id || idea.idea_id);
  const rich = exactFinal || sources[sources.length - 1] || idea;
  const protocol = idea.experiment_protocol || rich.experiment_protocol || {};
  const data = protocol.data_protocol || {};
  const externalPilot = [...(idea.external_reviews || [])].reverse().find((review) => review.decisive_pilot)?.decisive_pilot;
  const rawPilot = textOf(idea.decisive_pilot || rich.decisive_pilot || externalPilot || idea.pilot || {});
  const rawMetric = textOf(idea.decisive_metric || rich.decisive_metric || protocol.main_table || {});
  const pilot = humanPilotSummary(idea, rawPilot);
  const metric = humanMetricSummary(idea, rawMetric);
  const originalEval = idea.original_task_evaluation || rich.original_task_evaluation || protocol.original_task_evaluation || {};
  const pairedOriginal = textOf(originalEval.paired_measurement || {});
  const independentTruth = textOf(idea.independent_ground_truth || rich.independent_ground_truth || idea.method_substance?.independent_truth || rich.method_substance?.independent_truth || originalEval.independent_truth || data.test || {});
  const truth = [pairedOriginal,independentTruth].filter(Boolean).join(" ");
  const baseline = textOf(idea.strongest_baseline || rich.strongest_baseline || {});
  const stop = textOf(idea.stop_condition || rich.stop_condition || protocol.stop_gate || {});
  const go = textOf(idea.success_gate || rich.success_gate || protocol.success_gate || idea.surviving_claim || rich.surviving_claim || {});
  const resources = idea.matched_resources || rich.matched_resources || [];
  const budget = idea.budget || {};
  const hasBudget = Number(budget.max_gpus || 0) || Number(budget.gpu_hours || 0) || Number(budget.wall_days || 0);
  const state = experimentStateCopy(meta.status);
  const experimentTone = meta.status === "new-review" ? "review" : humanReviewStatusTone(meta.status);
  const actor = protocol.actor || "";
  const crossModel = protocol.cross_model || "";
  const verifier = protocol.critic_or_verifier || "";
  const apiRole = textOf(protocol.commercial_api_role || {});
  const parameterUpdates = textOf(protocol.parameter_updates || {});
  const discovery = textOf(data.discovery || {});
  const calibration = textOf(data.calibration || {});
  const frozenTest = textOf(data.test || {});
  const repetitions = textOf(protocol.repetitions || {});
  const callBudget = textOf(protocol.call_budget || {});
  const computeBudget = textOf(protocol.compute_budget || {});
  const controls = (protocol.controls || []).map((item) => `<li>${textOf(item)}</li>`).join("");
  const ablations = (protocol.ablations || []).map((item) => `<li>${textOf(item)}</li>`).join("");
  const phases = (protocol.phases || []).map((phase) => `<li><b>${esc(phase.id)} · ${textOf(phase.title)}</b><span>${textOf(phase.setup)}</span><small>${language === "zh" ? "通过条件" : "Gate"}: ${textOf(phase.gate)}</small></li>`).join("");
  const hasExecutionDetails = [actor,crossModel,verifier,apiRole,parameterUpdates,discovery,calibration,frozenTest,repetitions,callBudget,computeBudget,controls,ablations,phases].some(Boolean) || resources.length || hasBudget;
  if (![pilot,metric,truth,baseline,stop,go].some(Boolean) && !hasExecutionDetails) return "";
  const sourceDetails = sources.length > 1 ? `<details class="human-source-pilots"><summary>${language === "zh" ? "合并前的实验来源（追溯用）" : "Pre-merge experiment sources (traceability)"}</summary>${sources.map((source) => `<section><b>${textOf(source.title || {})}</b><p>${textOf(source.decisive_pilot || {})}</p></section>`).join("")}</details>` : "";
  const executionDetails = hasExecutionDetails ? `<details class="human-execution-details"><summary>${language === "zh" ? "模型、API、数据划分与预算" : "Models, API, data splits, and budget"}<small>${language === "zh" ? "执行时再看这些参数，不和上面的实验思路重复" : "Execution parameters only; no duplicate experiment narrative"}</small></summary><div class="human-execution-grid">${actor ? `<section><b>${language === "zh" ? "主模型" : "Main model"}</b><p>${esc(actor)}</p></section>` : ""}${crossModel ? `<section><b>${language === "zh" ? "第二模型" : "Second model"}</b><p>${esc(crossModel)}</p></section>` : ""}${verifier ? `<section><b>${language === "zh" ? "谁来判对错" : "Verifier"}</b><p>${esc(verifier)}</p></section>` : ""}${apiRole ? `<section><b>${language === "zh" ? "商业 API 做什么" : "Commercial API role"}</b><p>${apiRole}</p></section>` : ""}${parameterUpdates ? `<section><b>${language === "zh" ? "真正更新什么" : "What actually changes"}</b><p>${parameterUpdates}</p></section>` : ""}${discovery ? `<section><b>${language === "zh" ? "用什么数据找规律" : "Discovery split"}</b><p>${discovery}</p></section>` : ""}${calibration ? `<section><b>${language === "zh" ? "用什么数据定阈值" : "Calibration split"}</b><p>${calibration}</p></section>` : ""}${frozenTest ? `<section><b>${language === "zh" ? "最后在哪些数据上验" : "Frozen test"}</b><p>${frozenTest}</p></section>` : ""}${repetitions || callBudget ? `<section><b>${language === "zh" ? "重复次数 / 调用量" : "Repeats / calls"}</b><p>${repetitions}</p><p>${callBudget}</p></section>` : ""}${computeBudget || hasBudget ? `<section><b>${language === "zh" ? "算力" : "Compute"}</b><p>${computeBudget}</p>${hasBudget ? `<p>${budget.max_gpus || 0} GPU · ${budget.gpu_hours || 0}h · ${budget.wall_days || 0} ${language === "zh" ? "天" : "days"}</p>` : ""}</section>` : ""}</div>${resources.length ? `<div class="human-execution-list"><b>${language === "zh" ? "公平比较时必须保持一致" : "Must be matched across methods"}</b>${renderMatchedResourceList(resources)}</div>` : ""}${controls ? `<div class="human-execution-list"><b>${language === "zh" ? "额外对照" : "Additional controls"}</b><ol>${controls}</ol></div>` : ""}${ablations ? `<div class="human-execution-list"><b>${language === "zh" ? "关键消融" : "Key ablations"}</b><ol>${ablations}</ol></div>` : ""}${phases ? `<div class="human-phase-list"><b>${language === "zh" ? "如果继续，后面怎么扩" : "If it survives, how to scale"}</b><ol>${phases}</ol></div>` : ""}</details>` : "";
  return `<section class="human-experiment-section human-experiment-${experimentTone}">
    <header><div><h4 data-toc="false">${esc(state.title)}</h4><p>${esc(state.note)}</p></div><span>${language === "zh" ? (meta.status === "p0-ready" ? "P0" : (meta.status === "method-redesign" ? "待定稿" : (meta.status === "paused-merged" ? "暂停" : "待讨论"))) : (meta.status === "p0-ready" ? "P0" : (meta.status === "method-redesign" ? "DESIGN" : (meta.status === "paused-merged" ? "HOLD" : "REVIEW")))}</span></header>
    <div class="human-experiment-grid">
      <section class="human-experiment-wide"><h4 data-toc="false">${language === "zh" ? "最小实验怎么做" : "Smallest experiment"}</h4><p>${pilot || "—"}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "和谁比才公平" : "Fair comparison"}</h4><p>${baseline || "—"}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "原任务怎么评，谁来判对错" : "Original-task truth"}</h4><p>${truth || "—"}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "主要看什么结果" : "What to measure"}</h4><p>${metric || "—"}</p></section>
      <section><h4 data-toc="false">${language === "zh" ? "什么结果值得继续" : "What counts as a win"}</h4><p>${go || "—"}</p></section>
      <section class="human-experiment-stop"><h4 data-toc="false">${language === "zh" ? "什么情况直接放弃" : "When to stop"}</h4><p>${stop || "—"}</p></section>
    </div>
    ${executionDetails}
    ${sourceDetails}
  </section>`;
}
function renderHumanReviewedIdeaCard(idea, meta, index) {
  const overlay = (window.FINAL20_MERGE_OVERRIDES || {})[idea.id] || {};
  const redesigned = !!idea.redesign_iteration;
  const current = redesigned ? {...overlay, ...idea} : {...idea, ...overlay};
  const intuition = textOf(current.core_intuition || current.rationale || {});
  const example = textOf(current.concrete_example || {});
  const substance = current.method_substance || {};
  const mergeGate = current.parent_merge_gate || {};
  const historicalVerdict = String(idea.external_verdict || "pending").toUpperCase();
  const tone = humanReviewStatusTone(meta.status);
  const code = meta.code || idea.id;
  const canonicalReview = canonicalHumanReviewData().ideas?.[idea.id] || {};
  const humanOpinion = textOf(canonicalReview.opinion || meta.feedback || {});
  const originalNumber = Number(canonicalReview.original_number || 0);
  const humanRecommendation = canonicalReview.category || "unreviewed";
  const iteration = current.redesign_iteration || {};
  const iterationSummary = textOf(iteration.summary || {});
  const absorbed = overlay.absorbed_from || current.absorbed_from || [];
  const absorbedIdeas = absorbed.map(currentFinalIdeaById).filter(Boolean);
  const absorbedNote = absorbed.length ? `<div class="human-absorbed-methods"><b>${language === "zh" ? "已吸收 FINAL 方法资产" : "Absorbed FINAL method assets"}</b>${absorbed.map((id)=>`<span>${esc(id)}</span>`).join("")}</div>` : "";
  const freshCheck = current.fresh_reducibility_check || {};
  const freshSources = (freshCheck.sources || []).map((source) => `<a href="${esc(source.url)}" target="_blank" rel="noopener">${esc(source.title)}</a>`).join("");
  const freshBlock = freshSources ? `<section class="human-fresh-collision"><h4 data-toc="false">${language === "zh" ? `Fresh reducibility · ${esc(freshCheck.review_date || "")}` : `Fresh reducibility · ${esc(freshCheck.review_date || "")}`}</h4><p>${language === "zh" ? "以下是一手来源；上面的“最近工作与真正边界”已经按这些工作收窄，不把已有人做过的部分继续当贡献。" : "Primary sources below support the narrowed boundary above; already-covered mechanisms are not counted as the contribution."}</p><nav>${freshSources}</nav></section>` : "";
  return `<details class="human-review-idea-card human-tone-${tone}" id="idea-${esc(code.toLowerCase())}">
    <summary><div class="human-idea-title"><span class="human-idea-code">${esc(code)}</span><div><b>${textOf(current.title)}</b><small>${originalNumber ? `${language === "zh" ? "原讨论" : "Original"} Idea ${originalNumber} · ` : ""}${textOf(idea.track)} · ${language === "zh" ? "历史自动二审" : "historical automated R2"} ${esc(historicalVerdict)}</small></div></div><div class="human-idea-summary"><span class="human-status-badge human-status-${tone}">${esc(humanReviewStatusLabel(meta.status))}</span><p>${esc(iterationSummary || humanOpinion)}</p></div></summary>
    <div class="human-idea-body">
      <div class="human-review-history">
        <section class="human-opinion-box"><h4 data-toc="false">${language === "zh" ? `人工意见 · 2026-08-10（原讨论 Idea ${originalNumber || "?"}）` : `Human opinion · 2026-08-10 (original Idea ${originalNumber || "?"})`}</h4><p>${esc(humanOpinion || "—")}</p><small class="human-recommendation-label tone-${humanRecommendationTone(humanRecommendation)}">${esc(humanRecommendationLabel(humanRecommendation))}</small></section>
        ${iterationSummary ? `<section class="human-iteration-box"><h4 data-toc="false">${language === "zh" ? `本轮方法迭代 · ${esc(iteration.round || "2026-08-10")}` : `Current method iteration · ${esc(iteration.round || "2026-08-10")}`}</h4><p>${esc(iterationSummary)}</p>${iteration.verdict ? `<small>${language === "zh" ? "当前门禁" : "Current gate"}: ${esc(iteration.verdict)}</small>` : ""}</section>` : ""}
      </div>
      <div class="human-core-grid human-reading-grid">
        <section><h4 data-toc="false">${language === "zh" ? "这个 Idea 在解决什么" : "What problem is this solving?"}</h4><p>${textOf(current.purpose)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "最简单的直觉" : "Plain-language intuition"}</h4><p>${esc(intuition)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "具体准备怎么做" : "What would we actually do?"}</h4><p>${textOf(current.core_idea)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "举个具体例子" : "Concrete example"}</h4><p>${esc(example || "—")}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "为什么值得试" : "Why might this work?"}</h4><p>${textOf(current.rationale || current.importance)}</p></section>
      </div>
      ${absorbedNote}
      <details class="human-technical-details"><summary>${language === "zh" ? "方法细节与论文边界" : "Method details and paper boundary"}<small>${language === "zh" ? "需要写论文或审 novelty 时再展开" : "Open when checking implementation or novelty"}</small></summary><div class="human-evidence-grid">
        <section><h4 data-toc="false">${language === "zh" ? "方法步骤" : "Method steps"}</h4><p>${textOf(current.method_logic)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "为什么这个问题重要" : "Why the problem matters"}</h4><p>${textOf(current.importance)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "相比简单方法多了什么" : "What it adds over simpler methods"}</h4><p>${textOf(current.comparative_advantage)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "真正更新什么 / 用什么学" : "Persistent update / learning signal"}</h4><p>${textOf(substance.persistent_update_object || {})}</p><p>${textOf(substance.learning_signal || {})}</p></section>
        ${mergeGate.status === "merge-if-tied" ? `<section><h4 data-toc="false">${language === "zh" ? "什么时候必须并回父 Idea" : "When it must merge into its parent"}</h4><p>${textOf(mergeGate.decision_rule || {})}</p></section>` : ""}
        <section><h4 data-toc="false">${language === "zh" ? "最近工作与真正边界" : "Nearest work and real boundary"}</h4><p>${textOf(current.collision_boundary)}</p><div class="cvpr-chip-row">${(current.nearest_work || []).map((name) => `<span>${esc(name)}</span>`).join("")}</div></section>
        ${freshBlock}
      </div></details>
      ${renderIdeaExperimentSection(current,meta,absorbedIdeas)}
    </div>
  </details>`;
}
function renderDiscussedIdeaBank() {
  const bank = iclrIdeaBank();
  const review = humanReviewData();
  const byId = new Map((bank.passed_ideas || []).map((idea) => [idea.id, idea]));
  const statuses = review.status_order || ["p0-ready","method-redesign","paused-merged"];
  const all = Object.entries(review.ideas || {}).map(([id,meta]) => ({id,meta,idea:byId.get(id)})).filter((row) => row.idea);
  const counts = Object.fromEntries(statuses.map((status) => [status,all.filter((row) => row.meta.status === status).length]));
  const groups = (review.groups || []).map((group) => {
    const rows = all.filter((row) => row.meta.group === group.id).sort((a,b) => String(a.meta.code).localeCompare(String(b.meta.code),undefined,{numeric:true}));
    const statusBlocks = statuses.map((status) => {
      const subset = rows.filter((row) => row.meta.status === status);
      if (!subset.length) return "";
      return `<div class="human-status-block"><div class="human-status-heading human-status-${humanReviewStatusTone(status)}"><b>${esc(humanReviewStatusLabel(status))}</b><span>${subset.length}</span></div><div class="human-idea-list">${subset.map((row,index) => renderHumanReviewedIdeaCard(row.idea,row.meta,index)).join("")}</div></div>`;
    }).join("");
    return `<section class="human-science-group" id="discussed-group-${esc(group.id.toLowerCase())}"><header><span>${esc(group.id)}</span><div><h3>${textOf(group.title)}</h3><p>${textOf(group.question)}</p></div><strong>${rows.length}</strong></header>${statusBlocks}</section>`;
  }).join("");
  const canonicalDate = canonicalHumanReviewData().review_date || review.review_date || "2026-08-10";
  return `<section class="panel human-review-overview"><div class="idea-panel-heading"><div><b class="human-overview-kicker">H1 · ${esc(canonicalDate)}</b><p class="section-intro">${language === "zh" ? "按科学问题和当前成熟度组织。人工原始意见、后续方法迭代和当前科学门禁分开保存；原讨论 Idea 1–26 的编号已重新映射到当前 A/B/C 编号。展开后看“人工意见 → 本轮迭代 → 问题—直觉—具体做法—例子—论文边界—决定性实验”。" : "Organized by scientific problem and current maturity. Original human opinions, later method iterations, and current scientific gates are stored separately; original Idea 1–26 numbers are mapped to the current A/B/C codes. Expanded cards show human opinion → current iteration → problem → intuition → method → example → paper boundary → decisive experiment."}</p></div><strong>${all.length} ${language === "zh" ? "个已讨论" : "discussed"}</strong></div><div class="human-review-stats">${statuses.map((status) => `<div class="human-stat human-stat-${humanReviewStatusTone(status)}"><b>${counts[status] || 0}</b><span>${esc(humanReviewStatusLabel(status))}</span></div>`).join("")}</div></section>${renderHumanReviewMethodology()}${groups}`;
}
function supplementalGroupId(idea) {
  const key = `${idea.idea_id || idea.id || ""} ${textOf(idea.title || {})}`.toLowerCase();
  if (/world|embodied|recovery|transition.*state/.test(key)) return "F";
  if (/workflow|api|permission|provider|compiler|contract|tool|privilege|swap/.test(key)) return "E";
  if (/curriculum|exam|task-generation|challenge/.test(key)) return "D";
  if (/evaluator|rubric|reward|judge|correction|critic/.test(key)) return "C";
  if (/memory|skill|applicability|retrieval|consolidat|lesson/.test(key)) return "B";
  return "A";
}
function renderSupplementalIdeaCard(row) {
  const idea = row.idea;
  const id = idea.idea_id || idea.id || "candidate";
  const source = row.source;
  const sourceIdeas = (idea.source_ids || []).map(currentFinalIdeaById).filter(Boolean);
  const richSource = sourceIdeas[sourceIdeas.length - 1] || idea;
  const title = textOf(idea.title || {});
  const problem = textOf(idea.purpose || idea.problem || richSource.purpose || {});
  const method = textOf(idea.core_idea || richSource.core_idea || {});
  const intuition = textOf(idea.core_intuition || richSource.core_intuition || {});
  const rationale = textOf(idea.rationale || richSource.rationale || idea.hypothesis || {});
  const methodLogic = textOf(idea.method_logic || richSource.method_logic || {});
  const importance = textOf(idea.importance || richSource.importance || {});
  const advantage = textOf(idea.comparative_advantage || richSource.comparative_advantage || richSource.surviving_claim || idea.hypothesis || {});
  const collision = textOf(idea.collision_boundary || richSource.collision_boundary || {});
  const sourceLabel = source === "final-merged" ? (language === "zh" ? "FINAL20 合并审查后独立保留" : "Independent after FINAL20 merge audit") : `${language === "zh" ? "网络灵感" : "internet-inspired"} · ${String(idea.external_verdict || idea.final_status || "pending").toUpperCase()}`;
  const code = idea.code || (language === "zh" ? "新增候选" : "new candidate");
  const baseline = textOf(idea.strongest_baseline || richSource.strongest_baseline || {});
  const currentRole = source === "final-merged" ? (language === "zh" ? "FINAL 去重后仍不能合理并入已有方向，因此暂时作为独立 Idea 保留，等下一轮人工讨论。" : "After FINAL deduplication this still does not merge cleanly into an existing direction, so it remains independent pending human review.") : (language === "zh" ? "这是新增候选，还没有完成当前轮人工讨论；先判断问题是否真实、方法是否有实质，再决定保留或合并。" : "This is a new candidate that has not completed human review; first test whether the problem is real and the method substantive, then keep or merge it.");
  return `<details class="supplemental-idea-card" id="new-${esc(id)}"><summary><div><span>${esc(code)}</span><b>${esc(title)}</b><small>${esc(sourceLabel)}</small></div><p>${esc(problem)}</p></summary><div class="supplemental-human-grid"><section><b>${language === "zh" ? "这个 Idea 在解决什么" : "What problem is this solving?"}</b><p>${esc(problem || "—")}</p></section><section><b>${language === "zh" ? "最简单的直觉" : "Plain-language intuition"}</b><p>${esc(intuition || "—")}</p></section><section><b>${language === "zh" ? "具体准备怎么做" : "What would we actually do?"}</b><p>${esc(method || textOf(idea.hypothesis || {}))}</p></section><section><b>${language === "zh" ? "为什么值得试" : "Why might this work?"}</b><p>${esc(rationale || importance || "—")}</p></section><details class="human-technical-details supplemental-technical-details"><summary>${language === "zh" ? "方法细节与论文边界" : "Method details and paper boundary"}<small>${language === "zh" ? "审方法或 novelty 时再展开" : "Open for method/novelty review"}</small></summary><div class="human-evidence-grid"><section><h4 data-toc="false">${language === "zh" ? "方法步骤" : "Method steps"}</h4><p>${esc(methodLogic || "—")}</p></section><section><h4 data-toc="false">${language === "zh" ? "为什么重要" : "Why it matters"}</h4><p>${esc(importance || problem || "—")}</p></section><section><h4 data-toc="false">${language === "zh" ? "相比简单方法多了什么" : "What it adds"}</h4><p>${esc(advantage || "—")}</p></section><section><h4 data-toc="false">${language === "zh" ? "最近工作与真正边界" : "Nearest work and real boundary"}</h4><p>${esc(collision || "—")}</p></section><section><h4 data-toc="false">${language === "zh" ? "最强对照" : "Strongest baseline"}</h4><p>${baseline || "—"}</p></section><section><h4 data-toc="false">${language === "zh" ? "当前判断" : "Current role"}</h4><p>${esc(currentRole)}</p></section></div></details>${renderIdeaExperimentSection(idea,{status:"new-review"},sourceIdeas)}</div></details>`;
}
function renderNewIdeaCandidates() {
  const finalIdeas = (window.FINAL20_MERGE_AUDIT?.standalone_ideas || []).map((idea) => ({source:"final-merged",idea}));
  const inspired = window.MACHINE_SCHOOL_IDEAS || {};
  const inspiredRows = [...(inspired.passed_ideas || []),...(inspired.revise_ideas || [])].filter((idea) => String(idea.external_verdict || "pending").toLowerCase() !== "block").map((idea) => ({source:"inspired",idea}));
  const seen = new Set();
  const rows = [...finalIdeas,...inspiredRows].filter((row) => { const id=row.idea.idea_id || row.idea.id; if (!id || seen.has(id)) return false; seen.add(id); return true; });
  const groups = humanReviewData().groups || [];
  const merged = window.FINAL20_MERGE_AUDIT?.summary || {};
  return `<section class="panel supplemental-overview"><div class="idea-panel-heading"><div><p class="section-intro">${language === "zh" ? `20 个 FINAL 已完成合并审查：${merged.merged_into_discussed || 0} 个直接吸收进第一章，${merged.component_only || 0} 个仅保留为专门组件，4 条 FINAL 来源合并为 3 个真正独立的新 Idea。这里另外保留尚未完成人工讨论的网络灵感候选；前端仍按科学问题而不是批次组织。` : `The 20 FINAL ideas have completed merge review: ${merged.merged_into_discussed || 0} were absorbed into Chapter 1, ${merged.component_only || 0} remains only as a specialized component, and four FINAL source records collapsed into three genuinely independent new ideas. Internet-inspired candidates remain here until human review; the frontend stays organized by scientific problem, not generation round.`}</p></div><strong>${rows.length} ${language === "zh" ? "个待讨论" : "to review"}</strong></div></section>${groups.map((group) => { const subset=rows.filter((row)=>(row.idea.group || supplementalGroupId(row.idea))===group.id); if(!subset.length) return ""; return `<section class="supplemental-group" id="new-group-${esc(group.id.toLowerCase())}"><header><span>${esc(group.id)}</span><div><h3>${textOf(group.title)}</h3><p>${language === "zh" ? "新增方向按科学问题归组；FINAL 来源已经先做过去重合并。" : "New directions are grouped by scientific problem; FINAL-derived candidates have already been deduplicated and merged."}</p></div><strong>${subset.length}</strong></header><div class="supplemental-list">${subset.map(renderSupplementalIdeaCard).join("")}</div></section>`; }).join("")}`;
}
function renderCvprFollowupArchive() {
  return `<details class="panel cvpr-followup-archive"><summary><div><b>${language === "zh" ? "CVPR 后续视觉专门化池" : "CVPR follow-up visual-specialization bank"}</b><span>${language === "zh" ? "保留原视觉、视频、生成和 VLA Idea；不再作为当前主投入口。" : "Preserves the visual, video, generation, and VLA ideas; no longer the primary submission view."}</span></div></summary><div class="cvpr-followup-body">${renderPublishedExperimentAudit()}${renderCvprLowResourceBank()}</div></details>`;
}

function cvprIdeaBank() {
  return window.CVPR_LOW_RESOURCE_IDEAS || {summary:{raw_candidates:0,passed:0,early_rejected:0,tracks:0},policy:{},tracks:{},passed_ideas:[],early_rejected:[]};
}
function publishedExperimentAudit() {
  return window.PUBLISHED_EXPERIMENT_AUDIT || {summary:{papers:0},papers:[]};
}
function substrateLabel(value) {
  const labels = {
    hybrid:{zh:"API + 开源混合",en:"API + open hybrid"},
    "hybrid-retrospective-training":{zh:"混合基座 + 回顾模型训练",en:"Hybrid substrate + retrospective training"},
    "in-context-optimizer":{zh:"上下文优化器",en:"In-context optimizer"},
    "hybrid-evolutionary-search":{zh:"混合模型 + 进化搜索",en:"Hybrid models + evolutionary search"},
    "trained-embodied-continual-policy":{zh:"训练具身持续策略",en:"Trained embodied continual policy"},
    "workflow-search-hybrid":{zh:"混合模型工作流搜索",en:"Hybrid workflow search"},
    "open-weight-online-rl":{zh:"开放权重在线 RL",en:"Open-weight online RL"},
    "proprietary-online-rl":{zh:"闭源模型在线 RL",en:"Proprietary-model online RL"},
    "open-weight-reward-training":{zh:"开放权重 Reward 训练",en:"Open-weight reward training"},
    "benchmark-plus-open-training":{zh:"结构基准 + 开放模型训练",en:"Structured benchmark + open training"},
    "world-model-augmented-inference":{zh:"世界模型增强推理",en:"World-model-augmented inference"},
    "hybrid-synthetic-instruction-tuning":{zh:"混合合成 + 指令微调",en:"Hybrid synthesis + instruction tuning"},
    "dynamic-workflow-inference":{zh:"动态工作流推理",en:"Dynamic workflow inference"},
    "open-weight":{zh:"开源权重训练",en:"Open-weight training"},
    "open-or-hybrid-unknown-exact":{zh:"开源／混合待精确核验",en:"Open/hybrid exact setup pending"},
    "trained-open-critic-exact-backbone-pending":{zh:"训练开源 Critic，骨干待核验",en:"Trained open critic; backbone pending"},
    "api-and-model-agnostic-inference":{zh:"API 可用、方法推理时",en:"API-compatible inference-only"},
    "trained-policy-plus-mllm":{zh:"训练策略 + MLLM",en:"Trained policy + MLLM"},
    "llm-program-synthesis-exact-model-pending":{zh:"LLM 程序生成，模型待核验",en:"LLM program synthesis; model pending"},
    "open-weight-high-resource-training":{zh:"开源权重高资源训练",en:"Open-weight high-resource training"},
    "open-weight-model-plus-proprietary-tool":{zh:"开源模型 + 闭源工具",en:"Open model + proprietary tool"},
    "multi-tool-router-exact-substrates-pending":{zh:"多工具路由，基座待核验",en:"Multi-tool router; substrates pending"},
    "graph-and-web-tool-agent-exact-backbone-pending":{zh:"图与 Web 工具 Agent，骨干待核验",en:"Graph/web-tool agent; backbone pending"},
  };
  return textOf(labels[value] || {zh:value,en:value});
}
function verificationLabel(value) {
  const labels = {
    "verified-official":{zh:"官方材料已核验",en:"Verified from official sources"},
    "verified-with-open-variant-pending":{zh:"方法已核验，开源版本待确认",en:"Method verified; open variant pending"},
    "partial-official":{zh:"部分官方信息已核验",en:"Partially verified from official sources"},
    "verified-official-code":{zh:"官方论文与代码已核验",en:"Verified from official paper and code"},
    "verified-method-exact-checkpoint-pending":{zh:"方法已核验，精确 checkpoint 待确认",en:"Method verified; exact checkpoint pending"},
    "official-abstract-verified":{zh:"ICLR 官方摘要已核验",en:"Verified from the official ICLR abstract"},
    "official-abstract-method-verified":{zh:"ICLR 官方摘要与方法已核验",en:"Method verified from the official ICLR abstract"},
  };
  return textOf(labels[value] || {zh:value,en:value});
}
function renderPublishedExperimentAudit() {
  const audit = publishedExperimentAudit();
  const rows = (audit.papers || []).map((paper) => `<tr><td><a href="${esc(paper.source)}" target="_blank" rel="noopener"><strong>${esc(paper.title)}</strong></a><small>${esc(paper.venue)}</small></td><td><span class="substrate-badge">${esc(substrateLabel(paper.substrate))}</span><p>${esc(textOf(paper.actor))}</p></td><td><p>${esc(textOf(paper.api_role))}</p></td><td><p>${esc(textOf(paper.parameter_updates))}</p></td><td><p>${esc(textOf(paper.data))}</p><small>${esc(textOf(paper.hardware))}</small></td><td><span class="verification-badge">${esc(verificationLabel(paper.verification))}</span><p>${textOf(paper.implication)}</p></td></tr>`).join("");
  return `<section class="panel published-audit-panel"><div class="idea-panel-heading"><div><h3 id="published-experiment-substrate-audit">${language === "zh" ? "已发表视觉自进化论文：模型、API 与训练基座审计" : "Published visual self-evolution papers: model, API, and training substrate audit"}</h3><p class="section-intro">${language === "zh" ? "只陈述能够从正式论文、项目页或作者代码核验的事实；没有明确报告的模型版本与硬件保持 unknown。API、开源权重、参数训练和外部闭源工具分别统计，避免把“用了 GPT”误写成整篇论文都依赖 API。" : "Only facts traceable to official papers, project pages, or author code are stated. Unreported model variants and hardware remain unknown. API access, open weights, parameter training, and proprietary external tools are tracked separately."}</p></div><strong>${audit.summary?.papers || 0} ${language === "zh" ? "篇论文" : "papers"}</strong></div><div class="advisor-table-scroll"><table class="matrix published-audit-table"><thead><tr><th>${language === "zh" ? "论文" : "Paper"}</th><th>${language === "zh" ? "主模型／基座" : "Actor / substrate"}</th><th>${language === "zh" ? "API 角色" : "API role"}</th><th>${language === "zh" ? "更新什么" : "What is updated"}</th><th>${language === "zh" ? "数据与硬件" : "Data and hardware"}</th><th>${language === "zh" ? "低资源启示" : "Low-resource implication"}</th></tr></thead><tbody>${rows}</tbody></table></div><div class="published-audit-conclusion"><b>${language === "zh" ? "统一结论" : "Design conclusion"}</b><span>${language === "zh" ? "主结果采用本地开源权重；第二个开源架构验证迁移；商业 API 只作为可选上界／Judge，且不能成为唯一评测器。" : "Use local open weights for the primary result, a second open architecture for transfer, and commercial APIs only as optional ceilings/judges—not the sole evaluator."}</span></div></section>`;
}
function renderExperimentProtocol(idea, venue = "ICLR") {
  const p = idea.experiment_protocol || {};
  if (!p.actor) return "";
  const data = p.data_protocol || {};
  const phases = (p.phases || []).map((phase) => `<article><span>${esc(phase.id)}</span><div><b>${textOf(phase.title)}</b><p>${textOf(phase.setup)}</p><small><strong>Gate:</strong> ${textOf(phase.gate)}</small></div></article>`).join("");
  const controls = (p.controls || []).map((item) => `<li>${textOf(item)}</li>`).join("");
  const ablations = (p.ablations || []).map((item) => `<li>${textOf(item)}</li>`).join("");
  return `<details class="cvpr-experiment-protocol" open><summary>${language === "zh" ? "实验执行协议：模型、API、数据划分与主表" : "Executable protocol: models, API, splits, and main table"}</summary><div class="protocol-model-grid"><section><b>Actor</b><p>${esc(p.actor)}</p></section><section><b>${language === "zh" ? "跨模型验证" : "Cross-model"}</b><p>${esc(p.cross_model)}</p></section><section><b>Critic / Verifier</b><p>${esc(p.critic_or_verifier)}</p></section><section><b>${venue === "ICLR" ? (language === "zh" ? "跨领域／工具模型" : "Domain / tool model") : (language === "zh" ? "视觉工具" : "Visual tools")}</b><p>${esc(p.optional_domain_model || p.tool_models || "--")}</p></section><section><b>${language === "zh" ? "商业 API" : "Commercial API"}</b><p>${textOf(p.commercial_api_role)}</p></section><section><b>${language === "zh" ? "参数更新范围" : "Parameter updates"}</b><p>${textOf(p.parameter_updates)}</p></section></div><div class="protocol-split-grid"><section><b>${language === "zh" ? "Discovery" : "Discovery"}</b><p>${textOf(data.discovery)}</p></section><section><b>Calibration</b><p>${textOf(data.calibration)}</p></section><section><b>${language === "zh" ? "冻结测试" : "Frozen test"}</b><p>${textOf(data.test)}</p></section></div><div class="protocol-phases">${phases}</div><div class="protocol-detail-grid"><section><b>${language === "zh" ? "对照组" : "Controls"}</b><ol>${controls}</ol></section><section><b>${language === "zh" ? "消融" : "Ablations"}</b><ol>${ablations}</ol></section><section><b>${language === "zh" ? "重复与调用预算" : "Repetitions and calls"}</b><p>${textOf(p.repetitions)}</p><p>${textOf(p.call_budget)}</p></section><section><b>${language === "zh" ? "算力预算" : "Compute budget"}</b><p>${textOf(p.compute_budget)}</p></section><section><b>${language === "zh" ? "决定性主表" : "Decisive main table"}</b><p>${textOf(p.main_table)}</p></section><section><b>Go / Stop</b><p><strong>Go:</strong> ${textOf(p.success_gate)}</p><p><strong>Stop:</strong> ${textOf(p.stop_gate)}</p></section></div></details>`;
}
function renderCvprIdeaCard(idea, index) {
  const budget = idea.budget || {};
  const reviews = idea.reviews || [];
  const externalReviews = idea.external_reviews || [];
  const topOpen = index < 5 ? "open" : "";
  return `<details class="cvpr-idea-card cvpr-filter-target" data-cvpr-track="${esc(idea.track_id || "")}" data-cvpr-gpu-hours="${Number(budget.gpu_hours || 0)}" ${topOpen}><summary><div><span class="cvpr-rank">#${idea.rank}</span><b>${textOf(idea.title)}</b><small>${textOf(idea.track)}</small></div><div class="cvpr-budget"><strong>${budget.max_gpus || 0} GPU · ${budget.gpu_hours || 0}h</strong><span>${budget.wall_days || 0} ${language === "zh" ? "天 Pilot" : "day pilot"}</span></div></summary><div class="cvpr-idea-body"><div class="cvpr-six-grid"><section><h4 data-toc="false">${language === "zh" ? "目的／问题" : "Purpose / problem"}</h4><p>${textOf(idea.purpose)}</p></section><section><h4 data-toc="false">${language === "zh" ? "核心思想" : "Core idea"}</h4><p>${textOf(idea.core_idea)}</p></section><section><h4 data-toc="false">${language === "zh" ? "为什么合理" : "Why it is reasonable"}</h4><p>${textOf(idea.rationale)}</p></section><section><h4 data-toc="false">${language === "zh" ? "方法逻辑" : "Method logic"}</h4><p>${textOf(idea.method_logic)}</p></section><section><h4 data-toc="false">${language === "zh" ? "研究重要性" : "Research importance"}</h4><p>${textOf(idea.importance)}</p></section><section><h4 data-toc="false">${language === "zh" ? "相对优势" : "Comparative advantage"}</h4><p>${textOf(idea.comparative_advantage)}</p></section></div><div class="cvpr-proof-grid"><section><h4 data-toc="false">${language === "zh" ? "最近工作与碰撞边界" : "Nearest work and collision boundary"}</h4><p>${textOf(idea.collision_boundary)}</p><div class="cvpr-chip-row">${(idea.nearest_work || []).map((name) => `<span>${esc(name)}</span>`).join("")}</div></section><section><h4 data-toc="false">${language === "zh" ? "公开资产" : "Public assets"}</h4><p><b>${language === "zh" ? "数据集" : "Datasets"}:</b> ${(idea.datasets || []).map(esc).join(" · ")}</p><p><b>${language === "zh" ? "模型" : "Models"}:</b> ${(idea.models || []).map(esc).join(" · ")}</p></section><section><h4 data-toc="false">${language === "zh" ? "决定性 Pilot" : "Decisive pilot"}</h4><p>${textOf(idea.pilot)}</p><p><b>${language === "zh" ? "主指标" : "Primary metric"}:</b> ${textOf(idea.decisive_metric)}</p></section><section><h4 data-toc="false">${language === "zh" ? "最强对照与停止条件" : "Strongest baseline and Stop rule"}</h4><p>${textOf(idea.strongest_baseline)}</p><p class="cvpr-stop"><b>Stop:</b> ${textOf(idea.stop_condition)}</p></section></div>${renderExperimentProtocol(idea, "CVPR")}${externalReviews.map((review) => `<div class="project-web-gpt-review verdict-${esc(review.verdict)}"><header><b>${language === "zh" ? "agent 项目网页版 GPT 严格审查" : "Agent-project web GPT strict review"}</b><span>${esc(String(review.verdict || "").toUpperCase())}</span></header><p>${esc(review.finding || "")}</p><small><strong>${language === "zh" ? "要求" : "Required action"}:</strong> ${esc(window.localizedReviewAction ? window.localizedReviewAction(idea.id, review, language) : (review.required_action || ""))}</small></div>`).join("")}<div class="cvpr-review-strip">${reviews.map((review) => `<span class="cvpr-review-pass" title="${esc(review.finding || "")}"><i>✓</i>${esc(review.label)} <b>${review.score}/5</b></span>`).join("")}</div></div></details>`;
}
function renderCvprLowResourceBank() {
  const bank = cvprIdeaBank();
  const ideas = bank.passed_ideas || [];
  if (!ideas.length) return `<section class="panel"><h3 id="cvpr-low-resource-bank">${language === "zh" ? "CVPR 低资源 Idea Bank" : "Low-resource CVPR idea bank"}</h3><div class="warning-box">${language === "zh" ? "候选数据尚未生成。请运行 python -m research_pipeline --build-cvpr-bank。" : "The idea artifact has not been generated. Run python -m research_pipeline --build-cvpr-bank."}</div></section>`;
  const trackButtons = [["all",language === "zh" ? "全部方向" : "All tracks"], ...Object.entries(bank.tracks || {}).map(([key,label]) => [key,textOf(label)])];
  const topRows = ideas.slice(0,15).map((idea) => `<tr><td><strong>#${idea.rank}</strong></td><td><a href="#cvpr-${esc(idea.id)}" class="cvpr-jump" data-cvpr-id="${esc(idea.id)}"><b>${textOf(idea.title)}</b></a><small>${textOf(idea.track)}</small></td><td>${textOf(idea.purpose)}</td><td>${textOf(idea.core_idea)}</td><td>${idea.budget.max_gpus} GPU · ${idea.budget.gpu_hours}h</td><td>${idea.priority}</td></tr>`).join("");
  const earlyRejected = (bank.early_rejected || []).map((item) => `<li><b>${esc(item.title)}</b><span>${esc(item.reason)}</span></li>`);
  const structuredBlocked = (bank.blocked_ideas || []).map((item) => `<li class="structured-blocked"><b>${textOf(item.title)}</b><span>${(item.blocking_reasons || []).map(esc).join("；")}</span></li>`);
  const rejected = [...structuredBlocked, ...earlyRejected].join("");
  return `<section class="panel cvpr-bank-panel"><div class="idea-panel-heading"><div><h3 id="cvpr-low-resource-bank">${language === "zh" ? "CVPR 低资源自审查 Idea Bank" : "Self-reviewed low-resource CVPR idea bank"}</h3><p class="section-intro">${language === "zh" ? "先由五类程序化 Reviewer 检查新颖性、视觉不可替代性、科学成立性、主表证据和低资源可行性；优先候选再由你指定 agent 项目中的网页版 GPT 严格复核。仅展示未被阻断、使用公开资产且 Pilot 不超过 2 张 GPU／48 GPU 小时的候选。" : "Five programmatic reviewers first check novelty, visual necessity, scientific validity, decisive evidence, and low-resource feasibility; priority candidates are then reviewed by web GPT inside the designated agent project. Only unblocked candidates using public assets within 2 GPUs / 48 GPU-hours are shown."}</p></div><strong>${ideas.length} ${language === "zh" ? "个通过项" : "passed ideas"}</strong></div><div class="grid cvpr-bank-stats"><div class="stat"><b>${bank.summary.raw_candidates}</b><span>${language === "zh" ? "个初始候选" : "raw candidates"}</span></div><div class="stat"><b>${ideas.length}</b><span>${language === "zh" ? "个五审通过" : "passed five reviews"}</span></div><div class="stat"><b>${bank.summary.blocked_after_structured_review || 0}</b><span>${language === "zh" ? "个结构化阻断" : "structured blocked"}</span></div><div class="stat"><b>${bank.summary.early_rejected}</b><span>${language === "zh" ? "个前置淘汰" : "early rejected"}</span></div><div class="stat"><b>${bank.summary.tracks}</b><span>${language === "zh" ? "个 CVPR 方向" : "CVPR tracks"}</span></div></div><div class="cvpr-filter-bar"><div class="cvpr-track-filters">${trackButtons.map(([key,label],index) => `<button class="cvpr-filter-btn ${index === 0 ? "active" : ""}" data-cvpr-filter-type="track" data-cvpr-filter-value="${esc(key)}">${esc(label)}</button>`).join("")}</div><div class="cvpr-budget-filters"><button class="cvpr-filter-btn active" data-cvpr-filter-type="budget" data-cvpr-filter-value="48">≤48 GPUh</button><button class="cvpr-filter-btn" data-cvpr-filter-type="budget" data-cvpr-filter-value="24">≤24 GPUh</button><button class="cvpr-filter-btn" data-cvpr-filter-type="budget" data-cvpr-filter-value="16">≤16 GPUh</button></div></div><div class="advisor-table-scroll"><table class="matrix cvpr-top-table"><thead><tr><th>${language === "zh" ? "排序" : "Rank"}</th><th>Idea</th><th>${language === "zh" ? "问题" : "Problem"}</th><th>${language === "zh" ? "机制" : "Mechanism"}</th><th>${language === "zh" ? "预算" : "Budget"}</th><th>${language === "zh" ? "优先值" : "Priority"}</th></tr></thead><tbody>${topRows}</tbody></table></div><div id="cvpr-idea-list" class="cvpr-idea-list">${ideas.map((idea,index) => `<div id="cvpr-${esc(idea.id)}">${renderCvprIdeaCard(idea,index)}</div>`).join("")}</div><details class="cvpr-rejected"><summary>${language === "zh" ? `查看 ${(bank.summary.early_rejected || 0) + (bank.summary.blocked_after_structured_review || 0)} 个被阻断／淘汰方向及原因` : `See ${(bank.summary.early_rejected || 0) + (bank.summary.blocked_after_structured_review || 0)} blocked/rejected directions and reasons`}</summary><ul>${rejected}</ul></details></section>`;
}

function p0ExperimentPlan() {
  return window.P0_EXPERIMENT_PLAN || {summary:{},policy:{},ideas:[]};
}
function p0RuntimeReadiness() {
  return window.P0_RUNTIME_READINESS || {environment_ready:false,launch_ready:false,blockers:["runtime-preflight-not-generated"],python_modules:{},gpus:[],model:{ready:false},alfworld_data:{ready:false},smoke_rollout:{ready:false,status:"missing"},stages:{harness_ready:false,package_ready:false,data_ready:false,smoke_rollout_ready:false,p0_execution_started:false},data_disk_free_gib:0,supported_p0:[]};
}
function p0CollisionRecheck() {
  return window.P0_COLLISION_RECHECK || {ideas:{}};
}
function experimentPilotRegistry() {
  return window.RESEARCH_SYSTEM_STATE?.pilot_registry || {summary:{},policy:{},ideas:[],phases:[]};
}
function experimentPilotPhase(ideaId, phase = "P0") {
  return (experimentPilotRegistry().phases || []).find((row) => row.idea_id === ideaId && row.phase === phase) || null;
}
function experimentPilotIdea(ideaId) {
  return (experimentPilotRegistry().ideas || []).find((row) => row.idea_id === ideaId) || null;
}
function experimentPhaseMeta(status) {
  const map = {
    planned:{tone:"planned",zh:"尚未运行",en:"Not run"},
    running:{tone:"running",zh:"运行中",en:"Running"},
    pass:{tone:"pass",zh:"P0 PASS",en:"P0 PASS"},
    revise:{tone:"revise",zh:"需要修订",en:"Revise"},
    fail:{tone:"fail",zh:"P0 FAIL",en:"P0 FAIL"},
    blocked:{tone:"fail",zh:"已阻断",en:"Blocked"},
  };
  return map[status] || map.planned;
}
function experimentNumber(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return esc(String(value ?? "--"));
  if (Number.isInteger(value)) return String(value);
  return String(Math.round(value * 10000) / 10000);
}
function renderExperimentMetricPairs(values = {}) {
  const entries = Object.entries(values || {});
  if (!entries.length) return `<span class="experiment-empty">${language === "zh" ? "尚无指标" : "No metrics yet"}</span>`;
  return entries.map(([key,value]) => `<span><b>${esc(key.replaceAll("_"," "))}</b><strong>${experimentNumber(value)}</strong></span>`).join("");
}
function renderExperimentPhaseTrack(item) {
  const registry = experimentPilotRegistry();
  const ideaState = experimentPilotIdea(item.id) || {};
  const p0 = experimentPilotPhase(item.id,"P0");
  const p1 = experimentPilotPhase(item.id,"P1");
  const p2 = experimentPilotPhase(item.id,"P2");
  const p0Done = ["pass","revise","fail","blocked"].includes(p0?.status);
  const approval = ideaState.p0_human_approval;
  const cells = [
    {label:"P0",status:p0?.status || "planned",authorized:!!p0?.execution_authorized},
    {label:language === "zh" ? "人工审批" : "Human approval",status:approval ? "pass" : (p0?.status === "pass" ? "running" : "planned"),authorized:p0?.status === "pass"},
    {label:"P1",status:p1?.status || "planned",authorized:!!p1?.execution_authorized},
    {label:"P2",status:p2?.status || "planned",authorized:!!p2?.execution_authorized},
  ];
  return `<div class="experiment-phase-track">${cells.map((cell,index) => { const meta=experimentPhaseMeta(cell.status); return `<div class="experiment-phase-cell phase-${meta.tone} ${cell.authorized ? "phase-authorized" : ""}"><span>${index + 1}</span><b>${esc(cell.label)}</b><small>${language === "zh" ? meta.zh : meta.en}${cell.authorized && cell.status === "planned" ? (language === "zh" ? " · 已授权" : " · authorized") : ""}</small></div>`; }).join("")}</div>`;
}
function renderLiveP0Result(item, phase) {
  if (!phase?.result) {
    const blocked = phase?.blocked_by;
    return `<section class="experiment-live-result result-pending"><header><b>${language === "zh" ? "当前执行状态" : "Current execution state"}</b><span>${phase?.execution_authorized ? (language === "zh" ? "P0 已授权" : "P0 authorized") : (language === "zh" ? "P0 未授权" : "P0 locked")}</span></header><p>${blocked ? `${language === "zh" ? "阻塞原因" : "Blocked by"}: ${esc(blocked)}` : (language === "zh" ? "尚未写入真实 P0 结果；页面将在结果进入 registry 后自动显示效果、成本与决策。" : "No executed P0 result is registered yet. Effects, cost, and decision will appear automatically after ingestion.")}</p></section>`;
  }
  const result = phase.result;
  const meta = experimentPhaseMeta(result.result);
  return `<section class="experiment-live-result result-${meta.tone}"><header><b>${language === "zh" ? "真实 P0 结果" : "Executed P0 result"}</b><span>${language === "zh" ? meta.zh : meta.en}</span></header><div class="experiment-result-metrics">${renderExperimentMetricPairs(result.metrics)}</div><div class="experiment-result-cost">${renderExperimentMetricPairs(result.cost)}</div><p><strong>${language === "zh" ? "诊断" : "Diagnosis"}:</strong> ${esc(result.diagnosis || "--")}</p><p><strong>${language === "zh" ? "下一步" : "Next"}:</strong> ${esc(phase.next_action || result.next_action || "--")}</p></section>`;
}
function p0StatusMeta(status) {
  const map = {
    ready:{tone:"ready",zh:"P0 可准备",en:"P0 ready"},
    "pre-p0-repair":{tone:"redesign",zh:"Pre-P0 前置门未过",en:"Pre-P0 repair required"},
    "collision-recheck":{tone:"check",zh:"先查直接碰撞",en:"Collision recheck first"},
    "method-redesign":{tone:"redesign",zh:"fresh recheck 后方法重构",en:"Method redesign after fresh recheck"},
    "scenario-check":{tone:"hold",zh:"先确认真实场景",en:"Scenario confirmation first"},
  };
  return map[status] || {tone:"hold",zh:"暂不运行",en:"Not executable"};
}
function renderP0ExperimentBoard() {
  const plan = p0ExperimentPlan();
  const summary = plan.summary || {};
  const policy = plan.policy || {};
  const cards = (plan.ideas || []).map((item) => {
    const phase = experimentPilotPhase(item.id,"P0");
    const plannedStatus = p0StatusMeta(item.status);
    const executedStatus = experimentPhaseMeta(phase?.status);
    const status = phase?.status && phase.status !== "planned" ? {tone:executedStatus.tone,zh:executedStatus.zh,en:executedStatus.en} : plannedStatus;
    const resource = item.resource || {};
    const prerequisites = (item.prerequisites || []).map((row) => `<li>${textOf(row)}</li>`).join("");
    const outputs = (item.outputs || []).map((name) => `<span>${esc(name)}</span>`).join("");
    const collision = (p0CollisionRecheck().ideas || {})[item.id];
    const collisionWorks = (collision?.closest_work || []).map((work) => `<a href="${esc(work.url)}" target="_blank" rel="noopener">${esc(work.title)} <small>${esc(String(work.year || ""))}</small></a>`).join("");
    const collisionBlock = collision ? `<details class="p0-collision-result"><summary>${language === "zh" ? "2026-08-09 fresh collision 复查结果" : "Fresh collision recheck · 2026-08-09"}<span>${esc(String(collision.verdict || "").toUpperCase())}</span></summary><div><p>${textOf(collision.finding)}</p><b>${language === "zh" ? "必须怎么改" : "Required redesign"}</b><p>${textOf(collision.required_action)}</p>${collisionWorks ? `<nav>${collisionWorks}</nav>` : ""}</div></details>` : "";
    return `<details id="exp-${esc(String(item.code || "").toLowerCase())}" class="p0-plan-card p0-tone-${status.tone}" data-p0-status="${esc(item.status || "")}" data-p0-phase-status="${esc(phase?.status || "planned")}" data-p0-authorized="${phase?.execution_authorized ? "1" : "0"}">
      <summary><span class="p0-plan-code">${esc(item.code || "")}</span><div class="p0-plan-title"><b>${textOf(item.title)}</b><small>${language === "zh" ? status.zh : status.en}</small></div><p>${textOf(item.question)}</p><div class="p0-plan-budget"><b>${resource.max_gpus || 0} GPU · ≤${resource.gpu_hours_cap || 0} GPUh</b><span>${language === "zh" ? `最多 ${resource.episode_cap || 0} 次任务执行` : `≤${resource.episode_cap || 0} task episodes`}</span></div><div class="p0-plan-next">${textOf(item.next_action)}</div></summary>
      <div class="p0-plan-body">
        ${renderExperimentPhaseTrack(item)}
        ${renderLiveP0Result(item, phase)}
        ${prerequisites ? `<section class="p0-prerequisite"><b>${language === "zh" ? "运行前必须先完成" : "Must clear before execution"}</b><ul>${prerequisites}</ul></section>` : ""}
        ${collisionBlock}
        <div class="p0-plan-grid">
          <section><b>${language === "zh" ? "这轮刻意不做什么" : "Deliberately out of scope"}</b><p>${textOf(item.scope)}</p></section>
          <section class="p0-wide"><b>${language === "zh" ? "最小实验怎么做" : "Smallest experiment"}</b><p>${textOf(item.design)}</p></section>
          <section><b>${language === "zh" ? "和谁比" : "Fair baselines"}</b><p>${textOf(item.baselines)}</p></section>
          <section><b>${language === "zh" ? "谁来判对错" : "Independent truth"}</b><p>${textOf(item.truth)}</p></section>
          <section><b>${language === "zh" ? "最后主要看哪张表" : "Decision table"}</b><p>${textOf(item.metrics)}</p></section>
          <section class="p0-go"><b>Go</b><p>${textOf(item.go)}</p></section>
          <section class="p0-stop"><b>Stop</b><p>${textOf(item.stop)}</p></section>
          <section><b>${language === "zh" ? "资源硬上限" : "Hard resource cap"}</b><p>${resource.max_gpus || 0} GPU · ${resource.gpu_hours_cap || 0} GPUh · ${resource.wall_hours_cap || 0}h wall · ≤${resource.episode_cap || 0} episodes</p></section>
        </div>
        <div class="p0-output-row"><b>${language === "zh" ? "跑完必须留下" : "Required artifacts"}</b>${outputs}</div>
        <a class="link-btn p0-idea-link" href="${pageId === "paper-ideas" ? "" : "paper-ideas.html"}#idea-${esc(String(item.code || "").toLowerCase())}">${language === "zh" ? "回到这个 Idea 的完整说明 →" : "Open the full idea →"}</a>
      </div>
    </details>`;
  }).join("");
  return `<section class="panel p0-control-board" id="p0-experiment-board"><div class="p0-board-head"><div><div class="eyebrow">P0 · ${language === "zh" ? "实验准备" : "EXPERIMENT PREPARATION"}</div><h2 data-toc="false">${language === "zh" ? "实验准备与执行队列" : "Experiment preparation and execution queue"}</h2><p>${language === "zh" ? "这里只展示真正需要做决定的 5 个小 P0。先看能不能跑，再看最小实验、主表和 Stop；完整论文级 P1/P2 不在这里提前展开。" : "This board contains only the five small P0 decisions that matter now. First check whether execution is unlocked, then read the smallest test, decision table, and Stop rule; paper-scale P1/P2 remains out of scope."}</p></div><strong>${summary.ready_now || 0}/${summary.planned || 0}<span>${language === "zh" ? "当前可准备" : "ready now"}</span></strong></div>
    <div class="p0-policy-lock"><b>${language === "zh" ? "硬门禁" : "Hard gate"}</b><span>${language === "zh" ? `先通过 Pre-P0 十项可识别性审计，才允许小 P0。P0 PASS 也不会自动进入 P1，必须先回到人工审查。目前 P0 授权数 = ${experimentPilotRegistry().summary?.p0_authorized || 0}，P1 授权数 = ${summary.p1_authorized || 0}。` : `A small P0 is executable only after all ten Pre-P0 identifiability gates pass. A P0 PASS still never auto-escalates to P1 and must return to human review. Current P0 authorizations = ${experimentPilotRegistry().summary?.p0_authorized || 0}; P1 authorizations = ${summary.p1_authorized || 0}.`}</span></div>
    <div class="p0-board-stats"><div><b>${summary.ready_now || 0}</b><span>${language === "zh" ? "现在可执行" : "executable now"}</span></div><div><b>${summary.pre_p0_blocked || 0}</b><span>${language === "zh" ? "Pre-P0 被挡" : "Pre-P0 blocked"}</span></div><div><b>${summary.method_redesign || summary.collision_recheck || 0}</b><span>${language === "zh" ? "方法重构" : "method redesign"}</span></div><div><b>${summary.scenario_check || 0}</b><span>${language === "zh" ? "先确认场景" : "scenario check"}</span></div><div><b>${summary.gpu_hours_cap_ready_now || 0}</b><span>${language === "zh" ? "当前可授权 GPUh" : "authorized GPUh cap"}</span></div><div><b>${summary.p1_authorized || 0}</b><span>P1 ${language === "zh" ? "已授权" : "authorized"}</span></div></div>
    <div class="p0-reading-note"><b>${language === "zh" ? "建议执行顺序" : "Suggested order"}</b><span>${language === "zh" ? "先做不耗或极少 GPU 的 Pre-P0 repair-readiness：A-1 表示可实现性与 tiny-overfit，A-2 target entropy / sequence disagreement，B-1 utility-only vs process-robust disagreement mining，E-1 pairwise/listwise ranking alignment。只有对应硬门全部 PASS，才重新计算推理预算并启动小 P0。F-1 仍等真实场景确认。" : "First run the offline or near-zero-GPU Pre-P0 repair-readiness checks: A-1 representation realizability/tiny overfit, A-2 target entropy and sequence disagreement, B-1 utility-only vs process-robust disagreement mining, and E-1 pairwise/listwise ranking alignment. Only after all relevant gates pass should inference cost be recomputed and a small P0 launched. F-1 still awaits scenario confirmation."}</span></div>
    <div class="p0-plan-list">${cards}</div>
  </section>`;
}
function renderP0ExperimentEntry() {
  const plan = p0ExperimentPlan();
  const summary = plan.summary || {};
  const registry = experimentPilotRegistry();
  const executed = (plan.ideas || []).filter((item) => !!experimentPilotPhase(item.id,"P0")?.result).length;
  const execution = p0RuntimeReadiness()?.execution_state || {};
  const registryRunning = (plan.ideas || []).filter((item) => experimentPilotPhase(item.id,"P0")?.status === "running").length;
  const running = registryRunning || (String(execution.status || "").toLowerCase() === "running" ? 1 : 0);
  return `<section class="panel p0-entry-panel"><div><div class="eyebrow">P0 · ${language === "zh" ? "实验入口" : "EXPERIMENT TRACKER"}</div><h3 id="experiment-tracker-entry" data-toc="false">${language === "zh" ? "实验计划、进展和结果已移到独立页面" : "Experiment plans, progress, and results now live on a separate page"}</h3><p>${language === "zh" ? "Idea 页只保留科学问题与方法论证；实验页集中维护执行授权、前置条件、实际运行状态、效果、资源消耗、Go/Stop 与人工审批。" : "The idea page now focuses on scientific problems and mechanisms. The experiment page owns execution gates, prerequisites, live status, measured effects, resource use, Go/Stop decisions, and human approvals."}</p></div><div class="p0-entry-stats"><span><b>${summary.planned || 0}</b>${language === "zh" ? "个 P0" : "P0 plans"}</span><span><b>${summary.ready_now || 0}</b>${language === "zh" ? "已解锁" : "unlocked"}</span><span><b>${running}</b>${language === "zh" ? "运行中" : "running"}</span><span><b>${executed}</b>${language === "zh" ? "已有结果" : "with results"}</span><span><b>${registry.summary?.p1_authorized || 0}</b>P1 ${language === "zh" ? "授权" : "authorized"}</span></div><a class="link-btn p0-entry-link" href="experiments.html">${language === "zh" ? "打开实验进展与结果页 →" : "Open Experiment Progress & Results →"}</a></section>`;
}
function renderP0RuntimeReadiness() {
  const runtime = p0RuntimeReadiness();
  const gpu = (runtime.gpus || [])[0] || {};
  const modules = runtime.python_modules || {};
  const supported = new Set(runtime.supported_p0 || []);
  const stages = runtime.stages || {};
  const blockerRows = (runtime.blockers || []).map((item) => `<li>${esc(item)}</li>`).join("");
  const execution = runtime.execution_state || {};
  const executionStatus = String(execution.status || "").toLowerCase();
  const executionLabels = {running:{zh:"运行中",en:"RUNNING"},collected:{zh:"采集完成",en:"COLLECTED"},registered:{zh:"已登记",en:"REGISTERED"},failed:{zh:"运行失败",en:"FAILED"}};
  const status = executionStatus === "running" ? {tone:"running",zh:"真实 P0 运行中",en:"Real P0 running"} : executionStatus === "collected" ? {tone:"check",zh:"采集完成，待登记",en:"Collected; registration pending"} : executionStatus === "registered" ? {tone:"pass",zh:"P0 结果已登记",en:"P0 result registered"} : executionStatus === "failed" ? {tone:"fail",zh:"P0 运行失败",en:"P0 execution failed"} : runtime.launch_ready ? {tone:"pass",zh:"可启动真实 P0",en:"P0 launch ready"} : (runtime.environment_ready ? {tone:"check",zh:"环境通过，待 smoke",en:"Runtime ready; smoke pending"} : {tone:"revise",zh:"环境未就绪",en:"Runtime not ready"});
  const executionLabel = executionLabels[executionStatus] || {zh:"未启动",en:"PENDING"};
  const stageRows = [
    ["harness_ready", language === "zh" ? "Harness" : "Harness"],
    ["package_ready", language === "zh" ? "ALFWorld + TextWorld" : "ALFWorld + TextWorld"],
    ["data_ready", language === "zh" ? "PDDL / game 数据" : "PDDL / game data"],
    ["smoke_rollout_ready", language === "zh" ? "轻量 runtime smoke" : "lightweight runtime smoke"],
  ].map(([key,label],index) => `<span class="runtime-stage ${stages[key] ? "stage-pass" : "stage-pending"}"><i>${index+1}</i><b>${esc(label)}</b><small>${stages[key] ? (language === "zh" ? "通过" : "PASS") : (language === "zh" ? "未完成" : "PENDING")}</small></span>`).join("") + `<span class="runtime-stage ${executionStatus === "failed" ? "stage-fail" : (stages.p0_execution_started ? "stage-pass" : "stage-pending")}"><i>5</i><b>${language === "zh" ? "正式 P0" : "formal P0"}</b><small>${language === "zh" ? executionLabel.zh : executionLabel.en}</small></span>`;
  return `<section class="panel experiment-runtime-panel"><div class="idea-panel-heading"><div><h3 id="p0-runtime-readiness" data-toc="false">${language === "zh" ? "P0 运行环境 readiness" : "P0 runtime readiness"}</h3><p class="section-intro">${language === "zh" ? "科学授权、harness、依赖、数据、轻量 runtime smoke 和正式实验分开记账。轻量 smoke 只验证 Qwen tokenizer/chat template、各权重 shard 可读，以及真实 ALFWorld OOD 的 reset → parser → env.step；完整 7B 权重加载与生成只在正式 P0 事务里验证，失败不会登记科学结果。" : "Scientific authorization, harness, dependencies, data, a lightweight runtime smoke, and formal execution are tracked separately. The smoke checks the Qwen tokenizer/chat template, readability of every weight shard, and a real ALFWorld OOD reset → parser → env.step. Full 7B loading/generation is validated only by the formal P0 transaction, and failures cannot be registered as scientific results."}</p></div><span class="experiment-status-badge status-${status.tone}">${language === "zh" ? status.zh : status.en}</span></div><div class="experiment-runtime-stages">${stageRows}</div><div class="experiment-runtime-grid"><div><b>${gpu.name ? esc(gpu.name) : "--"}</b><span>${gpu.memory_free_mib ? `${Math.round(gpu.memory_free_mib/1024)} GB ${language === "zh" ? "空闲显存" : "VRAM free"}` : (language === "zh" ? "未检测到 GPU" : "No GPU detected")}</span></div><div><b>${runtime.model?.ready ? "YES" : "NO"}</b><span>${language === "zh" ? "Qwen2.5-7B 本地模型" : "local Qwen2.5-7B"}</span></div><div><b>${experimentNumber(runtime.data_disk_free_gib || 0)} GB</b><span>${language === "zh" ? "实验数据盘空闲" : "experiment disk free"}</span></div><div><b>${supported.has("update-trust-region") ? "YES" : "NO"}</b><span>A-1 harness</span></div><div><b>${supported.has("budgeted-evolution-controller") ? "YES" : "NO"}</b><span>A-2 harness</span></div><div><b>${Object.values(modules).filter(Boolean).length}/${Object.keys(modules).length || 3}</b><span>${language === "zh" ? "Python 运行依赖" : "Python runtime deps"}</span></div><div><b>${runtime.alfworld_data?.ready ? "YES" : "NO"}</b><span>${language === "zh" ? "ALFWorld PDDL / game 数据" : "ALFWorld PDDL / game data"}</span></div></div>${blockerRows ? `<div class="experiment-runtime-blockers"><b>${language === "zh" ? "当前阻塞" : "Current blockers"}</b><ul>${blockerRows}</ul></div>` : (runtime.smoke_rollout?.ready ? `<div class="experiment-runtime-ready">${language === "zh" ? "机器依赖、数据和轻量 runtime smoke 均通过；已授权 P0 现在可以启动，但尚未产生任何实验效果。" : "Machine dependencies, data, and the lightweight runtime smoke all pass; authorized P0s may now launch, but no experimental effect has been measured yet."}</div>` : `<div class="experiment-runtime-blockers"><b>${language === "zh" ? "下一步" : "Next"}</b><ul><li>${language === "zh" ? "先完成轻量 runtime smoke：Qwen tokenizer/权重 shard 可读 + ALFWorld OOD 单步链路；通过后 collect 才解锁。" : "First clear the lightweight runtime smoke: Qwen tokenizer/weight-shard readability plus one ALFWorld OOD environment step; collection unlocks only after it passes."}</li></ul></div>`)}</section>`;
}
function preP0IdentifiabilityState() {
  return window.RESEARCH_SYSTEM_STATE?.pre_p0_identifiability || {summary:{},policy:{},checks:[],nodes:[]};
}
function preP0CheckLabel(key="") {
  const labels={
    claim_alignment:["主张 ↔ 训练目标","Claim ↔ objective"],target_variation:["目标有变化","Target variation"],baseline_disagreement:["方法与简化版会分歧","Baseline disagreement"],representability:["表示可表达机制","Representability"],tiny_overfit:["小样本可拟合","Tiny-set overfit"],competence_window:["基础 Agent 可研究","Competence window"],effect_variation:["更新效应有变化","Effect variation"],cost_plan:["推理与时间先算账","Cost plan"],provenance_plan:["增量证据可追溯","Provenance plan"],interpretation_matrix:["结果解释预注册","Outcome interpretation"]
  };
  return language === "zh" ? (labels[key]?.[0] || key) : (labels[key]?.[1] || key);
}
function renderPreP0IdentifiabilityPanel() {
  const state=preP0IdentifiabilityState(); const nodes=state.nodes||[]; if(!nodes.length) return "";
  const cards=nodes.map((node)=>{
    const checks=(node.checks||[]).map((row)=>`<span class="${row.pass ? "pass" : "fail"}" title="${esc(row.evidence || row.question || "")}"><i>${row.pass ? "✓" : "×"}</i>${esc(preP0CheckLabel(row.key))}</span>`).join("");
    const blockers=(node.blockers||[]).map((key)=>`<b>${esc(preP0CheckLabel(key))}</b>`).join("");
    return `<article class="pre-p0-card ${node.execution_ready ? "ready" : "blocked"}" data-pre-p0="${esc(node.status||"")}"><header><span>${esc(node.code||"--")}</span><div><b>${node.execution_ready ? (language==="zh"?"允许启动 P0":"P0 executable") : (language==="zh"?"GPU 前先修":"Repair before GPU")}</b><small>${node.passed||0}/${node.total||10} ${language==="zh"?"项通过":"checks passed"} · VOI ${esc(node.estimated_voi||"--")}</small></div></header><div class="pre-p0-checks">${checks}</div>${blockers ? `<div class="pre-p0-blockers"><span>${language==="zh"?"当前阻塞":"Blockers"}</span>${blockers}</div>`:""}<p>${esc(node.required_next||"")}</p></article>`;
  }).join("");
  return `<section class="panel pre-p0-panel"><div class="idea-panel-heading"><div><h3 id="pre-p0-identifiability" data-toc="false">${language==="zh"?"Pre-P0 · 实验可识别性审计":"Pre-P0 · Identifiability audit"}</h3><p class="section-intro">${language==="zh"?"先证明实验有能力区分方法，再允许消耗 GPU。十项硬门覆盖主张—目标对齐、标签/效应变化、方法与最强简化是否会产生分歧、表示与小样本拟合能力、基础 Agent 难度窗口、成本和可追溯性，以及结果解释矩阵。任一项失败，P0 execution_authorized=false。":"Prove that the experiment can distinguish the mechanism before spending GPU. Ten hard gates cover claim alignment, target/effect variation, disagreement with the strongest simplification, representability and tiny-set fitting, substrate competence, cost/provenance, and preregistered outcome interpretation. Any failure keeps P0 execution_authorized=false."}</p></div><strong>${state.summary?.execution_ready||0}/${state.summary?.audited||0} READY</strong></div><div class="pre-p0-grid">${cards}</div></section>`;
}
function experimentIterationState() {
  return window.RESEARCH_SYSTEM_STATE?.experiment_iteration || {summary:{},policy:{},nodes:[],references:[]};
}
function experimentDiagnosisMeta(name="") {
  const map = {
    "representation-signal-mismatch":{tone:"mechanism",zh:"表示／学习信号不匹配",en:"Representation / signal mismatch"},
    "no-label-variation":{tone:"experiment",zh:"目标没有足够变化",en:"No target variation"},
    "matched-simplification-tie":{tone:"simplify",zh:"与更简单方法打平",en:"Matched simplification tie"},
    "objective-claim-mismatch":{tone:"mechanism",zh:"训练目标与论文主张不一致",en:"Objective / claim mismatch"},
    "substrate-degenerate":{tone:"experiment",zh:"实验基座退化",en:"Degenerate substrate"},
    "underfit":{tone:"optimization",zh:"尚未拟合",en:"Underfit"},
    "positive-signal":{tone:"positive",zh:"可汇报正向 P0",en:"Positive P0 signal"},
    "true-negative":{tone:"negative",zh:"可识别的真实负结果",en:"Identifiable negative"},
  };
  return map[name] || {tone:"neutral",zh:name || "未诊断",en:name || "Undiagnosed"};
}
function renderExperimentIterationPanel() {
  const state = experimentIterationState();
  const nodes = state.nodes || [];
  if (!nodes.length) return "";
  const cards = nodes.map((node) => {
    const meta = experimentDiagnosisMeta(node.diagnosis);
    const children = (node.repair_children || []).map((child,index) => `<li><b>${esc(child.child || `${language === "zh" ? "原子修复" : "Atomic repair"} ${index+1}`)}</b><span>${esc(child.changed_variable || "")}</span>${child.precondition ? `<small>${language === "zh" ? "重跑前条件" : "Precondition"}: ${esc(child.precondition)}</small>` : ""}</li>`).join("");
    const belief = node.scientific_belief_update_allowed;
    const identifiable = node.experiment_identifiable;
    return `<article class="experiment-diagnosis-card diagnosis-${meta.tone}" data-diagnosis="${esc(node.diagnosis || "")}">
      <header><span>${esc(node.code || "")}</span><div><b>${language === "zh" ? meta.zh : meta.en}</b><small>${esc(node.diagnosis || "")}</small></div></header>
      <div class="experiment-diagnosis-flags"><span class="${identifiable ? "yes" : "no"}">${language === "zh" ? "实验可判方法" : "Experiment identifiable"}: ${identifiable ? "YES" : "NO"}</span><span class="${belief ? "yes" : "no"}">${language === "zh" ? "允许更新科学判断" : "Scientific belief update"}: ${belief ? "YES" : "NO"}</span><span class="no">${language === "zh" ? "扩大实验" : "Scale up"}: NO</span></div>
      ${children ? `<ol>${children}</ol>` : `<p>${language === "zh" ? "当前不生成自动修复子节点。" : "No automatic repair child is generated."}</p>`}
    </article>`;
  }).join("");
  const refs = (state.references || []).map((item) => `<a href="${esc(item.url || "#")}" target="_blank" rel="noopener"><b>${esc(item.system || "")}</b><span>${esc(item.adopted || "")}</span></a>`).join("");
  return `<section class="panel experiment-iteration-panel"><div class="idea-panel-heading"><div><h3 id="experiment-diagnosis-repair" data-toc="false">${language === "zh" ? "实验诊断与原子修复树" : "Experiment diagnosis and atomic repair tree"}</h3><p class="section-intro">${language === "zh" ? "P0 没过不再自动等于 Idea 不成立。先判断这次实验是否有资格评价方法：基座、目标变化、拟合、训练目标和简化对照分别诊断；只有 experiment_identifiable=true 的结果才允许改变科学判断。每次修复只改一个变量。" : "A failed P0 no longer automatically means the idea is invalid. First diagnose whether the experiment can evaluate the mechanism at all: substrate, target variation, optimization, objective alignment, and matched simplification are separated. Only experiment_identifiable=true may update scientific belief, and every repair changes one variable."}</p></div><strong>${state.summary?.repair_children || 0} ${language === "zh" ? "个修复子节点" : "repair children"}</strong></div><div class="experiment-iteration-summary"><span><b>${state.summary?.nodes || 0}</b>${language === "zh" ? "已诊断 Pilot" : "diagnosed pilots"}</span><span><b>${state.summary?.identifiable || 0}</b>${language === "zh" ? "实验可识别" : "identifiable"}</span><span><b>${state.summary?.belief_updates_allowed || 0}</b>${language === "zh" ? "可更新科学判断" : "belief updates allowed"}</span><span><b>${state.summary?.scale_up_allowed || 0}</b>${language === "zh" ? "允许扩大" : "scale-up allowed"}</span></div><div class="experiment-diagnosis-grid">${cards}</div><details class="experiment-research-patterns"><summary>${language === "zh" ? "这套流程参考了哪些自动科研系统" : "Autonomous research systems informing this workflow"}</summary><div>${refs}</div></details></section>`;
}
function renderExperimentResourceLedger() {
  const plan = p0ExperimentPlan();
  const p0Phases = (plan.ideas || []).map((item) => experimentPilotPhase(item.id,"P0")).filter(Boolean);
  const results = p0Phases.map((phase) => phase.result).filter(Boolean);
  const spent = results.reduce((sum,row) => sum + Number(row.cost?.gpu_hours || 0), 0);
  const calls = results.reduce((sum,row) => sum + Number(row.cost?.model_calls || 0), 0);
  const tokens = results.reduce((sum,row) => sum + Number(row.cost?.tokens || 0), 0);
  const wall = results.reduce((sum,row) => sum + Number(row.cost?.wall_clock_hours || 0), 0);
  const authorizedCap = (plan.ideas || []).filter((item) => experimentPilotPhase(item.id,"P0")?.execution_authorized).reduce((sum,item) => sum + Number(item.resource?.gpu_hours_cap || 0), 0);
  const allCap = Number(plan.summary?.gpu_hours_cap_if_all_unlocked || 0);
  return `<section class="panel experiment-ledger"><div class="idea-panel-heading"><div><h3 id="experiment-resource-ledger">${language === "zh" ? "资源账本" : "Resource ledger"}</h3><p class="section-intro">${language === "zh" ? "预算上限来自冻结 P0 计划；实际消耗只从已登记的真实结果文件累计。" : "Caps come from the frozen P0 plans; actual usage is accumulated only from registered executed-result files."}</p></div><strong>${experimentNumber(spent)} / ${authorizedCap} GPUh</strong></div><div class="experiment-ledger-grid"><div><b>${experimentNumber(spent)}</b><span>${language === "zh" ? "已消耗 GPUh" : "GPUh spent"}</span></div><div><b>${authorizedCap}</b><span>${language === "zh" ? "当前授权上限" : "authorized cap"}</span></div><div><b>${allCap}</b><span>${language === "zh" ? "当前仍有效方案上限" : "current valid-plan cap"}</span></div><div><b>${experimentNumber(wall)}</b><span>${language === "zh" ? "累计墙钟小时" : "wall-clock hours"}</span></div><div><b>${experimentNumber(calls)}</b><span>${language === "zh" ? "模型调用" : "model calls"}</span></div><div><b>${experimentNumber(tokens)}</b><span>tokens</span></div></div></section>`;
}
function renderExperimentResultsSnapshot() {
  const plan = p0ExperimentPlan();
  const runtimeExecution = p0RuntimeReadiness()?.execution_state || {};
  const rows = (plan.ideas || []).map((item) => {
    const phase = experimentPilotPhase(item.id,"P0");
    const result = phase?.result;
    const liveStatus = runtimeExecution.idea_id === item.id ? String(runtimeExecution.status || "").toLowerCase() : "";
    const liveMeta = liveStatus === "running" ? {tone:"running",zh:"运行中",en:"Running"} : liveStatus === "collected" ? {tone:"check",zh:"采集完成，待登记",en:"Collected, pending registration"} : liveStatus === "failed" ? {tone:"fail",zh:"运行失败",en:"Execution failed"} : liveStatus === "registered" ? {tone:"pass",zh:"已登记",en:"Registered"} : null;
    const status = result ? experimentPhaseMeta(result.result) : (liveMeta || (phase?.execution_authorized ? {tone:"ready",zh:"已授权，未运行",en:"Authorized, not run"} : p0StatusMeta(item.status)));
    const metrics = result ? Object.entries(result.metrics || {}).slice(0,4).map(([key,value]) => `${esc(key.replaceAll("_"," "))}=${experimentNumber(value)}`).join(" · ") : (language === "zh" ? "尚无真实效果数据" : "No measured effect yet");
    const cost = result ? `${experimentNumber(result.cost?.gpu_hours || 0)} GPUh · ${experimentNumber(result.cost?.model_calls || 0)} calls · ${experimentNumber(result.cost?.tokens || 0)} tokens · ${experimentNumber(result.cost?.environment_episodes || 0)} episodes` : `0 / ${item.resource?.gpu_hours_cap || 0} GPUh`;
    return `<tr><td><a href="#exp-${esc(item.code.toLowerCase())}"><strong>${esc(item.code)}</strong><small>${textOf(item.title)}</small></a></td><td><span class="experiment-status-badge status-${esc(status.tone)}">${language === "zh" ? status.zh : status.en}</span></td><td>${metrics}</td><td>${esc(cost)}</td><td>${esc(phase?.next_action || textOf(item.next_action) || "--")}</td></tr>`;
  }).join("");
  return `<section class="panel experiment-results-panel"><div class="idea-panel-heading"><div><h3 id="experiment-results-snapshot">${language === "zh" ? "结果与效果总表" : "Results and effect snapshot"}</h3><p class="section-intro">${language === "zh" ? "这里不复制人工填写的结论；只显示 Pilot registry 中真正存在的结果、指标和成本。尚未运行的实验明确显示为无效果数据。" : "This table does not duplicate hand-written conclusions. It only renders results, metrics, and cost that actually exist in the pilot registry; unrun experiments explicitly show no measured effect."}</p></div></div><div class="advisor-table-scroll"><table class="matrix experiment-results-table"><thead><tr><th>Idea</th><th>${language === "zh" ? "状态" : "Status"}</th><th>${language === "zh" ? "已测效果" : "Measured effect"}</th><th>${language === "zh" ? "实际成本" : "Actual cost"}</th><th>${language === "zh" ? "下一步" : "Next"}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}
function renderExperimentApprovalPanel() {
  const plan = p0ExperimentPlan();
  const registry = experimentPilotRegistry();
  const rows = (plan.ideas || []).map((item) => {
    const state = experimentPilotIdea(item.id) || {};
    const p0 = experimentPilotPhase(item.id,"P0");
    const p1 = experimentPilotPhase(item.id,"P1");
    const p0Result = p0?.result?.result || "--";
    const approval = state.p0_human_approval;
    return `<tr><td><strong>${esc(item.code)}</strong><small>${textOf(item.title)}</small></td><td>${esc(p0Result)}</td><td>${approval ? `<span class="experiment-status-badge status-pass">${language === "zh" ? "已批准" : "Approved"}</span>` : `<span class="experiment-status-badge status-planned">${p0Result === "pass" ? (language === "zh" ? "等待人工审批" : "Awaiting human approval") : (language === "zh" ? "尚不适用" : "Not applicable yet")}</span>`}</td><td>${p1?.execution_authorized ? `<b class="experiment-auth-yes">YES</b>` : `<b class="experiment-auth-no">NO</b>`}</td></tr>`;
  }).join("");
  return `<section class="panel experiment-approval-panel"><div class="idea-panel-heading"><div><h3 id="experiment-human-approval">${language === "zh" ? "人工审批与下一阶段锁" : "Human approvals and next-phase locks"}</h3><p class="section-intro">${language === "zh" ? "P0 PASS 后必须先回到人工讨论。没有显式 approval artifact，P1 的 execution_authorized 永远为 false。" : "Every P0 PASS returns to human review. Without an explicit approval artifact, P1 execution_authorized remains false."}</p></div><strong>P1 = ${registry.summary?.p1_authorized || 0}</strong></div><div class="experiment-gate-summary"><span><b>${registry.summary?.valid_approval_files || 0}</b>${language === "zh" ? "有效审批文件" : "valid approvals"}</span><span><b>${registry.summary?.awaiting_human_approval || 0}</b>${language === "zh" ? "等待审批" : "awaiting approval"}</span><span><b>${registry.summary?.p0_authorized || 0}</b>P0 ${language === "zh" ? "已授权" : "authorized"}</span><span><b>${registry.summary?.p1_authorized || 0}</b>P1 ${language === "zh" ? "已授权" : "authorized"}</span></div><div class="advisor-table-scroll"><table class="matrix experiment-approval-table"><thead><tr><th>Idea</th><th>P0</th><th>${language === "zh" ? "人工审批" : "Human approval"}</th><th>P1 authorized</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}
function renderExperimentDashboard(config) {
  const chapters = pageArchitecture("experiments").chapters || [];
  const queue = `${renderPreP0IdentifiabilityPanel()}${renderP0RuntimeReadiness()}${renderP0ExperimentBoard()}`;
  const results = `${renderExperimentResourceLedger()}${renderExperimentIterationPanel()}${renderExperimentResultsSnapshot()}`;
  const approvals = renderExperimentApprovalPanel();
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("experiments"))}${renderCustomChapter(chapters[0],0,queue)}${renderCustomChapter(chapters[1],1,results)}${renderCustomChapter(chapters[2],2,approvals)}`;
}
function renderIdeaPortfolio(config) {
  const chapters = pageArchitecture("paper-ideas").chapters || [];
  const discussed = renderDiscussedIdeaBank();
  const newIdeas = renderNewIdeaCandidates();
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("paper-ideas"))}${renderP0ExperimentEntry()}${renderCustomChapter(chapters[0],0,discussed)}${renderCustomChapter(chapters[1],1,newIdeas)}`;
}
function renderIdeaRanking(config) {
  return `${pageHeader(config)}${(config.sections || []).map(renderSection).join("")}${renderIdeaRankingPanels()}`;
}
function historyFigureData() { return window.AGENT_HISTORY_FIGURE || null; }
function historyIdeaLevel(level = 0) {
  return `<span class="history-level" aria-label="${level} of 5">${[1,2,3,4,5].map((n) => `<i class="${n <= level ? "on" : ""}"></i>`).join("")}</span>`;
}
function historyPaperHref(title) {
  const slug = slugify(title);
  return `bibliography.html?paper=${encodeURIComponent(slug)}#ref-${slug}`;
}
function renderHistoryFigure() {
  const data = historyFigureData();
  if (!data) return "";
  const stageCards = data.stages.map((stage) => `<article class="history-stage" style="--stage:${esc(stage.color)}"><div class="history-stage-head"><span>${esc(stage.code)}</span><strong>${esc(stage.period)}</strong></div><h3>${textOf(stage.title)}</h3><p class="history-stage-subtitle">${textOf(stage.subtitle)}</p><ul>${stage.bullets[language].map((item) => `<li>${esc(item)}</li>`).join("")}</ul><div class="history-stage-meta"><b>${language === "zh" ? "更新对象" : "Update target"}</b><span>${textOf(stage.target)}</span><b>${language === "zh" ? "反馈" : "Feedback"}</b><span>${textOf(stage.feedback)}</span></div><div class="history-stage-limit">${textOf(stage.limitation)}</div></article>`).join("");
  const expansion = [
    [{en:"Prompt / context",zh:"提示词／上下文"},{en:"Rewrite the current interaction",zh:"改写当前交互"}],
    [{en:"Reasoning trace",zh:"推理轨迹"},{en:"Generate and verify intermediate supervision",zh:"生成并验证中间监督"}],
    [{en:"Memory",zh:"记忆"},{en:"Store, retrieve, repair, and consolidate experience",zh:"存储、检索、修复并巩固经验"}],
    [{en:"Skill / tool",zh:"技能／工具"},{en:"Create reusable executable capabilities",zh:"创建可复用可执行能力"}],
    [{en:"Workflow / model / world",zh:"工作流／模型／世界"},{en:"Evolve the complete agent system under release gates",zh:"在发布门控下进化完整 Agent 系统"}],
  ].map(([title,desc], index) => `<div class="history-expansion-step"><span>${index + 1}</span><b>${textOf(title)}</b><small>${textOf(desc)}</small></div>`).join("");
  const capabilityHead = data.stages.map((stage) => `<th><span>${esc(stage.period)}</span><small>${textOf(stage.title)}</small></th>`).join("");
  const capabilityRows = data.capabilities.map((row) => `<tr><th>${textOf(row.name)}</th>${row.values.map((cell) => `<td>${historyIdeaLevel(cell.l)}<span>${textOf(cell.t)}</span></td>`).join("")}</tr>`).join("");
  const directionRows = data.directions.map((direction) => `<tr><th>${esc(direction.code)}</th><td>${textOf(direction.title)}</td><td>${esc(direction.origin)}</td><td>${esc(direction.growth)}</td><td>${textOf(direction.status)}</td></tr>`).join("");
  const ladder = data.claimLadder.map((level) => `<div class="history-ladder-row"><span>${esc(level.level)}</span><div><b>${textOf(level.title)}</b><small>${textOf(level.question)}</small></div></div>`).join("");
  const milestones = data.milestones.map((paper) => `<a class="history-milestone" href="${historyPaperHref(paper.title)}"><span>${paper.year}</span><b>${esc(paper.short)}</b><small>${esc(paper.venue)}</small><em data-cite="${esc(paper.title)}"></em></a>`).join("");
  const shifts = data.shifts.map((shift) => `<div class="history-shift"><span>${textOf(shift.from)}</span><i>→</i><b>${textOf(shift.to)}</b><small>${textOf(shift.impact)}</small></div>`).join("");
  const enablers = data.enablers.map((item, index) => `<div class="history-enabler"><span>${index + 1}</span><div><b>${textOf(item.title)}</b><small>${textOf(item.body)}</small></div></div>`).join("");
  const challenges = data.challenges.map((item) => `<div class="history-challenge"><b>${textOf(item.title)}</b><span>${textOf(item.body)}</span></div>`).join("");
  return `<figure class="history-overview-figure"><header><div class="eyebrow">${language === "zh" ? "历史总览 · 已发表论文优先" : "Historical overview · published work prioritized"}</div><h2>${language === "zh" ? "Agent 自进化研究的历史、能力与方向演化" : "History, capability growth, and direction formation in agent self-evolution"}</h2><p>${language === "zh" ? "从基础模型、推理与自举，到经验记忆、技能工具、工作流搜索、多模态进化与安全治理。" : "From foundation models and self-bootstrapped reasoning to persistent memory, skills, workflow search, multimodal evolution, and governance."}</p></header><section class="history-panel history-timeline"><div class="history-panel-title">${language === "zh" ? "A · 六阶段历史时间线" : "A · Six-stage historical timeline"}</div><div class="history-stage-grid">${stageCards}</div></section><section class="history-panel history-expansion"><div class="history-panel-title">${language === "zh" ? "B · 更新对象如何扩展" : "B · How the update target expanded"}</div><div class="history-expansion-grid">${expansion}</div></section><div class="history-middle-grid"><section class="history-panel history-capabilities"><div class="history-panel-title">${language === "zh" ? "C · 能力层级随时间如何增长" : "C · Capability growth across historical stages"}</div><div class="history-table-scroll"><table><thead><tr><th>${language === "zh" ? "能力层" : "Capability"}</th>${capabilityHead}</tr></thead><tbody>${capabilityRows}</tbody></table></div></section><section class="history-panel history-directions"><div class="history-panel-title">${language === "zh" ? "D · 十个研究方向如何形成" : "D · Formation of the ten research directions"}</div><div class="history-table-scroll"><table><thead><tr><th>ID</th><th>${language === "zh" ? "方向" : "Direction"}</th><th>${language === "zh" ? "起源" : "Origin"}</th><th>${language === "zh" ? "增长" : "Growth"}</th><th>${language === "zh" ? "状态" : "Status"}</th></tr></thead><tbody>${directionRows}</tbody></table></div><div class="history-ladder"><h3>${language === "zh" ? "历史结论阶梯" : "Historical claim ladder"}</h3>${ladder}</div></section></div><div class="history-bottom-grid"><section class="history-panel history-milestones"><div class="history-panel-title">${language === "zh" ? "E · 正式发表里程碑" : "E · Peer-reviewed milestones"}</div><div class="history-milestone-grid">${milestones}</div></section><section class="history-panel history-shifts"><div class="history-panel-title">${language === "zh" ? "F · 七次关键范式迁移" : "F · Seven paradigm shifts"}</div>${shifts}</section><section class="history-panel history-enablers"><div class="history-panel-title">${language === "zh" ? "G · 六个关键驱动因素" : "G · Six enabling factors"}</div>${enablers}</section><section class="history-panel history-challenges"><div class="history-panel-title">${language === "zh" ? "H · 当前开放问题" : "H · Open problems"}</div>${challenges}</section></div><figcaption>${language === "zh" ? "主时间线和里程碑优先采用正式发表论文；预印本前沿只在正文文献库中补充，不与历史主线混列。" : "The main timeline and milestone panel prioritize formally published papers. Preprint-only frontier work remains in the bibliography rather than being mixed into the historical spine."}</figcaption></figure>`;
}
function renderHome(config) {
  const counts = {};
  catalog.forEach((p) => counts[p.updateTarget || "other"] = (counts[p.updateTarget || "other"] || 0) + 1);
  const chapters = pageArchitecture("home").chapters || [];
  const featured = config.featured || [];
  const cardsFor = (chapter) => featured.filter((item) => (chapter.links || []).includes(item.href)).map((item) => `<a class="framework-card ${item.paper ? "paper-card" : ""}" href="${item.href}"><b>${textOf(item.title)}</b><span>${textOf(item.desc)}</span></a>`).join("");
  const figure = renderOverviewFigure(config, language === "zh" ? "Agent 自进化知识地图" : "Agent self-evolution knowledge map");
  const sortedSurfaces = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const maxSurface = Math.max(1, ...sortedSurfaces.map(([, count]) => count));
  const stats = `<div class="grid"><div class="stat"><b>${catalog.length || DATA.length}</b><span>${language === "zh" ? "篇去重后的研究条目" : "deduplicated research records"}</span></div><div class="stat"><b>${portfolioDirections().length || 10}</b><span>${language === "zh" ? "个研究方向" : "research directions"}</span></div><div class="stat"><b>${(config.ideaCount || portfolioIdeas().length || 4)}</b><span>${language === "zh" ? "个具体论文 Idea" : "concrete paper ideas"}</span></div></div>`;
  const distribution = `<section class="panel"><h3 id="live-landscape">${language === "zh" ? "动态研究分布" : "Live research landscape"}</h3><p class="section-intro">${language === "zh" ? "根据当前合并文献库自动统计；自动分类用于导航，核心专题仍经过人工核验。" : "Computed from the current merged corpus. Automatic categories support navigation; core topic synthesis remains manually reviewed."}</p><div class="distribution-list">${sortedSurfaces.map(([surface, count]) => `<a class="distribution-row" href="bibliography.html?method=${encodeURIComponent(surface)}#searchable-corpus"><span>${esc(surface)}</span><i><b style="width:${Math.max(4, count / maxSurface * 100)}%"></b></i><strong>${count}</strong></a>`).join("")}</div></section>`;
  const understand = `${figure}${stats}<div class="framework-grid">${cardsFor(chapters[0])}</div>${distribution}${(config.sections || []).slice(0,2).map((section,index) => renderSectionForPage(section,index,pageId,"home-topic-section",3)).join("")}`;
  const select = `<div class="framework-grid">${cardsFor(chapters[1])}</div>`;
  const execute = `<div class="framework-grid">${cardsFor(chapters[2])}</div>${(config.sections || []).slice(2).map((section,index) => renderSectionForPage(section,index + 2,pageId,"home-topic-section",3)).join("")}`;
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("home"))}${renderCustomChapter(chapters[0],0,understand)}${renderCustomChapter(chapters[1],1,select)}${renderCustomChapter(chapters[2],2,execute)}`;
}
function renderResourceIndexSection(mode, headingLevel = 2) {
  const isRepository = mode === "repositories";
  const rows = catalog.filter((p) => isRepository ? Boolean(p.repo) : /benchmark|arena|gym|environment|dataset|evaluation|testbed|sandbox/i.test(`${p.title} ${p.category} ${p.subcategory}`));
  const grouped = rows.reduce((acc, row) => { const key = isRepository ? (row.updateTarget || "other") : (row.category || "Unclassified"); acc[key] = (acc[key] || 0) + 1; return acc; }, {});
  const summary = Object.entries(grouped).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([key, count]) => `<div class="stat"><b>${count}</b><span>${esc(key)}</span></div>`).join("");
  const title = isRepository ? (language === "zh" ? "动态代码仓库索引" : "Live repository index") : (language === "zh" ? "动态基准与环境索引" : "Live benchmark and environment index");
  const intro = isRepository ? (language === "zh" ? "从合并文献语料中自动抽取带公开代码链接的条目。仓库可用不代表完整复现，需结合上方复现等级审查。" : "Automatically extracts records with public code links from the merged corpus. Repository availability does not imply full reproduction; use the reproduction-readiness criteria above.") : (language === "zh" ? "从合并语料中抽取 benchmark、arena、gym、environment、dataset 与 evaluation 相关条目。" : "Extracts benchmark, arena, gym, environment, dataset, and evaluation records from the merged corpus.");
  const rankedRows = sortBibliographyRecords(rows);
  const level = Math.min(4, Math.max(2, Number(headingLevel) || 2));
  return `<section class="panel live-resource-panel" id="live-${mode}-index"><h${level} id="live-${mode}-heading">${title}</h${level}><p class="section-intro">${intro}</p><div class="grid resource-index-stats">${summary}</div><div class="resource-list">${rankedRows.length ? rankedRows.slice(0, 80).map((paper, index) => paperCard(paper, index + 1)).join("") : `<div class="empty">${language === "zh" ? "动态语料尚未加载。" : "The live corpus has not loaded yet."}</div>`}</div>${rows.length > 80 ? `<p class="resource-index-note">${language === "zh" ? `当前展示前 80 条，共 ${rows.length} 条；完整检索请进入文献库。` : `Showing the first 80 of ${rows.length} records; use the bibliography for the complete searchable set.`}</p>` : ""}</section>`;
}
function renderDynamicResourceIndex(config, mode) {
  return `${pageHeader(config)}${(config.sections || []).map(renderSection).join("")}${renderResourceIndexSection(mode)}`;
}
function bibliographySubset() {
  return catalog.filter((p) => (activeFilter === "all" || p.updateTarget === activeFilter) && (activeYear === "all" || String(p.year) === String(activeYear)) && (activePublicationType === "all" || publicationType(p) === activePublicationType) && (activeSignal === "all" || signalFamily(p) === activeSignal) && (!visionOnly || p.vision));
}
function renderTimelineMap() {
  const years = [...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a - b);
  const surfaces = [...new Set(catalog.map((p) => p.updateTarget || "other"))].sort();
  const maxCount = Math.max(1, ...surfaces.flatMap((surface) => years.map((year) => catalog.filter((p) => (p.updateTarget || "other") === surface && p.year === year).length)));
  return `<section class="panel bibliography-map"><div class="paper-figure-heading"><div><h3 id="method-time-map">${language === "zh" ? "方法与发表时间地图" : "Method and publication-time map"}</h3><p class="section-intro">${language === "zh" ? "每个单元格表示该年份与更新对象下的去重论文数量；点击即可筛选文献库。早期年份主要是 prompt、memory、continual learning 与 agent architecture 的前置工作。" : "Each cell counts deduplicated papers for one year and update surface. Click a cell to filter the bibliography. Early years mainly contain precursors in prompting, memory, continual learning, and agent architecture."}</p></div></div><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="timeline-row"><button class="timeline-label" data-filter="${esc(surface)}">${esc(surface)}</button>${years.map((year) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell" data-filter="${esc(surface)}" data-year="${year}" title="${esc(surface)} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderPublicationTypeMap() {
  const years = [...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a - b);
  const types = ["Published", "Preprint", "Repository", "Blog/Report", "Other"];
  const maxCount = Math.max(1, ...types.flatMap((type) => years.map((year) => catalog.filter((p) => publicationType(p) === type && p.year === year).length)));
  return `<section class="panel bibliography-map"><h3 id="publication-status-map">${language === "zh" ? "发表类型与时间地图" : "Publication type and time map"}</h3><p class="section-intro">${language === "zh" ? "区分正式发表、预印本、仓库和技术博客。自动识别仅用于导航，正式引用仍以论文页面核验为准。" : "Separates published papers, preprints, repositories, and technical reports. Automatic status is for navigation; formal citations still require source verification."}</p><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "发表类型" : "Publication type"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${types.map((type) => `<div class="timeline-row"><button class="timeline-label publication-label" data-publication="${esc(type)}">${esc(type)}</button>${years.map((year) => { const count = catalog.filter((p) => publicationType(p) === type && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell publication-cell" data-publication="${esc(type)}" data-year="${year}" title="${esc(type)} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderSignalMatrix() {
  const surfaces = [...new Set(catalog.map((p) => p.updateTarget || "other"))].sort();
  const signals = [...new Set(catalog.map(signalFamily))].sort();
  const maxCount = Math.max(1, ...surfaces.flatMap((surface) => signals.map((signal) => catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length)));
  return `<section class="panel bibliography-map"><h3 id="surface-signal-map">${language === "zh" ? "更新对象与反馈信号地图" : "Update-surface and feedback-signal map"}</h3><p class="section-intro">${language === "zh" ? "该矩阵把“更新什么”与“凭什么更新”分开；点击单元格可联合筛选。" : "This matrix separates what changes from the evidence that drives the change. Click a cell to apply both filters."}</p><div class="signal-map" style="--signal-count:${signals.length}"><div class="signal-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${signals.map((signal) => `<button class="signal-column" data-signal="${esc(signal)}">${esc(signal)}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="signal-row"><button class="signal-label" data-filter="${esc(surface)}">${esc(surface)}</button>${signals.map((signal) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="signal-cell" data-filter="${esc(surface)}" data-signal="${esc(signal)}" title="${esc(surface)} × ${esc(signal)}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderMilestoneTimeline() {
  const milestones = [
    [2022, "Self-generated instructions and early prompt evolution"],
    [2023, "Reflection, verbal reinforcement, open-ended skills, and tool critique"],
    [2024, "Textual gradients, agent graphs, visual tool update, and self-updatable memory"],
    [2025, "Online curriculum RL, workflow search, co-evolving world models, and GUI learning"],
    [2026, "VLM self-play, skill ecosystems, harness evolution, visual memory, and formal verification"],
  ];
  return `<section class="panel"><h3 id="field-timeline">${language === "zh" ? "领域演化时间线" : "Field evolution timeline"}</h3><div class="method-timeline">${milestones.map(([year, en]) => { const count = catalog.filter((p) => p.year === year).length; return `<div class="timeline-item"><div class="timeline-year">${year}</div><div><strong>${language === "zh" ? ({2022:"自生成指令与早期提示词进化",2023:"反思、语言强化、开放式技能与工具批评",2024:"文本梯度、Agent 图、视觉工具更新与可自更新记忆",2025:"在线课程 RL、工作流搜索、共进化世界模型与 GUI 学习",2026:"VLM 自博弈、技能生态、harness 进化、视觉记忆与形式化验证"}[year]) : en}</strong><p>${language === "zh" ? `当前语料库中收录 ${count} 条该年份记录。` : `${count} records from this year are currently indexed.`}</p></div></div>`; }).join("")}</div></section>`;
}
function renderBibliography(config) {
  const categories = ["all", ...new Set(catalog.map((p) => p.updateTarget || "other"))];
  const years = ["all", ...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a === "all" ? -1 : b === "all" ? 1 : b - a);
  const publicationTypes = ["all", "Published", "Preprint", "Repository", "Blog/Report", "Other"];
  const signals = ["all", ...new Set(catalog.map(signalFamily))].sort((a, b) => a === "all" ? -1 : b === "all" ? 1 : a.localeCompare(b));
  const filters = categories.map((category) => `<button class="filter-btn ${activeFilter === category ? "active" : ""}" data-filter="${esc(category)}">${esc(category === "all" ? (language === "zh" ? "全部方法" : "All methods") : category)}</button>`).join("");
  const yearOptions = years.map((year) => `<option value="${year}" ${String(activeYear) === String(year) ? "selected" : ""}>${year === "all" ? (language === "zh" ? "全部年份" : "All years") : year}</option>`).join("");
  const publicationOptions = publicationTypes.map((type) => `<option value="${type}" ${activePublicationType === type ? "selected" : ""}>${type === "all" ? (language === "zh" ? "全部发表类型" : "All publication types") : type}</option>`).join("");
  const signalOptions = signals.map((signal) => `<option value="${signal}" ${activeSignal === signal ? "selected" : ""}>${signal === "all" ? (language === "zh" ? "全部反馈信号" : "All feedback signals") : signal}</option>`).join("");
  const visionCount = catalog.filter((p) => p.vision).length;
  const publishedCount = catalog.filter((p) => publicationType(p) === "Published").length;
  const sourceCount = new Set(catalog.flatMap((p) => String(p.source || "").split("+")).filter(Boolean)).size;
  const coverage = citationCoverage();
  const sortOptions = (CITATION_CONFIG.sortModes || []).map((mode) => `<option value="${esc(mode.id)}" ${bibliographySort === mode.id ? "selected" : ""}>${textOf(mode.title)}</option>`).join("");
  const roleLegend = (CITATION_CONFIG.readingRoles || []).map((role) => `<span><b>${Number(role.rank || 0) + 1}</b>${textOf(role.title)}</span>`).join("");
  const rankingGuide = `<section class="panel citation-ranking-guide"><h3 id="literature-ranking">${language === "zh" ? "推荐阅读顺序与排序方式" : "Recommended reading order and sort modes"}</h3><p class="section-intro">${language === "zh" ? "默认顺序按论文在 Agent 自进化研究中的角色组织，而不是让总引用量主导：先读近期领域综述，再读直接自进化方法、评测与治理、关键支撑机制，最后回看 Agent 前置与基础模型前置工作。每一角色层内优先正式发表和较新的论文，引用量只作为辅助信号。纯引用量模式保留用于查看历史影响力。" : "The default order follows each paper's role in agent self-evolution rather than letting total citations dominate: recent field overviews first, then direct self-evolution methods, evaluation and governance, enabling mechanisms, agent foundations, and foundation-model precursors. Within each role, peer-reviewed and recent work is prioritized; citations are only a supporting signal. Citation-only mode remains available for historical influence."}</p><div class="citation-ranking-controls"><label><span>${language === "zh" ? "排序方式" : "Sort mode"}</span><select id="bibliography-sort">${sortOptions}</select></label><div id="citation-ranking-status" class="citation-ranking-status"><strong>${CITATION_CONFIG.sourceName || "OpenAlex snapshot"}</strong><span>${language === "zh" ? `引用覆盖 ${coverage.matched}/${coverage.total}` : `${coverage.matched}/${coverage.total} citation matches`}</span></div></div><div class="reading-role-legend">${roleLegend}</div><div class="ranking-secondary-note">${language === "zh" ? "角色层内部：正式发表优先 → 年份较新优先 → 引用量辅助；Agent 与模型基础层按历史时间顺序排列。" : "Within a role: peer-reviewed first → newer work first → citations as a tie-breaker. Agent and model foundations are shown chronologically."}</div></section>`;
  const analysisGuide = `<section class="panel paper-analysis-guide"><h3 id="paper-reading-schema">${language === "zh" ? "每篇论文的六项阅读框架" : "Six-part reading framework for every paper"}</h3><p class="section-intro">${language === "zh" ? "每个文献卡片都可展开查看：目的／问题、核心思想、合理性、方法逻辑、重要性和相对优势。相对优势表示设计上更适合什么条件，不等于未经实验验证的绝对领先。" : "Every paper card expands into purpose/problem, core idea, rationale, method logic, importance, and comparative advantage. Comparative advantage describes conditions where a design may be better suited; it is not an unverified claim of absolute superiority."}</p><div class="property-grid"><div class="property-card"><b>${language === "zh" ? "核心方法注释" : "Core method note"}</b><span>${language === "zh" ? "关键里程碑论文具有针对该论文单独整理的方法描述。" : "Key milestone papers have a paper-specific method description."}</span></div><div class="property-card"><b>${language === "zh" ? "基于已有摘要归纳" : "Summary-derived"}</b><span>${language === "zh" ? "依据人工补充的简短摘要、更新对象和反馈信号组织六项解释。" : "Uses the curated short summary, update surface, and feedback signal."}</span></div><div class="property-card"><b>${language === "zh" ? "基于元数据保守归纳" : "Metadata-derived"}</b><span>${language === "zh" ? "长尾论文仅依据标题与目录元数据保守归纳；引用方法细节前必须回看原文。" : "Long-tail papers use conservative title and catalog metadata; consult the original paper before citing method details."}</span></div><div class="property-card"><b>${language === "zh" ? "导出" : "Export"}</b><span>${language === "zh" ? "JSON 与 CSV 会同时导出六项结构化解释和归纳依据。" : "JSON and CSV exports include all six fields and the analysis basis."}</span></div></div></section>`;
  const chapters = pageArchitecture("bibliography").chapters || [];
  const statusAndStats = `<div class="integrity-status ${catalog.length > DATA.length ? "pass" : "warn"}"><strong>${catalog.length > DATA.length ? "LIVE" : "SNAPSHOT"}</strong><span>${catalog.length > DATA.length ? (language === "zh" ? "已同步两个综述目录、ICLR 机制文献与第二阶段 CVPR 视觉补充集，并完成去重。" : "Live-synced from two survey-maintained catalogs, the curated ICLR mechanism set, and a secondary CVPR visual supplement.") : (language === "zh" ? "上游同步失败，当前显示人工核验快照。" : "Upstream sync failed; showing the curated snapshot.")}</span></div><div class="grid bibliography-stats"><div class="stat"><b>${catalog.length}</b><span>${language === "zh" ? "篇去重条目" : "deduplicated records"}</span></div><div class="stat"><b>${publishedCount}</b><span>${language === "zh" ? "篇自动识别为正式发表" : "records classified as published"}</span></div><div class="stat"><b>${visionCount}</b><span>${language === "zh" ? "篇视觉/多模态相关" : "vision/multimodal records"}</span></div><div class="stat"><b>${sourceCount}</b><span>${language === "zh" ? "类文献来源" : "source streams"}</span></div></div>`;
  const coverageBody = `${renderGroupNav(config.groupsBefore || [])}${renderMergedGroups(config.groupsBefore || [])}${renderSemanticScholarStatus()}${statusAndStats}`;
  const rankingBody = `${rankingGuide}${analysisGuide}`;
  const mapsBody = `${renderTimelineMap()}${renderPublicationTypeMap()}${renderSignalMatrix()}${renderMilestoneTimeline()}`;
  const corpusBody = `<section class="panel"><div class="paper-figure-heading"><div><h3 id="searchable-corpus">${language === "zh" ? "可检索文献语料库" : "Searchable literature corpus"}</h3><p class="section-intro">${language === "zh" ? "筛选结果可直接导出、打印或生成可分享链接。" : "The current filtered set can be exported, printed, or shared through a filter-preserving URL."}</p></div><div class="export-actions"><button class="link-btn export-btn" data-export="json">JSON</button><button class="link-btn export-btn" data-export="csv">CSV</button><button class="link-btn export-btn" data-export="bibtex">BibTeX</button><button class="link-btn" id="copy-filter-link">${language === "zh" ? "复制筛选链接" : "Copy filter link"}</button><button class="link-btn" id="print-page">${language === "zh" ? "打印" : "Print"}</button><button class="link-btn" id="reset-filters">${language === "zh" ? "重置" : "Reset"}</button></div></div><div class="bibliography-controls"><select id="year-filter">${yearOptions}</select><select id="publication-filter">${publicationOptions}</select><select id="signal-filter">${signalOptions}</select><label class="toggle-filter"><input id="vision-filter" type="checkbox" ${visionOnly ? "checked" : ""}> ${language === "zh" ? "仅视觉/多模态" : "Vision/multimodal only"}</label></div><div class="filters">${filters}</div><div id="bibliography-list" class="resource-list"></div></section>`;
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("bibliography"))}${renderCustomChapter(chapters[0],0,coverageBody)}${renderCustomChapter(chapters[1],1,rankingBody)}${renderCustomChapter(chapters[2],2,mapsBody)}${renderCustomChapter(chapters[3],3,corpusBody)}`;
  return `${pageHeader(config)}${renderGroupNav(config.groupsBefore || [])}${renderMergedGroups(config.groupsBefore || [])}<div class="integrity-status ${catalog.length > DATA.length ? "pass" : "warn"}"><strong>${catalog.length > DATA.length ? "LIVE" : "SNAPSHOT"}</strong><span>${catalog.length > DATA.length ? (language === "zh" ? "已同步两个综述目录、ICLR 机制文献与第二阶段 CVPR 视觉补充集，并完成去重。" : "Live-synced from two survey-maintained catalogs, the curated ICLR mechanism set, and a secondary CVPR visual supplement.") : (language === "zh" ? "上游同步失败，当前显示人工核验快照。" : "Upstream sync failed; showing the curated snapshot.")}</span></div><div class="grid bibliography-stats"><div class="stat"><b>${catalog.length}</b><span>${language === "zh" ? "篇去重条目" : "deduplicated records"}</span></div><div class="stat"><b>${publishedCount}</b><span>${language === "zh" ? "篇自动识别为正式发表" : "records classified as published"}</span></div><div class="stat"><b>${visionCount}</b><span>${language === "zh" ? "篇视觉/多模态相关" : "vision/multimodal records"}</span></div><div class="stat"><b>${sourceCount}</b><span>${language === "zh" ? "类文献来源" : "source streams"}</span></div></div>${rankingGuide}${analysisGuide}${renderTimelineMap()}${renderPublicationTypeMap()}${renderSignalMatrix()}${renderMilestoneTimeline()}<section class="panel"><div class="paper-figure-heading"><div><h3 id="searchable-corpus">${language === "zh" ? "可检索文献语料库" : "Searchable literature corpus"}</h3><p class="section-intro">${language === "zh" ? "筛选结果可直接导出、打印或生成可分享链接。" : "The current filtered set can be exported, printed, or shared through a filter-preserving URL."}</p></div><div class="export-actions"><button class="link-btn export-btn" data-export="json">JSON</button><button class="link-btn export-btn" data-export="csv">CSV</button><button class="link-btn export-btn" data-export="bibtex">BibTeX</button><button class="link-btn" id="copy-filter-link">${language === "zh" ? "复制筛选链接" : "Copy filter link"}</button><button class="link-btn" id="print-page">${language === "zh" ? "打印" : "Print"}</button><button class="link-btn" id="reset-filters">${language === "zh" ? "重置" : "Reset"}</button></div></div><div class="bibliography-controls"><select id="year-filter">${yearOptions}</select><select id="publication-filter">${publicationOptions}</select><select id="signal-filter">${signalOptions}</select><label class="toggle-filter"><input id="vision-filter" type="checkbox" ${visionOnly ? "checked" : ""}> ${language === "zh" ? "仅视觉/多模态" : "Vision/multimodal only"}</label></div><div class="filters">${filters}</div><div id="bibliography-list" class="resource-list"></div></section>`;
}
function citationText(p) {
  const venue = p.venue || "";
  return `${p.title} (${p.year || "n.d."}). ${venue}${p.url ? `. ${p.url}` : ""}`;
}
function bibtexEntry(p) {
  const key = `${slugify(p.title).replace(/-/g, "_").slice(0, 48)}_${p.year || "nd"}`;
  const type = publicationType(p) === "Published" ? "inproceedings" : "misc";
  return `@${type}{${key},\n  title = {${String(p.title).replace(/[{}]/g, "")}},\n  year = {${p.year || ""}},\n  note = {${String(p.venue || "").replace(/[{}]/g, "")}},\n  url = {${p.url || ""}}\n}`;
}
function downloadBlob(filename, content, type = "text/plain;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url; link.download = filename; document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function exportBibliography(format) {
  const query = (document.getElementById("site-search")?.value || "").trim().toLowerCase();
  const rows = sortBibliographyRecords(bibliographySubset().filter((p) => !query || paperSearchText(p).includes(query)));
  const enriched = rows.map((p, index) => {
    const analysis = paperAnalysis(p);
    return {...p, priorityRank:index + 1, readingRole:readingRoleLabel(p), readingRoleRank:readingRoleRank(p), publicationTier:publicationTierLabel(p), citationCount:citationCount(p), citationSource:CITATION_CONFIG.sourceName || "OpenAlex", citationMatchedTitle:citationMetadata(p)?.matchedTitle || "", citationMatchScore:citationMetadata(p)?.matchScore ?? "", analysisBasis:paperAnalysisLabel(analysis), problemMotivation:analysis.purpose, comparativeAdvantage:analysis.advantage, coreIntuition:analysis.core, rationale:analysis.rationale, methodFlow:analysis.logic, experimentalValidation:analysis.validation};
  });
  if (format === "json") return downloadBlob("agent-self-evolution-bibliography.json", JSON.stringify(enriched, null, 2), "application/json;charset=utf-8");
  if (format === "bibtex") return downloadBlob("agent-self-evolution-bibliography.bib", rows.map(bibtexEntry).join("\n\n"));
  const fields = ["priorityRank","readingRole","readingRoleRank","publicationTier","citationCount","citationSource","citationMatchedTitle","citationMatchScore","year","title","venue","category","subcategory","updateTarget","signal","vision","analysisBasis","problemMotivation","comparativeAdvantage","coreIntuition","rationale","methodFlow","experimentalValidation","url","repo"];
  const csv = [fields.join(","), ...enriched.map((p) => fields.map((field) => `"${String(p[field] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
  downloadBlob("agent-self-evolution-bibliography.csv", csv, "text/csv;charset=utf-8");
}
function paperMethodNote(record) {
  return (window.PAPER_METHOD_NOTES || {})[record.title] || null;
}
function paperKind(record) {
  const text = `${record.title || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
  if (/survey|review|taxonomy|perspective/.test(text)) return "survey";
  if (/benchmark|evaluation|arena|testbed|dataset/.test(text)) return "benchmark";
  return "method";
}
function paperAnalysisFamily(record) {
  const text = `${record.updateTarget || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
  if (/prompt|context|instruction|reasoning trace/.test(text)) return "prompt";
  if (/memory|retrieval|experience|graph/.test(text)) return "memory";
  if (/tool|skill|api|code/.test(text)) return "tool";
  if (/workflow|scaffold|architecture|agent graph|harness/.test(text)) return "workflow";
  if (/world|embodied|robot|environment|navigation|gui|web/.test(text)) return "world";
  if (/evaluator|critic|reward|verification|safety|benchmark/.test(text)) return "evaluation";
  if (/model|parameter|training|reinforcement|fine-tun|adapter|lora/.test(text)) return "parameter";
  return "general";
}
function paperTargetLabel(record) {
  const raw = record.updateTarget || (language === "zh" ? "Agent 组件" : "agent component");
  if (language !== "zh") return raw;
  const key = String(raw).toLowerCase();
  if (/model parameter/.test(key)) return "模型参数";
  if (/prompt|context/.test(key)) return "提示词／上下文";
  if (/memory/.test(key)) return "记忆";
  if (/tool|skill/.test(key)) return "工具／技能";
  if (/workflow|scaffold|architecture/.test(key)) return "工作流／系统结构";
  if (/world|environment/.test(key)) return "世界模型／环境状态";
  if (/evaluator|reward/.test(key)) return "评价器／奖励";
  return raw;
}
function paperSignalLabel(record) {
  const family = signalFamily(record);
  if (language !== "zh") return record.signal || family;
  const labels = {
    "verification/tests":"可验证测试",
    "critique/evaluation":"批评与评价",
    "environment interaction":"环境交互",
    "scalar/preference reward":"标量或偏好奖励",
    "population/self-play":"群体反馈或自博弈",
    "experience reuse":"经验复用",
    "self-generated artifact":"自生成数据或轨迹",
  };
  return labels[family] || record.signal || family;
}
function paperAnalysis(record) {
  const kind = paperKind(record);
  const family = paperAnalysisFamily(record);
  const target = paperTargetLabel(record);
  const signal = paperSignalLabel(record);
  const summary = language === "zh" ? (record.summaryZh || record.summary || "") : (record.summary || record.summaryZh || "");
  const note = paperMethodNote(record);
  const topAnalysis = (window.TOP_PAPER_ANALYSES || {})[record.title];
  if (topAnalysis) {
    return {
      basis:"curated-full",
      purpose:textOf(topAnalysis.problem),
      advantage:textOf(topAnalysis.advantage),
      core:textOf(topAnalysis.intuition),
      rationale:textOf(topAnalysis.rationale),
      logic:textOf(topAnalysis.flow),
      validation:textOf(topAnalysis.validation),
      importance:textOf(topAnalysis.problem)
    };
  }
  const topic = record.subcategory || record.category || record.title;
  const familyText = {
    parameter:{
      rationale:{en:"When feedback captures a stable and recurring pattern, parameter updates can amortize the improvement across many future tasks.",zh:"当反馈反映稳定且会重复出现的规律时，参数更新可以把一次学习成本摊销到大量后续任务。"},
      importance:{en:"Parameter-level methods determine whether self-improvement becomes a reusable model capability rather than a one-session workaround.",zh:"参数级方法决定自我改进能否成为可复用模型能力，而不是一次会话中的临时补丁。"},
      advantage:{en:"Compared with prompt-only or memory-only changes, this family can produce broader and more persistent transfer when sufficient reliable data and compute are available.",zh:"相较仅修改提示词或记忆，当可靠数据和算力充足时，这类方法可能获得更广、更持久的迁移。"}
    },
    prompt:{
      rationale:{en:"Instructions and reasoning traces strongly control model behavior and can be searched or revised without changing model weights.",zh:"指令和推理轨迹会显著控制模型行为，而且可以在不修改模型权重的情况下搜索和修订。"},
      importance:{en:"Prompt-level evolution is a low-cost route for testing whether a behavior change requires training at all.",zh:"提示词级进化是检验某种行为变化是否真的需要训练的低成本路径。"},
      advantage:{en:"Compared with parameter updates, it is usually cheaper, faster, easier to inspect, and easier to roll back, although its persistence and capacity may be lower.",zh:"相较参数更新，它通常更便宜、更快、更容易检查和回滚，但持久性与容量可能较低。"}
    },
    memory:{
      rationale:{en:"Cross-episode memory lets specific experience influence later tasks while keeping the learned artifact inspectable and replaceable.",zh:"跨回合记忆能够让具体经验影响后续任务，同时保持学习产物可检查、可替换。"},
      importance:{en:"Memory is the main bridge between one-off interaction and persistent agent behavior without requiring full retraining.",zh:"记忆是不进行完整重训练时，把一次性交互转化为持久 Agent 行为的主要桥梁。"},
      advantage:{en:"Compared with fine-tuning, memory updates are more targeted and reversible; compared with retry-only methods, they can affect future tasks.",zh:"相较微调，记忆更新更定向且更可逆；相较仅重试的方法，它能够影响未来任务。"}
    },
    tool:{
      rationale:{en:"Repeated procedures can be externalized as executable artifacts and tested independently from the language model that invokes them.",zh:"重复流程可以外化为可执行产物，并与调用它的语言模型分开测试。"},
      importance:{en:"Tool and skill evolution turns verbal knowledge into reusable operational capability.",zh:"工具与技能进化把语言知识转化为可复用的实际操作能力。"},
      advantage:{en:"Compared with natural-language memory, executable skills provide clearer interfaces, direct tests, and more predictable reuse.",zh:"相较自然语言记忆，可执行技能具有更清晰的接口、直接测试方式和更可预测的复用。"}
    },
    workflow:{
      rationale:{en:"Many agent failures arise from coordination, routing, or control-flow choices rather than insufficient base-model capability.",zh:"许多 Agent 失败来自协调、路由或控制流选择，而不是基础模型能力不足。"},
      importance:{en:"Workflow-level research expands self-evolution from improving one component to redesigning the agent system itself.",zh:"工作流级研究把自进化从改进单一组件扩展到重新设计整个 Agent 系统。"},
      advantage:{en:"Compared with model-only improvement, it can exploit existing components more efficiently and localize which system interaction needs to change.",zh:"相较只改模型，它能够更高效地利用现有组件，并定位究竟是哪种系统交互需要变化。"}
    },
    world:{
      rationale:{en:"Interaction exposes state changes, action effects, and environment dynamics that cannot be recovered from text-only self-critique.",zh:"环境交互能够揭示文本自我批评无法获得的状态变化、动作效果与环境动力学。"},
      importance:{en:"Grounded adaptation is necessary when the agent acts in websites, visual worlds, or physical environments that change over time.",zh:"当 Agent 在会变化的网站、视觉世界或物理环境中行动时，基于真实环境的适应是必要的。"},
      advantage:{en:"Compared with text-only reflection, this family uses observable world feedback and can distinguish reasoning errors from environment or embodiment changes.",zh:"相较纯文本反思，这类方法利用可观测世界反馈，并能区分推理错误与环境或具身变化。"}
    },
    evaluation:{
      rationale:{en:"The evolution policy can only improve reliably when its feedback and measurements expose the failures that matter.",zh:"只有反馈与测量能够暴露真正重要的失败时，进化策略才可能可靠改进。"},
      importance:{en:"Evaluation defines what counts as improvement and prevents harmful updates from being hidden by average success.",zh:"评测决定什么才算改进，并防止有害更新被平均成功率掩盖。"},
      advantage:{en:"Compared with one-off task scores, dedicated evaluation methods provide controlled failure cases, comparable metrics, and evidence for release decisions.",zh:"相较一次性任务分数，专门评测方法能够提供受控失败案例、可比较指标和发布决策证据。"}
    },
    general:{
      rationale:{en:"The paper isolates a concrete update object and feedback source, making the proposed improvement mechanism testable rather than treating self-improvement as a single undifferentiated process.",zh:"该论文隔离了具体更新对象与反馈来源，使改进机制可以被检验，而不是把自我改进视为不可区分的整体过程。"},
      importance:{en:"It contributes to identifying which parts of an agent can change persistently and under what evidence.",zh:"它有助于识别 Agent 的哪些部分能够持久变化，以及这种变化需要什么证据。"},
      advantage:{en:"Its potential advantage is a more explicit and auditable update pathway than generic retry or undifferentiated self-improvement loops.",zh:"其潜在优势是更新路径比通用重试或未分层的自我改进闭环更明确、更可审计。"}
    }
  }[family];
  if (kind === "survey") {
    return {
      basis:"derived",
      purpose:language === "zh" ? `梳理 ${topic} 中分散的概念、方法与证据边界，建立可比较的研究框架。` : `Organize fragmented concepts, methods, and evidence boundaries in ${topic} into a comparable framework.`,
      core:summary || (language === "zh" ? "系统收集相关工作，建立分类体系，并比较不同方法的更新对象、反馈来源、评测方式与局限。" : "Systematically collect related work, build a taxonomy, and compare update targets, feedback sources, evaluation practices, and limitations."),
      rationale:language === "zh" ? "当术语和评测口径分散时，统一分类能够暴露方法之间真正可比和不可比的部分。" : "When terminology and evaluation practices are fragmented, a shared taxonomy reveals what is and is not genuinely comparable.",
      logic:language === "zh" ? "定义检索范围 → 收集并去重论文 → 按统一维度编码 → 比较方法与证据 → 总结缺口和研究议程。" : "Define scope → collect and deduplicate papers → code them with shared dimensions → compare methods and evidence → identify gaps and an agenda.",
      importance:language === "zh" ? "综述为领域提供共同语言，降低重复造轮子和错误比较的风险。" : "A survey supplies common language for the field and reduces duplicated work and invalid comparisons.",
      advantage:language === "zh" ? "相较单篇方法论文，它提供跨方法的全局视角；但它不替代具体方法的实验验证。" : "Compared with a single method paper, it provides a field-wide view, but it does not replace empirical validation of individual methods.",
      validation:language === "zh" ? "核查检索协议、覆盖范围、去重规则、分类一致性和关键结论是否由正式来源支持，并与其他综述的覆盖差异比较。" : "Audit the search protocol, coverage, deduplication, taxonomy consistency, and source support for key claims, then compare coverage with other surveys."
    };
  }
  if (kind === "benchmark") {
    return {
      basis:note ? "curated" : "derived",
      purpose:language === "zh" ? `解决现有评测无法充分衡量 ${topic} 的问题。` : `Address the lack of adequate measurement for ${topic}.`,
      core:textOf(note) || summary || (language === "zh" ? `围绕 ${topic} 构造任务、失败类型和指标，并在统一设置下比较系统。` : `Construct tasks, failure types, and metrics for ${topic}, then compare systems under a shared protocol.`),
      rationale:familyText.rationale[language],
      logic:language === "zh" ? `定义目标能力或失败 → 构造受控数据与任务 → 运行被测系统 → 计算统一指标 → 分析能力边界与失败来源。` : `Define the target capability or failure → construct controlled data and tasks → run evaluated systems → compute shared metrics → analyze capability boundaries and failure sources.`,
      importance:familyText.importance[language],
      advantage:familyText.advantage[language],
      validation:language === "zh" ? `在统一任务、失败类型和指标上运行多种代表系统，报告总体结果、分组结果、评价一致性和基准设计消融。` : `Run representative systems under shared tasks, failure types, and metrics; report aggregate and subgroup results, evaluator agreement, and benchmark-design ablations.`
    };
  }
  return {
    basis:note ? "curated" : (summary ? "summary" : "derived"),
    purpose:language === "zh" ? `该论文面向 ${topic}，试图改进 ${target} 在 Agent 自进化过程中的学习或使用方式。` : `The paper targets ${topic}, aiming to improve how ${target} is learned or used during agent self-evolution.`,
    core:textOf(note) || summary || (language === "zh" ? `把 ${target} 作为主要更新对象，并使用 ${signal} 驱动候选变化。` : `Treat ${target} as the main update surface and use ${signal} to drive candidate changes.`),
    rationale:familyText.rationale[language],
    logic:language === "zh" ? `收集 ${signal} → 生成针对 ${target} 的候选更新 → 在任务或留出数据上评估 → 保留、修订或拒绝更新 → 在后续任务中验证持久收益。` : `Collect ${signal} → propose a change to ${target} → evaluate it on tasks or held-out data → retain, revise, or reject the update → verify persistent benefit on later tasks.`,
    importance:familyText.importance[language],
    advantage:familyText.advantage[language],
    validation:language === "zh" ? `在留出或后续任务上与最强同类方法比较 ${target} 的收益、成本和回退；同时消融关键更新步骤、反馈来源和提交门控。` : `Compare gains, cost, and regressions for ${target} against the strongest same-family baselines on held-out or later tasks, with ablations of the update step, feedback source, and commitment gate.`
  };
}
function paperAnalysisLabel(analysis) {
  if (analysis.basis === "curated-full") return language === "zh" ? "人工核验六项分析" : "curated six-part analysis";
  if (analysis.basis === "curated") return language === "zh" ? "核心方法注释" : "core method note";
  if (analysis.basis === "summary") return language === "zh" ? "基于已有摘要归纳" : "derived from available summary";
  return language === "zh" ? "基于元数据保守归纳" : "conservative metadata-derived overview";
}
function paperSearchText(record) {
  const analysis = paperAnalysis(record);
  return [record.title,record.venue,record.category,record.subcategory,record.updateTarget,record.signal,publicationType(record),analysis.purpose,analysis.advantage,analysis.core,analysis.rationale,analysis.logic,analysis.validation,analysis.importance].join(" ").toLowerCase();
}
function paperCard(p, priorityRank = null) {
  const summary = language === "zh" ? (p.summaryZh || p.summary || "") : (p.summary || p.summaryZh || "");
  const refNo = p.refNo || catalog.indexOf(p) + 1;
  const slug = p.slug || slugify(p.title);
  const type = publicationType(p);
  const analysis = paperAnalysis(p);
  const citations = citationCount(p);
  const citationMeta = citationMetadata(p);
  const tierLabel = publicationTierLabel(p);
  const role = readingRoleInfo(p);
  const requested = new URLSearchParams(location.search).get("paper") === slug;
  const analysisSearch = [analysis.purpose,analysis.advantage,analysis.core,analysis.rationale,analysis.logic,analysis.validation,analysis.importance].join(" ");
  return `<article class="card reference-card" id="ref-${slug}" data-reading-role="${esc(role.id)}" data-role-rank="${readingRoleRank(p)}" data-tier="${publicationTier(p)}" data-citations="${citations === null ? -1 : citations}" data-year="${p.year || 0}" data-priority-rank="${priorityRank || ""}" data-search="${esc([p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal,type,analysisSearch].join(" ").toLowerCase())}"><div class="card-top"><div>${priorityRank ? `<div class="paper-priority-rank">${language === "zh" ? "推荐序号" : "reading order"} #${priorityRank}</div>` : ""}<h3 data-toc="false"><a class="ref-number" href="#ref-${slug}">[${refNo}]</a> ${esc(p.title)}</h3><div class="meta">${esc(String(p.year || ""))} · ${esc(p.venue || "Unknown venue")} · ${esc(p.category || "Unclassified")}</div></div><div class="badges"><span class="badge reading-role">${esc(textOf(role.title))}</span><span class="badge ranking-tier">${esc(tierLabel)}</span><span class="badge citation-count ${citations === null ? "citation-pending" : ""}">${citations === null ? (language === "zh" ? "引用量待匹配" : "citations pending") : `${citations.toLocaleString(language === "zh" ? "zh-CN" : "en-US")} ${language === "zh" ? "次引用" : "citations"}`}</span><span class="badge publication-type">${esc(type)}</span><span class="badge ${p.vision ? "vision" : ""}">${p.vision ? "vision/multimodal" : "general"}</span><span class="badge ${p.updateTarget === "model parameters" ? "model" : "scaffold"}">${esc(p.updateTarget || "agent component")}</span><span class="badge">${esc(p.signal || "feedback")}</span></div></div>${citationMeta ? `<div class="citation-source-note">${language === "zh" ? "引用数据" : "Citation data"}: ${esc(CITATION_CONFIG.sourceName || "OpenAlex")} · ${language === "zh" ? "匹配" : "match"} ${Math.round((citationMeta.matchScore || 0) * 100)}%</div>` : ""}${summary ? `<p>${esc(summary)}</p>` : ""}<details class="paper-analysis" ${requested || (priorityRank !== null && priorityRank <= 12 && analysis.basis === "curated-full") ? "open" : ""}><summary><span>${language === "zh" ? "六项论文梳理" : "Six-part paper analysis"}</span><small>${paperAnalysisLabel(analysis)}</small></summary><div class="paper-analysis-disclaimer">${analysis.basis === "curated-full" ? (language === "zh" ? "六项内容已针对该论文单独整理；仍建议在正式引用具体实验数字前回看原文。" : "All six fields are paper-specific; consult the original paper before citing exact experimental numbers.") : analysis.basis === "curated" ? (language === "zh" ? "核心方法描述已针对该论文单独整理；其余字段仍是面向快速阅读的压缩解释。" : "The core method description is paper-specific; the other fields remain compressed reading aids.") : (language === "zh" ? "该概览依据标题、目录分类、更新对象、反馈信号和已有摘要自动归纳；准确引用方法细节时仍应回看原文。" : "This overview is derived from the title, catalog taxonomy, update surface, feedback signal, and available summary. Consult the paper before citing method details.")}</div><div class="paper-analysis-grid"><div><b>${language === "zh" ? "问题动机（含重要性）" : "Problem motivation"}</b><p>${esc(analysis.purpose)}</p>${analysis.basis === "curated-full" ? "" : `<small>${esc(analysis.importance || "")}</small>`}</div><div><b>${language === "zh" ? "相对优势" : "Comparative advantage"}</b><p>${esc(analysis.advantage)}</p></div><div><b>${language === "zh" ? "核心直觉" : "Core intuition"}</b><p>${esc(analysis.core)}</p></div><div><b>${language === "zh" ? "成立依据" : "Why it should work"}</b><p>${esc(analysis.rationale)}</p></div><div><b>${language === "zh" ? "方法流程" : "Method flow"}</b><p>${esc(analysis.logic)}</p></div><div><b>${language === "zh" ? "实验验证" : "Experimental validation"}</b><p>${esc(analysis.validation || "")}</p></div></div></details><div class="links"><a class="link-btn" href="${esc(p.url)}" target="_blank" rel="noopener">${language === "zh" ? "论文" : "Paper"}</a>${p.repo ? `<a class="link-btn repo" href="${esc(p.repo)}" target="_blank" rel="noopener">${language === "zh" ? "代码" : "Code"}</a>` : ""}<button class="link-btn copy-citation" type="button" data-record="${encodeURIComponent(slug)}">${language === "zh" ? "复制引用" : "Copy citation"}</button><a class="link-btn cite-link" href="bibliography.html?paper=${encodeURIComponent(slug)}#ref-${slug}">${language === "zh" ? "引用定位" : "Reference"}</a></div></article>`;
}
function bindPaperCardEvents() {
  document.querySelectorAll(".copy-citation").forEach((button) => button.addEventListener("click", async () => {
    const slug = decodeURIComponent(button.dataset.record || "");
    const record = catalog.find((p) => p.slug === slug);
    if (!record) return;
    try {
      await navigator.clipboard.writeText(citationText(record));
      const original = button.textContent;
      button.textContent = language === "zh" ? "已复制" : "Copied";
      setTimeout(() => { button.textContent = original; }, 1200);
    } catch (error) {
      console.warn("Citation copy failed", error);
    }
  }));
}
function renderRecommendedPaperGroups(visible, filtered) {
  const counts = filtered.reduce((acc, paper) => {
    const role = readingRoleInfo(paper);
    acc[role.id] = (acc[role.id] || 0) + 1;
    return acc;
  }, {});
  let currentRole = "";
  let html = "";
  visible.forEach((paper, index) => {
    const role = readingRoleInfo(paper);
    if (role.id !== currentRole) {
      if (currentRole) html += "</div></section>";
      currentRole = role.id;
      html += `<section class="reference-role-group" data-reading-role="${esc(role.id)}"><header class="reference-role-header"><span>${String((role.rank ?? 0) + 1).padStart(2,"0")}</span><div><h4 data-toc="false">${textOf(role.title)}</h4><p>${textOf(role.description)}</p></div><strong>${counts[role.id] || 0}</strong></header><div class="reference-role-list">`;
    }
    html += paperCard(paper, index + 1);
  });
  if (currentRole) html += "</div></section>";
  return html;
}
function renderPaperList(query = "") {
  const list = document.getElementById("bibliography-list");
  if (!list) return;
  const q = query.trim().toLowerCase();
  const filtered = sortBibliographyRecords(bibliographySubset().filter((p) => !q || paperSearchText(p).includes(q)));
  const requested = new URLSearchParams(location.search).get("paper");
  if (requested) {
    const requestedIndex = filtered.findIndex((p) => p.slug === requested);
    if (requestedIndex >= 0) bibliographyLimit = Math.max(bibliographyLimit, requestedIndex + 1);
  }
  const visible = filtered.slice(0, bibliographyLimit);
  const remaining = Math.max(0, filtered.length - visible.length);
  const cards = bibliographySort === "priority" ? renderRecommendedPaperGroups(visible, filtered) : visible.map((paper, index) => paperCard(paper, index + 1)).join("");
  list.innerHTML = filtered.length ? `${cards}${remaining ? `<button id="load-more-papers" class="load-more">${language === "zh" ? `继续加载 ${Math.min(80, remaining)} 篇（剩余 ${remaining}）` : `Load ${Math.min(80, remaining)} more (${remaining} remaining)`}</button>` : ""}` : `<div class="empty">${language === "zh" ? "没有匹配条目。" : "No matching records."}</div>`;
  bindPaperCardEvents();
  document.getElementById("load-more-papers")?.addEventListener("click", () => { bibliographyLimit += 80; renderPaperList(query); });
  updateCounter(filtered.length === catalog.length ? (language === "zh" ? ` · 已加载 ${visible.length}` : ` · loaded ${visible.length}`) : (language === "zh" ? ` · 匹配 ${filtered.length}，已加载 ${visible.length}` : ` · ${filtered.length} matches, ${visible.length} loaded`));
  if (requested) requestAnimationFrame(() => document.getElementById(`ref-${requested}`)?.scrollIntoView({ block: "center" }));
}
function renderGlobalSearch(query) {
  let box = document.getElementById("global-search-results");
  if (!query) { box?.remove(); return; }
  const q = query.toLowerCase();
  const directionMatches = portfolioDirections().filter((direction) => { const evidence = directionLiterature(direction.id).flatMap((paper) => [paper.title,paper.short,textOf(paper.method),textOf(paper.fit)]); return [direction.code,textOf(direction.title),textOf(direction.question),textOf(direction.boundary),...evidence].join(" ").toLowerCase().includes(q); }).slice(0, 10);
  const ideaMatches = portfolioIdeas().filter((idea) => { const explanation = ideaExplanation(idea.name); const comparison = ideaComparison(idea.name); return [idea.name,textOf(explanation.purpose),textOf(explanation.core),textOf(explanation.rationale),textOf(explanation.logic),textOf(comparison.importance),textOf(comparison.advantage),textOf(idea.thesis),textOf(idea.experiment),textOf(idea.track)].join(" ").toLowerCase().includes(q); }).slice(0, 12);
  const paperMatches = sortBibliographyRecords(catalog.filter((p) => paperSearchText(p).includes(q))).slice(0, 12);
  if (!box) {
    box = document.createElement("section"); box.id = "global-search-results"; box.className = "panel";
    document.getElementById("dynamic-page")?.prepend(box);
  }
  const directionsHtml = directionMatches.length ? `<h3>${language === "zh" ? "研究方向" : "Research directions"}</h3><div class="framework-grid">${directionMatches.map((direction) => `<a class="framework-card" href="research-directions.html#${esc(direction.id)}"><b>${esc(direction.code)} · ${textOf(direction.title)}</b><span>${textOf(direction.question)}</span></a>`).join("")}</div>` : "";
  const ideasHtml = ideaMatches.length ? `<h3>${language === "zh" ? "论文 Idea" : "Paper ideas"}</h3><div class="framework-grid">${ideaMatches.map((idea) => { const direction = directionById(idea.directionId); return `<a class="framework-card paper-card" href="paper-ideas.html#${ideaAnchor(idea.name)}"><b>#${idea.rank} · ${esc(idea.name)}</b><span>${direction ? `${esc(direction.code)} · ${textOf(direction.title)}` : ""}</span></a>`; }).join("")}</div>` : "";
  const papersHtml = paperMatches.length ? `<h3>${language === "zh" ? "文献" : "Literature"}</h3><div class="resource-list">${paperMatches.map(paperCard).join("")}</div>` : "";
  box.innerHTML = `<h2>${language === "zh" ? "全站检索" : "Global search"}</h2>${directionsHtml}${ideasHtml}${papersHtml}${!directionMatches.length && !ideaMatches.length && !paperMatches.length ? `<div class="empty">${language === "zh" ? "没有匹配条目。" : "No matching records."}</div>` : ""}`;
  bindPaperCardEvents();
}
function findCitation(title) {
  const key = normalizeTitle(title);
  if (citationIndex.has(key)) return citationIndex.get(key);
  const candidates = [...citationIndex.entries()].filter(([candidate]) => candidate.includes(key) || key.includes(candidate));
  return candidates.sort((a, b) => Math.abs(a[0].length - key.length) - Math.abs(b[0].length - key.length))[0]?.[1] || null;
}
function hydrateCitations(root = document) {
  root.querySelectorAll("[data-cite]").forEach((node) => {
    const titles = String(node.dataset.cite || "").split("||").map((x) => x.trim()).filter(Boolean);
    const links = titles.map((title) => {
      const record = findCitation(title);
      if (!record) return `<span class="citation-missing" title="${esc(title)}">[?]</span>`;
      const label = node.dataset.citeLabel || `[${record.refNo}]`;
      return `<a href="bibliography.html?paper=${encodeURIComponent(record.slug)}#ref-${record.slug}" title="${esc(record.title)}">${esc(label)}</a>`;
    });
    node.innerHTML = links.join(" ");
    node.classList.add("inline-citations");
  });
}
function currentFilterUrl() {
  const url = new URL(location.href);
  ["method","year","publication","signal","vision","sort","paper","q"].forEach((key) => url.searchParams.delete(key));
  if (activeFilter !== "all") url.searchParams.set("method", activeFilter);
  if (activeYear !== "all") url.searchParams.set("year", activeYear);
  if (activePublicationType !== "all") url.searchParams.set("publication", activePublicationType);
  if (activeSignal !== "all") url.searchParams.set("signal", activeSignal);
  if (visionOnly) url.searchParams.set("vision", "1");
  if (bibliographySort !== "priority") url.searchParams.set("sort", bibliographySort);
  const query = document.getElementById("site-search")?.value.trim();
  if (query) url.searchParams.set("q", query);
  url.hash = "searchable-corpus";
  return url;
}
function syncFilterUrl() {
  if (pageId !== "bibliography") return;
  history.replaceState(null, "", currentFilterUrl());
}
function buildToc() {
  const container = document.getElementById("page-toc");
  if (!container) return;
  const headings = [...document.querySelectorAll("#dynamic-page h2, #dynamic-page h3, #dynamic-page h4")].filter((heading) => heading.dataset.toc !== "false" && !heading.closest(".review-trace-fold,.review-archive-fold") && (heading.id || heading.closest(".panel, .page-chapter, .merged-group, .direction-cluster, .idea-macro-cluster")));
  headings.forEach((heading, index) => { if (!heading.id) heading.id = `${slugify(heading.textContent)}-${index + 1}`; });
  const root = [];
  const stack = [{level:1, children:root}];
  headings.forEach((heading) => {
    const level = Number(heading.tagName.slice(1));
    while (stack.length > 1 && stack[stack.length - 1].level >= level) stack.pop();
    const node = {level, id:heading.id, label:heading.textContent.trim(), children:[]};
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  });
  const renderNodes = (nodes) => `<ul>${nodes.map((node) => `<li class="toc-node toc-level-${node.level}"><a href="#${esc(node.id)}">${esc(node.label)}</a>${node.children.length ? renderNodes(node.children) : ""}</li>`).join("")}</ul>`;
  container.innerHTML = headings.length ? `<div class="toc-title">${language === "zh" ? "本页多级目录" : "Page hierarchy"}</div><nav class="toc-tree" aria-label="${language === "zh" ? "页内多级目录" : "Hierarchical page contents"}">${renderNodes(root)}</nav>` : "";
}
function bindPageEvents() {
  const applyCvprFilters = () => {
    const track = document.querySelector('.cvpr-filter-btn.active[data-cvpr-filter-type="track"]')?.dataset.cvprFilterValue || "all";
    const budget = Number(document.querySelector('.cvpr-filter-btn.active[data-cvpr-filter-type="budget"]')?.dataset.cvprFilterValue || 48);
    document.querySelectorAll(".cvpr-filter-target").forEach((target) => {
      const trackMatch = track === "all" || target.dataset.cvprTrack === track;
      const budgetMatch = Number(target.dataset.cvprGpuHours || 0) <= budget;
      target.closest('[id^="cvpr-"]')?.classList.toggle("cvpr-filter-hidden", !(trackMatch && budgetMatch));
    });
  };
  document.querySelectorAll(".cvpr-filter-btn[data-cvpr-filter-type]").forEach((button) => button.addEventListener("click", () => {
    const type = button.dataset.cvprFilterType;
    document.querySelectorAll(`.cvpr-filter-btn[data-cvpr-filter-type="${type}"]`).forEach((item) => item.classList.toggle("active", item === button));
    applyCvprFilters();
  }));
  const applyIclrFilters = () => {
    const track = document.querySelector('.iclr-filter-btn.active[data-iclr-filter-type="track"]')?.dataset.iclrFilterValue || "all";
    const budget = Number(document.querySelector('.iclr-filter-btn.active[data-iclr-filter-type="budget"]')?.dataset.iclrFilterValue || 48);
    document.querySelectorAll(".iclr-filter-target").forEach((target) => {
      const trackMatch = track === "all" || target.dataset.iclrTrack === track;
      const budgetMatch = Number(target.dataset.iclrGpuHours || 0) <= budget;
      target.closest('[id^="iclr-"]')?.classList.toggle("cvpr-filter-hidden", !(trackMatch && budgetMatch));
    });
  };
  document.querySelectorAll(".iclr-filter-btn[data-iclr-filter-type]").forEach((button) => button.addEventListener("click", () => {
    const type = button.dataset.iclrFilterType;
    document.querySelectorAll(`.iclr-filter-btn[data-iclr-filter-type="${type}"]`).forEach((item) => item.classList.toggle("active", item === button));
    applyIclrFilters();
  }));
  document.querySelectorAll(".iclr-jump").forEach((link) => link.addEventListener("click", () => {
    const target = document.getElementById(`iclr-${link.dataset.iclrId || ""}`);
    const details = target?.querySelector("details");
    if (details) details.open = true;
  }));
  document.querySelectorAll(".cvpr-jump").forEach((link) => link.addEventListener("click", () => {
    const target = document.getElementById(`cvpr-${link.dataset.cvprId || ""}`);
    const details = target?.querySelector("details");
    if (details) details.open = true;
  }));
  document.querySelectorAll(".idea-board-filter").forEach((button) => button.addEventListener("click", () => {
    const filter = button.dataset.ideaFilter || "all";
    document.querySelectorAll(".idea-board-filter").forEach((item) => item.classList.toggle("active", item === button));
    document.querySelectorAll(".idea-filter-target").forEach((target) => {
      const visible = filter === "all" || target.dataset.ideaStage === filter || (filter === "visual" && target.dataset.ideaTrack === "visual");
      target.classList.toggle("idea-filter-hidden", !visible);
    });
  }));
  const refreshBibliography = (syncUrl = true, resetLimit = true) => {
    if (pageId !== "bibliography") return;
    if (resetLimit) bibliographyLimit = 80;
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.toggle("active", (b.dataset.filter || "all") === activeFilter));
    renderPaperList(document.getElementById("site-search")?.value || "");
    if (syncUrl) syncFilterUrl();
  };
  const jumpToCorpus = () => document.getElementById("searchable-corpus")?.scrollIntoView({ block: "start" });
  document.querySelectorAll(".filter-btn, .timeline-label:not(.publication-label)").forEach((button) => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter || "all";
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".timeline-cell:not(.publication-cell)").forEach((button) => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter || "all";
    activeYear = button.dataset.year || "all";
    const yearSelect = document.getElementById("year-filter");
    if (yearSelect) yearSelect.value = activeYear;
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".publication-label").forEach((button) => button.addEventListener("click", () => {
    activePublicationType = button.dataset.publication || "all";
    const select = document.getElementById("publication-filter");
    if (select) select.value = activePublicationType;
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".publication-cell").forEach((button) => button.addEventListener("click", () => {
    activePublicationType = button.dataset.publication || "all";
    activeYear = button.dataset.year || "all";
    const publicationSelect = document.getElementById("publication-filter");
    const yearSelect = document.getElementById("year-filter");
    if (publicationSelect) publicationSelect.value = activePublicationType;
    if (yearSelect) yearSelect.value = activeYear;
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".signal-label").forEach((button) => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter || "all";
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".signal-column").forEach((button) => button.addEventListener("click", () => {
    activeSignal = button.dataset.signal || "all";
    const select = document.getElementById("signal-filter");
    if (select) select.value = activeSignal;
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".signal-cell").forEach((button) => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter || "all";
    activeSignal = button.dataset.signal || "all";
    const signalSelect = document.getElementById("signal-filter");
    if (signalSelect) signalSelect.value = activeSignal;
    refreshBibliography(); jumpToCorpus();
  }));
  document.querySelectorAll(".timeline-year-btn").forEach((button) => button.addEventListener("click", () => {
    activeYear = button.dataset.year || "all";
    const yearSelect = document.getElementById("year-filter");
    if (yearSelect) yearSelect.value = activeYear;
    refreshBibliography(); jumpToCorpus();
  }));
  document.getElementById("year-filter")?.addEventListener("change", (event) => {
    activeYear = event.target.value || "all";
    refreshBibliography();
  });
  document.getElementById("publication-filter")?.addEventListener("change", (event) => {
    activePublicationType = event.target.value || "all";
    refreshBibliography();
  });
  document.getElementById("signal-filter")?.addEventListener("change", (event) => {
    activeSignal = event.target.value || "all";
    refreshBibliography();
  });
  document.getElementById("vision-filter")?.addEventListener("change", (event) => {
    visionOnly = Boolean(event.target.checked);
    refreshBibliography();
  });
  document.getElementById("bibliography-sort")?.addEventListener("change", (event) => {
    bibliographySort = event.target.value || "priority";
    localStorage.setItem("agent-evolution-bibliography-sort", bibliographySort);
    refreshBibliography();
  });
  document.querySelectorAll(".export-btn").forEach((button) => button.addEventListener("click", () => exportBibliography(button.dataset.export || "json")));
  document.getElementById("copy-filter-link")?.addEventListener("click", async (event) => {
    try {
      await navigator.clipboard.writeText(currentFilterUrl().toString());
      const button = event.currentTarget; const original = button.textContent;
      button.textContent = language === "zh" ? "链接已复制" : "Link copied";
      setTimeout(() => { button.textContent = original; }, 1200);
    } catch (error) { console.warn("Filter link copy failed", error); }
  });
  document.getElementById("print-page")?.addEventListener("click", () => window.print());
  document.getElementById("reset-filters")?.addEventListener("click", () => {
    activeFilter = "all"; activeYear = "all"; activePublicationType = "all"; activeSignal = "all"; visionOnly = false;
    const year = document.getElementById("year-filter"); if (year) year.value = "all";
    const publication = document.getElementById("publication-filter"); if (publication) publication.value = "all";
    const signal = document.getElementById("signal-filter"); if (signal) signal.value = "all";
    const vision = document.getElementById("vision-filter"); if (vision) vision.checked = false;
    const search = document.getElementById("site-search"); if (search) search.value = "";
    refreshBibliography();
  });
}
function renderPage() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  const config = PAGES[pageId] || PAGES.home;
  const root = document.getElementById("dynamic-page");
  if (!root || !config) return;
  const pageTitle = textOf(config.title);
  document.title = `${pageTitle} · Agent Self-Evolution Observatory`;
  let description = document.querySelector('meta[name="description"]');
  if (!description) { description = document.createElement("meta"); description.name = "description"; document.head.appendChild(description); }
  description.content = String(textOf(config.lead)).replace(/<[^>]+>/g, "").slice(0, 240);
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) { canonical = document.createElement("link"); canonical.rel = "canonical"; document.head.appendChild(canonical); }
  canonical.href = `https://agent-evolution.lightrain.asia/${pageId === "home" ? "" : `${pageId}.html`}`;
  const socialImage = config.overviewFigure ? `https://agent-evolution.lightrain.asia/${textOf(config.overviewFigure.src)}` : "https://agent-evolution.lightrain.asia/knowledge-map.svg";
  const socialMeta = {
    "og:title": document.title,
    "og:description": description.content,
    "og:url": canonical.href,
    "og:type": pageId === "bibliography" ? "website" : "article",
    "og:image": socialImage,
    "twitter:card": "summary_large_image",
    "twitter:title": document.title,
    "twitter:description": description.content,
  };
  Object.entries(socialMeta).forEach(([property, content]) => {
    const attribute = property.startsWith("twitter:") ? "name" : "property";
    let node = document.head.querySelector(`meta[${attribute}="${property}"]`);
    if (!node) { node = document.createElement("meta"); node.setAttribute(attribute, property); document.head.appendChild(node); }
    node.content = content;
  });
  document.getElementById("structured-data")?.remove();
  const structured = document.createElement("script"); structured.id = "structured-data"; structured.type = "application/ld+json";
  structured.textContent = JSON.stringify({ "@context":"https://schema.org", "@type": pageId === "bibliography" ? "CollectionPage" : "WebPage", name: pageTitle, description: description.content, url: canonical.href, isPartOf:{"@type":"WebSite",name:"Agent Self-Evolution Observatory",url:"https://agent-evolution.lightrain.asia/"} });
  document.head.appendChild(structured);
  renderFooter();
  if (pageId === "home") root.innerHTML = renderHome(config);
  else if (pageId === "system-overview") root.innerHTML = window.renderSystemOverview ? window.renderSystemOverview(config) : renderMergedHub(config);
  else if (config.renderMode === "merged-hub") root.innerHTML = renderMergedHub(config);
  else if (pageId === "research-directions") root.innerHTML = renderDirectionMap(config);
  else if (pageId === "paper-ideas") root.innerHTML = renderIdeaPortfolio(config);
  else if (pageId === "experiments") root.innerHTML = renderExperimentDashboard(config);
  else if (pageId === "direction-board") root.innerHTML = renderIdeaRanking(config);
  else if (pageId === "bibliography") root.innerHTML = renderBibliography(config);
  else if (pageId === "repositories") root.innerHTML = renderDynamicResourceIndex(config, "repositories");
  else if (pageId === "datasets-benchmarks") root.innerHTML = renderDynamicResourceIndex(config, "benchmarks");
  else root.innerHTML = `${pageHeader(config)}${renderOverviewFigure(config)}${(config.sections || []).map(renderSection).join("")}`;
  document.querySelector(".language-toggle")?.replaceChildren(document.createTextNode(language === "en" ? "中文" : "English"));
  bindPageEvents();
  if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
  bindPaperCardEvents();
  hydrateCitations(root);
  updateCitationStatus();
  buildToc();
}

function bindSearch() {
  const input = document.getElementById("site-search");
  if (!input) return;
  input.addEventListener("input", () => {
    const query = input.value.trim();
    if (pageId === "bibliography") { bibliographyLimit = 80; renderPaperList(query); }
    else renderGlobalSearch(query);
  });
}

citationIndex = new Map();
catalog = indexCatalog(mergeCatalog([], DATA));
renderShell();
renderPage();
resetPaperIdeasAfterReload();
bindSearch();
loadCatalog();
