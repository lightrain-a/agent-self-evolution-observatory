# E2-R17 vs SkillZip Pro — Experiment Workload Comparison

Date: 2026-09-04
Status: `ZERO_PROVIDER_DESIGN_AUDIT_ONLY`

## 1. Why compare against SkillZip Pro

SkillZip Pro is useful because it is a recent systems-style agent-skill paper whose empirical strength does not come from a wide benchmark/model matrix. Its scientific object is a production skill bundle with progressive loading, so its experiments go deep on execution costs, routing safety, deployment lifecycle, and continual updates.

Publicly verifiable paper facts:

- main production setting: one industrial content-moderation skill under a multi-round harness;
- second structural setting: a multi-entry bundle used to test routing / public-entry independence;
- four deployment configurations induced by two axes: One-Shot vs Continual, Persistent vs Transient;
- protected compression vs an intentionally unsafe/unprotected high-compression control;
- root-only / flat-style reductions are used to expose accounting/routing failures;
- reported headline production result: 38% bundle-token reduction and 10.4% end-to-end per-run token reduction with no reported quality loss;
- unprotected 71% compression can lose up to 26 accuracy points through one-sided false positives;
- multi-entry routing fidelity for the protected method is reported as 1.000 in public summaries, while root-only and flat comparisons can collapse routing fidelity.

The important experimental lesson is therefore **depth across orthogonal failure modes**, not benchmark breadth.

## 2. Workload shape

SkillZip Pro's workload should be understood as several orthogonal evidence blocks over a small number of realistic substrates:

1. **Production end-to-end quality + cost**
   - bundle/storage cost;
   - activation/path/per-run cost;
   - end-to-end quality.
2. **Safety / negative control**
   - protected vs unprotected aggressive compression;
   - demonstrates that more compression can be scientifically wrong.
3. **Routing / multi-entry correctness**
   - route preservation;
   - public-entry independence;
   - root-only / flat failure modes.
4. **Lifecycle comparison**
   - Persistent vs Transient;
   - storage/runtime/build/cache costs kept separate.
5. **Evolution schedule**
   - One-Shot vs Continual / Zip-on-Write;
   - tests whether the representation remains useful under repeated updates.

Thus SkillZip Pro is not a 'many datasets × many models' paper. It is a 'few realistic systems × many claim-specific diagnostics' paper.

## 3. Direct implication for E2-R17

E2-R17 is also a causal systems/interface paper, so the relevant comparator is the **number of independently justified evidence blocks**, not the raw benchmark count.

Current E2-R17 already has the analogous depth:

| SkillZip Pro evidence block | E2-R17 analogue | Status |
|---|---|---|
| production observation/cost boundary | search-projection availability/censoring | completed/support evidence exists |
| protected vs unsafe aggressive configuration | WIN-C vs universal MRW / interaction-only failure modes | closed global MRW is inconclusive and prevents universal promotion |
| routing correctness / public-entry independence | exact same-pool + same-acting causal invariants | frozen R2, independently reviewed |
| lifecycle distinction | current acting vs persistent future learning | central paper object |
| continual-update test | Stage-B persistent updater + heldout future-skill evaluation | planned in frozen V3/R2 |
| structural failure-mode comparison | procedural vs binding crossed moderator | frozen V3 primary interaction |
| real production evidence | one public natural transport lane | planned P1, not yet executed |

The one substantive evidence-type gap relative to the SkillZip Pro style is therefore **realistic external execution evidence**, not additional controlled synthetic workload.

## 4. Workload decision

### Controlled workload

`SUFFICIENT_AND_ALREADY_DEEP`

Do not increase V3 merely to imitate papers with more rows.

### Public / realistic workload

`ONE_REALISTIC_LANE_REQUIRED`

The already-planned SpreadsheetBench Verified unified transport + baseline lane is the correct analogue of SkillZip Pro's industrial production harness.

### Model breadth

`ONE_PRIMARY_MODEL_SUFFICIENT_FOR_MAIN_CAUSAL_STORY`

A second model is optional robustness, not a requirement to match SkillZip Pro. SkillZip Pro itself earns systems-paper strength through production depth, not a large model matrix.

### Benchmark breadth

`ONE_PUBLIC_BENCHMARK_SUFFICIENT_IF_DEEP`

Do not add multiple public benchmarks unless the first transport result raises a distinct generalization question prospectively.

## 5. What E2-R17 should copy from SkillZip Pro's experimental discipline

1. **One intentionally wrong extreme must remain visible.** The closed universal-MRW result should stay prominent rather than being hidden; it plays the same scientific role as SkillZip Pro's unprotected aggressive-compression failure.
2. **Measure the full systems path, not one endpoint.** Show generated evidence, served evidence/current behavior, learner-visible evidence, and future frozen skill together.
3. **Keep cost layers separate.** Public P1 should report update/evolution cost and learner evidence/token budget alongside heldout utility; do not collapse cost into one number.
4. **Add one realistic execution setting rather than a benchmark zoo.** SpreadsheetBench Verified P1 is enough if source-faithful, frozen, and baseline-complete.
5. **Stress the failure boundary.** If transport fails, retain the controlled mechanism and stop external-generalization claims; do not switch datasets.

## 6. Final comparison

Relative to SkillZip Pro, E2-R17's planned experimental workload is **not too small**. Its controlled causal tranche is actually heavier in stochastic executions and learned-state evaluations. The remaining risk is not workload quantity but whether the final paper includes the same kind of realistic systems evidence and failure-mode coverage that SkillZip Pro uses to make a narrow substrate convincing.

Final status:

`CONTROLLED_WORKLOAD_SUFFICIENT_PUBLIC_DEPTH_STILL_REQUIRED`
