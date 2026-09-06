# Agent Constraint Externality — AtomGit repeat-development pre-execution review

Date: 2026-09-06
Role: fresh independent adversarial scientific-method reviewer
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`
Review target Git commit: `23ffffbb99c80d5894bc76b7b95eaceb65bed8ce`
Provider calls created by the reviewed freeze: 0
Topology outcomes observed by the reviewed freeze: 0

## Narrow question

Is the newly frozen six-family development design scientifically valid as a **development-only calibration object** for freezing technical repeat count R* and workload-planning N*, without leaking confirmatory topology outcomes or silently changing the main estimand?

Do not review paper prose, novelty, or future empirical effect. Do not recommend extra work merely for appearance. Identify only defects that could invalidate R*/N* calibration or contaminate later confirmatory inference.

## Parent evidence and boundary

A separate AtomGit MiMo-V2.5-Pro Direct-SFQ development qualification completed 12/12 technically valid target-only cases, with 9/12 usable semantic target failures, 3 target successes, 0 transport/harness/non-semantic failures, and 155 scientific model rounds. It was explicitly `development_only=true`, `confirmatory_reuse=false`, and produced no topology outcomes or repairs.

The new design does **not** count those old source calls as new source units. It uses only the fact that a template produced a usable semantic failure to define a development conditional-failure population. Within FG and TNF categories, exactly 3 templates are selected by SHA256 of a pre-frozen salt and case ID. Selected templates are:

- DIRECT-SFQ-A0-FG-06
- DIRECT-SFQ-A0-FG-03
- DIRECT-SFQ-A0-FG-05
- DIRECT-SFQ-A0-TNF-02
- DIRECT-SFQ-A0-TNF-01
- DIRECT-SFQ-A0-TNF-05

These six are permanently excluded from confirmatory inference.

## New scientific units

Each selected template is wrapped into a **new development family** with a new family/task identity and a newly materialized AppWorld source episode. The old Direct-SFQ episode is not replayed and is not treated as the new source episode.

The new source fixture contains the same target challenge plus two prospectively created dummy preserve entities. The source instruction remains target-only: it does not expose non-target constraints, topology labels, or coupling information.

A new source phase is allowed to continue only if all six new source episodes are technically valid semantic target failures. There is no replacement or top-up. Every new source trajectory must be prospectively persisted before any repair is generated.

## Repair boundary

If and only if all six new source episodes are valid semantic failures, generate exactly one target-local procedural repair note per family. The repair writer sees only target task/constraint and the persisted target failure trajectory. It may not see non-target outcomes, topology labels, coupling structure, or future probe outcomes. No human edit is allowed. One exact repair byte string is frozen per family and reused across all later REAL_REPAIR branches.

## Matched topology construction

For each development family, two file entities used by the target challenge are designated as target-shared resources. Two new dummy file entities are created prospectively. Each dummy path is byte-length matched to the corresponding target-shared path.

All three topology arms have exactly three constraints: one identical TARGET plus two preserve-file NON_TARGET constraints.

- INDEPENDENT: preserve the two dummy files; target/non-target shared-resource exposure = 0.
- LOW: preserve target-shared file 1 plus dummy file 2; shared-resource exposure = 1.
- HIGH: preserve target-shared files 1 and 2; shared-resource exposure = 2.

The full model-visible arm instructions are verified to have identical UTF-8 byte count and identical whitespace word count across INDEPENDENT/LOW/HIGH. The TARGET constraint object is byte-identical across the three arms. All non-target constraints are initially satisfied. Static AppWorld materialization verifies 0/1/2 exposure for all six families.

For FG targets, a new semantic evaluator `EMAIL_EXACT_RECIPIENT_BODY_ATTACHMENTS_V1` checks exactly one matching email, exact recipient, exact subject, exact body, and exact attachment names/bytes; it rejects wrong recipient/body/attachment or duplicate matching emails. TNF targets use exact output file path/content evaluation.

## Frozen R* rule

Six development families are permanently excluded from confirmation.

Initial development panel:
6 families x 3 topology arms x 2 branches (NO_UPDATE / REAL_REPAIR) x 2 repeats = 72 episodes.

Freeze R*=2 iff BOTH:
1. repeat-1 vs repeat-2 target-success disagreement rate <= 0.10;
2. mean absolute CRR repeat difference <= 0.10.

If R2 fails but both metrics are <=0.20, run exactly one additional repeat on the same six families. Freeze R*=3 iff target non-unanimous-cell rate <=0.20 and mean within-cell CRR range <=0.20. Any technical invalidity stops. R>3 is forbidden.

No UPDATE-vs-NO_UPDATE mean/sign or HIGH-vs-INDEPENDENT mean/sign is used to choose R*.

## Frozen N* rule

After R* is fixed, use the same six development families only to estimate dispersion. For each of family-level pooled RQ1 UE and family-level RQ2 HIGH-minus-INDEPENDENT UE contrast, define conservative SD as max(full-sample SD, every leave-one-family-out SD). Choose the smallest N* in {12,16,20,24} for which both conservative_SD/sqrt(N*) <= 0.10. If N=24 fails, stop. The N* decision artifact must not contain development mean effect or effect sign.

This is a workload-planning precision rule; it is not a confirmatory effect-sign test.

## Confirmatory boundary

Only after R* and N* freeze would a separate step prospectively generate exactly 24 fresh confirmatory reserve family IDs. These six development families and all 12 earlier Direct-SFQ cases are permanently excluded. Confirmatory panel eligibility uses only pre-topology facts: valid semantic source failure, frozen repair, target-only uptake delta >=0.50, and no interface/measurement invalidity. Post-topology target outcomes cannot delete or backfill families.

## Frozen artifacts

- Git commit: `23ffffbb99c80d5894bc76b7b95eaceb65bed8ce`
- Contract file SHA256: `9f7a91d05e6ceb4df6fb2b515f473b3529b614574c49c15bb010a9371e1e72e7`
- Protected bundle SHA256: `edbed772435d58fb211acf97b57f250caf721f0662c5e510deccb5585d119a6d`
- Static qualification file SHA256: `d8252622260207bc5ad8ccc49554abb310d46d3786ebea6880ec76f4c317da13`
- Family builder SHA256: `07e449bc96f9c9062fcc63e73f2ff4de430b518eb759aafefbcacfb2bd4326fc`
- Build/freeze module SHA256: `ad3f510553a6a0794b5a8b212d1dd3128c5bc490d3fe52fd03e30136381e3928`
- AppWorld runtime/evaluator SHA256: `edbd5c41a8e96547668311a2cae0d1e55b64a24f147990d655c28686ea8e861b`
- Regression tests: 27/27 PASS under frozen AppWorld runtime.
- Provider requests in this static build: 0.
- Current execution authority: closed.

## Required review

Evaluate these eight items:

A. Is selecting six **development-only templates** conditional on prior usable semantic failure, then executing wholly new source units with no replacement, legitimate for estimating repeat/dispersion behavior of the intended repairable-failure population? Or does this create a verdict-changing selection problem for R*/N*?

B. Is source-vs-probe separation clean enough: same fixture, target-only source instruction, non-target/topology visible only later in topology arms, all selected development families excluded from confirmation?

C. Does the dummy-vs-target shared-resource construction identify the intended 0/1/2 structural coupling while keeping obvious instruction-length confounding controlled? Flag any remaining confound that is severe enough to block development calibration rather than merely a limitation.

D. Is the target evaluator complete enough, especially the semantic Gmail target, to avoid false target success?

E. Are the R* rules direction-blind and sufficiently protected from effect-driven repeat selection?

F. Is the N* precision rule direction-blind enough, or does using dispersion of HIGH-minus-INDEPENDENT itself improperly leak effect information into sample-size choice despite excluding means/signs?

G. Is the proposed ordering source -> freeze repair -> repeat panel -> freeze R* -> freeze N* -> fresh 24-family confirmatory reserve consistent with the stated anti-post-selection boundary?

H. List any blocker that must be repaired before **any new provider-bearing development source execution**. Separate MUST_FIX from SHOULD_FIX.

Return concise JSON only, no Markdown, with exactly these keys:
`verdict`, `must_fix`, `should_fix`, `a`, `b`, `c`, `d`, `e`, `f`, `g`, `execution_authority_recommendation`.

`verdict` must be exactly one of `PASS_PREEXEC_REVIEW`, `REVISE_BEFORE_PROVIDER`.
`execution_authority_recommendation` must be exactly one of `MAY_SEEK_SEPARATE_SOURCE_AUTHORITY`, `DO_NOT_AUTHORIZE_PROVIDER`.
