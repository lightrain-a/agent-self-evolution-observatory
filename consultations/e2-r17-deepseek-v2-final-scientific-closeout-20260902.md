# E2-R17 DeepSeek V2 — Final Scientific Closeout

Date: 2026-09-02

## 1. Final protocol status

The complete Repair2 / Continuation V2 sample passed the frozen full-integrity audit before any scientific score was read:

- 48/48 paired stream-replicate units;
- 96/96 learned states;
- 1728/1728 heldout K=1 measurements;
- duplicate Continuation V1 measurements permanently excluded;
- the old mid-trajectory HTTP-429 attempt excluded;
- Pair29 measurement-only recovery admitted with exact logical-unit provenance;
- global scientific-lineage lease completed exactly once;
- no execution-time scientific inference.

The primary analysis was then authorized exactly once and executed against the integrity-audited manifest.

## 2. Frozen primary result

WIN-C:

- 683 / 864 heldout successes;
- mean utility = 0.7905092593.

MRW:

- 703 / 864 heldout successes;
- mean utility = 0.8136574074.

Raw descriptive difference:

- +20 / 864;
- +0.0231481481 absolute utility;
- +2.31 percentage points.

The independent confirmatory units are the 12 predeclared stream effects, not the 1728 heldout measurements.

Frozen stream-level inference:

- mean stream effect = +0.0231481481;
- exact one-sided sign-flip p = 0.171875;
- paired-stream bootstrap 95% CI = [-0.0185185185, +0.0659722222];
- paired-t 90% CI = [-0.0172735970, +0.0635698933];
- practical-equivalence margin = +/- 1/18 = +/- 0.0555555556;
- TOST equivalence = FAIL;
- negative-direction sign-flip does not support harm.

Final frozen verdict:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

This is a valid scientific endpoint. It is not a technical failure.

## 3. What the result establishes and does not establish

Supported:

- MRW has a numerically positive aggregate point estimate on this DeepSeek V2 substrate.
- The complete confirmatory sample is inconsistent with a claim of demonstrated practical equivalence under the frozen +/-1/18 margin.
- The result is not significantly harmful under the frozen harm check.
- Stream effects are heterogeneous enough that the preregistered superiority criterion is not met.

Not supported:

- a causal claim that MRW improves future persistent-skill utility over contemporaneous WIN-C;
- a claim that MRW and WIN-C are practically equivalent;
- a claim that MRW is harmful;
- a universal rule that more mixed/rejected evidence produces larger MRW gains;
- family-specific statistical effects;
- a prospective intermediate-difficulty / rescueable-regime law;
- a post-hoc favorable-subset rescue of the primary claim.

## 4. Predeclared descriptive heterogeneity

The pre-outcome E1-A support artifact froze per-stream mixed-pool availability. The experiment plan predeclared reporting `per-stream mixed dose and effect` and `descriptive family grouping only`.

Descriptive family view:

| Family | Pre-outcome mixed pools (2 streams, /16) | Stream effects | Mean stream effect |
|---|---:|---:|---:|
| aggregation_join | 9/16 | +0.0278, +0.0556 | +0.0417 |
| formula_materialization | 15/16 | +0.0556, +0.1250 | +0.0903 |
| input_output_contract | 14/16 | +0.0278, -0.0278 | 0.0000 |
| multi_step_pipeline | 14/16 | 0.0000, +0.1806 | +0.0903 |
| schema_key_alignment | 13/16 | -0.1250, ~0.0000 | -0.0625 |
| target_sheet_range | 13/16 | -0.0139, -0.0278 | -0.0208 |

Direction counts from the frozen primary analysis are 7 positive, 1 zero, and 4 negative stream effects (25 positive, 5 zero, 18 negative replicate effects).

This view is compatible with real effect heterogeneity, but it does not identify a moderator. In particular, similar pre-outcome mixed-pool counts occur in families with positive, null, and negative descriptive effects. Therefore mixed-pool availability alone is not established as a monotone predictor of MRW benefit.

No new family-specific p-value, subgroup selection, moderator fit, or regime-law inference is authorized from this sample.

## 5. Consequence for the paper story

The strongest currently defensible story is no longer:

> MRW causally improves persistent learning over winner-only learning.

The defensible result is:

> Winner-only projection creates a theoretically and operationally meaningful information bottleneck, but under the fully controlled DeepSeek confirmatory experiment, exposing rejected-witness evidence produced a +2.31pp aggregate point estimate whose stream-level uncertainty crossed zero. The same sample also failed the preregistered practical-equivalence test, leaving the learning consequence unresolved rather than null. Predeclared descriptive results show substantial cross-stream/family variation, motivating a prospective heterogeneity study rather than a post-hoc rescue claim.

The general distinction between acting projection and learning projection remains a scientifically useful problem formulation, but this experiment alone does not establish MRW as the causal solution.

## 6. Next scientific gate

The existing protocol explicitly says:

- a valid noisy V2 endpoint may terminate as HOLD;
- additional models/tasks/threshold changes cannot rescue the primary DeepSeek claim;
- E3 prospective regime prediction is allowed only after E1 establishes a learning consequence.

Therefore no automatic Qwen/GPT second backbone, public benchmark, RB-AGG rescue, or E3 regime-law test is authorized from this closeout.

A future study may be proposed as a **new, independently preregistered hypothesis test**, not as continuation of the current confirmatory claim. The scientifically strongest candidate is a prospective heterogeneity study that freezes a moderator or regime prediction from pre-outcome variables and tests it on new disjoint streams. Such a study must preserve the current HOLD unchanged and must not select the moderator by optimizing on these 48 outcomes.

## 7. Final disposition

- DeepSeek Repair2/V2 execution: COMPLETE.
- Protocol integrity: PASS.
- Primary MRW superiority: NOT ESTABLISHED.
- Practical equivalence: NOT ESTABLISHED.
- Harm: NOT ESTABLISHED.
- Final scientific state: `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.
- Current sample: closed; no further outcome-conditioned execution.
- Second backbone / public benchmark / E3 / paper promotion: no authority from this result.
