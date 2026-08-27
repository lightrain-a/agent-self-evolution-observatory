You are one member of an independent Kimi × DeepSeek scientific red-team for a prospective ICLR-level paper. This is an INTERNAL, zero-authority consultation. You cannot authorize experiments, GPU use, paper promotion, or submission. Be adversarial, concrete, and willing to recommend STOP. Do not reward engineering volume or polished wording.

The candidate is E2-R17 / Search-Projection Censoring. The supplied dossier contains the full current R17 design artifacts, historical F0 state, a current-source collision audit through 2026-08-27, and a zero-provider theory strengthening proposal. Treat the primary-source facts and exact artifact boundaries as binding. In particular, SkillCAT is a direct method collision, TopoCurate is a representation/selection collision, and the old R3 runner is not an executable R4 implementation.

Requested endpoint: deepseek-v4-pro. Your actual resolved identity is recorded outside this prompt and is the source of truth.

Do not invent citations or claim to have browsed beyond the supplied primary-source dossier. Separate: (i) what follows mathematically, (ii) what is only a modeling assumption, (iii) what requires experiment, and (iv) what is already reduced by prior work.

ROUND 3 — SINGLE-OBJECT CONVERGENCE
You have seen both models' Round-1 and Round-2 outputs. You are forbidden to return a feature zoo, benchmark zoo, router, frontier, or module collection. Retain exactly:
- one central scientific object;
- one causal chain;
- one strongest falsifiable theoretical prediction;
- one decisive intervention;
- one method that follows naturally from the mechanism (prefer the simpler Rejected Witness if sufficient);
- one explicit STOP condition.
Delete claims already occupied by SkillCAT, TopoCurate, sibling distillation, SkillOpt, and failure-only skill evolution.

