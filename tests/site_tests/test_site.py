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
        self.assertTrue((ROOT / "site_docs/stylesheets/launch.css").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/portfolio.js").is_file())
        self.assertFalse((ROOT / "site_docs/javascripts/reader.js").exists())
        self.assertFalse((ROOT / "site_docs/reader/index.md").exists())
        self.assertTrue((ROOT / "site_docs/audiences.md").is_file())
        catalog = ROOT / "site_docs/generated/catalog.md"
        self.assertTrue(catalog.is_file())
        self.assertIn("Catálogo da legislação", catalog.read_text(encoding="utf-8"))
        self.assertIn("Grandes códigos e referências", catalog.read_text(encoding="utf-8"))
        homepage = ROOT / "site_docs/index.md"
        homepage_text = homepage.read_text(encoding="utf-8")
        self.assertIn("biblioteca", homepage_text)
        self.assertIn("biblioteca/catalog.json", (ROOT / "site_docs/javascripts/portfolio.js").read_text(encoding="utf-8"))
        metrics = json.loads((ROOT / "site_docs/generated/metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["corpus_count"], 375)
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
        self.assertIn('class="legacy-reader-redirect"', content)
        self.assertIn("Abrir na biblioteca", content)
        self.assertIn("biblioteca/#documento=br-federal-lei_ordinaria-10406-2002", content)
        self.assertIn("location.replace", content)

    def test_environmental_licensing_law_uses_its_correct_public_title(self):
        self.assertEqual(
            SITE_BUILDER.POPULAR_TITLES["br-federal-lei_ordinaria-15190-2025"],
            "Lei Geral do Licenciamento Ambiental (Lei nº 15.190/2025)",
        )

    def test_old_reader_urls_redirect_to_official_library_and_keep_article_anchor(self):
        page = SITE_BUILDER.legacy_reader_page("law-1", "Lei de teste", "federal/leis/2020/lei-1.md")
        self.assertIn("https://lucmolero.github.io/vademecum-md/biblioteca/#documento=law-1", page)
        self.assertIn('params.set("artigo", article[1])', page)
        self.assertIn("location.replace", page)


if __name__ == "__main__":
    unittest.main()
