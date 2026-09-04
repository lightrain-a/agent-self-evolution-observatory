# E2-R17 latest plan/frontend — R2 control-state repair

Date: 2026-09-04
Status: `ZERO_PROVIDER_FRONTEND_CONTROL_STATE_REPAIR_ONLY`

The fresh independent R2 rereview passed the repaired causal transport estimand, unified-lane separation, public replication rule, and paper/claim semantics. It found exactly one remaining blocker before the existing fresh-identity boundary: the frontend simultaneously described fresh identity as the next executable boundary and as `NEXT_NOT_AUTHORIZED` / under a global `0 authority` label.

This repair changes **frontend/control-state semantics only**. It does not change the V3/R2 scientific contract, treatments, tasks, scientific units, provider budget, Stage-A/Stage-B plan, Public-P1 estimands, or any scientific outcome.

## Exact repair

### Identity qualification

The frontend now records:

- `fresh_identity_qualification_permitted = true`;
- `fresh_identity_called = false`;
- B0 status = `NEXT_EXECUTABLE`;
- wording = identity qualification is the **next executable qualification gate**.

This is not Stage-A scientific authority and is not a scientific outcome call.

### Scientific authorities

The frontend now counts only:

- Stage A;
- Stage B;
- Public P1.

Current scientific authority summary is therefore `0/3`, with each explicitly false/not authorized.

`baseline_execution` remains a status flag, not an authority object.

### Removed contradictory wording

For E2-R17, the frontend no longer displays:

- `zero execution authority` as a global statement covering identity qualification;
- `Roadmap frozen · 0 authority`;
- B0 `NEXT_NOT_AUTHORIZED`;
- aggregate `0/5` mixing execution events with authorities.

Instead it states:

> identity qualification = next executable qualification gate; Stage-A / Stage-B / Public-P1 scientific authority remains closed.

## Validation

- `generated/e2-r17-frontend-status.js`: JS syntax PASS;
- `e2-r17-frontend-view.js`: JS syntax PASS;
- stale E2 authority wording scan: no rendered stale contradiction remains;
- R2 contract/preflight hashes remain unchanged.

## Authority boundary

This repair itself executes no provider call.

After an independent narrow rereview passes this one control-state fix, the next executable boundary remains the already-defined **exactly one fresh DeepSeek identity qualification**, followed by local adjudication and separately minted Stage-A authorization only if identity passes.