PRIOR REVIEWS:
{
  "requested_model": "deepseek-v4-pro",
  "resolved_model": "deepseek-v4-pro-ga-260813",
  "review": {
    "causal_identification_attacks": [
      "The cloned-state intervention is not a true causal experiment on the persistent learning process because it only tests a one-step update. The longitudinal claim—that repeated winner-only updates cause weaker frozen skill than L/L—requires a different causal estimand that the one-step clone design cannot identify. The dossier acknowledges this but the paper must not conflate the two.",
      "The precommitted rollout-0 arm is not a valid counterfactual for 'what the learner would have seen without winner selection' because rollout-0 is still generated under the same search policy and skill state. It is a different observation kernel, not a no-censoring baseline. The identity V_pre = 1-p is a modeling assumption about what the learner would see, not an observed quantity.",
      "The acting invariance validator requires that all high-K arms serve the exact same winner. This is only possible if the winner selection is deterministic given the pool. Any stochasticity in the verifier or selector breaks the exact-same-pool claim and confounds the projection effect with acting differences.",
      "The prospective prediction F3 is vulnerable to outcome-driven family selection. If the held-out families are chosen after seeing which families show large Gamma or delta in development, the prediction is not prospective. The dossier requires pre-outcome freezing, but the audit does not specify a mechanism to prevent post-hoc family redefinition.",
      "The family overlap problem is not solved by the dossier. The mutually exclusive partition Z of mixed pools is asserted as necessary but no operational rule is given for assigning a mixed pool with multiple failure types to a single family. Without this, the sum over z of Pr(M, Z=z) × delta_z is not identified.",
      "The delta_z estimand requires a fixed updater and a fixed future task distribution. If the updater's behavior depends on the order of updates or the specific contrast packet format, delta_z is not a stable property of the failure family but an artifact of the particular updater implementation. The paper must either fix the updater and report delta_z as conditional on it, or acknowledge that the mechanism does not generalize across updaters."
    ],
    "decisive_kill_experiment": "The cloned-state exact-same-pool projection-null experiment (F2). Take one fixed pre-update skill state S, one task batch, one exact K-pool T_K, one acting winner, one updater, one verifier, one update seed. Clone S into arms that differ only in g(T_K): winner-only vs. precommitted rollout-0 vs. rejected-witness vs. contrast packet. Then freeze all skills and evaluate on a common held-out probe with K=1. If changing g(T_K) produces no directional difference in future frozen skill J(U(S,g(T_K))) in the predicted direction, the central mechanism is dead regardless of any longitudinal or prospective results. This single experiment isolates the entire causal claim: that the learning projection, not the acting projection or compute amount, drives persistent skill quality.",
    "deeper_scientific_object": {
      "exists": true,
      "object": "Outcome-dependent observation kernels in sequential decision-feedback loops, where the deployed policy determines which generated outcomes become visible to a persistent learner. This subsumes Search-Projection Censoring as a special case where the deployed policy is a best-of-K verifier-selected winner and the learner is an external skill updater. It also subsumes selective labels, performative prediction, and DAgger as instances of the same structure: a decision rule induces an observation distribution that feeds back into future behavior.",
      "why_deeper": "The R17 object is a specific instantiation of a more general phenomenon: any system that generates multiple candidate outcomes and then selects one for deployment creates a missing-not-at-random observation process for any learner that only sees the deployed outcome. The deeper object is the coupling between the selection rule and the learner's observation kernel, of which winner-only best-of-K is one parametric case. This would unify R17 with RLVR pass@k inversion, selective labels, and performative prediction under a single formal object: the mapping from deployment policy to learner-visible distribution and its fixed points."
    },
    "formula_or_mechanism_that_is_pretty_but_empty": "The Gamma_K(p_z) × delta_z factorization is currently attractive but scientifically underidentified. The identity Gamma_K is exact, but delta_z = 'expected future gain from failure/contrast evidence minus expected future gain from served-success evidence' is not a measurable quantity without a precommitted, mutually exclusive failure-family partition and a fixed updater. The dossier itself admits overlapping post-hoc failure tags cannot be summed. Until delta_z is operationally defined via a frozen disjoint partition and a specific updater, the product is a tautological decomposition of an effect into 'how much was censored' times 'how valuable the censored evidence was', with the second factor free to absorb any residual. The continuous-verifier layer-cake extension is mathematically valid but adds no empirical content beyond the binary case unless a threshold policy is actually used.",
    "irreducible_novelty": "The exact rescue-censoring identity A_K - A_1 = V_pre - V_win = Gamma_K(Q) = Pr(Y_1=0, max_i Y_i=1), which holds without independence or exchangeability assumptions, together with the cloned-state exact-same-pool intervention that changes only the learning projection g(T_K) while holding the acting winner fixed. This is a precise order-statistic/coupling identity about how acting selection changes the updater-visible experience distribution, not a general claim that failures are useful or that search can harm learning.",
    "method_collision_assessment": {
      "SkillCAT": "SkillCAT is a direct method collision for the CADP contrast packet. It already does same-task multi-seed success/failure pairing, first-divergence extraction, contrastive skill editing, and replay validation in an external persistent-skill pipeline. CADP cannot claim novelty for any of these components. The only residual is the serving-time endogenous censoring mechanism and the exact identity, which SkillCAT does not study. If the paper's contribution is 'use success/failure contrast to update a skill', it is not novel. If the contribution is 'serving-time winner selection endogenously removes the failure evidence that SkillCAT-style methods would use', that is a different and potentially novel claim, but it requires the causal intervention to establish.",
      "TopoCurate": "TopoCurate is a direct representation/selection collision. It already argues that outcome-based filtering ignores interaction dynamics and uses branch/error topology to select training data. The R17 claim that winner-only projection discards useful structure is not novel. The residual is the specific serving-time best-of-K selection mechanism and the exact identity, which TopoCurate does not address. However, the paper must not frame its contribution as 'success filtering loses information' because TopoCurate already established that.",
      "other": [
        "Rethinking Self-Evolving Agent Skills (arXiv:2608.02636) already established that failure feedback is essential for skill evolution and that test-time scaling differs from persistent skill improvement. The R17 claim that failures matter is not novel. The residual is the endogenous censoring mechanism, not the value of failure feedback.",
        "Search-E1, Sibling-Guided Credit Distillation, Outcome-Verified Comparative Self-Distillation, and SKILL-KD already use sibling trajectories, success/failure divergence, and contrastive distillation. R17 cannot claim novelty for sibling contrast or first-divergence extraction.",
        "Do Not Waste Your Rollouts and TSR already establish that search experience can be recycled into training. The claim that search can teach more is already established. R17 must condition its claim on the learning projection, not on search budget.",
        "SkillOpt and SkillHEX already establish bounded validation-gated skill editing, rejected-edit memory, and diagnostic evidence for skill revision. R17 cannot claim novelty for the optimizer feature bundle.",
        "Selective labels, performative prediction, and DAgger are mature conceptual reductions. R17 is a specialized instance of these frameworks. The paper must acknowledge this and not claim to discover a new general phenomenon."
      ]
    },
    "recommendation": "REVISE_AND_NARROW. The paper should be reframed as a mechanism-level causal study of serving-induced selective trajectory logging in persistent self-evolution, with the exact rescue-censoring identity as a definitional tool, not a theorem. The CADP method should be demoted to a simple Rejected-Witness baseline unless the contrast packet beats it. The paper must not claim novelty for success/failure pairing, first divergence, bounded editing, replay validation, or rejected-edit memory. The decisive F2 cloned-state projection-null experiment must pass before any longitudinal or prospective claims are made. If SkillCAT-style contrast explains the full effect without the serving-selection causal chain, the paper should be reduced to an application or stopped.",
    "single_sentence_verdict": "The paper has a narrow but potentially real mechanism-level novelty—serving-time winner selection endogenously censoring diagnostic failures from a persistent updater—but it is currently buried under method components that are already published, and the central causal claim is only testable through a single decisive cloned-state projection-null experiment that has not been run.",
    "strongest_direct_reduction": "TopoCurate (arXiv:2603.01714) is the strongest direct reduction. It already argues that outcome-based filtering of successful trajectories ignores interaction dynamics, projects multiple same-task trials into a semantic quotient topology containing effective and failure branches, and uses branch/error structure to select training data. This preempts the general claim that winner-only selection discards useful branch structure. The residual R17 claim must be the serving-time endogenous censoring mechanism and the exact identity, not the general 'success filtering loses information' statement.",
    "theory_attacks": [
      "The independence-free identity A_K - A_1 = Pr(Y_1=0, max_i Y_i=1) is a trivial algebraic rearrangement: A_K - A_1 = E[max_i Y_i - Y_1] = Pr(Y_1=0, max_i Y_i=1) for binary Y_i. It is not a scientific discovery; it is a definition of the rescue-censoring event. The paper must not present this as a theorem with explanatory power.",
      "The i.i.d. Bernoulli specialization Gamma_K(p) = (1-p) - (1-p)^K and its maximizer p*(K) = 1 - K^(-1/(K-1)) are elementary order-statistic calculations. The intermediate-difficulty peak is a property of the binomial model, not an empirical law. Any deviation from i.i.d. (which the dossier admits is likely) destroys the peak location and the one-parameter curve.",
      "The correlated-rollout prediction that heterogeneity reduces Gamma_K relative to the i.i.d. curve is a Jensen's inequality observation about concavity of (1-theta) - (1-theta)^K. It is mathematically true but provides no quantitative prediction without a model of the heterogeneity distribution.",
      "The continuous-verifier layer-cake identity E[max_i R_i - R_1] = integral of [V_pre(t) - V_win(t)] dt is a standard layer-cake representation. It does not strengthen the scientific claim; it merely restates the binary identity at every threshold. The paper should not imply this is a substantive extension.",
      "The information-theoretic statement I(Z; g_win(T_K)) <= I(Z; T_K) is a direct consequence of the data-processing inequality for deterministic coarsening. It is true but vacuous as a scientific claim: it says a richer observation has weakly more information for a Bayes-optimal learner, which the dossier itself admits does not apply to a fixed LLM updater. This should be removed or explicitly labeled as non-contributing intuition.",
      "The Gamma × delta factorization is exact only under the gated-projection construction where the alternative projection equals winner-only outside the mixed event M. This is a tautological decomposition: any effect of changing the projection can be written as Pr(M) × E[effect | M]. The scientific content is entirely in whether delta_z is positive and predictable, which is an empirical claim about the updater, not a theoretical result."
    ],
    "thesis_reduction_verdict": "The thesis is partially reducible but not fully reducible. The broad claim that winner/success filtering discards useful failure structure is already established by TopoCurate and Rethinking Self-Evolving Agent Skills. The specific mechanism—serving-time best-of-K selection endogenously censoring diagnostic failures from an external persistent updater, with an exact acting-gain/failure-visibility identity—is not directly reduced by any cited work."
  },
  "round": 1
}
{
  "requested_model": "kimi-k3",
  "resolved_model": "kimi-k3",
  "review": {
    "causal_identification_attacks": [
      "The key causal claim requires exact pool identity and acting invariance. Any difference in served winner, prompt serialization, verifier access, tool trace truncation, or updater token budget across arms confounds projection with evidence quality or budget.",
      "Precommitted rollout-0 is not a clean substitute for a rejected witness if rollout-0 has different position bias, temperature realization, length, tool-use pattern, or verifier-score distribution from the counterfactual winner-conditioned evidence.",
      "The rejected-witness rule must be frozen before outcomes. Choosing the most informative, hardest, or representative failure after seeing trajectories reintroduces outcome-dependent selection and can manufacture delta.",
      "delta_z is not identifiable from observational success/failure feedback comparisons because mixed pools differ from all-success and all-fail pools in task difficulty and latent family prevalence. It needs cloned updater states and held-out probes.",
      "The longitudinal reversal can be confounded by skill-state divergence after the first update: later high-K pools are no longer the same across arms. The paper must separate first-update causal effects from path-dependent evolution effects.",
      "Held-out validation gating can itself preferentially accept patches from certain evidence types. Acceptance rate, patch type, and rejection memory must be reported or the gate becomes part of the treatment.",
      "If frozen evaluation uses tasks related to the evolution tasks by workbook, template, or family leakage, the estimated future-skill gain may be instance memorization rather than reusable skill learning.",
      "The scientific unit must remain complete independent evolution streams or cloned learned-skill states. Treating rollouts, patches, tasks, or repeated endpoint calls as independent n would invalidate uncertainty estimates."
    ],
    "decisive_kill_experiment": "Run the cloned-state same-pool intervention on a qualified substrate: same initial skill hash, same task batch, same exact K-pool hashes, same served winner, same updater and update seed, and compare winner-only versus precommitted rejected-witness learning evidence, followed by common frozen K=1 held-out evaluation. If the rejected witness does not improve future frozen skill in the preregistered direction—especially in mixed rescue pools with positive estimated diagnostic value—the central mechanism is dead.",
    "deeper_scientific_object": {
      "exists": true,
      "object": "Decision-induced observation kernels for persistent learning from search: a deployed selector maps a generated search object to served behavior and separately determines the updater-visible evidence measure, thereby controlling the future learning distribution.",
      "why_deeper": "This object contains Search-Projection Censoring as a special case, connects selective labels, performative prediction, DAgger, and search distillation, and makes the real scientific variable the observation kernel rather than search budget, contrastive prompting, or failure feedback. It also explains both harmful and beneficial search regimes through what evidence is retained, not through compute amount."
    },
    "formula_or_mechanism_that_is_pretty_but_empty": "The mutual-information diagnostic-retention quantity D_g = I(Z; g(T_K) | x, S_t) is currently attractive but mostly decorative outside the controlled suite. In real benchmarks Z is not identified, the estimator is not specified, and data processing only gives a weak inequality that does not imply a fixed LLM updater benefits from richer evidence. The paper should not present this as a measured mechanism unless Z is operationally defined and the estimator is validated.",
    "irreducible_novelty": "The only currently defensible irreducible novelty is the coupled package: (1) an independence-free rescue-censoring identity linking acting gain to winner-only failure-visibility loss on the same search pool; (2) an exact-same-pool, fixed-acting-winner cloned intervention that changes only the learning projection; and (3) prospective prediction of held-out frozen-skill deficits from pre-outcome censoring mass times diagnostic value. The novelty is not CADP, contrastive packets, or failure usefulness.",
    "method_collision_assessment": {
      "SkillCAT": "Direct method collision. It already covers same-task success/failure contrast, divergence extraction, external skill editing, and replay validation. R17 survives only if the serving-selection censoring law, same-pool fixed-winner intervention, and prospective frozen-skill prediction remain central and SkillCAT is treated as a mandatory baseline.",
      "TopoCurate": "Representation and selection collision. It already argues that outcome filtering discards useful branch structure and uses topology containing effective and failure branches for training-data selection. R17 must emphasize external persistent skill updating, winner-only serving-induced observation loss, and future frozen-skill endpoints rather than generic branch-structure value.",
      "other": [
        "Rethinking Self-Evolving Agent Skills removes novelty from failure feedback being useful and from test-time scaling differing from persistent skill gains.",
        "Search-E1, SGCD, OVCSD, and SKILL-KD remove novelty from sibling contrast, first divergence, and teacher/student trajectory patching.",
        "SkillOpt removes novelty from bounded edits, held-out acceptance, and rejected-edit memory.",
        "TSR, Expert Iteration, AlphaZero-style distillation, and best-of-N teacher selection falsify any universal claim that more search harms learning.",
        "Selective labels, performative prediction, and DAgger supply the mature conceptual parent class; R17 must present itself as a new instance with a new measurement law, not as the discovery of decision-dependent data."
      ]
    },
    "recommendation": "REVISE_BEFORE_ANY_EXECUTION. Do not stop yet, but narrow the paper to the mechanism-level serving-induced observation-kernel claim; add SkillCAT and TopoCurate as mandatory baselines; make the identity independence-free; freeze the mixed-event intervention and disjoint family partition; replace the old R3 runner; and treat CADP as optional unless it beats the simpler Rejected-Witness arm under matched budgets.",
    "single_sentence_verdict": "R17 is not novel as contrastive failure-based skill editing, but it may still be novel as a causal and predictive study of how winner-only serving over a shared search pool censors an external persistent learner—provided the same-pool intervention and prospective Gamma-times-delta law survive SkillCAT-style controls.",
    "strongest_direct_reduction": "SkillCAT is the strongest direct reduction. It already combines same-task multi-rollout success/failure pairing, meaningful divergence extraction, skill-editable lesson generation, and replay validation in a persistent external skill pipeline. If R17's empirical effect is reproduced by a source-faithful SkillCAT-style contrast baseline without needing the serving-selection causal chain, then R17 becomes an application of SkillCAT plus a selective-labels interpretation rather than a new mechanism.",
    "theory_attacks": [
      "The binary identity is exact only for the event {precommitted rollout fails, at least one other rollout succeeds}; it does not by itself establish learning harm. The paper must not slide from visibility loss to skill loss without independently estimating delta.",
      "The i.i.d. Bernoulli curve and p*(K) are only a reference model. Correlated rollouts, shared prompts, shared latent mode, verifier quantization, and non-exchangeable rollout generation can move the empirical Gamma far from the analytic curve.",
      "The continuous-verifier layer-cake identity is mathematically valid for max versus a fixed coordinate, but real selectors may use verifier ensembles, tie-breaking, constraints, or non-score rules; then the identity must be re-derived for the actual selector rather than assumed.",
      "Gamma times delta is exact only if the alternative projection differs from winner-only exclusively inside the preregistered mixed rescue event. If CADP also changes all-fail or all-success handling, the factorization becomes an estimand of a bundled intervention, not the clean mechanism.",
      "The family-level sum requires a mutually exclusive precommitted partition of mixed pools. Overlapping failure tags, post-hoc family assignment, or multiple deficiencies per trajectory will double-count pools and destroy calibration.",
      "The intermediate-difficulty peak is a modeling assumption under the one-parameter i.i.d. specialization, not a theorem about natural task distributions. Difficulty mixture and family heterogeneity can flatten, shift, or eliminate the peak.",
      "Data processing gives only I(Z; winner-only) <= I(Z; full pool). It does not imply greater value of information for a bounded LLM updater with finite context, attention failures, or validation-gated patch constraints.",
      "The theory currently assumes the updater mapping U is stable enough that one-step cloned effects predict longitudinal evolution. Compounding edits, validation-gate drift, and skill-interference can break that bridge."
    ],
    "thesis_reduction_verdict": "Partially reducible but not fully. The broad phenomenon is already covered by selective labels, performative prediction, DAgger, search distillation, and failure-feedback skill evolution. The narrower residual—serving-time winner selection over a shared search pool causally censoring an external persistent skill updater, with an exact rescue-censoring law and same-pool intervention—has not been shown to be directly reduced by the supplied sources."
  },
  "round": 1
}
{
  "requested_model": "deepseek-v4-pro",
  "resolved_model": "deepseek-v4-pro-ga-260813",
  "review": {
    "causal_identification_adjudication": "The central causal claim is only identified by the F2 cloned-state exact-same-pool intervention. The one-step clone design identifies the effect of changing the learning projection g(T_K) while holding the acting winner fixed, but it does not identify the longitudinal claim that repeated winner-only updates cause weaker frozen skill than L/L. The longitudinal claim requires a different estimand: the difference in frozen skill after multiple rounds of winner-only versus L/L updates, which is confounded by skill-state divergence after the first update. The paper must not conflate the one-step projection effect with the longitudinal reversal. The precommitted rollout-0 arm is not a no-censoring baseline; it is a different observation kernel. The identity V_pre = 1-p is a modeling assumption about what the learner would see, not an observed quantity. The acting invariance validator requires deterministic winner selection given the pool; any stochasticity in the verifier or selector breaks the exact-same-pool claim. The family overlap problem is unsolved: no operational rule is given for assigning a mixed pool with multiple failure types to a single family, so the sum over z of Pr(M, Z=z) × delta_z is not identified without a frozen disjoint partition.",
    "concessions_to_other_review": [
      "The other review is correct that the mutual-information quantity D_g = I(Z; g(T_K) | x, S_t) is decorative outside the controlled suite and should not be presented as a measured mechanism.",
      "The other review is correct that the continuous-verifier layer-cake identity must be re-derived for the actual selector if the selector uses verifier ensembles, tie-breaking, constraints, or non-score rules.",
      "The other review is correct that the longitudinal reversal can be confounded by skill-state divergence after the first update, and that the paper must separate first-update causal effects from path-dependent evolution effects.",
      "The other review is correct that held-out validation gating can itself preferentially accept patches from certain evidence types, and that acceptance rate, patch type, and rejection memory must be reported.",
      "The other review is correct that the i.i.d. Bernoulli curve and p*(K) are only a reference model, and that correlated rollouts, shared prompts, shared latent mode, verifier quantization, and non-exchangeable rollout generation can move the empirical Gamma far from the analytic curve."
    ],
    "experimental_leakage_risks": [
      "Held-out validation gating can preferentially accept patches from certain evidence types, making the gate part of the treatment rather than a neutral filter.",
      "If frozen evaluation uses tasks related to the evolution tasks by workbook, template, or failure family, the estimated future-skill gain may be instance memorization rather than reusable skill learning.",
      "The prospective prediction F3 is vulnerable to outcome-driven family selection: if held-out families are chosen after seeing which families show large Gamma or delta in development, the prediction is not prospective.",
      "The family overlap problem: without a mutually exclusive precommitted partition of mixed pools, overlapping failure tags double-count pools and destroy calibration of the Gamma × delta sum.",
      "The rejected-witness rule must be frozen before outcomes; choosing the most informative, hardest, or representative failure after seeing trajectories reintroduces outcome-dependent selection and can manufacture delta.",
      "The old R3 runner is not an executable R4 implementation: it uses an independent K=1 shadow rather than a same-pool precommitted rollout-0, and it forbids nonselected failures from updater input, which is the opposite of the R4 Rejected-Witness arm."
    ],
    "novelty_adjudication": "The irreducible novelty is narrower than either review fully states. It is not 'failure feedback is useful' (reduced by Rethinking Self-Evolving Agent Skills), not 'success/failure contrast editing' (reduced by SkillCAT), not 'outcome filtering discards branch structure' (reduced by TopoCurate), and not 'search can teach more' (reduced by TSR/Expert Iteration). The only surviving novelty is the coupled package: (1) an independence-free identity linking acting gain to winner-only failure-visibility loss on the same search pool, (2) an exact-same-pool, fixed-acting-winner cloned intervention that changes only the learning projection, and (3) prospective prediction of held-out frozen-skill deficits from pre-outcome censoring mass times diagnostic value. This package is not reduced by any cited work. However, the package is currently a design, not a result. The novelty is conditional on the F2 cloned-state projection-null experiment passing. If SkillCAT-style contrast explains the full effect without the serving-selection causal chain, the paper is an application, not a mechanism.",
    "revised_recommendation": "REVISE_AND_NARROW, with a conditional STOP. The paper should be reframed as a mechanism-level causal study of serving-induced selective trajectory logging in persistent self-evolution, with the exact rescue-censoring identity as a definitional tool, not a theorem. The CADP method should be demoted to a simple Rejected-Witness baseline unless the contrast packet beats it under matched budgets. The paper must not claim novelty for success/failure pairing, first divergence, bounded editing, replay validation, or rejected-edit memory. The decisive F2 cloned-state projection-null experiment must pass before any longitudinal or prospective claims are made. The paper must freeze a mutually exclusive failure-family partition before outcomes, and must precommit the rejected-witness rule before outcomes. If SkillCAT-style contrast explains the full effect without the serving-selection causal chain, the paper should be reduced to an application or stopped. The old R3 runner must be replaced with a new same-pool projection runner before any execution.",
    "selective_labels_or_distillation_reduction": "R17 is a specialized instance of selective labels, performative prediction, and DAgger. The selective-labels structure is: a decision rule (best-of-K winner selection) induces an observation distribution (winner-only) that feeds back into future behavior (persistent skill update). The performative-prediction structure is: the deployed policy (acting selector) alters the future data distribution (updater-visible experience). The DAgger structure is: sequential decisions induce the observation distribution used for learning. R17 does not discover a new general phenomenon; it provides a specific measurement law (the rescue-censoring identity) and a specific causal intervention (same-pool projection change) for the self-evolving-agent instantiation. The paper must acknowledge this and not claim to discover decision-dependent data. The distillation reduction is also direct: TSR, Expert Iteration, AlphaZero-style distillation, and best-of-N teacher selection already show that search can improve learning when the learner sees the rich search object. R17's claim is conditional on the learning projection, not on search budget.",
    "single_sentence_verdict": "The paper has a narrow but potentially real mechanism-level novelty—serving-time winner selection endogenously censoring diagnostic failures from a persistent updater, with an exact rescue-censoring identity and a same-pool projection intervention—but it is currently buried under method components that are already published, the central causal claim is only testable through a single decisive cloned-state projection-null experiment that has not been run, and the paper must survive a source-faithful SkillCAT-style contrast baseline before any novelty claim is defensible.",
    "strongest_attack_on_other_review": "The other review's strongest direct reduction is SkillCAT, but this is a method collision, not a mechanism collision. SkillCAT uses success/failure contrast as an input to a skill editor; it does not study whether the serving-time selector endogenously removes the failure evidence before any contrast method can see it. The other review therefore attacks the wrong novelty boundary: it treats the paper as a contrastive-editing method paper, when the only defensible residual is the selection-induced observation kernel. A SkillCAT baseline cannot falsify the censoring law or the same-pool projection intervention, because SkillCAT operates on whatever evidence is already visible; it does not model the mapping from acting selection to updater-visible distribution. The other review's kill experiment is also weaker than it appears: it compares winner-only to rejected-witness, but if the rejected witness is chosen by a frozen rule that is itself outcome-dependent (e.g., 'most informative failure'), the experiment reintroduces the exact selection bias the paper claims to identify. The other review does not require the rejected-witness rule to be precommitted before outcomes in its kill experiment, which is a material gap.",
    "strongest_baseline": "The strongest baseline is a source-faithful SkillCAT-style same-task success/failure contrast baseline, run on the same pools and same updater, but without the serving-selection causal chain. This baseline directly tests whether the effect is explained by contrastive editing alone, independent of the censoring mechanism. If SkillCAT-style contrast reproduces the full effect, the paper is an application of SkillCAT plus a selective-labels interpretation. The second strongest baseline is the duplicated-winner token-matched control, which tests whether the effect is explained by updater context budget rather than diagnostic evidence. The third is the random-pair control, which tests whether the effect is explained by mere diversity of evidence rather than outcome-grounded divergence. TopoCurate is a representation/selection collision, not a baseline, because it operates on training-data selection for parametric tool-agent training, not on serving-time observation kernels for an external persistent updater.",
    "theoretical_assumption_adjudication": "The independence-free identity A_K - A_1 = Pr(Y_1=0, max_i Y_i=1) is mathematically exact and follows from the definition of the rescue-censoring event. It is not a scientific discovery; it is a definitional tool. The i.i.d. Bernoulli specialization and the intermediate-difficulty peak p*(K) are elementary order-statistic calculations that hold only under the one-parameter i.i.d. model. The correlated-rollout prediction that heterogeneity reduces Gamma_K is a Jensen's inequality observation about concavity of (1-theta) - (1-theta)^K; it is mathematically true but provides no quantitative prediction without a model of the heterogeneity distribution. The continuous-verifier layer-cake identity is a standard layer-cake representation and adds no empirical content beyond the binary case unless a threshold policy is actually used. The Gamma × delta factorization is exact only under the gated-projection construction where the alternative projection equals winner-only outside the mixed event M; it is a tautological decomposition whose scientific content is entirely in whether delta_z is positive and predictable. The information-theoretic statement I(Z; g_win(T_K)) <= I(Z; T_K) is a direct consequence of the data-processing inequality and is vacuous as a scientific claim for a fixed LLM updater."
  },
  "round": 2
}
{
  "requested_model": "kimi-k3",
  "resolved_model": "kimi-k3",
  "review": {
    "causal_identification_adjudication": "Both reviews agree the decisive experiment is the cloned-state exact-same-pool projection-null test. Both agree the key threats are: acting invariance violations, outcome-dependent selection of the rejected witness, family overlap, and the gap between one-step and longitudinal estimands. The other review adds two sharp points I underweighted: (1) rollout-0 is not a no-censoring counterfactual but a different observation kernel, and (2) the one-step clone design cannot identify the longitudinal causal claim. I add two points the other review underweighted: (1) held-out validation gating can itself preferentially accept patches from certain evidence types, making the gate part of the treatment, and (2) frozen evaluation tasks related to evolution tasks by workbook, template, or family leakage can turn the estimated future-skill gain into instance memorization. The union of both reviews' attacks defines the identification burden. The design survives only if all of these are addressed in the R4 contract.",
    "concessions_to_other_review": [
      "The other review is correct that the one-step cloned-state intervention cannot identify the longitudinal causal estimand. The dossier itself acknowledges this, but the other review states it more sharply: the one-step clone design tests a single-update projection effect, and the multi-round claim requires a separate causal argument about path-dependent skill evolution. I concede this is a real identification gap that my Round-1 review mentioned but did not emphasize enough.",
      "The other review is correct that rollout-0 is not a clean 'no-censoring' counterfactual. It is generated under the same search policy and skill state, so it is a different observation kernel, not an absence of censoring. The identity V_pre = 1-p is a modeling assumption about what the learner would see under a precommitted branch, not an observed quantity. I concede this framing is more precise than my Round-1 treatment.",
      "The other review is correct that the family overlap problem is not operationally solved. The dossier asserts a mutually exclusive partition is necessary but gives no rule for assigning a mixed pool with multiple failure types to a single family. Without this, the sum over z is not identified. I concede this is a concrete gap, not just a theoretical concern.",
      "The other review is correct that delta_z is conditional on the updater implementation. If the updater's behavior depends on contrast packet format or update order, delta_z is not a stable property of the failure family. I concede the paper must either fix the updater and report delta_z as conditional, or acknowledge the mechanism does not generalize across updaters.",
      "The other review is correct that the information-theoretic statement I(Z; g_win) <= I(Z; T_K) is vacuous as a scientific claim. It is a direct consequence of data processing for deterministic coarsening and says nothing about whether a bounded LLM updater benefits. I concede this should be removed or explicitly labeled as non-contributing intuition, consistent with my own Round-1 'pretty but empty' assessment of D_g."
    ],
    "experimental_leakage_risks": [
      "Frozen evaluation tasks related to evolution tasks by workbook, template, or failure-family leakage can turn the estimated future-skill gain into instance memorization rather than reusable skill learning.",
      "Held-out validation gating can preferentially accept patches from certain evidence types, making the gate part of the treatment. Acceptance rate, patch type, and rejection memory must be reported by arm.",
      "Post-hoc family redefinition after seeing which families show large Gamma or delta in development destroys the prospective claim. The dossier requires pre-outcome freezing but does not specify a mechanism to prevent post-hoc redefinition.",
      "Overlapping failure tags or multiple deficiencies per trajectory can double-count mixed pools and destroy calibration of the Gamma times delta sum.",
      "Skill-state divergence after the first update means later high-K pools are no longer the same across arms. The paper must separate first-update causal effects from path-dependent evolution effects.",
      "Treating rollouts, patches, tasks, or repeated endpoint calls as independent n invalidates uncertainty estimates. The scientific unit must remain complete independent evolution streams or cloned learned-skill states.",
      "The old R3 runner's independent shadow is not the R4 same-pool precommitted rollout-0. Using it would silently change the causal estimand."
    ],
    "novelty_adjudication": "Both reviews converge on the same irreducible novelty: the coupled package of (1) an independence-free rescue-censoring identity linking acting gain to winner-only failure-visibility loss on the same search pool, (2) an exact-same-pool, fixed-acting-winner cloned intervention that changes only the learning projection, and (3) prospective prediction of held-out frozen-skill deficits from pre-outcome censoring mass times diagnostic value. Neither review defends CADP, contrastive packets, or failure usefulness as novel. The disagreement is on the strongest reduction: the other review picks TopoCurate, I pick SkillCAT. The dossier's own audit labels SkillCAT a 'direct method collision' and TopoCurate a 'representation/selection collision.' SkillCAT is the stronger reduction because it shares the external persistent-skill pipeline architecture. TopoCurate preempts the general claim that success filtering loses information, but SkillCAT preempts the specific method components. Both must be mandatory baselines. The residual novelty survives only if the serving-selection causal chain, the exact identity, and the prospective law are independently established and not reproduced by a SkillCAT-style contrast baseline.",
    "revised_recommendation": "REVISE_BEFORE_ANY_EXECUTION. Narrow the paper to the mechanism-level serving-induced observation-kernel claim. Add SkillCAT and TopoCurate as mandatory baselines, with SkillCAT as the strongest direct reduction. Make the identity independence-free. Freeze the mixed-event intervention and disjoint family partition before outcomes. Replace the old R3 runner with an exact-same-pool prefix runner. Treat CADP as optional unless it beats the simpler Rejected-Witness arm under matched budgets. Address the one-step to longitudinal gap explicitly: either run the longitudinal experiment with proper causal identification or downgrade the claim to one-step projection effects. Do not present the i.i.d. curve, the MI bound, or the layer-cake identity as empirical results. If the cloned-state projection-null experiment fails, STOP.",
    "selective_labels_or_distillation_reduction": "R17 is a specialized instance of selective labels, performative prediction, and DAgger. The dossier acknowledges this. The residual claim is not the discovery of decision-dependent data but a specific measurement law and causal intervention for the case where the decision is best-of-K serving selection over a shared search pool and the learner is an external persistent skill updater. This residual is narrow but not fully reduced by the supplied sources. However, if the paper is framed as 'search can teach less' without the exact identity, same-pool intervention, and prospective law, it is fully reduced by the parent class. The paper must present itself as a new instance with a new measurement law, not as the discovery of decision-dependent data.",
    "single_sentence_verdict": "R17 is not novel as contrastive failure-based skill editing, but it may still be novel as a causal and predictive study of how winner-only serving over a shared search pool censors an external persistent learner — provided the same-pool intervention, the independence-free identity, and the prospective Gamma-times-delta law survive SkillCAT-style controls and the one-step to longitudinal identification gap is closed.",
    "strongest_attack_on_other_review": "The other review's 'strongest direct reduction' choice of TopoCurate is wrong on the dossier's own collision audit. TopoCurate is a representation/selection collision for parametric tool-agent training: it argues outcome filtering discards branch structure and uses topology for SFT/RL data selection. It does not operate on an external persistent skill updater, does not have a serving-time acting/learning projection split, and does not produce a frozen-skill endpoint. SkillCAT is the stronger reduction because it already combines same-task multi-seed success/failure pairing, first-divergence extraction, contrastive skill editing, and replay validation in a persistent external-skill pipeline — the exact pipeline architecture R17 uses. If a source-faithful SkillCAT-style contrast baseline reproduces the effect without the serving-selection causal chain, R17 collapses to an application. The other review also overreaches by calling the identity 'a trivial algebraic rearrangement' with 'no explanatory power.' That is correct as pure algebra but misses the point: the identity's value is not mathematical depth but that it pins a falsifiable, measurable event — the rescue-censoring mass — that can be estimated pre-outcome and used prospectively. Calling it trivial is a rhetorical move that would also dismiss most useful measurement identities in causal inference. Finally, the other review's deeper scientific object ('outcome-dependent observation kernels in sequential decision-feedback loops') is so general it subsumes selective labels, performative prediction, and DAgger — which the dossier already lists as mature conceptual reductions. Proposing a parent class that is already acknowledged as a reduction is not a deeper object; it is a relabeling.",
    "strongest_baseline": "SkillCAT is the strongest baseline. It already combines same-task multi-seed success/failure pairing, meaningful divergence extraction, skill-editable lesson generation, and replay validation in a persistent external skill pipeline. A source-faithful SkillCAT-style contrast baseline, run on the same pools with the same updater and validation gate, is the mandatory control. If it reproduces the full effect without the serving-selection causal chain, R17 becomes an application of SkillCAT plus a selective-labels interpretation. TopoCurate is a secondary baseline for the general claim that branch structure matters, but it does not share the external persistent-updater architecture and is therefore a weaker direct reduction.",
    "theoretical_assumption_adjudication": "Both reviews agree the binary identity is exact only for the rescue-censoring event and does not by itself establish learning harm. Both agree the i.i.d. Bernoulli curve and p*(K) are only a reference model. Both agree the continuous-verifier layer-cake is mathematically valid but adds no empirical content. Both agree Gamma times delta is exact only under the gated-projection construction. Both agree the information-theoretic statement is vacuous. The other review is more aggressive in calling the identity 'trivial' and the factorization 'tautological.' I disagree with the rhetoric but not the substance: the identity is algebraically simple, but its value is as a measurement tool, not a theorem. The factorization is tautological as a decomposition, but the scientific content is whether delta_z is positive and predictable, which is an empirical claim. Both reviews agree the theory is currently underidentified outside the controlled suite and that the paper must not present the i.i.d. curve or the MI bound as empirical results."
  },
  "round": 2
}

