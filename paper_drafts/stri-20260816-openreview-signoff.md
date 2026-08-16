# STRI — ICLR 2027 OpenReview signoff

## Machine-closed items

- Official ICLR 2027 style: PASS.
- Double-blind PDF: PASS.
- Main text: 9 / 9 pages.
- Citations: 11 resolved; no undefined references; no overfull boxes.
- Mandatory AI-use statement: present.
- Reproducibility statement: present.
- Independent final paper review after the baseline/ablation/failure/sensitivity and qualified P0-E boundary revision: `READY_TO_SUBMIT` (confidence 0.93, score 7/10, 0 required revisions).
- Paper Evidence Quality v2: `PASS_MANUSCRIPT_EVIDENCE`, evidence debt 0.
- Current narrow claim scope requires no new GPU evidence.
- Paper Quality v2.1 visual evidence: 4 main figures, source-bound to data/scripts/captions; new ablation/robustness/failure panel included.
- Anonymous supplementary reproduction bundle: manifest PASS, `reproduce.py` PASS, 13/13 unit tests PASS, clone/split + sensitivity reproduction PASS, sanitized SkillRL P0-E receipt verification PASS, figure regeneration PASS, identity/path scan PASS.
- **Deadline source conflict is intentionally not machine-closed:** the current ICLR 2027 Author Guidelines say abstract/full deadlines are 2026-09-18/2026-09-25 AoE, while the official Dates, Call for Papers, and conference homepage publish 2026-09-11/2026-09-16 AoE. Until a human confirms the live OpenReview deadline, this checklist uses the earlier 2026-09-11/2026-09-16 dates operationally.

## Files to upload / archive

- Paper PDF: `/data/wyt/agent-self-evolution-observatory/submission-packages/STRI-ICLR2027-20260816.pdf`
  - SHA256: `15f02bcaef727853e6fa0a4387c22950fa9f82db83bb54bafceb8686c6b69589`
- Paper source ZIP: `/data/wyt/agent-self-evolution-observatory/submission-packages/STRI-ICLR2027-20260816-source.zip`
  - SHA256: `84ad1b0cff9504b9bebfc8b2178c6143f34a3bd34c063b562bcd25e551bee0f3`
- Anonymous supplementary ZIP: `/data/wyt/agent-self-evolution-observatory/submission-packages/STRI-ICLR2027-20260816-supplement.zip`
  - SHA256: `ab38373f19c38a09de528ec2daac21c359cc819d970edb7594379e4913edfb5f`

## Human signoff required before abstract submission

- [ ] **Before 2026-09-11 AoE, verify the live ICLR/OpenReview deadlines** and resolve the official-page conflict above. Do not plan against the later dates until this is confirmed.
- [ ] Freeze the **complete author list** by the confirmed abstract deadline (use 2026-09-11 AoE operationally until the conflict is resolved). ICLR 2027 does not allow adding or removing authors after the abstract deadline; author order may still be changed up to the full-paper deadline.
- [ ] Confirm every author has the correct OpenReview profile and verified email; update profile/affiliation information now rather than near the deadline.
- [ ] Check ICLR 2027 author quotas and reciprocal-reviewing obligations for the complete author list; register a qualified reviewer if required.
- [ ] Confirm there is no substantially similar archival submission under parallel review that violates the ICLR dual-submission policy.
- [ ] All authors read and acknowledge the ICLR Code of Ethics / Code of Conduct obligations.
- [ ] All authors review the paper's mandatory **AI-use statement** and explicitly accept responsibility for the final manuscript, claims, code, and AI-assisted artifacts.
- [ ] Review the title and genuine abstract used for reviewer bidding; do not submit a placeholder abstract. The title may still be revised before the confirmed full-paper deadline; use **2026-09-16 AoE** as the operational freeze until the official-page conflict is resolved.

## Final upload check

- [ ] Recompute SHA256 for the PDF and supplementary ZIP immediately before upload and match the values above.
- [ ] Open the exact upload PDF and visually confirm `Anonymous authors / Paper under double-blind review`.
- [ ] Search the exact PDF and supplementary archive once more for author names, affiliations, usernames, local paths, private repository names, tokens, and identifying URLs.
- [ ] Unless the official-page conflict is resolved to a later live OpenReview deadline, submit the genuine abstract by the operational-safe **2026-09-11 AoE**.
- [ ] Unless the official-page conflict is resolved to a later live OpenReview deadline, submit the full paper and supplementary materials by the operational-safe **2026-09-16 AoE**.

## Scientific lock

The submission claims only:

1. released self-evolving skill control surfaces can be sensitive to skill-package representation;
2. `R*(A)` exactly decides finite package-only additive-exposure equalizability on a frozen support matrix;
3. in the audited released regimes, non-equalizable support geometry rather than overlap prevalence tracks the static STRI residual.

Do **not** add claims of downstream utility harm, dynamic STRI success, empirical SQC success, LP algorithmic novelty, or use the qualification-failed Qwen3-8B bank as scientific evidence for or against dynamic STRI. The separate SkillRL final-policy C4 experiment is a qualified `STOP_FIXED_POLICY_DYNAMIC_BRIDGE` realization only: it does not certify a population-level no-effect theorem or persistent principle dead end, does not identify active recovery as the mechanism, leaves N1--N3 unchanged, keeps Stage-2 locked, and authorizes no new GPU.
