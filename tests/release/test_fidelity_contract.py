import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from validate_release import current_published_body_hash  # noqa: E402


class FidelityContractTest(unittest.TestCase):
    def test_all_documents_have_explicit_fidelity_metadata(self):
        documents = list((ROOT / "bases/curated/legislacao").rglob("*.md"))
        self.assertEqual(len(documents), 375)
        for path in documents:
            text = path.read_text(encoding="utf-8")
            self.assertIn("canonicalization_version: \"norm-v3\"", text, path)
            self.assertRegex(text, r"source_unit_id: \"[^\"]+\"")
            for field in ("sha256_source_raw", "sha256_source_normalized", "sha256_source_body", "sha256_published_body"):
                self.assertRegex(text, rf"{field}: \"[0-9a-f]{{64}}\"", path)

    def test_shared_constitution_source_has_independent_units(self):
        units = json.loads((ROOT / "manifests/source-units.json").read_text(encoding="utf-8"))["units"]
        self.assertNotEqual(units["br-federal-constituicao-1988"]["source_unit_id"], units["br-federal-ato_constitucional-1988"]["source_unit_id"])
        self.assertEqual(units["br-federal-constituicao-1988"]["shared_source_policy"], "separate_from_adct")

    def test_fidelity_report_covers_entire_corpus_and_does_not_publish_private_paths(self):
        report = json.loads((ROOT / "bases/derived/relatorios/fidelity-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(report["corpus_count"], 375)
        self.assertEqual(len(report["documents"]), 375)
        serialized = json.dumps(report, ensure_ascii=False).lower()
        self.assertNotIn(".private\\", serialized)
        self.assertNotIn(".private/", serialized)

    def test_published_body_mutation_changes_the_hash_bound_to_the_report(self):
        original = "---\nid: test-law\n---\n\n**Art. 1º** Texto original.\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "law.md"
            path.write_text(original, encoding="utf-8")
            original_id, original_hash, _ = current_published_body_hash(path)
            path.write_text(original.replace("Texto original", "Texto alterado"), encoding="utf-8")
            changed_id, changed_hash, _ = current_published_body_hash(path)

        self.assertEqual(original_id, "test-law")
        self.assertEqual(changed_id, original_id)
        self.assertNotEqual(changed_hash, original_hash)


if __name__ == "__main__":
    unittest.main()
