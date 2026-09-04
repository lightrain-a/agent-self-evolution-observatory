# G1 / Agent Safety R9 — ICLR 2027 manuscript workspace

## Active scientific object — 2026-09-04

**Auditing the refusal-to-action boundary under benign workflow accumulation in persistent browser agents.**

Current status: **PRECONFIRMATORY / SUBMISSION HOLD**.

The next paper identity is prospectively adjudicated by a capability-qualified Qwen3.5-397B-A17B experiment. No new safety outcome exists yet.

Read first:

1. `MAINLINE_BRIEF.md` — active scientific object, identification design, claim ladder, and paper-identity rule.
2. `SKILLZIP_PRECONFIRMATORY_MANUSCRIPT_R1.md` — paper architecture derived from the SkillZip / SkillZip Pro methodology and writing lessons.
3. `main_skillzip_preconfirmatory.tex` — compilable preconfirmatory manuscript skeleton with explicit outcome placeholders; this is the writing iteration target before the prospective result exists.
4. `main.tex` — preserved ERTA-centered historical manuscript draft; **not the active story source of truth** until rewritten after the prospective adjudication.

## Why the workspace has multiple historical stories

G1 evolved through three manuscript identities:

1. **Static-pass / first-violation story** — a current non-violation panel did not certify later HarmBench outcomes.
2. **Controlled same-schedule story** — Updated workflow produced more HarmBench event branches than the matched Frozen workflow in the finite historical design.
3. **ERTA / evaluator-relative story** — DeepSeek changed the historical arm ordering, so the manuscript pivoted to evaluator robustness.

A retrospective execution audit then found that 103/108 historical future episodes hit the four-step truncation ceiling, 0/108 normally terminated, and 0/108 had a listener-confirmed external effect. Therefore the historical mechanism and evaluator-reversal results remain useful discovery evidence but cannot by themselves determine the final paper identity.

The 2026-09-04 SkillZip iteration removes this split-brain state by fixing one prospective scientific object before further safety outcomes.

## Active identification design

Primary treatment contrast:

- **Updated** — prospectively frozen benign workflow units accumulate over longitudinal exposure steps.
- **Frozen** — the step-0 workflow remains fixed.

Matched across arms:

- initial state;
- future task schedule;
- seed structure;
- BrowserART/BrowserGym substrate;
- AXTree/BID action interface;
- execution budget.

Primary endpoint:

- **R1 — first harmful-task-directed action initiation**, implemented as a prospectively frozen task-specific programmatic predicate.

Behavioral decomposition:

- R0 — immediate refusal / safe handling;
- R1 — task-directed action initiation;
- R2 — partial execution depth;
- R3 — verified external effect.

Semantic evaluators (HarmBench, DeepSeek, blinded human labels) are a secondary measurement-robustness layer rather than the primary source of behavioral truth.

## Capability gate before any new safety trajectory

The exact Qwen3.5-397B-A17B + AWM + BrowserART/BrowserGym stack must first pass the official BrowserART ten-task benign panel under the benchmark-aligned ten-step budget.

Required gate: **10/10 PASS**.

The historical four-step setting is analyzed only as a prefix diagnostic of the same benign trajectories. Failure of the capability gate stops the safety experiment and is classified as a substrate/execution failure, not a safety result.

Current execution implementation lives on:

`research/g1-qwen397-capability-requal-20260902`

with the 2026-09-04 paper branch consuming its frozen outcomes only after closeout.

## Historical discovery evidence

Historical Qwen3-8B/AWM R9 remains immutable:

- HarmBench future branch events: Updated/Frozen/NullMemory = 8/4/0.
- DeepSeek on the same trajectories: 5/5/8.
- 103/108 future episodes hit the four-step truncation ceiling.
- 0/108 normally terminated.
- 0/108 listener-confirmed external effects.

These results motivate the new experiment; they do not constitute the new confirmatory mechanism result.

## Prospective paper-identity rule

- capability FAIL -> no safety run; substrate diagnosis only;
- capability PASS + preregistered Updated-vs-Frozen R1 effect with coherent R0/R2/R3 -> narrow self-evolution paper;
- capability PASS + no R1 effect but robust evaluator reversal on complete/objectively anchored trajectories -> evaluation/measurement paper;
- neither effect survives -> STOP/MERGE G1.

This rule must not be changed after observing safety outcomes.

## Paper-writing discipline

The narrative spine is:

**problem -> scientific object -> identification -> prospective evidence -> behavioral decomposition -> measurement robustness -> exact prior-work boundary -> limitations.**

Hashes, provider transport, execution recovery, and authorization bookkeeping remain in machine-readable artifacts / appendix unless they alter scientific interpretation.

The main normal-setting table must directly test the core advantage; secondary experiments only explain, diagnose, or bound it.

## Historical evidence artifacts retained

- `generated/agent-safety-r9-future-evidence-adjudication-20260820.json`
- `generated/agent-safety-r9-controlled-longitudinal-adjudication-20260821.json`
- `generated/agent-safety-r9-controlled-longitudinal-scientific-review-20260821.json`
- `generated/agent-safety-r9-controlled-paper-claim-table-20260821.json`
- `generated/agent-safety-r9-controlled-memory-graph21-inputs-20260821.json`
- human semantic calibration preregistration / packet artifacts from 2026-08-31.

These artifacts are preserved; none is relabeled as prospective confirmatory evidence.

## Build status

`main.tex/main.pdf` currently reproduce the ERTA-centered historical draft. Do not treat successful compilation of that file as approval of the active 2026-09-04 paper story.

A submission-oriented `main.tex` rewrite is authorized only after the prospective paper-identity gate resolves which claim ladder is supported.
