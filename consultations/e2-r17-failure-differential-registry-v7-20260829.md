# E2-R17 Failure Differential Registry V7

Date: 2026-08-29
Status: **ACTIVE_CANONICAL_FAILURE_LEDGER_FOR_R17_WORKTREE**
Supersedes: `consultations/e2-r17-failure-differential-registry-v6-20260829.md` (`5c9700078b5be8831d4428fc9dbba762707a102fc35fc8561c3a5af2d76bf025`)

## Current scientific state

- **central_mechanism**: `OPEN_NOT_YET_ADJUDICATED`
- **e0_censoring_existence**: `SUPPORTED_ON_CONTROLLED_PILOT`
- **e1_a_treatment_support**: `PASS_STRONG_SUPPORT_78_OF_96_MIXED_12_OF_12_STREAMS_6_OF_6_FAMILIES`
- **e1_b_mrw_causal_effect**: `UNKNOWN_AND_BLOCKED_BY_NEGATIVE_CONTROL`
- **e1_b_negative_control**: `HOLD_IDENTIFIABILITY_HOSTED_STOCHASTICITY_NOT_EQUIVALENT`
- **provider_runtime_pilot**: `PASS_RUNTIME_MEASURABILITY_ONLY`

## Failure assets

### R17-F001-V3-BPE-PARITY — FAIL_MECHANICAL_TOKEN_PARITY

- Classification: `MEASUREMENT_ANALYSIS, PROTOCOL_CAUSAL_PURITY`
- Stage: V3 mechanical runtime pilot
- Symptom: Nominally equal source-token slices re-tokenized to unequal final provider-visible lengths after head/tail decoding and concatenation.
- Root cause: BPE can create a new merge at the splice boundary; equal selected source-token counts do not imply equal final rendered token counts.
- Scientific belief update: NONE
- Repair / stop: New V3.1 ExactMatchedEvidenceBlockRenderer matches the actual final re-tokenized evidence block, uses deterministic no-padding search, and preserves old failed V3 root/contract.
- Reusable rule: Fairness budgets must bind the exact model-visible representation after all rendering/transformation steps, not an upstream proxy count.

### R17-F002-LEGACY-PROJECTION-LEAK — LEGACY_PATH_INVALID_FOR_CAUSAL_E1

- Classification: `PROTOCOL_CAUSAL_PURITY`
- Stage: V3 causal-purity audit
- Symptom: Legacy updater packet exposed PROJECTION/ROLE/rollout/provenance labels and could attach the served winner score to a failed MRW transcript.
- Root cause: Acting provenance and learner-visible evidence semantics were not separated in the original wrapper.
- Scientific belief update: NONE; old path was causally invalid.
- Repair / stop: V3.1 BlindedEvidenceUnit exposes only selected evidence text in messages, stores selected trajectory verifier score as the learner outcome, and keeps acting/projection provenance in audit-only r17_* fields.
- Reusable rule: For same-pool causal interventions, provenance required for audit must be kept out of model-visible treatment unless it is itself a predeclared treatment variable.

### R17-F003-E1A-BUDGET-POSTHOC — HOLD_PRECALL_BUDGET_GUARD_MISSING

- Classification: `IMPLEMENTATION`
- Stage: E1-A pre-execution review
- Symptom: The declared 10-call per-rollout / 7680-call total ceiling was checked after execution or delegated to an unbound runtime rather than enforced before provider I/O.
- Root cause: Budget accounting was observational instead of transactional.
- Scientific belief update: NONE
- Repair / stop: SQLite BEGIN IMMEDIATE ledger claims budget before provider I/O, binds contract+authorization, never releases ambiguous claims, and fail-closes before the 11th per-unit or 7681st total call.
- Reusable rule: A scientific provider-call ceiling is a pre-I/O safety invariant, not a post-hoc statistic.

### R17-F004-E1A-AMBIENT-PYTHON — TECHNICAL_FAILURE_BEFORE_FIRST_ROLLOUT

