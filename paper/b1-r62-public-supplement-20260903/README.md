# B1 R62 reproducibility supplement

This supplement contains the outcome-level, anonymous receipts used for the fresh exact-information provenance experiments reported in the paper.

Included evidence:

- `qwen_utilization.json`: Qwen memory-utilization first stage.
- `qwen_ab.json`: Qwen 32-pair exact-information A/B result.
- `llama_utilization.json`: Llama memory-utilization first stage.
- `llama_ab.json`: Llama 32-pair exact-information A/B replication.
- `cross_backbone_adjudication.json`: no-pooling cross-backbone adjudication.
- `recompute.py`: deterministic recomputation of paired terminal effects, exact two-sided sign tests, and frozen 100,000-resample percentile bootstrap intervals from the unit rows.
- `MANIFEST.json`: SHA-256 inventory of every packaged file.

The public supplement intentionally omits infrastructure-bound receipts, machine names, user names, local absolute model paths, and source-side parser transcripts that are unnecessary for recomputing the reported terminal statistics. Full internal R57/R59 execution and adjudication receipts remain content-addressed in the research repository, and their receipt hashes are bound by the cross-backbone adjudication. This omission is a submission-anonymity/minimization measure and does not alter scientific outcomes or statistical inputs.

The two executor estimates are reported separately. The supplement does not authorize post-hoc cross-model pooling, a universal zero-effect claim, source-faithful L3 transport, or PSMG efficacy.
