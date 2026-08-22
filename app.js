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
const LANGUAGE_STORAGE_KEY = "agent-evolution-language";
const LEGACY_SCOPED_LANGUAGE_KEYS = {"research-timeline":"research-timeline-language","research-map":"research-map-language","research-directions":"research-directions-language"};
const legacyScopedLanguage = localStorage.getItem(LEGACY_SCOPED_LANGUAGE_KEYS[pageId] || "") || "";
const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) || "";
const pageDefaultLanguage = pageId === "research-timeline" ? "zh" : "en";
let language = storedLanguage || legacyScopedLanguage || pageDefaultLanguage;
if (!storedLanguage && legacyScopedLanguage) localStorage.setItem(LANGUAGE_STORAGE_KEY, legacyScopedLanguage);
else if (!storedLanguage && !legacyScopedLanguage && pageId === "research-timeline") localStorage.setItem(LANGUAGE_STORAGE_KEY, pageDefaultLanguage);
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
    ["HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution", "VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents"],
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
    ["AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"],
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
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"],
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
    ["AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution", "Autogenesis: A Self-Evolving Agent Protocol", "HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry"],
    ["Self-evolving Embodied AI", "WorldEvolver: Self-Evolving World Models for LLM Agent Planning"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry", "MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", "Hidden in Memory: Sleeper Memory Poisoning in LLM Agents", "Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning", "From Memory to Skills: Evidence-Grounded Co-Evolution Governance for Long-Horizon LLM Agents", "FSFM: A Biologically-Inspired Framework for Selective Forgetting of Agent Memory"],
    ["Partially Performative Prediction", "Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback", "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", "Self-Evolving Software Agents", "Accelerating Scientific Discovery with Autonomous Goal-evolving Agents", "AI Agent Pull Requests on GitHub: Frequency, Structure, and Merge Conflict Rates"],
    ["Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", "Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels", "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents", "Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use", "Agentic Uncertainty Quantification", "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents"],
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "MemLens: Benchmarking Multimodal Long-Term Memory", "SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment"],
  ],
  "paper-problem": [
    ["VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning", "Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails"],
    ["EVE-Agent: Evidence-Verifiable Self-Evolving Agents", "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"],
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
    ["VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"],
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
const ZH_INLINE_TEXT = [
  [/Evaluation and Benchmarks/g,"评测与基准"],
  [/Evidence and execution provenance/g,"证据与执行溯源"],
  [/Memory and Context Management/g,"记忆与上下文管理"],
  [/2\.2\.1 Memory Object/g,"2.2.1 记忆对象"],
  [/2\.2\.2 Memory Structure/g,"2.2.2 记忆结构"],
  [/2\.2\.3 Memory Processing/g,"2.2.3 记忆处理"],
  [/Versioned evolution protocol/g,"版本化进化协议"],
  [/Memory-driven exploration/g,"记忆驱动探索"],
  [/Paper Design/g,"论文设计"],
  [/Method Design/g,"方法设计"],
  [/Problem Gate/g,"问题门"],
  [/same-information reducibility/g,"同信息可归约性"],
  [/support-pass/g,"支持通过"],
  [/support-hold/g,"支持暂缓"],
  [/scientific authority/g,"科学权限"],
  [/collision memory/g,"碰撞记忆"],
  [/qualification receipt/g,"资格凭据"],
  [/Paper-first/g,"论文优先"],
  [/\bIdea\b/g,"研究方向"],
  [/\bFresh\b/g,"新现象"],
  [/\bShadow\b/g,"影子搜索"],
  [/\bMemory\b/g,"记忆"],
  [/\bWorkflow\b/g,"工作流"],
  [/\bBaseline\b/g,"对照基线"],
  [/\bPilot\b/g,"局部试验"],
  [/\bstandalone\b/g,"独立论文"],
  [/\bthesis\b/g,"主张"],
  [/\bprovider\b/g,"模型服务"],
  [/\boperator\b/g,"控制器"],
  [/\bPortfolio\b/g,"组合"],
  [/\bMethod\b/g,"方法"],
  [/\bProblem\b/g,"问题"],
  [/\bSupport\b/g,"支持"],
  [/\bauthority\b/g,"权限"],
  [/\bqualification\b/g,"资格验证"],
  [/diagnostic artifact/g,"诊断工件"],
  [/\bartifact\b/g,"工件"],
  [/\blifecycle\b/g,"生命周期"],
  [/\badmission\b/g,"准入"],
  [/\bexecution\b/g,"执行"],
  [/local-validation/g,"局部验证"],
  [/local validation/g,"局部验证"],
  [/\bbackbone\b/g,"主干模型"],
  [/\bcandidate\b/g,"候选"],
  [/\bprobe\b/g,"探针"],
  [/simple baseline/g,"简单对照"],
  [/\bdesign\b/g,"设计"],
  [/\bhidden\b/g,"隐藏"],
  [/\blive\b/g,"实时"],
  [/\bcompleted\b/g,"已完成"],
  [/same-information/g,"同信息"],
  [/\breducibility\b/g,"可归约性"],
  [/matched-simplification/g,"匹配简化对照"],
  [/matched baseline/g,"匹配对照"],
  [/\bformulation\b/g,"表述方案"],
  [/\bdead-end\b/g,"死路"],
  [/\bfeedback\b/g,"反馈"],
  [/\bbaseline\b/g,"对照"],
  [/\bpilot\b/g,"局部试验"],
  [/\bcontribution\b/g,"贡献"],
  [/\bablation\b/g,"消融"],
  [/\breplication\b/g,"复现"],
  [/\befficiency\b/g,"效率"],
  [/\bgenerality\b/g,"泛化"],
  [/\bfailure\b/g,"失败"],
  [/\bsensitivity\b/g,"敏感性"],
  [/\brobustness\b/g,"稳健性"],
  [/\buncertainty\b/g,"不确定性"],
  [/supplement reproduction/g,"补充材料复现"],
  [/\bcontext\b/g,"上下文"],
  [/\breplay\b/g,"回放"],
  [/\bretrieval\b/g,"检索"],
  [/\binteraction\b/g,"交互"],
  [/\blesson\b/g,"经验"],
  [/\bepisodes\b/g,"回合"],
  [/\bepisode\b/g,"回合"],
  [/\bconsolidation\b/g,"整合"],
  [/support set/g,"支持集合"],
  [/contradiction core/g,"反证核心"],
  [/\btool task\b/g,"工具任务"],
  [/\badapter\b/g,"适配器"],
  [/\brollback\b/g,"回滚"],
  [/\bedge\b/g,"边"],
  [/\bgraph\b/g,"图"],
  [/\bpair\b/g,"配对"],
  [/\bpairs\b/g,"配对"],
  [/\btask\b/g,"任务"],
  [/\btasks\b/g,"任务"],
  [/\btrajectory pool\b/g,"轨迹池"],
  [/\bconsensus\b/g,"共识"],
  [/utility-only/g,"仅效用"],
  [/process family/g,"过程族"],
  [/fresh collision/g,"最新碰撞"],
  [/fresh audit/g,"最新审计"],
  [/\bheldout\b/g,"留出"],
  [/\bheld-out\b/g,"留出"],
  [/\bquery\b/g,"查询"],
  [/\bselector\b/g,"选择器"],
  [/\bstatus\b/g,"状态"],
  [/source transaction/g,"来源事务"],
  [/\bterminal\b/g,"终态"],
  [/external-wait/g,"外部等待"],
  [/\bwatch\b/g,"监控"],
  [/\bqueue\b/g,"队列"],
  [/\bhandoff\b/g,"交接"],
  [/\bcontroller\b/g,"控制器"],
  [/\bevidence\b/g,"证据"],
  [/anomaly-first/g,"异常优先"],
  [/\bstale\b/g,"过期"],
  [/\bmalformed\b/g,"格式错误"],
  [/\breviewer\b/g,"审稿者"],
  [/reduction basin/g,"归约盆地"],
  [/\bnovelty\b/g,"新颖性"],
  [/\bmemory\b/g,"记忆"],
  [/\btool\b/g,"工具"],
  [/restoration clause/g,"恢复条款"],
  [/workflow edit/g,"工作流编辑"],
  [/\bcheckpoint\b/g,"检查点"],
  [/\bstorage\b/g,"存储"],
  [/\bsnapshot\b/g,"快照"],
  [/\bcore\b/g,"核心"],
  [/episodic-only/g,"仅情景记忆"],
  [/consolidated memory/g,"整合记忆"],
  [/utility\/refinement/g,"效用/修订"],
  [/\braw\b/g,"原始"],
  [/conclusion-changing/g,"结论改变"],
  [/\bprevalence\b/g,"出现率"],
  [/pairwise residual/g,"成对残余"],
  [/\bselection\b/g,"选择"],
  [/\bintervention\b/g,"干预"],
  [/per-item/g,"单条目"],
  [/\bscore\b/g,"分数"],
  [/\bexclusion\b/g,"排斥"],
  [/\bprecedence\b/g,"优先级"],
  [/co-retrieval/g,"共检索"],
  [/\bharmful\b/g,"有害"],
  [/\bcausal\b/g,"因果"],
  [/\butility\b/g,"效用"],
  [/\bpool\b/g,"池"],
  [/\bsuccess\b/g,"成功"],
  [/\brate\b/g,"比例"],
  [/\bprecision\b/g,"精确率"],
  [/\bmatched\b/g,"匹配"],
  [/\baudit\b/g,"审计"],
  [/\bcost\b/g,"成本"],
  [/repair action set/g,"修复动作集合"],
  [/procedural memory/g,"程序记忆"],
  [/counterexample-driven/g,"反例驱动"],
  [/skill refinement/g,"技能修订"],
  [/skill body/g,"技能主体"],
  [/external applicability gate/g,"外部适用性门"],
  [/half-life/g,"半衰期"],
  [/\bactivation\b/g,"激活"],
  [/local utility drift/g,"局部效用漂移"],
  [/utility-hazard model/g,"效用风险模型"],
  [/audit fraction/g,"审计比例"],
  [/recency\/frequency/g,"最近性/频率"],
  [/\bschema\b/g,"接口模式"],
  [/local-state/g,"局部状态"],
  [/cheap trigger\/ranking/g,"低成本触发/排序"],
  [/pruning\/quarantine/g,"剪枝/隔离"],
  [/\bshift\b/g,"分布偏移"],
  [/utility-based/g,"基于效用"],
  [/\bdependency\b/g,"依赖"],
  [/learned hazard/g,"学习型风险模型"],
  [/\bextractor\b/g,"抽取器"],
  [/worst-process/g,"最差过程"],
  [/\bvariance\b/g,"方差"],
  [/\bmean\b/g,"均值"],
  [/\boutcome\b/g,"结果"],
  [/contrastive extraction/g,"对比抽取"],
  [/cross-trajectory abstraction/g,"跨轨迹抽象"],
  [/influence scope/g,"影响范围"],
  [/\ballocator\b/g,"分配器"],
  [/scope routing/g,"范围路由"],
  [/\bcritic\b/g,"评价器"],
  [/\btruth\b/g,"真值"],
  [/effective candidates/g,"有效候选"],
  [/reserve pool/g,"预留池"],
  [/target variation/g,"目标变化"],
  [/\bExperiment\b/g,"实验"],
  [/full experiment/g,"全量实验"],
  [/sign reversal/g,"符号反转"],
  [/decision context/g,"决策上下文"],
  [/intended-effect realization/g,"预期效应实现"],
  [/parent evidence/g,"父级证据"],
  [/prompt-patch substrate/g,"提示词补丁底座"],
  [/target gain/g,"目标增益"],
  [/effective fraction/g,"有效比例"],
  [/mastered panel/g,"已掌握任务面板"],
  [/\boriginal\b/g,"原任务"],
  [/source scenarios/g,"源场景"],
  [/target scenarios/g,"目标场景"],
  [/\bworkflows\b/g,"工作流"],
  [/\bedits\b/g,"编辑"],
  [/fresh pair-target scenarios/g,"全新配对目标场景"],
  [/\bfidelity\b/g,"保真度"],
  [/\bUpdater\b/g,"更新器"],
  [/discovery episode/g,"发现回合"],
  [/\bPrompt\b/g,"提示词"],
  [/\bProbe\b/g,"探针"],
  [/before\/after/g,"前后对照"],
  [/\bfresh\b/g,"全新"],
  [/\bworkflow\b/g,"工作流"],
  [/\bedit\b/g,"编辑"],
  [/\bcommit\b/g,"提交"],
  [/\btrials\b/g,"试验"],
  [/\bsearch\b/g,"搜索"],
  [/\bsource\b/g,"源"],
  [/\bprogrammatic\b/g,"程序化"],
  [/post-commit/g,"提交后"],
  [/\bconditional\b/g,"条件化"],
  [/\branking\b/g,"排序"],
  [/global-best/g,"全局最优"],
  [/nearest-neighbor/g,"最近邻"],
  [/\bpairwise\b/g,"成对"],
  [/\blistwise\b/g,"列表式"],
  [/\branker\b/g,"排序器"],
  [/\bcalibration\b/g,"校准"],
  [/\bpredictor\b/g,"预测器"],
  [/\btyped\b/g,"类型化"],
  [/\blibrary\b/g,"库"],
  [/\beditor\b/g,"编辑器"],
  [/\bpolicy\b/g,"策略"],
  [/\bbudget\b/g,"预算"],
  [/\bmotif\b/g,"模式"],
  [/\bgroup\b/g,"组"],
  [/\bsubgraph\b/g,"子图"],
  [/\bgrammar\b/g,"语法"],
  [/\brewrite\b/g,"重写"],
  [/\btransfer\b/g,"迁移"],
  [/\bsignature\b/g,"签名"],
  [/\bdiagnosis\b/g,"诊断"],
  [/\bgate\b/g,"门"],
  [/\bretrieved\b/g,"已检索"],
  [/\bplacebo\b/g,"安慰剂"],
  [/first-divergence/g,"首次分叉"],
  [/nonzero effect/g,"非零效应"],
  [/\bregeneration\b/g,"再生成"],
  [/state-signature localization/g,"状态签名定位"],
  [/task baseline/g,"任务对照"],
  [/benefit\/harm sign/g,"收益/伤害符号"],
  [/downstream context/g,"下游上下文"],
  [/formal-method/g,"正式方法"],
  [/soft audit-priority signal/g,"软审计优先级信号"],
  [/paired-rollout/g,"配对运行"],
  [/\brecall\b/g,"召回率"],
  [/hard gate/g,"硬门"],
  [/confirmatory cases/g,"确认性案例"],
  [/\bprompt\b/g,"提示词"],
  [/\bskill\b/g,"技能"],
  [/\bcode\b/g,"代码"],
  [/\bweights\b/g,"参数"],
  [/repair ownership/g,"修复归属"],
  [/persistent surface/g,"持久更新表面"],
  [/source-level/g,"源级"],
  [/\bregistry\b/g,"注册表"],
  [/\bthreshold\b/g,"阈值"],
  [/\bheuristic\b/g,"启发式"],
  [/\bsurvey\b/g,"综述"],
  [/\brun\b/g,"运行"],
  [/\btarget\b/g,"目标"],
  [/\bobjects\b/g,"对象"],
  [/\bobject\b/g,"对象"],
  [/\bproperty\b/g,"属性"],
  [/\bdiscovery\b/g,"发现"],
  [/\bshadow\b/g,"影子搜索"],
  [/\bprimary\b/g,"一手"],
  [/\bcanonical\b/g,"正式"],
  [/\bsupport\b/g,"支持"],
  [/\bverified\b/g,"已验证"],
  [/\brelease\b/g,"发布"],
  [/PAPER-FIRST/g,"论文优先"],
  [/paper-first/g,"论文优先"],
  [/main visuals/g,"主图"],
  [/reviewer question/g,"审稿问题"],
  [/\bclaim\b/g,"主张"],
  [/data\/script\/caption/g,"数据/脚本/图注"],
  [/main comparison/g,"主比较"],
  [/\bmechanism\b/g,"机制"],
  [/negative\/inconclusive/g,"负向/不确定"],
  [/post-C2/g,"C2 后"],
  [/Dead-End/g,"原理死路"],
  [/Pre-check/g,"前置检查"],
  [/\brepair\b/g,"修复"],
  [/clean R1/g,"独立 R1"],
  [/CPU-only/g,"仅 CPU"],
  [/token-matched/g,"Token 匹配"],
  [/nonzero units?/g,"非零单元"],
  [/nonzero effects/g,"非零效应"],
  [/\baction\b/g,"动作"],
  [/state-signature localization/g,"状态签名定位"],
  [/permutation p/g,"置换检验 p"],
  [/trajectory branch/g,"轨迹分支"],
  [/candidate-global replicated-effect/g,"候选级全局可复现效应"],
  [/soft 审计-priority signal/g,"软审计优先级信号"],
  [/hard 门/g,"硬门"],
  [/archived secondary diagnostic/g,"归档次级诊断"],
  [/\beffect sign\b/g,"效应符号"],
  [/\beffect\b/g,"效应"],
  [/local state/g,"局部状态"],
  [/task-level/g,"任务级"],
  [/\btransport\b/g,"迁移"],
  [/\bidea\b/g,"研究方向"],
  [/1-step/g,"一步"],
  [/5-step/g,"五步"],
  [/\bsignal\b/g,"信号"],
];
const ZH_PURE_TEXT = new Map([
  ["CANONICAL TEMPORAL FLOW","统一时间主流程"],
  ["SCOPE","范围界定"],
  ["EVIDENCE","证据"],
  ["NOVELTY","新颖性"],
  ["METHOD","方法"],
  ["EXPERIMENT BLUEPRINT","实验蓝图"],
  ["ECONOMY COMPILE","资源经济编译"],
  ["LOCAL VALIDATION","局部验证"],
  ["METHOD FREEZE","方法冻结"],
  ["FULL EXPERIMENT","全量实验"],
  ["PAPER EVIDENCE","论文证据"],
  ["LEARN","系统学习"],
  ["Current Research State","当前科研状态"],
  ["CURRENT","当前"],
  ["PIPELINE","流程"],
  ["JUDGE","裁决"],
  ["BACKEND ARCHITECTURE MANIFEST","后端架构清单"],
  ["CROSS-CUTTING METHODOLOGY CONTROLS","跨模块方法学控制"],
  ["Content-addressed trigger","内容寻址触发器"],
  ["P0 ECONOMY · BEFORE EXPERIMENT COMPILE","P0 资源经济 · 实验编译前"],
  ["Matched-Simplification Tournament","匹配简化对照赛"],
  ["ASSET-FIRST ICLR 2027 · PAPER QUALITY V2.1","工件优先 · ICLR 2027 · 论文证据质量 V2.1"],
  ["closest-work table + provenance + evidence/collision graph","最近工作表 + 溯源 + 证据/碰撞图"],
  ["gap + closest work + novelty axis + contribution claim + irreducible difference","问题缺口 + 最近工作 + 新颖性轴 + 贡献主张 + 不可约差异"],
  ["Economy 5/5 + Protocol Validity + REP + Pre-Experiment Card + 8 Gate","资源经济 5/5 + 协议有效性 + REP + 实验前卡片 + 8 道门"],
  ["F0 + P0-Support + minimal P0-Method evidence","F0 + P0 支持验证 + 最小 P0 方法证据"],
  ["method hash + blueprint hash + local-validation decision","方法哈希 + 蓝图哈希 + 局部验证裁决"],
  ["full-scale result package + replication + ablations + efficiency","全量结果包 + 复现 + 消融 + 效率"],
  ["Evidence Integrity / Chain-of-Evidence + paper-ready tables/figures","证据完整性 / 证据链 + 论文就绪表格/图"],
  ["rules/tests/config + Failure Assets + Meta-Trace + public snapshot","规则/测试/配置 + 失败资产 + 科学元轨迹 + 公开快照"],
  ["Retain zero-reward blast-radius only as a diagnostic under cross-task effect transport; no standalone GPU.","零奖励爆炸半径只保留为跨任务效应迁移下的诊断项；不再作为独立 GPU 方向。"],
  ["Keep the sequential-control problem; do not train a controller until a materially new persistent updater/admission stream passes qualification.","保留序列控制这一科学问题；只有实质全新的持久更新器/准入流通过资格验证后，才允许训练控制器。"],
  ["Stop GPU work on this prompt-patch P0 instance. Reopen A-3 only with a newly qualified update substrate/action stream and a newly frozen fresh-candidate validation; otherwise send the direction to human pivot/drop review.","停止当前提示词补丁 P0 实例的 GPU 工作。只有新的更新底座/动作流通过资格验证，并重新冻结全新候选验证后，才允许重开 A-3；否则转人工决定转向或放弃。"],
  ["Merge A-4 into a direct ordered-composition risk/repair baseline; the typed registry adds no held-out prediction or repair value.","把 A-4 并入直接的有序组合风险/修复对照；类型化注册表没有带来额外的留出预测或修复价值。"],
  ["Merge A-5 into generic version/history infrastructure; do not spend GPU on a standalone semantic-compaction method.","把 A-5 并入通用版本/历史基础设施；不要为独立的语义压缩方法继续消耗 GPU。"],
  ["Do not open hidden E_orig or train a B-2 selector on this table. Reopen only with a fresh dedicated deletion-sensitivity collection that independently supplies >=30 reproducible conclusion-change cases; otherwise send B-2 to human pivot/drop review.","不要打开隐藏 E_orig，也不要在当前表上训练 B-2 选择器。只有新的专用删除敏感性数据能够独立提供至少 30 个可复现的结论改变案例时才重开；否则转人工决定转向或放弃 B-2。"],
  ["Stop the current ALFWorld B-3 instance and send it to human pivot/drop review; reopen only on a fresh co-retrieval substrate with at least six independent unseen pair-target units.","停止当前 ALFWorld B-3 实例并转人工决定转向或放弃；只有新的共检索底座拥有至少 6 个独立、未见的配对目标单元时才允许重开。"],
  ["Merge B-5 into a standard compact precondition/ILP learner; monotone counterexample specialization adds no independent boundary-generalization value.","把 B-5 并入标准的紧凑前置条件/ILP 学习器；单调反例专化没有带来独立的边界泛化价值。"],
  ["Retain only a simple cache/revalidation policy; the learned utility-hazard model adds no future-reuse decision value.","只保留简单缓存/重验证策略；学习型效用风险模型没有增加未来复用的决策价值。"],
  ["Respect the typed F0 stop/hold; no GPU method expansion.","遵守类型化 F0 的停止/暂缓结论；不扩展 GPU 方法实验。"],
  ["Keep cross-version matrices only as diagnostics; merge evaluator repair into simple frozen-anchor calibration and do not spend GPU on standalone C-2.","跨版本矩阵只保留为诊断证据；把评价器修复并入简单的冻结锚点校准，不再为独立 C-2 消耗 GPU。"],
  ["Keep verifier counterexamples but drop per-example 1-minimality as a standalone curriculum variable; merge into generic counterexample learning.","保留验证器反例，但放弃把逐样本 1-minimality 作为独立课程变量；并入通用反例学习。"],
  ["Cross-version trend selection collapses to same-information direct yield prediction.","跨版本趋势选择可归约为同信息条件下的直接收益预测。"],
  ["Merge D-2 into direct mutation-yield prediction; retain versioned ranking as a diagnostic.","把 D-2 并入直接的变异收益预测；版本化排序只保留为诊断。"],
  ["Do not open hidden workflows or train the E-1 ranker on this table. Reopen only after a newly frozen paired intervention table has genuine non-tied edit effects at the preregistered source gate; otherwise send E-1 to human pivot/drop review.","不要打开隐藏工作流，也不要在当前表上训练 E-1 排序器。只有新冻结的配对干预表在预注册源域门上出现真实、非并列的编辑效应时才允许重开；否则转人工决定转向或放弃 E-1。"],
  ["Merge E-2 motif context into E-1/CE-Graph-style editing; do not spend GPU on a standalone causal-rewrite paper.","把 E-2 的模式上下文并入 E-1/CE-Graph 风格编辑；不再为独立的因果重写论文消耗 GPU。"],
  ["Direct action disagreement exactly reproduces the selector.","直接动作分歧可以精确复现该选择器。"],
  ["Keep decision-changing residuals as a data-selection diagnostic; drop standalone selector mechanism.","把会改变决策的残余保留为数据选择诊断；放弃独立选择器机制。"],
  ["Equal-capacity direct shield is exactly equivalent.","同容量直接安全屏障完全等效。"],
  ["Retain predecessor rules as shield explanations; no standalone GPU run.","把前驱规则保留为安全屏障解释；不再进行独立 GPU 实验。"],
  ["Direct residual-conditioned recovery policy is exactly equivalent.","直接的残余条件恢复策略完全等效。"],
  ["Retain recurrence audit and direct recovery policy; no standalone GPU run.","保留重现性审计和直接恢复策略；不再进行独立 GPU 实验。"],
  ["Stop standalone A-6; the current active query policy is exactly reproduced by non-learning binary group testing under the same sparse-fault prior.","停止独立 A-6；在相同稀疏故障先验下，非学习型二元组测试可以精确复现当前主动查询策略。"],
  ["Merge A-7 into A-2 as a simple same-state counterfactual decision rule; do not spend GPU on a standalone learned-controller paper.","把 A-7 并入 A-2，作为简单的同状态反事实决策规则；不再为独立的学习型控制器论文消耗 GPU。"],
  ["Human authors review and accept responsibility for the final manuscript and AI-use disclosure, freeze the complete author list before the ICLR abstract deadline, complete the OpenReview signoff checklist, then submit the genuine abstract by 2026-09-18 AoE and the paper plus anonymous supplement by 2026-09-25 AoE. Do not reopen dynamic P0 or broaden N1-N3 unless independently qualified new evidence appears.","作者需审阅最终稿与 AI 使用声明并承担责任，在 ICLR 摘要截止前冻结完整作者名单，完成 OpenReview 签字清单，然后于 2026-09-18 AoE 前提交真实摘要、于 2026-09-25 AoE 前提交论文和匿名补充材料。除非出现独立通过资格审查的新证据，否则不要重开动态 P0，也不要扩大 N1–N3。"],
  ["ICLR 2027 author-facing pages are aligned: submit the genuine abstract and freeze author membership by 2026-09-18 AoE; submit the full paper and anonymous supplement by 2026-09-25 AoE. Complete profile/quota/reviewer/dual-submission/ethics/AI-use signoff; do not reopen dynamic P0 or broaden N1-N3.","ICLR 2027 面向作者的官方页面已经一致：2026-09-18 AoE 前提交真实摘要并冻结作者成员；2026-09-25 AoE 前提交全文与匿名补充材料。同时完成账号资料、名额、审稿人、双重投稿、伦理与 AI 使用声明确认；不要重开动态 P0，也不要扩大 N1–N3 的主张范围。"],
  ["Stop standalone replication-gate escalation on this memory substrate; retain replication quality only as a diagnostic under B-9. Reopen only for a materially different update substrate.","停止在当前记忆底座上继续把复现门升级为独立方向；复现质量只作为 B-9 下的诊断保留。只有出现实质不同的更新底座时才重开。"],
  ["Archive the current transport-method line for this substrate/cycle. Support phenomenon remains valid, but no current representation beats simple baselines; no fresh-heldout GPU or second backbone.","归档当前底座/周期上的迁移方法路线。现象支持仍然有效，但当前表示均未超过简单对照；不启动新的留出 GPU，也不启用第二主干模型。"],
  ["Stop standalone B-10 and do not spend GPU; retain this P0 as the matched-simplification falsifier and return the drop/merge decision to human review.","停止独立 B-10，不再消耗 GPU；把该 P0 保留为匹配简化证伪器，并把放弃/合并决定交回人工审查。"],
  ["Return E-3 to human DROP/merge review; deterministic isomorphic P/E/X matches hidden state-changing effects and recovery under the same six-probe budget.","把 E-3 交回人工放弃/合并审查；在相同六探针预算下，确定性的同构 P/E/X 已匹配隐藏状态变化效应与恢复表现。"],
  ["Return E-4 to human DROP/merge review; the matched non-learning Boolean rule is equivalent or the safe-workload gate failed.","把 E-4 交回人工放弃/合并审查；匹配的非学习型布尔规则已经等效，或安全工作负载门未通过。"],
  ["Current prompt-patch substrate fails the block-only updater gate: 1/8 positive target-gain candidates and effective fraction 0.125 < required 0.400. Fresh A-3 collection is forbidden.","当前提示词补丁底座未通过仅阻断式更新器门：正目标增益候选为 1/8，有效比例 0.125 < 要求的 0.400；禁止采集新的 A-3 数据。"],
  ["ECONOMY + COMPILE","资源经济 + 编译"],
  ["EVIDENCE-KNOWLEDGE","证据与知识"],
  ["PAPER-DESIGN","论文设计"],
  ["EXPERIMENT-DESIGN","实验设计"],
  ["SCIENTIFIC-VALIDATION","科学验证"],
  ["RUNTIME-AUTHORITY","运行权限"],
  ["MEMORY-PUBLICATION","记忆与发布"],
  ["Owner","负责人"],
  ["AI CLINIC","AI 会诊"],
  ["SIMPLIFY","简化对照"],
  ["SUBSTRATE","实验底座"],
  ["Substrate Inventory","底座清单"],
  ["CAUSAL","因果"],
  ["Causal Unit / Observable","因果单元 / 可观测量"],
  ["Decision-Changing VOI","改变决策的信息价值"],
  ["AUTH","权限"],
  ["Single-Writer Authority","单写入者权限"],
  ["READY","就绪"],
  ["Paper Quality v2.1","论文证据质量 v2.1"],
  ["Visual Evidence","可视化证据"],
  ["Canonical Fresh Discovery","正式新现象发现"],
  ["PROBLEM DISCOVERY · BEFORE PAPER DESIGN","问题发现 · 论文设计前"],
  ["1 · PRIMARY EVIDENCE","1 · 一手证据"],
  ["1B · LANE COVERAGE","1B · 搜索通道覆盖"],
  ["1B2 · SCIENTIFIC OBJECT AXIS","1B2 · 科学对象轴"],
  ["1B3 · OBJECT RETRIEVAL GAP AUDIT","1B3 · 对象检索缺口审计"],
  ["1B4 · OBJECT CANDIDATE PRIMARY VERIFY","1B4 · 对象候选一手验证"],
  ["1B5 · SUPPORT RELEASE WATCH","1B5 · 支持证据发布监控"],
  ["1B6 · SUPPORT ASSET RECHECK QUEUE","1B6 · 支持资产复查队列"],
  ["1B7 · SUPPORT INVENTORY HANDOFF","1B7 · 支持库存交接"],
  ["1B8 · DISCOVERY FRONTIER","1B8 · 发现前沿"],
  ["1B9 · FRESH PHENOMENON PORTFOLIO","1B9 · 新现象组合"],
  ["1C · SOURCE TRANCHE","1C · 来源批次"],
  ["1C2 · NO-LANE CARRIER PROBE","1C2 · 无通道载体探针"],
  ["1D · DISCOVERY CONTRACT","1D · 发现合同"],
  ["1E · SHADOW SEARCH LAB","1E · 影子搜索实验室"],
  ["1F · SHADOW RUN ADMISSION","1F · 影子运行准入"],
  ["1G · SHADOW CONTINUATION FRONTIER","1G · 影子搜索继续边界"],
  ["2 · 4-LANE PROBLEM GENERATOR","2 · 四通道问题生成器"],
  ["2B · SATURATION / DEAD-END MEMORY","2B · 饱和 / 死路记忆"],
  ["2C · 4-LANE SEARCH AUDIT","2C · 四通道搜索审计"],
  ["2D · GLOBAL RELATION RECALL","2D · 全局关系召回"],
  ["2E · RELATION DELTA PREFLIGHT","2E · 关系增量前置检查"],
  ["2F · MANUAL RELATION SCAN ADMISSION","2F · 人工关系扫描准入"],
  ["3 · SEMANTIC BLOCKER","3 · 语义阻断器"],
  ["CURRENT RESEARCH OS","当前科研操作系统"],
  ["EVIDENCE → HYPOTHESIS","证据 → 假设"],
  ["DECISION → LEARN → PUBLISH","裁决 → 沉淀 → 发布"],
  ["SELF-EVOLVING RESEARCH OS","自进化科研操作系统"],
  ["DECISION LEDGER","决策账本"],
  ["REPAIR","修复"],
  ["AUTOMATION","自动化"],
  ["SCIENTIFIC META-TRACE","科学元轨迹"],
  ["FAILURE ASSETS","失败资产"],
  ["EXPERIMENT VALUE","实验价值"],
  ["CAPABILITY REGISTRY","能力注册表"],
  ["LITERATURE AUDIT","文献审计"],
  ["EVIDENCE INTEGRITY","证据完整性"],
  ["EXTERNAL SYSTEM LEARNING","外部系统学习"],
  ["LOCAL VALIDATION SUB-MACHINE · P0-SYSTEM v2","局部验证子状态机 · P0-SYSTEM v2"],
  ["REPAIR BUDGET","修复预算"],
  ["PRE-MODEL LOAD","模型加载前检查"],
  ["REQUIRED","必须"],
  ["RAW TRACE","原始轨迹"],
  ["MANDATORY","强制"],
  ["GPU LEASE","GPU 租约"],
  ["GPU-0 · SURVIVOR GATE","GPU-0 · 存活方向准入"],
  ["AI CONSULTATION CLINIC · CROSS-CUTTING","AI 会诊 · 跨阶段"],
  ["PAPER-FIRST · BEFORE IMPLEMENTATION","论文优先 · 实现前"],
  ["PRINCIPLE · BEFORE EXPERIMENT DESIGN","原理 · 实验设计前"],
  ["PROTOCOL VALIDITY · BEFORE SCIENTIFIC INTERPRETATION","协议有效性 · 科学解释前"],
  ["UPDATER · BEFORE GATE 1","更新器 · Gate 1 前"],
  ["RESEARCH EXECUTION PLAN · DERIVED, NOT A GATE","科研执行计划 · 派生接口，非新增门"],
  ["PRE-EXPERIMENT COMPILER · GATE 1–8","实验前编译器 · Gate 1–8"],
  ["GATE 3 · IDENTIFIABILITY SUB-AUDIT","Gate 3 · 可辨识性子审计"],
  ["A-1 · PROMPT PATCH","A-1 · 提示词补丁"],
  ["A-2 · UPDATE STREAM","A-2 · 更新流"],
  ["STATISTICAL RESOLUTION","统计分辨率"],
  ["MEASURED THROUGHPUT","实测吞吐"],
  ["SEALED HIDDEN","密封隐藏集"],
  ["NO EVALUATOR LEAK","无评测器泄漏"],
  ["INDEPENDENT TRUTH","独立真值"],
  ["MATCHED INFORMATION","信息匹配"],
  ["CLAIM ↔ METRIC","主张 ↔ 指标"],
  ["VERSIONED EVALUATOR","版本化评测器"],
  ["SHORTCUT AUDIT","捷径审计"],
  ["OBJECTIVE / PREDICTION","目标 / 预测"],
  ["DEPENDENCIES / CHECKPOINTS","依赖 / 检查点"],
  ["CAPABILITIES / ARTIFACTS","能力 / 工件"],
  ["FALLBACK","回退策略"],
  ["1 · PAPER NOVELTY","1 · 论文新颖性"],
  ["2 · METHOD DESIGN","2 · 方法设计"],
  ["3 · EXPERIMENT BLUEPRINT","3 · 实验蓝图"],
  ["4 · PAPER EVIDENCE QUALITY V2.1","4 · 论文证据质量 V2.1"],
  ["5 · VISUAL EVIDENCE CONTRACT","5 · 可视化证据合同"],
  ["6 · RESET ON CORE CHANGE","6 · 核心变化即重置"],
  ["1 · PRIMITIVES / ASSUMPTIONS","1 · 基本对象 / 假设"],
  ["2 · MECHANISM / PREDICTIONS","2 · 机制 / 预测"],
  ["3 · OPERATIONALIZATION","3 · 操作化"],
  ["4 · FAILURE UPDATE","4 · 失败更新"],
  ["after-evidence-before-hypothesis-freeze","证据完成后、研究假设冻结前"],
  ["before-p0-economy-freeze","P0 资源经济冻结前"],
  ["after-economy-pass-before-first-expensive-launch","资源经济通过后、首次高成本运行前"],
  ["after-screening-or-nonpositive-pilot-before-repair","筛查/非正向局部试验后、修复前"],
  ["before-full-p0-second-backbone-p1-or-paper-claim-expansion","全量 P0、第二主干模型、P1 或论文主张扩展前"],
  ["attack the scientific formulation before implementation begins","在实现开始前攻击科学问题表述"],
  ["find cheap ways to kill or simplify the method before GPU work","在 GPU 工作前寻找低成本证伪或简化方法的路径"],
  ["red-team the exact frozen experiment contract, not the idea wording","红队审查冻结的精确实验合同，而不是研究方向措辞"],
  ["separate formulation, substrate, representation, optimization, baseline, and execution failures before another run","在再次运行前区分表述、底座、表示、优化、对照与执行失败"],
  ["recheck novelty and marginal value before multiplying compute","在扩大算力前重新核验新颖性与边际价值"],
  ["Use frozen existing P0 evidence; do not rerun identical compute.","使用已冻结的现有 P0 证据；不要重复运行相同计算。"],
  ["Merge branch soft-audit into research-system scheduling; stop standalone A-1 repair and do not spend GPU unless a materially new observable/substrate is proposed.","把分支 soft-audit 并入科研系统调度；停止独立 A-1 修复，除非提出实质全新的可观测量/实验底座，否则不再消耗 GPU。"],
  ["Merge evidence-depth scheduling into A-1/system soft audit; stop standalone A-2 repair and do not launch controller GPU training.","把 evidence-depth 调度并入 A-1/系统 soft audit；停止独立 A-2 修复，不启动控制器 GPU 训练。"],
  ["Human authors must verify the live ICLR/OpenReview deadline because official ICLR pages currently conflict.","作者必须在提交前人工核验实时 ICLR/OpenReview 截止日期；当前官方 ICLR 页面信息存在冲突。"],
  ["4 · GATED INBOX","4 · 门控收件箱"],
]);
function localizeZhInline(value = "") {
  let text = String(value || "");
  if (!/[\u3400-\u9fff]/.test(text)) return text;
  const protectedTokens = [];
  const protect = (match) => {
    const index = protectedTokens.push(match) - 1;
    return `⟦M${index}⟧`;
  };
  // Display localization must never mutate auditable machine identities. Protect
  // typed enums, PA/PF/SP/STRI IDs, content-addressed hashes, and multi-hyphen
  // run/method identifiers before translating surrounding explanatory prose.
  text = text
    .replace(/\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g, protect)
    .replace(/\b(?:PA|PF|SP|STRI)(?:-[A-Za-z0-9]+)+\b/g, protect)
    .replace(/\b[a-z0-9]+(?:-[a-z0-9]+){2,}\b/g, protect)
    .replace(/\b[a-f0-9]{12,64}\b/g, protect);
  ZH_INLINE_TEXT.forEach(([pattern,replacement]) => { text = text.replace(pattern,replacement); });
  return text.replace(/⟦M(\d+)⟧/g, (_, index) => protectedTokens[Number(index)] || _);
}
function localizedDisplayText(value = "") {
  const raw = String(value ?? "");
  if (language !== "zh") return raw;
  const trimmed = raw.trim();
  if (ZH_PURE_TEXT.has(trimmed)) return raw.replace(trimmed, ZH_PURE_TEXT.get(trimmed));
  return localizeZhInline(raw);
}
function textOf(value) {
  if (typeof value === "string") return value;
  if (!value) return "";
  const selected = value[language] || value.en || value.zh || "";
  return language === "zh" && value.zh ? localizeZhInline(selected) : selected;
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
function renderNavigation() {
  const nav = document.querySelector(".sidebar .nav");
  if (!nav) return;
  nav.innerHTML = NAV_GROUPS.map((group) => {
    const isOpen = group.pages.some(([href]) => href.replace(".html", "") === pageId) || group.open;
    return `<details class="nav-group" ${isOpen ? "open" : ""}><summary class="nav-level1"><span>${esc(textOf(group.title))}</span><span class="nav-chevron">⌄</span></summary><div class="nav-children">${group.pages.map(([href, label]) => {
      const active = href.replace(".html", "") === pageId || (href === "index.html" && pageId === "home");
      return `<a class="nav-level2 ${active ? "active" : ""}" href="${href}">${esc(textOf(label))}</a>`;
    }).join("")}</div></details>`;
  }).join("");
}
function syncShellLanguage() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  const brandStrong = document.querySelector(".brand strong");
  const brandSpan = document.querySelector(".brand span");
  if (brandStrong) brandStrong.textContent = language === "zh" ? "Agent 自进化" : "Agent Self-Evolution";
  if (brandSpan) brandSpan.textContent = language === "zh" ? "科研观测站" : "Research Observatory";
  const searchInput = document.getElementById("site-search");
  if (searchInput) searchInput.placeholder = pageId === "research-timeline"
    ? (language === "zh" ? "搜索时间轴、研究问题、实验、论文或状态…" : "Search timeline, research questions, experiments, papers, or states…")
    : pageId === "bibliography"
      ? (language === "zh" ? "搜索论文、方法、方向或关键词…" : "Search papers, methods, directions, or keywords…")
      : (language === "zh" ? "搜索研究站内容…" : "Search the observatory…");
  const resultCount = document.getElementById("result-count");
  if (resultCount && pageId === "paper-ideas") resultCount.textContent = language === "zh" ? "当前研究方向账本" : "Current idea ledger";
  const languageToggle = document.querySelector(".language-toggle");
  if (languageToggle) languageToggle.textContent = language === "en" ? "中文" : "English";
  const skipLink = document.querySelector(".skip-link");
  if (skipLink) skipLink.textContent = language === "zh" ? "跳到正文" : "Skip to content";
  const sidebarNote = document.querySelector(".sidebar-note");
  if (sidebarNote) {
    sidebarNote.textContent = pageId === "system-overview"
      ? (language === "zh" ? "10 个阅读章节 · 统一 21 阶段科研到投稿生命周期 · 6 个职责层 · P0 七阶段验证子状态机" : "10 reader chapters · canonical 21-stage research-to-submission lifecycle · 6 responsibility layers · P0 7-stage validation sub-machine")
      : pageId === "research-timeline"
        ? (language === "zh" ? "完整研究历史只读投影 · 时间轴不新增科研权限" : "Read-only full research history · no new scientific authority")
        : pageId === "research-map"
          ? (language === "zh" ? "A–G 当前研究组合 · 只读映射 · 权威结论仍在 ResearchItem" : "Current A–G portfolio · read-only map · authoritative decisions stay on ResearchItems")
          : pageId === "research-directions"
            ? (language === "zh" ? "领域图谱总入口 · 六阶段主线 · D1–D10 总表 · 连接当前 A–G" : "Field-atlas entry · six-stage spine · D1–D10 comparison · bridge to current A–G")
            : pageId === "mechanisms"
              ? (language === "zh" ? "统一领域矩阵 · 更新对象 × 环境约束 × 证据标准 · 详细内容按需展开" : "Unified field matrix · update surface × environment × evidence · details on demand")
              : pageId === "foundations"
                ? (language === "zh" ? "定义与边界 · 核心名词 · 四个分类问题 · 历史全景统一进入领域图谱" : "Definition and boundary · core vocabulary · four classification questions · history lives in the Field Atlas")
                : pageId === "bibliography"
                  ? (language === "zh" ? "先看来源与可信度 · 再看领域分布 · 再决定读什么 · 最后检索、引用与导出" : "Provenance first · field maps next · choose what to read · search, cite, and export last")
                  : (language === "zh" ? "实时科研状态 · 文献、实验与论文证据持续更新" : "Live research state · literature, experiments, and paper evidence update continuously");
  }
  renderNavigation();
  renderFooter();
}
function setLanguage(next) {
  const oldHeight = Math.max(document.documentElement.scrollHeight, 1);
  const ratio = window.scrollY / oldHeight;
  language = next;
  localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  syncShellLanguage();
  renderPage();
  requestAnimationFrame(() => window.scrollTo(0, ratio * document.documentElement.scrollHeight));
}

function renderFooter() {
  const footer = document.querySelector(".footer");
  const updated = window.RESEARCH_SYSTEM_STATE?.generated_at || window.S2_LITERATURE_META?.retrieved_at || "";
  const updatedLabel = updated ? new Date(updated).toLocaleDateString(language === "zh" ? "zh-CN" : "en-US", {year:"numeric",month:"short",day:"numeric"}) : (language === "zh" ? "持续维护" : "continuously maintained");
  if (footer) footer.innerHTML = `${language === "zh" ? "Agent 自进化研究站" : "Agent Self-Evolution Observatory"} · <a href="bibliography.html#group-coverage-method">${language === "zh" ? "覆盖协议" : "Coverage protocol"}</a> · <a href="bibliography.html">${language === "zh" ? "动态文献库" : "Live bibliography"}</a> · <a href="https://www.semanticscholar.org/product/api" target="_blank" rel="noopener">${language === "zh" ? "文献元数据由 Semantic Scholar 提供" : "Literature metadata powered by Semantic Scholar"}</a> · <a href="https://github.com/lightrain-a/agent-self-evolution-observatory" target="_blank" rel="noopener">GitHub</a> · ${updatedLabel}`;
}
function renderSemanticScholarStatus() {
  const meta = window.S2_LITERATURE_META;
  if (!meta) return `<div class="integrity-status warn s2-provider-status"><strong>${language === "zh" ? "S2 快照" : "S2 SNAPSHOT"}</strong><span>${language === "zh" ? "尚未加载 Semantic Scholar 同步快照；当前仍可使用人工文献库。" : "No Semantic Scholar sync snapshot is loaded; the curated literature corpus remains available."}</span></div>`;
  const stats = meta.statistics || {};
  const retrieved = meta.retrieved_at ? new Date(meta.retrieved_at).toLocaleString(language === "zh" ? "zh-CN" : "en-US") : (language === "zh" ? "未知" : "unknown");
  const expanded = meta.seed_expansion?.expanded_count || 0;
  return `<div class="integrity-status pass s2-provider-status"><strong>${language === "zh" ? "S2 实时同步" : "S2 LIVE"}</strong><span>${language === "zh" ? `已同步 ${stats.paper_count || 0} 篇候选文献，覆盖 ${stats.query_count || 0} 条五路检索，并通过引用图补充 ${expanded} 篇；更新时间 ${retrieved}。这些结果用于发现最近工作，不自动等同于新颖性判断。` : `${stats.paper_count || 0} candidate papers from ${stats.query_count || 0} five-route queries, including ${expanded} citation-graph additions; updated ${retrieved}. These matches support discovery and do not constitute an automatic novelty verdict.`}</span></div>`;
}
function renderShell() {
  if (!document.querySelector('link[rel="icon"]')) document.head.insertAdjacentHTML("beforeend", '<link rel="icon" href="favicon.svg" type="image/svg+xml">');
  if (!document.querySelector('link[rel="manifest"]')) document.head.insertAdjacentHTML("beforeend", '<link rel="manifest" href="site.webmanifest">');
  document.body.insertAdjacentHTML("afterbegin", `<a class="skip-link" href="#main-content">Skip to content</a><button class="sidebar-overlay" aria-label="Close navigation" hidden></button><button class="back-to-top" type="button" aria-label="Back to top">↑</button>`);
  const sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;
  sidebar.insertAdjacentHTML("afterbegin", `<button class="sidebar-close" aria-label="Close navigation">×</button>`);
  renderNavigation();
  const topbar = document.querySelector(".topbar");
  const searchInput = document.getElementById("site-search");
  if (pageId === "bibliography" && initialQuery.get("q") && searchInput) searchInput.value = initialQuery.get("q");
  if (topbar && !topbar.querySelector(".language-toggle")) {
    topbar.insertAdjacentHTML("beforeend", `<button class="language-toggle" type="button">${language === "en" ? "中文" : "English"}</button>`);
  }
  syncShellLanguage();
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
const ZH_UPDATE_TARGET = {
  "agent component":"Agent 组件", memory:"记忆", "model parameters":"模型参数", prompt:"提示词", "prompt/context":"提示词/上下文",
  "tool/skill":"工具/技能", "workflow/scaffold":"工作流/脚手架", "world model":"世界模型", other:"其他"
};
const ZH_PUBLICATION_TYPE = {Published:"正式发表",Preprint:"预印本",Repository:"代码仓库","Blog/Report":"博客/报告",Other:"其他"};
const ZH_SIGNAL = {
  "critique/evaluation":"批评/评测", "environment interaction":"环境交互", "experience reuse":"经验复用", "population/self-play":"群体/自博弈",
  "scalar reward":"标量奖励", "scalar/preference reward":"标量/偏好奖励", "self-generated artifact":"自生成工件", "verification/tests":"验证/测试",
  "trace and provenance analysis":"轨迹与溯源分析", "multiple feedback types":"多类反馈", "runtime experience":"运行时经验", "experience and feedback":"经验与反馈",
  "environment feedback":"环境反馈", "retrieval and graph-edit feedback":"检索与图编辑反馈", "difficulty and diversity rewards":"难度与多样性奖励",
  "self-evaluation":"自评", "selector-predictor-judger feedback":"选择器/预测器/评判器反馈", "trajectory success and failure":"轨迹成功/失败信号",
  "propose-solve-evaluate-learn":"提出→求解→评测→学习", "self-constructed object-level preferences":"自构造对象级偏好", "bandit feedback":"Bandit 反馈",
  "reconstructive reinforcement learning":"重构式强化学习", "multi-agent critique":"多 Agent 批评", "environment reward":"环境奖励",
  "VLM critique and downstream accuracy":"VLM 批评与下游准确率", "searcher-questioner-solver co-evolution":"搜索器/提问器/求解器共进化",
  "adaptive environment and task synthesis":"自适应环境与任务合成", "flip-centered gating":"以翻转为中心的门控",
  "auditable propose-assess-commit loop":"可审计的提出→评估→提交闭环", "mutual reinforcement":"相互强化", "multi-task exploration reward":"多任务探索奖励",
  "fine-grained critique":"细粒度批评", "verbalized confidence and targeted reflection":"显式置信度与定向反思",
  "standardized cross-episode evaluation":"标准化跨回合评测", "counterfactual interventions":"反事实干预", "tool-grounded self-reward":"工具锚定自奖励",
  "quality supervision and skill balancing":"质量监督与技能平衡", "teacher review and hard verifier":"教师评审与硬验证器"
};
const ZH_CATEGORY = {
  "Paper List":"论文集合", Survey:"综述", Evaluation:"评测", "Scientific Discovery":"科学发现", "Gaming & Strategy":"博弈与策略",
  "Software Engineering":"软件工程", "Foundation Model Improvement":"基础模型改进", "Scaffolding Improvement":"脚手架改进", "Visual & Multimodal":"视觉与多模态",
  Embodied:"具身智能", Environment:"环境", Workflow:"工作流", "Tool & Skill":"工具与技能", "Safety & Verification":"安全与验证",
  "Live literature":"动态文献", "GUI & Web":"GUI / Web", "Web Navigation":"网页导航", "Embodied AI":"具身智能",
  "General Computer Control":"通用计算机控制", "Scaffold-Level":"脚手架级", "Foundation-Model-Level":"基础模型级"
};
const ZH_TAXONOMY = {
  "Evaluation and Benchmarks":"评测与基准",
  "Evidence and execution provenance":"证据与执行溯源",
  "Memory and Context Management":"记忆与上下文管理",
  "2.2.1 Memory Object":"2.2.1 记忆对象",
  "2.2.2 Memory Structure":"2.2.2 记忆结构",
  "2.2.3 Memory Processing":"2.2.3 记忆处理",
  "Versioned evolution protocol":"版本化进化协议",
  "Memory-driven exploration":"记忆驱动探索",
  "Self-evolving memory benchmark":"自进化记忆基准",
  "Visual memory benchmark":"视觉记忆基准",
  "Multi-session memory":"多会话记忆",
  "Action-world memory lifecycle":"动作—世界记忆生命周期",
  "Adaptive multimodal memory":"自适应多模态记忆",
  "Grow-and-refine semantic memory":"生长—修订式语义记忆",
  "Hierarchical video memory":"层级视频记忆",
};
function localizedTaxonomy(value){ const raw=String(value || ""); return language === "zh" ? (ZH_TAXONOMY[raw] || localizedCategory(raw)) : raw; }
function localizedVenue(value){ const raw=String(value || "Unknown venue"); if(language!=="zh") return raw; if(raw==="Paper / technical report") return "论文 / 技术报告"; if(raw==="Repository") return "代码仓库"; return raw; }
function localizedUpdateTarget(value){ const raw=String(value || "agent component"); return language === "zh" ? (ZH_UPDATE_TARGET[raw] || raw) : raw; }
function localizedPublicationType(value){ const raw=String(value || "Other"); return language === "zh" ? (ZH_PUBLICATION_TYPE[raw] || raw) : raw; }
function localizedSignal(value){ const raw=String(value || "feedback"); return language === "zh" ? (ZH_SIGNAL[raw] || raw) : raw; }
function localizedCategory(value){ const raw=String(value || "Unclassified"); return language === "zh" ? (ZH_CATEGORY[raw] || raw) : raw; }
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
function citationCountInfo(record) {
  const snapshotMeta = citationMetadata(record);
  const snapshotValue = Number(snapshotMeta?.citationCount);
  const recordValue = Number(record?.citationCount);
  const hasSnapshot = Number.isFinite(snapshotValue);
  const hasRecord = Number.isFinite(recordValue);
  if (!hasSnapshot && !hasRecord) return {value:null,source:"",matchScore:null};
  if (hasRecord && (!hasSnapshot || recordValue > snapshotValue)) {
    return {value:recordValue,source:String(record?.source || "").includes("semantic-scholar") ? "Semantic Scholar" : "record metadata",matchScore:null};
  }
  return {value:snapshotValue,source:CITATION_CONFIG.sourceName || "OpenAlex snapshot",matchScore:snapshotMeta?.matchScore ?? null};
}
function citationCount(record) { return citationCountInfo(record).value; }
function citationCountSource(record) { return citationCountInfo(record).source; }
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
function mustReadAnchorInfo(record) {
  const key = normalizeTitle(record.title);
  if (!key) return null;
  return (CITATION_CONFIG.mustReadAnchors || []).find((row) => normalizeTitle(row.title) === key) || null;
}
function readingRoleInfo(record) {
  const roles = CITATION_CONFIG.readingRoles || [];
  const findRole = (id) => roles.find((role) => role.id === id) || {id,rank:99,title:{en:id,zh:id},description:{en:"",zh:""}};
  if (mustReadAnchorInfo(record)) return findRole("must-read");
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
  if (roleId === "must-read") {
    return Number(mustReadAnchorInfo(a)?.rank || 999) - Number(mustReadAnchorInfo(b)?.rank || 999) || compareCitationValues(a, b) || publicationTier(a) - publicationTier(b) || a.title.localeCompare(b.title);
  }
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
  node.innerHTML = `<strong>OpenAlex + Semantic Scholar</strong><span>${language === "zh" ? `引用覆盖 ${coverage.matched}/${coverage.total} · OpenAlex 快照更新 ${updated}` : `${coverage.matched}/${coverage.total} citation matches · OpenAlex snapshot updated ${updated}`}</span>`;
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
  const declaredSignal = /semantic scholar retrieval/i.test(String(record.signal || "")) ? "" : (record.signal || "");
  const text = `${declaredSignal} ${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
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
    const existingCitations = Number(existing.citationCount), itemCitations = Number(item.citationCount);
    const mergedCitationCount = Number.isFinite(existingCitations) && Number.isFinite(itemCitations)
      ? Math.max(existingCitations, itemCitations)
      : Number.isFinite(itemCitations) ? itemCitations : Number.isFinite(existingCitations) ? existingCitations : undefined;
    map.set(key, { ...existing, ...item, ...(mergedCitationCount === undefined ? {} : {citationCount:mergedCitationCount}), source: existing.source && item.source ? `${existing.source}+${item.source}` : (item.source || existing.source || "curated") });
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

function projectStatusState(){ return window.CURRENT_RESEARCH_STATUS || {}; }
function canonicalPaperRegistry(){ return window.PAPER_REGISTRY || {}; }
function researchDashboard(){ return window.RESEARCH_DASHBOARD || {summary:{},attention:[],papers:[],week:{highlights:[]}}; }
function canonicalSTRIPaper(){ return (canonicalPaperRegistry().papers||[]).find(row=>row.paper_id==="STRI") || projectStatusState().leading_paper_track || {}; }
function renderProjectStatusStrip(){
  const state=projectStatusState(), h=state.headline||{}, asOf=state.as_of_date||"", paper=canonicalSTRIPaper(), paperSummary=canonicalPaperRegistry().summary||{};
  if(!Object.keys(h).length) return "";
  if(pageId==="research-map" || pageId==="bibliography") return "";
  if(pageId==="research-directions") {
    const labels=language==="zh"
      ? [["最新门禁可提交论文",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??h.paper_ready??0],["正式新问题",h.canonical_live_ideas||0],["可启动实验",h.launchable_formal_experiments||0]]
      : [["latest gate-clean papers",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??h.paper_ready??0],["formal new ideas",h.canonical_live_ideas||0],["launchable experiments",h.launchable_formal_experiments||0]];
    return `<section class="field-current-status-strip" aria-label="${language==="zh"?"当前科研状态":"Current research state"}"><b>${language==="zh"?`当前科研状态${asOf?` · ${asOf}`:""}`:`Current research state${asOf?` · ${asOf}`:""}`}</b><div class="field-current-status-metrics">${labels.map(([label,value])=>`<span><strong>${value}</strong>${label}</span>`).join("")}</div><a href="research-map.html">${language==="zh"?"查看当前研究组合图谱 →":"Open current research map →"}</a></section>`;
  }
  if(pageId==="system-overview") {
    const overviewAsOf=window.RESEARCH_SYSTEM_STATE?.generated_at?.slice?.(0,10)||asOf;
    const acceptance=window.RESEARCH_SYSTEM_STATE?.paper_acceptance||{}, index=acceptance.ledger_index||{}, entries=index.entries||[];
    const stri=entries.find(row=>row.paper_id==="STRI-ICLR2027")||{}, safety=entries.find(row=>row.paper_id==="AGENT-SAFETY-R9")||{};
    const story=stri.latest_story_search||{}, mockModes=stri.mock_pc_modes||{};
    const mockDone=[mockModes.BLIND_MANUSCRIPT,mockModes.ARTIFACT_AWARE].filter(Boolean).length;
    const striHuman=language==="zh"?({PAPER_EVIDENCE:"证据已冻结",PAPER_DESIGN:"故事线设计中",MANUSCRIPT:"成稿中",MOCK_PC:"模拟审稿中",TARGETED_REPAIR:"定向修稿中",CLAIM_AUDIT:"主张审计中",PDF_QA:"PDF 质检中",PREBUTTAL:"预答辩中",SUBMISSION_READY:"已准备投稿",SUBMITTED:"已投稿",REBUTTAL:"答辩中",LEARN:"复盘中"}[stri.current_state]||stri.current_state||"--"):(stri.current_state||"--");
    const safetyHuman=language==="zh"?({PAPER_EVIDENCE:"证据阶段",PAPER_DESIGN:"故事线设计中",MANUSCRIPT:"成稿中",MOCK_PC:"模拟审稿中",TARGETED_REPAIR:"定向修稿中",CLAIM_AUDIT:"主张审计中",PDF_QA:"PDF 质检中",PREBUTTAL:"预答辩中",SUBMISSION_READY:"已准备投稿",SUBMITTED:"已投稿",REBUTTAL:"答辩中",LEARN:"复盘中"}[safety.current_state]||safety.current_state||"--"):(safety.current_state||"--");
    const paperTotal=paperSummary.papers??index.summary?.papers??entries.length, ledgerReadyPapers=paperSummary.submission_ready??acceptance.summary?.submission_ready_papers??index.summary?.submission_ready??0, readyPapers=paperSummary.gate_clean_submission_ready??acceptance.summary?.gate_clean_submission_ready_papers??index.summary?.gate_clean_submission_ready??ledgerReadyPapers, holdPapers=paperSummary.immediate_submission_holds??acceptance.summary?.immediate_submission_holds??index.summary?.immediate_submission_holds??0, repairPapers=paperSummary.by_stage?.TARGETED_REPAIR??index.summary?.by_state?.TARGETED_REPAIR??0;
    const labels=language==="zh"
      ? [[`STRI · ${stri.current_state||"--"}`,striHuman],[`Agent Safety · ${safety.current_state||"--"}`,safetyHuman],["PaperState 总数",paperTotal],["Ledger SUBMISSION_READY",ledgerReadyPapers],["最新门禁可提交",readyPapers],["当前 HOLD",holdPapers]]
      : [["STRI",stri.current_state||"--"],["Agent Safety",safety.current_state||"--"],["PaperStates",paperTotal],["Ledger SUBMISSION_READY",ledgerReadyPapers],["Latest gate-clean",readyPapers],["Current HOLD",holdPapers]];
    const message=language==="zh"
      ? `Canonical Paper Acceptance 当前共有 ${paperTotal} 篇论文。${ledgerReadyPapers} 篇 ledger state 已到 SUBMISSION_READY；最新 readiness gate-clean=${readyPapers}，immediate HOLD=${holdPapers}。状态迁移与后追加复核分开记录，真实 SUBMITTED 继续要求人工投稿权限。`
      : `Canonical Paper Acceptance currently contains ${paperTotal} papers. ${ledgerReadyPapers} ledger states are at SUBMISSION_READY; latest readiness gate-clean=${readyPapers}, with immediate HOLD=${holdPapers}. State transitions and later re-audits remain separate, and real SUBMITTED still requires human submission authority.`;
    return `<section class="project-status-strip current system-overview-status"><div class="project-status-copy"><b>${language==="zh"?`当前科研状态${overviewAsOf?` · ${overviewAsOf}`:""}`:`Current research state${overviewAsOf?` · ${overviewAsOf}`:""}`}</b><span>${message}</span></div><div class="system-overview-status-metrics">${labels.map(([label,value])=>`<span><strong>${value}</strong><small>${label}</small></span>`).join("")}</div></section>`;
  }
  const selectedPaper=pageId==="selected-paper";
  const acceptance=window.RESEARCH_SYSTEM_STATE?.paper_acceptance||{}, acceptanceIndex=acceptance.ledger_index||{}, acceptanceEntry=(acceptanceIndex.entries||[]).find(row=>row.paper_id==="STRI-ICLR2027")||{}, acceptanceSummary=acceptance.summary||acceptanceIndex.summary||{};
  const acceptanceState=paper.paper_stage||paper.current_state||acceptanceEntry.current_state||"PAPER_EVIDENCE", story=paper.latest_story_search||acceptanceEntry.latest_story_search||{}, mockModes=paper.mock_pc_modes||acceptanceEntry.mock_pc_modes||{}, claimAudit=paper.latest_claim_audit||acceptanceEntry.latest_claim_audit||{}, manuscriptCI=paper.latest_manuscript_ci||acceptanceEntry.latest_manuscript_ci||{}, prebuttal=paper.latest_prebuttal||acceptanceEntry.latest_prebuttal||{}, submissionReadiness=paper.latest_submission_readiness||acceptanceEntry.latest_submission_readiness||{};
  const completedMockModes=[mockModes.BLIND_MANUSCRIPT,mockModes.ARTIFACT_AWARE].filter(Boolean).length, canonicalSubmissionReady=acceptanceState==="SUBMISSION_READY"&&paper.submission_ready===true&&submissionReadiness.submission_ready===true&&(paper.gate_clean_submission_ready!==false);
  const message=selectedPaper
    ? (canonicalSubmissionReady
      ? (language==="zh"?`当前选中论文是 STRI：PaperRegistry 与 canonical Paper Acceptance 已一致到 SUBMISSION_READY。Story Search winner=${story.selected_story_id||"--"}，Blind + Artifact-aware Mock PC=${completedMockModes}/2，Claim Audit=${claimAudit.pass?"PASS":"PENDING"}，Manuscript CI=${manuscriptCI.pass?`${manuscriptCI.passed||0}/${manuscriptCI.required||0} PASS`:"PENDING"}，Prebuttal=${prebuttal.pass?"PASS":"PENDING"}。论文侧闭环已完成；下一步只能由人工完成作者责任确认和真实 OpenReview 提交，系统没有 submission authority。`:`The selected paper is STRI: PaperRegistry and canonical Paper Acceptance now agree on SUBMISSION_READY. Story Search winner=${story.selected_story_id||"--"}; Blind + Artifact-aware Mock PC=${completedMockModes}/2; Claim Audit=${claimAudit.pass?"PASS":"PENDING"}; Manuscript CI=${manuscriptCI.pass?`${manuscriptCI.passed||0}/${manuscriptCI.required||0} PASS`:"PENDING"}; Prebuttal=${prebuttal.pass?"PASS":"PENDING"}. The paper-side closure is complete; human author responsibility/signoff and real OpenReview submission still require external authority.`)
      : (language==="zh"?`当前选中论文是 STRI：冻结的 3 条核心主张已有对应证据；canonical Paper Acceptance 当前=${acceptanceState}，Story Search winner=${story.selected_story_id||"--"}，Blind + Artifact-aware Mock PC=${completedMockModes}/2，Claim Audit=${claimAudit.pass?"PASS":"尚未 PASS"}，Submission Ready=${paper.submission_ready?"YES":"NO"}。继续按账本完成剩余论文硬门。`:`The selected paper is STRI: its three frozen claims have evidence; canonical Paper Acceptance=${acceptanceState}, Story Search winner=${story.selected_story_id||"--"}, Blind + Artifact-aware Mock PC=${completedMockModes}/2, Claim Audit=${claimAudit.pass?"PASS":"not yet PASS"}, Submission Ready=${paper.submission_ready?"YES":"NO"}. Continue through the remaining canonical paper gates.`))
    : (language==="zh"?`截至 ${asOf||"当前"}：STRI 的科研证据已进入论文流程，当前 Paper Acceptance 阶段=${acceptanceState}，最新门禁可提交论文=${paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??0}；还缺的旧版论文证据项=${h.paper_quality_evidence_debt||0}。通过正式问题检查、可以继续进入方法设计的新研究问题=${h.canonical_live_ideas||0}；现在允许正式启动的实验=${h.launchable_formal_experiments||0}。以前的记忆效应只保留为历史观察，不会因为论文状态变化而重新授权实验。`:`As of ${asOf||"now"}: STRI has entered the paper workflow; canonical Paper Acceptance=${acceptanceState}, latest gate-clean papers=${paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??0}, legacy paper-evidence debt=${h.paper_quality_evidence_debt||0}. New ideas past the formal problem check=${h.canonical_live_ideas||0}; formal experiments launchable now=${h.launchable_formal_experiments||0}. The earlier memory effect remains historical only and is not re-authorized by changes in paper state.`);
  const statusLabels = selectedPaper
    ? (language === "zh" ? [["Canonical PaperState",acceptanceState],["Story Search winner",story.selected_story_id||"--"],["Mock PC 完成模式",`${completedMockModes}/2`],["Claim Audit",claimAudit.pass?"PASS":"PENDING"],["Manuscript CI",manuscriptCI.pass?`${manuscriptCI.passed||0}/${manuscriptCI.required||0} PASS`:"PENDING"],["Prebuttal",prebuttal.pass?"PASS":"PENDING"],["最新门禁可提交",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??0],["当前 readiness HOLD",paperSummary.immediate_submission_holds??0]] : [["Canonical PaperState",acceptanceState],["Story Search winner",story.selected_story_id||"--"],["Mock PC modes",`${completedMockModes}/2`],["Claim Audit",claimAudit.pass?"PASS":"PENDING"],["Manuscript CI",manuscriptCI.pass?`${manuscriptCI.passed||0}/${manuscriptCI.required||0} PASS`:"PENDING"],["Prebuttal",prebuttal.pass?"PASS":"PENDING"],["Latest gate-clean",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??0],["Current readiness HOLD",paperSummary.immediate_submission_holds??0]])
    : (language === "zh"
      ? [["最新门禁可投稿论文",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??h.paper_ready??0],["还缺的旧版论文证据",h.paper_quality_evidence_debt||0],["通过正式问题检查的新研究问题",h.canonical_live_ideas||0],["正在做最小验证的新现象",h.fresh_active_f0||0],["因缺证据暂缓的新现象",h.fresh_support_holds||0],["现在允许启动的正式实验",h.launchable_formal_experiments||0],["已关闭的精确候选表述",h.shadow_closed_basins||h.shadow_dead_ends||0],["真正关闭到核心原理层",h.shadow_core_principle_stops||0],["整个基准或现象也被判定不成立",h.shadow_broader_core_principle_falsifications||0],["等待具体证据的暂定候选",h.shadow_holds||0]]
      : [["latest gate-clean papers",paperSummary.gate_clean_submission_ready??paperSummary.submission_ready??h.paper_ready??0],["unfinished legacy paper evidence",h.paper_quality_evidence_debt||0],["new ideas past formal problem check",h.canonical_live_ideas||0],["fresh phenomena in minimal validation",h.fresh_active_f0||0],["fresh phenomena waiting for evidence",h.fresh_support_holds||0],["formal experiments launchable now",h.launchable_formal_experiments||0],["closed exact candidate formulations",h.shadow_closed_basins||h.shadow_dead_ends||0],["core-principle scientific closures",h.shadow_core_principle_stops||0],["whole benchmark/phenomenon falsifications",h.shadow_broader_core_principle_falsifications||0],["tentative candidates waiting for evidence",h.shadow_holds||0]]);
  const selectedRegistryPapers=canonicalPaperRegistry().papers||[], selectedSafetyPaper=selectedRegistryPapers.find(row=>row.paper_id==="AGENT-SAFETY-R9")||{};
  const selectedPaperCount=paperSummary.papers??selectedRegistryPapers.length, selectedLedgerReadyCount=paperSummary.submission_ready??0, selectedGateCleanCount=paperSummary.gate_clean_submission_ready??selectedLedgerReadyCount, selectedHoldCount=paperSummary.immediate_submission_holds??0, selectedRepairCount=paperSummary.by_stage?.TARGETED_REPAIR??0;
  const selectedMessage=selectedPaper?(language==="zh"?`PaperRegistry 当前有 ${selectedPaperCount} 篇正式 PaperState。ledger SUBMISSION_READY=${selectedLedgerReadyCount}；最新门禁 clean=${selectedGateCleanCount}；readiness HOLD=${selectedHoldCount}。D2 论文保留 paper-first discovery provenance，真实 SUBMITTED 仍需要人工 OpenReview 提交。`:`PaperRegistry currently contains ${selectedPaperCount} formal PaperStates. Ledger SUBMISSION_READY=${selectedLedgerReadyCount}; latest gates clean=${selectedGateCleanCount}; readiness HOLD=${selectedHoldCount}. D2 papers preserve paper-first discovery provenance, and real SUBMITTED still requires human OpenReview action.`):message;
  const selectedStatusLabels=selectedPaper?(language==="zh"?[["PaperState 总数",selectedPaperCount],["Ledger SUBMISSION_READY",selectedLedgerReadyCount],["最新门禁 clean",selectedGateCleanCount],["Readiness HOLD",selectedHoldCount],["STRI",paper.paper_stage||paper.current_state||"--"],["Agent Safety R9",selectedSafetyPaper.paper_stage||selectedSafetyPaper.current_state||"--"]]:[["PaperStates",selectedPaperCount],["Ledger SUBMISSION_READY",selectedLedgerReadyCount],["Latest gates clean",selectedGateCleanCount],["Readiness HOLD",selectedHoldCount],["STRI",paper.paper_stage||paper.current_state||"--"],["Agent Safety R9",selectedSafetyPaper.paper_stage||selectedSafetyPaper.current_state||"--"]]):statusLabels;
  return `<section class="project-status-strip current"><div class="project-status-copy"><b>${selectedPaper?(language==="zh"?"当前论文 · PaperRegistry":"Current papers · PaperRegistry"):(language==="zh"?`当前科研状态${asOf?` · ${asOf}`:""}`:`Current research state${asOf?` · ${asOf}`:""}`)}</b><span>${selectedMessage}</span></div><dl class="project-status-metrics">${selectedStatusLabels.map(([label,value])=>`<div><dt>${label}</dt><dd>${value}</dd></div>`).join("")}</dl></section>`;
}
function pageHeader(config) {
  return `<div class="eyebrow">${esc(textOf(config.eyebrow))}</div><h1>${textOf(config.title)}</h1><p class="lead">${textOf(config.lead)}</p>${config.callout ? `<div class="callout">${textOf(config.callout)}</div>` : ""}${renderProjectStatusStrip()}`;
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
  const compactTwoRows=pageId==="system-overview";
  const intro=compactTwoRows
    ? (language === "zh" ? "按编号从左到右、从上到下阅读。第一行从研究问题走到小规模验证，第二行从证据冻结走到成稿、投稿与系统复盘；每章的详细问题在下方正文展开。" : "Read by number from left to right and top to bottom. The first row runs from research question to local validation; the second runs from evidence freeze through manuscript, submission, and system learning. Each chapter's full question is expanded below.")
    : (language === "zh" ? "先理解各章解决的主问题，再进入方法族、任务域或具体子问题。箭头表示推荐阅读顺序，不表示严格因果关系。" : "Start with the main question of each chapter, then move to method families, domains, or concrete subproblems. Arrows indicate the recommended reading order rather than strict causality.");
  const separator=compactTwoRows?"":"<i>→</i>";
  return `<section class="panel page-architecture${compactTwoRows?" page-architecture-two-rows":""}"><h2 id="page-framework">${language === "zh" ? "本页框架与阅读顺序" : "Page framework and reading order"}</h2><p class="section-intro">${intro}</p><div class="page-architecture-flow">${chapters.map((chapter, index) => {const rawTitle=textOf(chapter.title);const cardTitle=compactTwoRows&&chapter.navTitle?textOf(chapter.navTitle):(compactTwoRows?rawTitle.replace(language==="zh"?/^第[一二三四五六七八九十0-9]+章\s*[·：]\s*/:/^[IVX]+\s*·\s*/,""):rawTitle);return `<a class="page-architecture-card" href="#chapter-${esc(chapter.id)}"><span>${String(index + 1).padStart(2,"0")}</span><div><b>${cardTitle}</b>${compactTwoRows?"":`<small>${textOf(chapter.question)}</small>`}</div></a>`;}).join(separator)}</div></section>`;
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
function renderFieldAxisSwitcher() {
  if (!new Set(["mechanisms","domains","evaluation"]).has(pageId)) return "";
  const items = [
    ["mechanisms","mechanisms.html",language === "zh" ? "进化机制" : "Mechanisms",language === "zh" ? "怎么改？" : "How does it change?"],
    ["domains","domains.html",language === "zh" ? "应用场景" : "Application domains",language === "zh" ? "在哪里改？" : "Where does it change?"],
    ["evaluation","evaluation.html",language === "zh" ? "评测证据" : "Evaluation evidence",language === "zh" ? "怎么证明？" : "How is it proven?"],
  ];
  return `<nav class="field-axis-switcher" aria-label="${language === "zh" ? "领域图谱三个切面" : "Three field-atlas views"}">${items.map(([id,href,title,question])=>`<a class="${pageId===id?"active":""}" href="${href}"><b>${title}</b><span>${question}</span></a>`).join("")}</nav>`;
}
function renderFieldAxisPrimer() {
  if (pageId === "mechanisms") {
    const rows = language === "zh" ? [
      ["模型参数","SFT / DPO / RL / LoRA","持久；回滚成本高","高","遗忘、奖励投机、更新成本"],
      ["Prompt / Policy","可复用指令、规则、文本策略","版本化容易；回滚简单","低","基准过拟合、上下文膨胀"],
      ["Memory","事实、轨迹、规则、摘要","可编辑、可删除、可重检索","低–中","污染、过期、检索失败"],
      ["Skill / Tool","可执行过程、宏工具、路由规则","可版本化；需要契约","中","不兼容、技能爆炸、权限风险"],
      ["Workflow / Scaffold","控制流、组件组合、路由、评价器","可回滚但组件耦合更强","中–高","归因困难、搜索成本、评价器过拟合"],
    ] : [
      ["Model parameters","SFT / DPO / RL / LoRA","Persistent; expensive to roll back","High","Forgetting, reward hacking, update cost"],
      ["Prompt / policy","Reusable instructions, rules, textual policies","Easy to version and roll back","Low","Benchmark overfit, context bloat"],
      ["Memory","Facts, trajectories, rules, summaries","Editable, deletable, retrievable","Low–medium","Pollution, staleness, retrieval failure"],
      ["Skill / tool","Executable procedures, macro-tools, routing rules","Versionable; needs contracts","Medium","Incompatibility, skill explosion, permission risk"],
      ["Workflow / scaffold","Control flow, composition, routing, evaluators","Rollback possible but highly coupled","Medium–high","Attribution, search cost, evaluator overfit"],
    ];
    const headers = language === "zh" ? ["更新对象","典型写入","持久性 / 回滚","成本","最常见失败"] : ["Update surface","Typical write","Persistence / rollback","Cost","Typical failure"];
    return `<section class="panel field-axis-primer"><div class="eyebrow">${language === "zh" ? "一眼看懂 · 机制切面" : "AT A GLANCE · MECHANISM VIEW"}</div><h2 data-toc="false">${language === "zh" ? "同样叫“自进化”，真正被修改的对象可以完全不同" : "The same self-evolution label can hide very different update surfaces"}</h2><p>${language === "zh" ? "先比较更新对象、可回滚性、成本和失败模式，再进入下方各机制的论文与方法细节。" : "Compare update surface, rollback, cost, and failure mode first; then inspect the detailed method families below."}</p><div class="field-primer-table-wrap"><table class="matrix field-primer-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((cell,i)=>i===0?`<th>${cell}</th>`:`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
  }
  if (pageId === "domains") {
    const rows = language === "zh" ? [
      ["多模态 / 视觉","图像、视频、文本、多模态记忆","生成、检索、视觉工具调用","通常可重复离线评测","中","必须证明改进依赖正确视觉证据，而不只是语言先验"],
      ["GUI / Web","页面状态、截图、DOM、交互历史","点击、输入、导航、工具调用","多数任务可重置，但网站会变化","中–高","需要跨任务/跨会话验证，并区分环境漂移与 Agent 更新"],
      ["具身 / 机器人","传感器、视觉、身体状态、动力学","连续控制、导航、操作","常常只能近似重置","高","必须报告安全、恢复、动力学变化和不可逆动作带来的影响"],
    ] : [
      ["Multimodal / visual","Images, video, text, multimodal memory","Generation, retrieval, visual-tool calls","Usually repeatable offline","Medium","Show that gains rely on the right visual evidence rather than language priors"],
      ["GUI / Web","Page state, screenshots, DOM, interaction history","Clicks, typing, navigation, tool calls","Often resettable, but websites drift","Medium–high","Validate across tasks/sessions and separate environment drift from agent updates"],
      ["Embodied / robotics","Sensors, vision, body state, dynamics","Continuous control, navigation, manipulation","Often only approximately resettable","High","Report safety, recovery, dynamics shift, and effects of irreversible actions"],
    ];
    const headers = language === "zh" ? ["场景","观察","动作","可重置性","错误代价","最关键的证据要求"] : ["Domain","Observation","Action","Resetability","Failure cost","Critical evidence requirement"];
    return `<section class="panel field-axis-primer"><div class="eyebrow">${language === "zh" ? "一眼看懂 · 场景切面" : "AT A GLANCE · DOMAIN VIEW"}</div><h2 data-toc="false">${language === "zh" ? "同一种更新机制，换一个环境，实验结论可能就不再成立" : "The same update mechanism can behave differently after the environment changes"}</h2><p>${language === "zh" ? "场景差异主要来自观察、动作、可重置性和错误代价，因此跨领域迁移不能只比较最终分数。" : "Domain transfer is shaped by observation, action, resetability, and failure cost, so final score alone is not enough."}</p><div class="field-primer-table-wrap"><table class="matrix field-primer-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((cell,i)=>i===0?`<th>${cell}</th>`:`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
  }
  if (pageId === "evaluation") {
    const steps = language === "zh" ? [
      ["01","当前任务","更新后当前任务是否更好？这是起点，不是结论。"],
      ["02","未来收益","在未用于选择更新的后续任务上是否仍然受益？"],
      ["03","旧能力回退","改进新任务时，旧任务和已有能力损失了多少？"],
      ["04","跨回合持久性","变化是否跨 episode / session / version 继续存在？"],
      ["05","负向进化与安全","有多少更新使风险、违规或最坏情况变差？"],
      ["06","回滚与恢复","坏更新能否识别、撤回，并恢复到可接受状态？"],
      ["07","可复现性","别人能否用冻结的数据、环境、版本、日志和统计单位重跑关键结论？"],
    ] : [
      ["01","Current task","Did the updated agent improve the current task? This is the start, not the conclusion."],
      ["02","Future gain","Does the gain survive on later tasks not used to select the update?"],
      ["03","Regression","How much old-task or existing capability is lost while improving the new task?"],
      ["04","Persistence","Does the change survive across episodes, sessions, or committed versions?"],
      ["05","Negative evolution & safety","How often do updates worsen risk, violations, or worst-case behavior?"],
      ["06","Rollback & recovery","Can a bad update be detected, reverted, and returned to an acceptable state?"],
      ["07","Reproducibility","Can another researcher rerun the key result with frozen data, environment, versions, logs, and statistical units?"],
    ];
    return `<section class="panel field-axis-primer"><div class="eyebrow">${language === "zh" ? "一眼看懂 · 证据切面" : "AT A GLANCE · EVIDENCE VIEW"}</div><h2 data-toc="false">${language === "zh" ? "“当前分数更高”只是第一层，完整自进化证据至少要继续往下看" : "A higher current score is only the first layer of self-evolution evidence"}</h2><div class="evolution-evidence-stack">${steps.map(([n,t,d])=>`<div><span>${n}</span><b>${t}</b><p>${d}</p></div>`).join("")}</div></section>`;
  }
  return "";
}
function fieldSourceConfig(sourceId) {
  return (window.CONSOLIDATED_SOURCE_PAGES || {})[sourceId] || window.PAGE_CONTENT?.[sourceId] || null;
}
function renderFieldSourceSections(sourceId) {
  const config = fieldSourceConfig(sourceId);
  if (!config) return "";
  const sections = (config.sections || []).map((section,index) => {
    const citations = PAGE_CITATIONS[sourceId]?.[index] || [];
    const referenceNote = citations.length ? `<div class="section-reference-note"><span>${language === "zh" ? "代表文献" : "Representative references"}</span><span data-cite="${esc(citations.join("||"))}"></span></div>` : "";
    return `<section class="field-source-section"><h4 data-toc="false">${textOf(section.title)}</h4>${section.intro ? `<p class="section-intro">${textOf(section.intro)}</p>` : ""}<div class="section-body">${textOf(section.body)}${referenceNote}</div></section>`;
  }).join("");
  return `<div class="field-source-intro">${config.lead ? `<p>${textOf(config.lead)}</p>` : ""}${config.callout ? `<div class="field-source-callout">${textOf(config.callout)}</div>` : ""}</div>${sections}`;
}
function renderFieldDenseDetail(item, index) {
  const columns=(item.columns||[]).map(([label,value])=>`<span><small>${label}</small><b>${value}</b></span>`).join("");
  return `<details class="field-dense-detail" id="${esc(item.anchor)}"><summary><em>${String(index+1).padStart(2,"0")}</em><div><b>${item.title}</b><small>${item.subtitle}</small></div><div class="field-detail-summary-cols">${columns}</div></summary><div class="field-dense-detail-body">${renderFieldSourceSections(item.sourceId)}</div></details>`;
}
function renderFieldAtlasBridge(active="matrix") {
  return `<nav class="field-atlas-bridge" aria-label="${language === "zh" ? "领域图谱入口" : "Field atlas navigation"}"><a class="${active==="definition"?"active":""}" href="foundations.html"><span>01</span><div><b>${language === "zh" ? "定义与边界 · 什么是 Agent 自进化" : "Definition & boundary · what is self-evolution?"}</b><small>${language === "zh" ? "先区分持久学习与重试、自纠错、临时上下文" : "Separate persistent learning from retrying and temporary adaptation"}</small></div></a><a class="${active==="landscape"?"active":""}" href="research-directions.html"><span>02</span><div><b>${language === "zh" ? "领域全景 · 历史与问题" : "Field landscape · history & problems"}</b><small>${language === "zh" ? "领域怎么形成，D1–D10 在问什么" : "How the field formed and what D1–D10 asks"}</small></div></a><a class="${active==="matrix"?"active":""}" href="mechanisms.html"><span>03</span><div><b>${language === "zh" ? "领域矩阵 · 机制 × 场景 × 评测" : "Field matrix · mechanism × domain × evidence"}</b><small>${language === "zh" ? "改什么、在哪里改、怎么证明" : "What changes, where, and how it is proven"}</small></div></a></nav>`;
}
function renderFieldCrossMatrix() {
  const headers = language === "zh" ? ["更新对象","持久产物","回滚 / 成本","场景敏感点","最少要补的纵向证据","典型风险"] : ["Update surface","Persistent artifact","Rollback / cost","Domain sensitivity","Minimum longitudinal evidence","Typical risk"];
  const rows = language === "zh" ? [
    ["模型参数","权重 / Adapter","回滚重；高成本","数据分布、动作反馈质量","未来任务 + 旧能力回退 + 等预算基线","遗忘、奖励投机、难归因"],
    ["Prompt / Policy","版本化指令 / 文本策略","回滚易；低成本","上下文与工具描述漂移","留出任务 + 等预算推理搜索","基准过拟合、上下文膨胀"],
    ["Memory","事实 / 轨迹 / 规则 / 摘要","可编辑；低–中成本","可观测性、检索条件、时间漂移","跨回合复用 + 污染/过期测试","错误写入、过期、检索失败"],
    ["Skill / Tool","可执行过程 / 宏工具 / 路由规则","可版本化；中成本","动作空间、权限、接口稳定性","跨任务复用 + 契约 / 回退测试","不兼容、技能爆炸、权限风险"],
    ["Workflow / Scaffold","控制流 / 组件组合 / 评价器","可回滚但耦合强；中–高成本","环境状态、组件接口、评价器可靠性","未来收益 + 组件消融 + evaluator audit","搜索成本、归因困难、评价器过拟合"],
  ] : [
    ["Model parameters","Weights / adapters","Hard rollback; high cost","Data distribution and action-feedback quality","Future tasks + regression + matched-budget baseline","Forgetting, reward hacking, weak attribution"],
    ["Prompt / policy","Versioned instructions / textual policy","Easy rollback; low cost","Context and tool-description drift","Held-out tasks + matched-budget inference search","Benchmark overfit, context bloat"],
    ["Memory","Facts / trajectories / rules / summaries","Editable; low–medium cost","Observability, retrieval conditions, temporal drift","Cross-episode reuse + pollution/staleness tests","Bad writes, staleness, retrieval failure"],
    ["Skill / tool","Executable procedures / macro-tools / routing rules","Versionable; medium cost","Action space, permissions, interface stability","Cross-task reuse + contract / rollback tests","Incompatibility, skill explosion, permission risk"],
    ["Workflow / scaffold","Control flow / composition / evaluators","Rollback possible but coupled; medium–high cost","Environment state, component interfaces, evaluator reliability","Future gain + component ablation + evaluator audit","Search cost, attribution, evaluator overfit"],
  ];
  return `<section class="panel field-cross-matrix"><div class="field-matrix-title"><div><div class="eyebrow">${language === "zh" ? "先看这一张表" : "START WITH ONE TABLE"}</div><h2 data-toc="false">${language === "zh" ? "同一种“自进化”主张，必须同时回答三个维度" : "Every self-evolution claim must resolve three dimensions together"}</h2></div><div class="field-tuple"><span>${language === "zh" ? "更新对象" : "update"}</span><i>×</i><span>${language === "zh" ? "环境约束" : "environment"}</span><i>×</i><span>${language === "zh" ? "证据标准" : "evidence"}</span></div></div><div class="field-primer-table-wrap"><table class="matrix field-primer-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((cell,i)=>i===0?`<th>${cell}</th>`:`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div></section>`;
}
function renderUnifiedMechanismAxis(chapter,index) {
  const items = language === "zh" ? [
    {anchor:"field-model-parameters",sourceId:"model-improvement",title:"模型参数",subtitle:"SFT / DPO / RL / LoRA：真正改变基础策略",columns:[["成本","高"],["回滚","重"],["最常见失败","遗忘 / reward hacking"]]},
    {anchor:"field-prompt-policy",sourceId:"prompt-evolution",title:"Prompt / Policy",subtitle:"把反馈写成下一版本可复用指令或文本策略",columns:[["成本","低"],["回滚","易"],["最常见失败","过拟合 / context bloat"]]},
    {anchor:"field-memory",sourceId:"memory-evolution",title:"Memory",subtitle:"把经验变成可写、可检索、可修订的持久状态",columns:[["成本","低–中"],["回滚","易"],["最常见失败","污染 / 过期 / 检索错"]]},
    {anchor:"field-skill-tool",sourceId:"tool-evolution",title:"Skill / Tool",subtitle:"把过程知识变成跨任务可复用的可执行能力",columns:[["成本","中"],["回滚","中"],["最常见失败","不兼容 / 权限风险"]]},
    {anchor:"field-workflow",sourceId:"workflow-evolution",title:"Workflow / Scaffold",subtitle:"修改路由、控制流、组件组合与 evaluator",columns:[["成本","中–高"],["回滚","可行但耦合"],["最常见失败","归因 / evaluator 过拟合"]]},
  ] : [
    {anchor:"field-model-parameters",sourceId:"model-improvement",title:"Model parameters",subtitle:"SFT / DPO / RL / LoRA: change the underlying policy",columns:[["Cost","High"],["Rollback","Hard"],["Failure","Forgetting / reward hacking"]]},
    {anchor:"field-prompt-policy",sourceId:"prompt-evolution",title:"Prompt / policy",subtitle:"Write feedback into the next reusable textual policy",columns:[["Cost","Low"],["Rollback","Easy"],["Failure","Overfit / context bloat"]]},
    {anchor:"field-memory",sourceId:"memory-evolution",title:"Memory",subtitle:"Turn experience into writable, retrievable, revisable persistent state",columns:[["Cost","Low–medium"],["Rollback","Easy"],["Failure","Pollution / staleness / retrieval"]]},
    {anchor:"field-skill-tool",sourceId:"tool-evolution",title:"Skill / tool",subtitle:"Turn procedural knowledge into reusable executable capability",columns:[["Cost","Medium"],["Rollback","Medium"],["Failure","Incompatibility / permission risk"]]},
    {anchor:"field-workflow",sourceId:"workflow-evolution",title:"Workflow / scaffold",subtitle:"Change routing, control flow, composition, and evaluators",columns:[["Cost","Medium–high"],["Rollback","Coupled"],["Failure","Attribution / evaluator overfit"]]},
  ];
  return `<section class="page-chapter field-matrix-chapter" data-chapter="${esc(chapter.id)}"><header class="field-matrix-chapter-head"><span>${String(index+1).padStart(2,"0")}</span><div><h2 id="chapter-${esc(chapter.id)}">${textOf(chapter.title)}</h2><p>${textOf(chapter.question)}</p></div></header><div class="field-dense-list">${items.map(renderFieldDenseDetail).join("")}</div></section>`;
}
function renderUnifiedDomainAxis(chapter,index) {
  const headers = language === "zh" ? ["场景","观察","动作","重置","错误代价","最关键证据"] : ["Domain","Observation","Action","Reset","Failure cost","Critical evidence"];
  const rows = language === "zh" ? [
    ["多模态 / 视觉","图像、视频、文本、多模态记忆","生成、检索、视觉工具调用","通常可离线重复","中","证明改进依赖正确视觉证据，而不是语言先验"],
    ["GUI / Web","页面状态、截图、DOM、交互历史","点击、输入、导航、工具调用","多数可重置，但网站会漂移","中–高","跨任务 / 跨会话验证，并分离环境漂移与 Agent 更新"],
    ["具身 / 机器人","传感器、视觉、身体状态、动力学","连续控制、导航、操作","常只能近似重置","高","安全、恢复、动力学变化和不可逆动作必须单独报告"],
  ] : [
    ["Multimodal / visual","Images, video, text, multimodal memory","Generation, retrieval, visual-tool calls","Usually repeatable offline","Medium","Show reliance on correct visual evidence, not language priors"],
    ["GUI / Web","Page state, screenshots, DOM, interaction history","Clicks, typing, navigation, tool calls","Often resettable, websites drift","Medium–high","Cross-task/session tests; separate environment drift from agent updates"],
    ["Embodied / robotics","Sensors, vision, body state, dynamics","Continuous control, navigation, manipulation","Often only approximately resettable","High","Report safety, recovery, dynamics shift, and irreversible actions separately"],
  ];
  const items = language === "zh" ? [
    {anchor:"field-multimodal",sourceId:"visual-multimodal",title:"多模态 / 视觉",subtitle:"离线可复现更容易，但必须证明视觉证据真的驱动更新",columns:[["重置","较容易"],["动作风险","中"],["关键混杂","语言先验"]]},
    {anchor:"field-gui-web",sourceId:"gui-web",title:"GUI / Web",subtitle:"页面可部分重置，但网站漂移和长轨迹让因果归因更难",columns:[["重置","中"],["动作风险","中–高"],["关键混杂","环境漂移"]]},
    {anchor:"field-embodied",sourceId:"embodied-world",title:"具身 / 机器人",subtitle:"动作不可逆、动力学变化和安全代价让评测要求最高",columns:[["重置","弱"],["动作风险","高"],["关键混杂","动力学 / 恢复"]]},
  ] : [
    {anchor:"field-multimodal",sourceId:"visual-multimodal",title:"Multimodal / visual",subtitle:"Offline repetition is easier, but visual evidence must actually drive the update",columns:[["Reset","Easier"],["Risk","Medium"],["Confound","Language prior"]]},
    {anchor:"field-gui-web",sourceId:"gui-web",title:"GUI / Web",subtitle:"Partly resettable, but website drift and long trajectories complicate attribution",columns:[["Reset","Medium"],["Risk","Medium–high"],["Confound","Environment drift"]]},
    {anchor:"field-embodied",sourceId:"embodied-world",title:"Embodied / robotics",subtitle:"Irreversibility, dynamics, and safety impose the strongest evidence burden",columns:[["Reset","Weak"],["Risk","High"],["Confound","Dynamics / recovery"]]},
  ];
  return `<section class="page-chapter field-matrix-chapter" data-chapter="${esc(chapter.id)}"><header class="field-matrix-chapter-head"><span>${String(index+1).padStart(2,"0")}</span><div><h2 id="chapter-${esc(chapter.id)}">${textOf(chapter.title)}</h2><p>${textOf(chapter.question)}</p></div></header><div class="field-primer-table-wrap field-domain-table"><table class="matrix field-primer-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((cell,i)=>i===0?`<th>${cell}</th>`:`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div><div class="field-dense-list">${items.map(renderFieldDenseDetail).join("")}</div></section>`;
}
function renderUnifiedEvidenceAxis(chapter,index) {
  const steps = language === "zh" ? [
    ["01","当前任务","先确认更新后当前任务确实更好"],
    ["02","未来收益","在未用于选更新的后续任务上仍受益"],
    ["03","旧能力回退","新能力提升没有靠牺牲旧能力换来"],
    ["04","跨回合持久性","变化跨 episode / session / version 仍存在"],
    ["05","负向进化与安全","统计有害更新、违规和最坏情况"],
    ["06","回滚与恢复","坏更新可识别、撤回并恢复"],
    ["07","可复现性","冻结数据、环境、版本、日志和统计单位可重跑"],
  ] : [
    ["01","Current task","Confirm the updated agent really improves the current task"],
    ["02","Future gain","Gain survives on later tasks not used for update selection"],
    ["03","Regression","New capability is not bought by destroying old capability"],
    ["04","Persistence","Change survives across episodes, sessions, or versions"],
    ["05","Negative evolution & safety","Count harmful updates, violations, and worst cases"],
    ["06","Rollback & recovery","Bad updates can be detected, reverted, and recovered"],
    ["07","Reproducibility","Frozen data, environment, versions, logs, and units reproduce the result"],
  ];
  const resources = language === "zh" ? [
    ["评测 / 安全原则","evaluation-safety","future gain regression safety rollback"],
    ["Benchmark / 数据 / 环境","datasets-benchmarks","benchmark dataset environment longitudinal"],
    ["代码 / 复现资产","repositories","repository code reproducibility"],
  ] : [
    ["Evaluation / safety principles","evaluation-safety","future gain regression safety rollback"],
    ["Benchmarks / data / environments","datasets-benchmarks","benchmark dataset environment longitudinal"],
    ["Code / reproduction assets","repositories","repository code reproducibility"],
  ];
  const resourceDetails = resources.map(([title,sourceId,q],i)=>`<details class="field-evidence-resource" id="field-${esc(sourceId)}"><summary><span>${String(i+1).padStart(2,"0")}</span><b>${title}</b><a href="bibliography.html?q=${encodeURIComponent(q)}">${language === "zh" ? "去文献库筛选 →" : "Filter in bibliography →"}</a></summary><div>${renderFieldSourceSections(sourceId)}</div></details>`).join("");
  return `<section class="page-chapter field-matrix-chapter" data-chapter="${esc(chapter.id)}"><header class="field-matrix-chapter-head"><span>${String(index+1).padStart(2,"0")}</span><div><h2 id="chapter-${esc(chapter.id)}">${textOf(chapter.title)}</h2><p>${textOf(chapter.question)}</p></div></header><div class="evolution-evidence-stack field-evidence-stack">${steps.map(([n,t,d])=>`<div><span>${n}</span><b>${t}</b><p>${d}</p></div>`).join("")}</div><div class="field-resource-note"><b>${language === "zh" ? "为什么这里不再列 160 张资源卡？" : "Why are 160 resource cards no longer duplicated here?"}</b><span>${language === "zh" ? "领域图谱负责解释“该测什么、为什么测”；具体 benchmark、dataset、environment 和 repository 统一由文献库负责检索、排序和跳转。" : "The field atlas explains what to measure and why. Concrete benchmarks, datasets, environments, and repositories belong in the searchable bibliography."}</span></div><div class="field-evidence-resources">${resourceDetails}</div></section>`;
}
function renderFieldMatrixHub(config) {
  const chapters = pageArchitecture("mechanisms").chapters || [];
  const header = `<div class="field-matrix-page-header"><div class="eyebrow">${textOf(config.eyebrow)}</div><h1>${textOf(config.title)}</h1><p class="lead">${textOf(config.lead)}</p>${config.callout?`<div class="field-matrix-callout">${textOf(config.callout)}</div>`:""}</div>`;
  return `${header}${renderFieldAtlasBridge("matrix")}${renderFieldCrossMatrix()}${renderUnifiedMechanismAxis(chapters[0],0)}${renderUnifiedDomainAxis(chapters[1],1)}${renderUnifiedEvidenceAxis(chapters[2],2)}`;
}
function renderMergedHub(config) {
  const chapters = config.chapters || [];
  const fallbackOverview = !chapters.some((chapter) => chapter.includeOverview) && config.overviewFigure ? renderOverviewFigure(config) : "";
  const fieldBridge = pageId === "foundations" ? renderFieldAtlasBridge("definition") : "";
  return `${pageHeader(config)}${fieldBridge}${renderFieldAxisSwitcher()}${renderFieldAxisPrimer()}${renderArchitectureOverview()}${fallbackOverview}${chapters.map((chapter, index) => renderPageChapter(chapter, index, config)).join("")}`;
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
const HISTORICAL_TO_CURRENT_CATEGORIES = {
  D1:["A","B","D"], D2:["B"], D3:["E","G"], D4:["A","E"], D5:["F"],
  D6:["C","G"], D7:["A","G"], D8:["A","D","G"], D9:["B","C","D"], D10:["A","B"]
};
const HISTORICAL_DIRECTION_ANCHORS = {
  D1:"experience-admission",D2:"memory-lifecycle",D3:"skill-tool-lifecycle",D4:"system-composition",D5:"embodied-world",
  D6:"negative-evaluation",D7:"security-provenance",D8:"governance-control",D9:"adaptive-objectives",D10:"collective-evolution"
};
function canonicalResearchState(){ return window.RESEARCH_ITEM_STATE || {research_items:[],summary:{},categories:[]}; }
function directionByCode(code){ return portfolioDirections().find(direction=>String(direction.code||"").toUpperCase()===String(code||"").toUpperCase()); }
function currentCategoriesForDirection(direction){ return HISTORICAL_TO_CURRENT_CATEGORIES[String(direction?.code||"").toUpperCase()] || []; }
function historicalDirectionsForCategory(category){ return Object.entries(HISTORICAL_TO_CURRENT_CATEGORIES).filter(([,categories])=>categories.includes(category)).map(([code])=>code); }
function canonicalCategorySnapshot(category){
  const state=canonicalResearchState(), items=(state.research_items||[]).filter(row=>row.category===category), summary=state.summary?.by_category?.[category]||{};
  const counts=items.reduce((acc,row)=>(acc[row.scientific_state]=(acc[row.scientific_state]||0)+1,acc),{});
  return {items,total:Number(summary.portfolio_total||items.length),counts};
}
function renderDirectionCurrentBridge(direction){
  const categories=currentCategoriesForDirection(direction);
  if(!categories.length)return "";
  const cards=categories.map(category=>{const snap=canonicalCategorySnapshot(category);const active=snap.items.filter(row=>["HOLD","PAPER_READY"].includes(row.scientific_state)).slice(0,4);const labels=active.map(row=>`${row.code} · ${row.scientific_state}`).join(" · ") || (language==="zh"?"当前无 HOLD / PAPER_READY 主线":"no current HOLD / PAPER_READY line");return `<a class="direction-current-category" href="research-map.html#research-map-${category.toLowerCase()}"><span>${category}</span><div><b>${language==="zh"?`当前 ${category} 类 · ${snap.total} 个对象`:`Current ${category} · ${snap.total} objects`}</b><small>${esc(labels)}</small></div></a>`;}).join("");
  return `<section class="direction-current-bridge"><header><b>${language==="zh"?"今天落到哪些 canonical ResearchItem":"Current canonical ResearchItem landing"}</b><a href="paper-ideas.html">${language==="zh"?"打开 Research Portfolio →":"Open Research Portfolio →"}</a></header><div>${cards}</div></section>`;
}
function renderResearchItemFieldLineage(code){
  const category=String(code||"").split("-",1)[0], historical=historicalDirectionsForCategory(category);
  if(!category||!historical.length)return "";
  const historyLinks=historical.map(dcode=>{const direction=directionByCode(dcode),anchor=direction?.id||HISTORICAL_DIRECTION_ANCHORS[dcode];return anchor?`<a href="research-directions.html#${esc(anchor)}">${esc(dcode)}</a>`:`<span>${esc(dcode)}</span>`;}).join("");
  return `<nav class="research-item-field-lineage" aria-label="${language==="zh"?"ResearchItem 领域与时间线导航":"ResearchItem field and timeline navigation"}"><span><b>${language==="zh"?"领域谱系":"Field lineage"}</b>${historyLinks}</span><a href="research-map.html#research-map-${category.toLowerCase()}">${language==="zh"?`${category} 类全景`:`${category} landscape`}</a><a href="research-timeline.html?research=${encodeURIComponent(code)}">${language==="zh"?"完整时间线 →":"Full timeline →"}</a></nav>`;
}
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
  return `<article class="direction-card" style="--direction-color:${esc(direction.color || "#5b5bd6")}"><div class="direction-card-head"><span class="direction-code">${esc(direction.code)}</span><span class="direction-count">${directionIdeas.length} ${language === "zh" ? "个历史 Idea" : "historical ideas"}</span></div><h4 id="${esc(direction.id)}">${textOf(direction.title)}</h4><p class="direction-question">${textOf(direction.question)}</p><div class="direction-plain"><b>${language === "zh" ? "通俗理解" : "In plain language"}</b><span>${textOf(detail.plain)}</span></div><div class="direction-explanation-grid"><div><b>${language === "zh" ? "主要研究对象" : "Main object"}</b><p>${textOf(detail.object)}</p></div><div><b>${language === "zh" ? "典型例子" : "Typical example"}</b><p>${textOf(detail.example)}</p></div><div><b>${language === "zh" ? "与邻近方向的区别" : "Difference from neighbors"}</b><p>${textOf(detail.distinction)}</p></div><div><b>${language === "zh" ? "科学边界" : "Scientific boundary"}</b><p>${textOf(direction.boundary)}</p></div></div>${renderDirectionCurrentBridge(direction)}${renderDirectionLiterature(direction)}<div class="idea-chip-list" aria-label="historical idea lineage">${directionIdeas.map((idea) => `<span class="idea-chip" title="${language === "zh" ? "历史候选谱系，不代表当前合同" : "Historical candidate lineage; not a current contract"}"><span>#${idea.rank}</span>${esc(idea.name)}</span>`).join("")}</div></article>`;
}
function renderHistoricalDirectionMigration() {
  const rows = [
    ["D1",language==="zh"?"经验获取、准入与适用范围":"Experience acquisition, admission, and scope","A + B + D",language==="zh"?"准入/回归进入 A；经验价值、适用边界进入 B；把失败/边界经验转成下一批训练任务的部分进入 D。":"Admission/regression moves to A; experience value and applicability move to B; turning failure/boundary experience into later training tasks contributes to D."],
    ["D2",language==="zh"?"记忆表示、修复与巩固":"Memory representation, repair, and consolidation","B",language==="zh"?"成为当前“记忆、经验与持久知识”的主体。":"Becomes the core of current memory/experience research."],
    ["D3",language==="zh"?"技能、工具与权限生命周期":"Skill, tool, and permission lifecycle","E + G",language==="zh"?"技能/工具结构演化进入 E；权限与风险部分进入 G。":"Skill/tool structural evolution moves to E; permission/risk aspects move to G."],
    ["D4",language==="zh"?"更新路由、语义契约与组合":"Update routing, contracts, and composition","A + E",language==="zh"?"更新冲突和回归控制进入 A；工作流/结构契约进入 E。":"Update interaction/regression moves to A; workflow and structural contracts move to E."],
    ["D5",language==="zh"?"具身、探索与世界适应":"Embodiment, exploration, and world adaptation","F",language==="zh"?"直接沉淀为世界模型与具身适应。":"Maps directly into world-model and embodied adaptation."],
    ["D6",language==="zh"?"负向进化评测与基准科学":"Negative evolution evaluation and benchmark science","C + G",language==="zh"?"评价器偏差进入 C；长期负向安全结果进入 G。":"Evaluator bias moves to C; longitudinal safety failures move to G."],
    ["D7",language==="zh"?"安全、溯源与风险传播":"Security, provenance, and risk propagation","A + G",language==="zh"?"更新链审计成为 A 的系统规则；未来风险主线进入 G。":"Update-chain auditing feeds A; future-risk science moves to G."],
    ["D8",language==="zh"?"成本、监督与元控制":"Cost, oversight, and meta-control","A + D + G",language==="zh"?"更新预算/停止规则进入 A；课程选择和难度调度的元控制进入 D；安全监督与权限升级进入 G。":"Update budgets/stopping move to A; curriculum selection and difficulty scheduling contribute to D; safety oversight and escalation move to G."],
    ["D9",language==="zh"?"目标、个性化与内生反馈":"Goals, personalization, and performative feedback","B + C + D · sparse",language==="zh"?"个性化记忆进入 B、反馈漂移进入 C；目标条件下的任务生成与课程漂移进入 D，但当前覆盖仍较少。":"Personalized memory maps to B, feedback drift to C, and goal-conditioned task generation/curriculum drift contributes to D, where current coverage remains thin."],
    ["D10",language==="zh"?"跨 Agent 迁移与复数谱系":"Cross-agent transfer and plural lineages","A + B · sparse",language==="zh"?"迁移可靠性进入 A/B；当前没有独立主线持续推进。":"Transfer reliability maps to A/B; no standalone current line is advancing."],
  ];
  const currentCell = (rawCategories) => String(rawCategories).replace(/ · sparse/g,"").split("+").map(x=>x.trim()).filter(x=>/^[A-G]$/.test(x)).map(category=>{const snap=canonicalCategorySnapshot(category);return `<a class="taxonomy-current-link" href="paper-ideas.html#canonical-group-${category.toLowerCase()}"><b>${category}</b><span>${snap.total} ${language==="zh"?"个对象":"objects"}</span></a>`;}).join("");
  return `<section class="panel historical-taxonomy-migration"><div class="idea-panel-heading"><div><div class="eyebrow">${language==="zh"?"历史分类迁移":"TAXONOMY MIGRATION"}</div><h2 id="historical-to-current-taxonomy">${language==="zh"?"旧 D1–D10 没有废弃：它们被重新编译进当前 A–G":"D1–D10 was not discarded; it was recompiled into current A–G"}</h2><p class="section-intro">${language==="zh"?"这是多对多迁移，不是简单改名。现在表里的 A–G 不是静态文字，而是直接读取 canonical ResearchItemState 的对象数，并可跳到对应 Research Portfolio。":"This is a many-to-many migration, not a rename. The A–G cells now read canonical ResearchItemState counts and link directly to the corresponding Research Portfolio category."}</p></div><a class="link-btn" href="research-map.html">${language==="zh"?"打开当前研究组合图谱 →":"Open Current Research Map →"}</a></div><div class="history-table-scroll"><table class="matrix"><thead><tr><th>${language==="zh"?"历史方向":"Historical"}</th><th>${language==="zh"?"原问题":"Former problem"}</th><th>${language==="zh"?"当前 canonical 落点":"Current canonical landing"}</th><th>${language==="zh"?"迁移说明":"Migration"}</th></tr></thead><tbody>${rows.map(row=>`<tr><th><a href="#${esc(directionByCode(row[0])?.id||"")}">${esc(row[0])}</a></th><td>${esc(row[1])}</td><td><div class="taxonomy-current-links">${currentCell(row[2])}</div></td><td>${esc(row[3])}</td></tr>`).join("")}</tbody></table></div></section>`;
}
function renderCompactFieldHistory() {
  const data=historyFigureData();
  if(!data?.stages?.length)return "";
  const cards=data.stages.map(stage=>`<article class="field-history-stage" style="--stage:${esc(stage.color||"#456")}"><header><span>${esc(stage.code)}</span><b>${esc(stage.period)}</b></header><h3 data-toc="false">${textOf(stage.title)}</h3><p>${textOf(stage.subtitle)}</p><dl><div><dt>${language==="zh"?"更新对象":"Update"}</dt><dd>${textOf(stage.target)}</dd></div><div><dt>${language==="zh"?"反馈":"Feedback"}</dt><dd>${textOf(stage.feedback)}</dd></div></dl></article>`).join("");
  return `<section class="field-history-spine"><div class="field-compact-heading"><div><div class="eyebrow">${language==="zh"?"六阶段主线":"SIX-STAGE SPINE"}</div><h2 data-toc="false">${language==="zh"?"更新对象从局部改写扩展到系统级持续进化":"Update surfaces expanded from local rewriting to system-level evolution"}</h2></div><p>${language==="zh"?"这里只保留理解领域最需要的时间、更新对象和反馈变化；完整历史图放到下方审计折叠层。":"Keep only the time, update target, and feedback shifts needed for orientation; the full history figure remains in the audit fold below."}</p></div><div class="field-history-stage-grid">${cards}</div></section>`;
}
function renderDirectionAtlasTable(directions) {
  const rows=directions.map(direction=>{
    const detail=directionGuide(direction.id), categories=currentCategoriesForDirection(direction);
    const current=categories.map(category=>{const snap=canonicalCategorySnapshot(category);return `<a href="research-map.html#research-map-${category.toLowerCase()}"><b>${category}</b><small>${snap.total}</small></a>`;}).join("") || "—";
    const papers=directionLiterature(direction.id).slice(0,2).map(p=>`<a href="${directionPaperHref(p.title)}">${esc(p.short||p.title)}<small>${esc(String(p.year||""))}</small></a>`).join("") || "—";
    return `<tr><th><a href="#${esc(direction.id)}">${esc(direction.code)}</a></th><td><b>${textOf(direction.title)}</b><span>${textOf(direction.question)}</span></td><td>${textOf(detail.plain)}</td><td>${textOf(detail.example)}</td><td><div class="direction-table-current">${current}</div></td><td><div class="direction-table-papers">${papers}</div></td></tr>`;
  }).join("");
  return `<section class="panel direction-atlas-table-panel"><div class="field-compact-heading"><div><div class="eyebrow">D1–D10</div><h2 data-toc="false">${language==="zh"?"先横向比较十个问题，再决定要不要展开某个方向":"Compare all ten problems first, then open only the direction you need"}</h2></div><p>${language==="zh"?"总表直接回答“研究什么、通俗怎么理解、典型例子、今天落到 A–G 哪里、先读哪两篇论文”。":"The table answers what each direction studies, its plain meaning, a concrete example, its current A–G landing, and two papers to read first."}</p></div><div class="history-table-scroll"><table class="matrix direction-atlas-table"><thead><tr><th>ID</th><th>${language==="zh"?"问题":"Problem"}</th><th>${language==="zh"?"通俗理解":"Plain meaning"}</th><th>${language==="zh"?"典型例子":"Example"}</th><th>${language==="zh"?"当前 A–G":"Current A–G"}</th><th>${language==="zh"?"代表论文":"Papers"}</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}
function renderDirectionDetailFold(direction,index) {
  const directionIdeas=direction.ideaIds.map(ideaByName).filter(Boolean).sort((a,b)=>a.rank-b.rank), detail=directionGuide(direction.id), papers=directionLiterature(direction.id);
  const categories=currentCategoriesForDirection(direction).join(" · ") || "—";
  return `<details class="direction-atlas-detail" id="${esc(direction.id)}"><summary><span>${esc(direction.code)}</span><div><b>${textOf(direction.title)}</b><small>${textOf(detail.plain)}</small></div><em>${esc(categories)} · ${papers.length} ${language==="zh"?"篇代表论文":"papers"}</em></summary><div class="direction-atlas-detail-body"><div class="direction-explanation-grid"><div><b>${language === "zh" ? "主要研究对象" : "Main object"}</b><p>${textOf(detail.object)}</p></div><div><b>${language === "zh" ? "典型例子" : "Typical example"}</b><p>${textOf(detail.example)}</p></div><div><b>${language === "zh" ? "与邻近方向的区别" : "Difference from neighbors"}</b><p>${textOf(detail.distinction)}</p></div><div><b>${language === "zh" ? "科学边界" : "Scientific boundary"}</b><p>${textOf(direction.boundary)}</p></div></div>${renderDirectionCurrentBridge(direction)}${renderDirectionLiterature(direction)}<div class="idea-chip-list" aria-label="historical idea lineage">${directionIdeas.map(idea=>`<span class="idea-chip" title="${language==="zh"?"历史候选谱系，不代表当前合同":"Historical candidate lineage; not a current contract"}"><span>#${idea.rank}</span>${esc(idea.name)}</span>`).join("")}</div></div></details>`;
}
function renderDirectionMap(config) {
  const directions=portfolioDirections(), ideas=portfolioIdeas(), guide=directionGuideData(), chapters=pageArchitecture("research-directions").chapters||[];
  const macroCards=(guide.macroGroups||[]).map(group=>`<article class="direction-macro-card"><span>${esc(group.code)}</span><h3 data-toc="false">${textOf(group.title)}</h3><p>${textOf(group.plain)}</p><div>${(group.directionIds||[]).map(id=>{const direction=directionById(id);return direction?`<a href="#${esc(id)}">${esc(direction.code)} · ${textOf(direction.title)}</a>`:"";}).join("")}</div></article>`).join("");
  const stats=`<div class="field-landscape-stats"><span><b>${directions.length}</b>${language==="zh"?"个历史问题方向":"historical directions"}</span><span><b>${ideas.length}</b>${language==="zh"?"个历史 Idea formulation":"historical idea formulations"}</span><span><b>${portfolioTracks().length}</b>${language==="zh"?"类历史论文赛道":"historical paper tracks"}</span></div>`;
  const orientation=`${renderFieldAtlasBridge("landscape")}${renderCompactFieldHistory()}${stats}<section class="direction-primer"><div class="field-compact-heading"><div><h2 data-toc="false">${language==="zh"?"D1–D10 本质上是四类生命周期问题的进一步拆分":"D1–D10 decomposes four lifecycle questions"}</h2></div><p>${language==="zh"?"它们不是十种竞争方法；先用四类问题定位，再进入十方向总表。":"They are not ten competing methods. Use the four macro questions for orientation, then enter the ten-direction table."}</p></div><div class="direction-macro-grid">${macroCards}</div></section><details class="panel field-history-audit"><summary><div><b>${language==="zh"?"展开完整历史图与旧方向 SVG":"Open full history figure and legacy direction SVG"}</b><span>${language==="zh"?"审计层：保留能力增长、范式迁移、里程碑、驱动因素与开放问题。":"Audit layer retaining capability growth, paradigm shifts, milestones, enablers, and open problems."}</span></div><strong>${language==="zh"?"按需查看":"DETAIL"}</strong></summary><div>${renderHistoryFigure()}${renderOverviewFigure(config,language==="zh"?"Agent 自进化研究方向与历史 Idea 谱系图":"Agent self-evolution direction and historical idea-lineage map")}</div></details>`;
  const directionAtlas=`${renderDirectionAtlasTable(directions)}<section class="direction-detail-folds"><div class="field-compact-heading"><div><h2 data-toc="false">${language==="zh"?"需要边界、论文或历史谱系时，再展开单个方向":"Open a direction only for boundary, literature, or lineage detail"}</h2></div><p>${language==="zh"?"10 个方向默认全部收起，避免把总览重新拉成长页面。":"All ten directions stay collapsed by default so the atlas remains a comparison page rather than a long dossier dump."}</p></div>${directions.map(renderDirectionDetailFold).join("")}</section>`;
  const agendaGroups=config.groupsAfter||[];
  const agenda=`<details class="panel historical-agenda-fold"><summary><div><b>${language==="zh"?"历史长期议程与仍开放的领域问题":"Former long-term agenda and still-open field questions"}</b><span>${language==="zh"?"作为领域知识保留，不再作为当前研究队列。":"Preserved as field knowledge, not the current research queue."}</span></div><strong>${language==="zh"?"历史资产":"HISTORY"}</strong></summary><div>${renderGroupNav(agendaGroups)}${renderMergedGroups(agendaGroups)}</div></details>`;
  const bridge=`${renderHistoricalDirectionMigration()}${agenda}`;
  const header=`<div class="field-landscape-page-header"><div class="eyebrow">${textOf(config.eyebrow)}</div><h1>${textOf(config.title)}</h1><p class="lead">${textOf(config.lead)}</p></div>`;
  return `${header}${renderCustomChapter(chapters[0],0,orientation)}${renderCustomChapter(chapters[1],1,directionAtlas)}${renderCustomChapter(chapters[2],2,bridge)}`;
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
  return `<section class="panel advisor-board"><div class="idea-panel-heading"><div><h3 id="advisor-comparison-board">${language === "zh" ? "研究方向横向决策板" : "Advisor comparison board"}</h3><p class="section-intro">${language === "zh" ? "先横向比较问题、机制、优势和决定性证据，再打开下方完整论证卡。这里的阶段是资源决策，不是论文质量结论。" : "Compare the problem, mechanism, advantage, and decisive evidence first, then open the full dossiers below. Stages are resource decisions, not paper-quality claims."}</p></div><strong>${ideas.length} ${language === "zh" ? "个优先候选" : "priority candidates"}</strong></div><div class="idea-board-filters">${filters.map(([key,label],index) => `<button class="idea-board-filter ${index === 0 ? "active" : ""}" data-idea-filter="${key}">${label}</button>`).join("")}</div>${renderAdvisorDecisionTable(ideas)}${(meta.warnings || []).map((warning) => `<div class="idea-board-warning">${textOf(warning)}</div>`).join("")}</section>`;
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
function humanTerminalState() {
  return window.HUMAN_TERMINAL_IDEA_STATE || {decision_date:"",summary:{},parents:{},absorbed_children:{},independent_methods:{}};
}
function terminalParentState(id) {
  return humanTerminalState().parents?.[id] || null;
}
function currentParentDecisionRecord(terminal) {
  if (!terminal) return {};
  const batch = window.P0_REVIVED_BATCH_F0 || window.RESEARCH_SYSTEM_STATE?.p0_revived_batch_f0 || {};
  const revived = (batch.revived || []).find((row) => row.idea_id === terminal.idea_id || row.code === terminal.code) || {};
  const batchRow = (batch.parent_batch || []).find((row) => row.idea_id === terminal.idea_id || row.code === terminal.code) || {};
  return {
    ...batchRow,
    ...revived,
    decision: revived.decision || batchRow.decision || terminal.p0_decision || "",
    detail: revived.gpu0?.evidence || revived.next_action || terminal.current_fact || terminal.terminal_reason || {},
  };
}
function canonicalResearchItemByCode(code) {
  return (window.RESEARCH_ITEM_STATE?.research_items || []).find((row) => row.code === code) || null;
}
function humanParentFinalState(terminal) {
  if (!terminal) return "";
  const canonical = canonicalResearchItemByCode(terminal.code);
  if (canonical?.scientific_state === "HOLD") return "hold";
  if (canonical?.scientific_state === "MERGED") return "merge";
  if (canonical?.scientific_state === "STOPPED") return "stop";
  if (terminal.terminal_state === "merge") return "merge";
  if (String(currentParentDecisionRecord(terminal).decision || "").startsWith("STOP_")) return "stop";
  return terminal.terminal_state || "";
}
function humanParentFinalStatusLabel(status) {
  const labels = {
    p0:{zh:"历史：曾进入 P0",en:"Historical: entered P0"},
    "p0-ready":{zh:"历史：曾达到 P0-ready",en:"Historical: reached P0-ready"},
    hold:{zh:"暂缓 · 等待新证据",en:"HOLD · waiting for new evidence"},
    merge:{zh:"已合并",en:"Merged"},
    drop:{zh:"历史：曾停止",en:"Historical: previously stopped"},
    stop:{zh:"当前已停止",en:"Currently stopped"},
  };
  return textOf(labels[status] || {zh:status,en:status});
}
function humanParentFinalSummary() {
  const states = Object.values(humanTerminalState().parents || {}).map(humanParentFinalState);
  return {
    human_parents: states.length,
    p0: states.filter(state => state === "p0").length,
    p0_ready: states.filter(state => state === "p0-ready").length,
    hold: states.filter(state => state === "hold").length,
    merge: states.filter(state => state === "merge").length,
    drop: states.filter(state => state === "drop").length,
    stop: states.filter(state => state === "stop").length,
  };
}
function humanParentEvidenceDisposition(terminal, finalState = humanParentFinalState(terminal)) {
  const current = currentParentDecisionRecord(terminal);
  const decision = String(current.decision || "");
  const currentFact = textOf(terminal?.current_fact || {});
  const terminalReason = textOf(terminal?.terminal_reason || {});
  const priorReason = textOf(((terminal?.revival_history || []).at(-1) || {}).prior_terminal_reason || {});
  if (decision.startsWith("STOP_")) {
    const currentInstanceOnly = /CURRENT_SUBSTRATE|SUPPORT_INSUFFICIENT|UPDATER_INCOMPETENT|RANKING_DEGENERATE/.test(decision);
    return {
      tone: currentInstanceOnly ? "hold" : "stop",
      label: language === "zh"
        ? (currentInstanceOnly ? "当前实验实例已停止；方法结论未定" : "当前独立路线已停止")
        : (currentInstanceOnly ? "Current experiment instance stopped; method remains inconclusive" : "Current standalone route stopped"),
      detail: textOf(current.detail || {}) || currentFact || terminalReason,
      code: decision,
    };
  }
  if (finalState === "merge") return {tone:"merge",label:language === "zh" ? "已并入其他父级研究方向，不再独立推进" : "Merged into another parent; no standalone continuation",detail:terminalReason,code:""};
  if (finalState === "drop") return {tone:"stop",label:language === "zh" ? "已停止；满足重开条件前不推进" : "Stopped; do not proceed until the reopen condition is met",detail:priorReason || terminalReason,code:""};
  if (finalState === "p0-ready") return {tone:"hold",label:language === "zh" ? "等待门禁与人工执行授权" : "Waiting for gates and explicit human execution authority",detail:currentFact || terminalReason,code:decision};
  return {tone:"hold",label:language === "zh" ? "保留历史 P0；当前不授权重跑" : "Historical P0 preserved; rerun is not currently authorized",detail:currentFact || terminalReason,code:decision};
}
const IDEA_STOP_TAXONOMY = {
  simple:{zh:"简单方法达到相同或更好结果",en:"A simpler method matches or beats it",tone:"simple"},
  support:{zh:"当前数据或底座不支持验证",en:"The current data or substrate cannot support the test",tone:"support"},
  identify:{zh:"实验区分不了机制",en:"The experiment cannot distinguish the mechanism",tone:"identify"},
  collision:{zh:"已有工作基本解决",en:"Existing work already covers the contribution",tone:"collision"},
  merge:{zh:"更适合作为组件",en:"More useful as a component",tone:"merge"},
  principle:{zh:"核心假设被否定",en:"The core hypothesis was contradicted",tone:"principle"},
};
const PARENT_BRIEFING_ZH = {
  "A-1":{wanted:"用更新后的早期行为变化，低成本发现哪些任务值得重点回归检查。",why:"更简单的目标任务族优先级在更低成本下找回了更多真实变化，复杂的早期分支审计没有带来额外收益。",learned:"早期行为信号可以用于安排审计顺序，但不足以成为一篇独立方法论文。"},
  "A-2":{wanted:"让控制器根据当前证据，动态决定还要检查多深、何时停止。",why:"冻结测试上，固定检查一层与自适应策略找回了同样多的有效变化，而且成本更低。",learned:"当前场景不需要学习控制器；固定检查深度已经是更好的决策规则。"},
  "A-3":{wanted:"Qwen2.5-7B-Instruct 在 ALFWorld 的文字版家庭环境里执行多步家务任务。某个任务失败后，更新流程会根据这次失败生成一条候选 Prompt patch，并把它作为后续执行时持续生效的新规则；这不是 Agent 在任务中临时自己改 Prompt。我们想先确认 patch 确实修好目标任务，再判断它会不会让 Agent 原本已经会做的其他家务任务变差。A-3 要做的就是更新前检查：在真正接受 patch 前，用一小组旧任务提前预测这种能力回退。",why:"当前这版实验还没有走到 A-3 回归检查器本身。8 个冻结候选 Prompt patch 中只有 1 个真的改善了它想修的目标任务，因此没有形成足够多“新任务已变好”的有效更新去继续比较谁会伤害旧能力。6 个旧能力检查任务已经准备并确认模型原本会做，但隐藏旧任务没有打开。",learned:"先把“更新生成器能否稳定产生真正有效的更新”作为所有回归门控实验的前置资格检查；否则下游门控方法没有足够实验对象，负结果也不能解释成门控方法失败。"},
  "A-4":{wanted:"学习更新之间的冲突、先后顺序和局部修复规则。",why:"直接记录有序更新风险并做同预算局部修复，已经完全复现了类型化规则系统。",learned:"有序组合风险值得保留，但当前复杂规则注册表没有独立价值。"},
  "A-5":{wanted:"压缩长期更新历史，同时保持准确回滚和顺序依赖。",why:"通用状态差分和定期检查点都能同样准确回滚，而且存储或回放成本更低。",learned:"历史压缩应作为版本管理基础设施，而不是 Agent 特有的新方法。"},
  "B-1":{wanted:"从多条同结果轨迹中提取稳定、可复用的过程经验。",why:"真实实验只得到与简化方法并列的极小效应，独立机制没有留下足够空间。",learned:"保留效应验证思想，并入记忆准入与迁移审计。"},
  "B-2":{wanted:"只保留那些删除后会真正改变结论的关键经验。",why:"现有数据里没有专门的“删除后结论改变”案例，远不足以训练或判断该选择器。",learned:"结论改变是合理的保留标准，但必须先建立足够的真实案例库。"},
  "B-3":{wanted:"定位多条记忆共同被检索时，究竟是哪种组合造成干扰。",why:"当前底座缺少足够独立、未见过的共检索交互单元，无法公平判断方法。",learned:"先扩大真实共检索支持，再讨论复杂的干扰定位器。"},
  "B-4":{wanted:"经验只有在未来任务上因果性地有帮助时才允许长期写入。",why:"该问题与通用回归门控使用同一决策信息，独立保留会重复 A-3。",learned:"把经验准入作为回归控制的一种应用，而不是单独立题。"},
  "B-5":{wanted:"遇到反例后，只收缩经验的适用范围，而不重写整条经验。",why:"标准的紧凑前置条件／ILP 学习器在相同复杂度下已经达到相同结果。",learned:"单调适用范围可以作为实现约束，但不是独立机制贡献。"},
  "B-6":{wanted:"根据未来真实复用效果，决定记忆何时复验、降权或删除。",why:"简单的近期性加使用频率策略在同审计预算下更好，没有给学习型风险模型留下收益。",learned:"当前应采用简单缓存与定期复验策略。"},
  "B-7":{wanted:"给每条经验学习一个明确的适用边界。",why:"它与 B-5 的反例驱动适用范围收缩实质相同，继续独立推进会重复。",learned:"作为 B-5 的边界表示组件保留。"},
  "C-1":{wanted:"防止同一来源不断自我复制标签，造成虚假的高置信度。",why:"简单的来源降权已经取得相同效果，没有给复杂的标签谱系图留下足够增益空间。",learned:"保留标签来源审计；默认先用简单来源权重。"},
  "C-2":{wanted:"当评价器随系统一起变化时，识别并修复评分漂移。",why:"冻结锚点加简单残差校准已经等效，复杂的跨版本评价器修复没有额外收益。",learned:"跨版本评分矩阵适合做诊断，实际控制先用冻结锚点。"},
  "C-3":{wanted:"检查奖励定义在版本变化后是否仍表达同一个目标。",why:"与 C-2 的评价器漂移问题重复，独立立题不会增加新的决策。",learned:"作为 C-2 的奖励不变性诊断与消融保留。"},
  "C-4":{wanted:"尽早发现自纠正系统是否正在重复同一种失败模式。",why:"同信息的浅层规则已经达到当前数据上限，复杂检测器没有独立提升。",learned:"先把简单失败模式规则做成运行时监控。"},
  "C-5":{wanted:"只有被干预验证过的纠正，才允许长期写入系统。",why:"A-3 式回归门控或相同特征的简单阈值已经达到同样决策效果。",learned:"把干预证据并入通用更新准入，不单独训练纠正门。"},
  "C-6":{wanted:"把自纠正成功归因到真正起作用的动作，而不是整段轨迹。",why:"与已有自纠正和信用分配方向重叠，当前没有独立论文边界。",learned:"保留动作编译器作为 C 类方法资产。"},
  "D-1":{wanted:"从失败中生成最小且最有学习价值的反例任务。",why:"使用同一验证器的直接交集过滤已经与逐例最小化达到相同效果。",learned:"保留可靠反例生成，但不把逐样本最小化当作独立贡献。"},
  "D-2":{wanted:"沿着模型当前失败边界，持续生成下一批训练任务。",why:"直接预测候选任务的有效产出已经复现了版本化前沿选择器。",learned:"版本趋势适合做诊断；实际选课先看直接产出。"},
  "D-3":{wanted:"避免自动课程随系统迭代偏离真正需要学习的能力。",why:"与 D-2 依赖同一尚不成熟的自动课程场景，单独推进没有额外对象。",learned:"作为 D-2 的课程漂移监控组件保留。"},
  "E-1":{wanted:"预测并约束一次工作流修改在未见工作流上的真实效果。",why:"当前干预表里的编辑效果几乎没有可排序差异，无法判断任何排序器是否有效。",learned:"先收集有真实非并列编辑效果的配对干预，再评估工作流更新方法。"},
  "E-2":{wanted:"定位工作流图中真正导致失败的分支，并编译局部修复。",why:"直接的工作流编辑基线已经在相同信息下达到相同效果。",learned:"失败子图和修复语法可并入通用工作流编辑器。"},
  "F-1":{wanted:"只学习那些会改变后续决策的世界模型误差。",why:"直接比较动作是否改变，已经完全复现了价值感知误差门控。",learned:"动作分歧是更简单、可解释的学习优先级信号。"},
  "F-2":{wanted:"从不可逆失败的反事实中学习未来动作的前置安全条件。",why:"同容量的直接安全屏障已经完全等效，没有留下独立编译机制增益。",learned:"前驱条件适合作为安全屏障的解释，不必独立训练。"},
  "F-3":{wanted:"从成功恢复轨迹中提取可复用的最小恢复算子。",why:"直接的残余状态条件恢复策略已经达到相同结果。",learned:"保留恢复状态复现审计，执行层使用更简单的直接恢复策略。"},
};
const PARENT_SIMPLE_COMPARISONS_ZH = {
  "A-1":{ours:"先看更新前后轨迹在第 1 步是否分叉，再按这个早期行为变化给回归任务排序。",baseline:"不分析轨迹分叉，只按 development 集里哪个目标任务族更容易受更新影响来排优先级。另一个更便宜的规则只检查第 1 步是否出现 navigate→navigate。",matched:"两边都只用 36 个 development unit 定规则，再在同一批 36 个冻结 future_eval unit、同一 2813 个配对动作步上比较。",rows:[{metric:"找回真实变化",ours:"2/5（40%）",baseline:"3/5（60%）",delta:"简单方法 +20 个百分点"},{metric:"检查成本",ours:"624 / 2813 步",baseline:"613 / 2813 步",delta:"简单方法少 11 步"},{metric:"同召回的更便宜规则",ours:"40%，624 步",baseline:"40%，526 步",delta:"简单方法少 98 步"}],verdict:"简单规则不仅更便宜，还找回了更多真实变化，所以停止把早期分叉审计当独立方法；它只保留为审计排序提示。"},
  "A-2":{ours:"根据目标任务族、来源任务族或来源→目标关系，自适应决定证据要向后检查几层。",baseline:"所有案例一律只检查 1 层（fixed h=1），不学习控制器。",matched:"三种自适应策略和 fixed h=1 都在同一冻结 future_eval 的 5 个非零案例、同一 2813 步总空间上比较。",rows:[{metric:"找回真实变化",ours:"2/5（40%）",baseline:"2/5（40%）",delta:"0 个百分点"},{metric:"最佳检查成本",ours:"734 / 2813（26.1%）",baseline:"624 / 2813（22.2%）",delta:"固定规则少 110 步 / 3.9 个百分点"}],verdict:"自适应没有多找回一个变化，反而多检查 110 步，因此停止训练证据深度控制器。"},
  "A-4":{ours:"把 15 条更新对／顺序干预记录编译成 no-good、先后约束和兼容性规则，再据此修复。",baseline:"只存“有序描述符对→风险”的查表结果，并用同样候选预算做局部约束修复。",matched:"同一 15 条训练记录、20 个 update identity 全未见的隐藏三元组合、同一修复候选预算。",rows:[{metric:"风险预测准确率",ours:"100%",baseline:"100%",delta:"0"},{metric:"修复成功率",ours:"100%",baseline:"100%",delta:"0"},{metric:"候选检查次数",ours:"49",baseline:"49",delta:"0"}],verdict:"复杂规则注册表的每个输出都被查表+局部修复复现，准确率和成本没有任何差值。"},
  "A-5":{ours:"用 Prompt／Memory／Workflow 语义压缩 40 次连续更新的历史，并保持选择性回滚。",baseline:"方法一只保存通用状态差分，不理解 Agent 语义；方法二按固定间隔保存检查点。",matched:"同一 40 次更新、12 个冻结回滚查询；检查点方法使用与我们约 72 个存储单元相同的预算。",rows:[{metric:"回滚正确",ours:"12/12",baseline:"12/12",delta:"0"},{metric:"存储（状态差分）",ours:"73 个存储单元",baseline:"38 个存储单元",delta:"简单方法少 35 个（47.9%）"},{metric:"平均回放（检查点）",ours:"6.5 段",baseline:"2.25 次更新",delta:"简单方法少 4.25（65.4%）"}],verdict:"两种通用版本管理方法都同样正确，而且一个更省存储、一个更少回放，所以不再主张 Agent 专用历史压缩。"},
  "B-1":{ours:"从最终结果相同、但过程不同的轨迹中学习“过程不变量”，再决定哪些经验值得保留。",baseline:"只按经验对未来任务的实际 utility／effect 做准入，不额外建模同结果过程差异。",matched:"真实实验使用匹配的简化对照；当前终态记录只保留了 matched-simplification tie 和隐藏残余效应约 0.0139。",rows:[{metric:"隐藏独立残余效应",ours:"≈0.0139",baseline:"匹配简化对照打平",delta:"未留下可支持独立机制的差值"}],verdict:"这里不是说问题不存在，而是现有记录中过程不变量没有带来可区分于 utility/effect 准入的效果，因此并入后者。"},
  "B-5":{ours:"每遇到反例，只单调收紧经验的适用条件，不改经验正文和谓词词表。",baseline:"标准穷举 ILP／前置条件学习器，在相同复杂度预算内直接寻找条件。",matched:"同一 12 条技能、同一技能正文、谓词词表、反例、旧正例和复杂度上限。",rows:[{metric:"学到完全相同的 gate",ours:"12/12",baseline:"12/12",delta:"0"},{metric:"真实 gate 恢复",ours:"10/12",baseline:"10/12",delta:"0"}],verdict:"两边在 12 条技能上逐条得到相同 gate，失败案例也相同，所以单调修复只保留为实现约束。"},
  "B-6":{ours:"训练 utility-hazard 模型，根据未来复用效果决定记忆复验、降权或删除。",baseline:"固定规则：最近至少 4 个周期没用、且使用次数不超过 2 次，就隔离；阈值在同一审计标签上选。",matched:"12 条记忆×25 次复用=300 次机会；两边都只审计每 5 次激活（60/300），再看其余 240 次未来复用。",rows:[{metric:"仍保留的有害复用",ours:"16",baseline:"0",delta:"简单规则少 16"},{metric:"保留的有益复用",ours:"192",baseline:"192",delta:"0"}],verdict:"简单规则多移除了 16 次有害复用，却没有损失任何有益复用，因此停止学习型风险模型。"},
  "C-1":{ours:"给 400 个标签事件建立来源／祖先谱系图；共享祖先的标签不能被当成独立投票。",baseline:"按标签来源和谱系做简单降权，不构造完整图推断。",matched:"同一 Qwen2.5-7B+ALFWorld 冻结 40 行、400 个标签事件，同一来源和锚点信息。",rows:[{metric:"标签富集度",ours:"96.03%",baseline:"同一数据上的来源降权",delta:"—"},{metric:"两种方法的决策分歧",ours:"2.5%",baseline:"97.5% 决策相同",delta:"仅 2.5 个百分点有差异"}],verdict:"没有记录可支持“准确率完全相同”，但 97.5% 的准入决策相同，完整来源关系图没有留下足够可检验的额外价值。"},
  "C-2":{ours:"建立 3×3 的 actor版本×evaluator版本矩阵，再用因果中和干预定位并修复评分漂移。",baseline:"在每个 evaluator 上用冻结外部锚点拟合截距和 shortcut 残差，直接校准。",matched:"同一冻结外部锚点、同一锚点输出和同一跨版本比较。",rows:[{metric:"漂移归因正确",ours:"3/3",baseline:"3/3",delta:"0"},{metric:"修复 MAE / 最大误差",ours:"相同",baseline:"相同",delta:"0"},{metric:"额外干预调用",ours:"54",baseline:"0",delta:"我们多 54 次"}],verdict:"复杂矩阵没有改善归因或修复误差，只多了 54 次干预调用；矩阵保留为诊断图，不再当控制方法。"},
  "C-4":{ours:"学习失败序列中的重复／顺序特征，预测自纠正是否已经坍缩。",baseline:"只用同一批事前可见特征训练一棵浅层 CART 决策树。",matched:"同一 Qwen2.5-7B+ALFWorld 30 个失败案例、同一冻结 holdout。",rows:[{metric:"冻结 F0 得分",ours:"80.0%",baseline:"76.67%",delta:"我们 +3.33 个百分点"},{metric:"决策分歧率",ours:"6.67%",baseline:"93.33% 决策相同",delta:"只差 6.67 个百分点"}],verdict:"复杂检测器只提高 3.33 个百分点，且 93.33% 的决定与浅树相同，未达到独立方法所需的分歧和增益。"},
  "C-5":{ours:"训练干预验证 gate，只有模型判断某次纠正确实改变未来行为时才写入。",baseline:"使用与 A-3 相同特征的简单阈值规则。",matched:"同一 24 个候选、同一冻结未来观察；未来正向信号只有 3/21。",rows:[{metric:"冻结结果得分",ours:"62.5%",baseline:"79.17%",delta:"简单方法 +16.67 个百分点"},{metric:"准入决策分歧",ours:"33.33%",baseline:"—",delta:"1/3 决策不同"}],verdict:"这里不是打平：简单阈值实际高 16.67 个百分点，因此停止单独训练复杂的纠正准入判断器。"},
  "D-1":{ours:"对每个已验证反例做 delta-debug，删到 1-minimal，再用这些最小反例更新规则。",baseline:"不逐例最小化；对同一规则的多条验证反例直接求共同约束，再更新规则。",matched:"同一 20 条规则、每条 4 个验证反例、最终同为 320 个训练 token。",rows:[{metric:"编译后的规则",ours:"20/20 与对照相同",baseline:"20/20",delta:"0"},{metric:"隐藏边界正确",ours:"60/60",baseline:"60/60",delta:"0"},{metric:"额外 verifier 调用",ours:"320",baseline:"0",delta:"我们多 320 次"}],verdict:"逐例最小化没有改变一条最终规则或一个隐藏答案，只多 320 次验证调用。"},
  "D-2":{ours:"用三个历史版本的趋势和排名变化，选择下一批最值得生成的训练任务。",baseline:"直接用每个候选算子的历史产出拟合线性 yield 预测器。",matched:"3 个冻结版本、30 个 typed operator、留出第 2 版、top-k=6；两边都在看结果前冻结。",rows:[{metric:"隐藏 top-k utility",ours:"-21",baseline:"-21",delta:"0"},{metric:"选择集合一致率",ours:"100%",baseline:"100%",delta:"0"},{metric:"Oracle top-k utility",ours:"39",baseline:"39",delta:"说明场景有空间，但两种当前选择器都没抓到"}],verdict:"版本化选择器与直接产出预测器选了完全相同的 6 个任务，结果同为 -21；保留趋势图做诊断即可。"},
  "E-2":{ours:"学习带结构 credit 的因果工作流语法，定位失败分支并编译局部改写。",baseline:"把同类工作流编辑的配对效果直接存成 typed lookup，遇到新工作流就复用。",matched:"16 个源工作流、32 次调用；8 个 API 和 identity 都未见的隐藏工作流；隐藏阶段都不搜索。",rows:[{metric:"隐藏修复成功",ours:"8/8",baseline:"8/8",delta:"0"},{metric:"有害修复",ours:"0",baseline:"0",delta:"0"},{metric:"逐例改写一致",ours:"8/8",baseline:"8/8",delta:"0"}],verdict:"直接编辑复用逐例生成了相同改写，复杂因果语法没有带来额外结果。"},
  "F-1":{ours:"训练 value-aware residual selector，只挑预计会改变后续价值／决策的世界模型误差。",baseline:"不学价值模型，直接检查世界模型动作和真实动作是否不同。",matched:"同一 120 条 residual（80 开发、40 隐藏）、同一冻结策略；隐藏集中有 9 个真正改变决策的案例。",rows:[{metric:"隐藏 top-k 召回",ours:"33.33%",baseline:"100%",delta:"简单方法 +66.67 个百分点"},{metric:"真正改变决策的案例",ours:"9 个中的 3 个",baseline:"9 个中的 9 个",delta:"简单方法多找回 6 个"}],verdict:"直接动作分歧找全了 9 个决策变化，我们只找回 3 个，所以停止 value-aware selector。"},
  "F-2":{ours:"从反事实前驱案例编译“在什么状态下禁止某动作”的不可逆前置条件。",baseline:"使用同容量的单调 direct shield，直接从状态特征判断允许／禁止。",matched:"5 个风险族；4 个训练拓扑、2 个隐藏拓扑、20 个隐藏案例；隐藏时都关闭模拟器并使用相同信息和容量。",rows:[{metric:"隐藏准确率",ours:"100%",baseline:"100%",delta:"0"},{metric:"逐例决策一致",ours:"20/20",baseline:"20/20",delta:"0"}],verdict:"20 个隐藏案例逐例完全一致；前置条件可作为安全屏障解释，但不再独立训练编译器。"},
  "F-3":{ours:"从同一起点的正常成功轨迹和受扰后成功恢复轨迹中，抽取反复出现的“还差哪一步恢复”的动作模式，形成 2 个恢复算子。",baseline:"不建立恢复算子库，直接用相同配对轨迹训练一个根据当前恢复状态选择动作的策略。",matched:"同一 120 对成功轨迹、7 个训练场景、3 个隐藏场景、36 个隐藏案例。",rows:[{metric:"重复恢复模式占比",ours:"80%",baseline:"使用同一数据",delta:"—"},{metric:"隐藏恢复准确率",ours:"100%",baseline:"100%",delta:"0"},{metric:"逐例决策一致",ours:"36/36",baseline:"36/36",delta:"0"}],verdict:"算子库在 36 个隐藏案例上没有产生一个不同决定；保留恢复模式复现审计，执行改用直接恢复策略。"},
};
const PARENT_SIMPLE_METHOD_GUIDES_ZH = {
  "A-1":{input:"每个 development 案例的目标任务族，以及该任务族过去是否容易被更新影响。",steps:"先按目标任务族分组，统计每组历史上的真实变化率；future 案例只查所属任务族，把变化率高的族排到前面。更便宜的版本只额外检查第 1 步是否出现 navigate→navigate。",output:"一张旧任务的回归检查优先级列表：先测哪些、后测哪些。",omits:"不学习轨迹表示，不比较完整分叉路径，也不训练跨任务族预测器。"},
  "A-2":{input:"每个待审计案例，以及第 1 层可取得的更新后行为证据。",steps:"所有案例都固定只向后检查 1 层：取到这一层证据后立即停止，不根据任务类型或中间结果动态加深。",output:"固定成本的回归检查结果和固定检查步数。",omits:"没有自适应 horizon 控制器，也不学习‘这个案例值得再多看几层’。"},
  "A-4":{input:"两条更新的类型/描述符、先后顺序，以及历史上这个有序组合是否出过问题。",steps:"把历史记录直接存成“更新 A→更新 B = 风险/安全”的表；新三元组合出现时查其中的有序对，避开高风险组合，并在相同候选预算里尝试局部替换。",output:"组合风险判断和一个可行的局部修复。",omits:"不把记录编译成 no-good、precedence、compatibility 等可复用逻辑规则。"},
  "A-5":{input:"连续版本的完整系统状态，或相邻两个版本之间发生了哪些状态变化。",steps:"状态差分法只保存 v_t→v_{t+1} 的变化项；回滚时从目标版本前后逐段应用/撤销差分。检查点法则每隔固定 k 次更新保存一次完整状态，回滚时恢复最近检查点再重放少量更新。",output:"指定历史版本的可恢复状态。",omits:"不理解 Prompt、Memory、Workflow 的语义，也不学习哪些历史片段值得压缩。"},
  "B-1":{input:"同一未来任务在‘使用这条经验’和‘不使用/受控对照’下的结果。",steps:"直接计算经验带来的实际效用差；差值为正或超过预先阈值就保留，否则不准入长期记忆。",output:"这条经验 keep / reject 的准入决定。",omits:"不分析两条成功轨迹过程是否相似，也不学习过程不变量。"},
  "B-5":{input:"每条经验的布尔/离散前置条件、正例和反例，以及冻结的规则复杂度上限。",steps:"穷举候选条件组合，或用 ILP（整数规划）选择一组最短条件，使它尽量覆盖旧正例、排除反例；例如得到“容器已打开 AND 目标可见时才用这条经验”。",output:"一条可直接执行的 applicability / precondition gate。",omits:"不要求每次只做单调收缩，也没有特殊的增量修复机制。"},
  "B-6":{input:"每条记忆最近什么时候被调用、连续多久没被调用、累计调用次数。",steps:"计数器逐轮更新；如果连续 4 个周期没用且累计使用次数≤2，就把记忆标成 stale 并隔离/复验，否则继续保留。阈值只在 development 审计标签上选一次。",output:"keep / quarantine / revalidate 的缓存维护决定。",omits:"不预测未来 harm，也不训练 utility-hazard 模型。"},
  "C-1":{input:"每个标签的 ACCEPT/QUARANTINE 决定、置信度，以及它属于两个独立 root/祖先中的哪一个。",steps:"先在每个 root 内按置信度做一次多数表决，把同一祖先复制出的很多后代压成 1 票；只有两个独立 root 都投 ACCEPT，最终才接受。",output:"每个候选最终 ACCEPT / QUARANTINE。",omits:"不构建完整来源关系图，也不估计任意标签间相关系数；每个祖先最多贡献一票。"},
  "C-2":{input:"一组冻结外部锚点，在某个 evaluator 下的原始评分和已知参考结果。",steps:"在锚点上估计这个 evaluator 的固定偏置/捷径残差，例如整体偏高多少；随后对所有新评分统一减去这项校正。",output:"一个校准后的 evaluator 分数。",omits:"不建立 actor版本×evaluator版本的 3×3 因果矩阵，也不逐版本做干预。"},
  "C-4":{input:"与复杂检测器完全相同的事前特征，例如任务族、源轨迹步数、无效动作率、patch 长度。",steps:"CART 决策树每一层选择一个‘特征≤某阈值吗’的问题，让两类样本分得最开；最多分 3 层，到叶子后按训练样本多数类别直接输出。",output:"继续纠正 / 已坍缩（或目标纠错模式）的离散预测。",omits:"不建模长序列，不学习隐状态，也没有复杂的跨步骤交互表示。"},
  "C-5":{input:"与复杂 gate 相同的 source_gain、8 个 probe 的平均效果 probe_mean，以及 probe 中是否出现伤害 probe_harm。",steps:"使用冻结三条件：source_gain>0、probe_harm=0、probe_mean≥0。三项同时满足才接受纠正；任一不满足就隔离。",output:"commit / quarantine 的纠错写入决定。",omits:"不训练 logistic/干预表示模型，也不从数据学习多特征权重。"},
  "D-1":{input:"同一规则对应的多条已经由 verifier 确认会失败的反例。",steps:"不对每条反例做 delta-debug；直接取这些反例共同违反的条件/共同约束，用交集形成一条更新后的规则。",output:"一条覆盖这批反例的修正规则。",omits:"不逐例删除条件来寻找 1-minimal 反例，因此没有额外 verifier 搜索。"},
  "D-2":{input:"每个任务生成算子过去几版实际生成了多少可用训练任务/有效样本。",steps:"对每个算子的历史 yield 做一个简单线性预测，估计下一版还能产出多少有效任务；按预测 yield 从高到低取 top-k。",output:"下一批优先调用的任务生成算子列表。",omits:"不建模版本排名轨迹、前沿结构或复杂课程状态。"},
  "E-2":{input:"过去局部 workflow edit 的类型，以及这类 edit 在源工作流上的配对效果。",steps:"把“编辑类型/局部结构→效果”直接做成 typed lookup；新工作流遇到同类局部结构时，取表里历史效果最好的编辑并复用。",output:"要应用的局部 workflow edit。",omits:"不学习因果 credit 图，也不编译工作流语法或失败子图模型。"},
  "F-1":{input:"同一个状态下，世界模型预测出来的下一状态/动作与真实环境得到的下一状态/动作。",steps:"把两边都送进同一冻结策略；如果下一动作不同，就把这条误差标成‘会改变决策’，否则降到低优先级。",output:"哪些 world-model residual 最值得先修的排序/二元标记。",omits:"不训练 value predictor；直接把‘动作是否改变’当价值代理。"},
  "F-2":{input:"每个 hazard family 的训练状态谓词，以及哪些状态已知会导致不可逆失败。",steps:"对同一 hazard family 的所有 unsafe 训练状态取谓词交集，得到最小共同危险条件；新状态只要同时包含这组共同条件就直接 block，否则 allow。",output:"当前状态/动作 allow / block 的 direct shield。",omits:"不额外学习反事实前驱编译器；直接把 unsafe 样本的共同谓词当安全屏障条件。"},
  "F-3":{input:"训练轨迹中恢复后仍残留的 residual 类型，以及这个 residual 对应的成功恢复动作。",steps:"直接计数 residual→动作映射；同一个 residual 在训练场景里至少重复 2 次，就把它存成查表规则，新场景出现同 residual 时直接输出对应动作；没见过就输出 none。",output:"下一步恢复动作，或没有可复用动作。",omits:"不再额外建立恢复算子对象/组合结构；只做同一 residual 的直接查表。"},
};
function renderSimpleMethodGuide(guide){
  if(!guide)return "";
  const cells=[["输入看什么",guide.input],["具体怎么跑",guide.steps],["最后输出什么",guide.output],["相比复杂方法少了什么",guide.omits]];
  return `<div class="simple-method-guide"><b>简单方法具体怎么做到</b><div>${cells.map(([label,value])=>`<span><small>${esc(label)}</small><em>${esc(value)}</em></span>`).join("")}</div></div>`;
}
function renderConcreteMethodComparison(comparison,scope="parent",guide=null) {
  if(language!=="zh"||!comparison)return "";
  const rows=(comparison.rows||[]).map(row=>`<tr><th>${esc(row.metric)}</th><td>${esc(row.ours)}</td><td>${esc(row.baseline)}</td><td>${esc(row.delta)}</td></tr>`).join("");
  return `<section class="concrete-method-comparison comparison-${esc(scope)}"><header><div><b>具体对照：我们的方法 vs 简单方法</b><span>先看两边怎么做，再看效果差多少</span></div></header><div class="comparison-designs"><article><small>我们的方法怎么做</small><p>${esc(comparison.ours)}</p></article><article class="comparison-simple"><small>简单方法一句话</small><p>${esc(comparison.baseline)}</p></article></div>${renderSimpleMethodGuide(guide)}<div class="comparison-matched"><b>怎么保证比较公平</b><p>${esc(comparison.matched)}</p></div><div class="comparison-table-wrap"><table><thead><tr><th>指标</th><th>我们的方法</th><th>简单方法</th><th>效果差多少</th></tr></thead><tbody>${rows}</tbody></table></div><div class="comparison-verdict"><b>为什么这个结果足以停止</b><p>${esc(comparison.verdict)}</p></div></section>`;
}
function ideaStopReasonMeta(decision="", finalState="", failureLayer="") {
  const raw=`${decision} ${failureLayer}`.toUpperCase();
  let key="simple";
  if(finalState==="merge"||/MERGE/.test(raw)) key="merge";
  else if(/CURRENT_SUBSTRATE|SUPPORT_INSUFFICIENT|UPDATER_INCOMPETENT|RANKING_DEGENERATE|NO_R1|ABSENT/.test(raw)) key="support";
  else if(/IDENTIFIABILITY|PROTOCOL|OPERATIONALIZATION/.test(raw)) key="identify";
  else if(/COLLISION|REDUCTION|BLOCK/.test(raw)) key="collision";
  else if(/CORE_PRINCIPLE|PRINCIPLE_STOP|DEAD_END|FALSIF/.test(raw)) key="principle";
  return {key,...IDEA_STOP_TAXONOMY[key]};
}
const PARENT_SCENE_ZH = {
  "A-1":"Agent 接受一次候选更新后，不可能把所有旧任务都完整重跑。这里具体做的是：先看更新前后轨迹最早在哪一步发生行为变化，再用这个信号给旧任务排回归检查优先级；真正要回答的是，能不能更便宜地把最可能被更新弄坏的旧任务先找出来。",
  "A-2":"同样是在更新后的回归检查里，区别在于不预先固定要检查几步。我们让一个控制器根据已经看到的证据决定继续检查还是停止，再和“所有案例固定只检查 1 步”比较；如果自适应没有多发现回退，却花更多检查成本，就没有必要训练控制器。",
  "A-3":"Qwen2.5-7B-Instruct 在 ALFWorld 的文字家庭环境里执行多步家务。某个任务失败后，更新流程会根据失败轨迹生成一条候选 Prompt patch，作为后续执行持续可见的新规则，目的是让同类失败下次不再发生。我们先确认 patch 真的修好目标任务，再问它会不会让 Agent 原本会做的其他家务任务变差。",
  "A-4":"Agent 连续接受多条更新时，两条单独看都没问题的规则可能因为先后顺序或组合方式发生冲突。我们把 Prompt、工具和工作流更新组成成对/三元组合，比较复杂的冲突规则系统与直接记录“哪种有序组合有风险”的简单查表修复，看复杂表示是否真的能处理未见组合。",
  "A-5":"Agent 长期运行后会积累很多 Prompt、Memory 和 Workflow 更新，但出问题时仍要能准确回到某个旧版本。这里把 40 次顺序更新当成一段版本历史，比较语义压缩、普通状态差分和定期检查点：谁既能答对 12 个回滚请求，又更省存储和回放。",
  "B-1":"Agent 可能用不同操作过程完成同一个任务。我们想知道，能不能从这些“结果相同、过程不同”的成功轨迹里提取一条真正跨过程有用的经验；具体会把候选经验开/关后重放未来任务，再和只看实际任务收益的简单记忆准入方法比较。",
  "B-2":"Agent 的记忆库越来越大时，我们不想因为一条经验看起来重要就永久保留它。真正要找的是“删掉这条记忆以后，Agent 对任务的结论或动作真的会改变”的案例；只有这类删除敏感案例足够多，才有数据训练一个保留/删除选择器。",
  "B-3":"Agent 一次可能同时检索出多条记忆。某条记忆单独使用没问题，但和另一条一起出现时可能让动作变坏。这个方向想通过控制“是否检索、检索内容、排序和共同出现组合”来定位到底是哪一条或哪一组记忆造成干扰，再决定隔离、改写或限制排序。",
  "B-4":"Agent 生成一条新经验后，不直接写入长期记忆，而是先拿少量未来任务验证：这条经验到底有没有真正帮助后续决策。问题与 A-3 很接近——都是在接受持久更新前，用有限测试决定是否准入；这里把更新对象具体限定成 memory/lesson。",
  "B-5":"一条经验在厨房任务里可能有用，但遇到反例后不一定应该整条删除。我们给每条 skill 保留正文，只逐步收紧“什么状态下可以用它”的前置条件，再与普通 ILP/前置条件学习器比较，看这种单调收缩是否真的有额外价值。",
  "B-6":"长期记忆早期有用，随着任务分布变化可能逐渐过时。这里在连续复用任务流中记录每条记忆什么时候被用、用了以后是帮助还是伤害，再决定何时复验、降权或删除；对照是最简单的“多久没用 + 使用频率”缓存规则。",
  "B-7":"这个方向同样关心“经验在什么情况下才适用”：给每条 lesson 学一个明确的状态边界，避免在不合适的任务里继续调用。后续审查发现，它和 B-5 的“遇到反例就收紧适用范围”实际是在解决同一个决策问题。",
  "C-1":"Agent 反复用自己的输出给新数据打标签时，同一个错误来源可能被复制很多次，看起来像有很多独立证据。这里追踪 4 轮自标注中每个标签最初来自谁、哪些标签其实共享同一个上游来源，再比较完整的来源关系图和简单的“同来源降权”规则能否更好识别不可靠标签。",
  "C-2":"同一个回答今天被评价器打高分，换了新版评价器后可能被打低分；如果回答模型和评价器一起迭代，很难知道性能变化到底来自模型还是评分标准。这里把多个回答模型版本和多个评价器版本交叉评分，再用固定外部锚点判断评分漂移，并比较复杂修复与简单锚点校准。",
  "C-3":"系统版本更新后，奖励函数表面上还是同一个分数，但它可能已经不再代表原来的目标。这个方向原计划把同一批行为交给不同版本的奖励/评价器，检查“高分”含义是否发生改变；审查后发现它本质上就是 C-2 的评价器漂移诊断。",
  "C-4":"模型答错题后会让自己再纠正一轮，但有时会连续重复同一种错误。这里用 GSM8K/HumanEval 的失败与纠错轨迹，预测“再纠正一轮到底会不会有帮助”，并比较复杂序列检测器和一棵只看少量当前特征的浅层决策树。",
  "C-5":"Agent 答错后会生成一条纠错经验。我们不想因为它下一次偶然答对，就马上把这条经验永久写入；因此会对同一个失败做受控测试，确认这条纠正确实改变了后续行为，再决定是否保存，并与看到完全相同证据的简单阈值规则比较。",
  "C-6":"一次自纠正轨迹可能包含好几个动作：重新观察、换工具、改答案。我们原本想找出到底哪一步真正导致成功，再只保留那部分纠正经验；后续发现这个问题与已有自纠正信用分配工作高度重叠，因此没有继续建立独立任务实验。",
  "D-1":"Agent 失败后可以生成很多相似反例。这里想把一个已验证的失败任务删减到“再删任何条件就不再暴露错误”的最小反例，再用于更新规则；对照是不逐条最小化，直接从多条已验证反例里提取共同约束。",
  "D-2":"自动课程系统每轮都要决定“下一批让 Agent 练什么”。我们根据模型过去几个版本的失败变化来挑新任务，再和更简单的“哪个任务生成器过去产出最高就优先哪个”比较，看复杂的前沿跟踪是否真能选出更有用的训练任务。",
  "D-3":"如果自动课程长期由系统自己生成，课程可能越来越偏向容易生成、容易得分的题，而不是 Agent 真正缺的能力。这个方向想监控课程分布随版本漂移；但它依赖 D-2 的自动课程生成先可靠，因此当前只作为 D-2 的监控组件。",
  "E-1":"一个 Agent 工作流由多个工具/API 节点组成。我们想根据过去“改某个节点前后任务表现怎样变化”的配对记录，预测在一个没见过的新工作流里应该提交哪种局部编辑；但前提是源数据里不同编辑真的产生可排序的效果。",
  "E-2":"工作流失败时，不想整张图重写。这里根据真实执行轨迹定位最可能出错的分支，生成局部改写，再和更直接的办法比较：把过去同类局部编辑的实际效果记下来，在新工作流里直接复用最有效的编辑。",
  "F-1":"世界模型会预测下一状态，但不是每个预测误差都值得学习。我们只关心那些会让冻结策略改动作的误差：把预测状态替换成真实状态后，如果 Agent 的下一动作会变，就优先修这个误差；并与最简单的“直接看动作是否不同”规则比较。",
  "F-2":"具身 Agent 进入某些状态后，再怎么补救也无法恢复安全，例如跨过不可逆边界。这里从已知不可逆失败与安全案例里学习“什么状态下禁止什么动作”的前置条件，再和容量相同、直接从状态特征判断允许/禁止的安全屏障比较。",
  "F-3":"机器人受到扰动后仍可能最终完成任务。我们把从同一起点出发的正常轨迹和受扰后成功恢复轨迹配对，提取重复出现的最小恢复动作模式，再看这些恢复算子能否在新场景里比直接学习一个恢复策略更好。"
};
const PARENT_ONE_MINUTE_ZH = {
  "A-3":{
    scene:"Qwen2.5-7B-Instruct 在 ALFWorld 的文字版家庭环境里做多步家务，例如找物体、拿起物体、加热/清洗/冷却后再放到指定位置。某个源任务失败后，更新流程根据这次失败生成一条候选 Prompt patch，作为后续任务一直可见的新行为规则，目的是让同类失败下一次不再发生。A-3 关心的是：这条新规则即使修好了刚才的任务，会不会改变 Agent 在原来已经会做的家务任务上的动作，造成“学会新的、弄坏旧的”。",
    progress:"生命周期：历史 P0 → 当前 HOLD。已经固定 Qwen2.5-7B + ALFWorld 这一版实验，准备并确认了 6 个模型原本会做的旧能力检查任务，也实际生成并检查了 8 个候选 Prompt patch。还没有做 A-3 与简单回归规则的正式核心比较；隐藏旧任务也从未打开。",
    observed:"总体上，8 个候选 patch 只有 1 个真正让目标任务变好。成功例：原本失败的“拿苹果→放进微波炉加热→再放进垃圾桶”任务，加入对应 patch 后 9 步完成。失败例：为“清洗勺子后放到餐桌”生成的 patch 虽然写出了清洗再放置的操作原则，更新后仍跑满 50 步失败；“把土豆放冰箱冷却后再放到边桌”也仍跑满 50 步失败。说明当前主要问题发生在回归检查之前：大多数 patch 自己都没有先把目标任务修好。",
    judgment:"现在还不能判断 A-3 的回归检查器有没有用。A-3 真正需要比较的是一批“已经确认改善目标任务”的更新里，哪些会破坏旧能力；当前有效更新太少，核心测试集没有形成。因此被暂停的是这套 Qwen2.5-7B + ALFWorld + 当前 Prompt-patch 生成方式，不是 A-3 的科学问题或回归检查方法。",
    human:"现在最值得人工一起看的不是 A-3 门控模型，而是 7 个失败 patch 和唯一成功 patch 为什么不同：失败 patch 是没有抓到真实失败原因、写得太泛、没有改变实际动作，还是 Prompt 本身就不是这些失败的合适更新表面？尤其可以把原始失败轨迹、patch 内容和更新后动作逐例并排看，判断是否存在共同失败模式。",
    next:"先逐例对齐 8 个源任务的失败轨迹、patch 和更新后行为，给 7 个失败 patch 做原因归类，并与唯一成功 patch 对照；再决定是补充 updater 输入、修改 patch 生成方式，还是更换成 memory/skill 等更容易产生可测变化的更新表面。修好以后先在不打开隐藏旧任务的前提下生成一批全新的候选，确认有效更新比例达到预先冻结的资格要求；只有这一步通过，才打开旧能力回归测试并正式比较 A-3 与简单规则。"
  },
  "B-2":{
    scene:PARENT_SCENE_ZH["B-2"],
    progress:"生命周期：历史 P0 → 当前 HOLD。当前有 72 个记忆影响单元，其中 11 个已经确认“打开或关闭这条记忆会改变结果”；但专门用于 B-2 的“删掉一条记忆会让最终结论改变”案例是 0 个，隐藏旧任务没有打开。",
    observed:"B-2 需要的不是一般的记忆有效案例，而是可重复的“删除敏感”案例。当前 72 个单元里这类案例为 0，而预先要求至少 30 个，说明现有数据根本没有提供训练或比较记忆保留选择器所需的正例。",
    judgment:"现在不能说 B-2 的选择器失败，因为选择器还没有得到它要学习的现象。能确定的是：当前这张记忆影响表适合研究“记忆有没有影响”，不适合研究“哪条记忆删掉会改变结论”。",
    human:"希望人工重点判断两件事：第一，什么具体任务最容易自然产生“删掉一条经验就改变最终决策”的案例；第二，这类案例应该靠真实长期记忆积累获得，还是可以通过受控构造先验证方法可行性。不要在当前 0 正例的数据上继续调选择器。",
    next:"新建一个专门的删除敏感性数据收集：先只收集并复验“有/无某条记忆时最终动作或结论不同”的案例；达到预注册的至少 30 个可重复案例后，再冻结训练/留出划分，最后才训练 B-2 选择器并打开隐藏原任务。"
  },
  "B-3":{
    scene:PARENT_SCENE_ZH["B-3"],
    progress:"生命周期：历史 P0 → 当前 HOLD。已经做过合成筛查，也在 ALFWorld 中寻找真实的多记忆共同检索案例；但严格排除旧 source/target 和重复 target 后，只剩 5 个真正独立的新组合，低于预先要求的 6 对。",
    observed:"合成环境里可以看到“哪条记忆通过哪条路径造成干扰”的信号，但真实 ALFWorld 数据严格去掉旧任务、旧目标和重复目标后，只剩 5 个全新的独立共检索组合。样本量甚至没达到启动核心比较的最低门槛，所以现在没有资格判断复杂干扰定位器好不好。",
    judgment:"停止的是当前 ALFWorld 数据实例，不是“多条记忆一起出现会产生交互”这个问题。当前最可靠的结论只是：真实共检索案例太少，继续在同一批数据上扩模型会把重复样本当成证据。",
    human:"希望人工帮助选择新的数据来源：哪里会自然出现多条长期记忆同时被检索，而且能形成足够多彼此独立的新任务组合？优先判断换环境是否比继续挖 ALFWorld 更合理。",
    next:"换到新的共检索数据环境，先完全不训练方法，只检查是否有足够真实案例；拿到至少 6 个彼此独立、以前没见过的“记忆组合 × 目标任务”案例后，再冻结实验方案，比较“定位哪条/哪组记忆致害”与简单的逐条隔离或排序规则。"
  },
  "B-4":{
    scene:PARENT_SCENE_ZH["B-4"],
    progress:"生命周期：历史人工裁决 → 当前 MERGED。方法设计曾把每条经验限制为固定 6 个 sentinel 测试，但在进入独立核心实验前先做了问题归并审查。",
    observed:"B-4 要用的输入与 A-3 本质相同：都是拿有限的旧/未来任务证据，判断一条持久更新是否应该被接受。当前没有一组独立任务结果证明“更新对象是 memory”以后会产生 A-3 无法表达的新决策。",
    judgment:"因此没有必要再为 B-4 单独训练一个经验准入器。科学问题仍有用，但把它作为 A-3 的 memory 应用场景更清楚，也能避免两个方向重复消耗同一批实验。",
    human:"希望人工判断的是：memory 准入是否存在 A-3 通用回归检查无法处理的特殊信息，例如检索范围、记忆竞争或长期复用效应。如果没有这样的独有变量，就保持合并。",
    next:"后续若 A-3 重开，可把 memory admission 作为一个具体实验场景加入；只有出现通用回归门无法表达、且会改变接受/拒绝决定的 memory 特有证据，才重新独立立 B-4。"
  },
  "B-7":{
    scene:PARENT_SCENE_ZH["B-7"],
    progress:"生命周期：历史人工裁决 → 当前 MERGED。B-7 没有继续建立独立 P0，因为方法审查时已经发现它和 B-5 使用同一类反例、同一类适用条件，并做同一种“把可用范围越收越窄”的更新。",
    observed:"当前没有独立实验能把“给经验学习适用边界”和 B-5 的“遇到反例后收紧前置条件”区分成两个不同决策问题。两者最终都回答：这条经验在什么状态下还能安全使用。",
    judgment:"B-7 不是失败，而是被去重。它最有价值的部分是“显式显示经验适用边界”，现在作为 B-5 的表示/可解释组件保留。",
    human:"希望人工只检查一个问题：是否存在一种 B-7 边界表示能表达 B-5 单调前置条件无法表达的情况，并且这种差异会改变实际任务决策。如果没有，就不需要重开。",
    next:"继续在 B-5 下使用边界可视化和适用范围记录；只有出现 B-5 无法表示的新型非单调边界并有真实任务后果时，再单独评审 B-7。"
  },
  "C-3":{
    scene:PARENT_SCENE_ZH["C-3"],
    progress:"生命周期：历史人工裁决 → 当前 MERGED。该方向在独立实验前完成了问题去重：奖励含义随版本变化，本质上需要比较不同评价器版本对同一行为的评分，这正是 C-2 已经在做的事情。",
    observed:"当前没有一组独立结果说明“奖励含义是否保持不变”会给出不同于 C-2“评价器版本变化”检查的诊断或修复决定，因此继续单独跑实验只会重复同一套跨版本评分比较。",
    judgment:"C-3 保留为 C-2 的一个检查项：除了问评价器有没有漂移，还要问漂移后这个分数是否仍代表原来要优化的目标；不再作为独立论文方向。",
    human:"希望人工判断是否存在“评分器本身没漂移，但奖励语义仍发生目标替换”的具体任务案例。如果有，而且 C-2 的版本评分矩阵看不出来，才可能形成独立问题。",
    next:"先在 C-2 的审计里增加“这个分数是否仍代表原目标”的检查；只有拿到 C-2 无法解释的真实目标替换案例，才重开 C-3。"
  },
  "C-6":{
    scene:PARENT_SCENE_ZH["C-6"],
    progress:"生命周期：历史人工裁决 → 当前 MERGED。这个方向在独立实验前完成了最近工作与问题边界审查，没有再为“哪一步纠正真正起作用”单独启动新任务实验。",
    observed:"现有自纠正和信用分配研究已经直接处理“多步纠正轨迹里哪一步贡献成功”这一对象。当前没有发现一个 Agent 自进化特有、会改变归因结果的新变量。",
    judgment:"因此 C-6 不再单独成篇，但“把有效纠正动作编译成可复用动作/规则”的工程资产仍可供其他 C 类方向使用。",
    human:"希望人工关注是否出现真正持久化后的新问题：例如某一步当下有用，但写入长期系统后效果改变。如果只是普通轨迹信用分配，就不重开。",
    next:"把动作级归因作为其他自纠正实验的诊断工具使用；只有持久更新引入了现有信用分配无法解释的新现象时，再重新立题。"
  },
  "D-3":{
    scene:PARENT_SCENE_ZH["D-3"],
    progress:"生命周期：历史人工裁决 → 当前 MERGED。没有单独启动 D-3 的完整实验，因为它必须建立在 D-2 能稳定生成有学习价值的下一批任务之上，而这个前提本身尚未成立。",
    observed:"当前 D-2 的任务选择器还不能稳定优于简单的直接产出预测。上游课程生成都没有证明可靠时，继续研究“课程长期漂移”无法区分是监控方法问题，还是课程本身就不够好。",
    judgment:"D-3 作为 D-2 的监控维度保留：一旦自动课程真正可用，就同时记录任务分布是否越来越偏、是否遗漏真实薄弱能力。现在不单独占一个研究方向。",
    human:"希望人工先判断 D-2 的自动课程场景是否值得继续。如果以后有一个真实系统能连续多轮生成有效训练任务，再讨论什么漂移最危险、用什么指标监控。",
    next:"先解决 D-2 的任务生成/选择有效性；只有出现连续多轮有效自动课程后，才启动 D-3 的长期漂移测量。"
  },
  "E-1":{
    scene:PARENT_SCENE_ZH["E-1"],
    progress:"生命周期：历史 P0 → 当前 HOLD。已经冻结 16 个源工作流，每个比较 5 种局部编辑；但这张源表里只有 4/16 个工作流存在任何正向编辑，只有 3 个工作流能把不同编辑的效果排出唯一顺序。隐藏工作流没有打开。",
    observed:"我们想训练的是“看到新工作流后，选哪个编辑最可能有效”的编辑排序器，但源数据里大多数编辑效果都是并列或都不改善。只有 25% 的工作流提供可学习的排序信号，因此现在训练任何复杂排序方法都无法说明方法好坏。",
    judgment:"这不是 E-1 方法失败，而是 配对编辑数据表没有足够变化。当前可以确定的是：先要有一张不同编辑确实会产生不同结果的源表，才有资格比较复杂编辑策略。",
    human:"希望人工重点看 16×5 编辑表：为什么大多数编辑没有产生可排序差异？是编辑动作太弱、任务指标太粗，还是工作流本身对这些局部编辑不敏感？下一步应先改编辑集合还是换工作流场景。",
    next:"重新构造一张源工作流配对编辑表，先只检查“同一工作流的不同编辑是否产生稳定、非并列的真实效果”；达到预注册支持门后再冻结表，最后才训练 E-1 并打开完全未见工作流。"
  }
};
function parentBriefingCopy(idea,current,terminal,currentStatus,disposition) {
  const code=terminal?.code||idea.id;
  const override=language==="zh"?(PARENT_BRIEFING_ZH[code]||{}):{};
  const decision=String(currentParentDecisionRecord(terminal).decision||"");
  const reason=ideaStopReasonMeta(decision,currentStatus,terminal?.failure_layer||"");
  const merged=currentStatus==="merge";
  return {
    wanted:override.wanted||textOf(current.purpose||{}),
    why:override.why||disposition.detail||textOf(terminal?.terminal_reason||{}),
    learned:override.learned||(merged
      ? (language==="zh"?"该方向的有效部分已经并入更大的研究方向，不再作为独立论文重复推进。":"Its useful parts survive inside a larger direction rather than as a duplicate standalone paper.")
      : (language==="zh"?"当前证据帮助我们收窄了方法边界；后续只有新增证据满足重开条件才继续。":"The evidence narrows the method boundary; continuation requires new evidence that satisfies the reopen condition.")),
    reason,
  };
}
function parentOneMinuteCopy({idea,current,terminal,currentStatus,disposition,lifecycleStage,plainReopen,decisiveEvidence}) {
  if(language!=="zh") return null;
  const code=terminal?.code||idea.id;
  const fixed=PARENT_ONE_MINUTE_ZH[code];
  if(fixed)return fixed;
  const briefing=parentBriefingCopy(idea,current,terminal,currentStatus,disposition);
  const pilot=humanPilotSummary(idea,textOf(current.decisive_pilot||current.pilot||{}));
  const comparison=PARENT_SIMPLE_COMPARISONS_ZH[code];
  const comparisonEvidence=comparison
    ? `${(comparison.rows||[]).slice(0,2).map(row=>`${row.metric}：我们=${row.ours}；简单方法=${row.baseline}；差异=${row.delta}`).join("。")}${comparison.verdict?`。${comparison.verdict}`:""}`
    : "";
  const reason=briefing.reason?.key||"simple";
  const scene=PARENT_SCENE_ZH[code]||(pilot
    ? `${briefing.wanted} 具体怎么测：${pilot}`
    : `${briefing.wanted} 当前还没有进入一套独立任务实验；下面只说明已经确认的问题边界，不补造任务案例。`);
  const progress=comparisonEvidence
    ? `生命周期：${lifecycleStage} → ${humanParentFinalStatusLabel(currentStatus)}。实际已经完成公平对照：我们的方法和简单方法使用相同的数据、可见信息与测试预算，并在同一冻结留出数据上比较；结果如下。`
    : `生命周期：${lifecycleStage} → 当前${humanParentFinalStatusLabel(currentStatus)}。目前已完成问题、对照与最小验证设计；是否真正运行核心任务实验，以“实验实际看到了什么”为准，历史阶段本身不等于实验已完成。`;
  const observed=comparisonEvidence||briefing.why||decisiveEvidence||"当前没有可归纳为任务级结果的独立实验；现阶段只保留设计、文献或结构证据。";
  const judgment=reason==="support"
    ? `当前证据只足以说明这套数据、更新器或实验底座还不能公平检验方法，不能据此判定科学问题或方法失败。${briefing.learned}`
    : reason==="identify"
      ? `当前实验无法把观察到的结果归因到声称的新机制，因此继续放大同一实验也不会得到清楚结论。${briefing.learned}`
      : reason==="collision"
        ? `当前问题可能真实，但最近工作或成熟解释已经覆盖主要决策对象，现版本不足以作为独立论文继续。${briefing.learned}`
        : reason==="merge"
          ? `当前不再作为独立方向推进，但其中有效的机制、协议或审计资产已经保留到更大的研究方向。${briefing.learned}`
          : reason==="principle"
            ? `在当前有效证据范围内，关键科学预测被直接否定；除非出现能推翻这条证据的新结果，否则不重复同一方向。${briefing.learned}`
            : `${briefing.learned}`;
  const human=reason==="support"
    ? "希望人工优先判断：当前卡点究竟来自任务/数据不足、更新器没有产生有效变化，还是实验底座本身不适合检验这个问题；应该修上游条件，还是更换实验实现？"
    : reason==="identify"
      ? "希望人工优先判断：还缺哪个对照或干预，才能把本文声称的机制与更简单解释真正区分开；如果使用相同可见信息时仍然区分不了，就不值得继续加算力。"
      : reason==="collision"
        ? "希望人工优先判断：最近工作之后是否还剩一个会改变实验设计或实际决策的不可约差异；如果只剩换术语或重组组件，就不重开。"
        : reason==="merge"
          ? "希望人工判断保留下来的部分最适合成为哪个父方向的组件、基线或审计规则，以及是否还有必要保留独立实验入口。"
          : reason==="principle"
            ? "希望人工检查真正决定停止的反证是否充分、适用范围是否写得过宽；只有发现反证本身有问题，才考虑重开。"
            : "希望人工检查复杂方法相对最强简单方法是否还存在一个真正会改变决策的变量；如果没有，就优先复用简单方法。";
  const next=reason==="support"
    ? "先补齐或替换当前缺失的数据、有效变化或实验环境，再用全新任务做前置资格检查；只有资格通过，才进入核心方法比较。"
    : reason==="identify"
      ? "先设计一个最小对照，让本文机制和最强替代解释必须给出不同结果；如果仍然区分不了，就不继续扩大实验。"
      : reason==="collision"
        ? "先写出一个现有工作覆盖不了、而且会改变实验或实际决策的具体差异；没有这个差异就保持关闭。"
        : reason==="merge"
          ? "继续把可复用部分作为父方向资产使用；只有父方向无法表达的新现象真实出现，才重新独立立题。"
          : reason==="principle"
            ? "保持停止。只有新的独立结果直接推翻当前反证，才重新人工评审。"
            : "默认采用当前更简单的方法。只有新的冻结任务里，复杂方法在相同输入和预算下稳定做出更好的决定，才重新评审。";
  return {scene,progress,observed,judgment,human,next};
}
function humanReviewStatusLabel(status) {
  const terminalLabels = {
    p0:{zh:"已进入 P0",en:"Entered P0"},
    "p0-ready":{zh:"P0 就绪",en:"P0-ready"},
    merge:{zh:"已合并",en:"Merged"},
    drop:{zh:"已弃掉",en:"Dropped"},
  };
  const row = terminalLabels[status] || humanReviewData().status_labels?.[status] || {zh:status,en:status};
  return textOf(row);
}
function humanReviewStatusTone(status) {
  if (status === "p0" || status === "p0-ready") return "ready";
  if (status === "hold") return "paused";
  if (status === "stop") return "dropped";
  if (status === "merge") return "merged";
  if (status === "drop") return "dropped";
  if (status === "method-redesign") return "redesign";
  return "paused";
}
function currentFinalIdeaById(id) {
  return (window.CURRENT_FINAL_IDEAS?.ideas || []).find((idea) => (idea.idea_id || idea.id) === id) || null;
}
function experimentStateCopy(status) {
  if (status === "p0") return language === "zh"
    ? {title:"P0 生命周期已进入",note:"P0 表示方法、对照、真值、最小实验、Stop 与资源合同已经冻结；不等于真实实验已经运行。只有 GPU-0、Pre-P0、Updater Competence、Pre-Experiment 8/8 与 runtime/throughput 全部放行后，execution_authorized 才能为 true。"}
    : {title:"P0 lifecycle entered",note:"P0 means the method, baseline, truth, minimum experiment, stop rule, and resource contract are frozen; it does not imply execution. execution_authorized remains false until GPU-0, Pre-P0, updater competence, all eight Pre-Experiment gates, and runtime/throughput checks clear."};
  if (status === "p0-ready") return language === "zh"
    ? {title:"最小 P0 怎么做",note:"方法定义已经冻结到可证伪版本；只运行下面的最小 P0，命中 stop 条件就直接终止，不再自动生成修订 child。"}
    : {title:"Minimum P0",note:"The mechanism is frozen to a falsifiable version. Run only the minimum P0 below; if a stop condition fires, terminate rather than spawning an automatic repair child."};
  if (status === "merge" || status === "drop") return language === "zh"
    ? {title:"终态，不再独立执行",note:"该方向已经进入人工终态；历史实验设计仅作追溯，不再进入自动修订、独立 P0 或 advisor standalone 队列。"}
    : {title:"Terminal; no standalone execution",note:"This direction is human-terminal. Historical experiment design is traceability only and cannot re-enter automatic repair, standalone P0, or advisor queues."};
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
const PAPER_IDEA_ZH_RESOURCE = {
  "same candidate update pool":"相同候选更新池",
  "same frozen probe suite":"相同冻结探针套件",
  "same number of probe-task executions for estimation":"用于估计的探针任务执行次数相同",
  "same held-out evaluation tasks":"相同留出评测任务",
  "same model capacity and architecture":"模型容量与架构相同",
  "same total agent calls":"Agent 总调用次数相同",
  "same historical execution outcomes and training windows":"相同历史执行结果与训练窗口",
  "same probe pool and probe-lineage/update-diff features":"相同探针池，以及相同探针谱系/更新差分特征",
  "same total probe budget k per version":"每个版本使用相同的总探针预算 k",
  "same execution-cost budget per version":"每个版本使用相同执行成本预算",
  "same selector architecture, capacity, and parameter count":"选择器架构、容量与参数量相同",
  "same optimizer, minibatches, and training steps":"优化器、小批量与训练步数相同",
  "same atomic-update pool and held-out compositions":"相同原子更新池与留出组合",
  "same execution labels":"相同执行标签",
  "same calls/tokens per composition":"每个组合的调用数与 Token 预算相同",
  "matched predictor capacity":"预测器容量匹配",
  "same repair/search budget":"修复/搜索预算相同",
  "identical version-history sequences and update dependency/timestamp annotations":"版本历史序列、更新依赖与时间戳标注完全相同",
  "identical counterfactual replay probe set and replay outcomes":"反事实回放探针集与回放结果完全相同",
  "identical rollback metadata format and rollback-target probes":"回滚元数据格式与回滚目标探针完全相同",
  "identical verifier access and number of verifier queries":"验证器访问权限与查询次数完全相同",
  "identical fixed canonical-state compression budget (token count)":"固定规范状态的压缩预算（Token 数）完全相同",
  "identical base model, capacity, decoding settings, llm calls, and token budget":"基础模型、容量、解码设置、LLM 调用和 Token 预算完全相同",
  "identical memory capacity k":"记忆容量 K 完全相同",
  "identical retrieval top-m and retrieval interface":"检索 top-M 与检索接口完全相同",
  "identical observation streams and candidate memory entries":"观测流与候选记忆条目完全相同",
  "identical probe/query sets and gold labels":"探针/查询集合与金标标签完全相同",
  "identical downstream task calls and tokens per query":"下游任务调用数与每次查询 Token 数完全相同",
  "identical frozen agent model and decoding configuration per condition":"每个条件下的冻结 Agent 模型与解码配置完全相同",
  "same top-m memories":"相同 top-M 记忆",
  "same nested interventions and labels":"相同嵌套干预与标签",
  "same repair actions":"相同修复动作集合",
  "same calls/tokens/intervention budget":"调用数、Token 与干预预算相同",
  "same frozen future-reuse evaluation":"相同的冻结未来复用评测",
  "same frozen predicate vocabulary for all arms":"所有实验臂使用相同冻结谓词词表",
  "same training counterexample sets":"训练反例集合相同",
  "same positive-state sets":"正例状态集合相同",
  "same constraint-deletion traces":"约束删除轨迹相同",
  "same rule-complexity budget (number of rules, clauses, or tree nodes)":"规则复杂度预算相同（规则、子句或树节点数量）",
  "same model calls and token budget":"模型调用数与 Token 预算相同",
  "same frozen response pool":"相同冻结响应池",
  "same independent anchors/labels":"相同独立锚点/标签",
  "same evaluator calls/tokens":"评价器调用数与 Token 预算相同",
  "same rubric atoms/interventions":"相同 Rubric 原子与干预",
  "matched gate capacity and training steps":"门控容量与训练步数匹配",
  "actor frozen during evaluator repair":"评价器修复期间 Actor 保持冻结",
  "same workflow pool and traces":"工作流池与轨迹相同",
  "same candidate edit space":"候选编辑空间相同",
  "same programmatic verifier":"相同程序化验证器",
  "same real-intervention budget":"真实干预预算相同",
  "same llm/tool calls and tokens":"LLM/工具调用数与 Token 预算相同",
  "same api/motif holdout and second-model transfer":"相同 API/模体留出与第二模型迁移设置",
  "identical predefined memory types and provenance/function definitions":"预定义记忆类型及来源/功能定义完全相同",
  "identical training and held-out co-retrieved complete typed sets":"训练与留出的共同检索完整类型集合完全相同",
  "identical randomized/enumerated permutation-outcome data and evaluation-feedback counts":"随机化/枚举的排列结果数据与评测反馈计数完全相同",
  "matched parameter/clause capacity and regularization/mdl budget":"参数/子句容量以及正则化/MDL 预算匹配",
  "identical number of training permutations and optimizer steps/minibatches where applicable":"训练排列数量以及适用时的优化步数/小批量完全相同",
  "identical exact solver with identical candidate budget for solver cells":"求解器单元使用完全相同的精确求解器与候选预算",
  "identical source/target documentation and schemas":"源/目标文档与模式完全相同",
  "identical n actively selected target probes (same probe selection policy inputs)":"主动选择的 N 个目标探针完全相同（探针选择策略输入相同）",
  "identical p/e/x representational capacity and operator-graph compilation pipeline":"P/E/X 表征容量与算子图编译流水线完全相同",
  "identical tokens and model calls for any llm components":"所有 LLM 组件的 Token 与模型调用完全相同",
  "identical model capacity, optimizer, minibatches, and training steps for the learned arm's fitting budget accounted against the baseline's instantiation budget":"学习臂的模型容量、优化器、小批量与训练步数完全匹配，并将拟合预算计入基线实例化预算",
  "identical frozen-after-n-probes protocol with no test-time relearning":"N 次探针后冻结的协议完全相同，测试时均不再学习",
  "identical structured diffs over prompt, memory, skills, workflows, and dependencies":"Prompt、记忆、技能、工作流与依赖的结构化差分完全相同",
  "identical canary library and scoring":"金丝雀测试库与评分方式完全相同",
  "identical intervention-derived labels and environment logs":"干预得到的标签与环境日志完全相同",
  "identical llm calls, tokens, and wall-clock":"LLM 调用、Token 与墙钟预算完全相同",
  "identical reauthorization budget":"重授权预算完全相同",
  "identical independent safety harness":"独立安全测试框架完全相同"
};
const PAPER_IDEA_ZH_TECH = {
  "Frozen heterogeneous open-weight critic plus environment/tool ground truth whenever available.":"冻结的异构开放权重 Critic，并在可用时结合环境/工具独立真值。"
};
const PAPER_IDEA_ZH_TERMINAL = {
  "self-label-confidence-flow":{
    mechanism:"维护冻结的标签谱系图与有效证据权重；每个伪标签在后续轮次中获得持久的接纳、隔离或降权动作。",
    gate:"要求同祖先错误富集显著超过置信度匹配的独立来源，并且相对最强直接基线在留出决策上至少有 20% 分歧。",
    baseline:"相同特征、容量匹配的直接历史分类器，并比较置信度、EMA 教师和简单来源折扣规则。",
    minimum:"冻结 4–6 轮、至少 200 个带谱系的标签决策；留出祖先与后续轮次，在接纳数量匹配下比较错误接纳、干净标签保持和下一轮效用。",
    stop:"若没有谱系错误富集，或同信息直接分类/简单来源折扣基线等效，则停止或并入普通伪标签过滤。"
  },
  "self-correction-collapse-detector":{
    mechanism:"根据失败签名、上一纠错模式与验证器增量，冻结一个在重新规划、检索、改写、回滚和停止之间选择的模式转移策略；测试时不再训练。",
    gate:"要求至少 3 种纠错模式、存在非平凡顺序效应，并且相对最强浅层规则在留出决策上至少有 20% 分歧；否则并入 A-2/A-3。",
    baseline:"相同状态信息下的深度 3 CART/有限状态规则、固定顺序、重复上限、熵启发式与 A-2 风格停止规则，调用量完全匹配。",
    minimum:"使用至少 30 个失败案例、每例最多 3 轮纠错；冻结候选轨迹，按失败族留出，在调用数匹配下评估恢复和回退。",
    stop:"若重复上限、浅层 CART 或 A-2 风格规则在相同状态信息与调用预算下追平，则停止或合并。"
  },
  "intervention-validated-self-correction":{
    mechanism:"共享纠错生成器；计算删除/插入的必要性—充分性签名，并在打开隐藏未来任务之前冻结提交/拒绝门。",
    gate:"要求相对 A-3/简单阈值至少有 20% 的提交决策分歧，并且现有轨迹上还能看到额外的未来收益/伤害信号。",
    baseline:"A-3 回归面板、当前收益、仅成功准入，以及使用相同必要性/充分性特征、相同调用量和相同接纳数量的简单阈值。",
    minimum:"冻结至少 24 个候选、8 个探针和 24 个隐藏任务；拉平干预预算，在接纳数量匹配下比较有害提交与保留收益。",
    stop:"若 A-3 或相同特征简单阈值等效，则并入 A-3；若干预签名不能预测未来提交效用，则停止。"
  },
  "failure-frontier-curriculum":{
    mechanism:"冻结类型化任务变异库与选择器；每个版本根据当前失败签名选择变异算子来生成后续训练任务，不进行目标奖励搜索。",
    gate:"要求至少 3 类变异算子的效用排序会随版本改变，并且相对直接收益/失败频率基线在留出版本上存在非零 regret 差异。",
    baseline:"均匀 fuzzing、失败频率、uncertainty sampling、D-1 的 verifier-filtered generation，以及使用相同特征的直接变异收益预测器。",
    minimum:"使用至少 3 个连续 Agent 版本和 30 个类型化变异算子，固定训练 Token；留出最终版本/任务族，测边界覆盖与下一版本效用。",
    stop:"若没有跨版本排序变化，或最强直接/简单选择器等效，则并入普通课程或停止。"
  },
  "world-model-error-gated-learning":{
    mechanism:"使用独立真实转移；只有会改变决策的残差才允许更新世界模型残差适配器，策略始终冻结。",
    gate:"在精确动力学 MDP/Gridworld 中，decision-changing 标签不得退化为误差幅度或 value-aware 打分，并且相对最强基线至少有 20% 候选决策分歧。",
    baseline:"全量学习、残差幅度 top-k、等数量随机、value-aware/CVAML 风格加权，以及同数据的直接动作分歧选择。",
    minimum:"冻结一个小型世界模型与策略，收集至少 100 个转移误差并留出状态区域；只更新残差适配器，使用的转移不超过 learn-all 的 50%。",
    stop:"若 value-aware/CVAML 或直接动作分歧等效，或真正会改变决策的案例过少，则停止。"
  },
  "irreversible-action-counterfactuals":{
    mechanism:"对失败反事实做前驱删除/替换，归纳“状态谓词 → 禁止动作/必需检查点”条款，并由外部执行器强制执行。",
    gate:"有限状态穷举真值必须出现风险相近、但最小前驱约束不同的案例，并在留出拓扑上与 direct shield 产生决策差异。",
    baseline:"同标签、容量匹配的直接风险分类器/Shield、人工不可逆动作掩码，以及相同 simulator 调用和运行检查预算下的最近失败轨迹记忆。",
    minimum:"使用至少 40 个不可逆失败和 20 个匹配安全案例，按拓扑留出；冻结条款后关闭 simulator，测危险进入、误阻塞、成功率与成本。",
    stop:"若相同容量 direct shield 在留出安全—误阻塞前沿上追平，或条款需要更强运行时 Oracle，则停止或并入通用 Shield。"
  },
  "recovery-conditioned-experience":{
    mechanism:"从同一起点的正常/扰动成功轨迹对中提取最早恢复状态—动作残差；只有在至少两个上下文中复现后，才写入恢复算子及其适用谓词。",
    gate:"先满足至少 100 对同起点成功轨迹、直接状态残差与 success-only writer 审计；至少 20% 的轨迹对应支持可跨身份/上下文复用的恢复残差算子。",
    baseline:"完整恢复 episode 记忆、最近轨迹检索、同轨迹对直接条件恢复策略，以及在记忆/Token/调用匹配下的 success-only writer。",
    minimum:"现象门通过后冻结 10–20 个算子，在留出扰动类型/场景上关闭 simulator，评估恢复、额外步数、干净任务干扰与记忆成本。",
    stop:"若恢复残差不能稳定复现，或同数据 direct recovery/完整轨迹记忆在匹配预算下等效，则停止。"
  }
};
const PAPER_IDEA_ZH_METHOD_ASSET = {
  "api-error-semantic-adapter":"API 错误语义适配器",
  "applicability-bounded-lessons":"适用性有界经验",
  "certified-out-of-span-interaction-inverter-v53":"认证跨度外交互逆转器 v5.3",
  "compiler-residual-contract-editor-v53":"编译器残余合同编辑器 v5.3",
  "correction-action-causal-compiler":"纠错动作因果编译器",
  "failure-localization-before-reflection":"反思前失败定位",
  "local-counterexample-memory-repair":"局部反例记忆修复",
  "filtered-chronological-evaluator-state-v53":"过滤式时序评价器状态 v5.3",
  "heterogeneous-critic-disagreement":"异构 Critic 分歧",
  "memory-interaction-clause-learner":"记忆交互条款学习器",
  "monotone-applicability-specializer-v4":"单调适用性专化器 v4",
  "nested-pathway-memory-repair":"嵌套路径记忆修复",
  "probe-mutation-retirement-policy":"探针变异退役策略",
  "restoration-clause-induction-v5":"恢复条款归纳 v5",
  "rubric-intervention-sparse-solver":"Rubric 干预稀疏求解器",
  "update-composition-repair-compiler":"更新组合修复编译器",
  "update-history-semantic-compactor":"更新历史语义压缩器",
  "workflow-repair-grammar-v5":"工作流修复语法 v5",
  "update-trust-region":"更新信任域",
  "compositional-update-compatibility":"组合更新兼容性",
  "contradiction-preserving-consolidation":"矛盾保持式巩固"
};
const PAPER_IDEA_ZH_REFINEMENT = {
  "advance-to-pre-p0-offline-gate":"推进至 GPU 前离线门",
  "hold-after-fresh-collision":"最新碰撞审查后暂缓",
  "phenomenon-gate-before-standalone":"独立推进前先通过现象门",
  "merge-unless-disagreement-found":"若找不到稳定分歧则合并",
  "merge-into-A3":"并入 A-3",
  "hold-reality-check":"等待现实性检查",
  "advance-to-pre-p0-reality-gate":"推进至 GPU 前现实性门",
  "advance-to-pre-p0-objective-gate":"推进至 GPU 前目标门",
  "merge-into-E1":"并入 E-1",
  "hold-scenario-check":"等待场景核验",
  "hold-reality-and-collision-check":"等待现实性与碰撞核验",
  "phenomenon-gate-before-learning":"学习前先通过现象门"
};
function localizedPaperIdeaTechnical(value) {
  const raw = String(value || "");
  if (language !== "zh" || !raw) return raw;
  return PAPER_IDEA_ZH_TECH[raw] || raw;
}
function localizedMatchedResource(value) {
  const raw = String(value || "");
  if (language !== "zh" || !raw) return raw;
  return PAPER_IDEA_ZH_RESOURCE[raw.toLowerCase()] || raw;
}
function localizedPaperIdeaMethodAsset(value) {
  const raw = String(value || "");
  if (language !== "zh" || !raw) return raw;
  return PAPER_IDEA_ZH_METHOD_ASSET[raw] || raw;
}
function localizedRefinementRecommendation(value) {
  const raw = String(value || "");
  if (language !== "zh" || !raw) return raw;
  const zh = PAPER_IDEA_ZH_REFINEMENT[raw];
  return zh ? `${zh}（${raw}）` : raw;
}
function renderMatchedResourceList(items) {
  if (!Array.isArray(items) || !items.length) return "";
  const visible = items.slice(0,6).map((item) => `<li>${esc(localizedMatchedResource(item))}</li>`).join("");
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
    "world-model-error-gated-learning":"固定能进入更新的 transition 数量。对每条真实 transition，把 world-model 预测单独替换成真值，检查冻结 policy 的动作 / 风险 / 恢复决策是否会翻转；只优先学习真正会改变决策的 transition，再和 uniform、最大误差、uncertainty、AAWM-style 选样比较。",
    "memory-half-life":"在分段平稳的 ALFWorld 或 AndroidWorld 任务流中，在记忆容量、检索调用、复验调用和任务顺序完全一致的条件下，对比效用复验策略、SF-AMS、净价值筛选、固定衰减和 FIFO。重点不是时间久不久，而是复用机会出现时记忆的真实效用是否已经漂移。",
    "self-label-confidence-flow":"在同一偏好数据集上运行 4 轮自标注，并使用两个开放模型族；固定生成样本与 Judge 调用，只更新同一个小于 50M 参数的 Reward Head。比较无权重标签、当前轮置信度、CREAM 一致性和谱系置信度，评估留出人工标签错误 AUROC、校准误差、外部偏好准确率和逐轮退化。",
    "self-correction-collapse-detector":"在 GSM8K 与 HumanEval 上，使用完全相同的基础答案和纠错轨迹，比较三分量模式转移策略、纠错率、破坏率、置信度变化和任务难度，预测“再做一轮纠错是否真正有帮助”；重点检验浅层规则是否已经足够。",
    "intervention-validated-self-correction":"收集匹配的 GSM8K 与 ALFWorld 失败案例，在相同候选干预与 rollout 预算下比较自由文本 critique、CRITIC、InT、REFLECT replay 与本文的必要性/充分性干预门；将接纳的纠错写入相同记忆或小于 50M 参数适配器，并在留出任务模板上测试迁移。",
    "irreversible-action-counterfactuals":"在一个具有精确不可逆转移标记的沙箱中，给所有方法相同的 simulator discovery 预算来建立风险记忆；随后冻结记忆并在测试时关闭 simulator，比较条款库、在线世界模型规划、已执行危险事件记忆、语言反思和无记忆基线在未见任务上的安全进入、误阻塞、成功率与调用成本。",
    "recovery-conditioned-experience":"在最终都成功的 LIBERO 扰动 episode 中，用独立计算的持续重汇合与残余状态探针划分轨迹；在固定记忆容量下写入相同数量的经验，并在第二个 VLA 上比较未来复用伤害、恢复成功与额外步数，对照 endpoint-only Dejavu、PEAM-style 准入和直接恢复策略。",
    "contradiction-preserving-consolidation":"在具有程序化成功谓词的 ALFWorld 中，固定 Actor 与更新内容，只改变针对有状态违规的合并规则；与安全 Shield、知识编辑一致性约束和回归门控做预算匹配对照，并在隐藏谓词组合、第二个 LLM 脚手架和回滚有效性上评测。",
    "counterexample-generating-curriculum":"先生成一个所有实验臂共享的候选任务池。比较包装器、结果验证器、D-2 的现有失败前沿，以及学习型边界不确定性 + 反事实干预选择器；固定候选池、执行预算和 Agent，评测边界覆盖、错误接纳、训练效率、后续任务收益，以及学习型方法相对简单未见性指标的额外价值。"
  };
  const fallbackZh = {
    "In ALFWorld with programmatic success predicates, keep the actor and update fixed; change only the consolidation rule for stateful violations. Compare with safety shields, knowledge-editing consistency constraints, and regression gating under matched budgets. Evaluate hidden predicate compositions, a second LLM scaffold, and rollback validity.":"在具有程序化成功谓词的 ALFWorld 中，固定 Actor 与更新内容，只改变针对有状态违规的合并规则；与安全 Shield、知识编辑一致性约束和回归门控做预算匹配对照，并在隐藏谓词组合、第二个 LLM 脚手架和回滚有效性上评测。",
    "Generate one common candidate-task pool, score every task by adjacent-checkpoint discrimination, current success probability, failure provenance, and validation-gradient alignment; compare wrappers, outcome verifiers, D-2's existing failure frontier, and a learned boundary-uncertainty + counterfactual-intervention selector. Freeze pool, execution budget, and agent; evaluate boundary coverage, false admission, training efficiency, future-task gain, and learned-vs-simple novelty delta.":"先生成一个所有实验臂共享的候选任务池。按相邻检查点区分度、当前成功概率、失败来源和验证梯度一致性为任务打分；比较包装器、结果验证器、D-2 的现有失败前沿，以及学习型边界不确定性 + 反事实干预选择器。冻结候选池、执行预算和 Agent，评估边界覆盖、错误接纳、训练效率、后续任务收益，以及学习型方法相对简单未见性指标的额外价值。"
  };
  const en = {
    "update-trust-region":"Take a batch of candidate updates, measure how behavior changes on fixed probes, then use hidden original tasks to see which updates actually cause regressions. Compare admission by current gain, edit size, and behavioral shift. Continue only if behavioral shift blocks harmful updates more accurately without rejecting too many useful ones.",
    "budgeted-evolution-controller":"Run the same tasks with a fixed update count and with a controller that chooses continue, rollback, or stop. Compare calls and regressions at similar final success. Stop if the controller does not save substantial calls or saves calls only by hurting performance.",
    "outcome-equivalent-trajectory-contrast":"Freeze distinct valid process families that reach the same successful outcome and use one extractor for candidate lessons. Instead of textual consensus, run memory OFF/ON interventions with leave-one-process-family-out validation; persist only lessons with positive mean utility and non-harmful worst-process effect. Compare against consensus, single-trajectory, and utility-only admission at matched replay budget.",
    "workflow-generalization-certificate":"Replace the old certificate with a paired edit-effect editor: learn from true before/after execution deltas of typed local edits on source workflows, freeze the editor, and on unseen APIs/task graphs forbid candidate trials and allow exactly one direct edit commit. Compare with Agentic Predictor, nearest-neighbor edit reuse, and failure heuristics.",
    "world-model-error-gated-learning":"Fix the number of transitions allowed into updates. For each true transition, replace only the world-model prediction with truth and test whether the frozen policy changes its action, risk, or recovery decision. Prioritize decision-switch transitions and compare with uniform, largest-error, uncertainty, and AAWM-style selection."
  };
  const fuzzyFallbackZh = fallbackZh[fallback]
    || (String(fallback).startsWith("Generate one common candidate-task pool") ? "先生成一个所有实验臂共享的候选任务池。按相邻检查点区分度、当前成功概率、失败来源和验证梯度一致性为任务打分；比较包装器、结果验证器、D-2 的现有失败前沿，以及学习型边界不确定性 + 反事实干预选择器。冻结候选池、执行预算和 Agent，评估边界覆盖、错误接纳、训练效率、后续任务收益，以及学习型方法相对简单未见性指标的额外价值。" : "")
    || (String(fallback).startsWith("In ALFWorld with programmatic success predicates") ? "在具有程序化成功谓词的 ALFWorld 中，固定 Actor 与更新内容，只改变针对有状态违规的合并规则；与安全 Shield、知识编辑一致性约束和回归门控做预算匹配对照，并在隐藏谓词组合、第二个 LLM 脚手架和回滚有效性上评测。" : "");
  return language === "zh" ? (zh[id] || fuzzyFallbackZh || fallback) : (en[id] || fallback);
}
function humanMetricSummary(idea, fallback = "") {
  const id = idea.id || idea.idea_id || "";
  const zh = {
    "update-trust-region":"重点看三件事：坏更新识别得准不准、隐藏任务最坏回退有多大、好更新被误拒绝多少。",
    "budgeted-evolution-controller":"重点看同等任务成功率下节省了多少调用、是否减少无效更新轮次，以及跨任务后还能不能保持这种节省。",
    "outcome-equivalent-trajectory-contrast":"重点看同 replay 预算下 future-task success、负迁移率和 worst-process effect；utility-only 若等效就停止 process-invariance 主张。",
    "workflow-generalization-certificate":"重点看 hidden workflow 零搜索直接 edit 后的真实成功增量、坏 edit 率和执行数；absolute predictor 若等效就停止。",
    "world-model-error-gated-learning":"重点看相同 transition-update 数下的任务成功、action regret、风险 / 恢复错误，以及 decision-switch 选样是否比误差大小更省更新。",
    "memory-half-life":"重点看相同审计比例下未来复用的有害保留、正向记忆误隔离、保留收益与审计成本；若简单 recency/frequency 规则更好，就停止学习型 hazard。",
    "self-label-confidence-flow":"重点看后续轮错误接纳率、干净标签保持、下一轮效用，以及谱系信息相对相同特征直接分类器是否提供稳定增益。",
    "self-correction-collapse-detector":"重点看留出失败族上的恢复率、回退率、调用数和模式选择分歧；若 depth-3 CART/有限状态规则等效，就停止学习型控制器。",
    "intervention-validated-self-correction":"重点看相同接纳数量下的有害持久提交、保留收益和未来任务效用；若 A-3 或相同特征简单阈值等效，就并回 A-3。",
    "irreversible-action-counterfactuals":"重点看 simulator 关闭后的不可逆失败率、误阻塞、任务成功与运行成本；同容量 direct shield 若等效就停止条款机制。",
    "recovery-conditioned-experience":"重点看留出扰动类型/场景上的恢复成功、额外步数、干净任务干扰与记忆成本；若直接恢复策略或完整轨迹记忆等效就停止。",
    "contradiction-preserving-consolidation":"重点看隐藏谓词组合上的成功保持、违规率、回滚有效性，以及第二个 LLM 脚手架上的迁移；若简单安全 Shield 或一致性约束等效，就停止独立方法主张。",
    "counterexample-generating-curriculum":"重点看边界覆盖、错误接纳率、相同执行预算下的训练效率与后续任务收益；若简单未见性/失败频率选择器等效，就停止学习型课程选择器。"
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
  const rawMetric = textOf(idea.decisive_metric || rich.decisive_metric || protocol.main_table || idea.learning_signal || rich.learning_signal || {});
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
  const verifier = localizedPaperIdeaTechnical(protocol.critic_or_verifier || "");
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
    <header><div><h4 data-toc="false">${esc(state.title)}</h4><p>${esc(state.note)}</p></div><span>${esc(meta.status === "new-review" ? (language === "zh" ? "待讨论" : "REVIEW") : humanReviewStatusLabel(meta.status))}</span></header>
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
function renderTerminalDecision(ideaId) {
  const terminal = terminalParentState(ideaId);
  if (!terminal) return "";
  const absorbed = terminal.absorbed_children || [];
  const zhOverride = language === "zh" ? (PAPER_IDEA_ZH_TERMINAL[ideaId] || {}) : {};
  const mergeTarget = terminal.merge_into ? `<span><b>${language === "zh" ? "并入" : "Merge into"}</b><span title="${esc(terminal.merge_into)}">${esc(language === "zh" ? localizedPaperIdeaMethodAsset(terminal.merge_into) : terminal.merge_into)}</span></span>` : "";
  const mechanism = zhOverride.mechanism || textOf(terminal.final_parent_mechanism || {});
  const gate = zhOverride.gate || textOf(terminal.pre_p0_gate || {});
  const baseline = zhOverride.baseline || textOf(terminal.strongest_baseline || {});
  const minimum = zhOverride.minimum || textOf(terminal.minimum_p0 || {});
  const stop = zhOverride.stop || textOf(terminal.exact_stop || {});
  const children = absorbed.length ? `<div class="terminal-child-list"><b>${language === "zh" ? "已吸收子方法" : "Absorbed children"}</b>${absorbed.map((id) => `<span title="${esc(id)}">${esc(localizedPaperIdeaMethodAsset(id))}</span>`).join("")}</div>` : "";
  const finalState = humanParentFinalState(terminal);
  const reopen = textOf(terminal.reopen_condition || {}) || (["drop","merge","stop"].includes(finalState)
    ? (language === "zh" ? "只有新的第一手或独立证据在信息、预算和最强同信息基线完全匹配后推翻当前终态边界，才重新人工评审；改名、换术语或重复同一实验不足以重开。" : "Reopen human review only if new primary or independent evidence overturns the current terminal boundary after fully matching information, budget, and the strongest same-information baseline; renaming or repeating the same test is insufficient.")
    : (language === "zh" ? "若前置门或精确终止条件被新的可核验事实实质改变，需重新回到人工评审；历史阶段本身不自动授权继续。" : "Return to human review only if new verifiable facts materially change the pre-gate or exact-stop condition; historical stage alone grants no authority."));
  const disposition = humanParentEvidenceDisposition(terminal, finalState);
  const reason = disposition.detail || textOf(terminal.terminal_reason || {});
  const dispositionCode = disposition.code ? `<small>${esc(disposition.code)}</small>` : "";
  return `<section class="terminal-decision terminal-${esc(finalState)}"><header><div><b>${mechanism}</b><p>${reason}</p></div><strong>${esc(humanParentFinalStatusLabel(finalState))}</strong></header><div class="terminal-evidence-disposition tone-${esc(disposition.tone)}"><div><b>${language === "zh" ? "最新证据处置" : "Latest evidence disposition"}</b><span>${esc(disposition.label)}</span></div>${dispositionCode}</div><details class="terminal-technical-audit"><summary>${language === "zh" ? "查看原始门禁、最强对照与精确终止条件" : "Inspect raw gates, strongest baseline, and exact stop"}<small>${language === "zh" ? "技术审计层" : "technical audit layer"}</small></summary><div class="terminal-decision-grid">${mergeTarget}${gate ? `<span><b>${language === "zh" ? "Pre-P0 / 前置门" : "Pre-P0 gate"}</b>${gate}</span>` : ""}${baseline ? `<span><b>${language === "zh" ? "最强对照" : "Strongest baseline"}</b>${baseline}</span>` : ""}${minimum ? `<span><b>${language === "zh" ? "最小 P0" : "Minimum P0"}</b>${minimum}</span>` : ""}${stop ? `<span><b>${language === "zh" ? "精确终止条件" : "Exact stop"}</b>${stop}</span>` : ""}<span><b>${language === "zh" ? "什么情况下重开" : "Reopen only if"}</b>${esc(reopen)}</span></div>${children}</details></section>`;
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
  const terminal = terminalParentState(idea.id);
  const historicalStatus = terminal?.terminal_state || meta.status;
  const currentStatus = terminal ? humanParentFinalState(terminal) : meta.status;
  const disposition = humanParentEvidenceDisposition(terminal || {}, currentStatus);
  const briefing = parentBriefingCopy(idea,current,terminal,currentStatus,disposition);
  const tone = humanReviewStatusTone(currentStatus);
  const code = terminal?.code || meta.code || idea.id;
  const revivedFromDrop = (terminal?.revival_history || []).some((row) => row.prior_terminal_state === "drop");
  const lifecycleStage = historicalStatus === "p0"
    ? (revivedFromDrop ? (language === "zh" ? "历史 DROP 后重开，并曾进入 P0" : "Reopened after historical DROP and entered P0") : (language === "zh" ? "历史上曾进入 P0" : "Historically entered P0"))
    : historicalStatus === "p0-ready" ? (language === "zh" ? "历史上曾达到 Pre-P0 / P0-ready" : "Historically reached Pre-P0 / P0-ready")
    : (language === "zh" ? "历史人工裁决已形成" : "Historical human decision recorded");
  const experimentAuthority = Number(projectStatusState().headline?.launchable_formal_experiments || 0);
  const canonicalItem = canonicalResearchItemByCode(code) || {};
  const primaryAction = canonicalItem.primary_next_action || {};
  const primaryActionClass = String(primaryAction.action_class || "INTERNAL_REVIEW_REQUIRED");
  const primaryActionText = language === "zh" ? (primaryAction.action_zh || primaryAction.action || "") : (primaryAction.action || primaryAction.action_zh || "");
  const canonicalReview = canonicalHumanReviewData().ideas?.[idea.id] || {};
  const humanOpinion = textOf(canonicalReview.opinion || meta.feedback || {});
  const originalNumber = Number(canonicalReview.original_number || 0);
  const humanRecommendation = canonicalReview.category || "unreviewed";
  const iteration = current.redesign_iteration || {};
  const iterationSummary = textOf(iteration.summary || {});
  const finalRefinement = current.final_refinement || {};
  const finalRecommendation = String(finalRefinement.recommendation || "");
  const finalRecommendationDisplay = localizedRefinementRecommendation(finalRecommendation);
  const finalOfflineGate = textOf(finalRefinement.offline_pre_p0_gate || {});
  const plainReopen = textOf(terminal?.reopen_condition || {}) || (currentStatus === "merge"
    ? (language === "zh" ? "只有出现无法被当前父方向表达、且会改变独立论文结论的新机制证据时，才重新立为独立方向。" : "Reopen standalone only if new mechanism evidence cannot be expressed by the parent direction and changes the paper-level conclusion.")
    : (language === "zh" ? "只有新增第一手证据在同信息、同预算和最强简单对照下推翻当前结论，才重新人工评审。" : "Reopen human review only if new primary evidence overturns the current result against the strongest same-information, matched-budget baseline."));
  const minimumFalsifier = textOf(terminal?.minimum_p0 || current.decisive_pilot || current.pilot || {}) || (language === "zh" ? "历史实验合同与最强对照见技术审计层。" : "See the technical audit layer for the frozen experiment contract and strongest baseline.");
  const decisiveEvidence = disposition.detail || textOf(terminal?.terminal_reason || {}) || briefing.why;
  const oneMinuteBase=parentOneMinuteCopy({idea,current,terminal,currentStatus,disposition,lifecycleStage,plainReopen,decisiveEvidence});
  const oneMinute=oneMinuteBase?{...oneMinuteBase,next:primaryActionText||oneMinuteBase.next}:oneMinuteBase;
  const evidenceTrack = `<section class="research-item-evidence-track"><header><div><b>${language === "zh" ? "Idea + Experiment 一体化证据链" : "Unified Idea + Experiment evidence trail"}</b><span>${language === "zh" ? "实验是 ResearchItem 的证据事件，不再维护一套平行的当前状态。" : "Experiments are evidence-producing events inside the ResearchItem, not a parallel current-state system."}</span></div><a href="experiments.html#terminal-experiment-portfolio">${language === "zh" ? "技术审计 ↗" : "Technical audit ↗"}</a></header><div class="research-item-evidence-steps"><article><span>01</span><div><b>${language === "zh" ? "最小可证伪实验" : "Smallest falsifier"}</b><p>${esc(minimumFalsifier)}</p></div></article><i>→</i><article><span>02</span><div><b>${language === "zh" ? "决定性实验 / 证据" : "Decisive experiment / evidence"}</b><p>${esc(decisiveEvidence)}</p><small>${esc(disposition.label)} · ${esc(lifecycleStage)}</small></div></article><i>→</i><article><span>03</span><div><b>${language === "zh" ? "当前科学决策" : "Current scientific decision"}</b><p><strong>${esc(humanParentFinalStatusLabel(currentStatus))}</strong> · ${language === "zh" ? `全局可启动正式实验=${experimentAuthority}` : `global launchable formal experiments=${experimentAuthority}`}</p><small>${language === "zh" ? "重开：" : "Reopen: "}${esc(plainReopen)}</small></div></article></div></section>`;
  const absorbed = [...new Set([...(terminal?.absorbed_children || []),...(overlay.absorbed_from || current.absorbed_from || [])])];
  const absorbedIdeas = absorbed.map(currentFinalIdeaById).filter(Boolean);
  const absorbedNote = absorbed.length ? `<div class="human-absorbed-methods"><b>${language === "zh" ? "已吸收终态方法资产" : "Absorbed FINAL method assets"}</b>${absorbed.map((id)=>`<span title="${esc(id)}">${esc(localizedPaperIdeaMethodAsset(id))}</span>`).join("")}</div>` : "";
  const freshCheck = current.fresh_reducibility_check || {};
  const freshSources = (freshCheck.sources || []).map((source) => `<a href="${esc(source.url)}" target="_blank" rel="noopener">${esc(source.title)}</a>`).join("");
  const freshBlock = freshSources ? `<section class="human-fresh-collision"><h4 data-toc="false">${language === "zh" ? `最新可归约性审查 · ${esc(freshCheck.review_date || "")}` : `Fresh reducibility · ${esc(freshCheck.review_date || "")}`}</h4><p>${language === "zh" ? "以下是一手来源；上面的“最近工作与真正边界”已经按这些工作收窄，不把已有人做过的部分继续当贡献。" : "Primary sources below support the narrowed boundary above; already-covered mechanisms are not counted as the contribution."}</p><nav>${freshSources}</nav></section>` : "";
  return `<details class="human-review-idea-card human-tone-${tone}" id="idea-${esc(code.toLowerCase())}" data-terminal-status="${esc(currentStatus)}" data-historical-status="${esc(historicalStatus)}" data-evidence-disposition="${esc(disposition.tone)}" data-briefing-reason="${esc(briefing.reason.key)}">
    <summary><div class="human-idea-title"><span class="human-idea-code">${esc(code)}</span><div><b>${textOf(current.title)}</b><small>${originalNumber ? `${language === "zh" ? "原讨论" : "Original"} Idea ${originalNumber} · ` : ""}${textOf(idea.track)} · ${language === "zh" ? "历史自动二审" : "historical automated R2"} ${esc(historicalVerdict)}</small></div></div><div class="human-idea-summary"><div><span class="human-status-badge human-status-${tone}">${esc(humanParentFinalStatusLabel(currentStatus))}</span><span class="briefing-reason-pill tone-${esc(briefing.reason.tone)}">${esc(textOf(briefing.reason))}</span></div><p>${esc(briefing.why)}</p></div></summary>
    <div class="human-idea-body">
      <div class="canonical-lifecycle-strip"><span><b>${language === "zh" ? "当前最终状态" : "Current final state"}</b>${esc(humanParentFinalStatusLabel(currentStatus))}</span><span><b>${language === "zh" ? "唯一内部动作" : "Primary internal action"}</b>${esc(primaryActionClass)}</span><span><b>${language === "zh" ? "历史里程碑" : "Historical milestone"}</b>${esc(lifecycleStage)}</span><span><b>${language === "zh" ? "最新证据处置" : "Latest evidence disposition"}</b>${esc(disposition.label)}</span><span><b>${language === "zh" ? "正式实验权限" : "Formal experiment authority"}</b>${experimentAuthority}</span></div>
      ${renderResearchItemFieldLineage(code)}
      <section class="idea-briefing-summary one-minute-briefing tone-${esc(briefing.reason.tone)}"><header><b>${language === "zh" ? "【1min结论】" : "【1 min summary】"}</b><span>${esc(textOf(briefing.reason))}</span></header>${language==="zh"&&oneMinute?`<div class="one-minute-briefing-grid"><section class="briefing-scene" data-briefing-part="scene"><b>① 具体任务场景：到底在做什么？</b><p>${esc(oneMinute.scene)}</p></section><section data-briefing-part="progress"><b>② 生命周期 + 我们实际做到哪</b><p>${esc(oneMinute.progress)}</p></section><section data-briefing-part="observed"><b>③ 实验实际看到了什么</b><p>${esc(oneMinute.observed)}</p></section><section data-briefing-part="judgment"><b>④ 所以现在能确定什么，还不能确定什么</b><p>${esc(oneMinute.judgment)}</p></section><section class="briefing-human" data-briefing-part="human"><b>⑤ 当前最需要解决的问题 / 希望人工判断什么</b><p>${esc(oneMinute.human)}</p></section><section class="briefing-next" data-briefing-part="next"><b>⑥ 下一步方案</b><p>${esc(oneMinute.next)}</p></section></div>`:`<div><section><b>Research question</b><p>${esc(briefing.wanted)}</p></section><section><b>How far it got</b><p>${esc(lifecycleStage)}</p></section><section><b>Decisive evidence</b><p>${esc(decisiveEvidence)}</p></section><section><b>Current judgment</b><p>${esc(briefing.learned)}</p></section><section><b>Human decision needed</b><p>${esc(plainReopen)}</p></section><section><b>Next step</b><p><strong>${esc(primaryActionClass)}</strong> · ${esc(primaryActionText||plainReopen)}</p></section></div>`}</section>
      ${evidenceTrack}
      ${renderConcreteMethodComparison(PARENT_SIMPLE_COMPARISONS_ZH[code],"parent",PARENT_SIMPLE_METHOD_GUIDES_ZH[code])}
      <details class="human-lineage-details"><summary>${language === "zh" ? "历史人工意见与方法迭代" : "Historical human feedback and method iteration"}<small>${language === "zh" ? "谱系记录，不代表当前权限" : "lineage, not current authority"}</small></summary><div class="human-review-history">
        <section class="human-opinion-box"><h4 data-toc="false">${language === "zh" ? `人工意见 · 2026-08-10（原讨论 Idea ${originalNumber || "?"}）` : `Human opinion · 2026-08-10 (original Idea ${originalNumber || "?"})`}</h4><p>${esc(humanOpinion || "—")}</p><small class="human-recommendation-label tone-${humanRecommendationTone(humanRecommendation)}">${esc(humanRecommendationLabel(humanRecommendation))}</small></section>
        ${iterationSummary ? `<section class="human-iteration-box"><h4 data-toc="false">${language === "zh" ? `本轮方法迭代 · ${esc(iteration.round || "2026-08-10")}` : `Current method iteration · ${esc(iteration.round || "2026-08-10")}`}</h4><p>${esc(iterationSummary)}</p>${iteration.verdict ? `<small>${language === "zh" ? "当前门禁" : "Current gate"}: ${esc(iteration.verdict)}</small>` : ""}${finalRecommendation ? `<div class="human-final-refinement"><b>${language === "zh" ? "最终分流" : "Final recommendation"}</b><span>${esc(finalRecommendationDisplay)}</span>${finalOfflineGate ? `<p>${language === "zh" ? "GPU 前先做：" : "Before GPU: "}${esc(finalOfflineGate)}</p>` : ""}</div>` : ""}</section>` : ""}
      </div></details>
      ${renderTerminalDecision(idea.id)}
      <details class="human-complete-intro"><summary>${language === "zh" ? "完整 Idea 介绍" : "Complete idea introduction"}<small>${language === "zh" ? "问题、直觉、方法、例子与价值" : "problem, intuition, method, example, and value"}</small></summary><div class="human-core-grid human-reading-grid">
        <section><h4 data-toc="false">${language === "zh" ? "这个 Idea 在解决什么" : "What problem is this solving?"}</h4><p>${textOf(current.purpose)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "最简单的直觉" : "Plain-language intuition"}</h4><p>${esc(intuition)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "具体准备怎么做" : "What would we actually do?"}</h4><p>${textOf(current.core_idea)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "举个具体例子" : "Concrete example"}</h4><p>${esc(example || "—")}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "为什么值得试" : "Why might this work?"}</h4><p>${textOf(current.rationale || current.importance)}</p></section>
      </div></details>
      ${absorbedNote}
      <details class="human-technical-details"><summary>${language === "zh" ? "方法细节与论文边界" : "Method details and paper boundary"}<small>${language === "zh" ? "需要写论文或审 novelty 时再展开" : "Open when checking implementation or novelty"}</small></summary><div class="human-evidence-grid">
        <section><h4 data-toc="false">${language === "zh" ? "方法步骤" : "Method steps"}</h4><p>${textOf(current.method_logic)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "为什么这个问题重要" : "Why the problem matters"}</h4><p>${textOf(current.importance)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "相比简单方法多了什么" : "What it adds over simpler methods"}</h4><p>${textOf(current.comparative_advantage)}</p></section>
        <section><h4 data-toc="false">${language === "zh" ? "真正更新什么 / 用什么学" : "Persistent update / learning signal"}</h4><p>${textOf(substance.persistent_update_object || {})}</p><p>${textOf(substance.learning_signal || {})}</p></section>
        ${mergeGate.status === "merge-if-tied" ? `<section><h4 data-toc="false">${language === "zh" ? "什么时候必须并回父级研究方向" : "When it must merge into its parent"}</h4><p>${textOf(mergeGate.decision_rule || {})}</p></section>` : ""}
        <section><h4 data-toc="false">${language === "zh" ? "最近工作与真正边界" : "Nearest work and real boundary"}</h4><p>${textOf(current.collision_boundary)}</p><div class="cvpr-chip-row">${(current.nearest_work || []).map((name) => `<span>${esc(name)}</span>`).join("")}</div></section>
        ${freshBlock}
      </div></details>
      ${["p0","p0-ready"].includes(historicalStatus) ? renderIdeaExperimentSection(current,{...meta,status:historicalStatus},absorbedIdeas) : ""}
    </div>
  </details>`;
}
function renderDiscussedIdeaBank() {
  const bank = iclrIdeaBank();
  const review = humanReviewData();
  const byId = new Map((bank.passed_ideas || []).map((idea) => [idea.id, idea]));
  const statuses = ["hold","stop","merge"];
  const all = Object.entries(review.ideas || {}).map(([id,meta]) => {
    const terminal = terminalParentState(id);
    return {id,meta:{...meta,status:terminal ? humanParentFinalState(terminal) : meta.status,code:terminal?.code || meta.code,group:terminal?.group || meta.group},idea:byId.get(id)};
  }).filter((row) => row.idea);
  const counts = Object.fromEntries(statuses.map((status) => [status,all.filter((row) => row.meta.status === status).length]));
  const groups = (review.groups || []).map((group) => {
    const rows = all.filter((row) => row.meta.group === group.id).sort((a,b) => String(a.meta.code).localeCompare(String(b.meta.code),undefined,{numeric:true}));
    const statusBlocks = statuses.map((status) => {
      const subset = rows.filter((row) => row.meta.status === status);
      if (!subset.length) return "";
      return `<div class="human-status-block"><div class="human-status-heading human-status-${humanReviewStatusTone(status)}"><b>${esc(humanParentFinalStatusLabel(status))}</b><span>${subset.length}</span></div><div class="human-idea-list">${subset.map((row,index) => renderHumanReviewedIdeaCard(row.idea,row.meta,index)).join("")}</div></div>`;
    }).join("");
    return `<section class="human-science-group" id="discussed-group-${esc(group.id.toLowerCase())}"><header><span>${esc(group.id)}</span><div><h3>${textOf(group.title)}</h3><p>${textOf(group.question)}</p></div><strong>${rows.length}</strong></header>${statusBlocks}</section>`;
  }).join("");
  const terminalLedger = humanTerminalState();
  const canonicalDate = terminalLedger.decision_date || canonicalHumanReviewData().review_date || review.review_date || "2026-08-11";
  const terminalSummary = humanParentFinalSummary();
  const finalSummary = `<div class="human-final-summary terminal-summary"><div><b>${terminalSummary.hold || 0}</b><span>${language === "zh" ? "当前暂缓" : "currently on hold"}</span></div><div><b>${terminalSummary.stop || 0}</b><span>${language === "zh" ? "当前已停止" : "currently stopped"}</span></div><div><b>${terminalSummary.merge || 0}</b><span>${language === "zh" ? "当前已合并" : "currently merged"}</span></div><div><b>0</b><span>${language === "zh" ? "可启动正式实验" : "launchable formal experiments"}</span></div><small>${language === "zh" ? `当前科学状态 · ${canonicalDate}：HOLD 4 / STOP 16 / MERGED 6；历史 P0、P0-ready 与 DROP 只作里程碑。` : `Current scientific state · ${canonicalDate}: 4 HOLD / 16 STOPPED / 6 MERGED; historical P0, P0-ready, and DROP remain milestones only.`}</small></div>`;
  return `<section class="panel human-review-overview"><div class="idea-panel-heading"><div><b class="human-overview-kicker">${language === "zh" ? `H1 · ${esc(canonicalDate)} · 历史谱系` : `H1 · ${esc(canonicalDate)} · HISTORICAL LINEAGE`}</b><p class="section-intro">${language === "zh" ? "这一章保留人工冻结终态，同时单独呈现历史 P0 生命周期、最新实验处置与当前执行权限；三者不能互相覆盖。" : "This chapter preserves the frozen human terminal state while separating historical P0 lifecycle, latest evidence disposition, and current execution authority."}</p></div><strong>${all.length} ${language === "zh" ? "个历史父方向" : "historical parents"}</strong></div><div class="human-review-stats">${statuses.map((status) => `<div class="human-stat human-stat-${humanReviewStatusTone(status)}"><b>${counts[status] || 0}</b><span>${esc(humanParentFinalStatusLabel(status))}</span></div>`).join("")}</div>${finalSummary}</section>${renderHumanReviewMethodology()}${groups}`;
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
const SUPPLEMENTAL_TERMINAL_DISPLAY = {
  "active-causal-minimal-rollback":{
    intuition:{zh:"一次回滚不应撤销所有最近更新；先用有界干预定位真正共同导致回退的最小更新集合，再只撤销该集合。",en:"A rollback should not erase every recent update: use bounded interventions to locate the smallest jointly failing set, then revert only that set."},
    rationale:{zh:"如果能以更少测试定位最小故障集，就能避免误回滚无害更新；但必须证明收益不只是标准稀疏组测试。",en:"Finding the minimal fault set with fewer tests could preserve harmless updates, but the gain must exceed standard sparse group testing."},
    methodLogic:{zh:"冻结 24 个含 4–8 个更新的稀疏故障案例与故障真值；执行成组启停干预，逐步缩小候选集并输出最小故障集合；按逐案例测试次数与定位正确率，对比非学习二元组测试、ddmin、逐个消融和最后更新回滚。",en:"Freeze 24 sparse-fault cases with 4–8 updates and known fault sets; run grouped enable/disable interventions, narrow the candidate set, and compare exact recovery and per-case test count with non-learned binary group testing, ddmin, one-at-a-time ablation, and last-update rollback."},
    advantage:{zh:"原设想的附加价值是利用历史与因果信息减少定位测试；真实结果没有显示超出非学习二元组测试的独立优势。",en:"The proposed added value was fewer localization tests from history and causal information; the observed result shows no advantage beyond non-learned binary group testing."},
    collision:{zh:"匹配实验已经划清边界：相对 ddmin 的节省属于标准稀疏组测试；主动学习或因果排序没有额外贡献。",en:"The matched experiment fixes the boundary: savings over ddmin come from standard sparse group testing, with no added contribution from active learning or causal ordering."},
    metric:{zh:"精确最小故障集定位率、逐案例干预次数，以及相对匹配二元组测试的差值；当前结果为 24/24 对 24/24、均值 5.708 对 5.708、paired p=1.0。",en:"Exact minimal-fault-set recovery, per-case intervention count, and the delta versus matched binary group testing; observed: 24/24 versus 24/24, 5.708 versus 5.708 mean tests, paired p=1.0."},
    reopen:{zh:"只有新的第一手证据表明，在信息、稀疏先验与预算和二元组测试完全匹配后，历史或因果排序仍显著减少测试次数，或提高交互故障定位率，才重新人工评审。",en:"Reopen human review only if new primary evidence shows that history or causal ordering still reduces tests or improves interaction-fault localization after matching information, sparse prior, and budget to binary group testing."},
    failureLayer:{zh:"方法实现／独立机制",en:"method realization / standalone mechanism"}
  },
  "counterfactual-evolution-decision-controller":{
    intuition:{zh:"只有在同一进化状态和同一候选序列上比较继续、提交、回滚和停止，四种动作的反事实价值才可公平学习。",en:"Continue, commit, rollback, and stop are comparable only when their counterfactual values are measured from the same evolution state and candidate sequence."},
    rationale:{zh:"同状态四动作决策可以减少无效搜索和错误提交，但必须显示学习控制器比使用相同状态特征的浅规则更好。",en:"Same-state four-action decisions could reduce wasted search and bad commits, but a learned controller must outperform a shallow rule using the same state features."},
    methodLogic:{zh:"构建同状态四动作离线反事实表；用 train/calibration 训练并冻结控制器；在 hidden table 上比较动作准确率与 regret，并让 depth-3 CART 使用完全相同的四个原始状态特征。",en:"Build a same-state four-action offline counterfactual table; train and freeze the controller on train/calibration; evaluate action accuracy and regret on the hidden table against a depth-3 CART using the identical four raw state features."},
    advantage:{zh:"原设想是学习预算与回退约束下的四动作策略；真实结果被 13-node 的 depth-3 CART 完全复现。",en:"The proposal learned a four-action policy under budget and regression constraints; a 13-node depth-3 CART exactly reproduced the observed result."},
    collision:{zh:"边界已收口为普通浅层决策规则：16/16、mean/worst regret=0，四动作分布也完全一致。",en:"The boundary collapses to a shallow decision rule: 16/16, zero mean/worst regret, and the identical four-action distribution."},
    metric:{zh:"隐藏状态上的动作准确率、平均/最坏 regret 与四动作覆盖；当前两者均为 16/16、regret=0。",en:"Hidden-state action accuracy, mean/worst regret, and four-action coverage; both methods currently reach 16/16 with zero regret."},
    reopen:{zh:"只有在同一状态特征、候选、标签与预算下，匹配浅规则不再复现控制器，并且差异在新的冻结任务流上稳定出现，才重开独立方法。",en:"Reopen only if a matched shallow rule no longer reproduces the controller under identical state features, candidates, labels, and budget, with a stable delta on a new frozen stream."},
    failureLayer:{zh:"方法实现／独立机制",en:"method realization / standalone mechanism"}
  },
  "replicated-effect-memory-gate":{
    intuition:{zh:"不要因一次成功就写入经验；只有帮助或伤害能在相似未来条件中复现时，才准入、隔离或删除。",en:"Do not admit a lesson after one success; admit, quarantine, or delete only when benefit or harm replicates in comparable future conditions."},
    rationale:{zh:"门控可以减少少数任务上的强负迁移，但必须存在可在结果前定位的稳定适用性结构。",en:"Gating could reduce severe minority-task harm, but it requires stable applicability structure observable before outcomes."},
    methodLogic:{zh:"执行 retrieved／token-matched placebo／无记忆的匹配重放，估计条目效应并冻结准入门；随后检查同卡复放的首分叉可复现性、状态签名定位能力与审计成本—召回曲线。",en:"Run matched retrieved, token-matched-placebo, and no-memory replays; estimate entry effects and freeze admission, then audit same-card first-divergence reproducibility, state-signature localization, and the cost–recall curve."},
    advantage:{zh:"首分叉位置可复现，说明记忆确实稳定改变早期轨迹；但最终效应符号由下游上下文决定，candidate-global 门控假设过强。",en:"First divergence is reproducible, showing stable early branch steering, but downstream context determines the final effect sign, so candidate-global gating is too strong."},
    collision:{zh:"只保留为 soft audit-priority signal，不能作为 hard gate：1-step 成本约 25% 仅覆盖 54.5% nonzero effects，达到 90.9% recall 时 5-step 成本约 90.1%。",en:"Retain only as a soft audit-priority signal, never a hard gate: a 1-step screen costs about 25% for 54.5% nonzero-effect recall, while 90.9% recall at 5 steps costs about 90.1%."},
    metric:{zh:"未来帮助/伤害、首分叉复现率、状态签名定位与审计成本—召回；当前首分叉位置 11/11、动作对 10/11 复现，但 MI permutation p=0.216。",en:"Future benefit/harm, first-divergence reproducibility, state-signature localization, and audit cost–recall; current results reproduce positions 11/11 and action pairs 10/11, but MI permutation p=0.216."},
    reopen:{zh:"只有新的独立样本显示结果前适用性结构能在同信息基线之外稳定预测效应符号，并能以实质更低成本安全门控，才重开。",en:"Reopen only if new independent samples show pre-outcome applicability structure that predicts effect sign beyond same-information baselines and enables materially cheaper safe gating."},
    failureLayer:{zh:"证据支持／方法可学习性",en:"support / method learnability"}
  },
  "cross-task-effect-transport-certificate":{
    intuition:{zh:"源任务上有效的经验不能自动迁移；必须先证明效应符号和幅度在未见任务族中可运输。",en:"Source-task efficacy does not imply transfer; effect sign and magnitude must be shown transportable to unseen task families."},
    rationale:{zh:"迁移证书可以减少跨任务负迁移，但任务级效应假设必须在局部状态与下游上下文变化后仍成立。",en:"A transport certificate could reduce cross-task negative transfer, but task-level effect stability must survive local-state and downstream-context changes."},
    methodLogic:{zh:"在三任务族上学习效应表示，留出一整个任务族；冻结证书后比较效应符号、幅度、覆盖与负迁移，并用同硬件首分叉复放检查可复现部分究竟是早期分支还是最终效应。",en:"Learn effect representations on three task families and hold out one family; freeze the certificate, compare sign, magnitude, coverage, and negative transfer, and use matched-hardware first-divergence replay to distinguish early branch steering from final effect."},
    advantage:{zh:"可复现的是早期轨迹分支改变，而不是最终效应符号；完全相同的早期签名会在不同 target context 下翻转符号。",en:"What replicates is early trajectory-branch steering, not final effect sign; an identical early signature flips sign across target contexts."},
    collision:{zh:"task-level transport 假设过强，strict-LOTO 只保留为归档次级诊断，不授权 clean R1、第二 backbone 或替代研究方向。",en:"The task-level transport assumption is too strong; strict LOTO remains an archived secondary diagnostic with no clean R1, second backbone, or replacement idea authorized."},
    metric:{zh:"留出任务族的效应符号/幅度、有效覆盖、负迁移，以及首分叉的跨卡复现；当前证据不足以支持最终效应运输。",en:"Held-out-family effect sign/magnitude, valid coverage, negative transfer, and first-divergence replication; current evidence does not support final-effect transport."},
    reopen:{zh:"只有新的一手或独立实验在相同结果前信息下识别出跨任务稳定的适用性变量，并在完整留出任务族中显著优于语义相似度与同信息运输基线，才重开。",en:"Reopen only if new primary or independent evidence identifies a cross-task-stable pre-outcome applicability variable that beats semantic similarity and same-information transport baselines on fully held-out families."},
    failureLayer:{zh:"证据支持／假设范围",en:"support / assumption scope"}
  }
};
const SUPPLEMENTAL_BRIEFING_ZH = {
  "replicated-effect-memory-gate":{tone:"support",label:"当前数据或底座不支持验证",why:"记忆会稳定改变早期轨迹，但相同早期信号在不同后续上下文里可能变成帮助或伤害，因此现在学不出可靠的全局准入门。",learned:"只把早期分叉当作软审计优先级，不能用它硬性淘汰记忆。"},
  "cross-task-effect-transport-certificate":{tone:"support",label:"当前数据或底座不支持验证",why:"可以复现的是早期轨迹分叉，而不是跨任务稳定的最终收益方向；当前证据不足以支持迁移证书。",learned:"跨任务效应必须在完整后续上下文中验证，不能只看局部状态签名。"},
  "bounded-probe-api-transition-operator":{tone:"simple",label:"简单方法达到上限；复杂方法未运行",why:"确定性的 P/E/X 语义规则在读操作和有副作用操作上都达到满分，学习方法没有可提升空间。",learned:"保留类型化 API 语义与恢复测试，不再训练独立转移算子。"},
  "interventional-permission-triage-under-ceiling":{tone:"simple",label:"简单方法结果更好",why:"使用同一干预标签的简单单调布尔规则更少触发重授权，同时没有漏掉风险。",learned:"权限重授权优先使用可审计的简单规则。"},
  "constraint-complete-typed-memory-order-logic":{tone:"simple",label:"简单方法逐项打平",why:"匹配的 n 元因子模型在准确率和编译成本上完全复现了符号顺序逻辑。",learned:"保留约束测试，不再主张独立符号表示优势。"},
  "active-causal-minimal-rollback":{tone:"simple",label:"简单方法逐项打平",why:"标准二元组测试在相同信息和预算下取得完全相同结果，因此当前主动因果机制没有显示额外价值。",learned:"相对 ddmin 的收益来自稀疏组测试，不是新的因果学习机制。"},
  "counterfactual-evolution-decision-controller":{tone:"simple",label:"简单方法逐项打平",why:"只用相同四个状态特征的浅层决策树，完全复现了学习控制器的四动作选择和零 regret。",learned:"反事实表有诊断价值，但执行策略可以并入简单规则。"},
};
const SUPPLEMENTAL_ONE_MINUTE_ZH = {
  "active-causal-minimal-rollback":{
    scene:"Agent 连续接受 4–8 个更新后突然出现回退时，最笨的办法是把最近所有更新都撤掉。这个方向想用少量“成组开/关更新”的测试，找出真正共同导致故障的最小更新集合，只回滚有问题的那几条。",
    progress:"生命周期：历史 P0 → 当前 STOP。已经在 24 个冻结的稀疏故障案例上实际比较主动因果定位和标准二元组测试；两边看到相同更新集合、相同故障真值，并按每个案例用了多少次测试公平计费。",
    observed:"两种方法都在 24/24 个案例中找对最小故障集，平均都需要 5.708 次测试，逐案例完全一致。相对逐个删除方法约 62% 的节省是真实的，但标准二元组测试已经完整获得这项收益。",
    judgment:"能确定的是：稀疏组测试很适合做最小回滚；不能把这项收益归给主动因果学习。当前复杂方法没有留下任何额外决策或成本优势。",
    human:"希望人工判断是否还存在标准二元组测试处理不了的真实故障结构，例如强交互、非单调依赖或未知稀疏度。如果实际系统没有这种结构，就直接把二元组测试做成回滚工具。",
    next:"默认采用标准稀疏组测试作为实现。只有拿到新的真实更新故障，其中匹配信息和预算的二元组测试明显失效，而历史/因果排序稳定减少测试或提高定位率，才重开独立方法。"
  },
  "counterfactual-evolution-decision-controller":{
    scene:"Agent 在一次自我更新循环里经常面临四个动作：继续尝试、接受当前更新、回滚，或停止。这个方向想根据当前状态和四种动作可能带来的结果学习一个控制器，减少无效搜索和错误提交。",
    progress:"生命周期：历史 P0 → 当前 STOP。已经构造同一状态下四种动作的离线对照表，用训练/校准部分冻结控制器，再在 16 个完全留出的状态上与只看相同 4 个原始特征的浅层决策树比较。",
    observed:"学习控制器和 depth-3 浅树都在 16/16 个留出状态上选对动作，平均和最坏决策损失都是 0，continue/commit/rollback/stop 的动作分布也逐项相同。",
    judgment:"四动作反事实表本身很适合诊断，但当前不需要学习控制器；一棵 13 节点浅树已经完全复现执行策略。",
    human:"希望人工判断真实线上状态是否存在这 4 个简单特征无法表达的情况。如果没有，就优先把浅树作为可解释控制规则，而不是追加 GPU replay。",
    next:"保留反事实表做诊断，执行层改用浅树。只有在新的冻结任务流里出现稳定的浅树失效案例，并且学习控制器在看到完全相同输入时仍真正改善决定，才重开。"
  },
  "replicated-effect-memory-gate":{
    scene:"Agent 在 ALFWorld 做家务时会检索过去的记忆。我们观察到同一条记忆可以很稳定地让 Agent 在早期选择另一条行动分支，但这条分支在不同后续任务里有时帮助、有时伤害。这个方向原本想根据这种可复现影响决定一条记忆应写入、隔离还是删除。",
    progress:"生命周期：历史 P0 → 当前 STOP（方法证据不足，不是原理否定）。已经对 11 个真实非零记忆影响单元做同卡重放：最早分叉位置 11/11 复现，具体分叉动作 10/11 复现；同时检查了用早期状态特征预测最终帮助/伤害的能力。",
    observed:"记忆确实稳定改变早期行为，但“早期怎么分叉”不能稳定告诉我们最终是好还是坏。同一类早期行为签名在冷却、加热、清洗等不同目标上下文里会出现负/正/负不同结果；状态特征相对简单任务先验的改善也很弱。",
    judgment:"能确定的是“记忆会稳定推 Agent 走向不同早期分支”；不能据此做一个全局硬准入门，因为最终收益取决于后续任务上下文。早期分叉只适合告诉我们哪些记忆值得优先审计。",
    human:"希望人工判断是否存在更合适的、在结果发生前就能观察到的上下文变量，能把“这条记忆在什么任务里会帮忙、什么任务里会伤害”区分开。如果只能事后看最终结果，就不适合做准入证书。",
    next:"把早期分叉降级成软审计排序信号，不再用它直接淘汰记忆。只有新的独立样本证明某个结果前上下文变量能稳定预测最终影响，而且显著优于简单任务先验，才重开硬门控。"
  },
  "cross-task-effect-transport-certificate":{
    scene:"一条记忆在“冷却物体”任务上帮过 Agent，并不意味着换成“加热”或“清洗”任务后仍然有帮助。这个方向想给记忆做一个迁移证书：在源任务上验证有效后，判断它的帮助/伤害方向能不能安全带到未见任务族。",
    progress:"生命周期：历史 P0 → 当前 STOP（跨任务支持不足）。已经检查 11 个非零记忆影响单元的重放稳定性：早期分叉位置 11/11 可复现、动作 10/11 可复现，但没有观察到同样稳定的最终收益方向。",
    observed:"真正稳定的是“记忆会把早期轨迹推向另一条分支”，不是“这条记忆最后一定有益或有害”。完全相同的早期行为签名，在不同目标上下文下会翻转最终收益方向。",
    judgment:"因此当前不能给记忆发一个跨任务通用的效应证书。局部轨迹可复现不等于最终收益可迁移，这条区别本身保留为重要经验。",
    human:"希望人工判断是否有比任务名称或早期动作更接近最终后果的结果前上下文，例如目标约束、剩余子任务或资源状态；如果能找到跨任务稳定变量，迁移问题仍有机会。",
    next:"不再做 task-level 全局证书。未来若找到新的结果前上下文变量，先在完整留出任务族上检验其能否预测收益方向，并与语义相似度和简单任务先验比较；稳定胜出后再重开。"
  },
  "bounded-probe-api-transition-operator":{
    scene:"工具型 Agent 调 API 时，需要知道 create/update/delete 之后系统状态会怎样变化，以及失败后怎么恢复。这个方向原本想让模型通过少量探针学习 API 状态转移；对照是直接按接口的前置条件、效果和异常规则手写状态机。",
    progress:"生命周期：历史 P0 → 当前 STOP。先在 GitLab/Codeberg 做了 12 个只读案例，再在 ledger/vault 两类有副作用 API 上覆盖创建、更新、删除、重复操作和恢复。复杂 learned arm 没有运行，因为简单规则先达到满分。",
    observed:"手写确定性规则在 12/12 只读案例和 12/12 有副作用+恢复案例上都正确。简单方法已经达到 100%，因此没有剩余误差让学习型转移算子证明额外价值。",
    judgment:"这里不能说“两种方法打平”，因为复杂方法根本没有运行。能确定的是：当前这批 API 的状态语义已经可以被明确规则完整表达，继续训练模型没有可测提升空间。",
    human:"希望人工判断未来目标 API 是否真的存在规则无法直接写出的隐含状态、服务端异步行为或跨调用依赖。如果没有，就把确定性状态机当基础设施即可。",
    next:"保留类型化 API 语义和恢复测试，不训练独立模型。只有出现一类规则在相同可见信息下系统性预测不了、但少量探针能学出的真实 API 行为，才重开。"
  },
  "interventional-permission-triage-under-ceiling":{
    scene:"Agent 更新了 Prompt、记忆、工具或工作流后，如果每次都重新审核所有旧权限，成本很高。这个方向想预测“哪些既有权限因为这次更新真的需要重新授权”，同时绝不允许扩大原权限上限。",
    progress:"生命周期：历史 P0 → 当前 STOP。已经在 32 个训练/测试特征组合完全不重叠的工具变更上，比较线性风险模型与使用完全相同输入和风险标签的单调布尔规则；两边都必须做到不漏风险。",
    observed:"两种方法都漏掉 0 个风险，但学习模型触发 53 次重授权，简单布尔规则只触发 29 次，少打断 24 次操作（45.3%）。",
    judgment:"当前复杂风险模型被简单规则严格支配：安全性没有更好，人工/运行中断却更多。因此保留“按变更影响选择性重授权”的问题，执行方法改用可审计规则。",
    human:"希望人工检查简单规则在哪些真实权限变化上可能失效，尤其是多权限交互或隐式可达行为。如果没有这种失败案例，就没有理由恢复学习模型。",
    next:"默认部署简单单调规则并持续记录漏检/误报案例。只有新的冻结数据出现简单规则稳定漏掉的风险，而学习方法在使用相同输入时能补上且不显著增加重授权，才重开。"
  },
  "constraint-complete-typed-memory-order-logic":{
    scene:"Agent 一次检索到多条不同类型的记忆时，执行顺序可能重要：例如安全约束要先于普通策略，某些工具规则只有在特定上下文才生效。这个方向想用显式符号约束描述这些高阶顺序关系，再在没见过的记忆类型组合上检查能否正确排序。",
    progress:"生命周期：历史 P0 → 当前 STOP。已经在 32 个全部含有效约束的留出类型组合上，比较符号约束程序与容量、输入和检查预算完全匹配的多元因子模型，并同时比较编译后的免搜索执行。",
    observed:"原始准确率两边都是 100%，编译后准确率仍都是 100%，平均检查边数也同为 1.125。复杂符号表示没有产生一个不同决定，也没有节省检查成本。",
    judgment:"可以保留“多记忆顺序必须满足约束”这件事，但当前证据不支持独立的符号表示贡献；匹配的因子模型已经完整表达同一约束。",
    human:"希望人工判断是否存在因子模型无法用相同预算表达、而符号程序能系统外推的新组合结构。如果没有，就把符号形式保留为解释层而非方法贡献。",
    next:"执行层使用更简单的匹配表示，符号规则只保留为可读约束和真值检查器。只有新的组合任务里出现稳定、会改变决定的表示差异时才重开。"
  }
};
const SUPPLEMENTAL_SIMPLE_COMPARISONS_ZH = {
  "bounded-probe-api-transition-operator":{ours:"学习一个 API 状态转移算子：先做少量探针，再预测 create／update／delete 的最终状态与失败后的恢复动作。",baseline:"手写确定性的 P/E/X 规则：根据 precondition、effect 和 exception 直接更新状态，不训练模型。",matched:"先在 GitLab/Codeberg 做 12 个无泄漏只读案例；再在 ledger/vault 两个不同状态码 family 各做 6 个探针，并覆盖隐藏 create/update/delete、duplicate 和跨操作恢复。",rows:[{metric:"只读案例",ours:"未运行 learned arm",baseline:"12/12",delta:"无实验差值；简单法已到 100%"},{metric:"有副作用+恢复",ours:"未运行 learned arm",baseline:"12/12",delta:"无实验差值；简单法已到 100%"}],verdict:"这里不能写成“两边打平”：复杂方法没有运行。停止原因是简单规则在两层任务都已经 100%，继续训练 learned arm 没有可测提升空间。"},
  "interventional-permission-triage-under-ceiling":{ours:"用干预数据拟合线性 q，预测每个工具变更后是否必须重新授权。",baseline:"用完全相同的 mutation 表示和干预标签，归纳一条单调 DNF 布尔规则。",matched:"32 个 train/test 特征组合零重叠的 unseen operator；两边用相同输入和标签，都要求 missed risk=0。",rows:[{metric:"漏掉风险",ours:"0",baseline:"0",delta:"0"},{metric:"触发重授权",ours:"53",baseline:"29",delta:"简单规则少 24 次（45.3%）"}],verdict:"安全性相同，但简单规则少打断 24 次操作，因此 learned q 被严格支配。"},
  "constraint-complete-typed-memory-order-logic":{ours:"用符号类型、顺序和 n 元约束编译一套 memory-order logic，再执行约束检查。",baseline:"用匹配的 typed n-ary factor 表示同一约束，并把 active-edge 预算限制为完全相同。",matched:"32 个都含有效约束的 held-out 类型组合；同一 active-edge 编译预算。",rows:[{metric:"原始准确率",ours:"100%",baseline:"100%",delta:"0"},{metric:"编译后准确率",ours:"100%",baseline:"100%",delta:"0"},{metric:"平均 edge checks",ours:"1.125",baseline:"1.125",delta:"0"}],verdict:"表示、编译后结果和检查成本三项全部相同，符号逻辑没有留下独立优势。"},
  "active-causal-minimal-rollback":{ours:"主动选择干预组合，利用已经观察到的结果学习下一次测试，寻找最小故障更新集。",baseline:"不学习，只用标准的二元稀疏组测试逐步缩小故障范围。",matched:"24 个冻结的 4–8 update 稀疏故障案例；两边看到相同信息并按逐例测试次数比较。",rows:[{metric:"找对最小故障集",ours:"24/24",baseline:"24/24",delta:"0"},{metric:"平均测试次数",ours:"5.708",baseline:"5.708",delta:"0"},{metric:"配对检验",ours:"p=1.0",baseline:"逐例完全一致",delta:"无差异"}],verdict:"相对 ddmin 的 62% 节省确实存在，但它全部来自标准稀疏组测试，不来自主动因果学习。"},
  "counterfactual-evolution-decision-controller":{ours:"用同状态下 continue／commit／rollback／stop 四个反事实结果训练线性控制器。",baseline:"只用相同 4 个原始状态特征，训练 depth=3、13 个节点的浅 CART 树。",matched:"hidden 16 个状态；两边的模型与阈值都只由 train/calibration 决定，再同时打开 hidden。",rows:[{metric:"隐藏动作正确",ours:"16/16",baseline:"16/16",delta:"0"},{metric:"平均 / 最坏 regret",ours:"0 / 0",baseline:"0 / 0",delta:"0"},{metric:"四动作分布",ours:"6/2/6/2",baseline:"6/2/6/2",delta:"逐项相同"}],verdict:"浅树在 16 个状态上逐项复现控制器动作，连 regret 和动作分布都相同，因此不再做真实 GPU replay。"},
};
const SUPPLEMENTAL_SIMPLE_METHOD_GUIDES_ZH = {
  "bounded-probe-api-transition-operator":{input:"当前 API 状态、要执行的 create/update/delete 操作，以及文档中明确写出的前置条件、正常效果和异常码。",steps:"把文档规则直接写成 if/then：先检查前置条件；满足就按 effect 更新状态；命中 duplicate/permission/not-found 等 exception 就走对应恢复分支。每种操作都是确定性状态机。",output:"操作后的状态、成功/失败码，以及失败后下一步恢复动作。",omits:"不训练状态转移模型，也不从探针数据学习隐藏表示。"},
  "interventional-permission-triage-under-ceiling":{input:"与 learned q 完全相同的 mutation 布尔特征，以及训练干预中该 mutation 是否必须重新授权的标签。",steps:"用单调 DNF 学一组 OR-of-AND 规则：先找少量“条件同时成立就必须重授权”的合取子句，再把这些子句用 OR 合起来；只允许增加风险条件，不用连续分数。",output:"本次工具变更是否触发 re-authorization。",omits:"不拟合线性 q 分数，不学习连续权重；最终只是可读的布尔规则。"},
  "constraint-complete-typed-memory-order-logic":{input:"同一组 memory 类型、两两/多元约束和 active-edge 信息。",steps:"把每种类型组合看成一个 n 元 factor 表：给定当前活跃的类型组合，直接查这个组合允许哪些顺序/动作；多个 factor 同时存在时只保留共同允许项。",output:"当前记忆组合的合法顺序或约束通过/失败。",omits:"不编译符号逻辑程序，不引入额外的规则推理层；只是对相同约束做因子查表。"},
  "active-causal-minimal-rollback":{input:"一个包含 4–8 次更新的失败版本，以及测试某个更新子集时系统是否仍失败。",steps:"使用二元稀疏组测试：先成组撤销一半更新并测试；若失败消失，故障在这组里，就继续二分；若没消失，再测另一组/组合，直到缩到最小故障更新集。",output:"造成失败的最小 update subset。",omits:"不学习‘下一次测哪组最有信息’，测试顺序由固定二分/稀疏组测试规则决定。"},
  "counterfactual-evolution-decision-controller":{input:"与线性控制器相同的 4 个原始状态特征，以及训练状态下四种动作的正确选择。",steps:"训练一棵 depth=3、最多 13 节点的 CART：每个节点用一个特征阈值把状态分开，最多问三层问题；叶子直接输出 continue/commit/rollback/stop 中的多数正确动作。",output:"当前进化状态下一步采取哪一个四选一动作。",omits:"不学习反事实价值函数或连续控制分数，只用浅层阈值树。"},
};
function supplementalTerminalDisplay(idea) {
  const id=idea.idea_id||idea.id||"";
  const specific=SUPPLEMENTAL_TERMINAL_DISPLAY[id]||{};
  const decision=String(idea.p0_decision||"");
  const stopped=decision.startsWith("STOP_");
  return {
    ...specific,
    stopped,
    decision,
    failureLayer:specific.failureLayer||{zh:"方法实现／独立机制",en:"method realization / standalone mechanism"},
    reopen:specific.reopen||{
      zh:"只有新的第一手或独立证据在信息、预算与最强简化基线完全匹配后仍留下稳定的独立增益，才重新人工评审；改名或重复同一实验不足以重开。",
      en:"Reopen human review only if new primary or independent evidence leaves a stable standalone gain after fully matching information, budget, and the strongest simplification; renaming or repeating the same test is insufficient."
    }
  };
}
function renderSupplementalIdeaCard(row) {
  const idea = row.idea;
  const id = idea.idea_id || idea.id || "candidate";
  const source = row.source;
  const sourceIdeas = (idea.source_ids || []).map(currentFinalIdeaById).filter(Boolean);
  const richSource = sourceIdeas[sourceIdeas.length - 1] || idea;
  const title = textOf(idea.title || {});
  const currentFact = textOf(idea.current_fact || {});
  const terminalDisplay = supplementalTerminalDisplay(idea);
  const problem = textOf(idea.purpose || idea.problem || richSource.purpose || {}) || currentFact;
  const method = textOf(idea.core_idea || richSource.core_idea || idea.exact_mechanism || richSource.exact_mechanism || {});
  const intuition = textOf(idea.core_intuition || richSource.core_intuition || terminalDisplay.intuition || idea.changed_assumption || richSource.changed_assumption || {});
  const rationale = textOf(idea.rationale || richSource.rationale || terminalDisplay.rationale || idea.importance || richSource.importance || idea.hypothesis || {}) || problem;
  const methodLogic = textOf(idea.method_logic || richSource.method_logic || terminalDisplay.methodLogic || idea.exact_mechanism || richSource.exact_mechanism || {}) || method;
  const importance = textOf(idea.importance || richSource.importance || {});
  const advantage = textOf(idea.comparative_advantage || richSource.comparative_advantage || terminalDisplay.advantage || richSource.surviving_claim || idea.changed_assumption || richSource.changed_assumption || idea.hypothesis || {}) || method;
  const collision = textOf(idea.collision_boundary || richSource.collision_boundary || terminalDisplay.collision || {} ) || (language === "zh" ? "当前边界由最强同信息基线和最新真实裁决共同限定。" : "The current boundary is fixed by the strongest same-information baseline and the latest real adjudication.");
  const sourceLabel = source === "terminal-independent" ? `${language === "zh" ? "终态独立方法" : "Terminal standalone"} · ${humanReviewStatusLabel(idea.terminal_state || idea.status || "")}${terminalDisplay.stopped ? (language === "zh" ? " · 当前已停止" : " · currently stopped") : ""}` : (source === "final-merged" ? (language === "zh" ? "FINAL20 合并审查后独立保留" : "Independent after FINAL20 merge audit") : `${language === "zh" ? "网络灵感" : "internet-inspired"} · ${String(idea.external_verdict || idea.final_status || "pending").toUpperCase()}`);
  const code = idea.code || (language === "zh" ? "新增候选" : "new candidate");
  const canonicalItem = canonicalResearchItemByCode(code) || {};
  const canonicalAction = canonicalItem.primary_next_action || {};
  const canonicalActionClass = String(canonicalAction.action_class || "");
  const canonicalActionText = language === "zh" ? String(canonicalAction.action_zh || canonicalAction.action || "") : String(canonicalAction.action || canonicalAction.action_zh || "");
  const baseline = textOf(idea.strongest_baseline || richSource.strongest_baseline || {});
  const currentRole = currentFact || (source === "terminal-independent" ? (language === "zh" ? "人工终态曾将它保留为独立方法并进入 P0 lifecycle；这是历史 lineage，不代表当前可执行。2026-08-16 的执行结论以上方 unified current-status ledger / Experiment terminal ledger 为准。" : "The human-terminal ledger historically retained this as a standalone method and entered it into the P0 lifecycle. That is lineage, not current executability; use the 2026-08-16 unified current-status / experiment terminal ledger for the current decision.") : source === "final-merged" ? (language === "zh" ? "FINAL 去重后仍不能合理并入已有方向，因此暂时作为独立 Idea 保留，等下一轮人工讨论。" : "After FINAL deduplication this still does not merge cleanly into an existing direction, so it remains independent pending human review.") : (language === "zh" ? "这是新增候选，还没有完成当前轮人工讨论；先判断问题是否真实、方法是否有实质，再决定保留或合并。" : "This is a new candidate that has not completed human review; first test whether the problem is real and the method substantive, then keep or merge it."));
  const briefing=language==="zh"?(SUPPLEMENTAL_BRIEFING_ZH[id]||{tone:"simple",label:"当前独立方法已收口",why:currentRole,learned:"保留有效的诊断、协议或工程资产。"}):{tone:"simple",label:"Standalone method is closed",why:currentRole,learned:"Useful diagnostics, protocol, or engineering assets are retained."};
  const terminalPanel=source === "terminal-independent" ? `<section class="supplemental-terminal-panel"><b>${language === "zh" ? "当前终态、停止原因与重开条件" : "Current terminal state, stop reason, and reopen condition"}</b><div><span><strong>${language === "zh" ? "当前状态" : "Current state"}</strong>${terminalDisplay.stopped ? (language === "zh" ? "已停止独立升级；历史 P0 仅作谱系记录" : "Standalone escalation stopped; historical P0 is lineage only") : humanReviewStatusLabel(idea.terminal_state || idea.status || "")}</span><span><strong>${language === "zh" ? "失败层" : "Failure layer"}</strong>${esc(textOf(terminalDisplay.failureLayer))}</span><span><strong>${language === "zh" ? "为什么停止" : "Why it stopped"}</strong>${esc(currentRole)}</span><span><strong>${language === "zh" ? "什么情况下重开" : "Reopen only if"}</strong>${esc(textOf(terminalDisplay.reopen))}</span></div>${terminalDisplay.decision ? `<small>${esc(terminalDisplay.decision)}</small>` : ""}</section>` : "";
  const experimentIdea={...idea,decisive_metric:idea.decisive_metric||terminalDisplay.metric,success_gate:idea.success_gate||terminalDisplay.reopen};
  const supplementalComparison=language==="zh"?SUPPLEMENTAL_SIMPLE_COMPARISONS_ZH[id]:null;
  const oneMinute=language==="zh"?(SUPPLEMENTAL_ONE_MINUTE_ZH[id]||null):null;
  const supplementalObserved=oneMinute?.observed||supplementalComparison?.verdict||briefing.why;
  const supplementalHuman=oneMinute?.human||(language==="zh"?(briefing.tone==="support"?"希望人工判断：当前缺的是更多真实交互/更稳定的任务支持，还是假设本身要求了一个并不存在的稳定结构；先决定补证据还是收缩问题。":briefing.tone==="simple"?"希望人工检查：简单方法已经解释到什么程度，复杂方法还剩哪个会改变决策的变量；如果没有，就不要为复杂机制追加实验。":"希望人工检查当前停止理由是否仍覆盖最新证据，以及保留下来的部分最适合并入哪个父方向。") : "");
  const supplementalExplanation=oneMinute?.next||(language==="zh"?`先按上面的人工判断确定唯一需要补的事实；如果缺真实任务实验，就先做最小、未触碰留出集的验证；如果简单方法已经充分解释，就直接保留为基线/审计资产。原始重开边界：${textOf(terminalDisplay.reopen)}`:textOf(terminalDisplay.reopen));
  const supplementalNext=canonicalActionClass?`${canonicalActionClass} · ${canonicalActionText}`:supplementalExplanation;
  return `<details class="supplemental-idea-card" id="new-${esc(id)}" data-research-code="${esc(code)}" data-briefing-reason="${esc(briefing.tone)}"><summary><div><span>${esc(code)}</span><b>${esc(title)}</b><small>${esc(sourceLabel)}</small></div><div class="supplemental-summary-brief"><strong class="briefing-reason-pill tone-${esc(briefing.tone)}">${esc(briefing.label)}</strong><p>${esc(briefing.why)}</p></div></summary><div class="supplemental-human-grid"><section class="supplemental-briefing-section one-minute-briefing"><header><b>${language==="zh"?"【1min结论】":"【1 min summary】"}</b><span>${esc(briefing.label)}</span></header><div class="one-minute-briefing-grid"><section class="briefing-scene" data-briefing-part="scene"><b>${language==="zh"?"① 具体任务场景：到底在做什么？":"① Concrete task scene"}</b><p>${esc(oneMinute?.scene||(language==="zh"?`${problem} ${method?`当前设计准备这样做：${method}`:"当前没有已经运行的独立任务实验；这里只能说明问题和设计边界。"}`:problem))}</p></section><section data-briefing-part="progress"><b>${language==="zh"?"② 生命周期 + 我们实际做到哪":"② Lifecycle + actual work"}</b><p>${esc(oneMinute?.progress||`${sourceLabel}；${language==="zh"?"当前判断":"current decision"}=${currentRole}`)}</p></section><section data-briefing-part="observed"><b>${language==="zh"?"③ 实验实际看到了什么":"③ What the experiment observed"}</b><p>${esc(supplementalObserved)}</p></section><section data-briefing-part="judgment"><b>${language==="zh"?"④ 所以现在能确定什么，还不能确定什么":"④ What is / is not established"}</b><p>${esc(oneMinute?.judgment||(language==="zh"?`${briefing.why} ${briefing.learned}`:briefing.learned))}</p></section><section class="briefing-human" data-briefing-part="human"><b>${language==="zh"?"⑤ 当前最需要解决的问题 / 希望人工判断什么":"⑤ Human decision needed"}</b><p>${esc(supplementalHuman||briefing.why)}</p></section><section class="briefing-next" data-briefing-part="next"><b>${language==="zh"?"⑥ Research OS 唯一内部动作":"⑥ Canonical Research OS action"}</b><p>${esc(supplementalNext)}</p>${canonicalActionClass?`<small>${language==="zh"?"历史建议 / 重开解释：":"Historical guidance / reopen explanation: "}${esc(supplementalExplanation)}</small>`:""}</section></div></section>${renderConcreteMethodComparison(SUPPLEMENTAL_SIMPLE_COMPARISONS_ZH[id],"supplemental",SUPPLEMENTAL_SIMPLE_METHOD_GUIDES_ZH[id])}<details class="supplemental-complete-intro"><summary>${language==="zh"?"完整 Idea 介绍":"Complete idea introduction"}</summary><div class="supplemental-intro-grid"><section><b>${language === "zh" ? "这个 Idea 在解决什么" : "What problem is this solving?"}</b><p>${esc(problem)}</p></section><section><b>${language === "zh" ? "最简单的直觉" : "Plain-language intuition"}</b><p>${esc(intuition)}</p></section><section><b>${language === "zh" ? "具体准备怎么做" : "What would we actually do?"}</b><p>${esc(method || methodLogic)}</p></section><section><b>${language === "zh" ? "为什么值得试" : "Why might this work?"}</b><p>${esc(rationale || importance || problem)}</p></section></div></details>${terminalPanel}<details class="human-technical-details supplemental-technical-details"><summary>${language === "zh" ? "方法细节与论文边界" : "Method details and paper boundary"}<small>${language === "zh" ? "审方法或 novelty 时再展开" : "Open for method/novelty review"}</small></summary><div class="human-evidence-grid"><section><h4 data-toc="false">${language === "zh" ? "方法步骤" : "Method steps"}</h4><p>${esc(methodLogic)}</p></section><section><h4 data-toc="false">${language === "zh" ? "为什么重要" : "Why it matters"}</h4><p>${esc(importance || rationale || problem)}</p></section><section><h4 data-toc="false">${language === "zh" ? "相比简单方法多了什么" : "What it adds"}</h4><p>${esc(advantage)}</p></section><section><h4 data-toc="false">${language === "zh" ? "最近工作与真正边界" : "Nearest work and real boundary"}</h4><p>${esc(collision)}</p></section><section><h4 data-toc="false">${language === "zh" ? "最强对照" : "Strongest baseline"}</h4><p>${baseline}</p></section><section><h4 data-toc="false">${language === "zh" ? "当前判断" : "Current role"}</h4><p>${esc(currentRole)}</p></section></div></details>${renderIdeaExperimentSection(experimentIdea,{status:source === "terminal-independent" ? (idea.terminal_state || idea.status || "new-review") : "new-review"},sourceIdeas)}</div></details>`;
}
function renderNewIdeaCandidates() {
  const ledger = humanTerminalState();
  const discovery = [...(window.RESEARCH_SYSTEM_STATE?.idea_discovery_v3?.all_children || []),...(window.RESEARCH_SYSTEM_STATE?.idea_discovery_v31?.children || [])];
  const rows = Object.entries(ledger.independent_methods || {}).map(([id,terminal]) => {
    const rich = currentFinalIdeaById(id) || discovery.find((idea) => (idea.idea_id || idea.id) === id) || {};
    return {source:"terminal-independent",idea:{...rich,...terminal,id,idea_id:id,status:terminal.terminal_state,group:terminal.group || supplementalGroupId({...rich,...terminal,id})}};
  });
  const groups = humanReviewData().groups || [];
  const intro = language === "zh" ? `这里只保留 2026-08-11 terminal ledger 明确认定仍可独立存在的 ${rows.length} 个方法。已吸收的 ${ledger.summary?.absorbed_children || 0} 个 child 不再作为独立 Idea、独立 P0 或 advisor 候选；历史版本只用于追溯。` : `Only the ${rows.length} methods explicitly retained as standalone by the 2026-08-11 terminal ledger remain here. The ${ledger.summary?.absorbed_children || 0} absorbed children no longer appear as standalone ideas, P0s, or advisor candidates; history remains traceable.`;
  const head = `<section class="panel supplemental-overview"><div class="idea-panel-heading"><div><p class="section-intro">${intro}</p></div><strong>${rows.length} ${language === "zh" ? "个独立方法" : "standalone methods"}</strong></div></section>`;
  return head + groups.map((group) => { const subset=rows.filter((row)=>(row.idea.group || supplementalGroupId(row.idea))===group.id); if(!subset.length) return ""; return `<section class="supplemental-group" id="new-group-${esc(group.id.toLowerCase())}"><header><span>${esc(group.id)}</span><div><h3>${textOf(group.title)}</h3><p>${language === "zh" ? "只展示未被吸收、仍有独立实验身份的方法。" : "Only unabsorbed methods with a standalone experimental identity are shown."}</p></div><strong>${subset.length}</strong></header><div class="supplemental-list">${subset.map(renderSupplementalIdeaCard).join("")}</div></section>`; }).join("");
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
function p0RuntimeExecutions() {
  const runtime = p0RuntimeReadiness();
  if (Array.isArray(runtime.execution_states) && runtime.execution_states.length) return runtime.execution_states;
  return runtime.execution_state?.status ? [runtime.execution_state] : [];
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
function preGpuCandidateGateState() {
  return window.RESEARCH_SYSTEM_STATE?.pre_gpu_candidate_gates || {summary:{},policy:{},candidates:[],small_p0_candidates:[],shared_p0:{}};
}
function preGpuIdeaTitle(ideaId) {
  const rows = window.RESEARCH_SYSTEM_STATE?.idea_discovery_v3?.shortlist || [];
  const idea = rows.find((row) => row.id === ideaId);
  return idea ? textOf(idea.title) : ideaId;
}
function preGpuGateMeta(value) {
  const map = {
    pass:{tone:"pass",zh:"PASS",en:"PASS"},
    conditional:{tone:"check",zh:"CONDITIONAL",en:"CONDITIONAL"},
    hold:{tone:"hold",zh:"HOLD",en:"HOLD"},
    stop:{tone:"fail",zh:"STOP",en:"STOP"},
    "not-run":{tone:"planned",zh:"NOT RUN",en:"NOT RUN"},
  };
  return map[value] || {tone:"planned",zh:String(value || "--").toUpperCase(),en:String(value || "--").toUpperCase()};
}
function preGpuDecisionMeta(value) {
  const map = {
    "small-p0":{tone:"ready",zh:"进入真正小 P0",en:"True small P0"},
    hold:{tone:"hold",zh:"HOLD · 不耗 GPU",en:"HOLD · no GPU"},
    stop:{tone:"fail",zh:"STOP 当前 thesis",en:"STOP current thesis"},
    secondary:{tone:"check",zh:"并入 #3 次要分析",en:"Secondary inside #3"},
  };
  return map[value] || {tone:"planned",zh:String(value || "--"),en:String(value || "--")};
}
function renderPreGpuCandidateGateBoard() {
  const gate = preGpuCandidateGateState();
  const rows = gate.candidates || [];
  if (!rows.length) return "";
  const summary = gate.summary || {};
  const shared = gate.shared_p0 || {};
  const qualification = shared.qualification || {};
  const blockedAttempt = qualification.blocked_attempt;
  const signal = shared.signal_stage || {};
  const fullQwen = shared.full_qwen_stage || {};
  const offline = shared.offline_analysis || {};
  const offlineDecision = offline.decision || {};
  const idea3Frozen = offlineDecision.idea_3 || {};
  const idea5Frozen = offlineDecision.idea_5 || {};
  const support = shared.support_enriched_stage || {};
  const supportProgress = support.progress || {};
  const secondBackbone = shared.second_backbone || {};
  const gateCell = (value) => { const meta=preGpuGateMeta(value); return `<span class="pre-gpu-gate gate-${meta.tone}">${language === "zh" ? meta.zh : meta.en}</span>`; };
  const tableRows = rows.map((row) => {
    const decision=preGpuDecisionMeta(row.decision);
    return `<tr class="pre-gpu-row pre-gpu-decision-${decision.tone}"><td><b>#${row.rank}</b><span>${esc(preGpuIdeaTitle(row.idea_id))}</span><small>${esc(row.idea_id)}</small></td><td>${gateCell(row.offline)}</td><td>${gateCell(row.reality)}</td><td>${gateCell(row.phenomenon)}</td><td><span class="experiment-status-badge status-${decision.tone}">${language === "zh" ? decision.zh : decision.en}</span></td><td><p>${esc(row.reason || "--")}</p><small><b>${language === "zh" ? "下一步" : "Next"}:</b> ${esc(row.next_action || "--")}</small></td></tr>`;
  }).join("");
  const nominal = shared.target_design || {};
  const smallP0Names = (shared.ideas || []).map((id) => `<b>${esc(preGpuIdeaTitle(id))}</b>`).join(" + ");
  const secondary = (shared.secondary_analysis || []).map((id) => esc(preGpuIdeaTitle(id))).join(" · ");
  const qualTone = qualification.status === "pass" ? "pass" : qualification.status === "running" ? "running" : "check";
  const qualLabel = qualification.status === "pass" ? (language === "zh" ? "底座资格已通过" : "Substrate qualified") : esc(String(qualification.status || "pending").toUpperCase());
  const blocked = blockedAttempt ? `<div class="pre-gpu-blocked-attempt"><b>${language === "zh" ? "已隔离的错误路径运行" : "Isolated wrong-path run"}</b><span>${esc(blockedAttempt.model_path || "--")} · ${blockedAttempt.successes || 0}/${blockedAttempt.total || 0} · ${experimentNumber((blockedAttempt.success_rate || 0) * 100)}%</span><p>${language === "zh" ? "这是模型路径／runtime 选择问题，只保留为操作证据，不产生 #3/#5 科学结论。" : "This is a model-path/runtime selection issue retained as operational evidence only; it produces no scientific conclusion for #3/#5."}</p></div>` : "";
  return `<section class="panel pre-gpu-candidate-board" id="pre-gpu-candidate-gates"><div class="idea-panel-heading"><div><div class="eyebrow">GPU-0 · OFFLINE → REALITY → PHENOMENON</div><h2 data-toc="false">${language === "zh" ? "10 个存活项的 GPU 前置门：10 → 2" : "Pre-GPU gates for the ten survivors: 10 → 2"}</h2><p class="section-intro">${language === "zh" ? "先用不消耗 GPU 的证据判断可计算性、真实问题与现象是否成立。HOLD/INCONCLUSIVE 不更新负面科学信念；当前 thesis 已被直接碰撞或可约简时才 STOP。只有三门真正通过的方向才进入小 P0。" : "Before any GPU spend, test offline realizability, problem reality, and phenomenon evidence. HOLD/INCONCLUSIVE does not update negative scientific belief; STOP is reserved for a collided or reducible current thesis. Only candidates clearing the required gates enter a small P0."}</p></div><strong>${summary.small_p0 || 0}/${summary.total || 0}<span>${language === "zh" ? "真正小 P0" : "true small P0"}</span></strong></div><div class="pre-gpu-summary"><span><b>${summary.small_p0 || 0}</b>${language === "zh" ? "小 P0" : "small P0"}</span><span><b>${summary.hold || 0}</b>HOLD</span><span><b>${summary.stop || 0}</b>STOP</span><span><b>${summary.secondary || 0}</b>${language === "zh" ? "并入分析" : "secondary"}</span></div><div class="advisor-table-scroll"><table class="matrix pre-gpu-table"><thead><tr><th>Idea</th><th>Offline</th><th>Reality</th><th>Phenomenon</th><th>${language === "zh" ? "决定" : "Decision"}</th><th>${language === "zh" ? "证据与下一步" : "Evidence and next"}</th></tr></thead><tbody>${tableRows}</tbody></table></div><article class="shared-p0-card"><header><div><span>${esc(shared.id || "P0-MEM-XFER-CAUSAL")}</span><h3 data-toc="false">${language === "zh" ? "两项共享一套 treatment table" : "One treatment table for both methods"}</h3></div><span class="experiment-status-badge status-${qualTone}">${qualLabel}</span></header><p>${smallP0Names}</p><div class="shared-p0-grid"><section><b>${language === "zh" ? "核心干预单元" : "Core intervention unit"}</b><p>${esc(shared.core_unit || "--")}</p></section><section><b>${language === "zh" ? "目标规模" : "Target design"}</b><p>${nominal.task_families || 0} families × ${nominal.future_tasks_per_family || 0} tasks × ${nominal.arms || 0} arms × ${nominal.frozen_open_models || 0} models = <strong>${nominal.nominal_core_executions || 0}</strong> core executions；${language === "zh" ? "先跑 24-execution signal stage，不直接吃满预算。" : "start with a 24-execution signal stage rather than consuming the full budget."}</p></section><section><b>#3 ${language === "zh" ? "主看" : "reads"}</b><p>${(shared.p0_3_metrics || []).map(esc).join(" · ")}</p></section><section><b>#5 ${language === "zh" ? "主看" : "reads"}</b><p>${(shared.p0_5_metrics || []).map(esc).join(" · ")}</p></section><section><b>${language === "zh" ? "底座资格" : "Substrate qualification"}</b><p>${qualification.successes || 0}/${qualification.total || 0} = ${experimentNumber((qualification.success_rate || 0) * 100)}% · ${qualification.task_types_with_success || 0} task families · ${esc(qualification.model_path || "Qwen2.5-7B-Instruct")}</p></section><section><b>${language === "zh" ? "次要分析" : "Secondary analysis"}</b><p>${secondary || "--"}</p></section><section><b>${language === "zh" ? "Signal 结果" : "Signal result"}</b><p><strong>${esc(String(signal.decision || signal.status || "--"))}</strong> · ${signal.completed_executions || 0}/${signal.planned_executions || 0} executions · disagreement ${signal.outcome_disagreement_units || 0}/${signal.complete_units || 0}<br>${language === "zh" ? "retrieved 有害/有益" : "retrieved harm/benefit"} ${signal.retrieved_harm_units || 0}/${signal.retrieved_benefit_units || 0} · placebo changed ${signal.placebo_nonzero_units || 0} · ${experimentNumber(signal.gpu_hours || 0)} GPUh</p></section><section><b>${language === "zh" ? "Full Qwen 表" : "Full Qwen table"}</b><p><strong>${esc(String(fullQwen.status || "--").toUpperCase())}</strong> · ${fullQwen.completed_executions || 0}/${fullQwen.planned_executions || 0} executions · ${fullQwen.completed_units || 0}/32 units<br>disagreement ${fullQwen.outcome_disagreement_units || 0} · harm/benefit ${fullQwen.retrieved_harm_units || 0}/${fullQwen.retrieved_benefit_units || 0} · placebo nonzero ${fullQwen.placebo_nonzero_units || 0} · controlled nonzero ${fullQwen.controlled_nonzero_units || 0}</p></section><section><b>#3 ${language === "zh" ? "冻结判定" : "frozen verdict"}</b><p><span class="experiment-status-badge status-check">PHENOMENON PASS / METHOD INCONCLUSIVE</span><br>${esc(idea3Frozen.reason || "candidate_support_insufficient")} · 4 candidates &lt; required 8</p></section><section><b>#5 ${language === "zh" ? "冻结判定" : "frozen verdict"}</b><p><span class="experiment-status-badge status-check">PHENOMENON PASS / TRANSPORT SUPPORT INSUFFICIENT</span><br>${esc(idea5Frozen.reason || "controlled_effect_support_insufficient")} · 5 controlled nonzero &lt; 12 · 2 eligible target folds &lt; 3</p></section><section><b>${language === "zh" ? "下一轮 Qwen support" : "Next Qwen support stage"}</b><p><span class="experiment-status-badge status-${String(support.status || "").includes("running") ? "running" : String(support.status || "").includes("hold") ? "hold" : String(support.status || "").includes("pass") ? "pass" : "planned"}">${esc(String(support.status || "support_qualification_pending").toUpperCase())}</span><br>${supportProgress.completed_episodes || 0}/${supportProgress.total_episodes || support.support_executions || 72} executions · plan <code>${esc(String(support.plan_hash || "").slice(0,12))}</code></p></section><section><b>${language === "zh" ? "第二 Backbone" : "Second backbone"}</b><p><span class="experiment-status-badge status-hold">${esc(String(secondBackbone.status || "second_model_hold").toUpperCase())}</span><br>${language === "zh" ? "只有 support-enriched Qwen 通过冻结 mechanism/support gate 后才允许 qualification。" : "Qualification remains locked until the support-enriched Qwen mechanism/support gate passes."}</p></section></div>${blocked}<div class="shared-p0-next"><b>${language === "zh" ? "当前下一门" : "Current next gate"}</b><span>${esc(shared.next_gate || "--")}</span></div></article></section>`;
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
  const admission = window.RESEARCH_SYSTEM_STATE?.p0_admission?.summary || {};
  const registry = experimentPilotRegistry();
  return `<section class="panel p0-entry-panel"><div><div class="eyebrow">LEGACY P0 · ${language === "zh" ? "实验终态追溯" : "TERMINAL EXPERIMENT TRACE"}</div><h3 id="experiment-tracker-entry" data-toc="false">${language === "zh" ? `${admission.active_p0 || 0} 个历史 P0 lifecycle 合同由实验页保留终态、证据和权限追溯` : `${admission.active_p0 || 0} legacy P0 lifecycle contracts remain on the experiment page for terminal decisions, evidence, and authority traceability`}</h3><p>${language === "zh" ? "这些 P0 记录表示历史上方法、对照、真值和预算合同曾被冻结，不代表现在仍可启动。当前是否有可执行方向必须看统一 current status ledger；截至 2026-08-16 formal launchable=0。" : "These P0 records mean method/baseline/truth/budget contracts were frozen historically; they do not imply current launchability. Use the unified current-status ledger for execution decisions; as of 2026-08-16 formal launchable=0."}</p></div><div class="p0-entry-stats"><span><b>${admission.active_p0 || 0}</b>${language === "zh" ? "历史 P0" : "legacy P0"}</span><span><b>${admission.transitioned_from_p0_ready || 0}</b>${language === "zh" ? "历史迁入" : "historical transitions"}</span><span><b>${admission.settings_complete || 0}</b>${language === "zh" ? "设置完整" : "settings complete"}</span><span><b>${admission.execution_authorized || 0}</b>${language === "zh" ? "旧 admission 执行位" : "legacy admission execution bits"}</span><span><b>${window.CURRENT_RESEARCH_STATUS?.headline?.launchable_formal_experiments || 0}</b>${language === "zh" ? "当前 formal 可启动" : "current formal launchable"}</span></div><a class="link-btn p0-entry-link" href="experiments.html">${language === "zh" ? "打开当前证据与历史终态 →" : "Open current evidence and terminal history →"}</a></section>`;
}
function renderP0RuntimeReadiness() {
  const runtime = p0RuntimeReadiness();
  const gpu = (runtime.gpus || [])[0] || {};
  const modules = runtime.python_modules || {};
  const supported = new Set(runtime.supported_p0 || []);
  const stages = runtime.stages || {};
  const blockerRows = (runtime.blockers || []).map((item) => `<li>${esc(item)}</li>`).join("");
  const executions = p0RuntimeExecutions();
  const execution = executions.find((row) => String(row.status || "").toLowerCase() === "running") || runtime.execution_state || {};
  const executionStatus = String(execution.status || "").toLowerCase();
  const executionLabels = {running:{zh:"运行中",en:"RUNNING"},collected:{zh:"采集完成",en:"COLLECTED"},registered:{zh:"已登记",en:"REGISTERED"},failed:{zh:"运行失败",en:"FAILED"}};
  const status = executionStatus === "running" ? {tone:"running",zh:"真实 P0 运行中",en:"Real P0 running"} : executionStatus === "collected" ? {tone:"check",zh:"采集完成，待登记",en:"Collected; registration pending"} : executionStatus === "registered" ? {tone:"pass",zh:"P0 结果已登记",en:"P0 result registered"} : executionStatus === "failed" ? {tone:"fail",zh:"P0 运行失败",en:"P0 execution failed"} : runtime.launch_ready ? {tone:"pass",zh:"可启动真实 P0",en:"P0 launch ready"} : (runtime.environment_ready ? {tone:"check",zh:"环境通过，待 smoke",en:"Runtime ready; smoke pending"} : {tone:"revise",zh:"环境未就绪",en:"Runtime not ready"});
  const executionLabel = executionLabels[executionStatus] || {zh:"未启动",en:"PENDING"};
  const liveRuns = executions.map((row) => {
    const progress = row.progress || {};
    const runStatus = String(row.status || "pending").toUpperCase();
    const candidateProgress = progress.candidates_total ? ` · ${progress.candidates_completed || progress.candidate_index || 0}/${progress.candidates_total} candidates` : "";
    return `<div><b>${esc(row.idea_id || "runtime")}</b><span>${esc(runStatus)} · ${esc(progress.stage || row.stage || "--")} · ${experimentNumber(progress.environment_episodes || 0)} episodes · ${experimentNumber(progress.model_calls || 0)} calls · ${experimentNumber(progress.elapsed_hours || 0)}h${candidateProgress}</span></div>`;
  }).join("");
  const stageRows = [
    ["harness_ready", language === "zh" ? "Harness" : "Harness"],
    ["package_ready", language === "zh" ? "ALFWorld + TextWorld" : "ALFWorld + TextWorld"],
    ["data_ready", language === "zh" ? "PDDL / game 数据" : "PDDL / game data"],
    ["smoke_rollout_ready", language === "zh" ? "轻量 runtime smoke" : "lightweight runtime smoke"],
  ].map(([key,label],index) => `<span class="runtime-stage ${stages[key] ? "stage-pass" : "stage-pending"}"><i>${index+1}</i><b>${esc(label)}</b><small>${stages[key] ? (language === "zh" ? "通过" : "PASS") : (language === "zh" ? "未完成" : "PENDING")}</small></span>`).join("") + `<span class="runtime-stage ${executionStatus === "failed" ? "stage-fail" : (stages.p0_execution_started ? "stage-pass" : "stage-pending")}"><i>5</i><b>${language === "zh" ? "正式 P0" : "formal P0"}</b><small>${language === "zh" ? executionLabel.zh : executionLabel.en}</small></span>`;
  return `<section class="panel experiment-runtime-panel"><div class="idea-panel-heading"><div><h3 id="p0-runtime-readiness" data-toc="false">${language === "zh" ? "P0 运行环境 readiness" : "P0 runtime readiness"}</h3><p class="section-intro">${language === "zh" ? "科学授权、harness、依赖、数据、轻量 runtime smoke 和正式实验分开记账。轻量 smoke 只验证 Qwen tokenizer/chat template、各权重 shard 可读，以及真实 ALFWorld OOD 的 reset → parser → env.step；完整 7B 权重加载与生成只在正式 P0 事务里验证，失败不会登记科学结果。" : "Scientific authorization, harness, dependencies, data, a lightweight runtime smoke, and formal execution are tracked separately. The smoke checks the Qwen tokenizer/chat template, readability of every weight shard, and a real ALFWorld OOD reset → parser → env.step. Full 7B loading/generation is validated only by the formal P0 transaction, and failures cannot be registered as scientific results."}</p></div><span class="experiment-status-badge status-${status.tone}">${language === "zh" ? status.zh : status.en}</span></div><div class="experiment-runtime-stages">${stageRows}</div>${liveRuns ? `<div class="experiment-live-runs">${liveRuns}</div>` : ""}<div class="experiment-runtime-grid"><div><b>${gpu.name ? esc(gpu.name) : "--"}</b><span>${gpu.memory_free_mib ? `${Math.round(gpu.memory_free_mib/1024)} GB ${language === "zh" ? "空闲显存" : "VRAM free"}` : (language === "zh" ? "未检测到 GPU" : "No GPU detected")}</span></div><div><b>${runtime.model?.ready ? "YES" : "NO"}</b><span>${language === "zh" ? "Qwen2.5-7B 本地模型" : "local Qwen2.5-7B"}</span></div><div><b>${experimentNumber(runtime.data_disk_free_gib || 0)} GB</b><span>${language === "zh" ? "实验数据盘空闲" : "experiment disk free"}</span></div><div><b>${supported.has("update-trust-region") ? "YES" : "NO"}</b><span>A-1 harness</span></div><div><b>${supported.has("budgeted-evolution-controller") ? "YES" : "NO"}</b><span>A-2 harness</span></div><div><b>${Object.values(modules).filter(Boolean).length}/${Object.keys(modules).length || 3}</b><span>${language === "zh" ? "Python 运行依赖" : "Python runtime deps"}</span></div><div><b>${runtime.alfworld_data?.ready ? "YES" : "NO"}</b><span>${language === "zh" ? "ALFWorld PDDL / game 数据" : "ALFWorld PDDL / game data"}</span></div></div>${blockerRows ? `<div class="experiment-runtime-blockers"><b>${language === "zh" ? "当前阻塞" : "Current blockers"}</b><ul>${blockerRows}</ul></div>` : (runtime.smoke_rollout?.ready ? `<div class="experiment-runtime-ready">${language === "zh" ? "机器依赖、数据和轻量 runtime smoke 均通过；已授权 P0 现在可以启动，但尚未产生任何实验效果。" : "Machine dependencies, data, and the lightweight runtime smoke all pass; authorized P0s may now launch, but no experimental effect has been measured yet."}</div>` : `<div class="experiment-runtime-blockers"><b>${language === "zh" ? "下一步" : "Next"}</b><ul><li>${language === "zh" ? "先完成轻量 runtime smoke：Qwen tokenizer/权重 shard 可读 + ALFWorld OOD 单步链路；通过后 collect 才解锁。" : "First clear the lightweight runtime smoke: Qwen tokenizer/weight-shard readability plus one ALFWorld OOD environment step; collection unlocks only after it passes."}</li></ul></div>`)}</section>`;
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
  const runtimeExecutions = p0RuntimeExecutions();
  const rows = (plan.ideas || []).map((item) => {
    const phase = experimentPilotPhase(item.id,"P0");
    const result = phase?.result;
    const runtimeExecution = runtimeExecutions.find((row) => row.idea_id === item.id) || {};
    const liveStatus = String(runtimeExecution.status || "").toLowerCase();
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
  const auditNotice=`<section class="panel experiment-audit-notice"><div><div class="eyebrow">${language==="zh"?"非主导航 · 技术审计":"DEEP AUDIT · NOT A PRIMARY NAVIGATION SURFACE"}</div><h2 data-toc="false">${language==="zh"?"科学结论统一回到 ResearchItem；这里只查原始实验细节":"Scientific decisions live on ResearchItems; this page keeps experiment-level forensic detail"}</h2><p>${language==="zh"?"如果只是想知道某个方向是什么、做过什么实验、为什么停止或怎样重开，请回 Research Portfolio。这里保留冻结协议、运行状态、资源、审批与历史工件，避免它们再次形成一套平行状态。":"Use the Research Portfolio to understand what an item studies, which experiments matter, why it stopped, or how it can reopen. This audit keeps frozen protocols, runtime, resources, approvals, and historical artifacts without creating a parallel current-state model."}</p></div><a class="link-btn" href="paper-ideas.html">${language==="zh"?"← 回到 Research Portfolio":"← Back to Research Portfolio"}</a></section>`;
  return `${pageHeader(config)}${auditNotice}${renderArchitectureOverview(pageArchitecture("experiments"))}${renderCustomChapter(chapters[0],0,renderExperimentMasterBoard())}${renderCustomChapter(chapters[1],1,renderExperimentCurrentEvidenceHub())}${renderCustomChapter(chapters[2],2,renderExperimentTraceabilityHub())}`;
}
const CANONICAL_PF_GROUPS = {
  A:["PF-1","PF-4","PF-5","PF-6","PF-7"],
  B:["PF-3"],
  C:["PF-8"],
  D:[],
  E:["PF-2","PF-9"],
  F:[],
  G:[]
};
const CANONICAL_CONTEXT_GROUP_COUNTS = {A:0,B:2,C:0,D:0,E:4,F:0,G:0};
const CATEGORY_BRIEFING_ZH = {
  A:{focus:"研究一次更新什么时候值得保留，以及怎样尽早发现它会不会让旧能力变差、和其他更新冲突，或需要回滚。",reason:"在拿到相同信息时，固定规则、直接风险评分或普通版本管理已经达到相近效果，复杂控制器暂时没有证明额外价值。",survives:"仍然有用的是：运行前资格检查、回归测试集、同信息简单基线，以及低成本审计调度。"},
  B:{focus:"研究哪些记忆与经验值得长期保存、迁移和复用，以及它们在什么情况下会失效。",reason:"有些方案缺少足够真实交互来验证；另一些用简单缓存、前置条件或回归准入就能做到相近效果。",survives:"仍值得保留：先验证经验是否真的有效、记录适用边界、优先审计高风险记忆，以及可回滚的压缩和清理机制。"},
  C:{focus:"研究 Agent 使用自身评价、奖励或纠错信号持续更新时，怎样避免错误评价被一轮轮放大。",reason:"不少复杂的评价器修复或纠错机制，用冻结参考标准、降低可疑来源权重或简单规则就能达到相近效果，暂未证明复杂机制是必要的。",survives:"仍然有用的是：记录标签从哪里来、比较不同版本的评分变化，并保留独立于 Agent 自身的真值检查。"},
  D:{focus:"研究失败之后应该生成什么新任务，才能真正带来新信息，而不是重复已经知道的东西。",reason:"目前复杂的课程最小化、前沿维护和漂移控制，没有稳定超过直接过滤或成功率预测；自动课程生成的基础能力也还不够稳定。",survives:"仍值得保留：可靠的反例生成、任务难度随版本变化的诊断，以及课程分布漂移监控。"},
  E:{focus:"研究多节点工作流、API 和系统结构发生变化时，怎样判断改动是否真的有效，并把效果归因到正确的结构变化。",reason:"一些结构编辑没有产生可测差异；另一些复杂方法，被直接编辑、明确接口规则或简单权限控制做到相近效果。",survives:"仍然保留：配对编辑实验、工作流证据链、明确的接口约束，以及已经形成论文的 STRI 结果。"},
  F:{focus:"研究世界模型和具身 Agent 遇到环境变化或执行失败后，哪些误差和恢复经验值得长期学下来。",reason:"目前提出的价值门控、前置条件和恢复模块，分别可以被更直接的动作差异检测、安全屏障或恢复策略做到相近效果。",survives:"仍然有用的是：不可逆风险的解释、恢复过程的可复现审计，以及简单、可检查的运行时安全策略。"},
  G:{focus:"研究 Agent 的记忆和持久状态继续变化以后，今天看起来安全的 Agent，未来是否会更容易第一次违规。",reason:"核心科学问题仍然开放，但当前模型和运行环境里，没有足够多“现在都安全、其他条件又能匹配”的状态，因此暂时无法做公平的因果比较。",survives:"保留 G-1 和明确的重开条件；其他风险维度并入安全审计、对照基线和治理清单。"},
};
function renderResearchBriefingGuide(inventory) {
  const taxonomy=Object.values(IDEA_STOP_TAXONOMY).map(row=>`<article class="briefing-taxonomy-card tone-${esc(row.tone)}"><span></span><b>${esc(textOf(row))}</b><p>${language==="zh"?({simple:"问题可能真实，但复杂方法没有超过最强简单对照。",support:"现在还不能公平判断方法；需要先补数据、有效更新或合格底座。",identify:"实验结果无法说明收益是否来自声称的新机制。",collision:"问题存在，但已被最近工作或成熟理论基本覆盖。",merge:"有价值的部分保留为更大方向的组件、基线或审计项。",principle:"在有效实验下，关键预测被直接否定；除非出现推翻证据，否则不再重开。"}[row.tone]):({simple:"The idea may matter, but the complex method did not beat the strongest simple control.",support:"The method cannot yet be judged fairly; data or a qualified substrate is missing.",identify:"The experiment cannot attribute an effect to the claimed mechanism.",collision:"The problem is real, but prior work or mature theory already covers the same decision object.",merge:"Useful parts survive as a component, baseline, or audit item inside a larger direction.",principle:"A valid test contradicted the key prediction; reopening requires overturning evidence."}[row.tone])}</p></article>`).join("");
  const standard=language==="zh"?`<section class="one-minute-writing-standard" id="one-minute-writing-standard"><header><div><span>【1min结论】统一写作标准</span><h3 data-toc="false">它不是缩短版技术审计，而是一张可以直接拿来讨论下一步的科研决策记忆卡</h3><p>读完一张卡，应该不需要重新进入当时的系统上下文，就能回答：具体任务里发生了什么、我们真的做了什么、看到了什么、现在能下什么结论、希望人工帮忙判断什么、下一步怎么做。</p></div></header><div class="one-minute-reading-path"><b>快速阅读顺序</b><span><strong>30 秒回顾：</strong>① 具体场景 → ③ 实际现象 → ④ 当前判断</span><span><strong>讨论下一步：</strong>再看 ② 实际进度 → ⑤ 希望人工判断 → ⑥ 下一步方案</span></div><div class="one-minute-standard-grid"><article><b>① 具体任务场景</b><p>必须交代模型/Agent、环境、具体任务、为什么发生更新、谁生成更新、改了什么、希望改善什么。不能只写“Agent 修改 Prompt”或“做回归任务”。</p></article><article><b>② 生命周期 + 实际动作</b><p>先给“历史 P0 → 当前 HOLD”这类定位，再翻译成科研动作：哪些数据/任务已准备，哪些实验真的跑过，哪些隐藏测试从未打开。</p></article><article><b>③ 实验实际看到了什么</b><p>数字后面必须解释现实含义；有真实任务工件时至少给一个代表性失败例，必要时再给一个成功例。没有真实运行就明确写“尚未运行”。</p></article><article><b>④ 能确定 / 不能确定</b><p>把事实与解释分开。实验底座失败、支持不足、方法失败、原理失败是不同结论；后台 STOP/Gate 状态码只放技术审计。</p></article><article><b>⑤ 希望人工判断什么</b><p>明确告诉讨论者现在应该看什么材料、比较什么例子、判断哪几个可能原因。页面要让人能直接提出下一步方案，而不只是知道“这个方向停了”。</p></article><article><b>⑥ 下一步方案</b><p>写成可以执行的步骤：先诊断什么 → 修哪里 → 用什么全新样本重验 → 满足什么现象条件后才进入下一阶段。抽象 reopen condition 留在审计层。</p></article></div><div class="one-minute-standard-rules"><b>两条硬规则</b><span>有真实任务就写真实任务，不用专有名词代替场景；没有真实任务/实验就明确说尚未固定或尚未运行，绝不为了“具体”补造案例。</span><span>所有数字都必须说明“在数什么、为什么影响判断”，例如“8 个 Prompt patch 只有 1 个修好目标任务”，而不是只写 effective fraction=12.5%。</span></div></section>`:"";
  return `<section class="panel research-briefing-guide" id="briefing-guide"><div class="briefing-guide-head"><div><div class="eyebrow">${language==="zh"?"1min 汇报视图":"ONE-MINUTE BRIEFING"}</div><h2 data-toc="false">${language==="zh"?"先讲研究判断，再看实验日志":"Research judgments first; experiment logs second"}</h2><p>${language==="zh"?"默认视图给每个方向一段完整的【1min结论】：研究什么、已经做到哪一步、哪条证据形成当前判断、当前留下什么、下一步或什么条件下重开。原始状态码、门禁、完整数值、人工意见和实验协议继续保留在技术审计层。":"The default view gives every direction a one-minute summary: research question, progress, decisive evidence, what survives, and the next step or reopen condition. Raw codes, gates, full metrics, human feedback, and protocols remain in the technical audit layer."}</p></div><div class="briefing-mode-switch" role="group" aria-label="${language==="zh"?"阅读模式":"Reading mode"}"><button class="briefing-mode-btn active" data-briefing-mode="brief" aria-pressed="true">${language==="zh"?"汇报视图":"Briefing"}</button><button class="briefing-mode-btn" data-briefing-mode="audit" aria-pressed="false">${language==="zh"?"完整审计":"Full audit"}</button></div></div>${standard}<div class="briefing-lessons"><article><b>${language==="zh"?"结论 1 · 复杂不等于新增价值":"Lesson 1 · Complexity is not added value"}</b><p>${language==="zh"?"多条路线不是“完全没用”，而是被使用相同信息的简单规则追平，因此不能继续主张独立机制贡献。":"Many routes were not useless; they were matched by simpler rules using the same information, eliminating the standalone mechanism claim."}</p></article><article><b>${language==="zh"?"结论 2 · 先验证底座，再验证高级方法":"Lesson 2 · Qualify the substrate first"}</b><p>${language==="zh"?"如果更新器几乎产不出有效更新，或数据没有足够差异，负结果不能判方法失败，只能停止当前实验实例。":"If an updater rarely produces effective changes or the data lack variation, a negative result stops the current instance rather than falsifying the method."}</p></article><article><b>${language==="zh"?"结论 3 · 历史阶段不是当前权限":"Lesson 3 · Historical stage is not current authority"}</b><p>${language==="zh"?"历史 P0、P0-ready、Paper Design 和 ADVANCE 都保留为谱系；当前真正可执行的正式实验仍是 0。":"Historical P0, P0-ready, Paper Design, and ADVANCE remain lineage; currently launchable formal experiments remain zero."}</p></article></div><h3 data-toc="false">${language==="zh"?"停止原因只看六类":"Six plain-language stop reasons"}</h3><div class="briefing-taxonomy-grid">${taxonomy}</div><small class="briefing-inventory-note">${language==="zh"?`以下仍完整覆盖 ${inventory.total} 个 A–G 去重研究对象；通俗分类不会改写任何原始科学裁决。`:`The ledger below still covers all ${inventory.total} deduplicated A–G objects; plain-language categories never overwrite the scientific adjudication.`}</small></section>`;
}
function canonicalGroupInventory(groupId,parents,independent,closedCounts={}) {
  const projection=window.RESEARCH_ITEM_STATE;
  if(projection?.research_items?.length){
    const items=projection.research_items.filter(row=>row.category===groupId);
    const parent=items.filter(row=>row.source_kind==="parent").length;
    const related=items.filter(row=>["independent_method","paper_first","safety"].includes(row.source_kind)).length;
    const closed=items.filter(row=>row.source_kind==="shadow_closed").length;
    const context=items.filter(row=>row.source_kind==="paper_source").length
      +(projection.experiment_records||[]).filter(row=>row.portfolio_context&&String(row.portfolio_code||"").startsWith(`${groupId}-`)).length
      +(projection.evidence_contexts||[]).filter(row=>row.portfolio_context&&row.category===groupId).length;
    const canonicalTotal=Number(projection.summary?.by_category?.[groupId]?.portfolio_total||0);
    return {parent,related,context,closed,total:canonicalTotal||parent+related+context+closed};
  }
  const parent=parents.filter(row=>row.meta.group===groupId).length;
  const related=independent.filter(row=>(row.idea.group||supplementalGroupId(row.idea))===groupId).length+(CANONICAL_PF_GROUPS[groupId]||[]).length+(groupId==="G"?5:0);
  const context=CANONICAL_CONTEXT_GROUP_COUNTS[groupId]||0;
  const closed=closedCounts[groupId]||0;
  return {parent,related,context,closed,total:parent+related+context+closed};
}
function canonicalInventorySummary(groups,parents,independent) {
  const closedCounts=window.closedCandidateCategoryCounts?window.closedCandidateCategoryCounts():{};
  const closureSummary=window.closedCandidateRecordSummary?window.closedCandidateRecordSummary():{records:0,merged:0,standalone:0};
  const byGroup=Object.fromEntries(groups.map(group=>[group.id,canonicalGroupInventory(group.id,parents,independent,closedCounts)]));
  const sum=key=>Object.values(byGroup).reduce((n,row)=>n+(row[key]||0),0);
  const canonical=window.RESEARCH_ITEM_STATE?.summary||{};
  return {parent:sum("parent"),related:sum("related"),context:sum("context"),closed:sum("closed"),total:Number(canonical.portfolio_objects||sum("total")),closureRecords:closureSummary.records||0,mergedClosures:closureSummary.merged||0,byGroup};
}
function canonicalIdeaGroups() {
  const base=(humanReviewData().groups||[]).map(group=>({...group}));
  return [...base,{id:"G",title:{zh:"Agent 自进化安全与未来风险",en:"Safety and future risk in agent self-evolution"},question:{zh:"当前静态安全检查能否预测持久状态与经验继续演化后的未来首次违规风险？",en:"Can current static safety evaluation predict future first-violation risk after persistent state and experience continue to evolve?"}}];
}
function canonicalIndependentRows() {
  const ledger=humanTerminalState();
  const discovery=[...(window.RESEARCH_SYSTEM_STATE?.idea_discovery_v3?.all_children||[]),...(window.RESEARCH_SYSTEM_STATE?.idea_discovery_v31?.children||[])];
  return Object.entries(ledger.independent_methods||{}).map(([id,terminal])=>{
    const rich=currentFinalIdeaById(id)||discovery.find(idea=>(idea.idea_id||idea.id)===id)||{};
    return {source:"terminal-independent",idea:{...rich,...terminal,id,idea_id:id,status:terminal.terminal_state,group:terminal.group||supplementalGroupId({...rich,...terminal,id})}};
  });
}
function canonicalParentRows() {
  const bank=iclrIdeaBank(), review=humanReviewData(), byId=new Map((bank.passed_ideas||[]).map(idea=>[idea.id,idea]));
  return Object.entries(review.ideas||{}).map(([id,meta])=>{
    const terminal=terminalParentState(id);
    return {id,meta:{...meta,status:terminal?humanParentFinalState(terminal):meta.status,code:terminal?.code||meta.code,group:terminal?.group||meta.group},idea:byId.get(id)};
  }).filter(row=>row.idea);
}
function canonicalStatusControls(rows=[]) {
  const statuses=["hold","stop","merge"];
  return `<div class="canonical-filter-bar"><div><b>${language==="zh"?"筛选 26 个父级研究方向的当前最终状态":"Filter the 26 parent ideas by current final state"}</b><span>${language==="zh"?"P0、P0-ready 与历史 DROP 只作为卡片内的历史里程碑，不再充当当前状态；该筛选不会隐藏其他研究对象。":"P0, P0-ready, and historical DROP remain milestones inside cards rather than current states; this filter does not hide other research objects."}</span></div><div class="canonical-filter-actions">${["all",...statuses].map((status,index)=>{
    const count=status==="all"?rows.length:rows.filter(row=>row.meta.status===status).length;
    const label=status==="all"?(language==="zh"?"全部父级研究方向":"All parent ideas"):humanParentFinalStatusLabel(status);
    return `<button class="canonical-filter-btn${index===0?" active":""}" data-canonical-status="${esc(status)}" aria-pressed="${index===0?"true":"false"}">${esc(label)} <b>${count}</b></button>`;
  }).join("")}</div></div>`;
}
function renderCanonicalCategoryIndex(groups,parents,independent,inventory=canonicalInventorySummary(groups,parents,independent)) {
  return `<section class="panel canonical-category-index" data-research-inventory-total="${inventory.total}"><div class="idea-panel-heading"><div><div class="eyebrow">${language==="zh"?"全部研究对象 · A–G 分类导航":"ALL RESEARCH OBJECTS · A–G INDEX"}</div><h2 id="canonical-category-index">${language==="zh"?"页面呈现全部去重研究对象；关闭裁决也已并入编号研究方向":"The page shows every deduplicated research object, with closure decisions merged into numbered ideas"}</h2><p class="section-intro">${language==="zh"?`当前按 A–G 展示 ${inventory.total} 个去重研究对象：${inventory.parent} 个父级研究方向、${inventory.related} 条关联研究方向/方法、${inventory.closed} 个另行编号的已关闭研究方向，以及 ${inventory.context} 条论文/证据/实验记录。原 ${inventory.closureRecords} 条关闭裁决中有 ${inventory.mergedClosures} 条已合并进既有正式研究方向，其余直接成为同类编号卡片，不再另设“关闭候选档案”表格。`:`The A–G ledger shows ${inventory.total} deduplicated research objects: ${inventory.parent} parent ideas, ${inventory.related} related directions/methods, ${inventory.closed} separately numbered stopped ideas, and ${inventory.context} paper/evidence/experiment records. Of ${inventory.closureRecords} closure decisions, ${inventory.mergedClosures} are merged into existing formal ideas; the rest are peer numbered cards rather than a separate archive table.`}</p></div><strong>${inventory.total}<span>${language==="zh"?"个去重研究对象":"deduplicated objects"}</span></strong></div><nav class="canonical-category-nav" aria-label="${language==="zh"?"研究大类":"Research categories"}">${groups.map(group=>{
    const row=inventory.byGroup[group.id]||{parent:0,related:0,context:0,closed:0,total:0};
    return `<a href="#canonical-group-${esc(group.id.toLowerCase())}" data-category-total="${row.total}"><span>${esc(group.id)}</span><div><b>${textOf(group.title)}</b><small>${language==="zh"?`合计 ${row.total} 个 · 父级方向 ${row.parent} · 研究方向/方法 ${row.related} · 论文/证据 ${row.context} · 编号关闭研究方向 ${row.closed}`:`${row.total} total · ${row.parent} parents · ${row.related} directions/methods · ${row.context} paper/evidence · ${row.closed} numbered stopped ideas`}</small></div></a>`;
  }).join("")}</nav></section>`;
}
function renderCanonicalRelatedBank(group,independent) {
  const methods=independent.filter(row=>(row.idea.group||supplementalGroupId(row.idea))===group.id);
  const pfIds=CANONICAL_PF_GROUPS[group.id]||[];
  const pfCards=pfIds.length&&window.renderPaperFirstIdeaCards?window.renderPaperFirstIdeaCards(pfIds):"";
  const methodCards=methods.map(renderSupplementalIdeaCard).join("");
  if(!methodCards&&!pfCards)return "";
  return `<details class="canonical-related-bank" open><summary><div><b>${language==="zh"?"关联研究方向与方法资产":"Related research directions and method assets"}</b><span>${language==="zh"?"归入本类的研究方向、独立方法和衍生资产统一使用本类字母编号；它们是关联对象，不重复计入 26 个父级研究方向。":"Related directions, standalone methods, and derived assets use their category letter; they are related objects and are not recounted among the 26 parents."}</span></div><strong>${methods.length+pfIds.length}</strong></summary><div class="canonical-related-body">${methodCards?`<section class="canonical-related-section"><h3 data-toc="false">${language==="zh"?"独立方法／衍生方法资产":"Standalone / derived method assets"}</h3><div class="supplemental-list">${methodCards}</div></section>`:""}${pfCards?`<section class="canonical-related-section"><h3 data-toc="false">${language==="zh"?"归入本类的研究方向与终态裁决":"Category-aligned directions and terminal decisions"}</h3><div class="paper-incubation-list">${pfCards}</div></section>`:""}</div></details>`;
}
function renderCanonicalIdeaGroup(group,parents,independent) {
  const rows=parents.filter(row=>row.meta.group===group.id).sort((a,b)=>String(a.meta.code).localeCompare(String(b.meta.code),undefined,{numeric:true}));
  const holdRows=rows.filter(row=>row.meta.status==="hold"), stopRows=rows.filter(row=>row.meta.status==="stop"), mergeRows=rows.filter(row=>row.meta.status==="merge");
  const renderParents=(items)=>items.map((row,index)=>`<div class="canonical-parent-item" data-canonical-status="${esc(row.meta.status)}" data-canonical-group="${esc(group.id)}">${renderHumanReviewedIdeaCard(row.idea,row.meta,index)}</div>`).join("");
  const holdCards=renderParents(holdRows), stopCards=renderParents(stopRows), mergeCards=renderParents(mergeRows);
  const context=window.renderCategorizedResearchContext?window.renderCategorizedResearchContext(group.id):"";
  const safety=group.id==="G"&&window.renderAgentSafetyProgram?window.renderAgentSafetyProgram():"";
  const related=renderCanonicalRelatedBank(group,independent);
  const closed=window.renderClosedCandidateIdeas?window.renderClosedCandidateIdeas(group.id):"";
  const counts={hold:holdRows.length,stop:stopRows.length,merge:mergeRows.length};
  const inventory=canonicalGroupInventory(group.id,parents,independent,window.closedCandidateCategoryCounts?window.closedCandidateCategoryCounts():{});
  const terminalLine=inventory.parent?(language==="zh"?`父级方向当前科学状态：暂缓 ${counts.hold||0} · 停止 ${counts.stop||0} · 合并 ${counts.merge||0}`:`Current parent scientific states: hold ${counts.hold||0} · stopped ${counts.stop||0} · merged ${counts.merge||0}`):(group.id==="G"?(language==="zh"?"G-1 支持层暂缓（可条件重开）· G-2—G-5 已关闭":"G-1 support HOLD (conditionally reopenable) · G-2—G-5 closed"):"");
  const insight=CATEGORY_BRIEFING_ZH[group.id]||{};
  const categoryBriefing=language==="zh"?`<div class="canonical-category-briefing"><section><b>这类在研究什么</b><p>${esc(insight.focus||textOf(group.question))}</p></section><section><b>这一类目前的总体结论</b><p>${esc(insight.reason||"以每个编号卡片的当前终态为准。")}</p></section><section><b>留下了什么</b><p>${esc(insight.survives||"保留有效组件、审计规则与负证据。")}</p></section></div>`:`<div class="canonical-category-briefing"><section><b>Research focus</b><p>${textOf(group.question)}</p></section><section><b>Current category conclusion</b><p>See each ResearchItem's current scientific decision and decisive evidence.</p></section><section><b>What survives</b><p>Useful components, audit rules, and negative evidence remain preserved.</p></section></div>`;
  const currentBody=`${holdCards?`<div class="canonical-parent-list">${holdCards}</div>`:""}${context}${safety}` || `<div class="research-category-empty">${language==="zh"?"当前没有正在推进或等待决定性证据的 ResearchItem；如有新证据，按各卡片重开条件重新进入。":"No ResearchItem is currently advancing or awaiting decisive evidence; new evidence must satisfy the item-specific reopen condition."}</div>`;
  const concludedBody=`${stopCards?`<div class="canonical-parent-list">${stopCards}</div>`:""}${closed}` || `<div class="research-category-empty">${language==="zh"?"本类暂无已形成明确终态的 ResearchItem。":"No ResearchItem in this category has a clear terminal decision yet."}</div>`;
  const assetBody=`${mergeCards?`<div class="canonical-parent-list">${mergeCards}</div>`:""}${related}` || `<div class="research-category-empty">${language==="zh"?"本类暂无已合并或沉淀的方法资产。":"No merged or retained method asset in this category."}</div>`;
  const lane=(kind,titleZh,titleEn,noteZh,noteEn,body)=>`<section class="research-category-lane lane-${kind}"><header><div><span>${kind==="current"?"01":kind==="concluded"?"02":"03"}</span><div><h3 data-toc="false">${language==="zh"?titleZh:titleEn}</h3><p>${language==="zh"?noteZh:noteEn}</p></div></div></header><div class="research-category-lane-body">${body}</div></section>`;
  return `<section class="canonical-idea-group" id="canonical-group-${esc(group.id.toLowerCase())}" data-canonical-group="${esc(group.id)}" data-category-total="${inventory.total}"><header class="canonical-group-header"><span>${esc(group.id)}</span><div><h2>${textOf(group.title)}</h2><p>${textOf(group.question)}</p><div class="canonical-group-counts"><b>${inventory.total} ${language==="zh"?"个去重研究对象":"deduplicated objects"}</b><small>${language==="zh"?`父级方向 ${inventory.parent} · 研究方向/方法 ${inventory.related} · 论文/证据 ${inventory.context} · 编号关闭研究方向 ${inventory.closed}`:`${inventory.parent} parents · ${inventory.related} directions/methods · ${inventory.context} paper/evidence · ${inventory.closed} numbered stopped ideas`}</small>${terminalLine?`<small>${terminalLine}</small>`:""}</div></div></header>${categoryBriefing}${lane("current","当前值得关注","Current attention","仍在等待证据、存在条件重开，或已经进入论文阶段但需要保持研究链可见。","Items awaiting evidence, conditionally reopenable, or handed off into PaperState while retaining their research lineage.",currentBody)}${lane("concluded","已形成明确结论","Clear conclusions","这里放已经由实验、同信息简单基线或文献碰撞形成清楚科研结论的 ResearchItem。","ResearchItems with a clear scientific decision from experiments, same-information simplification, or literature collision.",concludedBody)}${lane("assets","已合并 / 沉淀为资产","Merged / retained assets","不再作为独立论文推进，但有价值的机制、协议、基线或审计规则继续保留。","No longer standalone papers; useful mechanisms, protocols, baselines, and audit rules remain reusable.",assetBody)}</section>`;
}
function renderLiveMementoPaperDesignCandidate(){
  const state=window.MEMENTO_JOINT_IDENTIFIABILITY_PAPER_DESIGN||{};
  if(!state.candidate_id)return "";
  const f0=state.f0_contract||{}, runtime=state.runtime_support||{}, audit=state.paper_design_audit||{}, quality=audit.paper_quality||{}, plain=state.plain_language||{}, source=state.source_integrity||{}, auth=state.authority||{};
  const zh=language==="zh";
  const title=zh?(state.title?.zh||state.title?.en):(state.title?.en||state.title?.zh);
  const status=zh?"论文设计已冻结 · 等待 exact MEMENTO 运行环境":"Paper Design frozen · exact MEMENTO runtime pending";
  const paperabilityLabel=String(state.paperability||"MEDIUM").split("_")[0];
  const scene=zh?plain.scene_zh:"MEMENTO combines two previously separate personalized tasks into one joint task. The published joint-memory drop therefore changes both memory coordination and task composition. This audit keeps the exact same scene and two subgoals, but spells out both personalized references explicitly so the agent needs no memory; any remaining loss measures composition difficulty itself.";
  const observed=zh?plain.observed_zh:"All 36/36 joint units admit a deterministic fully specified composed control, and the frozen 12-unit subset spans 12 scenes. The public no-memory joint condition still uses underspecified personalized instructions, and the audited release exposes no paired same-scene, same-composed-goal fully specified control. The new 36-episode F0 has not run yet, so there is no new composition-penalty number.";
  const judgment=zh?"这个候选已经通过 ProblemGate，新颖性只保留在 benchmark / empirical attribution：我们不声称新估计器，也不声称新记忆机制。真正能否成论文，只看新的 composition control 是否让原有 joint-memory 归因发生实质变化。":"The candidate passed ProblemGate only as a benchmark/empirical attribution audit. It claims neither a new estimator nor a new memory mechanism. Paperability now depends entirely on whether the missing composition control materially changes the published joint-memory attribution.";
  const human=zh?"当前不需要再发明方法。最需要解决的是 exact runtime 支持：恢复官方 Habitat/PARTNR/HSSD/MEMENTO 环境后，严格按冻结的 12 个 unit 跑 36 个 no-memory episode。":"No new method is needed. The remaining task is exact-runtime support: restore the official Habitat/PARTNR/HSSD/MEMENTO stack, then run exactly 36 no-memory episodes over the frozen 12 units.";
  const next=zh?`只允许先跑 Stage-1 F0。GO：${f0.go||"--"}；STOP：${f0.stop||"--"}；其余 HOLD。只有 GO 才打开完整 coordination audit。当前执行状态=${runtime.status||"--"}。`:`Stage-1 F0 only. GO: ${f0.go||"--"}; STOP: ${f0.stop||"--"}; otherwise HOLD. Only GO unlocks the full coordination audit. Current execution status=${runtime.status||"--"}.`;
  const simple=zh?plain.simple_baseline_zh:"The simplest explanation says that doing two goals together is naturally harder. It uses goal/object counts, scene metadata, and released scores to predict a joint-task penalty, but it cannot tell how large that penalty actually is in MEMENTO. The new control changes only one thing: keep the joint task fixed and make the two personalized facts explicit, removing memory coordination from the task.";
  const design=zh?"对每个 frozen joint unit，先重跑两个 fully-specified parent acquisition，再把这两个 parent 的目标按原顺序合成一个 fully-specified joint instruction，并在同一 scene 执行。每个 unit 得到 C_u = PC_joint_explicit − mean(PC_parent_i, PC_parent_j)。":"For every frozen joint unit, rerun both fully specified acquisition parents, compose their goals in the original order into one fully specified joint instruction, and execute it in the same scene. Each unit yields C_u = PC_joint_explicit − mean(PC_parent_i, PC_parent_j).";
  const sourcePassed=source.passed===true;
  const qualityPassed=quality.passed===true;
  const zeroAuthority=Object.values(auth).every(value=>value===false);
  return `<section class="panel live-paper-design-candidate" id="live-memento-paper-design" data-candidate-id="${esc(state.candidate_id)}"><div class="idea-panel-heading"><div><div class="eyebrow">${zh?"NEW · PROBLEMGATE → PAPER DESIGN":"NEW · PROBLEMGATE → PAPER DESIGN"}</div><h2 data-toc="false">${esc(title)}</h2><p class="section-intro">${zh?"这是本轮文献/异常边界搜索留下的唯一新论文问题；它暂时不计入 A–G ResearchItem 总数，也没有进入 PaperState。":"This is the sole new paper problem surviving the current boundary/collision search. It is not yet counted as an A–G ResearchItem and has not entered PaperState."}</p></div><strong>${esc(paperabilityLabel)}<span>${zh?"结果依赖型":"result-dependent"}</span></strong></div><div class="live-paper-design-status"><span><b>${zh?"当前状态":"Current state"}</b>${esc(status)}</span><span><b>Paper Design</b>${audit.passed?"PASS":"REPAIR"}</span><span><b>Source integrity</b>${sourcePassed?"PASS":"HOLD"}</span><span><b>Execution</b>${esc(runtime.status||"--")}</span></div><section class="pf-briefing-summary one-minute-briefing"><header><b>${zh?"【1min结论】":"【1 min summary】"}</b><span>${zh?"先把任务组合成本单独测出来，再谈多记忆协调":"Measure composition cost before claiming memory coordination"}</span></header><div class="one-minute-briefing-grid"><section class="briefing-scene" data-briefing-part="scene"><b>${zh?"① 具体任务场景：到底在做什么？":"① Concrete task scene"}</b><p>${esc(scene)}</p></section><section data-briefing-part="progress"><b>${zh?"② 生命周期 + 我们实际做到哪":"② Lifecycle + actual work"}</b><p>${esc(zh?`ProblemGate 已通过；36/36 control 可构造；12 个 scene-diverse unit 已冻结；Paper Design / Paper Quality 结构审计通过。新的 F0 还没运行，当前没有实验执行权限。`:`ProblemGate passed; 36/36 controls are constructible; 12 scene-diverse units are frozen; Paper Design / Paper Quality audits pass. The new F0 has not run and has no execution authority.`)}</p></section><section data-briefing-part="observed"><b>${zh?"③ 目前实际看到了什么":"③ What is actually observed"}</b><p>${esc(observed)}</p></section><section data-briefing-part="judgment"><b>${zh?"④ 所以现在能确定什么，还不能确定什么":"④ What is / is not established"}</b><p>${esc(judgment)}</p></section><section class="briefing-human" data-briefing-part="human"><b>${zh?"⑤ 当前最需要解决的问题":"⑤ Decision-critical remaining issue"}</b><p>${esc(human)}</p></section><section class="briefing-next" data-briefing-part="next"><b>${zh?"⑥ Research OS 唯一下一步":"⑥ Canonical next step"}</b><p>${esc(next)}</p></section></div></section><section class="live-memento-comparison"><header><div><b>${zh?"具体对照：新控制 vs 最简单解释":"Concrete comparison: new control vs simplest explanation"}</b><span>${zh?"这不是新 estimator，而是补齐缺失的对照条件":"A missing control, not a new estimator"}</span></div></header><div class="comparison-designs"><article><small>${zh?"我们的控制怎么做":"Our control"}</small><p>${esc(design)}</p></article><article class="comparison-simple"><small>${zh?"简单方法怎么做":"Simple baseline"}</small><p>${esc(simple)}</p></article></div><div class="simple-method-guide"><b>${zh?"简单方法具体怎么做到":"How the simple baseline works"}</b><div><span><small>${zh?"输入看什么":"Inputs"}</small><em>${esc(zh?"每个任务的 goal 数、object 数、scene、已有 acquisition/single/joint 分数。":"Goal count, object count, scene metadata, and released acquisition/single/joint scores.")}</em></span><span><small>${zh?"具体怎么跑":"Rule"}</small><em>${esc(zh?"把 joint 当成普通多目标任务：根据目标/对象数量增加预测一个固定或分层的复杂度 penalty，不新增任何环境 rollout。":"Treat joint as an ordinary multi-goal task and predict a fixed or stratified complexity penalty from goal/object counts, with no new rollout.")}</em></span><span><small>${zh?"最后输出什么":"Output"}</small><em>${esc(zh?"‘joint 应该比两个 single 更难多少’的元数据预测。":"A metadata-only prediction of how much harder joint should be than its parents.")}</em></span><span><small>${zh?"相比新控制少了什么":"What it omits"}</small><em>${esc(zh?"它没有真正执行 same-scene + same-composed-goal + fully-specified task，因此无法测出 MEMENTO 特定的 composition penalty。":"It never executes the same-scene, same-composed-goal fully specified task, so it cannot measure MEMENTO's actual composition penalty.")}</em></span></div></div><div class="comparison-matched"><b>${zh?"怎么保证比较公平":"What stays matched"}</b><p>${esc(zh?"scene、两个子目标、target objects、goal 顺序、planner/runtime 和 PC 指标全部固定；只把 personalized reference 从隐式记忆依赖改成显式文本。":"Scene, two subgoals, target objects, goal order, planner/runtime, and PC metric stay fixed; only personalized references change from memory-dependent to explicit text.")}</p></div><div class="comparison-verdict"><b>${zh?"什么时候这个新问题值得继续":"When the paper problem survives F0"}</b><p>${esc(zh?plain.decision_zh:`GO only if the upper 95% bootstrap bound of mean C_u is at or below -0.05 PC; STOP if the lower bound is at or above -0.05; otherwise HOLD.`)}</p></div></section><div class="live-f0-contract"><article><b>${f0.units||0} × ${f0.arms_per_unit||0}</b><span>${zh?"12 unit × 3 arms":"12 units × 3 arms"}</span></article><article><b>${f0.episodes||0}</b><span>${zh?"Stage-1 no-memory episodes":"Stage-1 no-memory episodes"}</span></article><article><b>${esc(String(f0.decision_margin??"--"))} PC</b><span>${zh?"冻结 headroom margin":"frozen headroom margin"}</span></article><article><b>${qualityPassed?"PASS":"HOLD"}</b><span>${zh?"Paper Quality v2.1":"Paper Quality v2.1"}</span></article></div><details class="human-technical-details live-paper-design-audit"><summary>${zh?"查看冻结合同、运行阻断与权限":"Inspect frozen contract, runtime blocker, and authority"}</summary><div class="human-evidence-grid"><section><h4 data-toc="false">Contract SHA</h4><p><code>${esc(state.contract_sha256||"--")}</code></p></section><section><h4 data-toc="false">${zh?"冻结 unit":"Frozen units"}</h4><p>${esc((f0.frozen_joint_episode_ids||[]).join(", "))}</p></section><section><h4 data-toc="false">GO / STOP</h4><p>${esc(f0.go||"--")}<br>${esc(f0.stop||"--")}</p></section><section><h4 data-toc="false">${zh?"exact runtime 阻断":"Exact-runtime blocker"}</h4><p>${esc(zh?runtime.interpretation:(runtime.interpretation||""))}</p></section><section><h4 data-toc="false">${zh?"设计审计":"Design audit"}</h4><p>Paper Design=${audit.passed?"PASS":"HOLD"} · Paper Quality=${qualityPassed?"PASS":"HOLD"} · Source integrity=${sourcePassed?"PASS":"HOLD"}</p></section><section><h4 data-toc="false">${zh?"科学/执行权限":"Scientific / execution authority"}</h4><p>${zeroAuthority?(zh?"全部为 0：设计冻结不等于实验授权。":"All zero: a frozen design is not experiment authority."):(zh?"存在非零权限，请检查 ledger。":"Non-zero authority detected; inspect ledger.")}</p></section></div></details></section>`;
}
function renderCanonicalIdeaLedger(groups=canonicalIdeaGroups(),parents=canonicalParentRows(),independent=canonicalIndependentRows(),inventory=canonicalInventorySummary(groups,parents,independent)) {
  const terminal=humanParentFinalSummary();
  const terminalSummary=`<div class="human-final-summary canonical-terminal-summary"><div><b>${terminal.hold||0}</b><span>${language==="zh"?"当前暂缓":"currently on hold"}</span></div><div><b>${terminal.stop||0}</b><span>${language==="zh"?"当前已停止":"currently stopped"}</span></div><div><b>${terminal.merge||0}</b><span>${language==="zh"?"当前已合并":"currently merged"}</span></div><div><b>0</b><span>${language==="zh"?"可启动正式实验":"launchable formal experiments"}</span></div><small>${language==="zh"?"这是 26 个父级 ResearchItem 的当前科学状态：4 个 HOLD、16 个 STOP、6 个 MERGED。历史 P0、P0-ready 与 DROP 只作为里程碑，不再覆盖当前科学结论。":"Current scientific state for the 26 parent ResearchItems: 4 HOLD, 16 STOPPED, and 6 MERGED. Historical P0, P0-ready, and DROP remain milestones only."}</small></div>`;
  const paperFirstSummary=window.renderPaperFirstIdeaIncubation?window.renderPaperFirstIdeaIncubation().split('<div class="paper-incubation-list">')[0]:"";
  const appendix=`<section class="panel canonical-audit-appendix"><h2 id="canonical-audit-appendix">${language==="zh"?"审计说明：怎样理解阶段、停止与重开":"Audit guide: how to read stage, stop, and reopen"}</h2><div class="canonical-audit-grid"><section><b>${language==="zh"?"阶段不等于权限":"Stage is not authority"}</b><p>${language==="zh"?"历史上进入 P0，只说明当时形成过可证伪合同；当前是否能运行，仍以正式实验权限为准。":"Historical P0 means a falsifiable contract once existed; current execution still requires formal authority."}</p></section><section><b>${language==="zh"?"失败必须分层":"Failures stay typed"}</b><p>${language==="zh"?"执行、协议、证据支持、方法实现和核心原理不会互相替代；只有核心原理级裁决才是科学死路。":"Execution, protocol, support, method-realization, and core-principle failures do not substitute for one another; only a core-principle ruling is a scientific dead end."}</p></section><section><b>${language==="zh"?"重开需要新证据":"Reopen requires new evidence"}</b><p>${language==="zh"?"换名字、换术语或重复同一实验不足以重开；必须满足卡片中写明的新增证据条件。":"Renaming or repeating the same test is insufficient; the card-specific new-evidence condition must be met."}</p></section></div>${paperFirstSummary}${renderHumanReviewMethodology()}</section>`;
  return `${renderResearchBriefingGuide(inventory)}${renderLiveMementoPaperDesignCandidate()}${renderCanonicalCategoryIndex(groups,parents,independent,inventory)}${terminalSummary}${canonicalStatusControls(parents)}${groups.map(group=>renderCanonicalIdeaGroup(group,parents,independent)).join("")}${appendix}`;
}
function initCanonicalIdeaFilters(){
  const buttons=[...document.querySelectorAll(".canonical-filter-btn")];
  if(!buttons.length)return;
  buttons.forEach(button=>button.addEventListener("click",()=>{
    const status=button.dataset.canonicalStatus||"all";
    buttons.forEach(item=>{const active=item===button;item.classList.toggle("active",active);item.setAttribute("aria-pressed",active?"true":"false");});
    document.querySelectorAll(".canonical-parent-item").forEach(item=>{item.hidden=status!=="all"&&item.dataset.canonicalStatus!==status;});
  }));
}
function initIdeaBriefingMode(){
  const buttons=[...document.querySelectorAll(".briefing-mode-btn")];
  if(!buttons.length)return;
  const setMode=(mode)=>{
    document.documentElement.classList.toggle("idea-audit-mode",mode==="audit");
    buttons.forEach(button=>{const active=button.dataset.briefingMode===mode;button.classList.toggle("active",active);button.setAttribute("aria-pressed",active?"true":"false");});
    const cardSelector=".human-review-idea-card,.supplemental-idea-card,.paper-incubation-card,.closed-idea-card";
    document.querySelectorAll(cardSelector).forEach(card=>{card.open=mode==="audit";});
    document.querySelectorAll(".human-technical-details,.terminal-technical-audit,.human-lineage-details,.human-complete-intro").forEach(detail=>{detail.open=mode==="audit";});
  };
  buttons.forEach(button=>button.addEventListener("click",()=>setMode(button.dataset.briefingMode||"brief")));
  setMode("brief");
}
function renderIdeaPortfolio(config) {
  const groups=canonicalIdeaGroups(), parents=canonicalParentRows(), independent=canonicalIndependentRows();
  const inventory=canonicalInventorySummary(groups,parents,independent);
  const current=window.renderCurrentResearchPortfolio?window.renderCurrentResearchPortfolio({includeClosed:false,ideasPage:true,inventory}):"";
  return `${pageHeader(config)}${current}${renderCanonicalIdeaLedger(groups,parents,independent,inventory)}`;
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
  const stageCards = data.stages.map((stage) => `<article class="history-stage" style="--stage:${esc(stage.color)}"><div class="history-stage-head"><span>${esc(stage.code)}</span><strong>${esc(stage.period)}</strong></div><h3 data-toc="false">${textOf(stage.title)}</h3><p class="history-stage-subtitle">${textOf(stage.subtitle)}</p><ul>${stage.bullets[language].map((item) => `<li>${esc(item)}</li>`).join("")}</ul><div class="history-stage-meta"><b>${language === "zh" ? "更新对象" : "Update target"}</b><span>${textOf(stage.target)}</span><b>${language === "zh" ? "反馈" : "Feedback"}</b><span>${textOf(stage.feedback)}</span></div><div class="history-stage-limit">${textOf(stage.limitation)}</div></article>`).join("");
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
  return `<figure class="history-overview-figure"><header><div class="eyebrow">${language === "zh" ? "历史总览 · 已发表论文优先" : "Historical overview · published work prioritized"}</div><h2 data-toc="false">${language === "zh" ? "Agent 自进化研究的历史、能力与方向演化" : "History, capability growth, and direction formation in agent self-evolution"}</h2><p>${language === "zh" ? "从基础模型、推理与自举，到经验记忆、技能工具、工作流搜索、多模态进化与安全治理。" : "From foundation models and self-bootstrapped reasoning to persistent memory, skills, workflow search, multimodal evolution, and governance."}</p></header><section class="history-panel history-timeline"><div class="history-panel-title">${language === "zh" ? "A · 六阶段历史时间线" : "A · Six-stage historical timeline"}</div><div class="history-stage-grid">${stageCards}</div></section><section class="history-panel history-expansion"><div class="history-panel-title">${language === "zh" ? "B · 更新对象如何扩展" : "B · How the update target expanded"}</div><div class="history-expansion-grid">${expansion}</div></section><div class="history-middle-grid"><section class="history-panel history-capabilities"><div class="history-panel-title">${language === "zh" ? "C · 能力层级随时间如何增长" : "C · Capability growth across historical stages"}</div><div class="history-table-scroll"><table><thead><tr><th>${language === "zh" ? "能力层" : "Capability"}</th>${capabilityHead}</tr></thead><tbody>${capabilityRows}</tbody></table></div></section><section class="history-panel history-directions"><div class="history-panel-title">${language === "zh" ? "D · 十个研究方向如何形成" : "D · Formation of the ten research directions"}</div><div class="history-table-scroll"><table><thead><tr><th>ID</th><th>${language === "zh" ? "方向" : "Direction"}</th><th>${language === "zh" ? "起源" : "Origin"}</th><th>${language === "zh" ? "增长" : "Growth"}</th><th>${language === "zh" ? "状态" : "Status"}</th></tr></thead><tbody>${directionRows}</tbody></table></div><div class="history-ladder"><h3 data-toc="false">${language === "zh" ? "历史结论阶梯" : "Historical claim ladder"}</h3>${ladder}</div></section></div><div class="history-bottom-grid"><section class="history-panel history-milestones"><div class="history-panel-title">${language === "zh" ? "E · 正式发表里程碑" : "E · Peer-reviewed milestones"}</div><div class="history-milestone-grid">${milestones}</div></section><section class="history-panel history-shifts"><div class="history-panel-title">${language === "zh" ? "F · 七次关键范式迁移" : "F · Seven paradigm shifts"}</div>${shifts}</section><section class="history-panel history-enablers"><div class="history-panel-title">${language === "zh" ? "G · 六个关键驱动因素" : "G · Six enabling factors"}</div>${enablers}</section><section class="history-panel history-challenges"><div class="history-panel-title">${language === "zh" ? "H · 当前开放问题" : "H · Open problems"}</div>${challenges}</section></div><figcaption>${language === "zh" ? "主时间线和里程碑优先采用正式发表论文；预印本前沿只在正文文献库中补充，不与历史主线混列。" : "The main timeline and milestone panel prioritize formally published papers. Preprint-only frontier work remains in the bibliography rather than being mixed into the historical spine."}</figcaption></figure>`;
}
function dashboardPaperStageLabel(stage="") {
  if(language!=="zh") return String(stage||"--").replaceAll("_"," ");
  return ({PAPER_EVIDENCE:"论文证据",PAPER_DESIGN:"论文设计",MANUSCRIPT:"成稿",MOCK_PC:"模拟审稿",TARGETED_REPAIR:"定向修稿",CLAIM_AUDIT:"主张审计",PDF_QA:"PDF 检查",PREBUTTAL:"预答辩",SUBMISSION_READY:"可投稿",SUBMITTED:"已投稿",REBUTTAL:"答辩",LEARN:"复盘"})[stage] || stage || "--";
}
function dashboardStateLabel(state="") {
  if(language!=="zh") return ({PAPER_READY:"PAPER READY",HOLD:"HOLD"})[state] || state || "--";
  return ({PAPER_READY:"已进入论文",HOLD:"等待明确条件"})[state] || state || "--";
}
function renderHomeHero(config, stats) {
  const steps = language === "zh"
    ? [["01","经验","任务结果、反馈或新证据"],["02","持久更新","记忆、技能、Prompt、工作流或参数发生可复用变化"],["03","未来复用","当前任务结束后，新状态仍会影响后续任务"],["04","纵向验证","检查收益、回退、安全与适用边界"]]
    : [["01","Experience","Task outcomes, feedback, or new evidence"],["02","Persistent update","Reusable changes to memory, skills, prompts, workflows, or weights"],["03","Future reuse","The changed state still affects later tasks"],["04","Longitudinal test","Measure gains, regressions, safety, and scope"]];
  const actions = language === "zh"
    ? [["foundations.html","先理解定义"],["research-map.html","看当前科研"],["selected-paper.html","看论文"],["bibliography.html","查文献"]]
    : [["foundations.html","Start with the definition"],["research-map.html","Current research"],["selected-paper.html","Papers"],["bibliography.html","Literature"]];
  return `<section class="home-hero"><div class="home-hero-main"><div class="home-hero-copy"><div class="eyebrow">${esc(textOf(config.eyebrow))}</div><h1>${textOf(config.title)}</h1><p class="lead">${textOf(config.lead)}</p><nav class="home-hero-actions">${actions.map(([href,label],index)=>`<a class="${index===0?"primary":""}" href="${href}">${label}<span>→</span></a>`).join("")}</nav></div><aside class="home-rule-card"><div class="home-rule-head"><span>${language==="zh"?"核心判据":"CORE TEST"}</span><b>${language==="zh"?"重试 ≠ 自进化":"Retrying ≠ self-evolution"}</b></div><p>${esc(textOf(config.callout||{}))}</p><div class="home-rule-flow">${steps.map(([n,title,desc])=>`<div><span>${n}</span><section><b>${title}</b><small>${desc}</small></section></div>`).join("")}</div></aside></div><div class="grid home-hero-stats">${stats.map(([value,label])=>`<div class="stat"><b>${value}</b><span>${label}</span></div>`).join("")}</div></section>`;
}
function renderHomeResearchConsole() {
  const d=researchDashboard(), s=d.summary||{}, attention=d.attention||[], week=d.week||{};
  if(!attention.length) return "";
  const primary=attention.find(row=>row.scientific_state==="PAPER_READY")||attention[0];
  const holds=attention.filter(row=>row.scientific_state==="HOLD");
  const brief=row=>language==="zh"?(row.briefing_zh||row.current_reason_zh||""):(row.briefing_en||row.current_reason_zh||"");
  const next=row=>language==="zh"?(row.next_step_zh||row.reopen_condition_zh||""):(row.next_step_en||row.reopen_condition_zh||"");
  const nextClass=row=>String(row.next_action_class||(row.primary_next_action||{}).action_class||"--");
  const title=row=>textOf(row.title||{})||row.code||"--";
  const primaryPaper=primary.paper_id?`${primary.paper_id} · ${dashboardPaperStageLabel(primary.paper_stage)}`:dashboardStateLabel(primary.scientific_state);
  const holdCards=holds.map(row=>`<article class="home-attention-row" data-dashboard-research="${esc(row.code)}"><header><span>${esc(row.code)}</span><b>${esc(title(row))}</b><em>${esc(dashboardStateLabel(row.scientific_state))}</em></header><small><b>${language==="zh"?"重开条件":"Reopen condition"} · ${esc(nextClass(row))}</b>${esc(next(row))}</small><footer><a href="${esc(row.portfolio_href||"paper-ideas.html")}">ResearchItem</a><a href="${esc(row.timeline_href||"research-timeline.html")}">${language==="zh"?"时间线":"Timeline"}</a>${row.paper_href?`<a href="${esc(row.paper_href)}">PaperState</a>`:""}</footer></article>`).join("");
  const highlights=(week.highlights||[]).slice(0,4).map(row=>`<a class="home-week-highlight" href="${esc(row.href||"research-timeline.html")}"><span>${esc(row.date||"")}</span><b>${esc(language==="zh"?(row.title_zh||row.title_en||""):(row.title_en||row.title_zh||""))}</b><small>${esc((row.research_items||[]).join(" · ") || (row.papers||[]).join(" · ") || row.event_class || "")}</small></a>`).join("");
  const weekRange=week.start_date&&week.end_date?`${week.start_date} → ${week.end_date}`:(d.as_of_date||"");
  const handoffCount=Number(s.research_handoffs??attention.filter(row=>nextClass(row)==="PAPERSTATE_HANDOFF").length);
  const waitingCount=Number(s.research_waiting_reopen??holds.length);
  const machineActionable=Number(s.machine_actionable_attention??0);
  const controlHeadline=language==="zh"?`当前跟踪 ${s.current_attention||attention.length} 个 ResearchItem：${handoffCount} 个已交接 PaperState，${waitingCount} 个等待重开条件`:`Tracking ${s.current_attention||attention.length} ResearchItems: ${handoffCount} PaperState handoff and ${waitingCount} waiting on reopen conditions`;
  return `<section class="home-research-console" id="current-research-console"><header class="home-console-head"><div><div class="eyebrow">${language==="zh"?"当前研究进展":"CURRENT RESEARCH"} · ${esc(d.as_of_date||"")}</div><h2 id="home-current-research">${controlHeadline}</h2><p>${language==="zh"?`这里展示控制面仍需跟踪的对象，不等于“现在都要继续做”。PaperState handoff 只保持谱系可见；HOLD 只等待自己的重开条件；当前 machine-actionable ResearchItem=${machineActionable}。`:`These are objects the control plane still tracks, not items that all require new work. A PaperState handoff keeps lineage visible; HOLD waits on its own reopen condition; machine-actionable ResearchItems=${machineActionable}.`}</p></div><nav><a href="research-map.html">${language==="zh"?"当前全景":"Current map"}</a><a href="paper-ideas.html">ResearchItems</a><a href="selected-paper.html">PaperRegistry</a></nav></header><div class="home-console-kpis"><span><b>${s.current_attention||attention.length}</b>${language==="zh"?"跟踪对象":"tracked"}</span><span><b>${handoffCount}</b>PaperState handoff</span><span><b>${waitingCount}</b>${language==="zh"?"等待重开":"waiting reopen"}</span><span><b>${machineActionable}</b>machine-actionable</span></div><div class="home-console-grid"><section class="home-console-current"><div class="home-console-section-title"><div><b>${language==="zh"?"当前论文交接":"Current paper handoff"}</b><span>${language==="zh"?"被跟踪不代表还有内部科研动作":"tracked does not imply unfinished internal research"}</span></div><strong>${esc(primaryPaper)}</strong></div><article class="home-primary-paper" data-dashboard-research="${esc(primary.code)}"><header><span>${esc(primary.code)} → ${esc(primary.paper_id||"PaperState")}</span><em>${esc(dashboardPaperStageLabel(primary.paper_stage))}</em></header><h3 data-toc="false">${esc(title(primary))}</h3><p>${esc(brief(primary))}</p><div><b>${language==="zh"?"下一步":"Next"} · ${esc(nextClass(primary))}</b><span>${esc(next(primary))}</span></div><footer><a class="link-btn" href="${esc(primary.paper_href||"selected-paper.html")}">PaperState →</a><a class="link-btn" href="${esc(primary.timeline_href||"research-timeline.html")}">${language==="zh"?"时间线 →":"Timeline →"}</a></footer></article><div class="home-console-section-title home-hold-title"><div><b>${language==="zh"?"等待条件的研究线":"Lines waiting on explicit conditions"}</b><span>${language==="zh"?"这里只保留重开条件；完整原因和证据回到 ResearchItem":"only reopen conditions are summarized here"}</span></div><strong>${holds.length} HOLD</strong></div><div class="home-attention-list">${holdCards}</div></section><aside class="home-console-week"><header><div><b>${language==="zh"?"最近一周":"This week"}</b><span>${esc(weekRange)}</span></div><a href="${esc(week.timeline_href||"research-timeline.html")}">${language==="zh"?"完整时间线 →":"Full timeline →"}</a></header><div class="home-week-kpis"><span><b>${week.research_days||0}</b>${language==="zh"?"研究日":"days"}</span><span><b>${week.substantive_events||0}</b>${language==="zh"?"科研事件":"events"}</span><span><b>${week.key_changes||0}</b>${language==="zh"?"关键变化":"key changes"}</span></div><div class="home-week-highlights">${highlights||`<div class="empty">${language==="zh"?"暂无周级摘要":"No weekly summary yet"}</div>`}</div><div class="home-week-note"><b>${language==="zh"?"这里只回答“哪里变了”":"This only answers what changed"}</b><p>${language==="zh"?"具体结果、失败类型和科研权限仍以对应 ResearchItem / PaperState 为准。":"Exact results, failure types, and authority remain in the linked ResearchItem or PaperState."}</p></div></aside></div></section>`;
}
function renderHomePortal(chapters, featuredByHref) {
  const cleanTitle=(chapter)=>textOf(chapter.title).replace(language==="zh"?/^(第一章|第二章|第三章)\s*·\s*/:/^(I|II|III)\s*·\s*/,"");
  const groupCards=(chapter)=>(chapter.links||[]).map(href=>featuredByHref.get(href)).filter(Boolean).map(item=>`<a class="framework-card home-route-card ${item.paper?"paper-card":""}" href="${item.href}"><b>${textOf(item.title)}</b><span>${textOf(item.desc)}</span><i>→</i></a>`).join("");
  return `<section class="home-route-portal" id="home-route-portal"><header><div><div class="eyebrow">${language==="zh"?"按目的进入，不按页面名猜":"CHOOSE BY GOAL"}</div><h2 data-toc="false">${language==="zh"?"你现在想解决什么？":"What are you trying to do?"}</h2></div><p>${language==="zh"?"首页只负责分流。领域知识、当前科研、论文与文献各自进入对应页面，不在这里重复展开。":"The home page routes rather than duplicates. Field knowledge, current research, papers, and literature live on their dedicated pages."}</p></header>${chapters.map((chapter,index)=>`<section class="page-chapter" data-chapter="${esc(chapter.id)}"><div class="home-route-section"><div class="home-route-heading"><span>${String(index+1).padStart(2,"0")}</span><div><h2 id="chapter-${esc(chapter.id)}">${cleanTitle(chapter)}</h2><p>${textOf(chapter.question)}</p></div></div><div class="framework-grid home-route-grid">${groupCards(chapter)}</div></div></section>`).join("")}</section>`;
}
function renderHome(config) {
  const chapters = pageArchitecture("home").chapters || [];
  const featured = config.featured || [];
  const featuredByHref = new Map(featured.map((item) => [item.href,item]));
  const homeStatus = projectStatusState().headline || {}, homePaperSummary=canonicalPaperRegistry().summary||{}, homeDashboardSummary=researchDashboard().summary||{};
  const stats = [
    [catalog.length || DATA.length, language === "zh" ? "篇去重研究条目" : "deduplicated research records"],
    [portfolioDirections().length || 10, language === "zh" ? "个历史问题方向" : "historical problem directions"],
    [homePaperSummary.papers ?? homeDashboardSummary.papers ?? 0, language === "zh" ? "篇已进入 PaperRegistry" : "papers in PaperRegistry"],
    [homePaperSummary.gate_clean_submission_ready ?? homeDashboardSummary.submission_ready ?? homePaperSummary.submission_ready ?? 0, language === "zh" ? "篇最新门禁可投稿" : "latest gate-clean papers"],
  ];
  return `${renderHomeHero(config,stats)}${renderHomeResearchConsole()}${renderHomePortal(chapters,featuredByHref)}`;
}
function renderResourceIndexSection(mode, headingLevel = 2) {
  const isRepository = mode === "repositories";
  const rows = catalog.filter((p) => isRepository ? Boolean(p.repo) : /benchmark|arena|gym|environment|dataset|evaluation|testbed|sandbox/i.test(`${p.title} ${p.category} ${p.subcategory}`));
  const grouped = rows.reduce((acc, row) => { const key = isRepository ? (row.updateTarget || "other") : (row.category || "Unclassified"); acc[key] = (acc[key] || 0) + 1; return acc; }, {});
  const summary = Object.entries(grouped).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([key, count]) => `<div class="stat"><b>${count}</b><span>${esc(language === "zh" ? (isRepository ? localizedUpdateTarget(key) : localizedCategory(key)) : key)}</span></div>`).join("");
  const title = isRepository ? (language === "zh" ? "动态代码仓库索引" : "Live repository index") : (language === "zh" ? "动态基准与环境索引" : "Live benchmark and environment index");
  const intro = isRepository ? (language === "zh" ? "从合并文献语料中自动抽取带公开代码链接的条目。仓库可用不代表完整复现，需结合上方复现等级审查。" : "Automatically extracts records with public code links from the merged corpus. Repository availability does not imply full reproduction; use the reproduction-readiness criteria above.") : (language === "zh" ? "从合并语料中抽取基准、评测环境、数据集与测试平台相关条目。" : "Extracts benchmark, arena, gym, environment, dataset, and evaluation records from the merged corpus.");
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
  return `<section class="panel bibliography-map"><div class="paper-figure-heading"><div><h3 id="method-time-map">${language === "zh" ? "方法与发表时间地图" : "Method and publication-time map"}</h3><p class="section-intro">${language === "zh" ? "每个单元格表示该年份与更新对象下的去重论文数量；点击即可筛选文献库。早期年份主要是提示词、记忆、持续学习与 Agent 架构的前置工作。" : "Each cell counts deduplicated papers for one year and update surface. Click a cell to filter the bibliography. Early years mainly contain precursors in prompting, memory, continual learning, and agent architecture."}</p></div></div><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="timeline-row"><button class="timeline-label" data-filter="${esc(surface)}">${esc(localizedUpdateTarget(surface))}</button>${years.map((year) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell" data-filter="${esc(surface)}" data-year="${year}" title="${esc(localizedUpdateTarget(surface))} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderPublicationTypeMap() {
  const years = [...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a - b);
  const types = ["Published", "Preprint", "Repository", "Blog/Report", "Other"];
  const maxCount = Math.max(1, ...types.flatMap((type) => years.map((year) => catalog.filter((p) => publicationType(p) === type && p.year === year).length)));
  return `<section class="panel bibliography-map"><h3 id="publication-status-map">${language === "zh" ? "发表类型与时间地图" : "Publication type and time map"}</h3><p class="section-intro">${language === "zh" ? "区分正式发表、预印本、仓库和技术博客。自动识别仅用于导航，正式引用仍以论文页面核验为准。" : "Separates published papers, preprints, repositories, and technical reports. Automatic status is for navigation; formal citations still require source verification."}</p><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "发表类型" : "Publication type"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${types.map((type) => `<div class="timeline-row"><button class="timeline-label publication-label" data-publication="${esc(type)}">${esc(localizedPublicationType(type))}</button>${years.map((year) => { const count = catalog.filter((p) => publicationType(p) === type && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell publication-cell" data-publication="${esc(type)}" data-year="${year}" title="${esc(localizedPublicationType(type))} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderSignalMatrix() {
  const surfaces = [...new Set(catalog.map((p) => p.updateTarget || "other"))].sort();
  const signals = [...new Set(catalog.map(signalFamily))].sort();
  const maxCount = Math.max(1, ...surfaces.flatMap((surface) => signals.map((signal) => catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length)));
  return `<section class="panel bibliography-map"><h3 id="surface-signal-map">${language === "zh" ? "更新对象与反馈信号地图" : "Update-surface and feedback-signal map"}</h3><p class="section-intro">${language === "zh" ? "该矩阵把“更新什么”与“凭什么更新”分开；点击单元格可联合筛选。" : "This matrix separates what changes from the evidence that drives the change. Click a cell to apply both filters."}</p><div class="signal-map" style="--signal-count:${signals.length}"><div class="signal-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${signals.map((signal) => `<button class="signal-column" data-signal="${esc(signal)}">${esc(localizedSignal(signal))}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="signal-row"><button class="signal-label" data-filter="${esc(surface)}">${esc(localizedUpdateTarget(surface))}</button>${signals.map((signal) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="signal-cell" data-filter="${esc(surface)}" data-signal="${esc(signal)}" title="${esc(localizedUpdateTarget(surface))} × ${esc(localizedSignal(signal))}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
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
  const filters = categories.map((category) => `<button class="filter-btn ${activeFilter === category ? "active" : ""}" data-filter="${esc(category)}">${esc(category === "all" ? (language === "zh" ? "全部方法" : "All methods") : localizedUpdateTarget(category))}</button>`).join("");
  const yearOptions = years.map((year) => `<option value="${year}" ${String(activeYear) === String(year) ? "selected" : ""}>${year === "all" ? (language === "zh" ? "全部年份" : "All years") : year}</option>`).join("");
  const publicationOptions = publicationTypes.map((type) => `<option value="${type}" ${activePublicationType === type ? "selected" : ""}>${type === "all" ? (language === "zh" ? "全部发表类型" : "All publication types") : localizedPublicationType(type)}</option>`).join("");
  const signalOptions = signals.map((signal) => `<option value="${signal}" ${activeSignal === signal ? "selected" : ""}>${signal === "all" ? (language === "zh" ? "全部反馈信号" : "All feedback signals") : localizedSignal(signal)}</option>`).join("");
  const visionCount = catalog.filter((p) => p.vision).length;
  const publishedCount = catalog.filter((p) => publicationType(p) === "Published").length;
  const sourceCount = new Set(catalog.flatMap((p) => String(p.source || "").split("+")).filter(Boolean)).size;
  const coreEvolutionCount = catalog.filter((p) => readingRoleInfo(p).id === "core-evolution").length;
  const deepAnalysisCount = Object.keys(window.TOP_PAPER_ANALYSES || {}).length;
  const coverage = citationCoverage();
  const sortOptions = (CITATION_CONFIG.sortModes || []).map((mode) => `<option value="${esc(mode.id)}" ${bibliographySort === mode.id ? "selected" : ""}>${textOf(mode.title)}</option>`).join("");
  const roleLegend = (CITATION_CONFIG.readingRoles || []).map((role) => `<span><b>${Number(role.rank || 0) + 1}</b>${textOf(role.title)}</span>`).join("");
  const trustGuide = `<section class="panel bibliography-trust-guide"><div class="eyebrow">${language === "zh" ? "文献证据层级" : "EVIDENCE PROVENANCE"}</div><h3 data-toc="false">${language === "zh" ? "先看信息来自哪一层，再决定能不能直接用于科研判断" : "Know the evidence layer before using a field in a research claim"}</h3><p class="section-intro">${language === "zh" ? "书目信息、逐篇分析、自动长尾和导航分类分开处理。" : "Bibliographic facts, curated analysis, synchronized long tail, and navigation labels stay separate."}</p><div class="bibliography-trust-grid"><article><b>${language === "zh" ? "一手书目" : "Primary bibliography"}</b><span>${language === "zh" ? "标题 / 年份 / venue / 链接优先回正式来源。" : "Title / year / venue / link resolve to primary sources."}</span></article><article><b>${language === "zh" ? `人工梳理 · ${deepAnalysisCount}` : `Curated · ${deepAnalysisCount}`}</b><span>${language === "zh" ? "关键论文逐篇写方法；具体数字仍回原文。" : "Key methods are paper-specific; exact numbers still require the source."}</span></article><article><b>${language === "zh" ? "自动长尾" : "Synchronized long tail"}</b><span>${language === "zh" ? "用于扩覆盖和找近邻；摘要归纳不冒充原文事实。" : "Broadens recall and neighbors; derived summaries are not source facts."}</span></article><article><b>${language === "zh" ? "导航分类" : "Navigation taxonomy"}</b><span>${language === "zh" ? "分布密度只辅助导航，不等于研究价值。" : "Corpus density guides navigation, not research value."}</span></article></div></section>`;
  const mapGuide = `<section class="panel bibliography-map-guide"><div class="eyebrow">${language === "zh" ? "三张地图分别回答什么" : "WHAT EACH MAP ANSWERS"}</div><div class="bibliography-map-guide-grid"><article><b>${language === "zh" ? "更新对象 × 年份" : "Update surface × year"}</b><span>${language === "zh" ? "看研究热点何时从 Prompt / 参数扩展到 Memory、Skill、Workflow、World。" : "See when activity expanded from prompts/parameters toward memory, skills, workflows, and worlds."}</span></article><article><b>${language === "zh" ? "更新对象 × 反馈信号" : "Update surface × feedback"}</b><span>${language === "zh" ? "把“改什么”和“凭什么改”分开，看哪些机制组合已经拥挤、哪些仍稀疏。" : "Separate what changes from what drives the change to see dense and sparse mechanism combinations."}</span></article><article><b>${language === "zh" ? "发表类型 × 年份" : "Publication status × year"}</b><span>${language === "zh" ? "区分正式发表与预印本前沿，避免把最新但未正式发表的工作和历史主线混在一起。" : "Separate peer-reviewed history from the preprint frontier instead of mixing bibliographic status with scientific maturity."}</span></article></div><p class="bibliography-map-caveat">${language === "zh" ? "这些图只描述当前语料中的分布；点击单元格可以直接把条件带到第四章的文献筛选。" : "These maps describe the current corpus only. Clicking a cell carries the condition into the searchable corpus in Chapter IV."}</p></section>`;
  const readingPaths = `<section class="panel bibliography-reading-paths"><div class="eyebrow">${language === "zh" ? "按目的选阅读入口" : "CHOOSE A READING PATH BY GOAL"}</div><div class="bibliography-reading-path-grid"><article><span>01</span><div><b>${language === "zh" ? "第一次理解领域" : "Understand the field"}</b><p>${language === "zh" ? "先读必读锚点 → 再用少量综述补全地图 → 进入直接方法与安全评测。" : "Must-read anchors → a few overviews for the map → direct methods and safety/evaluation."}</p></div></article><article><span>02</span><div><b>${language === "zh" ? "为 Idea 找最近工作" : "Find nearest work"}</b><p>${language === "zh" ? "按更新对象 + 反馈缩小范围，再回原文核碰撞。" : "Filter by update surface + feedback, then verify the collision in source."}</p></div></article><article><span>03</span><div><b>${language === "zh" ? "追历史根源" : "Trace foundations"}</b><p>${language === "zh" ? "按时间读 Agent / 模型前置，不和直接自进化混算。" : "Read agent/model precursors chronologically, separate from direct evolution."}</p></div></article></div></section>`;
  const rankingGuide = `<section class="panel citation-ranking-guide"><h3 id="literature-ranking">${language === "zh" ? "推荐阅读顺序与排序" : "Reading order and sorting"}</h3><p class="section-intro">${language === "zh" ? "默认先放少量必读锚点：综合高引用、直接相关性和已核验的重要作者／团队；随后才是领域综述、直接自进化、评测治理和支撑机制。作者声望只用于人工核验锚点，不会给缺作者信息的长尾论文瞎打分。" : "The default starts with a small must-read anchor set selected from citation impact, direct relevance, and verified field-defining authors/teams; field overviews and the remaining literature follow. Author reputation is used only for manually verified anchors, never guessed for long-tail records."}</p><div class="citation-ranking-controls"><label><span>${language === "zh" ? "排序方式" : "Sort mode"}</span><select id="bibliography-sort">${sortOptions}</select></label><div id="citation-ranking-status" class="citation-ranking-status"><strong>OpenAlex + Semantic Scholar</strong><span>${language === "zh" ? `引用覆盖 ${coverage.matched}/${coverage.total}` : `${coverage.matched}/${coverage.total} citation matches`}</span></div></div><div class="reading-role-legend">${roleLegend}</div><div class="ranking-secondary-note">${language === "zh" ? "必读层是阅读推荐，不是科学权威；其余层内仍优先正式发表、较新工作与可核验引用影响。" : "Must-read is a reading recommendation, not scientific authority; other layers still prioritize peer-reviewed status, recency, and verifiable citation impact."}</div></section>`;
  const analysisGuide = `<section class="panel paper-analysis-guide"><h3 id="paper-reading-schema">${language === "zh" ? "每篇论文：判断 + 实现" : "Every paper: judgment + implementation"}</h3><p class="section-intro">${language === "zh" ? "展开卡片即可同时看六项判断，以及组件、输入、更新闭环、持久产物和接受规则。" : "Expand a card for six judgments plus components, inputs, update loop, persistent artifact, and acceptance rule."}</p><div class="property-grid"><div class="property-card"><b>${language === "zh" ? "人工核验" : "Curated"}</b><span>${language === "zh" ? "关键论文保留逐篇方法。" : "Key papers keep paper-specific methods."}</span></div><div class="property-card"><b>${language === "zh" ? "摘要拆解" : "Summary-grounded"}</b><span>${language === "zh" ? "从摘要识别真实模块与数据流。" : "Infer concrete modules and flow from summaries."}</span></div><div class="property-card"><b>${language === "zh" ? "保守长尾" : "Conservative long tail"}</b><span>${language === "zh" ? "信息不足就不补不存在的细节。" : "Thin evidence never invents missing details."}</span></div><div class="property-card"><b>${language === "zh" ? "结构化导出" : "Structured export"}</b><span>${language === "zh" ? "分析与实现字段一起导出。" : "Analysis and implementation export together."}</span></div></div></section>`;
  const chapters = pageArchitecture("bibliography").chapters || [];
  const refreshMeta = window.LITERATURE_REFRESH_META || {};
  const openAlexDelta = refreshMeta.openalex_arxiv || {};
  const s2Delta = refreshMeta.semantic_scholar_arxiv || {};
  const refreshLog = refreshMeta.verified_at ? `<section class="panel bibliography-refresh-log"><div><div class="eyebrow">${language === "zh" ? "最近增量核验" : "LATEST VERIFIED DELTA"} · ${esc(refreshMeta.verified_at)}</div><h3 data-toc="false">${language === "zh" ? `+${(Number(openAlexDelta.added)||0)+(Number(s2Delta.added)||0)} 篇 · ${Number(s2Delta.updated)||0} 个版本更新` : `+${(Number(openAlexDelta.added)||0)+(Number(s2Delta.added)||0)} papers · ${Number(s2Delta.updated)||0} version update`}</h3><p>${language === "zh" ? "API 增量与 bulk snapshot 分开记录；Semantic Scholar key 不进入网页。" : "API deltas stay separate from the bulk snapshot; the Semantic Scholar key never enters web artifacts."}</p></div><div class="bibliography-refresh-methods"><article><b>OpenAlex + arXiv</b><strong>+${Number(openAlexDelta.added)||0}</strong><span>${language === "zh" ? "发现候选 + arXiv 元数据/摘要核验" : "candidate discovery + arXiv metadata/abstract verification"}</span></article><article><b>Semantic Scholar + arXiv</b><strong>+${Number(s2Delta.added)||0} / Δ${Number(s2Delta.updated)||0}</strong><span>${language === "zh" ? "认证 S2 检索 + arXiv 交叉核验" : "authenticated S2 retrieval + arXiv cross-check"}</span></article></div><div class="bibliography-refresh-chips">${(refreshMeta.key_deltas||[]).map(name=>`<span>${esc(name)}</span>`).join("")}</div></section>` : "";
  const statusAndStats = `<div class="integrity-status ${catalog.length > DATA.length ? "pass" : "warn"}"><strong>${catalog.length > DATA.length ? (language === "zh" ? "动态同步已合并" : "LIVE MERGED") : (language === "zh" ? "当前使用核验快照" : "VERIFIED SNAPSHOT")}</strong><span>${catalog.length > DATA.length ? (language === "zh" ? "页面已把两个综述维护目录、Semantic Scholar / ICLR 机制快照与人工视觉补充集合并并去重；动态同步扩大覆盖，但不会自动升级科学可信度。" : "The page merged two survey-maintained catalogs, the Semantic Scholar / ICLR mechanism snapshot, and the curated visual supplement. Live synchronization expands coverage but does not automatically increase scientific authority.") : (language === "zh" ? "上游动态目录当前未扩展本地核验集合；页面仍保留可复核的人工/生成快照，不把网络失败解释为文献不存在。" : "Upstream dynamic catalogs did not extend the verified local set in this load. The reviewable snapshot remains available; network failure is not interpreted as absence of literature.")}</span></div><div class="grid bibliography-stats"><div class="stat"><b>${catalog.length}</b><span>${language === "zh" ? "篇当前去重记录" : "current deduplicated records"}</span></div><div class="stat"><b>${publishedCount}</b><span>${language === "zh" ? "篇识别为正式发表" : "records classified as published"}</span></div><div class="stat"><b>${coreEvolutionCount}</b><span>${language === "zh" ? "篇归入直接自进化核心" : "direct self-evolution records"}</span></div><div class="stat"><b>${deepAnalysisCount}</b><span>${language === "zh" ? "篇人工深度梳理" : "manually curated deep analyses"}</span></div></div><div class="bibliography-meta-strip"><span><b>${sourceCount}</b>${language === "zh" ? "类来源流" : "source streams"}</span><span><b>${coverage.matched}/${coverage.total}</b>${language === "zh" ? "引用数据已匹配" : "citation records matched"}</span><span><b>${visionCount}</b>${language === "zh" ? "视觉 / 多模态相关" : "vision / multimodal records"}</span><span><b>${(CITATION_CONFIG.readingRoles || []).length}</b>${language === "zh" ? "个推荐阅读角色" : "reading-role layers"}</span></div>`;
  const publishedSpineBody = renderPublishedSpine();
  const publishedComparisonBody = renderPublishedComparisons();
  const ideaMiningBody = renderLiteratureIdeaMining();
  const mapsBody = `${mapGuide}${renderTimelineMap()}${renderSignalMatrix()}${renderPublicationTypeMap()}${renderMilestoneTimeline()}`;
  const corpusBody = `${rankingGuide}${analysisGuide}<section class="panel bibliography-corpus-panel"><div class="paper-figure-heading"><div><h3 id="searchable-corpus">${language === "zh" ? "找到你真正需要的论文，再缩小范围" : "Find the paper you need, then narrow the corpus"}</h3><p class="section-intro">${language === "zh" ? "顶部搜索框负责按论文名、方法和关键词定位；这里再用年份、发表类型、反馈信号、视觉范围和更新对象缩小集合。正式论文与预印本继续保留在同一个可检索库，但前两章只用正式发表论文建立主线。" : "Use the top search box to locate titles, methods, or keywords, then narrow by year, publication type, feedback signal, vision scope, and update surface. Published work and preprints remain searchable together, while Chapters I–II build the spine from published work only."}</p></div><div class="export-actions"><button class="link-btn export-btn" data-export="json">JSON</button><button class="link-btn export-btn" data-export="csv">CSV</button><button class="link-btn export-btn" data-export="bibtex">BibTeX</button><button class="link-btn" id="copy-filter-link">${language === "zh" ? "复制筛选链接" : "Copy filter link"}</button><button class="link-btn" id="print-page">${language === "zh" ? "打印" : "Print"}</button><button class="link-btn" id="reset-filters">${language === "zh" ? "重置" : "Reset"}</button></div></div><div class="bibliography-controls"><select id="year-filter">${yearOptions}</select><select id="publication-filter">${publicationOptions}</select><select id="signal-filter">${signalOptions}</select><label class="toggle-filter"><input id="vision-filter" type="checkbox" ${visionOnly ? "checked" : ""}> ${language === "zh" ? "仅视觉/多模态" : "Vision/multimodal only"}</label></div><div class="filters">${filters}</div><div id="bibliography-list" class="resource-list"></div></section>`;
  const coverageBody = `${trustGuide}${refreshLog}${statusAndStats}${renderSemanticScholarStatus()}${renderGroupNav(config.groupsBefore || [])}${renderMergedGroups(config.groupsBefore || [])}`;
  return `${pageHeader(config)}${renderArchitectureOverview(pageArchitecture("bibliography"))}${renderCustomChapter(chapters[0],0,publishedSpineBody)}${renderCustomChapter(chapters[1],1,publishedComparisonBody)}${renderCustomChapter(chapters[2],2,ideaMiningBody)}${renderCustomChapter(chapters[3],3,mapsBody)}${renderCustomChapter(chapters[4],4,corpusBody)}${renderCustomChapter(chapters[5],5,coverageBody)}`;
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
    const design = paperConcreteDesign(p, analysis);
    const anchor = mustReadAnchorInfo(p);
    const quick = publishedPaperReadout(p, analysis, design) || {};
    return {...p, priorityRank:index + 1, readingRole:readingRoleLabel(p), readingRoleRank:readingRoleRank(p), publicationTier:publicationTierLabel(p), citationCount:citationCount(p), citationSource:citationCountSource(p), citationMatchedTitle:citationMetadata(p)?.matchedTitle || "", citationMatchScore:citationMetadata(p)?.matchScore ?? "", mustReadRank:anchor?.rank || "", mustReadReason:anchor ? textOf(anchor.reason) : "", mustReadTeam:anchor?.team ? textOf(anchor.team) : "", analysisBasis:paperAnalysisLabel(analysis), problemMotivation:analysis.purpose, comparativeAdvantage:analysis.advantage, coreIntuition:analysis.core, rationale:analysis.rationale, methodFlow:analysis.logic, experimentalValidation:analysis.validation, designComponents:design.components, designInputs:design.inputs, designLoop:design.loop, designArtifact:design.artifact, designAcceptance:design.acceptance, publishedReadingTier:quick.tier||"", publishedDirection:quick.code||"", simplePriorMethod:quick.simple||"", whySimpleMethodInsufficient:quick.why||"", observedEvidence:quick.observed||"", supportedClaimBoundary:quick.proved||"", unprovenBoundary:quick.notProved||"", researchRelation:quick.relation||""};
  });
  if (format === "json") return downloadBlob("agent-self-evolution-bibliography.json", JSON.stringify(enriched, null, 2), "application/json;charset=utf-8");
  if (format === "bibtex") return downloadBlob("agent-self-evolution-bibliography.bib", rows.map(bibtexEntry).join("\n\n"));
  const fields = ["priorityRank","readingRole","readingRoleRank","publicationTier","citationCount","citationSource","citationMatchedTitle","citationMatchScore","mustReadRank","mustReadReason","mustReadTeam","year","title","venue","category","subcategory","updateTarget","signal","vision","analysisBasis","problemMotivation","comparativeAdvantage","coreIntuition","rationale","methodFlow","experimentalValidation","designComponents","designInputs","designLoop","designArtifact","designAcceptance","publishedReadingTier","publishedDirection","simplePriorMethod","whySimpleMethodInsufficient","observedEvidence","supportedClaimBoundary","unprovenBoundary","researchRelation","url","repo"];
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
  const text = `${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.updateTarget || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
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
  let raw = record.updateTarget || "agent component";
  const evidence = `${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.category || ""} ${record.subcategory || ""}`.toLowerCase();
  const generic = !raw || /^(agent component|component|other)$/i.test(String(raw).trim());
  if (generic) {
    if (/memory|retriev|experience bank|episodic|procedural/.test(evidence)) raw = "memory";
    else if (/tool|skill|api|function call/.test(evidence)) raw = "tool/skill";
    else if (/workflow|harness|scaffold|architecture|agent graph/.test(evidence)) raw = "workflow/scaffold";
    else if (/world model|dynamics|environment model/.test(evidence)) raw = "world model";
    else if (/evaluator|critic|grader|reward model|metric/.test(evidence)) raw = "evaluator/reward";
    else if (/prompt|instruction|context optimization/.test(evidence)) raw = "prompt/context";
    else if (/reinforcement learning|fine[- ]tun|lora|adapter|parameter update/.test(evidence)) raw = "model parameters";
  }
  if (language !== "zh") return raw;
  const key = String(raw).toLowerCase();
  if (/model parameter/.test(key)) return "模型参数";
  if (/prompt|context/.test(key)) return "提示词／上下文";
  if (/memory/.test(key)) return "记忆";
  if (/tool|skill/.test(key)) return "工具／技能";
  if (/workflow|scaffold|architecture/.test(key)) return "工作流／系统结构";
  if (/world|environment/.test(key)) return "世界模型／环境状态";
  if (/evaluator|reward/.test(key)) return "评价器／奖励";
  return raw === "agent component" ? "Agent 组件" : raw;
}
function paperSignalLabel(record) {
  const family = signalFamily(record);
  const declared = /semantic scholar retrieval/i.test(String(record.signal || "")) ? "" : (record.signal || "");
  if (language !== "zh") return declared || family;
  const labels = {
    "verification/tests":"可验证测试",
    "critique/evaluation":"批评与评价",
    "environment interaction":"环境交互",
    "scalar/preference reward":"标量或偏好奖励",
    "population/self-play":"群体反馈或自博弈",
    "experience reuse":"经验复用",
    "self-generated artifact":"自生成数据或轨迹",
  };
  return labels[family] || declared || family;
}
function paperMechanismKeys(record) {
  const text = `${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.category || ""} ${record.subcategory || ""} ${record.updateTarget || ""} ${record.signal || ""}`.toLowerCase();
  const rules = [
    ["attention",/transformer|multi[- ]head attention|self[- ]attention/],["reasoning",/chain[- ]of[- ]thought|rationale|reasoning trace|reasoning memory/],["demonstration",/in[- ]context|few[- ]shot|demonstration/],["synthetic",/self[- ]instruct|synthetic data|self[- ]generated instruction|self[- ]training/],
    ["hypergraph",/hypergraph/],["graph",/graph|knowledge graph|semantic network/],["retrieval",/retriev|nearest[- ]neighbor|rag\b/],["reflection",/reflect|retrospect|critique|self-correct/],
    ["skill",/skill library|skill bank|skill memory|procedural skill|skill[- ]aware/],["tool",/tool use|tool call|api\b|function call/],["harness",/harness|workflow|scaffold|agentic system/],
    ["search",/mcts|monte carlo|evolutionary search|quality[- ]diversity|gene[- ]bank|population search|tree search/],["critic",/critic|evaluator|grader|judge|verifier/],
    ["reward",/reward|preference|utility|score/],["rl",/reinforcement learning|policy gradient|\bppo\b|\bgrpo\b|\bdpo\b|lora|fine[- ]tun/],
    ["curriculum",/curriculum|task generat|question generat|experience synthesis/],["selfplay",/self[- ]play|population|broadcast|multi[- ]agent/],
    ["world",/world model|dynamics model|state transition|imagine[- ]then[- ]verify|prediction[- ]observation/],["planner",/planning|planner|reasoning policy/],
    ["embodied",/embodied|robot|navigation|physical|environment interaction|web agent|computer use|mobile gui/],["counterfactual",/counterfactual|intervention|causal/],
    ["provenance",/provenance|lineage|version|rollback|release engineering/],["compression",/compress|consolidat|prun|crystall|distill/],["safety",/safety|unsafe|attack|poison|backdoor|quarantine|guard/]
  ];
  return rules.filter(([,pattern])=>pattern.test(text)).map(([key])=>key).slice(0,6);
}
function paperMechanismLabel(key) {
  const labels = {
    attention:{zh:"Transformer / 多头注意力",en:"Transformer / multi-head attention"},reasoning:{zh:"显式推理/理由生成",en:"explicit reasoning / rationale generation"},demonstration:{zh:"上下文示例/任务演示",en:"in-context demonstrations"},synthetic:{zh:"自生成数据/自训练过滤",en:"self-generated data / self-training filter"},hypergraph:{zh:"超图结构",en:"hypergraph structure"},graph:{zh:"图结构/关系记忆",en:"graph-structured state"},retrieval:{zh:"检索器",en:"retriever"},reflection:{zh:"反思/经验抽取器",en:"reflection / experience extractor"},
    skill:{zh:"技能库",en:"skill library"},tool:{zh:"工具/API 调用层",en:"tool / API layer"},harness:{zh:"Harness / workflow 程序",en:"harness / workflow program"},search:{zh:"候选搜索/进化器",en:"candidate search / evolver"},
    critic:{zh:"Critic / evaluator / verifier",en:"critic / evaluator / verifier"},reward:{zh:"Reward / utility 信号",en:"reward / utility signal"},rl:{zh:"参数优化器",en:"parameter optimizer"},curriculum:{zh:"任务/课程生成器",en:"task / curriculum generator"},
    selfplay:{zh:"群体/自博弈机制",en:"population / self-play mechanism"},world:{zh:"世界模型/动力学状态",en:"world / dynamics model"},planner:{zh:"规划/决策器",en:"planner / decision policy"},embodied:{zh:"环境/机器人执行器",en:"environment / embodied executor"},
    counterfactual:{zh:"反事实/干预模块",en:"counterfactual / intervention module"},provenance:{zh:"版本/谱系/回滚层",en:"version / lineage / rollback layer"},compression:{zh:"压缩/巩固/剪枝模块",en:"compression / consolidation / pruning"},safety:{zh:"安全过滤/隔离层",en:"safety filter / quarantine layer"}
  };
  return textOf(labels[key] || {zh:key,en:key});
}
function paperSpecificFlow(record, kind, family, target, signal) {
  const text = `${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.subcategory || ""}`.toLowerCase();
  if (kind === "survey") return language === "zh" ? "定义检索问题与时间范围 → 从论文集/API/仓库收集候选 → 去重并按统一维度编码 → 比较更新对象、反馈、评测和失败边界 → 汇总研究空白与议程。" : "Define the review questions and time window → collect candidates from proceedings/APIs/repositories → deduplicate and code shared dimensions → compare update surfaces, feedback, evaluation, and failure boundaries → synthesize gaps and an agenda.";
  if (kind === "benchmark") return language === "zh" ? "先定义要暴露的能力或失败 → 构造任务/任务流与受控条件 → 让多种 Agent 在完全相同协议下运行 → 按统一指标和分组条件统计 → 检查哪些方法在什么场景失效。" : "Define the capability or failure to expose → construct tasks/streams and controlled conditions → run multiple agents under the same protocol → compute shared and subgroup metrics → identify where each method fails.";
  if (/hypergraph/.test(text)) return language === "zh" ? "把轨迹拆成子任务步骤与可复用技能 → 将步骤、技能及其多元关系写入超图 → 当前任务同时沿任务结构与技能关系检索 → 用执行结果更新节点/超边与效用 → 周期性整理超图后再服务后续任务。" : "Decompose trajectories into subtask steps and reusable skills → write steps, skills, and higher-order relations into a hypergraph → retrieve through both task structure and skill relations → update nodes/hyperedges from execution outcomes → periodically maintain the graph for later tasks.";
  if (/gene[- ]bank|quality[- ]diversity/.test(text)) return language === "zh" ? "保存一组语义上彼此不同的高质量 Harness → 根据失败诊断从 gene bank 选择并重组父代 → 生成新的 Harness 候选 → 先过低成本有效性/质量门 → 再做高成本任务评测 → 只有通过门的候选进入 bank。" : "Maintain a semantically diverse bank of strong harnesses → diagnose failures and select/recombine parents → generate new harness candidates → pass cheap validity/quality gates → run expensive task evaluation → admit only verified offspring back to the bank.";
  if (/population broadcast/.test(text) || (/broadcast/.test(text) && /memory/.test(text))) return language === "zh" ? "多个 Agent 实例分别执行任务并从失败轨迹生成语言记忆 → 评估每个实例的后续表现 → 选出当前最有效的记忆状态 → 把该记忆广播给群体 → 新一轮继续执行、反思和替换。" : "Let multiple agent instances act and derive verbal memories from failures → evaluate each instance on subsequent performance → select the strongest memory state → broadcast it to the population → repeat execution, reflection, and replacement.";
  if (/imagine[- ]then[- ]verify/.test(text)) return language === "zh" ? "从多模态轨迹抽取短期反思与长期启发式记忆 → 面对新状态先在记忆中形成候选行动/未来结果 → 用当前观测或环境执行去验证想象结果 → 把验证后的经验写回记忆，再用于后续决策。" : "Extract short-term reflections and long-term heuristics from multimodal trajectories → imagine candidate actions/outcomes in a new state → verify them against current observations or environment execution → write verified experience back to memory for later decisions.";
  if (/skill[- ]aware/.test(text) && /reflect/.test(text)) return language === "zh" ? "执行已有技能并记录轨迹 → 失败后先判断是“技能规则本身错”还是“Agent 没按正确规则执行” → 只有前一种证据触发技能重写 → 后一种只修正当前执行 → 用后续任务检查修改是否真的改善技能。" : "Execute the current skill and record the trajectory → after failure, distinguish a faulty skill rule from a lapse in following a valid rule → rewrite the persistent skill only for the former → correct execution only for the latter → test the revision on later tasks.";
  if (/co[- ]evol|co-evol/.test(text) && /evaluat|grader|metric/.test(text)) return language === "zh" ? "维护技能版本和显式评价指标 → 新技能产生后同时检查旧指标是否还能区分好坏 → 用锚定样例/多评判共识提出指标修订 → 在留出审计集上验证评价器没有漂移 → 通过后再让新指标参与下一轮技能选择。" : "Maintain skill versions and explicit evaluation metrics → after a new skill appears, test whether the old metric still separates good from bad behavior → revise metrics using anchored examples/consensus → audit evaluator drift on held-out cases → only then use the revised metric for the next skill-selection round.";
  const flows = {
    parameter: language === "zh" ? `收集 ${signal} 与轨迹/样本 → 过滤或构造训练对 → 用 RL、微调或 Adapter 更新 ${target} → 用新参数重新 rollout → 根据任务表现与留出结果决定继续训练、保留或回滚。` : `Collect ${signal} plus trajectories/examples → filter or construct training pairs → update ${target} with RL, fine-tuning, or adapters → roll out the new parameters → retain, continue, or roll back based on task and held-out results.`,
    prompt: language === "zh" ? `记录任务输出、失败与分数 → 把历史候选和反馈交给 prompt/文本优化器 → 生成新的 ${target} 候选 → 在开发任务上逐个执行比较 → 保留更好的版本并继续迭代 → 最后在未参与搜索的任务上复核。` : `Record outputs, failures, and scores → give candidate history and feedback to a prompt/text optimizer → generate new ${target} candidates → execute and compare them on development tasks → keep stronger versions and iterate → confirm on tasks not used by the search.`,
    memory: language === "zh" ? `执行 episode/轨迹 → 从成功、失败或反思中抽取可复用经验 → 写入并组织 ${target} → 新任务先检索相关经验再决策 → 用新的任务结果更新效用、关系、压缩或删除策略 → 检查跨回合收益和负迁移。` : `Run episodes/trajectories → extract reusable experience from success, failure, or reflection → write and organize ${target} → retrieve relevant experience before later decisions → use new outcomes to update utility, relations, compression, or pruning → measure cross-episode benefit and negative transfer.`,
    tool: language === "zh" ? `从轨迹中识别可重复操作模式 → 归纳/生成可执行的 ${target} → 存入带名称、说明或前置条件的技能/工具库 → 新任务检索并调用 → 用环境结果或测试验证 → 失败时修订、替换或淘汰具体技能。` : `Identify repeated procedures in trajectories → induce/generate executable ${target} → store them with names, descriptions, or preconditions in a skill/tool library → retrieve and invoke them on new tasks → verify with environment outcomes or tests → revise, replace, or retire failing skills.`,
    workflow: language === "zh" ? `把 Agent 的 ${target} 表示为可修改程序、图或 Harness → 根据失败轨迹/历史分数生成结构或组件变体 → 实际执行候选 → 用 evaluator、任务分数或 verifier 比较 → 提交最佳候选并保留版本/回滚信息 → 继续下一轮搜索。` : `Represent the agent's ${target} as a mutable program, graph, or harness → generate structural/component variants from failures or score history → execute candidates → compare with evaluators, task scores, or verifiers → commit the best candidate with version/rollback information → continue the search.`,
    world: language === "zh" ? `记录观测、动作和后继状态 → 更新 ${target} 中的环境规律/经验 → 用它预测候选动作的后果或规划下一步 → 在真实环境执行 → 比较预测与实际观测 → 只修订发生偏差的世界知识并在后续任务复用。` : `Record observations, actions, and successor states → update environmental knowledge in ${target} → predict action consequences or plan with it → execute in the real environment → compare prediction with observation → revise mismatched world knowledge and reuse it later.`,
    evaluation: language === "zh" ? `收集 Agent 输出/轨迹与参考证据 → 用 critic、grader、reward 或 verifier 给出反馈 → 与锚定真值、测试或独立评判比较 → 用该信号选择/拒绝 Agent 更新，必要时也修订评价器 → 在留出条件检查评价是否仍可靠。` : `Collect agent outputs/trajectories and reference evidence → score them with a critic, grader, reward, or verifier → compare against anchors, tests, or independent judgments → use the signal to accept/reject agent updates and, when applicable, revise the evaluator → audit reliability on held-out conditions.`,
    general: language === "zh" ? `收集 ${signal} → 定位需要变化的 ${target} → 生成一个或多个候选版本 → 在匹配任务上执行比较 → 按可观察结果保留、修订或拒绝 → 在后续/留出任务检查收益是否持续。` : `Collect ${signal} → identify the ${target} that should change → generate one or more candidate versions → execute them on matched tasks → retain, revise, or reject from observable outcomes → verify persistence on later/held-out tasks.`
  };
  return flows[family];
}
function paperConcreteDesign(record, analysis) {
  const kind = paperKind(record);
  const family = paperAnalysisFamily(record);
  const keys = paperMechanismKeys(record);
  const target = paperTargetLabel(record);
  const signal = paperSignalLabel(record);
  const text = `${record.title || ""} ${record.summary || ""} ${record.summaryZh || ""} ${record.signal || ""}`.toLowerCase();
  const components = [...new Set([target, ...keys.map(paperMechanismLabel)])].slice(0,6).join(language === "zh" ? " · " : " · ");
  const inputs = [];
  if (/trajectory|episode|rollout|execution trace/.test(text)) inputs.push(language === "zh" ? "执行轨迹 / episode" : "execution trajectories / episodes");
  if (/success|failure|outcome/.test(text)) inputs.push(language === "zh" ? "成功/失败结果" : "success/failure outcomes");
  if (/image|video|observation|visual|robot|environment|web/.test(text)) inputs.push(language === "zh" ? "视觉/环境观测" : "visual/environment observations");
  if (/reward|preference|utility|score/.test(text)) inputs.push(language === "zh" ? "reward / preference / utility" : "reward / preference / utility");
  if (/human|anchor|ground truth|verifier|test/.test(text)) inputs.push(language === "zh" ? "人工/锚点/验证器证据" : "human / anchor / verifier evidence");
  if (/task generat|question generat|synthetic|self-generated/.test(text)) inputs.push(language === "zh" ? "自生成任务/样本" : "self-generated tasks/examples");
  if (!inputs.length) inputs.push(signal);
  let artifact = target;
  if (kind === "survey") artifact = language === "zh" ? "分类体系、证据表和研究议程；不修改被综述 Agent" : "taxonomy, evidence map, and research agenda; no agent update";
  else if (kind === "benchmark") artifact = language === "zh" ? "任务/任务流、指标和评测结果；通常不修改被测 Agent" : "tasks/streams, metrics, and evaluation results; usually no agent update";
  else if (family === "memory") artifact = /hypergraph/.test(text) ? (language === "zh" ? "可持续更新的超图/结构化记忆" : "evolving hypergraph/structured memory") : (language === "zh" ? "可检索、可修订的持久记忆/经验条目" : "retrievable and revisable persistent memories/experience records");
  else if (family === "tool") artifact = language === "zh" ? "版本化的可执行技能/工具条目" : "versioned executable skills/tools";
  else if (family === "workflow") artifact = language === "zh" ? "新的 workflow / Harness / Agent 程序版本" : "a new workflow / harness / agent-program version";
  else if (family === "parameter") artifact = language === "zh" ? "更新后的模型权重、Adapter 或训练 checkpoint" : "updated model weights, adapters, or checkpoints";
  else if (family === "prompt") artifact = language === "zh" ? "新的 prompt / instruction / context 模板" : "a new prompt / instruction / context template";
  else if (family === "world") artifact = language === "zh" ? "更新后的世界模型、环境规律或具身经验" : "an updated world model, environment rule set, or embodied experience";
  else if (family === "evaluation") artifact = /evaluator|grader|critic|reward/.test(text) ? (language === "zh" ? "评价器/指标/奖励规则及其版本" : "evaluator/metric/reward-rule versions") : target;
  let acceptance = language === "zh" ? `主要依据 ${signal} 与任务表现决定候选是否保留；若论文没有公开固定提交门，则这里不臆造阈值。` : `Candidate retention is driven by ${signal} and task performance; if the paper does not expose a fixed commit gate, no threshold is invented here.`;
  if (kind === "benchmark") acceptance = language === "zh" ? "不做“提交更新”判断；统一运行协议后按主指标、分组指标和失败案例比较系统。" : "No update-commit decision; systems are compared under a shared protocol using primary/subgroup metrics and failure cases.";
  else if (kind === "survey") acceptance = language === "zh" ? "不做 Agent 更新；结论是否成立取决于检索覆盖、去重/分类一致性以及关键判断能否回到原始论文。" : "No agent update; validity depends on search coverage, deduplication/taxonomy consistency, and traceability of claims to primary papers.";
  else if (/verifier|verification|sealed|held[- ]out|test gate|validity gate/.test(text)) acceptance = language === "zh" ? "候选先通过 verifier / validity test / 留出测试，再进入持久版本；失败候选不提交或回滚。" : "Candidates pass verifier/validity/held-out tests before becoming persistent versions; failed candidates are rejected or rolled back.";
  else if (/reward|preference|utility|score/.test(text)) acceptance = language === "zh" ? "用 reward / utility / score 比较候选或更新其效用；真正是否持久保留还要看论文设置中的任务/留出表现。" : "Reward/utility/score ranks candidates or updates utility; persistence is then checked against task/held-out performance in the paper's protocol.";
  return {components, inputs:[...new Set(inputs)].slice(0,4).join(language === "zh" ? " · " : " · "), loop:analysis.logic, artifact, acceptance};
}
window.paperConcreteDesignAudit = function() {
  const rows = catalog || [];
  let missing = 0, s2SignalLeak = 0;
  rows.forEach((record) => {
    const analysis = paperAnalysis(record), design = paperConcreteDesign(record, analysis);
    if (![design.components,design.inputs,design.loop,design.artifact,design.acceptance].every(value=>String(value || "").trim())) missing += 1;
    if (/Semantic Scholar retrieval/i.test(paperSignalLabel(record))) s2SignalLeak += 1;
  });
  const getLoop = title => { const record=rows.find(row=>row.title===title); return record ? paperConcreteDesign(record,paperAnalysis(record)).loop : ""; };
  return {
    total:rows.length, missing, s2SignalLeak,
    samples:{
      hyper:getLoop("HyperSkill: Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory"),
      harness:getLoop("HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"),
      skill:getLoop("EmbodiSkill: Skill-Aware Reflection for Self-Evolving Embodied Agents")
    }
  };
};
function publishedReadingConfig(){ return window.PUBLISHED_LITERATURE_READING || {macroGroups:[],directions:{},mustRead:[],directionOverrides:{},foundationTitles:[],relationLabels:{}}; }
function publishedTitleKey(value){ return normalizeTitle(value || ""); }
function isPublishedFoundation(record){
  const keys=new Set((publishedReadingConfig().foundationTitles||[]).map(publishedTitleKey));
  return keys.has(publishedTitleKey(record.title));
}
function publishedVenueBand(record){
  const venue=String(record.venue||"");
  if(/workshop|findings/i.test(venue)) return {id:"workshop",label:{zh:"Workshop / Findings",en:"Workshop / Findings"}};
  if(/^openreview$/i.test(venue.trim())) return {id:"unresolved",label:{zh:"OpenReview 条目",en:"OpenReview record"}};
  return {id:"main",label:{zh:"主会 / 期刊",en:"Main conference / journal"}};
}
function isFormallyPublishedRecord(record){ return publicationType(record)==="Published" && publishedVenueBand(record).id!=="unresolved"; }
function publishedDirectionCode(record){
  if(isPublishedFoundation(record)) return "FOUNDATION";
  const cfg=publishedReadingConfig(), key=publishedTitleKey(record.title), override=cfg.directionOverrides?.[key];
  if(override) return override;
  const text=`${record.title||""} ${record.summary||""} ${record.summaryZh||""} ${record.category||""} ${record.subcategory||""} ${record.updateTarget||""} ${record.signal||""}`.toLowerCase();
  if(/poison|provenance|security|unsafe|attack|authorization|rollback|trustworthy|safety/.test(text)) return "D7";
  if(/budget|cost|econom|efficient|resource|constraint|stopping|compute/.test(text)) return "D8";
  if(/multi[- ]agent|opponent|coordination|population|supernet|team/.test(text)) return "D10";
  if(/benchmark|evaluation|critic|correct|forget|reliab|error detection|self-reflect/.test(text)) return "D6";
  if(/workflow|architecture|harness|router|agentic system|graph generation/.test(text)) return "D4";
  if(/tool|skill|api|program synthesis|script generator|tool use/.test(text)) return "D3";
  if(/memory|retriev|episodic|long[- ]term|experience bank|semantic memory/.test(text)) return "D2";
  if(/world model|embodied|robot|navigation|web agent|environment|device-control|locomotion/.test(text)) return "D5";
  if(/curriculum|reward|preference|self[- ]play|reinforcement learning|training/.test(text)) return "D9";
  return "D1";
}
function publishedDirectionMeta(code){ return publishedReadingConfig().directions?.[code] || null; }
function publishedReadingTier(record){
  const cfg=publishedReadingConfig(), must=new Set((cfg.mustRead||[]).map(publishedTitleKey));
  if(must.has(publishedTitleKey(record.title))) return "A";
  if(isPublishedFoundation(record)) return "C";
  const role=readingRoleInfo(record).id;
  if(role==="core-evolution") return "B";
  const text=`${record.title||""} ${record.summary||""} ${record.summaryZh||""} ${record.category||""} ${record.subcategory||""}`.toLowerCase();
  const direct=/self[- ]?(evolv|improv)|continual|lifelong|open[- ]ended|online curriculum|memory (agent|replay|management)|long[- ]term memory|skill (library|learning|generation)|agentic workflow|workflow generation|world model|retrospect|reflection|self[- ]correct|self[- ]reward|adaptive reinforcement|trustworthiness in web agents|forgetting.*agent|agent.*forgetting/.test(text);
  return direct ? "B" : "C";
}
function publishedTierLabel(record){
  const tier=publishedReadingTier(record), label=publishedReadingConfig().relationLabels?.[tier];
  return textOf(label || {zh:tier,en:tier});
}
function publishedEvidenceOverride(record){
  const evidence=window.PUBLISHED_PAPER_EVIDENCE || {};
  if(evidence[record.title]) return evidence[record.title];
  const key=publishedTitleKey(record.title);
  return Object.entries(evidence).find(([title])=>publishedTitleKey(title)===key)?.[1] || null;
}
function publishedEvidenceSummary(record){
  const zh=String(record.summaryZh||"").trim(), en=String(record.summary||"").trim();
  const pick=(text,pattern)=>String(text||"").split(/(?<=[.!?。！？])\s+/).find(sentence=>pattern.test(sentence)) || "";
  if(language==="zh"){
    const sentence=pick(zh,/提升|优于|改善|提高|超过|降低|发现|表明|实现|更好|退化|失败/);
    if(sentence) return `摘要报告：${sentence}`;
    if(zh) return `当前摘要明确了论文做法，但没有给出可直接引用的结果数字。这里不把“方法描述”冒充实验结果；具体提升量仍回原文表格核对。`;
    return "当前已核验正式发表身份与方法主线，但还没有逐表抽取可直接引用的实验数字；这里明确留空，不自动编造“提升多少”。";
  }
  const sentence=pick(en,/outperform|improv|increase|gain|surpass|achiev|demonstrat|show|reduce|fail/i);
  if(sentence) return `Abstract reports: ${sentence}`;
  return "The publication and method path are verified in the library, but exact result-table numbers have not yet been extracted; no synthetic improvement figure is inserted here.";
}
function publishedPaperReadout(record, analysis=paperAnalysis(record), design=paperConcreteDesign(record,analysis)){
  if(!isFormallyPublishedRecord(record)) return null;
  const code=publishedDirectionCode(record), meta=publishedDirectionMeta(code);
  const relation=code==="FOUNDATION"
    ? (language==="zh"?"历史前置：解释后续 Agent 自进化能力从哪里来，但不把它误算成直接自进化方法。":"Historical precursor: enables later self-evolution but is not counted as a direct self-evolution method.")
    : (language==="zh"?`${code} · ${textOf(meta?.title||{})} · ${publishedTierLabel(record)}`:`${code} · ${textOf(meta?.title||{})} · ${publishedTierLabel(record)}`);
  const evidence=publishedEvidenceOverride(record);
  const simple=evidence?.simple ? textOf(evidence.simple) : (meta ? textOf(meta.baseline) : (language==="zh"?"把当前任务直接交给固定 Agent 运行，不在任务之间提交持久更新。":"Run a fixed agent without committing persistent cross-task updates."));
  const why=evidence?.why ? textOf(evidence.why) : (meta ? textOf(meta.gap) : (language==="zh"?"这种做法不能形成可持续、可审计的跨任务学习闭环。":"This does not form a durable, auditable cross-task learning loop."));
  return {
    code,tier:publishedReadingTier(record),venueBand:publishedVenueBand(record),
    scenario:evidence?.scenario ? textOf(evidence.scenario) : analysis.purpose,
    simple,why,
    method:evidence?.method ? textOf(evidence.method) : design.loop,
    difference:evidence?.difference ? textOf(evidence.difference) : analysis.advantage,
    observed:evidence?.observed ? textOf(evidence.observed) : publishedEvidenceSummary(record),
    proved:evidence?.proved ? textOf(evidence.proved) : (language==="zh"?`论文在自己的实验设置中按“${analysis.validation}”建立证据，因此可以把结论限定在该任务、模型与评测协议覆盖的范围内。`:`Within its own experimental setting, the paper uses the following validation path: ${analysis.validation}`),
    notProved:evidence?.notProved ? textOf(evidence.notProved) : (language==="zh"?"不能仅凭这篇论文推出：同一机制换模型、换任务分布、长期连续更新后仍保持同样收益，也不能把单次平均提升自动解释为没有旧能力回退。":"This alone does not establish the same gain across models, task distributions, or long update streams, nor does an average gain rule out regressions."),
    source:evidence?.source ? textOf(evidence.source) : "",
    relation
  };
}
function renderPublishedQuickRead(record, analysis, design){
  const read=publishedPaperReadout(record,analysis,design); if(!read) return "";
  const cells=[
    [language==="zh"?"1 · 具体任务场景":"1 · Concrete scenario",read.scenario],
    [language==="zh"?"2 · 以前最简单的方法怎么做":"2 · Simplest previous approach",read.simple],
    [language==="zh"?"3 · 为什么还不够":"3 · Why that is insufficient",read.why],
    [language==="zh"?"4 · 这篇论文具体怎么做":"4 · What this paper actually does",read.method],
    [language==="zh"?"5 · 相比简单方法多了什么":"5 · What is added beyond the baseline",read.difference],
    [language==="zh"?"6 · 实验实际看到了什么":"6 · What the experiments actually show",read.observed],
    [language==="zh"?"7 · 真正能证明到哪里":"7 · What the evidence supports",read.proved],
    [language==="zh"?"8 · 还不能证明什么":"8 · What remains unproven",read.notProved]
  ];
  return `<section class="published-paper-quickread"><header><div><b>${language==="zh"?"30 秒读懂这篇正式论文":"30-second reading of this publication"}</b><span>${esc(publishedTierLabel(record))} · ${esc(textOf(read.venueBand.label))}</span>${read.source?`<small class="published-evidence-source">${esc(read.source)}</small>`:""}</div><strong>${esc(read.relation)}</strong></header><div class="published-paper-quickread-grid">${cells.map(([label,value])=>`<div><b>${esc(label)}</b><p>${esc(value||"")}</p></div>`).join("")}</div></section>`;
}
function publishedPapers(){ return catalog.filter(isFormallyPublishedRecord); }
function publishedDirectionPapers(code){
  return publishedPapers().filter(record=>publishedDirectionCode(record)===code).sort((a,b)=>{
    const ta=publishedReadingTier(a),tb=publishedReadingTier(b), order={A:0,B:1,C:2};
    return order[ta]-order[tb] || (a.year||0)-(b.year||0) || String(a.title).localeCompare(String(b.title));
  });
}
function renderPublishedSpine(){
  const cfg=publishedReadingConfig(), rows=publishedPapers(), counts={A:0,B:0,C:0}; rows.forEach(p=>counts[publishedReadingTier(p)]++);
  const main=rows.filter(p=>publishedVenueBand(p).id==="main").length, workshop=rows.filter(p=>publishedVenueBand(p).id==="workshop").length;
  const macro=cfg.macroGroups.map(group=>{
    const dirs=group.directions.map(code=>{const meta=publishedDirectionMeta(code),ps=publishedDirectionPapers(code),direct=ps.filter(p=>publishedReadingTier(p)!=="C").length,adj=ps.length-direct;return `<a href="#published-direction-${code.toLowerCase()}"><b>${code} · ${textOf(meta?.title||{})}</b><span>${direct} ${language==="zh"?"篇主线/直接":"main/direct"}${adj?` · +${adj} ${language==="zh"?"邻接":"adjacent"}`:""}</span></a>`;}).join("");
    return `<article class="published-question-card"><span>${group.code}</span><div><h3 data-toc="false">${textOf(group.title)}</h3><p>${textOf(group.plain)}</p><nav>${dirs}</nav></div></article>`;
  }).join("");
  const stories=Object.entries(cfg.directions||{}).map(([code,meta])=>{
    const papers=publishedDirectionPapers(code), featured=papers.slice(0,6);
    const paperLinks=featured.length?featured.map(p=>`<a href="${directionPaperHref(p.title)}"><span>${p.year||""}</span><b>${esc(p.title)}</b><small>${esc(publishedTierLabel(p))}</small></a>`).join(""):`<div class="published-empty-gap">${language==="zh"?"当前核验的正式主线里还没有足够直接论文；这是文献空白，不用预印本假装填满。":"No sufficiently direct peer-reviewed mainline work is currently verified; the gap is kept visible rather than filled with preprints."}</div>`;
    const directCount=papers.filter(p=>publishedReadingTier(p)!=="C").length, adjacentCount=papers.length-directCount;
    return `<details class="published-direction-story" id="published-direction-${code.toLowerCase()}" ${["D2","D3","D4","D6"].includes(code)?"open":""}><summary><div><span>${code}</span><div><b>${textOf(meta.title)}</b><small>${textOf(meta.question)}</small></div></div><strong>${directCount} ${language==="zh"?"主线/直接":"main/direct"}${adjacentCount?` · +${adjacentCount} ${language==="zh"?"邻接":"adjacent"}`:""}</strong></summary><div class="published-direction-story-body"><section><b>${language==="zh"?"先把场景说清楚":"Concrete scene"}</b><p>${textOf(meta.scene)}</p></section><section class="simple"><b>${language==="zh"?"以前最简单的方法怎么做":"Simplest prior design"}</b><p>${textOf(meta.baseline)}</p></section><section><b>${language==="zh"?"为什么简单方法不够":"Why it breaks"}</b><p>${textOf(meta.gap)}</p></section><section><b>${language==="zh"?"方法发展主线":"Method progression"}</b><p>${textOf(meta.progression)}</p></section><div class="published-direction-paper-links">${paperLinks}</div></div></details>`;
  }).join("");
  const foundations=rows.filter(isPublishedFoundation).sort((a,b)=>(a.year||0)-(b.year||0));
  return `<section class="panel published-spine-intro"><div><div class="eyebrow">${language==="zh"?"先读正式发表 · 再看预印本前沿":"PEER-REVIEWED SPINE FIRST"}</div><h3 data-toc="false">${language==="zh"?"先用正式论文把 Agent 自进化的研究主线搭起来":"Build the field spine from published work first"}</h3><p>${language==="zh"?"这一层只使用页面当前明确标记为“正式发表”的记录。主会/期刊与 Workshop/Findings 分开标注；预印本不混进来。":"This layer uses only records currently classified as published. Main venues and workshop/findings records are distinguished; preprints stay outside."}</p></div><div class="published-spine-stats"><span><b>${rows.length}</b>${language==="zh"?"篇正式记录":"published"}</span><span><b>${main}</b>${language==="zh"?"主会/期刊":"main venues"}</span><span><b>${workshop}</b>Workshop / Findings</span><span><b>${counts.A}</b>${language==="zh"?"主线必读":"must-read"}</span></div></section><div class="published-question-grid">${macro}</div><section class="panel published-tier-guide"><b>${language==="zh"?"同样是正式论文，也按阅读价值分层":"Published papers still have reading tiers"}</b><div>${["A","B","C"].map(t=>`<span><strong>${counts[t]}</strong>${textOf(cfg.relationLabels?.[t]||{})}</span>`).join("")}</div><p>${language==="zh"?"A 做逐篇深读；B 用于补齐直接近邻；C 保留历史前置和邻接机制。正式发表 ≠ 都是 Agent 自进化核心论文。":"A receives deep reading, B fills direct neighbors, and C preserves foundations/adjacent mechanisms. Publication does not make every paper a core self-evolution paper."}</p></section><div class="published-direction-stories">${stories}</div>${foundations.length?`<section class="panel published-foundations"><h3 data-toc="false">${language==="zh"?"历史前置：重要，但不误算成直接自进化":"Historical foundations: important, but not direct self-evolution"}</h3><div>${foundations.map(p=>`<a href="${directionPaperHref(p.title)}"><span>${p.year}</span><b>${esc(p.title)}</b><small>${esc(p.venue||"")}</small></a>`).join("")}</div></section>`:""}`;
}
function renderPublishedComparisons(){
  const cfg=publishedReadingConfig();
  const sections=Object.entries(cfg.directions||{}).map(([code,meta])=>{
    const papers=publishedDirectionPapers(code).filter(p=>publishedReadingTier(p)!=="C").slice(0,8);
    if(!papers.length) return `<section class="panel published-comparison-section"><header><div><span>${code}</span><h3 data-toc="false">${textOf(meta.title)}</h3></div><strong>${language==="zh"?"正式主线仍稀疏":"peer-reviewed gap"}</strong></header><p class="section-intro">${textOf(meta.gap)}</p></section>`;
    const body=papers.map(p=>{const a=paperAnalysis(p),d=paperConcreteDesign(p,a),r=publishedPaperReadout(p,a,d);return `<tr><td><a href="${directionPaperHref(p.title)}"><b>${esc(p.title)}</b></a><small>${p.year||""} · ${esc(p.venue||"")} · ${esc(publishedTierLabel(p))}</small></td><td>${esc(r.simple)}</td><td>${esc(r.difference)}</td><td>${esc(r.observed)}${r.source?`<small class="published-comparison-source">${esc(r.source)}</small>`:""}</td><td>${esc(r.relation)}</td></tr>`;}).join("");
    return `<section class="panel published-comparison-section"><header><div><span>${code}</span><h3 data-toc="false">${textOf(meta.title)}</h3></div><strong>${papers.length} ${language==="zh"?"篇重点比较":"compared"}</strong></header><p class="published-comparison-baseline"><b>${language==="zh"?"共同的简单起点":"Shared simple baseline"}</b>${textOf(meta.baseline)}</p><div class="published-comparison-scroll"><table><thead><tr><th>${language==="zh"?"论文":"Paper"}</th><th>${language==="zh"?"简单方法怎么做":"Simple method"}</th><th>${language==="zh"?"本文具体多了什么":"What the paper adds"}</th><th>${language==="zh"?"实验实际看到了什么":"Observed evidence"}</th><th>${language==="zh"?"与我们的关系":"Relation"}</th></tr></thead><tbody>${body}</tbody></table></div></section>`;
  }).join("");
  return `<section class="panel published-comparison-intro"><h3 data-toc="false">${language==="zh"?"不要逐篇孤立读：先看同一问题下，论文到底比简单方法多做了什么":"Compare papers within the same problem, not in isolation"}</h3><p>${language==="zh"?"横向表固定保留“简单方法怎么做”和“本文具体多了什么”。A 档主线论文优先使用逐篇核过的正式论文/项目页证据；正式来源没有一个统一汇总数字时就明确写出来，不用自动生成数字填空。":"The comparison fixes a concrete simple baseline and the added mechanism. A-tier papers prefer paper-specific source-grounded evidence; when the formal source exposes no single aggregate margin, the table says so instead of fabricating one."}</p></section>${sections}`;
}
window.publishedLiteratureAudit=function(){
  const rows=publishedPapers(), byTier={A:0,B:0,C:0}, byDirection={}, missingQuick=[];
  rows.forEach(p=>{const tier=publishedReadingTier(p),code=publishedDirectionCode(p);byTier[tier]++;byDirection[code]=(byDirection[code]||0)+1;const a=paperAnalysis(p),d=paperConcreteDesign(p,a),r=publishedPaperReadout(p,a,d);if(!r||![r.scenario,r.simple,r.why,r.method,r.difference,r.observed,r.proved,r.notProved,r.relation].every(v=>String(v||"").trim()))missingQuick.push(p.title);});
  const cfg=publishedReadingConfig(), evidence=window.PUBLISHED_PAPER_EVIDENCE||{}, mustRead=cfg.mustRead||[];
  const missingMustReadEvidence=mustRead.filter(title=>!publishedEvidenceOverride({title}));
  const paperSpecificEvidence=mustRead.filter(title=>publishedEvidenceOverride({title})).length;
  const numericEvidence=Object.values(evidence).filter(row=>/\d/.test(`${textOf(row.observed||{})}`)).length;
  return {published:rows.length,byTier,byDirection,missingQuick,workshopFindings:rows.filter(p=>publishedVenueBand(p).id==="workshop").length,mainVenue:rows.filter(p=>publishedVenueBand(p).id==="main").length,mustRead:mustRead.length,paperSpecificEvidence,numericEvidence,missingMustReadEvidence};
};
function literatureIdeaMiningConfig(){return window.LITERATURE_IDEA_MINING||{principles:[],directions:{},intersections:[],candidateContract:[]};}
function literatureIdeaCollisionConfig(){return window.LITERATURE_IDEA_COLLISIONS||{research_items:0,directions:{}};}
function ideaOpportunityMeta(level){
  const map={high:{rank:0,zh:"优先补缺",en:"Priority gap"},"medium-high":{rank:1,zh:"有明显机会",en:"Strong seam"},medium:{rank:2,zh:"窄缝机会",en:"Narrow seam"},crowded:{rank:3,zh:"高度拥挤",en:"Crowded"}};
  return map[level]||{rank:9,zh:level||"未分类",en:level||"Unclassified"};
}
function ideaMiningPublishedCounts(code){
  const rows=publishedDirectionPapers(code), counts={A:0,B:0,C:0};
  rows.forEach(row=>{const tier=publishedReadingTier(row);counts[tier]=(counts[tier]||0)+1;});
  return {...counts,direct:counts.A+counts.B,total:rows.length};
}
function renderIdeaMiningDirection(code,meta){
  const counts=ideaMiningPublishedCounts(code), opp=ideaOpportunityMeta(meta.opportunity), current=literatureIdeaMiningConfig().currentCategoryMap?.[code]||HISTORICAL_TO_CURRENT_CATEGORIES[code]||[];
  const categories=current.map(category=>`<a href="research-map.html#research-map-${category.toLowerCase()}">${category}</a>`).join("");
  const nearest=(meta.nearest||[]).map(title=>`<a href="${directionPaperHref(title)}">${esc(title)}</a>`).join("");
  const seeds=(meta.seedQuestions||[]).map(item=>`<li>${esc(item)}</li>`).join("");
  const collision=literatureIdeaCollisionConfig().directions?.[code]||{active:[],mapped_count:0,terminal_count:0};
  const activeInternal=[...(collision.active||[])].sort((a,b)=>String(a.code).localeCompare(String(b.code)));
  const concludedInternal=Number(collision.terminal_count||0);
  const internalLinks=activeInternal.map(row=>`<a href="paper-ideas.html?research=${encodeURIComponent(row.code)}"><b>${esc(row.code)}</b><span>${esc(textOf(row.title||{}))}</span><small>${esc(row.scientific_state||"")}</small></a>`).join("");
  return `<details class="idea-mining-direction idea-opportunity-${esc(meta.opportunity||"unknown")}" data-idea-direction="${esc(code)}" ${meta.opportunity==="high"?"open":""}><summary><div><span class="idea-mining-code">${esc(code)}</span><div><b>${textOf(publishedDirectionMeta(code)?.title||{})}</b><small>${textOf(meta.label||{})}</small></div></div><div class="idea-mining-counts"><strong>${counts.direct}</strong><span>${language==="zh"?"篇 A/B 正式近邻":"A/B published neighbors"}</span></div></summary><div class="idea-mining-body"><section><b>${language==="zh"?"已经被做掉的主线":"Already covered"}</b><p>${textOf(meta.covered)}</p></section><section class="collision"><b>${language==="zh"?"高碰撞排除项":"High-collision exclusion"}</b><p>${textOf(meta.collision)}</p></section><section><b>${language==="zh"?"文献反复暴露的失败":"Repeated failure"}</b><p>${textOf(meta.failure)}</p></section><section class="opening"><b>${language==="zh"?"还值得继续挖的断层":"Surviving opening"}</b><p>${textOf(meta.open)}</p></section><section class="idea-mining-seeds"><b>${language==="zh"?"后续 API 碰撞优先问":"Questions to seed later API collisions"}</b><ol>${seeds}</ol></section><section class="idea-mining-nearest"><b>${language==="zh"?"生成候选后必须先撞这些正式近邻":"Nearest published work to collide first"}</b><div>${nearest||`<span>${language==="zh"?"当前正式主线较稀疏":"Published line currently sparse"}</span>`}</div></section><section class="idea-mining-internal"><b>${language==="zh"?"再撞我们自己当前 ResearchItem（粗粒度接口）":"Then collide with our current ResearchItems (coarse interface)"}</b><p>${language==="zh"?`D→A–G 是多对多领域映射，不代表这些对象一定与新候选精确重复；但生成前必须先检查。当前可关注 ${activeInternal.length} 个，另有 ${concludedInternal} 个 STOPPED/MERGED 历史对象不能无证据复活。`:`D→A–G is a coarse many-to-many map, not proof of duplication. Check ${activeInternal.length} active/reopenable items and ${concludedInternal} stopped/merged historical objects before generation.`}</p><div>${internalLinks||`<span>${language==="zh"?"当前映射大类没有 HOLD / PAPER_READY 对象；仍需检查终止历史。":"No HOLD / PAPER_READY item in the mapped categories; stopped history still requires collision checking."}</span>`}</div></section><footer><span class="idea-opportunity-pill">${language==="zh"?opp.zh:opp.en}</span><span><b>${language==="zh"?"当前 A–G 接口":"Current A–G interfaces"}</b>${categories||"—"}</span><code>${esc(meta.searchTerms||"")}</code></footer></div></details>`;
}
function renderLiteratureIdeaMining(){
  const cfg=literatureIdeaMiningConfig(), opportunityRank=([,meta])=>ideaOpportunityMeta(meta.opportunity).rank;
  const principles=(cfg.principles||[]).map((row,index)=>`<article><span>0${index+1}</span><div><b>${textOf(row.title)}</b><p>${textOf(row.body)}</p></div></article>`).join("");
  const intersections=(cfg.intersections||[]).map(row=>`<article class="idea-intersection-card"><header><span>${esc(row.id)}</span><b>${textOf(row.title)}</b></header><p>${textOf(row.question)}</p><small>${textOf(row.why)}</small><div>${(row.codes||[]).map(code=>`<a href="#idea-gap-${code.toLowerCase()}">${esc(code)}</a>`).join("")}</div></article>`).join("");
  const contract=(cfg.candidateContract||[]).map((row,index)=>`<article><span>${index+1}</span><p>${esc(language==="zh"?row.zh:row.en)}</p></article>`).join("");
  const gapCards=Object.entries(cfg.directions||{}).sort((a,b)=>opportunityRank(a)-opportunityRank(b)||a[0].localeCompare(b[0])).map(([code,meta])=>`<div id="idea-gap-${code.toLowerCase()}" class="idea-gap-anchor">${renderIdeaMiningDirection(code,meta)}</div>`).join("");
  return `<section class="panel idea-mining-intro"><div class="eyebrow">${language==="zh"?"LITERATURE → IDEA MINING":"LITERATURE → IDEA MINING"}</div><div class="idea-mining-intro-head"><div><h3 data-toc="false">${language==="zh"?"这里不直接生成候选研究问题；先把“不能再做什么”和“真正还缺什么”整理成搜索空间":"Do not generate ideas yet; first turn covered territory and surviving gaps into a search space"}</h3><p>${textOf(cfg.basis||{})}</p></div><a class="link-btn" href="generated/literature-idea-mining-input.json" target="_blank" rel="noopener">${language==="zh"?"机器可读 Gap Registry ↗":"Machine-readable gap registry ↗"}</a></div><div class="idea-mining-principles">${principles}</div></section><section class="idea-mining-priority-strip">${Object.entries(cfg.directions||{}).sort((a,b)=>opportunityRank(a)-opportunityRank(b)||a[0].localeCompare(b[0])).map(([code,meta])=>{const c=ideaMiningPublishedCounts(code),o=ideaOpportunityMeta(meta.opportunity);return `<a href="#idea-gap-${code.toLowerCase()}" class="idea-opportunity-${esc(meta.opportunity)}"><b>${code}</b><span>${language==="zh"?o.zh:o.en}</span><small>${c.direct} ${language==="zh"?"篇正式 A/B 近邻":"A/B published"}</small></a>`;}).join("")}</section><div class="idea-mining-directions">${gapCards}</div><section class="panel idea-intersection-panel"><h3 data-toc="false">${language==="zh"?"优先看接口断层：成熟方向交叉处比“再加一个模块”更容易长出新科学问题":"Prioritize interface gaps between mature lines"}</h3><p class="section-intro">${language==="zh"?"这些不是候选论文，也不会自动进入 ResearchItem；它们只是后续批量 API 候选碰撞的高价值问题轴。":"These are not paper candidates and do not enter ResearchItem automatically; they are high-value axes for later batch idea collision."}</p><div class="idea-intersection-grid">${intersections}</div></section><section class="panel idea-candidate-contract"><h3 data-toc="false">${language==="zh"?"一个文献空白什么时候才值得升级成候选研究问题？":"When may a literature gap become an idea candidate?"}</h3><div>${contract}</div><p>${language==="zh"?"只有这 7 项都能写清楚，才把 gap 送入后续候选生成器 / tournament；否则继续留在 Literature Gap Registry。":"Only when all seven fields are explicit should a gap enter the later idea generator/tournament; otherwise it stays in the Literature Gap Registry."}</p></section>`;
}
window.literatureIdeaMiningAudit=function(){
  const cfg=literatureIdeaMiningConfig(), directions=Object.entries(cfg.directions||{}), missing=[];
  directions.forEach(([code,row])=>{if(![row.opportunity,row.covered,row.collision,row.failure,row.open,row.searchTerms].every(v=>String(v||"").trim())||(row.seedQuestions||[]).length<3||(row.nearest||[]).length<2)missing.push(code);});
  const collisionCfg=literatureIdeaCollisionConfig(), activeRefs=[], terminalRefs=[];
  directions.forEach(([code])=>{const block=collisionCfg.directions?.[code]||{};(block.active||[]).forEach(row=>activeRefs.push(`${code}:${row.code}`));for(let i=0;i<Number(block.terminal_count||0);i++)terminalRefs.push(`${code}:${i}`);});
  const uniqueActive=[...new Set(activeRefs.map(ref=>ref.split(":")[1]))];
  return {directions:directions.length,intersections:(cfg.intersections||[]).length,contract:(cfg.candidateContract||[]).length,missing,high:directions.filter(([,row])=>row.opportunity==="high").map(([code])=>code),crowded:directions.filter(([,row])=>row.opportunity==="crowded").map(([code])=>code),researchItems:Number(collisionCfg.research_items||0),activeCollisionRefs:activeRefs.length,uniqueActiveResearchItems:uniqueActive,terminalCollisionRefs:terminalRefs.length};
};
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
  const topic = localizedTaxonomy(record.subcategory || record.category || record.title);
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
      logic:paperSpecificFlow(record, kind, family, target, signal),
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
      logic:paperSpecificFlow(record, kind, family, target, signal),
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
    logic:paperSpecificFlow(record, kind, family, target, signal),
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
  const design = paperConcreteDesign(record, analysis);
  const quick = publishedPaperReadout(record, analysis, design);
  return [record.title,record.venue,record.category,record.subcategory,record.updateTarget,record.signal,publicationType(record),analysis.purpose,analysis.advantage,analysis.core,analysis.rationale,analysis.logic,analysis.validation,analysis.importance,design.components,design.inputs,design.loop,design.artifact,design.acceptance,quick?.simple,quick?.why,quick?.observed,quick?.relation].join(" ").toLowerCase();
}
function paperCard(p, priorityRank = null) {
  const summary = language === "zh" ? (p.summaryZh || p.summary || "") : (p.summary || p.summaryZh || "");
  const refNo = p.refNo || catalog.indexOf(p) + 1;
  const slug = p.slug || slugify(p.title);
  const type = publicationType(p);
  const analysis = paperAnalysis(p);
  const design = paperConcreteDesign(p, analysis);
  const citations = citationCount(p);
  const citationMeta = citationMetadata(p);
  const citationInfo = citationCountInfo(p);
  const citationSource = citationInfo.source;
  const tierLabel = publicationTierLabel(p);
  const role = readingRoleInfo(p);
  const anchor = mustReadAnchorInfo(p);
  const analysisSearch = [analysis.purpose,analysis.advantage,analysis.core,analysis.rationale,analysis.logic,analysis.validation,analysis.importance,design.components,design.inputs,design.loop,design.artifact,design.acceptance].join(" ");
  return `<article class="card reference-card" id="ref-${slug}" data-reading-role="${esc(role.id)}" data-role-rank="${readingRoleRank(p)}" data-tier="${publicationTier(p)}" data-citations="${citations === null ? -1 : citations}" data-year="${p.year || 0}" data-priority-rank="${priorityRank || ""}" data-must-read-rank="${anchor?.rank || ""}" data-search="${esc([p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal,type,analysisSearch].join(" ").toLowerCase())}"><div class="card-top"><div>${priorityRank ? `<div class="paper-priority-rank">${language === "zh" ? "推荐序号" : "reading order"} #${priorityRank}</div>` : ""}<h3 data-toc="false"><a class="ref-number" href="#ref-${slug}">[${refNo}]</a> ${esc(p.title)}</h3><div class="meta">${esc(String(p.year || ""))} · ${esc(localizedVenue(p.venue || "Unknown venue"))} · ${esc(localizedCategory(p.category || "Unclassified"))}</div></div><div class="badges">${anchor ? `<span class="badge must-read">${language === "zh" ? `必读 #${anchor.rank}` : `must-read #${anchor.rank}`}</span>` : ""}<span class="badge reading-role">${esc(textOf(role.title))}</span><span class="badge ranking-tier">${esc(tierLabel)}</span><span class="badge citation-count ${citations === null ? "citation-pending" : ""}">${citations === null ? (language === "zh" ? "引用量待匹配" : "citations pending") : `${citations.toLocaleString(language === "zh" ? "zh-CN" : "en-US")} ${language === "zh" ? "次引用" : "citations"}`}</span><span class="badge publication-type">${esc(localizedPublicationType(type))}</span><span class="badge ${p.vision ? "vision" : ""}">${p.vision ? (language === "zh" ? "视觉/多模态" : "vision/multimodal") : (language === "zh" ? "通用" : "general")}</span><span class="badge ${p.updateTarget === "model parameters" ? "model" : "scaffold"}">${esc(localizedUpdateTarget(p.updateTarget || "agent component"))}</span><span class="badge">${esc(localizedSignal(p.signal || "feedback"))}</span></div></div>${citations !== null && citationSource ? `<div class="citation-source-note">${language === "zh" ? "引用数据" : "Citation data"}: ${esc(citationSource)}${citationInfo.matchScore !== null ? ` · ${language === "zh" ? "匹配" : "match"} ${Math.round((citationInfo.matchScore || 0) * 100)}%` : ""}</div>` : ""}${anchor ? `<div class="must-read-note"><b>${language === "zh" ? "为什么先读" : "Why read first"}</b><span>${esc(textOf(anchor.reason))}</span>${anchor.team ? `<small>${language === "zh" ? "核验作者 / 团队：" : "Verified authors / team: "}${esc(textOf(anchor.team))}</small>` : ""}</div>` : ""}${summary ? `<p>${esc(summary)}</p>` : ""}<details class="paper-analysis"><summary><span>${language === "zh" ? "论文怎么做 · 六项判断 + 具体实现" : "How it works · analysis + concrete design"}</span><small>${paperAnalysisLabel(analysis)}</small></summary><div class="paper-analysis-disclaimer">${analysis.basis === "curated-full" ? (language === "zh" ? "六项内容已针对该论文单独整理；仍建议在正式引用具体实验数字前回看原文。" : "All six fields are paper-specific; consult the original paper before citing exact experimental numbers.") : analysis.basis === "curated" ? (language === "zh" ? "核心方法描述已针对该论文单独整理；其余字段仍是面向快速阅读的压缩解释。" : "The core method description is paper-specific; the other fields remain compressed reading aids.") : (language === "zh" ? "该概览依据标题、目录分类、更新对象、反馈信号和已有摘要自动归纳；准确引用方法细节时仍应回看原文。" : "This overview is derived from the title, catalog taxonomy, update surface, feedback signal, and available summary. Consult the paper before citing method details.")}</div>${renderPublishedQuickRead(p, analysis, design)}<div class="paper-analysis-grid"><div><b>${language === "zh" ? "问题动机（含重要性）" : "Problem motivation"}</b><p>${esc(analysis.purpose)}</p>${analysis.basis === "curated-full" ? "" : `<small>${esc(analysis.importance || "")}</small>`}</div><div><b>${language === "zh" ? "相对优势" : "Comparative advantage"}</b><p>${esc(analysis.advantage)}</p></div><div><b>${language === "zh" ? "核心直觉" : "Core intuition"}</b><p>${esc(analysis.core)}</p></div><div><b>${language === "zh" ? "成立依据" : "Why it should work"}</b><p>${esc(analysis.rationale)}</p></div><div><b>${language === "zh" ? "方法流程" : "Method flow"}</b><p>${esc(analysis.logic)}</p></div><div><b>${language === "zh" ? "实验验证" : "Experimental validation"}</b><p>${esc(analysis.validation || "")}</p></div></div><section class="paper-design-breakdown"><header><b>${language === "zh" ? "具体设计：这篇论文到底怎么做" : "Concrete design: how the paper actually works"}</b><span>${language === "zh" ? "按组件、输入、更新闭环、持久产物与接受规则拆开" : "Decomposed into components, inputs, update loop, persistent artifact, and acceptance rule"}</span></header><div class="paper-design-grid"><div><b>${language === "zh" ? "1 · 系统组成" : "1 · Components"}</b><p>${esc(design.components)}</p></div><div><b>${language === "zh" ? "2 · 输入与反馈" : "2 · Inputs & feedback"}</b><p>${esc(design.inputs)}</p></div><div class="paper-design-loop"><b>${language === "zh" ? "3 · 一次更新怎么跑" : "3 · One update cycle"}</b><p>${esc(design.loop)}</p></div><div><b>${language === "zh" ? "4 · 最后留下什么" : "4 · Persistent artifact"}</b><p>${esc(design.artifact)}</p></div><div><b>${language === "zh" ? "5 · 怎么决定保留" : "5 · Acceptance / validation"}</b><p>${esc(design.acceptance)}</p></div></div></section></details><div class="links"><a class="link-btn" href="${esc(p.url)}" target="_blank" rel="noopener">${language === "zh" ? "论文" : "Paper"}</a>${p.repo ? `<a class="link-btn repo" href="${esc(p.repo)}" target="_blank" rel="noopener">${language === "zh" ? "代码" : "Code"}</a>` : ""}<button class="link-btn copy-citation" type="button" data-record="${encodeURIComponent(slug)}">${language === "zh" ? "复制引用" : "Copy citation"}</button><a class="link-btn cite-link" href="bibliography.html?paper=${encodeURIComponent(slug)}#ref-${slug}">${language === "zh" ? "引用定位" : "Reference"}</a></div></article>`;
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
  localizeRenderedChinese(list);
  requestAnimationFrame(() => applyReadabilityFloor(list));
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
  localizeRenderedChinese(box);
  requestAnimationFrame(() => applyReadabilityFloor(box));
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
  if (pageId === "selected-paper") {
    const papers = [...document.querySelectorAll("#dynamic-page [data-paper-toc-root]")];
    const rows = papers.map((paper,index) => {
      const heading = paper.querySelector(":scope > .paper-detail-header h2") || paper.querySelector("h2");
      if (!heading) return null;
      const rootId = paper.id || heading.id || `paper-${index+1}`;
      if (!paper.id && !heading.id) heading.id = rootId;
      const children = [...paper.querySelectorAll("h3[data-paper-toc-child]")].map((child,childIndex) => {
        if (!child.id) child.id = `${rootId}-section-${childIndex+1}`;
        return {id:child.id,label:(child.dataset.tocLabel || child.textContent).trim()};
      });
      return {id:rootId,label:(heading.dataset.tocLabel || heading.textContent).trim(),children};
    }).filter(Boolean);
    container.innerHTML = rows.length ? `<div class="toc-title">${language === "zh" ? "论文目录" : "Papers"}</div><nav class="toc-tree paper-toc-tree" aria-label="${language === "zh" ? "论文页内目录" : "Paper page contents"}"><ul>${rows.map((row) => `<li class="toc-node toc-level-2 paper-toc-root"><a href="#${esc(row.id)}">${esc(row.label)}</a>${row.children.length ? `<ul>${row.children.map((child) => `<li class="toc-node toc-level-3"><a href="#${esc(child.id)}">${esc(child.label)}</a></li>`).join("")}</ul>` : ""}</li>`).join("")}</ul></nav>` : "";
    return;
  }
  const tocSelector = "#dynamic-page h2, #dynamic-page h3";
  const headings = [...document.querySelectorAll(tocSelector)].filter((heading) => heading.dataset.toc !== "false" && !heading.closest(".review-trace-fold,.review-archive-fold,.system-deep-dive") && (heading.id || heading.closest(".panel, .page-chapter, .merged-group, .direction-cluster, .idea-macro-cluster")));
  headings.forEach((heading, index) => { if (!heading.id) heading.id = `${slugify(heading.textContent)}-${index + 1}`; });
  const root = [];
  const stack = [{level:1, children:root}];
  headings.forEach((heading) => {
    const level = Number(heading.tagName.slice(1));
    while (stack.length > 1 && stack[stack.length - 1].level >= level) stack.pop();
    const node = {level, id:heading.id, label:(heading.dataset.tocLabel || heading.textContent).trim(), children:[]};
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  });
  const renderNodes = (nodes) => `<ul>${nodes.map((node) => `<li class="toc-node toc-level-${node.level}"><a href="#${esc(node.id)}">${esc(node.label)}</a>${node.children.length ? renderNodes(node.children) : ""}</li>`).join("")}</ul>`;
  container.innerHTML = headings.length ? `<div class="toc-title">${language === "zh" ? "本页多级目录" : "Page hierarchy"}</div><nav class="toc-tree" aria-label="${language === "zh" ? "页内多级目录" : "Hierarchical page contents"}">${renderNodes(root)}</nav>` : "";
}
function localizeRenderedChinese(root = document) {
  if (language !== "zh") return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach((node) => {
    const value = node.nodeValue || "";
    const trimmed = value.trim();
    if (ZH_PURE_TEXT.has(trimmed)) {
      node.nodeValue = value.replace(trimmed, ZH_PURE_TEXT.get(trimmed));
      return;
    }
    if (!/[\u3400-\u9fff]/.test(value) || !/[A-Za-z]{3}/.test(value)) return;
    const localized = localizeZhInline(value);
    if (localized !== value) node.nodeValue = localized;
  });
}
function applyReadabilityFloor(root = document) {
  const bodyTags = new Set(["P","LI","TD","DD"]);
  const mobile = window.matchMedia("(max-width: 820px)").matches;
  root.querySelectorAll(".layout *").forEach((node) => {
    if (![...node.childNodes].some((child) => child.nodeType === Node.TEXT_NODE && child.textContent.trim())) return;
    const size = Number.parseFloat(getComputedStyle(node).fontSize || "0");
    if (!Number.isFinite(size) || size <= 0) return;
    const floor = bodyTags.has(node.tagName) ? (mobile ? 12.5 : 12) : 11.5;
    if (size < floor) {
      node.classList.add(bodyTags.has(node.tagName) ? "readability-body-floor" : "readability-floor");
      node.style.setProperty("font-size", `${floor}px`, "important");
    }
  });
}
let readabilityResizeTimer = 0;
window.addEventListener("resize", () => {
  clearTimeout(readabilityResizeTimer);
  readabilityResizeTimer = window.setTimeout(() => applyReadabilityFloor(), 80);
}, { passive:true });
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
  else if (pageId === "research-timeline") root.innerHTML = window.renderResearchTimeline ? window.renderResearchTimeline(config) : `${pageHeader(config)}<div class="empty">Research timeline unavailable.</div>`;
  else if (pageId === "selected-paper") root.innerHTML = window.renderSelectedPaperWorkspace ? window.renderSelectedPaperWorkspace(config) : renderMergedHub(config);
  else if (config.renderMode === "field-matrix") root.innerHTML = renderFieldMatrixHub(config);
  else if (config.renderMode === "merged-hub") root.innerHTML = renderMergedHub(config);
  else if (pageId === "research-directions") root.innerHTML = renderDirectionMap(config);
  else if (pageId === "research-map") root.innerHTML = window.renderCurrentResearchMap ? window.renderCurrentResearchMap(config) : `${pageHeader(config)}<div class="empty">Current research map unavailable.</div>`;
  else if (pageId === "paper-ideas") root.innerHTML = renderIdeaPortfolio(config);
  else if (pageId === "experiments") root.innerHTML = renderExperimentDashboard(config);
  else if (pageId === "direction-board") root.innerHTML = renderIdeaRanking(config);
  else if (pageId === "bibliography") root.innerHTML = renderBibliography(config);
  else if (pageId === "repositories") root.innerHTML = renderDynamicResourceIndex(config, "repositories");
  else if (pageId === "datasets-benchmarks") root.innerHTML = renderDynamicResourceIndex(config, "benchmarks");
  else root.innerHTML = `${pageHeader(config)}${renderOverviewFigure(config)}${(config.sections || []).map(renderSection).join("")}`;
  document.querySelector(".language-toggle")?.replaceChildren(document.createTextNode(language === "en" ? "中文" : "English"));
  bindPageEvents();
  if (pageId === "research-timeline") window.bindResearchTimelineEvents?.();
  if (pageId === "paper-ideas") { initCanonicalIdeaFilters(); initIdeaBriefingMode(); focusResearchItemFromUrl(); }
  if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
  bindPaperCardEvents();
  hydrateCitations(root);
  updateCitationStatus();
  localizeRenderedChinese(root);
  buildToc();
  if (new Set(["mechanisms","research-directions"]).has(pageId) && location.hash) {
    const fieldAliases = pageId === "mechanisms" ? {
      "group-model-improvement":"field-model-parameters","group-prompt-evolution":"field-prompt-policy","group-memory-evolution":"field-memory","group-tool-evolution":"field-skill-tool","group-workflow-evolution":"field-workflow",
      "group-visual-multimodal":"field-multimodal","group-gui-web":"field-gui-web","group-embodied-world":"field-embodied","group-evaluation-safety":"field-evaluation-safety","group-datasets-benchmarks":"field-datasets-benchmarks","group-repositories":"field-repositories",
    } : {};
    const requestedId = decodeURIComponent(location.hash.slice(1));
    const targetId = fieldAliases[requestedId] || requestedId;
    const target = document.getElementById(targetId);
    const detail = target?.matches?.("details") ? target : target?.closest?.("details");
    if (detail) detail.open = true;
    if (target) requestAnimationFrame(() => target.scrollIntoView({block:"start"}));
  }
  requestAnimationFrame(() => applyReadabilityFloor());
}

function focusResearchItemFromUrl() {
  if (pageId !== "paper-ideas") return;
  const code = new URLSearchParams(window.location.search || "").get("research");
  if (!code) return;
  const normalized = String(code).trim().toUpperCase();
  const candidates = [
    document.getElementById(`idea-${normalized.toLowerCase()}`),
    ...[...document.querySelectorAll("[data-research-code],[data-pf-code],[data-closed-code]")].filter(node => String(node.dataset.researchCode || node.dataset.pfCode || node.dataset.closedCode || "").toUpperCase() === normalized)
  ].filter(Boolean);
  const target = candidates[0];
  if (!target) return;
  let node = target;
  while (node) {
    if (node.tagName === "DETAILS") node.open = true;
    node = node.parentElement;
  }
  target.classList.add("research-item-url-focus");
  requestAnimationFrame(() => target.scrollIntoView({behavior:"smooth",block:"center"}));
}

function bindSearch() {
  const input = document.getElementById("site-search");
  if (!input) return;
  input.addEventListener("input", () => {
    const query = input.value.trim();
    if (pageId === "bibliography") { bibliographyLimit = 80; renderPaperList(query); }
    else if (pageId === "research-timeline" && window.applyResearchTimelineFilters) window.applyResearchTimelineFilters(query);
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
