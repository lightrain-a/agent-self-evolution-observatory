# Evidence-Gated Literature-to-Idea Pipeline

This directory turns the observatory from a static survey into a reproducible ICLR-first literature-to-paper-idea decision system, while preserving a secondary CVPR visual-specialization bank.

## Design sources

The architecture combines the strongest reusable components from the previously reviewed research-agent repositories:

| Pipeline component | Reused idea |
|---|---|
| Query planning and perspective expansion | Nova / STORM-style plan-before-search and multi-perspective questions |
| Citation and concept neighborhood | ResearchAgent-style seed, citation, query, claim, dataset, model, and idea graph |
| Structured paper evidence | PaperQA/OpenScholar-style evidence retrieval plus the site's six-part paper schema |
| Candidate generation | AI-Researcher-style high-recall generation with hybrid problem/mechanism/experiment collision filtering |
| Mechanism transfer | Scideator/MOOSE-style purpose–mechanism–evaluation recombination |
| Branch history | Deep-Ideation-style non-destructive idea lineage and review provenance |
| Independent review | CycleResearcher-style role-separated reviewers plus a bounded repair queue |
| Execution gate | AI-Scientist-style P0/P1/P2 registry and result feedback; unrestricted code execution is disabled |

## End-to-end stages

```text
Research scope and assets
  -> perspective/query plan
  -> paper retrieval and citation graph
  -> paper/query/claim/mechanism evidence graph
  -> gap candidates: limitation, contradiction, missing cell, metric mismatch
  -> controlled idea operators
  -> hybrid problem/mechanism/experiment deduplication
  -> idea lineage and branch preservation
  -> seven-dimension ICLR reviewer tournament
  -> blocker-to-operator repair queue
  -> P0/P1/P2 pilot registry and result ingestion
  -> evidence-calibrated advance / revise / hold / stop decision
```

## Data contract

Every idea shown to an advisor must contain:

1. purpose / concrete problem;
2. core idea;
3. why the idea is reasonable;
4. method logic;
5. scientific importance;
6. conditional comparative advantage;
7. nearest-paper evidence and unresolved collision;
8. decisive pilot, strongest baseline, and Go/Stop rule;
9. reviewer findings and required actions;
10. an explicit decision stage rather than a misleading decimal rank.

The canonical schema is implemented in `models.py`. The current static-site portfolio is imported through `export_legacy_portfolio.mjs`, normalized by `pipeline.py`, and exported to `idea-pipeline-data.js` for the browser.

## Run

From the repository root:

```bash
python -m research_pipeline --storage-status
python -m research_pipeline --init-storage
python -m research_pipeline --s2-status
python -m research_pipeline --sync-s2
python -m research_pipeline --iclr-status
python -m research_pipeline --build-iclr-bank
python -m research_pipeline --iclr-audit-status
python -m research_pipeline --build-iclr-audit
python -m research_pipeline --research-system-status
python -m research_pipeline --build-research-system
python -m research_pipeline.automation_cycle --mode manual
python -m research_pipeline --check
python -m research_pipeline
```

Outputs:

- `generated/iclr-low-resource-ideas.json` / `.js`: ICLR-first mechanism bank;
- `generated/iclr-experiment-audit.json` / `.js`: ICLR model/API/training substrate audit;
- `generated/idea-pipeline.json`: historical auditable portfolio artifact;
- `generated/cvpr-low-resource-ideas.json` / `.js`: secondary visual-specialization bank;
- `generated/research-system-state.json` / `.js`: evidence graph, collision analysis, lineage, pilot registry, repair queue, component audit, and health state.

The hand-curated `idea-pipeline-data.js` contains the compact advisor-board configuration and is intentionally not overwritten by the generator.

## Storage policy

The Git checkout contains code, configuration templates, and small browser-consumable snapshots only. Large artifacts are redirected by `.env` to a dedicated data disk:

```text
/home/wyt/code/agent-self-evolution-observatory   # code and small site artifacts
/data/wyt/agent-self-evolution-observatory        # corpora, datasets, PDFs, indexes, caches, runs
```

`StorageSettings` in `config.py` owns this contract. `--init-storage` creates the configured directories and `--storage-status` reports both code-disk and data-disk capacity. The server `.env` also redirects Hugging Face, Torch, and XDG caches to the data disk.

## Provider layer

The Semantic Scholar Academic Graph provider is now connected through `semantic_scholar.py`, with a shared rate limiter, disk cache, retry/backoff, citation/reference expansion, and safe attribution metadata. The API key is read only from the ignored server `.env`. Provider contracts remain swappable without changing the frontend schema:

- `QueryPlanner`: produces topic, citation, failure-mode, mechanism, and cross-domain queries;
- `LiteratureRetriever`: live Semantic Scholar plus future OpenAlex/local PDF indexes;
- `FacetExtractor`: problem, limitation, claim, intuition, mechanism, evidence, assumptions, failure boundary;
- `IdeaSynthesizer`: applies one named operator at a time;
- `NoveltyChecker`: retrieves the nearest work for problem, mechanism, combination, and experiment;
- `Reviewer`: independently returns pass/revise/block plus required evidence;
- `PilotPlanner`: freezes a bounded falsification experiment and resource estimate.

No provider may directly mark an idea as accepted. `research_system.py` composes the evidence graph, collision engine, lineage, pilot registry, and repair queue. `automation_cycle.py` runs a fail-safe daily or weekly cycle and records each step under the data-disk run directory. Only structured pilot results may move a candidate into `pilot-ready` or `selected-ready`, and every move remains traceable to evidence.

## Independent review of all first-round ICLR passes

The seven-dimension programmatic gate currently passes 26 ICLR ideas. These are not treated as externally confirmed. `iclr_external_review.py` sends every pending pass through the existing Code Oracle → signed-in ChatGPT web UI → exact Agent-project route, requires a strict JSON verdict, and persists each completed batch before rebuilding the public bank.

Prepare the five default batches without invoking the browser:

```bash
python3 -m research_pipeline.iclr_external_review --batch-size 5
```

Execute them on the authoritative host that owns the authenticated Oracle/Chrome session:

```bash
./scripts/on-52.sh python3 -m research_pipeline.iclr_external_review --run --batch-size 5
```

The runner refuses other hosts. `generated/iclr-external-reviews.json` is the persistent source of truth, while `generated/iclr-low-resource-ideas.json` merges only stored results into the website. A failed batch cannot erase earlier reviews, and missing reviews remain pending rather than implicitly passing.

## Continuous automation and safety boundary

The daily cycle rebuilds deterministic artifacts without network access. The weekly cycle may refresh Semantic Scholar and request at most two project-scoped web-GPT repair reviews. Both use exclusive locks and keep the previous valid snapshots if one step fails. The repository includes systemd service/timer files under `deploy/systemd/`.

Unrestricted autonomous code execution is intentionally disabled. Controlled experiments may still be run through human-reviewed code or Codex workflows, then written as validated JSON under `runs/pilots/results/`; the pilot registry automatically ingests those results and updates each idea state.

## Decision policy

Legacy scores and ranks remain available for traceability, but they are not the primary interface. The advisor view prioritizes:

- reality of persistent evolution rather than extra inference;
- mechanistic specificity of the evolving object and update operator;
- credit assignment and identifiability;
- stability across multiple evolution rounds;
- out-of-loop generalization across tasks, environments, tools, and model families;
- feedback integrity under independent evidence;
- matched interaction, token, model-call, training, and wall-clock budgets.

A candidate can be held even when it sounds novel, and it can be advanced only with a concrete pilot and Stop condition.
