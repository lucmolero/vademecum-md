import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_release  # noqa: E402


class AutomaticUpdateLedgerTest(unittest.TestCase):
    def test_ledger_requires_exact_official_source_and_current_body(self):
        body = "**Art. 1º** Texto oficial.\n"
        digest = hashlib.sha256("Art. 1º Texto oficial.".encode()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            curated = root / "bases/curated"
            curated.mkdir(parents=True)
            law = curated / "lei-teste.md"
            law.write_text(f'---\nid: lei-teste\nsha256_published_body: "{digest}"\n---\n\n{body}', encoding="utf-8")
            (root / "manifests").mkdir()
            (root / "manifests/sources-registry.json").write_text(json.dumps({"sources": [{"hosts": ["planalto.gov.br"]}]}), encoding="utf-8")
            ledger = {
                "schema": "automatic-update-ledger/v1",
                "documents": [{
                    "document_id": "lei-teste",
                    "path": "bases/curated/lei-teste.md",
                    "source_url": "https://www.planalto.gov.br/lei.htm",
                    "approved_source_body_sha256": digest,
                    "approved_published_body_sha256": digest,
                    "evidence_status": "snapshot_verified",
                    "equivalence_basis": "normalized_exact_match",
                }],
            }
            (root / "manifests/automatic-update-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
            errors = []
            with patch.object(validate_release, "ROOT", root), patch.object(validate_release, "CURATED", curated):
                validate_release.validate_automatic_update_ledger(errors, {"lei-teste"})
            self.assertEqual(errors, [])

            ledger["documents"][0]["source_url"] = "https://example.com/lei.htm"
            (root / "manifests/automatic-update-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
            errors = []
            with patch.object(validate_release, "ROOT", root), patch.object(validate_release, "CURATED", curated):
                validate_release.validate_automatic_update_ledger(errors, {"lei-teste"})
            self.assertTrue(any("fonte não oficial" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