Return exactly one JSON object and no markdown, using this shape:
{
  "central_scientific_object": "",
  "single_causal_chain": "",
  "strongest_theoretical_prediction": "",
  "decisive_intervention": "",
  "mechanism_derived_method": "",
  "explicit_stop_condition": "",
  "claims_to_delete": [
    ""
  ],
  "recommendation": "",
  "single_sentence_verdict": ""
}

INDEPENDENCE FLAG: independent=false; exposed_to_other_review=true; exposure_scope=round1_and_round2_panel.

FULL DOSSIER START

===== SOURCE FILE: consultations/e2-r17-search-projection-censoring-literature-synthesis-20260825.md =====
# E2-R17 文献综合与重大重构：Search-Projection Censoring

日期：2026-08-25

状态：DESIGN-ONLY；不构成实验授权，不改写 R16，不覆盖已冻结 F0-R2 / F0-R3。

候选标题：**When Better Search Teaches Less: Search-Projection Censoring in Self-Evolving Agents**

候选副标题：**Act from the Winner, Learn from the Search Set**

## 0. 本轮结论

原来的“Compute Shielding”直觉仍有价值，但表述过宽，也会被已有反例直接击穿：Expert Iteration、AlphaZero-like distillation、TSR 等工作都说明，更多 search 完全可能产生更好的训练数据并改善后续策略。因此，不能把论文写成：

