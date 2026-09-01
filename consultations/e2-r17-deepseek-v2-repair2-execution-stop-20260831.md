# E2-R17 DeepSeek V2 Repair2 execution stop

Status: `STOP_AND_ADJUDICATE_ACTOR_AUTHORIZATION_STATUS_SCHEMA_MISMATCH`

Repair2 was launched exactly once under contract
`9e38bdbfc71186e3e58587169d8c619bff4ae24de4145fefafa63e49a6f148a3`
and authorization
`9643a0a30d0acc4f32607b217701b368a895b2fe1e86a0aa84da24aa0a80898b`.
The atomic run-start receipt was written before provider I/O; PID and PGID were both
`2150504`.

The continuation correctly injected the 14 inherited pairs without provider replay.
It then completed fresh WIN-C and MRW updater states for
`e1-fmv-01/rep2`: 20/20 provider receipts and 10 claims per arm. Both learned-state
checkpoints are persisted. No heldout actor call reached the provider.

The first heldout task failed locally in the actor authorization validator:

```text
RuntimeError: authorization artifact does not authorize actor execution
```

The Repair2 authorization status is
`AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2`, while the frozen actor runner accepts only
`AUTHORIZED_E0`, `AUTHORIZED_E1`, or `AUTHORIZED_PUBLIC_EXTERNALITY`.
The authorization already grants `scientific_experiment=true`, mode `e1`, the exact
heldout task IDs, K=1, and non-initial-skill access; the failure is the status whitelist,
not the scientific scope.

Terminal counts are:

- 14/48 paired units (all inherited)
- 30/96 learned states (28 inherited + 2 fresh)
- 504/1728 heldout units (all inherited)
- 20 Repair2 updater claims/calls
- 0 Repair2 evaluator claims/calls
- 0 fresh heldout outcomes
- 0 ambiguous provider responses
- 0 partial-effect reads

The frozen analyzer was not run and no scientific conclusion was produced. Scientific
belief update remains `NONE`.

An outcome-blind measurement-only repair is scientifically eligible only as a new,
separately authorized version. It must preserve both completed updater states, forbid
their provider replay, bind an actor-compatible authorization path or explicit whitelist
delta, and preflight through the actor authorization validator before any evaluator I/O.
The existing authorization and runner must not be modified in place or relaunched.
