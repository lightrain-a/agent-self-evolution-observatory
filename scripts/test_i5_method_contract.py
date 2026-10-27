#!/usr/bin/env python3
"""Check the I5 research contract and rendered evidence; no training is run."""
from __future__ import annotations
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    protocol = json.loads((ROOT/'rsi/i5-method-protocol.json').read_text(encoding='utf-8'))
    assert protocol['idea_id'] == 'I5'
    assert protocol['status'] == 'research_design_not_executed'
    main_population = protocol['population']['main']
    assert main_population['n'] == len(main_population['sizes_billion'])*len(main_population['specialties']) == 10
    assert main_population['unordered_pairs'] == math.comb(10,2) == 45
    assert main_population['directional_pairs'] == 90
    assert protocol['routing']['full_matchings_n10'] == math.factorial(10)//(2**5*math.factorial(5)) == 945
    assert protocol['population']['pilot']['unordered_pairs'] == math.comb(4,2)
    assert protocol['training_kernel']['cross_vocabulary_kl'] is False
    assert protocol['population']['weight_merging_or_member_replacement'] is False
    assert protocol['routing']['allow_solo'] is True
    assert protocol['routing']['duration_candidate_steps']['force_switch_at_maximum'] is False
    assert protocol['routing']['exhaustive_45_edge_trial_each_round'] is False
    assert 0 < protocol['routing']['probe_budget_fraction'] <= .2
    assert {'train','probe_dev','meta_valid','test'} == set(protocol['data_roles'])
    assert set(protocol['orthogonality']) == {'I1','I2','I3','I4','I6','I7','I8'}
    assert {'probe_branches','solo_branches','delayed_labels','peer_feedback','student_forward_backward'} <= set(protocol['compute_ledger'])
    experiment3 = next(e for e in protocol['experiments'] if e['id']=='E3')
    assert {'identical_frozen_material_reordering','frozen_tutors_live_feedback','both_peers_updated'} <= set(experiment3['controls'])
    assert {'matched_update_budget','matched_total_compute_with_saved_feedback_cost_reallocated'} <= set(protocol['gain_target']['solo_controls'])
    assert protocol['baselines']['must_not_label_inspired_baseline_as_official_reproduction'] is True
    assert protocol['statistics']['no_rollout_pseudoreplication'] is True
    with (ROOT/'rsi/sources.tsv').open(encoding='utf-8',newline='') as f:
        sources = list(csv.DictReader(f,delimiter='\t'))
    source_map = {x['id']:x for x in sources}
    assert len(source_map)==len(sources), 'Duplicate source IDs'
    assert set(protocol['source_ids']) <= set(source_map)
    assert 'Workshop' in source_map['S201']['date'] and '不是主会' in source_map['S201']['date']
    assert '未确认' in source_map['S205']['date']
    page = (ROOT/'rsi/idea-i5.html').read_text(encoding='utf-8')
    for anchor in ['scene','challenge','collisions','insight','design','gain','rewiring','experiments','evaluation','orthogonality','papers','teaching-feedback','summary']:
        assert f'id="{anchor}"' in page, anchor
    for ref in protocol['source_ids']:
        assert f'href="references.html#{ref}"' in page, ref
    assert 'i5-method-protocol.json' in page
    assert '同预算自学' in page and '未见任务' in page
    assert '945' in page and '冻结教师' in page and '相同材料' in page
    # The unified I5 link is kept; the historic teaching page is not a second menu entry.
    nav = (ROOT/'rsi/site-nav.js').read_text(encoding='utf-8')
    assert nav.count('"idea-i5.html"') == 1
    assert '"teaching.html"' not in nav
    assert 'href="teaching.html"' in page
    exported = ROOT/'_site/rsi'
    if exported.exists():
        assert (exported/'i5-method-protocol.json').read_bytes() == (ROOT/'rsi/i5-method-protocol.json').read_bytes()
    print('PASS I5 contract: ten independent learners, directed counterfactual gain, bounded probes, fixed kernel, ordering controls, sources, single I5 menu and export. No training was performed.')

if __name__ == '__main__':
    main()