> more test-time compute improves acting but harms learning.

真正更精确、可守住、也更有机制深度的科学对象是：

> **Test-time search 生成的是一个候选集合或搜索树；系统随后需要分别决定“给用户执行哪条轨迹”和“给 persistent learner 看哪部分搜索证据”。现有 self-evolving skill pipeline 往往把二者隐式绑定为同一个 winner-only projection。这个绑定会在 search 成功救回任务时，系统性删掉暴露 reusable deficiency 的失败分支。**

新的核心不是 compute amount，而是：

```text
search object / rollout pool T_K
          ├── acting projection a(T_K)   -> served winner
          └── learning projection g(T_K) -> updater evidence
```

现有默认：`g = a = winner-only`。

论文要证明：

1. acting-optimal projection 与 learning-optimal projection 一般不相同；
2. winner-only projection 会产生可精确预测的 selection censoring；
3. 当被删掉的失败比 winner 更有 reusable diagnostic value 时，在线 performance 上升但 frozen-skill quality 下降；
4. 通过 act–learn dual projection，可以在不降低 high-compute acting、且不增加 actor rollout 数量的情况下恢复 persistent learning。

一句话主张：

> **Better search does not inherently teach less; learning from only what search serves can.**

## 1. 文献给出的关键约束

### 1.1 Snell et al.：学习“统一科学变量”，不是复制 baseline 列表

`Scaling LLM Test-Time Compute Optimally...` 把 parallel search、sequential revision、verifier search 压进统一的 compute-allocation 问题，并证明最优策略随 prompt difficulty 改变。R17 应学习其方法论：先找到一个统一对象，再让公式、干预、算法和工程决策从该对象自然长出。

R17 的统一对象不再是 `Skill vs. Compute`，而是 `Search-to-Learning Projection`：test-time search 产生的完整搜索对象如何被压缩成 persistent updater 的观测。

### 1.2 Rethinking Self-Evolving Agent Skills：failure feedback 有价值，但尚未问 failure 为什么消失

该工作发现：388 个 candidate 中只有 55 个成为 byte-distinct validation new best；failure-containing 条件的 yield 高于 success-only，且 11 个最终选中 skill 全部来自包含 failure feedback 的条件。它还发现 Parallel Sampling 在 SearchQA 几乎追平 evolved skill，却在 SpreadsheetBench 上仍落后约 30.96pp。

这给 R17 两个直接启发：failure 可能是 skill evolution 的主要学习信号；skill/search 关系存在 substrate-specific regime，不能写成普遍单调规律。R17 的 residual 是继续追问 executor 的 best-of-K search 是否在 updater 之前内生地删掉了这些 failure。

### 1.3 TSR / Expert Iteration / AlphaZero-like distillation：search 本身不必然损害 learning

TSR 把 beam、lookahead、best-of-N 移到 train-time rollout construction，并在适中预算下改善 agent RL；只有 search 太强、search-induced distribution 与 policy 偏离过大时才退化。Expert Iteration 与 AlphaZero-like 系统更直接地把 search 视为 policy-improvement operator，并把 richer search targets（如 visit-count policy、成功路径或 state-action 数据）蒸馏回 policy。

这组文献构成 R17 的 strongest counterexample：如果 learner 看到了 search 产生的丰富对象，更多 search 可以帮助学习。因此，R17 必须把“compute harmful”改成“winner-only search projection can be harmful”。

### 1.4 Search-E1 / CRAFT / SGCD / OVCSD：不能声称“首次利用 sibling contrast”

这些工作已经使用 sibling successful/failed rollouts、privileged context、counterfactual credit、prefix-tree divergence 或 outcome-verified continuation，为 model-weight RL / self-distillation 提供更密集的 credit。

R17 不能把 novelty 写成“首次学习 rejected rollouts”“首次对比 success 与 failure”“首次从 sibling trajectory 提炼经验”。可守住的边界是：

> **我们研究的不是如何给 model weights 做 token-level credit，而是 acting selector 如何改变 external persistent skill updater 的可见经验分布；我们给出一个 order-statistic censoring law、同池 causal projection intervention，以及不增加 actor rollout 的 dual-channel skill update。**

### 1.5 SKILL-KD / SkillOpt：借鉴训练纪律，不重复 scientific object

SKILL-KD 已经把 student failure 与 stronger teacher trajectory 的差异蒸馏成 textual skill patch。SkillOpt 已经把 textual skill 当作外部可训练状态，引入 bounded edits、held-out validation gate、rejected-edit buffer、slow/meta update。

R17 应直接借鉴 bounded add/delete/replace、held-out acceptance gate、rejected patch memory、train/selection/test 隔离。但 R17 的 teacher 不是外部更强模型；证据来自同一 actor 的 search pool，真正问题是 winner-only logging/projection 导致的 selection censoring。

### 1.6 Selective labels / performative prediction / DAgger：理论母体，不是最终 novelty

Selective-label work研究“决策决定哪些 outcomes 可被观察”；performative prediction 研究“部署决策改变未来数据分布”；DAgger 强调 learner 应在其诱导的状态分布上获得监督。

R17 是这一结构在 self-evolving LLM agents 中的具体实例：

```text
search/selection policy
    -> which trajectory becomes observable to updater
    -> which persistent skill is learned
    -> future behavior
```

论文应承认该理论母体，不声称发现普遍意义上的 censoring。

### 1.7 RLVR pass@k inversion：最接近的“方向反转”类比

近期 RLVR 工作发现 pass@1 可以上升而 high-k coverage 下降，尤其发生在 boundary prompts：训练把稀有正确模式从 policy support 中挤掉。

R17 的方向相反但结构同构：RLVR inversion 是 training update 改变 future inference support；R17 是 inference selection 改变 future training support。这提示主结果不能只报平均 accuracy，而必须研究 support/diagnostic coverage 的丢失发生在哪个 regime。

## 2. 新的统一形式化

### 2.1 Search object 与双投影

给定 task `x`、persistent skill state `S_t`、search budget `K`：

\[
\mathcal T_K \sim Q_K(\cdot\mid x,S_t).
\]

`T_K` 可以是 K 个独立 rollout、beam tree、sequential revision trace 或其他 search object。

acting projection：

\[
\tau^+ = a(\mathcal T_K).
\]

learning projection：

\[
E_t = g(\mathcal T_K).
\]

persistent update：

\[
S_{t+1}=U(S_t,E_t).
\]

当前 acting value：

\[
A(a,K)=\mathbb E[R(a(\mathcal T_K))].
\]

统一低 compute、冻结 skill 后的 learning value：

\[
J(S_{t+1})=\mathbb E_{x'\sim D_{test}}[R(\pi_L(x';S_{t+1}))].
\]

核心区别：`A` 主要依赖 acting projection `a`，future skill quality 依赖 learning projection `g`，没有理论理由要求 `a*=g*`。

### 2.2 Winner-only coupling

许多 pipeline 实际使用：

\[
g_{win}(\mathcal T_K)=a(\mathcal T_K)=\tau^+.
\]

这意味着 search pool 中所有 nonserved branches 对 updater 都是 missing-not-at-random；它们是否缺失由 verifier outcome 与 selector 共同决定。

### 2.3 Diagnostic retention

设 `Z` 表示可复用 deficiency family，例如忘记 materialize formula value、修改 input file、漏掉 schema conversion、未做 verification、错误 sheet/range、tool sequence 错误。

理论上可定义：

\[
D_g=I(Z;g(\mathcal T_K)\mid x,S_t),
\]

但真实 benchmark 不应把 mutual information 当装饰性指标。controlled suite 中 Z 由 deterministic validator 精确给出，可估 exact diagnostic coverage/MI；real benchmark 只报告可审计的 failure-family coverage、rescue event 与 patch-rule coverage。

## 3. 核心理论：Rescue–Censoring Identity

### 3.1 Binary verifier 模型

设每条独立 rollout 成功概率为 `p`，K 条 rollout 相互独立。

\[
A_K(p)=1-(1-p)^K
\]

是 best-of-K acting success；winner-only updater 看到 failure 的概率为：

\[
V_K^{win}(p)=(1-p)^K.
\]

预先指定 rollout-0 作为 learning branch，其 failure visibility 不随 K 改变：

\[
V_K^{pre}(p)=1-p.
\]

于是：

\[
\boxed{A_K(p)-A_1(p)=V_K^{pre}(p)-V_K^{win}(p)=\Gamma_K(p)}
\]

其中：

\[
\Gamma_K(p)=(1-p)-(1-p)^K=(1-p)[1-(1-p)^{K-1}].
\]

解释：在该最小模型中，best-of-K 相对 single rollout 获得的每一单位 acting gain，恰好对应一单位从 winner-only learning channel 中消失的 single-rollout failure mass。等价事件是：predesignated rollout fails，且其余 K-1 条中至少一条成功。

### 3.2 Intermediate-difficulty law

`Gamma_K(p)` 在：

\[
\boxed{p^*(K)=1-K^{-1/(K-1)}}
\]

处最大。

| K | p* |
|---:|---:|
| 2 | 0.500 |
| 4 | 0.370 |
| 8 | 0.257 |
| 16 | 0.169 |

因此，shielding 最强的不是极易题，也不是完全不会的题，而是“单次不稳定、search 经常能救回”的 boundary/intermediate regime。可冻结预测：winner-only 与 diagnostic projection 的 frozen-skill gap 应在中等 single-rollout solvability 上最大，并在 floor/ceiling 两端减弱。

### 3.3 Visibility 不等于 learning value

仅证明 failure 被隐藏还不够。成功轨迹也可能比失败更适合学习。设 mixed group 中：

- `ell_F`：从 failure witness 更新后的期望 future gain；
- `ell_S`：从 served success 更新后的期望 future gain；
- `delta = ell_F - ell_S`：diagnostic advantage。

在简化齐次条件下：

\[
\boxed{\Delta_{learn}^{pre-win}(K,p)=\Gamma_K(p)\,\delta.}
\]

真正的 shielding risk 是：

\[
\boxed{\mathcal R_{shield}(K,z)=\Gamma_K(p_z)\,\delta_z.}
\]

三种 regime：

1. `Gamma≈0`：没有 selection censoring；
2. `Gamma>0, delta>0`：失败 witness 更适合形成 reusable correction，winner-only harms learning；
3. `Gamma>0, delta<=0`：success/search trajectory 更有价值，search 可以改善 learning，符合 TSR/Expert Iteration 类型结果。

机制深度由此收敛为：**selection censoring mass × censored evidence 的 reusable value**。

### 3.4 Prospective mechanism prediction

在 calibration split 上估计 `p_z` 与 cloned-state intervention 得到的 `delta_z`，在 longitudinal experiment 前冻结：

\[
\hat{\mathcal R}_{shield,z}=\Gamma_K(\hat p_z)\hat\delta_z.
\]

随后 prospectively 预测 held-out failure families/difficulty cells 的 reversal、方向和 gap 排序。只有能预测 unseen cells，机制才不只是事后解释。

## 4. Search topology × learning projection

原“Compute Shielding”会被 TSR 反例击穿。新版明确区分两个轴。

### Axis A：search topology

- Parallel best-of-K：失败分支彼此独立，winner selection 会整支删除 nonwinner trajectories；
- Sequential refinement：早期错误可能保留在同一 conversation/history 中；
- Beam/tree search：可能保留 partial-state statistics，也可能只输出 final path。

### Axis B：learning projection

- winner/final-only；
- precommitted branch；
- rejected witness；
- full-history/full-tree；
- contrastive packet。

关键预测：shielding 不是由 parallel compute 单独决定，而由 `topology × projection` 的组合决定；parallel + winner-only 应最强，sequential + full-history 应显著减弱。

| | winner/final-only | history/branch-preserving |
|---|---|---|
| Parallel search | 高 censoring 预测 | actor 相同，learning recovery 预测 |
| Sequential refinement | 若只存 final 仍可能 censor | 若保存 correction history，censoring 明显减弱 |

必须 match LLM calls、input/output tokens、tool calls、verifier access；sequential depth 与 parallel width 分开记账。

## 5. 方法闭环：Censor-Aware Dual Projection（CADP，暂名）

### 5.1 原则

不要让 served trajectory 自动成为唯一 training trajectory。

```text
Acting channel:  serve the verifier-selected winner.
Learning channel: preserve evidence that identifies what the base actor still needs to learn.
```

### 5.2 三层实现

#### I. Precommitted Shadow Projection（因果识别器）

从同一个 K-rollout pool 中，在任何 outcome 前指定 rollout-0：

- acting：serve best-of-K；
- learning：feed rollout-0；
- actor compute：与 H/H 完全相同；
- updater evidence volume：仍是一条 trajectory；
- 不需要额外 shadow call。

它不是最终最优方法，而是最干净的 causal intervention：只改变 learning observation kernel。

#### II. Rejected-Witness Projection（strong simple baseline）

在 mixed group 中选择一个非 served failure witness；在 all-fail group 中选择预先冻结规则下的代表 failure；在 all-success group 中用 winner 或 skip。

它检验是否只要利用 high-K pool 中现成 rejected failure 就足够，不需要额外 counterfactual generation。当前 `H_REJECTED_MINE` 应重命名为 `H/Rejected-Witness`；“hardmine”容易误导为跨任务重采样。

#### III. Contrastive Diagnostic Projection（论文方法）

对 mixed group 构造固定 token budget 的 packet：

