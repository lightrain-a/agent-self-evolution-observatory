#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
global.window = {};

const storyFiles = [
  "paper-story-blueprint.js",
  ...fs.readdirSync(ROOT)
    .filter((name) => /^paper-story-.*\.js$/.test(name) && !["paper-story-blueprint.js", "paper-story-view.js"].includes(name))
    .sort(),
];
for (const file of storyFiles) {
  const source = fs.readFileSync(path.join(ROOT, file), "utf8");
  vm.runInThisContext(source, { filename: file });
}
const noveltySource = fs.readFileSync(path.join(ROOT, "paper-novelty-audit-data.js"), "utf8");
vm.runInThisContext(noveltySource, { filename: "paper-novelty-audit-data.js" });

const data = global.window.PAPER_STORY_DATA || {};
const blueprint = data.blueprint || {};
const stories = data.papers || {};
const noveltyPapers = global.window.PAPER_NOVELTY_AUDIT?.papers || {};
const registry = JSON.parse(fs.readFileSync(path.join(ROOT, "generated", "paper-registry.json"), "utf8"));
const registryIds = new Set((registry.papers || []).map((row) => String(row.paper_id || "")).filter(Boolean));
const storyIds = new Set(Object.keys(stories));
const errors = [];

const nonempty = (value) => {
  if (typeof value === "string") return value.trim().length > 0;
  if (!value || typeof value !== "object") return false;
  return String(value.zh || value.en || "").trim().length > 0;
};
const localizedBoundary = (row) => nonempty({ zh: row?.boundary_zh, en: row?.boundary_en });
const arrayMin = (story, key, n) => {
  const value = story[key];
  if (!Array.isArray(value) || value.length < n) errors.push(`${story.paper_id || "paper"}:${key} must contain at least ${n} item(s)`);
};

if (String(data.schema_version || "") !== "3.0") errors.push(`PaperStory schema_version must be 3.0, got ${data.schema_version || "missing"}`);
if ((blueprint.steps || []).length !== 15) errors.push(`PaperStory V3 must expose exactly 15 argument steps, got ${(blueprint.steps || []).length}`);
if (!Array.isArray(blueprint.required_fields) || blueprint.required_fields.length < 20) errors.push("PaperStory V3 required_fields contract is missing or too small");

for (const id of registryIds) if (!storyIds.has(id)) errors.push(`PaperRegistry paper has no PaperStory V3 entry:${id}`);
for (const id of storyIds) if (!registryIds.has(id)) errors.push(`PaperStory V3 entry has no current PaperRegistry paper:${id}`);