- Classification: `RUNTIME_INFRA, IMPLEMENTATION`
- Stage: E1-A V2 pool-support execution
- Symptom: MindMemOS import failed with ModuleNotFoundError: pydantic before any rollout/provider call.
- Root cause: E1-A orchestrator launched the actor with ambient /usr/bin/python3 instead of the previously qualified frozen actor/evaluator venv.
- Scientific belief update: NONE
- Repair / stop: V2.1 binds exact actor venv/bin/python, VIRTUAL_ENV/PATH, runtime freeze SHA and qualification SHA before spawning any actor.
- Reusable rule: Runtime qualification must be executable-binding, not merely package-list provenance.

### R17-F005-SUPPORT-ZERO-FALSY — ADJUDICATOR_MECHANICAL_FAILURE

- Classification: `MEASUREMENT_ANALYSIS, IMPLEMENTATION`
- Stage: E1-A post-run support adjudication
- Symptom: A valid updater_calls=0 summary was parsed as -1 by int(summary.get('updater_calls') or -1).
- Root cause: Python falsy semantics incorrectly treated a meaningful zero as missing.
- Scientific belief update: NONE until repaired adjudicator reached the support endpoint.
- Repair / stop: Versioned adjudicator v2 changes only zero/missing parsing; the repair was independently reviewed before adjudicating the same frozen 96-pool artifact.
- Reusable rule: Scientific counters where zero is meaningful must distinguish absent/null from zero explicitly; never use truthiness as missingness.

### R17-F006-REVIEW-ACK-SCHEMA — LOCAL_FAIL_SCHEMA_WITH_VALID_MODEL_CONTENT

- Classification: `IMPLEMENTATION`
- Stage: V3.1 provider-runtime Pilot independent review
- Symptom: Both Kimi and DeepSeek returned complete PASS reviews, but the shared local validator required the historical repair_sha256_acknowledged field while the new schema defined draft_contract_sha256_acknowledged.
- Root cause: Review-harness validation hard-coded one historical acknowledgement field name instead of validating the acknowledgement field declared by the active schema.
- Scientific belief update: NONE
- Repair / stop: Shared validator now discovers active schema fields ending in _sha256_acknowledged, validates each exact SHA, remains backward-compatible, and fail-closes on wrong/missing acknowledgements. Existing model outputs were zero-provider reparsed.
- Reusable rule: Keep model generation and local schema adjudication as separate evidence layers; a parser failure does not erase a valid raw review.

### R17-F007-REPARSE-IMPORT-PATH — SCRIPT_IMPORT_FAILURE_THEN_REPAIRED

- Classification: `IMPLEMENTATION`
- Stage: Zero-provider review re-adjudication utility
- Symptom: Direct execution of the new reparse script initially failed before reading review data because repo root was not inserted into sys.path.
- Root cause: Launcher omitted the standard repository-root import binding used by other R17 scripts.
- Scientific belief update: NONE
- Repair / stop: Added explicit ROOT insertion before importing sibling scripts; successful second invocation reused the same raw reviews.
- Reusable rule: Standalone adjudication scripts must prove their own import-path reproducibility before being treated as evidence processors.

### R17-F008-UPDATER-RUNTIME-COVERAGE — HOLD_PROVIDER_RUNTIME_PILOT_BEFORE_PROVIDER_CALL

- Classification: `RUNTIME_INFRA, IMPLEMENTATION`
- Stage: V3.1 provider-runtime Pilot preflight
- Symptom: The actor/evaluator venv could import mindmemos_eval but failed importing first-party mindmemos.pipelines.skill.evolution.SkillEvolver because omegaconf was absent.
- Root cause: The existing runtime qualification covered the actor/evaluator entrypoints, not the persistent-updater dependency closure. The provider-runtime Pilot inherited a role-inappropriate runtime assumption.
- Scientific belief update: NONE
- Repair / stop: Created a dedicated updater runtime from pinned MindMemOS uv.lock/package, then explicitly applied the predeclared R17 renderer compatibility override tiktoken==0.11.0; first-party SkillEvolver import and zero-provider six-arm updater qualification pass under this dedicated runtime.
- Reusable rule: Runtime qualification is role-specific and must import/exercise the exact scientific entrypoint; actor/evaluator qualification never authorizes updater execution.

### R17-F009-PREFLIGHT-SOURCE-BINDING — NONAUTHORITATIVE_PREFLIGHT_MISMATCH

