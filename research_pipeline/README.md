# Evidence-Gated Literature-to-Idea Pipeline

This directory turns the observatory from a static survey into a reproducible literature-to-paper-idea decision system.

## Design sources

The architecture combines the strongest reusable components from the previously reviewed research-agent repositories:

| Pipeline component | Reused idea |
|---|---|
| Query planning and perspective expansion | Nova / STORM-style plan-before-search and multi-perspective questions |
| Citation and concept neighborhood | ResearchAgent-style seed, citation, and entity expansion |
| Structured paper evidence | PaperQA/OpenScholar-style evidence retrieval plus the site's six-part paper schema |
| Candidate generation | AI-Researcher-style high-recall generation and deduplication |
| Mechanism transfer | Scideator/MOOSE-style purpose–mechanism–evaluation recombination |
| Branch history | Deep-Ideation-style idea stack rather than destructive rewriting |
| Independent review | CycleResearcher-style role-separated reviewers |
| Execution gate | AI-Scientist-style bounded experiment branch, but only after a falsifiable pilot is fixed |

## End-to-end stages

```text
Research scope and assets
  -> perspective/query plan
  -> paper retrieval and citation graph
  -> six-part paper cards + claim/evidence records
  -> landscape matrices and evolution chains
  -> gap candidates: limitation, contradiction, missing cell, metric mismatch
  -> eight controlled idea operators
  -> semantic deduplication
  -> four-way novelty collision search
  -> independent reviewer tournament
  -> minimal falsification pilot
  -> advisor shortlist / hold / stop decision
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
python -m research_pipeline --check
python -m research_pipeline
```

Outputs:

- `generated/idea-pipeline.json`: auditable backend artifact;
- `generated/idea-pipeline-snapshot.js`: full browser-readable audit snapshot.

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

No provider may directly mark an idea as accepted. Only the gate engine can move a candidate into `pilot-ready` or `selected`, and every move must be traceable to evidence.

## Decision policy

Legacy scores and ranks remain available for traceability, but they are not the primary interface. The advisor view prioritizes:

- visual necessity for CVPR;
- importance of the failure;
- exact novelty evidence;
- mechanism identifiability;
- one-table experimental proof;
- feasibility with current assets;
- value of a negative pilot result.

A candidate can be held even when it sounds novel, and it can be advanced only with a concrete pilot and Stop condition.
