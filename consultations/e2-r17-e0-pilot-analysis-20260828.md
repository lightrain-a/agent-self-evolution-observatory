# E2-R17 E0-r3 formal analysis

Date: 2026-08-28T07:08:40+00:00
Run: `/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828`
Summary SHA-256: `533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`
Protocol integrity: **PASS**
Decision: **HOLD_FOR_PREDECLARED_E0_FULL**

## Integrity

- 12/12 tasks; 96/96 unique content-addressed rollouts.
- 566 provider calls; retry=0; thinking=disabled; resolved model `deepseek-v4-pro-ga-260813`.
- 80 output workbooks, exactly matching verifier successes; zero technical failures.

## Nested-prefix outcome

| K | Success@K | Delta vs K=1 | Mixed pools | Rescue | V_pre failure | V_winner failure | Gamma |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11/12 (91.67%) | +0.00 pp | 0/12 (0.00%) | 0/12 (0.00%) | 8.33% | 8.33% | 0.00% |
| 2 | 11/12 (91.67%) | +0.00 pp | 1/12 (8.33%) | 0/12 (0.00%) | 8.33% | 8.33% | 0.00% |
| 4 | 12/12 (100.00%) | +8.33 pp | 6/12 (50.00%) | 1/12 (8.33%) | 8.33% | 0.00% | 8.33% |
| 8 | 12/12 (100.00%) | +8.33 pp | 8/12 (66.67%) | 1/12 (8.33%) | 8.33% | 0.00% | 8.33% |

At every prefix, the observed-pool identity holds exactly: `A_K-A_1 = V_pre-V_winner = Gamma_K`. No rollout-independence assumption is used.

## Regime and family localization

- K=8 ceiling: 4/12; mixed with rollout-0 success: 7/12; rescueable: 1/12; floor: 0/12.
- Mixed K=8 pools cover 5/6 families: aggregation_join, formula_materialization, input_output_contract, schema_key_alignment, target_sheet_range.
- Rescue covers only 1/6 families: target_sheet_range.
- There are 16/96 failed rollouts across 5/6 families, but K=8 winner-only exposes 0 failed task-level winners.
- The acting gain is localized to `r17-b1-tsr-p7` (`target_sheet_range`), the only intermediate/rescueable task.

## GO / HOLD / STOP

**HOLD_FOR_PREDECLARED_E0_FULL**

- Not STOP: one real rescue event exists and protocol integrity passes.
- Not E1 GO: support is only one rescue task in one failure family.
- E0-full remains frozen at >=6 rescue tasks across >=3 families on all 54 calibration tasks.
- Do not rerun the completed pilot. Execute only the 42 predeclared extension tasks with immediate checkpoints and missing-unit resume, then combine both tranches.
- E1, public benchmarks, paper/front-end promotion, and submission remain unauthorized.

## Scientific belief update

Rescue censoring is observable and the exact joint-pool identity holds, but support is one task in one family and cannot authorize E1.

This is a support and measurement qualification, not evidence that Rejected-Witness improves future frozen skill. The exact-same-pool updater intervention remains the decisive causal test after E0-full support passes.