- Classification: `IMPLEMENTATION`
- Stage: Updater runtime diagnosis
- Symptom: An initial manual updater import check could not find mindmemos because it did not reproduce the runner's source-tree sys.path binding.
- Root cause: The diagnostic preflight did not mirror the actual execution environment/source binding.
- Scientific belief update: NONE
- Repair / stop: Repeated the check with the exact three source roots bound; that authoritative preflight then exposed the real missing omegaconf dependency in the actor venv.
- Reusable rule: A preflight that does not reproduce the execution binding is diagnostic noise and must not authorize or block science by itself.

### R17-F010-PROCESS-GUARD-SELF-MATCH — LAUNCH_NOT_ATTEMPTED_FALSE_ALREADY_RUNNING

- Classification: `IMPLEMENTATION`
- Stage: V3.1 provider-runtime Pilot V2 launch preflight
- Symptom: A naive pgrep -af duplicate-launch guard matched the current shell command and falsely reported ALREADY_RUNNING.
- Root cause: The search pattern was present in the guard process command line itself.
- Scientific belief update: NONE
- Repair / stop: Use separate process inspection plus run-root/lock/checkpoint state; after zero-state verification the exact same frozen contract was launched once.
- Reusable rule: Duplicate-launch guards must be resistant to self-match; content-addressed run-root/lock/checkpoint state is stronger than naive full-command pgrep.

### R17-F011-RUNNER-WRITE-TRANSPORT-LIMIT — ARTIFACT_WRITE_NOT_CREATED

- Classification: `IMPLEMENTATION`
- Stage: E1-B negative-control runner implementation
- Symptom: One oversized remote atomic source-write failed with spawn ENAMETOOLONG before creating the runner file.
- Root cause: Tool/transport command-size limit, not experiment/runtime failure.
- Scientific belief update: NONE
- Repair / stop: Write the same runner in bounded chunks; keep all protocol checks.
- Reusable rule: Tool payload limits are implementation failures; split artifact writes rather than deleting scientific checks.

### R17-F012-E1B-NC-NONEQUIVALENCE — HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY

- Classification: `SCIENTIFIC_IDENTIFIABILITY`
- Stage: E1-B identical-treatment WIN-A/WIN-B full negative control
- Protocol integrity: `12/12` stream pairs, `24/24` learned states, `432/432` held-out K=1 evaluations, no failure artifact, and exact contract/authorization bindings verified.
- Primary endpoint: With `N_s = J_s(WIN-B) - J_s(WIN-A)`, the mean difference is `-0.023148`; the preregistered 90% paired-t CI is `[-0.095239, 0.048943]`, which is not strictly inside the fixed equivalence margin `[-1/18, +1/18] = [-0.055556, +0.055556]`.
- Robustness: The 100,000-replicate paired bootstrap 90% CI is `[-0.087963, 0.041667]`; it is descriptive robustness and does not control the primary gate.
- Root cause: Identical-treatment variability was not demonstrated practically equivalent. The frozen negative control does not identify whether hosted updater stochasticity, evaluator stochasticity, or their interaction dominates.
- Scientific belief update: The sign and magnitude of the central Search-Projection mechanism remain `UNKNOWN`; no MRW effectiveness outcome was observed.
- Repair / stop: `HOLD MRW`. Do not rerun the same protocol, widen epsilon, delete noisy streams, change probes/model, or average favorable subsets. Any future identifiability attempt requires a new versioned nuisance-control protocol with an independently justified single-variable stochasticity/measurement intervention.
- Authority: `prepare_mrw_contract=false`, `execute_mrw=false`, `paper_promotion=false`, `submission=false`.
- Preserved evidence: `generated/e2-r17-e1-b-negative-control-adjudication-20260829.json` (`758d7514518216c6913d623b9175f237a35a63c4f2f523fa24a3097d07515a2e`).
- Reusable rule: A protocol-valid negative control that fails equivalence is an identifiability result, not an implementation failure and not evidence for or against the central mechanism.

### R17-F013-MRW-DECISION-LOGIC-CONFLICT — REPAIRED_BEFORE_ANY_MRW_OUTCOME