```text
- task requirement / common pre-state
- served winner 的最小成功摘要
- one precommitted or frozen-rule failure witness
- first outcome-relevant divergence / verifier failure signature
- instruction: propose one reusable correction; forbid task IDs and instance facts
```

然后：

1. updater 产生 bounded add/delete/replace patch；
2. patch 在 held-out selection split 上验证；
3. 只有严格提升才接受；tie/reject 进入 rejected-edit memory；
4. deployed skill 保持 compact、可审计。

该方法的核心不是“contrastive learning 首次出现”，而是：contrast packet 被 search-projection censoring mechanism 精确触发，只用于 mixed groups，并以 external persistent skill patch 为更新对象。

### 5.3 Censor-aware projection rule

\[
g_{CADP}(\mathcal T_K)=
\begin{cases}
\text{winner-only or no-update}, & \text{all success};\\
\text{representative failure}, & \text{all failure};\\
\text{winner--failure contrast packet}, & \text{mixed group}.
\end{cases}
\]

只有 mixed group 同时满足：search 产生 acting rescue、winner-only 删除可见失败、contrast 存在 outcome-grounded anchor。这避免把方法写成泛化的“大模型反思器”。

### 5.4 Fixed-budget controls

必须加入：winner-only；winner + duplicate winner（token matched）；winner + random nonselected success；failure witness only；random pair；full-pool/full-tree upper bound；contrast without validation gate；contrast with validation gate。

这样才能证明 gain 来自 diagnostic contrast，而不是更多文本或更多 updater tokens。

## 6. 实验体系：从 law 到 causality，再到 longitudinal system

### F0 — 当前静态门禁（已完成，保留）

保留 MindMemOS official clean substrate、SpreadsheetBench Verified-400 exact hashes、K=1 vs K=4、per-rollout receipts/CSV/checkpoints、winner-only/precommitted rollout-0/rejected witness semantics、provider 恢复前 0 scientific outcome。

当前 8-train/8-eval 只允许做 pipeline pilot，不能成为论文主证据。

### F1 — Controlled Procedure Suite：验证 regime law

构造 parameterized Spreadsheet Procedure Suite。它不是为了“制造 high compute 有害”，而是为了提供 independently executable latent deficiency labels。

建议 reusable failure families：

1. preserve source file / copy-before-edit；
2. correct sheet/range targeting；
3. formula materialization；
4. multi-sheet join / key alignment；
5. schema/type conversion；
6. output naming/path；
7. final verification / target-cell check。

每个 family 生成 easy/boundary/hard 三个 complexity regimes、train 与 held-out variants、deterministic task validator、deterministic failure-family validator，并严格分离 instance facts 与 skill rule。

预算采用 nested pools：每个 task 一次生成 Kmax=8 个 rollout，即可离线构造 K={1,2,4,8} prefix，避免重复生成。

F1 检验：

1. empirical `A_K` calibration；
2. rescue-censoring event rate 是否匹配 `Gamma_K(p)`；
3. event 是否在 intermediate p 附近峰值；
4. winner-only projection 的 failure-family coverage 是否按 K 收缩；
5. full pool 中 failure 仍存在，证明是 projection loss，不是 generator support 消失。

### F2 — Cloned-State One-Step Causal Intervention

这是最关键的因果实验，优先于 multi-round。

对同一个 pre-update skill state `S`、同一个 task batch、同一个 K-pool：

```text
clone S into several identical updater states
        ├── apply winner-only evidence
        ├── apply precommitted rollout-0 evidence
        ├── apply rejected-witness evidence
        └── apply contrast packet
```

随后全部 freeze skill，使用 common K=1 executor、same held-out probe，且 probe feedback 永不进入 updater。

candidate pool、acting winner、model、verifier、task、initial skill 全部相同，唯一变化是 `g(T_K)`。

主 estimand：

\[
\Delta_{proj}=\mathbb E[J(U(S,g_1(T_K)))-J(U(S,g_0(T_K)))].
\]

F2 还用于估计每个 failure family 的 `delta_z`，并在 F3 前冻结 shielding-risk prediction。

### F3 — Prospective Mechanism Prediction

使用 F1/F2 development cells 估计：

\[
\hat R_{shield,z}=\Gamma_K(\hat p_z)\hat\delta_z.
\]

对从未进入 F1/F2 的 held-out task templates/workbook families，在 outcome 前写下：哪些 cells 应有 reversal、哪些应无 effect、gap 大小排序。

执行后检验 sign accuracy、rank correlation、predicted-vs-observed calibration，以及 zero-risk cells 是否接近零。

### F4 — MindMemOS × SpreadsheetBench Multi-Round Evolution

五个 arm 从 exact same initial skill SHA 出发：

1. L/L；
2. H/H winner-only；
3. H/precommitted；
4. H/rejected-witness；
5. H/CADP contrast。

每 8 个 evolution tasks 形成一次 source-faithful update。正式实验应有 4–5 evolution batches、多个 independent evolution-stream seeds、每轮后 frozen K=1 held-out probe、final group-disjoint test。

同时画：

\[
R_t^{online}\quad\text{and}\quad J(S_t)^{frozen,K=1}.
\]

headline pattern：

\[
R_{online}^{H/H}>R_{online}^{L/L},
\]

但：

\[
J(S_T^{H/H})<J(S_T^{L/L}),
\]

并且：

\[
J(S_T^{H/CADP})>J(S_T^{H/H})
\]

而 high-compute acting 不下降。

F4 同时记录 SKILL.md exact diff、patch rule × failure-family coverage、accepted/rejected edits、updater input token budget、actor call/token/tool budget、mixed-group rate 与 rescue-censoring events。

### F5 — Topology × Projection

在 matched budget 下比较 parallel best-of-K 与 sequential refinement，以及 winner/final-only 与 full-history/branch-preserving。主要检验 interaction：

\[
(topology\times projection)\rightarrow failure\ retention\rightarrow frozen\ skill.
\]

若 sequential full-history 明显避免 reversal，而 sequential final-only 仍发生，说明核心是 observation projection，而不是“parallel search 天生有害”。

### F6 — 第二 substrate / backbone

只有 F1–F5 主机制成立后，再扩展 ALFWorld/WebShop/coding workflow/SkillEvolBench 中的一个，以及一个不同能力等级 backbone。第二 substrate 的职责是证明机制不只存在于 spreadsheet，不负责救主结论。

## 7. 数据分层与统计设计

### 7.1 四个完全分离的角色

1. **Runtime development pool**：只验证工具、checkpoint、provider、scorer；永不进入科学 claim；
2. **Mechanism calibration pool**：估计 `p_z`、`delta_z`；
3. **Evolution train + validation gate**：产生/选择 skill update；
4. **Held-out probe/final test**：从不送入 updater。

尽可能按 workbook/source/template/failure-family group-disjoint，而不是行级随机切分。

### 7.2 Scientific unit

主 scientific unit 是 one independently seeded complete evolution stream / learned skill state，不是 individual rollout、task repeat、LLM call 或 endpoint row。

### 7.3 Pairing

- 同一 task stream；
- 相同 initial skill SHA；
- 相同 candidate seed index；
- H/H 与 H/projection arms 在 one-step experiment 中共享 exact K-pool；
- longitudinal 中记录 skill divergence，不能假装后续 pools 仍完全相同。

### 7.4 Primary estimands

1. Acting gain：
   \[
   \Delta_A=A_H-A_L.
   \]
2. Winner-only shielding reversal：
   \[
   \Delta_S=J(S_L)-J(S_{H/win}).
   \]
3. Projection rescue：
   \[
   \Delta_P=J(S_{H/CADP})-J(S_{H/win}).
   \]
4. Causal one-step projection effect：
   \[
   \Delta_{clone}=J(U(S,g_{CADP}(T)))-J(U(S,g_{win}(T))).
   \]
5. Topology×projection interaction。

### 7.5 Statistical model

对 binary success 使用 paired hierarchical logistic model，random effects 至少覆盖 evolution stream seed、task/template、failure family；扩展阶段再加入 model/backbone。

同时报告 paired bootstrap CI、run-level effect distribution、AULC（frozen learning curve area）、final frozen score、prospective sign/rank prediction accuracy。

不得把 K 个 rollouts 当作 K 个 independent scientific n。

## 8. Validators

1. **Pool Identity Validator**：one-step clone arms 使用 exact same K-pool hashes；
2. **Projection Validator**：updater input 与预注册 `g(T)` 完全一致；
3. **Acting Invariance Validator**：所有 high-K projection arms serve exact same winner；
4. **No-extra-actor-compute Validator**：precommitted/rejected/contrast 只使用已生成 pool；
5. **Evidence-Budget Validator**：对比 packet 与 token-matched controls；
6. **Failure-Family Validator**：controlled suite 使用 deterministic executable labels；
7. **Skill Leakage Validator**：patch 不得含 task id、cell-specific answer、workbook filename 等 instance facts；
8. **Held-Out Gate Validator**：selection/test tasks 永不进入 updater；
9. **Frozen-Eval Validator**：所有 arms 同 backbone、K=1、temperature、tool harness；
10. **Scientific-Unit Validator**：统计 n 为 independent evolution streams；
11. **Checkpoint Validator**：每 rollout、pool selection、projection packet、skill patch、validation decision、final skill hash 均落 CSV/JSONL；
12. **Resume Validator**：只执行 missing units。

## 9. Kill / downgrade rules

### Kill central thesis

- qualified substrate 上 high-K 无 acting gain；
- winner-only 未降低 diagnostic coverage；
- cloned-state projection intervention 对 future skill 无方向性影响；
- multi-round H/H frozen skill 不弱于 L/L，且 planned replication 一致；
- CADP 不恢复，或恢复来自额外 actor/updater budget；
- prospective risk score 不能预测 held-out regime；
- effect 只在 outcome-selected task subset 出现。

### Downgrade stronger claims

- rejected-witness 与 precommitted/CADP 完全相同：保留“winner-only wastes existing pool evidence”，删除“需要 counterfactual low-C branch”；
- random pair 与 contrast packet 相同：删除“outcome-grounded divergence”机制，只保留“more diverse evidence”；
- winner+duplicate 追平 CADP：删除 diagnostic contrast claim，归因为 updater context budget；
- sequential full-history 与 winner-only 无差异：删除 topology×projection claim；
- failure witness 比 winner 的 diagnostic advantage `delta<=0`：该 family 属于 search-improves-learning regime，不为主 thesis 强行解释。

## 10. 论文主线

### Hook

Test-time scaling 让 agent 通过搜索更多候选并部署更好的结果。Self-evolving agents 又把执行轨迹当作未来 skill 的训练数据。这里存在一个被忽略的假设：

> the trajectory worth serving is also the trajectory worth learning from.

### Phenomenon

best-of-K winner selection 提高 online success，但 winner-only learner 只看到最终被服务的成功轨迹。

### Insight

Search 产生一个 richer object，acting 与 learning 是两个不同 projection。把二者绑定造成 outcome-dependent censoring。

### Law

在 binary verifier 下：

\[
\text{online gain}=\text{single-rollout failure visibility loss}=\Gamma_K(p),
\]

且该 loss 在 intermediate difficulty 最大。

### Mechanism

真正的长期 harm 由：

\[
\Gamma_K(p_z)\times\delta_z
\]

决定：censoring mass 与被 censor evidence 的 reusable value 缺一不可。

### Causal test

同一个 K-pool、同一个 acting winner、同一个 initial skill，只改变 learning projection；随后 common K=1 frozen evaluation。

### Solution

CADP：act from winner；在 mixed search groups 中 learn from winner–failure divergence；bounded patch + held-out gate；不增加 actor rollouts。

### Engineering implication

生产 self-evolving agent 不应只持久化“给用户看到的最终成功轨迹”。Search logs 是 learning substrate，serving policy 与 logging/learning policy 必须解耦。

## 11. 推荐主图

1. **Figure 1 — Dual Projection**：同一 search pool 分成 acting winner 与 learning evidence；winner-only 删除失败分支；
2. **Figure 2 — Rescue–Censoring Law**：`Gamma_K(p)` 随 difficulty/K 的曲线和 `p*(K)`；
3. **Figure 3 — Cloned-State Causal Intervention**：exact same pool，不同 `g(T)`，不同 frozen skill；
4. **Figure 4 — Online/Frozen Reversal**：H/H online 高、frozen learning 曲线低，CADP 同时保留两者；
5. **Figure 5 — Mechanism Prediction**：`Gamma×delta` 对 held-out skill deficit 的预测/校准；
6. **Figure 6 — Method Ablation**：winner-only、duplicate、random、witness、contrast、full-pool 在 fixed budget 下比较。

## 12. Contributions（通过全部 gate 后才允许使用）

1. **Search-to-learning projection formulation**：把 test-time search 明确建模为同时服务 acting 与 persistent learning 的数据生成过程；
2. **Rescue–Censoring Identity and regime law**：给出 online gain 与 winner-only failure visibility loss 的精确关系，以及 intermediate-difficulty peak；
3. **Causal projection evidence**：在 exact same search pools 上只改变 learning projection，证明 winner-only selection 可导致更弱的 persistent skill；
4. **Prospective mechanism prediction**：用 censoring mass × diagnostic advantage 预测 unseen regimes；
5. **CADP**：不增加 actor rollout 的 dual-channel projection，通过 bounded validation-gated skill patches 保留 high-compute acting 与 persistent learning。

## 13. 与当前 F0-R2 / R3 的关系

### 保留

