# E2-R17 DeepSeek V2 execution blocker — 2026-08-30

## Status

`STOP_AND_ADJUDICATE_IMPLEMENTATION_SCHEMA_MISMATCH_BEFORE_PROVIDER_IO`

This launch did not reach a scientific endpoint. It provides no evidence for or against the WIN-C versus Mixed Rejected Witness effect.

## Protocol integrity before launch

- Git HEAD: `6644260e96b997e12b39dfed362cc8d28891d6fe`
- Frozen contract SHA-256: `54f37f073881fe676064ec738676b1b869d1625b2bdd8fe11980b9abf801f2bc`
- Frozen authorization SHA-256: `fbe5c0ce0b033c0bebc10d5f9b14230c740b838da5dbf33ea676c9f54a809ac4`
- Hash-bound runner SHA-256: `4ea3ecbb44b4143e28c144b1e19df20921dab81451c455b5800085f8b71e6ac3`
- Requested model: `deepseek-v4-pro`
- Resolved model: `deepseek-v4-pro-ga-260813`
- Actor `max_output_tokens`: `8192`
- Zero-provider preflight: `PREFLIGHT_PASS`, with 12 streams, 4 replicates per stream, 96 learned states, and 1728 heldout units declared.

The historical V1 result remains unchanged as `HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY`.

## Execution

The one formal runner process, PID 888490, exited during initialization with:

```text
KeyError: 'env_file'
```

The first failing dereference is runner line 204:

```python
load_env_file(Path(contract["env_file"]))
```

The same missing field would also be required when constructing each actor invocation at runner line 168.

The run root was never created. Therefore:

- 0/48 paired replicate units completed
- 0/96 learned states completed
- 0/1728 heldout rollout units completed
- 0 provider budget claims
- 0 provider calls
- 0 provider tokens
- 0 ambiguous provider units
- no lock, checkpoint, learned state, evaluation, or partial scientific score
- analyzer not executed
- second model not executed
- public benchmark not executed

## Root cause

The frozen DeepSeek V2 contract omits `env_file`, although its hash-bound runner requires that field twice. The preflight checks cardinalities, runtimes, pools, code hashes, and run-root freshness, but does not assert the presence of every runner-required contract field. This allowed `PREFLIGHT_PASS` followed by an immediate formal-run schema failure.

This is an `IMPLEMENTATION` failure, not a scientific-mechanism or scientific-identifiability result. Scientific belief is unchanged.

## Recovery boundary

There is no legal missing-unit resume under the current SHA pair. Adding `env_file` changes the frozen contract SHA and invalidates the existing authorization; changing the runner changes its bound SHA.

The next permissible action is a separately authorized repaired DeepSeek V2 contract that:

1. adds the required `env_file` binding;
2. strengthens preflight to validate runner-required schema closure;
3. leaves every frozen scientific variable unchanged;
4. uses a fresh run root;
5. receives a matching new authorization before any provider I/O.

Until that authorization exists, DeepSeek V2 remains not executed scientifically.
