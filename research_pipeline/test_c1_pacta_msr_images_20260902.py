from __future__ import annotations
import hashlib,json
from pathlib import Path
from research_pipeline import prepare_c1_pacta_msr_images_20260902 as m


def test_image_units_cover_source_and_future_exactly_once():
    rows=m.image_units()
    assert len(rows)==20
    assert len({x['instance_id'] for x in rows})==20
    assert sum(x['role']=='source' for x in rows)==10
    assert sum(x['role']=='future' for x in rows)==10
    assert all(len(x['base_commit'])==40 for x in rows)


def test_image_prepare_is_zero_provider_by_construction():
    source=open(m.__file__,encoding='utf-8').read()
    assert 'AA_API_KEY' not in source
    assert 'chat/completions' not in source
    assert 'provider_calls' in source
    assert 'scientific_calls' in source


def test_checkpoint_finalize_uses_existing_bytes_only(tmp_path:Path,monkeypatch):
    base=[{'role':'source' if i%2==0 else 'future','unit_id':f'u{i//2}','instance_id':f'inst{i}','base_commit':f'{i:040x}'} for i in range(20)]
    monkeypatch.setattr(m,'image_units',lambda:base)
    monkeypatch.setattr(m,'image_repo',lambda x:'repo/'+x)
    monkeypatch.setattr(m,'image_ref',lambda x:'repo/'+x+':latest')
    monkeypatch.setattr(m,'CACHE',tmp_path/'cache')
    monkeypatch.setattr(m,'POOL',tmp_path/'pool.json')
    (tmp_path/'pool.json').write_text('{}')
    for pass_no in (1,2):
        d=tmp_path/'raw-manifests'/f'pass{pass_no}';d.mkdir(parents=True)
        for x in base:
            child={'schemaVersion':2,'config':{'digest':'sha256:'+'1'*64,'size':1},'layers':[]}
            raw=(json.dumps(child,sort_keys=True,separators=(',',':'))+'\n').encode();digest=hashlib.sha256(raw).hexdigest()
            (d/f"{x['instance_id']}__amd64.json").write_bytes(raw)
            index={'schemaVersion':2,'manifests':[{'digest':'sha256:'+digest,'platform':{'os':'linux','architecture':'amd64'}}]}
            (d/f"{x['instance_id']}__index.json").write_text(json.dumps(index))
    monkeypatch.setattr(m,'get_raw',lambda *a,**k:(_ for _ in ()).throw(AssertionError('network forbidden')))
    result=m.finalize_existing(tmp_path)
    assert result['image_count']==20
    assert result['recovery_mode']=='checkpoint_finalize_after_transport_disconnect'
    freeze=json.loads((tmp_path/'manifest-freeze.json').read_text())
    assert freeze['stable_twice'] is True and freeze['recovery_mode']=='checkpoint_finalize_after_transport_disconnect'
