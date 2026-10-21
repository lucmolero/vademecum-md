import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
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


if __name__ == "__main__":
    unittest.main()
