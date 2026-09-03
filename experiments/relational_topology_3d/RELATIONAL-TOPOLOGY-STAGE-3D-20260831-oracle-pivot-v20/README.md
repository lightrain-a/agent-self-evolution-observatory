# RELATIONAL-TOPOLOGY-STAGE-3D — Oracle R1 pivot

This successor records the prospective paper/experiment correction made **before any scientific P1 outcome was opened**.

## Why the paper pivots

The original story treated `SGP-12` versus `SGP-14` as a clean training-support intervention. An outcome-blind audit of the already-frozen real training corpora shows that this is too strong:

- both arms have 12,240 rows;
- SGP-12 contains 18,360 total relation edges (mean count 1.5);
- SGP-14 contains 30,600 total relation edges (mean count 2.5);
- SGP-14 therefore receives 66.7% more relation-edge supervision opportunities, along with a higher mean instruction token count.

The existing training remains useful, but the paper must call these **matched training exposure regimes**, not a pure causal manipulation of support alone.

## Corrected paper question

At fixed relation count and tightly controlled semantic/textual content, does **endpoint-sharing topology** create a residual difficulty within SGP-14's own training range, and can an exact-identity graph substitution through the same frozen decoder localize how much of that residual enters at or before the semantic-graph interface?

## Decisive developmental screen

Use unopened validation only:

- SGP-14 + the frozen shared SG2SC decoder;
- count 3: 40 matched CHAIN/HUB base-scene tuples;
- count 4: 40 matched CHAIN/HUB base-scene tuples;
- 160 total instructions;
- same base scene, active object IDs/classes/features/masks, relation count, predicate/direction multiset, instruction template, and exact CLIP token count within each pair;
- deterministic role counterbalancing and model-independent feasibility filtering;
- predicted graph and exact-identity oracle graph through the same decoder;
- identical downstream decoder random/noise seed;
- all materialized cases stay in primary end-to-end denominators;
- identity eligibility is an explicit diagnostic, never a silent filtering rule.

Count-2 CHAIN/HUB is removed because under the frozen undirected topology definition both are the same graph `P3 = K1,2`. `COMPONENT_BRIDGE_OPTIONAL` is also removed from the primary panel because no non-isomorphic definition was frozen.

## Frozen GO rule

Multi-seed confirmation is eligible only if all hold:

1. `|pooled predicted Delta_topo| >= 0.10` and the 95% paired base-scene bootstrap CI excludes zero;
2. count-3 and count-4 effects have the same sign and each `|effect| >= 0.05`;
3. text-to-graph topology effect has the same direction;
4. exact oracle substitution reduces the absolute topology gap by at least 50%, with `|pooled Delta_oracle| <= 0.05`;
5. exact-identity eligibility is at least 95% in every count × topology cell and the CHAIN/HUB difference is at most 5 percentage points within each count.

If any gate fails, the standalone topology/localization paper stops. It may not be rescued post hoc by SGP-12 OOD behavior, count 5/6, another topology label, relaxed matching, or a changed endpoint.

## Confirmation

Only after a developmental GO:

- keep official test untouched until confirmation;
- use three total independently trained SGP-14 seeds;
- apply the same frozen test-panel compiler, endpoints, thresholds, and oracle rules;
- keep claims explicitly conditional on the one frozen shared decoder unless decoder replication is separately authorized.

## Oracle review provenance

Independent browser review:

- Oracle 0.18.0 on server 52;
- GPT-5.6 Sol selected in the ChatGPT webpage;
- Extra High `4 of 5` verified in DOM;
- new conversation `6a995dbf-9f40-83ee-b5eb-dbce39b51d74`;
- `promptSubmitted=true`;
- verdict: `PIVOT`;
- full transcript remains content-addressed in the Oracle session and is referenced by `oracle_review_receipt.json`.

No scientific outcomes were used in this adjudication.
