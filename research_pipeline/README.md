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

The seven-dimension programmatic gate passes 26 ICLR ideas. On 2026-08-06, the authoritative host completed the Code Oracle → signed-in ChatGPT web UI → exact Agent-project audit for all 26. The external distribution is 4 PASS, 10 REVISE, and 12 BLOCK. The bank now orders ideas by R2 verdict while preserving the original R1 rank and priority.

Prepare the five default batches without invoking the browser:

```bash
python3 -m research_pipeline.iclr_external_review --batch-size 5
```

Execute them on the authoritative host that owns the authenticated Oracle/Chrome session:

```bash
bash scripts/on-52.sh python3 -m research_pipeline.iclr_external_review --run --batch-size 5 --max-attempts 3
```

The runner refuses other hosts. `generated/iclr-external-reviews.json` is the persistent source of truth, while `generated/iclr-low-resource-ideas.json` merges only stored results into the website. A failed or malformed response is retried without erasing earlier reviews. The completed store reports 26 reviewed, zero pending, and zero failed final batches. R2 PASS does not imply selected-ready: every surviving direction still requires P0/P1/P2 evidence.

## Internet-inspired expansion pipeline

`machine_school_idea_factory.py` translates six informal “machine school” metaphors into scientific variables rather than preserving the joke labels as paper titles. It generates 24 candidates and applies internal collision, identifiability, stability, transfer, budget, and falsification gates. The internal result is 11 PASS, 7 REVISE/MERGE, and 6 REJECT.

`machine_school_external_review.py` sends the 11 internal passes through the same Code Oracle → signed-in Agent-project ChatGPT route in three resumable batches. The completed external distribution is 1 PASS, 7 REVISE, and 3 BLOCK. `Regression-Probe Half-Life` is the sole `pilot-now` direction; seven explicit repair-first alternatives remain in `teacher_shortlist` for senior/teacher selection.

Persistent artifacts:

- `generated/machine-school-inspired-ideas.json/js`: all 24 candidates, internal decisions, external verdicts, final statuses, and the teacher shortlist;
- `generated/machine-school-external-reviews.json`: full official-source review evidence and required actions;
- `/data/wyt/agent-self-evolution-observatory/runs/reviews/machine-school-web-gpt/`: frozen prompts and response artifacts.

The weekly automation cycle rebuilds and publishes the inspired bank. Missing or malformed external responses remain pending and never count as passes.

## Solution-first method discovery and reviewer repair

`idea_discovery_v3.py` separates problem discovery from method invention. It records seven official GitHub system patterns, fourteen named idea operators, nine workflow stages, and five mechanism gates. A solution child must specify a changed assumption, exact persistent update surface, learning signal, independent ground truth, strongest irreducibility baseline, decisive pilot, and Stop rule.

The first v3 pool contains 14 children. Ten passed internal screening and were reviewed by `solution_first_external_review.py`; the external result is 0 PASS, 6 REVISE, and 4 BLOCK. `idea_discovery_v31.py` then applies the actual bilingual reviewer vectors to only those six REVISE children. Its six repaired algorithms were audited by `solution_first_v31_external_review.py`; the result is 0 PASS, 2 REVISE, and 4 BLOCK. The blocked children are not regenerated under new names.

The review outcome introduced a mechanism-irreducibility gate before external review. It blocks generic predictors, gates, contextual bandits, offline-RL controllers, and rule learners when a capacity-matched standard method can consume the same logs and reproduce the proposed effect. It also rejects circular verifier supervision, audit-only outputs that do not alter frozen future behavior, and calibration guarantees with insufficient independent units.

Artifacts:

- `generated/idea-discovery-v3.json/js` and `generated/idea-discovery-v3-external-reviews.json`;
- `generated/idea-discovery-v31.json/js` and `generated/idea-discovery-v31-external-reviews.json`;
- `/data/wyt/agent-self-evolution-observatory/runs/reviews/solution-first-v3-web-gpt/`;
- `/data/wyt/agent-self-evolution-observatory/runs/reviews/solution-first-v31-web-gpt/`.

Neither internal shortlist nor external REVISE changes the four formal R2 PASS ideas in the main ICLR bank.

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
