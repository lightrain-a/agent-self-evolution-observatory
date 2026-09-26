import copy
import json
import tempfile
import unittest
from pathlib import Path
from research_pipeline.discovery_method_formation import (
    audit_formation, build_method_formation_state, formation_shape,
    normalize_formation, write_method_formation_state,
)


def complete_card():
    card = formation_shape()
    card['observation']['evidence_refs'] = ['paper:1']
    card['analogies'][0]['source_refs'] = ['paper:2']
    card['no_analogy_reason'] = ''
    card['hypotheses'] = [
        {'id': 'H1', 'kind': 'MECHANISM', 'claim': 'executor interaction', 'scope': 'matched task panel', 'prediction': 'ordering changes on swap', 'falsifier': 'ordering stable on swap', 'evidence_refs': []},
        {'id': 'H2', 'kind': 'ALTERNATIVE', 'claim': 'sampling noise', 'scope': 'same panel', 'prediction': 'resampling accounts for shift', 'falsifier': 'swap exceeds resampling', 'evidence_refs': []},
    ]
    card['p0']['mode'] = 'OFFLINE_REPLAY'
    card['p0']['budget'].update(max_new_calls=0, estimated_wall_seconds=15, estimate_basis='assumed 2 replays/sec; verify before execution')
    card['p0']['hypothesis_predictions'] = {'H1': 'swap changes ordering beyond noise', 'H2': 'resampling explains ordering'}
    return card


REGISTRY = {'paper:1': {}, 'paper:2': {}}


