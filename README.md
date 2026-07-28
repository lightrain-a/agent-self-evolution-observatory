# Agent Self-Evolution Observatory

A bilingual, CVPR-oriented research observatory for self-evolving agents.

- Website: <https://agent-evolution.lightrain.asia>
- Repository: <https://github.com/lightrain-a/agent-self-evolution-observatory>

## Information architecture

The site follows the same research-observatory framework as the LLM Distillation Lineage Observatory:

- grouped sticky sidebar navigation;
- global literature search;
- automatic per-page table of contents;
- persistent English/Chinese switching;
- responsive mobile navigation;
- linked numbered references;
- a separate next-paper workspace;
- explicit QA and coverage protocols.

The current site contains 22 main pages.

### Foundations

- Definitions and history
- Four-axis knowledge map and taxonomy

### Evolution mechanisms

- Foundation-model parameter improvement
- Prompt and context evolution
- Memory evolution
- Tool and skill evolution
- Workflow and architecture evolution

### Visual and interactive agents

- Visual and multimodal agents
- GUI and web agents
- Embodied agents and world models

### Evaluation and reliability

- Evaluation, safety, governance, and rollback
- Datasets, environments, and longitudinal benchmarks
- Coverage and search protocol

### Resources

- Repositories and reproducible systems
- Live bibliography
- Long-term research agenda

### CVPR paper workspace

- Problem formulation
- Candidate ideas and collision history
- Benchmark and staged experiments
- Thesis, contribution ladder, and roadmap
- Review status and unresolved objections

## Literature corpus

The bibliography synchronizes two complementary survey-maintained catalogs in the browser:

1. `selfimproving-agent/Awesome-Self-Improving-Agents`
2. `FrontisAI/Awesome-Self-Improving-Agents`

It merges and normalizes these records with a manually verified visual/CVPR core set. The live interface includes:

- method × publication-year heatmap;
- publication-type × year heatmap;
- update-surface × feedback-signal matrix;
- year, method, feedback, publication status, and vision filters;
- filter-preserving share links and paginated rendering;
- global full-text search;
- linked numbered references from topic pages;
- JSON, CSV, and generic BibTeX export;
- per-record citation copying and print layout.

The site does **not** claim literal mathematical completeness. It targets comprehensive and auditable coverage under the inclusion, exclusion, source, deduplication, and publication-status protocol documented on `coverage-method.html`.

## Current research direction

The broader roadmap is **GroundEvo: Causally-Grounded Multilevel Self-Evolution for Visual Agents**. The frozen first-paper scope is **GroundEvo-Admission: Visual Causal Lesson Admission**.

The first falsifiable study asks whether visual agents admit spurious lessons from successful and failed trajectories, and whether active visual re-observation plus minimal environment counterfactual replay improves persistent-memory admission, lowers harmful commits, and preserves future-task gain under matched cost.

Retained alternatives:

- **EgoShift:** embodiment-drift diagnosis and self-calibration;
- **ViMEvo:** evidence-preserving self-evolving visual memory;
- **MetaEvolve-V:** failure-conditioned update-surface routing, retained as a later GroundEvo extension.

## External-agent review status

The configured CodexFlow service at `127.0.0.1:4318` and the installed Claude CLI are currently unavailable because the service or authentication is invalid. The repository therefore distinguishes completed role-separated audits—including the 2026 frontier-collision pass that froze GroundEvo-Admission—from independent external-agent consensus. See `REVIEWER_PROTOCOL.md` and `review-log.html`.

## Quality assurance

Run static site integrity checks:

```bash
python3 site_smoke_test.py
```

Run the online literature and citation audit:

```bash
python3 catalog_audit.py
```

Run the real-browser interaction test when Firefox and geckodriver are available:

```bash
python3 browser_smoke_test.py
```

The checks cover:

- all 22 main HTML pages;
- navigation targets and content configurations;
- JavaScript syntax;
- sitemap, CNAME, favicon, manifest, robots, and 404 resources;
- upstream catalog counts and deduplication;
- missing URLs and unresolved topic-page citations;
- dynamic catalog loading, three bibliography maps, filters, URL state, and pagination;
- knowledge-map rendering, linked resource pages, and mobile navigation.

## Deployment

GitHub Pages publishes the `main` branch with the custom domain stored in `CNAME`:

```text
agent-evolution.lightrain.asia
```
