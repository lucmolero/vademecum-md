import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from datetime import date
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "acquire"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "normalize"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

from collect_legislation import (  # noqa: E402
    build_plan,
    fetch_one,
    host_allowed,
    load_registry,
    normalized_hash,
    select_plan,
    stale_after_days,
)
from discover_legislation import build_queue  # noqa: E402
from normalize_source import normalize_bytes  # noqa: E402
from migrate_public_corpus import parse_frontmatter  # noqa: E402
from repair_encoding import candidate  # noqa: E402
from build_public_indexes import relation_is_plausible, relation_type  # noqa: E402


ROOT = Path(__file__).parents[1]


class WorkspaceTest(unittest.TestCase):
    def test_public_layers_exist(self) -> None:
        for relative in (
            "bases/raw", "bases/curated/legislacao/federal", "bases/curated/regulamentos",
            "bases/curated/tratados", "bases/curated/jurisprudencia", "bases/history",
            "bases/derived", "projects", "skills", "harness", "manifests", "tools",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_dir())

    def test_corpus_matrix_has_neutral_schema(self) -> None:
        with (ROOT / "manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        self.assertEqual(len(rows), 360)
        self.assertEqual(
            {row["camada"] for row in rows},
            {"core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"},
        )
        self.assertTrue(all(row["status_cobertura"] == "incluido" for row in rows))
        self.assertTrue({"document_id", "document_path", "status_consolidacao", "status_situacao", "data_corte", "sha256_origem", "fonte_oficial_count"} <= set(rows[0]))
        self.assertEqual(len({row["document_id"] for row in rows}), 360)

    def test_corpus_documents_have_canonical_contract(self) -> None:
        documents = list((ROOT / "bases/curated/legislacao").rglob("*.md"))
        self.assertEqual(len(documents), 360)
        required = {"id", "titulo", "fonte_oficial", "sha256_origem", "consolidacao_status", "data_corte"}
        for path in documents:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            self.assertTrue(all(f"{key}:" in text for key in required), path)
            self.assertGreater(len(text.split("---", 2)[-1].strip()), 100, path)

    def test_public_manifests_are_valid(self) -> None:
        for relative in ("manifests/sources-official.json", "manifests/sources-registry.json", "manifests/discovery-registry.json", "manifests/discovery-queue.json", "manifests/relation-exclusions.json", "manifests/vocabulary.json", "manifests/release.json", "manifests/completeness.json"):
            value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertIsInstance(value, dict)
        release = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))
        self.assertEqual(release["corpus_count"], 360)
        self.assertEqual(release["official_source_count"], 360)
        registry = json.loads((ROOT / "manifests/sources-registry.json").read_text(encoding="utf-8"))
        self.assertTrue(registry["policy"]["official_only"])
        self.assertTrue(all({"id", "adapter", "adapter_version", "hosts", "formats"} <= set(source) for source in registry["sources"]))

    def test_forbidden_acquisition_markers_are_absent(self) -> None:
        forbidden = ("ct" + "resb", "raw" + ".githubusercontent.com", "editorial" + "_benchmark", "senado" + "_4ed")
        paths = [ROOT / "README.md", ROOT / "SECURITY.md", *(ROOT / "docs").glob("*.md"), *(ROOT / "manifests").glob("*")]
        text = "\n".join(path.read_text(encoding="utf-8", errors="ignore").lower() for path in paths if path.is_file())
        self.assertFalse(any(marker in text for marker in forbidden))

    def test_release_validator_passes(self) -> None:
        result = subprocess.run([sys.executable, "tools/validate_release.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_workflows_cannot_mutate_main_directly(self) -> None:
        result = subprocess.run([sys.executable, "tools/validate/validate_workflows.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_editorial_matrix_audit_is_complete(self) -> None:
        result = subprocess.run([sys.executable, "tools/validate/sync_editorial_matrix.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((ROOT / "reports/editorial-matrix-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(report["matrix_rows"], report["canonical_documents"])
        self.assertEqual(report["matched_rows"], report["matrix_rows"])
        self.assertEqual(report["missing_or_ambiguous"], [])
        self.assertEqual(report["drift"], [])

    def test_editorial_expansion_inventory_is_controlled(self) -> None:
        result = subprocess.run([sys.executable, "tools/validate/audit_editorial_expansion.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with (ROOT / "manifests/editorial-expansion.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row["status_aquisicao"] == "adquirido_pendente_reconciliacao" for row in rows))

    def test_update_frequencies_are_declared(self) -> None:
        collection = (ROOT / ".github/workflows/collect-legislation.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "23 4 * * *"', collection)
        self.assertIn('cron: "37 4 * * 1"', collection)
        self.assertIn('cron: "53 4 1 * *"', collection)
        self.assertIn("--priority P0", collection)
        self.assertIn("--priority P1", collection)
        self.assertIn("--priority P2", collection)
        self.assertIn("repository_dispatch", collection)
        self.assertIn("docs/proposals", (ROOT / ".github/workflows/prepare-update-pr.yml").read_text(encoding="utf-8"))
        history = (ROOT / ".github/workflows/sync-private-history.yml").read_text(encoding="utf-8")
        self.assertIn("HISTORY_REPO_TOKEN", history)
        self.assertIn("environment: private-history", history)

    def test_source_registry_is_allowlisted(self) -> None:
        registry = load_registry()
        self.assertTrue(host_allowed("https://www.planalto.gov.br/", registry))
        self.assertTrue(host_allowed("https://normas.leg.br/", registry))
        self.assertFalse(host_allowed("https://raw.githubusercontent.com/example/repo/main/a", registry))

    def test_http_errors_are_classified_without_mutation(self) -> None:
        registry = load_registry()
        for status in (404, 429, 500):
            with self.subTest(status=status), patch(
                "collect_legislation.urlopen",
                side_effect=HTTPError("https://normas.leg.br/", status, "test", {}, None),
            ):
                result = fetch_one("https://normas.leg.br/", registry)
                self.assertEqual(result["status"], "http_error")
                self.assertEqual(result["http_status"], status)

    def test_official_fetch_request_uses_compatible_headers(self) -> None:
        registry = load_registry()
        with patch("collect_legislation.urlopen") as opener:
            response = opener.return_value.__enter__.return_value
            response.geturl.return_value = "https://www.planalto.gov.br/example"
            response.headers = {"Content-Type": "text/html; charset=utf-8"}
            response.status = 200
            response.read.return_value = b"Art. 1"
            result = fetch_one("https://www.planalto.gov.br/example", registry)
            self.assertEqual(result["status"], "fetched")
            request = opener.call_args.args[0]
            self.assertTrue(request.headers["User-agent"].startswith("Mozilla/5.0"))
            self.assertEqual(request.headers["Accept-encoding"], "identity")

    def test_collection_plan_covers_matrix_without_network(self) -> None:
        plan = build_plan(date(2026, 10, 21))
        self.assertEqual(len(plan), 360)
        self.assertTrue(all(item["status"] == "planned" for item in plan))
        self.assertTrue(all(item["urls"] for item in plan))
        self.assertEqual(len(select_plan(plan, ["P0"])), 30)
        self.assertEqual(len(select_plan(plan, ["P1"])), 324)
        self.assertEqual(len(select_plan(plan, ["P2"])), 6)

    def test_collection_plan_supports_editorial_expansion_without_corpus_mutation(self) -> None:
        expansion = ROOT / "manifests/editorial-expansion.csv"
        plan = build_plan(date(2026, 10, 21), expansion)
        self.assertEqual(len(plan), 12)
        self.assertTrue(all(item["matrix_id"].startswith("EXP-") for item in plan))
        self.assertTrue(all(item["status"] == "planned" for item in plan))
        self.assertTrue(all(item["current_sha256"] is None for item in plan))

    def test_freshness_policy_is_explicit(self) -> None:
        self.assertEqual(stale_after_days("P0"), 1)
        self.assertEqual(stale_after_days("P1"), 7)
        self.assertEqual(stale_after_days("P2"), 30)
        self.assertEqual(len(normalized_hash("a   b")), 64)

    def test_discovery_never_auto_includes_or_accepts_external_hosts(self) -> None:
        queue = build_queue([
            {"url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm"},
            {"url": "https://example.invalid/act"},
        ])
        self.assertEqual(len(queue["candidates"]), 1)
        self.assertFalse(queue["candidates"][0]["auto_include"])
        self.assertEqual(queue["candidates"][0]["status"], "candidate")
        self.assertEqual(len(queue["rejected"]), 1)

    def test_update_proposal_contains_review_evidence(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            report = directory / "collection.json"
            output = directory / "proposal.json"
            markdown = directory / "proposal.md"
            report.write_text(json.dumps({
                "results": [{
                    "matrix_id": "VM-001",
                    "status": "changed_candidate",
                    "current_sha256": "a" * 64,
                    "sha256_raw": "b" * 64,
                    "primary_url": "https://www.planalto.gov.br/example",
                }]
            }), encoding="utf-8")
            result = subprocess.run([
                sys.executable, "tools/release/prepare_update_pr.py",
                "--collection-report", str(report),
                "--output", str(output),
                "--proposal-markdown", str(markdown),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(markdown.is_file())
            self.assertIn("VM-001", markdown.read_text(encoding="utf-8"))
            proposal_data = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("risk_summary", proposal_data)
            self.assertIn("release_blockers", proposal_data)

    def test_private_ledger_export_is_hash_auditable(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "acquisition"
            source.mkdir()
            (source / "snapshot.source").write_bytes(b"official snapshot")
            output = directory / "history"
            result = subprocess.run([
                sys.executable, "tools/history/build_private_ledger.py",
                "--source", str(source),
                "--output", str(output),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ledger = json.loads((output / "ledger-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["files"][0]["sha256"], hashlib.sha256(b"official snapshot").hexdigest())

    def test_unresolved_relations_are_classified_without_matrix_expansion(self) -> None:
        report = json.loads((ROOT / "bases/history/alteracoes/2026-10-21-unresolved-relations.json").read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], "unresolved-relation-classification/v1")
        self.assertGreater(report["total"], 0)
        self.assertEqual(sum(report["by_classification"].values()), report["total"])
        self.assertEqual(set(report["by_classification"]), {"out_of_matrix"})
        self.assertIn("classification_method", report)
        self.assertIn("no candidate is added", report["policy"])

    def test_source_normalizer_is_deterministic(self) -> None:
        html = b"<html><script>x</script><p>Art. 1</p><p>Texto   legal</p></html>"
        expected = "Art. 1\n\nTexto legal\n"
        self.assertEqual(normalize_bytes(html, "html"), expected)
        self.assertEqual(normalize_bytes(html, "html"), normalize_bytes(html, "html"))

    def test_frontmatter_parser_fails_closed_in_strict_mode(self) -> None:
        with self.assertRaises(ValueError):
            parse_frontmatter("# sem frontmatter\n", strict=True)
        with self.assertRaises(ValueError):
            parse_frontmatter("---\n: invalid: yaml\n---\ntexto\n", strict=True)
        metadata, body = parse_frontmatter("---\ntitulo: \"Teste\"\n---\n\nArt. 1\n", strict=True)
        self.assertEqual(metadata["titulo"], "Teste")
        self.assertEqual(body, "Art. 1\n")

    def test_encoding_repair_only_accepts_real_mojibake_improvement(self) -> None:
        self.assertEqual(candidate("ConstituiÃ§Ã£o"), "Constituição")
        self.assertIsNone(candidate("Constituição"))

    def test_relation_direction_respects_active_and_passive_legal_language(self) -> None:
        self.assertEqual(relation_type("altera a Lei nº 12.345"), "altera")
        self.assertEqual(relation_type("com redação dada pela Lei nº 12.345"), "alterada_por")
        self.assertEqual(relation_type("revoga dispositivos do Decreto-Lei nº 2.848"), "revoga")
        self.assertEqual(relation_type("foi revogada pela Lei nº 12.345"), "revogada_por")
        self.assertEqual(relation_type("regulamenta a Lei nº 12.345"), "regulamenta")
        self.assertFalse(relation_is_plausible("altera", {"data_assinatura": "1991-01-01"}, {"data_assinatura": "1994-01-01"}))
        self.assertTrue(relation_is_plausible("alterada_por", {"data_assinatura": "1991-01-01"}, {"data_assinatura": "1994-01-01"}))

    def test_derived_index_build_is_idempotent(self) -> None:
        paths = sorted((ROOT / "bases/curated").rglob("*.md"))
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        result = subprocess.run([sys.executable, "tools/build_public_indexes.py", "--apply"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
