from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_paper_update import (
    render_results,
)


def test_render_results_is_claim_first_and_uses_task_blocked_statistics():
    adjudication = {
        "primary_A_vs_D": {
            "permutation": {"analyzable_task_count": 22, "observed_global_T": .12,
                            "monte_carlo_p_value": .01},
            "task_bootstrap_CI": {"lower": .03, "upper": .2},
        },
        "secondary_A_vs_N": {
            "permutation": {"observed_global_T": .08, "monte_carlo_p_value": .04},
            "task_bootstrap_CI": {"lower": .01, "upper": .15},
        },
        "missingness_gate": {
            "failure_rate_A": .02, "failure_rate_D": .03,
            "absolute_failure_rate_difference": .01,
            "fisher_exact_two_sided_p": .8, "decision": "MISSINGNESS_GATE_PASS",
        },
        "R4": {"A_vs_D": {
            "decision": "R4_TASK_BLOCKED_ANALYSIS_COMPLETE",
            "permutation": {"task_count": 21, "observed_mean_task_difference": .01,
                            "two_sided_monte_carlo_p_value": .9},
        }},
        "scientific_adjudication": {
            "strongest_supported_claim": "Cross-case partition shifted edit-target behavior.",
            "bounded_null_wording": "no qualified separation",
        },
    }
    text = render_results(adjudication)
    assert "22 task blocks" in text
    assert "T=0.1200" in text
    assert "Cross-case partition shifted edit-target behavior." in text
    assert "SHA-256" not in text
    assert "manifest" not in text.lower()
