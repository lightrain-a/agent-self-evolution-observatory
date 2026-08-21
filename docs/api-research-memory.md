# Persistent API Research Memory

This is a private, append-only provenance and retrieval layer. It does not
replace the Claim Ledger, scientific adjudication, or Research Memory Graph 2.1.

## Design references

- [The AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2) checkpoints
  its tree-search journal and stores timestamped experiment logs. Its public issue
  tracker shows why delaying summaries until the end makes interrupted runs hard
  to resume. Provider bytes are therefore archived before parsing and a call event
  is created immediately.
- [AI Co-Scientist](https://doi.org/10.1038/s41586-026-10644-y) uses asynchronous
  generate-debate-evolve cycles and tournament evolution. Run, call, object, and
  parent-child identities are therefore stored separately.
- [EvoScientist](https://arxiv.org/abs/2603.08127) separates ideation memory from
  experimentation memory and retains useful strategies and unsuccessful
  directions. Execution and parse failures are stored alongside successful
  candidates with zero belief authority.
- [ARIS](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep) writes
  papers, ideas, experiments, claims, and failed ideas back to persistent memory.
  This implementation exposes a read-only candidate projection to Research Memory
  Graph 2.1 while keeping raw model output outside the graph.

## Storage layers

1. Content-addressed raw and structured artifacts:

   `<persistent-root>/artifacts/api-research-memory/sha256/<prefix>/<sha256>`

2. SQLite WAL event log and query index:

   `<persistent-root>/indexes/api-research-memory.sqlite3`

   It tracks runs, artifacts, API calls, call events, research objects, lineage
   edges, deterministic exact-contract scientific identities, memory queries,
   and memory-consumption receipts. Identical re-import is idempotent. A reused
   run ID with a different manifest fails closed.

3. Research Memory Graph projection:

   Only bounded preflight candidates are projected. API candidate IDs are
   namespaced by source run so run-local ordinals cannot collide. Deterministic
   exact-contract signatures are projected only as grouping nodes; they never
   merge scientific authority. Every projected row remains
   `downstream_authorization_blocked=true` and `scientific_authority=false`.

## Research Memory 2.2 consumer loop

Canonical search stages can retrieve prior API research objects before provider
calls. The current consumers are `expand`, `evolve`, `formulate`, and semantic
`review`. Each call freezes a content-addressed query pack and records which
memory objects were actually consumed by the prompt. Replays do not inject new
memory.

Successful JSON parsing is also written back immediately: the parsed payload is
content-addressed, the call moves from `parse_status=PENDING` to `PARSED`, and a
`PARSE_COMPLETED` event is appended before any completed-run import. Validated
callers may additionally persist typed zero-authority research objects at this
boundary (for example, an independent evidence-review object). Completed-run
import is per-object idempotent so interruption-time writeback and later full
import can safely converge instead of conflicting.

Supported query purposes are `IDEA_DISCOVERY`, `FORMULATION`,
`SEMANTIC_REVIEW`, `EXPERIMENT_DESIGN`, and `PAPER_META_REVIEW`. The production
default remains `relevant` (Top-K relevance). `random` and `none` are evaluation
controls. `portfolio`, `relevant_neutral`, and `relevant_escape` are explicit
IDEA_DISCOVERY-only experimental variants and are never selected by the default
path.

The default is evidence-driven rather than assumed. Three matched Research
Memory 2.3 replicates (four memories / 2406 memory characters per arm) produced
criterion-panel clear counts of 10/18 for the four-role basin-aware portfolio,
16/18 for Top-K relevant, and 14/18 for random. The portfolio result was also
substantially less stable across replicates (6/6, 1/6, 3/6) than Top-K relevant
(5/6, 6/6, 5/6). This is a search-policy evaluation only, not scientific or
publication-success evidence.

A subsequent framing-only 2.4 test kept the exact same Top-K object IDs,
scientific signatures, per-item framing-prefix length, visible source bytes, and
total 2406 memory characters fixed. Across two corrected replicates, neutral
framing and explicit `CLOSED_BASIN: escape-not-rephrase` framing both cleared
11/12 candidates. Therefore always-on escape framing is not enabled. Closed-basin
classification remains audit/search-control metadata that can be used in future
controlled experiments without changing scientific thresholds.

A canonical stage run fails closed if its canonical API memory database is
missing. Noncanonical scratch/test runs do not attach to canonical API memory by
default; an explicit optional-memory switch is required even to read it. This
prevents tests and local development from silently adding query/consumption
bookkeeping to the durable history.

If a development defect ever creates a query-only run stub in canonical memory,
correction is append-only: `run_invalidations` hides the stub from active
retrieval/state while retaining the original rows for audit. The maintenance
path refuses to invalidate any run that has provider calls, research objects, or
persisted artifacts.

For A/B/C evaluation, `relevant` and `random` are the primary causal pair and
are frozen to the same realized memory-item count under the same character cap.
`none` is intentionally empty and measures total memory utility; it must not be
reported as token-matched. Provider prompt-token counts are part of the required
arm-level telemetry.

## Authority boundary

The database cannot authorize Problem Gate, paper or method design, experiment
execution, P0, GPU use, claim mutation, or scientific closure. Transport, parser,
orchestration, and provenance failures have `belief_authority=false`.

Substrate auditing also remains separate from scientific truth. A discovered
execution-protocol contradiction may return exactly once through
`PROTOCOL_REPAIR_REQUIRED` to bounded evidence design while compiler-owned
prediction/baseline/falsifier fields stay frozen. It cannot be converted into a
scientific negative or used to relax experiment budgets.

## Commands

```bash
python -m research_pipeline.api_research_memory_import import-run \
  --run-root generated/research-data/runs/<run-id>
python -m research_pipeline.api_research_memory_import status
python -m research_pipeline.api_research_memory_import lint

python -m research_pipeline.api_memory_ablation \
  --run-id-prefix memory-ablation-r1 \
  --purpose IDEA_DISCOVERY \
  --stage expand \
  --context-json '{"topic":"persistent agent self-evolution"}'
```

For canonical shadow runs, `problem_search_stage_runner` records raw provider
output automatically at the archive-before-parse boundary. Completed-run import
enriches it with model identity, request fingerprint, prompt hash, parse
disposition, structured artifacts, candidates, and lineage.
