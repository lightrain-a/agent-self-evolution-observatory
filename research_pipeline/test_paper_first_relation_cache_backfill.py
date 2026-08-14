from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from .config import StorageSettings
from .paper_first_relation_cache_backfill import backfill_relation_cache


class RelationCacheBackfillTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root,
            corpus_dir=root / "corpora",
            dataset_dir=root / "datasets",
            paper_dir=root / "papers",
            index_dir=root / "indexes",
            run_dir=root / "runs",
            cache_dir=root / "cache",
            lock_dir=root / "locks",
            site_artifact_dir=root / "site",
        )

    def generator(self, count: int = 4) -> dict:
        refs=[f"arXiv:2608.{i:05d}" for i in range(1,count+1)]
        return {"saturation_memory":{"portable_review_receipts":[{"run_id":"r1","source_refs":refs,"scientific_authority":False}]}}

    def requester(self, calls: list[str], *, fulltext_fails: bool = False):
        def fetch(url: str, *, timeout: float, headers: dict[str,str]):
            calls.append(url)
            arxiv_id=url.rsplit('/',1)[-1]
            if '/html/' in url:
                if fulltext_fails:
                    raise RuntimeError('fulltext-down')
                return SimpleNamespace(status_code=200,text=f'<html><body><section><h2>Results</h2><p>For {arxiv_id}, success improves from 40.0% to 60.0% on held-out tasks.</p></section></body></html>')
            return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="Primary {arxiv_id}"><meta name="citation_arxiv_id" content="{arxiv_id}"><blockquote class="abstract mathjax">Abstract: Verified agent evidence for {arxiv_id}.</blockquote>')
        return fetch

    def test_backfill_is_bounded_and_zero_authority(self) -> None:
        calls=[]
        with tempfile.TemporaryDirectory() as td:
            state=backfill_relation_cache(storage=self.storage(Path(td)),generator_state=self.generator(4),requester=self.requester(calls),max_primary_per_run=2,max_fulltext_per_run=1,min_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual((state['summary']['primary_attempted'],state['summary']['primary_succeeded'],state['summary']['primary_cached_after']),(2,2,2))
        self.assertEqual((state['summary']['fulltext_attempted'],state['summary']['fulltext_succeeded']),(1,1))
        self.assertEqual(state['summary']['primary_missing_after'],2)
        self.assertEqual(state['summary']['usable_reviewed_cache_records_after'],2)
        self.assertFalse(state['scientific_authority'])
        self.assertFalse(state['policy']['automatic_problem_gate_authority'])
        self.assertTrue(state['policy']['transport_replay_cannot_multiply_network_budget'])

    def test_fulltext_failure_does_not_invalidate_primary_cache(self) -> None:
        calls=[]
        with tempfile.TemporaryDirectory() as td:
            state=backfill_relation_cache(storage=self.storage(Path(td)),generator_state=self.generator(2),requester=self.requester(calls,fulltext_fails=True),max_primary_per_run=2,max_fulltext_per_run=2,min_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state['summary']['primary_cached_after'],2)
        self.assertEqual(state['summary']['primary_missing_after'],0)
        self.assertEqual(state['summary']['usable_reviewed_cache_records_after'],2)
        self.assertEqual(state['summary']['fulltext_failed'],2)
        self.assertEqual(state['status'],'COMPLETE')

    def test_existing_primary_cache_makes_zero_primary_requests(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));calls=[];now=datetime(2026,8,13,tzinfo=timezone.utc)
            first=backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=self.requester(calls),max_primary_per_run=2,max_fulltext_per_run=0,min_interval_seconds=0,now=now)
            calls.clear()
            def forbidden(*args,**kwargs):
                calls.append('called');raise AssertionError
            second=backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=forbidden,max_primary_per_run=2,max_fulltext_per_run=0,min_interval_seconds=0,now=now+timedelta(hours=1))
        self.assertEqual(first['summary']['primary_cached_after'],2)
        self.assertEqual(second['summary']['primary_attempted'],0)
        self.assertEqual(calls,[])

    def test_recent_running_receipt_blocks_transport_replay(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));calls=[];now=datetime(2026,8,13,tzinfo=timezone.utc)
            def interrupted(url: str, **kwargs): calls.append(url);raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):
                backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=interrupted,max_primary_per_run=1,max_fulltext_per_run=0,min_interval_seconds=0,now=now)
            calls.clear()
            def forbidden(*args,**kwargs): calls.append('called');raise AssertionError
            second=backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=forbidden,max_primary_per_run=1,max_fulltext_per_run=0,min_interval_seconds=0,now=now+timedelta(minutes=1))
        self.assertEqual(second['status'],'SKIPPED_RECENT_BACKFILL_ATTEMPT')
        self.assertEqual(second['previous_status'],'BACKFILL_RUNNING')
        self.assertEqual(second['summary']['primary_attempted'],0)
        self.assertEqual(calls,[])

    def test_recent_primary_failure_is_cooled_down(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));calls=[];now=datetime(2026,8,13,tzinfo=timezone.utc)
            def failing(url: str, **kwargs): calls.append(url);raise RuntimeError('provider-down')
            first=backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=failing,max_primary_per_run=2,max_fulltext_per_run=0,min_interval_seconds=0,now=now)
            calls.clear()
            second=backfill_relation_cache(storage=storage,generator_state=self.generator(2),requester=self.requester(calls),max_primary_per_run=2,max_fulltext_per_run=0,min_interval_seconds=0,now=now+timedelta(hours=1))
        self.assertEqual(first['summary']['primary_failed'],2)
        self.assertEqual(second['summary']['primary_attempted'],0)
        self.assertEqual(second['summary']['cooldown_skipped'],2)
        self.assertEqual(calls,[])


if __name__ == '__main__':
    unittest.main()