const archetypeIds = new Set((blueprint.archetypes || []).map((row) => row.id));
for (const [paperId, story] of Object.entries(stories)) {
  story.paper_id = paperId;
  if (!archetypeIds.has(story.paper_archetype)) errors.push(`${paperId}:unknown paper_archetype:${story.paper_archetype || "missing"}`);
  for (const field of blueprint.required_fields || []) {
    const value = story[field];
    const ok = Array.isArray(value) ? value.length > 0 : (typeof value === "object" && !["approaches","gaps","design_requirements","components","mechanism_predictions","alternative_explanations","experiments","mechanism_tests","component_evidence","failure_regimes","chain_of_evidence","outline"].includes(field) ? Object.keys(value || {}).length > 0 : nonempty(value));
    if (!ok) errors.push(`${paperId}:missing required PaperStory V3 field:${field}`);
  }
  for (const field of ["thesis","scene","value","failure_example","missing_scientific_object","research_question","motivation","why_better","generalization","boundary"]) {
    if (!nonempty(story[field])) errors.push(`${paperId}:${field} must contain localized reader-facing text`);
  }
  arrayMin(story, "approaches", 2);
  const closestWorkUrls = new Set();
  const closestWorkTitles = new Set();
  for (const approach of story.approaches || []) {
    if (!String(approach.name || "").trim()) errors.push(`${paperId}:approach missing name`);
    if (!nonempty({ zh: approach.how_zh, en: approach.how_en })) errors.push(`${paperId}:${approach.name || "approach"} missing how-it-works explanation`);
    if (!nonempty({ zh: approach.problem_zh, en: approach.problem_en })) errors.push(`${paperId}:${approach.name || "approach"} missing why-insufficient explanation`);
    const works = approach.closest_work;
    if (!Array.isArray(works) || works.length < 2 || works.length > 4) {
      errors.push(`${paperId}:${approach.name || "approach"}.closest_work must contain 2-4 representative papers`);
      continue;
    }
    const withinApproach = new Set();
    for (const work of works) {
      const title = String(work.title || "").trim();
      const url = String(work.url || "").trim();
      if (!title) errors.push(`${paperId}:${approach.name || "approach"} closest work missing title`);
      if (!/^https:\/\//.test(url)) errors.push(`${paperId}:${approach.name || "approach"}:${title || "closest work"} must use an https source URL`);
      if (!Number.isInteger(work.year) || work.year < 2000 || work.year > 2100) errors.push(`${paperId}:${approach.name || "approach"}:${title || "closest work"} missing valid publication year`);
      if (!String(work.venue || "").trim()) errors.push(`${paperId}:${approach.name || "approach"}:${title || "closest work"} missing venue/status`);
      for (const key of ["what","solves","overlap","missing","boundary"]) {
        if (!nonempty(work[key])) errors.push(`${paperId}:${approach.name || "approach"}:${title || "closest work"} missing ${key}`);
      }
      if (title) closestWorkTitles.add(title);
      if (url) {
        if (withinApproach.has(url)) errors.push(`${paperId}:${approach.name || "approach"} duplicates closest-work URL:${url}`);
        withinApproach.add(url);
        closestWorkUrls.add(url);
      }
    }
  }
  for (const nearest of noveltyPapers[paperId]?.nearest || []) {
    const url = String(nearest.u || "").trim();
    if (url && !closestWorkUrls.has(url)) errors.push(`${paperId}:decision-critical novelty work is missing from approaches[].closest_work:${url}`);
  }
  const noveltyAttack = noveltyPapers[paperId]?.reviewer_attack || {};
  for (const field of ["strongest_attack","surrender","defended_residual","manuscript_action"]) {
    if (!nonempty(noveltyAttack[field])) errors.push(`${paperId}:reviewer novelty attack missing ${field}`);
  }
  if (!String(noveltyAttack.verdict || "").trim()) errors.push(`${paperId}:reviewer novelty attack missing verdict`);
  if (!Array.isArray(noveltyAttack.pressure_titles) || noveltyAttack.pressure_titles.length < 2) {
    errors.push(`${paperId}:reviewer novelty attack must cite at least two pressure works`);
  } else {
    for (const title of noveltyAttack.pressure_titles) if (!closestWorkTitles.has(String(title))) errors.push(`${paperId}:reviewer novelty pressure work is missing from approaches[].closest_work:${title}`);
  }
  arrayMin(story, "gaps", 2);
  arrayMin(story, "design_requirements", 2);
  arrayMin(story, "components", 2);
  arrayMin(story, "mechanism_predictions", 1);
  arrayMin(story, "alternative_explanations", 1);
  arrayMin(story, "experiments", 2);
  arrayMin(story, "mechanism_tests", 1);
  arrayMin(story, "component_evidence", 1);
  arrayMin(story, "failure_regimes", 1);
  arrayMin(story, "chain_of_evidence", 1);
  arrayMin(story, "outline", 5);

  const gapIds = new Set((story.gaps || []).map((row) => String(row.id || "")).filter(Boolean));
  for (const component of story.components || []) {
    const refs = String(component.solves || "").split(/[\/,;+\s]+/).filter((x) => /^G\d+$/.test(x));
    if (!refs.length) errors.push(`${paperId}:component has no Gap reference:${component.name || "unnamed"}`);
    for (const ref of refs) if (!gapIds.has(ref)) errors.push(`${paperId}:component ${component.name || "unnamed"} references unknown gap:${ref}`);
  }
  for (const prediction of story.mechanism_predictions || []) {
    if (!nonempty({ zh: prediction.prediction_zh, en: prediction.prediction_en }) || !String(prediction.tested_by || "").trim()) errors.push(`${paperId}:mechanism prediction must include prediction text and tested_by`);
  }
  for (const alt of story.alternative_explanations || []) {
    if (!String(alt.name || "").trim() || !nonempty({ zh: alt.control_zh, en: alt.control_en })) errors.push(`${paperId}:alternative explanation must include name and control`);
  }
  const ec = story.evaluation_contract || {};
  for (const pair of [["strongest_baseline_zh","strongest_baseline_en"],["held_fixed_zh","held_fixed_en"],["unit_zh","unit_en"],["success_rule_zh","success_rule_en"]]) {
    if (!nonempty({ zh: ec[pair[0]], en: ec[pair[1]] })) errors.push(`${paperId}:evaluation_contract missing ${pair[0].replace("_zh","")}`);
  }
  for (const row of story.chain_of_evidence || []) {
    if (!String(row.claim || "").trim() || !String(row.evidence || "").trim() || !localizedBoundary(row)) errors.push(`${paperId}:chain_of_evidence rows require claim, evidence, and boundary`);
  }
}

if (errors.length) {
  console.error("PaperStory V3 contract validation FAILED");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log(`PASS PaperStory V3: ${registryIds.size} PaperRegistry papers, ${blueprint.steps.length} argument steps, ${blueprint.required_fields.length} required fields`);