- K=1/K=4 best-of-K；
- MindMemOS + SpreadsheetBench；
- winner-only、precommitted rollout-0、rejected branch；
- frozen K=1 evaluation；
- exact checkpoint/receipt；
- 8-train/8-eval 作为 runtime pilot。

### 修改（须在 provider 恢复前另行生成正式 R4 contract；本文不授权）

- scientific object 从 generic Compute Shielding 改为 Search-Projection Censoring；
- `H/L-shadow` 明确为 same-pool precommitted rollout-0，不是额外 independent call；
- `H/H-hardmine` 改名 `H/Rejected-Witness`；
- 增加 controlled procedure suite；
- 增加 cloned-state one-step causal intervention；
- 增加 `Gamma×delta` prospective prediction；
- contrastive CADP 仅在主机制 gate 后执行；
- multi-round 才是最终 paper evidence，single update 不承担 headline claim。

### 不做

- 不把 R17 塞回 R16 appendix；
- 不以“failure feedback 首次有用”为 novelty；
- 不以“首次利用 sibling rollouts”为 novelty；
- 不写 universal `compute hurts learning`；
- 不在 API 恢复前用 outcome 改 task/failure family；
- 不用更多 benchmark 掩盖主机制失败。

## 14. 关键参考文献（内部索引）

- Snell et al., 2024, `Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters`, arXiv:2408.03314.
- Liu et al., 2026, `Rethinking Self-Evolving Agent Skills`, arXiv:2608.02636.
- Wang et al., 2026, `Rethinking the Evaluation of Harness Evolution for Agents`, arXiv:2607.12227.
- Djuhera et al., 2026, `TSR: Trajectory-Search Rollouts for Multi-Turn RL of LLM Agents`, arXiv:2602.11767.
- Liang et al., 2026, `Search-E1`, arXiv:2605.22511.
- Meng & Chen, 2026, `CRAFT`, arXiv:2606.29476.
- Ding et al., 2026, `Sibling-Guided Credit Distillation`, arXiv:2606.12634.
- Xia et al., 2026, `Outcome-Verified Comparative Self-Distillation`, arXiv:2607.27937.
- Shi et al., 2026, `SKILL-KD`, arXiv:2607.28048.
- Yang et al., 2026, `SkillOpt`, arXiv:2605.23904.
- Wang et al., 2026, `Do Not Waste Your Rollouts`, arXiv:2601.21684.
- Zhou, 2026, `When RLVR Shrinks the Reasoning Boundary`, arXiv:2607.20543.
- Zhang et al., 2026, `On-Policy Distillation with Best-of-N Teacher Rollout Selection`, arXiv:2605.09725.
- Perdomo et al., 2020, `Performative Prediction`, arXiv:2002.06673.
- Ross et al., 2011, `DAgger`, arXiv:1011.0686.
- De-Arteaga et al., 2018, `Learning under selective labels...`, arXiv:1807.00905.


===== SOURCE FILE: generated/e2-r17-search-projection-f0-r4-design-20260825.json =====
{
  "schema_version": "1.0",
  "artifact_type": "scientific-child-design-only",
  "child_id": "E2-R17-SEARCH-PROJECTION-CENSORING",
  "parent_paper_id": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
  "working_title": "When Better Search Teaches Less: Search-Projection Censoring in Self-Evolving Agents",
  "status": "DESIGN_ONLY_NOT_EXECUTION_AUTHORITY",
  "created_at": "2026-08-25",
  "does_not_supersede": [
    "generated/e2-r17-compute-shielding-f0-contract-r2-20260825.json",
    "generated/e2-r17-compute-shielding-f0-r3-gate-20260825.json"
  ],
  "central_question": "When test-time search generates multiple trajectories, can the projection used for serving the current task be learning-suboptimal for a persistent skill updater?",
  "core_insight": "Test-time search is both an inference procedure and a data-generation process. The acting projection selects what is served; the learning projection selects what persistent self-evolution observes. Winner-only coupling can improve current success while censoring reusable deficiencies.",
  "formal_objects": {
    "search_object": "T_K ~ Q_K(. | x, S_t)",
    "acting_projection": "tau_plus = a(T_K)",
    "learning_projection": "E_t = g(T_K)",
    "persistent_update": "S_{t+1} = U(S_t, E_t)",
    "acting_value": "A(a,K) = E[R(a(T_K))]",
    "frozen_skill_value": "J(S) = E_{x'~D_test}[R(pi_L(x';S))]"
  },
  "winner_only_default": "g_win(T_K) = a(T_K)",
  "binary_rescue_censoring_law": {
    "single_rollout_success": "p",
    "best_of_k_success": "A_K(p) = 1 - (1-p)^K",
    "winner_visible_failure": "V_win(K,p) = (1-p)^K",
    "precommitted_visible_failure": "V_pre(K,p) = 1-p",
    "identity": "A_K(p)-A_1(p) = V_pre(K,p)-V_win(K,p) = Gamma_K(p)",
    "gamma": "Gamma_K(p) = (1-p)-(1-p)^K",
    "intermediate_difficulty_peak": "p_star(K) = 1 - K^(-1/(K-1))"
  },
  "learning_value_law": {
    "diagnostic_advantage": "delta_z = expected future gain from failure/contrast evidence minus expected future gain from served-success evidence for reusable family z",
    "shielding_risk": "R_shield(K,z) = Gamma_K(p_z) * delta_z",
    "interpretation": "Search is harmful only when selection censoring is nonzero and the censored evidence has positive reusable learning value. This admits TSR/expert-iteration regimes where richer search evidence improves learning."
  },
  "novelty_boundary": {
    "not_claimed": [
      "failures are useful",
      "first use of sibling rollouts",
      "first contrastive trajectory learning",
      "test-time compute universally harms learning",
      "first selective-label or performative-data phenomenon"
    ],
    "defended_residual": "Causal and predictive study of how best-of-K acting selection censors the experience distribution of an external persistent skill updater, including an exact order-statistic law, same-pool projection intervention, and no-extra-actor-compute dual projection."
  },
  "primary_interventions": {
    "L_L": {
      "acting": "K=1 rollout_0",
      "learning": "rollout_0"
    },
    "H_WINNER": {
      "acting": "best-of-K by frozen verifier",
      "learning": "same served winner"
    },
    "H_PRECOMMITTED": {
      "acting": "same best-of-K winner",
      "learning": "same-pool rollout_0 predesignated before outcomes",
      "extra_actor_rollouts": 0
    },
    "H_REJECTED_WITNESS": {
      "acting": "same best-of-K winner",
      "learning": "pre-frozen representative nonserved failure when a mixed group exists"
    },
    "H_CADP": {
      "acting": "same best-of-K winner",
      "learning": "fixed-budget winner-failure contrast packet on mixed groups plus bounded validation-gated skill patch"
    }
  },
  "method": {
    "name_provisional": "Censor-Aware Dual Projection",
    "abbreviation": "CADP",
    "rule": {
      "all_success": "winner-only or no update",
      "all_failure": "representative failure",
      "mixed": "outcome-grounded winner-failure contrast packet"
    },
    "controls": [
      "winner-only",
      "winner plus duplicate winner token-matched",
      "winner plus random nonselected success",
      "failure witness only",
      "random pair",
      "full-pool upper bound",
      "contrast without validation gate",
      "contrast with validation gate"
    ]
  },
  "experiment_stages": [
    {
      "stage": "F0",
      "purpose": "retain current static substrate/provider/checkpoint qualification",
      "scientific_outcome": false
    },
    {
      "stage": "F1",
      "purpose": "controlled executable procedure suite; validate Gamma_K(p), intermediate-difficulty peak, and exact failure-family coverage",
      "budgets": [1, 2, 4, 8],
      "nested_pool": true
    },
    {
      "stage": "F2",
      "purpose": "cloned-state one-step causal projection intervention using exact same K-pools and initial skill state"
    },
    {
      "stage": "F3",
      "purpose": "freeze Gamma times delta predictions and test sign/rank/calibration on unseen task cells"
    },
    {
      "stage": "F4",
      "purpose": "multi-round MindMemOS plus SpreadsheetBench evolution; measure online acting and common-K=1 frozen-skill curves"
    },
    {
      "stage": "F5",
      "purpose": "compute-matched search-topology by learning-projection interaction: parallel versus sequential; winner/final-only versus history-preserving"
    },
    {
      "stage": "F6",
      "purpose": "one second substrate and one different-capability backbone only after the main mechanism passes"
    }
  ],
  "primary_estimands": {
    "acting_gain": "A_H - A_L",
    "winner_shielding_reversal": "J(S_L) - J(S_H_WINNER)",
    "projection_rescue": "J(S_H_CADP) - J(S_H_WINNER)",
    "cloned_projection_effect": "J(U(S,g_CADP(T))) - J(U(S,g_WIN(T)))",
    "mechanism_prediction": "observed frozen-skill deficit versus preregistered Gamma_K(p_z)*delta_z",
    "topology_projection_interaction": "parallel/sequential by winner/history-preserving interaction"
  },
  "scientific_unit": "one independently seeded complete evolution stream or cloned learned-skill state, not a rollout or model call",
  "data_roles": [
    "runtime development pool",
    "mechanism calibration pool",
    "evolution train and validation-gate split",
    "never-fed held-out probe and final test"
  ],
  "required_validators": [
    "pool identity",
    "projection exactness",
    "acting invariance",
    "no extra actor compute",
    "evidence token budget",
    "deterministic failure-family labels on controlled suite",
    "skill instance-leakage",
    "held-out isolation",
    "common frozen evaluation",
    "scientific-unit integrity",
    "per-unit CSV/JSONL checkpoint",
    "resume missing units only"
  ],
  "kill_conditions": [
    "qualified high-K search has no acting gain",
    "winner-only does not reduce diagnostic coverage",
    "same-pool cloned projection has no effect on future frozen skill",
    "planned multi-round H_WINNER skill is not weaker than L_L",
    "CADP does not recover or recovery is explained by extra budget",
    "Gamma times delta fails prospective held-out prediction",
    "effect requires outcome-driven task or failure-family selection"
  ],
  "downgrade_conditions": [
    "rejected witness matches CADP: retain rollout-recycling claim but drop need for counterfactual branch",
    "random pair matches CADP: drop outcome-grounded divergence claim",
    "duplicate winner matches CADP: attribute effect to updater context budget",
    "sequential full-history does not differ: drop topology interaction",
    "delta_z is nonpositive: classify that family as search-improves-learning rather than force shielding"
  ],
  "authority": {
    "provider_calls": false,
    "gpu_execution": false,
    "r16_mutation": false,
    "paper_reframe": false,
    "submission": false
  },
  "next_required_artifact": "F0-R4 executable contract after literature-design review and before any R17 scientific provider outcome"
}


===== SOURCE FILE: consultations/e2-r17-search-projection-current-source-and-theory-audit-20260827.md =====
# E2-R17 Search-Projection Censoring — current-source collision and theory audit

Date: 2026-08-27
Status: ZERO-AUTHORITY PRE-DEBATE AUDIT
Branch: `research/e2-r17-compute-shielding-20260825`
Parent design commit: `21799444`
Historical-asset preservation commit: `10e2ae2b`

This note refreshes the closest-work boundary through 2026-08-27 and strengthens the mathematical object before blind Kimi/DeepSeek debate. It does **not** freeze F0-R4, authorize provider/GPU experiments, mutate R16, or claim novelty.

## 1. Current object under review

Search produces a structured object

\[
T_K\sim Q_K(\cdot\mid x,S_t),
\]

while acting and persistent learning consume different projections:

\[
\tau_t^+=a(T_K),\qquad E_t=g(T_K),\qquad S_{t+1}=U(S_t,E_t).
\]

The questionable default is `g_win=a`: only the trajectory selected for serving is shown to the persistent learner. The candidate thesis is therefore not that more test-time compute inherently harms learning. It is:

> Better search does not inherently teach less; learning only from what search serves can.

## 2. Strongest current collisions

### 2.1 Direct method collision: SkillCAT

**Chen et al., 2026, SkillCAT: Contrastive, Assessment-Augmented and Topology-Aware Skill Self-Evolution for LLM Agents, arXiv:2606.13317v2 (2026-07-29).**

Primary-source facts:

- It runs each evolution task multiple times and labels traces by the official evaluator.
- It forms same-task success/failure pairs.
- It identifies the meaningful divergence between paired trajectories and extracts a skill-editable lesson.
- It validates candidate patches by replaying the source task before merging.
- It explicitly frames single-trajectory evidence as unreliable.

Collision judgment: **CADP cannot claim novelty from success/failure pairing, first-divergence extraction, contrastive skill editing, or replay validation.** Those elements are already combined in a persistent external-skill pipeline.

Residual not directly tested by SkillCAT:

1. whether a serving-time winner selector endogenously removes the exact diagnostic evidence available in the generated search set;
2. an exact acting-gain/failure-visibility identity indexed by `K` and difficulty;
3. a cloned-state, exact-same-pool intervention that changes only the learning projection while holding the acting winner fixed;
4. prospective prediction of future learning deficits from pre-outcome censoring mass and diagnostic value;
5. a longitudinal online-acting/frozen-skill reversal induced by binding acting and learning projections.

Implication: SkillCAT is a mandatory strongest method baseline and closest-work discussion. If R17 reduces to “use a success/failure contrast to update a skill,” R17 is not novel.

### 2.2 Direct representation/selection collision: TopoCurate

**Yang et al., 2026, TopoCurate: Modeling Interaction Topology for Tool-Use Agent Training, arXiv:2603.01714.**

