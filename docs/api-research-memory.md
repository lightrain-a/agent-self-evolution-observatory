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

   It tracks runs, artifacts, API calls, call events, research objects, and
   lineage edges. Identical re-import is idempotent. A reused run ID with a
   different manifest fails closed.

3. Research Memory Graph projection:

   Only bounded preflight candidates are projected. Every projected row remains
   `downstream_authorization_blocked=true` and
   `scientific_authority=false`.

## Authority boundary

The database cannot authorize Problem Gate, paper or method design, experiment
execution, P0, GPU use, claim mutation, or scientific closure. Transport, parser,
orchestration, and provenance failures have `belief_authority=false`.

## Commands

```bash
python -m research_pipeline.api_research_memory_import import-run \
  --run-root generated/research-data/runs/<run-id>
python -m research_pipeline.api_research_memory_import status
python -m research_pipeline.api_research_memory_import lint
```

For canonical shadow runs, `problem_search_stage_runner` records raw provider
output automatically at the archive-before-parse boundary. Completed-run import
enriches it with model identity, request fingerprint, prompt hash, parse
disposition, structured artifacts, candidates, and lineage.
