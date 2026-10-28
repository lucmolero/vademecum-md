import json
import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
SITE_BUILDER_SPEC = importlib.util.spec_from_file_location("vmd_site_builder", ROOT / "tools/site/build_site.py")
SITE_BUILDER = importlib.util.module_from_spec(SITE_BUILDER_SPEC)
SITE_BUILDER_SPEC.loader.exec_module(SITE_BUILDER)
SITE_HOOKS_SPEC = importlib.util.spec_from_file_location("vmd_site_hooks", ROOT / "site_docs/hooks.py")
SITE_HOOKS = importlib.util.module_from_spec(SITE_HOOKS_SPEC)
SITE_HOOKS_SPEC.loader.exec_module(SITE_HOOKS)


class SiteContractTest(unittest.TestCase):
    def test_site_contract_and_brand_assets_exist(self):
        self.assertTrue((ROOT / "mkdocs.yml").is_file())
        self.assertTrue((ROOT / "site_docs/index.md").is_file())
        self.assertTrue((ROOT / "site_docs/assets/brand-mark.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/logo-lockup.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/og-card.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/og-card.png").is_file())
        self.assertTrue((ROOT / "site_docs/stylesheets/extra.css").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/portfolio.js").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/reader.js").is_file())
        self.assertTrue((ROOT / "site_docs/audiences.md").is_file())
        catalog = ROOT / "site_docs/generated/catalog.md"
        self.assertTrue(catalog.is_file())
        self.assertIn("Catálogo da legislação", catalog.read_text(encoding="utf-8"))
        self.assertIn("Grandes Códigos da República", catalog.read_text(encoding="utf-8"))
        homepage = ROOT / "site_docs/index.md"
        homepage_text = homepage.read_text(encoding="utf-8")
        self.assertIn("O direito federal", homepage_text)
        self.assertIn("Grandes Códigos da República", homepage_text)
        self.assertIn("Leitura humana e consulta por agentes", homepage_text)
        self.assertIn("Conhecimento para agentes", homepage_text)
        metrics = json.loads((ROOT / "site_docs/generated/metrics.json").read_text(encoding="utf-8"))
        baseline = json.loads((ROOT / "manifests/baseline.json").read_text(encoding="utf-8"))
        self.assertIn(f'{metrics["p0_ready"]}<sup>/{metrics["p0_total"]}</sup>', homepage_text)
        self.assertEqual((metrics["p0_ready"], metrics["p0_total"]), (baseline["p0"]["ready"], baseline["p0"]["total"]))
        self.assertIn("Leitura jurídica", (ROOT / "site_docs/audiences.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "tools/release/build_sbom.py").is_file())

    def test_social_metadata_uses_absolute_raster_card_and_page_context(self):
        page = SimpleNamespace(
            title='Código "Civil"',
            meta={"description": "Consulta com fonte oficial e corte."},
            canonical_url="https://lucmolero.github.io/vademecum-md/codigo-civil/",
        )
        config = SimpleNamespace(
            site_url="https://lucmolero.github.io/vademecum-md/",
            site_name="VadeMecum MD",
            site_description="Descrição geral.",
        )
        output = SITE_HOOKS.on_post_page(
            '<html lang="pt" class="no-js"><head></head><body></body></html>',
            page=page,
            config=config,
        )
        self.assertIn(
            'property="og:image" content="https://lucmolero.github.io/vademecum-md/assets/og-card.png"',
            output,
        )
        self.assertIn('property="og:title" content="Código &quot;Civil&quot;"', output)
        self.assertIn('property="og:description" content="Consulta com fonte oficial e corte."', output)
        self.assertIn('name="twitter:card" content="summary_large_image"', output)
        self.assertEqual(output.count('property="og:image"'), 1)

    def test_generated_law_page_has_editorial_metadata_and_article_anchor(self):
        law = ROOT / "site_docs/generated/laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md"
        content = law.read_text(encoding="utf-8")
        self.assertIn('class="law-hero"', content)
        self.assertIn("## Art. 1º", content)
        self.assertIn("data-copy-id=", content)
        self.assertIn('class="reader-toolbar"', content)
        self.assertIn('id="btn-quick-jump"', content)
        self.assertIn('id="btn-focus-mode"', content)

    def test_environmental_licensing_law_uses_its_correct_public_title(self):
        self.assertEqual(
            SITE_BUILDER.POPULAR_TITLES["br-federal-lei_ordinaria-15190-2025"],
            "Lei Geral do Licenciamento Ambiental (Lei nº 15.190/2025)",
        )

    def test_graph_context_preserves_direction_and_requires_an_article_device(self):
        relation = {
            "source_id": "law-a",
            "target_id": "law-b",
            "source_title": "Lei A",
            "target_title": "Lei B",
            "type": "altera",
            "dispositivo": "art. 5º",
            "confianca": "alta",
            "status_revisao": "aprovado_autonomamente",
            "fonte": "https://example.gov.br/lei",
            "evidencia_textual": "altera o art. 5º",
            "_site_id": "normative-relation-test",
            "_site_device_document_id": "law-b",
        }
        source_context = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.", [relation], "law-a")
        target_context = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.\n\n**Art. 6º** Outro.", [relation], "law-b")
        page = SITE_BUILDER.law_page({"id": "law-b", "titulo": "Lei B"}, "**Art. 5º** Texto.", [relation])
        self.assertNotIn("relation-margin-note", source_context)
        self.assertIn("relation-margin-note", target_context)
        self.assertIn("Ver relação no grafo", target_context)
        self.assertLess(target_context.index("Ver relação no grafo"), target_context.index("Texto."))
        self.assertIn("Lei A", page)
        self.assertIn("altera", page)
        self.assertIn("altera o art. 5º", page)
        self.assertIn('id="normative-relation-test"', page)
        self.assertLess(page.index("## Art. 5º"), page.index('id="law-relations-title"'))

        without_device = {**relation, "dispositivo": None}
        no_article_marker = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.", [without_device])
        no_article_page = SITE_BUILDER.law_page({"id": "law-a", "titulo": "Lei A"}, "**Art. 5º** Texto.", [without_device])
        self.assertNotIn("relation-margin-note", no_article_marker)
        self.assertIn("Dispositivo não identificado", no_article_page)

    def test_graph_mirror_is_shown_once_with_active_direction(self):
        active = {
            "source_id": "amending-law",
            "target_id": "amended-law",
            "type": "altera",
            "dispositivo": "art. 5º",
            "data_efeito": "2024-01-01",
            "evidencia_sha256": "same-evidence",
        }
        inverse = {
            **active,
            "source_id": "amended-law",
            "target_id": "amending-law",
            "type": "alterada_por",
        }
        unique = SITE_BUILDER.deduplicate_relation_mirrors([inverse, active])
        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0]["type"], "altera")
        self.assertEqual(unique[0]["source_id"], "amending-law")


if __name__ == "__main__":
    unittest.main()
