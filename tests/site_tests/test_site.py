import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]


class SiteContractTest(unittest.TestCase):
    def test_site_contract_and_brand_assets_exist(self):
        self.assertTrue((ROOT / "mkdocs.yml").is_file())
        self.assertTrue((ROOT / "site_docs/index.md").is_file())
        self.assertTrue((ROOT / "site_docs/assets/brand-mark.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/logo-lockup.svg").is_file())
        self.assertTrue((ROOT / "site_docs/stylesheets/extra.css").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/portfolio.js").is_file())
        catalog = ROOT / "site_docs/generated/catalog.md"
        self.assertTrue(catalog.is_file())
        self.assertIn("Catálogo da legislação", catalog.read_text(encoding="utf-8"))
        homepage = ROOT / "site_docs/index.md"
        self.assertIn("O direito federal", homepage.read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "tools/release/build_sbom.py").is_file())

    def test_generated_law_page_has_editorial_metadata_and_article_anchor(self):
        law = ROOT / "site_docs/generated/laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md"
        content = law.read_text(encoding="utf-8")
        self.assertIn('class="law-hero"', content)
        self.assertIn("## Art. 1º", content)
        self.assertIn("data-copy-id=", content)


if __name__ == "__main__":
    unittest.main()