Primary-source facts:

- It argues that outcome-based filtering of successful trajectories ignores interaction dynamics.
- It projects multiple same-task trials into a semantic quotient topology containing effective and failure branches.
- It uses branch/error structure to choose SFT trajectories and RL tasks.

Collision judgment: the broad statement “winner/success filtering discards useful branch structure” is already present in parametric tool-agent training. R17 must distinguish its external persistent-updater setting, selection-induced observation law, same-pool intervention, and future frozen-skill endpoint.

### 2.3 Direct feedback-dynamics collision: Rethinking Self-Evolving Agent Skills

**Liu et al., 2026, Rethinking Self-Evolving Agent Skills: Feedback Dynamics over Multiple Rounds, arXiv:2608.02636.**

Primary-source facts:

- It holds executor/optimizer/revision/validation/round budget fixed while varying Normal, Fail-only, and Success-only feedback.
- Every selected evolved skill in its primary study uses failed trajectories; Success-only is never selected.
- It separately evaluates oracle parallel sampling and sequential refinement as test-time-scaling controls.
- On SpreadsheetBench, parallel sampling recovers little of the persistent-skill gain.

Collision judgment: “failed trajectories matter for skill evolution” and “test-time scaling differs from persistent skill improvement” are no longer novel. The surviving question is whether **search serving itself changes which failures reach the updater**, and whether that selective projection causes a future-skill deficit.

### 2.4 Sibling-contrast and divergence collisions

The following primary works already exploit multiple trajectories or success/failure divergence:

- **Search-E1**, arXiv:2605.22511: sibling trajectories with sharply different quality; efficient correct trajectory supplies privileged reference for offline self-distillation.
- **Sibling-Guided Credit Distillation**, arXiv:2606.12634: mixed successful/failed sibling groups; an external model summarizes contrast and divergence to reweight token credit.
- **Outcome-Verified Comparative Self-Distillation**, arXiv:2607.27937: failed student branches, outcome-verified successful continuations, and first state-aligned divergence.
- **SKILL-KD**, arXiv:2607.28048: student failure versus teacher trajectory on the same task, distilled into a validated textual skill patch.
- **SkillCAT**, arXiv:2606.13317: same-task multi-seed success/failure contrast directly into an external skill.

Collision judgment: neither “sibling evidence,” “first divergence,” “contrastive packet,” nor “validated textual patch” is independently defensible novelty.

### 2.5 Search experience reuse collisions

- **Do Not Waste Your Rollouts / Recycling Search Experience**, arXiv:2601.21684: distills positive intermediate conclusions and negative failure patterns from search rollouts into a shared test-time experience bank.
- **TSR**, arXiv:2602.11767: search-guided rollouts are directly used inside the training loop.
- **Expert Iteration / AlphaZero-style search distillation**: search is a policy-improvement operator whose improved distribution is projected back into a learner.
- **On-Policy Distillation with Best-of-N Teacher Rollout Selection**, arXiv:2605.09725: best-of-N can generate improved training targets.

Collision judgment: search often teaches **more**, not less. Any universal “more search hurts learning” thesis is false. R17 must condition the claim on the learning projection `g`, not on search budget alone.

### 2.6 Skill optimizer and diagnostic-search collisions

- **SkillOpt**, arXiv:2605.23904: scored success/failure rollout batches, bounded text edits, held-out acceptance, rejected-edit buffer.
- **SkillHEX**, arXiv:2608.05628: falsifiable failure hypotheses, executable diagnostic evidence, and evidence-guided search over persistent skill revisions.
- **StarHarness**, arXiv:2608.24804 (submitted 2026-08-25): stratified harness-evolution search with hidden selection and held-out evaluation.
- **Evo-Bench**, arXiv:2608.09096: benchmark construction and stratified splitting for harness evolution.
- **SESA**, arXiv:2607.29468: informative failures are distilled into persistent skills that alter the future training distribution.

Collision judgment: bounded validation, rejected-edit memory, diagnostic evidence, and multi-round harness/skill evolution are established ingredients. R17 needs a mechanism-level causal result rather than an optimizer feature bundle.

### 2.7 Mature conceptual reductions

- **Selective labels**, arXiv:1807.00905: historical decisions selectively hide outcomes and induce partial blindness. R17 is related but differs because the nonserved rollout outcomes and trajectories were generated and verifiable; the pipeline chooses not to expose them to the persistent updater.
- **Performative prediction**, arXiv:2002.06673: deployed decisions alter the future data distribution. R17 is a specialized performative data-generation loop in which the acting selector alters the updater-visible experience distribution.
- **DAgger**, arXiv:1011.0686: sequential decisions induce the observation distribution used for learning. R17 is not novel merely because execution changes future training data.

Residual boundary: **outcome-dependent serving selection over a shared search set, coupled to an external persistent updater through a winner-only logging/projection policy.**

## 3. Theory strengthening before debate

### 3.1 Exact binary identity without rollout independence

Let `Y_1,...,Y_K in {0,1}` be arbitrary jointly distributed verifier outcomes. Let the actor succeed whenever any rollout succeeds:

\[
A_K=\mathbb E[\max_i Y_i],\qquad A_1=\mathbb E[Y_1].
\]

Let failure visibility under a precommitted rollout and winner-only projection be

\[
V_{\mathrm{pre}}=\Pr(Y_1=0),\qquad
V_{\mathrm{win}}=\Pr(\max_iY_i=0).
\]

Then, with no independence or exchangeability assumption,

\[
A_K-A_1
=\Pr(Y_1=0,\max_iY_i=1)
=V_{\mathrm{pre}}-V_{\mathrm{win}}.
\]

Define the joint-distribution rescue-censoring mass

\[
\Gamma_K(Q)=\Pr_Q(Y_1=0,\max_iY_i=1).
\]

The i.i.d. Bernoulli model is only a closed-form specialization:

\[
\Gamma_K(p)=(1-p)-(1-p)^K.
\]

Its interior maximizer is

\[
p^*(K)=1-K^{-1/(K-1)}.
\]

This removes the strongest avoidable theoretical weakness in the current draft: independence is not required for the identity itself, only for the one-parameter curve and peak formula.

### 3.2 Correlated-rollout prediction

For a conditionally i.i.d. mixture `Y_i | Theta ~ Bernoulli(Theta)`,

\[
\Gamma_K=\mathbb E[(1-\Theta)-(1-\Theta)^K].
\]

Because this function is concave in `Theta`, heterogeneity/positive exchangeable dependence weakly reduces rescue-censoring mass relative to the i.i.d. curve evaluated at `p=E[Theta]`.

Prospective prediction: parallel rollouts with high shared-mode correlation should show smaller censoring mass than independent samples at the same marginal pass rate. R17 should estimate the empirical joint event directly and use the i.i.d. curve only as a reference model.

### 3.3 Exact continuous-verifier extension

Let verifier scores `R_i in [0,1]` be arbitrarily dependent and let the actor choose `max_i R_i`. For threshold `t`, define

\[
V_{\mathrm{pre}}(t)=\Pr(R_1<t),\qquad
V_{\mathrm{win}}(t)=\Pr(\max_iR_i<t).
\]

By the layer-cake identity,

\[
\mathbb E[\max_iR_i-R_1]
=\int_0^1\left[V_{\mathrm{pre}}(t)-V_{\mathrm{win}}(t)\right]dt.
\]

Thus acting gain equals **integrated threshold-level censoring mass** even for continuous verifiers and correlated rollouts. This is more natural than binarizing every score, although deterministic task completion remains the cleanest F0 endpoint.

### 3.4 When `Gamma times delta` is exact

Let the mixed rescue event be

\[
M=\{Y_1=0,\max_iY_i=1\}.
\]

Define a gated alternative projection that equals winner-only outside `M` and supplies a preregistered diagnostic witness inside `M`. Let

\[
D(T)=J(U(S,g_{\mathrm{alt}}(T)))-J(U(S,g_{\mathrm{win}}(T))).
\]

Then

\[
\mathbb E[D(T)]
=\Pr(M)\,\mathbb E[D(T)\mid M]
=\Gamma_K(Q)\,\delta.
\]

This factorization is exact only because the two projections are identical outside the event whose evidence is claimed to be censored.

For failure families, use a **mutually exclusive, precommitted partition** `Z` of mixed pools—e.g. deterministic first meaningful divergence family:

\[
\mathbb E[D(T)]
=\sum_z \Pr(M,Z=z)\,\delta_z.
\]

Under an i.i.d. within-family model this becomes

\[
\sum_z \pi_z\Gamma_K(p_z)\delta_z.
\]

Overlapping post-hoc failure tags cannot simply be summed; that double-counts mixed pools. The R4 contract must freeze a disjoint assignment or an explicit overlap allocation.

### 3.5 Information-theoretic statement and its limit

For latent reusable failure family `Z`, winner-only is a deterministic coarsening of the full search object, so by data processing

\[
I(Z;g_{\mathrm{win}}(T_K))\le I(Z;T_K).
\]

Under a Bayes-optimal unconstrained learner, the richer object has weakly greater value of information because the learner can ignore irrelevant evidence. This does **not** prove a fixed LLM updater benefits from the full pool: context overload and noisy evidence can make a practical updater worse. Therefore the method should be a bounded, validation-gated diagnostic projection, not “always feed the whole pool.”

This information statement is supporting intuition, not the main causal theorem.

## 4. Surviving novelty candidate after collision review

The strongest defensible object is narrower than the current method pitch:

> **Serving-induced selective trajectory logging in persistent self-evolution:** a search system generates a shared set of candidate trajectories, an acting selector improves current reward, and a tied winner-only learning projection endogenously censors diagnostic failures from an external persistent updater.

Potential irreducible package:

1. exact binary and continuous rescue-censoring identities, with no independence assumption for the core equality;
2. a prospective intermediate/rescueable-regime prediction and a correlation correction;
3. exact-same-pool cloned-state intervention with acting winner fixed;
4. pre-outcome prediction of held-out learning gaps using disjoint-family censoring mass times diagnostic value;
5. longitudinal demonstration that online acting and frozen persistent skill can move in opposite directions;
6. the simplest validated repair—possibly only a Rejected Witness, not CADP.

If any paper is found that already studies this complete coupling, R17 should be reduced or stopped.

## 5. Decisive experimental falsifiers

1. **Projection-null:** on exact same pools, initial skill, updater, verifier, and update seed, changing winner-only to a preregistered failed witness does not change future frozen skill in the predicted direction. Central mechanism STOP.
2. **No prospective law:** empirical mixed-pool mass and calibrated diagnostic value do not predict held-out family/regime ranking or sign. Mechanism claim downgrade/STOP.
3. **No longitudinal reversal:** high-K winner-only does not produce weaker frozen skill than the low-K reference under planned independent streams. Headline STOP, even if one-step edits differ.
4. **Token/context explanation:** duplicated-winner or token-matched neutral evidence matches the failed-witness effect. Diagnostic-evidence mechanism fails.
5. **Simpler method dominance:** Rejected-Witness matches all CADP variants. Keep the simpler method and delete CADP-specific novelty.
6. **SkillCAT reduction:** a source-faithful SkillCAT-style same-task contrast baseline explains the full effect without the serving-selection causal chain. R17 becomes an application/replication unless the law and intervention remain independently novel.

## 6. Required changes before an executable R4 contract

- Add SkillCAT and TopoCurate as mandatory closest work and baselines.
- Rewrite the identity as independence-free; retain i.i.d. only for the analytic curve and `p*`.
- Define the continuous-verifier integral extension.
- Freeze the mixed-pool event and make alternative projections identical outside it for exact `Gamma times delta` interpretation.
- Freeze a mutually exclusive failure-family assignment before outcomes.
- Replace the historical independent-shadow runner with an exact-same-pool prefix runner.
- Rename historical `H/H-hardmine`; it is not the R4 Rejected-Witness arm.
- Include duplicated-winner, random-nonwinner, and SkillCAT-style contrast controls.
- Do not claim novelty for success/failure pairing, first divergence, bounded editing, replay validation, or rejected-edit memory.

## 7. Current decision before model debate

`REVISE_BUT_SURVIVES_FOR_BLIND_DEBATE`

Reason: the mechanism-level object remains distinguishable, but the provisional CADP method is much less novel than the 2026-08-25 synthesis implied. R17 should proceed to blind Kimi/DeepSeek debate only with this tightened collision boundary. No scientific experiment is authorized.


