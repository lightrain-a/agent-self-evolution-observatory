# E2-R17 Failure Differential Registry V5

Date: 2026-08-29

> This is the human-readable companion of the machine registry. A failure before a valid scientific endpoint does not update mechanism belief. Protocol-valid scientific negatives/identifiability failures are never laundered into engineering bugs.

## Current scientific state

- **central_mechanism**: `OPEN_NOT_YET_ADJUDICATED`
- **e0_censoring_existence**: `SUPPORTED_ON_CONTROLLED_PILOT`
- **e1_a_treatment_support**: `PASS_STRONG_SUPPORT_78_OF_96_MIXED_12_OF_12_STREAMS_6_OF_6_FAMILIES`
- **e1_b_mrw_causal_effect**: `UNKNOWN_AND_UNAUTHORIZED_UNTIL_NEGATIVE_CONTROL_EQUIVALENCE_PASS`
- **e1_b_negative_control**: `RUNNING_FROZEN_FULL_OUTCOME_NOT_YET_ADJUDICATED`
- **provider_runtime_pilot**: `PASS_RUNTIME_MEASURABILITY_ONLY`

## Failure / blocked-attempt ledger

| ID | Stage | Classification | Terminal status | Scientific belief update | Reusable rule |
|---|---|---|---|---|---|
| `R17-F001-V3-BPE-PARITY` | V3 mechanical runtime pilot | MEASUREMENT_ANALYSIS + PROTOCOL_CAUSAL_PURITY | `FAIL_MECHANICAL_TOKEN_PARITY` | NONE | Fairness budgets must bind the exact model-visible representation after all rendering/transformation steps, not an upstream proxy count. |
| `R17-F002-LEGACY-PROJECTION-LEAK` | V3 causal-purity audit | PROTOCOL_CAUSAL_PURITY | `LEGACY_PATH_INVALID_FOR_CAUSAL_E1` | NONE; old path was causally invalid. | For same-pool causal interventions, provenance required for audit must be kept out of model-visible treatment unless it is itself a predeclared treatment variable. |
| `R17-F003-E1A-BUDGET-POSTHOC` | E1-A pre-execution review | IMPLEMENTATION | `HOLD_PRECALL_BUDGET_GUARD_MISSING` | NONE | A scientific provider-call ceiling is a pre-I/O safety invariant, not a post-hoc statistic. |
| `R17-F004-E1A-AMBIENT-PYTHON` | E1-A V2 pool-support execution | RUNTIME_INFRA + IMPLEMENTATION | `TECHNICAL_FAILURE_BEFORE_FIRST_ROLLOUT` | NONE | Runtime qualification must be executable-binding, not merely package-list provenance. |
| `R17-F005-SUPPORT-ZERO-FALSY` | E1-A post-run support adjudication | MEASUREMENT_ANALYSIS + IMPLEMENTATION | `ADJUDICATOR_MECHANICAL_FAILURE` | NONE until repaired adjudicator reached the support endpoint. | Scientific counters where zero is meaningful must distinguish absent/null from zero explicitly; never use truthiness as missingness. |
| `R17-F006-REVIEW-ACK-SCHEMA` | V3.1 provider-runtime Pilot independent review | IMPLEMENTATION | `LOCAL_FAIL_SCHEMA_WITH_VALID_MODEL_CONTENT` | NONE | Keep model generation and local schema adjudication as separate evidence layers; a parser failure does not erase a valid raw review. |
| `R17-F007-REPARSE-IMPORT-PATH` | Zero-provider review re-adjudication utility | IMPLEMENTATION | `SCRIPT_IMPORT_FAILURE_THEN_REPAIRED` | NONE | Standalone adjudication scripts must prove their own import-path reproducibility before being treated as evidence processors. |
| `R17-F008-UPDATER-RUNTIME-COVERAGE` | V3.1 provider-runtime Pilot preflight | RUNTIME_INFRA + IMPLEMENTATION | `HOLD_PROVIDER_RUNTIME_PILOT_BEFORE_PROVIDER_CALL` | NONE | Runtime qualification is role-specific and must import/exercise the exact scientific entrypoint; actor/evaluator qualification never authorizes updater execution. |
| `R17-F009-PREFLIGHT-SOURCE-BINDING` | Updater runtime diagnosis | IMPLEMENTATION | `NONAUTHORITATIVE_PREFLIGHT_MISMATCH` | NONE | A preflight that does not reproduce the execution binding is diagnostic noise and must not authorize or block science by itself. |
| `R17-F010-PROCESS-GUARD-SELF-MATCH` | V3.1 provider-runtime Pilot V2 launch preflight | IMPLEMENTATION | `LAUNCH_NOT_ATTEMPTED_FALSE_ALREADY_RUNNING` | NONE | Duplicate-launch guards must be resistant to self-match; content-addressed run-root/lock/checkpoint state is stronger than naive full-command pgrep. |
| `R17-F011-RUNNER-WRITE-TRANSPORT-LIMIT` | E1-B negative-control runner implementation | IMPLEMENTATION | `ARTIFACT_WRITE_NOT_CREATED` | NONE | Tool payload limits are implementation failures; split artifact writes rather than deleting scientific checks. |

## Qualified successes

### R17-S001-PROVIDER-RUNTIME-V2
- Stage: V3.1 hosted provider-runtime Pilot V2
- Status: `PASS_PROVIDER_RUNTIME_MEASURABILITY_ONLY_E1B_STILL_UNAUTHORIZED`
- Lesson: Dedicated role-specific updater runtime repaired R17-F008; real first-party SkillEvolver consumed WIN-A/WIN-B/MRW under V3.1 blinding and exact budget accounting without runtime/parse failure.

### R17-S002-E1B-TRANSITION-HANDOFF
- Stage: E1-B update-to-noninitial-skill transition runtime Pilot
- Status: `PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF_ONLY`
- Lesson: Receipt/content-addressed learned skill can cross from dedicated updater runtime into frozen actor/evaluator runtime and complete K=1 verifier execution; this removes the final runtime handoff blocker before full WIN-A/WIN-B negative control.

### R17-S003-E1B-NC-PREEXECUTION-GATE
- Stage: E1-B WIN-A/WIN-B full negative-control dual review + zero-provider preflight
- Status: `PASS_AUTHORIZED_NOT_EXECUTED`
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

## Frozen next-endpoint policy

The WIN-A/WIN-B nuisance-control outcome is interpreted only through the predeclared policy below:

- PASS equivalence → **QUALIFIED_SUCCESS**: May prepare a separate MRW causal contract; MRW remains unauthorized until separately reviewed.
- FAIL equivalence → **SCIENTIFIC_IDENTIFIABILITY**: HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY; MRW remains unauthorized; no task/model/margin changes may rescue this tranche.
- Mechanism belief update: NONE from either nuisance-control outcome; it only determines whether MRW is identifiable under this substrate/runtime.
