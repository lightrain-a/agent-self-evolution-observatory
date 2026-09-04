# E2-R17 publication experiment coverage plan — learned from SkillZip / SkillZip Pro / SkillRevise / SkillOpt / RethinkSkill

Status: **ZERO_PROVIDER / PLANNING_ONLY / DOES_NOT_MODIFY M2-M4 AUTHORITY**
Date: 2026-09-04
Current manuscript checkpoint: R5 / `855ab147a423c4e301c7d4f79f77e47141f53406`

## 1. Core conclusion

The E2-R17 program is already large in raw scientific workload. The remaining publication risk is not too few provider calls or too few internal mechanism experiments. It is a mismatch between:

- strong internal causal/localization evidence; and
- still-limited publication-level breadth in **literature baselines** and **external transport**.

Do not add more same-substrate mechanism experiments merely to increase volume.

## 2. Lessons from existing skill papers

### SkillZip (Bai et al., 2026)

Experimental structure is claim-aligned rather than one giant main table:

- 3 procedural benchmarks × 3 backbones for primary fidelity/compression;
- uncompressed evolved skill + closest compression baseline SkillReducer;
- separate cost/rollout study;
- cross-model transfer matrix;
- 16-round continual Zip-on-Write study.

Lesson: one closest baseline plus orthogonal experiments for efficiency, transfer, and continual behavior can be more informative than many weak baselines.

### SkillZip Pro (Bai et al., 2026)

The public headline evidence is substantially narrower than SkillZip but more deployment-specific:

- production content-moderation multi-round harness;
- multi-entry bundle routing/public-entry audit;
- protected vs aggressively unprotected compression as a decisive negative control;
- token accounting at bundle and end-to-end execution levels.

Lesson: narrow workload can be defensible when each experiment directly attacks a load-bearing failure mode.

### SkillRevise

- 3 verifier-driven benchmarks;
- 5 executors;
- no-skill / one-shot skill-creator anchors plus revised-skill method comparison;
- cross-executor / task-environment transfer.

Lesson: for a new skill-update method, at least one genuine literature-method comparison and transfer evidence are expected beyond internal mechanism controls.

### SkillOpt

- 6 benchmarks;
- 7 target models;
- 3 execution harnesses;
- 52 evaluated cells;
- comparisons against human, one-shot LLM, Trace2Skill, TextGrad, GEPA, EvoSkill;
- cross-model / cross-harness / nearby-task transfer.

Lesson: this breadth supports a broad "general text-space optimizer" claim. E2-R17 should not imitate this scale unless it wants an equally broad method claim.

### Rethinking Self-Evolving Agent Skills

- 5 benchmarks, 3 models, 14 supported settings;
- 42 matched feedback runs and 388 candidates;
- controlled feedback-source intervention is the scientific center;
- broader model analysis and test-time-compute controls are secondary.

Lesson: a mechanistic paper can justify substantial contribution through matched intervention quality, but still needs enough settings to show the observed mechanism is not a one-environment artifact.

## 3. E2-R17 current coverage

### Already strong / do not inflate further

- V2 Repair2: 48 pairs / 96 learned states / 1,728 heldout units.
- S1 selector intervention.
- historical frozen-state stability.
- byte-identical evidence replay.
- M2 deterministic semantic sufficiency.
- M3R4 fully prospective actor-noise localization.
- M4 fresh balanced Evidence × Generator bridge with disjoint SCREEN/VALIDATION.
- score-only and diagnosis-cardinality-informed generic controls.
- universal state-SHA aliasing and realization sensitivity.

This is already more than sufficient internal-mechanism volume if M3R4/M4 produce interpretable outcomes.

### Publication-level gaps

1. **Closest literature method baseline gap.**
   `W_FREE` is a valid native updater baseline and the generic states are causal falsifiers, but neither is a convincing answer to "how does this compare with a strong recent skill-revision method?"

2. **External-validity gap.**
   Current mechanism evidence is one controlled SpreadsheetBench-compatible substrate and one primary DeepSeek route. Untouched E3 would still be the same controlled substrate.

3. **Backbone gap.**
   A generic self-evolving-agent claim with only one primary backbone remains vulnerable to model-specific state-writing behavior.

4. **Component attribution gap.**
   If the complete compiler wins, current Q2 falsifiers bound generic/scope explanations in FF4, but do not directly compare canonical compilation with a strong execution-grounded free-form revision method.

## 4. Minimum publication-complete experiment package — conditional, not authorized

Open this package **only after current M3R4 and M4 claim-specific gates permit it**. It cannot rescue a failed M4 Q1.

### P1 — Baseline comparison (MUST)