===== SOURCE FILE: generated/e2-r17-r3-assets-provenance-and-r4-supersession-20260827.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-f0-assets-provenance-and-semantic-supersession",
  "created_at_utc": "2026-08-27T13:18:12Z",
  "branch": "research/e2-r17-compute-shielding-20260825",
  "branch_head_before_commit": "217994440e9c630592be8f0b708b56e4ad799f65",
  "origin_main_observed": "272db497",
  "status": "HISTORICAL_R3_ASSETS_PRESERVED_R4_NOT_EXECUTABLE",
  "purpose": "Preserve the previously untracked, zero-scientific-outcome F0/R3 implementation and qualification chain without silently treating its obsolete Compute-Shielding semantics as the executable Search-Projection-Censoring R4 design.",
  "inspection": {
    "all_files_read": true,
    "json_documents_valid": 7,
    "historical_runner_unit_tests": {
      "passed": 7,
      "failed": 0,
      "scope": "historical R3 routing semantics only"
    },
    "python_compile_pass": true,
    "scientific_provider_outcomes_present": false,
    "benchmark_outcomes_accessed_by_adapter_smoke": false
  },
  "preserved_assets": [
    {
      "path": "consultations/e2-r17-compute-shielding-research-decision-20260825.md",
      "sha256": "2c5488857a6d68e4ff4ef8bd0caa8bad55ca5f0eb47a5df614b8602614c5ea48",
      "role": "historical research decision chain",
      "disposition": "preserve unchanged; superseded scientific object"
    },
    {
      "path": "generated/e2-r17-compute-shielding-f0-contract-20260825.json",
      "sha256": "abc12d0514bbd35ddcf3ad797597f80e5cc4ad70038232c317f268d6c54bb9d9",
      "role": "original max-turns F0 contract",
      "disposition": "preserve unchanged; explicitly superseded by F0-R2"
    },
    {
      "path": "generated/e2-r17-compute-shielding-f0-contract-r2-20260825.json",
      "sha256": "988d57f6cfaa5104efeeb1ec19bc3a25bdd518c607cf5035208546a3a8598e81",
      "role": "best-of-K pre-outcome F0-R2 contract",
      "disposition": "preserve unchanged; design ancestor only"
    },
    {
      "path": "generated/e2-r17-compute-shielding-f0-qualification-20260825.json",
      "sha256": "a6e670b5de86684e78cda7fad38b6a7c447a77f71154ec9044580630a55526a5",
      "role": "max-turns interface qualification",
      "disposition": "preserve as substrate/runtime evidence; not an R4 mechanism qualification"
    },
    {
      "path": "generated/e2-r17-compute-shielding-f0-r3-gate-20260825.json",
      "sha256": "6a928a246795e52df0bedafc4e49136db9ffff7854a725af239af564dc843943",
      "role": "historical R3 gate",
      "disposition": "preserve unchanged; remains non-authoritative and semantically superseded"
    },
    {
      "path": "generated/e2-r17-compute-shielding-failure-unverifiable-substrate-commit-20260825.json",
      "sha256": "4c887f719ef3e57ef64a834299687979e61b467a95a0ba315a5c48c5095a333b",
      "role": "failure asset for unverifiable shallow-clone commit",
      "disposition": "retain as active prevention asset"
    },
    {
      "path": "generated/e2-r17-mindmemos-ark-adapter-qualification-20260825.json",
      "sha256": "4b5363cd5228a55b0bd081372888d7b71ac4dc5c86693500f57d25d83285618f",
      "role": "historical Ark Plan protocol smoke",
      "disposition": "preserve; provider availability must be rechecked"
    },
    {
      "path": "generated/e2-r17-mindmemos-substrate-qualification-20260825.json",
      "sha256": "d49c50284e9b1c8086d8d46369c07afa15623c9c19460afbb64fd64dafc1a0a9",
      "role": "MindMemOS/SpreadsheetBench first-party substrate qualification",
      "disposition": "retain as reusable static qualification subject to freshness recheck"
    },
    {
      "path": "research_pipeline/e2_r17_compute_shielding_f0_qualification.py",
      "sha256": "d6e87f240b4e7af5adf15d21505c32136e56fa7d20bdea983daf9bf7d9162d89",
      "role": "historical max-turns qualification runner",
      "disposition": "preserve unchanged; not used to authorize R4"
    },
    {
      "path": "research_pipeline/e2_r17_compute_shielding_runner.py",
      "sha256": "430ea756fb03a1c2b853e7266b2ad3394f2f7bb4ed61a21f7c9be8e87982306a",
      "role": "historical four-arm routing semantics",
      "disposition": "preserve unchanged; prohibited as R4 runner"
    },
    {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "c8b105859cfe632b03bb8a3df35a53177f7cf22589cd09fd670f044c2faa7e80",
      "role": "Ark Plan transport adapter",
      "disposition": "retain as transport component after model-identity requalification"
    },
    {
      "path": "research_pipeline/test_e2_r17_compute_shielding_runner.py",
      "sha256": "7d1c2e9eaf053a621455568b801d7438cd1a81de350cf1ac388ca5ee7917b40b",
      "role": "historical runner tests",
      "disposition": "preserve as regression for superseded semantics"
    },
    {
      "path": "scripts/build_e2_r17_compute_shielding_f0_r3_gate.py",
      "sha256": "4b2ffcff652c36a6c96f18982ee6d33a81ee7687bf6ce788af678c0ced108b62",
      "role": "historical R3 gate builder",
      "disposition": "preserve unchanged; do not regenerate R4 from it"
    },
    {
      "path": "scripts/qualify_e2_r17_mindmemos_ark_adapter.py",
      "sha256": "6e2538affde374ade7997d00730214111cc614553385e8a15cb48307b5c34ce9",
      "role": "DeepSeek Ark Plan protocol qualifier",
      "disposition": "retain; extend separately for blind multi-model consultation receipts"
    },
    {
      "path": "scripts/qualify_e2_r17_mindmemos_substrate.py",
      "sha256": "3af8f1609dc7c3b0b50a9a0c06c160b1dc3567fe713c18d96d5fe6d079fb387f",
      "role": "first-party substrate qualifier",
      "disposition": "retain for freshness requalification"
    }
  ],
  "semantic_adjudication": {
    "surviving_scientific_object": "Search-Projection Censoring",
    "r3_object": "generic Compute Shielding",
    "r3_to_r4_change_is_pre_outcome": true,
    "material_conflicts": [
      {
        "issue": "shadow projection identity",
        "r2_contract": "pre-designated rollout_0 from the same high-K pool",
        "r3_gate_and_runner": "independently executed K=1 shadow",
        "r4_design": "precommitted rollout_0 from the exact same K-pool",
        "adjudication": "R3 gate/runner cannot implement the R4 same-pool causal intervention. A new runner and contract are required."
      },
      {
        "issue": "rejected failure availability",
        "r3_runner": "nonselected high-K failures are forbidden from updater input; hardmine can only duplicate a selected all-fail trajectory",
        "r4_design": "a frozen-rule nonserved rejected witness is an explicit learning projection and simple baseline",
        "adjudication": "Historical hardmine is not the R4 Rejected-Witness arm and must not be relabeled."
      },
      {
        "issue": "headline variable",
        "r3": "compute amount",
        "r4": "acting versus learning projection of a shared search object",
        "adjudication": "Static substrate/provider/checkpoint evidence may be reused, but R3 causal and promotion rules do not authorize R4."
      }
    ],
    "latest_design_artifacts": [
      "consultations/e2-r17-search-projection-censoring-literature-synthesis-20260825.md",
      "generated/e2-r17-search-projection-f0-r4-design-20260825.json"
    ],
    "latest_design_status": "DESIGN_ONLY_NOT_EXECUTION_AUTHORITY",
    "r16_unchanged": true
  },
  "next_required_steps": [
    "current primary-source collision review",
    "blind Kimi and DeepSeek round-1 scientific debate with exact receipts",
    "cross-exposed round-2 attack",
    "single-object round-3 convergence and paper-PC round-4 red team",
    "explicit R4 executable contract and pre-execution review",
    "new same-pool projection runner and tests"
  ],
  "authority": {
    "scientific_provider_experiment": false,
    "gpu_execution": false,
    "r16_mutation": false,
    "paper_reframe": false,
    "submission": false
  }
}


===== SOURCE FILE: generated/e2-r17-compute-shielding-f0-r3-gate-20260825.json =====
{
  "ark_adapter_sha256": "c8b105859cfe632b03bb8a3df35a53177f7cf22589cd09fd670f044c2faa7e80",
  "artifact_type": "e2-r17-compute-shielding-f0-r3-gate",
  "body_sha256": "8266287ee7d8613010b9347308aeb2bbcfed451a6f7ff4851982bbc50f0b72cb",
  "checks": {
    "archive_sha_exact": true,
    "benchmark_outcome_not_accessed_by_adapter_smoke": true,
    "dataset_records_400": true,
    "dataset_sha_exact": true,
    "development_task_count_4": true,
    "development_task_selection_outcome_blind": true,
    "provider_retry_disabled": true,
    "runner_semantics_tests_pass": true,
    "substrate_commit_matches_receipt": true,
    "substrate_receipt_pass": true,
    "xlsx_files_800": true
  },
  "child": "E2-R17-COMPUTE-SHIELDING",
  "compute_contract": {
    "all_subruns_are_receipts": true,
    "hardmine_cannot_reconstruct_rescued_failure": true,
    "high_k": 4,
    "low_k": 1,
    "nonselected_failures_may_not_feed_updater": true,
    "only_selected_subrun_is_deployed": true,
    "selector": "max score, stable lowest rollout index tie-break",
    "shadow_is_independent_k1_same_task_same_preupdate_skill_state": true
  },
  "data_contract": {
    "archive_sha256": "10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949",
    "dataset_sha256": "bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7",
    "development_task_ids": [
      "33722",
      "493-5",
      "39046",
      "14240"
    ],
    "records": 400,
    "selection_tag": "E2-R17-F1-DEVELOPMENT-TASKS-v1",
    "source": "SpreadsheetBench Verified-400",
    "task_prompt_or_outcome_inspected_for_selection": false,
    "xlsx_files": 800
  },
  "experiment_authority": false,
  "f1_arms": [
    "L/L",
    "H/H",
    "H/L-shadow",
    "H/H-hardmine"
  ],
  "f1_execution_authorized": false,
  "f1_promotion_rule": [
    "H/H online reward > L/L online reward",
    "H/H frozen-skill quality < L/L frozen-skill quality",
    "H/L-shadow frozen-skill quality > H/H",
    "H/L-shadow recovery > H/H-hardmine recovery"
  ],
  "gpu_authority": false,
  "paper_parent": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
  "provider_gate": {
    "qualification_sha256": "4b5363cd5228a55b0bd081372888d7b71ac4dc5c86693500f57d25d83285618f",
    "requested_model": "deepseek-v4-pro",
    "required_resolved_model": "deepseek-v4-pro-260425",
    "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
    "status": "HOLD_PROVIDER_SUBSCRIPTION"
  },
  "reason_f1_not_authorized": "provider gate must PASS and an execution artifact must bind exact tasks/seeds/call budget before model calls",
  "repeats_are_scientific_n": false,
  "runner_sha256": "430ea756fb03a1c2b853e7266b2ad3394f2f7bb4ed61a21f7c9be8e87982306a",
  "runner_test_result": {
    "output_tail": "----------------------------------------------------------------------\nRan 7 tests in 0.000s\n\nOK\n",
    "pass": true,
    "returncode": 0
  },
  "runner_test_sha256": "7d1c2e9eaf053a621455568b801d7438cd1a81de350cf1ac388ca5ee7917b40b",
  "schema_version": "1.0",
  "scientific_authority": false,
  "scientific_object": "acting-optimal compute can be learning-suboptimal because test-time rescue censors reusable failure signals",
  "scientific_unit": "one learned skill state from one independently seeded evolution stream",
  "status": "HOLD_PROVIDER_SUBSCRIPTION",
  "submission_authority": false,
  "substrate_contract": {
    "bound_file_sha256": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/pipelines/skill/version_store.py": "74528837205aa9501937aa6539c37f0826fd551557ae842899457c1cad635022",
      "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py": "ca7a6f7556accd7caa116ad0d184a27371d9e1b3bc5baa902e57d8a901dc04b7",
      "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py": "58f002b8c48f5e72fc24a26344c2122b2d990cf38f9e47d7545473c00cd28ad4",
      "src/mindmemos_eval/mindmemos_eval/skills/evolve/algo.py": "2d2264b712e788b7f7e4aa988085ae943ac230a2ef7b4ae6c750d9887a6cf2ad",
      "src/mindmemos_eval/mindmemos_eval/skills/runners.py": "a0b7dd1071148f570b65f53963ff5843beeaeded5aaf82f0846182bb55d61732"
    },
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "name": "MindMemOS",
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "qualification_sha256": "d49c50284e9b1c8086d8d46369c07afa15623c9c19460afbb64fd64dafc1a0a9",
    "remote": "https://github.com/mindscale-noah/MindMemOS.git",
    "skill_evolver": "src/mindmemos/mindmemos/pipelines/skill/evolution.py::SkillEvolver",
    "spreadsheet_env": "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py::SpreadsheetBenchEnv",
    "upstream_test_packaging_warning": {
      "output_tail": "\n==================================== ERRORS ====================================\n_____ ERROR collecting tests/mindmemos_eval/test_spreadsheetbench_eval.py ______\nImportError while importing test module '/data/wyt/evidence-substrates/MindMemOS-20260817/tests/mindmemos_eval/test_spreadsheetbench_eval.py'.\nHint: make sure your test modules/packages have valid Python names.\nTraceback:\n/usr/lib/python3.12/importlib/__init__.py:90: in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n/data/wyt/evidence-substrates/MindMemOS-20260817/tests/mindmemos_eval/test_spreadsheetbench_eval.py:12: in <module>\n    from mindmemos_eval.skills.envs.spreadsheetbench import (\nE   ImportError: cannot import name 'EvolveOutcome' from 'mindmemos_eval.skills.envs.spreadsheetbench' (/data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/__init__.py)\n=========================== short test summary info ============================\nERROR ../../../../data/wyt/evidence-substrates/MindMemOS-20260817/tests/mindmemos_eval/test_spreadsheetbench_eval.py\n!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!\nno tests collected, 1 error in 1.34s\n",
      "present": true,
      "scientific_runtime_dependency": false,
      "scope": "tests/mindmemos_eval/test_spreadsheetbench_eval.py collection import surface"
    }
  }
}


FULL DOSSIER END
