from __future__ import annotations
import tempfile, unittest
from pathlib import Path
import numpy as np
from .round1_tasks import tasks, split, workflows, reserve_tasks, UPDATES, LESSONS, EDITS
from .round1_runtime import fit_logistic, run_lock

class Round1FirstClassTest(unittest.TestCase):
    def test_task_splits_and_reserve_are_disjoint(self):
        xs=tasks(); d,c,h=split(xs); r=reserve_tasks(xs)
        self.assertEqual((len(xs),len(d),len(c),len(h),len(r)),(40,16,8,8,8))
        ids=[{x.task_id for x in z} for z in (d,c,h,r)]
        for i in range(len(ids)):
            for j in range(i+1,len(ids)): self.assertFalse(ids[i] & ids[j])

    def test_round1_prompt_budgets_are_small_and_exact(self):
        xs=tasks(); d,c,h=split(xs); wd,wc,_=workflows(xs); r=reserve_tasks(xs)
        a12=(1+len(UPDATES))*len(d+c+h)*3 + 10*4*8*3
        b1=(1+len(LESSONS))*len(c+h)*3 + len(d[:8])*3
        fresh_hidden=4
        e1=(sum(len(w['task_ids']) for w in wd+wc)+len(r))*(1+len(EDITS))*3 + 12*3
        self.assertEqual(a12,2976)
        self.assertEqual(b1,648)
        self.assertEqual(e1,612)
        self.assertEqual(fresh_hidden,4)

    def test_fit_cannot_exit_before_min_epochs(self):
        X=np.asarray([[-2.],[-1.],[1.],[2.]],float); y=np.asarray([0,0,1,1],int)
        with tempfile.TemporaryDirectory() as td:
            fit=fit_logistic(X,y,X,y,Path(td),min_epochs=40,max_epochs=80,patience=2)
            self.assertGreaterEqual(fit['epochs_ran'],40)
            self.assertTrue((Path(td)/'fit_history.jsonl').exists())
            self.assertTrue((Path(td)/'checkpoints').exists())

    def test_output_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with run_lock(root):
                with self.assertRaises(RuntimeError):
                    with run_lock(root): pass

    def test_e1_interaction_feature_is_representable(self):
        faults=['ordering','retry','schema','verification']; edits=[x[0] for x in EDITS]
        def feat(f,e): return [1. if f==x else 0. for x in faults]+[1. if e==x else 0. for x in edits]+[1. if (f==ff and e==ee) else 0. for ff in faults for ee in edits]
        a=feat('schema','schema_guard'); b=feat('schema','bounded_retry')
        self.assertEqual(len(a),len(faults)+len(edits)+len(faults)*len(edits))
        self.assertNotEqual(a,b)
        self.assertEqual(sum(a[-len(faults)*len(edits):]),1)

if __name__=='__main__': unittest.main()
