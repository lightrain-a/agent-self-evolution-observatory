# Agent Constraint Externality — AtomGit repeat-development static repair

Date: 2026-09-06  
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`  
Status: **STATIC REPAIR PASS / ZERO PROVIDER / EXECUTION CLOSED**

## Superseded static checkpoint

Commit `23ffffbb99c80d5894bc76b7b95eaceb65bed8ce` and protected bundle SHA256 `edbed772435d58fb211acf97b57f250caf721f0662c5e510deccb5585d119a6d` are superseded before any provider-bearing source execution.

No AtomGit scientific source request, repair request, topology episode, or scientific outcome was created under the superseded checkpoint.

## Defect

The first static design used `adjust-01.txt` and `modifier-01.txt` as the two TNF target-shared witnesses for every selected development template. That is insufficient: a topology edge is scientifically meaningful only if its shared resource is actually selected by the frozen target routing rule.

The selected Direct-SFQ TNF templates resolve to:

- `DIRECT-SFQ-A0-TNF-01`: `adjust-04.txt` + `modifier-03.txt`
- `DIRECT-SFQ-A0-TNF-02`: `adjust-04.txt` + `modifier-01.txt`
- `DIRECT-SFQ-A0-TNF-05`: `adjust-04.txt` + `modifier-01.txt`

Thus the old static TNF LOW/HIGH graph could overstate semantic coupling even though its declared resource-set intersection was 0/1/2.

Classification: `STATIC_TOPOLOGY_WITNESS_SEMANTIC_MISMATCH_ZERO_PROVIDER`.

## Repair

The family builder now deterministically replays the frozen target policy/routing rule and derives the actually selected adjustment and modifier file before constructing the matched topology arms. The repair changes only the development topology witness selection. It does not change:

- the six stable-hash-selected development templates;
- the selected AtomGit MiMo-V2.5-Pro backbone;
- target challenge instructions or expected target outputs;
- the R*/N* rules;
- the no-replacement/no-top-up rule;
- the confirmatory exclusion boundary;
- any provider/model outcome.

The selected development templates remain:

1. `DIRECT-SFQ-A0-FG-06`
2. `DIRECT-SFQ-A0-FG-03`
3. `DIRECT-SFQ-A0-FG-05`
4. `DIRECT-SFQ-A0-TNF-02`
5. `DIRECT-SFQ-A0-TNF-01`
6. `DIRECT-SFQ-A0-TNF-05`

## Requalification

Rebuilt frozen artifacts:

- contract file SHA256: `48c73344affd3c69a8156eac5073140cb1bf835a7632e39a534ac7667a59e980`
- protected bundle SHA256: `c1bc001b7d7fce0766d2ebc802211728f745013e8b0a4d863024830bb09b646b`
- static qualification file SHA256: `b4436f20632c8ff27206c64a492d9aa7ad1a31af512980b5a20a471833c9f38e`
- family builder SHA256: `f3fe153220a7d0d8fa290aebba64d9e8e2ffe689b16990d300fd847235b4e049`
- build/freeze module SHA256: `b47d1078175dd7bdc46ae18a12c74d8b59aada7dc2a76d174efb165d8c56d74b`
- AppWorld runtime/evaluator SHA256: `edbd5c41a8e96547668311a2cae0d1e55b64a24f147990d655c28686ea8e861b`

Static result:

- 6/6 families materialize;
- INDEPENDENT/LOW/HIGH exposure = 0/1/2 for all six;
- all non-target constraints initially satisfied;
- source/probe target instruction identical;
- target constraint identical across topology arms;
- arm instruction UTF-8 byte count and whitespace word count matched;
- exact-email evaluator rejects wrong recipient, body, attachment bytes, and duplicate matching email;
- 28/28 targeted + M1 regression tests PASS;
- protected bundle SHA unchanged before/after test execution;
- provider requests created by repair: 0;
- topology outcomes created by repair: 0.

## Authority

Execution remains closed. This static repair does not authorize source execution, repair generation, development repeat qualification, TO-V, RQ1/RQ2, RQ3, RQ4, or paper claim expansion.

The next legal action is an exact-code pre-execution review of the repaired checkpoint. Only a PASS may permit a separate narrow human source-execution authority.