class FormationTests(unittest.TestCase):
    def test_complete_is_plan_only(self):
        result = audit_formation(complete_card(), REGISTRY)
        self.assertEqual(result['status'], 'PLAN_FIELDS_COMPLETE')
        self.assertEqual(result['scientific_status'], 'NOT_EVALUATED')
        self.assertFalse(any(result['authority'].values()))
        self.assertEqual(result['logical_evaluations'], 32)

    def test_missing_plan_does_not_falsify(self):
        result = audit_formation({}, REGISTRY)
        self.assertEqual(result['status'], 'NEEDS_PLAN')
        self.assertEqual(result['scientific_status'], 'NOT_EVALUATED')

    def test_unknown_reference_needs_retrieval(self):
        result = audit_formation(complete_card(), {'paper:1': {}})
        self.assertIn('paper:2', result['retrieval_refs'])
        self.assertNotEqual(result['status'], 'PLAN_FIELDS_COMPLETE')

    def test_model_cannot_write_authority_or_outcomes(self):
        card = complete_card()
        card.update(authority={'gpu': True}, scientific_status='PASS', measured_gain=0.5)
        card['hypotheses'][0]['status'] = 'FALSIFIED_IN_SCOPE'
        card['p0']['execution_status'] = 'PASSED'
        clean = normalize_formation(card)
        self.assertEqual(clean['hypotheses'][0]['status'], 'PROPOSED')
        self.assertEqual(clean['p0']['execution_status'], 'NOT_EXECUTED')
        self.assertNotIn('measured_gain', clean)
        self.assertFalse(any(clean['authority'].values()))

    def test_analogy_requires_broken_assumption(self):
        card = complete_card()
        card['analogies'][0]['breaks'] = []
        self.assertIn('analogies.0.breaks', audit_formation(card, REGISTRY)['missing'])

    def test_no_analogy_allowed_with_reason(self):
        card = complete_card()
        card.update(analogies=[], no_analogy_reason='No source-domain mapping survives the operator audit.')
        self.assertEqual(audit_formation(card, REGISTRY)['status'], 'PLAN_FIELDS_COMPLETE')

    def test_competitors_require_distinct_predictions(self):
        card = complete_card()
        card['p0']['hypothesis_predictions'] = {'H1': 'same result', 'H2': 'same result'}
        self.assertIn('p0.distinguishing-predictions', audit_formation(card, REGISTRY)['missing'])

    def test_duplicate_ids_block_completeness(self):
        card = complete_card()
        card['hypotheses'][1]['id'] = 'H1'
        self.assertIn('unique-hypothesis-ids', audit_formation(card, REGISTRY)['missing'])

    def test_call_budget_and_boolean_guard(self):
        card = complete_card()
        card['p0']['mode'] = 'NEW_EXECUTIONS'
        card['p0']['budget']['max_new_calls'] = 2
        self.assertIn('p0.call-budget-below-estimated-provider-calls', audit_formation(card, REGISTRY)['missing'])
        card['p0']['budget']['tasks'] = True
        self.assertIn('p0.budget-positive-integer-counts', audit_formation(card, REGISTRY)['missing'])

    def test_unknown_time_is_visible(self):
        card = complete_card()
        card['p0']['budget']['estimated_wall_seconds'] = float('nan')
        self.assertIn('p0.budget.time-estimate-and-basis', audit_formation(card, REGISTRY)['missing'])

    def test_pure_and_idempotent_normalization(self):
        raw = complete_card()
        original = copy.deepcopy(raw)
        once = normalize_formation(raw)
        self.assertEqual(raw, original)
        self.assertEqual(once, normalize_formation(once))

    def test_projection_redacts_private_card_text(self):
        card = complete_card()
        card['intuition'] = 'PRIVATE_SOURCE_TEXT_SENTINEL'
        source = {'run_id': 'test', 'candidates': [{'candidate_id': 'T1', 'method_formation': card}]}
        primary = {'records': [{'ref': r, 'primary_source_verified': True} for r in REGISTRY]}
        result = build_method_formation_state(source, primary)
        self.assertEqual(result['summary']['plans_complete'], 1)
        self.assertNotIn('PRIVATE_SOURCE_TEXT_SENTINEL', json.dumps(result))
        self.assertEqual(result['summary']['model_calls'], 0)

    def test_atomic_projection_keeps_state_on_invalid_input(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_method_formation_state(project_root=root, generator_state={}, primary_state={})
            target = root / 'generated/discovery-method-formation.json'
            before = target.read_bytes()
            (root / 'generated/paper-first-problem-generator-state.json').write_text('{broken')
            with self.assertRaises(json.JSONDecodeError):
                write_method_formation_state(project_root=root)
            self.assertEqual(before, target.read_bytes())

    def test_both_generator_paths_include_contract(self):
        from research_pipeline.paper_first_problem_generator_prompts import generator_prompt
        from research_pipeline.paper_first_problem_search_portfolio import _formulation_prompt
        for prompt in (generator_prompt([]), _formulation_prompt([], {})):
            self.assertIn('METHOD-FORMATION PLANNING CONTRACT', prompt)
            self.assertIn('method_formation', prompt)
            self.assertIn('inconclusive_rule', prompt)

    def test_generator_preserves_card(self):
        from research_pipeline.paper_first_problem_generator import _normalize
        row = _normalize({'method_formation': complete_card()}, REGISTRY)
        self.assertEqual(row['method_formation_audit']['status'], 'PLAN_FIELDS_COMPLETE')
        self.assertEqual(row['method_formation']['scientific_status'], 'NOT_EVALUATED')

    def test_public_generator_summary_preserves_plan_counts_not_private_text(self):
        from research_pipeline.paper_first_problem_generator import _normalize, public_problem_generator_state
        card = complete_card()
        card['intuition'] = 'PRIVATE_FORMATION_SENTINEL'
        row = _normalize({'candidate_id': 'C1', 'method_formation': card}, REGISTRY)
        state = {'candidates': [row], 'search_portfolio': {'nested': {'method_formation': card}}}
        published = public_problem_generator_state(state)
        self.assertNotIn('PRIVATE_FORMATION_SENTINEL', json.dumps(published))
        self.assertIn('method_formation_summary', published['candidates'][0])
        projected = build_method_formation_state(published, {})
        self.assertEqual(projected['summary']['plans_complete'], 1)
        self.assertFalse(any(projected['authority'].values()))

    def test_pre_f0_candidates_are_visible_without_promotion(self):
        row = {'candidate_id': 'C1'}
        state = build_method_formation_state({'pre_f0_candidates': [row, row]}, {})
        self.assertEqual(state['summary']['candidates'], 1)
        self.assertEqual(state['summary']['automatic_promotions'], 0)
        self.assertEqual(state['rows'][0]['planning_status'], 'NEEDS_PLAN')

    def test_multiturn_provider_cost_is_not_logical_eval_count(self):
        card = complete_card()
        card['p0']['mode'] = 'NEW_EXECUTIONS'
        card['p0']['budget'].update(provider_calls_per_evaluation=10, retry_call_allowance=4, max_new_calls=324)
        result = audit_formation(card, REGISTRY)
        self.assertEqual(result['logical_evaluations'], 32)
        self.assertEqual(result['estimated_new_provider_calls'], 324)
        self.assertEqual(result['status'], 'PLAN_FIELDS_COMPLETE')
        card['p0']['budget']['max_new_calls'] = 32
        self.assertIn('p0.call-budget-below-estimated-provider-calls', audit_formation(card, REGISTRY)['missing'])

    def test_untrusted_types(self):
        for value in (None, 'x', [], 99, {'hypotheses': 'bad', 'p0': {'budget': []}}):
            self.assertFalse(any(audit_formation(value)['authority'].values()))


if __name__ == '__main__':
    unittest.main()
