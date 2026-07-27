# Agent Self-Evolution Observatory

A bilingual, CVPR-oriented research observatory for self-evolving agents.

## Live website

- <https://agent-evolution.lightrain.asia>
- Repository: <https://github.com/lightrain-a/agent-self-evolution-observatory>

## Site structure

The website follows the multi-page framework of the LLM Distillation Lineage Observatory:

- grouped left navigation;
- top-level literature search;
- automatic per-page table of contents;
- persistent English/Chinese switching;
- responsive mobile navigation;
- shared dynamic content and literature data;
- a separate next-paper workspace.

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

### Evaluation and resources

- Evaluation, safety, governance, and rollback
- Coverage and search protocol
- Live bibliography

### CVPR paper workspace

- Problem formulation
- Candidate ideas and collision history
- Benchmark and staged experiments
- Thesis, contribution ladder, and roadmap
- Review status and unresolved objections

## Literature coverage

The live bibliography fetches and parses the survey-maintained
[Awesome Self-Improving Agents](https://github.com/selfimproving-agent/Awesome-Self-Improving-Agents)
list in the browser and deduplicates it with a manually verified visual/CVPR supplement.

The website does **not** claim mathematical completeness. It targets comprehensive
coverage under the explicit inclusion, exclusion, source, and deduplication protocol
documented on `coverage-method.html`.

## Current research direction

The recommended direction is **GroundEvo: Causally-Grounded Multilevel
Self-Evolution for Visual Agents**. The first falsifiable study tests whether visual
agents write spurious lessons from successful and failed trajectories, and whether
active visual re-observation plus minimal environment counterfactual replay reduces
harmful persistent updates.

Alternative directions retained in the workspace:

- EgoShift: embodiment-drift diagnosis and self-calibration;
- ViMEvo: evidence-preserving self-evolving visual memory;
- MetaEvolve-V: failure-conditioned update-surface routing.

## External multi-agent review status

The configured CodexFlow service at `127.0.0.1:4318` is currently unavailable.
The repository therefore distinguishes completed role-separated review passes from
independent external-agent consensus. See `REVIEWER_PROTOCOL.md` and
`review-log.html`.

## Integrity test

Run:

```bash
python3 site_smoke_test.py
```

The test verifies all 19 HTML pages, all navigation/page configurations, JavaScript
syntax, shared scripts, placeholder removal, and the custom-domain CNAME.
