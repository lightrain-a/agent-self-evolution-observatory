from __future__ import annotations
import hashlib, json, tempfile, unittest
from pathlib import Path
from .paper_acceptance import MANDATORY_MANUSCRIPT_CI_CHECKS, MockReviewMode, ObjectionEvidenceState, PaperContract, PaperState, PrebuttalResolution, ReviewerObjection, ScientificPaperStatus, StoryCandidate
from .paper_acceptance_ledger import advance_paper_ledger, initialize_paper_ledger, record_claim_audit, record_manuscript_ci, record_mock_review, record_paper_preparation, record_prebuttal, record_story_search, record_submission_readiness
from .paper_preparation_protocol import PAPER_PREPARATION_GATE_KEYS, PAPER_PREPARATION_PROTOCOL_VERSION
from .presubmission_freeze import artifact, build_freeze, digest, publish_freeze, validate_freeze, verify_current_frozen_artifacts
from .test_paper_preparation_protocol import passing_packet

class PreSubmissionFreezeTest(unittest.TestCase):
    def ready(self, root:Path)->PaperContract:
        c=PaperContract(paper_id='FREEZE-PAPER',title='Freeze paper',central_question='Can bytes be frozen?',supported_claims={'C1':'Supported.'},evidence_refs=('artifact:evidence',),scientific_status=ScientificPaperStatus.READY,paper_preparation_protocol_version=PAPER_PREPARATION_PROTOCOL_VERSION,paper_preparation_requirements=PAPER_PREPARATION_GATE_KEYS)
        initialize_paper_ledger(root,c);advance_paper_ledger(root,c,PaperState.PAPER_DESIGN)
        record_story_search(root,c,[StoryCandidate('S1','Story','Frame',('C1',),('C1',))]);advance_paper_ledger(root,c,PaperState.MANUSCRIPT);advance_paper_ledger(root,c,PaperState.MOCK_PC)
        o=ReviewerObjection('R1','clarity','Clarify.',True,ObjectionEvidenceState.EXISTING_EVIDENCE,('C1',))
        record_mock_review(root,c,MockReviewMode.BLIND_MANUSCRIPT,[o]);record_mock_review(root,c,MockReviewMode.ARTIFACT_AWARE,[o]);advance_paper_ledger(root,c,PaperState.TARGETED_REPAIR);advance_paper_ledger(root,c,PaperState.CLAIM_AUDIT)
        record_claim_audit(root,c,manuscript_ref='artifact:paper',claimed_ids=('C1',),evidence_bound_claim_ids=('C1',),limitations_preserved=True);advance_paper_ledger(root,c,PaperState.PDF_QA)
        record_manuscript_ci(root,c,{k:True for k in MANDATORY_MANUSCRIPT_CI_CHECKS});advance_paper_ledger(root,c,PaperState.PREBUTTAL);record_prebuttal(root,c,[o],[PrebuttalResolution('R1',True,('artifact:evidence',))])
        record_paper_preparation(root,c,passing_packet());record_submission_readiness(root,c);self.assertTrue(advance_paper_ledger(root,c,PaperState.SUBMISSION_READY)['receipt']['allowed']);return c
    def test_freeze_requires_ready_preparation_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.ready(root);f=root/'paper.pdf';f.write_bytes(b'paper-bytes');a=artifact('paper_pdf',f)
            policy={'schema_version':'1.0','venue':'TEST','human_only_confirmation_required':True};policy['snapshot_sha256']=digest(policy)
            r=build_freeze('FREEZE-PAPER',[a],policy,root);self.assertEqual(r['status'],'MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING');self.assertFalse(r['submission_authority'])
            row=publish_freeze(r,root);row=publish_freeze(r,root);self.assertEqual(len(row['events']),1);self.assertEqual(validate_freeze(row),[]);self.assertEqual(verify_current_frozen_artifacts(row),[])
            f.write_bytes(b'paper-bytes-changed');self.assertIn('freeze-artifact-drift:paper_pdf',verify_current_frozen_artifacts(row))
            row['events'][0]['receipt']['human_signoff_status']='TAMPERED';self.assertIn('invalid-freeze-receipt-hash',validate_freeze(row))
    def test_artifact_hash_changes_when_bytes_change(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x';p.write_bytes(b'a');x=artifact('x',p);p.write_bytes(b'b');y=artifact('x',p);self.assertNotEqual(x['sha256'],y['sha256'])

if __name__=='__main__':unittest.main()