Use one public benchmark setting and matched task splits.

Required anchors:

- `S0 / no update` — lower anchor, not a strong method baseline;
- `Native FREE` — current MindMemOS free-form updater, already the primary causal baseline;
- `SkillRevise-style execution-grounded revision` — closest recent literature baseline to trajectory diagnosis + skill editing;
- `Typed Compiler (ours)`.

Strong optional baseline if implementation/budget is clean:

- `SkillOpt` as a high-cost validation-gated optimizer baseline.

Do **not** add SkillCAT merely to increase baseline count unless the evaluated claim explicitly includes evidence-source selection. SkillCAT is more relevant to the parked FF4/Search-Projection line than to the primary state-generation claim.

### P2 — Public transport (MUST if title remains generic)

Minimum:

- official/public SpreadsheetBench heldout setting; and
- one **non-spreadsheet procedural benchmark** where the same frozen compiler vocabulary can be applied without post-outcome redesign.

Candidate domains to qualify prospectively:

- BFCL-V4 style multi-step tool use; or
- LiveMathematicianBench style procedural reasoning.

If no non-spreadsheet substrate can use the frozen compiler without changing the method, narrow the paper's claim/title instead of creating a new method after outcomes.

### P3 — Second backbone (MUST for generic claim)

Run the publication main comparison on one genuinely different executor/updater family in addition to DeepSeek.

The purpose is not a huge model sweep. It is to falsify "this is a DeepSeek/MindMemOS-specific state-writing pathology."

Two backbones are sufficient for this narrow mechanism/method paper if P2 also includes two domains. Three or more models are optional.

### P4 — Component ablation (SHOULD)

Highest-value ablation:

- structured/typed diagnosis + **free-form renderer**
  vs
- the same diagnosis + **canonical compiler**.

This directly tests whether canonical state materialization contributes beyond diagnosis structure.

Run prospectively as a separate publication ablation. Do not retrofit it into the already frozen M4 after seeing M4 outcomes.

### P5 — Cost / reliability accounting (SHOULD, cheap)

Report for every method:

- updater/provider calls;
- actor validation/evaluation calls;
- wall-clock time;
- final state tokens/bytes;
- parse/correction failure rate;
- state-generation failure/retry rate;
- downstream utility.

This is cheap because the execution receipts already contain most of the needed accounting.

## 5. Recommended final table structure

### Table 1 — Main publication comparison

Rows:

- S0 / Initial Skill
- Native FREE updater
- SkillRevise-style baseline
- SkillOpt (if cleanly reproducible; otherwise appendix)
- Typed Compiler (ours)

Columns grouped by:

- Benchmark A × Model 1
- Benchmark A × Model 2
- Benchmark B × Model 1
- Benchmark B × Model 2
- average
- provider/update cost

This is a **2 benchmarks × 2 backbones** publication matrix, not a blind 3×3 or 7-model sweep.

### Table 2 — Mechanism / component attribution

- M3R4 `D_X`, `D_A`, `E_REAL`, exact conditional gate;
- Native FREE vs Compiler generator-factor contrast;
- score-only generic;
- scope-matched generic;
- structured diagnosis + free-form renderer (publication ablation, if opened prospectively).

### Figure / appendix — transfer and robustness

One cross-model state transfer or one state-regeneration reliability plot is enough. Do not add both unless one serves a distinct claim.

## 6. Stop rules

- M4 Q1 fails: **do not** open public baselines/benchmarks to rescue the method story.
- M4 Q1 passes but Q2 generic controls collapse the FF4 explanation: keep complete-method story narrow; do not claim typed diagnosis.
- Public transport fails on the non-spreadsheet benchmark: either narrow the claim to spreadsheet/procedural data agents or stop architecture-general language.
- Second backbone fails while DeepSeek passes: report model dependence; do not average it away with more models.
- SkillRevise/SkillOpt beats the compiler under a fair matched setting: retain the state-regeneration mechanism result, but do not claim a superior update method.

## 7. Workload verdict

**Raw workload: already sufficient / high.**

**Internal causal evidence: sufficient if current frozen stages complete cleanly.**

**Final method-comparison evidence: currently insufficient because literature baselines have not been run.**

**External/generalization evidence: currently insufficient for a generic "self-evolving agents" method claim.**

The efficient completion target is not dozens of more cells. It is:

1. finish current M2/M3R4/M4 without redesign;
2. if and only if M4 permits expansion, add one closest literature baseline comparison;
3. run a 2-domain × 2-backbone public/transport matrix;
4. add one canonicalization-specific ablation and cost accounting.

That package is scientifically stronger than simply matching SkillOpt's raw experiment count.