- Classification: `MEASUREMENT_ANALYSIS, IMPLEMENTATION`
- Stage: Pre-outcome MRW contemporaneous analysis sanity check
- Symptom: A synthetic small but perfectly consistent positive effect could satisfy the one-sided superiority test while also satisfying the preregistered ±1/18 practical-equivalence TOST, creating contradictory GO and practically-null interpretations.
- Root cause: The initial decision code evaluated statistical superiority independently of the practical-null equivalence gate, even though both were intended to be jointly authoritative.
- Scientific belief update: NONE
- Repair / stop: Freeze practical equivalence as disqualifying for GO: GO requires positive exact sign-flip significance, 95% paired-bootstrap lower bound >0, and TOST practical-equivalence must fail. If TOST equivalence passes, STOP_MRW_PRACTICALLY_NULL takes priority.
- Reusable rule: When statistical superiority and practical-equivalence gates coexist, their precedence and joint logic must be tested on synthetic boundary cases before outcome access; a method cannot be both GO and practically null.

## Qualified successes

### R17-S001-PROVIDER-RUNTIME-V2 — PASS_PROVIDER_RUNTIME_MEASURABILITY_ONLY_E1B_STILL_UNAUTHORIZED

- Stage: V3.1 hosted provider-runtime Pilot V2
- Lesson: Dedicated role-specific updater runtime repaired R17-F008; real first-party SkillEvolver consumed WIN-A/WIN-B/MRW under V3.1 blinding and exact budget accounting without runtime/parse failure.

### R17-S002-E1B-TRANSITION-HANDOFF — PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF_ONLY

- Stage: E1-B update-to-noninitial-skill transition runtime Pilot
- Lesson: Receipt/content-addressed learned skill can cross from dedicated updater runtime into frozen actor/evaluator runtime and complete K=1 verifier execution; this removes the final runtime handoff blocker before full WIN-A/WIN-B negative control.

### R17-S003-E1B-NC-PREEXECUTION-GATE — PASS_AUTHORIZED_NOT_EXECUTED

- Stage: E1-B WIN-A/WIN-B full negative-control dual review + zero-provider preflight
- Lesson: Both independent reviewers accepted the identical-treatment nuisance-control design and predeclared paired-equivalence statistics; zero-provider preflight revalidated all 96 E1-A pools, 12 stream pairs, 18 heldout probes, role-specific runtimes, hard budgets and frozen analysis constants before any A/B outcome exists.

## Permanent rules

- A technical, runtime, protocol, or measurement failure that occurs before a valid scientific endpoint produces no scientific belief update about the mechanism.
- The failed artifact, failed run root, stale lock, raw model response, and negative result are preserved when available; repair occurs under a new version/contract/root rather than overwriting history.
- A protocol-invalid result cannot be counted as a scientific negative or positive.
- A valid primary scientific negative cannot later be relabeled as implementation failure without new concrete evidence showing protocol invalidity that existed at execution time.
- A SCIENTIFIC_MECHANISM failure triggers the predeclared STOP/HOLD rule; additional benchmarks, models, task substitution, threshold changes, or favorable subsets cannot rescue the central causal claim.
- Every rerun must state the failure classification, exact repair delta, why rerun is scientifically permissible, and which scientific variables remain unchanged.
- Reviewer/parser/harness failures preserve exact raw model output separately from local validation status; reparsing existing output is preferred to paying for a new model call when semantics were already complete.
- Runtime qualification is role-specific: actor/evaluator, updater, and public-baseline harnesses must each import and exercise the exact execution entrypoint under their exact frozen runtime. Qualification of one role never implies qualification of another.
- A preflight is authoritative only if it reproduces the actual source-path binding, environment variables, executable, and entrypoint used by the scientific runner.
- Any dependency override applied after a lockfile-derived environment is explicit, versioned, hash-bound, justified, and requalified; it must never be described as lock-native.
- Success is also terminal evidence: completed runs must record protocol integrity, endpoint reached, scientific interpretation authority, and next gate rather than merely disappearing into a summary file.
- A protocol-valid negative-control non-equivalence is classified SCIENTIFIC_IDENTIFIABILITY, not IMPLEMENTATION and not SCIENTIFIC_MECHANISM: it blocks downstream causal interpretation without updating the sign/value of the central mechanism.
- If superiority and practical-equivalence criteria can both hold, the protocol must predeclare precedence before outcomes; R17 gives practical-null equivalence priority over method GO.
