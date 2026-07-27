const DATA = window.SUPPLEMENTAL_PAPERS || [];
const PAGES = window.PAGE_CONTENT || {};
const NAV_GROUPS = window.NAV_GROUPS || [];
const AWESOME_URL = "https://raw.githubusercontent.com/selfimproving-agent/Awesome-Self-Improving-Agents/main/README.md";
const pageId = document.body.dataset.page || "home";
let language = localStorage.getItem("agent-evolution-language") || "en";
let catalog = [];
let activeFilter = "all";

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

function renderShell() {
  document.body.insertAdjacentHTML("afterbegin", `<a class="skip-link" href="#main-content">Skip to content</a><button class="sidebar-overlay" aria-label="Close navigation" hidden></button>`);
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
  if (topbar && !topbar.querySelector(".language-toggle")) {
    topbar.insertAdjacentHTML("beforeend", `<button class="language-toggle" type="button">${language === "en" ? "中文" : "English"}</button>`);
  }
  document.querySelector(".language-toggle")?.addEventListener("click", () => setLanguage(language === "en" ? "zh" : "en"));
  const mobileToggle = document.querySelector(".mobile-toggle");
  const overlay = document.querySelector(".sidebar-overlay");
  const close = () => { sidebar.classList.remove("open"); overlay.hidden = true; };
  mobileToggle?.addEventListener("click", () => { sidebar.classList.add("open"); overlay.hidden = false; });
  sidebar.querySelector(".sidebar-close")?.addEventListener("click", close);
  overlay?.addEventListener("click", close);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
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
async function loadCatalog() {
  let upstream = [];
  try {
    const response = await fetch(AWESOME_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    upstream = parseAwesomeMarkdown(await response.text());
  } catch (error) {
    console.warn("Live literature synchronization failed; using curated snapshot.", error);
  }
  catalog = mergeCatalog(upstream, DATA);
  updateCounter();
  if (pageId === "bibliography" || pageId === "home") renderPage();
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
  return `<section class="panel topic-section"><h2 id="${id}">${title}</h2>${section.intro ? `<p class="section-intro">${textOf(section.intro)}</p>` : ""}<div class="section-body">${textOf(section.body)}</div></section>`;
}
function renderHome(config) {
  const counts = {};
  catalog.forEach((p) => counts[p.updateTarget || "other"] = (counts[p.updateTarget || "other"] || 0) + 1);
  const featured = (config.featured || []).map((item) => `<a class="framework-card ${item.paper ? "paper-card" : ""}" href="${item.href}"><b>${textOf(item.title)}</b><span>${textOf(item.desc)}</span></a>`).join("");
  return `${pageHeader(config)}<div class="grid"><div class="stat"><b>${catalog.length || DATA.length}</b><span>${language === "zh" ? "篇去重后的研究条目" : "deduplicated research records"}</span></div><div class="stat"><b>${Object.keys(counts).length || 6}</b><span>${language === "zh" ? "类更新对象" : "update surfaces"}</span></div><div class="stat"><b>${(config.ideaCount || 4)}</b><span>${language === "zh" ? "个经过碰撞审查的 CVPR 方向" : "CVPR ideas after collision review"}</span></div></div><div class="framework-grid">${featured}</div>${(config.sections || []).map(renderSection).join("")}`;
}
function renderBibliography(config) {
  const categories = ["all", ...new Set(catalog.map((p) => p.updateTarget || "other"))];
  const filters = categories.map((category) => `<button class="filter-btn ${activeFilter === category ? "active" : ""}" data-filter="${esc(category)}">${esc(category === "all" ? (language === "zh" ? "全部" : "All") : category)}</button>`).join("");
  return `${pageHeader(config)}<div class="integrity-status ${catalog.length > DATA.length ? "pass" : "warn"}"><strong>${catalog.length > DATA.length ? "LIVE" : "SNAPSHOT"}</strong><span>${catalog.length > DATA.length ? (language === "zh" ? "已从配套综述的 Awesome 列表实时同步并与视觉补充集去重。" : "Live-synced from the survey's Awesome list and deduplicated with the visual supplement.") : (language === "zh" ? "上游同步失败，当前显示人工核验快照。" : "Upstream sync failed; showing the curated snapshot.")}</span></div><div class="filters">${filters}</div><div id="bibliography-list" class="resource-list"></div>`;
}
function paperCard(p, index) {
  const summary = language === "zh" ? (p.summaryZh || p.summary || "") : (p.summary || p.summaryZh || "");
  return `<article class="card" data-search="${esc([p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal].join(" ").toLowerCase())}"><div class="card-top"><div><h3><span class="ref-number">[${index + 1}]</span> ${esc(p.title)}</h3><div class="meta">${esc(String(p.year || ""))} · ${esc(p.venue || "Unknown venue")}</div></div><div class="badges"><span class="badge ${p.vision ? "vision" : ""}">${p.vision ? "vision/multimodal" : "general"}</span><span class="badge ${p.updateTarget === "model parameters" ? "model" : "scaffold"}">${esc(p.updateTarget || "agent component")}</span><span class="badge">${esc(p.signal || "feedback")}</span></div></div>${summary ? `<p>${esc(summary)}</p>` : ""}<div class="links"><a class="link-btn" href="${esc(p.url)}" target="_blank" rel="noopener">Paper</a>${p.repo ? `<a class="link-btn repo" href="${esc(p.repo)}" target="_blank" rel="noopener">Code</a>` : ""}</div></article>`;
}
function renderPaperList(query = "") {
  const list = document.getElementById("bibliography-list");
  if (!list) return;
  const q = query.trim().toLowerCase();
  const filtered = catalog.filter((p) => (activeFilter === "all" || p.updateTarget === activeFilter) && (!q || [p.title,p.venue,p.category,p.subcategory,p.updateTarget,p.signal].join(" ").toLowerCase().includes(q)));
  list.innerHTML = filtered.length ? filtered.map(paperCard).join("") : `<div class="empty">${language === "zh" ? "没有匹配条目。" : "No matching records."}</div>`;
  updateCounter(filtered.length === catalog.length ? "" : (language === "zh" ? ` · 显示 ${filtered.length}` : ` · showing ${filtered.length}`));
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
}
function buildToc() {
  const container = document.getElementById("page-toc");
  if (!container) return;
  const headings = [...document.querySelectorAll("#dynamic-page h2, #dynamic-page h3")].filter((h) => h.id || h.closest(".panel"));
  headings.forEach((h, i) => { if (!h.id) h.id = `${slugify(h.textContent)}-${i + 1}`; });
  container.innerHTML = headings.length ? `<div class="toc-title">${language === "zh" ? "本页目录" : "On this page"}</div><div class="toc-links">${headings.map((h) => `<a class="${h.tagName === "H3" ? "toc-h3" : ""}" href="#${h.id}">${esc(h.textContent)}</a>`).join("")}</div>` : "";
}
function bindPageEvents() {
  document.querySelectorAll(".filter-btn").forEach((button) => button.addEventListener("click", () => {
    activeFilter = button.dataset.filter || "all";
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.toggle("active", b === button));
    renderPaperList(document.getElementById("site-search")?.value || "");
  }));
}
function renderPage() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  const config = PAGES[pageId] || PAGES.home;
  const root = document.getElementById("dynamic-page");
  if (!root || !config) return;
  if (pageId === "home") root.innerHTML = renderHome(config);
  else if (pageId === "bibliography") root.innerHTML = renderBibliography(config);
  else root.innerHTML = `${pageHeader(config)}${(config.sections || []).map(renderSection).join("")}`;
  document.querySelector(".language-toggle")?.replaceChildren(document.createTextNode(language === "en" ? "中文" : "English"));
  bindPageEvents();
  if (pageId === "bibliography") renderPaperList(document.getElementById("site-search")?.value || "");
  buildToc();
}

function bindSearch() {
  const input = document.getElementById("site-search");
  if (!input) return;
  input.addEventListener("input", () => {
    const query = input.value.trim();
    if (pageId === "bibliography") renderPaperList(query);
    else renderGlobalSearch(query);
  });
}

renderShell();
renderPage();
bindSearch();
loadCatalog();
