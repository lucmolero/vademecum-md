import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools" / "legal"))
from validate_consensus import validate  # noqa: E402


def ledger(decision: str = "preserve_current", consensus: bool = True) -> dict:
    pass_data = {
        "status": "complete",
        "decision": decision,
        "evidence": ["https://www.planalto.gov.br/"],
        "must_not_invent_text": True,
    }
    return {
        "schema": "legal-curation-consensus/v1",
        "decision_authority": "autonomous_legal_agent",
        "analysis_method": "deterministic_source_fidelity_gate",
        "independent_legal_opinion": False,
        "assessment_scope": "source_identity_and_text_fidelity_only",
        "role_scope": "legacy_technical_gate_label_not_legal_opinion",
        "documents": [{
            "document_id": "br-federal-lei_ordinaria-1-1900",
            "decision": decision,
            "official_evidence": ["https://www.planalto.gov.br/"],
            "legal_curator": pass_data,
            "legal_critic": dict(pass_data),
            "consensus": consensus,
        }],
    }


class LegalConsensusTest(unittest.TestCase):
    def validate_payload(self, payload: dict) -> tuple[bool, list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "consensus.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(path)

    def test_complete_consensus_is_valid(self):
        valid, errors = self.validate_payload(ledger())
        self.assertTrue(valid, errors)

    def test_disagreement_is_rejected(self):
        payload = ledger(consensus=False)
        payload["documents"][0]["legal_critic"]["decision"] = "reconcile"
        valid, errors = self.validate_payload(payload)
        self.assertFalse(valid)
        self.assertTrue(any("disagreement" in error for error in errors))

    def test_candidate_snapshot_hash_is_validated(self):
        payload = ledger()
        payload["documents"][0]["candidate_sha256_raw"] = "not-a-sha256"
        valid, errors = self.validate_payload(payload)
        self.assertFalse(valid)
        self.assertTrue(any("candidate_sha256_raw" in error for error in errors))

    def test_deterministic_gate_cannot_claim_an_independent_legal_opinion(self):
        payload = ledger()
        payload["independent_legal_opinion"] = True
        valid, errors = self.validate_payload(payload)
        self.assertFalse(valid)
        self.assertTrue(any("not an independent legal opinion" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
