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
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "acquire"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "normalize"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "history"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools" / "relations"))
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

from collect_legislation import (  # noqa: E402
    build_plan,
    fetch_one,
    fetch_plan,
    host_allowed,
    load_registry,
    normalized_hash,
    select_plan,
    stale_after_days,
)
from discover_legislation import build_queue  # noqa: E402
from normalize_source import normalize_bytes  # noqa: E402
from official_html_to_markdown import convert as official_html_to_markdown  # noqa: E402
from migrate_public_corpus import parse_frontmatter  # noqa: E402
from repair_encoding import candidate  # noqa: E402
from build_public_indexes import relation_is_plausible, relation_type  # noqa: E402
from build_structural_diffs import article_diff  # noqa: E402
from build_candidate_diffs import classify_change  # noqa: E402
from classify_unresolved import referenced_role  # noqa: E402
from pipeline_modes import load_modes, resolve_mode  # noqa: E402


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
        expected_count = len(rows)
        self.assertGreater(expected_count, 0)
        self.assertEqual(
            {row["camada"] for row in rows},
            {"core_constitucional", "core_codigos", "core_profissional", "cobertura_especializada", "auditoria_especialista"},
        )
        self.assertTrue(all(row["status_cobertura"] == "incluido" for row in rows))
        self.assertTrue({"document_id", "document_path", "status_consolidacao", "status_situacao", "data_corte", "sha256_origem", "fonte_oficial_count"} <= set(rows[0]))
        self.assertEqual(len({row["document_id"] for row in rows}), expected_count)

    def test_corpus_documents_have_canonical_contract(self) -> None:
        documents = list((ROOT / "bases/curated/legislacao").rglob("*.md"))
        with (ROOT / "manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
            expected_count = sum(1 for _ in csv.DictReader(stream, delimiter=";"))
        self.assertEqual(len(documents), expected_count)
        required = {"id", "titulo", "fonte_oficial", "sha256_origem", "consolidacao_status", "data_corte"}
        for path in documents:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            self.assertTrue(all(f"{key}:" in text for key in required), path)
            self.assertGreater(len(text.split("---", 2)[-1].strip()), 100, path)

    def test_public_manifests_are_valid(self) -> None:
        for relative in ("manifests/sources-official.json", "manifests/sources-registry.json", "manifests/source-comparison.json", "manifests/source-resolution.json", "manifests/discovery-registry.json", "manifests/discovery-queue.json", "manifests/relation-exclusions.json", "manifests/vocabulary.json", "manifests/operating-modes.json", "manifests/release.json", "manifests/completeness.json", "manifests/editorial-promotions.json", "manifests/baseline.json", "bases/derived/relatorios/editorial-legal-audit.json", "bases/derived/relatorios/editorial-legal-audit-p0.json", "bases/derived/relatorios/editorial-legal-audit-p1.json", "bases/derived/relatorios/editorial-legal-audit-p2.json"):
            value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertIsInstance(value, dict)
        promotions = json.loads((ROOT / "manifests/editorial-promotions.json").read_text(encoding="utf-8"))
        self.assertEqual(promotions["schema"], "editorial-promotion-decision/v2")
        self.assertEqual(promotions["reviewed_by"], "autonomous_legal_agent")
        self.assertEqual(promotions["analysis_executor"], "autonomous_legal_agent")
        self.assertEqual(set(promotions["decisions"]), {f"EXP-{number:03d}" for number in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16)})
        self.assertTrue(all(item["decision"] == "promote" for item in promotions["decisions"].values()))
        self.assertTrue(all(item.get("situacao") and item.get("evidencias") and item.get("revisor") for item in promotions["decisions"].values()))
        self.assertTrue(all(item.get("revisor") == "autonomous_legal_agent" and item.get("review_status") == "approved_autonomously" for item in promotions["decisions"].values()))
        document_count = len(list((ROOT / "bases/curated/legislacao").rglob("*.md")))
        baseline = json.loads((ROOT / "manifests/baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(baseline["schema"], "vademecum-baseline/v1")
        self.assertEqual(baseline["corpus_count"], document_count)
        self.assertEqual(baseline["status"], "pass")
        legal_audit = json.loads((ROOT / "bases/derived/relatorios/editorial-legal-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(legal_audit["schema"], "editorial-legal-audit/v1")
        self.assertEqual(legal_audit["status"], "pass")
        self.assertEqual(legal_audit["document_count"], 15)
        self.assertEqual(legal_audit["approved_count"], 15)
        self.assertTrue(all(item["hash_match"] for item in legal_audit["documents"]))
        p0_audit = json.loads((ROOT / "bases/derived/relatorios/editorial-legal-audit-p0.json").read_text(encoding="utf-8"))
        self.assertEqual(p0_audit["status"], "pass")
        self.assertEqual(p0_audit["document_count"], 33)
        self.assertEqual(p0_audit["approved_count"], 33)
        p1_audit = json.loads((ROOT / "bases/derived/relatorios/editorial-legal-audit-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(p1_audit["status"], "pass")
        self.assertEqual(p1_audit["document_count"], 336)
        self.assertEqual(p1_audit["approved_count"], 336)
        p2_audit = json.loads((ROOT / "bases/derived/relatorios/editorial-legal-audit-p2.json").read_text(encoding="utf-8"))
        self.assertEqual(p2_audit["status"], "pass")
        self.assertEqual(p2_audit["document_count"], 6)
        self.assertEqual(p2_audit["approved_count"], 6)
        release = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))
        self.assertEqual(release["corpus_count"], document_count)
        self.assertEqual(release["official_source_count"], document_count)
        sources = json.loads((ROOT / "manifests/sources-official.json").read_text(encoding="utf-8"))
        self.assertEqual(len(sources["documents"]), document_count)
        self.assertTrue(all(item.get("sha256_origem") for item in sources["documents"]))
        self.assertTrue(all(item.get("sha256_corpo") or item.get("sha256_corpo_por_fonte") for item in sources["documents"]))
        constitution = next(item for item in sources["documents"] if item["id"] == "br-federal-constituicao-1988")
        self.assertIsInstance(constitution["hash_scope"], dict)
        self.assertEqual(constitution["hash_scope"]["sha256_source_body"], "selected_normative_body_norm_v2")
        self.assertEqual(len(constitution["sha256_corpo_por_fonte"]), 2)
        registry = json.loads((ROOT / "manifests/sources-registry.json").read_text(encoding="utf-8"))
        self.assertTrue(registry["policy"]["official_only"])
        self.assertEqual(registry["policy"]["conflict_action"], "block_and_report")
        self.assertEqual(registry["policy"]["unavailable_action"], "preserve_current_and_alert")
        self.assertEqual(registry["policy"]["invalid_source_action"], "preserve_current_and_alert")
        self.assertTrue(all({"id", "adapter", "adapter_version", "hosts", "formats"} <= set(source) for source in registry["sources"]))
        ranks = {source["id"]: source["rank"] for source in registry["sources"]}
        self.assertEqual(ranks["planalto-br"], 1)
        self.assertEqual(ranks["senado-leg-br"], 2)
        self.assertEqual(ranks["camara-leg-br"], 3)
        self.assertEqual(ranks["dou-gov-br"], 4)

        resolutions = json.loads((ROOT / "manifests/source-resolution.json").read_text(encoding="utf-8"))
        self.assertEqual(resolutions["schema"], "source-resolution/v1")
        self.assertEqual(
            set(resolutions["documents"]),
            {"VM-006", "VM-009", "VM-012", "VM-026", "VM-036", "VM-047", "VM-069", "VM-092", "VM-312", "VM-313"},
        )
        self.assertTrue(all(item["status"] == "approved" for item in resolutions["documents"].values()))
        self.assertTrue(all(len(item["expected_source_sha256"]) == 64 for item in resolutions["documents"].values()))

    def test_operating_modes_are_explicit_and_autonomous(self) -> None:
        modes = load_modes()
        self.assertEqual(modes["default_mode"], "dry_run")
        self.assertEqual(set(modes["modes"]), {"dry_run", "proposal", "apply_reviewed", "release"})
        self.assertTrue(modes["policy"]["no_human_content_decision_required"])
        self.assertEqual(resolve_mode(None), "dry_run")
        self.assertEqual(resolve_mode(None, legacy_fetch=True), "proposal")
        self.assertEqual(resolve_mode(None, legacy_mutation=True), "apply_reviewed")

    def test_analysis_policy_separates_agent_and_deterministic_authority(self) -> None:
        policy = json.loads((ROOT / "manifests/analysis-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["decision_authority"], "autonomous_legal_agent")
        self.assertEqual(policy["deterministic_gate_authority"], "release_validators")
        self.assertEqual(policy["legal_analysis"]["method"], "llm_legal_analysis_plus_official_evidence")
        self.assertTrue(policy["deterministic_analysis"]["must_not_decide_legal_meaning"])
        self.assertFalse(policy["user_action_required"])

    def test_forbidden_acquisition_markers_are_absent(self) -> None:
        forbidden = ("ct" + "resb", "raw" + ".githubusercontent.com", "editorial" + "_benchmark", "senado" + "_4ed")
        paths = [ROOT / "README.md", ROOT / "SECURITY.md", *(ROOT / "docs").glob("*.md"), *(ROOT / "manifests").glob("*")]
        text = "\n".join(path.read_text(encoding="utf-8", errors="ignore").lower() for path in paths if path.is_file())
        self.assertFalse(any(marker in text for marker in forbidden))

    def test_release_validator_blocks_unreconciled_fidelity(self) -> None:
        result = subprocess.run([sys.executable, "tools/validate_release.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("fidelidade normativa", result.stdout)

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
        self.assertEqual(len(rows), 15)
        self.assertEqual(
            {row["id"] for row in rows if row["status_cobertura"] == "promovido_corpus"},
            {f"EXP-{number:03d}" for number in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16)},
        )
        self.assertTrue(all(row["status_aquisicao"] == "promovido_corpus" for row in rows))

    def test_update_frequencies_are_declared(self) -> None:
        collection = (ROOT / ".github/workflows/collect-legislation.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "23 4 1 1,4,7,10 *"', collection)
        self.assertIn("--priority P0", collection)
        self.assertIn("--priority P1", collection)
        self.assertIn("--priority P2", collection)
        self.assertIn("repository_dispatch", collection)
        self.assertIn("docs/proposals", (ROOT / ".github/workflows/prepare-update-pr.yml").read_text(encoding="utf-8"))
        proposal_workflow = (ROOT / ".github/workflows/prepare-update-pr.yml").read_text(encoding="utf-8")
        self.assertIn("--source-resolution manifests/source-resolution.json", proposal_workflow)
        self.assertIn("github.event.repository.default_branch", proposal_workflow)
        self.assertIn('git checkout -B "$base_branch" "origin/$base_branch"', proposal_workflow)
        self.assertIn("Refusing to write to the default branch", proposal_workflow)
        self.assertNotIn("gh pr create --draft", proposal_workflow)
        self.assertIn("gh pr merge", proposal_workflow)
        self.assertIn("--auto", proposal_workflow)
        history = (ROOT / ".github/workflows/sync-private-history.yml").read_text(encoding="utf-8")
        self.assertIn("HISTORY_REPO_SSH_KEY", history)
        self.assertNotIn("environment: private-history", history)
        self.assertIn("matrix_id", history)
        self.assertIn("timeout-minutes: 90", history)

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

    def test_application_shell_is_rejected_as_invalid_source(self) -> None:
        registry = load_registry()
        with patch("collect_legislation.urlopen") as opener:
            response = opener.return_value.__enter__.return_value
            response.geturl.return_value = "https://normas.leg.br/"
            response.headers = {"Content-Type": "text/html; charset=utf-8"}
            response.status = 200
            response.read.return_value = b"<html><head><title>Legislacao Federal</title></head><body><app-root></app-root></body></html>"
            result = fetch_one("https://normas.leg.br/", registry)
            self.assertEqual(result["status"], "invalid_source")
            self.assertEqual(result["reason"], "application_shell_without_legal_body")

    def test_normas_source_uses_current_public_compilation(self) -> None:
        registry = load_registry()
        metadata = MagicMock()
        metadata.__enter__.return_value = metadata
        metadata.geturl.return_value = "https://normas.leg.br/api/public/normas"
        metadata.headers = {"Content-Type": "application/json; charset=utf-8"}
        metadata.status = 200
        metadata.read.return_value = json.dumps({
            "encoding": [{
                "version": "Current",
                "additionalType": "CompilacaoMonoVigenteNaCD",
                "contentUrl": "https://normas.leg.br/api/binario/teste/texto",
            }],
        }).encode()
        content = MagicMock()
        content.__enter__.return_value = content
        content.geturl.return_value = "https://normas.leg.br/api/public/binario/teste/texto"
        content.headers = {"Content-Type": "text/html; charset=utf-8"}
        content.status = 200
        content.read.return_value = b"<html><body><p>Art. 1. Texto vigente.</p></body></html>"
        with patch("collect_legislation.urlopen", side_effect=[metadata, content]) as opener:
            result = fetch_one("https://normas.leg.br/?urn=urn:lex:br:federal:lei:2020-01-01;12345", registry)
        self.assertEqual(result["status"], "fetched")
        self.assertIn("api/public/binario/teste/texto", result["fetch_url"])
        self.assertEqual(opener.call_count, 2)

    def test_collection_plan_covers_matrix_without_network(self) -> None:
        plan = build_plan(date(2026, 10, 21))
        with (ROOT / "manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
            matrix_rows = list(csv.DictReader(stream, delimiter=";"))
        self.assertEqual(len(plan), len(matrix_rows))
        self.assertTrue(all(item["status"] == "planned" for item in plan))
        self.assertTrue(all(item["urls"] for item in plan))
        self.assertEqual(next(item for item in plan if item["matrix_id"] == "VM-001")["comparison_mode"], "complementary_sources")
        vm001 = next(item for item in plan if item["matrix_id"] == "VM-001")
        self.assertEqual(vm001["current_hash_kind"], "per_source")
        self.assertEqual(len(vm001["current_sha256_by_source"]), 2)
        self.assertEqual(len(select_plan(plan, ["P0"])), sum(row["prioridade"] == "P0" for row in matrix_rows))
        self.assertEqual(len(select_plan(plan, ["P1"])), sum(row["prioridade"] == "P1" for row in matrix_rows))
        self.assertEqual(len(select_plan(plan, ["P2"])), 6)
        vm359 = next(item for item in plan if item["matrix_id"] == "VM-359")
        self.assertEqual(vm359["current_hash_kind"], "legal_body")

    def test_complementary_sources_compare_hashes_per_url(self) -> None:
        plan = [{
            "matrix_id": "VM-001",
            "document_id": "br-federal-constituicao-1988",
            "source_manifest_ids": [],
            "current_sha256": None,
            "current_sha256_by_source": {
                "https://official.example/constitution": "body-a",
                "https://official.example/amendment": "body-b",
            },
            "current_hash_kind": "per_source",
            "prioridade": "P0",
            "sensibilidade": "alta",
            "urls": [
                "https://official.example/constitution",
                "https://official.example/amendment",
            ],
            "primary_url": "https://official.example/constitution",
            "source_count": 2,
            "comparison_mode": "complementary_sources",
            "data_corte": "2026-10-21",
            "idade_dias": 0,
            "stale": False,
            "status": "planned",
        }]
        registry = load_registry()

        def fake_fetch(url: str, _registry: dict[str, object]) -> dict[str, object]:
            body_hash = "body-a" if url.endswith("constitution") else "body-b"
            return {
                "status": "fetched",
                "url": url,
                "sha256_body": body_hash,
                "sha256_raw": "raw-" + body_hash,
                "sha256_normalized": "normalized-" + body_hash,
                "_data": body_hash.encode("utf-8"),
            }

        with TemporaryDirectory() as temporary, patch("collect_legislation.fetch_one", side_effect=fake_fetch):
            result = fetch_plan(plan, registry, Path(temporary))["results"][0]
        self.assertEqual(result["status"], "unchanged")

        def changed_fetch(url: str, _registry: dict[str, object]) -> dict[str, object]:
            value = "body-changed" if url.endswith("amendment") else "body-a"
            return {
                "status": "fetched",
                "url": url,
                "sha256_body": value,
                "sha256_raw": "raw-" + value,
                "sha256_normalized": "normalized-" + value,
                "_data": value.encode("utf-8"),
            }

        with TemporaryDirectory() as temporary, patch("collect_legislation.fetch_one", side_effect=changed_fetch):
            result = fetch_plan(plan, registry, Path(temporary))["results"][0]
        self.assertEqual(result["status"], "changed_candidate")

    def test_collection_can_target_explicit_matrix_ids(self) -> None:
        result = subprocess.run([
            sys.executable, "tools/acquire/collect_legislation.py", "--matrix-id", "VM-359",
        ], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["planned_count"], 1)
        self.assertEqual(payload["plan"][0]["matrix_id"], "VM-359")
        self.assertEqual(payload["plan"][0]["document_id"], "br-federal-decreto-24643-1934")

    def test_collection_plan_supports_editorial_expansion_without_corpus_mutation(self) -> None:
        with TemporaryDirectory() as temporary:
            expansion = Path(temporary) / "editorial-expansion.csv"
            with (ROOT / "manifests/editorial-expansion.csv").open(encoding="utf-8-sig", newline="") as source:
                rows = list(csv.DictReader(source, delimiter=";"))
            rows[0]["status_cobertura"] = "candidato_gap"
            rows[0]["status_aquisicao"] = "adquirido_pendente_reconciliacao"
            with expansion.open("w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=list(rows[0]), delimiter=";")
                writer.writeheader()
                writer.writerows([rows[0]])
            plan = build_plan(date(2026, 10, 21), expansion)
        self.assertEqual(len(plan), 1)
        self.assertTrue(all(item["matrix_id"].startswith("EXP-") for item in plan))
        self.assertTrue(all(item["status"] == "planned" for item in plan))
        self.assertTrue(all(item["current_sha256"] is None for item in plan))
        self.assertNotIn("EXP-004", {item["matrix_id"] for item in plan})

    def test_freshness_policy_is_explicit(self) -> None:
        self.assertEqual(stale_after_days("P0"), 100)
        self.assertEqual(stale_after_days("P1"), 100)
        self.assertEqual(stale_after_days("P2"), 180)
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
        unresolved = json.loads((ROOT / "bases/derived/relacoes/unresolved.json").read_text(encoding="utf-8"))
        classified = json.loads((ROOT / "bases/derived/relacoes/unresolved-classified.json").read_text(encoding="utf-8"))
        queue = json.loads((ROOT / "bases/derived/relacoes/review-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], "unresolved-relation-classification/v1")
        self.assertGreater(report["total"], 0)
        self.assertEqual(report["total"], len(unresolved))
        self.assertEqual(report["total"], classified["total"])
        self.assertEqual(report["total"], queue["occurrence_count"])
        self.assertEqual(report["total"], sum(item["occurrence_count"] for item in queue["targets"]))
        self.assertTrue(all(not item["requires_editorial_decision"] for item in queue["targets"]))
        self.assertTrue(all(item.get("referenced_role") for item in queue["targets"]))
        self.assertTrue(all(item.get("disposition") in {"historico", "grafo"} for item in queue["targets"]))
        self.assertTrue(all(item.get("decision") == item.get("disposition") for item in queue["targets"]))
        self.assertTrue(all(item.get("review_status") == "approved" for item in queue["targets"]))
        self.assertTrue(all(item.get("decision_scope") == "autonomous_agent_legal_curation" for item in queue["targets"]))
        self.assertTrue(all(item.get("analysis_method") == "llm_legal_analysis_plus_deterministic_gates" for item in queue["targets"]))
        self.assertTrue(all(set(item.get("assessment", {})) >= {
            "frequency", "p0_impact", "professional_relevance", "official_source",
            "autonomy", "duplication_risk", "actuality", "legal_situation",
        } for item in queue["targets"]))
        self.assertEqual(queue["by_disposition"], {"historico": 1408, "grafo": 83})
        self.assertIn("ato_alterador_ou_regulamentador", queue["by_referenced_role"])
        self.assertIn("by_referenced_role", report)
        completeness = (ROOT / "docs/COMPLETENESS.md").read_text(encoding="utf-8")
        self.assertIn(
            f"Disposição dos alvos únicos: **{queue['by_disposition']['historico']} históricos; "
            f"{queue['by_disposition']['grafo']} mantidos no grafo**",
            completeness,
        )
        expansion_targets = {item["expansion_candidate_id"] for item in queue["targets"] if item.get("expansion_candidate_id")}
        self.assertNotIn("EXP-014", expansion_targets)
        self.assertNotIn("EXP-015", expansion_targets)
        with (ROOT / "manifests/corpus.csv").open(encoding="utf-8", newline="") as stream:
            matrix_rows = list(csv.DictReader(stream, delimiter=";"))
            matrix_ids = {row["id"] for row in matrix_rows}
        self.assertIn("VM-363", matrix_ids)
        self.assertIn("VM-374", matrix_ids)
        self.assertEqual(len(matrix_rows), 375)

    def test_unknown_relation_type_is_explicitly_ambiguous(self) -> None:
        self.assertEqual(referenced_role("unknown_relation"), "ambiguo")

    def test_normative_graph_relations_have_machine_auditable_evidence(self) -> None:
        graph = (ROOT / "bases/derived/relacoes/normative-graph.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(graph), 0)
        for line in graph:
            relation = json.loads(line)
            self.assertTrue(relation.get("fonte"))
            self.assertTrue(relation.get("evidencia_textual"))
            self.assertEqual(relation.get("status_revisao"), "aprovado_autonomamente")
            self.assertIn(relation.get("confianca"), {"alta", "media", "baixa"})

    def test_source_normalizer_is_deterministic(self) -> None:
        html = b"<html><script>x</script><p>Art. 1</p><p>Texto   legal</p></html>"
        expected = "Art. 1\n\nTexto legal\n"
        self.assertEqual(normalize_bytes(html, "html"), expected)
        self.assertEqual(normalize_bytes(html, "html"), normalize_bytes(html, "html"))

    def test_official_converter_handles_legacy_cp1252_decrees(self) -> None:
        with TemporaryDirectory() as temporary:
            source = Path(temporary) / "legacy.html"
            source.write_bytes(
                "<html><body><p>O Chefe do Governo Provisório da República</p><p>Art. 1º A atribuição é oficial.</p></body></html>".encode("windows-1252")
            )
            converted = official_html_to_markdown(source, "auto")
            self.assertIn("Provisório", converted)
            self.assertIn("Art. 1º", converted)
            self.assertNotIn("�", converted)

    def test_structural_diff_recognizes_ordinal_article_labels(self) -> None:
        result = article_diff("**Art. 1º** texto anterior", "**Art. 1º** texto atual")
        self.assertEqual(result["artigos"]["total_anterior"], 1)
        self.assertEqual(result["artigos"]["total_atual"], 1)
        self.assertEqual(result["artigos"]["alterados"], 1)

    def test_structural_diff_covers_paragraphs_incises_and_alineas(self) -> None:
        old = "**Art. 1º**\n**§ 1º** antigo\nI – um\na – alínea antiga\n"
        new = "**Art. 1º**\n**§ 1º** novo\nI – um atualizado\nII – dois\na – alínea nova\n"
        details = article_diff(old, new)["detalhes"][0]
        self.assertEqual(details["paragrafos"]["changed"], 1)
        self.assertEqual(details["incisos"]["added"], 1)
        self.assertEqual(details["incisos"]["changed"], 1)
        self.assertEqual(details["alineas"]["changed"], 1)

    def test_candidate_diff_classifies_legal_effect_markers(self) -> None:
        structure = {"alterados": 1, "adicionados": 0, "removidos": 0}
        cases = {
            "O artigo foi revogado parcialmente.": "possivel_revogacao",
            "O veto foi mantido.": "possivel_veto",
            "A lei foi retificada.": "possivel_retificacao",
            "A vigência terá início em 1º de janeiro.": "possivel_efeito_de_vigencia",
            "A produção de efeitos ocorrerá posteriormente.": "possivel_efeito_de_vigencia",
        }
        for body, expected in cases.items():
            with self.subTest(expected=expected):
                self.assertIn(expected, classify_change("changed_candidate", "Art. 1º antigo.", body, structure))

    def test_candidate_diff_classifies_source_failures_without_inference(self) -> None:
        for status, expected in (
            ("source_conflict", "conflito_de_fontes"),
            ("source_unavailable", "fonte_indisponivel"),
            ("source_invalid", "fonte_invalida"),
        ):
            with self.subTest(status=status):
                labels = classify_change(status, "", "", {})
                self.assertIn(expected, labels)
                self.assertIn("requer_reconciliacao", labels)

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

    def test_derived_relation_files_use_portable_lf_line_endings(self) -> None:
        for relative in (
            "bases/derived/relacoes/normative-graph.jsonl",
            "bases/derived/relacoes/unresolved.json",
        ):
            data = (ROOT / relative).read_bytes()
            self.assertNotIn(b"\r\n", data, relative)


if __name__ == "__main__":
    unittest.main()
