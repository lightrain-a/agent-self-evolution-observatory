const DATA = window.SUPPLEMENTAL_PAPERS || [];
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
const pageId = document.body.dataset.page || "home";
const initialQuery = new URLSearchParams(location.search);
let language = localStorage.getItem("agent-evolution-language") || "en";
let catalog = [];
let activeFilter = initialQuery.get("method") || "all";
let activeYear = initialQuery.get("year") || "all";
let activePublicationType = initialQuery.get("publication") || "all";
let activeSignal = initialQuery.get("signal") || "all";
let visionOnly = initialQuery.get("vision") === "1";
let bibliographyLimit = 80;
let citationIndex = new Map();
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
    ["Self-Improvements in Modern Agentic Systems: A Survey", "A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve", "Self-Improving Agents in the Era of Experience: A Survey of Self- to Meta-Evolution"],
    ["VisPlay: Self-Evolving Vision-Language Models", "WorldMM: Dynamic Multimodal Memory Agent for Long Video Reasoning", "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding", "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval", "The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators", "AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering"],
    ["AI Agent Pull Requests on GitHub: Frequency, Structure, and Merge Conflict Rates", "Partially Performative Prediction", "Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback", "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", "Towards Healthy Evolution: Exploring the Role and Mechanisms of Human-Agent Interaction in Self-Evolving Systems", "Self-Evolving Software Agents", "Accelerating Scientific Discovery with Autonomous Goal-evolving Agents"],
    ["SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", "AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering", "Self-Improvements in Modern Agentic Systems: A Survey"],
    ["Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", "MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", "HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry", "Partially Performative Prediction"],
    ["From Fixed to Free Cameras: Calibration-Free View-Robust Vision-Language-Action Model", "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", "Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback", "FSFM: A Biologically-Inspired Framework for Selective Forgetting of Agent Memory"],
    ["Self-Evolving Software Agents", "Accelerating Scientific Discovery with Autonomous Goal-evolving Agents", "The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators", "Self-Evolving Multi-Agent Systems via Decentralized Memory"],
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
  if (footer) footer.innerHTML = `${language === "zh" ? "Agent 自进化研究站" : "Agent Self-Evolution Observatory"} · <a href="coverage-method.html">${language === "zh" ? "覆盖协议" : "Coverage protocol"}</a> · <a href="bibliography.html">${language === "zh" ? "动态文献库" : "Live bibliography"}</a> · <a href="https://github.com/lightrain-a/agent-self-evolution-observatory" target="_blank" rel="noopener">GitHub</a> · 28 July 2026`;
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
function indexCatalog(records) {
  return records.map((record, index) => ({ ...record, refNo: index + 1, slug: slugify(record.title) })).map((record) => {
    citationIndex.set(normalizeTitle(record.title), record);
    return record;
  });
}
async function loadCatalog() {
  let upstream = [];
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
  citationIndex = new Map();
  catalog = indexCatalog(mergeCatalog(upstream, DATA));
  updateCounter();
  renderPage();
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
function renderSection(section, index) {
  const title = textOf(section.title);
  const id = section.id || slugify(title || `section-${index + 1}`);
  const citations = PAGE_CITATIONS[pageId]?.[index] || [];
  const referenceNote = citations.length ? `<div class="section-reference-note"><span>${language === "zh" ? "代表文献" : "Representative references"}</span><span data-cite="${esc(citations.join("||"))}"></span></div>` : "";
  return `<section class="panel topic-section"><h2 id="${id}">${title}</h2>${section.intro ? `<p class="section-intro">${textOf(section.intro)}</p>` : ""}<div class="section-body">${textOf(section.body)}${referenceNote}</div></section>`;
}
function renderHome(config) {
  const counts = {};
  catalog.forEach((p) => counts[p.updateTarget || "other"] = (counts[p.updateTarget || "other"] || 0) + 1);
  const featured = (config.featured || []).map((item) => `<a class="framework-card ${item.paper ? "paper-card" : ""}" href="${item.href}"><b>${textOf(item.title)}</b><span>${textOf(item.desc)}</span></a>`).join("");
  const figure = config.overviewFigure ? `<figure class="overview-figure"><a href="${esc(config.overviewFigure.src)}" target="_blank" rel="noopener"><img src="${esc(config.overviewFigure.src)}" alt="Agent self-evolution knowledge map"></a><figcaption>${textOf(config.overviewFigure.caption)}</figcaption></figure>` : "";
  const sortedSurfaces = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const maxSurface = Math.max(1, ...sortedSurfaces.map(([, count]) => count));
  const distribution = `<section class="panel"><h2 id="live-landscape">${language === "zh" ? "动态研究分布" : "Live research landscape"}</h2><p class="section-intro">${language === "zh" ? "根据当前合并文献库自动统计；自动分类用于导航，核心专题仍经过人工核验。" : "Computed from the current merged corpus. Automatic categories support navigation; core topic synthesis remains manually reviewed."}</p><div class="distribution-list">${sortedSurfaces.map(([surface, count]) => `<a class="distribution-row" href="bibliography.html?method=${encodeURIComponent(surface)}#searchable-corpus"><span>${esc(surface)}</span><i><b style="width:${Math.max(4, count / maxSurface * 100)}%"></b></i><strong>${count}</strong></a>`).join("")}</div></section>`;
  return `${pageHeader(config)}${figure}<div class="grid"><div class="stat"><b>${catalog.length || DATA.length}</b><span>${language === "zh" ? "篇去重后的研究条目" : "deduplicated research records"}</span></div><div class="stat"><b>${Object.keys(counts).length || 6}</b><span>${language === "zh" ? "类更新对象" : "update surfaces"}</span></div><div class="stat"><b>${(config.ideaCount || 4)}</b><span>${language === "zh" ? "个经过碰撞审查的 CVPR 方向" : "CVPR ideas after collision review"}</span></div></div>${distribution}<div class="framework-grid">${featured}</div>${(config.sections || []).map(renderSection).join("")}`;
}
function renderDynamicResourceIndex(config, mode) {
  const isRepository = mode === "repositories";
  const rows = catalog.filter((p) => isRepository ? Boolean(p.repo) : /benchmark|arena|gym|environment|dataset|evaluation|testbed|sandbox/i.test(`${p.title} ${p.category} ${p.subcategory}`));
  const grouped = rows.reduce((acc, row) => { const key = isRepository ? (row.updateTarget || "other") : (row.category || "Unclassified"); acc[key] = (acc[key] || 0) + 1; return acc; }, {});
  const summary = Object.entries(grouped).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([key, count]) => `<div class="stat"><b>${count}</b><span>${esc(key)}</span></div>`).join("");
  const title = isRepository ? (language === "zh" ? "动态代码仓库索引" : "Live repository index") : (language === "zh" ? "动态基准与环境索引" : "Live benchmark and environment index");
  const intro = isRepository ? (language === "zh" ? "从合并文献语料中自动抽取带公开代码链接的条目。仓库可用不代表完整复现，需结合上方 R0–R4 等级审查。" : "Automatically extracts records with public code links from the merged corpus. Repository availability does not imply full reproduction; use the R0–R4 criteria above.") : (language === "zh" ? "从合并语料中抽取 benchmark、arena、gym、environment、dataset 与 evaluation 相关条目。" : "Extracts benchmark, arena, gym, environment, dataset, and evaluation records from the merged corpus.");
  return `${pageHeader(config)}${(config.sections || []).map(renderSection).join("")}<section class="panel"><h2 id="live-resource-index">${title}</h2><p class="section-intro">${intro}</p><div class="grid resource-index-stats">${summary}</div><div class="resource-list">${rows.length ? rows.map(paperCard).join("") : `<div class="empty">${language === "zh" ? "动态语料尚未加载。" : "The live corpus has not loaded yet."}</div>`}</div></section>`;
}
function bibliographySubset() {
  return catalog.filter((p) => (activeFilter === "all" || p.updateTarget === activeFilter) && (activeYear === "all" || String(p.year) === String(activeYear)) && (activePublicationType === "all" || publicationType(p) === activePublicationType) && (activeSignal === "all" || signalFamily(p) === activeSignal) && (!visionOnly || p.vision));
}
function renderTimelineMap() {
  const years = [...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a - b);
  const surfaces = [...new Set(catalog.map((p) => p.updateTarget || "other"))].sort();
  const maxCount = Math.max(1, ...surfaces.flatMap((surface) => years.map((year) => catalog.filter((p) => (p.updateTarget || "other") === surface && p.year === year).length)));
  return `<section class="panel bibliography-map"><div class="paper-figure-heading"><div><h2 id="method-time-map">${language === "zh" ? "方法与发表时间地图" : "Method and publication-time map"}</h2><p class="section-intro">${language === "zh" ? "每个单元格表示该年份与更新对象下的去重论文数量；点击即可筛选文献库。早期年份主要是 prompt、memory、continual learning 与 agent architecture 的前置工作。" : "Each cell counts deduplicated papers for one year and update surface. Click a cell to filter the bibliography. Early years mainly contain precursors in prompting, memory, continual learning, and agent architecture."}</p></div></div><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="timeline-row"><button class="timeline-label" data-filter="${esc(surface)}">${esc(surface)}</button>${years.map((year) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell" data-filter="${esc(surface)}" data-year="${year}" title="${esc(surface)} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderPublicationTypeMap() {
  const years = [...new Set(catalog.map((p) => p.year).filter(Boolean))].sort((a, b) => a - b);
  const types = ["Published", "Preprint", "Repository", "Blog/Report", "Other"];
  const maxCount = Math.max(1, ...types.flatMap((type) => years.map((year) => catalog.filter((p) => publicationType(p) === type && p.year === year).length)));
  return `<section class="panel bibliography-map"><h2 id="publication-status-map">${language === "zh" ? "发表类型与时间地图" : "Publication type and time map"}</h2><p class="section-intro">${language === "zh" ? "区分正式发表、预印本、仓库和技术博客。自动识别仅用于导航，正式引用仍以论文页面核验为准。" : "Separates published papers, preprints, repositories, and technical reports. Automatic status is for navigation; formal citations still require source verification."}</p><div class="timeline-map" style="--year-count:${years.length}"><div class="timeline-head"><span>${language === "zh" ? "发表类型" : "Publication type"}</span>${years.map((year) => `<button class="timeline-year-btn" data-year="${year}">${year}</button>`).join("")}</div>${types.map((type) => `<div class="timeline-row"><button class="timeline-label publication-label" data-publication="${esc(type)}">${esc(type)}</button>${years.map((year) => { const count = catalog.filter((p) => publicationType(p) === type && p.year === year).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="timeline-cell publication-cell" data-publication="${esc(type)}" data-year="${year}" title="${esc(type)} · ${year}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderSignalMatrix() {
  const surfaces = [...new Set(catalog.map((p) => p.updateTarget || "other"))].sort();
  const signals = [...new Set(catalog.map(signalFamily))].sort();
  const maxCount = Math.max(1, ...surfaces.flatMap((surface) => signals.map((signal) => catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length)));
  return `<section class="panel bibliography-map"><h2 id="surface-signal-map">${language === "zh" ? "更新对象与反馈信号地图" : "Update-surface and feedback-signal map"}</h2><p class="section-intro">${language === "zh" ? "该矩阵把“更新什么”与“凭什么更新”分开；点击单元格可联合筛选。" : "This matrix separates what changes from the evidence that drives the change. Click a cell to apply both filters."}</p><div class="signal-map" style="--signal-count:${signals.length}"><div class="signal-head"><span>${language === "zh" ? "更新对象" : "Update surface"}</span>${signals.map((signal) => `<button class="signal-column" data-signal="${esc(signal)}">${esc(signal)}</button>`).join("")}</div>${surfaces.map((surface) => `<div class="signal-row"><button class="signal-label" data-filter="${esc(surface)}">${esc(surface)}</button>${signals.map((signal) => { const count = catalog.filter((p) => (p.updateTarget || "other") === surface && signalFamily(p) === signal).length; const level = count ? Math.max(.16, count / maxCount) : 0; return `<button class="signal-cell" data-filter="${esc(surface)}" data-signal="${esc(signal)}" title="${esc(surface)} × ${esc(signal)}: ${count}" style="--level:${level}"><b>${count || ""}</b></button>`; }).join("")}</div>`).join("")}</div></section>`;
}
function renderMilestoneTimeline() {
  const milestones = [
    [2022, "Self-generated instructions and early prompt evolution"],
    [2023, "Reflection, verbal reinforcement, open-ended skills, and tool critique"],
    [2024, "Textual gradients, agent graphs, visual tool update, and self-updatable memory"],
    [2025, "Online curriculum RL, workflow search, co-evolving world models, and GUI learning"],
    [2026, "VLM self-play, skill ecosystems, harness evolution, visual memory, and formal verification"],
  ];
  return `<section class="panel"><h2 id="field-timeline">${language === "zh" ? "领域演化时间线" : "Field evolution timeline"}</h2><div class="method-timeline">${milestones.map(([year, en]) => { const count = catalog.filter((p) => p.year === year).length; return `<div class="timeline-item"><div class="timeline-year">${year}</div><div><strong>${language === "zh" ? ({2022:"自生成指令与早期提示词进化",2023:"反思、语言强化、开放式技能与工具批评",2024:"文本梯度、Agent 图、视觉工具更新与可自更新记忆",2025:"在线课程 RL、工作流搜索、共进化世界模型与 GUI 学习",2026:"VLM 自博弈、技能生态、harness 进化、视觉记忆与形式化验证"}[year]) : en}</strong><p>${language === "zh" ? `当前语料库中收录 ${count} 条该年份记录。` : `${count} records from this year are currently indexed.`}</p></div></div>`; }).join("")}</div></section>`;
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
  return `${pageHeader(config)}<div class="integrity-status ${catalog.length > DATA.length ? "pass" : "warn"}"><strong>${catalog.length > DATA.length ? "LIVE" : "SNAPSHOT"}</strong><span>${catalog.length > DATA.length ? (language === "zh" ? "已同步两个综述配套目录，并与人工核验的视觉/CVPR 补充集去重。" : "Live-synced from two survey-maintained catalogs and deduplicated with the curated visual/CVPR supplement.") : (language === "zh" ? "上游同步失败，当前显示人工核验快照。" : "Upstream sync failed; showing the curated snapshot.")}</span></div><div class="grid bibliography-stats"><div class="stat"><b>${catalog.length}</b><span>${language === "zh" ? "篇去重条目" : "deduplicated records"}</span></div><div class="stat"><b>${publishedCount}</b><span>${language === "zh" ? "篇自动识别为正式发表" : "records classified as published"}</span></div><div class="stat"><b>${visionCount}</b><span>${language === "zh" ? "篇视觉/多模态相关" : "vision/multimodal records"}</span></div><div class="stat"><b>${sourceCount}</b><span>${language === "zh" ? "类文献来源" : "source streams"}</span></div></div>${renderTimelineMap()}${renderPublicationTypeMap()}${renderSignalMatrix()}${renderMilestoneTimeline()}<section class="panel"><div class="paper-figure-heading"><div><h2 id="searchable-corpus">${language === "zh" ? "可检索文献语料库" : "Searchable literature corpus"}</h2><p class="section-intro">${language === "zh" ? "筛选结果可直接导出、打印或生成可分享链接。" : "The current filtered set can be exported, printed, or shared through a filter-preserving URL."}</p></div><div class="export-actions"><button class="link-btn export-btn" data-export="json">JSON</button><button class="link-btn export-btn" data-export="csv">CSV</button><button class="link-btn export-btn" data-export="bibtex">BibTeX</button><button class="link-btn" id="copy-filter-link">${language === "zh" ? "复制筛选链接" : "Copy filter link"}</button><button class="link-btn" id="print-page">${language === "zh" ? "打印" : "Print"}</button><button class="link-btn" id="reset-filters">${language === "zh" ? "重置" : "Reset"}</button></div></div><div class="bibliography-controls"><select id="year-filter">${yearOptions}</select><select id="publication-filter">${publicationOptions}</select><select id="signal-filter">${signalOptions}</select><label class="toggle-filter"><input id="vision-filter" type="checkbox" ${visionOnly ? "checked" : ""}> ${language === "zh" ? "仅视觉/多模态" : "Vision/multimodal only"}</label></div><div class="filters">${filters}</div><div id="bibliography-list" class="resource-list"></div></section>`;
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
  const rows = bibliographySubset().filter((p) => !query || [p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal,publicationType(p)].join(" ").toLowerCase().includes(query));
  if (format === "json") return downloadBlob("agent-self-evolution-bibliography.json", JSON.stringify(rows, null, 2), "application/json;charset=utf-8");
  if (format === "bibtex") return downloadBlob("agent-self-evolution-bibliography.bib", rows.map(bibtexEntry).join("\n\n"));
  const fields = ["year","title","venue","category","subcategory","updateTarget","signal","vision","url","repo"];
  const csv = [fields.join(","), ...rows.map((p) => fields.map((field) => `"${String(p[field] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
  downloadBlob("agent-self-evolution-bibliography.csv", csv, "text/csv;charset=utf-8");
}
function paperCard(p) {
  const summary = language === "zh" ? (p.summaryZh || p.summary || "") : (p.summary || p.summaryZh || "");
  const refNo = p.refNo || catalog.indexOf(p) + 1;
  const slug = p.slug || slugify(p.title);
  const type = publicationType(p);
  return `<article class="card reference-card" id="ref-${slug}" data-search="${esc([p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal,type].join(" ").toLowerCase())}"><div class="card-top"><div><h3><a class="ref-number" href="#ref-${slug}">[${refNo}]</a> ${esc(p.title)}</h3><div class="meta">${esc(String(p.year || ""))} · ${esc(p.venue || "Unknown venue")} · ${esc(p.category || "Unclassified")}</div></div><div class="badges"><span class="badge publication-type">${esc(type)}</span><span class="badge ${p.vision ? "vision" : ""}">${p.vision ? "vision/multimodal" : "general"}</span><span class="badge ${p.updateTarget === "model parameters" ? "model" : "scaffold"}">${esc(p.updateTarget || "agent component")}</span><span class="badge">${esc(p.signal || "feedback")}</span></div></div>${summary ? `<p>${esc(summary)}</p>` : ""}<div class="links"><a class="link-btn" href="${esc(p.url)}" target="_blank" rel="noopener">${language === "zh" ? "论文" : "Paper"}</a>${p.repo ? `<a class="link-btn repo" href="${esc(p.repo)}" target="_blank" rel="noopener">${language === "zh" ? "代码" : "Code"}</a>` : ""}<button class="link-btn copy-citation" type="button" data-record="${encodeURIComponent(slug)}">${language === "zh" ? "复制引用" : "Copy citation"}</button><a class="link-btn cite-link" href="bibliography.html?paper=${encodeURIComponent(slug)}#ref-${slug}">${language === "zh" ? "引用定位" : "Reference"}</a></div></article>`;
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
function renderPaperList(query = "") {
  const list = document.getElementById("bibliography-list");
  if (!list) return;
  const q = query.trim().toLowerCase();
  const filtered = bibliographySubset().filter((p) => !q || [p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal,publicationType(p)].join(" ").toLowerCase().includes(q));
  const requested = new URLSearchParams(location.search).get("paper");
  if (requested) {
    const requestedIndex = filtered.findIndex((p) => p.slug === requested);
    if (requestedIndex >= 0) bibliographyLimit = Math.max(bibliographyLimit, requestedIndex + 1);
  }
  const visible = filtered.slice(0, bibliographyLimit);
  const remaining = Math.max(0, filtered.length - visible.length);
  list.innerHTML = filtered.length ? `${visible.map(paperCard).join("")}${remaining ? `<button id="load-more-papers" class="load-more">${language === "zh" ? `继续加载 ${Math.min(80, remaining)} 篇（剩余 ${remaining}）` : `Load ${Math.min(80, remaining)} more (${remaining} remaining)`}</button>` : ""}` : `<div class="empty">${language === "zh" ? "没有匹配条目。" : "No matching records."}</div>`;
  bindPaperCardEvents();
  document.getElementById("load-more-papers")?.addEventListener("click", () => { bibliographyLimit += 80; renderPaperList(query); });
  updateCounter(filtered.length === catalog.length ? (language === "zh" ? ` · 已加载 ${visible.length}` : ` · loaded ${visible.length}`) : (language === "zh" ? ` · 匹配 ${filtered.length}，已加载 ${visible.length}` : ` · ${filtered.length} matches, ${visible.length} loaded`));
  if (requested) requestAnimationFrame(() => document.getElementById(`ref-${requested}`)?.scrollIntoView({ block: "center" }));
}
function renderGlobalSearch(query) {
  let box = document.getElementById("global-search-results");
  if (!query) { box?.remove(); return; }
  const matches = catalog.filter((p) => [p.title,p.category,p.subcategory,p.updateTarget,p.signal].join(" ").toLowerCase().includes(query.toLowerCase())).slice(0, 18);
  if (!box) {
    box = document.createElement("section"); box.id = "global-search-results"; box.className = "panel";
    document.getElementById("dynamic-page")?.prepend(box);
  }
  box.innerHTML = `<h2>${language === "zh" ? "全站论文检索" : "Global paper search"}</h2><div class="resource-list">${matches.length ? matches.map(paperCard).join("") : `<div class="empty">${language === "zh" ? "没有匹配条目。" : "No matching records."}</div>`}</div>`;
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
  ["method","year","publication","signal","vision","paper","q"].forEach((key) => url.searchParams.delete(key));
  if (activeFilter !== "all") url.searchParams.set("method", activeFilter);
  if (activeYear !== "all") url.searchParams.set("year", activeYear);
  if (activePublicationType !== "all") url.searchParams.set("publication", activePublicationType);
  if (activeSignal !== "all") url.searchParams.set("signal", activeSignal);
  if (visionOnly) url.searchParams.set("vision", "1");
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
  const headings = [...document.querySelectorAll("#dynamic-page h2, #dynamic-page h3")].filter((h) => h.id || h.closest(".panel"));
  headings.forEach((h, i) => { if (!h.id) h.id = `${slugify(h.textContent)}-${i + 1}`; });
  container.innerHTML = headings.length ? `<div class="toc-title">${language === "zh" ? "本页目录" : "On this page"}</div><div class="toc-links">${headings.map((h) => `<a class="${h.tagName === "H3" ? "toc-h3" : ""}" href="#${h.id}">${esc(h.textContent)}</a>`).join("")}</div>` : "";
}
function bindPageEvents() {
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
  const socialMeta = {
    "og:title": document.title,
    "og:description": description.content,
    "og:url": canonical.href,
    "og:type": pageId === "bibliography" ? "website" : "article",
    "og:image": "https://agent-evolution.lightrain.asia/knowledge-map.svg",
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
  else if (pageId === "bibliography") root.innerHTML = renderBibliography(config);
  else if (pageId === "repositories") root.innerHTML = renderDynamicResourceIndex(config, "repositories");
  else if (pageId === "datasets-benchmarks") root.innerHTML = renderDynamicResourceIndex(config, "benchmarks");
  else root.innerHTML = `${pageHeader(config)}${(config.sections || []).map(renderSection).join("")}`;
  document.querySelector(".language-toggle")?.replaceChildren(document.createTextNode(language === "en" ? "中文" : "English"));
  bindPageEvents();
  if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
  bindPaperCardEvents();
  hydrateCitations(root);
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

renderShell();
renderPage();
bindSearch();
loadCatalog();
